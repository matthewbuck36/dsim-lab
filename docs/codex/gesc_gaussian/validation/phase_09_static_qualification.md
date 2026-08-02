# Phase 09 Host Static/Offline Qualification

Date: `2026-07-31` (`America/Los_Angeles`)

Result: `PASS — SNAPSHOT STATIC INTEGRATION; HARDWARE DEFERRED`

This report covers the declared Phase 09 M6 host-only gates. It does not cover
the live Pi, serial devices, sensors, TurtleBot/OpenCR, motors, rotating frame,
lamps, floor motion, or physical emergency stop.

## Qualification root

All generated build, install, log, bytecode, and verbose evidence stayed under:

```text
/tmp/phase09_static_qual.vwhzo9
```

The snapshot source tree contains no `build`, `install`, `log`, `.git`,
`__pycache__`, or `.pytest_cache` directories and no symlinks.

## Preflight and syntax

| Gate | Result |
|---|---|
| `validate_phase_context.sh 09 implement` | PASS |
| Python `compileall` with bytecode redirected to qualification root | PASS |
| all snapshot launch XML parsed | 8 PASS |
| all Phase 09 YAML mappings parsed | 4 PASS |
| all Bash entry points checked with `bash -n` | 27 PASS |
| critical Python lint `E9,F63,F7,F82` | PASS |
| repository `git diff --check` | PASS |
| Phase 09-authored new-file newline/trailing-space check | 12 PASS |

The first attempt to apply newline/trailing-space policy to all transfer files
correctly exposed two inherited byte-identical cases: the intentionally empty
`gaussian_fill_node/__init__.py`, and existing trailing whitespace in the
shared `ros_esc_interfaces/CMakeLists.txt`. Those shared bytes must match
`dsim-lab`; they were not rewritten to satisfy a new cosmetic policy. The
final new-file hygiene gate passes.

## Isolated build and installed assets

Command shape:

```text
colcon --log-base QUAL/colcon_log build
  --base-paths /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src
  --build-base QUAL/build
  --install-base QUAL/install
  --packages-select ros_esc_interfaces ros_esc turtlebot3_vehicle_nodes
```

Result:

```text
ros_esc_interfaces       PASS
ros_esc                  PASS
turtlebot3_vehicle_nodes PASS
3 packages finished in 13.3 s
```

Installed source/share comparisons pass for the restored legacy launch, new
Phase 09 launch, all four Phase 09 YAML files, selected wrapper, and all three
Phase 05 recorder assets. Installed executable discovery retains every original
physical package entry point and exposes the additive supervisor/recorder
entry points. `ros2 interface show` passes for all six ported typed messages.

Retained installed-evidence files:

```text
/tmp/phase09_static_qual.vwhzo9/ros_esc_executables.txt
/tmp/phase09_static_qual.vwhzo9/turtlebot3_vehicle_nodes_executables.txt
/tmp/phase09_static_qual.vwhzo9/interface_show.log
```

## Offline test results

Every invocation was bounded and used `-p no:cacheprovider`.

| Collection | Result |
|---|---:|
| Phase 09 shared parity, physical recording, adapter, launch/config/legacy-wrapper tests | `76 passed in 0.97 s` |
| shared state machine, supervisor, robust Gaussian, escape/recenter, deferred shutdown, search epoch, convergence | `272 passed in 7.72 s` |
| physical-compatible observability subset | `13 passed, 2 deselected in 2.05 s` |
| inherited Phase 05 recorder and integration tests | `70 passed, 1 skipped in 2.03 s` |
| repository legacy behavior in the repository overlay | `34 passed in 3.09 s` |

The recording skip is the opt-in visible Gazebo smoke selected only when
`DSIM_RUN_GAZEBO_RECORDING_TEST=1`; Gazebo was not started in this no-hardware
qualification.

The first observability command used node IDs rooted above pytest's selected
root, so the two deliberately excluded simulation cost-source-owner tests ran:
`13 passed, 2 failed`. Their failures were the known physical-overlay CLI/source
gap, and the second was contaminated by the first test's initialized global
rclpy context. A fresh process with the exact name-based exclusion produced the
valid `13 passed, 2 deselected` result above. The failed attempt is retained and
is not counted as a pass.

An earlier attempt to rerun repository `test_legacy_behavior.py` inside the
physical overlay failed during collection on the deliberately excluded
simulation `Multi_Light_Source_Cost`. The final `34 passed` result was run in
the proper repository overlay. This preserves the physical package boundary
rather than copying simulator cost owners into the robot workspace.

