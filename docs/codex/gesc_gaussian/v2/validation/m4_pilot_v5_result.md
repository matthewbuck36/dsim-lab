# M4 v5 result and postmortem

Status: CLOSED_INCOMPLETE,2026-09-10UTC. Full V2 remains IN_PROGRESS.
The single dispatcher session21069 terminated exit1 after1923.637061631s.
Three development cases are complete; D is incomplete and all12 holdouts are
unstarted. No block science, holdout release, replacement or extra acquisition.
Never restart this version or import its slots into a later comparison.

## Retained case outcomes

| Slot | Acquisition | Behavior | Evidence |
| --- | --- | --- | --- |
| 1 A | COMPLETE/integrityPASS | PASS14/14 | One fill, assisted escape, returnSEARCH and ranked GOAL_HOLD;401.904648893s |
| 2 B | COMPLETE/integrityPASS | FAIL4/14 | No confirmations/fills; fixed StageA360.026simsec expired;507.676428890s |
| 3 C | COMPLETE/integrityPASS | FAIL4/14 | Four confirmations/VERIFY attempts returnSEARCH; no snapshots/fills; StageA360.026simsec;507.923945731s |
| 4 D | INCOMPLETE | Not admitted | Centroid publication coverage gap; seven confirmations, no snapshots/fills;505.335833072s |
| 5–16 | UNSTARTED | Unavailable | Integrity abort before holdout release |

Independent small-receipt audits verified exact identities/configurations and
each complete case's eight frozen input hashes without bag decoding. A passes
48/48 completeness checks, finalzero, recording finalization, target/bag exit0,
all3 performed cleanups and both8/8 kernel proofs. Recording289.311s/720s;
final goal distance0.1413m. Its preferred outside-radius anchor was available,
so the interior alternative was not exercised. Contact evidence is unavailable;
do not infer whole-trajectory clearance.

B passes52/52 completeness checks with10718 centroid diagnostics. Zero
confirmations/fills/escape starts, terminalSEARCH. Recording375.411s/720s;
finalzero/target/bag exit0, all3 cleanups and both8/8 kernel proofs pass.
Outer exit1 is a complete behavioral failure and does not invalidate this case.

C passes60/60 completeness checks. Four typed/legacy confirmations, zero
candidate snapshots/commands/results/commits/legacy requests. Finalzero,
recording, all3 cleanups and both8/8 kernel proofs pass. Small summaries do not
give a specific M3 rejection reason. Strict selected typed lifecycle/source
causality passes; committed-fill authority is unexercised without a commit.

## D integrity stop

D's sole failed completeness check is `motion_interval_coverage`:
`centroid diagnostics have a simulated publication coverage gap`.
The generic dispatcher error `M4 recording or final-zero integrity failed`
does **not** mean finalzero failed. D passes60/61 checks, including finalzero,
clean target/bag shutdown and exit0, typed lifecycle/source causality. Recorder
and runner exit1 reflect invalid recording evidence. Both recorded cleanup
inspections and both8/8 kernel proofs pass; independent-inner cleanup was not
reached after the integrity failure.

The fixed StageA stop is360.060simsec (0.122→360.182). Seven two-block
confirmations occurred, with zero snapshots/commands/results/commits and zero
lifecycle errors. Its state sequence alternates SEARCH/VERIFY and endsVERIFY.
The small receipts identify neither coverage-gap endpoints nor detailed
verification-abandonment reasons. Any targeted extraction requires a separate
prospective finite diagnostic, preserving this result without reclassification.

Read-only source review identifies a prospective cadence mismatch: moving
binding rejects non-SEARCH pose input by resetting, while the pose watchdog
returns outsideSEARCH; the recorder requires centroid publications throughout
the readiness interval. This source finding does not by itself locate the
recorded gap. Preserve the strict coverage requirement; a later source
amendment must cover actual moving verification transitions and inactive
diagnostic validity, timestamp/identity, reset/stale behavior and legacy modes.

## Report, provenance and next boundary

The canonical external `pilot/m4_pilot_v5/report/` contains all16 outcomes and
192 direction rows. Latency endpoints0/12 and pairs0/6; all research targets
EVIDENCE_UNAVAILABLE, including direction0/144 informative eligible holdout
targets, stopped-acquisition attribution and combined holdout sequence.
No independent scientific analysis ran, so supplemental time/path/jitter/lag
metrics remain unavailable. Operational A goal distance above is separate.
Seven D confirmations do not prove earlier independently labeled detection.

| Artifact | SHA256 |
| --- | --- |
| Contract | `42a7b57afcec26e8e4b643cacc0d71895e037c7b3129cb66cd37e26d0580f08e` |
| Acquisition | `acdb571e722f5c800a9188a312c16418f8a8b9ee3afd3c99a57d3b148531bf8c` |
| A slot | `81cfcb96da819556813d018c59369f8a426ed45104b4e52d9131a30c55005cfd` |
| B slot | `2efc7621f68b5070b2ea07dacedd67045e420e4e789346e00ad6c1efc81b052c` |
| C slot | `d12975279e3e7001980f26b677d6f5db258e8df2f25b80c188d4bf65d67ca292` |
| D slot | `55d34fac9e8aaac1768bdaa860c9350737581854c62efa4838f5a055186240fc` |
| Report result | `b2ae800234ae75f470d8974572a7ccd28ade8be8e7262e7505d6893bd79adeee` |
| Report markdown | `28489edd9767038167aeee44d12e7b97c87f01421f3adf042d473ebed27ea4d9` |
| Report receipt | `90d04456d75a76242c56af35542bc7e5ab230fe202282f49f4eeac24008a792f` |

One `timeout 60s /usr/bin/python3` invocation of external
`builds/m4_v5_moving_fill_v1/closure_audit_v1.py` passed5.009936803s,
session85499 terminal0. All623 source pins match before/after the attempt;
87 closed pilot files/1276218104bytes are hashed, all16 slot/ledger identities
match and complete input receipts verify. No bag decoding or science rerun.
`pilot_closure_audit_v1.json` SHA256
`b4b7f13c5250ef8243e8c5a7205d38f2ee94c6cce899ae22cd72d464968bd109`.

Next: material closure archive, separately bounded diagnostics and source
correction, then a fresh version under the saved preparation/release contract.
Do not tune the closed comparison, relax coverage/evidence guards or erase
the B/C failures. Both original goals remain open. Branch stays
feature/gesc-gaussian-robustness-v2 at3369cfc; all task changes saved uncommitted.
No physical/Pi, V1, commit or push action occurred.
