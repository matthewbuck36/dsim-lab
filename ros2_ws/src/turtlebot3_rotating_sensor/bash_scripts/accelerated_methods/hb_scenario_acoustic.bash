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
    "include_light_source",
    "light_source_entity_name",
    "light_source_model_filepath",
    "light_source_x",
    "light_source_y",
    "light_source_z",
    "light_source_roll",
    "light_source_pitch",
    "light_source_yaw",
    "include_light_source_2",
    "light_source_2_entity_name",
    "light_source_2_model_filepath",
    "light_source_2_x",
    "light_source_2_y",
    "light_source_2_z",
    "light_source_2_roll",
    "light_source_2_pitch",
    "light_source_2_yaw",
    "rotate_frame_config_filepath",
    "sensor_transform_config_filepath",
    "cost_function_config_filepath",
    "filter_config_filepath",
    "controller_config_filepath",
    "data_collection_filepath",
    "world",
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
