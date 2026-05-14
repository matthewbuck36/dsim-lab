# HBESC Work Log - 2026-04-22

This file records the Heavy-Ball ESC changes and experiment outcomes from the
2026-04-22 Codex session. The goal was to keep the working Gaussian-fill HBESC
case intact while adding a separate baseline HBESC momentum-escape workflow.

## Starting Point

- Existing Gaussian-fill HBESC setup was working from previous work:
  - `use_pde_extensions:=True`
  - cost map: `2D_local_min.json`
  - filter: `gesc_filter_full_rotation.json`
  - controller: `heavyball_controller_full_rotation.json`
  - expected behavior: approach local basin near `(2,2)`, inject Gaussian fill,
    then converge near global basin `(10,10)`.
- Baseline HBESC without PDE/Gaussian fill was expected to use:
  - `use_pde_extensions:=False`
  - raw cost topic `turtlebot3/cost_value_chatter`
  - no `modified_cost_node`, `convergence_detector_node`, `gaussian_fill_node`,
    or `pde_history_node`.

## Original Script Retired

### `hb_acoustic.bash`

File removed after dedicated HeavyBall scripts were added:

`ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_acoustic.bash`

Intermediate change made earlier in the session:

```diff
-use_pde_extensions:='True'
+use_pde_extensions:='False'
```

Reason:

- This first made the original script run baseline HBESC mode instead of
  Gaussian-fill mode.
- It is now intentionally removed because the dedicated scripts below make the
  workflows explicit and avoid manual toggling.

## New/Reorganized Controller Configs

The active TurtleBot HeavyBall controller configs now live under:

`ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/`

They were moved out of:

`ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/adaptive_methods/`

Moved Gaussian-fill controller:

- `heavyball_controller_full_rotation.json`

### `heavyball_escape_controller_full_rotation.json`

File:

`ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/heavyball_escape_controller_full_rotation.json`

Purpose:

- Separate controller for baseline HBESC momentum-escape tests.
- Keeps the stable Gaussian-fill controller untouched.

Initial version added:

```json
"gains": {
  "k_vx": 1.0,
  "k_wz": 5.0
}
```

Changed after logs showed forward velocity saturated almost constantly:

```diff
-"k_vx": 1.0,
-"k_wz": 5.0
+"k_vx": 0.2,
+"k_wz": 2.0
```

Current/final escape-controller gains:

```json
"gains": {
  "k_vx": 0.2,
  "k_wz": 2.0
}
```

Current HeavyBall ODE parameters:

```json
"k": 1.0,
"beta": 0.1,
"input_gain": -1.0
```

Parameter meaning:

- `k = 1.0`: HeavyBall gradient gain.
- `beta = 0.1`: damping. Low damping preserves momentum.
- `input_gain = -1.0`: sign adapter for the GESC filter output convention.

Current physical/motion limits:

```json
"wheel_radius": 0.033,
"wheel_distance": 0.158,
"wheel_max_rpm": 70,
"set_max_vx": null,
"set_max_wz": 0.75
```

Notes:

- `set_max_vx = null` means forward velocity uses the physical wheel/RPM limit.
- Computed physical forward limit:
  - `max_vx = 0.2419026343264141 m/s`
- Raw computed yaw limit from wheel geometry is about `3.062 rad/s`, but we cap:
  - `set_max_wz = 0.75 rad/s`

## New Bash Launch Scripts

### `hb_escape_acoustic.bash`

File:

`ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_acoustic.bash`

Purpose:

- Baseline HBESC momentum-escape test.
- PDE/Gaussian fill disabled.

Key settings:

```bash
init_x_position:=-2
init_y_position:=-2
use_pde_extensions:='False'
cost_function_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/2D_local_min.json'
controller_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/heavyball_escape_controller_full_rotation.json'
```

### `hb_gaussian_fill_acoustic.bash`

File:

`ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_gaussian_fill_acoustic.bash`

Purpose:

- Known-good HBESC + PDE/Gaussian-fill test.
- Kept separate from baseline escape tests.

Key settings:

```bash
init_x_position:=0
init_y_position:=0
use_pde_extensions:='True'
cost_function_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/2D_local_min.json'
controller_config_filepath:='~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/heavyball_controller_full_rotation.json'
pde_omega:=5.0
convergence_threshold:=0.2
convergence_decay_rate:=0.15
convergence_min_fill_periods:=2.0
gaussian_fill_amplitude:=5.0
gaussian_fill_min_sigma:=3.16
gaussian_fill_use_recent_fraction:=0.2
```

### `hb_escape_shallow_acoustic.bash`

File:

`ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_shallow_acoustic.bash`

Purpose:

- Flexible baseline HBESC tester.
- Lets us select cost-map variant and starting position without editing files.

Supported cost variants:

```bash
original
A3p0
A2p0
A1p0
globalW25
globalW30
globalW40
```

Supported start presets:

```bash
near0     -> (0, 0)
near0p5   -> (0.5, 0.5)
near1     -> (1, 1)
far       -> (-2, -2)
```

Custom numeric starts are also supported:

```bash
bash hb_escape_shallow_acoustic.bash A2p0 0.25 0.25
```

Example successful run command:

```bash
bash /home/mattb/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_shallow_acoustic.bash globalW40 near1
```

## New Cost Function Files

Original cost map:

`2D_local_min.json`

```text
J(x,y) =
2
- 4*exp(-((x-2)^2 + (y-2)^2)/20)
- 10*exp(-((x-10)^2 + (y-10)^2)/10)
```

Local basin: near `(2,2)`.

Global basin: near `(10,10)`.

### Shallow Local-Well Variants

These kept the global term unchanged and reduced only the local-well amplitude.

`2D_local_min_A3p0.json`

```text
2 - 3*exp(-((x-2)^2 + (y-2)^2)/20)
  - 10*exp(-((x-10)^2 + (y-10)^2)/10)
```

Change from original:

```diff
- local amplitude: 4
+ local amplitude: 3
```

`2D_local_min_A2p0.json`

```text
2 - 2*exp(-((x-2)^2 + (y-2)^2)/20)
  - 10*exp(-((x-10)^2 + (y-10)^2)/10)
```

Change from original:

```diff
- local amplitude: 4
+ local amplitude: 2
```

`2D_local_min_A1p0.json`

```text
2 - 1*exp(-((x-2)^2 + (y-2)^2)/20)
  - 10*exp(-((x-10)^2 + (y-10)^2)/10)
```

Change from original:

```diff
- local amplitude: 4
+ local amplitude: 1
```

Result:

- These did not produce reliable global convergence.
- From far starts, `A2p0` and `A1p0` could drift to the flat plateau.
- From near starts, they still tended to orbit/trap near the local region.

### Wider Global-Well Variants

These kept the local well unchanged and widened the global well so the robot
feels the pull toward `(10,10)` earlier.

`2D_local_min_globalW25.json`

```text
2 - 4*exp(-((x-2)^2 + (y-2)^2)/20)
  - 10*exp(-((x-10)^2 + (y-10)^2)/25)
```

Change from original:

```diff
- global denominator: 10
+ global denominator: 25
```

`2D_local_min_globalW30.json`

```text
2 - 4*exp(-((x-2)^2 + (y-2)^2)/20)
  - 10*exp(-((x-10)^2 + (y-10)^2)/30)
```

Change from original:

```diff
- global denominator: 10
+ global denominator: 30
```

`2D_local_min_globalW40.json`

```text
2 - 4*exp(-((x-2)^2 + (y-2)^2)/20)
  - 10*exp(-((x-10)^2 + (y-10)^2)/40)
```

Change from original:

```diff
- global denominator: 10
+ global denominator: 40
```

Approximate local-to-barrier heights along the diagonal:

```text
original:  2.785
globalW25: 1.091
globalW30: 0.692
globalW40: 0.181
```

Result:

- `globalW25`: still local orbit/trap.
- `globalW30`: still local orbit/trap.
- `globalW40`: successful global-basin convergence.

