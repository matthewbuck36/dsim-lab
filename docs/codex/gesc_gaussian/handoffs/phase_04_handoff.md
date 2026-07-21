# Phase 04 Handoff

## Objective status: complete

Phase 04 implements measured pure escape, one stall-triggered fill redesign,
safe assisted escape, and bounded indoor recentering for
`robust_gaussian_v1`. The complete focused suite, three-package build,
interface/launch checks, and required visible Gazebo startup/SIGINT smoke pass.
No physical hardware was run.

The first live smoke found two facts that contradicted the original saved
plan: integer-looking launch substitutions were rejected by double Gaussian
parameters, and automatic rclpy signal handling invalidated the context before
the controller and supervisor shutdown-zero publishes. Work stopped as
required. The user then authorized Amendment 1 in
`docs/codex/gesc_gaussian/plans/phase_04_plan.md`; bounded repairs were made and
the full gate was rerun successfully.

## Repository state

- Repository: `/home/mattb/dsim-lab`
- Branch: `feature/gesc-gaussian-robustness-v1`
- Phase starting commit: `8789693a82a6771eefb99b77ef3af95e3a0f0bca`
- Phase implementation commits:
  - `b0e024d` — `phase 04a: add escape and recenter geometry core`
  - `212c284` — `phase 04b: wire assisted escape and center return`
  - `63744b0` — `phase 04c: fix launch typing and signal-safe shutdown`
- The phase exceeded ten implementation/test files, so geometry/interfaces,
  ROS wiring, and the smoke-discovered lifecycle repair were kept as coherent
  commits.
- The pre-existing user modification to
  `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`
  was preserved and never staged.

## Files changed

### Geometry and interface core

