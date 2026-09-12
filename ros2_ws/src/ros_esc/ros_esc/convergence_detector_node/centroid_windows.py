"""Timestamped positional confinement, shared by the ROS owner and replay.

This detector observes spatial settling; it does not establish an extremum or
authorize a fill. Positions between observed samples are represented by line
segments. Integration and radius checks use that same representation.
"""

import math
from collections import deque
from dataclasses import dataclass, replace
from numbers import Integral

from ros_esc.convergence_detector_node.centroid_contract import (
    CENTROID_METRIC_MODES, CENTROID_WINDOWS_V2, centroid_score,
)

NANOSECONDS_PER_SECOND = 1_000_000_000
WINDOW_COUNT = 6
MAX_RETAINED_POINTS = 100_000
MAX_COMPLETIONS_PER_SAMPLE = 1_024


@dataclass(frozen=True)
class CentroidConfig:
    """Development parameters; empirical calibration is a separate gate."""

    window_seconds: float = 3.0
    epsilon_m: float = 0.06
    max_radius_m: float = 0.5
    max_gap_seconds: float = 0.5
    metric_mode: str = CENTROID_WINDOWS_V2

    def __post_init__(self):
        """Reject invalid thresholds and unrepresentable time intervals."""
        if self.metric_mode not in CENTROID_METRIC_MODES:
            raise ValueError('unsupported centroid metric mode')
        for name in (
            'window_seconds', 'epsilon_m', 'max_radius_m', 'max_gap_seconds'
        ):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f'{name} must be a finite positive number')
            if not math.isfinite(value) or value <= 0.0:
                raise ValueError(f'{name} must be a finite positive number')
        for name in ('window_seconds', 'max_gap_seconds'):
            scaled = getattr(self, name) * NANOSECONDS_PER_SECOND
            if not math.isfinite(scaled) or round(scaled) < 1:
                raise ValueError(
                    f'{name} must represent at least one nanosecond'
                )


@dataclass(frozen=True)
class CentroidResult:
    """One immutable evaluation or observation-status snapshot.

    Centroids and bounds are oldest first. ``sample_count`` counts source
    observations whose timestamps lie in the completed support, excluding
    interpolated vertices. ``max_source_gap_ns`` includes accepted source
    segments used to interpolate its boundary positions. Incomplete support
    has no score and cannot be eligible.
    """

    epoch_id: str
    frame_id: str
    stamp_ns: int | None
    start_ns: int | None = None
    end_ns: int | None = None
    window_bounds_ns: tuple = ()
    centroids: tuple = ()
    deltas_m: tuple = ()
    score_m: float | None = None
    radius_m: float | None = None
    mean_xy: tuple | None = None
    sample_count: int = 0
    max_source_gap_ns: int = 0
    represented_duration_ns: int = 0
    reset_sequence: int = 0
    full: bool = False
    eligible: bool = False
    confirmed_event: bool = False
    window_completed: bool = False
    reset_reason: str = ''


@dataclass(frozen=True)
class _Window:
    start_ns: int
    end_ns: int
    centroid: tuple
    points: tuple
    source_count: int
    start_is_source: bool
    maximum_gap_ns: int


