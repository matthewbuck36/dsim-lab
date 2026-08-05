# Phase 09 second physical-run diagnosis and M8G repair

Date: 2026-08-04
Milestone: M8G
Decision: **SECOND FAILED RUN RETAINED / SELECTED STARTUP-GRACE REPAIR
HOST-QUALIFIED AND TRANSFERRED / ON-PI REBUILD AND CHECK-ONLY PASS / PHYSICAL
ALGORITHM BEHAVIOR NOT YET DEMONSTRATED**

## Retained failed run

The second selected bare-wrapper attempt remains unchanged at:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/2026-08-04/
  20260804T205606472031Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_d4f0178d
```

Mounted inspection used the corresponding path below
`/home/mattb/tb3-pi`. This is failed commissioning evidence, not a physical
GESC + Gaussian result. Its failed completeness result and empty derived CSVs
are correct and must not be rewritten or deleted.

## Observed behavior

The M8F repairs worked: all three selected packages built in 14.5 seconds,
installed/source and CLI parser checks passed, OpenCR opened `/dev/ttyACM0`,
wheel/IMU `/odom` became live, the unchanged Vicon path became live, the bag
recorded, and every target process plus the bag shut down cleanly.

The run still never reached recording readiness and never authorized sensor
rotation. Its ordering was:

```text
20:56:10  selected target processes started
20:56:16  onboard /odom became live
20:56:17  supervisor reported SEARCH
20:56:22  supervisor reported FAILSAFE
20:56:25  evaluation-only Vicon became live
20:56:27  rosbag finished subscribing to all requested topics
20:56:52  recorder rejected pre-readiness SEARCH -> FAILSAFE
```

The finalized 10,234-message bag contains 765 `/odom`, 765 IMU, 1,255 encoder,
301 evaluation-only Vicon, 520 rotation-status, 698 algorithm-state, and 1,202
`/cmd_vel` messages. Readiness was false for the whole run and the recorder's
pre-ready nonzero map is empty, so every command was zero. It contains zero
Timekeeper and zero source-cost messages. The target and bag both exited zero
and cleanly; cleanup errors are empty. No algorithm motion occurred.

## Root cause

This failure was not a recurrence of the M8F parser problem and is not evidence
that `/dev/ttyUSB0` or the Arduino failed. It is a selected startup-timing
contract mismatch:

1. `record_run` allows up to 45 seconds for passive graph/parameter preflight.
2. After that passive barrier, it authorizes only the rotating sensor and
   allows another 45 seconds for alignment, the configured 10-second settle,
   Timekeeper, and the full sensor data plane.
3. The selected launch still gave the controller and supervisor their shared
   historical 5-second startup grace.
4. The rotation node owns the real-Timekeeper start and publishes it only after
   recorder authorization, alignment, and settle.
5. The photoresistor owner opens and reads the serial device but intentionally
   publishes no timestamped voltage/cost before that Timekeeper start.
6. The 5-second grace therefore expired before the passive recorder stage
   could authorize rotation. The supervisor changed from `SEARCH` to
   `FAILSAFE`, and the recorder correctly rejected that pre-readiness lifecycle
   transition.

The photoresistor's uncalibrated-operation warning proves that the node was
constructed; it does not prove whether a valid Arduino payload was received
because pre-Timekeeper samples are deliberately not published. Live serial
response therefore remains for the next retained run to demonstrate.

## Accepted bounded repair

Only the new selected wrapper and its focused compatibility test changed.
No controller, supervisor, state-machine, cost, filter, recorder, rotation,
photoresistor, Vicon, message, launch, or legacy-wrapper source changed.

The wrapper now makes all three bounded timings explicit:

```text
passive recorder preflight:  45.0 s
rotation startup:            45.0 s
selected algorithm grace:   100.0 s
```

It passes the 100-second value through the existing selected launch argument,
which already feeds both controller and supervisor. The extra 10 seconds is a
bounded margin over the two 45-second recorder stages. The selected graph still
requires `recording_ready=True`; the controller continues publishing only zero
before readiness. Recorder graph, parameter, lifecycle, nonzero-command,
rotation, heartbeat, final-zero, and completeness gates are unchanged.

The selected launch and shared node defaults remain 5.0 seconds. All 26
historical Bash wrappers, all historical launches, and the legacy controller
and supervisor defaults remain unchanged. RMSprop, Adagrad, legacy GESC,
HeavyBall, and older Gaussian experiments retain their original entry points.

## Backup, transfer, and parity

Matching pre-repair recovery roots and post-transfer receipts are:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260804T210435-0700_m8g_startup_grace_repair
/home/mattb/tb3-pi/phase09_backups/
  20260804T210435-0700_m8g_startup_grace_repair
```

