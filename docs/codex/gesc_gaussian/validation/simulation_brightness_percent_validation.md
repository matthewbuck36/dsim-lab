# Simulation percentage brightness validation

## Result and scope

The input/display interface passes its declared host qualification. The
conversion is `nominal_lumens = brightness_percent * 16.0`, with finite
0–100 input validation and a zero/off boundary. Equivalent inputs preserve
the existing sensor cost values, sign, units, and reference normalization.

The starting checkout was clean at `01e7645`. This work follows
`plans/simulation_brightness_percent_plan.md`; it does not reopen a frozen
Phase 08 experiment or mark outstanding physical work complete. All 291
protected historical/scenario/shared-algorithm files match their pre-edit
SHA-256 hashes. No physical source, snapshot, mount, device, or graph was used.

## Regressions

From the repository root:

```bash
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
export PYTHONPATH="$PWD/ros2_ws/src/ros_esc:$PYTHONPATH"
export MPLBACKEND=Agg
timeout 240 python3 -m pytest -q \
  ros2_ws/src/ros_esc/test/test_light_brightness.py \
  ros2_ws/src/ros_esc/test/test_legacy_behavior.py \
  ros2_ws/src/ros_esc/test/test_observability_contract.py \
  ros2_ws/src/ros_esc/test/test_scenario_schema.py \
  ros2_ws/src/ros_esc/test/test_scenario_runner.py \
  ros2_ws/src/ros_esc/test/test_aggregate_field_truth.py
```

Result: **491 passed, 1 skipped**, 173.56 seconds. Log:
`/tmp/dsim_brightness_percent/regressions.log`. The single skipped test is the
opt-in recorded Gazebo end-to-end test; no simulation was launched.

After the final JSON configuration/event coverage was added:

```bash
source /tmp/dsim_brightness_percent/install/setup.bash
timeout 120 python3 -m pytest -q ros2_ws/src/ros_esc/test/test_light_brightness.py
```

Result: **30 passed**, 1.26 seconds. Log:
`/tmp/dsim_brightness_percent/focused_final.log`. Counts overlap and must not
be added together. Coverage includes voltage/resistance equivalence at
multiple poses, zero/off, nonfinite/range/type rejection, dual-unit rejection,
unchanged high legacy inputs, CLI precedence, JSON-only configuration,
configuration events, plot labels, scenario expansion, metadata, and legacy
launch arguments.

## Build and installed paths

```bash
source /opt/ros/humble/setup.bash
timeout --signal=INT --kill-after=10s 180s colcon \
  --log-base /tmp/dsim_brightness_percent/build_logs build \
  --base-paths ros2_ws/src \
  --build-base /tmp/dsim_brightness_percent/build \
  --install-base /tmp/dsim_brightness_percent/install \
  --symlink-install \
  --packages-select ros_esc_interfaces turtlebot3_rotating_sensor ros_esc
source /tmp/dsim_brightness_percent/install/setup.bash
timeout 30 python3 /tmp/dsim_brightness_percent/installed_check.py
```

Build result: **three packages passed in 15.9 seconds**. Log:
`/tmp/dsim_brightness_percent/build.log`. The installed check constructs the
central XML and resolves all five percentage slots on all three cost/plot
commands, including 25%, 100%, and the unused legacy sentinels. It executes
argument declarations only, with no process-starting launch actions. It also
loads the installed example and verifies the 25%/100% sources. Artifacts:
`installed_check.log`, `installed_check.py`, and
`resolved_launch_commands.txt` under `/tmp/dsim_brightness_percent/`.

```bash
timeout 30 ros2 run ros_esc run_scenario \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/brightness_percent_example.yaml \
  --operator audit --dry-run \
  --runs-root /tmp/dsim_brightness_percent/dry_run
timeout 30 ros2 run ros_esc cost_surface_plotter \
  ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json \
  --light_source_count 2 \
  --light_source_1_x 1.0 --light_source_1_y 0.5 \
  --light_source_1_brightness_percent 25 \
  --light_source_2_x 3.5 --light_source_2_y 3.5 \
  --light_source_2_brightness_percent 100 \
  --resolution 12 --orientation-samples 8 --no-show \
  --output /tmp/dsim_brightness_percent/percentage_surface.png
```

Both commands pass. The preview expands one case without starting ROS/Gazebo;
the offline plot renders `L1: 25%` and `L2: 100%`, verified by image inspection.
The coarse plot is an interface smoke artifact, not a new experimental result.
Logs: `/tmp/dsim_brightness_percent/dry_run.log` and `plot.log`.

## Static checks and limitations

Changed Python files parse and pass fatal flake8 (`E9,F63,F7,F82`); changed
relative documentation links resolve; `git diff --check` passes. Protected
hashes are in `/tmp/dsim_brightness_percent/protected_before.json`.

Initial diagnostics found a test fixture using `--config` instead of the
existing positional plotter config and a noncanonical `local` evaluation role;
both were corrected before qualification. The installed-check script was
adapted to Humble's Parser return order and to resolve plain executable
actions without evaluating ROS Node execution-local substitutions. These
diagnostics made no launch or hardware attempt and did not change acceptance
thresholds. The initial focused diagnostic log is retained as `focused.log`.

Full inherited style lint, Gazebo behavioral trials, frozen matrices,
physical hardware, and measured Hue dimming calibration were not required or
run. Old lumen fields/defaults and above-1600 historical scenarios remain
compatible. Set percentages explicitly on every enabled light for new
Hue-style simulations. The SDF lamps remain visual markers; only the
simulated sensor model and its input/display conventions changed.
