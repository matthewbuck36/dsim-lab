# M4 v6 retained incomplete result

Status: CLOSED_INCOMPLETE,2026-09-10 UTC. The single dispatcher, root
session87498, terminated1 after818.281188141 s. Never restart this version,
repeat preparation, replace a slot or import old slots into its denominator.
The V2 goal remains active; both original scientific targets remain unproven.

The frozen comparison used the adopted matched gain profile and previously
validated two-block/continuous-search implementations. Source qualification
passed1285 unique checks with the explicitly documented test-only pin changes,
then preparation53.8155 s and frozen audit4.1997 s passed. Those prerequisites
did not guarantee a completed acquisition.

## Outcome and evidence boundary

Slot1, baseline Arm A, was attempted and is INCOMPLETE. The remaining15 slots
are UNSTARTED. No block science or one-time holdout release occurred. The
existing finalizer retained all16 outcome rows and all192 scheduled direction
rows; none was replaced or discarded. All four research target dispositions
are EVIDENCE_UNAVAILABLE:0/12 latency endpoints,0/6 holdout pairs,0/144 eligible
holdout direction targets. There are48 development and144 holdout direction
rows, all analysis_unavailable with target_ns=None/eligible=False. Missing
medians, availability and stopped-acquisition counts remain unavailable.

The recorder itself completed:48/48 completeness checks passed, no recorded
completeness failures/warnings, final_zero_observed=True, target and bag exit0
with clean_shutdown=True. Its counts include one GaussianFill and one
fill_request. These counts do not establish a completed fill/escape/goal
sequence or scientific success. Standalone resolved_scenario.yaml,
scenario_result.yaml and acquisition/summary_1.yaml are absent. Slot1 lacks
runner_result and independent_inner_cleanup because the enclosing runner did
not finish that evidence path.

Outer process evidence records timed_out=True, work_timed_out=True and return
code254. Its work deadline was51036.458344292; group SIGINT was sent at
51036.45966053. The absolute cleanup deadline was not exhausted. All eight
kernel ownership flags and performed outer graph/identity/session cleanup
passed, with no remaining owned processes or new nodes. Preserve the
distinction between successful outer ownership/cleanup and missing inner
scenario classification.

The console records the bag stopping at10:24:35.728630 UTC. The inner runner
traceback ends in _SubreaperOwner.cancel's sleep at run_scenario.py1054, reached
through specialized boundary cancellation at2075; the outer deadline SIGINT
interrupted that wait. Source record_run.py3017-3022 synchronously runs the
existing validate_run_directory after clean shutdown/console closure and
pre-validation wall_end metadata, before returning its wrapper. Retained
wall_end is10:24:35.925856 UTC; completeness mtime is10:26:31.047267, an
interval of115.121411 s, and final metadata mtime is10:26:31.965260. This
interval includes validation and writes; it is not a per-function profile.
The approximate wall mapping of the outer SIGINT is10:26:26.4, shortly before
completeness publication. These records support a finalization timing collision.

Both outer run_record_process and the inner --cleanup-deadline receive
case_end-30 (run_m4.py254-257); subreaper execution reserves another60 seconds
from that absolute deadline (run_scenario.py2213-2215). The outer therefore
starts cancellation at case_start+810 seconds. Specialized boundary cancellation
adds120 seconds to the45-second graceful wait (2071-2075), but that inner grace
does not protect against the enclosing work deadline. The recorder validator
reads/deserializes all recorded topics before its48 checks; the expensive
operation within that interval remains unmeasured. Do not claim a deadlock or
specific validator hot path. A future correction must address this timing
within the unchanged900/720-second maxima and retain every completeness check.

Live completeness initially read "run did not finalize" while recording and
finalization were pending; the later terminal48/48 result supersedes those
interim observations. The inherited report text about immutable block results
does not mean blocks ran: analysis_blocks is empty. Repeated failure text on
slots2-16 is their unstarted reason, not15 further attempts.

## Retained references

Paths below are relative to
`/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v6/`.

| Evidence | SHA256 |
| --- | --- |
| preflight/contract.json | 815b2e3c0c832f296320471af118e59ba8d189b555d978d45de342b13664b4e0 |
| preflight/dispatch_release.json | 7a69d2e465abdbca4511af6110fa0849a7216707abe53564c509223bb09aff09 |
| acquisition/acquisition.json | 77af3981d1207fb9a6b8ada892ac5b66f50e3767f62a1a0e43f59380411086be |
| acquisition/slot_1.json | 0d776e7fc04084205f3d9557a3c1d09ffa1dc2cf2d2a9788484e5b966efd4c5d |
| report/result.json | 4608a85767b62e5344fb6a8e6761ee5b16cb1122356fb2f28ef3a8bca0bc7aaa |
| report/report.md | 38e613b16a2c86f02b4139654e8e42ffc31e046cb55a0dcc8fdea35ad84ec837 |
| report/report_receipt.json | db9dfac3d6ec7cb2345672635f6e801e24166f487ae232a785b31c1504529875 |

Run root: runs/2026-09-10/m4-pilot-v6-slot01-A-26090801/.
metadata.yaml SHA25601c68568a3cb26fd77f97cf733006316c91b9309be56df359e7d43e3996d22f7;
completeness.json SHA256fc98c78f5014a24884071aba17df30128df4cf13832ae4d3001972af8f300ba7.
The raw bag remains retained, with no post-close bag decoding/replay or field
evaluation performed for this receipt/log audit.

Independent read-only audit verifies all16 exact identities and receipt links,
all192 direction rows/denominators and all631 current source hashes unchanged.
The source and prepared archive manifests remain immutable:
468966710ea77787eec847b61c9fbd7d77de6fd55002e1a7fc8e9769cf25414d and
7712b563463ee5e09ae2442866a69cadb55c8d869adf096d3dd1e8bee66a853d.
Next is material closure archive and a separately bounded, evidence-supported
finalization/cancellation investigation. No new experiment is released.

Git remains feature/gesc-gaussian-robustness-v2 at3369cfc, with all task changes
saved uncommitted. No physical/Pi, V1, commit or push action occurred.
