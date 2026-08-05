# Phase 09 Handoff — Physical Source Integration and Lab-SOP Entry

Date: `2026-08-04` (`America/Los_Angeles`)

Current outcome: `M8E CLEAN ON-PI CHECK-ONLY, INSTALLED-SOURCE PARITY, REAL-PI SOURCE PARITY, AND LAB WALL-CLOCK INITIALIZATION PASS FOR CURRENT BOOT`

The current human operator follows the attached lab Vicon SOP and invokes bare
`gesc_gaussian_two_source_voltage.bash`; no repository readiness tag,
authorization file, typed confirmation, site copy, calibration approval,
subject/segment value, or hash key is required. M8D retains that M8C operator
contract and adds automatic familiar CSV export after bag finalization. M8E
repairs the real-Pi build/underlay/install path and adds a selected-only
no-lidar base bringup without changing algorithm source or historical launch
behavior. The operator's strengthened on-Pi `--check-only` passed a clean
three-package build, installed-source parity, device separation, and launch
construction. Final snapshot/Pi parity is `345/345` regular files and
`433/433` inventory entries. No serial device, live Vicon connection, ROS
graph, recorder, actuator, rotating frame, lamp trial, or robot motion was
started. Nick's literal wall-clock `sudo date -s` initialization passed at
`2026-08-04T17:54:22+00:00` for the current powered session and must be
repeated after each Pi reboot.

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

## M8D familiar runtime CSV handoff amendment — 2026-08-03

<!-- MBuck 2026-08-03: Preserve one authoritative bag while restoring familiar CSV-shaped run artifacts for the selected experiment. -->

M8D answers the final operator-data requirement without changing the launch
graph: after the existing recorder finalizes the selected run's sole sqlite3
rosbag, its existing `validate_run` owner atomically and idempotently derives
the familiar headerless CSV files in that same reported run root. There is no
live CSV collector, second recorder, parallel logging process, or modification
to a historical ESC wrapper.

The retained run directory now has this output contract:

| Artifact | Meaning |
|---|---|
| `encoder.csv` | `encoder` alias as `[timestamp, angle]` |
| `cost_value.csv` | augmented `/cost_modified` as `[timestamp, augmented_cost]` |
| `filter_value.csv` | timestamp plus exactly two legacy filter values |
| `control_value.csv` | timestamp plus exactly six final-command values |
| `odometry.csv` | evaluation-only Vicon in legacy xyz/quaternion columns |
| `raw_cost_value.csv` | raw physical objective with `raw_cost = -voltage` |
| `algorithm_odometry.csv` | the algorithm's `/odom` pose, separate from Vicon |
| `legacy_csv_manifest.json` | aliases/topics, semantics, rows, sizes, hashes, and bounded errors |

Write-enabled final validation requires all required CSV views to be complete;
an incomplete export is retained and reported as a completeness failure. Dry
validation remains non-mutating and warns that it skipped export. Revalidation
replaces each derived file instead of appending duplicate rows. The columns are
compatible with the legacy low-level plotting reader, but the older one-level
`Test_*` directory browser does not automatically discover the selected
wrapper's nested date/run hierarchy; give the retained run directory directly
to the lower-level reader.

Implementation scope was exactly:

```text
modified  ros_esc/ros_esc/experiment_recording/validate_run.py
modified  ros_esc/test/test_phase09_physical_recording.py
new       ros_esc/ros_esc/experiment_recording/legacy_csv_export.py
```

