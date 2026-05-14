# HBESC Generalization Work Log - 2026-05-13

This file records the Heavy-Ball ESC generalization changes from the
2026-05-13 Codex session. The goal was to preserve the known-good baseline and
one-shot Gaussian-fill runs while adding configurable escape policies and
scenario-style experiment inputs.

## Starting Point

- Git working tree was clean before edits.
- Baseline HBESC mode:
  - `use_pde_extensions:=False`
  - raw cost enters the filter directly.
  - no Gaussian fills are published.
- Gaussian-fill HBESC mode:
  - `use_pde_extensions:=True`
  - cost is routed through `/cost_modified`.
  - `gaussian_fill_node` previously published exactly one fill and then stopped.
- Existing `modified_cost_node` already supported multiple stored fill terms, so
  the main missing piece was the Gaussian-fill policy logic.

## Files Modified

### `gaussian_fill_script.py`

File:

`ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`

Implemented a configurable escape policy layer.

New parameter:

```text
escape_policy
```

Supported values:

```text
none
conditional_gaussian_fill
multi_gaussian_fill
```

Aliases also accepted:

```text
off, false, disabled -> none
one_shot, single, gaussian_fill, conditional -> conditional_gaussian_fill
multi -> multi_gaussian_fill
```

New fill-control parameters:

```text
max_fills
fill_cooldown_sec
min_distance_between_fills
```

Existing parameters now explicitly supported through launch:

```text
max_sigma
min_points
```

Behavior changes:

- Previous hard-coded one-shot behavior:

```text
has_filled == True -> ignore every later convergence event
```

- New behavior:

```text
escape_policy == none -> publish no fills
max_fills == 1 -> preserve one-shot behavior
max_fills > 1 -> allow repeated basin-memory fills
max_fills == -1 -> allow unlimited fills
fill_cooldown_sec > 0 -> block rapid repeated fills
min_distance_between_fills > 0 -> block duplicate nearby fills
```

The published fill message format did not change:

```text
/cost_bias data = [A, mu_x, mu_y, sigma]
```

This keeps compatibility with `modified_cost_node`.

### `gazebo.launch.xml`

File:

`ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`

Added launch arguments:

```xml
<arg name="escape_policy" default="conditional_gaussian_fill"/>
<arg name="gaussian_fill_max_sigma" default="5.0"/>
<arg name="gaussian_fill_min_points" default="50"/>
<arg name="gaussian_fill_max_fills" default="1"/>
<arg name="gaussian_fill_cooldown_sec" default="0.0"/>
<arg name="gaussian_fill_min_distance_between_fills" default="0.0"/>
```

Preserved existing default behavior:

```xml
<arg name="use_pde_extensions" default="False"/>
<arg name="gaussian_fill_amplitude" default="5.0"/>
<arg name="gaussian_fill_min_sigma" default="3.16"/>
<arg name="gaussian_fill_use_recent_fraction" default="0.2"/>
```

Important compatibility note:

- `use_pde_extensions` still controls whether the PDE/modified-cost/fill nodes
  are launched.
- `escape_policy` controls what the Gaussian-fill node does once those nodes are
  launched.
- This avoids breaking the existing bash scripts and previously validated runs.

### Existing Bash Scripts

Files:

```text
ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_acoustic.bash
ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_shallow_acoustic.bash
ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_gaussian_fill_acoustic.bash
```

Baseline scripts now explicitly state:

```bash
use_pde_extensions:='False'
escape_policy:='none'
```

The Gaussian-fill script now explicitly states:

```bash
use_pde_extensions:='True'
escape_policy:='conditional_gaussian_fill'
gaussian_fill_max_fills:=1
gaussian_fill_cooldown_sec:=0.0
gaussian_fill_min_distance_between_fills:=0.0
```

This preserves the known-good one-fill run while making the policy visible in
the command.

## Files Added

### Generic Scenario Runner

File:

`ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash`

Purpose:

- Run HBESC experiments from a single scenario JSON file.
- Keep map, start pose, controller, and escape policy together.
- Reduce the need to create a new bash script for every experiment.

Default command:

```bash
bash ~/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash
```

Dry-run command that prints the resolved `ros2 launch` command without
building or starting Gazebo:

