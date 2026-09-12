# M2 synchronized rolling GESC — implementation contract, 2026-09-09 UTC

Status: ACTIVE. This elaborates the approved V2 plan before M2 source edits.
The later `m2_source_clock_correction.md` supersedes publication-key semantics
and source<=receipt assumptions for the selected schema2 runner. Schema1
fixtures and pre-correction evidence retain their original meaning.
M1/M1a outcomes remain closed with no selected detector setting. This milestone
is independent of detector calibration; see `m1_to_m2_sequencing.md`.

## Ownership and compatibility

Extend the existing source-cost publisher, disturbance relay, modified-cost
composer, filter, supervisor identity, runner, recorder and analyzer. Add pure
helpers and typed messages within their existing packages, never new runtime
nodes. `continuous_search_mode=stationary_v1` remains default; only explicit
`rolling_gesc_v2` with the robust profile and simulation time selects this path.
The filter CLI uses `--continuous-search-mode`, `--v2-run-id` and
`--v2-stream-config-json`; ROS parameters use corresponding underscore names.
The existing controller gates remain until M3; M2 cannot itself claim moving
verification or stationary-acquisition removal.

## Identity, time and source admission

The runner supplies its existing nonempty run ID to all opted-in owners and
the recorder. Direct opted-in startup requires an explicit run ID. A shared
pure `v2_stream.py` validates a canonical static JSON descriptor of resolved
algorithm raw/source/augmented/objective/provenance/pose/encoder/timekeeper
topics, planar frame, selected channel and sensor-geometry configuration
digests. Each owner binds that descriptor to the first valid simulation
Timekeeper origin and independently computes the same SHA256 contract ID.
The origin is unavailable before runtime, so no precomputed false origin is
used. Provenance carries the binding; no descriptor acknowledgement cycle is
introduced. The recorder keeps its existing wall clock.

Absolute integer nanoseconds are `origin_ns + round(relative_seconds*1e9)`.
Preserve the original finite legacy floating timestamp as the exact join key;
rounding is not used to merge distinct source records. The source publisher
records the actual evaluated transform timestamp/geometry separately from the
unchanged raw-cost publication timestamp. This transform still uses the
sensor-pose publisher's cached pose; it is not claimed as simultaneous odometry
acquisition. The existing delay owner delays provenance with the source stream.

The filter admits a sample only after matching selected raw cost, augmented
cost, atomic objective metadata and source provenance have actually arrived.
Metadata cannot bypass selected raw delay. The opted-in modified-cost owner
joins raw evidence/provenance and evaluates corrections at that exact observed
sensor geometry, removing the inherited latest-transform mismatch in this mode.
It stamps weights, active-fill digest, affine revision/configuration, effective
cost-composition time and monotonically increasing objective revision together
with the exact augmented values. Continuous affine decay is part of the same
objective law; fill/weight/affine-law changes and effective affine expiry change
the revision. State publication sequence alone does not change the objective.

Preserve the actual integer publication stamp. Its consistency with the legacy
floating timestamp allows only the numerical representation bound
`max(1 ns, ceil((ulp(publication_ns*1e-9) + ulp(origin_ns*1e-9) +
ulp(legacy_seconds))*1e9) + 1 ns)`. Exact floating join keys remain unchanged;
this is not approximate cost matching or the 50 ms synchronization tolerance.

Pose and encoder must bracket model-input time without extrapolation. Each
bracket endpoint must be within 50 ms, including exact coincident endpoints.
Interpolate xy linearly and yaw/phase by shortest arc; exact pi ambiguity is
invalid. Preserve all source/publication/bracket/receipt stamps. Future,
nonfinite, incompatible-frame/identity samples fail explicitly. Identical
duplicates are idempotent; conflicting duplicates poison that key. Process
pending costs in source order, including head-of-line waiting until expiry,
never integrate a late sample backward. Context change/rollback invalidates
pending synchronization and rolling confidence. Buffers are bounded: 2 s
source span, 4096 pose/encoder records, 1024 pending costs. Source and receipt
freshness limit is 0.5 s; timer-based expiry needs no new incoming sample.
Observations retain both the latest receipt (join-ready time) and oldest
contributing receipt; output freshness checks both, so late metadata cannot
refresh an old pose or encoder contribution.

The selected geometry has zero fixed mount yaw, zero joint xy offset, a
0.355 m joint height and sensor translation (0.18, 0, 0.015) m; reject
incompatible geometry for this implementation.
The source transform provides actual world orientation but no held joint-phase
wire field. Therefore demodulation uses the effective body angle
`wrap(observed_world_phase - synchronized_base_yaw)`. Label that relative angle
reconstructed, retain the separately interpolated encoder phase and discrepancy,
and never call it an observed held joint measurement. After world rotation this
uses the actual evaluated angular basis. No extra sensor-pose node or invented
acquisition stamp is introduced. Distinct source times at equal world phase may
count actual sector observations; duplicate source times never increase counts.

