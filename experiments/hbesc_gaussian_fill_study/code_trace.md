# Code Trace

This trace was verified from the local repo on 2026-06-09.

## Launch Pipeline

`ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml` launches the full stack:

- Gazebo world through `empty_world.launch.py`.
- Robot description through `robot_description.launch.py`.
- Joint controllers through `control.launch.py`.
- TurtleBot spawn through `gazebo_ros spawn_entity.py`.
- Optional manual light source spawns controlled by `include_light_source` and `include_light_source_2`.
- `encoder_node`, `rotate_frame_node`, `sensor_pose_node`, `cost_function_node`, `filter_node`, `controller_node`, and `data_collection_node`.
- Optional Gaussian-fill nodes when `use_pde_extensions` is true.

The scenario runner `hb_scenario_acoustic.bash` reads a JSON `launch` object and emits `ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml key:=value` arguments. It has a whitelist, so new launch keys must be added there before scenario JSONs can use them.

## Pose And Encoder Data

Robot pose comes from `/odom`.

- `sensor_pose_node/sensor_pose_node_script.py:SensorPosition.pose_callback` reads position and quaternion from `nav_msgs/Odometry`.
- `controller_node/controller_node_script.py:CustomController.state_callback` also reads `/odom` and converts quaternion orientation to roll, pitch, yaw for the controller state vector `[x, y, z, roll, pitch, yaw]`.
- The URDF diff-drive plugin publishes `odom` and listens on `cmd_vel`.

Rotating sensor angle comes from `/joint_states`.

- `encoder_node/encoder_node_script.py:EncoderNode.joint_state_callback` extracts `rotating_frame_joint` positions from `sensor_msgs/JointState`.
- `gazebo.launch.xml` passes `joint_name_1:=rotating_frame_joint` to the encoder node.
- `control.launch.py` starts `joint_state_broadcaster` and `velocity_controller`.
- `joint_controller.yaml` controls `rotating_frame_joint` through a velocity interface.

## Sensor Pose

`sensor_pose_node/sensor_pose_node_script.py:SensorPosition.publish_sensor_position` combines odometry, encoder angles, and transform config objects, then publishes `$(entity_name)/sensor_transform_chatter`.

The active transform config `turtlebot_rotating_sensor.json` uses:

- object `Transform_Odom_To_Sensor_Pose`,
- joint position `[0, 0, 0.355]`,
- rotation axis `[0, 0, 1]`,
- sensor offset matrix with x offset `0.18` and z offset `0.015`.

## Cost Function And Noise

`cost_function_node/cost_function_node_script.py:CostFunction.publish_cost_value` evaluates one cost value per sensor transform and publishes `$(entity_name)/cost_value_chatter`.

Cost configs currently use `cost_function_objects.py:Position_Based_Sympy_Expression.cost_output`, which evaluates the configured Sympy expression at sensor position `(x, y, z)` and time `t`.

Noise is added by the configured noise object after cost evaluation. The current HeavyBall study cost configs use `noise_objects.py:No_Noise.add_noise`, so the cost values are unchanged.

## Filter

`filter_node/filter_node_script.py:CustomFilter.publish_filter_value` subscribes to cost and encoder topics, optionally concatenates encoder data, evaluates the configured filter, updates filter state with a forward Euler step, and publishes `$(entity_name)/filter_value_chatter`.

The active `gesc_filter_full_rotation.json` is a cascade/parallel filter:

- cost channel `u[0]` goes through a washout filter with `omega = 1.0`,
- encoder angle `phi` is converted to `[(2/d)*cos(phi), (2/d)*sin(phi)]` with `d = 0.18`,
- final output is `[-1*u[0]*u[1], -1*u[0]*u[2]]`.

## Baseline HBESC Control

`controller_node/controller_node_script.py:CustomController.publish_control_value` calls the configured controller object with time, odometry-derived state, and filter output.

`turtlebot_vehicle.py:Rotating_Frame_Directional_Controller.controller_output`:

- calls `update_dynamic_states`,
- gets a vehicle-relative update direction from the HBESC ODE,
- computes `vx = k_vx * update_direction[0]`,
- computes `wz = k_wz * update_direction[1]`,
- clips `vx` to `max_vx`,
- clips `wz` to `max_wz`,
- returns `[vx, 0, 0, 0, 0, wz]`.

