# Phase 09 M8E Pi Runtime Repair and Check-Only Validation

Date: `2026-08-04` (`America/Los_Angeles`)

Outcome: **PASS — CLEAN ON-PI BUILD, INSTALLED-SOURCE PARITY, DEVICE
SEPARATION, AND LAUNCH CONSTRUCTION; NO ROS GRAPH OR MOTION STARTED**

## Purpose and evidence boundary

M8E repairs the first real-Pi wrapper startup failure without changing the
cumulative v8.12 algorithm, cost sign/units, control/evaluation boundary,
recorder ownership, or any historical ESC entry point. The ordinary operator
path remains the single bare wrapper:

```bash
cd ~/ros2_ws/src/turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values
./gesc_gaussian_two_source_voltage.bash
```

The successful evidence in this record is an operator-run `--check-only`. It
built and sourced software, inspected device paths and permissions, and
constructed launch descriptions. It did not start pigpio, open a serial port,
connect Vicon, create a ROS graph, start the recorder, command a servo or motor,
or move the robot. It is not a physical-algorithm success claim.

## Retained failed first attempt

The first bare wrapper attempt is retained at:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/
  2026-08-04/
  20260804T152851316144Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_df84804a
```

That attempt is failed commissioning evidence, not an experiment result. The
recorder started, but `turtlebot3_bringup` was unresolved and the installed
photoresistor console entry did not recognize the new serial arguments.
Readiness remained false; no odometry/command path became ready and no motion
occurred. Managed shutdown retained the run safely.

## Diagnosed causes

1. The wrapper sourced `/opt/ros/humble` and the selected workspace but omitted
   the lab Pi's established TurtleBot3 source underlay at
   `/home/pi/turtlebot3_ws/install/setup.bash`. The Pi already contained
   `turtlebot3_bringup`, `turtlebot3_node`, `turtlebot3_description`, and the
   LDS driver there; the absent APT package was not the required repair.
2. The selected incremental install was stale. For example, the current
   photoresistor source SHA-256 was
   `8300ab9d88de37cbc65a47e0026262c34263f4407962c8c89b4490a3eaab7ff1`,
   while the installed copy was
   `00973be58221696ea8b58d33d28d1a42cd124e1899a995e9a207a6e0092d6f40`.
   The source declared `--serial-port`; the installed copy did not. The stale
   servo install also contained the former `228` zero offset instead of the
   reviewed source value `54`.
3. `setup.py` and `sound_profile.launch.xml` retained the historical
   `sound_profile_experiment_node`, but its source module was absent. A truly
   clean rebuild would therefore have broken that legacy entry point. The
   exact prior generated module was restored to source with SHA-256
   `4b9b3f2b7e448a9c741ff0324ca4da1550ac024927ab304259fc98cc2f9dac32`.
4. The lab LDS-02 launch and historical photoresistor default both claimed
   `/dev/ttyUSB0`, although the selected open-field algorithm has no `/scan`
   consumer. M8E added a selected-only no-lidar base bringup that retains
   OpenCR motor and wheel/IMU odometry ownership. Every historical launch still
   uses the unchanged complete `vehicle_bringup.launch.py`.
5. A relative wrapper invocation could resolve its evidence path after the
   wrapper changed directory. M8E now resolves `BASH_SOURCE[0]` before `cd`.

## Package-manager incident

An interrupted pre-existing `linux-firmware` configuration initially prevented
APT from doing any work. The operator ran `sudo dpkg --configure -a`; it
completed the Raspberry Pi firmware/boot triggers. Final checks were:

```text
dpkg --configure -a exit: 0
dpkg --audit: no output
apt-get check: PASS
ros-humble-turtlebot3-bringup APT package: not installed
running kernel: 5.15.0-1079-raspi
reboot required: no
```

This operating-system recovery did not install the TurtleBot3 APT package and
did not change the selected algorithm. The wrapper deliberately uses the
existing lab source underlay.

## Recovery and source scope

Pre-repair recovery roots:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260804T224607Z_m8e_runtime_repair
/home/mattb/tb3-pi/phase09_backups/
  20260804T224607Z_m8e_runtime_repair
```

The Pi recovery root contains `17,958,560` bytes of the moved stale selected
`build`/`install` package directories under `generated_before`. They were
moved, not deleted, before the clean build.

