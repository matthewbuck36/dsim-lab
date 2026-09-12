"""Prospective V10 science selection/completion; no bags, nodes or field models."""
from copy import deepcopy
import json

import pytest
from ros_esc.plotting_scripts import m4_pilot as metrics
from ros_esc.scenario_runner.m4_scenario import expected_slots, experiment_run_id
from ros_esc.plotting_scripts.v2_enclosure import atomic_exclusive_json
from test_m4_evaluation_cli import cli, bag, planned, Obj, stamp

VERSION = 'm4-pilot-v10'


def v10_plan(arm='D', *, experiment_version=VERSION):
    row = deepcopy(expected_slots(experiment_version)['ABCD'.index(arm)])
    row['run_id'] = experiment_run_id(row, experiment_version)
    row['resolved_scenario'] = {'algorithm': {'launch_overrides': {}},
        'success': {'criterion': 'post_recovery_arrival_v1'}}
    return row


def target_rows(run):
    return [dict(run_id=run['run_id'], arm=run['arm'], partition=run['partition'],
        condition=run['condition'], number=n, offset_sec=t, exposure_status='unexposed',
        input_qualified=False, reference_qualified=False, informative=False, eligible=False,
        usable_output=False, usable_averaging=False, actual_error_deg=None,
        paired_improvement_deg=None) for n,t in enumerate(metrics.TARGET_OFFSETS_SEC, 1)]


def test_new_method_identity_does_not_relabel_old_science():
    assert metrics.experiment_fields(VERSION) == dict(experiment_version=VERSION, method_version='recurrent_arrival_v10')
    assert metrics.experiment_fields('m4-pilot-v9')['method_version'] == metrics.VERSION
    assert metrics.experiment_fields(metrics.VERSION) == {}


@pytest.mark.parametrize('arm,extra', [('A', set()), ('B', {'recurrent_convergence_diagnostics',
    'stationary_recurrent_fill_requests'}), ('C', {'v2_verification_guidance'}),
    ('D', {'recurrent_convergence_diagnostics', 'v2_verification_guidance'})])
def test_selected_full_science_aliases_are_mandatory_only_for_v10(arm, extra):
    names = {'clock', 'algorithm_state', 'recording_ready', 'pose', 'command_final',
        'control_diagnostics', 'algorithm_events', 'gaussian_fills', 'timekeeper', *extra}
    entries = [{'alias': n, 'topic': '/'+n} for n in names]
    actual = metrics.science_aliases(entries, pose_topic='/pose', experiment_version=VERSION, arm=arm)
    assert set(actual) == names
    for missing in extra | {'command_final'}:
        reduced = [e for e in entries if e['alias'] != missing]
        with pytest.raises(ValueError, match='missing M4 science aliases'):
            metrics.science_aliases(reduced, pose_topic='/pose', experiment_version=VERSION, arm=arm)
        # Historical union intentionally does not require these new streams.
        metrics.science_aliases(reduced, pose_topic='/pose')


def test_recurrent_confirmation_uses_full_alias_and_support_endpoint(monkeypatch):
    marker = object()
    b = bag({'recurrent_convergence_diagnostics': [(78.1, marker)]})
    observed = []
    def evaluator(_scenario, _states, events, diagnostics, _time):
        observed.extend(diagnostics)
        return events, [dict(diagnostic_publication_stamp_ns=78_100_000_000,
            diagnostic_source_stamp_ns=78_008_000_000, diagnostic_history_end_ns=78_000_000_000)], None
    monkeypatch.setattr(cli.runner, '_centroid_convergence_evaluation_events', evaluator)
    values, _, audit, errors = cli._confirmation_inputs(b, v10_plan())
    assert not errors and observed[0][1] is marker
    assert values == [dict(decision_ns=78_100_000_000, source_ns=78_000_000_000)]
    assert audit[0]['diagnostic_source_stamp_ns'] == 78_008_000_000


def arrival_fixture():
    # Actual retained D03 evaluator sample. No retrospective verdict change.
    position = dict(x_m=3.7412288197111785, y_m=3.0636442732174594)
    distance = .49859569167329104
    pose = Obj(header=Obj(stamp=stamp(155.971)),
        pose=Obj(pose=Obj(position=Obj(x=position['x_m'], y=position['y_m']))))
    b = bag({'pose': [(156., pose)]})
    evidence = dict(position=position, distance_m=distance, sample_bag_stamp=156_000_000_000,
        proximity_radius_m=.5, interpolation_used=False)
    live = dict(position=position, distance_m=distance, sample_sim_sec=155.971,
        proximity_radius_m=.5, interpolation_used=False)
    acquired = dict(runner_result=dict(outcomes=dict(post_recovery_global_proximity_passed=True,
        post_recovery_global_proximity=evidence, controller_goal='failed',
        counted_candidate_ranked_goal_passed=False), record_process=dict(global_proximity_sample_live=live)))
    return acquired, b


