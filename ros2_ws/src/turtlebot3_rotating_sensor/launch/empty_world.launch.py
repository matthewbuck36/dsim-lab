#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This script is used to launch an empty gazebo world."""

import os
from ament_index_python.packages import get_package_share_directory
from ament_index_python.packages import get_package_prefix
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import PythonExpression
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    """This function creates a launch description for an empty gazebo world."""

    pkg_tb_gazebo = get_package_share_directory('turtlebot3_rotating_sensor')

    # We get the whole install dir
    # We do this to avoid having to copy or softlink
    # manually the packages so that gazebo can find them
    description_package_name = "turtlebot3_rotating_sensor"
    install_dir = get_package_prefix(description_package_name)

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = (
            os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_dir + '/lib'
        )
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    # Launch Gazebo
    # Note adding in a -u tag before worlds/empty.world
    # means gazebo will be paused when it launches
    gui_enabled = [
        "'", LaunchConfiguration('gazebo_gui'),
        "'.lower() in ('true', '1')",
    ]
    seed_enabled = [
        "'", LaunchConfiguration('gazebo_use_random_seed'),
        "'.lower() in ('true', '1')",
    ]
    gazebo_launch = ExecuteProcess(
        cmd=['gazebo', '--verbose',
             '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so',
             LaunchConfiguration('world')],
        output='screen',
        condition=IfCondition(
            PythonExpression(
                [*gui_enabled, ' and not (', *seed_enabled, ')']
            )
        ),
    )
    seeded_gazebo_launch = ExecuteProcess(
        cmd=['gazebo', '--verbose',
             '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so',
             '--seed', LaunchConfiguration('gazebo_random_seed'),
             LaunchConfiguration('world')],
        output='screen',
        condition=IfCondition(
            PythonExpression(
                ['(', *gui_enabled, ') and (', *seed_enabled, ')']
            )
        ),
    )
    gzserver_launch = ExecuteProcess(
        cmd=['gzserver', '--verbose',
             '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so',
             LaunchConfiguration('world')],
        output='screen',
        additional_env={'DISPLAY': ''},
        condition=IfCondition(
            PythonExpression(
                ['not (', *gui_enabled, ') and not (', *seed_enabled, ')']
            )
        ),
    )
    seeded_gzserver_launch = ExecuteProcess(
        cmd=['gzserver', '--verbose',
             '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so',
             '--seed', LaunchConfiguration('gazebo_random_seed'),
             LaunchConfiguration('world')],
        output='screen',
        additional_env={'DISPLAY': ''},
        condition=IfCondition(
            PythonExpression(
                ['not (', *gui_enabled, ') and (', *seed_enabled, ')']
            )
        ),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=[
                os.path.join(pkg_tb_gazebo, 'worlds', 'gazebo_empty.world'), ''
            ],
            description='SDF world file'),
        DeclareLaunchArgument(
            'gazebo_gui', default_value='True',
            description='Start Gazebo server with its GUI client'),
        DeclareLaunchArgument(
            'gazebo_use_random_seed', default_value='False',
            description='Pass an explicit deterministic seed to Gazebo'),
        DeclareLaunchArgument(
            'gazebo_random_seed', default_value='0',
            description='Gazebo random seed when enabled'),
        gazebo_launch,
        seeded_gazebo_launch,
        gzserver_launch,
        seeded_gzserver_launch,
    ])
