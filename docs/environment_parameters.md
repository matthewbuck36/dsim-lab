# Simulation and physical environment parameters

Verified from source on 2026-09-08. `dsim-lab` is the simulation/Gazebo checkout.
`physical_TB3_files_snapshot/pi` is an offline copy of physical Pi source;
`tb3-pi` exposes the physical Pi home only while SSHFS is mounted. Running a
physical-source test on the laptop does not make that package a simulation
package. This guide documents differences; it does not change runtime values.

The physical source inspected for this audit was the snapshot refreshed from
the Pi earlier that day. The Pi was unmounted during this documentation task.
Selected settings below compare the v8.12 simulation scenario with the Phase 09
two-source physical wrapper, not every historical ESC experiment.

## Environment requirements

| Setting or interface | Simulation/Gazebo | Physical robot and its offline source |
| --- | --- | --- |
| Algorithm-node `use_sim_time` | Boolean `True`, driven by Gazebo `/clock` | Boolean `False`, system/wall time |
| `supervisor_use_sim_time` launch argument | `True` | `False` |
| Controller/filter clock CLI | `--use-sim-time True` | `--use-sim-time False` |
| `observability_source_mode` | `simulation` | `physical` |
| Recorder selection | `record_run --mode simulation`; record `/clock` | `record_run --mode physical`; physical heartbeat/rotation evidence |
| Algorithm pose provider | Gazebo `/odom`, or an explicitly selected simulated delay relay | OpenCR wheel/IMU-backed `/odom`; never replace it with Vicon |
| Sensor and rotation interfaces | Modeled cost, Gazebo `/joint_states`, `/velocity_controller/commands` | Serial photoresistor, GPIO encoder, gated physical rotation owner |
| Light inputs | `light_N_brightness_percent` / `brightness_percent` for new simulations; nominal 1600-lumen conversion | Measured voltage; simulation source positions/brightness/roles are not controller inputs or a physical calibration |
| JSON source-file paths | `~/dsim-lab/ros2_ws/src/...` | Pi paths `~/ros2_ws/src/...`; do not replace them with laptop snapshot paths |
| Workspace/launch package | `dsim-lab/ros2_ws`, `turtlebot3_rotating_sensor` | Pi `~/ros2_ws`, `turtlebot3_vehicle_nodes`; offline source under snapshot `pi/ros2_ws` |

### Clock selection must survive construction

The shared `ros_esc/clock_configuration.py` helper
`apply_legacy_sim_time_default` preserves an explicit startup override and
defaults to `True` only when no override exists. Modified-cost, PDE-history,
PDE-cost-history, convergence, and Gaussian-fill owners use it. A `True`
default in shared physical source is therefore not evidence of an active
physical clock error: inspect the launch override and resolved node parameter.
Do not unconditionally reset `use_sim_time` after node construction or globally
replace shared defaults with `False`.

Controller/filter entry points have strict argparse interfaces. Their clock
switch is `--use-sim-time`, not an extra ROS `-p` argument appended to that
legacy CLI. The selected physical launch supplies `False` to these interfaces
and the ROS-parameter owners; its recorder also enforces the physical clock
contract. Use typed booleans in YAML/ROS parameters, not quoted strings.

This clock rule concerns algorithm nodes. The existing recorder deliberately
starts `ros2 bag record` without `--use-sim-time` in both modes, while recording
`/clock` in simulation. Do not force bag orchestration/watchdogs onto simulated
time merely because the algorithm uses it.

## Selected configuration differences

These are current selected-case choices, not universal rules for all physical
robots or all simulated experiments. Preserve their owners; a later approved
tuning change must update its scenario/wrapper/config and this guidance.

| Parameter | Selected v8.12 simulation | Selected Phase 09 physical |
| --- | --- | --- |
| Controller JSON `set_max_vx` | `0.1` m/s | `0.05` m/s |
| Controller JSON `set_max_wz` | `0.5` rad/s | `0.30` rad/s |
| Launch `pde_omega` | `5.0` rad/s | `2.09439510239` rad/s |
| Launch `startup_timeout_sec` (supervisor/controller) | `5.0` s | `100.0` s from wrapper |
| Recorder runtime heartbeat stale threshold | `heartbeat_stale_sec=0.5` s | `runtime_heartbeat_stale_sec=1.5` s |
| Recorder additional stale-only runtime grace | None | `runtime_heartbeat_grace_sec=0.5` s |
| `pde_cost_history_topic` (retained/legacy cost history) | Raw `/turtlebot3/cost_value_chatter`, or its explicitly selected delay relay | `/cost_modified` |
| Vicon evaluation | No physical Vicon adapter | `enable_vicon_evaluation=True`, topic `/gesc_gaussian/evaluation/vicon_odom`; evaluation only |

The simulation scenario is
`ros_esc/ros_esc/scenario_runner/scenarios/phase08_v8_12_interior_anchor_visible_probe.yaml`;
the broad-matrix YAML uses the same selected profile. The scenario runner
selects the GESC JSON
`ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage.json`.
The physical wrapper selects
`turtlebot3_vehicle_nodes/config_files/controller_config_files/phase09_gesc_controller_full_rotation_voltage.json`.
The generic GESC JSON also present in physical source still has `0.1`/`0.5`;
that is not the selected physical controller file.

The physical recorder grace applies only to stale-heartbeat errors; semantic
faults remain immediate. It is not a controller freshness override. The cost-
history routing difference affects retained history and the legacy fitting
buffer: robust Gaussian estimation uses typed raw source-cost snapshots in
both environments and returns before the legacy fit. Preserve this existing
routing unless separately reviewing its legacy/history contract. Positional
`/pde_history` still participates in convergence/affine processing.

