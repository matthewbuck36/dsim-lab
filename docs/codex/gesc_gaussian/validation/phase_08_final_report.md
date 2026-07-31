# Phase 08 Final Report — GESC/Gaussian Simulation Validation

Verified: 2026-07-30

Branch: `feature/gesc-gaussian-robustness-v1`

Phase lineage covered:

```text
8c85d8c  phase 08: add robustness validation plan
...
3696677  phase 08.7: close reproduction campaign
```

This document is the whole-Phase-08 terminal report. It summarizes the
historical Phase 08 v1 result, the staged v2 restart, diagnostic Phases
08.1-08.2, acceptance versions v3-v5, the two-light V6 experiment, the
corner-origin Phase 08.7 development line, and the final M4.8 reproduction
campaign. The version-specific Plans, handoffs, reports, status entries, and
retained external run roots remain authoritative for their exact fixed
experiments.

## Terminal disposition

**PHASE 08 IS CLOSED AS A DEVELOPMENT AND DIAGNOSTIC PHASE. THE ORIGINAL
BROAD SIMULATION-ROBUSTNESS / SIMULATION-READY OBJECTIVE FAILED.**

Phase 08 did not complete a passing selection-blind holdout, a 70-unique-case
validation denominator, a reproducibility gate attached to that denominator,
or a simulation-ready parameter freeze. No simulation-ready tag was created.
No Phase 09 implementation or physical-hardware run occurred.

Phase 08 nevertheless established all of the following:

- the local-recovery mechanism can execute end to end in Gazebo:
  `SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE
  -> RECENTER -> SEARCH`;
- a lower-output two-light local can be associated causally with exactly one
  typed Gaussian fill, escaped, recentered from, and followed by progress
  toward the stronger light;
- the fixed simulator-relative `400/1600` local/global input ratio is the
  strongest known two-light condition tested in the final lineage;
- the final evidence-selected reproduction campaign produced `13/17` formal
  passes and `14/17` behavioral passes, clearing its literal “most pass
  again” threshold;
- recording, collision evidence, final-zero publication, scoped cleanup, and
  SQLite integrity were reliable across all `17/17` final reproduction
  attempts;
- legacy behavior, V6, all historical scenarios/worlds, canonical topics,
  controller ownership, cost sign/units, and shared simulation/physical
  algorithm ownership remain preserved.

The final reproduction result is useful but intentionally narrow. It sampled
conditions selected because they had succeeded before. It is not an unbiased
robustness population and cannot retroactively pass the failed v1-v6 or
Phase 08.7 spatial-suite gates.

## How to read the results

Phase 08 retained three different kinds of result:

- **behavioral pass**: the robot completed the declared algorithm path and
  arrival boundary;
- **formal pass**: behavior plus recording, evidence, collision, final-zero,
  and cleanup gates all passed;
- **infrastructure pass**: the simulation and evidence pipeline completed,
  whether or not the robot behavior met its scenario contract.

These are not interchangeable. Several runs safely reached a global target
but failed the branch they were assigned to exercise. Other runs completed
the desired robot behavior but failed a timestamp or console-evidence check.
Phase 08 preserved those distinctions rather than weakening a gate after
observing the result.

## Executive chronology

