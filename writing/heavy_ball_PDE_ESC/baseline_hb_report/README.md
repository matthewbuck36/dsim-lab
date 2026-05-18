# Baseline HBESC Report Workflow

1. Run scenarios manually, one at a time, from:

```text
~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/baseline_tests/
```

Use:

```bash
bash ~/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash \
  ~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/baseline_tests/Q1_quadratic_start0_real.json
```

2. Copy each generated `Test_YYYY-MM-DD_HH-MM-SS` folder path into
   `baseline_hb_run_manifest.csv`.
3. Generate metrics and plots from the repo root:

```bash
python3 ~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/analysis/analyze_baseline_hb_logs.py --plots
```

4. Fill in `baseline_hb_report.tex` using `baseline_hb_metrics.csv` and the
   generated figures.

Do not use batch/matrix launch scripts for Gazebo runs. The intended workflow
is manual one-run-at-a-time testing so Gazebo and live plots can be watched and
stopped by hand.
