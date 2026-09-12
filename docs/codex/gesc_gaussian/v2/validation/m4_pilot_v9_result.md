# M4 V9 comparison result — closed incomplete

Status: CLOSED_INCOMPLETE, 2026-09-10 UTC. Full V2 remains IN_PROGRESS.
The sole dispatcher session77764 is terminal1 and reaped. Ten slots are COMPLETE
with recording integrity PASS and overall behavior FAIL; slot11 is INCOMPLETE;
slots12–16 are UNSTARTED after the required integrity abort. Both completed
science blocks have unavailable results after their saved labels deadlines.
All16 outcomes and192 scheduled direction targets are retained in the finalizer's
immutable report. Neither original research goal is demonstrated. Closure records
this fixed negative attempt; it does not satisfy the full V2 objective.

## Purpose and fixed design

The two original goals remain faster settling/trapping detection, including
circling/oscillation, and reliable GESC direction during continuous motion
without mandatory stopped acquisition sweeps. The selected two-block method
uses six time-weighted centroids (6 s each), comparing the means of the oldest
and newest three; threshold .18 m and confinement radius .50 m. Selected moving
search uses rolling_gesc_v2/moving_cycle_coherence_v1 with mean weight .75.
Legacy PDE and five-shift modes remain selectable. These are simulation choices,
not physical calibration or established performance improvements.

Within each block, A uses inherited detector/stationary search; B uses two-block
detector/stationary search; C uses inherited detector/moving search; D uses both
improvements. Geometry, initialization, gains and limits remain matched within
the block. Four primary development runs use seed26090801. Twelve secondary
holdouts use nominal seed26090802, sensor noise .015/seed26090803, and .10 s
sensor-plus-pose delay/seed26090804. Selected V6 controller gains/limits and
all original observation, recording, cleanup and scientific gates stay frozen.
Details: [adopted execution plan](../m4_execution_evaluation_plan.md),
[V9 amendment](../m4_v9_budget_comparison_plan.md), and
[source/live validation](m4_v9_budget_comparison.md).

## All sixteen reserved outcomes

These are terminal classifications. Slot11's inner diagnostics remain separate
from accepted comparison input; later slots were released but never attempted.

| Slot | Block | Arm | Acquisition | Recording checks | Behavior |
| --- | --- | --- | --- | --- | --- |
| 1 | Development nominal | A | COMPLETE | PASS 48/48 | FAIL 4/14 |
| 2 | Development nominal | B | COMPLETE | PASS 52/52 | FAIL 4/14 |
| 3 | Development nominal | C | COMPLETE | PASS 60/60 | FAIL 4/14 |
| 4 | Development nominal | D | COMPLETE | PASS 61/61 | FAIL 7/14 |
| 5 | Holdout nominal | A | COMPLETE | PASS 48/48 | FAIL 7/14 |
| 6 | Holdout nominal | B | COMPLETE | PASS 52/52 | FAIL 7/14 |
| 7 | Holdout nominal | C | COMPLETE | PASS 60/60 | FAIL 6/14 |
| 8 | Holdout nominal | D | COMPLETE | PASS 61/61 | FAIL 7/14 |
| 9 | Holdout noise | A | COMPLETE | PASS 48/48 | FAIL 4/14 |
| 10 | Holdout noise | B | COMPLETE | PASS 52/52 | FAIL 4/14 |
| 11 | Holdout noise | C | INCOMPLETE | FAIL 59/60; outer cleanup FAIL | Unavailable; inner FAIL 3/14 retained |
| 12 | Holdout noise | D | UNSTARTED | Unavailable | Unavailable |
| 13 | Holdout delay | A | UNSTARTED | Unavailable | Unavailable |
| 14 | Holdout delay | B | UNSTARTED | Unavailable | Unavailable |
| 15 | Holdout delay | C | UNSTARTED | Unavailable | Unavailable |
| 16 | Holdout delay | D | UNSTARTED | Unavailable | Unavailable |

All four finalized development runs pass final-zero, clean target/bag exit and
the required inner/outer/performed cleanup proofs. A/B have zero confirmed
detections or fills. C has four confirmations and no candidate snapshot or fill.
D has six confirmations and one committed fill followed by direct repulse and
return to SEARCH. D ends VERIFY without a ranked GOAL_REACHED event. Its final
global distance .252151 m alone does not satisfy the goal contract.

D also retains a live centroid-event timestamp matching error: five live
confirmation bindings versus six final recorded-data bindings. Although the
final recording validation passes, this run does not establish a full 300-second
post-recovery observation. The exact monitor error, timing scopes, transaction
authority and recovery association are retained in the linked validation.

