"""ROS-independent GESC/Gaussian supervisor state machine."""

from collections import deque
from dataclasses import dataclass
from enum import IntEnum
import math
import statistics
from typing import Optional, Tuple


LEGACY_PROFILE = "legacy"
ROBUST_PROFILE = "robust_gaussian_v1"
VALID_PROFILES = (LEGACY_PROFILE, ROBUST_PROFILE)
ABSOLUTE_SOURCE_SCORE = "absolute_source_score"
COUNTED_CANDIDATES = "counted_candidates"
VALID_EXTREMUM_CLASSIFICATION_MODES = (
    ABSOLUTE_SOURCE_SCORE,
    COUNTED_CANDIDATES,
)
CANDIDATE_INFORMED_FILL_HEADER = (
    "ROBUST_FILL_CREATE:CANDIDATE_RAW_COST_V1"
)
CANDIDATE_INFORMED_FILL_BASE_VALUE_COUNT = 8
CANDIDATE_INFORMED_FILL_EVIDENCE_VALUE_COUNT = 5


class State(IntEnum):
    """Values intentionally match ros_esc_interfaces/AlgorithmState."""

    SEARCH = 1
    VERIFY_EXTREMUM = 2
    DESIGN_OR_MERGE_FILL = 3
    ESCAPE_REPULSE = 4
    ESCAPE_ASSIST = 5
    RECENTER = 6
    GOAL_HOLD = 7
    FAILSAFE = 8


STATE_WEIGHTS = {
    State.SEARCH: (1.0, 1.0, 0.0),
    State.VERIFY_EXTREMUM: (1.0, 1.0, 0.0),
    State.DESIGN_OR_MERGE_FILL: (0.0, 1.0, 0.0),
    State.ESCAPE_REPULSE: (0.0, 1.0, 0.0),
    State.ESCAPE_ASSIST: (0.0, 1.0, 1.0),
    State.RECENTER: (0.0, 1.0, 0.0),
    State.GOAL_HOLD: (0.0, 1.0, 0.0),
    State.FAILSAFE: (0.0, 0.0, 0.0),
}


