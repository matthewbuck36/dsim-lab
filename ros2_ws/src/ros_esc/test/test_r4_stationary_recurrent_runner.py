"""Selected Arm B schema, actual frontend and inherited live/offline arrival owners."""
from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool
from rclpy.serialization import serialize_message
from ros_esc_interfaces.msg import AlgorithmEvent

from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, RECURRENT_TOPIC
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner.scenario_schema import (
    POST_RECOVERY_ARRIVAL_CRITERION, expand_suite, load_suite,
)
from ros_esc.stationary_fill_protocol import STATIONARY_RECURRENT_FILL_REQUEST_TOPIC
from ros_esc.v2_stream import set_time, time_to_ns
from test_q1_launch_frontend import parsed_launch  # noqa: F401
from test_q7_launch_selection import parameters
from test_r4_stationary_recurrent_protocol import ORIGIN_NS, request, rehash, errors
import test_m4_monitor_progression as monitor
import test_m4_centroid_event_evaluation as centroid


SCENARIO = Path('/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/'
                'stationary_integrated_01/scenario.yaml')


def resolve(tmp_path, document):
    path = tmp_path/'stationary.yaml'
    path.write_text(yaml.safe_dump(document))
    runs, skipped = expand_suite(load_suite(path))
    assert not skipped and len(runs) == 1
    return runs[0]


def test_prospective_stationary_case_resolves_through_actual_frontend(tmp_path, parsed_launch):
    document = yaml.safe_load(SCENARIO.read_text())
    selected = resolve(tmp_path, document)
    assert selected['success']['criterion'] == POST_RECOVERY_ARRIVAL_CRITERION
    assert not runner._requires_ranked_goal(selected)
    argv = runner.build_launch_command(selected, run_id='r4-stationary-test')
    metadata = runner.build_metadata(selected, 'test', 'stationary', '', run_id='r4-stationary-test')
    values = dict(value.split(':=', 1) for value in argv[4:])
    _, owners = parameters(parsed_launch, values)
    pose = '/odom'
    choice = runner._m4_centroid_event_selection(selected)
    assert choice['pose_topic'] == pose and choice['diagnostic_topic'] == RECURRENT_TOPIC
    assert choice['timekeeper_topic'] == '/turtlebot3/timekeeper_chatter'
    for owner in owners.values():
        assert owner['continuous_search_mode'] == 'stationary_v1'
        assert owner['convergence_metric_mode'] == RECURRENT_MODE
        assert owner['pose_topic'] == pose
    # The other two constructors use their preserved simulation-clock defaults.
    assert owners['supervisor_node']['use_sim_time'] is True
    for name in ('supervisor_node', 'gaussian_fill_node'):
        assert owners[name]['stationary_recurrent_fill_request_topic'] == STATIONARY_RECURRENT_FILL_REQUEST_TOPIC
    assert metadata['scenario_runner']['algorithm']['launch_overrides'][
        'stationary_recurrent_fill_request_topic'] == STATIONARY_RECURRENT_FILL_REQUEST_TOPIC


@pytest.mark.parametrize('fault', [
    'physical', 'profile', 'old_schema', 'old_suite', 'holdout', 'centered',
    'moving_policy', 'request_topic', 'diagnostic_topic', 'state_gating',
    'source_gap', 'radius', 'missing_fill', 'missing_ownership', 'topology_binding',
])
def test_stationary_selection_preserves_original_arrival_and_authority_gates(tmp_path, fault):
    document = yaml.safe_load(SCENARIO.read_text())
    case = document['cases'][0]; values = case['algorithm']['launch_overrides']
    if fault == 'physical': document['mode'] = 'physical'
    elif fault == 'profile': case['profiles'] = ['legacy']
    elif fault == 'old_schema': document['schema_version'] = 13
    elif fault == 'old_suite': document['suite_id'] = 'm4_pilot_v9'
    elif fault == 'holdout': case['acceptance_partition'] = 'holdout'
    elif fault == 'centered': values['v2_verification_motion_mode'] = 'centered_tracking_v1'
    elif fault == 'moving_policy': values['v2_direction_policy'] = 'moving_cycle_coherence_v1'
    elif fault == 'request_topic': values['stationary_recurrent_fill_request_topic'] = '/wrong'
    elif fault == 'diagnostic_topic': values['recurrent_diagnostics_topic'] = '/wrong'
    elif fault == 'state_gating': values['convergence_state_gating_enabled'] = False
    elif fault == 'source_gap': values['centroid_maximum_gap_sec'] = .6
    elif fault == 'topology_binding': case.setdefault('disturbances', {})['pose_delay_sec'] = .1
    elif fault == 'radius':
        case['success']['staged_recovery']['global_proximity_radius_m'] = .6
        case['success']['ground_truth']['proximity_radius_m'] = .6
    else:
        name = 'fill_cardinality' if fault == 'missing_fill' else 'escape_command_ownership'
        case['success']['all_of'].remove(name)
    with pytest.raises(ValueError): resolve(tmp_path, document)


