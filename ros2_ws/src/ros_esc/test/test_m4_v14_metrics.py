"""V14 exact retained source identities and unchanged fixed-population arithmetic."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest

from ros_esc.plotting_scripts import m4_pilot as metrics
from test_m4_v12_science import integrated_rows


VERSION = 'm4-pilot-v14'
SOURCE_VERSION = 'm4-pilot-v13'
BEFORE = Path('/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/'
    'm4_v14_source_v1/before/ros2_ws/src/ros_esc/ros_esc/plotting_scripts/m4_pilot.py')


def rows():
    # Independent old descriptors, not new headers retrofitted onto old rows.
    retained = integrated_rows(SOURCE_VERSION)[:4]
    fresh = integrated_rows(VERSION)[4:]
    result = retained + fresh
    for row in result:
        row['arrival_binding_method'] = metrics.RECORDED_ARRIVAL_BINDING
        row['method_version'] = metrics.experiment_method_version(row['experiment_version'])
    retained[0].update(arrival_passed=False, time_to_arrival_sec=None,
        combined_sequence_passed=False, behavior_passed=False)
    retained[0]['combined_sequence_components'].update(
        local_recovery_stage_passed=False, post_recovery_global_proximity_passed=False)
    return result


def test_retained_source_headers_and_a_failure_survive_new_comparison_envelope():
    data = rows(); before = deepcopy(data)
    result = metrics.aggregate_pilot(data, experiment_version=VERSION)
    assert result['experiment_version'] == VERSION
    assert result['method_version'] == 'recurrent_trapping_integrated_arrival_v14'
    assert result['slots'] == before and data == before
    assert [row['run_id'] for row in result['slots'][:4]] == [
        'm4-pilot-v13-slot01-A-26091141', 'm4-pilot-v13-slot02-B-26091141',
        'm4-pilot-v13-slot03-C-26091141', 'm4-pilot-v13-slot04-D-26091141']
    assert all(row['experiment_version'] == SOURCE_VERSION
               and row['method_version'] == 'recurrent_trapping_integrated_arrival_v13'
               for row in result['slots'][:4])
    assert result['primary_outcomes']['development']['arrival_counts'] == dict(
        observed_arrival=3, observed_nonarrival=1, unavailable=0)
    assert result['primary_outcomes']['development']['runs'][0]['local_recovery_passed'] is False
    assert result['slots'][0]['behavior_passed'] is False
    assert result['slots'][2]['mandatory_stop_evidence'] == before[2]['mandatory_stop_evidence']
    assert result['acquisition_population']['retained_development'] == dict(
        planned_slots=[1, 2, 3, 4], source_experiment_version=SOURCE_VERSION,
        source_run_ids=[row['run_id'] for row in before[:4]], complete_acquisition_count=4)
    assert result['acquisition_population']['fresh_confirmation'] == dict(
        planned_slots=list(range(5, 17)), source_experiment_version=VERSION,
        source_run_ids=[row['run_id'] for row in before[4:]], complete_acquisition_count=12)


def test_four_and_twelve_target_populations_stay_separate_with_censored_secondary():
    result = metrics.aggregate_pilot(rows(), experiment_version=VERSION)
    assert result['scientific_scope'] == 'integrated_arrival_direction_v1'
    assert result['secondary_endpoint'] == 'independent_basin_entry_latency'
    for population, count, targets in [('development', 4, 48), ('confirmation', 12, 144)]:
        actual = result['primary_outcomes'][population]
        assert actual['planned_run_count'] == count
        assert actual['direction']['counts']['scheduled'] == targets
    assert result['direction_scheduled_total'] == 192
    assert result['latency']['planned_pair_count'] == 6
    assert result['latency']['planned_endpoint_count'] == 12
    assert result['latency']['observed_pair_count'] == 0
    assert result['latency']['status'] == 'EVIDENCE_UNAVAILABLE'
    assert result['combined_method_confirmation']['status'] == 'PASS'
    assert [(c['slot'], c['condition']) for c in result['combined_method_confirmation']['conditions']] == [
        (8, 'nominal'), (12, 'noise'), (16, 'delay')]
    assert all(c['direction_summary']['counts']['scheduled'] == 24
               for c in result['combined_method_confirmation']['conditions'])


@pytest.mark.parametrize('index,key,value', [
    (0, 'experiment_version', VERSION),
    (0, 'run_id', 'm4-pilot-v14-slot01-A-26091141'),
    (1, 'seed', 26091151),
    (3, 'case_id', 'replacement_development_case'),
    (4, 'experiment_version', SOURCE_VERSION),
    (4, 'seed', 26091142),
    (15, 'run_id', 'm4-pilot-v13-slot16-D-26091144'),
])
def test_only_exact_declared_old_development_and_fresh_confirmation_identities_are_admitted(index, key, value):
    data = rows(); data[index][key] = value
    with pytest.raises(ValueError, match='different experiment'):
        metrics.aggregate_pilot(data, experiment_version=VERSION)


def test_duplicate_retained_acquisition_does_not_increase_population():
    data = rows()
    with pytest.raises(ValueError, match='repeated'):
        metrics.aggregate_pilot(data + [deepcopy(data[0])], experiment_version=VERSION)


def test_new_envelope_does_not_make_original_scientific_documents_v14():
    original = dict(version=metrics.VERSION, **metrics.experiment_fields(SOURCE_VERSION))
    assert metrics.validate_experiment_document(original, SOURCE_VERSION) == SOURCE_VERSION
    with pytest.raises(ValueError, match='different experiment/method'):
        metrics.validate_experiment_document(original, VERSION)
    assert original['method_version'] == 'recurrent_trapping_integrated_arrival_v13'


def test_retained_development_does_not_count_as_twelve_new_acquisitions():
    result = metrics.aggregate_pilot(rows()[:4], experiment_version=VERSION)
    assert result['acquisition_population']['retained_development']['complete_acquisition_count'] == 4
    assert result['acquisition_population']['fresh_confirmation']['complete_acquisition_count'] == 0
    assert result['slot_status_counts'] == {'COMPLETE': 4, 'UNSTARTED': 12}
    confirmation = result['primary_outcomes']['confirmation']
    assert confirmation['planned_run_count'] == 12
    assert confirmation['arrival_counts'] == dict(observed_arrival=0, observed_nonarrival=0, unavailable=12)
    assert confirmation['direction']['counts']['scheduled'] == 144
    assert result['combined_method_confirmation']['status'] == 'EVIDENCE_UNAVAILABLE'
    assert all(c['direction_summary']['counts']['scheduled'] == 24
               for c in result['combined_method_confirmation']['conditions'])


def test_missing_retained_row_is_not_fabricated_from_declared_source_identity():
    data = rows(); data.pop(0)
    result = metrics.aggregate_pilot(data, experiment_version=VERSION)
    assert result['slots'][0]['status'] == 'UNSTARTED'
    assert result['slots'][0]['run_id'] == 'm4-pilot-v13-slot01-A-26091141'
    assert result['acquisition_population']['retained_development']['complete_acquisition_count'] == 3
    assert result['primary_outcomes']['development']['arrival_counts']['unavailable'] == 1


@pytest.mark.parametrize('fault,expected', [('direction_failure', 'FAIL'), ('missing_motion', 'EVIDENCE_UNAVAILABLE')])
def test_one_d_condition_cannot_borrow_other_condition_measurements(fault, expected):
    data = rows()
    if fault == 'direction_failure':
        data[11]['direction_rows'][0]['actual_error_deg'] = 70.
    else:
        data[11]['mandatory_stop_evidence']['analysis_complete'] = False
    result = metrics.aggregate_pilot(data, experiment_version=VERSION)
    assert result['direction']['status'] == 'PASS'
    assert result['combined_method_confirmation']['status'] == expected
    assert [c['status'] for c in result['combined_method_confirmation']['conditions']] == ['PASS', expected, 'PASS']


@pytest.mark.parametrize('enabled_latency,extra_errors,missing,status', [
    (7., False, False, 'PASS'), (7.1, False, False, 'FAIL'),
    (7., True, False, 'FAIL'), (7., False, True, 'EVIDENCE_UNAVAILABLE'),
])
def test_original_six_pair_thirty_percent_and_error_guards_remain_unchanged(
        enabled_latency, extra_errors, missing, status):
    data = rows()
    # Hand-labelled fixture endpoints only; this is not an empirical onset claim.
    for row in data[4:]:
        row['latency'] = dict(observed=True, independently_eligible=True,
            latency_sec=10. if row['arm'] in ('A', 'C') else enabled_latency)
    if extra_errors:
        data[5]['wrong_fills'] = 1
    if missing:
        data[15]['latency']['independently_eligible'] = False
    result = metrics.aggregate_pilot(data, experiment_version=VERSION)['latency']
    assert result['planned_pair_count'] == 6 and result['planned_endpoint_count'] == 12
    assert result['status'] == status
    assert result['observed_pair_count'] == (5 if missing else 6)


@pytest.mark.parametrize('version', ['m4-pilot-v11', 'm4-pilot-v12', SOURCE_VERSION])
def test_full_historical_aggregate_matches_preserved_before_owner(version):
    spec = importlib.util.spec_from_file_location('m4_v14_metrics_before', BEFORE)
    old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
    data = integrated_rows(version)
    for row in data:
        row['arrival_binding_method'] = metrics.RECORDED_ARRIVAL_BINDING
    before = old.aggregate_pilot(data, experiment_version=version)
    assert metrics.aggregate_pilot(data, experiment_version=version) == before
    assert 'acquisition_population' not in before
    assert metrics.arrival_sequence_required_keys(version) == old.arrival_sequence_required_keys(version)