The pre-repair trees matched 345/345 regular files. Two reviewed source files
were edited through SSHFS with no broad synchronization or source deletion:

```text
45b499446ac1bacf04442cde1adfbe74669d7e99daf67ae9c6accc0887b462aa  turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values/gesc_gaussian_two_source_voltage.bash
ab764c519a8df4f806a56eba0e3e5e47bd46519a4d5b31b1056c2072351591d3  turtlebot3_vehicle_nodes/test/test_phase09_physical_launch.py
```

Generated `*.pyc` and now-empty `__pycache__` directories left by the earlier
Pi build/run were removed from the source tree; no source or experiment data
was removed. Final parity is:

```text
regular-file SHA-256 parity: 345/345 PASS
type/mode/size inventory:   433/433 PASS
source symlinks:            0/0
source caches:              0/0
source manifest SHA-256:    5f34b1ad38fbfa7b489435655c27a96fb057163319e3abecf7599fa456321843
inventory SHA-256:          f96e540bdc693f994598ede3ade96f02d03b93d75c349321ce87600767a8e2c7
backup manifest SHA-256:    969339a8b65997dd47e6ab99cfa51d36067872afb8037f4a276806727e00bb33
transfer receipt SHA-256:   481a6ff698f875b9ba1360bd76b29bf55d17d880316835fb10ff9ca87f13d07e
```

## Qualification

No command in this qualification opened a Pi character device, started a Pi
ROS process, or commanded hardware.

```text
selected wrapper/launch focused suite: 23 passed
complete six-file Phase 09 suite:       239 passed
canonical legacy-behavior suite:        37 passed
all historical-wrapper hash checks:     PASS
all Bash syntax:                        27/27 PASS
all XML parsing:                        9/9 PASS
critical E9/F63/F7/F82 lint:            PASS
isolated three-package host build:      PASS in 15.2 s
isolated build/log root:                /tmp/phase09_m8g_build.SIYVPN
installed selected wrapper/source hash: PASS
mounted-Pi focused suite:               23 passed
snapshot/Pi source parity:              345/345 PASS
```

One legacy-test command first named a test path that does not exist in the
source-only Pi snapshot. A second attempt deliberately mixed the canonical
test with the physical snapshot overlay and exposed the expected package
surface mismatch. Running the canonical legacy test with the canonical source
prepended passed 37/37. The initial executable lookup also missed module-only
flake8; `python3 -m flake8` then passed the critical check. These were bounded
host-harness corrections, not product failures.

## Operator-run post-M8G check-only evidence

The operator ran the required one-time rebuild/check from the standalone
Linux-tower SSH terminal. Exact result:

```text
ros_esc_interfaces: PASS in 2.79 s
ros_esc: PASS in 5.27 s
turtlebot3_vehicle_nodes: PASS in 6.89 s
three-package summary: PASS in 16.3 s
installed Python parity: PASS (ros_esc=63, turtlebot3_vehicle_nodes=21)
selected CLI parser: PASS (physical=False, legacy default=True)
scenario: primary
turtlebot3 underlay: /home/pi/turtlebot3_ws/install/setup.bash
turtlebot3 model: burger
photoresistor/OpenCR: /dev/ttyUSB0, /dev/ttyACM0
selected lidar: disabled
launch construction: PASS
Pi lab clock: 2026-08-04T21:16:22+00:00
pigpio/serial/Vicon/ROS graph/recorder/motion: NOT STARTED
```

Read-only SSHFS inspection confirmed all three live `colcon_build.rc` files are
zero. The installed wrapper symlink resolves on the Pi through the selected
build tree to the repaired source wrapper containing the explicit `45/45/100`
timings. After removing only generated post-build bytecode caches, full
snapshot/Pi parity remains 345/345 regular-file hashes and 433/433 inventory
entries with the same M8G manifest and inventory digests. No source or run data
was removed.

## Current boundary and next action

The one-time M8G source/build/check gate is closed. If the Pi has not rebooted
and source has not changed, do not run check-only again. Follow the ordinary
Vicon/lab SOP, keep the floor clear and `Ctrl+C` immediately available, then
run the bare selected wrapper from the same standalone SSH terminal:

```bash
cd ~/ros2_ws/src/turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values
./gesc_gaussian_two_source_voltage.bash
```

This is permission to proceed with the human-operated experiment, not a claim
that physical behavior is already validated. The next retained run must still
demonstrate Timekeeper, voltage/raw cost, filter/control, readiness, authorized
command and motion, operator Ctrl+C, final zero, finalized bag, familiar CSVs,
and two-light behavior.
