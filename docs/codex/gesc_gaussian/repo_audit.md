# Phase 00 Repository Audit

Audit date: 2026-07-20

## Audit boundary and repository state

This is a read-only architecture audit for the GESC plus robust-Gaussian
implementation sequence. No ROS source, launch, configuration, generated
artifact, or physical-hardware behavior was changed.

- Repository root: `/home/mattb/dsim-lab`
- ROS workspace: `/home/mattb/dsim-lab/ros2_ws`
- Branch: `feature/gesc-gaussian-robustness-v1`
- Audited commit: `e0c693e6c9f954d3e7061c90089b7b2a2c6a1d4c`
- ROS distribution: Humble
- Prior Phase 00 handoffs: none, as expected
- Generated directories excluded from edits:
  `ros2_ws/build`, `ros2_ws/install`, `ros2_ws/log`, and top-level `log`

The working tree was already dirty before this audit:

```text
 M ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash
?? DSIM_GESC_Gaussian_Codex_Implementation_Package/
?? docs/
```

The modified GESC wrapper is user-owned and was not changed. Its current
three-light values are part of the audited active profile, not Phase 00 edits.

The saved plan in
`docs/codex/gesc_gaussian/plans/phase_00_plan.md` remains consistent with the
current checkout. No stop-condition contradiction was found.

## Workspace and package map

`colcon list --base-paths ros2_ws/src` finds exactly three ROS packages:

| Package | Exact path | Build type | Responsibility |
|---|---|---|---|
| `ros_esc` | `ros2_ws/src/ros_esc` | `ament_python` | ESC nodes, cost models, filtering, control, Gaussian/PDE extensions, CSV collection, and plotting |
| `ros_esc_interfaces` | `ros2_ws/src/ros_esc_interfaces` | `ament_cmake` | Repository custom ROS messages |
| `turtlebot3_rotating_sensor` | `ros2_ws/src/turtlebot3_rotating_sensor` | `ament_cmake` | TurtleBot model, Gazebo/control launch, joint configuration, and experiment wrappers |

`extremum-seeking/` is a conventional Python distribution named
`extremum_seeking`, not a ROS package. `ros_esc` imports its filter and
parameter-ODE implementations.

### Declared and effective dependencies

`ros_esc/package.xml` declares only `rclpy` and the runtime dependency
`python3-scipy`. The Python sources also effectively import:

- ROS packages: `ros_esc_interfaces`, `std_msgs`, `sensor_msgs`, `nav_msgs`,
  and `geometry_msgs`;
- Python libraries: `numpy`, `scipy`, `matplotlib`, `sympy`, and the local
  `extremum_seeking` distribution.

Those effective dependencies are not fully represented in
`ros_esc/package.xml` or `setup.py`.

`ros_esc_interfaces` declares `geometry_msgs`, `rclpy`,
`rosidl_default_generators`, and `rosidl_default_runtime`.

`turtlebot3_rotating_sensor` declares its Gazebo, URDF, xacro, ros2_control,
joint-state, velocity-controller, and `rclpy` dependencies in
`ros2_ws/src/turtlebot3_rotating_sensor/package.xml`.

## Existing custom interfaces

The dedicated interface package already exists and must be extended rather
than replaced:

