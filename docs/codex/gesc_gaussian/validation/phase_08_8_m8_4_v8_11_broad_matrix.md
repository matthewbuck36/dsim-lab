# Phase 08.8 M8.4 v8.11 Broad Matrix

Date: 2026-07-31
Committed dispatch boundary: `39b73f9`
Scenario: `phase08_v8_11_broad_matrix.yaml`
First fixed case: `v8_11_matrix_r1p25_a45_ratio1to3_19931`
First fixed seed: `19931`
Profile: `robust_gaussian_v1`

## Disposition

**FAIL — THE FIRST FIXED CASE CREATED EXACTLY ONE VALID FILL BUT ENTERED AN
IMMEDIATE APPROACH-CONTINUITY FAILSAFE BEFORE A VALID ESCAPE INTERVAL. THE
SERIAL SUITE STOPPED AS REQUIRED; SEEDS `19932..19934` WERE NOT DISPATCHED,
AND SEED `19931` WAS NOT RETRIED.**

This is a behavioral acceptance failure with complete infrastructure. The
recording, authoritative completeness, final zero, final readiness false,
cleanup, SQLite integrity, and one-time analysis all completed. The fixed
v8.11 broad-matrix population gate is not met and v8.11 may not claim the
varied-layout/intensity envelope.

The earlier v8.11 secondary result remains a separate `1/1 + 5/5` pass for
its exact fixed layout. This matrix failure does not relabel or erase those
results.

## Frozen dispatch and retained evidence

```text
dispatch commit:
  39b73f947e490febe8b496a37dee767193d64835
installed scenario:
  /tmp/phase08_8_v8_11_release_qual.AdUc5v/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/phase08_v8_11_broad_matrix.yaml
installed/source SHA-256:
  b0ac9ff6582deecb56970d38f0a3f7d08f09aa8518343dd0477ae953d2a04b02
ROS_DOMAIN_ID / ROS_LOCALHOST_ONLY:
  220 / 1
presentation / execution:
  headless Gazebo / serial / stop on first failure
attempts / retries:
  1 / 0
```

Scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_11_broad_matrix/scenario_summaries/
  20260731T215507749994Z_phase08_v8_11_broad_matrix.yaml
SHA-256:
  6504450fbd404bb4adea04a7d29ad92605ddd11a05201ce5d39f1d75335d235d
started / completed:
  2026-07-31T21:55:07.749994Z / 2026-07-31T22:02:16.204028Z
runner return code / stopped reason:
  1 / run_failure
resolved definitions / dispatched runs:
  4 / 1
```

Exact summary-owned run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_broad_matrix/
  2026-07-31/
  20260731T215508693457Z_simulation_phase08_v8_11_broad_matrix-
  v8_11_matrix_r1p25_a45_ratio1to3_19931-robust_gaussia_056336a1
```

```text
seed 19931:  dispatched once / failed / retained / no retry
seed 19932:  not dispatched after first failure
seed 19933:  not dispatched after first failure
seed 19934:  not dispatched after first failure
```

The recorder captured clean commit `39b73f9`, `dirty: false`, and no untracked
paths. Retained logs:

```text
/tmp/phase08_8_v8_11_broad_matrix_dispatch.log
SHA-256:
  f36e8324e5d9d2b07f6a80d628de74139e8ec570e34309c20536715f7fe900d8
/tmp/phase08_8_v8_11_matrix_19931_analysis.log
SHA-256:
  6b5d0e6b8be9125edecfa07bd24ab968afff1d974026a10a96777a4bdf31cce5
```

## Behavioral timeline

The first candidate path was valid through fill creation:

```text
71.4 sim s:  qualified-dwell convergence candidate
77.4 sim s:  convergence confirmed; fill ready
86.5 sim s:  VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL
86.7 sim s:  one robust basin fill created
86.7 sim s:  DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE event emitted
86.7 sim s:  immediate ESCAPE_REPULSE -> FAILSAFE event emitted
360.638 s:   runner's declared Stage A timeout boundary observed
```

The immediate failsafe reason was exact and unambiguous:

```text
open-field escape approach continuity has no pose outside the frozen exit radius
```

No publishable `ESCAPE_REPULSE` state interval or `ESCAPE_STARTED` event
survived the immediate transition. Offline state evidence therefore collapses
to:

```text
SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> FAILSAFE
```

Formal result:

```text
classification:                   failed
formal predicates:                3/14 PASS
passing predicates:               recording, cleanup, fill cardinality
terminal state:                   FAILSAFE
Stage A / Stage B:                FAIL / NOT REACHED
controller ranked goal:           false
final global distance:            3.600589 m
```

The single fill was nevertheless valid:

```text
confirmed convergence:            (0.886418, 0.733648) m
fill center:                       (1.069961, 0.760591) m
fill-to-convergence:               0.185510 m
convergence-to-local diagnostic:   0.150257 m
created / typed / active fills:    1 / 1 / 1
valid design samples:              69
fill amplitude:                    3.987920 raw-cost units
sigma major / minor:               0.506211 / 0.506211 m
support radius:                    1.518634 m
frozen exit radius:                1.366771 m
topology hash:
  da4e64008b2950c93ccbf08e31b6ead65c4fe6cc5791991965b9ceb156006bd6
```

## Root cause

The controller's approach-continuity owner freezes the newest pre-basin pose
strictly outside the runtime fill exit radius and uses its vector toward the
fill center as the continued escape direction. If no historical pose is
outside that radius, `_begin_escape()` returns a failure and the state machine
immediately enters `FAILSAFE`.

For seed `19931`, every available pose was inside:

