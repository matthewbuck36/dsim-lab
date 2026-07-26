# Phase 08 Plan — Robustness Validation and Parameter Freeze

Target save path: `docs/codex/gesc_gaussian/plans/phase_08_plan.md`

## Amendment 3 — Phase 08.1 diagnostic recovery and future v3

Approved on 2026-07-25 after the retained v2 activation evidence was diagnosed
against the current code, package source material, all package files, and all
`docs/` artifacts.

Phase 08 v2 remains a closed failed experiment. Its ten activation attempts,
manifest, reports, hashes, and 120-run contract are immutable historical
evidence. They must not be resumed, overwritten, relabeled, or counted in a
future experiment.

The v2 failure closes only that declared experiment version. It does not forbid
offline diagnosis, bounded engineering corrections, targeted simulation
probes, or a new versioned experiment. Those activities are governed by
`docs/codex/gesc_gaussian/plans/phase_08_1_plan.md`.

The exact 120-run design below is therefore historical v2 scope, not a
permanent development budget. A future v3 contract must separate:

- versioned diagnostic/development runs, which are retained and reported but
  never enter the acceptance denominator;
- a fixed, selection-blind holdout and unique validation denominator declared
  before formal freeze;
- reproducibility repeats reported separately from unique-case success.

No v3 holdout, fixed-profile acceptance run, simulation-ready tag, or physical
motion is authorized by this amendment. A machine-readable v3 acceptance
contract and fresh evidence root must be reviewed and sealed before those
stages.

## Amendment 1 — staged validation v2

Approved on 2026-07-25 after Phase 08 v1 exposed an unreachable supervisor
activation contract, an unsuitable instantaneous goal-score dwell, zero escape
attempts in the 81-run sweep, 0/12 controller holdout success, and a safely
stopped first full pass.

The former 519-run pass repeated three times is retired for all future
acceptance work. Its code, frozen C8 profile, parameter-selection file, partial
run directories, and observed failure results are immutable historical v1
evidence. They must not be resumed, overwritten, relabeled, or counted toward
v2 acceptance.

The amended empirical budget is exactly 120 declared runs:

```text
10 activation
30 tuning (3 candidates x the same 10 cases)
20 new hidden holdout
50 additional unique validation
10 reproducibility repeats
---
120 total
```

The 20 holdouts plus 50 additional unique cases form a 70-run acceptance
denominator. The ten repeats test reproducibility and do not inflate the
denominator. Failed infrastructure attempts are retained as evidence but do not
replace a declared run.

## Amendment 2 — compaction-safe execution

Phase 08 v2 must maintain
`docs/codex/gesc_gaussian/status/phase_08_status.md` throughout implementation.
After every verified milestone or empirical stage, record completed work,
decisions and rationale, exact tests/results, artifact paths, current Git state,
remaining work, and actions not to repeat; then run `checkpoint_phase.sh 08`.

After any context compaction, interruption, or model switch, reread
`AGENTS.md`, this plan, and the live status; inspect Git status and the relevant
diff; identify the next incomplete acceptance criterion; and continue only from
that reconstructed repository state. Never rerun an expensive v1 or v2 batch
merely to recover conversational context.

## Objective and scope

Repair and prove the detector-to-supervisor activation and rotation-aware goal
verification contracts; validate `robust_gaussian_v1` over a fixed,
predeclared stratified simulation sample; tune only on a bounded training
subset; reserve new holdout cases; freeze one parameter set; execute one unique
validation sample plus a targeted reproducibility subset; calculate every gate
in `06_TEST_MATRIX_AND_ACCEPTANCE_GATES.md`; preserve all failed evidence; and
create a simulation-ready tag only if every amended gate passes.

In scope:

- A prerequisite Phase 07.5 subphase adding deterministic simulation disturbances and collision evidence.
- Existing Phase 06 scenario orchestration, Phase 05 recording/validation, and Phase 07 analysis reuse.
- Ten activation proofs, three tuning candidates, one frozen parameter set, 20
  new hidden holdouts, 50 additional unique validation runs, and ten targeted
  reproducibility repeats.
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

