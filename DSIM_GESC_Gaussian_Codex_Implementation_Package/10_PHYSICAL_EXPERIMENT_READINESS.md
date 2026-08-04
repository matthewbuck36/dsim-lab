# Physical GESC + Gaussian Two-Source Operator Checklist

<!-- MBuck 2026-08-03: Align the selected physical run with the established lab Vicon SOP and a single Bash entry point. -->

This is the current Phase 09 M8C operator procedure. It supersedes the earlier
M8B commissioning sequence that required separate site files, stationary
preflight/approval, `--check-only`, typed authorization, Vicon identity fields,
and file hashes. Those M8B requirements remain in historical status and handoff
records only; the selected wrapper does not consult them.

The intended experiment is a human-supervised, exploratory physical test of the
cumulative terminal v8.12 GESC + Gaussian algorithm in a clear, open room with
two light sources. It is not a claim of broad physical robustness, obstacle
avoidance, or arbitrary-layout readiness.

## Current source-integration evidence

M8B snapshot implementation, host qualification, and reviewed source-only Pi
sync passed before this simplification. The rollback backup is
`/home/mattb/tb3-pi/phase09_backups/20260802T031409Z_m8b`; that M8B snapshot and
Pi matched `345/345` regular-file hashes and `432/432` inventory entries. This
is retained provenance, not proof of a later M8C build or physical run.

M8C implementation, host validation, recovery reseal, and the reviewed
source-only Pi transfer passed on 2026-08-03 local time. The current snapshot
and mounted Pi source match `342/342` regular-file hashes and `430/430`
type/mode/size inventory entries. The M8C Pi rollback is:

```text
/home/mattb/tb3-pi/phase09_backups/
  20260804T011049Z_m8c_pre_simplification
```

The wrapper's host-only `--check-only` path rebuilt all three selected packages
and passed without opening hardware. No on-Pi build, live ROS graph, Vicon
connection, serial/GPIO access, actuator command, lamp response, or robot motion
was run by Codex. Those are exercised for the first time by the human-operated
lab procedure below, not by another repository authorization gate.

## Before the run

- [ ] Follow `DSIM - TurtleBot3 Vicon Setup.pdf` to prepare Vicon Tracker, the
  network, TurtleBot3, and rotating light-sensor hardware.
- [ ] Make sure every required Vicon camera is healthy in Tracker and start the
  unchanged `vicon-tracker-server.py` on the Windows Vicon computer.
- [ ] Arrange the two lamps for the selected experiment and keep lamp
  coordinates/intensities outside controller inputs.
- [ ] Clear the floor and keep the robot within sight and reach of the person
  supervising the run.
- [ ] Keep the robot terminal focused so `Ctrl+C` is immediately available.

No separate build command, site-configuration copy, stationary preflight,
calibration approval, `--check-only`, typed `RUN`, subject/segment entry,
server-file SHA-256, handoff authorization, or `PHYSICAL READY` tag is required.
The experiment may expose physical issues; stop with `Ctrl+C`, retain the run,
and diagnose the evidence rather than hiding the result.

## Start the selected experiment

SSH to the Pi and run exactly:

```bash
cd ~/ros2_ws/src/turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values
./gesc_gaussian_two_source_voltage.bash
```

The selected wrapper is responsible for:

- building exactly `ros_esc_interfaces`, `ros_esc`, and
  `turtlebot3_vehicle_nodes`, then sourcing `install/setup.bash`;
- starting `pigpiod` only when it is not already running;
- launching the dedicated `gesc_gaussian_two_source` graph without changing any
  legacy ESC Bash file or launch;
- creating and printing one unique run directory before motion;
- starting the sole managed recorder before the controller becomes ready; and
- printing bounded one-second live diagnostics in the same terminal.

If `pigpiod` is absent and the Pi's normal sudo policy requires authentication,
`sudo` may request the Pi password once. That is ordinary operating-system
authentication from the lab SOP, not a Phase 09 confirmation or readiness gate.

## Control and evaluation contract

- [ ] Wheel/IMU-backed `/odom` is the sole algorithm pose.
- [ ] Photoresistor voltage/raw minimization cost, permitted IMU data, known
  source count, and typed Gaussian state are the only selected controller
  inputs.
- [ ] The unchanged Windows server's legacy `7f` stream is converted by the
  existing odometry owner to `nav_msgs/msg/Odometry` on
  `/gesc_gaussian/evaluation/vicon_odom`.
- [ ] Vicon remains passive evaluation data. It cannot affect controller
  readiness, motion, fill placement, escape, ranking, or stopping.
- [ ] Missing, stale, or incomplete Vicon is plainly labeled in the live
  diagnostics and retained validation, but never blocks or stops motion.
- [ ] Legacy RMSprop, Adagrad, and other ESC wrappers, launches, parameters, and
  owners remain selectable and unchanged.

## What to watch

The terminal should show the run directory and labeled live summaries when data
is available, including readiness, sensor voltage/raw cost, augmented-cost
components, filter output, controller/supervisor state, fill count, `/odom`,
evaluation-only Vicon odometry, and final linear/angular command.

The run directory should retain one sqlite3 rosbag with the legacy sensor,
encoder, odometry, filter, command, and timekeeper streams plus typed
GESC/Gaussian diagnostics and `/gesc_gaussian/evaluation/vicon_odom`. It should
also retain console output, resolved metadata/configuration, notes,
completeness/integrity results, and shutdown evidence.

Vicon absence is an evaluation-quality warning, not a robot-motion fault. A
photoresistor, `/odom`, required IMU, controller, recorder, or command-path fault
may still trigger the algorithm's automatic zero-command behavior.

## Stop and save

1. Press `Ctrl+C` once in the Pi experiment terminal.
2. Wait for the wrapper to report readiness false, the managed stop/final-zero
   sequence, recorded zero dwell, rosbag finalization, bounded validation, and
   the final retained run directory.
3. Only after Pi cleanup completes, stop `vicon-tracker-server.py` on Windows.
4. Keep the run directory whether the behavior succeeded, was interrupted, or
   exposed a hardware/algorithm issue.

Arbitrary intensity/layout matrices, three-light cases, boundaries, walls,
obstacles, and broad robustness remain future work unless separately planned.
