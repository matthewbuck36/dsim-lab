"""Bounded current-cycle norm arithmetic for the selected moving policy.

Imported only by the opt-in rolling core. The quadrature and interval rules
preserve the frozen D3 arithmetic; this module has no ROS or experiment I/O.
"""

from dataclasses import dataclass
import math
import warnings

from scipy.integrate import quad


VERSION = 'moving-cycle-coherence-math-v1'
UNITS = 'cost_units_per_metre'
MAGNITUDE_FLOOR = 1e-6
COHERENCE_THRESHOLD = .25
MAX_GAP_NS = 500_000_000
MAX_CYCLE_NS = 30_000_000_000
MAX_NORM_CALLS = 20_000
MAX_NEW_NORM_CALLS = 2048
NORM_ERROR_CEILING = 1e-10
MEAN_ABSOLUTE_TOLERANCE = 1e-10
MEAN_RELATIVE_TOLERANCE = 1e-8
QUAD_EPSABS = 1e-12
QUAD_EPSREL = 1e-10
QUAD_LIMIT = 64


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _ns(value):
    return type(value) is int and 0 <= value <= 2**63-1


def _vector(value):
    return (isinstance(value, (tuple, list)) and len(value) == 2
            and all(_finite(item) for item in value) and math.isfinite(math.hypot(*value)))


class Unavailable(ValueError):
    pass


def _require(condition, reason):
    if not condition:
        raise Unavailable(reason)


@dataclass
class EvaluationBudget:
    max_calls: int = MAX_NEW_NORM_CALLS
    calls: int = 0

    def __post_init__(self):
        if type(self.max_calls) is not int or self.max_calls < 0 or self.calls != 0:
            raise ValueError('invalid norm evaluation budget')

    def consume(self):
        if self.calls >= self.max_calls:
            raise Unavailable('norm_evaluation_budget')
        self.calls += 1


def linear_norm_integral(start_xy, end_xy, *, duration_sec=1.0, budget=None):
    """Integrate ||(1-s)*a+s*b||, with one shared finite per-update budget."""
    budget = EvaluationBudget() if budget is None else budget
    result = {'available': False, 'reason': 'invalid_norm_segment',
              'mean_norm': None, 'mean_error': None, 'integral': None,
              'integral_error': None, 'evaluations': 0,
              'minimum_fraction': None, 'warnings': [], 'exception': None}
    if not _vector(start_xy) or not _vector(end_xy) or not _finite(duration_sec) or duration_sec <= 0:
        return result
    before = budget.calls
    # Scaling keeps the closest-point calculation finite for large endpoints.
    scale = max(map(abs, [*start_xy, *end_xy]))
    minimum = None
    if scale:
        a = [value/scale for value in start_xy]
        delta = [value/scale-first for first, value in zip(a, end_xy)]
        squared = math.fsum(value*value for value in delta)
        if squared:
            point = -math.fsum(x*v for x, v in zip(a, delta))/squared
            if 0. < point < 1.:
                minimum = point
    result['minimum_fraction'] = minimum

    def norm(fraction):
        budget.consume()
        vector = [(1-fraction)*a+fraction*b for a, b in zip(start_xy, end_xy)]
        value = math.hypot(*vector)
        if not math.isfinite(value):
            raise Unavailable('nonfinite_segment_norm')
        return value

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            values = quad(norm, 0., 1., points=[] if minimum is None else [minimum],
                          epsabs=QUAD_EPSABS, epsrel=QUAD_EPSREL,
                          limit=QUAD_LIMIT, full_output=True)
            value, error = float(values[0]), float(values[1])
            if not _finite(value) or not _finite(error) or min(value, error) < 0:
                raise Unavailable('invalid_norm_quadrature')
            result['warnings'].extend(str(message) for message in values[3:])
            integral, integral_error = value*duration_sec, error*duration_sec
            if not _finite(integral) or not _finite(integral_error):
                raise Unavailable('norm_integral_overflow')
            result.update(mean_norm=value, mean_error=error,
                          integral=integral, integral_error=integral_error)
        except TimeoutError:
            raise
        except Exception as exc:
            result['reason'] = str(exc) if isinstance(exc, Unavailable) else 'norm_quadrature_exception'
            result['exception'] = f'{type(exc).__name__}: {exc}'
        result['warnings'].extend(str(item.message) for item in caught)
    result['evaluations'] = budget.calls-before
    if result['warnings']:
        result['reason'] = 'norm_quadrature_warning'
    elif result['exception'] is None and result['mean_norm'] is not None:
        result.update(available=True, reason='available')
    return result


