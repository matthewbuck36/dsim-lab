"""Pure source synchronization and rolling GESC evidence for the opt-in V2 path.

All times are absolute integer ROS nanoseconds, except the unchanged legacy
cost key. This module owns neither ROS callbacks, filter dynamics nor motion
authorization. See docs/codex/gesc_gaussian/v2/m2_plan.md.
"""

from bisect import bisect_left
from collections import OrderedDict, deque
from dataclasses import dataclass, replace
import math
from typing import Optional, Tuple

from ros_esc.v2_direction_policy import (
    MOVING_CYCLE_POLICY, THREE_CYCLE_POLICY, policy_config_sha256, validate_policy,
)


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


def publication_time_tolerance_ns(origin_ns, legacy_sec, publication_ns):
    """Bound floating publication-key representation error, not synchronization.

The actual ROS publication stamp stays integer-exact. Legacy cost keys still
join by exact float equality; this only checks consistency of their lossy
relative-seconds representation against that separately observed stamp.
"""
    if not _ns(origin_ns) or not _ns(publication_ns) or not _finite(legacy_sec) or legacy_sec < 0:
        raise ValueError("invalid publication time")
    error = (math.ulp(publication_ns * 1e-9) + math.ulp(origin_ns * 1e-9)
             + math.ulp(legacy_sec)) * 1e9
    if not _finite(error):
        raise ValueError("invalid publication time")
    return max(1, math.ceil(error) + 1)


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
class GescSyncConfig:
    sync_tolerance_ns: int = 50_000_000
    freshness_ns: int = 500_000_000
    buffer_span_ns: int = 2_000_000_000
    max_source_samples: int = 4096
    max_pending_costs: int = 1024

    def __post_init__(self):
        if any(not _ns(v) or v == 0 for v in vars(self).values()):
            raise ValueError("synchronization bounds must be positive integers")
        if self.buffer_span_ns < self.freshness_ns:
            raise ValueError("source buffer must cover freshness horizon")


@dataclass(frozen=True)
class StreamIdentity:
    run_id: str
    stream_contract_id: str
    frame_id: str
    time_origin_ns: int
    channel_index: int = 0
    cost_key_basis: str = "publication_time"


@dataclass(frozen=True)
class ObjectiveIdentity:
    revision: int
    sensor_weight: float = 1.0
    gaussian_weight: float = 0.0
    affine_weight: float = 0.0
    registry_digest: str = ""
    affine_revision: int = 0


@dataclass(frozen=True)
class PoseSample:
    stamp_ns: int
    xy: Vector
    yaw: float
    receipt_ns: int
    frame_id: str


@dataclass(frozen=True)
class EncoderSample:
    stamp_ns: int
    phase: float
    receipt_ns: int


@dataclass(frozen=True)
class RawCost:
    legacy_stamp_sec: float
    values: Tuple[float, ...]
    receipt_ns: int


@dataclass(frozen=True)
class Provenance:
    legacy_stamp_sec: float
    source_sequence: int
    model_input_ns: int
    cost_publication_ns: int
    sensor_xy: Vector
    sensor_world_phase: float
    identity: StreamIdentity
    receipt_ns: int
    channel_count: int = 1
    sensor_transform_valid: bool = True


@dataclass(frozen=True)
class AugmentedCost:
    legacy_stamp_sec: float
    values: Tuple[float, ...]
    objective: ObjectiveIdentity
    receipt_ns: int
    oldest_receipt_ns: Optional[int] = None


@dataclass(frozen=True)
class SynchronizedObservation:
    observation_id: int
    identity: StreamIdentity
    objective: ObjectiveIdentity
    source_sequence: int
    source_stamp_ns: int
    cost_source_stamp_ns: int
    legacy_cost_source_timestamp_sec: float
    pose_left_stamp_ns: int
    pose_right_stamp_ns: int
    encoder_left_stamp_ns: int
    encoder_right_stamp_ns: int
    receipt_stamp_ns: int
    base_xy: Vector
    base_yaw: float
    encoder_phase: float
    sensor_world_phase: float
    sensor_xy: Vector
    demodulation_phase_rad: float
    raw_cost: float
    augmented_cost: float
    sync_error_ns: int
    demodulation_phase_reconstructed: bool = True
    sensor_transform_observed: bool = True
    oldest_receipt_stamp_ns: Optional[int] = None
    admission_stamp_ns: Optional[int] = None


