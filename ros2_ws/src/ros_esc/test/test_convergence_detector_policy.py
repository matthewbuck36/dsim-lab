"""Focused robust convergence lifecycle and motion-policy tests."""

import numpy as np
import pytest
import rclpy
from rclpy.serialization import deserialize_message, serialize_message
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool

from ros_esc.convergence_detector_node.convergence_detector_node_script import (
    CROSSING_COUNT,
    CENTROID_WINDOWS_V2,
    PDE_MEAN_V1,
    QUALIFIED_DWELL,
    ConvergenceDetector,
    QualifiedDwellPolicy,
    motion_qualified,
    SearchEpochGate,
    trajectory_motion_statistics,
)
from ros_esc_interfaces.msg import AlgorithmState, CentroidConvergenceDiagnostics


class _PublishedMessages:
    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(message)


@pytest.fixture
def centroid_node():
    rclpy.init(args=[
        '--ros-args',
        '-p', 'algorithm_profile:=robust_gaussian_v1',
        '-p', 'state_gating_enabled:=true',
        '-p', 'convergence_metric_mode:=centroid_windows_v2',
        '-p', 'pose_topic:=/selected_delayed_pose',
    ])
    node = ConvergenceDetector()
    now = [1_000_000_000_000]
    node._centroid_now_ns = lambda: now[0]
    node.centroid_publisher = _PublishedMessages()
    node.algorithm_event_publisher = _PublishedMessages()
    node.pub = _PublishedMessages()
    node.pub_metric = _PublishedMessages()
    node.pub_r = _PublishedMessages()
    node.pub_count = _PublishedMessages()
    try:
        yield node, now
    finally:
        node.destroy_node()
        rclpy.shutdown()


def _centroid_state(node, now, value=AlgorithmState.STATE_SEARCH, **overrides):
    message = _state(value, run_id='centroid-run')
    message.algorithm_profile = 'robust_gaussian_v1'
    message.stamp = node._centroid_time(now[0])
    for key, value in overrides.items():
        setattr(message, key, value)
    node.algorithm_state_cb(message)


def _centroid_pose(node, now, x=1.0, y=2.0, frame='odom', lag_ns=0):
    message = Odometry()
    message.header.stamp = node._centroid_time(now[0] - lag_ns)
    message.header.frame_id = frame
    message.pose.pose.position.x = float(x)
    message.pose.pose.position.y = float(y)
    message.pose.pose.orientation.w = 1.0
    node.pose_cb(message)


def _centroid_drive(node, now, duration_sec, position=None, recording_ready=None):
    start = now[0]
    for step in range(round(duration_sec * 10) + 1):
        now[0] = start + step * 100_000_000
        _centroid_state(node, now)
        if recording_ready is not None:
            node._centroid_recording_ready_cb(Bool(data=recording_ready))
        point = position(step / 10.0) if position else (1.0, 2.0)
        _centroid_pose(node, now, *point)


def _confirmations(node):
    return [message for message in node.centroid_publisher.messages if message.confirmed]


def _state(value, run_id='run-a', valid=True):
    message = AlgorithmState()
    message.state = value
    message.state_valid = valid
    message.run_id = run_id
    message.run_id_valid = True
    return message


def test_search_epoch_gate_resets_only_on_typed_boundaries_and_new_runs():
    gate = SearchEpochGate(enabled=True)

    assert gate.active is False
    assert gate.update(_state(AlgorithmState.STATE_SEARCH)) == gate.ENTERED
    assert gate.active is True
    assert gate.update(_state(AlgorithmState.STATE_SEARCH)) is None
    assert gate.update(_state(AlgorithmState.STATE_VERIFY_EXTREMUM)) == gate.LEFT
    assert gate.active is False
    assert gate.update(_state(AlgorithmState.STATE_VERIFY_EXTREMUM)) is None
    assert gate.update(_state(AlgorithmState.STATE_SEARCH)) == gate.ENTERED
    assert gate.update(
        _state(AlgorithmState.STATE_SEARCH, run_id='run-b')
    ) == gate.ENTERED


def test_search_epoch_gate_disarms_invalid_state_and_legacy_gate_stays_open():
    gated = SearchEpochGate(enabled=True)
    assert gated.update(_state(AlgorithmState.STATE_SEARCH)) == gated.ENTERED
    assert gated.update(
        _state(AlgorithmState.STATE_SEARCH, valid=False)
    ) == gated.LEFT
    assert gated.active is False

    legacy = SearchEpochGate(enabled=False)
    assert legacy.active is True
    assert legacy.update(_state(AlgorithmState.STATE_FAILSAFE)) is None
    assert legacy.active is True


