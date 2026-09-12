"""Selected recurrent evidence retention and simulation-clock coverage."""
from copy import deepcopy
from types import SimpleNamespace

import pytest
from builtin_interfaces.msg import Time

from ros_esc.convergence_detector_node.recurrent_contract import RECURRENT_MODE, RECURRENT_TOPIC
from ros_esc.experiment_recording.record_run import applicable_topics, require_selected_algorithm_topics
from ros_esc.experiment_recording.validate_run import centroid_stream_errors
from ros_esc.scenario_runner.run_scenario import _m4_centroid_event_selection
from ros_esc.v2_stream import set_time
from test_v2_recording_contract import prepared
from test_v2_source_contract import resolved

ALIAS = 'recurrent_convergence_diagnostics'


def inputs():
    argv, _, manifest = prepared()
    argv = [arg for arg in argv if not arg.startswith('convergence_metric_mode:=')]
    argv.append('convergence_metric_mode:=' + RECURRENT_MODE)
    return applicable_topics(manifest, 'simulation'), argv


def descriptor(entries):
    return next(row for row in entries if row['alias'] == ALIAS)


def test_selected_recurrent_requires_actual_typed_stream_and_preserves_input():
    entries, argv = inputs()
    before = deepcopy(entries)
    result = require_selected_algorithm_topics(entries, 'simulation', argv)
    assert entries == before
    row = descriptor(result)
    assert row['required'] and row['singleton_publisher'] and row['minimum_messages'] >= 1
    assert row['algorithm_metric_mode'] == RECURRENT_MODE and row['topic'] == RECURRENT_TOPIC
    assert row['coverage'] == 'motion' and row['algorithm_maximum_diagnostic_gap_sec'] == 1.
    assert row['algorithm_invalid_status_heartbeat_enabled'] is True
    assert require_selected_algorithm_topics(result, 'simulation', argv) == result
    legacy = next(row for row in result if row['alias'] == 'centroid_convergence_diagnostics')
    assert not legacy['required'] and 'algorithm_metric_mode' not in legacy


@pytest.mark.parametrize('fault', ['missing', 'type', 'topic'])
def test_selected_recurrent_cannot_be_recorded_as_legacy_or_other_topic(fault):
    entries, argv = inputs()
    if fault == 'missing':
        entries = [row for row in entries if row['alias'] != ALIAS]
    else:
        descriptor(entries)[fault] = ('ros_esc_interfaces/msg/CentroidConvergenceDiagnostics'
                                     if fault == 'type' else '/wrong')
    with pytest.raises(ValueError, match='matching typed recording topic'):
        require_selected_algorithm_topics(entries, 'simulation', argv)


@pytest.mark.parametrize('key,value', [
    ('algorithm_metric_mode', 'centroid_two_block_v2'),
    ('algorithm_maximum_source_gap_sec', .7),
    ('algorithm_pose_stale_sec', .8),
    ('algorithm_invalid_status_heartbeat_enabled', False),
    ('algorithm_clock_admission', 'unknown'),
])
def test_retained_descriptor_cannot_silently_change_authority(key, value):
    entries, argv = inputs()
    selected = require_selected_algorithm_topics(entries, 'simulation', argv)
    descriptor(selected)[key] = value
    with pytest.raises(ValueError, match='recorded recurrent descriptor differs'):
        require_selected_algorithm_topics(selected, 'simulation', argv)


def test_selected_descriptor_cannot_be_reused_on_pde():
    entries, argv = inputs()
    selected = require_selected_algorithm_topics(entries, 'simulation', argv)
    argv = [arg.replace(RECURRENT_MODE, 'pde_mean_v1') for arg in argv]
    with pytest.raises(ValueError, match='recorded recurrent metric mode differs'):
        require_selected_algorithm_topics(selected, 'simulation', argv)


@pytest.mark.parametrize('value', ['nan', '-1', '0', '1e-20', 'inf'])
def test_invalid_source_allowance_fails_before_recording(value):
    entries, argv = inputs()
    with pytest.raises(ValueError, match='finite positive seconds'):
        require_selected_algorithm_topics(entries, 'simulation', argv + ['centroid_maximum_gap_sec:=' + value])


def test_stationary_mode_not_admitted_without_compatible_request_envelope():
    entries, argv = inputs()
    argv = [arg.replace('rolling_gesc_v2', 'stationary_v1') for arg in argv]
    entries = [row for row in entries if row['alias'] != 'stationary_recurrent_fill_requests']
    with pytest.raises(ValueError, match='selected stationary stream missing or incompatible'):
        require_selected_algorithm_topics(entries, 'simulation', argv)


def test_unselected_legacy_has_optional_recurrent_topic_only():
    entries, _ = inputs()
    row = descriptor(require_selected_algorithm_topics(entries, 'simulation', []))
    assert not row['required'] and row['minimum_messages'] == 0 and row['coverage'] == 'none'
    assert not any(key.startswith('algorithm_') for key in row)


