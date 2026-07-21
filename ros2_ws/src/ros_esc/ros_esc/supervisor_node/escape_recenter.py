"""Pure geometry and control helpers for measured escape and recentering."""

from dataclasses import dataclass
from collections import deque
import math
from typing import Optional, Sequence

import numpy as np


_EPSILON = 1e-12


def _finite_vector(values, name):
    vector = np.asarray(values, dtype=np.float64).reshape(-1)
    if vector.size != 2 or not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must contain two finite values")
    return vector


def _unit(values, name):
    vector = _finite_vector(values, name)
    norm = float(np.linalg.norm(vector))
    if norm <= _EPSILON:
        raise ValueError(f"{name} must be nonzero")
    return vector / norm


@dataclass(frozen=True)
class Pose2D:
    """One finite planar pose sample on a monotonic clock."""

    stamp_sec: float
    x: float
    y: float
    yaw: float

    def __post_init__(self):
        if not np.all(np.isfinite([self.stamp_sec, self.x, self.y, self.yaw])):
            raise ValueError("pose sample must be finite")

    @property
    def position(self):
        return np.array([self.x, self.y], dtype=np.float64)


@dataclass(frozen=True)
class OperatingBounds:
    """Configured virtual room and its wall-margin-inset operating rectangle."""

    x_min: float = -2.0
    x_max: float = 2.0
    y_min: float = -2.0
    y_max: float = 2.0
    center_x: float = 0.0
    center_y: float = 0.0
    wall_margin: float = 0.35

    def __post_init__(self):
        values = (
            self.x_min,
            self.x_max,
            self.y_min,
            self.y_max,
            self.center_x,
            self.center_y,
            self.wall_margin,
        )
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("room bounds, center, and margin must be finite")
        if self.x_min >= self.x_max or self.y_min >= self.y_max:
            raise ValueError("room minimum bounds must be below maximum bounds")
        if self.wall_margin < 0.0:
            raise ValueError("wall margin must be nonnegative")
        if self.inset_x_min >= self.inset_x_max or self.inset_y_min >= self.inset_y_max:
            raise ValueError("wall-margin-inset room must be nonempty")
        if not self.contains(self.center):
            raise ValueError("room center must lie inside the wall-margin inset")

    @property
    def inset_x_min(self):
        return self.x_min + self.wall_margin

    @property
    def inset_x_max(self):
        return self.x_max - self.wall_margin

    @property
    def inset_y_min(self):
        return self.y_min + self.wall_margin

    @property
    def inset_y_max(self):
        return self.y_max - self.wall_margin

    @property
    def center(self):
        return np.array([self.center_x, self.center_y], dtype=np.float64)

    def contains(self, point):
        point = _finite_vector(point, "point")
        return bool(
            self.inset_x_min <= point[0] <= self.inset_x_max
            and self.inset_y_min <= point[1] <= self.inset_y_max
        )

    def clearance(self, point):
        point = _finite_vector(point, "point")
        return float(
            min(
                point[0] - self.inset_x_min,
                self.inset_x_max - point[0],
                point[1] - self.inset_y_min,
                self.inset_y_max - point[1],
            )
        )


@dataclass(frozen=True)
class FillAvoidance:
    """Conservative circular avoidance geometry for one active fill."""

    fill_id: int
    cluster_id: int
    center_x: float
    center_y: float
    radius: float

    def __post_init__(self):
        if int(self.fill_id) <= 0 or int(self.cluster_id) <= 0:
            raise ValueError("fill and cluster IDs must be positive")
        if not np.all(np.isfinite([self.center_x, self.center_y, self.radius])):
            raise ValueError("fill avoidance geometry must be finite")
        if self.radius <= 0.0:
            raise ValueError("fill avoidance radius must be positive")

    @property
    def center(self):
        return np.array([self.center_x, self.center_y], dtype=np.float64)


@dataclass(frozen=True)
class EscapeGeometry:
    """Immutable reference geometry for one complete escape attempt."""

    initial_fill_id: int
    center_x: float
    center_y: float
    exit_radius: float
    started_sec: float
    approach_x: float
    approach_y: float

    def __post_init__(self):
        values = (
            self.center_x,
            self.center_y,
            self.exit_radius,
            self.started_sec,
            self.approach_x,
            self.approach_y,
        )
        if int(self.initial_fill_id) <= 0:
            raise ValueError("initial escape fill ID must be positive")
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("escape geometry must be finite")
        if self.exit_radius <= 0.0:
            raise ValueError("escape exit radius must be positive")

    @property
    def center(self):
        return np.array([self.center_x, self.center_y], dtype=np.float64)

    @property
    def approach(self):
        return np.array([self.approach_x, self.approach_y], dtype=np.float64)


