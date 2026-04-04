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
rotate_frame_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/no_rotation.json' \
sensor_transform_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json' \
cost_function_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_config_files/static_2D_photoresistor_voltage_map.json' \
filter_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/angular_tuning_filter.json' \
controller_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/angular_tuning_controller.json' \
data_collection_filepath:='~/Experiments/Gazebo-Simulations' \