| Definition | Exact path | Fields |
|---|---|---|
| `ros_esc_interfaces/msg/Timekeeper` | `ros2_ws/src/ros_esc_interfaces/msg/Timekeeper.msg` | `string mode`, `float64 start_time` |
| `ros_esc_interfaces/msg/StampedFloat64` | `ros2_ws/src/ros_esc_interfaces/msg/StampedFloat64.msg` | `string header`, `float64 timestamp`, `float64 data` |
| `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `ros2_ws/src/ros_esc_interfaces/msg/StampedFloat64MultiArray.msg` | `string header`, `float64 timestamp`, `float64[] data` |
| `ros_esc_interfaces/msg/StampedString` | `ros2_ws/src/ros_esc_interfaces/msg/StampedString.msg` | `string header`, `float64 timestamp`, `string data` |
| `ros_esc_interfaces/msg/StampedTransformMultiArray` | `ros2_ws/src/ros_esc_interfaces/msg/StampedTransformMultiArray.msg` | `string header`, `float64 timestamp`, `geometry_msgs/Transform[] transform_array` |

The timestamp convention is floating-point seconds, usually relative to the
experiment start for the legacy pipeline. The PDE nodes instead publish
floating-point simulation-clock seconds. This is a real synchronization
limitation; Phase 01 must expose the time basis without silently changing
legacy timestamps.

## Exact ROS executables and node names

All entries are console scripts from `ros2_ws/src/ros_esc/setup.py`.

| Executable | Runtime node name | Source |
|---|---|---|
| `encoder_node` | `encoder_node` | `ros2_ws/src/ros_esc/ros_esc/encoder_node/encoder_node_script.py` |
| `sensor_pose_node` | `sensor_position_node` | `ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/sensor_pose_node_script.py` |
| `rotate_frame_node` | `rotate_arm` | `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_node_script.py` |
| `cost_function_node` | `cost_function` | `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py` |
| `filter_node` | `custom_filter` | `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_node_script.py` |
| `convergence_detector_node` | `convergence_detector` | `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py` |
| `gaussian_fill_node` | `gaussian_fill` | `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py` |
| `modified_cost_node` | `modified_cost_2d` | `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py` |
| `pde_history_node` | `pde_history` | `ros2_ws/src/ros_esc/ros_esc/pde_history_node/pde_history_script.py` |
| `controller_node` | `custom_controller` | `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py` |
| `data_collection_node` | `data_collection_node` | `ros2_ws/src/ros_esc/ros_esc/data_collection_node/data_collection_node_script.py` |
| `pde_cost_history_node` | `pde_cost_history` | `ros2_ws/src/ros_esc/ros_esc/pde_cost_history_node/pde_cost_history_script.py` |
| `cost_surface_plotter` | `cost_surface_plotter` in live mode | `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/cost_surface_plotter.py` |

## Existing GESC path

### Sensor-frame dither

Owner files:

- `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/spin_profile_objects/spin_profile_objects.py`
- `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json`

The active configuration selects `Constant_Full_Rotation` with
`spin_rpm = 20`, which is `2.09439510239 rad/s`. The node publishes the
rotating-joint command on `/velocity_controller/commands` as
`std_msgs/msg/Float64MultiArray` and publishes
`/turtlebot3/timekeeper_chatter` as
`ros_esc_interfaces/msg/Timekeeper`.

### Gradient estimator

Owner files:

- `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json`

The filter consumes one cost channel plus encoder angle. It applies a washout
filter to the cost, constructs `(2 / d) cos(phi)` and `(2 / d) sin(phi)` with
`d = 0.18 m`, then publishes:

```text
[-washout(cost) * (2/d) cos(phi),
 -washout(cost) * (2/d) sin(phi)]
```

on `/turtlebot3/filter_value_chatter` as
`ros_esc_interfaces/msg/StampedFloat64MultiArray`.

### Directional controller and saturation

Owner files:

- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_ode_objects.py`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage.json`

The active GESC controller is `Directional_Controller` with:

- `k_vx = 1.0`;
- `k_wz = 5.0`;
- configured `|v_x| <= 0.1 m/s`;
- configured `|w_z| <= 0.5 rad/s`.

It publishes the post-saturation six-element command
`[vx, vy, vz, wx, wy, wz]` on
`/turtlebot3/control_value_chatter` and publishes the same values as a
`geometry_msgs/msg/Twist` on `/cmd_vel`. Pre-saturation commands, saturation
flags, and the complete filter state are not published.

## Sensor, pose, and simulation cost path

### Gazebo plant

The differential-drive plugin in
`ros2_ws/src/turtlebot3_rotating_sensor/urdf/turtlebot3_rotating_sensor.urdf`
consumes `/cmd_vel` and publishes `/odom` (`nav_msgs/msg/Odometry`). The same
URDF publishes `/joint_states` (`sensor_msgs/msg/JointState`). The
ros2_control configuration is
`ros2_ws/src/turtlebot3_rotating_sensor/controller_config/joint_controller.yaml`.

### Encoder and sensor pose

`encoder_node` converts the configured `rotating_frame_joint` from
`/joint_states` into `/turtlebot3/encoder_chatter`.

`sensor_pose_node` combines `/odom`, encoder angle, and
`ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json`
to publish `/turtlebot3/sensor_transform_chatter` as
`StampedTransformMultiArray`.

### Cost owner and sign

Owner files:

- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/cost_function_objects.py`

