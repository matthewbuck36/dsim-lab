"""Independent Arm B admission and unchanged robust-fit integration contracts."""
from copy import deepcopy
from dataclasses import replace
import math
import threading
from types import SimpleNamespace

import numpy as np
import pytest
import rclpy
from rclpy.time import Time
from std_msgs.msg import Bool

from ros_esc.gaussian_fill_node import gaussian_fill_script as gaussian
from ros_esc.gaussian_fill_node.basin_estimator import CostSnapshot, PoseSnapshot
from ros_esc.gaussian_fill_node.fill_registry import FillRegistry
from ros_esc_interfaces.msg import AlgorithmState, StampedFloat64MultiArray, Timekeeper
from ros_esc.v2_stream import set_time, time_to_ns
from test_q5_stationary_fill_protocol import ORIGIN_NS, RUN, request, rehash


@pytest.fixture
def fill_node(request):
    rclpy.init(args=['--ros-args',
        '-p', 'algorithm_profile:=robust_gaussian_v1',
        '-p', 'convergence_metric_mode:=centroid_windows_v2',
        '-p', 'continuous_search_mode:=stationary_v1',
        '-p', 'use_sim_time:=true',
        '-p', 'pose_topic:=/selected/odom',
        '-p', 'recording_ready_required:='+('true' if getattr(request, 'param', False) else 'false'),
    ])
    node = gaussian.GaussianFill()
    now, steady = [ORIGIN_NS+25_000_000_000], [5_000_000_000]
    node.get_clock = lambda: SimpleNamespace(now=lambda: Time(nanoseconds=now[0]))
    node.stationary_fill.steady = lambda: steady[0]
    node.stationary_fill.set_timekeeper(Timekeeper(mode='sim time', start_time=1000.))
    try:
        yield node, now, steady
    finally:
        node.destroy_node()
        rclpy.shutdown()


def live_state(node, now_ns, *, state=AlgorithmState.STATE_DESIGN_OR_MERGE_FILL,
               began_ns=ORIGIN_NS+25_000_000_000, run=RUN, redesign=False):
    msg = AlgorithmState(run_id=run, run_id_valid=True, algorithm_profile='robust_gaussian_v1',
        state=state, state_valid=True, previous_state_valid=True,
        previous_state=AlgorithmState.STATE_ESCAPE_REPULSE if redesign else AlgorithmState.STATE_VERIFY_EXTREMUM,
        state_elapsed_valid=True, state_elapsed_sec=max(0., (now_ns-began_ns)*1e-9),
        weights_valid=True, sensor_weight=1., gaussian_weight=1.)
    set_time(msg.stamp, now_ns)
    node.stationary_fill.state_cb(msg)
    return msg


def seed_support(node, end_ns):
    node.pose_snapshots.clear(); node.cost_snapshots.clear()
    for i in range(81):
        theta = 2*math.pi*i/30.
        radius = .06+.008*math.cos(3*theta)
        x, y = radius*math.cos(theta), .8*radius*math.sin(theta)
        stamp = (end_ns-(80-i)*100_000_000)*1e-9
        node.pose_snapshots.append(PoseSnapshot(stamp, x, y, 0.))
        node.cost_snapshots.append(CostSnapshot(stamp, 0., False,
            -1.+x*x+.5*y*y, 0., False, AlgorithmState.STATE_SEARCH, True))


def active_fill(node):
    clusters = node.fill_registry.active_clusters
    assert len(clusters) == 1
    return clusters[0].active_fill


def test_clock_and_state_waits_keep_original_sample_snapshot_and_receipts(fill_node, monkeypatch):
    node, now, steady = fill_node
    now[0] -= 100_000_000
    seed_support(node, now[0])
    original_poses, original_costs = tuple(node.pose_snapshots), tuple(node.cost_snapshots)
    msg = request()
    node.stationary_fill.request_cb(msg)
    pending = node.stationary_fill.pending
    assert pending is not None and pending.receipt_ns == now[0] and pending.steady_ns == steady[0]
    assert pending.pose_snapshots == original_poses and pending.cost_snapshots == original_costs
    assert node.fill_registry.generation == 0
    # Late transport data is older than the receipt endpoint, yet it was not in
    # either original deque and therefore must not enter the receipt-time fit.
    node.pose_snapshots.append(PoseSnapshot(original_poses[-2].stamp_sec, 99., 99., 0.))
    node.cost_snapshots.append(replace(original_costs[-2], raw_cost=999.))
    msg.confirmation.center_x_m = 999.  # Caller storage also cannot rewrite it.
    windows = []
    original_freeze = gaussian.freeze_sample_window
    def capture(samples, endpoint, config):
        frozen = original_freeze(samples, endpoint, config)
        windows.append((tuple(samples), endpoint, frozen))
        return frozen
    monkeypatch.setattr(gaussian, 'freeze_sample_window', capture)
    now[0] += 100_000_000; steady[0] += 100_000_000
    node.stationary_fill.poll()
    assert node.fill_registry.generation == 0  # Matching DESIGN still missing.
    live_state(node, now[0])
    node.stationary_fill.poll()
    assert windows and windows[0][1] == pending.receipt_ns*1e-9
    assert all(abs(sample.x) < 1. and sample.raw_cost < 0. for sample in windows[0][0])
    assert node.fill_registry.generation == 1, node.stationary_fill.last_reason
    assert active_fill(node).source_timestamp == 25.


