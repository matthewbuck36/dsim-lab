# R2 geometric detector v2: asymmetric competing explanations

ADOPTED 2026-09-10 UTC after the completed, failed v1 prototype. Its73 controls,
one false detection and all files remain immutable. This new offline version
changes only alternate-explanation admission/search, adds16 independently
specified negatives and fresh V9 B development poses. No production source or
simulation is changed; no old numerical job is repeated unchanged.

## Hypothesis and fixed method

V1 incorrectly applied stable-candidate angular-span/radius tests to rival
moving-center explanations. A rival can invalidate a stable interpretation
without independently qualifying as a stable candidate. Its45-degree grid also
misses intermediate drift directions. Retain all zero-drift/static thresholds
and support schedules from `r2_geometric_detector_plan.md` unchanged.

For each zero-drift support that passes the fixed stable-candidate geometry,
evaluate the original32 speed/heading grid alternatives (.005 diagnostic;
.01,.02,.04m/s at headings everypi/4). A rival is plausible when the weighted
circle fit has rank3, finite positive radius<=2m and finite radial residual.
Do not impose its own angular span, recurrence, .50m radius, actual-confinement,
or any other stable-candidate acceptance test. Retain these fields diagnostically.
Appreciable speed>=.01m/s vetoes if rival radialRMS
`<=min(.02, zero_drift_RMS+.002)`; .005m/s remains diagnostic-only.

If a grid rival already vetoes, further optimization is unnecessary and is
explicitly skipped with that reason. Otherwise refine the three lowest-radial-
residual finite grid alternatives with speed>=.01 (ties use original grid order).
Use scipy.optimize.least_squares over speed s in [.01,.06]m/s and heading phi
in [-pi,3*pi], initialized at each selected grid pair; default trf method,
ftol=xtol=gtol=1e-8, max_nfev60 per seed. At each trial, v=s*(cos(phi),sin(phi));
compute the same weighted algebraic circle fit of z=p-v*(t-tmid), then return
the vector `sqrt(w_i)*(||z_i-c||-r)` to the optimizer. Invalid/rank-deficient
trial fits return a finite constant residual1m, and their occurrence is counted.
Do not require radius<=2m during optimization; apply that plausibility limit
to each returned rival. No increased residual allowance or candidate threshold.

Keep all original grid rivals in the decision as well as every refined result.
Any plausible accepted result can veto, even when optimizer termination reports
an evaluation limit; inability to find a rival is not a mathematical guarantee.
Record seed, initial/final fit, x/nfev/njev/status/success, actual function-call
count, invalid trials, and final veto. This bounded local search is a development
method with explicit uncertainty, not a global infeasibility certificate.

Reuse pure R1 weighted_lstsq and v1 support/circle arithmetic by loading only
their function ASTs. No prior helper top-level code or old measurement executes.
Nearstatic remains12s measured radius<=.03m and fitted drift<=.005m/s. Circles
remain18/24/30/36s support at6s endpoints. Oscillations remain unsupported, with
no two-block acceptance fallback.

## Frozen89 controls and two development trajectories

Read v1's73 contracts and exact added samples plus R1's original28 samples;
do not regenerate different noise or alter labels. Add16 negatives in this
declared nesting order: speed {.017,.033}m/s, heading {pi/16,5*pi/16},
period {54,66}s, phase {.37, .37+pi/2}. Radius.25m, dt.1s, duration120s,
sigma0; the second phase is an independent phase variant fixed before execution.
Thus the total is89<=100. Preserve scope counts:26 circle/static positives,
54 negatives,8 unsupported oscillations and1 gray .005m/s drift.

Retain V5 B's exact R1 readiness poses/origin/end. Additionally read only fresh
V9 DEVELOPMENT B `pose_v1.jsonl.gz`, `recording_ready_v1.jsonl.gz` and
`clock_v1.jsonl.gz` under `development/20260910/v9_detector_inputs_v1/B/`.
Use the saved exporter schema and source-time/readiness rules from R1: one
closed bag-order readiness interval, latest recorded clock at each boundary,
Odometry header stamps, no extrapolation, no callback reconstruction. Both B
trajectories are declared development evidence; neither is an untouched
holdout or provides an independent settling-entry latency label. No D stream,
bag, model geometry or direction estimator is read or fitted.

## Single180s budget and complete retention

Exclusive output:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/geometric_detector_v2/`.
Use one178s SIGINT timeout plus2s kill-after, internal170s work timer; the larger
allowance is prospective for continuous multistart rival fits and extra inputs.
Save helper/plan/command hashes before dispatch. Preserve partial files/failures;
no unchanged numerical rerun. Hash only selected immutable input/helpers and
this plan/helper, allowing unrelated parallel production changes.

Retain all89 contracts/samples, every static and zero-drift endpoint decision,
all attempted grid/refined alternatives, explicit skipped-optimizer reasons,
both B results, every control classification, ambiguity counts, candidate
availability/timing, all selected-source/input pins and exact command timing.
Require no negative triggers and no circle/static misses before nomination;
do not relabel oscillations or gray drift to alter that result. Source-identifying
verification, detector generalization, runtime cost and integrated behavior
remain separate criteria even if this finite offline set passes.
