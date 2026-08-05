# Phase 09 M8H — Third Physical-Run Clock Repair

Verified: `2026-08-04T22:09:03-07:00`

## Result

The third selected physical attempt remains retained failed commissioning
evidence. M8H repairs the startup-clock defect that caused the failure, passes
the declared host tests and process probe, and is present byte-for-byte in the
canonical checkout, offline physical snapshot, and mounted Pi source. Codex
did not build or launch on the Pi, open either serial device, connect to Vicon,
start recording, or command motion.

This is a source-transfer and host-qualification result, not proof that the
physical algorithm now completes a run. Because Pi source changed, one new
human-operated `gesc_gaussian_two_source_voltage.bash --check-only` is required
before another bare experiment.

## Retained failure evidence

The preserved run is:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/2026-08-04/
  20260804T212226731572Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_309b9e71
```

The sqlite3 bag finalized with 8,833 messages. Evaluation-only Vicon and
onboard `/odom` were live. During recorder physical-parameter enforcement,
`gaussian_fill_node` changed from its constructor-forced
`use_sim_time=True` to the required physical `False`; rclpy destroyed the
`/clock` waitable while the node's multithreaded executor was active and raised
`InvalidHandle: cannot use Destroyable because destruction was requested`.

Safety evidence from the retained bag is unambiguous:

- all 815 recorded `/cmd_vel` messages were zero;
- all 421 rotation-authorization samples were false;
- all 416 recording-readiness samples were false;
- no rotation RPM command or robot motion occurred; and
- missing resolved snapshots and CSV export followed the pre-readiness abort
  and are not relabeled as successful output.

## Root cause and bounded correction

Five shared owners applied `use_sim_time=True` after node construction even
when ROS startup supplied an explicit physical `False`:

- modified cost;
- PDE position history;
- PDE cost history;
- convergence detector; and
- Gaussian fill.

The new `ros_esc.clock_configuration.apply_legacy_sim_time_default` helper
examines Humble's startup override map before an executor spins. It applies the
historical Gazebo `True` only when no startup override exists, preserves an
explicit physical `False`, preserves an explicit simulation `True`, and fails
rather than guessing if rclpy's override map is unavailable. Exactly the five
owners above use the helper.

The change does not alter Gaussian fill's two-thread executor, numerical
algorithm code or v8.12 tuning, topics, cost sign/units, `/odom` ownership,
evaluation-only Vicon, recorder enforcement, the selected wrapper/launch, or
any historical ESC wrapper/launch/configuration.

## Recovery and transfer

Matching pre-edit recovery roots were sealed before source writes:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260804T214018-0700_m8h_clock_initialization_repair
/home/mattb/tb3-pi/phase09_backups/
  20260804T214018-0700_m8h_clock_initialization_repair
```

Their `MANIFEST.md` files match at SHA-256
`c297823f6e2149c335412d99e5362637dccf1cd83595cd42c33459a17c9de643`.
The normalized 345-file pre-edit source-manifest SHA-256 is
`30c4641232eaac0bd290050e85c8d01464089e004b6f2ed12489ccc7a865bc96`.

The reviewed transfer was eight paths: five modified owners, one new shared
helper, one new focused test, and the physical shared-parity test. It used no
broad synchronization and no source deletion. `POST_TRANSFER.md` in each
recovery root records identical final receipts at SHA-256
`6ae98289e19c2a066a8f61005e16e01b3dc9d4b0a97d8201d29caa6933dc453c`.

After transfer, only generated `__pycache__`, `.pytest_cache`, and `*.pyc`
content was removed from the two source roots. Before cleanup the snapshot had
55 cache files under 23 cache directories and the Pi had 49 files under 22
directories; after cleanup both have zero cache directories. These generated
artifacts are not source and regenerate automatically.

## Host qualification

| Gate | Result |
|---|---:|
| canonical Python compile and critical lint | PASS |
| focused five-owner three-way clock suite | 16 passed in 0.82 s |
| clock + shared legacy/PDE/convergence/Gaussian/observability suite | 114 passed in 3.18 s |
| canonical isolated three-package build | PASS, 3 packages in 14.3 s |
| installed canonical Gaussian-fill physical-clock process probe | PASS |
| snapshot focused clock/parity suite | 45 passed in 0.85 s |
| complete snapshot Phase 09 suite | 256 passed in 3.26 s |
| snapshot isolated three-package build | PASS, 3 packages in 14.9 s |
| mounted-Pi source AST parse | 8/8 PASS |
| mounted-Pi critical lint `E9,F63,F7,F82` | 8/8 PASS |

The installed canonical process probe constructed Gaussian fill with explicit
`use_sim_time=False`, spun its unchanged two-thread executor, applied physical
parameter enforcement three times, and remained alive with no `InvalidHandle`
or traceback. The first harness attempt was invalid because shell nounset was
enabled before sourcing ROS; the corrected bounded harness passed and the
invalid harness attempt is not counted as product evidence.

## Final source seal

After the battery swap, Pi reboot, and SSHFS remount, fresh manifests—not the
pre-reboot results—proved:

```text
snapshot/Pi regular files:       347/347 PASS
source-manifest SHA-256:         87bfed392f98ad6cecca05c296fc2600c355821f2907e55e521ec00d6989fd6a
snapshot/Pi inventory entries:   435/435 PASS
inventory SHA-256:               55b2b88117506164cf339696c74f1fe4a571bf1b8ad7cefc62b29cdb36b1ebbb
snapshot/Pi source cache dirs:   0/0
canonical/snapshot/Pi shared:    7/7 byte-identical
snapshot/Pi physical parity test: 1/1 byte-identical
```

## Operator check-only closeout

The operator restored Nick's literal lab wall-clock convention and ran the
required one-time command from the standalone SSH terminal:

```bash
cd ~/ros2_ws/src/turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values
./gesc_gaussian_two_source_voltage.bash --check-only
```

The result passed:

```text
ros_esc_interfaces: 3.03 s
ros_esc: 5.91 s
turtlebot3_vehicle_nodes: 5.30 s
three packages: PASS in 16.4 s
installed Python parity: PASS (ros_esc=64, turtlebot3_vehicle_nodes=21)
selected CLI parser: PASS (physical=False, legacy default=True)
scenario/launch: primary, PASS
devices: /dev/ttyUSB0 photoresistor, /dev/ttyACM0 OpenCR
selected lidar: disabled
current time: 2026-08-04T22:06:12+00:00
pigpio/serial/Vicon/ROS graph/recorder/motion: NOT STARTED
```

Read-only SSHFS inspection then confirmed all three `colcon_build.rc` files are
zero. The installed `ros-esc.egg-link` targets `/home/pi/ros2_ws/build/ros_esc`,
whose package link targets `/home/pi/ros2_ws/src/ros_esc/ros_esc`; the active
source helper hash remains
`54942fc70164bbe7d36d5a82daea3f1d41e21ccd0dd90a1a9bb167a24a418ae9`.
Fresh post-build source comparison still passes 347/347 hashes and 435/435
inventory entries with the sealed manifest digests above.

The build regenerated 16 bytecode files (80,108 bytes) beneath 11 normal
`__pycache__` directories in the Pi source tree. They are excluded generated
artifacts, not source drift, and do not require another build or check-only.
The one-time M8H installed gate is closed.

The next human action may follow the ordinary Vicon/lab SOP and invoke the bare
selected wrapper. Live source cost, Timekeeper, filter/control, authorization,
motion, managed final zero, bag/CSV completeness, and physical two-light
behavior remain unverified until that retained run is finalized and reviewed.
