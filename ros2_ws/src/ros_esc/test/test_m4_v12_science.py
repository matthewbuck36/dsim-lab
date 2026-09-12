"""Prospective V12 reporting/sequence scope through existing science owners."""
from copy import deepcopy

import pytest

from ros_esc.plotting_scripts import m4_pilot as metrics
from ros_esc.scenario_runner.m4_scenario import expected_slots, experiment_run_id
from test_m4_evaluation_cli import Obj, bag, cli, stamp
from test_m4_v10_science import arrival_fixture, block_fixture, target_rows, v10_plan


VERSION = 'm4-pilot-v12'


def integrated_rows(version=VERSION):
    """Fixed selected identities with censored secondary latency and one target/run."""
    rows = []
    for planned in expected_slots(version):
        row = dict(planned, run_id=experiment_run_id(planned, version),
            status='COMPLETE', integrity_passed=True, scientific_analysis_complete=True,
            arrival_measurement_complete=True, arrival_passed=True, time_to_arrival_sec=200.,
            combined_sequence_passed=True,
            combined_sequence_components={key: key != 'required_state_path_passed'
                                          for key in metrics.ARRIVAL_SEQUENCE_KEYS},
            latency=dict(observed=False, independently_eligible=False, right_censored=True,
                         latency_sec=None, reason='unchanged first-opportunity residence unavailable'),
            wrong_fills=0, wrong_goals=0)
        if row['arm'] in ('C', 'D'):
            row.update(direction_analysis_complete=True, direction_rows=target_rows(row),
                mandatory_stopped_acquisitions=0,
                mandatory_stop_evidence=dict(status='OBSERVED_CONTINUOUS_ACQUISITION',
                    analysis_complete=True, authority_complete=True, command_pairing_complete=True))
            row['direction_rows'][0].update(exposure_status='observed', input_qualified=True,
                reference_qualified=True, informative=True, eligible=True, usable_output=True,
                usable_averaging=True, actual_error_deg=10., paired_improvement_deg=2.)
        rows.append(row)
    return rows


def test_v12_primary_population_keeps_failed_unavailable_and_development_separate():
    rows = integrated_rows()
    # Confirmation A has an observed failure, B an unavailable arrival, C no acquisition.
    rows[4].update(arrival_passed=False, time_to_arrival_sec=None, combined_sequence_passed=False)
    rows[5].update(arrival_measurement_complete=False, arrival_passed=None, time_to_arrival_sec=None)
    rows[6]['mandatory_stop_evidence'].update(status='NO_ACQUISITION_OBSERVED')
    rows[6]['mandatory_stopped_acquisitions'] = None
    before = deepcopy(rows)
    result = metrics.aggregate_pilot(rows, experiment_version=VERSION)
    assert result['version'] == 'm4-pilot-v1'
    assert result['method_version'] == 'recurrent_integrated_arrival_v12'
    assert result['scientific_scope'] == 'integrated_arrival_direction_v1'
    assert result['secondary_endpoint'] == 'independent_basin_entry_latency'
    development, confirmation = (result['primary_outcomes'][name]
                                 for name in ('development', 'confirmation'))
    assert development['planned_run_count'] == 4
    assert development['arrival_counts'] == dict(observed_arrival=4, observed_nonarrival=0, unavailable=0)
    assert development['direction']['counts']['scheduled'] == 48
    assert confirmation['planned_run_count'] == 12
    assert confirmation['arrival_counts'] == dict(observed_arrival=10, observed_nonarrival=1, unavailable=1)
    assert confirmation['direction']['counts']['scheduled'] == 144
    assert confirmation['direction']['counts']['eligible_informative'] == 6
    assert confirmation['direction']['counts']['usable_averaging'] == 6
    assert confirmation['acquisition_status_counts'] == {
        'OBSERVED_CONTINUOUS_ACQUISITION': 5, 'NO_ACQUISITION_OBSERVED': 1}
    for arm in confirmation['by_arm']:
        assert arm['planned_run_count'] == 3
        assert arm['direction']['counts']['scheduled'] == (72 if arm['arm'] in 'CD' else 0)
        if arm['arm'] in 'AB':
            assert arm['direction']['status'] == 'NOT_APPLICABLE'
            assert arm['acquisition_status_counts'] == {}
    assert confirmation['runs'][0]['time_to_arrival_sec'] is None
    assert confirmation['runs'][1]['arrival_status'] == 'EVIDENCE_UNAVAILABLE'
    assert confirmation['runs'][0]['first_verification_path_passed'] is False
    assert result['latency']['status'] == 'EVIDENCE_UNAVAILABLE'
    assert result['latency']['observed_pair_count'] == 0
    assert result['latency']['planned_pair_count'] == 6
    assert rows == before