| Lineage | Main purpose | Executed evidence | Terminal result |
|---|---|---:|---|
| Phase 08 v1 | Original parameter sweep, holdout, and large validation pass | 81 training, 12 exposed holdout, 203 retained directories from a planned 519-run pass | **Failed.** Every training candidate had zero end-to-end success and zero escape attempts. C8 was selected only by a path-length tie-break. Holdout controller success was `0/12`; the large pass was stopped. |
| Phase 08 v2 | Fresh staged 120-run design with a mandatory activation gate | 10/10 activation cases | **Failed at Gate 2, 1/10.** No tuning, freeze, holdout, 70-case denominator, or repeats ran. |
| Phase 08.1 | Diagnose and correct retained v2 activation defects | Two bounded diagnostic probes | Engineering recovery succeeded. The high-goal probe passed; the fill/escape probe completed escape but recenter orbited into timeout/failsafe. Not acceptance. |
| Phase 08.2 | Correct the observed recenter orbit | One sealed development probe | **Passed its recenter-only contract.** One fill, one escape, recenter in about `8.61 s`, return to `SEARCH`, no collision/failsafe/evidence failure. |
| Phase 08.3 / v3 | Fresh 120-slot robustness workflow | V3A-V3D bounded attempts; one retained V3B behavioral record and one V3D Gazebo record at terminal lineage | **Failed before acceptance.** Contact-control contamination, a real behavioral miss, a boundary-observer executor error, then recorder SIGINT context invalidation. |
| Phase 08.4 / V4 | Repair recorder/runner and restart fresh acceptance | Three actual Gazebo attempts across preserved roots; corrected pass-eligible root ran 1/120 | **Failed activation responsibility.** The corrected case safely reached the aggregate optimum directly but never exercised its required fill/escape/recenter branch. |
| Phase 08.5 / V5 | Force a two-/three-light blocking local basin | 8 visible activation runs | **Failed blocker encounter, 0/8.** Four runs executed the full recovery lifecycle, but the live path bypassed the predeclared blocker and filled another extremum. |
| Phase 08.6 / V6 | Simple two-light Hue-ratio demonstration | Four-case sweep plus three H25 repeats | **Failed repeatability.** H25 was the only eligible sweep ratio; full-record repeat result was `1/3`, while first local-recovery episode success was `2/3`. |
| Phase 08.7 | Shifted room, known topology, staged local/global result, focused two-light corrections | M2 through M4.7 probes/suites plus 17-case M4.8 campaign | Fixed several real integration defects and produced successful cases, but no complete prospective suite passed. Final retrospective M4.8 result: `13/17` formal, `14/17` behavioral. |

## Original Phase 08 objective and why it failed

The original Phase 08 objective was a parameter freeze backed by robust
simulation acceptance. Its evolved v2/v3/v4 design allocated:

```text
10 activation
30 development/tuning
20 selection-blind holdout
50 additional unique validation
10 reproducibility repeats
120 declared runs total
70 unique formal acceptance cases
```

No experiment version passed far enough to enter the 70-case denominator.
This is why there are no Phase 08 Wilson confidence intervals, no accepted
frozen robust profile, and no simulation-ready tag.

### V1

V1 executed all `81/81` training runs. Every candidate had zero end-to-end
success and zero observed escape attempts. Candidate C8 was selected only
because it had the lowest median path length, `13.2286087344 m`, after all
behavioral criteria tied at zero.

The exposed 12-run holdout produced:

```text
controller goal success:       0/12
simulation ground truth:       5/12
failsafe:                      2/12
collision:                     0/12
```

The planned 519-run first full pass was stopped with 203 retained run
directories and no completed `pass_1.json`. The v1 root contains immutable
historical evidence and must never be resumed or counted in a later
denominator.

Two blocking defects explained the zero escape activation:

1. the convergence detector's confirmed event and the supervisor's required
   continuous-status timing made real detector-to-supervisor activation
   unreachable;
2. goal verification used an instantaneous orientation-dependent source
   score, which could not remain high while the physical sensor rotated.

### V2

V2 corrected the activation contract, introduced rotation-aware verification,
and sealed the staged workflow. Its ten-run activation gate still passed only
`1/10` complete integrity/lifecycle contracts:

```text
recording complete:                 3/10
analysis complete:                  3/10
cleanup:                           10/10
controller plus ground truth:       1/10
valid no-collision evidence:        9/10
typed fills:                            7
escape attempts:                        1
```

Six cases suffered stale-source typed-event timestamp regressions after
timeout/failsafe; another missed a required publisher-parameter snapshot.
The early-stop rule worked: tuning and all later stages remained `NOT RUN`.

## Engineering recovery: Phases 08.1 and 08.2

Phase 08.1 used the retained v2 evidence to correct five bounded defects:

