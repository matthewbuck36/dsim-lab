# Phase 07 Handoff

## Objective completed

Implemented the bounded standard offline rosbag analysis pipeline inside the
existing `ros_esc` plotting owner. The installed commands analyze complete and
failed Phase 05/06 sqlite3 runs, preserve all recorded timestamp domains and
raw artifacts, export CSV by default, create eight separate diagnostic
figures, calculate validity-marked run metrics, and aggregate existing
per-run analyses into a matrix summary.

No controller, supervisor, Gaussian owner, recorder, validator, scenario
runner, launch graph, topic, message, cost sign, unit, simulation/physical
semantic, Heavy-Ball path, or physical hardware behavior changed.

## Context and repository state

- Branch: `feature/gesc-gaussian-robustness-v1`.
- Starting and current HEAD: `8c6191d` (`phase 06: add deterministic Gazebo
  robustness runner`); Phase 07 created no commit.
- Required pre-edit validator:
  `Phase 07 implement context is complete.`
- The saved Phase 07 plan, five Phase 00 audit documents, knowledge bridge,
  Phase 05.5 handoff, and every prior implementation handoff through Phase 06
  were read and verified against live source and retained runs.
- The pre-existing user modification to
  `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash`
  remains unstaged and untouched.
- The authoritative saved `phase_07_plan.md` remains untracked as it was at
  phase start.
- Build/test output stayed in ignored workspace trees with colcon logs under
  `/tmp/dsim_phase07_*`.

Live verification found sqlite3 registered for rosbag2 read/write, the six
generated canonical message types importable, the Phase 05 manifest and
installed manifest consistent, the retained passed and failed runs readable,
and no existing bag-analysis or matrix-summary owner.

## Exact files

Created:

- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/bag_reader.py`
- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py`
- `ros2_ws/src/ros_esc/test/test_bag_analysis.py`
- `ros2_ws/src/ros_esc/test/test_bag_analysis_integration.py`
- `docs/codex/gesc_gaussian/handoffs/phase_07_handoff.md`

Updated:

- `ros2_ws/src/ros_esc/setup.py`
- `ros2_ws/src/ros_esc/package.xml`
- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/README.md`
- `docs/codex/gesc_gaussian/recording_runs.md`
- `docs/codex/gesc_gaussian/topic_dictionary.md`
- `docs/codex/gesc_gaussian/test_commands.md`

The phase has two implementation modules and stays within the roughly ten-file
implementation limit. Tests and documentation follow their existing separate
owners, so no subcommit split was needed.

## Public offline interfaces

Installed commands:

```text
ros2 run ros_esc analyze_run RUN_DIRECTORY
  [--output-dir PATH]
  [--channel-index N]
  [--sync-tolerance-sec SEC]

ros2 run ros_esc summarize_matrix INPUT [...]
  --output-dir PATH