```bash
bash ~/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash --dry-run
```

Explicit scenario command:

```bash
bash ~/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash \
  ~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/hb_multi_fill_default.json
```

### Scenario Configs

Directory:

`ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/`

Added:

```text
hb_gaussian_fill_default.json
hb_multi_fill_default.json
hb_baseline_globalW40.json
```

#### `hb_gaussian_fill_default.json`

Purpose:

- Scenario version of the previous known-good Gaussian-fill run.
- Uses the original/default `2D_local_min.json`.
- Starts at `(0, 0)`.
- Uses `heavyball_controller_full_rotation.json`.
- Keeps one-fill behavior.

Key policy settings:

```json
"use_pde_extensions": true,
"escape_policy": "conditional_gaussian_fill",
"gaussian_fill_max_fills": 1,
"gaussian_fill_cooldown_sec": 0.0,
"gaussian_fill_min_distance_between_fills": 0.0
```

#### `hb_multi_fill_default.json`

Purpose:

- First repeated-fill scenario for maps with multiple local minima.
- Starts from the raw cost map.
- Injects fills only after convergence events.

Key policy settings:

```json
"use_pde_extensions": true,
"escape_policy": "multi_gaussian_fill",
"gaussian_fill_max_fills": 5,
"gaussian_fill_cooldown_sec": 10.0,
"gaussian_fill_min_distance_between_fills": 1.0
```

#### `hb_baseline_globalW40.json`

Purpose:

- Scenario version of the successful no-PDE baseline run on
  `2D_local_min_globalW40.json`.
- Starts at `(1, 1)`.
- Uses `heavyball_escape_controller_full_rotation.json`.

Key policy settings:

```json
"use_pde_extensions": false,
"escape_policy": "none"
```

## Parameters Preserved

Known-good conservative Gaussian-fill controller stayed unchanged:

```json
"k_vx": 1.0,
"k_wz": 5.0,
"k": 0.1,
"beta": 1.0,
"input_gain": -1.0,
"set_max_vx": 0.05,
"set_max_wz": 0.25
```

Baseline escape controller stayed unchanged:

```json
"k_vx": 0.2,
"k_wz": 2.0,
"k": 1.0,
"beta": 0.1,
"input_gain": -1.0,
"set_max_vx": null,
"set_max_wz": 0.75
```

Original/default map stayed unchanged:

```text
2D_local_min.json
```

## Validation

Passed:

```bash
python3 -m py_compile ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py
```

Passed:

```bash
python3 -c 'import xml.etree.ElementTree as ET; ET.parse("ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml"); print("xml ok")'
```

Passed:

```bash
python3 -c 'import json, sys; [json.load(open(path, encoding="utf-8")) for path in sys.argv[1:]]; print("json ok")' \
  ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/hb_gaussian_fill_default.json \
  ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/hb_multi_fill_default.json \
  ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/hb_baseline_globalW40.json \
  ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/heavyball_controller_full_rotation.json \
  ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/heavyball_escape_controller_full_rotation.json
```

Passed:

```bash
bash -n ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_acoustic.bash
bash -n ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_shallow_acoustic.bash
bash -n ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_gaussian_fill_acoustic.bash
bash -n ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash
```

Passed:

```bash
bash ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash --dry-run
bash ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash --dry-run \
  ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/hb_multi_fill_default.json
bash ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash --dry-run \
  ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/hb_baseline_globalW40.json
```

Passed:

```bash
git diff --check
```

Passed:

```bash
cd ~/dsim-lab/ros2_ws
colcon build --packages-select ros_esc ros_esc_interfaces turtlebot3_rotating_sensor
```

Build result:

```text
Summary: 3 packages finished
```

## Follow-up Fix

After the first scenario-run attempt, the package build succeeded but sourcing
`install/setup.bash` failed with:

```text
COLCON_TRACE: unbound variable
```

Cause:

- `hb_scenario_acoustic.bash` used `set -u`.
- Colcon's generated setup files can reference `COLCON_TRACE` while it is unset.

Fix:

```diff
-set -euo pipefail
+set -eo pipefail
```

Validation after fix:

```bash
bash -n ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash
bash ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash --dry-run \
  ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/scenarios/hb_gaussian_fill_default.json
```
