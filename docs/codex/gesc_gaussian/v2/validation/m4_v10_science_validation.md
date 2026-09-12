# M4v10 science and continuous-acquisition source validation

Implemented under the adopted [V10 plan](../m4_v10_arrival_comparison_plan.md),
2026-09-10. This is source validation plus a check on exposed D02 evidence;
it is not a new comparison result or confirmation release. V1–V9 outputs,
failed experiments and numerical methods remain unchanged.

## Selected owner changes

`m4_pilot.py` and `tools/evaluate_m4.py` select the new method identity only for
`m4-pilot-v10`. The filtered science union requires full recurrent diagnostics
for B/D, the typed recurrent stationary request for B, and centered guidance
for C/D. Existing lifecycle and stationary authority checkers remain the owners
of their respective request/state/command joins. Recurrent confirmation timing
uses its support endpoint and retains the actual input/publication coordinates.

Arrival binds the scenario's `post_recovery_arrival_v1` result to the exact
retained measured pose and matching live evaluator sample. Actual local
recovery, fill cardinality, required state/event paths, escape command ownership,
forbidden-state/event absence and global arrival form the combined sequence.
GOAL_HOLD timing and ranking remain optional diagnostics. Path length uses the
actual recorded pose alias. Independently frozen spatial labels still precede
event attribution, and the original latency/reference estimands remain intact.

Each run derives nine explicit science checks: acquisition, position labels,
confirmation attribution, selected authority, error attribution, arrival,
path length, motion measurement and direction inputs. The summary additionally
requires four complete run analyses and both complete C/D products, each with
the exact24 scheduled reference targets and explicit exposure/qualification
flags. Complete negative/censored baseline outcomes and unexposed targets can
remain scientifically complete; missing authority, measurements or references
cannot. Nested acquisition/label/input/reference receipts and late source
hashes are checked before publication. The workflow owner separately applies
the enabled-method behavioral release conditions.

The sole motion metric is `continuous_acquisition_metrics`; its BagData adapter
is `_v10_motion_metrics`. It uses the prospectively fixed0.5s source coverage
and sustained-interval limits, finite planar speed `hypot(vx,vy)>=0.001m/s` or
`abs(wz)>=0.001rad/s`, measured positive planar path, typed guidance and exact
full-stream final diagnostic/Twist pairing. Zero publications retain their ROS
and bag stamps/durations. Same-tick zero/nonzero pairs do not create invented
ROS dwell. Measured stationary intervals, sustained zero commands, absent
acquisition and missing coverage have distinct outcomes. Only observed complete
VERIFY plus initial DESIGN continuity establishes zero mandatory acquisitions.

## Retained source tests

All external paths below share:

`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_source_v1/`

Root ran the explicit selection through `validate_source.py`, under the adopted
230s pytest work cap,5s termination allowance and260s inclusive wrapper cap.
The selected runtime environment was
`development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh`
with `env -u PYTHONPATH`. Exact expanded pytest argv, file hashes and installed
entry-point bindings are retained in each `started.json` and
`source_validation.json`; the log and JUnit hashes are included in the latter.

| Receipt | Result | Inclusive elapsed |
| --- | --- | --- |
| `focused_v1/source_validation.json` |607 PASS,1 FAIL;757 source pins and21 installed entry points stable |131.639977s |
| `focused_v2/source_validation.json` |32 PASS in the affected version module;757 pins and21 entry points stable |9.894771s |

The first failure is preserved: `test_retained_v9_scenario_bytes_remain_exact`
used sorted JSON topology input instead of the original insertion-ordered YAML
input. The mappings were identical; serialization order differed. Only that
fixture input route changed. The prospective correction receipt is
`detector_v9_fixture_correction_v1.json`; it records no production changes.
The corrected32-case module passed separately, without repeating the whole
bundle. The owned new science20 cases and motion16 cases all passed in v1.
They cover actual arrival binding, complete failed/no-candidate baselines,
missing references, changed nested receipts, full24-target identities,
source gaps, sustained stops, same-tick zeros and actual BagData projections.

Receipt SHA256:

- v1: `a68cf39ade6305471152324aceea29c55b1bf1b438ffaa45b0f95b17ba14a50e`
- v2: `66918ecd467939371b294dee4feba070c01b67a092c3efcea2c007872aea5753`
- fixture correction: `c4328375524d2ade3ecb259b456ca2c9fa5d35ded9dcff3a6c314ecafb0a8ccc`

## Retained D02 motion check

Root invoked `check_retained_motion.py retained_motion_v1` once under60s, using
the same selected environment. It completed in4.244722s. The764 source/input
pins matched before/after; the original D02 analysis receipt, every consumed
artifact and the resolved scenario matched their retained original hashes.
The helper restored four complete generated-message JSONL streams with exact
canonical payload parity and only the consumed recorded odometry CSV fields.
It decoded no bag and ran no labeler, reference solver, model or simulation.

Result: `OBSERVED_CONTINUOUS_ACQUISITION`, `analysis_complete=True`,
`mandatory_stopped_acquisitions=0`, complete command pairing and prior valid
authority. Inputs:3616 states,3615 guidance messages,9419 diagnostics,
9419 actual commands and5314 measured poses. All604 zero publications in the
full command stream remain counted; the segment-specific records retain their
exact pulse details and guidance reasons.

| Actual segment | ROS interval | Measured poses* | Planar path | Zero publications | Longest zero ROS dwell |
| --- | --- | --- | --- | --- | --- |
| VERIFY |78.2–92.3s |415 |0.513372m |170 |0s |
| Initial DESIGN |92.3–92.9s |18 |0.016116m |8 |0s |

*Segment endpoints are inclusive for pose measurement and may be shared.
Both segments have complete coverage and positive measured motion; neither has
an observed sustained stationary interval. The longest retained zero/nonzero
bag-receipt separation is0.017663670s in VERIFY and0.014005540s in DESIGN.
The existing complete/valid D02 lifecycle summary supplies prior authority;
this check does not claim to revalidate that lifecycle. D02 remains exposed
development evidence, and its frozen original acquisition verdict is unchanged.

Full result: `retained_motion_v1/receipt.json`, SHA256
`483a217448974b4d64d5b65bd50a23eb9068562b78c1c5e724968dc421afccd1`.

## Source boundary

Owned production/test SHA256 values:

- `m4_pilot.py`: `6f65b8141bc92adabc303461bb2698b8b6039ae1f0273424fb385c11e3e488b0`
- `evaluate_m4.py`: `1ef07bb41d2705693d6bae7dd543bda4359bd616aedcbdd0a32b1dac769fc66b`
- `test_m4_v10_science.py`: `2fa5c4ccf3e77ab2f8d45726bea6bfe2133af22317e3b11e432b4fc11ffc3704`
- `test_m4_v10_motion.py`: `4288d89485f8c537c0205682b3962ef84b2f7ab2bf02b7cc1804b5b40446134d`

After the terminal jobs, the documentation-context check passed:
`timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`.
No additional test, bag read or simulation was run by this scoped closeout.
Root owns overall validation, checkpoint/archive and any later preparation.
