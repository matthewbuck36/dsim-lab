# M4 v3 result and confirmation-evidence postmortem

Status: CLOSED_INCOMPLETE,2026-09-10UTC. Full V2 remains IN_PROGRESS.
The single dispatcher exited1 after1394.491043s, within its15300s suite cap.
Slots1A and2B are COMPLETE; slot3C is INCOMPLETE and13slots UNSTARTED.
No replacement, block science or holdout release occurred.

## Outcomes and limits

| Slot | Acquisition integrity | Behavior | Inclusive seconds |
| --- | --- | --- | --- |
| 1 A | PASS | PASS14/14 predicates | 413.875127 |
| 2 B | PASS | FAIL4/14; zero confirmations/fills by fixed360s StageA timeout | 491.340042 |
| 3 C | FAIL lifecycle evidence | Not admitted | 488.514112 |
| 4–16 | UNSTARTED | Unavailable | Unavailable |

Slot3's recorder finalized with complete metadata, observed finalzero and clean
target/bag exit0. Its completeness passed59/60 checks; the only failing check
is `v2_lifecycle_contract`, with four occurrences of `legacy confirmation
snapshot lacks canonical observation mirror`. Both inner/outer eight-flag
kernel proofs and performed inner/outer cleanup pass. The later dispatcher
independent-inner inspection was not reached; do not claim it passed.
The generic dispatcher error `M4 recording or final-zero integrity failed`
must not be interpreted as missing finalzero here.

Four live legacy detector confirmations occurred with moving search selected;
there were no accepted CandidateSnapshot messages or fills. The fixed StageA
timeout360.026sim seconds ended the run. This is not an admitted scientific
latency/direction result. The mirror defect is separate from insufficient
moving evidence and does not justify loosening candidate safeguards.

All16 slots and192 scheduled direction rows (48development/144holdout) remain
in the report. Primary latency has0/12 observed endpoints and0/6 pairs. No
direction, latency, mandatory-stop or combined holdout target is established;
missing attribution cannot count as zero errors. A successful report write
does not complete this failed partial comparison or the full user goal.

## Defect and next boundary

Read-only source inspection finds the legacy detector publishes its canonical
status before updating qualified dwell. At confirmation the status still has
count_remaining1; the event and typed legacy_snapshot use the updated0.
The strict lifecycle evaluator requires an exact eight-field canonical mirror
and rejects this mismatch. The live moving supervisor consumes the typed
confirmation independently, so fixing the mirror alone does not establish
moving verification success. Preserve the completeB behavioral failure.

Next is material closure, then a separate source amendment fixing canonical
publication consistency with old modes selectable, strict validation intact,
matching actual producer/transport regression, and a fresh versioned16-slot
comparison after its source/preparation/audit/release gates. Never restart or
reinterpret M4v3, import old data into replacement slots, or retune frozen runs.

## Receipts

External root `/home/mattb/Experiments/GESC-Gaussian/v2/`.

| Artifact | SHA256 |
| --- | --- |
| `pilot/m4_pilot_v3/preflight/contract.json` | `f035a5c7de675d505f10952d06e55ad77166ee235512f8e10f5069cbf92918fb` |
| `pilot/m4_pilot_v3/acquisition/slot_3.json` | `ee37cf3d358f6fc8f8c7bfdeb20049ae224e12e0698719ce765b6854487057fe` |
| `pilot/m4_pilot_v3/report/result.json` | `6ada287ca5c274f31aaca09ef2ad9a40d1e0f5eae8beab746911642f2266684a` |
| `pilot/m4_pilot_v3/report/report.md` | `d9a3db7dd01b25f31cef74d2f37f718e11925ee74719f8ae5a5a86c5562c1cef` |
| `pilot/m4_pilot_v3/report/report_receipt.json` | `65624a4c121e2cdd35073f8a65215d008eb70008e231f6b4d91a0868beee62c4` |
| `builds/m4_v3_recorder_shutdown_v1/pilot_closure_audit_v1.json` | `04c263b617a6681621279bbbf6130e5926c4f732201d6077d00f7ca04c2a1a86` |

Independent audit verifies615 unchanged source pins, report/result receipt
chains and all73 pilot files/942803553bytes in2.138086s without scientific
reevaluation. Its initial audit-only equality assertion included the external
slot self-receipt; corrected checks compare the payload and independently hash
that receipt. No evidence or scientific output changed. Known dispatcher/case
identities are absent from procfs after terminal exec session99719 exit1.

Git remains feature/gesc-gaussian-robustness-v2 at3369cfc with task changes
saved uncommitted. No physical/Pi, V1, commit or push action occurred.

Material closure archive `checkpoints/m4_v3_closed_incomplete_v1/manifest.json`,
SHA256 `1553acb3257e96c612193c94d8460b37fbbd239384638020e59b0557cc7c9895`,
binds349 dirty/untracked files and141 artifacts with1378951-byte verified tar.
Context/diff/checkpoint passed. This receipt postdates the immutable archive.
