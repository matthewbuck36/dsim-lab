# Phase 09 M8I — Fourth Physical-Run Runtime/Evidence Repair

Verified: `2026-08-04T22:38:22-07:00`

## Result

The fourth selected physical attempt remains retained failed commissioning
evidence. It is also the first retained run that passed readiness and executed
the selected cumulative v8.12 controller on the physical TurtleBot3. M8I
repairs the bounded recorder-scheduling false positive that stopped that run
and two independent rotation-evidence defects. The repaired source passes host
qualification and is byte-identical in the offline snapshot and mounted Pi
source.

Codex did not build or source on the Pi, start pigpio or ROS, open either
serial device, connect Vicon, record a bag, or command motion. Because Pi
source changed, exactly one new human-operated selected `--check-only` is the
next gate before another bare experiment.

## Retained fourth-run evidence

The preserved run is:

```text
/home/pi/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/2026-08-04/
  20260804T221143126652Z_physical_phase09_selected_primary_r1p5_a45_ratio1to4_b27fffe0
```

It authorized sensor rotation, made recording readiness true, and ran the
controller in `SEARCH` for about 10.6 seconds. Live diagnostics retained
voltage and `raw_cost=-voltage`, filter output, onboard `/odom`,
evaluation-only Vicon, bounded commands, zero fills, and no supervisor
failsafe before revocation. Both onboard `/odom` and Vicon show roughly
`0.13 m` net movement during the operational interval. Recorded commands stay
within the selected `0.05 m/s` linear and `0.30 rad/s` angular ceilings.

The recorder then reported:

```text
operational heartbeat stale: source_cost (0.577 s)
operational heartbeat stale: filter_output_legacy (0.573 s)
```

Independent sqlite3-bag inspection shows those publishers continued through
the interval, with observed maximum receipt gaps below `0.25 s`. The selected
controller still retained its separate `0.50 s` subscription freshness
checks. The single recorder snapshot was therefore subscriber/coordinator
scheduling jitter rather than evidence that source or filter publication had
stopped.

The managed shutdown made readiness and rotation authorization false, issued
base and rotation zero commands within milliseconds, and finalized both the
target and bag cleanly. Familiar compatibility CSVs plus
`raw_cost_value.csv` and `algorithm_odometry.csv` exported successfully. The
historical `completeness.json` remains false for the recorded runtime failure,
the old first-`RUNNING` status carrying zero RPM, and the old validator's
comparison against a later repeated false heartbeat. It is not rewritten or
relabeled.

## Bounded correction

M8I changes six existing source/test files and no wrapper, launch, algorithm
tuning, controller, filter, cost owner, pose source, or Vicon owner.

- Startup authorization remains a strict one-snapshot `0.50 s` heartbeat
  check.
- Only the selected physical recorder manifest uses a `1.50 s` runtime
  coordinator threshold plus `0.50 s` continuous heartbeat-only grace.
- A transient stale-only snapshot that recovers clears the pending timer.
- Continuously stale heartbeat-only evidence revokes after the grace period.
- Malformed, nonfinite, semantic, process, controller-service, or mixed faults
  bypass grace and revoke immediately.
- Simulation and legacy behavior retain `0.50 s` and zero grace.
- Controller pose/filter/supervisor/readiness checks and rotation
  authorization/encoder checks remain independently fixed at `0.50 s`.
- The rotation state machine now emits its first finite RPM command in the
  same tick that it first reports `RUNNING`.
- Final-zero validation uses the first `true -> false` rotation-authorization
  boundary. Later recorder-owned false heartbeats no longer move the evidence
  boundary past a mechanism that already stopped.

The change therefore tolerates bounded recorder scheduling jitter without
allowing stale inputs to continue controlling the robot. `/odom` remains the
only algorithm pose; Vicon remains evaluation-only.

## Recovery and transfer

Matching pre-edit recovery roots were sealed before source writes:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260804T222620-0700_m8i_runtime_grace_rotation_evidence
/home/mattb/tb3-pi/phase09_backups/
  20260804T222620-0700_m8i_runtime_grace_rotation_evidence
```

The two `source_before.sha256` files match at SHA-256
`58e9a753e0e2510c2ecda84088ece12e74d3c3380f3cc7d160cef65a32917104`.
Immediately before transfer, all six Pi targets still matched those sealed
copies. The reviewed checksum-scoped SSHFS transfer used exactly
`transfer_scope.txt`, copied six files, and deleted no source.

After qualification, only generated `*.pyc`, `__pycache__`, and
`.pytest_cache` content was removed. The snapshot had 56 bytecode files and
the Pi had 50; both now have zero source cache directories. Matching
`POST_TRANSFER.md` receipts have SHA-256
`87ad2314ab69dab01c574e63732768223e43a6cd35e0ef85305677ae2839f544`.

## Host qualification

| Gate | Result |
|---|---:|
| targeted new runtime-grace/rotation evidence tests | 11 passed in 1.06 s |
| complete two edited focused-test files | 160 passed in 2.34 s |
| five directly related Phase 09 test files | 225 passed in 2.80 s |
| complete snapshot Phase 09 suite | 264 passed in 3.48 s |
| canonical recorder regression | 69 passed in 1.97 s |
| canonical legacy plus recording integration | 38 passed, 1 expected skip in 1.48 s |
| Python compile, YAML parse, critical lint `E9,F63,F7,F82` | PASS |
| isolated snapshot build | 3 packages PASS in 14.9 s |
| retained-run read-only validator replay | final rotation zero PASS; historical run still FAIL |

The first broad recorder regression found three old `object.__new__` fixtures
without the new runtime attributes. The implementation was corrected to
default absent attributes to the original startup bound and zero grace; the
full 69-test recorder suite then passed. A mixed physical-source invocation of
the simulation-only legacy test could not collect because the physical
snapshot intentionally excludes `Multi_Light_Source_Cost`; the authoritative
legacy suite was run against the canonical source checkout instead. One first
canonical invocation selected a stale installed module; explicitly selecting
the current canonical source produced the recorded passing result.

The read-only validator replay used `write_report=False`. It changed no run
artifact. The repaired `final_commands_zero` check passes with rotation zero
at bag timestamp `1785881561040932614` after the first authorization
revocation at `1785881556364158227`. The old run correctly remains failed for
its original runtime metadata and first-`RUNNING`/zero status; this is proof of
the evidence correction, not a retroactive successful run.

## Final source seal and next action

Fresh normalized whole-tree comparison proves:

```text
snapshot/Pi regular files:       347/347 PASS
source-manifest SHA-256:         d2b265445a82b73de2737780aaea607e94f0de1a3656828cab265980d290997f
snapshot/Pi inventory entries:   435/435 PASS
inventory SHA-256:               9fcc3725566217ebe4bd55a637f2da2b09d2b31e698293abaea55e2cc213afed
snapshot/Pi source cache dirs:   0/0
```

The sole next action is the human-owned standalone-SSH command:

```bash
cd ~/ros2_ws/src/turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/voltage_cost_values
./gesc_gaussian_two_source_voltage.bash --check-only
```

That command performs the required Pi build and installed-source checks but
starts no device or motion. If it passes, return to the ordinary Vicon/lab SOP
and invoke the bare wrapper. Do not weaken any remaining fault handling or
repeat check-only as a permanent per-run ceremony. A later retained physical
run must still demonstrate sustained GESC+Gaussian behavior, Gaussian-fill
creation when warranted, managed final zero, bag validation, CSV export, and
two-light performance.