That preflight and HEAD are historical v1 planning evidence. V2 implementation
must rerun the live context validator and record its actual branch, HEAD, and
worktree state before editing.

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
  - Keep `validate_robustness` as the sole validation command and extend it for
    v2 activation, tuning, holdout, unique validation, reproducibility, and
    partial/final reporting.
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/phase08_validation.py`
  - Preserve v1 evidence compatibility, refuse to treat v1 `full-pass` results
    as v2 acceptance, enforce the 120-run stage order and early-stop gates, and
    calculate confidence intervals without adding a second validator.
- `docs/codex/gesc_gaussian/test_commands.md`
  - Preserve executed v1 commands as history and record exact v2 activation,
    tuning, holdout, validation, reproducibility, analysis, gate, and tag
    commands in a new section.
- `docs/codex/gesc_gaussian/topic_dictionary.md`
  - Document the retired v1 interface and the implemented v2 stage contract
    without describing planned commands as already available.
- `docs/codex/gesc_gaussian/status/phase_08_status.md`
  - Maintain verified milestone, decision, validation, artifact, Git, blocker,
    do-not-repeat, and next-criterion state throughout v2 execution.

No controller, supervisor, Gaussian-design, message-definition, Heavy-Ball, or physical source file is modified for tuning.

## Files to create or retain

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

Existing v1 scenario inputs to retain byte-for-byte:

- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_parameter_candidates.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_training.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_holdout.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_full_matrix.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_frozen_parameters.yaml`

New v2 scenario inputs and tests:

- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_activation.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_training.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_holdout.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_validation.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_reproducibility.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_frozen_parameters.yaml`
  - Generate the v2 frozen file after selection and commit it before holdout.
- `ros2_ws/src/ros_esc/test/test_phase08_validation.py`

Existing v1 durable evidence to retain:

- `docs/codex/gesc_gaussian/validation/phase_08_parameter_selection.json`
  - Retain as the historical v1 selection record; do not regenerate it.

New closeout and v2 durable evidence:

- `docs/codex/gesc_gaussian/validation/phase_08_v1_failure_closeout.md`
  - Inventory and summarize the immutable failed/incomplete v1 evidence before
    v2 implementation; do not mutate the v1 run root.
- `docs/codex/gesc_gaussian/validation/phase_08_v2_parameter_selection.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_run_manifest.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_gate_results.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_validation_report.md`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_failure_report.md`, only if any
  amended gate fails.
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

The currently installed v1 subcommands (`sweep`, `freeze`, `holdout`,
`full-pass`, and `report`) are retained only to read and report historical v1
evidence. They are not an acceptance path.

V2 extends the same command owner with `activation`, `sweep`, `freeze`,
`holdout`, `validation`, `reproducibility`, and `report`. Every v2 invocation
requires workflow schema version 2 and a new evidence root such as
`~/Experiments/GESC-Gaussian/runs/phase08_v2`. The command refuses mixed v1/v2
evidence, out-of-order stages, an unclean frozen checkout, changed
scenario/frozen-file hashes, or a different Git commit after freeze.

## Parameter sweep and selection

Only the five listed values are tuned. All other algorithm values remain the
defaults fixed by the freeze commit.

| Candidate | Covariance scale | Depth scale | Exit sigma | Stall window | Minimum radial progress |
|---|---:|---:|---:|---:|---:|
| `V2-C0` | 2.5 | 1.5 | 2.50 | 3.0 s | 0.05 m |
| `V2-C1` | 2.0 | 1.2 | 2.25 | 4.0 s | 0.03 m |
| `V2-C2` | 3.0 | 1.8 | 2.75 | 2.0 s | 0.08 m |

The mapped launch arguments are:

```text
gaussian_fill_covariance_scale
gaussian_fill_amplitude_depth_scale
gaussian_fill_exit_sigma
stall_window_sec
minimum_radial_progress_m
```

Before tuning, ten activation runs must prove the corrected detector-supervisor
and rotation-aware goal contracts. The fixed set covers easy one-source goals
at low, medium, and high level; fill creation; pure escape; stalled assist;
merge; recenter/resume; boundary/contact-negative behavior; and one
noise/delay case. The declared lifecycle state/event must be observed in every
designated case. Zero fills, zero escape attempts, or an unobserved required
state/event stops the workflow before tuning.

