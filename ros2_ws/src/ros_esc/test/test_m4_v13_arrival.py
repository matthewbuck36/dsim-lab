"""V13 selects the existing recorded-pose binding in the actual science owner."""
from copy import deepcopy
from dataclasses import replace

import pytest

from ros_esc.plotting_scripts import m4_pilot as metrics
from ros_esc.plotting_scripts.bag_reader import BagRecord
from test_m4_evaluation_cli import Obj, cli, stamp
from test_m4_v10_science import v10_plan
from test_r12_arrival_binding import recorded_arrival_fixture


VERSION = 'm4-pilot-v13'
NS = 1_000_000_000


def projection_input(monkeypatch, version=VERSION):
    acquired, original_plan, data, origin = recorded_arrival_fixture()
    plan = v10_plan('A', experiment_version=version)
    plan['resolved_scenario'] = deepcopy(original_plan['resolved_scenario'])
    acquired.update(plan, status='COMPLETE', integrity_passed=True)
    outcomes = acquired['runner_result']['outcomes']
    outcomes.update(outcome_error=None, required_state_path_passed=False,
                    counted_candidate_ranked_goal_passed=False)
    current = data.records_by_topic['/odom'][0]
    previous = deepcopy(current.message)
    previous.header.stamp = stamp(103.)
    previous.pose.pose.position.x -= .01
    data.records_by_topic['/odom'].insert(0, replace(current,
        bag_timestamp_ns=1_099_900_000_000, ros_timestamp_ns=103*NS, message=previous))
    for alias in ('algorithm_state', 'algorithm_events', 'gaussian_fills', 'timekeeper'):
        data.topics_by_alias[alias] = dict(alias=alias, topic='/'+alias)
        data.records_by_topic['/'+alias] = []
    data.records_by_topic['/timekeeper'] = [BagRecord('/timekeeper', 'fixture/Timekeeper',
        1_000*NS, None, None, False, Obj(start_time=origin/NS, mode='sim time'), True)]
    labels = dict(spatial_labels_precede_event_join=True, admission_ns=103*NS,
        exposure_end_ns=103_100_000_000, labels=[], residence_intervals=[], pose_faults={},
        poses=[dict(stamp_ns=t, readiness_eligible=True) for t in (103*NS, 103_100_000_000)])
    # Keep this test about the actual projection/binding, with the independently
    # frozen position-label boundary supplied as in the preceding version fixture.
    monkeypatch.setattr(cli.metrics, 'analyze_labels', lambda *a, **k: deepcopy(labels))
    return acquired, plan, data


def project(data, version=VERSION):
    acquired, plan, recorded = data
    result, normalized = cli.analyze_run_data(acquired, plan, recorded, {}, {},
        freeze_labels=lambda value: {'path': 'frozen-position-only', 'sha256': 'receipt'},
        experiment_version=version)
    assert normalized is None
    return result


def test_v13_projection_uses_recorded_pose_time_with_distinct_valid_live_sample(monkeypatch):
    data = projection_input(monkeypatch)
    result = project(data)
    assert result['arrival_binding_method'] == 'recorded_pose_arrival_v1'
    assert result['arrival_measurement_complete'] and result['arrival_live_measurement_complete']
    assert result['arrival_binding_error'] is None
    assert result['arrival_ros_stamp_ns'] == 103_100_000_000
    assert result['arrival_bag_stamp_ns'] == 1_100*NS
    assert result['time_origin_ns'] == 3*NS
    assert result['time_to_arrival_sec'] == pytest.approx(100.1)
    assert result['arrival_live_evidence']['sample_sim_sec'] == 103.2
    assert result['time_to_arrival_sec'] != result['arrival_live_evidence']['sample_sim_sec']-3.
    assert result['scientific_analysis_complete'] is True
    assert result['combined_sequence_passed'] is True
    assert result['combined_sequence_components']['required_state_path_passed'] is False
    assert result['combined_sequence_required_keys'] == list(metrics.arrival_sequence_required_keys(VERSION))
    assert result['combined_sequence_diagnostic_keys'] == ['required_state_path_passed']
    assert result['optional_controller_goal']['ranked_goal_passed'] is False


@pytest.mark.parametrize('version', ['m4-pilot-v11', 'm4-pilot-v12'])
def test_same_distinct_live_sample_preserves_historical_unavailability(monkeypatch, version):
    result = project(projection_input(monkeypatch, version), version)
    assert 'arrival_binding_method' not in result
    assert result['arrival_measurement_complete'] is False
    assert result['time_to_arrival_sec'] is None


def test_low_level_default_is_still_opt_in_even_for_v13(monkeypatch):
    acquired, plan, data = projection_input(monkeypatch)
    historical = cli._arrival_metrics(acquired, plan, data, 3*NS)
    assert 'arrival_binding_method' not in historical
    assert historical['arrival_measurement_complete'] is False


@pytest.mark.parametrize('fault', ['missing_sample', 'duplicate_sample', 'wrong_frame',
    'wrong_alias', 'recorded_distance', 'missing_origin', 'wrong_clock', 'recovery_after_arrival'])
def test_v13_projection_preserves_binding_rejection_without_live_time_fallback(monkeypatch, fault):
    data = projection_input(monkeypatch)
    acquired, _, recorded = data
    sample = recorded.records_by_topic['/odom'][-1]
    if fault == 'missing_sample': recorded.records_by_topic['/odom'].pop()
    elif fault == 'duplicate_sample': recorded.records_by_topic['/odom'].append(deepcopy(sample))
    elif fault == 'wrong_frame': sample.message.header.frame_id = 'map'
    elif fault == 'wrong_alias': recorded.topics_by_alias['pose']['topic'] = '/other'
    elif fault == 'recorded_distance':
        acquired['runner_result']['outcomes']['post_recovery_global_proximity']['distance_m'] += .01
    elif fault == 'missing_origin': recorded.records_by_topic['/timekeeper'].clear()
    elif fault == 'wrong_clock': recorded.records_by_topic['/timekeeper'][0].message.mode = 'wall time'
    elif fault == 'recovery_after_arrival':
        acquired['runner_result']['outcomes']['local_recovery_stage']['stage_a_completion_stamp'] = 1_101*NS
    else: raise AssertionError(fault)
    result = project(data)
    assert result['arrival_measurement_complete'] is False
    assert result['arrival_binding_error']
    assert result['time_to_arrival_sec'] is None
    assert result['scientific_analysis_checks']['arrival_measurement_complete'] is False
    assert result['scientific_analysis_complete'] is False
    assert result['combined_sequence_passed'] is None


def test_v13_observed_nonarrival_remains_complete_measurement_without_time(monkeypatch):
    data = projection_input(monkeypatch)
    data[0]['runner_result']['outcomes']['post_recovery_global_proximity_passed'] = False
    data[0]['runner_result']['record_process'].clear()
    result = project(data)
    assert result['arrival_binding_method'] == metrics.RECORDED_ARRIVAL_BINDING
    assert result['arrival_measurement_complete'] is True
    assert result['arrival_passed'] is False
    assert result['time_to_arrival_sec'] is None
    assert result['combined_sequence_passed'] is False
    assert result['scientific_analysis_complete'] is True
