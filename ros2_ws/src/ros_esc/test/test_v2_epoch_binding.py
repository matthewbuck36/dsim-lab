"""Authoritative epoch, actual PDE input support and both confirmation arms."""

import copy
import time
from types import SimpleNamespace

import numpy as np
import pytest
from nav_msgs.msg import Odometry
from ros_esc_interfaces.msg import (
    CentroidConvergenceDiagnostics, SearchEpochContext,
    StampedFloat64MultiArray, Timekeeper,
)

from ros_esc.convergence_detector_node.v2_binding import V2DetectorBinding
from ros_esc.convergence_detector_node.centroid_windows import CentroidConfig, CentroidWindowDetector
from ros_esc.pde_history_node.pde_history_script import PDEHistory
from ros_esc.pde_history_node.v2_evidence import V2PdeEvidence, history_sha256
from ros_esc.v2_epoch import EpochBinding
from ros_esc.v2_stream import canonical_json, set_time, stream_contract_id, time_to_ns
from test_v2_stream import descriptor


class Publisher:
    def __init__(self):
        self.messages = []

    def publish(self, message):
        self.messages.append(copy.deepcopy(message))


class Host:
    algorithm_profile = 'robust_gaussian_v1'

    def __init__(self, centroid=False):
        self.now_ns = 1_000_000_000
        self.config = descriptor(2)
        self.params = {'continuous_search_mode': 'rolling_gesc_v2',
                       'v2_run_id': 'epoch-test', 'use_sim_time': True,
                       'v2_stream_config_json': canonical_json(self.config)}
        self.centroid_mode = centroid
        self.metric_mode = 'centroid_windows_v2' if centroid else 'pde_mean_v1'
        self.reset_count = 0
        self.buffers = []
        self.buffer_cb = self.buffers.append
        if centroid:
            self.centroid_detector = CentroidWindowDetector(CentroidConfig())
            self.centroid_search_epoch = 7
            self.centroid_pose_topic = self.config['pose_topic']
        self.pub = Publisher()

    def get_parameter(self, name):
        return SimpleNamespace(value=self.params[name])

    def get_clock(self):
        return SimpleNamespace(now=lambda: SimpleNamespace(nanoseconds=self.now_ns))

    def create_publisher(self, *args):
        return Publisher()

    def create_subscription(self, *args):
        return args

    def create_timer(self, *args, **kwargs):
        return args

    def resolve_topic_name(self, topic):
        return self.config['pose_topic'] if topic == '/odom' else topic

    def _reset_detection_state(self):
        self.reset_count += 1


def context(host, *, epoch=1, sequence=1, state=1, start=1_000_000_000):
    result = SearchEpochContext()
    result.schema_version = 1
    result.run_id, result.frame_id = 'epoch-test', 'odom'
    result.stream_contract_id = stream_contract_id(host.config, 0)
    result.search_epoch, result.context_sequence = epoch, sequence
    result.algorithm_state, result.valid = state, True
    set_time(result.stamp, host.now_ns)
    set_time(result.started_at, start)
    return result


def arm(binding, host, **kwargs):
    keeper = Timekeeper()
    keeper.mode, keeper.start_time = 'sim time', 0.0
    binding.set_timekeeper(keeper)
    binding.receive_context(context(host, **kwargs))


def pose(stamp=1_000_000_000, x=1.0, y=2.0):
    result = Odometry()
    result.header.frame_id = 'odom'
    set_time(result.header.stamp, stamp)
    result.pose.pose.position.x, result.pose.pose.position.y = x, y
    return result


def pde_host():
    node = Host()
    node.U = np.zeros((6, 2))
    node.last_stamp = None
    node.initialized = False
    node.search_epoch_reset_pending = False
    node.cfl, node.lambda_transport = .9, 6.0
    node._legacy_pose_cb = lambda msg: PDEHistory._legacy_pose_cb(node, msg)
    node.publish_history = lambda stamp: PDEHistory.publish_history(node, stamp)
    node.v2_evidence = V2PdeEvidence(node)
    arm(node.v2_evidence.binding, node)
    return node


def test_epoch_is_authoritative_and_duplicate_heartbeat_cannot_refresh_age():
    node = Host()
    resets = []
    binding = EpochBinding(node, resets.append)
    arm(binding, node)
    first = copy.deepcopy(binding.context)
    assert binding.ready() and resets == ['new_search_epoch']
    node.now_ns += 400_000_000
    binding.receive_context(first)
    assert binding.receipt_ns == 1_000_000_000
    node.now_ns += 101_000_000
    assert not binding.ready()
    binding.receive_context(context(node, sequence=2))
    assert binding.ready() and resets == ['new_search_epoch']
    binding.receive_context(context(node, epoch=2, sequence=3, start=node.now_ns))
    assert resets == ['new_search_epoch', 'new_search_epoch']


