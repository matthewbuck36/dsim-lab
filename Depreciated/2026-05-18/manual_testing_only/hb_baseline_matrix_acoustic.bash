#!/bin/bash

# Run or preview the focused baseline Heavy-Ball ESC test matrix.
# Usage:
#   bash hb_baseline_matrix_acoustic.bash --dry-run
#   bash hb_baseline_matrix_acoustic.bash
#
# Each scenario disables PDE/Gaussian extensions. Running the full matrix can
# take several hours because the scenarios are intentionally empirical tests.

set -eo pipefail

DRY_RUN="False"
if [ "${1:-}" = "--dry-run" ] || [ "${1:-}" = "--print-args" ]; then
  DRY_RUN="True"
  shift
fi

RUNNER="$HOME/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash"
SCENARIO_DIR="$HOME/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/baseline_tests"

SCENARIOS=(
  "Q1_quadratic_start0_real.json"
  "Q2_quadratic_start6_real.json"
  "Q3_quadratic_start8_real.json"
  "R1_quartic_start0_real.json"
  "R2_quartic_start6_real.json"
  "R3_quartic_start8_real.json"
  "W1_double_well_start1_slow.json"
  "W2_double_well_start1_real.json"
  "W3_double_well_start1_fast.json"
  "G1_globalW40_start1_slow.json"
  "G2_globalW40_start1_real.json"
  "G3_globalW40_start1_fast.json"
  "H1_original_start0_slow.json"
  "H2_original_start0_real.json"
  "H3_original_start0_fast.json"
)

for scenario in "${SCENARIOS[@]}"; do
  scenario_path="${SCENARIO_DIR}/${scenario}"
  echo "================================================================"
  echo "Baseline HBESC matrix scenario: ${scenario}"
  echo "================================================================"

  if [ "${DRY_RUN}" = "True" ]; then
    bash "${RUNNER}" --dry-run "${scenario_path}"
  else
    bash "${RUNNER}" "${scenario_path}"
  fi
done
