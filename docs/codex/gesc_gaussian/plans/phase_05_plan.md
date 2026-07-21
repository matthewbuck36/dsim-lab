# Phase 05 Plan — Unified GESC/Gaussian Experiment Recording

Artifact target: `docs/codex/gesc_gaussian/plans/phase_05_plan.md`

## Objective and scope

Implement one repository-native experiment-recording workflow for `robust_gaussian_v1` that:

- records the same canonical algorithm interfaces in Gazebo and future physical operation;
- validates required topic names, types, publishers, and recorder subscriptions before allowing motion;
- records with ROS 2 Humble rosbag2 using `sqlite3`;
- captures metadata, resolved parameters, Git state, console output, and shutdown evidence;
- produces a machine-readable completeness report;
- preserves the existing CSV collector and legacy launch behavior;
- adds no algorithm replacement, Heavy-Ball work, physical adapter, or hardware execution.

The Phase 05 planning validator passed:

```text
Phase 05 plan context is complete.
```

This planning turn is read-only. Save this document verbatim at the artifact target before opening the Phase 05 implementation chat.

## Repository findings relevant to Phase 05

- Repository: `/home/mattb/dsim-lab`
- Branch: `feature/gesc-gaussian-robustness-v1`
- Planning HEAD: `2e40388`
- ROS distribution: Humble.
- Installed rosbag writer/reader backend: `sqlite3`.
- `rosbag2_py`, `ros2bag`, `rosbag2_storage_default_plugins`, `rosidl_runtime_py`, `ament_index_python`, and `python3-yaml` are available.
- MCAP is not registered. Test-only rosbag plugins are present but must not be used.
- No repository-native rosbag runner, topic preflight, metadata workflow, parameter snapshotter, or completeness validator exists.
- The existing CSV owner is
  `ros2_ws/src/ros_esc/ros_esc/data_collection_node/data_collection_node_script.py`.
  It remains launch-integrated and unchanged.
- The current controller is the sole `/cmd_vel` and final-command owner. Phase 04 already provides signal-safe final-zero publication while the ROS context remains valid.
- The current launch has no simulation/physical recording gate. Therefore, merely starting rosbag cannot guarantee preflight before motion.
- The selected solution is an opt-in recorder heartbeat interlock in the existing controller. It is default-off and does not change unrecorded or legacy runs.
- Raw experiment data must remain outside Git, consistent with `.gitignore`. The default root will be:

```text
~/Experiments/GESC-Gaussian/runs
```

Pre-existing working-tree changes must be preserved:

- the user-owned light settings in
  `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`;
- the uncommitted `10.0`/`80.0` correction in
  `docs/codex/gesc_gaussian/topic_dictionary.md`;
- the existing untracked implementation-package and durable phase documents.

## Existing implementations to reuse or extend

- Keep `data_collection_node` as the legacy CSV/live-plot path. Rosbag becomes authoritative only for runs started through the new recorder.
- Reuse the canonical Phase 01–04 topics and message types. Do not aggregate or republish algorithm data through another node.
- Extend `CustomController` only with the recording-ready gate. Preserve its existing GESC calculation, supervisor arbitration, saturation, watchdog, diagnostics, and shutdown-zero path.
- Reuse `/gesc_gaussian/stop_requested` for robust shutdown initiation.
- Reuse the existing Gazebo launch graph. Do not create a second simulation launch graph.
- Reuse structured `AlgorithmState`, `AlgorithmEvent`, `CostBreakdown`, `GescDiagnostics`, `ControlDiagnostics`, and `GaussianFill` data as the authoritative record.
- Reuse `rosbag2_py` for offline validation and ROS message deserialization. Use the installed `ros2 bag record` CLI for recording and dynamic topic discovery.

## Recording architecture

### Entry points

Add two console entry points to the existing `ros_esc` package:

```text
record_run = ros_esc.experiment_recording.record_run:main
validate_run = ros_esc.experiment_recording.validate_run:main
```

Primary invocation:

```bash
ros2 run ros_esc record_run [recorder options] -- <target launch command and arguments>
```

The target command is passed as an argv list and launched without `shell=True`. This permits the same runner to manage the existing Gazebo launch and a future audited physical launch.

Offline validation:

```bash
ros2 run ros_esc validate_run <run-directory>
```

### Motion-safe startup

`record_run` will:

1. Validate the metadata input, manifest, backend, run ID, target command, and non-existing destination.
2. Create the unique run directory and initial failure-safe metadata.
3. Start publishing `/gesc_gaussian/recording_ready=False` at 10 Hz.
4. Start `ros2 bag record` before the target process, using the explicit manifest topic list and `--include-unpublished-topics`, so startup/configuration messages are not intentionally omitted.
5. Start the supplied target command and capture its stdout/stderr.
6. Wait for every mode-required topic with its exact type and at least one publisher.
7. Verify that `/custom_controller` subscribes to `/gesc_gaussian/recording_ready`; seeing only the rosbag subscription is insufficient.
8. Verify rosbag has subscribed to every required topic.
9. Require at least one gated zero message on `/cmd_vel` before readiness.
10. Capture resolved topics and active-node parameters.
11. Publish `/gesc_gaussian/recording_ready=True` only after all checks pass.

A missing topic, wrong type, missing controller interlock, missing recorder subscription, or timeout leaves readiness false, initiates safe shutdown, retains the failed run, and returns nonzero.

### Shutdown and final zero

Normal duration completion, Ctrl-C, target exit, and exceptions use the same shutdown sequence:

1. Publish `/gesc_gaussian/recording_ready=False`.
2. Publish `True` once on the existing `/gesc_gaussian/stop_requested` topic.
3. Keep rosbag active while waiting up to three seconds for new zero messages on:

   - `/cmd_vel`;
   - `/turtlebot3/control_value_chatter`;
   - `/gesc_gaussian/control_diagnostics`.

4. Record for another 0.5 seconds after the zero evidence.
5. Send SIGINT to the managed target process group and allow its Phase 04 signal-safe cleanup to finish.
6. Stop rosbag last with SIGINT and wait for its metadata/database finalization.
7. Run the completeness validator and finalize metadata atomically.

If zero evidence or clean process exit is absent, the bag is retained but the run fails completeness. Gazebo Classic exit code 255 is accepted only when it occurs after the requested shutdown and is attributable to the Gazebo process; ROS-node errors, tracebacks, `RCLError`, or invalid-context publication remain failures.

## Public interfaces and parameters

### New topic

| Topic | Type | Owner | Contract |
|---|---|---|---|
| `/gesc_gaussian/recording_ready` | `std_msgs/msg/Bool` | `record_run` | Reliable 10 Hz heartbeat; false during startup/shutdown, true only after preflight and recorder subscription checks |

No new message, service, action, interface package, or algorithm node is required.

### Controller and launch additions

| Argument | Default | Behavior |
|---|---:|---|
| `recording_ready_required` | `False` | Enables the recorder interlock when explicitly selected |
| `recording_ready_topic` | `/gesc_gaussian/recording_ready` | Heartbeat topic |
| `recording_ready_stale_sec` | `0.50` | Missing, false, nonfinite-time, or stale heartbeat forces zero |

When `recording_ready_required=False`, controller behavior is byte-for-byte the existing path. When true, the controller publishes zero until a fresh true heartbeat exists and immediately returns to zero on false/stale heartbeat. The interlock applies after existing state authorization and before final publication; it must not bypass or duplicate saturation.

### Recorder CLI

