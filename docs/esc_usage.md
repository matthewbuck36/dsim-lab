# Running ESC in Gazebo

This checkout runs the original ESC methods and the V3 development algorithm.
Gaussian V1/V2 are frozen references; physical V1 is preserved in complete
backups during the separately authorized [V3 deployment](esc_physical_v3.md).
Software checks do not establish Gazebo behavior or physical
qualification. See [architecture](esc_architecture.md) and [history](esc_history.md).

## Build and source

Use a fresh terminal with ROS 2 Humble and this workspace, without an archived
workspace overlay. Install the local numerical library once, then build after
source or configuration changes:

```bash
cd /home/mattb/dsim-lab
source /opt/ros/humble/setup.bash
timeout 120s python3 -m pip install --user --no-deps -e ./extremum-seeking
cd ros2_ws
timeout 300s colcon build --symlink-install \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
```

In later terminals, source `/opt/ros/humble/setup.bash` and
`/home/mattb/dsim-lab/ros2_ws/install/setup.bash`. Run commands never build or
rewrite JSON. Gazebo and its ROS plugins belong to the simulation environment;
the shared algorithm core does not require Gazebo or Matplotlib imports.

## Run one method

Interactive V3 starts Gazebo, the original Matplotlib live plot, and optional
rosbag recording:

```bash
ros2 launch turtlebot3_rotating_sensor gazebo.launch.py profile:=gesc_v3
```

The 19 Bash aliases select named profiles. For example, choose one of:

```bash
cd /home/mattb/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts
bash gradient_methods/gesc_full_rotation_acoustic.bash
bash adaptive_methods/rmsprop_full_rotation.bash
bash gradient_methods/gesc_v3.bash
```

Each run continues until **Ctrl+C**, including after a best-source event. Allow
shutdown to finish so the controller and arm can publish zero commands and the
bag can close. A zero command record alone does not prove measured stopping.

The shared launch has six options:

| Option | Default | Meaning |
| --- | --- | --- |
| `profile` | `gesc_v3` | Installed algorithm name or custom profile JSON |
| `environment` | `gazebo` | This launch supports Gazebo only |
| `gui` | `true` | Display Gazebo; false also disables live plotting |
| `plot` | `auto` | Automatic interactive Matplotlib plot; `false` disables it |
| `record` | `true` | Optional ordinary rosbag; failure never gates control |
| `output` | `~/Experiments/ESC` | Root for a new uniquely named bag directory |

A bounded headless example, with recording disabled:

```bash
timeout --foreground --signal=INT --kill-after=15s 120s ros2 launch \
  turtlebot3_rotating_sensor gazebo.launch.py \
  profile:=gesc_v3 gui:=false plot:=false record:=false
```

Closing the plot or losing the recorder does not stop the algorithm. Physical
runs have no automatic plotting; their adapters remain in the separate
`turtlebot3_vehicle_nodes` workspace, outside this checkout.

For automated bounds, `--foreground` sends the deadline signal to launch, which
forwards it to its directly owned processes. This avoids a second simultaneous
process-group interrupt during cleanup. Allow the shutdown grace to complete
and verify that the bag closed and the launched processes exited.

## Configuration and analysis

Algorithm/environment profiles and their numerical JSON files live in
[`ros_esc/config/profiles`](../ros2_ws/src/ros_esc/config/profiles). Installed
profiles are resolved from the selected workspace. Built-in object references
use Python module names; custom original JSON objects may still use `filepath`.
The V3 controller JSON owns its effective gains and speed caps. Scene parameters
belong to the modeled cost configuration, not the controller's observations.
The current V3 development caps are 0.10 m/s and 0.50 rad/s, matching the archived
full-rotation light GESC baseline. Its linear gain remains 0.5. Physical V3 uses
the shared algorithm with separately selected caps of 0.05 m/s and 0.30 rad/s;
the physical guide owns its configuration and qualification status. V1 is backed
up. Gazebo's visible light models use the selected cost JSON positions.

The V3 controller JSON currently sets `direct_escape_assistance_enabled: false`
for the user-requested unaided escape experiment. Gaussian and affine cost
shaping remain active; only direct heading-command assistance is disabled.
Setting this boolean true enables the last-resort fallback: less than 5 cm
outward progress over 15 seconds permits one nominal 20 cm measured-path pulse
per escape, followed by ordinary GESC. The controller JSON owns
`escape_assist_stall_window_sec` and `escape_assist_distance_m`; odometry/control
sampling determines the actual cutoff resolution.
The same controller JSON accepts `escape_affine_magnitude`. The user-selected
V3 development value is now 2.0; omitted values in older custom profiles still
default to 0.5. Use an external custom profile for one-off slope comparisons.

Valid moving approach and verification have no elapsed-time deadline. They
continue while motion, fresh inputs and candidate geometry remain valid, until
the evidence is ready or the run is interrupted. Automated Gazebo test bounds
do not impose an internal candidate deadline. Input freshness and finite
numerical-worker budgets remain separate requirements. Escape likewise ends
on measured spatial exit, invalid control evidence or interruption, rather
than an elapsed attempt deadline.

Analyze a **closed** ordinary bag directory; no project manifest is required:

```bash
timeout 120s ros2 run ros_esc analyze_bag "/path/to/closed_bag" --csv
```

The default output is a new sibling directory ending in `_analysis`, containing
`summary.json`, available plots and optional CSVs. Use `--output /path/to/new_dir`
for another destination. Missing topics or measurements remain unavailable;
analysis does not turn incomplete evidence into qualification. Keep bags and
analysis products under `~/Experiments`, outside Git.