M8E replaced six existing selected/documentation/test paths:

```text
turtlebot3_vehicle_nodes/README.md
turtlebot3_vehicle_nodes/package.xml
turtlebot3_vehicle_nodes/launch/gesc_gaussian_two_source.launch.xml
turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values/gesc_gaussian_two_source_voltage.bash
turtlebot3_vehicle_nodes/test/test_phase09_physical_launch.py
turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/photoresistor_node/README.md
```

It added exactly two source paths:

```text
turtlebot3_vehicle_nodes/launch/gesc_gaussian_two_source_vehicle_bringup.launch.py
turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/sound_profile_experiment_node_script.py
```

No `ros_esc` algorithm source changed in M8E. Transfer was checksum-scoped and
used no delete behavior.

## Runtime repairs

The selected wrapper now:

- sources `/opt/ros/humble`, then the established `~/turtlebot3_ws` underlay,
  before the selected workspace build;
- exports the established default `TURTLEBOT3_MODEL=burger` while permitting
  an explicit environment override;
- uses `colcon build --symlink-install --packages-select` for exactly
  `ros_esc_interfaces`, `ros_esc`, and `turtlebot3_vehicle_nodes`;
- verifies the TurtleBot3 base/state packages and selected files before launch;
- constructs the selected no-lidar base launch and complete experiment launch
  with bounded `--show-args` commands;
- checks byte-for-byte installed Python/source parity for `ros_esc` and
  `turtlebot3_vehicle_nodes`, including copied installs or expected egg-links;
- requires distinct readable/writable photoresistor and OpenCR character
  devices before the normal run; and
- keeps `--check-only` nonlaunching and non-device-opening.

The selected helper starts only `turtlebot3_node` on OpenCR and the standard
TurtleBot3 state publisher. It does not start LDS-02. This is selected-only
physical adaptation: the algorithm, `/odom` input, controller, and historical
launches are unchanged.

## Host qualification

The final host-side evidence was:

```text
bash syntax + Python compile + XML parsing: PASS
focused selected launch/wrapper/compatibility tests: 22 passed
isolated --symlink-install build: 3 packages finished in 15.1 s
selected no-lidar bringup --show-args: PASS (14 lines)
complete selected launch --show-args: PASS (666 lines)
installed-overlay Phase 09/device tests: 233 passed in 2.77 s
vehicle functional tests excluding inherited style meta-tests: 74 passed
new helper focused flake8: PASS
```

Two early combined pytest invocations stopped during collection because they
did not source the generated interface/installed overlay. Repeating the tests
under the isolated overlay produced the passing `233`-test result. A host
import of the GPIO communication module also lacked host `pigpio`; static
syntax/constant validation passed instead. These were host-environment limits,
not source acceptance failures.

## Successful on-Pi check-only

The operator first confirmed the current physical device mapping:

```text
/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0 -> ../../ttyUSB0
/dev/serial/by-id/usb-ROBOTIS_OpenCR_Virtual_ComPort_in_FS_Mode_FFFFFFFEFFFF-if00 -> ../../ttyACM0
/dev/ttyUSB0: character device, root:dialout, readable/writable by dialout
/dev/ttyACM0: character device, OpenCR, readable/writable
```

The operator then ran:

```bash
./gesc_gaussian_two_source_voltage.bash --check-only
```

The first clean build printed missing-prefix warnings for the three selected
install directories intentionally moved to the recovery backup. They were
expected one-time environment warnings; the build recreated those prefixes.
Final output was:

```text
ros_esc_interfaces: PASS in 1 min 20 s
ros_esc: PASS in 11.8 s
turtlebot3_vehicle_nodes: PASS in 5.32 s
3 packages: PASS in 1 min 39 s
installed Python parity: PASS (ros_esc=63, turtlebot3_vehicle_nodes=21)
scenario: primary
turtlebot3_bringup: /home/pi/turtlebot3_ws/install/turtlebot3_bringup/share/turtlebot3_bringup
turtlebot3 setup: /home/pi/turtlebot3_ws/install/setup.bash
turtlebot3 model: burger
photoresistor: /dev/ttyUSB0
OpenCR: /dev/ttyACM0
selected lidar: disabled
launch construction: PASS
Pi time: 2026-08-04T16:27:57+00:00
pigpio/serial/Vicon/ROS graph/recorder/motion: NOT STARTED
```

