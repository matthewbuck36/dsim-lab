"""Typed centroid provenance bridges only the selected private M4 evaluator."""

from copy import deepcopy
from types import SimpleNamespace
import math
import json

import pytest
from rclpy.serialization import serialize_message
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool
from ros_esc_interfaces.msg import AlgorithmEvent, AlgorithmState, GaussianFill, Timekeeper
from ros_esc.v2_stream import set_time, time_to_ns
from ros_esc.scenario_runner import run_scenario as runner

import test_scenario_runner as inherited
from test_q5_stationary_fill_protocol import ORIGIN_NS, confirmation


@pytest.mark.parametrize('mode,strict,accepted', [
    ('subreaper_group_v3', True, True), ('subreaper_group_v3', False, False),
    ('subreaper_v2', True, False), ('observed_tree_v1', True, False),
])
def test_development_route_requires_exact_existing_group_owner(monkeypatch, mode, strict, accepted):
    class Admitted(Exception):
        pass
    def expansion(*args, **kwargs):
        raise Admitted
    monkeypatch.setattr(runner, 'load_suite', lambda *args: {'suite_id': 'v2_method_development_v1'})
    monkeypatch.setattr(runner, 'expand_suite', expansion)
    with pytest.raises(Admitted if accepted else ValueError):
        runner.execute_suite('fixture', 'fixture', process_ownership_mode=mode, strict_cleanup=strict)


@pytest.mark.parametrize('arm', ['B', 'D'])
def test_development_typed_centroid_route_preserves_inherited_join(arm):
    data = fixture(arm)
    expected = normalize(data)
    data[0]['suite_id'] = 'v2_method_development_v1'
    actual = normalize(data)
    assert actual[1:] == expected[1:]
    assert [serialize_message(message) for _, message in actual[0]] == [
        serialize_message(message) for _, message in expected[0]]
    data[0]['suite_id'] = 'unreleased_other_suite'
    assert runner._m4_centroid_event_selection(data[0]) is None


@pytest.mark.parametrize('condition', ['present', 'delayed', 'absent', 'changed', 'malformed'])
def test_development_daemon_baseline_requires_exact_stable_native_visibility(monkeypatch, condition):
    from ros2cli.node import daemon as daemon_module
    calls = []
    class Daemon:
        def __init__(self, *args):
            self.reads = 0
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return None
        def get_name(self):
            self.reads += 1
            if condition == 'malformed':
                return '/invalid'
            return 'changed' if condition == 'changed' and self.reads > 1 else 'exact_daemon'
        def get_namespace(self):
            return '/shared'
    clock = iter(range(100))
    monkeypatch.setattr(daemon_module, 'DaemonNode', Daemon)
    monkeypatch.setattr(runner.time, 'monotonic', lambda: float(next(clock)))
    monkeypatch.setattr(runner.time, 'sleep', lambda *args: None)
    def graph():
        calls.append(True)
        return ({'/unrelated'} if condition == 'absent' or condition == 'delayed' and len(calls) == 1
                else {'/shared/exact_daemon', '/unrelated'})
    monkeypatch.setattr(runner, '_native_ros_graph_nodes', graph)
    if condition in ('absent', 'changed', 'malformed'):
        with pytest.raises(TimeoutError if condition == 'absent' else ValueError):
            runner._native_development_graph_baseline()
    else:
        assert runner._native_development_graph_baseline() == {'/shared/exact_daemon', '/unrelated'}
        assert len(calls) == (2 if condition == 'delayed' else 1)


