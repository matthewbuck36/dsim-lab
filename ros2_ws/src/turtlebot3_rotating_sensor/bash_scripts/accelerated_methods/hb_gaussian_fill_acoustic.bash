#!/bin/bash

# HBESC + PDE/Gaussian-fill basin-escape test.
cd ~/dsim-lab/ros2_ws

colcon build --packages-select ros_esc ros_esc_interfaces turtlebot3_rotating_sensor

source install/setup.bash

ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
entity_name:='turtlebot3' \
init_x_position:=0 \
init_y_position:=0 \
init_yaw_angle:=0 \
input_encoder_data_to_filter:='True' \
live_plot_mode:='2D' \
use_pde_extensions:='True' \
escape_policy:='conditional_gaussian_fill' \
rotate_frame_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json' \
sensor_transform_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json' \
cost_function_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/gaussian_two_basin_original.json' \
filter_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json' \
controller_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/hbesc_gaussian_conservative_full_rotation.json' \
pde_omega:=5.0 \
convergence_threshold:=0.2 \
convergence_decay_rate:=0.15 \
convergence_min_fill_periods:=2.0 \
gaussian_fill_amplitude:=5.0 \
gaussian_fill_min_sigma:=3.16 \
gaussian_fill_max_sigma:=5.0 \
gaussian_fill_min_points:=50 \
gaussian_fill_use_recent_fraction:=0.2 \
gaussian_fill_max_fills:=1 \
gaussian_fill_cooldown_sec:=0.0 \
gaussian_fill_min_distance_between_fills:=0.0 \
include_light_source:='True' \
light_source_entity_name:='manual_light_1' \
light_source_x:=2.0 \
light_source_y:=2.0 \
light_source_z:=0.0 \
include_light_source_2:='True' \
light_source_2_entity_name:='manual_light_2' \
light_source_2_x:=10.0 \
light_source_2_y:=10.0 \
light_source_2_z:=0.0 \
data_collection_filepath:='~/Experiments/Gazebo-Simulations'
