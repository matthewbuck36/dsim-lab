# Post-V9 D3: remove redundant labels-analysis work and verify budget feasibility

Status: ADOPTED, 2026-09-10 UTC, simulation only. The user authorizes recommended
bounded corrections toward the original16-run comparison and its report.
D2 is materially closed at archive
d5df2e6049b15ea99515426dfd17448f31260412ea161b5e55c7310c4f2ff814.
Read [D2 handoff](m4_post_v9_monitor_handoff.md),
[post-V9 plan](m4_post_v9_integrity_plan.md) and
[analysis diagnosis](validation/m4_v9_development_diagnostics.md).

## Entry evidence and objective

Both completed V9 labels blocks exhausted their fixed work allowances, leaving
the direction references and latency comparison unavailable. V9 remains closed
incomplete; no existing job/output is retried, replaced or reclassified.
Two redundant operations are directly confirmed in the current source. Removing
them preserves the analysis while reducing unnecessary work. Their sufficiency
for the120-second block allowance is unknown and must be measured separately.
This milestone targets analysis feasibility, not a replacement research target.

## Exact source correction

Extend only these existing owners and their focused tests:

1. `docs/codex/gesc_gaussian/v2/tools/evaluate_m4.py::labels_stage`: retain
   `atomic_exclusive_json`'s returned SHA for both per-slot labels and normalized
   observations. Construct the identical resolved-path/SHA receipt without
   reopening the file immediately. The writer already hashes the exact bytes
   it publishes exclusively. Preserve formatting, schema, ordering, fsync,
   exclusive creation and every later consumer's real `check_receipts` rehash.
2. Existing `gesc_gaussian_bag_analysis.py` direction-input adapter: construct
   the legacy snapshot only in its non-augmented branch. M4 currently builds a
   snapshot including `message_payload(objective)` and immediately discards it
   for `_m4_objective_snapshot`, which converts that objective again. Preserve
   the selected snapshot, all numerical/identity/error checks, complete rows,
   qualification, canonical observation hashes and the legacy/Q1 branch.

For the required diagnostic benchmark, add only a keyword-only optional output
directory to the existing labels_stage owner. Default output resolution remains
unchanged. This allows the original historical contract/acquisition inputs to
remain intact while an explicitly diagnostic wrapper writes elsewhere. Do not
modify the frozen contract/root/source receipts, `_context`, `verify_frozen`,
normal CLI routing or acquisition files. The diagnostic wrapper must separately
bind historical evidence and current analysis source, and must never claim the
old frozen-source gate passed on changed source. Test both default and isolated
output paths, with identical content/receipt integrity except declared paths.

Do not edit the whole-file-pinned `v2_enclosure.py`, its atomic writer or the
geometry/reference numerical owners. Do not add a parallel reader/analyzer,
change JSON formatting or compactness yet, reuse validation caches speculatively,
change observation/label/target selection, loosen40000-observation admission,
remove late consumer integrity checks or increase any science/runtime budget.
Source changes remain independent of startup/daemon corrections, which are still
required before a fresh comparison.

## Source evidence

Preserve pre-edit files/source pins externally at
`builds/m4_post_v9_analysis_v1/`. Add meaningful tests in the existing
`test_m4_evaluation_cli.py` and `test_m4_objective_inputs.py` owners before
production edits. One120s baseline on the new tests must reproduce immediate
artifact rereads and the duplicate objective conversion. Source remains held
until that result is retained; fixture faults use a corrected version without
rewriting the baseline.

Tests must exercise actual labels_stage output for both artifact types,
independently hash written bytes, retain exactly one bag read per run and
exclusive output behavior. Actual references_stage must consume the receipts
and still reject mutated artifact bytes. The adapter test counts only actual
objective conversions, preserves full returned observation/qualification values
and exercises the inherited branch and malformed/objective-mismatch failures.
Use generated messages/current fixture owners, not a substitute algorithm.

After the correction run both complete focused modules under180s. Then run
relevant `test_m4_pilot_metrics.py`, `test_m4_science_job.py`,
`test_q1_direction_inputs.py`, `test_q2_recorded_layout.py` and
`test_q1_direction_references.py` under240s; verify actual filenames and save
any necessary substitution before execution. No ROS context, Gazebo, physical
action, retained bag read, model/reference job or acquisition belongs to these
source tests. Preserve all failed versions and count actual unique JUnit results,
skips/exclusions and stable installed bindings/source hashes.

Use clean installed Humble -> Q2 -> Q5 imports, explicit finite root timeouts,
exclusive external logs/JUnit/receipts, independent review, context/diff checks
and the existing V2 checkpoint. Close the source boundary with one exclusive
material archive under60s before any retained-data performance job.

## Required performance evidence after source validation

Save a separate exact benchmark amendment before reading retained data. The
desired evidence is whether the existing labels pipeline can process a complete
four-arm development block inside the original120s inclusive allowance. A small
serialization benchmark alone cannot prove that. Bind current source, unchanged
retained inputs and a new diagnostic identity/output root; preserve the frozen
V9 contract and its failed outputs. Reuse existing analysis owners, at most one
read per declared bag, and no direction-reference/model evaluation or science
promotion. Exact contract routing, input count/hash inventory, deadlines,
cleanup, profiling overhead and output-identity scope must be reviewable before
release. A timeout is retained, never retried unchanged or granted more time.

If these exact local corrections do not provide adequate throughput, diagnose
the measured remaining work and save a further bounded correction. Compact
intermediates or cache reuse require separate explicit semantics/default-identity
tests before adoption. No new16-run comparison is released by source passes or
partial timing evidence. Both original research goals remain open.