1. **Fill synchronization:** estimator inputs were restricted to the actual
   request window and matched deterministically. The retained
   4,000-pose/14,000-cost workload fell from approximately `5.5-15.7 s` to
   about `0.07 s` without weakening the `5.0 s` timeout.
2. **Verification evidence:** rotation evidence now resets on entry into
   `VERIFY_EXTREMUM`; SEARCH-era maxima cannot classify the new extremum.
3. **Verification timing:** the robust default moved from `10.0` to
   `12.0 s`, enough for two 3-second rotations, a 3-second dwell, and
   operational margin.
4. **Readiness/evidence semantics:** operational readiness, publisher
   ownership, delayed routes, typed stamps, causality, strict finite JSON,
   collision evidence, and final-zero checks were bound to the existing
   recorder and validator.
5. **Scenario contracts:** controller classification and simulation
   ground truth were separated; the first verification branch and forbidden
   evidence became explicit.

The two Phase 08.1 development probes then showed a mixed result:

- `activation_goal_high` passed
  `SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD`;
- `activation_fill_create` created a fill in about `0.09 s`, completed an
  `8.714 s` pure-repulsion escape, then orbited during recenter for 30 seconds
  and entered `FAILSAFE`.

Phase 08.2 corrected only recenter direction selection. Hard wall/fill safety
remained eligibility; center-distance reduction became the recenter
preference. The sealed seed-8304 probe passed:

```text
fills:                       1
escape attempts/successes:   1/1
escape duration:             7.532641327 s
recenter duration:           8.610255022 s
terminal state:              SEARCH
collision:                   false
final goal distance:         0.277956 m
```

This was a real, valuable recovery result, but only one development case.

## Acceptance restarts: v3, V4, and V5

### V3

V3 created a fresh cleartext precommitted population, aggregate-field ground
truth, fixed identities/seeds, stage-order enforcement, collision and
completeness gates, and the full 120-slot workflow.

The successive retained lineages exposed infrastructure and behavior in
order:

- **V3A:** contact-control instrumentation contaminated the intended
  controller behavior;
- **V3B:** one valid direct-path behavioral failure was retained;
- **V3C:** a prelaunch boundary observer used the wrong ROS executor context;
- **V3D:** the correction passed qualification and launched visible Gazebo,
  but default rclpy SIGINT handling invalidated the recorder context before
  readiness-false, final-zero, bag finalization, and completeness validation.

V3D's bag was healthy—`400,131` messages over `190.097876649 s`—but the run
was infrastructure-invalid. No valid activation retry was allowed.

### V4

V4 made recorder shutdown signal-safe, gave graceful scenario completion a
separate finalization allowance, cleaned nested descendants, and improved
causal evidence scoping. The corrected pass-eligible root qualified.

Its first visible activation then followed:

```text
SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD
```

It safely reached the aggregate optimum at `0.096979 m`, with complete
recording, cleanup, final-zero, and no collision. It nevertheless failed the
predeclared activation responsibility because that slot required a fill,
escape, recenter, second search, and final goal. A safe direct goal was not
relabeled as proof of the unexercised robustness branch.

### V5

V5 declared only two- and three-light cases and precomputed a lower-output
basin between start and global. Eight visible Gazebo activation runs all
recorded and cleaned up successfully, but the live GESC path curved around
the intended blocker. First fills were `1.2624-1.5782 m` from it, outside the
required `0.35 m` encounter radius.

Four cases did execute the full fill/escape/recenter/goal state path. They
proved that the mechanism worked in Gazebo, but at the wrong basin. The
static straight-line route-barrier proof was therefore rejected as an
insufficient model of the actual GESC trajectory.

## V6: the known-good two-light ratio emerged

V6 narrowed the claim to exactly two lights, unchanged zero-yaw/full-rotation
GESC startup, and no affine escape assist. It swept the local light against a
fixed `1600` global input:

