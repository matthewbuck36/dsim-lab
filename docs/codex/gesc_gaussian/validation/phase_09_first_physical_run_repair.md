# Phase 09 first physical-run diagnosis and M8F repair

Date: 2026-08-04
Milestone: M8F
Decision: **SOURCE REPAIR HOST-QUALIFIED AND TRANSFERRED; ON-PI CHECK-ONLY
REBUILD NOT YET RUN; PHYSICAL ALGORITHM RUN NOT DEMONSTRATED**

## Retained failed run

The first selected bare-wrapper attempt is retained unchanged at:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/2026-08-04/
  20260804T201250796597Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_6d9b4ac3
```

Mounted read-only inspection path:

```text
/home/mattb/tb3-pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/
  2026-08-04/
  20260804T201250796597Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_6d9b4ac3
```

This remains failed commissioning evidence. It must not be deleted, retried in
place, or described as a physical GESC + Gaussian result.

## What happened

The selected launch appended the ROS parameter tail
`--ros-args -p use_sim_time:=False` to two executables whose historical
interfaces use strict Python `argparse` parsing. Both executables rejected the
ROS arguments and exited with code 2:

```text
controller_node: error: unrecognized arguments: --ros-args -p use_sim_time:=False
filter_node: error: unrecognized arguments: --ros-args -p use_sim_time:=False
```

The recorder detected the physical parameter failure, never asserted
recording readiness, and initiated shutdown. The bag itself closed cleanly and
contains 3,187 messages, including 336 `/odom`, 336 `/imu`, 101 evaluation-only
Vicon odometry, and 441 encoder messages. It contains zero `/cmd_vel`, zero
filter output, zero final control output, zero source-cost output, and zero
timekeeper messages. `recording_ready_ever` is false, the target exit code is
`-15`, and completeness correctly fails 18 checks. Therefore no GESC command
or robot motion occurred.

The failed shutdown also revealed three lifecycle defects that did not cause
the initial failure but could contaminate a later successful run:

- the Vicon UDP reader attempted to publish after ROS publisher destruction;
- the selected rotation node attempted its final publication after the ROS
  context was invalid; and
- the photoresistor reader could read from pyserial after its descriptor had
  been closed.

## Accepted bounded repair

The repair does not retune, replace, or fork the cumulative v8.12-derived
algorithm.

1. `controller_node` and `filter_node` now accept their own strict
   `--use-sim-time` boolean option. Its default is `True`, preserving every
   historical simulation/legacy invocation.
2. The selected physical launch passes `--use-sim-time False` through those
   native CLI interfaces instead of forwarding ROS arguments.
3. The selected wrapper's nonlaunching `--check-only` path now imports both
   complete parsers and proves selected `False` plus legacy-default `True`
   before reporting success.
4. Filter, selected rotation, photoresistor, and Vicon odometry-client shutdown
   now stop their worker/executor activity and perform final cleanup while the
   ROS context is still valid.
5. The unchanged Windows/Pi Vicon server, IP `192.168.1.6`, UDP port `12346`,
   native seven-float packet, millimetre-to-metre conversion, topic, and
   evaluation-only role are preserved. The Vicon server SHA-256 remains
   `7e92f63ead57e26ffafc82a2013826a41fe4de291a6e9feba2d1e0812545d0e3`.
6. `/odom` remains the sole algorithm pose. Vicon remains outside the
   controller, filter, supervisor, cost, convergence, and fill inputs.

No historical ESC Bash wrapper or launch file was changed. RMSprop, Adagrad,
legacy GESC, HeavyBall, and older Gaussian experiment selection therefore
retain their established paths. The additive controller/filter clock option
defaults to their historical simulation-time behavior when omitted.

## Backup and transfer evidence

Verified pre-repair recovery roots:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260804T202726-0700_m8f_runtime_graph_repair
/home/mattb/tb3-pi/phase09_backups/
  20260804T202726-0700_m8f_runtime_graph_repair
```

Both roots contain matching `MANIFEST.md` and `POST_TRANSFER.md` receipts plus
all pre-repair files. Their manifest SHA-256 is
`a0ef0bf75cc73b4858fe64f9965d9d775dc7fe34c769d12d1469c4ede864ac6a`;
their post-transfer receipt SHA-256 is
`c01b70f709269fef639e69474780fd53b7b7fbc998b6eb3e5f3445c80eff40cb`.