@dataclass(frozen=True)
class SyncFault:
    reason: str
    legacy_stamp_sec: Optional[float] = None


@dataclass(frozen=True)
class SyncBatch:
    observations: Tuple[SynchronizedObservation, ...] = ()
    faults: Tuple[SyncFault, ...] = ()
    reset_sequence: int = 0
    retired_keys: Tuple[float, ...] = ()


class SourceSynchronizer:
    """Bounded exact-key join followed by source-time bracketing.

Receipt times are ROS clock times supplied by the adapter, never wall time.
Identical retransmissions do not refresh the original receipt. A fault drops
pending history; the adapter must invalidate its rolling/filter context as
appropriate before processing another batch. A batch with faults has no
observations. Used/poisoned keys remain tombstoned within the source horizon.
"""

    def __init__(self, config=GescSyncConfig()):
        self.config = config
        self.identity = None
        self.reset_sequence = 0
        self._now = None
        self._observation_id = 0
        self._last_source = None
        self._last_sequence = None
        self._poses = []
        self._encoders = []
        self._poisoned_support = (OrderedDict(), OrderedDict())
        self._pending = {}
        self._used = OrderedDict()
        self._retired = OrderedDict()

    def _batch(self, observations=(), faults=()):
        return SyncBatch(tuple(observations), tuple(faults), self.reset_sequence)

    def invalidate(self, reason):
        self.reset_sequence += 1
        self._poses.clear()
        self._encoders.clear()
        self._pending.clear()
        self._last_source = None
        self._last_sequence = None
        return self._batch(faults=(SyncFault(str(reason)),))

    def is_retired(self, key):
        """Expiry-only tombstones do not replace consumed/conflicting keys."""
        return (self.identity is not None
                and self.identity.cost_key_basis == "model_input_time"
                and key in self._retired and key not in self._used)

    def retire_keys(self, keys, now_ns=None):
        """Boundedly retire discarded joins, preserving support and hard poison."""
        if self.identity is None or self.identity.cost_key_basis != "model_input_time":
            return ()
        now = self._now if now_ns is None else now_ns
        if not _ns(now) or now < self.identity.time_origin_ns:
            return ()
        retired = []
        for key in keys:
            try:
                source = self._absolute_key(key)
                uncertainty = publication_time_tolerance_ns(self.identity.time_origin_ns, key, now)
            except (TypeError, ValueError, OverflowError):
                continue
            if source > now + self.config.freshness_ns + uncertainty or key in self._used:
                continue
            if key not in self._retired:
                self._retired[key] = None
                retired.append(key)
        # The adapter can hold a disjoint full partial queue while this core
        # holds fully joined costs awaiting support. Retain their whole union.
        while len(self._retired) > 2 * self.config.max_pending_costs:
            self._retired.popitem(last=False)
        return tuple(retired)

    def expire_pending(self, reason="pending_expired", extra_keys=(), now_ns=None):
        """Restart numerical evidence after join loss without losing support."""
        if self.identity is None or self.identity.cost_key_basis != "model_input_time":
            return self.invalidate(reason)
        if now_ns is not None:
            fault = self._clock(now_ns)
            if fault:
                return fault
        retired = self.retire_keys((*self._pending, *extra_keys), now_ns)
        self._pending.clear()
        self.reset_sequence += 1
        # A cost-join expiry says nothing adverse about independent support.
        # Keep its original receipts and source/sequence order frontiers.
        return replace(self._batch(faults=(SyncFault(str(reason)),)), retired_keys=retired)

    def set_context(self, identity):
        if not isinstance(identity, StreamIdentity) or not all(
            isinstance(v, str) and v.strip()
            for v in (identity.run_id, identity.stream_contract_id, identity.frame_id)
        ) or not _ns(identity.time_origin_ns) or not _ns(identity.channel_index) or identity.cost_key_basis not in (
            "publication_time", "model_input_time"
        ):
            raise ValueError("invalid stream identity")
        if identity == self.identity:
            return self._batch()
        self.identity = identity
        self._used.clear()
        self._retired.clear()
        for poisoned in self._poisoned_support:
            poisoned.clear()
        self._now = None
        return self.invalidate("context_changed")

    def _fault(self, reason, key=None):
        if (reason == "pending_expired" and self.identity is not None
                and self.identity.cost_key_basis == "model_input_time"):
            return replace(self.expire_pending(reason), faults=(SyncFault(reason, key),))
        result = self.invalidate(reason)
        if key is not None:
            self._used[key] = None
            self._trim_used()
        return replace(result, faults=(SyncFault(reason, key),))

    def invalidate_key(self, key, reason="source_key_invalidated"):
        """A source-owner invalidation cannot be undone by late valid packets."""
        self._absolute_key(key)
        return self._fault(reason, key)

    def _trim_used(self):
        while len(self._used) > self.config.max_pending_costs:
            self._used.popitem(last=False)

    def _clock(self, now_ns):
        if not _ns(now_ns) or self.identity is None:
            return self._fault("invalid_clock_or_context")
        if now_ns < self.identity.time_origin_ns:
            return self._fault("clock_before_origin")
        if self._now is not None and now_ns < self._now:
            self._now = now_ns
            return self._fault("clock_rollback")
        self._now = now_ns
        return None

    def _fresh(self, stamp, receipt, now):
        if self.identity.cost_key_basis == "model_input_time":
            # Source headers can lead this subscriber's held /clock. Admission
            # waits below; retaining the original receipt does not restamp data.
            return (_ns(stamp) and _ns(receipt)
                    and stamp >= self.identity.time_origin_ns
                    and abs(now-stamp) <= self.config.freshness_ns
                    and 0 <= now-receipt <= self.config.freshness_ns)
        return (_ns(stamp) and _ns(receipt)
                and 0 <= now - stamp <= self.config.freshness_ns
                and stamp <= receipt <= now
                and now - receipt <= self.config.freshness_ns)

    def latest_admitted_pose(self, now_ns):
        """Most recent source pose covered by clock and original freshness."""
        return next((pose for pose in reversed(self._poses)
                     if pose.stamp_ns <= now_ns
                     and self._fresh(pose.stamp_ns, pose.receipt_ns, now_ns)), None)

    def _absolute_key(self, key):
        if not _finite(key) or key < 0:
            raise ValueError("invalid_cost_key")
        scaled = key * 1e9
        if not _finite(scaled):
            raise ValueError("invalid_cost_key")
        result = self.identity.time_origin_ns + round(scaled)
        if not _ns(result):
            raise ValueError("invalid_cost_key")
        return result

    @staticmethod
    def _same(a, b):
        # A retransmission cannot extend freshness by replacing its receipt.
        if isinstance(a, AugmentedCost) and isinstance(b, AugmentedCost):
            return replace(a, receipt_ns=0, oldest_receipt_ns=None) == replace(b, receipt_ns=0, oldest_receipt_ns=None)
        return replace(a, receipt_ns=0) == replace(b, receipt_ns=0)

    @staticmethod
    def _oldest_receipt(value):
        oldest = getattr(value, "oldest_receipt_ns", None)
        return value.receipt_ns if oldest is None else oldest

    def add_pose(self, sample, now_ns):
        return self._add_support(sample, now_ns, True)

    def add_encoder(self, sample, now_ns):
        return self._add_support(sample, now_ns, False)

    def _add_support(self, sample, now, pose):
        fault = self._clock(now)
        if fault:
            return fault
        correct_type = isinstance(sample, PoseSample if pose else EncoderSample)
        valid = correct_type and self._fresh(sample.stamp_ns, sample.receipt_ns, now)
        if pose:
            valid = valid and sample.frame_id == self.identity.frame_id and _vector(sample.xy) and _finite(sample.yaw)
        else:
            valid = valid and _finite(sample.phase)
        if not valid:
            return self._fault("invalid_pose" if pose else "invalid_encoder")
        poisoned = self._poisoned_support[0 if pose else 1]
        if sample.stamp_ns in poisoned:
            return self.poll(now)
        records = self._poses if pose else self._encoders
        if records and sample.stamp_ns <= records[-1].stamp_ns:
            if sample.stamp_ns == records[-1].stamp_ns and self._same(sample, records[-1]):
                return self.poll(now)
            if sample.stamp_ns == records[-1].stamp_ns:
                poisoned[sample.stamp_ns] = None
                while len(poisoned) > self.config.max_source_samples:
                    poisoned.popitem(last=False)
            return self._fault("support_rollback_or_conflict")
        records.append(sample)
        cutoff = sample.stamp_ns - self.config.buffer_span_ns
        while len(records) > 1 and records[1].stamp_ns < cutoff:
            records.pop(0)
        if len(records) > self.config.max_source_samples:
            return self._fault("support_capacity")
        return self._drain(now)

    def add_raw_cost(self, sample, now_ns):
        return self._add_component("raw", sample, now_ns)

    def add_provenance(self, sample, now_ns):
        return self._add_component("provenance", sample, now_ns)

    def add_augmented(self, sample, now_ns):
        return self._add_component("augmented", sample, now_ns)

    def _add_component(self, kind, sample, now):
        fault = self._clock(now)
        if fault:
            return fault
        expected = {"raw": RawCost, "provenance": Provenance, "augmented": AugmentedCost}[kind]
        if not isinstance(sample, expected):
            return self._fault("invalid_component")
        key = sample.legacy_stamp_sec
        try:
            publication = self._absolute_key(key)
        except (TypeError, ValueError, OverflowError):
            return self._fault("invalid_cost_key")
        retired = self.is_retired(key)
        # Until provenance arrives the key-derived stamp is only a float
        # reconstruction. Permit its declared ULP uncertainty at time bounds;
        # the separately observed integer publication stamp stays strict below.
        try:
            key_error = publication_time_tolerance_ns(self.identity.time_origin_ns, key, sample.receipt_ns)
        except (TypeError, ValueError, OverflowError):
            return self._fault("invalid_receipt", key)
        model_key = self.identity.cost_key_basis == "model_input_time"
        ahead = self.config.freshness_ns if model_key else 0
        if (not _ns(sample.receipt_ns) or sample.receipt_ns > now
                or not retired and now-sample.receipt_ns > self.config.freshness_ns
                or now-publication < -ahead-key_error
                or not retired and now-publication > self.config.freshness_ns+key_error
                or not model_key and publication > sample.receipt_ns + key_error):
            return self._fault("stale_or_future_cost", key)
        if kind == "provenance":
            actual_publication = sample.cost_publication_ns
            try:
                publication_consistent = (
                    abs((sample.model_input_ns if model_key else actual_publication) - publication)
                    <= publication_time_tolerance_ns(self.identity.time_origin_ns, key,
                                                     sample.model_input_ns if model_key else actual_publication)
                )
            except (TypeError, ValueError, OverflowError):
                publication_consistent = False
            if (sample.identity != self.identity or not _ns(sample.source_sequence)
                    or not _ns(sample.model_input_ns) or not _ns(actual_publication)
                    or sample.model_input_ns < self.identity.time_origin_ns
                    or sample.model_input_ns > actual_publication
                    or actual_publication > (now + ahead if model_key else sample.receipt_ns)
                    or not retired and now - sample.model_input_ns > self.config.freshness_ns
                    or not publication_consistent
                    or not _ns(sample.channel_count) or sample.channel_count <= self.identity.channel_index
                    or not sample.sensor_transform_valid or not _vector(sample.sensor_xy)
                    or not _finite(sample.sensor_world_phase)):
                return self._fault("invalid_provenance", key)
        else:
            if (not isinstance(sample.values, tuple) or len(sample.values) <= self.identity.channel_index
                    or not _finite(*sample.values)):
                return self._fault("invalid_cost_values", key)
            if kind == "augmented" and not _objective_valid(sample.objective):
                return self._fault("invalid_objective", key)
            if kind == "augmented" and (not _ns(self._oldest_receipt(sample))
                    or not self._oldest_receipt(sample) <= sample.receipt_ns
                    or not retired and now-self._oldest_receipt(sample) > self.config.freshness_ns):
                return self._fault("invalid_augmented_receipt", key)
        if retired:
            # Only old age is immaterial for discarded keys. Structure/context
            # remain validated above; no receipt or pending record is refreshed.
            return self._batch()
        if key in self._used:
            used = self._used[key]
            if used is not None and kind in used and self._same(used[kind], sample):
                return self._drain(now)
            return self._fault("conflicting_or_poisoned_key", key)
        entry = self._pending.setdefault(key, {})
        if kind in entry:
            if self._same(entry[kind], sample):
                return self._drain(now)
            return self._fault("conflicting_duplicate", key)
        entry[kind] = sample
        if len(self._pending) > self.config.max_pending_costs:
            return self._fault("pending_capacity", key)
        return self._drain(now)

    def poll(self, now_ns):
        fault = self._clock(now_ns)
        return fault if fault else self._drain(now_ns)

    def _bracket(self, records, target, now):
        index = bisect_left([v.stamp_ns for v in records], target)
        if index < len(records) and records[index].stamp_ns == target:
            left = right = records[index]
        elif index == 0 or index == len(records):
            return None
        else:
            left, right = records[index - 1], records[index]
        if max(target - left.stamp_ns, right.stamp_ns - target) > self.config.sync_tolerance_ns:
            return None
        if any(not 0 <= now - v.receipt_ns <= self.config.freshness_ns for v in (left, right)):
            return None
        if left.stamp_ns > now or right.stamp_ns > now:
            return None
        return left, right

    def _drain(self, now):
        for key, entry in tuple(self._pending.items()):
            source = entry.get("provenance")
            stamp = source.model_input_ns if source else self._absolute_key(key)
            if now - stamp > self.config.freshness_ns or any(
                now - self._oldest_receipt(value) > self.config.freshness_ns for value in entry.values()
            ):
                return self._fault("pending_expired", key)
        output = []
        for key in sorted(key for key, entry in self._pending.items() if "raw" in entry):
            entry = self._pending[key]
            if len(entry) != 3:
                break  # Earlier admitted raw costs own ordering, not callback order.
            raw, augmented, provenance = (entry[name] for name in ("raw", "augmented", "provenance"))
            target = provenance.model_input_ns
            if any(target in poisoned for poisoned in self._poisoned_support):
                return self._fault('poisoned_support_target', key)
            if max(target, provenance.cost_publication_ns) > now:
                break
            if len(raw.values) != provenance.channel_count or len(augmented.values) != provenance.channel_count:
                return self._fault("channel_count_mismatch", key)
            if ((self._last_source is not None and target <= self._last_source)
                    or (self._last_sequence is not None and provenance.source_sequence <= self._last_sequence)):
                return self._fault("source_rollback", key)
            pose = self._bracket(self._poses, target, now)
            encoder = self._bracket(self._encoders, target, now)
            if pose is None or encoder is None:
                break
            pl, pr = pose
            el, er = encoder
            pf = 0.0 if pl is pr else (target - pl.stamp_ns) / (pr.stamp_ns - pl.stamp_ns)
            ef = 0.0 if el is er else (target - el.stamp_ns) / (er.stamp_ns - el.stamp_ns)
            try:
                xy = tuple(_lerp(a, b, pf) for a, b in zip(pl.xy, pr.xy))
                yaw = wrap_angle(pl.yaw + pf * _angular_delta(pl.yaw, pr.yaw))
                phase = wrap_angle(el.phase + ef * _angular_delta(el.phase, er.phase))
                world_phase = wrap_angle(provenance.sensor_world_phase)
                demod = wrap_angle(world_phase - yaw)
            except (ArithmeticError, ValueError, OverflowError):
                return self._fault("invalid_interpolation", key)
            self._observation_id += 1
            output.append(SynchronizedObservation(
                self._observation_id, self.identity, augmented.objective, provenance.source_sequence,
                target, provenance.cost_publication_ns, key, pl.stamp_ns, pr.stamp_ns,
                el.stamp_ns, er.stamp_ns,
                max(v.receipt_ns for v in (raw, augmented, provenance, pl, pr, el, er)),
                xy, yaw, phase, world_phase, provenance.sensor_xy, demod,
                raw.values[self.identity.channel_index], augmented.values[self.identity.channel_index],
                max(target - pl.stamp_ns, pr.stamp_ns - target,
                    target - el.stamp_ns, er.stamp_ns - target),
                oldest_receipt_stamp_ns=min(self._oldest_receipt(v) for v in (raw, augmented, provenance, pl, pr, el, er)),
                admission_stamp_ns=now,
            ))
            self._last_source = target
            self._last_sequence = provenance.source_sequence
            self._used[key] = entry
            self._trim_used()
            del self._pending[key]
        return self._batch(output)