Each candidate then runs the same ten training cases: three two-source starts,
pure-repulsion escape, stalled assisted escape, fill merge, recenter/resume,
one three-source case, one seeded-noise case, and one delay case. Total tuning
execution is 30 recorded runs. The numerical values reused by `V2-C2` do not
make the historical v1 `C8` profile a v2 winner; selection starts again from
the corrected activation contract and new evidence.

A candidate is eligible only if every run has complete recording/analysis,
clean process/graph cleanup, valid collision evidence with no collision,
bounded completion, and its designated lifecycle coverage. Among eligible
candidates select lexicographically:

1. Highest end-to-end success, defined as both controller goal and simulation ground truth.
2. Highest local-escape success.
3. Highest minimum family goal-success rate.
4. Lowest 95th-percentile then median escape time.
5. Lowest median orbit count.
6. Lowest revisit rate.
7. Lowest median convergence time, path length, then candidate ID.

If no candidate is eligible, or if all candidates again have zero fill/escape
activation or zero end-to-end success, stop before freeze, classify the
outcome as Level C, preserve all runs, write the failure report, and do not run
holdout or validation.

## Holdout, unique validation, and reproducibility

The 20 v2 holdout runs are newly generated, sealed by manifest hash before
tuning, and unopened by the validation command until after the freeze.
"Hidden" is a selection-blind workflow rule, not a security boundary: their
identities and outcomes cannot be used for candidate selection. The exposed v1
holdout cases and results are excluded. The v2 set is allocated across ordered
two-source levels, multi-source/close/overlap, wall/corner, noise/delay,
saturation/timeout/safe-failure, and lifecycle
escape/assist/merge/recenter/revisit families.

Holdout is executed once after the freeze commit, without retuning. It must
produce at least 18/20 end-to-end successes, complete/valid evidence for all 20
runs, no collision, the declared state/event coverage, and no unexplained
failsafe. A miss is an honest Level C result and stops the later 50-run and
10-repeat stages.

The holdout plus the 50 additional unique validation runs must meet this
predeclared allocation:

| Family | Hidden holdout | Additional validation | Unique total | Repeats |
|---|---:|---:|---:|---:|
| All 25 ordered two-source level pairs, one balanced case each | 7 | 18 | 25 | 2 |
| Multi-source, close, and overlap | 3 | 6 | 9 | 2 |
| Wall and corner | 2 | 6 | 8 | 1 |
| Noise and delay | 2 | 6 | 8 | 1 |
| Saturation, timeout, and safe failure | 2 | 6 | 8 | 1 |
| Escape, assist, merge, recenter, and revisit lifecycle | 4 | 8 | 12 | 3 |
| **Total** | **20** | **50** | **70** | **10** |

Starts, headings, and seeds are balanced across the allocation and recorded in
the immutable v2 manifest. This is a stratified empirical sample, not an
exhaustive Cartesian-product proof.

After all unique gates pass, repeat ten predeclared cases selected across the
six families. Repeats use the same source, freeze file, scenario definition,
start, seed, and environment. They are reported separately and never added to
the 70-run success denominator.

## Acceptance calculation

Calculate gates over the 70 unique cases and report observed rates with
two-sided 95% Wilson score confidence intervals overall and by family. Small-family
intervals are descriptive; they do not replace the predeclared point-estimate
gates. Reproducibility is a separate ten-run gate.

1. Functional unit/integration tests all pass; repository-wide lint does not worsen from the documented inherited baseline.
2. All ten activation proofs pass before any tuning.
3. The new 20-run holdout passes its 18/20 early gate before additional validation.
4. Every required run passes Phase 05 completeness and Phase 07 analysis completeness.
5. Collision evidence is valid for every required run and contains zero non-ground contacts.
6. Local-escape success is successful escape attempts divided by all valid observed escape attempts and is at least 95%; designated escape cases must actually exercise their declared state/event coverage.
7. End-to-end goal success is runs with both controller success and simulation-ground-truth success divided by all 70 unique required runs and is at least 90%.
8. Every required family has at least 80% end-to-end goal success.
9. Median successful escape time is at most 20 seconds.
10. 95th-percentile successful escape time is at most 45 seconds.
11. Median valid post-fill orbit count is at most 1.5.
12. Every run terminates normally or through a recorded safe algorithm timeout; no wall timeout, orphan, indefinite circle, or missing terminal evidence is permitted.
13. Revisit rate is successful goal runs with at least one active fill and `revisit_count > 0`, divided by successful goal runs with valid fill/revisit evidence; it must be below 5%.
14. All ten reproducibility repeats preserve goal/timeout/failsafe/collision
    categorical outcomes and required state/event coverage. Relative to the
    corresponding unique run, escape and convergence times differ by no more
    than the greater of 2 seconds or 10%, path length by no more than the
    greater of 0.25 m or 10%, orbit count by no more than 0.25, and final
    goal-distance by no more than 0.10 m.