| Option | Default |
|---|---|
| `--mode` | Required: `simulation` or `physical` |
| `--metadata-input` | Required YAML |
| `--runs-root` | `~/Experiments/GESC-Gaussian/runs` |
| `--manifest` | Installed repository manifest |
| `--run-id` | Generated when omitted |
| `--storage-id` | `sqlite3` |
| `--duration-sec` | `0.0`, meaning until stopped |
| `--preflight-timeout-sec` | `45.0` |
| `--recorder-ready-timeout-sec` | `15.0` |
| `--shutdown-zero-timeout-sec` | `3.0` |
| `--target-exit-timeout-sec` | `15.0` |
| `--post-zero-record-sec` | `0.50` |
| `--recording-ready-rate-hz` | `10.0` |
| `--recording-ready-topic` | `/gesc_gaussian/recording_ready` |
| `--stop-topic` | `/gesc_gaussian/stop_requested` |

Only `sqlite3` is accepted by the checked-in default manifest. A requested backend must be present in `rosbag2_py.get_registered_writers()`.

## Required-topic manifest

Create a repository-specific schema with `schema_version`, exact topic/type, applicable modes, minimum message count, coverage policy, and semantic checks.

### Required in both modes

| Alias | Topic | Type |
|---|---|---|
| `source_cost` | `/gesc_gaussian/source_cost` | `ros_esc_interfaces/msg/CostBreakdown` |
| `cost_breakdown` | `/gesc_gaussian/cost_breakdown` | `ros_esc_interfaces/msg/CostBreakdown` |
| `gesc_diagnostics` | `/gesc_gaussian/gesc_diagnostics` | `ros_esc_interfaces/msg/GescDiagnostics` |
| `control_diagnostics` | `/gesc_gaussian/control_diagnostics` | `ros_esc_interfaces/msg/ControlDiagnostics` |
| `algorithm_state` | `/gesc_gaussian/algorithm_state` | `ros_esc_interfaces/msg/AlgorithmState` |
| `algorithm_events` | `/gesc_gaussian/algorithm_events` | `ros_esc_interfaces/msg/AlgorithmEvent` |
| `raw_cost_legacy` | `/turtlebot3/cost_value_chatter` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` |
| `augmented_cost_legacy` | `/cost_modified` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` |
| `filter_output_legacy` | `/turtlebot3/filter_value_chatter` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` |
| `command_array_final` | `/turtlebot3/control_value_chatter` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` |
| `command_final` | `/cmd_vel` | `geometry_msgs/msg/Twist` |
| `pose` | `/odom` | `nav_msgs/msg/Odometry` |
| `timekeeper` | `/turtlebot3/timekeeper_chatter` | `ros_esc_interfaces/msg/Timekeeper` |
| `recording_ready` | `/gesc_gaussian/recording_ready` | `std_msgs/msg/Bool` |

The manifest maps `raw_sensor`, `raw_cost`, and `source_score` logical concepts to fields in `source_cost`; they are not invented as separate topics.

Semantic validation:

- Simulation requires `SOURCE_SIMULATION`, valid raw cost, and valid normalized source score. `raw_sensor_valid=false` remains the documented simulator behavior.
- Physical mode requires `SOURCE_PHYSICAL`, valid raw sensor, valid raw cost, and valid calibrated source score. This is enforced when a future audited physical adapter is used.
- Successful Phase 05 runs require `algorithm_profile=robust_gaussian_v1`.

### Additional simulation-required topics

