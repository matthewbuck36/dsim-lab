# Phase 08.7 M4.5 fixed visible-probe report

## Disposition

**M4.5 fixed visible probe: INFRASTRUCTURE COMPLETE / STAGE A PASS /
EXACT ONE-FILL PASS / STAGE B FAIL / COMBINED FAIL.**

The single committed attempt is retained without retry or in-run change. The
conditional eight-case headless suite did not run and remains blocked.

The attempt used qualified implementation commit `f89e989`, dispatch-record
commit `9714be4`, ROS domain `165`, visible Gazebo, fixed seed `18508`, and
case key:

```text
4058b99c8e404cdc9eea12e3ecabef5a6befc3085dc9f541faaec204745ec1d2
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_5_probe/
  2026-07-30/
  20260730T124849713987Z_simulation_phase08_v7_m4_5_visible_probe-
  v7_m4_5_probe_r2p0_a45_h25_18508-robust_gaussian_v_b36220b0
```

The runner started at `2026-07-30T12:48:48.771600Z`, completed at
`2026-07-30T12:54:25.580679Z`, and returned `1` because the declared
behavioral gate failed. The outer `780 s` timeout did not fire.

## Infrastructure and safety

The idempotent controller helper processed
`joint_state_broadcaster`, then `velocity_controller`. Both loaded,
configured, and activated on their first observed load request; the transient
helper exited cleanly. Recorder preflight passed and motion readiness became
true.

Infrastructure and safety predicates pass:

```text
record process:                  return 0
recording completeness:          48/48 PASS
fresh Phase 05 validation:       PASS
cleanup:                         PASS
SQLite PRAGMA quick_check:       ok
bag messages/topics:             582137 / 34
collision evidence:              available
non-ground collision:            none
forbidden state/event:           none
final command streams zero:      PASS
final readiness false:           PASS
remaining session processes:     none
remaining ROS-domain nodes:      none
```

No wall-margin stop, physical-room violation, collision stop, controller
ownership failure, recorder failure, startup retry, `TIMEOUT` algorithm
event, or `FAILSAFE` occurred.

## Staged behavioral result

The accepted Stage A path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

Stage A completed before its `480 s` bound. Exactly one fill was created,
typed, and active. Its association evidence is:

```text
convergence point:              (1.8195024620, 1.7376361684) m
fill center:                    (1.8117325336, 1.7511796132) m
fill-to-convergence:             0.0156139900 m
convergence-to-local:            0.5185183451 m
convergence-to-global:           2.4351587731 m
support radius:                  0.5086747487 m
avoidance radius:                0.6086747487 m
```

The runner reserved and observed the complete independent Stage B budget:

```text
Stage A live completion sample:  155.119 s
Stage B terminal sample:         275.139 s
elapsed:                         120.020 s
terminal position:              (1.3800558824, 0.5554794317) m
terminal global distance:        3.6282729279 m
valid post-Stage-A samples:      3533
interpolation used:              false
```

No valid recorded sample entered the primary `1.20 m` radius or the
non-gating `1.00 m` diagnostic radius. Stage B and the combined result
therefore fail.

## Root cause

The source-led handoff started at simulation time `155.0 s`:

```text
anchor:                         (1.1809160175, 1.5969815630) m
fill distance:                   0.6493893406 m
global distance:                 2.9999382809 m
```

At the `167.0 s` stalled boundary, the robot was approximately:

```text
position:                       (1.3563818523, 1.5646136279) m
source-led path:                 0.7868994292 m
source-led displacement:         0.1784262940 m
fill distance:                   0.4920885183 m
global distance:                 2.8880476402 m
global-distance change:         -0.1118906407 m
```

The measured displacement was meaningful and reduced global distance, but its
alignment with the radial outward fallback was:

```text
source direction:               ( 0.9834079431, -0.1814078760)
radial outward direction:       (-0.9253430316, -0.3791309456)
dot product:                    -0.8412123478
M4.5 trigger:                   <= -0.90
```

Because `-0.8412123478 > -0.90`, M4.5 did exactly what it declared: it did
not arm the source-continuity bypass and emitted no
`post-recovery source-continuity bypass armed` event. It selected the
unchanged M4.4 radial fallback:

```text
selected direction:             (-0.9252604036, -0.3793325526)
selected/source dot:             -0.8411137950
```

