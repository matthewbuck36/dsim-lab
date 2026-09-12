# Q1 recorder simulation duration — 2026-09-09

Status: implemented in the existing recorder and coordinator; **129 focused
tests pass**. Q1 acquisition has not started. This result checks orchestration
and duration semantics, not Gazebo trajectories or scientific qualification.

## Selected behavior

`record_run --sim-duration-sec` defaults to0, disabled. A positive value is
accepted only in simulation with a valid selected manifest `clock` alias of
type `rosgraph_msgs/msg/Clock`. Nonfinite, negative, sub-nanosecond and
out-of-range values are rejected before creating a run directory. The existing
`--duration-sec` remains elapsed wall time from readiness when the new option
is disabled. Q1 supplies `--sim-duration-sec 125 --duration-sec 0`; the runner
owns its separate overall wall limit.

The existing `RecordingCoordinator` receives the selected clock topic using
best-effort volatile QoS. The first successful readiness authorization freezes
the latest actual Clock payload as integer-nanosecond origin, under its existing
state lock. The clock must be present, valid and received within the inherited
0.5s freshness interval before authorization. Receipt time, Timekeeper origin,
bag time and wall time never replace the source-clock value. A failed attempt
does not freeze an origin; later checks cannot restart an accepted origin.

Repeated or paused clock values do not advance elapsed simulated duration.
Malformed or backward clocks latch a failure; a later forward value cannot
rehabilitate the run. A slow clock reaches its actual simulated target even
after more wall time than the requested simulated duration. If both optional
durations are positive, wall expiry before simulated completion fails.
An external interrupt before requested simulated completion also fails, while
preserving the existing default interrupt behavior when the new option is off.

Target and rosbag process exits are checked before duration completion, so an
early exit remains a failure even if a simultaneous clock sample reaches the
target. All paths retain the existing `finally` shutdown owner: readiness false,
stop request, final-zero observation, post-zero recording tail, target/bag stop
and ROS teardown. No second recorder, process controller or physical path was
introduced.

`metadata.recording.simulation_duration` records `enabled`, `requested_sec`,
`clock_topic`, `ready_clock_ns`, `latest_clock_ns`, `target_clock_ns`,
`elapsed_sec`, `completed` and `clock_error`. It is saved at readiness and frozen
again immediately before cleanup. Cleanup clock advancement cannot inflate that
snapshot or turn interrupted exposure into completion. Natural completion adds
`recording.completion_reason=simulation_duration_elapsed`; legacy wall completion
is named `wall_duration_elapsed`. Existing UTC and operational wall timestamps
remain available separately.

## Commands and evidence

From `/home/mattb/dsim-lab`, initial version (before the four full-orchestration
fixtures) used this exact environment and test set, with output redirected to
`q1_sim_duration_v1.log`: **125 passed in4.20s**, exit0, no warnings.
The final expanded version was:

```bash
timeout 120s bash <<'BASH' > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_sim_duration_v2.log 2>&1
set -e
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
export ROS_DOMAIN_ID=187
export PYTHONPATH="/home/mattb/dsim-lab/ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_sim_duration.py ros2_ws/src/ros_esc/test/test_experiment_recording.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py
BASH
```

Result: **129 passed in4.10s**, exit0, no warnings. The new tests instantiate the
actual coordinator and selected Clock subscription, exercise callback admission
and simulated/wall stop decisions, and check the unchanged cleanup sequence.
Four `run()` fixtures execute actual orchestration for normal completion,
interrupt, rollback and early target exit; external graph/process/capture I/O
is mocked, so those cases are not live DDS or real-bag completeness evidence.
The established recorder and V2 contract regressions also pass.

`timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`
passed before editing. `git diff --check` passed. A read-only comparison against
the M3 archive confirmed the recorder delta contains this optional timing path;
prior M2/M3 changes and shutdown implementation remain intact. No Gazebo,
hardware, package installation, field evaluation or commit occurred.

## Hash boundary

| Input/artifact | SHA-256 |
| --- | --- |
| `experiment_recording/record_run.py` | `af4a38c3bac66051ab645d0c2ee7659a581915e28394cbbe35516a1392b4b7da` |
| `test/test_q1_sim_duration.py` | `e67a19b3610bdca606a1fd645bfeaea33a21b718c46eaf3432e78ed60a3799e5` |
| `q1_sim_duration_v1.log` | `379d85326237d94748f8c089ffefa40a9ee4d0e084d0a356f85b66851533c86b` |
| `q1_sim_duration_v2.log` | `77c2e0c9682e6be503560e1fa2c50693d7bd221d2e522866ecbc7755391ebbed` |

Both logs are retained under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.
