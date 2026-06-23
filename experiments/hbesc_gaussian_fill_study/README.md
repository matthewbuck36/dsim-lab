# HeavyBall ESC Versus Gaussian Fill Study

Phase 5 status as of 2026-06-23: repository verification, foundational docs, harness scripts, analysis entrypoints, the bounded Phase 2 smoke run, the Phase 3 minimal quartic matrix, the Phase 4 HBESC gain-sensitivity matrix, the first bounded Phase 5 characterization matrix, and the expanded 84-scenario Phase 5 characterization matrix are complete. A reusable batch runner is active for dry-run and bounded execute batches.

## What This Directory Contains

- `MASTER_PLAN.md`: source planning document for the study.
- `experiment_plan.md`: Phase 1 experiment design, minimal matrix, and Phase 2 handoff.
- `code_trace.md`: local repo trace of the ROS2/Gazebo pipeline and data flow.
- `hbesc_gain_trace.md`: local repo trace of HBESC, velocity, filter, sensor-spin, and Gaussian-fill parameters.
- `results_manifest.csv`: initialized manifest for future runs.
- `phase3_results.md`: Phase 3 run table, classifications, invalidated run note, and Phase 4 handoff.
- `phase4_results.md`: Phase 4 HBESC gain-sensitivity run table, conclusions, unresolved world-path note, and Phase 5 handoff.
- `phase5_results.md`: Phase 5A bounded characterization run table, world-path fix evidence, aggregate artifacts, and conclusions.
- `phase5_expanded_results.md`: Phase 5B expanded characterization matrix, execution evidence, aggregate artifacts, and conclusions.
- `configs/scenarios/phase1_trial_matrix.csv`: initial trial matrix scaffold.
- `configs/scenarios/phase2_smoke_quartic_baseline.json`: first dry-run/smoke scenario config.
- `configs/scenarios/phase3_qrt_a_hb.json`: Phase 3 convex quartic baseline continuation.
- `configs/scenarios/phase3_qrt_a_gf.json`: next Phase 3 paired Gaussian-fill dry-run candidate.
- `configs/scenarios/phase4_gain_sensitivity_matrix.csv`: Phase 4 low/default/high one-at-a-time HBESC gain-sensitivity matrix.
- `configs/scenarios/phase5_characterization_matrix.csv`: Phase 5 first bounded curvature/barrier/speed characterization matrix.
- `configs/scenarios/phase5_expanded_characterization_matrix.csv`: Phase 5 expanded characterization matrix.
- `scripts/`: harness scripts for one trial, reusable batches, sim-time monitoring, output checks, analysis dispatch, and manifest recording.
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

No further Phase 3 run command is pending.

## Phase 4 Gain Sensitivity Result

Completed Phase 4 matrix:

- Summary: see `phase4_results.md`.
- Valid execute runs: 9.
- Dry-run batch: `results/batches/phase4_gain_dry_run/`.
- Execute batch: `results/batches/phase4_gain_execute/`.
- Aggregate metrics: `results/batches/phase4_gain_execute/phase4_metrics.csv`.
- Result: all 9 gain variants converged within the 2 m success radius on the
  representative convex quartic field, but all exceeded TurtleBot3 Burger
  reference wheel limits.
- Strongest sensitivity: HeavyBall `k`, `k_vx`, and `beta`; `k_wz` was less
  important on this field.

No further Phase 4 run command is pending.

## Phase 5 Expanded Characterization Result

Completed first bounded Phase 5A matrix:

- Summary: see `phase5_results.md`.
- Valid host-level execute runs: 7.
- Dry-run batch: `results/batches/phase5_characterization_dry_run/`.
- Controlling execute batch: `results/batches/phase5_characterization_execute_host/`.
- Aggregate metrics: `results/batches/phase5_characterization_execute_host/phase5_metrics.csv`.
- Aggregate plots: `results/batches/phase5_characterization_execute_host/figures/`.
- World path: `gazebo.launch.xml` now forwards `world` into `empty_world.launch.py`, and `empty_world.launch.py` passes that launch configuration to Gazebo. Phase 5 scenarios explicitly route `/home/mattb/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/worlds/gazebo_empty.world`.
- Result: convex quartic curvature changed convergence quality and speed; the tested double-well barrier-speed slice stayed trapped for all four baseline HBESC cases.
- Note: two sandboxed execute rows in `results_manifest.csv` timed out because DDS/Gazebo socket creation is blocked in the restricted sandbox. They are superseded by the host-level execute batch.

Completed expanded Phase 5B matrix:

- Summary: see `phase5_expanded_results.md`.
- Matrix: `configs/scenarios/phase5_expanded_characterization_matrix.csv`.
- Generated scenarios/configs: `scripts/generate_phase5_expanded_matrix.py`.
- Valid execute runs: 84.
- Dry-run batch: `results/batches/phase5_expanded_dry_run/`.
- Canary execute batch: `results/batches/phase5_expanded_execute_canary/`.
- Controlling execute batch: `results/batches/phase5_expanded_execute/`.
- Aggregate metrics: `results/batches/phase5_expanded_execute/phase5_expanded_metrics.csv`.
- Aggregate summary: `results/batches/phase5_expanded_execute/phase5_expanded_summary.json`.
- Aggregate plots: `results/batches/phase5_expanded_execute/figures/`.
- Result: all 84 scenarios reached sim-time; double-well alpha/speed, beta,
  gamma, start-grid, and noise-seed slices did not enter the 2 m target radius;
  Gaussian fill executed one fill in every Gaussian-fill row but did not rescue
  the tested quartic double-well failure mode.

No further Phase 5 expanded characterization run command is pending.

## Batch Simulation Runner

Use `scripts/run_batch.py` for reusable batch simulations. It writes a batch
plan and summary under `results/batches/<batch_id>/`, calls `run_one_trial.sh`
for each scenario, and leaves each trial artifact under `results/runs/<run_id>/`.
The older `scripts/run_sweep.py` entrypoint remains as a compatibility wrapper.

Default mode is dry-run:

```bash
experiments/hbesc_gaussian_fill_study/scripts/run_batch.py --limit 1 --csv experiments/hbesc_gaussian_fill_study/configs/scenarios/phase3_remaining_matrix.csv
```

Execute a batch with the opt-in barebones path:

```bash
experiments/hbesc_gaussian_fill_study/scripts/run_batch.py --execute --headless --wall-timeout 700 --retries 1 --csv experiments/hbesc_gaussian_fill_study/configs/scenarios/phase3_remaining_matrix.csv
```

`--headless` requests `gzserver` instead of `gazebo` and rewrites only the
per-run copied scenario to `live_plot_mode:=None`; source scenario JSON files
are not changed. Useful controls: `--plan-only`, `--resume`, `--limit N`,
`--fail-fast`, and `--batch-id NAME`.
