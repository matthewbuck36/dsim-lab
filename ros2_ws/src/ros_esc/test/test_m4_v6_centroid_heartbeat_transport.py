"""Real detector/DDS status cadence and original receipts.

Default-off cases retain the existing coverage failure as an asserted baseline.
Enabled cases require the separately adopted heartbeat implementation. Synthetic
poses/clocks/epochs exercise real owners; W=.1s is a finite transport-test choice,
not the pilot's W=6s or an empirical convergence result. No Gazebo/model/bag runs.
Subscriber receipt time supplies the existing validator's record-row ordering;
these are actual DDS callbacks, not reconstructed bag callback provenance.
"""
from contextlib import contextmanager
import json
import os
import time
from pathlib import Path

import pytest
import rclpy
from nav_msgs.msg import Odometry
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosgraph_msgs.msg import Clock
from std_msgs.msg import Bool
from ros_esc_interfaces.msg import (
    AlgorithmEvent, AlgorithmState, CentroidConvergenceDiagnostics, DetectorConfirmation,
    SearchEpochContext, Timekeeper,
)
from ros_esc.convergence_detector_node.convergence_detector_node_script import ConvergenceDetector
from ros_esc.experiment_recording.validate_run import centroid_diagnostic_errors, centroid_stream_errors
from ros_esc.experiment_recording import validate_run as recording_validator
from ros_esc.experiment_recording.record_run import applicable_topics, load_manifest, require_selected_algorithm_topics
from ros_esc.v2_stream import SUPPORTED_GEOMETRY, TOPIC_KEYS, canonical_json, set_time, stream_contract_id, time_to_ns

MODES = ('centroid_windows_v2', 'centroid_two_block_v2')
SEARCH, VERIFY = AlgorithmState.STATE_SEARCH, AlgorithmState.STATE_VERIFY_EXTREMUM
STEP_NS = 100_000_000
HEARTBEAT_OPTION = 'centroid_invalid_status_heartbeat_enabled'


