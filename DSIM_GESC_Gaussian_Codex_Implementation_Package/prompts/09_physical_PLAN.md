You are planning Phase 09 inside the existing `dsim-lab` Git repository.
Phase 09 will integrate the current terminal, cumulative Phase 08 GESC +
Gaussian algorithm through v8.12 into the local source-only snapshot of the
physical TurtleBot3. Planning and later snapshot implementation do not
authorize physical motion.

## Read before doing anything

Read completely:

- `AGENTS.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/00_MASTER_IMPLEMENTATION_PLAN.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`;
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/10_PHYSICAL_EXPERIMENT_READINESS.md`;
- `docs/codex/gesc_gaussian/implementation_sequence.md`;
- `docs/codex/gesc_gaussian/validation/phase_08_8_final_report.md`;
- `docs/codex/gesc_gaussian/handoffs/phase_08_8_handoff.md`;
- `docs/codex/gesc_gaussian/status/phase_08_status.md`; and
- `docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt`.

Reconstruct the current state from code, Git, the final reports, and retained
interfaces. Do not rely on chat memory or reopen a failed Phase 08 version.
The final Phase 08 closeout commits are `9335da2` and `c04c222`.

Before planning, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 09 plan
```

If required durable context is missing, stop and report it. The absence of the
historical broad `simulation_ready=true` tag is not a blocker for this
selected-scenario, no-hardware Plan. Do not alter or relabel the historical
Phase 08 result.

## Current user authority and evidence boundary

The user accepts the demonstrated simulation evidence as sufficient for a few
selected physical scenarios:

- v8.10 primary fixed two-light layout: `11/11` formal passes;
- v8.11 secondary fixed two-light layout: `6/6` formal passes; and
- v8.12 interior-anchor visible probe: `1/1` formal pass.

The v8.12 matrix remains formally failed on its first case, despite complete
local-to-global scientific behavior. Do not claim arbitrary layout/intensity,
three-light, wall, obstacle, or broad simulation readiness.

## Cumulative v8.12 algorithm-selection rule

Do not cherry-pick, blend, or independently merge v8.10, v8.11, and v8.12.
They are successive experiment/evidence versions in one cumulative Git
history:

- v8.10 retained the counted-candidate controller profile and corrected the
  scenario runner/recorder working-directory boundary;
- v8.11 changed the simulation evaluator/schema for shifted aggregate-basin
  association but did not change the controller, filter, Gaussian-fill,
  modified-cost, convergence-detector, or supervisor runtime owners; and
- v8.12 added the opt-in `interior_farthest` odometry-history fallback to the
  three existing supervisor files.

The shared core runtime did not change between the qualifying v8.12 source
commit `0263f1c` and Phase 08 terminal commit `c04c222`. Plan one exact port of
the current terminal shared runtime files. The selected physical wrapper must
explicitly enable:

```text
open_field_escape_interior_anchor_fallback_enabled=True
open_field_escape_interior_anchor_min_displacement_m=0.50
```

Keep the shared node/launch default `False` for legacy and nonselected paths.
The original `outside_radius` anchor retains priority. Preserve the historical
v8.12 `13/14` formal result without treating its completed scientific behavior
as excluded from the user-selected physical algorithm. V8.11 evaluator
topology remains recorder/evaluator metadata and must never enter control.

This authority permits Phase 09 planning and, after an approved Plan,
snapshot-only implementation and static qualification. It does not authorize
mounting or writing to the live Pi, commanding motors, or running physical
hardware. Later physical motion requires a separate explicit user
authorization plus live calibration, emergency-stop, final-zero, recording,
and operator-readiness checks.

### Shared-laboratory compatibility authority