def test_b_normalization_matches_existing_legacy_common_fit_and_geometry(fill_node):
    node, now, steady = fill_node
    seed_support(node, now[0])
    # Use the actual legacy entry into the shared robust body with equivalent
    # correlation and no candidate-informed floor; no estimator is substituted.
    legacy = StampedFloat64MultiArray(header='ROBUST_FILL_CREATE', timestamp=25., data=[])
    node._robust_trigger_cb(legacy)
    assert node.fill_registry.generation == 1
    expected = active_fill(node)
    expected_samples = tuple(node.fill_registry.active_clusters[0].samples)
    node.fill_registry = FillRegistry(node.fill_registry.config)
    live_state(node, now[0])
    node.stationary_fill.request_cb(request())
    node.stationary_fill.poll()
    assert node.fill_registry.generation == 1, node.stationary_fill.last_reason
    actual = active_fill(node)
    for field in ('center', 'amplitude', 'covariance', 'sigma_major', 'sigma_minor',
                  'orientation', 'support_radius', 'exit_radius', 'confidence',
                  'sample_count', 'fit_residual', 'fit_condition_number', 'design_escalations'):
        np.testing.assert_equal(getattr(actual, field), getattr(expected, field), err_msg=field)
    actual_samples = tuple(node.fill_registry.active_clusters[0].samples)
    assert [(s.stamp_sec, s.x, s.y, s.raw_cost) for s in actual_samples] == [
        (s.stamp_sec, s.x, s.y, s.raw_cost) for s in expected_samples]


@pytest.mark.parametrize('fault', ['deadline', 'stop', 'run_change', 'origin_change'])
def test_delivered_authority_revocation_during_real_fit_prevents_commit(fill_node, monkeypatch, fault):
    node, now, steady = fill_node
    seed_support(node, now[0])
    live_state(node, now[0])
    original_estimate = gaussian.estimate_basin
    calls = []
    def revoke(*args, **kwargs):
        result = original_estimate(*args, **kwargs)
        calls.append(True)
        if fault == 'deadline':
            now[0] = ORIGIN_NS+30_000_000_000
        elif fault == 'stop':
            now[0] += 1
            live_state(node, now[0], state=AlgorithmState.STATE_FAILSAFE)
        elif fault == 'run_change':
            now[0] += 1
            live_state(node, now[0], run='other-run')
        else:
            node.stationary_fill.set_timekeeper(Timekeeper(mode='sim time', start_time=1001.))
        return result
    monkeypatch.setattr(gaussian, 'estimate_basin', revoke)
    node.stationary_fill.request_cb(request())
    node.stationary_fill.poll()
    assert calls
    assert node.fill_registry.generation == 0 and not node.fill_registry.active_clusters


@pytest.mark.parametrize('clock', ['ros', 'steady'])
def test_pending_request_duplicate_does_not_extend_original_lease(fill_node, clock):
    node, now, steady = fill_node
    now[0] -= 100_000_000
    seed_support(node, now[0])
    msg = request()
    node.stationary_fill.request_cb(msg)
    original = node.stationary_fill.pending
    steady[0] += 400_000_000
    node.stationary_fill.request_cb(deepcopy(msg))
    assert node.stationary_fill.pending is original
    if clock == 'ros': now[0] += 500_000_001
    else:
        now[0] += 100_000_000
        steady[0] += 100_000_001
    live_state(node, now[0])
    node.stationary_fill.poll()
    assert node.fill_registry.generation == 0
    node.stationary_fill.request_cb(deepcopy(msg))
    node.stationary_fill.poll()
    assert node.fill_registry.generation == 0