@dataclass(frozen=True)
class EscapeProgressConfig:
    """Rolling radial-progress and stable-exit settings."""

    stall_window_sec: float = 3.0
    minimum_radial_progress_m: float = 0.05
    escape_exit_hold_sec: float = 1.0

    def __post_init__(self):
        values = (
            self.stall_window_sec,
            self.minimum_radial_progress_m,
            self.escape_exit_hold_sec,
        )
        if not all(math.isfinite(float(value)) for value in values):
            raise ValueError("escape progress settings must be finite")
        if self.stall_window_sec <= 0.0 or self.escape_exit_hold_sec <= 0.0:
            raise ValueError("escape progress windows must be positive")
        if self.minimum_radial_progress_m < 0.0:
            raise ValueError("minimum radial progress must be nonnegative")


@dataclass(frozen=True)
class EscapeProgress:
    """One measured radial-progress result."""

    radial_distance: float
    radial_progress: float
    radial_progress_valid: bool
    exit_hold_elapsed_sec: float
    exit_hold_elapsed_valid: bool
    stable_exit: bool
    stalled: bool
    stalled_valid: bool


class EscapeProgressTracker:
    """Track progress against frozen geometry using exact-window interpolation."""

    def __init__(self, geometry: EscapeGeometry, config=None):
        self.geometry = geometry
        self.config = config or EscapeProgressConfig()
        self._distances = deque()
        self._exit_hold_started_sec = None
        self.latest = None

    def update(self, pose: Pose2D):
        if self._distances and pose.stamp_sec <= self._distances[-1][0]:
            if pose.stamp_sec == self._distances[-1][0]:
                return self.latest
            raise ValueError("escape pose timestamps must increase")
        distance = float(np.linalg.norm(pose.position - self.geometry.center))
        self._distances.append((pose.stamp_sec, distance))
        boundary = pose.stamp_sec - self.config.stall_window_sec
        while len(self._distances) >= 3 and self._distances[1][0] <= boundary:
            self._distances.popleft()

        previous_distance = self._interpolated_distance(boundary)
        progress_valid = previous_distance is not None
        radial_progress = (
            distance - previous_distance if progress_valid else float("nan")
        )
        qualifies_for_exit = bool(
            distance > self.geometry.exit_radius
            and progress_valid
            and radial_progress >= 0.0
        )
        if qualifies_for_exit:
            if self._exit_hold_started_sec is None:
                self._exit_hold_started_sec = pose.stamp_sec
            hold_elapsed = pose.stamp_sec - self._exit_hold_started_sec
            hold_valid = True
        else:
            self._exit_hold_started_sec = None
            hold_elapsed = float("nan")
            hold_valid = False
        stable_exit = bool(
            qualifies_for_exit
            and hold_elapsed >= self.config.escape_exit_hold_sec
        )
        stalled_valid = progress_valid
        stalled = bool(
            progress_valid
            and not qualifies_for_exit
            and radial_progress < self.config.minimum_radial_progress_m
        )
        self.latest = EscapeProgress(
            radial_distance=distance,
            radial_progress=radial_progress,
            radial_progress_valid=progress_valid,
            exit_hold_elapsed_sec=hold_elapsed,
            exit_hold_elapsed_valid=hold_valid,
            stable_exit=stable_exit,
            stalled=stalled,
            stalled_valid=stalled_valid,
        )
        return self.latest

    def _interpolated_distance(self, stamp_sec):
        if not self._distances or self._distances[0][0] > stamp_sec:
            return None
        for index, (right_stamp, right_distance) in enumerate(self._distances):
            if right_stamp == stamp_sec:
                return right_distance
            if right_stamp > stamp_sec:
                left_stamp, left_distance = self._distances[index - 1]
                fraction = (stamp_sec - left_stamp) / (right_stamp - left_stamp)
                return left_distance + fraction * (right_distance - left_distance)
        return self._distances[-1][1]