def test_actual_arrival_is_measured_even_without_optional_goal_hold():
    acquired, b = arrival_fixture()
    result = cli._arrival_metrics(acquired, v10_plan(), b, 0)
    assert result['arrival_measurement_complete'] and result['arrival_passed']
    assert result['time_to_arrival_sec'] == pytest.approx(155.971)
    assert result['arrival_distance_m'] == .49859569167329104


@pytest.mark.parametrize('fault', ['missing_pose', 'changed_live_time', 'changed_live_position', 'wrong_criterion'])
def test_arrival_requires_exact_existing_evaluator_sample(fault):
    acquired, b = arrival_fixture(); plan = v10_plan()
    if fault == 'missing_pose': b = bag({'pose': []})
    elif fault == 'changed_live_time': acquired['runner_result']['record_process']['global_proximity_sample_live']['sample_sim_sec'] += .01
    elif fault == 'changed_live_position':
        acquired['runner_result']['record_process']['global_proximity_sample_live']['position'] = {'x_m': 3.5, 'y_m': 3.5}
    else: plan['resolved_scenario']['success']['criterion'] = 'unknown'
    assert cli._arrival_metrics(acquired, plan, b, 0)['arrival_measurement_complete'] is False


def test_valid_no_arrival_is_complete_censored_measurement_without_fabricated_time():
    acquired = dict(runner_result=dict(outcomes=dict(post_recovery_global_proximity_passed=False,
        post_recovery_global_proximity={'reason': 'Stage A did not complete'})))
    result = cli._arrival_metrics(acquired, v10_plan('A'), bag({}), 0)
    assert result['arrival_measurement_complete'] and result['arrival_passed'] is False
    assert result['time_to_arrival_sec'] is None


def test_actual_science_owner_accepts_complete_no_candidate_baseline(monkeypatch):
    plan = v10_plan('A')
    outcomes = dict(outcome_error=None, post_recovery_global_proximity_passed=False,
        post_recovery_global_proximity={'reason': 'Stage A did not complete'},
        local_recovery_stage_passed=False, fill_cardinality_passed=False,
        required_state_path_passed=False, escape_command_ownership_passed=False,
        required_events_passed=False, required_event_sequence_passed=False,
        forbidden_states_absent=True, forbidden_events_absent=True)
    acquired = dict(plan, status='COMPLETE', integrity_passed=True, runner_result={'outcomes': outcomes})
    pose = lambda t: Obj(header=Obj(stamp=stamp(t)), pose=Obj(pose=Obj(position=Obj(x=t,y=0.))))
    b = bag({'pose': [(1., pose(1.)), (1.1, pose(1.1))], 'algorithm_events': [],
        'algorithm_state': [], 'gaussian_fills': [], 'timekeeper': [(0., Obj(start_time=0., mode='sim time'))]})
    labels = dict(spatial_labels_precede_event_join=True, admission_ns=1_000_000_000,
        exposure_end_ns=1_100_000_000, labels=[], residence_intervals=[], pose_faults={},
        poses=[dict(stamp_ns=t, readiness_eligible=True) for t in (1_000_000_000,1_100_000_000)])
    monkeypatch.setattr(cli.metrics, 'analyze_labels', lambda *a, **k: deepcopy(labels))
    result, normalized = cli.analyze_run_data(acquired, plan, b, {}, {},
        freeze_labels=lambda value: {'path':'frozen-position-only','sha256':'receipt'}, experiment_version=VERSION)
    assert result['scientific_analysis_complete'], result['scientific_analysis_checks']
    assert normalized is None and result['combined_sequence_passed'] is False
    assert result['arrival_passed'] is False and result['time_to_arrival_sec'] is None
    assert result['latency']['observed'] is False
    assert result['wrong_fills'] == result['wrong_goals'] == result['negative_control_confirmations']['count'] == 0


