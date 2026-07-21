# Phase 04 Plan — Measured Escape, Assisted Escape, and Bounded Recentering

Artifact target: `docs/codex/gesc_gaussian/plans/phase_04_plan.md`

## Amendment 1 — launch typing and signal-safe shutdown (2026-07-21)

This user-authorized amendment resolves the two contradictions documented by
the first visible Gazebo smoke after partial implementation commits `b0e024d`
and `212c284`. It supersedes only the file-ownership and shutdown-reuse claims
identified below; the Phase 04 algorithm, interfaces, numerical semantics,
legacy defaults, and physical/simulation boundary remain unchanged.

The resumed implementation is explicitly authorized to:

1. change the `gazebo.launch.xml` defaults for
   `gaussian_fill_center_cost_percentile` and
   `gaussian_fill_shoulder_cost_percentile` from `10`/`80` to
   `10.0`/`80.0`, preserving their values while making ROS infer the declared
   `DOUBLE` parameter type;
2. edit both `supervisor_node_script.py` and
   `controller_node_script.py` process-level `main()` shutdown sequencing so
   SIGINT is handled without invalidating the rclpy context before each node
   publishes its final zero command;
3. use disabled automatic rclpy signal handlers plus a bounded
   `SingleThreadedExecutor.spin_once()` loop, or an equivalently tested
   mechanism, provided zero is published while `rclpy.ok()` is still true,
   node/executor cleanup is deterministic, and `rclpy.try_shutdown()` occurs
   only after the zero-command path;
4. add focused regression coverage for the launch parameter types and the
   controller/supervisor SIGINT cleanup order, then rerun the visible Gazebo
   finite-command/topic/clean-shutdown smoke.

This amendment does not authorize a new command owner, topic, watchdog,
controller law, saturation path, cost sign, unit conversion, hardware action,
or broader refactor. If the repaired smoke exposes another repository/plan
contradiction, the original stop-and-document rule still applies.

## Objective and scope

Implement measurable escape progress, one stall-triggered fill redesign, deterministic boundary-aware affine assistance, and bounded center return for `robust_gaussian_v1`.

Phase 04 will:

- freeze the initial escape center and exit radius for the entire escape attempt;
- measure radial distance and rolling radial progress;
- detect a stall only after a complete observation window;
- request exactly one targeted redesign of the active fill before assisted escape;
- select and publish a safe affine direction using room bounds, retained fills, and recent approach history;
- command a bounded differential-drive return to room center;
- retain all fills as recenter avoidance constraints;
- reuse the existing controller arbitration, saturation, watchdog, and
  zero-command paths while repairing process-level signal/shutdown sequencing;
- make the existing robust Gaussian percentile launch arguments type-correct;
- add synthetic/ROS tests and one visible Gazebo startup smoke test.

It will not add Heavy-Ball behavior, physical adapters, hardware commands, Nav2, a general path planner, collision sensing, rosbag recording, or Phase 06 scenario automation.

The required planning validator passed:

```text
Phase 04 plan context is complete.
```

Current repository baseline:

- Branch: `feature/gesc-gaussian-robustness-v1`
- HEAD: `8789693a82a6771eefb99b77ef3af95e3a0f0bca`
- Focused Phase 03 baseline: `65 passed in 2.28s`
- The existing user modification to
  `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`
  remains out of scope.

## Repository findings and reuse decisions

Already implemented and retained:

- `SupervisorStateMachine` already owns the eight states, abstract
  `stable_exit`, `stalled`, and `recenter_complete` inputs, one redesign path,
  one shared escape deadline, recenter timeout, and state weights.
- The supervisor already correlates fill requests/results, tracks the active
  fill ID, owns `/gesc_gaussian/algorithm_state`, and publishes
  `/gesc_gaussian/supervisor_command`.
- Robust `GaussianFill` records already provide immutable centers,
  `support_radius`, `exit_radius`, fill/cluster/revision identities, and
  supersession state.
- The Phase 03 registry already combines samples and commits replacement
  revisions without stacking fills.
