"""Selected existing callback routes, cleanup evidence and pure science jobs.

Real finite children run in isolated owner workers. ROS lifecycle calls are
fixtures: no graph, model, recorder, Gazebo or scientific input is started.
"""

import json
from pathlib import Path
import signal
import time

import pytest

from ros_esc.scenario_runner import run_scenario as runner
from test_m4_v2_subreaper_adversarial import assert_complete, worker


FAKE_ROS = '''
class FakeNode:
    def create_subscription(self, *args): return object()
    def destroy_node(self): lifecycle.append('node_destroyed')
class FakeExecutor:
    def __init__(self, **kwargs): pass
    def add_node(self, node): pass
    def remove_node(self, node): lifecycle.append('node_removed')
    def shutdown(self): lifecycle.append('executor_shutdown')
    def spin_once(self, timeout_sec): time.sleep(min(.01, timeout_sec))
lifecycle=[]
owner.rclpy.context.Context=lambda: object()
owner.rclpy.init=lambda **kwargs: lifecycle.append('init')
owner.rclpy.shutdown=lambda **kwargs: lifecycle.append('context_shutdown')
owner.rclpy.create_node=lambda *args,**kwargs: FakeNode()
owner.SingleThreadedExecutor=FakeExecutor
resolved={'suite_id':'m4_pilot_v2',
    'success':{'staged_recovery':{'global_source_id':'global'}},
    'sources':[{'id':'global','x_m':1.,'y_m':1.}],
    'algorithm':{'launch_overrides':{
        'convergence_metric_mode':'centroid_two_block_v2',
        'centroid_window_sec':6.,'centroid_epsilon_m':.18}}}
'''


def route_arguments(route):
    return ("dict(staged_recovery=resolved)" if route == 'global' else
            "dict(anchor_state='SEARCH',boundary_state='VERIFY_EXTREMUM')")


@pytest.mark.parametrize('route', ['boundary', 'global'])
@pytest.mark.parametrize('timeout', [False, True])
def test_actual_specialized_owner_preserves_status_or_cleans_at_original_deadline(route, timeout):
    code = 'import time; time.sleep(3.)' if timeout else 'import time; time.sleep(.10); raise SystemExit(17)'
    result = worker(FAKE_ROS + f'''
end=time.monotonic()+2.
result=selected({code!r}, wall_timeout_sec={.15 if timeout else 1.},
    shutdown_grace_sec=.1, absolute_deadline=end, **{route_arguments(route)})
emit(dict(result=result,lifecycle=lifecycle,end=end))
''')
    assert_complete(result['result'], -signal.SIGINT if timeout else 17)
    assert result['result']['timed_out'] is timeout
    assert result['result']['deadline_audit']['absolute_deadline'] == result['end']
    assert result['result']['deadline_audit']['completed_monotonic'] < result['end']
    assert result['lifecycle'] == ['init', 'node_removed', 'executor_shutdown',
                                    'node_destroyed', 'context_shutdown']


@pytest.mark.parametrize('route', ['boundary', 'global'])
def test_specialized_setup_cannot_renew_work_budget_or_launch_after_it_expires(route):
    result = worker(FAKE_ROS + f'''
def slow_node(*args, **kwargs):
    time.sleep(.20)
    return FakeNode()
owner.rclpy.create_node=slow_node
def forbidden(*args, **kwargs): raise AssertionError('late child launch')
owner.subprocess.Popen=forbidden
end=time.monotonic()+2.
try:
    selected('pass',wall_timeout_sec=.10,shutdown_grace_sec=.1,
        absolute_deadline=end,**{route_arguments(route)})
except TimeoutError as error:
    emit(dict(error=str(error),audit=error.process_ownership,
        deadline=error.execution_deadline_audit,end=end,lifecycle=lifecycle))
else:
    raise AssertionError('expired work budget accepted')
''')
    assert result['audit']['root_pid'] is None
    assert result['audit']['kernel_proof']['final_echild'] is True
    assert result['audit']['kernel_proof']['state_restored'] is True
    assert result['audit']['kernel_proof']['complete'] is False
    assert result['deadline']['absolute_deadline'] == result['end']
    assert result['deadline']['completed_monotonic'] < result['end']
    assert result['lifecycle'][-1] == 'context_shutdown'


@pytest.mark.parametrize('suite,selected', [
    ('m4_pilot_v1', True), ('m4_pilot_v2', True),
    ('m4_pilot_v15', False), ('q1_primary_shadow_v1', False), ('', False)])
def test_centroid_evaluator_exact_version_allowlist(suite, selected):
    value = runner._m4_centroid_event_selection({'suite_id': suite, 'algorithm': {
        'launch_overrides': {'convergence_metric_mode': 'centroid_two_block_v2',
            'centroid_window_sec': 6., 'centroid_epsilon_m': .18}}})
    assert (value is not None) is selected
    if selected:
        assert value['metric_mode'] == 'centroid_two_block_v2'
        assert value['window_sec'] == 6. and value['epsilon_m'] == .18


def proof():
    return dict(mode='subreaper_v2', root_pid=73301, inspection_complete=True,
        identities=[], session_ids=[73301], kernel_proof=dict.fromkeys((
            'baseline_echild', 'subreaper_verified', 'root_reaped', 'final_echild',
            'scope_exclusive', 'sigchld_valid', 'state_restored', 'complete'), True))