## Launch and shared-lab compatibility

Every unique installed launch named by a Bash entry point passes bounded
`ros2 launch ... --show-args`:

```text
acoustic_esc_experiment.launch.xml
light_esc_experiment.launch.xml
light_gesc_gaussian_fill_experiment.launch.xml
light_hbesc_gaussian_fill_experiment.launch.xml
gesc_gaussian_two_source.launch.xml
rotating_frame.launch.xml
```

The inherited acoustic wrapper spelling is accepted by `--show-args`, and its
requested `True` value is the unchanged declared default. Output is retained at:

```text
/tmp/phase09_static_qual.vwhzo9/show_args.log
```

The compatibility test freezes all 26 pre-existing Bash hashes and the old
GESC+Gaussian launch hash. The broader baseline check covers 40 legacy
selection assets: 26 wrappers, 8 launches, and 6 configurations. All remain
M0-identical. Only the new selected wrapper references the new Phase 09 launch;
the historical wrapper still references its untouched historical launch.

`--show-args` proves package discovery and launch construction, not ROS
parameter types or node execution. Host-safe constructors and pure helpers are
covered by the focused tests; Pi, serial, GPIO, OpenCR, servo, driver, and motor
nodes were not instantiated.

## Inert selected entry point

The installed selected wrapper was tested through a temporary workspace view
that linked only the qualification install and snapshot source. For both
`primary` and `secondary`, the shipped templates produced:

```text
exit code: 2
reason: Phase 09 inputs are motion-blocking
run directory created: no
character-device check reached: no
record_run/launch reached: no
```

Logs:

```text
/tmp/phase09_static_qual.vwhzo9/inert_primary_preflight.log
/tmp/phase09_static_qual.vwhzo9/inert_secondary_preflight.log
```

## Snapshot scope and recovery gates

The current snapshot has `339` regular files. Relative to the verified M0
manifest, it has `33` new files and `18` modified files, for exactly `51`
changed paths. The frozen transfer manifest also contains exactly those `51`
paths:

```text
unexpected changed paths: 0
declared but unmaterialized paths: 0
missing baseline paths: 0
```

The shared parity test passes for every declared interface/shared-runtime file.
The M0 backup was rehashed during M6 and still matches:

```text
8109c5c47789ce1d2bb2cf69ba82f6901b054193989c488fefcfb9cf507404b8
```

The reserved `/home/mattb/tb3-pi` directory is not a mountpoint. No `ros2
launch`, `ros2 run`, `ros2 bag`, Gazebo, or SSHFS process remained after the
checks.

## Exploratory broad style diagnostic

An additional broad `ament_flake8` probe was run on six Phase 09 Python/test
files even though it is not a declared Phase 09 acceptance gate. It returned
`rc=1` with `917` style findings after the final EOF hygiene correction:

```text
Q000 quote preference: 873
E501 79-column length: 26
D202 docstring spacing: 14
I100/I101 import ordering: 4
```

This host plugin set enforces a quote/docstring/79-column policy beyond the
declared compile, critical-error lint, and repository diff gates. The result is
retained at:

```text
/tmp/phase09_static_qual.vwhzo9/exploratory_broad_flake8.log
/tmp/phase09_static_qual.vwhzo9/exploratory_broad_flake8_errors.txt
```

It is not relabeled as a pass. It does not indicate a syntax/import/runtime
failure; the critical error-code selection and all declared build/tests pass.
No acceptance threshold was weakened to hide it.

## Hardware-deferred result

Live-Pi comparison/transfer (M8) and stationary/motion commissioning (M9) are
`NOT RUN`. This M6 result is not `PHYSICAL READY` and authorizes no hardware
action.

## M7.1 final operator-entry and recording qualification

Verified: `2026-08-01T05:00:08Z`

Result: `PASS — FINAL SNAPSHOT STATIC/OFFLINE QUALIFICATION; HARDWARE DEFERRED`

This is a fresh qualification of the M7.1 amendment, not a relabeling of the
historical M6 results above. Generated build, install, log, and bytecode output
was isolated under:

```text
/tmp/phase09_m71_final.bmS5g9
```

The three-package build completed in `13.1 s`. Tests were run in fresh
processes with bytecode/cache output kept outside the snapshot:

