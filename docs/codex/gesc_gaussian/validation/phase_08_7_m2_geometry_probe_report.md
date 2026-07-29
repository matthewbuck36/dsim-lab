# Phase 08.7 M2 Geometry Probe Report

Date: `2026-07-29`

Verdict:

```text
M2 execution                    COMPLETE
geometry / infrastructure      PASS
Stage A local recovery         PASS
exact fill cardinality         PASS
Stage B global proximity       FAIL
combined behavioral result     FAIL
simulation readiness           NOT ESTABLISHED
M3 authority                   NOT GRANTED
```

This is the sole authorized Phase 08.7 M2 attempt. It was run once, with a
visible Gazebo GUI, from the case committed before execution. It was not
retried. The result does not alter or count toward V6 or any other historical
scenario.

## Frozen case

```text
pre-execution commit:
  a8b9d97031c44f4557936c2e24143da2d183c431
suite:
  phase08_v7_m2_geometry_probe
case:
  v7_m2_diagonal_r1p5_h25_18001
case key:
  d07a23d9a77f938038fbe58c5d2b312dd5e550394d4f60c56d22d6ead8ca2961
seed:
  18001
scenario SHA-256:
  9623b001d91a1216d35c037c2eeb46d4a0f05cdf46d3b3ea68c2b4ad7a0af442
shifted-world SHA-256:
  88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf
```

Resolved geometry:

```text
room inner bounds: [-0.25, 3.75] m on x and y
room center:       (1.75, 1.75) m
wall margin:       0.20 m
start:             (0.0, 0.0), yaw 0
local:             (1.0606601717798212, 1.0606601717798212)
local polar point: radius 1.5 m, angle 45 degrees
global:            (3.5, 3.5)
known topology:    one local, one global
maximum fills:     one
contacts:          enabled
affine assist:     disabled
```

## Execution

The installed isolated overlay from M2 qualification was used:

```text
/tmp/phase08_7_m2_install
```

Exact bounded command:

```bash
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m2_install/setup.bash
export ROS_DOMAIN_ID=88
export ROS_LOG_DIR=/tmp/phase08_7_m2_probe_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m2_probe_mpl
export TURTLEBOT3_MODEL=burger
export DISPLAY=:0
timeout --signal=INT --kill-after=60s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m2_install/ros_esc/share/ros_esc/scenario_runner/scenarios/phase08_v7_m2_geometry_probe.yaml \
  --operator phase08_7_m2 \
  --case-id v7_m2_diagonal_r1p5_h25_18001 \
  --runs-root /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2 \
  --summary-output /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2/phase08_v7_m2_geometry_probe_summary.yaml \
  --gui
```

The outer runner returned `1` because the behavioral classification failed.
The recorder returned `0`, `timed_out=false`, and retained a complete run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2/
  2026-07-29/
  20260729T220933564961Z_simulation_phase08_v7_m2_geometry_probe-
  v7_m2_diagonal_r1p5_h25_18001-robust_gaussian_v1-d0_3ad17fc6
```

Suite summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2/
  phase08_v7_m2_geometry_probe_summary.yaml
```

The retained run occupies approximately `390 MiB`.

## Live geometry and ownership evidence

The preferred `/gazebo/model_states` topic was not exposed by this launch.
That read-only query failed without affecting the run. Runtime geometry was
instead checked through the available `/get_model_list` service and native
read-only `gz model -m ... -p` queries.

Observed model poses:

| Model | x (m) | y (m) | z (m) |
|---|---:|---:|---:|
| east wall | 3.80 | 1.75 | 0.25 |
| west wall | -0.30 | 1.75 | 0.25 |
| north wall | 1.75 | 3.80 | 0.25 |
| south wall | 1.75 | -0.30 | 0.25 |
| local light | 1.06066 | 1.06066 | 0 |
| global light | 3.50 | 3.50 | 0 |

The first readiness-interval odometry sample was
`(0.000352821454192, 0.000458412508747) m`, which verifies the corner-origin
spawn within normal simulation settling error. A later live query observed
the moving TurtleBot3 at `(1.48650, 1.28811) m`.

The contacts topic had the expected
`gazebo_msgs/msg/ContactsState` type, two simulation publishers, and the
rosbag recorder as a subscriber. `/cmd_vel` had exactly one publisher,
`custom_controller`; the recording coordinator, recorder, and TurtleBot3
drive controller were subscribers.

## Geometry and infrastructure result

Geometry and infrastructure pass:

- the four live wall centerlines imply the committed inner faces at
  `-0.25 m` and `3.75 m`;
- both lights and the robot start matched the frozen scenario;
- the recorder completed normally and cleanup passed with no remaining new
  nodes or session processes;
- the run was classified with
  `infrastructure_status: completed`;
- `completeness.json` passed with no failures or warnings;
- `validate_run` passed with no failures or warnings;
- all three final command streams were zero and final readiness was false;
- the bag contains `71,918` contact messages, collision evidence is
  available, and no non-ground collision was observed;
- a read-only Python `sqlite3` `PRAGMA quick_check` returned `ok` because the
  `sqlite3` CLI is not installed;
- after cleanup, no runner, recorder, Gazebo server/client, or physical
  hardware process remained.

Selected retained topic counts:

| Topic | Messages |
|---|---:|
| `/cmd_vel` | 51,055 |
| `/odom` | 10,597 |
| `/gesc_gaussian/recording_ready` | 3,733 |
| `/gesc_gaussian/algorithm_state` | 7,213 |
| `/gesc_gaussian/algorithm_events` | 40 |
| `/gesc_gaussian/gaussian_fills` | 1 |
| `/gesc_gaussian/simulation/contacts` | 71,918 |

## Staged behavioral result

### Stage A and fill cardinality: PASS

One complete local-recovery episode followed the required path:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

The final resumed `SEARCH` was recorded at bag stamp
`1785363195303143037`. The required convergence, fill, escape, recenter-start,
and recenter-complete evidence was present.

Exactly one accepted typed active cluster was created:

```text
cluster / fill id:           1
fill center:                 (1.2239058490, 1.4353952912) m
causal convergence point:    (1.3282657490, 1.3428301900) m
fill-to-convergence:         0.1394965472 m  (limit 0.50 m)
convergence-to-local:        0.3888864411 m  (limit 0.60 m)
convergence-to-global:       3.0610147413 m  (minimum 0.75 m)
```

This proves one local recovery and the declared one-fill cardinality for this
attempt. It does not prove repeatability.

### Stage B and combined result: FAIL

After Stage A, all `4,268` valid odometry samples were evaluated without
interpolation. None entered the committed `0.35 m` radius around
`(3.5, 3.5)`, so the global-proximity stop did not trigger.

The closest post-Stage-A sample was:

```text
position:             (1.9883714796, 1.8959068678) m
distance to global:   2.2041178645 m
motion time:          360.054148057 s
```

The later observed sequence was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> FAILSAFE
```

with `FILL_REJECTED` followed by `FAILSAFE`. Consequently the forbidden-state
and forbidden-event predicates failed, Stage B failed, and the combined
behavioral result failed. Stage A remains independently passed.

## Offline analysis

The retained run was checked with:

```bash
timeout 180s ros2 run ros_esc validate_run \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2/2026-07-29/\
20260729T220933564961Z_simulation_phase08_v7_m2_geometry_probe-\
v7_m2_diagonal_r1p5_h25_18001-robust_gaussian_v1-d0_3ad17fc6
```

Result: exit code `0`, `passed: true`, no failures, and no warnings.

The standard offline analysis used the same retained bag:

```bash
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m2_install/setup.bash
export ROS_DOMAIN_ID=89
export ROS_LOG_DIR=/tmp/phase08_7_m2_analysis_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m2_analysis_mpl
timeout --signal=INT --kill-after=30s 300s \
  ros2 run ros_esc analyze_run \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2/2026-07-29/\
20260729T220933564961Z_simulation_phase08_v7_m2_geometry_probe-\
v7_m2_diagonal_r1p5_h25_18001-robust_gaussian_v1-d0_3ad17fc6 \
  --output-dir \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2/2026-07-29/\
20260729T220933564961Z_simulation_phase08_v7_m2_geometry_probe-\
v7_m2_diagonal_r1p5_h25_18001-robust_gaussian_v1-d0_3ad17fc6/analysis
```

It completed with exit code `0` and wrote eight plots, eleven CSV tables,
`summary_metrics.json`, and `analysis_completeness.json` under the retained
run's `analysis/` directory.

Its status is `partial`, not `complete`, because the terminal state is
`FAILSAFE`, one state-duration gap was invalid, and aggregate-target metrics
were unavailable to the generic analyzer. Fresh Phase 05 validation inside
the analysis passed. The analyzer also independently reports one fill, one
successful escape attempt, no collision, controller success false, and
terminal `FAILSAFE`.

## Evidence hashes

```text
389aa07e84a56bb5210071de5f1e82aef9b59536dfc5685e157dea810c26ba04  suite summary
0f5773d92f6a7d318749f9e8182f26cd0294721d0d5ad78adf9a53efa376feeb  scenario_result.yaml
6300173abb17a9e1227e8761d7412da571775501efa5fa6842c4ba560ca9b13e  completeness.json
d78846f3c353198e268976aa335afd193dc871065f4155b306facca8a4f79d22  metadata.yaml
a590764b29dc824bbabbbf4a342ec3d0bac599e220d5d363ff4cd4e05c1de457  bag/bag_0.db3
63664e5be15556ffdc5d15a8bc68654bc6b7b43668f552ed2bfcf9bd796fb310  analysis/summary_metrics.json
171be0671ca2013f7126fac8b367ba786493fc8d639b1cbd2cb3a41ee174d125  analysis/analysis_completeness.json
```

Post-run repository checks:

```text
validate_phase_context.sh 08 implement:
  PASS; active subphase phase_08_7_plan.md
shifted-world plus historical scenario/world immutability:
  2 passed, 58 deselected in 35.05s
git diff --check:
  PASS
```

The first context-validator attempt used a nonexistent package-local path and
returned `127` without making a change. The immediate rerun through
`DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/` passed.

## Boundary

M2 is executed and retained. Its geometry/infrastructure objective passed,
but its Stage B and combined behavioral contract failed. This single
development result is not simulation readiness. M3 remains unauthorized, and
the Plan's “only after M2 passes” prerequisite has not been established by
the combined result.
