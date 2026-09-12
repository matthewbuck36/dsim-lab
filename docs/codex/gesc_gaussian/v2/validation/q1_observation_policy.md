# Q1 observation-only supervisor — 2026-09-09

Status: source and focused/regression checks complete for parent integration.
No Gazebo, acquisition, parameter qualification, M4 release, physical execution,
commit or push. The Q1 plan remains the acquisition authorization boundary.

## Source contract

The existing supervisor accepts startup-only ROS parameter
`v2_qualification_observation_only`, default `false`, declared read-only. Its
immutable state-machine field is `qualification_observation_only`. True requires
moving verification; existing node identity validation also requires
`robust_gaussian_v1`, `rolling_gesc_v2` and simulation time. Invalid types and
incompatible startup combinations fail. The moving configuration event records
the effective boolean as the same named numeric value (0 or 1).

`MovingSupervisor.confirmation()` returns before candidate allocation or SEARCH
epoch consumption when enabled. Direction/raw evidence and state/epoch
publication continue. The only numerical state-machine gate is at entry to
`_step_search()`: it clears convergence dwell and ignores direct/dwell convergence.
Earlier `step()` clock, explicit stop, controller, pose/source and recovery checks
remain authoritative. Other state policies and weights are unchanged. Thus a
safety recovery can leave SEARCH; Q1 must record that interval honestly.

Positive finite `v2_candidate_radius_m` and `v2_candidate_epsilon_m` remain
mandatory. The frozen Q1 inactive values, 0.75m and 0.15m, are used in these tests
without a calibration claim. No Gaussian request, candidate snapshot or GOAL
decision is authorized by these values under observation policy.

Only three runtime owners changed relative to the immutable M3 archive: one
boolean/config validation and SEARCH guard in `state_machine.py`; parameter,
read-only descriptor, forwarding and configuration-event entry in
`supervisor_node_script.py`; one pre-allocation guard in `v2_supervisor.py`.
A read-only comparison against the three archived tar members verified this
boundary. The archive itself and M3 validation records were not changed.

## Exact checks and evidence

Run from `/home/mattb/dsim-lab`. Context preflight passed:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
```

First focused run, exit 0: **25 passed in 3.48s**.

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
ROS_DOMAIN_ID=186 PYTHONPATH="ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_observation_policy.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_observation_policy_v1.log 2>&1
```

Relevant legacy/M3 regression run, exit 0: **270 passed in 21.04s**.

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
ROS_DOMAIN_ID=186 PYTHONPATH="ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_observation_policy.py ros2_ws/src/ros_esc/test/test_state_machine.py ros2_ws/src/ros_esc/test/test_supervisor_integration.py ros2_ws/src/ros_esc/test/test_v2_supervisor.py ros2_ws/src/ros_esc/test/test_v2_controller_motion.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_observation_policy_regressions_v1.log 2>&1
```

New coverage includes default/explicit-false direct and dwell transitions; strict
boolean/scope and still-required neighborhood startup; repeated valid PDE and
centroid confirmations with complete informative three-cycle evidence, including
known-source counts one and two; no consumed IDs/epoch/preparation/snapshot;
SEARCH weights/heartbeats; clock rollback, stop, controller, pose/source faults;
bounded recovery and timeout. The false-policy controls enter the inherited
VERIFY then GOAL/DESIGN path on identical valid evidence. Actual SupervisorNode
callback tests use real ROS message classes with controlled ROS time and collected
publisher output, retain real steady time, verify parameter immutability, emit
one effective configuration event, and assert stop plus explicit shutdown zero.
These new callback tests are not claimed as a new end-to-end DDS acquisition.
The unchanged integration/controller regressions provide their existing transport
coverage. No failed Q1 policy test attempt occurred.

`git diff --check` passed for the assigned tracked source files. The new test and
record are additive; parent owns launch/schema/runner wiring and pre-acquisition
checkpoint. `ParameterDescriptor` is imported from `rcl_interfaces.msg`; parent
was notified to declare the direct runtime dependency in the package manifest.

## Frozen focused boundary

| File | SHA256 |
| --- | --- |
| `ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py` | `b2fb79199dfd7ca901c59aaab85f115ce65847fb42de71bd104d3d40e7068e6a` |
| `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py` | `9e1f41ecd0cb62ff30869500638ae1fdc77da5c1ca900a95d2069258b034e4d1` |
| `ros2_ws/src/ros_esc/ros_esc/supervisor_node/v2_supervisor.py` | `ef72def465cdd7c61cd22c66f54a35e0b57f2c0a7b36f599dc1b1d44b137e91c` |
| `ros2_ws/src/ros_esc/test/test_q1_observation_policy.py` | `7d2e4b58a2482db9ed4b05465e68a91aa17cde6061e25e783bab41b70c6fd1cc` |
| `q1_observation_policy_v1.log` under the retained build directory above | `dbf20f1c1eadba46380d5e37294e9e545e443d5592d93621f11254c1fb7c1bc9` |
| `q1_observation_policy_regressions_v1.log` under the same directory | `3a1987c1a18083bb2410e3ff265805747cc2fa77e92799ec65152f2ea0c707a1` |

M3 archive manifest remains
`0e144f64d392741f5388a2eaef4c0b98dd1f9068669eb1de1b3533e644602920`.
Archived prior owner hashes are respectively
`63a2e0a57561e6d29f5bcc465ad03b715b523d4f33ffb70a4571c42f6ef962f1`,
`45a9c825bd680ac1256a18250d2143b6d5cf2cf8078af5a100a90f9040bf6241`, and
`a661a2513e2c158ce426a391fa19dde1c62c1877bb10538136a1f143ed400912`.
