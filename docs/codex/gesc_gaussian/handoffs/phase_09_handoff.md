# Phase 09 Handoff — Physical Source Integration and Lab-SOP Entry

Date: `2026-08-03` (`America/Los_Angeles`)

Current outcome: `M8C ONE-COMMAND SOURCE CONTRACT, HOST QUALIFICATION, AND REAL-PI SOURCE PARITY PASS — LIVE HARDWARE NOT RUN BY CODEX`

The current human operator follows the attached lab Vicon SOP and invokes bare
`gesc_gaussian_two_source_voltage.bash`; no repository readiness tag,
authorization file, typed confirmation, site copy, calibration approval,
subject/segment value, or hash key is required. M8C implementation, host
qualification, recovery backup, and reviewed SSHFS source transfer passed with
exact `342/342` regular-file and `430/430` inventory parity. No direct Pi
command, on-Pi build/source, ROS graph, serial/GPIO access, live Vicon
connection, sensor, motor, servo, rotating frame, lamp, floor trial, or robot
motion was run by Codex.

## Historical M0-M8B implementation record (superseded by M8C)

The implementation record from this heading through the M8B terminal boundary
is retained for provenance. Its JSON Vicon pose/status, inert calibration,
stationary-preflight, typed-authorization, and readiness-tag procedures are not
the current operator contract. The controlling handoff is the M8C amendment at
the end of this file.

## What was integrated

The local source-only physical snapshot at:

```text
/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src
```

now contains the current terminal Phase 08 shared runtime and typed interfaces,
plus bounded physical sensor/recording packaging. The selected behavior is one
cumulative v8.12 source boundary:

- v8.10 supplies the retained counted-candidate controller profile and primary
  evidence;
- v8.11 supplies evaluator/schema and secondary evidence without changing the
  core controller runtime; and
- v8.12 adds the opt-in `interior_farthest` odometry-history fallback at the
  frozen `0.50 m` minimum displacement.

The implementation does not blend three independent algorithms. The selected
wrapper explicitly enables the cumulative v8.12 fallback; shared and legacy
defaults remain off. The historical v8.12 `13/14` formal broad-matrix hiccup is
retained and no broad simulation/physical robustness claim is made.

## Shared-lab compatibility boundary

The user's shared-robot requirement is enforced structurally:

- the historical `light_gesc_gaussian_fill_experiment.launch.xml` is restored
  byte-for-byte to its M0 SHA-256;
- all 26 pre-existing Bash entry points, all 8 legacy launches, and 6 legacy
  controller/filter/rotation configs retain their M0 hashes;
- the selected graph exists only in
  `gesc_gaussian_two_source.launch.xml`;
- only the new `gesc_gaussian_two_source_voltage.bash` and the physical
  recorder target contract point to that new launch;
- all 27 Bash files pass syntax and static launch/argument checks; and
- all original package console entry points remain present.

The new launch has no legacy Vicon-to-odometry relay, legacy CSV owner, broad
`pkill`, evaluator coordinate input to control, or second `/cmd_vel` owner.
M8B adds only a selected Phase-09 Vicon evidence client on separate evaluation
topics. Historical wrappers retain their historical launch behavior.

One inherited acoustic spelling mismatch remains intentionally byte-identical:
the wrappers pass `input_encoder_data_to_filter=True`, while the launch declares
`input_encoder_data_into_filter=True`. Every wrapper requests the unchanged
effective default `True`, and installed `--show-args` accepts the invocation.
The compatibility test permits only this exact behavior-neutral historical
case.

## Physical data and safety contract

The existing photoresistor owner preserves its historical positional CLI and
legacy `-V` publication. Additive Phase 09 behavior provides exact finite
protocol parsing, bounded serial shutdown, stable device-by-id calibration,
and typed physical `CostBreakdown` publication with:

```text
raw_sensor_value = +V
raw_cost = -V
source_mode = physical
source_score = unavailable unless calibrated and explicitly enabled
```

The selected graph uses wheel/IMU-backed `/odom` as the sole algorithm pose
for every controller, supervisor, PDE/history, fill, and escape consumer and
records/heartbeat-gates `/imu`. Vicon is required for accepted selected-trial
evaluation evidence only, on
`/gesc_gaussian/evaluation/vicon_pose` (`PoseStamped`) and
`/gesc_gaussian/evaluation/vicon_status` (`String`). It is not remapped or
copied into `/odom`, and it cannot influence motion, fill placement, ranking,
or stopping. Missing, stale, occluded, wrong-identity, session-changing, or
nonadvancing Vicon evidence prevents an evidence-complete run.