15. Only after gates 1–14 pass, create the annotated tag.

Unsupported or invalid metric status fails the corresponding gate; it is never converted to zero or excluded silently.

## Backward compatibility and migration

- `algorithm_profile=legacy`, direct visible Gazebo, unseeded execution, canonical topics, and delay/contact controls remain unchanged by default.
- Scenario-schema version 1 files retain their current parsing, expansion, deterministic identity, and behavior. Phase 08 uses schema version 2.
- The relay and contact plugins are simulation-only and default off.
- Canonical topics remain the recorded source of algorithm behavior; validation-only original/delayed topics are additional evidence.
- No frozen value becomes a global launch default. The historical
  `phase08_frozen_parameters.yaml` remains v1-only;
  `phase08_v2_frozen_parameters.yaml` is applied only by the v2 validation
  command.
- The freeze consists of the exact Git commit, the frozen override file, scenario hashes, launch/config hashes, and resolved parameter snapshots.
- Physical integration receives no inferred topic or calibration migration.

## Implementation sequence

After every numbered milestone that changes code or produces evidence, update
the live Phase 08 status from observed results, inspect the bounded diff, and
run `checkpoint_phase.sh 08`. A checkpoint does not replace the exact
validation record or authorize a commit.

1. Preserve and close v1: inventory its hashes and partial results, write the
   v1 failure closeout, and do not resume or mutate its evidence root.
2. Save this amendment and run `validate_phase_context.sh 08 implement`.
3. Confirm the completed Phase 07.5 support and its handoff still pass live
   probes.
4. Repair the detector-to-supervisor activation and rotation-aware goal
   verification contracts in their existing owners. Add focused unit,
   integration, and representative bag-replay regression tests before running
   new simulation batches.
5. Extend the existing Phase 08 orchestration, v2 scenario files, gate
   evaluator, tests, and documentation. Keep v1 reporting readable and commit:
   `phase 08a: add staged robustness validation v2`.
6. Build and run the retained functional suite, new regression tests, schema
   dry-runs, and recorded robust/legacy smoke.
7. Execute all ten activation runs. If any required activation/state/event gate
   fails, preserve evidence and stop before tuning.
8. Execute the three candidates over the same ten training cases (30 runs),
   analyze every run, and generate `phase_08_v2_parameter_selection.json`.
9. Select the winner by the frozen criterion; create
   `phase08_v2_frozen_parameters.yaml`, record source/config/scenario hashes,
   and commit: `phase 08b: freeze staged robust Gaussian parameters`.
10. Require a clean worktree at that freeze commit. Execute the 20 new hidden
    holdouts once without retuning. Stop later stages if the early gate fails.
11. Execute the 50 additional unique validation cases only after the holdout
    passes. Evaluate the 70-run unique gates.
12. Execute ten targeted reproducibility repeats only after the unique gates
    pass.
13. Generate the run manifest, gate JSON, confidence intervals, Markdown
    report, and conditional failure report.
14. If any gate fails, do not create a tag. Record the smallest
    evidence-supported next engineering phase.
15. If gates 1–14 all pass and the tag does not already exist, tag the tested
    freeze commit without force or rewrite:

```bash
git tag -a gesc-gaussian-simulation-ready-v1 <freeze-commit> \
  -m "GESC Gaussian simulation-ready v1: Phase 08 gates passed"
```

Do not push the tag automatically.
16. Write `phase_08_handoff.md`, update durable test evidence, and commit:
   `phase 08: validate and freeze robust Gaussian profile`.

## Tests and commands

Core validation:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 08
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

The focused suite must include detector-supervisor activation, goal-verification
dwell, and representative v1-bag replay regressions before simulation
acceptance begins.

Scenario dry-runs:

```bash
ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_activation.yaml \
  --operator phase08_v2 --dry-run \
  --summary-output /tmp/phase08_v2_activation_dry.yaml

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_training.yaml \
  --operator phase08_v2 --dry-run \
  --summary-output /tmp/phase08_v2_training_dry.yaml

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_holdout.yaml \
  --operator phase08_v2 --dry-run \
  --summary-output /tmp/phase08_v2_holdout_dry.yaml

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_validation.yaml \
  --operator phase08_v2 --dry-run \
  --summary-output /tmp/phase08_v2_validation_dry.yaml

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_reproducibility.yaml \
  --operator phase08_v2 --dry-run \
  --summary-output /tmp/phase08_v2_reproducibility_dry.yaml
```

The files must resolve to 10 activation, 10 training cases per candidate, 20
holdout, 50 additional unique validation, and 10 reproducibility cases. The
orchestrator expands the training set over three candidates for 30 executions.

Planned v2 execution, available only after the existing command owner is
implemented and tested:

```bash
PHASE08_V2_ROOT=~/Experiments/GESC-Gaussian/runs/phase08_v2

ros2 run ros_esc validate_robustness activation \
  --operator phase08_v2 --evidence-root "$PHASE08_V2_ROOT"

ros2 run ros_esc validate_robustness sweep \
  --operator phase08_v2 --evidence-root "$PHASE08_V2_ROOT"

ros2 run ros_esc validate_robustness freeze \
  --operator phase08_v2 --evidence-root "$PHASE08_V2_ROOT"

ros2 run ros_esc validate_robustness holdout \
  --operator phase08_v2 --evidence-root "$PHASE08_V2_ROOT"

ros2 run ros_esc validate_robustness validation \
  --operator phase08_v2 --evidence-root "$PHASE08_V2_ROOT"

ros2 run ros_esc validate_robustness reproducibility \
  --operator phase08_v2 --evidence-root "$PHASE08_V2_ROOT"

ros2 run ros_esc validate_robustness report \
  --operator phase08_v2 --evidence-root "$PHASE08_V2_ROOT"
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
- Performance, holdout, or final gate misses are Level C. Finish the current
  declared stage, preserve every run, generate the structured failure report,
  and obey the predeclared early stop before any later expensive stage. Do not
  retune or weaken thresholds.
- Runtime is bounded but still material: 10 activation, 30 tuning, 20 holdout,
  50 additional unique validation, and 10 reproducibility runs. Verify storage
  and uninterrupted execution capacity before each stage; retries remain
  evidence and do not silently replace declared runs.

## Implementation-time verification

- Confirm the branch, clean status, HEAD, all prior handoffs, and saved Phase 08 plan before edits.
- Reconfirm `gazebo_msgs/msg/ContactsState` and `libgazebo_ros_bumper.so`.
- Verify the actual xacro collision names and that ground contacts are excluded without hiding wall contacts.
- Verify every algorithm consumer uses `algorithm_pose_topic`, `algorithm_source_cost_topic`, and `algorithm_raw_cost_topic` when delay injection is enabled.
- Verify schema-version-1 case keys remain unchanged and schema-version-2 keys include world, disturbance, frozen parameters, and seed.
- Verify all validation topics are recorded and original plus delayed stamps can be paired.
- Verify Phase 07 analysis remains read-only and preserves raw bag hashes.
- Verify the dry-run counts: 10 activation, 10 cases expanded over three
  candidates, 20 holdout, 50 additional unique validation, and 10
  reproducibility runs.
- Verify the unique manifest meets the 25/9/8/8/8/12 family allocation and that
  the 20 plus 50 unique case IDs have no duplicates.
- Verify `phase08_v2_frozen_parameters.yaml` and the freeze commit remain
  byte-identical during holdout, validation, and reproducibility.
- Verify the historical v1 scenario, freeze, parameter-selection, and run
  evidence hashes remain unchanged and are not referenced by the v2 manifest.
- Verify the proposed tag name is absent before creation; never overwrite an existing tag.
- Verify the live status agrees with Git, retained artifacts, and the next
  incomplete acceptance criterion before and after every compaction.
- Verify verbose logs and large run artifacts are retained at recorded paths
  rather than copied into the live status or conversation.
- Treat current code, runtime graph, tests, and completed handoffs as authoritative if any older audit or memory statement differs.