def coherence_interval(mean, denominator, denominator_error, mean_component_tolerance):
    """Propagate the frozen reconstruction tolerance and denominator estimate."""
    result = {'available': False, 'reason': 'invalid_coherence_inputs',
              'coherence': None, 'lower': None, 'upper': None, 'qualified': False}
    if (not _vector(mean) or not all(_finite(value) for value in
            (denominator, denominator_error, mean_component_tolerance))
            or denominator <= 0 or min(denominator_error, mean_component_tolerance) < 0):
        return result
    if denominator_error > NORM_ERROR_CEILING:
        result['reason'] = 'denominator_error_bound'
        return result
    if denominator <= denominator_error:
        result['reason'] = 'denominator_not_resolved_positive'
        return result
    numerator = math.hypot(*mean)
    numerator_error = math.sqrt(2)*mean_component_tolerance
    if numerator > denominator+denominator_error+numerator_error:
        result['reason'] = 'coherence_triangle_inequality'
        return result
    point = numerator/denominator
    lower = max(0., numerator-numerator_error)/(denominator+denominator_error)
    upper = min(1., (numerator+numerator_error)/(denominator-denominator_error))
    if not all(_finite(value) for value in (point, lower, upper)):
        result['reason'] = 'coherence_overflow'
        return result
    result.update(available=True, coherence=min(1., point), lower=lower, upper=upper,
                  qualified=lower >= COHERENCE_THRESHOLD,
                  reason='coherent' if lower >= COHERENCE_THRESHOLD else (
                      'coherence_below_threshold' if upper < COHERENCE_THRESHOLD
                      else 'coherence_threshold_unresolved'))
    return result


class NormCache:
    """One receipt per actual source segment; only the left clip is transient.

    Points are the existing rolling owner's immutable source points. The
    owner clears this object on every history reset and prunes it with points.
    """

    def __init__(self):
        self.receipts = {}
        self.budget = EvaluationBudget()

    def clear(self):
        self.receipts.clear()
        self.budget = EvaluationBudget()

    def begin_update(self):
        self.budget = EvaluationBudget()

    @staticmethod
    def key(left, right):
        return (left.stamp_ns, left.observation_id,
                right.stamp_ns, right.observation_id)

    def append(self, left, right):
        key = self.key(left, right)
        if key not in self.receipts:
            self.receipts[key] = linear_norm_integral(left.q, right.q, budget=self.budget)

    def prune(self, points):
        keep = {self.key(a, b) for a, b in zip(points, points[1:])}
        self.receipts = {key: value for key, value in self.receipts.items() if key in keep}

    def evaluate(self, start, end, points, mean):
        result = {'available': False, 'reason': 'missing_norm_support',
                  'denominator': None, 'denominator_error': None,
                  'coherence': None, 'lower': None, 'upper': None,
                  'qualified': False, 'window_evaluations': 0}
        duration = end.stamp_ns - start.stamp_ns
        if duration <= 0:
            return result
        support = [start] + [p for p in points
                             if start.stamp_ns < p.stamp_ns < end.stamp_ns] + [end]
        receipts = []
        for index, (left, right) in enumerate(zip(support, support[1:])):
            if left.observation_id is not None and right.observation_id is not None:
                receipt = self.receipts.get(self.key(left, right))
                if receipt is None:
                    return result
            elif index == 0 and left.observation_id is None and right.observation_id is not None:
                receipt = linear_norm_integral(left.q, right.q, budget=self.budget)
            else:
                return result
            result['window_evaluations'] += receipt['evaluations']
            if result['window_evaluations'] > MAX_NORM_CALLS:
                result['reason'] = 'norm_window_evaluation_budget'
                return result
            if not receipt['available']:
                result['reason'] = receipt['reason']
                return result
            receipts.append(((right.stamp_ns-left.stamp_ns)/duration, receipt))
        denominator = math.fsum(dt * value['mean_norm'] for dt, value in receipts)
        error = math.fsum(dt * value['mean_error'] for dt, value in receipts)
        margin = MEAN_ABSOLUTE_TOLERANCE + MEAN_RELATIVE_TOLERANCE * math.hypot(*mean)
        result.update(coherence_interval(mean, denominator, error, margin),
                      denominator=denominator, denominator_error=error)
        return result
