# Heavy-Ball PDE ESC Experiments

This folder contains the active Heavy-Ball ESC paper recreation assets that are
still used by the Gazebo launch paths.

Active layout:

```text
analysis/                 # log analysis scripts
controller/               # older paper recreation controller assets
cost_function/            # active cost-map configs
filter/                   # filter configs for paper recreation assets
```

Historical baseline scenarios, reference-run scenarios, cost sweeps, controller
variants, and work logs were moved out of the active ROS source tree:

```text
~/dsim-lab/writing/heavy_ball_PDE_ESC/archive/
```

Written reports and report figures live outside `ros2_ws`:

```text
~/dsim-lab/writing/heavy_ball_PDE_ESC/
```

Gaussian-fill runs are enabled by `use_pde_extensions:=True` in
`turtlebot3_rotating_sensor/launch/gazebo.launch.xml`. The active extension
chain is `modified_cost_node`, `pde_history_node`, `pde_cost_history_node`,
`convergence_detector_node`, and `gaussian_fill_node`. The fill node now fits
basin center and sigma from `/pde_history` and `/pde_cost_history`, while
`gaussian_fill_amplitude` directly sets the published fill height.
`modified_cost_node` applies the Gaussian correction plus a PDE-history-based
affine exploration bias before publishing `/cost_modified`.

Light-source cost runs use the same extension chain, but select
`cost_function/multi_light_source_photoresistor.json`. In that mode, the
Gazebo light-source model remains the visible marker, while `number_of_lights`
and `light_N_x`, `light_N_y`, and `light_N_intensity_lumens` define the
source-seeking cost map. `Multi_Light_Source_Cost` uses the rotating sensor
orientation and the fitted photoresistor response; lumens are relative to the
configured reference intensity rather than an absolute photometric calibration.
The ready-to-run bash entrypoint is:

```bash
bash ~/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_gaussian_full_rotation_voltage.bash
```

The active GESC comparison entrypoint is:

```bash
bash ~/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash
```

The older hardcoded `J` equation configs, such as
`2D_local_min.json`, are still supported through `cost_function_config_filepath`
and do not consume the light-source lumen overrides.

The consolidated 2026-05-13 work summary is:

```text
~/dsim-lab/writing/heavy_ball_PDE_ESC/archive/work_logs/HBESC_session_summary_2026-05-13.md
```
