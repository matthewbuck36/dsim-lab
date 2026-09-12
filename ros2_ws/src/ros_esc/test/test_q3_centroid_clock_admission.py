"""Actual detector callback contracts for a held simulation clock.

ROS and steady times are controlled independently. No executor/Gazebo runs and
no detector model is substituted: callbacks exercise the real node and core.
"""
from copy import deepcopy

import pytest
import rclpy
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool

from ros_esc.convergence_detector_node import convergence_detector_node_script as detector
from ros_esc_interfaces.msg import AlgorithmState
from ros_esc.controller_node.clock_admission import MAX_PENDING
from ros_esc.experiment_recording.validate_run import centroid_diagnostic_errors
from test_convergence_detector_policy import (
    centroid_node, _centroid_drive, _PublishedMessages,  # noqa: F401
)


@pytest.fixture
def clock_node(centroid_node, monkeypatch):
    node, now = centroid_node
    steady = [10_000_000_000]
    monkeypatch.setattr(detector.time, 'monotonic_ns', lambda: steady[0])
    monkeypatch.setattr(detector.time, 'monotonic', lambda: steady[0]*1e-9)
    return node, now, steady


def state(node, source_ns, value=AlgorithmState.STATE_SEARCH, run='centroid-run', **overrides):
    message = AlgorithmState()
    message.stamp = node._centroid_time(source_ns)
    message.state = value
    message.state_valid = True
    message.algorithm_profile = 'robust_gaussian_v1'
    message.run_id = run
    message.run_id_valid = True
    for key, value in overrides.items():
        setattr(message, key, value)
    return message


def pose(node, source_ns, x=1., y=2., frame='odom'):
    message = Odometry()
    message.header.stamp = node._centroid_time(source_ns)
    message.header.frame_id = frame
    message.pose.pose.position.x = float(x)
    message.pose.pose.position.y = float(y)
    message.pose.pose.orientation.w = 1.
    return message


def prepared(clock_node):
    node, now, steady = clock_node
    _centroid_drive(node, now, 6.)
    assert node.search_gate.active and node.centroid_state_valid
    assert node.latest_centroid_result.centroids
    assert not any(message.confirmed for message in node.centroid_publisher.messages)
    return node, now, steady


def test_leading_search_keeps_admitted_state_and_history_until_clock_coverage(clock_node):
    node, now, steady = prepared(clock_node)
    receipt = now[0]
    history = node.latest_centroid_result
    epoch = node.centroid_search_epoch
    incoming = state(node, receipt+100_000_000)
    node.algorithm_state_cb(incoming)
    assert node.centroid_state_source_ns == receipt
    assert node.centroid_state_valid and node.search_gate.active
    assert node.latest_centroid_result.reset_sequence == history.reset_sequence
    assert node.latest_centroid_result.start_ns == history.start_ns
    node._centroid_watchdog_cb()
    assert node.centroid_search_epoch == epoch
    now[0] += 100_000_000
    steady[0] += 100_000_000
    node._centroid_watchdog_cb()
    assert node.centroid_state_source_ns == receipt+100_000_000
    assert node.centroid_state_receipt_ns == receipt
    assert node.centroid_search_epoch == epoch
    assert node.latest_centroid_result.reset_sequence == history.reset_sequence


def test_leading_stationary_pose_keeps_admitted_pose_and_history_until_coverage(clock_node):
    node, now, steady = prepared(clock_node)
    receipt = now[0]
    history = node.latest_centroid_result
    incoming = pose(node, receipt+100_000_000, x=1.05)
    node.pose_cb(incoming)
    assert node.centroid_pose_source_ns == receipt
    assert node.latest_centroid_result.reset_sequence == history.reset_sequence
    assert node.latest_centroid_result.start_ns == history.start_ns
    node._centroid_watchdog_cb()
    assert node.centroid_pose_source_ns == receipt
    now[0] += 100_000_000
    steady[0] += 100_000_000
    node._centroid_watchdog_cb()
    assert node.centroid_pose_source_ns == receipt+100_000_000
    assert node.centroid_pose_receipt_ns == receipt
    assert node.latest_centroid_result.stamp_ns == receipt+100_000_000
    assert node.latest_centroid_result.reset_sequence == history.reset_sequence


