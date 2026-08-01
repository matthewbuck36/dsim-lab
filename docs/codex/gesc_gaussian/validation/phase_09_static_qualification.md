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
phase09_gesc_gaussian_counted_two_source.launch.xml
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
