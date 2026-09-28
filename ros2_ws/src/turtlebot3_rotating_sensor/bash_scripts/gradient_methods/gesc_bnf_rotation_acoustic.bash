#!/usr/bin/env bash
set -euo pipefail
# Source the built workspace once before running this alias.
exec ros2 launch turtlebot3_rotating_sensor gazebo.launch.py \
    profile:=gesc_bnf_rotation_acoustic environment:=gazebo "$@"
