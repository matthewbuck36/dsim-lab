# M3 supervisor source and focused validation — 2026-09-09

Status: supervisor source and focused validation complete for integrated review.
Actual moving pipeline DDS passes two cases, recorded in `m3_pipeline_transport.md`;
the final combined integration rerun remains root-owned.
No Gazebo, hardware, source calibration, pilot or research qualification claim.
Synthetic radius0.5m/epsilon0.1m fixtures are declared inputs, not selected tuning.

## Implemented ownership and evidence

- Existing supervisor owns authoritative SEARCH epochs, both typed detector
  confirmation modes, candidate IDs, original12s verification deadlines, immutable
  raw snapshots and PREPARE/ACTIVATE/CANCEL. Existing state machine retains legacy
  defaults and negative counted ranking; moving mode allows known_count1 only
  behind the raw-information gate. Defaultzero candidate radius/epsilon refuses
  continuous startup. Initial DESIGN preserves SEARCH weights; redesign keeps
  its exact active target, candidate association and original escape timeout.
- Pure moving raw evidence uses actual synchronized source stamps and world phase,
  first-arrival/interpolated nonoverlap revolution boundaries, 12 sectors with
  two actual observations, maximum0.5s gap and30s cycle including unfinished
  cycles. Latest3 individually qualified candidate-neighborhood cycles are chosen
  before all-pairs corresponding-sector trajectory comparisons. Minima and the
  raw-value ULP floor exclude outside-interval boundary-support observations.
  Timeweighted piecewise-linear base positions supply centroids/confinement.
- Information uses demeaned raw sector medians: RMS of mean profile A and RMS
  of all three unordered pairwise profile differences D; A>max(3D,delta),
  delta=max(1e-6,64*actual raw-value ULP), negative baseline and upper<-delta.
  This rejects declared zero/constant/incoherent fixtures, not all possible noise.
- First valid filter diagnostic *received by this supervisor* supplies immutable
  state/stamp metadata, cached before readiness's numerical gate. It is filter
  publication-state evidence, not physical acquisition-state evidence or the
  globally first diagnostic another DDS subscriber might record. Repeats cannot
  overwrite it. A bounded20,000-entry/one-second source cache supports readiness
  transitions; source history itself is capped20,000, snapshots4,000.
- Actual selected poses ahead of the local held simulation clock wait in at most
  1,024 pending entries with original ROS/steady receipts and0.5s source/receipt
  bounds. Latest already-admitted pose remains authorization input; clock polling
  drains covered poses. Duplicates do not refresh, conflicts/regressions tombstone.
  Continuous existing Pose2D history uses admitted header acquisition time, while
  health retains original callback receipt. Legacy continues its prior behavior.
- Shared recorder-ready policy remains default-off. When required, original steady
  heartbeat freshness gates confirmation and activation and false/expiry cancels.
  Context starts no earlier than actual Timekeeper origin. Selected direction
  diagnostic topic is configurable through the existing launch argument.
- Every successful candidate snapshot is published once per candidate/revision on
  `/gesc_gaussian/v2/candidate_snapshots`, including no-fill GOAL candidates, and
  identical content enters PREPARE. Preparation has separate original5s design
  deadline; redesign caps it by the existing escape deadline, with no renewed12s
  evidence wait. Accepted commits update the counted ledger exactly once even
  after motion epoch exit; both actual objective and direction registry-digest
  acknowledgements are required for current-candidate escape authorization.
  Canonical fill mirrors are observational in continuous mode.

## Exact commands and retained attempts

Preflight passed:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
```

All pytest invocations sourced both overlays and preserved inherited PYTHONPATH:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
ROS_DOMAIN_ID=125 PYTHONPATH="ros2_ws/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" timeout 90s python3 -m pytest -q <tests>
```

All logs below are retained under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.

