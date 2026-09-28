"""Bounded catch-up for independently delivered simulation clocks and inputs."""

from collections import deque
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Delivery:
    stamp: float
    value: object
    receipt: float
    steady: float
    available_at: float


class ClockDelivery:
    """Hold inputs, never authorize future data or rewrite their timestamps.

    Gazebo's observed 10 Hz clock can trail a 30 Hz sensor message. A 125 ms
    maximum lead covers one such clock interval with 25 ms margin; it is a
    buffering bound, not permission to use future input. The existing 0.5 s
    expiry still bounds source and monotonic receipt age. Thirty-two records
    retain all 30 Hz odometry over that expiry with headroom, without a FIFO
    that can grow under a frozen clock. Old/duplicate stamps never renew age.
    """

    def __init__(self, expiry=0.5, max_lead=0.125, capacity=32):
        if not (0 < max_lead <= expiry and capacity > 0):
            raise ValueError('invalid clock delivery bounds')
        self.expiry, self.max_lead = expiry, max_lead
        self.pending = deque(maxlen=capacity)
        self.last_stamp = -math.inf

    def add(self, stamp, value, now, steady, *, available_at=None):
        # Source identity stays distinct from the clock threshold: a received
        # batch may contain several source stamps with the same receipt time.
        available_at = stamp if available_at is None else available_at
        if (not all(math.isfinite(v) for v in (stamp, now, steady, available_at))
                or stamp <= self.last_stamp
                or not now-self.expiry <= stamp <= available_at
                or available_at-now > self.max_lead):
            return False
        self.last_stamp = stamp
        self.pending.append(Delivery(stamp, value, now, steady, available_at))
        return True

    def ready(self, now, steady):
        ready, pending = [], deque(maxlen=self.pending.maxlen)
        for record in self.pending:
            if (not 0 <= steady-record.steady <= self.expiry
                    or now-record.stamp > self.expiry):
                continue
            if record.available_at <= now:
                ready.append(record)
            else:
                pending.append(record)
        self.pending = pending
        return ready

    def clear(self):
        self.pending.clear()
