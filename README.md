# DSIM Lab

This repository contains ROS 2 Humble/Gazebo research code for extremum-seeking
control, including the completed V1 GESC + adaptive Gaussian evidence line.

The canonical project summary is the LaTeX-typeset
[GESC + Robust Gaussian V1 Final Project Report](docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.pdf).
Its [LaTeX source](docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.tex) and
[auditable Markdown companion](docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.md)
are retained beside it.
Its [coverage matrix](docs/codex/gesc_gaussian/validation/phase_10_report_coverage.tsv)
accounts for the full implementation package and material Phase 00–10
evidence. Start with those files before relying on historical README examples.

V1 preserved legacy ESC behavior and implemented an opt-in
`robust_gaussian_v1` pipeline with typed observability, an explicit supervisor,
adaptive Gaussian fills, managed rosbag recording, deterministic scenarios,
offline analysis, and a selected physical workflow. It demonstrated selected
two-basin behavior, but it did **not** establish broad simulation robustness,
broad physical readiness, or complete second-extremum physical acceptance.

## Repository map

- [`ros2_ws/src/ros_esc`](ros2_ws/src/ros_esc/README.md): algorithm, recorder,
  validator, scenario runner, and analysis owners.
- [`ros2_ws/src/ros_esc_interfaces`](ros2_ws/src/ros_esc_interfaces/README.md):
  six robust typed messages and five preserved compatibility messages.
- [`ros2_ws/src/turtlebot3_rotating_sensor`](ros2_ws/src/turtlebot3_rotating_sensor/README.md):
  Gazebo model, launch graph, worlds, and simulation wrappers.
- [`DSIM_GESC_Gaussian_Codex_Implementation_Package`](DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md):
  original requirements, source material, phase prompts, templates, and tools.
- [`docs/codex/gesc_gaussian`](docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.pdf):
  Plans, statuses, handoffs, validation, technical reference, and final report.
- [`EXPERIMENT_STORAGE.md`](EXPERIMENT_STORAGE.md): external run retention and
  evidence-authority rules.

## Minimal build

```bash
cd /home/mattb/dsim-lab/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
```

Use `algorithm_profile:=robust_gaussian_v1` explicitly for the V1 robust path;
direct launches retain `legacy` compatibility defaults. Use
`ros2 run ros_esc record_run` for managed evidence and
`ros2 run ros_esc validate_run` for completeness. Verified simulation,
analysis, and operator commands are in
[Section 15 of the report](docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.md#15-verified-operating-instructions).

Raw bags, CSVs, plots, and physical run products remain outside Git. Failed and
partial evidence is retained and must not be overwritten. The future intended
branch `feature/gesc-gaussian-robustness-v2` must begin from a reviewed,
committed V1 closeout; Phase 10 did not create it.
