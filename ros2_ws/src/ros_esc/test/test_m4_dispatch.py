"""Finite M4 population, strict process evidence and one-time dispatch tests.

No Gazebo/ROS graph or model evaluation is started. Separate finite process
fixtures exercise actual procfs ownership; topology fixtures test condition
routing while replacing only the expensive numerical validation function.
"""

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest
import yaml

from ros_esc.scenario_runner import aggregate_field_truth as truth
from ros_esc.scenario_runner import run_scenario as runner
from ros_esc.scenario_runner import m4_scenario as scenario
from ros_esc.scenario_runner.scenario_schema import expand_suite, load_suite


ROOT = Path(__file__).resolve().parents[4]
TOOL = ROOT/'docs/codex/gesc_gaussian/v2/tools/run_m4.py'
spec = importlib.util.spec_from_file_location('m4_dispatch_test_tool', TOOL)
dispatch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dispatch)


def rehash(record):
    record.pop('result_sha256', None)
    record['result_sha256'] = truth.canonical_sha256(record)
    return record


def topology_fixtures():
    original = scenario._template('secondary')['cases'][0]['success']['staged_recovery']['topology_qualification']
    return {condition: rehash({**deepcopy(original), 'fixture_condition': condition})
            for condition in ('nominal', 'noise', 'delay')}


def test_exact_sixteen_matching_seeds_geometry_and_selectors_without_new_numerics(tmp_path, monkeypatch):
    calls = []
    def validate(record, sources, start, bounds, disturbances, local_id, global_id, **kwargs):
        calls.append((record['fixture_condition'], deepcopy(disturbances), deepcopy(sources)))
        return deepcopy(record)
    monkeypatch.setattr(truth, 'validate_two_source_topology_qualification', validate)
    ref = scenario.write_m4_scenario(tmp_path/'scenario.yaml', topology_fixtures(), runs_root=tmp_path/'runs')
    suite = load_suite(ref['path'])
    runs, unsupported = expand_suite(suite)
    assert not unsupported and len(runs) == 16 and len(calls) == 12
    assert [run['seed'] for run in runs] == [26090801]*4 + [26090802]*4 + [26090803]*4 + [26090804]*4
    assert [slot['visible'] for slot in scenario.expected_slots()] == [True]*4 + [False]*12
    assert (suite['execution']['run_timeout_sec'], suite['execution']['wall_timeout_sec'],
            suite['execution']['shutdown_grace_sec']) == (720., 900., 45.)
    for index, run in enumerate(runs):
        arm = ('A', 'B', 'C', 'D')[index % 4]
        selected = run['algorithm']['launch_overrides']
        assert selected['convergence_metric_mode'] == ('centroid_two_block_v2' if arm in ('B', 'D') else 'pde_mean_v1')
        assert selected['continuous_search_mode'] == ('rolling_gesc_v2' if arm in ('C', 'D') else 'stationary_v1')
        assert selected['v2_qualification_observation_only'] is False
        assert run['start'] == runs[index-index%4]['start']
        assert run['sources'] == runs[index-index%4]['sources']
        assert run['algorithm']['ablations'] == {'gaussian_fill_enabled': True, 'affine_assist_enabled': True, 'recenter_enabled': False}
        if arm in ('B', 'D'):
            assert (selected['centroid_window_sec'], selected['centroid_epsilon_m'], selected['centroid_maximum_radius_m']) == (6., .18, .5)
        if arm in ('C', 'D'):
            assert (selected['v2_candidate_radius_m'], selected['v2_candidate_epsilon_m']) == (.75, .15)
            assert selected['v2_direction_policy'] == 'moving_cycle_coherence_v1'
    assert [item[0] for item in calls] == ['nominal']*4 + ['noise']*4 + ['delay']*4
    assert calls[4][1]['sensor_noise']['std_dev'] == .015
    assert calls[8][1]['sensor_delay_sec'] == calls[8][1]['pose_delay_sec'] == .1
    assert calls[0][2][0]['x_m'] == .5740251485476348
    with pytest.raises(FileExistsError):
        scenario.write_m4_scenario(ref['path'], topology_fixtures(), runs_root=tmp_path/'runs')


