# Phase 07 Plan — Rosbag Extraction and GESC/Gaussian Diagnostics

## Artifact status

This Plan-mode task made no repository changes. Save this document verbatim as:

`docs/codex/gesc_gaussian/plans/phase_07_plan.md`

Before implementation, run `validate_phase_context.sh 07 implement`; do not open the Implement chat until the saved plan passes that check.

## Objective and scope

Implement one offline Python analysis command inside the existing `ros_esc` plotting area that reads Phase 05 sqlite3 run directories, preserves the raw bag and all recorded timestamp domains, exports synchronized evidence tables, generates the eight required diagnostic plots, and writes validity-marked summary metrics and an analysis-completeness report.

In scope:

- Passed and failed Phase 05/06 run directories.
- `legacy` and `robust_gaussian_v1` profiles.
- Phase 05 `resolved_topics.yaml`, `resolved_parameters.yaml`, metadata, live completeness rules, sqlite3 bag, and real generated message types.
- Cost, component, state, event, weight, trajectory, fill, command, escape, success, failure, revisit, and completeness diagnostics.
- Deterministic generated bag fixtures for behavior coverage absent from retained real bags.

Out of scope:

- Changing controller, supervisor, Gaussian, recorder, validator, scenario, launch, topic, or message behavior.
- Phase 08 tuning or robustness acceptance.
- New simulation scenarios as empirical evidence.
- Physical hardware, physical adapters, Heavy-Ball ESC, collision inference, or physical calibration.
- Deleting, rewriting, converting, or annotating raw bags in place.

Success means the command produces all required files for both complete and failed runs, explicitly marks unavailable/invalid metrics, preserves raw timestamps, and does not weaken the Phase 05 completeness result.

## Repository findings

- Required preflight passed: `Phase 07 plan context is complete.`
- Current branch/HEAD: `feature/gesc-gaussian-robustness-v1` at `8c6191d`.
- The only working-tree modification is the pre-existing user-owned `gesc_gaussian_full_rotation_voltage.bash`; Phase 07 will not touch it.
- `ros_esc` is the correct package and `ros_esc/plotting_scripts/` is the existing analysis/plotting owner. No bag-analysis command currently exists.
- `record_run.py` and `validate_run.py` remain the sole recorder and completeness authority. Analysis must call `validate_run_directory(..., write_report=False)` and must not replace or rewrite root `completeness.json`.
- The installed manifest is `ros_esc/experiment_recording/topic_manifest.yaml`. Simulation uses sqlite3 and 19 required topics; fill, convergence, supervisor, stop, PDE, and TF topics are optional/conditional.
- `rosbag2_py` has a registered sqlite3 reader and writer. NumPy, Matplotlib, SciPy, and PyYAML are installed. Phase 07 needs only `rosbag2_py`, NumPy, Matplotlib, PyYAML, and the standard library; pandas and new heavy dependencies are unnecessary.
- Canonical analysis inputs are the real `CostBreakdown`, `GescDiagnostics`, `ControlDiagnostics`, `AlgorithmState`, `AlgorithmEvent`, and `GaussianFill` messages plus `nav_msgs/Odometry`.
- The accepted Phase 05 run has all 19 required topics and passes completeness, but contains no typed fill lifecycle and only reaches `SEARCH` before managed shutdown. Retained Phase 06 smoke runs likewise contain no fill/escape/recenter sequence. Generated sqlite3 fixtures are therefore required to test those diagnostics without claiming Phase 08 empirical acceptance.
- Multiple retained failed Phase 05 runs are available, including timestamp, clock, console, coverage, and unfinalized failures. They must remain analyzable.

## Existing implementation to reuse or extend

- Reuse `validate_run.validate_run_directory(write_report=False)` for the current Phase 05 completeness decision.
- Reuse the run-specific `resolved_topics.yaml`; use the installed manifest only as an expected-contract fallback. Missing run-specific resolution remains a critical defect.
- Reuse `resolved_parameters.yaml` for the Gaussian estimation channel, synchronization tolerance, supervisor rate, thresholds, and command limits.
- Reuse metadata and `resolved_scenario.yaml`, when present, for sources, bounds, goal roles, and ground-truth tolerances. Do not infer ground truth from source position alone.
- Reuse `plotting_helper_functions.init_plot_style()` and the existing Matplotlib plotting area, while adding specialized multi-panel Phase 07 figures.
- Reuse authoritative typed fill revisions. Never derive robust fill history from lossy `/cost_bias`.
- Preserve Phase 06’s separation between recording completeness, controller-observable success, and simulation-ground-truth success.

