"""Bounded, source-time raw evidence for moving candidate verification.

No direction-confidence decision or augmented objective is used here. Samples
retain the first filter-publication state; that is not acquisition-state truth.
The piecewise-linear measured trajectory supplies integration and confinement.
"""

from bisect import bisect_left
from copy import deepcopy
from dataclasses import dataclass
import math
import statistics

from ros_esc.v2_lifecycle import hash_payload, observation_payload
from ros_esc.v2_stream import time_to_ns
from ros_esc.supervisor_node.state_machine import RotationCostWindow

TAU = 2.0 * math.pi
SECTOR = TAU / 12


@dataclass(frozen=True)
class RawRecord:
    observation: object
    stamp_ns: int
    phase: float
    x: float
    y: float
    raw: float
    filter_state: int
    filter_stamp_ns: int
    fingerprint: str


@dataclass(frozen=True)
class RawCycle:
    start_ns: int
    end_ns: int
    start_phase: float
    end_phase: float
    centroid: tuple
    sector_centroids: tuple
    sector_counts: tuple
    sector_medians: tuple
    minimum: float
    vertices: tuple
    sample_stamps: tuple
    support_stamps: tuple
    qualified: bool


@dataclass(frozen=True)
class MovingEvidence:
    ready: bool = False
    reason: str = 'missing_cycles'
    cycles: tuple = ()
    records: tuple = ()
    sample_ranges: tuple = ()
    summary: object = None
    amplitude: float = 0.0
    disagreement: float = 0.0
    information_floor: float = 1e-6
    informative: bool = False
    diagnostics: tuple = ()