| Version | Tests supplied after `-q` | Outcome |
| --- | --- | --- |
| v1 | `ros2_ws/src/ros_esc/test/test_v2_moving_evidence.py` | 14 passed/4 failed,1.48s. Three fixture/config failures exposed inherited known1/fill-budget guard; moving-only known1 support and explicit budget fixed. One assertion wrongly required identical finite-sample sector medians at floating boundaries; bounded quadrature/discrete disagreement checked instead. |
| v2 | `test_v2_moving_evidence.py test_v2_supervisor.py` under the same test directory | 28 passed,4.40s. |
| v3 | v2 plus `test_state_machine.py test_supervisor_integration.py` | 194 passed,12.06s. |
| v4 | v3 plus `test_v2_source_contract.py` | 212 passed/2 failed,17.79s. All new M3 tests passed. Inherited DDS low-score test missed first request; source-contract expected only6 launch owners before M3's3 new bindings. |
| legacy diagnostic v1 | `ros2_ws/src/ros_esc/test/test_supervisor_integration.py::test_m2_low_score_replay_does_not_publish_a_second_fill_request`, domain126,timeout30s | 1 passed,1.21s. No source change to the legacy test. Prior failure retained as timing/infrastructure observation. |
| v5 | same full five-file selection as v4, after authorized launch fixture adaptation and new GOAL snapshot check | 215 passed,16.24s; inherited DDS case also passed in this complete suite. |
| v6 | `ros2_ws/src/ros_esc/test/test_v2_moving_evidence.py ros2_ws/src/ros_esc/test/test_v2_supervisor.py` | 44 passed,11.24s after final metadata-cache and duplicate-identity guards. |

Focused coverage includes source cadence/wrap/negative rotation, interpolated
boundary exclusion, gap/reversal/unfinished-cycle resets, confinement/drift/
shifted-sector paths, zero/constant/phase-incoherent profiles, finite numerical
extremes, capacities, source/ID conflict and revocation, both epoch-bound detector
modes, pretrigger-only evidence, immutable preparation, wrong hashes/geometry,
late accepted commit after SEARCH exit, no repeated ledger increment, two-owner
acknowledgement, readiness, future pose original receipts, separate deadlines,
redesign preservation/abandonment, and actual SupervisorNode callbacks.

Source hashes at this focused boundary:

| File | SHA256 |
| --- | --- |
| `ros2_ws/src/ros_esc/ros_esc/supervisor_node/moving_evidence.py` | `abc29fd1ed457e207539883435ede4803d6958f8315624c74960c989b6c9ee71` |
| `ros2_ws/src/ros_esc/ros_esc/supervisor_node/v2_supervisor.py` | `5e26bca8e2bdea39b765924aa308138a44041fb3be3e2d23a2adb3d620b89466` |
| `ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py` | `63a2e0a57561e6d29f5bcc465ad03b715b523d4f33ffb70a4571c42f6ef962f1` |
| `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py` | `45a9c825bd680ac1256a18250d2143b6d5cf2cf8078af5a100a90f9040bf6241` |
| `ros2_ws/src/ros_esc/test/test_v2_moving_evidence.py` | `99a0c69027bd97b0425723602c59e7268d6d3a189ab2eecc296ce0bbd99ade22` |
| `ros2_ws/src/ros_esc/test/test_v2_supervisor.py` | `c84f5b6a02702ca864cee5f4dd17651ef76aed25bdeb4f69ebc4037c2976c108` |
| `ros2_ws/src/ros_esc/test/test_v2_source_contract.py` | `167d18f8166fb7ffcf4d9c12016db45a8900d109bb5cc171eb702835d92c93a8` |

Retained log hashes:

| Log | SHA256 |
| --- | --- |
| `m3_supervisor_v1.log` | `0ee384781c82e711f88bb98894be91f3c52b4d08b3c0a30ce4b3f9e3ee822ef6` |
| `m3_supervisor_v2.log` | `2e6c0f58aec8ce4f10a6ab379798fc1ede9ac71dd58c6c0ea74b0bbe06a4f046` |
| `m3_supervisor_v3.log` | `a6391297eb7d8336a907bc04b8ff58f9a79b2166da91b722a9fdc368824a058a` |
| `m3_supervisor_v4.log` | `ded722079c6dbf338b8687043acefd791b8d408a83660abfec88ba3c90b1bfc0` |
| `m3_supervisor_legacy_diagnostic_v1.log` | `070a0a1a384f8986bf91c5e6a28d1adb0cf8744a853fe1ce7e8ca4541698f8d4` |
| `m3_supervisor_v5.log` | `0eded775f3f643f4da80cff2fce0c87e3ca9ce3bd496e8be56452a14208d302b` |
| `m3_supervisor_v6.log` | `a42711e6bc29b4d4aec351d96d782ecbfc71f2cc0958ca5345a3b9eac8b551b0` |