The sole Phase 05 recorder sets and verifies
`use_sim_time=false` on the shared owners before readiness, then rechecks the
resolved parameter snapshot. Missing, invalid, regressed, nonfinite, or stale
physical heartbeats revoke readiness, publish stop, and preserve final-zero and
bag-completeness validation.

The selected controller speed ceilings are `0.05 m/s` and `0.30 rad/s`. These
are configuration limits, not motion authorization.

## Shipped templates are intentionally inert

The calibration template contains no physical measurement or artifact hash and
has:

```text
status: uncalibrated
motion_ready: false
serial_device: null
```

The selected audit profile exactly freezes the cumulative v8.12 overrides and
also has `motion_ready: false`. Primary and secondary metadata contain only
evaluation geometry, null lamp settings/responses, `operator: UNASSIGNED`,
uncalibrated state, and nine false live-readiness fields.

Both primary and secondary wrapper preflights stop with exit `2` before the
character-device check, run-directory creation, `record_run`, or ROS launch.
Future commissioning starts by creating mutable calibration and
primary/secondary metadata copies under
`${XDG_CONFIG_HOME:-$HOME/.config}/dsim-lab/phase09`; installed inert templates
and the frozen selected profile remain unchanged. Future motion requires those
reviewed copies to contain
calibration, assigned operator and observer, measured response, Vicon identity,
live transfer, stationary graph, emergency stop, field, and explicit
authorization evidence as applicable. The stationary preflight runs while
calibration is still uncalibrated and readiness stays false; its retained
metadata bytes must be hash-coupled to a later explicit approval rather than
self-certifying the gate.

Physical arrival remains manual operator `Ctrl+C`; there is no coordinate or
proximity termination in the controller graph.

## Validation summary

Clean M6 root:

```text
/tmp/phase09_static_qual.vwhzo9
```

Results:

| Gate | Result |
|---|---:|
| isolated three-package build | PASS, `13.3 s` |
| Phase 09 installed-overlay tests | `76 passed` |
| shared-core regressions | `272 passed` |
| compatible observability | `13 passed, 2 deselected` |
| inherited recording | `70 passed, 1 skipped` |
| repository legacy behavior | `34 passed` |
| Bash syntax | `27 passed` |
| unique installed wrapper launches via `--show-args` | `6 passed` |
| typed interfaces via `ros2 interface show` | `6 passed` |
| critical Python error lint | PASS |
| XML/YAML/compile/diff/manifest/generated-root gates | PASS |

The skipped test is the opt-in visible Gazebo recording smoke and was not run
under the no-hardware boundary. Failed diagnostic attempts and their clean
retries are recorded in the live status and static qualification report.

An extra broad style probe remains `FAIL` with 917 host-plugin findings,
primarily 873 single-quote preferences. It is not a declared Phase 09 gate and
is not relabeled. Compilation, critical lint, build, and all declared tests
pass; exact logs are retained in the M6 root.

## Historical M7 snapshot scope and recovery

```text
before: 306 regular files, 389 inventory entries
after:  339 regular files, 425 inventory entries
delta:  33 new + 18 modified = 51 paths
transfer manifest: exactly the same 51 paths
```

Evidence:

```text
M0 backup SHA-256:
  8109c5c47789ce1d2bb2cf69ba82f6901b054193989c488fefcfb9cf507404b8
after inventory SHA-256:
  ebb8534a8298092e813c54966e68069ec039a40e40d6cd5fb354633679257744
after regular-file manifest SHA-256:
  af470b19b3aae91518e45fd093dcbe6874f67cccdd4ca6cf26213659c865afe4
snapshot patch SHA-256:
  8d56261f6857ff0f6f1bd83021202d32a3a13a0242fa7a9cb5011153b4393d1b
```

A fresh archive extraction accepted the 51-file patch and matched every after
hash. Git patches encode only executable/non-executable state, so the after
inventory was then applied as the authoritative full-mode manifest; the entire
after inventory matched. Reverse application plus the before mode inventory
recreated every M0 hash and inventory entry. Temporary staging/proof roots were
removed. The real snapshot was never used as a patch target.

The first patch attempt omitted 33 untracked new files because plain `git diff`
does not include them. It stopped on missing after files. The final patch uses
intent-to-add for all transfer paths and contains exactly 51 files. Reverse
application warns while restoring four inherited baseline whitespace lines;
that is expected byte preservation, not a forward patch defect.

