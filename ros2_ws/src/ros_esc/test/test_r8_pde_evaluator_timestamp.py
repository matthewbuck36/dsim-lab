"""Actual C03 PDE mirrors, inherited recovery owner and selected live/final paths."""
from copy import deepcopy
import math

import pytest
from rclpy.serialization import serialize_message
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool
from ros_esc_interfaces.msg import (AlgorithmEvent, AlgorithmState, GaussianFill,
    DetectorConfirmation, StampedFloat64MultiArray, Timekeeper)
from ros_esc.v2_stream import set_time, time_to_ns, stream_contract_id
from ros_esc.v2_lifecycle import message_payload
from ros_esc.scenario_runner import run_scenario as runner
import test_scenario_runner as inherited
from test_m4_centroid_event_evaluation import wire

# Exact canonical messages retained in r8_pde_evaluator_v1/c03_actual_join.json.
C03 = {'event': {'stamp': 85000000000,
           'source_timestamp': 85.0,
           'source_timestamp_valid': True,
           'event_type': 11,
           'state': 0,
           'state_name': 'UNAVAILABLE',
           'state_valid': False,
           'fill_id': 0,
           'fill_id_valid': False,
           'reason_code': 0,
           'detail': 'convergence confirmed; fill ready',
           'value_names': ['metric',
                           'r_mean_m2',
                           'decay',
                           'fill_center_x_m',
                           'fill_center_y_m',
                           'mean_old_x_m',
                           'mean_old_y_m',
                           'count_remaining',
                           'path_length_m',
                           'net_displacement_m',
                           'path_efficiency',
                           'qualified_dwell_elapsed_sec',
                           'qualified_dwell_required_sec'],
           'values': [-0.12026685861084162,
                      0.0004714221244267287,
                      0.07926171926473166,
                      1.0175027795332772,
                      1.1813345975980196,
                      1.0323123199414244,
                      1.1972122434350505,
                      0.0,
                      2.27552684384765,
                      0.44234044750842183,
                      0.1943903446818829,
                      6.0,
                      6.0]},
 'confirmation': {'schema_version': 1,
                  'stamp': 85000000000,
                  'time_origin': 0,
                  'run_id': 'v2_method_development_C_20260910_03',
                  'stream_contract_id': '3b420701fd196da3525c4716b8064b935f0d637f7f1c945726a724b304b7a8d4',
                  'frame_id': 'odom',
                  'search_epoch': 1,
                  'context_sequence': 1701,
                  'epoch_started_at': 0,
                  'source_stamp': 84927000000,
                  'history_start': 17709000000,
                  'history_end': 84927000000,
                  'metric_mode': 'pde_mean_v1',
                  'history_kind': 'pde_input_support',
                  'source_stamp_kind': 'pose_input',
                  'confirmation_sequence': 1,
                  'detector_local_epoch': 0,
                  'center_x_m': 1.0175027795332772,
                  'center_y_m': 1.1813345975980196,
                  'convergence_score_m': 0.0,
                  'convergence_score_valid': False,
                  'legacy_r_mean_m2': 0.0004714221244267287,
                  'legacy_r_mean_valid': True,
                  'legacy_snapshot': [-0.12026685861084162,
                                      0.0004714221244267287,
                                      0.07926171926473166,
                                      1.0175027795332772,
                                      1.1813345975980196,
                                      1.0323123199414244,
                                      1.1972122434350505,
                                      0.0],
                  'valid': True,
                  'reason': ''},
 'legacy': {'header': 'CONVERGENCE_STATUS',
            'timestamp': 85.0,
            'data': [-0.12026685861084162,
                     0.0004714221244267287,
                     0.07926171926473166,
                     1.0175027795332772,
                     1.1813345975980196,
                     1.0323123199414244,
                     1.1972122434350505,
                     0.0]},
 'origin': {'mode': 'sim time', 'start_time': 0.0}}

def from_payload(cls, payload):
    result = cls()
    for key, kind in result.get_fields_and_field_types().items():
        value = payload[key]
        if kind == 'builtin_interfaces/Time':
            set_time(getattr(result, key), value)
        else:
            setattr(result, key, value)
    return result


def fixture(origin_ns=0):
    resolved = inherited._v5_staged_resolved()
    resolved['suite_id'] = 'v2_method_development_v1'
    resolved['algorithm']['launch_overrides'].update(
        convergence_metric_mode='pde_mean_v1', continuous_search_mode='rolling_gesc_v2')
    old_states, old_events, old_fills = inherited._staged_records()
    states = [(stamp, wire(AlgorithmState, item)) for stamp, item in old_states]
    events = [(stamp, wire(AlgorithmEvent, item)) for stamp, item in old_events]
    fills = [(stamp, wire(GaussianFill, item)) for stamp, item in old_fills]
    event = from_payload(AlgorithmEvent, C03['event'])
    typed = from_payload(DetectorConfirmation, C03['confirmation'])
    legacy = from_payload(StampedFloat64MultiArray, C03['legacy'])
    for _, state in states:
        state.run_id, state.run_id_valid = typed.run_id, True
        state.algorithm_profile = 'robust_gaussian_v1'
    if origin_ns:
        for message in (event, typed):
            for name, kind in message.get_fields_and_field_types().items():
                if kind == 'builtin_interfaces/Time':
                    field = getattr(message, name)
                    set_time(field, time_to_ns(field)+origin_ns)
        typed.stream_contract_id = stream_contract_id(runner.build_v2_stream_config(resolved), origin_ns)
    events[0] = (events[0][0], event)
    fills[0][1].source_timestamp = 84.927
    fills[0][1].center_x, fills[0][1].center_y = typed.center_x_m, typed.center_y_m
    events[1][1].source_timestamp = 84.927
    origins = [(0, Timekeeper(mode='sim time', start_time=origin_ns/1e9))]
    return resolved, states, events, fills, [(2, typed)], [(2, legacy)], origins