- `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmState.msg`
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/escape_recenter.py`
- `ros2_ws/src/ros_esc/test/test_escape_recenter.py`

### ROS integration and tests

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_registry.py`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`
- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`
- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
- `ros2_ws/src/ros_esc/test/test_state_machine.py`
- `ros2_ws/src/ros_esc/test/test_supervisor_integration.py`
- `ros2_ws/src/ros_esc/test/test_robust_gaussian_algorithm.py`
- `ros2_ws/src/ros_esc/test/test_observability_contract.py`
- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`

### Documentation

- `docs/codex/gesc_gaussian/plans/phase_04_plan.md`
- `docs/codex/gesc_gaussian/topic_dictionary.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/handoffs/phase_04_handoff.md`

## Behavior implemented

- The first accepted fill enters `ESCAPE_REPULSE` with weights `(0, 1, 0)`,
  so escape begins with pure Gaussian repulsion.
- Initial fill ID, center, exit radius, escape start time, and recent approach
  are frozen for one escape attempt and survive replacement fill revisions.
- Radial distance and exact rolling-window radial progress are published with
  explicit validity. Stall is evaluated only after a complete window and does
  not override a stable exit.
- The first stall emits one structured event and exactly one targeted
  same-cluster redesign request. Accepted redesign enters `ESCAPE_ASSIST`
  without resetting frozen geometry or the shared escape deadline; rejection
  or a subsequent stall fails safely.
- Assisted direction candidates are deterministic and checked against virtual
  room bounds, wall margin, every active fill support radius plus margin, and
  approach history. No safe candidate enters `FAILSAFE` with zero command.
- Robust modified cost binds its affine descent term to the supervisor's
  selected world direction and revision. Legacy approach/history affine
  behavior is unchanged.
- Bounded mode uses a capped differential-drive center-return command. It
  rotates in place for large heading error, keeps all fills active as avoidance
  constraints, publishes zero inside the center tolerance, and returns to
  `SEARCH` after the uninterrupted completion hold.
- The final controller continues to publish GESC unsaturated, supervisor
  contribution, combined pre-saturation, and final post-saturation commands,
  with one existing final saturation step.
- Stale pose/source data, nonfinite or invalid data, bounds violation, no safe
  direction, timeout, explicit stop, exception, and shutdown all produce zero.

## Public contract and compatibility

`AlgorithmState` adds frozen escape geometry, radial distance/progress,
exit-hold/stall status, safe direction/clearance/revision, and recenter
target/distance fields with explicit validity. No public topic was added or
renamed. Legacy state owners populate unavailable floats with `NaN`, revisions
with zero, and validity flags with false.

The numeric layout and correlation timestamp of
`/gesc_gaussian/fill_requests` remain unchanged. Robust headers add:

```text
ROBUST_FILL_CREATE
ROBUST_FILL_REDESIGN:<active_fill_id>
```

`algorithm_profile=legacy` remains the default. Legacy cost sign and units,
raw/modified topics, `/cost_bias` layout, affine policy, controller arrays,
timestamps, queue depths, saturation limits, and Heavy-Ball behavior are
unchanged. `recenter_after_escape=False` retains the unbounded robust path and
returns directly to `SEARCH` after stable exit.

Configured room bounds are a virtual simulation operating envelope, not
inferred walls, collision sensing, or a physical safety claim.

## Amendment 1 repairs

- `gaussian_fill_center_cost_percentile` and
  `gaussian_fill_shoulder_cost_percentile` retain values 10 and 80 but use XML
  defaults `10.0` and `80.0`, so rclpy receives declared double parameters.
- Controller and supervisor initialize with `SignalHandlerOptions.NO` and use
  a bounded `SingleThreadedExecutor.spin_once(timeout_sec=0.05)` loop.
- On SIGINT, each node is removed from its executor, its existing
  `destroy_node()` zero path runs while `rclpy.ok()` is still true, then the
  executor and ROS context are shut down.
- Command ownership, callback behavior, controller law, saturation, topics,
  and numerical semantics were not changed.

## Tests run

```text
validate_phase_context.sh 04 implement
PASS: Phase 04 implement context is complete.
```

```text
colcon build --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
PASS: 3 packages finished.
```

```text
Focused Phase 04 numerical/ROS/legacy suite
PASS: 93 passed in 3.12s.
```

The focused suite covers pure escape, rolling progress, stalled escape, one
redesign, assisted escape, wall/fill rejection, affine direction binding,
recenter commands/completion, controller arbitration/saturation, invalid and
stale inputs, timeout/failsafe, launch parameter types, and controller plus
supervisor signal-safe cleanup order.

```text
AlgorithmState/AlgorithmEvent interface show and legacy/robust --show-args
PASS: interfaces resolve; both launch profiles parse; percentile defaults are
10.0 and 80.0.
```

```text
Visible robust Gazebo startup and controlled SIGINT smoke
PASS: the complete graph started; gaussian_fill stayed alive; canonical state,
control-diagnostics, and /cmd_vel topics published finite values; every ROS
process exited cleanly; no RCLError or invalid-context publish occurred.
```

The launch log is
`/home/mattb/.ros/log/2026-07-21-15-19-00-809176-ubuntu-ssd-61214/launch.log`.
Gazebo Classic itself reports exit code 255 when interrupted by the launch
SIGINT; all ROS processes report clean exits, and this is not a Phase 04 node
failure.

```text
colcon test / colcon test-result --all --verbose
EXPECTED BASELINE FAILURES: 978 tests, 0 errors, 875 failures, 1 skipped.
```

The failure count is unchanged from Phases 00-03. The 875 failures remain the
repository's existing flake8, pep257, and lint-cmake debt. Phase 04 adds 28
passing focused tests over the 65-test Phase 03 focused baseline.

Build and test artifacts for the Amendment 1 rerun are under:

```text
/tmp/dsim_phase04_amend_build
/tmp/dsim_phase04_amend_install
/tmp/dsim_phase04_amend_log
/tmp/dsim_phase04_amend_test_log
```

No physical hardware was run.

## Known limitations and unresolved issues

- No Phase 04 functional blocker remains.
- Repository-standard lint remains red at the unchanged 875-failure baseline.
- Bounds are virtual; the current world does not provide wall/contact sensing.
- The local candidate controller is bounded, not a complete path planner;
  retained-fill layouts can legitimately produce no safe direction.
- Circular support-radius avoidance is conservative for anisotropic fills.
- Full scenario characterization and tuning remain Phase 06/08 work.

## Recommended commit message

```text
phase 04: add escape progress and indoor recentering
```
