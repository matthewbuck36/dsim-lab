"""Bounded causal static, arc-center and harmonic recurrence detector.

All geometry includes original source vertices. The harmonic fit alone uses a
fixed interpolated representation. This observes confinement, never a source.
"""
import math
from collections import deque
from dataclasses import dataclass, replace
from functools import lru_cache
from numbers import Integral

import numpy as np

from .centroid_windows import CentroidResult
from .recurrent_contract import RECURRENT_MODE, SCORE_SCALE_SEC

NS = 1_000_000_000
EVALUATION_NS = 6 * NS
MAX_RETAINED_POINTS = 100_000
BRANCHES = (('static', 30), ('circle', 30), ('circle', 36),
            ('oscillation', 36), ('oscillation', 54))


@dataclass(frozen=True)
class RecurrentConfig:
    max_gap_seconds: float = .5
    metric_mode: str = RECURRENT_MODE
    # Common node logging fields; fixed model constants, not centroid tuning.
    window_seconds: float = 6.0
    epsilon_m: float = .072
    max_radius_m: float = .5

    def __post_init__(self):
        if (self.metric_mode != RECURRENT_MODE or self.window_seconds != 6.
                or self.epsilon_m != .072 or self.max_radius_m != .5
                or isinstance(self.max_gap_seconds, bool)
                or not isinstance(self.max_gap_seconds, (int, float))
                or not math.isfinite(self.max_gap_seconds)
                or not 0 < self.max_gap_seconds <= .5
                or round(self.max_gap_seconds * NS) < 1):
            raise ValueError('invalid recurrent geometry configuration')


@dataclass(frozen=True)
class RecurrentResult(CentroidResult):
    branch: str = ''
    support_duration_sec: float = 0.
    persistence_start_ns: int | None = None
    persistence_count: int = 0
    persistence_required: int = 0
    drift_m_s: float = math.nan
    maximum_drift_m_s: float = math.nan
    fit_residual_rms_m: float = math.nan
    radius_difference_m: float = math.nan
    period_sec: float = math.nan
    amplitude_m: float = math.nan
    perpendicular_rms_m: float = math.nan
    axis_variance_ratio: float = math.nan
    design_condition: float = math.nan
    arc_center_x_m: tuple = ()
    arc_center_y_m: tuple = ()
    arc_radius_m: tuple = ()
    arc_radial_rms_m: tuple = ()
    arc_net_angle_rad: tuple = ()
    fit_rejection_reason: str = ''


def diagnostic_model_fields(result):
    """Pure model fields; transport supplies timestamps and identity envelope."""
    names = ('branch support_duration_sec persistence_count persistence_required '
             'drift_m_s maximum_drift_m_s fit_residual_rms_m radius_difference_m '
             'period_sec amplitude_m perpendicular_rms_m axis_variance_ratio '
             'design_condition arc_center_x_m arc_center_y_m arc_radius_m '
             'arc_radial_rms_m arc_net_angle_rad fit_rejection_reason').split()
    fields = {name: getattr(result, name) for name in names}
    fields.update(evaluation_interval_sec=6., score_scale_sec=SCORE_SCALE_SEC,
                  score_threshold_m=result.maximum_drift_m_s * SCORE_SCALE_SEC)
    return fields


def support(stamps, points, start, end):
    """Trapezoid support in relative seconds, with exact bracketed boundaries."""
    if (len(stamps) < 2 or stamps[0] > start or stamps[-1] < end
            or not np.isfinite(points).all() or not np.all(np.diff(stamps) > 0)):
        raise ValueError('unsupported source history')
    inner = (stamps > start) & (stamps < end)
    times = np.concatenate(([start], stamps[inner], [end]))
    xy = np.column_stack([np.interp(times, stamps, points[:, j]) for j in (0, 1)])
    delta = np.diff(times)
    weights = np.zeros(len(times))
    weights[:-1] += delta / 2
    weights[1:] += delta / 2
    weights /= end - start
    return times, xy, weights


