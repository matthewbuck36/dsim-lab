"""V11 science registration and first-opportunity feasibility; no bag/model jobs."""
from copy import deepcopy
from pathlib import Path

import pytest

from ros_esc.plotting_scripts import m4_pilot as metrics
from test_m4_evaluation_cli import bag, cli
from test_m4_pilot_metrics import bag_fixture, geometry
from test_m4_v10_science import arrival_fixture, block_fixture, v10_plan


VERSION = 'm4-pilot-v11'


def first_opportunity_latency(*, decision_sec=18., fault=None):
    """Use the unchanged position-label and first-opportunity owners."""
    labels = metrics.analyze_labels(bag_fixture(), geometry(), pose_topic='/odom')
    kwargs = dict(confirmation_stamps_ns=[round(decision_sec*metrics.NS)],
                  intervention_evidence_complete=True)
    if fault == 'short_first':
        labels['residence_intervals'].insert(0, dict(source_id='local', start_ns=1_500_000_000,
            end_ns=1_750_000_000, duration_sec=.25, kind='positive_basin_residence'))
    elif fault == 'left':
        kwargs['admission_ns'] = 3*metrics.NS
    elif fault == 'intervention':
        kwargs['intervention_ns'] = 10*metrics.NS
    elif fault == 'no_confirmation':
        kwargs['confirmation_stamps_ns'] = []
    elif fault == 'source_guard':
        labels['poses'][30]['qualified'] = False
    elif fault == 'attribution':
        kwargs['intervention_evidence_complete'] = False
    elif fault is not None:
        raise ValueError('unknown fixture fault')
    return metrics.join_first_opportunity(labels, **kwargs)


def development_rows():
    return [dict(v10_plan(arm, experiment_version=VERSION), status='COMPLETE',
                 integrity_passed=True, combined_sequence_passed=False,
                 latency=first_opportunity_latency(decision_sec=18. if arm in 'AC' else 20.))
            for arm in 'ABCD']


def test_v11_method_identity_keeps_historical_scientific_format_and_v10_fields():
    fields = metrics.experiment_fields(VERSION)
    assert fields == dict(experiment_version=VERSION, method_version='recurrent_arrival_v11')
    document = dict(version=metrics.VERSION, **fields)
    assert document['version'] == 'm4-pilot-v1'
    assert metrics.validate_experiment_document(document, VERSION) == VERSION
    with pytest.raises(ValueError, match='different experiment/method'):
        metrics.validate_experiment_document(document, metrics.ARRIVAL_VERSION)
    assert metrics.experiment_fields(metrics.ARRIVAL_VERSION) == dict(
        experiment_version='m4-pilot-v10', method_version='recurrent_arrival_v10')
    assert metrics.experiment_fields('m4-pilot-v9')['method_version'] == 'm4-pilot-v1'


@pytest.mark.parametrize('arm,extra', [('A', set()), ('B', {'recurrent_convergence_diagnostics',
    'stationary_recurrent_fill_requests'}), ('C', {'v2_verification_guidance'}),
    ('D', {'recurrent_convergence_diagnostics', 'v2_verification_guidance'})])
def test_v11_requires_full_selected_science_streams(arm, extra):
    names = {'clock', 'algorithm_state', 'recording_ready', 'pose', 'command_final',
             'control_diagnostics', 'algorithm_events', 'gaussian_fills', 'timekeeper', *extra}
    entries = [{'alias': name, 'topic': '/'+name} for name in names]
    assert set(metrics.science_aliases(entries, pose_topic='/pose', experiment_version=VERSION, arm=arm)) == names
    for missing in extra | {'command_final'}:
        with pytest.raises(ValueError, match='missing M4 science aliases'):
            metrics.science_aliases([row for row in entries if row['alias'] != missing],
                pose_topic='/pose', experiment_version=VERSION, arm=arm)


def test_v11_recurrent_input_retains_support_endpoint_and_arrival_owner(monkeypatch):
    marker = object()
    seen = []
    def joined(_scenario, _states, events, diagnostics, _origins):
        seen.extend(diagnostics)
        return events, [dict(diagnostic_publication_stamp_ns=78_100_000_000,
            diagnostic_source_stamp_ns=78_008_000_000, diagnostic_history_end_ns=78_000_000_000)], None
    monkeypatch.setattr(cli.runner, '_centroid_convergence_evaluation_events', joined)
    planned = v10_plan(experiment_version=VERSION)
    confirmations, _, audit, errors = cli._confirmation_inputs(
        bag({'recurrent_convergence_diagnostics': [(78.1, marker)]}), planned)
    assert seen[0][1] is marker and not errors
    assert confirmations == [dict(decision_ns=78_100_000_000, source_ns=78_000_000_000)]
    assert audit[0]['diagnostic_source_stamp_ns'] == 78_008_000_000
    acquired, actual = arrival_fixture()
    value = cli._arrival_metrics(acquired, planned, actual, 0)
    assert value['arrival_passed'] and value['arrival_measurement_complete']
    assert value['time_to_arrival_sec'] == pytest.approx(155.971)


