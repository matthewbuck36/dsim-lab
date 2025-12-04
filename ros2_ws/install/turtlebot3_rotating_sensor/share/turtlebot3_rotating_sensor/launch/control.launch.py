#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This script is used to launch two controllers that are used to rotate
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


from launch_ros.actions import Node
from launch import LaunchDescription

def generate_launch_description():
    """This function generates a launch description for two controllers."""

    spawn_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )

    spawn_velocity_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["velocity_controller"],
        output="screen",
    )

    # Create and return launch description object
    return LaunchDescription(
        [
            spawn_joint_state_broadcaster,
            spawn_velocity_controller,
        ]
    )
