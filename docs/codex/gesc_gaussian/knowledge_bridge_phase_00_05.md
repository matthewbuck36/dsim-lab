# GESC + Robust Gaussian Knowledge Bridge Through Phase 05

## Purpose and authority

This file is the durable context bridge for a fresh Phase 06-10 Codex chat.
It describes the repository at branch `feature/gesc-gaussian-robustness-v1`,
HEAD `a7df8cf` when Phase 05.5 audited it. Current code/tests and the resolved
launch graph outrank this summary if the checkout later changes.

Source-of-truth order is: current code/tests; resolved interfaces/launch graph;
completed handoffs; saved plans; Phase 00 audit/maps; package specifications;
saved chats; experimental memory.

## Research direction

- Active controller: gradient-descent extremum seeking control (GESC).
- Active robustness mechanism: Gaussian augmentation/fill for undesired local
  minima, followed by measured escape and bounded recentering.
- Heavy-Ball ESC is inactive. Historical files remain for repository history
  and compatibility but are not in the active implementation or matrix.
- Current experimental field: light sources evaluated by the existing
  simulator/light-sensing model. `intensity_lumens` is relative to
  `reference_intensity_lumens`; it is not an absolute lux calibration.
- Acoustic source seeking is future motivation only. Do not convert the
  current graph to acoustic sensing.
- Robustness claims are limited to a declared, tested family of bounded,
  experimentally relevant multimodal fields. There is no universal guarantee
  for arbitrary nonconvex functions.

## Consolidated meeting interpretation

### Dr. Nili

Treat raw sensor-derived cost, Gaussian contribution, and affine/directional
assistance as independently observable and switchable. Search on raw GESC,
verify a converged extremum using a calibrated source criterion, hold safely at
the desired source, or fill and escape an undesired basin. Begin escape with
raw attraction disabled and pure Gaussian repulsion. Add bounded directional
assistance only after measured stall. Keep prior fills active, return to the
safe center in bounded mode, then resume search. Do not continue physical work
until simulation gates pass.

### Patrick data collection

ROS messages and rosbag2 are the experimental record. Record each block's
inputs/outputs, raw and augmented costs, weights, Gaussian parameters and
revisions, modes/transitions/events, pre/post-saturation commands, pose/motion,
timestamps, parameters, source/scenario configuration, and shutdown zeros.
Console output is a diagnostic mirror. Simulation and physical runs use the
same canonical algorithm topics.

### Patrick Gaussian whiteboard

The normalized exponential of negative squared distance is a kernel/softmax
weight. It is used for local center refinement and fill-cluster association.
A hard distance/overlap gate is mandatory because softmax alone can associate
distant minima. The adopted response to narrow/weak/miscentered fills is to
estimate the basin, broaden the fill, couple amplitude and width, validate a
local augmented model for residual minima, merge overlapping candidates, and
fail safely if bounded redesign cannot remove the fitted residual minimum.

## Implemented state-machine policy

| State | Weights `(raw, Gaussian, affine)` | Motion policy |
|---|---:|---|
| `SEARCH` | `(1,1,0)` | GESC search with retained fills |
| `VERIFY_EXTREMUM` | `(1,1,0)` | Zero while source-score dwell is checked |
| `DESIGN_OR_MERGE_FILL` | `(0,1,0)` | Zero while fill design completes |
| `ESCAPE_REPULSE` | `(0,1,0)` | Pure Gaussian-driven escape |
| `ESCAPE_ASSIST` | `(0,1,1)` | Gaussian plus bounded directional assistance |
| `RECENTER` | `(0,1,0)` | Supervisor-only center-return command |
| `GOAL_HOLD` | `(0,1,0)` | Latched zero |
| `FAILSAFE` | `(0,0,0)` | Latched zero |

Raw cost acquisition and publication continue while its weight is zero.
Stable escape uses frozen fill center/exit radius, radial progress, exit hold,
and a common escape deadline. One stall may request one same-cluster redesign;
accepted redesign enters assisted escape without moving the frozen geometry.
Invalid/stale/nonfinite inputs, bounds/safe-direction failures, timeout,
explicit stop, exception, recording-gate failure, and shutdown produce zero.

## Basin fill and merge behavior