`turtlebot_ode_objects.py:HeavyBallODE.differential_equation`:

- applies `input_gain` to the first two filter outputs,
- converts the relative gradient estimate to the absolute frame using `rotation_matrix`,
- evaluates `extremum_seeking.seekers.parameter_odes.HeavyBallFlow(k, beta)`,
- splits the ODE output into `theta_dot_absolute` and momentum derivative `v_dot`,
- converts `theta_dot_absolute` back to the vehicle frame.

## Gaussian Fill Modification

When `use_pde_extensions:=False`, the filter input is raw `$(entity_name)/cost_value_chatter`.

When `use_pde_extensions:=True`:

- `modified_cost_node/modified_cost_script.py:ModifiedCost2D` subscribes to raw cost, `/cost_bias`, sensor transforms, and `/odom`, then publishes `/cost_modified`.
- `pde_history_node/pde_history_script.py:PDEHistory.cb` stores a transport-PDE style position history from `/odom` and publishes `/pde_history`.
- `convergence_detector_node/convergence_detector_node_script.py:ConvergenceDetector.buffer_cb` computes `r`, `metric`, publishes `/convergence_metric` and `/convergence_r`, and publishes `/convergence_event` on sign crossing.
- `gaussian_fill_node/gaussian_fill_script.py:GaussianFill.trigger_cb` fits a fill from `/pde_history` and publishes `/cost_bias` as `[A, mu_x, mu_y, sigma]`.
- The filter subscribes to `/cost_modified`.

This means the Gaussian-fill controller still uses the same filter and controller pipeline, but its cost signal is biased after fill events.

## vx, wz, And Sensor Spin

`vx` and `wz` are robot body commands:

- `controller_node_script.py:CustomController.publish_control_value` maps output index `0` to `Twist.linear.x` and output index `5` to `Twist.angular.z`.
- The published topic is `/cmd_vel`.
- The URDF diff-drive plugin listens to `cmd_vel`.

Sensor spin is separate:

- `rotate_frame_node/rotate_frame_node_script.py:RotateFrame.publish_velocity_cmds` publishes velocity commands to the rotating-frame joint controller.
- `spin_profile_objects.py:Constant_Full_Rotation.velocity_output` returns a constant angular velocity from `spin_rpm * 2*pi/60`.
- `full_rotation.json` uses `spin_rpm = 20`; `full_rotation_acoustic.json` uses `spin_rpm = 10`.

Therefore changing controller `wz` changes robot yaw command, not rotating sensor spin. Changing `spin_rpm` changes sampling geometry and filter excitation, not `/cmd_vel`.

## Velocity Limits And Wheel RPM

Controller configs define `wheel_radius = 0.033`, `wheel_distance = 0.158`, and `wheel_max_rpm = 70`.

`Rotating_Frame_Directional_Controller.__init__` computes:

- `omega_max = wheel_max_rpm / 60 * 2*pi`,
- `max_vx = omega_max * wheel_radius`,
- `max_wz = 2 * omega_max * wheel_radius / wheel_distance`.

Then `set_max_vx` and `set_max_wz` override those computed values when not null.

Wheel reconstruction for analysis:

```text
omega_left_rad_s  = (v - omega * L / 2) / r
omega_right_rad_s = (v + omega * L / 2) / r
rpm = omega_rad_s * 60 / (2*pi)
```

Use controller config `L = wheel_distance` and `r = wheel_radius` for controller-feasibility analysis. Use URDF values separately when discussing Gazebo physical model.

## Logged Verification Streams

Normal data collection writes:

- `odometry.csv`: `/odom`.
- `sensor_transform.csv`: `$(entity_name)/sensor_transform_chatter`.
- `cost_value.csv`: raw cost in baseline mode, `/cost_modified` in PDE mode.
- `filter_value.csv`: `$(entity_name)/filter_value_chatter`.
- `control_value.csv`: `$(entity_name)/control_value_chatter`, containing `[vx, vy, vz, wx, wy, wz]`.
- `comments.txt`: config metadata.

Needed before full Gaussian-fill runs:

- raw cost in Gaussian-fill mode,
- `/cost_bias`,
- `/pde_history`,
- `/convergence_event`,
- `/convergence_metric`,
- `/convergence_r`.
