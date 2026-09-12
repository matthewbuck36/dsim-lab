#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Launch the selected rotating-sensor controllers.

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
    mode = LaunchConfiguration(
        'continuous_search_mode', default='stationary_v1'
    ).perform(context)
    if mode not in ('stationary_v1', 'rolling_gesc_v2'):
        raise ValueError('unsupported continuous_search_mode')
    controllers = ['joint_state_broadcaster', 'velocity_controller']
    if mode == 'rolling_gesc_v2':
        # The existing Gazebo plugin supplies the same joint on /joint_states.
        # One source avoids merging independently ordered acquisition streams.
        controllers = ['velocity_controller']
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
                arguments=controllers + [
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
    return ([spawn_joint_state_broadcaster] if mode == 'stationary_v1' else []) + [
        spawn_velocity_controller]


def generate_launch_description():
    """Keep legacy broadcasters; rolling mode uses the existing Gazebo source."""
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'controller_spawner_load_recovery_enabled',
                default_value='False',
            ),
            DeclareLaunchArgument(
                'continuous_search_mode',
                default_value='stationary_v1',
                choices=['stationary_v1', 'rolling_gesc_v2'],
            ),
            OpaqueFunction(function=_controller_spawners),
        ]
    )
