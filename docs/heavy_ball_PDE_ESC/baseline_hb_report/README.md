# Baseline HBESC Report Workflow

1. Historical scenarios for this report are archived at:

```text
~/dsim-lab/docs/heavy_ball_PDE_ESC/archive/scenarios/baseline_tests/
```

The original scenario runner has been retired from the active ROS tree. These
scenario files are retained as report provenance rather than as the current
manual Gazebo workflow.

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
