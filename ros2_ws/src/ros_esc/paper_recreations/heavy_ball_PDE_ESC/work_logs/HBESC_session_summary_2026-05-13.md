# HBESC Session Summary - 2026-05-13

This document consolidates the two previous 2026-05-13 work logs and the
follow-up chat context from the same day. The old split logs were moved to:

```text
Depreciated/2026-05-13/old_work_logs/
```

## Starting Context

- The workspace was `/home/mattb/dsim-lab`.
- The Heavy-Ball ESC stack already had two validated modes:
  - baseline HBESC with `use_pde_extensions:=False`
  - HBESC plus Gaussian fill with `use_pde_extensions:=True`
- The working goal changed from one-off HeavyBall runs to a more modular,
  scenario-driven setup that can handle different cost maps, starts,
  controller settings, and escape policies.

## Gaussian-Fill Generalization

The Gaussian-fill node was changed from hard-coded one-shot behavior into a
configurable escape-policy component.

Updated file:

```text
ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py
```

Supported policies:

```text
none
conditional_gaussian_fill
multi_gaussian_fill
```

New fill-control parameters:

```text
max_fills
fill_cooldown_sec
min_distance_between_fills
max_sigma
min_points
```

Behavior summary:

- `none`: publish no fills.
- `conditional_gaussian_fill`: preserve known-good one-fill behavior when
  `max_fills` is `1`.
- `multi_gaussian_fill`: allow repeated basin-memory fills, bounded by
  `max_fills`, cooldown, and duplicate-distance checks.

The fill message remained compatible with `modified_cost_node`:

```text
/cost_bias data = [A, mu_x, mu_y, sigma]
```

## Launch and Scenario Support

Updated launch file:

```text
ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml
```

New launch args exposed the Gaussian-fill policy and limits:

```text
escape_policy
gaussian_fill_max_sigma
gaussian_fill_min_points
gaussian_fill_max_fills
gaussian_fill_cooldown_sec
gaussian_fill_min_distance_between_fills
```

Important separation:

- `use_pde_extensions` decides whether the PDE/modified-cost/fill nodes launch.
- `escape_policy` decides what the Gaussian-fill node does after it launches.

This preserves a clean baseline mode:

```json
"use_pde_extensions": false,
"escape_policy": "none"
```

## Scenario Runner

Active runner path:

```text
ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash
```

Purpose:

- Run an HBESC experiment from one scenario JSON.
- Keep map, start pose, controller, escape policy, and logging path together.
- Avoid making a new bash file for every experiment.

Default reference scenarios now live in:

```text
ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/reference_runs/
```

Reference scenarios:

```text
hb_gaussian_fill_default.json
hb_multi_fill_default.json
hb_baseline_globalW40.json
```

The first attempted scenario run exposed a shell issue:

```text
install/setup.bash: line 11: COLCON_TRACE: unbound variable
```

Cause:

- `hb_scenario_acoustic.bash` originally used `set -u`.
- Colcon setup scripts can reference `COLCON_TRACE` while it is unset.

Fix:

```text
set -eo pipefail
```

## Reference Run Observations

Gaussian-fill default:

- Run folder: `Test_2026-05-13_10-22-02`
- Converged near `(10,10)`.
- One Gaussian fill was published near the local basin around `(2,2)`.
- Later convergence events were harmless because `max_fills=1`.

Baseline `globalW40`:

- Run folder: `Test_2026-05-13_10-40-22`
- Baseline HBESC reached the global basin without PDE/Gaussian fill.
- It circled wider around `(10,10)` than the conservative Gaussian-fill run.

Multi-fill default:

- Run folder: `Test_2026-05-13_10-50-03`
- The multi-fill machinery worked.
- A later fill was published near the global minimum, which is undesirable for
  a polished future policy.
- Follow-up idea: add a smarter guard so fills are not injected after reaching a
  good basin or after best-cost improvement has stabilized.

## Baseline Professor Assignment Setup

The clarified assignment was to test baseline Heavy-Ball only, without
Gaussian/PDE extensions, on quadratic, quartic, plateau-like, and local-escape
maps.

All assignment scenarios use:

```json
"use_pde_extensions": false,
"escape_policy": "none"
```

### Cost Configs

Active cost-function layout:

```text
cost_function/
  gaussian_two_basin/
    original_local_min.json
    shallow_local_A1p0.json
    shallow_local_A2p0.json
    shallow_local_A3p0.json
    wide_global_W25.json
    wide_global_W30.json
    wide_global_W40.json
  polynomial/
    quadratic_bowl_center10.json
    quartic_bowl_center10.json
    quartic_double_well_2_10.json
```

Polynomial costs:

```text
quadratic: J = 0.05*((x-10)^2 + (y-10)^2)
quartic:   J = 0.0005*((x-10)^4 + (y-10)^4)
double:    J = 0.01*(u-2)^2*(u-10)^2 + 0.0125*(x-y)^2 - 0.005*u
           u = (x+y)/2
```