def normalize(data):
    return runner._moving_pde_convergence_evaluation_events(data[0], data[1], data[2],
                                                            data[4], data[5], data[6])


@pytest.mark.parametrize('origin_ns', [0, 1_000_000_000])
def test_actual_c03_clock_mismatch_rejects_before_private_join_and_passes_after(origin_ns):
    data = fixture(origin_ns)
    original = deepcopy(message_payload(data[2][0][1]))
    stage, cardinality, before, error = runner._staged_recovery_evidence(*data[:4])
    assert not stage and not cardinality and error is None
    assert before['assignments'] == []
    events, audit, error = normalize(data)
    assert error is None, error
    assert events[0][1] is not data[2][0][1]
    assert events[0][1].source_timestamp == pytest.approx(84.927)
    assert message_payload(data[2][0][1]) == original
    assert events[0][0] == data[2][0][0]
    assert message_payload(events[0][1], exclude=('source_timestamp',)) == message_payload(
        data[2][0][1], exclude=('source_timestamp',))
    stage, cardinality, after, error = runner._staged_recovery_evidence(data[0], data[1], events, data[3])
    assert error is None and stage and cardinality
    assert audit[0]['original_source_timestamp'] == 85.
    assert audit[0]['confirmation_source_stamp_ns'] == origin_ns+84_927_000_000
    assert audit[0]['event_publication_stamp_ns'] == origin_ns+85_000_000_000
    assert len(audit[0]['event_sha256']) == 64


def test_live_monitor_accepts_late_cross_topic_join_without_resetting_public_event(monkeypatch):
    data = fixture()
    resolved, states, events, fills, confirmations, legacy, origins = data
    callbacks, signals = {}, []
    class Node:
        def create_subscription(self, kind, topic, callback, depth): callbacks[topic] = callback
        def destroy_node(self): pass
    node, context = Node(), object()
    selected = runner._m4_pde_event_selection(resolved)
    schedule = [(stamp, topic, message) for topic, records in (
        ('/gesc_gaussian/algorithm_state', states), ('/gesc_gaussian/algorithm_events', events),
        ('/gesc_gaussian/gaussian_fills', fills)) for stamp, message in records]
    sequence = [(topic, message) for _, topic, message in sorted(schedule)]
    sequence += [(selected['confirmation_topic'], confirmations[0][1]),
                 (selected['legacy_topic'], legacy[0][1]),
                 (selected['timekeeper_topic'], origins[0][1]),
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
    assert result['stage_a_completion_evidence_live'] is not None
    assert result['pde_event_timestamp_binding_error_live'] is None
    assert result['pde_event_timestamp_bindings_live'][0]['relative_source_timestamp'] == pytest.approx(84.927)
    assert signals == [(7321, runner.signal.SIGINT)] and not sequence
    assert data[2][0][1].source_timestamp == 85.


@pytest.mark.parametrize('missing', [False, True])
def test_existing_final_reader_selects_actual_pde_types_and_requires_complete_join(monkeypatch, tmp_path, missing):
    data = fixture()
    resolved, states, events, fills, confirmations, legacy, origins = data
    selected = runner._m4_pde_event_selection(resolved)
    rows = [(stamp, topic, serialize_message(message)) for topic, records in (
        ('/gesc_gaussian/algorithm_state', states), ('/gesc_gaussian/algorithm_events', events),
        ('/gesc_gaussian/gaussian_fills', fills), (selected['timekeeper_topic'], origins),
        (selected['confirmation_topic'], [] if missing else confirmations),
        (selected['legacy_topic'], legacy)) for stamp, message in records]
    rows.append((0, '/gesc_gaussian/recording_ready', serialize_message(Bool(data=True))))
    pose = Odometry(); pose.pose.pose.position.x = pose.pose.pose.position.y = 3.3
    pose.pose.pose.orientation.w = 1.
    rows.append((16, '/odom', serialize_message(pose)))
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
        assert result['pde_event_timestamp_binding_error']
        assert not result['local_recovery_stage_passed']
    else:
        assert result['pde_event_timestamp_binding_error'] is None
        assert result['local_recovery_stage_passed']
        assert result['pde_event_timestamp_bindings'][0]['relative_source_timestamp'] == pytest.approx(84.927)
    assert data[2][0][1].source_timestamp == 85.
