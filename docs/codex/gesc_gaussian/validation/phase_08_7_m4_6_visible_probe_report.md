# Phase 08.7 M4.6 visible-probe report

Date: 2026-07-30
Result: FAIL
Infrastructure: PASS
Behavioral gate: Stage B FAIL
Conditional suite: NOT RUN

## Immutable attempt

The one predeclared M4.6 visible attempt ran once on ROS domain `166`:

```text
suite: phase08_v7_m4_6_visible_probe
case:  v7_m4_6_probe_r2p0_a45_h25_18508
seed:  18508
key:   0adae0a552ae5f715240dcc22d1478e710711e8e82429e6752daa7c45f6045a4
```

The run started at `2026-07-30T18:15:54.073631Z` and completed at
`2026-07-30T18:21:26.298012Z`. The outer timeout did not fire. The recorder
returned `0`; the runner returned `1` because the combined behavioral gate
failed.

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_6_probe/
  2026-07-30/
  20260730T181555011761Z_simulation_phase08_v7_m4_6_visible_probe-
  v7_m4_6_probe_r2p0_a45_h25_18508-robust_gaussian_v_0a93dbb1
```

The installed scenario definition used at runtime is byte-identical to the
qualified source input:

```text
deb08439f285a1bcff7e7b5fe763acbf095e7175d995367c626f9d83d7b30e11
```

No retry, in-run parameter change, headless-suite case, three-light case,
Phase 09 action, physical action, or hardware action occurred.

## Gate result

```text
controller startup and readiness: PASS
recording completeness:           PASS
cleanup:                          PASS
collision expectation:            PASS, no collision
forbidden states/events:           PASS, none in readiness
final zero/readiness false:        PASS
required recovery path/events:     PASS
Stage A local recovery:            PASS, 1 episode
unique fill cardinality:           PASS, exactly 1
Stage A time budget:               PASS
complete Stage B opportunity:      PASS, 120.020 s observed
Stage B global proximity:          FAIL
non-gating 1.00 m diagnostic:      FAIL
combined result:                   FAIL
```

Stage A completed at simulation time `152.814 s`. The full Stage B window
ended at `272.834 s`, position
`(1.6518105957, 1.6165048946) m`, distance `2.6388175166 m` from the
declared global. The final recorded position was
`(1.6582865378, 1.6141363540) m`, distance `2.6359799256 m`.

There were `3534` valid post-Stage-A noninterpolated odometry samples and
zero invalid samples. None entered the unchanged primary `1.20 m` radius or
the non-gating `1.00 m` radius. The best Stage B sample was:

```text
simulation time: 225.336 s
position:        (1.7009517630, 1.5989658704) m
global distance:  2.6173470005 m
```

## What M4.6 corrected

M4.6 successfully corrected the M4.5 trigger-calibration miss. The live
source-led handoff began at:

```text
simulation time: 152.700 s
anchor:          (1.2274432561, 1.4964333762) m
fill center:     (1.8189935808, 1.7649913445) m
fill distance:    0.6496577321 m
```

At `164.700 s`, the explicit `-0.80` detector armed:

```text
source direction:             (0.9909899820, 0.1339360130)
source displacement:           0.1147496923 m
radial/source dot:            -0.9383691118
configured threshold:         -0.80
bypass clearance target:       0.7086747487 m
```

This proves the detector, scenario-to-launch binding, supervisor
integration, event reporting, and retained threshold all executed as
qualified. The failure is downstream of the detector.

## Failure mechanism

The generic hard-safe selector chose:

```text
selected direction:           (0.1339360130, -0.9909899820)
rotation from source:         -90 degrees
source alignment:              approximately 0.0
affine weight:                 0.50
```

The direction is hard-safe and nonreversing under the M4.6 contract, but it
is tangential rather than source-progressing. At the live arm geometry, the
direct source direction and both `+/-45 degree` candidates initially
intersect the active fill avoidance region. The tangential `-90 degree`
candidate is the only safe candidate in the nonnegative source half-plane.
The generic selector therefore satisfies M4.6 while sending the robot
downward around the fill.

Measured segment evidence:

```text
source-led window, 152.7 -> 164.7 s:
  path:                        0.6970670476 m
  net:                         0.1145706260 m
  global distance change:     -0.0947478903 m
  global-direction alignment:  0.8329592960

bypass, 164.7 -> 172.2 s:
  path:                        0.6492323099 m
  net:                         0.3802099940 m
  displacement:               (0.1306543292, -0.3570561382) m
  global distance change:     +0.1656946276 m
  global-direction alignment: -0.3833255134
