# GESC Gaussian Interface Map

This file maps the Phase 00 logical architecture to the exact public and
internal ROS interfaces in the current checkout.

## Interface conventions

- Legacy repository timestamps are `float64` seconds, not
  `builtin_interfaces/Time`.
- Most legacy `ros_esc` topics use queue depth 10.
- `/turtlebot3/timekeeper_chatter` uses queue depth 150.
- Topic names passed without a leading slash in `gazebo.launch.xml` resolve at
  the root namespace in the current launch, for example
  `turtlebot3/cost_value_chatter` resolves to
  `/turtlebot3/cost_value_chatter`.
- Legacy arrays rely on positional layouts. Phase 01 must retain them and add
  typed diagnostics in parallel.
- All PDE/Gaussian nodes force `use_sim_time=true`.

## Custom message definitions

| Type | Exact definition | Layout |
|---|---|---|
| `ros_esc_interfaces/msg/Timekeeper` | `ros2_ws/src/ros_esc_interfaces/msg/Timekeeper.msg` | `mode`, `start_time` |
| `ros_esc_interfaces/msg/StampedFloat64` | `ros2_ws/src/ros_esc_interfaces/msg/StampedFloat64.msg` | `header`, `timestamp`, `data` |
| `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `ros2_ws/src/ros_esc_interfaces/msg/StampedFloat64MultiArray.msg` | `header`, `timestamp`, `data[]` |
| `ros_esc_interfaces/msg/StampedString` | `ros2_ws/src/ros_esc_interfaces/msg/StampedString.msg` | `header`, `timestamp`, `data` |
| `ros_esc_interfaces/msg/StampedTransformMultiArray` | `ros2_ws/src/ros_esc_interfaces/msg/StampedTransformMultiArray.msg` | `header`, `timestamp`, `geometry_msgs/Transform[] transform_array` |

## Active topic graph

The table describes the active
`gesc_gaussian_full_rotation_voltage.bash` profile. "Always" means always in
the central Gazebo launch; "PDE" means only when
`use_pde_extensions=True`.

| Topic | Message type | Publisher/owner | Subscriber/consumer | Condition and layout |
|---|---|---|---|---|
| `/clock` | `rosgraph_msgs/msg/Clock` | Gazebo | nodes using simulation time | Gazebo |
| `/robot_description` | `std_msgs/msg/String` | `robot_state_publisher_node` | Gazebo `spawn_entity.py` | Always |
| `/joint_states` | `sensor_msgs/msg/JointState` | Gazebo joint-state plugin/broadcaster | `encoder_node` | Always; joint `rotating_frame_joint` |
| `/velocity_controller/commands` | `std_msgs/msg/Float64MultiArray` | `rotate_arm` | `velocity_controller` | Always; `[rad_per_sec]` |
| `/turtlebot3/timekeeper_chatter` | `ros_esc_interfaces/msg/Timekeeper` | `rotate_arm` | encoder, pose, cost, filter, controller, collector | Always; `mode="sim time"` and simulation start seconds |
| `/turtlebot3/encoder_chatter` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `encoder_node` | rotate, pose, filter | Always; rotating-joint angles in radians |
| `/odom` | `nav_msgs/msg/Odometry` | Gazebo differential drive | pose, controller, PDE history, modified cost, collector, plotter | Always; world pose and measured twist |
| `/turtlebot3/sensor_transform_chatter` | `ros_esc_interfaces/msg/StampedTransformMultiArray` | `sensor_position_node` | cost, modified cost, collector | Always; one transform per sensor |
| `/turtlebot3/cost_value_chatter` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `cost_function` | filter in legacy mode; modified cost in PDE mode | Always; one minimization cost per sensor |
| `/pde_history` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `pde_history` | convergence, Gaussian fill, modified cost | PDE; `[x0,y0,x1,y1,...]`, newest first |
| `/cost_bias` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `gaussian_fill` | modified cost, cost-surface plotter | PDE; `[amplitude,center_x,center_y,sigma]` |
| `/cost_modified` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `modified_cost_2d` | filter, PDE cost history, collector | PDE; raw plus all Gaussian and affine contributions, one value per input channel |
| `/pde_cost_history` | `std_msgs/msg/Float64MultiArray` | `pde_cost_history` | Gaussian fill | PDE; `[J0,J1,...]`, newest first, unstamped |
| `/convergence_metric` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `convergence_detector` | diagnostics only | PDE; `[metric]` |
| `/convergence_r` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `convergence_detector` | diagnostics only | PDE; `[squared_mean_distance]` |
| `/convergence_count` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `convergence_detector` | diagnostics only | PDE; `[count_remaining]` |
| `/convergence_event` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `convergence_detector` | Gaussian fill | PDE; eight-element event layout below |
| `/turtlebot3/filter_value_chatter` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `custom_filter` | `custom_controller`, collector | Always; two signed GESC gradient/direction estimates |
| `/turtlebot3/control_value_chatter` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `custom_controller` | collector | Always; post-saturation `[vx,vy,vz,wx,wy,wz]` |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `custom_controller` | Gazebo differential drive | Always; post-saturation command |

## Positional array contracts

### `/convergence_event`

Type: `ros_esc_interfaces/msg/StampedFloat64MultiArray`

```text
data[0] = convergence metric
data[1] = squared mean displacement r
data[2] = exponential decay term
data[3] = recent mean x
data[4] = recent mean y
data[5] = old mean x
data[6] = old mean y
data[7] = convergence count remaining
```

Header: `CONVERGED_FILL_READY`.

### `/cost_bias`

Type: `ros_esc_interfaces/msg/StampedFloat64MultiArray`

```text
data[0] = amplitude
data[1] = center x, meters in odom frame
data[2] = center y, meters in odom frame
data[3] = isotropic sigma, meters
```

Header: `GaussianFill2D`.

### `/pde_history`

Type: `ros_esc_interfaces/msg/StampedFloat64MultiArray`

```text
data = [x0, y0, x1, y1, ..., xN-1, yN-1]
```

Index zero is newest. Positions are meters in the odometry frame.

### `/pde_cost_history`

Type: `std_msgs/msg/Float64MultiArray`

```text
data = [J0, J1, ..., JN-1]
```

Index zero is newest. This message has no timestamp.

### Filter and controller arrays

`/turtlebot3/filter_value_chatter` contains:

```text
[signed_x_gradient_estimate, signed_y_gradient_estimate]
```

`/turtlebot3/control_value_chatter` contains:

```text
[vx, vy, vz, wx, wy, wz]
```

The current GESC controller only produces nonzero `vx` and `wz`. Values are
already saturated.

## Executable argument interfaces

| Executable | Required positional arguments | Optional/parameterized inputs |
|---|---|---|
| `encoder_node` | joint-state topic, timekeeper topic, output topic | `--joint_names` |
| `rotate_frame_node` | encoder topic, timekeeper output topic, JSON path | JSON-selected spin profile |
| `sensor_pose_node` | odom topic, encoder topic, timekeeper topic, output topic, JSON path | none |
| `cost_function_node` | transform topic, timekeeper topic, output topic, JSON path | `--light_source_count`; five sets of x/y/intensity args |
| `filter_node` | input value topic, encoder topic, timekeeper topic, output topic | `--filter_file`, `--append_encoder_data` |
| `controller_node` | filter topic, state topic, timekeeper topic, diagnostic output topic, Twist output topic, JSON path | none |
| `modified_cost_node` | raw cost topic, fill topic, output topic | sensor-transform and odom topics; ROS parameters |
| `cost_surface_plotter` | cost JSON path | plot bounds, live topics, output, light settings |
| `data_collection_node` | output directory, five config paths, six topics, plot mode | none |

PDE history, convergence, and Gaussian-fill interfaces use ROS parameters
rather than positional topic arguments, except the hard-coded topic names
listed above.

## PDE/Gaussian ROS parameters

### `pde_history_node`

| Parameter | Default | Active wrapper |
|---|---:|---:|
| `n_buffer` | `2000` | default |
| `k_periods` | `20` | default |
| `omega` | `5.0` | `5.0` |
| `cfl` | `0.9` | default |

`/odom` and `/pde_history` are hard-coded.

### `pde_cost_history_node`

| Parameter | Default | Active wrapper |
|---|---:|---:|
| `n_buffer` | `2000` | default |
| `k_periods` | `20` | default |
| `omega` | `5.0` | `5.0` |
| `cfl` | `0.9` | default |
| `cost_topic` | `/turtlebot3/cost_value_chatter` | `/cost_modified` |

Output `/pde_cost_history` is hard-coded.

### `convergence_detector_node`

| Parameter | Default | Active wrapper |
|---|---:|---:|
| `k_periods` | `20` | default |
| `threshold` | `0.1` | `0.2` |
| `decay_rate` | `0.15` | `0.15` |
| `n_buffer` | `2000` | default |
| `omega` | `5.0` | `5.0` |
| `min_fill_periods` | `1.0` | `2.0` |
| `convergence_count_start` | `3` | default |
| `reset_counter_after_event` | `True` | default |

Input `/pde_history` and the four convergence outputs are hard-coded.

### `gaussian_fill_node`

| Parameter | Node default | Launch default | Active wrapper |
|---|---:|---:|---:|
| `escape_policy` | `conditional_gaussian_fill` | same | same |
| `amplitude` | `5.0` | `5.0` | `0.20` |
| `min_sigma` | `0.10` | `3.16` | `0.25` |
| `max_sigma` | `5.0` | `5.0` | `0.55` |
| `min_points` | `50` | `50` | `50` |
| `use_recent_fraction` | `1.0` | `0.2` | `0.1` |
| `max_fills` | `1` | `1` | `2` |
| `fill_cooldown_sec` | `0.0` | `0.0` | `0.0` |
| `min_distance_between_fills` | `0.0` | `0.0` | `0.0` |
| `min_event_center_distance_between_fills` | `0.0` | `0.0` | `1.0` |
| `center_source` | `event_mean` | same | same |
| `max_fit_center_distance_from_event` | `0.75` | `0.75` | `0.75` |
| `fit_min_amplitude` | `0.15` | not exposed | default |
| `fit_max_amplitude` | `10.0` | not exposed | default |
| `fit_offset_bound` | `10.0` | not exposed | default |
| `use_pde_cost_mean_for_amplitude` | `True` | not exposed | legacy compatibility only |

Input/output topic names are hard-coded.

### `modified_cost_node`

| Parameter | Default | Active wrapper |
|---|---:|---:|
| `bias_all_channels` | `True` | default |
| `direction_lpf_alpha` | `0.90` | default |
| `min_direction_step` | `1e-4` | default |
| `enable_affine_bias` | `True` | `True` |
| `affine_gain` | `0.5` | `0.5` |
| `affine_decay_rate` | `0.0000005` | launch default |
| `affine_min_norm` | `1e-4` | default |
| `affine_max_age` | `30.0` | `30.0` |
| `affine_direction_sign` | `1.0` | `1.0` |
| `input_pde_history_topic` | `/pde_history` | default |
| `use_pde_history_for_affine` | `True` | `True` |
| `history_exclusion_radius_factor` | `3.0` | `3.0` |
| `history_direction_mode` | `outside_to_anchor` | same |

The launch passes raw cost, `/cost_bias`, and `/cost_modified` as positional
topics, plus `/turtlebot3/sensor_transform_chatter` and `/odom`.

## Central launch compatibility switches

File: `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`

| Argument | Default | Effect |
|---|---|---|
| `use_pde_extensions` | `False` | Selects raw-cost legacy graph or PDE/Gaussian modified-cost graph |
| `escape_policy` | `conditional_gaussian_fill` | Gaussian policy; `none` preserves disabled behavior |
| `input_encoder_data_to_filter` | `True` | Appends encoder angle to filter input |
| `controller_config_filepath` | Heavy-Ball JSON | Generic launch default; active GESC wrapper overrides it |
| `filter_config_filepath` | GESC full-rotation JSON | Selects filter architecture |
| `cost_function_config_filepath` | `2D_local_min.json` | Generic default; wrapper selects multi-light photoresistor |
| `live_plot_mode` | `2D` | CSV collector live plot |
| `show_cost_surface_plot` | `False` | Optional independent 3D surface plot |

The active wrapper sets `use_pde_extensions=True` and selects the GESC
controller JSON.

### Active wrapper values not covered above

File:
`ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`

| Setting | Active value |
|---|---|
| Initial pose | `x=0`, `y=0`, `yaw=0 rad` |
| Live CSV plot | `2D` |
| Cost-surface plot | enabled, delayed `30.0 s` |
| Cost-surface bounds | `x=[-0.5,4.5] m`, `y=[-0.75,4.5] m` |
| Cost-surface resolution | `80` |
| Cost-surface orientation/z mode | `average` / `base` |
| Number of lights | `3` |
| Light 1 | `(1.0, 0.5) m`, `450.0` relative-lumen input |
| Light 2 | `(3.35, 3.20) m`, `1600.0` relative-lumen input |
| Light 3 | `(3.75, 3.45) m`, `3000.0` relative-lumen input |
| Data directory | `~/Experiments/Gazebo-Simulations` |

The rotation profile is 20 RPM (`2.09439510239 rad/s`) while the active wrapper
passes `pde_omega=5.0`. Phase 00 records both values but does not infer that
they are equivalent or that the mismatch is intentional.

## Logging interface

`data_collection_node` subscribes to:

- `/turtlebot3/timekeeper_chatter`;
- `/odom`;
- `/turtlebot3/sensor_transform_chatter`;
- `/cost_modified` in PDE mode, otherwise raw cost;
- `/turtlebot3/filter_value_chatter`;
- `/turtlebot3/control_value_chatter`.

It writes no ROS topics. It creates six files in a timestamped `Test_*`
directory. CSV rows contain no header line; positional meanings are defined in
the callback docstrings.

## Logical target to current-interface mapping

| Required logical concept | Current source | Status |
|---|---|---|
| Raw sensor value | Simulation cost output | Not separated from raw minimization cost |
| Raw minimization cost | `/turtlebot3/cost_value_chatter` | Available |
| Calibrated source score | none | Missing; do not synthesize a value |
| Gaussian contribution | internal `modified_cost_node` calculation | Exists but is not published |
| Affine contribution | internal `modified_cost_node` calculation | Exists but is not published |
| Augmented cost | `/cost_modified` | Available |
| Raw/Gaussian/affine weights | implicit constants `1,1,1` | Not switchable or published |
| Active fill | `/cost_bias` | Legacy four-field message only |
| Fill registry | `modified_cost_node.terms` in memory | Not published |
| Algorithm state/mode | none | Missing |
| Structured event | convergence array only | Partial, untyped |
| GESC filter output | `/turtlebot3/filter_value_chatter` | Available |
| Complete filter state | `filter_node.z_vec` in memory | Not published |
| Command before saturation | local values in `Directional_Controller` | Not published |
| Command after saturation | controller chatter and `/cmd_vel` | Available |
| Saturation flags | none | Missing |
| Measured pose/velocity | `/odom` | Available in simulation |
| Canonical physical pose | none | Missing |
| Source configuration | launch arguments and cost JSON | Not published |
| Room bounds/center | none | Missing |

## Phase 01 compatibility direction

Phase 01 must:

- extend `ros_esc_interfaces`;
- add typed topics under one documented GESC/Gaussian namespace;
- keep all tabled legacy topics and array layouts unchanged;
- mark unavailable source-score/physical fields explicitly rather than use
  invented numeric values;
- mirror console convergence/fill events as typed messages;
- expose internal values from their current owners;
- retain the legacy algorithm outputs bit-for-bit in focused tests.

Exact message names and edit paths are frozen in
`handoffs/phase_00_handoff.md` for the Phase 01 planning task.
