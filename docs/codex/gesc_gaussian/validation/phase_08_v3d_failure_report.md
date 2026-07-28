# Phase 08.3 V3D activation failure report

## Terminal disposition

V3D and Phase 08.3 are **CLOSED / FAILED / NOT SIMULATION-READY**.

The immutable evidence root is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3d
```

Fresh V3D adoption and qualification passed. The GUI-visible activation then
executed one new case and stopped at the first unchanged infrastructure hard
failure. No replacement or second case ran.

This detailed report supplements the workflow-generated
`phase_08_v3_failure_report.md`. The workflow-generated report and terminal
state remain byte-identical.

## Actual Gazebo execution

```text
case_id: v3a_below_target_fill
seed: 9302
attempt_index: 1
gazebo_gui: true
simulation_contacts_enabled: true
simulation_contact_probe_enabled: false
```

Run ID:

```text
20260728T093403582899Z_simulation_phase08_v3_activation-
v3a_below_target_fill-robust_gaussian_v1-f20cd3c751_74a3fcfb
```

Run directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3d/activation/
attempts/002_v3a_below_target_fill/attempt_01/runs/2026-07-28/
20260728T093403582899Z_simulation_phase08_v3_activation-
v3a_below_target_fill-robust_gaussian_v1-f20cd3c751_74a3fcfb
```

Gazebo server and client both ran on X11 display `:0`; no headless argument
was present. Motion readiness became true. The retained state path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> FAILSAFE
```

The boundary observer recorded `CONVERGENCE_CONFIRMED`, `FILL_CREATED`, and
`ESCAPE_STARTED`, then requested a graceful scoped stop.

## Hard-stop cause

The record process returned `2` with:

```text
RCLError: Failed to publish: publisher's context is invalid
```

`record_run` initialized the default ROS context with rclpy's default signal
handlers. The runner's declared boundary stop sent `SIGINT` to the recorder
process group. rclpy invalidated the default context before
`RecordingCoordinator.request_stop()` could publish readiness false and stop
true. The main thread and the 10 Hz readiness timer then raced while publishing
on that invalid context.

The first exception aborted the remainder of recorder finalization:

- final-zero observation did not complete;
- owned target and bag shutdown did not complete through the recorder;
- executor shutdown and spin-thread join did not complete;
- node/context teardown did not complete;
- final recording metadata was not written;
- the final completeness validator did not run.

Outer scoped cleanup removed the Gazebo/ROS descendants, so cleanup passed and
no process contamination remained. That does not repair recording
completeness.

## Evidence disposition

The run is infrastructure-invalid and is not a valid behavioral result:

```text
recording_complete: false
infrastructure_status: runner_or_recorder_failure
completeness failure: run did not finalize
activation integrity passes: 0
activation behavior-contract passes: 0
```

The bag is structurally readable:

- `PRAGMA quick_check`: `ok`;
- `PRAGMA integrity_check`: `ok`;
- messages: `400131`;
- topics: `33`;
- duration: `190.097876649 s`;
- odometry messages: `5456`;
- simulation-contact messages: `37085`;
- algorithm-state messages: `3713`;
- algorithm-event messages: `30`.

The bag has no retained stop request. Recording readiness has `1602` messages
but ends true, with no terminal false. Recording continued after the intended
boundary through recenter, a second fill rejection, and `FAILSAFE`. Canonical
command streams later happened to reach zero, but the recorder did not
observe and prove the coordinated final-zero contract.

Partial analysis is retained for diagnosis only. It must not be used to
retroactively finalize, relabel, replace, or count this run.

## Counts and early stop

```text
carried V3B records: 1
new V3D executions: 1
V3D attempts: 1
ambiguous interrupted attempts: 0
replacements: 0
remaining not_run slots: 8
pass_eligible: false
activation passed: false
```

The remaining `not_run` case IDs are:

```text
v3a_pure_escape_recenter
v3a_stalled_assist
v3a_fill_merge
v3a_full_lifecycle_goal
v3a_revisit_guard
v3a_boundary_saturation
v3a_noise_delay
v3a_safe_timeout
```

The executed slot is not replacement-eligible: readiness became true and the
robot traversed multiple non-`SEARCH` states. V3D must not be rerun or
continued.

## Immutable hashes

```text
workflow_state/v3_activation.json
  file: b1e4d5d9290057503f49e88976949c1ebb6eb337f6edf65110a56efac93e5c1c
  internal: 24ea143a452ecf28b5cd8a2c54d91444932de49334862038bbe47f29c898adcb