## Filter and revolution mathematics

Keep the selected custom filter's negative demodulation, gains and washout
dynamics. Evaluate once per synchronized model-input source time, output before
the inherited forward-Euler state update. This explicitly replaces publication
time as the opted-in integration clock. Initialize a fresh filter state on
context discontinuity, use zero dt for its first source observation, and bound
new-path numerical updates; do not change legacy integration behavior. Objective
revision clears rolling confidence, without requiring a washout reset or a
same-objective SEARCH/VERIFY/DESIGN reset.

Rotate instantaneous body output by synchronized base yaw. Use actual observed
sensor WORLD phase, including base/mount motion, for phase coverage. The first
nonzero shortest phase increment selects direction; exact-pi ambiguity,
reversal beyond 1e-12 rad or a source gap over 0.5 s clears cycle confidence.
Zero phase progress adds time without completing a revolution. Maximum cycle
duration is 30 s and maximum retained rolling samples is 20000; exceeding a
bound is an explicit incomplete-coverage fallback.

The rolling mean is source-time trapezoidal integration of world vectors over
the latest fully represented 2pi of monotonic phase, divided by its duration.
Interpolate phase-crossing time/vector at the start, never extrapolate. The
first arrival at a boundary phase defines its crossing during a plateau.
Separately summarize nonoverlapping complete cycles anchored at the first
accepted phase. Shared interpolated endpoints support quadrature but do not
manufacture observations. Each actual observation belongs to one half-open
cycle and one of twelve absolute wrapped-world-phase sectors; every sector
needs two actual observations. The rolling window has the same coverage gate.

Qualification requires three latest complete coverage-valid cycle summaries.
Let their vectors be m1,m2,m3 and their mean m. Cycle variability is
`sqrt(sum(norm(mi-m)^2)/3)` in filter-output units. Every cycle mean and the
rolling mean must exceed `max(1e-6, 3*variability)` before angular comparisons;
all pairwise cycle angles must be at most 30 degrees. This is a deterministic
confidence rule, not a statistical confidence interval or gradient proof.
For this fixed `2/d` filter with d in metres, filter-output units are cost units
per metre. Matching gradient dimensions does not make the signal a proven
spatial gradient; the source's cost convention remains unchanged.

With valid confidence, blend `.5*instant_world + .5*rolling_mean_world` and
rotate by minus the latest fresh selected-pose yaw for output. Otherwise use
fresh instantaneous world GESC rotated to that same current body frame. A weak
instantaneous vector can remain zero; do not normalize it. Publish detailed
validity/fallback diagnostics independently of recording readiness. Invalid or
stale inputs never receive a fabricated fresh-valid zero filter heartbeat;
existing controller stale-input safety remains effective. The adapter applies
the blend only in SEARCH/VERIFY/DESIGN; escape retains its existing selected
objective/geometric ownership and receives no raw-source attraction blend.
Legacy GescDiagnostics remains the instantaneous filter's own inputs/states/
output; the new direction message explicitly reports the blended output.

## Verification and remaining scientific work

Before runtime qualification, build typed interfaces in the retained isolated
overlay and test source ordering/delay, identity/hash conflicts, time/frame
rollback, bounded expiry, yaw wraps/base turns/CW/CCW/reversals, quadrature and
real observation counts, cycle disagreement/weak signals/objective changes,
current-body output and opt-in/legacy separation. Include real bounded ROS
transport through the existing owners. No physical or Gazebo action is released
by this source contract alone.

The reference is the selected stationary-cycle GESC improvement signal, not a
raw spatial gradient. For signed world rate Omega, washout alpha=1 and sensor
offset d=.18, evaluate first harmonics a,b of the exact stationary angular
objective. With Hc=i*Omega/(alpha+i*Omega)=u+i*v, the continuous reference is
`-[(u*a+v*b),(u*b-v*a)]/d`. Verify the sign numerically. At uniform observed
cadence h also report Hd=(exp(i*Omega*h)-1)/(exp(i*Omega*h)-1+alpha*h), matching
output-before-Euler-update. Nonuniform cadence/variable motion is explicitly a
local stationary counterfactual. The objective includes sensor-position
Gaussian and affine terms when present; raw-only reference cannot qualify an
augmented output. Freeze bounded same-trajectory sampling, informative-vector
denominators and evaluator tolerance in a separate M2 reference protocol before
any new evaluator calculations. Retained recordings without exact provenance
cannot be relabeled as exact M2 source observations.

Record commands, results, skipped evidence and material checkpoints. M2 tests
do not select detector thresholds, satisfy M3 calibrated-neighborhood evidence,
or prove the M4 angular/availability/latency targets.
