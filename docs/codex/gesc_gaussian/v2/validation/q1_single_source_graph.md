# Q1 selected simulation source graph — 2026-09-09 UTC

Status: source and focused regression checks PASS. This is a bounded correction
under `../q1_simulation_source_plan.md`, not an acquisition release or scientific
qualification. Neither closed Q1 acquisition is replaced or rescored.

## Changes and compatibility

- The existing Gazebo include forwards `continuous_search_mode` to the existing
  controller launch. `rolling_gesc_v2` requests only `velocity_controller` in
  both normal and idempotent spawner paths. The unchanged Gazebo joint plugin
  remains the expected sole `/joint_states` publisher at its existing30Hz rate.
  `stationary_v1`, including a direct controller launch without a mode override,
  still requests both controllers. Invalid mode selection is rejected.
- The existing recorder validates the manifest and exact target/identity before
  deriving the rolling simulation contract. The retained resolved topic requires
  exactly `/turtlebot3_joint_state`, a singleton publisher and `single_stream`
  ordering. Active `velocity_controller` remains mandatory; only the redundant
  broadcaster is removed from the selected required-controller list. Shared
  manifest defaults still require both publishers and both controllers.
  Physical applicability is unchanged.
- A narrow existing V2 validation bug was corrected: the local
  `config = validate_mode_identity(...)` assignment overwrote the operational
  configuration with the stream descriptor. The later delay/consumer loops then
  saw no operational heartbeat override keys and silently skipped their checks.
  The descriptor now uses `stream_config`; the original operational loops are
  intact. Positive delayed/no-delay cases and metadata-delay/consumer-routing
  mismatches exercise those checks before source-contract derivation.
- Actual Humble executable resolution found the existing idempotent spawner
  tracked as100644, with the isolated installed path symlinked to that
  non-executable source. `ExecutableInPackage` therefore rejected the recovery
  path even though CMake already lists the script under `install(PROGRAMS ...)`.
  The authorized correction is mode-only100644→100755. Its bytes equal HEAD;
  content SHA256 remains
  `de1a3bb2d5cd1c15019b98f25e705c9e3bac55050c6f7e263ee5c7750c2e4c4e`.
  The installed symlink consequently resolves without a rebuild.

## Verification boundary

The new33-case fixture uses the actual Humble XML frontend, include substitution
resolution, source controller launch actions and executable/argument resolution.
It forbids execution of Node and ExecuteProcess actions. Because this milestone
has not rebuilt installed launch assets, the resolved control include loads the
current source module explicitly. Both modes and both spawner paths are checked;
the URDF plugin/topic/joint/rate are read from the unchanged source.

Recorder tests exercise exact publisher and controller readiness, target and
delay coupling, immutable base manifest inputs, saved YAML contracts, and actual
`record_run.run` resolution before any ROS/runtime start. Five cases call the
central `validate_run_directory` with synthetic clock/joint records and retained
resolved configuration. V2 matching ordered input passes its source checks;
regression or an extra publisher fails. Old correctly declared dual-publisher
input retains its bounded-clock ordering interpretation, while missing owners
fail and do not receive that exception. These partial synthetic records are
checker-wiring evidence, not a complete run. No current manifest is reloaded by
that validator, and no old bag was analyzed again.

All logs below are retained outside Git under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.

| Log | Result |
| --- | --- |
| `q1_single_source_v1.log` | exit1;70 passed,4 failed in6.21s. New test incorrectly treated Humble's descriptive source location string as substitution objects. |
| `q1_single_source_v2.log` | exit1;70 passed,4 failed in6.22s. Descriptive location text is not an expanded path; fixture now uses the public loader to resolve the actual include. |
| `q1_single_source_v3.log` | exit1;31 passed,2 failed in5.04s. Actual idempotent executable lookup exposed the missing executable bit described above. |
| `q1_single_source_v4.log` | exit0;33 passed in5.23s, including both actual recovery argument paths and all five central checker cases. |
| `q1_single_source_regressions_v1.log` | exit0;211 passed in12.73s. Existing recorder, old manifest/bag semantics, source/stream/lifecycle contracts, launch frontend and spawner checks. |

Exact environment for each command, with no source-package prepend:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
```

Final focused command (v3 used the same test command with its own log):

```bash
PYTHONPATH="${PYTHONPATH}:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_single_source_graph.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_single_source_v4.log 2>&1
```

Earlier v1/v2 commands used the same environment/90s timeout, listing
`test_q1_single_source_graph.py`, `test_v2_recording_contract.py`,
`test_observability_contract.py` and `test_controller_spawner_recovery.py` under
`ros2_ws/src/ros_esc/test/`, redirected to their respective versioned logs.

Exact regression command:

```bash
PYTHONPATH="${PYTHONPATH}:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_experiment_recording.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py ros2_ws/src/ros_esc/test/test_observability_contract.py ros2_ws/src/ros_esc/test/test_controller_spawner_recovery.py ros2_ws/src/ros_esc/test/test_q1_launch_frontend.py ros2_ws/src/ros_esc/test/test_v2_source_contract.py ros2_ws/src/ros_esc/test/test_v2_stream.py ros2_ws/src/ros_esc/test/test_v2_lifecycle_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_single_source_regressions_v1.log 2>&1
```

Context preflight `timeout30s tools/validate_phase_context.sh v2 implement`
(using the full implementation-package prefix from the repository root) passed.
`git diff --check` passed. No Gazebo, physical operation, build, acquisition,
checkpoint, commit or push was performed by this subtask. Necessary installed
launch-asset verification/rebuild and the controller-clock owner's independent
closeout remain parent-owned before any new acquisition release.

## Final source and log hashes

Paths below are repository-relative unless noted.

| Path | SHA256 |
| --- | --- |
| `ros2_ws/src/turtlebot3_rotating_sensor/launch/control.launch.py` | `d2754a53275f74d68900524f1e869be1cfe98fd56a3b5a23f5d60fe87d861e4d` |
| `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml` | `9e9e46b7c8e2200091e1a217331b8475799aea0b298ba706fadc01c4477e0c00` |
| `ros2_ws/src/ros_esc/ros_esc/experiment_recording/record_run.py` | `d835731a6bf6f3134abfd578e8b04fddb24cf858560958126a61b1a24bc37b7e` |
| `ros2_ws/src/ros_esc/test/test_q1_single_source_graph.py` | `c94193b3dc7ac3aeb51bd6a1c3ca0b6bbcb7bca03852f2d46ab79587d4a29987` |
| `ros2_ws/src/ros_esc/test/test_observability_contract.py` | `cf8db71504692beba1854844aedd10b5dc289bb9ed1e177d72a71b4245f8e9d6` |
| External `q1_single_source_v1.log` | `9dce52bd9e574472c4f9c615716d630f7f0e0f5e54938780635bb3cd57b0bd0d` |
| External `q1_single_source_v2.log` | `5c43fb2bee46d1f7458c6b3748e44d67d1715e4c0144ff1403b8cdfb9f12db04` |
| External `q1_single_source_v3.log` | `5264e52b2e41197c5317294ca326683acdfcfb045b4a3eaa0daf7645e4f4a969` |
| External `q1_single_source_v4.log` | `c9006a81c811131b722bcffa3474e3413ec090c74e0d303da52e3e62bea3eb02` |
| External `q1_single_source_regressions_v1.log` | `e6533a04d97398232c3a03d0afd392e443901680c82143c31868d61f6c6be760` |
