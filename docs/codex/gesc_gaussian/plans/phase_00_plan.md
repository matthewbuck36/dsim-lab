# Phase 00 Plan — Read-Only Repository Audit

## Objective and scope

Create the durable Phase 00 repository audit for the GESC + robust Gaussian
work without changing ROS source code, launch behavior, parameters, public
interfaces, or physical hardware. The audit must convert the implementation
package's logical architecture into the exact packages, nodes, topics, message
types, launch files, and tests present in this checkout.

Heavy-Ball ESC is outside this work. Existing Heavy-Ball files may be identified
as compatibility context, but they must not be redesigned or extended.

## Repository state at planning time

- Repository root: `/home/mattb/dsim-lab`
- ROS workspace root: `ros2_ws`
- Branch: `feature/gesc-gaussian-robustness-v1`
- Existing user-owned modified file that must not be changed:
  `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`
- The implementation package is untracked and must be preserved as the project
  specification and prompt record.
- No prior files existed under `docs/codex/gesc_gaussian/` when this plan was
  completed.

Phase 00 has no prior-phase handoff requirement. The absence of
`phase_00_handoff.md` is expected until Phase 00 implementation completes.

## Workspace and package findings

The repository contains one ROS 2 workspace and three ROS packages:

| Package | Path | Build type | Role |
|---|---|---|---|
| `ros_esc` | `ros2_ws/src/ros_esc` | `ament_python` | ESC nodes, cost models, Gaussian/PDE extensions, logging, and plotting |
| `ros_esc_interfaces` | `ros2_ws/src/ros_esc_interfaces` | `ament_cmake` | Custom ROS messages |
| `turtlebot3_rotating_sensor` | `ros2_ws/src/turtlebot3_rotating_sensor` | `ament_cmake` | TurtleBot/Gazebo description, launch files, controller wiring, and experiment wrappers |

The top-level `extremum-seeking` directory is a conventional Python library,
not a ROS package.

The existing interface package defines:

- `ros2_ws/src/ros_esc_interfaces/msg/Timekeeper.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/StampedFloat64.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/StampedFloat64MultiArray.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/StampedString.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/StampedTransformMultiArray.msg`

The audit must distinguish declared package dependencies from effective Python
imports. In particular, `ros_esc/package.xml` does not fully describe every
ROS message package and Python library imported by the current nodes.

## Existing GESC implementation

The audit must document and preserve these current owners:

- Dither/frame rotation:
  `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_node_script.py`
  and
  `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/spin_profile_objects/spin_profile_objects.py`.
  The active full-rotation profile uses `Constant_Full_Rotation`; the current
  experiment wrapper runs the sensor at 20 RPM, approximately
  `2.09439510239 rad/s`.
- Gradient filter:
  `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_node_script.py` with
  `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json`.
  Its inputs are cost and encoder angle. It applies a washout filter to cost,
  forms geometric signals `(2/d) cos(phi)` and `(2/d) sin(phi)` with
  `d = 0.18`, and produces the signed two-axis gradient estimate.
- Directional control:
  `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`,
  `controller_objects/turtlebot_vehicle.py`, and
  `controller_objects/turtlebot_ode_objects.py`, using
  `gesc_controller_full_rotation_voltage.json`.
  The audited active gains are `k_vx = 1.0` and `k_wz = 5.0`; configured command
  limits are `0.1 m/s` linear and `0.5 rad/s` angular.
- The controller publishes `/cmd_vel` and
  `/turtlebot3/control_value_chatter`. The current diagnostic output exposes
  the post-saturation command but does not expose the complete internal filter
  state or pre-saturation command.

Phase 01 must extend these existing owners for observability rather than create
a parallel controller or filter graph.

## Existing convergence and Gaussian-fill implementation

The current pipeline is owned by:

- `ros2_ws/src/ros_esc/ros_esc/pde_history_node/pde_history_script.py`
- `ros2_ws/src/ros_esc/ros_esc/pde_cost_history_node/pde_cost_history_script.py`
- `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`
- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`

Current behavior to record:

- `pde_history_node` consumes hard-coded `/odom`, keeps a PDE/upwind position
  history, and publishes flattened position history on `/pde_history`.
- `pde_cost_history_node` consumes the configured cost topic and publishes
  unstamped `/pde_cost_history`. The active Gaussian launch routes it to
  `/cost_modified`.
- The convergence detector compares recent and older PDE-history means,
  publishes `/convergence_metric`, `/convergence_r`, `/convergence_count`, and
  `/convergence_event`, and triggers on a positive-to-negative threshold
  crossing after the configured event count and startup gate.
- The active launch values `threshold = 0.2`, `decay = 0.15`,
  `min_fill_periods = 2`, `omega = 5`, and `k = 20` imply a startup gate of
  approximately `50.27 s`.
- A convergence-event payload contains metric, residual, decay, recent mean,
  old mean, and event count values in the current stamped array convention.
- `gaussian_fill_node` performs an isotropic inverted-Gaussian least-squares
  fit, normally anchors the published fill to the convergence-event mean,
  bounds fitted-center movement, publishes a configured amplitude, adapts
  sigma within configured limits, applies cooldown and distance-based duplicate
  rejection, and publishes the legacy `/cost_bias` array
  `[amplitude, center_x, center_y, sigma]`.
- `modified_cost_node` stores accepted Gaussian terms in a persistent list,
  sums every retained fill, and optionally creates a decaying affine term.
  Raw cost remains active at all times:
  `modified_cost = raw_cost + gaussian_terms + affine_term`.

Already implemented behavior that must be extended rather than duplicated:

- convergence-event gating and counting;
- convergence-event mean anchoring;
- bounded fitted centers;
- configurable/adaptive isotropic sigma;
- persistent multi-fill summation;
- duplicate-distance rejection;
- a decaying affine term.

Behavior not currently implemented:

- independently switchable raw/Gaussian/affine weights;
- an explicit hybrid controller state machine;
- source-score verification;
- robust synchronized outlier rejection and covariance estimation;
- anisotropic or curvature/depth-derived fills;
- residual-minimum checking and escalation;
- soft association, true merging, revisions, and supersession;
- measured escape progress/stall handling;
- bounded recentering;
- a unified failsafe supervisor.

## Simulation, physical, and pose wiring

- Gazebo differential drive publishes `/odom` and consumes `/cmd_vel`.
- `sensor_pose_node` combines `/odom` with encoder angle and publishes sensor
  transforms used by the cost model.
- `cost_function_node` is the simulation cost owner.
  `Photoresistor_Interpolated_Map` models the legacy single-light response;
  `Multi_Light_Source_Cost` combines multiple directional light contributions.
- `intensity_lumens / reference_intensity_lumens` is a relative simulator
  scaling, not an absolute lux calibration.
- Gazebo's visual point lights are not themselves the mathematical cost field;
  the software cost model is separate.
- This checkout contains no canonical Vicon adapter, physical photoresistor
  acquisition node, physical launch graph, Nav2/planner integration, or
  recenter implementation.
- Current PDE/Gaussian nodes use simulation time and `/odom` assumptions that
  must be abstracted before physical integration.

Phase 09 must begin with a physical-interface inventory and must stop rather
than invent filenames, topics, message types, or hardware wiring.

## Launch profiles and compatibility

The central launch entry point is:

`ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`

The active GESC + Gaussian wrapper is:

`ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`

Important audited behavior:

- `use_pde_extensions` defaults to false.
- With PDE extensions disabled, the filter consumes raw cost.
- With PDE extensions enabled, the modified-cost, PDE-history,
  convergence-detector, and Gaussian-fill nodes are launched and the filter
  consumes `/cost_modified`.
- `escape_policy` currently aliases `none`, `conditional_gaussian_fill`, and
  `multi_gaussian_fill`.
- The default controller configuration in the generic Gazebo launch is
  Heavy-Ball while the active GESC wrapper overrides it with the GESC
  configuration. Future phases must not change Heavy-Ball behavior and must
  keep the GESC robust behavior opt-in.
- Existing user-edited light-source values in the active wrapper must be
  preserved.

Public topics, cost sign, units, legacy array layouts, launch arguments, and
default legacy behavior must remain compatible unless a documented migration
adds parallel typed observability.

## Existing recording and tests

`ros2_ws/src/ros_esc/ros_esc/data_collection_node/data_collection_node_script.py`
currently writes timestamped experiment directories under
`~/Experiments/Gazebo-Simulations/` containing:

- `odometry.csv`
- `sensor_transform.csv`
- `cost_value.csv`
- `filter_value.csv`
- `control_value.csv`
- `comments.txt`

In the current PDE mode, `cost_value.csv` records `/cost_modified` rather than
raw and augmented costs simultaneously. The live cost-surface plotter can save
a PNG into the newest run directory. No repository-native rosbag recorder,
required-topic preflight, run metadata contract, or bag parser currently
exists.

The environment provides ROS 2 Humble, `rosbag2_py`, and the default sqlite3
storage plugin. MCAP was not available during the audit.

The audited build command passed:

```bash
source /opt/ros/humble/setup.bash
colcon build --base-paths ros2_ws/src \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
```

The existing test suite is primarily lint-oriented and is not clean. The audit
observed 885 tests, 875 failures, and 1 skipped test across the selected
packages, dominated by existing flake8/pep257 failures. There are no focused
algorithmic unit, launch, or end-to-end tests for the Gaussian pipeline.
Phase 00 must record the baseline rather than misrepresent it as a regression
caused by later work.

## Required Phase 00 outputs

Phase 00 implementation must inspect the current checkout again and create:

- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/handoffs/phase_00_handoff.md`

The implementation must stop and document a contradiction if the current
checkout no longer supports a finding in this plan.

## Proposed Phase 01–10 implementation sequence

### Phase 01 — Observability