def _objective_valid(value):
    return (isinstance(value, ObjectiveIdentity) and _ns(value.revision)
            and _ns(value.affine_revision) and isinstance(value.registry_digest, str)
            and _finite(value.sensor_weight, value.gaussian_weight, value.affine_weight))


@dataclass(frozen=True)
class RollingGescConfig:
    max_gap_ns: int = 500_000_000
    max_cycle_duration_ns: int = 30_000_000_000
    max_samples: int = 20_000
    blend_weight: float = 0.5
    sectors: int = 12
    min_sector_samples: int = 2
    confidence_cycles: int = 3
    max_pair_angle_rad: float = math.pi / 6
    absolute_magnitude_floor: float = 1e-6
    variability_multiplier: float = 3.0
    freshness_ns: int = 500_000_000
    direction_policy: str = THREE_CYCLE_POLICY

    def __post_init__(self):
        validate_policy(self.direction_policy)
        for name in ("max_gap_ns", "max_cycle_duration_ns", "max_samples", "sectors",
                     "min_sector_samples", "confidence_cycles", "freshness_ns"):
            if not _ns(getattr(self, name)) or getattr(self, name) == 0:
                raise ValueError("rolling bounds must be positive integers")
        if self.sectors != 12 or self.confidence_cycles != 3 or self.min_sector_samples != 2:
            raise ValueError("frozen confidence contract requires 12 sectors, 2 samples, 3 cycles")
        if (not _finite(self.blend_weight, self.max_pair_angle_rad,
                        self.absolute_magnitude_floor, self.variability_multiplier)
                or not 0 <= self.blend_weight <= 1 or not 0 <= self.max_pair_angle_rad <= math.pi
                or self.absolute_magnitude_floor <= 0 or self.variability_multiplier < 0):
            raise ValueError("invalid rolling configuration")
        if self.direction_policy == MOVING_CYCLE_POLICY:
            frozen = dict(max_gap_ns=500_000_000, max_cycle_duration_ns=30_000_000_000,
                          max_samples=20_000, absolute_magnitude_floor=1e-6,
                          freshness_ns=500_000_000, max_pair_angle_rad=math.pi/6,
                          variability_multiplier=3.0)
            if any(getattr(self, name) != value for name, value in frozen.items()):
                raise ValueError("moving policy requires its fixed numerical descriptor")


