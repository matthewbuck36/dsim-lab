# Phase 09 fifth physical-run gate-lane repair

Date: 2026-08-04
Milestone: M8J
Result: host-qualified, reviewed two-path Pi source transfer complete; live Pi
build and check-only not run by Codex

## Retained run and diagnosis

The fifth bare selected run remains unchanged at:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/2026-08-04/
  20260804T224523162901Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_8d7f9b77
```

The post-M8I wrapper build and installed parity passed. The run reached
readiness for `6.189496959 s`, executed `SEARCH`, respected the frozen
`0.05 m/s` and `0.30 rad/s` command ceilings, and moved approximately
`0.045709275 m` net by onboard `/odom` and `0.059153267 m` by evaluation-only
Vicon. No Gaussian fill was created before shutdown.

The retained rosbag distinguishes the direct stop from the terminal's later
error:

| Stream | Maximum receipt gap (s) |
|---|---:|
| recorder `/gesc_gaussian/recording_ready` | 1.572357758 |
| recorder `/gesc_gaussian/rotation_authorized` | 1.572276295 |
| source cost | 0.208691926 |
| filter output | 0.225295334 |
| `/cmd_vel` | 0.233850926 |
| control diagnostics | 0.240259019 |
| onboard `/odom` | 0.066318445 |
| evaluation-only Vicon | 0.114491926 |
| algorithm state | 0.073921852 |
| rotation status | 0.067659759 |
| rotation command | 0.064828556 |

Both gate topics are published by the same recorder timer and paused together
while all algorithm, pose, and actuator-evidence streams continued. The
rotation owner correctly enforced its unchanged `0.50 s` authorization lease,
reported `FAULT` with `rotation authorization heartbeat became stale`, and
published rotation zero. The base's first zero followed the recorded rotation
fault by approximately `12.663 ms`, and no later nonzero base or rotation
command occurred. The recorder's later
`operational rotation status heartbeat is invalid` message describes the
already-faulted rotation status; it is downstream evidence, not the initiating
fault and not a check to bypass.

Target and bag processes stopped cleanly, familiar CSV export passed, and the
offline base final-zero check passed. The old completeness report remains
honestly failed for rotation-status evidence, the resulting end-gap in
rotation-command operational coverage, and runtime metadata. The retained bag
cannot distinguish a single lower-level operating-system, storage, or Python
callback delay, but it proves the code-level vulnerability: the recorder used
one single-threaded executor for its safety heartbeats, all subscriptions, and
passive diagnostics.

## Bounded correction

M8J changes only the existing physical recorder owner and its focused test.

- Physical mode now creates one dedicated mutually exclusive callback group
  for the existing periodic readiness/rotation-authorization publisher.
- Physical mode uses exactly two executor threads: the default recorder group
  retains all subscriptions and passive live diagnostics, while the second
  lane can service the gate timer.
- Simulation and legacy modes still select `SingleThreadedExecutor` and retain
  the original default callback group.
- Gate topics, gate rate, readiness decisions, runtime/semantic checks,
  controller and rotation-owner `0.50 s` leases, final-zero behavior, wrapper,
  launch graph, algorithm tuning, `/odom` ownership, and evaluation-only Vicon
  behavior are unchanged.
- No new node, process, recorder, validator, authorization file, or operator
  ceremony was added.

This repairs producer scheduling without making either motion consumer accept
stale authorization.

## Recovery and transfer

Matching pre-edit recovery roots were sealed before source writes:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260804T225906-0700_m8j_physical_gate_lane
/home/mattb/tb3-pi/phase09_backups/
  20260804T225906-0700_m8j_physical_gate_lane
```

Both `source_before.sha256` files have SHA-256
`c73da57ec8df83a03f620c4f2c3d6a2745f90c579fb283eb46eb3210d33ed4db`.
The transfer scope hash is
`47c3244595077d850fac326308c3f73ef20d1cf7ffce9ddc57a465ded3bb3bf7`.
Immediately before transfer, both Pi targets still matched their sealed
copies. Checksum-scoped `rsync` through the user-mounted SSHFS tree copied
exactly:

```text
ros_esc/ros_esc/experiment_recording/record_run.py
ros_esc/test/test_phase09_physical_recording.py
```

No source file was deleted. Qualification-generated cache cleanup removed
only `__pycache__`, `.pytest_cache`, and `*.pyc` artifacts: `23` snapshot and
`22` Pi cache directories containing `50/50` bytecode files. Matching
`POST_TRANSFER.md` receipts have SHA-256
`44148426828219c4d8a2be5aa984ccc8a46c4cfd651c3f0317bdba5cb9244db4`.

## Host qualification

| Gate | Result |
|---|---:|
| focused executor selection plus blocked-default-group test | 2 passed |
| blocked-default-group test repeated independently | 5/5 passed |
| complete snapshot Phase 09 functional suite | 266 passed |
| canonical recorder regression against changed snapshot owner | 69 passed |
| canonical legacy plus recording integration | 38 passed, 1 expected skip |
| Python AST/compile and critical lint `E9,F63,F7,F82` | PASS |
| focused full-style delta versus pre-edit files | unchanged baseline, 1783 |
| isolated three-package snapshot build | PASS in 14.8 s |
| isolated installed-overlay focused probe | 2 passed |
| mounted-Pi AST and critical lint | PASS |

The package-wide `ament_flake8` test still traverses the repository and reports
the documented inherited style baseline. Direct comparison of the two edited
files reports exactly the same `1783` pre-existing style findings before and
after M8J; critical changed-file lint passes.

Fresh normalized whole-source comparison proves:

```text
snapshot/Pi regular files:       347/347 PASS
source-manifest SHA-256:         4cac14581722f81a98677a41f0e5d867951f25c55d46f895d9484553fe781d98
snapshot/Pi inventory entries:   435/435 PASS
inventory SHA-256:               aa1589808c9d76fb9201c51edcdb087cf0aeedda6bf9999e4b1e06f247f0699d
snapshot/Pi source cache dirs:   0/0
```

The isolated build is retained at `/tmp/phase09_m8j_build.xS35G3`.

## Boundary and next action

Codex ran no command on the Pi, built no Pi package, started no ROS graph,
opened no serial/GPIO device, connected no Vicon client, started no recorder,
and commanded no actuator or robot motion. Source parity is not a physical
result.

Because Pi source changed, the sole next action is the human-owned standalone
SSH command:

```bash
cd ~/ros2_ws/src/turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values
./gesc_gaussian_two_source_voltage.bash --check-only
```

Review the three package results, installed parity, selected physical `False`,
legacy-default `True`, device separation, and launch construction. If it
passes, return to the ordinary Vicon/lab SOP and the bare wrapper; check-only
does not become a permanent per-run gate. A later retained run must still
demonstrate sustained GESC+Gaussian operation, warranted Gaussian-fill
lifecycle behavior, managed final zero, complete bag/CSV evidence, and the
physical two-light objective.