def recent_approach(history: Sequence[Pose2D], window_sec: float):
    """Return displacement over a complete recent window, or a zero vector."""

    if not math.isfinite(window_sec) or window_sec <= 0.0:
        raise ValueError("approach history window must be finite and positive")
    if len(history) < 2:
        return np.zeros(2, dtype=np.float64)
    ordered = tuple(history)
    if any(
        ordered[index].stamp_sec >= ordered[index + 1].stamp_sec
        for index in range(len(ordered) - 1)
    ):
        raise ValueError("approach history timestamps must increase")
    current = ordered[-1]
    boundary = current.stamp_sec - window_sec
    if ordered[0].stamp_sec > boundary:
        return np.zeros(2, dtype=np.float64)
    previous = None
    for index, sample in enumerate(ordered):
        if sample.stamp_sec == boundary:
            previous = sample.position
            break
        if sample.stamp_sec > boundary:
            left = ordered[index - 1]
            fraction = (boundary - left.stamp_sec) / (
                sample.stamp_sec - left.stamp_sec
            )
            previous = left.position + fraction * (sample.position - left.position)
            break
    if previous is None:
        previous = ordered[-1].position
    return current.position - previous


def preferred_escape_direction(position, geometry, bounds=None):
    """Choose bounded-center, opposite-approach, then outward radial direction."""

    position = _finite_vector(position, "position")
    if bounds is not None:
        preferred = bounds.center - position
    else:
        preferred = -geometry.approach
    if float(np.linalg.norm(preferred)) <= _EPSILON:
        preferred = position - geometry.center
    return _unit(preferred, "preferred escape direction")


@dataclass(frozen=True)
class DirectionConfig:
    """Safe-direction look-ahead and deterministic candidate settings."""

    lookahead_m: float = 0.50
    candidate_step_rad: float = math.pi / 4.0

    def __post_init__(self):
        if not math.isfinite(self.lookahead_m) or self.lookahead_m <= 0.0:
            raise ValueError("direction look-ahead must be finite and positive")
        if (
            not math.isfinite(self.candidate_step_rad)
            or self.candidate_step_rad <= 0.0
            or self.candidate_step_rad >= math.pi
        ):
            raise ValueError("direction candidate step must be in (0, pi)")


@dataclass(frozen=True)
class DirectionSelection:
    """One deterministic safe world-frame unit direction."""

    x: float
    y: float
    clearance_m: float
    rotation_rad: float
    candidate_index: int

    @property
    def direction(self):
        return np.array([self.x, self.y], dtype=np.float64)


def _segment_clearance(start, end, center):
    segment = end - start
    length_squared = float(np.dot(segment, segment))
    if length_squared <= _EPSILON:
        return float(np.linalg.norm(start - center))
    fraction = float(np.dot(center - start, segment) / length_squared)
    fraction = float(np.clip(fraction, 0.0, 1.0))
    closest = start + fraction * segment
    return float(np.linalg.norm(closest - center))


def evaluate_direction(
    position,
    direction,
    preferred,
    fills: Sequence[FillAvoidance],
    config: DirectionConfig,
    bounds: Optional[OperatingBounds] = None,
):
    """Return candidate safety and clipped predicted endpoint clearance."""

    position = _finite_vector(position, "position")
    direction = _unit(direction, "candidate direction")
    preferred = _unit(preferred, "preferred direction")
    if float(np.dot(direction, preferred)) < -_EPSILON:
        return False, float("nan")
    endpoint = position + config.lookahead_m * direction
    clearance = config.lookahead_m
    if bounds is not None:
        if not bounds.contains(endpoint):
            return False, float("nan")
        clearance = min(clearance, bounds.clearance(endpoint))

    for fill in sorted(fills, key=lambda item: (item.cluster_id, item.fill_id)):
        start_distance = float(np.linalg.norm(position - fill.center))
        endpoint_distance = float(np.linalg.norm(endpoint - fill.center))
        if start_distance <= fill.radius + _EPSILON:
            outward_projection = float(np.dot(direction, position - fill.center))
            if outward_projection < -_EPSILON or endpoint_distance < start_distance - _EPSILON:
                return False, float("nan")
        elif _segment_clearance(position, endpoint, fill.center) <= fill.radius + _EPSILON:
            return False, float("nan")
        clearance = min(clearance, endpoint_distance - fill.radius)
    return True, float(min(config.lookahead_m, clearance))