def test_first_future_search_is_drained_without_active_gate_or_receipt_refresh(clock_node):
    node, now, steady = clock_node
    receipt = now[0]
    incoming = state(node, receipt+100_000_000,
                     state_elapsed_valid=True, state_elapsed_sec=2.)
    node.algorithm_state_cb(incoming)
    assert not node.search_gate.active and node.centroid_search_epoch == 0
    now[0] += 100_000_000
    steady[0] += 100_000_000
    node._centroid_watchdog_cb()
    assert node.search_gate.active and node.centroid_state_valid
    assert node.centroid_search_epoch == 1
    assert node.centroid_state_source_ns == receipt+100_000_000
    assert node.centroid_state_receipt_ns == receipt
    assert node.centroid_epoch_started_ns == receipt+100_000_000-2_000_000_000


def send(node, kind, message):
    return node.algorithm_state_cb(message) if kind == 'state' else node.pose_cb(message)


def sample(node, kind, source_ns):
    return state(node, source_ns) if kind == 'state' else pose(node, source_ns)


def current_source(node, kind):
    return getattr(node, f'centroid_{kind}_source_ns')


def original_receipts(node, kind):
    return (getattr(node, f'centroid_{kind}_receipt_ns'),
            getattr(node, f'centroid_{kind}_receipt_steady_ns'))


@pytest.mark.parametrize('kind', ['state', 'pose'])
@pytest.mark.parametrize('expiry_clock', ['ros', 'steady'])
def test_covered_repeats_preserve_original_receipts_and_expire_the_original_lease(
        clock_node, kind, expiry_clock):
    node, now, steady = prepared(clock_node)
    received_ros, received_steady = now[0], steady[0]
    incoming = sample(node, kind, received_ros+100_000_000)
    send(node, kind, incoming)
    now[0] += 100_000_000
    steady[0] += 100_000_000
    node._centroid_watchdog_cb()
    assert current_source(node, kind) == received_ros+100_000_000
    assert original_receipts(node, kind) == (received_ros, received_steady)
    # Repeat an already admitted identical packet much later. Its acquisition
    # remains fresh when its original receipt expires, so this separates clocks.
    now[0] = received_ros+400_000_000 if expiry_clock == 'ros' else received_ros+100_000_000
    steady[0] = received_steady+400_000_000
    send(node, kind, deepcopy(incoming))
    assert original_receipts(node, kind) == (received_ros, received_steady)
    if expiry_clock == 'ros':
        now[0] = received_ros+490_000_000
        other = 'pose' if kind == 'state' else 'state'
        send(node, other, sample(node, other, now[0]))
        now[0] = received_ros+500_000_001
    else:
        steady[0] = received_steady+500_000_001
    node._centroid_watchdog_cb()
    assert not node.latest_centroid_result.centroids
    assert not node.centroid_publisher.messages[-1].metric_valid
    assert not any(message.confirmed for message in node.centroid_publisher.messages)


@pytest.mark.parametrize('kind', ['state', 'pose'])
def test_paused_clock_pending_duplicates_cannot_extend_receipt_or_later_resurrect(
        clock_node, kind):
    node, now, steady = prepared(clock_node)
    received_ros, received_steady = now[0], steady[0]
    incoming = sample(node, kind, received_ros+100_000_000)
    send(node, kind, incoming)
    steady[0] += 400_000_000
    send(node, kind, deepcopy(incoming))
    steady[0] = received_steady+500_000_001
    node._centroid_watchdog_cb()
    assert not node.centroid_admission.pending[kind]
    assert not node.latest_centroid_result.centroids
    now[0] += 100_000_000
    send(node, kind, deepcopy(incoming))
    node._centroid_watchdog_cb()
    assert current_source(node, kind) != received_ros+100_000_000
    assert not node.latest_centroid_result.centroids
    assert not any(message.confirmed for message in node.centroid_publisher.messages)


@pytest.mark.parametrize('kind', ['state', 'pose'])
def test_exact_500ms_lead_is_covered_without_early_admission(clock_node, kind):
    node, now, steady = prepared(clock_node)
    previous = now[0]
    send(node, kind, sample(node, kind, previous+500_000_000))
    assert current_source(node, kind) == previous
    now[0] += 500_000_000
    steady[0] += 100_000_000
    node._centroid_watchdog_cb()
    assert current_source(node, kind) == now[0]
    assert original_receipts(node, kind)[0] == previous


