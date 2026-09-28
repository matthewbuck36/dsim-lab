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
