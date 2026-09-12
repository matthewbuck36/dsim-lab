# M1a technical recovery v1

Status: FROZEN before recovery implementation or execution, 2026-09-09 UTC.
This is a bounded performance/recovery correction within M1. It changes no
scientific definition in `m1a_plan.md` or `validation/m1a_contract_v1.json`.

## Preserved incomplete attempt

The original M1a label command stopped at its 600-second limit with exit 124.
All six enclosures qualified and all 8,625 completed point calculations were
published, but only the first input's spatial-label count reached the log.
No complete `labels.json` exists. Do not calibrate from this incomplete attempt.
Preserve `/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1/` and
its log without modifying or recomputing its numerical evidence.

The root verified the old analyzer against the original started receipt and
saved an exact source snapshot. The recovery input manifest is
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_recovery_v1/recovery_inputs.json`,
SHA256 `ac8165d721cc3557b06f84c85c0fa42ab0a98dea45ba076c1539dce38f4a2cfd`.
It binds 8,642 JSON receipts, including every point, plus the original owner
hashes and unchanged input identities. The old analyzer SHA256 is
`c95a509fef294fff89ec61a08fb3b8d022bc653a9e0790f0e12fe69e68c64a09`.

## Bounded correction

The 69,222 frozen poses create 67,685 candidate six-second windows. Rechecking
each full segment in each overlapping window permits up to 23,960,490 mask
negative-exclusion queries. Cache each full segment's validity and outside-all-enclosures result
once, with prefix counts of invalid segments. For each window, separately
check only the first segment clipped at exactly `end_time - 6 s`; an exactly
aligned start reuses the cached full segment. Preserve full source-gap checks
even when clipping that segment. This reduces the upper bound to 273,798
negative-exclusion queries without changing any spatial, temporal, or acceptance
rule. Positive-membership checks remain additional, unchanged work.

Keep the direct per-window NumPy net/path calculation and summation, including
its current strict comparisons. Cheap progress rejection may precede mask
queries because it cannot admit a case. Do not change positive labels,
12-second residence, 54-second common support, once-per-epoch comparison,
boundary tolerance, holes, confinement, synthetic traces or the 36-grid.

Extend the existing analyzer with an explicit optional recovery-manifest
argument; no new labeling pipeline. Before reuse, verify every old receipt
hash, the immutable traces/partition/contract, and exact group keys from the
recorded sources, bounds and model/sensor configuration. Require unchanged
enclosure helper, evaluator, cost-function and configuration hashes. Preserve
the original geometry provenance and analyzer snapshot/hash. Verify that the
geometry-task function body is unchanged from that snapshot. Record the new
label-owner hash separately; do not rewrite the old numerical owner's hash
to claim the entire analyzer file stayed unchanged.

Recovery must load completed, qualified source/group receipts only. It must
never call the numerical geometry qualifier or resume partial point work.
Publish a new exclusive label attempt at
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1_recovery1/`.
Its manifest binds both the original numerical chain and the new label owner.
All earlier contracts and artifacts remain unchanged.

## Verification and execution

Use bounded analytic fixtures to compare optimized labels against the retained
pre-recovery implementation for crossings, clipped boundaries, invalid/gapped
support and near-threshold directed travel. Include the case where clipping
removes an earlier excluded portion of a segment. Verify query-count bounds,
immutable-geometry recovery, changed-owner/receipt rejection, and that recovery
never calls the geometry qualifier. Run the existing focused analyzer/replay
regressions under `timeout 180s`. The numerical helper is unchanged; do not
repeat its expensive field calculations or broaden unrelated tests.

After focused checks, root reviews the diff and records a checkpoint. Execute
recovery once under `timeout 600s`, with at most five seconds of process-kill
grace. Complete reviewed labels then permit the original fresh M1a 36-grid
under `timeout 300s` at `m1a_calibration_v1/`. No calibration has yet run there.
Retain a further timeout/failure honestly; no automatic retries or scientific
rule changes are permitted. This correction authorizes no Gazebo or hardware.
