# M1 independent replay labels and frozen calibration contract

Version: m1-labels-v1. Written before any V2 detector replay/calibration output.
Scope: the eight development/diagnostic inputs frozen in baseline_inventory.json;
the thirteen retrospective holdout bags remain excluded from calibration.

## Evidence boundary and time qualification

Spatial truths use only recorded pose, source/sensor data and evaluator geometry.
The label pass reads pose, source_cost, raw_cost_legacy, encoder,
sensor_transform, clock and timekeeper; the reader also retains readiness for
later eligibility masking. No convergence, fill or supervisor-state output is
read to choose a spatial label. Readiness and SEARCH states are applied only
after labels are frozen, as runtime eligibility/censor masks.

Require simulation timekeeper mode, one finite constant experiment start,
finite nondecreasing timestamps (duplicates reported, never extra time), and
nonempty stable pose frames within each segment. Source timestamps become
absolute simulation seconds by adding timekeeper start; odometry uses its ROS
header. Qualify full streams, record regressions, gaps and invalid fields.
Maximum supported source/pose gap is 0.50 s; nearest source/encoder/transform
alignment tolerance is 0.05 s. Unqualified intervals are unknown, not negatives.

## Prospective evaluator geometry

Reuse the existing aggregate_field_truth model and sensor geometry binding.
Require recorded cost/filter/controller JSON hashes and geometry hashes to agree
with current files, or fail qualification until the recorded versions are
reconstructed. Do not reuse old approximate optimizer centers as certified truth.

For each declared source, minimize full stationary-cycle mean raw cost over a
square extending 0.75 m in x/y around that source, clipped to scenario bounds.
Use 72 evenly spaced sensor world orientations, with nine optimizer starts
on offsets {-0.25, 0, 0.25} m in each axis. Bounded L-BFGS-B uses 200 iterations,
ftol 1e-12, gtol 1e-7. Require at least two successful starts agreeing within
0.05 m of the best result. Require the best point at least 0.05 m inside the
search square, and 72/144-orientation mean agreement within 0.01 raw-cost unit.

Independently verify a surrounding ring at radius 0.50 m, 36 spatial bearings,
and 72 sensor orientations per point. Every ring point must be inside the
scenario bounds and at least 0.025 raw-cost unit above the best cycle mean.
Store all optimizer receipts, quadrature differences, ring minimum and model/
geometry hashes. A failed/ambiguous qualification produces no positive basin
labels for that source; the old experiment outcome is untouched.

The qualified basin-residence region is the 0.50 m disk about that independently
derived minimum. This labels sustained residence in a certified modeled basin;
it does not prove a spatial optimum or distinguish every possible confined
motion. Synthetic positional-settling labels remain a separate category.

## Frozen input-only intervals

- Positive basin residence: a continuously qualified pose/source segment stays
  inside one qualified basin disk for at least 12 s (four nominal sensor turns).
  The onset is its first in-disk sample, not the twelfth second or an old flag.
- Common calibration positives require at least 54 s of eligible uninterrupted
  support (the largest fixed six-window horizon). Shorter genuine residence
  intervals are explicitly right-censored for the common grid comparison.
  Report their lengths and any candidate outputs without treating them as misses
  or silently giving long-window configurations a smaller denominator.
- Before first label/calibration output, opportunity clarification: at most one
  required positive per observed SEARCH epoch. Use its earliest genuine labeled
  residence opportunity. If that first opportunity is shorter than 54 s or is
  interrupted by unavailable runtime eligibility, right-censor the whole epoch
  for positive success; later residence is counterfactual after possible earlier
  intervention and cannot replace the first opportunity. All later events and
  negative/unknown outcomes remain reportable. This changes no spatial truth.
- Negative directed progress: a six-second observed subtrajectory remains
  outside every certified basin disk, moves at least 0.12 m net, and has net/
  path-length ratio >=0.80. Union overlapping qualified subtrajectories. This
  labels independently observable directed travel at >=0.02 m/s, not all
  possible progress. Other intervals remain unknown.
- Report every detector event as positive, negative or unknown. Events outside
  declared labels cannot be called true positives. Do not alter labels after
  observing a detector result.

## Synthetic and calibration population

Use 90-second deterministic traces, source periods 3/4.5/6 s, initial phases
0 and 0.7 rad, sample steps 0.05 and 0.10 s. Positives are fixed-center circles
and fore/aft oscillations of radius/amplitude 0.15 m, plus stationary positions.
Negatives are straight drift at 0.02/0.05 m/s, radius-0.15 m circles translating
at those speeds, and fixed-center loops of radius 1.0/1.5 m. Include input-only
changing sample-rate variants. Gaps/rollback/frame/duplicate/epoch lifecycle
semantics are qualified in focused tests, rather than inventing spatial truth
for invalid intervals. Stationary/flat-field traces test candidate semantics;
they never constitute accepted fill/goal evidence.

The immutable grid is W={3,6,9} s, epsilon={0.03,0.06,0.12,0.24} m,
R={0.25,0.50,0.75} m. Require every declared uncensored positive detection and
zero detections on declared negative intervals. Replay the shared pure detector
core with one latch per observed SEARCH epoch; do not reset at label boundaries.
Selection minimizes median positive detection delay, then R, epsilon, W.
Report synthetic and retained counts separately, including censored/unknown
counts and common-support limitations. If no setting qualifies, preserve a
failed calibration version without modifying this grid or the label contract.

## Durable outputs

Before importing/evaluating the detector, write an exclusive-create label manifest
with input IDs/hashes, this contract hash, label-owner source hash, geometry
receipts, qualified input traces and frozen intervals. Large traces and run
receipts belong below /home/mattb/Experiments/GESC-Gaussian/v2/replay/ outside Git.
Calibration records the frozen label hash and detector source hash. Small m1_*
reports/manifests in this directory link to the exact retained artifacts.
The historical analyzer convergence_time keeps its existing goal-event meaning;
new replay metrics explicitly name detector event/detection delay and label type.

## Recorded eligibility timing limitation

The offline mask preserves recorded state receipt order and invalid-state
history, rearming only on a valid non-SEARCH to SEARCH transition or a genuinely
new run. False/missing/stale readiness or state invalidates support without
rearming. State source and recorded receipt freshness use 0.50 s. Causal recorded
clock comparison allows the same 0.05 s alignment tolerance for cross-topic
receipt skew; publication-minus-source skew is retained and qualified at 0..50 ms.
Readiness receipt freshness uses bag receipt time as a documented proxy. Bags do
not preserve the node's wall-monotonic callback clock, so pauses/variable real-time
factor prevent an exact reconstruction of that runtime freshness condition.
The replay is source-qualified retrospective evidence, not exact execution parity.
