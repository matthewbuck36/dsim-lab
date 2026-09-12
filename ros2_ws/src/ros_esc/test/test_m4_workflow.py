"""M4 immutable workflow contracts using files and mocked science jobs only.

No bag, model, ROS graph, or acquisition is created. The unchanged aggregate
owner supplies the final missing-evidence denominators.
"""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

from ros_esc.scenario_runner.m4_scenario import expected_slots


REPOSITORY = Path(__file__).resolve().parents[4]
TOOLS = REPOSITORY/'docs/codex/gesc_gaussian/v2/tools'
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('m4_workflow_test_owner', TOOLS/'m4_workflow.py')
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)
import m4_science_job


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, sort_keys=True)
    return workflow.receipt(path)


@pytest.fixture
def contract(tmp_path, monkeypatch):
    root = tmp_path/'pilot'
    root.mkdir()
    marker = save(root/'source.json', {'unchanged': True})
    runs = [{**row, 'run_id': f'fixed-m4-slot-{row["slot"]}',
             'summary_path': str(root/'acquisition'/f'summary_{row["slot"]}.yaml'),
             'expected_cost_configuration': marker} for row in expected_slots()]
    value = dict(schema_version=1, version=workflow.VERSION, root=str(root),
        contract_path=str(root/'preflight/contract.json'), runs=runs,
        source_files=[marker], scenario=marker, topology_receipts={'fixture': marker},
        geometry_contexts={'fixture': dict(label_geometry=marker, geometry_recovery=marker,
                                          geometry_receipts=[marker])},
        environment={'selected': 'fixture'}, installed_entry_points={'source': 'fixture'},
        science={'labels_sec': 120., 'references_sec': 45., 'summary_sec': 10.,
                 'freeze_report_sec': 20., 'maximum_observations': 40000})
    save(Path(value['contract_path']), value)
    monkeypatch.setattr(workflow, 'selected_environment', lambda: value['environment'])
    monkeypatch.setattr(workflow, 'installed_entry_points', lambda **kwargs: value['installed_entry_points'])
    monkeypatch.setattr(workflow.time, 'monotonic', lambda: 100.)
    monkeypatch.setattr(workflow.subprocess, 'check_output',
        lambda argv, **kwargs: 'fixture-git-state\n')
    return value


def acquisition(contract, slot, *, status='COMPLETE', behavior=False, integrity=True):
    row = {**workflow.slot_spec(contract, slot), 'status': status,
           'integrity_passed': integrity, 'behavior_passed': behavior,
           'run_directory': str(Path(contract['root'])/'runs'/'2026-09-09'/f'slot-{slot}'),
           'input_files': contract['source_files']}
    return {**row, 'receipt': save(Path(contract['root'])/'acquisition'/f'slot_{slot}.json', row)}


def block_cases(contract, block=0):
    return [acquisition(contract, n) for n in range(block*4+1, block*4+5)]


def unstarted_remainder(contract, rows):
    return rows + [acquisition(contract, n, status='UNSTARTED', integrity=False)
                   for n in range(len(rows)+1, 17)]


def fake_jobs(monkeypatch, rows, *, timeout=None, invalid=None, mutate=None):
    calls = []

    def run(argv, log_path, receipt_path, *, cap_sec, suite_end):
        stage = argv[2]
        number = int(argv[-1])
        name = stage if stage != 'references' else f'references_{number}'
        calls.append((name, cap_sec, suite_end, list(argv)))
        complete = name != timeout and name != invalid
        result = dict(complete=complete, integrity_passed=name != invalid,
                      timed_out=name == timeout, clean_termination=True, name=name)
        save(Path(receipt_path), result)
        Path(log_path).write_text('mocked finite scientific job\n')
        output = Path(log_path).parent
        if complete and stage in ('labels', 'summary'):
            data = dict(complete=True, integrity_passed=True, block=rows[0]['block'],
                        runs=workflow._science_unavailable(rows, 'fixture_no_scientific_evidence'),
                        cases=[row['receipt'] for row in rows])
            if mutate is not None:
                mutate(stage, data)
            save(output/('labels.json' if stage == 'labels' else 'result.json'), data)
        return result

    monkeypatch.setattr(m4_science_job, 'finite_science_job', run)
    return calls


