# Phase 02 Handoff

## Objective completed

Implemented the opt-in `robust_gaussian_v1` hybrid supervisor while retaining
`legacy` as the default profile. The eight specified states, state-owned cost
weights, source-score verification/dwell, correlated fill requests, timeouts,
controller watchdog, and latched zero-command failsafe are now explicit and
testable.

The saved Phase 02 Plan was verified against the live checkout before editing.
`validate_phase_context.sh 02 implement` passed, HEAD was exactly the Phase 01
commit `2ba43f3`, every planned existing owner was present, and the only
tracked pre-existing change remained the user-owned GESC wrapper. No plan
contradiction or required-file overlap was found.

## Repository state

- Repository: `/home/mattb/dsim-lab`
- Branch: `feature/gesc-gaussian-robustness-v1`
- Starting commit: `2ba43f3f2e3a4e8a30ed5d3559e559feb65b7470`
- Phase 02 implementation commits:
  - `000f001` — state-machine core and transition tests;
  - `3ebdf70` — robust source/cost/fill profile switching;
  - `571a193` — ROS supervisor, command safety, launch, and integration tests.
- Pre-existing user change preserved and not staged:
  `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`
- Pre-existing untracked implementation package, audit/plan documents, and
  other Phase 00 durable files were preserved.
- Build/test output remained in ignored workspace trees. Colcon logs were
  directed to `/tmp/dsim_phase02_build_log` and
  `/tmp/dsim_phase02_test_log`.

The approved implementation spans more than ten files because state, source,
cost, fill, and final-command responsibilities remain with their audited
owners. It was split into the three coherent implementation commits listed
above instead of introducing a duplicate pipeline.

## Files changed

### State and interface core

- `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmEvent.msg`
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/__init__.py`
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py`
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py`
- `ros2_ws/src/ros_esc/setup.py`

### Existing owners extended

- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/cost_function_objects.py`
- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`
- `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`
- `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`

### Tests and documentation

- `ros2_ws/src/ros_esc/test/test_state_machine.py`
- `ros2_ws/src/ros_esc/test/test_supervisor_integration.py`
- `ros2_ws/src/ros_esc/test/test_observability_contract.py`
- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`
- `docs/codex/gesc_gaussian/topic_dictionary.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/handoffs/phase_02_handoff.md`

No Heavy-Ball file, physical adapter, data collector, cost/filter/controller
JSON, PDE history node, or user-owned wrapper was changed.

## Public interfaces added or changed

New topics:

- `/gesc_gaussian/source_cost` — synchronized raw simulation cost and
  model-normalized score (`CostBreakdown`);
- `/gesc_gaussian/convergence_status` — continuous eight-value convergence
  status (`StampedFloat64MultiArray`);
- `/gesc_gaussian/fill_requests` — single-flight request to the existing fill
  owner (`StampedFloat64MultiArray`);
- `/gesc_gaussian/supervisor_command` — supervisor contribution (`Twist`),
  always zero in Phase 02;
- `/gesc_gaussian/stop_requested` — external true-only stop latch (`Bool`).

`AlgorithmEvent` adds the non-conflicting constant
`EVENT_STATE_TRANSITION=3`. No existing constant or field changed.

In robust mode, the supervisor is the sole
`/gesc_gaussian/algorithm_state` owner. `modified_cost_2d` remains the final
cost-breakdown owner and `custom_controller` remains the sole publisher of
`/cmd_vel`, legacy controller chatter, and control diagnostics.

## Parameters added or changed

The central launch now exposes:

- profile/rates: `algorithm_profile=legacy`,
  `supervisor_publish_rate_hz=20.0`, `command_watchdog_rate_hz=20.0`;
- dwell/timeouts: `startup_timeout_sec=5.0`,
  `convergence_hold_sec=2.0`, `goal_score_threshold=0.95`,
  `goal_hold_sec=3.0`, `undesired_score_hold_sec=3.0`,
  `verification_max_sec=10.0`, `fill_design_timeout_sec=5.0`,
  `escape_max_sec=20.0`, `recenter_max_sec=30.0`;
- policy/freshness: `recenter_after_escape=True`,
  `stale_pose_sec=0.50`, `stale_sensor_sec=0.50`,
  `supervisor_state_stale_sec=0.50`,
  `supervisor_command_stale_sec=0.50`,
  `zero_command_on_shutdown=True`;
- the five new topic arguments listed above.

Robust observability is mandatory even if the legacy
`enable_observability` argument remains false. Unknown profile names are
rejected. A robust launch without PDE extensions or with a controller other
than `Directional_Controller` stays at zero and fails safely rather than
falling back to legacy behavior.

## Behavior implemented

- Pure ROS-independent state machine with `SEARCH`, `VERIFY_EXTREMUM`,
  `DESIGN_OR_MERGE_FILL`, `ESCAPE_REPULSE`, `ESCAPE_ASSIST`, `RECENTER`,
  `GOAL_HOLD`, and `FAILSAFE`.
