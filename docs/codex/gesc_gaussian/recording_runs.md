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

Preflight holds every final command at zero. It first requires the target
graph, exact types/publisher counts, bag subscriptions, controller interlock,
and a gated zero command. Simulation then starts a fresh receipt epoch and
requires valid, current pose, source-cost, filter-output, and timekeeper
messages. Robust runs additionally require a finite supervisor command and a
valid, finite-weight, non-failsafe `SEARCH` state. An actual
`/controller_manager/list_controllers` response must report
`joint_state_broadcaster` and `velocity_controller` active. Delayed scenarios
check the resolved delayed pose/source streams consumed by the algorithm, and
the recorder requires the canonical Gazebo target and rejects profile, delay,
relay-gate, or pose/source/raw-history consumer routes that disagree with
metadata. Every selected operational stream is promoted for that run to a
required singleton publisher, required rosbag subscription, required parameter
owner, and minimum one retained message even when the base manifest lists the
topic as conditionally optional.

Only after that barrier does the recorder snapshot exact ROS parameter values
and types. Node snapshots remain serial and retain their local 15-second
response cap, but graph discovery, operational readiness, every service wait
and response, retry delay, parameter capture, and a second post-capture
readiness epoch all share the single `--preflight-timeout-sec` deadline. The
second barrier proves the controller manager and data publishers survived
parameter capture before readiness can become true. A callback lock pairs
heartbeat messages with receipt times and performs one final service/data
snapshot plus an atomic authorization. Any pre-readiness nonzero command is a
permanent safety failure, including one observed between the ordinary barrier
and the atomic authorization. Robust lifecycle evidence is also permanent:
any pre-authorization non-`SEARCH`, failsafe, prior-transition, or active-fill
or active-escape state survives both receipt-epoch resets and disqualifies the
attempt even if the latest state returns to clean `SEARCH`. The monitor closes
atomically when readiness opens or shutdown begins; the bag validator uses the
earlier readiness/stop boundary, so expected post-stop `FAILSAFE` evidence is
not mislabeled. The retained bag and coordinator metadata independently
enforce the same completeness check. A
controller-manager response that completes after the one absolute deadline is
also rejected before readiness can change.

The controller-manager/data-plane barrier is simulation-only; physical mode
retains its prior graph/interlock gate until Phase 09 defines audited physical
operational checks. Parameter capture remains bounded by the common preflight
deadline in both modes. A simulation manifest cannot omit the operational
block; the physical path deliberately has no such block, and manifest/runtime
validation rejects a physical operational block rather than relying on that
file convention.

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
If readiness never becomes true, the runner reports
`infrastructure_invalid` and marks behavior outcomes unavailable rather than
failed. It never retries automatically; any allowed development replacement
must be separately predeclared, identical, and retained under a new run ID.
Finalized recorder runtime failures, malformed/missing completeness evidence,
bag-outcome extraction failures, and cleanup leaks remain distinct
infrastructure statuses instead of being mislabeled as completed runs.

`phase06_catalog.yaml` labels supported geometries as
`executable_unverified`. Its unsupported records are not launched: no
authoritative source-level map, deterministic Gaussian noise, sensor/pose
delay, collision truth, static raw-attraction ablation, more than five
sources, or plain non-PDE legacy recording exists in this simulator contract.
The runner has no physical launch or mode.

## Prove Phase 08 simulation-validation support

Phase 07.5 extends the same runner with schema version 2. Direct launch
behavior and schema-version-1 case identities remain unchanged. The validation
world, contact sensors, delayed-input relay, and contact positive-control probe
are simulation-only and default off.

```bash
ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_validation_support.yaml \
  --operator "$USER" \
  --dry-run

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_validation_support.yaml \
  --operator "$USER" \
  --runs-root ~/Experiments/GESC-Gaussian/runs/phase08/prerequisite
```

The five probes cover valid empty contact evidence, a real static Gazebo
contact positive control, configured seeded Gaussian noise, 100 ms sensor
delay, and 100 ms pose delay. Analyze the retained run directories with the
existing `analyze_run` command. Collision and observed-delay statuses must be
valid; an unavailable or invalid result is not acceptable Phase 08 evidence.

