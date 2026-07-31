# Phase 08.8 M4.6 Fixed V8.5 Primary Repeats

Date: 2026-07-31
Committed dispatch boundary: `89946b9`
Scenario: `phase08_v8_5_primary_repeats.yaml`
Case: `v8_5_primary_repeat_r1p5_a45_h25`
Seeds: `19311..19320`
Profile: `robust_gaussian_v1`

## Result

**FIXED POPULATION FAIL — seeds `19311..19315` passed, seed `19316`
passed Stage A and local escape but failed the independent `180.0 s` Stage B
gate, and seeds `19317..19320` were not dispatched.**

The fixed population ran once, serially and headlessly, from the committed
isolated install. Every executed seed was retained. Seed `19316` was not
retried or changed in flight. The runner stopped at the first formal failure
as required.

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_repeats/
  scenario_summaries/
  20260731T102730662971Z_phase08_v8_5_primary_repeats.yaml
SHA-256:
  b6f563206de201654264de12d2fadf694e0d34f0bf47cac9614271dd479484ea
```

```text
resolved runs:       10
executed runs:       6
formal passes:       5
formal failures:     1
not dispatched:      4
stopped early reason: run_failure
runner return code:  1
```

## Population results

| Seed | Formal result | Stage A (s) | Stage B (s) | Final global distance |
|---:|---|---:|---:|---:|
| 19311 | PASS | 259.525 | 124.882 | 0.147096 m |
| 19312 | PASS | 141.614 | 123.012 | 0.120690 m |
| 19313 | PASS | 191.332 | 134.096 | 0.299232 m |
| 19314 | PASS | 203.921 | 161.602 | 0.164801 m |
| 19315 | PASS | 234.604 | 141.304 | 0.123232 m |
| 19316 | FAIL | 177.532 | 180.030 | 2.149315 m |
| 19317..19320 | NOT DISPATCHED | — | — | — |

All six executed runs passed recording completeness, final readiness false,
final-zero commands, exactly one typed active fill, Stage A local recovery,
and cleanup. No executed run entered `RECENTER` or `FAILSAFE`, emitted a
forbidden event, timed out its escape, or left a Gazebo, recorder, scenario,
or rosbag process behind.

The five passing seeds each completed the full path:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Seed `19316` completed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
```

It never produced a second convergence candidate or `GOAL_REACHED` before
the independent Stage B evidence clock expired.

## Failed-seed retained evidence

Run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_repeats/
  2026-07-31/
  20260731T110116556773Z_simulation_phase08_v8_5_primary_repeats-v8_5_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_3d6091a5
```

Hashes:

```text
raw bag:
  9b06dbf5374fd52a08f11c466b386b996075cc97496c280beaaec3cbff2a8edd
completeness.json:
  b3dc4e5b4ac3ee64571354c275b9fbf708fe2330367091918fb92b153a43a9ff
scenario_result.yaml:
  70387d3cd73c586344ba27ea366c63dc77c9aa92e54022463f4a735abfc21372
analysis/phase07/analysis_completeness.json:
  01a3016d38d0a56d537c0c124b2cb624ca13c88c284834e8e5be44ccee59d085
analysis/phase07/summary_metrics.json:
  fb2f6d47a7a9606534307543ed3cc7709d059b05da492296536d67a66c794af6
```

The standard analyzer was executed exactly once for each of the six retained
runs. Seeds `19311`, `19313..19316` have `complete` analysis with no
failures. Seed `19312` is honestly `partial` with no analysis failures:
exactly one ordinary algorithm-state sample gap exceeded the generic
`0.150 s` duration-reconstruction limit, so only aggregate state durations
are invalid. Its formal staged scenario result, event/state sequence,
candidate ranking, Stage A, Stage B, completeness, and cleanup all pass.

## Escape geometry comparison

The v8.5 selected direction remained revision one in every run. The
evaluator-only `selected/global` column is the dot product between that
onboard-history direction and the offline fill-to-global direction.
`exit/selected` and `exit/global` describe the actual radial direction from
the fill center to the measured escape-completion pose.

| Seed | Selected/global | Exit/selected | Exit/global | Global distance at Stage B start |
|---:|---:|---:|---:|---:|
| 19311 | +0.999 | +0.707 | +0.680 | 2.544 m |
| 19312 | +0.958 | +0.960 | +0.838 | 2.018 m |
| 19313 | +1.000 | +0.180 | +0.180 | 3.529 m |
| 19314 | +1.000 | +0.027 | +0.042 | 3.613 m |
| 19315 | +0.850 | -0.214 | +0.333 | 2.963 m |
| 19316 | +0.943 | **-0.925** | **-0.746** | **4.544 m** |

The selected vector itself did not reverse and was not the v8.5 failure.
For seed `19316`:

```text
fill center:
  (0.942275, 1.234690) m
