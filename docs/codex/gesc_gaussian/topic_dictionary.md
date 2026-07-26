# GESC Gaussian Topic and Message Dictionary

> Phases 01-07.5 are implemented. Phase 04 passed its amended focused and visible
> Gazebo/SIGINT gates, Phase 05 produced a complete retained sqlite3 run, and
> Phase 06 composes the same launch/recording owners in a deterministic serial
> scenario runner. These results establish implementation and recording
> readiness only; they do not establish the Phase 08 simulation-robustness
> acceptance claim.

This dictionary is the resolved Phase 05 interface contract for the current
`dsim-lab` checkout. `algorithm_profile=legacy` remains the default and keeps
the numerical legacy path. `robust_gaussian_v1` enables the explicit
supervisor, state-weighted cost composition, model-normalized simulation
source score, robust synchronized basin estimation, adaptive anisotropic fill
design, and revision-aware typed fill consumption.
Phase 04 adds measured radial escape, one targeted stall redesign,
boundary-aware assisted direction, and bounded indoor recentering. Phase 05
adds the default-off recording interlock and the unified recorder contract.
Phase 06 adds no algorithm topic or message; it adds only simulation
orchestration, Gazebo execution arguments, and per-run metadata.
Phase 07.5 adds default-off, simulation-only contact and delay evidence needed
to make Phase 08 validation dimensions executable.

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
| `/gesc_gaussian/gaussian_fills` | `ros_esc_interfaces/msg/GaussianFill` | `gaussian_fill` | Once per new fill; superseded then active records on a merge revision |
| `/gesc_gaussian/algorithm_state` | `ros_esc_interfaces/msg/AlgorithmState` | Legacy final cost owner, or robust supervisor | Sample-driven legacy placeholder; timer/transition-driven robust state |
| `/gesc_gaussian/algorithm_events` | `ros_esc_interfaces/msg/AlgorithmEvent` | Source, modified-cost, convergence, and fill owners | At the corresponding configuration, convergence, fill-created, or fill-rejected site |
| `/gesc_gaussian/source_cost` | `ros_esc_interfaces/msg/CostBreakdown` | `cost_function` | Each opt-in simulation-observability raw-cost sample; robust photoresistor profiles also carry model-normalized source score |
| `/gesc_gaussian/convergence_status` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `convergence_detector` | Every valid post-startup convergence evaluation |
| `/gesc_gaussian/fill_requests` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | supervisor | Once on each entry to fill design |
| `/gesc_gaussian/supervisor_command` | `geometry_msgs/msg/Twist` | supervisor | Configured supervisor rate; nonzero only for bounded `RECENTER` |
| `/gesc_gaussian/stop_requested` | `std_msgs/msg/Bool` | experiment operator/runner | `True` latches `FAILSAFE`; `False` is ignored |

The two cost owners are mutually exclusive in `gazebo.launch.xml`. Multiple
event publishers are intentional because each existing node retains ownership
of the event it detects.

For `robust_gaussian_v1`, the detector's typed
`EVENT_CONVERGENCE_CONFIRMED` event is the sole activation input that moves
the supervisor from `SEARCH` to `VERIFY_EXTREMUM`. The continuous
`/gesc_gaussian/convergence_status` stream remains diagnostic and cannot
activate the supervisor by itself. Confirmed events contain the same canonical
eight values as `CONVERGED_FILL_READY`; the supervisor can also reconstruct
that snapshot from the matching historical six-value typed event plus its
same-timestamp status sample for v1 replay only.

Goal verification uses the minimum of the maximum source score observed in
each of `goal_score_required_rotations` complete
`goal_score_rotation_period_sec` windows. Incomplete rotation evidence waits
within the existing bounded verification timeout. An observed invalid score
still fails safe.

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
| `supervisor_contribution[6]` | Invalid in legacy; robust supervisor contribution before final arbitration |
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

The topic is the authoritative registry stream in `robust_gaussian_v1`.
`cluster_id` is the stable basin identity; `fill_id` identifies one immutable
published version; and `revision` increases within a cluster. A merge publishes
the old version once as `active=false, superseded=true`, then publishes the
replacement as active. Consumers reject stale/out-of-order records and retain
only one active version per cluster.

