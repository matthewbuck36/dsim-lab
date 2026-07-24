# Phase 08 Plan — Robustness Validation and Parameter Freeze

Target save path: `docs/codex/gesc_gaussian/plans/phase_08_plan.md`

## Objective and scope

Validate `robust_gaussian_v1` over a fixed, documented simulation envelope; tune only on a bounded training subset; reserve holdout cases; freeze one parameter set; execute three unchanged full-suite passes; calculate every gate in `06_TEST_MATRIX_AND_ACCEPTANCE_GATES.md`; preserve all failed evidence; and create a simulation-ready tag only if every gate passes.

In scope:

- A prerequisite Phase 07.5 subphase adding deterministic simulation disturbances and collision evidence.
- Existing Phase 06 scenario orchestration, Phase 05 recording/validation, and Phase 07 analysis reuse.
- Nine training candidates, one frozen parameter set, a 12-run holdout, and three complete validation passes.
- Structured success or Level C failure reporting.

Out of scope:

- Algorithm redesign after the final parameter freeze.
- Heavy-Ball ESC.
- Physical hardware, Vicon, physical calibration, or Phase 09 work.
- Changing cost sign, units, canonical algorithm topics, controller ownership, or legacy defaults.

The required preflight passed on branch `feature/gesc-gaussian-robustness-v1` at clean HEAD `80d5c6a`:

```text
Phase 08 plan context is complete.
```

## Repository findings

- `run_scenario` already owns deterministic serial simulation orchestration and composes the sole `record_run`, `validate_run`, and `gazebo.launch.xml` owners. It must be extended, not replaced.
- `analyze_run` and `summarize_matrix` already deserialize the sqlite3 bags and compute validity-marked success, escape, orbit, revisit, fill, saturation, timeout, and failsafe metrics.
- Phase 06 provides 26 executable catalog runs and seven explicit unsupported records. The unsupported required dimensions are deterministic Gaussian noise, sensor/pose delay, and collision truth.
- The scenario schema already supports ordered level expansion, five starts, three seeds, and allowlisted launch overrides. It lacks an authoritative level map.
- Phase 07 currently marks collision unavailable. The active world contains only sun and ground; light collisions are disabled.
- Humble provides `gazebo_msgs/msg/ContactsState` and `/opt/ros/humble/lib/libgazebo_ros_bumper.so`, so collision evidence can be added without a new message or package.
- Existing functional baseline: `153 passed, 2 skipped`. Global baseline: `1037 tests, 0 errors, 872 inherited lint failures, 3 skipped`.
- The accepted simulation level map will be versioned as simulator-relative inputs, not physical calibration:

```yaml
level_map:
  "1": 450.0
  "2": 800.0
  "3": 1200.0
  "4": 1800.0
  "5": 2500.0
```

## Existing implementation to reuse or extend

- Extend `scenario_schema.py` and `run_scenario.py` for a backward-compatible schema-v2 validation environment, delay controls, contact recording, and frozen-parameter application.
- Continue using `record_run.py`, `validate_run.py`, their sqlite3 layout, readiness interlock, manifest, final-zero checks, cleanup, and run IDs. Do not create another recorder or completeness validator.
- Extend `gesc_gaussian_bag_analysis.py` to calculate collision and observed-delay metrics. Do not create a second bag reader or matrix analyzer.
- Use the existing Gaussian, supervisor, modified-cost, filter, controller, and launch owners unchanged during final validation.
- Correct the existing seeded-Gaussian RNG implementation in its current noise owner.
- Add one simulation-only disturbance relay node because no existing node owns delayed test-input publication. It will not implement control or physical behavior.
- Add opt-in Gazebo contact sensors to the existing robot description and a validation world with four physical walls.

## Files to modify

### Phase 07.5 prerequisite

- `DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh`
  - Require `handoffs/phase_07_5_handoff.md` before the post-prerequisite Phase 08 validation run.
- `ros2_ws/src/ros_esc/package.xml`
  - Declare the installed `gazebo_msgs` runtime dependency used by collision analysis.
- `ros2_ws/src/ros_esc/setup.py`
  - Install the new validation scenarios and expose the disturbance and validation console entry points.
- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/noise_objects.py`
  - Make configured Gaussian `seed_num` seed the NumPy generator actually used for sampling; preserve unseeded legacy behavior.
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py`
  - Continue accepting schema version 1 unchanged; add schema version 2 validation-world, disturbance, and frozen-profile fields.
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py`
  - Pass validation-world/contact/delay arguments through the existing launch and include them in deterministic case identity and metadata.
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/topic_manifest.yaml`
  - Record simulation contacts and original/delayed test inputs as optional simulation-only topics; Phase 08 applies conditional requirements.
- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py`
  - Produce valid collision and observed pose/sensor delay metrics when the validation topics exist.
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
  - Add default-off validation arguments, launch the delay relay only when requested, and route algorithm consumers to delayed topics.
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/robot_description.launch.py`
  - Forward the opt-in contact-sensor xacro argument.
- `ros2_ws/src/turtlebot3_rotating_sensor/urdf/turtlebot3_rotating_sensor.urdf`
  - Name the existing base/rotating collisions and add conditional Gazebo contact sensors without changing default robot behavior.
- Existing scenario, recording, analysis, observability, and launch-contract tests where required to cover the additive interfaces.
- `docs/codex/gesc_gaussian/topic_dictionary.md`
- `docs/codex/gesc_gaussian/recording_runs.md`
- `docs/codex/gesc_gaussian/test_commands.md`

### Phase 08 validation

- `ros2_ws/src/ros_esc/setup.py`
  - Register `validate_robustness`.
- `docs/codex/gesc_gaussian/test_commands.md`
  - Record exact smoke, sweep, holdout, pass, analysis, gate, and tag commands.
- `docs/codex/gesc_gaussian/topic_dictionary.md`
  - Document the test-only topics and offline validation command.

No controller, supervisor, Gaussian-design, message-definition, Heavy-Ball, or physical source file is modified for tuning.

## Files to create

### Phase 07.5 prerequisite

- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/simulation_disturbance_node.py`
  - Simulation-only delayed-message relay; the only new ROS node.
- `ros2_ws/src/turtlebot3_rotating_sensor/worlds/gesc_gaussian_validation.world`
  - Existing empty world plus four static walls at the configured `[-2,2] × [-2,2] m` envelope.
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_validation_support.yaml`
  - Negative-contact, positive-contact, seeded-Gaussian, sensor-delay, and pose-delay runtime probes.
- `ros2_ws/src/ros_esc/test/test_simulation_disturbances.py`
- `docs/codex/gesc_gaussian/handoffs/phase_07_5_handoff.md`

### Phase 08

- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/phase08_validation.py`
  - Sequences the existing runner and analyzer, enforces stage order and freeze hashes, calculates gates, and writes reports.
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_parameter_candidates.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_training.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_holdout.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_full_matrix.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_frozen_parameters.yaml`
  - Generated after selection and committed before holdout/final execution.
- `ros2_ws/src/ros_esc/test/test_phase08_validation.py`
- `docs/codex/gesc_gaussian/validation/phase_08_parameter_selection.json`
- `docs/codex/gesc_gaussian/validation/phase_08_run_manifest.json`
- `docs/codex/gesc_gaussian/validation/phase_08_gate_results.json`
- `docs/codex/gesc_gaussian/validation/phase_08_validation_report.md`
- `docs/codex/gesc_gaussian/validation/phase_08_failure_report.md`, only if any gate fails.
- `docs/codex/gesc_gaussian/handoffs/phase_08_handoff.md`

The implementation exceeds ten files because simulation disturbance injection, physical collision evidence, existing recording/analysis integration, scenario definitions, validation orchestration, tests, and durable reports have separate owners. Split it into Phase 07.5 support, Phase 08 harness, parameter freeze, and final evidence commits.

## Public interfaces and parameters

No new custom message, service, action, algorithm topic, interface package, or controller dependency is introduced.

Simulation-only topics, all recorded only when present:

| Topic | Type | Owner |
|---|---|---|
| `/gesc_gaussian/simulation/raw_cost_delayed` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | disturbance relay |
| `/gesc_gaussian/simulation/source_cost_delayed` | `ros_esc_interfaces/msg/CostBreakdown` | disturbance relay |
| `/gesc_gaussian/simulation/pose_delayed` | `nav_msgs/msg/Odometry` | disturbance relay |
| `/gesc_gaussian/simulation/contacts` | `gazebo_msgs/msg/ContactsState` | opt-in Gazebo contact plugins |

Additive launch arguments:

```text
algorithm_raw_cost_topic=/turtlebot3/cost_value_chatter
algorithm_source_cost_topic=/gesc_gaussian/source_cost
algorithm_pose_topic=/odom
simulation_disturbance_enabled=False
simulation_sensor_delay_sec=0.0
simulation_pose_delay_sec=0.0
simulation_disturbance_publish_rate_hz=100.0
simulation_raw_cost_delayed_topic=/gesc_gaussian/simulation/raw_cost_delayed
simulation_source_cost_delayed_topic=/gesc_gaussian/simulation/source_cost_delayed
simulation_pose_delayed_topic=/gesc_gaussian/simulation/pose_delayed
simulation_contacts_enabled=False
simulation_contacts_topic=/gesc_gaussian/simulation/contacts
```

