# R4 stationary recurrent protocol, interface and detector selection

SOURCE_BOUNDARY_PASS for this owner subset, 2026-09-10. The new stationary
recurrent wire, shared protocol, detector selection and launch forwarding pass85
focused/legacy tests. This is source/transport evidence; integrated Arm B
supervisor/fill/recording acceptance remains in the parent milestone's record.
No Gazebo, bag/model read, numerical retuning, comparison or historical-result
change was performed. Authority is the adopted
[pairing plan](../r4_stationary_recurrent_pairing_plan.md).

## Existing-owner changes

Added `StationaryRecurrentFillRequest.msg` with schema1 and the unchanged outer
stationary request field semantics, embedding full
`RecurrentConvergenceDiagnostics`. CMake registration and the interface README
name its distinct `/gesc_gaussian/v2/stationary_recurrent_fill_requests` topic.
The old request IDL, topic and diagnostic layout remain unchanged. Root's new
isolated interface build completed before tests and provides the generated type.

`stationary_fill_protocol.py` remains ROS-independent. Its new API is:

- `stationary_contract(metric_mode)`: selected request/diagnostic ROS type-name
  strings, canonical topics, parameter names and recording aliases;
- `stationary_diagnostic_errors(messages, ...)`: the existing checker keyword
  signature, dispatching from configured expected_metric_mode and rejecting a
  mismatched diagnostic type; absent selection retains the legacy route;
- `stationary_diagnostic_origin_errors(message, origin_ns,
  expected_metric_mode=None)`: the existing model history guard plus full
  persistence support for selected recurrent evidence;
- `stationary_request_errors(...)`: preserved public signature, exact selected
  request type and full nested checker/origin validation, with the original
  schema/hash/correlation/admission/deadline/target/candidate-evidence rules.

The existing `stationary_centroid_selected` API now returnsTrue for robust
simulation recurrent+stationary andFalse for recurrent+rolling. Its historical
name remains for callers; unsupported profile/clock/mode selections fail.
Centroid configuration checking stays specific to centroid modes. Recurrent
fixed fit/support/score/persistence constants remain in its existing checker;
no artificial centroid windows/epsilon fields or second formula are introduced.

The existing detector admits recurrent stationary selection with robust state
gating and simulation time. It reuses its existing AlgorithmState SEARCH-origin,
selected pose, readiness and source/clock guards. The numerical core is untouched.
The existing standalone path emits the new diagnostic directly without a moving
EpochBinding, PDE subscriber or moving DetectorConfirmation. Its mandatory
invalid-status heartbeat remains active outside SEARCH.

`gazebo.launch.xml` adds the new request parameter with its canonical default,
forwards old and new request parameters to the existing supervisor/GaussianFill
constructors, and forwards recurrent_diagnostics_topic to the supervisor. Legacy
defaults and node/controller/fill ownership remain unchanged. The other agent
owns those constructors and adapters; root owns recording/validation/analysis.

## Exact focused validation

Current AGENTS, handoff, plan/status and Git state were reread before edits.
`timeout --signal=INT --kill-after=2s 28s
docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh
v2 plan` PASS; root separately recorded implement-contextPASS for the adopted
plan. Scoped `git diff --check` PASS before testing.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/`.
Eleven selected source/interface/test files were pinned in
`detector_tests_v1_prepared.json` before dispatch. The one job used the new
generated overlay and reserved localhost-only ROS domain217:

```bash
set -o noclobber
timeout --signal=INT --kill-after=2s 118s env -u PYTHONPATH bash -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/environment.sh; export PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc:$PYTHONPATH; export ROS_DOMAIN_ID=217; export ROS_LOCALHOST_ONLY=1; exec /usr/bin/time -o /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/detector_tests_v1_time.txt -f "elapsed_seconds=%e exit=%x" python3 -m pytest -q ros2_ws/src/ros_esc/test/test_r4_stationary_recurrent_protocol.py ros2_ws/src/ros_esc/test/test_q5_stationary_fill_protocol.py ros2_ws/src/ros_esc/test/test_r4_stationary_recurrent_detector_transport.py' > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/detector_tests_v1.log 2>&1
```

PTY23264 exited0/reaped. Result85 passed in3.01s pytest time,3.52s measured wall,
within118+2s. All11 source pins remained unchanged, including the original old
StationaryFillRequest and frozen numerical core. No existing test was weakened
or modified in this owner subset. Log SHA256:
`414123a6c04770a33d4b87edd1de51371ccde36b205d122ddf5f530f03769789`.
Exact before pins and terminal/source audit remain in the prepared/receipt files.

The new protocol test module supplies reusable independent generated-wire
fixtures for the other owners. Nonzero Timekeeper origin is10^12ns; confirmed
model end is origin+60s while latest pose source is end+.009s and publication is
end+.1s. The request is published at origin+70s after original admission at
origin+60.2s. All three model branches survive actual CDR serialization with
their original evidence intact. Tests reject self-consistently rehashed invalid
model claims, cross-type/absent-mode evidence, admission refresh, partial
redesign targets and persistence before origin even when current model history
alone is later. A clean isolated Python import verifies that the shared protocol
imports neither rclpy nor generated ros_esc_interfaces.

The real DDS test supplies original pose/AlgorithmState/clock/readiness messages
to the actual standalone detector. Static confirmation occurs exactly once at
ROS31s for SEARCH epoch origin1s; persistence starts1s. It confirms without a
moving context or transaction and continues invalid outside-SEARCH heartbeats.
It does not establish empirical basin detection or a complete fill transaction.

Root retains build evidence and performs the combined source boundary after
the adapter and recording tests. No numerical core or lifecycle threshold change
is needed by this subset. Status/handoff/checkpoint remain root-owned.

## Final launch pose correction before the pairing archive

Independent actual-owner review found GaussianFill still selected its legacy
pose parameter for recurrent stationary mode. Under pairing plan step4 the
existing conditional now includes recurrent_geometry_v3. Actual Humble frontend
resolution verifies explicit and delayed algorithm pose topics reach detector,
supervisor and stationary GaussianFill; recurrent rolling retains its legacy
Gaussian pose parameter. No process/timer is executed by these frontend checks.

A separately retained job used the same overlay/domain and118+2s cap as above,
with `python3 -m pytest -q ros2_ws/src/ros_esc/test/test_r4_stationary_recurrent_protocol.py
ros2_ws/src/ros_esc/test/test_q7_launch_selection.py`. PTY20606 exited0/reaped:
64 passed in18.08s pytest /18.47s wall. This includes four new actual frontend
pose cases and the original Q7 selection regressions. Five selected source pins
(including frozen recurrent core) stayed unchanged. Exact preparation, log,
wall-time and terminal receipt are `detector_launch_v2_{prepared.json,log,time.txt,receipt.json}`
in the external pairing directory. This supplements the earlier85-test result,
with overlapping protocol tests explicitly included; it is not149 unique tests.
