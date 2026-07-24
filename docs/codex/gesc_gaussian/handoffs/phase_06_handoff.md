# Phase 06 Handoff

## Objective completed

Implemented the bounded Phase 06 deterministic serial Gazebo scenario runner.
The runner validates and expands schema-version-1 scenario YAML, assigns an
explicit deterministic seed and unique non-overwriting run ID to every
resolved run, and composes the existing:

- `ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml`;
- `ros2 run ros_esc record_run`;
- Phase 05 topic manifest, run-directory layout, and validator;
- existing `legacy` and `robust_gaussian_v1` algorithm profiles;
- existing source, start-pose, bounds, escape, fill, affine, recenter, and
  controller-saturation controls.

Execution is serial and headless by default. Every launched case has a scoped
wall timeout, ordered recorder shutdown, exact-process-session and ROS-graph
cleanup checks, retained success/failure artifacts, resolved scenario
metadata, and separate controller-observable versus simulation-ground-truth
outcomes.

No second recorder, validator, launch graph, run format, algorithm node,
controller fork, Heavy-Ball path, physical launch, topic, message, cost sign,
unit, or public default was introduced.

## Context and ownership verification

The required pre-edit command passed:

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 06 implement
Phase 06 implement context is complete.
```

The saved Phase 06 plan, implementation package, all Phase 00 audit artifacts,
knowledge bridge, and every prior handoff through Phase 05.5 were read before
editing. Live repository search confirmed:

- no active GESC scenario/matrix/sweep runner exists;
- retired Heavy-Ball runners are historical and were not reused;
- `record_run.py` remains the sole recording/run-directory/ordered-shutdown
  owner;
- `validate_run.py` remains the sole completeness authority;
- `gazebo.launch.xml` remains the sole simulation graph;
- Gazebo and gzserver expose `--seed`;
- Uniform noise has an effective seed, while Gaussian noise still seeds the
  wrong RNG;
- no sensor-delay, pose-delay, wall-contact, collision-truth, authoritative
  discrete light-level mapping, or physical adapter exists.

The pre-edit focused baseline was `113 passed, 1 skipped in 3.74s`. The
accepted Phase 05 run also passed validation before editing.

## Implementation

### Scenario schema and deterministic expansion

`scenario_schema.py` implements strict unknown-key rejection and validation
for:

- simulation-only mode and schema version;
- serial execution (`max_parallel_runs=1`);
- finite ordered bounds, in-bounds start poses, room center, and timeouts;
- explicit profiles, start poses/headings, seeds, source geometries, source
  roles, and one-to-five source limits;
- numeric simulator-relative intensity and optional explicit `level_map`;
- ordered profile/start/source-level/seed Cartesian expansion;
- deterministic SHA-256 case keys;
- supported Uniform noise and explicit unsupported disturbance records;
- component ablations and explicit success predicates.

The same resolved object produces launch argv and recording metadata. Seeds are
passed to Gazebo, supported Uniform noise, and Phase 05 metadata. Run IDs add a
UTC timestamp and UUID fragment to the deterministic case identity.

### Serial orchestration and artifacts

`run_scenario.py`:

- invokes argv directly without a shell;
- starts the shared ros2cli daemon before creating per-run process sessions;
- launches every run through `record_run`;
- times out and signals only the exact process group it created;
- finds run directories by exact run ID across UTC date directories;
- compares the post-run ROS graph to its suite baseline;
- checks for survivors in the exact run session;
- retains ordinary failed runs and stops immediately on cleanup failure;
- reads the completed sqlite3 bag only for minimal Phase 06 classification;
- collapses repeated state samples into an observed transition sequence;
- reports robust controller goal, legacy not-applicable state, final-pose
  ground truth, required states/events, forbidden events, saturation count,
  timeout, recording, and cleanup separately.

Every launched run adds:

- `scenario_definition.yaml`;
- `resolved_scenario.yaml`;
- `scenario_result.yaml`;
- `resolved_cost_function.json` when seeded Uniform noise is selected.

The suite summary defaults to
`<runs-root>/scenario_summaries/<UTC>_<suite_id>.yaml`.

### Scenario suites

`phase06_smoke.yaml` contains identical short robust and legacy recorded
profiles. `phase06_catalog.yaml` expands to 26 executable-unverified runs
covering:

- two-source spacing/overlap and close minima;
- three- and four-source geometries;
- virtual boundary/corner placement;
- seeded Uniform noise;
- multiple starts/headings and velocity saturation;
- pure repulsion, stalled assisted escape, fill merge, and recenter/resume;
- legacy-versus-robust comparisons;
- Gaussian-fill, affine-assist, and recenter ablations.

Seven catalog records remain explicitly unsupported and are never launched:

1. discrete source levels 1-5 without an authoritative `level_map`;
2. sensor and pose delay;
3. deterministic Gaussian noise;
4. physical-wall collision truth;
5. static raw-attraction ablation;
6. more than five sources;
7. plain non-PDE legacy recording under the shared manifest.

All executable empirical cases are labeled `executable_unverified`. Phase 06
does not claim that the catalog meets Phase 08 robustness acceptance.

### Existing-owner extensions

- Simulation recording metadata now accepts `legacy` and
  `robust_gaussian_v1`; physical recording remains robust-only.
- The existing validator uses the same audited per-mode profile table while
  retaining every manifest, timestamp, semantics, coverage, final-zero,
  shutdown, and console gate.
- Direct Gazebo launches retain visible/unseeded defaults. Additive launch
  arguments select GUI versus gzserver and optional `--seed`.
- Opt-in legacy simulation observability now publishes the existing canonical
  `/gesc_gaussian/source_cost` message required by the unchanged Phase 05
  manifest. Default legacy observability remains off and numerical behavior is
  unchanged.

## Exact files

Created:

- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/__init__.py`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase06_smoke.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase06_catalog.yaml`
- `ros2_ws/src/ros_esc/test/test_scenario_schema.py`
- `ros2_ws/src/ros_esc/test/test_scenario_runner.py`
- `docs/codex/gesc_gaussian/handoffs/phase_06_handoff.md`

Updated:

- `ros2_ws/src/ros_esc/setup.py`
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/record_run.py`
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/validate_run.py`
- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py`
- `ros2_ws/src/ros_esc/test/test_experiment_recording.py`
- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`
- `ros2_ws/src/ros_esc/test/test_observability_contract.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/empty_world.launch.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
- `docs/codex/gesc_gaussian/recording_runs.md`
- `docs/codex/gesc_gaussian/topic_dictionary.md`
- `docs/codex/gesc_gaussian/test_commands.md`

