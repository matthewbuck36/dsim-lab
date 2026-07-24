# Phase 06 Plan — Deterministic Serial Gazebo Scenario Runner

## Objective and scope

Implement a repeatable, deterministic, serial Gazebo scenario runner inside the existing `ros_esc` package.

The runner will:

- validate and expand versioned scenario YAML;
- execute each resolved case through `ros2 run ros_esc record_run`;
- use only `turtlebot3_rotating_sensor/launch/gazebo.launch.xml`;
- pass existing source, start-pose, profile, ablation, bounds, escape, and recenter arguments;
- assign deterministic seeds and unique non-overwriting run IDs;
- preserve every successful or failed Phase 05 run directory;
- verify cleanup after every run;
- write per-run and suite-level scenario summaries;
- report controller-observable success separately from simulation ground truth.

Phase 06 will not create another algorithm node, launch graph, recorder, validator, run-directory format, analysis pipeline, physical path, or Heavy-Ball workflow. Detailed bag synchronization, metrics, and plots remain Phase 07; tuning and the full acceptance matrix remain Phase 08.

This Plan-mode chat has not written the artifact. Save this document verbatim as:

`docs/codex/gesc_gaussian/plans/phase_06_plan.md`

Do not begin implementation until:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 06 implement
```

passes against that saved file.

## Repository findings

The required planning preflight passed:

```text
Phase 06 plan context is complete.
```

Current repository state:

- branch: `feature/gesc-gaussian-robustness-v1`;
- HEAD: `a7df8cf`;
- the tree is intentionally dirty with known durable-document and user-owned wrapper changes;
- the Phase 06 edit set does not include the user-owned
  `gesc_gaussian_full_rotation_voltage.bash`.

Relevant live findings:

- No active GESC scenario, matrix, sweep, or batch runner exists.
- A retired Heavy-Ball scenario runner and archived matrices exist under `Depreciated/` and `writing/`; they must not be revived or extended.
- `record_run.py` is the sole run-directory, rosbag, readiness-interlock, ordered-shutdown, final-zero, and descendant-cleanup owner.
- `validate_run.py` is the sole completeness validator.
- `gazebo.launch.xml` is the central simulation graph.
- Gazebo supports initial `x`, `y`, and yaw; zero to five numeric relative-intensity light sources; virtual bounds and room center; robust/legacy profiles; escape/recenter parameters; and selected component controls.
- Gazebo Classic on this host supports `--seed`, while the current launch does not expose it.
- The current launch always starts the Gazebo GUI. Phase 06 will add an additive server-only option while preserving the current visible launch default.
- Existing `Uniform` sensor noise accepts a deterministic `seed_num`. The current `Gaussian` implementation seeds Python’s RNG but samples NumPy’s RNG, so seeded Gaussian noise is not deterministic and will remain explicitly unsupported in Phase 06.
- No sensor-delay or pose-delay injection exists.
- No wall/contact/collision sensor exists. Wall and corner cases can test only the configured virtual bounds.
- Numeric relative source intensity is supported, but no authoritative mapping from discrete light levels 1–5 to numeric intensity exists.
- `record_run` and `validate_run` currently require `robust_gaussian_v1`, which conflicts with the Phase 06 legacy-versus-robust requirement. This is a bounded Level B compatibility correction: extend the existing recorder and validator for recorded simulation legacy runs without weakening topic, shutdown, or completeness gates.
- A recorded legacy comparison must use `use_pde_extensions=True` and `enable_observability=True` because the Phase 05 manifest requires `/cost_modified` and the canonical typed topics. Plain `use_pde_extensions=False` legacy recording remains unsupported by the current manifest.

## Existing implementation to reuse or extend

- `ros_esc/experiment_recording/record_run.py`: invoke once per resolved run; retain its run-ID protection, readiness gate, metadata, rosbag start/stop, final-zero capture, and cleanup.
- `ros_esc/experiment_recording/validate_run.py`: remain the only completeness authority; make its profile check accept the two audited simulation profiles while retaining every other gate.
- `ros_esc/experiment_recording/topic_manifest.yaml`: reuse unchanged.
- `gazebo.launch.xml`: pass existing algorithm, source, pose, bounds, escape, recenter, observability, and recording arguments.
- `empty_world.launch.py`: extend only to select `gazebo` versus `gzserver` and optionally pass a deterministic Gazebo seed.
- `Multi_Light_Source_Cost`: continue using its zero-to-five source slots and negative-voltage minimization semantics.
- Existing `Uniform` noise: use only with an explicit seed; do not alter legacy noise classes.
- `AlgorithmState`, `AlgorithmEvent`, `ControlDiagnostics`, `/odom`, and `/gesc_gaussian/recording_ready`: read from completed bags for minimal Phase 06 outcome classification.
- `setup.py`: install the scenario assets and register one orchestration console entry point.

The new runner is a non-ROS console tool with a distinct orchestration responsibility. It will not publish algorithm topics or own any controller state.

## Files to modify

Implementation and launch:

- `ros2_ws/src/ros_esc/setup.py`
  - Register `run_scenario = ros_esc.scenario_runner.run_scenario:main`.
  - Install the checked-in Phase 06 scenario YAML files.
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/record_run.py`
  - Accept `legacy` and `robust_gaussian_v1` for simulation metadata.
  - Preserve the current robust and physical behavior.
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/validate_run.py`
  - Replace the robust-only gate with an audited-profile gate.
  - Retain all topic, clock, semantic, coverage, final-zero, console, and cleanup checks.
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/empty_world.launch.py`
  - Add visible/server-only selection and optional Gazebo seeding.
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
  - Declare and forward the three additive Gazebo execution arguments.