- `modified_cost_2d` already evaluates anisotropic fills, has an affine-cost
  implementation, and applies the supervisor’s raw/Gaussian/affine weights.
- `custom_controller` already:

  - uses GESC plus supervisor contribution in search/escape;
  - uses supervisor-only commands in `RECENTER`;
  - combines before one final `Directional_Controller.saturate_command()`;
  - publishes pre/post-saturation diagnostics;
  - publishes zero for stale, invalid, disallowed, exception, and shutdown
    paths.

Planner decision:

- No Nav2 integration, planner, costmap, navigation action, boundary owner,
  recenter controller, or collision/contact topic exists.
- The Gazebo world contains only the ground plane and sun; configured bounds
  will be a virtual operating envelope, not inferred physical walls.
- Therefore, implement the required bounded center-return controller as a pure
  internal component of the existing `ros_esc` supervisor. Do not create
  another ROS node or package.

The approved simulation default is the implementation package’s scenario
template:

```text
bounds: [-2.0, 2.0] x [-2.0, 2.0] m
room center: (0.0, 0.0) m
wall margin: 0.35 m
```

`recenter_after_escape=True` selects bounded mode. Setting it to `False`
selects unbounded mode and bypasses bounds/recentering.

## Implementation design

### Frozen escape geometry and progress

On the first matching fill result that enters `ESCAPE_REPULSE`, validate and
freeze:

```text
initial fill ID
center_x
center_y
exit_radius
escape start time
recent approach vector
```

The frozen center and radius remain unchanged through the stall redesign and
`ESCAPE_ASSIST`, even when a replacement fill revision becomes authoritative.
The state machine may update `active_escape_fill_id` to that revision, but the
published escape geometry remains the initial reference until transition to
`SEARCH`, `GOAL_HOLD`, or `FAILSAFE`.

For each newer valid pose sample:

```text
d(t) = norm(position(t) - frozen_center)
delta_d = d(t) - d(t - stall_window_sec)
```

Interpolate distance linearly at the exact rolling-window boundary. Radial
progress remains invalid until a complete window exists.

Stable exit requires all of:

- `d(t) > frozen_exit_radius`;
- valid `delta_d >= 0`;
- the conditions remain uninterrupted for `escape_exit_hold_sec`.

While a valid exit hold is in progress, suppress stall detection so a robot
already beyond the radius can complete the hold with zero radial change.

Declare stall when:

- a complete progress window exists;
- no qualifying exit hold is active;
- `delta_d < minimum_radial_progress_m`.

The exact threshold is non-stalled. Publish one
`EVENT_ESCAPE_STALLED` per escape attempt with the frozen geometry, current
distance, progress, window, and threshold.

### Single targeted fill redesign

Reuse the existing state-machine transition:

```text
ESCAPE_REPULSE
  -> DESIGN_OR_MERGE_FILL
  -> ESCAPE_ASSIST
```

The current eight-value fill-request timestamp/data contract remains
unchanged. Add robust-only request-header semantics:

```text
ROBUST_FILL_CREATE
ROBUST_FILL_REDESIGN:<active_fill_id>
```

Unknown/older headers remain accepted as ordinary create requests.

For a redesign request:

- resolve the target fill to its current active cluster;
- require the new estimate to pass the existing hard-overlap gate with that
  cluster;
- combine retained cluster samples with the new window;
- run the existing Phase 03 estimator, validation, and bounded design
  escalation;
- commit a revision of that cluster only;
- reject safely if the target is absent, superseded without a replacement, or
  fails overlap/design validation;
- never create a second cluster as the response to a stall redesign.

The state machine’s existing `redesign_attempted` flag continues to enforce
one request and one total escape deadline.

### Safe direction selection

Maintain a continuous pose history and freeze the recent approach direction
over `approach_history_window_sec` when escape begins.

Preferred direction:

1. Bounded mode: current pose toward configured room center.
2. Unbounded mode: opposite the frozen recent approach vector.
3. If the preferred vector is degenerate, use radial direction away from the
   frozen escape center.