The TurtleBot3 is shared. Plan strict nonregression for every pre-existing ESC
method and its Bash run file. The historical
`light_gesc_gaussian_fill_experiment.launch.xml`, all pre-existing Bash
wrappers, and their legacy configurations must remain byte-identical to the
sealed snapshot baseline. Put the selected Phase 09 graph in a new dedicated
launch file and point only a new managed Phase 09 wrapper at it. Plan static
`bash -n`, wrapper-to-launch argument resolution, installed `--show-args`,
entry-point preservation, and baseline hash checks for every legacy wrapper.

### Final operator-entry and recording authority

The selected new-only manual entry point is exactly
`gesc_gaussian_two_source_voltage.bash`, and its selected new-only launch is
exactly `gesc_gaussian_two_source.launch.xml`. Do not retain aliases under the
superseded Phase 09-only names, and do not rename or alter any historical
wrapper or launch.

The selected manual Bash entry point must change to the reviewed ROS 2
workspace, build exactly `ros_esc_interfaces`, `ros_esc`, and
`turtlebot3_vehicle_nodes`, verify the resulting `install/setup.bash`, and
source it before resolving installed package assets. Preserve this behavior
with a build-before-source regression assertion. This requirement applies only
to the new Phase 09 wrapper and must not alter any historical wrapper.

Plan the existing `ros_esc record_run` as the sole recorder. One selected run
must automatically create one unique run directory and one sqlite3 rosbag that
contains the legacy sensor, encoder, odometry, filter, command, and timekeeper
streams plus the additional typed GESC/Gaussian diagnostics and both required
evaluation-only Vicon pose/status streams. The same run
directory must retain metadata, resolved topics/parameters, notes, console
output, completeness evidence, and hashed byte-for-byte copies of the exact
calibration/profile/scenario/controller/filter/rotation inputs plus the
selected wrapper/launch and recorder topic/QoS contracts. Do not plan a second
recorder or promise legacy CSV-format equivalence.

Plan an opt-in terminal tee and a bounded one-second diagnostics summary for
the selected wrapper only, with wheel/IMU odometry and Vicon evaluation data
unambiguously labeled. Preserve complete Git provenance when available,
but explicitly support the normal physical case where the source-only Pi
workspace is not a Git checkout. The run directory must be visible at startup
so evidence remains findable after an interrupted manual run.

### M8B continuation amendment

<!-- MBuck 2026-08-01: Preserve the approved M8B control/evaluation and commissioning order across fresh planning runs. -->

For an M8B continuation, read the current Phase 09 Plan, status, handoff, and
transfer receipt before treating the older snapshot-only wording below as the
active boundary. The M8B snapshot implementation, host-side qualification, and
reviewed real-Pi source sync have passed. The current receipt records backup
`/home/mattb/tb3-pi/phase09_backups/20260802T031409Z_m8b`, `345/345` matching
regular-file hashes, and `432/432` matching inventory entries. A dated,
user-authorized, reviewed SSHFS source-only transfer does not authorize an
on-Pi command, build, ROS graph, serial/GPIO access, Vicon commissioning,
actuator, calibration, or
motion, and it is not standing authority for a later transfer.

Freeze this architecture in every continuation:

- wheel/IMU-backed `/odom` is the sole algorithm pose;
- Vicon is required accepted-trial evaluation evidence only on
  `/gesc_gaussian/evaluation/vicon_pose` (`PoseStamped`) and
  `/gesc_gaussian/evaluation/vicon_status` (`String`);
- Vicon identity, session, advancing sequence/Tracker frame, occlusion,
  freshness, and run coverage may gate recorder readiness/completeness but may
  never enter controller, fill, escape, ranking, or stopping calculations;
- historical Vicon/odometry, rotation, launch, configuration, and Bash paths
  remain byte-identical; and
- the bare `gesc_gaussian_two_source_voltage.bash` is the eventual normal
  primary-run entry point and still requires the assigned operator/observer
  plus typed `RUN`.

