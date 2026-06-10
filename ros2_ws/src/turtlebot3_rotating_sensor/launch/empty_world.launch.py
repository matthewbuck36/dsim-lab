#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This script is used to launch an empty gazebo world."""

import os
from ament_index_python.packages import get_package_share_directory
from ament_index_python.packages import get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess

def generate_launch_description():
    """This function creates a launch description for an empty gazebo world."""

    pkg_tb_gazebo = get_package_share_directory('turtlebot3_rotating_sensor')

    # We get the whole install dir
    # We do this to avoid having to copy or softlink
    # manually the packages so that gazebo can find them
    description_package_name = "turtlebot3_rotating_sensor"
    install_dir = get_package_prefix(description_package_name)

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH']+':'+install_dir+'/lib'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    headless = os.environ.get('HBESC_GAZEBO_HEADLESS', '').lower() in [
        '1', 'true', 'yes', 'on'
    ]
    gazebo_executable = 'gzserver' if headless else 'gazebo'

    # Launch Gazebo. Normal launches keep the historical GUI-capable gazebo
    # command; batch headless runs set HBESC_GAZEBO_HEADLESS=1 to use gzserver.
    # Note adding in a -u tag before worlds/empty.world
    # means gazebo will be paused when it launches
    gazebo_launch = ExecuteProcess(
        cmd=[gazebo_executable, '--verbose',
             '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so',
             'worlds/gazebo_empty.world'],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
          'world',
          default_value=[os.path.join(pkg_tb_gazebo, 'worlds', 'gazebo_empty.world'), ''],
          description='SDF world file'),
        gazebo_launch
    ])