def block_fixture(tmp_path, monkeypatch, *, references=True, experiment_version=VERSION, latencies=None):
    runs = [v10_plan(arm, experiment_version=experiment_version) for arm in 'ABCD']
    contract = dict(version=experiment_version, root=str(tmp_path), contract_path=str(tmp_path/'contract.json'), runs=runs)
    atomic_exclusive_json(tmp_path/'contract.json', contract)
    directory = tmp_path/'analysis/block_0'; directory.mkdir(parents=True)
    rows = []
    for plan in runs:
        slot = plan['slot']
        acquisition = tmp_path/'acquisition'/f'slot_{slot}.json'
        acquisition.parent.mkdir(exist_ok=True)
        atomic_exclusive_json(acquisition, dict(plan, status='COMPLETE', integrity_passed=True,
            runner_result={'classification': {'passed': False}}))
        label = directory/f'slot_{slot}_labels.json'
        atomic_exclusive_json(label, dict(version=metrics.VERSION, **metrics.experiment_fields(experiment_version),
            short_residences=[{'duration_sec': 7.}], spatial_labels_precede_event_join=True))
        row = dict(plan, status='COMPLETE', integrity_passed=True,
            acquisition_receipt=cli.receipt(acquisition), labels=cli.receipt(label), input_files=[],
            combined_sequence_passed=False, scientific_analysis_complete=True,
            scientific_analysis_checks={'complete_negative_attribution': True},
            latency={'observed': False, 'right_censored': True}, wrong_fills=0, wrong_goals=0)
        if latencies is not None:
            row['latency'] = deepcopy(latencies[plan['arm']])
        if plan['arm'] in 'CD':
            path = directory/f'slot_{slot}_normalized.json'
            atomic_exclusive_json(path, dict(version=metrics.VERSION, **metrics.experiment_fields(experiment_version), run_id=plan['run_id']))
            row['normalized_inputs'] = cli.receipt(path)
            if references:
                values = target_rows(row)
                atomic_exclusive_json(directory/f'slot_{slot}_references.json', dict(
                    version=metrics.VERSION, **metrics.experiment_fields(experiment_version),
                    slot=slot, run_id=row['run_id'], complete=True, integrity_passed=True,
                    direction_analysis_complete=True, normalized_inputs=row['normalized_inputs'],
                    contract=cli.receipt(contract['contract_path']), rows=values,
                    summary=metrics.summarize_direction(values), supplemental={}))
        rows.append(row)
    atomic_exclusive_json(directory/'labels.json', dict(version=metrics.VERSION,
        **metrics.experiment_fields(experiment_version), block=0, complete=True, integrity_passed=True,
        contract=cli.receipt(contract['contract_path']), input_files=[r['acquisition_receipt'] for r in rows], runs=rows))
    monkeypatch.setattr(cli, 'verify_frozen', lambda *a, **k: None)
    monkeypatch.setattr(cli, 'read_run_bag', lambda *a, **k: pytest.fail('summary decoded a bag'))
    return contract, directory, rows


def test_complete_failed_baselines_and_censored_references_are_complete_science(tmp_path, monkeypatch):
    contract, directory, rows = block_fixture(tmp_path, monkeypatch)
    result = cli.summary_stage(contract, 0)
    assert result['scientific_analysis_complete'] is True
    assert len(result['references']) == 2 and result['contract'] == cli.receipt(contract['contract_path'])
    assert all(r['combined_sequence_passed'] is False for r in result['runs'])


def test_missing_both_reference_products_never_means_complete_v10_science(tmp_path, monkeypatch):
    contract, _, _ = block_fixture(tmp_path, monkeypatch, references=False)
    result = cli.summary_stage(contract, 0)
    assert result['complete'] is True and result['integrity_passed'] is True
    assert result['scientific_analysis_complete'] is False
    assert not result['scientific_analysis_checks']['both_reference_products_complete']


def test_changed_nested_label_is_rejected_before_summary_publication(tmp_path, monkeypatch):
    contract, directory, rows = block_fixture(tmp_path, monkeypatch)
    from pathlib import Path
    Path(rows[0]['labels']['path']).write_text('{}')
    with pytest.raises(ValueError, match='retained input changed'):
        cli.summary_stage(contract, 0)
    assert not (directory/'result.json').exists()


@pytest.mark.parametrize('fault', ['missing', 'identity', 'invalid_input', 'reference_failure'])
def test_direction_product_requires_all_frozen_targets_and_valid_reference_computation(fault):
    run = v10_plan(); rows = target_rows(run)
    if fault == 'missing': rows.pop()
    elif fault == 'identity': rows[0]['run_id'] = 'other'
    elif fault == 'invalid_input': rows[0]['exposure_status'] = 'invalid_input'
    else: rows[0].update(exposure_status='observed', input_qualified=True, reference_qualified=False)
    assert metrics.direction_product_complete(rows, run) is False