| Field | Robust meaning | Units/validity |
|---|---|---|
| `frame_id` | `odom` in the current simulation adapter | Frame name |
| `fill_id` | Globally monotonic concrete-version ID | Valid |
| `cluster_id` | Stable basin identity | Valid |
| `revision` | One-based version within the cluster | Valid |
| `center_x`, `center_y` | Kernel/cost-weighted basin center | Meters |
| `amplitude` | Maximum of minimum, depth, and curvature requirements after bounded escalation | Existing raw-cost units |
| `covariance_xx`, `covariance_xy`, `covariance_yy` | Anisotropic fill covariance | Square meters, valid |
| `sigma_major`, `sigma_minor`, `orientation` | Canonical principal geometry | Meters, meters, radians |
| `support_radius` | `support_sigma * sigma_major` | Meters, valid |
| `exit_radius` | `exit_sigma * sigma_major` | Meters, valid and frozen for the revision |
| `confidence` | Mean of count, coverage, condition, residual, cap-use, and validation scores | Dimensionless `[0,1]`, valid |
| `sample_count` | Valid retained samples used for the estimate | Valid |
| `fit_residual` | Weighted quadratic-fit RMS | Raw-cost units, valid when finite |
| `fit_condition_number` | Unregularized weighted-design condition | Valid only when finite |
| `design_escalations` | Completed bounded escalation rounds | Valid |
| `active`, `superseded` | Lifecycle state of this immutable version | Valid |

The robust owner pairs `/odom` and `/gesc_gaussian/source_cost` one-to-one by
absolute ROS stamp within `sample_sync_tolerance_sec`. The cost stamp becomes
the sample stamp. Request-time windows are duration-based and include pose,
yaw, raw sensor validity/value, raw cost, source score, and controller mode.
Invalid/stale/regressed/jump samples and MAD outliers are rejected before the
minimum-sample gate. The robust estimator never uses the independently updated
legacy `/pde_history` and `/pde_cost_history` buffers.

Center weighting uses a log-sum-exp-normalized spatial/cost kernel. Covariance
is symmetrized and eigenvalue-clipped; the local quadratic records condition,
rank, and residual; basin depth comes from center/shoulder percentiles. Width
is deliberately expanded from the sample covariance, and amplitude scales
with both depth and width-coupled positive curvature. A 41-by-41 principal-axis
grid must contain no 8-neighbor interior minimum inside the exit support.
Amplitude and width escalation are bounded; failure publishes
`EVENT_FILL_DESIGN_FAILED` and leaves the registry unchanged.

Soft association alone cannot force a merge: the probability threshold and
the sigma-scaled hard-overlap radius must both pass. A merge combines retained
sample windows, deterministically de-duplicates/caps them, re-estimates the
basin, and commits one replacement only after validation. Published fill
versions and the registry history are immutable.

Targeted stall redesign requests use the header
`ROBUST_FILL_REDESIGN:<active_fill_id>` while retaining the existing request
timestamp and eight numeric fields. The fill owner resolves the target to its
current active cluster, requires the same hard-overlap gate, combines retained
samples, and may commit only a revision of that cluster. `ROBUST_FILL_CREATE`
marks an ordinary robust request; unknown older headers remain ordinary create
requests.

Legacy behavior remains separate: legacy still uses the original isotropic
least-squares path and the legacy modified-cost owner still consumes
`/cost_bias`. Robust modified cost consumes only `GaussianFill`, evaluates
`A*exp(-0.5*delta^T*Sigma^-1*delta)`, and replaces Gaussian cluster terms on
revision. Robust affine terms are created only in `ESCAPE_ASSIST` from the
supervisor's safe world-frame direction. One direction revision is applied
once, so the 20 Hz state stream does not reset affine decay. Legacy
fill-triggered history/odometry affine construction is unchanged.
`/cost_bias` remains exactly
`[amplitude, center_x, center_y, sigma]`; robust publishes `sigma_major` as a
lossy compatibility projection, so that topic is not authoritative and cannot
retract a superseded revision.

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
| `RECENTER` | `(0,1,0)` | Supervisor-only bounded center-return command |
| `GOAL_HOLD` | `(0,1,0)` | Zero, latched |
| `FAILSAFE` | `(0,0,0)` | Zero, latched |

