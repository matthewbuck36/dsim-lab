# Phase 09 sixth physical-run heartbeat-lane repair

Date: 2026-08-04
Milestone: M8K
Result: host/source qualified; reviewed Pi transfer and parity pass;
post-source-change operator check-only pending

## Retained run and direct result

The sixth selected run remains unchanged at:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/2026-08-04/
  20260804T231459927630Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_2155c436
```

Recorder readiness was true for `119.608472429 s`. Integrated onboard `/odom`
path length was `4.554253040 m` with `2.461536026 m` net displacement.
Evaluation-only Vicon path length was `5.282798477 m` with `2.329767063 m` net
displacement. The detector published a qualified convergence candidate at
`23:17:31.812 UTC`, confirmed convergence after `6.003336 s` of qualified
dwell at `23:17:37.817 UTC`, and supplied onboard `/odom` fill center
`(-1.492954, -1.607303) m`. The supervisor entered `VERIFY_EXTREMUM` and held
zero command. Recorder shutdown interrupted verification about `5.4 s` later,
before the configured nine-second candidate-cost evidence window. The bag has
zero fill requests and zero typed Gaussian fills.

The finalized bag contains `48,731` messages. Familiar and additional CSV
exports passed, bag and target cleanup were clean, and offline final-zero
checks passed. Completeness remains honestly failed for runtime shutdown
metadata and the downstream convergence-node teardown process marker.

## Receipt-gap diagnosis

During the authorized interval:

| Stream | Maximum bag receipt gap (s) |
|---|---:|
| recorder readiness | 0.144462 |
| recorder rotation authorization | 0.144453 |
| source cost | 0.229922 |
| onboard `/odom` | 0.077911 |
| IMU | 0.072415 |
| encoder | 0.054173 |
| filter output | 0.254152 |
| Timekeeper | 0.091584 |
| rotation status | 0.093077 |
| rotation command | 0.079583 |
| algorithm state | 0.089001 |
| supervisor command | 0.091248 |

M8J therefore succeeded: both gate heartbeats remained well inside the
unchanged `0.50 s` motion-owner leases. All actual runtime publishers also
remained well inside the recorder's `1.50 s` runtime bound. Only the
coordinator's in-process subscription observations aged together to
approximately `1.846-2.019 s`, crossing the `1.50 s` bound plus `0.50 s`
stale-only grace. This is a recorder callback-lane false positive, not sensor,
pose, algorithm, Vicon, OpenCR, or publisher loss.

## Approved bounded correction

Keep the M8J gate group. In physical mode only, move passive diagnostic
subscriptions and the terminal diagnostic timer to a second dedicated
mutually exclusive callback group, retain safety-heartbeat and command
subscriptions in the default group, and use exactly three executor threads.
Simulation and legacy remain single-threaded. No threshold, lease, semantic
fault, final-zero rule, algorithm, topic, cost convention, pose owner, Vicon
role, launch, wrapper, or legacy method changes.

## Pre-edit recovery evidence

Matching recovery roots:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260804T234106-0700_m8k_physical_heartbeat_lane
/home/mattb/tb3-pi/phase09_backups/
  20260804T234106-0700_m8k_physical_heartbeat_lane
```

Pre-edit evidence:

```text
snapshot/Pi regular files:     347/347 PASS
source-manifest SHA-256:       4cac14581722f81a98677a41f0e5d867951f25c55d46f895d9484553fe781d98
snapshot/Pi inventory entries: 435/435 PASS
inventory SHA-256:             aa1589808c9d76fb9201c51edcdb087cf0aeedda6bf9999e4b1e06f247f0699d
transfer-scope SHA-256:        47c3244595077d850fac326308c3f73ef20d1cf7ffce9ddc57a465ded3bb3bf7
```

Source implementation and qualification results will be appended after each
verified milestone. Codex will not run a Pi build or any physical process.

## Implemented source boundary

M8K changes exactly the existing physical recorder and its focused test.

- The M8J gate timer remains in its dedicated mutually exclusive callback
  group.
- Physical mode adds `passive_diagnostic_callback_group` for passive
  diagnostic subscriptions and the terminal diagnostic timer.
- Heartbeat and command-observation subscriptions remain in the default
  safety group.
- Physical mode uses exactly three executor threads so all three groups can
  progress independently.
- Simulation and legacy retain `SingleThreadedExecutor`; their subscriptions
  and diagnostic timer remain in the default callback group.
- Gate topics/rates, all stale thresholds and grace, both motion-owner leases,
  semantic/process checks, final zero, algorithm/tuning, topics, cost
  semantics, `/odom`, evaluation-only Vicon, launches, wrappers, and legacy
  methods are unchanged.

