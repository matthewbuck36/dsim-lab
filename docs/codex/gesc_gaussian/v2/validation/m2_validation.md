# M2 implementation validation — in progress

Source contract: `../m2_plan.md`. Prospective reference protocol:
`../m2_reference_plan.md`. This record does not close M2 or select an M1 detector
setting. No M2 Gazebo or physical experiment has run.

## Source scope

The opted-in path now has source/stream identity, evaluated-transform
provenance, a selected-stream delay relay, atomic augmented-objective receipts,
source-time synchronization and rolling world-frame GESC. Existing source,
modified-cost, filter, supervisor identity, launch, runner and recorder owners
remain. Legacy mode is still default. M3 moving-state authorization and fill
transactions are not implemented by this milestone.

The composer requires the selected raw message, source breakdown and provenance
before evaluating corrections at the captured sensor location. It records
integer composition time and the active objective law. The filter additionally
joins unchanged augmented output to those typed receipts, uses actual world
phase projected into the synchronized body frame, and preserves the selected
custom filter sign/gains. Confidence and fallback follow the frozen contract.

Review corrections before empirical qualification:

- Clear both adapter and numerical pending state after a source fault, so a
  partial join cannot survive only on one side.
- Recheck source/pose/state freshness after filter computation, at publication.
- Report the actual reconstructed demodulation phase in inherited filter
  diagnostics through an additive optional argument; preserve legacy calls.
- Retain oldest and latest contributing receipt times, and check both for
  output freshness.
- Preserve actual publication/composition integer timestamps. Permit only the
  declared floating representation bound for legacy timestamp consistency;
  cost joins still use exact unchanged floating keys.
- Reject malformed timestamps and bounded queue overflow explicitly; keep
  objective configuration and geometry attached to each composed sample.

## Build and focused checks