@pytest.mark.parametrize('failure', ['kernel', 'deadline', 'graph', 'sessions', None])
def test_selected_cleanup_records_missing_inspection_as_unknown(monkeypatch, failure):
    selected = proof()
    def graph(**kwargs):
        if failure == 'graph': raise PermissionError('graph denied')
        return set()
    def sessions(*args, **kwargs):
        if failure == 'sessions': raise PermissionError('process inspection denied')
        return []
    monkeypatch.setattr(runner, 'ros_graph_nodes', graph)
    monkeypatch.setattr(runner, 'session_processes', sessions)
    monkeypatch.setattr(runner, '_live_snapshot_processes', lambda *a, **k: {})
    if failure == 'kernel': selected['kernel_proof']['final_echild'] = False
    result = runner.cleanup_evidence(set(), 73301, strict=True,
        absolute_deadline=time.monotonic()+(-1. if failure == 'deadline' else 2.),
        process_ownership=selected, process_ownership_mode='subreaper_v2')
    assert result['passed'] is (failure is None)
    assert result['inspection_performed'] is (failure is None)
    assert result['process_ownership_mode'] == 'subreaper_v2'
    for field in ('remaining_new_nodes', 'remaining_session_processes', 'remaining_owned_processes'):
        expected = [] if failure is None or (failure == 'sessions' and field == 'remaining_new_nodes') else None
        assert result[field] == expected


def test_native_sigchld_rejects_unrecognized_libc_before_reading_layout(monkeypatch):
    class UnsupportedLibc:
        def sigaction(self, *args): pytest.fail('unsupported ABI must not be inspected')
    monkeypatch.setattr(runner.ctypes, 'CDLL', lambda *a, **k: UnsupportedLibc())
    with pytest.raises(RuntimeError, match='verified glibc ABI'):
        runner._subreaper_sigchld()


def science(tmp_path, code, cap=4.):
    tools = Path(__file__).resolve().parents[4]/'docs/codex/gesc_gaussian/v2/tools'
    return worker(f'''
sys.path.insert(0,{str(tools)!r})
from m4_science_job import finite_science_job
result=finite_science_job([sys.executable,'-c',{code!r}],
    {str(tmp_path/'science.log')!r},{str(tmp_path/'science.json')!r},
    cap_sec={cap},suite_end=time.monotonic()+8.,process_ownership_mode='subreaper_v2')
emit(result)
''')


def test_v2_science_success_has_source_receipt_and_kernel_proof(tmp_path):
    result = science(tmp_path, 'import time; time.sleep(.08); print("complete")')
    assert_complete(result)
    assert result['complete'] and result['integrity_passed']
    assert result['process_ownership_mode'] == 'subreaper_v2'
    assert result['source']['kind'] == 'inline_python'
    assert json.loads((tmp_path/'science.json').read_text()) == result


def test_v2_science_timeout_handles_selected_sigint_as_unavailability(tmp_path):
    result = science(tmp_path, 'import time; time.sleep(4.)', cap=3.3)
    assert_complete(result, -signal.SIGINT)
    assert not result['complete'] and result['timed_out'] and result['integrity_passed']
    assert result['elapsed_wall_sec'] < 3.3


def test_v2_science_resistant_child_escalates_inside_short_cap(tmp_path):
    result = science(tmp_path,
        'import signal,time; signal.signal(signal.SIGINT,signal.SIG_IGN); '
        'signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(4.)', cap=3.3)
    assert_complete(result, -signal.SIGKILL)
    assert result['integrity_passed'] and result['timed_out']
    assert [row['signal'] for row in result['process_ownership']['signals']] == [
        signal.SIGINT, signal.SIGTERM, signal.SIGKILL]
    assert result['elapsed_wall_sec'] < 3.3


@pytest.mark.parametrize('code,accepted', [
    ('raise RuntimeError("source fault")', False),
    ('import json,sys; print(json.dumps({"scientific_status":"EVIDENCE_UNAVAILABLE",'
     '"integrity_passed":True,"reason":"no informative reference"})); sys.exit(1)', True)])
def test_v2_science_nonzero_still_requires_explicit_typed_unavailability(tmp_path, code, accepted):
    result = science(tmp_path, code)
    assert_complete(result, 1)
    assert not result['complete']
    assert result['integrity_passed'] is accepted


def test_v2_science_rejects_and_reaps_forbidden_fast_orphan(tmp_path):
    result = science(tmp_path,
        'import os,time; pid=os.fork(); '
        'time.sleep(.10 if pid else .40); os._exit(0 if pid else 21)')
    assert_complete(result)
    assert result['unexpected_observed_descendants']
    assert not result['integrity_passed'] and result['clean_termination']


def test_v2_science_shortened_cap_retains_unavailable_without_launch(tmp_path):
    result = science(tmp_path, 'raise AssertionError("must not launch")', cap=2.)
    assert not result['launched'] and result['integrity_passed'] and result['timed_out']
    assert result['process_ownership']['mode'] == 'subreaper_v2'
    assert result['process_ownership']['no_child_launched']
