"""ROS-independent GESC/Gaussian supervisor state machine."""

from collections import deque
from dataclasses import dataclass
from enum import IntEnum
import math
from typing import Optional, Tuple


LEGACY_PROFILE = "legacy"
ROBUST_PROFILE = "robust_gaussian_v1"
VALID_PROFILES = (LEGACY_PROFILE, ROBUST_PROFILE)


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
    recenter_after_escape: bool = True
    recenter_max_sec: float = 30.0
    max_fill_clusters: int = 0
    post_recovery_guidance_enabled: bool = False
    post_recovery_guidance_max_sec: float = 0.0
    post_recovery_retry_limit: int = 0

    def __post_init__(self):
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
            isinstance(self.max_fill_clusters, bool)
            or not isinstance(self.max_fill_clusters, int)
            or self.max_fill_clusters < 0
        ):
            raise ValueError("max_fill_clusters must be a nonnegative integer")
        if (
            isinstance(self.post_recovery_retry_limit, bool)
            or not isinstance(self.post_recovery_retry_limit, int)
            or self.post_recovery_retry_limit < 0
        ):
            raise ValueError(
                "post_recovery_retry_limit must be a nonnegative integer"
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


@dataclass(frozen=True)
class Transition:
    """A state change returned to the ROS adapter."""

    previous: State
    current: State
    reason: str


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

    @staticmethod
    def _require_time(now_sec):
        if not math.isfinite(float(now_sec)):
            raise ValueError("state-machine time must be finite")

    @property
    def weights(self) -> Tuple[float, float, float]:
        """Return explicit raw, Gaussian, and affine weights."""

        if self.state == State.SEARCH and self.post_recovery_guidance_active:
            return (1.0, 1.0, 1.0)
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
        score = inputs.source_score
        if not inputs.source_score_observed:
            if self.elapsed(now_sec) >= self.config.verification_max_sec:
                return self._transition(State.FAILSAFE, now_sec, "verification timeout")
            return None
        if not inputs.source_score_valid:
            return self._transition(State.FAILSAFE, now_sec, "source score invalid")
        if not inputs.source_score_ready:
            if self.elapsed(now_sec) >= self.config.verification_max_sec:
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
            return self._transition(State.FAILSAFE, now_sec, "verification timeout")
        return None

    def _step_design(self, now_sec, inputs):
        if inputs.fill_result is not None:
            if not self._matching_fill_result(inputs.fill_source_timestamp):
                return None
            if inputs.fill_result == "success":
                if inputs.active_fill_count is None:
                    self.active_fill_count += 1
                elif int(inputs.active_fill_count) < 0:
                    return self._transition(
                        State.FAILSAFE, now_sec, "invalid active fill-cluster count"
                    )
                else:
                    self.active_fill_count = int(inputs.active_fill_count)
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
            return self._transition(State.FAILSAFE, now_sec, "invalid fill result")

        if self.elapsed(now_sec) >= self.config.fill_design_timeout_sec:
            return self._transition(State.FAILSAFE, now_sec, "fill design timeout")
        return None

    def _step_repulse(self, now_sec, inputs):
        if self._escape_timed_out(now_sec):
            return self._transition(State.FAILSAFE, now_sec, "escape timeout")
        if inputs.stable_exit:
            destination = State.RECENTER if self.config.recenter_after_escape else State.SEARCH
            return self._transition(destination, now_sec, "stable escape exit")
        if inputs.stalled:
            if self.redesign_attempted:
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
            return self._transition(State.FAILSAFE, now_sec, "assisted escape timeout")
        if inputs.stable_exit:
            destination = State.RECENTER if self.config.recenter_after_escape else State.SEARCH
            return self._transition(destination, now_sec, "stable assisted escape exit")
        return None

    def _step_recenter(self, now_sec, inputs):
        if inputs.recenter_complete:
            if self._fill_budget_exhausted():
                if not self._activate_post_recovery_guidance(now_sec):
                    return self._transition(
                        State.FAILSAFE,
                        now_sec,
                        "post-recovery guidance has no accepted fill",
                    )
            return self._transition(State.SEARCH, now_sec, "recenter complete")
        if self.elapsed(now_sec) >= self.config.recenter_max_sec:
            return self._transition(State.FAILSAFE, now_sec, "recenter timeout")
        return None

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