activation/progress.json
  file: de919138523b7b04b1f5cca10c94f06e14e06b26387d2c7692633c61c0695c5f
  internal: 30047de029892f16f16d6ab972bb23a47cfd3dc085caa5a6935cfcb5102e2b5a
activation/attempt_records.json
  8b7edaac2ddb2bbe07ecd4fc4f73c44e9c41589dd887fb809ad13480429721f5
activation/records.json
  ed32711e2206fde3da4b72e3bd634e480c6513c952218f2ae4ccab7fdcacec98
activation/scenario_summary.yaml
  196bd037e6d618ab0540fe612c4960f4a9c60ef943d1984b0a1c74462d3d17cf
attempt scenario summary
  ef8a6dd3b334db8de4069c9b38d49853ec362faa0b8b7fa7a2d691915f0ad5dc
attempt record
  a8ddcdf5363e7dd05085a674336afe7db3c5143fc95bcc76f95a130971bb6f91
bag database
  c2c526bf0f969276a6c6c987517cc2da2d77484e7a20e33e27865f0caba274bd
```

The new run directory contains `33` regular files with manifest SHA-256
`cfe30977ac51d11b04c35125a277c8eac0538c018f8ccb2faadc4a73c67ab6cd`.

After the terminal state was written, the complete V3D root contains `1576`
regular files with manifest SHA-256
`94161e4ec08512d844c43949da4a7ff0883031b4ea536aafad79390c66f261c9`.
The root audit also records these excluded directory-symlink mappings:

```text
qualification/isolated_build/logs/latest -> latest_build
qualification/isolated_build/logs/latest_build ->
  build_2026-07-28_02-30-33
```

The immutable carried V3B record remains SHA-256
`d1cc6b4b2f73d5ad70031d3b74d7ac4b535894bdf5425100d3f72175d2593ad5`;
its 33-file run manifest remains
`1794d2424f966fff75e08218379e69d5e3f990c912a144c1897d48bce1aefae5`.

## Terminal artifacts

The terminal report command returned `1`, matching the failed verdict, and
created:

```text
phase_08_v3_gate_results.json
  3d9835ff504a9a87af4a752a77c30a9a1ac9f47ee143968b2d7912309ee83fce
phase_08_v3_run_manifest.json
  81a721f5cbb815f85db11c946f0f7099969e09a05e845356a4baf6f9f1d319b3
phase_08_v3_validation_report.md
  cb88420088dd71899806c496029e2e9c8b4e081fe4233537d36f204382b323e3
phase_08_v3_failure_report.md
  0b7ac933655c27a124b4251b046e69225ade15ec6e20a01b1f79ab04e80ac5cc
workflow_state/v3_terminal.json
  file: 09ff05ce70090553857377966bd983c4eba6e247b97393d045ef7eec992bc3b6
  internal: e29c501868ea7f1a03fd678d78ca56f07bbf3eca8d4ea2688d6766c087370d74
```

Prepare and qualification passed. Activation failed. Development/tuning,
freeze, acceptance-contract seal, holdout, unique validation, and
reproducibility are `NOT RUN`. No acceptance denominator or Wilson confidence
interval exists.

## Smallest justified successor

The recorder correction should:

1. initialize rclpy with `SignalHandlerOptions.NO`;
2. reuse `DeferredSignalShutdown` so `SIGINT`/`SIGTERM` request shutdown
   without invalidating the context;
3. keep the context alive through readiness-false, stop-true, bounded
   final-zero observation, target stop, and bag stop;
4. perform bounded executor shutdown and spin-thread join before node/context
   destruction;
5. retain the first cleanup/finalization error while still attempting every
   remaining cleanup and durable failure-write step;
6. capture spin-thread failures in the run result;
7. prove the order with focused unit tests and an installed real-ROS,
   no-Gazebo signal smoke.

This Plan does not authorize an automatic successor. A separately authorized
diagnostic V3E could carry both the immutable V3B behavioral failure and this
V3D infrastructure-invalid execution, then execute only the remaining eight
cases once while remaining forced failed. A pass-eligible claim requires a
separately planned fresh v4 activation after the recorder correction.

No encryption key was used. No readiness tag, Phase 09 work, or physical
hardware was started.
