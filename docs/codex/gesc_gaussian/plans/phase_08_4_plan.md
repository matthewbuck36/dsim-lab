# Phase 08.4 Plan — Fresh V4 Robustness Acceptance

## Status and authority

This is the authorized implementation-and-execution Plan for a fresh,
pass-eligible Phase 08 V4 experiment. The user authorized Codex on
2026-07-28 to plan and execute V4 and to make the bounded corrections needed
to reach the declared 120-run test.

V4 is not V3E and does not resume, overwrite, relabel, retry, or count V3A,
V3B, V3C, or V3D. It does not authorize physical hardware or Phase 09.

Planning preflight passed:

```text
Phase 08 plan context is complete.
```

Verified planning boundary:

- branch: `feature/gesc-gaussian-robustness-v1`;
- planning HEAD: `db7db1cd5091053cefda3a1c8ee57d1357e9e538`;
- worktree: clean and 27 commits ahead of the remote tracking branch;
- Phase 08.3: `FAILED / NOT SIMULATION-READY`;
- no simulation-ready V3 tag exists;
- V3A, V3B, V3C, and V3D evidence roots are immutable;
- one real GUI Gazebo V3D simulation exposed a recorder shutdown race;
- the retained post-run functional baseline is
  `475 passed, 2 skipped`;
- no encryption, GPG recipient, key, ciphertext, or selection-blindness
  requirement exists.

Current code, tests, resolved ROS interfaces, launch graph, Git state, and
future retained evidence remain authoritative.

## Objective and permitted claim

Fix the existing recorder's signal-safe shutdown lifecycle, qualify a fresh V4
workflow and scenario envelope, select one bounded parameter bundle from fresh
development evidence, freeze the implementation/profile/contract, and execute
one predeclared 120-slot robustness experiment.

Only if every declared V4 gate passes may the project claim:

> One fixed `robust_gaussian_v1` implementation and parameter profile met the
> V4 behavioral, evidence-integrity, safety, completeness, collision, cleanup,
> timing, causality, family, and reproducibility gates over the declared
> bounded simulator-relative multi-light scenario population.

This is a stratified simulator result. It is not universal convergence,
absolute photometric calibration, physical TurtleBot readiness, Phase 09
authorization, or a claim about arbitrary nonconvex fields.

## Historical evidence boundary

These roots are read-only historical evidence:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_2_recenter
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3c
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3d
```

V4 uses the absent fresh root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4
```

No historical run enters a V4 numerator, denominator, replacement, or
reproducibility comparison.

## Why V4 is justified

V3D did not fail because Gazebo could not simulate the robot. It launched
`gzserver` and `gzclient`, authorized motion, and retained real algorithm
states and events. It failed because scoped `SIGINT` reached `record_run`,
whose default rclpy signal handler invalidated the ROS context before
readiness-false and stop-true publication.

The smallest justified correction is inside the existing recorder:

1. initialize rclpy with `SignalHandlerOptions.NO`;
2. use the existing `DeferredSignalShutdown`;
3. keep the context valid through readiness-false, stop-true, final-zero,
   target stop, and bag stop;
4. stop the executor and join its spin thread before destroying the node or
   context;
5. execute all cleanup/finalization steps even when one step raises;
6. retain the first cleanup error and fail completeness honestly.

This is a Level B runtime/evidence correction. It does not change cost sign,
units, algorithm behavior, scenario truth, controller ownership, topics,
messages, simulation/physical parity, thresholds, or acceptance arithmetic.

## Existing owners to extend

- `experiment_recording/record_run.py` remains the sole recorder and shutdown
  coordinator.
- `experiment_recording/validate_run.py` remains the sole completeness
  validator.
- `scenario_runner/run_scenario.py` remains the sole serial Gazebo
  orchestrator.
- `scenario_runner/phase08_validation.py` remains the sole Phase 08 workflow
  owner.
- `gesc_gaussian_bag_analysis.py` remains the sole offline analyzer.
- `gazebo.launch.xml` remains the sole simulation graph.
- `custom_controller` remains the sole final `/cmd_vel` publisher.
- Existing supervisor, Gaussian fill, modified-cost, filter, and controller
  implementations remain shared with future physical operation.

No parallel recorder, validator, runner, analyzer, algorithm node, launch
graph, package, simulation fork, or physical fork may be added.

## V4 run allocation

The fresh 120-slot structure is retained:

| Stage | Runs | Acceptance denominator |
|---|---:|---|
| Fresh activation | 10 | No |
| Bounded development | 30 = 3 candidates x 10 common cases | No |
| Predeclared holdout | 20 | Yes |
| Additional unique validation | 50 | Yes |
| Reproducibility repeats | 10 | No |
| **Total** | **120** | **70 unique cases** |