No parallel recorder, validator, scenario runner, ROS node, interface package, or plotting package is needed.

## Files to modify

- `ros2_ws/src/ros_esc/setup.py`
  - Add `analyze_run = ros_esc.plotting_scripts.gesc_gaussian_bag_analysis:main`.
- `ros2_ws/src/ros_esc/package.xml`
  - Declare direct runtime dependencies `python3-numpy` and `python3-matplotlib`; retain existing rosbag2, runtime-message, and PyYAML dependencies.
- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/README.md`
  - Document the offline run-directory interface, output tree, timestamp policy, and validity semantics.
- `docs/codex/gesc_gaussian/recording_runs.md`
  - Add the post-recording analysis command and explain that analysis does not replace validation.
- `docs/codex/gesc_gaussian/topic_dictionary.md`
  - Add the Phase 07 offline interface and output contract without changing ROS topics.
- `docs/codex/gesc_gaussian/test_commands.md`
  - Record exact Phase 07 focused/global/real-bag results and inherited lint debt separately.

Do not modify `validate_run.py`, the manifest, message definitions, launch files, algorithm owners, scenario runner, or raw run artifacts unless implementation discovers a Level A contradiction.

## Files to create

- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/bag_reader.py`
  - Read-only sqlite3 deserialization, timestamp extraction, readiness filtering, long-form row normalization, and bounded synchronization helpers.
- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py`
  - CLI, metric validity model, CSV writers, metric calculations, plot generation, atomic output publication, and exit-code handling.
- `ros2_ws/src/ros_esc/test/test_bag_analysis.py`
  - Pure synchronization, lifecycle, metric, validity, and output-schema tests.
- `ros2_ws/src/ros_esc/test/test_bag_analysis_integration.py`
  - Temporary sqlite3 fixtures using `rosbag2_py.SequentialWriter` and real ROS message classes.
- `docs/codex/gesc_gaussian/handoffs/phase_07_handoff.md`
  - Final files, interfaces, tests, real-run evidence, skips, risks, Level A/B/C results, and exact next prompt.

No binary bag fixture will be committed. Tests will generate deterministic temporary bags.

## Public interfaces and parameters

### Offline command

```bash
ros2 run ros_esc analyze_run RUN_DIRECTORY \
  [--output-dir PATH] \
  [--channel-index N] \
  [--sync-tolerance-sec SEC]