def test_both_pose_consumers_refuse_routing_outside_stream_identity():
    node = Host(centroid=True)
    node.centroid_pose_topic = '/wrong_pose'
    with pytest.raises(ValueError, match='pose topic'):
        V2DetectorBinding(node)
    node = Host()
    node.resolve_topic_name = lambda topic: '/wrong_pose'
    with pytest.raises(ValueError, match='pose topic'):
        V2PdeEvidence(node)


@pytest.mark.parametrize('change', ['run', 'frame', 'hash', 'start', 'sequence', 'valid'])
def test_conflicting_identity_or_epoch_never_authorizes(change):
    node = Host()
    binding = EpochBinding(node, lambda reason: None)
    arm(binding, node)
    bad = context(node, sequence=2)
    if change == 'run': bad.run_id = 'foreign'
    elif change == 'frame': bad.frame_id = 'map'
    elif change == 'hash': bad.stream_contract_id = 'b' * 64
    elif change == 'start': set_time(bad.started_at, 1_000_000_001)
    elif change == 'sequence': bad.context_sequence = 0
    elif change == 'valid': bad.valid = False
    binding.receive_context(bad)
    assert not binding.ready()


def test_future_heartbeat_waits_for_clock_and_changed_origin_latches():
    node = Host()
    binding = EpochBinding(node, lambda reason: None)
    arm(binding, node)
    future = context(node, sequence=2)
    set_time(future.stamp, node.now_ns + 100_000_000)
    binding.receive_context(future)
    assert not binding.ready()
    node.now_ns += 100_000_000
    assert binding.ready()
    keeper = Timekeeper(mode='sim time', start_time=1.0)
    binding.set_timekeeper(keeper)
    assert binding.origin_fault and not binding.ready()


def test_clock_rollback_requires_new_heartbeat_and_resets_history():
    node = Host()
    resets = []
    binding = EpochBinding(node, resets.append)
    arm(binding, node)
    node.now_ns -= 1
    assert not binding.ready() and 'clock_rollback' in resets


def test_pde_preserves_numerical_owner_and_records_actual_input_support():
    node = pde_host()
    adapter = node.v2_evidence
    adapter.receive_pose(pose())
    assert np.array_equal(node.U, np.tile([1., 2.], (6, 1)))
    node.now_ns += 100_000_000
    adapter.binding.receive_context(context(node, sequence=2))
    adapter.receive_pose(pose(node.now_ns, 2., 2.))
    expected = np.tile([1., 2.], (6, 1))
    expected[0, 0] += .1 * 6.
    assert np.allclose(node.U, expected)
    wire = adapter.publisher.messages[-1]
    assert list(wire.history.data) == list(node.pub.messages[-1].data)
    assert time_to_ns(wire.input_start) == 1_000_000_000
    assert time_to_ns(wire.input_end) == node.now_ns
    assert wire.history.timestamp == pytest.approx(node.now_ns / 1e9)
    assert wire.history_sha256 == history_sha256(wire)


def test_future_pose_waits_without_retiming_original_receipt_or_publication():
    node = pde_host()
    adapter = node.v2_evidence
    message = pose(node.now_ns + 100_000_000)
    adapter.receive_pose(message)
    assert not adapter.publisher.messages
    message.pose.pose.position.x = 900.  # Pending input was detached.
    node.now_ns += 100_000_000
    adapter.poll()
    wire = adapter.publisher.messages[-1]
    assert time_to_ns(wire.input_end) == node.now_ns
    assert time_to_ns(wire.latest_input_receipt) == 1_000_000_000
    assert wire.history.data[0] == 1.


def test_pde_duplicate_and_conflict_cannot_restore_support():
    node = pde_host()
    adapter = node.v2_evidence
    adapter.receive_pose(pose())
    adapter.receive_pose(pose())
    assert len(adapter.publisher.messages) == 1
    adapter.receive_pose(pose(x=3.))
    assert adapter.first_source is None
    assert not adapter.publisher.messages[-1].valid
    adapter.receive_pose(pose())
    assert len([msg for msg in adapter.publisher.messages if msg.valid]) == 1
    node.now_ns += 100_000_000
    adapter.receive_pose(pose(node.now_ns))
    assert time_to_ns(adapter.publisher.messages[-1].input_start) == node.now_ns


