# Q1 cost-join expiry recovery validation

Verified 2026-09-09 under `q1_filter_expiry_recovery_plan.md`. The final
core/adapter and independent transport/adversarial run passes **233 tests in
5.38 seconds**, exit0. This closes the bounded source correction. Recovery3
remains CLOSED INCOMPLETE; no acquisition, scientific qualification or M4
release follows from this result.

## Source contract

Only these implementation owners and the dedicated test were changed by this
owner:

- `ros2_ws/src/ros_esc/ros_esc/filter_node/rolling_gesc.py`
- `ros2_ws/src/ros_esc/ros_esc/filter_node/v2_runtime.py`
- `ros2_ws/src/ros_esc/test/test_q1_filter_expiry.py`

`SourceSynchronizer.expire_pending(reason, extra_keys, now_ns)` now retires all
discarded core and adapter partial keys, clears cost joins and increments the
reset sequence while preserving independently valid pose/encoder samples,
their original receipt times, and source/sequence frontiers. The returned
`SyncBatch.retired_keys` records newly retired keys. `is_retired(key)` and
`retire_keys(keys, now_ns)` distinguish expiry retirement from used or poisoned
keys. Used/poisoned keys retain precedence.

The adapter coordinates its partial cleanup with the core instead of causing
a second support reset. Both expiry paths reset the existing filter state,
integration source time and rolling confidence. No observation is emitted by
a fault batch. Fresh recovery starts with zero integration interval,
instantaneous fallback and empty completed-cycle confidence.

Expiry-retired packets are ignored only after applicable key, clock, typed
envelope, identity, source geometry, array and objective checks. Retired
objective samples retain the existing finite weighted-arithmetic check with
`rel_tol=abs_tol=1e-12`. A benign old packet cannot refresh its original age or
recreate a join. Invalid context/frame/source data, malformed values, explicit
revocation, real consumed-payload conflicts, poisoned support, clock rollback
and context replacement retain hard rejection/reset behavior. Old support
still fails the unchanged500ms freshness and50ms no-extrapolation bracket
rules. No expiry-retirement frontier is inferred from malformed/future input.

The exact retirement map holds at most `2 * max_pending_costs` keys:2048 by
default. Core and adapter can each have a disjoint full1024-entry pending
queue, so this holds their entire discarded union. The adapter uses the same
configured pending bound as the core, preserving its default1024 limit.
Repeated packets do not refresh retirement order. Older entries are evicted
normally; no new public launch parameter or cutoff was introduced.

These semantics apply only to `model_input_time` schema2. The inherited
publication-time expiry path still clears support. Filter equations, gains,
confidence rules, source schema, control ownership and scientific settings
are unchanged.

## Focused evidence and retained failures

All commands ran from `/home/mattb/dsim-lab`. The isolated overlay was sourced
after Humble; only the external filter dependency was appended to PYTHONPATH.
The source package directory was not prepended. No Gazebo or hardware ran.

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="${PYTHONPATH}:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=186 timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_filter_expiry.py ros2_ws/src/ros_esc/test/test_rolling_gesc.py ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_v2_clock_admission.py ros2_ws/src/ros_esc/test/test_q1_filter_expiry_adversarial.py ros2_ws/src/ros_esc/test/test_q1_filter_expiry_transport.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_filter_expiry_core_v6.log 2>&1
```

Final result:233 passed,5.38s,exit0. No skips. The independent actual DDS test
uses domain186, held10Hz simulation clocks and108 synthetic30Hz acquisitions,
with the first raw component omitted. Its first recovered output has one
sample, no completed cycles and zero blend; later retired fragments do not
repeat resets. Independent malformed/context tests are included in this final
run. Their separate earlier results are documented in
`q1_filter_expiry_transport.md`.

Core/adapter regressions cover retained original support receipts, source and
sequence order, stale support, no bracket fabrication, all24 late component
orders, malformed retired keys/payloads, explicit revocation, used-key
conflict, rollback/new context, empty-history recovery, and unchanged legacy
expiry behavior. The capacity regression fills two disjoint queues to their
declared bound, expires them together, and sends every late fragment without
another reset or support change. It uses exact wire float keys throughout.

Earlier commands v1–v3 used the same environment with domain191 and only the
first four test files above. V4–v5 used the final six-file command with their
corresponding log suffix. Every command had timeout90s. Logs remain at
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`:

| Log | Outcome | SHA256 |
| --- | --- | --- |
| `q1_filter_expiry_core_v1.log` | 182 passed,2 failed,4.40s,exit1 | `16acf18ee144af6ee55a5b89bea1f79216671c65959e8f6fce10d73ca687b8a3` |
| `q1_filter_expiry_core_v2.log` | 184 passed,4.41s,exit0 | `7fb5b258d0722f7b7a760630005451806f01998d21975d0ef80868ec3a83c707` |
| `q1_filter_expiry_core_v3.log` | 184 passed,4.30s,exit0 | `9935e6f5f41671969d86f7250f7ae7f7c5cd24f5fcc40d86142957b7a0b8b30f` |
| `q1_filter_expiry_core_v4.log` | 232 passed,1 failed,5.34s,exit1 | `43888ee611e5ad911a2c70011977d58623518c932631282327ce68b01641b297` |
| `q1_filter_expiry_core_v5.log` | 232 passed,1 failed,5.52s,exit1 | `fd38716737b761b8bc07f6c2c3b1d0225a9dc9bb025b9ee5540b454d3490b271` |
| `q1_filter_expiry_core_v6.log` | 233 passed,5.38s,exit0 | `45c9d1bb21dc83fafc8d6dca6bb0363f05846b9f2ca96c0029eefaaf3134d110` |

