"""Small immutable records used across adapters, numerical work and control."""

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Pose:
    stamp: float
    x: float
    y: float
    yaw: float
    frame: str = 'odom'

    def valid(self):
        return bool(self.frame) and all(math.isfinite(v) for v in
                                       (self.stamp, self.x, self.y, self.yaw))


@dataclass(frozen=True)
class Observation:
    """A host observation; a receipt timestamp never claims an ADC timestamp."""

    source_instance: str
    sequence: int
    stamp: float
    receipt_stamp: float
    pose: Pose
    phase: float
    raw_cost: float
    sensor_x: float
    sensor_y: float
    timestamp_basis: str = 'receipt'
    acquisition_uncertainty: float = math.nan
    pose_support_age: float = 0.0
    phase_support_age: float = 0.0
    device_sequence: int | None = None

    def valid(self):
        return (bool(self.source_instance) and self.sequence >= 0
                and self.pose.valid()
                and self.timestamp_basis in ('device', 'estimated', 'receipt')
                and all(math.isfinite(v) for v in
                        (self.stamp, self.receipt_stamp, self.phase, self.raw_cost,
                         self.sensor_x, self.sensor_y, self.pose_support_age,
                         self.phase_support_age))
                and self.pose_support_age >= 0 and self.phase_support_age >= 0
                and (math.isnan(self.acquisition_uncertainty)
                     or (math.isfinite(self.acquisition_uncertainty)
                         and self.acquisition_uncertainty >= 0)))


@dataclass(frozen=True)
class Command:
    vx: float = 0.0
    wz: float = 0.0

    def valid(self):
        return math.isfinite(self.vx) and math.isfinite(self.wz)


@dataclass(frozen=True)
class Event:
    stamp: float
    kind: str
    state: str
    reason: str


@dataclass(frozen=True)
class CoreConfig:
    input_expiry: float = 0.5
    control_hz: float = 20.0
    max_vx: float = 0.05
    max_wz: float = 0.30
    k_vx: float = 0.5
    k_wz: float = 5.0
    sensor_radius: float = 0.18
    washout_omega: float = 1.0
    candidate_radius: float = 0.75
    verification_timeout: float = 12.0
    preparation_timeout: float = 5.0
    escape_timeout: float = 35.0
    maximum_history: int = 20_000
    maximum_snapshot: int = 4_000

    def __post_init__(self):
        for name in ('input_expiry', 'control_hz', 'max_vx', 'max_wz', 'k_vx',
                     'k_wz', 'sensor_radius', 'washout_omega', 'candidate_radius',
                     'verification_timeout', 'preparation_timeout', 'escape_timeout'):
            value = getattr(self, name)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f'{name} must be finite and positive')
        if not 1 <= self.maximum_snapshot <= 4000:
            raise ValueError('maximum_snapshot must be in [1, 4000]')
        if self.maximum_history < self.maximum_snapshot:
            raise ValueError('history must contain a full snapshot')
