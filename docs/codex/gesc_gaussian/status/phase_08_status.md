# Phase 08 Live Status

Last verified: `2026-07-28T02:48:20-07:00`
Status: `CLOSED — PHASE 08.3 FAILED / NOT SIMULATION-READY`

## Objective

Execute the fresh Phase 08.3 v3 robustness-acceptance design without changing
controller ownership, cost sign or units, canonical topics, selectable legacy
behavior, or simulation/physical algorithm parity. Preserve every failed
version, stop at the first declared hard gate, and claim simulation readiness
only if the full activation, development/freeze, holdout, unique-validation,
and reproducibility chain passes.

## Verified repository state

- Branch: `feature/gesc-gaussian-robustness-v1`
- HEAD at v2 implementation start:
  `787350e38522856f6463e645714dcc512ad2a5e5`
  (`phase 08: stage validation v2 and harden context recovery`).
- Working tree at v2 implementation start: clean and matched
  `origin/feature/gesc-gaussian-robustness-v1`.
- Plan: `docs/codex/gesc_gaussian/plans/phase_08_plan.md`
- Closed recovery Plan:
  `docs/codex/gesc_gaussian/plans/phase_08_1_plan.md`
- Completed recovery Plan:
  `docs/codex/gesc_gaussian/plans/phase_08_2_plan.md`.
- Terminal v3 Plan:
  `docs/codex/gesc_gaussian/plans/phase_08_3_plan.md`.
- Phase 08.2 starting boundary: clean commit `db8bd66`
  (`phase 08.1: close mixed diagnostic recovery`), branch ahead of origin by
  ten commits.
- Phase 08.2 M3 probe-candidate implementation:
  `204d1a1c9efad3d7d3b9f81315437fa8f671bdae`
  (`phase 08.2: validate recenter probe candidate`).
- Phase 08.2 terminal handoff SHA-256:
  `7f97d6bed7e8a28eccdd60298a52c1cdcd8b94cca70038d91f2b6007d3a05261`.
- Clean M6 evidence commit:
  `c959ce1` (`phase 08.1: retain minimal runtime probes`).
- M7 documentation/checkpoint base: clean `c959ce1`; the bounded closeout
  commit follows final validation.
- Last checkpoint:
  `docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt`

## Completed milestones

- Phase 07.5 support and handoff exist.
- Historical v1 executed 81 training runs, exposed its original holdout, and
  stopped safely during the first planned full pass.
- The v1 outcome did not establish robustness acceptance.
- The plan and implementation package now declare the 120-run v2 design:
  10 activation, 30 tuning, 20 selection-blind holdout, 50 additional unique
  validation, and 10 targeted reproducibility repeats.
- Root agent guidance, live-status initialization, compaction recovery,
  milestone checkpointing, bounded-log guidance, and context-bundle support are
  implemented for future phase work.
- Phase 08 Plan and Implement context validators passed after the amendment.
- V2 implementation preflight reran from clean HEAD `787350e`:
  `init_phase_status.sh 08` preserved this nonempty file and
  `validate_phase_context.sh 08 implement` passed.
- Historical v1 is durably closed in
  `docs/codex/gesc_gaussian/validation/phase_08_v1_failure_closeout.md`.
  Its 50 GiB root, representative hashes, 81-run training result, exposed
  12-run holdout failure, and 203/519 partial full pass were inventoried
  read-only. The separate v2 evidence root was absent.
- Historical closeout commit:
  `5a26638e655e136e154dc16fa13a0ee2b3c39726`
  (`phase 08: close historical v1 evidence`).
- The detector-owned `EVENT_CONVERGENCE_CONFIRMED` activation path and
  rotation-aware source-score verification are implemented in the existing
  detector/supervisor owners. The continuous convergence status remains
  diagnostic.
- The v2 orchestrator, five scenario suites, sealed manifest, three-candidate
  selection, clean-freeze enforcement, 20-run holdout early gate, 70-run
  unique gates, Wilson intervals, ten-repeat comparison, and v1 execution
  retirement are implemented in the existing `validate_robustness` owner.
- Phase 08a implementation commit:
  `8aab27c` (`phase 08a: add staged robustness validation v2`).
- The mandatory v2 activation stage executed all ten declared cases exactly
  once under the separate `phase08_v2` evidence root. It retained all runs,
  passed cleanup 10/10, produced seven typed fills and one observed escape
  attempt, but only 1/10 met the complete integrity and lifecycle contract.
- Gate 2 therefore failed and the plan's early-stop rule closed Phase 08 before
  tuning. Partial and failure reports mark Gates 3–14 `NOT RUN`; no v2 profile
  was selected or frozen.
- Phase 08.1 M1 audited all 58 package files and all 37 `docs/` files. JSON
  validation and local Markdown-link checks passed; the 4,041-line v2 manifest
  parsed with the expected 10/30/20/50/10 structure and 70-case unique
  denominator.
- M1 separated direct research requirements from provisional pure-repulsion,
  redesign, recenter, fill-design, timeout, and threshold hypotheses.
- M1 replaced mandatory fresh chats, verbatim Plan copying, all-history
  rereads, blanket drift/dirty-tree/test-unavailable stops, per-small-milestone
  checkpoints, and the arbitrary file-count cap with current-state,
  Level A/B/C, coherent-owner, and material-boundary rules.
- M1 preserved hard compatibility, final-zero, cleanup, evidence retention,
  freeze/holdout, no-tag, and no-physical-motion gates.
- The historical plan/report threshold mismatch is recorded in
  `validation/phase_08_v2_contract_erratum.md`; historical v2 artifacts were
  not rewritten.
- Phase 08.1 M2 prefilters pose/cost snapshots to the estimator's actual
  request window, rejects nonfinite stamps, and replaces repeated full-set
  sorting with deterministic ordered nearest matching that preserves the
  historical `(absolute delta, pose stamp, original index)` tie rule.
- M2 adds request snapshot/candidate counts and callback-entry wall duration to
  every robust fill success/failure diagnostic path. At the retained
  4,000-pose/14,000-cost scale, synchronization completed in about 0.07 seconds
  rather than the observed 5.5–15.7 seconds.
- Phase 08.1 M3 resets rotation evidence at the actual transition into
  `VERIFY_EXTREMUM` and accepts valid score samples only while verification is
  active. SEARCH-era maxima therefore cannot satisfy goal or undesired-minimum
  classification.
- M3 changes the live verification default from 10 to 12 seconds: two
  three-second rotations plus the longest three-second dwell leave a
  three-second operational margin. Configuration evidence now reports the
  rotation duration, remaining margin, and timing-sufficiency flag. Shorter
  timing remains available only for explicitly declared safe-timeout probes.
- Phase 08.1 M4 implementation makes robust controller startup a one-time
  input-readiness latch. Before a complete valid set arrives, missing/stale
  gaps inside the
  startup timeout remain zero and non-latching; after the latch, stale input is
  strict immediately. After the timeout, both the timer and input-driven
  command path still suppress robust-input fault events while the required
  recording interlock is closed, without relaxing zero output. Normal latching
  resumes when that interlock opens.
- M4 adds a simulation-only operational barrier in the existing recorder:
  fresh valid post-epoch pose, source-cost, legacy-filter-output, timekeeper,
  and robust state/supervisor-command data on the actual canonical or delayed
  algorithm inputs; an actual controller-manager response with both
  controllers active; one total preflight/parameter deadline; and a second
  fresh epoch after parameter capture. Selected heartbeat streams become
  run-specific graph/type/singleton, rosbag-subscription, parameter-owner, and
  minimum-count requirements. Any pre-readiness nonzero command is a permanent
  failure. Any robust pre-authorization non-`SEARCH`, failsafe,
  prior-transition, active-fill, or active-escape evidence is also permanently
  latched across epoch resets and rechecked from the retained bag. The
  pre-authorization monitor closes atomically at authorization or shutdown,
  and the offline scan uses the earlier readiness/stop boundary so expected
  post-stop evidence is not mislabeled. Physical mode does not inherit
  Gazebo-specific checks.
- M4 keeps the existing `AlgorithmEvent` schema readable and validates its six
  publishers per semantic producer stream. A separate receipt-ordered
  `/clock` comparison detects stale event emission, while exact fill-request
  `source_timestamp` correlation remains a distinct causality contract.
- M4 classifies a run that never reached true readiness as
  `infrastructure_invalid`; controller and simulation-ground-truth outcomes
  are unavailable rather than failed. The generic runner retains the attempt
  and does not retry automatically.
- M4 requires strict finite JSON evidence, treats invalid timestamp tolerance
  as an explicit failed check, and turns nonfinite terminal odometry or
  distance overflow into `evidence_extraction_failed` rather than a fabricated
  behavioral result.
- M4 places every mutable Gaussian-fill callback in one dedicated mutually
  exclusive callback group in both profiles and uses the production
  two-thread executor, allowing simulation time to advance during bounded fill
  design without concurrent mutation.
- Phase 08.1 M5 adds a separate schema-v3 development suite at
  `phase08_1_diagnostic_activation.yaml`; the sealed historical v2 activation
  suite remains byte-identical at SHA-256
  `a5e91d2132b3dacccedc24aba13bdacd9ef5ba4ec7c8ae7b69ced6eadaf47d72`
  with all ten historical normalized case keys unchanged.
- M5 replaces the impossible isolated 450/800-input controller-goal
  expectations with explicit below-target classifications, retains the
  calibrated 2500-input goal case, and keeps controller classification
  separate from simulation ground-truth proximity.
- M5 binds each activation contract to its case identity, a contiguous path
  anchored at the first `VERIFY_EXTREMUM`, declared terminal and forbidden
  evidence, and an explicit verification outcome. It uses unordered
  membership for cross-producer event evidence and ordering only for
  same-producer lifecycles such as `FILL_SUPERSEDED -> FILL_MERGED` and
  `TIMEOUT -> FAILSAFE`.
- M5 treats the typed numeric state enum as canonical retained evidence,
  rejects contradictory state names, and prevents a later successful cycle
  from concealing an incorrect first verification branch or forbidden
  `FAILSAFE`.
- Every normal M5 case has two three-second verification rotations, a
  three-second goal or below-target dwell, and a 12-second timeout: a positive
  three-second classification margin. Timing-insufficient contracts are
  reserved for an explicit safe-timeout outcome.
- The M5 reachability record documents analytical source-score bounds,
  synthetic/retained lifecycle support, and the limits of that evidence.
  Pointwise local-center scores do not prove closed-loop convergence; the
  calibrated goal and fill route remain fresh M6 runtime questions.
- Future v3 ground truth must use the realized aggregate field or justified
  dominant-target geometry. A manually assigned multi-source `goal` role is
  not accepted as proof of the actual global optimum.

## Current milestone

- Historical milestone: ten-run Phase 08 v2 activation gate — **FAILED and
  closed** at `2d796dd`.
- Completed milestone: Phase 08.1 M1 durable diagnosis and workflow correction.
- Completed milestone: Phase 08.1 M2 fill-latency correction.
- Completed milestone: Phase 08.1 M3 verification-boundary correction.
- Completed milestone: Phase 08.1 M4 readiness and evidence-semantics
  correction. The first implementation's review gaps were corrected; its
  earlier evidence is superseded by the final source-state gates below.
- Completed milestone: Phase 08.1 M5 scenario-contract correction.
- Completed milestone: Phase 08.1 M6 minimal simulation probes, with one full
  contract pass and one retained mixed-result/full-contract failure.
- Completed milestone: Phase 08.1 M7 handoff and next-step recommendation.
- Completed milestone: Phase 08.2 M1 plan and preflight.
- Completed milestone: Phase 08.2 M2 deterministic recenter correction.
- Completed milestone: Phase 08.2 M3 source-state validation.
- Completed milestone: Phase 08.2 M4 retained Gazebo probe and closeout.
- Current milestone: none; Phase 08.2 is closed.
- Current plan:
  `docs/codex/gesc_gaussian/plans/phase_08_2_plan.md`.
- Next criterion: create and review a separate v3 acceptance Plan. No v3
  development/tuning, freeze, holdout, validation, reproducibility, tag,
  Phase 09, or physical action is authorized by this closeout.
- V3 acceptance, a readiness tag, Phase 09, and physical hardware remain
  unauthorized.

### M6 pre-execution declaration

- Evidence root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6`.
- Suite:
  `phase08_1_diagnostic_activation.yaml`, source SHA-256
  `1e030602ecee99c2d1f563a0ae19e65b1c8e6608662e178eb52b8766edc5a9a7`.
- Probe 1: `activation_goal_high`, one serial headless finite run. Question:
  does post-M3 verification observe two fresh rotations and enter
  `GOAL_HOLD` without readiness, timestamp, collision, cleanup, or final-zero
  regression?
- Conditional probe 2: `activation_fill_create`, one serial headless finite
  run after Probe 1 cleanup. Distinct question: does the corrected
  below-target branch create a typed fill and start escape without blocked
  design, stale emission, collision, cleanup, or final-zero regression?
- Each retained attempt will be analyzed once. No replacement, third probe,
  matrix, tuning, holdout, tag, GUI, or physical command is predeclared.

### M6 retained results

- Probe 1 `activation_goal_high`: **PASSED** at committed M5 HEAD `8ca59d1`.
  The finite headless run completed without outer or inner timeout and retained
  run ID
  `20260726T060431139250Z_simulation_phase08_1_diagnostic_activation-activation_goal_high-robust_gaussian_v1-5ca0c583_860f0907`.
- Recording completeness, classification, cleanup, controller goal,
  ground-truth goal, expected terminal, first-verification path, required and
  forbidden lifecycle evidence, no-collision evidence, final readiness false,
  no motion before readiness, clean pre-authorization lifecycle, fresh event
  timestamps, strict finite JSON, and final-zero checks all passed.
- The collapsed path was
  `SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD`; verification lasted about
  `9.118 s`, the first goal event occurred `98.543 s` after readiness, and the
  final goal distance was `0.280389 m`.
- Cleanup retained no new node or session process. The standard Phase 07
  analyzer ran exactly once into the run-local `analysis/` directory and
  completed with no recording or analysis failures. Raw bag SHA-256:
  `9b9905db133be446039570a8d6c9897726d87e00830625326af48cdc7c9bb652`.
- Probe 1 summary:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6/activation_goal_high_summary.yaml`.
- Probe 2 `activation_fill_create`: **ACTIVATION SUBCLAIM PASSED; FULL
  CONTRACT FAILED** at the same committed M5 HEAD. The finite headless run
  retained run ID
  `20260726T061155030660Z_simulation_phase08_1_diagnostic_activation-activation_fill_create-robust_gaussian_v1-66aad7_9bba343b`.
- Recording, completeness, cleanup, readiness, strict JSON, collision,
  timestamp, request/source causality, and final-zero evidence passed. The
  required first-verification path and required activation events also passed:
  `SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE`.
  Fill design completed in about `0.091 s`, request-to-fill receipt latency was
  about `0.092 s` against the unchanged `5.0 s` limit, and fill request,
  result, and lifecycle source timestamps correlated exactly.
- Escape completed successfully in `8.714 s`, with `0.204169 m` maximum
  radial progress, no stall, no assist, no collision, and a transition to
  `RECENTER`.
- The global schema-v3 contract correctly failed because the later lifecycle
  was
  `RECENTER -> FAILSAFE` after a `30.0469 s` recenter timeout, so the globally
  forbidden `FAILSAFE` state and `TIMEOUT`/`FAILSAFE` events were present.
  This valid behavioral failure is not reclassified or hidden by the passing
  activation prefix.
- Recenter started `0.970 m` from room center while inside the retained fill's
  `0.608675 m` avoidance disk. The direct center route was unsafe, and the
  shared safe-direction selector ranked clearance before center alignment.
  The robot accumulated 141 direction revisions and traveled about `2.738 m`
  tangentially, but its best center distance was only `0.658224 m`, outside
  the `0.25 m` tolerance. No command saturation or tracking defect explains
  the trace.