| Alias | Topic | Type |
|---|---|---|
| `clock` | `/clock` | `rosgraph_msgs/msg/Clock` |
| `encoder` | `/turtlebot3/encoder_chatter` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` |
| `sensor_transform` | `/turtlebot3/sensor_transform_chatter` | `ros_esc_interfaces/msg/StampedTransformMultiArray` |
| `joint_states` | `/joint_states` | `sensor_msgs/msg/JointState` |
| `sensor_rotation_command` | `/velocity_controller/commands` | `std_msgs/msg/Float64MultiArray` |

### Optional or event-conditional topics

Record these when present:

- `/gesc_gaussian/gaussian_fills`
- `/gesc_gaussian/convergence_status`
- `/gesc_gaussian/fill_requests`
- `/gesc_gaussian/supervisor_command`
- `/gesc_gaussian/stop_requested`
- `/cost_bias`
- `/pde_history`
- `/pde_cost_history`
- `/convergence_metric`
- `/convergence_r`
- `/convergence_count`
- `/convergence_event`
- `/tf`
- `/tf_static`

`/gesc_gaussian/gaussian_fills` is conditionally required: if an event or state reports a created, merged, superseded, or active fill, the bag must contain the corresponding lifecycle record. A run with no fill must not be failed merely because an event-driven fill topic has zero messages.

No collision or physical raw topic is named because the repository has no audited owner for either.

## Run directory and metadata

### Naming

Runs are stored as:

```text
~/Experiments/GESC-Gaussian/runs/<YYYY-MM-DD>/<run_id>/
```

Generated run IDs use:

```text
<YYYYMMDDTHHMMSSffffffZ>_<mode>_<scenario-slug>_<8-hex-uuid>
```

User-supplied IDs must match `[A-Za-z0-9][A-Za-z0-9._-]{0,127}`. Any existing destination is a hard failure; runs are never overwritten.

### Directory contents

```text
<run_id>/
├── bag/
├── metadata.yaml
├── resolved_parameters.yaml
├── resolved_topics.yaml
├── console.log
├── completeness.json
└── notes.md
```

### Metadata input and generated fields

The checked-in metadata template distinguishes operator-supplied fields from recorder-generated fields.

Operator-supplied required fields:

- experiment version;
- operator;
- mode and `robust_gaussian_v1` profile;
- scenario ID and deterministic seed;
- bounds, room center, starting pose, and source configuration;
- calibration file and source-score definition;
- parameter/config file paths;
- human-intervention declaration and notes.

Recorder-generated fields:

- run ID and UTC creation time;
- exact target argv and working directory;
- host, ROS distribution, RMW implementation, and `use_sim_time`;
- Git repository root, branch/detached state, full commit, dirty state, and diff hash;
- bag backend and ROS/wall start/end times;
- resolved topics, publishers, and recorder subscriptions;
- process exit and shutdown status;
- resolved parameter snapshot path;
- completeness result.

The dirty-tree hash is SHA-256 over a deterministic representation of:

- `git diff --binary HEAD`;
- sorted untracked paths;
- the SHA-256 content digest for each untracked file.

Raw diffs are not copied into the run unless a later plan explicitly requires that.

### Parameter snapshots

After preflight and before readiness:

- discover all active nodes;
- identify publishers of required topics;
- query every node exposing parameter services;
- serialize parameter names, types, values, capture time, and per-node failures into `resolved_parameters.yaml`;
- require successful snapshots for required-topic publishers that expose parameter services;
- retain the exact target argv and config-file paths for owners configured primarily through CLI/JSON rather than ROS parameters.

## Completeness validation

`validate_run` will use `rosbag2_py.SequentialReader`, `rosidl_runtime_py`, and generated message classes. It writes:

```json
{
  "schema_version": 1,
  "run_id": "...",
  "passed": true,
  "checks": {},
  "topic_counts": {},
  "failures": [],
  "warnings": []
}
```

A successful run requires:

- complete metadata and notes;
- sqlite3 bag metadata/database readable to EOF;
- every applicable required topic present with the exact type and at least one message;
- optional-topic presence/counts reported;
- successful parameter snapshot;
- simulation `/clock` present and non-regressing;
- typed/header timestamps within the selected ROS clock interval, with documented legacy relative timestamps excluded from absolute-clock checks;
- no material timestamp regression beyond a 50 ms scheduling tolerance;
- source-cost semantics matching the selected mode;
- state, source cost, cost breakdown, pose, GESC diagnostics, control diagnostics, and command topics spanning the motion interval within one second at each boundary;
- event `value_names` and `values` lengths matching;
- fill lifecycle messages whenever fill events/state require them;
- a final false recording-ready heartbeat;
- the last `/cmd_vel`, legacy command array, and typed final command all zero within `1e-9`;
- final-zero bag timestamps after the shutdown request and after the last nonzero command;
- rosbag finalization and clean target shutdown;
- no controller/supervisor `RCLError`, invalid-context publication, unexpected ROS-node death, or traceback in `console.log`.

For a no-motion diagnostic run, readiness-true to readiness-false defines the coverage interval. Failed runs retain all available artifacts and set `recording.completeness_passed=false`.

## Exact files proposed for modification

- `ros2_ws/src/ros_esc/setup.py`
  - Register `record_run` and `validate_run`.
  - Install the manifest and metadata template.

- `ros2_ws/src/ros_esc/package.xml`
  - Add runtime dependencies for `ament_index_python`, `ros2bag`, `rosbag2_py`, `rosbag2_storage_default_plugins`, `rosidl_runtime_py`, and `python3-yaml`.

- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`
  - Add the default-off recording heartbeat subscription and freshness gate.
  - Reuse `_publish_zero`, watchdog, diagnostics, and Phase 04 cleanup.

- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
  - Add and pass the three recording-interlock arguments to the existing controller declaration.
  - Do not add another algorithm or simulation graph.

- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`
  - Prove interlock-disabled behavior is unchanged and interlock faults publish zero.

- `ros2_ws/src/ros_esc/test/test_observability_contract.py`
  - Verify launch defaults, topic type, controller subscription wiring, and single `/cmd_vel` ownership.

- `docs/codex/gesc_gaussian/topic_dictionary.md`
  - Preserve the pre-existing percentile edit and document the recording topic, manifest, ownership, timing, and physical boundary.

- `docs/codex/gesc_gaussian/test_commands.md`
  - Record exact Phase 05 focused, package, validation, and simulation-smoke results.

## Exact files proposed for creation

- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/__init__.py`
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/record_run.py`
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/validate_run.py`
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/topic_manifest.yaml`
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/experiment_metadata.yaml`
- `ros2_ws/src/ros_esc/test/test_experiment_recording.py`
- `ros2_ws/src/ros_esc/test/test_recording_integration.py`
- `ros2_ws/src/ros_esc/test/fixtures/recording_smoke_metadata.yaml`
- `docs/codex/gesc_gaussian/handoffs/phase_05_handoff.md`

No new package or custom message is justified. `record_run` is a distinct recording/process-lifecycle owner, not a second algorithm implementation. `validate_run` is an offline CLI, not a ROS algorithm node.

## Backward compatibility and migration effects

- `algorithm_profile=legacy` remains the launch default.
- `recording_ready_required=False` preserves all existing controller behavior.
- The current GESC wrapper remains unchanged and therefore does not enable the interlock.
- The CSV collector, its directory format, plots, and legacy data files remain available.
- Existing topics, message schemas, cost sign, units, weights, command limits, and queue depths remain unchanged.
- No `ros_esc_interfaces` rebuild or ROS type-hash migration is introduced.
- Recorded robust runs use the new entry point and explicitly enable the interlock.
- A future physical launch must use the same shared controller, canonical topics, and recording-interlock arguments. Phase 05 provides the mode-aware workflow but does not invent or test absent physical adapters.
- Raw bags are retained after validation or later CSV extraction.

## Implementation sequence

The phase exceeds ten files because the recorder, offline validator, safety interlock, tests, installed schemas, and durable documentation are separate responsibilities. Split implementation into coherent commits:

1. `phase 05a: add rosbag recorder and completeness core`

   - Add dependencies, installed templates, recorder, validator, run naming, metadata, Git hashing, topic resolution, parameter snapshots, and synthetic-bag tests.

2. `phase 05b: gate motion on recording readiness`

   - Add the default-off controller heartbeat gate and launch arguments.
   - Add controller, launch, preflight, shutdown-zero, and legacy-equivalence tests.

3. `phase 05c: validate unified simulation recording`

   - Add the short Gazebo integration fixture/test.
   - Run one complete recorded simulation.
   - Update the topic dictionary, test record, and Phase 05 handoff.

## Tests and commands

### Context, build, and focused suite

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 05 implement
```

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
```

