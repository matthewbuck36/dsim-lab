You are implementing the approved Phase 09 Plan in the local physical
TurtleBot3 source snapshot, or recovering a later dated continuation recorded
by the Plan/status/handoff. The original M0-M7 implementation is strictly
no-hardware. This prompt alone never authorizes mounting or writing the
physical Raspberry Pi, executing a Pi command, launching ROS, accessing a
device, actuating a mechanism, calibrating, or moving the TurtleBot3; only a
current explicit user authorization may open the exact bounded continuation
described below.

## Recover the durable boundary

Read completely:

- `AGENTS.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/10_PHYSICAL_EXPERIMENT_READINESS.md`;
- `docs/codex/gesc_gaussian/plans/phase_09_plan.md`;
- `docs/codex/gesc_gaussian/status/phase_09_status.md`, if already present;
- `docs/codex/gesc_gaussian/validation/phase_08_8_final_report.md`;
- `docs/codex/gesc_gaussian/handoffs/phase_08_8_handoff.md`;
- `docs/codex/gesc_gaussian/status/phase_08_status.md`; and
- `docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt`.

Inspect current code, Git state, the saved Plan, and the physical snapshot
before editing. The saved Plan is authoritative unless current evidence
requires a bounded, documented correction under the Level A/B/C policy.

