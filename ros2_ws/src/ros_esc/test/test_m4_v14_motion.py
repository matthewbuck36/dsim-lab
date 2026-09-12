"""Fresh V14 routing to qualified R22 motion and existing recorded arrival."""
from copy import deepcopy
from dataclasses import replace

import pytest

from ros_esc.scenario_runner.m4_scenario import expected_slots, experiment_run_id
from test_m4_evaluation_cli import cli
from test_r9_motion_readiness import fixture, extra_zero
from test_m4_v13_arrival import projection_input, project


VERSION = 'm4-pilot-v14'
BASIS = 'full_publication_order_v1'


def plan(arm='D', version=VERSION):
    row = deepcopy(expected_slots(version)[4+'ABCD'.index(arm)])
    row['run_id'] = experiment_run_id(row, version)
    row['resolved_scenario'] = {'algorithm': {'launch_overrides': {'algorithm_pose_topic': '/pose'}},
        'success': {'criterion': 'post_recovery_arrival_v1'}}
    return row


def split_boundary(data):
    for alias in ('command_final', 'control_diagnostics'):
        rows = data.records_by_topic['/'+alias]
        outside = alias == 'command_final'
        rows[0] = replace(rows[0], bag_timestamp_ns=data.readiness_start_ns+(-1 if outside else 1),
                          in_readiness_interval=not outside)
    data.records_by_topic['/command_final'][0].message.linear.x = 0.
    data.records_by_topic['/control_diagnostics'][0].message.final_command = [0.]*6


@pytest.mark.parametrize('arm', ['C', 'D'])
def test_fresh_v14_uses_full_pairing_but_v13_default_remains_unavailable(arm):
    data = fixture()
    split_boundary(data)
    selected = cli._motion_metrics(data, plan(arm), {'complete': True})
    assert selected['status'] == 'OBSERVED_CONTINUOUS_ACQUISITION'
    assert selected['analysis_complete'] and selected['authority_complete']
    assert selected['mandatory_stopped_acquisitions'] == 0
    assert selected['command_pairing_scope'] == BASIS
    assert selected['command_pairing_admitted_pair_count'] == 50
    assert [row['index'] for row in selected['command_pairing_excluded_boundary_pairs']] == [0]
    old_plan = plan(arm, 'm4-pilot-v13')
    old = cli._motion_metrics(data, old_plan, {'complete': True})
    assert old == cli._v10_motion_metrics(data, old_plan, {'complete': True})
    assert old['status'] == 'EVIDENCE_UNAVAILABLE'
    assert old['mandatory_stopped_acquisitions'] is None
    assert old['command_pairing_scope'] == 'recorded_readiness_interval_v1'


@pytest.mark.parametrize('arm', ['A', 'B'])
def test_stationary_arms_remain_not_applicable(arm):
    assert cli._motion_metrics(fixture(), plan(arm), {'complete': True}) == dict(
        mandatory_stopped_acquisitions=None, status='NOT_APPLICABLE')


@pytest.mark.parametrize('fault', ['unpaired_outside', 'nonfinite', 'vector_mismatch', 'authority'])
def test_v14_cannot_hide_full_stream_or_authority_faults(fault):
    data = fixture()
    if fault == 'unpaired_outside':
        extra_zero(data, 'command_final', data.readiness_start_ns-1)
    elif fault == 'nonfinite':
        data.records_by_topic['/command_final'][20].message.angular.y = float('nan')
    elif fault == 'vector_mismatch':
        data.records_by_topic['/control_diagnostics'][20].message.final_command[1] = .01
    result = cli._motion_metrics(data, plan(), {'complete': fault != 'authority'})
    assert not result['analysis_complete']
    assert result['mandatory_stopped_acquisitions'] is None
    assert result['status'] == 'EVIDENCE_UNAVAILABLE'


def test_original_v13_retained_plan_does_not_implicitly_select_new_pairing():
    data = fixture()
    split_boundary(data)
    retained = deepcopy(expected_slots(VERSION)[3])
    retained['resolved_scenario'] = plan()['resolved_scenario']
    assert retained['experiment_version'] == 'm4-pilot-v13'
    result = cli._motion_metrics(data, retained, {'complete': True})
    assert result['status'] == 'EVIDENCE_UNAVAILABLE'
    assert result['command_pairing_scope'] == 'recorded_readiness_interval_v1'


def test_fresh_v14_arrival_uses_recorded_pose_owner_and_optional_goal(monkeypatch):
    acquired, _, data = projection_input(monkeypatch, 'm4-pilot-v13')
    fresh = plan('A')
    fresh['resolved_scenario'] = deepcopy(acquired['resolved_scenario'])
    acquired.update(fresh)
    result = project((acquired, fresh, data), VERSION)
    assert result['arrival_binding_method'] == 'recorded_pose_arrival_v1'
    assert result['arrival_measurement_complete'] and result['arrival_live_measurement_complete']
    assert result['time_to_arrival_sec'] == pytest.approx(100.1)
    assert result['arrival_ros_stamp_ns'] == 103_100_000_000
    assert result['arrival_live_evidence']['sample_sim_sec'] == 103.2
    assert result['combined_sequence_passed'] is True
    assert result['combined_sequence_components']['required_state_path_passed'] is False
    assert result['optional_controller_goal']['ranked_goal_passed'] is False


def test_v14_arrival_missing_recorded_sample_is_unavailable_without_live_fallback(monkeypatch):
    acquired, _, data = projection_input(monkeypatch, 'm4-pilot-v13')
    fresh = plan('A')
    fresh['resolved_scenario'] = deepcopy(acquired['resolved_scenario'])
    acquired.update(fresh)
    data.records_by_topic['/odom'].pop()
    result = project((acquired, fresh, data), VERSION)
    assert result['arrival_binding_method'] == 'recorded_pose_arrival_v1'
    assert not result['arrival_measurement_complete']
    assert result['time_to_arrival_sec'] is None
