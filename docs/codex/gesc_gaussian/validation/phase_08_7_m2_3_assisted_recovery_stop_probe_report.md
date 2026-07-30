# Phase 08.7 M2.3 assisted-recovery and operator-stop probe report

Date: 2026-07-30

## Result

The one fixed M2.3 development attempt is retained as **PASS**.

- infrastructure, recording, validation, final-zero, and cleanup: **PASS**;
- convergence detection at the intended local: **PASS**;
- exact one-cluster fill cardinality and local association: **PASS**;
- Stage A local Gaussian recovery: **PASS**;
- Stage B post-recovery global proximity and graceful stop: **PASS**;
- collision and forbidden-state/event expectations during readiness: **PASS**;
- combined behavioral result: **PASS**.

The robot confirmed the declared lower-output local, created exactly one
associated Gaussian fill, escaped, recentered, resumed `SEARCH`, approached
the declared global with post-recovery affine assistance active, and stopped
on the first recorded sample within the prospectively committed `1.20 m`
operator-equivalent radius.

This single development probe establishes the prerequisite result for a
separately authorized M3 spatial suite. It does not establish repeatability,
simulation readiness, or physical readiness, and it does not authorize M3.

## Frozen input

```text
qualified commit:
  9a2612beb0e987c4d328d04660529f77a2f089af
suite:
  phase08_v7_m2_3_assisted_recovery_stop_probe
experiment version:
  phase08-v7-m2.3
case:
  v7_m2_3_diagonal_r1p5_h25_18001
case key:
  13cf3a091db9f9e72fff3abc0c1885b4e64033766f5317ee628490e468e10cbd
scenario SHA-256:
  f03db4462527620321eb299656d9f56fe32e10362664e595f7d3850fc3f53eca
seed:
  18001
maximum fills:
  1
detector:
  SEARCH-only, minimum path 0.20 m, maximum efficiency 0.50
accepted recovery paths:
  direct or one-redesign assisted
post-recovery affine:
  enabled, maximum age 60.0 s, gain 0.5
post-Stage-A global proximity:
  1.20 m
```

The installed scenario and source hashes matched before dispatch. The run
metadata identifies the exact qualified commit. Its `dirty=true` field and
diff hash refer only to the predeclared live-status dispatch entry made after
that commit; no algorithm or scenario byte changed.

## Invocation and retained run

Exactly one visible-Gazebo attempt was dispatched on ROS domain `101`:

```bash
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m2_3_qual/install/setup.bash
export ROS_DOMAIN_ID=101
export ROS_LOG_DIR=/tmp/phase08_7_m2_3_probe_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m2_3_probe_mpl
export TURTLEBOT3_MODEL=burger
export DISPLAY=:0
timeout --signal=INT --kill-after=60s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m2_3_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m2_3_assisted_recovery_stop_probe.yaml \
  --operator phase08_7_m2_3 \
  --case-id v7_m2_3_diagonal_r1p5_h25_18001 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_3 \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_3/\
phase08_v7_m2_3_assisted_recovery_stop_probe_summary.yaml \
  --gui
```

The runner exited `0`. The retained attempt is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_3/
  2026-07-30/
  20260730T005434366368Z_simulation_phase08_v7_m2_3_
  assisted_recovery_stop_probe-v7_m2_3_diagonal_r1p5_h25_18001-
  rob_fe3286c1
