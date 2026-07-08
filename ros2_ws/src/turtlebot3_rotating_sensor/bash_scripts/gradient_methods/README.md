# Description

This folder contains launch executables for gradient based extremum seeking
methods tuned for a journal paper by Dylan James Kavanaugh. Most experiments
use a photoresistor voltage based cost function.

`gesc_gaussian_full_rotation_voltage.bash` is a comparison entrypoint for
GESC plus Gaussian fill using the same multi-light rotating photoresistor cost
model and light layout as the HeavyBall light-source script.

Set `show_cost_surface_plot:=False` in that script to disable the separate 3D
cost-surface window. With `cost_surface_live:=True`, the plot subscribes to
`/odom` and `/cost_bias`, draws the robot path as a red floor trace, and redraws
the surface when Gaussian fills publish. `cost_surface_z_scale_mode:=base` keeps
the original z/color scale after fills, so a large fill shows how it changes the
original surface instead of rescaling the whole plot around a spike.
