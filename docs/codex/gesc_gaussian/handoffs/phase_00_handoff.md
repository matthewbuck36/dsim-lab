# Phase 00 Handoff

## Objective completed

Completed a read-only audit of the current `dsim-lab` ROS 2/Gazebo
GESC-plus-Gaussian implementation and created the five durable architecture
documents required before Phase 01.

The saved Phase 00 Plan was verified against the live checkout. No repository
change contradicted it, so implementation proceeded. No algorithm source,
launch behavior, parameter, topic, cost sign, unit, or physical/simulation
semantics changed.

## Repository state

- Repository: `/home/mattb/dsim-lab`
- Branch: `feature/gesc-gaussian-robustness-v1`
- Audited commit: `e0c693e6c9f954d3e7061c90089b7b2a2c6a1d4c`
- Working tree before Phase 00:

```text
 M ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash
?? DSIM_GESC_Gaussian_Codex_Implementation_Package/
?? docs/
```

- Working tree after Phase 00, in the repository's default collapsed
  untracked-directory view:

```text
## feature/gesc-gaussian-robustness-v1
 M ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash
?? DSIM_GESC_Gaussian_Codex_Implementation_Package/
?? docs/
```

- The modified wrapper and untracked implementation package predate Phase 00
  implementation and were preserved.
- Build/install/log handling: no build or test execution was run; existing
  generated trees were not modified. Two transient top-level colcon discovery
  log folders created during inspection were immediately removed, leaving no
  Phase 00 generated artifact.

## Files changed

Phase 00 created only:

- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/handoffs/phase_00_handoff.md`

The pre-existing saved plan
`docs/codex/gesc_gaussian/plans/phase_00_plan.md` was read, not modified.

## Public interfaces added or changed

None.

## Parameters added or changed

None.

## What is already implemented

- GESC full-rotation filtering and `Directional_Controller`;
- 20 RPM rotating sensor profile;
- negative-voltage minimization cost convention;
- single- and multi-light simulation cost models;
- opt-in PDE extension launch graph;
- PDE pose and cost histories;
- convergence metric, startup gate, repeated-candidate counter, and event;
- convergence-event mean anchoring;
- bounded fitted Gaussian center;
- adaptive bounded isotropic sigma;
- one or multiple persistent Gaussian fills;
- duplicate rejection by fill center and event center;
- decaying affine term based on PDE approach history with odometry fallback;
- raw and modified legacy cost topics;
- saturated `/cmd_vel` and controller diagnostic array;
- CSV experiment directories, live plotting, and final cost-surface PNG support;
- a dedicated custom interface package with five legacy messages.

## What is missing

- typed cost, GESC, controller, state, fill, and event observability;
- separate valid raw sensor, raw cost, and calibrated source score concepts;
- published Gaussian/affine contributions and cost weights;
- filter internal state and pre-saturation command diagnostics;
- explicit hybrid state machine and unified failsafe;
- synchronized robust basin estimation, covariance, depth, and curvature;
- residual-minimum validation, escalation, merge, revision, supersession, and
  confidence;
- measured escape progress, stall handling, deterministic assistance,
  boundaries, and recentering;
- rosbag recording, metadata, topic preflight, completeness checking, scenario
  automation, and bag analysis;
- Vicon, physical photoresistor, physical launch, and physical command
  adapters.

## Package assumptions disproved by the real repository

1. No Vicon or physical sensor path exists in this checkout.
2. No existing planner or recenter component can be reused.
3. No supervisor/state machine exists.
4. No repository-native rosbag workflow exists; only the environment provides
   `rosbag2_py` and sqlite3.
5. The simulated raw sensor and raw minimization cost are not separate topics.
6. No source score or source-score calibration is implemented.
7. The logical typed messages in the package are not existing interfaces.
8. Algorithm parameters use a mix of JSON, launch XML, CLI arguments, and ROS
   parameters; YAML is only established here for ros2_control.
9. `intensity_lumens` is relative to `reference_intensity_lumens`, not an
   absolute lux calibration.
10. The current Gaussian path already implements event-mean anchoring,
    bounded fits, multiple retained fills, duplicate rejection, and an affine
    term; later phases must extend these rather than duplicate them.
11. PDE nodes force simulation time and one uses hard-coded `/odom`, so
    simulation/physical parity is not already present.

## Exact Phase 01 edit set

The Phase 01 Plan must begin from this bounded set.

Interface definitions:

- modify `ros2_ws/src/ros_esc_interfaces/CMakeLists.txt`;
- create `ros2_ws/src/ros_esc_interfaces/msg/CostBreakdown.msg`;
- create `ros2_ws/src/ros_esc_interfaces/msg/GescDiagnostics.msg`;
- create `ros2_ws/src/ros_esc_interfaces/msg/ControlDiagnostics.msg`;
- create `ros2_ws/src/ros_esc_interfaces/msg/GaussianFill.msg`;
- create `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmState.msg`;
- create `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmEvent.msg`.

Existing owners to instrument:

- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py`;
- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`;
- `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_node_script.py`;
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`;
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py`;
- `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py`;
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`;
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`;
- `ros2_ws/src/ros_esc/package.xml` for actual changed-node dependencies.

Tests and documentation:

- create `ros2_ws/src/ros_esc/test/test_observability_contract.py`;
- create `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`;
- create `docs/codex/gesc_gaussian/topic_dictionary.md`;
- create `docs/codex/gesc_gaussian/handoffs/phase_01_handoff.md`.

Do not edit
`ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`
in Phase 01. Do not create a new ROS node solely to aggregate diagnostics.
Publish each value from its current owner. Mark unavailable source-score,
state-machine, and physical fields explicitly; never invent values.

Because this set exceeds roughly ten implementation files, the Phase 01 Plan
must split it into:

1. interface definitions/generation plus serialization tests;
2. existing-owner instrumentation/launch wiring plus numerical
   legacy-equivalence tests.

## Backward compatibility

- No legacy topic or message was changed in Phase 00.
- Phase 01 must add typed topics in parallel.
- `/cost_bias` remains `[amplitude, center_x, center_y, sigma]`.
- `/cost_modified` retains existing numerical output and timestamp.
- `/turtlebot3/control_value_chatter` remains the saturated six-value command.
- `use_pde_extensions=False` must remain unchanged.
- Heavy-Ball behavior is outside scope and must remain untouched.

## Tests and discovery run

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 00 implement
PASS: Phase 00 implement context is complete.
```

