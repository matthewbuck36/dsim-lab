# Phase 05 Handoff

## Objective completed

Phase 05 implements and validates one motion-gated ROS 2 Humble rosbag2
recording entry point for simulation and future audited physical runs. The
implementation retains failed runs, records an explicit topic manifest and
console log, captures Git and resolved parameter state, verifies final zeros,
and rejects incomplete bags. No physical hardware was run.

The implementation began only after
`validate_phase_context.sh 05 implement` passed and the saved plan was checked
against branch `feature/gesc-gaussian-robustness-v1` at starting HEAD
`2e40388b70734dcc3c54fddf9607e55983771ade`. Live findings that contradicted
unverified plan assumptions were retained in failed-run artifacts. The user
then authorized Amendment 1 in `phase_05_plan.md`; the final implementation
follows that amendment.

## Repository state

- Branch: `feature/gesc-gaussian-robustness-v1`.
- Starting commit: `2e40388b70734dcc3c54fddf9607e55983771ade`.
- Build/install/log handling: the normal `ros2_ws/{build,install,log}` tree was
  used for the final build and live smoke; generated artifacts are ignored.
- Pre-existing light-placement edits in
  `gesc_gaussian_full_rotation_voltage.bash` were not modified or staged.
- The pre-existing `10.0`/`80.0` topic-dictionary correction was preserved.

## Files changed

The implementation is split into three coherent groups because the complete
phase exceeds ten files:

1. recorder core and installed assets: `experiment_recording/`, `setup.py`,
   and `package.xml`;
2. motion/shutdown integration: controller, PDE cost history, central launch,
   and focused tests;
3. operator documentation, topic/parameter reference, plan amendment, test
   evidence, and this handoff.

## Public interfaces added or changed

- Console entry points: `ros2 run ros_esc record_run` and
  `ros2 run ros_esc validate_run`.
- Required readiness heartbeat:
  `/gesc_gaussian/recording_ready` (`std_msgs/msg/Bool`).
- Optional stop request:
  `/gesc_gaussian/stop_requested` (`std_msgs/msg/Bool`).
- One installed explicit manifest for simulation and physical mode, using the
  audited canonical, legacy, pose, clock, and sensor topics.
- Run artifacts: `metadata.yaml`, `resolved_topics.yaml`,
  `resolved_parameters.yaml`, `console.log`, `notes.md`, `bag/`, and
  `completeness.json`.

## Parameters added or changed

- Controller CLI/launch arguments, all legacy-safe by default:
  `recording_ready_required=False`,
  `recording_ready_topic=/gesc_gaussian/recording_ready`, and
  `recording_ready_stale_sec=0.50`.
- Simulation launch argument `supervisor_use_sim_time=True`. This aligns robust
  supervisor timers and stamps with Gazebo `/clock`; a future physical launch
  must select its physical clock explicitly.
- Manifest validation tolerance
  `timestamp_regression_tolerance_sec=0.15`, based on the measured 0.10-second
  maximum plus a 50 ms scheduling margin.

## Behavior implemented

- Creates non-overwriting UTC/mode/scenario/UUID run directories under the
  configured runs root.
- Starts rosbag before the target and records only explicit manifest topics
  with Humble sqlite3 and `--include-unpublished-topics`.
- Blocks readiness until required topic names/types/publishers, singleton
  ownership, recorder subscriptions, controller interlock, and gated zero are
  verified. The shared algorithm-event bus and simulation `/joint_states` are
  the audited multi-publisher exceptions.
- Captures commit, branch, dirty state, deterministic tracked/untracked diff
  hash, target argv, operator metadata, resolved publishers/subscriptions, and
  exact parameter values/types for nodes exposing parameter services.
- Captures target and rosbag console output in one timestamped log.
- On duration expiry, Ctrl-C, or failure, publishes readiness false and stop
  true, records fresh zero evidence on `/cmd_vel`, the legacy command array,
  and typed control diagnostics, then stops the target and rosbag in order.
- Uses PID/start-time protected descendant cleanup so a failed launch cannot
  contaminate the next experiment.
- Validates sqlite readability, exact required types/counts, semantics,
  readiness ordering, motion coverage, typed stamp order and clock range,
  conditional fill evidence, clean console/process metadata, and final zeros.
- Records pre-clock configuration messages but applies the simulation clock
  range rule only from readiness true through the following false heartbeat.

## Backward compatibility

- Recording is opt-in. With `recording_ready_required=False`, the controller
  creates no readiness subscription and follows the legacy command path.
- Recorder false/missing/stale readiness forces all final outputs to zero but
  does not create a supervisor-latching controller-fault event. Other
  controller faults retain their existing event behavior.
- Cost sign, source-score normalization, units, existing public topics,
  controller saturation, and legacy CSV collection are unchanged.
- Simulation and physical modes share the runner, but Phase 05 does not invent
  a physical graph, calibration, or hardware procedure. Physical execution
  remains deferred to Phase 09.

## Tests run

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 05 implement
PASS: Phase 05 implement context is complete.

Focused Phase 05/source regression suite
PASS: 111 passed, 1 skipped (before final endpoint/parameter tests).
PASS: 49 passed in 1.22s for the amended recorder/observability/legacy subset.

colcon build --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
PASS: all 3 packages finished.
```

The final direct visible-Gazebo smoke run is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/2026-07-21/
20260721T232824094290Z_simulation_phase05-short-recording_92bb8be7
```

Its `completeness.json` reports `passed: true`, no failures, and no warnings.
All 19 required topics have messages; both process groups exited with code 0;
all three final-zero forms passed; 21 of 23 live nodes supplied parameter
values and exact types. The two optional failures were controller spawners
that exited normally before their snapshot calls. No recorder, ROS, Gazebo, or
experiment process remained after completion.

Repository-standard package tests and final syntax/lint results are recorded
in `docs/codex/gesc_gaussian/test_commands.md`.

## Known limitations

- The audited Humble CLI parameter snapshot takes about 90 seconds for this
  graph. Motion remains gated during the capture.
- `algorithm_events` is intentionally multi-publisher; its ordering tolerance
  is manifest controlled and clock mixing still fails.
- Raw sqlite3 bags can be large, and the legacy CSV collector remains active.
- Source intensities are simulator-relative values, not physical lux
  calibration.

## Unresolved failures

None for Phase 05 acceptance. Repository-wide flake8, pep257, and lint-cmake
failures remain the unchanged Phase 00 baseline and are reported separately.

## Decisions made

- Keep sqlite3 because it is the installed Humble backend; MCAP is unavailable.
- Retain every failed attempt rather than reusing a run ID.
- Enforce publisher endpoint counts, not only unique node-name strings, so two
  orphan/current processes with the same ROS node name cannot pass preflight.
- Treat controlled robot-state-publisher `-2` and Gazebo Classic `255` exits
  after managed shutdown as attributable, while continuing to reject traces,
  ROS context errors, and failed process termination.

## Exact next phase

Run `validate_phase_context.sh 06 plan`, then plan Phase 06 against this
recorder entry point and the successful run artifact above. Do not introduce a
second bag workflow.

## Recommended commit message

```text
phase 05: unify rosbag experiment recording
```
