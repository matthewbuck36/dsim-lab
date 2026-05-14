# Heavy-Ball PDE ESC Experiments

This folder contains Heavy-Ball ESC paper recreation assets, generalized
scenario configs, baseline test reports, and analysis tooling.

Active layout:

```text
analysis/                 # log analysis scripts
controller/               # older paper recreation controller assets
cost_function/            # cost-map configs grouped by family
docs/                     # session summaries and implementation notes
filter/                   # filter configs for paper recreation assets
report/                   # baseline report, manifest, metrics, figures
scenarios/
  baseline_tests/         # 15 professor-assignment baseline scenarios
  reference_runs/         # known-good Gaussian/multi-fill/reference scenarios
```

Use this runner for new manual Gazebo tests:

```bash
bash ~/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash \
  ~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/baseline_tests/Q1_quadratic_start0_real.json
```

The consolidated 2026-05-13 work summary is:

```text
docs/HBESC_session_summary_2026-05-13.md
```