class Transport:
    """One finite real-node fixture; every wait shares a 28s work deadline."""
    def __init__(self, mode, moving, selection, observe_events=False):
        assert os.environ.get('ROS_LOCALHOST_ONLY') == '1'
        assert os.environ.get('ROS_DOMAIN_ID', '').isdigit(), 'root must reserve the test domain'
        self.end = time.monotonic() + 28.
        self.nodes, self.executor = [], None
        self.mode, self.moving, self.now_ns = mode, moving, 0
        self.epoch, self.epoch_start, self.context_sequence = 0, 0, 0
        self.state = None
        self.run_id = 'heartbeat-transport'
        self.rows = {name: [] for name in ('diagnostic', 'clock', 'ready', 'confirmation', 'state')}
        self.config = dict(schema_version=2, selected_channel=0, frame_id='odom',
            cost_key_basis='model_input_time', sensor_geometry_config_sha256='a'*64,
            sensor_geometry=dict(SUPPORTED_GEOMETRY),
            **{key: '/heartbeat_transport/'+key for key in TOPIC_KEYS})
        params = dict(use_sim_time='true', algorithm_profile='robust_gaussian_v1',
            continuous_search_mode='rolling_gesc_v2' if moving else 'stationary_v1',
            state_gating_enabled='true', convergence_metric_mode=mode,
            centroid_window_sec='0.1', centroid_epsilon_m='0.18',
            centroid_maximum_radius_m='0.5', centroid_maximum_gap_sec='0.5',
            centroid_pose_stale_sec='0.5', centroid_state_stale_sec='0.5',
            recording_ready_required='true', recording_ready_stale_sec='0.5',
            recording_ready_topic='/heartbeat_transport/ready',
            algorithm_state_topic='/heartbeat_transport/state',
            convergence_diagnostics_topic='/heartbeat_transport/diagnostics',
            pose_topic=self.config['pose_topic'])
        diagnostic_type = CentroidConvergenceDiagnostics
        if mode == 'recurrent_geometry_v3':
            from ros_esc_interfaces.msg import RecurrentConvergenceDiagnostics
            diagnostic_type = RecurrentConvergenceDiagnostics
            params['recurrent_diagnostics_topic'] = '/heartbeat_transport/diagnostics'
        if moving:
            params.update(v2_run_id=self.run_id,
                          v2_stream_config_json="|-\n  "+canonical_json(self.config))
        if selection is not None:
            params[HEARTBEAT_OPTION] = 'true' if selection else 'false'
        if observe_events:
            params.update(enable_observability='true',
                          algorithm_event_topic='/heartbeat_transport/events')
        args = ['--ros-args']
        for name, value in params.items():
            args.extend(['-p', name+':='+value])
        rclpy.init(args=args)
        try:
            self.node = ConvergenceDetector(); self.nodes.append(self.node)
            self.driver = Node('heartbeat_transport_driver', use_global_arguments=False)
            self.nodes.append(self.driver)
            if observe_events:
                self.rows['event'] = []
                self.driver.create_subscription(AlgorithmEvent, '/heartbeat_transport/events',
                    lambda msg: self.rows['event'].append((time.monotonic_ns(), msg)), 100)
            self.executor = SingleThreadedExecutor()
            for node in self.nodes:
                self.executor.add_node(node)
            for name, kind, topic in (
                ('diagnostic', diagnostic_type, '/heartbeat_transport/diagnostics'),
                ('clock', Clock, '/clock'), ('ready', Bool, '/heartbeat_transport/ready'),
                ('state', AlgorithmState, '/heartbeat_transport/state'),
                ('confirmation', DetectorConfirmation, '/gesc_gaussian/v2/detector_confirmation')):
                self.driver.create_subscription(kind, topic,
                    lambda msg, key=name: self.rows[key].append((time.monotonic_ns(), msg)), 100)
            self.pubs = {name: self.driver.create_publisher(kind, topic, 100)
                for name, kind, topic in (
                    ('clock', Clock, '/clock'), ('ready', Bool, '/heartbeat_transport/ready'),
                    ('state', AlgorithmState, '/heartbeat_transport/state'),
                    ('pose', Odometry, self.config['pose_topic']),
                    ('epoch', SearchEpochContext, '/gesc_gaussian/v2/search_epoch'),
                    ('keeper', Timekeeper, self.config['timekeeper_topic']))}
            required = ('clock', 'ready', 'state', 'pose', *(['epoch', 'keeper'] if moving else []))
            self.until(lambda: all(self.pubs[key].get_subscription_count() for key in required)
                and self.node.centroid_publisher.get_subscription_count() > 0)
            if observe_events:
                self.until(lambda: self.node.algorithm_event_publisher.get_subscription_count() > 0)
            if selection is True:
                assert self.node.get_parameter(HEARTBEAT_OPTION).value is True
            if moving:
                self.pubs['keeper'].publish(Timekeeper(mode='sim time', start_time=0.))
                self.until(lambda: self.node.v2_binding.binding.origin_ns == 0)
        except BaseException:
            self.close()
            raise

    def until(self, predicate, seconds=1.5):
        end = min(self.end, time.monotonic()+seconds)
        while not predicate() and time.monotonic() < end:
            self.executor.spin_once(timeout_sec=.005)
        assert predicate(), 'finite DDS delivery deadline; '+str({k:len(v) for k,v in self.rows.items()})

    def settle(self, seconds=.12, refresh_ready=False):
        end = min(self.end, time.monotonic()+seconds)
        while time.monotonic() < end:
            if refresh_ready:
                self.pubs['ready'].publish(Bool(data=True))
            self.executor.spin_once(timeout_sec=.005)
        assert time.monotonic() < self.end, '28s fixture work cap exhausted'

    def clock(self, stamp_ns):
        self.now_ns = stamp_ns
        msg = Clock(); set_time(msg.clock, stamp_ns)
        self.pubs['clock'].publish(msg)
        self.until(lambda: self.node.get_clock().now().nanoseconds == stamp_ns
            and self.rows['clock'] and time_to_ns(self.rows['clock'][-1][1].clock) == stamp_ns)
        self.pubs['ready'].publish(Bool(data=True))
        self.until(lambda: self.node._centroid_recording_authorized()
            and self.rows['ready'] and self.rows['ready'][-1][1].data)

    def context(self, state, *, epoch=None):
        if epoch is not None and epoch != self.epoch:
            self.epoch, self.epoch_start = epoch, self.now_ns
        assert self.epoch > 0
        self.state = state
        msg = AlgorithmState(state=state, state_valid=True, run_id=self.run_id,
            run_id_valid=True, algorithm_profile='robust_gaussian_v1',
            state_elapsed_sec=(self.now_ns-self.epoch_start)*1e-9,
            state_elapsed_valid=True)
        set_time(msg.stamp, self.now_ns)
        self.pubs['state'].publish(msg)
        self.until(lambda: self.node.centroid_state_source_ns == self.now_ns
            and self.node.centroid_last_valid_state == state)
        if self.moving:
            self.context_sequence += 1
            msg = SearchEpochContext(schema_version=1, run_id=self.run_id,
                stream_contract_id=stream_contract_id(self.config, 0), frame_id='odom',
                search_epoch=self.epoch, context_sequence=self.context_sequence,
                algorithm_state=state, valid=True)
            set_time(msg.stamp, self.now_ns); set_time(msg.started_at, self.epoch_start)
            self.pubs['epoch'].publish(msg)
            self.until(lambda: self.node.v2_binding.binding.last_sequence == self.context_sequence)

    def pose(self, source_ns=None, *, admitted=True):
        source_ns = self.now_ns if source_ns is None else source_ns
        msg = Odometry(); set_time(msg.header.stamp, source_ns)
        msg.header.frame_id = 'odom'
        msg.pose.pose.position.x, msg.pose.pose.position.y = 1., 2.
        msg.pose.pose.orientation.w = 1.
        self.pubs['pose'].publish(msg)
        if admitted:
            self.until(lambda: any(message.source_valid and time_to_ns(message.source_stamp) == source_ns
                for _, message in self.rows['diagnostic']))
        return msg

    def step(self, *, state=SEARCH, epoch=None, pose=True):
        self.clock(self.now_ns+STEP_NS if self.now_ns else 1_000_000_000)
        if state is not None:
            self.context(state, epoch=epoch)
        if pose:
            self.pose(admitted=state == SEARCH)
        self.settle()

    def support(self, *, epoch=None, count=13):
        for index in range(count):
            self.step(epoch=epoch if index == 0 else None)

    def core_state(self):
        # Read-only exact value snapshot; never restore/mock the numerical owner.
        return (repr(self.node.centroid_detector.__dict__),
                self.node.centroid_search_epoch, self.node.centroid_confirmation_sequence,
                self.node.centroid_confirmed_in_epoch)

    def finish(self):
        self.pubs['ready'].publish(Bool(data=False))
        self.until(lambda: not self.rows['ready'][-1][1].data and not self.node.recording_ready)
        self.settle(.02)

    def coverage(self, rows=None):
        ready = self.rows['ready']
        first = next(stamp for stamp, msg in ready if msg.data)
        last = next(stamp for stamp, msg in ready if stamp >= first and not msg.data)
        return centroid_stream_errors(self.rows['diagnostic'] if rows is None else rows,
            self.rows['clock'], first, last, maximum_gap_sec=1.)

    def typed_checks(self):
        return centroid_diagnostic_errors([msg for _, msg in self.rows['diagnostic']],
            expected_metric_mode=self.mode, expected_source_pose_topic=self.config['pose_topic'],
            supervisor_run_ids={self.run_id}, maximum_source_gap_sec=.5,
            allow_clock_admission=True, expected_frame_id='odom', pose_freshness_sec=.5)

    def close(self):
        if self.executor is not None:
            for node in self.nodes:
                self.executor.remove_node(node)
            self.executor.shutdown(timeout_sec=1.)
        for node in reversed(self.nodes):
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


