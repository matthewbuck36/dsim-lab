# Phase 08.8 Final Report — Counted-Source Open-Field Reproducibility

Verified: 2026-07-31

Branch: `feature/gesc-gaussian-robustness-v1`

Phase 08.8 implementation lineage:

```text
bc25fef  phase 08: close final report boundary
...
6f42040  phase 08.8: retain failed v8.10 secondary probe
```

The earlier
[whole-Phase-08 final report](phase_08_final_report.md) remains authoritative
through Phase 08.7. This additive report covers the separately approved
Phase 08.8 counted-source iteration, including every versioned correction,
fixed empirical result, and the terminal v8.10 evidence.

The v8.10 disposition below is preserved as its historical closeout snapshot.
The current overall Phase 08.8 disposition is the
[v8.11/v8.12 terminal amendment](#goal-continuation-terminal-amendment--v811-and-v812)
at the end of this report.

## V8.10 terminal snapshot

**PHASE 08.8 IS CLOSED AS A FIXED-LAYOUT DEVELOPMENT AND REPRODUCIBILITY
ITERATION. THE PRIMARY TWO-SOURCE LAYOUT PASSED ITS COMPLETE FORMAL GATE;
THE SECONDARY LAYOUT COMPLETED THE SCIENTIFIC BEHAVIOR BUT FAILED ITS FROZEN
EVALUATOR GEOMETRY CONTRACT.**

The final v8.10 result is:

```text
primary visible probe:                 1/1 formal pass
primary fresh-process repeats:        10/10 formal pass
primary fixed-layout total:           11/11 formal pass

secondary visible probe:               0/1 formal pass
secondary scientific behavior:         1/1 complete
secondary repeats:                     NOT RUN

v8.10 formal total:                   11/12
v8.10 scientific local-to-global:     12/12
v8.10 strict raw candidate ranking:   12/12
recording/final-zero/cleanup:          12/12
one-time analyzers:                    12/12
plots:                               108/108

M6 broader position/intensity matrix:  NOT RUN
three-light Gazebo:                    NOT RUN
physical motion:                       NOT RUN
```

The secondary failure triggered the Plan's fixed first-failure gate.
Seeds `19861..19865` and M6 were therefore prohibited. Phase 08.8 does not
establish two-layout formal repeatability, arbitrary position or intensity
robustness, three-light behavior, disturbance robustness, or broad simulation
readiness. No simulation-ready tag is created.

## Adopted research contract

Phase 08.8 implements the user's approved information and behavior boundary:

- the controller may know the total number of sources;
- every confirmed extremum is initially an unknown candidate;
- with `known_source_count=2`, the first distinct candidate must be filled
  and escaped before the second can be terminal;
- the controller compares candidates using rotation-stable raw sensor cost;
- the second candidate is accepted only when its uncertainty interval is
  strictly lower than the retained first-candidate interval;
- source coordinates, source roles, light inputs, global coordinates, Vicon,
  room dimensions, and simulator outcome remain unavailable to the
  controller;
- declared geometry is evaluator-only;
- the existing relative `/odom` input remains available for fill placement
  and local motion history, but Phase 08.8 adds no global localization,
  dead-reckoned route map, SLAM, waypoint planner, coverage planner, or
  persistent traveled-route memory;
- raw cost is authoritative for candidate identity and ranking;
- Gaussian and affine modifications are recovery terms, not evidence that a
  candidate is global;
- direct convergence to the second source without one completed local fill
  and recovery is not a pass;
- the operating field is assumed open and obstacle-free;
- wall and obstacle avoidance is outside the assignment and not claimed;
- physical arrival remains operator-terminated with `Ctrl+C`.

The supported behavior is deliberately local-first. Encountering the
strongest source first and filling it is not solved by this iteration because
return-to-best navigation was explicitly outside scope.

## Implemented architecture

### Counted candidates and raw-cost ranking

The existing supervisor now has a selectable:

```text
extremum_classification_mode =
  absolute_source_score   # preserved historical default
  counted_candidates      # Phase 08.8 opt-in
```

For counted candidates, `known_source_count=N` requires exactly `N-1`
possible active fill clusters. Complete physical-sensor rotations contribute
their minimum raw costs. Candidate estimates use the median of those rotation
minima and MAD-based uncertainty. A terminal candidate is accepted only when
its upper bound is strictly below every filled candidate's lower bound.
Revisits associated with an active fill do not consume another source
ordinal, and no fill can be added after the `N-1` budget.

The final profile uses six bounded pre-trigger rotations plus three
verification rotations. This retains approach evidence that would otherwise
be lost when confirmation occurs near the end of a basin approach.

ROS-independent state-machine tests also cover `known_source_count=3`: two
distinct fill/recovery episodes are required before a third candidate can be
terminal. That is logic coverage only, not three-light Gazebo evidence.

### Detector and fill behavior

The existing convergence detector gained an opt-in qualified-dwell policy.
It accumulates only while the existing motion/state gates are valid, uses
hysteresis to prevent repeated confirmation, and resets at invalid evidence
or search boundaries. The historical crossing-count policy remains the
default.

The existing adaptive Gaussian owner remains responsible for synchronized
basin estimation, anisotropic fill design, revision-one typed fills, and
active-fill identity. Phase 08.8 adds candidate-informed fill strength while
retaining historical defaults and the existing fill registry. It does not
replace the adaptive estimator with a fixed scalar Gaussian.

### Open-field recovery and affine role

The selected profile disables configured operating bounds, recenter,
post-recovery guidance, and wall/contact evaluation. It retains stale-input,
invalid-data, explicit-stop, watchdog, fill-design-timeout, final-zero, and
shutdown protections.

Recovery evolved into two accepted command-ownership branches:

```text
direct:
  ESCAPE_REPULSE -> SEARCH

assisted:
  ESCAPE_REPULSE -> ESCAPE_ASSIST -> SEARCH
```

During recovery, raw attraction is suppressed and the Gaussian/affine
geometry drives outward motion. If measured radial progress stalls, the
supervisor may take temporary command ownership using only onboard approach
history and active-fill geometry. On the first stable returned `SEARCH`
sample, ordinary GESC ownership and weights `(raw, Gaussian, affine) =
(1, 1, 0)` are restored, and escape direction/authority is cleared.

Thus the affine term is active only as a local-recovery aid. It is not a
permanent no-reversal rule, route memory, or source classifier. Persistent
avoidance of the old basin comes from the retained Gaussian fill.

### Evidence and simulation-only stop

Schema v13 accepts either recovery branch only with positive measured
distance, radial progress, command arithmetic, saturation, state/command
ownership, causal handoff, cleanup, and returned-search evidence.

The simulation may stop only after both:

1. the controller emits `GOAL_REACHED` for candidate ordinal two with one
   filled candidate and positive strict raw-cost separation; and
2. a later finite, noninterpolated evaluator odometry sample is within the
   declared simulation radius.

The final v8.10 radius is `0.50 m`, but actual retained final distances were
approximately `0.105-0.189 m`. The coordinate and stop are not passed to the
controller and are absent from the physical path.

## Versioned execution chronology

Phase 08.8 used fresh identities and retained every fixed failure. Across the
versions below, 46 Gazebo runs executed; one additional v8.9 attempt stopped
before Gazebo. The formal counts are not one acceptance denominator because
the implementation and evidence contract changed between versions.

| Version | Gazebo runs | Formal result | What the fixed evidence established |
|---|---:|---:|---|
| v8 | 1 | `0/1` | Counted policy treated the first candidate as unknown and created one fill, but departure from the filled basin failed. |
| v8.1 | 1 | `0/1` | Assisted local recovery completed and the simulated robot reached the stronger basin; post-confirmation-only raw sampling rejected the correct second candidate. |
| v8.2 | 2 | `1/2` | Pre-trigger raw evidence made the visible probe pass; repeat seed `19011` failed Stage B. |
| v8.3 | 6 | `5/6` | Candidate-informed fill passed the visible probe and four repeats; seed `19115` escaped through the arrival-side corridor and failed Stage B. |
| v8.4 | 3 | `2/3` | Approach-continuity guidance passed the visible probe and seed `19211`; seed `19212` reversed the selected direction and failed Stage B. |
| v8.5 | 7 | `6/7` | Active-fill transit passed the visible probe and five repeats; seed `19316` completed recovery but exhausted Stage B away from the global. |
| v8.6 | 2 | `1/2` | Supervisor-owned assist made seed `19316` pass; repeat `19411` reached the global scientifically but failed formal handoff and cleanup evidence. |
| v8.7 | 5 | `4/5` | Causal assist-exit evidence passed; seed `19514` completed the behavior but exposed an assist-entry evidence false negative. |
| v8.8 | 7 | `6/7` | Causal assist-entry evidence passed; seed `19616` completed a valid direct recovery that the assist-only result topology rejected. |
| v8.9 | 0 | pre-Gazebo fail | Schema v13 qualified both recovery branches, but the installed runner launched the recorder from `/tmp`; Git metadata creation stopped before Gazebo. |
| v8.10 | 12 | `11/12` | Recorder CWD was corrected. Primary passed `11/11`; secondary completed the behavior but failed declared-source Stage-A association. |

This sequence separated genuine behavior defects from evidence defects. No
failed fixed version was retried, relabeled, or added to a later version's
denominator.

## Final v8.10 primary result

### Frozen layout

```text
start:          (0.0, 0.0)
first lamp:     (1.0606601718, 1.0606601718)
second lamp:    (3.5, 3.5)
relative input: 400 / 1600
known count:    2
maximum fills:  1
environment:    open field, no validation walls or contacts
```

These coordinates and roles are scenario/evaluator declarations. The
controller receives only the source count and onboard signals.

### Repeatability

Visible seed `19801` and headless seeds `19811..19820` all passed every one
of the fourteen formal predicates:

```text
formal:                              11/11
complete local-recovery episodes:   11/11
exactly one typed active fill:       11/11
assisted command-ownership branch:  11/11
strict second-candidate ranking:    11/11
post-ranking global proximity:      11/11
recording/final-zero/cleanup:        11/11
```

For the ten repeat seeds:

```text
Stage A completion:              121.634 to 294.024 s
Stage B duration:                100.402 to 127.704 s
strict ranking margin:             0.094916 to 2.475247
exit alignment:                    0.991816 to 0.999946
assist-entry handoff:              2.091 to 9.999 ms
assist-exit handoff:               4.004 to 11.238 ms
final global distance:             0.106346 to 0.188818 m
```

The visible seed's strict margin was `0.898660` and final distance was
`0.104573 m`.

The complete evidence is in:

- [v8.10 primary visible report](phase_08_8_m4_11_primary_probe.md)
- [v8.10 primary repeat report](phase_08_8_m4_11_primary_repeats.md)

## Final v8.10 secondary result

### Frozen layout

```text
start:          (0.0, 0.0)
first lamp:     (0.5740251485, 1.3858192988)
second lamp:    (3.5, 3.5)
relative input: 400 / 1600
known count:    2
maximum fills:  1
environment:    open field, no validation walls or contacts
```

Seed `19851` completed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

It created exactly one fill, passed the schema-v13 direct-repulse ownership
branch, restored ordinary GESC, ranked candidate two lower by
`3.6060025904`, and finished `0.1055488518 m` from the global.

The formal evaluator nevertheless reported `10/14`, because its frozen
Stage-A rule associated the observed basin to the declared lamp coordinate:

```text
observed first convergence:        (1.1932522798, 1.8213642373)
fill center:                       (1.1854262109, 1.8223420991)
fill-to-convergence:                0.0078869239 m
convergence-to-declared lamp:       0.7570611822 m
fill-to-declared lamp:              0.7512412491 m
fixed association maximum:          0.60 m
```

The overlapping two-light field shifted the aggregate local basin away from
the lamp marker. The controller and fill agreed closely on the observed
basin, but the evaluator left the fill unassigned, never credited Stage A,
and consequently never opened Stage B. This is one cascading evaluator
geometry false negative, not four independent controller failures.

The result remains formally failed because widening `0.60 m` after observing
the outcome would weaken a fixed gate. A future version may precompute the
aggregate-field extremum evaluator-side or use a predeclared basin-association
rule, while keeping that geometry inaccessible to control.

The complete evidence is in:

- [v8.10 secondary fixed result](phase_08_8_m4_11_secondary_probe.md)

Secondary repeatability is **not established**. The planned five repeats did
not run.

## Candidate-ranking result

All twelve v8.10 runs demonstrate the controller-level counted policy:

```text
candidate one:
  initially unknown
  characterized from raw rotation minima
  filled exactly once
  escaped

candidate two:
  distinct from the active fill
  characterized from raw rotation minima
  ordinal 2 with filled count 1 and known total 2
  strictly lower than candidate one
  accepted as GOAL_REACHED
```

Across v8.10, the strict separation margin ranged from `0.094916` to
`3.606003`. No candidate was accepted from the absolute source-score
threshold, declared source input, position, or evaluator proximity.

This supports the narrow claim that the robot can compare the two encountered
basins and identify the stronger second minimum after a required local
recovery. It does not prove that only two extrema exist unless the known-count
assumption is true, nor does it solve global-first encounter order.

## Infrastructure and evidence result

The final no-Gazebo qualification passed:

```text
targeted recorder-CWD tests:       10 passed
schema and runner:                366 passed, 1 skipped
controller/supervisor/detector:   310 passed
evidence/recording/analyzer:      653 passed, 2 skipped
broad ROS-independent suite:      963 passed, 3 skipped
isolated package build:             3 packages passed
source/install parity:             10/10
installed scenario dry-runs:         4/4
```

All three runner owners now start the sole Phase 05 recorder with
`cwd=REPOSITORY_ROOT`. Every v8.10 metadata record captured the intended clean
dispatch commit and `/home/mattb/dsim-lab`, even when the installed runner was
called from `/tmp`.

All twelve v8.10 bags passed authoritative completeness, final readiness
false, final-zero, SQLite integrity, and scoped cleanup. Each complete run was
analyzed exactly once from its runner-summary-owned directory.

One primary repeat, seed `19812`, has `analysis_status=partial` because an
optional generic state-duration metric rejected one sampling gap over
`0.150 s`. Its critical inputs, formal predicates, scientific metrics,
validator result, tables, and all nine plots are complete. It was not rerun.

The final qualification record is:

- [v8.10 no-Gazebo qualification](phase_08_8_m4_11_no_gazebo_qualification.md)

Historical V6, worlds, scenarios, reports, failures, and retained external
artifacts remain unchanged and selectable. The legacy profile, cost sign and
units, canonical topics, one `/cmd_vel` owner, and shared
simulation/physical algorithm owners remain preserved.

## Plots and retained artifacts

Each v8.10 run has:

```text
analysis/phase07/plots/
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

Primary visible summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_probe/
  phase08_v8_10_primary_visible_probe_summary.yaml
```

Primary repeat summary, which owns all ten exact run paths:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_repeats/
  phase08_v8_10_primary_repeats_summary.yaml
```

Secondary visible summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_secondary_probe/
  phase08_v8_10_secondary_visible_probe_summary.yaml
```

The primary visible and all ten primary repeat trajectories were visually
inspected. The secondary trajectory was also inspected and shows the shifted
first basin, one fill, direct escape, ordinary transit, and final global
capture.

## What is usable now

The primary fixed layout is the defensible repeatable simulation
demonstration:

> With two known sources, an obstacle-free open field, local-first encounter,
> and simulator-relative `400/1600` inputs, the selected controller repeatedly
> fills and escapes the first basin, resumes ordinary GESC, strictly ranks the
> second basin by raw cost, and converges near it.

The evidence for that exact statement is `11/11` formal runs.

The secondary fixed layout is scientifically promising because its one run
completed the same objective through the direct branch. It is not a formally
qualified repeatable layout because the evaluator failed and the five
repeats were correctly withheld.

The simulator-relative `400/1600` values are not lux, volts, or a physical
calibration. A physical experiment must establish a sensor-response condition
that produces a comparable two-basin field without exposing either source
position to the controller.

## What remains unproven

- arbitrary light positions or intensity ratios;
- two formally repeatable layouts;
- an offline topology-admitted broader matrix;
- three-light Gazebo behavior;
- unknown source count;
- global-first encounter and return to the best remembered candidate;
- noise, delay, saturation, uneven flooring, wheel slip, and physical-light
  transfer;
- wall, collision, and obstacle avoidance;
- finite-field completeness outside the searched region;
- broad simulation readiness or physical readiness.

Guaranteed wall avoidance was deliberately removed from this iteration's
claim. The primary success must not be described as evidence that the robot
can safely handle walls or obstacles.

## Physical stop and safety boundary

No coordinate-based simulation arrival stop may enter the physical launch or
controller.

Physical operation must continue until the user decides the robot is close
enough and presses `Ctrl+C`. The shutdown must still preserve:

```text
readiness false
-> stop motion
-> publish final zero
-> finalize recording
-> scoped descendant cleanup
```

This manual arrival policy does not authorize physical motion by itself.

## Recommended next boundary

Phase 09 should begin as a separate static physical-interface and calibration
Plan, not as a continuation of Phase 08.8 Gazebo tuning. Its first empirical
target should be the primary two-source geometry and a measured physical
response ratio corresponding to the known simulator `1:4` condition.

Before motion, Phase 09 should verify the real sensor range, polarity,
rotation timing, odometry/IMU interfaces, launch parity, recorder,
emergency-stop procedure, final-zero ordering, and operator-managed open-field
boundary. It should receive separate explicit authorization for physical
motion.

The secondary evaluator geometry defect can be corrected in a separately
versioned simulation Plan if a second formal layout is still required. It
must not be hidden inside the physical commissioning path.

## M7 closeout qualification

The final no-Gazebo closeout rechecked the current source, installed v8.10
overlay, retained summaries, all twelve bags, analysis bundles, documentation,
and runtime boundary:

```text
counted/detector/recorder-CWD regressions:   108 passed
schema-v1..v13 and legacy regressions:       218 passed
new Markdown links:                          12/12
changed Phase 08.8 Python syntax:            12/12
v8.10 YAML / central launch XML:              4/4 / PASS
source/install byte parity:                  10/10
summary-owned retained runs:                 12/12
authoritative completeness:                  12/12
SQLite PRAGMA quick_check:                   12/12
analysis failures:                            0
plots:                                      108/108
historical worlds and V6 hashes:             unchanged
Phase 08 context / git diff check:           PASS / PASS
active simulation, analysis, or physical:    none
```

This M7 validation changed no source, launch, scenario, world, test, retained
run, bag, analysis, or plot.

## Final go/no-go

```text
primary fixed-layout simulation demo:        GO
primary 10-run repeatability claim:           GO
counted raw-cost candidate ranking:           GO for tested local-first cases
secondary scientific demonstration:          GO as retained evidence
secondary formal repeatability claim:         NO-GO / NOT RUN
broader positions or intensities:             NO-GO / NOT RUN
three-light Gazebo claim:                     NO-GO / NOT RUN
wall or obstacle claim:                       NOT APPLICABLE
broad simulation-ready tag:                   NO-GO
automatic physical coordinate stop:           PROHIBITED
physical motion from this report alone:       NOT AUTHORIZED
```

## Goal-continuation terminal amendment — v8.11 and v8.12

Verified: 2026-07-31

**PHASE 08.8 IS NOW TERMINALLY CLOSED AFTER V8.12. V8.11 QUALIFIED THE
SECONDARY FIXED LAYOUT AT `1/1 + 5/5`; V8.12 PASSED ITS VISIBLE CORRECTIVE
PROBE, THEN CLOSED WHEN THE FIRST BROAD-MATRIX CASE COMPLETED THE SCIENTIFIC
LOCAL-TO-GLOBAL BEHAVIOR BUT FAILED ONE FROZEN FORMAL EXIT-ALIGNMENT
PREDICATE. NO RETRY, REMAINING MATRIX CASE, V8.13, OR PHYSICAL RUN IS
AUTHORIZED.**

This amendment supersedes the overall Phase 08.8 disposition in the v8.10
snapshot without altering any v8.10 result. Every fixed failure, bag, plot,
scenario, world, V6 selection, and historical denominator remains unchanged.

### Current empirical boundary

The results must remain separated by fixed experiment version and layout:

| Evidence population | Formal result | Scientific behavior | Disposition |
|---|---:|---:|---|
| v8.10 primary fixed `1:4` | `11/11` | `11/11` | qualified repeatable simulation demo |
| v8.10 secondary fixed `1:4` | `0/1` | `1/1` | historical evaluator-geometry failure |
| v8.11 secondary fixed `1:4` | `6/6` | `6/6` | qualified second fixed-layout demo |
| v8.11 matrix seed `19931`, `1:3` | `0/1` | `0/1` | immediate pre-escape anchor failure; v8.11 closed |
| v8.12 visible seed `20001`, `1:3` | `1/1` | `1/1` | corrective interior-anchor pass |
| v8.12 matrix seed `20031`, `1:3` | `0/1` | `1/1` | formal alignment failure after complete behavior; v8.12 closed |
| v8.12 matrix seeds `20032..20034` | not run | not run | withheld after first failure |

These rows are not one pooled acceptance denominator: implementation and
evidence contracts changed between v8.10, v8.11, and v8.12. The defensible
repeatability claims are the exact v8.10 primary `11/11` population and the
exact v8.11 secondary `6/6` population.

### V8.11 outcome

Schema v14 replaced the old individual-lamp distance gate with a predeclared,
evaluator-only aggregate-field topology record. That correction never enters
the launch command or controller graph. It allowed the already-observed
shifted aggregate basin to be credited without exposing a source position,
role, intensity, or global coordinate to control.

The v8.11 secondary visible seed `19901` and headless seeds `19911..19915`
passed every formal predicate:

```text
visible / repeats:                    1/1 + 5/5 PASS
formal predicates:                   84/84 PASS
exact one-fill local recoveries:      6/6
strict candidate-two rankings:       6/6
post-recovery global proximity:       6/6
recording/final-zero/cleanup:          6/6
one-time analyses / plots:             6 / 54
escape branches:                       5 direct / 1 assisted
final global distance range:          0.124299..0.185811 m
```

This establishes the requested second fixed two-source layout at the retained
simulator-relative `400/1600` (`1:4`) condition. It also demonstrates both
accepted local-recovery ownership branches.

Reports:

- [v8.11 secondary visible](phase_08_8_m8_3_v8_11_secondary_visible_probe.md)
- [v8.11 secondary repeats](phase_08_8_m8_3_v8_11_secondary_repeats.md)

The subsequent first broad-matrix seed `19931` created one valid fill but had
no approach-history pose outside the runtime fill exit radius. It immediately
entered `FAILSAFE` before a valid escape interval. The serial suite stopped;
seeds `19932..19934` were not run. V8.11 remained failed for the varied matrix.

Report:

- [v8.11 broad-matrix failure](phase_08_8_m8_4_v8_11_broad_matrix.md)

### V8.12 correction and visible result

V8.12 added an opt-in, historical-default-off supervisor fallback:

```text
open_field_escape_interior_anchor_fallback_enabled:       false
open_field_escape_interior_anchor_min_displacement_m:     0.50
```

If no pre-fill pose lies outside the frozen exit radius, enabled counted-source
open-field runs may select the farthest finite odometry-history pose when its
displacement is at least `0.50 m`. The original outside-radius anchor retains
priority. Empty, nonfinite, unordered, degenerate, and below-minimum histories
still fail safe. The controller uses only its existing odometry history, fill
center, and fill radius; it receives no evaluator geometry or global data.

No-Gazebo qualification passed `1012` functional tests with `3` unchanged
skips, exact retained-bag replay, all `97/97` historical scenarios, V6/world
hashes, a fresh isolated three-package install, installed graph construction,
source/install parity, and both scenario dry-runs.

The fresh visible seed `20001` then passed `14/14` predicates. It selected the
`interior_farthest` anchor at `1.330955 m`, completed assisted recovery,
strictly ranked candidate two by `0.648504`, and stopped `0.116707 m` from the
global. Its exact run was analyzed once and retains all nine plots.

Reports:

- [v8.12 no-Gazebo qualification](phase_08_8_m8_7_v8_12_no_gazebo_qualification.md)
- [v8.12 visible pass](phase_08_8_m8_8_v8_12_visible_probe.md)

### V8.12 terminal matrix result

The fixed v8.12 matrix was dispatched once, serially, with stop-on-first-fail
and no retry. Only seed `20031` ran. It passed `13/14` predicates and completed:

```text
first candidate characterized
-> exactly one typed fill created
-> interior_farthest anchor selected at 1.318198 m
-> direct local recovery completed
-> ordinary SEARCH restored
-> candidate two strictly ranked by 2.518884
-> GOAL_HOLD
-> first valid post-recovery proximity sample at 0.127754 m
```

Stage A, Stage B, fill cardinality, ranked goal, ground-truth goal, state/event
path, forbidden-state/event absence, recording, final zero, readiness false,
SQLite integrity, and cleanup all passed. The only formal failure was:

```text
escape_command_ownership:
  direct measured fill-to-exit alignment is below 0.80
```

The direct route cleared the `1.366771 m` exit radius and reached
`1.425083 m` maximum radial distance. Its measured returned-`SEARCH` exit was
`1.439288 m` from the fill center, but GESC curved to an alignment of
`0.735563`, or `42.6452 degrees`, against the initially selected direction.
The fixed gate requires at least `0.80`, or at most `36.8699 degrees`.

This is a formal evidence-contract failure alongside a completed scientific
behavior. Direct GESC recovery is not a straight-line supervisor command; its
raw, Gaussian, and affine terms may produce a curved but outward, radius-clearing
exit. The retained evidence therefore shows that the algorithm escaped and
converged while the prescriptive alignment gate rejected that trajectory.
V8.12 remains formally failed because changing the gate after dispatch would
invalidate the frozen experiment.

The exact run was analyzed once and retains all nine plots. Analyzer status is
`partial` solely because an optional generic state-duration metric observed one
sampling gap over `0.150 s`; critical and scientific metrics, stored and fresh
Phase 05 validation, and all plots are complete with no analysis failures.

Report:

- [v8.12 broad-matrix result](phase_08_8_m8_9_v8_12_broad_matrix.md)

### What is qualified now

Two exact obstacle-free, local-first, two-source layouts are repeatable at the
simulator-relative `400/1600` (`1:4`) ratio:

```text
primary layout:
  start (0.0, 0.0)
  local (1.0606601718, 1.0606601718)
  global (3.5, 3.5)
  formal repeatability 11/11

secondary layout:
  start (0.0, 0.0)
  local (0.5740251485, 1.3858192988)
  global (3.5, 3.5)
  formal repeatability 6/6 under schema-v14 topology evidence
```

For those exact fixed demonstrations, the selected controller treats the first
extremum as unknown, characterizes raw rotational cost, creates one adaptive
Gaussian fill, escapes it through a direct or assisted branch, resumes ordinary
GESC, rejects the filled basin as a terminal candidate, ranks the second basin
strictly lower, and converges near it.

V8.12 additionally shows two fresh scientific local-to-global completions at
the same `1:3` geometry, one formal pass and one formal alignment failure. That
is useful development evidence, not a repeatability population.

### What remains unproven

- the planned four-case varied-layout/intensity matrix;
- the `1:5` cases and alternate local placements in v8.12;
- arbitrary or continuous light positions and intensity ratios;
- three-light Gazebo behavior, despite known-count-three unit coverage;
- unknown source count;
- global-first encounter and return to a remembered best candidate;
- noise, latency, saturation, wheel slip, uneven flooring, or physical-light
  transfer;
- walls, obstacles, or autonomous collision avoidance;
- field-wide simulation readiness or a physical-readiness tag.

The broad matrix gate is not met. No simulation-ready tag is created.

### Plots and direct inspection

The v8.12 visible and matrix runs each retain the standard nine plots under
their exact `analysis/phase07/plots/` directories. The terminal matrix run is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_12_broad_matrix/
  2026-07-31/
  20260731T233137972843Z_simulation_phase08_v8_12_broad_matrix-
  v8_12_matrix_r1p25_a45_ratio1to3_20031-robust_gaussia_6efe976a/
  analysis/phase07/plots/
```

Its trajectory, radial-escape, state-event, candidate-ranking, and cost plots
were visually inspected. They show origin-to-local motion, one fill, a direct
outward exit, curved transit, strict candidate separation, and a final orbit
near the global.

### Physical and phase boundary

The simulation `0.50 m` global-proximity stop is evaluator-only and is never
passed to the controller. It must not enter the physical launch path. During a
future physical run, the robot continues until the operator decides it is
sufficiently close and presses `Ctrl+C`, while shutdown still enforces:

```text
readiness false -> stop -> final zero -> recording finalization -> cleanup
```

Phase 08.8 authorized no physical motion, and none occurred.

V8.12 is the final Phase 08.8 experiment version. There is no v8.13 under this
goal. The next permitted work is a separately planned and authorized Phase 09
boundary, beginning with static physical-interface, sensor calibration,
operator-stop, recording, and launch-parity qualification before any physical
motion.

### Current final go/no-go

```text
v8.10 primary fixed-layout simulation demo:    GO / 11/11
v8.11 secondary fixed-layout simulation demo:  GO / 6/6
counted raw-cost ranking in those layouts:      GO
v8.12 interior-anchor implementation:           QUALIFIED, default off
v8.12 visible corrective run:                   GO / 1/1
v8.12 varied-layout/intensity matrix:           NO-GO / first case formal fail
remaining v8.12 cases:                          NOT RUN
v8.13:                                          NOT PLANNED OR AUTHORIZED
three-light Gazebo claim:                       NO-GO / NOT RUN
broad simulation-ready tag:                     NO-GO
automatic physical coordinate stop:             PROHIBITED
physical motion from Phase 08.8:                 NOT AUTHORIZED
Phase 09 planning:                              NEXT SEPARATE BOUNDARY
```

### M8.10 terminal closeout qualification

The terminal closeout performed no new Gazebo, ROS graph, analyzer, or physical
execution. Source and scenario code remained at committed dispatch HEAD
`dd2185d`; the only pending paths were this report, the handoff, live status,
navigation, and the new v8.12 result report. The complete v8.12 no-Gazebo
implementation qualification therefore remains applicable and was not
expensively rerun merely to close documentation.

Fresh closeout checks passed:

```text
required Phase 00 audit documents:             PASS
Phase 08 implement context:                    PASS
changed paths outside Phase 08.8 docs:         0
relative Markdown links:                       38/38
git diff --check:                              PASS

v8.10 retained results / plots:                12 / 108
v8.11 retained results / plots:                 7 / 63
v8.12 retained results / plots:                 2 / 18
v8.12 matrix summary run entries:               1
v8.12 matrix seed 20031 entries:                1
v8.12 matrix seed 20032-20034 entries:           0
terminal bag SQLite PRAGMA quick_check:         ok
terminal analysis failures / plots:             0 / 9

gazebo_empty.world hash:                       unchanged
gesc_gaussian_validation.world hash:           unchanged
corner-origin validation world hash:           unchanged
Phase 08 V6 selection hash:                    unchanged
active simulation, analysis, or physical:      none
```

Retained anchor hashes are still:

```text
gazebo_empty.world:
  3085542f9dc1d13fdf9368a24808a226908d1a2c5a7a4ffd07bc6f374ca14b43
gesc_gaussian_validation.world:
  8ecc1a231efec24401d74fef3cd5139d48c6029f88e71d044cefdf2fd14c5bef
gesc_gaussian_corner_origin_validation.world:
  88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf
phase_08_v6_selection.json:
  dcdbf937fe3de0cab9449c2b01af79fd938e1d3f9791b4897937875d0747590d
```

Every dispatched result and undispatched definition is accounted for. V8.12
is closed without a retry, v8.13 is absent, and Phase 08.8 has no remaining
authorized work.