@pytest.mark.parametrize('fault', ['absent_condition', 'changed_hash'])
def test_incomplete_topology_records_cannot_make_resource(tmp_path, fault):
    records = topology_fixtures()
    if fault == 'absent_condition': records.pop('delay')
    else: records['noise']['result_sha256'] = '0'*64
    with pytest.raises(ValueError):
        scenario.write_m4_scenario(tmp_path/'scenario.yaml', records, runs_root=tmp_path/'runs')
    assert not (tmp_path/'scenario.yaml').exists()


def test_strict_ros_probe_is_child_bounded_and_failures_are_visible(monkeypatch):
    monkeypatch.setattr(runner.time, 'monotonic', lambda: 100.)
    calls = []
    def run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(stdout='["/existing"]')
    monkeypatch.setattr(runner.subprocess, 'run', run)
    assert runner.ros_graph_nodes(strict=True, absolute_deadline=102.) == {'/existing'}
    assert calls[0][0][:2] == [sys.executable, '-c']
    assert calls[0][1]['timeout'] == 2.
    monkeypatch.setattr(runner.subprocess, 'run', lambda *args, **kwargs: (_ for _ in ()).throw(
        subprocess.TimeoutExpired('probe', 2.)))
    with pytest.raises(subprocess.TimeoutExpired):
        runner.ros_graph_nodes(strict=True, absolute_deadline=102.)
    with pytest.raises(TimeoutError):
        runner.ros_graph_nodes(strict=True, absolute_deadline=100.)


def ownership(root=50):
    return {'inspection_complete': True, 'identities': [
        dict(pid=root, session_id=root, start_ticks=9, process_group_id=root, parent_pid=1, state='S'),
        dict(pid=root+1, session_id=root+1, start_ticks=10, process_group_id=root+1, parent_pid=root, state='S')],
        'session_ids': [root, root+1], 'inspection_errors': []}


@pytest.mark.parametrize('fault', ['none', 'probe', 'process', 'nested_survivor', 'missing_owner'])
def test_strict_cleanup_inspects_nested_sessions_and_refuses_unavailable(monkeypatch, fault):
    monkeypatch.setattr(runner.time, 'monotonic', lambda: 100.)
    sessions = []
    def graph(**kwargs):
        if fault == 'probe': raise OSError('discovery unavailable')
        return set()
    def processes(sid, **kwargs):
        sessions.append(sid)
        if fault == 'process': raise OSError('procfs unavailable')
        return [{'pid': 51}] if fault == 'nested_survivor' and sid == 51 else []
    monkeypatch.setattr(runner, 'ros_graph_nodes', graph)
    monkeypatch.setattr(runner, 'session_processes', processes)
    monkeypatch.setattr(runner, '_live_snapshot_processes', lambda *a, **k: {})
    result = runner.cleanup_evidence(set(), 50, settle_sec=0., strict=True,
        absolute_deadline=101., process_ownership=None if fault == 'missing_owner' else ownership())
    assert result['passed'] is (fault == 'none')
    if fault in ('none', 'nested_survivor'): assert sessions == [50, 51]
    if fault in ('probe', 'process', 'missing_owner'): assert result['inspection_errors']


def test_owned_tracking_retains_previous_nested_session_and_bounds_evidence(monkeypatch):
    audit = runner._process_tracking(True)
    source = ownership()
    current = {row['pid']: row for row in source['identities']}
    monkeypatch.setattr(runner, '_snapshot_process_tree', lambda *a, **k: deepcopy(current))
    process = SimpleNamespace(pid=50)
    runner._track_owned_processes(process, audit)
    current.pop(51)
    runner._track_owned_processes(process, audit)
    assert audit['session_ids'] == [50, 51] and len(audit['identities']) == 2
    monkeypatch.setattr(runner, 'MAX_TRACKED_PROCESSES', 1)
    for _ in range(30): runner._track_owned_processes(process, audit)
    assert not audit['inspection_complete'] and len(audit['inspection_errors']) == 16


