# TurtleBot3 rotating sensor simulation

This package owns Gazebo models, world/robot bringup and the simulation launch.
Start with [usage](../../../docs/esc_usage.md),
[architecture](../../../docs/esc_architecture.md), and
[history](../../../docs/esc_history.md).

`gazebo.launch.py` resolves one algorithm profile and the Gazebo environment.
Its six options are `profile`, `environment`, `gui`, `plot`, `record`, and
`output`. The [19 short Bash aliases](bash_scripts) select original
ESC methods or V3; none builds or modifies configuration.

Interactive Gazebo automatically opens the original Matplotlib live plot.
Headless runs disable plotting. Ordinary rosbag recording is optional and on by
default. Plot/recorder failures do not gate control. Runs continue until Ctrl+C.

V3 uses the simulation sensor/arm adapters, one observation adapter and one
controller core. Original ESC methods retain the filter/controller path. The
physical `turtlebot3_vehicle_nodes` package stays outside this checkout; this
Gazebo launch does not start physical hardware. V3 simulation behavior and
physical qualification require their own evidence. Gaussian V1/V2 and previous
package documentation are preserved in the frozen history and archive.
