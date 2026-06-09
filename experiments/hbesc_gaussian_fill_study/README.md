# HeavyBall ESC Versus Gaussian Fill Study

Phase 1 status as of 2026-06-09: repository verification and foundational docs are complete. No long Gazebo simulation or full trial was run.

## What This Directory Contains

- `MASTER_PLAN.md`: source planning document for the study.
- `experiment_plan.md`: Phase 1 experiment design, minimal matrix, and Phase 2 handoff.
- `code_trace.md`: local repo trace of the ROS2/Gazebo pipeline and data flow.
- `hbesc_gain_trace.md`: local repo trace of HBESC, velocity, filter, sensor-spin, and Gaussian-fill parameters.
- `results_manifest.csv`: initialized manifest for future runs.
- `configs/scenarios/phase1_trial_matrix.csv`: initial trial matrix scaffold.
- `configs/scenarios/phase2_smoke_quartic_baseline.json`: first dry-run/smoke scenario config.

## Verified Repo Facts

- Baseline HBESC uses `Rotating_Frame_Directional_Controller` from `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py` and `HeavyBallODE` from `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_ode_objects.py`.
- The active baseline controller configs are `hbesc_baseline_slow_full_rotation.json`, `hbesc_baseline_real_full_rotation.json`, and `hbesc_baseline_fast_sim_full_rotation.json`.
- Gaussian fill is implemented by `modified_cost_node`, `pde_history_node`, `convergence_detector_node`, and `gaussian_fill_node`; it is enabled from `gazebo.launch.xml` with `use_pde_extensions:=True`.
- The scenario runner is `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash`; it rejects unknown `launch` keys through a whitelist.
- Normal data collection writes `odometry.csv`, `sensor_transform.csv`, `cost_value.csv`, `filter_value.csv`, `control_value.csv`, and `comments.txt`.
- In Gaussian-fill mode, `cost_value.csv` records `/cost_modified`; raw cost, `/cost_bias`, `/pde_history`, `/convergence_event`, `/convergence_metric`, and `/convergence_r` are not recorded by the normal data collection node.
- Controller outputs in `control_value.csv` are `[vx, vy, vz, wx, wy, wz]` robot body commands. Sensor spin is separate and comes from the rotate-frame node.

## Phase 1 Validation

Run these lightweight checks after editing Phase 1 files:

```bash
python3 -m json.tool experiments/hbesc_gaussian_fill_study/configs/scenarios/phase2_smoke_quartic_baseline.json
python3 -c 'import csv, pathlib; [row for row in csv.reader(pathlib.Path("experiments/hbesc_gaussian_fill_study/results_manifest.csv").open(newline=""))]'
python3 -m xml.etree.ElementTree ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml
bash -n ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash
bash ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash --dry-run experiments/hbesc_gaussian_fill_study/configs/scenarios/phase2_smoke_quartic_baseline.json
```

## Phase 2 Handoff

Next exact command for the Phase 2 smoke dry-run:

```bash
bash ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash --dry-run experiments/hbesc_gaussian_fill_study/configs/scenarios/phase2_smoke_quartic_baseline.json
```

Do not run a full 500-second trial until a Phase 2 harness can terminate by sim time and archive logs deterministically.