The source/config/test/doc split exceeds roughly ten files because schema,
orchestration, checked-in suites, existing-owner compatibility, launch
plumbing, tests, and durable handoff have separate repository owners. No
single mixed commit was used. The work was checkpointed coherently as:

- `7cc9ace` — Phase 05.5 durable context and workflow dependency;
- `b84518a` — runner, schema, scenarios, packaging, and focused tests;
- `04505ca` — existing-owner launch, recording, validation, and compatibility
  integration;
- the final documentation checkpoint containing this handoff and the shared
  parameter/test references.

The pre-existing user edit in
`gesc_gaussian_full_rotation_voltage.bash` was not touched.

## Bounded Level B corrections

Five runtime corrections were required and retained without weakening gates:

1. Headless gzserver initially inherited `DISPLAY=:0` and failed GLX
   initialization. Only headless ExecuteProcess actions now receive an empty
   `DISPLAY`; visible direct-launch behavior is unchanged.
2. `cost_function` used rclpy's default signal handler and could exit with
   status 245 during recorder SIGINT cleanup. It now uses the repository's
   proven explicit executor and `SignalHandlerOptions.NO` shutdown order.
3. The ros2cli daemon was first created inside the per-run process session and
   appeared as contamination. The suite now starts the shared daemon before
   capturing the graph/session baseline.
4. Installed entry-point execution could not infer the checkout from its
   installed module path. Repository discovery now prefers
   `git rev-parse --show-toplevel`, with bounded source/conventional fallbacks.
5. Legacy PDE observability lacked `/gesc_gaussian/source_cost`, so the
   unchanged manifest correctly rejected it. The existing simulation source
   owner now creates that publisher whenever observability is explicitly
   enabled. The value semantics and invalid source-score markers already
   existed and are tested.