Plan future commissioning in this exact order: (1) a separate bounded on-Pi
build/source and installed-static gate, currently `NOT RUN`; (2) create mutable
calibration and primary/secondary metadata copies under
`${XDG_CONFIG_HOME:-$HOME/.config}/dsim-lab/phase09`; (3)
run `--stationary-preflight` while uncalibrated, readiness false, and no base
or rotating-frame actuation is possible; (4) review the retained PASS and run
`--approve-stationary RUN_DIR --reviewer NAME` against the exact same
hash-coupled metadata bytes; (5) test the independent emergency stop, then run
a separately authorized safe nontranslating/final-zero rehearsal; (6) perform
and retain real calibration; (7) run `--check-only`; and (8) invoke the bare
wrapper for the primary scenario and type `RUN` only after the displayed live
conditions pass. Do not claim `PHYSICAL READY`, completed calibration, a live
Vicon identity, an on-Pi build, a ROS graph, or motion without retained direct
evidence.

### M8C lab-SOP one-command amendment

<!-- MBuck 2026-08-03: Make the attached lab SOP and bare selected wrapper the controlling operator workflow. -->

This M8C amendment supersedes every conflicting M8B/M9 operator-gate statement
in this prompt. Preserve M8B source-integration, validation, backup, transfer,
and parity results as historical evidence, but do not carry its commissioning
ceremony into the current design.

Plan the normal human-operated experiment exactly around the attached
`DSIM - TurtleBot3 Vicon Setup.pdf`: prepare Vicon Tracker on the Windows
computer, run the unchanged `vicon-tracker-server.py`, prepare a clear floor and
the two lamps, SSH to the Pi, and invoke bare
`gesc_gaussian_two_source_voltage.bash`. The wrapper must build the selected
three ROS packages, source the workspace, start `pigpiod` only if absent, start
the one managed recorder/launch, print the run directory, and show bounded live
diagnostics. Do not require a separate build, site copies, calibration approval,
stationary preflight, `--check-only`, typed `RUN`, subject/segment input,
server-script SHA-256, handoff authorization, or a `PHYSICAL READY` tag.

Keep wheel/IMU-backed `/odom` as the sole algorithm pose. Reuse the existing
legacy `7f` Vicon transport and existing odometry owner to publish passive
evaluation `nav_msgs/msg/Odometry` on
`/gesc_gaussian/evaluation/vicon_odom`. Vicon loss, staleness, or incompleteness
must be conspicuous in live diagnostics and retained evaluation evidence, but
must never gate, stop, steer, rank, or otherwise alter motion.

Operator `Ctrl+C` is the normal stop. Preserve automatic readiness-false,
final-zero, bag zero-dwell, finalization, bounded validation, and run-directory
reporting inside the wrapper/recorder without adding operator approvals. Keep
all legacy ESC Bash and launch entry points working. This planning or
implementation work must not itself launch physical hardware; report M8C
implementation, host validation, source transfer, and hardware results only
after they actually occur.

### M8D familiar post-bag CSV amendment

<!-- MBuck 2026-08-03: Preserve familiar physical CSV outputs without adding a live collector or second recorder. -->

For the selected wrapper only, plan the runtime root as
`${HOME}/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/<UTC-date>/<run-id>/`.
The one sqlite3 rosbag remains the sole recorder and source of truth. After that
bag cleanly finalizes, plan the existing `record_run` final validation path to
atomically and idempotently export these headerless familiar files into the same
run directory:

- `encoder.csv`: `[timestamp, angle]`;
- `cost_value.csv`: `[timestamp, augmented cost]` from `/cost_modified`;
- `filter_value.csv`: `[timestamp, two filter values]`;
- `control_value.csv`: `[timestamp, six command-array values]`; and
- `odometry.csv`: `[timestamp, x, y, z, qw, qx, qy, qz]` with legacy
  Vicon/evaluation plotting semantics.

Also plan `raw_cost_value.csv` as `[timestamp, raw_cost]`, with
`raw_cost=-voltage`, and `algorithm_odometry.csv` as
`[timestamp, x, y, z, qw, qx, qy, qz]` from algorithm `/odom`. Require
`legacy_csv_manifest.json` to retain source mappings and semantics, row counts,
byte sizes, SHA-256 hashes, and bounded export errors. Export incompleteness
must fail final validation.