```

The bypass completed at `172.200 s` as soon as fixed fill clearance was
observed. At that boundary the supervisor cleared the retained source
direction and safe direction, ended post-recovery guidance, and reduced
affine weight from `0.50` to `0.0`. The release predicate did not require a
source-aligned candidate, positive projected source progress, or global
approach.

After release, ordinary search traveled:

```text
post-bypass path:              5.5220164059 m
post-bypass net displacement:  0.4954968315 m
path efficiency:               0.08973
global distance change:       -0.4617735493 m
```

It repeatedly circulated near the active fill and produced later convergence
candidates, but did not reach the global. Post-recovery liveness monitoring
and affine assistance were no longer active, so they could neither detect
nor correct this low-efficiency ordinary-search orbit.

The observed defect is therefore:

```text
detector:                PASS
threshold calibration:  PASS
hard safety:             PASS
continuity topology:     INCOMPLETE
selector priority:       permits zero-progress tangent
release semantics:       clearance-only and premature
post-release liveness:   absent
affine persistence:      ends at clearance release
combined behavior:       FAIL
```

## What did not cause the failure

This was not a wall-margin, collision-failsafe, physical-room, startup,
recording, fill-cardinality, staged-budget, or global-stop failure.

During Stage B:

```text
x range:                         [1.1608383976, 1.8063755164] m
y range:                         [1.0444790512, 1.7015756466] m
minimum physical-wall clearance:  1.2944790512 m
minimum wall-inset clearance:      1.0944790512 m
```

The robot was nowhere near a wall. No collision, algorithm `TIMEOUT`,
in-readiness `FAILSAFE`, or room-boundary event occurred. Relaxing the
already operator-equivalent `1.20 m` stop cannot convert a best distance of
`2.617 m` into a successful run.

## Supported next correction

A fresh version must correct the selector-to-release handoff, not relax
safety or the global stop. The evidence supports a bounded two-stage
continuity corridor:

1. retain hard fill, room, collision, ownership, and finite-data checks;
2. use a source-continuity-specific selector that ranks source alignment
   before excess clearance while retaining the safe forward half-plane;
3. recompute that selector during the bypass so a tangential direction is
   replaced as soon as a more source-aligned candidate becomes hard-safe;
4. treat fixed fill clearance as a transition into a source-resume leg, not
   as completion of all guidance;
5. require bounded positive projected source progress before releasing
   retained continuity;
6. keep affine assistance and post-recovery liveness active through that
   source-resume leg, with the existing bounded recenter/fallback behavior;
7. preserve default-off behavior, V6, every historical scenario, exact one
   fill, `1.20 m` primary proximity, full staged budgets, final zero, and
   cleanup.

Pure reconstruction at the live geometry shows that the stored source
direction becomes hard-safe after approximately `0.425 m` of the selected
tangential contour, while M4.6 releases earlier at fixed clearance. This
supports dynamic safe-source reacquisition rather than a looser wall,
collision, or global-stop threshold. Any exact progress/alignment values
must be frozen in a fresh reviewed Plan and qualified against the complete
retained M4.4-M4.6 evidence before another Gazebo attempt.

## Standard analysis and integrity

The standard analyzer ran exactly once into `analysis/phase07` and returned:

```text
analysis_status: complete
analysis failures: none
plots:  8
tables: 11
```

Fresh Phase 05 validation passes. Standalone installed `validate_run` also
passes. Read-only SQLite validation returns:

```text
PRAGMA quick_check: ok
messages: 579958
topics: 34
```

## Retained hashes

```text
b746f1083f006b20fed97e9a584ef480b615dac0126027683d21343d1cd6e93c
  visible suite summary
a095e8e1c6046b65cc2d1d45e9cf2ea48d864003f34a555ba4a70ad9e2c323cc
  completeness.json
fe3d5010c39282fdd104345a32680986cd0775d73a51c800ecb700fe7ec63aa2
  scenario_result.yaml
d52be6874dec45810949689b8e0ab0635526cb334fd8f122e492d95ffea2080b
  bag/bag_0.db3
36687623660234baee372a448658965ec31d7c6cc90863ce73f0c18df7c8e79f
  analysis/phase07/analysis_completeness.json
81e9f44683872ba64249c73a80e95e5f6ee3193fc6229f3fc0c11847c25e7268
  analysis/phase07/summary_metrics.json
db0a514252f83ba0b4eab379677bda237a2564fd5040f37bd3865de95589c112
  resolved_scenario.yaml
deb08439f285a1bcff7e7b5fe763acbf095e7175d995367c626f9d83d7b30e11
  scenario_definition.yaml
a095e8e1c6046b65cc2d1d45e9cf2ea48d864003f34a555ba4a70ad9e2c323cc
  /tmp/phase08_7_m4_6_validate_run.json
```

## Stop boundary

M4.6 is closed failed and cannot be retried, overwritten, relabeled, or
counted as a pass. The fixed M4.6 headless suite did not run and its evidence
root remains absent. Cleanup reconfirmed no Gazebo, runner, recorder,
analyzer, rosbag, validator, or matching launch process, and ROS domain
`166` is empty with the CLI daemon disabled.

Any further correction requires a fresh reviewed version, fresh identities,
no-Gazebo qualification, checkpoint, and commit before another simulation.
