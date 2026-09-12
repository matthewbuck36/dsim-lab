# V2 Git closeout — 2026-09-12 UTC

The user requested cleanup, a substantive commit and push/synchronization of the complete pending V2 tree. The accepted simulation implementation and its chronological research record are committed together from base3369cfc on feature/gesc-gaussian-robustness-v2. This is source-control closeout; deferred algorithm investigations and physical integration are not reopened.

## Scope and preservation

The initial inventory contains36 modified tracked files and660 untracked files, approximately7.4MB of new source, interfaces, tests and documentation. No raw bag, build tree, cache, log, binary report, credential pattern or transient file was present in the candidate set. Existing ignores and external Experiment storage already separate generated data. Preserve all plans, failed experiment records, test fixtures, versioned tooling and source-receipt manifests. Cleanup removes whitespace from seven blank lines in status.md and extra blank lines at the ends of four historical Markdown records; their substantive content and archived originals are retained. No algorithm source is retuned or repaired.

Before edits, a scoped worktree archive, binary diff and per-file hashes were saved under:
`/home/mattb/Experiments/GESC-Gaussian/v2/git_closeout/20260912T015343Z/`.
The reviewed commit message, exact regression selection/command, logs, JUnit, execution receipt and final synchronization receipt live there. The commit containing this record is the recoverable implementation snapshot; older references to3369cfc/uncommitted files describe the historical precommit state. The generated checkpoint is intentionally a precommit snapshot and excludes its own hash.

## Verification

Remote fetch completed and the branch initially matched origin exactly (ahead0/behind0). Static parsing passed for241 changed/new Python files,8JSON files and2XML files. Focused closeout tests reuse the21-module R21 bundle and add detector/direction, R20-R22, M4v14, deadlines, legacy/clock/observability and phase-tool regressions:46modules total. They run in the selected R21 installed environment with a300s command bound and BLAS threads limited to1, without a Gazebo study.

Regression result: **1449 PASS,25 setup errors,0 test failures,0 skips** in141.99pytest seconds (142.754700wrapper seconds), exit1, within the300s cap. Every error is in `test_m4_v14_workflow.py` and reports the same frozen-input mismatch for `v2_lifecycle_validation.py`. That historical V14 fixture requires pre-R23 bytes; the accepted R23 guidance/admission correction changed them. Current SHA256 `f18906fce8e6994f5d803995ad7b78c427b9d965024476069010ddb9d8d92710` matches the pre-closeout file exactly. Its original correction/187-test validation is retained in [R23 validation](r23_guidance_admission.md); the new closeout also passes the current lifecycle tests. The historical fixture and release guard are left unchanged. No claim that this entire46-module invocation passed: the25historical cases did not execute. No full-suite rerun or source modification was undertaken to bypass the frozen contract.

Exact selected tests and argv: external validation_plan.json. Execution and JUnit: focused_execution.json / focused_junit.xml. The full historical suite and study matrix are not rerun; historical build-specific qualification receipts remain retained. Staged whitespace, phase-context and candidate-file review pass. The post-push `sync_receipt.json` in the external closeout root records local/remote SHA equality and clean-tree status; it is generated after the commit so the repository can remain clean.

## Accepted result and remaining boundaries

Test D is the user-accepted simulation baseline. The completed sixteen-run comparison has4/4qualified D arrivals and zero mandatory stopped acquisitions; the latest matched normal-speed A/D presentations both pass11/11runtime predicates, with210.823/158.053simsec arrivals. The25.03%arrival improvement describes that pair. Historical wrong outcomes and unavailable scientific measurements remain preserved.

The independent-onset30%criterion stays retired; runtime GOAL_HOLD stays available and optional for arrival acceptance. Intermittent command-ownership/fill issues and A/B/C repairs are deferred. D/noise has a missing direction anchor. Physical source integration is the next discussion and remains unimplemented/unvalidated by this closeout. No physical operation, branch rewrite or V1 change is authorized here.
