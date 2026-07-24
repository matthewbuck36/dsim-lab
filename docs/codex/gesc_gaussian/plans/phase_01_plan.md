# Phase 01 Plan — Common GESC/Gaussian Observability and Data Interface

## Objective and scope

Add opt-in, typed observability for the existing GESC-plus-Gaussian pipeline without changing its numerical behavior, control policy, cost sign, saturation, launch defaults, or legacy topics.

This phase will expose:

- raw sensor availability, raw cost, source-score availability, Gaussian contribution, affine contribution, augmented cost, and effective weights;
- GESC filter input, output, and internal state;
- commands before and after saturation, limits, gains, and saturation flags;
- the current Gaussian-fill registry and fit diagnostics;
- algorithm-state placeholders and typed convergence/fill/configuration events;
- canonical pose, velocity, command, TF, and simulation/physical mappings.

It will not add the Phase 02 state machine, switch cost weights, calibrate `source_score`, implement physical adapters, run hardware, add rosbag recording, or introduce Heavy-Ball work.

The required Phase 01 context validator passed:

```text
Phase 01 plan context is complete.
```

## Repository findings and reuse

- Extend the existing `ros_esc_interfaces` package; do not create another interface package.
- Instrument these existing owners:

  - `CostFunction`: simulation source metadata and the non-PDE final cost.
  - `ModifiedCost2D`: raw/Gaussian/affine/augmented decomposition and effective weights.
  - `CustomFilter`: GESC input, output, state-before, derivative, and state-after.
  - `Directional_Controller` and `CustomController`: unsaturated and saturated commands, limits, gains, and saturation flags.
  - `ConvergenceDetector`: typed mirrors of convergence candidates and fill-ready events.
  - `GaussianFill`: typed fill records, current fit diagnostics, and fill outcomes.

- Preserve existing implementations rather than duplicating them:

  - `/turtlebot3/cost_value_chatter` remains the raw minimization cost.
  - `/cost_modified` remains raw plus Gaussian and affine terms.
  - `/cost_bias` remains `[amplitude, center_x, center_y, sigma]`.
  - `/turtlebot3/filter_value_chatter` remains the two-value GESC output.
  - `/turtlebot3/control_value_chatter` remains the saturated six-value command.
  - `/cmd_vel` and `/odom` remain the command and simulation feedback interfaces.
  - Existing convergence detection, Gaussian fitting, fill retention, duplicate rejection, and affine calculation remain unchanged.

- No raw ADC/photoresistor value, filtered sensor value, calibrated source score, supervisor state, physical pose adapter, room bounds, room center, or collision topic exists. These values must be marked unavailable, not synthesized.
- The working tree contains the previously documented user-owned modification to `gesc_gaussian_full_rotation_voltage.bash` and untracked implementation-package/docs directories. Preserve them.
- The audited commit remains `e0c693e6c9f954d3e7061c90089b7b2a2c6a1d4c`.

## Public interface design

### Timestamp contract

Every new typed message will contain:

```text
builtin_interfaces/Time stamp
float64 source_timestamp
bool source_timestamp_valid
```

- `stamp` is taken once from the publishing node’s ROS clock using `get_clock().now().to_msg()`.
- Simulation therefore uses `/clock`; a future physical launch will use ROS system time.
- `source_timestamp` preserves the triggering legacy message’s current float timestamp, including its existing relative-time semantics.
- No legacy timestamp is changed.
- Event and configuration messages without a meaningful upstream timestamp set `source_timestamp_valid=false`.

This requires adding `builtin_interfaces` to `ros_esc_interfaces`.

### New messages

Create the following definitions in `ros_esc_interfaces`.

#### `CostBreakdown.msg`