| Case | Local/global ratio | Local input | Primary recovery | Full-record gate |
|---|---:|---:|---|---|
| H25 | `0.25` | `400` | pass | pass |
| H50 | `0.50` | `800` | fail | fail |
| H70 | `0.70` | `1120` | fail | fail |
| H85 | `0.85` | `1360` | pass | fail after a later fill rejection/failsafe |

H25 was the only eligible ratio. Its three fixed repeats produced:

```text
seed 17101: full contract pass
seed 17102: convergence/fill at global, then failsafe
seed 17103: local recovery pass, later fill rejection/failsafe
```

The fixed full-record repeatability gate was `1/3`, below `2/3`. The
first-recovery-episode result was `2/3`. V6 proved the mechanism can work and
identified `400/1600` as the best tested ratio; it did not prove stable
multi-cycle operation.

## Phase 08.7 design

Phase 08.7 replaced the centered validation geometry only for new scenarios:

```text
room bounds:        [-0.25, 3.75] x [-0.25, 3.75] m
room center:        (1.75, 1.75) m
robot start:        (0.0, 0.0), yaw 0
global source:      (3.5, 3.5)
local region:       radius 1.0-2.0 m, angle 0-90 degrees
wall margin:        0.20 m
two-light inputs:   local 400, global 1600
```

The old world and every historical case key remained unchanged. The new
world has physical inner wall faces exactly at the declared bounds.

Phase 08.7 also introduced two important result contracts.

### Known topology and fill cardinality

For the two-light cases:

```text
declared locals:             1
declared globals:            1
gaussian_fill_max_fills:     1
required unique local fills: 1
```

Fill cardinality is based on unique accepted typed cluster identity, not raw
message count. Revisions, repeats, supersession, and merging do not create
extra local minima. A fill at the global, a missing fill, or an extra unique
fill fails the contract.

### Staged result

Stage A is the local Gaussian recovery:

```text
SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE -> RECENTER -> SEARCH
```

Stage B begins only after Stage A and exact cardinality pass. It requires one
valid noninterpolated odometry sample inside the scenario's global-proximity
radius, followed by graceful simulation shutdown. Stage A remains reportable
if Stage B later fails.

The initial approved radius was `0.35 m`. M2.3 adopted an evidence-backed
`1.20 m` operator-equivalent simulation boundary; M3 deliberately used a
stricter `1.00 m` gate. `GOAL_REACHED`, `GOAL_HOLD`, dwell, and post-arrival
stability are not required.

## Phase 08.7 execution chronology