```

`analyze_run` defaults to `<RUN_DIRECTORY>/analysis/phase07`; existing output
directories are rejected. A readable run returns 0 after producing evidence
even when recording or experiment behavior failed. Input, deserialization,
atomic-publication, or output errors return 2.

`summarize_matrix` accepts per-run analysis directories, run directories with
the default analysis path, direct `summary_metrics.json` files, or a directory
tree containing summaries. It writes `matrix_summary.csv` and
`matrix_summary.json` atomically and rejects an existing output directory.

No ROS parameter was added. `--channel-index` defaults to the captured
`estimation_channel_index`, then an explicitly warned fallback of 0.
`--sync-tolerance-sec` defaults to the captured
`sample_sync_tolerance_sec`, then an explicitly warned fallback of 0.05.
State-gap validation reads captured `supervisor_publish_rate_hz`, with an
explicitly warned fallback of 20.0 Hz.

Direct runtime dependencies `python3-numpy` and `python3-matplotlib` are now
declared; the existing rosbag2, runtime-message, PyYAML, and SciPy declarations
remain.

## Timestamp and synchronization contract

Every raw CSV row preserves:

- exact `bag_timestamp_ns`;
- typed/header `ros_timestamp_ns` when present;
- legacy `source_timestamp_sec` and validity when present;
- readiness-interval membership;
- motion-relative time from the first recorded readiness-true bag stamp.

The first readiness true through the following false defines the motion
interval. Raw preflight/shutdown records remain exported.

`/gesc_gaussian/cost_breakdown` is the synchronization anchor. Source cost,
GESC diagnostics, odometry, and control diagnostics use deterministic nearest
absolute typed/header ROS time within the resolved tolerance. Algorithm state
uses the latest causal sample within that tolerance. Missing matches have
empty values, `*_valid=false`, skew/reason fields, and no interpolation,
extrapolation, or forward fill. Headerless legacy topics never substitute for
missing canonical diagnostics.

## Output and metric behavior

Each readable run produces:

- 11 CSV tables for synchronized samples, raw canonical topics, state
  intervals, events, typed fill history, and escape attempts;
- 8 separate figures for cost, components, state/events, weights,
  trajectory/sources/fills, command saturation, radial escape, and Gaussian
  history;
- `summary_metrics.json`, `summary_metrics.csv`, and
  `analysis_completeness.json`.

Unavailable figures remain real PNG files with an explicit unavailable reason.
Variable event names/values remain JSON cells, and six-component command
arrays use repository order `[vx, vy, vz, wx, wy, wz]`.

Every summary metric contains `value`, `status`, `unit`, `reason`, and
`provenance`. Implemented metrics include:

- readiness duration, path length, convergence time, and controller/ground
  truth success;
- escape attempts, successes, failures, total escape time, maximum published
  radial progress, stall/assist evidence, exit hold, and approximate orbit
  count from absolute unwrapped odometry angle about frozen escape geometry;
- outside-to-inside revisit crossings of active typed fill exit ellipses;
- fill creation, active-cluster, merge, supersession/event, and design
  escalation evidence;
- readiness-clipped state durations, transition count, and terminal state,
  with gaps over three captured supervisor periods invalidated;
- saturation time, saturation fraction, per-axis counts, and maximum
  unsaturated limit excess;
- timeout, failsafe, recording completeness, and collision availability.

Typed fill revisions are authoritative; `/cost_bias` is not used for robust
fill history. Simulation ground truth is computed only when
`resolved_scenario.yaml` supplies goal IDs and a final-position tolerance.
Collision remains unavailable because no audited contact-truth topic exists.

Analysis completeness is `complete`, `partial`, or `invalid`. Behavior that
did not occur is `not_applicable`. Critical missing cost/pose/control/readiness
data becomes invalid rather than a fabricated zero. A failed Phase 05
validation remains a separate recording failure while useful analysis outputs
remain first-class evidence.

## Backward compatibility and retention

- Analysis is opt-in and offline.
- Root run artifacts, raw `.db3` files, stored `completeness.json`, metadata,
  resolved topics/parameters, and scenario results are read-only.
- Raw bag SHA-256 is checked before and after every analysis.
- Existing plotting and legacy CSV paths remain available.
- Legacy and robust profiles use the same command; unavailable robust behavior
  in legacy data is validity-marked.
- The same reader remains available for future audited physical bags; no
  physical-specific fork or inferred physical metric was introduced.

## Tests and results

### Build

```text
colcon --log-base /tmp/dsim_phase07_build_log_final build
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
PASS: 3 packages finished.
```

### Focused changed-package tests

Pre-edit retained baseline:

```text
143 passed, 2 skipped in 3.72s
```

New Phase 07 tests:

```text
10 passed in 4.38s
```

Final Phase 00-07 focused suite:

```text
153 passed, 2 skipped in 7.77s
```

The generated fixture uses `rosbag2_py.SequentialWriter`, sqlite3, CDR
serialization, and real ROS message classes. Coverage includes exact
timestamp preservation, bounded nearest/causal matching, no interpolation,
state-gap validity, complete/partial/invalid/not-applicable statuses, standard
files and placeholders, escape/path/radial/revisit/fill/merge/saturation/
success metrics, failed-run retention, raw hash/mtime preservation,
non-overwrite/atomic output, and complete-plus-failed matrix aggregation.

### Retained passed and failed bags

Final temporary analysis root:

```text
/tmp/dsim_phase07_real_bags_final.WKZRlx
```

Accepted Phase 05 run:

```text
analysis status: complete
fresh Phase 05 validation: passed
outputs: 11 CSV tables, 8 PNG plots
fill/escape/orbit: not applicable
```

Failed Phase 05 run:

```text
analysis status: partial
fresh Phase 05 validation: failed
recording failures retained:
  - typed ROS timestamps regressed by more than 50 ms
  - console contains a ROS/process failure marker