The active GESC-plus-Gaussian wrapper selects:

`ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json`

which instantiates `Multi_Light_Source_Cost` in `Voltage` mode. Voltage is
multiplied by `-1`, so the light source is a minimum and the existing
minimization sign must not be changed.

`Photoresistor_Interpolated_Map` remains the compatible single-light model.
`Multi_Light_Source_Cost` sums per-light conductance deltas and uses:

```text
intensity_scale = intensity_lumens / reference_intensity_lumens
```

This is relative simulator scaling. It is not an absolute lux calibration.
Gazebo point-light models are visual markers; the Python cost object is the
mathematical field.

The cost owner publishes one value per sensor transform on
`/turtlebot3/cost_value_chatter` as
`StampedFloat64MultiArray`. There is no distinct raw physical sensor topic and
no calibrated `source_score`.

## Existing convergence, Gaussian, and affine path

### PDE histories

`pde_history_node`:

- source:
  `ros2_ws/src/ros_esc/ros_esc/pde_history_node/pde_history_script.py`;
- subscribes to hard-coded `/odom`;
- publishes `/pde_history` as
  `StampedFloat64MultiArray`;
- layout: `[x0, y0, x1, y1, ...]`, newest first;
- defaults: `n_buffer=2000`, `k_periods=20`, `omega=5.0`, `cfl=0.9`;
- forces `use_sim_time=true`.

`pde_cost_history_node`:

- source:
  `ros2_ws/src/ros_esc/ros_esc/pde_cost_history_node/pde_cost_history_script.py`;
- subscribes to parameter `cost_topic`;
- publishes `/pde_cost_history` as unstamped
  `std_msgs/msg/Float64MultiArray`;
- layout: `[J0, J1, ...]`, newest first;
- active wrapper routes `cost_topic=/cost_modified`;
- defaults: `n_buffer=2000`, `k_periods=20`, `omega=5.0`, `cfl=0.9`.

The pose and cost histories are independently updated and are not
message-filter synchronized.

### Convergence detector

Owner:
`ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py`

It compares the recent history mean with an older history mean:

```text
r = ||mean_recent - mean_old||^2
metric = r + exp(-decay_rate * (t - t0)) - threshold
```

A candidate requires a positive-to-negative metric crossing. The default
counter begins at three, and `/convergence_event` is published when it reaches
zero. The event layout is:

```text
[metric, r, decay, mean_recent_x, mean_recent_y,
 mean_old_x, mean_old_y, count_remaining]
```

It also publishes `/convergence_metric`, `/convergence_r`, and
`/convergence_count`, each as `StampedFloat64MultiArray`.

With active wrapper values `k_periods=20`, `omega=5.0`, and
`min_fill_periods=2.0`, the startup gate is approximately `50.27 s`.
The separate sensor-rotation profile is 20 RPM (`2.09439510239 rad/s`);
Phase 00 does not assume the active `pde_omega=5.0` value is the same
quantity or that their difference is intentional.

### Gaussian fill

Owner:
`ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`

Already implemented:

- policies `none`, `conditional_gaussian_fill`, and
  `multi_gaussian_fill`, including aliases;
- inverted isotropic Gaussian least-squares fit against `-cost`;
- default convergence-event mean anchoring;
- fitted-center bounds and optional clamp behavior;
- adaptive isotropic sigma within configured bounds;
- fixed configured published amplitude, with fitted amplitude used as a
  quality gate;
- fill cooldown;
- duplicate rejection by fill center and by event center;
- configurable maximum fill count.

