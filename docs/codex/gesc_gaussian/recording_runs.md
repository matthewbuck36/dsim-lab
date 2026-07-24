# Unified GESC/Gaussian Recording Runs

Phase 05 provides one entry point for simulation and future audited physical
runs. It always records explicit manifest topics to a ROS 2 Humble sqlite3
bag, captures the target console, snapshots Git and parameters, holds motion
at zero until preflight passes, and validates the finished run.

## Before starting

Build and source the workspace, prepare a metadata YAML from the installed
`experiment_metadata.yaml` template, and fill every operator field honestly.
`mode` must match the CLI. Physical metadata still requires
`algorithm_profile=robust_gaussian_v1`; audited simulation recording accepts
`legacy` or `robust_gaussian_v1` without changing the shared manifest or
completeness gates. Simulation source levels are relative model inputs, not lux
calibration.

```bash
source /opt/ros/humble/setup.bash
cd /home/mattb/dsim-lab/ros2_ws
colcon build --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
```

## Start a simulation run

The target launch is an argv list after `--`; no shell command is evaluated.
The controller interlock must be enabled in the target launch.

```bash
ros2 run ros_esc record_run \
  --mode simulation \
  --metadata-input src/ros_esc/test/fixtures/recording_smoke_metadata.yaml \
  --duration-sec 8.0 \
  --preflight-timeout-sec 60.0 \
  --runs-root ~/Experiments/GESC-Gaussian/runs \
  -- \
  ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
  algorithm_profile:=robust_gaussian_v1 \
  use_pde_extensions:=True \
  enable_observability:=True \
  recording_ready_required:=True \
  recording_ready_topic:=/gesc_gaussian/recording_ready \
  recording_ready_stale_sec:=0.50
```

The generated directory is
`~/Experiments/GESC-Gaussian/runs/<YYYY-MM-DD>/<run_id>/`. A supplied
`--run-id` is never overwritten. Physical mode uses the same command shape and
manifest, but must not be run until Phase 09 supplies and audits the physical
target graph.

Preflight holds every final command at zero. It waits for the target graph and
bag subscriptions, then snapshots exact ROS parameter values and types before
publishing readiness true. On the audited simulation graph this can take about
90 seconds in addition to Gazebo startup because Humble queries each live node;
`--preflight-timeout-sec` applies to graph discovery, not parameter capture.

## Run deterministic Gazebo scenario suites

Phase 06 adds a simulation-only orchestration layer over the same
`gazebo.launch.xml`, `record_run`, run directory, manifest, and validator. It
runs one fresh Gazebo process at a time, assigns an explicit Gazebo/noise seed
and unique run ID, enforces a scoped wall timeout, and checks that no new ROS
nodes or processes from that run remain before continuing.

```bash
ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase06_smoke.yaml \
  --operator "$USER" \
  --dry-run

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase06_smoke.yaml \
  --operator "$USER"
```

The runner is headless by default; add `--gui` for a visible one-off run.
`--case-id CASE_ID` is repeatable, `--runs-root PATH` overrides the suite root,
and `--summary-output PATH` selects an explicit suite summary. `--dry-run`
validates and expands the YAML and prints exact recorder/launch argv without
starting ROS, Gazebo, rosbag, or hardware.

Every launched run retains the Phase 05 artifacts and adds
`scenario_definition.yaml`, `resolved_scenario.yaml`,
`scenario_result.yaml`, and, for seeded uniform noise,
`resolved_cost_function.json`. Suite summaries distinguish
controller-observable goal success from final-pose simulation ground truth.
An ordinary failed case is preserved and may be followed by the next case;
cleanup failure stops the suite to prevent contamination.

`phase06_catalog.yaml` labels supported geometries as
`executable_unverified`. Its unsupported records are not launched: no
authoritative source-level map, deterministic Gaussian noise, sensor/pose
delay, collision truth, static raw-attraction ablation, more than five
sources, or plain non-PDE legacy recording exists in this simulator contract.
The runner has no physical launch or mode.

## Stop a run

For an indefinite run (`--duration-sec 0`), press Ctrl-C once in the
`record_run` terminal. The runner then publishes readiness false, requests the
existing supervisor stop latch, waits while rosbag records fresh zero evidence
on all three final-command topics, stops the target process group, and stops
rosbag last. Do not kill Gazebo or rosbag separately during normal shutdown.

Success requires `completeness.json` to contain `"passed": true`. The raw bag
is retained regardless of validation outcome.

## Validate or recover a failed run

Run the validator at any time:

```bash
ros2 run ros_esc validate_run <run-directory>
```

If rosbag was interrupted before its metadata was finalized, reindex it first:

```bash
ros2 bag reindex <run-directory>/bag
ros2 run ros_esc validate_run <run-directory>
```

Inspect `console.log`, `resolved_topics.yaml`, `resolved_parameters.yaml`,
`metadata.yaml`, and `completeness.json` for the exact failure. Never delete,
rename for reuse, or overwrite the failed run. Correct the cause and start a
new run ID. Parameter changes also require a new experiment version and run.

If preflight reports duplicate publisher endpoints, an earlier launch is still
alive. Do not bypass the singleton checks. Identify only the stale experiment
processes with `ps -eo pid,ppid,pgid,lstart,args`, stop their owning launch or
exact process group, verify `ros2 node list` is clear, and then start a new run.
Do not use a broad process-name kill on a physical host.