def test_completed_duplicate_replays_without_refitting_or_recommitting(fill_node, monkeypatch):
    node, now, steady = fill_node
    seed_support(node, now[0]); live_state(node, now[0])
    msg = request()
    node.stationary_fill.request_cb(msg); node.stationary_fill.poll()
    assert node.fill_registry.generation == 1
    def forbidden(*args, **kwargs):
        raise AssertionError('duplicate request refit existing result')
    monkeypatch.setattr(gaussian, 'estimate_basin', forbidden)
    now[0] += 10_000_000_000  # Historical terminal outcome is durable.
    node.stationary_fill.request_cb(deepcopy(msg))
    node.stationary_fill.poll()
    assert node.fill_registry.generation == 1
    conflicting = deepcopy(msg)
    conflicting.confirmation.center_x_m += .1
    conflicting.confirmation.centroid_x_m = [conflicting.confirmation.center_x_m]*6
    node.stationary_fill.request_cb(rehash(conflicting)); node.stationary_fill.poll()
    assert node.fill_registry.generation == 1


def test_wrong_target_identity_never_enters_common_redesign_fit(fill_node, monkeypatch):
    node, now, steady = fill_node
    seed_support(node, now[0]); live_state(node, now[0])
    node.stationary_fill.request_cb(request()); node.stationary_fill.poll()
    assert node.fill_registry.generation == 1
    def forbidden(*args, **kwargs):
        raise AssertionError('invalid target reached estimator')
    monkeypatch.setattr(gaussian, 'estimate_basin', forbidden)
    now[0] += 100_000_000
    live_state(node, now[0], began_ns=now[0], redesign=True)
    redesign = request(redesign=True)
    redesign.request_sequence = 2
    set_time(redesign.stamp, now[0]); set_time(redesign.expires_at, now[0]+5_000_000_000)
    redesign.source_timestamp = (now[0]-ORIGIN_NS)*1e-9
    redesign.target_fill_id, redesign.target_cluster_id, redesign.target_revision = 1, 1, 99
    node.stationary_fill.request_cb(rehash(redesign)); node.stationary_fill.poll()
    assert node.fill_registry.generation == 1


def test_same_tick_predecessor_arriving_after_request_waits_for_design(fill_node):
    node, now, steady = fill_node
    seed_support(node, now[0])
    msg = request()
    node.stationary_fill.request_cb(msg)
    original = node.stationary_fill.pending
    live_state(node, now[0], state=AlgorithmState.STATE_VERIFY_EXTREMUM)
    node.stationary_fill.poll()
    assert node.stationary_fill.pending is original
    assert node.fill_registry.generation == 0
    live_state(node, now[0])
    node.stationary_fill.poll()
    assert node.fill_registry.generation == 1, node.stationary_fill.last_reason


def test_registry_staging_allows_concurrent_delivered_revocation_before_commit(fill_node, monkeypatch):
    node, now, steady = fill_node
    seed_support(node, now[0]); live_state(node, now[0])
    original_stage = node.fill_registry.stage_commit
    delivered = threading.Event()
    threads = []
    def stage(*args, **kwargs):
        def revoke():
            live_state(node, now[0], state=AlgorithmState.STATE_FAILSAFE)
            delivered.set()
        thread = threading.Thread(target=revoke)
        threads.append(thread); thread.start()
        assert delivered.wait(1.), 'registry staging held the authority update lock'
        return original_stage(*args, **kwargs)
    monkeypatch.setattr(node.fill_registry, 'stage_commit', stage)
    try:
        node.stationary_fill.request_cb(request()); node.stationary_fill.poll()
    finally:
        for thread in threads: thread.join(timeout=1.)
    assert delivered.is_set() and threads and all(not thread.is_alive() for thread in threads)
    assert node.fill_registry.generation == 0 and not node.fill_registry.active_clusters


@pytest.mark.parametrize('fill_node', [True], indirect=True)
def test_gaussian_recording_false_then_fresh_true_preserves_one_original_pending_request(fill_node):
    node, now, steady = fill_node
    seed_support(node, now[0]); live_state(node, now[0])
    node.stationary_fill.request_cb(request())
    original = node.stationary_fill.pending
    node.stationary_fill.poll()
    assert node.fill_registry.generation == 0
    assert original is not None
    node.stationary_fill.ready_cb(Bool(data=True))
    node.stationary_fill.poll()
    assert node.fill_registry.generation == 1