@pytest.mark.parametrize('fault', ['source', 'environment', 'installed', 'in_memory', 'population'])
def test_frozen_source_environment_and_population_are_mandatory(contract, monkeypatch, fault):
    assert workflow.verify_frozen(contract)
    if fault == 'source': Path(contract['source_files'][0]['path']).write_text('changed')
    elif fault == 'environment': monkeypatch.setattr(workflow, 'selected_environment', lambda: {})
    elif fault == 'installed': monkeypatch.setattr(workflow, 'installed_entry_points', lambda **kwargs: {})
    elif fault == 'in_memory': contract['runs'][0]['run_id'] = 'foreign'
    else: contract['runs'].pop()
    with pytest.raises(ValueError): workflow.verify_frozen(contract)


def test_four_exact_cases_analyzed_once_with_fixed_stage_budgets(contract, monkeypatch):
    rows = block_cases(contract)
    calls = fake_jobs(monkeypatch, rows)
    result = workflow.analyze_block(contract, 0, rows, 1000.)
    assert [row[:3] for row in calls] == [
        ('labels', 120., 320.), ('references_3', 45., 320.),
        ('references_4', 45., 320.), ('summary', 10., 320.)]
    assert result['cases'] == [row['receipt'] for row in rows]
    assert result['complete'] and result['integrity_passed']
    workflow.check_receipts([result['receipt'], result['result']])
    before = Path(result['receipt']['path']).read_bytes()
    with pytest.raises(FileExistsError): workflow.analyze_block(contract, 0, rows, 1000.)
    assert len(calls) == 4 and Path(result['receipt']['path']).read_bytes() == before


@pytest.mark.parametrize('fault', ['wrong_order', 'duplicate', 'foreign_run', 'changed_input', 'invalid_integrity'])
def test_bad_acquisition_receipts_stop_before_any_science(contract, monkeypatch, fault):
    rows = block_cases(contract)
    calls = fake_jobs(monkeypatch, rows)
    if fault == 'wrong_order': rows.reverse()
    elif fault == 'duplicate': rows[-1] = deepcopy(rows[0])
    elif fault == 'foreign_run': rows[0]['run_id'] = 'another-acquisition'
    elif fault == 'changed_input': Path(rows[0]['input_files'][0]['path']).write_text('changed')
    else: rows[0]['integrity_passed'] = False
    with pytest.raises(ValueError): workflow.analyze_block(contract, 0, rows, 1000.)
    assert not calls
    output = Path(contract['root'])/'analysis/block_0'
    assert (output/'started.json').exists() and not (output/'block_receipt.json').exists()


@pytest.mark.parametrize('stage,expected_count', [('labels', 1), ('summary', 4)])
def test_clean_science_timeout_preserves_all_unavailable_rows(contract, monkeypatch, stage, expected_count):
    rows = block_cases(contract)
    calls = fake_jobs(monkeypatch, rows, timeout=stage)
    result = workflow.analyze_block(contract, 0, rows, 1000.)
    data = workflow.read_json(result['result']['path'])
    assert len(calls) == expected_count
    assert data['complete'] and data['integrity_passed']
    assert data['scientific_analysis_complete'] is False
    assert [row['slot'] for row in data['runs']] == [1, 2, 3, 4]
    for row in data['runs']:
        assert row['science_status'] == 'EVIDENCE_UNAVAILABLE'
        assert row['latency']['observed'] is False
        assert row['wrong_fills'] is None and row['wrong_goals'] is None
        assert row['direction_rows'] == [] and row['direction_analysis_complete'] is False


def test_clean_reference_timeout_still_attempts_other_reference_and_summary(contract, monkeypatch):
    rows = block_cases(contract)
    calls = fake_jobs(monkeypatch, rows, timeout='references_3')
    result = workflow.analyze_block(contract, 0, rows, 1000.)
    assert [row[0] for row in calls] == ['labels', 'references_3', 'references_4', 'summary']
    assert result['integrity_passed'] and result['jobs'][1]['timed_out']