class MovingRawEvidence:
    """Latest-three revolution evidence, with explicit resets and finite caps."""

    def __init__(self, *, max_observations=20000, max_snapshot=4000):
        if max_observations < 4 or max_snapshot < 4:
            raise ValueError('evidence capacities must be at least four')
        self.max_observations = max_observations
        self.max_snapshot = max_snapshot
        self.epoch = None
        self.epoch_start_ns = 0
        self.reset_sequence = 0
        self.reason = ''
        self._poisoned = set()
        self.poison_capacity_exhausted = False
        self.reset('initial')

    def start_epoch(self, epoch, start_ns):
        if self.epoch == epoch:
            if self.epoch_start_ns != start_ns:
                raise ValueError('epoch identity reused with different start')
            return
        self.epoch, self.epoch_start_ns = epoch, start_ns
        self._poisoned.clear()
        self.poison_capacity_exhausted = False
        self.reset('search_epoch')

    def reset(self, reason):
        self.records = []
        self.observation_ids = {}
        self.source_sequences = {}
        self.cycles = []
        self.direction = 0
        self.anchor = None
        self.next_boundary = None
        self.cycle_start = None
        self.reset_sequence += 1
        self.reason = reason

    def revoke(self, stamp_ns):
        # A revoked key cannot be resurrected within this authoritative epoch.
        if len(self._poisoned) >= self.max_observations:
            self.poison_capacity_exhausted = True
            self.reset('revocation_capacity')
            return False
        self._poisoned.add(stamp_ns)
        affected = any(r.stamp_ns == stamp_ns for r in self.records)
        if affected:
            self.reset('source_revoked')
        return affected

    def add(self, observation, filter_state, filter_stamp_ns):
        try:
            stamp = time_to_ns(observation.source_stamp)
            values = (observation.base_x_m, observation.base_y_m,
                      observation.raw_cost, observation.sensor_world_phase_rad)
            if (self.poison_capacity_exhausted or stamp < self.epoch_start_ns or stamp in self._poisoned
                    or observation.observation_id <= 0 or observation.source_sequence <= 0
                    or not observation.raw_cost_valid
                    or not observation.synchronized_valid
                    or not observation.sensor_transform_observed
                    or not all(math.isfinite(v) for v in values)
                    or filter_stamp_ns < stamp):
                return False
            fingerprint = hash_payload(observation_payload(observation))
            if self.records and stamp <= self.records[-1].stamp_ns:
                found = next((r for r in reversed(self.records) if r.stamp_ns == stamp), None)
                if found is not None and found.fingerprint == fingerprint:
                    return False  # never refresh the first filter state/receipt
                if len(self._poisoned) >= self.max_observations:
                    self.poison_capacity_exhausted = True
                else:
                    self._poisoned.add(stamp)
                self.reset('conflicting_observation' if found else 'source_regression')
                return False
            prior_keys = (self.observation_ids.get(observation.observation_id),
                          self.source_sequences.get(observation.source_sequence))
            if any(key is not None and key != stamp for key in prior_keys):
                for key in (*prior_keys, stamp):
                    if key is not None:
                        self.revoke(key)
                self.reset('conflicting_observation')
                return False
            reset_before = self.reset_sequence
            phase = float(observation.sensor_world_phase_rad)
            if self.records:
                previous = self.records[-1]
                delta = math.atan2(math.sin(phase - previous.phase),
                                   math.cos(phase - previous.phase))
                if stamp - previous.stamp_ns > 500_000_000:
                    self.reset('source_gap')
                elif abs(abs(delta) - math.pi) <= 1e-12:
                    self.reset('ambiguous_phase_step')
                elif delta and self.direction and delta * self.direction < -1e-12:
                    self.reset('phase_reversal')
                else:
                    phase = previous.phase + delta
                    if delta and not self.direction:
                        self.direction = 1 if delta > 0 else -1
                        self.next_boundary = self.anchor + self.direction * TAU
            if self.cycle_start is not None and stamp - self.cycle_start[0] > 30_000_000_000:
                self.reset("cycle_timeout")
            if len(self.records) >= self.max_observations:
                self.reset('observation_capacity')
                return False
            record = RawRecord(deepcopy(observation), stamp, phase,
                               float(values[0]), float(values[1]), float(values[2]),
                               int(filter_state), int(filter_stamp_ns), fingerprint)
            self.records.append(record)
            self.observation_ids[observation.observation_id] = stamp
            self.source_sequences[observation.source_sequence] = stamp
            if self.anchor is None:
                self.anchor = phase
                self.cycle_start = (stamp, phase)
            if (self.direction and self.direction * (phase - self.next_boundary) >= -1e-12):
                end = self._crossing(self.next_boundary)
                cycle = self._cycle(self.cycle_start, (end, self.next_boundary))
                self.cycles.append(cycle)
                self.cycle_start = (end, self.next_boundary)
                self.next_boundary += self.direction * TAU
            if self.reset_sequence == reset_before:
                self.reason = ''
            return True
        except (ValueError, OverflowError, TypeError, ArithmeticError):
            self.reset('invalid_or_overflow')
            return False

    def _crossing(self, phase):
        for i, point in enumerate(self.records):
            if self.direction * (point.phase - phase) >= -1e-12:
                if abs(point.phase - phase) <= 1e-12:
                    return point.stamp_ns  # first arrival, including a dwell
                previous = self.records[i - 1]
                fraction = (phase - previous.phase) / (point.phase - previous.phase)
                return previous.stamp_ns + round(fraction * (point.stamp_ns - previous.stamp_ns))
        raise ValueError('unbracketed revolution boundary')

    def _point(self, stamp):
        stamps = [r.stamp_ns for r in self.records]
        index = bisect_left(stamps, stamp)
        if index < len(stamps) and stamps[index] == stamp:
            r = self.records[index]
            return (stamp, r.phase, r.x, r.y)
        if index == 0 or index == len(stamps):
            raise ValueError('no extrapolation')
        a, b = self.records[index - 1:index + 1]
        fraction = (stamp - a.stamp_ns) / (b.stamp_ns - a.stamp_ns)
        return (stamp, a.phase + fraction * (b.phase - a.phase),
                a.x + fraction * (b.x - a.x), a.y + fraction * (b.y - a.y))

    def _cycle(self, start, end):
        lo, hi = start[0], end[0]
        actual = [r for r in self.records if lo <= r.stamp_ns < hi]
        inside = [r for r in self.records if lo < r.stamp_ns < hi]
        vertices = [self._point(lo)] + [(r.stamp_ns, r.phase, r.x, r.y) for r in inside] + [self._point(hi)]
        integral = [0.0, 0.0]
        sector_integral = [[0.0, 0.0, 0.0] for _ in range(12)]
        for a, b in zip(vertices, vertices[1:]):
            dt = (b[0] - a[0]) * 1e-9
            for axis in range(2):
                integral[axis] += dt * (a[axis + 2] / 2 + b[axis + 2] / 2)
            fractions = [0.0, 1.0]
            if b[1] != a[1]:
                low, high = sorted((a[1], b[1]))
                for k in range(math.floor(low / SECTOR) + 1, math.ceil(high / SECTOR)):
                    f = (k * SECTOR - a[1]) / (b[1] - a[1])
                    if 0 < f < 1:
                        fractions.append(f)
            fractions.sort()
            for f, g in zip(fractions, fractions[1:]):
                phase = a[1] + (f + g) / 2 * (b[1] - a[1])
                sector = min(11, int((phase % TAU) / SECTOR))
                duration = dt * (g - f)
                sector_integral[sector][2] += duration
                for axis in range(2):
                    v = a[axis + 2] + (f + g) / 2 * (b[axis + 2] - a[axis + 2])
                    sector_integral[sector][axis] += duration * v
        costs = [[] for _ in range(12)]
        for record in actual:
            sector = min(11, int((record.phase % TAU) / SECTOR))
            costs[sector].append(record.raw)
        duration = (hi - lo) * 1e-9
        stamps = [r.stamp_ns for r in self.records]
        left = max(0, bisect_left(stamps, lo) - (lo not in stamps))
        right = min(len(stamps) - 1, bisect_left(stamps, hi))
        qualified = (0 < duration <= 30 and all(len(c) >= 2 for c in costs)
                     and all(v[2] > 0 for v in sector_integral))
        centroid = tuple(v / duration for v in integral)
        sectors = tuple((v[0] / v[2], v[1] / v[2]) if v[2] else (0., 0.) for v in sector_integral)
        medians = tuple(statistics.median(c) if c else 0. for c in costs)
        if not all(math.isfinite(v) for v in (*centroid, *(x for pair in sectors for x in pair))):
            raise ValueError('nonfinite integrated geometry')
        return RawCycle(lo, hi, start[1], end[1], centroid, sectors,
                        tuple(len(c) for c in costs), medians,
                        min((r.raw for r in actual), default=0.),
                        tuple((v[2], v[3]) for v in vertices),
                        tuple(r.stamp_ns for r in actual), tuple(stamps[left:right + 1]), qualified)

    def evaluate(self, center, radius, epsilon, confirmation_ns, *, mad_scale=3.,
                 evidence_policy='angular_profiles_v1'):
        if not all(math.isfinite(v) for v in (*center, radius, epsilon)) or min(radius, epsilon) <= 0:
            raise ValueError('explicit finite positive candidate geometry required')
        try:
            return self._evaluate(center, radius, epsilon, confirmation_ns,
                                  mad_scale=mad_scale, evidence_policy=evidence_policy)
        except (ValueError, OverflowError, ArithmeticError):
            return MovingEvidence(reason='numerical_overflow')

    def _evaluate(self, center, radius, epsilon, confirmation_ns, *, mad_scale,
                  evidence_policy):
        if evidence_policy not in ('angular_profiles_v1', 'recurrent_trapping_v1'):
            return MovingEvidence(reason='unknown_evidence_policy')
        qualified = [c for c in self.cycles if c.qualified]
        inside = [c for c in qualified
                  if all(math.dist(p, center) <= radius for p in c.vertices)]
        eligible = [c for c in inside if math.dist(c.centroid, center) <= epsilon]
        diagnostics = dict(completed_cycles=len(self.cycles), qualified_cycles=len(qualified),
                           inside_radius_cycles=len(inside), eligible_cycles=len(eligible),
                           centroid_tolerance_m=epsilon,
                           nearest_inside_centroid_m=min(
                               (math.dist(c.centroid, center) for c in inside), default=None))
        if len(eligible) < 3:
            return MovingEvidence(reason='missing_qualified_neighborhood_cycles',
                                  diagnostics=tuple(diagnostics.items()))
        cycles = tuple(eligible[-3:])
        sector_distance = max(math.dist(a.sector_centroids[k], b.sector_centroids[k])
                              for i, a in enumerate(cycles) for b in cycles[i + 1:] for k in range(12))
        diagnostics['sector_trajectory_margin_m'] = epsilon - sector_distance
        if sector_distance > epsilon:
            return MovingEvidence(reason='incomparable_sector_trajectories', cycles=cycles,
                                  diagnostics=tuple(diagnostics.items()))
        support = set(s for c in cycles for s in c.support_stamps)
        records = tuple(r for r in self.records if r.stamp_ns in support)
        if len(records) > self.max_snapshot:
            return MovingEvidence(reason='snapshot_capacity', cycles=cycles,
                                  diagnostics=tuple(diagnostics.items()))
        if len(records) != len(support):
            return MovingEvidence(reason='lost_boundary_support', cycles=cycles,
                                  diagnostics=tuple(diagnostics.items()))
        stamps = [r.stamp_ns for r in records]
        ranges = tuple((bisect_left(stamps, c.start_ns), bisect_left(stamps, c.end_ns)) for c in cycles)
        minima = [c.minimum for c in cycles]
        pre = sum(c.end_ns <= confirmation_ns for c in cycles)
        summary = RotationCostWindow.summarize_minima(
            minima, required_rotations=3, mad_scale=mad_scale,
            pretrigger_rotation_count=pre, verification_rotation_count=3 - pre)
        profiles = [tuple(x - statistics.fmean(c.sector_medians) for x in c.sector_medians) for c in cycles]
        mean = [statistics.fmean(p[k] for p in profiles) for k in range(12)]
        amplitude = math.sqrt(statistics.fmean(x*x for x in mean))
        disagreement = math.sqrt(statistics.fmean((p[k] - q[k])**2 for i, p in enumerate(profiles) for q in profiles[i + 1:] for k in range(12)))
        actual_stamps = {s for cycle in cycles for s in cycle.sample_stamps}
        floor = max(1e-6, 64 * max(math.ulp(r.raw) for r in records if r.stamp_ns in actual_stamps))
        baseline = statistics.median(c for cycle in cycles for c in cycle.sector_medians)
        informative = bool(summary and summary.valid and math.isfinite(amplitude)
                           and math.isfinite(disagreement) and math.isfinite(floor)
                           and amplitude > max(3 * disagreement, floor)
                           and baseline < -floor and summary.upper < -floor)
        diagnostics.update(signal_margin=amplitude - max(3 * disagreement, floor),
                           baseline_negative_margin=-floor - baseline,
                           upper_cost_negative_margin=(-floor - summary.upper
                                                       if summary and summary.valid else None))
        ready = informative
        reason = 'ready' if informative else 'uninformative_raw_profiles'
        if evidence_policy == 'recurrent_trapping_v1':
            # Trapping authority is validated separately by the supervisor/fill
            # owners. This branch changes only raw-cost usability, never the
            # measured angular informativeness or the geometric support guards.
            ready = bool(summary and summary.valid
                         and all(math.isfinite(v) for v in
                                 (amplitude, disagreement, floor, baseline,
                                  summary.estimate, summary.mad, summary.uncertainty,
                                  summary.lower, summary.upper))
                         and baseline < -floor and summary.upper < -floor)
            reason = 'ready' if ready else 'raw_cost_quality_failed'
        return MovingEvidence(ready, reason,
                              cycles, records, ranges, summary, amplitude, disagreement, floor, informative,
                              tuple(diagnostics.items()))