- The standard analyzer ran exactly once into the run-local `analysis/`
  directory and completed with no recording or analysis failures. Raw bag
  SHA-256:
  `f10924891a97478add654d373301a76047fce9921c0fb348ecd3a1987de1122e`.
  Summary:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6/activation_fill_create_summary.yaml`.
- No replacement or third probe was run. Both predeclared M6 questions were
  answered, and another unchanged or timeout-only run would repeat diagnosed
  evidence rather than resolve a distinct question.

### Phase 08.2 M4 pre-execution declaration

- Candidate implementation commit:
  `204d1a1c9efad3d7d3b9f81315437fa8f671bdae`.
- Suite:
  `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_2_recenter.yaml`,
  SHA-256
  `1b116ef7984d8a679f69da919576125a1ad066da3d55098466da9afac2bae017`.
- Evidence root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_2_recenter`.
- Exactly one serial, finite, GUI-enabled development run is authorized:
  `recenter_retained_fill_create`, seed `8304`.
- Required full path:
  `SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE ->
  RECENTER -> SEARCH`; required events:
  `CONVERGENCE_CONFIRMED`, `FILL_CREATED`, `ESCAPE_STARTED`,
  `RECENTER_STARTED`, and `RECENTER_COMPLETE`.
- `FAILSAFE`, `TIMEOUT`, fill rejection/design failure, collision,
  incomplete recording, missing cleanup, and missing final zero remain
  forbidden. Infrastructure completeness and behavioral success remain
  separate.
- The retained bag will be analyzed exactly once. The attempt is preserved
  regardless of outcome. One identical replacement is permitted only if this
  attempt is objectively pre-readiness infrastructure-invalid and that
  classification is recorded before redispatch. A valid behavioral failure is
  never replaced.
- No additional probe, formal v3 stage, tuning, freeze, holdout, acceptance
  denominator, readiness tag, Phase 09 action, or physical command is
  authorized.

### Phase 08.2 M4 retained result

- The one authorized GUI-enabled seed-8304 probe ran exactly once from
  candidate implementation `204d1a1` and suite SHA-256
  `1b116ef7984d8a679f69da919576125a1ad066da3d55098466da9afac2bae017`.
  The outer runner and `record_run` both returned `0` without timeout.
- Retained run ID:
  `20260726T075031828248Z_simulation_phase08_2_recenter-recenter_retained_fill_create-robust_gaussian_v1-6eb8111305_92a4911a`.
- Evidence root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_2_recenter`;
  summary:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_2_recenter/recenter_retained_fill_create_summary.yaml`.
- The full required path passed:
  `SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE ->
  RECENTER -> SEARCH`. Required convergence/fill/escape/recenter events were
  present. Forbidden states/events and collision were absent.
- Recording completeness passed with no failures or warnings. Cleanup left no
  new node or session process. Final zero passed on all three command evidence
  streams; final readiness was false; typed timestamps, event freshness and
  causality, clean preauthorization, and strict finite JSON passed.
- One typed fill was created. One escape completed in `7.532641327 s`.
  Recenter completed in `8.610255022 s`; observed distance was first
  `0.365533 m`, maximum `0.397381 m`, and final/minimum `0.238489 m`.
  Terminal state was `SEARCH`.
- The standard analyzer ran exactly once into the run-local `analysis/`
  directory and returned `analysis_status=complete` with no recording or
  analysis failures. It retained 22 files, 11 tables, eight plots, and
  `23,243` synchronized anchors.
- Simulation ground truth passed at final goal distance `0.277956 m`.
  Controller goal success remained false because the declared development
  contract required return to `SEARCH`, not a later goal-hold cycle. That
  retained metric does not fail Phase 08.2 and cannot be treated as v3
  acceptance.
- Raw bag SHA-256:
  `47e06cb865f6cb9b5976d2387d9ad479fa90b17bd1efc5ef46df15627c2f226c`.
- No replacement, second probe, second analysis, v3 stage, tag, Phase 09
  action, or physical command ran.

## Current problem or blocker

- No Level A blocker is present. The observed Phase 08.1 recenter engineering
  blocker is closed by deterministic and fresh runtime evidence.
- V2 remains a Level C failure and cannot be resumed, retuned, relabeled, or
  counted toward a new claim.
- M2 removed the repeated full-history synchronization delay that blocked the
  fill node for 5.5–15.7 seconds. M4 now distinguishes cross-producer event
  order from true stale emission. All Gaussian-fill mutable callbacks now
  share a dedicated mutually exclusive callback group under a two-thread
  executor, and an in-process test proves `/clock` advances during a
  deliberately blocked real design callback. Both M6 probes confirmed fresh
  timestamps, and Probe 2 confirmed exact fill request/result causality.
  Historical v2 bags are not reclassified.
- Four activation goal expectations were inconsistent with the adopted
  calibrated `source_score >= 0.95` rule. Only the high calibrated case was
  reachable as `GOAL_HOLD`; ground-truth proximity did not make the others
  controller goals.
- M3 corrected the SEARCH-to-verification evidence leak; the historical high
  goal remains v2 evidence and is not retroactively reclassified.
- The stalled-assist attempt was infrastructure-invalid during Gazebo/controller
  startup, and recenter/resume failed from a pre-behavior watchdog/pose startup
  race.
- The retained bags are sufficient for code and contract diagnosis. Do not
  rerun the historical activation stage.
- M6 confirms the corrected calibrated-goal contract and the fill-create plus
  escape activation prefix. Its second full-run contract remains failed
  because the provisional recenter direction policy did not converge. This is
  a Level C result for that retained probe and a bounded Level B engineering
  question for a future versioned diagnostic iteration, not a Level A
  conflict and not permission to weaken the global safety predicates.
- Phase 08.2 is a passing bounded development phase, not robustness
  acceptance. Phase 08 remains not simulation-ready until a separately
  planned v3 passes its complete frozen acceptance design.

## Files currently relevant

- `docs/codex/gesc_gaussian/plans/phase_08_plan.md`
- `docs/codex/gesc_gaussian/plans/phase_08_1_plan.md`
- `docs/codex/gesc_gaussian/plans/phase_08_2_plan.md`
- `docs/codex/gesc_gaussian/validation/phase_08_v1_failure_closeout.md`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_run_manifest.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_gate_results.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_validation_report.md`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_failure_report.md`
- `docs/codex/gesc_gaussian/handoffs/phase_08_handoff.md`
- `docs/codex/gesc_gaussian/handoffs/phase_08_1_handoff.md`
- `docs/codex/gesc_gaussian/handoffs/phase_08_2_handoff.md`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/phase08_validation.py`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_1_diagnostic_activation.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_2_recenter.yaml`
- `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py`
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/escape_recenter.py`
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/basin_estimator.py`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/record_run.py`
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/validate_run.py`
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/topic_manifest.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py`
- `ros2_ws/src/ros_esc/test/test_phase08_validation.py`
- `ros2_ws/src/ros_esc/test/test_experiment_recording.py`
- `ros2_ws/src/ros_esc/test/test_scenario_runner.py`
- `ros2_ws/src/ros_esc/test/test_state_machine.py`
- `ros2_ws/src/ros_esc/test/test_supervisor_integration.py`
- `ros2_ws/src/ros_esc/test/test_observability_contract.py`
- `ros2_ws/src/ros_esc/test/test_robust_gaussian_algorithm.py`
- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`
- `ros2_ws/src/ros_esc/test/test_scenario_schema.py`
- `docs/codex/gesc_gaussian/validation/phase_08_1_activation_contract.md`

## Decisions and rationale

- D-08-01: retire 519 x 3 for future acceptance. It was unnecessarily
  exhaustive for the bounded empirical claim and v1 failed before completing
  it.
- D-08-02: use exactly 120 declared runs with a 70-case unique denominator and
  ten repeats. This preserves all ordered two-source level pairs while
  stratifying the remaining families.
- D-08-03: activation and the new 20-run holdout are early-stop gates. Preserve
  evidence and do not spend later stages after failure.
- D-08-04: retain the existing runner, recorder, analyzer, and
  `validate_robustness` owner. Do not create parallel orchestration or
  validation implementations.
- D-08-05: detector confirmation is the activation owner. A candidate status
  sample alone cannot leave `SEARCH`; confirmed events carry the canonical
  eight-value fill snapshot, with same-timestamp fallback only for historical
  v1 replay.
- D-08-06: goal verification uses the minimum of per-rotation maxima across
  two complete 3-second rotations. Missing first-score evidence waits within
  the existing timeout; an observed invalid score still fails safe.
- D-08-07: the 20 holdout identities are sealed before tuning. The manifest
  excludes historical v1 run paths/hashes and later stages require exact
  scenario hashes plus a clean, unchanged freeze commit/tree.
- D-08-08: preserve the existing greedy cost-order synchronization and tie
  semantics while bounding its candidate set and implementation cost. Keep the
  five-second design timeout unchanged; measured computation, not a relaxed
  timeout, resolves the observed M2 defect. Defer formal multi-producer
  timestamp semantics and any needed concurrent clock servicing to M4.
- D-08-09: goal evidence begins at the transition into verification, not at
  approach. Use a 12-second default to provide three seconds beyond the
  required rotation-plus-dwell duration. Report rather than globally reject a
  shorter timing configuration because an explicit expected-FAILSAFE timeout
  probe is valid; require timing sufficiency in future GOAL/DESIGN contracts.
- D-08-10: startup grace ends when the robust controller first validates its
  complete input set, not merely when five seconds elapse. This prevents an
  early stale receipt from latching before readiness while preserving strict
  post-authorization watchdog behavior.
- D-08-11: simulation motion readiness requires two fresh operational epochs,
  active controller-manager state, pose/source/filter/timekeeper plus robust
  state/command heartbeats, and parameter capture under one total deadline.
  Promote selected streams into retained run requirements, couple every actual
  consumer route to the canonical target, and permanently reject pre-ready
  motion or pre-authorization lifecycle history even after an epoch reset.
  Use metadata-resolved delayed input aliases when applicable; do not impose
  Gazebo controller-manager semantics on physical mode.
- D-08-12: preserve the existing `AlgorithmEvent` interface. Identify its
  current producer from stable type/detail ownership, fail unknown ownership,
  check regression per producer, check emission freshness separately, and use
  `source_timestamp` only for exact request/result correlation.
- D-08-13: no-true-readiness evidence is infrastructure-invalid and behavior is
  unavailable. The generic scenario runner never retries; a development
  replacement, if later needed, must be identical, predeclared, separately
  retained, and limited to one.
- D-08-14: evidence must remain strict JSON. Normalize corrupt nonfinite values
  to `null` only while recording an explicit failed check; unavailable or
  overflowed terminal geometry is an extraction failure, never a controller
  success/failure inference.
- D-08-15: create a separate schema-v3 diagnostic activation suite and leave
  the historical v2 YAML immutable. Schema v3 is development-contract
  machinery, not retroactive v2 evidence.
- D-08-16: distinguish `goal`, `below_target_extremum`, and `safe_timeout`
  controller outcomes. Only the calibrated goal contract binds controller
  goal; ground-truth proximity remains an independent metric.
- D-08-17: anchor state evidence at the first contiguous verification path,
  use the typed numeric enum as canonical, bind forbidden/terminal predicates,
  and require event order only within one producer. Cross-producer lifecycle
  evidence uses membership because rosbag receipt order is not causal order.
- D-08-18: future multi-source acceptance ground truth must derive from the
  realized aggregate field or justified dominant-target geometry.
- D-08-19: M6 starts with exactly the calibrated high goal and conditional
  fill-create cases under a fresh development-only root. They answer distinct
  post-M3 and post-M2/M4 questions; no full suite is authorized.
- D-08-20: preserve Probe 2 as a mixed-result, globally failed diagnostic.
  Its activation prefix proves the M2/M4/M5 fill-and-escape question, while
  its later recenter timeout independently fails the full lifecycle contract.
  Do not delete global forbiddens, raise the timeout, weaken the retained-fill
  radius, or rerun unchanged. The smallest next Level B correction is
  recenter-only greatest-predicted-center-distance-reduction/alignment
  selection among candidates that already pass the existing hard fill and wall
  checks, without a positive-progress eligibility predicate; escape assistance
  remains clearance-first. Do not change timeout or margin merely to
  reclassify this retained run; any future parameter change requires separate
  versioned evidence.
- D-08-21: the source material makes bounded recenter a tentative strategy,
  not an immutable objective. Correct the master/navigation text that
  overstated it, retain the historical implementation description, and
  require a new Plan plus deterministic closed-loop evidence before changing
  the current policy.
- D-08-22: keep activation-prefix and full-lifecycle results separately
  visible without weakening the current global schema-v3 default. A
  machine-readable multi-scope extension is optional if a later diagnostic
  needs it; it is not a prerequisite for recenter correction.
- D-08-23: Phase 08.1 closes after M7. Future Phase 08 Plan prompts may not
  overwrite the historical Phase 08/08.1 Plans or implicitly authorize v3.
  Phase 09 context now requires the Phase 08.1 handoff as well as the
  historical Phase 08 handoff.
- D-08-24: Phase 08.2 preserves `ESCAPE_ASSIST` selection and all existing
  safety/timeout geometry. `RECENTER` receives a separate safety-filtered
  center-progress ranking, per-update reselection, and current-yaw command
  sweep guard using the existing `0.50 s` supervisor-command stale horizon.
  Passing this bounded phase authorizes only a separate v3 Plan.
- D-08-25: checkpoint tooling selects the highest versioned saved subphase
  Plan instead of hardcoding `_1`. Its 30-line milestone snapshot now consumes
  the full source section while printing the intended bound, avoiding the
  prior `head`/`pipefail` exit `141`. These changes remove mechanical
  checkpoint stops without changing phase gates.

## Validation checkpoints

- `validate_phase_context.sh 08 plan`:
  `Phase 08 plan context is complete.`
- `validate_phase_context.sh 08 implement`:
  `Phase 08 implement context is complete.`
- `validate_required_docs.sh`:
  `All Phase 00 audit documents exist.`
- `bash -n` on the status initializer, checkpoint, context-bundle, and context
  validator scripts: passed.
- `init_phase_status.sh 08`: preserved the existing nonempty status without
  overwriting it.
- Temporary Git-repository initializer test: created a Phase 09 status with the
  slash-containing branch `feature/status-test`, substituted the plan path,
  preserved it on a second call, and returned exit 2 for invalid phase 11.
- `make_codex_context_bundle.sh ... /tmp/dsim_phase08_context_bundle.txt`:
  passed; the bundle contains `AGENTS.md`, the Phase 08 live status, attempts
  not to repeat, and compaction recovery.
- `checkpoint_phase.sh 08`: wrote the stable Phase 08 checkpoint with plan and
  status hashes, Git state, diff check, changed files, and a live-status
  snapshot.
- `git diff --check`: passed after the staged-plan and context-retention
  additions.
- V2 start Git audit: clean branch at `787350e`, no simulation-ready tag, and
  no active Phase 08/Gazebo/recording process.
- V1 closeout representative SHA-256 inventory: passed; source scenario hashes
  match the frozen v1 snapshot. Current v1 inventory contains 320 sqlite3 bags
  and 320 completeness reports.
- Storage preflight: v1 uses about 50 GiB and the filesystem has 329 GiB free.
- Dependency recheck: `gazebo_msgs/msg/ContactsState` resolves and
  `/opt/ros/humble/lib/libgazebo_ros_bumper.so` exists.
- Selected-package build:
  `3 packages finished` using
  `/tmp/dsim_phase08_v2_m2_harness_build`.
- Focused activation/orchestration regression:
  `91 passed, 1 skipped`; the skip is the explicit opt-in recorded Gazebo E2E.
- Retained functional suite after the final test-harness scheduling correction:
  `188 passed, 2 skipped in 9.49s`. Both skips are explicit environment-gated
  Gazebo recording tests.
- Synthetic supervisor integration repeated three times:
  `5 passed` on each pass.
- V2 scenario dry-runs:
  activation `10/0 unsupported`, training `10/0`, holdout `20/0`,
  validation `50/0`, reproducibility `10/0`. Training expands over three
  candidates in the validator for 30 executions; total declared arithmetic is
  120.
- All ten repeat definitions match their referenced unique scenario
  projection exactly for profile, start, sources, bounds, room, disturbances,
  validation, frozen profile, algorithm, success predicates, and seed.
- Python compile, JSON/YAML/schema parsing, fatal flake8, focused E/W/F
  flake8, and `git diff --check`: passed.
- Phase 08 checkpoint refreshed after the Phase 08a implementation evidence:
  passed.
- Repository-standard package result:
  `1040 tests, 0 errors, 836 failures, 3 skipped`. The failures remain
  inherited flake8, pep257, and `ros_esc_interfaces` lint-cmake debt; the
  failure total is 36 lower than the documented Phase 07 baseline of 872.