All defaults preserve the current launch graph. Delay messages retain original ROS/header/source timestamps and are released according to ROS simulation time. The validation analyzer measures bag-receipt delay by matching those retained stamps.

Offline command:

```text
ros2 run ros_esc validate_robustness <subcommand>
  --operator OPERATOR
  --evidence-root PATH
```

Subcommands are `sweep`, `freeze`, `holdout`, `full-pass`, and `report`. `full-pass` requires `--pass-index 1|2|3`. The command refuses out-of-order stages, an unclean frozen checkout, changed scenario/frozen-file hashes, or a different Git commit after freeze.

## Parameter sweep and selection

Only four factor groups are tuned. All other algorithm values remain the defaults fixed by the freeze commit.

| Candidate | Covariance scale | Depth scale | Exit sigma | Stall window | Minimum radial progress |
|---|---:|---:|---:|---:|---:|
| `C0` | 2.5 | 1.5 | 2.50 | 3.0 s | 0.05 m |
| `C1` | 2.0 | 1.2 | 2.25 | 4.0 s | 0.03 m |
| `C2` | 2.0 | 1.2 | 2.75 | 2.0 s | 0.08 m |
| `C3` | 2.0 | 1.8 | 2.25 | 2.0 s | 0.08 m |
| `C4` | 2.0 | 1.8 | 2.75 | 4.0 s | 0.03 m |
| `C5` | 3.0 | 1.2 | 2.25 | 2.0 s | 0.08 m |
| `C6` | 3.0 | 1.2 | 2.75 | 4.0 s | 0.03 m |
| `C7` | 3.0 | 1.8 | 2.25 | 4.0 s | 0.03 m |
| `C8` | 3.0 | 1.8 | 2.75 | 2.0 s | 0.08 m |

The mapped launch arguments are:

```text
gaussian_fill_covariance_scale
gaussian_fill_amplitude_depth_scale
gaussian_fill_exit_sigma
stall_window_sec
minimum_radial_progress_m
```

Each candidate runs the same nine training runs: three two-source starts, pure-repulsion escape, stalled assisted escape, fill merge, recenter/resume, one three-source case, and one seeded-Uniform-noise case. Total training execution: 81 recorded runs.

A candidate is eligible only if every run has complete recording/analysis, clean process/graph cleanup, valid collision evidence with no collision, and bounded completion. Among eligible candidates select lexicographically:

1. Highest end-to-end success, defined as both controller goal and simulation ground truth.
2. Highest local-escape success.
3. Highest minimum family goal-success rate.
4. Lowest 95th-percentile then median escape time.
5. Lowest median orbit count.
6. Lowest revisit rate.
7. Lowest median convergence time, path length, then candidate ID.

If no candidate is eligible, stop before freeze, classify the outcome as Level C, preserve all runs, write the failure report, and do not run holdout/final passes.

## Holdout and final matrix

The 12 holdout runs are not exposed during selection:

- Eight two-source runs from two unseen intensity tuples, two unseen starts/headings, and two unseen seeds.
- One four-source close/overlap run.
- One corner-boundary run.
- One seeded Gaussian-noise run.
- One combined sensor/pose-delay run.

Holdout is executed once after the freeze commit. Its outcome is reported without retuning. Behavioral failure does not change parameters or code and does not suppress the final evidence collection; only cleanup contamination, unreadable artifacts, invalid collision evidence, or loss of the frozen checkout stops execution.

Each complete final pass contains 519 recorded scenarios:

| Group | Runs |
|---|---:|
| Existing robust/legacy recorded smoke | 2 |
| Ordered two-source levels: 25 combinations × 5 starts × 3 seeds | 375 |
| Three- and four-source: 2 cases × 3 starts × 3 seeds | 18 |
| Overlap and close-minimum: 2 cases × 3 starts × 3 seeds | 18 |
| Wall and corner boundary: 2 cases × 2 starts × 3 seeds | 12 |
| Uniform, Gaussian, sensor delay, pose delay, combined delay | 27 |
| Linear/angular saturation cases | 18 |
| Pure escape, assisted escape, merge, recenter | 12 |
| Multiple-prior-fill/revisit case | 3 |
| Legacy ordered-level regression: 25 combinations × 1 start × 1 seed | 25 |
| Gaussian, affine, and recenter ablation diagnostics | 9 |