Nominal holdout A has one confirmation, one legacy fill request, one fill and
one assisted recovery. ESCAPE_STALLED precedes ESCAPE_ASSIST, then ordinary GESC
search resumes. Stage A completes; Stage B runs222.529–522.545 s and expires
after300.016 s. No live monitor error is recorded. Final global distance .101494 m
and observed proximity .499508 m do not qualify a goal because no valid ranked
GOAL_REACHED occurs. Final state is SEARCH. All recording/final-zero/cleanup
checks pass; case658.991910 s is within900. Its seven passing behavioral
predicates establish local recovery/escape ownership/fill cardinality and the
recording/cleanup/no-forbidden-state/event requirements, not full goal success.

Nominal holdout B has four centroid confirmations, one successful typed stationary
fill request and one assisted recovery. It ends VERIFY without ranked goal,
despite final global distance .160397 m. The live monitor repeats the development
D limitation: Stage B advances209.616–389.952 s before a missing typed companion
clears Stage A and triggers its expired timer (389.946 s elapsed). Final matching
binds all four confirmations; recording and cleanup pass, but a full300-second
post-recovery observation is unavailable. Case514.425923 s remains within900.
Its seven passing behavioral predicates have the same limited scope as slot5.

Nominal holdout C has seven PDE confirmations, one candidate snapshot and one
committed fill. A direct-repulse recovery completes and Stage B observes the
full300.016 s (332.018–632.034), with no live monitor error. The escape-ownership
predicate fails with the retained reason `direct measured fill-to-exit alignment
is below 0.80`; the failed numeric alignment is absent from these outcome receipts.
No ranked goal qualifies proximity .497523 m; final state SEARCH/globaldistance
.251141 m. Six behavioral predicates pass. Recording/finalzero/cleanup pass and
case801.423983 s stays within900. Direction diagnostic counts do not establish
direction accuracy. A sensor-pose sqrt warning appears in the retained console;
passing completeness console checks do not imply a warning-free run.

Nominal holdout D has five confirmations, one candidate snapshot and one fill,
followed by assisted recovery. Escape alignment .996610 and both handoffs pass.
The monitor limitation recurs: four live versus five final centroid matches;
Stage B225.910–375.816 s precedes reactivated Stage A timeout375.462 s elapsed.
The full300 s post-recovery window is unavailable. Final stateVERIFY/global
distance .245973 m; proximity .498932 m remains unqualified without ranked goal.
Seven behavioral predicates pass, within the same limited scope as slots5/6.
Recording/finalzero/cleanup pass; case508.719748 s stays within900.

Noise holdout A remains in SEARCH with zero confirmations/requests/fills/recovery.
Stage A expires after360.026 s; Stage B never starts. Final globaldistance3.769821 m,
no monitor error. Recording/finalzero/cleanup pass; case475.598108 s stays within900.
Its durable captured cost JSON exactly matches frozen sigma.015/seed26090803
configuration87e2ea96...ffcb6. Only the witnessed temporary cost-path relocation
differs from planned argv; metadata's baseline parameter-file listing is not the
effective noisy-configuration authority.

Noise holdout B likewise remains in SEARCH, with zero confirmations, typed
requests, fills or recovery. Stage A expires after360.026 s; Stage B never starts.
Final globaldistance3.614588 m; no final or live timestamp-binding error. All52
recording checks/finalzero/cleanup pass, case480.726527 s within900. The captured
noisyJSON/frozenhash and sole argv relocation match exactly. Its10,651 centroid
diagnostics are message counts only: these receipts lack a score/eligibility
breakdown, so they do not identify the cause of non-detection.

Noise Cslot11 has two independent integrity failures. Outer cleanup compares an
empty baseline with a final graph containing only
`/_ros2cli_daemon_201_43f547f7f0ec4c73834cdd093a15b9c9`. All earlier outer baselines
and slot11's inner baseline contain that same daemon. Outer owned/session survivor
lists are empty, inspections are performed without errors, and both inner/outer
eight-flag kernel proofs pass. The inconsistent discovery baseline is a source
diagnostic; the strict failed result remains unchanged. No independent-inner
cleanup was performed after that outer exception.

Separately, inner recording fails `v2_synchronized_stream_contract`:21 atomic-cost
records lack the selected raw/augmented/provenance join. The scenario therefore
records `recording_evidence_invalid`, even though59 other checks, final zero,
clean target/bag exits and inner cleanup pass. Three shutdown-time
`transform_original_receipt_expired` warnings do not establish the cause of the
21 joins. The actual inner summary/scenario/metadata/completeness remain retained
under `runs/2026-09-10/m4-pilot-v9-slot11-C-26090803/`; the outer slot omits their
attachment because it failed first. These files are not promoted to valid input.