Extend `ros_esc_interfaces` and the existing GESC/filter/controller,
modified-cost, convergence, Gaussian-fill, and simulation-source owners.
Add typed cost, state/event, fill, control, escape, and environment diagnostics
only after the audit confirms the minimal message set. Preserve all existing
legacy topics and arrays. Add unit and launch tests that prove every canonical
signal is timestamped and populated without changing algorithm behavior.

### Phase 02 — State machine

Extend current algorithm owners and add a supervisor only if the Phase 00
architecture map confirms no existing node owns state coordination. The
proposed location is:

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/__init__.py`
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py`

Add robust and legacy parameter profiles using the repository's existing config
and launch conventions. Test every transition, timeout, source verification,
weight output, and zero-command failsafe.

### Phase 03 — Robust Gaussian redesign

Refactor and extend the existing Gaussian-fill node rather than replace its ROS
wiring. Proposed internal modules, subject to the final Phase 00 map:

- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/basin_estimator.py`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_designer.py`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_registry.py`

Implement synchronized samples, robust center/covariance estimation, regularized
local fitting, coupled width/amplitude design, residual-minimum checks,
escalation, association/merge, revisions, supersession, confidence, and
deterministic numerical tests. Keep `/cost_bias` as a legacy compatibility
output.

### Phase 04 — Escape and recenter

Extend the supervisor with measured progress, deterministic assisted escape,
boundary-aware direction selection, and recentering. Proposed internal module:

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/escape_recenter.py`

Reuse an existing planner only if Phase 00 discovers one; otherwise implement
the smallest bounded-environment behavior approved by the phase plan. Keep
retained fills active throughout escape and recenter.

### Phase 05 — Recording

Add a repository-native experiment-recording area under the audit-approved
package, with proposed files:

- `experiment_recording/record_run.py`
- `experiment_recording/validate_run.py`
- `experiment_recording/topic_manifest.yaml`
- `experiment_recording/experiment_metadata.yaml`

Record raw and augmented costs, all controller contributions, state/events,
fills, commands, poses, transforms, environment configuration, and parameters.
Keep existing CSV workflows available as legacy outputs.

### Phase 06 — Scenario runner

Add deterministic serial Gazebo execution under an audit-approved
`scenario_runner/` area:

- `scenario_runner/run_scenario.py`
- `scenario_runner/scenario_schema.py`
- scenario-suite YAML files for smoke, source layouts, boundaries,
  noise/delay, and ablations.

Use the existing launch graph, enforce seed/timeout/clean shutdown, and do not
add a physical execution path.

### Phase 07 — Analysis

Extend the existing plotting/analysis package rather than create a disconnected
workflow. Proposed internal files:

- `bag_reader.py`
- `gesc_gaussian_bag_analysis.py`

Read the actual Phase 05 bag backend, preserve timestamps, export CSV, compute
the required escape/revisit/state/saturation metrics, and generate separate
diagnostic figures. Add generated or small known fixtures.

### Phase 08 — Validation

Add the final validation runner, scenario matrices, and report under
`docs/codex/gesc_gaussian/validation/`. Separate tuning scenarios from holdouts,
freeze one parameter set before holdout evaluation, run the required repeated
suite, and report failed gates honestly without tagging simulation-ready.

### Phase 09 — Physical integration

Do not guess source paths. The first deliverable must be:

`docs/codex/gesc_gaussian/phase09_physical_interface_inventory.md`

Proceed only after the simulation-ready gate and explicit hardware approval.
Wire audited photoresistor and Vicon/pose adapters into the same canonical
algorithm interfaces; do not fork the algorithm.

### Phase 10 — Documentation

Update the repository's real READMEs and add the approved architecture,
algorithm, topic, parameter, experiment, reproducibility, results, and
limitations documentation under `docs/codex/gesc_gaussian/`. All commands and
links must be verified against artifacts produced by prior phases.

Every phase must produce:

`docs/codex/gesc_gaussian/handoffs/phase_XX_handoff.md`

## Phase 00 verification and acceptance

- Re-run repository discovery rather than relying only on this plan.
- Confirm all workspace/package/interface entries.
- Trace publishers, subscribers, parameters, launch conditions, and message
  layouts to source.
- Record both declared and effective dependencies.
- Run non-hardware XML, shell-syntax, build, and test-discovery commands.
- Preserve pre-existing failures and user changes.
- Ensure the five audit documents agree on names and paths.
- End with the Phase 00 handoff, exact Git status, commands/results, unresolved
  issues, and recommended commit message.

## Stop conditions and risks

Stop and report with exact evidence if:

- repository structure or active wiring contradicts this plan;
- exact interfaces cannot be established from source;
- required inspection would command physical hardware;
- an external physical repository is required to make a Phase 00 claim;
- the audit would overwrite unrelated user work;
- a proposed later-phase owner duplicates a responsibility already present.

The principal Phase 00 risks are hidden effective dependencies, stale default
configuration paths, simulation-specific `/odom` assumptions, incomplete
diagnostics, large legacy lint debt, and accidentally treating relative
simulator light scaling as absolute calibration.