- Explicit recorded robust/legacy smoke:
  `1 passed in 34.69s`. Both runs passed completeness, classification, and
  cleanup with no surviving graph/process contamination. Retained paths:
  `/tmp/pytest-of-mattb/pytest-10/test_recorded_short_headless_e0`.
  The five-second robust smoke observed `SEARCH` only and did not claim
  behavioral activation; legacy remained not-applicable for controller goal.
- Bounded v2 activation command:
  `timeout 7200s ros2 run ros_esc validate_robustness activation --operator
  phase08_v2 --evidence-root
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2`; exit 1 after retaining
  exactly ten runs. The workflow manifest SHA-256 is
  `66c17005f67dd056e41673a0754e838f5ee22a0280b0f5d649043ad3c461cd71`.
- Activation result: integrity/lifecycle `1/10`, recording complete `3/10`,
  analysis complete `3/10`, classification `1/10`, cleanup `10/10`,
  controller plus ground-truth success `1/10`, valid no-collision evidence
  `9/10`, typed fills `7`, escape attempts `1`.
- The activation-owned functional run passed:
  `189 passed, 2 skipped in 10.44s`.
- Read-only evidence verification: ten completeness documents, ten sqlite3
  bags, and `PRAGMA quick_check=ok` for 10/10. The v2 root uses 1.8 GiB and no
  Phase 08/Gazebo/recording/rosbag process remains.
- Closure report command:
  `ros2 run ros_esc validate_robustness report ...`; expected exit 1,
  Gate 1 PASS, Gate 2 FAIL (`1/10`), Gates 3–14 `NOT RUN`, Wilson intervals
  not applicable, and `simulation_ready=false`.
- Closure retained functional suite after adding partial-report coverage:
  `190 passed, 2 skipped in 11.70s`; focused report file:
  `14 passed in 3.98s`.
- `ament_flake8` and `ament_pep257` on the changed validator/test files:
  passed with no problems. Python compile, fatal/focused flake8, and
  `git diff --check`: passed.
- Representative historical v1 hashes still match the read-only closeout.
  No v1 artifact was resumed, overwritten, referenced by the v2 manifest, or
  counted.
- No tuning, parameter selection, freeze, holdout, 70-run validation,
  reproducibility, physical command, or tag was executed.
- Phase 08.1 M1 shell/context checks:
  `bash -n` passed for `validate_phase_context.sh`, `checkpoint_phase.sh`,
  `init_phase_status.sh`, and `make_codex_context_bundle.sh`;
  both normal and `--strict-history` Phase 08 Implement validation passed;
  both changed template YAML files parsed; `git diff --check` passed.
- Phase 08.1 M1 material-boundary checkpoint:
  `checkpoint_phase.sh 08` passed and wrote the compact precommit snapshot at
  `docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt`.
- The first M2 combined fill test exposed two real matcher assertions plus a
  test-environment failure: `12 failed, 32 passed in 2.17s`. The ROS logging
  path under `/home/mattb/.ros` was read-only and caused the later rclpy context
  failures; reruns used `ROS_LOG_DIR=/tmp/dsim_phase08_1_ros_logs`. The matcher
  was corrected to choose the lowest original index across duplicate nearest
  stamps, and the retained-scale expected match count was corrected from 3,501
  to 3,502.
- M2 estimator regression after correction: `21 passed in 1.30s`; pytest
  duration reporting measured the 4,000-pose/14,000-cost synchronization case
  at about 0.07 seconds.
- M2 fill/legacy regression with a writable ROS log directory:
  `44 passed in 2.07s`.
- M2 final fill, legacy, and observability regression:
  `59 passed in 2.31s`; bag-analysis regressions:
  `11 passed in 5.46s`.
- M2 Python compile and `git diff --check`: passed. Direct `ament_flake8`
  still reports 683 inherited whole-file style findings in the four old source
  and test owners; same-configuration HEAD/current counts are unchanged at
  `41/41`, `410/410`, `27/27`, and `190/190`, respectively. Direct
  `ament_pep257` reports 23 inherited findings; the new diagnostic method does
  not add one.
- Phase 08.1 M2 material-boundary checkpoint:
  `checkpoint_phase.sh 08` passed and refreshed the compact precommit snapshot
  at `docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt`.
- The first broad M3 regression found a scheduling-sensitive new test:
  `1 failed, 88 passed in 10.52s`. The fresh-window behavior itself passed in
  isolation (`1 passed in 0.61s`); the test was corrected to use a one-second
  verification budget and a longer fresh-source publication interval rather
  than depending on a narrow DDS scheduling window.
- Final M3 state-machine, supervisor, observability, Phase 08 validator, and
  legacy regression: `89 passed in 6.88s`.
- The six-test synthetic supervisor integration suite passed on two additional
  isolated runs: `6 passed in 2.07s` and `6 passed in 2.10s`. Including the
  final broad run, the post-entry boundary integration passed three times.
- M3 central launch XML parsing, illustrative-default YAML parsing, Python
  compile, normal Phase 08 Implement context validation, and
  `git diff --check`: passed.
- Same-configuration flake8 HEAD/current counts for the five changed Python
  owners are `49/49`, `243/243`, `28/28`, `50/49`, and `246/246`: no new
  finding and one inherited test-style finding removed.
- Phase 08.1 M3 material-boundary checkpoint:
  `checkpoint_phase.sh 08` passed and refreshed
  `docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt`.
- Superseded pre-review M4 focused recorder/runner/controller regression:
  `58 passed, 1 skipped in 1.49s`; the skip is the explicit recorded
  headless-Gazebo opt-in test.
- Superseded pre-review M4 broad recording, analysis, state-machine,
  supervisor, and Phase 08
  regression: `136 passed, 2 skipped in 11.61s`. The skips are the explicit
  visible-Gazebo recording and recorded headless-Gazebo opt-in tests; neither
  Gazebo nor hardware ran.
- Superseded pre-review M4 isolated build:
  `2 packages finished in 1min 1s` under
  `/tmp/dsim_phase08_1_m4_{build,install}`. The installed `record_run --help`
  entry point returned exit 0.
- Same-configuration `ament_flake8` HEAD/current findings for M4 owners are
  `375/375`, `193/192`, `0/0`, `259/258`, `0/0`, `135/134`, and `190/190`.
  M4 adds no finding and removes three. `ament_pep257` retains the inherited
  `13/13` and `5/5` findings in the two old recorder/validator owners.
- Final review reopened M4 because the original operational heartbeat set did
  not include filter/timekeeper/supervisor command, state validity admitted a
  non-clean lifecycle, readiness was not atomically authorized, future event
  stamps could pass, and runner infrastructure statuses were incomplete.
- Final M4 lifecycle-history targeted regression:
  `8 passed, 49 deselected in 0.41s`. It covers each non-`SEARCH`, failsafe,
  prior-transition, active-fill, and active-escape signal;
  `VERIFY_EXTREMUM -> SEARCH -> fresh epoch` remaining permanently
  unauthorized; corresponding retained-bag/coordinator completeness
  rejection; and a never-authorized shutdown excluding post-stop evidence.
- Final M4 focused recorder/runner/controller regression:
  `104 passed, 1 skipped in 2.33s`; the skip is the explicit recorded
  headless-Gazebo opt-in.
- Final M4 broad recording/analysis/state regression:
  `182 passed, 2 skipped in 12.08s`; the skips are the explicit visible-Gazebo
  recording and recorded headless-Gazebo opt-ins. Neither was enabled.
- Final isolated build completed both selected packages in `2min 30s`; the
  exact final Python source then received incremental `ros_esc` rebuilds after
  final cleanup (`31.2s`), the live shutdown-boundary correction (`31.0s`),
  and the matching offline command boundary (`30.9s`).
  Installed `record_run --help`, `run_scenario --help`,
  `GaussianFill`, and production `main` all passed. A preceding smoke used the
  nonexistent test symbol `GaussianFillNode`; the corrected full smoke passed.
- Final same-configuration `ament_flake8` current/HEAD counts are
  `371/375`, `191/193`, `0/0`, `410/410`, `134/135`, `259/259`, `0/0`, and
  `190/190` for the eight M4 Python owners. M4 adds no finding and removes
  seven. Fatal `E9,F63,F7,F82` and Python compilation pass. Remaining pep257
  findings are inherited in the four older source owners.
- Final normal and strict-history Phase 08 Implement context validation passed;
  required-doc validation, package XML parsing, topic-manifest YAML parsing,
  and `git diff --check` passed.
- Phase 08.1 M4 material-boundary checkpoint passed and refreshed
  `docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt`.
- M5 schema/runner focused regression:
  `64 passed, 1 skipped in 1.98s`; the skip is the explicit recorded
  headless-Gazebo opt-in.
- M5 full non-linter package sweep with writable ROS/Matplotlib paths:
  `278 passed, 2 skipped, 3 deselected in 15.38s`. The skips are the explicit
  visible-Gazebo recording and recorded headless-Gazebo opt-ins; the three
  deselected tests are repository linter markers. Neither Gazebo nor hardware
  ran. A preceding identical sweep without `ROS_LOG_DIR` was
  environment-invalid (`20 failed, 258 passed, 2 skipped, 3 deselected`)
  because rclpy could not write `/home/mattb/.ros`; its isolated rerun above
  passed.
- M5 Python compilation, `ament_flake8`, and `ament_pep257` passed with no
  problems across `run_scenario.py`, `scenario_schema.py`, and their two
  focused test files. The changed legacy test and setup owner retain inherited
  same-configuration debt at `190/190` and `23/23`; M5 adds none.
- M5 final isolated `ros_esc` build succeeded against the M4
  `ros_esc_interfaces` under
  `/tmp/dsim_phase08_1_m5_{build,install}_final3`. The installed schema-v3
  dry-run resolved 10 cases, 0 unsupported cases, 10 bound contracts, and a
  positive `3.0 s` selected verification margin in every case. Summary:
  `/tmp/phase08_1_m5_installed_dry_run_final.yaml`.
- M5 suite SHA-256:
  `1e030602ecee99c2d1f563a0ae19e65b1c8e6608662e178eb52b8766edc5a9a7`;
  reachability-record SHA-256:
  `e787e226d3de4ef19e93867fcb148164d8c306dd7e0264d0354c519793ec3590`.
  The historical v2 activation SHA and ten normalized keys remain unchanged.
- M5 normal and strict-history Phase 08 Implement context validation passed;
  required-doc validation, both activation YAML parses, and
  `git diff --check` passed.
- Phase 08.1 M5 material-boundary checkpoint passed and refreshed
  `docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt`.
- M6 Probe 1 bounded scenario command returned exit 0 after `217.7 s` of
  orchestration for one 180-second recording; `record_run` returned 0 without
  timeout, completeness passed, classification passed, and cleanup passed.
- Probe 1 completeness contains no failures or warnings. In particular,
  `typed_timestamps_nonregressing`, `typed_timestamps_within_clock`,
  `algorithm_event_emission_fresh`, `no_motion_before_readiness`,
  `clean_lifecycle_before_readiness`, `final_readiness_false`,
  `final_commands_zero`, `collision_expectation`, and `strict_json_finite`
  passed.
- Probe 1 one-time offline analysis returned
  `{"analysis_status":"complete"}` with no recording or analysis failures,
  23 event rows, 3,655 state rows, 5,371 odometry rows, 23,261 synchronized
  rows, and eight plots. No Gazebo, recorder, bag-record, or scenario-runner
  process remained.
- M6 Probe 2 bounded scenario command returned exit 1 after about `216.7 s`;
  this was the expected process representation of a valid behavioral
  classification failure. `record_run` returned 0 without timeout, recording
  and completeness passed, infrastructure status was `completed`, cleanup
  passed, and no process remained.
- Probe 2 completeness passed the typed timestamp, source-causality,
  fill-lifecycle, readiness, pre-authorization, strict-JSON, collision, and
  final-zero checks. The required activation path/events passed. The global
  contract failed only because later `RECENTER -> FAILSAFE` introduced the
  forbidden state and timeout/failsafe events.
- Probe 2 one-time offline analysis returned
  `{"analysis_status":"complete"}` with no recording or analysis failures,
  one active fill, one successful escape, no collision, and eight plots.
  Recenter lasted `30.0469 s`, reached a minimum center distance of
  `0.658224 m`, and timed out. No replacement, third probe, formal matrix,
  GUI, tag, or physical command was run.
- M6 normal and strict-history Phase 08 Implement context validation,
  required-document validation, `git diff --check`, process cleanup, and the
  material-boundary Phase 08 checkpoint passed.
- M7 read-only retained-evidence assertions passed for both one-run summaries,
  classification predicates, completeness files, one-time analysis status,
  empty recording/analysis failure lists, and the recorded raw-bag hashes.
  The large bags were not rehashed or reanalyzed.
- Terminal Phase 08.1 activation-contract SHA-256:
  `71a3f8033996298c0d13cebc7efb8c25b98812a3dd80023bd4a2057736214b1e`.
  The earlier
  `e787e226d3de4ef19e93867fcb148164d8c306dd7e0264d0354c519793ec3590`
  hash identifies the committed M5 contract at `8ca59d1`; it is not relabeled
  as the terminal document. The suite and historical-v2 YAML hashes remained
  `1e030602ecee99c2d1f563a0ae19e65b1c8e6608662e178eb52b8766edc5a9a7`
  and
  `a5e91d2132b3dacccedc24aba13bdacd9ef5ba4ec7c8ae7b69ced6eadaf47d72`.
- M7 `bash -n` passed for the context validator. Phase 08 normal and
  strict-history Implement validation, Phase 09 Plan-context validation with
  the new Phase 08.1 handoff requirement, and required-document validation
  passed.
- M7 local Markdown-target validation, historical v1/v2 evidence immutability,
  no-simulation-ready-tag, no active Gazebo/recorder/scenario process, and
  `git diff --check` checks passed. No pytest, build, Gazebo, bag analysis, or
  hardware command was repeated for this documentation/workflow-tooling
  closure.
- M7 terminal material-boundary `checkpoint_phase.sh 08` passed at clean M6
  base `c959ce1` and captured the closed status, complete M7 diff, plan hashes,
  and next-step boundary before the closeout commit.
- Phase 08.2 M1 saved Plan SHA-256
  `e8eac2725298116335c3f35f886e8b00057313108b836112f2d15f9728e6da14`.
  The Phase 08.1 handoff and diagnostic suite remained
  `cdd9ebd2c0649eb8d8e6fa603695aad4afab0c3147d6522ceefd7c615f00a7c2`
  and
  `1e030602ecee99c2d1f563a0ae19e65b1c8e6608662e178eb52b8766edc5a9a7`.
- M1 focused baseline passed: `101 passed in 3.35 s`. Normal and
  strict-history Phase 08 Implement context validation, validator shell
  syntax, and `git diff --check` passed. ROS logs were bounded under
  `/tmp/phase08_2_m1_ros_logs`.
- M2 added safety-only fill/wall eligibility, a recenter-only deterministic
  center-progress selector, per-update recenter reselection, and a current-yaw
  command sweep guard. `ESCAPE_ASSIST` retains its existing preferred
  hemisphere, clearance-first score, and cached selection.
- The exact retained M6 pose/fill closed-loop regression passed with the
  unchanged `0.25 m` tolerance, one-second hold, `30.0 s` state timeout,
  current gains/caps, `0.5 m` lookahead, `pi/4` candidate spacing, and
  `0.50 s` command horizon. It requires completion by `20.0 s`, no inward
  motion while inside the disk, no post-exit re-entry, wall-inset containment,
  and bounded commands.
- M2 focused source-state result: `112 passed in 3.51 s`; modified Python
  compilation and `git diff --check` passed. A prior collection command that
  replaced rather than prepended ROS `PYTHONPATH` ran no tests and was
  immediately corrected; it is not a source failure.
- M3 final focused regression: `112 passed in 3.56 s`.
- M3 final broad non-linter functional regression:
  `289 passed, 2 skipped, 3 deselected in 15.57 s`, compared with the M5
  baseline `278 passed, 2 skipped, 3 deselected`. The two skips are the
  explicit visible and recorded-headless Gazebo opt-ins; the three
  deselections are repository linter markers. Neither Gazebo nor physical
  hardware ran.
- The exact final M3 source built successfully in the isolated
  `/tmp/phase08_2_m3_{build,install}` prefixes: all three selected existing
  packages finished in `1.64 s`. Verbose build logs are retained under
  `/tmp/phase08_2_m3_colcon_logs`.