@pytest.mark.parametrize('stage,count', [('labels', 1), ('references_3', 2), ('summary', 4)])
def test_failed_job_integrity_aborts_without_block_completion(contract, monkeypatch, stage, count):
    rows = block_cases(contract)
    calls = fake_jobs(monkeypatch, rows, invalid=stage)
    with pytest.raises(ValueError, match='integrity'):
        workflow.analyze_block(contract, 0, rows, 1000.)
    assert len(calls) == count
    output = Path(contract['root'])/'analysis/block_0'
    assert (output/(stage+'_job.json')).exists()
    assert not (output/'block_receipt.json').exists()


@pytest.mark.parametrize('field,value', [('run_id', 'foreign-run'), ('case_id', 'foreign-case'),
    ('seed', 99), ('geometry', 'foreign-geometry'), ('behavior_passed', True),
    ('run_directory', '/foreign/run'), ('visible', False)])
def test_summary_cannot_substitute_run_identity_with_same_slot(contract, monkeypatch, field, value):
    rows = block_cases(contract)
    def mutate(stage, data):
        if stage == 'summary': data['runs'][0][field] = value
    fake_jobs(monkeypatch, rows, mutate=mutate)
    with pytest.raises(ValueError): workflow.analyze_block(contract, 0, rows, 1000.)
    assert not (Path(contract['root'])/'analysis/block_0/block_receipt.json').exists()


def development_analysis(contract, monkeypatch):
    rows = block_cases(contract)
    fake_jobs(monkeypatch, rows, timeout='labels')
    return rows, workflow.analyze_block(contract, 0, rows, 1000.)


def test_holdouts_freeze_once_after_complete_behavior_failure_and_science_timeout(contract, monkeypatch):
    rows, analysis = development_analysis(contract, monkeypatch)
    released = workflow.release_holdouts(contract, rows, analysis, 1000.)
    assert released['status'] == 'RELEASED' and released['scientific_pass_required'] is False
    assert released['holdouts'] == contract['runs'][4:]
    assert released['development'] == [row['receipt'] for row in rows]
    assert released['analysis'] == analysis['receipt']
    assert released['tuning_performed'] is False and released['replacements_allowed'] is False
    with pytest.raises(FileExistsError): workflow.release_holdouts(contract, rows, analysis, 1000.)


@pytest.mark.parametrize('opened', ['summary', 'run', 'slot'])
def test_started_holdout_blocks_release_even_with_good_development(contract, monkeypatch, opened):
    rows, analysis = development_analysis(contract, monkeypatch)
    holdout = contract['runs'][4]
    root = Path(contract['root'])
    if opened == 'summary': Path(holdout['summary_path']).write_text('started')
    elif opened == 'run': (root/'runs'/'2026-09-09'/holdout['run_id']).mkdir(parents=True)
    else: save(root/'acquisition/slot_5.json', {'status': 'STARTED'})
    with pytest.raises(ValueError, match='sealed'):
        workflow.release_holdouts(contract, rows, analysis, 1000.)
    assert not (root/'preflight/holdout_release.json').exists()


@pytest.mark.parametrize('fault', ['in_memory_analysis', 'foreign_cases'])
def test_holdout_release_requires_exact_immutable_development_analysis(contract, monkeypatch, fault):
    rows, analysis = development_analysis(contract, monkeypatch)
    if fault == 'in_memory_analysis':
        analysis['cases'] = []
    else:
        changed = {key: value for key, value in analysis.items() if key != 'receipt'}
        changed['cases'] = [contract['source_files'][0]]*4
        analysis = {**changed, 'receipt': save(Path(contract['root'])/'foreign_block.json', changed)}
    with pytest.raises(ValueError): workflow.release_holdouts(contract, rows, analysis, 1000.)


