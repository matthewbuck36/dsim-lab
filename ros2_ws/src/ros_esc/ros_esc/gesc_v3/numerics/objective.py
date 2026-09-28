"""Local selected objective composition; no publication/revision protocol."""
from dataclasses import dataclass
import math
import numpy as np
from .registry import active_fill_value


@dataclass(frozen=True)
class AffineTerm:
    anchor: tuple
    b0: tuple
    started_sec: float
    decay_rate: float = .0000005
    minimum_norm: float = 1e-4
    maximum_age_sec: float = 30.0

    def value(self, point, at_time):
        values = (*self.anchor, *self.b0, self.started_sec, self.decay_rate,
                  self.minimum_norm, self.maximum_age_sec, *point, at_time)
        if not all(math.isfinite(x) for x in values):
            raise ValueError('nonfinite affine objective')
        age = max(0.0, at_time-self.started_sec)
        if self.maximum_age_sec > 0 and age > self.maximum_age_sec:
            return 0.0
        vector = math.exp(-self.decay_rate*age)*np.asarray(self.b0)
        if float(np.linalg.norm(vector)) < self.minimum_norm:
            return 0.0
        return -float(np.dot(vector, np.asarray(point)-self.anchor))


@dataclass(frozen=True)
class ObjectiveValue:
    raw: float
    gaussian: float
    affine: float
    augmented: float


def compose_cost(raw_cost, sensor_xy, at_time, *, fills=(), affine_terms=(),
                 sensor_weight=1.0, gaussian_weight=1.0, affine_weight=1.0):
    """Evaluate at the measured sensor position and original source time."""
    if (len(sensor_xy) != 2 or not all(math.isfinite(x) for x in
            (raw_cost, *sensor_xy, at_time, sensor_weight, gaussian_weight, affine_weight))):
        raise ValueError('invalid objective inputs')
    gaussian = active_fill_value(sensor_xy, fills)
    affine = sum(term.value(sensor_xy, at_time) for term in affine_terms)
    augmented = sensor_weight*raw_cost+gaussian_weight*gaussian+affine_weight*affine
    if not all(math.isfinite(x) for x in (gaussian, affine, augmented)):
        raise ValueError('nonfinite objective result')
    return ObjectiveValue(float(raw_cost), float(gaussian), float(affine), float(augmented))