## Host qualification

| Gate | Result |
|---|---:|
| focused physical lane and simulation-construction tests | 4 passed |
| blocked-passive-diagnostics probe, independent processes | 5/5 passed |
| complete changed focused file | 143 passed |
| complete snapshot Phase 09 functional suite | 268 passed |
| canonical recorder regression against changed snapshot owner | 69 passed |
| canonical legacy plus recording integration | 38 passed, 1 expected skip |
| Python AST and critical lint `E9,F63,F7,F82` | PASS |
| edited-file full-style delta | 1,942 before / 1,942 after; zero added-line findings |
| isolated three-package snapshot build | PASS in 14.9 s |
| isolated installed-overlay focused probe | 4 passed |

The real-rclpy M8K probe blocks the passive diagnostic callback for `2.25 s`,
longer than the complete `1.50 s` runtime threshold plus `0.50 s` stale-only
grace. During the block, the synthetic heartbeat remains younger than
`0.30 s`, both gate topics continue with sub-`0.30 s` gaps, and
`revoke_if_unsafe()` returns no errors with readiness still true. The separate
M8J regression still blocks the default callback group for `0.75 s` and proves
both gate topics remain live.

The fresh isolated build is retained at
`/tmp/phase09_m8k_build.IL3wl3`. It built `ros_esc_interfaces`, `ros_esc`, and
`turtlebot3_vehicle_nodes` in `14.9 s` without using Pi build/install state.

Two command-environment mistakes were retained and corrected:

1. Running canonical legacy tests with the physical snapshot package first on
   `PYTHONPATH` produced the expected cross-tree
   `Multi_Light_Source_Cost` collection mismatch. Rerunning the unchanged
   canonical tests in canonical source context passed `38`, with one expected
   skip.
2. Clearing `PYTHONPATH` after sourcing the isolated overlay removed ROS's own
   Python paths and caused `ModuleNotFoundError: rclpy`. A fresh sourced shell
   without clearing the variable passed all four installed-overlay probes.

Neither command error changed source or represents a product failure.

## Reviewed SSHFS transfer and final parity

Immediately before transfer, both mounted-Pi target files still matched their
sealed pre-edit recovery copies. The checksum dry run listed exactly:

```text
ros_esc/ros_esc/experiment_recording/record_run.py
ros_esc/test/test_phase09_physical_recording.py
```

The source transfer used checksum-scoped `rsync -rlptO` through the existing
user-mounted SSHFS tree, with no delete option and no directory-time updates.
The post-transfer dry run was empty. Final per-target hashes are:

```text
record_run.py:                       911c370d2019578781c909d9fd9cbe85b585fb3e70d9f5000b7147ab68ce5cbc
test_phase09_physical_recording.py:  dc7e2281a56d80e441ab3d70e55c4dfc8cceff5c87928e14918b98b96b1af385
```

Snapshot and mounted-Pi hashes match for both files. Their sealed rollback
copies remain unchanged at hashes
`4debc462b173b6c33590187536e5094d4b28a6518433ebce9666a0602ff6c52d`
and
`0ceadac36282310bb969bdb105fc2965fdf3d46bdc7b5f4ab391fc2c650725a7`.

Generated test/build caches were removed only from the two source roots:
snapshot/Pi cache-directory counts were `24/22`, and bytecode counts were
`54/50`. Final cache and bytecode counts are zero. Normalized final parity is:

```text
snapshot/Pi regular files:     347/347 PASS
source-manifest SHA-256:       b4608bed1cca5a7e45f9e5411ea12156c5c40f282ea0be6d44f53ba3bea57fe0
snapshot/Pi inventory entries: 435/435 PASS
inventory SHA-256:             269523e491eec089a21ce72138ed8ef8b3eb3331993ef1024a86c73f20d04312
```

Host-side AST parsing and critical lint of the mounted copies pass. Matching
post-transfer receipts are retained in both M8K backup roots with SHA-256
`056a826d1f9b0e686c758753e5e399c37064a536f33b4af824778ea920e26a0c`.

Codex did not execute a Pi command, build, source operation, ROS graph,
serial/GPIO access, Vicon client, recorder, actuator, or motion. Because Pi
source changed, the next criterion is one operator-owned
`./gesc_gaussian_two_source_voltage.bash --check-only` from the standalone SSH
terminal. It must pass the three-package build, installed parity, selected
physical `False`, legacy-default `True`, device separation, and launch
construction before the next bare experiment.