@contextmanager
def transport(mode, moving=True, selection=True, observe_events=False):
    fixture = Transport(mode, moving, selection, observe_events)
    try:
        yield fixture
    finally:
        fixture.close()


def invalid_status(message):
    assert not any((message.source_valid, message.history_valid, message.metric_valid,
                    message.confinement_valid, message.eligible, message.confirmed))
    assert time_to_ns(message.source_stamp) == 0
    assert message.completed_window_count == message.sample_count == 0
    assert message.represented_duration_sec == 0.
    assert not message.window_start and not message.window_end
    assert not message.centroid_x_m and not message.centroid_y_m and not message.displacement_m


@pytest.mark.parametrize('mode', MODES)
@pytest.mark.parametrize('selection', [None, False], ids=['absent', 'false'])
def test_default_off_retains_original_verify_coverage_gap(mode, selection):
    """Baseline PASS means the original strict coverage gate FAIL was retained."""
    with transport(mode, selection=selection) as f:
        f.support(epoch=1)
        for _ in range(23):
            f.step(state=VERIFY, pose=False)
        f.support(epoch=2)
        f.finish()
        errors = f.coverage()
        assert errors == ['centroid diagnostics have a simulated publication coverage gap']
        assert not f.typed_checks()
        print(json.dumps(dict(case='original-default-off-gap', mode=mode,
            selection=selection, existing_coverage_errors=errors,
            diagnostics=len(f.rows['diagnostic']), research_qualification=False)))