@pytest.mark.parametrize('kind', ['state', 'pose'])
@pytest.mark.parametrize('fault', ['excessive_future', 'stale', 'regressed', 'invalid'])
def test_invalid_callback_revokes_pending_support_without_relaxing_limits(
        clock_node, kind, fault):
    node, now, _ = prepared(clock_node)
    history = node.latest_centroid_result
    incoming = sample(node, kind, now[0]+100_000_000)
    send(node, kind, incoming)
    source = {'excessive_future': now[0]+500_000_001,
              'stale': now[0]-500_000_001,
              'regressed': now[0]+50_000_000,
              'invalid': now[0]+200_000_000}[fault]
    bad = sample(node, kind, source)
    if fault == 'invalid':
        if kind == 'state':
            bad.run_id_valid = False
        else:
            bad.pose.pose.position.x = float('nan')
    send(node, kind, bad)
    assert not node.centroid_admission.pending[kind]
    assert node.latest_centroid_result.reset_sequence > history.reset_sequence
    assert not node.latest_centroid_result.centroids
    now[0] += 200_000_000
    node._centroid_watchdog_cb()
    assert current_source(node, kind) != node._centroid_stamp_ns(
        incoming.stamp if kind == 'state' else incoming.header.stamp)
    assert not any(message.confirmed for message in node.centroid_publisher.messages)


@pytest.mark.parametrize('fault', ['conflicting_pose', 'invalid_stamp'])
def test_pose_identity_fault_cannot_restore_original_pending_packet(clock_node, fault):
    node, now, _ = prepared(clock_node)
    stamp = now[0]+100_000_000
    incoming = pose(node, stamp)
    node.pose_cb(incoming)
    bad = deepcopy(incoming)
    if fault == 'conflicting_pose':
        bad.pose.pose.position.x = 99.
    else:
        bad.header.stamp.nanosec = 1_000_000_000
    node.pose_cb(bad)
    assert not node.latest_centroid_result.centroids
    now[0] = stamp+1
    node.pose_cb(deepcopy(incoming))
    node._centroid_watchdog_cb()
    assert node.centroid_pose_source_ns != stamp
    assert not node.latest_centroid_result.centroids


def test_stationary_frame_change_resets_at_coverage_then_accepts_new_frame_support(clock_node):
    node, now, _ = prepared(clock_node)
    original, history = now[0], node.latest_centroid_result
    node.pose_cb(pose(node, original+100_000_000, frame='new_frame'))
    assert node.centroid_frame_id == 'odom'
    assert node.latest_centroid_result.reset_sequence == history.reset_sequence
    now[0] += 100_000_000
    node._centroid_watchdog_cb()
    assert node.centroid_frame_id == 'new_frame'
    assert node.latest_centroid_result.reset_sequence > history.reset_sequence
    assert not node.latest_centroid_result.centroids
    reset_sequence = node.latest_centroid_result.reset_sequence
    start = now[0]
    for index in range(1, 62):
        now[0] = start+index*100_000_000
        node.algorithm_state_cb(state(node, now[0]))
        node.pose_cb(pose(node, now[0], frame='new_frame'))
    assert node.centroid_frame_id == 'new_frame'
    assert node.latest_centroid_result.centroids
    assert node.latest_centroid_result.reset_sequence == reset_sequence
    assert not any(message.confirmed for message in node.centroid_publisher.messages)


@pytest.mark.parametrize('kind', ['state', 'pose'])
def test_queued_messages_are_detached_from_publisher_object_mutation(clock_node, kind):
    node, now, _ = prepared(clock_node)
    history = node.latest_centroid_result
    stamp = now[0]+100_000_000
    incoming = sample(node, kind, stamp)
    send(node, kind, incoming)
    if kind == 'state':
        incoming.state = AlgorithmState.STATE_FAILSAFE
        incoming.run_id = 'mutated-after-callback'
    else:
        incoming.pose.pose.position.x = float('nan')
    now[0] = stamp
    node._centroid_watchdog_cb()
    assert current_source(node, kind) == stamp
    assert node.search_gate.active
    assert node.latest_centroid_result.reset_sequence == history.reset_sequence


