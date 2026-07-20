# GESC Gaussian Topic and Message Dictionary

This dictionary is the resolved Phase 01 interface contract for the current
`dsim-lab` checkout. The new interface is additive and opt-in. The central
Gazebo launch keeps `enable_observability=False` by default, so all legacy
behavior and traffic remain unchanged unless observability is requested.

## Common timestamp and validity contract

Every new message contains:

- `stamp`: the publishing node's ROS clock, captured with
  `get_clock().now().to_msg()`. Gazebo nodes therefore follow `/clock`; the
  same field can use ROS system time in a future physical launch.
- `source_timestamp`: the float timestamp on the legacy input that triggered
  the publication.
- `source_timestamp_valid`: whether `source_timestamp` is meaningful and
  finite. Configuration events have no upstream sample and set this false.

An unavailable floating-point scalar or array element is `NaN` and its
corresponding validity field is false. An unavailable unsigned identifier is
zero and its validity field is false. Empty unavailable strings also have a
false validity field. Consumers must inspect validity fields before using a
value.

All new publishers use queue depth 10. Publication is sample-driven; Phase 01
adds no timer, synchronizer, polling loop, or control branch.

## Canonical typed topics

| Topic | Message | Owner | Publication rate |
|---|---|---|---|
| `/gesc_gaussian/cost_breakdown` | `ros_esc_interfaces/msg/CostBreakdown` | `cost_function` without PDE extensions; `modified_cost_2d` with PDE extensions | Once per accepted raw-cost sample |
| `/gesc_gaussian/gesc_diagnostics` | `ros_esc_interfaces/msg/GescDiagnostics` | `custom_filter` | Once per legacy filter output |
| `/gesc_gaussian/control_diagnostics` | `ros_esc_interfaces/msg/ControlDiagnostics` | `custom_controller` | Once per legacy command output |
| `/gesc_gaussian/gaussian_fills` | `ros_esc_interfaces/msg/GaussianFill` | `gaussian_fill` | Once per accepted fill |
| `/gesc_gaussian/algorithm_state` | `ros_esc_interfaces/msg/AlgorithmState` | Same mutually exclusive owner as final cost breakdown | Once per accepted raw-cost sample |
| `/gesc_gaussian/algorithm_events` | `ros_esc_interfaces/msg/AlgorithmEvent` | Source, modified-cost, convergence, and fill owners | At the corresponding configuration, convergence, fill-created, or fill-rejected site |

The two cost owners are mutually exclusive in `gazebo.launch.xml`. Multiple
event publishers are intentional because each existing node retains ownership
of the event it detects.

## `CostBreakdown`

### Source metadata

| Field | Meaning |
|---|---|
| `source_mode` | `SOURCE_UNKNOWN`, `SOURCE_SIMULATION`, or `SOURCE_PHYSICAL` |
| `source_name` | Current simulation cost-model class in non-PDE mode; `modified_cost_2d` in PDE mode |
| `channel_count` | Number of sensor/cost channels represented by every cost array |

`observability_source_mode` selects the enum without changing algorithm logic.
The same topic and message can therefore be populated by simulation and future
audited physical adapters.

### Cost fields and units

| Field | Current source | Units/semantics | Phase 01 validity |
|---|---|---|---|
| `raw_sensor_value[]` | No separate value exists in this checkout | Adapter-native sensor units | Invalid, `NaN` |
| `filtered_sensor_value[]` | No separate value exists | Adapter-native sensor units | Invalid, `NaN` |
| `raw_cost[]` | Legacy `/turtlebot3/cost_value_chatter` | Existing minimization cost units; voltage profiles retain negative-voltage sign | Valid when finite |
| `source_score[]` | No calibration exists | Intended dimensionless source score | Invalid, `NaN` |
| `gaussian_cost[]` | Existing Gaussian term evaluation | Cost units | Valid; zero when no fill contributes |
| `affine_cost[]` | Existing decaying affine evaluation | Cost units | Valid; zero when disabled or inactive |
| `augmented_cost[]` | Legacy raw or `/cost_modified` result | Cost units | Valid when finite |
| `sensor_weight` | Fixed Phase 01 observation | Dimensionless | `1.0`, valid |
| `gaussian_weight` | Fixed Phase 01 observation | Dimensionless | `0.0` in legacy mode, `1.0` in PDE mode |
| `affine_weight` | Fixed Phase 01 observation | Dimensionless | `0.0` in legacy/disabled-affine mode, otherwise `1.0` |

