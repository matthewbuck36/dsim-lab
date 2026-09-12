"""Opt-in recorded arrival binding through the existing owner; no bag or model."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace as Obj

import pytest

from ros_esc.plotting_scripts.bag_reader import BagData, BagRecord
from test_m4_evaluation_cli import cli, stamp
from test_m4_v10_science import arrival_fixture, v10_plan

NS = 1_000_000_000


def recorded_arrival_fixture():
    """Distinct deterministic samples; source time is a fixture, not V12 time."""
    goal = dict(x_m=3.5, y_m=3.5)
    xy = dict(x_m=3.1, y_m=3.5)
    live_xy = dict(x_m=3.2, y_m=3.5)
    evidence = dict(position=xy, distance_m=3.5-3.1,
        sample_bag_stamp=1_100*NS, interpolation_used=False,
        proximity_radius_m=.5, global_source_id='global', global_point=goal)
    live = dict(position=live_xy, distance_m=3.5-3.2, sample_sim_sec=103.2,
        interpolation_used=False, proximity_radius_m=.5,
        controller_ranked_goal_required=False, callback_sequence=40)
    flags = {key: True for key in ('local_recovery_stage_passed', 'fill_cardinality_passed',
        'escape_command_ownership_passed', 'required_events_passed',
        'required_event_sequence_passed', 'forbidden_states_absent', 'forbidden_events_absent')}
    acquired = dict(runner_result=dict(outcomes=dict(flags,
        post_recovery_global_proximity_passed=True, post_recovery_global_proximity=evidence,
        local_recovery_stage={'stage_a_completion_stamp': 1_090*NS}),
        record_process=dict(global_proximity_observed_live=True, global_proximity_sample_live=live)))
    planned = v10_plan('B', experiment_version='m4-pilot-v12')
    planned['resolved_scenario']['sources'] = [dict(id='global', evaluation_role='goal', **goal)]
    planned['resolved_scenario']['success'].update(
        staged_recovery=dict(global_source_id='global', global_proximity_radius_m=.5),
        ground_truth=dict(method='declared_global_proximity', global_source_id='global', proximity_radius_m=.5))
    message = Obj(header=Obj(stamp=stamp(103.1), frame_id='odom'),
                  pose=Obj(pose=Obj(position=Obj(x=xy['x_m'], y=xy['y_m']))))
    record = BagRecord('/odom', 'nav_msgs/msg/Odometry', 1_100*NS, 103_100_000_000,
                       None, False, message, True)
    bag = BagData(Path('/unused'), {'/odom': 'nav_msgs/msg/Odometry'},
                  {'pose': {'alias': 'pose', 'topic': '/odom'}}, {'/odom': [record]}, 1_000*NS, 1_200*NS)
    return acquired, planned, bag, 3*NS


def measured(data):
    return cli._arrival_metrics(*data, binding_method=cli.RECORDED_ARRIVAL_BINDING)


def test_distinct_live_pose_keeps_exact_recorded_timestamp_and_nonzero_origin():
    data = recorded_arrival_fixture()
    result = measured(data)
    assert result['arrival_measurement_complete'], result
    assert result['arrival_live_measurement_complete']
    assert result['arrival_binding_method'] == 'recorded_pose_arrival_v1'
    assert result['arrival_binding_error'] is None
    assert result['time_to_arrival_sec'] == pytest.approx(100.1)
    assert result['arrival_ros_stamp_ns'] == 103_100_000_000
    assert result['arrival_bag_stamp_ns'] == 1_100*NS
    assert result['arrival_live_evidence']['sample_sim_sec'] == 103.2
    assert result['time_to_arrival_sec'] != result['arrival_live_evidence']['sample_sim_sec']-3.


def test_historical_default_remains_exact_and_no_version_auto_selects():
    acquired, bag = arrival_fixture()
    expected = dict(arrival_criterion='post_recovery_arrival_v1', arrival_passed=True,
        time_to_arrival_sec=155.971, arrival_ros_stamp_ns=155_971_000_000,
        arrival_bag_stamp_ns=156_000_000_000, arrival_distance_m=.49859569167329104,
        arrival_evidence=deepcopy(acquired['runner_result']['outcomes']['post_recovery_global_proximity']),
        arrival_live_evidence=deepcopy(acquired['runner_result']['record_process']['global_proximity_sample_live']),
        arrival_measurement_complete=True,
        time_to_arrival_scope='Exact retained evaluator pose ROS stamp minus original Timekeeper origin; optional GOAL_HOLD separate.')
    for version in ('m4-pilot-v10', 'm4-pilot-v11', 'm4-pilot-v12'):
        assert cli._arrival_metrics(acquired, v10_plan(experiment_version=version), bag, 0) == expected
    data = recorded_arrival_fixture()
    original = cli._arrival_metrics(*data)
    assert not original['arrival_measurement_complete'] and original['time_to_arrival_sec'] is None
    assert 'arrival_binding_method' not in original


@pytest.mark.parametrize('fault', [
    'missing', 'duplicate', 'not_ready', 'wrong_bag_stamp', 'wrong_alias', 'wrong_frame',
    'wrong_topic', 'wrong_type', 'unbounded_readiness', 'outside_readiness',
    'source_before_origin', 'source_at_origin', 'source_missing', 'source_nsec_range',
    'source_projection_mismatch', 'origin_nan', 'origin_boolean', 'position_nan',
    'changed_recorded_position', 'changed_recorded_distance', 'recorded_interpolated',
    'wrong_global_point', 'wrong_global_id', 'duplicate_global_source', 'wrong_radius',
    'recovery_unavailable', 'recovery_after_arrival', 'ownership_invalid', 'outcome_error',
    'live_missing', 'live_not_observed', 'live_outside', 'live_time_nan', 'live_interpolated',
    'live_distance_changed', 'unsupported_criterion',
])
def test_invalid_binding_stays_unavailable_without_live_time_substitution(fault):
    acquired, planned, bag, origin = recorded_arrival_fixture()
    record = bag.records_by_topic['/odom'][0]
    outcome = acquired['runner_result']['outcomes']; evidence = outcome['post_recovery_global_proximity']
    live = acquired['runner_result']['record_process']['global_proximity_sample_live']
    if fault == 'missing': bag.records_by_topic['/odom'].clear()
    elif fault == 'duplicate': bag.records_by_topic['/odom'].append(deepcopy(record))
    elif fault == 'not_ready': record = replace(record, in_readiness_interval=False)
    elif fault == 'wrong_bag_stamp': record = replace(record, bag_timestamp_ns=record.bag_timestamp_ns+1)
    elif fault == 'wrong_alias': bag.topics_by_alias['pose']['topic'] = '/other'
    elif fault == 'wrong_frame': record.message.header.frame_id = 'map'
    elif fault == 'wrong_topic': record = replace(record, topic='/other')
    elif fault == 'wrong_type': record = replace(record, type_name='wrong/Type')
    elif fault == 'unbounded_readiness': bag = replace(bag, readiness_end_ns=None)
    elif fault == 'outside_readiness': bag = replace(bag, readiness_end_ns=1_099*NS)
    elif fault == 'source_before_origin': record.message.header.stamp = stamp(2.)
    elif fault == 'source_at_origin': record.message.header.stamp = stamp(3.)
    elif fault == 'source_missing': del record.message.header.stamp
    elif fault == 'source_nsec_range': record.message.header.stamp.nanosec = NS
    elif fault == 'source_projection_mismatch': record = replace(record, ros_timestamp_ns=103*NS)
    elif fault == 'origin_nan': origin = float('nan')
    elif fault == 'origin_boolean': origin = True
    elif fault == 'position_nan': record.message.pose.pose.position.x = float('nan')
    elif fault == 'changed_recorded_position': evidence['position']['x_m'] += .01
    elif fault == 'changed_recorded_distance': evidence['distance_m'] += .01
    elif fault == 'recorded_interpolated': evidence['interpolation_used'] = True
    elif fault == 'wrong_global_point': evidence['global_point']['x_m'] += 1.
    elif fault == 'wrong_global_id': evidence['global_source_id'] = 'local'
    elif fault == 'duplicate_global_source': planned['resolved_scenario']['sources'] *= 2
    elif fault == 'wrong_radius': planned['resolved_scenario']['success']['ground_truth']['proximity_radius_m'] = .6
    elif fault == 'recovery_unavailable': outcome['local_recovery_stage_passed'] = False
    elif fault == 'recovery_after_arrival': outcome['local_recovery_stage']['stage_a_completion_stamp'] = 1_101*NS
    elif fault == 'ownership_invalid': outcome['escape_command_ownership_passed'] = False
    elif fault == 'outcome_error': outcome['outcome_error'] = 'unbound fill'
    elif fault == 'live_missing': acquired['runner_result']['record_process'].clear()
    elif fault == 'live_not_observed': acquired['runner_result']['record_process']['global_proximity_observed_live'] = False
    elif fault == 'live_outside': live.update(position=dict(x_m=2., y_m=3.5), distance_m=1.5)
    elif fault == 'live_time_nan': live['sample_sim_sec'] = float('nan')
    elif fault == 'live_interpolated': live['interpolation_used'] = True
    elif fault == 'live_distance_changed': live['distance_m'] += .01
    elif fault == 'unsupported_criterion': planned['resolved_scenario']['success']['criterion'] = 'other'
    else: raise AssertionError(fault)
    if bag.records_by_topic['/odom']:
        bag.records_by_topic['/odom'][0] = record
    result = measured((acquired, planned, bag, origin))
    assert result['arrival_measurement_complete'] is False, (fault, result)
    assert result['time_to_arrival_sec'] is result['arrival_ros_stamp_ns'] is result['arrival_bag_stamp_ns'] is None
    assert result['arrival_binding_error']


def test_valid_censor_has_no_fabricated_arrival_even_without_pose_or_live_sample():
    acquired, planned, bag, origin = recorded_arrival_fixture()
    acquired['runner_result']['outcomes']['post_recovery_global_proximity_passed'] = False
    acquired['runner_result']['record_process'].clear()
    bag.records_by_topic.clear()
    result = measured((acquired, planned, bag, origin))
    assert result['arrival_passed'] is False and result['arrival_measurement_complete'] is True
    assert result['time_to_arrival_sec'] is None


def test_unknown_binding_method_is_not_silently_accepted():
    with pytest.raises(ValueError, match='unsupported arrival binding'):
        cli._arrival_metrics(*recorded_arrival_fixture(), binding_method='other')
