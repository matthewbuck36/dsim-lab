# Physical GESC + Gaussian Two-Source Operator Checklist

<!-- MBuck 2026-08-04: Align the selected physical run with the established lab Vicon SOP, repaired Pi runtime, and a single Bash entry point. -->

## Phase 10 V1 closeout notice — 2026-08-12

This checklist is retained as the final selected-run operator procedure and
historical provenance; Phase 10 does **not** authorize another hardware run,
Pi access, transfer, calibration, or motion. The final Phase 09 M8L
source/snapshot/transfer evidence and eighth-run validation supersede the older
M8C-M8E "current" snapshots in the narrative below.

The eighth retained physical run was the first selected two-basin behavioral
success: local convergence/classification, one fill, repulsive plus assisted
escape, return to `SEARCH`, and stronger-light reacquisition. It ended before
a second convergence or `GOAL_HOLD` and passed `61/62` completeness checks;
the sole failure was retained as cross-topic shutdown-ordering evidence. This
is neither complete second-extremum acceptance nor broad physical readiness.
See the
[eighth-run validation](../codex/gesc_gaussian/validation/phase_09_eighth_physical_run_validation.md)
and
the LaTeX-typeset
[`FINAL_PROJECT_REPORT_V1.pdf`](../codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.pdf)
with its `.tex`/`.md` sources.

For any future separately planned and explicitly authorized selected run,
manual operator `Ctrl+C` remains the normal stop. `GOAL_HOLD` does not
terminate the physical process. No V2 branch or V2 behavior is created by this
checklist or by Phase 10.

This is the current Phase 09 M8C operator procedure with the M8D familiar-CSV
recording amendment and M8E real-Pi runtime repair. It supersedes the earlier
M8B commissioning sequence that required separate site files, stationary
preflight/approval, `--check-only`, typed authorization, Vicon identity fields,
and file hashes. Those M8B requirements remain in historical status and
handoff records only; the selected wrapper does not consult them. The one
successful M8E `--check-only` was a diagnostic/qualification run, not a new
per-experiment operator gate.

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

M8D added familiar post-bag CSV output and ended at `343/343` source hashes and
`431/431` inventory entries. M8E then repaired the real-Pi underlay and stale
install path, restored the historical sound-profile source owner, and added a
selected-only no-lidar OpenCR/odometry helper. The human operator completed a
clean on-Pi `--check-only`: all three packages built in `1 min 39 s`, installed
Python parity passed (`63 + 21` files), device separation and launch
construction passed, and no pigpio, serial, Vicon, ROS graph, recorder, or
motion started. Following the earlier power cycle, snapshot/Pi parity is
`345/345` files and `433/433` inventory entries with all three build return
codes zero; the final strengthened check-only was captured after the Pi was
back online.

M8E rollback evidence is retained at:

```text
/home/mattb/tb3-pi/phase09_backups/
  20260804T224607Z_m8e_runtime_repair
```

The full result is
`docs/codex/gesc_gaussian/validation/phase_09_pi_runtime_repair.md`. The Pi has
no RTC and DSIMOVERWATCH has no internet NTP access. Nick's established
literal wall-clock `sudo date -s` procedure successfully initialized the
current powered session to `2026-08-04T17:54:22+00:00`; no timezone or NTP
setting changed. The earlier Unix-epoch copy to August 5 was superseded before
any experiment or run directory started.

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
- [ ] After every Pi reboot, verify the lab Linux computer's clock, then use
  Nick's literal wall-clock `sudo date -s` procedure before starting ROS. If
  the Pi has remained powered since the successful
  `2026-08-04T17:54:22+00:00` initialization, this is already complete for the
  current session.

From an accurately timed lab Linux terminal outside the Pi SSH session, the
offline-safe form is:

```bash
date '+%Y-%m-%d %H:%M:%S %Z %z'

ssh -t pi@192.168.1.36 \
  "sudo date -s '$(date '+%Y-%m-%d %H:%M:%S')' && date --iso-8601=seconds"
```

This uses only the DSIMOVERWATCH LAN and transfers the Linux tower's displayed
wall-clock fields. Do not replace the formatted string with Unix epoch or add
`PDT`/an offset. A final `+00:00` is expected because the Pi remains configured
as UTC, but its calendar and hour must match the Linux tower's Pacific wall
clock. `System clock synchronized: no` is expected without NTP. Never change
the Pi clock after ROS or rosbag has started.

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

- sourcing `/opt/ros/humble`, the established `~/turtlebot3_ws` underlay, and
  then building exactly `ros_esc_interfaces`, `ros_esc`, and
  `turtlebot3_vehicle_nodes` with `--symlink-install`;
- constructing both selected launches, verifying installed-source parity, and
  checking distinct photoresistor/OpenCR devices before hardware access;
- bringing up OpenCR motors plus wheel/IMU `/odom` without the unused lidar,
  leaving `/dev/ttyUSB0` exclusively available to the photoresistor;
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

The exact selected-wrapper runtime directory is:

```text
${HOME}/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/
  <UTC-date>/<run-id>/
```

The terminal summaries remain live during recording. The CSV files are created
only after a clean shutdown has finalized the authoritative sqlite3 rosbag and
the existing `record_run` finalizer begins final validation. The export is
atomic and idempotent, and missing or malformed required output makes final
validation fail. Do not stop the terminal while this finalization is running.

After successful finalization, the same run directory should contain these
headerless, familiar-format files:

- `encoder.csv`: `[timestamp, angle]`;
- `cost_value.csv`: `[timestamp, augmented cost]` from `/cost_modified`;
- `filter_value.csv`: `[timestamp, two filter values]`;
- `control_value.csv`: `[timestamp, six command-array values]`; and
- `odometry.csv`: `[timestamp, x, y, z, qw, qx, qy, qz]` using the legacy
  Vicon/evaluation plotting meaning.

The additional selected-algorithm files are `raw_cost_value.csv`, containing
`[timestamp, raw_cost]` with `raw_cost=-voltage`, and
`algorithm_odometry.csv`, containing
`[timestamp, x, y, z, qw, qx, qy, qz]` from algorithm `/odom`.
`legacy_csv_manifest.json` records the source aliases/topics, semantics, row
counts, byte sizes, SHA-256 hashes, and bounded export errors.

The old `extract_test_data` column reader can consume these files directly, but
its top-level `Test_*` browser does not auto-discover this nested directory and
the exporter does not fabricate `comments.txt`. The one rosbag remains the sole
recorder and source of truth; there is no second recorder or live CSV collector.
This M8D exception supersedes the earlier no-CSV-equivalence statement only for
the selected wrapper's post-bag output. Legacy wrappers, nodes, launches, and
their runtime behavior remain unchanged.

Vicon absence is an evaluation-quality warning, not a robot-motion fault. A
photoresistor, `/odom`, required IMU, controller, recorder, or command-path fault
may still trigger the algorithm's automatic zero-command behavior.

## Stop and save

1. Press `Ctrl+C` once in the Pi experiment terminal.
2. Wait for the wrapper to report readiness false, the managed stop/final-zero
   sequence, recorded zero dwell, rosbag finalization, bounded validation, and
   the final retained run directory. Confirm that validation reports the M8D
   CSV export complete before closing the terminal.
3. Only after Pi cleanup completes, stop `vicon-tracker-server.py` on Windows.
4. Keep the run directory whether the behavior succeeded, was interrupted, or
   exposed a hardware/algorithm issue.

Arbitrary intensity/layout matrices, three-light cases, boundaries, walls,
obstacles, and broad robustness remain future work unless separately planned.