```

Defaults:

- `--output-dir`: `<RUN_DIRECTORY>/analysis/phase07`
- `--channel-index`: `/gaussian_fill.estimation_channel_index` from `resolved_parameters.yaml`; fallback `0`, explicitly recorded as assumed.
- `--sync-tolerance-sec`: `/gaussian_fill.sample_sync_tolerance_sec`; fallback `0.05`, explicitly recorded as assumed.
- Existing output directories are rejected. There is no destructive overwrite flag; reruns must use a new `--output-dir`.

Exit behavior:

- `0`: analysis artifacts were produced, even if the experiment or recording failed.
- `2`: input could not be read, output could not be published atomically, or the analysis process itself failed.
- Experimental success, recording completeness, and metric validity remain fields in the reports and are never encoded solely in the process exit code.

No ROS node, topic, message, launch argument, or ROS parameter is added.

### Timestamp and synchronization contract

Every extracted raw row retains:

- `bag_timestamp_ns`
- typed/header `ros_timestamp_ns`, when present
- legacy `source_timestamp_sec`, when present
- `source_timestamp_valid`
- `in_readiness_interval`
- `t_motion_sec`, when a canonical motion origin is available

The readiness interval is selected using the first `recording_ready=True` bag record through the first subsequent false record. Preflight and shutdown records remain in raw tables but are excluded from motion metrics.

The synchronized table is anchored on every `/gesc_gaussian/cost_breakdown` sample, as selected during planning. For every channel:

- Source cost, GESC diagnostics, pose, and control diagnostics use nearest typed ROS timestamp within the resolved synchronization tolerance.
- State uses the latest causal state sample within the same tolerance.
- No numeric interpolation, extrapolation, or forward filling is allowed.
- Missing matches produce empty/NaN values, `*_valid=false`, and recorded skew/reason fields.
- Headerless legacy topics remain raw/completeness evidence and are not substituted for missing typed diagnostics.

### Output tree

```text
analysis/phase07/
├── tables/
│   ├── synchronized_samples.csv
│   ├── source_cost.csv
│   ├── cost_breakdown.csv
│   ├── gesc_diagnostics.csv
│   ├── control_diagnostics.csv
│   ├── odometry.csv
│   ├── algorithm_state.csv
│   ├── state_intervals.csv
│   ├── algorithm_events.csv
│   ├── gaussian_history.csv
│   └── escape_attempts.csv
├── plots/
│   ├── cost.png
│   ├── components.png
│   ├── state_events.png
│   ├── weights.png
│   ├── trajectory_sources_fills.png
│   ├── command_saturation.png
│   ├── radial_escape.png
│   └── gaussian_history.png
├── summary_metrics.json
├── summary_metrics.csv
└── analysis_completeness.json
```

All eight plots are created for every readable run. An unavailable plot contains an explicit “not available” annotation and the reason instead of fabricated data.

`synchronized_samples.csv` includes cost-anchor timestamps; match timestamps/skews/validity; channel index; raw/source/augmented/component costs; weights; pose/yaw/measured velocity; GESC output; unsaturated, supervisor, combined, and final commands; saturation flags; state; radial progress; stall; and recenter fields.

Variable-length event diagnostics are preserved as JSON-encoded `value_names` and `values` cells. Fixed six-element command arrays are flattened using repository order `[vx, vy, vz, wx, wy, wz]`.

### Metric validity contract

Every JSON metric is represented as:

```json
{
  "value": null,
  "status": "valid|not_applicable|unavailable|invalid",
  "unit": "declared unit or null",
  "reason": "explicit explanation or null",
  "provenance": "topic/metadata/derived rule"
}
```

The summary CSV flattens each metric into value, status, and reason columns. Lists/maps are JSON-encoded.

`analysis_completeness.json` contains:

- Stored root completeness status and a fresh non-mutating Phase 05 validation result.
- Required topic/type/count findings.
- Timestamp/readiness findings.
- Alignment match counts, fractions, and maximum skews.
- Output file/row checks.
- Metric validity.
- Recording failures, analysis failures, and warnings as separate lists.

Status rules:

- `complete`: Phase 05 validation passes, core outputs exist, and every metric applicable to observed behavior is valid.
- `partial`: enough data exists for useful evidence, but recording failed or a noncritical input/metric is unavailable.
- `invalid`: bag/type/time/readiness or critical cost/pose/control data prevents trustworthy core analysis.
- Behavior that never occurred is `not_applicable`, not a fabricated zero and not automatically partial.

## Metrics and diagnostic behavior

- Cost: raw, augmented, and source score per selected channel.
- Components: unweighted raw/Gaussian/affine values plus their weighted contributions; verify their finite sum against augmented cost and report residual.
- State: collapsed sequence, state-transition count, terminal state, and per-state dwell clipped to readiness. State dwell is invalid if gaps exceed three periods of the resolved supervisor rate.
- Events: count by real `AlgorithmEvent` enum, timeout/failsafe reasons, and ordered timeline.
- Trajectory: path length from consecutive finite odometry samples without smoothing; final pose; sources from metadata; active fill ellipses from typed covariance revisions.
- Control: saturation sample count/fraction, per-axis counts, maximum limit excess, and unsaturated-versus-final `vx`/`wz` plots.
- Fill history: active cluster count, creation count, merge/replacement count, supersession count, design failures, escalation totals/maxima, confidence, geometry, and revision history.
- Escape:
  - Start on `EVENT_ESCAPE_STARTED` or first valid entry to `ESCAPE_REPULSE`.
  - Mark stall and assist from real event/state evidence.
  - Success is transition from an escape state to `RECENTER` or `SEARCH`.
  - Failure is transition to `FAILSAFE`, timeout, or readiness-end censoring.
  - Report duration, published radial distance/progress, maximum progress, exit hold, and approximate orbit count from absolute unwrapped trajectory angle around the frozen escape center.
  - Published radial fields remain authoritative; pose-derived radial distance is a labeled QA overlay, not a silent replacement.
- Revisit: after a successful escape, count outside-to-inside crossings of the current active fill’s exit ellipse using valid covariance and `exit_radius/sigma_major`. Missing lifecycle/covariance makes the metric invalid; no fill or escape makes it not applicable.
- Success/failure:
  - Robust controller success requires both `EVENT_GOAL_REACHED` and `GOAL_HOLD`.
  - Legacy controller success is not applicable.
  - Simulation ground-truth success is computed only when Phase 06 metadata supplies goal-source IDs and final-position tolerance.
  - Timeout and failsafe use in-readiness state/event evidence so managed shutdown does not become a false run failure.
  - Collision remains unavailable because the audited graph has no collision/contact truth topic.
- Per-run summary includes recording completeness, readiness duration, path length, convergence time, escape attempts/successes/failures, escape duration/orbit statistics, revisit count, fill/merge/escalation counts, saturation statistics, controller result, ground-truth result, timeout, failsafe, and collision availability.

## Backward compatibility and migration

- Analysis is opt-in and offline; recording, launch, controller, state, cost, and legacy numerical behavior remain unchanged.
- Both profiles use the same command. Legacy-invalid state/fill fields are marked not applicable rather than interpreted as robust state.
- Root run artifacts and `completeness.json` are never rewritten.
- `/cost_bias` may be exported as legacy evidence if present but is never used as authoritative robust fill history.
- Existing plotting scripts and CSV collection remain available.
- Existing run directories need no migration. Analysis creates a new sibling subdirectory only.
- No physical-specific analysis fork is introduced; future physical bags use the same manifest/type-driven reader, with unsupported environment metrics validity-marked.

## Implementation sequence

1. Run Phase 07 implementation context validation; verify branch, dirty-tree ownership, installed sqlite3 reader, manifest, message definitions, retained bags, and absence of an existing analysis owner.
2. Implement `bag_reader.py` with read-only `SequentialReader`, real type resolution, per-topic row normalization, readiness classification, and deterministic bounded timestamp matching.
3. Add raw CSV exports and cost-anchored long-form synchronization, preserving all timestamp domains and unmatched-row evidence.
4. Implement profile-aware metric/status objects and the state, event, fill, escape, revisit, trajectory, command, and success calculations.
5. Implement the eight Matplotlib figures, including explicit unavailable panels.
6. Implement `analyze_run` with manifest/metadata/parameter precedence, live non-mutating validation, atomic temporary-output publication, refusal to overwrite, and failed-run-friendly exit semantics.
7. Add packaging dependencies, console entry point, and operator/interface documentation.
8. Add deterministic temporary sqlite3 fixtures covering:
   - complete robust data with create/merge, escape, stall, assist, recenter, goal, saturation, and revisit;
   - legacy state-unavailable behavior;
   - failed/missing/skewed critical data and timeout/failsafe behavior.
9. Run focused tests, retained regression suites, real passed/failed bag analyses, syntax/style checks, and repository-standard tests.
10. Write the Phase 07 handoff with exact results and any Level B amendments or Level C evidence. Do not claim Phase 08 acceptance.

## Tests and acceptance criteria

### Focused tests

```bash
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash

