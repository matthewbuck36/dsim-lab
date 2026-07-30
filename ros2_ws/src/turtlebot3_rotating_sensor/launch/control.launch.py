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
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _enabled(value):
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


def _controller_spawners(context):
    recovery_enabled = _enabled(
        LaunchConfiguration(
            'controller_spawner_load_recovery_enabled'
        ).perform(context)
    )
    if recovery_enabled:
        return [
            Node(
                package='turtlebot3_rotating_sensor',
                executable='idempotent_controller_spawner.py',
                arguments=[
                    'joint_state_broadcaster',
                    'velocity_controller',
                    '--service-call-timeout',
                    '30.0',
                ],
                output='screen',
            )
        ]

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
    return [
        spawn_joint_state_broadcaster,
        spawn_velocity_controller,
    ]


def generate_launch_description():
    """Generate a launch description for the two controllers."""
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'controller_spawner_load_recovery_enabled',
                default_value='False',
            ),
            OpaqueFunction(function=_controller_spawners),
        ]
    )