The pre-transfer snapshot and Pi recovery roots are, respectively:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/20260804T023735Z_m8d_legacy_csv_export
/home/mattb/tb3-pi/phase09_backups/20260804T023735Z_m8d_legacy_csv_export
```

The verified post-change snapshot seal is
`/home/mattb/physical_TB3_files_snapshot/phase09_backups/20260804T030145Z_m8d_post_legacy_csv_export`;
its source manifest, inventory, and archive SHA-256 values are respectively
`49f969c72021242f25eaa4b2b87993904a9c0a5decd79278385d1d35bcf5b9af`,
`88b84d44dd478a09da610f75f9caf98619b71d5017f2f3d5a123cbd8f18a5bf7`,
and `e713a243daa6c5e687494798fd0ed76096d5000904108716bf2106f22c95a23c`.

The scoped no-delete SSHFS transfer finished with `343/343` full-tree regular
file hashes and `431/431` type/mode/size entries matching, with no source cache
files or symlinks. Qualification results were:

```text
source five-file Phase 09 regression: 209 passed
isolated selected-package build: 3 packages finished in 12.6 s
installed-overlay five-file Phase 09 regression: 209 passed
ros_esc functional regression: 159 passed (3 inherited style tests excluded)
vehicle functional regression: 71 passed (3 inherited style tests excluded)
mounted-source recording regression: 131 passed
mounted-source remaining Phase 09 regression: 78 passed
```

The first shell attempt set `-u` before ROS setup and stopped because
`AMENT_TRACE_SETUP_FILES` was unset; sourcing ROS first and then enabling
`set -u` passed. No source defect or behavior failure was involved.

No on-Pi build/source, ROS graph, live Vicon connection, calibration, safety
rehearsal, serial/GPIO access, lamp response, actuator command, or robot motion
was performed for M8D. The next action remains the M8C human-operated lab SOP
and bare wrapper. On shutdown, wait for the final-zero dwell, bag finalization,
validation, and automatic CSV export before taking the reported run directory
for analysis.

## M8E real-Pi runtime-repair handoff — 2026-08-04

M8E supersedes the M8D statement that no on-Pi build had run. The operator has
now completed the bounded, nonlaunching `--check-only`; no experiment graph or
motion has run.

The retained first bare attempt failed before readiness because the wrapper did
not source the established `/home/pi/turtlebot3_ws` underlay and the selected
install contained stale Python. It also exposed an absent historical sound
profile source module and a potential LDS-02/photoresistor `/dev/ttyUSB0`
collision. The recorder retained the failed run and shut down with readiness
false; there was no robot command or motion.

The accepted repair:

- restores the lab TurtleBot3 underlay before the selected build;
- forces the three selected packages through `--symlink-install`;
- verifies installed Python/source parity and both launch descriptions before
  any recorder or hardware access;
- verifies `/dev/ttyUSB0` photoresistor and `/dev/ttyACM0` OpenCR are distinct;
- starts only OpenCR, wheel/IMU `/odom`, and the standard state publisher in a
  new selected-only base helper because this open-field algorithm has no scan
  consumer; and
- restores the exact historical sound-profile module so clean rebuilds retain
  all pre-existing console entry points.

No `ros_esc` algorithm source changed. Existing wrapper/launch/config hashes
remain protected by the Phase 09 compatibility suite. Recovery roots are:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/20260804T224607Z_m8e_runtime_repair
/home/mattb/tb3-pi/phase09_backups/20260804T224607Z_m8e_runtime_repair
```

The successful Pi output was:

```text
3 selected packages finished in 1 min 39 s
installed Python parity PASS: ros_esc=63, turtlebot3_vehicle_nodes=21
turtlebot3_bringup: established ~/turtlebot3_ws source underlay
model: burger
photoresistor: /dev/ttyUSB0
OpenCR: /dev/ttyACM0
selected lidar: disabled
launch construction: PASS
pigpio/serial/Vicon/ROS graph/recorder/motion: NOT STARTED
```

Following the earlier low-battery power cycle, the remounted Pi retained all
three successful build return codes and exact `345/345` source hashes plus
`433/433` inventory entries. The final strengthened check-only output was
captured after the Pi was back online. The final verified source seal is:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260804T234034Z_m8e_post_runtime_repair
```

with source-manifest, inventory, and archive SHA-256 values:

```text
5469c772d0649d42cee3581d207d19a29a16d6df1f13d30620e1a10ce301c66d
3775454cb80812501495c4315b6ce696302960d580ba7750d550be3a9bfb6fd2
2a2b81cef6e1156890191e0667795c9ddfbca111cffa5e9d88fc2a9e3bdb659a
```

See
`docs/codex/gesc_gaussian/validation/phase_09_pi_runtime_repair.md` for commands,
failed-attempt diagnosis, host results, Pi output, and rollback details.

The Pi has no RTC and cannot reach internet NTP through the isolated
DSIMOVERWATCH router. After reboot it returned to a stale June 2025 clock,
confirming why Nick's package README requires `sudo date -s` before experiments.
An initial Unix-epoch copy produced August 5 UTC while the lab was still on the
evening of August 4; no run started under that superseded setup. Nick's README
and both legacy collectors establish literal local-wall-time entry. The Linux
tower reported `2026-08-04 17:54:22 PDT -0700`, and the corrected Pi reported
`2026-08-04T17:54:22+00:00`. No timezone or NTP setting changed. The Pi's
`+00:00` and recorder `Z` labels reflect the historical lab clock convention,
not an external true-UTC synchronization claim.

The current powered session is ready for the ordinary M8C SOP and bare wrapper.
If the Pi reboots first, repeat the literal wall-clock date step before starting
ROS; do not copy a Unix epoch or timezone/offset. The successful check-only need
not be repeated for every experiment. Keep the floor clear and `Ctrl+C`
available, then wait through managed final zero, bag finalization, validation,
and M8D CSV export before collecting the run.

## M8F first physical-run repair handoff — 2026-08-04

The first bare selected run did not execute the algorithm. Controller and
filter rejected the selected ROS parameter tail, both exited code 2,
recording readiness remained false, `/cmd_vel` remained empty, and the
recorder retained a correctly failed 3,187-message run at
`20260804T201250796597Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_6d9b4ac3`.
Do not delete or relabel it.

M8F replaces the incompatible tail with native strict parser options while
preserving legacy `use_sim_time=True` as the default and selecting wall time
only for Phase 09. It also makes filter, rotation, photoresistor, and Vicon
client teardown context-safe. This changes neither the cumulative v8.12
algorithm nor any historical ESC wrapper/launch. `/odom` remains the only
algorithm pose; Vicon remains required evaluation evidence only. The Windows
server and its seven-float UDP protocol are unchanged.

Host qualification passed 238 complete Phase 09 physical tests, 37 canonical
legacy tests, critical lint/static checks, launch and node construction, and a
fresh 12.5-second three-package isolated build. Eleven unique reviewed files
were copied through SSHFS with no delete behavior. Snapshot/Pi parity is
345/345 files and 0/0 symlinks. Matching rollback roots are:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/20260804T202726-0700_m8f_runtime_graph_repair
/home/mattb/tb3-pi/phase09_backups/20260804T202726-0700_m8f_runtime_graph_repair
```