The required robust acceptance denominator is 483 runs per pass. Smoke, legacy comparator, and ablation runs are reported separately. Three passes execute 1,557 scenarios with identical code, parameter file, scenario hashes, and deterministic seeds.

## Acceptance calculation

Calculate every gate separately for each pass and over the pooled three-pass evidence. Every pass must pass; pooled success cannot hide a failed pass.

1. Functional unit/integration tests all pass; repository-wide lint does not worsen from the documented inherited baseline.
2. Every required run passes Phase 05 completeness and Phase 07 analysis completeness.
3. Collision evidence is valid for every required run and contains zero non-ground contacts.
4. Local-escape success is successful escape attempts divided by all valid observed escape attempts and is at least 95%; designated escape cases must actually exercise their declared state/event coverage.
5. End-to-end goal success is runs with both controller success and simulation-ground-truth success divided by all 483 required robust runs and is at least 90%.
6. Every required family has at least 80% end-to-end goal success.
7. Median successful escape time is at most 20 seconds.
8. 95th-percentile successful escape time is at most 45 seconds.
9. Median valid post-fill orbit count is at most 1.5.
10. Every run terminates normally or through a recorded safe algorithm timeout; no wall timeout, orphan, indefinite circle, or missing terminal evidence is permitted.
11. Revisit rate is successful goal runs with at least one active fill and `revisit_count > 0`, divided by successful goal runs with valid fill/revisit evidence; it must be below 5%.
12. Passes 1, 2, and 3 all pass without source, parameter, scenario, or freeze-hash changes.
13. Only after gates 1–12 pass, create the annotated tag.

Unsupported or invalid metric status fails the corresponding gate; it is never converted to zero or excluded silently.

## Backward compatibility and migration

- `algorithm_profile=legacy`, direct visible Gazebo, unseeded execution, canonical topics, and delay/contact controls remain unchanged by default.
- Scenario-schema version 1 files retain their current parsing, expansion, deterministic identity, and behavior. Phase 08 uses schema version 2.
- The relay and contact plugins are simulation-only and default off.
- Canonical topics remain the recorded source of algorithm behavior; validation-only original/delayed topics are additional evidence.
- No frozen value becomes a global launch default. `phase08_frozen_parameters.yaml` is applied only by the Phase 08 validation command.
- The freeze consists of the exact Git commit, the frozen override file, scenario hashes, launch/config hashes, and resolved parameter snapshots.
- Physical integration receives no inferred topic or calibration migration.

## Implementation sequence

1. Save this plan verbatim and run `validate_phase_context.sh 08 implement`.
2. Implement Phase 07.5 disturbance/contact support in existing owners, add its tests and runtime probes, write `phase_07_5_handoff.md`, and commit:
   `phase 07.5: add deterministic validation disturbances and collision evidence`.
3. Rerun the updated Phase 08 context validator. Stop if the prerequisite handoff or live support probes are incomplete.
4. Implement the Phase 08 orchestration, candidate and scenario files, gate evaluator, tests, and documentation. Commit:
   `phase 08a: add robustness validation harness and suites`.
5. Build and run the retained functional suite, new tests, schema dry-runs, and recorded robust/legacy smoke.
6. Execute all 81 training runs, analyze every run, and generate `phase_08_parameter_selection.json`.
7. Select the winner by the frozen criterion; create `phase08_frozen_parameters.yaml`, record source/config/scenario hashes, and commit:
   `phase 08b: freeze robust Gaussian simulation parameters`.
8. Require a clean worktree at that freeze commit. Execute holdout once without retuning.
9. Execute full passes 1, 2, and 3 consecutively. Continue after ordinary Level C behavioral failures; stop immediately for cleanup contamination or corrupted evidence.
10. Generate the run manifest, per-pass/pooled gate JSON, Markdown report, and conditional failure report.
11. If any gate fails, do not create a tag. Record the smallest evidence-supported next engineering phase.
12. If gates 1–12 all pass and the tag does not already exist, tag the tested freeze commit without force or rewrite:

```bash
git tag -a gesc-gaussian-simulation-ready-v1 <freeze-commit> \
  -m "GESC Gaussian simulation-ready v1: Phase 08 gates passed"
```

Do not push the tag automatically.
13. Write `phase_08_handoff.md`, update durable test evidence, and commit:
   `phase 08: validate and freeze robust Gaussian profile`.

## Tests and commands

Core validation:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 implement

