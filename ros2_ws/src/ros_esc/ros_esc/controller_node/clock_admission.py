"""Bounded source-clock admission for the existing V2 controller callbacks.

Pose stamps identify acquisitions. State and filter stamps identify publications,
so distinct same-tick revisions retain their singleton publisher order. Exact
repeats never refresh either original receipt. No controller calculation lives
here, and pending samples never replace an admitted sample.
"""

from collections import deque
from copy import deepcopy
from dataclasses import dataclass


FRESHNESS_NS = 500_000_000
MAX_PENDING = 1024


@dataclass(frozen=True)
class ReceivedSample:
    source_ns: int
    receipt_ns: int
    steady_ns: int
    message: object


class ClockAdmission:
    def __init__(self):
        self.pending = {kind: deque() for kind in ('state', 'pose', 'filter')}
        self.frontier = {}

    def clear(self):
        for queue in self.pending.values():
            queue.clear()
        self.frontier.clear()

    def discard(self, kind):
        # Retain the source frontier across input faults: retransmission of an
        # old/contradictory sample cannot restore revoked authorization.
        self.pending[kind].clear()

    def receive(self, kind, source_ns, receipt_ns, steady_ns, message, *, limit_ns,
                fingerprint=None):
        if not -limit_ns <= receipt_ns - source_ns <= limit_ns:
            raise ValueError(f'V2 {kind} source stale or excessively future')
        previous = self.frontier.get(kind)
        payload_key = message if fingerprint is None else fingerprint
        if previous is not None:
            stamp, payload = previous
            if source_ns < stamp:
                raise ValueError(f'V2 {kind} source regressed')
            if source_ns == stamp:
                if payload_key == payload:
                    return False
                if kind == 'pose':
                    raise ValueError('V2 pose source has conflicting duplicate')
        if len(self.pending[kind]) >= MAX_PENDING:
            raise ValueError(f'V2 {kind} pending capacity exceeded')
        frozen = deepcopy(message)
        self.frontier[kind] = (source_ns, deepcopy(payload_key))
        self.pending[kind].append(ReceivedSample(source_ns, receipt_ns, steady_ns, frozen))
        return True

    def covered(self, kind, now_ns, steady_ns, *, limit_ns):
        queue = self.pending[kind]
        admitted = []
        while queue:
            item = queue[0]
            if (not 0 <= now_ns - item.receipt_ns <= limit_ns
                    or not 0 <= steady_ns - item.steady_ns <= limit_ns):
                raise ValueError(f'V2 {kind} original pending receipt stale or regressed')
            if item.source_ns > now_ns:
                break
            if not 0 <= now_ns - item.source_ns <= limit_ns:
                raise ValueError(f'V2 {kind} pending source stale or regressed')
            admitted.append(queue.popleft())
        return admitted