- Installed launch `--show-args` exposed `gazebo_gui`,
  `algorithm_profile`, and `supervisor_command_stale_sec`. The installed
  supervisor instantiated with the additive `0.50 s` parameter, stopped under
  bounded SIGINT with expected timeout-wrapper exit `124`, and left no
  process.
- The installed Phase 08.2 suite dry-run resolved exactly one seed-8304 case,
  no unsupported cases, and case key
  `6eb811130559703b3253b7eb49d842165037902b12ad47b4d8747d408da70c47`.
  Summary: `/tmp/phase08_2_m3_dry_run.yaml`.
- Sealed one-case suite SHA-256:
  `1b116ef7984d8a679f69da919576125a1ad066da3d55098466da9afac2bae017`.
- Same-configuration focused style debt improved from `623` to `613`
  `ament_flake8` findings across the seven Phase 08.2 Python owners;
  `ament_pep257` remained `7/7`. A changed-line comparison against
  `db8bd66` reports zero new flake8 and zero new pep257 findings. Python
  compilation and `git diff --check` passed.
- One read-only dry-run summary assertion initially used the nonexistent
  `suite` key after the dry run itself had succeeded. The corrected parser used
  canonical `suite_id`, `resolved_run_count`, and `unsupported_count` fields
  and passed; no scenario was redispatched.
- M4 source/install/suite byte comparisons, clean Git check, absent fresh
  evidence root, `DISPLAY=:0`, 327 GiB free-space check, and pre-run process
  check passed before dispatch.
- The bounded GUI scenario command returned `0` after about `223.5 s`.
  `record_run` returned `0` without timeout; the classification, all seven
  predicates, completeness, and cleanup passed.
- The one-time analyzer returned
  `{"analysis_status":"complete"}` after about `49 s`; completeness and
  analysis-completeness contain no failures, and eight standard plots were
  retained.
- Read-only M4 closeout assertions confirmed the exact case key, full collapsed
  state path, required events, no forbidden evidence, no collision, final
  zero, final readiness false, zero recording/analysis failures, raw bag hash,
  and no remaining supervisor/runner/recorder/analyzer/Gazebo process.
- No replacement or additional runtime/analysis attempt ran.
- Closeout local Markdown validation passed six changed-file targets. Normal
  and strict-history Phase 08 Implement context, the updated Phase 09 Plan
  boundary, required-document validation, validator shell syntax, historical
  evidence immutability, no-readiness-tag, suite hash, process cleanup, and
  `git diff --check` passed.
- The terminal checkpoint initially exposed its historical hardcoded `_1`
  subphase label. The bounded tooling correction selects the highest numbered
  saved subphase Plan. Its first regeneration also exposed exit `141` from the
  bounded `head` pipeline under `pipefail`; consuming the whole section while
  printing 30 lines preserved the bound and removed the false failure. Shell
  syntax passed and the final checkpoint returns `0` and identifies
  `phase_08_2_plan.md`.

## Attempts not to repeat

- Do not resume or overwrite the v1 partial full pass.
- Do not reuse exposed v1 holdouts as v2 holdouts.
- Do not accept the historical C8 tie-break as a v2 selection result.
- Do not run planned v2 commands until their interface and scenario files are
  implemented and tested. This condition is now satisfied for dry-run use;
  runtime still begins only after the Phase 08a commit and recorded smokes.
- Do not infer behavioral success from recording completeness or cleanup.
- Do not rerun the v1 JSON/YAML/SQLite integrity sweep; its exact 548/2242/320
  results and representative hashes are retained in the closeout.
- Do not rerun or relabel the ten v2 activation runs, start tuning after their
  failed gate, or compute Wilson intervals without the 70-run denominator.
- Do not treat the one passing high-level goal or one real escape/recenter
  sequence as whole-gate acceptance.
- Do not relabel Probe 2 as a full pass merely because its activation prefix
  passed, and do not hide the useful activation evidence merely because its
  downstream full-run contract failed.
- Do not repeat Probe 2 unchanged, increase its recenter timeout merely to
  chase a pass, or weaken fill/wall safety. Correct and test the progress
  policy in a separately versioned development iteration first; any future
  parameter change requires its own versioned evidence.
- Do not repeat or reanalyze the passing Phase 08.2 seed-8304 probe. Its one
  declared development question is answered and all evidence is retained.
- Do not count the Phase 08.2 development case in a future v3 holdout,
  validation denominator, or reproducibility claim.

## Remaining work

- No Phase 08.2 work remains.
- The smallest justified successor is a separately reviewed v3 acceptance
  Plan with a new evidence root, declared development/tuning design, clean
  freeze, selection-blind holdout, unique validation denominator, and
  reproducibility stage.
- No v3 tuning, holdout, acceptance denominator, tag, Phase 09, or physical
  motion is authorized.

## Stop conditions

- Phase 08.1 and Phase 08.2 are closed and immutable. A future version may not
  rewrite or count their development evidence.
- Stop before Gazebo if the deterministic retained-geometry regression,
  focused regressions, build, launch instantiation, or dry run fails.
- Stop runtime dispatch on cleanup/final-zero/collision/recording corruption.
  Retain every attempt. Replace only an objectively pre-readiness invalid
  attempt under the predeclared bounded policy.
- The closed v2 workflow would stop before tuning if any activation case lacked
  its required state/event, and after holdout if fewer than 18/20 runs
  succeeded or an evidence/collision/lifecycle gate were invalid. These rules
  govern acceptance execution, not M5-M7 recovery development.
- Historical v2 Gate 2 failed, so its later tuning, selection, holdout,
  validation, reproducibility, and simulation-ready tag remain forbidden.
- Never create any simulation-ready tag unless a separately authorized,
  unchanged future attempt passes every amended gate.

## Compaction recovery

Phase 08 v2, Phase 08.1, and Phase 08.2 are terminally closed. Reread
`AGENTS.md`, the Phase 08/08.1/08.2 Plans, this status, and the Phase 08.1 and
08.2 handoffs; inspect Git state and create a separate Plan before any v3
action. Never resume or relabel historical evidence, rerun completed probes or
analysis merely to recover context, or infer authorization for v3, Phase 09,
or physical work.

## Phase 08.3 implementation continuation

The user authorized execution of the saved Phase 08.3 Plan on 2026-07-27.
This continuation is append-only with respect to the closed v1, v2, Phase
08.1, and Phase 08.2 history above. Their evidence, conclusions, case
identities, and hashes remain immutable and excluded from every v3
denominator.

Authority:

- active Plan:
  `docs/codex/gesc_gaussian/plans/phase_08_3_plan.md`;
- active Plan SHA-256:
  `2d669f84c79c863bcb61f28c92be0a4607223a4b40843774db34011fb53c20e0`;
- implementation starting HEAD:
  `bc4b420d` (`phase 08.2: retain passing recenter recovery`);
- branch:
  `feature/gesc-gaussian-robustness-v1`, initially 15 commits ahead of
  origin;
- fresh evidence root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3`;
- terminal Phase 08.2 handoff SHA-256:
  `7f97d6bed7e8a28eccdd60298a52c1cdcd8b94cca70038d91f2b6007d3a05261`;
- Phase 08.2 scenario SHA-256:
  `1b116ef7984d8a679f69da919576125a1ad066da3d55098466da9afac2bae017`;
- historical v2 activation SHA-256:
  `a5e91d2132b3dacccedc24aba13bdacd9ef5ba4ec7c8ae7b69ced6eadaf47d72`.

The implementation authorization covers the Plan's declared milestone commit
boundaries. It does not authorize pushes, physical hardware, Phase 09, an
early holdout reveal, contract weakening, or a readiness tag before every v3
gate passes. The exact user-controlled GPG recipient fingerprint remains
required before M2 can prepare the encrypted acceptance population.

## Current milestone

- Completed milestone: **M0 — reopen context without rewriting history**.
- Current milestone: **M1 — implement and test v3 evidence contracts**.
- State: implementation in progress.
- M0 result: latest-subphase Plan discovery selects
  `phase_08_3_plan.md`; the status is reopened without deleting its closed
  history; checkpoint and context-bundle tooling are freeze-state aware; and
  Phase 09 requires the v3 handoff plus machine-readable
  `simulation_ready=true`.
- No schema-v4 implementation, Gazebo stage, tuning, acceptance-suite
  generation, holdout reveal, validation, repeat, tag, Phase 09, or physical
  action has started.
- Next criterion: schema-v4/aggregate/envelope implementation and its focused
  tests.

## Validation checkpoints

- Initial normal Phase 08 Implement context validation: passed, but the
  pre-M0 validator still selected the hardcoded Phase 08.2 Plan.
- Initial strict-history Phase 08 Implement context validation: passed with
  the same known pre-M0 limitation.
- Historical Phase 08.1/08.2 handoff and v2/08.1/08.2 scenario hashes matched
  their recorded values.
- The v3 evidence root and proposed simulation-ready tag were absent.
- The older status referenced
  `tools/validate_required_documents.sh`, which does not exist. The historical
  command owner is `tools/validate_required_docs.sh`; this stale path is not a
  runtime or source failure.
- M0 `bash -n` passed for the context validator, checkpoint, and context
  bundle.
- `init_phase_status.sh 08` preserved this nonempty status.
- M0 normal and strict-history Phase 08 Implement validation both selected
  `docs/codex/gesc_gaussian/plans/phase_08_3_plan.md` and passed.
- `validate_required_docs.sh` passed.
- Phase 09 Plan-context validation returned the expected exit `1` because
  `phase_08_3_handoff.md` and `phase_08_v3_gate_results.json` do not yet
  exist. No placeholder was created.
- The bounded context bundle at
  `/tmp/dsim_phase08_v3_m0_context_bundle.txt` identifies the v3 Plan, latest
  M0 milestone, absent freeze/contract, and terminal boundary.
- `checkpoint_phase.sh 08` selected the v3 Plan and latest status milestone.
- `git diff --check` and the untracked Plan whitespace check passed.
- No pytest, build, ROS, Gazebo, bag analysis, acceptance-suite generation,
  tag, Phase 09, or physical command ran in M0.

## Attempts not to repeat

- Preserve every attempt-not-to-repeat entry above.
- Do not allow a generic Phase 08 Implement pass to conceal selection of an
  older subphase Plan.
- Do not overwrite the closed status history with a new template.
- Do not create a placeholder v3 handoff or gate result merely to make Phase
  09 validation pass.
- Do not create, reveal, or log plaintext acceptance-suite identities before
  the clean freeze.
- Do not infer the user's GPG recipient fingerprint.

## Remaining work

- Complete and checkpoint M0.
- Implement and test M1 schema-v4, aggregate-ground-truth, encrypted-suite,
  v3 workflow, analyzer, scenario, packaging, and documentation contracts.
- Obtain the exact approved GPG recipient fingerprint before M2 suite
  preparation.
- Execute M2–M9 only in declared order and only while every prior gate passes.

## Stop conditions

- All Level A/B/C conditions in the active Plan apply.
- Stop for any cost-sign/unit, controller ownership, canonical topic,
  selectable-legacy, simulation/physical parity, safety, or overlapping-user
  change conflict.
- Stop before Gazebo if M1/M2 source, deterministic aggregate, build,
  installed-runtime, schema, dry-run, encryption, historical-exclusion, or
  cleanup qualification fails.
- A valid activation, development eligibility, holdout, validation, or
  reproducibility gate miss closes v3 honestly without weakening the
  contract or starting v4 automatically.

## Compaction recovery

Read `AGENTS.md`, `phase_08_3_plan.md`, this status's last
`## Current milestone` section, `phase_08_3_freeze_state.json` when present,
the current external `workflow_state/v3_<stage>.json`, the latest Phase 08
checkpoint, and Git status/diff/log. Recover empirical work from retained
manifests, completeness files, analyses, gate results, and hashes. Never rerun
a matrix, analyzer, or large-bag hash merely to recover context.

## Phase 08.3 M1 completion

M1 is complete at the precommit material boundary. It implements the
schema-v4, aggregate-ground-truth, analysis, runner, encrypted-suite,
replacement, serial-stage, freeze/seal, terminal-report, packaging, test, and
operator-documentation contracts in the existing owners. It adds no
controller, recorder, validator, analyzer, node, message, service, action,
topic, launch owner, physical fork, or algorithm behavior change.

### Bounded Level B corrections

- The Plan's `70/70` behavior gate is implemented as positive lifecycle,
  safety, completeness, cleanup, and applicability evidence. Endpoint goal
  outcomes remain independently scored by the nonredundant `63/70`
  end-to-end gate and family floors. This preserves the declared objective
  instead of making the `63/70` gate unreachable by definition.
- Aggregate truth reads the installed TurtleBot sensor URDF.
  `ros_esc/package.xml` now declares
  `turtlebot3_rotating_sensor` as its runtime owner, and the isolated
  qualification build uses `--packages-up-to ros_esc` so a missing dependency
  cannot be hidden by an explicit three-package list.
- New escape-attempt, timestamped-fill revisit, and aggregate-goal analyzer
  semantics are gated to schema 4. Schema 1–3 retain their prior attempt
  boundaries, current-active-fill revisit calculation, exact provenance, and
  manual-goal reason/status text.
- Prepare publishes the fresh evidence root only after a mode-`0600`
  recoverable transaction is ready. Freeze and seal use deterministic
  create-or-verify recovery across every tested interruption window.
- Serial execution rehashes the resolved suite before every dispatch and the
  terminal audit. Replacement authorization binds and later re-derives the
  invalid record, metadata, and completeness proof. Passing terminal evidence
  rejects a later contradictory failure report, and every sealed failure
  report carries the contract hash.

These corrections are local evidence, compatibility, packaging, and recovery
fixes. They do not weaken a gate or change cost sign/units, canonical topics,
controller ownership, selectable legacy behavior, or simulation/physical
algorithm parity.

### M1 validation evidence

- Final source-first functional gate:
  `381 passed, 2 skipped in 57.55 s` from 383 collected tests. The skips were
  exactly the opt-in headless Phase 06 Gazebo integration and visible Gazebo
  recording smoke; neither ran.
- Focused v3 workflow regression after the final recovery correction:
  `80 passed in 14.84 s`.
- All modified and new Python files passed `ament_flake8`,
  `ament_pep257`, and Python compilation. `git diff --check` passed.
- A final clean non-symlink dependency-closure build at
  `/tmp/phase08_v3_m1_final_install.Q71CfM` built
  `ros_esc_interfaces`, `turtlebot3_rotating_sensor`, and `ros_esc`.
  Installed `validate_robustness --help`, package resources, sensor-URDF
  resolution, and activation/development dry runs passed from `/tmp`.
  Both dry runs resolved exactly ten schema-v4 cases with zero unsupported
  entries.
- All 13 retained schema-v1–v3 suites were deep-equal to their pre-M1
  expansion: 684 resolved runs and seven unsupported records. A
  representative legacy SQLite analysis summary was exactly equal as a whole
  document.
- Static v3 hashes:
  activation
  `8fa385c50f19adf1f362dba286ed3e5c527a175b89692b38632d77471b450031`;
  development
  `1c5ef231b5839386f8db67d7b83e25a6ca11dc2935bc1a7c6584a8645a57f433`;
  candidates
  `c17459dfceaeb16e0d4dfea70469ed0a200c3edd34255e99030dd38eb5a43f7e`.
- Normal and strict-history Phase 08 Implement validation and required
  document validation passed.
- The fresh v3 evidence root and proposed simulation-ready tag remain absent.
  No Gazebo, rosbag, v3 runtime, acceptance generation, tuning, holdout
  reveal, validation, repeat, Phase 09, or physical command ran in M1. No
  related runtime process remains.

## Current milestone

- Completed milestone: **M0 — reopen context without rewriting history**.
- Completed milestone: **M1 — implement and test v3 evidence contracts**.
- State: **WAITING BEFORE M2**.
- Next criterion: obtain the exact user-approved 40-hex GPG recipient
  fingerprint, then run M2 pre-activation source/build/dry-run qualification
  and opaque acceptance-suite commitment.
- M2 performs no Gazebo simulation. If M2 passes and is checkpointed, M3 runs
  ten serial GUI-visible activation simulations. Only the later repeated
  development, holdout, validation, and reproducibility batches are
  headless.

## Remaining work

- Include this status and the precommit checkpoint in the independently
  validated, authorized M1 commit boundary.
