"""Start the existing Gazebo world with or without its interactive client."""

import os
from pathlib import Path
from ament_index_python.packages import get_package_prefix, get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration


def _start(context):
    gui = LaunchConfiguration("gazebo_gui").perform(context).lower() == "true"
    plugin_path = str(Path(get_package_prefix("turtlebot3_rotating_sensor")) / "lib")
    if os.environ.get("GAZEBO_PLUGIN_PATH"):
        plugin_path += os.pathsep + os.environ["GAZEBO_PLUGIN_PATH"]
    # Own server and GUI directly: the `gazebo` wrapper can exit while its
    # children continue running after launch's shutdown escalation.
    actions = [ExecuteProcess(
        cmd=["gzserver", "--verbose", "-s", "libgazebo_ros_init.so", "-s", "libgazebo_ros_factory.so",
             LaunchConfiguration("world")], output="screen",
        additional_env={"GAZEBO_PLUGIN_PATH": plugin_path, "DISPLAY": ""},
    )]
    if gui:
        actions.append(ExecuteProcess(cmd=["gzclient", "--verbose"], output="screen",
                                      additional_env={"GAZEBO_PLUGIN_PATH": plugin_path}))
    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("world", default_value=str(Path(get_package_share_directory("turtlebot3_rotating_sensor")) / "worlds" / "gazebo_empty.world")),
        DeclareLaunchArgument("gazebo_gui", default_value="true"),
        OpaqueFunction(function=_start),
    ])