Eleven unique reviewed files were copied from the offline snapshot to the
mounted Pi in two checksum-scoped transfers. There was no delete operation.
Final snapshot/Pi parity is:

```text
regular files: 345/345, all relative SHA-256 entries identical
symlinks:      0/0
parity work:   /tmp/phase09_m8f_parity.t9JtlI
```

The repaired Vicon odometry-client SHA-256 is
`3f8413fc2977107de6e04f6011b44331e49c9ab866d2af15c8eb73020a4f385c`.
Its pre-repair source remains in both recovery roots.

## Qualification evidence

All commands were bounded where runtime could exceed a trivial static check.
No host test opened either Pi character device.

```text
changed-source Python syntax: PASS
selected wrapper Bash syntax: PASS
selected launch XML parse: PASS
critical E9/F63/F7/F82 lint on changed files: PASS
controller/filter complete-parser smoke checks: PASS
canonical focused parser/legacy checks: 10 passed
canonical full test_legacy_behavior.py: 37 passed
focused Vicon plus physical-launch tests: 35 passed
complete six-file Phase 09 physical suite: 238 passed
fresh isolated host build: 3 packages passed in 12.5 s
isolated build/log root: /tmp/phase09_m8f_vicon_build.W6aNEB
selected launch construction with TURTLEBOT3_MODEL=burger: PASS
installed-overlay parser compatibility: PASS
controller/filter construction with --use-sim-time False: PASS
mounted-Pi source syntax/XML/Bash/critical-lint checks: PASS
snapshot/Pi source parity: PASS, 345/345
```

The first focused test invocation omitted the already-built
`ros_esc_interfaces` overlay and stopped during import; rerunning against the
isolated overlay passed 35/35. An earlier launch-construction probe omitted
`TURTLEBOT3_MODEL`; the corrected bounded invocation with `burger` passed.
These are retained host-harness corrections, not product failures.

Package-wide flake8 meta-tests still report thousands of inherited formatting
findings in the historical packages. Critical syntax/name lint on the repair
scope passes; M8F does not reformat unrelated shared-lab source.

## Operator-run on-Pi check-only evidence

The operator ran the required one-time post-repair check from the standalone
Linux-tower SSH terminal. Exact result:

```text
ros_esc_interfaces: PASS in 2.61 s
ros_esc: PASS in 5.19 s
turtlebot3_vehicle_nodes: PASS in 5.31 s
three-package summary: PASS in 14.4 s
installed Python parity: PASS (ros_esc=63, turtlebot3_vehicle_nodes=21)
selected CLI parser compatibility: PASS (physical=False, legacy default=True)
final check-only result: PASS
scenario: primary
turtlebot3 underlay/model: /home/pi/turtlebot3_ws, burger
photoresistor/OpenCR: /dev/ttyUSB0, /dev/ttyACM0
selected lidar: disabled
launch construction: PASS
Pi lab clock: 2026-08-04T20:52:29+00:00
pigpio/serial/Vicon/ROS graph/recorder/motion: NOT STARTED
```

Read-only SSHFS inspection also found `colcon_build.rc=0` for all three
packages. This closes the post-M8F source/build/parser check-only gate. Codex
did not run the command and did not start any Pi process.

## Current boundary and exact next action

The repaired source and installed Pi packages are now statically qualified.
This does not demonstrate live voltage input, `/odom`/IMU, evaluation-only
Vicon evidence, controller output, robot motion, managed shutdown, rosbag
completion, familiar CSV export, or two-source search behavior.

If the Pi has not rebooted and no source changed after the passing check, do
not repeat check-only. Follow the established lab/Vicon setup, keep the floor
clear and `Ctrl+C` immediately available, then run from the same standalone
SSH owner:

```bash
cd ~/ros2_ws/src/turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values
./gesc_gaussian_two_source_voltage.bash
```

Watch the printed run directory and one-second diagnostics. Motion must remain
blocked until readiness becomes true. Stop on any sensor, odometry, Vicon,
command, rotation, or physical-behavior error. After stopping, wait for
readiness false, final-zero dwell, bag finalization, validation, CSV export,
and the final retained run-directory report before closing the terminal.
