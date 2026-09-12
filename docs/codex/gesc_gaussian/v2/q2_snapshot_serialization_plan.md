# Q2 snapshot serialization correction

Status: CDR timing version CLOSED FAILED_TIMING_GATE; Q2 source milestone open.
The held Q2 integrated run completed981PASS/1FAIL in148.35s; it did not close
the milestone or release fresh qualification. This amendment records evidence
before changing completed M3 owners. Read `q2_policy_runtime_plan.md`, live
status and `validation/q2_policy_runtime.md` first.

## Observed problem and unchanged contract

The autonomous40Hz transport fixture reproduced a cancellation with Gaussian
and composer generations both0. Its retained instrumented run includes the
preceding lifecycle-contract tests:20PASS/1FAIL in24.86s. The result reason is
`epoch context changed`; the worker itself finished in167.500ms. Supervisor
snapshot construction took395.65ms and begin-preparation193.98ms. The last
recorded live check had a valid matching context at500ms source age and408.65ms
steady receipt age. The next invalid context is consistent with readiness
expiry during serialized callback work; the exact context payload was not
instrumented, so that final causal step remains a source-supported inference.
Receipts are under external `builds/q2_policy_runtime_v1/pipeline_timing_diagnostic_v2/`.

Preserve500ms source/pose/state/context/readiness freshness, the original5s
fill-design deadline,12s verification deadline, source identity, canonical
hashes, detached immutable snapshots, registry generations, worker/result
matching and all moving authorization. Keep the corrected autonomous source
fixture and its50s per-case/120s outer caps. Neither more source exposure nor
larger freshness/deadline values is a remedy. No field/model/weight change or
scientific acquisition is authorized by this amendment.

## Narrow existing-owner changes

1. In `ros_esc/v2_lifecycle.py`, introduce a lazy generated-ROS-message clone
   using installed rclpy serialization/deserialization. It must preserve the
   exact message type and wire content while detaching every mutable nested
   value. Unsupported non-message inputs fail; generic Python deepcopy behavior
   is not globally replaced. Small Time/envelope copies remain unchanged.
2. Make `snapshot_sha256` omit `observations` from its first outer traversal,
   then populate the identical existing observation payloads once. Current code
   traverses them twice and discards the first result. Preserve canonical JSON,
   excluded publication fields and every source/admission/objective hash input.
   Preserve the old rejection of malformed observation publication Time fields:
   the discarded first traversal still validated them. Explicitly validate those
   times once without including their values in the final hash.
3. In `supervisor_node/v2_supervisor.py`, construct the local snapshot using
   observation references only during synchronous assembly, then clone the
   whole typed snapshot before hashing, retention or publication. Replace only
   the large complete-message copies for snapshot publication, command snapshot
   assignment and `_send`. Candidate, published message and retained command
   must remain mutually detached exactly as before.
4. In `gaussian_fill_node/v2_fill_runtime.py`, use the same clone for the full
   command retained by `PendingPreparation`. Preserve validation order, original
   receipt/deadline and small result/context/state copies. No new worker, node,
   subscriber, controller or public message layout is needed.

Snapshot/command/result decisions remain serialized within their existing
owners. Faster cloning does not authorize reuse of a mutable published object,
skipping evidence checks or refreshing an input timestamp.

## Fixed validation and closeout

Compare against the original D3 lifecycle hash definition and Python deepcopy,
using generated typed snapshots with0,1,363 and4000 observations. Cover nested
Time/arrays/messages, Unicode, optional NaN/infinities and signed zero; compare
canonical payload and every declared field exactly, using IEEE bits for every
floating-point leaf and exact integers, strings, generated types and array
shapes/values. Record serialized bytes as transport diagnostics. Mutate both
original and cloned nested
objects to prove detachment. Source/admission/objective changes must still alter
hashes while the same excluded publication fields remain irrelevant. Exercise
actual supervisor publication/retained-command ownership and Gaussian pending
support through existing fixtures; do not merely test a clone in isolation.
Restrict cloning to the generated message representations used here. Embedded
NUL strings are not losslessly representable by the installed ROS C conversion;
reject them before cloning rather than silently truncating content. Ordinary
Unicode remains supported. This helper is not a generic Python-object clone.

Run one fixed synthetic timing job under60s:10 repetitions at363 observations
and3 at4000, old deepcopy/two-pass hashing versus the new clone/one-pass path.
Report full snapshot/publication/command copy and hash costs. At the selected
363-observation size require maximum new serialization-path time below200ms
and at least2x median improvement; report4000 behavior separately without a
general real-time claim. Preserve failures, do not repeat for favorable timing.
The existing1000-update direction-core performance job remains closed and is
not repeated by this amendment.

Run focused clone/lifecycle/fill/supervisor regressions and the actual unchanged
autonomous-source pipeline. Retain callback and readiness-age instrumentation
to verify the correction addresses the observed stall. Then run relevant held
integration, update source/installed receipts, validation/status/handoff and a
material checkpoint. Source correctness is not scientific qualification.

## Recorded validation clarification before the timing job

The first independent clone suite is retained36PASS/2FAIL in52.93s at
`builds/q2_policy_runtime_v1/snapshot_clone_contract_v1.log`. Its two failures
are whole-CDR-byte comparisons at string alignment padding, not identified
declared-field differences. The4000-observation snapshot differed at byte109
after its65-byte stream string; the363-observation command differed at byte121
after its frame string. Exact fields/hashes for those two bulk cases still need
verification because their test stopped at the byte assertion.

This explicitly replaces the initial whole-buffer equality assertion with
complete declared-field equality and float-bit preservation, alongside exact
old canonical hashes and mutation isolation. Transport padding is not an input
to the established canonical lifecycle identity. Retain raw serialized-buffer
hashes as diagnostics; do not make runtime hashes depend on them. The fixed
timing population,200ms/2x requirements and all source gates are unchanged;
the timing harness has not executed. This clarification does not excuse any
string, time, array, integer, float-bit, type, canonical hash or ownership change.

A separate source audit noticed that a committed fill result arriving before
the composer's clock is rejected without a queue. That race did not occur in
this reproduced failure and is not part of this serialization change; retain
it for a bounded clock-ordering check before M4. It is not evidence of the
observed cancellation and does not justify speculative transaction changes.

## Fixed timing outcome

The one fixed timing job completed all repetitions and parity checks. Selected
maximum163.631029ms passes200ms, but median speedup1.4752642286544517x fails2x.
Retain this CDR implementation boundary and its failed timing result; do not
repeat it or relax its gates. `validation/q2_snapshot_serialization.md` records
exact evidence and saved per-stage diagnosis. Four cloning stages dominate;
a distinct structural-copy correction may be planned within the same owners.
Actual DDS/integrated checks and Q2 source closure remain pending.
