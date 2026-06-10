# HeavyBall ESC Versus Gaussian Fill Study

Phase 3 status as of 2026-06-10: repository verification, foundational docs, harness scripts, analysis entrypoints, the bounded Phase 2 smoke run, and the Phase 3 minimal quartic matrix are complete. No Phase 4 gain-sensitivity run has been started.

## What This Directory Contains

- `MASTER_PLAN.md`: source planning document for the study.
- `experiment_plan.md`: Phase 1 experiment design, minimal matrix, and Phase 2 handoff.
- `code_trace.md`: local repo trace of the ROS2/Gazebo pipeline and data flow.
- `hbesc_gain_trace.md`: local repo trace of HBESC, velocity, filter, sensor-spin, and Gaussian-fill parameters.
- `results_manifest.csv`: initialized manifest for future runs.
- `phase3_results.md`: Phase 3 run table, classifications, invalidated run note, and Phase 4 handoff.
- `configs/scenarios/phase1_trial_matrix.csv`: initial trial matrix scaffold.
- `configs/scenarios/phase2_smoke_quartic_baseline.json`: first dry-run/smoke scenario config.
- `configs/scenarios/phase3_qrt_a_hb.json`: Phase 3 convex quartic baseline continuation.
- `configs/scenarios/phase3_qrt_a_gf.json`: next Phase 3 paired Gaussian-fill dry-run candidate.
- `scripts/`: Phase 2 harness scripts for one trial, sweeps, sim-time monitoring, output checks, and manifest recording.
- `analysis/`: Phase 2 analysis and topographic plotting entrypoints.

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
experiments/hbesc_gaussian_fill_study/scripts/run_one_trial.sh --dry-run experiments/hbesc_gaussian_fill_study/configs/scenarios/phase2_smoke_quartic_baseline.json
```

Actual smoke command:

```bash
experiments/hbesc_gaussian_fill_study/scripts/run_one_trial.sh --execute --wall-timeout 120 experiments/hbesc_gaussian_fill_study/configs/scenarios/phase2_smoke_quartic_baseline.json
```

The execute mode uses the scenario `stop_rule_sec` as a sim-time stop rule, writes logs under `results/runs/<run_id>/`, and updates `results_manifest.csv`.

## Phase 2 Smoke Result

Successful smoke run:

- Run ID: `20260609T224323Z_phase2_smoke_quartic_baseline_execute`
- Status: `smoke_sim_time_reached`
- Run directory: `experiments/hbesc_gaussian_fill_study/results/runs/20260609T224323Z_phase2_smoke_quartic_baseline_execute`
- Validation: all normal data collection files were present.
- Metrics file: `summary_metrics.json`
- Figure: `figures/trajectory.png` topographic cost contour with trajectory overlay

The smoke run required execution outside the sandbox because ROS/Gazebo DDS and Gazebo networking need local socket/interface access.

## Phase 3 Minimal Quartic Result

Completed minimal quartic matrix:

- Summary: see `phase3_results.md`.
- Valid execute runs: 11.
- Invalidated execute runs: 1 (`20260609T234054Z_phase3_qrt_b_hb_execute`, superseded by `20260610T013008Z_phase3_qrt_b_hb_execute`).
- Gazebo cleanup: `run_one_trial.sh` now terminates the whole runner process session after each execute run so `gazebo`, `gzserver`, and `gzclient` do not accumulate.
- Gazebo physics: `worlds/gazebo_empty.world` sets `real_time_update_rate` to 3000.

No further Phase 3 run command is pending. Phase 4 should start by adding
low/default/high HBESC gain scenario configs, then dry-running that Phase 4
scenario list before execution.