## Historical M7 durable evidence

- Phase 09 Plan and live status;
- M0 backup receipt, before inventory, and before hashes;
- classified shared-source and transfer manifests;
- shared-lab compatibility report;
- M6 static qualification report;
- after inventory and hashes;
- 51-file reviewable snapshot patch;
- future Pi transfer/rollback procedure; and
- Phase 09 checkpoint and this handoff.

The snapshot is not a Git repository. These Git-side artifacts describe and
recover it; no snapshot file is described as committed.

## Historical M8A source transfer and deferred gates

M8A live-Pi comparison, rollback backup, scoped transfer, and host-side static
qualification completed under explicit user authorization. This statement is
historical and does not claim the later M8B source synchronization. The on-Pi
build, installed-overlay checks, and motion-blocked wrapper preflight are
`NOT RUN`. M9 stationary hardware checks, calibration, emergency-stop
rehearsal, and any selected motion trial are `NOT RUN`.

The exact live-Pi receipt and rollback boundary are in
`docs/codex/gesc_gaussian/validation/phase_09_pi_transfer_receipt.md`. The first
future commissioning action remains the separately authorized, no-launch
on-Pi build/installed-static gate after the current M8B transfer receipt is
complete. It does not authorize serial access, a physical graph, calibration,
or motion.

## Git state and commit boundary

Repository base during Phase 09 remained branch
`feature/gesc-gaussian-robustness-v1` at
`c04c222dfeac525197bf0542cbde64f1421dc664`, ahead of origin with the user's
pre-existing Phase 09 implementation-package edits preserved. On 2026-07-31,
the user authorized bounded Phase 09 closeout and receipt commits so the
repository could return to a clean worktree. The exact closeout commit is
recorded in the post-commit receipt in `phase_09_status.md`. No push is
authorized by that cleanup request.

## M7.1 final operator handoff

Verified: `2026-08-01T05:00:08Z`

The M7.1 amendment supersedes the current-snapshot M6 counts and M7 recovery
digests above while preserving them as historical evidence. The final selected
manual entry point is:

```text
~/ros2_ws/src/turtlebot3_vehicle_nodes/bash_scripts/
  light_esc_experiments/voltage_cost_values/
  gesc_gaussian_two_source_voltage.bash
```

After the exact M8B/M9 gates below have each been separately authorized and
completed, the eventual normal primary command is the bare wrapper:

```bash
~/ros2_ws/src/turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values/gesc_gaussian_two_source_voltage.bash
```

The bare command selects the primary scenario and its reviewed stable serial
device from the site calibration. It still requires the assigned operator and
observer to review the displayed conditions and type `RUN`; there is no
noninteractive motion bypass. Use `--scenario secondary` only for a separately
reviewed later secondary trial, and use explicit path overrides only when their
provenance is intentionally reviewed. The default run root is:

```text
~/Experiments/GESC-Gaussian/runs/phase09_physical
```

The shipped calibration/profile/metadata inputs are intentionally
motion-blocking, so the example is not currently a motion-ready command.

### What one accepted run records

The wrapper launches `gesc_gaussian_two_source.launch.xml` only through the
existing managed `ros_esc record_run`. It prints the unique run directory at
startup and completion, creates one sqlite3 rosbag, and retains the legacy raw
cost, augmented cost, filter, command, `/cmd_vel`, `/odom`, timekeeper, and
encoder streams. The same bag adds typed source/cost breakdown, GESC/control
diagnostics, algorithm state/events, Gaussian fills, readiness, `/imu`, the
declared GESC/Gaussian support streams, and both required evaluation-only Vicon
pose/status streams.

The terminal receives the managed child output plus a bounded one-second
summary of readiness, voltage/raw cost, cost components, filter output,
algorithm state/fill/failsafe, wheel/IMU odometry, clearly labeled Vicon
evaluation pose/status, final `vx`/`wz`, and maximum data age. The tee is
asynchronous and bounded: `console.log` is written first, so a slow or failed
display cannot block callback processing or authoritative capture. On shutdown
the terminal also reports completeness PASS/FAIL, the first bounded set of
failures, and the run directory.

The unique run directory additionally retains metadata, resolved topics and
parameters, notes, console output, `completeness.json`, Git or explicit
non-Git provenance, and validated SHA-256 copies of every file-backed input in
`configuration/manifest.yaml`. This includes calibration, profile, scenario,
used controller/filter/rotation configs, their immutable templates, selected
wrapper/launch, topic manifest, and QoS contract. The validator recomputes the
hashes. No legacy CSV collector, `ros2 topic echo`, or second recorder is
started; the sqlite3 bag and retained run files are authoritative.

