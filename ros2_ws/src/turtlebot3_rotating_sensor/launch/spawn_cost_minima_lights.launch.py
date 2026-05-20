#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Spawn light source models at minima listed in a cost function config."""

import json
import os
import re

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def _sanitize_name(value, fallback):
    """Convert arbitrary metadata labels into ROS/Gazebo-friendly name fragments."""

    sanitized = re.sub(r"[^A-Za-z0-9_]+", "_", str(value)).strip("_")
    return sanitized or fallback


def _numeric_value(entry, key, config_filepath):
    """Read a numeric minimum-coordinate value with a clear launch-time error."""

    if key not in entry:
        raise RuntimeError(
            f"Minimum entry in {config_filepath} is missing required key '{key}': {entry}"
        )

    value = entry[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeError(
            f"Minimum entry key '{key}' must be numeric in {config_filepath}: {entry}"
        )

    return float(value)


def _spawn_cost_minima_lights(context):
    cost_config_filepath = os.path.expanduser(
        LaunchConfiguration("cost_function_config_filepath").perform(context)
    )
    light_model_filepath = LaunchConfiguration("light_source_model_filepath").perform(context)
    entity_prefix = _sanitize_name(
        LaunchConfiguration("cost_minima_light_entity_prefix").perform(context),
        "cost_minimum_light",
    )

    if not os.path.isfile(cost_config_filepath):
        raise RuntimeError(f"Cost function config file not found: {cost_config_filepath}")

    with open(cost_config_filepath, mode="r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    minima = config.get("Minima")
    if not isinstance(minima, list) or not minima:
        raise RuntimeError(
            f"Cost function config must define a non-empty top-level 'Minima' list "
            f"to spawn minima lights: {cost_config_filepath}"
        )

    spawn_nodes = []
    for index, minimum in enumerate(minima):
        if not isinstance(minimum, dict):
            raise RuntimeError(
                f"Minimum entry {index} in {cost_config_filepath} must be an object: "
                f"{minimum}"
            )

        x_pos = _numeric_value(minimum, "x", cost_config_filepath)
        y_pos = _numeric_value(minimum, "y", cost_config_filepath)
        z_pos = _numeric_value(minimum, "z", cost_config_filepath)
        label = _sanitize_name(
            minimum.get("name", minimum.get("type", "minimum")),
            "minimum",
        )
        entity_name = f"{entity_prefix}_{label}_{index}"

        spawn_nodes.append(
            Node(
                package="gazebo_ros",
                executable="spawn_entity.py",
                name=f"spawn_{entity_name}",
                arguments=[
                    "-file",
                    light_model_filepath,
                    "-entity",
                    entity_name,
                    "-x",
                    str(x_pos),
                    "-y",
                    str(y_pos),
                    "-z",
                    str(z_pos),
                    "-R",
                    "0.0",
                    "-P",
                    "0.0",
                    "-Y",
                    "0.0",
                ],
                output="screen",
            )
        )

    return spawn_nodes


def generate_launch_description():
    """Create a launch description for cost-minima light source spawns."""

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "cost_function_config_filepath",
                default_value=(
                    "~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/"
                    "heavy_ball_PDE_ESC/cost_function/"
                    "gaussian_two_basin_original.json"
                ),
                description="Cost function config containing top-level Minima metadata.",
            ),
            DeclareLaunchArgument(
                "light_source_model_filepath",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("turtlebot3_rotating_sensor"),
                        "models",
                        "light_source",
                        "model.sdf",
                    ]
                ),
                description="SDF model to spawn for each configured minimum.",
            ),
            DeclareLaunchArgument(
                "cost_minima_light_entity_prefix",
                default_value="cost_minimum_light",
                description="Entity name prefix for spawned cost-minimum light sources.",
            ),
            OpaqueFunction(function=_spawn_cost_minima_lights),
        ]
    )
