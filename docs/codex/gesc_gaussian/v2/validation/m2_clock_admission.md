# M2 clock admission — focused implementation evidence, 2026-09-09 UTC

The latest integrated implementation suite passed **433 tests in9.27s**, with
one retained warning. This includes the earlier158-check admission boundary,
upstream callback checks, seven regressions for clock advancement during
callback work, and the selected legacy/configuration/recording regressions.
It does not establish the full upstream DDS chain, natural-trajectory
direction quality, calibrated detector parameters, M3 readiness or pilot release.

The implementation follows [m2_source_clock_correction.md](../m2_source_clock_correction.md).
The closed [historical reference result](m2_reference_v1.md) remains
EVIDENCE_UNAVAILABLE. No historical replay or field calculation was repeated
for these checks. Configuration and launch checks are recorded separately in
[m2_clock_wiring.md](m2_clock_wiring.md).

## Reviewed behavior and corrections

The schema2 exact cost key identifies model-input acquisition time; actual
integer publication time remains distinct. Typed source, objective, direction
and observation envelopes use the matching descriptor schema version. Schema1
publication-key fixtures remain supported with their previous semantics.

`SourceSynchronizer` may retain source/support data up to0.5s ahead of its held
local clock, while preserving original callback receipts. It creates no
observation until the clock covers source time, actual cost publication and
both right brackets. Existing50ms interpolation limits remain. The explicit
admission stamp records clock coverage; it does not replace original receipts.
The selected current pose must itself already be clock-covered and fresh.
`RollingGesc` rejects output before admission or after source/input/pose expiry.

Independent review identified three concrete issues in the initial draft.
The subsequent source review confirms the following corrections:

- The filter stores first receipt per raw, provenance, augmented and objective
  component. The augmented contribution carries both constituent receipt
  extrema; the synchronizer combines them with raw/provenance/pose/encoder
  receipts. A late objective or augmented message is therefore included in the
  reported latest receipt. Duplicate delivery cannot refresh original age.
- Conflicting same-stamp pose/encoder support retains bounded tombstones across
  numerical resets. Retransmission cannot turn that stamp back into valid
  support; new stream context clears the old context's tombstones.
- Ordinary composer clock rollback clears pending input and reports the fault
  without permanently latching `origin_fault`. Fresh evidence can resume;
  an invalid or changed Timekeeper origin still requires a new run.

The reviewed schema2 source-key invalidation path also immediately discards
pending/numerical context, remembers the revoked key and suppresses late valid
copies. Filter repeats are idempotent. These tests exercise a source-owner
invalidation arriving before, during or after callback delivery. Already
published output cannot be retroactively withdrawn; the assertion is that
later delivery cannot restore validity or create another output for that key.
Actual upstream invalidation publication is a separate integration boundary.

The recording validator intentionally retains its strict quarantine: a valid
provenance message followed by an invalidation of that same source key makes
the recording's source evidence ambiguous. Successful bounded callback recovery
does not qualify such a recording. Future pilot dispatch still aborts on a
source-integrity failure; this correction does not weaken that gate.

## Exact commands and retained outcomes

All commands used `/home/mattb/dsim-lab` as working directory. The interface
build was executed as:

```bash
source /opt/ros/humble/setup.bash
timeout 180s colcon --log-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/log build --base-paths ros2_ws/src --packages-select ros_esc_interfaces --build-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/build --install-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install --symlink-install > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_clock_interfaces_v1.log 2>&1
```

Result: one package built successfully; package time15.1s, total15.4s.