## Historical Phase 08 v1 workflow — report only, do not execute

The retired workflow produced retained failed/incomplete v1 evidence. Execution
commands are intentionally omitted to avoid accidental resume. Do not run
`sweep`, `freeze`, `holdout`, or `full-pass` against that root. The only safe
workflow command is a read-only report:

```bash
EVIDENCE_ROOT=~/Experiments/GESC-Gaussian/runs/phase08

ros2 run ros_esc validate_robustness report \
  --operator "$USER" --evidence-root "$EVIDENCE_ROOT"
```

The v1 arithmetic was 81 training runs, 12 holdouts, and three planned
519-run passes. Its scenarios, frozen profile, selection result, and run
directories are immutable historical evidence and do not count toward v2.

## Historical Phase 08 v2 workflow — report only, do not execute

The v2 commands and scenarios were installed, but activation failed at 1/10 and
closed the version before tuning. Do not execute activation, sweep, freeze,
holdout, validation, or reproducibility against this root. The only safe
workflow command is its read-only report:

```bash
PHASE08_V2_ROOT=~/Experiments/GESC-Gaussian/runs/phase08_v2

ros2 run ros_esc validate_robustness report \
  --operator "$USER" --evidence-root "$PHASE08_V2_ROOT"
```

The historical declared budget was 10 activation, 30 tuning, 20 new hidden
holdout, 50 additional unique validation, and 10 repeats. Only activation ran.
Phase 08.1 uses a fresh development-only root for minimal probes; any future
formal attempt requires a new version and sealed contract.

## Stop a run

For an indefinite run (`--duration-sec 0`), press Ctrl-C once in the
`record_run` terminal. The runner then publishes readiness false, requests the
existing supervisor stop latch, waits while rosbag records fresh zero evidence
on all three final-command topics, stops the target process group, and stops
rosbag last. Do not kill Gazebo or rosbag separately during normal shutdown.

Success requires `completeness.json` to contain `"passed": true`. The raw bag
is retained regardless of validation outcome.

## Analyze a recorded run

Phase 07 analyzes complete and failed runs through the same offline command:

```bash
ros2 run ros_esc analyze_run <run-directory>
```

The default output is `<run-directory>/analysis/phase07`. The command exports
CSV by default, creates eight separate standard figures, and writes
validity-marked per-run metrics and analysis completeness. It preserves all
raw bags, recorded timestamps, root metadata, and `completeness.json`.
Critical missing or out-of-tolerance samples are marked rather than
interpolated.

To keep an existing analysis immutable, rerun to a new destination:

```bash
ros2 run ros_esc analyze_run <run-directory> \
  --output-dir <new-analysis-directory>
```

After analyzing each run in a scenario matrix:

```bash
ros2 run ros_esc summarize_matrix <run-or-analysis-directory> [...] \
  --output-dir <new-matrix-summary-directory>
```

Analysis does not replace `validate_run`, and a readable failed run can
legitimately produce useful partial or invalid analysis evidence with process
exit code 0. Experimental success and completeness remain fields in the
reports rather than being inferred from the analysis command's exit code.

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
`metadata.yaml` distinguishes `failure_stage`, `infrastructure_status`,
whether readiness was ever true, initial versus total preflight completion,
both barrier pass times, any observed pre-readiness nonzero command, and any
permanently latched pre-authorization lifecycle violation.
`resolved_topics.yaml` retains both operational barrier snapshots, heartbeat
ages/validity, run-specific required heartbeat streams, the metadata/target
delay and consumer-topic coupling, active controller states, and final
authorization evidence. `completeness.json` is strict JSON. Corrupt nonfinite
diagnostic values are changed to `null`, recorded by a failed
`strict_json_finite` check, and never written as `NaN` or `Infinity`.

If preflight reports duplicate publisher endpoints, an earlier launch is still
alive. Do not bypass the singleton checks. Identify only the stale experiment
processes with `ps -eo pid,ppid,pgid,lstart,args`, stop their owning launch or
exact process group, verify `ros2 node list` is clear, and then start a new run.
Do not use a broad process-name kill on a physical host.