| Milestone | Correction or question | Retained result |
|---|---|---|
| M1 | Add shifted world/profile, known topology, exact fill cardinality, staged reporting, and post-recovery stop without running Gazebo | **Qualified.** `107 passed, 1 skipped`; focused regression `282 passed, 1 skipped, 1 deselected`; three-package build and nonexecuting installed launch passed. |
| M2 | First visible geometry probe | Geometry, recording, Stage A, and one-fill passed. Stage B failed at `2.204118 m`; a later fill rejection/failsafe closed the run. |
| M2.1 | Integrate detector lifecycle, topology-aware recovery, affine guidance, and relaxed stop | Infrastructure passed, but no convergence confirmation occurred; no fill or Stage A. Fixed attempt failed. |
| M2.2 | Calibrate detector efficiency from retained evidence | Detector and one-fill passed. The recovery topology happened, but the Stage A reporter missed it, so Stage B never armed; later east-wall contact occurred. Fixed attempt failed. |
| M2.3 | Accept assisted Stage A evidence and use the `1.20 m` operator-equivalent stop | **Passed.** Stage A, one-fill, Stage B at `1.199192 m`, collision, recording, final-zero, and cleanup all passed. |
| M3 | Five-position spatial suite with a stricter `1.00 m` primary arrival | **Failed 1/5.** Stage A `2/5`; exact fill `4/5`; `1.20 m` approach `2/5`; primary Stage B `1/5`. Failures included one-sample detector floor, wall contact after approach, wrong local association, and recenter timeout. |
| M4 | Recoverable navigation, trap-based Stage A, and two-light readiness | Robot behavior passed Stage A/Stage B at `1.199229 m`, but merged `/joint_states` stamps from two legitimate publishers failed the old single-stream timestamp model. Formal evidence failure. |
| M4.1 | Model multi-publisher timestamp evidence without raising global tolerance | Evidence correction passed. Fresh probe passed Stage A and all integrity gates but looped after recovery; best Stage B distance `2.399676 m`. |
| M4.2 | Add post-recovery progress/liveness epochs, search-history reset, safer fallback, and an independent Stage B budget | Behavior passed Stage B at `1.198171 m`. Formal evidence failed because two new supervisor configuration events were not attributed to their producer. |
| M4.3 | Correct AlgorithmEvent producer attribution only | Visible probe passed. The fixed eight-case suite then failed `6/8`: one corner fill had no fixed-lookahead recenter candidate; one post-recovery safe direction maximized fill clearance while pointing away from the global route. |
| M4.4 | Adaptive recenter lookahead and source-led handoff before assistance | Visible probe passed. Eight-case suite failed `5/8`, with one startup unavailable. The corner defect was corrected; remaining failures were an exact reversal of useful source-led motion, an unreserved Stage B budget, and a lost controller-load response. |
| M4.5 | Anti-reversal bypass, fixed `480+120 s` staged budgets, and idempotent controller-load recovery | Infrastructure and Stage A passed. Trigger threshold did not arm (`-0.841` versus `-0.90`); fallback reversed useful progress. Stage B ended at `3.628273 m`. |
| M4.6 | Calibrate the trigger to `-0.80` using retained evidence | Trigger and hard-safe nonreversing tangent worked. Guidance released at fixed clearance before source progress or affine taper completion; best Stage B distance `2.617347 m`. |
| M4.7 | Dynamically reselect a source-resume corridor and retain affine/liveness until progress is proved | The fresh trajectory produced a global-opposing source direction, so the reversal detector correctly did not arm and the new corridor was not exercised. Best Stage B distance `2.744859 m`. |
| M4.8 | Re-run every historically behavior-successful Phase 08.7 case definition once, without tuning or retry | **Met its narrow observation:** `13/17` formal, `14/17` behavioral; `17/17` collision/forbidden, final-zero, cleanup, and SQLite integrity. |

## What M4.3-M4.7 taught about the remaining navigation problem

The late failures were not one generic “wall failsafe” problem.

M4.3 did expose one overly conservative corner interaction: a fixed `0.50 m`
lookahead found no wall/fill-safe candidate even though a shorter safe
segment existed. M4.4's adaptive lookahead corrected that case. After that,
the dominant failures changed:

- a clearance-first safe direction could oppose the useful source-led
  trajectory;
- a tangent could be hard-safe but make zero source progress;
- assistance could release at fill clearance before affine taper and
  liveness had completed;
- the measured source direction itself could vary enough between same-seed
  runs to point toward or away from the global;
- convergence confirmation could miss one of three required candidates,
  preventing Stage A before recovery logic even began;
- fixed total run time could leave too little time after late Stage A until
  staged `480+120 s` budgets were implemented.

M4.5-M4.7 corrected increasingly narrow pieces of that topology but did not
produce a passing fresh radius-2 visible probe. M4.7's new corridor remains
source-qualified but not empirically exercised because its one fixed run
never armed the prerequisite reversal detector.

The evidence therefore does not support disabling collision or physical-room
protection. In the M4.6 and M4.7 failures the robot remained well inside the
room, had no collision, no in-readiness failsafe, and received the full
Stage B budget. Their best distances of `2.617 m` and `2.745 m` would not be
rescued by a slightly looser wall margin or arrival radius.

## Safety and stop conditions that were legitimately relaxed

Phase 08 did remove several conditions that were unnecessarily strict while
retaining actual safety:

- the shifted corner-origin profile uses a `0.20 m` controller wall margin
  instead of the historical `0.35 m`, because the fixed start/global points
  are only `0.25 m` from their nearest physical walls;