def circle_fit(times, points, weights):
    origin = np.sum(weights[:, None] * points, axis=0)
    centered = points - origin
    design = np.column_stack((2 * centered, np.ones(len(times))))
    coefficient, _, rank, _ = np.linalg.lstsq(
        design * np.sqrt(weights[:, None]),
        np.sum(centered * centered, axis=1) * np.sqrt(weights), rcond=None)
    square = float(coefficient[2] + coefficient[:2] @ coefficient[:2])
    if rank != 3 or square <= 0 or not math.isfinite(square):
        raise ValueError('invalid circle fit')
    center = origin + coefficient[:2]
    radius = math.sqrt(square)
    radial = np.linalg.norm(points - center, axis=1)
    rms = math.sqrt(float(weights @ ((radial - radius) ** 2)))
    bearing = np.unwrap(np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0]))
    return center, radius, rms, float(bearing[-1] - bearing[0])


@lru_cache(maxsize=2)
def harmonic_design(width):
    times = np.arange(round(width / .2) + 1) * .2 - width / 2
    weights = np.ones(len(times)); weights[[0, -1]] = .5
    weights /= weights.sum()
    periods = np.arange(6., min(96., width / .75) + .01, .5)
    designs = np.array([np.column_stack((np.ones(len(times)), times / width,
                      np.cos(2 * np.pi * times / period),
                      np.sin(2 * np.pi * times / period))) for period in periods])
    weighted = designs * np.sqrt(weights)[None, :, None]
    return times, weights, periods, designs, np.linalg.pinv(weighted), np.linalg.cond(weighted)


def evaluate_model(branch, width, stamps, points, end):
    times, xy, weights = support(stamps, points, end - width, end)
    mean = np.sum(weights[:, None] * xy, axis=0)
    centered = xy - mean
    radius = float(np.max(np.linalg.norm(centered, axis=1)))
    out = dict(mean_xy=tuple(mean), radius_m=radius, maximum_drift_m_s=.005 if branch == 'static' else .006)
    passed = False
    if branch == 'static':
        design = np.column_stack((np.ones(len(times)), times - (end - width / 2)))
        coef = np.linalg.lstsq(design * np.sqrt(weights[:, None]),
                              centered * np.sqrt(weights[:, None]), rcond=None)[0]
        out.update(drift_m_s=float(np.linalg.norm(coef[1])),
                   fit_residual_rms_m=math.sqrt(float(np.sum(weights[:, None] * (design @ coef - centered) ** 2))))
        passed = radius <= .04 and out['drift_m_s'] <= .005
    elif branch == 'circle':
        half = width / 2
        old = circle_fit(*support(stamps, points, end - width, end - half))
        new = circle_fit(*support(stamps, points, end - half, end))
        out.update(mean_xy=tuple((old[0] + new[0]) / 2),
                   drift_m_s=float(np.linalg.norm(new[0] - old[0]) / half),
                   radius_difference_m=abs(new[1] - old[1]),
                   fit_residual_rms_m=max(old[2], new[2]),
                   arc_center_x_m=(float(old[0][0]), float(new[0][0])),
                   arc_center_y_m=(float(old[0][1]), float(new[0][1])),
                   arc_radius_m=(old[1], new[1]), arc_radial_rms_m=(old[2], new[2]),
                   arc_net_angle_rad=(old[3], new[3]))
        passed = (radius <= .5 and out['drift_m_s'] <= .006
                  and out['radius_difference_m'] <= .08
                  and all(.03 <= arc[1] <= .5 and arc[2] <= .02
                          and abs(arc[3]) >= math.pi / 3 for arc in (old, new)))
    else:
        cov = centered.T @ (weights[:, None] * centered)
        values = np.linalg.eigvalsh(cov)
        perpendicular = math.sqrt(max(0., float(values[0])))
        ratio = float(values[0] / values[1]) if values[1] > 1e-12 else 1.
        out.update(perpendicular_rms_m=perpendicular, axis_variance_ratio=ratio)
        if radius > .5 or perpendicular > .02 or ratio > .1:
            return dict(out, eligible=False, fit_rejection_reason='not_confined_line_geometry')
        t, w, periods, designs, inverses, conditions = harmonic_design(width)
        actual = np.column_stack([np.interp(t + end - width / 2, stamps, points[:, j]) for j in (0, 1)]) - mean
        coefficients = np.einsum('pkn,nj->pkj', inverses, actual * np.sqrt(w[:, None]))
        predicted = np.einsum('pnk,pkj->pnj', designs, coefficients)
        loss = np.einsum('n,pnj,pnj->p', w, predicted - actual[None, :, :], predicted - actual[None, :, :])
        i = int(np.argmin(loss))
        out.update(drift_m_s=float(np.linalg.norm(coefficients[i, 1]) / width),
                   amplitude_m=float(np.linalg.svd(coefficients[i, 2:4].T, compute_uv=False)[0]),
                   fit_residual_rms_m=math.sqrt(max(0., float(loss[i]))),
                   period_sec=float(periods[i]), design_condition=float(conditions[i]),
                   mean_xy=tuple(mean + coefficients[i, 0]))
        passed = (out['drift_m_s'] <= .006 and out['amplitude_m'] >= .05
                  and out['fit_residual_rms_m'] <= .02 and out['design_condition'] <= 50.)
    return dict(out, eligible=passed, fit_rejection_reason='model_pass' if passed else 'model_guard')