@dataclass(frozen=True)
class DemodulatedSample:
    observation: SynchronizedObservation
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
    observation: Optional[SynchronizedObservation] = None
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
    max_pair_angle_rad: Optional[float] = None
    cycle_variability: Optional[float] = None
    effective_magnitude_floor: Optional[float] = None
    actual_blend_weight: float = 0.0
    mean_full: bool = False
    coverage_valid: bool = False
    cycles_valid: bool = False
    qualified: bool = False
    fallback_used: bool = False
    output_valid: bool = False
    reset_sequence: int = 0
    reset_reason: str = ""
    fallback_reason: str = "initializing"
    direction_policy: str = THREE_CYCLE_POLICY
    policy_config_sha256: str = ""
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


class RollingGesc:
    """World-vector temporal quadrature with independent whole-cycle confidence."""

    def __init__(self, config=RollingGescConfig()):
        self.config = config
        self._policy_sha256 = policy_config_sha256(config.direction_policy)
        self._norm_cache = None
        if config.direction_policy == MOVING_CYCLE_POLICY:
            from .cycle_coherence import NormCache
            self._norm_cache = NormCache()
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
        self._result = RollingResult(direction_policy=config.direction_policy,
                                     policy_config_sha256=self._policy_sha256)
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
        if self._norm_cache is not None:
            self._norm_cache.clear()
        self._result = RollingResult(reset_sequence=self.reset_sequence,
                                     reset_reason=self.reset_reason, fallback_reason=self.reset_reason,
                                     direction_policy=self.config.direction_policy,
                                     policy_config_sha256=self._policy_sha256,
                                     coherence_reason=self.reset_reason if self._norm_cache is not None
                                     else "not_selected")
        return self._result

    def set_context(self, stream_identity, objective_identity):
        if not isinstance(stream_identity, StreamIdentity) or not _objective_valid(objective_identity):
            raise ValueError("invalid rolling context")
        if stream_identity != self.identity:
            self.identity, self.objective = stream_identity, objective_identity
            return self.invalidate("context_changed")
        if objective_identity != self.objective:
            if self.objective is not None and objective_identity.revision <= self.objective.revision:
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
        self._result = self._snapshot(reason or "initializing")
        return self._result

    def update(self, sample):
        if (not isinstance(sample, DemodulatedSample) or not _vector(sample.q_body)
                or not isinstance(sample.observation, SynchronizedObservation)):
            return self.invalidate("invalid_sample")
        obs = sample.observation
        if (not isinstance(obs.identity, StreamIdentity)
                or not _ns(obs.source_stamp_ns) or not _ns(obs.observation_id)
                or not _ns(obs.receipt_stamp_ns)
                or (obs.identity.cost_key_basis == "publication_time"
                    and obs.receipt_stamp_ns < obs.source_stamp_ns)
                or (obs.identity.cost_key_basis == "model_input_time"
                    and (not _ns(obs.admission_stamp_ns)
                         or obs.admission_stamp_ns < max(obs.source_stamp_ns, obs.cost_source_stamp_ns,
                                                        obs.pose_right_stamp_ns, obs.encoder_right_stamp_ns,
                                                        obs.receipt_stamp_ns)))
                or not _objective_valid(obs.objective)
                or not _finite(obs.base_yaw, obs.sensor_world_phase)
                or (obs.oldest_receipt_stamp_ns is not None
                    and (not _ns(obs.oldest_receipt_stamp_ns)
                         or obs.oldest_receipt_stamp_ns > obs.receipt_stamp_ns))):
            return self.invalidate("invalid_sample")
        if self.identity is not None and obs.identity == self.identity and self.objective is not None:
            if obs.objective != self.objective and obs.objective.revision <= self.objective.revision:
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
            if self._norm_cache is not None:
                self._norm_cache.begin_update()
                self._norm_cache.append(previous, point)
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
            # Keep the first crossing support (including plateaus) and current
            # anchored-cycle support; confidence itself retains only summaries.
            if self._direction and self._result.mean_full:
                cutoff = min(self._result.rolling_start_ns, self._cycle_start.stamp_ns)
                while len(self._points) > 2 and self._points[1].stamp_ns < cutoff:
                    self._points.pop(0)
                if self._norm_cache is not None:
                    self._norm_cache.prune(self._points)
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
        covered = (all(c >= self.config.min_sector_samples for c in counts)
                   and gap <= self.config.max_gap_ns and duration <= self.config.max_cycle_duration_ns)
        return CycleSummary(start.stamp_ns, end.stamp_ns, start.phase, end.phase,
                            mean, tuple(counts), sum(counts), gap, covered)

    def _snapshot(self, reason=""):
        result = self._snapshot_legacy(reason)
        result = replace(result, direction_policy=self.config.direction_policy,
                         policy_config_sha256=self._policy_sha256)
        if self._norm_cache is None:
            return result
        warmup = len(result.cycles) == 3 and all(c.coverage_valid for c in result.cycles)
        result = replace(result, qualified=False, warmup_valid=warmup,
                         norm_new_evaluations=self._norm_cache.budget.calls,
                         coherence_reason=result.fallback_reason)
        if not result.mean_full or not result.coverage_valid:
            return result
        if not warmup:
            reason = "incomplete_cycle_confidence" if len(result.cycles) < 3 else "incomplete_cycle_coverage"
            return replace(result, coherence_reason=reason, fallback_reason=reason)
        if result.mean_magnitude <= self.config.absolute_magnitude_floor:
            return replace(result, coherence_reason="weak_current_mean", fallback_reason="weak_current_mean")
        start = self._crossing(result.phase_start)
        value = self._norm_cache.evaluate(start, self._points[-1], self._points, result.mean_world)
        return replace(result, qualified=value['qualified'],
                       norm_denominator=value['denominator'], norm_error=value['denominator_error'],
                       coherence=value['coherence'], coherence_lower=value['lower'],
                       coherence_upper=value['upper'], coherence_available=value['available'],
                       coherence_reason=value['reason'],
                       norm_new_evaluations=self._norm_cache.budget.calls,
                       norm_window_evaluations=value['window_evaluations'],
                       fallback_reason="" if value['qualified'] else value['reason'])

    def _snapshot_legacy(self, reason=""):
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
        means = [c.mean_world for c in self._cycles]
        center = tuple(math.fsum(v[k] / 3.0 for v in means) for k in range(2))
        variability = math.hypot(*(math.hypot(v[0] - center[0], v[1] - center[1])
                                   / math.sqrt(3.0) for v in means))
        floor = max(self.config.absolute_magnitude_floor,
                    self.config.variability_multiplier * variability)
        if not _finite(variability, floor):
            raise ArithmeticError("numerical_overflow")
        norms = [math.hypot(*v) for v in means]
        result = replace(result, cycle_variability=variability, effective_magnitude_floor=floor)
        if min(norms + [result.mean_magnitude]) <= floor:
            return replace(result, fallback_reason="weak_cycle_direction")
        angles = [math.acos(max(-1.0, min(1.0,
                     (means[i][0] / norms[i]) * (means[j][0] / norms[j])
                     + (means[i][1] / norms[i]) * (means[j][1] / norms[j]))))
                  for i, j in ((0, 1), (0, 2), (1, 2))]
        angle = max(angles)
        valid = angle <= self.config.max_pair_angle_rad
        return replace(result, max_pair_angle_rad=angle, cycles_valid=valid,
                       qualified=valid, fallback_reason="" if valid else "cycle_disagreement")

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
                or not 0 <= now_ns - obs.source_stamp_ns <= self.config.freshness_ns
                or not 0 <= now_ns - obs.receipt_stamp_ns <= self.config.freshness_ns
                or (obs.admission_stamp_ns is not None and obs.admission_stamp_ns > now_ns)
                or (obs.oldest_receipt_stamp_ns is not None
                    and not 0 <= now_ns - obs.oldest_receipt_stamp_ns <= self.config.freshness_ns)
                or not 0 <= now_ns - output_pose_stamp_ns <= self.config.freshness_ns):
            return replace(result, output_valid=False, fallback_used=False,
                           actual_blend_weight=0.0, final_body=None, final_magnitude=None,
                           fallback_reason="stale_or_invalid_output_input")
        if self._norm_cache is not None:
            return self._evaluate_moving(result, output_yaw, output_pose_stamp_ns)
        weight = self.config.blend_weight if result.qualified else 0.0
        try:
            world = result.instant_world if weight == 0 else tuple(
                (1.0 - weight) * a + weight * b
                for a, b in zip(result.instant_world, result.mean_world))
            body = _rotation(world, -output_yaw)
            magnitude = math.hypot(*body)
            if not _finite(magnitude):
                raise ArithmeticError("numerical_overflow")
        except (ArithmeticError, ValueError, OverflowError):
            return self.invalidate("numerical_overflow")
        return replace(result, final_body=body, final_magnitude=magnitude,
                       output_yaw=output_yaw, output_pose_stamp_ns=output_pose_stamp_ns,
                       actual_blend_weight=weight, output_valid=True,
                       fallback_used=not result.qualified)

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
