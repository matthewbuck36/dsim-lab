# Phase 08.7 M2.2 efficiency-correction probe report

Date: 2026-07-30

## Result

The one fixed M2.2 attempt is retained as **FAIL**.

- infrastructure, recording, validation, final-zero, and cleanup: **PASS**;
- convergence detection at the intended local: **PASS**;
- exact unique fill cardinality: **PASS**;
- local escape, assisted escape, recenter, and resumed search mechanism:
  **OBSERVED**;
- formal Stage A local-recovery predicate: **FAIL** because the reporter only
  accepts the direct recovery topology and does not accept the observed legal
  assisted topology;
- formal Stage B post-recovery global proximity: **FAIL** because the false
  Stage A result prevented the live monitor from arming and the frozen
  `0.60 m` boundary was not reached before a wall-margin failsafe;
- collision expectation: **FAIL** because east-wall contact occurred after the
  missed stop boundary;
- combined behavioral result: **FAIL**.

M2.2 is not retried or relabeled. It proves that the M2.2 detector correction
worked and that post-recovery affine assistance was active, while exposing a
detector/topology/supervisor/reporting contract mismatch and an
operator-equivalent stop radius that was too strict for the observed safe
approach.

## Frozen input

```text
qualified commit:
  4fdc43fede08e0abdb69e799e1273329ed01129f
suite:
  phase08_v7_m2_2_efficiency_correction_probe
experiment version:
  phase08-v7-m2.2
case:
  v7_m2_2_diagonal_r1p5_h25_18001
case key:
  5078f6eff97d05419af1c59452fba15fb31b34c496e80f5ab3063ac091520e90
scenario SHA-256:
  1f11448b37ef8fbfb146124a0141d91d3404ee614d6d33e3a30f58aa0a179439
seed:
  18001
maximum fills:
  1
detector:
  SEARCH-only, minimum path 0.20 m, maximum efficiency 0.50
post-recovery affine:
  enabled, maximum age 60.0 s, gain 0.5
post-Stage-A global proximity:
  0.60 m
```

The installed scenario and source hashes matched before dispatch. The run
metadata identifies the exact qualified commit. Its `dirty=true` field is the
predeclared live-status dispatch entry made after that commit; there was no
algorithm or scenario-byte change.

## Invocation and retained run

Exactly one visible-Gazebo attempt was dispatched on ROS domain `92`:

```bash
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m2_2_qual/install/setup.bash
export ROS_DOMAIN_ID=92
export ROS_LOG_DIR=/tmp/phase08_7_m2_2_probe_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m2_2_probe_mpl
export TURTLEBOT3_MODEL=burger
export DISPLAY=:0
timeout --signal=INT --kill-after=60s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m2_2_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m2_2_efficiency_correction_probe.yaml \
  --operator phase08_7_m2_2 \
  --case-id v7_m2_2_diagonal_r1p5_h25_18001 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_2 \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_2/\
phase08_v7_m2_2_efficiency_correction_probe_summary.yaml \
  --gui
```

The retained attempt is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_2/
  2026-07-30/
  20260730T001458667712Z_simulation_phase08_v7_m2_2_
  efficiency_correction_probe-v7_m2_2_diagonal_r1p5_h25_18001-
  robu_bfd6b97a
```

The runner exited `1` for failed behavioral classification. The recorder
exited `0`, did not time out, and retained a complete run.

## Infrastructure and lifecycle

Infrastructure is classified `completed`.

- readiness duration is `360.079972932 s`;
- recording and cleanup passed;
- no new nodes or session processes remained;
- the bag contains `10,635` odometry samples, `3,615` PDE-history samples,
  `7,235` typed state samples, `1,491` convergence-status samples, and
  `72,250` contact samples;
- all three final command streams are zero and final readiness is false;
- `validate_run` returned `0`, `passed=true`, with no failures or warnings;
- read-only sqlite `PRAGMA quick_check` returned `ok`;
- standard `analyze_run` returned `0`, retained
  `analysis_status=complete`, and wrote eight plots plus eleven tables.

The analysis reports `20.1514118974 m` of path, one escape attempt, one
successful escape-state exit, one active/created fill cluster, one merge, a
terminal `FAILSAFE`, and `36` non-ground contact-state records.

## Detector correction

The frozen `0.50` maximum path-efficiency correction produced three
SEARCH-only convergence candidates:

```text
source time   path efficiency   count remaining
193.7 s       0.3231200474      2
216.9 s       0.3576478619      1
238.4 s       0.3804596064      0
```

`CONVERGENCE_CONFIRMED` followed at `238.4 s`. The detector therefore did not
confirm directed initial travel and did confirm the compact local trajectory,
as intended.

The confirmed convergence point was:

```text
(1.3856016612, 1.1866239560) m
distance to declared local:  0.3485022905 m
distance to declared global: 3.1340690892 m
```

The accepted fill center was:

```text
(1.3550616314, 1.3133489174) m
distance to convergence point: 0.1303530179 m
```

These values satisfy the frozen local association thresholds.

## Observed recovery topology

The in-readiness collapsed state sequence was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_ASSIST
-> RECENTER
-> SEARCH
-> FAILSAFE
```

The relevant events were:

```text
CONVERGENCE_CONFIRMED
FILL_CREATED
ESCAPE_STARTED
ESCAPE_STALLED
FILL_SUPERSEDED
FILL_MERGED
RECENTER_STARTED
RECENTER_COMPLETE
```