```text
bash -n ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash
PASS
```

```text
Read-only AST/JSON/XML parsing
PASS: 61 Python, 62 JSON, 5 XML files
```

```text
colcon list --base-paths ros2_ws/src
PASS: ros_esc, ros_esc_interfaces, turtlebot3_rotating_sensor
```

```text
colcon test-result --test-result-base ros2_ws/build --all --verbose
BASELINE: 885 tests, 0 errors, 875 failures, 1 skipped
```

No Gazebo launch, simulation, physical hardware, build, or new test execution
was performed.

## Known limitations

- The stored test tree is heavily failing from pre-existing lint debt.
- Installed executable discovery reflects the existing install tree, while
  source discovery is authoritative for current unbuilt files.
- No physical repository/interface was inspected.
- Float timestamps use inconsistent absolute/relative conventions between the
  legacy pipeline and PDE nodes.
- `/pde_cost_history` is unstamped and independently updated from pose history.
- The active rotation profile is `2.09439510239 rad/s` while
  `pde_omega=5.0`; Phase 00 did not establish whether this difference is
  intentional.

## Unresolved failures

- Existing test baseline: 875 failures, dominated by flake8/pep257/lint-cmake.
- No focused algorithm tests exist yet.
- Missing declared effective dependencies in `ros_esc/package.xml`.

## Decisions made

- `ros_esc_interfaces` is the only approved message package.
- Existing owners will publish their own diagnostics.
- Typed observability will be parallel to, not a replacement for, legacy
  arrays.
- `/odom` remains the simulation pose/velocity source until later canonical
  adapters are approved.
- Phase 09 must inventory physical interfaces before any physical edit.

## Exact next phase

Start a new Plan-mode chat with:

`DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/01_observability_PLAN.md`

Before planning, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 01 plan
```

Save the approved Plan at:

`docs/codex/gesc_gaussian/plans/phase_01_plan.md`

## Recommended commit message

```text
phase 00: audit dsim-lab GESC/Gaussian architecture
```
