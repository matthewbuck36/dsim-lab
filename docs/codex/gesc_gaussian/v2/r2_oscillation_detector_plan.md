# R2 oscillation component prototype

ADOPTED offline development, 2026-09-10. Circle geometry is intentionally not
applied to a nearly collinear oscillation. This separate component will only be
combined with a circle/static method after each passes its declared negatives.
No runtime mode or experimental result is changed by this prototype.

Fit the timestamped two-dimensional trajectory with
`p(t)=c+v*(t-tmid)+a*cos(2*pi*(t-tmid)/P)+b*sin(2*pi*(t-tmid)/P)` by
trapezoidally weighted least squares. Scan the fixed P grid6..96s at.5s spacing,
retaining only P<=support/.75. Use36s and54s causal supports at6s endpoints.
Choose minimum residual (smaller P tie), retaining the explicit vector drift.
Time column is normalized by support for numerical conditioning; convert fitted
displacement back to m/s. All samples remain available; uniform .2s evaluation
interpolation must be bracketed and original source gaps <=.5s.

An oscillation proposal needs actual radius about its time-weighted mean<=.5m,
principal-axis perpendicular RMS<=.02m and axis variance ratio<=.1, harmonic
major-axis amplitude>=.05m, positional fit RMS<=.02m, design condition<=50,
and fitted drift norm<=.006m/s. Require three consecutive passing6s endpoints
for the same support width. No detrended confinement replaces actual confinement.
These are finite-development choices, not formal uncertainty bounds.

Use the28 fixed R1 controls unchanged, plus64 independent prescribed oscillatory
controls: periods12/24/48/72s; phases0/.73; independent position-noise sigma0/.005m
with fixed seed26091011; and no drift, .02m/s parallel drift, .02m/s perpendicular
drift, or .04m/s parallel drift. Amplitude .25m along direction .7rad; all
trajectories120s at.1s cadence. Any drifting/large-loop/straight negative
trigger rejects nomination. Circle/static positives are outside this component's
scope and reported separately, not called failures of an oscillation detector.

One120s job in exclusive external
`development/20260910/oscillation_detector_v1/` retains exact control identities,
all support scores/reasons and outcomes, source/helper/plan hashes and elapsed
time. No bag/ROS/field model/Gazebo or production source changes. If qualified
on this finite set, implement through the existing convergence-detector owner
alongside the separately validated circle/static component, then perform fresh
development validation. Passing these controls alone does not qualify V2.

## V2 pre-integration representation correction

After v1's fixed-control success, inspection found the .2s fit representation
also governed geometry guards. V2 keeps the harmonic fit unchanged but computes
time-weighted center/covariance and maximum confinement from every original
support vertex plus exact interpolated boundaries. Reject unsupported source
gaps/regressions. This prevents a short off-grid excursion from disappearing
from confinement. V1 remains retained with its declared representation limit.

One new120s job in `oscillation_detector_v2/` evaluates all92 unchanged controls
plus two prescribed amplitude2m spikes on alternating off-grid .1s source
samples in an otherwise .25m/P24 oscillation (directions parallel/perpendicular),
and two irregular-cadence positive/negative fixtures with .07/.13s spacing and
the same P24 oscillation, with drift0/.02m/s. All spikes must block any support
that contains them; complete trace acceptance still respects actual support.
The fixture checks each spiked support before its endpoint, not only whether a
later clean support eventually becomes eligible. No threshold change is adopted.