- Obtain the exact approved GPG recipient fingerprint; never infer or
  substitute it.
- Execute M2–M9 in declared order while every prior gate remains open.

## Stop conditions

- Preserve all historical and M1 stop conditions above.
- Do not create the v3 evidence root or acceptance ciphertext before the exact
  recipient fingerprint is supplied and verified.
- Stop before Gazebo if M2 source, dependency-closure build, installed
  runtime, schema, dry-run, encryption, historical-exclusion, process, disk,
  or cleanup qualification fails.
- Never reinterpret a valid behavioral miss, replace an attempt without the
  bound raw proof, weaken a frozen threshold, reveal holdout identities early,
  or create the readiness tag before all sealed gates pass.

## Phase 08.3 M1A cleartext-precommit amendment

The user explicitly authorized execution without an encryption key on
2026-07-27. This append-only section supersedes the GPG, recipient,
ciphertext, hidden-identity, and selection-blind requirements in the prior M1
status without rewriting that historical result.

The amended scientific design is a fixed, predeclared, researcher-visible
evaluation. It does not support a selection-blind or independently
administered claim. The 120 declared slots, 70 unique-case denominator, ten
repeats, family allocations/floors, candidate-selection rule, aggregate truth,
thresholds, replacements, stage order, early stops, and every behavioral,
safety, evidence, collision, completeness, cleanup, final-zero, timestamp, and
causality gate remain unchanged.

Authority and implementation:

- amended active Plan SHA-256:
  `4dfcb2d99f3347d40862ea530e71566783352cbef77bd24a73f0fa310c74a63a`;
- `v3-prepare` now writes
  `phase08_v3_acceptance_suite.json` as canonical cleartext plus
  `phase_08_v3_suite_commitment.json`; no GPG executable, fingerprint, key, or
  recipient argument is used;
- the commitment declares
  `population_visibility=researcher_visible_before_activation`,
  `selection_blind=false`, and
  `precommit_mechanism=canonical_json_sha256`;
- `v3-qualify` reparses the tracked bytes, verifies canonical serialization,
  revalidates all 70 unique cases and ten repeat references, and binds the
  exact suite hash into its runtime-input snapshot;
- M3 refuses dispatch unless both precommit files are exact tracked `HEAD`
  blobs and the worktree is clean;
- freeze, seal, contract, stage-state, checkpoint, context-bundle, and terminal
  audit fields use the exact suite SHA-256 rather than ciphertext/plaintext
  hashes.

### M1A validation evidence

- Focused v3 workflow:
  `81 passed in 13.95 s`.
- Full source-first functional gate:
  `382 passed, 2 skipped in 55.72 s`. The only skips were the opt-in headless
  Phase 06 Gazebo integration and visible Gazebo recording smoke; neither ran.
- `ament_flake8` and `ament_pep257` passed for both modified Python files.
- Python compilation, shell syntax for the checkpoint/context-bundle tools,
  `git diff --check`, normal Phase 08 Implement validation, strict-history
  validation, and required-document validation passed.
- The CLI accepts `v3-prepare --operator ... --evidence-root ...` and rejects
  the retired `--holdout-recipient` option.
- Focused tests cover exact tracked-HEAD acceptance, working-tree mismatch
  rejection, untracked precommit rejection, prepare crash recovery, canonical
  hash metadata, and the unchanged freeze/terminal chain.
- No algorithm, controller, recorder, validator, analyzer, topic, ROS
  interface, launch graph, simulation/physical fork, cost sign/unit, threshold,
  allocation, denominator, or candidate value changed.
- The fresh v3 evidence root, cleartext acceptance suite, commitment, frozen
  profile, selection file, contract, and proposed tag remain absent. No
  Gazebo, rosbag, v3 runtime, tuning, holdout, validation, repeat, Phase 09,
  physical, or hardware action ran in M1A.

## Current milestone

- Completed milestone: **M0 — reopen context without rewriting history**.
- Completed milestone: **M1 — implement and test v3 evidence contracts**.
- Completed milestone: **M1A — adopt the user-authorized cleartext
  precommit**.
- State: **READY TO CHECKPOINT AND COMMIT M1A**.
- Next criterion: create the bounded M1A checkpoint/commit, then run M2
  `v3-prepare` and `v3-qualify`.
- M2 performs no Gazebo simulation. If M2 passes and its generated suite and
  commitment are checkpointed and committed, M3 runs ten serial GUI-visible
  Gazebo activation simulations. Development, holdout, validation, and
  reproducibility remain serial headless batches.

## Remaining work

- Checkpoint and commit only the reviewed M1A source/test/Plan/status/operator
  documentation boundary.
- Execute M2–M9 in declared order while every prior gate remains open.

## Stop conditions

- Preserve all historical, M1, and unchanged Plan stop conditions except the
  explicitly superseded encryption/blinding requirements.
- Do not create the v3 evidence root or cleartext suite before the M1A
  checkpoint/commit is clean.
- Stop before Gazebo if M2 source, dependency-closure build, installed runtime,
  schema, dry-run, suite/commitment, historical-exclusion, process, disk, or
  cleanup qualification fails.
- Never alter or regenerate the suite after its M2 commitment, weaken a gate,
  reinterpret a valid behavioral miss, replace an attempt without bound raw
  proof, or create the readiness tag before all sealed gates pass.

## Phase 08.3 M2 completion

M2 is complete at the precommit material boundary. It generated the one fixed
researcher-visible acceptance population and passed the full pre-activation
source, population, dependency-closure build, installed-runtime,
instantiation, schema, dry-run, historical-exclusion, process-cleanliness, and
disk gates. M2 launched no Gazebo simulation and consumed none of the 120
declared simulation slots.

### Fixed population and commitment

- Evidence root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3`.
- Canonical cleartext suite:
  `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v3_acceptance_suite.json`;
  file SHA-256
  `d733ef9dffb372d2c60b57f83c2b96e1062a0a62818587de59a0166df4efe88e`;
  size `927581` bytes.
- Commitment:
  `docs/codex/gesc_gaussian/validation/phase_08_v3_suite_commitment.json`;
  file SHA-256
  `f142f9044b19c51113bb1363e5114f9a831d095648fe647fe15c5c04088e45a2`;
  canonical commitment SHA-256
  `cf981d60e235a3b4fd63ae5a61ccddae87e94ea76a3fb2d4ccaad78bcaa29437`.
- Prepare state:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3/workflow_state/v3_prepare.json`;
  state SHA-256
  `298b58e95550e8be9e93ce6defb3633f963dbacf89feac5ab8987e3860c0f9bb`.
- Recoverable mode-`0600` prepare transaction:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3/prepare/prepare_transaction.json`;
  transaction SHA-256
  `d19a4ced1c961fd851587436c92ba23577e3c98cc68863db2d0fed4f083f6990`.
- The fixed allocation is exactly `20` holdout, `50` additional validation,
  `70` unique, and `10` reproducibility references. Family unique counts are
  `25` ordered-two-source, `9` multi/close/overlap, `8` wall/corner, `8`
  noise/delay, `8` constraint-recovery, and `12` lifecycle.
- Full population validation passed with zero reasons, `80` distinct total
  case keys including repeats, and case-key-set SHA-256
  `8ee311818af1c6b62bfdd355ac75621301430a2a4d5ad079da54a654fa56a7aa`.
- The suite and commitment explicitly record
  `selection_blind=false`,
  `population_visibility=researcher_visible_before_activation`, and
  `precommit_mechanism=canonical_json_sha256`.

### Qualification evidence

- Qualification state:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3/workflow_state/v3_qualification.json`;
  state SHA-256
  `9d3491e6d232cc5223f88750ff5d7313d529e132462e6faa8d452b78ce635060`.
- Qualified runtime-input-map SHA-256:
  `f48268944e7ee1176bdbf8bb93482b0a16bedf283cd0575de7fa330daf55872e`.
- Functional gate:
  `382 passed, 2 skipped in 55.61 s`. The skips were exactly the opt-in
  headless Phase 06 Gazebo integration and visible Gazebo recording smoke;
  neither ran.
- The isolated non-symlink dependency-closure build under
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3/qualification/isolated_build`
  built `ros_esc_interfaces`, `turtlebot3_rotating_sensor`, and `ros_esc`;
  log SHA-256
  `1420ca954d8cca20902d97f0c9b46b02992ee2af5df36f51e6af585349def209`.
- Installed aggregate-truth resources, v3 scenario resources, and
  `validate_robustness --help` passed.
- Launch-argument inspection passed. The bounded supervisor and fill
  instantiations returned expected timeout-wrapper exit `124` after clean
  SIGINT, with no forced kill or surviving process.
- Installed activation dry run:
  exactly `10` schema-v4 cases, zero unsupported, summary SHA-256
  `66fc6e9a48ad3a86c4ed0d1e83ae3fcfae967bb01fbcf0d7a9c9c1a2473f21c0`.
- Installed development dry run:
  exactly `10` schema-v4 cases, zero unsupported, summary SHA-256
  `91c21c6b13813579bfbd7d17f7b1a392ef8000762cfd51006e69fbc0deeaedfe`.
- Historical-exclusion hashes matched all thirteen declared Phase 08,
  v2/08.1/08.2, activation, development, and support inputs. Normal and
  strict-history Implement context checks passed.
- Process sets were empty before and after qualification. Disk forecast passed
  with `350194487296` bytes free against `91268055040` required.

## Current milestone

- Completed milestone: **M0 — reopen context without rewriting history**.
- Completed milestone: **M1 — implement and test v3 evidence contracts**.
- Completed milestone: **M1A — adopt the user-authorized cleartext
  precommit**.
- Completed milestone: **M2 — pre-activation qualification and cleartext
  suite commitment**.
- State: **READY TO CHECKPOINT AND COMMIT M2**.
- Next criterion: checkpoint and commit the exact suite/commitment/status,
  then run all ten M3 activation contracts.
- M3 is the first actual v3 Gazebo stage. It is serial and GUI-visible with
  `gazebo_gui=true`; no headless override is permitted. Only after all ten
  activation contracts and integrity checks pass may M4 run the 30 serial
  headless development simulations.

## Stop conditions

- The suite, commitment, prepare state, qualification state, and runtime-input
  hashes above are immutable. Any drift stops dispatch.
- M3 requires the suite and commitment to be exact tracked `HEAD` blobs and
  the worktree to be clean.
- Preserve all unchanged safety, ownership, collision, recording,
  final-zero, cleanup, evidence-integrity, replacement, and early-stop rules.
- A valid activation behavioral miss is retained and reported; it is never
  tuned away or replaced as infrastructure-invalid.

## Phase 08.3 M3 V3A retained result

The first actual V3 Gazebo stage started from clean committed HEAD
`d69407bfafdd3e79b96b82b5f02bd0a49c715369`. It used the declared
GUI-visible activation suite with `gazebo_gui=true`; this was not a dry run or
headless substitute.

Exactly one case executed:

- case `v3a_goal_aggregate_direct`, seed `9301`;
- run ID
  `20260728T053833113025Z_simulation_phase08_v3_activation-v3a_goal_aggregate_direct-robust_gaussian_v1-acd554565b_92ee18ce`;
- retained under
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3/activation/attempts/001_v3a_goal_aggregate_direct/attempt_01`;
- raw bag SHA-256
  `bf07bcd3458e42b497d33fc302c2e018a68a1ce6636ab75b09af5ec26d405ae8`.

Recording, bag readability, completeness, final zero, and process/node cleanup
passed. No ROS or Gazebo process remained. The standard analyzer ran once.
The post-activation functional gate passed `382` tests with `2` opt-in Gazebo
tests skipped.

The workflow correctly hard-stopped on `non-ground collision` and retained:

- activation state
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3/workflow_state/v3_activation.json`;
  internal state SHA-256
  `5fa0b4e91746bfadca363a7cdb8438d46488f4009c0bd31ae33f81d8a2457cc2`;
  file SHA-256
  `f54c61c8589e46df7655d8e2513218ff7fd29994b1c3d964bdf61378ca0dc8bb`;
- one retained record, `0/1` integrity passes, and `0/1` contract passes;
- all remaining nine activation IDs as `not_run`;
- no M4 development, freeze, holdout, validation, reproducibility, tag,
  Phase 09, physical, or hardware action.

### Contact-control diagnosis

The reported collision was literal but instrumentation-induced. The launch
command incorrectly set `simulation_contact_probe_enabled:=True` even though
the case declared `collision_expected=false`. The validation node spawned its
static `0.20 x 0.20 x 0.40 m` positive-control obstacle at the robot after
readiness.

Read-only bag inspection found `48,298` contact messages, `47,814` during
readiness, and `105` non-ground contact states. All `105` involved
`phase08_contact_positive_control`; none involved another non-ground pair.
They began about `0.154 s` after readiness and ended about `0.388 s` after
readiness, with a maximum retained wrench magnitude of about `5314.15`.

The analyzer correctly reported collision. The physical impulse contaminates
the trajectory, so neither the collision nor the later
`DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE -> RECENTER -> FAILSAFE` path is
reclassified as independent algorithm behavior. The attempt is not eligible
for pre-readiness replacement and will not be rerun in the same root.

Durable records:

- `validation/phase_08_v3a_failure_report.md`;
- `validation/phase_08_v3a_contact_probe_contamination.json`, omission
  SHA-256
  `4f8af99b1b937ea79fa8ceaad459b37d63a29978e6f2fa2360cfcf6abe317add`.

## Current milestone

- Closed lineage: **M3 V3A — FAILED / INSTRUMENTATION-CONTAMINATED / NOT
  SIMULATION-READY**.
- Current milestone: **M3A — bounded contact-control correction and fresh
  lineage qualification support**.
- Amended Plan: the append-only `M3A amendment` in
  `docs/codex/gesc_gaussian/plans/phase_08_3_plan.md`.
- Corrected launch policy: spawn the real probe only when
  `collision_expected=true`; keep contact sensors and the unchanged
  zero-non-ground-contact gate for expected-false formal runs.
- Fresh corrected evidence root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b`; it must remain
  absent until the correction is tested, checkpointed, and committed.
- The exact V3 acceptance suite and commitment are reused byte-identically.
  No population, case, seed, candidate, threshold, denominator, family floor,
  early-stop, or replacement change is authorized.
- Next criterion: implement/test/checkpoint/commit M3A, adopt the exact
  precommit into V3B, rerun qualification, then execute all ten GUI-visible
  activation cases from the beginning.

## Stop conditions

- Never overwrite, resume, relabel, combine, or count the V3A root.
- Never filter the positive-control collision out and claim the contaminated
  run was collision-free.
- V3B must reject any suite/commitment drift and must bind a fresh corrected
  runtime-input snapshot before Gazebo.
- Preserve every original collision, completeness, cleanup, final-zero,
  timestamp, causality, behavior, and early-stop gate.
- M4 remains prohibited unless V3B activation passes `10/10`.

## Phase 08.3 M3A correction validation

The bounded contact-control correction and fresh-lineage adoption workflow
have passed their pre-redispatch validation. No V3B root or additional Gazebo
run was created during these checks.

Implemented boundary:

- `run_scenario.py` now enables the physical contact probe if and only if the
  resolved case declares `collision_expected=true`;
- passive contact sensors remain enabled for all ten expected-false
  activation cases;
- `v3-adopt-precommit` verifies the immutable V3A failure artifacts and
  correction audit, requires an absent fresh root and clean committed source,
  requires the same operator across recovery, and compares the current suite
  and commitment against V3A's exact recorded hashes before adopting their
  bytes without regeneration;
- the recovery transaction binds the declared V3B root and rejects relocation
  or source drift on resume;
- V3B qualification revalidates the retained V3A proof and automatically
  checks the installed direct and recorder launch arguments for all ten cases;
  activation rehashes the retained installed dry-run artifact and revalidates
  that recovery chain immediately before dispatch;
- the public `run_scenario` CLI permits dry inspection but rejects direct
  empirical execution of the formal v3 activation/development suites; formal
  dispatch must use the qualified `validate_robustness` workflow;
- the collision analyzer, missing-contact invalidity rule, zero-non-ground
  gate, activation cases, seeds, profile, thresholds, denominators, and
  hard-stop rules are unchanged.

Validation evidence:

- focused runner/disturbance/v3 workflow gate:
  `129 passed, 1 skipped in 15.80 s`;
- full source-first functional gate:
  `390 passed, 2 skipped in 59.30 s`;