- Continuous convergence dwell, symmetric high/low score dwell, verification
  timeout, fill-design timeout, total escape timeout across one redesign, and
  recenter timeout.
- State weights:
  - search/verify `(1,1,0)`;
  - design/repulse/recenter/goal `(0,1,0)`;
  - assist `(0,1,1)`;
  - failsafe `(0,0,0)`.
- Post-noise photoresistor score normalization from the existing `337260 ohm`
  dark and `100 ohm` near model limits. This is a dimensionless simulator
  model-range score, not lux or absolute physical calibration.
- Raw cost acquisition/publication continues while its state weight is zero.
- `modified_cost_2d` evaluates raw, Gaussian, and stateful affine components
  once, applies supervisor weights, and publishes the explicit decomposition.
- Current Gaussian fitting remains unchanged behind the timestamp-correlated
  fill request/result topic boundary. Late results are ignored and one redesign
  is allowed by the pure Phase 04 input stub.
- The directional controller exposes reusable saturation. Robust commands are
  combined before one final saturation; disallowed, stale, invalid, exception,
  and shutdown paths publish zero.
- `GOAL_HOLD` and `FAILSAFE` latch. No automatic restart is implemented.
- `RECENTER` selects the supervisor-command interface, but the Phase 02
  supervisor contribution is deliberately zero.

## Backward compatibility

- `algorithm_profile=legacy` is the default.
- Legacy raw, modified cost, convergence event/counter, fill fit and
  `/cost_bias`, filter, controller, saturation, `/cmd_vel`, timestamps, array
  layouts, queue depths, cost sign, units, and launch defaults are retained.
- Legacy direct `/convergence_event` fill triggering remains selected.
- The numerical legacy-equivalence tests pass after extracting reusable
  directional saturation.
- Heavy-Ball behavior remains outside the robust profile and untouched.

## Tests run

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 02 implement
PASS: Phase 02 implement context is complete.
```

```text
colcon build --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
PASS: 3 packages finished.
```

```text
python3 -m pytest -q test_state_machine.py test_supervisor_integration.py test_observability_contract.py test_legacy_behavior.py
PASS: 44 passed in 1.05s.
```

The non-Gazebo ROS integration test observes
`SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE`, exactly
one correlated fill request, then a stop-triggered latched `FAILSAFE` with zero
supervisor command and structured transition/failsafe events.

```text
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml algorithm_profile:=robust_gaussian_v1 use_pde_extensions:=True --show-args
PASS: both launch profiles parsed and exposed Phase 02 arguments.
```

```text
colcon test --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose
EXPECTED BASELINE FAILURES: 929 tests, 0 errors, 875 failures, 1 skipped.
```

The failing count is exactly the Phase 00/01 baseline. The total rose by 28
passing Phase 02 tests over Phase 01's 901-test total. Remaining failures are
the repository's existing flake8, pep257, and lint-cmake test cases.

No Gazebo motion run and no physical-hardware command was performed.

## Known limitations

- Phase 02 deliberately does not compute stable radial exit, stall, assisted
  direction, boundaries, or recenter completion from live geometry.
- A robust run that reaches escape therefore remains in escape and safely
  times out unless a later Phase 04 producer supplies the tested transition
  inputs.
- `RECENTER` is an interface/state stub and never commands motion in this
  phase.
- The existing fill remains isotropic and has no merge/revision/support/exit
  design; Phase 03 owns those changes.
- Simulation score calibration is relative to the current mathematical model,
  not physical light intensity or lux.
- ROS timestamps in legacy/PDE inputs retain the Phase 00 mixed time-basis
  limitation; freshness uses local ROS receipt time.

## Unresolved failures

- Repository-standard lint remains red at the unchanged 875-test baseline.
- Physical pose/sensor/command mappings remain blocked on the Phase 09
  inventory and simulation acceptance gates.
- No end-to-end Gazebo motion acceptance claim is made for Phase 02.

## Decisions made

- Added one supervisor inside `ros_esc`; no duplicate algorithm or command
  package was created.
- Kept final `/cmd_vel` ownership in `custom_controller` and made the
  supervisor an authorization/zero-contribution owner.
- Used existing model endpoints and post-noise raw cost for source score; no
  source position or invented physical calibration is used.
- Preserved the current Gaussian implementation behind a correlated topic
  interface so Phase 03 can replace internals without changing the supervisor.
- Kept stable-exit, stall, assisted-direction, and recenter motion as explicit
  later-phase inputs rather than simulating them with timers.

## Exact next phase

Start a new Plan-mode chat with:

`DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/03_gaussian_fill_PLAN.md`

Before planning, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 03 plan
```

Save the approved plan at:

`docs/codex/gesc_gaussian/plans/phase_03_plan.md`

## Recommended commit message

```text
phase 02: add robust Gaussian supervisor state machine
```
