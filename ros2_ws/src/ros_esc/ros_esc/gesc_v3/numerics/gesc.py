"""Selected measured-phase GESC washout/demodulation, before-step Euler output."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Demodulation:
    source_stamp_ns: int
    direction_body: tuple
    state_before: float
    derivative: float
    state_after: float
    dt_sec: float


class InstantaneousGesc:
    """The original full-rotation filter: q = -(J-z) (2/d) [cos phi,sin phi].

    Evaluate output before integrating z_dot=omega*(J-z). A first sample or
    explicit history reset has dt=0. Source gaps reset state, never synthesize
    missing observations. The runtime owns admission and availability.
    """
    def __init__(self, *, omega=1.0, arm_length_m=.18, max_gap_ns=500_000_000):
        if not all(math.isfinite(x) and x > 0 for x in (omega, arm_length_m)):
            raise ValueError('positive finite GESC scales required')
        if type(max_gap_ns) is not int or max_gap_ns <= 0:
            raise ValueError('positive source gap required')
        self.omega = float(omega)
        self.arm_length_m = float(arm_length_m)
        self.max_gap_ns = max_gap_ns
        self.reset()

    def reset(self):
        self.state = 0.0
        self.previous_source_ns = None

    def update(self, source_stamp_ns, augmented_cost, demodulation_phase_rad):
        if (type(source_stamp_ns) is not int or source_stamp_ns < 0
                or not all(math.isfinite(x) for x in (augmented_cost, demodulation_phase_rad))):
            raise ValueError('invalid GESC sample')
        if self.previous_source_ns is not None:
            delta = source_stamp_ns - self.previous_source_ns
            if delta <= 0:
                raise ValueError('GESC source stamps must strictly increase')
            if delta > self.max_gap_ns:
                self.reset()
        dt = (0.0 if self.previous_source_ns is None else
              (source_stamp_ns-self.previous_source_ns)*1e-9)
        before = self.state
        washed = augmented_cost-before
        # Keep the old multiplication order: -(J-z) * ((2/d)*trig(phi)).
        output = (-washed*((2/self.arm_length_m)*math.cos(demodulation_phase_rad)),
                  -washed*((2/self.arm_length_m)*math.sin(demodulation_phase_rad)))
        derivative = self.omega*washed
        after = before + dt*derivative
        if not all(math.isfinite(x) for x in (*output, derivative, after)):
            raise ValueError('invalid GESC numerics')
        self.state, self.previous_source_ns = after, source_stamp_ns
        return Demodulation(source_stamp_ns, output, before, derivative, after, dt)