All commands run from `/home/mattb/dsim-lab`. ROS commands source
`/opt/ros/humble/setup.bash`, then
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash`.
No normal stale install overlay is used as qualification.

```bash
timeout 180s colcon --log-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/log build --base-paths ros2_ws/src --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor --build-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/build --install-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install --symlink-install
```

PASS, three packages, both initial four-message build (`m2_build_v1.log`) and
the oldest-receipt additive field build (`m2_build_v2.log`). Logs are under the
same `builds/initial/` directory.

```bash
PYTHONPATH=ros2_ws/src/ros_esc timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_rolling_gesc.py ros2_ws/src/ros_esc/test/test_centroid_windows.py
```

PASS: 129 tests in 2.65 s (67 M2 core checks plus 62 centroid regressions).
Includes exact joins, CW/CCW/base turns, source-time quadrature, actual sector
counts, all-pair cycle agreement, weak signals, reversals, caps and freshness.

```bash
timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_legacy_behavior.py ros2_ws/src/ros_esc/test/test_observability_contract.py ros2_ws/src/ros_esc/test/test_clock_configuration.py
```

PASS: 105 tests in 2.84 s, `builds/initial/m2_runtime_v3.log`. Uses actual
generated ROS messages with controlled callback/clock fixtures, including all
24 cost-topic orders, no early raw admission, exact correction geometry,
same-objective VERIFY preservation, escape blend prohibition and stale safety.
This is not DDS transport or Gazebo evidence.

The same 105 checks pass in 3.02 s after the additive oldest-receipt wire field,
`builds/initial/m2_runtime_v4.log`.

After the final stream-binding, recorder and wire changes, the integrated
non-DDS check passes **361 tests in 8.39 s**:

```bash
ROS_DOMAIN_ID=175 PYTHONPATH="ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" timeout 180s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_rolling_gesc.py ros2_ws/src/ros_esc/test/test_v2_stream.py ros2_ws/src/ros_esc/test/test_v2_source_contract.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py ros2_ws/src/ros_esc/test/test_v2_detector_contract.py ros2_ws/src/ros_esc/test/test_legacy_behavior.py ros2_ws/src/ros_esc/test/test_observability_contract.py ros2_ws/src/ros_esc/test/test_clock_configuration.py ros2_ws/src/ros_esc/test/test_experiment_recording.py
```

Log: `builds/initial/m2_integrated_contracts_v1.log`. Domain 175 isolates actual
ROS-node fixtures in the legacy tests; the new runtime callback tests use
controlled clocks. No behavior was tuned from field results.

```bash
ROS_DOMAIN_ID=122 PYTHONPATH="ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" timeout 120s python3 -m pytest -q -s ros2_ws/src/ros_esc/test/test_v2_direction_transport.py
```

PASS: one real DDS transport test in 3.46 s,
`builds/initial/m2_direction_transport_v3.log`. Actual `ModifiedCost2D` and
`CustomFilter` process 301 observations spanning 15.1 s of simulation time,
with 301 objective receipts and outputs and 245 qualified diagnostic messages
(diagnostic count is not an independent trial count). Withheld raw input for
0.1 s cannot be bypassed by earlier typed source/provenance. Gaussian correction
uses the observed 0.18 m sensor location despite a deliberately wrong cached
position. SEARCH-to-VERIFY keeps same-objective cycles; stale cost cannot
produce a fresh filter output even when pose/state remain fresh. No controller,
base motion or Gazebo is part of this test. Earlier transport harness failures
remain at `m2_direction_transport_v1.log` and `m2_direction_transport_v2.log`:
separate DDS callback/timer delivery assertions needed explicit waits; these
failures required no runtime source correction.

Earlier retained runtime logs: `m2_legacy_runtime_v1.log` (68 inherited checks
pass), `m2_runtime_v1.log` (two test fixture list-versus-ROS-array comparisons
failed; 32 pass), `m2_runtime_v2.log` (one misplaced test assertion failed;
104 pass). Corrected fixtures do not change experimental labels or targets.

Reference helper and analyzer fixtures: 91 reference/M1 replay tests pass in
5.68 s, `builds/initial/m2_reference_full_tests_v1.log`, with a 180 s bound.
Analytic cosine parity exercises the actual pre-update Euler filter against
Hd. This includes no new field-model or retained 192-anchor calculation.

Final helper/source/runner/recorder contracts:

```bash
timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_stream.py ros2_ws/src/ros_esc/test/test_v2_source_contract.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py ros2_ws/src/ros_esc/test/test_v2_detector_contract.py ros2_ws/src/ros_esc/test/test_simulation_disturbances.py
timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_experiment_recording.py ros2_ws/src/ros_esc/test/test_recording_integration.py ros2_ws/src/ros_esc/test/test_observability_contract.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py
timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_scenario_runner.py -k 'launch or metadata or unique_run_ids or dry_run'
timeout 45s env ROS_DOMAIN_ID=173 python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_source_transport.py
```

Respectively: 128 PASS in 2.62 s (`m2_evidence_contract_tests_final.log`);
101 PASS / 1 SKIP in 3.33 s (`m2_recorder_legacy_tests_final.log`); 72 PASS /
123 deselected in 21.41 s (`m2_runner_focused_tests.log`); one DDS test PASS in
0.64 s (`m2_source_transport.log`). All logs are under `builds/initial/`.
The skip is `test_short_visible_gazebo_recording`, which requires
`DSIM_RUN_GAZEBO_RECORDING_TEST=1`; that release was deliberately not enabled.

The source DDS test instantiates full `CostFunction` and
`SimulationDisturbanceNode` owners, sending Timekeeper, transform and clock
messages. Only the model/noise functions use deterministic analytic fixtures;
actual source/provenance serialization and delayed ROS delivery are exercised.
This is no light-field or Gazebo dynamics result. ROS parameter parsing also
verifies the launch JSON/block-scalar roundtrip. Recorder validation recomputes
cycle agreement/variability, checks observed pose/encoder brackets against
selected recorded streams and checks separate source/current-pose/oldest-input
freshness; it does not equate bag receipt order with DDS callback order.

Earlier focused contracts: 105 pass in 1.61 s at
`builds/initial/m2_evidence_contract_tests.log`.
One broader source/runner/schema attempt reached its 60 s bound after over 290
progress items without completion; retained `m2_source_runner_tests.log` is not
a passing suite claim. The focused affected checks above subsequently completed.

The final reference review fixes pass 96 reference/M1 replay checks in 5.72 s,
`builds/initial/m2_reference_review_tests_v1.log`, using the same isolated ROS
overlay and `PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH` with
an outer 180 s timeout. Fixed target selection uses model-input time; binding
checks recorded launch/configuration; evidence availability is excluded from
objective identity; invalid runtime outputs remain missing; phase plateaus
use the runtime's first-arrival rule. This test boundary preceded the actual reference job recorded below.

## Fixed reference outcome and source-clock diagnosis

The reference job is closed as **EVIDENCE_UNAVAILABLE**. See
[m2_reference_v1.md](m2_reference_v1.md) and its complete byte-hash manifest.
The corrected launcher exited0 in79.666s; all192 slots lacked causal anchors
because all8 stream normalizations aborted on timestamp conflicts. No angular
error, availability, lag or field value was measured. Preserve all211 receipts
and earlier launcher failures. Do not rerun or reinterpret this fixed version.

Read-only first-bag forensics used the existing19801 recording, preserving
SequentialReader/SQLite receipt order. Its retained script ran under timeout90s
in6.808s, exit0. Encoder and transform each have35,147 conflicting adjacent
same-stamp readings, including34,937 after readiness, with zero regressions.
Pose stamps are strictly increasing. Full retained diagnosis and command:
`/home/mattb/Experiments/GESC-Gaussian/v2/diagnostics/m2_timestamp_19801_v1/`;
`diagnosis.json` SHA256
`55c00562eddca3482018f90f9293a2f01970b05133d14f61c472d3001035b15e`.

Source inspection finds the current encoder discards JointState.header.stamp;
the sensor-pose owner discards encoder source time; the cost owner restamps
again. The recorded Gazebo clock publication rate is10Hz. Current opt-in M2
still traverses those upstream owners, so the strict new synchronizer cannot
assume its synthetic unique-stamp fixtures establish runtime readiness.
The existing source DDS fixture begins at transform messages and the direction
fixture injects encoder/provenance directly. Their passing results remain
valid within that scope, without covering this newly identified integration gap.

## Pending evidence

Freeze a bounded source-clock correction and test the actual upstream owners,
including repeated local clock values and source/header ordering. No historical
retiming, source sorting, duplicate arbitration by outcome or repeated fixed
reference calculation is authorized by this diagnosis. Preserve all failures.

Retained trajectories lack exact new provenance and remain unsuitable for an
exact M2 transport claim. Neither proxy replay nor synthetic/DDS tests establish
closed-loop performance, calibrated detector neighborhoods, M3 lifecycle
correctness or M4 pilot targets.

## Source-clock correction boundary

The separately recorded correction is implemented and reviewed. See
[m2_clock_wiring.md](m2_clock_wiring.md),
[m2_clock_admission.md](m2_clock_admission.md),
[m2_upstream_clock.md](m2_upstream_clock.md), and
[m2_upstream_transport.md](m2_upstream_transport.md) for exact commands, retained
failures, final source/log hashes and evidence limits.

The final integration command extends the original ten-file list above with
`test_v2_clock_admission.py` and `test_v2_upstream_clock.py`, retains domain175
and timeout180s, and uses
`PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH` after sourcing
the same ROS/isolated overlay. Result:433 PASS/1 inherited unused-quaternion
warning in9.27s, `builds/initial/m2_clock_integrated_v3.log`. Interfaces built
successfully in15.4s. The final full upstream DDS fixture uses domain176 and
timeout120s:2 PASS in8.00s with3 inherited warnings,
`builds/initial/m2_upstream_transport_v8.log`. All checked geometry is finite.

The fixture observes453 ordinary source acquisitions sharing151 actual
publication stamps,186 qualified observations after at least3complete cycles,
and one fresh instantaneous recovery after two deliberate source invalidations.
These counts are transport observations, not independent research trials.
Upstream tombstone suppression is exercised through actual JointState replay;
late raw/objective/provenance resurrection is exercised by reordered adapter
fixtures. No previously failed reference or field calculation was rerun.

Original clock receipts can precede source time; schema2 waits for source,
publication and bracket clock coverage and records admission separately. The
first clock read at each component callback is retained through copies/hash
work. Known disputed keys are explicitly invalidated and cannot be restored by
late packets. Runtime recovery does not waive the strict recorder quarantine of
an ambiguously sourced recording.

M2 source implementation and its finite historical evaluation are concluded.
Scientific direction qualification remains unavailable. Calibrated detector
parameters, moving-pipeline integration, prospective direction comparison and
the16-run pilot remain outstanding. The full user goal is not complete.
