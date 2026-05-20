#!/bin/bash

# Baseline HBESC momentum-escape test with selectable local-well depth.
# Usage:
#   bash hb_escape_shallow_acoustic.bash A3p0 near0
#   bash hb_escape_shallow_acoustic.bash A2p0 near0p5
#   bash hb_escape_shallow_acoustic.bash A1p0 near1
#   bash hb_escape_shallow_acoustic.bash globalW30 near1
#   bash hb_escape_shallow_acoustic.bash original far
#   bash hb_escape_shallow_acoustic.bash A2p0 0.5 0.5

set -e

VARIANT="${1:-A2p0}"
START_PRESET="${2:-near0}"
COST_DIR="~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function"

case "${VARIANT}" in
  original|A4p0|4|4.0)
    COST_CONFIG="${COST_DIR}/gaussian_two_basin_original.json"
    ;;
  A3p0|3|3.0)
    COST_CONFIG="${COST_DIR}/gaussian_two_basin_localA3p0.json"
    ;;
  A2p0|2|2.0)
    COST_CONFIG="${COST_DIR}/gaussian_two_basin_localA2p0.json"
    ;;
  A1p0|1|1.0)
    COST_CONFIG="${COST_DIR}/gaussian_two_basin_localA1p0.json"
    ;;
  globalW25|W25|25)
    COST_CONFIG="${COST_DIR}/gaussian_two_basin_globalW25.json"
    ;;
  globalW30|W30|30)
    COST_CONFIG="${COST_DIR}/gaussian_two_basin_globalW30.json"
    ;;
  globalW40|W40|40)
    COST_CONFIG="${COST_DIR}/gaussian_two_basin_globalW40.json"
    ;;
  *)
    echo "Unknown variant '${VARIANT}'." >&2
    echo "Use one of: original, A3p0, A2p0, A1p0, globalW25, globalW30, globalW40" >&2
    exit 2
    ;;
esac

if [ "$#" -ge 3 ]; then
  INIT_X="$2"
  INIT_Y="$3"
elif [ "$#" -eq 2 ]; then
  case "${START_PRESET}" in
    near0|0|0,0)
      INIT_X=0
      INIT_Y=0
      ;;
    near0p5|0.5|0.5,0.5)
      INIT_X=0.5
      INIT_Y=0.5
      ;;
    near1|1|1,1)
      INIT_X=1
      INIT_Y=1
      ;;
    far|-2|-2,-2)
      INIT_X=-2
      INIT_Y=-2
      ;;
    *)
      echo "Unknown start preset '${START_PRESET}'." >&2
      echo "Use one of: near0, near0p5, near1, far, or pass numeric x y." >&2
      exit 2
      ;;
  esac
else
  INIT_X=0
  INIT_Y=0
fi

echo "Running baseline HBESC escape test with cost config: ${COST_CONFIG}"
echo "Initial position: (${INIT_X}, ${INIT_Y})"

cd ~/dsim-lab/ros2_ws

colcon build --packages-select ros_esc ros_esc_interfaces turtlebot3_rotating_sensor

source install/setup.bash

ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
entity_name:='turtlebot3' \
init_x_position:="${INIT_X}" \
init_y_position:="${INIT_Y}" \
init_yaw_angle:=0 \
input_encoder_data_to_filter:='True' \
live_plot_mode:='2D' \
use_pde_extensions:='False' \
escape_policy:='none' \
rotate_frame_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json' \
sensor_transform_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json' \
cost_function_config_filepath:="${COST_CONFIG}" \
filter_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json' \
controller_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/hbesc_baseline_real_full_rotation.json' \
data_collection_filepath:='~/Experiments/Gazebo-Simulations'