## Process/Runtime Cleanup

Problem:

- Gazebo stopped popping up, while live plots still launched.

Cause found:

- Stale host process:

```bash
gzserver --verbose -s libgazebo_ros_init.so -s libgazebo_ros_factory.so worlds/gazebo_empty.world
```

Action:

- Killed stale `gzserver` process.

Recommended manual reset commands:

```bash
pkill -f "gzserver"
pkill -f "gzclient"
pkill -f "gazebo --verbose"
pkill -f "spawn_entity.py"
pkill -f "controller_manager/spawner"
pkill -f "ros2 run ros_esc"
ros2 daemon stop
ros2 daemon start
```

## Run Results Reviewed

### Baseline PDE-Off Check Before New Escape Config

Run:

`Test_2026-04-22_11-42-27`

Mode:

- `use_pde_extensions:=False`
- raw cost topic
- no Gaussian fill

Result:

- Final position about `(2.111, 1.875)`.
- Final cost about `-1.9895`.
- Confirmed baseline HBESC could settle at the local minimum near `(2,2)`.

Note:

- That run had evidence of a non-clean Gazebo start, so later Gazebo cleanup was done.

### Gaussian-Fill Verification

Run:

`Test_2026-04-22_12-35-15`

Mode:

- `use_pde_extensions:=True`
- `/cost_modified`
- Gaussian fill enabled

Result:

- Convergence event and Gaussian fill fired.
- Left local basin near `(2,2)`.
- Final position about `(9.968, 10.187)`.
- Final cost about `-7.98`.
- Confirmed Gaussian-fill HBESC path still worked.

### First Dedicated Baseline Escape Attempt

Run:

`Test_2026-04-22_12-38-51`

Config:

- `2D_local_min.json`
- start `(-2,-2)`
- `heavyball_escape_controller_full_rotation.json`
- initial escape gains: `k_vx=1.0`, `k_wz=5.0`

Result:

- Did not reach `(10,10)`.
- Settled into orbit around local region.
- Ended around `(1.10, 3.01)`.
- Final cost about `-1.62`.
- Forward velocity saturated at about `0.2419 m/s`.

### Shallow Local-Well Sweep From Far Start

Runs:

- `Test_2026-04-22_12-54-45`: `A3p0`
- `Test_2026-04-22_12-57-45`: `A2p0`
- `Test_2026-04-22_12-59-36`: `A1p0`

Results:

- `A3p0`: local orbit near `(2,2)`.
- `A2p0`: ran to far-field plateau, cost `2.0`.
- `A1p0`: ran to far-field plateau, cost `2.0`.

Interpretation:

- Reducing the local-well amplitude alone can weaken useful gradient structure.
- Too-shallow cases can drift into the flat plateau instead of escaping to `(10,10)`.

### Near-Start Shallow-Well Sweep

Runs reviewed:

- `Test_2026-04-22_13-28-37`: `A1p0`, near `(1,1)`
- `Test_2026-04-22_13-30-16`: `A1p0`, near `(0.5,0.5)`
- `Test_2026-04-22_13-32-03`: `A2p0`, near `(1,1)`, short run
- `Test_2026-04-22_13-32-51`: `A2p0`, near `(1,1)`
- `Test_2026-04-22_13-34-12`: `A2p0`, near `(0.5,0.5)`
- `Test_2026-04-22_13-35-54`: `A3p0`, near `(1,1)`
- `Test_2026-04-22_13-37-17`: `A3p0`, near `(0.5,0.5)`
- `Test_2026-04-22_13-38-28`: original, near `(1,1)`

Result:

- None reached global basin.
- All classified as local orbit/trap.
- Forward velocity was saturated for most of these runs.

### Controller Gain Reduction

Change:

```diff
-k_vx = 1.0
-k_wz = 5.0
+k_vx = 0.2
+k_wz = 2.0
```

Reason:

- Logs showed `vx` saturated in 94-100% of the earlier runs.
- Lowering vehicle gains preserves the HeavyBall signal shape better while keeping
  the physical velocity limit unchanged.