```

The recorder exited `0`, did not time out, completed its final-zero and
readiness-false contracts, and retained a complete bag.

## Detector, fill, and Stage A

The corrected `0.50` maximum path-efficiency detector emitted three
SEARCH-only candidates:

```text
source time   path efficiency   count remaining
131.8 s       0.2852566130      2
153.8 s       0.3430636994      1
175.9 s       0.3616799274      0
```

The last candidate produced `CONVERGENCE_CONFIRMED`. Its convergence point
was:

```text
(1.3938876873, 1.1160647584) m
distance to declared local:  0.3378020801 m
distance to declared global: 3.1810149811 m
```

Exactly one typed fill cluster was created:

```text
cluster id: 1
fill id:    1
center:     (1.3945263243, 1.2521809924) m
distance from convergence point: 0.1361177322 m
```

The in-readiness state path was the accepted direct topology:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

`ESCAPE_REPULSE` began at source time `185.2 s`, reached its stable exit at
`194.6 s`, and recenter completed at `208.0 s`. All required causal events
were present and the terminal in-readiness state was `SEARCH`. Stage A and
exact fill cardinality therefore passed.

This attempt did not need the redesign-assisted alternative. That alternative
remains part of the frozen schema-v5 contract and passed the direct,
controller, scoped-reporter, and live-monitor qualification tests before this
run.

## Affine guidance and Stage B

Post-recovery affine guidance was enabled and active. Immediately after the
return to `SEARCH`, recorded cost weights were:

```text
(sensor, Gaussian, affine) = (1, 1, 1)
```

The staged live monitor armed only after Stage A and exact cardinality passed.
It then stopped the run on this first qualifying noninterpolated odometry
sample:

```text
bag timestamp:        1785373119246261619
sample index:         6940
position:             (3.4433011933, 2.3021489031) m
declared global:      (3.5, 3.5) m
distance to global:   1.1991922303 m
committed radius:     1.20 m
post-Stage-A valid samples considered:   905
post-Stage-A invalid samples considered: 0
interpolation used:   false
```

No non-ground collision, in-readiness `FAILSAFE`, `TIMEOUT`, forbidden event,
or evidence-integrity failure preceded that sample. Stage B therefore passed.
The shutdown-induced explicit-stop `FAILSAFE` transition occurs only after
readiness is false and is correctly excluded from behavioral classification.

The runner's graceful proximity stop is the simulation equivalent of the
user's allowed physical `Ctrl+C` once the robot is observably close enough to
the global minimum. It does not require `GOAL_REACHED` or `GOAL_HOLD`.
Accordingly, the diagnostic controller-goal result is false while independent
simulation ground truth, Stage B, and the declared combined result all pass.

## Infrastructure and independent analysis

The suite summary classifies the run as `passed` with infrastructure
`completed`. Every required predicate is true:

```text
recording_complete:                true
cleanup_complete:                  true
required_state_path:               true
required_events:                   true
no_forbidden_states:               true
no_forbidden_events:               true
collision_expectation:             true
local_recovery_stage:              true
post_recovery_global_proximity:    true
fill_cardinality:                  true
```

Cleanup found no remaining new ROS nodes or session processes. Independent
`validate_run` returned `0`, `passed=true`, with no failures or warnings.
Read-only sqlite `PRAGMA quick_check` returned `ok`.

Standard `analyze_run` returned `0` and wrote its complete result below
`analysis/phase07`: eight plots, eleven tables, and no analysis failures. It
reports:

```text
readiness duration:       236.992702246 s
path length:              14.9839405545 m
escape attempts:          1
successful escape exits:  1
escape failures:          0
created/active fills:     1 / 1
collision:                false
in-readiness failsafe:    false
in-readiness timeout:     false
terminal state:           SEARCH
```

## Evidence identities

```text
b607f577f261f1b133d730abbe51fe372c3141804fe48406bc2f6b66d33bfd1f  suite summary
9a85e950a341a6c4c1f69aefbbcb3d87d469deea068d0923ad3530766d010819  scenario_result.yaml
337be8d933be644cc37d3b0b1b93ed052336d0997f64bc7e231d67c7829fcb81  completeness.json
b14cb52d1d2eaa5e24f2bb50e4d84a95934678f7e6f3c86ad85b8d788340b9f3  bag/bag_0.db3
16e5136fa7a4b4715054ce50320bb0e7720dd83d20b0cda0e09b7083a3d5ee0b  analysis/phase07/summary_metrics.json
3d9497adda29ca8ef255473c6a55b248810b9382a8798a88489e91cdf43e99dd  analysis/phase07/analysis_completeness.json
```

## Boundary

M2.3 is closed and retained as a successful fixed development experiment. M2,
M2.1, and M2.2 remain immutable failed experiments and are neither retried nor
relabelled. V6 and every historical scenario, world, result, and evidence root
remain unchanged.

This result establishes the declared prerequisite for M3, but M3 remains
unauthorized. No second M2.3 attempt, physical run, readiness claim, or
multi-position suite is implied.