class CentroidWindowDetector:
    """Observe six complete windows and emit at most once per explicit epoch.

    ``update`` returns an ordered tuple so a segment crossing several window
    boundaries never loses an evaluation. With no boundary it returns one
    status result with ``window_completed=False``. Completed evaluations use
    their exact window-end timestamp, including interpolated boundaries.

    History faults preserve the confirmation latch. Only a new identity in
    ``start_epoch`` rearms it; calling that method with the same ID is a no-op.
    """

    def __init__(self, config=None):
        """Construct an unarmed detector with bounded observation history."""
        self.config = config if config is not None else CentroidConfig()
        if not isinstance(self.config, CentroidConfig):
            raise TypeError('config must be CentroidConfig')
        self.window_ns = round(
            self.config.window_seconds * NANOSECONDS_PER_SECOND
        )
        self.maximum_gap_ns = round(
            self.config.max_gap_seconds * NANOSECONDS_PER_SECOND
        )
        self.epoch_id = ''
        self.confirmed = False
        self.reset_sequence = 0
        self._clear_history()

    @property
    def retained_point_count(self):
        """Count vertices in six completed windows plus the open window."""
        return len(self._points) + sum(len(w.points) for w in self._windows)

    def _clear_history(self):
        self._windows = deque(maxlen=WINDOW_COUNT)
        self._points = []
        self._previous_stamp = None
        self._previous_xy = None
        self._frame_id = ''
        self._window_start = None
        self._integral = [0.0, 0.0]
        self._source_count = 0
        self._start_is_source = False
        self._maximum_gap = 0
        self._latest = None
        self._pending_reason = ''

    def start_epoch(self, epoch_id):
        """Clear history and rearm only when the explicit epoch changes."""
        if not isinstance(epoch_id, str) or not epoch_id.strip():
            raise ValueError('epoch_id must be a nonempty string')
        if epoch_id == self.epoch_id:
            return
        self.epoch_id = epoch_id
        self.confirmed = False
        self.invalidate('epoch_started')
        self._pending_reason = 'epoch_started'

    def invalidate(self, reason):
        """Discard unsupported history without rearming a confirmed epoch."""
        if not isinstance(reason, str) or not reason:
            raise ValueError('invalidation reason must be a nonempty string')
        self._clear_history()
        self.reset_sequence += 1
        return self._status(None, reset_reason=reason)

    def _seed(self, stamp_ns, xy, frame_id):
        self._previous_stamp = stamp_ns
        self._previous_xy = xy
        self._frame_id = frame_id
        self._window_start = stamp_ns
        self._points = [xy]
        self._start_is_source = True

    def _restart(self, stamp_ns, xy, frame_id, reason):
        self.invalidate(reason)
        self._seed(stamp_ns, xy, frame_id)
        return (self._status(stamp_ns, reset_reason=reason),)

    def _status(self, stamp_ns, reset_reason=''):
        if self._latest is not None:
            return replace(
                self._latest, stamp_ns=stamp_ns, window_completed=False,
                confirmed_event=False, reset_reason=reset_reason,
            )
        return CentroidResult(
            epoch_id=self.epoch_id, frame_id=self._frame_id,
            stamp_ns=stamp_ns, reset_sequence=self.reset_sequence,
            reset_reason=reset_reason,
        )

    def update(self, stamp_ns, xy, frame_id):
        """Integrate one absolute, integer-nanosecond source observation."""
        if not self.epoch_id:
            return (self._status(None, reset_reason='epoch_not_started'),)
        if (
            not isinstance(stamp_ns, Integral)
            or isinstance(stamp_ns, bool)
            or stamp_ns < 0
        ):
            return (self.invalidate('invalid_stamp'),)
        stamp_ns = int(stamp_ns)
        try:
            if isinstance(xy, (str, bytes)) or len(xy) != 2:
                raise ValueError('position must contain two coordinates')
            point = (float(xy[0]), float(xy[1]))
            if not all(math.isfinite(value) for value in point):
                raise ValueError('position must be finite')
        except (TypeError, ValueError, OverflowError):
            return (self.invalidate('invalid_position'),)
        if not isinstance(frame_id, str) or not frame_id.strip():
            return (self.invalidate('invalid_frame'),)
        if self._previous_stamp is None:
            reason = self._pending_reason
            self._pending_reason = ''
            self._seed(stamp_ns, point, frame_id)
            return (self._status(stamp_ns, reset_reason=reason),)
        if frame_id != self._frame_id:
            return self._restart(stamp_ns, point, frame_id, 'frame_changed')
        if stamp_ns < self._previous_stamp:
            return self._restart(stamp_ns, point, frame_id, 'time_rollback')
        if stamp_ns == self._previous_stamp:
            return (self._status(stamp_ns),)
        gap = stamp_ns - self._previous_stamp
        if gap > self.maximum_gap_ns:
            return self._restart(stamp_ns, point, frame_id, 'source_gap')
        if self.retained_point_count >= MAX_RETAINED_POINTS:
            return self._restart(stamp_ns, point, frame_id, 'sample_capacity')
        completions = (stamp_ns - self._window_start) // self.window_ns
        if completions > MAX_COMPLETIONS_PER_SAMPLE:
            return self._restart(stamp_ns, point, frame_id, 'window_capacity')

        segment_start = self._previous_stamp
        segment_point = self._previous_xy
        results = []
        while segment_start < stamp_ns:
            boundary = self._window_start + self.window_ns
            segment_end = min(boundary, stamp_ns)
            required_points = 1 + int(segment_end == boundary)
            if (
                self.retained_point_count + required_points
                > MAX_RETAINED_POINTS
            ):
                return tuple(results) + self._restart(
                    stamp_ns, point, frame_id, 'sample_capacity',
                )
            fraction = (segment_end - self._previous_stamp) / gap
            endpoint = tuple(
                (1.0 - fraction) * old + fraction * new
                for old, new in zip(self._previous_xy, point)
            )
            weight = (segment_end - segment_start) / self.window_ns
            for axis in (0, 1):
                self._integral[axis] += (
                    0.5 * segment_point[axis] + 0.5 * endpoint[axis]
                ) * weight
            if not all(math.isfinite(value) for value in self._integral):
                return tuple(results) + self._restart(
                    stamp_ns, point, frame_id, 'numerical_overflow',
                )
            self._points.append(endpoint)
            self._source_count += int(segment_end == stamp_ns)
            self._maximum_gap = max(self._maximum_gap, gap)
            if segment_end == boundary:
                self._windows.append(_Window(
                    self._window_start, boundary, tuple(self._integral),
                    tuple(self._points), self._source_count,
                    self._start_is_source, self._maximum_gap,
                ))
                self._window_start = boundary
                self._integral = [0.0, 0.0]
                self._points = [endpoint]
                self._source_count = 0
                self._start_is_source = segment_end == stamp_ns
                self._maximum_gap = 0
                try:
                    self._latest = self._evaluate(boundary)
                except (OverflowError, ValueError):
                    return tuple(results) + self._restart(
                        stamp_ns, point, frame_id, 'numerical_overflow',
                    )
                results.append(self._latest)
            segment_start = segment_end
            segment_point = endpoint
        self._previous_stamp = stamp_ns
        self._previous_xy = point
        return tuple(results) if results else (self._status(stamp_ns),)

    def _evaluate(self, stamp_ns):
        windows = tuple(self._windows)
        centroids = tuple(w.centroid for w in windows)
        deltas = tuple(
            math.hypot(new[0] - old[0], new[1] - old[1])
            for old, new in zip(centroids, centroids[1:])
        )
        mean = tuple(
            math.fsum(point[axis] / len(centroids) for point in centroids)
            for axis in (0, 1)
        )
        radius = max(
            math.hypot(point[0] - mean[0], point[1] - mean[1])
            for window in windows for point in window.points
        )
        full = len(windows) == WINDOW_COUNT
        score = centroid_score(centroids, self.config.metric_mode) if full else None
        if not all(math.isfinite(value) for value in (*mean, radius, *deltas)):
            raise ValueError('nonfinite confinement calculation')
        if score is not None and not math.isfinite(score):
            raise ValueError('nonfinite confinement score')
        eligible = bool(
            full and score < self.config.epsilon_m
            and radius <= self.config.max_radius_m
        )
        event = eligible and not self.confirmed
        self.confirmed = self.confirmed or event
        return CentroidResult(
            epoch_id=self.epoch_id, frame_id=self._frame_id,
            stamp_ns=stamp_ns, start_ns=windows[0].start_ns,
            end_ns=windows[-1].end_ns,
            window_bounds_ns=tuple((w.start_ns, w.end_ns) for w in windows),
            centroids=centroids, deltas_m=deltas, score_m=score,
            radius_m=radius, mean_xy=mean,
            sample_count=(
                sum(w.source_count for w in windows)
                + int(windows[0].start_is_source)
            ),
            max_source_gap_ns=max(w.maximum_gap_ns for w in windows),
            represented_duration_ns=windows[-1].end_ns - windows[0].start_ns,
            reset_sequence=self.reset_sequence, full=full, eligible=eligible,
            confirmed_event=event, window_completed=True,
        )