- the two full-gate skips remain exactly the explicit Phase 06 recorded
  headless Gazebo integration and visible Gazebo recording smoke opt-ins;
- all five changed Python/test files passed `ament_flake8`,
  `ament_pep257`, and Python compilation;
- the installed dependency-closure workspace build completed all three
  packages:
  `ros_esc_interfaces`, `turtlebot3_rotating_sensor`, and `ros_esc`;
- installed `validate_robustness --help` exposes
  `v3-adopt-precommit`;
- the production V3A recovery proof passed and resolved the exact suite
  SHA-256
  `d733ef9dffb372d2c60b57f83c2b96e1062a0a62818587de59a0166df4efe88e`
  and commitment SHA-256
  `cf981d60e235a3b4fd63ae5a61ccddae87e94ea76a3fb2d4ccaad78bcaa29437`;
- focused recovery tests reject a jointly changed suite/commitment, a changed
  operator, a relocated interrupted root, an audited-precommit mismatch,
  missing adopted recovery, installed probe-on launch arguments, a changed
  installed dry-run artifact, and retained V3A proof drift before activation;
- an installed non-dry direct `run_scenario phase08_v3_activation.yaml`
  invocation returned the required guard exit `2` without launching Gazebo;
- the installed activation dry run resolved exactly ten schema-v4 cases with
  zero unsupported cases. Across both the direct launch and recorder target
  arguments it contained `20` passive-contact enables, `20` GUI enables,
  `20` probe disables, and zero probe enables. Dry-run SHA-256:
  `52a3ebc30bac2e415c394db6d8e7a938e99cb7424974f9f01d5f034e8edcc19c`;
- normal and strict-history Phase 08 Implement context validation, required
  document validation, and `git diff --check` passed;
- V3A activation state, progress, and records file SHA-256 values remain
  `f54c61c8589e46df7655d8e2513218ff7fd29994b1c3d964bdf61378ca0dc8bb`,
  `b82109f94c1416eb237bd80bafd29342db7d48e91f1ecb8474e351f535763530`,
  and
  `fb604d812eff92940d4c27ac0054c361f00a1ad2b3b07ef7e5f4977de92448a3`;
- the correction-audit omission SHA-256 is
  `4f8af99b1b937ea79fa8ceaad459b37d63a29978e6f2fa2360cfcf6abe317add`.

## Current milestone

- Closed lineage: **M3 V3A — FAILED / INSTRUMENTATION-CONTAMINATED / NOT
  SIMULATION-READY**.
- Completed implementation/test boundary: **M3A — bounded contact-control
  correction and fresh-lineage qualification support**.
- State: **READY TO CHECKPOINT AND COMMIT M3A**.
- Fresh V3B root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b`; confirmed absent.
- Next criterion: checkpoint and commit this correction, create V3B with
  `v3-adopt-precommit`, rerun the complete qualification there, and then
  execute all ten GUI-visible activation cases from the beginning.

## Phase 08.3 M3B V3B adoption and qualification

The corrected fresh lineage was adopted and fully qualified from clean
committed HEAD
`e9e1d500116fe884d06574d316143da94e25d920`. These two commands performed
evidence adoption, source/build/test/schema/launch qualification, and dry
inspection only; they did not launch Gazebo or move a simulated robot:

```text
timeout 1800s ros2 run ros_esc validate_robustness v3-adopt-precommit \
  --operator phase08_v3 \
  --evidence-root /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b \
  --superseded-evidence-root /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3

timeout 1800s ros2 run ros_esc validate_robustness v3-qualify \
  --operator phase08_v3 \
  --evidence-root /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b
```

Both commands exited `0`. The adopted prepare state records:

- lineage `phase08-v3b`, operator `phase08_v3`, and `passed=true`;
- corrected source commit
  `e9e1d500116fe884d06574d316143da94e25d920`, tree
  `7681ec09563849acf5a55895472cd90aded29204`, and runtime-input SHA-256
  `6b76ddfe0ca0751bfbbce7eba4a3fc39b247492e77f7a1e6731721b9f4f5c227`;
- prepare internal state SHA-256
  `f48514e2c5f4fc40517ffd690edc6d2ba4f6239b43d06f0cd867b0af5e7d502a`
  and retained file SHA-256
  `db2961d542a586aa82d8265be57dc46fc4ccfbb69dc5b4ab091dccd57bb88942`;
- prepare transaction internal SHA-256
  `1c758255cfece1da5925c99827417ad27e008cb8789e336bebe940876a2065a4`
  and retained file SHA-256
  `921fc049a938423ae83783d64efd46b3d55c7cedd40a537cf09b01c55be558fa`;
- unchanged acceptance-suite file SHA-256
  `d733ef9dffb372d2c60b57f83c2b96e1062a0a62818587de59a0166df4efe88e`;
- unchanged commitment file SHA-256
  `f142f9044b19c51113bb1363e5114f9a831d095648fe647fe15c5c04088e45a2`
  and commitment omission SHA-256
  `cf981d60e235a3b4fd63ae5a61ccddae87e94ea76a3fb2d4ccaad78bcaa29437`;
- the required V3A contamination-recovery proof, immutable superseded root,
  and researcher-visible, `selection_blind=false` population.

The complete V3B qualification state records `passed=true`, no reasons, and:

- internal state SHA-256
  `5f36c29f5a008375da801b68ca1c8c22efbfc876595195a46f0aa80776e937cd`;
- retained qualification-state file SHA-256
  `5e3489ee3c60e4e1dc218c480d880e6824d89ffcdba644414852ffd5c1e95fb3`;
- prepare-state binding
  `f48514e2c5f4fc40517ffd690edc6d2ba4f6239b43d06f0cd867b0af5e7d502a`;
- full source-first functional gate:
  `390 passed, 2 skipped in 55.96 s`; the skips remain exactly the opt-in
  recorded headless Phase 06 integration and visible Gazebo recording smoke;
- isolated dependency-closure build: all three packages passed in `11.9 s`;
  retained build-log SHA-256
  `2999af9f17deba944d6c74e95864979273179149fb54722c50b5c65a276fcf6f`;
- supervisor and Gaussian-fill runtime instantiation passed with the expected
  bounded exit `124` after clean SIGINT;
- activation/development/candidate counts `10/10/3`;
- activation installed dry-run SHA-256
  `f4841836249531d880ea051f4b33025de87624adbc9cfad642fed11aeaf841a2`
  and development installed dry-run SHA-256
  `8dfd72ae6ffc05ed7081a2de31988569f2f1ae76f1f9fdd4ca9dc47ebdcbeea2`;
- activation contact-launch contract passed for all `10/10` direct and
  `10/10` recorder commands: GUI enabled, passive contact sensors enabled,
  and the positive-control probe disabled;
- exact acceptance population passed with `80` distinct normalized case keys,
  `20/50/70/10` holdout/validation/unique/repeat counts, and the fixed family
  allocation;
- recovery validation passed with SHA-256
  `b880fe9d2dc5724ed016fe5c2d42bb20796330aa7f1124f0ef7d875f0b6922e`;
- process sets before and after qualification were empty;
- disk forecast passed with `349847269376` free bytes versus
  `91268055040` required bytes.

Retained paths:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b/prepare/prepare_transaction.json
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b/workflow_state/v3_prepare.json
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b/workflow_state/v3_qualification.json
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b/qualification/
```

## Current milestone

- Closed lineage: **M3 V3A — FAILED / INSTRUMENTATION-CONTAMINATED / NOT
  SIMULATION-READY**.
- Completed corrected boundary: **M3B adoption and pre-activation
  qualification — PASS**.
- State: **READY TO CHECKPOINT, COMMIT THE EVIDENCE-ONLY QUALIFICATION
  RECORD, AND START ALL TEN GUI-VISIBLE V3B ACTIVATION CASES**.
- No actual V3B Gazebo run has executed yet.
- Next criterion: serially execute all ten fixed activation cases with
  `gazebo_gui=true`; pass every declared contract and integrity gate before
  M4 development is permitted.

## Stop conditions

- Rehash the retained installed activation dry run and revalidate the V3A
  recovery chain immediately before dispatch.
- A real non-ground collision, cleanup contamination, corrupt evidence,
  missing final zero, duplicate ownership, or frozen-input/hash drift stops
  dispatch immediately.
- An ordinary valid behavioral miss does not receive replacement or tuning:
  finish the ten activation cases, retain the complete diagnosis, and close
  V3B before development.
- M4 remains prohibited unless V3B activation passes `10/10`.

## Phase 08.3 M3B V3B retained activation result

Actual Gazebo activation began from clean evidence-only commit `23c2b9b`
against the qualified runtime-input snapshot at
`e9e1d500116fe884d06574d316143da94e25d920`:

```text
timeout 10800s ros2 run ros_esc validate_robustness v3-activation \
  --operator phase08_v3 \
  --evidence-root /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b
```

This was a real GUI-visible simulation, not a dry run or headless substitute.
The first case launched `gzserver` and `gzclient` with `gazebo_gui=True`,
seed `9301`, passive contacts enabled, and
`simulation_contact_probe_enabled=False`.

The workflow retained exactly one case:

- case `v3a_goal_aggregate_direct`, seed `9301`;
- run ID
  `20260728T064829892284Z_simulation_phase08_v3_activation-v3a_goal_aggregate_direct-robust_gaussian_v1-acd554565b_1b6fb3f5`;
- run directory under
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b/activation/attempts/001_v3a_goal_aggregate_direct/attempt_01`;
- raw bag SHA-256
  `2d9b2813b2c15623f62fc44907dc391636e4cd53254d2d923ce13d71ac72453c`.

Infrastructure and evidence observations:

- recorder exit `0`, no outer timeout, and recording completeness passed;
- sqlite3 bag readability, required topics/types/counts, fresh Phase 05
  validation, timestamps, causality, strict JSON, and clean shutdown passed;
- cleanup passed with no remaining descendants;
- all final-command representations were zero and final readiness was false;
- collision evidence was valid and reported zero non-ground collision;
- no timeout or failsafe occurred;
- no analysis exception, analysis failure, recording failure, invalid metric,
  missing critical input, or raw-bag drift occurred;
- the post-activation functional gate passed
  `390 passed, 2 skipped in 58.92 s`;
- no ROS or Gazebo process remained after the workflow exited.

The controller and aggregate-field ground truth both passed. The terminal
state was `GOAL_HOLD`, convergence time was approximately `234.225 s`, and
the final aggregate-target distance was `0.03908346942306904 m`.

The predeclared direct-path behavior contract nevertheless failed. It
required:

```text
SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD
```

and forbade fill, escape, and recenter. The observed path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

`FILL_CREATED`, `ESCAPE_STARTED`, `RECENTER_STARTED`, and
`RECENTER_COMPLETE` were observed. This remains an ordinary valid behavioral
miss even though the robustness path eventually recovered to the goal.

### Premature hard-stop diagnosis

The case predeclared escape metrics as not applicable. The analyzer correctly
retained the unexpected escape as:

```text
analysis_status = partial
applicability_integrity.passed = false
reason = "escape occurred in a case declared not applicable"
```

The outer workflow incorrectly treated that pure behavioral applicability
miss as corrupt evidence, hard-stopped, and left the other nine activation
IDs `not_run`. This contradicts the Plan rule to finish all ten activation
questions after an ordinary behavioral miss and then stop before development.

V3B is therefore closed failed and immutable. It is not resumed or
reclassified. The correction changes only immediate hard-stop routing; the
retained partial analysis, failed applicability integrity, failed direct
behavior contract, and final failed V3B verdict remain unchanged.

Durable records:

- failure report:
  `docs/codex/gesc_gaussian/validation/phase_08_v3b_failure_report.md`;
- machine-readable audit:
  `docs/codex/gesc_gaussian/validation/phase_08_v3b_hard_stop_policy_misclassification.json`;
- audit omission SHA-256
  `dbec6d73e23a7b590e99558e43ec57c99c68fbe5f6921301a8fc618407ebf56e`;
- activation internal state SHA-256
  `8d50df1cf6eed92a8829758357aacbc61503f816f65086a3f51120e1105c9a48`
  and retained state-file SHA-256
  `e915d249e855d8b17c214bdd72efb378caa66636f9838c660ca327cd0c14a80e`;
- progress internal SHA-256
  `49194f254dd6939216d3889623390f333df11eb4fc00d3e26044c0463346e113`
  and retained file SHA-256
  `265d69ae8c4c806fadb5658cb41e88c04832738fc97b44817aa9d62e3e772e45`;
- records and attempt-records file SHA-256
  `4d1edcddec10dbf5b529b0b46d4f1d8189ade380432838f1023cfa1e3c5544ec`;
- attempt-record SHA-256
  `d1cc6b4b2f73d5ad70031d3b74d7ac4b535894bdf5425100d3f72175d2593ad5`;
- analysis-summary SHA-256
  `fa6f06a7a3cd1e80d8405616c6955644e944097ad5f2fceb23579d467540cbd6`;
- analysis-completeness SHA-256
  `c3fc7196032469cb5d3d7966d15ed79706290e5ad506739d9c5ccdf5d300e43c`.

## Current milestone

- Closed lineage: **M3 V3A — FAILED / INSTRUMENTATION-CONTAMINATED / NOT
  SIMULATION-READY**.
- Closed lineage: **M3B V3B — FAILED / VALID DIRECT-PATH BEHAVIORAL MISS /
  PREMATURE HARD-STOP ROUTING / NOT SIMULATION-READY**.
- Current milestone: **M3C — preserve V3B and implement/test the bounded
  behavioral-miss routing correction plus chained V3C recovery**.
- Amended Plan: the append-only `M3C amendment` in
  `docs/codex/gesc_gaussian/plans/phase_08_3_plan.md`.
- Fresh corrected evidence root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3c`; confirmed absent.
- The exact suite, commitment, cases, seeds, profile, contracts, thresholds,
  denominators, collision gate, and final integrity verdict remain unchanged.
- Next criterion: test/checkpoint/commit M3C; adopt the exact precommit into
  V3C; rerun complete qualification; then execute all ten GUI-visible cases
  from the beginning.

## Stop conditions

- Never resume, overwrite, relabel, combine, or count the V3B root.
- Never change the analyzer output or call the V3B direct case a pass.
- V3C adoption must re-prove both V3B and its nested V3A recovery, bind a
  fresh corrected runtime snapshot, and reject any retained-artifact drift.
- A pure applicability-driven behavioral miss may continue dispatch only when
  all other evidence is valid; every genuine evidence, collision, cleanup,
  ownership, timeout, or hash failure remains an immediate stop.
- M4 remains prohibited unless V3C activation passes `10/10`.

## Phase 08.3 M3C-A no-replacement clarification

Independent review completed before M3C source implementation, V3C adoption,
or V3C Gazebo dispatch found a scientific conflict in the proposed all-ten
V3C restart.

The V3B direct-goal trajectory is valid unperturbed behavioral evidence. It
passed recording, cleanup, final-zero, collision, and goal-ground-truth
checks, then failed its fixed direct-path contract. Unlike the
instrumentation-contaminated V3A attempt, it cannot be rerun as if it never
happened. An unchanged retry after observing the failure would violate the
no-replacement rule.

The previous all-ten V3C proposal is therefore retired before implementation.
Its machine audit remains retained as superseded planning history. The
binding policy is:

- machine-readable audit:
  `docs/codex/gesc_gaussian/validation/phase_08_v3b_diagnostic_completion.json`;
- audit omission SHA-256:
  `c7a8acb97755ee7d41b3bd7932e7d4181bc854b7ee310bf1d4325f365a385e8d`;
- carry the exact V3B direct-goal record from its original path with SHA-256
  `d1cc6b4b2f73d5ad70031d3b74d7ac4b535894bdf5425100d3f72175d2593ad5`;
- do not copy, rewrite, reanalyze, redispatch, replace, or relabel it;
- execute only the nine IDs retained by V3B as `not_run`;
- report `carried_record_count=1`, `new_execution_count=9`, and an explicit
  composite ten-slot provenance;
- force V3C activation and Phase 08.3 failed before M4 because the carried
  contract is failed, regardless of the nine new outcomes.

This preserves the purpose of the routing correction: complete the remaining
activation diagnosis after an ordinary behavioral miss. It does not create a
second chance at the failed slot.

## Current milestone

- Closed lineage: **M3 V3A — FAILED / INSTRUMENTATION-CONTAMINATED / NOT
  SIMULATION-READY**.