### Final static evidence

| Gate | M7.1 result |
|---|---:|
| isolated three-package build | PASS, `13.1 s` |
| Phase 09 focused qualification | `93 passed` |
| shared-core regressions | `272 passed` |
| inherited recording | `70 passed, 1 skipped` |
| compatible observability | `13 passed, 2 deselected` |
| repository legacy behavior | `34 passed` |
| installed wrapper launch descriptions | `6 passed` |
| legacy selection hashes | `26` wrappers + `8` launches + `6` configs PASS |
| independent algorithm/wrapper/recorder reviews | no unresolved defect found |

The regenerated current-snapshot receipts are:

```text
after regular-file manifest:
  3bca5cf1845311a2cedc40081f055f1bb51333184a195488f823c130fee33373
after inventory/modes:
  522a1440de034c1538181db9792214432c237d162b323ba065542da582c7f37c
51-path patch:
  c92d0f96578ca28883b8c173f05411ca1a4b8d6e68cccd4e4f6b1ae667066723
51-path transfer manifest:
  5f60d69adc5d0feb87cb2fa2dd7c16cdc3bab846d3ec84fee181cb1dce9661f5
```

Fresh forward reconstruction reproduces `339` hashes and `425` inventory
entries; reverse reconstruction reproduces `306` M0 hashes and `389` baseline
entries. At that M7.1 boundary, M8 and M9 remained `NOT RUN`. The M8A addendum
below supersedes only the source-comparison/transfer portion; this is still not
`PHYSICAL READY`.

## M8A live-Pi transfer addendum

Verified: `2026-08-01T23:21:44Z`

The physical Pi source matched the complete sealed M0 baseline before write:
`306/306` hashes and `389/389` type/mode/size entries passed. The 51 transfer
paths classified cleanly as 18 expected replacements and 33 absent additions,
with zero overlap. All 40 historical operator-selection assets also matched.

The verified rollback root is:

```text
/home/mattb/tb3-pi/phase09_backups/20260801T230325Z
```

Its 25-entry manifest hash is
`17859e95c590c78abc8fb015229d825ae7f10d167d1ac86afb20d24e283f2561`.
The transfer used the exact 51-path manifest, no delete behavior, explicit
generated-file exclusions, and flags that avoided changing unrelated parent
directory times or ownership.

During the operator audit, the new wrapper was found to source but not build
the workspace. The user requires the manual Bash entry point to do both. A
bounded, commented correction now builds only `ros_esc_interfaces`, `ros_esc`,
and `turtlebot3_vehicle_nodes` before sourcing. Its test enforces that order,
and the physical README documents it. No legacy path changed.

Final results:

```text
snapshot and Pi hashes: 339/339 each PASS
snapshot and Pi inventory: 425/425 each PASS
final snapshot-to-Pi dry run: zero changes
legacy assets: 40/40 PASS
Bash syntax: 27/27 PASS
mounted-source Phase 09 tests: 93 passed in 28.34 s
```

The current resealed hashes are:

```text
after-file manifest:
  1d86d9ebceffbef49df06a53470f972f1897fc7488fd0fa315abd2a47004cd36
after inventory:
  8eacf7b7f36cd67979688cf168ae5fd3c4e8274ebdffa149e76b12c737c647ee
51-path patch:
  8985b4b2f5a33383a9abe4b6dc48a48a999c4da9dec5dfc24b88e9b324708939
```

The on-Pi build/source, installed launch checks, inert installed-wrapper
preflight, ROS graph, serial devices, calibration, emergency stop, and motion
remain unexecuted. The SSHFS mount was left mounted for the user.

## M8B evaluation-evidence and commissioning handoff

Current boundary on 2026-08-01: the M8B snapshot implementation, host-side
isolated build/regression qualification, and reviewed real-Pi source sync
passed. The verified rollback root is
`/home/mattb/tb3-pi/phase09_backups/20260802T031409Z_m8b`; snapshot and Pi
match `345/345` regular-file hashes and `432/432` inventory entries, with an
empty final scoped dry run. Reading and copying source files through SSHFS is
not an on-Pi build or live ROS test. No live Vicon subject/segment identity,
on-Pi build, installed graph, serial/GPIO path, calibration measurement,
emergency stop, mechanism, or base motion has been verified.

