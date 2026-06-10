# Experiment Plan

Phase: 2 experiment harness.

This plan is based on the current local checkout, not prior assumptions. Full 500-second simulations are intentionally deferred until the smoke harness produces complete output files.

## Current Verified Infrastructure

Baseline path:

- Launch entrypoint: `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`.
- Scenario runner: `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash`.
- Controller node: `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`.
- Controller object: `Rotating_Frame_Directional_Controller` in `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py`.
- HBESC ODE: `HeavyBallODE` in `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_ode_objects.py`.
- Filter config: `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json`.
- Full-rotation config: `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json`.
- Acoustic full-rotation config: `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation_acoustic.json`.

Gaussian-fill path:

- Enabled by `use_pde_extensions:=True` in `gazebo.launch.xml`.
- Raw cost node always publishes `$(entity_name)/cost_value_chatter`.
- `modified_cost_node` subscribes to raw cost plus `/cost_bias` and publishes `/cost_modified`.
- `pde_history_node` publishes `/pde_history`.
- `convergence_detector_node` publishes `/convergence_event`, `/convergence_metric`, and `/convergence_r`.
- `gaussian_fill_node` publishes `/cost_bias` as `[A, mu_x, mu_y, sigma]`.
- With PDE extensions enabled, the filter subscribes to `/cost_modified` instead of raw cost.

Logging path:

- `data_collection_node` writes five CSVs plus `comments.txt`.
- Baseline mode records raw cost in `cost_value.csv`.
- Gaussian-fill mode records modified cost in `cost_value.csv`; raw cost and fill diagnostics need additional logging before full Gaussian-fill trials.

## Existing Cost Families

All current cost configs under `ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/` use `Position_Based_Sympy_Expression` with `No_Noise`.

- Quadratic bowl: `polynomial_quadratic_bowl_center10.json`, function `0.05*((x-10)**2 + (y-10)**2)`.
- Quartic bowl: `polynomial_quartic_bowl_center10.json`, function `0.0005*((x-10)**4 + (y-10)**4)`.
- Quartic double well: `polynomial_quartic_double_well_local2_global10.json`, function `0.01*(((x+y)/2)-2)**2*(((x+y)/2)-10)**2 + 0.0125*(x-y)**2 - 0.005*((x+y)/2)`.
- Gaussian two-basin variants: `gaussian_two_basin_original.json`, `gaussian_two_basin_localA1p0.json`, `gaussian_two_basin_localA2p0.json`, `gaussian_two_basin_localA3p0.json`, `gaussian_two_basin_globalW25.json`, `gaussian_two_basin_globalW30.json`, `gaussian_two_basin_globalW40.json`.

## Minimal Trial Matrix

The first runnable matrix is scaffolded in `configs/scenarios/phase1_trial_matrix.csv`. Start with `phase2_smoke_quartic_baseline.json`, using `scripts/run_one_trial.sh` for both dry-runs and bounded execute attempts.

Priority order:

1. `SMOKE-QRT-HB`: baseline real-speed quartic dry-run/smoke from `(0,0)`.
2. `QRT-A-HB`: baseline real-speed quartic success candidate.
3. `QRT-A-GF`: paired Gaussian-fill comparison on the same quartic.
4. `QRT-B-HB`: baseline real-speed quartic double-well local-basin failure candidate.
5. `QRT-B-GF`: one-fill Gaussian-fill rescue candidate on the same double well.
6. `QVQ-1` and `QVQ-2`: quadratic-versus-quartic comparison with matched start and controller limits.
7. `QRT-C-SLOW`, `QRT-C-REAL`, `QRT-C-FAST`: physical-limit sweep.
8. `QRT-VWZ` and `QRT-GAIN`: focused mini-sweeps after one-at-a-time defaults are understood.

## Controls

- Keep initial comparisons deterministic with `No_Noise`.
- Use the same init pose, cost field, filter, sensor transform, spin profile, success criteria, and duration for paired HBESC/Gaussian-fill comparisons.
- Label fast simulation-only controller results separately from physically valid TurtleBot3 Burger results.
- Do not interpret Gaussian-fill results as complete until raw cost and fill diagnostic streams are logged.

## Phase 2 Harness Requirements

The Phase 2 harness now includes:

- `scripts/run_one_trial.sh`: creates run directories, copies scenario metadata, rewrites `data_collection_filepath` to the run directory, saves the exact launch command, supports dry-run and execute modes, supports opt-in headless execution, monitors `/clock`, and appends the manifest.
- `scripts/run_batch.py`: reusable batch runner over scenario JSON files or CSV scenario lists; writes `results/batches/<batch_id>/batch_plan.csv`, `batch_summary.json`, and per-attempt logs while delegating each trial to `run_one_trial.sh`.
- `scripts/monitor_sim_time.py`: subscribes to `/clock` using best-effort clock QoS and exits when scenario `stop_rule_sec` elapses.
- `scripts/check_trial_outputs.py`: checks expected logs and, for execute runs, the normal data collection CSVs.
- `scripts/run_sweep.py`: compatibility wrapper for `run_batch.py`.
- `analysis/analyze_results.py`: computes basic distance, path length, command, wheel RPM, and saturation metrics when CSVs exist.
- `analysis/make_plots.py`: creates a topographic cost contour plot with trajectory, start, end, target, and local-basin overlays when odometry exists and Matplotlib is available.

Execute runs are isolated with per-run `ROS_DOMAIN_ID`, `GAZEBO_MASTER_URI`, `ROS_LOG_DIR`, and `MPLCONFIGDIR`. If the sim-time monitor succeeds but required output files are absent, the manifest status is downgraded to `smoke_outputs_missing`. Headless runs are opt-in with `--headless`; that path requests `gzserver`, sets Matplotlib to `Agg`, and rewrites only the copied per-run scenario to `live_plot_mode:=None`.

## Unresolved Questions

- Which diagnostic recorder should be used for `/cost_bias`, `/pde_history`, `/convergence_event`, `/convergence_metric`, `/convergence_r`, and raw cost during Gaussian-fill runs: a new lightweight node, `ros2 bag`, or an extension of `data_collection_node`?
- Headless execution must still be proven with at least one short execute smoke on any new machine before trusting it for long batches.
