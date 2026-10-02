"""An expensive/failed optional job cannot own or block the control thread."""

import math
import time

from ros_esc.gesc_v3.worker import NumericalWorker


def ready(worker):
    deadline = time.monotonic() + 5
    while not worker.ready and time.monotonic() < deadline:
        worker.poll()
        time.sleep(0.005)
    assert worker.ready


def result(worker):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        value = worker.poll()
        if value is not None:
            return value
        time.sleep(0.005)
    raise AssertionError('worker did not complete within the finite test deadline')


def test_worker_result_error_and_one_job_limit():
    worker = NumericalWorker()
    try:
        ready(worker)
        assert worker.submit(('first',), math.sqrt, (9,), timeout=2)
        assert not worker.submit(('second',), math.sqrt, (4,), timeout=2)
        got = result(worker)
        assert got.key == ('first',) and got.value == 3 and got.error is None
        assert worker.submit(('bad',), math.sqrt, (-1,), timeout=2)
        assert 'ValueError' in result(worker).error
    finally:
        worker.close()


def test_slow_job_expires_without_waiting_or_late_result():
    worker = NumericalWorker()
    try:
        ready(worker)
        assert worker.submit(('old',), time.sleep, (2,), timeout=0.08)
        ticks = 0
        deadline = time.monotonic() + 1
        expired = None
        while time.monotonic() < deadline:
            began = time.monotonic()
            got = worker.poll()
            assert time.monotonic() - began < 0.2
            ticks += 1
            if got is not None:
                expired = got
                break
            time.sleep(0.005)
        assert ticks > 2
        assert expired.key == ('old',) and expired.error == 'numerical_deadline'
        ready(worker)
        assert worker.submit(('new',), math.sqrt, (16,), timeout=2)
        assert result(worker).value == 4
    finally:
        worker.close()


def test_optional_worker_queue_allocation_failure_does_not_block_startup(monkeypatch):
    from types import SimpleNamespace
    from ros_esc.gesc_v3 import worker as module
    calls = []
    def unavailable(**kwargs):
        calls.append(kwargs)
        raise OSError('simulated semaphore exhaustion')
    monkeypatch.setattr(module.mp, 'get_context', lambda mode: SimpleNamespace(Queue=unavailable))
    instance = module.NumericalWorker(clock=lambda: 10.)
    try:
        assert instance.ready is False and instance.job is None
        result = instance.poll()
        assert result.error.startswith('numerical_process_unavailable:')
        assert instance.submit(('optional',), time.sleep, (.01,)) is False
        assert instance.poll() is None
        assert len(calls) == 1  # no tight retry loop at the same clock value
    finally:
        instance.close()


def test_slow_numerical_import_finishes_before_first_job_budget(tmp_path):
    """Reproduce a cold import longer than the real 0.5 s coherence budget."""
    import json
    import os
    import subprocess
    import sys

    # Spawned workers run sitecustomize too. Delay the actual SciPy import,
    # without mocking the worker handshake, queue, deadline or numerical job.
    (tmp_path/'sitecustomize.py').write_text('''
import sys, time
class DelayScipy:
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'scipy.integrate':
            time.sleep(.75)
        return None
sys.meta_path.insert(0, DelayScipy())
''')
    script = '''
import json, math, time
from ros_esc.gesc_v3.worker import NumericalWorker
from ros_esc.gesc_v3.numerics.rolling import (
    RollingGesc, DirectionObservation, DemodulatedSample, compute_coherence)
rolling = RollingGesc()
for i in range(66):
    stamp = 1_000_000_000 + i*200_000_000
    observation = DirectionObservation(i, stamp, stamp, 0., i*2*math.pi/15)
    rolling.update(DemodulatedSample(observation, (1., .2)))
job = rolling.coherence_job()
assert job is not None
began = time.monotonic()
worker = NumericalWorker()
try:
    deadline = began + 8
    polls = 0
    while not worker.ready and time.monotonic() < deadline:
        assert worker.job is None
        assert not worker.submit(('premature',), compute_coherence, (job,), timeout=.5)
        poll_start = time.monotonic()
        assert worker.poll() is None
        assert time.monotonic()-poll_start < .2
        polls += 1
        time.sleep(.005)
    assert worker.ready
    ready_elapsed = time.monotonic()-began
    pid = worker.process.pid
    started = time.monotonic()
    assert worker.submit(('coherence',), compute_coherence, (job,), timeout=.5)
    result = None
    while result is None and time.monotonic()-started < 2:
        result = worker.poll()
        time.sleep(.005)
    assert result is not None and result.error is None, result
    assert dict(result.value.values)['qualified']
    assert worker.process.pid == pid and worker.ready
    assert ready_elapsed >= .75 and polls > 2
    print(json.dumps(dict(ready_elapsed=ready_elapsed,
                         job_elapsed=time.monotonic()-started, polls=polls)))
finally:
    worker.close()
'''
    environment = dict(os.environ, PYTHONPATH=str(tmp_path)+os.pathsep+
                       os.environ.get('PYTHONPATH', ''))
    completed = subprocess.run([sys.executable, '-c', script], env=environment,
                               capture_output=True, text=True, timeout=12)
    assert completed.returncode == 0, completed.stdout+completed.stderr
    receipt = json.loads(completed.stdout)
    assert receipt['ready_elapsed'] >= .75
    assert receipt['job_elapsed'] < .5


def test_worker_dies_when_parent_is_killed(tmp_path):
    """A hard-killed control owner cannot leave a worker waiting on its queue."""
    import os
    from pathlib import Path
    import signal
    import subprocess
    import sys
    import pytest
    if not sys.platform.startswith('linux'):
        pytest.skip('Linux parent-death signal contract')
    script = tmp_path/'owner.py'
    pidfile = tmp_path/'worker.pid'
    script.write_text('''
import sys, time
from pathlib import Path
from ros_esc.gesc_v3.worker import NumericalWorker
if __name__ == '__main__':
    worker = NumericalWorker()
    while not worker.ready:
        worker.poll()
        time.sleep(.01)
    Path(sys.argv[1]).write_text(str(worker.process.pid))
    time.sleep(30)
''')
    owner = subprocess.Popen([sys.executable, str(script), str(pidfile)])
    child = None
    try:
        deadline = time.monotonic() + 5
        while not pidfile.exists() and time.monotonic() < deadline:
            time.sleep(.01)
        assert pidfile.exists()
        child = int(pidfile.read_text())
        owner.kill()
        owner.wait(timeout=3)
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            path = Path(f'/proc/{child}/stat')
            if not path.exists():
                return
            stat = path.read_text()
            if stat[stat.rfind(')') + 2] in 'ZX':
                return
            time.sleep(.01)
        raise AssertionError('worker survived its killed parent')
    finally:
        if owner.poll() is None:
            owner.kill()
        owner.wait(timeout=3)
        if child is not None:
            try:
                os.kill(child, signal.SIGKILL)
            except ProcessLookupError:
                pass
