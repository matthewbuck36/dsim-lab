# TurtleBot SSHFS mount point — local instructions

**Environment: physical TurtleBot when mounted; local mount-point directory
when unmounted.** These README/AGENTS files were created locally while
unmounted. They are not on the robot. SSHFS hides them while mounted and they
reappear after unmounting; edits made through a mounted path instead affect
the Pi.

Check the exact mount point before treating this directory as robot source:

```bash
findmnt --mountpoint /home/mattb/tb3-pi --output TARGET,SOURCE,FSTYPE
```

An empty result/nonzero exit means this exact mount point is unmounted; do not
mistake the laptop filesystem returned by `findmnt -T` for a live Pi mount.
The expected SSHFS source is `pi@192.168.1.36:/home/pi`; when present, the
physical source root is `ros2_ws/src`. When absent, use the offline snapshot
at `/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src` for source inspection.

While mounted, explicitly read the always-visible copies in
`/home/mattb/dsim-lab/docs/environment_guides/tb3_pi_README.md` and
`tb3_pi_AGENTS.md`. The hidden local AGENTS file cannot automatically guide a
new mounted-folder session. Do not create robot-side documentation just to
make this local file visible.

## Physical parameter contract

Verified against the offline physical source refreshed from the Pi on
2026-09-08. These are physical packages even when edited or tested on the
laptop. The detailed [simulation/physical comparison](/home/mattb/dsim-lab/docs/environment_parameters.md)
records source owners, exceptions, and the simulation values. It is versioned
in `feature/gesc-gaussian-robustness-v1`.

| Environment setting | Required physical selection |
| --- | --- |
| Algorithm-node `use_sim_time` | Boolean `False` (system/wall time) |
| `supervisor_use_sim_time` | `False` |
| Controller/filter clock CLI | `--use-sim-time False` |
| `observability_source_mode` | `physical` |
| Recorder mode | `record_run --mode physical` |
| Algorithm pose provider | OpenCR wheel/IMU `/odom`, not Gazebo or Vicon |
| JSON object paths | Pi `~/ros2_ws/src/...`, not `~/dsim-lab/...` or laptop snapshot paths |
| Sensor/rotation interfaces | Serial photoresistor, GPIO encoder, physical gated rotation owner; no Gazebo joint/controller interfaces |

Shared `ros_esc/clock_configuration.py` deliberately defaults to simulation time
when **no** startup override is supplied. It must preserve explicit physical
`False`. Do not globally change all shared defaults to False, and do not reset
the clock after startup. Controller/filter entry points use their strict
`--use-sim-time` CLI; appending ROS `-p` arguments is not interchangeable.
The recorder enforces the selected physical node-clock contract. Bag recording
and watchdog timing have their own implementation; do not change those clocks
just to match an algorithm-node setting.

## Current selected Phase 09 settings

These are checked selected-case choices, not defaults for every robot or
legacy ESC method. Values shared with selected simulation are omitted.

| Setting | Selected physical value |
| --- | --- |
| Controller JSON `set_max_vx` / `set_max_wz` | `0.05` m/s / `0.30` rad/s (simulation selected: `0.1` / `0.5`) |
| Launch `pde_omega` | `2.09439510239` rad/s (simulation: `5.0`) |
| Launch `startup_timeout_sec` (supervisor/controller) | `100.0` s (simulation: `5.0`) |
| Recorder startup allowances | Preflight `45.0` s, rotation startup `45.0` s |
| Recorder `runtime_heartbeat_stale_sec` | `1.5` s (simulation runtime threshold: `0.5`) |
| Recorder `runtime_heartbeat_grace_sec` | `0.5` s for stale-only faults (simulation: none); not controller freshness |
| `pde_cost_history_topic` | `/cost_modified` (simulation: raw source cost); retained/legacy cost-history routing, not robust Gaussian raw-sample selection |
| Vicon evaluation | `enable_vicon_evaluation=True`; `/gesc_gaussian/evaluation/vicon_odom` |
| `photoresistor_serial_port` | `/dev/ttyUSB0`; wrapper `--serial-device DEVICE` |
| `photoresistor_baud_rate` / `photoresistor_serial_timeout_sec` | `9600` baud / `0.50` s |
| `turtlebot3_usb_port` | `/dev/ttyACM0`; wrapper `--opencr-device DEVICE` or `PHASE09_OPENCR_DEVICE` environment override; distinct from photoresistor port |
| `TURTLEBOT3_MODEL` | Defaults to `burger`; respect the configured model |
| Sensor selection | `Photoresistor`, `Voltage`, `Volts`; physical measurements |
| Physical timekeeper | `mode="real time"` |
| Rotation hardware | Servo BCM18, encoder BCM23 |
| `rotating_frame_init_angular_position` | `-90` degrees, passed as physical `--starting-position`; simulated URDF joint starts at `0.0` radians |
| `rotation_authorization_stale_sec` / `rotation_encoder_stale_sec` | `0.50` s / `0.50` s |
| `rotation_settle_sec` | `10.0` s |
| Current Vicon UDP endpoint | `192.168.1.6:12346`; external Windows server; evaluation only |

The selected no-lidar bringup avoids photoresistor serial contention. Vicon
cannot replace algorithm `/odom` or enter fill, ranking, escape, or stopping
calculations. Its absence makes evaluation incomplete. Simulated
`brightness_percent`, light coordinates, and nominal lumens are not physical
sensor parameters or a measured calibration. Physical source-score reporting
is disabled by default; the calibration YAML is an inert uncalibrated template.

## Follow the effective configuration

Paths below are relative to the physical `ros2_ws/src` root:

- Selected operator wrapper:
  `turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values/gesc_gaussian_two_source_voltage.bash`.
- Selected launch:
  `turtlebot3_vehicle_nodes/launch/gesc_gaussian_two_source.launch.xml`.
- Selected speed configuration:
  `turtlebot3_vehicle_nodes/config_files/controller_config_files/phase09_gesc_controller_full_rotation_voltage.json`.
- Parameter record:
  `turtlebot3_vehicle_nodes/config_files/gesc_gaussian/phase09_selected_profile.yaml`.
- Recorder contract: `ros_esc/ros_esc/experiment_recording/topic_manifest.yaml`.
- Clock regression: `ros_esc/test/test_clock_configuration.py`.

The wrapper selects `robust_gaussian_v1`, clocks, recorder mode, controller
JSON, and overrides. The selected-profile YAML is attached as evidence; it is
**not** loaded as ROS parameters. Bare XML keeps legacy defaults, including
the generic controller JSON with higher `0.1`/`0.5` limits. Older
Resistance/Ohms launches are separate legacy workflows; this selected-path
audit does not certify their resolved clocks or readiness.

Trace wrapper/scenario → launch → CLI/ROS overrides → JSON/YAML → resolved
node values before editing. Preserve shared algorithms and selectable legacy
behavior. The Pi terminal owns physical builds, overlays, devices, recording,
and motion under the user's authorization; these documents are not a launch
or transfer request. Source parity and passing clock tests are not physical
runtime qualification.