def test_pde_new_epoch_resets_old_filter_support_and_rejects_old_pose():
    node = pde_host()
    adapter = node.v2_evidence
    adapter.receive_pose(pose())
    node.now_ns += 100_000_000
    adapter.binding.receive_context(context(node, epoch=2, sequence=2, start=node.now_ns))
    adapter.receive_pose(pose())
    assert adapter.first_source is None
    adapter.receive_pose(pose(node.now_ns, 8., 9.))
    assert np.array_equal(node.U, np.tile([8., 9.], (6, 1)))
    assert adapter.publisher.messages[-1].search_epoch == 2


def legacy_payload():
    result = StampedFloat64MultiArray()
    result.data = [-.1, .03, .01, 1., 2., 1., 2., 0.]
    return result


def test_legacy_confirmation_echoes_epoch_and_actual_input_support_once():
    pde = pde_host()
    pde.v2_evidence.receive_pose(pose())
    node = Host()
    adapter = V2DetectorBinding(node)
    arm(adapter.binding, node)
    adapter.receive_history(pde.v2_evidence.publisher.messages[-1])
    assert len(node.buffers) == 1
    assert adapter.publish_legacy(legacy_payload())
    result = adapter.publisher.messages[-1]
    assert result.history_kind == 'pde_input_support'
    assert result.search_epoch == 1 and result.legacy_r_mean_valid
    assert not result.convergence_score_valid
    assert list(result.legacy_snapshot) == list(legacy_payload().data)
    assert not adapter.publish_legacy(legacy_payload())


def test_pde_fault_notification_revokes_detector_persistence_before_new_history():
    pde = pde_host()
    pde.v2_evidence.receive_pose(pose())
    node = Host()
    detector = V2DetectorBinding(node)
    arm(detector.binding, node)
    original = copy.deepcopy(pde.v2_evidence.publisher.messages[-1])
    detector.receive_history(original)
    assert detector.history is not None
    pde.v2_evidence.receive_pose(pose(x=99.))
    invalid = pde.v2_evidence.publisher.messages[-1]
    assert not invalid.valid
    detector.receive_history(invalid)
    assert detector.history is None and node.reset_count >= 2
    detector.receive_history(original)
    assert detector.history is None
    assert not detector.publish_legacy(legacy_payload())


@pytest.mark.parametrize('mutation', ['hash', 'epoch', 'support', 'duplicate_conflict'])
def test_legacy_delayed_or_tampered_history_is_not_rebound(mutation):
    pde = pde_host()
    pde.v2_evidence.receive_pose(pose())
    node = Host()
    adapter = V2DetectorBinding(node)
    arm(adapter.binding, node)
    msg = copy.deepcopy(pde.v2_evidence.publisher.messages[-1])
    if mutation == 'hash': msg.history.data[0] = 99.
    elif mutation == 'epoch': msg.search_epoch = 2
    elif mutation == 'support': set_time(msg.input_start, 999_999_999)
    else:
        adapter.receive_history(msg)
        msg.history.data[0] = 99.
        msg.history_sha256 = history_sha256(msg)
    adapter.receive_history(msg)
    assert adapter.history is None
    assert not adapter.publish_legacy(legacy_payload())


@pytest.mark.parametrize('metric_mode', ['centroid_windows_v2', 'centroid_two_block_v2'])
def test_centroid_confirmation_retains_local_epoch_only_as_diagnostic(metric_mode):
    node = Host(centroid=True)
    node.metric_mode = metric_mode
    adapter = V2DetectorBinding(node)
    arm(adapter.binding, node, epoch=20)
    diagnostic = CentroidConvergenceDiagnostics()
    diagnostic.metric_mode = metric_mode
    diagnostic.frame_id = 'odom'
    set_time(diagnostic.history_start, node.now_ns)
    set_time(diagnostic.history_end, node.now_ns)
    diagnostic.center_x_m, diagnostic.center_y_m = 2., 3.
    diagnostic.score_m, diagnostic.metric_valid = .02, True
    adapter.latest_pose_steady_ns = time.monotonic_ns()
    assert adapter.publish_centroid(diagnostic)
    result = adapter.publisher.messages[-1]
    assert result.search_epoch == 20 and result.detector_local_epoch == 7
    assert result.history_kind == 'centroid_windows'
    assert result.metric_mode == metric_mode
    assert result.convergence_score_valid and not result.legacy_r_mean_valid
    assert not adapter.publish_centroid(diagnostic)


