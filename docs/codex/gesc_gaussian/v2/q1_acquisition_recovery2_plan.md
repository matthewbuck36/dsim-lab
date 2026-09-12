# Q1 acquisition recovery 2 — prospective, 2026-09-09 UTC

Status: SELECTED FOR FREEZE, NOT YET RELEASED. The source checks in
`q1_simulation_source_plan.md` pass; verified checkpoint and exact dispatch
receipt are required before acquisition. This document declares the finite
acquisition that follows; it does not make earlier attempts successful.

## Preserved attempts and permitted correction

Original acquisition failed before recorder startup because a source-path prepend
selected stale console metadata. Recovery1 fixed that startup but failed after
its controller rejected a21ms leading odometry header during a held clock tick.
Its125s recording, FAILSAFE, diagnostic coverage failure and clean shutdown are
retained in `validation/q1_acquisition_recovery1_failure.md` and the immutable
`qualification/q1_primary_shadow_v1_recovery1/acquisition_closed.json` outside Git.
It also demonstrated independent merged-joint-source regressions.

Recovery2 may run only after the declared controller clock-admission and selected
single-joint-source corrections, focused legacy/actual-transport tests, required
build/installed-source checks, exact source freeze and checkpoint pass. Preserve
the corrected overlay environment and actual console entry-point check from
recovery1. Do not change detector thresholds, filter equations/gains, cost sign,
units, speed ceilings, recorder completeness, safety/final-zero or numerical
reference rules to obtain an accepted run.

## Exact finite acquisition

Scientific method/version remains `q1-primary-shadow-v1` in `q1_plan.md`.
Acquisition version is exactly `q1-primary-shadow-v1-recovery2`; artifact root
is `/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery2/`.
Generate all four run IDs from that acquisition version. Never overwrite old
roots, IDs, source freezes, bags, diagnostic receipts or analytical outputs.

Keep the original four starts, seeds26090911–26090914, discovery/confirmation
partitions, first-run visibility,125s readiness-based simulation duration,
240s process bound,1200s acquisition bound and fixed48 direction targets. This
reuses deterministic inputs after a diagnosed technical failure. It is not an
independent replication of recovery1, a replacement sample, or a successful
rerun of its frozen version. Recovery1's first fault occurred0.1 simulated
seconds after readiness; diagnosis inspected source timing, graph and safety
messages, not detector/trajectory performance. No source position, start, seed,
threshold or grid choice is selected from that outcome. Its confirmation cases
were never dispatched. No held-out result guides this correction.

The new machine-readable contract must link the exact recovery1 acquisition and
closure receipts, this amendment and the completed source correction plan. Bind
the current actual source graph and clock handling through source/installed
receipts; verify remaining science and resolved case controls against the old
contract. The existing runner's explicit `runs_root` override remains the only
recording path; keep the original scenario's scientific metadata version.

Before dispatch, reject unknown acquisition versions, wrong paths/IDs, changed
prior receipts, mismatched environment or source files. Require the prior
attempt to be the recorded first-case INCOMPLETE result with clean cleanup and
zero qualified inputs; never automatically generalize this recovery to another
failed version. Check single-source readiness and exact publisher ownership;
the V2 graph must not accept the redundant publisher if it reappears.

## Outcomes and analysis boundary

Run each fixed case once. The first safety, recording, cleanup or input-binding
failure stops later dispatch. Preserve any measured behavioral/input failure;
do not retune or retry this fixed version. Only four complete qualified inputs
produce a study manifest. Then use the unchanged one600s label/nomination job,
confirmation unlock rule and one300s48-target reference job. The original
discovery/confirmation gates, missing-data outcomes and M4 release requirements
remain in force. A source or infrastructure pass is not research qualification.
