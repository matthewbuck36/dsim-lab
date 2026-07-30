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

    def contains_physical(self, point):
        """Return whether a robot-center point remains inside the room faces."""
        point = _finite_vector(point, 'point')
        return bool(
            self.x_min <= point[0] <= self.x_max
            and self.y_min <= point[1] <= self.y_max
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
    return evaluate_direction_safety(position, direction, fills, config, bounds)


def evaluate_direction_safety(
    position,
    direction,
    fills: Sequence[FillAvoidance],
    config: DirectionConfig,
    bounds: Optional[OperatingBounds] = None,
):
    """Return hard fill/wall eligibility without a progress preference."""
    position = _finite_vector(position, 'position')
    direction = _unit(direction, 'candidate direction')
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


def _direction_candidates(preferred, config):
    preferred = _unit(preferred, 'preferred direction')
    base_angle = math.atan2(preferred[1], preferred[0])
    step = config.candidate_step_rad
    rotations = (0.0, step, -step, 2 * step, -2 * step, 3 * step, -3 * step, math.pi)
    seen = []
    for index, rotation in enumerate(rotations):
        angle = base_angle + rotation
        direction = np.array([math.cos(angle), math.sin(angle)], dtype=np.float64)
        if any(float(np.linalg.norm(direction - prior)) <= _EPSILON for prior in seen):
            continue
        seen.append(direction)
        yield index, float(rotation), direction


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
    selections = []
    for index, rotation, direction in _direction_candidates(preferred, config):
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


def select_post_recovery_direction(
    position,
    preferred,
    fills: Sequence[FillAvoidance],
    config=None,
    bounds: Optional[OperatingBounds] = None,
):
    """Select a hard-safe direction without forbidding the backward half-plane."""
    config = config or DirectionConfig()
    position = _finite_vector(position, 'position')
    preferred = _unit(preferred, 'preferred direction')
    selections = []
    for index, rotation, direction in _direction_candidates(preferred, config):
        safe, clearance = evaluate_direction_safety(
            position, direction, fills, config, bounds
        )
        if not safe:
            continue
        endpoint = position + config.lookahead_m * direction
        fill_progress = min(
            (
                float(np.linalg.norm(endpoint - fill.center))
                - float(np.linalg.norm(position - fill.center))
                for fill in fills
            ),
            default=0.0,
        )
        alignment = float(np.dot(direction, preferred))
        selection = DirectionSelection(
            x=float(direction[0]),
            y=float(direction[1]),
            clearance_m=clearance,
            rotation_rad=float(rotation),
            candidate_index=index,
        )
        score = (
            round(clearance, 12),
            round(fill_progress, 12),
            round(alignment, 12),
            -round(abs(rotation), 12),
            -index,
        )
        selections.append((score, selection))
    if not selections:
        return None
    return max(selections, key=lambda item: item[0])[1]


def _point_outside_fills(point, fills, clearance_m=0.0):
    point = _finite_vector(point, 'point')
    return all(
        float(np.linalg.norm(point - fill.center))
        > fill.radius + clearance_m + _EPSILON
        for fill in fills
    )


def select_safe_recenter_target(
    position,
    preferred_target,
    fills: Sequence[FillAvoidance],
    bounds: OperatingBounds,
    clearance_m=0.05,
    angular_samples=32,
):
    """Choose the closest in-bounds target outside all active fill regions."""
    position = _finite_vector(position, 'position')
    preferred_target = _finite_vector(
        preferred_target, 'preferred recenter target'
    )
    if not math.isfinite(float(clearance_m)) or clearance_m < 0.0:
        raise ValueError('recenter target clearance must be finite and nonnegative')
    if (
        isinstance(angular_samples, bool)
        or not isinstance(angular_samples, int)
        or angular_samples < 8
    ):
        raise ValueError('recenter target angular samples must be at least eight')

    if (
        bounds.contains(preferred_target)
        and _point_outside_fills(preferred_target, fills, clearance_m)
    ):
        return np.array(preferred_target, copy=True)

    candidates = []
    ordered_fills = sorted(fills, key=lambda item: (item.cluster_id, item.fill_id))
    for fill in ordered_fills:
        # Place generated candidates just beyond the requested clearance
        # boundary.  The strict comparison in _point_outside_fills prevents a
        # point exactly on that boundary from being treated as a valid target.
        radius = fill.radius + clearance_m + 1e-6
        current_angle = math.atan2(
            position[1] - fill.center_y,
            position[0] - fill.center_x,
        )
        center_angle = math.atan2(
            preferred_target[1] - fill.center_y,
            preferred_target[0] - fill.center_x,
        )
        angles = [current_angle, center_angle]
        angles.extend(
            2.0 * math.pi * index / angular_samples
            for index in range(angular_samples)
        )
        for angle in angles:
            candidate = fill.center + radius * np.array(
                [math.cos(angle), math.sin(angle)], dtype=np.float64
            )
            if not bounds.contains(candidate):
                continue
            if not _point_outside_fills(candidate, fills, clearance_m):
                continue
            candidates.append(candidate)

    if not candidates:
        return None

    def score(candidate):
        return (
            round(float(np.linalg.norm(candidate - preferred_target)), 12),
            round(float(np.linalg.norm(candidate - position)), 12),
            round(float(candidate[0]), 12),
            round(float(candidate[1]), 12),
        )

    return np.array(min(candidates, key=score), copy=True)


def _segment_blocking_fill(position, target, fills):
    """Return the first deterministic fill blocking a complete target segment."""
    position = _finite_vector(position, 'position')
    target = _finite_vector(target, 'target')
    segment = target - position
    length_squared = float(np.dot(segment, segment))
    blockers = []
    for fill in sorted(fills, key=lambda item: (item.cluster_id, item.fill_id)):
        start_distance = float(np.linalg.norm(position - fill.center))
        if start_distance <= fill.radius + _EPSILON:
            fraction = 0.0
        elif length_squared <= _EPSILON:
            continue
        else:
            fraction = float(
                np.dot(fill.center - position, segment) / length_squared
            )
            if fraction < 0.0 or fraction > 1.0:
                continue
        clearance = _segment_clearance(position, target, fill.center)
        if clearance <= fill.radius + _EPSILON:
            blockers.append((round(fraction, 12), fill.cluster_id, fill.fill_id, fill))
    return min(blockers, default=(None, None, None, None))[-1]


class RecenterRoutePlanner:
    """Select safe recenter directions while retaining one obstacle side."""

    def __init__(self):
        self.blocking_cluster_id = None
        self.side = 0

    def reset(self):
        self.blocking_cluster_id = None
        self.side = 0

    def select(
        self,
        position,
        target,
        fills: Sequence[FillAvoidance],
        config=None,
        bounds: Optional[OperatingBounds] = None,
    ):
        """Return a deterministic hard-safe direction toward a frozen target."""
        config = config or DirectionConfig()
        position = _finite_vector(position, 'position')
        target = _finite_vector(target, 'recenter target')
        preferred_vector = target - position
        if float(np.linalg.norm(preferred_vector)) <= _EPSILON:
            self.reset()
            return None
        preferred = _unit(preferred_vector, 'preferred direction')
        blocker = _segment_blocking_fill(position, target, fills)
        if blocker is None:
            self.reset()
            return select_recenter_direction(
                position, target, fills, config, bounds
            )

        if self.blocking_cluster_id != blocker.cluster_id:
            self.blocking_cluster_id = blocker.cluster_id
            self.side = 0

        current_distance = float(np.linalg.norm(preferred_vector))
        candidates = []
        for index, rotation, direction in _direction_candidates(preferred, config):
            safe, clearance = evaluate_direction_safety(
                position, direction, fills, config, bounds
            )
            if not safe:
                continue
            radial = position - blocker.center
            cross = float(
                radial[0] * direction[1] - radial[1] * direction[0]
            )
            candidate_side = 0
            if cross > _EPSILON:
                candidate_side = 1
            elif cross < -_EPSILON:
                candidate_side = -1
            if (
                self.side != 0
                and candidate_side != 0
                and candidate_side != self.side
            ):
                continue
            endpoint = position + config.lookahead_m * direction
            progress = current_distance - float(np.linalg.norm(target - endpoint))
            outward = float(np.dot(direction, radial))
            selection = DirectionSelection(
                x=float(direction[0]),
                y=float(direction[1]),
                clearance_m=clearance,
                rotation_rad=float(rotation),
                candidate_index=index,
            )
            score = (
                round(progress, 12),
                round(outward, 12),
                round(clearance, 12),
                -round(abs(rotation), 12),
                -index,
            )
            candidates.append((score, candidate_side, selection))

        if not candidates and self.side != 0:
            self.side = 0
            return self.select(position, target, fills, config, bounds)
        if not candidates:
            return None
        unused_score, selected_side, selection = max(
            candidates, key=lambda item: item[0]
        )
        if self.side == 0 and selected_side != 0:
            self.side = selected_side
        return selection


def select_recenter_direction(
    position,
    target,
    fills: Sequence[FillAvoidance],
    config=None,
    bounds: Optional[OperatingBounds] = None,
):
    """Select the deterministic safe candidate with greatest center progress."""
    config = config or DirectionConfig()
    position = _finite_vector(position, 'position')
    target = _finite_vector(target, 'recenter target')
    preferred_vector = target - position
    if float(np.linalg.norm(preferred_vector)) <= _EPSILON:
        return None
    preferred = _unit(preferred_vector, 'preferred direction')
    current_distance = float(np.linalg.norm(preferred_vector))
    selections = []
    for index, rotation, direction in _direction_candidates(preferred, config):
        safe, clearance = evaluate_direction_safety(
            position, direction, fills, config, bounds
        )
        if not safe:
            continue
        endpoint = position + config.lookahead_m * direction
        progress = current_distance - float(np.linalg.norm(target - endpoint))
        alignment = float(np.dot(direction, preferred))
        selection = DirectionSelection(
            x=float(direction[0]),
            y=float(direction[1]),
            clearance_m=clearance,
            rotation_rad=float(rotation),
            candidate_index=index,
        )
        score = (
            round(progress, 12),
            round(alignment, 12),
            round(clearance, 12),
            -round(abs(rotation), 12),
            -index,
        )
        selections.append((score, selection))
    if not selections:
        return None
    return max(selections, key=lambda item: item[0])[1]


def command_sweep_is_safe(
    position,
    yaw,
    linear_velocity_mps,
    horizon_sec,
    fills: Sequence[FillAvoidance],
    bounds: Optional[OperatingBounds] = None,
    allow_inward_from_margin=False,
    boundary_trigger_clearance_m=None,
):
    """Check the current-yaw forward sweep for the command persistence horizon."""
    position = _finite_vector(position, 'position')
    values = np.asarray(
        [yaw, linear_velocity_mps, horizon_sec], dtype=np.float64
    )
    if not np.all(np.isfinite(values)):
        raise ValueError('command sweep values must be finite')
    if linear_velocity_mps < 0.0 or horizon_sec < 0.0:
        raise ValueError('command sweep velocity and horizon must be nonnegative')
    if (
        boundary_trigger_clearance_m is not None
        and (
            not math.isfinite(float(boundary_trigger_clearance_m))
            or float(boundary_trigger_clearance_m) < 0.0
        )
    ):
        raise ValueError('boundary trigger clearance must be finite and nonnegative')

    heading = np.array([math.cos(float(yaw)), math.sin(float(yaw))])
    endpoint = position + float(linear_velocity_mps * horizon_sec) * heading
    if bounds is not None:
        if not allow_inward_from_margin:
            if not bounds.contains(position) or not bounds.contains(endpoint):
                return False
        elif (
            not bounds.contains_physical(position)
            or not bounds.contains_physical(endpoint)
        ):
            return False
        else:
            start_clearance = bounds.clearance(position)
            endpoint_clearance = bounds.clearance(endpoint)
            if bounds.contains(position):
                if not bounds.contains(endpoint):
                    return False
                if (
                    boundary_trigger_clearance_m is not None
                    and start_clearance
                    <= float(boundary_trigger_clearance_m) + _EPSILON
                    and endpoint_clearance < start_clearance - _EPSILON
                ):
                    return False
            elif endpoint_clearance <= start_clearance + _EPSILON:
                return False

    translating = linear_velocity_mps > _EPSILON and horizon_sec > _EPSILON
    for fill in sorted(fills, key=lambda item: (item.cluster_id, item.fill_id)):
        offset = position - fill.center
        start_distance = float(np.linalg.norm(offset))
        endpoint_distance = float(np.linalg.norm(endpoint - fill.center))
        if start_distance <= fill.radius + _EPSILON:
            outward_projection = float(np.dot(heading, offset))
            if translating and outward_projection < -_EPSILON:
                return False
            if endpoint_distance < start_distance - _EPSILON:
                return False
        elif _segment_clearance(position, endpoint, fill.center) <= fill.radius + _EPSILON:
            return False
    return True


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