- Closed lineage: **M3B V3B — FAILED / VALID DIRECT-PATH BEHAVIORAL MISS /
  PREMATURE HARD-STOP ROUTING / NOT SIMULATION-READY**.
- Current milestone: **M3C — implement/test a diagnostic-completion V3C
  recovery with one immutable carried failure and nine new GUI runs**.
- Fresh root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3c`; still absent.
- Next criterion: prove the chained recovery, carried-record immutability,
  non-dispatch of slot one, exact nine-case continuation, and unchanged true
  hard stops; checkpoint and commit before V3C adoption.
- Terminal expectation: after at most nine new activation diagnostics, close
  Phase 08.3 failed. No M4 or readiness tag is possible in this version.

## Stop conditions

- Never rerun or reanalyze the carried V3B direct-goal slot.
- Never claim ten fresh V3C simulations or a pass-eligible V3C activation.
- Reject any V3A/V3B artifact, nested-recovery, carried-record, source,
  operator, root, suite, commitment, launch-contract, or installed dry-run
  drift.
- Preserve every original collision, cleanup, recording, final-zero,
  ownership, timeout, evidence-integrity, and hash hard stop.
- M4, freeze, holdout, validation, reproducibility, tag, Phase 09, and
  physical hardware are prohibited.

## Phase 08.3 M3C implementation and verification

The diagnostic-completion recovery is implemented and independently reviewed.
It preserves the immutable V3B direct-goal failure by pointer and hash, rejects
dispatch of that slot, and permits only the exact nine retained `not_run`
case IDs in their fixed order. The pure applicability exception is limited to
this diagnostic V3C activation and does not convert partial analysis,
applicability failure, direct-path failure, or the composite verdict into a
pass.

Recovery and provenance proof:

- canonical chained-recovery SHA-256:
  `f4f347f17f886dcadb002f44f20b9e8eebe14163e462239b5e52a8787bb182f3`;
- immutable V3B run-directory manifest SHA-256:
  `1794d2424f966fff75e08218379e69d5e3f990c912a144c1897d48bce1aefae5`
  across `33` files, rehashed before every dispatch;
- V3B-to-current source projection:
  `345` unchanged runtime inputs, SHA-256
  `4fcd8c31e7bb8959c2e22ca7f843f121e91a1cce1699d6745fa36ffbc01c3d76`;
- exact activation-invocation contract SHA-256:
  `8e1872d0ea6379ea664d4e37c36f31ed29dd58f8b54818ca2eeb5f5afa411e3b`;
- machine audit file SHA-256:
  `029410f59f27db61bfb1271c0d6a27d429cbca7b94fbd632f93673c7fdf112fa`;
- audit omission SHA-256:
  `c7a8acb97755ee7d41b3bd7932e7d4181bc854b7ee310bf1d4325f365a385e8d`.

Runtime interruption handling now journals dispatch intent before simulation,
classifies an intent without a terminal summary as ambiguous rather than
`not_run`, and never redispatches it. The scenario runner snapshots process,
process-group, and session identities, then applies bounded
`SIGINT -> SIGTERM -> SIGKILL` cleanup to owned descendants on normal timeout,
graceful stop, `KeyboardInterrupt`, or other `BaseException`.

Verification completed before V3C adoption:

- complete functional gate:
  `433 passed, 2 skipped in 64.62 s`; the skips are the two explicit opt-in
  Gazebo tests;
- focused recovery/runner gate:
  `164 passed, 1 skipped`, plus a separate cleanup gate of
  `37 passed, 1 skipped`;
- `flake8`, `pydocstyle`, `compileall`, Bash syntax, strict JSON parsing,
  repository context validation, required-document validation, and
  `git diff --check`: passed;
- standard build of `ros_esc_interfaces`,
  `turtlebot3_rotating_sensor`, and `ros_esc`: passed;
- isolated non-symlink three-package build under
  `/tmp/dsim_phase08_v3_m3c_isolated.cKR2Ws`: passed in `13.0 s`;
- installed activation dry run:
  `10` cases, `0` unsupported, schema `4`, GUI and contacts enabled, physical
  contact probe disabled, zero-probe control enabled; retained SHA-256
  `c1979bc6ad23c2aabf6dd4a70369fda5f8eae6aa892fb39651322953648d6583`;
- installed development dry run:
  `10` cases, `0` unsupported, schema `4`; retained SHA-256
  `4b5f69ea22a35551a123831aef8d7987375e832610757e815ccba642e8c47250`;
- installed supervisor and fill-manager graph instantiation each reached the
  expected bounded wrapper exit `124` after five seconds without `SIGKILL`;
- a real nested-session cleanup smoke left no owned child process behind;
- independent review verdict: **GO** for the bounded M3C correction.

No V3C evidence root exists yet, and no Gazebo simulation was launched during
this implementation or verification. The next operation is to checkpoint and
commit this exact source state, adopt it into the fresh V3C root, rerun
qualification, and then launch only the nine remaining GUI-visible Gazebo
diagnostics.

## Phase 08.3 V3C adoption and qualification

The exact M3C source boundary was committed as
`7cb7b44a33b23f575efe72abcd3a6f733041f0ab`
(`phase 08.3: complete activation diagnosis without retry`) with a clean
working tree. V3C adoption then passed and created the fresh cleartext evidence
root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3c
```

Adoption retained the fixed Phase 08 v3 suite and commitment, revalidated the
immutable V3A/V3B recovery chain, and bound runtime-input SHA-256
`c460f8ad67dcc5b44509e3f8c3be3e9b7c4eab33353c2724c87ac16ab8be6c83`.
Its prepare internal state SHA-256 is
`e8c2a7e3ad18ebe0ed87521108bee1adc4bff5f5309a284c9dfe382e7c9c9d4e`;
the retained prepare-state file SHA-256 is
`286d5b81f2714ad80a498778cb233c7203c16b5b235dee1bb3a6d8b6004a8a55`;
and the retained prepare transaction file SHA-256 is
`d3bd1971e7e35870bb13de526d1fccd3b434b9b39e841c698950dbecea79e15b`.

V3C qualification passed:

- isolated non-symlink build and installed-entrypoint/resource checks passed;
- complete functional gate:
  `433 passed, 2 skipped in 62.76 s`, with only the two explicit opt-in
  Gazebo tests skipped;
- activation and development installed dry runs each resolved `10` cases with
  `0` unsupported;
- all `10/10` direct and recorder activation launch contracts retained visible
  Gazebo, simulation contacts, disabled physical contact probe, and enabled
  zero-probe control;
- chained recovery SHA-256 remained
  `f4f347f17f886dcadb002f44f20b9e8eebe14163e462239b5e52a8787bb182f3`;
- activation invocation contract remained
  `8e1872d0ea6379ea664d4e37c36f31ed29dd58f8b54818ca2eeb5f5afa411e3b`;
- qualification internal state SHA-256:
  `b751fa5f3fc552c8929ff5b5c8c793a9bfa71a224e4dd88d6a5a5ec718111561`;
- retained qualification-state file SHA-256:
  `c5779b50dfef76b55bb00ecb17dd844e4c8fd066cac9f10201f85c6713ef23d5`;
- process sets before and after qualification were empty.

No V3C Gazebo case has run. The qualified next action is the bounded V3C
activation command, which must carry the immutable V3B slot and launch only
the exact nine remaining cases with the Gazebo GUI visible. The composite
activation and Phase 08.3 verdict remain forced failed regardless of those
nine diagnostic outcomes.

## Phase 08.3 V3C prelaunch failure and V3D successor

Verified at `2026-07-28T01:36:30-07:00` against repository HEAD
`6af523fd9485802b8659bb3df4628867802e00b6`
(`phase 08.3: qualify diagnostic v3c activation`).

V3C is now **CLOSED / FAILED / PRELAUNCH INFRASTRUCTURE ERROR / NO
SIMULATION OUTCOME / NOT SIMULATION-READY**. The qualified activation reached
the first required new slot, `v3a_below_target_fill`, but failed in the
runner's ROS boundary observer before a Gazebo run could produce evidence.
The exact retained error is:

```text
AttributeError: __enter__
```

Root cause: `run_scenario._run_record_to_boundary` initialized a private
`rclpy` context and created its observer node on that context, then called
`rclpy.spin_once` without an explicit executor. ROS 2 Humble selected its
global executor, whose default context was uninitialized. Guard-condition
construction attempted `with self._context.handle` on that missing handle and
raised the observed exception. The accompanying
`SingleThreadedExecutor._sigint_gc` destructor warning is secondary cleanup
from the same partially constructed executor.

The failed V3C slot has no attempt run directory below `runs/`, no attempt
scenario summary, no attempt record, no bag, and no simulation outcome.
`attempt_records.json` is empty, the top-level scenario summary contains zero
runs, and `new_execution_count=0`. The sole item in `records.json` is the
immutable V3B `v3a_goal_aggregate_direct` failure carried by pointer and hash;
the workflow's top-level `run_count=1` must not be reported as a V3C
simulation.

Retained V3C activation artifacts, rehashed read-only:

```text
activation/attempts/002_v3a_below_target_fill/attempt_01/
  execution_error.json
  233397500285c7c761bd09f9377d787d9dac7ce3b925a25db727402e1a56a891
activation/progress.json
  1a878ced1c18201f28b1d3caadd5ffa7631d8cb16c002b4d57b2dbb0b69503ba
activation/attempt_records.json
  37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570
activation/records.json
  731d87ab80559b20087c00319062648c582b47a2e19f2623563df573266e423c
activation/scenario_summary.yaml
  73bb4b3fd847b541391738d43adbaafd39dab47245d72da012875a51cabed789
activation/resolved_suite.yaml
  75134d172a44ef70b5ca4370a6e6b9fd91fbb6981f786ce71565749481882108
workflow_state/v3_activation.json
  54067b813957e7cd0e84b0388050dc972668499695bf87a583d7531d261f1186
```

The progress internal SHA-256 is
`e31a27ee6f4ab649fef24dd470af6a12acc4b59a3fee90da0c2963fc9f48edf4`;
the activation-state internal SHA-256 is
`bf0d085b31fa3b2e06c433743c507f89c21ea385f1d57fcc3047a0f8799cfcfe`.
The immutable V3C evidence root remains:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3c
```

The bounded successor is fresh V3D. Its root
`/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3d` was confirmed absent.
V3D must preserve V3C as failed infrastructure evidence, carry the immutable
V3B direct-goal behavioral failure, and execute only the same exact nine
previously undispatched case IDs once each after a focused executor-context
correction, clean checkpoint, adoption, and full qualification.

Current milestone: **M3E — implement and validate the private-context executor
correction, then adopt, qualify, and execute fresh diagnostic V3D**. No V3D
root or V3D result exists yet.

V3D remains diagnostic-only and forced failed. M4, freeze, holdout,
validation, reproducibility, a readiness tag, Phase 09, and physical hardware
remain prohibited regardless of the nine outcomes.

## Phase 08.3 M3E correction verification

Verified at `2026-07-28T02:26:23-07:00` against repository HEAD
`6af523fd9485802b8659bb3df4628867802e00b6` before the correction checkpoint.

The bounded private-context executor correction is implemented. The boundary
observer now owns a `SingleThreadedExecutor` created on the same initialized
private `rclpy` context as its node, spins that executor directly, and
deterministically removes the node, destroys the executor and node, and shuts
down the context. Setup, subscription, spin, cancellation, and cleanup
failures retain the primary exception and bounded descendant cleanup.

The fresh V3D proof is fail-closed and binds:

- immutable complete-root manifests for V3A, V3B, and V3C:
  `1574`, `1574`, and `1540` regular files with SHA-256
  `14344a34be7990a9f1dc359b2b0bcca18eb0a7b775775d4a845e99d8ff943312`,
  `8cb4f77a4d4196e4fbabfe6b2dc4a2ce83b4ab0acc35de60b7f4472550f017c8`,
  and `b3befdcd760ac56f2e2b13a8fe4c1b50a3b7b78eba8e7f659e6193485ccec19d`;
- the exact retained V3B direct-goal record SHA-256
  `d1cc6b4b2f73d5ad70031d3b74d7ac4b535894bdf5425100d3f72175d2593ad5`;
- the exact nine V3C `not_run` cases in fixed order, one attempt each, with no
  replacement state or infrastructure retry;
- the exact V3C prelaunch artifacts and absence of an attempt summary, record,
  runs directory, bag, or new execution;
- the unchanged suite, commitment, operator, activation invocation, repository
  projection, GUI/contact launch contract, and empty process boundary.

The correction audit is retained at
`docs/codex/gesc_gaussian/validation/phase_08_v3c_prelaunch_correction.json`.
Its file SHA-256 is
`b4ba3b2a270adc1eb399c995abc34472d874fc1f33691b9deea97c1e1847ae10`;
its omission SHA-256 is
`00bc460ced8fd8d2490a6ffc88e430b531b6eb11f9564f20aff069afd2c30b4c`.
The four audit-bound source/test SHA-256 values are:

```text
phase08_validation.py
  ea1ee693f2d57ec9f5d08030aff90df4631615d4798ec810e841455915369ea9
run_scenario.py
  82dd7b0f0d7aea90882fad0cc05f8c5a2694328e56f5fbb3b1320748765f7176
test_phase08_validation.py
  cbb1d7394c705a823d4a87309fbf034b5442529efad89ecad8743aabbdadadbb
test_scenario_runner.py
  adb2b4674ffed19d75b430175e6b0e11652ed4062c05d89cced6788cf6c94c80
```

Verification:

- real-root production recovery proof: passed in `8.29 s`, resolving the exact
  nine V3D execution IDs and the `1574/1574/1540` retained-root counts;
- complete source-first functional gate:
  `475 passed, 2 skipped in 65.83 s`; the skips are only the explicit
  headless-Gazebo and visible-Gazebo opt-in tests; retained log:
  `/tmp/dsim_phase08_v3d_functional_resealed.log`;
- independent source-first focused gate:
  `206 passed, 1 skipped`, with only the opt-in Gazebo test skipped;
- targeted `ament_flake8` across the four changed Python files, fatal
  `flake8` checks, production-file `pydocstyle`, `py_compile`, strict JSON,
  context validation, and `git diff --check`: passed;
- the repository-wide package lint wrappers remain outside a usable changed-
  file gate because they report the existing broad baseline (`5130` flake8
  and `589` pep257 violations); no result from those wrappers is claimed as
  passed;
- bounded standard build of `ros_esc_interfaces`,
  `turtlebot3_rotating_sensor`, and `ros_esc`: passed, `3` packages in
  `2.17 s`; retained colcon logs:
  `/tmp/dsim_phase08_v3d_standard_build_resealed`;
- installed `validate_robustness --help`: passed;
- installed real-ROS, no-Gazebo private-context boundary smoke: passed, with
  normal child exit, no timeout, no false boundary observation, and retained
  child output;
- installed copies of `phase08_validation.py` and `run_scenario.py` matched
  the audit-bound source hashes exactly;
- independent read-only audit: **GO** for checkpoint, commit, V3D adoption,
  and V3D qualification.

The V3D root remained absent and the ROS/Gazebo/workflow process set remained
empty after verification. No Gazebo simulation was launched by this
correction gate. The next action is a clean checkpoint and commit, followed by
fresh V3D adoption and full qualification. Only a successful qualification
may authorize the exact nine GUI-visible Gazebo diagnostic simulations.

## Phase 08.3 V3D adoption and qualification

Verified at `2026-07-28T02:32:07-07:00`.

The M3E correction boundary was committed as
`7a0db9533491eaed7eaed29fe4f6a26ee038913a`
(`phase 08.3: recover prelaunch diagnostic activation`) with a clean working
tree. Fresh V3D adoption then passed and created the cleartext evidence root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3d
```

Adoption resolved lineage `phase08-v3d` and retained:

- repository commit
  `7a0db9533491eaed7eaed29fe4f6a26ee038913a`, tree
  `a46e70a0ccca18824252f5a60eb8c98187fece8c`, and runtime-input SHA-256
  `db8a707e7230d31a34833a89749f75d67aec7ed4628013dd6881f83cecc974af`;
- unchanged suite SHA-256
  `d733ef9dffb372d2c60b57f83c2b96e1062a0a62818587de59a0166df4efe88e`
  and commitment SHA-256
  `cf981d60e235a3b4fd63ae5a61ccddae87e94ea76a3fb2d4ccaad78bcaa29437`;
