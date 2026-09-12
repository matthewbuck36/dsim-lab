# M1 timed-centroid implementation validation

Status: IN PROGRESS. No Gazebo, moving-pipeline or full-plan acceptance claim.
Baseline HEAD is `3369cfc`; this record describes the current uncommitted V2
changes. The active details are in [M1 clarifications](../m1_implementation_clarifications.md).

## Interface and configuration checks

From `/home/mattb/dsim-lab`, build the new typed diagnostic in the isolated
source-qualified overlay:

```bash
source /opt/ros/humble/setup.bash
timeout 300s colcon --log-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/log build --base-paths ros2_ws/src --packages-select ros_esc_interfaces --build-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/build --install-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install --symlink-install --event-handlers console_cohesion+ > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m1_interfaces_build.log 2>&1
```

PASS, exit 0. The generated `CentroidConvergenceDiagnostics` preserves absolute
nanosecond source times and named metre units in a serialization round trip.

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_detector_contract.py ros2_ws/src/ros_esc/test/test_experiment_recording.py -k 'v2_detector_contract or manifest_has_unique' > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m1_contract_tests.log 2>&1
```

PASS: 30 tests, 68 deselected, 0.72 s. Covers finite/positive tuning, unknown
mode and ungated-mode rejection, unchanged launch default, selected delayed-pose
routing, actual typed serialization, and simulation-only recorder inclusion.
Inherited manifest checks also pass. This does not prove selected V2 run
completeness; conditional checks remain required before the pilot.

```bash
timeout 180s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_scenario_schema.py ros2_ws/src/ros_esc/test/test_v2_detector_contract.py -k 'v2_detector_contract or schema_v8_rejects_count_topology or schema_v13_resolves_four_v8_10 or schema_v14_resolves_topology_bound_secondary or schema_v14_resolves_v8_12' > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m1_scenario_regressions.log 2>&1
```

PASS: 43 tests, 188 deselected, 21.21 s in the same sourced overlay. Checks the
inherited selected primary/secondary/interior-anchor scenario contracts and
counted-candidate rejection gates alongside V2 tuning. The parser only relaxes
the inherited dwell requirement when the explicit timed-centroid mode replaces
it; no selected V1 scenario or failed artifact was changed.

## Selected-mode recording checks

The existing recorder now promotes the typed diagnostic to required when the
target selects `centroid_windows_v2`, validates its resolved topic/type, and
retains the inherited optional/default behavior. The existing completeness
validator checks six-window support, metre-score consistency, time ordering,
validity flags and once-per-epoch confirmations. These internal checks do not
replace replay against the recorded trajectory.

```bash
timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_detector_contract.py ros2_ws/src/ros_esc/test/test_experiment_recording.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m1_recording_tests.log 2>&1
```

PASS: 109 tests in 2.55 s, same sourced isolated overlay. Includes all existing
recorder regressions and rejection of incorrect support/score/radius/identity
claims. Cross-topic runtime readiness consistency and final mode/parameter
binding remain required before the pilot.

## Core, node and ROS transport

```bash
timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_centroid_windows.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m1_core_tests.log 2>&1
timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_convergence_detector_policy.py ros2_ws/src/ros_esc/test/test_centroid_windows.py ros2_ws/src/ros_esc/test/test_search_epoch_history.py ros2_ws/src/ros_esc/test/test_legacy_behavior.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/centroid_node_and_regressions.log 2>&1
```

PASS: 62 pure-core tests in 0.23 s (root rerun); 130 node/core/history/legacy
regressions in 2.77 s. Core tests cover exact 18 s onset, sampling equivalence,
interpolated support/counts, circles/oscillations/drift/large loops/spirals,
strict score/inclusive radius boundaries, once-per-epoch resets and numerical/
memory/work limits. Node tests cover source/state/readiness freshness, actual
SEARCH transitions versus invalid-message recovery, and unchanged legacy arrays.

```bash
ROS_DOMAIN_ID=121 timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_centroid_detector_transport.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m1_transport_tests.log 2>&1
```

PASS: one transport test in 0.77 s, sourced isolated overlay. This starts the
actual detector and a test publisher/subscriber node in an isolated ROS domain.
It delivers `/clock`, readiness, typed state and the selected odometry stream
through ROS, receives typed diagnostics through ROS, and observes exactly one
confirmation after 18 simulated seconds. No PDE publisher/subscription, Gazebo
process, physical graph or motion command is involved. Captured diagnostics
pass the current internal completeness checks. This establishes node routing
and timing, not supervisor/fill integration or improved closed-loop behavior.

## Review corrections and final focused checks

The recorder review found malformed-duration overflow, impossible sample/support
claims, missing source/run binding, and insufficient coverage from a single
startup diagnostic. The existing validator now rejects those cases, binds the
observed supervisor UUID (currently distinct from the recorder run ID), and
checks selected diagnostic coverage in simulation time, including interior
gaps. Inherited runs retain their original requirements.

```bash
PYTHONPATH="ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" timeout 180s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_detector_contract.py ros2_ws/src/ros_esc/test/test_experiment_recording.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m1_recording_review_v1.log 2>&1
```

PASS: 123 tests in 2.71 s, isolated overlay. Includes a run-directory validator
integration test and invariance to simulation/wall-time scaling.

A deterministic node test reproduced lost authorization after the numerical
core latched its event but before typed publication. The failure is retained
in `centroid_publish_race_before.log`. The correction invalidates support and
keeps the node publication latch available; only complete newly authorized
support can publish. A publisher exception also leaves that latch unconsumed.

```bash
timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_convergence_detector_policy.py ros2_ws/src/ros_esc/test/test_centroid_windows.py ros2_ws/src/ros_esc/test/test_search_epoch_history.py ros2_ws/src/ros_esc/test/test_legacy_behavior.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/centroid_publish_race_regressions.log 2>&1
ROS_DOMAIN_ID=121 timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_centroid_detector_transport.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m1_transport_review_tests.log 2>&1
```

PASS: 132 regressions in 2.99 s and one actual ROS transport check in 0.74 s.
No Gazebo or hardware was launched. Installed launch bytes in the isolated
overlay match the edited source; launch SHA-256:
`da5df061758a73ac72da203a686d7fa428ac3ae6251503b36a6747b717be1519`.

Independent label publication had a retained scalar-serialization failure;
see [publication record](m1_label_publication_failure.md). The subsequent v1a
manifest is intact, but its six modeled basins do not satisfy the frozen
qualification criteria. That is an unavailable truth-label denominator, not
evidence that the robot has no basin or that a detector passed.

## Still required for M1

- Close the original calibration version with its exact failure evidence.
- Freeze and validate a separately justified corrective version before
  selecting any configuration or advancing to the pilot.
- Update the acceptance ledger and material checkpoint at each boundary.
