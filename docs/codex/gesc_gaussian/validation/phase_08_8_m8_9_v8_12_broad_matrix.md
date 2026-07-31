# Phase 08.8 M8.9 v8.12 Broad Matrix

Date: 2026-07-31
Committed dispatch boundary: `dd2185d`
Scenario: `phase08_v8_12_broad_matrix.yaml`
First fixed case: `v8_12_matrix_r1p25_a45_ratio1to3_20031`
First fixed seed: `20031`
Profile: `robust_gaussian_v1`

## Disposition

**FORMAL FAIL — THE FIRST FIXED CASE PASSED 13/14 PREDICATES AND COMPLETED
THE SCIENTIFIC LOCAL-RECOVERY-TO-GLOBAL BEHAVIOR, BUT THE FROZEN DIRECT-EXIT
ALIGNMENT PREDICATE FAILED. THE SERIAL SUITE STOPPED AS REQUIRED; SEEDS
`20032..20034` WERE NOT DISPATCHED, AND SEED `20031` WAS NOT RETRIED.**

Seed `20031` found and characterized candidate one, created exactly one valid
typed fill, selected the new `interior_farthest` approach anchor, escaped by
the direct-repulse branch, returned to ordinary `SEARCH`, strictly ranked
candidate two from raw rotational cost, entered `GOAL_HOLD`, and triggered
the first valid evaluator-only global-proximity stop `0.127754 m` from the
declared global. Recording, final zero, readiness false, SQLite integrity,
cleanup, and one-time analysis all completed.

The sole formal failure is preserved exactly:

```text
escape_command_ownership:
  direct measured fill-to-exit alignment is below 0.80
```

The measured alignment was `0.735563`, or `42.6452 degrees` from the initial
selected direction. The frozen `0.80` dot-product threshold admits at most
`36.8699 degrees`; the miss was `0.064438` in dot product or `5.7753 degrees`.
No acceptance gate is weakened or reclassified in this report.

This result closes v8.12 under its first-failure stop condition. It does not
authorize a retry, in-place tuning, the remaining matrix seeds, a v8.13
iteration, or a varied-layout/intensity robustness claim.

## Frozen dispatch and retained evidence

```text
dispatch commit:
  dd2185dba1b9e1f979a72cf1b5b4a960912ee35d
installed scenario:
  /tmp/phase08_8_v8_12_release_qual.HnEptF/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/phase08_v8_12_broad_matrix.yaml
installed/source SHA-256:
  311667e8c8d330732ea32c894bb78fed43b63cd23ef86f486ca25c86fe727bdc
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
  phase08_8_12_broad_matrix/scenario_summaries/
  20260731T233137289914Z_phase08_v8_12_broad_matrix.yaml
SHA-256:
  01cd46bed898afbd229abd2c0fda6db4d0e70487f6cb7716c4a409aec3182216
started / completed:
  2026-07-31T23:31:37.289914Z / 2026-07-31T23:36:15.858997Z
runner return code / stopped reason:
  1 / run_failure
resolved definitions / dispatched runs:
  4 / 1
```

Exact summary-owned run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_12_broad_matrix/
  2026-07-31/
  20260731T233137972843Z_simulation_phase08_v8_12_broad_matrix-
  v8_12_matrix_r1p25_a45_ratio1to3_20031-robust_gaussia_6efe976a
```

Population accounting:

```text
seed 20031:  dispatched once / formal fail / behavioral objective complete /
             retained / analyzed once / no retry
seed 20032:  not dispatched after first failure
seed 20033:  not dispatched after first failure
seed 20034:  not dispatched after first failure
```

The recorder captured clean commit `dd2185d`, `dirty: false`, and no
untracked paths. Retained logs are:

```text
/tmp/phase08_8_v8_12_matrix_dispatch.log
SHA-256:
  cb8d5400920e9c794d856e5e914ee040e2104faa1321d34838bf4926e2b3db7f
/tmp/phase08_8_v8_12_matrix_seed20031_analysis.log
SHA-256:
  f0a9b3d73b6ba8dc8574afb008694a07e07f899458c205b8d600f4c674b1c8fc