The operator subsequently completed the one-time on-Pi rebuild/check from the
standalone Linux SSH terminal:

```text
three selected packages: PASS in 14.4 s
installed Python parity: PASS (ros_esc=63, turtlebot3_vehicle_nodes=21)
selected CLI parser: PASS (physical=False, legacy default=True)
launch construction: PASS
devices/model/lidar: /dev/ttyUSB0, /dev/ttyACM0, burger, selected lidar off
pigpio/serial/Vicon/ROS graph/recorder/motion: NOT STARTED
```

All three live `colcon_build.rc` files are zero. The M8F rebuild/parser gate is
closed. If the Pi has not rebooted and source has not changed, the next action
is the established Vicon/lab SOP followed by the bare selected wrapper from the
standalone SSH terminal. No repeated check-only or separate build command is
required. A real run must still prove live sensor, `/odom`/IMU, Vicon evidence,
command/motion, managed final zero, bag validation, CSV export, and two-light
behavior. No ROS graph, serial device, Vicon client, recorder, actuator, or
motion was started by Codex for M8F. Full evidence is in
`docs/codex/gesc_gaussian/validation/phase_09_first_physical_run_repair.md`.

## M8G second physical-run repair handoff — 2026-08-04

The second bare selected run passed the M8F parser/cleanup boundary but did not
execute the algorithm. OpenCR, onboard `/odom`/IMU, encoder, evaluation-only
Vicon, rosbag, zero-command ownership, and clean shutdown were operational.
The selected supervisor changed from `SEARCH` to `FAILSAFE` after its 5-second
startup grace, before recorder preflight could authorize sensor rotation.
Readiness remained false, all 1,202 `/cmd_vel` messages were zero, Timekeeper
and source cost remained absent, and no robot motion occurred. Preserve the
failed run `20260804T205606472031Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_d4f0178d`.

M8G changes only `gesc_gaussian_two_source_voltage.bash` and its focused test.
It explicitly retains the recorder's 45-second passive and 45-second rotation
startup bounds while passing a selected-only 100-second startup grace through
the existing launch argument to both controller and supervisor. Recorder
readiness, lifecycle, nonzero-command, rotation, heartbeat, final-zero, and
completeness gates are unchanged. The launch and shared node defaults remain
5 seconds; all historical ESC entry points and algorithm code remain
unchanged.

Host/source qualification passed 23 focused tests, 239 complete Phase 09
tests, 37 canonical legacy tests, all 27 Bash syntax checks, all nine XML
parses, critical lint, and a fresh 15.2-second three-package build. Matching
snapshot/Pi backups and receipts are under
`20260804T210435-0700_m8g_startup_grace_repair`. The two-file SSHFS transfer
finished with 345/345 regular-file and 433/433 inventory parity and zero source
caches/symlinks. Codex started no Pi build, ROS graph, device, recorder, or
motion.

The operator subsequently completed the required post-M8G check-only. All
three packages passed in 16.3 seconds; installed Python parity, selected
physical `False`, legacy-default `True`, device separation, and launch
construction passed; no runtime or hardware started. Read-only SSHFS inspection
confirmed all three build return codes zero, the installed wrapper symlink
chain targeting repaired source, and exact post-cleanup 345/345 file plus
433/433 inventory parity.

