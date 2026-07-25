"""Defer process signals until the current Python callback has returned."""

import signal
import threading


class DeferredSignalShutdown:
    """
    Turn SIGINT/SIGTERM into a loop-visible shutdown request.

    Python's default SIGINT handler raises ``KeyboardInterrupt`` at an arbitrary
    bytecode boundary. ROS callbacks that are converting or publishing large
    messages can therefore be unwound while native middleware code is active.
    This handler records the request instead, allowing a single-threaded
    executor callback to return before node teardown begins.
    """

    def __init__(self):
        self._requested = threading.Event()
        self._previous_handlers = {}

    @property
    def requested(self):
        """Return whether SIGINT, SIGTERM, or a caller requested shutdown."""
        return self._requested.is_set()

    def request(self, _signum=None, _frame=None):
        """Record a shutdown request without touching the ROS context."""
        self._requested.set()

    def __enter__(self):
        for signum in (signal.SIGINT, signal.SIGTERM):
            self._previous_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, self.request)
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        for signum, handler in self._previous_handlers.items():
            signal.signal(signum, handler)
        self._previous_handlers.clear()
