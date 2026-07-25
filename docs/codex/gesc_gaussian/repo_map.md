# GESC Gaussian Repository Map

This map records exact ownership in the Phase 00 checkout. Paths are relative
to `/home/mattb/dsim-lab`.

## Top-level structure

```text
dsim-lab/
├── DSIM_GESC_Gaussian_Codex_Implementation_Package/  # requirements/prompts
├── docs/codex/gesc_gaussian/                         # durable phase memory
├── extremum-seeking/                                 # Python library, not ROS
├── ros2_ws/
│   └── src/
│       ├── ros_esc/
│       ├── ros_esc_interfaces/
│       └── turtlebot3_rotating_sensor/
└── writing/                                          # prior study material
```

Generated `ros2_ws/build`, `ros2_ws/install`, `ros2_ws/log`, and top-level
`log` are not source and must not be edited.

## Package dependency graph

```text
turtlebot3_rotating_sensor
  ├── launches Gazebo, ros2_control, and ros_esc executables
  └── owns URDF/world/light-marker/controller configuration

ros_esc
  ├── imports messages from ros_esc_interfaces
  ├── imports algorithms from extremum_seeking
  └── imports standard ROS messages and scientific Python libraries

ros_esc_interfaces
  └── generates repository-specific ROS messages
```

## Active GESC plus Gaussian execution graph

```text
Gazebo diff drive ───────────────────────────────> /odom
Gazebo joint publisher ─────────────────────────> /joint_states

/joint_states
  -> encoder_node [encoder_node]
  -> /turtlebot3/encoder_chatter

/turtlebot3/encoder_chatter
  -> rotate_frame_node [rotate_arm]
  -> /velocity_controller/commands
  -> /turtlebot3/timekeeper_chatter

/odom + /turtlebot3/encoder_chatter
  -> sensor_pose_node [sensor_position_node]
  -> /turtlebot3/sensor_transform_chatter

/turtlebot3/sensor_transform_chatter
  -> cost_function_node [cost_function]
  -> /turtlebot3/cost_value_chatter

/odom
  -> pde_history_node [pde_history]
  -> /pde_history

/turtlebot3/cost_value_chatter + /cost_bias
  -> modified_cost_node [modified_cost_2d]
  -> /cost_modified

/cost_modified
  -> pde_cost_history_node [pde_cost_history]
  -> /pde_cost_history

/pde_history
  -> convergence_detector_node [convergence_detector]
  -> /convergence_metric, /convergence_r, /convergence_count
  -> /convergence_event

/convergence_event + /pde_history + /pde_cost_history
  -> gaussian_fill_node [gaussian_fill]
  -> /cost_bias

/cost_modified + /turtlebot3/encoder_chatter
  -> filter_node [custom_filter]
  -> /turtlebot3/filter_value_chatter

/turtlebot3/filter_value_chatter + /odom
  -> controller_node [custom_controller]
  -> /turtlebot3/control_value_chatter
  -> /cmd_vel
  -> Gazebo diff drive
```

When `use_pde_extensions=False`, the PDE/Gaussian branch is absent and
`filter_node` consumes `/turtlebot3/cost_value_chatter` directly.

## Exact package ownership

### `ros_esc_interfaces`

Build and dependency files:

- `ros2_ws/src/ros_esc_interfaces/CMakeLists.txt`
- `ros2_ws/src/ros_esc_interfaces/package.xml`

Message definitions:

- `ros2_ws/src/ros_esc_interfaces/msg/Timekeeper.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/StampedFloat64.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/StampedFloat64MultiArray.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/StampedString.msg`
- `ros2_ws/src/ros_esc_interfaces/msg/StampedTransformMultiArray.msg`

No services are defined.

### `ros_esc`

Package and console entry points:

- `ros2_ws/src/ros_esc/package.xml`
- `ros2_ws/src/ros_esc/setup.py`
- `ros2_ws/src/ros_esc/setup.cfg`

Configuration parser and library bridge:

- `ros2_ws/src/ros_esc/ros_esc/config_parsing.py`
- `ros2_ws/src/ros_esc/ros_esc/helper_functions.py`

GESC sensor/dither path:

- `ros2_ws/src/ros_esc/ros_esc/encoder_node/encoder_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/spin_profile_objects/spin_profile_objects.py`
- `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json`
- `ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/sensor_pose_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_objects/transform_objects.py`
- `ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json`

Simulation cost:

- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/cost_function_objects.py`
- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/noise_objects.py`
- `ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json`

GESC filter:

- `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json`

Controller:

- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_ode_objects.py`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage.json`

PDE/convergence/Gaussian/affine:

- `ros2_ws/src/ros_esc/ros_esc/pde_history_node/pde_history_script.py`
- `ros2_ws/src/ros_esc/ros_esc/pde_cost_history_node/pde_cost_history_script.py`
- `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`
- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`

Collection and plotting:

- `ros2_ws/src/ros_esc/ros_esc/data_collection_node/data_collection_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/data_collection_node/live_plot_animation.py`
- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/cost_surface_plotter.py`
- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/plotting_node_outputs.py`
- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/plotting_trajectories.py`
- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/plotting_vehicle_states.py`

Automated tests:

- `ros2_ws/src/ros_esc/test/test_copyright.py`
- `ros2_ws/src/ros_esc/test/test_flake8.py`
- `ros2_ws/src/ros_esc/test/test_pep257.py`

### `turtlebot3_rotating_sensor`

Package/build:

- `ros2_ws/src/turtlebot3_rotating_sensor/package.xml`
- `ros2_ws/src/turtlebot3_rotating_sensor/CMakeLists.txt`

Central and included launch:

- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/empty_world.launch.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/robot_description.launch.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/control.launch.py`

Other launch:

- `ros2_ws/src/turtlebot3_rotating_sensor/launch/rviz.launch.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/rviz.launch.xml`

Plant and controller files:

- `ros2_ws/src/turtlebot3_rotating_sensor/urdf/turtlebot3_rotating_sensor.urdf`
- `ros2_ws/src/turtlebot3_rotating_sensor/controller_config/joint_controller.yaml`
- `ros2_ws/src/turtlebot3_rotating_sensor/worlds/gazebo_empty.world`

Light marker:

- `ros2_ws/src/turtlebot3_rotating_sensor/models/light_source/model.sdf`
- `ros2_ws/src/turtlebot3_rotating_sensor/models/light_source/model.config`

Active GESC-plus-Gaussian wrapper:

- `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`

Compatibility-only Heavy-Ball Gaussian wrapper:

- `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_gaussian_full_rotation_voltage.bash`

Heavy-Ball is outside the new implementation scope.

## Runtime node/executable naming map

| Console executable | Node name |
|---|---|
| `encoder_node` | `encoder_node` |
| `rotate_frame_node` | `rotate_arm` |
| `sensor_pose_node` | `sensor_position_node` |
| `cost_function_node` | `cost_function` |
| `modified_cost_node` | `modified_cost_2d` |
| `pde_history_node` | `pde_history` |
| `pde_cost_history_node` | `pde_cost_history` |
| `convergence_detector_node` | `convergence_detector` |
| `gaussian_fill_node` | `gaussian_fill` |
| `filter_node` | `custom_filter` |
| `controller_node` | `custom_controller` |
| `data_collection_node` | `data_collection_node` |
| `cost_surface_plotter` | `cost_surface_plotter` in live mode |

Later documentation and tests must not assume executable names and runtime node
names are identical.

## Configuration path map for the active wrapper

| Purpose | Exact file |
|---|---|
| Sensor rotation | `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json` |
| Sensor transform | `ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json` |
| Multi-light cost | `ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json` |
| GESC gradient filter | `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json` |
| GESC directional controller | `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage.json` |
| Rotating joint controller | `ros2_ws/src/turtlebot3_rotating_sensor/controller_config/joint_controller.yaml` |

The multi-light file remains under a historical `heavy_ball_PDE_ESC` directory,
but the selected cost class is controller-independent. Do not interpret its
directory name as evidence that the active controller is Heavy-Ball.

## Later-phase owner map

| Capability | Existing owner to extend | New owner allowed only if still absent |
|---|---|---|
| Raw/simulation cost and source metadata | `cost_function_node` | Physical adapter after Phase 09 inventory |
| Cost-term evaluation and weights | `modified_cost_node` | None |
| GESC estimate diagnostics | `filter_node` | None |
| Command diagnostics/saturation | `controller_node` and `Directional_Controller` | Supervisor final-command owner in Phase 02 |
| Convergence events | `convergence_detector_node` | None |
| Basin estimation/fill registry | `gaussian_fill_node` | Internal helper modules, not a duplicate ROS node |
| Hybrid state coordination | No current owner | `ros_esc/ros_esc/supervisor_node/` after Phase 02 approval |
| Escape/recenter | No current owner | Internal supervisor component after Phase 04 approval |
| Experiment recording | Legacy `data_collection_node` | Repository-native recorder after Phase 05 approval |
| Scenario automation | No current owner | `ros_esc` scenario-runner area after Phase 06 approval |
| Analysis | Existing plotting scripts | Bag reader/analysis modules after Phase 07 approval |
| Physical pose/sensor adapters | Absent | Phase 09 inventory decides exact paths |

Phase 08 recorder/shutdown support remains inside the existing owners:
`experiment_recording/record_run.py` owns native parameter snapshots and
process-tree coordination, `deferred_signal_shutdown.py` is the shared
callback-safe Python signal helper, and
`turtlebot3_rotating_sensor/launch/control.launch.py` owns the bounded
controller-spawner timeout. None is a second recorder, controller, or launch
graph.

## Known absence map

No tracked source path implements a Vicon adapter, physical photoresistor
reader, physical GESC-plus-Gaussian launch, supervisor, state machine, Nav2
planner, recenter controller, rosbag runner, scenario schema, or bag parser.