Do not add a second bag process or live CSV collector. Terminal diagnostics
remain live while the bag records; CSVs appear only after clean shutdown and bag
finalization. The old `extract_test_data` column reader may consume the files
directly, but do not promise automatic discovery by its top-level `Test_*`
browser and do not fabricate `comments.txt`. This M8D amendment supersedes the
earlier no-CSV-equivalence statement only for this selected wrapper's post-bag
export. Keep all legacy wrappers, nodes, launches, and experiment behavior
unchanged, and do not broaden any safety or hardware-readiness claim.

## Exact physical snapshot boundary

The physical Pi-home snapshot is:

```text
/home/mattb/physical_TB3_files_snapshot/pi
```

The physical ROS source target is:

```text
/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src
```

It contains the existing `ros_esc`, `ros_esc_interfaces`, and
`turtlebot3_vehicle_nodes` packages. The snapshot is not Git-controlled.
Plan a recoverable pre-edit backup, source manifest, and SHA-256 baseline
before any later implementation edit.

The original Plan and snapshot-only implementation must not mount, read from,
or write to `/home/mattb/tb3-pi`. Any later SSHFS comparison or source-only
transfer requires its own explicit current authorization, exact manifest,
pre-write rollback backup, reviewed dry run, and receipt; the prompt itself is
not authorization.

## Controller and experiment constraints

The physical controller may consume only:

- the rotating photoresistor and derived raw minimization cost;
- wheel odometry;
- IMU data already required by the physical stack;
- active typed Gaussian fills; and
- the configured total source count.

It may not consume GPS, Vicon pose, source coordinates, source roles, declared
lamp intensities, room dimensions, a global start position, or evaluator
proximity. Vicon is required on separate canonical topics for selected-trial
evaluation evidence and recorder completeness only; it must not enter control,
classification, fill design, escape direction, ranking, or stopping.

Preserve the Phase 08 algorithm contract:

- every confirmed extremum begins as an unknown candidate;
- raw complete-rotation cost owns candidate comparison;
- the adaptive Gaussian is persistent visited-basin memory;
- affine/approach direction is temporary local-recovery assistance;
- direct and supervisor-assisted escape remain supported;
- known source count two permits exactly one local fill before terminal
  ranking;
- the physical arrival decision is manual operator `Ctrl+C`;
- shutdown must publish readiness false and final zero before recording and
  scoped cleanup finish; and
- the initial field is open, obstacle-free, and operator-managed, with no
  autonomous wall or obstacle-avoidance claim.

## Planning rules

1. Do not edit source code in this Plan task.
2. Do not run or command physical hardware.
3. Preserve simulation/physical algorithm parity; only adapters, launch,
   calibration, and physical configuration may differ.
4. Reuse existing owners. Do not create a second controller, supervisor,
   recorder, validator, or message owner. Isolate orchestration in a dedicated
   Phase 09 launch without editing the historical launch.
5. Preserve every legacy Bash entry point/launch/configuration, legacy
   behavior, cost sign/units, canonical topics, message semantics, and the
   existing physical `/cmd_vel` owner.
6. Do not introduce Heavy-Ball ESC, SLAM, route planning, or a coordinate-based
   physical global stop.
7. Inspect the snapshot and current `dsim-lab` source before naming exact
   files, topics, interfaces, or dependencies.
8. Apply the Level A/B/C policy. Missing motion authority is a hard stop only
   for physical motion, not for safe Plan work or static snapshot integration.

## Required Plan content

Plan one reviewable milestone at a time, including:

1. snapshot baseline, backup, manifest, and recovery procedure;
2. current `dsim-lab` versus snapshot package/interface/launch audit;
3. exact current terminal cumulative v8.12 algorithm-source integration,
   without version cherry-picking or a simulation/physical fork;
