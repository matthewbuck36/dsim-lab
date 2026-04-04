#!/bin/bash

# Navigate to the ros2 workspace
cd ~/dsim-lab/ros2_ws

# Build the required packages
colcon build --packages-select ros_esc ros_esc_interfaces turtlebot3_rotating_sensor

# Source the ROS setup bash script
source install/setup.bash

# Run the gazebo launch file with requested parameters
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
entity_name:='turtlebot3' \
init_x_position:=0 \
init_y_position:=0 \
init_yaw_angle:=0 \
input_encoder_data_to_filter:='True' \
live_plot_mode:='2D' \
use_pde_extensions:='True' \
rotate_frame_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json' \
sensor_transform_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json' \
cost_function_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/2D_local_min.json' \
filter_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json' \
controller_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/adaptive_methods/heavyball_controller_full_rotation.json' \
pde_omega:=5.0 \
convergence_threshold:=0.2 \
convergence_decay_rate:=0.15 \
convergence_min_fill_periods:=2.0 \
gaussian_fill_amplitude:=5.0 \
gaussian_fill_min_sigma:=3.16 \
gaussian_fill_use_recent_fraction:=0.2 \
data_collection_filepath:='~/Experiments/Gazebo-Simulations' \
