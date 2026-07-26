# Phase 08 v2 Failure Report

Outcome: **FAILED — LEVEL C**.

The workflow stopped after the mandatory ten-run `activation` stage. No tuning,
parameter selection, freeze, holdout, 70-run validation denominator,
reproducibility run, physical command, or simulation-ready tag was authorized
or executed.

## Executed command and retained evidence

```bash
timeout 7200s ros2 run ros_esc validate_robustness activation \
  --operator phase08_v2 \
  --evidence-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2
```

The command retained all ten declared runs and exited 1. The sealed workflow
manifest SHA-256 is
`66c17005f67dd056e41673a0754e838f5ee22a0280b0f5d649043ad3c461cd71`.
The evidence root uses 1.8 GiB and contains ten completeness documents and ten
sqlite3 bags; read-only `PRAGMA quick_check` returned `ok` for 10/10 bags.
Cleanup passed for 10/10 runs and no Phase 08, Gazebo, recording, or rosbag
process remained.

Durable state:

- `workflow_state/v2_activation.json`: SHA-256
  `1cfa609acf6e39d91230b300bf8bf14f08b486de36f561172deb6dc1d621d0b8`
- `workflow_state/v2_failure.json`: SHA-256
  `3de93fd5571412ed23152b2e09ef98257a5ed63f16c1121b243a8d26f95c8d3c`
- `activation/records.json`
- `activation/scenario_summary.yaml`

The v2 manifest excludes historical v1 paths and hashes. Representative v1
artifact hashes were rechecked after activation and remained identical to
`phase_08_v1_failure_closeout.md`; no v1 evidence was resumed, overwritten, or
counted.

## Activation result

| Measure | Observed | Required |
|---|---:|---:|
| Declared runs retained | 10/10 | 10/10 |
| Full integrity and lifecycle pass | 1/10 | 10/10 |
| Recording complete | 3/10 | 10/10 |
| Analysis complete | 3/10 | 10/10 |
| Classification pass | 1/10 | 10/10 |
| Cleanup pass | 10/10 | 10/10 |
| Controller and ground-truth success | 1/10 | designated-case coverage |
| Valid no-collision evidence | 9/10 | 10/10 valid |
| Typed fills | 7 | greater than zero |
| Observed escape attempts | 1 | greater than zero |

The retained functional suite run inside activation passed:
`189 passed, 2 skipped in 10.44s`. The skips were the explicit
`RUN_GESC_PHASE06_GAZEBO_E2E` and `DSIM_RUN_GAZEBO_RECORDING_TEST` gates.

## Per-case findings

| Case | Evidence and lifecycle outcome |
|---|---|
| `activation_goal_low` | Timestamp-integrity failure; `SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> FAILSAFE`; late `FILL_CREATED`; controller false, ground truth true. |
| `activation_goal_medium` | Same timestamp/lifecycle failure; controller false, ground truth true. |
| `activation_goal_high` | The only full pass; `SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD`; `CONVERGENCE_CONFIRMED` and `GOAL_REACHED`; controller and ground truth true. |
| `activation_fill_create` | Timestamp-integrity failure; fill observed only after timeout/failsafe; designated lifecycle failed. |
| `activation_pure_escape` | Timestamp-integrity failure; no `ESCAPE_REPULSE`; fill observed, zero escape attempts. |
| `activation_stalled_assist` | Infrastructure failure while capturing required publisher parameters after controller-manager unavailability and a robot-state-publisher response timeout; analysis and collision evidence invalid. |
| `activation_fill_merge` | Timestamp-integrity failure; no merge; ended in `FAILSAFE`. |
| `activation_recenter_resume` | Recording and analysis complete, but only `FAILSAFE` was observed; designated lifecycle failed. |
| `activation_boundary_negative` | Timestamp-integrity failure; no collision, ground truth true, controller false. |
| `activation_noise_delay` | Recording and analysis complete; one real `ESCAPE_REPULSE -> RECENTER -> SEARCH` sequence with `FILL_CREATED`, `ESCAPE_STARTED`, and `RECENTER_COMPLETE`, but its required goal lifecycle did not complete. |

Six runs failed completeness because a late stale-source `FILL_CREATED` event
arrived after a later timeout/failsafe event, causing typed ROS timestamps to
regress by more than 0.150 seconds. One run had the separate publisher-parameter
snapshot failure. Two additional complete runs missed their designated
behavioral lifecycle. These retained failures make Gate 2 fail even though the
nonzero fill and escape-activation subconditions were observed.

## Amended acceptance gates

- Gate 1, retained functional tests: **PASS**.
- Gate 2, all ten activation proofs: **FAIL**, `1/10`.
- Gates 3–14: **NOT RUN** because Gate 2 is an early-stop gate.
- The 70-run denominator and two-sided Wilson score intervals are not
  applicable because those runs were not executed.
- Simulation ready: **false**.

## Smallest justified next engineering phase

Open a bounded Phase 08.1 diagnosis against these retained bags, completeness
documents, resolved scenarios, and console logs. Its scope should distinguish:

1. the late stale-source event timestamp ordering;
2. the low/medium and lifecycle-case path from verified minima into fill-design
   timeout/failsafe;
3. the stalled-assist publisher-parameter snapshot failure; and
4. whether the rotation score window should exclude approach samples before a
   new acceptance plan is approved.

Do not retune, weaken the gate, resume historical v1 evidence, reuse these ten
runs as a future passing denominator, begin physical Phase 09, or create the
simulation-ready tag.

No physical hardware was run.
