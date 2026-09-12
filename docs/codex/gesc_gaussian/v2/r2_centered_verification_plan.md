# R2 continuous centered verification feasibility

ADOPTED for bounded offline development, 2026-09-10. Authority:
[method/development amendment](method_development_20260910.md). R1 establishes
specific fixed-center support failures in earlier C/D reconstructions while
the moving estimator passes its first measured development-C direction targets.
Keep that estimator. This job tests a candidate active evidence-collection
motion policy before any runtime integration or Gazebo dispatch.

## Hypothesis and model

Continuing the original orbit need not bring short sensor cycles near its
long-horizon center. Instead, during moving verification, continuously track a
small moving target about the frozen candidate center. Use only algorithm pose,
candidate center and clock. No source coordinates, cost model or evaluator
direction enter the motion proposal. Safety and final-goal holding remain
separate. The candidate center, evidence guards and12-second deadline are held.

Let `z(t)=c+.03*[cos(.3t),sin(.3t)]` metres and
`q_world=z(t)-p(t)+z_dot(t)/.5`. Rotate q into the current body frame, then pass
it through the existing `Directional_Controller` with the actual selected
`.5/5` gains and `.1m/s/.5rad/s` limits. This is a prospective bounded tracking
proposal, not a new claim that q estimates the source gradient. Negative forward
velocity and natural zero crossings remain possible; there is no stopped
sensor-acquisition state. The rotating sensor continues its observation.

Integrate ideal unicycle kinematics at dt=.025s for exactly12s. This is a
kinematic development model, not Gazebo or an empirical success. Feed the
existing MovingRawEvidence owner generated synchronized observations at that
cadence, using sensor-world phase `2*pi*t/3+yaw`, and an optimistic repeatable
raw profile `-2+.5*cos(phase)`. That artificial profile isolates geometric
collectability; it cannot establish real signal-repeatability or ranking.

Use18 fixed initial conditions: radius .25,.35,.50m from center, position
bearing0 or pi/2, heading0,pi/2 or pi. No pretrigger evidence is supplied.
Candidate radius .75m, centroid/sector tolerance .15m,3 complete sensor cycles,
unchanged MAD/information checks, and decision strictly before12s. Use the
controller configuration JSON directly and retain it as an input receipt.
Every case is retained; do not tune during the job. Report first evidence-ready
time or its absence, all rejection reasons/margins, center distance and speed
history, maximum speed, and intervals with both commanded velocities near zero.

## Finite decision and ownership

One90-second job under new exclusive external directory
`development/20260910/centered_verification_v1/`, preserving helper/config/core
source hashes, exact command and complete trajectories/results. No ROS node,
bag, field model, hardware or historical output is used. Existing controller
and evidence owners perform computation; the helper only orchestrates ideal
kinematics and generated observations. No production source changes yet.

Proceed to runtime design only if all .25/.35m cases collect acceptable evidence
before the existing deadline, without a sustained commanded stop. Report .50m
cases as deliberately harder reachability probes. Failure calls for a changed
motion/evidence model or explicit scoped limitation, not an automatic timeout
increase. Any promising runtime integration needs a selectable mode, the
existing controller as sole cmd_vel publisher, fresh candidate/pose binding,
existing operating-bound sweep guards, cancellation/legacy tests and a finite
visible experiment. Real field repeatability/ranking remains an empirical gate.
