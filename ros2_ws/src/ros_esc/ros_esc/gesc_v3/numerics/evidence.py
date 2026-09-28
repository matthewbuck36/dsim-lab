"""Bounded, source-time raw evidence for moving candidate verification.

No direction-confidence decision or augmented objective is used here. Samples
retain the first filter-publication state; that is not acquisition-state truth.
The piecewise-linear measured trajectory supplies integration and confinement.
"""

from bisect import bisect_left
from dataclasses import dataclass
import math
import statistics

from typing import Optional

@dataclass(frozen=True)
class CandidateCostSummary:
    """Rotation-stable raw-cost evidence for one extremum candidate."""

    estimate: float
    mad: float
    uncertainty: float
    rotation_count: int
    pretrigger_rotation_count: int = 0
    verification_rotation_count: int = 0
    available_rotation_count: int = 0

    @property
    def lower(self) -> float:
        return float(self.estimate - self.uncertainty)

    @property
    def upper(self) -> float:
        return float(self.estimate + self.uncertainty)

    @property
    def valid(self) -> bool:
        return bool(
            math.isfinite(float(self.estimate))
            and math.isfinite(float(self.mad))
            and float(self.mad) >= 0.0
            and math.isfinite(float(self.uncertainty))
            and float(self.uncertainty) >= 0.0
            and not isinstance(self.rotation_count, bool)
            and isinstance(self.rotation_count, int)
            and self.rotation_count > 0
            and not isinstance(self.pretrigger_rotation_count, bool)
            and isinstance(self.pretrigger_rotation_count, int)
            and self.pretrigger_rotation_count >= 0
            and not isinstance(self.verification_rotation_count, bool)
            and isinstance(self.verification_rotation_count, int)
            and self.verification_rotation_count >= 0
            and not isinstance(self.available_rotation_count, bool)
            and isinstance(self.available_rotation_count, int)
            and self.available_rotation_count >= 0
        )


def summarize_minima(
    values,
    required_rotations: int,
    mad_scale: float,
    pretrigger_rotation_count: int = 0,
    verification_rotation_count: int = 0,
) -> Optional[CandidateCostSummary]:
    """Summarize the strongest repeated minima in a bounded pool."""

    if (
        isinstance(required_rotations, bool)
        or not isinstance(required_rotations, int)
        or required_rotations <= 0
    ):
        raise ValueError("required_rotations must be a positive integer")
    mad_scale = float(mad_scale)
    if not math.isfinite(mad_scale) or mad_scale < 0.0:
        raise ValueError("mad_scale must be finite and nonnegative")
    if (
        isinstance(pretrigger_rotation_count, bool)
        or not isinstance(pretrigger_rotation_count, int)
        or pretrigger_rotation_count < 0
        or isinstance(verification_rotation_count, bool)
        or not isinstance(verification_rotation_count, int)
        or verification_rotation_count < 0
    ):
        raise ValueError("rotation provenance counts must be nonnegative")
    finite_values = tuple(float(value) for value in values)
    if any(not math.isfinite(value) for value in finite_values):
        raise ValueError("rotation minima must be finite")
    if len(finite_values) < required_rotations:
        return None
    selected = tuple(sorted(finite_values)[:required_rotations])
    estimate = float(statistics.median(selected))
    mad = float(
        statistics.median(abs(value - estimate) for value in selected)
    )
    return CandidateCostSummary(
        estimate=estimate,
        mad=mad,
        uncertainty=float(mad_scale * mad),
        rotation_count=len(selected),
        pretrigger_rotation_count=pretrigger_rotation_count,
        verification_rotation_count=verification_rotation_count,
        available_rotation_count=len(finite_values),
    )



TAU = 2.0 * math.pi
SECTOR = TAU / 12


@dataclass(frozen=True)
class RawObservation:
    """Raw authoritative source data. Unknown device timing is not fabricated."""
    observation_id: int
    source_sequence: int
    source_stamp_ns: int
    base_x_m: float
    base_y_m: float
    raw_cost: float
    sensor_world_phase_rad: float
    raw_cost_valid: bool = True
    synchronized_valid: bool = True
    sensor_transform_observed: bool = True
    base_yaw_rad: float = 0.0


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
    fingerprint: RawObservation


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

    def __init__(self, *, max_observations=20000, max_snapshot=4000,
                 min_sector_samples=1):
        if max_observations < 4 or max_snapshot < 4:
            raise ValueError('evidence capacities must be at least four')
        if type(min_sector_samples) is not int or min_sector_samples not in (1, 2):
            raise ValueError('raw evidence needs one or two actual samples per sector')
        self.max_observations = max_observations
        self.max_snapshot = max_snapshot
        self.min_sector_samples = min_sector_samples
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
            stamp = observation.source_stamp_ns
            if type(stamp) is not int or stamp < 0:
                return False
            values = (observation.base_x_m, observation.base_y_m,
                      observation.raw_cost, observation.sensor_world_phase_rad)
            if (self.poison_capacity_exhausted or stamp < self.epoch_start_ns or stamp in self._poisoned
                    or observation.observation_id <= 0 or observation.source_sequence <= 0
                    or not observation.raw_cost_valid
                    or not observation.synchronized_valid
                    or not observation.sensor_transform_observed
                    or not all(math.isfinite(v) for v in (*values, observation.base_yaw_rad))
                    or filter_stamp_ns < stamp):
                return False
            fingerprint = observation
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
            record = RawRecord(observation, stamp, phase,
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
        qualified = (0 < duration <= 30
                     and all(len(c) >= self.min_sector_samples for c in costs)
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
                 evidence_policy='recurrent_trapping_v1'):
        if not all(math.isfinite(v) for v in (*center, radius, epsilon)) or min(radius, epsilon) <= 0:
            raise ValueError('explicit finite positive candidate geometry required')
        try:
            return self._evaluate(center, radius, epsilon, confirmation_ns,
                                  mad_scale=mad_scale, evidence_policy=evidence_policy)
        except (ValueError, OverflowError, ArithmeticError):
            return MovingEvidence(reason='numerical_overflow')

    def _evaluate(self, center, radius, epsilon, confirmation_ns, *, mad_scale,
                  evidence_policy):
        if evidence_policy != 'recurrent_trapping_v1':
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
        summary = summarize_minima(
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