```text
uint8 SOURCE_UNKNOWN=0
uint8 SOURCE_SIMULATION=1
uint8 SOURCE_PHYSICAL=2

builtin_interfaces/Time stamp
float64 source_timestamp
bool source_timestamp_valid

uint8 source_mode
string source_name
uint32 channel_count

float64[] raw_sensor_value
float64[] filtered_sensor_value
float64[] raw_cost
float64[] source_score
float64[] gaussian_cost
float64[] affine_cost
float64[] augmented_cost

float64 sensor_weight
float64 gaussian_weight
float64 affine_weight

bool raw_sensor_valid
bool filtered_sensor_valid
bool raw_cost_valid
bool source_score_valid
bool gaussian_cost_valid
bool affine_cost_valid
bool augmented_cost_valid
bool weights_valid
```

Arrays retain the repository’s multi-sensor-channel behavior. Unavailable arrays have `channel_count` entries containing `NaN` and a false validity flag.

Current simulation semantics:

- `raw_sensor_valid=false`;
- `filtered_sensor_valid=false`;
- `raw_cost_valid=true`;
- `source_score_valid=false`;
- legacy non-PDE profile: `augmented_cost=raw_cost`, weights `(1,0,0)`;
- PDE profile: weights `(1,1,1)` except `affine_weight=0` when the existing affine feature is disabled.

Weights are observational snapshots only; Phase 01 does not make them switchable.

#### `GescDiagnostics.msg`

```text
builtin_interfaces/Time stamp
float64 source_timestamp
bool source_timestamp_valid
bool valid

float64[] filter_input
float64[] filter_output
float64[] filter_state_before
float64[] filter_state_derivative
float64[] filter_state_after

float64 dither_phase_rad
bool dither_phase_valid
float64 dither_amplitude_m
bool dither_amplitude_valid
float64 dither_angular_frequency_rad_sec
bool dither_angular_frequency_valid
```

The first appended encoder value supplies the observed phase when present. Amplitude and frequency remain unavailable because `CustomFilter` cannot unambiguously derive them from its generic configuration.

#### `ControlDiagnostics.msg`

```text
builtin_interfaces/Time stamp
float64 source_timestamp
bool source_timestamp_valid
string controller_type

float64[6] gesc_command_unsaturated
bool gesc_command_unsaturated_valid

float64[6] supervisor_contribution
bool supervisor_contribution_valid

float64[6] combined_command_unsaturated
bool combined_command_unsaturated_valid

float64[6] final_command
bool final_command_valid

bool[6] saturation_flags
bool[6] limit_valid
float64[6] lower_limits
float64[6] upper_limits

float64 k_vx
float64 k_wz
bool gains_valid
```

For `Directional_Controller`, the unsaturated and combined commands are identical in Phase 01. `supervisor_contribution_valid=false` and its values are `NaN`; no supervisor is simulated. The final command must exactly match the legacy controller output.

#### `GaussianFill.msg`

```text
builtin_interfaces/Time stamp
float64 source_timestamp
bool source_timestamp_valid
string frame_id

uint64 fill_id
uint64 cluster_id
uint32 revision

float64 center_x
float64 center_y
float64 amplitude
float64 covariance_xx
float64 covariance_xy
float64 covariance_yy
float64 sigma_major
float64 sigma_minor
float64 orientation
float64 support_radius
float64 exit_radius
float64 confidence
uint32 sample_count
float64 fit_residual
float64 fit_condition_number
uint32 design_escalations

bool covariance_valid
bool principal_widths_valid
bool support_radius_valid
bool exit_radius_valid
bool confidence_valid
bool sample_count_valid
bool fit_residual_valid
bool fit_condition_number_valid
bool design_escalations_valid
bool active
bool superseded
```

For current isotropic fills:

- IDs are observational, one-based, and assigned in acceptance order.
- `cluster_id=fill_id`, `revision=1`, `active=true`, and `superseded=false`.
- covariance is `diag(sigma², sigma²)`, widths are both `sigma`, and orientation is zero.
- sample count, RMS fit residual, and Jacobian condition number are reported from the existing least-squares fit without affecting acceptance.
- support radius, exit radius, confidence, and design escalation remain invalid until later phases.
- The append-only stream is the Phase 01 registry: latest revision per `fill_id` defines registry state.