Tests and documentation:

- `ros2_ws/src/ros_esc/test/test_experiment_recording.py`
  - Cover accepted simulation legacy metadata and continued rejection of unknown profiles.
- `docs/codex/gesc_gaussian/recording_runs.md`
  - Document scenario execution as a composition layer over `record_run`.
- `docs/codex/gesc_gaussian/topic_dictionary.md`
  - Add the console and launch interfaces.
- `docs/codex/gesc_gaussian/test_commands.md`
  - Append exact Phase 06 commands and results.

## Files to create

Implementation:

- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/__init__.py`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py`
  - Pure YAML validation, default resolution, deterministic matrix expansion, launch-argument construction, and unsupported-dimension classification.
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py`
  - CLI, serial execution, metadata generation, `record_run` composition, scoped timeout handling, cleanup verification, minimal bag outcome extraction, and summary writing.

Scenarios:

- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase06_smoke.yaml`
  - Short robust and legacy recorder/orchestration cases using explicit source arguments.
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase06_catalog.yaml`
  - Supported-but-unverified behavioral families plus explicit unsupported entries.

Tests and handoff:

- `ros2_ws/src/ros_esc/test/test_scenario_schema.py`
- `ros2_ws/src/ros_esc/test/test_scenario_runner.py`
- `docs/codex/gesc_gaussian/handoffs/phase_06_handoff.md`

No package, message, service, action, ROS node, topic, or new dependency will be added. Existing `python3-yaml`, `rosbag2_py`, and `rosidl_runtime_py` dependencies are sufficient.

## Scenario YAML schema

Schema version 1 has this canonical shape:

```yaml
schema_version: 1
suite_id: phase06_example
description: Deterministic Gazebo scenario suite
mode: simulation

execution:
  max_parallel_runs: 1
  gazebo_gui: false
  runs_root: ~/Experiments/GESC-Gaussian/runs
  preflight_timeout_sec: 60.0
  run_timeout_sec: 180.0
  wall_timeout_sec: 480.0
  shutdown_grace_sec: 30.0
  stop_on_run_failure: false
  stop_on_cleanup_failure: true

metadata:
  experiment_version: phase06-v1
  operator_notes: Automated Phase 06 scenario run.

level_map: {}

