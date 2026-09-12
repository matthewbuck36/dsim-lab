# R2 four-arm development labels throughput benchmark

ADOPTED, 2026-09-10. This is the retained-data performance measurement required
by [D3](m4_post_v9_analysis_plan.md), following its validated source correction
and the [method/development amendment](method_development_20260910.md).
No old experiment is reopened. This benchmark does not run direction reference
integration, a field model, Gazebo, ROS graph discovery or new acquisition.

## Exact route and identity

Read the unchanged historical contract at
`/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9/preflight/contract.json`
as data. Call the existing
`evaluate_m4.labels_stage(contract, 0, output_directory=<new root>/labels)`
exactly once. Its block0 is slots1–4, armsA/B/C/D, nominal development runs
`m4-pilot-v9-slot01-A-26090801` through `slot04-D-26090801`.
These four acquisitions remain COMPLETE/integrity-passed/behavior-failed.
The historical contract, acquisition manifests, bag contents and failed science
outputs retain their original identity and paths.

The new exclusive root is
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/labels_block_benchmark_v1/`.
The diagnostic manifest binds this plan, current imported pipeline source,
interface/environment bindings, the exact historical contract/acquisitions,
their declared input SHA256 receipts, each bag's size/device/inode/mtime, and
the geometry receipts. Keep current source separate from the historical frozen
source set. This diagnostic calls neither `_context` nor `verify_frozen` and
never claims the old frozen-source gate passed. The normal CLI is unchanged.

## Inputs, work and inclusive bound

Before dispatch inventory small metadata/receipt files and filesystem metadata
only. Do not read or warm retained bag bytes outside the work allowance.
The unchanged `_acquired` owner validates original input receipts, including
each bag SHA, inside `labels_stage`. The existing reader then performs exactly
one decoding read for each declared run. No extra message query, second bag
reader, observation filtering, cache, compression, numerical change, artifact
format change or relaxed40000-observation admission is introduced.

A thin parent wrapper calls the existing `m4_science_job.finite_science_job`
with the original120-second inclusive cap and `subreaper_group_v3` ownership.
The existing owner reserves3 seconds of that cap for cleanup and receipt
publication, so useful work stops by117 seconds. Preserve its identity-checked
group interruption/escalation and reaping; do not add another process owner.
The cap includes child imports, source/input checks, original receipt hashing,
four reads, label/normalization analysis, JSON writes/fsync, instrumentation
and normal completion. Parent invocation has a130-second outer ceiling for
pre-established clean environment, imports and result inventory; it grants no
extra child work. No unchanged retry or longer budget is allowed.

Reuse the built Humble→Q2→Q5→centered interface overlay. Before launch retain
one scoped pipeline/source/evidence archive under60 seconds; root owns the
overall material checkpoint. Hold only those pinned pipeline sources through
the child; unrelated runtime/prototype edits may continue. The wrapper records
pre/post source and input filesystem identities and any added imported source.
An unpinned dependency or changed required input invalidates the benchmark.

Thin wrappers around the existing reader and per-run analysis record begin/end,
elapsed seconds, selected aliases and record counts; they return the original
objects untouched. Sparse JSONL progress and standard output are retained.
No deterministic profiler is used. Instrumentation overhead remains inside the
120-second budget and is not subtracted.

## Decision rule and artifacts

PASS requires normal child completion by120 seconds, all four original
acquisition receipt checks and exactly one read per run, four labels and metrics,
both C/D normalized outputs, final `labels.json` with the existing complete
schema, and unchanged pinned source/input identity. Independently verify the
newly written receipt bytes before reporting success; this is inside the same
child allowance. Failure or timeout retains all partial outputs and stage
timings without labeling uncompleted slots as processed. Unreached input bags
retain declared historical hashes; their receipt verification is not claimed.

The result concerns full-block label throughput on these development inputs.
It does not complete any historical V9 science job, establish direction
accuracy, qualify current runtime, or release a16-run comparison. A failing
result permits a separately saved diagnosis/correction using retained timings;
it does not justify retrying this fixed benchmark unchanged.