outputs: 11 CSV tables, 8 PNG plots
fill/escape/orbit: not applicable
```

The matrix command found two runs, one complete and one partial. SHA-256 values
for both raw bags and both root completeness reports matched exactly before
and after. No output was written under either `bag/` directory.

These short retained runs contain no fill/escape/recenter lifecycle and do not
constitute Phase 08 robustness acceptance. The generated fixture supplies
analysis coverage only.

### Diff, syntax/import, and focused style

- Python `compileall`: passed for both implementation modules and both tests.
- Installed imports: passed for reader and analyzer.
- `ament_flake8`: no problems in the two modules and two tests.
- `ament_pep257`: no problems in the two modules and two tests.
- Package-wide lint XML: zero Phase 07 reader/analyzer/test findings.
- `git diff --check`: passed.

### Global baseline and trend

```text
Current: 1037 tests, 0 errors, 872 failures, 3 skipped
Prior:   1027 tests, 0 errors, 872 failures, 3 skipped
Trend:   +10 test records, 0 errors, 0 failures, 0 skips
```

The 872 failures remain inherited package-wide flake8, pep257, and lint-cmake
debt. The functional `ros_esc` result was `153 passed`, two inherited lint
meta-test failures, and three global skips.

### Exact skips and unexecuted tests

- The ordinary focused suite skipped the Phase 06 headless Gazebo E2E because
  `RUN_GESC_PHASE06_GAZEBO_E2E` was unset. Its retained prior run passed.
- The ordinary focused suite skipped the Phase 05 visible Gazebo recording
  test because `DSIM_RUN_GAZEBO_RECORDING_TEST` was unset. Its retained
  accepted run revalidated and analyzed successfully.
- The third global skip is the inherited copyright skip.
- No new Gazebo run was required or executed.
- The 26 Phase 06 behavioral catalog runs, Phase 08 acceptance matrix, and
  seven unsupported catalog dimensions were not executed.
- No physical launch, hardware, sensor, Vicon, or robot command was run.

### Final authoritative totals

- new Phase 07 tests: `10 passed`;
- focused functional suite: `153 passed, 2 skipped`;
- real bags: 1 complete, 1 partial, 22 CSV tables, 16 PNG plots;
- matrix aggregation: 2/2 per-run summaries included;
- global: `1037 tests, 0 errors, 872 failures, 3 skipped`;
- focused Phase 07 lint/style findings: 0;
- raw/root retained artifact hash changes: 0.

## Contradictions and amendments

### Level A hard contradictions

None.

### Level B bounded implementation correction

The saved plan froze only the `analyze_run` entry point, while the authoritative
Phase 07 implementation prompt explicitly requires both a one-run command and
a matrix-summary command. Live search confirmed no existing summary owner.

The bounded correction adds `summarize_matrix` as a second entry point into the
same approved analysis module. It only aggregates already-produced
`summary_metrics.json` files, adds no ROS interface or algorithm owner, changes
no per-run result, and is covered by complete/partial aggregation,
percentile/rate, atomic output, and overwrite-refusal tests. Files:
`setup.py`, `gesc_gaussian_bag_analysis.py`, both analysis documentation
owners, and focused tests. The correction completes the explicit requirement
without expanding controller, recording, simulation, or acceptance scope.

### Level C acceptance or research failures

None for the declared Phase 07 software/data gates. The retained failed run is
reported honestly as partial evidence, not a Phase 07 failure or success. No
Phase 08 behavioral gate was run or claimed.

## Known limitations and unresolved issues

- The global inherited lint baseline remains red at 872 failures.
- Retained real runs do not cover fill, merge, escape, assist, revisit,
  recenter, or goal success; those paths are tested with deterministic
  generated bags but remain empirically unverified.
- Collision/contact truth remains unavailable.
- Raw sensor and filtered sensor fields remain unavailable in the current
  simulator adapter; raw minimization cost remains valid.
- Ground-truth success is unavailable without Phase 06 scenario metadata.
- Revisit evaluation requires valid active typed fill covariance and escape
  lifecycle; otherwise it is invalid or not applicable.
- Analysis output can be large because it preserves raw canonical rows and
  never deletes bags.

There is no blocking Phase 07 implementation issue. Phase 08 must still tune,
freeze, execute, and honestly evaluate the declared matrix before any
simulation-ready claim.

## Exact next phase

Start a new Plan-mode chat with:

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/08_validation_PLAN.md
```

Before planning, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh \
  08 plan
```

Save the approved plan at:

```text
docs/codex/gesc_gaussian/plans/phase_08_plan.md
```

## Recommended commit message

```text
phase 07: add rosbag analysis and standard diagnostics
```
