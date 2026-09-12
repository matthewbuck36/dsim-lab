# M4 v7 retained incomplete result

Status: CLOSED_INCOMPLETE, 2026-09-10 UTC. Dispatcher session5888 returned1
after966.142382783s; acquisition962.275019487s. Never resume this version,
repeat preparation, replace a slot or import prior slots into its denominator.
The V2 goal remains active; both scientific goals remain unproven.

## Outcome

| Slot | Acquisition | Evidence |
| --- | --- | --- |
| 1 A | COMPLETE, integrityPASS, behaviorFAIL | 48/48 recorder checks;5/14 behavior predicates; one confirmation/fill/escape start, no later SEARCH |
| 2 B | INCOMPLETE | 51/52 recorder checks; event-causality routing defect; original failed receipt retained |
| 3–16 | UNSTARTED | Dispatch aborted after B; no replacements |

No development science or holdout release occurred. The existing finalizer
retains all16 rows and192 scheduled direction targets. Every scientific gate
is EVIDENCE_UNAVAILABLE:0/12 independently labeled latency endpoints,0/6 pairs,
0/144 eligible holdout direction targets. Missing metrics are unavailable,
not zero. Repeated failure text for unstarted rows is their unstarted reason,
not fourteen additional attempts.

Both acquisitions have finalized recorder metadata, target/bag exit0 and
clean_shutdown=True, final_zero_observed=True, and successful inner/outer
kernel ownership and performed graph/session/identity cleanup. Neither work
nor absolute deadline was exhausted. A's inner recorder returned0; B's
returned1 because completeness failed. The enclosing behavioral runner returns1.
A includes successful independent_inner_cleanup; B aborts acquisition before
that redundant independent check is admitted. Its saved inner and outer cleanup
receipts nevertheless pass. No live Gazebo/recorder/dispatcher was found after
terminal closure. Source636-map closure audit is recorded separately.

A reached Stage A360.026 simulated seconds (0.125→360.151), terminal
ESCAPE_ASSIST, no completed recovery episode and no Stage B. It recorded one
confirmation, one legacy fill request, one Gaussian fill and17 AlgorithmEvents.
The escape-command evaluator requires a later SEARCH boundary; its zero sample
fields do not independently prove absence of assist commands. A's full slot
was479.304932790s, inner recorder404.527s; graceful signal to inner exit36.395s
includes shutdown/finalization. No isolated validator duration was recorded.
This is selected successful finalization, not a controlled speedup benchmark.

B reached Stage A360.060 simulated seconds (0.311→360.371), with no later
SEARCH boundary or completed recovery episode. Its existing scenario result
materializes one confirmed convergence, fill creation and escape start. Because
recording integrity failed, B remains INCOMPLETE and its comparison behavior
field remains unavailable; no post-close reclassification is performed.

## Causality diagnosis

B completeness has exactly one failed check, algorithm_event_source_causality,
for event_type20 at bag time1789041919172055296ns, source353.90000000000003s,
source_timestamp_valid=True. Legacy /gesc_gaussian/fill_requests has0 messages;
/gesc_gaussian/v2/stationary_fill_requests has1. These are selected distinct
protocols, not missing aliases.

The SAME original completeness already passes stationary_centroid_contract.
Its stationary_centroid_audit binds:

- confirmation run dce58aa63fe34576b430c0754e487f47, epoch1/sequence1,
  source344629000000ns and publication344700000000ns;
- typed request sequence1, source353.90000000000003s, publication353900000000ns,
  origin0, deadline358900000000ns;
- active fill1/cluster1/revision1 and matching type20 event, both published
 354000000000ns, with exact request association and no terminal failure.

Existing validate_run.py computes that typed audit around908–923, but its
nonmoving robust-profile causality branch around1134–1136 passes only the
legacy request topic to fill_event_source_causality. The selected Arm B falls
through that branch. The original recorded typed audit plus source establish
a routing false positive without another bag decode. A correction must reuse
the selected typed authority, fail closed on malformed/unavailable selection,
and preserve the legacy and moving paths. It must not simply skip event
causality or suppress errors. Any implementation requires a separate adopted
source amendment and meaningful fault regressions.

B's console also retains quaternion candidate-square-root warnings (mag_q2,
later mag_q1). Source inspection shows those NaN intermediate candidates do not
select their equality branch and are not directly copied to the output. The
publisher has no final finite guard; prior selected fixtures passed output
finite/geometry checks despite the same warning. Neither the warning nor those
old fixtures establish validity of every current sample. B's sole recorded
completeness failure is the separate request-causality routing issue. No source
change or extra runtime/analysis was performed during the frozen comparison.

## Retained references

Paths are relative to /home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v7/.

| Evidence | SHA256 |
| --- | --- |
| preflight/contract.json | 12865711f2f7e5cd1c7527dd84220333a44e5a8875489e09796caedf71dc7a7a |
| preflight/dispatch_release.json | 12e2e58fd567d892f294374755cce86c0eff91fde042d00c6cbf584d9e068756 |
| acquisition/acquisition.json | 282348c644a98f9008ad0b78c7e611d6fbd87b7ac612ae1dfea8b333948b9ddb |
| acquisition/slot_1.json | 905431f1e613193a82b6a0bb4f1d4def9df2e60052b18b02aa176d50cf04087e |
| acquisition/slot_2.json | 84a4a5f77468b9d0892ee3ba38df0612001e3c5d5e70828486963629f2cab4f1 |
| report/result.json | 1fb6778fcbf385dc2ce9517ff794afb9ab68b6d979b5a0ef90df055fff727172 |
| report/report.md | 70c0eb0364089237694f54b1debcefb93745a8ebee9501aff063037f33c20c44 |
| report/report_receipt.json | 6dd9937470712aa7251f97d05d1df0ec18447566b4035e3ddcd3abf8328e314a |

A completeness SHA2564fb46d46db41be23e0a15f6544b443d880508126f9b31a304d111c511c399c14;
B completeness5e25abcf2a926075f0ffffa0c4ef2cedf69b052d62bd19ea7016d550f36cc798.
Raw bags remain external and unchanged (A303919104bytes; B311218176bytes).
The detailed source/preparation history is retained in
[m4_v7_clock_range_comparison.md](m4_v7_clock_range_comparison.md).

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