Final M8B host qualification and recovery receipts:

```text
fresh isolated three-package host build: PASS in 13.0 s
Phase 09 focused tests: 309 passed
shared core: 272 passed
inherited recording: 70 passed, 1 opt-in Gazebo smoke skipped
compatible observability: 13 passed, 2 simulation-only cases deselected
repository legacy behavior: 34 passed
legacy operator selection: 40/40 M0-identical
expanded legacy configurations: 68/68 M0-identical

snapshot delta: 39 new + 18 modified + 0 deleted = 57 paths
transfer manifest:
  f015285fa8b618f985d7257ac1471fe02c61e4ba17bc4701457ba36411931ff6
345-row after-file manifest:
  97af95a46bc8161f83a6776d609eb2480c0af0584b09ac62d5d60b9f2f638053
432-row inventory:
  602c2c9fa1f31fa7bd29692a07127e65b72c8570b1dcb6273226367db38643d2
57-path recovery patch:
  6fd166368449f33cff85d5e1422a414199171b27d8420e9ea1364cb2f5090885
Pi backup archive:
  a88dab7d51832f634558af9f886767a82c19c60ae7ff9a4b1c38764444a6fdbc
Pi backup manifest:
  c2fc028ba28bfb4244e706256a7b84c08654a112398987be808ae331bd7cb459
```

Forward recovery matches all `345` final hashes and `432` entries; reverse
recovery matches all `306` M0 hashes and `389` entries. The actual M8B transfer
itemization exactly matched the reviewed 15-existing/6-new/no-delete dry run,
and both final scoped and full-source dry runs are empty.

M8B preserves the control/evaluation separation:

- wheel/IMU-backed `/odom` is the sole algorithm pose;
- Vicon is required selected-trial evaluation evidence only on
  `/gesc_gaussian/evaluation/vicon_pose` and
  `/gesc_gaussian/evaluation/vicon_status`;
- identity, session, advancing packet/Tracker frame, occlusion, freshness, and
  run-interval coverage are recorder/validator gates, never control inputs;
- one `record_run` sqlite3 bag and one run directory retain both odometry and
  Vicon streams, live diagnostics, immutable configuration copies/hashes, and
  shutdown/completeness evidence; and
- historical Vicon, rotation, launch, wrapper, and ESC selection paths remain
  byte-identical.

The next authorized session must follow this exact order and stop at the first
failure:

1. Run the separate bounded on-Pi build/source and installed-static gate. It is
   currently `NOT RUN`; do not start the graph or touch serial/actuators.
2. Create mutable calibration and primary/secondary metadata copies under
   `${XDG_CONFIG_HOME:-$HOME/.config}/dsim-lab/phase09` before any stationary
   preflight. Do not edit installed inert templates or the frozen selected
   profile.
3. While still uncalibrated and with readiness false, run
   `gesc_gaussian_two_source_voltage.bash --stationary-preflight`. It uses the
   passive selected-only timekeeper and must produce no base or rotating-frame
   actuation.
4. Review the retained offline `PASS`, then run
   `gesc_gaussian_two_source_voltage.bash --approve-stationary RUN_DIR
   --reviewer NAME`. The approval must consume the same site-metadata bytes and
   remain hash-coupled to that preflight.
5. Test the independent emergency stop, then run a separately authorized,
   mechanically safe nontranslating command/final-zero rehearsal.
6. Perform and retain the real stationary rotating-photoresistor calibration;
   freeze only measured response bands backed by the sqlite3 bag, calculation,
   resolved configuration, and SHA-256 evidence.
7. Run `gesc_gaussian_two_source_voltage.bash --check-only`. This audits the
   reviewed configuration but does not prove a live graph or motion safety.
8. For the primary selected two-source run, invoke the bare
   `gesc_gaussian_two_source_voltage.bash`, verify the assigned operator and
   observer plus every live prompt, and type `RUN` only when all are true.

For step 2, create only the three files the wrapper resolves from the site
directory. The no-clobber option protects any already commissioned copy:

```bash
phase09_site_dir="${XDG_CONFIG_HOME:-$HOME/.config}/dsim-lab/phase09"
phase09_template_dir="$HOME/ros2_ws/src/turtlebot3_vehicle_nodes/config_files/gesc_gaussian"
mkdir -p "$phase09_site_dir"
cp --no-clobber -- "$phase09_template_dir/phase09_photoresistor_calibration.yaml" "$phase09_site_dir/"
cp --no-clobber -- "$phase09_template_dir/phase09_primary_metadata.yaml" "$phase09_site_dir/"
cp --no-clobber -- "$phase09_template_dir/phase09_secondary_metadata.yaml" "$phase09_site_dir/"
```