| Collection | Result |
|---|---:|
| Phase 09 parity, recording, adapter, wrapper, launch, configuration, and legacy guards | `93 passed in 1.72 s` |
| shared core/state-machine/Gaussian regressions | `272 passed in 8.20 s` |
| inherited Phase 05 recording regressions | `70 passed, 1 skipped in 2.88 s` |
| physical-compatible observability | `13 passed, 2 deselected in 2.36 s` |
| repository legacy behavior | `34 passed in 3.73 s` |

The inherited skip is the existing opt-in visible-Gazebo recording smoke; it
was not enabled for this no-hardware snapshot pass. One first legacy command
sourced a stale repository install and stopped during collection. The corrected
fresh source-owner invocation above passed all `34` tests; the environment
attempt is not represented as a behavior pass or failure.

Fresh installed-overlay checks proved:

- `gesc_gaussian_two_source_voltage.bash` and
  `gesc_gaussian_two_source.launch.xml` are installed;
- both superseded Phase 09-only names are absent;
- all six unique launch descriptions referenced by wrappers pass
  `ros2 launch ... --show-args`;
- all 27 wrappers pass `bash -n`, including guarded failures for each of the
  four valued options when its value is omitted;
- the installed selected wrapper's inert probe exits `2` at the deliberate
  motion-readiness gate, never reaches the ROS target, and leaves the count of
  its exact temporary-directory prefix at `0 -> 0`; and
- `record_run --help` exposes the additive evidence-file, terminal-streaming,
  and live-diagnostic options.

### Final algorithm and ownership audit

All 27 declared shared runtime/interface/config paths match the terminal
cumulative Phase 08 v8.12 source boundary byte-for-byte. The selected profile
enables the reviewed single-fill, counted two-source behavior and its opt-in
`interior_farthest` fallback at `0.50 m`; the shared and legacy defaults keep
that fallback disabled. Source cost remains `raw_cost = -voltage` in volts.
The selected graph retains one source-cost owner, one modified-cost/filter/
fill/supervisor/controller chain, one `/cmd_vel` owner, and one recorder. The
only controller changes relative to the shared algorithm are the reviewed
physical speed ceilings of `0.05 m/s` and `0.30 rad/s`.

Three independent final read-only reviews covered the algorithm/parity
boundary, wrapper/launch/Ctrl+C lifecycle, and recorder/validator/data path.
After the bounded terminal-queue and truncated-option corrections, none found
an unresolved defect. This is strong static/offline evidence; it is not a
claim that unrun hardware behavior is bug-free.

### Recording and live terminal contract

The selected wrapper invokes only `ros2 run ros_esc record_run`. Each accepted
run creates one unique run directory and one sqlite3 rosbag. The physical bag
retains the legacy raw and augmented costs, filter output, command array,
`/cmd_vel`, `/odom`, timekeeper, and encoder streams. It additionally retains
typed source/cost breakdown, GESC/control diagnostics, algorithm state/events,
Gaussian fills, recording readiness, `/imu`, and the declared optional
convergence, supervisor, bias, history, and transform streams. It does not
start the historical CSV collector, `ros2 topic echo`, or a second recorder.

The selected wrapper opts into a one-second passive terminal summary and an
asynchronous bounded terminal tee. The durable `console.log` write occurs
first; a slow or broken terminal cannot block ROS callback processing or child
output capture. The live summary reports readiness, voltage/raw cost, raw/
Gaussian/affine/augmented cost, filter output, algorithm state/fill/failsafe,
pose, final `vx`/`wz`, and maximum input age as data become available. The
sqlite3 bag and retained files remain authoritative even if display lines are
dropped under terminal saturation.

Each physical run validates, copies, and SHA-256 hashes the exact metadata,
calibration, selected profile, used controller/filter/rotation inputs,
selected wrapper/launch, topic manifest, and QoS contract under
`configuration/manifest.yaml`. The immutable controller/rotation templates
are retained as additional evidence. The validator recomputes those hashes
and fails completeness for missing, escaped, duplicate, or corrupted evidence.
Git provenance remains complete in a worktree; a source-only Pi workspace is
recorded explicitly as `git.available=false` instead of aborting before bag
startup. The run path is printed at startup and completion, followed by a
bounded PASS/FAIL completeness summary.

### M7.1 reseal and recovery proof

The snapshot still has exactly `339` regular files and `425` inventory entries,
with zero symlinks or generated roots. Its delta from M0 is exactly the frozen
transfer manifest: `33` new, `18` modified, `0` deleted, and no unexpected
path. The regenerated recovery receipts are:

```text
transfer manifest, 51 paths:
  5f60d69adc5d0feb87cb2fa2dd7c16cdc3bab846d3ec84fee181cb1dce9661f5
after regular-file manifest, 339 rows:
  3bca5cf1845311a2cedc40081f055f1bb51333184a195488f823c130fee33373
after inventory/modes, 425 rows:
  522a1440de034c1538181db9792214432c237d162b323ba065542da582c7f37c
Git-format snapshot patch, 51 paths and 21,950 lines:
  c92d0f96578ca28883b8c173f05411ca1a4b8d6e68cccd4e4f6b1ae667066723
```

A second fresh same-permissions M0 extraction accepted the patch. Applying the
after mode inventory reproduced all `339` hashes and all `425` inventory
entries. Reverse application plus the before mode inventory reproduced all
`306` M0 hashes and all `389` baseline inventory entries. The temporary patch
and proof roots were moved to Trash after verification; the real snapshot was
never a patch target.

The final authored-file `git diff --check` passes when the recovery patch and
inventory TSVs are excluded. Those generated artifacts deliberately preserve
historical source whitespace and an empty final symlink-target column; they
must not be normalized independently of the sealed recovery contract. A clean
post-commit worktree has no Git diff to check.

M8 live-Pi comparison/transfer and M9 stationary/motion commissioning remain
`NOT RUN`. Therefore M7.1 closes as a static snapshot pass, not `PHYSICAL
READY`, and authorizes no live-Pi, serial, actuator, lamp, or motion action.

## M8A transfer-time wrapper correction and mounted-source requalification

Verified: `2026-08-01T23:21:44Z`

The user required the manually invoked Phase 09 Bash file to build and source
its workspace. The M7.1 wrapper only verified and sourced a pre-existing
install. A bounded correction now changes to the workspace, builds exactly
`ros_esc_interfaces`, `ros_esc`, and `turtlebot3_vehicle_nodes`, verifies
`install/setup.bash`, and sources it before resolving installed assets. The
change has an `MBuck 2026-08-01` explanation comment and a test enforcing
build-before-source order. The physical package README documents the behavior.

The corrected snapshot collection reports `93 passed in 1.49 s`. The final
mounted-Pi-source collection reports `93 passed in 28.34 s`; its caches and
temporary files were redirected to
`/tmp/phase09_pi_final_full_retry.4Cft1g`. A direct mounted-source parity/launch
subset reports `44 passed`. All 27 Bash files pass `bash -n`; Python compileall
and parsing of 11 XML, 7 YAML, and 68 JSON documents pass. No on-Pi build,
installed overlay, launch, ROS graph, serial device, or physical mechanism ran.

Both snapshot and Pi match all 339 final file hashes and all 425 expected
type/mode/size entries. The final manifest-scoped dry run is empty, and the
40-path historical operator-selection set remains M0-identical. The updated
patch reproduces all 339 final hashes forward and all 306 M0 hashes in reverse.

The authored-document diff check passes when the generated checkpoint,
recovery patch, and full-mode inventory TSV are excluded. The generic check
reports only the three intentional empty final TSV fields and the checkpoint's
three verbatim echoes of those fields; no authored source or prose finding is
present.

```text
after-file manifest:
  1d86d9ebceffbef49df06a53470f972f1897fc7488fd0fa315abd2a47004cd36
after inventory:
  8eacf7b7f36cd67979688cf168ae5fd3c4e8274ebdffa149e76b12c737c647ee
51-path patch:
  8985b4b2f5a33383a9abe4b6dc48a48a999c4da9dec5dfc24b88e9b324708939
```

See `phase_09_pi_transfer_receipt.md` for the backup and rollback evidence.

## M8B final host qualification

Verified: `2026-08-02T03:09:13Z`

Result: `PASS — EVALUATION-ONLY VICON, STAGED ROTATION, STATIONARY PREFLIGHT,
RECORDING, AND SINGLE-ENTRY SOURCE QUALIFIED ON HOST; HARDWARE DEFERRED`

This is a fresh host qualification after the M8B implementation and final
adversarial review. It did not execute a command on the Pi, start the physical
ROS graph, contact Vicon Tracker, open serial/GPIO/OpenCR, run calibration, or
command either actuator. The isolated build root was:

```text
/tmp/phase09_m8b_final3.DhSBng
```

The final source was built after all production corrections. All three
packages completed in `13.0 s`:

```text
ros_esc_interfaces       PASS
ros_esc                  PASS
turtlebot3_vehicle_nodes PASS
```

Every test process disabled bytecode and the pytest cache. Results:

| Collection | Result |
|---|---:|
| final Phase 09 parity, physical recording, rotation, Vicon, launch/wrapper, and calibration adapter | `309 passed in 5.09 s` |
| physical recorder/validator adversarial contract alone | `137 passed` |
| Phase 09 Vicon protocol alone | `58 passed` |
| shared core/state-machine/Gaussian regressions | `272 passed in 7.53 s` |
| inherited Phase 05 recording regressions | `70 passed, 1 skipped in 2.85 s` |
| physical-compatible observability | `13 passed, 2 deselected in 0.85 s` |
| repository legacy behavior in its correct source overlay | `34 passed in 2.71 s` |

The one skip remains the opt-in visible-Gazebo recording smoke and was not
enabled for this physical source-only gate. The two observability exclusions
are the known simulation cost-owner cases absent by design from the physical
package. A first local command replaced, rather than prepended, `PYTHONPATH`
and failed collection because it hid `/opt/ros/humble`'s `rclpy`; the corrected
fresh commands above prepended the snapshot sources and passed. No behavior
pass is claimed for that environment mistake.

The final independent audits and counterexamples prove:

- strict JSON wire types, normalized identity, nonce/session/script hashes,
  finite pose values, subject/segment identity, session continuity, and
  advancing Vicon packet and Tracker-frame evidence;
- at least two same-session status samples per readiness epoch, with Vicon
  retained only on evaluation topics and `/odom` retained as every algorithm
  pose input;
- passive `WAITING_AUTHORIZATION` evidence before any rotation GPIO owner may
  initialize, a permanent pre-gate nonzero-command latch, and an exact
  authorization-revoked terminal zero status;
- no base readiness before the selected rotation and data planes are ready;
- stationary-preflight no-authorization/no-actuation behavior for the full
  hold interval;
- exact operational heartbeat requirements in the retained physical manifest,
  bounded start, interior, and end gaps across the complete readiness-true
  interval, including zero-command `GOAL_HOLD`;
- final-zero dwell while rosbag remains active both before and after target
  termination; and
- immutable calibration provenance: real readable sqlite3 bag, resolved
  serial/firmware configuration, calculation schema, raw negative-voltage
  sign, rotation/sample cardinality, median/MAD intervals, and artifact hashes.

Installed-overlay checks passed for all six typed interfaces, all six unique
wrapper launch descriptions with `--show-args`, the selected wrapper/launch,
and ten installed source/share copies. The install exposes `15` `ros_esc` and
`10` vehicle-node executables. A first comparison used an incorrect assumed
extra `ros_esc/` share subdirectory and stopped before reporting a result; the
correct installed layout then passed `10/10` byte comparisons.

Static and preservation gates:

| Gate | Result |
|---|---:|
| Bash syntax | `27/27` |
| structured files | `11 XML + 7 YAML + 68 JSON = 86/86` |
| critical Python `E9,F63,F7,F82` | `111/111` files |
| formal legacy operator-selection assets | `40/40` M0-identical |
| expanded legacy configuration set | `68/68` M0-identical |
| generated/cache paths in snapshot source | `0` |

The final snapshot recovery seal is `345` regular files and `432` complete
inventory entries, with `39` new, `18` modified, `0` deleted, and `0`
symlinks relative to M0. The exact receipts are:

```text
transfer manifest, 57 paths:
  f015285fa8b618f985d7257ac1471fe02c61e4ba17bc4701457ba36411931ff6
after regular-file manifest, 345 rows:
  97af95a46bc8161f83a6776d609eb2480c0af0584b09ac62d5d60b9f2f638053
after inventory/modes, 432 rows:
  602c2c9fa1f31fa7bd29692a07127e65b72c8570b1dcb6273226367db38643d2
57-path, 31,986-line patch:
  6fd166368449f33cff85d5e1422a414199171b27d8420e9ea1364cb2f5090885
```

A fresh same-permissions M0 extraction passed forward patch checks and matched
all `345/345` hashes plus `432/432` inventory entries. Reverse application
matched all `306/306` M0 hashes and `389/389` baseline entries. Four reverse
warnings reproduce inherited M0 trailing whitespace exactly; they are not
patch corruption. This is strong source/static evidence, not `PHYSICAL READY`.

The authored-document diff check passes when the generated recovery patch,
full-mode inventory, and verbatim checkpoint are excluded. The generic
`git diff --check` reports only sealed recovery representation: 14 patch lines
that preserve source bytes, 22 changed inventory rows with the intentionally
empty symlink-target column, and 36 checkpoint echoes of those findings. No
authored prose or source outside that generated evidence fails the check.