def test_motion_policy_rejects_translation_and_accepts_compact_orbit():
    translation = np.column_stack(
        (np.linspace(0.0, 0.30, 301), np.zeros(301))
    )
    path, net, efficiency = trajectory_motion_statistics(translation)
    assert path == pytest.approx(0.30)
    assert net == pytest.approx(0.30)
    assert efficiency == pytest.approx(1.0)
    assert not motion_qualified(path, efficiency, 0.20, 0.35)

    angles = np.linspace(0.0, 2.0 * np.pi, 301)
    orbit = np.column_stack((0.15 * np.cos(angles), 0.15 * np.sin(angles)))
    path, net, efficiency = trajectory_motion_statistics(orbit)
    assert path > 0.90
    assert net == pytest.approx(0.0, abs=1e-12)
    assert efficiency == pytest.approx(0.0, abs=1e-12)
    assert motion_qualified(path, efficiency, 0.20, 0.35)


def test_motion_policy_rejects_stationary_and_short_histories():
    stationary = np.zeros((301, 2), dtype=np.float64)
    path, net, efficiency = trajectory_motion_statistics(stationary)
    assert (path, net, efficiency) == (0.0, 0.0, 0.0)
    assert not motion_qualified(path, efficiency, 0.20, 0.35)

    with pytest.raises(ValueError):
        trajectory_motion_statistics(np.zeros((1, 2), dtype=np.float64))


def test_qualified_dwell_accumulates_only_below_entry_and_confirms_once():
    policy = QualifiedDwellPolicy(dwell_sec=2.0, exit_metric=0.5)

    assert policy.update(0.0, -0.1) is False
    assert policy.update(1.0, -0.1) is False
    assert policy.accumulated_sec == pytest.approx(1.0)

    assert policy.update(1.5, 0.1) is False
    assert policy.episode_active is True
    assert policy.accumulated_sec == pytest.approx(1.0)
    assert policy.update(2.0, -0.1) is False
    assert policy.update(3.0, -0.1) is True
    assert policy.confirmed is True
    assert policy.accumulated_sec == pytest.approx(2.0)
    assert policy.update(4.0, -0.1) is False


def test_qualified_dwell_hysteresis_rearms_only_above_exit():
    policy = QualifiedDwellPolicy(dwell_sec=1.0, exit_metric=0.5)
    policy.update(0.0, -0.1)
    assert policy.update(1.0, -0.1) is True

    assert policy.update(2.0, 0.5) is False
    assert policy.confirmed is True
    assert policy.update(3.0, 0.500001) is False
    assert policy.confirmed is False
    assert policy.episode_active is False

    policy.update(4.0, -0.1)
    assert policy.update(5.0, -0.1) is True


def test_qualified_dwell_resets_on_motion_loss_invalidity_and_backward_time():
    policy = QualifiedDwellPolicy(dwell_sec=2.0, exit_metric=0.5)
    policy.update(0.0, -0.1)
    policy.update(1.0, -0.1)
    assert policy.accumulated_sec == pytest.approx(1.0)

    assert policy.update(2.0, -0.1, qualified=False) is False
    assert policy.accumulated_sec == 0.0
    policy.update(3.0, -0.1)
    assert policy.update(4.0, np.nan, valid=False) is False
    assert policy.episode_active is False

    policy.update(5.0, -0.1)
    assert policy.update(4.0, -0.1) is False
    assert policy.accumulated_sec == 0.0
    assert policy.episode_active is True


@pytest.mark.parametrize(
    ("dwell_sec", "exit_metric"),
    [
        (0.0, 0.5),
        (np.nan, 0.5),
        (1.0, 0.0),
        (1.0, np.nan),
    ],
)
def test_qualified_dwell_rejects_invalid_configuration(
    dwell_sec,
    exit_metric,
):
    with pytest.raises(ValueError):
        QualifiedDwellPolicy(dwell_sec, exit_metric)


