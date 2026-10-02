"""Optional Pi-local process lease, independent of data validity and ROS.

The physical parent supplies these environment variables. Gazebo has no lease.
Call ``check_guard`` before each control callback and ``tick`` only after its
command was published successfully (acquisition: after loop progress). This is
not a network/SSH heartbeat and has no research or run-duration deadline.
"""
from __future__ import annotations

import os
from pathlib import Path
import signal
import socket
import sys
import time


def bind_parent_death(expected_parent: int):
    """On Linux stop a child when its original owner dies, including a race.

    Numerical workers also use this: multiprocessing's daemon flag only helps
    on orderly parent shutdown. Other supported platforms keep that behavior.
    """
    if not sys.platform.startswith("linux"):
        return
    import ctypes
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signal.SIGKILL, 0, 0, 0) != 0:  # PR_SET_PDEATHSIG
        raise OSError(ctypes.get_errno(), "PR_SET_PDEATHSIG failed")
    if os.getppid() != expected_parent:
        os.kill(os.getpid(), signal.SIGKILL)


class LeaseClient:
    def __init__(self, role: str, *, required: bool = False):
        if role not in {"controller", "acquisition"}:
            raise ValueError("unsupported physical process role")
        self.role = role
        self.socket = None
        self.path = None
        endpoint = os.environ.get("DSIM_V3_LEASE_SOCKET")
        if not endpoint:
            if required:
                raise RuntimeError("physical acquisition requires its V3 runtime")
            return
        self.guard_pid = int(os.environ["DSIM_V3_GUARD_PID"])
        if self.guard_pid != os.getppid():
            raise RuntimeError("V3 runtime must directly own the leased process")
        self.timeout = float(os.environ.get("DSIM_V3_LEASE_SEC", "1.0"))
        if not 0.1 <= self.timeout <= 10.0:
            raise ValueError("invalid local process lease duration")
        # Imports/ROS initialization have no deadline and cannot start the
        # driver. Arm this local execution lease only at the first actual tick.
        self.last_ack = None
        self.path = str(Path(endpoint).parent / f"{role}-{os.getpid()}.sock")
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.socket.bind(self.path)
        self.socket.connect(endpoint)
        self.socket.setblocking(False)

    def _expired(self):
        # SIGKILL reaches a SIGSTOP'ed guard too. Linux parent-death bindings
        # then stop its actual OpenCR driver, which otherwise keeps heartbeating.
        if os.getppid() == self.guard_pid:
            os.kill(self.guard_pid, signal.SIGKILL)
        raise RuntimeError("physical local process guard stopped progressing")

    @property
    def enabled(self):
        return self.socket is not None

    def check_guard(self):
        if self.socket is None:
            return
        for _ in range(32):
            try:
                payload = self.socket.recv(128).decode("ascii")
            except BlockingIOError:
                break
            except UnicodeError:
                continue
            except OSError:
                self._expired()
            try:
                kind, timestamp = payload.split(":")
                stamp = int(timestamp) / 1e9
            except (ValueError, UnicodeError):
                continue
            now = time.monotonic()
            if kind == "guard" and (self.last_ack is None or self.last_ack <= stamp) and stamp <= now:
                self.last_ack = stamp
        if self.last_ack is not None and time.monotonic() - self.last_ack > self.timeout:
            self._expired()

    def tick(self, *, pulsewidth: int | None = None):
        if self.socket is None:
            return
        message = f"{self.role}:{time.monotonic_ns()}"
        if self.role == "acquisition":
            if pulsewidth is None or not 1280 <= pulsewidth <= 1720:
                raise ValueError("acquisition needs a bounded servo pulse")
            message += f":{int(pulsewidth)}"
        try:
            self.socket.send(message.encode("ascii"))
            if self.last_ack is None:
                self.last_ack = time.monotonic()
        except BlockingIOError:
            # A full local queue does not renew either peer's lease.
            pass
        except OSError:
            self._expired()

    def close(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None
        if self.path is not None:
            Path(self.path).unlink(missing_ok=True)


if __name__ == "__main__":
    # A fresh interpreter avoids Python preexec_fn in the multithreaded pigpio
    # parent. exec preserves this PID and parent-death binding for the actual
    # OpenCR executable; no intermediate ros2 run/launch process remains.
    if len(sys.argv) < 3:
        raise SystemExit("usage: process_lease PARENT_PID EXECUTABLE [ARG ...]")
    bind_parent_death(int(sys.argv[1]))
    os.execvpe(sys.argv[2], sys.argv[2:], os.environ)