#### `AlgorithmState.msg`

Define constants for `STATE_UNAVAILABLE` and the eight planned Phase 02 states, followed by:

```text
builtin_interfaces/Time stamp
float64 source_timestamp
bool source_timestamp_valid

string run_id
bool run_id_valid
string algorithm_profile

uint8 state
string state_name
bool state_valid
uint8 previous_state
string previous_state_name
bool previous_state_valid
string transition_reason
bool transition_reason_valid
float64 state_elapsed_sec
bool state_elapsed_valid

uint32 active_fill_count
bool active_fill_count_valid
uint64 active_escape_fill_id
bool active_escape_fill_id_valid

float64 sensor_weight
float64 gaussian_weight
float64 affine_weight
bool weights_valid

bool failsafe
bool failsafe_valid
```

Phase 01 publishes `STATE_UNAVAILABLE` with `state_valid=false`; it does not imitate a state machine. `algorithm_profile` is `legacy` or `legacy_pde_gaussian`. Run ID, transition, elapsed state, active escape fill, and failsafe remain explicitly unavailable.

#### `AlgorithmEvent.msg`

Define stable constants for configuration, capability-unavailable, convergence, fill, goal, escape, recenter, timeout, and failsafe event categories. Include:

```text
builtin_interfaces/Time stamp
float64 source_timestamp
bool source_timestamp_valid

uint16 event_type
uint8 state
string state_name
bool state_valid

uint64 fill_id
bool fill_id_valid
int32 reason_code
string detail

string[] value_names
float64[] values
```

`value_names` and `values` must always have equal lengths. Phase 01 emits only configuration/capability, convergence, fill-created, and fill-rejected events. Later event constants are interface reservations, not implemented behavior.

### Canonical topics

All new typed topics use queue depth 10 and the selected platform-independent namespace:

| Topic | Type | Phase 01 publisher |
|---|---|---|
| `/gesc_gaussian/cost_breakdown` | `ros_esc_interfaces/msg/CostBreakdown` | `CostFunction` in non-PDE mode; `ModifiedCost2D` in PDE mode |
| `/gesc_gaussian/gesc_diagnostics` | `ros_esc_interfaces/msg/GescDiagnostics` | `CustomFilter` |
| `/gesc_gaussian/control_diagnostics` | `ros_esc_interfaces/msg/ControlDiagnostics` | `CustomController` |
| `/gesc_gaussian/gaussian_fills` | `ros_esc_interfaces/msg/GaussianFill` | `GaussianFill` |
| `/gesc_gaussian/algorithm_state` | `ros_esc_interfaces/msg/AlgorithmState` | Same mutually exclusive owner as final cost breakdown |
| `/gesc_gaussian/algorithm_events` | `ros_esc_interfaces/msg/AlgorithmEvent` | Intentional append-only event bus from current source, modified-cost, convergence, and fill owners |

There must never be two active publishers for cost breakdown or algorithm state. Multiple event publishers are intentional because each event retains its producing responsibility.

### Simulation/physical mapping

| Logical data | Simulation mapping | Physical mapping |
|---|---|---|
| Cost chain and source selection | `/gesc_gaussian/cost_breakdown`; `source_mode=SIMULATION` | Same topic/type from the audited physical adapter and shared modified-cost owner; adapter path remains Phase 09 work |
| GESC internals | `/gesc_gaussian/gesc_diagnostics` from shared `CustomFilter` | Same node/topic/type |
| Control diagnostics | `/gesc_gaussian/control_diagnostics` from shared controller | Same node/topic/type |
| Fill registry | `/gesc_gaussian/gaussian_fills` | Same shared Gaussian owner/topic/type |
| State/events | `/gesc_gaussian/algorithm_state`, `/gesc_gaussian/algorithm_events` | Same canonical topics; Phase 02 supervisor later becomes sole state owner |
| Measured pose/velocity | Existing `/odom`, `nav_msgs/msg/Odometry` | Physical adapter must provide/remap the same canonical odometry interface after Phase 09 inventory |
| Final command | Existing `/cmd_vel`, `geometry_msgs/msg/Twist` | Same canonical command; hardware adapter is not created here |
| Raw Vicon | Unavailable | Optional raw physical topic remains unnamed until Phase 09 |
| TF | Existing `/tf` and `/tf_static` | Same standard topics when physical adapters provide them |
| Room bounds/center and collision | Unavailable and reported as such | Remain unavailable until their actual owners are implemented |

