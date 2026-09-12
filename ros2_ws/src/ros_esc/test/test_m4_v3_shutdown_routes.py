"""V3 selection across existing runner callbacks, cleanup and science owners.

ROS lifecycle calls are mocked; actual installed ros2run wrappers and finite
Python children exercise signal delivery without ROS graph or model startup.
"""

import json
from pathlib import Path
import signal
import time

import pytest

from ros_esc.scenario_runner import run_scenario as runner
from test_m4_v2_subreaper_adversarial import worker
from test_m4_v2_subreaper_routes import FAKE_ROS, route_arguments, proof


MODE = 'subreaper_group_v3'
STRATEGY = 'initial_unreaped_root_group_sigint_then_adopted_pidfd'


def complete(result, code):
    assert result['return_code'] == code
    ownership = result['process_ownership']
    assert ownership['mode'] == MODE
    assert ownership['signal_strategy'] == STRATEGY
    assert ownership['inspection_complete'] and not ownership['inspection_errors']
    assert all(ownership['kernel_proof'].values())


@pytest.mark.parametrize('route', ['boundary', 'global'])
def test_specialized_route_interrupts_installed_wrapper_and_allows_recorder_finish(route):
    recorder = '''
import signal,time
stopping=False
def stop(*args):
    global stopping
    stopping=True
signal.signal(signal.SIGINT,stop)
signal.signal(signal.SIGTERM,stop)
end=time.monotonic()+4.
while not stopping and time.monotonic()<end: time.sleep(.01)
assert stopping
time.sleep(.20)
print('RECORDER_FINALIZED',flush=True)
'''
    wrapper = ('import sys; from ros2run.api import run_executable; '
               f'sys.exit(run_executable(path=sys.executable,argv=["-c",{recorder!r}]))')
    value = worker(FAKE_ROS + f'''
resolved['suite_id']='m4_pilot_v3'
end=time.monotonic()+3.
result=owner.run_record_process([sys.executable,'-c',{wrapper!r}],.50,.60,
    absolute_deadline=end,process_ownership_mode={MODE!r},**{route_arguments(route)})
emit(dict(result=result,end=end,lifecycle=lifecycle))
''')
    result = value['result']
    complete(result, 0)
    assert result['timed_out']
    assert 'RECORDER_FINALIZED' in result['stdout']
    rows = result['process_ownership']['signals']
    assert len(rows) == 1, rows
    assert rows[0]['transport'] == 'killpg_unreaped_root'
    assert rows[0]['sent'] and rows[0]['no_reap_guard'] and rows[0]['pidfd'] is False
    assert rows[0]['signal'] == signal.SIGINT and rows[0]['phase'] == 'graceful'
    identity = rows[0]['leader_identity']
    assert identity['pid'] == identity['session_id'] == identity['process_group_id'] == result['session_id']
    assert result['deadline_audit']['absolute_deadline'] == value['end']
    assert result['deadline_audit']['completed_monotonic'] < value['end']
    assert value['lifecycle'][-1] == 'context_shutdown'


@pytest.mark.parametrize('suite,accepted', [
    ('m4_pilot_v1', True), ('m4_pilot_v2', True), ('m4_pilot_v3', True),
    ('m4_pilot_v15', False), ('q1_primary_shadow_v1', False)])
def test_evaluator_selector_exact_v3_admission(suite, accepted):
    resolved = {'suite_id': suite, 'algorithm': {'launch_overrides': {
        'convergence_metric_mode': 'centroid_two_block_v2',
        'centroid_window_sec': 6., 'centroid_epsilon_m': .18}}}
    value = runner._m4_centroid_event_selection(resolved)
    assert (value is not None) is accepted
    if accepted:
        assert value['metric_mode'] == 'centroid_two_block_v2'
        assert value['window_sec'] == 6. and value['epsilon_m'] == .18


