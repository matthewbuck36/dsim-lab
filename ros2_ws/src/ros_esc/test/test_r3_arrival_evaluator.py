"""Prospective arrival criterion through existing schema, monitor and bag owners."""
from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool
from rclpy.serialization import serialize_message
from ros_esc_interfaces.msg import AlgorithmEvent, AlgorithmState

from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner.scenario_schema import (
    POST_RECOVERY_ARRIVAL_CRITERION, load_suite, expand_suite,
)
from ros_esc.v2_stream import set_time, time_to_ns
from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_TOPIC, RECURRENT_MODE

import test_m4_centroid_event_evaluation as centroid
import test_m4_monitor_progression as monitor
from test_v2_lifecycle_recording import recurrent_fixture, TOPICS


TEMPLATE = Path('/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/'
                'visible_integrated_02/scenario.yaml')


def selected_document():
    document = yaml.safe_load(TEMPLATE.read_text())
    success = document['cases'][0]['success']
    success['criterion'] = POST_RECOVERY_ARRIVAL_CRITERION
    omitted = {'controller_goal', 'expected_terminal_state'}
    success['all_of'] = [name for name in success['all_of'] if name not in omitted]
    for scope in success['result_scopes'].values():
        scope['all_of'] = [name for name in scope['all_of'] if name not in omitted]
    control = success['controller']
    control.pop('expected_terminal_state')
    control['required_state_paths'] = [path[:-2] for path in control['required_state_paths']]
    control['required_state_path'] = control['required_state_paths'][0]
    control['required_events'].remove('GOAL_REACHED')
    control['required_event_sequence'] = ['CONVERGENCE_CONFIRMED', 'FILL_CREATED', 'ESCAPE_STARTED']
    return document


def resolve(tmp_path, document):
    path = tmp_path/'scenario.yaml'
    path.write_text(yaml.safe_dump(document))
    runs, skipped = expand_suite(load_suite(path))
    assert not skipped and len(runs) == 1
    return runs[0]


def test_selected_schema_roundtrip_and_metadata_preserve_algorithm_and_boundaries(tmp_path):
    selected = resolve(tmp_path, selected_document())
    legacy = resolve(tmp_path, yaml.safe_load(TEMPLATE.read_text()))
    assert selected['success']['criterion'] == POST_RECOVERY_ARRIVAL_CRITERION
    assert 'criterion' not in legacy['success']
    assert selected['algorithm'] == legacy['algorithm']
    assert selected['success']['staged_recovery'] == legacy['success']['staged_recovery']
    assert runner.build_launch_command(selected, run_id='arrival-fixture') == runner.build_launch_command(
        legacy, run_id='arrival-fixture')
    metadata = runner.build_metadata(selected, 'test', 'arrival', '', run_id='arrival-fixture')
    assert metadata['scenario_runner']['success']['criterion'] == POST_RECOVERY_ARRIVAL_CRITERION
    assert not runner._requires_ranked_goal(selected) and runner._requires_ranked_goal(legacy)


@pytest.mark.parametrize('fault', ['unknown', 'old_schema', 'other_suite', 'holdout', 'physical',
    'legacy', 'radius', 'terminal', 'goal_event', 'incomplete_path', 'missing_fill', 'missing_ownership'])
def test_selected_scenario_rejects_incompatible_or_weakened_contract(tmp_path, fault):
    document = selected_document()
    case = document['cases'][0]; success = case['success']; control = success['controller']
    if fault == 'unknown': success['criterion'] = 'arrival_guess'
    elif fault == 'old_schema': document['schema_version'] = 13
    elif fault == 'other_suite': document['suite_id'] = 'm4_pilot_v9'
    elif fault == 'holdout': case['acceptance_partition'] = 'holdout'
    elif fault == 'physical': document['mode'] = 'physical'
    elif fault == 'legacy': case['profiles'] = ['legacy']
    elif fault == 'radius':
        success['staged_recovery']['global_proximity_radius_m'] = .6
        success['ground_truth']['proximity_radius_m'] = .6
    elif fault == 'terminal': control['expected_terminal_state'] = 'GOAL_HOLD'
    elif fault == 'goal_event': control['required_events'].append('GOAL_REACHED')
    elif fault == 'incomplete_path':
        control['required_state_paths'] = [path[:-1] for path in control['required_state_paths']]
        control['required_state_path'] = control['required_state_paths'][0]
    elif fault in ('missing_fill', 'missing_ownership'):
        name = 'fill_cardinality' if fault == 'missing_fill' else 'escape_command_ownership'
        success['all_of'].remove(name)
    with pytest.raises(ValueError):
        resolve(tmp_path, document)


def test_omitted_selector_rejects_arrival_paths_without_changing_legacy(tmp_path):
    document = selected_document(); del document['cases'][0]['success']['criterion']
    with pytest.raises(ValueError):
        resolve(tmp_path, document)
    result = resolve(tmp_path, yaml.safe_load(TEMPLATE.read_text()))
    assert result['success']['controller']['expected_terminal_state'] == 'GOAL_HOLD'


