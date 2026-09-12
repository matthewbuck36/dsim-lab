# Frozen recurrent component confirmation: 96 new procedural histories

ADOPTED 2026-09-10 before input generation or detector execution. Root approved
this finite independent component check after the final combined runtime replay
and visible02 development analysis. It does not release the16-run comparison.
No production edits, bag/model reads, Gazebo or prior control replay. The D3
single-C profile must be terminal before dispatch; it has now released CPU and
source holds. Root owns the next visible run and receives this job's terminal
notification first.

## Frozen method and interpretation

Run the existing production `RecurrentGeometryDetector(RecurrentConfig())` on
all original source points, `start_epoch(case_id,0)`, frame `odom`, through120s.
Reuse the actual per-case loop from `combined_runtime_replay_v2/run.py`, pinned
and extracted before its optional historical-D work. No branch replacement,
resampling at the caller, early stop after a candidate or threshold change.
The fixed method is static30s/radius.04/drift.005; circle30/36s and oscillation
36/54s with their existing geometry/drift.006 guards and three consecutive6s
endpoints. Exact equations remain in the runtime plan and production source.

Ground-truth labels follow the prospectively defined generating model, not the
detector's fit. Positive classes have zero translating center: static, circles
with r<=.35m/P<=79s, and line oscillations with A<=.31m/P<=67.9s. Negative
translations are >=.021m/s; large loops have r>=1.1m; recurrent source spikes
violate confinement in every complete support. Observed noisy support geometry
is not used to relabel a miss. Gaussian noise is unbounded mathematically; the
retained finite samples, noise scales and any effect on acceptance are reported.

The .26/.35 circle radii and especially .31 oscillation amplitude expand the
earlier finite coverage. The prior static-cancellation endpoint argument assumed
oscillation amplitude A<=.25m; it does NOT establish rejection for A=.31m here.
Those larger translated oscillations are deliberately negative empirical tests
of the final OR behavior. Any failure closes this fixed version unchanged.

## Exact population, ordered identity and samples

Cases have new IDs `r4_fixed96_000` through `r4_fixed96_095`; no historical ID is
reused or deduplicated. For global case index i:

- phase phi_i=(.173+.371*i) modulo2pi;
- direction theta_i=(.239+.613*i) modulo2pi;
- independent NumPy default_rng seed=202609100400+i;
- center c=(1.2,-.7)m;
- uniform integer-ns sampling every100ms unless i modulo3 equals2;
- that irregular subset uses repeating71/113/127/97ms intervals, starting0,
  truncating before120s and appending exactly120s. Maximum source gap127ms.

At each source time, add independent two-axis N(0,sigma^2) noise from the fixed
case generator. Unless specified below sigma=.002m. The sample generator is
saved and pinned; no random draw depends on detector output.

Circle: p(t)=c+r[cos(2pi*t/P+phi),sin(...)]+v*t.
Oscillation: p(t)=c+A*sin(2pi*t/P+phi)*[cos(theta),sin(theta)]+v*t.
Straight/static: p(t)=c+v*t. Translation v=s*[cos(alpha),sin(alpha)].
Products below use first-listed quantity as outer loop and second as inner.

| Indices | Count | Label/class | Fixed model |
| --- | ---: | --- | --- |
| 0-15 |16|positive/circle|r=.09,.17,.26,.35 x P17,29,53,79; v=0|
|16-31|16|positive/oscillation|A=.08,.14,.23,.31 x P19.3,35.7,51.1,67.9; v=0|
|32-35|4|positive/static|v=0; sigma=0,.003,.006,.009 respectively|
|36-51|16|negative/translating circle|same circle product; local j=i-36, s=.023 if j even else.037, alpha=theta_i|
|52-67|16|negative/translating oscillation|same oscillation product; local j=i-52, s=.023 if j even else.037, alpha=theta_i if j even else theta_i+pi/8|
|68-71|4|negative/straight drift|s=.021,.029,.043,.057 respectively; alpha=theta_i; sigma=0|
|72-79|8|negative/large loop|r=1.1,1.3 x P23,47,73,101; v=0|
|80-83|4|negative/source spikes|first2: r=.26,P53 circle; last2: A=.23,P51.1 oscillation; v=0; add(2,0)m to first original sample at/after each4.3+9.7*k seconds<=120|
|84-87|4|gray/slow translating circle|r=.26,P53; s=.003,.005,.008,.012; alpha=theta_i|
|88-91|4|gray/slow translating oscillation|A=.23,P51.1; same4 speeds; alpha=theta_i|
|92|1|withheld/long-period circle|r=.26,P107; v=0|
|93|1|withheld/long-period oscillation|A=.23,P91; v=0|
|94|1|withheld/small oscillation|A=.04,P35.7; v=0|
|95|1|gray/slow straight drift|s=.005; alpha=theta_i|

Expected totals:96 histories,36 positives,48 negatives,12 gray/withheld;
32 irregular histories. All generated numeric records and parameters are saved
before dispatch in `control_samples.jsonl` and `control_contract.json`, each
with exact sample hashes. Earlier family populations are not pooled into the
new denominators. The seed generator and off-grid values give new identities;
this designed finite grid is not an IID estimate of arbitrary-world error rate.

## Decision, budget and retained evidence

Exclusive directory:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/frozen_component_confirmation_v1/`.
Preparation is source/input generation only. Save the exact invocation,
selected core/dependency/contract, original replay owner, plan and helper hashes
in `prepared.json` before any detector evaluation. Check those hashes at both
job entry and completion. No production file may change during execution.

One job:118s SIGINT deadline plus2s kill-after, internal110s limit. No unchanged
rerun. Retain all branch supports, reset/rejection reasons, source counts,
first-candidate source/model endpoint times, first branch, per-class latency
min/median/p90/max, eligible-branch counts, positives missed, negatives accepted,
gray outcomes and repeated-confirmation violations. All original points remain
in the frozen inputs, including irregular samples and source spikes.

Finite component PASS requires all36 positives detected by120s, zero of48
negatives confirmed and at most one confirmation in every history. Report
first-branch mismatches separately: all branches detect positional trapping,
so matching the generating motion class is descriptive and not a retroactive
acceptance gate. Gray/withheld cases remain outside pass/fail regardless of
outcome. Execution/integrity completeness and scientific PASS/FAIL are distinct.
Retain useful partial results and the error if interrupted. No threshold,
population, label or deadline changes after inspecting outcomes.

Before preparation: `validate_phase_context.sh v2 implement` PASS under28s.
Root receives numerical results and terminal/source-release notice before its
next simulation. Save exact command, pins, metrics and limits in
`validation/r4_frozen_component_confirmation.md`; status/handoff remain root-owned.
