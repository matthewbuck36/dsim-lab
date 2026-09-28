"""Gazebo adapters plus one named ESC profile; plotting and bags are observers."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, LogInfo, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from ros_esc.profiles import resolve_profile


def _boolean(value):
    value = str(value).lower()
    if value not in ("true", "false"):
        raise ValueError(f"expected true or false, got {value!r}")
    return value == "true"


def algorithm_commands(profile):
    """Pure legacy adapter argv; useful for parity checks without launching ROS."""
    t, c = profile["topics"], profile["config_paths"]
    commands = [
        ["encoder_node", t["joints"], t["timekeeper"], t["encoder"], "--joint_names", "rotating_frame_joint"],
        ["rotate_frame_node", t["encoder"], t["timekeeper"], c["rotation"]],
        ["sensor_pose_node", t["pose"], t["encoder"], t["timekeeper"], t["sensor"], c["sensor"]],
        ["cost_function_node", t["sensor"], t["timekeeper"], t["cost"], c["cost"]],
    ]
    if profile["algorithm"] == "gesc_v3":
        commands[-1] += ["--sample-rate-hz", str(profile["v3"]["sample_rate_hz"])]
    else:
        clock = str(profile["use_sim_time"])
        commands += [
            ["filter_node", t["cost"], t["encoder"], t["timekeeper"], t["filter"],
             "--filter_file", c["filter"], "--append_encoder_data", str(profile["append_encoder"]),
             "--use-sim-time", clock],
            ["controller_node", t["filter"], t["pose"], t["timekeeper"], t["control"], t["command"],
             c["controller"], "--use-sim-time", clock],
        ]
    return commands


def _launch(context):
    get = lambda key: LaunchConfiguration(key).perform(context)
    profile = resolve_profile(get("profile"), get("environment"))
    if profile["mode"] != "simulation":
        raise ValueError("Gazebo launch requires environment=gazebo; physical adapters remain in the external physical workspace")
    gui = _boolean(get("gui"))
    plot_value = get("plot")
    plotting = gui and (profile["plot"] if plot_value == "auto" else _boolean(plot_value))
    recording = _boolean(get("record"))
    share = Path(get_package_share_directory("turtlebot3_rotating_sensor"))
    world = Path(profile["world"])
    if not world.is_absolute():
        world = share / "worlds" / world
    if not world.is_file():
        raise FileNotFoundError(f"world is unavailable: {world}")

    def include(name, **arguments):
        return IncludeLaunchDescription(
            PythonLaunchDescriptionSource(str(share / "launch" / name)),
            launch_arguments={key: str(value) for key, value in arguments.items()}.items(),
        )

    start = profile["start"]
    actions = [
        LogInfo(msg="Resolved ESC profile: " + json.dumps(profile, sort_keys=True)),
        include("empty_world.launch.py", world=world, gazebo_gui=gui),
        include("robot_description.launch.py", simulation_sensor_update_rate_hz=profile["sensor_support_rate_hz"]),
        include("control.launch.py", joint_state_broadcaster=profile["algorithm"] != "gesc_v3"),
        Node(package="gazebo_ros", executable="spawn_entity.py", arguments=[
            "-topic", "/robot_description", "-entity", profile["entity"],
            "-x", str(start["x"]), "-y", str(start["y"]), "-Y", str(start["yaw"]),
        ], output="screen"),
    ]
    actions.extend(ExecuteProcess(cmd=["ros2", "run", "ros_esc", *command], output="screen")
                   for command in algorithm_commands(profile))
    if profile["algorithm"] == "gesc_v3":
        parameters = {"profile": get("profile"), "environment": get("environment"), "use_sim_time": True}
        actions += [
            Node(package="ros_esc", executable="sensor_observation_node", parameters=[parameters], output="screen"),
            Node(package="ros_esc", executable="controller_node", arguments=["--v3"], parameters=[parameters], output="screen"),
        ]
    if plotting:
        actions.append(ExecuteProcess(cmd=["ros2", "run", "ros_esc", "live_plot_node", "--mode", "2D",
                                           "--odom-topic", profile["topics"]["pose"],
                                           "--cost-topic", profile["topics"]["cost"]], output="screen"))
    if recording:
        run_name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ") + f"-{os.getpid()}"
        output = Path(get("output")).expanduser() / run_name
        actions.append(ExecuteProcess(cmd=["ros2", "run", "ros_esc", "record_bag", "--output", str(output),
                                           "--environment", "simulation"], output="screen",
                                      sigterm_timeout="12.0", sigkill_timeout="2.0"))
    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("profile", default_value="gesc_v3", description="Installed algorithm name or custom profile JSON"),
        DeclareLaunchArgument("environment", default_value="gazebo", description="Environment profile; this launch requires gazebo"),
        DeclareLaunchArgument("gui", default_value="true", choices=["true", "false"]),
        DeclareLaunchArgument("plot", default_value="auto", choices=["auto", "true", "false"]),
        DeclareLaunchArgument("record", default_value="true", choices=["true", "false"]),
        DeclareLaunchArgument("output", default_value="~/Experiments/ESC", description="Optional rosbag output directory"),
        OpaqueFunction(function=_launch),
    ])
