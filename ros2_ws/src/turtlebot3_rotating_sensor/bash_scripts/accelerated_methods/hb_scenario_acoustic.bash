#!/bin/bash

# Generic HBESC scenario runner.
# Usage:
#   bash hb_scenario_acoustic.bash
#   bash hb_scenario_acoustic.bash --dry-run
#   bash hb_scenario_acoustic.bash ~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/reference_runs/hb_multi_fill_default.json
#   bash hb_scenario_acoustic.bash --dry-run ~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/reference_runs/hb_multi_fill_default.json

set -eo pipefail

DRY_RUN="False"
if [ "${1:-}" = "--dry-run" ] || [ "${1:-}" = "--print-args" ]; then
  DRY_RUN="True"
  shift
fi

SCENARIO="${1:-~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/reference_runs/hb_gaussian_fill_default.json}"
SCENARIO="${SCENARIO/#\~/$HOME}"

if [ ! -f "${SCENARIO}" ]; then
  echo "Scenario file not found: ${SCENARIO}" >&2
  exit 2
fi

echo "Running HBESC scenario: ${SCENARIO}"

python3 - "${SCENARIO}" <<'PY'
import json
import sys
from pathlib import Path

scenario_path = Path(sys.argv[1]).expanduser()
with scenario_path.open("r", encoding="utf-8") as handle:
    scenario = json.load(handle)

name = scenario.get("name", scenario_path.stem)
description = scenario.get("description", "")
print(f"Scenario name: {name}")
if description:
    print(f"Description: {description}")
PY

mapfile -t LAUNCH_ARGS < <(
python3 - "${SCENARIO}" <<'PY'
import json
import sys
from pathlib import Path

scenario_path = Path(sys.argv[1]).expanduser()
with scenario_path.open("r", encoding="utf-8") as handle:
    scenario = json.load(handle)

launch = scenario.get("launch", {})
if not isinstance(launch, dict):
    print("Scenario must contain a 'launch' object.", file=sys.stderr)
    sys.exit(2)

launch_arg_order = [
    "entity_name",
    "init_x_position",
    "init_y_position",
    "init_z_position",
    "init_roll_angle",
    "init_pitch_angle",
    "init_yaw_angle",
    "joint_name_1",
    "input_encoder_data_to_filter",
    "live_plot_mode",
    "show_cost_surface_plot",
    "cost_surface_x_min",
    "cost_surface_x_max",
    "cost_surface_y_min",
    "cost_surface_y_max",
    "cost_surface_resolution",
    "cost_surface_orientation_mode",
    "cost_surface_z_scale_mode",
    "cost_surface_show_base_wireframe",
    "cost_surface_live",
    "cost_surface_odom_topic",
    "cost_surface_fill_topic",
    "cost_surface_refresh_hz",
    "cost_surface_trajectory_period",
    "use_pde_extensions",
    "escape_policy",
    "pde_omega",
    "convergence_threshold",
    "convergence_decay_rate",
    "convergence_min_fill_periods",
    "gaussian_fill_amplitude",
    "gaussian_fill_min_sigma",
    "gaussian_fill_max_sigma",
    "gaussian_fill_min_points",
    "gaussian_fill_use_recent_fraction",
    "gaussian_fill_max_fills",
    "gaussian_fill_cooldown_sec",
    "gaussian_fill_min_distance_between_fills",
    "number_of_lights",
    "light_source_1_entity_name",
    "light_source_1_model_filepath",
    "light_1_x",
    "light_1_y",
    "light_source_1_z",
    "light_source_1_roll",
    "light_source_1_pitch",
    "light_source_1_yaw",
    "light_1_intensity_lumens",
    "light_source_2_entity_name",
    "light_source_2_model_filepath",
    "light_2_x",
    "light_2_y",
    "light_source_2_z",
    "light_source_2_roll",
    "light_source_2_pitch",
    "light_source_2_yaw",
    "light_2_intensity_lumens",
    "light_source_3_entity_name",
    "light_source_3_model_filepath",
    "light_3_x",
    "light_3_y",
    "light_source_3_z",
    "light_source_3_roll",
    "light_source_3_pitch",
    "light_source_3_yaw",
    "light_3_intensity_lumens",
    "light_source_4_entity_name",
    "light_source_4_model_filepath",
    "light_4_x",
    "light_4_y",
    "light_source_4_z",
    "light_source_4_roll",
    "light_source_4_pitch",
    "light_source_4_yaw",
    "light_4_intensity_lumens",
    "light_source_5_entity_name",
    "light_source_5_model_filepath",
    "light_5_x",
    "light_5_y",
    "light_source_5_z",
    "light_source_5_roll",
    "light_source_5_pitch",
    "light_source_5_yaw",
    "light_5_intensity_lumens",
    "rotate_frame_config_filepath",
    "sensor_transform_config_filepath",
    "cost_function_config_filepath",
    "filter_config_filepath",
    "controller_config_filepath",
    "data_collection_filepath",
]

known = set(launch_arg_order)
unknown = sorted(set(launch) - known)
if unknown:
    print(
        "Unknown launch keys in scenario: " + ", ".join(unknown),
        file=sys.stderr,
    )
    sys.exit(2)

for key in launch_arg_order:
    if key not in launch:
        continue
    value = launch[key]
    if isinstance(value, bool):
        value = "True" if value else "False"
    elif value is None:
        value = ""
    else:
        value = str(value)
    print(f"{key}:={value}")
PY
)

if [ "${DRY_RUN}" = "True" ]; then
  printf 'ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml'
  for arg in "${LAUNCH_ARGS[@]}"; do
    printf ' %q' "${arg}"
  done
  printf '\n'
  exit 0
fi

cd ~/dsim-lab/ros2_ws

colcon build --packages-select ros_esc ros_esc_interfaces turtlebot3_rotating_sensor

source install/setup.bash

ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml "${LAUNCH_ARGS[@]}"
