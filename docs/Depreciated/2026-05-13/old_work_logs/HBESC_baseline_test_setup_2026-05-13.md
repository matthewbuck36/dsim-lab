# HBESC Baseline Test Setup - 2026-05-13

This file records the setup added for the professor's baseline Heavy-Ball ESC
assignment. These tests intentionally disable Gaussian fill and PDE extensions.

## Goal

Test baseline Heavy-Ball ESC on different cost functions and report how speed
limits, local minima, and plateau-like gradients affect convergence and escape.

Every baseline test scenario uses:

```json
"use_pde_extensions": false,
"escape_policy": "none"
```

## Cost Configs Added

Directory:

`ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/`

Added:

```text
hb_quadratic_bowl.json
hb_quartic_bowl.json
hb_quartic_double_well.json
```

Quadratic bowl:

```text
J = 0.05*((x-10)^2 + (y-10)^2)
```

Quartic bowl:

```text
J = 0.0005*((x-10)^4 + (y-10)^4)
```

Quartic double-well:

```text
u = (x+y)/2
J = 0.01*(u-2)^2*(u-10)^2 + 0.0125*(x-y)^2 - 0.005*u
```

## Controller Variants Added

Directory:

`ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/`

Added:

```text
heavyball_escape_controller_slow_full_rotation.json
heavyball_escape_controller_real_full_rotation.json
heavyball_escape_controller_fast_full_rotation.json
```

All three keep the same baseline HeavyBall tuning:

```json
"k_vx": 0.2,
"k_wz": 2.0,
"k": 1.0,
"beta": 0.1,
"input_gain": -1.0
```

Speed variants:

```text
slow: set_max_vx = 0.05, set_max_wz = 0.25
real: set_max_vx = null, set_max_wz = 0.75
fast: set_max_vx = 0.40, set_max_wz = 1.25
```

The fast case is simulation-only and should not be claimed as physically valid.

## Scenario Matrix Added

Directory:

`ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/baseline_tests/`

Added 15 scenario files:

```text
Q1_quadratic_start0_real.json
Q2_quadratic_start6_real.json
Q3_quadratic_start8_real.json
R1_quartic_start0_real.json
R2_quartic_start6_real.json
R3_quartic_start8_real.json
W1_double_well_start1_slow.json
W2_double_well_start1_real.json
W3_double_well_start1_fast.json
G1_globalW40_start1_slow.json
G2_globalW40_start1_real.json
G3_globalW40_start1_fast.json
H1_original_start0_slow.json
H2_original_start0_real.json
H3_original_start0_fast.json
```

All write experiment outputs to:

```text
~/Experiments/HBESC-Baseline-Tests
```

## Runner Added

File:

`ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_baseline_matrix_acoustic.bash`

Preview the whole matrix:

```bash
bash ~/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_baseline_matrix_acoustic.bash --dry-run
```

Run one scenario manually:

```bash
bash ~/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash \
  ~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/baseline_tests/Q1_quadratic_start0_real.json
```

## Analysis and Report Files Added

Manifest:

`ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/baseline_hb_run_manifest.csv`

After each run, paste the generated `Test_YYYY-MM-DD_HH-MM-SS` folder into the
matching row's `run_folder` column.

Analysis script:

`ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/analysis/analyze_baseline_hb_logs.py`

Run after manifest entries are filled:

```bash
python3 ~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/analysis/analyze_baseline_hb_logs.py --plots
```

Report skeleton:

`ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/report/baseline_hb_report.tex`

## Validation

Passed:

```bash
python3 -c 'import json, pathlib; roots=[...]; [json.load(open(path, encoding="utf-8")) for path in paths]'
```

Result:

```text
json ok: 30 files
```

Passed:

```bash
python3 -m py_compile ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/analysis/analyze_baseline_hb_logs.py
```

Passed:

```bash
bash -n ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_baseline_matrix_acoustic.bash
bash -n ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash
```

Passed:

```bash
bash ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_baseline_matrix_acoustic.bash --dry-run
```

This expanded all 15 baseline scenarios without launching Gazebo.

Passed:

```bash
python3 ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/analysis/analyze_baseline_hb_logs.py
```

With blank `run_folder` entries, the script skipped all 15 tests as expected.

Passed:

```bash
python3 -c 'from sympy.parsing.sympy_parser import parse_expr; ...'
```

Result:

```text
sympy expressions ok
```

Passed:

```bash
git diff --check
```

Passed:

```bash
cd ~/dsim-lab/ros2_ws
colcon build --packages-select ros_esc ros_esc_interfaces turtlebot3_rotating_sensor
```

Build result:

```text
Summary: 3 packages finished
```

Not run:

```text
pdflatex baseline_hb_report.tex
```

Reason:

```text
pdflatex is not installed in this environment.
```