defaults:
  bounds_m: [-2.0, 2.0, -2.0, 2.0]
  room_center_m: [0.0, 0.0]
  disturbances:
    sensor_noise:
      model: none
      bound: 0.0
    sensor_delay_sec: 0.0
    pose_delay_sec: 0.0

cases:
  - case_id: one_source_smoke
    family: smoke
    status: executable_unverified
    profiles: [robust_gaussian_v1]
    seeds: [6001]
    starts:
      - {id: center_east, x_m: 0.0, y_m: 0.0, yaw_rad: 0.0}
    sources:
      - id: source_1
        x_m: 1.0
        y_m: 0.5
        relative_lumen_input: 1000.0
        evaluation_role: goal
    algorithm:
      ablations:
        gaussian_fill_enabled: true
        affine_assist_enabled: true
        recenter_enabled: true
      launch_overrides: {}
    success:
      all_of: [recording_complete, cleanup_complete]
      controller:
        expected_terminal_state: null
        required_state_sequence: []
        required_events: []
        forbidden_events: []
      ground_truth:
        goal_source_ids: [source_1]
        final_position_tolerance_m: 0.35
      minimum_saturation_samples: 0
```

Validation rules:

- `schema_version` must equal `1`; `mode` must be `simulation`.
- `suite_id`, `case_id`, start IDs, and source IDs must be nonempty and unique within their scope.
- `max_parallel_runs` must equal `1`; values greater than one are rejected.
- Timeouts must be finite and positive, with `wall_timeout_sec` greater than `run_timeout_sec`.
- Bounds must be finite and ordered. Starts must lie inside bounds.
- Source count must be between one and five for executable light scenarios.
- Every source requires finite `x_m`, `y_m`, one evaluation role, and exactly one of:
  - `relative_lumen_input`, or
  - `levels`, whose labels must all resolve through `level_map`.
- Relative intensity must be finite and nonnegative and is explicitly simulator-relative, not lux.
- Multiple source `levels` lists expand by ordered Cartesian product. Two sources with `[1,2,3,4,5]` each therefore produce 25 ordered combinations.
- No default level-to-intensity mapping will be supplied. The checked-in ordered-level case remains `unsupported` until a versioned mapping is provided.
- Seeds must be explicit integers. Empty seed lists are invalid; no implicit random seed is permitted.
- Supported sensor noise is `none` or seeded `uniform`. Nonzero Gaussian noise, sensor delay, and pose delay produce an `UNSUPPORTED` summary without launching.
- `status` is `executable_unverified` or `unsupported`. Unsupported cases require a nonempty reason.
- Unknown keys, profiles, families, ablations, success predicates, or launch overrides are rejected.
- Raw-cost static ablation is unsupported because robust state weights are state-machine invariants. Supported ablations are:
  - Gaussian fill through existing `escape_policy`;
  - affine assistance through `modified_cost_enable_affine_bias`;
  - recentering through `recenter_after_escape`.
- Ground-truth source roles are metadata/evaluation-only. They are never sent to the controller.

The runtime `--operator` argument is required rather than stored as a permanent person name in checked-in scenario files.

## Scenario coverage catalog

`phase06_catalog.yaml` will contain:

- one-source smoke;
- two-source large, medium, and close separations;
- overlapping-attraction geometry;
- three-source and four-source cases;
- local sources near virtual walls and corners;
- close residual-minimum geometry;
- five starting poses/headings;
- seeded uniform sensor noise;
- final linear and angular saturation cases;
- pure-repulsion expected sequence;
- repulsion-stall and assisted-escape expected sequence;
- fill-merge expected events;
- escape, recenter, and resumed-search expected sequence;
- legacy-versus-robust cases over identical resolved geometry and seed;
- Gaussian, affine-assist, and recenter ablations.

The initial geometry will use bounds `[-2,2] × [-2,2]`, center `(0,0)`, direct numeric inputs already meaningful to the simulator, and explicit expectations. These cases are “executable but unverified”; failure to produce the intended phenomenon is a Level C result, not permission to silently tune thresholds.

The catalog will also contain skipped entries with explicit reasons for:

- ordered levels 1–5 until an authoritative `level_map` exists;
- sensor and pose delay;
- deterministically seeded Gaussian noise;
- physical-wall collision outcomes;
- static raw-attraction ablation;
- more than five sources;
- plain `use_pde_extensions=False` recording under the current manifest.

## Determinism, expansion, and run identity

For every resolved run:

- Expand cases in stable YAML order, then profile, start, ordered level tuple, and seed order.
- Pass the same seed to Gazebo `--seed`, supported sensor noise, and Phase 05 metadata.
- Do not claim bit-for-bit physics reproducibility; record the seed, resolved launch arguments, Git state, and parameters so repeated behavior can be compared honestly.
- Build a deterministic case key from suite, case, profile, start ID, level/intensity tuple, ablations, and seed.
- Generate a unique Phase 05-compatible run ID from that case key plus UTC timestamp and UUID, then pass it through `record_run --run-id`.
- Never reuse or overwrite a run ID.
- Generate metadata from the same resolved object used to construct launch arguments, preventing divergence between recorded sources and the actual target command.
- Include a nested `scenario_runner` metadata section containing the suite/case identity, seed, profile, start, sources, bounds, disturbances, ablations, expected criteria, and exact launch overrides.

For uniform noise, create a temporary resolved copy of the existing multi-light cost JSON with only its `Noise` stanza changed to `Uniform` with `bound` and `seed_num`. Source positions and intensities continue to be passed through the launch’s existing source arguments.

## Public interfaces and defaults

New CLI:

```bash
ros2 run ros_esc run_scenario SCENARIO_YAML \
  --operator OPERATOR \
  [--case-id CASE_ID ...] \
  [--runs-root PATH] \
  [--summary-output PATH] \
  [--gui] \
  [--dry-run]
