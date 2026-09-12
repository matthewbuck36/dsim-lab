# Q1 event attribution correction — 2026-09-09 UTC

Status: IMPLEMENTED AND VALIDATED; material checkpoint receipt in `status.md`
closes this bounded correction within approved simulation-only V2 implementation.
115 focused/inherited tests and all60 corrected retained-bag validation checks
PASS. The original failed acquisition remains unchanged. Exact commands and
receipts are in `validation/q1_event_attribution.md`.
Read `plan.md`, `status.md`, `q1_plan.md` and the preserved
`validation/q1_acquisition_recovery2_failure.md` before editing.

Extend only the existing shared-bus event attribution owner for CONFIG events:
the exact detail `centroid_windows_v2 source-time configuration` identifies the
existing convergence detector. Keep unknown, empty and near-match signatures
rejected. Feed recognized events into the same existing detector timestamp
stream, with unchanged regression, source causality and emission freshness
checks. Preserve inherited signature handling, message interfaces, runtime
publishers, source clocks, thresholds, filter/controller behavior and all
scientific population/nomination/confirmation rules.

Test the actual detector-emitted signature, wrong event type and unknown/near
matches, same-producer regression and valid cross-producer interleaving, and
the central validator's valid/unknown outcomes. Run focused inherited recording
regressions. A read-only corrected validation of the retained bag may be saved
under a new diagnostics path as defect confirmation; it must never overwrite
original completeness/metadata/scenario classification or turn the failed
fixed acquisition into a successful one. No scientific outputs may be opened.

Record exact commands, outputs and hashes; inspect the bounded diff, checkpoint
the correction, then freeze a separately declared acquisition recovery before
dispatch. This source plan alone does not release Gazebo or the M4 pilot.
