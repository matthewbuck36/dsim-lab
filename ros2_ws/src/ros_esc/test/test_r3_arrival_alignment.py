"""Existing escape owners retain authority guards when bearing is supplemental."""
import math
import pickle

import pytest

from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner.scenario_schema import POST_RECOVERY_ARRIVAL_CRITERION
import test_scenario_runner as old


# Exact closed attempt03 event geometry and nearest SEARCH-boundary odometry.
# Source receipt: validation/r3_arrival_alignment_separation.md. No bag access.
CENTER = (0.9968323455755517, 1.1369128918721536)
DIRECTION = (0.575124615259862, 0.818065814541957)
EXIT = (2.4638994067988924, 1.1662629137534182)
RADIUS = 1.3683294852468366
DISTANCE = 1.467360618904201
ALIGNMENT = 0.5913724394154973


def fixture(branch, selected=True):
    data = (old._direct_escape_owner_fixture() if branch == 'direct'
            else old._causal_entry_supervisor_owner_fixture())
    if branch == 'assisted':
        data['resolved'] = old.expand_suite(old.load_suite(old.V8_9_PRIMARY_VISIBLE_PROBE))[0][0]
    if selected:
        data['resolved']['success']['criterion'] = POST_RECOVERY_ARRIVAL_CRITERION
    for _, state in data['states']:
        if state.state not in (runner.AlgorithmState.STATE_ESCAPE_REPULSE,
                               runner.AlgorithmState.STATE_ESCAPE_ASSIST):
            continue
        state.escape_center_x, state.escape_center_y = CENTER
        state.safe_direction_x, state.safe_direction_y = DIRECTION
        state.escape_exit_radius = RADIUS
        if branch == 'direct':
            state.radial_distance = DISTANCE
    event = data['events'][0][1]
    replacements = dict(escape_center_x_m=CENTER[0], escape_center_y_m=CENTER[1],
        approach_selected_direction_x=DIRECTION[0], approach_selected_direction_y=DIRECTION[1],
        escape_exit_radius_m=RADIUS)
    event.values = [replacements.get(name, value) for name, value in zip(event.value_names, event.values)]
    data['odometry'] = [(data['odometry'][0][0], old._odom_message(*EXIT))]
    return data


def evaluate(data):
    before = pickle.dumps(data)
    result = old._evaluate_escape_owner(data)
    assert pickle.dumps(data) == before, 'evaluator changed its evidence inputs'
    return result


@pytest.mark.parametrize('branch', ['direct', 'assisted'])
@pytest.mark.parametrize('selected', [False, True])
def test_actual03_exit_geometry_separates_arrival_from_legacy_bearing(branch, selected):
    passed, evidence, error = evaluate(fixture(branch, selected))
    assert error is None and passed is selected
    if selected:
        assert evidence['fill_to_exit_distance_m'] == pytest.approx(DISTANCE)
        assert evidence['fill_to_exit_alignment'] == pytest.approx(ALIGNMENT)
        assert evidence['exit_alignment_required'] is False
        assert evidence['exit_alignment_threshold'] == .80
        assert evidence['exit_alignment_passed'] is False
        if branch == 'direct':
            assert evidence['ordinary_gesc_ownership_proven']
            assert evidence['returned_search_authority_cleared']
        else:
            assert evidence['post_exit_ordinary_gesc_restored']
            assert evidence['assist_entry_steady_owned_control_sample_count'] == 3
    else:
        assert 'alignment is below 0.80' in evidence['reason']
        assert 'exit_alignment_required' not in evidence


@pytest.mark.parametrize('branch', ['direct', 'assisted'])
def test_unknown_selector_keeps_legacy_guard(branch):
    data = fixture(branch); data['resolved']['success']['criterion'] = 'arrival_unspecified'
    passed, evidence, error = evaluate(data)
    assert error is None and not passed
    assert 'alignment is below 0.80' in evidence['reason']
    assert 'exit_alignment_required' not in evidence


@pytest.mark.parametrize('branch', ['direct', 'assisted'])
def test_selected_good_alignment_is_still_reported(branch):
    data = fixture(branch)
    position = [CENTER[i]+DISTANCE*DIRECTION[i] for i in range(2)]
    data['odometry'] = [(data['odometry'][0][0], old._odom_message(*position))]
    passed, evidence, error = evaluate(data)
    assert error is None and passed
    assert evidence['exit_alignment_passed'] is True
    assert evidence['fill_to_exit_alignment'] == pytest.approx(1.)