In PDE mode the identity is:

```text
augmented_cost = raw_cost + gaussian_cost + affine_cost
```

`bias_all_channels=False` preserves the legacy first-channel-only correction;
typed Gaussian and affine contributions for the other channels are zero.

## `GescDiagnostics`

| Field | Meaning | Units/validity |
|---|---|---|
| `valid` | All published filter arrays are finite | Boolean |
| `filter_input[]` | Exact cost input, including appended encoder data when configured | Mixed legacy input units |
| `filter_output[]` | Exact values sent on `/turtlebot3/filter_value_chatter` | Existing GESC estimate units |
| `filter_state_before[]` | State before the current differential update | Filter-state units |
| `filter_state_derivative[]` | Derivative used by the current update | Filter-state units per second |
| `filter_state_after[]` | State after the existing validity-aware Euler update | Filter-state units |
| `dither_phase_rad` | First appended encoder value | Radians; valid only when encoder append is active and finite |
| `dither_amplitude_m` | Not unambiguously available from the generic filter owner | `NaN`, invalid |
| `dither_angular_frequency_rad_sec` | Not unambiguously available from the generic filter owner | `NaN`, invalid |

Diagnostics copy the values already evaluated by `CustomFilter`; they do not
perform a second filter or state update.

## `ControlDiagnostics`

All command arrays use the repository order
`[vx, vy, vz, wx, wy, wz]`, with linear components in meters per second and
angular components in radians per second.

| Field | Current `Directional_Controller` meaning |
|---|---|
| `controller_type` | Python controller class name |
| `gesc_command_unsaturated[6]` | GESC command immediately before existing limit checks |
| `supervisor_contribution[6]` | `NaN` and invalid; no Phase 01 supervisor exists |
| `combined_command_unsaturated[6]` | Same as the unsaturated GESC command in Phase 01 |
| `final_command[6]` | Exact post-saturation legacy command |
| `saturation_flags[6]` | True where a component exceeded its configured limit |
| `limit_valid[6]` | True for `vx` and `wz`; other components are structurally zero and have no declared numeric limit |
| `lower_limits[6]`, `upper_limits[6]` | `[-max_vx,+max_vx]` and `[-max_wz,+max_wz]`; invalid positions are `NaN` |
| `k_vx`, `k_wz` | Configured directional-controller gains |

For controller classes that do not retain these internals, the unsaturated,
limit, and supervisor fields are explicitly invalid. `final_command` remains
available from the generic controller output.

## `GaussianFill`

The topic is an append-only registry stream. The latest revision for a
`fill_id` defines registry state; Phase 01 creates revision one only.

| Field | Phase 01 meaning | Units/validity |
|---|---|---|
| `frame_id` | `odom` | Frame name |
| `fill_id` | One-based acceptance order | Valid |
| `cluster_id` | Equal to `fill_id` | Valid |
| `revision` | `1` | Valid |
| `center_x`, `center_y` | Exact legacy published fill center | Meters |
| `amplitude` | Exact legacy configured fill amplitude | Cost units |
| `covariance_xx`, `covariance_yy` | `sigma^2` | Square meters, valid |
| `covariance_xy` | `0.0` | Square meters, valid |
| `sigma_major`, `sigma_minor` | Exact legacy isotropic sigma | Meters, valid |
| `orientation` | `0.0` for isotropic fill | Radians |
| `support_radius`, `exit_radius` | Not implemented | `NaN`, invalid |
| `confidence` | Not implemented | `NaN`, invalid |
| `sample_count` | Samples used by the existing least-squares fit | Valid |
| `fit_residual` | Root-mean-square residual of that fit | Cost units, valid when finite |
| `fit_condition_number` | Condition number of the existing fit Jacobian | Valid only when finite |
| `design_escalations` | Not implemented | Zero placeholder, invalid |
| `active` | Current accepted fill is active | True |
| `superseded` | No Phase 01 supersession exists | False |

Residual and condition diagnostics do not participate in fill acceptance.
The legacy `/cost_bias` layout remains exactly
`[amplitude, center_x, center_y, sigma]`.