The supervisor uses local ROS receipt time for freshness, carries a per-process
`run_id`, reports previous/current state and transition reason, and correlates
fill results to the one in-flight request by exact legacy source timestamp.
Phase 03 derives `active_fill_count` from unique active typed clusters, not
fill publications, and an accepted revision becomes `active_escape_fill_id`.
Supersession tombstones are lifecycle updates and are never treated as a
design rejection.

Phase 04 adds these `AlgorithmState` fields. Legacy publishers set all floats
to `NaN`, revisions to zero, and validity flags false.

| Field group | Meaning |
|---|---|
| `escape_center_x`, `escape_center_y`, `escape_exit_radius`, `escape_geometry_valid` | Initial accepted fill geometry, frozen through repulse, redesign, assist, and recenter |
| `radial_distance`, `radial_distance_valid` | `norm(position - frozen_center)` in meters |
| `radial_progress`, `radial_progress_valid` | Current distance minus linearly interpolated distance exactly `stall_window_sec` earlier |
| `escape_exit_hold_elapsed_sec`, validity | Uninterrupted time beyond the strict exit radius with nonnegative valid progress |
| `escape_stalled`, `escape_stalled_valid` | Valid complete-window progress below `minimum_radial_progress_m`, suppressed during a qualifying exit hold |
| `safe_direction_x`, `safe_direction_y`, `safe_direction_clearance_m`, validity | Selected world-frame unit direction and predicted look-ahead clearance |
| `safe_direction_revision`, validity | Increments only when a selected assisted/recenter direction changes |
| `recenter_target_x`, `recenter_target_y`, validity | Configured room center in meters |
| `recenter_distance`, validity | Current Euclidean distance to the recenter target in meters |

The initial escape uses pure Gaussian repulsion. A stall emits one event and
one targeted fill redesign request; an accepted replacement enters
`ESCAPE_ASSIST` without changing the frozen center, exit radius, or shared
escape deadline. Stable exit requires `distance > exit_radius`, valid
nonnegative progress, and the configured uninterrupted hold. Bounded mode
then enters `RECENTER`; unbounded mode returns directly to `SEARCH`.

Safe direction candidates are evaluated in deterministic rotation order
`0,+step,-step,+2*step,-2*step,+3*step,-3*step,pi`. Candidates pointing away
from the preferred half-plane, leaving the wall-margin inset, moving inward
while already inside a fill avoidance circle, or entering another fill circle
are rejected. Remaining candidates maximize predicted clearance, alignment,
then minimum rotation with positive-before-negative tie-breaking. Fill
avoidance radius is `support_radius + fill_avoidance_margin_m`.

In bounded mode the preferred direction is toward the configured room center;
in unbounded assisted escape it is opposite the frozen recent approach, with
outward radial fallback. `RECENTER` uses a bounded differential-drive command,
rotates in place for large heading error, and holds zero inside the center
tolerance. All retained fills remain active in the Gaussian cost and in the
direction selector.

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

Phase 03 adds:

- `EVENT_FILL_MERGED=22` for an accepted replacement revision;
- `EVENT_FILL_SUPERSEDED=23` for the frozen inactive prior version;
- `EVENT_FILL_DESIGN_ESCALATED=24` with amplitude/width step counts;
- `EVENT_FILL_DESIGN_FAILED=25` when bounded grid validation fails;
- `EVENT_FILL_LOW_CONFIDENCE=26` when an accepted fill is below threshold.

Robust design events publish finite paired diagnostics for sample/rejection
counts, center/covariance, depth/curvature, fit validity/residual/condition,
residual minima, escalation, six confidence components, association,
identity, revision, and supersession.

Phase 04 emits:

- `EVENT_ESCAPE_STARTED` with frozen fill ID, center, exit radius, and approach;
- exactly one `EVENT_ESCAPE_STALLED` per attempt with distance, progress,
  window, and threshold;
- `EVENT_RECENTER_STARTED` with target and retained-fill count;
- `EVENT_RECENTER_COMPLETE` after the uninterrupted tolerance dwell;
- `EVENT_CONFIGURATION` with effective bounds, progress/direction settings,
  recenter gains, and command caps;