The failure is therefore a trigger-calibration miss, not a failure of the
implemented forward-half-plane selector.

The retained segments show the behavioral consequence:

| Segment | Simulation interval | Path | Net | Global distance start/min/end |
|---|---:|---:|---:|---:|
| source-led | `155.0-167.0 s` | `0.786 m` | `0.178 m` | `3.000/2.888/2.888 m` |
| radial fallback | `167.0-186.8 s` | `1.529 m` | `0.396 m` | `2.888/2.883/3.261 m` |
| refreshed fallback | `186.8-202.4 s` | `1.120 m` | `0.419 m` | `3.261/3.244/3.678 m` |
| recoverable recenter | `202.4-216.8 s` | `0.865 m` | `0.735 m` | `3.678/3.017/3.017 m` |
| guided after recenter | `216.8-275.139 s` | `4.091 m` | `1.281 m` | `3.017/2.998/3.628 m` |

Because the bypass was never armed, its measured continuity constraint was
also not retained across the recoverable recenter. Post-recenter guidance
first selected `(-0.999114, 0.042089)`, whose alignment with the original
source direction was `-0.990177`; the later refresh selected
`(0.143177, -0.989697)`. The robot remained safe but moved away until the
complete Stage B budget expired.

## Cross-case threshold evidence

Read-only reconstruction of every retained M4.4 behavioral source-led window
gives:

| Retained case | Result | radial/source dot |
|---|---:|---:|
| visible central | PASS | `-0.336356` |
| radius 1.0 | PASS | `0.885685` |
| radius 1.5, 45 deg | PASS | `0.201668` |
| radius 1.5, 67.5 deg | PASS | `0.787593` |
| radius 2.0 | FAIL | `-0.999969` |
| repeat 18410 | budget-invalid behavioral FAIL | `0.413417` |
| repeat 18411 | PASS | `0.953112` |
| repeat 18412 | PASS | `-0.192921` |

The fresh M4.5 failure is `-0.841212`. An explicit fresh threshold of
`-0.80` would catch both retained radius-2 reversals while leaving every
retained M4.4 passing case, including repeat `18412`, on its existing path.
It provides `0.0412` alignment margin for the fresh failure.

Pure geometry replay at `-0.80` returns the finite hard-safe
forward-half-plane candidate:

```text
direction:                       (-0.1814078760, -0.9834079431)
source alignment:                 approximately 0.0
radial outward alignment:         0.5407048973
lookahead endpoint:              (1.2656779143, 1.0729096564) m
endpoint fill distance:           0.8707616100 m
required bypass release radius:   0.7086747487 m
```

This is the smallest evidence-supported next correction. It changes no wall,
collision, physical-room, one-fill, ownership, cost, staged-budget, or
`1.20 m` global-proximity rule.

## Standard analysis

The standard analyzer ran exactly once into `analysis/phase07`. It produced
eight plots and eleven tables, with no analysis failures and fresh Phase 05
validation passing. `analysis_status` is `partial` only because one
AlgorithmState gap invalidates generic state-duration metrics and generic
aggregate-target metrics are unavailable. Those limitations do not change
the scenario runner's direct noninterpolated Stage A/Stage B result.

## Retained hashes

```text
c4f7da06667aa57f21c87d51d5a9c3cd1188bd55010dfe94cd39cc7ee6105e99
  visible suite summary
5d39fbcbf68c720ca35eb86a8e8aa2669445a20e42c8ad531ccd7cd0e065fd47
  completeness.json
0256fbce2cb2a302c1d7681febc6f103317d867d6198942b3ab88ebea23694fc
  scenario_result.yaml
dfa0765978f67a4c317edc8e088fe62d29971da0ffb93ec348d5b8ac858f63be
  bag/bag_0.db3
197848518999cf2981007a1baa767ca8c33e0ae144f66a93d298c133ec6d0df7
  analysis/phase07/analysis_completeness.json
caa56a51d65e75fe49721f15d35a89113765db6ee24b03a670955b5c901aa7c9
  analysis/phase07/summary_metrics.json
```

## Stop boundary

M4.5 is closed failed and cannot be retried, overwritten, relabeled, or
counted as a pass. No M4.5 headless-suite, optional three-light, Phase 09, or
physical action occurred. Any correction requires a fresh planned version,
fresh identities, no-Gazebo qualification, checkpoint, and commit before
another simulation.