Shared geometry, GESC/filter gains, spin RPM, and equal selected-profile values
are intentionally omitted. In particular, do not infer environment-specific
recenter behavior by comparing a generic launch default with a selected
scenario override.

## Physical hardware and operator settings

These checked defaults belong to the current lab setup, not arbitrary hardware.

| Setting | Current selected physical value and owner |
| --- | --- |
| `photoresistor_serial_port` | `/dev/ttyUSB0`; wrapper `--serial-device DEVICE` override |
| `photoresistor_baud_rate` | `9600` baud |
| `photoresistor_serial_timeout_sec` | `0.50` s |
| `turtlebot3_usb_port` | `/dev/ttyACM0`; wrapper `--opencr-device DEVICE` or `PHASE09_OPENCR_DEVICE` environment override; distinct from photoresistor device |
| `TURTLEBOT3_MODEL` | Defaults to `burger`; wrapper respects an explicit existing value |
| Sensor selection | `sensor_name=Photoresistor`, `sensor_datatype=Voltage`, `sensor_units=Volts` |
| Physical timekeeper | `mode="real time"` |
| Rotation GPIO | Servo BCM18; encoder BCM23 |
| `rotating_frame_init_angular_position` | `-90` degrees, physical `--starting-position`; simulation instead initializes its URDF joint position to `0.0` radians |
| `rotation_authorization_stale_sec`, `rotation_encoder_stale_sec` | `0.50` s each |
| `rotation_settle_sec` | `10.0` s |
| Recorder startup allowances | Preflight `45.0` s and rotation startup `45.0` s, distinct from the algorithm startup argument's `100.0` s |
| Vicon UDP endpoint | Current adapter `192.168.1.6:12346`; Windows server is external; evaluation coordinates convert mm to m |

The selected wrapper uses the no-lidar base bringup to avoid sharing the
photoresistor serial device. It sources ROS Humble, then `~/turtlebot3_ws`,
then `~/ros2_ws`; it resolves per-run physical JSON object paths. A laptop
overlay is not a replacement for a Pi build or its installed overlay.

The selected photoresistor adapter leaves `--source-score-enabled=False` and
has no calibration file by default. Its calibration YAML is an inert,
uncalibrated template, not evidence of measured calibration or a new runtime
gate. Vicon is needed for complete selected evaluation evidence; it must not
become algorithm localization, source ranking, fill placement, or stopping.

## Select the actual entry point

For selected simulation, follow the scenario runner and its resolved launch
arguments. Bare `gazebo.launch.xml` retains `algorithm_profile=legacy` and
an HBESC controller default. A wrapper whose filename contains GESC/Gaussian
does not by itself select `robust_gaussian_v1`.

For selected physical operation, the existing operator-owned entry point is
`turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values/gesc_gaussian_two_source_voltage.bash`.
It supplies the selected clocks, controller, tuning, and recorder mode to
`turtlebot3_vehicle_nodes/launch/gesc_gaussian_two_source.launch.xml`.
The bare XML also has legacy defaults. `phase09_selected_profile.yaml` is
recorded with `--evidence-file`; editing that record does not apply ROS
parameters. Older physical Resistance/Ohms launches remain separate legacy
workflows and are not certified by this selected-path audit.

Before parameter edits, trace: selected wrapper/scenario → launch arguments →
node CLI/ROS overrides → selected JSON/YAML → resolved node values. Do not
copy a simulation launch or a historical backup over the physical package.
For an already authorized running graph, bounded `ros2 param get NODE
use_sim_time` checks can verify the selected clock; do not start hardware just
to inspect documentation. Existing clock regression tests cover both values
without starting a robot or Gazebo.

## Source map and instruction placement

Simulation sources are under `dsim-lab/ros2_ws/src`; physical counterparts are
under `physical_TB3_files_snapshot/pi/ros2_ws/src` offline or `tb3-pi/ros2_ws/src`
when mounted. Relevant owners, relative to those source roots:

- `turtlebot3_rotating_sensor/launch/gazebo.launch.xml` and
  `turtlebot3_rotating_sensor/urdf/turtlebot3_rotating_sensor.urdf` (simulation).
- `turtlebot3_vehicle_nodes/launch/gesc_gaussian_two_source.launch.xml` and
  the selected physical wrapper above (physical).
- `ros_esc/ros_esc/{clock_configuration.py,experiment_recording/record_run.py,experiment_recording/topic_manifest.yaml}`.
- `ros_esc/ros_esc/{controller_node/controller_node_script.py,filter_node/filter_node_script.py}`.
- `ros_esc/ros_esc/scenario_runner/run_scenario.py` (simulation selection).
- `turtlebot3_vehicle_nodes/config_files/gesc_gaussian/phase09_selected_profile.yaml`
  (physical record, not a runtime parameter loader).
- `ros_esc/test/test_clock_configuration.py` (both source trees).

The roots use both README and `AGENTS.md`: the latter tells Codex to read the
environment guidance. For a non-Git folder, start the session at its documented
root or explicitly supply its `AGENTS.md`; do not assume ancestor instructions
are discovered from an arbitrary nested working directory. This follows
[OpenAI's instruction discovery documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

`tb3-pi/README.md` and `tb3-pi/AGENTS.md` were written while unmounted. SSHFS
hides them while mounted; they are not transferred to the Pi and cannot guide
a new agent through that hidden path. The always-available versioned copies
are in [environment_guides](environment_guides/README.md). When working on a
mounted Pi from this checkout, read the physical guide explicitly. No agent
configuration on the live Pi was installed by this documentation task.