Inner behavioral diagnostics show four PDE confirmations/four VERIFY visits,
five epochs, no candidate snapshot/transaction/fill/recovery, then SEARCH.
Stage A expires after360.026 s; no Stage B starts, final globaldistance3.595541 m.
Only3/14 inner predicates pass. Case516.167809 s is within900; neither process
deadline expires. Noise JSON retains the exact frozen87e2ea96...ffcb6 hash.
Read-only process inspection found none of43 unique receipt-owned PID/start
identities remaining and no PID reuse. This does not waive the graph or recording
failure. No replacement, retry, deadline extension or post-freeze tuning occurred.

## Scientific results and denominators

Development labels reached the original work deadline; the child terminated
cleanly after113.399111326 s, with the whole block taking118.648928269 s under220.
All four scientific rows are EVIDENCE_UNAVAILABLE (`labels_analysis_timeout`).
References and summary were skipped for `no_complete_frozen_label_inputs`.
Partial A/B/C files are retained without promotion to completed scientific input.

Nominal labels likewise time out with clean termination: child112.657976764 s,
block118.631022823 s under220. All four nominal scientific rows are unavailable
for labels_analysis_timeout; references and summary are skipped for missing
complete frozen label inputs. This leaves the four nominal latency endpoints
unavailable under the all12-endpoint acceptance rule. Partial artifacts remain
separate from completed measurements; the original analysis is not retried.

No detector improvement can be inferred from confirmation counts alone. Primary
latency acceptance requires all12 independent holdout endpoints/six B/A and D/C
pairs and >=30% median improvement without added wrong fills/goals. Missing or
censored endpoints and unknown error attribution remain explicit.

Direction reporting must retain all192 scheduled targets (48 development,
144 holdout), with exposure, input qualification, reference informativeness and
output-availability denominators. The final report contains192 explicit
`analysis_unavailable` rows,24 for each C/D slot, preserving48 development and144
holdout targets. The reported zero qualified/informative/exposed counts describe
unavailable analysis, not measured absence of robot exposure. Median <=30 degrees,
p90 <=60 degrees and availability >=80% remain unproven. Message counts do not
qualify those metrics. Slots9–16 have no completed science block; this differs
from the explicit labels-timeout rows for slots1–8.

| Acceptance | Final evidence |
| --- | --- |
| A01: >=30% latency reduction, no added wrong fills/goals | EVIDENCE_UNAVAILABLE:0/12 observed endpoints,0/6 pairs; medians/reduction/error attribution unknown |
| A02: direction median/p90/availability targets | EVIDENCE_UNAVAILABLE: all192 targets retained, all144 holdout analyses unavailable |
| A03: zero mandatory stopped acquisition | EVIDENCE_UNAVAILABLE: eight C/D counts are null; natural reversals/safety/goal stops cannot be inferred from missing attribution |
| A04: complete combined sequence in every holdout | EVIDENCE_UNAVAILABLE: nominal D has partial recovery evidence; noise/delay D unstarted; none qualifies the full sequence |
| A05: goal time/path/jitter/lag/fallback and failures | All16 rows/failures/denominators reported; all supplementary scientific values unavailable |

The finalizer's six latency-pair records retain nominal timeout reasons; the
noise/delay endpoint objects are empty because those blocks never ran. Their
planned endpoints remain in the12-endpoint denominator. Mandatory-stop and
combined-sequence unknowns are null, not zero or passes. Operational confinement
labels are not certified cost-basin membership; stationary periodic GESC
references are not spatial gradients. No broad robustness or physical result
follows from this simulation-only selected-condition comparison.

## Evidence and recovery

External root: `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9/`.

| Receipt | SHA-256 |
| --- | --- |
| preflight/contract.json | 623b6ffa1b8795582138d7d39374ae04f52788beb7c211278ab58a9ee3a0a022 |
| preflight/dispatch_release.json | 43dce36fc62feafd676782c170e7544e0ecf42c02aa14892b1707fd1eca6fd60 |
| analysis/block_0/block_receipt.json | bcfacffe508b75bedd3fd51a4ad3ad4d1072b467c51c996698b5f3f6243cb67f |
| analysis/block_0/unavailable_result.json | 35165efda6c1492f7d1b7021dc2c28c4c621f538e30fff93cd819bf00b609dff |
| preflight/holdout_release.json | 4d877ad7f72c632d7df93a88302cb1d36dd3f2576f091dbed3032fde522d0bf6 |
| analysis/block_1/block_receipt.json | b61415ba53611bf4735e9674941843fa461c8e50e2c88c104f028e5fbb411b17 |
| analysis/block_1/unavailable_result.json | 1bb60fa9f1959ef306c277e92921361040042733ca7d86cb01d5a00fc61f3a39 |
| acquisition/acquisition.json | f7c27eefe94e8f1d987f05f8f1bfe5e57c85a7595bec58da0eac5b303419ca8a |
| acquisition/slot_11.json | f6278450f32c5edb6fce3c4318ed2006a33c86b04e758ed7b9bb0169f9ffec8f |
| report/result.json | 8258857924192c9e3ac294960fd70638737f5a7ca3df1b7cb1823ef58e9ea323 |
| report/report.md | 2fbe3c6b73e044e70acb5556fde04ea7fd4996f445609c738de78166cc9b1037 |
| report/report_receipt.json | b4564b2474420aae9efee407b9cbee308163b4673388213b9a80aa36146ae4f8 |

