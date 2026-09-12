"""Actual Humble ros2run delivery with finite, ordered recorder fixtures.

No ROS graph, bag, Gazebo or hardware is started. Each owner is isolated in a
bounded Python worker. M4_SHUTDOWN_OWNER_PATH permits the retained exact v2
source to reproduce its missing recorder SIGINT without editing that source.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest


PREFIX = '''
import ctypes, errno, importlib.util, json, os, signal, subprocess, sys, time
from pathlib import Path
from ros_esc.scenario_runner import run_scenario as owner
if os.environ.get('M4_SHUTDOWN_OWNER_PATH'):
    spec=importlib.util.spec_from_file_location(
        'ros_esc.scenario_runner.m4_retained_shutdown_owner',
        os.environ['M4_SHUTDOWN_OWNER_PATH'])
    owner=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(owner)
owner.CANCEL_ESCALATION_SEC=.15
MODE=os.environ.get('M4_SHUTDOWN_MODE','subreaper_group_v3')
def emit(value):
    print('M4_SHUTDOWN_RESULT='+json.dumps(value),flush=True)
def selected(command, **kwargs):
    return owner.run_record_process(command,kwargs.pop('work',1.2),
        kwargs.pop('grace',1.2),process_ownership_mode=MODE,
        absolute_deadline=kwargs.pop('end',time.monotonic()+5.),**kwargs)
'''


def worker(code, *, timeout=14.):
    process = subprocess.run([sys.executable, '-c', PREFIX + textwrap.dedent(code)],
        capture_output=True, text=True, timeout=timeout, start_new_session=True)
    assert process.returncode == 0, process.stdout[-5000:]+process.stderr[-5000:]
    packets = [line.partition('=')[2] for line in process.stdout.splitlines()
               if line.startswith('M4_SHUTDOWN_RESULT=')]
    assert len(packets) == 1, process.stdout[-5000:]+process.stderr[-5000:]
    return json.loads(packets[0])


def assert_proof(result):
    audit = result['process_ownership']
    assert audit['mode'] == 'subreaper_group_v3', audit
    assert audit['inspection_complete'] is True, audit
    assert not audit['inspection_errors'], audit
    for key in ('baseline_echild', 'subreaper_verified', 'root_reaped',
                'final_echild', 'scope_exclusive', 'sigchld_valid', 'state_restored', 'complete'):
        assert audit['kernel_proof'][key] is True, (key, audit)


MARKER_SUPPORT = '''
def mark(event, **fields):
    row=dict(event=event,pid=os.getpid(),sid=os.getsid(0),pgid=os.getpgid(0),
             monotonic=time.monotonic(),**fields)
    descriptor=os.open(str(log),os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
    try: os.write(descriptor,(json.dumps(row)+'\\n').encode())
    finally: os.close(descriptor)
'''


def recording_hierarchy(tmp_path):
    log = tmp_path/'events.jsonl'
    child = tmp_path/'resource.py'
    child.write_text('import json,os,signal,sys,time\nfrom pathlib import Path\n'
        'log=Path(sys.argv[1]);role=sys.argv[2];requested=False\n'+MARKER_SUPPORT+'''
def stop(signum, frame):
    global requested
    mark(role+'_signal',signum=signum,premature=not (log.parent/(role+'_stop_allowed')).exists())
    requested=True
signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
mark(role+'_ready')
end=time.monotonic()+9.
while not requested and time.monotonic()<end: time.sleep(.01)
if not requested: mark(role+'_expired');sys.exit(88)
if role=='bag': time.sleep(.10);mark('bag_flushed')
mark(role+'_exit')
''')
    recorder = tmp_path/'recorder'
    recorder.write_text('#!'+sys.executable+'\n'
        'import json,os,signal,subprocess,sys,time\nfrom pathlib import Path\n'
        f'log=Path({str(log)!r});requested=False\n'+MARKER_SUPPORT+f'''
def stop(signum, frame):
    global requested
    if not requested: mark('recorder_signal',signum=signum)
    requested=True
signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
target=subprocess.Popen([sys.executable,{str(child)!r},str(log),'target'],start_new_session=True)
bag=subprocess.Popen([sys.executable,{str(child)!r},str(log),'bag'],start_new_session=True)
mark('recorder_ready',target_pid=target.pid,bag_pid=bag.pid)
end=time.monotonic()+8.
while not requested and time.monotonic()<end: time.sleep(.01)
if not requested: mark('recorder_expired');sys.exit(88)
mark('final_zero')
time.sleep(.40)
(log.parent/'target_stop_allowed').touch();target.send_signal(signal.SIGTERM)
target.wait(timeout=1.);mark('target_stopped')
time.sleep(.20)
(log.parent/'bag_stop_allowed').touch();bag.send_signal(signal.SIGINT)
bag.wait(timeout=1.);mark('bag_stopped')
(log.parent/'finalized.json').write_text(json.dumps(dict(final_zero=True,target=target.returncode,bag=bag.returncode)))
mark('finalized')
''')
    recorder.chmod(0o700)
    # This is the actual installed wrapper owner, not a replacement that happens
    # to share its current signal behavior. No package lookup or ROS is needed.
    command = [sys.executable, '-c',
        'from ros2run.api import run_executable;import sys;'
        'sys.exit(run_executable(path=sys.argv[1],argv=[]))', str(recorder)]
    return command, log


def test_actual_ros2run_shutdown_finalizes_in_order_without_signaling_resource_sessions(tmp_path):
    command, log = recording_hierarchy(tmp_path)
    sentinel = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(12.)'],
                                start_new_session=True)
    try:
        packet = worker(f'''
            started=time.monotonic();end=started+5.
            result=selected({command!r},end=end)
            emit(dict(result=result,elapsed=time.monotonic()-started,end=end,
                      finished=time.monotonic()))
        ''')
        rows = [json.loads(line) for line in log.read_text().splitlines()]
        # Retain exact fixture/owner evidence outside pytest temporary state.
        evidence = os.environ.get('M4_SHUTDOWN_EVIDENCE')
        if evidence:
            with Path(evidence).open('x') as stream:
                json.dump(dict(packet=packet,events=rows),stream,indent=2)
        received = [r for r in rows if r['event']=='recorder_signal']
        assert received and received[0]['signum']==2, (received,packet,rows)
        assert (tmp_path/'finalized.json').exists(), (packet,rows)
        assert json.loads((tmp_path/'finalized.json').read_text()) == {
            'final_zero': True, 'target': 0, 'bag': 0}
        assert packet['result']['return_code'] == 0, packet
        assert packet['finished'] <= packet['end'], packet
        assert_proof(packet['result'])
        events=[r['event'] for r in rows]
        ordered=['recorder_signal','final_zero','target_signal','target_exit',
                 'target_stopped','bag_signal','bag_flushed','bag_exit','bag_stopped','finalized']
        assert [events.index(e) for e in ordered] == sorted(events.index(e) for e in ordered),rows
        assert not any(r.get('premature') for r in rows), rows
        signals=packet['result']['process_ownership']['signals']
        groups=[r for r in signals if r.get('transport')=='killpg_unreaped_root']
        assert len(groups)==1 and groups[0]['signal']==2, signals
        assert groups[0]['pidfd'] is False and groups[0]['no_reap_guard'] is True, groups
        assert groups[0]['phase']=='graceful' and groups[0]['sent'] is True, groups
        assert groups[0]['monotonic'] <= received[0]['monotonic'], (groups,received)
        assert not any(r['signal'] in (15,9) for r in signals), signals
        ready=next(r for r in rows if r['event']=='recorder_ready')
        resources={ready['target_pid'],ready['bag_pid']}
        assert not resources.intersection(r.get('pid',r.get('leader_identity',{}).get('pid'))
                                          for r in signals), signals
        assert sentinel.poll() is None
        assert sentinel.pid not in packet['result']['process_ownership']['session_ids']
    finally:
        sentinel.terminate();sentinel.wait(timeout=2.)


@pytest.mark.parametrize('field', ['pid','start_ticks','parent_pid','session_id','process_group_id'])
def test_original_root_identity_guard_rejects_substitution_without_group_send(field):
    packet=worker(f'''
        original=owner._process_identity;groups=[];attempted=False
        call_group=owner._SubreaperOwner._signal_initial_root_group
        def guarded(self):
            global attempted
            attempted=True
            def changed(pid,**kwargs):
                result=original(pid,**kwargs)
                if result and pid==self.process.pid:
                    result=dict(result);result[{field!r}]+=1
                return result
            owner._process_identity=changed
            try: return call_group(self)
            finally: owner._process_identity=original
        owner._SubreaperOwner._signal_initial_root_group=guarded
        real_killpg=os.killpg
        def checked_group(*args):
            groups.append(args);return real_killpg(*args)
        os.killpg=checked_group
        result=selected([sys.executable,'-c','import time;time.sleep(3.)'],work=.20,grace=.25)
        emit(dict(result=result,groups=groups,attempted=attempted))
    ''')
    assert packet['attempted'] and packet['groups']==[],packet
    audit=packet['result']['process_ownership']
    assert audit['kernel_proof']['complete'] is False and audit['inspection_errors'],audit
    group=next(r for r in audit['signals'] if r.get('transport')=='killpg_unreaped_root')
    assert not group['sent'] and 'guard failed' in group['error'],group


def test_permission_failure_is_retained_without_weaker_graceful_fallback():
    packet=worker('''
        attempts=[]
        def denied(*args):
            attempts.append(args);raise PermissionError(errno.EPERM,'injected group permission failure')
        os.killpg=denied
        result=selected([sys.executable,'-c','import time;time.sleep(3.)'],work=.20,grace=.25)
        emit(dict(result=result,attempts=attempts))
    ''')
    assert len(packet['attempts'])==1,packet
    audit=packet['result']['process_ownership']
    assert not audit['kernel_proof']['complete'] and audit['inspection_errors'],audit
    assert not any(r['signal']==2 and r.get('pidfd') for r in audit['signals']),audit
    group=next(r for r in audit['signals'] if r.get('transport')=='killpg_unreaped_root')
    assert not group['sent'] and 'PermissionError' in group['error'],group


def test_reaped_root_uses_adopted_pidfd_without_stale_group_signal(tmp_path):
    marker=tmp_path/'orphan.json'
    code=textwrap.dedent(f'''
        import json,os,signal,time
        from pathlib import Path
        pid=os.fork()
        if pid:
            end=time.monotonic()+1.
            while not Path({str(marker)!r}).exists() and time.monotonic()<end:time.sleep(.005)
            os._exit(0)
        os.setsid();os.close(1);os.close(2)
        signal.signal(signal.SIGINT,signal.SIG_IGN);signal.signal(signal.SIGTERM,signal.SIG_IGN)
        Path({str(marker)!r}).write_text(json.dumps(dict(pid=os.getpid(),sid=os.getsid(0))))
        time.sleep(4.)
    ''')
    packet=worker(f'''
        groups=[];real_killpg=os.killpg
        def checked(*args):groups.append(args);return real_killpg(*args)
        os.killpg=checked
        result=selected([sys.executable,'-c',{code!r}],grace=.25)
        emit(dict(result=result,groups=groups))
    ''')
    assert packet['groups']==[],packet
    assert_proof(packet['result'])
    assert packet['result']['return_code']==0
    audit=packet['result']['process_ownership']
    assert any(r.get('context')=='root_already_reaped_use_adopted_pidfds'
               for r in audit['signals']),audit
    assert any(r['signal']==9 and r.get('pidfd') for r in audit['signals']),audit
    assert not Path('/proc/'+str(json.loads(marker.read_text())['pid'])).exists()


def test_foreign_wait_is_detected_before_group_delivery():
    packet=worker('''
        original=owner._SubreaperOwner._signal_initial_root_group
        groups=[];stolen=[]
        real_killpg=os.killpg
        def checked(*args):groups.append(args);return real_killpg(*args)
        os.killpg=checked
        def foreign_wait(self):
            # Violate the documented precondition explicitly: consume this
            # root's kernel status without updating its Popen returncode.
            os.kill(self.process.pid,signal.SIGKILL)
            stolen.append(os.waitpid(self.process.pid,0))
            return original(self)
        owner._SubreaperOwner._signal_initial_root_group=foreign_wait
        result=selected([sys.executable,'-c','import time;time.sleep(3.)'],work=.20,grace=.25)
        emit(dict(result=result,groups=groups,stolen=stolen))
    ''')
    assert packet['stolen'] and packet['groups']==[],packet
    audit=packet['result']['process_ownership']
    assert not audit['kernel_proof']['complete'],audit
    assert any('wait-owned' in r for r in audit['inspection_errors']),audit


def test_root_exit_after_guard_keeps_unreaped_group_pinned(tmp_path):
    received=tmp_path/'child_received'
    ready=tmp_path/'child_ready'
    code=textwrap.dedent(f'''
        import os,signal,time
        from pathlib import Path
        if os.fork()==0:
            os.close(1);os.close(2)
            def stop(signum,frame):
                Path({str(received)!r}).write_text(str(signum));os._exit(0)
            signal.signal(signal.SIGINT,stop)
            Path({str(ready)!r}).touch()
            time.sleep(4.);os._exit(88)
        time.sleep(4.)
    ''')
    packet=worker(f'''
        real_killpg=os.killpg;guards=[]
        def exit_between_guard_and_send(group,signum):
            registered=owner._ACTIVE_SUBREAPER.process
            assert registered.pid==group and registered.returncode is None
            # The group leader exits after the production guard, but its wait
            # status remains unconsumed. Its child must still receive SIGINT.
            os.kill(group,signal.SIGKILL)
            end=time.monotonic()+.5
            while time.monotonic()<end:
                state=Path('/proc/'+str(group)+'/stat').read_text().split(') ')[1][0]
                if state=='Z':break
                time.sleep(.005)
            assert state=='Z' and registered.returncode is None
            status=os.waitid(os.P_PID,group,os.WEXITED|os.WNOHANG|os.WNOWAIT)
            assert status.si_pid==group
            guards.append(dict(pid=group,zombie_unreaped=True))
            return real_killpg(group,signum)
        os.killpg=exit_between_guard_and_send
        result=selected([sys.executable,'-c',{code!r}],work=.35,grace=.35)
        emit(dict(result=result,guards=guards))
    ''')
    assert_proof(packet['result'])
    assert packet['result']['return_code']==-9 and len(packet['guards'])==1,packet
    assert ready.exists() and received.read_text()=='2'
    assert not any(r['signal'] in (15,9) for r in packet['result']['process_ownership']['signals'])


def test_native_no_cld_wait_rejected_before_launch(tmp_path):
    marker=tmp_path/'forbidden'
    packet=worker(f'''
        class Action(ctypes.Structure):
            _fields_=[('handler',ctypes.c_void_p),('mask',ctypes.c_ulong*16),
                      ('flags',ctypes.c_int),('restorer',ctypes.c_void_p)]
        libc=ctypes.CDLL(None,use_errno=True);old=Action();changed=Action()
        assert libc.sigaction(signal.SIGCHLD,None,ctypes.byref(old))==0
        ctypes.memmove(ctypes.byref(changed),ctypes.byref(old),ctypes.sizeof(old))
        changed.flags|=2
        assert libc.sigaction(signal.SIGCHLD,ctypes.byref(changed),None)==0
        error=None
        try:selected([sys.executable,'-c',"from pathlib import Path;Path({str(marker)!r}).touch()"])
        except RuntimeError as caught:error=str(caught)
        finally:assert libc.sigaction(signal.SIGCHLD,ctypes.byref(old),None)==0
        emit(dict(error=error,launched=Path({str(marker)!r}).exists()))
    ''')
    assert packet['error'] and not packet['launched'],packet


def test_keyboard_interrupt_and_forced_escalation_keep_original_deadline():
    packet=worker('''
        import threading
        timer=threading.Timer(.35,lambda:os.kill(os.getpid(),signal.SIGINT))
        end=time.monotonic()+3.
        timer.start()
        try:
            selected([sys.executable,'-c','import signal,time;'
                'signal.signal(signal.SIGINT,signal.SIG_IGN);'
                'signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(5.)'],end=end,grace=.25)
            raise AssertionError('interruption was not delivered')
        except KeyboardInterrupt as caught:
            packet=dict(ownership=caught.process_ownership,deadline=caught.execution_deadline_audit,
                        end=end,finished=time.monotonic())
        finally:timer.cancel();timer.join(timeout=1.)
        emit(packet)
    ''')
    assert packet['finished']<packet['end'],packet
    assert packet['deadline']['absolute_deadline']==packet['end'],packet
    assert packet['ownership']['kernel_proof']['complete'] is True,packet
    signals=packet['ownership']['signals']
    assert any(r['signal']==9 and r.get('pidfd') for r in signals),signals
    assert sum(r.get('transport')=='killpg_unreaped_root' for r in signals)==1,signals