@dataclass(frozen=True)
class StateMachineConfig:
    """Time and policy settings owned by the supervisor."""

    convergence_hold_sec: float = 2.0
    goal_score_threshold: float = 0.95
    goal_hold_sec: float = 3.0
    undesired_score_hold_sec: float = 3.0
    verification_max_sec: float = 12.0
    fill_design_timeout_sec: float = 5.0
    escape_max_sec: float = 20.0
    open_field_escape_assist_enabled: bool = False
    open_field_escape_approach_continuity_enabled: bool = False
    open_field_escape_active_fill_transit_enabled: bool = False
    open_field_escape_supervisor_owned_assist_enabled: bool = False
    recenter_after_escape: bool = True
    recenter_max_sec: float = 30.0
    max_fill_clusters: int = 0
    post_recovery_guidance_enabled: bool = False
    post_recovery_guidance_max_sec: float = 0.0
    post_recovery_retry_limit: int = 0
    recoverable_navigation_enabled: bool = False
    recovery_retry_limit: int = 0
    extremum_classification_mode: str = ABSOLUTE_SOURCE_SCORE
    known_source_count: int = 0
    candidate_cost_rotation_period_sec: float = 3.0
    candidate_cost_required_rotations: int = 2
    candidate_cost_pretrigger_rotations: int = 0
    candidate_cost_mad_scale: float = 3.0
    candidate_informed_fill_enabled: bool = False

    def __post_init__(self):
        mode = str(self.extremum_classification_mode).strip().lower()
        if mode not in VALID_EXTREMUM_CLASSIFICATION_MODES:
            raise ValueError(
                "extremum_classification_mode must be one of "
                + ", ".join(VALID_EXTREMUM_CLASSIFICATION_MODES)
            )
        object.__setattr__(self, "extremum_classification_mode", mode)
        durations = (
            self.convergence_hold_sec,
            self.goal_hold_sec,
            self.undesired_score_hold_sec,
            self.verification_max_sec,
            self.fill_design_timeout_sec,
            self.escape_max_sec,
            self.recenter_max_sec,
        )
        if not all(math.isfinite(value) and value > 0.0 for value in durations):
            raise ValueError("all supervisor durations must be finite and positive")
        if not math.isfinite(self.goal_score_threshold):
            raise ValueError("goal_score_threshold must be finite")
        if (
            not math.isfinite(float(self.candidate_cost_mad_scale))
            or float(self.candidate_cost_mad_scale) < 0.0
        ):
            raise ValueError("candidate_cost_mad_scale must be finite and nonnegative")
        if (
            not math.isfinite(float(self.candidate_cost_rotation_period_sec))
            or float(self.candidate_cost_rotation_period_sec) <= 0.0
        ):
            raise ValueError(
                "candidate_cost_rotation_period_sec must be finite and positive"
            )
        if (
            isinstance(self.candidate_cost_required_rotations, bool)
            or not isinstance(self.candidate_cost_required_rotations, int)
            or self.candidate_cost_required_rotations <= 0
        ):
            raise ValueError(
                "candidate_cost_required_rotations must be a positive integer"
            )
        if (
            isinstance(self.candidate_cost_pretrigger_rotations, bool)
            or not isinstance(self.candidate_cost_pretrigger_rotations, int)
            or self.candidate_cost_pretrigger_rotations < 0
        ):
            raise ValueError(
                "candidate_cost_pretrigger_rotations must be a "
                "nonnegative integer"
            )
        if self.candidate_cost_pretrigger_rotations > 0:
            if mode != COUNTED_CANDIDATES:
                raise ValueError(
                    "candidate pretrigger rotations require "
                    "counted-candidate classification"
                )
            if (
                self.candidate_cost_pretrigger_rotations
                < self.candidate_cost_required_rotations
            ):
                raise ValueError(
                    "candidate_cost_pretrigger_rotations must be zero or "
                    "at least candidate_cost_required_rotations"
                )
        if not isinstance(self.candidate_informed_fill_enabled, bool):
            raise ValueError("candidate_informed_fill_enabled must be boolean")
        if (
            self.candidate_informed_fill_enabled
            and mode != COUNTED_CANDIDATES
        ):
            raise ValueError(
                "candidate-informed fill requires counted-candidate "
                "classification"
            )
        if (
            isinstance(self.max_fill_clusters, bool)
            or not isinstance(self.max_fill_clusters, int)
            or self.max_fill_clusters < 0
        ):
            raise ValueError("max_fill_clusters must be a nonnegative integer")
        if (
            isinstance(self.known_source_count, bool)
            or not isinstance(self.known_source_count, int)
            or self.known_source_count < 0
        ):
            raise ValueError("known_source_count must be a nonnegative integer")
        if self.extremum_classification_mode == COUNTED_CANDIDATES:
            if self.known_source_count < 2:
                raise ValueError(
                    "counted-candidate classification requires at least two sources"
                )
            required_fills = self.known_source_count - 1
            if self.max_fill_clusters != required_fills:
                raise ValueError(
                    "counted-candidate classification requires "
                    "max_fill_clusters == known_source_count - 1"
                )
        if not isinstance(self.open_field_escape_assist_enabled, bool):
            raise ValueError(
                "open_field_escape_assist_enabled must be boolean"
            )
        if not isinstance(
            self.open_field_escape_approach_continuity_enabled,
            bool,
        ):
            raise ValueError(
                "open_field_escape_approach_continuity_enabled must be "
                "boolean"
            )
        if not isinstance(
            self.open_field_escape_active_fill_transit_enabled,
            bool,
        ):
            raise ValueError(
                "open_field_escape_active_fill_transit_enabled must be "
                "boolean"
            )
        if not isinstance(
            self.open_field_escape_supervisor_owned_assist_enabled,
            bool,
        ):
            raise ValueError(
                "open_field_escape_supervisor_owned_assist_enabled must be "
                "boolean"
            )
        if self.open_field_escape_assist_enabled and (
            self.recenter_after_escape
            or self.post_recovery_guidance_enabled
            or self.recoverable_navigation_enabled
        ):
            raise ValueError(
                "open-field escape assist requires recenter, recoverable "
                "navigation, and post-recovery guidance to be disabled"
            )
        if self.open_field_escape_approach_continuity_enabled:
            if not self.open_field_escape_assist_enabled:
                raise ValueError(
                    "open-field escape approach continuity requires "
                    "open-field escape assist"
                )
            if not self.candidate_informed_fill_enabled:
                raise ValueError(
                    "open-field escape approach continuity requires "
                    "candidate-informed fill"
                )
        if (
            self.open_field_escape_active_fill_transit_enabled
            and not self.open_field_escape_approach_continuity_enabled
        ):
            raise ValueError(
                "open-field escape active-fill transit requires "
                "approach continuity"
            )
        if (
            self.open_field_escape_supervisor_owned_assist_enabled
            and not self.open_field_escape_active_fill_transit_enabled
        ):
            raise ValueError(
                "open-field escape supervisor-owned assist requires "
                "active-fill transit"
            )
        if (
            isinstance(self.post_recovery_retry_limit, bool)
            or not isinstance(self.post_recovery_retry_limit, int)
            or self.post_recovery_retry_limit < 0
        ):
            raise ValueError(
                "post_recovery_retry_limit must be a nonnegative integer"
            )
        if (
            isinstance(self.recovery_retry_limit, bool)
            or not isinstance(self.recovery_retry_limit, int)
            or self.recovery_retry_limit < 0
        ):
            raise ValueError('recovery_retry_limit must be a nonnegative integer')
        if (
            self.recoverable_navigation_enabled
            and self.recovery_retry_limit <= 0
        ):
            raise ValueError(
                'recoverable navigation requires a positive recovery retry limit'
            )
        if self.post_recovery_guidance_enabled:
            if self.max_fill_clusters <= 0:
                raise ValueError(
                    "post-recovery guidance requires a positive fill-cluster limit"
                )
            if (
                not math.isfinite(self.post_recovery_guidance_max_sec)
                or self.post_recovery_guidance_max_sec <= 0.0
            ):
                raise ValueError(
                    "post-recovery guidance duration must be finite and positive"
                )
            if self.post_recovery_retry_limit <= 0:
                raise ValueError(
                    "post-recovery guidance requires a positive retry limit"
                )


