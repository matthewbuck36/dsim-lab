# R24 retained C11 validation: complete

The existing full validator passed all61 checks on the original C11 recording
with `write_report=False`. Only v2_lifecycle_contract and
algorithm_event_source_causality changed; the other59 check objects are identical.
No warnings. The derived lifecycle metrics change consistently with the admitted
earlier guidance row. The entire report is not claimed identical.

Sole92663 terminal/reaped0 in43.668513s under120s INT plus5s kill. One existing
validate_run_directory call, no alternate validator/science/runtime call. All567
source/input hashes and raw file stats remained stable. Original ten non-bag run
files, old completeness/metadata flags, acquisition and scenario results are
unchanged. No raw hash rescan. The corrected recording view separately qualifies
a measured baseline failure; original C11/V14 remain INCOMPLETE, and C11's
360.026s Stage A no-fill/no-arrival does not become success.

External work root: development/20260911/r24_retained_c11_validation_v1/ under
/home/mattb/Experiments/GESC-Gaussian/v2/.

- New report: validation_v1/revalidated_completeness.json, SHA256
  0ed9e004935eee86d49a2714d9221b54e03cebf26b08814dcf146e459d04961d.
- Execution receipt: validation_v1/receipt.json, SHA256
  e40e391f9cbaab3e9f167f56c14fd4d89818131bd9e2a6add30ec01dcc6d7da3.
- Independent review: result_review_v1.json, PASS27 in0.334s, SHA256
  b675844ca607c3fe2ef238776ea75989e2a98e0adb0adf6510d2fe984eb0fa76.

The exact invocation used the existing R21 environment and
`timeout --signal=INT --kill-after=5s 120s /usr/bin/python3 -B` with
the retained validate_once.py. R23's source review/187tests/archive bind the two
intentional source changes. No production change or new tests were needed here.

Next: one separately planned continuation using11retained recordings and only
the five never-attempted slots12–16 in a new output root. Retained9–11 still need
their first scientific analysis; existing1–8 measurements stay cached. Use existing
run_scenario/process/cleanup/case validators and per-case science owners, preserving
fixed settings and original IDs and evidence. No new M4 version infrastructure is
needed. Source/protocol scope and corrected C11 provenance must be explicit.
The full goal, missing conditions and original30% latency target remain open.

Git is V2 at3369cfc with existing uncommitted task changes. No physical/Pi/snapshot,
V1, commit or push. Exact context/diff/material-checkpoint receipts are recorded
in live status before subsequent dispatch.

R24 material checkpoint COMPLETE: 691 verified source members in 0.951133s at
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/r24_retained_c11_validation_closed_v1/`;
manifest SHA256 `f3edc3a102d975dde7ad8045a2ce2dbe4ec93f1b34476c473d101fdb659d8e38`.
The archive predates this receipt annotation. Context validation and diff check passed.
R25 independent prerequisite review PASS31; only the declared R23 validator/test
and current root plan differ among 836 selected source/runtime/config pins.
Five unused IDs have no matching original run directories. No empirical job is running.