- existing timeout/failsafe events for stale/invalid input, bounds violation,
  no safe candidate, state timeout, exception, explicit stop, and watchdog
  faults.

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
limit, or direct-launch default changes in Phase 06.

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
| `goal_score_rotation_period_sec` | `3.0` |
| `goal_score_required_rotations` | `2` |
| `goal_hold_sec` | `3.0` |
| `undesired_score_hold_sec` | `3.0` |
| `verification_max_sec` | `10.0` |
| `fill_design_timeout_sec` | `5.0` |
| `escape_max_sec` | `20.0` |
| `escape_exit_hold_sec` | `1.0` |
| `stall_window_sec` | `3.0` |
| `minimum_radial_progress_m` | `0.05` |
| `approach_history_window_sec` | `3.0` |
| `recenter_after_escape` | `True` |
| `recenter_max_sec` | `30.0` |
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
| `recording_ready_required` | `False` |
| `recording_ready_topic` | `/gesc_gaussian/recording_ready` |
| `recording_ready_stale_sec` | `0.50` |
| `supervisor_use_sim_time` | `True` |
| `gazebo_gui` | `True` |
| `gazebo_use_random_seed` | `False` |
| `gazebo_random_seed` | `0` |

The three Gazebo execution arguments are additive. Direct launches remain
visible and use Gazebo's prior unseeded behavior. `run_scenario` passes
`gazebo_gui=False`, `gazebo_use_random_seed=True`, and the resolved explicit
seed unless `--gui` is requested.

Phase 03 adds these robust-fill launch arguments; each maps to the node
parameter obtained by removing the `gaussian_fill_` prefix:

| Launch argument | Default |
|---|---:|
| `gaussian_fill_pose_topic` | `/odom` |
| `gaussian_fill_estimation_channel_index` | `0` |
| `gaussian_fill_sample_sync_tolerance_sec` | `0.05` |
| `gaussian_fill_maximum_position_speed_mps` | `0.20` |
| `gaussian_fill_outlier_mad_threshold` | `3.5` |
| `gaussian_fill_maximum_cluster_samples` | `4000` |
| `gaussian_fill_estimation_window_sec` | `8.0` |
| `gaussian_fill_minimum_valid_samples` | `40` |
| `gaussian_fill_maximum_sample_age_sec` | `12.0` |
| `gaussian_fill_mean_shift_iterations` | `5` |
| `gaussian_fill_center_tolerance_m` | `0.005` |
| `gaussian_fill_position_kernel_bandwidth_m` | `0.25` |
| `gaussian_fill_cost_temperature_normalized` | `0.05` |
| `gaussian_fill_covariance_eigenvalue_min_m2` | `0.0025` |
| `gaussian_fill_covariance_eigenvalue_max_m2` | `0.25` |
| `gaussian_fill_quadratic_ridge_lambda` | `1e-6` |
| `gaussian_fill_quadratic_condition_number_max` | `1e8` |
| `gaussian_fill_center_cost_percentile` | `10.0` |
| `gaussian_fill_shoulder_cost_percentile` | `80.0` |
| `gaussian_fill_inner_mahalanobis_radius` | `1.0` |
| `gaussian_fill_minimum_basin_depth` | `0.02` |
| `gaussian_fill_covariance_scale` | `2.5` |
| `gaussian_fill_sigma_floor_m` | `0.15` |
| `gaussian_fill_sigma_ceiling_m` | `1.25` |
| `gaussian_fill_amplitude_depth_scale` | `1.5` |
| `gaussian_fill_amplitude_curvature_scale` | `1.2` |
| `gaussian_fill_amplitude_min` | `0.10` |
| `gaussian_fill_amplitude_max` | `3.00` |
| `gaussian_fill_validation_grid_points_per_axis` | `41` |
| `gaussian_fill_validation_support_sigma` | `3.0` |
| `gaussian_fill_maximum_design_escalations` | `5` |
| `gaussian_fill_amplitude_escalation_factor` | `1.5` |
| `gaussian_fill_width_escalation_factor` | `1.25` |
| `gaussian_fill_grid_minimum_tolerance` | `1e-9` |
| `gaussian_fill_support_sigma` | `3.0` |
| `gaussian_fill_exit_sigma` | `2.5` |
| `gaussian_fill_merge_bandwidth_m` | `0.50` |
| `gaussian_fill_merge_radius_scale` | `2.0` |
| `gaussian_fill_minimum_merge_probability` | `0.60` |
| `gaussian_fill_low_confidence_threshold` | `0.60` |

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
the shared filter, controller, fill, state, or event interfaces. Phase 03 does
not guess a photoresistor, Vicon, physical launch, calibration, room-boundary,
or collision topic; those remain unavailable until the Phase 09 inventory.
The Phase 04 bounds are a configured virtual operating envelope. The audited
Gazebo world has no inferred walls/contact owner, so passing these checks is
not a physical collision-safety claim. Setting `recenter_after_escape=False`
selects the unbounded robust path and bypasses bounds and recentering.

