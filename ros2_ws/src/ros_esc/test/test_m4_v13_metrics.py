"""V13 fixed populations and condition-specific package claims; no field model."""
from copy import deepcopy
import importlib.util
from pathlib import Path

import pytest

from ros_esc.plotting_scripts import m4_pilot as metrics
from test_m4_v12_science import integrated_rows
from test_m4_v10_science import block_fixture, target_rows
from test_m4_evaluation_cli import cli


VERSION = 'm4-pilot-v13'
BEFORE = Path('/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/'
              'm4_v13_source_v1/before/ros2_ws/src/ros_esc/ros_esc/plotting_scripts/m4_pilot.py')


def v13_rows():
    rows = integrated_rows(VERSION)
    for row in rows:
        row['arrival_binding_method'] = metrics.RECORDED_ARRIVAL_BINDING
    return rows


def test_fixed_population_and_independent_secondary_are_preserved():
    rows = v13_rows(); original = deepcopy(rows)
    result = metrics.aggregate_pilot(rows, experiment_version=VERSION)
    assert result['method_version'] == 'recurrent_trapping_integrated_arrival_v13'
    assert result['scientific_scope'] == 'integrated_arrival_direction_v1'
    assert result['secondary_endpoint'] == 'independent_basin_entry_latency'
    assert result['primary_outcomes']['development']['planned_run_count'] == 4
    assert result['primary_outcomes']['development']['direction']['counts']['scheduled'] == 48
    assert result['primary_outcomes']['confirmation']['planned_run_count'] == 12
    assert result['primary_outcomes']['confirmation']['direction']['counts']['scheduled'] == 144
    assert result['direction_scheduled_total'] == 192
    assert result['latency']['status'] == 'EVIDENCE_UNAVAILABLE'
    assert result['latency']['planned_pair_count'] == 6
    assert result['latency']['observed_pair_count'] == 0
    combined = result['combined_method_confirmation']
    assert combined['status'] == 'PASS' and combined['planned_condition_count'] == 3
    assert [(row['slot'], row['condition']) for row in combined['conditions']] == [
        (8, 'nominal'), (12, 'noise'), (16, 'delay')]
    assert all(row['direction_summary']['counts']['scheduled'] == 24 for row in combined['conditions'])
    assert rows == original


def test_one_failed_d_condition_cannot_be_hidden_by_pooled_direction():
    rows = v13_rows()
    rows[11]['direction_rows'][0]['actual_error_deg'] = 70.
    result = metrics.aggregate_pilot(rows, experiment_version=VERSION)
    assert result['direction']['status'] == 'PASS'
    assert result['combined_method_confirmation']['status'] == 'FAIL'
    assert [row['status'] for row in result['combined_method_confirmation']['conditions']] == ['PASS', 'FAIL', 'PASS']
    assert result['combined_method_confirmation']['conditions'][1]['direction_passed'] is False


def test_complete_c_failure_remains_comparator_evidence_not_d_rejection():
    rows = v13_rows()
    for row in rows:
        if row['arm'] == 'C':
            row.update(arrival_passed=False, time_to_arrival_sec=None, combined_sequence_passed=False)
            row['direction_rows'][0]['actual_error_deg'] = 120.
    result = metrics.aggregate_pilot(rows, experiment_version=VERSION)
    assert result['direction']['status'] == 'FAIL'
    assert result['combined_method_confirmation']['status'] == 'PASS'
    comparator = next(row for row in result['primary_outcomes']['confirmation']['by_arm'] if row['arm'] == 'C')
    assert comparator['arrival_counts'] == dict(observed_arrival=0, observed_nonarrival=3, unavailable=0)
    assert comparator['direction']['counts']['scheduled'] == 72
    assert comparator['direction']['status'] == 'FAIL'


@pytest.mark.parametrize('fault', ['integrity', 'science', 'arrival_binding', 'arrival_time',
    'reference', 'target', 'empty_eligible', 'pairing', 'authority', 'stop_unknown'])