def test_detector_resets_counter_and_decay_on_typed_search_boundaries():
    rclpy.init(
        args=[
            '--ros-args',
            '-p',
            'algorithm_profile:=robust_gaussian_v1',
            '-p',
            'state_gating_enabled:=true',
        ]
    )
    node = ConvergenceDetector()
    try:
        assert node.metric_mode == PDE_MEAN_V1
        assert node.pose_subscriber is None
        assert node.centroid_publisher is None
        assert node.confirmation_policy == CROSSING_COUNT
        node.count_remaining = 1
        node.first_time = 10.0
        node.t0 = 11.0
        node.last_metric = -0.1

        node.algorithm_state_cb(_state(AlgorithmState.STATE_SEARCH))
        assert node.search_gate.active is True
        assert node.count_remaining == node.count_start
        assert node.first_time is None
        assert node.t0 is None
        assert node.last_metric is None

        node.first_time = 12.0
        node.algorithm_state_cb(_state(AlgorithmState.STATE_SEARCH))
        assert node.first_time == 12.0

        node.algorithm_state_cb(_state(AlgorithmState.STATE_VERIFY_EXTREMUM))
        assert node.search_gate.active is False
        assert node.first_time is None
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_centroid_node_confirms_after_18_source_seconds_without_legacy_output(centroid_node):
    node, now = centroid_node
    assert node.metric_mode == CENTROID_WINDOWS_V2
    assert node.sub is None
    assert node.pose_subscriber.topic_name == '/selected_delayed_pose'
    _centroid_drive(node, now, 17.9)
    assert not _confirmations(node)
    now[0] += 100_000_000
    _centroid_state(node, now)
    _centroid_pose(node, now)

    confirmation, = _confirmations(node)
    assert confirmation.source_stamp.sec == 1018
    assert confirmation.history_start.sec == 1000
    assert confirmation.history_end.sec == 1018
    assert confirmation.represented_duration_sec == 18.0
    assert confirmation.score_m == pytest.approx(0.0, abs=1e-12)
    assert confirmation.center_x_m == pytest.approx(1.0)
    assert confirmation.center_y_m == pytest.approx(2.0)
    assert confirmation.completed_window_count == 6
    assert len(confirmation.displacement_m) == 5
    assert confirmation.sample_count == 181
    assert confirmation.metric_valid and confirmation.source_valid
    assert confirmation.source_pose_topic == '/selected_delayed_pose'
    assert node.first_time is None and node.t0 is None
    assert not node.pub.messages
    assert not node.pub_metric.messages
    assert not node.pub_r.messages
    assert not node.pub_count.messages
    event = node.algorithm_event_publisher.messages[-1]
    assert 'score_m' in event.value_names
    assert 'r_mean_m2' not in event.value_names
    assert not event.source_timestamp_valid


def test_centroid_node_circle_freezes_six_window_mean_and_confirms_once(centroid_node):
    node, now = centroid_node
    _centroid_drive(node, now, 24.0, position=lambda t: (
        1.0 + 0.15 * np.cos(2 * np.pi * t / 3.0),
        2.0 + 0.15 * np.sin(2 * np.pi * t / 3.0),
    ))
    confirmation, = _confirmations(node)
    assert confirmation.center_x_m == pytest.approx(1.0, abs=1e-12)
    assert confirmation.center_y_m == pytest.approx(2.0, abs=1e-12)
    assert confirmation.confinement_radius_m == pytest.approx(0.15, abs=1e-12)
    assert node.centroid_publisher.messages[-1].eligible
    assert not node.centroid_publisher.messages[-1].confirmed
    assert node.centroid_publisher.messages[-1].confirmation_sequence == 1


@pytest.mark.parametrize('fault', ['identity', 'invalid_state', 'stale_state', 'future_state'])
def test_centroid_invalid_state_does_not_rearm_same_search_epoch(centroid_node, fault):
    node, now = centroid_node
    _centroid_drive(node, now, 18.0)
    epoch = node.centroid_search_epoch
    now[0] += 100_000_000
    if fault == 'identity':
        _centroid_state(node, now, run_id_valid=False)
    elif fault == 'invalid_state':
        _centroid_state(node, now, state_valid=False)
    else:
        offset = -1_000_000_000 if fault == 'stale_state' else 1_000_000_000
        _centroid_state(node, now, stamp=node._centroid_time(now[0] + offset))
    assert not node._centroid_state_ready(now[0])
    assert not node.centroid_publisher.messages[-1].metric_valid
    _centroid_drive(node, now, 18.0)
    assert node.centroid_search_epoch == epoch
    assert len(_confirmations(node)) == 1


def test_centroid_valid_search_boundary_and_new_run_rearm(centroid_node):
    node, now = centroid_node
    _centroid_drive(node, now, 18.0)
    now[0] += 100_000_000
    _centroid_state(node, now, AlgorithmState.STATE_VERIFY_EXTREMUM)
    _centroid_pose(node, now)
    assert not node.centroid_publisher.messages[-1].eligible
    # The acquisition just received outside SEARCH cannot be relabeled by an
    # identical retransmission. Rebuild from the next genuine source sample.
    now[0] += 100_000_000
    _centroid_drive(node, now, 18.0)
    assert len(_confirmations(node)) == 2
    assert node.centroid_search_epoch == 2
    now[0] += 100_000_000
    _centroid_state(node, now, run_id='another-run')
    assert node.centroid_search_epoch == 3
    assert not node.centroid_confirmed_in_epoch