## Phase 05 recording interface

`/gesc_gaussian/recording_ready` uses `std_msgs/msg/Bool` and is owned by the
single `record_run` process. It is a reliable 10 Hz heartbeat. The recorder
publishes false during preflight and shutdown and true only after all required
publishers, exact types, the `/custom_controller` interlock subscription, the
rosbag subscriptions, and a gated zero `/cmd_vel` have been observed.
Every required topic except the intentionally shared algorithm-event bus and
the two-owner simulation `/joint_states` stream also requires exactly one live
publisher endpoint. This prevents an orphaned prior launch from contaminating
a new experiment even when the orphan reused the same ROS node name.

The controller's three recording arguments are default-off. When
`recording_ready_required=False`, no readiness subscription is created and
the existing controller path is unchanged. When true, a missing, false, or
older-than-`recording_ready_stale_sec` heartbeat forces all final command
representations to zero. The gate adds no second saturation or `/cmd_vel`
owner.

The authoritative required/optional topic list, exact types, applicable
modes, minimum counts, and semantic policies are installed from
`ros_esc/experiment_recording/topic_manifest.yaml`. Simulation and physical
modes use this same manifest and runner; Phase 05 does not invent the absent
physical adapter or claim physical calibration. Full operator instructions
are in `docs/codex/gesc_gaussian/recording_runs.md`.

## Phase 06 scenario runner interface

`ros2 run ros_esc run_scenario SCENARIO_YAML --operator OPERATOR` is a
non-ROS, simulation-only orchestration process. It owns no algorithm state,
topic, recorder, validator, launch graph, or physical adapter. It expands
schema-version-1 YAML serially and invokes the existing
`ros2 run ros_esc record_run ... -- ros2 launch
turtlebot3_rotating_sensor gazebo.launch.xml ...` command.

The scenario seed is shared by Gazebo, supported Uniform noise, metadata, and
the deterministic case key. Run IDs additionally contain a UTC timestamp and
UUID fragment so reruns never overwrite an artifact. Ground-truth source roles
and tolerances remain evaluation metadata and are never exposed to the
controller. See `recording_runs.md` for commands and retained artifacts.

## Phase 07.5 simulation-validation interface

Schema version 2 preserves schema-version-1 parsing and case identities while
adding a validation world, deterministic Gaussian noise, delayed algorithm
inputs, contact truth, and per-run frozen-profile overrides. These controls are
simulation-only and default off in direct launches.

| Topic | Type | Owner |
|---|---|---|
| `/gesc_gaussian/simulation/raw_cost_delayed` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | simulation disturbance relay |
| `/gesc_gaussian/simulation/source_cost_delayed` | `ros_esc_interfaces/msg/CostBreakdown` | simulation disturbance relay |
| `/gesc_gaussian/simulation/pose_delayed` | `nav_msgs/msg/Odometry` | simulation disturbance relay |
| `/gesc_gaussian/simulation/contacts` | `gazebo_msgs/msg/ContactsState` | opt-in Gazebo contact sensors |

The delay relay retains the original message timestamps and releases messages
against ROS simulation time. Algorithm consumers alone are routed to delayed
topics; canonical publishers and recordings remain unchanged. The Phase 07
analyzer pairs retained timestamps to report observed raw-cost, source-cost,
and pose delay. Contact metrics are valid only when the opt-in Gazebo contact
stream is present; valid empty messages mean no collision, and non-ground
contact states mean a collision.

The validation robot monitors the exact collision names produced by Gazebo's
fixed-joint lumping. The four-wall validation world bounds the declared
`[-2, 2] x [-2, 2] m` simulation envelope. A positive-control probe spawns a
static collision object only after recording readiness, proving that the
contact path detects physical Gazebo contacts rather than synthetic messages.

## Phase 08 offline validation interface

