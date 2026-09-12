"""V14 retained acquisition admission and fresh-only finite dispatch; no ROS."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from test_m4_dispatch import dispatch, runner, scenario, frozen_dispatch


VERSION = 'm4-pilot-v14'


@pytest.fixture
def retained_case(tmp_path, monkeypatch):
    clock = [100.]
    monkeypatch.setattr(dispatch.time, 'monotonic', lambda: clock[0])
    monkeypatch.setenv('ROS_DOMAIN_ID', '79')
    # Scenario authentication is independently exercised by V14 version tests;
    # this fixture retains the dispatcher's actual budgets/population/path checks.
    monkeypatch.setattr(dispatch, 'validate_experiment_contract', lambda value: None)
    root = tmp_path/'comparison'
    root.mkdir()
    scenario_path = root/'scenario.yaml'
    scenario_path.write_text('fixture scenario\n')
    contract_path = root/'contract.json'
    contract = dict(version=VERSION, root=str(root), contract_path=str(contract_path),
        scenario=dispatch.receipt(scenario_path), source_files=[],
        execution={**scenario.experiment_execution_budgets(VERSION),
            'runs_root': str(root/'runs'), 'ros_domain_id': 79},
        science=dict(labels_sec=240., references_sec=45., summary_sec=10., freeze_report_sec=40.),
        runs=[])
    source_rows = []
    for slot in scenario.expected_slots(VERSION):
        planned = {**slot, 'run_id': scenario.experiment_run_id(slot, VERSION),
            'summary_path': str(root/'acquisition'/f'summary_{slot["slot"]}.yaml')}
        planned['runner_argv'] = dispatch.runner_command(contract, planned)
        if slot['slot'] <= 4:
            planned.update(summary_path=str(tmp_path/'original'/f'summary_{slot["slot"]}.yaml'),
                           runner_argv=['original-v13-command', str(slot['slot'])])
            row = {**slot, 'run_id': planned['run_id'], 'status': 'COMPLETE',
                'integrity_passed': True, 'behavior_passed': slot['arm'] != 'A',
                'started_monotonic': -900.+slot['slot'], 'completed_monotonic': -100.+slot['slot']}
            path = tmp_path/'original'/f'slot_{slot["slot"]}.json'
            path.parent.mkdir(exist_ok=True)
            path.write_text(json.dumps(row))
            source_rows.append({**row, 'receipt': dispatch.receipt(path)})
        contract['runs'].append(planned)
    contract_path.write_text(json.dumps(contract))
    block = dict(block=0, complete=True, integrity_passed=True,
        cases=[row['receipt'] for row in source_rows], source='retained-v13-and-r22')
    block_path = root/'cached_block_receipt.json'
    block_path.write_text(json.dumps(block))
    block['receipt'] = dispatch.receipt(block_path)
    calls, analyses, releases, finalized, loads = [], [], [], [], []
    faults = {}
    monkeypatch.setattr(runner, 'ensure_ros_daemon', lambda: None)
    monkeypatch.setattr(runner, 'ros_graph_nodes', lambda **kwargs: set())
    monkeypatch.setattr(runner, 'cleanup_evidence', lambda *a, **k: {'passed': True})
    monkeypatch.setattr(dispatch, 'validate_process_ownership', lambda *a: None)

    def process(command, wall, grace, **kwargs):
        planned = next(p for p in contract['runs'] if p['case_id'] == command[command.index('--case-id')+1])
        calls.append(planned['slot'])
        assert planned['slot'] >= 5
        assert wall == 900. and grace == 45.
        assert kwargs['process_ownership_mode'] == 'subreaper_group_v3'
        assert kwargs['strict_process_tracking'] and kwargs['absolute_deadline'] == clock[0]+870.
        clock[0] += faults.get('case_elapsed', 1.)
        return dict(stdout='fixture\n', session_id=60)

    def native_result(_contract, planned, outer):
        if faults.get('case_failure') == planned['slot']:
            raise ValueError('native integrity failure')
        directory = root/'runs'/'fixture-date'/planned['run_id']
        (directory/'bag').mkdir(parents=True)
        for name in ('metadata.yaml', 'resolved_topics.yaml', 'resolved_scenario.yaml',
                     'resolved_parameters.yaml', 'scenario_result.yaml', 'completeness.json',
                     'bag/metadata.yaml'):
            (directory/name).write_text('{}')
        return dict(record_process=dict(session_id=50, process_ownership={}),
                    classification=dict(passed=True)), directory

    monkeypatch.setattr(runner, 'run_record_process', process)
    monkeypatch.setattr(dispatch, 'validate_case_result', native_result)

    def load(value, deadline):
        loads.append(deadline)
        clock[0] += faults.get('load_elapsed', 0.)
        if faults.get('missing_cache'):
            raise FileNotFoundError('cached development is absent')
        return deepcopy(source_rows), deepcopy(block)

    def analyze(value, index, rows, deadline):
        analyses.append((index, [row['slot'] for row in rows]))
        return dict(complete=True, integrity_passed=True, block=index)

    def release(value, rows, result, deadline):
        releases.append(deepcopy(rows))
        assert not calls and result == block
        return {'status': 'WITHHELD' if faults.get('release_failure') else 'RELEASED'}

    def finalize(value, rows, deadline):
        finalized.append(deepcopy(rows))
        return dict(complete=True)

    def run(callback=load):
        return dispatch.dispatch(contract_path, verify_frozen=lambda value: None,
            analyze_block=analyze, release_holdouts=release, finalize=finalize,
            retained_development=callback, bind_recorded=lambda *a, **k: {'passed': True})

    return SimpleNamespace(run=run, root=root, contract=contract, path=contract_path,
        source_rows=source_rows, block=block, clock=clock, faults=faults, calls=calls,
        analyses=analyses, releases=releases, finalized=finalized, loads=loads)


def test_retained_originals_and_reference_envelopes_then_exactly_twelve_fresh(retained_case):
    case = retained_case
    originals = deepcopy(case.source_rows)
    result = case.run()
    assert result['status'] == 'COMPLETE' and result['failure'] is None
    assert case.calls == list(range(5, 17))
    assert case.analyses == [(1, list(range(5, 9))), (2, list(range(9, 13))), (3, list(range(13, 17)))]
    assert case.releases == [originals] and len(case.loads) == 1
    assert result['slots'][:4] == originals == case.finalized[0][:4]
    assert len(result['slots']) == 16 and len(result['analysis_blocks']) == 4
    assert result['analysis_blocks'][0] == case.block
    assert result['replacements_dispatched'] is False
    assert not list((case.root/'runs').glob('*/m4-pilot-v13-*'))
    for row, ref in zip(originals, result['retained_development_references']):
        envelope = json.loads(Path(ref['path']).read_text())
        assert ref == dispatch.receipt(ref['path'])
        assert envelope == dict(experiment_version=VERSION, comparison_slot=row['slot'],
            acquisition_origin='retained_v13', source_row=row,
            source_acquisition=row['receipt'], reuse_receipt=case.block['receipt'])
        assert json.loads(Path(row['receipt']['path']).read_text()) == {k: v for k, v in row.items() if k != 'receipt'}
        assert not (case.root/'acquisition'/f'runner_{row["slot"]}.log').exists()
    with pytest.raises(FileExistsError):
        case.run()


@pytest.mark.parametrize('fault', ['missing_callback', 'missing_cache', 'short_rows',
    'wrong_identity', 'incomplete_row', 'changed_source_bytes', 'invented_row_time',
    'incomplete_block', 'changed_block_bytes', 'invented_block_field', 'wrong_block_cases', 'load_deadline'])
def test_unauthenticated_retained_evidence_never_releases_or_launches(retained_case, fault):
    case = retained_case
    if fault == 'missing_cache': case.faults[fault] = True
    elif fault == 'short_rows': case.source_rows.pop()
    elif fault == 'wrong_identity': case.source_rows[0]['run_id'] = 'wrong'
    elif fault == 'incomplete_row': case.source_rows[0]['integrity_passed'] = False
    elif fault == 'changed_source_bytes': Path(case.source_rows[0]['receipt']['path']).write_text('{}')
    elif fault == 'invented_row_time': case.source_rows[0]['started_monotonic'] = 101.
    elif fault == 'incomplete_block': case.block['complete'] = False
    elif fault == 'changed_block_bytes': Path(case.block['receipt']['path']).write_text('{}')
    elif fault == 'invented_block_field': case.block['invented'] = True
    elif fault == 'wrong_block_cases':
        case.block['cases'].reverse()
        path = Path(case.block['receipt']['path'])
        path.write_text(json.dumps({k: v for k, v in case.block.items() if k != 'receipt'}))
        case.block['receipt'] = dispatch.receipt(path)
    elif fault == 'load_deadline': case.faults['load_elapsed'] = 15800.
    result = case.run(None) if fault == 'missing_callback' else case.run()
    assert result['status'] == 'INCOMPLETE'
    assert not case.calls and not case.analyses and not case.releases
    assert len(result['slots']) == 16
    assert [row['status'] for row in result['slots']] == ['RETAINED_UNAVAILABLE']*4+['UNSTARTED']*12
    assert all('started_monotonic' not in row for row in result['slots'])
    assert result['retained_development_references'] == []


def test_release_withheld_preserves_authenticated_originals_and_all_fresh_unstarted(retained_case):
    case = retained_case
    case.faults['release_failure'] = True
    result = case.run()
    assert result['status'] == 'INCOMPLETE' and len(case.releases) == 1
    assert result['slots'][:4] == case.source_rows
    assert [row['status'] for row in result['slots'][4:]] == ['UNSTARTED']*12
    assert not case.calls and not case.analyses
    assert len(result['retained_development_references']) == 4


def test_first_fresh_failure_does_not_replace_or_reacquire(retained_case):
    case = retained_case
    case.faults['case_failure'] = 5
    result = case.run()
    assert result['status'] == 'INCOMPLETE' and case.calls == [5]
    assert result['slots'][:4] == case.source_rows
    assert result['slots'][4]['status'] == 'INCOMPLETE'
    assert [row['status'] for row in result['slots'][5:]] == ['UNSTARTED']*11
    assert not case.analyses and len(case.releases) == 1


def test_fresh_path_checks_remain_strict_after_original_plans(retained_case):
    case = retained_case
    assert dispatch.validate_contract(case.contract) == case.root
    changed = deepcopy(case.contract)
    changed['runs'][4]['summary_path'] = str(case.root/'wrong.yaml')
    with pytest.raises(ValueError, match='summary path'):
        dispatch.validate_contract(changed)
    changed = deepcopy(case.contract)
    changed['runs'][4]['runner_argv'] = ['wrong']
    with pytest.raises(ValueError, match='canonical'):
        dispatch.validate_contract(changed)


def test_historical_dispatch_ignores_new_callback(frozen_dispatch, monkeypatch):
    original = dispatch.dispatch
    def forbidden(*args):
        raise AssertionError('historical version cannot reuse development')
    def selected(*args, **kwargs):
        return original(*args, **kwargs, retained_development=forbidden)
    monkeypatch.setattr(dispatch, 'dispatch', selected)
    result = frozen_dispatch.run()
    assert result['status'] == 'COMPLETE'
    assert frozen_dispatch.calls == list(range(1, 17))
    assert 'retained_development_references' not in result


def test_public_cli_forwards_existing_workflow_loader_after_material_release(tmp_path, monkeypatch):
    calls = []
    loader = lambda *a: None
    def release(path):
        calls.append('material_release')
    def launch(path, **kwargs):
        assert kwargs['retained_development'] is loader
        calls.append('dispatch')
        return dict(status='COMPLETE', failure=None, elapsed_wall_sec=1.)
    hooks = SimpleNamespace(verify_dispatch_release=release, verify_frozen=lambda *a: None,
        analyze_block=lambda *a: None, release_holdouts=lambda *a: None,
        finalize=lambda *a: None, load_retained_development=loader)
    monkeypatch.setitem(sys.modules, 'm4_workflow', hooks)
    monkeypatch.setattr(sys, 'argv', ['run_m4.py', '--contract', str(tmp_path/'contract.json')])
    monkeypatch.setattr(dispatch, 'dispatch', launch)
    assert dispatch.main() == 0 and calls == ['material_release', 'dispatch']