V3 did not execute development, holdout, validation, or repeats. There is no
evidence supporting a smaller family allocation or weaker denominator.

## Acceptance-population decision

V4 adopts the exact canonical bytes of the existing tracked
`phase08_v3_acceptance_suite.json`, whose 70 unique cases and ten repeat
references were generated and committed before any V3 activation outcome.
None of those 80 formal acceptance/repeat slots executed in V3.

This is scientifically preferable to regenerating a new population after
seeing V3 activation behavior:

- the case population cannot be adapted to the recorder correction;
- every case identity, source layout, start, disturbance, family allocation,
  partition, and repeat mapping remains pre-outcome;
- the original suite SHA-256 remains binding;
- V4 adds an adoption manifest proving zero historical execution for every
  carried formal slot;
- V4 run IDs, evidence root, implementation freeze, profile selection,
  contract, and outcomes remain fresh.

The internal V3 suite identifier is preserved as provenance and is never
rewritten. The V4 contract records that the population is researcher-visible,
not selection-blind, and adopted byte-for-byte from the unused V3 formal
population.

## Fresh activation and development inputs

V4 creates new schema-v4 activation and development YAML files. Their case
keys must not match any V1, V2, Phase 08.1, Phase 08.2, V3 activation, or V3
development case.

Activation uses seeds `10301` through `10310`, serial GUI Gazebo, enabled
passive contact evidence, disabled physical contact probe, and the existing
finite `150/240/600/30 s` preflight/run/wall/shutdown bounds.

The ten activation responsibilities are:

1. aggregate-goal convergence, allowing any safe declared robust recovery
   path before `GOAL_HOLD`;
2. below-target fill creation and repulsive escape;
3. pure escape, recenter completion, and resumed search;
4. measured stall and assisted escape;
5. fill supersession and merge;
6. full fill/escape/recenter-to-goal lifecycle;
7. post-fill revisit guard;
8. wall/corner saturation recovery without collision;
9. Gaussian noise plus sensor/pose delay;
10. the explicit safe verification-timeout path.

V3's failed direct-path requirement is not silently relabeled. V4 replaces it
with a new case and a new predeclared end-to-end contract because V3 proved
that forbidding all robust recovery in an aggregate-goal activation case does
not measure the intended robustness claim. Branch-specific cases still
require fill, escape, assist, merge, and recenter exactly.

Development uses seeds `10401` through `10410`, new transformed geometries,
headless Gazebo, and the same ten common cases for all candidates:

- `V4-C0`: current baseline;
- `V4-C1`: compact/patient;
- `V4-C2`: broad/reactive.

The only tunable parameters and values remain:

| Parameter | V4-C0 | V4-C1 | V4-C2 |
|---|---:|---:|---:|
| fill covariance scale | 2.5 | 2.0 | 3.0 |
| amplitude-depth scale | 1.5 | 1.2 | 1.8 |
| fill exit sigma | 2.50 | 2.25 | 2.75 |
| stall window | 3.0 s | 4.0 s | 2.0 s |
| minimum radial progress | 0.05 m | 0.03 m | 0.08 m |

Every other algorithm, launch, model, threshold, timeout, topic, and
acceptance setting remains frozen from V4 preparation.

Candidate eligibility remains:

- ten evidence-valid slots;
- at least `9/10` end-to-end successes;
- every declared lifecycle branch reached;
- at least eight observed escape attempts, all successful;
- no collision, unexpected failsafe, cleanup failure, orphan, corrupt bag,
  missing final zero, or unavailable applicable metric.

Selection remains the V3 lexicographic rule: end-to-end count, behavior count,
escape rate, minimum family rate, escape p95/median, orbit median, revisit
rate, convergence median, path median, then candidate ID.

## V4 workflow and artifacts

Add flat commands to the existing entry point:

```text
validate_robustness v4-prepare
validate_robustness v4-qualify
validate_robustness v4-activation
validate_robustness v4-development
validate_robustness v4-freeze
validate_robustness v4-seal
validate_robustness v4-holdout
validate_robustness v4-validation
validate_robustness v4-reproducibility
validate_robustness v4-report
```

The V4 implementation must reuse the existing V3 engine helpers through an
explicit version/specification object or bounded parameterization. It must not
copy the 11,000-line workflow into a second implementation.

Tracked artifacts:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v4_activation.yaml
  phase08_v4_development.yaml
  phase08_v4_candidates.yaml
  phase08_v4_frozen_parameters.yaml