`validate_robustness` sequences the existing scenario runner, recorder,
validator, and analyzer. It does not own an algorithm topic or launch graph:

```text
ros2 run ros_esc validate_robustness <subcommand>
  --operator OPERATOR
  --evidence-root PATH
```

The historical v1 interface remains readable through `sweep`, `freeze`,
`holdout`, `full-pass`, and `report`, with `--pass-index 1|2|3` for
`full-pass`. Its fixed arithmetic was 9 candidates x 9 training runs = 81, 12
holdouts, and 519 runs per full pass. The command recognizes an existing v1
workflow state only to retain reporting compatibility. Do not execute or
resume it for a new acceptance claim.

The installed v2 interface is `activation`,
`sweep`, `freeze`, `holdout`, `validation`, `reproducibility`, and `report`.
It uses workflow schema version 2 and a separate evidence root. Its arithmetic
is 10 activation + 30 tuning + 20 new hidden holdout + 50 additional unique
validation + 10 targeted repeats = 120 declared runs. Holdout plus additional
validation form the 70-run unique acceptance denominator; repeats remain
separate.

The v2 command refuses mixed v1/v2 evidence and out-of-order execution.
Holdout, validation, and reproducibility require a clean committed freeze and
compare the exact commit/tree, frozen profile, and input hashes. Before
activation it seals scenario hashes and the declared case identities,
including the selection-blind holdout, without importing any historical v1
run path or hash.

Only these launch overrides are candidates for the Phase 08 profile file:

| Override | Scope |
|---|---|
| `gaussian_fill_covariance_scale` | Gaussian design width factor |
| `gaussian_fill_amplitude_depth_scale` | basin-depth amplitude factor |
| `gaussian_fill_exit_sigma` | stable-exit geometry |
| `stall_window_sec` | escape stall observation window |
| `minimum_radial_progress_m` | minimum progress within the stall window |

The generated historical `phase08_frozen_parameters.yaml` is v1-only.
`phase08_v2_frozen_parameters.yaml` is generated only after v2 selection and
is applied only through the v2 validation harness. Neither changes a
direct-launch or legacy default.

## Phase 07 offline analysis interface

Phase 07 adds no ROS node, topic, message, parameter, launch argument, or
controller behavior. The existing plotting owner provides two offline console
commands:

```text
ros2 run ros_esc analyze_run RUN_DIRECTORY
  [--output-dir PATH]
  [--channel-index N]
  [--sync-tolerance-sec SEC]

ros2 run ros_esc summarize_matrix INPUT [...]
  --output-dir PATH
```

`analyze_run` reads the run-specific `resolved_topics.yaml`, sqlite3 bag, real
generated message types, metadata, resolved parameters, stored completeness,
and a fresh non-mutating Phase 05 validation result. Defaults are:

| Option | Default and precedence |
|---|---|
| `--output-dir` | `<RUN_DIRECTORY>/analysis/phase07` |
| `--channel-index` | captured `estimation_channel_index`, else `0` with warning |
| `--sync-tolerance-sec` | captured `sample_sync_tolerance_sec`, else `0.05` with warning |

The synchronized CSV uses `/gesc_gaussian/cost_breakdown` as its anchor.
Source cost, GESC diagnostics, pose, and control diagnostics use nearest
absolute typed/header ROS time within the explicit tolerance. Algorithm state
uses the latest causal sample within the same tolerance. No critical numeric
data is interpolated, extrapolated, or forward-filled. Every raw table retains
the original bag timestamp, typed/header ROS timestamp when available, legacy
source timestamp and validity, readiness membership, and motion-relative
time.

The command writes eleven CSV tables, eight separate PNG figures,
`summary_metrics.json`, `summary_metrics.csv`, and
`analysis_completeness.json`. Metrics use the statuses `valid`,
`not_applicable`, `unavailable`, and `invalid`, each with an explicit value,
unit, reason, and provenance. Missing behavior is not silently converted to
zero. A readable failed run is analyzed as first-class partial or invalid
evidence; analysis-process failure alone returns exit code 2.

`summarize_matrix` aggregates existing per-run `summary_metrics.json` files
into `matrix_summary.csv` and `matrix_summary.json`. Both commands reject
existing output directories. They never modify raw bags, root metadata,
`completeness.json`, per-run summaries, or Phase 05 validation results.
