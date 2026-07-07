# Gaussian Fill Light-Source Sweep Report

Run artifacts:

- Full trial table: `/tmp/codex_light_search/results.tsv`
- Trial logs: `/tmp/codex_light_search/logs/`
- Temporary headless launch wrapper: `/tmp/codex_light_search/gazebo_headless.launch.xml`
- Temporary runner/analyzer: `/tmp/codex_light_search/run_trial.sh`, `/tmp/codex_light_search/analyze_trial.py`

The runs used headless Gazebo through a temporary launch copy. The repo launch files and Python source were not changed during the sweep. The existing `gesc_light_source_gaussian_fill_acoustic.bash` and `hb_light_source_gaussian_fill_acoustic.bash` scripts still contain GUI-oriented defaults (`live_plot_mode:='2D'`, `show_cost_surface_plot:='True'`) and a stale `gaussian_fill_amplitude:=10.0`, so the sweep used explicit launch arguments instead of running those bash files directly.

## Setup

Common launch settings:

- `live_plot_mode:='None'`
- `show_cost_surface_plot:='False'`
- `use_pde_extensions:='True'`
- `escape_policy:='conditional_gaussian_fill'`
- `cost_function_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json'`
- `number_of_lights:=3`
- light 1: `(1.0, 0.5)`, `500 lm`
- light 2 original: `(1.5, 3.0)`, `1000 lm`
- light 3: `(4.0, 4.0)`, `2000 lm`

The search also tested moved middle-light layouts inside the 4 m by 4 m lab box, mainly `(2.7, 3.0)`, after the original layout repeatedly skipped or missed the middle light.

## GESC + Gaussian Results

Trials run: 10.

Outcomes:

- `PASS_GESC`: 0
- `FAIL_SKIP_2`: 4
- `FAIL_WANDER`: 6

Best original-layout GESC run:

- Label: `gesc_A0p20_s0p25_0p55_r0p1_l2_1p5_3p0`
- Parameters: `A=0.20`, `min_sigma=0.25`, `max_sigma=0.55`, `recent=0.1`, `min_points=50`, `threshold=0.2`, `min_periods=2.0`, `max_fills=2`
- Outcome: `FAIL_SKIP_2`
- Evidence: light 1 min distance `0.15 m`; light 2 min distance `0.89 m`; light 3 min distance `1.50 m`; final `(2.50, 3.82)`
- Interpretation: tightening the fit window helped point the second convergence toward the middle region, but the robot still did not truly trap at light 2 or converge to light 3.

Best overall GESC run after moving light 2:

- Label: `gesc_A0p20_s0p25_0p55_r0p1_l2_2p7_3p0_long`
- Moved light 2: `(2.7, 3.0)`
- Parameters: `A=0.20`, `min_sigma=0.25`, `max_sigma=0.55`, `recent=0.1`, `min_points=50`, `threshold=0.2`, `min_periods=2.0`, `max_fills=2`
- Outcome by strict classifier: `FAIL_WANDER`
- Evidence: light 1 min distance `0.15 m`; light 2 min distance `0.53 m`; light 3 min distance `0.01 m`; final `(3.94, 4.04)`
- Fills: `1@(1.83,0.26)s0.25`; `2@(2.12,3.32)s0.55`
- Interpretation: this is behaviorally closest to the requested sequence: it visited the first region, produced two fills, visited the moved middle region, and ended at light 3 without a third fill. It still fails strict criteria because the first published fill center drifted too far from light 1.

Rerun command for best GESC candidate:

```bash
/tmp/codex_light_search/run_trial.sh GESC gesc_A0p20_s0p25_0p55_r0p1_l2_2p7_3p0_long 0.20 0.25 0.55 0.1 2.0 0.2 50 2.7 3.0 420
```

## HB + Gaussian Results

Trials run: 9.

Outcomes:

- `PASS_HB`: 0
- `FAIL_SKIP_2`: 6
- `FAIL_WANDER`: 3

Original-layout HB behavior:

- Tested `A=0.03`, `0.05`, `0.10`, `0.20` with `min_sigma=0.25`, `max_sigma=0.55`, `recent=0.1`, `min_periods=2.0`, `threshold=0.2`.
- All original-layout runs spent both fills around the first-light basin or nearby approach trajectory.
- None got within `1.70 m` of the original light 2 location; most stayed around light 1.

Best moved-layout HB candidate:

- Label: `hb_A0p10_s0p25_0p55_r0p1_l2_2p7_3p0`
- Moved light 2: `(2.7, 3.0)`
- Parameters: `A=0.10`, `min_sigma=0.25`, `max_sigma=0.55`, `recent=0.1`, `min_points=50`, `threshold=0.2`, `min_periods=2.0`, `max_fills=2`
- Outcome: `FAIL_SKIP_2`
- Evidence: light 1 min distance `0.19 m`; moved light 2 min distance `0.00 m`; light 3 min distance `1.09 m`; final `(2.60, 3.17)`
- Fills: `1@(1.01,0.57)s0.25`; `2@(1.32,0.88)s0.55`
- Interpretation: this run proves HB can physically reach the moved light-2 region, but it consumed both allowed fills before that happened. By the time the robot was trapped near light 2, `gaussian_fill_max_fills=2` was exhausted.

Focused min-distance tests:

- Added `gaussian_fill_min_distance_between_fills:=1.0` for two moved-layout HB runs.
- This did not solve the problem. The fill fit centers drifted enough that the second fill could still be published away from the actual second basin, or the robot still failed to reach light 3.

Rerun command for best HB candidate:

```bash
/tmp/codex_light_search/run_trial.sh HB hb_A0p10_s0p25_0p55_r0p1_l2_2p7_3p0 0.10 0.25 0.55 0.1 2.0 0.2 50 2.7 3.0 360
```

## Parameter Trends

The current stack is very sensitive to fill-center quality, not just fill amplitude.

- Very low HB amplitude (`A=0.03`) did not push the robot out of the first basin reliably.
- Moderate HB amplitude (`A=0.10`) let the robot reach the moved middle-light region, but both fills had already been consumed.
- Larger or wider fills tended to produce poorer fill centers and more wandering around light 1.
- Tight sigma bounds and a smaller recent fraction (`0.25/0.55`, `recent=0.1`) were generally better than wider bounds for GESC, but still did not produce a clean original-layout pass.
- Moving light 2 to the observed trajectory near `(2.7, 3.0)` was far more effective than any amplitude-only change, which suggests the cost surface/controller path does not naturally visit `(1.5, 3.0)` before the global light under the current model.

## Source-Level Findings

These are suggestions and failure hypotheses from reading the current source. I did not implement them in this sweep.

### 1. GaussianFill ignores the convergence event center

`convergence_detector_node_script.py` publishes `mean_recent` as the recommended fill center in the convergence event data. See:

- `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py:297-327`

But `gaussian_fill_script.py` ignores the event's center fields and instead refits a Gaussian over its current PDE position and raw-cost history. See:

- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py:211-279`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py:290-399`

This matches the run evidence. Several logs had convergence centers near the actual trap, while the published fill center drifted far away. Example from the best moved-layout GESC run: convergence was around the first-light region, but fill #1 published at `(1.83, 0.26)`.

Suggested change: add a mode that uses the convergence event center directly as `mu`, or clamps/refuses a fitted `mu` when it is too far from the event center. The fit can still estimate `sigma`, but center quality should be bounded.

### 2. PDECostHistory fits raw cost, not modified cost

The launch wiring sends raw cost into `pde_cost_history_node`:

- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml:406-413`

The controller uses `/cost_modified`, but the Gaussian fit history is built from `/turtlebot3/cost_value_chatter`, before prior fills and affine terms. That means later Gaussian fits can behave as if previous fills did not reshape the cost surface.

Suggested change: for multi-fill mode, test feeding `/cost_modified` into `pde_cost_history_node`, or explicitly subtract/account for already-published fill terms during fitting.

### 3. The convergence detector is not basin-aware

The detector uses a mean-motion stability metric:

- `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py:211-257`

It has no knowledge of light identity, global-vs-local status, or whether the robot already escaped a previous basin. It correctly detects "stable/looping" behavior, but it can trigger repeated events around the same broad first-basin region. This was especially visible in HB.

Suggested change: add state around convergence events: minimum distance from previous event centers, required post-fill displacement, or a cooldown based on leaving the prior basin before another fill can be consumed.

### 4. ModifiedCost adds a second mechanism beyond Gaussian fill

Every fill also adds an affine exploration bias by default:

- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py:329-400`

The affine direction is estimated from the fill center and PDE history:

- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py:454-524`

If the fill center is wrong, the affine term can also be wrong. It is not a pure Gaussian-fill experiment. The default affine age is 30 seconds and default gain is 0.5:

- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py:95-121`

Suggested change: expose `enable_affine_bias`, `affine_gain`, `affine_max_age`, and `history_exclusion_radius_factor` as launch arguments and run an A/B test with affine disabled. If Gaussian-only behaves more predictably, tune/rework affine separately.

### 5. The bash defaults are stale for current amplitude semantics

Both light-source Gaussian bash scripts still use:

- `live_plot_mode:='2D'`
- `show_cost_surface_plot:='True'`
- `gaussian_fill_amplitude:=10.0`

See:

- `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_light_source_gaussian_fill_acoustic.bash:18-19`
- `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_light_source_gaussian_fill_acoustic.bash:44`
- `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_light_source_gaussian_fill_acoustic.bash:18-19`
- `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_light_source_gaussian_fill_acoustic.bash:44`

Since `gaussian_fill_amplitude` now directly sets published fill height, `10.0` is far too large for the voltage-scale multi-light runs tested here.

Suggested change: update the scripts to headless-safe defaults or add separate headless variants, and change amplitude defaults to the direct-height range used in this sweep (`0.05` to `0.20`).

## Recommended Next Changes

1. Add launch args for the modified-cost affine settings, especially `enable_affine_bias`, then run GESC/HB Gaussian-only tests.
2. Add a GaussianFill guard: reject or clamp fitted centers too far from the convergence event's `mean_recent`.
3. Add a "must leave previous basin" condition before consuming another fill. `min_distance_between_fills` alone was not sufficient because the fit centers can drift away from the true basin.
4. Consider feeding modified cost into `pde_cost_history_node` for multi-fill trials, or otherwise make the fitting model aware of previous fills.
5. Treat the current original light-2 location `(1.5, 3.0)` as not naturally visited under the present cost/controller stack. If the lab sequence requires that physical middle light, the cost model/controller behavior likely needs adjustment beyond Gaussian-fill amplitude tuning.

## Bottom Line

No tested parameter set produced a clean pass for either GESC + Gaussian or HB + Gaussian on the original three-light layout. The best GESC run can complete the intended sequence only after moving the middle light onto the observed trajectory, and even then the first fill center is loose. HB performs worse: it often reaches or approaches the moved middle-light region only after spending both fills near the first basin.

The most likely failure is not simply "wrong amplitude." The logs and source point to a mismatch between convergence-event centers, Gaussian fit centers, raw-vs-modified cost history, and the extra affine bias added by `modified_cost_node`.
