# Phase 01 Handoff

## Objective completed

Implemented opt-in common observability and data interfaces for the existing
GESC plus Gaussian pipeline. Six typed messages now expose cost decomposition,
GESC internals, controller saturation, accepted fills, algorithm-state
availability, and structured events without changing the numerical controller
path.

The saved Phase 01 Plan was verified against the live checkout before editing.
The required context validator passed, the repository remained at the audited
commit, `builtin_interfaces` was available, the active wrapper still selected
`Directional_Controller`, and no required implementation file had an
overlapping user change. No stop-condition contradiction was found.

## Repository state

- Repository: `/home/mattb/dsim-lab`
- Branch: `feature/gesc-gaussian-robustness-v1`
- Starting commit: `e0c693e6c9f954d3e7061c90089b7b2a2c6a1d4c`
- Pre-existing user change preserved:
  `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`
- Pre-existing untracked implementation package and Phase 00/Plan documents
  were preserved.
- Build/install/log handling: repository-standard colcon build/test updated
  the ignored generated workspace trees. Diagnostic colcon logs were directed
  to `/tmp/dsim_phase01_*`; no generated artifact was added as source.

The implementation exceeds ten files because the approved contract requires
six messages and instrumentation at each existing owner. It is split into the
two coherent units required by the saved Plan:

1. interface definitions and generation dependencies;
2. existing-owner instrumentation, launch wiring, tests, and documentation.

## Files changed

### Interface foundation

- `ros2_ws/src/ros_esc_interfaces/CMakeLists.txt`
- `ros2_ws/src/ros_esc_interfaces/package.xml`
- `ros2_ws/src/ros_esc_interfaces/msg/CostBreakdown.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/GescDiagnostics.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/ControlDiagnostics.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/GaussianFill.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmState.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmEvent.msg`

### Existing-owner instrumentation

- `ros2_ws/src/ros_esc/package.xml`
- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`
- `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py`
- `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`

### Tests and documentation

- `ros2_ws/src/ros_esc/test/test_observability_contract.py`
- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`
- `docs/codex/gesc_gaussian/topic_dictionary.md`
- `docs/codex/gesc_gaussian/handoffs/phase_01_handoff.md`

The user-owned GESC wrapper, Heavy-Ball files, data collector, CSV format,
filter/controller JSON, cost JSON, PDE history nodes, and physical files were
not changed by Phase 01.

## Public interfaces added or changed

Added messages in `ros_esc_interfaces`:

- `CostBreakdown`
- `GescDiagnostics`
- `ControlDiagnostics`
- `GaussianFill`
- `AlgorithmState`
- `AlgorithmEvent`

Added canonical opt-in topics:

- `/gesc_gaussian/cost_breakdown`
- `/gesc_gaussian/gesc_diagnostics`
- `/gesc_gaussian/control_diagnostics`
- `/gesc_gaussian/gaussian_fills`
- `/gesc_gaussian/algorithm_state`
- `/gesc_gaussian/algorithm_events`

Every message has an absolute ROS stamp, the triggering legacy float timestamp,
and explicit source-timestamp validity. Unavailable floating-point data is
`NaN` with false validity. Unsigned placeholders use zero with false validity.

No existing message definition or topic contract changed.

## Parameters added or changed

New central launch arguments, all additive:

| Argument | Default |
|---|---|
| `enable_observability` | `False` |
| `cost_breakdown_topic` | `/gesc_gaussian/cost_breakdown` |
| `gesc_diagnostics_topic` | `/gesc_gaussian/gesc_diagnostics` |
| `control_diagnostics_topic` | `/gesc_gaussian/control_diagnostics` |
| `gaussian_fill_diagnostics_topic` | `/gesc_gaussian/gaussian_fills` |
| `algorithm_state_topic` | `/gesc_gaussian/algorithm_state` |
| `algorithm_event_topic` | `/gesc_gaussian/algorithm_events` |
| `observability_source_mode` | `simulation` |

The cost, filter, and controller executables receive optional CLI arguments.
Modified cost, convergence, and Gaussian fill receive equivalent ROS
parameters. PDE and non-PDE cost executables are mutually exclusive; only the
selected final cost owner publishes cost breakdown and algorithm state.

## Behavior implemented

- `CostFunction` publishes simulation source metadata, raw cost, fixed legacy
  weights, explicit sensor/source-score unavailability, legacy augmented cost,
  placeholder state, and source configuration/capability events.
- `ModifiedCost2D` retains separate Gaussian and affine results from each
  existing evaluation and publishes their exact recombination. The stateful
  affine evaluation is not repeated for diagnostics.
- `CustomFilter` publishes exact input, output, state before, derivative, state
  after, and observed encoder phase. Generic amplitude/frequency remain
  explicitly unavailable.
- `Directional_Controller` retains its pre-saturation command, final command,
  flags, limits, and gains. `CustomController` publishes those values after
  the unchanged legacy Twist and array messages.
- `ConvergenceDetector` publishes configuration, candidate, and confirmed
  typed events after the corresponding legacy output/log site.
