# Observed-phase direction diagnostic result — 2026-09-09 UTC

Status: CLOSED COMPLETE_DIAGNOSTIC; qualification NOT_EVALUATED. The single
24-target run completed with exit0 in24.32wall seconds under its300s cap.
All24 original targets produced qualified, informative references. No source,
target, waveform or blend weight changed during the job. Confirmation remains
sealed; no runtime policy, detector setting or M4 pilot is qualified by this
diagnostic.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_observed_phase_direction_diagnostic_v1/`.
The exclusive closure rechecks all556 current source receipts, the complete
historical lineage, both actual recorded discovery bindings and every saved
anchor, and binds70 artifacts. Closure SHA256:
`52c8942e1f311ee4aae7659ee90b14e01c70136f532f2811229ebf98b197af04`.

## What the comparison establishes

The observed phase-time reference makes every preselected anchor evaluable.
The prior constant-rate diagnostic remains closed with its original20
exclusions; these are results of a separately declared reference, not a
reclassification or replacement of those earlier results.

| Same recorded population | Informative targets | Actual median error | Actual p90 error | Actual averaging | Hypothetical50/50 median | Hypothetical50/50 p90 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Residence26090911 |12/12 |57.015676deg |97.643647deg |1/12 |23.012355deg |54.894532deg |
| Approach26090912 |12/12 |53.492357deg |103.902573deg |3/12 |23.533062deg |74.577569deg |
| Pooled |24/24 |55.342800deg |103.692391deg |4/24 (16.67%) |23.012355deg |71.986722deg |

All24 actual vectors and all24 predeclared latent vectors are finite and
nonweak. There are no missing angular outputs in this population. The aligned
instantaneous pooled median is also55.342800deg; equality of the medians does
not imply equality of every actual and instantaneous vector.

The hypothetical50/50 vector improves on the aligned instantaneous estimate at
all24 anchors. It equals actual output at the four anchors already blended;
the other20 compare a prospective mixture with recorded fallback. The same
fixed weight and original first diagnostic's one-cycle mean were used at
every target. No post-result subset, new mean, weight search or gate adjustment
was applied. Source-time and publication/bag identity joins passed before any
field evaluation, including four actual-blend matches within1e-12.

Relative to the original30deg median/60deg p90 reference levels, the latent
median is lower, but pooled p90 remains71.986722deg. Two latent errors exceed
100deg (residence target5 and approach target5). Improvement over an
instantaneous vector is therefore not sufficient evidence of reliable
direction everywhere. The actual averaging availability remains4/24; the
hypothetical vector's24/24 calculability is not actual runtime availability.

These results support investigating whether a better averaging/confidence
policy can improve recorded direction estimates. They do not establish that
it will remove the orbit, speed convergence, reject noise, yield a different
trajectory or satisfy closed-loop acceptance. Translation, washout transients
and local periodic-model limitations remain. No spatial-gradient or causal
controller-performance claim follows from this reference.

## Numerical and provenance evidence

Each cycle retains actual phase-time knots, source cadence, readiness and
sector coverage; the full recorded augmented objective and selected geometry
remain bound. Reference magnitudes range0.032800106–0.320325326cost/metre;
estimated vector errors range5.81e-8–7.12e-7cost/metre. The largest normalized
component error estimate is9.71e-8, below1e-6. Periodic closure residual is at
most1.78e-16seconds. All24 references exceed their fixed informative floors.
These are numerical estimates, not model-error certificates.

There were74,679 objective calls in total,2,794–3,760 per anchor, below the
25,000/anchor cap. No warning, numerical exclusion, timeout or target replacement
occurred. The325-check source boundary and all retained preflight failures are
recorded in `q1_observed_phase_preflight.md` and `q1_observed_phase_numeric.md`.

Exact single invocation from repository root:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 /usr/bin/time -p -o /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_observed_phase_direction_diagnostic_v1/process_time.txt timeout 300s python3 docs/codex/gesc_gaussian/v2/tools/q1_discovery_direction.py evaluate --reference-version observed-phase-v1 > /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_observed_phase_direction_diagnostic_v1/reference_console.log 2>&1
```

Primary receipts:

- `analysis/references.json`: SHA256
  `6c7ca706ed779df45003bccf909890e07e83b5ac1d4f84f9a2c637c7d8f357bf`.
- `reference_console.log`: SHA256
  `297fa5ee983a67613ecd5b1e9f4900b02b1561f2821d0baf2e380dd4a2ffe40e`.
- `process_time.txt`: SHA256
  `0a87a6f9fa31bfb041cc679d0a8bb4a9bada91694b35fc4f98e44ac17b948c6f`.
- Frozen contract: SHA256
  `d9ed31f52c9f088199fdf700076424b730e0248a143f9ace2495c8666527b45e`.
- Dispatch release: SHA256
  `57425c8434d15043a6dd169b707c31c6039489b1975909f8b00c0b6bfc8b23e0`.

Closure command, same sourced environment/domain191:
`timeout 60s python3 /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_observed_phase_direction_diagnostic_v1/close_diagnostic.py`.
It passed once. No new objective calculation occurs in closure.

Next: independently audit saved arithmetic and plot the24 comparisons, then
save a prospective bounded direction-development amendment before considering
additional weights or confidence rules. Reuse these reference receipts without
re-evaluating the field. Original Q1 and both diagnostic versions remain closed;
new runtime evidence and qualification must have their own declared versions.

## Independent saved-result audit and plot

The separate `diagnostics/result_audit_v1/` audit passed in1.4625s under60s.
It verifies all24 saved anchor rows, original target/source/observation/objective
and first-diagnostic/supplement joins, independently recomputes only the saved
vector/angle/quantile arithmetic, and confirms602 files unchanged, including
all556 current sources. The latent vector improves24/24 versus instantaneous;
versus actual output,20 improve and four match. No bags, models, filter replays,
new weights or confidence rules were evaluated.

The exact invocation, scripts and retained initial metadata-shape helper error
are in the adjacent README. The first helper treated checkpoint.files as a
mapping; its original source/log remain. The corrected helper reads its exact
receipt-list mapping. This changed no research result or frozen source.

The24-row `targets.csv`, `paired_errors.png` and PDF show every target and both
runs, with actual/instantaneous versus explicitly hypothetical50/50 vectors.
The30/60deg lines are labeled original reference levels, not diagnostic gates.
Both author and root visually reviewed the PNG; labels and all points are
readable, including the two errors above100deg.

Audit manifest SHA256:
`e111892b1e5e18a534271de806f0168f0af2e4ca4b40ee8c42a2dfb675ae2741`;
result SHA256:
`8b0337ed550641d8475ee7d8b1aeb05ff03094a8f47e1f86818c527b03436bed`;
PNG SHA256:
`ac2beedad59ccc77d614fd30015b2968b81d0147fed9457aaa82d9fff4400a6b`.
The primary70-artifact closure predates this separate audit. The subsequent
material checkpoint binds both; primary numerical invocation count remains1.