The Phase 05 topic manifest may map `raw_sensor`, `raw_cost`, and `source_score` aliases to fields on the single cost-breakdown topic.

## Exact file changes

### Modify

- `ros2_ws/src/ros_esc_interfaces/CMakeLists.txt`
  - Register the six messages and add `builtin_interfaces` to generated-interface dependencies.
- `ros2_ws/src/ros_esc_interfaces/package.xml`
  - Declare `builtin_interfaces`.
- `ros2_ws/src/ros_esc/package.xml`
  - Declare the effective changed-node dependencies: `ros_esc_interfaces`, `geometry_msgs`, `nav_msgs`, and `std_msgs`.
- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py`
  - Add optional final-breakdown/state publishers, source/configuration events, source-mode metadata, and validity-marked unavailable fields.
- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`
  - Preserve the existing calculation while retaining separate effective Gaussian and affine arrays for typed publication.
  - Publish final cost breakdown/state and one configuration snapshot.
- `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_node_script.py`
  - Capture the exact input, state-before, derivative, state-after, output, and observed encoder phase.
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`
  - Publish typed diagnostics after publishing the unchanged legacy command.
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py`
  - Have `Directional_Controller` retain its most recent pre-saturation values, post-saturation values, flags, limits, and gains without changing `controller_output()` or its return value.
- `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py`
  - Mirror current candidate/fill-ready logs and parameter snapshots as typed events.
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`
  - Publish the accepted fill as typed data and mirror current acceptance/rejection logs.
  - Return observational sample-count/residual/condition diagnostics from the existing fit without using them for control decisions.
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
  - Add compatible observability arguments and wire them to existing executables.
  - Select `CostFunction` as the final typed cost/state owner only when `use_pde_extensions=False`.
- `docs/codex/gesc_gaussian/topic_dictionary.md`
  - Created during implementation, then populated with fields, units, validity semantics, owners, rates, timestamps, and legacy mappings.
- `docs/codex/gesc_gaussian/handoffs/phase_01_handoff.md`
  - Created at the end of implementation with exact changes and test results.

### Create

- `ros2_ws/src/ros_esc_interfaces/msg/CostBreakdown.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/GescDiagnostics.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/ControlDiagnostics.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/GaussianFill.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmState.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmEvent.msg`
- `ros2_ws/src/ros_esc/test/test_observability_contract.py`
- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`
- `docs/codex/gesc_gaussian/topic_dictionary.md`
- `docs/codex/gesc_gaussian/handoffs/phase_01_handoff.md`

No new ROS node, algorithm package, interface package, service, recorder, or hardware adapter is justified or permitted.

Do not modify:

- `gesc_gaussian_full_rotation_voltage.bash`;
- the data-collection node or CSV format;
- PDE history nodes;
- controller/filter JSON;
- cost-model JSON;
- Heavy-Ball files;
- generated `build`, `install`, or `log` files except as normal build/test outputs.

## Parameters and launch arguments

Add these `gazebo.launch.xml` arguments:

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

Match existing node configuration styles:

- `CostFunction`, `CustomFilter`, and `CustomController` receive optional CLI arguments with the defaults above.
- `ModifiedCost2D`, `ConvergenceDetector`, and `GaussianFill` receive equivalent ROS parameters.
- `CostFunction` receives `publish_final_breakdown=True` only in non-PDE mode.
- Observability disabled means no typed diagnostic publication and no extra diagnostic calculations beyond the inexpensive guard check.
- If the launch front end cannot evaluate the inverse PDE condition as a boolean argument, use two mutually exclusive cost-function executable declarations with identical legacy arguments and different observability-owner flags; do not allow duplicate canonical publishers.