4. If all are degenerate, enter `FAILSAFE`.

Generate candidates in deterministic order:

```text
0, +step, -step, +2*step, -2*step, +3*step, -3*step, pi
```

For each unit candidate `u`, evaluate the look-ahead endpoint
`p_next = p + direction_lookahead_m * u`.

Reject a candidate when:

- its dot product with the preferred direction is negative;
- bounded mode places `p_next` outside the wall-margin-inset rectangle;
- it moves closer to a fill whose avoidance circle currently contains the
  robot;
- its projected segment enters another fill’s avoidance circle.

Each fill’s conservative avoidance radius is:

```text
support_radius + fill_avoidance_margin_m
```

For accepted candidates, score the minimum predicted endpoint clearance to
walls and active-fill avoidance circles, clipped to the look-ahead distance.
Select lexicographically by:

1. maximum predicted clearance;
2. maximum alignment with the preferred direction;
3. smallest absolute rotation;
4. the fixed positive-before-negative candidate order.

Hold a selected assisted direction while it remains safe. Reselect only when
it becomes unsafe. Increment a direction revision whenever selection changes.
If no candidate is safe, enter `FAILSAFE`.

### Affine assistance

Extend the existing `AlgorithmState` stream with the selected direction and
revision. Do not create a new command or direction topic.

In `robust_gaussian_v1`:

- stop constructing affine terms from PDE/odometry history when a fill arrives;
- create the active cluster’s affine term only in `ESCAPE_ASSIST`, using the
  supervisor-selected world-frame unit direction;
- use the existing `affine_gain`, `affine_direction_sign`, decay, and
  `affine_weight=1`;
- apply a direction only once per direction revision, preventing the 20 Hz
  state stream from resetting affine decay;
- clear robust affine terms outside `ESCAPE_ASSIST`;
- call the affine synchronization logic from both fill and state callbacks so
  DDS callback order cannot lose the direction.

Legacy fill-triggered affine construction and its history-direction parameters
remain numerically unchanged.

### Bounds and recentering

In bounded mode, validate at startup that:

- min bounds are strictly below max bounds;
- the wall-margin-inset rectangle is nonempty;
- the configured center lies inside that inset rectangle.

A valid pose outside the inset operating rectangle causes a controlled
`FAILSAFE`; Phase 04 will not invent obstacle recovery outside the approved
envelope.

After stable escape, `RECENTER` uses the same candidate selector with the room
center as its preferred direction and every active fill as an avoidance
constraint.

For selected world direction `u`:

```text
desired_heading = atan2(u_y, u_x)
heading_error = wrap(desired_heading - yaw)
angular = clamp(recenter_angular_gain * heading_error,
                +/- recenter_max_angular_velocity_rps)
```

When `abs(heading_error) >= recenter_rotate_in_place_angle_rad`, command zero
linear velocity. Otherwise:

```text
linear = min(recenter_max_linear_velocity_mps,
             recenter_linear_gain * distance_to_center)
         * max(0, cos(heading_error))
```

The supervisor publishes `[linear, 0, 0, 0, 0, angular]` as a `Twist`.
`custom_controller` suppresses GESC in `RECENTER` and applies its existing
final saturation once.

Inside `recenter_tolerance_m`, publish zero and start the completion hold.
Transition to `SEARCH` only after an uninterrupted `recenter_hold_sec`.
Leaving the tolerance resets the hold. Publish
`EVENT_RECENTER_COMPLETE` on success.

Retained fills remain observable through the Gaussian-weighted cost and are
actively used by the center-return direction selector.

## Public interface changes

### Extend `ros_esc_interfaces/msg/AlgorithmState`

Add:

```text
float64 escape_center_x
float64 escape_center_y
float64 escape_exit_radius
bool escape_geometry_valid

float64 radial_distance
bool radial_distance_valid
float64 radial_progress
bool radial_progress_valid
float64 escape_exit_hold_elapsed_sec
bool escape_exit_hold_elapsed_valid
bool escape_stalled
bool escape_stalled_valid

float64 safe_direction_x
float64 safe_direction_y
float64 safe_direction_clearance_m
bool safe_direction_valid
uint32 safe_direction_revision
bool safe_direction_revision_valid

float64 recenter_target_x
float64 recenter_target_y
bool recenter_target_valid
float64 recenter_distance
bool recenter_distance_valid
```

Unavailable floating-point values are `NaN`, revisions are zero, and validity
flags are false. Legacy state publishers populate these fields as unavailable.

Changing the message definition changes its ROS type hash. All three workspace
packages must be rebuilt together; existing source consumers can ignore the
additive fields, but stale installed binaries are not wire-compatible.

### Reused topics

No topic is added or renamed:

- `/gesc_gaussian/algorithm_state` carries progress and safe direction.
- `/gesc_gaussian/algorithm_events` carries stall/configuration/recenter events.
- `/gesc_gaussian/gaussian_fills` supplies active fill geometry.
- `/gesc_gaussian/fill_requests` retains its timestamp and eight numeric fields.
- `/gesc_gaussian/supervisor_command` becomes nonzero only in `RECENTER`.
- `/gesc_gaussian/control_diagnostics`, controller chatter, and `/cmd_vel`
  retain final command observability.

Reuse existing event constants:

- `EVENT_CONFIGURATION`
- `EVENT_ESCAPE_STARTED`
- `EVENT_ESCAPE_STALLED`
- `EVENT_RECENTER_STARTED`
- `EVENT_RECENTER_COMPLETE`
- `EVENT_TIMEOUT`
- `EVENT_FAILSAFE`
- `EVENT_STATE_TRANSITION`

No new node, package, message file, topic, service, action, or dependency is
justified.

## Parameters and defaults

Add matching `gazebo.launch.xml` arguments and supervisor ROS parameters:

| Parameter | Default |
|---|---:|
| `escape_exit_hold_sec` | `1.0` |
| `stall_window_sec` | `3.0` |
| `minimum_radial_progress_m` | `0.05` |
| `approach_history_window_sec` | `3.0` |
| `room_bounds_x_min_m` | `-2.0` |
| `room_bounds_x_max_m` | `2.0` |
| `room_bounds_y_min_m` | `-2.0` |
| `room_bounds_y_max_m` | `2.0` |
| `room_center_x_m` | `0.0` |
| `room_center_y_m` | `0.0` |
| `wall_margin_m` | `0.35` |
| `direction_lookahead_m` | `0.50` |
| `direction_candidate_step_rad` | `0.7853981633974483` |
| `fill_avoidance_margin_m` | `0.10` |
| `recenter_tolerance_m` | `0.25` |
| `recenter_hold_sec` | `1.0` |
| `recenter_linear_gain` | `0.50` |
| `recenter_angular_gain` | `1.50` |
| `recenter_max_linear_velocity_mps` | `0.10` |
| `recenter_max_angular_velocity_rps` | `0.40` |
| `recenter_rotate_in_place_angle_rad` | `1.0471975511965976` |

Retain existing defaults:

```text
escape_max_sec=20.0
recenter_after_escape=True
recenter_max_sec=30.0
stale_pose_sec=0.50
stale_sensor_sec=0.50
```

Publish one supervisor `EVENT_CONFIGURATION` containing the effective bounds,
center, margins, progress thresholds, candidate settings, controller gains,
and command caps.

## Exact file changes

### Modify

- `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmState.msg`
  - Add the progress, frozen geometry, safe-direction, and recenter fields.

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py`
  - Store complete pose/yaw and fill records.
  - Integrate escape tracking, bounds validation, candidate selection,
    recenter completion, state diagnostics, structured events, and nonzero
    recenter commands.
  - Preserve state-machine transition and timeout ownership.

- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_registry.py`
  - Add deterministic lookup from active `fill_id` to cluster for targeted
    stall redesigns.

- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`
  - Retain the eight-value request data.
  - Parse the robust request header and force stall redesigns to the targeted
    active cluster.
  - Cache the complete algorithm state rather than only its state enum.

- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`
  - Keep legacy affine creation unchanged.
  - Bind robust affine direction to the supervisor’s safe-direction revision.
  - Remove the old approach-derived robust affine term creation.

- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py`
  - Populate the new legacy placeholder fields with `NaN`/false validity.

- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`
  - Preserve command arbitration, final saturation, watchdog, topics, and
    legacy behavior exactly.
  - Change only process-level signal/spin/cleanup sequencing so its existing
    shutdown-zero publication runs while the rclpy context is valid.

- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
  - Expose and pass every Phase 04 parameter through the existing robust
    supervisor declaration.
  - Spell the existing robust center/shoulder percentile defaults as
    floating-point literals (`10.0` and `80.0`) so they match the Gaussian
    node's declared double parameters.
  - Keep `algorithm_profile=legacy` as the launch default.

- `ros2_ws/src/ros_esc/test/test_state_machine.py`
  - Retain the abstract transition tests and add exact exit/stall priority and
    one-redesign assertions.

- `ros2_ws/src/ros_esc/test/test_supervisor_integration.py`
  - Exercise progress, stall/redesign, assist direction, recenter command,
    completion, and structured events using simulated ROS messages.

- `ros2_ws/src/ros_esc/test/test_robust_gaussian_algorithm.py`
  - Test active-fill lookup and targeted same-cluster revision behavior.

- `ros2_ws/src/ros_esc/test/test_observability_contract.py`
  - Test new state fields, validity semantics, request headers, events, launch
    defaults and runtime-compatible parameter types, and configuration
    publication.

- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`
  - Prove legacy affine behavior remains unchanged.
  - Test robust safe-affine binding and existing recenter-only arbitration and
    final saturation.
  - Test controller and supervisor process cleanup ordering with a valid ROS
    context, final zero publication before shutdown, and deterministic
    executor/node cleanup.

- `docs/codex/gesc_gaussian/topic_dictionary.md`
  - Document new fields, parameters, formulas, header semantics, owners,
    validity, bounds, and virtual-safety limitation.

- `docs/codex/gesc_gaussian/test_commands.md`
  - Record exact Phase 04 commands and results.

### Create

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/escape_recenter.py`
  - Pure dataclasses and deterministic helpers for bounds, frozen geometry,
    rolling progress, exit/stall dwell, approach history, candidate scoring,
    fill avoidance, angle wrapping, and center-return commands.
  - This is an internal helper, not a ROS node.

- `ros2_ws/src/ros_esc/test/test_escape_recenter.py`
  - ROS-independent numerical coverage of the Phase 04 geometry and controller.

- `docs/codex/gesc_gaussian/handoffs/phase_04_handoff.md`
  - Final repository state, implementation details, commands/results,
    limitations, and Phase 05 boundary.

`state_machine.py`, `setup.py`, package manifests, controller/filter JSON,
PDE-history nodes, data collection, the user-owned wrapper, physical files,
and Heavy-Ball files require no implementation edit. Their existing behavior
is reused and regression-tested. Amendment 1 expressly removes
`controller_node_script.py` from this no-edit list, but limits its edit to the
process lifecycle described above.

## Implementation sequence

1. Save this plan at the artifact target and require
   `validate_phase_context.sh 04 implement` to pass.
2. Reconfirm HEAD, working-tree ownership, exact source owners, and the
   65-test focused baseline.
3. Extend `AlgorithmState`; add the pure `escape_recenter.py` core and its
   deterministic tests.
4. Integrate frozen geometry, radial progress, stall/exit dwell, direction
   selection, bounds, recenter commands, and state/event publication into the
   existing supervisor.
5. Add targeted same-cluster redesign handling to the existing fill owner and
   registry.
6. Replace only the robust affine-direction source with the supervisor’s safe
   direction; preserve the legacy affine path.
7. Wire all parameters through the existing Gazebo launch, including the two
   Amendment 1 float-typed percentile literals.