Runs:

- `Test_2026-04-22_14-03-12`: `A2p0`, near `(1,1)`
- `Test_2026-04-22_14-05-24`: `A2p0`, near `(0.5,0.5)`
- `Test_2026-04-22_14-07-58`: `A1p0`, near `(1,1)`

Result:

- Still did not escape to `(10,10)`.
- Continued local orbit/trap behavior.

### Wider Global-Well Sweep

Runs:

- `Test_2026-04-22_14-41-06`: `globalW25`, near `(1,1)`
- `Test_2026-04-22_14-44-34`: `globalW30`, near `(1,1)`
- `Test_2026-04-22_14-47-48`: `globalW40`, near `(1,1)`
- `Test_2026-04-22_14-50-06`: `globalW40`, near `(0,0)`

Results:

`globalW25`:

- Stayed local/orbit.
- Ended around `(2.817, 0.822)`.
- Did not reach global basin.

`globalW30`:

- Stayed local/orbit.
- Ended around `(2.549, 3.995)`.
- Did not reach global basin.

`globalW40`, near `(1,1)`:

- Successful global-basin convergence.
- Came near `(2,2)` first.
- Left local basin at about `t = 19.816`.
- Ended around `(9.489, 8.653)`.
- Tail mean position about `(9.874, 9.866)`.
- Tail mean cost about `-7.518`.
- Closest distance to `(10,10)` about `1.38`.

`globalW40`, near `(0,0)`:

- Successful global-basin convergence.
- Ended around `(8.772, 10.691)`.
- Tail mean position about `(9.886, 10.110)`.
- Tail mean cost about `-7.517`.
- Closest distance to `(10,10)` about `1.38`.

## Physical Limit Check

Current escape controller:

```json
"set_max_vx": null,
"set_max_wz": 0.75
```

Computed from physical wheel parameters:

```text
max_vx = 0.2419026343264141 m/s
```

Observed in successful `globalW40` runs:

```text
max |vx| = 0.2419 m/s
max |wz| = 0.75 rad/s
```

Conclusion:

- The robot often saturates at the configured physical velocity limits.
- It does not exceed those limits.
- The successful `globalW40` result is therefore still physical-limit-respecting
  with the current controller configuration.

## Validation Performed

- Ran `bash -n` on new/modified bash scripts.
- Ran Python JSON parsing on new JSON files.
- Parsed `gazebo.launch.xml` with Python XML parsing after updating the default
  controller path.
- Instantiated the new escape controller config once via the ROS config parser.
- Verified logs for:
  - cost config used,
  - PDE on/off routing,
  - final odometry,
  - final cost,
  - max commanded `vx`/`wz`.

## Current Recommended Run Commands

Working Gaussian-fill HBESC:

```bash
bash /home/mattb/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_gaussian_fill_acoustic.bash
```

Baseline HBESC momentum escape with widened global basin:

```bash
bash /home/mattb/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_shallow_acoustic.bash globalW40 near1
```

Alternative successful baseline start:

```bash
bash /home/mattb/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_shallow_acoustic.bash globalW40 near0
```

## Source Control Notes

Intentional new source files from this session:

- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/heavyball_controller_full_rotation.json`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/heavyball_escape_controller_full_rotation.json`
- `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_acoustic.bash`
- `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_gaussian_fill_acoustic.bash`
- `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_shallow_acoustic.bash`
- `ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/2D_local_min_A1p0.json`
- `ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/2D_local_min_A2p0.json`
- `ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/2D_local_min_A3p0.json`
- `ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/2D_local_min_globalW25.json`
- `ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/2D_local_min_globalW30.json`
- `ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/2D_local_min_globalW40.json`

Intentional modified source file:

- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`

Intentional deleted/retired source files:

- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/adaptive_methods/heavyball_controller_full_rotation.json`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/adaptive_methods/heavyball_escape_controller_full_rotation.json`
- `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_acoustic.bash`

Untracked `.codex` appears in `git status`, but it is not part of the HBESC
source changes documented here.