```

## Behavioral result

The complete controller path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Stage A and fill evidence:

```text
Stage A completion:                  107.209 sim s
first convergence source time:       75.700 sim s
first convergence point:             (0.926605, 0.792475) m
fill center:                         (1.047125, 0.797401) m
fill-to-convergence:                  0.120621 m
created / typed / active fills:      1 / 1 / 1
unassigned fills:                    none
escape branch:                       direct_repulse
escape duration:                     22.151666 s
escape successes / failures:         1 / 0
stall / assist / timeout / failsafe: false / false / false / false
```

The v8.12 fallback was exercised:

```text
approach anchor mode / value:        interior_farthest / 1
minimum displacement:                0.500000 m
measured displacement:               1.318198 m
anchor:                               (0.000063, -0.003415) m
anchor source time / history age:     3.400000 / 81.600000 s
frozen fill exit radius:              1.366771 m
selected direction:                   (0.794313, 0.607509)
```

Direct-repulse evidence before the alignment check was substantial:

```text
repulse state samples:               442
raw GESC control samples:            2,856
supervisor zero-command samples:     442
nonzero GESC samples:                2,856
mature radial-progress samples:      382
minimum mature radial progress:      0.133830 m
maximum mature radial progress:      0.214764 m
maximum radial distance:             1.425083 m
```

The robot exceeded the `1.366771 m` frozen exit radius, returned to `SEARCH`,
and ordinary GESC then carried it to candidate two. Candidate ranking was
strict:

```text
candidate-one estimate:              -0.9586415534
candidate-one interval:              [-1.3183251413, -0.5989579654]
candidate-two upper bound:            -3.8372093023
strict separation margin:              2.5188841610
candidate ordinal / known count:       2 / 2
invalid ranked-goal events:            0
```

Stage B then passed:

```text
proximity sample time:               236.919 sim s
post-Stage-A elapsed time:           129.710 s
sample position:                     (3.562950, 3.611168) m
sample global distance:              0.127754 m
proximity radius:                    0.500000 m
interpolation used:                  false
graceful global-proximity stop:      true
final position:                      (3.562918, 3.611149) m
final global distance:               0.127721 m
```

The coordinate is evaluator-only. The controller receives no declared source
position, role, intensity, topology solution, or global proximity. Physical
arrival remains manual operator `Ctrl+C`.

## Formal result and alignment diagnosis

Formal classification:

```text
classification:                     failed
formal predicates:                  13/14 PASS
infrastructure status:              completed
terminal state:                     GOAL_HOLD
Stage A / Stage B:                  PASS / PASS
fill cardinality:                   PASS
controller ranked goal:             PASS
ground-truth goal:                  PASS
recording / cleanup:                PASS / PASS
sole failed predicate:              escape_command_ownership
```

The direct-branch evaluator freezes the approach direction at
`ESCAPE_STARTED`. At the first returned-`SEARCH` boundary it selects the
nearest measured odometry sample, forms the vector from fill center to that
exit pose, and requires the normalized dot product with the frozen direction
to be at least `0.80`.

For seed `20031`:

```text
fill center:                        (1.0471251354, 0.7974014064) m
selected direction:                (0.7943130917, 0.6075086109)
SEARCH boundary bag stamp:          1785540810002364859 ns
nearest odometry bag stamp:         1785540810009579454 ns
nearest stamp difference:           0.007214592 s
measured exit pose:                 (2.4804077980, 0.6660631401) m
fill-to-exit distance:              1.4392876471 m
frozen exit radius:                 1.3667708294 m
fill-to-exit alignment:             0.7355625246
required alignment:                 0.8000000000
alignment shortfall:                0.0644374754
measured direction angle:           42.6452 degrees
maximum admitted angle:             36.8699 degrees
angle excess:                        5.7753 degrees
```

This is a frozen evidence-contract failure even though the scientific motion
objective completed. The direct branch is ordinary GESC operating on raw,
Gaussian, and affine terms; it is not a straight-line supervisor command.
Consequently, its measured trajectory can curve while still making bounded
outward progress and clearing the fill. Here the robot cleared the radius,
returned to ordinary search, reached and ranked candidate two, and stopped
near the global. The `0.80` direction gate therefore rejected a successful
curved direct exit.

That diagnosis does not turn the result into a formal pass. Any future change
from initial-direction alignment to an evidence contract based on monotonic
radial progress, exit-radius clearance, causal state/command ownership, and
clean returned-search authority would require a separately authorized future
phase and fresh scenarios. It is not made in v8.12.

## Recording, shutdown, analysis, and plots

```text
record process return code / timeout:  0 / false
recording complete:                    true
authoritative completeness:            PASS
fresh Phase 05 validation:             PASS
stored Phase 05 validation:            PASS
final command zero:                    PASS
final readiness false:                 PASS
cleanup:                               PASS
remaining nodes / processes:           none / none
SQLite PRAGMA quick_check:             ok
analysis status / failures:            partial / []
plots:                                 9/9
path length:                           13.479140 m
controller success metric:             true
raw bag SHA-256:
  9ccef857ebfba6e762f0f26ef206c1b7906b4a7f8fd385f589d77b5817421ca8