8. Repair controller and supervisor process-level signal/shutdown sequencing
   without changing either node's runtime command semantics.
9. Extend ROS integration, observability, controller, Gaussian, and legacy
   tests.
10. Run focused tests, package build/tests, interface and launch checks, and a
   visible Gazebo startup smoke.
11. Update the topic dictionary/test record and write the Phase 04 handoff.

Because the phase touches more than ten source/test files, split implementation
into coherent commits:

```text
phase 04a: add escape and recenter geometry core
phase 04b: wire assisted escape and center return
phase 04c: fix launch typing and signal-safe shutdown
phase 04d: document and validate bounded escape behavior
```

The Amendment 1 repair is a separate coherent unit discovered only by the
mandatory live smoke; it does not reopen the first two implementation units.

## Tests and acceptance criteria

### Pure synthetic tests

`test_escape_recenter.py` must cover:

- exact radial distance and interpolated rolling progress;
- progress invalidity before a full window;
- equality with the stall threshold being non-stalled;
- stationary/inward stall detection;
- exit-radius strictness, nonnegative progress, hold completion, and reset;
- frozen center/radius surviving a replacement fill revision;
- bounded/unbounded preferred directions;
- opposite-approach fallback;
- wall rejection and deterministic rotated selection;
- active-fill avoidance when outside and outward-only recovery when inside;
- deterministic tie-breaking and no-safe-candidate failure;
- angle wrapping, rotate-in-place behavior, linear/angular caps;
- recenter tolerance and hold reset;
- invalid bounds, center, margins, poses, and nonfinite inputs.

### State, ROS, cost, and command tests

Cover:

- pure repulsion reaching stable exit without redesign;
- one stall event and exactly one targeted redesign request;
- accepted redesign entering `ESCAPE_ASSIST` without resetting the deadline or
  frozen geometry;
- rejected redesign and second-stall paths entering `FAILSAFE`;
- safe direction publication and revision stability;
- the robust affine descent direction matching the selected world direction;
- recenter using supervisor-only command while retained fills remain avoidance
  constraints;
- controller combination followed by one final saturation;
- diagnostics, controller chatter, and `/cmd_vel` matching exactly;
- stale pose/source, bounds violation, no candidate, timeout, exception, stop,
  and shutdown producing zero;
- SIGINT leaving the rclpy context valid through controller and supervisor
  zero publication, followed by clean node/executor/context teardown;
- robust center/shoulder percentile launch defaults resolving as double rather
  than integer parameters;
- recenter completion returning to `SEARCH`;
- all new legacy placeholder fields invalid/`NaN`;
- unchanged legacy cost, fill, affine, controller, topics, timestamps, and
  launch defaults.

### Commands

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 04 implement
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
  src/ros_esc/test/test_escape_recenter.py \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
```

```bash
ros2 interface show ros_esc_interfaces/msg/AlgorithmState
ros2 interface show ros_esc_interfaces/msg/AlgorithmEvent

ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
  algorithm_profile:=robust_gaussian_v1 \
  use_pde_extensions:=True \
  --show-args
```

Run one visible Gazebo startup smoke through the existing launch graph, with
no physical hardware:

```bash
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
  algorithm_profile:=robust_gaussian_v1 \
  use_pde_extensions:=True \
  controller_config_filepath:=/home/mattb/dsim-lab/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage.json \
  cost_function_config_filepath:=/home/mattb/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json \
  recenter_after_escape:=True \
  room_bounds_x_min_m:=-2.0 \
  room_bounds_x_max_m:=2.0 \
  room_bounds_y_min_m:=-2.0 \
  room_bounds_y_max_m:=2.0 \
  room_center_x_m:=0.0 \
  room_center_y_m:=0.0 \
  show_cost_surface_plot:=False