def centroid_host(monkeypatch):
    node = Host(centroid=True)
    node.steady_ns = 1_000_000_000
    monkeypatch.setattr('ros_esc.convergence_detector_node.v2_binding.time.monotonic_ns',
                        lambda: node.steady_ns)
    node.admitted = []
    node._admitted_pose_cb = lambda msg, receipt_ns: node.admitted.append(
        (copy.deepcopy(msg), receipt_ns))
    adapter = V2DetectorBinding(node)
    arm(adapter.binding, node)
    return node, adapter


def test_centroid_pending_pose_keeps_original_receipts_and_selected_frame(monkeypatch):
    node, adapter = centroid_host(monkeypatch)
    future = pose(node.now_ns + 100_000_000)
    adapter.receive_pose(future)
    future.pose.pose.position.x = 900.
    assert not node.admitted
    node.now_ns += 100_000_000
    adapter.poll()
    admitted, receipt = node.admitted[-1]
    assert receipt == 1_000_000_000
    assert time_to_ns(admitted.header.stamp) == node.now_ns
    assert admitted.pose.pose.position.x == 1.
    foreign = pose(node.now_ns + 1)
    foreign.header.frame_id = 'map'
    adapter.receive_pose(foreign)
    assert len(node.admitted) == 1 and not adapter.pending
    diagnostic = CentroidConvergenceDiagnostics(frame_id='map', metric_valid=True)
    diagnostic.metric_mode = node.metric_mode
    set_time(diagnostic.history_start, node.now_ns)
    set_time(diagnostic.history_end, node.now_ns)
    assert not adapter.publish_centroid(diagnostic)


def test_centroid_publication_rechecks_original_receipt_after_computation(monkeypatch):
    node, adapter = centroid_host(monkeypatch)
    adapter.receive_pose(pose())
    diagnostic = CentroidConvergenceDiagnostics(frame_id='odom', metric_valid=True)
    diagnostic.metric_mode = node.metric_mode
    set_time(diagnostic.history_start, node.now_ns)
    set_time(diagnostic.history_end, node.now_ns)
    node.steady_ns += 500_000_001  # Clock held while computation was delayed.
    assert not adapter.publish_centroid(diagnostic)
    assert not adapter.publisher.messages and adapter.latest_pose_steady_ns is None


@pytest.mark.parametrize('pending', [False, True])
def test_centroid_duplicates_cannot_refresh_paused_clock_freshness(monkeypatch, pending):
    node, adapter = centroid_host(monkeypatch)
    sample = pose(node.now_ns + (100_000_000 if pending else 0))
    adapter.receive_pose(sample)
    node.steady_ns += 400_000_000
    adapter.receive_pose(sample)
    node.steady_ns += 100_000_001
    adapter.poll()
    assert not adapter.pending and adapter.latest_pose_steady_ns is None
    node.now_ns += 100_000_000
    adapter.receive_pose(sample)
    assert len(node.admitted) == (0 if pending else 1)


def test_centroid_conflict_and_source_regression_do_not_restore_history(monkeypatch):
    node, adapter = centroid_host(monkeypatch)
    adapter.receive_pose(pose())
    adapter.receive_pose(pose(x=9.))
    adapter.receive_pose(pose())
    assert len(node.admitted) == 1
    adapter.receive_pose(pose(node.now_ns - 1))
    assert len(node.admitted) == 1
    node.now_ns += 100_000_000
    adapter.receive_pose(pose(node.now_ns))
    assert len(node.admitted) == 2


def test_same_epoch_fault_requires_six_fresh_windows_without_rearming(monkeypatch):
    node, adapter = centroid_host(monkeypatch)
    node.centroid_detector = CentroidWindowDetector(CentroidConfig(window_seconds=.1))
    adapter.reset('fixture_new_core')
    results = []
    node._admitted_pose_cb = lambda msg, receipt_ns: results.extend(
        node.centroid_detector.update(time_to_ns(msg.header.stamp),
                                     (msg.pose.pose.position.x, msg.pose.pose.position.y),
                                     msg.header.frame_id))
    for index in range(6):
        node.now_ns = 1_000_000_000 + index * 100_000_000
        adapter.binding.receive_context(context(node, sequence=index + 2))
        adapter.receive_pose(pose(node.now_ns))
    assert node.centroid_detector.retained_point_count > 0
    assert not any(result.full for result in results)
    adapter.receive_pose(pose(node.now_ns, x=99.))
    assert node.centroid_detector.retained_point_count == 0
    results.clear()
    for index in range(7):
        node.now_ns = 1_600_000_000 + index * 100_000_000
        adapter.binding.receive_context(context(node, sequence=index + 8))
        adapter.receive_pose(pose(node.now_ns))
        if index < 6:
            assert not any(result.full for result in results)
    assert results[-1].full and results[-1].confirmed_event
    adapter.confirmed_epoch = 1
    adapter.reset('another_source_fault')
    assert node.centroid_detector.confirmed
    assert node.centroid_confirmed_in_epoch