### Controller Configs

Active HeavyBall controller layout:

```text
ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/
turtlebot_vehicle/accelerated_methods/
```

Active files:

```text
hbesc_gaussian_conservative_full_rotation.json
hbesc_baseline_slow_full_rotation.json
hbesc_baseline_real_full_rotation.json
hbesc_baseline_fast_sim_full_rotation.json
```

Baseline tuning was fixed across speed tests:

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

The fast case is simulation-only and should not be described as physically
valid TurtleBot behavior.

## Fifteen Manual Baseline Runs

The scenarios remain in:

```text
ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/baseline_tests/
```

Run groups:

- Q1-Q3: quadratic bowl from `(0,0)`, `(6,6)`, `(8,8)` at real speed.
- R1-R3: quartic bowl from `(0,0)`, `(6,6)`, `(8,8)` at real speed.
- W1-W3: quartic double-well from `(1,1)` at slow, real, and fast speeds.
- G1-G3: widened Gaussian global basin from `(1,1)` at slow, real, and fast speeds.
- H1-H3: original two-basin map from `(0,0)` at slow, real, and fast speeds.

Matt ran all 15 scenarios manually in Gazebo to watch the robot and live plots.
The run folders were entered in:

```text
~/dsim-lab/writing/heavy_ball_PDE_ESC/baseline_hb_report/baseline_hb_run_manifest.csv
```

The analyzer generated:

```text
~/dsim-lab/writing/heavy_ball_PDE_ESC/baseline_hb_report/baseline_hb_metrics.csv
~/dsim-lab/writing/heavy_ball_PDE_ESC/baseline_hb_report/figures/
```

## Baseline Results Summary

Single-well maps:

- Quadratic and quartic bowls all moved toward `(10,10)`.
- The robot settled into a bounded orbit rather than an exact point.
- The quartic near-start case showed plateau behavior: weaker control effort,
  no speed saturation, and slower near-minimum progress.

Speed-limit and local-escape maps:

- On `wide_global_W40.json`, slow speed stayed near the local basin, physical
  speed escaped to the global basin, and fast simulation-only speed escaped but
  circled/overshot more.
- On `original_local_min.json`, all slow/real/fast baseline runs failed to
  reach the global basin.
- On `quartic_double_well_2_10.json`, all slow/real/fast runs remained trapped
  near the local basin around `(2,2)`.

Main conclusion:

- Baseline Heavy-Ball ESC can work well on smooth single-well maps and can
  escape some favorable local-basin geometries when physical speed is enough.
- It is not reliable on harder local-minimum or plateau-like geometries without
  an escape mechanism such as Gaussian fill.

## Report

Updated report:

```text
~/dsim-lab/writing/heavy_ball_PDE_ESC/baseline_hb_report/baseline_hb_report.tex
```

The report now includes:

- method and test matrix
- quadratic vs quartic results
- plateau discussion
- speed-limit/local-escape discussion
- results tables
- selected figures
- findings and conclusion

`pdflatex` was not available in this environment, so the PDF was not built.

## Cleanup Performed

Added project-level retired-file policy:

```text
Depreciated/README.md
```

Naming cleanup:

- Cost functions were grouped into `gaussian_two_basin/` and `polynomial/`.
- HeavyBall controller configs use clearer `hbesc_*` filenames directly under
  `accelerated_methods/`, matching the existing method-folder convention.
- HeavyBall bash scripts use clearer `hb_*` filenames directly under
  `bash_scripts/accelerated_methods/`, matching the existing method-folder
  convention.
- Reference scenarios were moved to `scenarios/reference_runs/`.
- The baseline run manifest was moved next to the report outputs.
- A duplicate controller config and generated `__pycache__` were moved to
  `Depreciated/`.

## Follow-up Cleanup - 2026-05-18

Matt clarified that written reports should live outside `ros2_ws`, and that all
Gazebo testing should be manual, one scenario at a time, so he can watch Gazebo
and live plots and stop each run himself.

Report artifacts were moved to:

```text
~/dsim-lab/writing/heavy_ball_PDE_ESC/baseline_hb_report/
```

This folder now contains:

```text
baseline_hb_report.tex
baseline_hb_run_manifest.csv
baseline_hb_metrics.csv
figures/
README.md
```

The analysis script remains in `ros2_ws`, but its default manifest, metrics,
and figure paths now point to the writing folder.

The previous batch/matrix runner was retired to:

```text
Depreciated/2026-05-18/manual_testing_only/hb_baseline_matrix_acoustic.bash
```

The active Gazebo workflow is:

```text
manual scenario JSON -> hb_scenario_acoustic.bash -> watch Gazebo/live plots -> stop by hand
```

## Useful Commands

Run a single scenario manually:

```bash
bash ~/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash \
  ~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/baseline_tests/Q1_quadratic_start0_real.json
```

Analyze completed baseline logs:

```bash
python3 ~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/analysis/analyze_baseline_hb_logs.py --plots
```
