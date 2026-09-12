# M3 controller — implementation validation, 2026-09-09 UTC

The final focused controller suite passes **58 tests in2.28s**, including a
real subprocess/DDS SIGINT test after moving VERIFY. The inherited focused
controller/interlock/signal/launch regressions pass19 tests, with34 deliberately
deselected. This validates the exercised controller behavior, not the complete
moving verification/fill pipeline, calibrated neighborhoods or the Gazebo pilot.

## Implemented ownership and safety

The existing controller remains the only command publisher. Its strict CLI adds
`--continuous-search-mode` (default `stationary_v1`) and `--v2-run-id`. Continuous
mode requires `robust_gaussian_v1`, simulation time and the existing shared run-ID
syntax. Root owns the matching nested launch entry.

One `_motion_authorized` predicate is used by the immediate state callback,
combiner and watchdog. Fresh selected-run VERIFY and initial DESIGN
(`previous_state_valid` and `previous_state=VERIFY`) take GESC alone, excluding
delayed supervisor commands. Redesign DESIGN identified by
`previous_state=ESCAPE_REPULSE` uses the inherited REPULSE combination. The
supervisor owner confirmed it retains escape weights/direction and the original
timeout; the controller neither starts nor extends that deadline. Enabled
ASSIST-exclusive command ownership and RECENTER behavior remain unchanged.

Continuous mode checks state source/receipt age, run/profile/validity, monotonic
state source time, source bounds relative to the selected origin, and pose/filter
source freshness. First callback receipts are captured before computation.
Clock rollback clears cached authorization and requires fresh inputs; changing
the Timekeeper origin latches invalidity until a new run. Saturation, zero on
invalid state/GOAL/FAILSAFE, exceptions, shutdown and the wall-monotonic recorder
interlock remain active. Authorization is rechecked after controller computation
before command publication. Legacy/default branches remain selectable.

## Exact commands and outcomes

Working directory `/home/mattb/dsim-lab`. Context preflight passed:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
```

Every pytest invocation below used a fresh shell with this prefix:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
```

```bash
ROS_DOMAIN_ID=178 DSIM_M3_TEST_ARTIFACT_DIR=/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_controller_v1 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_controller_motion.py -k "not process_sigint" > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_controller_v1.log 2>&1
```

Initial result:11 failed,40 passed,1 deselected in1.26s. All11 failures compared
ROS `array('d')` zero vectors directly with Python lists. The retained output
shows zero values; the fixture assertions were corrected to compare lists.
No runtime behavior was changed to resolve these failures.

```bash
ROS_DOMAIN_ID=178 DSIM_M3_TEST_ARTIFACT_DIR=/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_controller_v2 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_controller_motion.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_controller_v2.log 2>&1
```

Result:52 passed in2.30s. Focused inherited regression command:

```bash
ROS_DOMAIN_ID=178 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_legacy_behavior.py ros2_ws/src/ros_esc/test/test_deferred_signal_shutdown.py ros2_ws/src/ros_esc/test/test_observability_contract.py -k "controller or recording or supervisor_owned_assist or sigint or robust_startup or signal_request" > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_controller_legacy_v1.log 2>&1
```

Result:19 passed,34 deselected in1.02s. Subsequent source-origin and callback
receipt corrections added six meaningful regression cases. Final command:

```bash
ROS_DOMAIN_ID=178 DSIM_M3_TEST_ARTIFACT_DIR=/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_controller_v3 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_controller_motion.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m3_controller_v3.log 2>&1
```

Result:58 passed in2.28s. Repeated counts are not independent experiments and
must not be summed. Syntax/scoped diff checks passed:

```bash
python3 -m py_compile ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py ros2_ws/src/ros_esc/test/test_v2_controller_motion.py
git diff --check -- ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py
```

## Process-level shutdown scope

The real child process runs the existing controller module with the selected
GESC controller configuration and scoped `/m3_controller_test/*` input/output
topics in isolated ROS domain178. The fixture publishes clock, pose, state,
ready and filter-value inputs, observes nonzero VERIFY motion on the scoped
command topic, sends actual SIGINT, and checks exit0 plus the last received
zero command. Discovery/motion observation is bounded20s; termination
observation5s, process wait1s, final receive drain0.25s. Cleanup has finite
terminate/kill waits. This does not publish the robot's `/cmd_vel` or start
Gazebo/hardware. The child logs are empty because no diagnostics were printed;
the passing pytest assertions provide the shutdown observation evidence.

## Retained byte hashes

Paths below are relative to
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.

| Artifact | Bytes | SHA256 |
| --- | ---: | --- |
| `m3_controller_v1.log` | 14179 | `f351fe09f527121080c4b428c883b4d1db2ac147d1158c008d5ee2d27e8fe494` |
| `m3_controller_v2.log` | 99 | `57d58264cd2e7d8a3dbb125d50dfe7dc5e1deae3c7e3c1b017208c3406221d0b` |
| `m3_controller_v3.log` | 99 | `7b524368fdf96e8187075dd32bd79a301d8d1d648459a13751d2c6903cac3d72` |
| `m3_controller_legacy_v1.log` | 114 | `dd7e4bd39cc996a6ed03a17a8607514f3784ebb6dc14c481f0fed142e1d6bb98` |
| `m3_controller_v2/controller_sigint_1788940861225520710.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `m3_controller_v3/controller_sigint_1788940983014891032.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Source at this controller boundary:

| File | SHA256 |
| --- | --- |
| `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py` | `3573d7f445d8d19800d065c7eecc4d0b620a7793646aa000b346e63f7cba25e8` |
| `ros2_ws/src/ros_esc/test/test_v2_controller_motion.py` | `f6efd3bad98cbd85bd5ce00adf38a15b914fc06fd0ca7e7854e59e95d5bbd9d3` |

No Gazebo, field evaluator, historical replay, physical tree or hardware action
was involved. Integrated M3 validation, lifecycle transport and the final source
checkpoint remain the enclosing milestone's responsibility.
