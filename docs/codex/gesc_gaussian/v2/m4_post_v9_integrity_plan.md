# Post-V9 recording integrity and comparison repair

Status: ADOPTED, 2026-09-10 UTC, simulation only. The active user instruction
authorizes recommended bounded corrections without another choice. This work
continues the original two goals and the approved16-run comparison; it does
not replace research acceptance with source passes or an incomplete pilot.

## Verified entry and retained boundary

V9 is CLOSED_INCOMPLETE:10 COMPLETE/integrityPASS/behaviorFAIL,1 INCOMPLETE,
5 UNSTARTED. Both completed label blocks timed out cleanly; all192 direction
targets and12 latency endpoints/six pairs remain unavailable. The sole dispatcher
is terminal/reaped. Closure audit f3a30ae3c128ab0d6e0e402009a8564a6c697d621ca195f01a72981ff4881a07,
archive fc818ab0a7831dedeee25876fc65faa3b2142b1daf99b091f351ea16250ad759,
context/diff/checkpoint and current645-source hash verification PASS.
All206 pilot files/11 bags are retained. Read the
[V9 handoff](m4_pilot_v9_handoff.md) and
[diagnoses](validation/m4_v9_development_diagnostics.md).

Work on feature/gesc-gaussian-robustness-v2 at3369cfc, preserving uncommitted task
changes. No V1/Pi/physical action, commit/push, old-evidence rewrite or retry.
Existing shared nodes, recorder, graph probe, validator, analyzer and numerical
owners remain authoritative. Preserve legacy selectors, cost sign/units, strict
identity/clock/safety gates, controller ownership and original research targets.

## Milestone D1: identify the21 missing recorded joins

The failed slot11C has59/60 recording checks. Its sole failed synchronized-stream
check has21 copies of `atomic cost lacks selected raw/augmented/provenance join`.
The existing validator at validate_run.py:138–305 checks the full bag before
readiness/motion interval handling. It indexes legacy exact float timestamps and
identity-admitted provenance, then requires all three companions for each valid,
identity-admitted objective. Do not substitute nearest-time or tolerant matching.

Small receipts show10582 raw, source-cost and provenance records,10603 atomic
objectives and10602 legacy augmented records. This difference does not prove
where a record was lost or that publisher/callback delivery was faulty. Three
shutdown transform warnings likewise do not establish the21 errors' cause.

Use one read of the closed
`pilot/m4_pilot_v9/runs/2026-09-10/m4-pilot-v9-slot11-C-26090803` bag through
existing `read_run_bag` and `records_for_alias`. Select exactly these resolved
aliases: raw_cost_legacy, augmented_cost_legacy, source_cost,
v2_source_provenance, v2_objective_cost, timekeeper, clock, recording_ready.
The added source-cost stream distinguishes its paired publications; clock and
readiness provide temporal context only. No topic is clipped to readiness and
no scientific endpoint, detector replay, field/reference/model job or full
recording validator rerun occurs. No other V9 bag is read in this milestone.

Read exact alias/type/count declarations from resolved_topics and bag metadata
before decoding. Maximum40000 rows per selected stream/160000 total; do not
truncate. Preserve every selected record externally as compressed JSONL with
bag, publication and source times, full message payload and explicit tagged
nonfinite values. Reuse the prior diagnostic serializer conventions. Existing
reader may annotate readiness; do not use that annotation to discard records.

Use existing v2_identity_from_metadata, v2_message_identity_error and exact
Timekeeper conversion helpers. For every valid admitted objective report its
exact legacy key (also float.hex), sequence/model/composition/publication/bag
times, provenance identity admission and presence/absence of each required
companion. Retain all unmatched objective payloads, present companions and the
nearest preceding/following recorded keys for each absent companion. Neighbors
are diagnostic context only, never replacement matches. Summarize unmatched
keys' locations relative to first/last recorded streams and readiness, duplicate
and identity-rejection counts, and the exact missing-topic combinations.
The21 count is a baseline to explain, not a condition to force by filtering.
If reproduced count differs, preserve it and explain the scope mismatch.

External exclusive output: `builds/m4_post_v9_integrity_v1/diagnostic_v1/`.
Preserve helper/fixture/plan hashes, exact command and clean Humble→Q2→Q5
installed imports. No ROS initialization/graph probe/daemon is allowed in D1.
Bind the closed V9 archive and all selected original run files including the bag;
verify their hashes and all645 held source bytes before/after/exit. The wrapper
retains nonzero/timeout/partial output and performs bounded child cleanup.

First one45s fixture job checks actual serialized message-like records for:
complete joins; each missing companion separately and combined; exact-key
near misses; rejected provenance identity; duplicate keys; unbound/invalid
objectives; records outside readiness remaining included; and nonfinite tagging.
Then one90s inclusive extraction, with work ending at75s, child exit by85s and
remaining5s for final hashes/receipt. Record actual scopes and outcomes, no
automatic retry or cap extension. These bounds are separate diagnostic work,
not a renewal of V9's failed science allowance. Reuse existing read/identity
owners and prior extraction wrapper patterns; no parallel analysis pipeline.

D1 acceptance is an auditable classification of the missing exact joins with
unchanged source/original files, or an honest retained diagnostic failure.
Record the evidence and concrete repair conclusion before dependent source
changes. A missing recorded prerequisite cannot be repaired by weakening the
validator or reclassifying V9. If the cause is unrecorded delivery, distinguish
the observable boundary from unproven transport causality.

## Subsequent source repair scope

After D1, save the exact justified recording correction and its finite tests in
this amendment before implementation. The following independently established
harness defects also need correction before another expensive comparison:

- Discovery admission: obtain the shared daemon's exact name/namespace from
  installed Humble DaemonNode in a bounded child, require its visibility through
  the existing independent native graph probe, and recheck identity. The full
  observed baseline remains the strict cleanup baseline. Preserve ordinary
  ensure_ros_daemon/default graph behavior, original deadlines and process
  ownership proofs. No wildcard exclusion, fabricated node, cached daemon graph
  substitution or broad kill. Local API calls can block, so the existing5s
  graph envelope must bound all RPC/probe/teardown work.
- Monitor progression: after a completed recovery, a later incomplete typed
  confirmation pair must not restart the old Stage A timer. Keep original Stage B
  and inclusive deadlines running. Pending evidence withholds dependent acceptance;
  contradictory/unresolved final evidence still fails. Preserve the500ms typed
  publication ordering and exact identity rules, with both callback arrival
  orders, intervening odometry and permanent/conflicting misses tested.
- Analysis throughput: preserve numerical semantics, selected observations and
  all error checks while eliminating demonstrated discarded conversion/digest
  work. Any compact intermediate format needs default byte compatibility,
  decoded/canonical identity and actual downstream receipt-consumer tests, plus
  a separately scoped performance measurement before relying on the120s labels
  budget. Retained failed V9 jobs remain untouched.

These outlines define the intended repair direction. Their exact edits/test
selection and any real integration/retained-data performance job are recorded
before execution, based on D1 and existing source evidence. Work one validated
milestone at a time; do not bundle speculative algorithm tuning with recording
repairs. Preserve the failed direct-alignment gate and add rejection diagnostics
only if separately scoped. No new16-run experiment is released by this plan;
its source, budget feasibility, frozen prerequisites and fresh identity must
be concrete and verified first. Full goal remains active until original
requirement-by-requirement acceptance and final report are satisfied.