## `AlgorithmState`

The interface reserves `SEARCH`, `VERIFY_EXTREMUM`,
`DESIGN_OR_MERGE_FILL`, `ESCAPE_REPULSE`, `ESCAPE_ASSIST`, `RECENTER`,
`GOAL_HOLD`, and `FAILSAFE` for Phase 02. Phase 01 does not imitate that state
machine.

| Field | Phase 01 value |
|---|---|
| `algorithm_profile` | `legacy` without PDE; `legacy_pde_gaussian` with PDE |
| `state`, `state_name`, `state_valid` | `STATE_UNAVAILABLE`, `UNAVAILABLE`, false |
| Previous state/transition/elapsed state | Explicitly unavailable |
| `active_fill_count` | `0` in legacy mode; current accepted term count in PDE mode, valid |
| `active_escape_fill_id` | Zero, invalid |
| Weights | Same fixed observational weights as `CostBreakdown`, valid |
| `failsafe` | False placeholder, invalid because no supervisor owns failsafe yet |
| `run_id` | Empty, invalid until run metadata exists |

## `AlgorithmEvent`

`value_names[]` and `values[]` always have equal lengths. Every numeric value
included in the pair is finite. `reason_code` is zero for non-error events;
fill rejections use stable local codes documented by their `detail` string.

Phase 01 emits:

- `EVENT_CONFIGURATION` for the effective source, weight, convergence, and
  Gaussian settings;
- `EVENT_CAPABILITY_UNAVAILABLE` for current raw-sensor, filtered-sensor, and
  source-score gaps;
- `EVENT_CONVERGENCE_CANDIDATE` at the existing candidate log site;
- `EVENT_CONVERGENCE_CONFIRMED` after the legacy fill-ready event;
- `EVENT_FILL_CREATED` after the exact legacy `/cost_bias` publication;
- `EVENT_FILL_REJECTED` at existing rejection paths and bounded silent policy
  gates.

Goal, escape, recenter, timeout, and failsafe constants are reserved for later
phases and are not emitted in Phase 01. Event state fields remain explicitly
unavailable until the supervisor exists.

## Legacy compatibility mapping

| Legacy topic | Preserved type/layout | Typed relationship |
|---|---|---|
| `/turtlebot3/cost_value_chatter` | `StampedFloat64MultiArray`, raw minimization cost | `CostBreakdown.raw_cost` |
| `/cost_modified` | Same type and input timestamp, raw plus Gaussian plus affine | `CostBreakdown.augmented_cost` |
| `/cost_bias` | `[amplitude, center_x, center_y, sigma]` | `GaussianFill` record |
| `/turtlebot3/filter_value_chatter` | Two-value GESC output | `GescDiagnostics.filter_output` |
| `/turtlebot3/control_value_chatter` | Saturated six-value command | `ControlDiagnostics.final_command` |
| `/cmd_vel` | Saturated `geometry_msgs/msg/Twist` | Same final command |
| `/convergence_event` | Existing eight-value fill-ready event | `AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED` |
| `/odom` | `nav_msgs/msg/Odometry` | Canonical simulation pose/velocity feedback; physical mapping remains Phase 09 |
| `/tf`, `/tf_static` | Standard TF topics | Unchanged |

No legacy topic, queue depth, array order, timestamp, cost sign, unit, command
limit, or default launch behavior changes in Phase 01.

## Launch and parameter reference

The central launch adds these arguments:

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

`cost_function_node`, `filter_node`, and `controller_node` receive the
settings as optional CLI arguments. `modified_cost_node`,
`convergence_detector_node`, and `gaussian_fill_node` receive equivalent ROS
parameters. The PDE and non-PDE cost executables are mutually exclusive so
only the selected final owner publishes cost breakdown and algorithm state.

## Simulation and physical mapping boundary

The typed topic names and message definitions are platform independent.
Current Gazebo owners populate them with `source_mode=SOURCE_SIMULATION`.
`SOURCE_PHYSICAL` is selectable for a future audited adapter without changing
the shared filter, controller, fill, state, or event interfaces. Phase 01 does
not guess a photoresistor, Vicon, physical launch, calibration, room-boundary,
or collision topic; those remain unavailable until the Phase 09 inventory.
