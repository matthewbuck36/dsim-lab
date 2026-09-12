# M4 v7 incomplete acquisition handoff

M4v7 is CLOSED_INCOMPLETE, 2026-09-10 UTC. Full V2 remains IN_PROGRESS.
Read [the result and diagnosis](validation/m4_pilot_v7_result.md), newest
status and any later adopted amendment. Both original research goals remain
open: faster settling/trapping detection and better GESC direction while moving
without mandatory stopped acquisition.

The single dispatcher, root session5888, is terminal1 after966.142382783s;
its acquisition receipt measures962.275019487s. Slot1 A is COMPLETE with
integrityPASS and behaviorFAIL. Slot2 B is INCOMPLETE because the selected
stationary typed request is omitted from the later legacy event-causality
check. Fourteen slots remain UNSTARTED, with no analysis blocks or holdout
release. Never resume this fixed version or replace/reclassify its slots.

A passes48/48 recorder checks. B passes51/52: its existing typed stationary
contract already matches the fill event to the unique recorded request, but
algorithm_event_source_causality incorrectly falls through to the empty legacy
request topic. This is a source-supported validator selection defect; B's
original failed completeness remains unchanged. Both runs finalized with
clean target/bag exits, final zero and inner/outer ownership/cleanup proof.
Neither exceeded a work/absolute deadline. Both reached the360s Stage A limit
without a completed escape-to-SEARCH sequence; integrity repair would not
establish behavioral acceptance or scientific success.

The report retains16 outcomes and192 direction targets, with0/12 latency
endpoints,0/6 pairs and0/144 eligible holdout targets. Both goals remain
EVIDENCE_UNAVAILABLE. No post-close replay or model evaluation was performed.

External root: /home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v7/.
Contract SHA25612865711f2f7e5cd1c7527dd84220333a44e5a8875489e09796caedf71dc7a7a;
acquisition282348c644a98f9008ad0b78c7e611d6fbd87b7ac612ae1dfea8b333948b9ddb.
Material closure audit/archive follows. A separate saved source amendment and
fresh experiment identity are required for any correction/acquisition.

Git remains feature/gesc-gaussian-robustness-v2 at3369cfc with saved uncommitted
task work. No commit/push, V1, physical snapshot or Pi action occurred.

## Closure audit

Finalized closure audit PASS (not experiment acceptance),0.660437915s/60:
`builds/m4_v7_clock_range_comparison_v1/pilot_closure_audit_v1.json`
under the external V2 root, SHA256
`e5eac2ddd288d15600b2b7c17778b9e08bf1a858d72393fb571429a9b2e9bf9f`.
All636 frozen sources match; exact1COMPLETE/1INCOMPLETE/14UNSTARTED and
all192targets are retained. B has saved successful scenario-inner and outer
cleanup, but no later independent_inner_cleanup receipt; do not claim all
three passes for B. Original completeness, metadata and reports are unchanged.
Material closure checkpoint/archive is next; no source correction yet.

## Material closure and next source milestone

V7 material closure PASS: checkpoints/m4_v7_closed_incomplete_v1/manifest.json
SHA256ea3fa730800fc55d7d07878b2794c9c39e578a113b80e876898f65061d4f1359,
400repository files/860refs/1571813-byte verified tar. Original2recordings,
16outcomes/192targets remain unchanged. New source amendment ADOPTED:
m4_v8_stationary_causality_plan.md. Reuse selected typed stationary authority
in the existing validator before legacy fallback; preserve strict legacy/moving
checks. Baseline fixtures and source tests precede one read-only retained-B
verification. No V8 identity/preparation/acquisition admitted; no process live.