@dataclass(frozen=True)
class TransitionInputs:
    """One deterministic input sample for the state machine."""

    convergence: bool = False
    convergence_confirmed: bool = False
    source_score: Optional[float] = None
    source_score_observed: bool = True
    source_score_valid: bool = False
    source_score_ready: bool = True
    candidate_cost_observed: bool = True
    candidate_cost_valid: bool = False
    candidate_cost_ready: bool = True
    candidate_cost_summary: Optional["CandidateCostSummary"] = None
    candidate_associated_with_fill: bool = False
    pose_valid: bool = True
    sensor_valid: bool = True
    explicit_stop: bool = False
    controller_fault: bool = False
    fill_result: Optional[str] = None
    fill_source_timestamp: Optional[float] = None
    fill_id: Optional[int] = None
    active_fill_count: Optional[int] = None
    stable_exit: bool = False
    stalled: bool = False
    recenter_complete: bool = False
    recenter_recovery_requested: bool = False
    recenter_recovery_allowed: bool = False


@dataclass(frozen=True)
class Transition:
    """A state change returned to the ROS adapter."""

    previous: State
    current: State
    reason: str


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


@dataclass(frozen=True)
class CandidateFillEvidence:
    """Versioned raw-cost evidence carried by one robust fill request."""

    estimate: float
    mad: float
    uncertainty: float
    lower: float
    rotation_count: int

    @property
    def valid(self) -> bool:
        return bool(
            math.isfinite(float(self.estimate))
            and math.isfinite(float(self.mad))
            and float(self.mad) >= 0.0
            and math.isfinite(float(self.uncertainty))
            and float(self.uncertainty) >= 0.0
            and math.isfinite(float(self.lower))
            and float(self.lower) < 0.0
            and math.isclose(
                float(self.lower),
                float(self.estimate) - float(self.uncertainty),
                rel_tol=1e-9,
                abs_tol=1e-9,
            )
            and not isinstance(self.rotation_count, bool)
            and isinstance(self.rotation_count, int)
            and self.rotation_count >= 2
        )


def candidate_fill_evidence_from_summary(summary):
    """Freeze one valid repeated raw-cost interval for fill design."""

    if not isinstance(summary, CandidateCostSummary) or not summary.valid:
        raise ValueError("candidate fill evidence requires a valid cost summary")
    evidence = CandidateFillEvidence(
        estimate=float(summary.estimate),
        mad=float(summary.mad),
        uncertainty=float(summary.uncertainty),
        lower=float(summary.lower),
        rotation_count=int(summary.rotation_count),
    )
    if not evidence.valid:
        raise ValueError(
            "candidate fill evidence requires repeated finite negative "
            "raw-cost support"
        )
    return evidence


def encode_candidate_informed_fill_payload(base_values, summary):
    """Append the v1 candidate evidence suffix to one canonical snapshot."""

    values = tuple(float(value) for value in base_values)
    if (
        len(values) != CANDIDATE_INFORMED_FILL_BASE_VALUE_COUNT
        or any(not math.isfinite(value) for value in values)
    ):
        raise ValueError(
            "candidate-informed fill requires eight finite convergence values"
        )
    evidence = candidate_fill_evidence_from_summary(summary)
    return values + (
        evidence.estimate,
        evidence.mad,
        evidence.uncertainty,
        evidence.lower,
        float(evidence.rotation_count),
    )


