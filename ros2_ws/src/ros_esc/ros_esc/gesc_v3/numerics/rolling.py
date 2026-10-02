"""Measured-angle world-vector quadrature with asynchronous cycle coherence.

Update/evaluate contain no SciPy calls. The sole numerical worker computes an
immutable coherence snapshot; only the exact current snapshot can receive it.
Instantaneous output remains usable before complete cycles or during a job.
"""
from collections import deque
from dataclasses import dataclass, replace
import math
from typing import Optional, Tuple

Vector = Tuple[float, float]
_TAU = 2.0 * math.pi
_MAX_NS = 2**63 - 1

def _ns(value):
    return isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= _MAX_NS

def _finite(*values):
    try:
        return all(not isinstance(v, bool) and math.isfinite(v) for v in values)
    except (TypeError, ValueError, OverflowError):
        return False

def _vector(value):
    return isinstance(value, tuple) and len(value) == 2 and _finite(*value)

def wrap_angle(angle):
    """Return a finite angle in [-pi, pi]; ambiguous pi is checked by callers."""
    return math.remainder(angle, _TAU)

def _rotation(vector, yaw):
    c, s = math.cos(yaw), math.sin(yaw)
    result = (c * vector[0] - s * vector[1], s * vector[0] + c * vector[1])
    if not _finite(*result):
        raise ArithmeticError("numerical_overflow")
    return result

def _lerp(a, b, fraction):
    # Avoid the unnecessary b-a overflow for finite large endpoints.
    value = (1.0 - fraction) * a + fraction * b
    if not _finite(value):
        raise ArithmeticError("numerical_overflow")
    return value

def _angular_delta(a, b):
    delta = wrap_angle(wrap_angle(b) - wrap_angle(a))
    if abs(delta) == math.pi:
        raise ArithmeticError("ambiguous_phase_step")
    return delta

@dataclass(frozen=True)
class DirectionObservation:
    observation_id: int
    source_stamp_ns: int
    receipt_stamp_ns: int
    base_yaw: float
    sensor_world_phase: float
    objective_revision: int = 0
    frame_id: str = "odom"
    oldest_receipt_stamp_ns: Optional[int] = None

    @property
    def identity(self):
        return self.frame_id

    @property
    def objective(self):
        return self.objective_revision


@dataclass(frozen=True)
class RollingGescConfig:
    max_gap_ns: int = 500_000_000
    max_cycle_duration_ns: int = 30_000_000_000
    max_samples: int = 20_000
    sectors: int = 12
    confidence_cycles: int = 3
    absolute_magnitude_floor: float = 1e-6
    freshness_ns: int = 500_000_000

    def __post_init__(self):
        for name in ("max_gap_ns", "max_cycle_duration_ns", "max_samples", "freshness_ns"):
            if not _ns(getattr(self, name)) or getattr(self, name) == 0:
                raise ValueError("rolling bounds must be positive integers")
        if self.sectors != 12 or self.confidence_cycles != 3:
            raise ValueError("selected rolling mean requires 12 sectors and 3 warmup cycles")
        if not _finite(self.absolute_magnitude_floor) or self.absolute_magnitude_floor <= 0:
            raise ValueError("invalid magnitude floor")


@dataclass(frozen=True)
class DemodulatedSample:
    observation: DirectionObservation
    q_body: Vector

@dataclass(frozen=True)
class CycleSummary:
    start_ns: int
    end_ns: int
    phase_start: float
    phase_end: float
    mean_world: Vector
    sector_counts: Tuple[int, ...]
    sample_count: int
    max_gap_ns: int
    coverage_valid: bool

@dataclass(frozen=True)
class RollingResult:
    observation: Optional[DirectionObservation] = None
    instant_body: Optional[Vector] = None
    instant_world: Optional[Vector] = None
    mean_world: Optional[Vector] = None
    final_body: Optional[Vector] = None
    instantaneous_magnitude: Optional[float] = None
    mean_magnitude: Optional[float] = None
    final_magnitude: Optional[float] = None
    output_yaw: Optional[float] = None
    output_pose_stamp_ns: Optional[int] = None
    rolling_start_ns: Optional[int] = None
    rolling_end_ns: Optional[int] = None
    rolling_duration_ns: int = 0
    phase_start: Optional[float] = None
    phase_end: Optional[float] = None
    sector_counts: Tuple[int, ...] = (0,) * 12
    sample_count: int = 0
    max_gap_ns: int = 0
    cycles: Tuple[CycleSummary, ...] = ()
    completed_cycle_count: int = 0
    actual_blend_weight: float = 0.0
    mean_full: bool = False
    coverage_valid: bool = False
    qualified: bool = False
    fallback_used: bool = False
    output_valid: bool = False
    reset_sequence: int = 0
    reset_reason: str = ""
    fallback_reason: str = "initializing"
    norm_denominator: Optional[float] = None
    norm_error: Optional[float] = None
    coherence: Optional[float] = None
    coherence_lower: Optional[float] = None
    coherence_upper: Optional[float] = None
    coherence_available: bool = False
    coherence_reason: str = "not_selected"
    warmup_valid: bool = False
    norm_new_evaluations: int = 0
    norm_window_evaluations: int = 0