selected direct vector:
  (0.485035, 0.874495)
selected rotation:
  0.0 rad
direction revision:
  1
active-fill exclusion:
  fill 1 only
retained other fills:
  0
escape-completion pose:
  (0.780608, -0.139229) m
```

The selected vector was strongly aligned with the offline direction to the
global, but the physical exit occurred almost exactly opposite it.

## Root cause: command-arbitration defect

The default v8.5 command combiner adds the GESC command to the bounded
supervisor assist command and saturates only after addition:

```text
ESCAPE_ASSIST output = saturate(GESC Gaussian/affine command
                                + supervisor direction command)
```

That does not give the latched direction physical command authority. In the
failed seed's `2,860` synchronized `ESCAPE_ASSIST` control samples:

```text
samples with nonzero supervisor angular request:      2,847
samples where |GESC angular| > |supervisor angular|: 2,640
samples where combined turn opposed supervisor:      1,605
mean |GESC angular request|:                           7.095 rad/s
mean |supervisor angular request|:                     0.398 rad/s
samples with nonzero supervisor linear request:       0
```

The supervisor correctly requested approximately `+0.4 rad/s` toward the
latched world-frame direction. The much larger oscillatory GESC angular
request dominated before saturation, repeatedly kept heading outside the
supervisor's drive cone, and therefore held supervisor linear assistance at
exactly zero for the complete `22.172 s` assist interval. The robot escaped
only because the competing GESC command happened to carry it radially beyond
the fill.

This explains the population dispersion: the same nominal direct-direction
contract produced actual exit-direction alignment from `+0.960` through
`-0.925`. V8.5 latched and reported a direction, but did not make that
direction the owner of the assisted physical command.

## Why the Stage B clock exposed rather than caused the failure

Seed `19316` was not stuck after recovery. Once ordinary affine-free `SEARCH`
resumed, it made a wide open-field turn and began approaching the global:

```text
global distance at Stage B start: 4.544 m
global distance at retained end:  2.141 m by final odometry sample
distance reduction in final 60 s: 1.979 m
final-60-s path efficiency:        0.912
failsafe:                          false
controller timeout event:          false
```

Its trajectory was still converging when the scenario-only `180.0 s`
evidence clock expired. A larger evidence budget would probably have admitted
this particular trajectory, but it would not correct the seed-dependent
escape-side dispersion or the defeated supervisor command. The next version
must correct command ownership first. A relaxed Stage B evidence budget can
then provide nonphysical timing slack without being presented as the
algorithmic fix.

## Plots

Each executed run now contains all nine standard plots under:

```text
<run_directory>/analysis/phase07/plots/
```

The failed seed's directory is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_repeats/
  2026-07-31/
  20260731T110116556773Z_simulation_phase08_v8_5_primary_repeats-v8_5_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_3d6091a5/
  analysis/phase07/plots/
```

It contains:

```text
trajectory_sources_fills.png
candidate_ranking.png
cost.png
components.png
state_events.png
weights.png
command_saturation.png
radial_escape.png
gaussian_history.png
```

The failed trajectory plot shows the south-side escape, wide turn, and late
northeast approach. The components and weights plots show affine authority
ending correctly at Stage A completion. The command plot and synchronized
control table expose the GESC/supervisor arbitration defect.

## Gate disposition

The fixed v8.5 primary population is closed at `5/6` executed passes. It does
not authorize the v8.5 secondary probe, secondary repeats, broad
characterization, three-light testing, physical motion, or a reproducibility
claim. Seeds `19317..19320` remain deliberately undispatched.

The next permissible work is a separately planned, default-off v8.6
correction that gives the bounded supervisor direction exclusive command
ownership during `ESCAPE_ASSIST`, retains ordinary GESC ownership before and
after recovery, and relaxes only the scenario Stage B evidence budget.