def test_v12_unstarted_confirmation_remains_twelve_unknown_runs_and_144_targets():
    result = metrics.aggregate_pilot(integrated_rows()[:4], experiment_version=VERSION)
    confirmation = result['primary_outcomes']['confirmation']
    assert confirmation['planned_run_count'] == 12
    assert confirmation['scientific_complete_run_count'] == 0
    assert confirmation['arrival_counts'] == dict(observed_arrival=0, observed_nonarrival=0, unavailable=12)
    assert confirmation['direction']['counts']['scheduled'] == 144
    assert confirmation['direction']['status'] == 'EVIDENCE_UNAVAILABLE'
    assert confirmation['acquisition_status_counts'] == {'EVIDENCE_UNAVAILABLE': 6}


@pytest.mark.parametrize('fault', ['integrity', 'missing_reference', 'missing_target', 'missing_arrival_time'])
def test_v12_primary_projection_cannot_make_incomplete_inputs_positive(fault):
    rows = integrated_rows(); row = rows[6]
    if fault == 'integrity': row['integrity_passed'] = False
    elif fault == 'missing_reference': row['direction_analysis_complete'] = False
    elif fault == 'missing_target': row['direction_rows'].pop()
    else: row['time_to_arrival_sec'] = None
    result = metrics.aggregate_pilot(rows, experiment_version=VERSION)['primary_outcomes']['confirmation']
    if fault in ('integrity', 'missing_arrival_time'):
        assert result['runs'][2]['arrival_status'] == 'EVIDENCE_UNAVAILABLE'
    if fault != 'missing_arrival_time':
        assert result['direction']['status'] == 'EVIDENCE_UNAVAILABLE'
    assert result['direction']['counts']['scheduled'] == 144


@pytest.mark.parametrize('version', ['m4-pilot-v10', 'm4-pilot-v11'])
def test_v12_scope_does_not_change_historical_aggregate_or_latency_fields(version):
    previous = metrics.aggregate_pilot(integrated_rows(version), experiment_version=version)
    current = metrics.aggregate_pilot(integrated_rows(), experiment_version=VERSION)
    assert 'scientific_scope' not in previous and 'primary_outcomes' not in previous
    assert 'secondary_endpoint' not in previous
    assert current['latency'] == previous['latency']
    assert current['direction'] == previous['direction']
    assert metrics.arrival_sequence_required_keys(version) == metrics.ARRIVAL_SEQUENCE_KEYS


@pytest.mark.parametrize('arm,extra', [('A', set()), ('B', {'recurrent_convergence_diagnostics',
    'stationary_recurrent_fill_requests'}), ('C', {'v2_verification_guidance'}),
    ('D', {'recurrent_convergence_diagnostics', 'v2_verification_guidance'})])
def test_v12_selected_science_aliases_retain_current_authority_and_motion(arm, extra):
    names = {'clock', 'algorithm_state', 'recording_ready', 'pose', 'command_final',
             'control_diagnostics', 'algorithm_events', 'gaussian_fills', 'timekeeper', *extra}
    entries = [{'alias': name, 'topic': '/'+name} for name in names]
    assert set(metrics.science_aliases(entries, pose_topic='/pose', experiment_version=VERSION, arm=arm)) == names
    with pytest.raises(ValueError, match='missing M4 science aliases'):
        metrics.science_aliases([row for row in entries if row['alias'] != 'command_final'],
                               pose_topic='/pose', experiment_version=VERSION, arm=arm)