@pytest.mark.parametrize('selected', [False, True])
def test_development_graph_admission_uses_existing_five_second_child_envelope(monkeypatch, selected):
    calls = []
    monkeypatch.setattr(runner.time, 'monotonic', lambda: 100.)
    def completed(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(stdout=json.dumps(['/shared/exact_daemon', '/other']))
    monkeypatch.setattr(runner.subprocess, 'run', completed)
    result = runner.ros_graph_nodes(strict=True, absolute_deadline=130., require_shared_daemon=selected)
    assert result == {'/shared/exact_daemon', '/other'}
    assert calls[0][1]['timeout'] == 5.
    assert ('_native_development_graph_baseline' in calls[0][0][-1]) is selected
    with pytest.raises(ValueError, match='strict graph'):
        runner.ros_graph_nodes(require_shared_daemon=True)


def test_development_daemon_admission_failure_prevents_simulation(monkeypatch, tmp_path):
    suite = {'suite_id': 'v2_method_development_v1', 'schema_version': 14, 'source_path': '/fixture',
             'execution': {'runs_root': str(tmp_path), 'gazebo_gui': True}}
    monkeypatch.setattr(runner, 'load_suite', lambda *args: suite)
    monkeypatch.setattr(runner, 'expand_suite', lambda *args, **kwargs: ([{}], []))
    monkeypatch.setattr(runner, 'ensure_ros_daemon', lambda: None)
    monkeypatch.setattr(runner.time, 'monotonic', lambda: 100.)
    def absent(**kwargs):
        assert kwargs == {'strict': True, 'absolute_deadline': 460., 'require_shared_daemon': True}
        raise TimeoutError('shared daemon was absent')
    monkeypatch.setattr(runner, 'ros_graph_nodes', absent)
    monkeypatch.setattr(runner, 'run_record_process', lambda *a, **k: pytest.fail('simulation launched'))
    with pytest.raises(TimeoutError, match='shared daemon was absent'):
        runner.execute_suite('fixture', 'fixture', run_id='v2-development-fixture', strict_cleanup=True,
            cleanup_deadline=460., process_ownership_mode='subreaper_group_v3')


def wire(cls, old):
    result = cls()
    for key, value in vars(old).items(): setattr(result, key, value)
    return result


def fixture(arm='B'):
    resolved = inherited._v5_staged_resolved()
    resolved['suite_id'] = 'm4_pilot_v1'
    values = resolved['algorithm']['launch_overrides']
    values.update(convergence_metric_mode='centroid_two_block_v2',
        continuous_search_mode='stationary_v1' if arm == 'B' else 'rolling_gesc_v2',
        centroid_window_sec=6., centroid_epsilon_m=.18, centroid_maximum_radius_m=.5)
    old_states, old_events, old_fills = inherited._staged_records()
    states = [(stamp, wire(AlgorithmState, item)) for stamp, item in old_states]
    events = [(stamp, wire(AlgorithmEvent, item)) for stamp, item in old_events]
    fills = [(stamp, wire(GaussianFill, item)) for stamp, item in old_fills]
    for _, state in states:
        state.run_id, state.run_id_valid = 'actual-supervisor-run', True
        state.algorithm_profile = 'robust_gaussian_v1'
    diagnostic = confirmation()
    diagnostic.run_id, diagnostic.source_pose_topic = states[0][1].run_id, '/odom'
    diagnostic.metric_mode = 'centroid_two_block_v2'
    diagnostic.window_duration_sec, diagnostic.represented_duration_sec = 6., 36.
    diagnostic.sample_count = 2*diagnostic.sample_count-1
    diagnostic.epsilon_m = .18
    for name in ('stamp', 'receipt_stamp', 'source_stamp', 'history_start', 'history_end'):
        item = getattr(diagnostic, name)
        set_time(item, ORIGIN_NS+1_000_000_000+2*(time_to_ns(item)-ORIGIN_NS-1_000_000_000))
    for item in [*diagnostic.window_start, *diagnostic.window_end]:
        set_time(item, ORIGIN_NS+1_000_000_000+2*(time_to_ns(item)-ORIGIN_NS-1_000_000_000))
    diagnostic.center_x_m = diagnostic.center_y_m = 1.04
    diagnostic.centroid_x_m = diagnostic.centroid_y_m = [1.04]*6
    event = events[0][1]
    event.source_timestamp, event.source_timestamp_valid = math.nan, False
    set_time(event.stamp, time_to_ns(diagnostic.stamp)+100_000_000)
    event.value_names = ['score_m', 'confinement_radius_m', 'fill_center_x_m',
                         'fill_center_y_m', 'search_epoch', 'confirmation_sequence']
    event.values = [diagnostic.score_m, diagnostic.confinement_radius_m, 1.04, 1.04,
                    float(diagnostic.search_epoch), float(diagnostic.confirmation_sequence)]
    for _, message in [*events[1:], *fills]:
        if message.source_timestamp_valid: message.source_timestamp += 27.
    timekeepers = [(0, Timekeeper(mode='sim time', start_time=ORIGIN_NS*1e-9))]
    return resolved, states, events, fills, [(2, diagnostic)], timekeepers


def normalize(data):
    resolved, states, events, _, diagnostics, origins = data
    return runner._centroid_convergence_evaluation_events(resolved, states, events, diagnostics, origins)


@pytest.mark.parametrize('arm', ['B', 'D'])
def test_selected_b_and_d_generated_messages_reach_inherited_stage_a_without_public_timestamp_rewrite(arm):
    data = fixture(arm)
    original = serialize_message(data[2][0][1])
    assert runner._staged_recovery_evidence(*data[:4])[-1] == 'CONVERGENCE_CONFIRMED source timestamp is invalid'
    events, audit, error = normalize(data)
    assert error is None, error
    assert events[0][1].source_timestamp == 37.
    assert events[0][1].source_timestamp_valid
    assert serialize_message(data[2][0][1]) == original and not data[2][0][1].source_timestamp_valid
    stage, cardinality, evidence, error = runner._staged_recovery_evidence(data[0], data[1], events, data[3])
    assert error is None and stage and cardinality
    assert audit[0]['diagnostic_source_stamp_ns'] == ORIGIN_NS+37_000_000_000
    assert audit[0]['diagnostic_publication_stamp_ns'] == time_to_ns(data[4][0][1].stamp)
    assert audit[0]['time_origin_ns'] == ORIGIN_NS and len(audit[0]['diagnostic_sha256']) == 64


@pytest.mark.parametrize('fault', ['missing_diagnostic', 'missing_origin', 'changed_origin', 'wrong_clock',
    'wrong_metric', 'wrong_run', 'wrong_pose', 'wrong_configuration', 'wrong_score', 'wrong_center',
    'wrong_epoch', 'fractional_sequence', 'duplicate_field', 'early_publication', 'late_publication',
    'conflicting_diagnostic', 'conflicting_event', 'missing_event', 'wrong_relative'])
def test_missing_ambiguous_or_changed_join_is_not_evaluator_evidence(fault):
    data = fixture()
    event, diagnostic = data[2][0][1], data[4][0][1]
    if fault == 'missing_diagnostic': data[4].clear()
    elif fault == 'missing_origin': data[5].clear()
    elif fault == 'changed_origin': data[5].append((1, Timekeeper(mode='sim time', start_time=999.)))
    elif fault == 'wrong_clock': data[5][0][1].mode = 'wall time'
    elif fault == 'wrong_metric': diagnostic.metric_mode = 'centroid_windows_v2'
    elif fault == 'wrong_run': diagnostic.run_id = 'other'
    elif fault == 'wrong_pose': diagnostic.source_pose_topic = '/other'
    elif fault == 'wrong_configuration': diagnostic.epsilon_m = .2
    elif fault == 'wrong_score': event.values[0] += .01
    elif fault == 'wrong_center': event.values[2] += .01
    elif fault == 'wrong_epoch': event.values[4] += 1.
    elif fault == 'fractional_sequence': event.values[5] += .5
    elif fault == 'duplicate_field': event.value_names[-1] = event.value_names[-2]
    elif fault == 'early_publication': set_time(event.stamp, time_to_ns(diagnostic.stamp)-1)
    elif fault == 'late_publication': set_time(event.stamp, time_to_ns(diagnostic.stamp)+500_000_001)
    elif fault == 'conflicting_diagnostic':
        conflict = deepcopy(diagnostic); conflict.reset_reason = 'conflict'
        data[4].append((3, conflict))
    elif fault == 'conflicting_event':
        conflict = deepcopy(event); conflict.detail = 'conflict'
        data[2].append((4, conflict))
    elif fault == 'missing_event': data[2].pop(0)
    elif fault == 'wrong_relative': event.source_timestamp_valid, event.source_timestamp = True, 19.
    events, _, error = normalize(data)
    assert error and events is data[2], fault


def test_existing_valid_relative_identity_and_identical_repeated_inputs_are_preserved():
    data = fixture()
    event = data[2][0][1]
    event.source_timestamp_valid, event.source_timestamp = True, 37.
    data[4].append((20, deepcopy(data[4][0][1])))
    data[5].append((21, deepcopy(data[5][0][1])))
    events, _, error = normalize(data)
    assert error is None and events[0][1] is event


def test_private_source_coordinate_does_not_replace_the_typed_decision_publication_clock():
    data = fixture()
    source = time_to_ns(data[4][0][1].source_stamp)
    set_time(data[4][0][1].stamp, source+50_000_000)
    set_time(data[2][0][1].stamp, source+150_000_000)
    events, audit, error = normalize(data)
    assert error is None and events[0][1].source_timestamp == 37.
    assert audit[0]['diagnostic_source_stamp_ns'] == source
    assert audit[0]['diagnostic_publication_stamp_ns'] == source+50_000_000
    assert time_to_ns(events[0][1].stamp) == source+150_000_000


@pytest.mark.parametrize('change', ['legacy_metric', 'other_suite'])
def test_nonselected_legacy_route_does_not_reinterpret_or_require_typed_evidence(change):
    data = fixture()
    if change == 'legacy_metric': data[0]['algorithm']['launch_overrides']['convergence_metric_mode'] = 'pde_mean_v1'
    else: data[0]['suite_id'] = 'historical-q5'
    events, audit, error = runner._centroid_convergence_evaluation_events(*data[:3])
    assert events is data[2] and audit == [] and error is None


@pytest.mark.parametrize('arm', ['B', 'D'])
def test_live_existing_monitor_joins_late_diagnostic_and_origin_then_observes_stage_a(monkeypatch, arm):
    data = fixture(arm)
    resolved, states, events, fills, diagnostics, origins = data
    callbacks, signals = {}, []
    class Node:
        def create_subscription(self, kind, topic, callback, depth): callbacks[topic] = callback
        def destroy_node(self): pass
    node = Node(); context = object()
    selection = runner._m4_centroid_event_selection(resolved)
    schedule = [(stamp, topic, message) for topic, records in (
        ('/gesc_gaussian/algorithm_state', states), ('/gesc_gaussian/algorithm_events', events),
        ('/gesc_gaussian/gaussian_fills', fills)) for stamp, message in records]
    sequence = [(topic, message) for _, topic, message in sorted(schedule)]
    # Delivery arrives after all public events/fills: no permanent error latch.
    sequence += [(selection['diagnostic_topic'], diagnostics[0][1]),
                 (selection['timekeeper_topic'], origins[0][1]),
                 ('/odom', inherited._odom_message(2.5, 2.5)),
                 ('/odom', inherited._odom_message(3.30, 3.30))]
    class Process:
        def __init__(self, command, stdout, **kwargs): self.pid, self.returncode = 7321, None
        def poll(self): return self.returncode
        def wait(self, timeout=None): self.returncode = 0; return 0
    def spin(timeout_sec):
        topic, message = sequence.pop(0)
        callbacks[topic](message)
    monkeypatch.setattr(runner.rclpy.context, 'Context', lambda: context)
    monkeypatch.setattr(runner.rclpy, 'init', lambda context: None)
    monkeypatch.setattr(runner.rclpy, 'shutdown', lambda context: None)
    monkeypatch.setattr(runner.rclpy, 'create_node', lambda *a, **k: node)
    inherited._install_boundary_executor(monkeypatch, context, node, spin, [])
    monkeypatch.setattr(runner.subprocess, 'Popen', Process)
    monkeypatch.setattr(runner.os, 'killpg', lambda pid, sig: signals.append((pid, sig)))
    result = runner._run_record_to_global_proximity(['record'], 5., 1., resolved)
    assert result['stage_a_observed_live'] and result['fill_cardinality_observed_live']
    assert result['centroid_event_timestamp_binding_error_live'] is None
    assert result['centroid_event_timestamp_bindings_live'][0]['relative_source_timestamp'] == 37.
    assert signals == [(7321, runner.signal.SIGINT)] and not sequence


@pytest.mark.parametrize('arm,missing', [('B', False), ('D', False), ('B', True)])
def test_existing_bag_reader_uses_actual_typed_wires_and_rejects_absent_final_join(monkeypatch, tmp_path, arm, missing):
    data = fixture(arm)
    resolved, states, events, fills, diagnostics, origins = data
    selected = runner._m4_centroid_event_selection(resolved)
    rows = [(stamp, topic, serialize_message(message)) for topic, records in (
        ('/gesc_gaussian/algorithm_state', states), ('/gesc_gaussian/algorithm_events', events),
        ('/gesc_gaussian/gaussian_fills', fills), (selected['timekeeper_topic'], origins),
        (selected['diagnostic_topic'], [] if missing else diagnostics)) for stamp, message in records]
    rows.append((0, '/gesc_gaussian/recording_ready', serialize_message(Bool(data=True))))
    pose = Odometry(); pose.pose.pose.position.x = pose.pose.pose.position.y = 3.3
    pose.pose.pose.orientation.w = 1.
    rows.append((15, '/odom', serialize_message(pose)))
    stream = iter((topic, blob, stamp) for stamp, topic, blob in sorted(rows))
    class Reader:
        def __init__(self): self.next = next(stream, None)
        def open(self, *args): pass
        def has_next(self): return self.next is not None
        def read_next(self):
            value, self.next = self.next, next(stream, None)
            return value
    monkeypatch.setattr(runner.rosbag2_py, 'SequentialReader', Reader)
    result = runner._bag_outcomes(tmp_path, resolved)
    if missing:
        assert result['centroid_event_timestamp_binding_error']
        assert not result['local_recovery_stage_passed']
    else:
        assert result['centroid_event_timestamp_binding_error'] is None
        assert result['local_recovery_stage_passed']
        assert result['centroid_event_timestamp_bindings'][0]['relative_source_timestamp'] == 37.
    assert not data[2][0][1].source_timestamp_valid