Initialize the live status without overwriting a nonempty file, then run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 09
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 09 implement
```

The historical absence of a broad `simulation_ready=true` tag does not block
the approved selected-scenario snapshot implementation. It also does not
become a passing Phase 08 claim. Missing Plan/status context, an interface or
ownership conflict, loss of simulation/physical parity, or any attempt to
command hardware remains a stop.

## Exact edit and hardware boundary

Implement physical source changes only under:

```text
/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src
```

Keep Phase 09 Plan, status, validation, manifests, checkpoints, and handoff in
`/home/mattb/dsim-lab/docs/codex/gesc_gaussian/`.

The snapshot is not Git-controlled. Before its first edit:

1. create the approved recoverable source backup;
2. record an exact source inventory and SHA-256 manifest;
3. prove `/home/mattb/tb3-pi` is not mounted or accessed; and
4. record the baseline paths and hashes in the live Phase 09 status.

Do not edit `/home/mattb/tb3-pi`, use SSH/SSHFS, command motors, invoke a
physical launch, or perform a physical sensor test. Do not copy generated
`build`, `install`, `log`, cache, editor, Git-metadata, or runtime content.

### M8B continuation boundary

<!-- MBuck 2026-08-01: A fresh continuation must recover M8B state and preserve the exact commissioning order. -->

The paragraph above is the original M0-M7 snapshot-only boundary. For an M8B
continuation, first read the current Phase 09 Plan, status, handoff, and Pi
transfer receipt. The M8B snapshot implementation, host-side qualification,
and reviewed real-Pi source sync passed. The receipt records backup
`/home/mattb/tb3-pi/phase09_backups/20260802T031409Z_m8b`, `345/345` matching
regular-file hashes, and `432/432` matching inventory entries. Only a current
explicit user authorization may permit another reviewed SSHFS source-only
comparison/transfer. In that case, create and verify a new scoped rollback
backup before write, transfer only exact manifest paths with no delete behavior
or generated/runtime content,
and require target hashes plus an empty final dry run. Do not execute a command
on the Pi, build/source there, start ROS, open serial/GPIO, start Vicon live,
command a mechanism, calibrate, operate lamps, or move the robot under source-
transfer authority.

The first future Pi-executed software gate is a separate bounded on-Pi
build/source and installed-static check. It is currently `NOT RUN`; a host
build or host test that reads SSHFS-mounted files cannot satisfy it.

## Required implementation contract

Integrate the current terminal, cumulative Phase 08 counted-source GESC +
adaptive Gaussian behavior through v8.12 into the existing physical owners.
Reuse or extend the snapshot's `ros_esc`, `ros_esc_interfaces`, and
`turtlebot3_vehicle_nodes`; do not create a parallel algorithm or duplicate
controller/recorder stack.

The TurtleBot3 is shared laboratory equipment. Preserve every pre-existing ESC
Bash run file, historical launch, and legacy configuration byte-for-byte
against the sealed baseline. Do not extend the historical
`light_gesc_gaussian_fill_experiment.launch.xml` in place. Put the selected
Phase 09 orchestration in a new dedicated launch and point only the new managed
Phase 09 wrapper and physical recorder target contract at it. A change that
breaks or silently reroutes any legacy wrapper is a hard compatibility stop.

### Final operator-entry and recording contract

Name the selected new-only Bash entry point exactly
`gesc_gaussian_two_source_voltage.bash` and its selected new-only launch
exactly `gesc_gaussian_two_source.launch.xml`. Remove the superseded Phase
09-only installed names rather than leaving ambiguous aliases. This rename may
not touch any historical wrapper, launch, or configuration.

The selected manual Bash entry point must change to the reviewed ROS 2
workspace, run `colcon build --packages-select ros_esc_interfaces ros_esc
turtlebot3_vehicle_nodes`, verify `install/setup.bash`, and then source that
workspace before resolving installed package assets. Add an explanatory
`MBuck <date>` comment and a regression assertion that build precedes source.
Do not add this behavior to, or otherwise edit, a historical wrapper.

Keep `ros2 run ros_esc record_run` as the only recorder, readiness owner, and
shutdown/completeness owner. The selected wrapper must opt into a terminal tee
and a bounded one-second live diagnostic summary while the same output remains
in `console.log`. The summary should include readiness, voltage/raw cost,
augmented-cost components, filter output, algorithm state/fill count,
wheel/IMU odometry, unambiguously labeled Vicon evaluation pose/status, and
final `vx`/`wz` when those inputs are available. Do not add `ros2 topic echo`,
the legacy CSV collector, or another bag process.

Each selected run must automatically create one unique run directory and one
sqlite3 rosbag containing all legacy sensor/encoder/odometry/filter/command/
timekeeper streams plus the typed GESC/Gaussian diagnostics and both required
evaluation-only Vicon streams. Retain metadata, resolved topics/parameters,
notes, console output, completeness evidence, and
validated SHA-256 copies of the calibration, selected profile, scenario
metadata, controller, filter, and rotation files under that same run
directory, together with the selected wrapper/launch and recorder topic/QoS
contracts. Print the run directory at startup and completion. Preserve full
Git provenance when available, but record an explicit nonfatal
`git.available=false` state when the source-only physical workspace is not a
Git checkout.

### Evaluation-only Vicon and commissioning contract

Wheel/IMU-backed `/odom` is the sole pose input to every controller,
supervisor, PDE/history, modified-cost, fill-placement, and escape owner. Vicon
is required evidence for an accepted selected two-source run, but only as
`geometry_msgs/msg/PoseStamped` on
`/gesc_gaussian/evaluation/vicon_pose` plus a canonical `std_msgs/msg/String`
status heartbeat on `/gesc_gaussian/evaluation/vicon_status`. Require reviewed
subject/segment identity, exact server-script hash, protocol/session,
advancing packet sequence and Tracker frame, nonocclusion, finite normalized
pose, freshness, and run coverage. These may gate recorder readiness and
offline completeness; no Vicon value may be remapped, forwarded, or copied
into `/odom`, motion, fill, ranking, escape, or stopping logic. Keep all legacy
Vicon/odometry sources and launches byte-identical.

Keep shipped calibration/profile/scenario templates inert. Create mutable
calibration and primary/secondary metadata copies under
`${XDG_CONFIG_HOME:-$HOME/.config}/dsim-lab/phase09` before the stationary
preflight; keep the selected profile frozen. `--stationary-preflight` runs
while uncalibrated with readiness false, selects a passive Phase-09-only
timekeeper instead of the servo command owner, never authorizes motion, and
fails on any base/rotation
actuation or robust lifecycle advance. It must not self-certify. After an
operator reviews the retained offline PASS,
`--approve-stationary RUN_DIR --reviewer NAME` may set the persistent gate only
when it consumes the exact same site-metadata bytes and retained hash-coupled
evidence.

Future execution order is immutable: (1) separate on-Pi build/installed-static
gate; (2) calibration and primary/secondary metadata site copies; (3)
uncalibrated/readiness-false/no-actuation
`--stationary-preflight`; (4) review plus hash-coupled
`--approve-stationary RUN_DIR --reviewer NAME`; (5) independent emergency-stop
test followed by a separately authorized safe nontranslating/final-zero
rehearsal; (6) real retained calibration; (7) `--check-only`; and (8) the bare
`gesc_gaussian_two_source_voltage.bash` for the primary scenario with assigned
operator/observer and typed `RUN`. The bare wrapper is the eventual normal
primary entry point; there is no noninteractive motion bypass.

### M8C lab-SOP one-command implementation amendment

<!-- MBuck 2026-08-03: Supersede the M8B commissioning gates with the established lab SOP and one bare wrapper. -->

This M8C amendment is controlling wherever it conflicts with the historical
M8B commissioning text in this prompt. Retain M8B qualification, backup,
transfer, parity, and failed/unrun evidence, but remove its operator gates from
the selected runtime.

Implement the normal human workflow from the attached
`DSIM - TurtleBot3 Vicon Setup.pdf`: the operator prepares Vicon Tracker and
runs the unchanged Windows `vicon-tracker-server.py`, then invokes bare
`gesc_gaussian_two_source_voltage.bash` on the Pi. That wrapper must build
exactly `ros_esc_interfaces`, `ros_esc`, and `turtlebot3_vehicle_nodes`, source
the result, start `pigpiod` only if absent, start the sole selected managed
recorder/launch, announce the run directory, and display bounded one-second
diagnostics. It must not require a separate build command, site configuration,
calibration approval, stationary preflight, `--check-only`, typed `RUN`, Vicon
subject/segment entry, server-file SHA-256, handoff authorization, or a
`PHYSICAL READY` tag.

Leave `vicon-tracker-server.py` untouched. Reuse its legacy `struct.pack('7f')`
transport and the existing odometry owner to expose Vicon only as
`nav_msgs/msg/Odometry` on `/gesc_gaussian/evaluation/vicon_odom`. Wheel/IMU
`/odom` remains the sole algorithm pose. Do not retain the M8B custom JSON
evidence protocol or pose/status readiness gate in the selected graph. Missing,
stale, or incomplete Vicon must remain visible in live output and make retained
evaluation evidence incomplete, but it must never inhibit or stop motion.

Preserve the existing managed `Ctrl+C` shutdown: readiness false, stop/final
zero, rosbag coverage through the zero dwell, finalization, bounded validation,
and retained run-directory output. Store the legacy streams, typed
GESC/Gaussian diagnostics, and evaluation-only Vicon odometry in the same
sqlite3 bag. Preserve every historical ESC wrapper/launch/configuration and its
owner selection. Do not run live hardware during this implementation task.
Record M8C validation and transfer outcomes only after direct verification; the
current Phase 09 status/handoff now contain the completed host and Pi-parity
results.

### Cumulative v8.12 source-selection rule

Do not cherry-pick, blend, or independently merge v8.10, v8.11, and v8.12.
They are successive experiment/evidence versions in one cumulative Git
history. V8.10 retained the counted-candidate profile; v8.11 changed the
simulation evaluator/schema without changing core runtime owners; and v8.12
added the `interior_farthest` odometry-history fallback to the three existing
supervisor files. The shared core runtime did not change between qualifying
v8.12 commit `0263f1c` and Phase 08 terminal commit `c04c222`.

Port the current terminal shared runtime files exactly and prove their
source-to-snapshot hashes. Do not copy the v8.11 simulation evaluator or its
source geometry into physical control. The selected physical wrapper must
explicitly set:

```text
open_field_escape_interior_anchor_fallback_enabled=True
open_field_escape_interior_anchor_min_displacement_m=0.50
```

Keep the shared node/launch default `False` for legacy and nonselected paths;
the original `outside_radius` anchor retains priority. Preserve the historical
v8.12 `13/14` formal result, while implementing the complete scientific
behavior the user accepted. Stop if the saved Plan or implementation diff
selects an older runtime boundary, disables the fallback in the selected
wrapper, or introduces evaluator geometry into control.

Preserve:

- rotating photoresistor raw minimization cost and timestamp semantics;
- wheel odometry and permitted IMU inputs;
- known source count and counted-candidate raw-cost ranking;
- adaptive typed Gaussian fill lifecycle and exact one-fill behavior for two
  sources;
- temporary affine/approach-continuity assistance, including the v8.12
  interior-anchor fallback explicitly enabled by the selected physical wrapper
  while remaining default-off for legacy/nonselected paths, plus direct and
  assisted escape paths;
- persistent Gaussian memory after affine assistance is cleared;
- legacy profile selection plus byte-identical legacy Bash/launch/config entry
  points;
- canonical topics, public message semantics, cost sign/units, and the sole
  physical `/cmd_vel` owner;
- Phase 05 recording/final-zero contract; and
- simulation/physical algorithm parity.

Do not add GPS, Vicon, source position/role/intensity, room dimensions, global
coordinates, SLAM, route planning, autonomous wall avoidance, or a physical
coordinate-distance stop to control. Required Vicon evaluation evidence stays
on its separate pose/status topics; no Vicon value may affect control, fill,
escape, ranking, or stopping.

Physical arrival remains operator `Ctrl+C`. The selected field assumption is
open, obstacle-free, and human-managed. A future physical run must still prove
stale-input stop, readiness false, final-zero ordering, recorder finalization,
emergency stop, and scoped cleanup before motion is authorized.

## Execution discipline

Work one Plan milestone at a time. Before moving on:

- run the milestone's focused static/offline tests;
- record exact commands, outcomes, skips, and retained paths in
  `docs/codex/gesc_gaussian/status/phase_09_status.md`;
- inspect snapshot and repository diffs for unintended scope;
- run `bash -n` for every Bash entry point, resolve every wrapper launch and
  supplied argument, run installed `--show-args` for every unique referenced
  launch, and verify all pre-existing wrapper/launch/config hashes;
- update the before/after snapshot manifest and recoverable patch evidence;
- run `checkpoint_phase.sh 09` at material boundaries; and
- create only bounded, authorized `dsim-lab` commits for durable Phase 09
  documentation/manifests. Never imply that external snapshot files were
  captured by Git unless a retained patch or manifest proves them.

Use bounded host-side checks only: static imports where dependencies exist,
unit tests, syntax/YAML/XML parsing, interface comparison, launch construction
without hardware, source-package builds that are compatible with the host,
and recorder/configuration validation. Report Pi-only, hardware-only, serial,
GPIO, Arduino, motor, live-topic, emergency-stop, and physical-motion checks as
unexecuted—not passed.

Label host builds and tests as host-side. Label checks that merely read the
SSHFS tree as host-mounted-source checks. Neither is an on-Pi build, installed
static check, live ROS graph, or hardware result.

Do not weaken acceptance or safety checks merely to make host qualification
green. Preserve every failed attempt and distinguish source integration,
static readiness, and physical readiness.

## Required closeout

Write:

```text
docs/codex/gesc_gaussian/handoffs/phase_09_handoff.md
```

Also retain the final snapshot inventory, before/after SHA-256 manifests,
reviewable source patch/diff, static validation report, reviewed SSHFS transfer
manifest and receipt when authorized, Pi backup/rollback procedure, and exact
hardware-deferred checklist. The static report must include shared-lab legacy
hash, entry-point, Bash syntax, wrapper-to-launch compatibility, `/odom` versus
Vicon isolation, and stationary no-actuation evidence.

Close Phase 09 snapshot implementation only when the declared static criteria
pass, every skip is explicit, the snapshot is recoverable, runtime is inactive,
the live status and checkpoint are current, and Git plus external snapshot
state are reported. Do not declare physical readiness or run the robot.

Recommended bounded commit message:

```text
phase 09: integrate physical snapshot workflow
```
