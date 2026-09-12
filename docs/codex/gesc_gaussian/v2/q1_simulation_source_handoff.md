# Q1 simulation source handoff — 2026-09-09 UTC

The controller source-clock and selected joint-source corrections are implemented
and validated. `validation/q1_simulation_source_correction.md` records401 combined
checks, actual held-clock ROS transport, focused legacy/recording regressions,
three-package build and installed-asset/entry-point verification. The source
boundary is closed only with its verified checkpoint receipt in `status.md`.

The first field attempt after packaging recovery remains CLOSED INCOMPLETE:
125s simulated recording and clean shutdown/cleanup, but controller FAILSAFE
and diagnostic coverage failure. First fault2.7s precedes the separately diagnosed
joint-stream reversal9.011s ->9.008s. Preserve both causes and their distinct
corrections; no detector or direction performance result was obtained.
Full failed-run hashes and narrow diagnostic receipts are retained under
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery1/`.

Current branch is `feature/gesc-gaussian-robustness-v2`, HEAD/origin3369cfc.
Changes remain uncommitted and task-owned; no push/merge occurred. V1, the offline
physical snapshot and mounted-Pi path were not changed. No new node, recorder,
numerical/reference owner or control publisher was created.

Next work is the separately frozen recovery2 acquisition declared in
`q1_acquisition_recovery2_plan.md`, after source checkpoint and release. Keep the
four starts/seeds and original scientific gates; reused development inputs are
technical recovery, not independent replications or replacements for the failed
attempt. Stop dispatch on safety/completeness/input/cleanup failure. Four valid
inputs are needed before discovery nomination and sealed confirmation analysis.
The16-run M4 pilot remains unreleased until independent qualification passes.