```

The historical `heavy_ball_PDE_ESC` directory contains the audited
controller-independent multi-light cost model; this command does not enable or
modify Heavy-Ball control.

The smoke gate is limited to launch health, finite bounded commands, canonical
topic availability, and clean shutdown zero. Capture enough topic/process
evidence to show that the supervisor and final `/cmd_vel` owner each publish a
zero while their ROS contexts are valid and exit without an `RCLError`. Phase
04 does not claim a full Gazebo scenario matrix; that remains Phase 06/08 work.

```bash
colcon test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose
```

Report focused results separately from the documented 875 pre-existing lint
failures.

```bash
cd ..
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_required_docs.sh
git diff --check
git status --short --branch
```

Acceptance requires:

- all focused tests pass;
- no new package-test failure beyond the existing lint baseline;
- frozen escape geometry never changes during one attempt;
- exactly one stall redesign is possible;
- no unsafe direction or command is published;
- recenter commands are supervisor-only and finally saturated by the existing
  controller;
- both controller and supervisor publish their shutdown zero before context
  invalidation and exit cleanly under controlled SIGINT;
- the robust Gaussian percentile launch values reach the node as doubles;
- legacy behavior remains unchanged;
- no physical or Heavy-Ball action occurs.

## Backward compatibility and migration

- `algorithm_profile=legacy` remains the default.
- Legacy convergence, Gaussian fitting, `/cost_bias`, affine-history policy,
  cost composition, controller behavior, topics, arrays, timestamps, and
  limits remain unchanged.
- Robust mode intentionally changes from eventual escape timeout to measured
  escape/recenter behavior.
- `recenter_after_escape=False` preserves the unbounded robust path and resumes
  `SEARCH` after stable exit.
- Existing typed topic names remain unchanged.
- Robust fill request numeric layout and correlation timestamp remain
  unchanged; only the header gains documented intent.
- Consumers must rebuild after the additive `AlgorithmState` schema change.
- No physical safety claim is made from configured virtual bounds.

## Stop conditions, risks, and implementation assumptions

Stop and report exact evidence if:

- the Phase 04 implementation validator or saved plan is absent/fails;
- required Phase 00–03 handoffs or current owners no longer match the checkout;
- unrelated user changes overlap a planned file;
- robust fills do not provide finite valid support/exit radii;
- a stall redesign cannot be tied to the active cluster without duplicating a
  fill;
- odometry and fill frames are not both `odom`;
- the default affine sign fails the minimization-direction unit test;
- nonzero recenter commands bypass the existing final saturation/watchdog;
- legacy numerical tests change;
- bounds or center cannot be validated;
- the bounded signal-safe loop cannot preserve the existing timer/callback
  behavior or causes controller command semantics to change;
- clean controlled shutdown cannot be demonstrated after the authorized
  controller/supervisor lifecycle repair;
- implementation requires a physical, Heavy-Ball, Nav2, or collision-interface
  change.

Principal risks:

- Bounds are a virtual envelope because the current Gazebo world has no walls
  or contact owner.
- The center-return controller is deliberately bounded and local, not a
  globally complete planner; retained-fill layouts can still leave no safe
  candidate.
- Circular `support_radius` avoidance is conservative for anisotropic fills.
- Phase 08 may tune candidate look-ahead, fill margin, and recenter gains.
- A targeted redesign can fail honestly when new samples no longer overlap the
  active basin; that must produce zero-command `FAILSAFE`, not a new cluster.
- DDS callback order is addressed by idempotent state/fill affine
  synchronization, but integration tests must exercise both orders.

Implementation assumptions to verify:

- `recenter_after_escape=True` is the bounded-mode selector established by
  Phase 02.
- `Directional_Controller` remains the robust controller and retains
  `0.1 m/s` linear and `0.5 rad/s` angular final limits.
- The Phase 04 angular command default of `0.40 rad/s` remains below that final
  controller limit.
- Supervisor and odometry timestamps follow Gazebo ROS time; freshness remains
  based on local ROS receipt time.
- The 20 Hz supervisor rate is sufficient for the 0.50 m look-ahead and current
  command limits.
- The selected template bounds and center are simulation defaults, not claims
  about the later physical room.
