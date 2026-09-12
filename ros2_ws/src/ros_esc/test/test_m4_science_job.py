"""Pure subprocess fixtures for M4 scientific caps; no model or ROS work."""

import importlib.util
import json
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest


ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('m4_science_job_test_owner',
    ROOT/'docs/codex/gesc_gaussian/v2/tools/m4_science_job.py')
job = importlib.util.module_from_spec(spec)
spec.loader.exec_module(job)


def run(tmp_path, code, cap=4.):
    return job.finite_science_job([sys.executable, '-c', code], tmp_path/'worker.log',
        tmp_path/'receipt.json', cap_sec=cap, suite_end=time.monotonic()+20.)


def test_success_is_source_bound_and_outputs_are_exclusive(tmp_path):
    result = run(tmp_path, 'import time; time.sleep(.08); print("complete")')
    assert result['complete'] and result['integrity_passed']
    assert not result['timed_out'] and result['return_code'] == 0
    assert result['source']['kind'] == 'inline_python'
    assert json.loads((tmp_path/'receipt.json').read_text()) == result
    assert result['elapsed_wall_sec'] < 4.
    with pytest.raises(FileExistsError): run(tmp_path, 'print("do not overwrite")')


def test_clean_timeout_escalates_only_owned_group_and_is_scientific_unavailability(tmp_path):
    sentinel = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(10)'], start_new_session=True)
    try:
        result = run(tmp_path,
            'import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(10)', cap=3.3)
        assert result['timed_out'] and not result['complete'] and result['integrity_passed'], result
        assert [row['signal'] for row in result['signals']] == [signal.SIGTERM, signal.SIGKILL]
        assert result['clean_termination'] and result['elapsed_wall_sec'] < 3.3
        assert sentinel.poll() is None
        assert sentinel.pid not in result['process_ownership']['session_ids']
    finally:
        sentinel.terminate()
        sentinel.wait(timeout=3.)


@pytest.mark.parametrize('code,accepted', [
    ('raise RuntimeError("source failure")', False),
    ('import sys; sys.exit(1)', False),
    ('import json,sys; print(json.dumps({"scientific_status":"EVIDENCE_UNAVAILABLE",'
     '"integrity_passed":True,"reason":"no informative reference"})); sys.exit(1)', True),
    ('import json,sys; print(json.dumps({"scientific_status":"EVIDENCE_UNAVAILABLE",'
     '"integrity_passed":False,"reason":"source integrity failed"})); sys.exit(1)', False),
])
def test_nonzero_requires_explicit_scientific_unavailable_packet(tmp_path, code, accepted):
    result = run(tmp_path, code)
    assert not result['complete'] and not result['timed_out']
    assert result['integrity_passed'] is accepted, result


def test_timeout_does_not_hide_unexplained_nonzero_exit(tmp_path):
    code = ('import signal,sys,time; '
            'signal.signal(signal.SIGTERM,lambda *args:sys.exit(1)); time.sleep(10)')
    result = run(tmp_path, code, cap=3.2)
    assert result['timed_out'] and result['return_code'] == 1
    assert result['clean_termination'] and not result['integrity_passed']


def test_pure_worker_must_not_launch_observed_child_process(tmp_path):
    code = ('import subprocess,sys,time; '
            'subprocess.Popen([sys.executable,"-c","import time; time.sleep(10)"],start_new_session=True); '
            'time.sleep(10)')
    result = run(tmp_path, code, cap=3.3)
    assert result['unexpected_observed_descendants']
    assert not result['integrity_passed'] and result['clean_termination']
    assert len(result['process_ownership']['session_ids']) == 2


def test_inspection_failure_remains_invalid_even_when_child_exits_cleanly(tmp_path, monkeypatch):
    def failed(process, audit):
        audit['inspection_complete'] = False
        audit['inspection_errors'].append('fixture procfs denied')
    monkeypatch.setattr(job.owner, '_track_owned_processes', failed)
    result = run(tmp_path, 'import time; time.sleep(.08)')
    assert result['return_code'] == 0 and not result['integrity_passed']
    assert result['process_ownership']['inspection_errors']


def test_near_suite_deadline_reserves_cleanup_without_starting_job(tmp_path, monkeypatch):
    monkeypatch.setattr(job.time, 'monotonic', lambda: 100.)
    def forbidden(*a, **k): pytest.fail('no work budget remains')
    monkeypatch.setattr(job.subprocess, 'Popen', forbidden)
    result = job.finite_science_job([sys.executable, '-c', 'pass'], tmp_path/'log',
        tmp_path/'receipt', cap_sec=10., suite_end=102.)
    assert not result['launched'] and result['timed_out'] and result['integrity_passed']
    assert result['absolute_deadline'] == 102.


def test_shortened_positive_stage_cap_reports_unavailable_without_child(tmp_path, monkeypatch):
    monkeypatch.setattr(job.time, 'monotonic', lambda: 100.)
    def forbidden(*a, **k): pytest.fail('cleanup reserve consumes shortened stage cap')
    monkeypatch.setattr(job.subprocess, 'Popen', forbidden)
    result = job.finite_science_job([sys.executable, '-c', 'pass'], tmp_path/'log',
        tmp_path/'receipt', cap_sec=2., suite_end=120.)
    assert not result['launched'] and result['timed_out'] and result['integrity_passed']
    assert result['absolute_deadline'] == 102.


def test_exhausted_receipt_budget_refuses_without_creating_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(job.time, 'monotonic', lambda: 100.)
    with pytest.raises(TimeoutError, match='unavailable receipt'):
        job.finite_science_job([sys.executable, '-c', 'pass'], tmp_path/'log', tmp_path/'receipt',
                              cap_sec=10., suite_end=100.1)
    assert not (tmp_path/'log').exists() and not (tmp_path/'receipt').exists()


def test_script_bytes_are_retained_in_source_receipt(tmp_path):
    path = tmp_path/'worker.py'
    path.write_text('print("explicit worker")\n')
    result = job.finite_science_job([sys.executable, str(path)], tmp_path/'worker.log',
        tmp_path/'receipt.json', cap_sec=4., suite_end=time.monotonic()+10.)
    assert result['integrity_passed'] and result['complete']
    assert result['source']['path'] == str(path) and result['source']['kind'] == 'script'


@pytest.mark.parametrize('cap', [True, '10', 0., -1., float('nan'), float('inf')])
def test_invalid_cap_rejects_before_output(tmp_path, cap):
    with pytest.raises(ValueError): run(tmp_path, 'pass', cap=cap)
    assert not (tmp_path/'worker.log').exists()
