# R12: remove analysis subprocess and bind recorded arrival independently

ADOPTED prospectively, 2026-09-11 UTC, after the completed
[R11 diagnosis](r11_retained_diagnosis_handoff.md). Simulation/evaluation only.
This milestone corrects the two demonstrated analysis defects through their
existing owners. It does not alter the detector, controller, moving verification,
scientific error thresholds or any historical experiment result.

Work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r12_measurement_correction_v1/`.
Preserve before copies and exact deltas. Root owns execution; disjoint owners
may prepare source and focused checks concurrently. No new matrix is released.

## Repository discovery without an import subprocess

Extend `run_scenario._repository_root()`. Preserve current-checkout selection:
resolve the nearest Git worktree marker from the current directory using the
filesystem, including a `.git` file, and validate the existing ros_esc layout.
Do not accidentally select an outer checkout through an intervening Git root.
Retain the existing Git fallback for unresolved layouts or explicit Git
environment overrides, then the existing module-ancestor/conventional fallback.
Do not switch normal selection from the current checkout to a different module
checkout. Normal selected analysis imports must launch no subprocess.

Keep the single-process science gate unchanged. Focused checks must cover normal
and nested current directories, worktree markers, nested non-DSIM Git roots,
module fallback, explicit Git overrides, fallback failure and unchanged selected
paths. One fresh import-only audit after correction has a 20-second inclusive
limit and must observe zero subprocesses in the selected runtime environment.
Historical V12 process integrity remains failed.

## Independent recorded arrival binding

Extend existing `evaluate_m4._arrival_metrics` with a private explicit selection
for a corrected binding method; preserve the current default for historical
analysis. No old version silently opts into the new method. The R12 component
probe explicitly selects it; a later prospective experiment must select it too.

Bind time to the unique readiness-scoped recorded pose at the exact immutable
evaluator bag timestamp. Require finite pose, valid source ROS timestamp and
origin, exact recorded evaluator position, noninterpolated in-radius evidence,
correct goal/radius association and consistent recomputed distance. Preserve
the existing successful recovery/arrival outcome prerequisite. Report live
monitor evidence separately: it must remain a valid observed arrival, but its
independently selected first pose need not equal the recorded first pose.
Do not substitute live time or infer an absent recorded timestamp. Missing,
duplicate, wrong-frame/alias, mismatched recorded position/distance, invalid
source time or unsupported outcome stays unavailable.

Focused checks include different valid live/recorded first poses, exact recorded
timestamp binding, historical-default parity, missing/duplicate samples, invalid
times/positions/distances and failed/censored arrivals. Then one separately
named B/noise retained component probe through the corrected existing owner,
using one filtered pose/readiness read under 30 seconds inclusive. Save the new
time and original unavailable result side by side; do not rewrite V12.

## Validation and closure

Run one named focused bundle for the two corrections and relevant existing
science/arrival compatibility checks under 90 seconds work, 10 seconds
termination allowance, 100 seconds inclusive. Do not run a broad source-test
campaign. Record exact selected checks, any failures, commands and elapsed time.
Use the unchanged selected ROS environment and verify the actual imported source
and selected entry points. No build is needed for symlinked Python source.

Complete source reviews before component probes, retain hashes before/after,
record the two empirical component outputs and limitations, then checkpoint and
write the handoff. Prospective profile-method study planning may proceed in
parallel, but no numerical method experiment or method source change starts
before its own bounded plan is adopted. No physical/Pi/snapshot/V1, commit, push,
simulation or old-version resume belongs to R12.