## Post-integration envelope and fixture correction

The initial root combined run `m3_integrated_v1.log` retains2 failed/684 passed,
51.88s, with one inherited unused-quaternion warning. Both failures were in pure
supervisor fixtures that held their fake ROS/source clock at9s while allowing
real monotonic time to elapse during Python snapshot/hash work. The only changed
input capable of producing the observed DESIGN→SEARCH cancellation in those
fixtures was original recorder/pose steady age; source time, geometry, identity
and deadlines remained fixed. A new deterministic +500,000,001ns steady-expiry
fixture reproduces that exact transition and verifies retained accepted ledger
state. The old combined log does not contain measured original wall ages.

Pure tests now explicitly control monotonic_ns, independently of computation
speed under integrated load. Explicit expiry tests still advance it. Actual-node
callbacks and separate DDS tests retain real steady clocks. No runtime freshness
limit was relaxed. The redesign fixture also asserts its initial ESCAPE entry
before testing unavailable redesign, making a prerequisite failure explicit.

Runtime envelope corrections authorized after review:

- SEARCH context is valid only after local clock covers its frozen started_at;
  a future-leading nonzero Timekeeper origin can no longer publish a valid
  context with started_at later than its publication stamp.
- Guarded `relative_stamp_ns(0,start_time)` and stream-contract construction occur
  before first-origin assignment. Malformed, scaled-overflow, out-of-ROS-range or
  replaced origins latch invalidity without throwing from the callback or
  accepting a later replacement identity.

Commands use the same sourced overlay, domain125 and90s timeout, with precisely
`ros2_ws/src/ros_esc/test/test_v2_moving_evidence.py ros2_ws/src/ros_esc/test/test_v2_supervisor.py`.

| Version | Outcome |
| --- | --- |
| `m3_supervisor_v7.log` | 44 passed/1 failed,11.70s. New controlled-expiry test inspected the cancellation reason after SEARCH cleanup replaced it with `search_reentry`; moved that assertion before transition cleanup. This was a test observation-order error. |
| `m3_supervisor_v8.log` | 45 passed,12.43s, including controlled steady-expiry reproduction and future-origin context coverage. |
| `m3_supervisor_v9.log` | 51 passed,11.54s after guarded origin conversion; extreme, nonfinite, negative, out-of-range and replaced-origin cases pass. This is the final supervisor source/focused boundary before root integration rerun. |

Updated final source hashes (earlier hashes remain historical boundaries):

| File | SHA256 |
| --- | --- |
| `ros2_ws/src/ros_esc/ros_esc/supervisor_node/v2_supervisor.py` | `a661a2513e2c158ce426a391fa19dde1c62c1877bb10538136a1f143ed400912` |
| `ros2_ws/src/ros_esc/test/test_v2_supervisor.py` | `c93d2eb768201ccd269b45b46d56623a2b66cbbdae0d0c0551374a7004c3c06f` |

| Retained log | SHA256 |
| --- | --- |
| `m3_integrated_v1.log` | `a58b23e2321bc947b521bf96f114b673f1c124e8a2b0746730f2ec7c58c76b46` |
| `m3_supervisor_v7.log` | `f7d94ecd5b47fca71e26b3e678f1f44c85475bb46f311d56b287d14ebbdbdf31` |
| `m3_supervisor_v8.log` | `f905f7d90c1c54f7836a68bc31a197209c9c01e3b4ab6877f27fa0b94e9d7e75` |
| `m3_supervisor_v9.log` | `1acc7eed9aafaf9026d844537e5502f3f9a9e6e0bd8d94f1cb27fe065e82664a` |