def test_real_plain_child_tracks_nested_session_and_preserves_unrelated_sentinel(monkeypatch):
    monkeypatch.setattr(runner, 'ros_graph_nodes', lambda **kwargs: set())
    sentinel = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)'],
                                start_new_session=True)
    code = ('import subprocess,sys,time; child=subprocess.Popen([sys.executable,"-c",'
            '"import time; time.sleep(10)"],start_new_session=True); '
            'print(child.pid,flush=True); time.sleep(.35); child.terminate(); '
            'child.wait(timeout=2); time.sleep(.35)')
    try:
        result = runner.run_record_process([sys.executable, '-c', code], 3., .2,
            absolute_deadline=time.monotonic()+20., strict_process_tracking=True)
        child_pid = int(result['stdout'].strip())
        audit = result['process_ownership']
        assert result['return_code'] == 0 and not result['timed_out']
        assert audit['inspection_complete'], audit
        assert child_pid in audit['session_ids'] and result['session_id'] in audit['session_ids']
        assert sentinel.pid not in audit['session_ids']
        cleanup = runner.cleanup_evidence(set(), result['session_id'], settle_sec=0.,
            strict=True, absolute_deadline=time.monotonic()+5., process_ownership=audit)
        assert cleanup['passed'], cleanup
        assert sentinel.poll() is None
    finally:
        sentinel.terminate()
        sentinel.wait(timeout=3.)


@pytest.mark.parametrize('noisy', [False, True])
def test_actual_runner_retains_selected_launch_and_captured_cost_witness(tmp_path, monkeypatch, noisy):
    document = yaml.safe_load((scenario.SCENARIOS/'phase06_smoke.yaml').read_text())
    document['schema_version'] = 2
    document['cases'][0]['profiles'] = ['robust_gaussian_v1']
    if noisy:
        document['defaults']['disturbances']['sensor_noise'] = {'model': 'gaussian', 'std_dev': .015}
    path = tmp_path/'suite.yaml'
    path.write_text(yaml.safe_dump(document))
    run_id = 'm4-owner-witness'
    directory = tmp_path/'runs'/'2026-09-09'/run_id
    directory.mkdir(parents=True)
    (directory/'completeness.json').write_text('{"passed": true}')
    monkeypatch.setattr(runner, 'ensure_ros_daemon', lambda: None)
    monkeypatch.setattr(runner, 'ros_graph_nodes', lambda **kwargs: set())
    captured = {}
    def process(command, *args, **kwargs):
        assert kwargs['strict_process_tracking'] is True
        captured['launch'] = command[command.index('--')+1:]
        cost_arg = next(arg for arg in captured['launch'] if arg.startswith('cost_function_config_filepath:='))
        captured['cost_path'] = cost_arg.split(':=', 1)[1]
        (directory/'metadata.yaml').write_text(yaml.safe_dump({'recording': {'status': 'finalized',
            'readiness_ever_true': True}, 'target_argv': captured['launch']}))
        return {'return_code': 0, 'timed_out': False, 'stdout': 'retained',
                'session_id': 50, 'process_ownership': ownership()}
    monkeypatch.setattr(runner, 'run_record_process', process)
    monkeypatch.setattr(runner, 'cleanup_evidence', lambda *a, **k: {'passed': True, 'strict': True})
    monkeypatch.setattr(runner, '_bag_outcomes', lambda *a, **k: {'readiness_interval_available': True})
    result = runner.execute_suite(path, 'test', run_id=run_id, runs_root=tmp_path/'runs',
        summary_output=tmp_path/'summary.yaml', strict_cleanup=True,
        cleanup_deadline=time.monotonic()+30.)['runs'][0]
    assert result['launch_argv'] == captured['launch']
    witness = result['captured_cost_configuration']
    assert witness['argv_path'] == captured['cost_path']
    expected_path = directory/'resolved_cost_function.json' if noisy else runner.MULTI_LIGHT_COST
    assert witness['path'] == str(expected_path)
    assert witness['sha256'] == hashlib.sha256(expected_path.read_bytes()).hexdigest()
    assert yaml.safe_load((directory/'scenario_result.yaml').read_text()) == result
    if noisy:
        assert not Path(witness['argv_path']).exists()
        noise = json.loads(expected_path.read_text())['Noise']
        assert noise['params'] == {'std_dev': .015, 'seed_num': 6001}


