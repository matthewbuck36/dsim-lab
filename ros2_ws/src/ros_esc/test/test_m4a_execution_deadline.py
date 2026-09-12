"""Independent inclusive-deadline tests; no ROS graph or scientific work."""

import json
import math
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

from ros_esc.scenario_runner import run_scenario as runner


@pytest.fixture(autouse=True)
def no_ros_start(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('plain deadline owner must not initialize ROS or discovery')
    monkeypatch.setattr(runner.rclpy, 'init', forbidden)
    monkeypatch.setattr(runner, 'ensure_ros_daemon', forbidden)


class Clock:
    def __init__(self, now=100.):
        self.now = now
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        assert seconds >= 0
        self.sleeps.append((self.now, seconds))
        self.now += seconds


class Process:
    pid = 733001

    def __init__(self, clock, *, first_error=None, complete=False):
        self.clock = clock
        self.first_error = first_error
        self.complete = complete
        self.returncode = None
        self.waits = []

    def communicate(self, timeout=None):
        assert timeout is not None and math.isfinite(timeout) and timeout >= 0
        self.waits.append((self.clock.now, timeout))
        if self.complete:
            self.returncode = 1
            return 'completed behavioral work\n', None
        self.clock.now += timeout
        if len(self.waits) == 1 and self.first_error is not None:
            raise self.first_error
        raise subprocess.TimeoutExpired(['fixture'], timeout)

    def wait(self, timeout=None):
        self.communicate(timeout=timeout)

    def poll(self):
        return self.returncode


def fake_tree(monkeypatch, *, first_error=None, complete=False, snapshot_delay=0.):
    clock = Clock()
    process = Process(clock, first_error=first_error, complete=complete)
    identities = {pid: dict(pid=pid, state='S', parent_pid=1 if index == 0 else process.pid,
                           process_group_id=pid, session_id=pid, start_ticks=900+index)
                  for index, pid in enumerate((process.pid, process.pid+1))}
    signals, launches = [], []

    def snapshot(pid, **kwargs):
        assert pid == process.pid
        clock.now += snapshot_delay
        return {key: dict(value) for key, value in identities.items()}

    def popen(*args, **kwargs):
        launches.append((args, kwargs))
        return process

    monkeypatch.setattr(runner.time, 'monotonic', clock.monotonic)
    monkeypatch.setattr(runner.time, 'sleep', clock.sleep)
    monkeypatch.setattr(runner.subprocess, 'Popen', popen)
    monkeypatch.setattr(runner, '_snapshot_process_tree', snapshot)
    monkeypatch.setattr(runner, '_process_identity', lambda pid, **kwargs: identities.get(pid))
    monkeypatch.setattr(runner.os, 'killpg', lambda pid, sig: signals.append((pid, sig)))
    monkeypatch.setattr(runner, 'CANCEL_ESCALATION_SEC', 1.)
    return clock, process, identities, signals, launches


@pytest.mark.parametrize('deadline', [float('nan'), float('inf'), -float('inf'),
                                     100., 99., 103., True, '110'])
def test_invalid_expired_or_unreservable_deadline_rejects_before_launch(monkeypatch, deadline):
    _, _, _, _, launches = fake_tree(monkeypatch)
    with pytest.raises((TypeError, ValueError)):
        runner.run_record_process(['fixture'], 60., 1., absolute_deadline=deadline)
    assert not launches


@pytest.mark.parametrize('route', [dict(boundary_state='ESCAPE_REPULSE'),
                                  dict(staged_recovery={})])
def test_deadline_cannot_enter_specialized_native_callback_route(monkeypatch, route):
    _, _, _, _, launches = fake_tree(monkeypatch)
    with pytest.raises(ValueError):
        runner.run_record_process(['fixture'], 60., 1., absolute_deadline=110., **route)
    assert not launches


def test_work_and_all_escalations_share_original_absolute_end(monkeypatch):
    clock, process, _, signals, _ = fake_tree(monkeypatch, snapshot_delay=.25)
    result = runner.run_record_process(['fixture'], 60., 1., absolute_deadline=110.)
    assert process.waits[0] == (100., 6.)  # 1 s grace plus three 1 s escalations reserved.
    assert all(start+duration <= 110. for start, duration in process.waits)
    assert sum(duration for _, duration in process.waits) == pytest.approx(9.75)
    assert clock.now == pytest.approx(110.)
    assert all(start+duration <= 110. for start, duration in clock.sleeps)
    audit = result['deadline_audit']
    assert audit['absolute_deadline'] == 110.
    assert audit['work_deadline'] == 106.
    assert audit['shutdown_reserve_sec'] == 4.
    assert result['timed_out'] is True and audit['deadline_exhausted'] is True
    cancellation = audit['cancellation']
    assert cancellation['absolute_deadline'] == 110.
    assert cancellation['leader_reaped'] is False
    assert cancellation['remaining_owned_count'] == 2
    assert (process.pid+1, signal.SIGKILL) in signals


def test_exception_cleanup_reraises_and_never_renews_original_budget(monkeypatch):
    clock, process, _, _, _ = fake_tree(monkeypatch, first_error=KeyboardInterrupt())
    actual = runner._cancel_scoped_process
    calls = []

    def cancel(*args, **kwargs):
        calls.append(kwargs['absolute_deadline'])
        return actual(*args, **kwargs)

    monkeypatch.setattr(runner, '_cancel_scoped_process', cancel)
    with pytest.raises(KeyboardInterrupt):
        runner.run_record_process(['fixture'], 60., 1., absolute_deadline=110.)
    assert calls == [110.]
    assert clock.now == 110.
    assert all(start+duration <= 110. for start, duration in process.waits)


def test_cleanup_retry_retains_original_deadline(monkeypatch):
    clock, process, _, _, _ = fake_tree(monkeypatch)
    actual = runner._cancel_scoped_process
    calls = []

    def cancel(*args, **kwargs):
        calls.append(kwargs['absolute_deadline'])
        if len(calls) == 1:
            clock.now += 2.5
            raise RuntimeError('fixture cleanup interruption')
        return actual(*args, **kwargs)

    monkeypatch.setattr(runner, '_cancel_scoped_process', cancel)
    with pytest.raises(RuntimeError, match='cleanup interruption'):
        runner.run_record_process(['fixture'], 60., 1., absolute_deadline=110.)
    assert calls == [110., 110.]
    assert clock.now == 110.
    assert all(start+duration <= 110. for start, duration in process.waits)


def test_expired_cleanup_uses_only_nonwaiting_identity_checked_attempts(monkeypatch):
    clock, process, _, signals, _ = fake_tree(monkeypatch)
    result = runner._cancel_scoped_process(process, 10., True, absolute_deadline=100.)
    assert all(duration == 0 for _, duration in process.waits)
    assert not clock.sleeps and clock.now == 100.
    assert (process.pid+1, signal.SIGKILL) in signals
    assert result['audit']['leader_reaped'] is False
    assert result['audit']['remaining_owned_count'] == 2
    assert result['audit']['deadline_exhausted'] is True


def test_unavailable_inspection_never_signals_unknown_group_or_claims_cleanup(monkeypatch):
    _, process, _, signals, _ = fake_tree(monkeypatch)
    monkeypatch.setattr(runner, '_snapshot_process_tree', lambda pid, **kwargs: {})
    result = runner._cancel_scoped_process(process, 1., True, absolute_deadline=100.)
    assert signals == []
    assert result['audit']['inspection_complete'] is False
    assert result['audit']['leader_reaped'] is False


def test_reused_pid_cannot_be_killed_from_old_snapshot(monkeypatch):
    _, process, identities, signals, _ = fake_tree(monkeypatch)
    original = {pid: dict(value) for pid, value in identities.items()}
    for value in identities.values():
        value['start_ticks'] += 1
    monkeypatch.setattr(runner, '_snapshot_process_tree', lambda pid, **kwargs: original)
    result = runner._cancel_scoped_process(process, 1., True, absolute_deadline=100.)
    assert signals == []
    assert result['audit']['leader_reaped'] is False


def test_completed_exit_one_is_preserved_without_behavioral_reinterpretation(monkeypatch):
    _, process, _, _, _ = fake_tree(monkeypatch, complete=True)
    result = runner.run_record_process(['fixture'], 2., 1., absolute_deadline=110.)
    assert result['return_code'] == 1 and result['timed_out'] is False
    assert result['stdout'] == 'completed behavioral work\n'
    assert process.waits == [(100., 2.)]
    assert 'classification' not in result


def test_unselected_plain_result_shape_and_wall_wait_are_unchanged(monkeypatch):
    _, process, _, _, _ = fake_tree(monkeypatch, complete=True)
    result = runner.run_record_process(['fixture'], 60., 1.)
    assert process.waits == [(100., 60.)]
    assert set(result) == {'return_code', 'timed_out', 'stdout', 'session_id',
                           'graceful_boundary_stop', 'boundary_anchor_state', 'boundary_state',
                           'boundary_observed', 'boundary_required_events',
                           'boundary_required_events_observed'}
    assert result['return_code'] == 1


def test_unselected_exception_cleanup_keeps_original_call_contract(monkeypatch):
    _, _, _, _, _ = fake_tree(monkeypatch, first_error=KeyboardInterrupt())
    calls = []

    def legacy_cancel(process, shutdown_grace_sec, drain_output):
        calls.append((process.pid, shutdown_grace_sec, drain_output))

    monkeypatch.setattr(runner, '_cancel_scoped_process', legacy_cancel)
    with pytest.raises(KeyboardInterrupt):
        runner.run_record_process(['fixture'], 60., 1.)
    assert calls == [(Process.pid, 1., True)]


def procfs_reads(monkeypatch, mode):
    """Use real inspection/identity helpers with only kernel file reads supplied."""
    clock = Clock()
    process = Process(clock, complete=True)
    signals = []
    original_read = Path.read_text
    root, child = process.pid, process.pid+1
    child_stat_reads = [0]
    root_stat_reads = [0]

    def stat(pid, ticks=None):
        fields = ['S', str(1 if pid == root else root), str(pid), str(pid)]
        fields += ['0']*15 + [str(ticks if ticks is not None else 900 if pid == root else 901)]
        return f'{pid} (fixture process) ' + ' '.join(fields)

    def read(path, *args, **kwargs):
        name = str(path)
        if not name.startswith((f'/proc/{root}/', f'/proc/{child}/')):
            return original_read(path, *args, **kwargs)
        if process.returncode is not None:
            raise FileNotFoundError(name)
        if name == f'/proc/{root}/stat':
            root_stat_reads[0] += 1
            if mode == 'root-reused-after-partial' and root_stat_reads[0] > 1:
                return stat(root, ticks=1900)
            return stat(root)
        if name == f'/proc/{root}/task/{root}/children':
            if mode in ('children-permission', 'root-reused-after-partial'):
                raise PermissionError(name)
            if mode == 'children-missing-live-parent':
                raise FileNotFoundError(name)
            return str(child)
        if name == f'/proc/{child}/stat':
            child_stat_reads[0] += 1
            if mode == 'child-identity-permission':
                raise PermissionError(name)
            if mode == 'child-identity-permission-after-enumeration' and child_stat_reads[0] > 1:
                raise PermissionError(name)
            if mode == 'child-identity-malformed':
                return 'malformed kernel identity'
            if mode == 'child-disappeared':
                raise FileNotFoundError(name)
            if mode == 'child-disappeared-after-enumeration' and child_stat_reads[0] > 1:
                raise FileNotFoundError(name)
            return stat(child)
        if name == f'/proc/{child}/task/{child}/children':
            return ''
        raise AssertionError('unexpected procfs read: '+name)

    monkeypatch.setattr(Path, 'read_text', read)
    monkeypatch.setattr(runner.time, 'monotonic', clock.monotonic)
    monkeypatch.setattr(runner.time, 'sleep', clock.sleep)
    monkeypatch.setattr(runner.os, 'killpg', lambda pid, sig: signals.append((pid, sig)))
    monkeypatch.setattr(runner, 'CANCEL_ESCALATION_SEC', .1)
    return process, signals


@pytest.mark.parametrize('mode', ['children-permission', 'children-missing-live-parent',
                                  'child-identity-permission', 'child-identity-malformed',
                                  'child-disappeared',
                                  'child-identity-permission-after-enumeration'])
def test_real_procfs_helpers_cannot_hide_unknown_inspection_as_empty_cleanup(monkeypatch, mode):
    process, signals = procfs_reads(monkeypatch, mode)
    result = runner._cancel_scoped_process(process, .1, True, absolute_deadline=101.)
    audit = result['audit']
    assert audit['inspection_complete'] is False
    assert audit['cleanup_complete'] is False
    assert audit['inspection_errors']
    assert audit['remaining_owned_count'] is None  # Unknown is not zero survivors.
    assert any(item['pid'] == process.pid for item in audit['owned_snapshot'])
    assert (process.pid, signal.SIGINT) in signals  # Keep the independently known root.


def test_disappeared_child_is_distinct_from_unknown_kernel_inspection(monkeypatch):
    process, signals = procfs_reads(monkeypatch, 'child-disappeared-after-enumeration')
    result = runner._cancel_scoped_process(process, .1, True, absolute_deadline=101.)
    audit = result['audit']
    assert audit['inspection_complete'] is True and audit['inspection_errors'] == []
    assert audit['leader_reaped'] is True and audit['cleanup_complete'] is True
    assert audit['owned_snapshot_count'] == 2 and audit['remaining_owned_count'] == 0
    assert all(pid == process.pid for pid, _ in signals)


def test_unselected_procfs_failure_behavior_is_unchanged(monkeypatch):
    process, _ = procfs_reads(monkeypatch, 'children-permission')
    assert runner._process_children(process.pid) == []
    process, _ = procfs_reads(monkeypatch, 'child-identity-permission')
    assert runner._process_identity(process.pid+1) is None


def test_partial_snapshot_recheck_cannot_replace_original_root_after_pid_reuse(monkeypatch):
    process, signals = procfs_reads(monkeypatch, 'root-reused-after-partial')
    result = runner._cancel_scoped_process(process, .1, True, absolute_deadline=101.)
    audit = result['audit']
    assert signals == []
    assert audit['owned_snapshot'][0]['start_ticks'] == 900
    assert audit['inspection_complete'] is False and audit['cleanup_complete'] is False


def _stop_fixture_process(process):
    if process.poll() is None:
        process.terminate()
    try:
        process.wait(timeout=2.)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=2.)


