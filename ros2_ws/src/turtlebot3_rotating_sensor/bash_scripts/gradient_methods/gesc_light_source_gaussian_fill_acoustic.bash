#!/bin/bash

# GESC + PDE/Gaussian-fill source-seeking run with the multi-light
# photoresistor cost map. Edit number_of_lights and light_N_* below.

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
show_cost_surface_plot:='True' \
cost_surface_x_min:=0.0 \
cost_surface_x_max:=4.5 \
cost_surface_y_min:=0.0 \
cost_surface_y_max:=4.5 \
cost_surface_resolution:=80 \
cost_surface_orientation_mode:='average' \
cost_surface_z_scale_mode:='base' \
cost_surface_show_base_wireframe:='False' \
cost_surface_live:='True' \
cost_surface_odom_topic:='/odom' \
cost_surface_fill_topic:='/cost_bias' \
cost_surface_refresh_hz:=10.0 \
cost_surface_trajectory_period:=0.2 \
use_pde_extensions:='True' \
escape_policy:='conditional_gaussian_fill' \
rotate_frame_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json' \
sensor_transform_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json' \
cost_function_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json' \
filter_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json' \
controller_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_acoustic.json' \
pde_omega:=5.0 \
pde_cost_history_topic:='/cost_modified' \
convergence_threshold:=0.2 \
convergence_decay_rate:=0.15 \
convergence_min_fill_periods:=2.0 \
gaussian_fill_amplitude:=0.20 \
gaussian_fill_min_sigma:=0.25 \
gaussian_fill_max_sigma:=0.55 \
gaussian_fill_min_points:=50 \
gaussian_fill_use_recent_fraction:=0.1 \
gaussian_fill_max_fills:=2 \
gaussian_fill_cooldown_sec:=0.0 \
gaussian_fill_min_distance_between_fills:=0.0 \
gaussian_fill_min_event_center_distance_between_fills:=1.0 \
gaussian_fill_center_source:='event_mean' \
gaussian_fill_max_fit_center_distance_from_event:=0.75 \
modified_cost_enable_affine_bias:='True' \
modified_cost_affine_gain:=0.5 \
modified_cost_affine_max_age:=30.0 \
modified_cost_affine_direction_sign:=1.0 \
modified_cost_use_pde_history_for_affine:='True' \
modified_cost_history_exclusion_radius_factor:=3.0 \
modified_cost_history_direction_mode:='outside_to_anchor' \
number_of_lights:=3 \
light_1_x:=1.0 \
light_1_y:=0.5 \
light_1_intensity_lumens:=500.0 \
light_2_x:=2.7 \
light_2_y:=3.0 \
light_2_intensity_lumens:=1000.0 \
light_3_x:=4.0 \
light_3_y:=4.0 \
light_3_intensity_lumens:=2000.0 \
data_collection_filepath:='~/Experiments/Gazebo-Simulations'