class RecurrentGeometryDetector:
    """Source-time core. At most five finite fits per six-second endpoint."""
    def __init__(self, config=None):
        self.config = config or RecurrentConfig()
        if not isinstance(self.config, RecurrentConfig):
            raise TypeError('config must be RecurrentConfig')
        self.maximum_gap_ns = round(self.config.max_gap_seconds * NS)
        self.epoch_id = ''; self.epoch_start_ns = None
        self.confirmed = False; self.reset_sequence = 0
        self._clear_history()

    def _clear_history(self):
        self._points = deque(); self._frame_id = ''; self._next = None
        self._latest = None; self._streaks = {key: deque(maxlen=3) for key in BRANCHES}

    @property
    def retained_point_count(self):
        return len(self._points)

    def start_epoch(self, epoch_id, start_ns=None):
        if not isinstance(epoch_id, str) or not epoch_id.strip():
            raise ValueError('epoch_id must be nonempty')
        if start_ns is not None and (isinstance(start_ns, bool) or not isinstance(start_ns, Integral) or start_ns < 0):
            raise ValueError('invalid epoch origin')
        if epoch_id == self.epoch_id:
            return
        self.epoch_id = epoch_id; self.epoch_start_ns = start_ns; self.confirmed = False
        self.invalidate('epoch_started')

    def _status(self, stamp_ns, reason=''):
        if self._latest is not None:
            return replace(self._latest, stamp_ns=stamp_ns, window_completed=False,
                           confirmed_event=False, reset_reason=reason)
        return RecurrentResult(epoch_id=self.epoch_id, frame_id=self._frame_id,
                               stamp_ns=stamp_ns, reset_sequence=self.reset_sequence, reset_reason=reason)

    def invalidate(self, reason):
        if not isinstance(reason, str) or not reason:
            raise ValueError('invalidation reason must be nonempty')
        self._clear_history(); self.reset_sequence += 1
        return self._status(None, reason)

    def _seed(self, stamp, point, frame):
        self._frame_id = frame; self._points.append((stamp, point))
        origin = self.epoch_start_ns if self.epoch_start_ns is not None else stamp
        self._next = origin + ((stamp - origin) // EVALUATION_NS + 1) * EVALUATION_NS

    def update(self, stamp_ns, xy, frame_id):
        if not self.epoch_id:
            return (self._status(None, 'epoch_not_started'),)
        if isinstance(stamp_ns, bool) or not isinstance(stamp_ns, Integral) or stamp_ns < 0:
            return (self.invalidate('invalid_stamp'),)
        stamp_ns = int(stamp_ns)
        try:
            if isinstance(xy, (str, bytes)) or len(xy) != 2:
                raise ValueError('two coordinates required')
            point = tuple(float(v) for v in xy)
            if not all(math.isfinite(v) for v in point):
                raise ValueError('finite coordinates required')
        except (TypeError, ValueError, OverflowError):
            return (self.invalidate('invalid_position'),)
        if not isinstance(frame_id, str) or not frame_id.strip():
            return (self.invalidate('invalid_frame'),)
        if self.epoch_start_ns is not None and stamp_ns < self.epoch_start_ns:
            return (self.invalidate('pose_before_epoch'),)
        if not self._points:
            self._seed(stamp_ns, point, frame_id)
            return (self._status(stamp_ns),)
        previous, old = self._points[-1]
        reason = ('frame_changed' if frame_id != self._frame_id else
                  'time_rollback' if stamp_ns < previous else
                  'conflicting_duplicate' if stamp_ns == previous and point != old else
                  'source_gap' if stamp_ns - previous > self.maximum_gap_ns else
                  'sample_capacity' if len(self._points) >= MAX_RETAINED_POINTS else '')
        if reason:
            self.invalidate(reason); self._seed(stamp_ns, point, frame_id)
            return (self._status(stamp_ns, reason),)
        if stamp_ns == previous:
            return (self._status(stamp_ns),)
        self._points.append((stamp_ns, point))
        results = []
        if stamp_ns >= self._next:
            end_ns = self._next; self._next += EVALUATION_NS
            origin = end_ns - 54 * NS
            stamps_ns = np.array([row[0] for row in self._points], dtype=np.int64)
            stamps = (stamps_ns - origin) / NS
            points = np.array([row[1] for row in self._points])
            for branch, width in BRANCHES:
                start_ns = end_ns - width * NS
                base = dict(epoch_id=self.epoch_id, frame_id=self._frame_id, stamp_ns=end_ns,
                            reset_sequence=self.reset_sequence, branch=branch, support_duration_sec=float(width),
                            persistence_required=1 if branch == 'static' else 3, window_completed=True,
                            maximum_drift_m_s=.005 if branch == 'static' else .006)
                streak = self._streaks[(branch, width)]
                if stamps_ns[0] > start_ns:
                    streak.clear(); results.append(RecurrentResult(**base, fit_rejection_reason='incomplete_support'))
                    continue
                left = max(0, int(np.searchsorted(stamps_ns, start_ns, side='right')) - 1)
                right = min(len(stamps_ns)-1, int(np.searchsorted(stamps_ns, end_ns, side='left')))
                maximum_gap = int(np.max(np.diff(stamps_ns[left:right+1])))
                base.update(start_ns=start_ns, end_ns=end_ns, full=True,
                            represented_duration_ns=width * NS, max_source_gap_ns=maximum_gap,
                            sample_count=int(np.count_nonzero((stamps_ns >= start_ns) & (stamps_ns <= end_ns))))
                try:
                    model = evaluate_model(branch, width, stamps, points, 54.)
                except (ValueError, OverflowError, np.linalg.LinAlgError, FloatingPointError):
                    model = dict(eligible=False, fit_rejection_reason='invalid_model_fit')
                if model.pop('eligible'):
                    streak.append(start_ns)
                else:
                    streak.clear()
                count = min(len(streak), base['persistence_required'])
                eligible = count >= base['persistence_required']
                model['score_m'] = model.get('drift_m_s', math.nan) * SCORE_SCALE_SEC
                model.pop('maximum_drift_m_s', None)
                base.update(model, eligible=eligible, persistence_count=count,
                            persistence_start_ns=(start_ns if branch == 'static' else streak[0]) if streak else None,
                            confirmed_event=eligible and not self.confirmed)
                if eligible:
                    self.confirmed = True
                results.append(RecurrentResult(**base))
            self._latest = next((r for r in results if r.eligible), next((r for r in results if r.full), results[0]))
        cutoff = stamp_ns - 54 * NS
        while len(self._points) > 2 and self._points[1][0] <= cutoff:
            self._points.popleft()
        return tuple(results) if results else (self._status(stamp_ns),)