def decode_candidate_informed_fill_payload(header, values):
    """Decode a v1 suffix; unrelated historical create headers return None."""

    if str(header).strip() != CANDIDATE_INFORMED_FILL_HEADER:
        return None
    payload = tuple(float(value) for value in values)
    expected = (
        CANDIDATE_INFORMED_FILL_BASE_VALUE_COUNT
        + CANDIDATE_INFORMED_FILL_EVIDENCE_VALUE_COUNT
    )
    if len(payload) != expected or any(
        not math.isfinite(value) for value in payload
    ):
        raise ValueError(
            "candidate-informed fill payload must contain thirteen "
            "finite values"
        )
    rotation_value = payload[-1]
    rotation_count = int(rotation_value)
    if not math.isclose(
        rotation_value,
        float(rotation_count),
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise ValueError(
            "candidate-informed fill rotation count must be integral"
        )
    evidence = CandidateFillEvidence(
        estimate=payload[-5],
        mad=payload[-4],
        uncertainty=payload[-3],
        lower=payload[-2],
        rotation_count=rotation_count,
    )
    if not evidence.valid:
        raise ValueError(
            "candidate-informed fill evidence is invalid or inconsistent"
        )
    return evidence


class RotationScoreWindow:
    """Aggregate rotating-sensor scores over complete revolutions."""

    def __init__(self, rotation_period_sec: float, required_rotations: int = 2):
        rotation_period_sec = float(rotation_period_sec)
        required_rotations = int(required_rotations)
        if not math.isfinite(rotation_period_sec) or rotation_period_sec <= 0.0:
            raise ValueError("rotation_period_sec must be finite and positive")
        if required_rotations <= 0:
            raise ValueError("required_rotations must be positive")
        self.rotation_period_sec = rotation_period_sec
        self.required_rotations = required_rotations
        self.completed_maxima = deque(maxlen=required_rotations)
        self.window_started_sec = None
        self.current_maximum = None
        self.last_stamp_sec = None

    def reset(self):
        """Discard incomplete and completed rotation evidence."""

        self.completed_maxima.clear()
        self.window_started_sec = None
        self.current_maximum = None
        self.last_stamp_sec = None

    def update(self, stamp_sec: float, score: float):
        """Add one valid score and close elapsed complete rotation windows."""

        stamp_sec = float(stamp_sec)
        score = float(score)
        if not math.isfinite(stamp_sec) or not math.isfinite(score):
            raise ValueError("rotation score samples must be finite")
        if self.last_stamp_sec is not None and stamp_sec < self.last_stamp_sec:
            self.reset()
        self.last_stamp_sec = stamp_sec

        if self.window_started_sec is None:
            self.window_started_sec = stamp_sec
            self.current_maximum = score
            return

        elapsed = stamp_sec - self.window_started_sec
        if elapsed < self.rotation_period_sec:
            self.current_maximum = max(self.current_maximum, score)
            return

        elapsed_windows = int(elapsed // self.rotation_period_sec)
        if elapsed_windows > 1:
            self.completed_maxima.clear()
            self.window_started_sec = stamp_sec
            self.current_maximum = score
            return

        self.completed_maxima.append(float(self.current_maximum))
        self.window_started_sec += self.rotation_period_sec
        self.current_maximum = score

    @property
    def ready(self) -> bool:
        """Return whether the configured number of rotations is complete."""

        return len(self.completed_maxima) == self.required_rotations

    @property
    def evidence_duration_sec(self) -> float:
        """Return the minimum duration of complete rotation evidence."""
        return self.rotation_period_sec * self.required_rotations

    @property
    def score(self) -> Optional[float]:
        """Return the conservative peak score across completed rotations."""

        if not self.ready:
            return None
        return float(min(self.completed_maxima))


class RotationCostWindow:
    """Aggregate raw minimization cost over complete sensor revolutions."""

    def __init__(
        self,
        rotation_period_sec: float,
        required_rotations: int = 2,
        mad_scale: float = 3.0,
        retained_rotations: Optional[int] = None,
    ):
        rotation_period_sec = float(rotation_period_sec)
        if (
            isinstance(required_rotations, bool)
            or not isinstance(required_rotations, int)
            or required_rotations <= 0
        ):
            raise ValueError("required_rotations must be a positive integer")
        mad_scale = float(mad_scale)
        if not math.isfinite(rotation_period_sec) or rotation_period_sec <= 0.0:
            raise ValueError("rotation_period_sec must be finite and positive")
        if not math.isfinite(mad_scale) or mad_scale < 0.0:
            raise ValueError("mad_scale must be finite and nonnegative")
        if retained_rotations is None:
            retained_rotations = required_rotations
        if (
            isinstance(retained_rotations, bool)
            or not isinstance(retained_rotations, int)
            or retained_rotations < required_rotations
        ):
            raise ValueError(
                "retained_rotations must be an integer no smaller than "
                "required_rotations"
            )
        self.rotation_period_sec = rotation_period_sec
        self.required_rotations = required_rotations
        self.mad_scale = mad_scale
        self.retained_rotations = retained_rotations
        self.completed_minima = deque(maxlen=retained_rotations)
        self.window_started_sec = None
        self.current_minimum = None
        self.last_stamp_sec = None

    def reset(self):
        """Discard incomplete and completed rotation evidence."""

        self.completed_minima.clear()
        self.window_started_sec = None
        self.current_minimum = None
        self.last_stamp_sec = None

    def update(self, stamp_sec: float, raw_cost: float):
        """Add one valid raw-cost sample and close complete rotation windows."""

        stamp_sec = float(stamp_sec)
        raw_cost = float(raw_cost)
        if not math.isfinite(stamp_sec) or not math.isfinite(raw_cost):
            raise ValueError("rotation cost samples must be finite")
        if self.last_stamp_sec is not None and stamp_sec < self.last_stamp_sec:
            self.reset()
        self.last_stamp_sec = stamp_sec

        if self.window_started_sec is None:
            self.window_started_sec = stamp_sec
            self.current_minimum = raw_cost
            return

        elapsed = stamp_sec - self.window_started_sec
        if elapsed < self.rotation_period_sec:
            self.current_minimum = min(self.current_minimum, raw_cost)
            return

        elapsed_windows = int(elapsed // self.rotation_period_sec)
        if elapsed_windows > 1:
            self.completed_minima.clear()
            self.window_started_sec = stamp_sec
            self.current_minimum = raw_cost
            return

        self.completed_minima.append(float(self.current_minimum))
        self.window_started_sec += self.rotation_period_sec
        self.current_minimum = raw_cost

    @property
    def ready(self) -> bool:
        return len(self.completed_minima) >= self.required_rotations

    @property
    def evidence_duration_sec(self) -> float:
        return self.rotation_period_sec * self.required_rotations

    @property
    def summary(self) -> Optional[CandidateCostSummary]:
        if not self.ready:
            return None
        return self.summarize_minima(
            tuple(self.completed_minima),
            required_rotations=self.required_rotations,
            mad_scale=self.mad_scale,
            verification_rotation_count=len(self.completed_minima),
        )

    @staticmethod
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


class SupervisorStateMachine:
    """Deterministic state machine with latched terminal states."""

    def __init__(self, now_sec: float = 0.0, config=None):
        self.config = config or StateMachineConfig()
        self._require_time(now_sec)
        self.state = State.SEARCH
        self.previous_state = None
        self.transition_reason = "initialized"
        self.state_entered_sec = float(now_sec)
        self.last_now_sec = float(now_sec)
        self.convergence_started_sec = None
        self.goal_dwell_started_sec = None
        self.undesired_dwell_started_sec = None
        self.escape_started_sec = None
        self.fill_request_timestamp = None
        self.redesign_attempted = False
        self.design_returns_to_assist = False
        self.active_fill_count = 0
        self.active_escape_fill_id = None
        self.post_recovery_fill_id = None
        self.post_recovery_guidance_active = False
        self.post_recovery_guidance_started_sec = None
        self.post_recovery_retry_count = 0
        self.recovery_retry_count = 0
        self.filled_candidate_costs = []
        self.pending_candidate_cost = None
        self.terminal_candidate_cost = None
        self.last_rejected_candidate_cost = None

    @staticmethod
    def _require_time(now_sec):
        if not math.isfinite(float(now_sec)):
            raise ValueError("state-machine time must be finite")

    @property
    def weights(self) -> Tuple[float, float, float]:
        """Return explicit raw, Gaussian, and affine weights."""

        if self.state == State.SEARCH and self.post_recovery_guidance_active:
            return (1.0, 1.0, 1.0)
        if (
            self.state in (State.ESCAPE_REPULSE, State.ESCAPE_ASSIST)
            and self.config.open_field_escape_approach_continuity_enabled
        ):
            return (0.0, 1.0, 1.0)
        if (
            self.state == State.ESCAPE_ASSIST
            and self.config.open_field_escape_assist_enabled
        ):
            return (0.0, 1.0, 0.0)
        return STATE_WEIGHTS[self.state]

    def elapsed(self, now_sec: float) -> float:
        """Return elapsed state time without mutating the machine."""

        self._require_time(now_sec)
        return max(0.0, float(now_sec) - self.state_entered_sec)

    def register_fill_request(self, source_timestamp: float):
        """Register the one in-flight request accepted by the fill interface."""

        if self.state != State.DESIGN_OR_MERGE_FILL:
            raise RuntimeError("fill requests are valid only in the design state")
        self._require_time(source_timestamp)
        self.fill_request_timestamp = float(source_timestamp)

    def force_failsafe(self, now_sec: float, reason: str) -> Optional[Transition]:
        """Latch FAILSAFE after an adapter exception or validation failure."""

        self._require_time(now_sec)
        if self.state == State.FAILSAFE:
            return None
        return self._transition(State.FAILSAFE, float(now_sec), str(reason))

    def step(self, now_sec: float, inputs=None) -> Optional[Transition]:
        """Advance the machine by one input sample."""

        inputs = inputs or TransitionInputs()
        self._require_time(now_sec)
        now_sec = float(now_sec)
        if now_sec < self.last_now_sec:
            return self.force_failsafe(now_sec, "ROS clock moved backward")
        self.last_now_sec = now_sec

        if self.state == State.FAILSAFE:
            return None
        if inputs.explicit_stop:
            return self._transition(State.FAILSAFE, now_sec, "explicit stop requested")
        if inputs.controller_fault:
            return self._transition(State.FAILSAFE, now_sec, "controller reported failsafe")
        if not inputs.pose_valid:
            return self._transition(State.FAILSAFE, now_sec, "pose invalid or stale")
        if not inputs.sensor_valid:
            return self._transition(State.FAILSAFE, now_sec, "source sample invalid or stale")

        self._expire_post_recovery_guidance(now_sec)
        if (
            self.config.recoverable_navigation_enabled
            and inputs.recenter_recovery_requested
            and self.state != State.RECENTER
        ):
            if self.recovery_retry_count >= self.config.recovery_retry_limit:
                return self._transition(
                    State.FAILSAFE,
                    now_sec,
                    'recoverable navigation retry limit reached',
                )
            self.recovery_retry_count += 1
            return self._transition(
                State.RECENTER,
                now_sec,
                'recoverable navigation requested',
            )
        if self.state == State.GOAL_HOLD:
            return None
        if self.state == State.SEARCH:
            return self._step_search(now_sec, inputs)
        if self.state == State.VERIFY_EXTREMUM:
            return self._step_verify(now_sec, inputs)
        if self.state == State.DESIGN_OR_MERGE_FILL:
            return self._step_design(now_sec, inputs)
        if self.state == State.ESCAPE_REPULSE:
            return self._step_repulse(now_sec, inputs)
        if self.state == State.ESCAPE_ASSIST:
            return self._step_assist(now_sec, inputs)
        if self.state == State.RECENTER:
            return self._step_recenter(now_sec, inputs)
        return self._transition(State.FAILSAFE, now_sec, "unknown supervisor state")

    def _step_search(self, now_sec, inputs):
        if inputs.convergence_confirmed:
            return self._transition(
                State.VERIFY_EXTREMUM,
                now_sec,
                "detector convergence confirmation received",
            )
        if inputs.convergence:
            if self.convergence_started_sec is None:
                self.convergence_started_sec = now_sec
            if now_sec - self.convergence_started_sec >= self.config.convergence_hold_sec:
                return self._transition(
                    State.VERIFY_EXTREMUM,
                    now_sec,
                    "continuous convergence dwell satisfied",
                )
        else:
            self.convergence_started_sec = None
        return None

    def _step_verify(self, now_sec, inputs):
        if self.config.extremum_classification_mode == COUNTED_CANDIDATES:
            return self._step_counted_verify(now_sec, inputs)

        score = inputs.source_score
        if not inputs.source_score_observed:
            if self.elapsed(now_sec) >= self.config.verification_max_sec:
                if self.config.recoverable_navigation_enabled:
                    return self._recover_to_search(
                        now_sec,
                        'verification evidence window exhausted; resume search',
                    )
                return self._transition(State.FAILSAFE, now_sec, "verification timeout")
            return None
        if not inputs.source_score_valid:
            return self._transition(State.FAILSAFE, now_sec, "source score invalid")
        if not inputs.source_score_ready:
            if self.elapsed(now_sec) >= self.config.verification_max_sec:
                if self.config.recoverable_navigation_enabled:
                    return self._recover_to_search(
                        now_sec,
                        'verification evidence window exhausted; resume search',
                    )
                return self._transition(State.FAILSAFE, now_sec, "verification timeout")
            return None
        if score is None or not math.isfinite(float(score)):
            return self._transition(State.FAILSAFE, now_sec, "source score invalid")

        if float(score) >= self.config.goal_score_threshold:
            self.undesired_dwell_started_sec = None
            if self.goal_dwell_started_sec is None:
                self.goal_dwell_started_sec = now_sec
            if now_sec - self.goal_dwell_started_sec >= self.config.goal_hold_sec:
                return self._transition(
                    State.GOAL_HOLD,
                    now_sec,
                    "goal source-score dwell satisfied",
                )
        else:
            self.goal_dwell_started_sec = None
            if self.undesired_dwell_started_sec is None:
                self.undesired_dwell_started_sec = now_sec
            if (
                now_sec - self.undesired_dwell_started_sec
                >= self.config.undesired_score_hold_sec
            ):
                if self._fill_budget_exhausted():
                    if (
                        self.post_recovery_retry_count
                        >= self.config.post_recovery_retry_limit
                    ):
                        return self._transition(
                            State.FAILSAFE,
                            now_sec,
                            "post-recovery retry limit reached",
                        )
                    if not self._activate_post_recovery_guidance(now_sec):
                        return self._transition(
                            State.FAILSAFE,
                            now_sec,
                            "post-recovery guidance has no accepted fill",
                        )
                    self.post_recovery_retry_count += 1
                    return self._transition(
                        State.SEARCH,
                        now_sec,
                        "known local-fill budget exhausted; resume guided search",
                    )
                return self._transition(
                    State.DESIGN_OR_MERGE_FILL,
                    now_sec,
                    "undesired-minimum score dwell satisfied",
                )

        if self.elapsed(now_sec) >= self.config.verification_max_sec:
            if self.config.recoverable_navigation_enabled:
                return self._recover_to_search(
                    now_sec,
                    'verification classification window exhausted; resume search',
                )
            return self._transition(State.FAILSAFE, now_sec, "verification timeout")
        return None

    def _step_counted_verify(self, now_sec, inputs):
        if inputs.candidate_associated_with_fill:
            return self._transition(
                State.SEARCH,
                now_sec,
                "confirmed candidate associated with active fill; resume search",
            )

        if not inputs.candidate_cost_observed:
            return self._wait_for_candidate_cost_or_timeout(now_sec)
        if not inputs.candidate_cost_valid:
            return self._transition(
                State.FAILSAFE, now_sec, "candidate raw-cost evidence invalid"
            )
        if not inputs.candidate_cost_ready:
            return self._wait_for_candidate_cost_or_timeout(now_sec)

        summary = inputs.candidate_cost_summary
        if (
            summary is None
            or not isinstance(summary, CandidateCostSummary)
            or not summary.valid
            or summary.rotation_count
            < self.config.candidate_cost_required_rotations
        ):
            return self._transition(
                State.FAILSAFE, now_sec, "candidate raw-cost summary invalid"
            )

        active_count = self.active_fill_count
        if inputs.active_fill_count is not None:
            if (
                isinstance(inputs.active_fill_count, bool)
                or not isinstance(inputs.active_fill_count, int)
                or inputs.active_fill_count < 0
            ):
                return self._transition(
                    State.FAILSAFE, now_sec, "invalid active fill-cluster count"
                )
            active_count = int(inputs.active_fill_count)
            self.active_fill_count = active_count

        required_fills = self.config.known_source_count - 1
        if active_count > required_fills:
            return self._transition(
                State.FAILSAFE,
                now_sec,
                "active fill count exceeds counted-source cardinality",
            )
        if active_count != len(self.filled_candidate_costs):
            return self._transition(
                State.FAILSAFE,
                now_sec,
                "active fills and retained candidate costs disagree",
            )

        if active_count < required_fills:
            self.pending_candidate_cost = summary
            return self._transition(
                State.DESIGN_OR_MERGE_FILL,
                now_sec,
                "counted candidate requires local fill before terminal ranking",
            )

        self.pending_candidate_cost = None
        strictly_lower = all(
            summary.upper < retained.lower
            for retained in self.filled_candidate_costs
        )
        if strictly_lower:
            self.terminal_candidate_cost = summary
            self.last_rejected_candidate_cost = None
            return self._transition(
                State.GOAL_HOLD,
                now_sec,
                "counted candidate raw-cost interval strictly lower than "
                "all filled candidates",
            )

        self.last_rejected_candidate_cost = summary
        return self._transition(
            State.SEARCH,
            now_sec,
            "counted candidate not strictly stronger; resume search",
        )

    def _wait_for_candidate_cost_or_timeout(self, now_sec):
        if self.elapsed(now_sec) >= self.config.verification_max_sec:
            return self._transition(
                State.FAILSAFE, now_sec, "candidate raw-cost verification timeout"
            )
        return None

    def _step_design(self, now_sec, inputs):
        if inputs.fill_result is not None:
            if not self._matching_fill_result(inputs.fill_source_timestamp):
                return None
            if inputs.fill_result == "success":
                previous_active_fill_count = self.active_fill_count
                if inputs.active_fill_count is None:
                    self.active_fill_count += 1
                elif int(inputs.active_fill_count) < 0:
                    return self._transition(
                        State.FAILSAFE, now_sec, "invalid active fill-cluster count"
                    )
                else:
                    self.active_fill_count = int(inputs.active_fill_count)
                if self.config.extremum_classification_mode == COUNTED_CANDIDATES:
                    required_fills = self.config.known_source_count - 1
                    if self.active_fill_count > required_fills:
                        return self._transition(
                            State.FAILSAFE,
                            now_sec,
                            "accepted fill exceeds counted-source cardinality",
                        )
                    if not self.design_returns_to_assist:
                        if self.pending_candidate_cost is None:
                            return self._transition(
                                State.FAILSAFE,
                                now_sec,
                                "accepted fill has no pending candidate cost",
                            )
                        expected_count = len(self.filled_candidate_costs) + 1
                        if (
                            self.active_fill_count != expected_count
                            or self.active_fill_count
                            != previous_active_fill_count + 1
                        ):
                            return self._transition(
                                State.FAILSAFE,
                                now_sec,
                                "counted candidate did not create one distinct fill",
                            )
                        self.filled_candidate_costs.append(
                            self.pending_candidate_cost
                        )
                        self.pending_candidate_cost = None
                if inputs.fill_id is not None and int(inputs.fill_id) > 0:
                    self.active_escape_fill_id = int(inputs.fill_id)
                    self.post_recovery_fill_id = int(inputs.fill_id)
                self.post_recovery_guidance_active = False
                self.post_recovery_guidance_started_sec = None
                self.post_recovery_retry_count = 0
                destination = (
                    State.ESCAPE_ASSIST
                    if self.design_returns_to_assist
                    else State.ESCAPE_REPULSE
                )
                return self._transition(destination, now_sec, "matching fill design accepted")
            if inputs.fill_result == "rejected":
                return self._transition(State.FAILSAFE, now_sec, "fill design rejected")
            if (
                inputs.fill_result == 'retryable_rejected'
                and self.config.recoverable_navigation_enabled
            ):
                return self._recover_to_search(
                    now_sec, 'insufficient fill samples; reacquire search'
                )
            return self._transition(State.FAILSAFE, now_sec, "invalid fill result")

        if self.elapsed(now_sec) >= self.config.fill_design_timeout_sec:
            return self._transition(State.FAILSAFE, now_sec, "fill design timeout")
        return None

    def _step_repulse(self, now_sec, inputs):
        if self._escape_timed_out(now_sec):
            if (
                self.config.recoverable_navigation_enabled
                and self.active_escape_fill_id is not None
            ):
                return self._recover_to_recenter(
                    now_sec, 'escape duration exhausted; recover by recenter'
                )
            return self._transition(State.FAILSAFE, now_sec, "escape timeout")
        if inputs.stable_exit:
            destination = State.RECENTER if self.config.recenter_after_escape else State.SEARCH
            return self._transition(destination, now_sec, "stable escape exit")
        if inputs.stalled:
            if self.config.open_field_escape_assist_enabled:
                return self._transition(
                    State.ESCAPE_ASSIST,
                    now_sec,
                    "escape stalled; continue bounded outward assist",
                )
            if self.redesign_attempted:
                if self.config.recoverable_navigation_enabled:
                    return self._recover_to_recenter(
                        now_sec, 'redesigned escape stalled; recover by recenter'
                    )
                return self._transition(State.FAILSAFE, now_sec, "escape stalled after redesign")
            self.redesign_attempted = True
            self.design_returns_to_assist = True
            return self._transition(
                State.DESIGN_OR_MERGE_FILL,
                now_sec,
                "escape stalled; request single fill redesign",
            )
        return None

    def _step_assist(self, now_sec, inputs):
        if self._escape_timed_out(now_sec):
            if self.config.recoverable_navigation_enabled:
                return self._recover_to_recenter(
                    now_sec, 'assisted escape duration exhausted; recover by recenter'
                )
            return self._transition(State.FAILSAFE, now_sec, "assisted escape timeout")
        if inputs.stable_exit:
            destination = State.RECENTER if self.config.recenter_after_escape else State.SEARCH
            return self._transition(destination, now_sec, "stable assisted escape exit")
        return None

    def _step_recenter(self, now_sec, inputs):
        if inputs.recenter_complete:
            self.recovery_retry_count = 0
            if self._fill_budget_exhausted():
                if not self._activate_post_recovery_guidance(now_sec):
                    return self._transition(
                        State.FAILSAFE,
                        now_sec,
                        "post-recovery guidance has no accepted fill",
                    )
            return self._transition(State.SEARCH, now_sec, "recenter complete")
        if self.elapsed(now_sec) >= self.config.recenter_max_sec:
            if (
                self.config.recoverable_navigation_enabled
                and inputs.recenter_recovery_allowed
                and self.recovery_retry_count < self.config.recovery_retry_limit
            ):
                self.recovery_retry_count += 1
                previous = self.state
                self.state_entered_sec = float(now_sec)
                self.transition_reason = 'bounded recenter recovery extension'
                return Transition(
                    previous,
                    State.RECENTER,
                    self.transition_reason,
                )
            return self._transition(State.FAILSAFE, now_sec, "recenter timeout")
        return None

    def _recover_to_search(self, now_sec, reason):
        if self.recovery_retry_count >= self.config.recovery_retry_limit:
            return self._transition(
                State.FAILSAFE,
                now_sec,
                'recoverable navigation retry limit reached',
            )
        self.recovery_retry_count += 1
        return self._transition(State.SEARCH, now_sec, reason)

    def _recover_to_recenter(self, now_sec, reason):
        if self.recovery_retry_count >= self.config.recovery_retry_limit:
            return self._transition(
                State.FAILSAFE,
                now_sec,
                'recoverable navigation retry limit reached',
            )
        self.recovery_retry_count += 1
        return self._transition(State.RECENTER, now_sec, reason)

    def deactivate_post_recovery_guidance(self):
        """Clear affine authorization while retaining accepted Gaussian fills."""
        self.post_recovery_guidance_active = False
        self.post_recovery_guidance_started_sec = None
        self.active_escape_fill_id = None

    def _matching_fill_result(self, source_timestamp):
        if self.fill_request_timestamp is None or source_timestamp is None:
            return False
        if not math.isfinite(float(source_timestamp)):
            return False
        return math.isclose(
            float(source_timestamp),
            self.fill_request_timestamp,
            rel_tol=0.0,
            abs_tol=1e-9,
        )

    def _escape_timed_out(self, now_sec):
        return (
            self.escape_started_sec is not None
            and now_sec - self.escape_started_sec >= self.config.escape_max_sec
        )

    def _fill_budget_exhausted(self):
        return bool(
            self.config.post_recovery_guidance_enabled
            and self.config.max_fill_clusters > 0
            and self.active_fill_count >= self.config.max_fill_clusters
        )

    def _activate_post_recovery_guidance(self, now_sec):
        fill_id = self.post_recovery_fill_id
        if fill_id is None or int(fill_id) <= 0:
            return False
        self.post_recovery_guidance_active = True
        self.post_recovery_guidance_started_sec = float(now_sec)
        self.active_escape_fill_id = int(fill_id)
        return True

    def _expire_post_recovery_guidance(self, now_sec):
        if (
            not self.post_recovery_guidance_active
            or self.post_recovery_guidance_started_sec is None
        ):
            return
        if (
            float(now_sec) - self.post_recovery_guidance_started_sec
            >= self.config.post_recovery_guidance_max_sec
        ):
            self.post_recovery_guidance_active = False
            self.post_recovery_guidance_started_sec = None
            if self.state == State.SEARCH:
                self.active_escape_fill_id = None

    def _transition(self, destination, now_sec, reason):
        previous = self.state
        self.previous_state = previous
        self.state = destination
        self.transition_reason = reason
        self.state_entered_sec = now_sec
        self.convergence_started_sec = None
        self.goal_dwell_started_sec = None
        self.undesired_dwell_started_sec = None
        self.fill_request_timestamp = None

        if destination == State.ESCAPE_REPULSE and self.escape_started_sec is None:
            self.escape_started_sec = now_sec
        if destination == State.SEARCH:
            self.escape_started_sec = None
            self.redesign_attempted = False
            self.design_returns_to_assist = False
            if not self.post_recovery_guidance_active:
                self.active_escape_fill_id = None
        if destination in (State.FAILSAFE, State.GOAL_HOLD):
            self.design_returns_to_assist = False
            self.post_recovery_guidance_active = False
            self.post_recovery_guidance_started_sec = None
            self.active_escape_fill_id = None

        return Transition(previous, destination, reason)