def test_missing_condition_measurement_is_unavailable(fault):
    row = v13_rows()[11]
    if fault == 'integrity': row['integrity_passed'] = False
    elif fault == 'science': row['scientific_analysis_complete'] = False
    elif fault == 'arrival_binding': row.pop('arrival_binding_method')
    elif fault == 'arrival_time': row['time_to_arrival_sec'] = None
    elif fault == 'reference': row['direction_analysis_complete'] = False
    elif fault == 'target': row['direction_rows'].pop()
    elif fault == 'empty_eligible': row['direction_rows'] = target_rows(row)
    elif fault == 'pairing': row['mandatory_stop_evidence']['command_pairing_complete'] = False
    elif fault == 'authority': row['mandatory_stop_evidence']['authority_complete'] = False
    elif fault == 'stop_unknown': row['mandatory_stopped_acquisitions'] = None
    else: raise AssertionError(fault)
    assert metrics.integrated_method_run_checks(row)['status'] == 'EVIDENCE_UNAVAILABLE'


@pytest.mark.parametrize('fault', ['nonarrival', 'recovery', 'stopped', 'no_acquisition', 'direction', 'averaging'])
def test_measured_condition_failure_is_not_relabelled_unavailable(fault):
    row = v13_rows()[11]
    if fault == 'nonarrival': row.update(arrival_passed=False, time_to_arrival_sec=None)
    elif fault == 'recovery': row['combined_sequence_passed'] = False
    elif fault == 'stopped': row['mandatory_stopped_acquisitions'] = 1
    elif fault == 'no_acquisition':
        row['mandatory_stop_evidence']['status'] = 'NO_ACQUISITION_OBSERVED'
        row['mandatory_stopped_acquisitions'] = None
    elif fault == 'direction': row['direction_rows'][0]['actual_error_deg'] = 31.
    elif fault == 'averaging': row['direction_rows'][0]['usable_averaging'] = False
    else: raise AssertionError(fault)
    assert metrics.integrated_method_run_checks(row)['status'] == 'FAIL'


def test_unstarted_delay_keeps_twelve_confirmation_slots_and_all_targets():
    result = metrics.aggregate_pilot(v13_rows()[:12], experiment_version=VERSION)
    assert result['primary_outcomes']['confirmation']['planned_run_count'] == 12
    assert result['primary_outcomes']['confirmation']['direction']['counts']['scheduled'] == 144
    combined = result['combined_method_confirmation']
    assert combined['status'] == 'EVIDENCE_UNAVAILABLE'
    assert combined['conditions'][2]['slot'] == 16
    assert combined['conditions'][2]['arrival_passed'] is None
    assert combined['conditions'][2]['direction_passed'] is None
    assert combined['conditions'][2]['direction_summary']['counts']['scheduled'] == 24


@pytest.mark.parametrize('version', ['m4-pilot-v11', 'm4-pilot-v12'])
def test_historical_full_aggregate_matches_preserved_before_owner(version):
    spec = importlib.util.spec_from_file_location('m4_v13_metrics_before', BEFORE)
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    rows = integrated_rows(version)
    assert metrics.aggregate_pilot(rows, experiment_version=version) == old.aggregate_pilot(rows, experiment_version=version)
    assert metrics.arrival_sequence_required_keys(version) == old.arrival_sequence_required_keys(version)


def test_v13_complete_summary_preserves_scope_and_no_onset_claim(tmp_path, monkeypatch):
    contract, _, _ = block_fixture(tmp_path, monkeypatch, experiment_version=VERSION)
    result = cli.summary_stage(contract, 0)
    assert result['scientific_analysis_complete'] is True
    assert result['scientific_scope'] == 'integrated_arrival_direction_v1'
    assert result['secondary_endpoint'] == 'independent_basin_entry_latency'
    assert 'development_latency_feasibility' not in result
    assert len(result['references']) == 2
    assert all(len(row['direction_rows']) == 24 for row in result['runs'] if row['arm'] in ('C', 'D'))


def test_v13_missing_reference_keeps_science_incomplete(tmp_path, monkeypatch):
    contract, _, _ = block_fixture(tmp_path, monkeypatch, experiment_version=VERSION, references=False)
    result = cli.summary_stage(contract, 0)
    assert result['scientific_analysis_complete'] is False
    assert result['scientific_analysis_checks']['both_reference_products_complete'] is False