@pytest.fixture
def frozen_dispatch(tmp_path, monkeypatch):
    clock = [100.]
    monkeypatch.setattr(dispatch.time, 'monotonic', lambda: clock[0])
    monkeypatch.setattr(runner.time, 'monotonic', lambda: clock[0])
    monkeypatch.setenv('ROS_DOMAIN_ID', '79')
    scenario_path = tmp_path/'scenario.yaml'
    scenario_path.write_text('fixture scenario owner\n')
    contract_path = tmp_path/'contract.json'
    contract = dict(version='m4-pilot-v1', root=str(tmp_path), contract_path=str(contract_path),
        scenario=dispatch.receipt(scenario_path), source_files=[], execution=dict(
            runs_root=str(tmp_path/'runs'), ros_domain_id=79, suite_timeout_sec=15300.,
            case_timeout_sec=900., cleanup_reserve_sec=30., science_budget_sec=900.,
            recording_sec=720., shutdown_grace_sec=45.),
        science=dict(labels_sec=120., references_sec=45., summary_sec=10., freeze_report_sec=20.),
        runs=[])
    for slot in scenario.expected_slots():
        planned = {**slot, 'run_id': 'm4-fixture-'+str(slot['slot']),
            'summary_path': str(tmp_path/'acquisition'/f'summary_{slot["slot"]}.yaml'),
            'resolved_scenario': {'case_key': 'key-'+str(slot['slot'])},
            'launch_argv': ['selected-launch', 'convergence_metric_mode:=centroid_two_block_v2',
                            'supervisor_use_sim_time:=True']}
        planned['runner_argv'] = dispatch.runner_command(contract, planned)
        contract['runs'].append(planned)
    contract_path.write_text(json.dumps(contract))
    calls, analyses, releases, finalized = [], [], [], []
    faults = {}
    monkeypatch.setattr(runner, 'ensure_ros_daemon', lambda: None)
    monkeypatch.setattr(runner, 'ros_graph_nodes', lambda **kwargs: set())
    monkeypatch.setattr(runner, 'cleanup_evidence', lambda *args, **kwargs:
        {'passed': not faults.get('cleanup'), 'strict': True, 'inspection_errors': []})
    def process(command, wall, grace, **kwargs):
        slot_number = len(calls)+1
        planned = contract['runs'][slot_number-1]
        assert command == planned['runner_argv'] + ['--cleanup-deadline', str(clock[0]+870.)]
        assert wall == 900. and grace == 45. and kwargs['absolute_deadline'] == clock[0]+870.
        assert kwargs['strict_process_tracking'] is True
        calls.append(planned['slot'])
        clock[0] += faults.get('case_elapsed', 1.)
        directory = tmp_path/'runs'/'2026-09-09'/planned['run_id']
        directory.mkdir(parents=True)
        recording = dict(status='finalized', complete=True, final_zero_observed=True,
            target_clean_shutdown=True, bag_clean_shutdown=True, completeness_passed=True,
            readiness_ever_true=True, infrastructure_status='completed')
        if faults.get('final_zero') == slot_number: recording['final_zero_observed'] = False
        launch_argv = list(planned['launch_argv'])
        if faults.get('changed_selector') == slot_number:
            launch_argv[1] = 'convergence_metric_mode:=centroid_windows_v2'
        if faults.get('changed_controller_clock') == slot_number:
            launch_argv.append('controller_use_sim_time:=False')
        if faults.get('changed_supervisor_clock') == slot_number:
            launch_argv[2] = 'supervisor_use_sim_time:=False'
        metadata = {'recording': recording, 'target_argv': launch_argv, 'run_id': planned['run_id']}
        result = dict(run_id=planned['run_id'], case_id=planned['case_id'], seed=planned['seed'],
            case_key=planned['resolved_scenario']['case_key'], run_directory=str(directory),
            recording_complete=True, cleanup={'passed': True, 'strict': True, 'inspection_errors': []},
            record_process={'session_id': 50, 'return_code': 0, 'timed_out': False, 'process_ownership': ownership()},
            classification={'passed': not faults.get('behavior'), 'infrastructure_status': 'completed'},
            outcomes={'observed_state_sequence': ['SEARCH'], 'observed_events': ['FILL_REJECTED', 'TIMEOUT']},
            launch_argv=launch_argv)
        if faults.get('wrong_id') == slot_number: result['run_id'] = 'wrong'
        if faults.get('failsafe') == slot_number: result['outcomes']['observed_state_sequence'].append('FAILSAFE')
        if faults.get('summary_missing') != slot_number:
            Path(planned['summary_path']).write_text(yaml.safe_dump(dict(resolved_run_count=1,
                dry_run=False, selected_case_ids=[planned['case_id']], source_path=str(scenario_path), runs=[result])))
        for name, document in (('metadata.yaml', metadata), ('resolved_scenario.yaml', planned['resolved_scenario']),
            ('scenario_result.yaml', result), ('resolved_topics.yaml', {}), ('resolved_parameters.yaml', {})):
            (directory/name).write_text(yaml.safe_dump(document))
        (directory/'completeness.json').write_text(json.dumps({'passed': True}))
        (directory/'bag').mkdir()
        (directory/'bag/metadata.yaml').write_text('fixture: true\n')
        return dict(return_code=1 if faults.get('behavior') else 0, timed_out=False, stdout='retained\n',
            session_id=60, process_ownership=ownership(60), deadline_audit={'deadline_exhausted': False})
    monkeypatch.setattr(runner, 'run_record_process', process)
    def verify(value):
        if faults.get('source_change') and len(calls) >= faults['source_change']:
            raise ValueError('source hash changed')
    def analyze(value, block, rows, suite_end):
        analyses.append((block, len(rows), all(row['receipt'] for row in rows)))
        clock[0] += faults.get('science_elapsed', 1.)
        return {'complete': True, 'integrity_passed': not faults.get('analysis_integrity'),
                'scientific_status': 'EVIDENCE_UNAVAILABLE'}
    def release(value, rows, result, suite_end):
        releases.append(len(rows))
        return {'status': 'RELEASED'}
    def finalize(value, rows, suite_end):
        finalized.append(deepcopy(rows))
        return {'complete': True}
    def run():
        return dispatch.dispatch(contract_path, verify_frozen=verify, analyze_block=analyze,
            release_holdouts=release, finalize=finalize, bind_recorded=lambda *a, **k: {'passed': True})
    return SimpleNamespace(run=run, contract=contract, path=contract_path, clock=clock,
        faults=faults, calls=calls, analyses=analyses, releases=releases, finalized=finalized)


