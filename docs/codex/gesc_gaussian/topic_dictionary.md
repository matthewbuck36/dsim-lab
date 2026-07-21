# GESC Gaussian Topic and Message Dictionary

This dictionary is the resolved Phase 02 interface contract for the current
`dsim-lab` checkout. `algorithm_profile=legacy` remains the default and keeps
the Phase 01/numerical legacy path. `robust_gaussian_v1` enables the explicit
supervisor, state-weighted cost composition, model-normalized simulation
source score, and command watchdog.

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

All new publishers use queue depth 10. The robust supervisor and command
watchdog publish at their configured rates; the other typed publishers remain
sample-driven.

## Canonical typed topics

| Topic | Message | Owner | Publication rate |
|---|---|---|---|
| `/gesc_gaussian/cost_breakdown` | `ros_esc_interfaces/msg/CostBreakdown` | Legacy final cost owner; `modified_cost_2d` in robust mode | Once per accepted raw-cost sample |
| `/gesc_gaussian/gesc_diagnostics` | `ros_esc_interfaces/msg/GescDiagnostics` | `custom_filter` | Once per legacy filter output |
| `/gesc_gaussian/control_diagnostics` | `ros_esc_interfaces/msg/ControlDiagnostics` | `custom_controller` | Once per legacy command output |
| `/gesc_gaussian/gaussian_fills` | `ros_esc_interfaces/msg/GaussianFill` | `gaussian_fill` | Once per accepted fill |
| `/gesc_gaussian/algorithm_state` | `ros_esc_interfaces/msg/AlgorithmState` | Legacy final cost owner, or robust supervisor | Sample-driven legacy placeholder; timer/transition-driven robust state |
| `/gesc_gaussian/algorithm_events` | `ros_esc_interfaces/msg/AlgorithmEvent` | Source, modified-cost, convergence, and fill owners | At the corresponding configuration, convergence, fill-created, or fill-rejected site |
| `/gesc_gaussian/source_cost` | `ros_esc_interfaces/msg/CostBreakdown` | `cost_function` | Each robust raw-cost sample, synchronized with model-normalized source score |
| `/gesc_gaussian/convergence_status` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `convergence_detector` | Every valid post-startup convergence evaluation |
| `/gesc_gaussian/fill_requests` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | supervisor | Once on each entry to fill design |
| `/gesc_gaussian/supervisor_command` | `geometry_msgs/msg/Twist` | supervisor | Configured supervisor rate; always zero in Phase 02 |
| `/gesc_gaussian/stop_requested` | `std_msgs/msg/Bool` | experiment operator/runner | `True` latches `FAILSAFE`; `False` is ignored |

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
| `source_score[]` | Compatible simulated photoresistor model endpoints | Dimensionless `[0,1]` model-range score | Valid in robust photoresistor profiles; otherwise invalid, `NaN` |
| `gaussian_cost[]` | Existing Gaussian term evaluation | Cost units | Valid; zero when no fill contributes |
| `affine_cost[]` | Existing decaying affine evaluation | Cost units | Valid; zero when disabled or inactive |
| `augmented_cost[]` | Legacy raw or `/cost_modified` result | Cost units | Valid when finite |
| `sensor_weight` | Profile/state policy | Dimensionless | Explicit and valid |
| `gaussian_weight` | Profile/state policy | Dimensionless | Explicit and valid |
| `affine_weight` | Profile/state policy | Dimensionless | Explicit and valid |

In legacy PDE mode the identity remains:

```text
augmented_cost = raw_cost + gaussian_cost + affine_cost
```

In `robust_gaussian_v1` the published identity is:

```text
augmented_cost = sensor_weight * raw_cost
               + gaussian_weight * gaussian_cost
               + affine_weight * affine_cost
```

All unweighted components are evaluated and published once even when their
weight is zero. The raw source owner continues sampling and publishing on both
the legacy raw topic and `/gesc_gaussian/source_cost` while
`sensor_weight=0`.

The simulation score is
`clip((raw_cost-dark_cost)/(near_cost-dark_cost), 0, 1)` using the existing
photoresistor resistance limits (`337260 ohm` dark and `100 ohm` near). It is
computed after the configured noise object. This is a model-range score, not
lux calibration and not a source-ground-truth position test. With multiple
channels, the supervisor verifies the maximum finite channel score.

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
| `supervisor_contribution[6]` | Invalid in legacy; received/cancelling robust contribution in Phase 02 |
| `combined_command_unsaturated[6]` | Legacy GESC command, or robust state-authorized combination before one final saturation |
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