```

The analyzer's `partial` status is unrelated to the formal alignment failure.
One optional generic `state_durations` metric rejected one state-sampling gap
over its `0.150 s` bound. Critical inputs, scientific metrics, stored and
fresh Phase 05 validation, applicability integrity, and all nine plots are
present; `analysis_failures` and `recording_failures` are empty. The analyzer
was invoked exactly once.

Primary artifact hashes:

| Artifact | SHA-256 |
|---|---|
| `scenario_result.yaml` | `0ec6110dbb8021caaf4f836288d6804d8c4d705c8ed90df2e4ba5612a1da0c7b` |
| `completeness.json` | `58e3adf822c7813f31d7efe311d93890be0ab5c3718234cfe85a5884201bebba` |
| `metadata.yaml` | `d9cc5a7dca93a6e14d35f9dd156d249629d0644bc150ad952548028b63f2316c` |
| `analysis/phase07/analysis_completeness.json` | `f8fe6b9fcd773086b6ce352c535fb6214c5051827d375725b795f7ef3d92917c` |
| `analysis/phase07/summary_metrics.json` | `087d69dc3d2b023f132be6b4ab3185b917a6c5c0020ce5e0c7eb57abc0cf6456` |

All plot paths are under `analysis/phase07/plots/` in the exact run:

| Plot | SHA-256 |
|---|---|
| `candidate_ranking.png` | `b50deb2e396b2c14a3bb6bc8507c09b361011bcae7581b44e7a9f55c30f31631` |
| `command_saturation.png` | `0a5cb0595560ce1f2e310cdb82496ce3a78ecf92bb5a40e99e6e097cbbac6893` |
| `components.png` | `c3101471f1e2af39f367f0e2cd83006fec3bce612ed038e3e85381b54fdd6e4a` |
| `cost.png` | `09228ed72e35a1d954165e098a47e71df1f3df18875405bf67b7cd629eddcd6d` |
| `gaussian_history.png` | `533a697bc3b8478c90d441f750eb06615be57c619b89cb289c33250fdecd1278` |
| `radial_escape.png` | `1068217d12ee0585bd8bf1e773b408d0476598d7161a99e81600009bcb296ee8` |
| `state_events.png` | `9f72b929eb4684f78e4796d3151fee81b67f7a19d69a52c9390ae1272cb54bd9` |
| `trajectory_sources_fills.png` | `ccca5ca6e500cb666428dac191666f3cceffb125ce20ac3527accaa93cce1ebb` |
| `weights.png` | `16e2f50cd8f9cf0a789dbd7596e835886ef4a46db02b6a083f88bb2e6bb555bc` |

Visual inspection of trajectory, radial escape, state events, candidate
ranking, and cost confirms the origin-to-local approach, one fill, direct
outward departure, curved transit to candidate two, strict raw-cost
separation, and final orbit near the global. No wall or collision behavior
was involved.

## Terminal v8.12 boundary

V8.12 produced:

```text
visible seed 20001:                 1/1 formal pass
matrix seed 20031:                  0/1 formal pass, 1/1 scientific behavior
matrix seeds 20032..20034:          not dispatched
v8.12 dispatched total:             1/2 formal, 2/2 scientific local-to-global
recording/final-zero/cleanup:        2/2
one-time analyses / plots:           2 / 18
```

The visible and matrix results are separate fixed runs, not a population
claim. The four-case matrix gate is `0/1` among dispatched cases and not met;
the intended `1:5` cases and alternate placements were never executed.

No Gazebo, scenario runner, recorder, analyzer, rosbag recorder, or physical
process remains active. V8.12 is closed, and no v8.13 will be created under
the current Phase 08.8 goal. The next permitted work is a separately planned
and authorized Phase 09 boundary.