Earlier in the same commissioning sequence, low battery required the operator
to power down and connect wall power. The stale SSHFS connection was lazily
detached at exactly `/home/mattb/tb3-pi`, the Pi was booted again, and the
mount was re-established after SSH became available. Post-power-cycle
read-only verification found:

```text
snapshot/Pi source hashes: 345/345 PASS
snapshot/Pi inventory: 433/433 PASS
ros_esc_interfaces colcon_build.rc: 0
ros_esc colcon_build.rc: 0
turtlebot3_vehicle_nodes colcon_build.rc: 0
workspace install/setup.bash: present
selected helper/wrapper install links: current clean build
rollback backup: present
```

The final strengthened `--check-only` output reported above was captured after
the Pi was back online and the mount had been re-established.

## Final source seal

Final retained seal:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260804T234034Z_m8e_post_runtime_repair
```

Evidence:

```text
regular-file manifest entries: 345
type/mode/size inventory entries: 433
source caches: 0
source symlinks: 0
source manifest SHA-256:
  5469c772d0649d42cee3581d207d19a29a16d6df1f13d30620e1a10ce301c66d
inventory SHA-256:
  3775454cb80812501495c4315b6ce696302960d580ba7750d550be3a9bfb6fd2
verified same-permissions source archive SHA-256:
  2a2b81cef6e1156890191e0667795c9ddfbca111cffa5e9d88fc2a9e3bdb659a
```

The archive was extracted with `--same-permissions`; file hashes and the full
type/mode/size inventory matched the live seal exactly. Small post-repair
manifests and the transfer/rollback receipt are also retained under the Pi
M8E recovery root.

## Offline manual clock initialization

The check-only timestamp was `2026-08-04T16:27:57+00:00`, while the operator
and host were at approximately `16:27` Pacific (`23:27 UTC`). Earlier, local
wall-clock numbers had been assigned manually while the Pi remained configured
for UTC, leaving that check-only timestamp about seven hours behind.

The next reboot exposed the complete lab clock contract:

```text
Pi date after reboot: 2025-06-04T14:59:08+00:00
time zone: Etc/UTC
RTC: n/a
system clock synchronized: no
NTP service: active
```

The Pi has no RTC and DSIMOVERWATCH is an isolated lab router without internet
NTP access. The mounted package README therefore intentionally requires
Nick's `sudo date -s` step before experiments. The earlier one-time NTP/timezone
correction assumption is superseded; no timezone or NTP configuration was
changed.

After verifying the lab Linux computer's clock, the operator ran from that
computer, outside the existing Pi SSH shell:

```bash
ssh -t pi@192.168.1.36 \
  "sudo date -s '@$(date +%s)' && date --iso-8601=seconds"
```

The local shell supplied its Unix epoch over the isolated LAN, and the Pi
reported:

```text
Wed Aug  5 12:02:42 AM UTC 2026
2026-08-05T00:02:42+00:00
```

This is the correct UTC representation of approximately `17:02` Pacific on
2026-08-04 and is a PASS for the current powered session. It requires no
internet connection. Repeat the established manual time initialization after
every Pi reboot and before starting ROS or rosbag; never change the clock
during a run. `System clock synchronized: no` is expected under this offline
manual procedure and is not a Phase 09 authorization gate.

## Remaining physical boundary

M8E establishes the selected software/check-only boundary. The following have
not yet been demonstrated by the repaired wrapper:

- a live photoresistor protocol sample and changing `raw_cost=-voltage`;
- live OpenCR `/odom`, IMU, command, and watchdog behavior;
- live Vicon evaluation data and retained evaluation completeness;
- recorder readiness, motion onset, rotating sensor behavior, or actual robot
  translation/rotation;
- operator `Ctrl+C`, readiness-false/final-zero dwell, bag finalization, final
  validation, and familiar CSV export on a real selected run; or
- the algorithm's physical two-light search behavior.

The clock is valid for the current powered session. The next normal action is
the attached lab SOP followed by the bare wrapper, with the floor clear, the
robot supervised, and `Ctrl+C` immediately available. If the Pi reboots first,
repeat Nick's manual date step. No additional repository authorization file or
repeated `--check-only` is part of that normal operator path.