def sequence_projection(monkeypatch, version, fault=None):
    """Exercise actual analysis projection and retained arrival sample, without bag/model work."""
    plan = v10_plan('A', experiment_version=version)
    acquired, actual = arrival_fixture()
    outcomes = acquired['runner_result']['outcomes']
    outcomes.update({key: key != 'required_state_path_passed' for key in metrics.ARRIVAL_SEQUENCE_KEYS})
    outcomes['outcome_error'] = None
    if fault is not None:
        outcomes[fault] = False
    acquired.update(plan, status='COMPLETE', integrity_passed=True)
    retained = actual.records_by_topic[actual.topics_by_alias['pose']['topic']][0].message
    preceding = deepcopy(retained); preceding.header.stamp = stamp(155.871)
    preceding.pose.pose.position.x -= .01
    actual = bag({'pose': [(155.9, preceding), (156., retained)], 'algorithm_events': [],
        'algorithm_state': [], 'gaussian_fills': [], 'timekeeper': [(0., Obj(start_time=0., mode='sim time'))]})
    labels = dict(spatial_labels_precede_event_join=True, admission_ns=155_871_000_000,
        exposure_end_ns=155_971_000_000, labels=[], residence_intervals=[], pose_faults={},
        poses=[dict(stamp_ns=t, readiness_eligible=True) for t in (155_871_000_000,155_971_000_000)])
    monkeypatch.setattr(cli.metrics, 'analyze_labels', lambda *a, **k: deepcopy(labels))
    result, normalized = cli.analyze_run_data(acquired, plan, actual, {}, {},
        freeze_labels=lambda value: {'path':'frozen-position-only','sha256':'receipt'}, experiment_version=version)
    assert normalized is None
    return result


def test_v12_actual_science_accepts_later_recovery_and_retains_first_path_failure(monkeypatch):
    result = sequence_projection(monkeypatch, VERSION)
    assert result['combined_sequence_passed'] is True
    assert result['combined_sequence_components']['required_state_path_passed'] is False
    assert result['combined_sequence_required_keys'] == list(metrics.arrival_sequence_required_keys(VERSION))
    assert result['combined_sequence_diagnostic_keys'] == ['required_state_path_passed']
    assert len(result['combined_sequence_required_keys']) == 8
    assert result['arrival_passed'] and result['arrival_measurement_complete']
    assert result['time_to_arrival_sec'] == pytest.approx(155.971)
    assert result['optional_controller_goal']['ranked_goal_passed'] is False
    historical = sequence_projection(monkeypatch, 'm4-pilot-v11')
    assert historical['combined_sequence_passed'] is False
    assert 'combined_sequence_required_keys' not in historical


@pytest.mark.parametrize('fault', [key for key in metrics.ARRIVAL_SEQUENCE_KEYS if key != 'required_state_path_passed'])
def test_v12_keeps_every_other_combined_recovery_component_mandatory(monkeypatch, fault):
    result = sequence_projection(monkeypatch, VERSION, fault)
    assert result['combined_sequence_passed'] is False
    assert result['combined_sequence_components'][fault] is False


def test_v12_summary_scopes_complete_censored_science_without_v11_latency_feasibility(tmp_path, monkeypatch):
    contract, _, _ = block_fixture(tmp_path, monkeypatch, experiment_version=VERSION)
    result = cli.summary_stage(contract, 0)
    assert result['scientific_analysis_complete'] is True
    assert set(result['scientific_analysis_checks']) == {'four_arm_analysis_complete', 'both_reference_products_complete'}
    assert result['scientific_scope'] == 'integrated_arrival_direction_v1'
    assert result['secondary_endpoint'] == 'independent_basin_entry_latency'
    assert 'development_latency_feasibility' not in result
    assert result['method_version'] == 'recurrent_integrated_arrival_v12'
    with pytest.raises(ValueError, match='only for M4 v11'):
        metrics.development_latency_feasibility(result['runs'], experiment_version=VERSION)


def test_v12_summary_still_requires_both_reference_products(tmp_path, monkeypatch):
    contract, _, _ = block_fixture(tmp_path, monkeypatch, experiment_version=VERSION, references=False)
    result = cli.summary_stage(contract, 0)
    assert not result['scientific_analysis_complete']
    assert not result['scientific_analysis_checks']['both_reference_products_complete']


def test_v12_summary_retains_late_nested_receipt_check(tmp_path, monkeypatch):
    from pathlib import Path
    contract, directory, rows = block_fixture(tmp_path, monkeypatch, experiment_version=VERSION)
    Path(rows[0]['labels']['path']).write_text('{}')
    with pytest.raises(ValueError, match='retained input changed'):
        cli.summary_stage(contract, 0)
    assert not (directory/'result.json').exists()
