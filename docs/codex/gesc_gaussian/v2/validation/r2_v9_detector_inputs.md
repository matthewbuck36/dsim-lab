# R2 V9 development B/D detector inputs

Status: DIAGNOSTIC_ONLY_COMPLETE, 2026-09-10 UTC. The
[prospective selective extraction](../r2_v9_detector_inputs_plan.md) completed
exactly one existing-owner read of development B and D. No other trial was read,
no numerical replay/reference ran, and V9 remains CLOSED_INCOMPLETE.

## Execution and preservation

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/v9_detector_inputs_v1/`.
The original run identities are `m4-pilot-v9-slot02-B-26090801` and
`m4-pilot-v9-slot04-D-26090801`. Each run's eleven original files, including its
closed bag, matched the final V9 archive receipts before and after extraction;
the exact inventories also remained equal. Six held source/helper/plan files
and the archive manifest matched before and after each read. All eighteen
compressed output artifacts were independently rehashed after completion.

The existing `read_run_bag` and `records_for_alias` owners decoded only the
selected aliases. Full generated payload serialization, tagged nonfinite
values, compact compressed rows and descriptive summaries reused the retained
V6 export helper without invoking its old V5 extraction entrypoint. No duplicate
analysis owner or ROS context was created. Both helper ASTs and manifest/count
preflight passed; no new source-test campaign was needed for these reused owners.

Exact command from repository root:

```bash
timeout --signal=INT --kill-after=2s 148s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/v9_detector_inputs_v1/run_batch.py
```

The exact clean Humble -> Q2 -> Q5 child commands are retained in
`B_command.json` and `D_command.json`; full logs are `B.log` and `D.log`.
The wrapper returned 0 in **24.234410425 seconds** under 150 seconds. Both
children returned 0 and were reaped; no timeout or forced exit occurred.

| Run | PID | Selected records | Bag read seconds | Inclusive child seconds |
|---|---:|---:|---:|---:|
| B | 8550 | 39,635 | 3.956398435 | 12.191439881 |
| D | 8576 | 45,555 | 3.845456788 | 12.042572266 |

Both runs stayed below their 60-second ceilings, every stream below 40,000 and
each selected total below 160,000. All 85,190 rows match immutable bag metadata.

## Recorded findings

B retains 10,617 poses and 10,711 centroid diagnostics. Among readiness-scoped
messages, 1,059 have invalid history and **9,472 have valid computed score and
confinement**. All 9,472 fail the strict `score_m < 0.18 m` test. Finite scores
range from **0.204688289 to 0.823992887 m**. Of those valid histories, 7,883 pass
confinement only and 1,589 fail both gates. No score-only or joint pass and no
confirmation is recorded. This directly identifies V9 B's recorded threshold
non-crossing; it does not require borrowing V5's different score values. Whether
the underlying trajectory should be labeled trapped requires independent
trajectory/control evidence, beyond this descriptive extraction.

D retains 10,734 poses, 9,053 centroid diagnostics, 7,310 epoch messages and six
typed confirmations. During readiness, 6,716 diagnostics have invalid history
and 2,310 have valid computed scores/confinement. The valid categories are
1,765 both-fail, 354 score-only, 177 confinement-only and **14 joint-pass**.
Six diagnostics are confirmed, matching six typed confirmations. Recorded
transitions include six detector-confirmation entries, four generic moving
candidate cancellations, two local-fill-required reasons, one acknowledged fill
commit and one stable escape exit. These are retained transition descriptions,
not reconstructed callback causes or proof of full behavioral acceptance.

The existing centroid coverage owner reports **zero coverage violations** for
both runs. D's earlier shortened exposure is preserved; nothing here extends it
or repairs the historical monitor outcome. The full typed confirmations retain
candidate centers, so no direction-diagnostic stream was needed. B's epoch route
is explicitly absent in its recorded stationary manifest and was not invented.

## Files for the next bounded replay

Each `B/` or `D/` directory retains `pose_v1.jsonl.gz`,
`centroid_convergence_diagnostics_v1.jsonl.gz`, algorithm state/events, readiness,
clock and timekeeper streams. D additionally retains `v2_search_epoch_v1.jsonl.gz`
and `v2_detector_confirmation_v1.jsonl.gz`. Every row carries the complete
message, source/header and bag timestamps, source validity, readiness membership
and motion-relative time. NaN/Infinity remain explicit tagged values.

Use each `receipt.json` for exact per-stream counts/hashes and `summary.json`
for score/reset/confinement ranges and publication gaps. `state_transitions.json`
and `events.json` provide complete descriptive event payloads. `hashes_before.json`
and `hashes_after.json` are byte-identical integrity receipts within each run.

Final `result.json` binds both run receipts, summaries, integrity records and
execution. Its SHA256 is
`704a599692eb956ccc9b155b5ec51cabdd1a8e0b11aae99c53edcfe1048781ac`.
Prepared manifest SHA256:
`34caf3c1b998b98e49fd56262f5a94edca77f390c9b7c2dbab0786e85d6284f9`.
Execution receipt SHA256:
`b7a1d4a094ab12672ec8c387579ac38194b52efdd42e90decdcfa8f0f46f6653`.

Actual V9 development input is now available for a prospectively bounded
detector replay alongside independent negatives. No runtime detector has been
nominated by this extraction and no new comparison is released. Parent owns
status/handoff and the material development checkpoint.
