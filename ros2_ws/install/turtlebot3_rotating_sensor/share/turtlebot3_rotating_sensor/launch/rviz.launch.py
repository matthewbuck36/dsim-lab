#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This script is used to visualize the robot model in an RVIZ simulation.
A RVIZ configuration file will be used to load in pre-set RVIZ settings, then
a joint state publisher will be launched to setup the robot's joints.
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import ExecuteProcess

def generate_launch_description():
    """This function creates a launch description for rviz and the joint state publisher."""

    # Get the package description
    package_description = "turtlebot3_rotating_sensor"

    # RVIZ node
    rviz_config_dir = os.path.join(
        get_package_share_directory(package_description),
        'rviz_config', 'urdf_vis.rviz'
        )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        name='rviz_node',
        parameters=[{'use_sim_time':True}],
        arguments=['-d',rviz_config_dir]
    )

    # Joint state publisher
    joint_state_publisher = ExecuteProcess(
        cmd=['ros2','run','joint_state_publisher','joint_state_publisher'],
        output='screen'
    )

    # Create and return launch description object
    return LaunchDescription(
        [
            joint_state_publisher,
            rviz_node,
        ]
    )
