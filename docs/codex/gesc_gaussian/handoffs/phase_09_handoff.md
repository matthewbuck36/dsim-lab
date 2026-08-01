# Phase 09 Handoff — Physical Snapshot Static Integration

Date: `2026-07-31` (`America/Los_Angeles`)

Outcome: `SNAPSHOT STATIC INTEGRATION PASS — HARDWARE DEFERRED`

This is not `PHYSICAL READY`. No live Pi, serial device, sensor, TurtleBot,
motor, servo, rotating frame, lamp, floor trial, or emergency stop was used.

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
  `phase09_gesc_gaussian_counted_two_source.launch.xml`;
- only the new `gesc_gaussian_counted_two_source_voltage.bash` and the physical
  recorder target contract point to that new launch;
- all 27 Bash files pass syntax and static launch/argument checks; and
- all original package console entry points remain present.

The new launch has no Vicon relay, legacy CSV owner, broad `pkill`, evaluator
coordinate input, or second `/cmd_vel` owner. Historical wrappers retain their
historical launch behavior.

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

The selected graph uses wheel/IMU-backed `/odom` for every pose consumer and
records/heartbeat-gates `/imu`. The sole Phase 05 recorder sets and verifies
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
Future motion requires reviewed copies with calibration, operator, measured
response, live transfer, stationary graph, emergency stop, observer, field,
and explicit authorization evidence all true.

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

## Exact snapshot scope and recovery

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

## Durable evidence

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

## Deferred M8 and M9

M8 live-Pi read-only comparison, backup, scoped transfer, on-Pi build, and
rollback rehearsal are `NOT RUN`. M9 stationary hardware checks, calibration,
emergency-stop rehearsal, and any selected motion trial are `NOT RUN`.

The next action, if desired, is a separate authorization for M8 read-only live
Pi comparison only. It does not automatically authorize transfer or hardware
motion. Follow `phase_09_pi_transfer_and_rollback.md` and stop on any overlap.

## Git state and commit boundary

Repository base during Phase 09 remained branch
`feature/gesc-gaussian-robustness-v1` at
`c04c222dfeac525197bf0542cbde64f1421dc664`, ahead of origin with the user's
pre-existing Phase 09 implementation-package edits preserved. On 2026-07-31,
the user authorized bounded Phase 09 closeout and receipt commits so the
repository could return to a clean worktree. The exact closeout commit is
recorded in the post-commit receipt in `phase_09_status.md`. No push is
authorized by that cleanup request.