The failed diagnostic run directories were preserved:

```text
/tmp/pytest-of-mattb/pytest-2/test_recorded_short_headless_e0/runs/2026-07-24/20260724T202317076553Z_simulation_phase06_smoke-recorded_profile_smoke-robust_gaussian_v1-f562307ac8_9d58555b
/tmp/pytest-of-mattb/pytest-3/test_recorded_short_headless_e0/runs/2026-07-24/20260724T202556351149Z_simulation_phase06_smoke-recorded_profile_smoke-robust_gaussian_v1-f562307ac8_8530f043
/tmp/pytest-of-mattb/pytest-4/test_recorded_short_headless_e0/runs/2026-07-24/20260724T203110600629Z_simulation_phase06_smoke-recorded_profile_smoke-legacy-5d2c1438c0_100a4f95
```

Focused shutdown, publisher, schema, orchestration, cleanup, and end-to-end
tests cover the corrections.

## Recorded runtime acceptance

The environment-gated headless end-to-end pytest ran both profiles serially:

```text
1 passed in 207.60s
```

Accepted run directories:

```text
/tmp/pytest-of-mattb/pytest-8/test_recorded_short_headless_e0/runs/2026-07-24/20260724T203530142261Z_simulation_phase06_smoke-recorded_profile_smoke-robust_gaussian_v1-f562307ac8_ed189846
/tmp/pytest-of-mattb/pytest-8/test_recorded_short_headless_e0/runs/2026-07-24/20260724T203721764538Z_simulation_phase06_smoke-recorded_profile_smoke-legacy-5d2c1438c0_a06b57e6
```

Both runs:

- returned through the recorder with no wall timeout;
- produced unique Phase 05 directories and required artifacts;
- had `completeness.json` `passed: true`;
- had no remaining new ROS nodes;
- had no remaining exact-session processes;
- produced `scenario_result.yaml`;
- passed their explicit smoke predicates: recording and cleanup.

The robust short run observed state `SEARCH` and event
`CONVERGENCE_CANDIDATE`. Its controller goal and final-pose ground truth were
both `failed`; final distance to `source_1` was approximately 0.861 m. Legacy
correctly reported controller goal `not_applicable`; ground truth was `failed`
at approximately 0.873 m. Those outcome fields were not smoke predicates and
are not silently promoted to success.

There was no Level C acceptance-gate failure: the executed smoke's explicit
recording and cleanup criteria passed. The behavioral catalog was not run and
remains unverified.

## Tests and results

### Build

```text
colcon build --packages-select \
  ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
PASS: 3 packages finished.
```

### Focused and newly added tests

```text
Focused Phase 00-06 matrix:
143 passed, 2 skipped in 3.77s.

Recorded Phase 06 headless E2E:
1 passed in 207.60s.
```

The two new modules contain 29 ordinary tests plus the one gated end-to-end
test. New behavior covered includes strict parsing, 25 ordered level
combinations, deterministic case keys, exact seeded Uniform repeatability,
stable expansion, profile/source/start/bounds metadata-to-launch identity,
unique/date-safe run lookup, direct argv without a shell, legacy and robust
generation, classification, controller/ground-truth separation, exact-session
cleanup, failure retention, cleanup-stop behavior, and summaries.

### Syntax, imports, XML/YAML, style, and diff

- Python `compileall`: passed for scenario, recording, cost-function, and
  launch Python.
- Installed imports: passed for schema, runner, recorder, and validator.
- `gazebo.launch.xml` ElementTree parse and package xmllint: passed.
- Both scenario YAML documents loaded successfully.
- Focused E/W/F flake8 passed for the new runner/schema, changed
  recorder/validator/tests, and modified launch.
- Fatal syntax/undefined-name flake8 passed for the legacy cost-function owner;
  its unrelated historical E226/E231 formatting debt remains.
- `git diff --check`: passed.

An external pre-commit review correctly identified 1,413 strict-style findings
in the new runner/schema/tests. Before checkpointing, all 1,331 quote findings
were normalized mechanically and the remaining line-length, import-order,
test-docstring, and function-docstring-spacing findings were corrected. Final
unfiltered flake8 and ament pep257 checks on every new Phase 06 Python file
pass with no findings.