@pytest.mark.parametrize('mode', MODES)
@pytest.mark.parametrize('moving', [False, True], ids=['stationary', 'moving'])
def test_enabled_zero_epoch_waiting_status_does_not_create_authority(mode, moving):
    with transport(mode, moving) as f:
        original = f.core_state()
        for _ in range(15):
            f.step(state=None, pose=False)
        assert f.core_state() == original
        relevant = [msg for _, msg in f.rows['diagnostic'] if time_to_ns(msg.stamp) >= 1_000_000_000]
        assert len({time_to_ns(msg.stamp) for msg in relevant}) > 2
        for msg in relevant:
            invalid_status(msg)
            assert msg.search_epoch == msg.confirmation_sequence == 0
            assert time_to_ns(msg.receipt_stamp) == 0
        assert not f.rows['confirmation']
        f.finish()
        assert not f.typed_checks()
        assert not f.coverage()


@pytest.mark.parametrize('mode', MODES)
@pytest.mark.parametrize('moving', [False, True], ids=['stationary', 'moving'])
def test_enabled_search_verify_search_has_invalid_coverage_and_fresh_confirmations(mode, moving, tmp_path, monkeypatch):
    with transport(mode, moving, observe_events=True) as f:
        f.support(epoch=1)
        confirmed = [msg for _, msg in f.rows['diagnostic'] if msg.confirmed]
        assert len(confirmed) == 1
        f.step(state=VERIFY, pose=False)
        verify_start = f.now_ns
        original = f.core_state()
        for _ in range(23):
            f.step(state=VERIFY, pose=False)
        verify_end = f.now_ns
        assert f.core_state() == original, 'heartbeat changed numerical/epoch/confirmation state'
        status = [msg for _, msg in f.rows['diagnostic'] if verify_start < time_to_ns(msg.stamp) <= verify_end]
        assert status
        for msg in status:
            invalid_status(msg)
        # Continuing non-SEARCH poses remain rejected numerical support. Their
        # existing callback resets are legitimate and not counted as heartbeat resets.
        for _ in range(23):
            f.step(state=VERIFY, pose=True)
            assert f.node.centroid_detector.retained_point_count == 0
        f.step(epoch=2, pose=False)
        original = f.core_state()
        for _ in range(24):
            f.step(pose=False)
        assert f.core_state() == original
        assert f.node.centroid_pose_receipt_ns is None
        fresh_start = f.now_ns+STEP_NS
        f.support()
        confirmed = [msg for _, msg in f.rows['diagnostic'] if msg.confirmed]
        assert len(confirmed) == 2
        assert confirmed[1].search_epoch > confirmed[0].search_epoch
        assert time_to_ns(confirmed[1].history_start) >= fresh_start
        assert confirmed[1].confirmation_sequence == confirmed[0].confirmation_sequence+1
        if moving:
            assert len(f.rows['confirmation']) == 2
        events = [msg for _, msg in f.rows['event']]
        configuration = [msg for msg in events if msg.event_type == AlgorithmEvent.EVENT_CONFIGURATION]
        assert len(configuration) == 1
        assert dict(zip(configuration[0].value_names, configuration[0].values))[HEARTBEAT_OPTION] == 1.
        assert len([msg for msg in events
                    if msg.event_type == AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED]) == 2
        f.finish()
        assert not f.typed_checks()
        assert not f.coverage()
        # Use the real coverage checker again: losing the inactive interval
        # must remain a failure even with this selected observability extension.
        stripped = [(stamp, msg) for stamp, msg in f.rows['diagnostic']
                    if not verify_start < time_to_ns(msg.stamp) <= verify_end]
        assert f.coverage(stripped) == ['centroid diagnostics have a simulated publication coverage gap']
        full = recorded_report(f, tmp_path, monkeypatch)
        assert full['checks']['centroid_diagnostics_consistent']['passed']
        assert not any('centroid' in error for error in full['checks']['motion_interval_coverage']['detail'])
        missing = recorded_report(f, tmp_path, monkeypatch, stripped)
        assert 'centroid diagnostics have a simulated publication coverage gap' in (
            missing['checks']['motion_interval_coverage']['detail'])
        print(json.dumps(dict(case='enabled-cycle', mode=mode, moving=moving,
            diagnostic_count=len(f.rows['diagnostic']), confirmations=len(confirmed),
            existing_coverage_errors=f.coverage(), research_qualification=False)))


