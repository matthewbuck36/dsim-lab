"""Exact two-block selection through existing recorder and scenario owners.

These fixtures assert scoped evidence contracts; synthetic incomplete bags do
not claim run acceptance. Historical scenarios and recordings remain untouched.
"""

from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from rclpy.serialization import deserialize_message, serialize_message

from ros_esc.experiment_recording.record_run import (
    applicable_topics, load_manifest, require_selected_algorithm_topics,
    stationary_centroid_config_from_target,
)
from ros_esc.experiment_recording.validate_run import algorithm_event_producer_stream
from ros_esc.scenario_runner.scenario_schema import (
    _validate_correction_overrides, expand_suite, load_suite,
)
from ros_esc.scenario_runner.run_scenario import build_launch_command, build_metadata
from ros_esc_interfaces.msg import AlgorithmEvent
from test_convergence_detector_policy import centroid_node  # noqa: F401
from test_q3_centroid_clock_admission import clock_node  # noqa: F401
from test_q3_centroid_recording_contract import (  # noqa: F401
    emitted_confirmation, recorded_run,
)


PACKAGE = Path(__file__).resolve().parents[1]
OLD, NEW = 'centroid_windows_v2', 'centroid_two_block_v2'
ALIAS = 'centroid_convergence_diagnostics'


def target(metric=NEW, mode='stationary_v1', profile='robust_gaussian_v1'):
    return [f'algorithm_profile:={profile}', f'convergence_metric_mode:={metric}',
            f'continuous_search_mode:={mode}', 'algorithm_pose_topic:=/odom']


def entries():
    return applicable_topics(load_manifest(
        PACKAGE / 'ros_esc/experiment_recording/topic_manifest.yaml'), 'simulation')


@pytest.mark.parametrize('metric', [OLD, NEW])
def test_selected_recorder_retains_exact_formula_without_changing_defaults(metric):
    original = entries()
    before = deepcopy(original)
    selected = require_selected_algorithm_topics(original, 'simulation', target(metric))
    assert original == before
    diagnostic = next(entry for entry in selected if entry['alias'] == ALIAS)
    assert diagnostic['algorithm_metric_mode'] == metric
    assert diagnostic['algorithm_source_pose_topic'] == '/odom'
    assert diagnostic['required'] and diagnostic['minimum_messages'] >= 1
    stationary = stationary_centroid_config_from_target(target(metric))
    assert stationary['metric_mode'] == metric
    assert (stationary['window_sec'], stationary['epsilon_m'],
            stationary['maximum_radius_m']) == (3., .06, .5)
    request = next(entry for entry in selected if entry['alias'] == 'stationary_fill_requests')
    assert request['stationary_centroid_config'] == stationary
    assert require_selected_algorithm_topics(selected, 'simulation', target(metric)) == selected


def test_prospective_method_parameters_are_explicit_in_selected_metadata():
    selected = stationary_centroid_config_from_target(target() + [
        'centroid_window_sec:=6', 'centroid_epsilon_m:=0.18',
        'centroid_maximum_radius_m:=0.50'])
    assert (selected['window_sec'], selected['epsilon_m'],
            selected['maximum_radius_m']) == (6., .18, .5)


@pytest.mark.parametrize('metric', [OLD, NEW])
@pytest.mark.parametrize('mode,profile', [
    ('rolling_gesc_v2', 'robust_gaussian_v1'), ('stationary_v1', 'legacy'),
])
def test_stationary_request_contract_does_not_select_other_owners(metric, mode, profile):
    assert stationary_centroid_config_from_target(target(metric, mode, profile)) is None


def test_pde_and_absent_selection_leave_manifest_unselected():
    original = entries()
    for argv in ([], target('pde_mean_v1')):
        assert require_selected_algorithm_topics(original, 'simulation', argv) == original
        assert stationary_centroid_config_from_target(argv) is None


@pytest.mark.parametrize('metric', [OLD, NEW])
def test_selected_centroid_recording_requires_simulation(metric):
    with pytest.raises(ValueError, match='requires simulation'):
        require_selected_algorithm_topics(entries(), 'physical', target(metric))


@pytest.mark.parametrize('metric', [OLD, NEW])
def test_recorded_explicit_metric_identity_cannot_be_rewritten_by_argv(metric):
    selected = require_selected_algorithm_topics(entries(), 'simulation', target(metric))
    other = OLD if metric == NEW else NEW
    with pytest.raises(ValueError, match='metric mode differs'):
        require_selected_algorithm_topics(selected, 'simulation', target(other))


