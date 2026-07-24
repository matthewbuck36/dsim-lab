#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Publish the robot's URDF.

Launch files use this description for RViz or Gazebo simulation.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Publish the URDF on `/robot_description`."""
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
        parameters=[{
            'use_sim_time': True,
            'robot_description': Command([
                'xacro ', urdf_desc_path,
                ' simulation_contacts_enabled:=',
                LaunchConfiguration('simulation_contacts_enabled'),
                ' simulation_contacts_topic:=',
                LaunchConfiguration('simulation_contacts_topic'),
            ]),
        }],
        output='screen'
    )

    # create and return launch description object
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'simulation_contacts_enabled',
                default_value='False',
            ),
            DeclareLaunchArgument(
                'simulation_contacts_topic',
                default_value='/gesc_gaussian/simulation/contacts',
            ),
            robot_state_publisher_node,
        ]
    )