def test_final_abort_preserves_all_sixteen_slots_and_192_direction_denominators(contract, monkeypatch):
    rows, analysis = development_analysis(contract, monkeypatch)
    rows.append(acquisition(contract, 5, status='ABORTED', integrity=False))
    rows = unstarted_remainder(contract, rows)
    final = workflow.finalize(contract, rows, 1000.)
    data = workflow.read_json(final['result']['path'])
    assert [row['slot'] for row in data['slots']] == list(range(1, 17))
    assert data['slot_status_counts'] == {'COMPLETE': 4, 'ABORTED': 1, 'UNSTARTED': 11}
    assert data['direction_scheduled_total'] == 192
    assert len(data['direction_rows']) == 192
    by_run = {}
    for target in data['direction_rows']:
        by_run.setdefault(target['run_id'], []).append(target)
        assert target['exposure_status'] == 'analysis_unavailable' and target['eligible'] is False
    assert len(by_run) == 8
    for targets in by_run.values():
        assert [row['number'] for row in targets] == list(range(1, 25))
        assert [row['offset_sec'] for row in targets] == [15+30*k for k in range(24)]
    assert data['direction']['counts']['scheduled'] == 144
    assert len(data['direction_by_condition_arm']) == 8
    assert all(row['summary']['counts']['scheduled'] == 24 for row in data['direction_by_condition_arm'])
    assert all(row['summary']['counts']['exposure_status'] == {'analysis_unavailable': 24}
               for row in data['direction_by_condition_arm'])
    assert data['direction']['status'] == data['latency']['status'] == 'EVIDENCE_UNAVAILABLE'
    assert data['latency']['observed_endpoint_count'] == 0
    assert data['latency']['no_additional_errors'] is None
    report = Path(final['report']['path']).read_text()
    assert '0/12 observed endpoints; 0/6 pairs' in report
    assert 'All 192' in report and '/144 scheduled holdout targets' in report
    workflow.check_receipts([final['receipt'], final['report'], final['result']])
    with pytest.raises(FileExistsError): workflow.finalize(contract, rows, 1000.)


@pytest.mark.parametrize('fault', ['duplicate', 'in_memory_run', 'in_memory_outcome'])
def test_finalization_rejects_duplicate_or_mutated_acquisition_receipts(contract, fault):
    rows = unstarted_remainder(contract, block_cases(contract))
    if fault == 'duplicate': rows.append(deepcopy(rows[0]))
    elif fault == 'in_memory_run': rows[0]['run_id'] = 'foreign'
    else: rows[0]['behavior_passed'] = True
    with pytest.raises(ValueError): workflow.finalize(contract, rows, 1000.)
    assert not (Path(contract['root'])/'report/report_receipt.json').exists()


def test_finalization_rejects_foreign_science_run_even_after_rehash(contract, monkeypatch):
    rows, analysis = development_analysis(contract, monkeypatch)
    rows = unstarted_remainder(contract, rows)
    block_path = Path(analysis['receipt']['path'])
    block = workflow.read_json(block_path)
    result = workflow.read_json(block['result']['path'])
    result['runs'][0]['run_id'] = 'foreign'
    block['result'] = save(Path(contract['root'])/'foreign_science.json', result)
    block_path.write_text(json.dumps(block))
    with pytest.raises(ValueError): workflow.finalize(contract, rows, 1000.)


def test_prepare_wrong_branch_refuses_before_preflight_creation(tmp_path, monkeypatch):
    root = tmp_path/'uncreated'
    monkeypatch.setattr(workflow, 'ROOT', root)
    monkeypatch.setattr(workflow.subprocess, 'check_output', lambda *a, **k: 'feature/closed-v1\n')
    with pytest.raises(ValueError, match='V2 branch'): workflow.prepare()
    assert not root.exists()


def test_prepare_existing_version_refuses_without_model_or_overwrite(tmp_path, monkeypatch):
    root = tmp_path/'retained'
    root.mkdir()
    sentinel = save(root/'failed_preparation.json', {'status': 'INCOMPLETE'})
    monkeypatch.setattr(workflow, 'ROOT', root)
    monkeypatch.setattr(workflow.subprocess, 'check_output',
        lambda *a, **k: 'feature/gesc-gaussian-robustness-v2\n')
    monkeypatch.setattr(workflow, 'collect_sources', lambda: pytest.fail('retained version cannot retry'))
    with pytest.raises(FileExistsError): workflow.prepare()
    workflow.check_receipts([sentinel])