```

Behavior:

- Default execution is headless and serial.
- `--gui` enables visible Gazebo for one-off debugging.
- `--dry-run` validates, expands, and prints exact `record_run` and launch argv without starting ROS, Gazebo, or rosbag.
- `--case-id` limits execution to named cases without changing expansion semantics.
- The default summary path is
  `<runs-root>/scenario_summaries/<UTC>_<suite_id>.yaml`.

New launch arguments:

| Argument | Default | Effect |
|---|---:|---|
| `gazebo_gui` | `True` | Preserve current direct-launch GUI behavior; runner passes `False` unless `--gui` is used. |
| `gazebo_use_random_seed` | `False` | Preserve current direct-launch seeding behavior. |
| `gazebo_random_seed` | `0` | Used only when `gazebo_use_random_seed=True`. |

No topic or message changes are planned.

Additive per-run artifacts:

- `scenario_definition.yaml` — original checked-in/input suite;
- `resolved_scenario.yaml` — one fully expanded case;
- `resolved_cost_function.json` — exact generated noise configuration when applicable;
- `scenario_result.yaml` — bounded Phase 06 outcome classification.

The required Phase 05 artifacts and their semantics remain unchanged.

Suite summary fields include:

- suite and schema identity;
- start/end UTC;
- selected cases and expansion count;
- unsupported entries and reasons;
- run ID and run-directory path;
- recorder/completeness result;
- cleanup result;
- controller goal result;
- simulation ground-truth result;
- observed terminal state;
- required state/event sequence results;
- failsafe/timeout indicators;
- saturation sample count;
- final distance to each configured evaluation goal;
- overall result based only on the case’s explicit `all_of` predicates.

Controller goal success is true only when recorded robust messages show `EVENT_GOAL_REACHED` and `STATE_GOAL_HOLD`. It is `not_applicable` for legacy state-unavailable runs. Simulation ground truth uses the final `/odom` pose inside the readiness-true window and distance to configured goal-source positions. The two results are never collapsed into one implicit success flag.

## Cleanup and failure policy

Each run starts a fresh Gazebo target through `record_run`; no Gazebo reset service is reused between cases.

Before a suite starts, capture baseline ROS nodes and matching experiment-process identities. After every run:

1. Require the Phase 05 metadata to report clean target and bag shutdown.
2. Require `completeness.json` to exist and preserve its pass/fail result.
3. Compare the post-run ROS graph with the captured baseline.
4. Check for new surviving processes belonging to the exact launched process tree.
5. Record cleanup evidence in `scenario_result.yaml`.
6. Continue after an ordinary failed run only when cleanup passed.
7. Stop the suite immediately on cleanup failure to prevent cross-run contamination.

The runner will not broadly kill by process name. On its own wall timeout it will signal the exact `record_run` process, allow Phase 05 ordered shutdown, then escalate only against the exact process session it created if the grace period expires.

All failed run directories remain in place. Missing run creation, runner infrastructure failure, recorder failure, completeness failure, controller failure, ground-truth failure, timeout, and unsupported dimensions remain distinct statuses.

## Backward compatibility and migration

- Direct `gazebo.launch.xml` users retain visible, unseeded, `legacy` defaults.
- `algorithm_profile=legacy`, existing topics, message layouts, cost sign and units, source arguments, controller saturation, and CSV collection remain unchanged.
- Existing robust `record_run` behavior and the accepted Phase 05 artifact must continue to validate.
- Legacy simulation becomes an additive accepted metadata profile only when it satisfies the same Phase 05 manifest and completeness gates.
- No alternative manifest, reduced topic requirement, or relaxed shutdown rule will be introduced for legacy runs.
- The runner always forces `recording_ready_required=True`, `enable_observability=True`, `use_pde_extensions=True`, `show_cost_surface_plot=False`, and `live_plot_mode=None`.
- No physical mode is exposed by `run_scenario`.
- No existing scenario or historical Heavy-Ball file is migrated.

## Implementation sequence

1. Re-run the Phase 06 implement validator, inspect Git status/diff, and stop if planned files gained overlapping user changes.
2. Implement the pure schema validator and deterministic expansion first, including unsupported-case records and ordered level Cartesian products.
3. Add `run_scenario --dry-run`, metadata generation, exact argv construction, unique IDs, and deterministic case ordering without launching ROS.
4. Extend `empty_world.launch.py` and `gazebo.launch.xml` with visible/headless and optional seed arguments, preserving all direct-launch defaults.
5. Apply the bounded legacy-recording correction to the existing recorder and validator. Do not change the manifest or completeness thresholds.
6. Compose serial runtime execution through `record_run`; add scoped wall-timeout handling, run-directory discovery by exact run ID, and cleanup verification.
7. Add minimal bag outcome extraction for state/events, final readiness-window odometry, and saturation flags. Reuse `completeness.json` rather than reproducing validation.
8. Add per-run and suite summaries, then install the console entry point and checked-in scenarios.
9. Run dry-run, focused, runtime, global-baseline, syntax, diff, and accepted-bag regression checks.
10. Record any Level B correction or Level C scenario failure in `phase_06_handoff.md`, including preserved artifact paths.

## Tests and acceptance criteria

Focused tests:

- `test_scenario_schema.py`
  - required keys, unknown-key rejection, finite/type/range checks;
  - source count 1–5;
  - bounds and start validation;
  - explicit source level mapping;
  - exactly 25 ordered two-source combinations for a test 1–5 map;
  - stable profile/start/level/seed expansion order;
  - deterministic case keys;
  - supported/unsupported disturbance classification;
  - `max_parallel_runs != 1` rejection;
  - ablation and success-predicate validation.
- `test_scenario_runner.py`
  - exact `record_run` and `gazebo.launch.xml` argv;
  - no shell evaluation;
  - generated metadata matches launch sources, start, seed, bounds, and profile;
  - unique safe run IDs;
  - robust and legacy command generation;
  - per-run result classification;
  - controller versus ground-truth separation;
  - cleanup comparison and stop-on-cleanup-failure;
  - failed-run retention;
  - summary output and dry-run behavior.
- `test_experiment_recording.py`
  - robust behavior retained;
  - legacy simulation accepted;
  - unknown profile and invalid physical combinations rejected;
  - validator profile gate does not weaken any other check.

Commands:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 06 implement

source /opt/ros/humble/setup.bash
cd /home/mattb/dsim-lab/ros2_ws
colcon build \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash

python3 -m pytest -q \
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

Dry-run checks:

```bash
ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase06_smoke.yaml \
  --operator codex-automated-test \
  --dry-run

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase06_catalog.yaml \
  --operator codex-automated-test \
  --dry-run