def snapshot_raw_evidence(snapshot, *, evidence_policy='angular_profiles_v1', mad_scale=3.):
    """Reconstruct the *declared* three rotations through the existing raw owner.

    Snapshot observations include original interpolation brackets. Starting a
    new phase anchor at the first such bracket changes the cycle boundaries, so
    replace the replay's automatically discovered cycles with exact wire bounds.
    Identity/authority and original observation admission remain caller-owned.
    """
    try:
        s = snapshot
        n = len(s.observations)
        if (not 4 <= n <= 4000 or s.completed_revolutions != 3
                or len(s.observation_filter_state) != n
                or len(s.observation_filter_stamp) != n
                or any(len(getattr(s, key)) != 3 for key in
                       ('revolution_start', 'revolution_end',
                        'revolution_sample_start', 'revolution_sample_end'))):
            raise ValueError('invalid raw snapshot population')
        core = MovingRawEvidence()
        core.start_epoch(s.search_epoch, time_to_ns(s.time_origin))
        reset = core.reset_sequence
        for obs, state, publication in zip(s.observations, s.observation_filter_state,
                                           s.observation_filter_stamp):
            if state not in (1, 2, 3, 4, 5) or not core.add(obs, state, time_to_ns(publication)):
                raise ValueError('invalid original raw support')
            if core.reset_sequence != reset:
                raise ValueError('raw support was interrupted')
        if len(core.records) != n:
            raise ValueError('raw support was lost')
        bounds = [(time_to_ns(lo), time_to_ns(hi))
                  for lo, hi in zip(s.revolution_start, s.revolution_end)]
        if (time_to_ns(s.evidence_start) != bounds[0][0]
                or time_to_ns(s.evidence_end) != bounds[-1][1]
                or any(lo >= hi for lo, hi in bounds)
                or any(a[1] > b[0] for a, b in zip(bounds, bounds[1:]))):
            raise ValueError('invalid declared raw cycle bounds')
        cycles = []
        for lo, hi in bounds:
            a, b = core._point(lo), core._point(hi)
            # Source boundaries were rounded to nanoseconds by _crossing.
            # Their maximum half-ns phase error is bounded by the adjacent
            # measured phase slopes; this does not admit a partial rotation.
            slopes = [abs((y.phase - x.phase) / (y.stamp_ns - x.stamp_ns))
                      for x, y in zip(core.records, core.records[1:])
                      if x.stamp_ns <= hi and y.stamp_ns >= lo]
            tolerance = max(slopes, default=0.) + 1e-12
            if abs(abs(b[1] - a[1]) - TAU) > tolerance:
                raise ValueError('declared raw support is not one complete rotation')
            cycles.append(core._cycle(a[:2], b[:2]))
        core.cycles = cycles
        result = core.evaluate((s.center_x_m, s.center_y_m), s.neighborhood_radius_m,
            s.centroid_tolerance_m, time_to_ns(s.confirmation_stamp),
            mad_scale=mad_scale, evidence_policy=evidence_policy)
        if len(result.cycles) != 3 or len(result.records) != n or result.summary is None:
            raise ValueError('raw snapshot geometry is not usable')
        if (tuple(result.sample_ranges) != tuple(zip(s.revolution_sample_start, s.revolution_sample_end))
                or tuple((c.start_ns, c.end_ns) for c in result.cycles) != tuple(bounds)
                or result.summary.pretrigger_rotation_count != s.pretrigger_revolutions
                or result.summary.verification_rotation_count != s.verification_revolutions
                or result.informative != s.informative):
            raise ValueError('declared raw snapshot assignment or informativeness changed')
        pairs = [(getattr(result.summary, key), getattr(s, 'candidate_cost_' + key))
                 for key in ('estimate', 'mad', 'uncertainty', 'lower', 'upper')]
        pairs += [(result.amplitude, s.information_amplitude),
                  (result.disagreement, s.information_disagreement),
                  (result.information_floor, s.information_floor)]
        if any(not math.isfinite(a) or not math.isfinite(b)
               or not math.isclose(a, b, rel_tol=0., abs_tol=1e-12) for a, b in pairs):
            raise ValueError('declared raw statistics differ from original samples')
        return result
    except (AttributeError, TypeError, ValueError, OverflowError, ArithmeticError):
        return MovingEvidence(reason='invalid_raw_snapshot')
