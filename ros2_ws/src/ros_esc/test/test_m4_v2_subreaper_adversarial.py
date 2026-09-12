"""Independent Linux ownership fixtures for the explicit M4 v2 runner route.

Each owner lives in a separate finite Python process, so pytest never changes
its subreaper or SIGCHLD state. No ROS graph, Gazebo, bag or model is started.
Child processes have finite lifetimes, including fixtures resisting signals.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import time

import pytest


WORKER_PREFIX = '''
import ctypes, errno, json, os, signal, subprocess, sys, time
from pathlib import Path
from ros_esc.scenario_runner import run_scenario as owner
owner.CANCEL_ESCALATION_SEC = .10
def selected(code, **kwargs):
    return owner.run_record_process([sys.executable, '-c', code],
        kwargs.pop('wall_timeout_sec', 2.), kwargs.pop('shutdown_grace_sec', .20),
        absolute_deadline=kwargs.pop('absolute_deadline', time.monotonic()+7.),
        process_ownership_mode='subreaper_v2', **kwargs)
def emit(value):
    print('M4_ADVERSARIAL_RESULT=' + json.dumps(value), flush=True)
'''


def worker(code, *, timeout=14.):
    """Bound even a broken owner; embedded fixture descendants also expire."""
    result = subprocess.run([sys.executable, '-c', WORKER_PREFIX+textwrap.dedent(code)],
        capture_output=True, text=True, timeout=timeout, start_new_session=True)
    assert result.returncode == 0, result.stdout[-3000:]+result.stderr[-3000:]
    packets = [line.partition('=')[2] for line in result.stdout.splitlines()
               if line.startswith('M4_ADVERSARIAL_RESULT=')]
    assert len(packets) == 1, result.stdout[-3000:]+result.stderr[-3000:]
    return json.loads(packets[0])


def assert_complete(result, expected_code=0):
    assert result['return_code'] == expected_code
    audit = result['process_ownership']
    assert audit['mode'] == 'subreaper_v2'
    assert audit['inspection_complete'] is True, audit
    assert not audit['inspection_errors'], audit
    proof = audit['kernel_proof']
    for key in ('baseline_echild', 'subreaper_verified', 'root_reaped',
                'final_echild', 'scope_exclusive', 'sigchld_valid', 'state_restored', 'complete'):
        assert proof[key] is True, (key, proof)


@pytest.mark.parametrize('exit_code', [0, 17])
def test_normal_root_exit_keeps_popen_status_and_restores_subreaper(exit_code):
    result = worker(f'''
        result = selected('import sys; sys.exit({exit_code})')
        emit(result)
    ''')
    assert_complete(result, exit_code)
    assert result['timed_out'] is False


def test_rapid_parent_exit_cannot_hide_live_nested_setsid_descendant(tmp_path):
    marker = tmp_path/'nested.json'
    nested = textwrap.dedent(f'''
        import json,os,time
        from pathlib import Path
        pid=os.fork()
        if pid:
            os.waitpid(pid,0)
            end=time.monotonic()+.5
            while not Path({str(marker)!r}).exists() and time.monotonic()<end: time.sleep(.005)
            assert Path({str(marker)!r}).exists()
            os._exit(0)
        os.setsid()
        pid=os.fork()
        if pid: os._exit(0)
        os.close(1); os.close(2)
        Path({str(marker)!r}).write_text(json.dumps(dict(pid=os.getpid(), sid=os.getsid(0))))
        time.sleep(1.0)
        os._exit(23)
    ''')
    result = worker(f'''
        result = selected({nested!r})
        emit(result)
    ''')
    assert_complete(result)
    child = json.loads(marker.read_text())
    assert child['sid'] != result['session_id']
    # A kernel ECHILD proof must include the orphan, even if its transient
    # parents were never present in one complete procfs traversal.
    assert not Path(f'/proc/{child["pid"]}').exists()


def test_adopted_zombie_is_reaped_before_final_echild(tmp_path):
    marker = tmp_path/'zombie.pid'
    code = textwrap.dedent(f'''
        import os,time
        from pathlib import Path
        pid=os.fork()
        if pid == 0:
            Path({str(marker)!r}).write_text(str(os.getpid()))
            os._exit(29)
        time.sleep(.15)
        os._exit(0)
    ''')
    result = worker(f'emit(selected({code!r}))\n')
    assert_complete(result)
    assert not Path('/proc/'+marker.read_text()).exists()


def test_live_adopted_survivor_does_not_escape_via_setsid_or_kill_unrelated_sibling(tmp_path):
    marker = tmp_path/'survivor.pid'
    code = textwrap.dedent(f'''
        import os,signal,time
        from pathlib import Path
        pid=os.fork()
        if pid:
            end=time.monotonic()+.5
            while not Path({str(marker)!r}).exists() and time.monotonic()<end: time.sleep(.005)
            assert Path({str(marker)!r}).exists()
            os._exit(0)
        os.setsid()
        os.close(1); os.close(2)
        signal.signal(signal.SIGINT,signal.SIG_IGN)
        signal.signal(signal.SIGTERM,signal.SIG_IGN)
        Path({str(marker)!r}).write_text(str(os.getpid()))
        time.sleep(5.)
    ''')
    sentinel = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(12.)'],
                                start_new_session=True)
    try:
        result = worker(f'emit(selected({code!r}))\n')
        assert_complete(result)
        assert sentinel.poll() is None
        assert sentinel.pid not in result['process_ownership']['session_ids']
        assert not Path('/proc/'+marker.read_text()).exists()
    finally:
        sentinel.terminate()
        sentinel.wait(timeout=2.)


@pytest.mark.parametrize('baseline', ['live', 'zombie'])
def test_preexisting_popen_child_is_not_reaped_or_signaled_by_new_scope(tmp_path, baseline):
    marker = tmp_path/'forbidden-launch'
    launch_code = f'from pathlib import Path; Path({str(marker)!r}).touch()'
    result = worker(f'''
        existing = subprocess.Popen([sys.executable, '-c',
            'import time; time.sleep(4.)' if {baseline!r} == 'live' else 'import sys;sys.exit(37)'])
        if {baseline!r} == 'zombie':
            end=time.monotonic()+2.
            while time.monotonic()<end:
                state=Path('/proc/'+str(existing.pid)+'/stat').read_text().split(') ')[1][0]
                if state=='Z': break
                time.sleep(.01)
            assert state=='Z'
        error=None
        try:
            selected({launch_code!r})
        except (ValueError, RuntimeError) as caught:
            error=type(caught).__name__+': '+str(caught)
        launched=Path({str(marker)!r}).exists()
        if {baseline!r}=='live':
            alive=existing.poll() is None
            existing.terminate()
            status=existing.wait(timeout=2.)
        else:
            alive=None
            status=existing.wait(timeout=2.)
        emit(dict(error=error, launched=launched, alive=alive, status=status))
    ''')
    assert result['error'] and not result['launched'], result
    if baseline == 'live': assert result['alive'] is True
    else: assert result['status'] == 37


@pytest.mark.parametrize('foreign_action', ['ignore', 'no_cld_wait'])
@pytest.mark.skipif(os.uname().machine != 'x86_64', reason='native fixture uses Linux x86_64 glibc sigaction ABI')
def test_native_sigchld_policy_is_rejected_even_when_python_cache_says_default(tmp_path, foreign_action):
    marker = tmp_path/'forbidden-sigchld-launch'
    launch_code = f'from pathlib import Path; Path({str(marker)!r}).touch()'
    result = worker(f'''
        class Sigaction(ctypes.Structure):
            _fields_=[('handler',ctypes.c_void_p),('mask',ctypes.c_ulong*16),
                      ('flags',ctypes.c_int),('restorer',ctypes.c_void_p)]
        libc=ctypes.CDLL(None,use_errno=True)
        old=Sigaction()
        assert libc.sigaction(signal.SIGCHLD,None,ctypes.byref(old))==0
        changed=Sigaction()
        ctypes.memmove(ctypes.byref(changed),ctypes.byref(old),ctypes.sizeof(old))
        if {foreign_action!r}=='ignore': changed.handler=1
        else: changed.flags |= 2  # Linux SA_NOCLDWAIT.
        assert libc.sigaction(signal.SIGCHLD,ctypes.byref(changed),None)==0
        cached_default=signal.getsignal(signal.SIGCHLD)==signal.SIG_DFL
        error=None
        try:
            selected({launch_code!r})
        except (ValueError,RuntimeError) as caught:
            error=type(caught).__name__+': '+str(caught)
        finally:
            assert libc.sigaction(signal.SIGCHLD,ctypes.byref(old),None)==0
        emit(dict(error=error,cached_default=cached_default,launched=Path({str(marker)!r}).exists()))
    ''')
    assert result['cached_default'] and result['error'] and not result['launched'], result


def test_echild_is_required_even_when_observation_returns_empty_for_live_children(tmp_path):
    marker = tmp_path/'real-child.pid'
    code = textwrap.dedent(f'''
        import os,time
        from pathlib import Path
        pid=os.fork()
        if pid:
            end=time.monotonic()+.5
            while not Path({str(marker)!r}).exists() and time.monotonic()<end: time.sleep(.005)
            assert Path({str(marker)!r}).exists()
            os._exit(0)
        os.close(1);os.close(2)
        Path({str(marker)!r}).write_text(str(os.getpid()))
        time.sleep(.35)
    ''')
    result = worker(f'''
        # Observation is deliberately blind. Root Popen and the final kernel
        # witness must still wait/reap; no empty snapshot may certify success.
        owner._process_children=lambda *a,**k: []
        began=time.monotonic()
        result=selected({code!r})
        emit(dict(result=result,elapsed=time.monotonic()-began))
    ''')
    assert_complete(result['result'])
    assert not Path('/proc/'+marker.read_text()).exists()


def test_invalid_selected_mode_cannot_launch(tmp_path):
    marker=tmp_path/'invalid-mode-launch'
    launch_code = f'from pathlib import Path; Path({str(marker)!r}).touch()'
    result=worker(f'''
        error=None
        try:
            owner.run_record_process([sys.executable,'-c', {launch_code!r}],
                1.,.1,absolute_deadline=time.monotonic()+3.,
                process_ownership_mode='subreaper_typo')
        except ValueError as caught: error=str(caught)
        emit(dict(error=error,launched=Path({str(marker)!r}).exists()))
    ''')
    assert result['error'] and not result['launched']


def test_timeout_escalation_and_kernel_reaping_share_original_end():
    code = ('import signal,time;signal.signal(signal.SIGINT,signal.SIG_IGN);'
            'signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(5.)')
    result = worker(f'''
        began=time.monotonic()
        end=began+3.
        result=selected({code!r},wall_timeout_sec=.25,absolute_deadline=end)
        emit(dict(result=result,elapsed=time.monotonic()-began,end=end))
    ''')
    assert_complete(result['result'], -9)
    assert result['result']['timed_out'] is True
    assert result['elapsed'] < 3.
    assert result['result']['deadline_audit']['absolute_deadline'] == result['end']
    assert result['result']['deadline_audit']['deadline_exhausted'] is False


def test_expired_end_refuses_before_any_selected_child(tmp_path):
    marker = tmp_path/'expired-launch'
    code = f'from pathlib import Path;Path({str(marker)!r}).touch()'
    result = worker(f'''
        error=None
        try: selected({code!r},absolute_deadline=time.monotonic()-1.)
        except (ValueError,RuntimeError) as caught: error=str(caught)
        emit(dict(error=error,launched=Path({str(marker)!r}).exists()))
    ''')
    assert result['error'] and not result['launched']


def test_slow_popen_setup_cannot_renew_selected_work_or_cleanup_budget():
    result = worker('''
        real_popen=owner.subprocess.Popen
        def delayed_popen(*args,**kwargs):
            time.sleep(.75)
            return real_popen(*args,**kwargs)
        owner.subprocess.Popen=delayed_popen
        began=time.monotonic()
        end=began+1.2
        result=selected('import time;time.sleep(3.)',wall_timeout_sec=1.,absolute_deadline=end)
        emit(dict(result=result,elapsed=time.monotonic()-began,end=end))
    ''')
    assert result['elapsed'] < 1.2, result
    assert_complete(result['result'], result['result']['return_code'])
    assert result['result']['timed_out'] is True
    assert result['result']['deadline_audit']['absolute_deadline'] == result['end']


@pytest.mark.parametrize('fault', ['permission', 'malformed', 'capacity'])
def test_nontransient_inspection_failure_cannot_be_discharged_by_root_exit(fault):
    result = worker(f'''
        if {fault!r}=='capacity':
            owner.MAX_TRACKED_PROCESSES=0
        else:
            def denied(*args,**kwargs):
                if {fault!r}=='permission': raise PermissionError(errno.EACCES,'fixture procfs denied')
                raise ValueError('fixture malformed procfs children')
            owner._process_children=denied
        result=selected('import time;time.sleep(.15)')
        emit(result)
    ''')
    assert result['return_code'] == 0
    audit = result['process_ownership']
    assert audit['inspection_complete'] is False
    assert audit['kernel_proof']['complete'] is False
    assert audit['inspection_errors'], audit
    if fault != 'capacity':
        assert audit['kernel_proof']['final_echild'] is True
        assert audit['kernel_proof']['state_restored'] is True


def test_changed_identity_after_pidfd_open_is_never_signaled():
    result = worker('''
        original_identity=owner._process_identity
        original_signal=signal.pidfd_send_signal
        count=0
        sent=[]
        def changed_identity(*args,**kwargs):
            global count
            result=original_identity(*args,**kwargs)
            if result is not None:
                count+=1
                result=dict(result,start_ticks=result['start_ticks']+count)
            return result
        def record_signal(*args,**kwargs):
            sent.append(args[1])
            return original_signal(*args,**kwargs)
        owner._process_identity=changed_identity
        signal.pidfd_send_signal=record_signal
        result=selected('import time;time.sleep(.6)',wall_timeout_sec=.15)
        emit(dict(result=result,sent=sent))
    ''')
    assert result['sent'] == []
    audit = result['result']['process_ownership']
    assert audit['inspection_complete'] is False and audit['kernel_proof']['complete'] is False
    assert any('identity changed' in error for error in audit['inspection_errors']), audit


def test_selected_keyboard_interrupt_reaps_child_and_retains_same_end_audit():
    result = worker('''
        import threading
        timer=threading.Timer(.25,lambda:os.kill(os.getpid(),signal.SIGINT))
        end=time.monotonic()+3.
        timer.start()
        try:
            selected('import signal,time;signal.signal(signal.SIGINT,signal.SIG_IGN);'
                     'signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(5.)',
                     absolute_deadline=end)
            raise AssertionError('interrupt was not delivered')
        except KeyboardInterrupt as caught:
            result=dict(ownership=caught.process_ownership,
                        deadline=caught.execution_deadline_audit,end=end,
                        completed=time.monotonic())
        finally:
            timer.cancel()
            timer.join(timeout=1.)
        emit(result)
    ''')
    assert result['ownership']['kernel_proof']['complete'] is True
    assert result['deadline']['absolute_deadline'] == result['end']
    assert result['deadline']['deadline_exhausted'] is False
    assert result['completed'] < result['end']


def test_controlled_scope_rejects_nested_registered_owner_without_stealing_status():
    result = worker('''
        observed=[]
        original_track=owner._track_owned_processes
        attempted=False
        def nested(process,audit):
            global attempted
            original_track(process,audit)
            if attempted: return
            attempted=True
            try: selected('raise AssertionError("nested owner must not launch")')
            except RuntimeError as error: observed.append(str(error))
        owner._track_owned_processes=nested
        result=selected('import time;time.sleep(.15);raise SystemExit(41)')
        emit(dict(result=result,observed=observed))
    ''')
    assert_complete(result['result'], 41)
    assert len(result['observed']) == 1 and 'scope' in result['observed'][0]
