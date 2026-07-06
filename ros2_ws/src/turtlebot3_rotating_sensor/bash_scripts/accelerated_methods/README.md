# Accelerated Method Bash Scripts

HeavyBall launch helpers live directly in this `accelerated_methods/` folder,
matching the existing adaptive/gradient-method layout style.

Current active scripts:

```text
hb_scenario_acoustic.bash
hb_escape_acoustic.bash
hb_escape_shallow_acoustic.bash
hb_gaussian_fill_acoustic.bash
hb_light_source_gaussian_fill_acoustic.bash
```

Use `hb_scenario_acoustic.bash` for new work. It launches one selected scenario
at a time, which is the preferred Gazebo workflow.

Use `hb_light_source_gaussian_fill_acoustic.bash` for a direct HeavyBall
source-seeking run where the cost map is generated from configured light-source
positions, lumen values, and the rotating photoresistor sensor orientation. The
script is intentionally edited the same way as the other accelerated-method
launch helpers:

```text
number_of_lights:=3
light_1_x:=2.0
light_1_y:=2.0
light_1_intensity_lumens:=1000.0
```

Set `number_of_lights` from 0 to 5. Only the first N light definitions are
spawned and used by the light-source cost map.

For Gaussian-fill runs, `gaussian_fill_amplitude` is the direct height of the
published fill term. The fill node still fits basin center and sigma from
history, but it no longer replaces this launch value with a doubled fitted
amplitude.

Several HeavyBall scripts pass `show_cost_surface_plot:=True` into
`gazebo.launch.xml`. Set it to `False` to disable the separate 3D cost-surface
window. The surface plot uses the same cost config and `light_N_*` launch values
as the Gazebo run. With `cost_surface_live:=True`, the plot subscribes to
`/odom` and `/cost_bias`, draws the robot path as a red floor trace, and redraws
the surface when Gaussian fills publish. `cost_surface_z_scale_mode:=base` keeps
the original z/color scale after fills, so a large fill shows how it changes the
original surface instead of rescaling the whole plot around a spike.

The previous matrix/batch runner was retired to:

```text
Depreciated/2026-05-18/manual_testing_only/
```