@dataclass(frozen=True)
class _Point:
    stamp_ns: int
    phase: float  # Signed, locally unwrapped actual world phase.
    q: Vector
    observation_id: Optional[int]

@dataclass(frozen=True)
class CoherenceJob:
    source_stamp_ns: int
    reset_sequence: int
    objective_revision: int
    start: _Point
    end: _Point
    points: tuple
    mean_world: Vector


@dataclass(frozen=True)
class CoherenceResult:
    source_stamp_ns: int
    reset_sequence: int
    objective_revision: int
    values: tuple


def compute_coherence(job: CoherenceJob) -> CoherenceResult:
    """Worker-only bounded quadrature; completion never renews source age."""
    from .coherence import MAX_NORM_CALLS, NormCache
    cache = NormCache()
    calls = 0
    for left, right in zip(job.points, job.points[1:]):
        # An immutable job replaces the old in-callback incremental cache.
        # Recompute only complete segments in this window. Each segment keeps
        # the original 2048-call limit and the window keeps its 20000 limit.
        if left.stamp_ns < job.start.stamp_ns or right.stamp_ns > job.end.stamp_ns:
            continue
        cache.begin_update()
        cache.append(left, right)
        calls += cache.budget.calls
        if calls > MAX_NORM_CALLS:
            break
    cache.begin_update()  # the interpolated left boundary has a finite budget
    values = cache.evaluate(job.start, job.end, job.points, job.mean_world)
    values['new_evaluations'] = calls + cache.budget.calls
    return CoherenceResult(job.source_stamp_ns, job.reset_sequence,
                           job.objective_revision, tuple(values.items()))