@pytest.mark.parametrize('mode', MODES)
@pytest.mark.parametrize('moving', [False, True], ids=['stationary', 'moving'])
def test_enabled_held_future_and_stale_receipts_are_not_refreshed(mode, moving):
    with transport(mode, moving) as f:
        f.support(epoch=1, count=3)
        receipt = f.now_ns
        future = receipt+50_000_000
        message = f.pose(future, admitted=False)
        pending = (lambda: f.node.v2_binding.pending) if moving else (lambda: f.node.centroid_admission.pending['pose'])
        f.until(lambda: bool(pending()))
        original = f.core_state()
        for _ in range(3):
            f.pubs['pose'].publish(message)  # Exact repeat; first receipt must survive.
            f.settle(.03, refresh_ready=True)
        assert f.core_state() == original
        assert not any(time_to_ns(msg.source_stamp) == future for _, msg in f.rows['diagnostic'])
        f.clock(future); f.context(SEARCH)
        f.until(lambda: any(msg.source_valid and time_to_ns(msg.source_stamp) == future
                           for _, msg in f.rows['diagnostic']))
        admitted = next(msg for _, msg in f.rows['diagnostic']
                        if msg.source_valid and time_to_ns(msg.source_stamp) == future)
        assert time_to_ns(admitted.receipt_stamp) == receipt < future
        # A second pending source expires while /clock is held. Readiness alone
        # is refreshed; original state/pose leases must still age on steady time.
        expired_source = f.now_ns+400_000_000
        expired = f.pose(expired_source, admitted=False)
        f.until(lambda: bool(pending()))
        f.settle(.70, refresh_ready=True)
        f.until(lambda: not pending())
        assert not any(msg.source_valid and time_to_ns(msg.source_stamp) == expired_source
                       for _, msg in f.rows['diagnostic'])
        frozen_stamp = f.now_ns
        core = f.core_state()
        count = len(f.rows['diagnostic'])
        f.settle(.30, refresh_ready=True)
        assert f.core_state() == core, 'heartbeat added resets after source revocation settled'
        added = [msg for _, msg in f.rows['diagnostic'][count:]]
        assert len(added) <= 1, 'same-clock heartbeat flood'
        for msg in added:
            invalid_status(msg)
            assert time_to_ns(msg.stamp) == frozen_stamp
        f.clock(expired_source); f.context(SEARCH)
        f.pubs['pose'].publish(expired)
        f.settle(.12)
        assert not any(msg.source_valid and time_to_ns(msg.source_stamp) == expired_source
                       for _, msg in f.rows['diagnostic']), 'expired duplicate resurrected support'
        for _ in range(15):
            f.step(pose=False)
        f.finish()
        assert not f.typed_checks()
        assert not f.coverage()