The calibration copy may receive the reviewed stable serial/firmware fields
needed for preflight but must remain `uncalibrated` and `motion_ready: false`
until the later real calibration is accepted. Do not copy or edit the selected
profile; it remains the frozen installed audit input.

Only after a complete accepted primary run may the secondary scenario be
considered under a separately reviewed progression decision. At this handoff,
all eight future actions remain unexecuted and this repository must not be
described as `PHYSICAL READY`.

## M8C lab-SOP one-command handoff amendment — 2026-08-03

<!-- MBuck 2026-08-03: Supersede the M8B operator gate sequence without erasing its implementation and transfer history. -->

The M8B sequence immediately above is retained as historical evidence, but it
is no longer the current operator workflow. The user approved alignment with
the attached `DSIM - TurtleBot3 Vicon Setup.pdf` and the existing, unchanged
Windows `vicon-tracker-server.py`.

The current human-operated lab sequence is:

1. Follow the lab SOP to prepare Vicon Tracker and the room. On the Windows
   Vicon computer, run the unchanged `vicon-tracker-server.py` and leave its
   console visible.
2. SSH to the Pi and run the bare selected wrapper:

   ```bash
   cd ~/ros2_ws/src/turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values
   ./gesc_gaussian_two_source_voltage.bash
   ```

3. Keep the robot in view on a clear floor. Watch the wrapper's run-directory
   announcement and live one-second diagnostics.
4. Press `Ctrl+C` in the robot terminal to end the run. Wait for the managed
   final-zero dwell, rosbag/metadata finalization, bounded validation, and final
   run-directory report before stopping the Windows server.

The wrapper itself owns the selected three-package build/source sequence and
starts `pigpiod` only if it is absent. There is no separate build command,
stationary preflight, site-configuration copy, calibration approval,
`--check-only`, typed `RUN`, Vicon subject/segment entry, server-script SHA-256,
handoff authorization, or readiness tag in this operator path.

Control/evaluation separation remains mandatory:

- wheel/IMU-backed `/odom` is the sole pose used by the GESC/Gaussian
  algorithm;
- the existing legacy `7f` Vicon transport feeds passive evaluation
  `nav_msgs/msg/Odometry` on `/gesc_gaussian/evaluation/vicon_odom` only; and
- missing or stale Vicon is reported live and makes evaluation evidence
  incomplete, but it never gates, stops, or changes robot motion.

The recorder remains the sole selected-run bag/finalization owner. It must keep
the existing legacy streams plus typed GESC/Gaussian diagnostics and the
evaluation-only Vicon odometry in the same sqlite3 bag, with live terminal
diagnostics, final readiness false/final zero, zero dwell, integrity checks, and
the retained run directory.

M8C implementation, host validation, recovery reseal, and reviewed live-Pi
source transfer are complete. The exact results are:

```text
isolated host build: 3/3 packages PASS in 12.6 s
focused M8C tests: 196 passed
ros_esc functional tests: 153 passed, 3 deselected
vehicle-node functional tests: 71 passed, 3 deselected
Bash syntax: 27/27 PASS
structured parsing: 9 changed Python + 9 XML + 7 YAML + 68 JSON PASS
selected wrapper --check-only: PASS; 3 packages rebuilt in 12.6 s
selected launch --show-args: PASS
snapshot/Pi hashes: 342/342 PASS
snapshot/Pi inventory: 430/430 PASS
final checksum dry run: empty
```

Snapshot recovery artifacts are under
`/home/mattb/physical_TB3_files_snapshot/phase09_backups/20260804T003650Z_m8c_pre_simplification`
and
`/home/mattb/physical_TB3_files_snapshot/phase09_backups/20260804T010757Z_m8c_post_simplification`.
The current Pi rollback is
`/home/mattb/tb3-pi/phase09_backups/20260804T011049Z_m8c_pre_simplification`.

No on-Pi build, ROS graph, serial/GPIO access, Vicon connection, lamp
experiment, actuator command, or robot motion was performed by Codex. The next
step is the four-step human-operated lab sequence above; it requires no extra
Phase 09 authorization file, readiness tag, subject/segment input, or hash key.
The first physical runs remain exploratory selected two-source tests of the
cumulative terminal v8.12 algorithm, not broad physical-robustness claims.