- wall-margin pressure while still inside the physical room becomes
  zero-translation plus rotation/replanning where recoverable, rather than an
  immediate failsafe;
- adaptive recenter shortens its candidate horizon in wall/fill pinches;
- valid low-net-progress loops use bounded direction refresh and at most one
  recoverable recenter before releasing to ordinary search;
- Stage B accepts the first valid proximity sample and requires no goal-hold
  state, dwell, or post-arrival stability;
- a complete independent post-Stage-A time budget is reserved;
- Stage A remains a valid reported subresult even if Stage B fails.

The following remained hard requirements:

- no physical wall-face violation or non-ground collision;
- finite, fresh required inputs and valid controller/graph ownership;
- one and only one `/cmd_vel` controller owner;
- bounded runtime and bounded recovery;
- final zero, final readiness false, complete recording, and scoped cleanup;
- no relabeling or overwriting of failed evidence.

## Final M4.8 reproduction result

M4.8 selected the 17 Phase 08.7 case definitions whose original robot
behavior had passed Stage A, exact fill cardinality, Stage B, collision, and
forbidden-evidence predicates. Every definition ran once with its original
seed, scenario values, GUI/headless mode, and time bounds.

```text
formal combined pass:             13/17
behavioral pass:                  14/17
behavioral failure:                3/17
Stage A:                          16/17
exact one-fill cardinality:       16/17
Stage B overall:                  14 pass, 2 fail, 1 unavailable
Stage B after completed Stage A:  14/16
recording completeness:           16/17
collision/forbidden evidence:     17/17
final command zero:               17/17
cleanup:                          17/17
SQLite quick_check:               17/17
```

Groupings:

```text
visible GUI:             4/5 formal,  4/5 behavioral
headless:                9/12 formal, 10/12 behavioral
r=1.5, 45 degrees:      10/12 formal, 11/12 behavioral
r=1.5, 67.5 degrees:     2/2 formal,   2/2 behavioral
r=1.0, 45 degrees:       1/2 formal,   1/2 behavioral
r=2.0, 45 degrees:       0/1 formal,   0/1 behavioral
```

All 16 completed local recoveries followed the direct path. No fresh M4.8
case entered `ESCAPE_ASSIST`. This campaign therefore does not validate the
redesign-assisted path.

The three behavioral disagreements were:

1. **M4 visible:** Stage A completed late and left only `66.810 s`; best
   distance was `2.270542 m`, with no wall/collision/failsafe.
2. **M4.3 radius 2.0:** the full `120.020 s` Stage B budget ended with a live
   sample at `1.221840 m`; ordered shutdown recorded `1.213880 m`, only
   `0.013880 m` outside the gate. It remains a formal failure.
3. **M4.4 radius 1.0:** two convergence candidates occurred but the third
   confirmation never arrived; no fill or Stage A was created. The original
   same-seed run had confirmed, demonstrating detector/continuous-trajectory
   sensitivity.

Seed 18311 was the one evidence-only failure. The controller became active,
but a switch-service response was lost and the spawner later retried an
already-active controller. Behavior, final zero, cleanup, and bag integrity
passed; the strict `console_clean` failure remains formal.

## What exists in the current implementation

The current checkout contains, behind compatible/default-off controls where
appropriate:

- deterministic disturbances and collision/contact evidence;
- sealed scenario identities, stage ordering, manifests, and immutable run
  roots;
- aggregate-field truth and route/basin diagnostics;
- typed detector, fill, state, event, and control observability;
- bounded fill synchronization and causal source/fill association;
- rotation-aware verification and clean search epochs;
- robust recenter selection with adaptive wall/fill handling;
- post-recovery progress, liveness, affine, source-continuity, and
  source-resume mechanisms;
- staged live monitoring and graceful simulation proximity stop;
- signal-safe recording/finalization and idempotent controller-load recovery;
- strict recording, timestamp, ownership, causality, final-zero, cleanup, and
  SQLite integrity validation;
- one additive corner-origin world/profile plus all historical worlds and
  scenarios unchanged.