def stationary_data():
    data = monitor.data('B', ranked=True)
    resolved, states, events, fills, diagnostics, _ = data
    resolved['suite_id'] = 'v2_method_development_v1'
    resolved['algorithm']['launch_overrides']['convergence_metric_mode'] = RECURRENT_MODE
    resolved['success']['criterion'] = POST_RECOVERY_ARRIVAL_CRITERION
    transaction = request()
    diagnostic = transaction.confirmation
    diagnostic.run_id = states[0][1].run_id
    diagnostic.source_pose_topic = '/odom'
    diagnostic.center_x_m = diagnostic.center_y_m = 1.04
    diagnostic.arc_center_x_m = diagnostic.arc_center_y_m = [1.04, 1.04]
    rehash(transaction)
    assert errors(transaction, expected_run_id=diagnostic.run_id, expected_pose_topic='/odom') == []
    diagnostics[:] = [(2, diagnostic)]
    event = events[0][1]
    set_time(event.stamp, time_to_ns(diagnostic.stamp)+100_000_000)
    event.values = [diagnostic.score_m, diagnostic.confinement_radius_m, 1.04, 1.04,
                    float(diagnostic.search_epoch), float(diagnostic.confirmation_sequence)]
    for _, message in events[1:]+fills:
        if message.source_timestamp_valid:
            message.source_timestamp = transaction.source_timestamp
    return data


def test_stationary_fill_keeps_later_request_coordinate_and_original_diagnostic_support():
    data = stationary_data()
    before = monitor.wire_identity(data[2][0][1])
    events, audit, error = centroid.normalize(data)
    assert error is None, error
    assert events[0][1].source_timestamp == pytest.approx(60., abs=1e-12)
    assert data[3][0][1].source_timestamp == 70.
    assert audit[0]['diagnostic_source_stamp_ns'] == ORIGIN_NS+60_009_000_000
    assert audit[0]['evaluator_source_stamp_ns'] == ORIGIN_NS+60_000_000_000
    assert monitor.wire_identity(data[2][0][1]) == before
    stage, count, evidence, error = runner._staged_recovery_evidence(data[0], data[1], events, data[3])
    assert stage and count and error is None, (evidence, error)


def test_stationary_event_rejects_preorigin_persistence_with_valid_later_model_history():
    data = stationary_data()
    diagnostic = data[4][0][1]
    for name in ('epoch_started_at', 'history_start', 'history_end', 'source_stamp',
                 'receipt_stamp', 'stamp', 'persistence_start'):
        set_time(getattr(diagnostic, name), time_to_ns(getattr(diagnostic, name))-19_000_000_000)
    assert time_to_ns(diagnostic.history_start) > ORIGIN_NS
    assert time_to_ns(diagnostic.persistence_start) < ORIGIN_NS
    _, _, error = centroid.normalize(data)
    assert 'persistence_start precedes time origin' in error


@pytest.mark.parametrize('fault', [None, 'missing_fill', 'conflicting_diagnostic'])
def test_stationary_live_monitor_requires_current_recovery_before_arrival(monkeypatch, fault):
    data = stationary_data()
    schedule = [monitor.odom(0., goal=True)]+monitor.recovered(data)
    if fault == 'missing_fill':
        schedule = [(topic, item) for topic, item in schedule if topic != monitor.FILL]
    elif fault == 'conflicting_diagnostic':
        conflict = deepcopy(data[4][0][1]); conflict.reset_reason = 'conflicting_identity'
        schedule += [(RECURRENT_TOPIC, conflict)]
    schedule += [monitor.odom(100., goal=True)]
    if fault: schedule += [monitor.odom(460., goal=True)]
    result, remaining, _ = monitor.run_callbacks(monkeypatch, data[0], schedule)
    assert not remaining
    assert result['graceful_global_proximity_stop'] is (fault is None)
    assert not result['controller_ranked_goal_observed_live']
    if fault is None:
        assert result['stage_a_observed_live'] and result['fill_cardinality_observed_live']
        assert result['global_proximity_sample_live']['sample_sim_sec'] == 100.


@pytest.mark.parametrize('missing', [False, True])
def test_stationary_serialized_offline_owner_retains_typed_join_and_arrival(monkeypatch, tmp_path, missing):
    resolved, states, events, fills, diagnostics, origins = stationary_data()
    choice = runner._m4_centroid_event_selection(resolved)
    rows = [(stamp, topic, serialize_message(message)) for topic, records in (
        (monitor.STATE, states), (monitor.EVENT, events), (monitor.FILL, fills),
        (choice['timekeeper_topic'], origins),
        (choice['diagnostic_topic'], [] if missing else diagnostics))
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
    assert bool(result['centroid_event_timestamp_binding_error']) is missing
    if missing:
        assert result['local_recovery_stage_passed'] is None
        assert not result['post_recovery_global_proximity_passed']
    else:
        assert result['local_recovery_stage_passed'] is True
        assert result['post_recovery_global_proximity_passed'] is True
    assert not result['counted_candidate_ranked_goal_passed']
