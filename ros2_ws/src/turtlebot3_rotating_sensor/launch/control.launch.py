#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Launch the two rotating-sensor controllers.

The controllers rotate
the sensor frame in simulation. The joint state broadcaster will publish
the joint state, while the velocity controller will accept velocity commands
and then move the revolute joints where the sensor frame is attached.

The joint state broadcaster and velocity controllers are configured in
a yaml file within the this package. This file states what joints are
controlled, and the type of commands accepted (in this case, a velocity
command).

To check the active controllers with an active gazebo simulation use the
following command in a separate terminal: ros2 control list_controllers
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Generate a launch description for the two controllers."""
    spawn_joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--service-call-timeout',
            '30.0',
        ],
        output='screen',
    )

    spawn_velocity_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'velocity_controller',
            '--service-call-timeout',
            '30.0',
        ],
        output='screen',
    )

    # Create and return launch description object
    return LaunchDescription(
        [
            spawn_joint_state_broadcaster,
            spawn_velocity_controller,
        ]
    )