@pytest.mark.parametrize('incorrect', [None, 'mode', 'strategy'])
def test_cleanup_requires_v3_strategy_and_keeps_actual_independent_inspection(monkeypatch, incorrect):
    selected = proof()
    selected.update(mode=MODE, signal_strategy=STRATEGY)
    if incorrect == 'mode': selected['mode'] = 'subreaper_v2'
    if incorrect == 'strategy': selected['signal_strategy'] = 'direct_child_pidfd'
    calls=[]
    def graph(**kwargs): calls.append('graph'); return set()
    def sessions(*args, **kwargs): calls.append('sessions'); return []
    def identities(*args, **kwargs): calls.append('identities'); return {}
    monkeypatch.setattr(runner, 'ros_graph_nodes', graph)
    monkeypatch.setattr(runner, 'session_processes', sessions)
    monkeypatch.setattr(runner, '_live_snapshot_processes', identities)
    result = runner.cleanup_evidence(set(), 73301, strict=True,
        absolute_deadline=time.monotonic()+2., process_ownership=selected,
        process_ownership_mode=MODE)
    assert result['passed'] is (incorrect is None)
    assert result['inspection_performed'] is (incorrect is None)
    assert calls == ([] if incorrect else ['graph', 'sessions', 'identities'])
    if incorrect:
        assert result['remaining_new_nodes'] is None


def test_existing_public_cli_selects_v3_without_new_entrypoint(monkeypatch):
    seen=[]
    def execute(*args, **kwargs): seen.append((args,kwargs)); return {'runs': []}
    monkeypatch.setattr(runner, 'execute_suite', execute)
    monkeypatch.setattr(runner, 'load_suite', lambda path: {'suite_id': 'm4_pilot_v3'})
    assert runner.main(['fixture.yaml','--operator','fixture','--strict-cleanup',
                        '--process-ownership-mode',MODE]) == 0
    assert seen[0][1]['process_ownership_mode'] == MODE
    assert seen[0][1]['strict_cleanup'] is True


def science(tmp_path, code, cap=4.):
    tools=Path(__file__).resolve().parents[4]/'docs/codex/gesc_gaussian/v2/tools'
    return worker(f'''
sys.path.insert(0,{str(tools)!r})
from m4_science_job import finite_science_job
result=finite_science_job([sys.executable,'-c',{code!r}],
    {str(tmp_path/'science.log')!r},{str(tmp_path/'science.json')!r},
    cap_sec={cap},suite_end=time.monotonic()+8.,process_ownership_mode={MODE!r})
emit(result)
''')


def test_science_selected_v3_normal_exit_retains_exact_mode_and_source(tmp_path):
    result=science(tmp_path,'import time; time.sleep(.05); print("complete")')
    complete(result,0)
    assert result['complete'] and result['integrity_passed']
    assert result['process_ownership']['signals'] == []
    assert json.loads((tmp_path/'science.json').read_text()) == result


def test_science_v3_timeout_sends_one_guarded_group_interrupt(tmp_path):
    result=science(tmp_path,'import time; time.sleep(4.)',cap=3.3)
    complete(result,-signal.SIGINT)
    assert result['timed_out'] and result['integrity_passed']
    assert not result['complete']
    assert result['process_ownership']['signals'][0]['transport']=='killpg_unreaped_root'
    assert len(result['process_ownership']['signals'])==1
    assert result['elapsed_wall_sec']<3.3


def test_science_v3_resistant_root_escalates_with_pidfds_inside_existing_cap(tmp_path):
    result=science(tmp_path,
        'import signal,time; signal.signal(signal.SIGINT,signal.SIG_IGN); '
        'signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(4.)',cap=3.3)
    complete(result,-signal.SIGKILL)
    assert result['timed_out'] and result['integrity_passed']
    rows=result['process_ownership']['signals']
    assert [r['signal'] for r in rows]==[signal.SIGINT,signal.SIGTERM,signal.SIGKILL]
    assert rows[0]['pidfd'] is False and all(r['pidfd'] is True for r in rows[1:])
    assert all(r['monotonic']<result['absolute_deadline'] for r in rows)
    assert result['elapsed_wall_sec']<3.3


def test_science_v3_short_budget_does_not_start_or_invent_kernel_proof(tmp_path):
    result=science(tmp_path,'raise AssertionError("must not start")',cap=2.)
    assert result['timed_out'] and result['integrity_passed'] and not result['launched']
    assert result['process_ownership']['mode']==MODE
    assert result['process_ownership']['signal_strategy']==STRATEGY
    assert result['process_ownership']['no_child_launched'] is True
    assert 'kernel_proof' not in result['process_ownership']


def test_science_v3_source_error_is_not_scientific_unavailability(tmp_path):
    result=science(tmp_path,'raise RuntimeError("source error")')
    complete(result,1)
    assert not result['integrity_passed'] and not result['complete']
