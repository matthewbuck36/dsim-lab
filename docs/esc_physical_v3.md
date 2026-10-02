# Physical V3 commissioning

V3 uses the original Pi workspace `/home/pi/ros2_ws`. Physical acquisition,
rotation and bringup remain in `turtlebot3_vehicle_nodes` on the Pi and in the
offline physical mirror, outside this simulation checkout. Deployment status and
exact validation receipts are in [physical deployment status](codex/gesc_gaussian/v3/physical_deployment_status.md).
Deployment and operator-observed raised-wheel checks completed on 2026-09-29:
normal Ctrl+C, controller crash/freeze, acquisition freeze and guard crash/freeze
all stopped wheels and arm. Subsequent floor trials remained in SEARCH and
were stopped by the operator for clearance. The reproduced numerical-worker
initialization fault was corrected on 2026-09-30 and verified on the Pi without
devices. A subsequent steering correction was followed by a 382-second
SEARCH-only floor run, with no candidate or fill. Read the current
[physical handoff](codex/gesc_gaussian/v3/physical_fresh_chat_handoff.md) for that
analysis and the physical-first continuation. Physical Gaussian escape and
measured stopping latency remain unproven.

## Operator command

On the Pi, the explicit commissioning command is:

```bash
bash ~/ros2_ws/src/turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values/gesc_gaussian_v3_voltage.bash
```

The short script sources ROS/robot underlays, completes an ordinary copied
`colcon build`, sources its installation and starts V3. A build failure prevents
launch. The build has an automated bound; the physical operator run has no
elapsed duration limit. Stop with **Ctrl+C** and allow cleanup/bag closure to
finish. Global-source arrival is judged by the operator; a 20–30 cm orbit is
acceptable. There is no automatic goal hold.

Append `--check-only` to build and inspect installed command/configuration
selection without opening devices, starting pigpiod or launching ROS nodes.
Append `--assist` to enable the optional last-resort assistance for that run.
Append `--no-record` to disable the ordinary rosbag.
Append `--no-vicon` to disable the optional Vicon client for a run. `--output DIRECTORY`,
`--serial-device DEVICE` and `--opencr-device DEVICE` are the remaining practical
overrides. `--help` describes the options. The serial defaults use the retained
CH340 and OpenCR by-id paths; OpenCR remains the algorithm pose provider.

## Selected settings and recovery

- Gains 0.5/5; physical caps **0.05 m/s and 0.30 rad/s**; affine magnitude 2.0.
  These lower caps were authorized after the first floor-run review; the
  initial deployment and Gazebo use 0.10/0.50. The startup message displays
  the resolved physical caps.
- Original fixed5Hz UNO application,9600baud; nominal arm20RPM and54-degree
  calibration once. The short raised-wheel run measured 4.972 Hz and about
  17.95 RPM; these are selected-run observations, not long-run qualification.
- Assistance off by default. When enabled, less than5cm outward progress over
  15seconds allows one nominal20cm measured-path pulse per escape, then GESC.
  Actual cutoff has odometry/control sampling resolution. A data interruption
  consumes an active pulse rather than repeatedly restarting it.
- Moving SEARCH/VERIFY/DESIGN/ESCAPE; no stop-to-sample state or approach,
  verification, escape or overall behavioral deadline. Bad samples are rejected
  without refreshing good input. Essential input expiry produces recoverable
  zero; same-frame reconnects preserve a committed escape and original affine
  decay while discarding stale numerical/direction/progress evidence.
- Physical system time, OpenCR `/odom`, no simulator source positions or Vicon
  control input. Unknown ADC timing remains unknown; observations explicitly use
  complete-line host receipt time. No device sequence is invented.
- No research supervisor, recorder readiness or SSH/session-loss heartbeat.
  The small local process owner watches completed controller/acquisition loops,
  not research progress or input quality. The servo expiry executes in pigpiod.
  Selected raised-wheel process-stop checks passed with operator observation;
  OS/daemon/hardware failures remain untested.

The numerical worker loads its dependencies before announcing readiness.
Control can use fresh instantaneous steering during that initialization; it
does not wait for the worker. The existing 0.5-second coherence and 5-second
fill computation budgets and original data-age checks remain unchanged.

The steering follow-up preserves a still-fresh accepted direction while its
replacement is being computed, preventing a switch to instantaneous steering
on every incoming sample. Original freshness limits, current-yaw reprojection
and context resets still apply. Initial acquisition now seeds the washout
filter from the first valid brightness reading; a usable change can start
control at the next sample, without a startup timer or full-rotation wait.
It does not prime again during moving objective transitions. The subsequent
one-light floor run supports continued averaged steering, but still produced a
broad orbit and no candidate. Controlled comparisons remain necessary to judge
the trajectory effect; changing light brightness confounded the existing runs.

## Recording and configuration

By default the optional standard bag is under
`~/turtlebot_rotating_sensor_tests/gesc_gaussian_v3/<timestamp-and-pid>/bag`, with
`configuration.json` alongside it. Directory timestamps follow the Pi's
user-managed system clock; the user adjusted it on 2026-09-30. Retain the
recorded clock/offset when comparing runs with laptop timestamps.
Recording failure warns and does not stop control. There is no physical live
plot or duplicate CSV writer.

Vicon tracking starts by default using the original physical `odometry_node`
client at `192.168.1.6:12346`. Its independent measurements are recorded on
`/gesc_gaussian/evaluation/vicon_odom`; the algorithm still uses OpenCR `/odom`.
No Vicon connection, measurement, or process-exit condition gates control.
`--no-record` leaves tracking enabled; `--no-vicon` disables the client only.

Start the lab's Vicon UDP server before starting V3. The retained client sends
one initial greeting, and the retained server streams to one client address.
Restart the server script between runs so it waits for the new client. If you
forget to start it, V3 still performs the algorithm, but that run lacks Vicon
tracking. Starting the server late does not automatically repeat the original
client's greeting; a new run reconnects. This preserves the legacy client and
server rather than changing their protocol. The client converts wire millimetres
to ROS metres and publishes host-receipt wall timestamps; it has no device-time
or timekeeper requirement in this V3 path.

The physical selected controller source is
`~/ros2_ws/src/ros_esc/config/profiles/assets/gesc_v3/controller.json`.
The script rebuilds before each run. Use this source configuration for deliberate
changes; do not edit generated installation copies or switch build modes in the
same cached workspace. Original ESC scripts and numerical/configuration sources
remain intact; their selected legacy launch behavior is preserved.

A closed bag can be analyzed with the shared `analyze_bag` command. Pose and
Gaussian-fill messages support trajectory/fill plots; unavailable measurements
remain unavailable. The bag does not prove successful escape solely by existing.

## Backup and promotion

Complete pre-deployment V1 source/build/install and the original numerical
library are preserved under
`~/mbuck_backups/gesc_v3_deployment_20260929T210229Z`, including `RESTORE.md`.
The full prior trees are also in `prior_workspace/`; no old generated tree was
used as a V3 build input. Old V2 source, firmware and failed records remain intact.
The source archive/receipts are redundantly retained on the laptop.

The old V1-only symlink-building Gaussian wrapper now gives an explicit
informational message and exits; its original content is backed up. The generic
Gaussian command is not silently redirected to V3 during commissioning. After
physical acceptance, promote V3 and remove only unused V1-specific active files,
retaining everything required by the original ESC methods and the backups.