- prepare internal state SHA-256
  `f21fa08c1ee4ed702db2d25f681c0394b062664321c9e27268a25c602a804831`
  and retained state-file SHA-256
  `502c2f9c72ba990ccba3883fe7c84f3bae5fbe69e954658b77f20bcf59d5aa05`;
- prepare transaction internal SHA-256
  `f0f2f7bcade5d8f9ffd19e0365bedff9e47f26616f6cecf32fe9a30d9973cd16`
  and retained file SHA-256
  `004107ba936e25a574916b9fe1b4e0634006332a6318a31dff0d00535e7a2841`.

V3D qualification passed:

- complete functional gate:
  `475 passed, 2 skipped in 63.88 s`; the only skips were the explicit
  headless-Gazebo and visible-Gazebo opt-in integration tests;
- isolated non-symlink three-package build, installed entrypoint/resources,
  launch-argument resolution, and bounded supervisor/fill instantiation:
  passed;
- installed real-ROS private-context boundary smoke:
  passed with retained log SHA-256
  `24297f5e399060cabe44a88bc19d1946869ea99dac4e00f9789a6f9929729e4d`;
- activation and development installed dry runs each resolved `10` cases with
  `0` unsupported; retained SHA-256 values
  `12e1b867b5e2bbde25a2a60b825eb5a36d1ec694ade5d3bd5b624fab369ddcf5`
  and
  `c9539a147b4b189946541d8d4ffc8f4c939233f68ba9db890f9af3062fce0f98`;
- all `10/10` direct and `10/10` recorder activation launch contracts retained
  GUI-visible Gazebo, simulation contacts, disabled physical contact probe,
  and enabled zero-probe control;
- exact activation invocation contract SHA-256 remained
  `8e1872d0ea6379ea664d4e37c36f31ed29dd58f8b54818ca2eeb5f5afa411e3b`;
- complete V3A-to-V3D recovery validation passed with SHA-256
  `b335abafb92386d977c810bc58017b62fbb502546cc459cadec4470d88285fbd`;
- qualification internal state SHA-256
  `4019cb7293b2bf9cc666e2462b3562f8374d10ec86c3cfa44dd45f601105e1d8`
  and retained state-file SHA-256
  `972062154f51c3ad2313e71980b70cc8c01e171a170789c7d7d2e8090d0bfe28`;
- process sets before and after qualification were empty.

No Gazebo simulation was launched during adoption or qualification. V3D is
now qualified for one bounded activation. That activation must carry the
immutable V3B `v3a_goal_aggregate_direct` failure without dispatch and execute
only these nine new cases, in order and at most once each:

```text
v3a_below_target_fill
v3a_pure_escape_recenter
v3a_stalled_assist
v3a_fill_merge
v3a_full_lifecycle_goal
v3a_revisit_guard
v3a_boundary_saturation
v3a_noise_delay
v3a_safe_timeout
```

The next action is the bounded `v3-activation` command with Gazebo GUI enabled.
V3D and Phase 08.3 remain forced failed regardless of the nine outcomes; M4,
readiness tagging, Phase 09, and physical hardware remain prohibited.

## Phase 08.3 terminal V3D activation result

Verified at `2026-07-28T02:48:20-07:00` against clean activation commit
`a21671e858d504c81761c258cea18e407924c2e2`.

Phase 08.3 is **CLOSED / FAILED / NOT SIMULATION-READY**. The bounded V3D
activation command ran with X11 display `:0`, launched Gazebo server and client
with `gazebo_gui:=True`, and executed exactly one new case:

```text
case: v3a_below_target_fill
seed: 9302
attempt: 1
run_id:
  20260728T093403582899Z_simulation_phase08_v3_activation-
  v3a_below_target_fill-robust_gaussian_v1-f20cd3c751_74a3fcfb
```

The run enabled simulation contacts, disabled the physical contact probe, and
used no headless argument. Motion readiness became true. The retained bag
contains real Gazebo/ROS behavior through:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> FAILSAFE
```

The runner's boundary observer saw `CONVERGENCE_CONFIRMED`, `FILL_CREATED`,
and `ESCAPE_STARTED` and requested a graceful scoped stop. That stop exposed
an unchanged recorder hard failure:

```text
RCLError: Failed to publish: publisher's context is invalid
```

`record_run` used the default rclpy signal handlers. Scoped `SIGINT` invalidated
its default context before the main thread could publish readiness false and
stop true. `RecordingCoordinator.request_stop()` and the 10 Hz publisher timer
then raced on the invalid context. The exception aborted the final-zero wait,
owned target/bag stop sequence, executor/thread teardown, metadata
finalization, and the final validator. The recorder returned `2`.

This is an infrastructure/recording failure, not a valid behavioral result:

- `recording_complete=false`;
- infrastructure status `runner_or_recorder_failure`;
- immutable `completeness.json` remains the `run did not finalize` sentinel;
- `/stop_requested` has no retained message;
- `/recording_ready` ends true with no final false;
- shutdown/final-zero completeness was not proved;
- partial analysis exists but cannot repair or reclassify the run.

The SQLite bag itself is structurally healthy: both `PRAGMA quick_check` and
`PRAGMA integrity_check` returned `ok`. It retains `400131` messages across
`33` topics over `190.097876649 s`, including `5456` odometry,
`37085` simulation-contact, `3713` algorithm-state, and `30`
algorithm-event messages. Its diagnostic content remains useful, but it is
not acceptance evidence.

The activation correctly stopped without replacement or retry:

- immutable carried V3B records: `1`;
- new V3D executions: `1`;
- V3D attempts: `1`, at `attempt_index=1`;
- ambiguous interrupted attempts: `0`;
- replacements: `0`;
- behavior-contract passes: `0`;
- integrity passes: `0`;
- remaining exact cases marked `not_run`: `8`.

The eight `not_run` cases are:

```text
v3a_pure_escape_recenter
v3a_stalled_assist
v3a_fill_merge
v3a_full_lifecycle_goal
v3a_revisit_guard
v3a_boundary_saturation
v3a_noise_delay
v3a_safe_timeout
```

The executed slot is not replacement-eligible because readiness was true and
the robot executed non-`SEARCH` behavior. V3D is immutable and must not be
continued or rerun.

Retained activation hashes:

```text
workflow_state/v3_activation.json
  file: b1e4d5d9290057503f49e88976949c1ebb6eb337f6edf65110a56efac93e5c1c
  internal: 24ea143a452ecf28b5cd8a2c54d91444932de49334862038bbe47f29c898adcb
activation/progress.json
  file: de919138523b7b04b1f5cca10c94f06e14e06b26387d2c7692633c61c0695c5f
  internal: 30047de029892f16f16d6ab972bb23a47cfd3dc085caa5a6935cfcb5102e2b5a
activation/attempt_records.json
  8b7edaac2ddb2bbe07ecd4fc4f73c44e9c41589dd887fb809ad13480429721f5
activation/records.json
  ed32711e2206fde3da4b72e3bd634e480c6513c952218f2ae4ccab7fdcacec98
activation/scenario_summary.yaml
  196bd037e6d618ab0540fe612c4960f4a9c60ef943d1984b0a1c74462d3d17cf
attempt scenario summary
  ef8a6dd3b334db8de4069c9b38d49853ec362faa0b8b7fa7a2d691915f0ad5dc
attempt record
  a8ddcdf5363e7dd05085a674336afe7db3c5143fc95bcc76f95a130971bb6f91
```

The new run directory retains `33` files with manifest SHA-256
`cfe30977ac51d11b04c35125a277c8eac0538c018f8ccb2faadc4a73c67ab6cd`.
The bag SHA-256 is
`c2c526bf0f969276a6c6c987517cc2da2d77484e7a20e33e27865f0caba274bd`.
After terminal reporting, the complete V3D root contains `1576` regular files
with SHA-256
`94161e4ec08512d844c43949da4a7ff0883031b4ea536aafad79390c66f261c9`;
its two excluded directory-symlink mappings are recorded by the root-manifest
audit.

The post-run functional integrity gate still passed:
`475 passed, 2 skipped in 64.72 s`; the two skips remained the explicit
Gazebo opt-in integration tests. Cleanup retained no new nodes or session
processes, and the final ROS/Gazebo/workflow process scan was empty.

## Phase 08.3 terminal report

The declared `v3-report` command generated the terminal machine and human
artifacts and returned `1`, matching the failed outcome:

```text
phase_08_v3_gate_results.json
  3d9835ff504a9a87af4a752a77c30a9a1ac9f47ee143968b2d7912309ee83fce
phase_08_v3_run_manifest.json
  81a721f5cbb815f85db11c946f0f7099969e09a05e845356a4baf6f9f1d319b3
phase_08_v3_validation_report.md
  cb88420088dd71899806c496029e2e9c8b4e081fe4233537d36f204382b323e3
phase_08_v3_failure_report.md
  0b7ac933655c27a124b4251b046e69225ade15ec6e20a01b1f79ab04e80ac5cc
workflow_state/v3_terminal.json
  file: 09ff05ce70090553857377966bd983c4eba6e247b97393d045ef7eec992bc3b6
  internal: e29c501868ea7f1a03fd678d78ca56f07bbf3eca8d4ea2688d6766c087370d74
```

Prepare and qualification passed; activation failed. Development/tuning,
freeze, acceptance-contract seal, holdout, unique validation, and
reproducibility are all `NOT RUN`. No candidate was selected, no frozen
profile or acceptance contract was created, no Wilson interval denominator
exists, and no result may be represented as Gaussian robustness acceptance.

The detailed failure record is
`docs/codex/gesc_gaussian/validation/phase_08_v3d_failure_report.md`.
The terminal handoff is
`docs/codex/gesc_gaussian/handoffs/phase_08_3_handoff.md`.

No encryption or GPG key was used or required. No readiness tag was created.
M4, Phase 09, and physical hardware were not started.

The smallest justified next engineering work is a separately authorized
recorder correction using `SignalHandlerOptions.NO`, the existing
`DeferredSignalShutdown`, bounded executor shutdown/thread join, and
exception-resilient finalization. The present Plan does not authorize an
automatic V3E or v4. A diagnostic V3E would have to preserve both the V3B and
V3D failed slots and execute only the remaining eight once; a pass-eligible
claim requires a separately planned fresh v4/full activation.

## Phase 08.4 V4 implementation authorization

Opened at `2026-07-28` from clean repository HEAD
`db7db1cd5091053cefda3a1c8ee57d1357e9e538`
(`phase 08.3: close fresh robustness acceptance`).

The user explicitly authorized planning and executing a fresh, pass-eligible
V4 and requested that Codex make the bounded corrections needed to reach the
120-run test. The binding Plan is:

```text
docs/codex/gesc_gaussian/plans/phase_08_4_plan.md
SHA-256
63369edbbfa2c8fb987822f5f05d0dea7487443f27e4963e5b61e24ccc644f69
```

V4 is not V3E and does not resume or retry V3A, V3B, V3C, or V3D. All prior
roots and outcomes remain immutable failed evidence. The fresh proposed V4
root is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4
```

The `10/30/20/50/10` 120-slot allocation and 70-unique-case denominator are
retained. V4 uses new activation and development cases. It adopts the exact
canonical bytes of the still-unexecuted V3 70+10 formal population, with a
machine proof that none of those formal slots has a historical execution.
This prevents post-V3 case adaptation while keeping V4 runs, implementation
freeze, profile selection, contract, evidence root, and outcomes fresh.

No encryption, GPG key, physical hardware, Phase 09, or readiness tag is
authorized by opening V4.

### M0 validation evidence

Verified at `2026-07-28T10:21:19-07:00`:

- normal and strict-history Phase 08 Implement context checks pass and select
  `phase_08_4_plan.md`;
- the V4 Plan SHA-256 is
  `63369edbbfa2c8fb987822f5f05d0dea7487443f27e4963e5b61e24ccc644f69`;
- required-document validation passes;
- shell syntax passes for the context validator, checkpoint tool, and context
  bundle;
- the checkpoint and context bundle both select the V4 Plan and the latest V4
  milestone;
- versioned freeze-state and acceptance-contract discovery now prefers the
  latest available Phase 08 version instead of hardcoding V3;
- `git diff --check` passes;
- no Gazebo, ROS runtime, V4 evidence root, or hardware action was started.

The repeated-heading recovery defect exposed by the first M0 checkpoint was
corrected in the existing tools. Their verified SHA-256 values are:

```text
checkpoint_phase.sh
  144c5054c85c6cd0ec547571df8ac31517f34e7dad6ce5b1f7dc10c9e01d185e
make_codex_context_bundle.sh
  f6950d84305b8f328e67bb4e876fac99c2e27862be2a835c0a831924667c7962
```

## Current milestone

**M1 — repair recorder shutdown.**

The M1 correction remains inside the sole existing `record_run` owner:

1. initialize rclpy with `SignalHandlerOptions.NO`;
2. use `DeferredSignalShutdown`;
3. publish readiness false and stop true while the context is valid;
4. observe final zero and stop the target and bag;
5. stop the executor and join its thread before node/context teardown;
6. complete every cleanup/finalization step after an individual exception
   while retaining the primary failure.

### Next criterion

Focused recorder lifecycle/order/error tests, an installed real-ROS no-Gazebo
SIGINT smoke, the retained functional gate, build/static checks, status,
checkpoint, and a clean bounded commit must pass before V4 workflow
implementation or any V4 Gazebo simulation.

### Stop conditions

- Stop for any Level A ownership, compatibility, cost-sign/unit, physical,
  dependency, or overlapping-user-change conflict.
- Document and test bounded recorder/runner/workflow corrections as Level B.
- Close V4 honestly on any valid Level C activation, development, holdout,
  validation, or reproducibility failure.
- Never weaken a gate or replace a valid behavioral failure.

## Phase 08.4 M1 recorder correction completion

Verified at `2026-07-28T10:30:20-07:00` from committed V4-opening boundary
`70d9cdc`.

The sole existing recorder now:

- initializes rclpy with `SignalHandlerOptions.NO`;
- installs the shared `DeferredSignalShutdown`;
- observes signal requests only at bounded orchestration boundaries;
- publishes readiness false and stop true before context teardown;
- retains the final-zero observation window before stopping the target/bag;
- removes and stops the executor, joins its spin thread, destroys the
  coordinator, and only then shuts down rclpy;
- continues every later cleanup step after an individual exception;
- stores cleanup errors in metadata and fails completeness honestly.

This directly corrects the V3D
`RCLError: Failed to publish: publisher's context is invalid` root cause
without modifying controller, supervisor, Gaussian-fill, cost, filter,
scenario, analyzer, topic, message, launch, or physical behavior.

Source/test SHA-256 values:

```text
record_run.py
  c46daa9e4b2193bb53777ddbc74b48b03f814b08026926cf46562f95749f9e8a
test_experiment_recording.py
  770a1457c475e0ad3bd0f2ccaf1a3ccf17ca93c0fe9b4e0de7c44ee1a5185520
```

Validation:

- focused recording subset: `60 passed, 1 skipped in 1.22 s`;
- complete retained functional gate:
  `477 passed, 2 skipped in 63.56 s`;
- standard build: three packages passed in `1 min 1 s`;
- installed real-ROS, no-Gazebo, process-level SIGINT smoke: passed with
  normal local DDS and no invalid-context error;
- fatal `flake8` (`E9/F63/F7/F82`), `py_compile`, and
  `git diff --check`: passed;
- focused historical-file `ament_flake8` baseline remains `625` style
  findings and production `pydocstyle` remains `17` inherited findings;
  neither is represented as a passing gate.

The two functional skips remain the explicit headless- and visible-Gazebo
opt-in tests. No Gazebo, V4 evidence root, readiness tag, Phase 09, or hardware
action ran during M1.

## Current milestone

**M2 — implement and precommit the fresh V4 workflow.**

### Next criterion

Parameterize the existing Phase 08 workflow owner for V4 without duplicating
it, add new activation/development/candidate inputs, bind the unchanged unused
70+10 formal population with a zero-prior-execution proof, add V4 CLI and
stage/hash tests, then pass source/build/installed dry qualification at a
clean commit before creating the V4 evidence root.

### M2 stop conditions

- Do not change algorithm behavior or formal acceptance thresholds silently.
- Do not modify the adopted 70+10 population bytes.
- Do not create or run a V4 Gazebo root before M2/M3 qualification.
- Stop for a required duplicate owner, physical fork, or unresolved
  historical-execution collision.