def select_safe_direction(
    position,
    preferred,
    fills: Sequence[FillAvoidance],
    config=None,
    bounds: Optional[OperatingBounds] = None,
):
    """Search the fixed rotated candidates and select the deterministic optimum."""

    config = config or DirectionConfig()
    preferred = _unit(preferred, "preferred direction")
    base_angle = math.atan2(preferred[1], preferred[0])
    step = config.candidate_step_rad
    rotations = (0.0, step, -step, 2 * step, -2 * step, 3 * step, -3 * step, math.pi)
    selections = []
    seen = []
    for index, rotation in enumerate(rotations):
        angle = base_angle + rotation
        direction = np.array([math.cos(angle), math.sin(angle)], dtype=np.float64)
        if any(float(np.linalg.norm(direction - prior)) <= _EPSILON for prior in seen):
            continue
        seen.append(direction)
        safe, clearance = evaluate_direction(
            position, direction, preferred, fills, config, bounds
        )
        if not safe:
            continue
        selections.append(
            DirectionSelection(
                x=float(direction[0]),
                y=float(direction[1]),
                clearance_m=clearance,
                rotation_rad=float(rotation),
                candidate_index=index,
            )
        )
    if not selections:
        return None

    def score(selection):
        alignment = float(np.dot(selection.direction, preferred))
        return (
            round(selection.clearance_m, 12),
            round(alignment, 12),
            -round(abs(selection.rotation_rad), 12),
            -selection.candidate_index,
        )

    return max(selections, key=score)


def wrap_angle(angle):
    """Wrap a finite angle to [-pi, pi)."""

    if not math.isfinite(angle):
        raise ValueError("angle must be finite")
    return (float(angle) + math.pi) % (2.0 * math.pi) - math.pi


@dataclass(frozen=True)
class RecenterControlConfig:
    """Bounded differential-drive center-return controller settings."""

    tolerance_m: float = 0.25
    hold_sec: float = 1.0
    linear_gain: float = 0.50
    angular_gain: float = 1.50
    max_linear_velocity_mps: float = 0.10
    max_angular_velocity_rps: float = 0.40
    rotate_in_place_angle_rad: float = math.pi / 3.0

    def __post_init__(self):
        positive = (
            self.tolerance_m,
            self.hold_sec,
            self.linear_gain,
            self.angular_gain,
            self.max_linear_velocity_mps,
            self.max_angular_velocity_rps,
            self.rotate_in_place_angle_rad,
        )
        if not all(math.isfinite(float(value)) and value > 0.0 for value in positive):
            raise ValueError("recenter controller settings must be finite and positive")
        if self.rotate_in_place_angle_rad > math.pi:
            raise ValueError("rotate-in-place angle must not exceed pi")


class RecenterHoldTracker:
    """Track an uninterrupted center-tolerance dwell."""

    def __init__(self, config=None):
        self.config = config or RecenterControlConfig()
        self.started_sec = None
        self.elapsed_sec = float("nan")

    def update(self, stamp_sec, distance_m):
        if not np.all(np.isfinite([stamp_sec, distance_m])) or distance_m < 0.0:
            raise ValueError("recenter time and distance must be finite")
        if distance_m <= self.config.tolerance_m:
            if self.started_sec is None:
                self.started_sec = float(stamp_sec)
            self.elapsed_sec = max(0.0, float(stamp_sec) - self.started_sec)
            return self.elapsed_sec >= self.config.hold_sec
        self.started_sec = None
        self.elapsed_sec = float("nan")
        return False


def recenter_command(direction, yaw, distance_m, config=None):
    """Return bounded linear/angular command for one selected safe direction."""

    config = config or RecenterControlConfig()
    direction = _unit(direction, "recenter direction")
    if not np.all(np.isfinite([yaw, distance_m])) or distance_m < 0.0:
        raise ValueError("recenter yaw and distance must be finite")
    desired_heading = math.atan2(direction[1], direction[0])
    heading_error = wrap_angle(desired_heading - float(yaw))
    angular = float(
        np.clip(
            config.angular_gain * heading_error,
            -config.max_angular_velocity_rps,
            config.max_angular_velocity_rps,
        )
    )
    if distance_m <= config.tolerance_m or abs(heading_error) >= config.rotate_in_place_angle_rad:
        linear = 0.0
    else:
        linear = min(
            config.max_linear_velocity_mps,
            config.linear_gain * float(distance_m),
        ) * max(0.0, math.cos(heading_error))
    return float(linear), angular