`gaussian_fill` synchronizes `/odom` and `/gesc_gaussian/source_cost`, rejects
invalid/stale/regressed/jump/outlier samples, initializes at minimum raw cost,
uses stable spatial/cost kernel weights, estimates clipped PSD covariance and
a regularized quadratic model, derives depth and curvature, and designs a
broader anisotropic fill. A 41-by-41 local grid checks for residual interior
minima. Bounded escalation increases amplitude, then width while scaling
amplitude with width squared.

Candidate merging requires both soft association and a sigma-scaled hard
overlap gate. A merge combines retained samples and publishes an immutable
superseded revision followed by one replacement revision. Robust modified cost
consumes only typed `GaussianFill` lifecycle records, so `/cost_bias` cannot
double-count the same robust fill. Well-separated active clusters are summed.

## Current repository architecture

ROS workspace: `ros2_ws`. Packages:

- `ros_esc`: cost, filter, controller, convergence, Gaussian, supervisor,
  recording, data collection, and plotting owners.
- `ros_esc_interfaces`: the sole custom interface package.
- `turtlebot3_rotating_sensor`: Gazebo/robot description, central launch, and
  experiment wrappers.

Shared graph owners:

- simulated source/cost: `ros_esc/ros_esc/cost_function_node/`;
- cost composition and active typed fill evaluation:
  `ros_esc/ros_esc/modified_cost_node/`;
- GESC filter: `ros_esc/ros_esc/filter_node/`;
- final command and sole `/cmd_vel` ownership:
  `ros_esc/ros_esc/controller_node/`;
- convergence: `ros_esc/ros_esc/convergence_detector_node/`;
- basin estimation/design/registry and fill publication:
  `ros_esc/ros_esc/gaussian_fill_node/`;
- state, escape, assistance, recenter, and stop policy:
  `ros_esc/ros_esc/supervisor_node/`;
- central simulation graph:
  `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`;
- sole unified recorder:
  `ros_esc/ros_esc/experiment_recording/record_run.py`;
- sole completeness validator:
  `ros_esc/ros_esc/experiment_recording/validate_run.py`.

No scenario/matrix runner, physical Vicon adapter, physical photoresistor
adapter, physical launch graph, Nav2 integration, or physical calibration
workflow exists in this checkout through Phase 05.

## Phase 00-05 implementation status

### Phase 00 — audit

Created the five durable audit/map documents and Phase 00 handoff. It changed
no ROS behavior. It established the negative-voltage minimization convention,
existing PDE/Gaussian owners, lack of physical adapters/planner/recorder, and
the inherited repository-wide lint baseline of 875 failures.

### Phase 01 — typed observability

Added six messages and opt-in typed publications from existing owners while
preserving legacy arrays and numerical behavior. Focused result: 16 passed.
Global result then: 901 tests, 875 inherited failures, 1 skipped.

### Phase 02 — robust supervisor and switchable terms

Added the eight-state `robust_gaussian_v1` supervisor, source-score model
normalization, explicit weights, correlated fill request/result boundary,
controller arbitration/watchdogs, and zero-command failsafe. Focused result:
44 passed. Global: 929 tests, 875 inherited failures, 1 skipped.

### Phase 03 — robust basin fill

Added pure estimator/designer/registry helpers inside the existing fill owner,
anisotropic fill lifecycle, residual-minimum escalation, merge/revision/
supersession, and typed robust cost consumption. Focused: 65 passed. Global:
950 tests, 875 inherited failures, 1 skipped.

### Phase 04 — measured escape and recenter

Added frozen escape geometry, radial progress/stall, one redesign, deterministic
boundary/fill-aware assistance, and bounded recentering. Runtime-discovered
double parameter typing and rclpy shutdown ordering were approved as a bounded
amendment: `10.0`/`80.0`, `SignalHandlerOptions.NO`, bounded executor loop, and
zero publication before context teardown. Final focused: 93 passed. Global:
978 tests, 875 inherited failures, 1 skipped. Visible Gazebo startup and
controlled SIGINT passed; ROS processes exited cleanly.

### Phase 05 — unified recording

