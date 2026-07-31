# Phase 08.8 M4 Fixed v8.2 Primary Repeat Gate

Date: 2026-07-30
Scenario: `phase08_v8_2_primary_repeats.yaml`
Profile: `phase08_v8_2_counted_open_field_basin_raw_rank_v1`
Sealed seeds: `19011` through `19020`

## Result

**FIXED GATE FAILED — one of ten cases dispatched, seed `19011` failed
Stage B, and the remaining nine cases were not dispatched.**

The fixed v8.2 population was executed serially and headlessly from the
qualified isolated install. The runner obeyed the precommitted first-failure
rule. Seed `19011` was not retried, no parameter changed after dispatch, and
seeds `19012` through `19020` did not run.

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_2_primary_repeats/
  scenario_summaries/
  20260731T055403171613Z_phase08_v8_2_primary_repeats.yaml
SHA-256:
  d51eb7887ec39becfaf032c2209745da86179524ea0a7d79ff4bc88635974447
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_2_primary_repeats/
  2026-07-31/
  20260731T055404130734Z_simulation_phase08_v8_2_primary_repeats-v8_2_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_d33decfa
```

## Dispatch accounting

```text
resolved population:                 10
dispatched:                           1
formal passes:                        0
formal failures:                      1
not dispatched after first failure:  9
retry count:                          0
runner stop reason:                   run_failure
```

This is not a `0/10` empirical result: only one case ran. It is a failed
ten-consecutive-run gate because the very first fixed member missed.

## Infrastructure and evidence

The failed behavior is not an infrastructure failure:

```text
record process return code: 0
record process timed out:   false
recording complete:         true
authoritative completeness: PASS
final readiness false:      PASS
final commands zero:        PASS
cleanup:                    PASS
remaining nodes:            none
remaining processes:        none
analyze_run status:         partial because behavior failed
analysis failures:          none
recording failures:         none
```

Evidence hashes:

```text
raw bag:
  1a01ae32f0b5b95d229643f186d2447908be8a06071dc61d21143a0578d0392c
completeness.json:
  16beeaa58bee468726374109d6db3389d5a718c4c38f0ce756f9432ae2e41fc8
scenario_result.yaml:
  03ec929dd1762c74da137f34b9922f5711a468a2f0d4afdf9bc7981ff79eb31f
analysis/phase07/analysis_completeness.json:
  24b727b8a70b0b198dbedf81eb7ac97552694c8dab11988dd61359d37e61f8cd
analysis/phase07/summary_metrics.json:
  4cc6705e0220531af956a44b00117a32a80c1f1d813c2afa9a72311471177b21
```

## What passed

The required local-recovery episode completed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
```

```text
Stage A:                       PASS at simulation time 296.710 s
Stage A budget:                360.0 s
created fill clusters:         [1]
active fill clusters:          [1]
fill cardinality:              exactly one
fill-to-convergence distance:  0.178007 m
convergence-to-local distance: 0.246982 m
required ESCAPE_STALLED:       observed
finite outward assist:         completed
escape duration:               26.427079 s
maximum radial progress:       0.284869 m
approximate escape orbit:      1.443680
fill merge or supersession:    none
in-readiness failsafe/timeout: none
```

The first counted candidate retained valid repeated raw evidence:

```text
raw estimate:     -1.572582366887451
MAD:               0.2898819545479434
uncertainty:       0.8696458636438302
lower bound:      -2.4422282305312812
rotation count:    3
decision:          create the one required local fill
```

## What failed

Stage B began after the completed Stage A and consumed its full fixed budget:

```text
Stage B start:                  296.710 s
Stage B stop:                   476.740 s
elapsed:                        180.030 s
controller GOAL_REACHED:       absent
post-recovery global sample:   absent
final position:                (1.035316, 1.490587) m
final global distance:         3.180001 m
terminal state:                SEARCH
```

The post-recovery sequence was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> SEARCH
-> VERIFY_EXTREMUM
-> SEARCH
```

Both later confirmations were spatially associated with the already active
fill. The counted-source supervisor therefore correctly rejected them as
revisits instead of calling either one source two or creating another fill.
The robot never reached and ranked a distinct second candidate.

## Root-cause diagnosis

The retained evidence separates three facts:

1. Candidate classification used repeated complete-rotation minima. Its
   conservative local lower bound was `-2.442228` cost units.
2. The adaptive basin estimator used an eight-second orientation-level raw
   sample window. MAD filtering and the trigger orientation reduced its
   estimated basin depth to the configured `0.02` minimum.
3. The resulting fill was only:

```text
amplitude:       0.10 cost units
sigma major:     0.169558 m
sigma minor:     0.169558 m
support radius:  0.508675 m
exit radius:     1.356466 m
```

The two owners therefore summarized the same directional sensor at
incompatible scales. The fill was a valid typed basin marker, but it was too
weak and narrow to neutralize the old raw attraction after the finite outward
assist ended. Gaussian contribution then decayed, affine guidance was
intentionally disabled, and ordinary GESC returned to the filled local.

The trajectory plot confirms departure followed by return. The components
plot confirms a maximum Gaussian height of only `+0.10` and a zero affine
term. No wall, operating bound, collision check, recenter, or safety failsafe
caused the miss.

This is a detector/fill signal-summary integration defect, not evidence that
the counted-source policy, raw ranking, recorder, cleanup, or local-recovery
state path failed.

## Plots and tables

Plot directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_2_primary_repeats/
  2026-07-31/
  20260731T055404130734Z_simulation_phase08_v8_2_primary_repeats-v8_2_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_d33decfa/
  analysis/phase07/plots/
```

Available plots:

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

Machine-readable tables are under `analysis/phase07/tables/`.

## Gate disposition

The fixed v8.2 primary repeat profile is closed as failed. It is not retried,
and its nine undispatched seeds remain undispatched. The v8.2 secondary and
broad gates are not authorized.

The Plan's broader execution authority permits a separately versioned,
no-Gazebo-qualified correction. That correction must make the accepted
Gaussian fill commensurate with the already retained candidate raw-cost
interval while keeping source coordinates, roles, evaluator geometry, Vicon,
affine guidance, recenter, walls, and route planning outside the controller.