V1 exposed two fixture errors: revision0 is permitted by the pure objective
identity contract, and the imported held-clock fixture fixed publication at
1.1s regardless of its source argument. The malformed test now uses a
nonfinite weight; the local multi-time fixture supplies source-following
publication/composition times. Independent review then caught a real missing
retired-objective arithmetic check, repaired before v3. V4's new capacity
fixture supplied1.1s after the shared support helper advanced clock to1.12s;
the correct rollback rejection failed the fixture. V5 compared decimal
literals against actual wire keys such as1.4200000000000002. Both fixtures were
corrected using the actual clock and exact wire keys; runtime rules were not
relaxed.

Context validation passed before edits and at final recovery:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
git diff --check
```

## Corrective admission diagnostic and equivalence

The original diagnosis and both original reports remain unchanged under:

`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery3/diagnostics/filter_startup_confirmation_residence/`

Its `manifest.json` SHA256 is
`dc740d60c8b96b02f010a41984780cb426e3e2f72c8313d164a83217ddb3af59`.
It binds the exact original commands/scripts/reports and the closed startup bag
SHA256 `8d4664a4d1cd7ebb262fa97b9c3912ed41852dd1d671513cb7a015e1192c5d35`.

The unchanged-byte diagnostic scripts were each copied into `corrective_v1/`
and executed once against the corrected source, with fresh exclusive output:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="${PYTHONPATH}:/home/mattb/dsim-lab/extremum-seeking/src" timeout 60s python3 /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery3/diagnostics/filter_startup_confirmation_residence/corrective_v1/replay_admission.py > /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery3/diagnostics/filter_startup_confirmation_residence/corrective_v1/replay_admission_v1.log 2>&1
PYTHONPATH="${PYTHONPATH}:/home/mattb/dsim-lab/extremum-seeking/src" timeout 60s python3 /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery3/diagnostics/filter_startup_confirmation_residence/corrective_v1/replay_prefix_loss.py > /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery3/diagnostics/filter_startup_confirmation_residence/corrective_v1/replay_prefix_loss_v1.log 2>&1
```

Both exited0. These are admission-only checks through the actual adapter/core,
with synthetic constant payloads and `_evaluate_filter` replaced by an
admission counter. They use the first10 simulated seconds of recorded timing
and bag row order. They do not execute ROS nodes, filter equations, field
models, direction quality, centroid detection or scientific performance.

The complete-prefix corrected report is exactly equal to the original report:
288 admissions, initial context reset only, the same stored20 admission
receipts, faults, aggregates and final state. Its JSON SHA256 is unchanged:
`c3f35edd7703d059dc53956b7ed2bb5f452910d371376acd340d21522052bd08`.

The controlled first-raw omission previously admitted14 samples then suffered
repeated expiry with no recovery. The fresh corrective report admits287
samples, with exactly one pending expiry at0.8s after initial context setup,
no repeated expiry and no unbracketable heads. Its SHA256 is
`143c5808a52a6c3624f20850328a1452ae08f1d2fbe5c019908eed6482cbc893`.
The original failed report is retained with SHA256
`13f1ef4b4f85ea73cb4d4d7e7b7f115ec8169a564416549d62df0d750c7ef4f8`.
The omitted callback is a controlled hypothetical trigger; recorded bag order
does not prove actual filter subscription initialization or callback order.

`corrective_v1/equivalence.json`, SHA256
`cf976f2328eb0362f196a78932322de49e7debf9c1657040d3c7fd9a9520a5ab`,
binds those harnesses, reports and logs and compares the numerical function
against the recovery3 checkpoint archive. The exact source of
`RollingFilterAdapter._evaluate_filter` is unchanged, SHA256
`ee28e97aec595963471bc994f2e8190ca29370c88229c6c6ed5a31df8d01fd39`.
This equality was checked again after the final capacity edit against
`checkpoints/q1_preacquisition_recovery3/source_and_evidence.tar.gz` member
`ros2_ws/src/ros_esc/ros_esc/filter_node/v2_runtime.py`.

The replay receipt predates the final union-capacity edit. No replay was
repeated solely for that edit: each diagnostic contains at most288 cost keys
in total, below both the old1024 and new2048 retirement limits; the default
adapter pending limit is still1024. Thus the capacity-only change cannot alter
either saved diagnostic path. The combined full-queue regression separately
exercises the changed capacity behavior. These are bounded compatibility
prerequisites, not broad equivalence or authorization to import other inputs.

## Final source boundary

Source paths below are relative to `ros2_ws/src/ros_esc/`:

| Source | SHA256 |
| --- | --- |
| `ros_esc/filter_node/rolling_gesc.py` | `7914b8aac889182f4440844c27678076074577328df2586eb87c4dc7947811fb` |
| `ros_esc/filter_node/v2_runtime.py` | `ad36418ed1f001db887bd7620f4429bed9a9931ae08686a4b2a2032c8099b201` |
| `test/test_q1_filter_expiry.py` | `4937f5be99ffbb06ec33f88c345ceb9fa78c98625d24d4f130a91408663c71e0` |

Source and tests are frozen at this boundary. Parent coordination owns the
live status, checkpoint, any later build/release and prospective input import.
No retained run, scientific label, filter setting or old evidence was rewritten.