Added one sqlite3 rosbag workflow, explicit manifest, metadata/Git/parameter
capture, required-topic/type/publisher/subscriber preflight, controller
readiness interlock, final-zero recording, protected descendant cleanup, and
completeness validation. Final focused: 113 passed, 1 environment-gated skip.
Global: 999 tests, 0 errors, 875 inherited failures, 2 skipped. The accepted
short run reports no failures or warnings and all 19 required topics present.

## Public messages and topics

Messages under `ros_esc_interfaces/msg/`:

- `CostBreakdown.msg`
- `GescDiagnostics.msg`
- `ControlDiagnostics.msg`
- `GaussianFill.msg`
- `AlgorithmState.msg`
- `AlgorithmEvent.msg`
- legacy `Timekeeper`, `StampedFloat64`, `StampedFloat64MultiArray`,
  `StampedString`, and `StampedTransformMultiArray` messages.

Canonical robust topics:

| Topic | Type | Current owner |
|---|---|---|
| `/gesc_gaussian/source_cost` | `CostBreakdown` | `cost_function` |
| `/gesc_gaussian/cost_breakdown` | `CostBreakdown` | selected final cost owner |
| `/gesc_gaussian/gesc_diagnostics` | `GescDiagnostics` | `custom_filter` |
| `/gesc_gaussian/control_diagnostics` | `ControlDiagnostics` | `custom_controller` |
| `/gesc_gaussian/gaussian_fills` | `GaussianFill` | `gaussian_fill` |
| `/gesc_gaussian/algorithm_state` | `AlgorithmState` | robust supervisor |
| `/gesc_gaussian/algorithm_events` | `AlgorithmEvent` | existing event owners |
| `/gesc_gaussian/convergence_status` | `StampedFloat64MultiArray` | convergence detector |
| `/gesc_gaussian/fill_requests` | `StampedFloat64MultiArray` | supervisor |
| `/gesc_gaussian/supervisor_command` | `geometry_msgs/Twist` | supervisor |
| `/gesc_gaussian/stop_requested` | `std_msgs/Bool` | operator/runner |
| `/gesc_gaussian/recording_ready` | `std_msgs/Bool` | `record_run` |

Preserved legacy topics include `/turtlebot3/cost_value_chatter`,
`/cost_modified`, `/cost_bias`, `/turtlebot3/filter_value_chatter`,
`/turtlebot3/control_value_chatter`, `/cmd_vel`, `/odom`, `/pde_history`,
`/pde_cost_history`, `/convergence_*`, `/tf`, and `/tf_static`.

## Profiles and exact parameter surfaces

Profiles are `legacy` (default) and `robust_gaussian_v1` (opt-in). Legacy
retains existing topics, arrays, arithmetic, Gaussian path, and controller.
Robust requires PDE extensions, typed observability, the supervisor, and the
directional controller.

Central launch defaults:

```text
enable_observability=False
algorithm_profile=legacy
supervisor_publish_rate_hz=20.0
startup_timeout_sec=5.0
convergence_hold_sec=2.0
goal_score_threshold=0.95
goal_hold_sec=3.0
undesired_score_hold_sec=3.0
verification_max_sec=10.0
fill_design_timeout_sec=5.0
escape_max_sec=20.0
escape_exit_hold_sec=1.0
stall_window_sec=3.0
minimum_radial_progress_m=0.05
approach_history_window_sec=3.0
recenter_after_escape=True
recenter_max_sec=30.0
room_bounds_x_min_m=-2.0
room_bounds_x_max_m=2.0
room_bounds_y_min_m=-2.0
room_bounds_y_max_m=2.0
room_center_x_m=0.0
room_center_y_m=0.0
wall_margin_m=0.35
direction_lookahead_m=0.50
direction_candidate_step_rad=0.7853981633974483
fill_avoidance_margin_m=0.10
recenter_tolerance_m=0.25
recenter_hold_sec=1.0
recenter_linear_gain=0.50
recenter_angular_gain=1.50
recenter_max_linear_velocity_mps=0.10
recenter_max_angular_velocity_rps=0.40
recenter_rotate_in_place_angle_rad=1.0471975511965976
stale_pose_sec=0.50
stale_sensor_sec=0.50
supervisor_state_stale_sec=0.50
supervisor_command_stale_sec=0.50
command_watchdog_rate_hz=20.0
zero_command_on_shutdown=True
recording_ready_required=False
recording_ready_stale_sec=0.50
supervisor_use_sim_time=True
```