python3 -m pytest -q \
  ros2_ws/src/ros_esc/test/test_bag_analysis.py \
  ros2_ws/src/ros_esc/test/test_bag_analysis_integration.py
```

Required coverage:

- sqlite3 topic/type discovery and real deserialization;
- every timestamp domain retained exactly;
- readiness filtering;
- cost-anchor matching and skew columns;
- no interpolation across missing or out-of-tolerance data;
- variable channel counts;
- state interval collapse and gap invalidation;
- event value-name/value preservation;
- fill revision/supersession and active-cluster reconstruction;
- escape success/failure/stall/assist/orbit metrics;
- revisit entry counting;
- saturation counts and limit excess;
- robust, legacy, complete, partial, invalid, failed, and not-applicable statuses;
- placeholder plots;
- output schemas and all required filenames;
- existing-output refusal and atomic publication;
- raw `.db3` checksum/mtime unchanged.

### Build and retained regression

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon --log-base /tmp/dsim_phase07_build_log build \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash

python3 -m pytest -q -rs \
  src/ros_esc/test/test_bag_analysis.py \
  src/ros_esc/test/test_bag_analysis_integration.py \
  src/ros_esc/test/test_scenario_schema.py \
  src/ros_esc/test/test_scenario_runner.py \
  src/ros_esc/test/test_experiment_recording.py \
  src/ros_esc/test/test_recording_integration.py \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_escape_recenter.py
```

All newly added tests and the retained functional suite must pass. Environment-gated Gazebo tests may remain skipped only if their exact reasons are reported; Phase 07 requires no new Gazebo or hardware run.

