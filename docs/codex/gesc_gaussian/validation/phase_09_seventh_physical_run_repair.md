# Phase 09 seventh physical-run rotation initialization repair

Date: 2026-08-05
Milestone: M8L
State: host-qualified and transferred; operator check-only pending

## Retained run and direct result

Preserve this failed run unchanged:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/2026-08-05/
  20260805T000043179553Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_d9eb86a8
```

The passive barrier and rotation-authorization decision passed, but base
readiness never became true. The bag contains `1,900` `/cmd_vel` samples and
all are exactly zero. Rotation never reached `ALIGNING`, `SETTLING`, or
`RUNNING`; consequently source cost, filter output, and timekeeper data never
started. The recorder timed out its bounded post-rotation startup window and
performed managed shutdown. Completeness remains failed and no run file will
be rewritten or deleted.

## Causal evidence

The first true `/gesc_gaussian/rotation_authorized` bag receipt is
`1785888078881203550 ns`. `/gesc_gaussian/rotation_status` first records
`FAULT` at `1785888079448718420 ns`, approximately `0.5675 s` later, with:

```text
state: FAULT
fault_reason: rotation authorization heartbeat became stale
hardware_initialized: true
timekeeper_started: false
last_command_rpm: 0.0
```

True recorder authorization heartbeats continued near 10 Hz and one arrived
only about `0.026 s` before the fault. Thus neither the M8K gate publisher lane
nor recorder gate health failed. The rotation node's single callback lane
instead held the first true callback while it synchronously opened pigpio and
constructed PWM ownership. The state machine timestamped that same heartbeat
before initialization. When initialization exceeded the unchanged `0.50 s`
lease, a timer callback could run before a queued later heartbeat callback and
fault on the old pre-initialization timestamp. The fifth and sixth runs
entered `ALIGNING` in about `0.057 s` and `0.054 s`; those faster instances
explain why the latent race did not stop them.

## Approved bounded correction

The first true heartbeat initializes the selected rotation hardware once,
immediately commands and records neutral zero, clears the consumed timestamp,
and leaves the owner in `WAITING_AUTHORIZATION`. The owner may enter
`ALIGNING` only on a subsequent fresh true heartbeat. Ticks during this
initialized-neutral wait remain motionless and do not apply the operational
lease. After re-arm, the existing `0.50 s` authorization lease and every
encoder, command, fault, shutdown, controller, and recorder safety rule remain
unchanged.

The public schema remains version 1 and uses the existing state name. Offline
transition validation may accept initialized-neutral
`WAITING_AUTHORIZATION` only after the first recorder authorization boundary.
Preauthorization live and offline checks continue to require
`hardware_initialized=false`, `last_command_rpm=null`, and no prior
authorization.

## Pre-edit recovery evidence

Matching rollback roots are:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260805T002822-0700_m8l_rotation_initialization_rearm
/home/mattb/tb3-pi/phase09_backups/
  20260805T002822-0700_m8l_rotation_initialization_rearm
```

Before editing, snapshot and mounted-Pi normalized trees match at `347/347`
regular files and `435/435` inventory entries. The full normalized source
manifest SHA-256 is
`b4608bed1cca5a7e45f9e5411ea12156c5c40f282ea0be6d44f53ba3bea57fe0`;
the inventory SHA-256 is
`269523e491eec089a21ce72138ed8ef8b3eb3331993ef1024a86c73f20d04312`.
The four transfer candidates also match their sealed copies exactly.

## Source and validation boundary

M8L changes exactly these existing files in the offline snapshot before any
reviewed transfer:

```text
turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/rotate_frame_node/phase09_rotation_node.py
turtlebot3_vehicle_nodes/test/test_phase09_rotation_gate.py
ros_esc/ros_esc/experiment_recording/validate_run.py
ros_esc/test/test_phase09_physical_recording.py
```

## Implemented behavior

The rotation state machine now treats the first true heartbeat as permission
to initialize only. Once the hardware factory returns, it issues the existing
neutral command path, publishes `0.0 rpm`, clears the consumed heartbeat
timestamp, leaves both authorization flags false, and remains in
`WAITING_AUTHORIZATION`. Any number of waiting ticks are no-ops. The next true
heartbeat records its own fresh timestamp, sets both authorization flags, and
enters `ALIGNING`; later true heartbeats refresh the timestamp without
reopening hardware. Existing false-heartbeat revocation, post-arm staleness,
encoder, profile, fault, close, and GPIO-release paths remain fail-closed.