def test_v11_direction_products_keep_all_24_unexposed_targets_and_current_identity():
    planned = v10_plan('C', experiment_version=VERSION)
    normalized = metrics.normalize_direction_targets([], dict(origin_ns=0, qualified=True,
        integrity_errors=[]), **{key: planned[key] for key in ('run_id', 'arm', 'partition', 'condition')},
        exposure_end_ns=0, experiment_version=VERSION)
    completed = []
    result = metrics.evaluate_direction_targets(normalized,
        raw_owner=lambda *args: pytest.fail('unexposed target requested numerical evaluation'),
        binding={}, sources=[], on_result=lambda value: completed.append(value['number']))
    assert completed == list(range(1, 25))
    assert all(row['exposure_status'] == 'unexposed' for row in result['rows'])
    assert metrics.validate_experiment_document(normalized, VERSION) == VERSION
    assert metrics.validate_experiment_document(result, VERSION) == VERSION
    assert result['summary']['counts']['eligible_informative'] == 0


def test_both_development_pairs_are_feasible_without_any_improvement_or_behavior_pass():
    rows = development_rows()
    before = deepcopy(rows)
    result = metrics.development_latency_feasibility(rows, experiment_version=VERSION)
    assert result['feasible'] and result['observed_pair_count'] == 2
    assert result['observed_endpoint_count'] == 4 and result['reason'] is None
    assert all(pair['enabled']['latency_sec'] > pair['control']['latency_sec'] for pair in result['pairs'])
    assert rows == before and all(row['combined_sequence_passed'] is False for row in rows)


@pytest.mark.parametrize('fault', ['short_first', 'left', 'intervention', 'no_confirmation', 'source_guard', 'attribution'])
def test_ineligible_first_opportunity_withholds_pair_without_replacing_endpoint(fault):
    rows = development_rows()
    rows[1]['latency'] = first_opportunity_latency(fault=fault)
    result = metrics.development_latency_feasibility(rows, experiment_version=VERSION)
    assert not result['feasible'] and result['observed_pair_count'] == 1
    assert 'A/B' in result['reason'] and result['observed_endpoint_count'] == 3
    assert result['pairs'][0]['enabled'] == rows[1]['latency']
    if fault == 'short_first':
        assert rows[1]['latency']['later_opportunity_count'] == 1
        assert rows[1]['latency']['first_opportunity']['duration_sec'] == .25


@pytest.mark.parametrize('fault', ['missing', 'order', 'other_version', 'wrong_seed'])
def test_feasibility_accepts_only_the_exact_v11_development_population(fault):
    rows = development_rows()
    version = VERSION
    if fault == 'missing': rows.pop()
    elif fault == 'order': rows.reverse()
    elif fault == 'other_version': version = metrics.ARRIVAL_VERSION
    else: rows[0]['seed'] += 1
    with pytest.raises(ValueError, match='development latency feasibility'):
        metrics.development_latency_feasibility(rows, experiment_version=version)


@pytest.mark.parametrize('observed', [False, True])
def test_v11_summary_keeps_feasibility_separate_from_complete_censored_science(tmp_path, monkeypatch, observed):
    latencies = {row['arm']: row['latency'] for row in development_rows()} if observed else None
    contract, _, rows = block_fixture(tmp_path, monkeypatch, experiment_version=VERSION, latencies=latencies)
    result = cli.summary_stage(contract, 0)
    assert result['scientific_analysis_complete'] is True
    assert set(result['scientific_analysis_checks']) == {'four_arm_analysis_complete', 'both_reference_products_complete'}
    assert len(result['references']) == 2 and len(result['runs'][2]['direction_rows']) == 24
    assert result['development_latency_feasibility'] == metrics.development_latency_feasibility(
        rows, experiment_version=VERSION)
    assert result['development_latency_feasibility']['feasible'] is observed
    assert result['method_version'] == 'recurrent_arrival_v11'


def test_v11_summary_missing_references_remains_incomplete_despite_feasible_latency(tmp_path, monkeypatch):
    latencies = {row['arm']: row['latency'] for row in development_rows()}
    contract, _, _ = block_fixture(tmp_path, monkeypatch, experiment_version=VERSION,
                                   latencies=latencies, references=False)
    result = cli.summary_stage(contract, 0)
    assert result['development_latency_feasibility']['feasible']
    assert not result['scientific_analysis_complete']


def test_v11_summary_rechecks_nested_label_before_publication(tmp_path, monkeypatch):
    contract, directory, rows = block_fixture(tmp_path, monkeypatch, experiment_version=VERSION)
    Path(rows[0]['labels']['path']).write_text('{}')
    with pytest.raises(ValueError, match='retained input changed'):
        cli.summary_stage(contract, 0)
    assert not (directory/'result.json').exists()


def test_v10_summary_has_no_v11_feasibility_field(tmp_path, monkeypatch):
    contract, _, _ = block_fixture(tmp_path, monkeypatch)
    result = cli.summary_stage(contract, 0)
    assert result['scientific_analysis_complete']
    assert 'development_latency_feasibility' not in result
