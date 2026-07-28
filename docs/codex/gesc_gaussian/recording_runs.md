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

`record_run` owns a deferred signal-safe shutdown. It disables rclpy's
automatic signal handlers, converts `SIGINT`/`SIGTERM` into a loop-visible
request, and keeps the ROS context valid while it publishes readiness false
and stop true, observes the final-zero representations, stops the target and
bag, and closes the executor. The spin thread is joined before the coordinator
node and context are destroyed. If an individual cleanup step raises, the
remaining cleanup and finalization steps still run; the retained primary and
cleanup errors make completeness fail instead of leaving a misleading
`run did not finalize` sentinel.

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

## Phase 08.1 diagnostic activation

The schema-v3 suite is development-only and does not call the closed v2
orchestrator. Inspect all ten resolved contracts without Gazebo:

```bash
ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_1_diagnostic_activation.yaml \
  --operator "$USER" \
  --dry-run \
  --summary-output /tmp/phase08_1_m5_dry_run.yaml
```

M6 runs only predeclared selected cases under a new root such as
`~/Experiments/GESC-Gaussian/runs/phase08_1_m6`. Never point this command at
the historical `phase08_v2` root. Every probe is finite and serial:

```bash
PHASE08_1_ROOT=~/Experiments/GESC-Gaussian/runs/phase08_1_m6

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_1_diagnostic_activation.yaml \
  --operator "$USER" \
  --case-id activation_goal_high \
  --runs-root "$PHASE08_1_ROOT"
```

Use the live Phase 08 status for the next predeclared case. Do not dispatch the
whole ten-case suite merely because it is schema-valid.

## Phase 08.3 v3 workflow and retained attempts

Phase 08.3 uses a new root and flat workflow commands. It must never reuse the
historical v1, v2, Phase 08.1, or Phase 08.2 roots:

```bash
PHASE08_V3_ROOT=~/Experiments/GESC-Gaussian/runs/phase08_v3

ros2 run ros_esc validate_robustness v3-prepare \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3_ROOT"

ros2 run ros_esc validate_robustness v3-qualify \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3_ROOT"
```

These are command shapes, not a statement that either command or any v3
simulation ran. Follow the active Plan and live Phase 08 status. Later flat
subcommands are `v3-activation`, `v3-development`, `v3-freeze`, `v3-seal`,
`v3-holdout`, `v3-validation`, `v3-reproducibility`, and `v3-report`; every
one requires the same operator and evidence root, and each refuses an
out-of-order stage.

`v3-prepare` owns creation of the root: it must be absent on first entry. A
private mode-`0600` prepare transaction retains the canonical cleartext suite,
hash commitment, and input hashes so publication is resumable after an
interruption. The tracked suite is researcher-visible before activation and
is explicitly not selection-blind. It must be checkpointed and committed
unchanged before `v3-activation`; do not create the root manually, delete one
side of the transaction, or edit/regenerate the suite after preparation.

Fresh activation is a serial, GUI-visible diagnostic gate. Development,
holdout, additional validation, and reproducibility are serial headless
batches. Their schema/workflow settings own presentation; do not use `--gui`
to turn a batch into an interactive run. A `--dry-run` performs resolution and
qualification only and starts no ROS, Gazebo, rosbag, or hardware.

Every resolved schema-v4 case carries an immutable aggregate-truth record and
canonical result hash. Escape-designated cases also carry an immutable local
below-threshold proof. Freeze and acceptance records bind the implementation,
profile, scenario population, cost model, sensor geometry, suite, and
contract hashes. The acceptance contract hash is SHA-256 of canonical JSON
with the top-level `contract_sha256` field omitted; the inserted value must
match everywhere it is referenced. Never edit a sealed record in place.
A corrected contract or case is a new version before runtime, not a rewritten
attempt.

Every dispatched attempt keeps its original run directory, raw-bag hash,
scenario result, completeness result, analysis, and classification. A valid
behavioral miss is never replaced. An `infrastructure_invalid` attempt is
replaceable only when retained coordinator and bag evidence proves readiness
was never true, no nonzero command or robust lifecycle advance occurred, the
cause was external startup infrastructure, and cleanup permits a clean start.
The replacement uses the identical case, seed, profile, frozen hashes, and
contract; both attempts remain linked and no slot receives more than one
replacement.

Progress, attempt aggregates, replacement links, and all referenced
summary/record/error files are hashed. The terminal report rehashes them and
is itself create-once: a rerun verifies existing gate, manifest, report, and
failure-report bytes instead of overwriting drift. Qualification also freezes
the exact runtime-input map used by activation/development; M5 repeats the
isolated build and dry runs before the final implementation/profile freeze.

| Stage | Maximum replacement attempts |
|---|---:|
| Activation | 1 |
| Development | 3, at most one per candidate |
| Holdout | 1 |
| Additional validation | 2 |
| Reproducibility | 1 |
| **V3 total** | **8** |

Exceeding a stage or total cap, or a second invalid attempt for one slot, fails
the infrastructure gate. A later stage prohibited by an earlier gate is
recorded as `outcome: "not_run"` with `passed: null`; it is not a failed or
zero-valued run.

### V3A contact-control closeout and V3B restart

The original `/phase08_v3` activation root is closed and immutable after its
first expected-false case was struck by the validation contact-positive-control
probe. Do not resume that root or run only its nine undispatched cases.

After the M3A correction is tested, checkpointed, and committed, V3B adopts
the exact existing suite and commitment into a fresh lineage:

```bash
PHASE08_V3A_ROOT=~/Experiments/GESC-Gaussian/runs/phase08_v3
PHASE08_V3B_ROOT=~/Experiments/GESC-Gaussian/runs/phase08_v3b

timeout 1800s ros2 run ros_esc validate_robustness v3-adopt-precommit \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3B_ROOT" \
  --superseded-evidence-root "$PHASE08_V3A_ROOT"

timeout 1800s ros2 run ros_esc validate_robustness v3-qualify \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3B_ROOT"

timeout 10800s ros2 run ros_esc validate_robustness v3-activation \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3B_ROOT"
```

`v3-adopt-precommit` requires the V3B root to be absent, verifies the retained
V3A contamination hashes, compares the suite and commitment to V3A's recorded
precommit hashes, binds the fresh V3B root, operator, and corrected source
snapshot, and reuses the exact tracked population bytes without regeneration.
Resumed adoption rejects root, operator, or source drift. Qualification
revalidates that lineage and the installed probe-off launch arguments before
activation; activation rehashes the retained dry run and checks them again
before dispatch. Direct non-dry `run_scenario` calls for the formal v3
activation/development suites are rejected; use the workflow commands above.
Activation reruns all ten cases GUI-visible from the beginning. Contact
sensors remain enabled in every formal case, but the physical probe is enabled
only for an explicit `collision_expected=true` positive control.

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
