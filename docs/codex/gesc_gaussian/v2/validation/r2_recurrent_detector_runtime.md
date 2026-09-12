# R2 recurrent detector: source and finite transport boundary

SOURCE_VALIDATION_PASS, 2026-09-10. New selectable
`recurrent_geometry_v3` runs inside the existing detector and typed V2 binding.
No Gazebo, model, bag or holdout was used in this boundary. No closed-loop or
source/fill qualification follows. Root owns integrated release and checkpoint.

Design: [runtime plan](../r2_recurrent_detector_runtime_plan.md), including its
measured static amendment; [static correction plan](../r2_static_correction_plan.md).
Circle/oscillation prototypes remain independently retained in their validation
records, including failed earlier geometric hypotheses.

## Preserved failure and fixed static calibration

The initial combined core's 31 focused tests had30 passes and1 genuine negative
failure in2.60s: a translating line oscillation (amplitude.25m, P66s, phase.37,
drift.02m/s) triggered static12 at12s, radius.026246882m, measured local drift
.001383909m/s. This is transient cancellation, not an oscillation-fit failure.
`development/20260910/recurrent_runtime_v1/initial_core_result.json` and initial
source hashes retain it. `core_before_static_correction.py` is the exact
pre-correction core, hash-verified against the calibration's prospective pin:
`a6e1854cf39a4c5a50d3bc100a84c9a5e15c0fa4142b9068a6ad064d7842a3d0`.

One prospective static job ran:

```bash
timeout --signal=INT --kill-after=2s 118s env PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/static_correction_v1/run.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/static_correction_v1/execution.log 2>&1
```

Exit0, numerical1.438103435s, no unchanged retry. Retained228 family rows:
99 arc fixtures,96 oscillator fixtures, the new failure and32 independent
P54/60/66/72,8-phase translating negatives. Overlapping R1 fixtures remain
explicitly identified by family; there are4 static-positive rows representing
3 unique traces,159 negative rows,65 other/gray rows. At30s support and unchanged
.005m/s trend limit, radius.03 detects3/4 static positives, misses the fixed
sigma.01m fixture, and admits0/159 negatives. Radius.04 detects4/4 (all at30s)
and admits0/159. The prospective decision therefore selects static30/.04.
No noisy fixture was removed or relabeled. Five receipt-hashed files verified.
Result SHA256 `74a9d50e743abc9cb4b0b93df3f48e42cb011afead6ca90c7d447fa8aaf5877f`;
receipt `21f9a8cb6540fc1ba01660dc7fa8a0aceb553b8e2336f46be03cf029a377cc7f`.

## Production change

New pure `convergence_detector_node/recurrent_geometry.py` combines static30,
independent arc-center30/36 and harmonic36/54. The circle and oscillator
thresholds are unchanged from passing prototypes. Actual geometry covers all
original vertices and bracketed boundaries; resampling affects only the finite
harmonic fit. Source-time6s endpoints are anchored to authoritative SEARCH time.
Each circle/oscillator width has its own3-pass streak. Only new epoch identity
rearms; source faults discard history/streaks, preserve the confirmation latch,
and rebuild causally. History has54s plus one bracket and100000-point cap.
Cached finite pseudoinverses replace continuous fitting searches.

New `recurrent_contract.py` exports explicit mode/topic/history constants and
`recurrent_diagnostic_errors`. `RecurrentConvergenceDiagnostics.msg` preserves
source/receipt/history identities while recording drift in m/s and the explicit
12s-scaled metre score, branch quality, current support and separate persistence
support. Existing messages retain their old wire layout. The node reuses its
pose/state/readiness/clock gates and steady watchdog; new-mode invalid heartbeat
is mandatory although the old heartbeat parameter remains false. Selection is
limited to rolling simulation, with first integration moving verification only.
The old centroid mode tuple and all legacy algorithms remain selectable.

The existing `v2_binding.py` forwards authoritative epoch origin and the new
history_kind through existing confirmation/freshness logic. That file was
released to root for its additional review/regressions. Launch/centered
supervisor owners belong to direction agent; recorder/analyzer/lifecycle owners
belong to root/D3. This record does not claim their separate validation results.

## Exact focused verification

Shared generated interface environment (built by direction agent, exit0 in27.9s):
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_runtime_v1/environment.sh`.
Commands start with `env -u PYTHONPATH bash -c`, source that file, then prepend
`/home/mattb/dsim-lab/ros2_ws/src/ros_esc` to PYTHONPATH. DDS tests explicitly use
`ROS_LOCALHOST_ONLY=1 ROS_DOMAIN_ID=153`; every command has an outer timeout.

Initial inherited regressions:

```bash
timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_centroid_windows.py ros2_ws/src/ros_esc/test/test_q7_centroid_method.py ros2_ws/src/ros_esc/test/test_convergence_detector_policy.py ros2_ws/src/ros_esc/test/test_q3_centroid_clock_admission.py
```

PASS189 in7.40s. The first real new-mode DDS test transported the correct
confirmation, then failed an assertion comparing whole messages containing NaN
in inapplicable scalar fields. Preserve that test-only failure in
`initial_transport_result.json`; comparing serialized roundtrip bytes fixes the
assertion without changing payload or detector. Corrected core+transport then
PASS32 in5.09s (`corrected_core_transport.log`).

Final bounded source run after the static correction and malformed-support guard:

```bash
timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_recurrent_geometry.py ros2_ws/src/ros_esc/test/test_recurrent_detector_transport.py ros2_ws/src/ros_esc/test/test_centroid_detector_transport.py ros2_ws/src/ros_esc/test/test_convergence_detector_policy.py ros2_ws/src/ros_esc/test/test_q3_centroid_clock_admission.py
```

PASS109 in11.38s. Log: external `recurrent_runtime_v1/final_source_transport.log`.
Seven selected source/interface/test hashes were captured before and verified
unchanged afterward in `final_source_pins.json`. These counts overlap earlier
regressions and must not be added as unique tests.

New checks include circles/oscillations atP12/24/36/48/60/72, independent
translation and large-loop controls, original off-grid spikes, fault/epoch/latch
handling, no extrapolation, bounded source storage, per-width persistence loss,
and malformed diagnostic rejection. Real DDS confirms the circle at43s for an
epoch starting1s (42s elapsed), exactly once, with matching diagnostic/typed
history bounds, scaled metre score, explicit source_stamp and persistence.
It serializes the new type without value loss and covers outside-SEARCH status
without another confirmation. Existing centroid DDS and clock/policy checks pass.

`python3 -m py_compile` for new core/contract/node, `git diff --check` and
`timeout 30s .../tools/validate_phase_context.sh v2 implement` PASS. This boundary
leaves the inherited dirty V2 work intact. No commit, status/handoff change or
Gazebo dispatch was made by this detector subtask.

Final selected hashes: core
`b10fa55d49373493327369385f1b5964d0fae8a7461111724745c5d9cf5c7920`;
contract `d41ec642ede342d53e89e01d043a90f2710468ef437cac7dda922d73cda4ae78`;
node `151d5360eca2cdfcf8009877cf3f90359619d797cda6aa931da20a0a41a39383`;
message `f962f9e0c105290ef208d4fe9a4d4422ff88bd60f4fbd4ee65ae096c12017640`.