Each test invocation first sourced:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
```

The first invocation accidentally replaced the sourced Python path:

```bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_clock_admission.py ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_clock_admission_v1.log 2>&1
```

Collection failed in0.13s with `ModuleNotFoundError: No module named 'nav_msgs'`.
No passing checks are credited to this invocation. The failed log is retained.

The corrected v2 invocation preserved the sourced Python path:

```bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_clock_admission.py ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_clock_admission_v2.log 2>&1
```

Result:76 passed in2.75s. After matching schema2 typed envelopes, v3 was:

```bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_clock_admission.py ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_clock_admission_v3.log 2>&1
```

Result:76 passed in2.78s. After review corrections and adding the pure rolling
regressions, v4 was:

```bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_clock_admission.py ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py ros2_ws/src/ros_esc/test/test_rolling_gesc.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_clock_admission_v4.log 2>&1
```

Result:150 passed in5.16s. With the additional source-key invalidation callback
cases, v5 was:

```bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_clock_admission.py ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py ros2_ws/src/ros_esc/test/test_rolling_gesc.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_clock_admission_v5.log 2>&1
```

Result:158 passed in5.15s. Repeated suite counts are not independent trials and
must not be summed. These tests use fake callback owners and the pure helper;
they are not the complete real upstream DDS fixture.

Two earlier pure-core invocations exist only in the executing parent's tool
output, with no retained log file or byte hash. The exact first invocation was:

```bash
timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_rolling_gesc.py
```

It failed collection with missing `ros_esc` because the source path was absent.
The corrected invocation was:

```bash
PYTHONPATH=ros2_ws/src/ros_esc timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_rolling_gesc.py
```

The parent reported67 passed in2.42s. This is ancillary tool-output evidence;
the retained v4/v5 logs include the same test file in their broader suites.

## Resolved receipt finding and integrated checks

After the admission v5 boundary, source review found that raw/provenance
adapters still passed a later clock read into their pure-core records after
preserving each component's receipt. The implementation now captures receipt
at callback entry for all four filter cost components and all three composer
inputs. Stored metadata and pure-core records use the same captured value;
current admission time is read separately. Seven additional cases deliberately
advance the clock during message copying and verify preservation: four filter
component cases and three composer input cases. This resolves the reported
within-callback receipt issue; the earlier fixed-clock v5 result remains
preserved without being relabeled as coverage of that case.

Each integrated invocation used the same ROS/isolated-overlay sourcing prefix
shown above. The exact test commands were:

```bash
ROS_DOMAIN_ID=175 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 180s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_rolling_gesc.py ros2_ws/src/ros_esc/test/test_v2_stream.py ros2_ws/src/ros_esc/test/test_v2_source_contract.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py ros2_ws/src/ros_esc/test/test_v2_detector_contract.py ros2_ws/src/ros_esc/test/test_legacy_behavior.py ros2_ws/src/ros_esc/test/test_observability_contract.py ros2_ws/src/ros_esc/test/test_clock_configuration.py ros2_ws/src/ros_esc/test/test_experiment_recording.py ros2_ws/src/ros_esc/test/test_v2_clock_admission.py ros2_ws/src/ros_esc/test/test_v2_upstream_clock.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_clock_integrated_v1.log 2>&1
```

Result:426 passed,1 warning in9.78s.

```bash
ROS_DOMAIN_ID=175 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 180s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_rolling_gesc.py ros2_ws/src/ros_esc/test/test_v2_stream.py ros2_ws/src/ros_esc/test/test_v2_source_contract.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py ros2_ws/src/ros_esc/test/test_v2_detector_contract.py ros2_ws/src/ros_esc/test/test_legacy_behavior.py ros2_ws/src/ros_esc/test/test_observability_contract.py ros2_ws/src/ros_esc/test/test_clock_configuration.py ros2_ws/src/ros_esc/test/test_experiment_recording.py ros2_ws/src/ros_esc/test/test_v2_clock_admission.py ros2_ws/src/ros_esc/test/test_v2_upstream_clock.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_clock_integrated_v2.log 2>&1
```

Result:430 passed,1 warning in8.92s, including the four filter receipt cases.

```bash
ROS_DOMAIN_ID=175 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 180s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_rolling_gesc.py ros2_ws/src/ros_esc/test/test_v2_stream.py ros2_ws/src/ros_esc/test/test_v2_source_contract.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py ros2_ws/src/ros_esc/test/test_v2_detector_contract.py ros2_ws/src/ros_esc/test/test_legacy_behavior.py ros2_ws/src/ros_esc/test/test_observability_contract.py ros2_ws/src/ros_esc/test/test_clock_configuration.py ros2_ws/src/ros_esc/test/test_experiment_recording.py ros2_ws/src/ros_esc/test/test_v2_clock_admission.py ros2_ws/src/ros_esc/test/test_v2_upstream_clock.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_clock_integrated_v3.log 2>&1
```

Result:433 passed,1 warning in9.27s, additionally including the three composer
receipt cases. All versions retain the same `invalid value encountered in sqrt`
warning in
`test_upstream_retransmission_conflict_regression_and_origin_are_explicit[sensor]`.
The implementation owner identified this as an inherited unused-quaternion
calculation; the warning is retained rather than suppressed. Passing these
checks does not qualify runtime numerical behavior outside their fixture scope.

The integrated suite includes actual ROS-node configuration fixtures under
isolated domain175, plus pure and controlled-callback tests. It does not run
the full upstream DDS transport test, which is recorded separately by its
owner. Counts across repeated versions must not be summed.

## Log byte provenance

All listed logs are under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.

| Log | Bytes | SHA256 |
| --- | ---: | --- |
| `m2_clock_interfaces_v1.log` | 109 | `cf2c0035434770789dba46e16db5fe755e24f6a907afaf09142e5da52888e294` |
| `m2_clock_admission_v1.log` | 2007 | `f826cda18ba8102c134ac9e487151242c49ec92efcad6faff3d7eb3f901c9394` |
| `m2_clock_admission_v2.log` | 179 | `281206dc0807d5630cbb6e831e5f3e2ecad03fee8332985b57a25d63cec91a5a` |
| `m2_clock_admission_v3.log` | 179 | `bffe4c29f8491b62196b64fd0585cbe188701da87b97c1de9fbe27c5d706f372` |
| `m2_clock_admission_v4.log` | 260 | `037d101a90d4734a8dbad82049548424d38e47452615ce2f8a9fa9a1e637394f` |
| `m2_clock_admission_v5.log` | 260 | `588a17b397d4f823e3d3551af82972055114247bbc5854d9e3323d294eeb7615` |
| `m2_clock_integrated_v1.log` | 808 | `e16e28e29f69255c69bad887f4b0a08982ec680c6cc7f7911041758f545a30f0` |
| `m2_clock_integrated_v2.log` | 808 | `cf0d01e78c09533635f8e4007aa5fbeb7e9cacd1667b26f2759d04f9734bf805` |
| `m2_clock_integrated_v3.log` | 888 | `6e6a313c46259410bdcfce484f565126c2a05c2fce722d3a9b7ae07610d52f09` |

This record was written by inspecting existing logs and source. Its author
did not rerun tests, start ROS/Gazebo, calculate fields or alter runtime source.
The final integrated source checkpoint and upstream transport outcome belong
to the enclosing M2 correction closeout.