@pytest.mark.parametrize('selected', [OLD, NEW])
@pytest.mark.parametrize('observed', [OLD, NEW])
def test_full_validator_binds_observed_formula_to_selected_argv(recorded_run, selected, observed):
    run = recorded_run
    run.metadata['target_argv'][0] = 'convergence_metric_mode:=' + selected
    message = run.message
    # Independently computed typed geometry: six points along a 0.1 m line.
    # Adjacent-shift sum is 0.10 m; block-mean distance is 0.06 m.
    message.metric_mode = observed
    message.centroid_x_m = [0., .02, .04, .06, .08, .10]
    message.centroid_y_m = [0.] * 6
    message.displacement_m = [.02] * 5
    message.center_x_m, message.center_y_m = .05, 0.
    message.confinement_radius_m, message.epsilon_m = .05, .11
    message.score_m = .06 if observed == NEW else .10
    encoded = deserialize_message(serialize_message(message), type(message))
    assert encoded.metric_mode == observed and encoded.score_m == message.score_m
    result = run.run()
    assert result['passed'] is (selected == observed), result
    if selected != observed:
        assert any('metric mode' in error for error in result['detail'])
    else:
        # Correct identity cannot authorize the other formula's arithmetic.
        message.score_m = .10 if observed == NEW else .06
        assert not run.run()['passed']


def test_switching_only_selected_mode_cannot_relabel_historical_diagnostic(recorded_run):
    run = recorded_run
    assert run.run()['passed']
    run.metadata['target_argv'][0] = 'convergence_metric_mode:=' + NEW
    result = run.run()
    assert not result['passed']
    assert run.message.metric_mode == OLD


@pytest.mark.parametrize('metric', [OLD, NEW])
def test_source_time_configuration_event_keeps_detector_producer(metric):
    event = AlgorithmEvent(event_type=1, detail=metric + ' source-time configuration')
    assert algorithm_event_producer_stream(event) == 'convergence_detector'
    event.detail = 'unknown_mode source-time configuration'
    assert algorithm_event_producer_stream(event) is None


@pytest.mark.parametrize('metric', [OLD, NEW])
def test_scenario_selector_preserves_explicit_state_gating(metric):
    overrides = {'convergence_metric_mode': metric,
                 'centroid_window_sec': 6., 'centroid_epsilon_m': .18,
                 'centroid_maximum_radius_m': .5}
    with pytest.raises(ValueError, match='requires convergence_state_gating_enabled'):
        _validate_correction_overrides(overrides, {}, 'q7')
    overrides['convergence_state_gating_enabled'] = True
    _validate_correction_overrides(overrides, {}, 'q7')
    overrides['convergence_metric_mode'] = 'centroid_two_block_v3'
    with pytest.raises(ValueError, match='unsupported'):
        _validate_correction_overrides(overrides, {}, 'q7')


@pytest.mark.parametrize('mode', ['stationary_v1', 'rolling_gesc_v2'])
def test_new_explicit_scenario_roundtrip_reaches_recording_without_editing_old_suite(tmp_path, mode):
    original = PACKAGE / 'ros_esc/scenario_runner/scenarios/phase06_smoke.yaml'
    retained = original.read_bytes()
    document = yaml.safe_load(retained)
    case = document['cases'][0]
    case['profiles'] = ['robust_gaussian_v1']
    case['algorithm']['launch_overrides'] = {
        'continuous_search_mode': mode, 'convergence_metric_mode': NEW,
        'convergence_state_gating_enabled': True, 'centroid_window_sec': 6.,
        'centroid_epsilon_m': .18, 'centroid_maximum_radius_m': .5,
    }
    if mode == 'rolling_gesc_v2':
        case['algorithm']['launch_overrides'].update(
            v2_candidate_radius_m=.5, v2_candidate_epsilon_m=.18)
    path = tmp_path / 'prospective_q7_selection.yaml'
    path.write_text(yaml.safe_dump(document))
    runs, _ = expand_suite(load_suite(path))
    assert len(runs) == 1
    argv = build_launch_command(runs[0], run_id='q7_selection')
    metadata = build_metadata(runs[0], 'test', 'q7-selection', '', run_id='q7_selection')
    assert metadata['scenario_runner']['algorithm']['launch_overrides']['convergence_metric_mode'] == NEW
    selected = require_selected_algorithm_topics(entries(), 'simulation', argv)
    diagnostic = next(entry for entry in selected if entry['alias'] == ALIAS)
    assert diagnostic['algorithm_metric_mode'] == NEW
    request = next(entry for entry in selected if entry['alias'] == 'stationary_fill_requests')
    assert bool(request.get('stationary_centroid_config')) is (mode == 'stationary_v1')
    assert original.read_bytes() == retained