Canonical topic defaults are the topic names in the preceding table. Robust
fill launch defaults, mapped by removing `gaussian_fill_`, are:

```text
pose_topic=/odom
estimation_channel_index=0
sample_sync_tolerance_sec=0.05
maximum_position_speed_mps=0.20
outlier_mad_threshold=3.5
maximum_cluster_samples=4000
estimation_window_sec=8.0
minimum_valid_samples=40
maximum_sample_age_sec=12.0
mean_shift_iterations=5
center_tolerance_m=0.005
position_kernel_bandwidth_m=0.25
cost_temperature_normalized=0.05
covariance_eigenvalue_min_m2=0.0025
covariance_eigenvalue_max_m2=0.25
quadratic_ridge_lambda=1e-6
quadratic_condition_number_max=1e8
center_cost_percentile=10.0
shoulder_cost_percentile=80.0
inner_mahalanobis_radius=1.0
minimum_basin_depth=0.02
covariance_scale=2.5
sigma_floor_m=0.15
sigma_ceiling_m=1.25
amplitude_depth_scale=1.5
amplitude_curvature_scale=1.2
amplitude_min=0.10
amplitude_max=3.00
validation_grid_points_per_axis=41
validation_support_sigma=3.0
maximum_design_escalations=5
amplitude_escalation_factor=1.5
width_escalation_factor=1.25
grid_minimum_tolerance=1e-9
support_sigma=3.0
exit_sigma=2.5
merge_bandwidth_m=0.50
merge_radius_scale=2.0
minimum_merge_probability=0.60
low_confidence_threshold=0.60
```

`topic_dictionary.md` is the exhaustive parameter-to-node and typed-field
reference. Future code must read live launch/source rather than copy defaults
blindly from this bridge.

## Phase 05 recording foundation

Authoritative source paths:

- runner: `ros2_ws/src/ros_esc/ros_esc/experiment_recording/record_run.py`;
- validator: `ros2_ws/src/ros_esc/ros_esc/experiment_recording/validate_run.py`;
- manifest: `ros2_ws/src/ros_esc/ros_esc/experiment_recording/topic_manifest.yaml`;
- metadata template: `ros2_ws/src/ros_esc/ros_esc/experiment_recording/experiment_metadata.yaml`;
- QoS: `ros2_ws/src/ros_esc/ros_esc/experiment_recording/qos_overrides.yaml`;
- operator guide: `docs/codex/gesc_gaussian/recording_runs.md`.

Installed entry points are `ros2 run ros_esc record_run` and
`ros2 run ros_esc validate_run`. Runs live under
`~/Experiments/GESC-Gaussian/runs/<YYYY-MM-DD>/<run_id>/` and contain
`bag/`, `metadata.yaml`, `resolved_topics.yaml`,
`resolved_parameters.yaml`, `console.log`, `completeness.json`, and `notes.md`.
Phase 06 must compose this workflow. It must not add another recorder, format,
readiness gate, or validator.

Accepted retained smoke:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/2026-07-21/
20260721T232824094290Z_simulation_phase05-short-recording_92bb8be7
```

Its `completeness.json` has `passed: true`, zero failures/warnings, 19 required
topics with messages, all three final-zero forms, clean target/bag exits, and
21 of 23 live-node parameter snapshots; the two optional spawners exited before
snapshot calls.

## Authoritative verification commands

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 06 plan

source /opt/ros/humble/setup.bash
cd /home/mattb/dsim-lab/ros2_ws
colcon build --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
python3 -m pytest -q \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_escape_recenter.py \
  src/ros_esc/test/test_experiment_recording.py \
  src/ros_esc/test/test_recording_integration.py

colcon test --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose

cd /home/mattb/dsim-lab
git diff --check
```

The accepted bag can be revalidated after sourcing the workspace:

```bash
ros2 run ros_esc validate_run \
  /home/mattb/Experiments/GESC-Gaussian/runs/2026-07-21/20260721T232824094290Z_simulation_phase05-short-recording_92bb8be7
```

