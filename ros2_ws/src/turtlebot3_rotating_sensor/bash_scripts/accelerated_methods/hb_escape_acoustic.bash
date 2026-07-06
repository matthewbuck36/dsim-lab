#!/bin/bash

# Baseline HBESC momentum-escape test.
# PDE/Gaussian fill is disabled; escape should come from Heavy-Ball momentum.
cd ~/dsim-lab/ros2_ws

colcon build --packages-select ros_esc ros_esc_interfaces turtlebot3_rotating_sensor

source install/setup.bash

ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
entity_name:='turtlebot3' \
init_x_position:=-2 \
init_y_position:=-2 \
init_yaw_angle:=0 \
input_encoder_data_to_filter:='True' \
live_plot_mode:='2D' \
show_cost_surface_plot:='True' \
cost_surface_x_min:=0.0 \
cost_surface_x_max:=12.0 \
cost_surface_y_min:=0.0 \
cost_surface_y_max:=12.0 \
cost_surface_resolution:=80 \
cost_surface_orientation_mode:='fixed' \
cost_surface_z_scale_mode:='base' \
cost_surface_show_base_wireframe:='True' \
cost_surface_live:='True' \
cost_surface_odom_topic:='/odom' \
cost_surface_fill_topic:='/cost_bias' \
cost_surface_refresh_hz:=10.0 \
cost_surface_trajectory_period:=0.2 \
use_pde_extensions:='False' \
escape_policy:='none' \
rotate_frame_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json' \
sensor_transform_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json' \
cost_function_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/gaussian_two_basin_original.json' \
filter_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json' \
controller_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/hbesc_baseline_real_full_rotation.json' \
number_of_lights:=2 \
light_1_x:=2.0 \
light_1_y:=2.0 \
light_1_intensity_lumens:=1000.0 \
light_2_x:=10.0 \
light_2_y:=10.0 \
light_2_intensity_lumens:=2500.0 \
data_collection_filepath:='~/Experiments/Gazebo-Simulations'