def test_new_evaluator_route_selects_exact_new_topic():
    scenario = resolved()
    scenario['suite_id'] = 'v2_method_development_v1'
    scenario['algorithm']['launch_overrides']['convergence_metric_mode'] = RECURRENT_MODE
    choice = _m4_centroid_event_selection(scenario)
    assert choice['metric_mode'] == RECURRENT_MODE and choice['diagnostic_topic'] == RECURRENT_TOPIC
    scenario['algorithm']['launch_overrides']['continuous_search_mode'] = 'stationary_v1'
    stationary = _m4_centroid_event_selection(scenario)
    assert stationary['diagnostic_topic'] == RECURRENT_TOPIC
    assert stationary['timekeeper_topic'] == '/turtlebot3/timekeeper_chatter'
    scenario['suite_id'] = 'm4_pilot_v9'
    with pytest.raises(ValueError, match='requires selected method development simulation'):
        _m4_centroid_event_selection(scenario)


def stamp(value):
    return set_time(Time(), round(value * 1e9))


def test_coverage_uses_simulated_time_and_keeps_invalid_history_status():
    clocks = [(0, SimpleNamespace(clock=stamp(100))), (100_000_000_000, SimpleNamespace(clock=stamp(102)))]
    records = [(int(i * 50e9), SimpleNamespace(stamp=stamp(100+i), history_valid=False)) for i in range(3)]
    assert centroid_stream_errors(records, clocks, 0, 100_000_000_000, 1.01, diagnostic_kind='recurrent') == []
    errors = centroid_stream_errors(records[::2], clocks, 0, 100_000_000_000, 1.01, diagnostic_kind='recurrent')
    assert errors == ['recurrent diagnostics have a simulated publication coverage gap']
    assert centroid_stream_errors([], clocks, 0, 100_000_000_000, 1., diagnostic_kind='recurrent')


def test_scenario_roundtrip_forwards_selected_modes_and_keeps_metadata(tmp_path):
    from pathlib import Path
    import yaml
    from ros_esc.scenario_runner.scenario_schema import load_suite, expand_suite
    from ros_esc.scenario_runner.run_scenario import build_launch_command, build_metadata
    template = Path('/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/integrated_route_v1/scenario_template.yaml')
    document = yaml.safe_load(template.read_text())
    selected = document['cases'][0]['algorithm']['launch_overrides']
    selected.update(convergence_metric_mode=RECURRENT_MODE,
                    v2_verification_motion_mode='centered_tracking_v1',
                    recurrent_diagnostics_topic=RECURRENT_TOPIC,
                    centroid_invalid_status_heartbeat_enabled=False)
    path = tmp_path/'selected.yaml'
    path.write_text(yaml.safe_dump(document))
    runs, skipped = expand_suite(load_suite(path))
    assert not skipped and len(runs) == 1
    argv = build_launch_command(runs[0], run_id='recurrent-schema-test')
    metadata = build_metadata(runs[0], 'test', 'recurrent', '', run_id='recurrent-schema-test')
    for key in ('convergence_metric_mode', 'v2_verification_motion_mode', 'recurrent_diagnostics_topic'):
        assert f'{key}:={selected[key]}' in argv
        assert metadata['scenario_runner']['algorithm']['launch_overrides'][key] == selected[key]
    entries, _ = inputs()
    assert descriptor(require_selected_algorithm_topics(entries, 'simulation', argv))['required']


@pytest.mark.parametrize('mutation,error', [
    ({'continuous_search_mode':'stationary_v1'}, 'requires rolling_gesc_v2'),
    ({'centroid_invalid_status_heartbeat_enabled':True}, 'requires centroid mode'),
    ({'convergence_state_gating_enabled':False}, 'requires convergence_state_gating_enabled'),
    ({'recurrent_diagnostics_topic':'/wrong'}, 'differs from fixed contract'),
    ({'centroid_maximum_gap_sec':.6}, 'exceeds fixed'),
    ({'v2_verification_motion_mode':'unrecognized'}, 'unsupported'),
])
def test_scenario_rejects_incompatible_selected_method(mutation, error):
    from ros_esc.scenario_runner.scenario_schema import _validate_correction_overrides
    values = dict(convergence_metric_mode=RECURRENT_MODE,
                  convergence_state_gating_enabled=True,
                  continuous_search_mode='rolling_gesc_v2',
                  v2_candidate_radius_m=.75, v2_candidate_epsilon_m=.15,
                  v2_verification_motion_mode='centered_tracking_v1')
    values.update(mutation)
    with pytest.raises(ValueError, match=error):
        _validate_correction_overrides(values, {}, 'recurrent')


def test_recorded_recurrent_configuration_is_attributed_to_actual_detector():
    from ros_esc_interfaces.msg import AlgorithmEvent
    from ros_esc.experiment_recording.validate_run import algorithm_event_producer_stream
    event = AlgorithmEvent(event_type=AlgorithmEvent.EVENT_CONFIGURATION,
                           detail=RECURRENT_MODE+' source-time configuration')
    assert algorithm_event_producer_stream(event) == 'convergence_detector'
    event.detail = 'unrecognized_recurrent_mode source-time configuration'
    assert algorithm_event_producer_stream(event) is None