## Known limitations and unresolved research questions

- The global lint baseline remains 875 inherited failures. Focused behavior
  tests are green and must be reported separately.
- `raw_sensor_value` and `filtered_sensor_value` are unavailable in the current
  simulator adapter; raw minimization cost remains valid and continuously
  recorded.
- Source score is model-range normalization, not absolute photometry.
- Residual-minimum validation uses a fitted local model, not the unknown whole
  field.
- `/cost_bias` is lossy and cannot retract superseded anisotropic revisions;
  typed fills are authoritative in robust mode.
- Bounds are a virtual envelope; there is no wall/contact sensor or complete
  path planner.
- The accepted Phase 05 run proves recording/shutdown, not fill/escape/recenter
  success; it contains no fill lifecycle event and used a short smoke setup.
- Parameter snapshotting can add about 90 seconds while motion remains gated.
- No automated scenario infrastructure exists yet.
- No physical adapters or authorization have been established.
- Final tuning, robustness rates, holdout behavior, and repeated full-suite
  results remain Phase 08 work.

## Lessons from Phase 04 and Phase 05 interruptions

- `--show-args` does not prove rclpy runtime parameter types; instantiate the
  graph. Double parameters need double-form defaults.
- Shutdown-zero publication must occur while `rclpy.ok()` is true, before ROS
  context teardown.
- A recording gate must be enforced by the final command owner, not operator
  convention.
- Topic presence alone is insufficient: verify exact types, endpoint counts,
  recorder subscriptions, and the final command gate.
- Simulation-clock alignment, publisher ownership, parameter-service behavior,
  and descendant cleanup are runtime facts. Local testable corrections belong
  in a documented Level B amendment.
- Preserve failed run artifacts and distinguish intermediate from final test
  totals.

## Requirements for Phase 06

- Inspect first for existing scenario/sweep/matrix runners; none existed at
  this audit, but recheck the live tree.
- Add only a distinct orchestration owner if needed. Do not duplicate cost,
  supervisor, fill, controller, launch, recorder, or validator ownership.
- Compose `record_run` and `gazebo.launch.xml`; every run must be recorded.
- Run serially by default with deterministic seeds, unique IDs, timeout,
  cleanup/graph verification, retained failures, and matrix summaries.
- Use actual source/start-pose/bounds/profile arguments. Record unsupported
  noise/delay or ground-truth dimensions rather than inventing infrastructure.
- Separate controller-observable goal success from simulator ground truth.
- Cover supported smoke, two-/three-source, separation/overlap, wall/corner,
  close-minimum, multiple-start, saturation, escape/assist, merge, recenter,
  legacy regression, and ablation families.

## Requirements for Phases 07-10

- Phase 07: read sqlite3 bags and real message types/manifest, preserve raw
  timestamps/bags, mark critical missing data, synchronize explicitly, analyze
  successful and failed runs, and compute escape/state/fill/command/revisit/
  saturation metrics.
- Phase 08: separate tuning and holdout scenarios, freeze one parameter set,
  run the final matrix and three unchanged repetitions, report Level C failures,
  and tag simulation-ready only if all declared gates pass.
- Phase 09: require the simulation-ready gate and explicit authorization;
  inventory physical adapters, reuse the shared algorithm and Phase 05
  recording graph, and stop on any safety or architectural hard contradiction.
- Phase 10: update real repository docs from final live evidence, keep
  Heavy-Ball only as history, document verified commands/parameters/results,
  and state limitations honestly.

## Files every future chat reads first

1. `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
2. `00_MASTER_IMPLEMENTATION_PLAN.md`
3. `01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md`
4. the phase-specific package specifications
5. `docs/codex/gesc_gaussian/repo_audit.md`
6. `docs/codex/gesc_gaussian/repo_map.md`
7. `docs/codex/gesc_gaussian/interface_map.md`
8. `docs/codex/gesc_gaussian/test_commands.md`
9. `docs/codex/gesc_gaussian/implementation_sequence.md`
10. this knowledge bridge
11. all completed handoffs, including `phase_05_5_handoff.md`
12. the saved plan for the current Implement phase
13. current Git status/history and the live source/launch/tests in scope