@pytest.mark.parametrize('fill_node', [True], indirect=True)
def test_gaussian_recording_revocation_during_fitting_prevents_commit(fill_node, monkeypatch):
    node, now, steady = fill_node
    seed_support(node, now[0]); live_state(node, now[0])
    node.stationary_fill.ready_cb(Bool(data=True))
    original_estimate = gaussian.estimate_basin
    calls = []
    def revoke(*args, **kwargs):
        result = original_estimate(*args, **kwargs)
        node.stationary_fill.ready_cb(Bool(data=False))
        calls.append(True)
        return result
    monkeypatch.setattr(gaussian, 'estimate_basin', revoke)
    node.stationary_fill.request_cb(request()); node.stationary_fill.poll()
    assert calls and node.fill_registry.generation == 0


def test_valid_targeted_redesign_reuses_common_fit_and_echoes_new_correlation(fill_node):
    node, now, steady = fill_node
    seed_support(node, now[0]); live_state(node, now[0])
    node.stationary_fill.request_cb(request()); node.stationary_fill.poll()
    assert node.fill_registry.generation == 1
    original = active_fill(node)
    now[0] += 100_000_000; steady[0] += 100_000_000
    live_state(node, now[0], began_ns=now[0], redesign=True)
    redesign = request(redesign=True)
    redesign.request_sequence = 2
    redesign.target_fill_id, redesign.target_cluster_id, redesign.target_revision = (
        original.fill_id, original.cluster_id, original.revision)
    set_time(redesign.stamp, now[0]); set_time(redesign.expires_at, now[0]+5_000_000_000)
    redesign.source_timestamp = (now[0]-ORIGIN_NS)*1e-9
    node.stationary_fill.request_cb(rehash(redesign)); node.stationary_fill.poll()
    assert node.fill_registry.generation == 2, node.stationary_fill.last_reason
    revised = active_fill(node)
    assert revised.cluster_id == original.cluster_id and revised.revision == original.revision+1
    assert revised.fill_id != original.fill_id
    assert revised.source_timestamp == redesign.source_timestamp
    assert not redesign.candidate_evidence_valid


def test_duplicate_correlation_for_distinct_request_cannot_replace_pending_fit(fill_node):
    node, now, steady = fill_node
    seed_support(node, now[0])
    first = request()
    node.stationary_fill.request_cb(first)
    original = node.stationary_fill.pending
    second = deepcopy(first); second.request_sequence = 2
    node.stationary_fill.request_cb(rehash(second))
    assert node.stationary_fill.pending is original
    assert 'correlation' in node.stationary_fill.last_reason
    live_state(node, now[0]); node.stationary_fill.poll()
    assert node.fill_registry.generation == 1


def test_bounded_request_ledger_rejects_new_identity_and_preserves_completed_retry(fill_node, monkeypatch):
    from ros_esc.gaussian_fill_node import stationary_fill as module
    node, now, steady = fill_node
    seed_support(node, now[0]); live_state(node, now[0])
    monkeypatch.setattr(module, 'MAX_COMMANDS', 1)
    first = request()
    node.stationary_fill.request_cb(first); node.stationary_fill.poll()
    assert node.fill_registry.generation == 1
    second = deepcopy(first); second.request_sequence = 2
    set_time(second.stamp, time_to_ns(first.stamp)+100_000_000)
    second.source_timestamp = (time_to_ns(second.stamp)-ORIGIN_NS)*1e-9
    node.stationary_fill.request_cb(rehash(second))
    assert len(node.stationary_fill.requests) == 1 and node.fill_registry.generation == 1
    node.stationary_fill.request_cb(deepcopy(first))
    assert len(node.stationary_fill.requests) == 1 and node.fill_registry.generation == 1


def test_legacy_insufficient_samples_still_precedes_candidate_payload_decode(fill_node, monkeypatch):
    from ros_esc.supervisor_node.state_machine import CANDIDATE_INFORMED_FILL_HEADER
    node, now, steady = fill_node
    node.pose_snapshots.clear(); node.cost_snapshots.clear()
    failures = []
    original_failure = node._publish_robust_failure
    def capture(*args, **kwargs):
        failures.append(args[1])
        return original_failure(*args, **kwargs)
    def forbidden(*args, **kwargs):
        raise AssertionError('legacy payload decoded before insufficient-sample rejection')
    monkeypatch.setattr(node, '_publish_robust_failure', capture)
    monkeypatch.setattr(gaussian, 'decode_candidate_informed_fill_payload', forbidden)
    node._robust_trigger_cb(StampedFloat64MultiArray(
        header=CANDIDATE_INFORMED_FILL_HEADER, timestamp=25., data=[]))
    assert failures == [30]
    assert node.fill_registry.generation == 0
