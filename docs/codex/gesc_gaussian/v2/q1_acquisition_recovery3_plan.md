# Q1 acquisition recovery 3 — prospective, 2026-09-09 UTC

Status: SELECTED FOR PREFLIGHT; not released by this document. This finite
technical recovery follows `q1_event_attribution_plan.md`. Require its tests,
separately saved full diagnostic validation of the retained bag, source freeze
and checkpoint before dispatch. All prior acquisitions remain CLOSED INCOMPLETE.

Recovery2 recorded125s in SEARCH and passed every completeness check except
identification of the V2 detector's CONFIG signature. Its original acquisition,
bag, reports and closure remain immutable. The correction identifies that exact
configuration in the existing validator and leaves all runtime code and
scientific controls unchanged. The old bag can demonstrate the defect through
a separate read-only diagnostic report; it is not imported as a qualified Q1
input or reclassified in place.

Use scientific version `q1-primary-shadow-v1` and new acquisition version
`q1-primary-shadow-v1-recovery3`, rooted exclusively at
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery3/`.
Keep the existing four-case acquisition and strict original-input receipt
contract. A mixed old/new input population would require a broader adapter and
provenance change; this recovery instead acquires each fixed case once under
new IDs after validating the correction. There is no automatic retry loop.

Preserve the four starts/seeds26090911–26090914, original discovery/confirmation
partition, first-case GUI,125 simulated seconds after readiness,240s process
cap and1200s suite cap. This is deterministic input reuse after a diagnosed
technical failure, not an independent replication or a replacement success
for recovery2. Diagnosis used event/clock/graph/integrity evidence, not detector
scores, spatial labels or direction quality. No holdout was dispatched or
opened. No control tuning, start, seed, geometry, threshold, label, target or
nomination rule is selected from the failed acquisition.

The new contract binds this amendment, the event attribution correction plan,
and recovery2's exact acquisition/closure receipts. Require its one-case
INCOMPLETE result, zero qualified inputs, no later/confirmation dispatch, passed
safety and cleanup, and the sole failed producer-attribution check. Check all
new root/run IDs before output. Unknown recovery versions remain rejected.
Freeze actual installed entry points and environment as before. Compare all
scientific keys/resolved cases and unchanged runtime source against recovery2.

Dispatch stops on the first safety, completeness, cleanup or input-binding
failure. Only four complete inputs permit the unchanged one600s discovery/
nomination/conditional-confirmation job and one300s48-slot reference job.
Preserve all scientific failure/unavailable outcomes without tuning/replacement.
M4 remains unreleased until independent component qualification passes.