- `GaussianFill` publishes one-based, revision-one isotropic fill records,
  sample count, fit RMS residual, finite Jacobian condition when available,
  and fill-created/rejected events. Fit diagnostics do not affect acceptance.
- `AlgorithmState` is intentionally `STATE_UNAVAILABLE` in Phase 01. The eight
  planned Phase 02 states are reserved, not simulated.
- Source-mode metadata supports the same logical topic/type mapping for
  simulation and future physical adapters. No physical topic or calibration
  was guessed.

## Backward compatibility

- `enable_observability=False` remains the default.
- Existing calculations and legacy publications occur before typed mirrors.
- `/turtlebot3/cost_value_chatter` is unchanged.
- `/cost_modified` retains its numerical output, channel layout, and input
  timestamp.
- `/cost_bias` remains exactly
  `[amplitude, center_x, center_y, sigma]`.
- `/turtlebot3/filter_value_chatter` retains the existing output and filter
  integration order.
- `/turtlebot3/control_value_chatter` and `/cmd_vel` retain the exact
  post-saturation command.
- Negative-voltage minimization sign, units, queue depths, controller limits,
  Gaussian acceptance, fill retention, convergence counters, and launch
  defaults are unchanged.
- No state machine, weight switching, calibrated source score, recorder,
  physical adapter, or Heavy-Ball behavior was added.

## Tests run

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 01 implement
PASS: Phase 01 implement context is complete.
```

```text
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
PASS: 3 packages finished.
```

```text
source install/setup.bash
python3 -m pytest -q \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
PASS: 16 passed in 0.79s.
```

The focused tests cover generated-message serialization, timestamp retention,
validity/`NaN` semantics, fixed arrays, event value pairing, canonical launch
defaults and owner selection, publisher opt-in, cost recombination, first-
channel bias behavior, filter state equivalence, deterministic controller
saturation, Twist/legacy/typed command equality, legacy fill layout, one-based
fill IDs, covariance, and fit diagnostics without Gazebo or hardware.

```text
ros2 interface show ros_esc_interfaces/msg/{CostBreakdown,GescDiagnostics,
ControlDiagnostics,GaussianFill,AlgorithmState,AlgorithmEvent}
PASS: all six generated interfaces resolved.
```

```text
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args
PASS: launch parsed and displayed all eight observability defaults.
```

```text
colcon test --packages-select \
  ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose
EXPECTED BASELINE FAILURES: 901 tests, 0 errors, 875 failures, 1 skipped.
```

The Phase 00 stored baseline was 885 tests, 875 failures, and 1 skipped. Phase
01 adds 16 passing tests; the count of failing tests remains exactly 875. The
failures remain the repository's pre-existing flake8, pep257, and lint-cmake
test cases. The already-failing flake8 report also scans the new files and
continues to report the repository's double-quote/style convention; this phase
does not attempt the out-of-scope repository-wide lint cleanup.

No Gazebo motion run and no physical command was executed.

## Known limitations

- Raw sensor, filtered sensor, and calibrated source score do not exist in the
  current simulation adapter and are explicitly unavailable.
- Phase 01 state, previous state, transition, run ID, active escape fill, and
  failsafe are unavailable until the supervisor is implemented.
- Supervisor contribution, dither amplitude/frequency, support/exit radius,
  confidence, design escalations, room bounds/center, collision, physical pose,
  and physical sensor mappings remain unavailable.
- The existing PDE nodes still force simulation time and `/odom` remains a
  simulation mapping until the physical inventory.
- `intensity_lumens` remains a relative simulator input, not an absolute
  photometric calibration.
- The event bus intentionally has multiple responsible publishers; final cost
  breakdown and state intentionally have only one selected publisher.

## Unresolved failures

- Repository-standard lint remains red at the documented 875-test baseline.
- No full Gazebo motion run was required or performed for this interface-only
  phase.
- Physical integration remains blocked on the Phase 09 inventory and the
  simulation acceptance gates.

## Decisions made

- Extended `ros_esc_interfaces`; no duplicate interface or algorithm package
  was created.
- Kept typed observability parallel to every legacy interface.
- Used explicit validity plus `NaN` rather than invented raw sensor,
  source-score, supervisor, or physical values.
- Kept source and final-cost ownership separate: source configuration events
  may come from `CostFunction`, while `ModifiedCost2D` is the sole PDE final
  breakdown/state owner.
- Represented current Gaussian fills as isotropic covariance with observational
  one-based IDs; later merge/revision behavior can extend the same message.
- Reserved later state/event enums without emitting unimplemented behavior.

## Exact next phase

Start a new Plan-mode chat with:

`DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/02_state_machine_PLAN.md`

Before planning, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 02 plan
```

Save the approved plan at:

`docs/codex/gesc_gaussian/plans/phase_02_plan.md`

## Recommended commit messages

```text
phase 01a: add GESC Gaussian observability messages
phase 01b: instrument existing GESC Gaussian owners
```

The user-facing combined recommendation remains:

```text
phase 01: add common GESC Gaussian observability interfaces
```