The legacy output `/cost_bias` is
`StampedFloat64MultiArray` with:

```text
[amplitude, center_x, center_y, sigma]
```

No fill ID, covariance, confidence, revision, merge/supersession state, fit
residual, or typed registry message exists.

### Modified cost and affine term

Owner:
`ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`

It retains every accepted Gaussian term in memory and evaluates:

```text
modified_cost =
    raw_cost
  + sum(gaussian terms)
  + sum(decaying affine terms)
```

The affine term is:

```text
-b(t)^T (x - anchor)
b(t) = b0 exp(-affine_decay_rate * age)
```

The preferred direction comes from the newest `/pde_history` point outside
`history_exclusion_radius_factor * sigma`; low-pass odometry direction is the
fallback. The output `/cost_modified` preserves the input message timestamp
and type.

Raw cost is always weighted by one. There are no independently switchable or
published raw/Gaussian/affine weights, no per-term diagnostic topic, and no
explicit escape state.

## Launch and profile audit

The central launch file is:

`ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`

Included launch files:

- `ros2_ws/src/turtlebot3_rotating_sensor/launch/empty_world.launch.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/robot_description.launch.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/control.launch.py`

Additional launch files not used by the active GESC wrapper:

- `ros2_ws/src/turtlebot3_rotating_sensor/launch/rviz.launch.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/rviz.launch.xml`

The active wrapper is:

`ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`

Key compatibility behavior:

- `use_pde_extensions` defaults to `False`;
- when false, the filter consumes `/turtlebot3/cost_value_chatter`;
- when true, modified cost, both PDE histories, convergence, and Gaussian fill
  run, and the filter consumes `/cost_modified`;
- the generic launch default controller is the Heavy-Ball JSON, but the active
  GESC wrapper explicitly selects the GESC JSON;
- robust work must remain opt-in and must not modify Heavy-Ball behavior;
- the current wrapper's user-edited light positions and intensities must be
  preserved.

The exact parameter and launch-argument inventory is in `interface_map.md`.

## Existing logging and plotting

Owner:
`ros2_ws/src/ros_esc/ros_esc/data_collection_node/data_collection_node_script.py`

Each run creates:

```text
~/Experiments/Gazebo-Simulations/Test_YYYY-MM-DD_HH-MM-SS/
├── comments.txt
├── control_value.csv
├── cost_value.csv
├── filter_value.csv
├── odometry.csv
└── sensor_transform.csv
```

In PDE mode, `cost_value.csv` records `/cost_modified`; raw cost and individual
Gaussian/affine contributions are not recorded simultaneously.

`ros2_ws/src/ros_esc/ros_esc/plotting_scripts/cost_surface_plotter.py`
subscribes to `/odom` and `/cost_bias` in live mode and can save a PNG into
the newest `Test_*` directory.

There is no repository-native rosbag recorder, topic manifest enforcement,
run-metadata schema, completeness checker, or bag analysis pipeline.
The environment provides `rosbag2_py` and sqlite3 storage; MCAP is not
registered.

## Physical and Vicon audit

This checkout contains no canonical:

- physical photoresistor acquisition node;
- Vicon or motion-capture adapter;
- physical launch graph;
- Nav2/planner integration;
- room-boundary or room-center interface;
- recenter controller;
- hardware command adapter for this pipeline.

Comments and reusable math mention physical experiments, but those are not an
executable physical GESC-plus-Gaussian graph. Phase 09 must begin with
`docs/codex/gesc_gaussian/phase09_physical_interface_inventory.md` and stop if
the external physical checkout/interfaces are unavailable.

## Existing tests and baseline

Repository-native automated tests are lint-oriented:

- `ros2_ws/src/ros_esc/test/test_copyright.py`
- `ros2_ws/src/ros_esc/test/test_flake8.py`
- `ros2_ws/src/ros_esc/test/test_pep257.py`
- `ament_lint_auto` in
  `ros2_ws/src/ros_esc_interfaces/CMakeLists.txt`
- `ament_lint_auto` in
  `ros2_ws/src/turtlebot3_rotating_sensor/CMakeLists.txt`

