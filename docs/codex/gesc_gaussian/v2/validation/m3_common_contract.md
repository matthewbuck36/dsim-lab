# M3 common interfaces, epoch binding and wiring — 2026-09-09 UTC

Implementation is in progress under `../m3_plan.md`. These are bounded synthetic
source/transport checks, not neighborhood calibration or closed-loop evidence.

Root-owned changes extend existing PDE/detector owners, common typed interfaces,
canonical hashing, launch selection, scenario validation and recorder registration.
The PDE wrapper retains actual admitted input support and unchanged legacy
transport-filter arithmetic. It never assigns nominal PDE bins exact source
timestamps. Both detector modes echo the supervisor-owned epoch; local centroid
epochs remain diagnostic. Lifecycle protocol1 nests acquisition stream schema2.

All logs below are retained under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.
Before each pytest command:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
```

## Interface build

```bash
timeout 180s colcon --log-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/log build --base-paths ros2_ws/src --packages-select ros_esc_interfaces --build-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/build --install-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install --symlink-install
```

`m3_interfaces_v1.log`: first5 messages, PASS19.3s; retained overlay-override
warning from sourcing the old isolated interface overlay before rebuilding.
`m3_interfaces_v2.log`: added PDE wrapper and confirmation history-kind fields,
PASS19.3s. The second command sources base ROS only. Imports of rebuilt types pass.

## Epoch and inherited detector checks

```bash
ROS_DOMAIN_ID=183 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_epoch_binding.py ros2_ws/src/ros_esc/test/test_centroid_windows.py ros2_ws/src/ros_esc/test/test_convergence_detector_policy.py ros2_ws/src/ros_esc/test/test_v2_detector_contract.py
```

`m3_epoch_binding_v1.log`:163PASS2.31s. After explicit PDE invalidation and its
late-duplicate regression, `m3_epoch_binding_v2.log`:164PASS2.21s. Coverage includes
first-receipt preservation, future clock admission, actual PDE numeric parity,
changed origin, authoritative epoch vs local epoch, rejected delayed/tampered
history and once-per-epoch confirmations. Synthetic neighborhoods are explicit.

## Common hashes, launch and recorder contracts

```bash
ROS_DOMAIN_ID=183 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_lifecycle_contract.py ros2_ws/src/ros_esc/test/test_v2_stream.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py
```

`m3_lifecycle_wiring_v1.log`:86PASS/5FAIL2.10s, all fixture expectations: XML
normalizes attribute newlines, two aliases were guessed incorrectly, and the
old exact consumer-list assertion omitted3new owners. Corrected those explicit
expectations; `m3_lifecycle_wiring_v2.log`:91PASS1.95s. Coverage binds actual M2
composer-law digest, source/admission/first-state snapshot hashing, both wire
protocols, positive explicit neighborhood requirements, nested controller flags,
and event registration without requiring a candidate in a constant field.

## Actual PDE/detector DDS

```bash
ROS_DOMAIN_ID=184 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_epoch_transport.py
```

The actual PDE and detector nodes run in an isolated domain; a fixture publishes
only clock, selected pose, Timekeeper, AlgorithmState and epoch context. Each
metric confirms once in each of2authoritative epochs with its retained units and
distinct centers. Synthetic faster window/dwell settings test message routing,
not scientific latency. No controller, command topic, Gaussian or Gazebo is run.

`m3_epoch_transport_v1.log`:2FAIL0.29s before ROS initialization because bare
JSON was parsed as a YAML mapping. Corrected the fixture to the same YAML block
scalar string used by launch. `m3_epoch_transport_v2.log`:2PASS0.57s. After PDE
invalidation source changes, `m3_epoch_transport_v3.log`:2PASS0.57s.

Source hashes and integrated M3 evidence will be frozen at the milestone
checkpoint after supervisor/fill/recording integration, not claimed here yet.

## Integrated review and bounded corrections

`m3_common_integrated_v1.log`:256PASS3.85s, same environment/domain183/timeout120s;
files `test_v2_epoch_binding.py test_v2_lifecycle_contract.py test_v2_stream.py
test_v2_recording_contract.py test_centroid_windows.py
test_convergence_detector_policy.py test_v2_detector_contract.py` under the
same test directory. Adds selected-pose routing and candidate-event registration.

`m3_lifecycle_analysis_v1.log`:5PASS2.27s, domain183/timeout120s,
`test_v2_lifecycle_analysis.py`. The existing analyzer retains historical
`convergence_time`, adds explicit epoch-to-confirmation (not basin-entry),
candidate-to-snapshot and prepare-to-commit intervals with observation/valid
denominators, and withholds timing when the lifecycle contract fails. It uses
the selected MAD scale through the existing resolved-setting owner.

Independent review found normal future-leading pose headers repeatedly reset
the rolling centroid core and a foreign frame could be relabeled in typed
confirmation. The opt-in binding now detaches and buffers those poses until
clock coverage, preserves original ROS/steady receipts and selected frame,
and prevents duplicates/conflicts/regressions from refreshing or reviving data.
The standalone centroid callback retains its prior admission policy/arithmetic.
Recorder validation explicitly permits receipt-before-source only in selected
rolling mode, requiring both fresh times before actual publication.

A second concrete review reproduction delivered valid PDE1, delayed valid2,
revocation3, then previously unseen valid2. The revocation now latches its
authenticated sequence; late2 cannot restore history. Malformed revocation
cannot advance that watermark. Oversized Timekeeper conversion is guarded;
see `m3_epoch_origin_review.md` for20focused checks and exact boundary.

```bash
ROS_DOMAIN_ID=183 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_epoch_binding.py ros2_ws/src/ros_esc/test/test_v2_epoch_origin.py ros2_ws/src/ros_esc/test/test_centroid_windows.py ros2_ws/src/ros_esc/test/test_convergence_detector_policy.py ros2_ws/src/ros_esc/test/test_v2_detector_contract.py
```

`m3_centroid_admission_v1.log`:192PASS2.43s. New checks include original receipts,
detached pending values, selected frame, paused-clock duplicate expiry, source
regressions/conflicts, unseen pre-revocation support and valid later recovery.

Actual DDS command remains the epoch transport command above. Added a third
case with33.333333ms-leading pose headers and100ms clock ticks across both
authoritative epochs. `m3_epoch_transport_v4.log`:3PASS1.12s. After connecting
the diagnostic fixture to the actual selected topic and asserting each valid
diagnostic retains original receipt<source<=publication,
`m3_epoch_transport_v5.log`:3PASS1.13s. No thresholds or freshness limits changed.

The first20-file milestone integration, `m3_integrated_v1.log`, retained
684PASS/2FAIL/1inherited quaternion warning in51.88s. Both failures were
supervisor pure fixtures holding ROS time fixed while hashing/snapshot work
consumed real steady time: activation accounting returned SEARCH cancellation,
and the dependent redesign assertion found no candidate. The log alone lacks
measured receipt ages; the supervisor record documents the controlled
steady-expiry reproduction and fixture correction. Runtime freshness remains
0.5s; the failed attempt is retained. Final integration is recorded separately.


The reset review also exposed that `start_epoch` is intentionally idempotent
within one SEARCH epoch: calling it alone did not clear numerical support after
a source fault. The adapter now explicitly invalidates history without rearming
the once-epoch latch. `m3_centroid_admission_v2.log`:193PASS2.34s under the same
command above, including five old windows followed by a conflict and six
required fresh windows. Final centroid publication also rechecks the original
steady receipt, so a held-clock computation delay cannot publish expired
support. The integrated command includes its deterministic publication race.
`m3_epoch_transport_v6.log`:3PASS1.23s after these final node guards.

The final three-package isolated build uses base ROS only:

```bash
source /opt/ros/humble/setup.bash
timeout 180s colcon --log-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/log build --base-paths ros2_ws/src --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor --build-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/build --install-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install --symlink-install --event-handlers console_cohesion+
```

`m3_build_final_v1.log`:3packagesPASS20.7s. Python modules use symlink install;
subsequent bounded Python-only admission corrections do not change generated
interfaces or package entry points.


## Final milestone integration before Arm C publication admission

```bash
ROS_DOMAIN_ID=175 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 180s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_rolling_gesc.py ros2_ws/src/ros_esc/test/test_v2_stream.py ros2_ws/src/ros_esc/test/test_v2_source_contract.py ros2_ws/src/ros_esc/test/test_v2_recording_contract.py ros2_ws/src/ros_esc/test/test_v2_detector_contract.py ros2_ws/src/ros_esc/test/test_legacy_behavior.py ros2_ws/src/ros_esc/test/test_observability_contract.py ros2_ws/src/ros_esc/test/test_clock_configuration.py ros2_ws/src/ros_esc/test/test_experiment_recording.py ros2_ws/src/ros_esc/test/test_v2_clock_admission.py ros2_ws/src/ros_esc/test/test_v2_upstream_clock.py ros2_ws/src/ros_esc/test/test_v2_epoch_binding.py ros2_ws/src/ros_esc/test/test_v2_epoch_origin.py ros2_ws/src/ros_esc/test/test_v2_lifecycle_contract.py ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py ros2_ws/src/ros_esc/test/test_v2_lifecycle_analysis.py ros2_ws/src/ros_esc/test/test_v2_moving_evidence.py ros2_ws/src/ros_esc/test/test_v2_supervisor.py ros2_ws/src/ros_esc/test/test_v2_fill_transactions.py ros2_ws/src/ros_esc/test/test_v2_controller_motion.py ros2_ws/src/ros_esc/test/test_centroid_windows.py ros2_ws/src/ros_esc/test/test_convergence_detector_policy.py
```

`m3_integrated_v2.log`:812PASS/1inherited quaternion warning in53.36s.
The warning is the same unused inherited transform intermediate recorded in
M2; checked outputs remain finite. No skipped tests. This command adds the
origin tests, centroid core and inherited detector policy to the first20files.
The v1 command was this same list without `test_v2_epoch_origin.py`,
`test_centroid_windows.py` and `test_convergence_detector_policy.py`. The
remaining Arm C future-publication callback ordering correction receives a
separate focused source/transport validation before the final checkpoint.

## Recorder consistency after original-receipt admission

A PDE original callback receipt may precede a nonzero experiment origin when
source/context messages arrive ahead of the receiver clock. Input/source bounds
must remain after epoch start; the original receipt must be nonnegative, precede
publication and remain within0.5s. Requiring receipt>=origin would contradict
preserving that valid callback time. The lifecycle validator now checks the
correct distinct bounds; stale support is still rejected.

```bash
ROS_DOMAIN_ID=183 PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py::test_pde_original_receipt_before_origin_is_allowed_only_with_fresh_source_support ros2_ws/src/ros_esc/test/test_v2_lifecycle_recording.py::test_quiet_run_needs_epoch_but_no_candidate_or_event_occurrence ros2_ws/src/ros_esc/test/test_v2_lifecycle_analysis.py
```

`m3_recording_admission_v1.log`:7PASS2.58s. This includes valid and stale
before-origin receipts, missing authoritative epoch rejection, both analyzer
modes, legacy behavior and unavailable/invalid interval handling. The prior
82-check recorder record remains its earlier source boundary; the final archive
captures this one-line temporal correction and its regression.