@pytest.mark.parametrize('stop', [AlgorithmState.STATE_VERIFY_EXTREMUM,
                                  AlgorithmState.STATE_GOAL_HOLD, AlgorithmState.STATE_FAILSAFE])
def test_future_nonsearch_revokes_without_applying_early_or_integrating_older_search(
        clock_node, stop):
    node, now, _ = prepared(clock_node)
    original, epoch = now[0], node.centroid_search_epoch
    node.algorithm_state_cb(state(node, original+50_000_000))
    node.pose_cb(pose(node, original+50_000_000))
    node.algorithm_state_cb(state(node, original+100_000_000, stop))
    assert not node._centroid_state_ready(now[0])
    assert node.centroid_last_valid_state == AlgorithmState.STATE_SEARCH
    assert not node.latest_centroid_result.centroids
    now[0] += 50_000_000
    node._centroid_watchdog_cb()
    # The last admitted logical state can still be SEARCH; the future-stop
    # fence must deny actual authorization and all intervening pose support.
    assert not node._centroid_state_ready(now[0])
    assert node.centroid_search_epoch == epoch
    now[0] += 25_000_000
    node.pose_cb(pose(node, now[0]))
    assert not node.latest_centroid_result.centroids
    assert not any(message.confirmed for message in node.centroid_publisher.messages)
    now[0] = original+100_000_000
    node._centroid_watchdog_cb()
    assert node.centroid_last_valid_state == stop
    assert not node.search_gate.active
    assert not any(message.confirmed for message in node.centroid_publisher.messages)


def test_same_tick_distinct_state_publications_preserve_order(clock_node):
    node, now, _ = clock_node
    original = now[0]
    node.algorithm_state_cb(state(node, original+100_000_000, AlgorithmState.STATE_VERIFY_EXTREMUM))
    node.algorithm_state_cb(state(node, original+100_000_000, AlgorithmState.STATE_SEARCH))
    assert not node.search_gate.active
    now[0] += 100_000_000
    node._centroid_watchdog_cb()
    assert node.centroid_last_valid_state == AlgorithmState.STATE_SEARCH
    assert node.search_gate.active and node.centroid_search_epoch == 1
    assert node.centroid_state_receipt_ns == original


def test_new_run_flushes_old_future_frontier_and_retired_run_cannot_return(clock_node):
    node, now, _ = prepared(clock_node)
    original, epoch = now[0], node.centroid_search_epoch
    node.algorithm_state_cb(state(node, original+100_000_000))
    node.pose_cb(pose(node, original+100_000_000))
    node.algorithm_state_cb(state(node, original+50_000_000, run='new-run'))
    assert not node.search_gate.active
    now[0] += 50_000_000
    node._centroid_watchdog_cb()
    assert node.centroid_run_id == 'new-run'
    assert node.centroid_search_epoch == epoch+1
    assert not node.latest_centroid_result or not node.latest_centroid_result.centroids
    now[0] += 50_000_000
    node._centroid_watchdog_cb()
    assert node.centroid_run_id == 'new-run'
    assert node.centroid_pose_source_ns != original+100_000_000
    node.algorithm_state_cb(state(node, now[0], run='centroid-run'))
    assert node.centroid_run_id == 'new-run'
    assert node.centroid_search_epoch == epoch+1


@pytest.mark.parametrize('fault', ['invalid_state', 'wrong_profile', 'excessive_future'])
def test_invalid_new_run_message_cannot_retire_the_valid_current_run(clock_node, fault):
    node, now, _ = prepared(clock_node)
    original, epoch = now[0], node.centroid_search_epoch
    bad = state(node, original+100_000_000, run='invalid-new-run')
    if fault == 'invalid_state':
        bad.state_valid = False
    elif fault == 'wrong_profile':
        bad.algorithm_profile = 'legacy'
    else:
        bad.stamp = node._centroid_time(original+500_000_001)
    node.algorithm_state_cb(bad)
    now[0] += 200_000_000
    node.algorithm_state_cb(state(node, now[0]))
    assert node.centroid_run_id == 'centroid-run'
    assert node.search_gate.active and node.centroid_state_valid
    assert node.centroid_search_epoch == epoch


def test_epoch_start_uses_queued_publication_time_when_elapsed_unavailable(clock_node):
    node, now, _ = clock_node
    source = now[0]+100_000_000
    node.algorithm_state_cb(state(node, source))
    now[0] += 200_000_000
    node._centroid_watchdog_cb()
    assert node.centroid_epoch_started_ns == source


