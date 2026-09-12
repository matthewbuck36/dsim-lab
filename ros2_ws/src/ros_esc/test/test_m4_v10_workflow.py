"""V10 real workflow/schema and immutable release joins, with no scientific jobs.

Only topology calculation, environment discovery and child execution are
replaced. Tests use temporary files; no retained experiment or bag is opened.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

from ros_esc.plotting_scripts import q1_study
from ros_esc.scenario_runner import aggregate_field_truth as truth
from ros_esc.scenario_runner import m4_scenario as scenario
from ros_esc.scenario_runner import run_scenario as runner
from test_m4_workflow import acquisition, save, workflow
from test_m4_v5_versions import synthetic_topology
import m4_science_job

VERSION = 'm4-pilot-v10'
FIELDS = dict(version='m4-pilot-v1', experiment_version=VERSION,
              method_version='recurrent_arrival_v10')
ROW_CHECKS = ('acquisition_complete', 'position_labels_complete',
    'confirmation_attribution_complete', 'selected_authority_complete',
    'error_attribution_complete', 'arrival_measurement_complete',
    'path_length_complete', 'motion_measurement_complete', 'direction_inputs_complete')
SEQUENCE_KEYS = ('local_recovery_stage_passed', 'fill_cardinality_passed',
    'required_state_path_passed', 'escape_command_ownership_passed',
    'required_events_passed', 'required_event_sequence_passed',
    'forbidden_states_absent', 'forbidden_events_absent',
    'post_recovery_global_proximity_passed')


def unavailable(*args, **kwargs):
    pytest.fail('workflow fixture must not launch processes or numerical models')


@pytest.fixture(scope='module')
def preparation(tmp_path_factory):
    directory = tmp_path_factory.mktemp('m4_v10_workflow')
    marker = save(directory / 'source.json', {'fixture': 'immutable source'})
    sources = [marker, workflow.receipt(runner.GESC_CONTROLLER),
               workflow.receipt(scenario.v6_controller_configuration()['path'])]
    runtime = {'environment_script': marker, 'files': [marker], 'selected': 'fixture-overlay'}
    primary_sources = scenario._template('primary')['cases'][0]['sources']
    calls = []

    def topology(sources, start, bounds, disturbance, *args):
        geometry = 'primary' if sources == primary_sources else 'secondary'
        calls.append((geometry, deepcopy(disturbance)))
        return synthetic_topology(geometry, disturbance)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(scenario, 'PILOT_ROOT', directory / 'pilot')
        patch.setattr(workflow.subprocess, 'check_output', lambda *a, **k: 'feature/gesc-gaussian-robustness-v2\n')
        patch.setattr(workflow.subprocess, 'Popen', unavailable)
        patch.setattr(workflow, 'collect_sources', lambda *a: deepcopy(sources))
        patch.setattr(workflow, '_v10_runtime_binding', lambda: deepcopy(runtime))
        patch.setattr(workflow, 'geometry_context', lambda *a: dict(
            label_geometry=marker, geometry_recovery=marker, geometry_receipts=[marker]))
        patch.setattr(workflow, 'selected_environment', lambda: {'fixture': 'environment'})
        patch.setattr(workflow, 'installed_entry_points', lambda **kw: {'fixture': 'installed'})
        patch.setenv('ROS_DOMAIN_ID', '201')
        patch.setattr(truth, 'derive_two_source_topology_qualification', topology)
        patch.setattr(truth, '_model', unavailable)
        patch.setattr(truth, 'validate_two_source_topology_qualification', lambda record, *a, **kw: deepcopy(record))
        patch.setattr(q1_study, 'verify_geometry_receipts', lambda *a: True)
        contracts = {version: workflow.read_json(workflow.prepare(version)['path'])
                     for version in ('m4-pilot-v9', VERSION)}
    return dict(directory=directory, contracts=contracts, runtime=runtime, calls=calls,
        files={path: path.read_bytes() for path in directory.rglob('*') if path.is_file()},
        directories={directory, *(path for path in directory.rglob('*') if path.is_dir())})


@pytest.fixture
def prepared(preparation, monkeypatch):
    root = preparation['directory']
    for path in root.rglob('*'):
        if path.is_file() and path not in preparation['files']:
            path.unlink()
    for path in sorted(root.rglob('*'), key=lambda item: len(item.parts), reverse=True):
        if path.is_dir() and path not in preparation['directories']:
            path.rmdir()
    for path, contents in preparation['files'].items():
        path.write_bytes(contents)
    monkeypatch.setattr(scenario, 'PILOT_ROOT', root / 'pilot')
    monkeypatch.setattr(workflow, '_v10_runtime_binding', lambda: deepcopy(preparation['runtime']))
    monkeypatch.setattr(workflow, 'selected_environment', lambda: {'fixture': 'environment'})
    monkeypatch.setattr(workflow, 'installed_entry_points', lambda **kw: {'fixture': 'installed'})
    monkeypatch.setattr(workflow.subprocess, 'Popen', unavailable)
    monkeypatch.setattr(workflow.subprocess, 'check_output', lambda *a, **kw: 'fixture-git\n')
    monkeypatch.setattr(workflow.time, 'monotonic', lambda: 100.)
    monkeypatch.setattr(truth, '_model', unavailable)
    monkeypatch.setattr(truth, 'derive_two_source_topology_qualification', unavailable)
    return deepcopy(preparation['contracts'][VERSION])


def fake_jobs(monkeypatch, contract, acquired, *, timeout=None):
    calls = []

    def run(argv, log_path, receipt_path, *, cap_sec, suite_end, process_ownership_mode):
        stage, number = argv[2], int(argv[-1])
        name = stage if stage != 'references' else f'references_{number}'
        calls.append((name, cap_sec, suite_end))
        output = Path(log_path).parent
        Path(log_path).write_text('fixture child; no process launched\n')
        complete = name != timeout
        record = dict(argv=argv, complete=complete, integrity_passed=True, timed_out=not complete,
            clean_termination=True, launched=True, return_code=0 if complete else -2,
            cap_sec=cap_sec, elapsed_wall_sec=1., process_ownership_mode=process_ownership_mode,
            source={'kind': 'script', **workflow.receipt(workflow.TOOLS / 'evaluate_m4.py')},
            log_path=str(log_path), log_sha256=workflow.receipt(log_path)['sha256'])
        save(Path(receipt_path), record)
        if not complete:
            return record
        if stage == 'labels':
            rows = []
            for original in acquired:
                slot = original['slot']
                labels = save(output / f'slot_{slot}_labels.json',
                    {**FIELDS, 'spatial_labels_precede_event_join': True, 'pose_faults': [],
                     'short_residences': [{'duration_sec': 7.8}]})
                row = {**original, 'labels': labels, 'acquisition_receipt': original['receipt'],
                    'scientific_analysis_complete': True,
                    'scientific_analysis_checks': dict.fromkeys(ROW_CHECKS, True),
                    'latency': {'status': 'EVIDENCE_UNAVAILABLE', 'observed': False,
                                'reason': 'short_or_censored_first_residence', 'right_censored': True},
                    'wrong_fills': 0, 'wrong_goals': 0, 'combined_sequence_passed': original['arm'] == 'B',
                    'combined_sequence_components': {
                        **original['runner_result']['outcomes'], 'arrival_criterion': 'post_recovery_arrival_v1',
                        'arrival_measurement_complete': True},
                    'arrival_passed': original['arm'] == 'B', 'time_to_arrival_sec': 172.6 if original['arm'] == 'B' else None,
                    'arrival_criterion': 'post_recovery_arrival_v1', 'arrival_measurement_complete': True,
                    'mandatory_stopped_acquisitions': 0 if original['arm'] in ('C', 'D') else None,
                    'mandatory_stop_evidence': {'status': 'OBSERVED_CONTINUOUS_ACQUISITION',
                        'analysis_complete': True, 'command_pairing_complete': True, 'authority_complete': True},
                    'direction_analysis_complete': False}
                if original['arm'] in ('C', 'D'):
                    row['normalized_inputs'] = save(output / f'slot_{slot}_normalized.json',
                        {**FIELDS, 'fixture': 'normalized input bound by successful reference owner'})
                rows.append(row)
            save(output / 'labels.json', {**FIELDS, 'block': 0, 'complete': True, 'integrity_passed': True,
                'runs': rows, 'input_files': [row['receipt'] for row in acquired],
                'contract': workflow.receipt(contract['contract_path'])})
        elif stage == 'references':
            labeled = workflow.read_json(output / 'labels.json')['runs'][number - 1]
            targets = [dict(run_id=labeled['run_id'], arm=labeled['arm'], partition=labeled['partition'],
                condition=labeled['condition'], number=i, offset_sec=offset, exposure_status='unexposed',
                input_qualified=False, reference_qualified=False, informative=False, eligible=False,
                usable_output=False, usable_averaging=False, reason='unexposed')
                for i, offset in enumerate(contract['science']['targets_sec'], 1)]
            save(output / f'slot_{number}_references.json', {**FIELDS, 'slot': number,
                'run_id': labeled['run_id'], 'normalized_inputs': labeled['normalized_inputs'],
                'contract': workflow.receipt(contract['contract_path']), 'complete': True,
                'integrity_passed': True, 'direction_analysis_complete': True, 'rows': targets})
        else:
            rows = workflow.read_json(output / 'labels.json')['runs']
            refs = []
            for row in rows:
                if row['arm'] not in ('C', 'D'):
                    continue
                path = output / f'slot_{row["slot"]}_references.json'
                if path.exists():
                    row.update(direction_analysis_complete=True,
                               direction_rows=workflow.read_json(path)['rows'])
                    refs.append(workflow.receipt(path))
                else:
                    row['scientific_analysis_complete'] = False
                    row['scientific_analysis_checks']['references'] = False
            complete_science = len(refs) == 2
            save(output / 'result.json', {**FIELDS, 'block': 0, 'complete': True, 'integrity_passed': True,
                'runs': rows, 'labels': workflow.receipt(output / 'labels.json'), 'references': refs,
                'contract': workflow.receipt(contract['contract_path']),
                'scientific_analysis_complete': complete_science,
                'scientific_analysis_checks': {'four_arm_analysis_complete': True,
                                               'both_reference_products_complete': complete_science}})
        return record

    monkeypatch.setattr(m4_science_job, 'finite_science_job', run)
    return calls


def development(prepared, monkeypatch, *, timeout=None):
    rows = [acquisition(prepared, slot, behavior=slot == 2) for slot in range(1, 5)]
    for row in rows:
        payload = {key: value for key, value in row.items() if key != 'receipt'}
        payload['runner_result'] = {'outcomes': dict.fromkeys(SEQUENCE_KEYS, row['arm'] == 'B')}
        path = Path(row['receipt']['path'])
        path.write_text(json.dumps(payload))
        row.update(payload, receipt=workflow.receipt(path))
    calls = fake_jobs(monkeypatch, prepared, rows, timeout=timeout)
    return rows, workflow.analyze_block(prepared, 0, rows, 1000.), calls


def rewrite_result(prepared, block, mutation):
    output = Path(prepared['root']) / 'analysis/block_0'
    result = workflow.read_json(output / 'result.json')
    mutation(result)
    (output / 'result.json').write_text(json.dumps(result))
    payload = {key: value for key, value in block.items() if key != 'receipt'}
    payload['result'] = workflow.receipt(output / 'result.json')
    (output / 'block_receipt.json').write_text(json.dumps(payload))
    return {**payload, 'receipt': workflow.receipt(output / 'block_receipt.json')}


def test_real_preparation_keeps_topology_gain_and_binds_v10_method_budget_runtime(prepared, preparation):
    old = preparation['contracts']['m4-pilot-v9']
    assert preparation['calls'][:4] == preparation['calls'][4:]
    assert prepared['method_version'] == 'recurrent_arrival_v10'
    assert prepared['development_release_policy'] == 'usable_four_arm_analysis_v1'
    assert prepared['runtime_binding'] == preparation['runtime']
    assert prepared['installed_entry_points'] == old['installed_entry_points']
    assert prepared['controller_configuration'] == old['controller_configuration']
    assert prepared['science']['labels_sec'] == 240. and old['science']['labels_sec'] == 120.
    assert prepared['science']['freeze_report_sec'] == 40.
    assert prepared['execution']['science_budget_sec'] == 1400.
    assert prepared['execution']['suite_timeout_sec'] == 15800.
    assert {row['seed'] for row in prepared['runs']} == {26091011, 26091012, 26091013, 26091014}
    assert len(prepared['runs']) == 16 and workflow.verify_frozen(prepared)


@pytest.mark.parametrize('fault', ['runtime', 'release_policy'])
def test_frozen_runtime_and_required_policy_cannot_be_removed(prepared, fault):
    prepared['runtime_binding' if fault == 'runtime' else 'development_release_policy'] = {}
    Path(prepared['contract_path']).write_text(json.dumps(prepared))
    with pytest.raises(ValueError):
        workflow.verify_frozen(prepared)


def test_complete_censored_failed_baselines_and_unexposed_targets_release_once(prepared, monkeypatch):
    rows, block, calls = development(prepared, monkeypatch)
    assert calls == [('labels', 240., 440.), ('references_3', 45., 440.),
                     ('references_4', 45., 440.), ('summary', 10., 440.)]
    release = workflow.release_holdouts(prepared, rows, block, 1000.)
    assert release['status'] == 'RELEASED' and release['scientific_completion_required'] is True
    assert release['scientific_pass_required'] is False
    assert release['development_evidence']['enabled_arrival_slots'] == [2]
    assert release['development_evidence']['continuous_development_slot'] == 4
    assert release['holdouts'] == prepared['runs'][4:]
    with pytest.raises(FileExistsError):
        workflow.release_holdouts(prepared, rows, block, 1000.)


@pytest.mark.parametrize('stage', ['labels', 'references_3', 'summary'])
def test_clean_science_timeout_keeps_ledger_but_withholds_v10(prepared, monkeypatch, stage):
    rows, block, _ = development(prepared, monkeypatch, timeout=stage)
    assert block['complete'] and block['integrity_passed']
    assert block['scientific_analysis_complete'] is False
    with pytest.raises(ValueError, match='science incomplete'):
        workflow.release_holdouts(prepared, rows, block, 1000.)
    assert not (Path(prepared['root']) / 'preflight/holdout_release.json').exists()


@pytest.mark.parametrize('artifact', ['slot_1_labels.json', 'slot_3_normalized.json',
                                     'slot_4_references.json', 'labels_job.json', 'summary.log'])
def test_changed_nested_artifact_blocks_release_despite_intact_outer_ledger(prepared, monkeypatch, artifact):
    rows, block, _ = development(prepared, monkeypatch)
    path = Path(prepared['root']) / 'analysis/block_0' / artifact
    path.write_text(path.read_text() + '\nchanged')
    with pytest.raises((ValueError, json.JSONDecodeError)):
        workflow.release_holdouts(prepared, rows, block, 1000.)


@pytest.mark.parametrize('fault', ['authority', 'missing_reference', 'target_population',
                                  'enabled_arrival', 'continuous_evidence', 'empty_checks', 'invented_checks'])
def test_rehashed_outer_result_does_not_certify_missing_science_or_enabled_evidence(prepared, monkeypatch, fault):
    rows, block, _ = development(prepared, monkeypatch)
    def mutate(result):
        if fault == 'authority': result['runs'][1]['scientific_analysis_checks']['selected_authority_complete'] = False
        elif fault == 'missing_reference': result['references'].pop()
        elif fault == 'target_population': result['runs'][3]['direction_rows'].pop()
        elif fault == 'enabled_arrival': result['runs'][1]['combined_sequence_passed'] = False
        elif fault == 'continuous_evidence': result['runs'][3]['mandatory_stop_evidence']['status'] = 'NO_ACQUISITION_OBSERVED'
        elif fault == 'invented_checks': result['scientific_analysis_checks'] = {'looks_good': True}
        else: result['scientific_analysis_checks'] = {}
    changed = rewrite_result(prepared, block, mutate)
    with pytest.raises(ValueError, match='usable development analysis'):
        workflow.release_holdouts(prepared, rows, changed, 1000.)


def test_coherently_rehashed_science_cannot_invent_arrival_against_actual_outcomes(prepared, monkeypatch):
    rows, block, _ = development(prepared, monkeypatch)
    output = Path(prepared['root']) / 'analysis/block_0'
    labels = workflow.read_json(output / 'labels.json')
    claimed = labels['runs'][3]
    claimed.update(combined_sequence_passed=True, arrival_passed=True, time_to_arrival_sec=172.6)
    claimed['combined_sequence_components'].update(dict.fromkeys(SEQUENCE_KEYS, True))
    (output / 'labels.json').write_text(json.dumps(labels))
    def mutate(result):
        result['labels'] = workflow.receipt(output / 'labels.json')
        result['runs'][3].update({key: claimed[key] for key in (
            'combined_sequence_passed', 'arrival_passed', 'time_to_arrival_sec', 'combined_sequence_components')})
    changed = rewrite_result(prepared, block, mutate)
    with pytest.raises(ValueError, match='actual acquisition outcomes'):
        workflow.release_holdouts(prepared, rows, changed, 1000.)


@pytest.mark.parametrize('kind', ['summary', 'run', 'slot'])
def test_any_started_confirmation_blocks_release(prepared, monkeypatch, kind):
    rows, block, _ = development(prepared, monkeypatch)
    target = prepared['runs'][-1]
    root = Path(prepared['root'])
    if kind == 'summary': Path(target['summary_path']).write_text('started')
    elif kind == 'run': (root / 'runs/date' / target['run_id']).mkdir(parents=True)
    else: save(root / 'acquisition/slot_16.json', {'status': 'STARTED'})
    with pytest.raises(ValueError, match='sealed'):
        workflow.release_holdouts(prepared, rows, block, 1000.)


def test_late_input_change_after_nested_verification_cannot_release(prepared, monkeypatch):
    rows, block, _ = development(prepared, monkeypatch)
    original = workflow._verify_v10_development_science
    def mutate_after(*args):
        result = original(*args)
        Path(rows[0]['input_files'][0]['path']).write_text('changed after nested checks')
        return result
    monkeypatch.setattr(workflow, '_verify_v10_development_science', mutate_after)
    with pytest.raises(ValueError, match='changed'):
        workflow.release_holdouts(prepared, rows, block, 1000.)


def test_failed_release_finalizes_all_sixteen_with_arrival_and_confirmation_scope(prepared, monkeypatch):
    rows, block, _ = development(prepared, monkeypatch, timeout='labels')
    with pytest.raises(ValueError):
        workflow.release_holdouts(prepared, rows, block, 1000.)
    for slot in range(5, 17):
        row = acquisition(prepared, slot, status='UNSTARTED', integrity=False)
        rows.append(row)
    final = workflow.finalize(prepared, rows, 1000.)
    result = workflow.read_json(final['result']['path'])
    report = Path(final['report']['path']).read_text()
    assert len(result['slots']) == 16 and result['slot_status_counts']['UNSTARTED'] == 12
    assert result['development_release']['status'] == 'WITHHELD'
    assert result['analysis_completion']['scientific_analysis_complete'] is False
    assert result['analysis_completion']['complete_blocks'] == 0
    assert 'recurrent_arrival_v10' in report and 'recurrent_geometry_v3' in report
    assert 'centroid_two_block_v2' not in report and 'stronger candidate' not in report
    assert 'previously exposed conditions' in report and 'Time to arrival' in report