### Accepted Phase 05 bag regression

```text
/home/mattb/Experiments/GESC-Gaussian/runs/2026-07-21/20260721T232824094290Z_simulation_phase05-short-recording_92bb8be7
passed: true
failures: []
warnings: []
```

### Global status and baseline trend

```text
Current:  1027 tests, 0 errors, 872 failures, 3 skipped
Prior:     999 tests, 0 errors, 875 failures, 2 skipped
Trend:     +28 tests, 0 errors, -3 failures, +1 skip
```

The remaining failure records are package-wide flake8, pep257, and lint-cmake
results. The numerical global trend improves by three, but the two existing
`ros_esc` lint meta-tests now contain no finding from the new Phase 06
runner/schema/tests. The functional `ros_esc` result inside colcon was
`143 passed, 2 lint meta-test failures, 3 skipped`. The three global skips are
the existing copyright skip, visible Phase 05 Gazebo recording guard, and new
Phase 06 headless E2E guard.

### Exact skips and unexecuted tests

- Ordinary focused pass skipped the Phase 06 headless E2E because
  `RUN_GESC_PHASE06_GAZEBO_E2E` was unset; it was run separately and passed.
- The older visible Phase 05 pytest remained skipped because
  `DSIM_RUN_GAZEBO_RECORDING_TEST` was unset. Its retained accepted run passed
  the current validator.
- The 26 behavioral catalog runs were not executed or tuned; Phase 08 owns the
  acceptance matrix.
- Seven unsupported catalog dimensions were not launched.
- No physical launch, hardware, sensor, Vicon, or robot command was run.

### Final authoritative totals

- focused: `143 passed, 2 skipped`;
- Phase 06 recorded E2E: `1 passed`;
- global: `1027 tests, 0 errors, 872 failures, 3 skipped`;
- accepted Phase 05 bag: `passed: true`, zero failures/warnings;
- Phase 06 recorded profiles: 2/2 completeness passed, 2/2 cleanup passed.

## Compatibility and limitations

- Direct `gazebo.launch.xml` remains visible, unseeded, and legacy by default.
- The runner is simulation-only and always uses PDE extensions,
  observability, and the recording interlock to satisfy the one shared
  manifest.
- Numeric intensity is simulator-relative and is not lux or physical
  calibration.
- Gazebo seeding and Uniform noise are deterministic inputs; Phase 06 does not
  claim bit-for-bit physics reproducibility.
- Discrete light levels, Gaussian determinism, delay injection, collision
  truth, more than five sources, and a plain non-PDE legacy recording remain
  unsupported.
- Controller goal and simulation ground truth are deliberately separate.
- Full robustness, repeated trials, tuning/holdout, and acceptance remain
  Phase 08 work.
- Strict full-package style remains red from files outside the new Phase 06
  runner/schema/tests.
- After the Phase 06 checkpoints, the only expected working-tree change is the
  untouched user wrapper edit.

## Blocking issues

None for Phase 07 planning.

## Phase 07 readiness

`READY WITH NONBLOCKING LIMITATIONS`

Phase 07 may consume the existing sqlite3 bags and Phase 06 scenario metadata,
but must not infer that unexecuted catalog cases or Phase 08 gates passed.
Before building behavior plots, Phase 07 should inventory the available bags
for `DESIGN_OR_MERGE_FILL`, `ESCAPE_REPULSE`, `ESCAPE_ASSIST`, `RECENTER`,
fill creation, and fill merge. If those behaviors are absent, run only a
minimal analysis-coverage subset or add focused fixtures; do not mislabel that
coverage work as Phase 08 acceptance.

## Git status

Branch: `feature/gesc-gaussian-robustness-v1`.

Phase 05.5 and Phase 06 implementation are committed in the checkpoints listed
above. The final documentation commit is the commit containing this handoff.
The pre-existing `gesc_gaussian_full_rotation_voltage.bash` modification
remains intentionally uncommitted and untouched.

## Recommended commit message

```text
phase 06: add deterministic Gazebo robustness runner
```