The `*_config_testing.py` scripts under `ros_esc/ros_esc` are manual examples,
not pytest tests.

Stored test results in `ros2_ws/build` report:

```text
Summary: 885 tests, 0 errors, 875 failures, 1 skipped
```

The failures are pre-existing flake8, pep257, and interface-package lint
debt. No focused unit, launch, or end-to-end tests exercise the current
Gaussian pipeline.

Read-only syntax validation during Phase 00 passed for 61 Python files, 62 JSON
files, five XML files, and the active GESC wrapper. The exact commands and
results are recorded in `test_commands.md`.

## Behavior already matching the target specification

- GESC is selectable and used by the active wrapper.
- Raw simulation cost remains available on its legacy topic.
- Gaussian behavior is opt-in through `use_pde_extensions`.
- Convergence gating and repeated-candidate counting exist.
- The convergence-event recent mean can anchor a fill.
- Fitted-center drift is bounded.
- Sigma is fit and clamped.
- Multiple separated fills can persist and be summed.
- Duplicate fill/event-center rejection exists.
- A decaying affine term exists.
- Legacy cost sign, array topics, and controller limits are explicit.
- CSV logging and live plotting already exist.

## Missing target behavior

- typed observability for cost breakdown, fills, controller diagnostics,
  state, and events;
- a calibrated and validity-marked source score;
- simultaneous logging of raw and augmented cost;
- independent raw, Gaussian, and affine weights;
- explicit hybrid states and transitions;
- synchronized pose/raw-cost samples and robust outlier rejection;
- covariance/anisotropic basin estimation;
- depth/curvature-based fill design;
- residual-minimum verification and bounded escalation;
- association, merge, revision, and supersession;
- measured escape/stall handling and assisted escape;
- boundary safety and recentering;
- a unified failsafe owner and explicit zero-command fault path;
- rosbag recording, metadata, completeness checks, scenario automation, and
  bag analysis;
- audited physical sensor/Vicon adapters.

## Package expectations disproved by the checkout

These are not contradictions in the saved Phase 00 plan; they are target
assumptions that the package explicitly required Phase 00 to resolve.

1. There is no existing Vicon, physical sensor, or physical launch path to map.
2. There is no planner to reuse for recentering.
3. There is no existing supervisor/state-machine owner.
4. There is no repository rosbag workflow even though the environment has
   `rosbag2_py`.
5. The current "raw sensor -> raw cost" chain is not separated in simulation;
   the synthetic cost value is the available sensor-like signal.
6. The package's logical typed messages and canonical topics do not exist.
7. Existing algorithm configuration is primarily JSON plus XML/CLI/ROS
   parameters, not a general algorithm YAML convention.
8. Several requested Gaussian behaviors are already partly implemented and
   must be extended, not created as a second Gaussian system.
9. `intensity_lumens` is relative simulator scaling, not absolute photometric
   calibration.
10. Simulation-time assumptions and hard-coded `/odom` remain inside the PDE
    path, so sim/physical parity does not yet exist.

## Compatibility constraints

- Preserve `/turtlebot3/cost_value_chatter`, `/cost_modified`, `/cost_bias`,
  `/turtlebot3/filter_value_chatter`,
  `/turtlebot3/control_value_chatter`, and `/cmd_vel`.
- Preserve all legacy `StampedFloat64MultiArray` layouts.
- Preserve negative-voltage minimization semantics and documented units.
- Keep `use_pde_extensions=False` behavior unchanged.
- Add typed observability in parallel with legacy topics.
- Extend `ros_esc_interfaces`; do not create another interface package.
- Extend the current cost, filter, controller, convergence, Gaussian, and
  modified-cost owners rather than add duplicate nodes.
- Do not edit the user-owned active wrapper until a later approved plan
  explicitly includes it.
- Do not infer physical filenames or topics before the Phase 09 inventory.

## Blocking issues

There is no Phase 00 blocker. The existing lint baseline is not clean and must
be separated from failures introduced by later phases. Physical integration
remains blocked until the external physical interfaces are inventoried and
simulation acceptance gates pass.