def test_complete_behavioral_failure_and_scientific_unavailability_keep_all_sixteen(frozen_dispatch):
    fixture = frozen_dispatch
    fixture.faults['behavior'] = True
    result = fixture.run()
    assert result['status'] == 'COMPLETE'
    assert fixture.calls == list(range(1, 17)) and fixture.releases == [4]
    assert [row[0] for row in fixture.analyses] == [0, 1, 2, 3]
    assert all(row['integrity_passed'] and not row['behavior_passed'] for row in result['slots'])
    assert len(fixture.finalized[0]) == 16
    with pytest.raises(FileExistsError): fixture.run()


@pytest.mark.parametrize('fault', ['wrong_id', 'failsafe', 'final_zero', 'summary_missing', 'source_change',
                                 'changed_selector', 'changed_controller_clock', 'changed_supervisor_clock'])
def test_integrity_failure_aborts_later_slots_and_preserves_unstarted(frozen_dispatch, fault):
    fixture = frozen_dispatch
    fixture.faults[fault] = 2
    result = fixture.run()
    assert result['status'] == 'INCOMPLETE' and fixture.calls == [1, 2]
    assert result['slots'][1]['status'] == 'INCOMPLETE'
    assert all(row['status'] == 'UNSTARTED' for row in result['slots'][2:])
    assert fixture.releases == [] and fixture.analyses == []


@pytest.mark.parametrize('fault', [None, 'nominal', 'missing_witness', 'changed_source',
    'changed_capture', 'argv_path', 'capture_path', 'capture_symlink', 'changed_hash',
    'extra_witness', 'changed_selector', 'changed_clock', 'duplicate_cost', 'extra_argument'])