Legacy continues subscribing directly to `/convergence_event` and preserves
its publication behavior. Robust mode subscribes to
`/gesc_gaussian/fill_requests`; an accepted typed `GaussianFill` or rejected
`AlgorithmEvent` carries the request's exact `source_timestamp`. The accepted
legacy `/cost_bias` payload is still published unchanged for the existing
modified-cost owner.

## `AlgorithmState`

Legacy keeps the Phase 01 unavailable-state placeholder. In
`robust_gaussian_v1`, `gesc_gaussian_supervisor` is the sole state owner and
publishes at `supervisor_publish_rate_hz` plus immediately after transitions.

| State | Weights `(raw, Gaussian, affine)` | Final-command policy |
|---|---:|---|
| `SEARCH` | `(1,1,0)` | GESC plus supervisor contribution |
| `VERIFY_EXTREMUM` | `(1,1,0)` | Zero |
| `DESIGN_OR_MERGE_FILL` | `(0,1,0)` | Zero |
| `ESCAPE_REPULSE` | `(0,1,0)` | GESC plus supervisor contribution |
| `ESCAPE_ASSIST` | `(0,1,1)` | GESC plus supervisor contribution |
| `RECENTER` | `(0,1,0)` | Supervisor-only; Phase 02 publishes zero |
| `GOAL_HOLD` | `(0,1,0)` | Zero, latched |
| `FAILSAFE` | `(0,0,0)` | Zero, latched |

The supervisor uses local ROS receipt time for freshness, carries a per-process
`run_id`, reports previous/current state and transition reason, and correlates
fill results to the one in-flight request by exact legacy source timestamp.
Stable-exit, stall, and recenter-complete inputs exist only in the pure state
machine in Phase 02; no timer or guessed geometry synthesizes success.

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

Phase 02 adds `EVENT_STATE_TRANSITION=3` and emits transition, goal, escape,
recenter-interface, timeout, and failsafe events from the supervisor. The
controller emits `EVENT_FAILSAFE` for watchdog faults; the supervisor consumes
that event and latches the global failsafe.

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
limit, or default launch behavior changes in Phase 02.

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
| `algorithm_profile` | `legacy` |
| `supervisor_publish_rate_hz` | `20.0` |
| `startup_timeout_sec` | `5.0` |
| `convergence_hold_sec` | `2.0` |
| `goal_score_threshold` | `0.95` |
| `goal_hold_sec` | `3.0` |
| `undesired_score_hold_sec` | `3.0` |
| `verification_max_sec` | `10.0` |
| `fill_design_timeout_sec` | `5.0` |
| `escape_max_sec` | `20.0` |
| `recenter_after_escape` | `True` |
| `recenter_max_sec` | `30.0` |
| `stale_pose_sec` | `0.50` |
| `stale_sensor_sec` | `0.50` |
| `supervisor_state_stale_sec` | `0.50` |
| `supervisor_command_stale_sec` | `0.50` |
| `command_watchdog_rate_hz` | `20.0` |
| `zero_command_on_shutdown` | `True` |
| `source_cost_topic` | `/gesc_gaussian/source_cost` |
| `convergence_status_topic` | `/gesc_gaussian/convergence_status` |
| `fill_request_topic` | `/gesc_gaussian/fill_requests` |
| `supervisor_command_topic` | `/gesc_gaussian/supervisor_command` |
| `supervisor_stop_topic` | `/gesc_gaussian/stop_requested` |

`cost_function_node`, `filter_node`, and `controller_node` receive the
settings as optional CLI arguments. `modified_cost_node`,
`convergence_detector_node`, and `gaussian_fill_node` receive equivalent ROS
parameters. The PDE and non-PDE cost executables remain mutually exclusive.
The supervisor is launched only for `robust_gaussian_v1`; legacy cost owners
retain the placeholder state, so there is one state owner and one `/cmd_vel`
owner in each profile. Robust observability is mandatory even when the legacy
`enable_observability` flag is false.

## Simulation and physical mapping boundary

The typed topic names and message definitions are platform independent.
Current Gazebo owners populate them with `source_mode=SOURCE_SIMULATION`.
`SOURCE_PHYSICAL` is selectable for a future audited adapter without changing
the shared filter, controller, fill, state, or event interfaces. Phase 01 does
not guess a photoresistor, Vicon, physical launch, calibration, room-boundary,
or collision topic; those remain unavailable until the Phase 09 inventory.
