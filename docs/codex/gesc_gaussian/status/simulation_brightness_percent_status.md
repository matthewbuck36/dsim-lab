# Simulation brightness percentage status

Status: COMPLETE — interface implementation and host qualification only

## Verified repository state

Clean starting checkout at `01e7645` on
`feature/gesc-gaussian-robustness-v1`. Phase 08 implement-context validation
passed before editing. The current phase history remains closed/frozen as
recorded; this work follows `plans/simulation_brightness_percent_plan.md`.

## Current milestone

Implemented and validated the simulation-only percentage input/display
interface. New inputs accept 0–100%; 100% maps to nominal 1600 lumens. JSON,
YAML, CLI, configuration events, metadata, and surface labels agree. The
existing lumen compatibility path and internal fitted-curve normalization
remain available; frozen outcomes and physical files are unchanged.

## Validation checkpoints

Protected baseline SHA-256 hashes are retained at
`/tmp/dsim_brightness_percent/protected_before.json`.

- Combined focused/legacy/observability/schema/runner/aggregate regression:
  **491 passed, 1 skipped** in 173.56 seconds. The skip is the opt-in recorded
  Gazebo end-to-end test (`RUN_GESC_PHASE06_GAZEBO_E2E` was not enabled).
- Final expanded percentage suite after adding JSON-without-CLI coverage:
  **30 passed** in 1.26 seconds. Counts overlap the combined suite.
- Isolated build: **3 packages passed**, 15.9 seconds.
- Installed XML construction: all three cost/plot command paths resolve the
  percentage arguments correctly; no process-starting action executed.
- Installed example and runner dry-run: PASS, one 25%/100% case expanded.
- Installed offline surface plot: PASS; rendered legend visually checked as
  `L1: 25%`, `L2: 100%`.
- Protected historical/shared-owner hashes: **291 unchanged**.
- Changed Python AST, fatal flake8 (`E9,F63,F7,F82`), relative documentation
  links, and `git diff --check`: PASS.

Exact commands, artifacts, diagnostics, and evidence limits are in
`validation/simulation_brightness_percent_validation.md`.

## Attempts not to repeat

Do not convert old values above 1600 lumens into invalid percentages, change
fitted-curve normalization, rewrite frozen scenarios, or treat this nominal
linear mapping as physical Hue calibration.

## Remaining work

No required interface implementation work remains. Changes are uncommitted.
The host qualification overlay is `/tmp/dsim_brightness_percent/install`;
normal workspace builds can install the new example through the existing
three-package build procedure. No new Gazebo behavioral run, physical test,
calibration, or robustness claim was performed.

## Compaction recovery

Read AGENTS.md, this status, its plan, current Git status/diff, and the next
incomplete acceptance criterion before continuing.
