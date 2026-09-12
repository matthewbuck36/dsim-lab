# R2 centered collection v2: separate approach from evidence time

ADOPTED, simulation-development only, 2026-09-10. V1 remains failed as recorded
in [validation](validation/r2_centered_verification.md). The user authorizes
moving evidence-collection redesign; no historical12s result is changed.

V1 measured an actual geometric reachability/evidence timing limitation even
with an optimistic signal: only3/12 required starts produced three acceptable
cycles in12s. The old orbit does not systematically visit the fixed center;
the proposed tracked target does, but the initial approach consumes observation
time and contaminates early spatial profiles. This amendment tests a two-stage
continuous collection contract, not additional waiting on the old orbit.

Retain the same target, controller, bounds, raw guards,18 initial conditions,
dt.025s and artificial signal as v1. Give the approach at most8s to first enter
.08m of the frozen center. Once that source-time condition is observed, freeze
one12s evidence deadline; never restart it on later entry/exit. Absolute
candidate duration is at most20s. Motion remains the same bounded moving-target
tracking throughout; no stopped-sweep fallback. Record the first approach time,
deadline, first raw-evidence ready time and every guard. A candidate unable to
approach or collect within its fixed deadline fails, with no timeout extension.

One new90s job in exclusive external
`development/20260910/centered_verification_v2/` runs the full20s ideal trajectory
for diagnostic visibility. Acceptance uses the fixed per-case approach/evidence
deadline, ignoring later success. All12 required .25/.35m cases must approach
within8s and collect within12s thereafter, with no joint commanded-zero interval
>=.5s. Hard .50m results remain separately reported. Do not tune during the job.

If this passes, it supports a selectable runtime experiment with equivalent
finite stage admission, freshness/candidate binding, operating-bound command
sweep checks, sole existing controller ownership and legacy behavior. It does
not establish real signal informativeness/ranking or justify a full matrix.
