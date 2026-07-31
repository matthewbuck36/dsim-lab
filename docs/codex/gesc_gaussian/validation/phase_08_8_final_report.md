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

## Terminal disposition

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