4. photoresistor, odometry, IMU, required evaluation-only Vicon, command, stop,
   and readiness adapters;
5. a dedicated Phase 09 launch/configuration with conservative inactive
   defaults and byte-identical historical launches/wrappers;
6. source-response calibration and the two selected scenario definitions;
7. Phase 05 recorder/validator reuse and run metadata;
8. manual `Ctrl+C`, emergency stop, stale-input, and final-zero behavior;
9. host-side static tests, syntax/interface checks, launch construction, and
   build checks that are possible without the Pi;
10. explicit hardware-required checks that must remain unexecuted;
11. later SSHFS read-only diff, Pi backup, scoped source transfer, and rollback
    procedure, with the separate on-Pi build/installed-static gate explicitly
    distinguished from host or mounted-source checks;
12. the exact M8B/M9 site-copy, stationary preflight/approval, emergency-stop,
    nontranslating rehearsal, calibration, check-only, and bare-run order; and
13. exact stop conditions, checkpoints, commits, and handoff evidence.

Do not plan a blind whole-home mirror. The later transfer must use a reviewed
source/configuration manifest and exclude generated `build`, `install`, `log`,
cache, editor, Git-metadata, and runtime paths.

## Required durable artifact

Write one self-contained Plan suitable for review at:

```text
docs/codex/gesc_gaussian/plans/phase_09_plan.md
```

It must include the objective and nonclaims, repository and snapshot findings,
exact files to modify/create, ownership/interface effects, parameter defaults,
compatibility strategy, milestone sequence, tests and commands, checkpoint
boundaries, stop conditions, risks, hardware-deferred checks, SSHFS transfer
boundary, and assumptions requiring implementation-time verification.

For an initial planning-only run, end after the Plan, context validation
result, Git state, and a clear statement that no snapshot source, live Pi file,
or physical process was changed. For a separately authorized M8B continuation,
report only the exact source/evidence actions actually verified, distinguish
host-side from on-Pi results, and retain every unrun build, Vicon, ROS,
calibration, safety, mechanism, and motion gate as `NOT RUN`.

### Current M8E runtime-repair planning boundary — 2026-08-04

<!-- MBuck 2026-08-04: Recover the accepted on-Pi check-only result without treating it as a physical experiment. -->

For any continuation after M8E, first read
`docs/codex/gesc_gaussian/validation/phase_09_pi_runtime_repair.md`. The first
bare wrapper attempt is retained failed commissioning evidence: omitted
`~/turtlebot3_ws` underlay plus stale selected installs prevented readiness,
and no motion occurred. Do not rerun, delete, or relabel that run merely to
obtain a clean result.

The accepted repair is selected-only and legacy-preserving. It restores the
established TurtleBot3 source underlay before a three-package
`--symlink-install` build, verifies installed-source parity, uses distinct
photoresistor `/dev/ttyUSB0` and OpenCR `/dev/ttyACM0`, and starts the selected
base without lidar because this open-field algorithm has no `/scan` consumer.
All historical ESC wrappers and launch files remain unchanged. The exact
historical sound-profile module is restored so clean rebuilds preserve that
legacy entry point.

The operator-run `--check-only` passed all three packages in `1 min 39 s`,
installed Python parity (`ros_esc=63`, `turtlebot3_vehicle_nodes=21`), and both
launch constructions without opening serial, starting pigpio/Vicon/ROS/
recording, or moving the robot. Final snapshot/Pi parity is `345/345` files and
`433/433` inventory entries. Do not plan another repository authorization
ceremony or require repeated check-only before ordinary runs.

One OS prerequisite remains: correct and verify the Pi's absolute clock once;
it printed Pacific wall-clock numbers as UTC and was about seven hours behind.
Only after that correction should planning proceed to the attached lab SOP and
bare wrapper. Retain actual sensor, odometry, Vicon, command, final-zero, bag,
CSV, and physical two-light behavior as unverified until a real run proves
them.