def test_centroid_source_and_state_freshness_reset_support(centroid_node):
    node, now = centroid_node
    _centroid_drive(node, now, 6.0)
    assert node.latest_centroid_result.centroids
    now[0] += 100_000_000
    _centroid_state(node, now)
    _centroid_pose(node, now, lag_ns=600_000_000)
    assert node.centroid_publisher.messages[-1].reset_reason == 'stale_or_future_pose'
    assert not node.centroid_publisher.messages[-1].source_valid
    assert not node.centroid_publisher.messages[-1].metric_valid
    _centroid_drive(node, now, 6.0)
    now[0] += 600_000_000
    node._centroid_watchdog_cb()
    assert node.centroid_publisher.messages[-1].reset_reason == 'stale_algorithm_state'
    assert not node.latest_centroid_result.centroids
    _centroid_state(node, now)
    node._centroid_watchdog_cb()
    assert node.centroid_publisher.messages[-1].reset_reason == 'stale_pose'
    assert not _confirmations(node)


def test_centroid_frame_and_nonfinite_position_reset_without_rearming(centroid_node):
    node, now = centroid_node
    _centroid_drive(node, now, 18.0)
    now[0] += 100_000_000
    _centroid_state(node, now)
    _centroid_pose(node, now, frame='another_frame')
    assert node.centroid_publisher.messages[-1].reset_reason == 'frame_changed'
    assert not node.centroid_publisher.messages[-1].metric_valid
    now[0] += 100_000_000
    _centroid_state(node, now)
    _centroid_pose(node, now, x=np.nan)
    assert node.centroid_publisher.messages[-1].reset_reason == 'invalid_position'
    assert not node.centroid_publisher.messages[-1].source_valid
    _centroid_drive(node, now, 18.0)
    assert len(_confirmations(node)) == 1


def test_centroid_readiness_blocks_pre_authorization_history_and_stale_heartbeat(centroid_node):
    node, now = centroid_node
    node.recording_ready_required = True
    _centroid_drive(node, now, 20.0)
    assert not _confirmations(node)
    assert not node.latest_centroid_result.centroids
    node._centroid_recording_ready_cb(Bool(data=True))
    _centroid_drive(node, now, 18.0, recording_ready=True)
    confirmation, = _confirmations(node)
    assert confirmation.history_start.sec == 1020
    node.recording_ready_receipt_monotonic -= 1.0
    node._centroid_watchdog_cb()
    assert node.centroid_publisher.messages[-1].reset_reason == 'recording_not_ready'
    assert not node.centroid_publisher.messages[-1].eligible
    assert node.centroid_confirmed_in_epoch


def test_centroid_readiness_expiry_during_update_requires_fresh_support(
        centroid_node, monkeypatch):
    node, now = centroid_node
    node.recording_ready_required = True
    wall_now = [10.0]
    monkeypatch.setattr(
        'ros_esc.convergence_detector_node.convergence_detector_node_script.time.monotonic',
        lambda: wall_now[0],
    )
    _centroid_drive(node, now, 17.9, recording_ready=True)
    original_update = node.centroid_detector.update

    def expire_after_update(*args):
        results = original_update(*args)
        assert any(result.confirmed_event for result in results)
        wall_now[0] += node.recording_ready_stale_sec + 0.01
        return results

    monkeypatch.setattr(node.centroid_detector, 'update', expire_after_update)
    now[0] += 100_000_000
    _centroid_state(node, now)
    _centroid_pose(node, now)
    assert not _confirmations(node)
    assert node.centroid_detector.confirmed  # Numerical eligibility was reached.
    assert not node.centroid_confirmed_in_epoch
    assert node.centroid_confirmation_sequence == 0
    assert node.centroid_publisher.messages[-1].reset_reason == 'recording_not_ready'
    assert not node.latest_centroid_result.centroids
    epoch = node.centroid_search_epoch

    monkeypatch.setattr(node.centroid_detector, 'update', original_update)
    # The last acquisition was consumed before readiness expired. Its repeat
    # cannot seed new support or renew either original receipt.
    now[0] += 100_000_000
    fresh_start = now[0]
    _centroid_drive(node, now, 17.9, recording_ready=True)
    assert not _confirmations(node)
    now[0] += 100_000_000
    _centroid_state(node, now)
    node._centroid_recording_ready_cb(Bool(data=True))
    _centroid_pose(node, now)
    confirmation, = _confirmations(node)
    assert confirmation.history_start == node._centroid_time(fresh_start)
    assert confirmation.history_end == node._centroid_time(fresh_start + 18_000_000_000)
    assert confirmation.confirmation_sequence == 1
    assert confirmation.search_epoch == epoch
    # Partial-window publications and later completed windows cannot repeat it.
    _centroid_drive(node, now, 3.0, recording_ready=True)
    assert len(_confirmations(node)) == 1