```bash
python3 -m pytest -q \
  src/ros_esc/test/test_experiment_recording.py \
  src/ros_esc/test/test_recording_integration.py \
  src/ros_esc/test/test_escape_recenter.py \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
```

Focused tests must cover:

- manifest schema, mode filtering, duplicate-topic de-duplication, and exact type validation;
- safe run-ID validation and refusal to overwrite;
- metadata input validation, atomic finalization, and deterministic Git hashing;
- parameter serialization and unavailable-node reporting;
- rosbag command construction using sqlite3 and explicit topics;
- preflight missing-topic, wrong-type, missing-publisher, missing-interlock, and missing-recorder-subscription failures;
- interlock false/missing/stale behavior and immediate zero;
- unchanged controller output when the interlock is disabled;
- readiness true enabling the existing authorized controller path;
- orderly shutdown ordering and final-zero wait;
- valid, missing-topic, wrong-type, truncated, clock-regressed, conditionally missing-fill, and nonzero-final-command synthetic bags;
- failed-run retention and nonzero exit status.

### Interface and launch checks

```bash
ros2 run ros_esc record_run --help
ros2 run ros_esc validate_run --help
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
  algorithm_profile:=robust_gaussian_v1 \
  use_pde_extensions:=True \
  recording_ready_required:=True \
  --show-args
```

### Short visible Gazebo recording

Run through the new entry point with no physical hardware:

```bash
DISPLAY=:0 ros2 run ros_esc record_run \
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
  recording_ready_stale_sec:=0.50 \
  cost_surface_start_delay_sec:=0.0 \
  show_cost_surface_plot:=False \
  live_plot_mode:=None \
  recenter_after_escape:=False \
  controller_config_filepath:=/home/mattb/dsim-lab/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage.json \
  cost_function_config_filepath:=/home/mattb/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json \
  data_collection_filepath:=/tmp/dsim_phase05_legacy_csv
```

The historical cost-model directory name does not enable Heavy-Ball control.

Acceptance requires:

- readiness remains false until every preflight and rosbag-subscription check passes;
- no nonzero `/cmd_vel` precedes readiness true;
- the bag uses sqlite3 and records every required simulation topic;
- metadata, parameters, topics, console, notes, and completeness artifacts exist;
- final false readiness and all three final-command representations are zero;
- the validator returns success;
- all ROS nodes exit cleanly without invalid-context errors;
- no physical hardware is addressed.

### Package and repository checks

```bash
colcon test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose
```

Report focused results separately from the documented 875 pre-existing lint failures.

```bash
cd ..
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_required_docs.sh
git diff --check
git status --short --branch
```

### Failed-run recovery documentation

Document these supported recovery steps:

```bash
ros2 bag reindex <run-directory>/bag
ros2 run ros_esc validate_run <run-directory>
```

A failed run is never deleted or reused. Diagnose it from `console.log`, `resolved_topics.yaml`, `metadata.yaml`, and `completeness.json`, then start a new run ID.

## Stop conditions and risks

Stop implementation and report exact evidence if:

- the Phase 05 implementation validator or saved plan is absent or fails;
- the Phase 04 handoff or signal-safe shutdown behavior is missing;
- unrelated user changes overlap a planned file and cannot be preserved;
- sqlite3 or required rosbag2 Python/runtime packages are unavailable;
- `--include-unpublished-topics` cannot capture dynamically appearing explicit topics without losing startup data;
- the recorder cannot verify its subscriptions before readiness;
- the controller interlock cannot hold zero without changing legacy behavior;
- final-zero evidence cannot be captured before rosbag shutdown;
- required publishers cannot provide exact audited topic types;
- timestamp checks cannot distinguish absolute typed stamps from documented legacy relative timestamps;
- the short Gazebo run cannot pass completeness;
- implementation would require a physical adapter, physical command, Heavy-Ball change, or second algorithm graph.

Principal risks:

- QoS negotiation for startup-only or transient topics;
- rosbag subprocess interruption before metadata finalization;
- multiple publishers on the algorithm event bus producing small timestamp reordering;
- duplicate disk I/O while the legacy CSV collector remains enabled;
- large raw bags;
- treating simulator source scores as physical calibration;
- claiming physical validation before Phase 09 provides an audited physical graph.

## Assumptions requiring implementation-time verification

- `ros2 bag record --include-unpublished-topics` works with the explicit manifest topic list in this Humble installation.
- The rosbag node appears in graph subscription introspection for every required topic.
- `/custom_controller` is discoverable as the interlock subscriber.
- `rosbag2_py.SequentialReader` can read the generated sqlite3 bag to EOF.
- The short Gazebo graph publishes all always-required topics within 60 seconds.
- Configuration events are captured because rosbag starts before the target.
- A 50 ms timestamp-regression tolerance avoids false failures from normal multi-publisher scheduling while still detecting clock resets.
- Event-driven Gaussian-fill data remains conditionally required.
- Future physical integration uses the same canonical source, cost, state, command, pose, timekeeper, and recording-ready interfaces.
- Physical execution and calibration validation remain deferred to Phase 09.
- The current working-tree changes listed above are preserved exactly.

## Amendment 1 — live-clock and shutdown corrections (user authorized)

Authorization date: 2026-07-21.

The first three retained visible recording attempts found runtime behavior
that the original plan could not verify in Plan mode. The user explicitly
authorized amending whatever is required to resolve these issues. This
amendment is part of the authoritative Phase 05 implementation handoff and is
bounded to the demonstrated recording acceptance failures.

### Evidence requiring the amendment

The clean evidence run is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/2026-07-21/
20260721T230813124669Z_simulation_phase05-short-recording_1e5e6063
```

- The existing robust supervisor used the system clock while other Gazebo
  owners used simulation time. Its structured configuration/state events had
  epoch-scale stamps interleaved with simulation stamps near zero.
- Single-owner typed streams showed bounded 0.1 second bag-order stamp
  regression under Humble/Gazebo scheduling. The original 50 ms threshold was
  too small for this measured graph.
- Expected preflight `recording_ready=False` was mirrored as a controller
  failsafe event and latched the supervisor before readiness.
- `pde_cost_history_node` used default rclpy signal handling and exited with
  code 245 during the managed group SIGINT, while the signal-safe Phase 04
  controller and supervisor exited cleanly.

### Authorized corrections

1. The Gazebo launch passes `use_sim_time:=True` to the robust supervisor.
   This makes simulation supervisor dwell, timeout, freshness, state stamps,
   and event stamps use the same ROS simulation clock as the rest of the
   robust graph. It is an explicit simulation correction; future physical
   launch wiring must select its configured physical clock and is not changed
   here.
2. Pre-clock configuration messages remain recorded but are excluded from the
   motion-interval absolute-clock check. Every typed message received from the
   first readiness-true heartbeat through the first subsequent false heartbeat
   must fall within the recorded `/clock` range.
3. The typed per-topic regression tolerance becomes a manifest-controlled
   `0.15 s`, justified by the measured `0.10 s` maximum plus one 50 ms
   scheduling margin. Larger regressions and all wall/simulation clock mixing
   still fail completeness.
4. Missing, false, or stale recording readiness always forces final zero but
   does not emit a supervisor-latching algorithm failsafe event. Recorder loss
   remains visible through readiness, final commands, metadata, console, and
   completeness. Existing non-recorder controller faults retain their current
   event behavior.
5. Extend the Phase 04 signal-safe executor/shutdown pattern to the existing
   `pde_cost_history_node`. No PDE calculation, topic, parameter, timestamp,
   or legacy numerical behavior changes.
6. Add focused tests for simulation-clock launch wiring, the amended 150 ms
   boundary, rejection beyond that boundary and outside `/clock`, non-latching
   recording faults, and PDE cost-history cleanup order.

If another existing ROS owner dies on a clean retry, stop and record its exact
process/evidence unless it has the identical default-rclpy shutdown pattern
and a focused, behavior-preserving extension is required for this same clean
recording gate.
