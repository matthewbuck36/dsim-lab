"""Focused tests for callback-safe process signal handling."""

import signal

from ros_esc.deferred_signal_shutdown import DeferredSignalShutdown


def test_signal_request_is_deferred_and_handlers_are_restored(monkeypatch):
    installed = {}
    calls = []
    previous = {
        signal.SIGINT: object(),
        signal.SIGTERM: object(),
    }

    monkeypatch.setattr(
        signal,
        'getsignal',
        lambda signum: previous[signum],
    )

    def capture_handler(signum, handler):
        calls.append((signum, handler))
        installed[signum] = handler

    monkeypatch.setattr(signal, 'signal', capture_handler)

    shutdown = DeferredSignalShutdown()
    with shutdown:
        assert not shutdown.requested
        installed[signal.SIGINT](signal.SIGINT, None)
        assert shutdown.requested

    assert calls[:2] == [
        (signal.SIGINT, shutdown.request),
        (signal.SIGTERM, shutdown.request),
    ]
    assert calls[2:] == [
        (signal.SIGINT, previous[signal.SIGINT]),
        (signal.SIGTERM, previous[signal.SIGTERM]),
    ]