def test_centroid_publication_failure_does_not_consume_epoch(centroid_node, monkeypatch):
    node, now = centroid_node
    _centroid_drive(node, now, 17.9)
    publish = node.centroid_publisher.publish

    def fail_confirmation(message):
        if message.confirmed:
            raise RuntimeError('typed publication failed')
        publish(message)

    monkeypatch.setattr(node.centroid_publisher, 'publish', fail_confirmation)
    now[0] += 100_000_000
    _centroid_state(node, now)
    with pytest.raises(RuntimeError, match='typed publication failed'):
        _centroid_pose(node, now)
    assert not node.centroid_confirmed_in_epoch
    assert node.centroid_confirmation_sequence == 0
    assert not _confirmations(node)

    monkeypatch.setattr(node.centroid_publisher, 'publish', publish)
    now[0] += 100_000_000
    _centroid_drive(node, now, 2.8)
    assert node.centroid_publisher.messages[-1].eligible
    assert not _confirmations(node)  # Partial-window status is not a new event.
    now[0] += 100_000_000
    _centroid_state(node, now)
    _centroid_pose(node, now)
    confirmation, = _confirmations(node)
    assert confirmation.confirmation_sequence == 1
    assert node.centroid_confirmed_in_epoch


def test_centroid_stale_republished_state_does_not_refresh_authorization(centroid_node):
    node, now = centroid_node
    _centroid_state(node, now)
    original_stamp = now[0]
    now[0] += 600_000_000
    _centroid_state(node, now, stamp=node._centroid_time(original_stamp))
    _centroid_pose(node, now)
    assert not node._centroid_state_ready(now[0])
    assert not node.latest_centroid_result.centroids
    assert not _confirmations(node)


def test_centroid_duplicate_pose_does_not_supply_time_and_state_rollback_is_invalid(centroid_node):
    node, now = centroid_node
    _centroid_drive(node, now, 17.9)
    source_ns = now[0]
    for step in range(1, 5):
        now[0] = source_ns + step * 100_000_000
        _centroid_state(node, now)
        _centroid_pose(node, now, lag_ns=now[0] - source_ns)
    assert not _confirmations(node)
    _centroid_state(node, now, stamp=node._centroid_time(now[0] - 100_000_000))
    assert node.centroid_publisher.messages[-1].reset_reason == 'algorithm_state_time_rollback'
    assert not node._centroid_state_ready(now[0])


def test_centroid_confirmation_uses_generated_ros_type_without_unit_loss(centroid_node):
    node, now = centroid_node
    _centroid_drive(node, now, 18.0)
    confirmation, = _confirmations(node)
    received = deserialize_message(
        serialize_message(confirmation), CentroidConvergenceDiagnostics
    )
    assert received == confirmation
    assert received.source_stamp.sec == 1018
    assert received.window_start[0].sec == 1000
    assert received.window_end[-1].sec == 1018
    assert received.confirmation_sequence == 1
    assert received.score_m == pytest.approx(0.0, abs=1e-12)


def test_detector_resets_qualified_dwell_on_search_epoch_boundaries():
    rclpy.init(
        args=[
            "--ros-args",
            "-p",
            "algorithm_profile:=robust_gaussian_v1",
            "-p",
            "state_gating_enabled:=true",
            "-p",
            f"convergence_confirmation_policy:={QUALIFIED_DWELL}",
            "-p",
            "convergence_confirmation_dwell_sec:=6.0",
            "-p",
            "convergence_confirmation_exit_threshold_scale:=1.5",
        ]
    )
    node = ConvergenceDetector()
    try:
        assert node.confirmation_policy == QUALIFIED_DWELL
        node.algorithm_state_cb(_state(AlgorithmState.STATE_SEARCH))
        node.qualified_dwell_policy.update(10.0, -0.1)
        node.qualified_dwell_policy.update(12.0, -0.1)
        assert node.qualified_dwell_policy.accumulated_sec == pytest.approx(2.0)

        node.algorithm_state_cb(
            _state(AlgorithmState.STATE_VERIFY_EXTREMUM)
        )
        assert node.search_gate.active is False
        assert node.qualified_dwell_policy.accumulated_sec == 0.0
        assert node.qualified_dwell_policy.episode_active is False
    finally:
        node.destroy_node()
        rclpy.shutdown()