def test_first_future_search_preserves_its_queued_first_pose_for_new_epoch(clock_node):
    node, now, steady = clock_node
    receipt, source = now[0], now[0]+100_000_000
    node.algorithm_state_cb(state(node, source))
    node.pose_cb(pose(node, source))
    assert not node.search_gate.active
    assert node.centroid_pose_source_ns is None
    now[0], steady[0] = source, steady[0]+100_000_000
    node._centroid_watchdog_cb()
    assert node.centroid_search_epoch == 1
    assert node.centroid_pose_source_ns == source
    assert node.centroid_pose_receipt_ns == receipt
    assert node.latest_centroid_result.stamp_ns == source
    _centroid_drive(node, now, 18.)
    confirmation, = [message for message in node.centroid_publisher.messages if message.confirmed]
    assert node._centroid_stamp_ns(confirmation.history_start) == source
    assert node._centroid_stamp_ns(confirmation.history_end) == source+18_000_000_000


def test_final_future_pose_confirms_only_after_coverage_with_its_original_receipt(clock_node):
    node, now, _ = clock_node
    _centroid_drive(node, now, 17.9)
    receipt, source = now[0], now[0]+100_000_000
    node.algorithm_state_cb(state(node, source))
    node.pose_cb(pose(node, source))
    assert not any(message.confirmed for message in node.centroid_publisher.messages)
    now[0] = source
    node._centroid_watchdog_cb()
    confirmation, = [message for message in node.centroid_publisher.messages if message.confirmed]
    assert node._centroid_stamp_ns(confirmation.receipt_stamp) == receipt
    assert node._centroid_stamp_ns(confirmation.source_stamp) == source
    assert node._centroid_stamp_ns(confirmation.stamp) == source
    assert confirmation.represented_duration_sec == 18.
    assert centroid_diagnostic_errors(
        [confirmation], allow_clock_admission=True,
        expected_source_pose_topic='/selected_delayed_pose', expected_frame_id='odom',
        maximum_source_gap_sec=.5) == []
    # The historical strict timestamp mode still refuses receipt-before-source.
    assert centroid_diagnostic_errors([confirmation], allow_clock_admission=False)


@pytest.mark.parametrize('revoke', ['recording', 'nonsearch', 'steady_expiry'])
def test_queued_final_pose_cannot_confirm_after_authorization_or_original_lease_loss(
        clock_node, revoke):
    node, now, steady = clock_node
    if revoke == 'recording':
        node.recording_ready_required = True
        node._centroid_recording_ready_cb(Bool(data=True))
    _centroid_drive(node, now, 17.9, recording_ready=True if revoke == 'recording' else None)
    assert not any(message.confirmed for message in node.centroid_publisher.messages)
    source = now[0]+100_000_000
    node.pose_cb(pose(node, source))
    if revoke == 'recording':
        node._centroid_recording_ready_cb(Bool(data=False))
    elif revoke == 'nonsearch':
        node.algorithm_state_cb(state(node, source, AlgorithmState.STATE_VERIFY_EXTREMUM))
    else:
        steady[0] += 500_000_001
    now[0] = source
    node._centroid_watchdog_cb()
    assert not any(message.confirmed for message in node.centroid_publisher.messages)
    assert not node.latest_centroid_result.centroids
    assert not node.centroid_admission.pending['pose']


def test_recording_loss_drops_queued_support_without_rearming_confirmed_epoch(clock_node):
    node, now, _ = clock_node
    node.recording_ready_required = True
    _centroid_drive(node, now, 18., recording_ready=True)
    epoch = node.centroid_search_epoch
    assert sum(message.confirmed for message in node.centroid_publisher.messages) == 1
    source = now[0]+100_000_000
    node.algorithm_state_cb(state(node, source))
    node.pose_cb(pose(node, source))
    node._centroid_recording_ready_cb(Bool(data=False))
    now[0] = source
    node._centroid_watchdog_cb()
    node._centroid_recording_ready_cb(Bool(data=True))
    # The old packets may be repeated by transport; they are not new support.
    node.algorithm_state_cb(state(node, source))
    node.pose_cb(pose(node, source))
    assert not node.latest_centroid_result.centroids
    now[0] += 100_000_000
    _centroid_drive(node, now, 18., recording_ready=True)
    assert node.centroid_search_epoch == epoch
    assert node.centroid_confirmed_in_epoch
    assert sum(message.confirmed for message in node.centroid_publisher.messages) == 1


