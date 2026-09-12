# Q1 simulation source correction — validation boundary

Source/validation outcome: PASS. Empirical qualification remains outstanding;
the prior recovery1 field run remains CLOSED INCOMPLETE. The controlling
amendment is `../q1_simulation_source_plan.md`.

## Corrected behavior and evidence

- The existing controller queues near-future stamped pose, state and filter
  inputs until covered by its local clock, retaining fresh covered inputs and
  original ROS/steady receipts. Pose acquisitions remain immutable; distinct
  same-tick state/filter publications retain singleton publication order.
  Exact repeats use canonical payload fingerprints, including unavailable NaNs,
  and do not refresh receipts. Stop states fence motion immediately. Strict
 500ms-or-smaller freshness, source ordering, bounded queues, origin/clock reset,
  moving VERIFY/DESIGN, escape ownership and final zero remain checked.
- Final controller owner suite passes103 checks in3.44s:58 moving/SIGINT,
 44 new admission cases and one actual ROS transport case. The transport case
  covers27 leading poses over nine held100ms clock ticks, future state/filter
  input, excessive-future stop and held-clock steady expiry. Nineteen selected
  legacy regressions pass in1.08s after the final receipt-timing restoration
  (34 other tests intentionally deselected). `q1_controller_clock.md` and its
  manifest retain exact commands, source hashes and earlier failed checks.
- Rolling simulation starts velocity control with the existing joint-state
  plugin as sole publisher. Both ordinary/idempotent launch paths and the
  matching selected recorder readiness/publisher contract pass33 checks5.23s;
 211 existing recording/launch/source/interface regressions pass12.73s.
  `q1_single_source_graph.md` preserves exact checks and historical-bag semantics.
- The recorder's operational config local-variable shadowing is corrected so
  actual delayed-input/consumer-coupling validation executes before deriving the
  selected graph. The existing idempotent spawner receives only its missing
  executable bit; script bytes remain unchanged. Default/legacy graph and the
  base topic manifest remain unchanged.

These are implementation checks, not detector sensitivity or direction accuracy.
Earlier failed fixtures, runtime attempts and logs are retained separately.

## Combined source verification

After sourcing base Humble and the isolated local overlay:

```bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 180s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_*.py ros2_ws/src/ros_esc/test/test_v2_controller_motion.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_source_correction_integrated_v1.log 2>&1
```

Result:401 passed in41.90s, exit0. This includes current acquisition-path,
entry-point, single-source, controller, source-adapter, study/reference, recorder
and actual frontend checks. Counts above overlap; do not sum them as independent
experiments. Log SHA256:
`9745af988305ad82046b8dacdf3e27e29f5c309a47dfd63e444c9b611d982ca4`.

From base ROS, bounded incremental build:

```bash
source /opt/ros/humble/setup.bash
timeout 180s colcon --log-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/log build --base-paths ros2_ws/src --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor --build-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/build --install-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install --symlink-install --event-handlers console_cohesion+ > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_source_correction_build_v1.log 2>&1
```

Result:three packages finished2.21s, exit0. Log SHA256
`b8a15c47caacd5b7454136660cbd0284d71d42b6a302b49297e646ffd95174f5`.
A30s bounded no-node Python check verifies six selected installed assets against
source: Gazebo/control launch files, URDF, empty world, Q1 scenario and topic
manifest. It verifies the installed spawner is executable with unchanged bytes
and loads all21 console targets while forbidding ROS node initialization.
Receipt `builds/initial/q1_source_correction_installed_v1.json`, SHA256
`d16dc4687f1a4e31dfdc557e07f08c82157edb895c6d441820fb6f38e4e9e0b6`.

Actual installed `timeout 30s ros2 launch turtlebot3_rotating_sensor
gazebo.launch.xml --show-args` exits0, saved in
`builds/initial/q1_source_correction_launch_v1.log`, SHA256
`49695eb54899e2c725aa3add8ccb183dcdefd7c868c21c115a08c37a4a20564f`.
No Gazebo was started by these checks. Context and diff checks pass.

## Next acquisition boundary

`../q1_acquisition_recovery2_plan.md` preserves the method and four deterministic
inputs under new IDs/root. Its routing/lineage guards pass28 checks in2.08s,
`builds/initial/q1_recovery2_paths_v1.log`, SHA256
`a40593eea89d6c1286077ed1c027b10f47d7b1ccdc386ef5790a7fb47cd2246e`.
They are also included in the401-check integration. An exact contract and verified
checkpoint/release remain mandatory before dispatch. Earlier acquisitions are
never overwritten or rescored as passing, and confirmation remains unopened.
