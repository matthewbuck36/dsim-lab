# R2 v3: stability of independently fitted arc centers

ADOPTED 2026-09-10 UTC after the failed geometricv2 sensitivity result was saved.
This changes the model, not the prior rival residual thresholds or outcomes.
The two previous geometric prototypes and R1 remain immutable. Offline only;
no production detector, simulation, bag, field model or holdout changes.

## Fixed hypothesis and candidate rule

Time means of partial arcs move even around a stable circle center. Independently
estimated geometric centers of successive arcs may remain stable and separate
moving-center motion without excluding every partial-trajectory alternative.
This is a testable model-specific rule, not a proof against arbitrary paths.

At fixed6s causal endpoints evaluate two supports: two disjoint15s arcs (30s
total) and two disjoint18s arcs (36s total). Within each arc use all source
samples, exact interpolated boundaries only when bracketed, and trapezoidal
time weights. Reuse the R1/v1 algebraic circle fit: after translating to the
weighted origin, solve `x*x+y*y=2*cx*x+2*cy*y+k`, radius
`sqrt(k+cx*cx+cy*cy)`. No fitted period or center-velocity rival is calculated.

Both arcs must have rank3, finite parameters, radius in [.03,.50]m and radial
RMS<=.02m. Genuine angular coverage is **absolute net unwrapped bearing change**
about that arc's fitted center>=pi/3; cumulative noisy angular travel does not
substitute for net coverage. Save span, net and total variation independently.
Record matrix conditioning without introducing a fitted condition-number gate.

For each same-width arc pair require:

- center drift `||c_new-c_old|| / L <= .006 m/s`, where L is the15/18s
  separation between the two arc midpoint times;
- absolute fitted radius difference<=.08m;
- maximum distance of every represented full-support position from the
  full-support time-weighted measured mean<=.50m.

Require **three consecutive passing6s endpoints of the same support width**
before candidate admission (12s endpoint persistence). A failed or invalid
evaluation resets only that width's consecutive-pass count; do not pool
different widths or carry a stale fit through a failure. No candidate before
42s for30s support or48s for36s support. Keep all later evaluations after the
first candidate. The existing prototype nearstatic rule remains12s measured
radius<=.03m and weighted linear drift<=.005m/s, with no added persistence.
Oscillations remain unsupported; no two-block fallback.

Reject nonfinite/gapped/regressing/conflicting or unbracketed support exactly
as the prior prototypes. Centers are model estimates, not ground-truth source
coordinates. No source/fill/goal authorization follows from motion detection.

## Frozen99 controls and development-only inputs

Use the exact89 control contracts/samples from geometricv2, preserving all
prior phases, noise and labels. Add only the following10 traces, fixed before
execution; duration120s, dt.1s, no measurement noise:

1. Six fixed-center variable-speed circles, radius.25m: P in {36,60,72}s,
   phase phi in {0,.73}, with
   `theta(t)=2*pi*t/P+phi+.4*sin(2*pi*t/P+phi)`.
   Thus angular speed stays positive between .6 and1.4 times nominal; these
   are prescribed circle positives rather than constant-rate harmonic fits.
2. Four translating-ellipse negatives:
   `p(t)=v*t*(cos(h),sin(h)) + (.35*cos(theta),.18*sin(theta))`,
   `theta=2*pi*t/60+.37`, v in {.02,.04}m/s,
   h in {pi/8,3*pi/8}. These independent shape controls are not derived from
   whichever prior negative happened to fail.

Total99:32 circle/static positives,58 negatives,8 unsupported oscillations and
one gray .005m/s drift. Preserve exact V5 B R1 readiness poses and V9 B v2
readiness poses/clock bounds. Both are exposed DEVELOPMENT inputs, not holdout
evidence; no independent entry label or empirical intervention latency exists.

## Single120s job and decision

Exclusive directory:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/arc_center_detector_v1/`.
Save plan/helper/argv/hashes before the sole command, with118s SIGINT timeout,
2s kill-after and110s internal work limit. No unchanged numerical retry.
Reuse only pure support/circle/weighted-solve functions by AST from the saved
helpers; do not run old top-level measurements. No production edits.

Retain all99 contracts, exact new samples, each arc fit and pair-score margin,
counter/reset reason, every static/support endpoint, both B timelines, first
candidates, candidate rates, false-positive/miss/unsupported/gray summaries,
selected source/input hashes and exact timing/failure receipt. Invalid/missing
and failed supports stay in the complete denominator. Hash only selected
immutable artifacts/helpers plus this plan/helper, permitting unrelated work.

No runtime nomination if any declared negative triggers or circle/static
positive is missed. Useful candidates on both retained B inputs support only
development feasibility; source-identifying verification, a separate principled
oscillation method, runtime cost, independent validation and integrated closed-
loop behavior remain unfinished even if this finite prototype passes.
