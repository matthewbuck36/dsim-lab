"""Explicit R21 development recovery acceptance preserves all prior defaults."""
from copy import deepcopy

import pytest

from ros_esc.scenario_runner import run_scenario as runner
from test_r3_arrival_evaluator import selected_document, resolve


def document():
    value = selected_document()
    case = value['cases'][0]
    case['algorithm']['launch_overrides']['v2_verification_evidence_policy'] = 'recurrent_trapping_v1'
    success = case['success']
    success['all_of'].remove('required_state_path')
    for scope in success['result_scopes'].values():
        scope['all_of'].remove('required_state_path')
    return value


def test_explicit_trapping_development_keeps_declared_path_diagnostic(tmp_path):
    selected = resolve(tmp_path, document())
    success = selected['success']
    assert success['controller']['required_state_path']
    assert len(success['controller']['required_state_paths']) == 2
    assert 'required_state_path' not in success['all_of']
    assert len(success['all_of']) == 11
    assert 'required_state_path' in resolve(tmp_path, selected_document())['success']['all_of']


@pytest.mark.parametrize('fault', ['default_policy', 'other_suite', 'holdout', 'no_arrival'])
def test_exception_requires_exact_development_arrival_and_policy(tmp_path, fault):
    value = document(); case = value['cases'][0]
    if fault == 'default_policy':
        case['algorithm']['launch_overrides'].pop('v2_verification_evidence_policy')
    elif fault == 'other_suite': value['suite_id'] = 'other_development'
    elif fault == 'holdout': case['acceptance_partition'] = 'holdout'
    else: case['success'].pop('criterion')
    with pytest.raises(ValueError): resolve(tmp_path, value)


@pytest.mark.parametrize('predicate', [
    'recording_complete', 'cleanup_complete', 'ground_truth_goal', 'required_events',
    'required_event_sequence', 'no_forbidden_states', 'no_forbidden_events',
    'local_recovery_stage', 'escape_command_ownership',
    'post_recovery_global_proximity', 'fill_cardinality'])
def test_every_other_primary_predicate_remains_required(tmp_path, predicate):
    value = document(); success = value['cases'][0]['success']
    success['all_of'].remove(predicate)
    for scope in success['result_scopes'].values(): scope['all_of'].remove(predicate)
    with pytest.raises(ValueError): resolve(tmp_path, value)


def test_classification_allows_false_first_path_only_after_other_requirements_pass(tmp_path):
    selected = resolve(tmp_path, document())
    outcomes = dict(required_state_path_passed=False, required_events_passed=True,
        required_event_sequence_passed=True, forbidden_states_absent=True,
        forbidden_events_absent=True, local_recovery_stage_passed=True,
        fill_cardinality_passed=True, escape_command_ownership_passed=True,
        simulation_ground_truth='passed', post_recovery_global_proximity_passed=True,
        result_scopes={'full_lifecycle': {'anchor_observed': True}})
    process = dict(timed_out=False, return_code=0, graceful_global_proximity_stop=True)
    def classify(value):
        return runner.classify_result(selected, {'passed': True}, {'passed': True}, value, process)['passed']
    assert classify(outcomes) is True
    for key in ('local_recovery_stage_passed', 'escape_command_ownership_passed',
                'forbidden_states_absent', 'forbidden_events_absent',
                'post_recovery_global_proximity_passed', 'fill_cardinality_passed'):
        fault = deepcopy(outcomes); fault[key] = False
        assert classify(fault) is False