docs/codex/gesc_gaussian/validation/
  phase_08_v4_population_adoption.json
  phase_08_v4_parameter_selection.json
  phase_08_v4_freeze_state.json
  phase_08_v4_acceptance_contract.json
  phase_08_v4_gate_results.json
  phase_08_v4_run_manifest.json
  phase_08_v4_validation_report.md
  phase_08_v4_failure_report.md
docs/codex/gesc_gaussian/handoffs/
  phase_08_4_handoff.md
```

External workflow states live below
`phase08_v4/workflow_state/v4_<stage>.json`. Large bags, plots, and logs never
enter Git.

## Unchanged acceptance gates

The V3 gates remain binding unless this Plan explicitly changes activation
identity or provenance:

- exactly 70 unique formal cases, at least `63/70` end-to-end;
- family floors: `20/25`, `8/9`, `7/8`, `7/8`, `7/8`, `10/12`;
- at least 39 designated escape attempts and at least 95% success;
- at least 38 valid successful escape durations and orbit values;
- median escape at most `20.0 s`, p95 at most `45.0 s`;
- median orbit count at most `1.5`;
- fewer than 5% revisits over at least 24 valid applicable successful runs;
- all 70 unique cases and ten repeats pass recording, sqlite3, completeness,
  collision, cleanup, final-zero, final readiness false, timestamp, causality,
  strict-JSON, ownership, and frozen-hash gates;
- zero non-ground contacts;
- every formal case reaches its sealed lifecycle and aggregate-field contract;
- all ten reproducibility comparisons pass their categorical and numeric
  tolerances;
- two-sided 95% Wilson intervals are reported overall and by family but never
  replace point gates.

Status values remain `passed`, `failed`, `not_applicable`, `unavailable`,
`infrastructure_invalid`, and `not_run`. A valid behavioral failure is never
replaced.

## Early stops and replacement limits

- Recorder correction or qualification failure: no Gazebo activation.
- Activation: hard integrity/collision/cleanup/hash failure stops immediately;
  ordinary valid behavior misses finish all ten, then V4 stops before
  development.
- Development: complete 30 unless a hard stop occurs; no eligible candidate
  closes V4 before freeze.
- Holdout: stop when `18/20` or any family floor is impossible.
- Validation: stop only when a declared 70-case/family/escape/orbit/revisit
  gate is mathematically impossible or a zero-tolerance gate fails.
- Reproducibility: first mismatch stops the remaining repeats.

Infrastructure-invalid replacement caps remain `1/3/1/2/1`, total `8`, with
at most one replacement per slot. Eligibility requires readiness never true,
no nonzero command, no non-`SEARCH` lifecycle, external startup cause, and
clean retained cleanup evidence.

## Milestones and commit boundaries

### M0 — open V4

- save this Plan;
- append V4 authority and next criterion to the Phase 08 live status;
- make context/checkpoint tooling identify `phase_08_4_plan.md`;
- validate normal and strict-history Phase 08 context;
- checkpoint and commit.

Exit: durable V4 implementation context is complete.

### M1 — repair recorder shutdown

- implement signal-safe, exception-resilient recorder cleanup;
- add focused lifecycle/order/error-injection tests;
- run an installed real-ROS no-Gazebo SIGINT smoke;
- run recording, scenario-runner, legacy, and full retained functional tests;
- update status, checkpoint, inspect diff, and commit.

Exit: readiness-false, stop-true, final-zero, target/bag stop, metadata
finalization, and validator completion occur with a valid context and no
surviving process.

### M2 — implement and precommit V4

- parameterize the existing workflow owner for V4;
- add fresh activation/development/candidate inputs;
- bind the unchanged unused 70+10 population and adoption proof;
- add V4 CLI, stage-order, no-history-counting, hash, and compatibility tests;
- run source/build/installed dry qualification;
- checkpoint and commit all exact pre-runtime inputs.

Exit: fresh root absent, all V4 static contracts pass, and inputs are tracked
at a clean commit.

### M3 — prepare and qualify

- create the fresh V4 evidence root transactionally;
- prove every carried formal case has zero prior execution;
- run the full functional suite, isolated build, installed resources,
  launch instantiation, real-ROS recorder SIGINT smoke, and activation/
  development dry runs;
- verify disk forecast and empty process sets;
- checkpoint and commit qualification evidence.

Exit: only a passing qualification may start Gazebo.

### M4 — run ten fresh GUI activation cases

- execute serially with visible Gazebo;
- retain/analyze every attempt once;
- apply only the predeclared replacement policy;
- rerun the retained functional gate.

Exit: `10/10` integrity and contracts pass, or V4 closes before development.

### M5 — run 30 headless development cases

- execute all three candidates over the same ten cases;
- retain/analyze every attempt;
- select exactly one eligible candidate by the declared rule;
- checkpoint and commit selection evidence.

Exit: one eligible deterministic winner, or V4 closes before freeze.

### M6 — freeze and seal

- generate frozen parameters and selection evidence;
- rerun qualification;
- commit the implementation/profile/scenario freeze;
- require clean Git;
- create the V4 contract binding the original unused population hash;
- checkpoint and commit evidence-only seal artifacts.

Exit: immutable runtime contract exists.

### M7 — run 20 holdout cases

Exit: all integrity gates and the `18/20` plus family floors pass, or V4
closes with later slots `not_run`.

### M8 — run 50 additional unique cases

Exit: all 70-case gates pass, or V4 closes before repeats.

### M9 — run ten repeats

Exit: `10/10` reproducibility comparisons pass, or V4 closes.

### M10 — terminal closeout

Always generate the gate JSON, manifest, report, status, checkpoint, and V4
handoff. Preserve all evidence and report exact run/skipped/not-run totals.

On success only, after the terminal tested commit, create the local annotated
tag:

```text
gesc-gaussian-simulation-ready-v4
```

Never force, move, overwrite, or push the tag automatically.

## Validation commands

All ROS/Gazebo/build commands are bounded. The functional source-first gate is:

```bash
timeout 300s python3 -m pytest -q -rs \
  src/ros_esc/test/test_aggregate_field_truth.py \
  src/ros_esc/test/test_phase08_validation.py \
  src/ros_esc/test/test_bag_analysis.py \
  src/ros_esc/test/test_bag_analysis_integration.py \
  src/ros_esc/test/test_scenario_schema.py \
  src/ros_esc/test/test_scenario_runner.py \
  src/ros_esc/test/test_simulation_disturbances.py \
  src/ros_esc/test/test_experiment_recording.py \
  src/ros_esc/test/test_recording_integration.py \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_escape_recenter.py