def test_unseen_history_older_than_revocation_cannot_revive_persistence():
    pde = pde_host()
    node = Host()
    adapter = V2DetectorBinding(node)
    arm(adapter.binding, node)
    pde.v2_evidence.receive_pose(pose())
    adapter.receive_history(pde.v2_evidence.publisher.messages[-1])
    pde.now_ns = node.now_ns = 1_100_000_000
    pde.v2_evidence.receive_pose(pose(pde.now_ns))
    delayed = copy.deepcopy(pde.v2_evidence.publisher.messages[-1])
    pde.v2_evidence.receive_pose(pose(pde.now_ns, x=99.))
    revoked = pde.v2_evidence.publisher.messages[-1]
    assert delayed.history_sequence < revoked.history_sequence
    adapter.receive_history(revoked)
    adapter.receive_history(delayed)
    assert adapter.history is None
    assert adapter.last_history_sequence == revoked.history_sequence
    pde.now_ns = node.now_ns = 1_200_000_000
    pde.v2_evidence.receive_pose(pose(pde.now_ns))
    adapter.receive_history(pde.v2_evidence.publisher.messages[-1])
    assert adapter.history is not None


def test_malformed_revocation_does_not_advance_authenticated_watermark():
    pde = pde_host()
    pde.v2_evidence.receive_pose(pose())
    node = Host()
    adapter = V2DetectorBinding(node)
    arm(adapter.binding, node)
    valid = pde.v2_evidence.publisher.messages[-1]
    bad = copy.deepcopy(valid)
    bad.valid = False
    bad.history_sequence = 999
    bad.history_sha256 = history_sha256(bad)
    adapter.receive_history(bad)
    assert adapter.last_history_sequence == 0
    adapter.receive_history(valid)
    assert adapter.history is not None


@pytest.mark.parametrize('expired', [False, True])
def test_recurrent_binding_uses_authoritative_epoch_and_original_pose_lease(monkeypatch, expired):
    from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, RECURRENT_HISTORY_KIND
    from ros_esc.convergence_detector_node.recurrent_geometry import RecurrentGeometryDetector
    from ros_esc_interfaces.msg import RecurrentConvergenceDiagnostics
    node = Host(centroid=True)
    node.metric_mode = RECURRENT_MODE
    node.centroid_detector = RecurrentGeometryDetector()
    steady = 1_000_000_000
    monkeypatch.setattr('ros_esc.convergence_detector_node.v2_binding.time.monotonic_ns', lambda: steady)
    adapter = V2DetectorBinding(node)
    arm(adapter.binding, node, epoch=20)
    assert node.centroid_detector.epoch_start_ns == 1_000_000_000
    assert adapter.subscription is None and adapter.pose_timer is not None
    node.now_ns = 13_000_000_000
    adapter.binding.receive_context(context(node, epoch=20, sequence=2))
    diagnostic = RecurrentConvergenceDiagnostics(frame_id='odom', metric_valid=True)
    diagnostic.metric_mode = RECURRENT_MODE
    set_time(diagnostic.history_start, 1_000_000_000)
    set_time(diagnostic.history_end, node.now_ns)
    diagnostic.center_x_m, diagnostic.center_y_m, diagnostic.score_m = 2., 3., .02
    adapter.latest_pose_steady_ns = steady - (500_000_001 if expired else 0)
    assert adapter.publish_centroid(diagnostic) is (not expired)
    if not expired:
        message = adapter.publisher.messages[-1]
        assert message.history_kind == RECURRENT_HISTORY_KIND and message.search_epoch == 20
        assert time_to_ns(message.history_start) == 1_000_000_000
        assert time_to_ns(message.source_stamp) == 13_000_000_000
        assert message.convergence_score_m == .02 and not message.legacy_r_mean_valid
        assert not message.legacy_snapshot
        adapter.reset('source_gap')
        adapter.latest_pose_steady_ns = steady
        assert not adapter.publish_centroid(diagnostic)  # Source fault cannot rearm same epoch.
    else:
        assert not adapter.publisher.messages
