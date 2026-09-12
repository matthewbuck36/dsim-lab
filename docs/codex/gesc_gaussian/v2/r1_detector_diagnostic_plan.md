# R1 retained B detector diagnostic

Status: ADOPTED, 2026-09-10 UTC, under
[the method/development amendment](method_development_20260910.md).
This is a new development measurement, not a retry or reclassification of M4v5,
V9, or sealed qualification. No runtime source changes are part of this job.

## Hypotheses and decisions fixed before computation

H1: the two-block score can reject confined circling because its response depends
on the ratio between orbital period and block duration. H2: shortening the
history alone can introduce detections on translating circles. Report both
without choosing a threshold to match the retained B outcome.

For an ideal stationary circle of radius r and period P, consecutive equal blocks
of length L=3W have centroid-distance score

`S = 2*r*P/(pi*L) * sin(pi*L/P)^2`.

The runtime integrates the piecewise-linear source trajectory, so ideal values
are comparison references, not substitutions for recorded or replayed values.
Both configurations use the existing `centroid_two_block_v2` selector,
epsilon .18 m, maximum radius .50 m and maximum source gap .50 s: current W=6 s
and one W=3 s sensitivity comparison. The same existing
`CentroidWindowDetector`/`CentroidConfig` owner computes every replay outcome.
No new detector, modified arithmetic, fitted acceptance threshold, or nomination.

Report each control's first candidate time or absence, all completed supports,
minimum/maximum score and confinement radius, all eligible supports, and explicit
false-positive/false-negative classifications. A configuration that misses any
declared positive or detects any declared negative fails this finite control
set. Passing this set alone cannot qualify research latency or robustness.

## Fixed inputs and population

Read only five completed B exports under external V2 root
`builds/m4_v6_development_diagnostic_v1/B/`:
`pose_v1.jsonl.gz`, `centroid_convergence_diagnostics_v1.jsonl.gz`,
`recording_ready_v1.jsonl.gz`, `algorithm_state_v1.jsonl.gz`,
`clock_v1.jsonl.gz`. Preserve all original files. No bags, C/D reconstruction,
V9/holdout files, model geometry, or field/reference owner are read.

All synthetic traces have dt=.1 s, duration120 s, phase0, start time0 and
identity frame `synthetic`. Their classifications follow their declared motion,
independently of any detector output. Use exactly 28 controls:

- One stationary positive `(0,0)`.
- Ten bounded positives: circles and x-axis oscillations with radius/amplitude
  .25 m and each period P in {12,18,24,36,48} s. Circle is
  `.25*(cos(2*pi*t/P), sin(2*pi*t/P))`; oscillation is its x projection.
- Ten translating-circle negatives: add `(v*t,0)` to each .25 m circle for
  v in {.02,.04} m/s and the same five periods.
- Two straight-drift negatives `(v*t,0)` for v in {.02,.04} m/s.
- Five large-loop negatives: radius1 m circles with those five periods.

Both configurations replay all 28 controls, retaining every row and all support
outcomes. Synthetic labels concern settling only; a stationary constant-field
input is not evidence of source/fill/goal validity. No field model is calculated.

## Recorded timelines and descriptive geometry

Retain every original publication from all five selected streams in one ordered
timeline, including full payloads and nonfinite tags. Preserve bag order and
each stream's row index. Preserve all detector publications separately with
score/radius margins, validity, eligibility, epoch and reset data. Distinct
completed supports are keyed by `(run_id,search_epoch,reset_sequence,
history_start,history_end)`; repeats do not enlarge the numerical denominator.
Preserve each nonempty reset reason and reset-generation transition.

Odometry uses `message.header.stamp`; the export's generic source timestamp is
unavailable. `t_motion_sec` is recorder-relative and cannot substitute for
simulation time. Readiness is the retained bag-order interval; associate its
start/end with the latest recorded `/clock` at those boundaries. Source-time
geometry uses readiness poses and rejects invalid, conflicting duplicate,
regressing or source-gap samples rather than silently filling gaps.

Use all pose data in fixed consecutive 36 s and 72 s bins from the readiness
clock origin. Retain partial bins as partial; never select only visually good
loops. Interpolate a complete bin's exact boundaries only from available
bracketing samples. Descriptive fits have no effect on detector replay or labels:

1. Algebraic circle least squares solves
   `x*x+y*y = 2*cx*x + 2*cy*y + k`, with trapezoidal time weights. Report center,
   radius, radial RMS residual, rank and condition. Unwrap measured bearing
   about this fitted center and regress bearing against source time; report
   accumulated turns and period where the slope is nonzero.
2. Independently report the best translation-plus-harmonic fit
   `p(t)=c+v*(t-tmid)+a*cos(2*pi*(t-tmid)/P)+b*sin(2*pi*(t-tmid)/P)`.
   Scan only the fixed period grid6..72 s in .25 s increments. For each P,
   solve weighted linear least squares for both coordinates; choose the lowest
   positional squared error, ties using the smaller period. Report P, center c,
   drift v and its magnitude, RMS residual, the singular values of `[a b]`,
   the axis ratio, and the complete number of represented cycles.
   This is a descriptive affine-ellipse model; call it circle-like only when
   its smaller/larger axis ratio>=.5, positional RMS<=.05 m, larger axis>=.02 m
   and represented cycles>=1.5. Poor/partial fits remain visible and cannot
   supply an established orbital period or proof of settled behavior.

The model describes the measured trajectory and can absorb unmodelled motion.
Its drift is not a calibrated hypothesis test. Never remove fitted drift and
then label the remainder settled. In particular, B has no independent physical
basin-entry label here, so empirical detector latency is unavailable.

## Exclusive job, budget and evidence

New job root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/detector_b_v1/`.
Save this plan, helper, exact command and their hashes before execution. Admit
exactly one attempt with exclusive output creation. Use one command bounded by
`timeout --signal=INT --kill-after=2s 118s`; an internal110 s work timer reserves
exit/hash time inside the120 s total limit. Preserve failures and partial output;
no automatic retry. Hash only the five input exports, this plan, helper and the
two imported detector source files before/after. Other agents are making
nonoverlapping source changes; no whole-tree stability claim is appropriate.

One independent analytic check inside this same job verifies stationary and
straight-drift arithmetic plus an ideal sinusoid interpolation-error bound.
This is measurement validation, not an unrelated source-test campaign.
Save a receipt with exact command, versions, scope, timing, hashes, all output
references and outcome. Write the results in
`validation/r1_detector_diagnostic.md`; root owns status/handoff/checkpoint.

The next decision uses measured B shape/period and positive-negative separation:
consider a method with explicit center translation or multiscale recurrence if
the fixed two-block settings fail. No runtime method, new simulation, or full
comparison is released by this diagnostic alone.
