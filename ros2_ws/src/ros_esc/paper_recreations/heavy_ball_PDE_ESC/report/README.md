# Baseline HBESC Report Workflow

1. Run scenarios from `scenarios/baseline_tests/`.
2. Copy each generated `Test_YYYY-MM-DD_HH-MM-SS` folder path into
   `report/baseline_hb_run_manifest.csv`.
3. Generate metrics and plots:

```bash
python3 ~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/analysis/analyze_baseline_hb_logs.py --plots
```

4. Fill in `baseline_hb_report.tex` using `baseline_hb_metrics.csv` and the
   generated figures.