The first fill and its revision share cluster identity `1`. The revision and
merge do not create a second local cluster, so exact one-fill cardinality
passes.

The recovery mechanism completed:

- repulse began from the accepted local fill;
- the existing bounded stall rule requested one targeted redesign;
- the accepted revision entered `ESCAPE_ASSIST`;
- the assisted escape reached its stable exit;
- recenter completed at source time `275.2 s`;
- the supervisor returned to `SEARCH`.

The Stage A reporter nevertheless returned zero episodes because its
implementation recognizes only this contiguous direct path:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

It does not recognize the already-supported redesign plus `ESCAPE_ASSIST`
branch. The controller's singular `required_state_path` predicate has the same
defect. Because the live staged monitor uses that reporter result, the false
Stage A failure also prevented the global-proximity monitor from arming.

This is a reporting/evidence-contract integration defect, not evidence that
the local recovery mechanism failed.

## Affine assistance

Post-recenter affine guidance was active, not disabled.

- resumed `SEARCH` reported weights
  `(sensor, Gaussian, affine) = (1, 1, 1)`;
- the accepted fill remained active;
- the first post-recenter safe direction was approximately
  `(0.776196, 0.630491)`, revision `217`;
- the selector later changed the direction to approximately
  `(-0.420, 0.907)` and continued through revision `232`;
- the robot moved from recenter toward the global corner.

The affine term therefore provided bounded, fill-aware direction assistance
through the existing modified-cost and controller owners. It did not know or
consume the global-source coordinates. It cannot itself declare success or
override wall safety; those responsibilities belong to the evidence monitor
and supervisor.

## Stop-boundary diagnosis

After recenter, the first noninterpolated odometry samples at progressively
closer global radii were:

```text
radius    ROS time   pose (x, y)               actual distance   east inset
1.30 m    304.738 s  (3.316058, 2.215189) m    1.297912 m        0.233942 m
1.20 m    306.030 s  (3.369463, 2.308150) m    1.198977 m        0.180537 m
1.10 m    307.322 s  (3.422131, 2.403209) m    1.099552 m        0.127869 m
1.00 m    308.410 s  (3.469435, 2.500712) m    0.999756 m        0.080565 m
0.85 m    310.450 s  (3.534989, 2.652805) m    0.847917 m        0.015011 m
```

The supervisor entered `FAILSAFE` at source time `310.8 s` because the pose
left the wall-margin-inset operating bounds. The first east-wall contact
followed at approximately `311.879 s`. No `0.60 m` sample was possible before
that safety boundary; the closest recorded distance was about `0.780 m` after
failsafe/inertial motion.

A `1.20 m` first-sample stop would have triggered:

- `4.77 s` before the wall-margin failsafe;
- approximately `5.85 s` before first wall contact;
- with `0.180537 m` remaining to the east controller inset;
- after local recovery, recenter, resumed `SEARCH`, and exact-cardinality
  completion.

This is an evidence-backed simulation equivalent of the user's explicitly
permitted physical `Ctrl+C` once the robot is close enough to the global
minimum. It remains a post-Stage-A boundary and cannot hide a missing local
recovery, extra fill, collision before arrival, or evidence-integrity failure.

## Bounded correction

A fresh M2.3 experiment may preserve every M2.2 algorithm, geometry, detector,
topology, affine, retry, and timing value while making two evidence-contract
corrections:

1. accept either the direct recovery path or the observed legal
   redesign-assisted recovery path for Stage A and the controller path
   predicate;
2. set both staged and ground-truth post-recovery proximity to exactly
   `1.20 m`.

The schema should retain singular-path compatibility for historical scenarios,
make alternative paths additive and schema-v5-only, require at least one
complete valid path, and evaluate the same `required_state_path` predicate as
true when any declared alternative is observed. The relaxed radius must remain
bounded, must equal the ground-truth tolerance, and must only apply to the
opt-in post-recovery guidance profile.

No detector, supervisor, controller, fill, affine, topic, sign/unit, world,
historical scenario, V6 evidence, or physical-hardware behavior needs to
change.

## Evidence identities

```text
3638818042255b508d441b6222e16c91b2d85614d22776589385f2d6f3dd2052  suite summary
27648c8344318c43883f9296a450f9ed4a350c915e626cd4405f7a8b3b7ef264  scenario_result.yaml
bf72611b9a9b006401ae1b2070eb6ddba880a753ae3d61e8a0f35354ed7b6b8e  completeness.json
17c57b1e0247b1ea079b0a8e1ef0aff6a750cf301e4bd3ab21dfaccb53255527  bag/bag_0.db3
c5bbe0a306cfa17f5d41268aeb400b1104ca99f09a392d07e4f2622ac48bef34  analysis/summary_metrics.json
b4cfeaebf17a1c0fe8946353ad4438f2603147c9c8bca289bd0d26b3d014ed1c  analysis/analysis_completeness.json
```

## Boundary

M2.2 is closed and immutable as a failed fixed experiment. Its result does not
authorize M3 or establish repeatability/simulation readiness. It does provide
direct empirical qualification of the corrected convergence detector, the
one-cluster topology, the assisted local-recovery mechanism, recenter, and
bounded post-recovery affine guidance.

A separately versioned M2.3 may implement only the reporter/path-alternative
and `1.20 m` operator-stop corrections above, subject to a fresh scenario
hash, case key, evidence root, full no-Gazebo qualification, checkpoint, and
commit before one bounded visible probe.