def test_real_exit_one_and_output_survive_selected_envelope(monkeypatch):
    monkeypatch.setattr(runner, 'CANCEL_ESCALATION_SEC', .1)
    result = runner.run_record_process(
        [sys.executable, '-c', "print('real work completed'); raise SystemExit(1)"],
        2., .1, absolute_deadline=time.monotonic()+3.)
    assert result['return_code'] == 1 and result['timed_out'] is False
    assert result['stdout'] == 'real work completed\n'


def test_real_nested_session_escalated_without_touching_unrelated_sentinel(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, 'CANCEL_ESCALATION_SEC', .2)
    nested_receipt = tmp_path/'nested.json'
    child_code = (
        'import os,signal,time; '
        'signal.signal(signal.SIGINT,signal.SIG_IGN); '
        'signal.signal(signal.SIGTERM,signal.SIG_IGN); '
        'time.sleep(20)')
    parent_code = (
        'import json,os,pathlib,signal,subprocess,sys,time\n'
        'signal.signal(signal.SIGINT,lambda *_:sys.exit(0))\n'
        f'child=subprocess.Popen([sys.executable,"-c",{child_code!r}], '
        'start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n'
        f'pathlib.Path({str(nested_receipt)!r}).write_text(json.dumps('
        '{"root":os.getpid(),"child":child.pid,"root_sid":os.getsid(0),'
        '"child_sid":os.getsid(child.pid)}))\n'
        'print("owned nested process launched",flush=True)\n'
        'time.sleep(20)\n')
    sentinel = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(20)'],
                                start_new_session=True, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
    nested_identity = None
    started = time.monotonic()
    deadline = started+2.
    try:
        result = runner.run_record_process([sys.executable, '-c', parent_code],
                                           60., .25, absolute_deadline=deadline)
        elapsed = time.monotonic()-started
        assert elapsed <= 2.75  # Scheduling tolerance; blocking budgets tested exactly above.
        receipt = json.loads(nested_receipt.read_text())
        assert receipt['root_sid'] == receipt['root'] == result['session_id']
        assert receipt['child_sid'] == receipt['child'] != receipt['root_sid']
        nested_identity = runner._process_identity(receipt['child'])
        assert nested_identity is None or nested_identity['state'] == 'Z'
        assert sentinel.poll() is None
        audit = result['deadline_audit']['cancellation']
        assert result['timed_out'] is True
        assert audit['leader_reaped'] is True and audit['inspection_complete'] is True
        assert audit['remaining_owned_count'] == 0
        assert audit['owned_snapshot_count'] >= 2
        assert 'owned nested process launched' in result['stdout']
    finally:
        # Bounded fixture cleanup, using only the exact child's captured identity.
        if nested_receipt.exists():
            child_pid = json.loads(nested_receipt.read_text())['child']
            current = runner._process_identity(child_pid)
            if current is not None and current['state'] != 'Z':
                if nested_identity is None:
                    nested_identity = current
                runner._signal_owned_process_group(child_pid, [nested_identity], signal.SIGKILL)
        _stop_fixture_process(sentinel)
