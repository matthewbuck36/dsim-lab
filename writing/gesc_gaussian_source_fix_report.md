# GESC Gaussian Fill Source-Level Fix Report

Branch: `gesc-gaussian-source-fixes`

This branch narrows the realistic Gazebo light-source path to GESC + Gaussian fill. HB is no longer part of the recommended next run path.

## Why These Changes Were Made

The latest sweep report showed that the failing runs were not mainly an amplitude problem. The key issue was that the convergence detector already computes a stable loop average, `mean_recent`, but the Gaussian fill node ignored that event center and refit the fill center from raw history. That allowed a fill to land away from the basin the robot had actually circled.

The intended behavior is now encoded directly: the robot circles a local basin, the convergence detector publishes the averaged center of that loop, and Gaussian fill uses that averaged center as the fill anchor.

## Source Changes

### `gaussian_fill_node`

File: `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`

- Added `center_source`, defaulting to `event_mean`.
- Added `max_fit_center_distance_from_event`, defaulting to `0.75 m`.
- Added `min_event_center_distance_between_fills`, defaulting to `0.0 m`.
- The node now reads the convergence event center from `/convergence_event` data fields 3 and 4, matching `convergence_detector_node`.
- The published fill center now defaults to the convergence detector's `mean_recent` center.
- The Gaussian fit is still used to validate basin shape and estimate `sigma`.
- The fit is initialized at the event center and bounded around it, so history fitting cannot freely drift away from the loop average.
- Repeat-fill suppression can now compare event centers instead of only comparing fitted/published fill centers. This is the basin-aware guard that `min_distance_between_fills` did not provide.

Supported center modes:

- `event_mean`: publish the convergence-event mean center. This is the new default.
- `fit`: publish the fitted center, but reject it if it drifts too far from the event center.
- `fit_clamped`: publish the fitted center, clamped toward the event center if needed.

### `gazebo.launch.xml`

File: `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`

- Exposed Gaussian center-control launch args:
  - `gaussian_fill_center_source`
  - `gaussian_fill_max_fit_center_distance_from_event`
  - `gaussian_fill_min_event_center_distance_between_fills`
- Exposed `pde_cost_history_topic`, so the fit history can subscribe to `/cost_modified` instead of always using raw `/turtlebot3/cost_value_chatter`.
- Exposed modified-cost affine launch args:
  - `modified_cost_enable_affine_bias`
  - `modified_cost_affine_gain`
  - `modified_cost_affine_decay_rate`
  - `modified_cost_affine_max_age`
  - `modified_cost_affine_direction_sign`
  - `modified_cost_use_pde_history_for_affine`
  - `modified_cost_history_exclusion_radius_factor`
  - `modified_cost_history_direction_mode`

The affine default remains enabled, with `outside_to_anchor` and sign `1.0`, because that direction uses the approach path into the circled basin as the forward escape direction. The important difference is that the anchor is now the averaged basin center, not a free-drifting fitted center.

### GESC Two-Light Runner

File: `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`

- Kept one-off visual-test defaults enabled:
  - `live_plot_mode:='2D'`
  - `show_cost_surface_plot:='True'`
- Set `number_of_lights:=3` after the two-light validation run succeeded.
- Kept the first light at `(1.0, 0.5)` with `500 lm`.
- Kept the second test light at `(2.7, 3.0)` with `1000 lm`, matching the best moved-layout sweep result.
- Set `gaussian_fill_max_fills:=2`, so the three-light run can fill the first basin and the middle basin before moving to the final light.
- Set `pde_cost_history_topic:='/cost_modified'`, so future fills are fit against the same modified surface the controller is using.
- Set `gaussian_fill_center_source:='event_mean'`.
- Set `gaussian_fill_max_fit_center_distance_from_event:=0.75`.
- Set `gaussian_fill_min_event_center_distance_between_fills:=1.0`; this mostly matters when switching back to 3 lights and `max_fills:=2`.
- Kept affine enabled and explicitly exposed its key settings in the command.

### Cost-Surface Snapshot Saving

Files:

- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/cost_surface_plotter.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`

The normal data collection node saves CSVs, not the 3D cost-surface map. The live cost-surface plotter now saves a final PNG snapshot when the plotter shuts down, including when the launch is stopped with Ctrl+C. By default the snapshot is written under `~/Experiments/Gazebo-Simulations` with a filename like `cost_surface_final_YYYY-MM-DD_HH-MM-SS.png`.

### HB Manual Test Runner

File: `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_gaussian_full_rotation_voltage.bash`

HB is still not the primary path, but the script now uses the same event-centered Gaussian-fill source fixes so it can be tried manually. It uses the same two-light moved layout, visible plots, `/cost_modified` cost history, `center_source:='event_mean'`, and one fill. Its starting amplitude is `0.10`, based on the earlier HB sweep where `0.10` behaved better than the larger values.

## First Run Command

From any shell:

```bash
cd ~/dsim-lab/ros2_ws && ./src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash
```

This is now the recommended three-light GESC run. It keeps the Gazebo GUI and plots visible, uses the moved middle light at `(2.7, 3.0)`, includes the third light at `(4.0, 4.0)`, and allows two Gaussian fills.