def recurrent_data():
    data = monitor.data('D', ranked=True)
    resolved, states, events, fills, diagnostics, origins = data
    resolved['suite_id'] = 'v2_method_development_v1'
    resolved['algorithm']['launch_overrides']['convergence_metric_mode'] = RECURRENT_MODE
    diagnostic = deepcopy(recurrent_fixture()[0][TOPICS['recurrent_convergence_diagnostics']][0][1])
    origin = centroid.ORIGIN_NS
    # Existing inherited fill stamp is37.0 relative; add a distinct actual pose.
    for name in ('stamp', 'receipt_stamp', 'source_stamp', 'history_start', 'history_end',
                 'persistence_start', 'epoch_started_at'):
        set_time(getattr(diagnostic, name), time_to_ns(getattr(diagnostic, name))+origin+7_000_000_000)
    set_time(diagnostic.source_stamp, origin+37_008_000_000)
    set_time(diagnostic.receipt_stamp, origin+37_009_000_000)
    diagnostic.run_id = states[0][1].run_id
    diagnostic.source_pose_topic = '/odom'
    diagnostic.center_x_m = diagnostic.center_y_m = 1.04
    diagnostics[:] = [(2, diagnostic)]
    event = events[0][1]
    set_time(event.stamp, time_to_ns(diagnostic.stamp)+100_000_000)
    event.values = [diagnostic.score_m, diagnostic.confinement_radius_m, 1.04, 1.04,
                    float(diagnostic.search_epoch), float(diagnostic.confirmation_sequence)]
    return data


def test_recurrent_support_coordinate_reaches_staged_fill_with_actual_input_audited():
    data = recurrent_data()
    original = monitor.wire_identity(data[2][0][1])
    events, audit, error = centroid.normalize(data)
    assert error is None, error
    assert events[0][1].source_timestamp == 37.
    assert audit[0]['diagnostic_source_stamp_ns'] == centroid.ORIGIN_NS+37_008_000_000
    assert audit[0]['diagnostic_history_end_ns'] == centroid.ORIGIN_NS+37_000_000_000
    assert audit[0]['evaluator_source_stamp_ns'] == audit[0]['diagnostic_history_end_ns']
    assert audit[0]['evaluator_coordinate'] == 'confirmed_history_end'
    assert audit[0]['time_origin_ns'] == centroid.ORIGIN_NS
    assert monitor.wire_identity(data[2][0][1]) == original
    stage, count, evidence, error = runner._staged_recovery_evidence(data[0], data[1], events, data[3])
    assert stage and count and error is None, (evidence, error)


@pytest.mark.parametrize('selected', [False, True])
def test_live_arrival_needs_complete_recovery_but_selected_needs_no_ranked_event(monkeypatch, selected):
    data = recurrent_data()
    if selected: data[0]['success']['criterion'] = POST_RECOVERY_ARRIVAL_CRITERION
    schedule = [monitor.odom(0., goal=True)] + monitor.recovered(data)
    schedule += [monitor.odom(100., goal=True)]
    if not selected: schedule += [monitor.odom(400., goal=True)]
    result, remaining, _ = monitor.run_callbacks(monkeypatch, data[0], schedule)
    assert not remaining and result['stage_a_observed_live']
    assert result['graceful_global_proximity_stop'] is selected
    assert result['graceful_post_stage_a_timeout_stop'] is not selected
    assert not result['controller_ranked_goal_observed_live']
    if selected:
        assert result['global_proximity_sample_live']['sample_sim_sec'] == 100.
        assert result['global_proximity_sample_live']['controller_ranked_goal_required'] is False


@pytest.mark.parametrize('fault', ['conflicting_diagnostic', 'missing_fill'])
def test_selected_live_arrival_cannot_hide_invalid_current_evidence(monkeypatch, fault):
    data = recurrent_data(); data[0]['success']['criterion'] = POST_RECOVERY_ARRIVAL_CRITERION
    schedule = monitor.recovered(data)
    if fault == 'conflicting_diagnostic':
        conflict = deepcopy(data[4][0][1]); conflict.reset_reason = 'conflict'
        schedule += [(RECURRENT_TOPIC, conflict), monitor.odom(100.), monitor.odom(400., goal=True)]
    else:
        schedule = [(topic, message) for topic, message in schedule if topic != monitor.FILL]
        schedule += [monitor.odom(360., goal=True)]
    result, remaining, _ = monitor.run_callbacks(monkeypatch, data[0], schedule)
    assert not remaining and not result['graceful_global_proximity_stop']
    assert not result['global_proximity_observed_live']


@pytest.mark.parametrize('selected', [False, True])
def test_actual_offline_owner_keeps_ranked_diagnostic_separate_from_arrival(monkeypatch, tmp_path, selected):
    data = recurrent_data()
    resolved, states, events, fills, diagnostics, origins = data
    if selected: resolved['success']['criterion'] = POST_RECOVERY_ARRIVAL_CRITERION
    choice = runner._m4_centroid_event_selection(resolved)
    rows = [(stamp, topic, serialize_message(message)) for topic, records in (
        (monitor.STATE, states), (monitor.EVENT, events), (monitor.FILL, fills),
        (choice['timekeeper_topic'], origins), (choice['diagnostic_topic'], diagnostics))
        for stamp, message in records]
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
    assert result['centroid_event_timestamp_binding_error'] is None
    assert result['local_recovery_stage_passed'] and result['fill_cardinality_passed']
    assert result['post_recovery_global_proximity_passed'] is selected
    assert result['counted_candidate_ranked_goal_passed'] is False
    assert result['controller_goal'] == 'failed'
