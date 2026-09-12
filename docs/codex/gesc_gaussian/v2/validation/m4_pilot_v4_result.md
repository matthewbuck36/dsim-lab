# M4 v4 result and moving-fill evidence boundary

Status: CLOSED_INCOMPLETE,2026-09-10UTC. Full V2 remains IN_PROGRESS.
Single dispatcher session76091 exited1 after1598.156786s. A/B are COMPLETE
with behavioral failures, C is INCOMPLETE and13slots are UNSTARTED. No block
science, holdout release or replacement occurred. Never restart this version.

| Slot | Integrity | Behavior | Inclusive seconds |
| --- | --- | --- | --- |
| 1 A | PASS | FAIL7/14: one fill/local recovery, no ranked goal by post-recovery cap | 627.797797 |
| 2 B | PASS | FAIL4/14: no confirmation/fill by StageA cap | 491.238070 |
| 3 C | FAIL event request-source causality | Not admitted | 478.356145 |
| 4–16 | UNSTARTED | Unavailable | Unavailable |

## Corrected publication and new failure

C passes canonical confirmation/lifecycle validation with no errors:2typed
confirmations,2legacy convergence events,356canonical status rows,1candidate
snapshot,3fillcommands,3results and1Gaussian fill. This is actual selected-run
evidence for the v4 publication correction, not overall scientific success.

Only completeness check `algorithm_event_source_causality` fails (59/60pass):
FILL_CREATED event20 at source151.41500000000002 lacks a recorded legacy fill
request. Moving mode intentionally uses typed transactions; legacy requests0.
Current helper/caller inspect only legacy request timestamps. Typed lifecycle
metrics separately bind epoch2 start83.3s, confirmation2 source151.415s,
candidate2/PREPARE1 at151.6s, generation1/fill1 commit152.0s and matching
objective/direction acknowledgements152.1s. Do not bypass strict causality;
a correction must derive authority from the complete typed transaction chain.

The same run reaches SEARCH→VERIFY→SEARCH→VERIFY→DESIGN→FAILSAFE, with no
ESCAPE_STARTED, completed local recovery or ranked goal. The small receipts
prove commit/acknowledgement but omit the FAILSAFE detail. Source inspection
identifies a possible shared escape-anchor guard; that is a hypothesis until
the recorded detail is extracted under a bounded diagnostic plan. Do not
silently remove the guard, label this successful escape, or infer an exact cause.

Recorder finalizes complete/finalzero true, target/bag exit0 and clean. Inner
and outer eight-flag kernel proofs and both performed cleanup checks pass.
The dispatcher independent-inner cleanup is not reached after the completeness
failure. Its generic recording/finalzero error does not mean finalzero failed.

All16 slot outcomes and192 direction targets (48development/144holdout) are
retained. No block science: primary latency0/12 endpoints and0/6pairs; direction,
latency, mandatory-stop and combined holdout targets EVIDENCE_UNAVAILABLE.
Missing error/stop attribution is not zero. This partial attempt does not
complete the full comparison/report goal.

## Immutable receipts and next action

External root `/home/mattb/Experiments/GESC-Gaussian/v2/`.

| Artifact | SHA256 |
| --- | --- |
| `pilot/m4_pilot_v4/preflight/contract.json` | `4ab2883e73654bbd2c1a5626fcf296316f790f7c1c3a11de063f8e85d8cf055d` |
| `pilot/m4_pilot_v4/acquisition/acquisition.json` | `8bafc3a481142ef31ef85a3782602ae80b0b8481aa16e7a7d338321a152f4cde` |
| `pilot/m4_pilot_v4/acquisition/slot_3.json` | `a4b93edea229225a3b781eed2e071369c97ff7a9854f6b0ce09d4aea17f97564` |
| `pilot/m4_pilot_v4/report/result.json` | `79b1c03de75fb823783b50e44b0b09bfc8f318fd72e4dce473a11fc3de0b4094` |
| `pilot/m4_pilot_v4/report/report.md` | `079a54908dd5fd36e527b7da4f853746681f114f3db1c9dc634447497b31a536` |
| `pilot/m4_pilot_v4/report/report_receipt.json` | `71e558cad31343c09a2870bedc93b147f2ca358258758aa0f2251be868ae9cd7` |
| `builds/m4_v4_confirmation_mirror_v1/pilot_closure_audit_v1.json` | `70218bb13c270e37406537927e5870f6d12249a885f6b3195bf5e1ee075f561a` |

Closure audit under `timeout 30s python3` verifies618 unchanged source pins,
all-slot/report receipt chains and all73pilotfiles/981393641bytes in2.272495s.
No bag decoding or scientific reevaluation occurred. Known exec is terminal;
no new acquisition is released. Preserve all previous versions and originals.

Next: material closure, a finite read-only event-detail diagnostic, then a
recorded amendment for strict typed request authority and any evidence-backed
escape-policy correction before fresh v5 source/preparation/audit/release.
User authorizes recommended bounded simulation changes; no old-version retry,
physical/Pi, V1, commit or push action is authorized by this document.