Source milestone:1333 unique PASS cases/18 modules,645 held sources and21 installed
bindings, actual CLI PASS. Source aggregate e65ef0e6e0a7c3751213d3a4e6b21e4fa6cf4a7bd02982695b175bfd1c93c98a;
prepared archive e07eaa2f3839d081f44e3c1fb42b7e866d0ef6d01c849df2ca960d5604dedbc2.
These source/preparation passes are not scientific acceptance. Detailed exact
commands, timing, prior source failures, case hashes and preserved V1–V8 evidence
are linked from current validation/status. This prose is outside frozen sources.

The exact sole dispatcher command is retained in
`builds/m4_v9_budget_comparison_v1/acquisition_owner_v1.json` under the external V2
root. Outer execution took6165.657050622 s, internal acquisition6161.857533948 s,
final report1.221787284 s; all stayed inside their original budgets. Execution
receipt SHA25627fb4954b96cd19dbdb0344fc5271cd4a915e3f45bb83877a85058ff62b93192.
All206 pilot files, including11 raw bags totaling4155301888 bytes, are retained.
No bag replay or model computation was performed for this closure audit.
Read [closure handoff](../m4_pilot_v9_handoff.md), the exact validation record and
the [post-comparison diagnoses](m4_v9_development_diagnostics.md) before proceeding.
Any correction needs its own saved bounded amendment and fresh evidence; V9 and
all prior fixed failures stay immutable. Closure audit/checkpoint/archive receipts
are recorded below and in the handoff once completed.
Branch feature/gesc-gaussian-robustness-v2 remains at3369cfc83a64ff5d8354827fd5310caaf0c8e945;
task changes are saved uncommitted. No V1/Pi/physical change or commit/push occurs.

Closure audit PASS, 2026-09-10 UTC: external
builds/m4_v9_budget_comparison_v1/closure_audit_v1.json SHA256
f3a30ae3c128ab0d6e0e402009a8564a6c697d621ca195f01a72981ff4881a07.
The sole audit took0.452959323 s internally/0.515175102 s enclosing under30 s.
It verifies645 current source pins,101 selected small-file references and490
receipt-owned PID/start identities with none remaining or reused. The identity
population includes analysis children as well as acquisition owners; the separate
486-identity run-only review and43-identity slot11 review have narrower scopes.
All206 pilot files/11 bags,16 outcomes/192 targets and both slot11 failures are
accounted for. Raw bag hashes are deferred to the material archive, without any
bag decoding or reanalysis. Context validator and git diff --check PASS.

Existing checkpoint_phase.sh v2 PASS,0.216754284 s under30; exact command/result
in externalbuilds/m4_v9_budget_comparison_v1/closure_checkpoint_execution_v1.json.
One reviewed60-second material archive is next; no source or evidence changes.

Material closure archive PASS, 2026-09-10 UTC: external
checkpoints/m4_v9_closed_incomplete_v1/manifest.json SHA256
fc818ab0a7831dedeee25876fc65faa3b2142b1daf99b091f351ea16250ad759.
The sole archive completed10.210715831 s under60:420 repository files,
398 external references,1680256-byte verified source tar. Every206 pilot file
and all11 raw bag files are retained as hashed external references; existing
recorded bag hashes agree. Source645 pins and artifact inventories/signatures
remain stable. No bag decoding/reanalysis, source change or evidence rewrite.
Independent claim/helper audits, context/diff,26 local report/navigation links
and repository checkpoint PASS. Exact archive command/timing is in
builds/m4_v9_budget_comparison_v1/closure_archive_execution_v1.json.
This final receipt is appended after the immutable archive; it does not alter
archived evidence. Fixed V9 closure is complete; full V2 and both research goals
remain IN_PROGRESS. Next: adopt a bounded post-V9 correction/diagnostic plan
before source changes or retained-data analysis. No new comparison is released.