```

The standard three-package build uses isolated logs under `/tmp`. Changed
Python files must pass focused `ament_flake8`, fatal `flake8`, production
`pydocstyle`, and `compileall`; inherited repository-wide lint debt remains a
separate baseline.

V4 workflow commands use explicit bounds:

```text
v4-prepare          1800 s
v4-qualify          1800 s
v4-activation      10800 s
v4-development     28800 s
v4-freeze           1800 s
v4-seal             1800 s
v4-holdout         21600 s
v4-validation      46800 s
v4-reproducibility 10800 s
v4-report           1800 s
```

Before and after every empirical stage, require no unexpected `run_scenario`,
`record_run`, `ros2 bag`, Gazebo, controller, supervisor, fill, or workflow
process. Free space must be at least:

```text
25 GiB + 512 MiB x remaining declared slots
```

Use Python sqlite3 read-only `PRAGMA quick_check`; never open retained bags
read-write.

## Stop conditions

Level A — stop and request direction:

- cost sign/units, controller ownership, canonical topics, shared algorithm,
  physical boundary, or compatibility must change;
- a duplicate owner, physical fork, new package, or unavailable required ROS/
  Gazebo dependency becomes necessary;
- the formal population bytes or their unused-execution proof drift;
- overlapping user changes cannot be preserved.

Level B — document, test, checkpoint, and continue:

- bounded recorder, runner, workflow, schema, packaging, evidence, timeout, or
  performance corrections that preserve the objective and gates.

Level C — close V4 honestly:

- valid activation, candidate, holdout, validation, or reproducibility gate
  failure;
- frozen contract/hash/denominator cannot be satisfied;
- replacement cap is exceeded.

Do not weaken a gate, rerun a valid behavioral failure, or begin V5
automatically.

## Compaction-safe recovery

After every milestone:

1. update `phase_08_status.md`;
2. update the current external `workflow_state/v4_<stage>.json`;
3. run `checkpoint_phase.sh 08`;
4. record bounded logs and exact artifact paths/hashes;
5. commit the independently validated boundary when authorized.

After interruption, reconstruct from this Plan, live status, checkpoint,
Git state, V4 workflow state, manifests, progress, completeness files,
analysis summaries, and retained hashes. Never rerun an expensive matrix only
to recover chat context.

## Immediate next criterion

M0 context/checkpoint completion, followed by the M1 recorder signal-safe
shutdown correction. No Gazebo V4 run may begin before M1 and M2/M3
qualification pass.