## Publication timing and behavior

- Cost breakdown and algorithm state: once per accepted raw-cost callback, using the same channel sample and preserved source timestamp.
- GESC diagnostics: once per legacy filter output.
- Control diagnostics: once per legacy command output.
- Gaussian fill: once per accepted fill/revision.
- Convergence/fill events: once at the corresponding existing event/log site.
- Configuration snapshot events: once per enabled owner after a valid ROS clock/sample is available.
- Legacy outputs are calculated and published first; optional typed mirrors follow.
- Source configuration snapshots include the actual configured source count, active source positions, relative-intensity inputs, and cost-model class. They must not describe relative simulator intensity as absolute photometric calibration.
- Existing console lines remain. Each typed convergence/fill event uses the same reason and numeric values as its console mirror.
- No periodic timer, polling loop, synchronization policy, state transition, or control branch is added.

## Backward compatibility and migration

- `enable_observability=False` is the unchanged legacy profile and remains the default.
- Existing topic names, message definitions, queue depths, positional layouts, cost sign, timestamps, parameters, command limits, and launch wrapper remain unchanged.
- `/cost_modified` must remain numerically identical and preserve its input timestamp.
- `/cmd_vel` and `/turtlebot3/control_value_chatter` must remain identical to current post-saturation output.
- Existing consumers require no migration.
- New consumers must rebuild `ros_esc_interfaces` and subscribe to `/gesc_gaussian/*`.
- Adding messages is additive; none of the five existing custom messages is edited.
- Phase 02 will make weights switchable and move `/gesc_gaussian/algorithm_state` to the new supervisor as its sole publisher without changing the Phase 01 message/topic contract.
- Phase 03 will publish fill revisions, merge/supersession state, support/exit radii, and confidence through the existing `GaussianFill` interface.
- Phase 05 will record these topics while retaining the legacy CSV collector.

## Implementation sequence

Implement as two coherent subcommits because the bounded Phase 00 edit set exceeds ten implementation files.

1. Interface and serialization foundation

   - Add `builtin_interfaces`.
   - Add and register all six messages.
   - Build `ros_esc_interfaces`.
   - Add import, constant, round-trip serialization, fixed-array, validity, and event-name/value pairing tests.
   - Create the topic-dictionary skeleton.

2. Existing-owner instrumentation

   - Instrument cost owners with mutually exclusive canonical publishing.
   - Decompose modified cost without changing evaluation order or arithmetic.
   - Instrument filter and controller internals.
   - Add typed convergence, configuration, fill, and rejection events.
   - Wire opt-in launch arguments.
   - Add numerical legacy-equivalence and launch-contract tests.
   - Complete the topic dictionary and Phase 01 handoff.

Recommended subcommit messages:

```text
phase 01a: add GESC Gaussian observability messages
phase 01b: instrument existing GESC Gaussian owners
```

## Tests and acceptance criteria

### `test_observability_contract.py`

Test:

- all six generated messages import and serialize/deserialize;
- `stamp` and source-timestamp fields retain their values;
- cost arrays match `channel_count`;
- unavailable raw sensor, filtered sensor, source score, state, failsafe, and supervisor fields have false validity and `NaN` placeholders;
- event `value_names` and `values` lengths match;
- Gaussian covariance and widths correctly represent the current isotropic sigma;
- fill IDs are stable, one-based, active, and revision one;
- each owner creates its typed publisher only when enabled;
- exactly one final cost/state publisher is selected in PDE and non-PDE launch profiles;
- all canonical topic names and defaults parse from `gazebo.launch.xml`;
- configuration, convergence, and fill events contain finite numeric values where marked valid.

### `test_legacy_behavior.py`

Test:

- enabling/disabling observability does not alter raw cost messages;
- Gaussian and affine decomposition recombines exactly to the existing `/cost_modified` result for per-sensor and odometry-fallback paths;
- `bias_all_channels=False` retains the existing first-channel-only behavior;
- `/cost_modified` retains the incoming timestamp;
- `/cost_bias` remains exactly `[A, center_x, center_y, sigma]`;
- filter output and state integration remain unchanged with diagnostics disabled and enabled;
- `Directional_Controller` returns the same six-value saturated output as before;
- unsaturated diagnostics, flags, limits, and final diagnostics match deterministic saturation cases;
- legacy controller chatter and `/cmd_vel` remain identical;
- typed event emission does not change convergence counters, reset behavior, fill acceptance, cooldown, duplicate rejection, or maximum-fill handling.

### Commands

From the repository root:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 01 implement
```

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
```

```bash
ros2 interface show ros_esc_interfaces/msg/CostBreakdown
ros2 interface show ros_esc_interfaces/msg/GescDiagnostics
ros2 interface show ros_esc_interfaces/msg/ControlDiagnostics
ros2 interface show ros_esc_interfaces/msg/GaussianFill
ros2 interface show ros_esc_interfaces/msg/AlgorithmState
ros2 interface show ros_esc_interfaces/msg/AlgorithmEvent
```

```bash
python3 -m pytest -q \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
```

```bash
colcon test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose
```

```bash
cd ..
python3 -B - <<'PY'
import xml.etree.ElementTree as ET
ET.parse("ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml")
print("gazebo.launch.xml: OK")
PY

source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args

DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_required_docs.sh
git diff --check
git status --short --branch
```

No Gazebo motion run and no physical-hardware command is required for Phase 01. Report focused test results separately from the documented pre-existing lint baseline of 875 failures.

Acceptance requires:

- all focused tests pass;
- all six interfaces generate and serialize;
- no legacy-equivalence test changes numerically;
- no duplicate final cost/state publisher exists;
- every available value is finite and every unavailable value is explicitly invalid;
- default launch behavior remains observability-disabled;
- no physical or Heavy-Ball files change.

## Stop conditions and risks

Stop and report exact evidence if:

- the Phase 01 validator or saved-plan validator fails;
- the repository no longer matches the audited commit/owners;
- `builtin_interfaces` is unavailable;
- interface generation requires changing an existing message;
- PDE and non-PDE launch selection produces duplicate canonical publishers;
- decomposition changes `/cost_modified`, its timestamp, or channel layout;
- controller instrumentation changes saturation or returned commands;
- filter instrumentation changes integration order or state;
- a physical filename, topic, calibration, or hardware command would have to be guessed;
- the user-owned wrapper would have to be edited;
- focused tests cannot run;
- unrelated working-tree changes overlap a required file.

Principal risks are diagnostic overhead, accidental double evaluation of the stateful affine-term pruning path, ambiguity between raw sensor and simulated cost, and inconsistent legacy timestamps. Mitigate them with opt-in publication, one affine evaluation per channel, explicit validity flags, absolute ROS stamps, preserved source timestamps, and exact legacy-equivalence tests.

## Implementation-time verification assumptions

- Verify `builtin_interfaces` resolves in ROS 2 Humble before editing interfaces.
- Verify the launch Boolean inversion selects only one final cost/state owner; use the specified mutually exclusive executable fallback if needed.
- Verify `Directional_Controller` is the selected controller in the active GESC wrapper before asserting GESC-specific pre-saturation validity.
- Verify Gaussian Jacobian condition calculation is finite for the deterministic fixture; mark only that field invalid if the existing fit is singular.
- Verify source-count and active source arguments remain available after `configure_light_source_cost`; otherwise publish only the source model/mode and mark detailed source configuration unavailable.
- Treat `/odom` as simulation-only until Phase 09 audits the physical adapter.
- Treat `intensity_lumens` as relative simulator input, never absolute calibration.
- Preserve the known user-owned wrapper modification and all pre-existing untracked project documents.