source /opt/ros/humble/setup.bash
cd ros2_ws
colcon --log-base /tmp/dsim_phase08_build build \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
```

Focused functional suite:

```bash
python3 -m pytest -q -rs \
  src/ros_esc/test/test_simulation_disturbances.py \
  src/ros_esc/test/test_phase08_validation.py \
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

Scenario dry-runs and prerequisite runtime:

```bash
ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_validation_support.yaml \
  --operator phase08 --dry-run --summary-output /tmp/phase08_support_dry.yaml

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_full_matrix.yaml \
  --operator phase08 --dry-run --summary-output /tmp/phase08_full_dry.yaml
```

The second dry-run must resolve exactly 519 runs and no unsupported Phase 08 record.

Execution:

```bash
ros2 run ros_esc validate_robustness sweep \
  --operator phase08 --evidence-root ~/Experiments/GESC-Gaussian/runs/phase08

ros2 run ros_esc validate_robustness freeze \
  --operator phase08 --evidence-root ~/Experiments/GESC-Gaussian/runs/phase08

ros2 run ros_esc validate_robustness holdout \
  --operator phase08 --evidence-root ~/Experiments/GESC-Gaussian/runs/phase08

for pass_index in 1 2 3; do
  ros2 run ros_esc validate_robustness full-pass \
    --pass-index "$pass_index" \
    --operator phase08 \
    --evidence-root ~/Experiments/GESC-Gaussian/runs/phase08
done

ros2 run ros_esc validate_robustness report \
  --operator phase08 \
  --evidence-root ~/Experiments/GESC-Gaussian/runs/phase08
```

Final checks:

```bash
colcon --log-base /tmp/dsim_phase08_test test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --test-result-base ros2_ws/build --all --verbose

python3 -m compileall -q \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner \
  ros2_ws/src/ros_esc/ros_esc/plotting_scripts

ament_flake8 <all Phase 07.5/08 Python files>
ament_pep257 <all Phase 07.5/08 Python files>
git diff --check
git status --short --branch
```

Report exact focused/global/skipped totals and compare global failures against the `1037/872/3-skipped` Phase 07 baseline. Retained environment-gated tests must either be run explicitly or listed as unexecuted with reasons.

## Risks and stop conditions

- Level A: stop if the saved plan/preflight is missing, the working tree has overlapping unrelated edits, validation support requires a second recorder/controller/algorithm fork, delay routing cannot preserve canonical semantics, installed contact support is unavailable, cost sign/units would change, or physical hardware would be required.
- Stop before tuning if contact sensors cannot demonstrate both an empty-state no-collision run and an intentional wall-contact positive control.
- Stop before tuning if measured sensor/pose delays do not match configured values within one 100 Hz relay period plus scheduler tolerance.
- Stop immediately on failed cleanup, orphaned processes/nodes, duplicate canonical publishers, corrupted bags, missing frozen hashes, changed freeze commit, or insufficient disk capacity.
- A bounded local runtime correction is Level B only when it preserves architecture and gates; record its assumption, evidence, files, and tests.
- Performance, holdout, or final gate misses are Level C. Finish the declared safe evidence collection, preserve every run, generate the structured failure report, and do not retune or weaken thresholds.
- Runtime is substantial: 81 training runs, 12 holdout runs, and 1,557 final-pass runs, with recorder parameter snapshots and raw sqlite3 storage. Verify storage and uninterrupted execution capacity before starting each stage.

## Implementation-time verification

- Confirm the branch, clean status, HEAD, all prior handoffs, and saved Phase 08 plan before edits.
- Reconfirm `gazebo_msgs/msg/ContactsState` and `libgazebo_ros_bumper.so`.
- Verify the actual xacro collision names and that ground contacts are excluded without hiding wall contacts.
- Verify every algorithm consumer uses `algorithm_pose_topic`, `algorithm_source_cost_topic`, and `algorithm_raw_cost_topic` when delay injection is enabled.
- Verify schema-version-1 case keys remain unchanged and schema-version-2 keys include world, disturbance, frozen parameters, and seed.
- Verify all validation topics are recorded and original plus delayed stamps can be paired.
- Verify Phase 07 analysis remains read-only and preserves raw bag hashes.
- Verify the dry-run counts: 81 training runs, 12 holdout runs, and 519 runs per final pass.
- Verify `phase08_frozen_parameters.yaml` and the freeze commit remain byte-identical during holdout and all three passes.
- Verify the proposed tag name is absent before creation; never overwrite an existing tag.
- Treat current code, runtime graph, tests, and completed handoffs as authoritative if any older audit or memory statement differs.