@pytest.mark.parametrize('kind', ['state', 'pose'])
def test_pending_capacity_is_finite_and_fault_discards_unadmitted_history(clock_node, kind):
    node, now, _ = prepared(clock_node)
    original = now[0]
    for index in range(MAX_PENDING+1):
        send(node, kind, sample(node, kind, original+100_000_000+index))
    assert not node.centroid_admission.pending[kind]
    assert not node.latest_centroid_result.centroids
    now[0] += 200_000_000
    node._centroid_watchdog_cb()
    assert current_source(node, kind) == original or current_source(node, kind) is None
    assert not any(message.confirmed for message in node.centroid_publisher.messages)


@pytest.mark.parametrize('rollback_clock', ['ros', 'steady'])
def test_clock_rollback_flushes_future_support_without_late_confirmation(clock_node, rollback_clock):
    node, now, steady = prepared(clock_node)
    original, original_steady = now[0], steady[0]
    node.algorithm_state_cb(state(node, original+100_000_000))
    node.pose_cb(pose(node, original+100_000_000))
    if rollback_clock == 'ros':
        now[0] -= 1
    else:
        steady[0] -= 1
    node._centroid_watchdog_cb()
    assert not node.latest_centroid_result.centroids
    assert not node.centroid_admission.pending['state']
    assert not node.centroid_admission.pending['pose']
    now[0], steady[0] = original+100_000_000, original_steady+100_000_000
    node._centroid_watchdog_cb()
    assert not any(message.confirmed for message in node.centroid_publisher.messages)


@pytest.mark.parametrize('kind', ['state', 'pose'])
def test_positive_configured_one_second_freshness_accepts_750ms_lead_and_rejects_excess(
        monkeypatch, kind):
    # Actual startup parameters exercise the selected configuration owner.
    # The independent pose-gap limit is also one second in this synthetic case,
    # so it cannot mask admission with a separate default500ms gap rejection.
    rclpy.init(args=[
        '--ros-args', '-p', 'use_sim_time:=true',
        '-p', 'algorithm_profile:=robust_gaussian_v1',
        '-p', 'state_gating_enabled:=true',
        '-p', 'convergence_metric_mode:=centroid_windows_v2',
        '-p', 'pose_topic:=/selected_delayed_pose',
        '-p', 'centroid_state_stale_sec:=1.0',
        '-p', 'centroid_pose_stale_sec:=1.0',
        '-p', 'centroid_maximum_gap_sec:=1.0',
    ])
    node = detector.ConvergenceDetector()
    now, steady = [1_000_000_000_000], [10_000_000_000]
    node._centroid_now_ns = lambda: now[0]
    monkeypatch.setattr(detector.time, 'monotonic_ns', lambda: steady[0])
    monkeypatch.setattr(detector.time, 'monotonic', lambda: steady[0]*1e-9)
    for name in ('centroid_publisher', 'algorithm_event_publisher', 'pub',
                 'pub_metric', 'pub_r', 'pub_count'):
        setattr(node, name, _PublishedMessages())
    try:
        assert node.centroid_state_stale_sec == node.centroid_pose_stale_sec == 1.
        prepared((node, now, steady))
        original, original_steady = now[0], steady[0]
        history = node.latest_centroid_result
        source = original+750_000_000
        send(node, kind, sample(node, kind, source))
        assert current_source(node, kind) == original
        assert node.latest_centroid_result.reset_sequence == history.reset_sequence
        now[0], steady[0] = source, original_steady+750_000_000
        node._centroid_watchdog_cb()
        assert current_source(node, kind) == source
        assert original_receipts(node, kind) == (original, original_steady)
        assert node.latest_centroid_result.reset_sequence == history.reset_sequence
        send(node, kind, sample(node, kind, now[0]+1_000_000_001))
        assert not node.centroid_admission.pending[kind]
        assert not node.latest_centroid_result.centroids
        assert not any(message.confirmed for message in node.centroid_publisher.messages)
    finally:
        node.destroy_node()
        rclpy.shutdown()