The validator accepts either untouched passive waiting or
initialized-neutral waiting after the recorded authorization boundary. Its
separate preauthorization loop still calls the unchanged live status contract,
which accepts only untouched hardware and a null command. The recorder owner,
its M8K three callback lanes and threads, all thresholds, and every launch and
wrapper remain unchanged.

## Host qualification

| Gate | Result |
|---|---:|
| targeted initialization/re-arm/lease/evidence tests | 16 passed |
| complete rotation and physical-recording focused files | 165 passed |
| complete snapshot Phase 09 functional suite | 269 passed |
| canonical recorder regression against snapshot owners | 69 passed |
| canonical legacy plus recording integration | 38 passed, 1 expected skip |
| Python AST and critical lint `E9,F63,F7,F82` | PASS |
| edited-file full-style delta | 1,888 before / 1,881 after; zero added-line findings |
| isolated three-package snapshot build | PASS in 15.4 s |
| isolated installed-overlay focused probe | 4 passed |

The primary regression initializes and publishes neutral at `1.0 s`, remains
in zero-command waiting when ticked at `100.0 s`, then enters `ALIGNING` only
after a new true heartbeat timestamped `100.0 s`. Separate tests prove the
unchanged `0.50 s` post-arm stale fault and false-heartbeat revocation still
neutralize and latch. The evidence test accepts initialized-neutral waiting
after authorization and explicitly proves the unchanged live preauthorization
check rejects the same status before authority.

The fresh isolated build is retained at
`/tmp/phase09_m8l_build.3pi2KJ`; it built `ros_esc_interfaces`, `ros_esc`, and
`turtlebot3_vehicle_nodes` in `15.4 s`. The sourced installed overlay resolved
both changed owners from that isolated build and passed four focused probes.

The first focused test command incorrectly placed the message-definition
source directory on `PYTHONPATH` rather than sourcing a generated interface
overlay. Collection therefore stopped at
`ModuleNotFoundError: ros_esc_interfaces`. The corrected sourced host-overlay
command passed. This command-composition error did not execute a test, change
source, or represent a product failure.

Host qualification completed before the reviewed transfer. Codex had not run
a Pi build or physical process at that boundary.

## Reviewed SSHFS transfer and final parity

Immediately before transfer, each mounted-Pi target still matched the exact
file in the M8L rollback subtree. The checksum dry run listed exactly the four
declared paths. `rsync -rlptOc` then copied those paths through the existing
SSHFS mount without a delete option; the post-transfer dry run was empty.

Final target hashes are:

```text
429469ca69ff88274e13efb6e5151d9918a58aaf8743e98a244673c323348f5c  turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/rotate_frame_node/phase09_rotation_node.py
5c9fbc40f0cc13267f023c86ca059300c12858c91b740ab62183fe3c4a940ba8  turtlebot3_vehicle_nodes/test/test_phase09_rotation_gate.py
60d5a86556f4fe91db3537fc33a86eaaa73ca42040f07c16c9bea3c40ea0a41e  ros_esc/ros_esc/experiment_recording/validate_run.py
808b9667aba7fb6c2d0c98bbc4df894b57689fa688e27e16f394fc2a9849465f  ros_esc/test/test_phase09_physical_recording.py
```

The snapshot and Pi now match at `347/347` regular files and `435/435`
inventory entries. The normalized full-source SHA-256 is
`e6315dd935f129b4da0b8071774dc38b60de66a63091c3f9f8136b913a07baf8`;
the inventory SHA-256 is
`555de4d862976f9cd11d56882e3aa47e14a83d38126761f2b702d51e3e5c559a`.
Generated cache directories and bytecode are zero in both roots. Mounted AST
and critical lint pass. Identical `POST_TRANSFER.md` receipts in both backup
roots have SHA-256
`694a9f83ef3c8dcd9bfe5fa9f4222fdf4e21b1b01a9f2f68fa4ca7f1b81b8cec`.

Codex did not execute a Pi build, source an overlay on the Pi, launch ROS,
open either device, connect Vicon, start a recorder, actuate, or move the
robot. Since Pi source changed, the next incomplete gate is exactly one
operator-owned selected `--check-only`. A passing check returns to the normal
lab/Vicon SOP and bare wrapper; it does not create a per-run check ceremony.
