# Q3 detector clock-admission source handoff

Q3 source validation is complete. Node, selected recorder and installed binding
checks pass; the material checkpoint receipt is recorded in live status.
Exact commands, failures and receipts are in
`validation/q3_detector_clock_admission.md`.

The existing centroid node now defers bounded future state publications and
standalone pose acquisitions until its ROS clock covers their original stamps.
It preserves the previous admitted evidence only while its original ROS and
steady receipts remain fresh. The steady watchdog drains even before SEARCH
activation and expires support while the simulation clock is paused. State
authorization precedes pose integration. Identity changes, invalid input,
recording loss, actual non-SEARCH transitions and rollback retain conservative
invalidation; duplicate messages cannot refresh or resurrect revoked support.
Standalone frame transitions reset/reseed and retain the confirmation latch.
Rolling pose admission remains in its existing V2 binding.

Selected recorder metadata carries the explicit centroid admission policy and
existing configured pose-freshness bound. The validator requires publication
to cover both original source and receipt within that bound. Unselected strict
ordering, the rolling default and invalid metadata rejection are preserved.
Selected defaults remain0.5s; positive configured node limits are not silently
clamped. No centroid formula/window/threshold, shared clock defaults, controller
law, PDE compatibility, GESC policy or M3 numerical owner changed.

Three actual-node baseline failures are preserved. The first expanded test run
has220 passes and five fixture failures; corrected authorization and genuine
fresh-acquisition expectations produce226 passes. Existing DDS centroid,
epoch and controller-clock transport passes5 checks. Installed imports bind to
the held source without rebuilding. Independent recorder checks pass24 new cases plus81 existing regressions;
explicit1s freshness overrides pass2 additional actual-node cases.

This is a source-ordering correction, not scientific qualification. Recorded
Q2 notices do not distinguish stale from future state; the exact old trigger
remains unresolved. All20 complete recorded histories independently fail the
score. Q2 acquisition/science/diagnostics remain closed, confirmation sealed.

Next resolve the separate committed-fill clock-admission issue and the Arm B
centroid/stationary confirmation-to-fill adapter. Then make one prospective
finite development decision on settling labels, window/period sensitivity,
moving-evidence support and direction accuracy before the unchanged16-run pilot.
Do not retune or rerun a closed study or infer research readiness from these
source tests. The full implementation goal remains active.

Branch is `feature/gesc-gaussian-robustness-v2`, HEAD `3369cfc`. Task-owned dirty
source/evidence remain recoverable. No new commit/push, V1 edit or physical
snapshot/Pi/hardware action occurred.