There is not one universally enabled “affine mode.” V6 explicitly disabled
affine escape assistance. Later M4.x profiles added opt-in post-recovery
affine and supervisor assistance. All final M4.8 local recoveries were direct
and did not use `ESCAPE_ASSIST`. The `legacy` profile remains selectable and
the default-compatible behavior is preserved.

## What is and is not ready

| Question | Phase 08 answer |
|---|---|
| Can the Gaussian local-recovery mechanism work in Gazebo? | **Yes.** It was observed repeatedly, including `16/17` Stage A passes in M4.8. |
| Is the two-light `400/1600` condition useful as a known-good test? | **Yes.** It produced `13/17` formal and `14/17` behavioral M4.8 passes. |
| Is broad two-light spatial robustness proven? | **No.** Prospective M3, M4.3, and M4.4 suite gates failed. |
| Is radius-2 behavior reliable? | **No.** It remained a near miss or clear post-recovery failure depending on profile. |
| Is three-light behavior proven? | **No.** The optional Phase 08.7 three-light probe never ran. |
| Is stable full-record multi-cycle behavior proven? | **No.** V6 failed its `2/3` full-record repeat gate. |
| Is the current profile simulation-ready under the original 120-run contract? | **No.** No version entered and passed the 70-case acceptance denominator. |
| Is physical light output calibrated to Gazebo `400/1600`? | **No.** Those are simulator-relative inputs, not a measured lux transfer. |
| Did Phase 08 run physical hardware? | **No.** |

## Recommended Phase 09 starting point

This section is a proposal for a separately reviewed Phase 09 Plan. It is not
authorization to move hardware.

Start with exactly two lights and reproduce the most stable, physically
simple condition:

```text
inner clear room:      4.0 m x 4.0 m
robot center:          (0.25, 0.25) m from the southwest inner-wall corner
robot yaw:             east / 0 rad
primary local:         (1.3107, 1.3107) m from the southwest corner
                       equivalent to r=1.5 m, 45 degrees from robot
global:                (3.75, 3.75) m from the southwest corner
relative light target: local:global = 1:4
```

If the primary setup is repeatable, a secondary two-light layout can use:

```text
secondary local:       (0.8240, 1.6358) m from the southwest corner
                       equivalent to r=1.5 m, 67.5 degrees from robot
```

The simulator values `400/1600` should not be copied as if they were
calibrated physical lumens. Use identical repeatable AC-powered lights and
calibrate an ambient-subtracted sensor response or lux ratio at equal
geometry. A nominal 400-lumen-class local and 1600-lumen-class global can be
a starting hardware choice, but the measured `1:4` response is the relevant
target.

The first physical sequence should be small:

1. inventory the actual TurtleBot3 launch, topics, adapters, sensor height,
   emergency-stop path, and recorder in a Phase 09 Plan;
2. perform static light/ambient calibration with no robot motion;
3. run three primary 45-degree repeats;
4. only if those are operationally sound, run two 67.5-degree repeats;
5. defer three-light work until the two-light physical path is understood.

Use the exact known-good profile chosen by the Phase 09 Plan rather than
combining unrelated M4.5-M4.7 switches. The M4.4 radius-1.5 family is the
strongest current candidate: its selected 45/67.5-degree M4.8 subset passed
all five fresh formal reproductions.

## Physical termination policy

**THE SIMULATION `1.20 m` / `1.00 m` AUTOMATIC PROXIMITY STOP MUST NOT BE
ENABLED IN PHYSICAL TESTING.**

For physical operation:

- global distance is diagnostic only;
- the robot continues operating until the human operator judges it
  sufficiently close;
- the operator presses `Ctrl+C`;
- `Ctrl+C` must use the ordered shutdown path: readiness false, stop request,
  final-zero publication/verification, bag finalization, and scoped cleanup.

There is no Phase 08 requirement that the physical robot stop automatically
at `1.2 m`, `1.0 m`, `0.35 m`, or any other distance. This policy also avoids
turning the room's global-light wall placement into an artificial automatic
termination constraint.