def test_noise_launch_allows_only_exact_witnessed_cost_relocation(tmp_path, fault):
    frozen = tmp_path/'frozen_cost.json'
    frozen.write_text('{"Noise": {"params": {"std_dev": 0.015}}}\n')
    directory = tmp_path/'recorded_run'
    directory.mkdir()
    captured = directory/'resolved_cost_function.json'
    captured.write_bytes(frozen.read_bytes())
    prefix = 'cost_function_config_filepath:='
    planned = {'condition': 'noise', 'expected_cost_configuration': dispatch.receipt(frozen),
        'launch_argv': ['selected-launch', 'convergence_metric_mode:=centroid_two_block_v2',
            'supervisor_use_sim_time:=True', prefix+str(frozen)]}
    temporary = str(tmp_path/'removed_temporary_cost.json')
    result = {'launch_argv': planned['launch_argv'][:-1] + [prefix+temporary],
        'captured_cost_configuration': {'argv_path': temporary, **dispatch.receipt(captured)}}
    witness = result['captured_cost_configuration']
    if fault == 'nominal': planned['condition'] = 'nominal'
    elif fault == 'missing_witness': del result['captured_cost_configuration']
    elif fault == 'changed_source': frozen.write_text('{}')
    elif fault == 'changed_capture': captured.write_text('{}')
    elif fault == 'argv_path': witness['argv_path'] = str(tmp_path/'different_temp.json')
    elif fault == 'capture_path': witness['path'] = str(frozen)
    elif fault == 'capture_symlink':
        captured.unlink()
        captured.symlink_to(frozen)
    elif fault == 'changed_hash': witness['sha256'] = '0'*64
    elif fault == 'extra_witness': witness['unbound'] = True
    elif fault == 'changed_selector': result['launch_argv'][1] = 'convergence_metric_mode:=centroid_windows_v2'
    elif fault == 'changed_clock': result['launch_argv'][2] = 'supervisor_use_sim_time:=False'
    elif fault == 'duplicate_cost': result['launch_argv'].append(prefix+temporary)
    elif fault == 'extra_argument': result['launch_argv'].append('use_sim_time:=False')
    if fault is None:
        assert dispatch.validate_launch_binding(planned, result, directory) is None
        assert not Path(temporary).exists()
    else:
        with pytest.raises(ValueError, match='M4 .*launch'):
            dispatch.validate_launch_binding(planned, result, directory)


def test_development_analysis_integrity_cannot_open_holdouts(frozen_dispatch):
    fixture = frozen_dispatch
    fixture.faults['analysis_integrity'] = True
    result = fixture.run()
    assert result['status'] == 'INCOMPLETE'
    assert fixture.calls == [1, 2, 3, 4] and fixture.releases == []
    assert all(row['status'] == 'UNSTARTED' for row in result['slots'][4:])


def test_full_remaining_science_envelope_is_reserved(frozen_dispatch):
    fixture = frozen_dispatch
    fixture.faults.update(case_elapsed=900., science_elapsed=221.)
    result = fixture.run()
    assert result['status'] == 'INCOMPLETE'
    assert fixture.calls == [1, 2, 3, 4]
    assert 'envelopes' in result['failure']


@pytest.mark.parametrize('fault', ['seed', 'order', 'command', 'budget', 'duplicate_id'])
def test_contract_mutations_refuse_before_process(frozen_dispatch, fault):
    fixture = frozen_dispatch
    contract = fixture.contract
    if fault == 'seed': contract['runs'][4]['seed'] += 1
    elif fault == 'order': contract['runs'][0], contract['runs'][1] = contract['runs'][1], contract['runs'][0]
    elif fault == 'command': contract['runs'][0]['runner_argv'].append('--dry-run')
    elif fault == 'budget': contract['execution']['case_timeout_sec'] = 901.
    else: contract['runs'][1]['run_id'] = contract['runs'][0]['run_id']
    fixture.path.write_text(json.dumps(contract))
    with pytest.raises(ValueError): fixture.run()
    assert not fixture.calls


@pytest.mark.parametrize('released', [False, True])
def test_public_cli_checks_material_source_release_before_dispatch(tmp_path, monkeypatch, released):
    calls = []
    def release(path):
        calls.append('release')
        if not released: raise ValueError('source release absent')
    def launch(*args, **kwargs):
        calls.append('dispatch')
        return dict(status='COMPLETE', failure=None, elapsed_wall_sec=1.)
    hooks = SimpleNamespace(verify_dispatch_release=release, verify_frozen=lambda *a: None,
        analyze_block=lambda *a: None, release_holdouts=lambda *a: None, finalize=lambda *a: None)
    monkeypatch.setitem(sys.modules, 'm4_workflow', hooks)
    monkeypatch.setattr(sys, 'argv', ['run_m4.py', '--contract', str(tmp_path/'contract.json')])
    monkeypatch.setattr(dispatch, 'dispatch', launch)
    if released:
        assert dispatch.main() == 0 and calls == ['release', 'dispatch']
    else:
        with pytest.raises(ValueError, match='source release absent'): dispatch.main()
        assert calls == ['release']