### Real passed and failed bags

Use separate temporary output paths and hash bags before and after:

```bash
accepted=/home/mattb/Experiments/GESC-Gaussian/runs/2026-07-21/20260721T232824094290Z_simulation_phase05-short-recording_92bb8be7
failed=/home/mattb/Experiments/GESC-Gaussian/runs/2026-07-21/20260721T230813124669Z_simulation_phase05-short-recording_1e5e6063
analysis_tmp="$(mktemp -d)"

sha256sum "$accepted"/bag/*.db3 "$failed"/bag/*.db3

ros2 run ros_esc analyze_run "$accepted" \
  --output-dir "$analysis_tmp/accepted"
ros2 run ros_esc analyze_run "$failed" \
  --output-dir "$analysis_tmp/failed"

sha256sum "$accepted"/bag/*.db3 "$failed"/bag/*.db3
```

Acceptance:

- Accepted run reports recording passed and analysis complete, with fill/escape outputs marked not applicable.
- Failed run still produces all outputs, preserves the Phase 05 failure reasons, and reports partial or invalid according to its critical data.
- Input hashes are identical.
- No output is written into `bag/` and root `completeness.json` is unchanged.

### Static, style, and global checks

```bash
python3 -m compileall -q \
  ros2_ws/src/ros_esc/ros_esc/plotting_scripts/bag_reader.py \
  ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py

python3 -c \
  'import ros_esc.plotting_scripts.bag_reader; import ros_esc.plotting_scripts.gesc_gaussian_bag_analysis'

python3 -m flake8 \
  ros2_ws/src/ros_esc/ros_esc/plotting_scripts/bag_reader.py \
  ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py \
  ros2_ws/src/ros_esc/test/test_bag_analysis.py \
  ros2_ws/src/ros_esc/test/test_bag_analysis_integration.py

python3 -m pydocstyle \
  ros2_ws/src/ros_esc/ros_esc/plotting_scripts/bag_reader.py \
  ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py

colcon --log-base /tmp/dsim_phase07_test_log test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose

git diff --check
git status --short --branch
```

Report focused totals, new tests, real-bag results, global totals, skips, unexecuted tests, and the inherited lint baseline separately.

## Risks and stop conditions

Stop as Level A before edits or further work if:

- Phase 07 implementation context is incomplete.
- sqlite3 or `rosbag2_py` is unavailable.
- Live message definitions or manifest types contradict the plan without a bounded compatibility path.
- A current analysis owner already exists and would be duplicated.
- Analysis requires changing recorder/completeness policy, ROS messages/topics, controller behavior, or simulation/physical algorithm ownership.
- The pre-existing wrapper edit cannot be preserved.
- Physical hardware or a Heavy-Ball path would be required.
- A raw bag, root completeness report, or user-owned artifact would need overwriting.

Handle as Level B only for local, testable reader/API/runtime corrections that preserve the output contract and do not weaken validity/completeness rules; record exact evidence and tests in the handoff.

Treat missing behavior or failed experimental outcomes as evidence:

- Retain failed runs.
- Emit partial/invalid/not-applicable metrics honestly.
- Never turn missing fill, escape, collision, or ground-truth data into zero or success.
- Never relabel Phase 07 extraction coverage as Phase 08 robustness acceptance.

## Implementation-time verification

Before editing, verify:

- HEAD, branch, dirty-tree scope, and absence of overlap with the user wrapper.
- The saved plan exists and `validate_phase_context.sh 07 implement` passes.
- The installed and source manifests agree on sqlite3 and real topic types.
- `rosbag2_py.get_registered_readers()` contains `sqlite3`.
- Generated message imports resolve after sourcing the workspace.
- The retained accepted and failed Phase 05 directories still exist and remain readable.
- `resolved_parameters.yaml` still stores `/gaussian_fill.estimation_channel_index`, `sample_sync_tolerance_sec`, supervisor rate, escape thresholds, and relevant command limits in the audited structure.
- Phase 06 metadata continues to provide source roles/tolerances only when ground-truth evaluation is authorized.
- No durable retained run currently covers fill/escape/assist/recenter; if that changes, analyze it as additional evidence but keep deterministic fixtures.
- The default output path is writable and absent; never remove an existing analysis directory.
- Current baseline remains attributable: Phase 06 reported 143 focused passes with two guarded skips and a global `1027 tests, 0 errors, 872 failures, 3 skipped`, with remaining failures inherited lint debt.