## Remaining risks for Phase 09

- Same-seed Gazebo runs are not bitwise trajectory-identical; detector
  confirmation and handoff geometry can change.
- The final 17-case set is evidence-selected, so its pass rate overstates what
  should be expected from an unseen spatial population.
- The physical sensor/light transfer function, ambient light, wall
  reflections, lamp geometry, and rotating-sensor height are uncalibrated.
- The declared fill topology covers direct overlapping modeled light fields;
  it does not prove robustness to arbitrary reflections or unmodeled physical
  extrema.
- The source-resume corridor is source-tested but was not exercised in its
  only M4.7 Gazebo probe.
- The final reproduction campaign did not exercise `ESCAPE_ASSIST`.
- The algorithm can recover locally yet fail to make reliable global
  progress. Stage A and operator-observed arrival must remain separate
  physical outcomes.
- The light-source collision geometry was not an obstacle contract. Physical
  lamp stands and cables must remain outside the drive area.

## Retained evidence index

Primary historical handoffs:

- [Phase 08 v2 handoff](../handoffs/phase_08_handoff.md)
- [Phase 08.1 handoff](../handoffs/phase_08_1_handoff.md)
- [Phase 08.2 handoff](../handoffs/phase_08_2_handoff.md)
- [Phase 08.3 handoff](../handoffs/phase_08_3_handoff.md)
- [Phase 08.4 handoff](../handoffs/phase_08_4_handoff.md)
- [Phase 08.5 handoff](../handoffs/phase_08_5_handoff.md)
- [Phase 08.6 handoff](../handoffs/phase_08_6_handoff.md)

Core terminal reports:

- [V1 failure closeout](phase_08_v1_failure_closeout.md)
- [V2 failure report](phase_08_v2_failure_report.md)
- [V3D failure report](phase_08_v3d_failure_report.md)
- [V4 validation report](phase_08_v4_validation_report.md)
- [V5 validation report](phase_08_v5_validation_report.md)
- [V6 validation report](phase_08_v6_validation_report.md)
- [Phase 08.7 M2 report](phase_08_7_m2_geometry_probe_report.md)
- [Phase 08.7 M2.3 passing report](phase_08_7_m2_3_assisted_recovery_stop_probe_report.md)
- [Phase 08.7 M3 report](phase_08_7_m3_spatial_suite_report.md)
- [Phase 08.7 M4.3 suite report](phase_08_7_m4_3_two_light_suite_report.md)
- [Phase 08.7 M4.4 suite report](phase_08_7_m4_4_two_light_suite_report.md)
- [Phase 08.7 M4.8 reproduction report](phase_08_7_m4_8_success_reproduction_report.md)
- [Phase 08.7 M4.8 manifest](phase_08_7_m4_8_success_reproduction_manifest.json)

Major retained external roots:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_2_recenter
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3c
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3d
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2b
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5b
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5c
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v6
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_success_reproduction_1
```

The Phase 08.7 milestone reports contain the exact intermediate M2-M4.7
roots. Large artifacts remain outside Git and must not be rerun merely to
recover context.

## Final go/no-go

```text
broad Phase 08 simulation-ready claim:       NO-GO
simulation-ready tag:                         NOT CREATED
resume or relabel a failed experiment:        PROHIBITED
three-light readiness claim:                  NO-GO
automatic physical global-distance stop:      PROHIBITED
Phase 09 planning and hardware inventory:     GO, after explicit request
Phase 09 physical motion:                     REQUIRES A SEPARATE REVIEWED
                                               PLAN AND USER AUTHORIZATION
initial Phase 09 scientific focus:             TWO LIGHTS, 1:4 RESPONSE,
                                               MANUAL CTRL+C
```

Phase 08's correct final interpretation is neither “nothing worked” nor
“simulation is solved.” The mechanism is real, instrumented, and repeatable
under a useful subset of two-light conditions. The broad robustness claim
failed, and the remaining variability is concentrated in detector
confirmation and post-recovery global routing rather than a general need to
remove wall or collision protection.