@pytest.mark.parametrize('fault,reason', [
    ('inside', 'inside the frozen exit radius'),
    ('no_odometry', 'no measured exit odometry'),
    ('progress', 'fell below the stall threshold'),
    ('stale_event', 'exactly one ESCAPE_STARTED'),
    ('nonzero_supervisor', 'supervisor command is nonzero'),
    ('command_leak', 'not ordinary GESC ownership'),
    ('saturation', 'saturation is invalid'),
    ('returned_authority', 'cleared stable direct exit'),
])
def test_selected_direct_keeps_ownership_safety_and_measured_exit_guards(fault, reason):
    data = fixture('direct')
    if fault == 'inside':
        position = [CENTER[i]+.5*DIRECTION[i] for i in range(2)]
        data['odometry'][0] = (data['odometry'][0][0], old._odom_message(*position))
    elif fault == 'no_odometry': data['odometry'].clear()
    elif fault == 'progress': data['states'][0][1].radial_progress = .01
    elif fault == 'stale_event': data['events'][0] = (499_999_999, data['events'][0][1])
    elif fault == 'nonzero_supervisor': data['commands'][0][1].linear.x = .01
    elif fault == 'command_leak': data['diagnostics'][0][1].combined_command_unsaturated[0] += .01
    elif fault == 'saturation': data['diagnostics'][0][1].final_command[0] = .2
    elif fault == 'returned_authority': data['states'][-1][1].safe_direction_valid = True
    passed, evidence, error = evaluate(data)
    assert error is None and not passed
    assert reason in evidence['reason']


@pytest.mark.parametrize('fault,reason', [
    ('state_authority', 'returned SEARCH state retained escape authority'),
    ('nonzero_command', 'post-exit SEARCH supervisor command is not zero'),
    ('missing_diagnostic', 'post-exit SEARCH has no control diagnostic sample'),
    ('contribution', 'post-exit supervisor contribution is inconsistent'),
    ('saturation', 'post-exit SEARCH final command saturation is invalid'),
    ('missing_return', 'never restored ordinary GESC ownership'),
    ('late_return', 'handoff exceeded its timeout'),
])
def test_selected_assisted_runs_every_later_handoff_guard_after_bad_alignment(fault, reason):
    data = fixture('assisted')
    if fault == 'state_authority': data['states'][-1][1].active_escape_fill_id_valid = True
    elif fault == 'nonzero_command': data['commands'][-1][1].linear.x = .01
    elif fault == 'missing_diagnostic':
        data['diagnostics'] = [(s, m) for s, m in data['diagnostics'] if s < 2_000_000_000]
    elif fault == 'contribution': data['diagnostics'][-1][1].supervisor_contribution[0] = .01
    elif fault == 'saturation': data['diagnostics'][-1][1].final_command[0] = .2
    elif fault == 'missing_return': data['diagnostics'].pop()
    elif fault == 'late_return': data['diagnostics'][-1] = (2_150_000_001, data['diagnostics'][-1][1])
    passed, evidence, error = evaluate(data)
    assert error is None and not passed
    assert reason in evidence['reason']
    assert evidence['exit_alignment_required'] is False
    assert evidence['exit_alignment_passed'] is False
    assert evidence['fill_to_exit_alignment'] == pytest.approx(ALIGNMENT)


@pytest.mark.parametrize('branch', ['direct', 'assisted'])
def test_selected_owner_failure_remains_a_required_predicate(branch):
    data = fixture(branch)
    passed, evidence, error = evaluate(data)
    assert passed and error is None
    resolved = data['resolved']
    resolved['success']['all_of'] = ['escape_command_ownership']
    resolved['success']['result_scopes'] = {}
    outcomes = runner._unavailable_outcomes('unused')
    outcomes.update(readiness_interval_available=True, escape_command_ownership_passed=True,
                    escape_command_ownership=evidence, outcome_error=None)
    process = dict(timed_out=False, return_code=0)
    result = runner.classify_result(resolved, {'passed':True}, {'passed':True}, outcomes, process)
    assert result['passed']
    outcomes['escape_command_ownership_passed'] = False
    result = runner.classify_result(resolved, {'passed':True}, {'passed':True}, outcomes, process)
    assert not result['passed']