The one-time M8G rebuild/check gate is closed. If the Pi has not rebooted and
source has not changed, the next human action is the ordinary Vicon/lab SOP and
bare `./gesc_gaussian_two_source_voltage.bash` from the standalone SSH terminal.
Do not repeat check-only or add a permanent ceremony. Full diagnosis,
qualification, hashes, rollback, operator evidence, and remaining live checks
are in
`docs/codex/gesc_gaussian/validation/phase_09_second_physical_run_repair.md`.

## M8H third physical-run clock repair handoff — 2026-08-04

The third bare selected run reached OpenCR, wheel/IMU `/odom`, encoder,
evaluation-only Vicon, the selected supervisor, rosbag, and zero-command
ownership, but it did not reach readiness or execute the algorithm. Recorder
physical-clock enforcement changed Gaussian fill's internally forced
`use_sim_time=True` to `False` while its multithreaded executor owned the
`/clock` waitable, producing rclpy `InvalidHandle`. All 815 recorded
`/cmd_vel` messages were zero, all readiness and rotation-authorization
samples were false, and no rotation command or robot motion occurred. Preserve
run
`20260804T212226731572Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_309b9e71`
exactly as failed evidence.

M8H adds one shared startup-only clock helper and uses it in exactly modified
cost, both PDE histories, convergence detector, and Gaussian fill. With no ROS
startup override it retains the historical Gazebo `True`; an explicit physical
`False` and explicit simulation `True` are preserved from construction. The
two-thread Gaussian executor, numerical algorithm and v8.12 tuning, interfaces,
cost semantics, `/odom`-only algorithm pose, evaluation-only Vicon, recorder
gates, selected entry point, and every historical ESC wrapper/launch remain
unchanged.

Host qualification passed 16 focused clock tests, 114 shared/legacy/clock
regressions, 45 snapshot clock/parity tests, 256 complete snapshot Phase 09
tests, critical syntax/lint, two isolated three-package builds, and a real
installed Gaussian-fill two-thread physical-clock probe. The probe retained
`False` through construction and three parameter-enforcement calls without
`InvalidHandle` or traceback.

Matching pre-edit recovery roots are:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260804T214018-0700_m8h_clock_initialization_repair
/home/mattb/tb3-pi/phase09_backups/
  20260804T214018-0700_m8h_clock_initialization_repair
```

The reviewed eight-path SSHFS transfer used no broad sync or source deletion.
After the Pi battery swap, reboot, and remount, fresh manifests proved 347/347
regular-file hashes and 435/435 type/mode/size entries, with source-manifest
SHA-256
`87bfed392f98ad6cecca05c296fc2600c355821f2907e55e521ec00d6989fd6a`
and inventory SHA-256
`55b2b88117506164cf339696c74f1fe4a571bf1b8ad7cefc62b29cdb36b1ebbb`.
Generated Python/pytest caches were cleaned from both source roots; final cache
counts are zero. The matching post-transfer receipt hash is
`6ae98289e19c2a066a8f61005e16e01b3dc9d4b0a97d8201d29caa6933dc453c`.

Codex ran no Pi command, build, ROS graph, serial/GPIO operation, Vicon client,
recorder, actuator, or motion for M8H. Because source changed and the Pi
rebooted, the next action is one human-operated
`./gesc_gaussian_two_source_voltage.bash --check-only` after restoring Nick's
literal lab wall clock. Review its three-package build, installed parity,
selected physical `False`, legacy default `True`, device separation, and
launch-construction result before another bare experiment. The physical
algorithm, motion, shutdown, rosbag validation, CSV export, and two-light
behavior are still unverified. Full evidence is in
`docs/codex/gesc_gaussian/validation/phase_09_third_physical_run_repair.md`.

The operator subsequently completed the one required post-M8H check-only from
the standalone SSH terminal. All three packages passed in 16.4 seconds;
installed Python parity passed with `ros_esc=64` and
`turtlebot3_vehicle_nodes=21`; selected physical `False`, legacy-default
`True`, device separation, and launch construction passed; and no pigpio,
serial, Vicon, ROS graph, recorder, or motion started. Mounted read-only checks
confirmed zero build return codes, the helper on the active symlink-install
path, and retained 347/347 source plus 435/435 inventory parity. Eleven normal
Pi bytecode-cache directories were regenerated by the build and are excluded
from source parity.

The M8H installed gate is closed. Do not request another check-only unless
source changes or diagnosis requires it. The next human action is the ordinary
Vicon/lab SOP and bare `./gesc_gaussian_two_source_voltage.bash`; retain and
validate its output regardless of success or failure. Physical algorithm
behavior remains unverified until that run completes.