def test_prepare_freezes_real_sixteen_case_expansion_without_model_or_acquisition(tmp_path, monkeypatch):
    from ros_esc.scenario_runner import aggregate_field_truth as truth
    from ros_esc.scenario_runner import m4_scenario
    from ros_esc.plotting_scripts import q1_study

    root = tmp_path/'fresh-pilot'
    marker = save(tmp_path/'frozen_source.json', {'fixture': 'source'})
    original = m4_scenario._template('secondary')['cases'][0]['success']['staged_recovery']['topology_qualification']
    calls = []
    def topology(sources, start, bounds, disturbance, *args):
        calls.append(deepcopy(disturbance))
        record = deepcopy(original)
        record.pop('result_sha256')
        record['disturbances_sha256'] = truth.canonical_sha256(disturbance)
        record['result_sha256'] = truth.canonical_sha256(record)
        return record

    monkeypatch.setattr(workflow, 'ROOT', root)
    monkeypatch.setattr(workflow.subprocess, 'check_output',
        lambda *a, **k: 'feature/gesc-gaussian-robustness-v2\n')
    monkeypatch.setattr(workflow.subprocess, 'Popen', lambda *a, **k: pytest.fail('no acquisition'))
    monkeypatch.setattr(workflow, 'collect_sources', lambda: [marker])
    monkeypatch.setattr(workflow, 'geometry_context', lambda *args: dict(
        label_geometry=marker, geometry_recovery=marker, geometry_receipts=[marker]))
    monkeypatch.setattr(workflow, 'selected_environment', lambda: {'fixture': 'environment'})
    monkeypatch.setattr(workflow, 'installed_entry_points', lambda **kwargs: {'fixture': 'installed'})
    monkeypatch.setenv('ROS_DOMAIN_ID', '78')
    monkeypatch.setattr(truth, 'derive_two_source_topology_qualification', topology)
    monkeypatch.setattr(truth, 'validate_two_source_topology_qualification', lambda record, *a, **k: deepcopy(record))
    monkeypatch.setattr(q1_study, 'verify_geometry_receipts', lambda *a, **k: True)

    ref = workflow.prepare()
    prepared = workflow.read_json(root/'preflight/prepared.json')
    data = workflow.read_json(ref['path'])
    assert prepared['status'] == 'PREPARED' and prepared['acquisition_started'] is False
    assert len(calls) == 3 and calls[1]['sensor_noise']['std_dev'] == .015
    assert calls[2]['sensor_delay_sec'] == calls[2]['pose_delay_sec'] == .1
    assert workflow.verify_frozen(data)
    assert [row['slot'] for row in data['runs']] == list(range(1, 17))
    assert [row['visible'] for row in data['runs']] == [True]*4+[False]*12
    assert data['execution']['suite_timeout_sec'] == 15300.
    assert data['science']['maximum_observations'] == 40000
    for row in data['runs']:
        assert row['resolved_scenario']['seed'] == row['seed']
        assert ('--gui' in row['runner_argv']) == row['visible']
        assert '--strict-cleanup' in row['runner_argv']
        workflow.check_receipts([row['expected_cost_configuration']])
    assert not (root/'acquisition').exists() and not (root/'runs').exists()
    with pytest.raises(FileExistsError): workflow.prepare()


@pytest.mark.parametrize('fault', [None, 'validation_failed', 'changed_pins', 'unverified_archive', 'wrong_prepared_contract', 'holdout_initial_release'])
def test_public_dispatch_requires_exact_prepared_validated_checkpointed_development(contract, fault):
    root = Path(contract['root'])
    contract_ref = workflow.receipt(contract['contract_path'])
    pins = {row['path']: row['sha256'] for row in contract['source_files']}
    validation = dict(returncode=0, source_stable=True, before=deepcopy(pins), after=deepcopy(pins))
    checkpoint = dict(archive_verified=True)
    prepared = dict(status='PREPARED', contract=contract_ref)
    if fault == 'validation_failed': validation['returncode'] = 1
    elif fault == 'changed_pins': validation['before'] = validation['after'] = {}
    elif fault == 'unverified_archive': checkpoint['archive_verified'] = False
    elif fault == 'wrong_prepared_contract': prepared['contract'] = contract['source_files'][0]
    release = dict(status='RELEASED', initial_slots=[1, 2, 3, 4], contract=contract_ref,
        prepared=save(root/'preflight/prepared.json', prepared),
        source_validation=save(root/'validation.json', validation),
        source_checkpoint=save(root/'checkpoint.json', checkpoint))
    if fault == 'holdout_initial_release': release['initial_slots'] = [5, 6, 7, 8]
    save(root/'preflight/dispatch_release.json', release)
    if fault is None:
        assert workflow.verify_dispatch_release(contract['contract_path']) == release
    else:
        with pytest.raises(ValueError): workflow.verify_dispatch_release(contract['contract_path'])
