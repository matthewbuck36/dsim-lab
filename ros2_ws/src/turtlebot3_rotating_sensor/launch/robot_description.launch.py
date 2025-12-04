#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This script is responsible for publishing the robot's URDF file to the
robot description topic. Various launch files make use of this script to gather
the robot's description for use in a RVIZ or Gazebo simulation.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.substitutions import Command

def generate_launch_description():
    """This function publishes the robot's URDF file to the /robot_description topic."""

    # Gather URDF file information
    urdf_file = 'turtlebot3_rotating_sensor.urdf'
    urdf_desc_path = os.path.join(
        get_package_share_directory('turtlebot3_rotating_sensor'),
        'urdf', urdf_file
    )

    # Start robot state publisher
    # Parses and stores our urdf file into robot_description
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        parameters=[{'use_sim_time':True,'robot_description': Command(['xacro ', urdf_desc_path])}],
        output='screen'
    )

    # create and return launch description object
    return LaunchDescription(
        [
            robot_state_publisher_node,
        ]
    )