class RollingGesc:
    """World-vector temporal quadrature with independent whole-cycle confidence."""

    def __init__(self, config=RollingGescConfig()):
        self.config = config
        self.identity = None
        self.objective = None
        self.reset_sequence = 0
        self.reset_reason = ""
        self._points = []
        self._cycles = deque(maxlen=3)
        self._direction = 0
        self._anchor = None
        self._cycle_start = None
        self._completed = 0
        self._last_sample = None
        self._instant_world = None
        self._result = RollingResult()
        self._accepted_result = None
        self._last_evaluation_ns = None

    def invalidate(self, reason):
        self.reset_sequence += 1
        self.reset_reason = str(reason)
        self._points.clear()
        self._cycles.clear()
        self._direction = 0
        self._anchor = None
        self._cycle_start = None
        self._completed = 0
        self._last_sample = None
        self._instant_world = None
        self._last_evaluation_ns = None
        self._accepted_result = None
        self._result = RollingResult(reset_sequence=self.reset_sequence,
                                     reset_reason=self.reset_reason, fallback_reason=self.reset_reason,
                                     coherence_reason=self.reset_reason)
        return self._result

    def set_context(self, stream_identity, objective_identity):
        if not isinstance(stream_identity, str) or not stream_identity or not _ns(objective_identity):
            raise ValueError("invalid rolling context")
        if stream_identity != self.identity:
            self.identity, self.objective = stream_identity, objective_identity
            return self.invalidate("context_changed")
        if objective_identity != self.objective:
            if self.objective is not None and objective_identity <= self.objective:
                return self.invalidate("objective_revision_conflict")
            self.objective = objective_identity
            return self.invalidate("objective_changed")
        return self._result

    def _seed(self, sample, q_world, reason=""):
        obs = sample.observation
        point = _Point(obs.source_stamp_ns, wrap_angle(obs.sensor_world_phase), q_world, obs.observation_id)
        self._points = [point]
        self._anchor = point.phase
        self._cycle_start = point
        self._last_sample = sample
        self._instant_world = q_world
        self._accepted_result = None
        self._result = self._snapshot(reason or "initializing")
        return self._result

    def update(self, sample):
        if (not isinstance(sample, DemodulatedSample) or not _vector(sample.q_body)
                or not isinstance(sample.observation, DirectionObservation)):
            return self.invalidate("invalid_sample")
        obs = sample.observation
        if (not isinstance(obs.identity, str) or not obs.identity
                or not _ns(obs.source_stamp_ns) or not _ns(obs.observation_id)
                or not _ns(obs.receipt_stamp_ns) or not _ns(obs.objective)
                or not _finite(obs.base_yaw, obs.sensor_world_phase)
                or (obs.oldest_receipt_stamp_ns is not None
                    and (not _ns(obs.oldest_receipt_stamp_ns)
                         or obs.oldest_receipt_stamp_ns > obs.receipt_stamp_ns))):
            return self.invalidate("invalid_sample")
        if self.identity is not None and obs.identity == self.identity and self.objective is not None:
            if obs.objective != self.objective and obs.objective <= self.objective:
                return self.invalidate("objective_revision_conflict")
        self.set_context(obs.identity, obs.objective)
        try:
            world = _rotation(sample.q_body, obs.base_yaw)
            if not self._points:
                return self._seed(sample, world)
            previous = self._points[-1]
            dt = obs.source_stamp_ns - previous.stamp_ns
            if dt == 0 and sample == self._last_sample:
                return self._result
            if dt <= 0 or obs.observation_id <= self._last_sample.observation.observation_id:
                return self.invalidate("source_rollback_or_duplicate_conflict")
            if dt > self.config.max_gap_ns:
                self.invalidate("source_gap")
                return self._seed(sample, world, "source_gap")
            delta = _angular_delta(previous.phase, obs.sensor_world_phase)
            if abs(delta) <= 1e-12:
                delta = 0.0
            if delta and self._direction and delta * self._direction < 0:
                self.invalidate("phase_reversal")
                return self._seed(sample, world, "phase_reversal")
            if delta and not self._direction:
                self._direction = 1 if delta > 0 else -1
            point = _Point(obs.source_stamp_ns, previous.phase + delta, world, obs.observation_id)
            self._points.append(point)
            self._last_sample, self._instant_world = sample, world
            if len(self._points) > self.config.max_samples:
                self.invalidate("sample_capacity")
                return self._seed(sample, world, "sample_capacity")
            if self._direction:
                target = self._anchor + self._direction * _TAU * (self._completed + 1)
                if self._direction * (point.phase - target) >= -1e-12:
                    boundary = self._crossing(target)
                    summary = self._summarize(self._cycle_start, boundary)
                    if summary.end_ns - summary.start_ns > self.config.max_cycle_duration_ns:
                        self.invalidate("cycle_duration")
                        return self._seed(sample, world, "cycle_duration")
                    self._cycles.append(summary)
                    self._completed += 1
                    self._cycle_start = boundary
            if point.stamp_ns - self._cycle_start.stamp_ns > self.config.max_cycle_duration_ns:
                self.invalidate("cycle_duration")
                return self._seed(sample, world, "cycle_duration")
            self._result = self._snapshot()
            if self._result.coherence_reason != "pending_coherence":
                self._accepted_result = None
            # Keep the first crossing support (including plateaus) and current
            # anchored-cycle support; confidence itself retains only summaries.
            if self._direction and self._result.mean_full:
                cutoff = min(self._result.rolling_start_ns, self._cycle_start.stamp_ns)
                while len(self._points) > 2 and self._points[1].stamp_ns < cutoff:
                    self._points.pop(0)
            return self._result
        except (ArithmeticError, ValueError, OverflowError):
            return self.invalidate("numerical_or_phase_error")

    def _crossing(self, phase):
        for index, point in enumerate(self._points):
            if self._direction * (point.phase - phase) >= -1e-12:
                if abs(point.phase - phase) <= 1e-12:
                    return replace(point, phase=phase)
                if index == 0:
                    raise ArithmeticError("unrepresented_boundary")
                left = self._points[index - 1]
                fraction = (phase - left.phase) / (point.phase - left.phase)
                stamp = left.stamp_ns + round(fraction * (point.stamp_ns - left.stamp_ns))
                return _Point(stamp, phase,
                              tuple(_lerp(a, b, fraction) for a, b in zip(left.q, point.q)), None)
        raise ArithmeticError("unrepresented_boundary")

    def _summarize(self, start, end):
        duration = end.stamp_ns - start.stamp_ns
        if duration <= 0:
            raise ArithmeticError("empty_revolution")
        internal = [p for p in self._points if start.stamp_ns < p.stamp_ns < end.stamp_ns]
        support = [start] + internal + [end]
        # Normalize durations before multiplying to avoid integral overflow.
        mean = tuple(math.fsum(
            ((b.stamp_ns - a.stamp_ns) / duration) * (0.5 * a.q[k] + 0.5 * b.q[k])
            for a, b in zip(support, support[1:])) for k in range(2))
        if not _finite(*mean):
            raise ArithmeticError("numerical_overflow")
        counts = [0] * self.config.sectors
        for p in self._points:
            if start.stamp_ns <= p.stamp_ns < end.stamp_ns and p.observation_id is not None:
                sector = min(11, int((p.phase % _TAU) / (_TAU / 12)))
                counts[sector] += 1
        gaps = [b.stamp_ns - a.stamp_ns for a, b in zip(support, support[1:])]
        # Include full original source gaps behind interpolated endpoints.
        gaps.extend(b.stamp_ns - a.stamp_ns for a, b in zip(self._points, self._points[1:])
                    if b.stamp_ns > start.stamp_ns and a.stamp_ns < end.stamp_ns)
        gap = max(gaps)
        # This branch's moving policy is the explicitly identified 5 Hz
        # experiment. Retain actual full revolutions and temporal support;
        # only its sector population requirement is disabled.
        # Selected 5 Hz moving policy retains full revolutions and source
        # support; it does not require two actual samples in every sector.
        covered = gap <= self.config.max_gap_ns and duration <= self.config.max_cycle_duration_ns
        return CycleSummary(start.stamp_ns, end.stamp_ns, start.phase, end.phase,
                            mean, tuple(counts), sum(counts), gap, covered)

    def _snapshot(self, reason=""):
        result = self._snapshot_geometry(reason)
        warmup = len(result.cycles) == 3 and all(c.coverage_valid for c in result.cycles)
        result = replace(result, qualified=False, warmup_valid=warmup,
                         coherence_reason=result.fallback_reason)
        if not result.mean_full or not result.coverage_valid:
            return result
        if not warmup:
            reason = "incomplete_cycle_confidence" if len(result.cycles) < 3 else "incomplete_cycle_coverage"
            return replace(result, coherence_reason=reason, fallback_reason=reason)
        if result.mean_magnitude <= self.config.absolute_magnitude_floor:
            return replace(result, coherence_reason="weak_current_mean", fallback_reason="weak_current_mean")
        return replace(result, coherence_reason="pending_coherence", fallback_reason="pending_coherence")

    def coherence_job(self):
        result = self._result
        if result.coherence_reason != "pending_coherence":
            return None
        return CoherenceJob(result.observation.source_stamp_ns, self.reset_sequence,
                            result.observation.objective_revision,
                            self._crossing(result.phase_start), self._points[-1],
                            tuple(self._points), result.mean_world)

    def apply_coherence(self, response):
        result = self._result
        if (not isinstance(response, CoherenceResult) or result.observation is None
                or (response.source_stamp_ns, response.reset_sequence, response.objective_revision)
                != (result.observation.source_stamp_ns, self.reset_sequence,
                    result.observation.objective_revision)):
            return False
        value = dict(response.values)
        self._result = replace(result, qualified=value['qualified'],
            norm_denominator=value['denominator'], norm_error=value['denominator_error'],
            coherence=value['coherence'], coherence_lower=value['lower'],
            coherence_upper=value['upper'], coherence_available=value['available'],
            coherence_reason=value['reason'], norm_new_evaluations=value['new_evaluations'],
            norm_window_evaluations=value['window_evaluations'],
            fallback_reason="" if value['qualified'] else value['reason'])
        self._accepted_result = self._result if value['qualified'] else None
        return True

    def _snapshot_geometry(self, reason=""):
        sample = self._last_sample
        if sample is None:
            return self._result
        latest = self._points[-1]
        magnitude = math.hypot(*self._instant_world)
        if not _finite(magnitude):
            raise ArithmeticError("numerical_overflow")
        result = RollingResult(
            observation=sample.observation, instant_body=sample.q_body,
            instant_world=self._instant_world,
            instantaneous_magnitude=magnitude,
            cycles=tuple(self._cycles), completed_cycle_count=self._completed,
            reset_sequence=self.reset_sequence, reset_reason=self.reset_reason,
            fallback_reason=reason or "incomplete_revolution",
        )
        if not self._direction:
            return result
        phase = latest.phase - self._direction * _TAU
        if self._direction * (phase - self._points[0].phase) < -1e-12:
            return result
        rolling = self._summarize(self._crossing(phase), latest)
        result = replace(result, mean_world=rolling.mean_world,
                         mean_magnitude=math.hypot(*rolling.mean_world),
                         rolling_start_ns=rolling.start_ns, rolling_end_ns=rolling.end_ns,
                         rolling_duration_ns=rolling.end_ns - rolling.start_ns,
                         phase_start=rolling.phase_start, phase_end=rolling.phase_end,
                         sector_counts=rolling.sector_counts, sample_count=rolling.sample_count,
                         max_gap_ns=rolling.max_gap_ns, mean_full=True,
                         coverage_valid=rolling.coverage_valid,
                         fallback_reason="incomplete_cycle_confidence")
        if not _finite(result.mean_magnitude):
            raise ArithmeticError("numerical_overflow")
        if not rolling.coverage_valid:
            return replace(result, fallback_reason="incomplete_phase_coverage")
        if len(self._cycles) != 3:
            return result
        if not all(c.coverage_valid for c in self._cycles):
            return replace(result, fallback_reason="incomplete_cycle_coverage")
        return result

    def _observation_fresh(self, observation, now_ns):
        if observation is None:
            return False
        stamps = (observation.source_stamp_ns, observation.receipt_stamp_ns,
                  observation.oldest_receipt_stamp_ns)
        return all(0 <= now_ns-stamp <= self.config.freshness_ns
                   for stamp in stamps if stamp is not None)

    def evaluate(self, now_ns, output_yaw, output_pose_stamp_ns):
        """Rotate into a fresh actual pose's body frame; yaw is held, not predicted."""
        if _ns(now_ns):
            if self._last_evaluation_ns is not None and now_ns < self._last_evaluation_ns:
                return self.invalidate("clock_rollback")
            self._last_evaluation_ns = now_ns
        result = self._result
        obs = result.observation
        if (obs is None or not _ns(now_ns) or not _ns(output_pose_stamp_ns)
                or not _finite(output_yaw)
                or not self._observation_fresh(obs, now_ns)
                or not 0 <= now_ns - output_pose_stamp_ns <= self.config.freshness_ns):
            return replace(result, output_valid=False, fallback_used=False,
                           actual_blend_weight=0.0, final_body=None, final_magnitude=None,
                           fallback_reason="stale_or_invalid_output_input")
        accepted = self._accepted_result
        if (result.coherence_reason == "pending_coherence" and accepted is not None
                and accepted.reset_sequence == result.reset_sequence
                and accepted.observation.identity == obs.identity
                and accepted.observation.objective == obs.objective
                and self._observation_fresh(accepted.observation, now_ns)):
            # Hold the accepted snapshot, including its original timestamps.
            # New input still creates a new job; old confidence never qualifies
            # its uncomputed geometry. Reproject the held vector at current yaw.
            result = accepted
        return self._evaluate_moving(result, output_yaw, output_pose_stamp_ns)

    def _evaluate_moving(self, result, output_yaw, output_pose_stamp_ns):
        """A meaningful mean can bridge a finite instantaneous zero crossing."""
        weight = .75 if result.qualified else 0.0
        reason = result.fallback_reason
        world = result.instant_world
        if weight:
            world = tuple(.25*a + .75*b for a, b in zip(world, result.mean_world))
            if not _vector(world) or math.hypot(*world) <= self.config.absolute_magnitude_floor:
                world, weight, reason = result.instant_world, 0.0, "weak_or_nonfinite_mixture"
        if (not _vector(world) or math.hypot(*world) <= self.config.absolute_magnitude_floor):
            return replace(result, final_body=None, final_magnitude=None, output_valid=False,
                           fallback_used=False, actual_blend_weight=0.0,
                           fallback_reason="no_meaningful_direction")
        try:
            body = _rotation(world, -output_yaw)
            magnitude = math.hypot(*body)
            if not _finite(magnitude):
                raise ArithmeticError("numerical_overflow")
        except (ArithmeticError, ValueError, OverflowError):
            return self.invalidate("numerical_overflow")
        return replace(result, final_body=body, final_magnitude=magnitude,
                       output_yaw=output_yaw, output_pose_stamp_ns=output_pose_stamp_ns,
                       actual_blend_weight=weight, output_valid=True,
                       fallback_used=weight == 0.0, fallback_reason=reason)
