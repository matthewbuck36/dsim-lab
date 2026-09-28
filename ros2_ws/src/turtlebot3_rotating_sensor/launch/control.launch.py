"""Spawn only the controllers used by the selected simulation adapter."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("joint_state_broadcaster", default_value="true"),
        Node(package="controller_manager", executable="spawner",
             arguments=["joint_state_broadcaster", "--controller-manager-timeout", "30", "--service-call-timeout", "30"],
             condition=IfCondition(LaunchConfiguration("joint_state_broadcaster")), output="screen"),
        Node(package="controller_manager", executable="spawner",
             arguments=["velocity_controller", "--controller-manager-timeout", "30", "--service-call-timeout", "30"],
             output="screen"),
    ])