def recorded_report(fixture, path, monkeypatch, diagnostic_rows=None):
    """Actual captured wire into the real validator; other run evidence is absent."""
    package = Path(__file__).resolve().parents[1]
    entries = applicable_topics(load_manifest(package/'ros_esc/experiment_recording/topic_manifest.yaml'), 'simulation')
    replacements = {'raw_cost_legacy': fixture.config['raw_cost_topic'],
        'source_cost': fixture.config['source_cost_topic'],
        'augmented_cost_legacy': fixture.config['augmented_cost_topic'],
        'v2_objective_cost': fixture.config['objective_cost_topic'],
        'v2_source_provenance': fixture.config['provenance_topic'],
        'pose': fixture.config['pose_topic'], 'encoder': fixture.config['encoder_topic'],
        'timekeeper': fixture.config['timekeeper_topic'],
        'algorithm_state': '/heartbeat_transport/state', 'recording_ready': '/heartbeat_transport/ready',
        'centroid_convergence_diagnostics': '/heartbeat_transport/diagnostics'}
    for entry in entries:
        if entry['alias'] in replacements:
            entry['topic'] = replacements[entry['alias']]
    topics = {row['alias']: row['topic'] for row in entries}
    messages = {topics[alias]: fixture.rows[name] for alias, name in (
        ('clock','clock'), ('recording_ready','ready'), ('algorithm_state','state'),
        ('centroid_convergence_diagnostics','diagnostic'), ('v2_detector_confirmation','confirmation'))}
    if diagnostic_rows is not None:
        messages[topics['centroid_convergence_diagnostics']] = diagnostic_rows
    target = ['algorithm_profile:=robust_gaussian_v1', 'convergence_metric_mode:='+fixture.mode,
        'continuous_search_mode:='+('rolling_gesc_v2' if fixture.moving else 'stationary_v1'),
        HEARTBEAT_OPTION+':=True', 'algorithm_pose_topic:='+fixture.config['pose_topic'],
        'convergence_diagnostics_topic:=/heartbeat_transport/diagnostics',
        'timekeeper_topic:='+fixture.config['timekeeper_topic'],
        'stationary_timekeeper_topic:='+fixture.config['timekeeper_topic'],
        'v2_source_provenance_topic:='+fixture.config['provenance_topic'],
        'centroid_window_sec:=0.1', 'centroid_epsilon_m:=0.18',
        'v2_run_id:='+fixture.run_id, 'v2_stream_config_json:='+canonical_json(fixture.config)]
    # Real recorder admission must succeed before this fixture asks the full
    # validator about coverage; unrelated absent run streams remain failures.
    entries = require_selected_algorithm_topics(entries, 'simulation', target)
    documents = {'metadata.yaml': dict(mode='simulation', algorithm_profile='robust_gaussian_v1',
        recording={}, git={}, run_id=fixture.run_id, target_argv=target),
        'resolved_topics.yaml': {'topics':entries}, 'resolved_parameters.yaml': {'nodes':{}, 'failures':[]}}
    monkeypatch.setattr(recording_validator, '_load_yaml', lambda file: documents[Path(file).name])
    monkeypatch.setattr(recording_validator, '_read_bag', lambda *args: (
        {row['topic']:row['type'] for row in entries}, messages))
    (path/'notes.md').write_text('Actual DDS centroid cadence only; other complete-run streams are absent.\n')
    result = recording_validator.validate_run_directory(path, write_report=False)
    assert not any('selected algorithm recording contract:' in error for error in result['failures'])
    assert not result['passed']  # This is not a complete-recording qualification fixture.
    return result


@pytest.mark.parametrize('mode', MODES)
@pytest.mark.parametrize('captured_delta_ns', [-100_000_000, 100_000_000], ids=['rollback', 'advance'])
def test_status_heartbeat_never_reads_mutating_binding_clock_or_refreshes_receipts(mode, captured_delta_ns, monkeypatch):
    with transport(mode, moving=True) as f:
        f.support(epoch=1)
        f.step(state=VERIFY, pose=False)
        binding = f.node.v2_binding.binding
        def state():
            return (f.core_state(), repr(binding.__dict__),
                repr(f.node.centroid_admission.__dict__),
                f.node.centroid_pose_receipt_ns, f.node.centroid_pose_receipt_steady_ns,
                f.node.centroid_pose_source_ns, f.node.centroid_state_receipt_ns,
                f.node.centroid_state_receipt_steady_ns, f.node.centroid_state_source_ns,
                f.node.v2_binding.latest_pose_steady_ns,
                repr(f.node.v2_binding.pending), repr(f.node.v2_binding.seen),
                f.node.v2_binding.pose_frontier)
        def forbidden_clock_read():
            raise AssertionError('heartbeat called mutating EpochBinding.now')
        # The executor is deliberately not spinning during these direct calls.
        # Force only publication bookkeeping due; no numerical state is mocked.
        with monkeypatch.context() as selected:
            selected.setattr(binding, 'now', forbidden_clock_read)
            # This direct-read fault fixture injects a captured clock boundary;
            # it makes no cadence/recording claim for this deliberate rollback.
            captured = f.now_ns + captured_delta_ns
            selected.setattr(f.node, '_centroid_now_ns', lambda: captured)
            selected.setattr(f.node, 'centroid_last_publication_steady_ns', None)
            selected.setattr(f.node, 'centroid_last_publication_ns', None)
            original = state()
            assert not f.node.v2_binding.centroid_ready(now_ns=captured, steady_ns=time.monotonic_ns())
            assert state() == original
            f.node._centroid_invalid_status_heartbeat()
            assert state() == original
        f.settle(.02)
        assert f.rows['diagnostic']
        invalid_status(f.rows['diagnostic'][-1][1])