```

Launch checks:

```bash
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args

ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
  gazebo_gui:=False \
  gazebo_use_random_seed:=True \
  gazebo_random_seed:=6001 \
  algorithm_profile:=robust_gaussian_v1 \
  use_pde_extensions:=True \
  enable_observability:=True \
  recording_ready_required:=True \
  --show-args
```

Runtime acceptance:

- Run one short headless robust smoke and one short headless legacy smoke through `run_scenario`.
- Both must create Phase 05 run directories with unique IDs.
- Both must preserve all required Phase 05 artifacts.
- `completeness.json` must pass for both; if the legacy graph cannot satisfy the existing manifest without weakening it, stop and mark recorded legacy regression unsupported.
- Each run must have `scenario_result.yaml`.
- The suite summary must distinguish controller and ground-truth results.
- Post-run ROS graph and process checks must match the baseline.
- Revalidate the accepted Phase 05 robust bag and require it to remain passing.

Repository-standard reporting:

```bash
colcon test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose

cd /home/mattb/dsim-lab
python3 -m compileall -q \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner \
  ros2_ws/src/ros_esc/ros_esc/experiment_recording
python3 -c \
  'import xml.etree.ElementTree as ET; ET.parse("ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml")'
git diff --check
git status --short --branch
```

The prior authoritative focused baseline is `113 passed, 1 skipped`; the global baseline is `999 tests, 0 errors, 875 inherited failures, 2 skipped`. Phase 06 must report new focused results separately and must not describe the inherited lint baseline as a new regression.

## Risks and stop conditions

Level A — stop before further edits if:

- an overlapping user change appears in a planned file and cannot be preserved;
- legacy recording requires a second manifest, recorder, launch graph, or weakened completeness gate;
- source sign, units, profile semantics, or final `/cmd_vel` ownership would change;
- a new algorithm, physical path, Heavy-Ball path, or simulation-only controller fork becomes necessary;
- cleanup cannot be scoped to processes created by the runner;
- a required dependency is unavailable.

Level B — document and continue only for a bounded, tested correction such as:

- launch substitution or runtime parameter typing;
- headless/seed argument propagation;
- Gazebo interrupt exit attribution;
- recorder subprocess timeout sequencing;
- graph-settling or process-baseline timing;
- profile-aware validation that retains every existing completeness requirement.

Level C — retain evidence and report failure without weakening gates when:

- an executable scenario does not produce its intended state/event sequence;
- controller goal and ground truth disagree;
- fill, escape, assistance, merge, or recenter expectations fail;
- completeness, final-zero, timeout, or cleanup fails;
- a robustness threshold is missed.

Unsupported dimensions must be summarized explicitly and must not be converted into zero-valued fake measurements.

## Implementation-time verification

Before editing or runtime execution, verify:

- the branch, HEAD, dirty files, prior handoffs, and saved Phase 06 plan;
- `gazebo --help` and `gzserver --help` still expose deterministic seed support;
- current `record_run`, `validate_run`, manifest, setup entry points, and launch arguments match this plan;
- a legacy graph with PDE extensions and observability publishes every required manifest topic with singleton ownership;
- legacy controller recording interlock and final-zero behavior remain valid without a supervisor process;
- the accepted Phase 05 run still passes before and after validator changes;
- `Uniform` noise repeats exactly for identical seed/configuration;
- no deterministic Gaussian or delay injection has appeared since planning;
- headless Gazebo starts without a GUI dependency and shuts down through the Phase 05 owner;
- run-directory lookup by exact run ID is unambiguous across a UTC date boundary;
- the checked-in catalog’s empirical geometries are clearly labeled unverified;
- no physical command or hardware path is invoked.