```text
pre-escape odometry samples checked:        2,536
frozen fill exit radius:                    1.366770829 m
first-pose distance from fill center:       1.312731367 m
maximum historical distance:               1.315565112 m
outside-radius samples:                     0
radius shortfall at farthest sample:        0.051205717 m
farthest-pose -> fill-center unit vector:   (0.814782, 0.579768)
```

The schema-v14 topology preflight admitted the declared source route using
`start_to_local_m = 1.25`, but it did not bind the runtime supervisor
precondition that at least one pose must lie outside the fill designer's
eventual exit radius. The fill radius depends on measured basin data and was
not available to the preflight. This is a detector/fill/topology/supervisor
integration gap, not a failed extremum detector or malformed fill.

Specifically, this failure was not caused by:

- walls, obstacle avoidance, contacts, or collision failsafes; all were out
  of scope or disabled;
- source-count classification; candidate one correctly required a fill;
- fill cardinality; exactly one fill was created and remained active;
- fill geometry validity; every recorded geometry-validity field passed;
- affine assistance being disabled; the frozen profile retained affine
  enablement, but escape authority failed before ordinary escape motion;
- global ranking; candidate two was never reached; or
- recording or process contamination; completeness and cleanup passed.

## Recording, analysis, and plots

```text
record process return code / timeout:  0 / false
recording complete:                    true
authoritative completeness:            PASS
fresh Phase 05 validation:             PASS
final command zero:                    PASS
final readiness false:                 PASS
cleanup:                               PASS
remaining nodes / processes:           none / none
SQLite PRAGMA quick_check:             ok
analysis status / failures:            partial / []
plots:                                 9/9
raw bag SHA-256:
  15a91e7edc924d5bb98c974261e6f31aa67a5c41a1d276a3153f056e415bc901
```

`partial` is the correct analyzer status because no escape interval or goal
exists from which to calculate escape and convergence metrics. It is not an
analysis failure; `analysis_failures` and `recording_failures` are empty.

Artifact hashes:

| Artifact | SHA-256 |
|---|---|
| `scenario_result.yaml` | `d08088db7ec285679dbb64a5fa2bf1d4b17993d987e57c05dd0e6ad5ccc223ae` |
| `completeness.json` | `25161f89316736f75d437bc99167700cc1c88ebf71fe835fb1743b3a84cb31ea` |
| `analysis/phase07/analysis_completeness.json` | `9c236ee1eeb3e867d4b9ff713dbab0dd5d074d88b47a120d8399db4c3c5b622a` |
| `analysis/phase07/summary_metrics.json` | `43d252f0deff010616bde62a58a96612e1fa9a1e93ea119efb21f7a0d06b2ad5` |

Plot hashes; each path is under `analysis/phase07/plots/` in the exact run:

| Plot | SHA-256 |
|---|---|
| `candidate_ranking.png` | `536414c44ed044973a80ab767e5b97134a243c4196d2fa33761bc37412ddf2d1` |
| `command_saturation.png` | `8d35e34c6ce84144e846ad6b930884bee7c46e66832224c76e18429f7defa89d` |
| `components.png` | `2a8b6cb220f50852e12266b645510bcdd4f9e86d26c0c7d58e7da6f8d9c6b55b` |
| `cost.png` | `98c58950f085c9681e63f2cf3bf05b324f91aa87a158b95f61144e843ff96ef5` |
| `gaussian_history.png` | `069b8257c031f00aa0b0ee4c45f077af9b3551b5ef637f70667bf7cdd7462cd0` |
| `radial_escape.png` | `9eaa428edc807e8d5523dab5a2eae23a5adf07b4d74d4ee2f5c7edf5b193fa54` |
| `state_events.png` | `7f0781d3c0bbb9207d952738b02e17fe4399e42be72f1bd837d3493f25638c57` |
| `trajectory_sources_fills.png` | `1758402fbe8e7a39d9e26e40a27ad56e95f1d8004b877adc65ae2a4411224d72` |
| `weights.png` | `24eab4921df7f58d5e9183dd6f660eed85f0b754eafde571938cf07d781e06d2` |

Visual inspection confirms approach and orbit around candidate one, one fill,
an immediate persistent `FAILSAFE`, no escape trajectory, and no candidate-two
evidence. The radial-escape plot correctly reports that no valid escape state
evidence exists.

## Fresh-version correction boundary

V8.11 is closed for the broad matrix. A correction must use a fresh version,
fresh scenarios, and fresh seeds; seed `19931` may not be retried or
reclassified.

The smallest coherent correction is a legacy-default-off supervisor option
that, only when no pose exists outside the fill exit radius, selects the
farthest pre-fill odometry pose as an interior approach anchor if its
displacement is above a frozen meaningful minimum. The direction still
continues the robot's measured approach through the basin; it uses no source,
global, room, Vicon, or evaluator coordinate. Insufficient or degenerate
history must remain a failsafe.

A fresh Plan must also bind and test the integration contract:

1. preserve the original outside-radius anchor path byte-for-byte by default;
2. expose the fallback as one new explicit ROS parameter, default `false`;
3. record whether `outside_radius` or `interior_farthest` evidence was used;
4. require a frozen minimum fallback displacement and positive finite unit
   direction;
5. replay this exact failed history offline and prove it selects
   `(0.814782, 0.579768)` without entering a controller graph;
6. retain negative tests for empty, tiny, nonfinite, and unordered histories;
7. extend topology admission with a minimum start-to-local route length that
   proves a meaningful odometry approach can exist, while leaving the runtime
   fill-radius check authoritative; and
8. qualify code, historical defaults, V6, all prior scenarios, retained bags,
   installed parity, final zero, and inactive runtime before any fresh Gazebo
   dispatch.

No Gazebo, scenario runner, recorder, analyzer, rosbag recorder, or physical
process remains active. Physical stopping remains manual operator `Ctrl+C`.
