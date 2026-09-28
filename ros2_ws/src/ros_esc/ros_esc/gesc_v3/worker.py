"""One optional numerical process; computation never owns control state."""

from dataclasses import dataclass
import multiprocessing as mp
import queue
import time


def _serve(requests, results):
    """Top-level spawn target. No ROS initialization or inherited node handles."""
    results.put(('ready', None, None))
    while True:
        request = requests.get()
        if request is None:
            return
        key, function, args = request
        try:
            results.put(('result', key, function(*args)))
        except Exception as exc:  # a rejected fit is data, not a controller crash
            results.put(('error', key, f'{type(exc).__name__}: {exc}'))


@dataclass(frozen=True)
class JobResult:
    key: tuple
    value: object = None
    error: str | None = None


class NumericalWorker:
    """One in-flight job, no pending FIFO, monotonic expiry and bounded cleanup."""

    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.context = mp.get_context('spawn')
        self.process = None
        self.requests = None
        self.results = None
        self.ready = False
        self.job = None
        self.closed = False
        self.retired = []
        self.start_error = None
        self.retry_at = 0.
        self._start()

    def _start(self):
        if self.closed:
            return
        self.requests = self.results = self.process = None
        try:
            self.requests = self.context.Queue(maxsize=1)
            self.results = self.context.Queue(maxsize=1)
            self.process = self.context.Process(target=_serve,
                                                args=(self.requests, self.results),
                                                daemon=True)
            self.process.start()
        except (OSError, RuntimeError) as error:
            self.start_error = f'numerical_process_unavailable: {error}'
            self.process = None
            self.retry_at = self.clock()+1.
            for channel in (self.requests, self.results):
                if channel is not None:
                    channel.cancel_join_thread()
                    channel.close()
            self.requests = self.results = None
        self.ready = False

    def submit(self, key, function, args=(), timeout=0.5):
        """Do not queue work behind another job or while a child initializes."""
        if self.closed or self.job is not None or not self.ready:
            return False
        if timeout <= 0:
            raise ValueError('job deadline must be positive')
        self.requests.put_nowait((tuple(key), function, tuple(args)))
        self.job = (tuple(key), self.clock() + timeout)
        return True

    def _retire(self):
        if self.process is not None:
            if self.process.is_alive():
                self.process.terminate()
            self.retired.append(self.process)
        for channel in (self.requests, self.results):
            if channel is not None:
                channel.cancel_join_thread()
                channel.close()
        self.process = None
        self.ready = False
        self.job = None

    def poll(self):
        """Never wait for child execution. Expired results cannot commit late."""
        for child in tuple(self.retired):
            if not child.is_alive():
                child.join(timeout=0)
                self.retired.remove(child)
        if self.closed:
            return None
        if self.process is None:
            error = self.start_error
            self.start_error = None
            if self.clock() >= self.retry_at:
                self._start()
            return JobResult((), error=error) if error else None
        if self.job is not None and self.clock() >= self.job[1]:
            key = self.job[0]
            self._retire()
            self._start()
            return JobResult(key, error='numerical_deadline')
        if self.process is not None and not self.process.is_alive():
            key = self.job[0] if self.job else ()
            self._retire()
            self._start()
            return JobResult(key, error='numerical_process_exited')
        try:
            kind, key, payload = self.results.get_nowait()
        except queue.Empty:
            return None
        if kind == 'ready':
            self.ready = True
            return None
        if self.job is None or key != self.job[0]:
            return None
        self.job = None
        return JobResult(key, value=payload if kind == 'result' else None,
                         error=payload if kind == 'error' else None)

    def close(self):
        self.closed = True
        self._retire()
        for child in self.retired:
            child.join(timeout=0.5)
            if child.is_alive():
                child.kill()
                child.join(timeout=0.5)
        self.retired.clear()
