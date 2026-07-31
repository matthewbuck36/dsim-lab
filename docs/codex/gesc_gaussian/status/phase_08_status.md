# Phase 08 Live Status

Last verified: `2026-07-31T12:44:26-07:00`
Status: `PHASE 08.8 CLOSED; CLOSEOUT COMMITTED AT 4DEF990; PRIMARY 11/11 FORMAL PASS; SECONDARY FORMAL FAIL; BROAD CLAIM NOT ESTABLISHED`

## Objective

Retain the complete Phase 08 simulation-validation history, close the failed
broad simulation-ready objective honestly, and identify the strongest bounded
two-light evidence without relabeling failed versions. Preserve controller
ownership, cost sign/units, canonical topics, selectable legacy behavior,
historical worlds/scenarios/results, original sensor rotation, and
simulation/physical algorithm parity. Keep three-light and physical execution
outside Phase 08, and carry the user-required manual physical `Ctrl+C`
termination policy into the Phase 09 planning boundary.

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

## Phase 08.4 M2 workflow implementation completion

Verified at `2026-07-28T11:03:00-07:00` from committed recorder boundary
`43a27b6`.

The existing `phase08_validation.py` owner is now bounded by an explicit
V3/V4 specification selection. No workflow, runner, recorder, analyzer,
controller, supervisor, fill, launch, or physical owner was duplicated.
The flat V4 CLI exposes all ten planned stages and writes
`workflow_state/v4_<stage>.json`.

Fresh pre-runtime inputs are:

- ten visible-Gazebo activation cases with seeds `10301..10310`;
- ten common, start-pose-rotated headless development cases with seeds
  `10401..10410`;
- the three exact candidate bundles `V4-C0`, `V4-C1`, and `V4-C2`;
- a new first activation contract that predeclares the demonstrated
  fill/escape/recenter-to-goal lifecycle instead of relabeling V3's failed
  direct-only requirement.

The formal suite remains the exact original canonical bytes:

```text
phase08_v3_acceptance_suite.json
  d733ef9dffb372d2c60b57f83c2b96e1062a0a62818587de59a0166df4efe88e
```

`phase_08_v4_population_adoption.json` binds those bytes to the original
cleartext commitment, the terminal V3 gate/manifest hashes, null formal-stage
state hashes, three inspected historical attempt records, and an empty
formal-case overlap. No encryption or GPG key is used.

Input and implementation SHA-256 values:

```text
phase08_validation.py
  53577ac874d35cd48ef057d4faf38eb194a6334f634a826737814c814e0639c8
test_phase08_validation.py
  b32d209e7baa2a005db4f84b61ca9273045ebfa2d7efd27f9a040ea181de08d2
phase08_v4_activation.yaml
  7751a2aa97a0cc53ddc5d18576ea0c0729828687022da81758a9c1a4d974617b
phase08_v4_development.yaml
  c37fb227fb2b75937f473a33ad01ea79e2366ae971f6e6a1c9dfa2d4502d5bbd
phase08_v4_candidates.yaml
  2eb56f3a2a4f57eabb109a842885311c014b61f695ef339d51216c4f779a51df
phase_08_v4_population_adoption.json
  f250cf1877898ed9b2a25078026ec0e8ae7a612d558676a56d5a571fbee8c8e4
```

Validation:

- focused workflow/schema tests: `223 passed in 53.17 s`;
- complete retained functional gate, with writable isolated ROS logs:
  `489 passed, 2 skipped in 86.28 s`;
- the two skips are only the explicit headless/visible Gazebo opt-ins;
- standard three-package build passed in `1 min 31 s`;
- installed V4 activation/development resources and original formal suite are
  present;
- installed activation dry run: schema 4, `10` resolved, `0` unsupported,
  GUI true;
- installed development dry run: schema 4, `10` resolved, `0` unsupported,
  GUI false;
- installed help exposes all ten V4 commands;
- fatal `flake8` (`E9/F63/F7/F82`), `py_compile`, and `git diff --check`
  passed.

The first complete functional invocation used an unwritable default ROS log
location and failed at `rclpy.init`; it left the global context initialized,
causing 20 derivative failures. The identical bounded test command passed
when rerun with `ROS_LOG_DIR` and `ROS_HOME` under `/tmp`. This was an
environment-only correction, not a product-code change.

No V4 evidence root, Gazebo simulation, physical hardware, readiness tag, or
Phase 09 action occurred during M2.

## Current milestone

**M3 — prepare and qualify V4.**

### Next criterion

Commit the exact M2 inputs, require clean Git, transactionally create
`/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4`, then pass the
zero-prior-execution recheck, full functional suite, isolated build, installed
resource/launch/dry-run checks, recorder SIGINT smoke, disk forecast, and
empty process-set gates. Only that passing state may start the ten real GUI
Gazebo activation simulations.

### M3 stop conditions

- No Gazebo dispatch if prepare or qualification is incomplete or failed.
- Do not alter an input captured by the V4 repository snapshot.
- Do not reuse any V3 evidence record as V4 evidence.

### M3 transactional-prepare preflight correction

The first `v4-prepare` invocation at
`2026-07-28T11:08:00-07:00` stopped before publishing the fresh root because
the new transaction path passed unsupported keyword `mode` to the existing
`atomic_json` helper. The staging directory was removed and
`phase08_v4` remained absent.

This bounded workflow-only correction now writes the JSON through the
existing helper and applies mode `0600` to the completed file. A new focused
test proves the root contains both a valid `v4_prepare.json` state and a
hash-valid mode-`0600` transaction. Focused Phase 08 validation tests pass:
`179 passed in 45.39 s`; fatal `flake8`, `py_compile`, and
`git diff --check` pass.

Corrected hashes:

```text
phase08_validation.py
  6d6e8059c89b8c5467c44bcc8082bcc4969404841e5dee0acf585161fa60f284
test_phase08_validation.py
  d4f8304e9d21a0aa7bb34c24533499153e67efbe7cc5e7c367c0b199533f0ae8
```

No evidence root, Gazebo process, simulation slot, hardware action, or
scientific result was created by the failed invocation.

## Phase 08.4 M3 prepare and qualification completion

Verified at `2026-07-28T11:17:00-07:00` from clean implementation commit
`7689f2f55e47a2ecfe38445a936c59d7d3b1be32`.

The fresh V4 evidence root is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4
```

Transactional preparation passed with:

- all `80` formal case identities valid;
- zero overlap with the three inspected historical V3 attempt records;
- unchanged formal suite SHA-256
  `d733ef9dffb372d2c60b57f83c2b96e1062a0a62818587de59a0166df4efe88e`;
- `349045542912` free bytes versus `91268055040` required;
- no active ROS/Gazebo process before preparation;
- clean repository commit/tree and complete runtime-input hash map.

Qualification passed with no reasons:

- retained functional gate: `490 passed, 2 skipped in 86.02 s`;
- isolated three-package build: passed;
- installed truth and V4 resources: passed;
- installed entry point and launch arguments: passed;
- private-context boundary observer smoke: passed;
- bounded supervisor and Gaussian-fill node instantiation: passed with clean
  SIGINT shutdown;
- activation dry run: schema 4, `10` resolved, `0` unsupported, all ten
  direct and recorder launch contracts valid;
- development dry run: schema 4, `10` resolved, `0` unsupported;
- process sets before and after qualification: empty;
- installed real-ROS, no-Gazebo recorder-coordinator SIGINT smoke: passed,
  with no invalid-context exception.

The first standalone M3 recorder-smoke harness used a noncanonical simulation
target and had a quoting defect. `record_run` rejected it before rclpy
initialization, so no run directory or simulation evidence was created. The
corrected installed process-level smoke is retained as
`qualification/recorder_sigint_smoke_v2.json`; the failed harness log remains
retained separately and is not counted as qualification evidence.

Evidence hashes:

```text
workflow_state/v4_prepare.json
  5d9eb740126ca2eb81889c86c46eb7576b411901114fd96c46fb5ad32233c5d2
workflow_state/v4_qualification.json
  52c4247e20acb02e6edf3633f7cf585b288080ef9e61f5afd36e9ca2acc91ce9
prepare/prepare_transaction.json
  fa8913755fa15dbd04473b24133147385e8fcee85dd1e5b530994749fa3fcf4a
qualification/activation_dry_run.yaml
  d7bada78cdebd7d24f45c6c72b87e0a6fc189b160e5a21c7da4131cfff46758c
qualification/development_dry_run.yaml
  840fc9f7a4549b9e05073aedf658cb86f459fc523d78406d89c72c386644f1ce
qualification/logs/recorder_sigint_smoke_v2.log
  f14c5529f9fd9d18609ee77a335f2948a19c007a3df0b7bd20d834fb8b48419e
```

No Gazebo simulation, physical hardware, formal slot, readiness tag, or
Phase 09 action occurred in M3.

## Current milestone

**M4 — execute ten fresh GUI Gazebo activation cases.**

### Next criterion

At clean Git, immediately rehash the passing prepare/qualification states,
repository snapshot, V4 inputs, and dry-run invocation contract; require an
empty process set; then execute the ten V4 activation cases serially with the
Gazebo GUI visible. Retain and analyze each attempt exactly once. Continue to
headless development only if all ten integrity and lifecycle contracts pass.

### M4 stop conditions

- Stop immediately on collision, evidence corruption, cleanup failure,
  ownership/hash drift, orphan process, or replacement-policy breach.
- Finish all ten ordinary valid behavior misses, but do not enter development
  unless activation is `10/10`.
- Do not count any V3 record or failed smoke harness as a V4 activation slot.

## Phase 08.4 original activation stop and Level B diagnosis

The first V4 activation invocation ran from clean commit `90b8c74` against
the qualified root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4
```

It dispatched two real serial simulations with the Gazebo GUI visible.

- `v4a_goal_aggregate_robust` passed all recording, cleanup, controller,
  aggregate-ground-truth, lifecycle, event, collision, and terminal-state
  predicates.
- `v4a_below_target_fill` reached the declared
  `SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE`
  behavior with its required events and clean scenario-runner cleanup, but
  the recorder process was externally terminated with return code `-15`
  before it could replace the initial `run did not finalize` completeness
  record.
- Eight activation cases were not run.

The workflow stopped exactly as required and reports:

```text
passed = false
run_count = 2
integrity_pass_count = 1
contract_pass_count = 1
stopped_early_reason =
  activation.v4a_below_target_fill:
  infrastructure status runner_or_recorder_failure
```

Retained evidence SHA-256 values:

```text
workflow_state/v4_activation.json
  e2690d7610ac1dc16eba643323cc5c6e569e3e7932f905febb79ddb82fcc43c9
activation/progress.json
  abbedda6ec56c257bb24992d1f103afd2f30a91c8f58620e672e7a9c6b61b903
case 1 record.json
  ee4a88d5983b5a6778dc0da11a90156f396e3168a08062252ad658c3fa449576
case 2 record.json
  fa16fb8fc8a81e2e3f83d5faca83462240fe7220c5b80c33b27a5934016e4605
case 2 scenario_summary.yaml
  f09544fcd8ff964e0c8af2f8098df2d0d7ab648f1dff24db40c6226c172594b8
```

Timing evidence isolates the failure:

- boundary SIGINT and orderly recorder shutdown started at
  `2026-07-28T18:22:27Z`;
- Gazebo and rosbag reported stopped by `18:22:34Z`;
- the outer runner's `30 s` cancellation budget expired while the recorder
  was still validating the bag and escalated it to SIGTERM;
- the preceding full-lifecycle case required about `39 s` for that same
  offline validation phase after shutdown.

Read-only re-evaluation of the retained case-2 bag also proved that the named
activation scope excluded the causal `CONVERGENCE_CONFIRMED` event immediately
before `VERIFY_EXTREMUM` and applied the untrimmed path beginning in `SEARCH`.
With the generic scope correction, the retained observations satisfy both
required state-path and event predicates. This diagnostic does not repair,
relabel, or count the incomplete run.

The original root is now immutable `FAILED / INFRASTRUCTURE STOP` and is not
resumed. It is not a scientific behavior failure and no formal case has run.

## Phase 08.4.1 bounded correction

Authority and execution rules are recorded in
`plans/phase_08_4_1_plan.md`.

The existing scenario-runner owner now:

- grants graceful branch-boundary runs a separate bounded `120 s` recorder
  finalization allowance after the `30 s` child-cleanup allowance;
- retains immediate escalation for wall timeouts and exceptions;
- immediately cleans nested-session survivors after the recorder leader exits;
- observes the causal event preceding a named activation anchor;
- evaluates events from the transition into that anchor and clips state
  requirements to the anchor.

Focused verification passes:

```text
test_scenario_runner.py
  41 passed, 1 skipped in 1.91 s

test_scenario_runner.py + test_phase08_validation.py
+ test_experiment_recording.py
  279 passed, 1 skipped in 46.56 s
```

A read-only evaluation of the retained 253 MiB case-2 bag now reports:

```text
anchor_observed = true
boundary_observed = true
required_state_path = true
required_events = true
```

No historical file or external evidence was modified. No formal slot,
development case, physical action, tag, or Phase 09 action occurred.

## Current milestone

**M4.1 — precommit and qualify a fresh corrected V4 activation identity.**

### Next criterion

Create and commit `phase08_v4r2_activation.yaml` with all ten unchanged
activation responsibilities/geometries, new `v4r2a_` identities, and seeds
`10601..10610`; extend the existing V4 spec selector without duplicating its
engine; validate source/build/installed boundary-finalization behavior at
clean Git; then transactionally prepare
`/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2`.

### M4.1 stop conditions

- Do not resume, overwrite, relabel, or count either original V4 attempt.
- Do not change the formal 70+10 population bytes or any acceptance gate.
- Do not start corrected Gazebo activation before clean precommit
  qualification passes.
- Do not enter headless development unless the fresh corrected activation is
  `10/10`.

## Phase 08.4.1 precommit correction and fresh-input completion

The bounded runner and scope corrections, amendment Plan, and fresh corrected
activation input are implemented without changing algorithm behavior.

`phase08_v4r2_activation.yaml` retains every original V4 activation geometry,
source layout, launch override, ground-truth record, lifecycle responsibility,
and predicate. It changes only:

- suite/contract identity from `v4a_` to `v4r2a_`;
- seeds from `10301..10310` to `10601..10610`;
- metadata that identifies the corrected fresh activation gate.

All ten corrected case keys are unique and disjoint from both the original V4
activation cases and the V3 activation/development inputs. The V4 selector
uses the corrected activation input while retaining the existing development,
candidate, workflow, recorder, analyzer, and formal-population owners.

The population-adoption proof is revision 2. It now:

- inspects the two immutable original V4 activation records in addition to the
  three historical V3 records;
- proves all five are disjoint from the formal 80-case population;
- adds the corrected activation suite to the historical-exclusion hash set;
- retains the exact formal suite bytes and all original acceptance counts.

The first mechanical generation of the corrected YAML used an overbroad seed
substring replacement. Static aggregate-truth validation detected altered
digits inside a precomputed truth record before commit, root creation, or
Gazebo execution. The file was regenerated from the untouched original with
seed replacements restricted to complete YAML seed lines. The corrected
static tests then passed.

Current SHA-256 values:

```text
run_scenario.py
  10b86fc3a4a95b5fcd9b539fe19f8b1ef185e55673f5023b5dedb9ec9942cc17
phase08_validation.py
  e02305339d7de7705661d196f485058da6f578bfe538badd7fc3b42530efc120
test_scenario_runner.py
  f5667651e6423a4fe191f7285acc3ec9bf06b249d7899c1ff5661a71fff452c3
test_phase08_validation.py
  2514b1a2768ccbe6c53ef71d0b8c1304cf781a2e2ecf817ad292d200f32ffd2e
phase08_v4r2_activation.yaml
  c0727f48ec39517af1714cac1912c3c216f12d0b9f66e6c383baee7f30d817e1
phase_08_v4_population_adoption.json
  da91b8c791e157e4b4a88e77d4b8b363ac947e40155d9c8645ae1a7a246c91fc
phase_08_4_1_plan.md
  226ea1a48b507a4aeb7aa847b7b43b0852ce0abc7c7647df888954ec95361802
```

Verification:

- focused runner/workflow/recorder gate:
  `279 passed, 1 skipped in 50.44 s`;
- corrected static input and formal-adoption tests:
  `2 passed, 177 deselected in 29.30 s`;
- fatal `flake8`, `py_compile`, and `git diff --check`: passed;
- normal and strict-history Phase 08 implementation context: passed and
  selected `phase_08_4_1_plan.md`.

The context validator and checkpoint helper now sort nested numeric subphase
names correctly, so `phase_08_4_1_plan.md` supersedes its parent
`phase_08_4_plan.md` without renaming either durable artifact.

No corrected evidence root, Gazebo process, formal run, physical action,
readiness tag, or Phase 09 action exists.

## Current milestone

**M4.2 — commit, prepare, and qualify corrected V4.**

### Next criterion

Checkpoint and commit this independently verified correction, require clean
Git, transactionally create
`/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2`, and pass the
complete functional/build/installed/dry-run/process-level qualification
before starting corrected GUI activation.

### M4.2 stop conditions

- No corrected evidence-root creation from a dirty or uncommitted tree.
- No Gazebo dispatch unless corrected prepare and qualification both pass.
- Preserve the original V4 root and all five inspected historical records.

## Phase 08.4.1 first corrected-root qualification stop

Commit `e9c6369` cleanly built and the first corrected root was prepared at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2
```

Preparation passed:

- exact formal suite SHA-256
  `d733ef9dffb372d2c60b57f83c2b96e1062a0a62818587de59a0166df4efe88e`;
- five historical V3/V4 records inspected;
- zero formal-case overlap;
- `348455469056` free bytes versus `91268055040` required;
- clean commit/tree and empty process set.

Qualification then stopped before any Gazebo dispatch:

- retained functional gate: `491 passed, 2 skipped in 88.99 s`;
- isolated three-package build: passed;
- installed aggregate-truth resources: passed;
- installed corrected V4 activation resource: failed;
- process sets before and after: empty.

Root cause: `setup.py` included `phase08_v4_*` through the pattern
`phase08_v[34]_*`, which requires an underscore immediately after `v4`.
It therefore did not package the new `phase08_v4r2_activation.yaml` name.
This is an installed-resource packaging omission, not a source, behavior,
simulation, or formal-population failure.

Retained evidence SHA-256 values:

```text
workflow_state/v4_qualification.json
  ee0ca8b4fbb684f39928cd1b2ae1e3cac363bd0b670a2110be9957637e5ed597
qualification/logs/isolated_build.log
  9e0cdd92fd096f189f6ca899ccf4efcc6c777146cd4f54c8dc542353a9caf854
qualification/logs/installed_v4_resources.log
  09a596a85bd2c6b81ed1c4f1519e29c8f5cdb5b6a1f7e3b5bde6b48fad697970
```

The failed qualification state is immutable. The `phase08_v4r2` root is not
resumed or counted. Because it contains no Gazebo attempt, the exact already
predeclared corrected activation suite remains unobserved and may be used
from a new clean prelaunch root.

The bounded correction explicitly adds
`phase08_v4r2_activation.yaml` to the existing `setup.py` package-data list
and adds a static test for that installed-resource ownership.

Correction verification:

```text
setup.py
  06a61a29d09d3a84130951e6f6d501fe0c00ca53f0d9a331eac1ba96d723fd6f
test_phase08_validation.py
  bbc04ed767ee39b5e3fe034fd246f29717ebbce1f517204274c8a925602ffd72
focused runner/workflow/recorder gate
  279 passed, 1 skipped in 50.17 s
fatal flake8, py_compile, git diff --check
  passed
```

## Current milestone

**M4.2b — checkpoint packaging correction and requalify prelaunch.**

### Next criterion

Pass focused source and packaging checks, checkpoint and commit, build the
installed package, then transactionally prepare and qualify:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2b
```

Only its passing immutable qualification may start the ten corrected visible
Gazebo activation cases.

### M4.2b stop conditions

- Do not alter or resume either `phase08_v4` or `phase08_v4r2`.
- Do not change corrected activation identities, seeds, geometries, or
  contracts after the no-Gazebo qualification failure.
- Do not dispatch Gazebo unless `phase08_v4r2b` qualification passes.

## Phase 08.4.1 corrected-root qualification pass

Commit `54559da` was cleanly and transactionally prepared at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2b
```

Preparation passed with:

- clean commit `54559da7455ff32afa4a9466a9437ff4b7b85552`;
- repository tree `a36307e7f2a163016d493d9030bd2cbc522239c7`;
- runtime-input SHA-256
  `4eb7ad904b5c9713ac1f27f369543d4abc23d498c502b247598bf1ce40164979`;
- exact formal suite SHA-256
  `d733ef9dffb372d2c60b57f83c2b96e1062a0a62818587de59a0166df4efe88e`;
- five prior V3/V4 records inspected and zero formal overlap;
- no active ROS/Gazebo processes.

The fresh immutable qualification passed:

```text
functional tests
  491 passed, 2 skipped in 89.20 s
isolated three-package build
  passed
installed truth and V4 scenario resources
  passed
installed validation entrypoint
  passed
process-level boundary observer smoke
  passed
launch argument introspection
  passed
supervisor and fill graph instantiation
  passed with clean bounded SIGINT shutdown
activation/development installed dry runs
  10/10 resolved, zero unsupported
direct/recorder activation launch contracts
  10/10 and 10/10
processes before/after
  empty / empty
```

Retained qualification SHA-256 values:

```text
workflow_state/v4_prepare.json
  63cc8834fd5ea8aa9ab97606ba68faa04ac4e54aa7a97985c4c502a2b69ee21c
workflow_state/v4_qualification.json
  bdf0646aedc7888c44cbda90d528836c856936704e1fa909c0bbd883ffb745c9
qualification/activation_dry_run.yaml
  e07fbb5f396b1d41a6e5a926ca9b94d63c97e32e2fc1c1a3f9e90cebe178bb47
qualification/development_dry_run.yaml
  ee74e67218f14f8fabb85d5f162de91e708bd5aa8a89c6e3102adfe9ef203627
qualification/logs/isolated_build.log
  126f3a97f7bdce6a8f4af01332bfadcfef9ec72998dc1d8f9c3f955132f072af
```

No Gazebo case has yet run in either corrected root.

## Current milestone

**M4.3 — execute the ten-case corrected visible-Gazebo activation gate.**

### Next criterion

Run all ten `v4r2a_*` cases serially with visible Gazebo and bounded
durations. Preserve every attempt and require a complete `10/10` activation
pass before starting the 30 headless development runs.

### M4.3 stop conditions

- A valid behavioral predicate failure closes V4.1 before development.
- Any integrity, collision, cleanup, hash, ownership, or orphan-process
  failure stops dispatch immediately.
- Do not enter headless development unless corrected activation is `10/10`.

## Phase 08.4 terminal closeout

**V4 CLOSED / FAIL / NOT SIMULATION-READY.**

The corrected visible-Gazebo activation executed one case and stopped before
the remaining nine:

```text
case
  v4r2a_goal_aggregate_robust
seed
  10601
observed path
  SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD
predeclared required path
  SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE
  -> RECENTER -> SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD
```

The run safely reached the aggregate optimum:

- controller goal and simulation ground truth passed;
- nearest aggregate target distance was `0.096979 m`;
- recording, cleanup, collision, final-zero, readiness, and retained
  functional checks passed;
- there were zero fills and zero escape attempts.

Direct convergence is a successful navigation outcome, but it does not prove
the activation slot's declared full recovery lifecycle. `required_state_path`
and `required_events` therefore failed, and the predeclared escape-attempt,
escape-duration, and orbit metrics were unavailable. Analysis correctly
remained partial for that lifecycle responsibility. This is a valid
activation-contract miss, so V4 cannot enter headless development.

Corrected-root terminal counts:

```text
Gazebo runs
  1/120
activation
  1 executed, 9 not_run
development
  0 executed, 30 not_run
holdout
  0 executed, 20 not_run
validation
  0 executed, 50 not_run
reproducibility
  0 executed, 10 not_run
formal unique/repeat denominator entered
  0/70 and 0/10
```

No replacement was eligible or run. The two original V4 attempts and the
zero-Gazebo `phase08_v4r2` packaging failure remain historical failed evidence
and are not counted.

Retained corrected activation SHA-256 values:

```text
workflow_state/v4_activation.json
  ae49b5fc50a1afb189866a07298de2b2f18db872817864ca0012dd66d612273d
activation/records.json
  e3f993c89f694104eb5714fd9e2134063cc1ffccbf1299403f199c9feda0985f
attempt record.json
  563d53a1c312d7ab62dd3fcf2fc4c00ef0d9b8322e2a6fcde82e89cd3d8bea99
attempt scenario_summary.yaml
  6af341a4c68a8e16ecd6375ce7c0040f2596e05574c62f80958ff4b7c06cf777
raw bag
  dbbe74dd961932391a6b5a40e5f6b481a4fbc7568593728695a3ccfd2b966a80
```

The required gate JSON, manifest, validation report, failure report, and V4
handoff were generated. A terminal-report erratum records two generic
V3-label/legacy-prepare diagnostics without changing the correct `FAIL`,
`0/10` activation, or `not_run` later-gate disposition.

## Current milestone

**None — Phase 08.4 V4 is terminally closed.**

### Next criterion

Do not begin V5 automatically. A separately reviewed V5 Plan is required
before any fresh evidence. It should predeclare deterministic branch-forcing
activation responsibilities, or explicitly separate acceptable direct-goal
success from cases that must exercise recovery, without changing the unused
formal population or weakening formal behavior gates.

V4 headless development, freeze, holdout, validation, reproducibility,
readiness tag, Phase 09, and physical hardware remain unauthorized.

## Phase 08.5 V5 authority

The user authorized a fresh V5 on 2026-07-28 with a narrower scientific
objective:

- exclude direct-convergence cases;
- place a lower-intensity local minimum directly between the robot start and
  stronger aggregate/global minimum;
- use exactly two or three lights in every case;
- require Gaussian fill, escape, recenter, resumed search, and final global
  convergence.

The binding Plan is:

```text
docs/codex/gesc_gaussian/plans/phase_08_5_plan.md
```

V5 uses a fresh pre-outcome population rather than the V3/V4 formal suite,
because that older population contains four-light and direct-convergence
responsibilities outside the user's question. All 120 V5 slots must satisfy a
new deterministic route-barrier proof before any V5 Gazebo execution.

Historical V1-V4 code/evidence remains preserved. V5 does not rerun or
reclassify the V4 direct-goal failure.

## Current milestone

**M1 — implement deterministic route-barrier truth and encounter evidence.**

### Next criterion

Inside the existing aggregate-truth, runner, analyzer, and workflow owners:

1. prove every declared local basin exists in the realized authoritative
   field and lies in the start-to-global corridor;
2. bind the proof into aggregate truth;
3. prove at runtime that the first typed fill belongs to that blocker;
4. add focused validation without changing existing V1-V4 behavior.

No V5 evidence root or Gazebo process may exist before the exact fresh V5
inputs and qualification are committed and pass.

## Phase 08.5 M1 route-barrier implementation

The existing aggregate-field owner now derives and validates a deterministic
`route_barrier_qualification` for exactly two or three lights. It:

- requires one strictly strongest declared global source;
- selects an authoritative aggregate target localized at that source;
- proves the designated weaker blocker and its refined local basin lie between
  the start and selected global target inside the fixed route corridor;
- proves the basin remains below the `0.95` goal threshold under declared
  noise;
- proves a conservative positive enclosing-ring depth;
- binds model, source, sensor geometry, route geometry, local basin, ring,
  threshold, and runtime fill-center tolerance into the aggregate result hash.

The existing scenario runner now reads typed `GaussianFill` messages from the
retained readiness interval and exposes the
`route_blocker_encountered` predicate. The first active nonsuperseded fill must
be within `0.35 m` of the precomputed blocker basin. Older scenarios without a
route proof remain unchanged and report this predicate as not applicable.

Schema support rejects unbacked use of the new predicate and requires a
scenario containing a route proof to bind it into acceptance.

Focused verification:

```text
test_aggregate_field_truth.py
+ test_scenario_runner.py
+ test_scenario_schema.py
  97 passed, 1 skipped in 37.23 s

skip
  explicit RUN_GESC_PHASE06_GAZEBO_E2E opt-in

py_compile
  passed
fatal flake8 E9/F63/F7/F82
  passed
git diff --check
  passed
```

The focused two-light fixture proves a `650`-input blocker between a fixed
start and `2500`-input global source. Its refined blocker score is below
threshold and its noise-adjusted ring depth exceeds the fixed `0.015`
minimum. Four-light and off-route inputs are rejected.

No V5 scenario input, evidence root, Gazebo process, physical action, or
formal execution exists.

## Current milestone

**M2 — implement and precommit the fresh V5 workflow and population.**

### Next criterion

Generate and validate the exact ten activation, ten development, three
candidate, 70 unique formal, and ten repeat inputs. Every case must contain
exactly two or three lights, bind a route-barrier proof and blocker-encounter
predicate, and require the full fill/escape/recenter/research/global-goal
lifecycle. Commit all bytes before creating the V5 evidence root.

## Phase 08.5 M2 precommitted population

The existing Phase 08 workflow owner now exposes a separate `phase08-v5`
identity and the bounded `v5-*` command family. V5 does not adopt or relabel
the V3/V4 population. Its exact researcher-visible inputs are:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v5_activation.yaml
  phase08_v5_development.yaml
  phase08_v5_candidates.yaml
  phase08_v5_acceptance_suite.json
docs/codex/gesc_gaussian/validation/
  phase_08_v5_suite_commitment.json
```

The population contains ten visible activation cases, ten shared development
cases executed once per each of three candidates, 20 holdout cases, 50
validation cases, and ten preselected repeats. The 70 unique formal cases have
the Plan-declared family allocation:

```text
20  obstructing two-light collinear
12  obstructing two-light offset
12  obstructing three-light lateral
 8  obstructing three-light sequential-route stress
 8  obstructing wall/corner
10  obstructing noise/delay
```

All cases:

- contain exactly two or three lights;
- declare a strictly stronger global source and a weaker route blocker;
- bind validated aggregate, local-branch, and route-barrier truth;
- require `route_blocker_encountered`;
- require `SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL ->
  ESCAPE_REPULSE -> RECENTER -> SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD`;
- treat direct convergence as a behavioral failure.

Precommit validation passed with no reasons:

```text
activation cases       10
development cases      10
holdout cases          20
validation cases       50
reproducibility cases  10
unique formal cases    70
accepted light counts  2 or 3

suite sha256
  b91d99405a29dc04688a8b6bac66f3344b09a564832077930ed62329587c4515
commitment sha256
  3c9ea5c6679ba2547a643fe3dc394a308cd25fee7f4ffdedd19476a3259670cd

focused regression
  266 passed, 1 skipped in 60.38 s
skip
  explicit RUN_GESC_PHASE06_GAZEBO_E2E opt-in
py_compile
  passed
fatal flake8 E9/F63/F7/F82
  passed
git diff --check
  passed
```

The first full focused regression initially exposed that extending the schema
family vocabulary affected the historical V3 generator iteration and that
future V5 YAML changed the V4 historical scan. Both were corrected without
changing V3/V4 bytes: the V3 generator iterates its own fixed allocation, and
older workflow identities exclude future V5 inputs from their historical
hash scan.

No V5 evidence root, Gazebo process, physical action, or outcome exists yet.

## Current milestone

**M3 — commit the exact V5 inputs, qualify the fresh root, and execute the
ten-case visible Gazebo activation gate.**

### Next criterion

Checkpoint and commit the M2 implementation and exact input bytes. Then create
`/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5`, run the bounded
qualification gate, and execute all ten visible activation cases. Do not start
headless development unless all ten cases complete cleanly and demonstrate the
required blocker fill, escape, recenter, resumed search, and global goal.

## Phase 08.5 M3 prepare and qualification

The exact V5 implementation and input bytes were committed before evidence:

```text
a17518d4429b5496954982178c09af2246ac38e9
phase 08.5: precommit obstructing V5 population
```

Fresh preparation passed at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5
workflow_state/v5_prepare.json
```

The state binds the clean `a17518d` repository snapshot, suite and commitment
hashes, exact 70+10 formal population, all six family counts, no pre-existing
ROS/Gazebo processes, and a free-space forecast of `348087951360` bytes versus
`91268055040` required bytes.

Qualification passed with no reasons:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5/
  workflow_state/v5_qualification.json
  qualification/
```

Evidence includes:

- `494 passed, 2 skipped in 95.90 s`; the skips are the two explicit opt-in
  Gazebo recording integrations;
- an isolated source build and installed V5 resource check;
- installed entrypoint, launch-argument, boundary-observer, supervisor, and
  fill instantiation checks;
- installed dry-run expansion of exactly ten activation and ten development
  cases with zero unsupported cases;
- passive contact launch arguments on both direct and recorder commands for
  all ten activation cases;
- revalidation of the exact V5 population and authoritative route proofs;
- no process leakage after qualification.

No V5 Gazebo outcome exists yet.

## Current milestone

**M3 — execute and inspect the ten-case visible Gazebo activation gate.**

### Next criterion

Commit this qualification checkpoint, then run `v5-activation` with the
qualified isolated install. Preserve all completed evidence on interruption or
failure. Headless development remains forbidden unless activation is exactly
`10/10` infrastructure-complete and `10/10` on the mandatory blocker fill,
escape, recenter, resumed search, and global-goal contract.

## Phase 08.5 M3 prelaunch correction

The first `v5-activation` invocation stopped before dispatch with:

```text
RuntimeError: v3 corrected activation requires adopted recovery
```

This was an orchestration precondition inherited from the V3 recovery engine.
It occurred before `execute_suite`, created no activation state or run
directory, and launched no Gazebo/ROS process. The qualified
`phase08_v5` root is preserved unchanged and is not a behavioral attempt.

The bounded correction adds a distinct fresh-precommit branch to the existing
predispatch verifier. It requires:

- V5 lineage identity in both prepare and qualification;
- exact suite and commitment hashes from the fresh precommit proof;
- all ten installed passive-contact launch contracts;
- the retained installed activation dry-run hash;
- byte-equivalent installed activation invocation projection.

It does not change scenario bytes, parameters, aggregate truth, route proof,
behavior predicates, recording, analysis, controller behavior, or acceptance
gates. Focused compatibility verification passed:

```text
V5 fresh-precommit predispatch
V3C diagnostic-recovery predispatch
V4 population adoption
  3 passed in 23.29 s
py_compile
  passed
fatal flake8 E9/F63/F7/F82
  passed
git diff --check
  passed
```

Because runtime inputs differ from the already qualified snapshot, the
preserved root will not be mutated or executed. The same immutable V5
population will restart after commit and full qualification at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5b
```

No Gazebo outcome exists yet.

## Current milestone

**M3 — qualify the bounded V5B prelaunch correction, then execute the same
ten-case visible Gazebo activation gate.**

### Next criterion

Commit and checkpoint the prelaunch-only correction, prepare and qualify the
fresh V5B root against that commit, and run visible activation. Do not change
or regenerate any V5 scenario input. Headless development remains forbidden
unless visible activation is a strict `10/10` lifecycle pass.

## Phase 08.5 M3 V5B infrastructure stop

V5B preparation and qualification passed against:

```text
e6a21aa9bd167cff4596c719ccb0f83ccb094294
suite sha256
  b91d99405a29dc04688a8b6bac66f3344b09a564832077930ed62329587c4515
qualification
  495 passed, 2 skipped in 94.86 s
```

The first activation slot reached the recorder invocation, but the shell had
only the stale workspace install active. `ros2 run ros_esc record_run` resolved
to `/home/mattb/dsim-lab/ros2_ws/install/ros_esc` and failed before creating a
run directory:

```text
StopIteration
[ros2run]: Process exited with failure 1
```

Cleanup passed, no Gazebo process remained, the workflow stopped immediately,
and the other nine slots were not dispatched. The immutable V5B activation
state is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5b/
  workflow_state/v5_activation.json
  activation/progress.json
  activation/records.json
  activation/scenario_summary.yaml

passed                false
run_count             1
integrity_pass_count  0
contract_pass_count   0
infrastructure        run_directory_missing
```

This is not a Gazebo behavioral result: the recorder failed before launching
its target command, the run directory is absent, and all behavior predicates
are unavailable. The V5B root remains failed and preserved.

The already qualified isolated install was then checked directly:

```text
source .../phase08_v5b/qualification/isolated_build/install/setup.bash
ros2 pkg prefix ros_esc
  .../phase08_v5b/qualification/isolated_build/install/ros_esc
ros2 pkg executables ros_esc
  ros_esc record_run
  ros_esc validate_robustness
ros2 run ros_esc record_run --help
  passed
```

The bounded execution correction is therefore environmental: source the
root's qualified isolated install after the normal workspace overlay before
calling `v5-activation`. It changes no repository byte, input, parameter,
contract, or analysis rule.

## Current milestone

**M3 — run V5C from its own qualified isolated install, then execute the same
ten-case visible Gazebo activation gate.**

### Next criterion

Preserve V5B, prepare and qualify the fresh
`/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5c` root with the unchanged
V5 inputs, source that exact qualification install, and invoke visible
activation. Headless development remains forbidden unless activation is a
strict `10/10` lifecycle pass.

## Phase 08.5 terminal V5C activation

V5C preparation and qualification passed from the root's own isolated install
at tested commit:

```text
034338d1dd87e306bb390c44027791f449f8d7f8
suite sha256
  b91d99405a29dc04688a8b6bac66f3344b09a564832077930ed62329587c4515
commitment sha256
  3c9ea5c6679ba2547a643fe3dc394a308cd25fee7f4ffdedd19476a3259670cd
qualification
  495 passed, 2 skipped in 92.10 s
```

The pass-eligible visible-Gazebo activation executed eight cases at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5c
```

All eight recordings and cleanups completed. All eight failed the mandatory
runtime blocker predicate. First Gaussian fills were `1.2624-1.5782 m` from
the committed route-blocking basin, versus the required maximum of `0.35 m`.
The actual GESC trajectory curved around the statically proven straight-route
basin and first converged elsewhere.

Four runs reached `GOAL_HOLD` and exercised the exact intended state path:

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

This proves the mechanism can execute in Gazebo, but not that it escaped the
intended obstructing local minimum. The other terminal states were two
`SEARCH`, one `VERIFY_EXTREMUM`, and one `FAILSAFE`.

Case `v5a_obstructing_two_light_offset_08_15008` retained a complete recording,
clean shutdown, full lifecycle, and passed controller/global outcomes, but its
analysis was partial because `state_durations` was invalid. That integrity
condition stopped cases 9 and 10.

The Plan required the first behavior-contract failure to stop activation.
The workflow did not enforce that rule on case 1 and continued until case 8's
integrity hard stop. This policy defect is retained honestly. It does not make
any outcome eligible or alter the `0/8` blocker result.

Terminal counts:

```text
visible activation       8 executed, 2 not_run
headless development     0 executed, 30 not_run
headless holdout         0 executed, 20 not_run
headless validation      0 executed, 50 not_run
headless reproducibility 0 executed, 10 not_run
total                    8 executed, 112 not_run
formal unique            0/70
formal repeats           0/10
```

V5 is closed failed and not simulation-ready. No headless stage, readiness tag,
Phase 09 action, or physical hardware run is authorized.

Terminal records:

- `docs/codex/gesc_gaussian/validation/phase_08_v5_gate_results.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v5_run_manifest.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v5_validation_report.md`
- `docs/codex/gesc_gaussian/validation/phase_08_v5_failure_report.md`
- `docs/codex/gesc_gaussian/handoffs/phase_08_5_handoff.md`

## Current milestone

**M10 — terminal closeout complete.**

### Next criterion

Do not resume or modify V5. Any successor requires a separately reviewed Plan
that forces the local basin against the observed GESC trajectory/envelope,
retains the two-/three-light cap and exact recovery responsibility, and fixes
first-contract-miss activation dispatch before Gazebo.

## Phase 08.6 V6 opening

The user authorized a focused two-light Hue-ratio development demonstration
instead of V5's formal 120-run acceptance design. The binding Plan is:

```text
docs/codex/gesc_gaussian/plans/phase_08_6_plan.md
```

V6 preserves Nick's original GESC and full-rotation photoresistor behavior.
The wrapper's ordinary `init_yaw_angle=0`, encoder input, and constant
full-rotation profile remain unchanged. No outcome-selected orientation,
steering aid, duplicate controller, or physical command is authorized.

The fixed `4 m x 4 m` geometry is:

```text
start   (-1.30, -0.20) m, yaw 0
local   (-0.80,  0.00) m
global  ( 1.30,  0.80) m
```

The four visible-Gazebo development ratios are:

```text
H25  local 25% / 400 nominal, global 100% / 1600 nominal
H50  local 50% / 800 nominal, global 100% / 1600 nominal
H70  local 70% / 1120 nominal, global 100% / 1600 nominal
H85  local 85% / 1360 nominal, global 100% / 1600 nominal
```

The simulator lumen value is retained as a relative model input; Hue percentage
and nominal lumens are recorded separately and are not claimed as a physical
lux calibration.

Primary success is:

```text
SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE
-> RECENTER -> SEARCH
```

The runtime must bind the first fill to a confirmed nonglobal convergence near
the declared local source and away from the global source. Global convergence
after resumed search is secondary. Wall/corner, noise/delay, assist, merge,
revisit, three-light, 70/70, and 120-run requirements are deferred.

Fresh external root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v6
```

The root is not created until the exact scenario and implementation are
committed and qualification begins.

## Current milestone

**M3 — terminal closeout complete.**

### Next criterion

Do not start the 120-run matrix or relabel V6. A successor Plan must choose
prospectively between a first-recovery-episode claim and full-record
multi-cycle stability, then diagnose only the behavior required by that claim.

## Phase 08.6 M1 implementation and qualification

Implemented inside the existing scenario schema and runner:

- optional schema-v3-or-newer `success.local_recovery`;
- required `observed_local_recovery` predicate backing;
- causal matching of the first active typed fill to its
  `CONVERGENCE_CONFIRMED` source timestamp;
- retained convergence-to-local, convergence-to-global, and
  fill-to-convergence distances;
- explicit behavioral failure for no active fill or no matching convergence,
  while malformed/nonfinite evidence remains an integrity error.

The exact visible suite is:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v6_hue_sweep.yaml
sha256 3be130581b88c986fd845aef0c33c9db94ceb02ecfe2a6361926b0317ef8e655
```

The commitment is retained at:

```text
docs/codex/gesc_gaussian/validation/phase_08_v6_sweep_commitment.json
```

Qualification:

- Python compilation: PASS.
- Focused schema and runner tests:
  `89 passed, 1 skipped in 11.85s`.
- Isolated `ros_esc` build:
  PASS in `1.70s`; logs at `/tmp/phase08_v6_colcon_log`.
- Installed-resource `run_scenario --dry-run --gui`:
  PASS; four serial runs, zero unsupported.
- Dry-run launch resolution confirms `init_yaw_angle:=0.0`,
  `number_of_lights:=2`, `modified_cost_enable_affine_bias:=False`,
  validation-world contacts, fixed geometry, and the four exact intensities.
- No Gazebo/ROS scenario descendant was active and the V6 root remained absent
  at qualification.

## Phase 08.6 M2 visible sweep and selection

The committed visible sweep executed all four cases from
`2026-07-29T01:20:23Z` to `2026-07-29T01:44:54Z`. All four recordings,
cleanups, and collision checks completed and passed. Retained summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v6/
  phase08_v6_hue_sweep_summary.yaml
```

Behavior:

- H25: complete local convergence, fill, escape, recenter, resumed search,
  and secondary global goal.
- H50: local fill created, then `ESCAPE_STALLED`, `FILL_REJECTED`, and
  `FAILSAFE`; failed.
- H70: entered `GOAL_HOLD` at the local convergence without a fill; failed.
- H85: completed an initial recovery, but later `FILL_REJECTED` and
  `FAILSAFE`; failed the no-failure contract.

The sweep exposed a bounded evidence-binding bug: the first implementation
required the convergence source timestamp to equal the later fill-design
source timestamp. H25 actually converged at `84.7 s` and created the typed fill
at `93.8 s`; their centers were only `0.0140 m` apart. The correction selects
the latest valid `CONVERGENCE_CONFIRMED` event preceding the first active fill
and retains all three committed distance thresholds unchanged.

Corrected bag analysis identifies H25 as the only eligible ratio:

```text
convergence to local:  0.3701 m <= 0.60 m
convergence to global: 1.8836 m >= 0.75 m
fill to convergence:   0.0140 m <= 0.50 m
```

Selection and frozen repeats:

```text
docs/codex/gesc_gaussian/validation/phase_08_v6_selection.json
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v6_selected_repeats.yaml
repeat sha256 3b9badc92cf63739f65662158999e3c2aab71761f790e3f360be9a52e6f38688
seeds 17101, 17102, 17103
```

The post-correction focused regression is
`89 passed, 1 skipped in 12.93s`.

## Phase 08.6 M3 repeats and terminal result

The three headless H25 repeats ran from `2026-07-29T01:48:39Z` through
`2026-07-29T02:06:44Z`. All recordings, cleanups, and collision checks passed.

```text
17101 full contract PASS
17102 full contract FAIL — convergence/fill at global, then FAILSAFE
17103 full contract FAIL — local recovery completed, later FILL_REJECTED/FAILSAFE
```

Fixed repeatability gate: `1/3`, below `2/3`.

The requested first local-recovery episode occurred in `2/3` repeats, including
17103, but V6's full-record forbidden-state/event contract makes 17103 a fixed
failure. This distinction is retained and V6 is not weakened after execution.

Across all seven V6 Gazebo executions, the full local convergence/fill/escape/
recenter/resumed-search mechanism occurred four times. Two of those later
failed a subsequent cycle. V6 therefore proves the mechanism can work but does
not prove the stability needed for a 120-run campaign.

Terminal artifacts:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v6/
  phase08_v6_hue_sweep_summary.yaml
  phase08_v6_selected_repeats_summary.yaml
docs/codex/gesc_gaussian/validation/phase_08_v6_validation_report.md
docs/codex/gesc_gaussian/validation/phase_08_v6_failure_report.md
docs/codex/gesc_gaussian/handoffs/phase_08_6_handoff.md
```

No ROS/Gazebo descendants remained after the final cleanup. External evidence
size at closeout was approximately `1.8 GiB`.

## Phase 08.7 Plan-only geometry contract

The user approved a successor geometry contract on 2026-07-29. It is saved at:

```text
docs/codex/gesc_gaussian/plans/phase_08_7_plan.md
```

V6 remains closed and unchanged. Phase 08.7 is Plan-only; no new world,
scenario implementation, Gazebo run, or evidence root is authorized yet.

Approved geometry:

```text
room bounds: x,y in [-0.25, 3.75] m
robot start: (0.0, 0.0) m, yaw 0
global:      (3.5, 3.5) m
local:       radius 1.0-2.0 m
             angle 0-90 degrees
             equivalently +/-45 degrees around the 45-degree diagonal
new wall margin: 0.20 m
```

The current centered validation world cannot implement these bounds merely by
changing scenario values. The successor implementation must add a separate
shifted world while preserving the historical world and case identities.

### Phase 08.7 next criterion

Review the complete Plan and explicitly authorize implementation. Execution
remains separately paused.

## Phase 08.7 two-stage and known-topology amendment

The user approved a two-stage result contract and explicitly allowed the
algorithm to know the number of local and global minima:

```text
Stage A: complete every declared local convergence/fill/escape/recenter episode
Stage B: after Stage A, enter the global's committed proximity radius
Combined: Stage A + Stage B + exact fill count + infrastructure evidence
```

Fill count is defined by unique accepted typed fill clusters, not raw topic
message count:

```text
1 local + 1 global -> exactly 1 unique local fill, max_fills=1
2 locals + 1 global -> exactly 2 unique local fills, max_fills=2
```

Each fill must be associated one-to-one with a different declared local
source. A global fill, missing fill, extra fill, or shared cluster fails the
cardinality contract. Revisions and repeated publications do not add fills.

Stage B now requires only a valid post-Stage-A odometry sample within `0.35 m`
of `(3.5,3.5)`. That sample triggers a graceful simulation stop equivalent to
the user's allowed physical `Ctrl+C`. `GOAL_REACHED`, `GOAL_HOLD`, dwell,
stationary observation, and post-arrival behavior are not behavioral gates.
Stage A remains reported independently if Stage B fails, while the combined
run still fails. Existing final-zero, final-readiness-false, completeness,
cleanup, and collision evidence remain infrastructure requirements.

## Phase 08.7 M1 implementation and qualification

M1 started from clean HEAD
`970bdc02047aa7da9c3f94616c723ba8e6842206` on
`feature/gesc-gaussian-robustness-v1`, ahead of its remote by 50 commits.
`validate_phase_context.sh 08 implement` from
`DSIM_GESC_Gaussian_Codex_Implementation_Package/tools` passed before editing
and selected `phase_08_7_plan.md`. The prior checkpoint was the intentionally
precommit Plan-amendment snapshot based on `e6ba847`; this M1 boundary
refreshes it without reopening or relabeling V6.

Implemented additively:

- new world
  `turtlebot3_rotating_sensor/worlds/gesc_gaussian_corner_origin_validation.world`;
- exact inner wall faces `x,y = -0.25, 3.75 m`, corresponding wall
  centerlines `-0.30, 3.80 m`, and orthogonal center `1.75 m`;
- schema-v5 geometry profile `corner_origin_diagonal_sector_v1` with fixed
  start `(0,0,0)`, fixed global `(3.5,3.5)`, inclusive local radius
  `1.0-2.0 m`, inclusive local angle `0-90 degrees`, wall margin `0.20 m`,
  contacts, and recorded local polar metadata;
- a prospective two-light known-topology contract declaring one local and one
  global minimum and requiring `gaussian_fill_max_fills=1`;
- typed fill cardinality based on unique accepted `FILL_CREATED`
  cluster/revision identity, with repeated publications and merges excluded
  from the count and one-to-one spatial association to declared locals;
- independent Stage A local-recovery, Stage B post-recovery global-proximity,
  fill-cardinality, and combined result records;
- the exact Stage A path
  `SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE
  -> RECENTER -> SEARCH`;
- first finite recorded post-Stage-A odometry sample within `0.35 m` of the
  declared global as the Stage B boundary, followed by scoped `SIGINT` through
  the existing recorder process and its unchanged final-zero,
  readiness-false, completeness, and cleanup path.

No scenario suite, evidence root, algorithm fork, controller, launch graph,
recorder, validator, or analyzer was added. `custom_controller` ownership and
all legacy selection paths remain unchanged. The historical validation world
remains byte-identical at
`8ecc1a231efec24401d74fef3cd5139d48c6029f88e71d044cefdf2fd14c5bef`.
The new world SHA-256 is
`88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf`.

Historical preservation is sealed in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m1_historical_immutability.json
```

It binds all 29 pre-M1 scenario/config source hashes, the old-world hash, and
22 loadable schema-v1-through-v4 normalized case-key and launch-argv digests.
The manifest separately retains the pre-M1
`phase08_v5_acceptance_suite.json` aggregate-truth hash-drift expansion
failure; M1 did not rewrite that historical artifact.

### M1 qualification evidence

All commands were bounded and no behavioral launch was performed.

- Final milestone-owned tests, from `ros2_ws/src/ros_esc` with the isolated
  overlay sourced:

  ```text
  timeout 180s env -u RUN_GAZEBO_E2E -u RUN_ROS_INTEGRATION \
    python3 -m pytest -q \
    test/test_scenario_schema.py test/test_scenario_runner.py
  ```

  Result: `107 passed, 1 skipped in 45.70s`. The skip is the explicit
  `RUN_GESC_PHASE06_GAZEBO_E2E=1` recorded headless-Gazebo integration.

- Focused recording, bag, legacy, and Phase-08 regressions:

  ```text
  timeout 300s env -u RUN_GAZEBO_E2E -u RUN_ROS_INTEGRATION \
    python3 -m pytest -q \
    test/test_experiment_recording.py \
    test/test_recording_integration.py \
    test/test_bag_analysis.py \
    test/test_legacy_behavior.py \
    test/test_phase08_validation.py \
    -k 'not v4_population_adoption_is_exact_and_unused'
  ```

  Result: `282 passed, 1 skipped, 1 deselected in 29.25s`. The skip is the
  explicit `DSIM_RUN_GAZEBO_RECORDING_TEST=1` visible-Gazebo smoke.

- The same broad set plus the two M1-owned files, before the one historical
  deselection, produced `389 passed, 2 skipped, 1 failed in 99.27s`. The sole
  failure was the unchanged
  `test_v4_population_adoption_is_exact_and_unused`: its V4 adoption proof
  now sees the later
  `phase08_v6_hue_sweep.yaml` and
  `phase08_v6_selected_repeats.yaml` as two additional historical files.
  Both files and the historical validator are present at base HEAD and have
  zero M1 diff. Direct diagnostic output was
  `reasons=["v4 historical exclusion hashes drifted"]`,
  `expected_only=[]`, `actual_only=[the two V6 files]`, and
  `hash_drift=[]`. This is retained as a pre-existing stale V4 test
  expectation, not hidden or weakened by changing V6.

- One initial broader invocation omitted the isolated overlay and stopped
  during collection with
  `ModuleNotFoundError: No module named 'ros_esc_interfaces'`; it ran no test,
  ROS, or Gazebo process. The identical sourced rerun produced the results
  above. An earlier targeted development selection exposed three
  test-fixture expectation mismatches; those test-only fixtures were
  corrected before the final 107-test qualification.

- `ament_flake8` on the five changed Python/setup files: PASS,
  `5 files checked`, no problems.
- `ament_pep257` on the four changed Python/test modules: PASS.
- bounded `python3 -m compileall -q` on the changed modules/tests: PASS.
- final `validate_phase_context.sh 08 implement`: PASS; active subphase
  `phase_08_7_plan.md`.
- isolated build:

  ```text
  timeout 420s colcon \
    --log-base /tmp/phase08_7_m1_colcon_log build \
    --base-paths src \
    --build-base /tmp/phase08_7_m1_build \
    --install-base /tmp/phase08_7_m1_install \
    --packages-select ros_esc_interfaces ros_esc \
      turtlebot3_rotating_sensor \
    --event-handlers console_cohesion+
  ```

  Result: `3 packages finished in 1.67s`. Final installed
  `run_scenario.py`, `scenario_schema.py`, and shifted-world hashes exactly
  match their source files.

- Non-executing installed launch instantiation:

  ```text
  timeout 60s ros2 launch -p turtlebot3_rotating_sensor \
    gazebo.launch.xml \
    gazebo_gui:=False \
    gazebo_world:=/tmp/phase08_7_m1_install/turtlebot3_rotating_sensor/share/turtlebot3_rotating_sensor/worlds/gesc_gaussian_corner_origin_validation.world \
    algorithm_profile:=robust_gaussian_v1 \
    init_x_position:=0.0 init_y_position:=0.0 init_yaw_angle:=0.0 \
    number_of_lights:=2 \
    light_1_x:=1.0606601717798212 \
    light_1_y:=1.0606601717798212 \
    light_1_intensity_lumens:=400.0 \
    light_2_x:=3.5 light_2_y:=3.5 \
    light_2_intensity_lumens:=1600.0 \
    room_bounds_x_min_m:=-0.25 room_bounds_x_max_m:=3.75 \
    room_bounds_y_min_m:=-0.25 room_bounds_y_max_m:=3.75 \
    room_center_x_m:=1.75 room_center_y_m:=1.75 \
    wall_margin_m:=0.2 gaussian_fill_max_fills:=1 \
    escape_policy:=conditional_gaussian_fill \
    recenter_after_escape:=True \
    simulation_contacts_enabled:=True \
    recording_ready_required:=True
  ```

  Result: PASS, 248-line launch description retained at
  `/tmp/phase08_7_m1_launch_description.txt`. XML parsing of source and
  installed worlds passed. Installed `ros2 run ros_esc run_scenario --help`
  passed. `git diff --check` passed.

Qualification verdict: **M1 PASS**. No Gazebo server/client, scenario run,
physical-hardware process, or Phase 08.7 evidence root was started or created.
This is implementation qualification only, not behavioral acceptance,
simulation readiness, or a change to V6's terminal failure.

`checkpoint_phase.sh 08` completed at the material M1 boundary and refreshed
`docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt` against base
HEAD `970bdc02047aa7da9c3f94616c723ba8e6842206`.

## Current milestone

**Phase 08.7 M1 — qualified; implementation checkpoint boundary.**

### Next criterion

Keep execution paused. M2 requires separate explicit approval before committing
a fresh scenario or starting the one bounded visible-Gazebo geometry probe.

## Phase 08.7 M2 pre-execution freeze and qualification

The user explicitly authorized M2 execution after the clean M1 commit:

```text
7c87e5a9d8b486bdb0cb465d3e392d78ccc3959b
phase 08.7: qualify corner-origin M1
```

M2 began from that clean HEAD, branch ahead of its remote by 51 commits.
`validate_phase_context.sh 08 implement` passed, `DISPLAY=:0` was available,
approximately `320 GiB` was free, the fresh M2 evidence root was absent, and
no runner, recorder, Gazebo server/client, or physical-hardware process was
active.

The committed-before-execution development probe is:

```text
suite:       phase08_v7_m2_geometry_probe
case:        v7_m2_diagonal_r1p5_h25_18001
case key:    d07a23d9a77f938038fbe58c5d2b312dd5e550394d4f60c56d22d6ead8ca2961
seed:        18001
start:       (0.0, 0.0), yaw 0
local:       (1.0606601717798212, 1.0606601717798212)
local polar: radius 1.5 m, angle 45 degrees
inputs:      local 400.0, global 1600.0 nominal relative lumens
global:      (3.5, 3.5)
topology:    1 local, 1 global, max_fills=1
presentation: visible Gazebo GUI
run count:   exactly 1
```

Scenario:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v7_m2_geometry_probe.yaml
sha256 9623b001d91a1216d35c037c2eeb46d4a0f05cdf46d3b3ea68c2b4ad7a0af442
```

The Plan now contains the exact M2 execution amendment. The diagonal midpoint
was selected from the Plan's prospective examples before any corner-origin
Gazebo outcome. H25 is a development diagnostic carried from V6 and cannot
tune, select, or count toward M3. V6 remains closed and unchanged.

Pre-execution qualification:

- strict schema load and deterministic expansion: PASS, one supported run;
  resolved radius `1.4999999999999998 m`, angle `45 degrees`, and the exact
  case key above;
- the first read-only qualification script used exact floating equality for
  derived radius/angle and raised `AssertionError`; its immediate
  tolerance-aware rerun passed without changing the scenario;
- focused schema/runner regression:
  `107 passed, 1 skipped in 46.23s`; the skip is the explicitly gated
  recorded headless-Gazebo integration;
- fresh isolated build:
  `3 packages finished in 11.5s`; logs under
  `/tmp/phase08_7_m2_colcon_log`;
- source and installed scenario hashes match; source and installed shifted
  world hashes match;
- XML/SDF wall-pose qualification: PASS for wall centerlines
  `(-0.30, 3.80)` and inner faces `(-0.25, 3.75)` on both axes;
- installed `run_scenario --gui --dry-run`: PASS, one resolved run, zero
  unsupported, 70 launch arguments, and 89 recorder arguments;
- dry-run launch resolution binds GUI, seed 18001, zero-yaw corner start,
  exactly two lights at the frozen coordinates, shifted bounds/center,
  wall margin `0.20`, contacts, no affine assist, and
  `gaussian_fill_max_fills=1`;
- dry-run summary:
  `/tmp/phase08_7_m2_dry_run.yaml`;
- `git diff --check`: PASS;
- the external M2 evidence root remained absent and no ROS/Gazebo process was
  started by qualification.

The pre-execution material boundary is checkpointed before the scenario is
committed. No automatic retry is authorized. Runtime geometry/infrastructure
and Stage A/Stage B behavior remain separate results.

## Current milestone

**Phase 08.7 M2 — frozen case qualified; one visible probe authorized.**

### Next criterion

Commit the exact Plan amendment, scenario, live status, and checkpoint. Verify
the clean commit and unchanged installed scenario hash, then dispatch exactly
one bounded visible-Gazebo run to the fresh M2 evidence root.

## Phase 08.7 M2 execution and result

The pre-execution case, Plan amendment, status, and checkpoint were committed
cleanly at:

```text
a8b9d97031c44f4557936c2e24143da2d183c431
phase 08.7: freeze M2 geometry probe
```

The installed scenario SHA-256 still matched the frozen source. From that
clean boundary, the one authorized M2 attempt was dispatched once with the
visible Gazebo GUI and no retry:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m2_install/setup.bash
ROS_DOMAIN_ID=88
ROS_LOG_DIR=/tmp/phase08_7_m2_probe_ros_logs
MPLCONFIGDIR=/tmp/phase08_7_m2_probe_mpl
TURTLEBOT3_MODEL=burger
DISPLAY=:0
timeout --signal=INT --kill-after=60s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m2_install/ros_esc/share/ros_esc/scenario_runner/scenarios/phase08_v7_m2_geometry_probe.yaml \
  --operator phase08_7_m2 \
  --case-id v7_m2_diagonal_r1p5_h25_18001 \
  --runs-root /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2 \
  --summary-output /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2/phase08_v7_m2_geometry_probe_summary.yaml \
  --gui
```

The outer runner returned `1` for failed behavioral classification. The
recorder returned `0`, did not time out, retained a complete run, and passed
cleanup:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2/
  2026-07-29/
  20260729T220933564961Z_simulation_phase08_v7_m2_geometry_probe-
  v7_m2_diagonal_r1p5_h25_18001-robust_gaussian_v1-d0_3ad17fc6
```

Suite summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2/
  phase08_v7_m2_geometry_probe_summary.yaml
```

### Geometry and infrastructure: PASS

- Runtime `/get_model_list` plus read-only native Gazebo pose queries observed
  wall centerlines at east `3.80`, west `-0.30`, north `3.80`, and south
  `-0.30 m`, with orthogonal centers at `1.75 m`. These establish the frozen
  inner faces at `-0.25` and `3.75 m`.
- Runtime light poses were local `(1.06066, 1.06066)` and global
  `(3.50, 3.50) m`.
- The first readiness odometry pose was
  `(0.000352821454192, 0.000458412508747) m`, verifying the corner-origin
  spawn within settling error.
- The contacts topic had the declared type, two Gazebo contact publishers,
  and the rosbag recorder subscriber. The bag retained `71,918` contact
  messages, collision evidence was available, and no non-ground collision was
  observed.
- `/cmd_vel` had one publisher, `custom_controller`.
- `classification.infrastructure_status` is `completed`;
  `recording_complete=true`; cleanup passed with no remaining new nodes or
  session processes.
- `completeness.json` passed with no failures or warnings; all three final
  command streams were zero and final readiness was false.
- `timeout 180s ros2 run ros_esc validate_run <run_dir>` returned `0` and
  passed with no failures or warnings.
- The `sqlite3` CLI was unavailable. Its read-only Python `sqlite3` fallback
  ran `PRAGMA quick_check` on `bag/bag_0.db3` and returned `ok`.
- Final process inspection found no Gazebo server/client, scenario runner,
  recorder, ROS bag recorder, or physical-hardware process.

The preferred `/gazebo/model_states` topic was absent. Its read-only query
failed without mutating or interrupting the attempt; the available model-list
service and native Gazebo pose query supplied the live geometry evidence.

### Staged behavior

**Stage A local recovery: PASS.** One episode completed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

The final resumed-SEARCH stamp is `1785363195303143037`. One unique accepted
typed active cluster, id `1`, was associated with the local:

```text
fill center:              (1.2239058490, 1.4353952912) m
convergence point:        (1.3282657490, 1.3428301900) m
fill-to-convergence:      0.1394965472 m <= 0.50 m
convergence-to-local:     0.3888864411 m <= 0.60 m
convergence-to-global:    3.0610147413 m >= 0.75 m
```

**Exact fill cardinality: PASS.** Created, typed, and active cluster sets were
all exactly `{1}`.

**Stage B global proximity: FAIL.** All `4,268` finite post-Stage-A odometry
samples were checked without interpolation. None entered the required
`0.35 m` radius. The closest was
`(1.9883714796, 1.8959068678) m`, `2.2041178645 m` from the global, at
motion time `360.054148057 s`; the graceful global-proximity stop therefore
did not trigger.

The later sequence was
`SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> FAILSAFE`, with
`FILL_REJECTED` followed by `FAILSAFE`. The no-forbidden-state/event
predicates failed. The combined behavioral result is therefore **FAIL** while
the independent Stage A result remains **PASS**.

### Retained offline evidence

The standard bounded `analyze_run` command completed from the retained bag
with exit code `0` and wrote eight plots, eleven tables, metrics, and
analysis-completeness evidence under `<run_dir>/analysis`. It reports
`analysis_status=partial`, one fill, one successful escape attempt, no
collision, controller success false, and terminal `FAILSAFE`. Fresh embedded
Phase 05 validation passed. The partial status retains one invalid
state-duration gap and unavailable generic aggregate-target metrics; it is not
relabeled as complete.

Full command, runtime evidence, hashes, and interpretation:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m2_geometry_probe_report.md
```

Key immutable evidence SHA-256 values:

```text
389aa07e84a56bb5210071de5f1e82aef9b59536dfc5685e157dea810c26ba04  suite summary
0f5773d92f6a7d318749f9e8182f26cd0294721d0d5ad78adf9a53efa376feeb  scenario_result.yaml
6300173abb17a9e1227e8761d7412da571775501efa5fa6842c4ba560ca9b13e  completeness.json
a590764b29dc824bbabbbf4a342ec3d0bac599e220d5d363ff4cd4e05c1de457  bag/bag_0.db3
63664e5be15556ffdc5d15a8bc68654bc6b7b43668f552ed2bfcf9bd796fb310  analysis/summary_metrics.json
171be0671ca2013f7126fac8b367ba786493fc8d639b1cbd2cb3a41ee174d125  analysis/analysis_completeness.json
```

Post-run repository qualification:

- `validate_phase_context.sh 08 implement`: PASS with active subphase
  `phase_08_7_plan.md`;
- the first context-validation invocation used the nonexistent
  `ros2_ws/src/ros_esc/tools/` path and returned `127` without changing the
  workspace; the immediate invocation through
  `DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/` passed;
- focused shifted-world plus historical scenario/world immutability tests:
  `2 passed, 58 deselected in 35.05s`;
- `git diff --check`: PASS.

M2 execution did not change algorithm code, the shifted world, V6, or any
historical scenario/evidence. This one development attempt neither counts
toward a fixed suite nor establishes simulation readiness.

## Current milestone

**Phase 08.7 M2 — executed and retained. Geometry/infrastructure, Stage A,
and fill cardinality passed; Stage B and the combined behavioral contract
failed.**

### Next criterion

Stop at the M2 checkpoint. M3 remains unauthorized, and its Plan prerequisite
has not been established by this combined M2 result. Await explicit user
direction before any new scenario, tuning, retry, or Gazebo execution.

## Phase 08.7 M2.1 authorization and correction boundary

The user authorized the complete bounded correction on 2026-07-29 after review
of the retained M2 diagnosis. M2 remains immutable at commit `7d02fb6`; its
Stage B and combined failures are not reopened, retried, or relabeled.

Live recovery began from a clean
`feature/gesc-gaussian-robustness-v1` worktree, ahead of its remote by 53
commits. The active HEAD was `7d02fb6`. No ROS/Gazebo scenario process was
running. The required context command passed:

```text
timeout 60s bash \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/\
  validate_phase_context.sh 08 implement

Active subphase plan: docs/codex/gesc_gaussian/plans/phase_08_7_plan.md
Phase 08 implement context is complete.
```

The approved M2.1 amendment is now durable in
`plans/phase_08_7_plan.md`. It requires opt-in robust SEARCH-epoch convergence
gating, fresh-history reset, motion/orbit qualification, topology-aware
low-score recovery without a second fill, bounded post-recenter affine
guidance, three recoverable retries, and a fresh `0.60 m` operator-equivalent
Stage B stop. Legacy, V6, historical scenarios/worlds/evidence, cost semantics,
topics, controller ownership, exact one-fill cardinality, and final-zero remain
unchanged.

**Current milestone: Phase 08.7 M2.1 implementation and no-Gazebo
qualification.**

No Gazebo execution is permitted until the amendment's focused, replay,
legacy/V6, launch-instantiation, context, diff, status, and checkpoint gates
all pass and the exact new scenario input is committed.

## Phase 08.7 M2.1 no-Gazebo qualification

The bounded correction is implemented in the existing detector, supervisor,
modified-cost, central-launch, scenario, and test owners. The new behavior is
opt-in; all new launch defaults preserve legacy and historical robust
selection:

- the convergence detector consumes typed state only when its new robust
  SEARCH gate is enabled, resets at SEARCH boundaries, waits for fresh
  history, and requires the frozen `0.20 m` path and `0.35` maximum path
  efficiency;
- the supervisor treats the known one-fill limit as topology exhaustion,
  retains the accepted fill, resumes SEARCH without another fill request, and
  allows three bounded low-score retries before an honest failsafe;
- post-recenter SEARCH publishes the existing safe direction and weights
  `(1, 1, 1)` for at most `60.0 s`; the existing modified-cost owner accepts
  that typed SEARCH authorization and clears the affine term when the typed
  weight or state no longer authorizes it;
- the scenario schema retains the historical schema-v5 `0.35 m` contract and
  allows the new `0.60 m` stop only for the explicit post-recovery correction;
- the scenario runner's existing first-valid-sample graceful-stop mechanism is
  unchanged.

### Focused and regression evidence

All required no-Gazebo behavior gates passed:

```text
convergence detector policy:
  5 passed in 0.26s

detector plus state-machine focus:
  42 passed

new supervisor integration focus:
  5 passed, 3 deselected

retained-M2 topology replay:
  2 passed, 7 deselected

new detector/supervisor/schema/runner selection:
  31 passed, 155 deselected

owned detector/supervisor/scenario/legacy/observability/recording suite:
  269 passed, 1 skipped in 52.25s

M1 recording/bag/legacy/Phase-08 regression:
  282 passed, 1 skipped, 1 deselected in 29.02s

full scenario-schema and runner regression:
  112 passed, 1 skipped in 46.08s

detector/state-machine/supervisor/observability focus:
  67 passed in 3.55s
```

The skips are the repository's explicitly gated Gazebo integration tests; no
runtime process was started by these commands. The historical scenario tests
recomputed their existing case keys and passed. No V6 file, historical
scenario, shifted-world file, interface, recorder, validator, topic, cost
sign/unit, or controller owner is changed.

The new detector-policy test passes both `ament_flake8` and `ament_pep257`.
Running whole-file `ament_flake8` across the historically nonconforming owners
reported `931` style-only findings (`886 Q`, `34 D`, and `11 I`). That inherited
formatting baseline is not relabeled as a pass. The fatal Python selection
`E9,F63,F7,F82` passes across every changed Python source and test, and
`compileall` plus `git diff --check` pass.

### Build and launch qualification

The normal workspace build passed:

```text
colcon --log-base /tmp/phase08_7_m2_1_build_logs build \
  --packages-select ros_esc_interfaces ros_esc \
  turtlebot3_rotating_sensor

Summary: 3 packages finished in 3.79s
```

A clean isolated source build also passed:

```text
build base:   /tmp/phase08_7_m2_1_qual/build
install base: /tmp/phase08_7_m2_1_qual/install
log base:     /tmp/phase08_7_m2_1_qual/log
Summary: 3 packages finished in 11.7s
```

The isolated installed scenario dry-run resolved one supported run, zero
unsupported runs, the frozen case key
`2db8a5e49c8068373c22c621be13506419f9f2d7364ec50274f9f7d9895840eb`,
and `75` launch arguments. It bound the frozen geometry, one-fill limit,
typed detector gate, path qualification, three retries, affine gain and age,
visible GUI, and both `0.60 m` stop radii. Its summary is retained at
`/tmp/phase08_7_m2_1_dry_run.yaml`.

Nonexecuting `ros2 launch -p` instantiation produced the expected `254`-line
description at `/tmp/phase08_7_m2_1_launch_description.txt`. Separate bounded
three-second supervisor, detector, and modified-cost node instantiations
reached their expected outer timeout `124` after clean startup with the exact
new parameter types and values; none produced an application error.

Source and isolated-install identities match:

```text
541194d6152a8384c469f5bcc8573aef9afdb295bde6e148e5a82a692b8e4c8b  scenario
9277b63743c7672268721c50b414020fc5951d719f358fd053d5f86d0b06e49c  central launch
7820407ddea144e98cc1c30b1a4ee071861c153d887e324b7ee258db1a3a5182  detector
```

The required Phase 08 context validator passes from the active Phase 08.7
plan. `DISPLAY=:0` is available, the external evidence root
`/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_1` remains absent,
and no Gazebo, scenario-runner, recorder, or physical-hardware process is
running.

Development-only corrections made before this qualified boundary are retained
honestly:

- the first pytest discovery omitted the installed overlay and failed import;
  the sourced invocation passed;
- the first schema selection exposed the historical fixed `0.35 m` check; the
  schema was corrected to preserve it unless the new opt-in guidance contract
  is present, then its focused and full suites passed;
- the first new supervisor-integration fixture used bounds that admitted no
  safe candidate at its synthetic pose; corrected representative corner bounds
  made the intended replay pass;
- the whole-file style baseline remains the inherited failure described above,
  while the new test's style checks and all fatal checks pass.

None of those development invocations started Gazebo, created the external
evidence root, or altered retained evidence.

## Current milestone

**Phase 08.7 M2.1 — implementation and no-Gazebo qualification PASS; exact
input ready for pre-execution checkpoint and commit.**

### Next criterion

Checkpoint and commit this reviewed material boundary. Verify the clean commit
and frozen installed scenario identity, then dispatch exactly one bounded
visible-Gazebo M2.1 probe with no automatic retry.

## Phase 08.7 M2.1 committed dispatch boundary

The qualified implementation, tests, exact scenario, Plan amendment, live
status, and Phase 08 checkpoint were committed at:

```text
46a06c665fafb19edcd6d3ef7553907f1656b05e
phase 08.7: qualify M2.1 recovery correction
```

The post-commit worktree was clean and ahead of its remote by `54` commits.
The source and isolated installed scenario still have identical SHA-256
`541194d6152a8384c469f5bcc8573aef9afdb295bde6e148e5a82a692b8e4c8b`.
The external M2.1 evidence root remains absent and no ROS/Gazebo scenario
process is running.

Exactly one attempt is predeclared with ROS domain `89` and this bounded
visible-Gazebo invocation:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m2_1_qual/install/setup.bash
ROS_DOMAIN_ID=89
ROS_LOG_DIR=/tmp/phase08_7_m2_1_probe_ros_logs
MPLCONFIGDIR=/tmp/phase08_7_m2_1_probe_mpl
TURTLEBOT3_MODEL=burger
DISPLAY=:0
timeout --signal=INT --kill-after=60s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m2_1_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m2_1_correction_probe.yaml \
  --operator phase08_7_m2_1 \
  --case-id v7_m2_1_diagonal_r1p5_h25_18001 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_1 \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_1/\
phase08_v7_m2_1_correction_probe_summary.yaml \
  --gui
```

No automatic retry, parameter change, second case, M3 work, physical action,
or readiness claim is authorized by this dispatch.

## Phase 08.7 M2.1 execution and retained failure

The first shell wrapper stopped before `run_scenario` because `set -u` was
applied before the ROS setup script. It changed no evidence or process state
and is not an experiment attempt. The predeclared invocation was then run
without that wrapper error. Exactly one visible M2.1 experiment was executed:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_1/
  2026-07-29/
  20260729T234858803958Z_simulation_phase08_v7_m2_1_correction_probe-
  v7_m2_1_diagonal_r1p5_h25_18001-robust_gaussian_80ca5c97
```

The runner returned `1` for failed behavioral classification. The recorder
returned `0`, did not time out, retained a complete bag, and passed cleanup.

### Infrastructure and recording: PASS

- `classification.infrastructure_status=completed`;
- readiness duration is `360.128014908 s`;
- recording and cleanup passed with no remaining new nodes or session
  processes;
- no non-ground collision was observed;
- all three final command streams are zero and final readiness is false;
- `validate_run` returned `0`, `passed=true`, with no failures or warnings;
- the read-only sqlite fallback returned `ok` from `PRAGMA quick_check`;
- standard `analyze_run` returned `0`, wrote eight plots and eleven tables,
  and retained honest `analysis_status=partial` because the applicable escape
  never occurred.

### Staged behavior: FAIL before Stage A

The sole in-readiness state was `SEARCH` for `360.096129064 s`. There was no
convergence candidate or confirmation, no verification, fill, escape,
recenter, post-recovery affine state, or graceful global-proximity stop.

```text
Stage A local recovery:             FAIL
exact fill cardinality:             FAIL (zero fills)
Stage B global proximity:           FAIL (Stage A absent)
combined behavioral result:         FAIL
```

The robot was not stationary. It traveled `22.0617045159 m`, came within
`0.0539395645 m` of the intended local, and orbited there, but its closest
global distance was `2.8623873320 m`.

### Root cause

Read-only replay of the exact `3,622` PDE-history buffers found only `746`
qualified under the frozen `0.35` path-efficiency cap. Eligibility fragmented
into intervals no longer than `17.1 s`; the metric never crossed zero
(`minimum=+0.0657099110`) and the counter remained `3`.

The threshold excluded the known legitimate signal. At the retained M2
successful local candidates, the exact same `k=20` motion statistic was:

```text
121.4 s: 0.3639431494
156.4 s: 0.4434453791
180.1 s: 0.3605826563
```

All exceed `0.35`. A conservative read-only replay of the failed M2.1 path
with only the cap changed to `0.50` yields three local candidates at `172.9`,
`198.9`, and `220.7 s`. Their recent-window means are respectively `0.19395`,
`0.35529`, and `0.04452 m` from the local. No candidate occurs before
`172.9 s`, so directed translation remains rejected.

Full commands, evidence, hashes, and interpretation are retained in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m2_1_correction_probe_report.md
```

Immutable evidence SHA-256:

```text
b2d714392e4d17cca0fac7e054a6c48a4d2fb7cdece2e8caa42d1681f17b7db7  suite summary
c04ddbc912686693f045c3ae34b31ae692b2182361521448b309f459a7895414  scenario_result.yaml
02bf4614df8a4645cc29ef06cfe8a752fcace91dff2bfdd47e7946786b99e43b  completeness.json
c7d4eec24fbd272267447cb2d63f5add1095afc0f395b5fc0a451f1a9d426b5c  bag/bag_0.db3
74c467cef88e6c270c4b2d72284be6bb9fb58eaeeb3932f1c6f9cd5615fc7e3c  analysis/summary_metrics.json
1cd4d7001d8b981cf8cd88c0165858014b592f4cb4be09fac87433339ba0c8d9  analysis/analysis_completeness.json
```

M2.1 is closed and will not be retried or relabeled. It did not exercise the
topology-exhaustion or affine runtime corrections, so they remain
implementation/test-qualified rather than empirically passed.

## Current milestone

**Phase 08.7 M2.1 — retained FAIL. Infrastructure passed; the uncalibrated
`0.35` detector compactness cap prevented Stage A.**

### Next criterion

Checkpoint and commit the immutable M2.1 result. A separately versioned M2.2
may preserve every qualified implementation, geometry, topology, affine, and
stop value while changing only the empirically contradicted maximum path
efficiency from `0.35` to `0.50`, with a fresh hash, key, evidence root,
qualification, checkpoint, and commit. M3 remains unauthorized.

## Phase 08.7 M2.2 correction boundary

M2.1 and its evidence were checkpointed and committed unchanged at:

```text
c231647
phase 08.7: retain M2.1 detector failure
```

Under the user's standing authorization to execute the complete bounded
correction, the evidence-supported M2.2 amendment is now durable in
`plans/phase_08_7_plan.md`. M2.2 is a fresh experiment version and changes
only the detector's maximum path efficiency from `0.35` to `0.50`. It does
not reopen or retry M2.1.

The exact new input is:

```text
suite:    phase08_v7_m2_2_efficiency_correction_probe
case:     v7_m2_2_diagonal_r1p5_h25_18001
case key: 5078f6eff97d05419af1c59452fba15fb31b34c496e80f5ab3063ac091520e90
scenario: 1f11448b37ef8fbfb146124a0141d91d3404ee614d6d33e3a30f58aa0a179439
root:     /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_2
```

The strict source-level comparison and launch-binding tests pass:
`2 passed in 0.68s`. The first two discovery invocations accidentally replaced
the ROS `PYTHONPATH` and failed import before collection; the corrected
overlay-preserving invocation produced the reported pass. No Gazebo, runner,
recorder, or evidence-root process was started.

**Current milestone: Phase 08.7 M2.2 no-Gazebo qualification.**

No M2.2 Gazebo run is permitted until the complete Plan gates pass and the
fresh scenario, Plan, tests, status, and checkpoint are committed.

## Phase 08.7 M2.2 no-Gazebo qualification result

M2.2 passes its complete pre-execution boundary.

The source-level and central-launch comparisons prove that the only
behavioral input change from immutable M2.1 is:

```text
convergence_maximum_path_efficiency: 0.35 -> 0.50
```

The full bounded no-Gazebo functional set passed:

```text
536 passed, 2 skipped, 1 deselected in 112.29s
```

This set covers aggregate truth, bag analysis, convergence policy, shutdown,
escape/recenter, recording, legacy, observability, Phase 08 validation, robust
Gaussian behavior, scenario schema/runner, disturbances, state machine, and
supervisor integration. The two skips are explicit runtime integrations. The
one deselection is the recorded historical V4 adoption assertion that treats
later versioned scenario files as an error. No required behavioral test
failed.

Both changed test files pass `ament_flake8`, `ament_pep257`, and fatal Python
checks `E9,F63,F7,F82`. `git diff --check` passes.

The fresh isolated build passed:

```text
build base:   /tmp/phase08_7_m2_2_qual/build
install base: /tmp/phase08_7_m2_2_qual/install
log base:     /tmp/phase08_7_m2_2_qual/log
Summary: 3 packages finished in 11.7s
```

The installed dry-run resolved one run, zero unsupported cases, the frozen
case key, `75` launch arguments, and the exact `0.50` detector cap. It retained
the M2.1 geometry, one-fill limit, affine gain/age, three retries, visible GUI,
and both `0.60 m` stop boundaries. The dry-run summary is
`/tmp/phase08_7_m2_2_dry_run.yaml`.

Nonexecuting central-launch instantiation produced the expected `254`-line
description at `/tmp/phase08_7_m2_2_launch_description.txt` and binds the
detector, modified-cost, and supervisor through the existing owners.

Source/install hashes match:

```text
1f11448b37ef8fbfb146124a0141d91d3404ee614d6d33e3a30f58aa0a179439  M2.2 scenario
541194d6152a8384c469f5bcc8573aef9afdb295bde6e148e5a82a692b8e4c8b  immutable M2.1 scenario
9277b63743c7672268721c50b414020fc5951d719f358fd053d5f86d0b06e49c  central launch
```

The Phase 08 context validator passes with the active Phase 08.7 plan.
`DISPLAY=:0` is available. The fresh M2.2 evidence root remains absent, and
no Gazebo, runner, recorder, bag recorder, or physical-hardware process is
running. No V6, historical scenario/world/evidence, algorithm implementation,
interface, topic, cost sign/unit, or controller owner changed.

## Current milestone

**Phase 08.7 M2.2 — no-Gazebo qualification PASS; exact input ready for
checkpoint and commit.**

### Next criterion

Checkpoint and commit the exact M2.2 scenario, Plan, tests, and status. Verify
the clean commit and unchanged installed hash, then run exactly one bounded
visible probe without automatic retry.

## Phase 08.7 M2.2 committed dispatch boundary

The qualified M2.2 material was committed cleanly at:

```text
4fdc43fede08e0abdb69e799e1273329ed01129f
phase 08.7: qualify M2.2 detector calibration
```

The source and isolated installed scenario remain identical at SHA-256
`1f11448b37ef8fbfb146124a0141d91d3404ee614d6d33e3a30f58aa0a179439`.
The fresh root is absent and no ROS/Gazebo process is running.

Exactly one visible attempt is predeclared on ROS domain `92`:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m2_2_qual/install/setup.bash
ROS_DOMAIN_ID=92
ROS_LOG_DIR=/tmp/phase08_7_m2_2_probe_ros_logs
MPLCONFIGDIR=/tmp/phase08_7_m2_2_probe_mpl
TURTLEBOT3_MODEL=burger
DISPLAY=:0
timeout --signal=INT --kill-after=60s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m2_2_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m2_2_efficiency_correction_probe.yaml \
  --operator phase08_7_m2_2 \
  --case-id v7_m2_2_diagonal_r1p5_h25_18001 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_2 \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_2/\
phase08_v7_m2_2_efficiency_correction_probe_summary.yaml \
  --gui
```

The result will be retained without automatic retry. M3, physical hardware,
parameter changes, and readiness claims remain outside this dispatch.

## Phase 08.7 M2.2 execution and retained failure

Exactly one bounded visible-Gazebo M2.2 attempt was executed:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_2/
  2026-07-30/
  20260730T001458667712Z_simulation_phase08_v7_m2_2_
  efficiency_correction_probe-v7_m2_2_diagonal_r1p5_h25_18001-
  robu_bfd6b97a
```

The runner returned `1` for failed behavioral classification. The recorder
returned `0`, did not time out, retained a complete bag, and passed cleanup.
`validate_run` passed with no failures or warnings, sqlite
`PRAGMA quick_check` returned `ok`, and standard analysis completed with eight
plots, eleven tables, and no analysis failures.

### Detector, topology, and local mechanism

The `0.50` detector cap worked. SEARCH-only candidates occurred at source
times `193.7`, `216.9`, and `238.4 s`; the third produced
`CONVERGENCE_CONFIRMED` at the intended local. The convergence point was
`(1.3856016612, 1.1866239560) m`, `0.3485022905 m` from the local and
`3.1340690892 m` from the global.

Exactly one unique fill cluster was created. The first fill and its later
merged revision both have cluster identity `1`, so exact cardinality passes.
The observed path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_ASSIST
-> RECENTER
-> SEARCH
-> FAILSAFE
```

The assisted escape and recenter mechanism completed, with
`RECENTER_COMPLETE` at source time `275.2 s`. The formal Stage A reporter
nevertheless returned zero episodes because it only recognizes the direct
path without the legal redesign plus `ESCAPE_ASSIST` branch. The singular
controller `required_state_path` fails for the same reason, and the live
global monitor therefore never armed.

### Affine guidance and global stop

Affine assistance was active after recenter: resumed `SEARCH` retained the
accepted fill and reported `(raw, Gaussian, affine) = (1, 1, 1)`. The safe
direction began near `(0.776196, 0.630491)`, later changed near
`(-0.420, 0.907)`, and moved the robot toward the global corner.

The frozen `0.60 m` stop was too strict for that safe approach. The first
post-recenter noninterpolated sample within `1.20 m` occurred at ROS time
`306.030 s`, pose `(3.369462640, 2.308150068) m`, distance
`1.198977173 m`. It remained `0.180537360 m` inside the east controller
inset. The wall-margin failsafe followed `4.77 s` later and first east-wall
contact approximately `5.85 s` later. There was no `0.60 m` sample; the
closest recorded distance was about `0.780 m` after failsafe/inertial motion.

```text
infrastructure/recording/cleanup:       PASS
detector local confirmation:            PASS
exact unique fill cardinality:          PASS
local escape/recenter mechanism:        OBSERVED
formal Stage A reporter:                FAIL
formal Stage B global proximity:        FAIL
collision expectation:                  FAIL
combined behavioral result:             FAIL
```

Full commands, causal evidence, hashes, and the bounded counterfactual are
retained in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m2_2_efficiency_correction_probe_report.md
```

Immutable evidence SHA-256:

```text
3638818042255b508d441b6222e16c91b2d85614d22776589385f2d6f3dd2052  suite summary
27648c8344318c43883f9296a450f9ed4a350c915e626cd4405f7a8b3b7ef264  scenario_result.yaml
bf72611b9a9b006401ae1b2070eb6ddba880a753ae3d61e8a0f35354ed7b6b8e  completeness.json
17c57b1e0247b1ea079b0a8e1ef0aff6a750cf301e4bd3ab21dfaccb53255527  bag/bag_0.db3
c5bbe0a306cfa17f5d41268aeb400b1104ca99f09a392d07e4f2622ac48bef34  analysis/summary_metrics.json
b4cfeaebf17a1c0fe8946353ad4438f2603147c9c8bca289bd0d26b3d014ed1c  analysis/analysis_completeness.json
```

M2.2 is closed and will not be retried or relabeled. A fresh M2.3 may preserve
all M2.2 algorithm values while (1) accepting the direct or legal assisted
recovery path in the reporter/controller predicate and (2) setting both
post-recovery proximity boundaries to the evidence-backed `1.20 m`
operator-equivalent stop. M3 remains unauthorized.

## Current milestone

**Phase 08.7 M2.2 — retained FAIL. The detector, one-fill topology, assisted
local escape, recenter, and affine guidance worked; the recovery-path reporter
and overly strict stop boundary prevented the combined result.**

### Next criterion

Checkpoint and commit the immutable M2.2 result. Implement a separately
versioned M2.3 contract correction, fully qualify it without Gazebo, and
checkpoint/commit its frozen input before any new visible probe.

## Phase 08.7 M2.3 correction boundary

The immutable M2.2 result, report, live status, and Phase 08 checkpoint were
committed at:

```text
ccb9a52d01a57474db784a24cca097a999a8c1b4
phase 08.7: retain M2.2 recovery contract failure
```

The post-commit worktree was clean. Under the user's standing authorization to
execute the complete bounded correction, the fresh M2.3 amendment is now
durable in `plans/phase_08_7_plan.md`. M2.3 does not reopen, retry, or relabel
M2.2.

M2.3 preserves every M2.2 algorithm and launch value. It:

- adds schema-v5-only `required_state_paths` while retaining the singular
  `required_state_path` as the first alternative;
- recognizes both the direct recovery path and the existing legal
  one-redesign `ESCAPE_ASSIST` path in Stage A, live-stop, controller, and
  scoped reporting;
- retains exact one-cluster cardinality and every causal-event requirement;
- permits only the opt-in post-recovery profile to declare a radius from
  `0.60` through `1.20 m`;
- fixes both M2.3 global-proximity declarations at the empirically safe
  `1.20 m` operator-equivalent boundary.

Absent alternatives, existing schema-v5 normalization remains unchanged.
Schema-v1 through schema-v4 reject the new field. Guidance-disabled geometry
retains the exact historical `0.35 m` boundary. M2.1 and M2.2 remain exact
`0.60 m` inputs.

The fresh exact input is:

```text
suite:    phase08_v7_m2_3_assisted_recovery_stop_probe
case:     v7_m2_3_diagonal_r1p5_h25_18001
case key: 13cf3a091db9f9e72fff3abc0c1885b4e64033766f5317ee628490e468e10cbd
scenario: f03db4462527620321eb299656d9f56fe32e10362664e595f7d3850fc3f53eca
root:     /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_3
```

Initial no-Gazebo checks pass:

- the four changed Python files compile;
- `ament_flake8 --linelength 99` and `ament_pep257` pass on all four;
- ten new/affected contract tests pass (`114` deselected);
- the direct and assisted live monitors both wait for Stage A plus exact
  cardinality and then stop on the first near odometry sample;
- the source dry-run resolves one run, zero unsupported cases, the frozen key,
  both legal paths, both `1.20 m` declarations, and the unchanged `75` launch
  arguments;
- strict source tests prove M2.3's launch command equals M2.2's command.

The source dry-run is retained at
`/tmp/phase08_7_m2_3_source_dry_run.yaml`. The fresh external evidence root is
absent, and no Gazebo, runner, recorder, bag recorder, or physical-hardware
process is running.

## Current milestone

**Phase 08.7 M2.3 — complete no-Gazebo qualification in progress.**

### Next criterion

Run the full declared functional regressions, isolated build, installed
dry-run, and nonexecuting launch instantiation. Verify historical identities,
source/install hash equality, context, diff, and process/root absence; then
checkpoint and commit before any Gazebo execution.

## Phase 08.7 M2.3 no-Gazebo qualification result

M2.3 passes its complete pre-execution boundary.

### Functional and compatibility evidence

The final clean bounded functional run used fresh ROS domain `98`, explicitly
disabled every Gazebo integration gate, and produced:

```text
546 passed, 2 skipped, 1 deselected in 110.19s
JUnit: /tmp/phase08_7_m2_3_functional_clean.xml
errors=0, failures=0, skipped=2, tests=548
```

This is the same broad envelope used for M2.2 plus the new M2.3 tests. It
covers aggregate truth, bag analysis, convergence policy, deferred shutdown,
escape/recenter, recording, legacy, observability, Phase 08 validation, robust
Gaussian behavior, schema/runner, disturbances, state machine, and supervisor
integration. The two skips are explicit runtime integrations. The one
deselection is the recorded historical V4 adoption assertion that treats
later fixed scenario files as an error.

An orchestration wrapper yielded before its first broad shell finished and
accidentally allowed a duplicate broad run to overlap it. The duplicate JUnit
record retained `545` passes, two expected skips, and one supervisor
integration wait failure. That exact failing test passed alone on fresh ROS
domain `97` (`1 passed in 0.96s`), and the clean nonoverlapping full run above
then passed it as part of all `548` executed tests. The overlap result is
retained as a qualification-process artifact, not hidden or represented as an
algorithm failure, and no Gazebo or experiment evidence was involved.

The final contract-focused selection passes:

```text
14 passed, 114 deselected in 1.01s
```

It proves:

- schema-v1 through schema-v4 reject `required_state_paths`;
- empty, duplicate, unreachable, misclassified, and singular-inconsistent
  alternatives are rejected;
- both direct and assisted recovery paths satisfy Stage A and the live monitor;
- radii below `0.60 m`, above `1.20 m`, or inconsistent between staged and
  ground truth are rejected;
- the M2.3 launch command is exactly equal to M2.2's launch command;
- M2.1 and M2.2 case keys and stop contracts remain unchanged.

All four changed Python source/test files pass `ament_flake8 --linelength 99`,
`ament_pep257`, compilation, and fatal Python checks. `git diff --check`
passes. The full historical immutability test, including all sealed
schema-v1-through-schema-v4 identities, passed inside the broad suite.

### Isolated build and installed resolution

The fresh isolated source build passed:

```text
build base:   /tmp/phase08_7_m2_3_qual/build
install base: /tmp/phase08_7_m2_3_qual/install
log base:     /tmp/phase08_7_m2_3_qual/log
Summary: 3 packages finished in 11.6s
```

The installed dry-run resolved one run, zero unsupported cases, the exact case
key, both legal state paths, exact one-fill topology, the `0.50` detector cap,
three retries, affine gain/age, and both `1.20 m` boundaries. Its launch argv
contains four ROS launch-owner entries plus the same `75` launch arguments as
M2.2. The summary is `/tmp/phase08_7_m2_3_dry_run.yaml`.

Nonexecuting installed central-launch instantiation passed and produced the
expected `254`-line description at
`/tmp/phase08_7_m2_3_launch_description.txt`. It binds the detector,
modified-cost node, fill owner, and supervisor through the existing central
launch owner. It did not start Gazebo.

Source and isolated-install identities match:

```text
f03db4462527620321eb299656d9f56fe32e10362664e595f7d3850fc3f53eca  M2.3 scenario
8ea18406346af0e7c0b7f2a23c895ff67e48232e37f7510268a926b92c76a1f8  scenario schema
b2a0085f184f4f46113b58dd2e76a1cc7195ceab9214628ee4b556db79f5b0b1  scenario runner
9277b63743c7672268721c50b414020fc5951d719f358fd053d5f86d0b06e49c  central launch
88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf  shifted world
1f11448b37ef8fbfb146124a0141d91d3404ee614d6d33e3a30f58aa0a179439  immutable M2.2 scenario
541194d6152a8384c469f5bcc8573aef9afdb295bde6e148e5a82a692b8e4c8b  immutable M2.1 scenario
```

The Phase 08 context validator passes with the active Phase 08.7 plan.
`DISPLAY=:0` passes `xdpyinfo`, approximately `319 GiB` is free, the fresh
M2.3 evidence root remains absent, and no Gazebo, runner, recorder, bag
recorder, or physical-hardware process is running. No V6 file, historical
scenario/world/evidence, controller, supervisor algorithm, fill algorithm,
interface, topic, cost sign/unit, or `/cmd_vel` owner changed.

## Current milestone

**Phase 08.7 M2.3 — no-Gazebo qualification PASS; exact input ready for
checkpoint and commit.**

### Next criterion

Checkpoint and commit the exact M2.3 runtime changes, scenario, tests, Plan,
and status. Verify a clean commit, unchanged installed scenario hash, absent
evidence root, and inactive ROS/Gazebo process set before dispatching exactly
one bounded visible probe without automatic retry.

## Phase 08.7 M2.3 committed dispatch boundary

The qualified M2.3 material was committed cleanly at:

```text
9a2612beb0e987c4d328d04660529f77a2f089af
phase 08.7: qualify M2.3 recovery contract
```

The source and isolated installed scenario remain identical at SHA-256
`f03db4462527620321eb299656d9f56fe32e10362664e595f7d3850fc3f53eca`.
The fresh evidence root is absent and no ROS/Gazebo scenario process is
running.

Exactly one visible attempt is predeclared on ROS domain `101`:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m2_3_qual/install/setup.bash
ROS_DOMAIN_ID=101
ROS_LOG_DIR=/tmp/phase08_7_m2_3_probe_ros_logs
MPLCONFIGDIR=/tmp/phase08_7_m2_3_probe_mpl
TURTLEBOT3_MODEL=burger
DISPLAY=:0
timeout --signal=INT --kill-after=60s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m2_3_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m2_3_assisted_recovery_stop_probe.yaml \
  --operator phase08_7_m2_3 \
  --case-id v7_m2_3_diagonal_r1p5_h25_18001 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_3 \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_3/\
phase08_v7_m2_3_assisted_recovery_stop_probe_summary.yaml \
  --gui
```

The result will be retained without automatic retry. M3, physical hardware,
parameter changes, a second M2.3 attempt, and readiness claims remain outside
this dispatch.

## Phase 08.7 M2.3 execution and retained pass

Exactly one bounded visible-Gazebo M2.3 attempt was executed on ROS domain
`101`. The runner returned `0`:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_3/
  2026-07-30/
  20260730T005434366368Z_simulation_phase08_v7_m2_3_
  assisted_recovery_stop_probe-v7_m2_3_diagonal_r1p5_h25_18001-
  rob_fe3286c1
```

The result is retained as **PASS**:

```text
infrastructure/recording/cleanup:       PASS
detector local confirmation:            PASS
exact unique fill cardinality:          PASS
Stage A local recovery:                 PASS
Stage B post-recovery global proximity: PASS
collision expectation:                  PASS
combined behavioral result:             PASS
```

### Local detection, fill, and recovery

SEARCH-only convergence candidates occurred at source times `131.8`, `153.8`,
and `175.9 s`, with path efficiencies `0.2852566130`, `0.3430636994`, and
`0.3616799274`. The last candidate produced `CONVERGENCE_CONFIRMED`.

The convergence point was `(1.3938876873, 1.1160647584) m`,
`0.3378020801 m` from the declared local and `3.1810149811 m` from the
global. Exactly one typed fill cluster was created: cluster/fill identity
`1`, center `(1.3945263243, 1.2521809924) m`, and
`0.1361177322 m` fill-to-convergence distance.

The in-readiness path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

Repulse began at `185.2 s`, reached its stable exit and entered recenter at
`194.6 s`, and returned to `SEARCH` at `208.0 s`. All required causal events
were present. The direct path passed in this attempt; the alternative legal
redesign-assisted path remains qualified by the pre-run contract tests.

### Affine assistance and global operator stop

Post-recovery affine guidance was enabled and active. Immediately after
recenter the recorded weights were
`(sensor, Gaussian, affine) = (1, 1, 1)`.

After Stage A and exact one-fill cardinality passed, the live monitor stopped
on the first qualifying noninterpolated odometry sample:

```text
bag timestamp:        1785373119246261619
sample index:         6940
position:             (3.4433011933, 2.3021489031) m
distance to global:   1.1991922303 m
committed radius:     1.20 m
valid post-A samples: 905
invalid post-A:       0
interpolation used:   false
```

No collision, in-readiness `FAILSAFE`, `TIMEOUT`, forbidden event, or
evidence-integrity failure preceded the stop. The explicit-stop `FAILSAFE`
samples emitted during shutdown occur after readiness is false and do not
alter the behavioral result. This is the committed simulation equivalent of
the user's allowed physical `Ctrl+C` once the robot is observably close enough
to the global minimum.

The controller-goal diagnostic is false because there is intentionally no
`GOAL_REACHED`/`GOAL_HOLD` requirement. Independent simulation ground truth,
Stage B, and combined classification pass.

### Infrastructure and retained evidence

The recorder returned `0`, did not time out, and completed final-zero and
final-readiness-false. Cleanup passed with no remaining new nodes or session
processes. `validate_run` returned `0`, `passed=true`, with no failures or
warnings. Read-only sqlite `PRAGMA quick_check` returned `ok`.

Standard analysis completed at `<run>/analysis/phase07` with eight plots,
eleven tables, and no analysis failures. It reports
`236.992702246 s` readiness, `14.9839405545 m` path length, one successful
escape attempt, one active/created fill, no in-readiness failsafe or timeout,
no collision, and terminal `SEARCH`.

Immutable evidence SHA-256:

```text
b607f577f261f1b133d730abbe51fe372c3141804fe48406bc2f6b66d33bfd1f  suite summary
9a85e950a341a6c4c1f69aefbbcb3d87d469deea068d0923ad3530766d010819  scenario_result.yaml
337be8d933be644cc37d3b0b1b93ed052336d0997f64bc7e231d67c7829fcb81  completeness.json
b14cb52d1d2eaa5e24f2bb50e4d84a95934678f7e6f3c86ad85b8d788340b9f3  bag/bag_0.db3
16e5136fa7a4b4715054ce50320bb0e7720dd83d20b0cda0e09b7083a3d5ee0b  analysis/phase07/summary_metrics.json
3d9497adda29ca8ef255473c6a55b248810b9382a8798a88489e91cdf43e99dd  analysis/phase07/analysis_completeness.json
```

Full commands, causal evidence, classification, and limitations are retained
in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m2_3_assisted_recovery_stop_probe_report.md
```

M2.3 is closed and will not be retried or relabeled. It establishes the
declared prerequisite for a separately authorized M3 spatial suite, but one
development pass is not repeatability or simulation-readiness evidence.
M3, physical hardware, a second M2.3 attempt, and readiness claims remain
unauthorized.

### Result checkpoint

The bounded material-boundary command passed:

```text
timeout 180s \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/\
checkpoint_phase.sh 08
```

It wrote
`docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt` against base
HEAD `9a2612beb0e987c4d328d04660529f77a2f089af`. `git diff --check` and the
Phase 08 implementation-context validator pass, the qualified source/install
scenario hashes remain identical, and the ROS/Gazebo scenario process set is
inactive.

## Current milestone

**Phase 08.7 M2.3 — retained PASS. Stage A, Stage B, exact fill cardinality,
collision, infrastructure, validation, and combined predicates all passed.**

### Next criterion

Commit the immutable M2.3 result and verify a clean worktree. Stop before M3
unless the user separately authorizes its frozen multi-position suite.

## Phase 08.7 M3 authorization and frozen amendment

The M2.3 result was committed cleanly at:

```text
e912cc086ac2290e8c0ff3be62decfc95507faa3
phase 08.7: retain successful M2.3 probe
```

The user authorized the complete M3 amendment and execution on 2026-07-30.
M3 tightens primary Stage B and combined success to `1.00 m` from the global.
The earlier `1.20 m` boundary becomes a separately reported, non-gating
post-Stage-A global-region approach diagnostic.

The suite is frozen as a five-position cross using one constant fresh seed:

```text
v7_m3_r1p0_a45_h25_18101
  r=1.0 m, angle=45 deg
  local=(0.7071067811865476, 0.7071067811865475)

v7_m3_r1p5_a22p5_h25_18101
  r=1.5 m, angle=22.5 deg
  local=(1.38581929876693, 0.5740251485476346)

v7_m3_r1p5_a45_h25_18101
  r=1.5 m, angle=45 deg
  local=(1.0606601717798214, 1.0606601717798212)

v7_m3_r1p5_a67p5_h25_18101
  r=1.5 m, angle=67.5 deg
  local=(0.5740251485476348, 1.38581929876693)

v7_m3_r2p0_a45_h25_18101
  r=2.0 m, angle=45 deg
  local=(1.4142135623730951, 1.414213562373095)

seed for every case: 18101
local/global input: 400.0 / 1600.0 relative units
known topology: 1 local, 1 global
maximum fills: 1
primary Stage B radius: 1.00 m
approach diagnostic: 1.20 m
```

The positions were prospectively listed as examples in the approved geometry
Plan before any corner-origin outcome. The shared seed isolates spatial
placement rather than mixing position and seed effects.

M3 will execute exactly five serial headless runs from the fresh root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m3
```

Every attempt is retained. Behavioral failure does not stop later cases;
cleanup failure does. M3 passes only at `5/5` combined primary successes.
The `1.20 m` diagnostic cannot rescue a case that misses `1.00 m`.

Before Gazebo, add and test only the optional schema-v5
`global_approach_radius_m` diagnostic, freeze the exact suite, run the complete
no-Gazebo qualification boundary, checkpoint, and commit. M2.3 and all
historical scenarios, case keys, worlds, results, and evidence remain
immutable.

## Current milestone

**Phase 08.7 M3 — amendment frozen; additive reporting and exact-suite
implementation authorized, with no Gazebo dispatch before qualification and
commit.**

### Next criterion

Implement the optional non-gating approach diagnostic and exact five-case
suite. Qualify the complete source/install boundary, checkpoint, and commit it
before creating the fresh evidence root or launching Gazebo.

## Phase 08.7 M3 implementation and no-Gazebo qualification

M3's additive reporter and exact spatial suite are implemented without
changing the controller, detector, supervisor, fill owner, central launch
graph, recorder, validator, analyzer, shifted world, M2.3 algorithm values, or
historical scenarios.

The optional schema-v5
`success.staged_recovery.global_approach_radius_m`:

- is present in normalized output only when declared;
- requires post-recovery guidance;
- must be strictly greater than the primary radius and no greater than
  `1.20 m`;
- records the first finite noninterpolated post-Stage-A odometry sample;
- is invalidated by a non-ground collision before that sample;
- is retained live without stopping the recorder before the primary radius;
- appears as `staged_results.global_region_approach` and is absent from every
  required predicate and combined-success calculation.

Absent the field, M2.3 normalization, live result shape, classification shape,
and its case key remain unchanged. Schema-v1 through schema-v4 and the sealed
historical identities remain unchanged.

### Exact qualified input

```text
suite:
  phase08_v7_m3_spatial_suite
scenario:
  1221d8cb9d7235218d4f3da710f10d41284632a93712bd89d763d938a0437dae
resolved runs: 5
unsupported:   0
seed:          18101 for every case
execution:     serial, headless
primary:       1.00 m
diagnostic:    1.20 m
root:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m3

v7_m3_r1p0_a45_h25_18101
  75d0c27b3cf3b0a88aff539723a907d7bd48c26f218eee2baae89487364b1712
v7_m3_r1p5_a22p5_h25_18101
  67d7c6d4959f5656e81394a31509a4a66a516d4fe3cc4625b91b31e2dbba1d0a
v7_m3_r1p5_a45_h25_18101
  0bbd09a8898e7bfaafa6fe75b4cd813c286c9d0a378d90df11685393b5100115
v7_m3_r1p5_a67p5_h25_18101
  474302bb0c69f67e0efe875bc9031a38dc33f4cd89506d615b7a6e3b1804acf1
v7_m3_r2p0_a45_h25_18101
  94deae52e7c35eb428663e4eb099d8078d23f5dda8561b357998a71d46b43614
```

The source dry-run is retained at
`/tmp/phase08_7_m3_source_dry_run.yaml`. An initial attempt to invoke the
source through the old M2.3 installed console wrapper stopped before runner
entry with `StopIteration` because source `PYTHONPATH` does not carry the old
distribution entry-point metadata. The direct source-module invocation then
resolved all five runs and zero unsupported cases. No Gazebo or recorder
process was started by either command.

### Functional and compatibility evidence

The focused M3/M2.3 contract selection passed:

```text
24 passed, 116 deselected in 1.42 s
```

It covers the exact five positions and case identities, primary/diagnostic
radius validation, M2.3 absence-shape compatibility, distinct first approach
and primary samples, collision scoping before the approach sample, live
continuation past `1.20 m`, and proof that the diagnostic cannot rescue or
fail combined success.

The final clean declared functional envelope used fresh ROS domain `104`,
explicitly disabled all Gazebo integration opt-ins, and produced:

```text
556 passed, 2 skipped, 1 deselected in 105.56 s
JUnit: /tmp/phase08_7_m3_functional_clean.xml
```

The skips are the explicit recording/Gazebo runtime integrations. The
deselection is the recorded historical V4 adoption assertion that treats
later fixed scenarios as an error. The run covers aggregate truth, bag
analysis, convergence policy, deferred shutdown, escape/recenter, recording,
legacy behavior, observability, Phase 08 validation, robust Gaussian behavior,
schema/runner, disturbances, state machine, and supervisor integration.

A broader whole-package superset was also retained at
`/tmp/phase08_7_m3_functional.xml`. Its functional tests produced
`561 passed, 3 skipped, 1 deselected`; only the generic whole-tree
`test_flake8.py` and `test_pep257.py` wrappers failed on `5,209` flake8 and
`589` pep257 findings in pre-existing historical files. Direct
`ament_flake8 --linelength 99`,
`ament_pep257`, compilation, and `git diff --check` all pass on the four
changed Python files.

The fresh isolated build passed:

```text
build base:   /tmp/phase08_7_m3_qual/build
install base: /tmp/phase08_7_m3_qual/install
log base:     /tmp/phase08_7_m3_qual/log
Summary: 3 packages finished in 11.5 s
```

The installed dry-run at
`/tmp/phase08_7_m3_installed_dry_run.yaml` resolves the same five case keys,
zero unsupported cases, exact topology, both legal recovery paths, primary
`1.00 m`, diagnostic `1.20 m`, and the unchanged M2.3 algorithm controls.
Nonexecuting installed central-launch description generation produced the
expected `254` lines at
`/tmp/phase08_7_m3_launch_description.txt` and bound the existing modified
cost, detector, fill, supervisor, and controller owners without launching
Gazebo.

Source and isolated-install identities match:

```text
1221d8cb9d7235218d4f3da710f10d41284632a93712bd89d763d938a0437dae  M3 suite
342710fd87fb138c44e1edeca8821bb2e9cb0c646da8ca7a38e3b488c2761085  scenario schema
7d9947de4e46abb9b21adad52768b55d02654bf7f561f6d32ffdf6ee474ec9b6  scenario runner
9277b63743c7672268721c50b414020fc5951d719f358fd053d5f86d0b06e49c  central launch
88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf  shifted world
f03db4462527620321eb299656d9f56fe32e10362664e595f7d3850fc3f53eca  immutable M2.3 suite
1f11448b37ef8fbfb146124a0141d91d3404ee614d6d33e3a30f58aa0a179439  immutable M2.2 suite
541194d6152a8384c469f5bcc8573aef9afdb295bde6e148e5a82a692b8e4c8b  immutable M2.1 suite
```

The Phase 08 implementation-context validator passes, approximately `318 GiB`
is free, the fresh M3 evidence root remains absent, and the
Gazebo/runner/recorder process set is inactive.

The bounded material-boundary command passed:

```text
timeout 180s \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/\
checkpoint_phase.sh 08
```

It wrote
`docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt` against base
HEAD `888692ece7440f45dc310359116b51f9e1b0972d`.

## Current milestone

**Phase 08.7 M3 — additive reporting and exact five-case input qualified
without Gazebo; checkpoint and pre-dispatch commit pending.**

### Next criterion

Checkpoint and commit the exact implementation, tests, scenario, Plan, and
status. Verify a clean commit, identical installed suite hash, absent evidence
root, and inactive process set before dispatching the five serial headless
attempts.

## Phase 08.7 M3 committed dispatch boundary

The qualified implementation and exact five-case suite were committed at:

```text
d5d29aa2225c26d2bfa62f00a398b238b67a709b
phase 08.7: qualify M3 spatial suite
```

The post-commit worktree was clean. Source and isolated-install suite hashes
remain identical at
`1221d8cb9d7235218d4f3da710f10d41284632a93712bd89d763d938a0437dae`.
The fresh evidence root is absent and the Gazebo/runner/recorder process set is
inactive.

Exactly five serial headless attempts are predeclared on ROS domain `106`:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m3_qual/install/setup.bash
ROS_DOMAIN_ID=106
ROS_LOG_DIR=/tmp/phase08_7_m3_ros_logs
MPLCONFIGDIR=/tmp/phase08_7_m3_mpl
TURTLEBOT3_MODEL=burger
timeout --signal=INT --kill-after=90s 3000s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m3_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m3_spatial_suite.yaml \
  --operator phase08_7_m3 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m3 \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m3/\
phase08_v7_m3_spatial_suite_summary.yaml
```

There is no `--gui` override and the committed suite declares
`gazebo_gui: false`. Every attempt is retained. A behavioral failure continues
to the next fixed case; a cleanup failure stops dispatch. No case will be
retried and no threshold, position, seed, or algorithm value will be changed
inside M3.

## Current milestone

**Phase 08.7 M3 — qualified input committed; exact five-run headless dispatch
predeclared.**

### Next criterion

Execute the one bounded serial batch, preserve all attempts, validate and
analyze every completed run, evaluate the strict all-five gate, write the M3
report, checkpoint, and commit the retained result.

## Phase 08.7 M3 retained execution result

The exact committed five-case batch ran once from qualified commit
`d5d29aa2225c26d2bfa62f00a398b238b67a709b`. It started at
`2026-07-30T02:53:29.648468Z`, completed at
`2026-07-30T03:29:15.306672Z`, and retained all five cases under:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m3
```

The outer runner returned `1` because four completed cases failed required
behavioral predicates. The 3000-second outer timeout did not fire, every
recorder returned `0`, and no cleanup failure stopped dispatch.

### Strict suite gate

```text
infrastructure / recording / cleanup: 5 / 5
formal Stage A local recovery:         2 / 5
exact associated fill cardinality:    4 / 5
non-gating 1.20 m approach:            2 / 5
primary 1.00 m Stage B:                1 / 5
collision expectation:                 4 / 5
combined success:                       1 / 5
required M3 gate:                       5 / 5
```

M3 is therefore **FAIL** and closed without retry or tuning.

### Per-case causal result

- `v7_m3_r1p0_a45_h25_18101`: **PASS**. The direct Stage A path and exact
  fill assignment passed; first approach distance was `1.1974712642 m`, first
  primary distance was `0.9987060992 m`, and no collision occurred.
- `v7_m3_r1p5_a22p5_h25_18101`: **FAIL**. The local and one fill associated
  correctly, but repulsive escape stalled. The one permitted redesign retained
  `39` valid synchronized samples against the unchanged `40` minimum, emitted
  `FILL_REJECTED`, and entered `FAILSAFE` before recenter.
- `v7_m3_r1p5_a45_h25_18101`: **FAIL**. The redesign-assisted Stage A path,
  exact cluster cardinality, and `1.20 m` diagnostic passed at
  `1.1976898679 m`. It never entered `1.00 m`; the minimum anywhere in the
  complete post-Stage-A in-readiness trace was `1.0981376815 m`. The run also
  retained wall-margin-inset failsafe and collision evidence.
- `v7_m3_r1p5_a67p5_h25_18101`: **FAIL**. The mechanical lifecycle returned
  to `SEARCH`, but convergence was `0.7491931004 m` from the declared local,
  outside the `0.60 m` tolerance, so the cluster remained unassigned and
  formal Stage A/cardinality failed. It later entered `FAILSAFE` with
  `no safe post-recovery direction candidate`.
- `v7_m3_r2p0_a45_h25_18101`: **FAIL**. Local association and exact
  cardinality passed, but recenter emitted `TIMEOUT` after about `30.10 s` and
  entered `FAILSAFE`; Stage A did not complete.

### Evidence integrity

All five independent `validate_run` invocations returned `0`, `passed=true`,
with empty failure and warning lists. Read-only sqlite `PRAGMA quick_check`
returned `ok` for each bag. All five `analyze_run` invocations returned `0`
and status `complete`, with fresh Phase 05 validation true, eight plots,
eleven tables, and empty recording/analysis failure lists.

The `sqlite3 -readonly` CLI audit could not start because the executable is
unavailable. The approved Python standard-library fallback opened every bag
with `file:...?mode=ro`; all five `PRAGMA quick_check` results were
`[('ok',)]`.

A shell bookkeeping loop around validation exited `1` despite printing five
child return codes of `0`. The retained logs independently prove five passing
validators; this wrapper anomaly is recorded but is not a run-validation
failure:

```text
/tmp/phase08_7_m3_validate_*.log
/tmp/phase08_7_m3_analyze_*.log
```

A read-only immutable-evidence assertion reloaded the suite summary, every
scenario result, run metadata, and analysis completeness file. It passed the
expected aggregate vector:

```text
[infrastructure, Stage A, fill, approach, Stage B, collision gate, combined]
[5,              2,       4,    2,        1,       4,              1]
```

Every metadata file identifies qualified commit `d5d29aa`. The source and
isolated-install M3 suite remain byte-identical at
`1221d8cb9d7235218d4f3da710f10d41284632a93712bd89d763d938a0437dae`.
The immutable M2.3, M2.2, and M2.1 suite hashes remain respectively
`f03db4462527620321eb299656d9f56fe32e10362664e595f7d3850fc3f53eca`,
`1f11448b37ef8fbfb146124a0141d91d3404ee614d6d33e3a30f58aa0a179439`,
and
`541194d6152a8384c469f5bcc8573aef9afdb295bde6e148e5a82a692b8e4c8b`.

Suite-summary SHA-256:

```text
0fe3d63b9223aac22ffe442cd78d7732f94f118504aee5463eab09d506610fe9
```

The full run IDs, causal measurements, per-artifact hashes, and validation
record are in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m3_spatial_suite_report.md
```

M2.3 remains a successful one-case development result. V6 and all historical
scenarios, worlds, case keys, results, and evidence remain immutable.

### Closeout checkpoint

The bounded material-boundary command passed:

```text
timeout 180s \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/\
checkpoint_phase.sh 08
```

It wrote
`docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt` against base
HEAD `d5d29aa2225c26d2bfa62f00a398b238b67a709b`. The retained-result commit
follows this precommit snapshot.

## Current milestone

**Phase 08.7 M3 — executed once, retained as FAIL at 1/5, and closed.**

### Next criterion

The retained-result checkpoint and commit close M3. No replacement suite,
retry, tuning, M4, readiness claim, Phase 09 action, or physical command is
authorized; await an explicit, separately planned next step.

## Phase 08.7 M4 authorization and planning boundary

On 2026-07-29 the user explicitly authorized planning and complete execution
of Phase 08.7 M4. The fresh amendment is now recorded in
`docs/codex/gesc_gaussian/plans/phase_08_7_plan.md`.

M4 is a new schema-v6, opt-in robust correction. It preserves M3 as an
immutable `1/5` failure and preserves M2.3, V6, every historical scenario,
world, case key, result, evidence root, topic, cost sign/unit, and controller
owner.

The pre-edit reconstruction found:

- branch `feature/gesc-gaussian-robustness-v1` at `a952909`, ahead of origin
  by `62`, with a clean worktree;
- Phase 08 implementation-context validation passed;
- no M4 implementation or evidence root existed;
- the `0.20 m` wall margin matches the rotating sensor's approximately
  `0.195 m` half-span and will not be reduced;
- the M3 radius-2.0 recenter started `0.5307223180 m` from room center,
  reached only `0.5072853892 m`, and diverged to `0.7761077767 m`;
- that run's fill-avoidance radius was approximately `0.6086747487 m`,
  while the fill center was only approximately `0.0815 m` from room center,
  making the old exact room-center target geometrically infeasible;
- post-recovery direction selection still applies a blanket nonnegative
  preferred-direction dot-product gate;
- targeted redesign still reconstructs from moving live buffers although the
  fill registry retains immutable accepted samples.

The M4 plan freezes:

- recoverable boundary behavior with the physical wall margin retained;
- safe proxy recenter targets and persistent circumnavigation;
- affine override/fallback, spatial taper, `0.50` post-recovery weight,
  `0.05 s^-1` decay, and `20.0 s` age;
- immutable redesign sample reuse with the `40`-sample floor unchanged;
- schema-v6 verified-trap Stage A and a non-gating `1.00 m` closer diagnostic;
- `1.20 m` primary two-light Stage B;
- one visible probe followed, only on pass, by five spatial and three repeat
  attempts;
- one optional three-light development attempt only after the complete
  two-light gate passes.

Physical hardware and Phase 09 remain unauthorized.

## Current milestone

**Phase 08.7 M4 — amendment authorized and saved; implementation has not
started.**

### Next criterion

Validate and checkpoint the M4 Plan boundary, commit it, then implement the
opt-in runtime and schema changes. Do not start Gazebo until source tests,
replays, regressions, isolated build, installed dry-run, launch
instantiation, historical immutability, checkpoint, and a clean qualified
commit all pass.

## Phase 08.7 M4 implementation and no-Gazebo qualification

The Plan-only M4 boundary was committed as `3b1edd4`. Implementation then
extended the existing robust owners without adding a controller, launch graph,
recorder, validator, simulation fork, or physical path.

### Implemented runtime correction

- The supervisor now distinguishes the physical room faces from the retained
  `0.20 m` wall-margin inset. Physical-room violations, invalid/stale data,
  explicit stop, controller/watchdog faults, clock reversal, invalid geometry,
  and exhausted recovery still latch zero-output `FAILSAFE`.
- Opt-in boundary pressure at `0.025 m` enters `RECENTER`. Motion from outside
  the inset must remain inside the physical room and strictly improve inset
  clearance. Motion from inside cannot cross outward, and motion already in
  the trigger band cannot reduce clearance. Interior fill-circumnavigation is
  not incorrectly frozen by a wall-clearance comparison.
- Recenter prefers room center, but selects a deterministic in-bounds proxy
  outside every active fill plus `0.05 m` when center is infeasible. The
  target is frozen for the episode, and a route planner retains one
  circumnavigation side until direct line-of-sight clears. Completion also
  requires the pose to be outside every active fill.
- Finite recenter timeouts retain the same target and route for only the
  remaining bounded recovery budget. They do not synthesize a recenter
  completion. Exhaustion remains terminal.
- Post-recovery direction selection now applies hard wall/fill segment safety
  without the old blanket backward-half-plane rejection. One empty candidate
  set requests recenter; if it is still empty after recenter, affine authority
  is cleared while the accepted Gaussian remains active.
- Post-recovery `SEARCH` reports affine weight `0.50`, tapers it to zero over
  `0.50 m` beyond active-fill support, and retains the fixed modified-cost
  decay `0.05 s^-1` and age `20.0 s`. `ESCAPE_ASSIST` retains full affine
  authority, while wall recovery and `RECENTER` override it.
- Targeted redesign can opt into the accepted cluster's immutable retained
  samples. Initial creation still requires `40` valid synchronized samples;
  the retained redesign also keeps the `40`-sample floor. Only an initial
  reason-`30` insufficient-sample rejection is retryable through fresh
  search/verification. Missing targets, malformed geometry, estimator/design
  failure, and invalid results remain terminal.

### Implemented evidence and fixed inputs

Schema version 6 adds only opt-in recovery controls,
`local_association_mode: verified_trap`, and
`global_closer_radius_m`. Schema versions 1 through 5 retain their normalized
shape and reject these fields.

`verified_trap` keeps the verified below-threshold controller decision,
unique convergence-to-fill association, fill-center tolerance, global
exclusion, accepted direct/one-redesign lifecycle, complete events, and exact
known-topology cardinality. Declared-local distance remains reported, but is
diagnostic. The new `1.00 m` closer result is non-gating; the primary
operator-equivalent Stage B and live stop remain `1.20 m`.

The committed-input candidates are:

```text
phase08_v7_m4_visible_probe.yaml       1 visible two-light case
phase08_v7_m4_two_light_suite.yaml     5 spatial + 3 repeat cases
phase08_v7_m4_three_light_probe.yaml   1 optional visible three-light case
```

The visible case key is
`a7d115b9893ee9b4ee0885a477820125ad68e21c93da689d858f69dc9aca9c32`.
The two-light central validation key is
`8b9b0605e83528496a25b78bb88bbd18af8ef43eb2da078e14a444ddd0a03057`;
all three repeat references bind that exact key. The optional three-light key
is `d4c7fe02cf52e3fab2c1cfd9e1d319305e0d22d546753633743fab5dfbb3a41a`.

### No-Gazebo test evidence

The final focused source envelope, in fresh ROS domain `148`, passed:

```text
256 passed, 1 skipped in 54.07 s
```

It covers the retained `39/40` boundary and same-cluster replacement,
boundary inward/outward sweeps, the exact M3 infeasible-center geometry and
persistent route, backward-safe post-recovery selection, empty-candidate
recenter/fallback, finite bounded retry exhaustion, hard-fault latching,
affine taper, verified-trap Stage A, exact cardinality, the non-gating closer
diagnostic, fixed M4 inputs, and M1 historical immutability. The skip is the
explicitly gated Gazebo integration.

The clean broad functional split passed:

```text
570 passed, 3 skipped, 1 deselected in 107.78 s
JUnit: /tmp/phase08_7_m4_functional_nonintegration.xml

12 passed in 3.26 s
JUnit: /tmp/phase08_7_m4_supervisor_integration.xml
```

The three skips are explicit runtime/Gazebo opt-ins. The one deselection is
the already-recorded stale
`test_v4_population_adoption_is_exact_and_unused`, whose immutable V4 hash
inventory treats later fixed V6 and V7 scenarios as drift. The V4 source and
adoption artifacts were not changed.

One combined long-process run produced
`581 passed, 3 skipped, 1 deselected, 1 failed`: the unchanged M2 topology
integration assertion missed a transient `SEARCH` state. That test passed
immediately alone, passed in the final 12-test integration file, and the full
focused envelope passed. A prior whole-tree invocation from repository root
also made the generic flake8/pep257 wrappers scan historical non-package
trees; those two wrapper failures and the same stale V4 assertion are
non-authoritative and did not launch ROS or Gazebo.

Same-configuration lint comparison across all 12 changed Python source/test
files is:

```text
HEAD:    930 findings = D 31, I 13, Q 886
current: 922 findings = D 31, I 13, Q 878
```

M4 adds no flake8 finding and removes eight. `ament_pep257` is unchanged at
`31/31`. Fatal `E9/F63/F7/F82`, Python compilation, `git diff --check`,
launch/world `xmllint`, and
`validate_phase_context.sh 08 implement` all pass.

### Build, installed dry-run, and launch evidence

The fresh isolated build passed:

```text
build base:   /tmp/phase08_7_m4_qual/build
install base: /tmp/phase08_7_m4_qual/install
log base:     /tmp/phase08_7_m4_qual/log
Summary: 3 packages finished in 11.6 s
```

Installed-executable dry-runs of the installed scenario definitions passed
with `[1, 8, 1]` resolved cases and zero unsupported cases:

```text
/tmp/phase08_7_m4_visible_installed_dry_run.yaml
/tmp/phase08_7_m4_two_light_installed_dry_run.yaml
/tmp/phase08_7_m4_three_light_installed_dry_run.yaml
```

They resolve exactly two, two, and three lights respectively; the fixed
start/global/local coordinates; exact topology/fill limits; `0.20 m` wall
margin; retained-sample redesign; bounded recovery; affine decay/age/weight;
`60.0 s` recenter; `1.20 m` primary Stage B; and `1.00 m` non-gating closer
diagnostic.

Nonexecuting installed central-launch expansion passed and retained a
`262`-line description at:

```text
/tmp/phase08_7_m4_launch_description.txt
```

It binds the new arguments into the existing modified-cost, Gaussian-fill,
and supervisor owners while retaining the existing controller graph.
Source and isolated-install bytes match:

```text
58eebc21f21561713a8cdf04d9a534f34efd5fc4f7ee4c0cf36e73be288af14e  Gaussian node
350857cbd930ea3c9df9ddae9706897e705418fe3075562d55861ae8c0bd4dc1  scenario runner
ed35836fc26228acfb91f5c74b562252a42d2b33ce9dee951cd1ed224219d904  scenario schema
4e7662dcbd74c792711138ed43ac4201c8543651e525b23eacbf9dcb300b543d  recenter helpers
1b61c3a6b056bc9a46d0cd44de08c88c28d71c85f1a804380abaf0c442baaba3  state machine
73f6c98957b2ee34d419b8aea37e8ad6e4c08a1d32d8fa76ce97860ec7b17b24  supervisor node
b402144a6d78999435e5470bd591d60c0518786f92527c8b78dd1cd8330e4e24  central launch
37ba6e1e9adc842691328cc0a1c66e5fd04034db59c6fcdb0c05f6f6c4b769a1  visible input
6e67e657b11f080a545abe6b87a8730112c350163e47f85ec6ac83ab32abb937  two-light input
1a9ac4774094d43822b7d33f5eba24566e15cf745b9481ce8f25720a8e42c721  three-light input
```

Historical anchors remain:

```text
88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf  shifted world
3be130581b88c986fd845aef0c33c9db94ceb02ecfe2a6361926b0317ef8e655  V6 hue sweep
3b9badc92cf63739f65662158999e3c2aab71761f790e3f360be9a52e6f38688  V6 repeats
1221d8cb9d7235218d4f3da710f10d41284632a93712bd89d763d938a0437dae  M3 suite
34f20a3bd66893be295c44f860e85645f6c9c182d82a658ee47bc785f3b42dba  M1 immutability manifest
```

All three M4 evidence roots remain absent and the Gazebo/runner/recorder
process set is inactive.

The bounded material-boundary checkpoint command passed and refreshed
`docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt` against base
HEAD `3b1edd4356e73675550f9928ca767621397692b2`.

## Current milestone

**Phase 08.7 M4 — implementation and no-Gazebo qualification PASS;
checkpointed; qualified commit pending.**

### Next criterion

Commit the exact qualified source, tests, launch wiring, scenarios, status,
and checkpoint. Reconfirm an inactive process set plus absent probe root, then
dispatch only the one fixed visible two-light probe.

## Phase 08.7 M4 committed dispatch boundary

The qualified M4 implementation, tests, launch wiring, and exact three
scenario inputs were committed at:

```text
19d413c9c129bcda9cf953741c95ed42c5913bc4
phase 08.7: qualify M4 recoverable navigation
```

The post-commit worktree is clean. Source and isolated-install scenario bytes
remain identical:

```text
37ba6e1e9adc842691328cc0a1c66e5fd04034db59c6fcdb0c05f6f6c4b769a1  visible probe
6e67e657b11f080a545abe6b87a8730112c350163e47f85ec6ac83ab32abb937  two-light suite
1a9ac4774094d43822b7d33f5eba24566e15cf745b9481ce8f25720a8e42c721  optional three-light probe
```

All three fresh evidence roots remain absent. The Gazebo, scenario-runner,
recorder, and matching ROS launch process set is inactive.

Exactly one visible two-light attempt is predeclared on ROS domain `153`:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m4_qual/install/setup.bash
ROS_DOMAIN_ID=153
ROS_LOG_DIR=/tmp/phase08_7_m4_probe_ros_logs
MPLCONFIGDIR=/tmp/phase08_7_m4_probe_mpl
TURTLEBOT3_MODEL=burger
DISPLAY=:0
timeout --signal=INT --kill-after=90s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m4_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m4_visible_probe.yaml \
  --operator phase08_7_m4 \
  --case-id v7_m4_probe_r1p5_a45_h25_18201 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_probe \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_probe/\
phase08_v7_m4_visible_probe_summary.yaml \
  --gui
```

The attempt is retained without automatic retry or in-run parameter changes.
The fixed eight-case suite is prohibited unless this probe passes
infrastructure, Stage A, exact fill cardinality, primary `1.20 m` Stage B,
collision, forbidden-state/event, and combined predicates. The optional
three-light attempt remains prohibited unless the visible probe and all eight
fixed two-light suite cases pass.

## Current milestone

**Phase 08.7 M4 — qualified input committed; one fixed visible two-light
probe predeclared.**

### Next criterion

Refresh the Phase 08 checkpoint against commit `19d413c`, commit this dispatch
record, reconfirm the process/evidence boundary, and execute only the bounded
visible probe.

## Phase 08.7 M4 retained visible-probe result

Exactly one bounded visible-Gazebo attempt ran on ROS domain `153` from the
committed scenario SHA-256
`37ba6e1e9adc842691328cc0a1c66e5fd04034db59c6fcdb0c05f6f6c4b769a1`.
The runner returned `1` without outer or recorder timeout. The run is retained
at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_probe/
  2026-07-30/
  20260730T054527662523Z_simulation_phase08_v7_m4_visible_probe-
  v7_m4_probe_r1p5_a45_h25_18201-robust_gaussian_v1-a7_e99d857b
```

The result is a formal **FAIL: recording evidence invalid**, even though every
declared behavioral and safety predicate passed:

```text
Stage A verified-trap recovery:       PASS
exact fill cardinality 1/1:           PASS
Stage B primary 1.20 m proximity:     PASS
collision expectation false:          PASS
forbidden state/event absence:        PASS
cleanup and final zero:                PASS
recording completeness:               FAIL
combined result:                       FAIL
```

The in-readiness path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

One convergence was confirmed at source time `248.5 s`. Cluster `1` was
created at `(1.1108335595, 1.3813284464) m`, `0.1865943066 m` from its
convergence point and `0.3953410337 m` from the declared local. Escape
completed successfully in `8.775931438 s`; recenter started and completed;
there was no redesign escalation, timeout, collision, or in-readiness
`FAILSAFE`.

The live global stop triggered on the first qualifying noninterpolated sample:

```text
position:                (3.1291616104, 2.3595487198) m
distance to global:      1.1992290164 m
primary radius:          1.20 m
valid post-A samples:    1710
invalid post-A samples:  0
```

The final classified distance was `1.1926238875 m`. The `1.00 m` closer
diagnostic was false and non-gating.

### Evidence-validator root cause

The sole completeness failure was one `/joint_states` header-stamp regression
from `271.747 s` to `271.522 s`, exceeding the fixed `0.150 s` tolerance by
`0.075 s`.

The live graph and retained resolved manifest show two intentional publishers:

```text
/joint_state_broadcaster
/turtlebot3_joint_state
```

Read-only bag deserialization found one `225 ms` rollback only in the merged
receipt order. The `33,181` effort-present and `9,769` effort-empty message
signatures independently had zero backward stamps. The three older
effort-empty messages arrived approximately `1.30 ms` after a newer
effort-present message. Simulation `/clock` was monotonic, every typed stamp
remained inside the `/clock` range, and all other timestamp, lifecycle,
final-zero, topic, parameter, collision, console, and cleanup checks passed.

The passing M2.3 bag contains the same two publishers and ten merged-order
rollbacks whose maximum happened to be only `1 ms`. The validator therefore
models a deliberately multi-publisher stream as one source-time sequence and
can turn GUI scheduling into a false recording failure. This is not a robot
clock reversal or a wall-margin, recenter, affine, collision, or navigation
failure.

Read-only sqlite `PRAGMA quick_check` returned `ok`. Standard analysis returned
`0`, wrote eight plots and eleven tables, and honestly reports
`analysis_status: partial` because the retained completeness document failed.
Exact commands, values, hashes, and the bounded fresh-correction requirement
are recorded in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_visible_probe_report.md
```

The fixed eight-case two-light suite and optional three-light probe were not
run. This failed fixed M4 attempt will not be retried, overwritten, or
relabelled.

## Current milestone

**Phase 08.7 M4 — visible behavior passed, but the formal probe and M4 gate
are closed FAIL on a multi-publisher timestamp-validation defect.**

### Next criterion

Checkpoint and commit the retained M4 result. A fresh version requires
explicit authorization to correct the shared evidence contract: preserve
strict clock/range and singleton-stream checks, declare the exact two
`/joint_states` publishers, avoid a merged-order monotonicity claim that
cannot identify producers, qualify without Gazebo, and dispatch one new
visible probe under a new evidence root before any suite.

## Phase 08.7 M4.1 authorization and planning boundary

On 2026-07-29 the user explicitly authorized the bounded correction identified
by M4. M4 remains an immutable formal failure. M4.1 does not change or retry
its case, seed, root, bag, completeness document, analysis, classification, or
scenario.

The saved M4.1 amendment extends only the existing Phase 05 manifest,
recorder, and validator owners. It freezes:

- exact `/joint_states` owners `/joint_state_broadcaster` and
  `/turtlebot3_joint_state`;
- additive `expected_publishers` and
  `timestamp_ordering: multi_publisher_within_clock` evidence fields;
- unchanged `0.150 s` tolerance;
- strict singleton/per-topic and per-producer `AlgorithmEvent`
  nonregression;
- monotonic `/clock` plus within-clock checks for every multi-publisher typed
  message;
- no navigation, wall, recenter, fill, affine, detector, collision, stop,
  geometry, light, or runtime-value change;
- one new visible case `v7_m4_1_probe_r1p5_a45_h25_18207`, seed `18207`,
  under the absent root
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_1_probe`.

The worktree was clean at retained-result commit `2d95deb`, the three M4
planning/implementation/result commits are intact, the M4.1 evidence root was
absent, and no Gazebo process was active. Phase 08 implementation-context
validation passed.

## Current milestone

**Phase 08.7 M4.1 — evidence correction authorized and saved; implementation
has not started.**

### Next criterion

Validate, checkpoint, and commit the Plan-only M4.1 boundary. Then implement
the exact publisher and timestamp-ordering contract, qualify it without
Gazebo, and commit the fresh visible input before any simulator process starts.

## Phase 08.7 M4.1 implementation and no-Gazebo qualification

The Plan-only M4.1 boundary was validated, checkpointed, and committed at:

```text
d96b65e585d403f54c381e091f85fdae431f0286
phase 08.7: plan M4.1 timestamp evidence correction
```

The shared Phase 05 recorder/validator now supports the additive optional
topic fields `expected_publishers` and `timestamp_ordering`. The absent
ordering field still resolves to `single_stream`. The only canonical topic
using `multi_publisher_within_clock` is simulation `/joint_states`, with the
exact owners:

```text
/joint_state_broadcaster
/turtlebot3_joint_state
```

Manifest loading rejects empty, duplicate, relative, underdeclared, physical,
optional, singleton-conflicting, and unknown-ordering contracts. Recorder
preflight and offline completeness both require an exact owner-list match.
Only the valid merged `/joint_states` sequence is excluded from the
single-stream nonregression assertion. Every one of its typed stamps remains
subject to monotonic `/clock` and the unchanged `0.150 s` within-clock
tolerance. Singleton typed topics and the independently attributed
`AlgorithmEvent` producer streams retain strict nonregression.

No navigation, detector, fill, affine, recenter, wall, collision, stop,
geometry, light, topic type, cost sign/unit, controller-owner, or runtime
value changed. The evidence semantics are also recorded in
`docs/codex/gesc_gaussian/topic_dictionary.md`.

### Source and regression evidence

The final focused recording/schema rerun passed:

```text
149 passed in 51.11 s
/tmp/phase08_7_m4_1_focused_final.xml
```

Earlier same-source qualification envelopes passed:

```text
212 passed, 2 skipped in 51.47 s
  /tmp/phase08_7_m4_1_recording_scenario.xml
573 passed, 3 skipped, 1 deselected in 109.66 s
  /tmp/phase08_7_m4_1_broad_functional.xml
12 passed in 3.27 s
  /tmp/phase08_7_m4_1_supervisor_integration.xml
```

The two skips in the recording/scenario envelope are the explicit opt-in
Gazebo integration tests. The three broad skips are existing opt-in/generated
tests. A deliberately broad nonintegration invocation that included the
generic package lint wrappers returned `2 failed, 573 passed, 3 skipped,
1 deselected`: `test_flake8.py` and `test_pep257.py` scanned inherited
whole-package debt. The matching changed-file comparison proves M4.1 adds no
finding:

```text
ament_flake8:
  HEAD:    815 = D202 18, E501 13, I101 1, Q000 783
  current: 815 = D202 18, E501 13, I101 1, Q000 783
ament_pep257:
  HEAD:    D202 18
  current: D202 18
```

Python compilation and `python3 -m flake8
--select=E9,F63,F7,F82` pass. `git diff --check` and
`validate_phase_context.sh 08 implement` pass.

The new focused tests prove:

- malformed ownership and ordering declarations fail manifest loading;
- exact preflight owners pass, while missing, duplicate, and unexpected
  endpoints fail;
- a merged `1.8 s -> 1.2 s` multi-publisher sequence passes only the scoped
  nonregression assertion while remaining inside `/clock`;
- an unexpected owner and an out-of-clock multi-publisher stamp fail;
- a singleton typed rollback and an `AlgorithmEvent` producer rollback fail;
- M4.1 has fresh identity while every nonidentity M4 behavior value matches;
- the sealed historical scenario-byte and normalized-key manifest still
  passes.

Read-only validation of the retained M4 directory with
`validate_run_directory(..., write_report=False)` remains failed on the same
`225 ms` legacy merged `/joint_states` rollback. Its old resolved contract
does not acquire the new ordering declaration, the new multi-publisher scope
is empty, and its immutable completeness SHA-256 is unchanged before and
after replay:

```text
4acc311734e63896faf33c07439b7c1c81e9ebdcd6902b0514bf9c9ce0846e88
```

This proves M4 was not retroactively relabelled.

Non-authoritative setup diagnostics did not start ROS or Gazebo: direct
execution of the relative-import source file failed before dry-run, a first
focused invocation omitted the built interface overlay and failed during
collection, and the shell name `flake8` was unavailable. The corrected module,
overlay, and `python3 -m flake8` forms produced the passing results above.

### Isolated build and installed evidence

The isolated build passed:

```text
build base:   /tmp/phase08_7_m4_1_qual/build
install base: /tmp/phase08_7_m4_1_qual/install
log base:     /tmp/phase08_7_m4_1_qual/log
Summary: 3 packages finished in 12.0 s
```

The installed executable dry-run at
`/tmp/phase08_7_m4_1_installed_dry_run.yaml` resolved exactly one supported
GUI case, zero unsupported cases, `89` launch argv entries, `108` recorder
argv entries, and the frozen case key:

```text
b5ac3146c6bb6b91c3d374031b3531d34c4a7506f03728c3688ae73cb7159400
```

Installed manifest loading resolves the exact two owners and
`multi_publisher_within_clock`. Source/install bytes match:

```text
4182d330ca43d2b48f14a0a388bcd86279adfbcc877e2fbcd19f4c14593c1a57  record_run.py
76614b2420b5f5f00c9b5da8e95d6394f561524c20da6f28b10f11c72404a64d  validate_run.py
2e131c4fc6aee447b3395a41ab62128fce8997e019012b475685902e40606843  topic manifest
2d881faa180c18c0b423671f12f91868e2b12d484a533909f607fef8372ca313  M4.1 probe
```

Historical anchors remain byte-identical:

```text
37ba6e1e9adc842691328cc0a1c66e5fd04034db59c6fcdb0c05f6f6c4b769a1  M4 visible
6e67e657b11f080a545abe6b87a8730112c350163e47f85ec6ac83ab32abb937  M4 two-light
1a9ac4774094d43822b7d33f5eba24566e15cf745b9481ce8f25720a8e42c721  M4 three-light
3be130581b88c986fd845aef0c33c9db94ceb02ecfe2a6361926b0317ef8e655  V6 hue sweep
3b9badc92cf63739f65662158999e3c2aab71761f790e3f360be9a52e6f38688  V6 repeats
1221d8cb9d7235218d4f3da710f10d41284632a93712bd89d763d938a0437dae  M3 suite
88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf  shifted world
```

The fresh M4.1 evidence root remains absent and the Gazebo, runner, recorder,
and matching launch process set remains inactive.

## Current milestone

**Phase 08.7 M4.1 — evidence correction implemented and no-Gazebo
qualification PASS; material-boundary checkpoint PASS; commit pending.**

### Next criterion

Commit this exact qualified boundary, record its full commit identity,
reconfirm a clean tree plus absent evidence root and inactive process set,
and only then dispatch the single authorized visible M4.1 probe.

## Phase 08.7 M4.1 committed dispatch boundary

The exact qualified evidence correction, tests, documentation, and fresh
scenario were committed at:

```text
7068a5f27a30918e38829548a359e7a66ae25df5
phase 08.7: qualify M4.1 timestamp evidence
```

The post-commit worktree is clean. Source and isolated-install probe bytes are
identical:

```text
2d881faa180c18c0b423671f12f91868e2b12d484a533909f607fef8372ca313
```

The fresh evidence root remains absent. The Gazebo, scenario-runner,
recorder, and matching ROS launch process set is inactive. Exactly one visible
attempt is predeclared on ROS domain `159`:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m4_1_qual/install/setup.bash
ROS_DOMAIN_ID=159
ROS_LOG_DIR=/tmp/phase08_7_m4_1_probe_ros_logs
MPLCONFIGDIR=/tmp/phase08_7_m4_1_probe_mpl
TURTLEBOT3_MODEL=burger
DISPLAY=:0
timeout --signal=INT --kill-after=90s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m4_1_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m4_1_visible_probe.yaml \
  --operator phase08_7_m4_1 \
  --case-id v7_m4_1_probe_r1p5_a45_h25_18207 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_1_probe \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_1_probe/\
phase08_v7_m4_1_visible_probe_summary.yaml \
  --gui
```

The attempt will be retained without retry or in-run value changes. The fixed
eight-case suite and optional three-light probe remain prohibited under this
authorization.

## Current milestone

**Phase 08.7 M4.1 — qualified input committed; one fixed visible two-light
probe predeclared.**

### Next criterion

Refresh the Phase 08 checkpoint against commit `7068a5f`, commit this dispatch
record, reconfirm the process/evidence boundary, and execute only the bounded
visible M4.1 probe.

## Phase 08.7 M4.1 retained visible-probe result

Exactly one visible-Gazebo attempt ran on ROS domain `159` from committed
scenario SHA-256
`2d881faa180c18c0b423671f12f91868e2b12d484a533909f607fef8372ca313`.
The recorder returned `0` without timeout; the runner returned `1` because
the combined behavioral contract failed. The run is retained at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_1_probe/
  2026-07-30/
  20260730T063749069795Z_simulation_phase08_v7_m4_1_visible_probe-
  v7_m4_1_probe_r1p5_a45_h25_18207-robust_gaussian_v_a3af59ef
```

A first combined shell guard stopped before launch after matching its own
later `run_scenario` text. It created no evidence root and started no Gazebo
process. The guard and command were separated before the single actual
attempt.

The M4.1 evidence correction passed completely, while the fixed fresh
behavior exposed a genuine Stage B failure:

```text
recording completeness:                   PASS
exact /joint_states owners:               PASS
multi-publisher timestamp scope:          PASS
all typed stamps inside /clock:           PASS
singleton/event timestamp nonregression:  PASS
Stage A local recovery:                   PASS
exact fill cardinality 1/1:               PASS
Stage B primary 1.20 m proximity:         FAIL
collision expectation false:              PASS
forbidden in-readiness states/events:      PASS
final zero/readiness/cleanup:              PASS
combined result:                           FAIL
```

All `48` completeness checks passed. `/joint_states` resolved exactly
`/joint_state_broadcaster` and `/turtlebot3_joint_state`; the ordering scope,
monotonic `/clock`, unchanged `0.150 s` within-clock tolerance, singleton
nonregression, per-producer event nonregression, final commands, final
readiness, sqlite integrity, and cleanup all passed. Read-only
`PRAGMA quick_check` returned `ok` for `768,138` messages.

Stage A completed the direct path and resumed `SEARCH` at simulation time
`311.0 s`. Convergence at source time `279.9 s` was `0.0654552587 m` from
the declared local. Fill/cluster `1` was centered at
`(1.1169995189, 1.0055016861) m`, `0.1276227945 m` from convergence.

The remaining `49.606 s` contained `1,460` valid and zero invalid post-A
odometry samples. The first, best, and final global distances were:

```text
first: 2.7053139770 m
best:  2.3996759290 m
final: 2.4331356924 m
```

The robot traveled `3.3343982367 m` after Stage A but displaced only
`0.2826786800 m`, looping near the recenter region. There was no collision,
wall stop, safety failsafe, evidence defect, or extra/missing fill. Compared
with retained M4 over the same post-A duration, path length was similar but
global-distance gain was `0.3056380480 m` instead of `0.9439522646 m`;
duration alone is not the full cause.

The retained evidence supports a post-recovery liveness defect: recenter
completed `0.3412297750 m` from its target at the edge of the `0.35 m`
tolerance; the correctly localized fill was farther from that endpoint; the
fill-centered affine taper resumed around weight `0.23` rather than M4's
approximately `0.36` and faded with distance; and no supervisor progress
monitor detects substantial path length with low net translation in guided
`SEARCH`.

Standard analysis returned `0` with `analysis_status: complete`, eight plots,
eleven tables, and no analysis or recording failure. Exact execution,
comparison, diagnosis, retained hashes, and a bounded fresh-version
recommendation are recorded in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_1_visible_probe_report.md
```

The fixed eight-case suite and optional three-light probe were not run. M4.1
will not be retried, extended, overwritten, or retuned in place.

## Current milestone

**Phase 08.7 M4.1 — evidence correction PASS; fixed visible probe retained
as formal Stage B / combined FAIL; result checkpoint PASS; commit pending.**

### Next criterion

Commit the retained result. Any further implementation requires a fresh,
explicitly authorized version that corrects post-recovery liveness without
weakening proximity, evidence, collision, or cleanup gates.

## Phase 08.7 M4.1 retained-result commit boundary

The retained result, exact analysis, live status, and validation report were
committed at:

```text
0f66c59e597f4e2416ca2120d0a45f68ed79385a
phase 08.7: retain M4.1 visible probe result
```

The post-commit worktree is clean. The Gazebo, scenario-runner, recorder, and
matching launch process set is inactive. The retained M4 completeness hash
remains unchanged at
`4acc311734e63896faf33c07439b7c1c81e9ebdcd6902b0514bf9c9ce0846e88`;
the M4.1 completeness hash remains
`afd4cbd707004e2a8b6965ea08f1db1329a08ff816ff0965b821d95f28a0fcc0`.

## Current milestone

**Phase 08.7 M4.1 — CLOSED / FORMAL FAIL on Stage B and combined behavior;
evidence correction independently PASS and retained for future versions.**

### Next criterion

Stop. No suite, three-light, physical, or additional Gazebo execution is
authorized. A post-recovery liveness correction requires a fresh Plan and
explicit user approval.

## Phase 08.7 M4.2 authorization and planning boundary

On 2026-07-30 the user explicitly authorized the fresh full correction after
reviewing the M4.1 Stage B diagnosis. The active subphase Plan now records
M4.2 as a schema-v7, robust-only, default-off correction. M4.1 remains closed
and immutable: its evidence correction passed, while its fixed behavior
failed Stage B and combined success.

The M4.2 contract fixes all six retained diagnosis items within existing
owners:

- a fresh direction/progress epoch at `RECENTER_COMPLETE`;
- safe bounded supervisor translation until `0.60 m` outward progress;
- progress-coupled affine hold and taper;
- a `12.0 s` high-path/low-net liveness detector with one direction refresh,
  one nonterminal recoverable recenter, and ordinary-SEARCH fallback;
- `0.15 m` recenter tolerance plus paired robust PDE-history reset;
- a schema-v7 `120.0 s` post-Stage-A budget inside bounded
  `480 / 660 / 45 s` run/wall/shutdown limits.

The fixed first attempt is visible case
`v7_m4_2_probe_r1p5_a45_h25_18208`, seed `18208`, under:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_2_probe
```

That root is not yet created. No implementation, fresh scenario, Gazebo
process, suite, three-light run, Phase 09 action, or physical command has
started.

## Current milestone

**Phase 08.7 M4.2 — correction authorized and Plan amendment saved;
Plan validation and checkpoint PASS; Plan-only commit pending.**

The Plan-only boundary was checked with:

```text
bash DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 plan
Phase 08 plan context is complete.

git diff --check
PASS

bash DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh 08
PASS
```

The fresh evidence root is absent. No Gazebo, scenario-runner, or recorder
process is active; the only `pgrep` match during the guard was the guard shell
containing its own search text. The worktree changes are limited to this
status, the active subphase Plan, and the generated Phase 08 checkpoint.

### Next criterion

Refresh the checkpoint for this exact status and commit the Plan-only
boundary. Then implement and qualify the complete M4.2 correction without
Gazebo.

## Phase 08.7 M4.2 Plan commit boundary

The exact authorized amendment, live-status planning record, and refreshed
checkpoint were committed before implementation at:

```text
99aa6bd
phase 08.7: plan M4.2 post-recovery liveness
```

M4.1 and every earlier scenario/result remain closed and immutable.

## Phase 08.7 M4.2 implementation and no-Gazebo qualification

M4.2 extends only the existing robust supervisor, paired PDE-history owners,
convergence detector epoch gate, custom-controller command path, central
launch, schema, and scenario runner. It adds no node, recorder, validator,
launch graph, simulation/physical fork, message, or `/cmd_vel` publisher.
Every new runtime control is robust-only, opt-in, and default off.

### Implemented post-recovery behavior

- `RECENTER -> SEARCH` now creates one fresh progress/direction epoch anchored
  at the next accepted local-recovery boundary. It discards the escape-era
  direction, recomputes a hard-safe direction, and increments the existing
  typed direction revision.
- The supervisor publishes only its existing
  `/gesc_gaussian/supervisor_command` contribution. The existing custom
  controller remains the sole `/cmd_vel` owner and combines/saturates that
  contribution with GESC.
- Safe direct translation remains active until `0.60 m` measured outward
  progress. The affine contribution remains at full configured post-recovery
  weight through `0.60 m`, tapers over the next `0.50 m`, and releases after
  `1.10 m` outward progress or the fixed `90.0 s` maximum. Negative or zero
  outward progress does not consume this distance budget.
- The exact-window liveness tracker uses `12.0 s`, `0.60 m` path, and
  `0.20 m` maximum displacement. Duplicate stamps are ignored, backward time
  is rejected, and the exact window boundary is interpolated. The first loop
  refreshes direction once; the next requests one recoverable recenter; a
  recurrence after that recenter releases the extra guidance and continues
  ordinary SEARCH without entering `FAILSAFE`.
- Every translation still passes the existing wall/fill/persistence command
  sweep. An unsafe translation becomes zero while safe angular
  alignment/replanning continues. Physical-room violation, invalid/stale
  data, hard controller faults, explicit stop, nonfinite data, and exhausted
  hard-navigation recovery remain terminal zero-output failures.
- The existing position and cost PDE-history owners share a typed
  `SearchEpochGate`. With
  `robust_search_epoch_reset_enabled:=True`, each new SEARCH boundary arms one
  paired reset, and each owner waits for its next finite pose/cost sample.
  Default-off and legacy behavior are unchanged; the accepted fill registry
  remains intact.
- Schema v7 requires the progress/history dependencies and a positive
  `post_stage_a_timeout_sec` below the run timeout. The live runner starts the
  `120.0 s` simulation-time budget only after Stage A and exact fill
  cardinality are both observed. A qualifying global sample wins immediately,
  including at the same timestamp as budget expiry; expiry is a graceful
  behavioral failure rather than an infrastructure wall timeout.

The fixed M4.2 inputs are:

```text
phase08_v7_m4_2_visible_probe.yaml       1 visible GUI case, seed 18208
phase08_v7_m4_2_two_light_suite.yaml     5 spatial + 3 repeat headless cases
```

The visible case key is
`d4aaa0d2d7e4af20c7721d2912620fe2a0a2f9f16004c462a0299e235f2866c8`.
The eight suite keys, in fixed execution order, are:

```text
8cf1f923bfb6a876e7d43fbc23ece7d455b7c5f902d7e183a898c8525e9515cd
cc18feff229376ba27b2a476a03ec6221e29fc1ac0ac0d461df33b1df3cfe8e5
45c7f2d178557c65713246cfbc8580a2bc1f8841d4fe3e74bc877b95448008fa
0f999a6cbeef8742327fe6fa82037ab33d58f2e424f519fe7bcbbb190e1d76db
803bdde8526d72574eb2e70eb93244a88f26c472e1f5e61bde5739877d6338f2
4d789ca92b889348b46b628e14c5f2e6717403ca0fc57b173d1d8f6060f22e3e
79c628f86d0f65010a2a4137fe89653d39e107a9a661bea6f316f581d9fdae97
24594df685cfad8f5295f8ca8bdaf557c9feb234f306cda683a0360cd1c80446
```

All three reproducibility cases bind the central validation key
`45c7f2d178557c65713246cfbc8580a2bc1f8841d4fe3e74bc877b95448008fa`.

### No-Gazebo source-test evidence

Focused correction envelopes passed:

```text
11 passed, 118 deselected   exact-window progress/liveness plus schema
10 passed, 12 deselected    paired histories plus supervisor integration
4 passed, 77 deselected     live runner budget plus launch contract
18 passed, 41 deselected    final typed reporting/recovery regression
10 passed                  final schema-v7 negative/compatibility regression
```

The final broad functional command was bounded and produced:

```text
timeout --signal=INT --kill-after=20s 300s \
  python3 -m pytest -q ros2_ws/src/ros_esc/test \
  --ignore=ros2_ws/src/ros_esc/test/test_flake8.py \
  --ignore=ros2_ws/src/ros_esc/test/test_pep257.py \
  -k 'not v4_population_adoption_is_exact_and_unused' \
  --junitxml=/tmp/phase08_7_m4_2_broad_functional_final.xml

609 passed, 3 skipped, 1 deselected in 115.26 s
```

JUnit SHA-256:

```text
f4e6958f06b27a3667674068ea97c6450e9bb18b385ba0e0b2a82bd0215d0aaa
```

The three skips are exact existing opt-ins:

- generated-source copyright header is absent;
- `DSIM_RUN_GAZEBO_RECORDING_TEST=1` was not set;
- `RUN_GESC_PHASE06_GAZEBO_E2E=1` was not set.

The single deselection is the sealed stale
`test_v4_population_adoption_is_exact_and_unused`, which treats later fixed
V6/V7 additions as drift. M4.2 changes none of its immutable V4 inputs. A
nonfatal rclpy destroyable warning printed after the passing process result;
the command exited zero and JUnit has zero errors/failures.

Fatal `E9/F63/F7/F82` checking across every changed Python source/test file,
Python compilation, `git diff --check`, source and installed `xmllint`, and:

```text
bash DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 implement
```

all pass.

The passing tests directly cover:

- exact-window interpolation, progress, liveness, duplicate stamps, backward
  time, and invalid parameter relations;
- new SEARCH anchoring/direction revision, safe command, progress release,
  affine hold/taper, one refresh, one recenter, maximum-time release, and
  nonterminal fallback;
- wall/fill command-sweep suppression plus retained physical-room and
  hard-fault `FAILSAFE` latching;
- paired finite-sample history reset and legacy/default-off preservation;
- schema-v1-through-v6 compatibility, schema-v7 dependencies, fixed case keys,
  topology/fill cardinality, and historical byte hashes;
- live Stage A/cardinality start, global-stop precedence, graceful budget
  failure, and independent infrastructure wall-timeout classification;
- retained M4/M4.1 evidence, geometry, direction, wall, command, ownership,
  timestamp, topic, cost-sign, and unit regressions.

### Isolated build and installed qualification

The fresh isolated three-package build passed:

```text
source /opt/ros/humble/setup.bash
timeout --signal=INT --kill-after=20s 180s \
  colcon --log-base /tmp/phase08_7_m4_2_qual/log build \
  --base-paths ros2_ws/src \
  --build-base /tmp/phase08_7_m4_2_qual/build \
  --install-base /tmp/phase08_7_m4_2_qual/install \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor \
  --event-handlers console_direct+

Summary: 3 packages finished in 12.3 s
```

Installed-executable dry-runs passed:

```text
/tmp/phase08_7_m4_2_visible_installed_dry_run.yaml
  resolved_run_count: 1
  unsupported_count: 0
  gazebo_gui: True

/tmp/phase08_7_m4_2_suite_installed_dry_run.yaml
  resolved_run_count: 8
  unsupported_count: 0
  gazebo_gui: False for all eight
```

Each installed case resolves schema v7, `post_stage_a_timeout_sec: 120.0`,
the progress/liveness controls, paired history reset, fixed two-light
geometry, exact known topology, one-fill limit, `1.20 m` primary stop, and
`1.00 m` closer diagnostic. The summary hashes are:

```text
2024600c86723135c7b19f97e668804d6782cb0798616805d17ee62c343b4031  visible
35a10229a1c5265a278b53630f04a2ce2c3b72b775b0ded3602515a8b595ec4c  suite
```

Nonexecuting installed `ros2 launch -p` expansion of the exact visible
`launch_argv` passed with `92` supplied launch arguments and retained its
`270`-line description at:

```text
/tmp/phase08_7_m4_2_installed_launch_description.txt
05f213dd2b0f317a55d5b75f42bae17e9cbb34e2c9207998080de8163cdc11e1
```

It binds the new parameters into the existing supervisor and paired
PDE-history processes. The central launch contains exactly one `/cmd_vel`
argument, owned by `controller_node`; the supervisor retains only
`/gesc_gaussian/supervisor_command`.

Production Python, both new scenarios, and the central launch are
byte-identical between source and the isolated install. Source hashes are:

```text
b3af244b14adc42e8efc315d5544dd7109380b4e98d6c1a69d7cfe347e64dc05  convergence detector
9f29dd9c9e0534a4e28515c404409ef3e69004916af7f3777696a7704432b1c0  cost PDE history
b8fb551adbd9a0ccfcfddb9830e8a7cc5b9e30ad60ee09f7cb5763acf83f212e  pose PDE history
55d32f36dcbbdf24b7a6f3af9a3670e6c1941b3af9794a6c5a8feb04e8713906  scenario runner
57f797fc106c0246e4d1b12599b45f7e7fd67c35cc8545f68848294169fed8e7  scenario schema
50128f2c98ee909b8c564cba855fecc0fa9d926609e9086d9a2ca6e5d2c7b458  SEARCH epoch gate
ff643987f2f874207dc23d083390fcaa854bdd12b16147272a5a09e42704f1a2  recenter/progress helpers
ffd55910474d6cae7b5af85c3b8a3b8362c0aee1ebe55fecbae3f89d677a7ab2  supervisor
e6ec6120df271afab3ae71192b601c4bcf866105a8cdaa13a10dcd94b7632973  visible input
8d56eb4872aafc485103f8ddd2e03a7105101fd97b8b26b532e880a9d7c84219  suite input
4e8b9a187362abac31a21e70fbb1d4df220686c6ee37a9f94a3426e8d7de2f1f  central launch
```

### Historical and evidence immutability

Historical source anchors remain:

```text
3be130581b88c986fd845aef0c33c9db94ceb02ecfe2a6361926b0317ef8e655  V6 hue sweep
3b9badc92cf63739f65662158999e3c2aab71761f790e3f360be9a52e6f38688  V6 repeats
1221d8cb9d7235218d4f3da710f10d41284632a93712bd89d763d938a0437dae  M3 suite
37ba6e1e9adc842691328cc0a1c66e5fd04034db59c6fcdb0c05f6f6c4b769a1  M4 visible
2d881faa180c18c0b423671f12f91868e2b12d484a533909f607fef8372ca313  M4.1 visible
6e67e657b11f080a545abe6b87a8730112c350163e47f85ec6ac83ab32abb937  M4 two-light
1a9ac4774094d43822b7d33f5eba24566e15cf745b9481ce8f25720a8e42c721  M4 three-light
88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf  shifted world
8ecc1a231efec24401d74fef3cd5139d48c6029f88e71d044cefdf2fd14c5bef  historical world
```

Read-only hashing of the actual retained evidence confirms:

```text
4acc311734e63896faf33c07439b7c1c81e9ebdcd6902b0514bf9c9ce0846e88  M4 completeness
afd4cbd707004e2a8b6965ea08f1db1329a08ff816ff0965b821d95f28a0fcc0  M4.1 completeness
```

The fresh probe and suite evidence roots remain absent. The Gazebo,
scenario-runner, recorder, and matching launch process set is inactive. No
Gazebo or physical process was started during M4.2 implementation or
qualification.

The bounded material-boundary checkpoint command passed and refreshed
`docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt` against base
HEAD `99aa6bd85783d1c017b49306b85d32c1a7eb46bf`. The checkpoint is refreshed
again after this status update so it snapshots the exact qualified precommit
boundary whose only next action is the authorized commit.

## Current milestone

**Phase 08.7 M4.2 — implementation and all required no-Gazebo qualification
criteria PASS; material-boundary checkpoint PASS; qualified commit pending.**

### Next criterion

Inspect the complete implementation/status/checkpoint diff and commit the
qualified implementation plus fixed fresh inputs. Only after that clean
committed boundary may the single authorized visible two-light probe be
dispatched.

## Phase 08.7 M4.2 committed dispatch boundary

The exact qualified M4.2 implementation, tests, fresh fixed inputs, live
status, and precommit checkpoint were committed at:

```text
a1f58fb8b706181823877de35ff029fa812402bb
phase 08.7: qualify M4.2 post-recovery liveness
```

The post-commit worktree is clean and the implementation context validator
passes. Source and isolated-install probe bytes are identical:

```text
e6ec6120df271afab3ae71192b601c4bcf866105a8cdaa13a10dcd94b7632973
```

The fresh probe and suite evidence roots remain absent. The Gazebo,
scenario-runner, recorder, and matching launch process set is inactive.
`DISPLAY=:0` passes `xdpyinfo`, `316 GiB` is free on the evidence filesystem,
and ROS domain `160` has no discovered nodes with the CLI daemon disabled.

Exactly one visible attempt is predeclared:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m4_2_qual/install/setup.bash
ROS_DOMAIN_ID=160
ROS_LOG_DIR=/tmp/phase08_7_m4_2_probe_ros_logs
MPLCONFIGDIR=/tmp/phase08_7_m4_2_probe_mpl
TURTLEBOT3_MODEL=burger
DISPLAY=:0
timeout --signal=INT --kill-after=90s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m4_2_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m4_2_visible_probe.yaml \
  --operator phase08_7_m4_2 \
  --case-id v7_m4_2_probe_r1p5_a45_h25_18208 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_2_probe \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_2_probe/\
phase08_v7_m4_2_visible_probe_summary.yaml \
  --gui
```

This attempt will be retained without retry or in-run value changes. The
fixed eight-case suite remains conditional on a complete visible-probe pass;
the optional three-light probe remains conditional on the complete two-light
gate.

## Current milestone

**Phase 08.7 M4.2 — qualified implementation committed; one fixed visible
two-light probe predeclared.**

### Next criterion

Refresh the Phase 08 checkpoint against commit `a1f58fb`, commit this dispatch
record, reconfirm the clean process/evidence boundary, and execute only the
bounded visible probe.

## Phase 08.7 M4.3 retained visible-probe result

Exactly one visible-Gazebo attempt ran on ROS domain `161` from committed
scenario SHA-256
`cacbdafbc9aa289f178e684503519283bdf4b5496cbdd2dfb8c61ff69ebf1658`.
The run is retained at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3_probe/
  2026-07-30/
  20260730T085116266752Z_simulation_phase08_v7_m4_3_visible_probe-
  v7_m4_3_probe_r1p5_a45_h25_18308-robust_gaussian_v_91c59c52
```

The suite started at `2026-07-30T08:51:15.319251Z`, completed at
`2026-07-30T08:56:09.342914Z`, and returned `0`. The fixed visible result is
**PASS**:

```text
recording completeness:                   PASS (48/48)
required state path and events:           PASS
Stage A local recovery:                   PASS
exact fill cardinality 1/1:               PASS
Stage B primary 1.20 m proximity:         PASS
post-Stage-A budget:                      PASS (not expired)
collision expectation false:              PASS
forbidden in-readiness states/events:      PASS
final zero/readiness/cleanup:              PASS
combined result:                           PASS
```

The accepted path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

Exactly one fill was created. Pure Gaussian repulsion escaped in
`8.735487521 s`, and recenter completed `0.1452067367 m` from its fixed
safe-proxy target, inside the `0.15 m` tolerance.

The M4.3 guidance epoch started at simulation time `216.1 s` and released
normally at `236.7 s`:

```text
epoch path length:            1.7596027588 m
epoch net displacement:       1.1082037413 m
outward progress:             1.1045059990 m
12 s window path:             1.0635155091 m
12 s window displacement:     0.8501738801 m
direction refresh count:      0
liveness recenter attempted:  false
```

The first qualifying noninterpolated Stage B sample arrived approximately
`25.36 s` into its independent `120.0 s` budget:

```text
pose:                      (2.9945190974, 2.4141474035) m
distance to global:        1.1977423781 m
valid post-A samples:      747
invalid post-A samples:    0
interpolation used:        false
```

The non-gating `1.00 m` closer diagnostic was not reached.

Both new `post-recovery ` configuration events passed producer
identification, per-producer ordering, and freshness. Read-only sqlite
`PRAGMA quick_check` returned `ok` for `513,328` messages. Standard analysis
returned `0`, reports `complete` with no analysis failures, and retained eight
plots and eleven tables.

Exact execution, behavior, evidence, and hashes are recorded in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_3_visible_probe_report.md
```

Key retained hashes are:

```text
38565f76dc00424fecc6a4ac032ba9376a8cd8eb90e400f3fe2410ee6a5a93de  suite summary
a8a3c54c11028c7746ae4739f9357e7bb2245fc69c5b51cd5793a82c36d60390  completeness
6065e89a36628df5fa79bd04f3c6dbdeeb04fca137968c77d575c60ea94312e4  scenario result
5346b6d8b2cbaa6bcfeedfe6abd071fbcca57291abb80cbbf2d9bdc7654566b9  sqlite bag
eeac4d8f77d0dd5f94723f9f95f9edb760fa18670b4edb84be19fc238bdb6ba3  analysis completeness
5e0700b9410c02a18bfed7808bb6c1b52b255bf03f7c2316d88d3333cd424b8b  summary metrics
```

The visible pass opens the fixed serial M4.3 two-light suite. It does not by
itself establish readiness. The suite input remains committed at SHA-256
`37c1f7f2d81132be46adee576a1b603093fd03dd5488c5465d53d8876b9d50cc`;
its evidence root remains absent. All Gazebo, runner, and recorder processes
are inactive after the visible cleanup.

The exact suite dispatch is:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m4_3_qual/install/setup.bash
export ROS_DOMAIN_ID=162
export ROS_LOG_DIR=/tmp/phase08_7_m4_3_suite_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m4_3_suite_mpl
export TURTLEBOT3_MODEL=burger
timeout --signal=INT --kill-after=90s 5400s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m4_3_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m4_3_two_light_suite.yaml \
  --operator Codex \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3 \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3/\
phase08_v7_m4_3_two_light_suite_summary.yaml
```

Every case runs once in committed order and is retained regardless of
behavioral outcome. A cleanup failure stops later dispatch. No failed case is
retried or changed.

## Current milestone

**Phase 08.7 M4.3 — fixed visible probe PASS; serial eight-case two-light
qualification is now authorized by the passing gate but has not started.**

### Next criterion

Checkpoint and commit the immutable visible pass plus exact suite dispatch
record. Reconfirm the clean process/root/domain boundary, then run only the
committed eight-case suite on ROS domain `162`. The optional three-light probe
remains unauthorized.

## Phase 08.7 M4.2 retained visible-probe result

Exactly one visible-Gazebo attempt ran on ROS domain `160` from committed
scenario SHA-256
`e6ec6120df271afab3ae71192b601c4bcf866105a8cdaa13a10dcd94b7632973`.
The run is retained at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_2_probe/
  2026-07-30/
  20260730T081058251159Z_simulation_phase08_v7_m4_2_visible_probe-
  v7_m4_2_probe_r1p5_a45_h25_18208-robust_gaussian_v_56b72dfe
```

The runner started at `2026-07-30T08:10:57.281166Z`, completed at
`2026-07-30T08:18:20.539562Z`, and returned `1`. The recorder did not time
out; cleanup passed with no remaining new nodes or session processes. The
Gazebo, runner, recorder, and matching launch process set is inactive.

The formal result is **FAIL: recording evidence invalid**. The behavioral
correction independently passed:

```text
recording completeness:                   FAIL (47/48)
required state path and events:           PASS
Stage A local recovery:                   PASS
exact fill cardinality 1/1:               PASS
Stage B primary 1.20 m proximity:         PASS
post-Stage-A budget:                      PASS (not expired)
collision expectation false:              PASS
forbidden in-readiness states/events:      PASS
final zero/readiness/cleanup:              PASS
combined formal result:                    FAIL
```

The accepted path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

Exactly one fill was created. Pure repulsion escaped in `8.362181527 s`, and
recenter completed `0.1349758792 m` from its fixed safe-proxy target, inside
the new `0.15 m` tolerance.

The M4.2 post-recovery epoch started at simulation time `340.0 s`. It released
normally at `359.1 s` after:

```text
epoch path length:            1.6420006682 m
epoch net displacement:       1.1386958164 m
outward progress:             1.1087168804 m
12 s window path:             1.0305195589 m
12 s window displacement:     0.7656182086 m
direction refresh count:      0
liveness recenter attempted:  false
```

The runner began Stage B at `340.022 s` and stopped on the primary global
sample at `361.918 s`, only `21.896 s` into the independent `120.0 s` budget:

```text
pose:                      (2.9001106472, 2.4628184159) m
distance to global:        1.1981706364 m
valid post-A samples:      645
invalid post-A samples:    0
interpolation used:        false
```

The non-gating `1.00 m` closer diagnostic was not reached.

### Evidence defect

Only `algorithm_event_producer_identified` failed. The two unidentified
messages are finite, fresh, nonregressing supervisor-owned
`EVENT_CONFIGURATION` records:

```text
post-recovery guidance epoch started
post-recovery outward progress completed
```

The shared-bus validator classifies configuration-event ownership through a
closed prefix table. It contains the supervisor's older `measured escape`
prefix but not the new M4.2 `post-recovery ` prefix.

A read-only in-memory replay added only:

```text
EVENT_CONFIGURATION + detail.startswith("post-recovery ")
-> supervisor
```

With `write_report=False`, that replay passed every completeness check:

```text
patched_read_only_passed:             true
failures:                             []
algorithm_event_producer_identified:  PASS
typed_timestamps_nonregressing:       PASS
algorithm_event_emission_fresh:       PASS
```

The retained M4.2 `completeness.json` remains unmodified and failed. The
defect is evidence attribution coverage, not navigation, timestamp content,
publisher ownership, or acceptance thresholds.

Read-only Python sqlite `PRAGMA quick_check` returned `ok`; the bag contains
`772,486` messages. Standard bounded analysis returned `0`, with no analysis
failure, eight plots, and eleven tables under `analysis/phase07`. Its status
is correctly `partial` only because the stored/fresh Phase 05 validation sees
the same recording failure. Three existing assumed-fallback warnings remain
for channel index, sync tolerance, and supervisor publish rate.

Exact execution, behavior, evidence diagnosis, immutable replay, and retained
hashes are recorded in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_2_visible_probe_report.md
```

Key retained hashes are:

```text
9d296d50c203804f3938bcb22379b6b6bc6c5636d9c5880bded51ee4a75043ad  suite summary
4abaecc2dacf8fb544de01ba198e4e26792566c5cc44c059e6d99e4802d746d0  completeness
b7f4a57a973f79ff9e2b07c5ad7c8968f341b7ee0d3fa6b3b2c9029fd07984fe  scenario result
7dd10ccd0231cd9e17eb8b9e1a76d8dbba5779d19d7c8fd2e1dc2f3d8093af66  sqlite bag
414a9537a888adc30fc0b586b8c5832cb1039c6271913639c0264d0d7eb537cc  analysis completeness
2da54701a71a5ee4befe788461af766f19f1333107b928730d286032d5d736d4  summary metrics
```

The fixed eight-case suite and optional three-light probe were not run.
M4.2 will not be retried, overwritten, relabelled, or extended.

## Current milestone

**Phase 08.7 M4.2 — CLOSED / FORMAL FAIL on recording completeness and
combined result; Stage A, exact fill, Stage B, collision, cleanup, and the
post-recovery behavioral correction independently PASS.**

### Next criterion

Checkpoint and commit the retained result. Any new code or simulation requires
a fresh, explicitly authorized version. The smallest correction is to extend
the existing AlgorithmEvent configuration-prefix map with
`("post-recovery ", "supervisor")`, prove M4.2 read-only replay while keeping
its failed file immutable, preserve M4/M4.1 outcomes and hashes, requalify
without Gazebo, and use a fresh case/seed/evidence root for the next visible
gate.

## Phase 08.7 M4.3 authorization and Plan boundary

The M4.2 retained-result boundary was committed at `c418808`
(`phase 08.7: retain M4.2 visible probe result`). The user then explicitly
authorized the diagnosed correction with: "Great, then make that fix."

M4.3 is therefore a fresh Level B evidence-contract correction. It adds only
the existing supervisor's `post-recovery ` configuration-event prefix to the
closed AlgorithmEvent producer map, extends the existing recording tests, and
creates fresh visible and conditional two-light scenario identities. It does
not change navigation, thresholds, safety classification, wall handling,
affine guidance, Stage A/B behavior, or any M4.2 fixed launch value.

Fresh fixed identities are:

```text
visible suite/version:  phase08_v7_m4_3_visible_probe
                        phase08-v7-m4-3-probe
visible case/seed:      v7_m4_3_probe_r1p5_a45_h25_18308 / 18308
visible evidence root:  /home/mattb/Experiments/GESC-Gaussian/runs/
                        phase08_v7_m4_3_probe
headless suite/version: phase08_v7_m4_3_two_light_suite
                        phase08-v7-m4-3
headless seeds:         18309, 18310, 18311, 18312
headless evidence root: /home/mattb/Experiments/GESC-Gaussian/runs/
                        phase08_v7_m4_3
```

The M4.2 visible probe remains a formal failure and its failed completeness
file remains immutable. The M4.3 Plan requires a read-only counterfactual
M4.2 replay, retained M4/M4.1 replay and hash checks, focused and broad
functional tests, build, installed dry-run, launch instantiation, checkpoint,
and implementation commit before any new Gazebo process.

## Current milestone

**Phase 08.7 M4.3 — PLAN AUTHORIZED; no M4.3 implementation or Gazebo
execution has started.**

### Next criterion

Validate, checkpoint, and commit the M4.3 amendment. Then implement only the
declared evidence-prefix correction, regression coverage, and fresh frozen
scenario identities; complete every no-Gazebo gate before dispatch.

## Phase 08.7 M4.3 implementation and no-Gazebo qualification

The M4.3 Plan amendment was committed at `6f7a5fa`
(`phase 08.7: plan M4.3 event attribution correction`). Implementation stayed
inside the declared boundary:

- `algorithm_event_producer_stream()` now maps only
  `EVENT_CONFIGURATION + detail.startswith("post-recovery ")` to the existing
  `supervisor` producer;
- the current signature matrix covers both observed M4.2 details;
- a deliberate cross-event supervisor timestamp regression proves the new
  signature participates in the existing supervisor stream;
- unknown configuration signatures and malformed watchdog ownership remain
  unidentified;
- fresh M4.3 visible and conditional suite identities copy every M4.2
  behavioral value.

No ROS message, publisher, node, topic, launch control, navigation behavior,
safety classification, cost sign/unit, schema field, acceptance threshold, or
physical-hardware path changed.

### Focused and broad source tests

The first focused command sourced `/opt/ros/humble` but not the workspace
install and stopped during collection because generated
`ros_esc_interfaces` was unavailable. It exercised no test and changed no
evidence. The corrected bounded command sourced both ROS and
`ros2_ws/install/setup.bash`, with source `ros_esc` first on `PYTHONPATH`, and
passed:

```text
ros2_ws/src/ros_esc/test/test_experiment_recording.py
ros2_ws/src/ros_esc/test/test_scenario_schema.py
ros2_ws/src/ros_esc/test/test_scenario_runner.py

223 passed, 1 skipped in 50.39 s
/tmp/phase08_7_m4_3_focused.xml
SHA-256 5a191e33367f196c2d8f49015901e6c1f55b0616db6575e550e883b392b70df1
```

The skip is the existing explicit Gazebo opt-in. The final broad functional
command was:

```text
timeout --signal=INT --kill-after=20s 300s \
  python3 -m pytest -q ros2_ws/src/ros_esc/test \
  --ignore=ros2_ws/src/ros_esc/test/test_flake8.py \
  --ignore=ros2_ws/src/ros_esc/test/test_pep257.py \
  -k 'not v4_population_adoption_is_exact_and_unused' \
  --junitxml=/tmp/phase08_7_m4_3_broad_functional.xml

613 passed, 3 skipped, 1 deselected in 113.89 s
SHA-256 811da2678e342deb71fd7dfa118be7d6aeb7002270e8497ad48d3d37d8961176
```

The three skips remain the generated copyright-header check and two explicit
Gazebo opt-ins. The deselected test is the sealed stale V4 population
assertion that treats every later fixed scenario as drift. Fatal
`E9/F63/F7/F82` checking, Python compilation, `git diff --check`, and:

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/
  validate_phase_context.sh 08 implement
```

all pass.

### Immutable read-only replay

The first replay wrapper stopped before opening a bag because its hash
manifest used nonexistent `scenario_result.json` rather than the retained
`scenario_result.yaml`. The corrected wrapper ran all three validators with
`write_report=False` and opened every sqlite bag `READ_ONLY`:

```text
M4:   passed false; 48 checks; original typed timestamp regression retained
M4.1: passed true;  48 checks; no failures
M4.2: passed true;  48 checks; no failures
```

This is counterfactual evidence for the correction only. M4.2 remains the
stored formal failure. Hashes before and after replay were identical:

```text
4acc311734e63896faf33c07439b7c1c81e9ebdcd6902b0514bf9c9ce0846e88  M4 completeness
afd4cbd707004e2a8b6965ea08f1db1329a08ff816ff0965b821d95f28a0fcc0  M4.1 completeness
4abaecc2dacf8fb544de01ba198e4e26792566c5cc44c059e6d99e4802d746d0  M4.2 completeness
b7f4a57a973f79ff9e2b07c5ad7c8968f341b7ee0d3fa6b3b2c9029fd07984fe  M4.2 result
7dd10ccd0231cd9e17eb8b9e1a76d8dbba5779d19d7c8fd2e1dc2f3d8093af66  M4.2 bag
414a9537a888adc30fc0b586b8c5832cb1039c6271913639c0264d0d7eb537cc  M4.2 analysis completeness
9d296d50c203804f3938bcb22379b6b6bc6c5636d9c5880bded51ee4a75043ad  M4.2 suite summary
```

### Fresh frozen inputs

The M4.3 visible scenario SHA-256 and deterministic key are:

```text
cacbdafbc9aa289f178e684503519283bdf4b5496cbdd2dfb8c61ff69ebf1658
a5ea7f8b3d12aa01be4018ba059d12f9366f722687f95403e1c47c6929fc4655
```

The M4.3 conditional suite SHA-256 is:

```text
37c1f7f2d81132be46adee576a1b603093fd03dd5488c5465d53d8876b9d50cc
```

Its fixed execution-order keys are:

```text
cf5bea10bd2d904bea008d4d9f6d22cc4a026862fdbda2e45fe7b63358cd5fab
d58512ad9cc4488243861b89bd7120a9bce309473fa18ac0dc71966d69830540
896201a5ad6b907860270b109aaac4ff4666878c08e502d3e96c8b91fa08940a
a90044d4ed94d4ebd03ac6fdc78369d06f19235d1aadc86706fc6718e9e68cf0
71f003ea659ab8f0a3ae8193fa24b6a0e43b9cd65b67d5c23d3d7108e53116d2
9fd3b4a5d3c8aefaca899bd73f6a273c8d1d88c61304794ed9631aeefc54a0c4
0542aa9a360e470ab9db2533ee350276b772312996a43503329f6493f78d047b
acac96fa8659c2e8efc042292d56b3a9e2cb099bcb18fcf840ee44419c618206
```

All three repeats bind the fresh central validation key
`896201a5ad6b907860270b109aaac4ff4666878c08e502d3e96c8b91fa08940a`.
The schema regression strips only fresh identity fields and proves every
resolved behavior field plus all execution controls equal M4.2.

Historical source hashes remain:

```text
e6ec6120df271afab3ae71192b601c4bcf866105a8cdaa13a10dcd94b7632973  M4.2 visible
8d56eb4872aafc485103f8ddd2e03a7105101fd97b8b26b532e880a9d7c84219  M4.2 suite
3be130581b88c986fd845aef0c33c9db94ceb02ecfe2a6361926b0317ef8e655  V6 sweep
3b9badc92cf63739f65662158999e3c2aab71761f790e3f360be9a52e6f38688  V6 repeats
88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf  shifted world
8ecc1a231efec24401d74fef3cd5139d48c6029f88e71d044cefdf2fd14c5bef  historical world
```

### Isolated build and installed qualification

The bounded isolated build passed under
`/tmp/phase08_7_m4_3_qual`:

```text
ros_esc_interfaces
ros_esc
turtlebot3_rotating_sensor

Summary: 3 packages finished in 12.2 s
```

Installed dry-runs passed:

```text
/tmp/phase08_7_m4_3_visible_installed_dry_run.yaml
  1 supported case; GUI true
  SHA-256 f13e0f8a193c2254e9dc5759aaa6f1cecf468a8a5f5846387af02911031e633d

/tmp/phase08_7_m4_3_suite_installed_dry_run.yaml
  8 supported cases; GUI false for every case
  SHA-256 9dd89302b97cea7190e517cffcd9aa72fa91e41cb6c1ffa1a7489a3532058786
```

Installed nonexecuting `ros2 launch -p` expansion passed with `92` supplied
arguments and a `270`-line description:

```text
/tmp/phase08_7_m4_3_installed_launch_description.txt
SHA-256 e297909cb1253fa6a7ca8cc2a3207e5ad8d6453a47548516c55596a3151e5578
```

The corrected validator and both fresh scenarios are byte-identical between
source and isolated install. Their source hashes are:

```text
b709c0b093f49ad5f229cb070fe10512cd5590d4abf8c11f3a7ed39b5eec6597  validator
cacbdafbc9aa289f178e684503519283bdf4b5496cbdd2dfb8c61ff69ebf1658  visible scenario
37c1f7f2d81132be46adee576a1b603093fd03dd5488c5465d53d8876b9d50cc  suite scenario
```

The central launch still contains exactly one `/cmd_vel` argument in the
custom controller path; the supervisor retains only
`/gesc_gaussian/supervisor_command`.

The fresh M4.3 evidence roots are absent. `gzserver`, `gzclient`,
`run_scenario`, and `record_run` process names are inactive, and ROS domain
`161` has no discovered nodes with the CLI daemon disabled. No Gazebo or
physical process started during implementation or qualification.

## Current milestone

**Phase 08.7 M4.3 — exact implementation and every required no-Gazebo
qualification gate PASS; material-boundary checkpoint and commit pending.**

### Next criterion

Refresh the Phase 08 checkpoint, inspect and commit the exact qualified
implementation plus fixed inputs, then reconfirm the clean dispatch boundary.
Only then may the one fixed visible M4.3 two-light probe run on ROS domain
`161`. The eight-case headless suite remains conditional on a complete visible
pass; the three-light probe remains unauthorized.

## Phase 08.7 M4.3 committed dispatch boundary

The exact qualified evidence correction, regression tests, fresh scenario
inputs, status, and precommit checkpoint were committed at:

```text
85fdd6f6bfc884c16e1b79d60fd813a1b9c989a1
phase 08.7: qualify M4.3 event attribution
```

The post-commit worktree is clean and the implementation context validator
passes. Source and isolated-install bytes remain identical:

```text
b709c0b093f49ad5f229cb070fe10512cd5590d4abf8c11f3a7ed39b5eec6597  validator
cacbdafbc9aa289f178e684503519283bdf4b5496cbdd2dfb8c61ff69ebf1658  visible scenario
37c1f7f2d81132be46adee576a1b603093fd03dd5488c5465d53d8876b9d50cc  suite scenario
```

The visible and suite roots remain absent. `gzserver`, `gzclient`,
`run_scenario`, and `record_run` are inactive. ROS domain `161` has no
discovered nodes with the CLI daemon disabled. `DISPLAY=:0` passes
`xdpyinfo`, and the evidence filesystem has `315 GiB` free.

Exactly one fresh visible attempt is predeclared:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m4_3_qual/install/setup.bash
export ROS_DOMAIN_ID=161
export ROS_LOG_DIR=/tmp/phase08_7_m4_3_probe_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m4_3_probe_mpl
export TURTLEBOT3_MODEL=burger
export DISPLAY=:0
timeout --signal=INT --kill-after=90s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m4_3_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m4_3_visible_probe.yaml \
  --operator Codex \
  --case-id v7_m4_3_probe_r1p5_a45_h25_18308 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3_probe \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3_probe/\
phase08_v7_m4_3_visible_probe_summary.yaml \
  --gui
```

The attempt will be retained without retry or in-run value changes. The
fixed eight-case suite remains passing-gated; the optional three-light probe
remains unauthorized.

## Current milestone

**Phase 08.7 M4.3 — qualified implementation committed; one fixed visible
two-light probe predeclared.**

### Next criterion

Refresh the Phase 08 checkpoint against commit `85fdd6f`, commit this dispatch
record, reconfirm the clean process/evidence boundary, and execute only the
bounded visible probe.

## Phase 08.7 M4.3 retained two-light-suite result

The passing visible gate opened exactly one serial execution of the committed
eight-case M4.3 suite on ROS domain `162`. It ran from
`2026-07-30T09:00:39.750638Z` through
`2026-07-30T09:41:46.322069Z`. The outer timeout did not fire; all eight
fixed cases executed exactly once in order, and the suite returned `1`
because two behavioral contracts failed.

The immutable result is:

```text
fixed visible probe:               PASS
spatial suite cases:               3/5 PASS
repeat cases:                      3/3 PASS
fixed visible + central variants:  5/5 PASS
all suite cases:                   6/8 PASS
recording completeness:            8/8 PASS, each 48/48
cleanup:                           8/8 PASS
collision expectation:             8/8 PASS
Stage A local recovery:            7/8 PASS
Stage B global proximity:          6/8 PASS
combined two-light readiness:      FAIL
```

All eight retained sqlite bags returned `ok` from read-only
`PRAGMA quick_check`. Standard analysis ran exactly once per bag; all eight
invocations returned `0`, report `complete` with no analysis failure, and
retained eight plots plus eleven tables each. The summary SHA-256 is:

```text
40babf08ce27f22d23e5ccfbbf3913e1627e9d092ad7be602fafbe234377e367
```

The complete per-case table, paths, metrics, immutable hashes, and commands
are retained in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_3_two_light_suite_report.md
```

### Failure 1 — fixed-horizon corner recenter

`v7_m4_3_r1p0_a45_h25_18309` converged near the declared corner local,
created the exact one fill, and escaped it, then followed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> FAILSAFE
```

At simulation time `253.1 s`, it emitted
`RECENTER->FAILSAFE: no safe recenter direction candidate`. The terminal
robot center `(0.4455714550, 0.3016966342)` remained inside the physical
room. Its `0.6086747487 m` conservative fill-avoidance circle and the
southwest inset made every full `0.50 m` lookahead candidate invalid, even
though a shorter outward segment remained physically available. This is a
recoverable local-planner resolution defect, not a collision or
physical-room violation.

### Failure 2 — fill-clearance direction reversed global progress

`v7_m4_3_r1p5_a22p5_h25_18309` passed Stage A and exact cardinality, then
started post-recovery SEARCH from `(1.7300872541, 1.7399268693)`. The current
selector chose `(-0.9615999066, 0.2744551323)` because it maximized hard-safe
clearance and fill-distance progress. That direction pointed west; its dot
product with the evidence-only anchor-to-global direction was approximately
`-0.49`.

The supervisor translation and robust affine term shared that direction.
Liveness refreshed it once, requested one recoverable recenter, started a
second epoch, and finally released ordinary search. The fixed `120.0 s`
Stage B budget expired with `3,533` valid and `0` invalid post-Stage-A
samples. The stop pose was `(1.2672143994, 1.1016695200)`, still
`3.2767851058 m` from the global.

The Gaussian fill already preserves the old basin. Maximizing distance from
that fill is not a global navigation objective and can reverse source-led
progress. Extending the timeout or relaxing the `1.20 m` stop would not
correct this trajectory.

### Closed boundary and next criterion

M4.3 is **CLOSED / FAIL at 6/8 / NOT SIMULATION-READY**. No M4.3 case will
be retried, changed, relabelled, or counted in a later gate. The optional
three-light probe remains prohibited because the complete two-light gate did
not pass. `gzserver`, `gzclient`, `run_scenario`, `record_run`, and matching
launch processes are inactive after suite analysis.

Any further code or Gazebo execution requires a fresh version. The smallest
evidence-backed behavior correction is:

1. adaptive finite recenter lookahead near a fill/wall pinch, while retaining
   physical-room and collision hard stops;
2. a source-led post-recovery SEARCH handoff before affine or supervisor
   translation, so a safe fill-clearance direction cannot immediately
   override ordinary GESC;
3. liveness intervention only after measured source-led motion fails, with no
   global coordinates supplied to the algorithm;
4. unchanged `1.20 m` primary global-proximity stop and immutable M4.3,
   V6, and historical artifacts.

That correction must be planned, tested, checkpointed, and committed without
Gazebo before any fresh fixed probe.

## Current milestone

**Phase 08.7 M4.3 — CLOSED / TWO-LIGHT QUALIFICATION FAIL AT 6/8 /
COMPLETE EVIDENCE / NOT SIMULATION-READY.**

### Next criterion

Checkpoint and commit the immutable M4.3 suite result. Any further behavior
change must use a fresh planned version, preserve all M4.3/V6/historical
inputs and evidence, qualify without Gazebo, and commit its exact dispatch
boundary before a new fixed simulation. The optional three-light probe,
Phase 09, and physical hardware remain unauthorized.

## Phase 08.7 M4.4 authorization and Plan boundary

The immutable M4.3 suite result was committed at `e28fc3c`
(`phase 08.7: retain M4.3 two-light suite result`). The active user goal is
to fix the two-light behavior fully. M4.4 is the fresh bounded continuation
for the two retained M4.3 defects; it does not reopen or relabel M4.3.

The append-only M4.4 Plan amendment declares two default-off robust controls:

```text
adaptive_recenter_lookahead_enabled
post_recovery_source_led_handoff_enabled
```

Adaptive recenter preserves the configured `0.50 m` candidate as the first
choice, then tries `0.25`, `0.125`, `0.0625`, and `0.05 m` only if the longer
horizons are empty. The `0.05 m` minimum is the complete
`0.10 m/s * 0.50 s` supervisor-command persistence distance. A physically
valid empty set holds zero translation under the existing bounded
recenter-retry budget rather than latching immediately.

The source-led handoff gives raw-plus-Gaussian GESC sole motion authority for
the first complete `12.0 s` post-recovery window:

```text
affine weight:           0.0
supervisor translation:  0.0
safe direction:          unavailable
```

Net displacement greater than `0.20 m` releases the extra guidance and keeps
ordinary SEARCH. Net displacement at most `0.20 m` arms the existing
hard-safe fallback and resets its liveness window. The algorithm receives no
global coordinate, source role, or simulation ground truth.

Fresh fixed identities are:

```text
visible suite/version:  phase08_v7_m4_4_visible_probe
                        phase08-v7-m4-4-probe
visible case/seed:      v7_m4_4_probe_r1p5_a45_h25_18408 / 18408
visible evidence root:  /home/mattb/Experiments/GESC-Gaussian/runs/
                        phase08_v7_m4_4_probe
headless suite/version: phase08_v7_m4_4_two_light_suite
                        phase08-v7-m4-4
headless seeds:         18409, 18410, 18411, 18412
headless evidence root: /home/mattb/Experiments/GESC-Gaussian/runs/
                        phase08_v7_m4_4
```

Every M4.3 algorithm value and acceptance threshold remains fixed, including
the primary `1.20 m` global-proximity stop, `1.00 m` non-gating diagnostic,
`120.0 s` post-Stage-A budget, exact one-fill cardinality, collision false,
physical-room hard boundary, final zero, and cleanup.

No M4.4 source, scenario, or Gazebo action has started. The amendment must
pass context validation, checkpointing, and a bounded Plan commit before
implementation.

## Current milestone

**Phase 08.7 M4.4 — USER-AUTHORIZED PLAN AMENDMENT SAVED; IMPLEMENTATION
HAS NOT STARTED.**

### Next criterion

Validate, checkpoint, and commit the M4.4 amendment. Then implement only the
default-off adaptive-recenter and source-led-handoff controls, regression
coverage, and fresh fixed identities. Complete every no-Gazebo gate and
commit the exact dispatch boundary before any fresh simulation. The
three-light probe, Phase 09, and physical hardware remain unauthorized.

## Phase 08.7 M4.4 implementation and no-Gazebo qualification

The frozen M4.4 amendment was committed at `ff127a1`
(`phase 08.7: plan M4.4 source-led recovery`). Implementation stayed inside
its declared ownership and compatibility boundary:

- `RecenterRoutePlanner` preserves the configured `0.50 m` candidate first
  and, only when enabled and empty, evaluates `0.25`, `0.125`, `0.0625`, and
  the full `0.05 m` supervisor-command persistence distance;
- the retained M4.3 route-side sequence and exact corner geometry now select
  a hard-safe `0.25 m` candidate, while default-off selection remains exactly
  the prior single-horizon behavior;
- a physically valid, finite empty adaptive route holds zero translation,
  retains bounded angular replanning, reports one supervisor-owned typed event
  per continuous episode, and remains under the existing finite timeout/retry
  budget; physical-room violations, nonfinite geometry, hard faults, and
  exhausted recovery remain terminal;
- the accepted `RECENTER -> SEARCH` boundary starts one source-led window with
  raw/Gaussian weights `1.0/1.0`, affine weight `0.0`, zero supervisor
  translation, and no safe direction;
- greater-than-`0.20 m` net displacement in the first complete `12.0 s`
  window releases ordinary SEARCH; at-most-`0.20 m` arms the existing
  hard-safe fallback exactly once, and that fallback's one recenter cannot
  restart source-led mode;
- both controls default `false`, are schema-v7-only robust controls, and bind
  through the existing central launch and supervisor. No node, topic,
  controller, `/cmd_vel` publisher, recorder, validator, message, source role,
  global coordinate, cost sign/unit, or simulation/physical fork changed.

The temporarily empty-route event uses the existing closed supervisor
producer family without changing the validator:

```text
measured escape: recenter route temporarily unavailable; bounded recovery continues
```

The three source-led details retain the existing `post-recovery ` producer
prefix. Focused recording classification covers all four new details and
keeps unknown configuration signatures unidentified.

### Source qualification

The final focused command used the retained M4.3 interface overlay with source
`ros_esc` first on `PYTHONPATH`:

```text
timeout --signal=INT --kill-after=20s 300s \
  python3 -m pytest -q \
  test_escape_recenter.py test_state_machine.py \
  test_supervisor_integration.py test_scenario_schema.py \
  test_scenario_runner.py test_observability_contract.py \
  test_experiment_recording.py \
  --junitxml=/tmp/phase08_7_m4_4_focused.xml

355 passed, 1 skipped in 54.68 s
SHA-256 22687adf5d60dfada12074992394cddccd2f86590f30f4a7ba44167631d403ab
```

The skip is the existing explicit Gazebo opt-in. Within that set, all nine
M4.4 supervisor integration cases and all 67 recording tests pass. The exact
M4.3 corner regression includes its preceding route-side sequence,
full-horizon failure, adaptive `0.25 m` selection, and complete command-sweep
safety.

The final broad ROS-independent functional command was:

```text
timeout --signal=INT --kill-after=20s 300s \
  python3 -m pytest -q ros2_ws/src/ros_esc/test \
  --ignore=ros2_ws/src/ros_esc/test/test_flake8.py \
  --ignore=ros2_ws/src/ros_esc/test/test_pep257.py \
  -k 'not v4_population_adoption_is_exact_and_unused' \
  --junitxml=/tmp/phase08_7_m4_4_broad_functional.xml

634 passed, 3 skipped, 1 deselected in 117.43 s
SHA-256 071af1256793f43d0af4651a51b78a2ee5ab869049226ff727899dd8d9e52f29
```

The skips remain the generated copyright-header check and two explicit
Gazebo opt-ins. The one deselection remains the documented stale V4
population assertion that treats every later fixed scenario as drift.
An exploratory repository-root `ament_flake8`/`ament_pep257` invocation
scanned historical repository content and reproduced the known large baseline
of approximately 16,000 flake8 and 2,551 pep257 findings. It made no source
change and is not the Plan's fatal gate. The bounded final
`E9,F63,F7,F82` check on every changed Python source/test passes, as do
`python3 -m py_compile`, `git diff --check`, and:

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/
  validate_phase_context.sh 08 implement
```

### Fresh fixed inputs

The M4.4 visible input SHA-256 and deterministic case key are:

```text
1559ee2ab0a7d2fa26834bc0bfd226aaa2b8d6d7dad62dcdac85ca2e83293eb4
22ce182a7f02becf7d5f53e8193e99fdb11266ebd0fc51018ca27b8ab23aafff
```

The conditional suite SHA-256 is:

```text
78be277362ac060c7cb77c5d2215836cb914a95bd81a5ed9221f0db4bc62a188
```

Its fixed execution-order keys are:

```text
699ff166fc90149cf52e528f82f064e3b4c2fd9fed338969a20966c6d46c4b86
eb3ff82af459346e884bfc2a8a304dfd8f0d242475efe1b36a7a83e13e527566
cacad8b96a05e2bcda31072284edeeb4dea23f62a7bf016f46527a86d8e19b8f
8ee88d3ef6a9a74edcf5d41ef428b4d81414c82ea15379d3a577d884cdc437eb
8697df57b64a97f070c3f0657684bec265cadf38c0bae856ac3ee2e79e1daa03
6f979d54f1cc796740003a1613d2e1f07e783590ad829e205e9a0d2efc304e4f
443625cf507b870b420c383126b414f0fd5dc12490e7b6ec83165864017fd469
6f3ae4792673cf2176e62d54319efc152902b716444042a82be11d7bfbe21260
```

All repeats bind the fresh central key
`cacad8b96a05e2bcda31072284edeeb4dea23f62a7bf016f46527a86d8e19b8f`.
Schema regression normalizes only fresh identities/descriptions and the two
new enabled controls; all M4.3 behavior, execution controls, acceptance
values, known topology, exact one-fill limit, and source geometry match.

Historical source and retained-summary hashes remain:

```text
40babf08ce27f22d23e5ccfbbf3913e1627e9d092ad7be602fafbe234377e367  M4.3 suite summary
cacbdafbc9aa289f178e684503519283bdf4b5496cbdd2dfb8c61ff69ebf1658  M4.3 visible
37c1f7f2d81132be46adee576a1b603093fd03dd5488c5465d53d8876b9d50cc  M4.3 suite
3be130581b88c986fd845aef0c33c9db94ceb02ecfe2a6361926b0317ef8e655  V6 sweep
3b9badc92cf63739f65662158999e3c2aab71761f790e3f360be9a52e6f38688  V6 repeats
88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf  shifted world
8ecc1a231efec24401d74fef3cd5139d48c6029f88e71d044cefdf2fd14c5bef  historical world
```

No retained validator or bag was rewritten or rerun.

### Isolated installed qualification

The fresh isolated build at `/tmp/phase08_7_m4_4_qual` passed:

```text
ros_esc_interfaces
ros_esc
turtlebot3_rotating_sensor

Summary: 3 packages finished in 13.4 s
```

Installed-executable dry-runs passed:

```text
/tmp/phase08_7_m4_4_visible_installed_dry_run.yaml
  1 supported case; GUI true
  SHA-256 f0ade3b285cced325d0ab9a047e4d25d88e2b8914285f9acc11465db6d831d6f

/tmp/phase08_7_m4_4_suite_installed_dry_run.yaml
  8 supported cases; GUI false for every case
  SHA-256 15d544d10de88d0b456fc2e8e58abcf8d3443378cd2f0bf7961f72d063ca218a
```

Every installed run resolves both M4.4 controls `true`; the fresh scenarios
otherwise retain the fixed M4.3 launch and acceptance values. Nonexecuting
installed `ros2 launch -p` expansion accepted all `94` supplied arguments and
retained a `271`-line description:

```text
/tmp/phase08_7_m4_4_installed_launch_description.txt
SHA-256 5abaa3b598d12dc3fcd41335d078252b36f96d09e7fa519d501077a6820fb860
```

The expansion binds both new parameters only into the existing supervisor.
The central launch retains one `/cmd_vel` argument in the custom-controller
path; the supervisor retains only `/gesc_gaussian/supervisor_command`.
Installed/build-resolved production Python, both new scenarios, and the
central launch are byte-identical to source. Source hashes are:

```text
c4842466ed4064d2708db8cfe10c674ba1b35a978753c8b88e1eacaf147c3475  scenario schema
58bdc1bf28de841fb62efcb879fd2740464f71558a75faa62ce95108d0b03969  recenter geometry
8c5e00fba21eff56506b8402d2cb5d18b4f4898165d0f1d75d450e733b7d90ef  supervisor
61a3fb43eccd74216437ca0f7ac3b5fb634bf6373258ad4daff65de8dea59c9c  central launch
```

The fresh visible and suite evidence roots remain absent. `gzserver`,
`gzclient`, `run_scenario`, `record_run`, and matching launch processes are
inactive. ROS domain `163` has no discovered nodes with the CLI daemon
disabled. No Gazebo or physical process started during implementation or
qualification.

## Current milestone

**Phase 08.7 M4.4 — exact implementation and every required no-Gazebo
qualification gate PASS; material-boundary checkpoint and commit pending.**

### Next criterion

Refresh the Phase 08 checkpoint, inspect and commit the exact qualified
implementation plus fixed inputs, then reconfirm the clean dispatch boundary.
Only then may the one fixed visible M4.4 probe run. The eight-case suite
remains conditional on a complete visible pass; the optional three-light
probe, Phase 09, and physical hardware remain unauthorized.

## Phase 08.7 M4.4 committed dispatch boundary

The exact qualified behavior correction, regression tests, fresh scenario
inputs, status, and precommit checkpoint were committed at:

```text
516fccde11c5961226558b0aa26d7b13f672331d
phase 08.7: qualify M4.4 source-led recovery
```

The post-commit worktree is clean and the implementation-context validator
passes. The source scenarios and installed resources remain byte-identical at:

```text
1559ee2ab0a7d2fa26834bc0bfd226aaa2b8d6d7dad62dcdac85ca2e83293eb4  visible scenario
78be277362ac060c7cb77c5d2215836cb914a95bd81a5ed9221f0db4bc62a188  suite scenario
```

The fresh visible and suite roots remain absent. `gzserver`, `gzclient`,
`run_scenario`, `record_run`, and matching launch processes are inactive.
ROS domain `163` has no discovered nodes with the CLI daemon disabled.
`DISPLAY=:0` passes `xdpyinfo`, and the evidence filesystem has `313 GiB`
available.

Exactly one fresh visible attempt is predeclared:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m4_4_qual/install/setup.bash
export ROS_DOMAIN_ID=163
export ROS_LOG_DIR=/tmp/phase08_7_m4_4_probe_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m4_4_probe_mpl
export TURTLEBOT3_MODEL=burger
export DISPLAY=:0
timeout --signal=INT --kill-after=90s 660s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m4_4_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m4_4_visible_probe.yaml \
  --operator Codex \
  --case-id v7_m4_4_probe_r1p5_a45_h25_18408 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4_probe \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4_probe/\
phase08_v7_m4_4_visible_probe_summary.yaml \
  --gui
```

The attempt will be retained without retry or in-run changes. The fixed
eight-case suite remains passing-gated; the optional three-light probe,
Phase 09, and physical hardware remain unauthorized.

## Current milestone

**Phase 08.7 M4.4 — qualified implementation committed; one fixed visible
two-light probe predeclared.**

### Next criterion

Refresh the Phase 08 checkpoint against `516fccd`, commit this exact dispatch
record, reconfirm the clean process/evidence boundary, and execute only the
bounded visible probe.

## Phase 08.7 M4.4 retained visible-probe pass

The one committed visible attempt ran on ROS domain `163` from
`2026-07-30T10:45:55.781756Z` through
`2026-07-30T10:50:56.989440Z`. The outer timeout did not fire, the record
process returned `0`, and the runner returned `0`.

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4_probe/
  2026-07-30/
  20260730T104556725279Z_simulation_phase08_v7_m4_4_visible_probe-
  v7_m4_4_probe_r1p5_a45_h25_18408-robust_gaussian_v_86533a18
```

The fixed visible gate passes every formal and behavioral predicate:

```text
recording completeness:           PASS, 48/48
cleanup:                          PASS
collision expectation:            PASS, no collision
forbidden states/events:           PASS, none
Stage A local recovery:            PASS, 1 episode
unique fill cardinality:           PASS, exactly 1
Stage B global proximity:          PASS
combined result:                   PASS
post-Stage-A time budget:          PASS, not expired
```

The accepted path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_ASSIST
-> RECENTER
-> SEARCH
```

The single accepted cluster was associated with the declared local:

```text
convergence point:              (1.3636727905, 1.2805420264) m
fill center:                    (1.2519110241, 1.3952389305) m
convergence-to-local:           0.3743857330 m
convergence-to-global:          3.0805661238 m
fill-to-convergence:            0.1601439110 m
```

At the post-recovery boundary, the M4.4 source-led policy executed exactly as
declared. It started at simulation time `210.2 s` with no affine/supervisor
direction. At the first complete window it had traveled `0.767347 m` but
translated only `0.145095 m`, so it reported one stalled handoff and armed
the existing fallback. The fallback released at `242.2 s` after
`1.106318 m` outward progress. No recenter-route-unavailable event or
`FAILSAFE` occurred in this central case.

Stage A completed at `210.315 s`. The runner then stopped gracefully on the
first valid, recorded, noninterpolated sample inside the primary boundary:

```text
sample simulation time:         246.491 s
post-Stage-A elapsed:             36.176 s
position:                       (3.0227022094, 2.4004886344) m
distance to global:              1.1986402396 m
primary radius:                  1.20 m
```

The `1.00 m` closer diagnostic did not pass and remains non-gating. The
controller's source-score `GOAL_HOLD` classification also did not occur and
is not the Stage B contract; recorded physical proximity is the declared
operator-equivalent stop.

Read-only SQLite `PRAGMA quick_check` returned `ok`. The standard analyzer
ran exactly once into the run-local `analysis/phase07` directory and returned
`analysis_status: complete` with no failures, eight plots, and eleven tables.
Retained hashes are:

```text
c85afd4cc024bec5742e3a178c801ac857399ca4e4439807a34e5f1061635879  visible summary
217c498441a09b2a1247aab6da94236342cf8d726d03608924ffbb63f32a5208  completeness
28066a9f28561c59676396946a36c3d87108ce1aa907fa67cdd0d0bf647de967  scenario result
8c37934e356aceb29a76130904ec7f08f4a2d75341fb9543ff2be50683cfe132  bag
03ba002c25245eb9de7050fcceea6ec57a6a921bd292acd883a78904e355eabf  analysis completeness
ecc46ca10ed6d0349cf9b3cef2d2e400db08af1784af79fdcf907924bbec430b  analysis metrics
```

Cleanup reconfirmed no Gazebo, runner, recorder, analyzer, or matching launch
process, and ROS domain `163` is empty with the CLI daemon disabled. No retry
or in-run change occurred.

The complete visible pass opens the Plan's one conditional serial headless
suite. Its exact predeclared command is:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m4_4_qual/install/setup.bash
export ROS_DOMAIN_ID=164
export ROS_LOG_DIR=/tmp/phase08_7_m4_4_suite_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m4_4_suite_mpl
export TURTLEBOT3_MODEL=burger
timeout --signal=INT --kill-after=90s 5400s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m4_4_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m4_4_two_light_suite.yaml \
  --operator Codex \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4 \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4/\
phase08_v7_m4_4_two_light_suite_summary.yaml
```

All eight committed cases will run exactly once in fixed order. Any formal,
behavioral, or cleanup failure is retained and is not retried; a cleanup
failure stops later dispatch. The optional three-light probe, Phase 09, and
physical hardware remain unauthorized.

## Current milestone

**Phase 08.7 M4.4 — fixed visible probe PASS with complete evidence; exact
conditional eight-case two-light suite predeclared.**

### Next criterion

Checkpoint and commit the retained visible result plus exact suite dispatch
record. Then reconfirm the clean domain/evidence/process boundary and execute
only the fixed serial headless suite.

## Phase 08.7 M4.4 retained two-light suite result

The committed eight-case suite ran exactly once in fixed order on ROS domain
`164` from `2026-07-30T10:55:19.930174Z` through
`2026-07-30T11:38:21.719708Z`. The outer `5400 s` timeout did not fire.
The suite returned `1` because the all-case readiness gate failed.

Retained summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4/
  phase08_v7_m4_4_two_light_suite_summary.yaml

SHA-256
d5ab58ad26c8329c20e08b4954697daca6a5f01bd4a821856202fc16761d2897
```

The immutable result is:

```text
fixed visible probe:               1/1 PASS
spatial suite cases:               3/5 PASS
repeat suite cases:                2/3 PASS
all suite cases:                   5/8 PASS
visible plus suite:                6/9 PASS
Stage A local recovery:            7/8 PASS, one unavailable
exact unique fill cardinality:     7/8 PASS, one unavailable
Stage B global proximity:          5/8 PASS, two fail, one unavailable
complete recording:                7/8 PASS, each 48/48
cleanup:                           8/8 PASS
collision and forbidden evidence:  7/7 behavioral attempts PASS
combined two-light readiness:      FAIL
```

Per-case outcomes:

- `v7_m4_4_r1p0_a45_h25_18409`: **PASS**. The former M4.3 corner
  recenter failure now completes Stage A and reaches Stage B at
  `1.1981386677 m`, proving the adaptive-recenter correction.
- `v7_m4_4_r1p5_a22p5_h25_18409`: **infrastructure invalid**. The
  controller manager loaded `velocity_controller`, its first load response
  was lost, and the Humble spawner's non-idempotent retry failed on
  “already loaded.” Cleanup and SQLite integrity passed; Stage A/B are
  unavailable.
- `v7_m4_4_r1p5_a45_h25_18409`: **PASS**, Stage B
  `1.1990207307 m`.
- `v7_m4_4_r1p5_a67p5_h25_18409`: **PASS**, Stage B
  `1.1997246446 m`.
- `v7_m4_4_r2p0_a45_h25_18409`: **FAIL**, with complete `48/48`
  evidence. Stage A and exact one-fill cardinality pass, but the full
  `120.020 s` Stage B budget expires at `3.3300033703 m`.
- `v7_m4_4_repeat_r1p5_a45_h25_18410`: **FAIL**, with complete
  `48/48` evidence. Stage A occurs at `452.022 s`, leaving only
  `29.104 s` before the fixed `480 s` recording ends; the declared
  `120 s` Stage B opportunity was not reserved.
- `v7_m4_4_repeat_r1p5_a45_h25_18411`: **PASS**, Stage B
  `1.1969963924 m`.
- `v7_m4_4_repeat_r1p5_a45_h25_18412`: **PASS**, Stage B
  `1.1986026674 m`.

No behavioral case entered `FAILSAFE`, collided, emitted a forbidden
in-readiness state/event, or failed cleanup/final-zero. The wall-margin and
collision gates are therefore not the cause of the remaining behavioral
failure.

The radius-2.0 trace isolates the supervisor defect. The source-led window
moved `0.163114 m` in a northeast direction that reduced global distance
from `3.043 m` to `2.886 m`. The fallback then selected
`(-0.894328, -0.447412)`, whose dot product with the observed source-led
direction is approximately `-1.000`. It was an exact reversal chosen because
fill-clearance remained the primary score. The fallback and its refresh
moved the robot away to `3.828 m`; recenter recovered some distance, but
the second fill-clearance epoch moved away again. Ordinary SEARCH resumed
too late to meet the budget.

All seven behavioral first source-led windows ended at net displacement at
most `0.20 m`; none directly completed the M4.4 source-led handoff.
Consequently, M4.4 withheld premature affine/supervisor authority but did
not use the observed source-led displacement to constrain the fallback.

The repeat-18410 result exposes a separate runner defect: schema v7 checks
only `post_stage_a_timeout_sec < run_timeout_sec`, not that a complete Stage
B budget remains after a late Stage A. The startup-invalid attempt exposes a
third independent defect in Humble controller-spawner load idempotency.

The standard analyzer ran exactly once per attempt. Six behavioral analyses
are `complete`; the corner pass is `partial` only because one
`0.358869 s` AlgorithmState gap invalidated derived state durations, while
all critical inputs, `48/48` completeness, eight plots, and eleven tables
remain present. The infrastructure-invalid bag correctly produced no
analysis artifact. Read-only SQLite `PRAGMA quick_check` is `ok` for all
eight bags.

Full report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_4_two_light_suite_report.md
```

No optional three-light run occurred.

## Current milestone

**Phase 08.7 M4.4 — CLOSED / TWO-LIGHT QUALIFICATION FAIL /
5 PASS, 2 BEHAVIORAL FAIL, 1 INFRASTRUCTURE INVALID /
NOT SIMULATION-READY.**

### Next criterion

Checkpoint and commit the immutable M4.4 suite result. Any further correction
must use a fresh planned version. It must preserve M4.4, M4.3, V6, all
historical scenarios/evidence, the `1.20 m` primary Stage B boundary,
physical-room/collision hard gates, exact one-fill cardinality, sole
`/cmd_vel` ownership, and simulation/physical algorithm parity.

A fresh bounded correction should prevent an evidence-backed source-led
direction from being reversed by the radial fill-clearance fallback, reserve
the complete post-Stage-A budget, and recover idempotently from the observed
controller loaded/response-lost startup state. It must qualify without
Gazebo and be checkpointed/committed before any fresh simulation. The
optional three-light probe, Phase 09, and physical hardware remain
unauthorized.

## Phase 08.7 M4.5 authorization and Plan boundary

The immutable M4.4 suite result was committed at `55b017b`
(`phase 08.7: retain M4.4 two-light suite result`). The active
user-authorized goal remains a reliable two-light local escape followed by
global convergence. M4.5 is the fresh bounded correction for the three
independently retained M4.4 defects.

The append-only M4.5 Plan amendment declares:

```text
post_recovery_source_continuity_enabled = false
controller_spawner_load_recovery_enabled = false
```

Both controls default off. The source-continuity policy triggers only when a
finite source-led displacement of at least `0.05 m` would be reversed by a
radial fill-clearance direction with dot product at most `-0.90`. It then
uses the measured source-led forward half-plane to select a hard-safe
tangential/outward bypass and releases at the active avoidance radius plus
`0.10 m`. It receives no global coordinate or source role.

The staged runner adds an optional `stage_a_timeout_sec`. Fresh M4.5 cases
use a fixed `480 s` Stage A budget plus the unchanged `120 s` Stage B budget
inside a `600 s` recording. The live monitor stops a Stage A miss at its
explicit boundary, guaranteeing that any accepted Stage A retains the full
Stage B opportunity.

The transient controller-spawner recovery substitutes the existing two
concurrent spawner processes only when enabled. It processes the same
controllers in fixed order, issues no duplicate load after a missing
response, confirms loaded state through `/list_controllers`, and retains the
existing active-controller readiness gate.

Fresh fixed identities are:

```text
visible suite/version:  phase08_v7_m4_5_visible_probe
                        phase08-v7-m4-5-probe
visible case/seed:      v7_m4_5_probe_r2p0_a45_h25_18508 / 18508
visible evidence root:  /home/mattb/Experiments/GESC-Gaussian/runs/
                        phase08_v7_m4_5_probe
headless suite/version: phase08_v7_m4_5_two_light_suite
                        phase08-v7-m4-5
headless seeds:         18509, 18510, 18511, 18512
headless evidence root: /home/mattb/Experiments/GESC-Gaussian/runs/
                        phase08_v7_m4_5
```

The `1.20 m` Stage B stop, `1.00 m` diagnostic, wall margin, collision
contract, physical room, exact one-fill topology, cost sign/units, canonical
topics, sole `/cmd_vel` publisher, M4.4/M4.3/V6 scenarios, and every retained
historical result remain unchanged.

No M4.5 source, scenario, checkpoint, or Gazebo action has started. The Plan
amendment must pass context validation, checkpointing, and a bounded commit
before implementation.

## Current milestone

**Phase 08.7 M4.5 — USER-AUTHORIZED PLAN AMENDMENT SAVED; IMPLEMENTATION
HAS NOT STARTED.**

### Next criterion

Validate, checkpoint, and commit the M4.5 amendment. Then implement only the
default-off source-continuity, full staged-budget, and controller-load
recovery corrections plus fresh fixed inputs. Complete every no-Gazebo gate
and commit the exact dispatch boundary before any fresh simulation. The
optional three-light probe, Phase 09, and physical hardware remain
unauthorized.

## Phase 08.7 M4.5 implementation and no-Gazebo qualification

M4.5 was implemented from Plan commit `fc9b3b1` without starting Gazebo.
The bounded edit extends the existing supervisor, central launch, rotating
sensor control launch, scenario schema/runner, and focused tests. It adds no
persistent node, controller, `/cmd_vel` publisher, recorder, validator,
message, topic, cost source, algorithm profile, or simulation/physical fork.

The source-continuity correction is default-off. When enabled, it records the
source-led displacement and rejects the existing radial fallback only when the
finite displacement is at least `0.05 m` and the radial/source dot product is
at most `-0.90`. It selects from the unchanged hard-safe candidate geometry
in the measured source-forward half-plane, preserves the constraint across
the one existing recoverable recenter, and releases supervisor plus affine
assistance at the active fill avoidance radius plus `0.10 m`. The correction
receives no global coordinate, source role, or simulation ground truth.

The staged runner now accepts optional `stage_a_timeout_sec`. It anchors Stage
A at the first finite odometry sample, lets an observed Stage A completion win
at the exact boundary, reports a live Stage A timeout sample, and reserves the
independent Stage B window. Historical scenarios that omit the field retain
their prior runner behavior. Fresh M4.5 cases use exactly:

```text
Stage A:       480.0 s
Stage B:       120.0 s
recording:     600.0 s
wall timeout:  780.0 s
```

The controller-startup correction is also default-off. When enabled, the
control launch substitutes one transient package helper for the original two
concurrent Humble spawners. The helper processes
`joint_state_broadcaster`, then `velocity_controller`, issues at most one
load request for an observed-unloaded controller, confirms loaded state after
a missing or negative response, and otherwise fails nonzero. Configuration,
activation, readiness, and controller ownership remain upstream and
unchanged.

Fresh fixed source hashes are:

```text
3653a46c5a0ee4cf866cd257c6df2d9c18c745335f93b4fac400d0d51a313f97
  phase08_v7_m4_5_visible_probe.yaml
0eecc1337371ba75d8a6ae80e766415f8bdabe2a925d0034eaa2c6f2af34e384
  phase08_v7_m4_5_two_light_suite.yaml
```

### No-Gazebo validation evidence

Focused supervisor geometry/integration, schema, runner, recording, launch,
and controller-recovery tests:

```text
timeout --signal=INT --kill-after=20s 300s python3 -m pytest -q \
  test_escape_recenter.py test_state_machine.py \
  test_supervisor_integration.py test_scenario_schema.py \
  test_scenario_runner.py test_observability_contract.py \
  test_experiment_recording.py test_controller_spawner_recovery.py \
  --junitxml=/tmp/phase08_7_m4_5_focused.xml

376 passed, 1 skipped in 56.55 s
JUnit:
9dd900e898ade48db9ab8b54ab329b7d0d897826fff78cc5b4761c12c98aa30e
```

The retained radius-2 geometry proves a radial/source alignment of
`-0.9999689709`; default-off preserves the old radial fallback, while enabled
selection is finite, hard-safe, and nonreversing. The repeat-18412 retained
alignment of `-0.192921` does not trigger. The tests also cover exact bypass
release, one-recenter persistence, no forward-safe candidate, sub-threshold
displacement, nonfinite/stale geometry, room/collision/ownership faults,
exhausted recovery, Stage A and Stage B exact-boundary precedence, graceful
Stage A timeout, historical omission, lost controller response, confirmed
loaded state, and no duplicate load.

Broad ROS-independent functional regression:

```text
timeout --signal=INT --kill-after=20s 300s python3 -m pytest -q \
  ros2_ws/src/ros_esc/test \
  --ignore=test_flake8.py --ignore=test_pep257.py \
  -k 'not v4_population_adoption_is_exact_and_unused' \
  --junitxml=/tmp/phase08_7_m4_5_broad_functional.xml

655 passed, 3 skipped, 1 deselected in 116.91 s
JUnit:
ccaaad247e3521cba86ad35c9c882a14bc7b3d21aadc2b1c99238fef5beee720
```

The deselected test is the already documented retired V4 population-adoption
assertion. The three skips and one focused skip are existing conditional
environment cases; there are no failures or errors.

Fatal changed-file lint (`E9,F63,F7,F82`), modified-Python compilation,
fresh-scenario YAML parsing, launch XML parsing, and `git diff --check` all
pass. Exploratory repository-root `ament_flake8 .` and `ament_pep257 .`
remain failed inherited baselines, not M4.5 gates: the former reports
`16115` errors while recursively including generated `ros2_ws/build` copies,
and the latter reports `2551` errors across the repository. Their retained
logs are:

```text
/tmp/phase08_7_m4_5_repo_ament_flake8.log
SHA-256 aaf9dbf125ea9b2fc00722be51b97618c3f4e295fec76d7055bb02b96c2b2da1
/tmp/phase08_7_m4_5_repo_ament_pep257.log
SHA-256 26f5ac699b28fd0efc6c0f1aad5045b7f2b5ba0ab74977fa42dc1a5beea62d8a
```

The fresh isolated build command:

```text
colcon --log-base /tmp/phase08_7_m4_5_qual/log build \
  --base-paths ros2_ws/src \
  --build-base /tmp/phase08_7_m4_5_qual/build \
  --install-base /tmp/phase08_7_m4_5_qual/install \
  --packages-select ros_esc_interfaces ros_esc \
    turtlebot3_rotating_sensor \
  --event-handlers console_direct+
```

passed all three packages in `12.5 s`. The transient helper is installed
executable at:

```text
/tmp/phase08_7_m4_5_qual/install/turtlebot3_rotating_sensor/lib/
  turtlebot3_rotating_sensor/idempotent_controller_spawner.py
```

Byte parity passes for the installed supervisor helper/node, schema/runner,
both fresh scenarios, central Gazebo launch, control launch, and transient
spawner helper. Nonexecuting installed launch descriptions are retained at:

```text
/tmp/phase08_7_m4_5_installed_launch_description.txt
SHA-256 66b9e378c53bf6f688b0f2a0f064cc6a893efc4bd56eeba59ee3b7b2cde14ea2
/tmp/phase08_7_m4_5_installed_control_description.txt
SHA-256 7c90634210025eeb5315c7e3dc17ed46a52f87facdf656f658859ac7e877d7f3
```

Direct installed `OpaqueFunction` resolution proves:

```text
recovery false:
  controller_manager/spawner joint_state_broadcaster, 30.0 s
  controller_manager/spawner velocity_controller, 30.0 s
recovery true:
  turtlebot3_rotating_sensor/idempotent_controller_spawner.py
  joint_state_broadcaster, velocity_controller, 30.0 s
```

Installed dry-runs resolve one visible and eight headless cases with zero
unsupported cases. Every case has source-continuity and controller recovery
enabled, `480 + 120 <= 600 s`, `780 s` wall bound, exactly one declared local
and one global, maximum one fill, unchanged `1.20 m` primary proximity, and
unchanged non-gating `1.00 m` diagnostic. Retained dry-run summaries:

```text
/tmp/phase08_7_m4_5_visible_installed_dry_run_final.yaml
SHA-256 15e62bb04e1b4ac64293ddb6a56d4d2c3a7dd9b43508e71984a50b96840bae75
/tmp/phase08_7_m4_5_suite_installed_dry_run_final.yaml
SHA-256 17323344d29d51ddf289aef5a93910198b388bc778f76ec2a80300afd566f234
```

The case keys are fixed as:

```text
4058b99c8e404cdc9eea12e3ecabef5a6befc3085dc9f541faaec204745ec1d2
55c2915ad5505f91655732677bcf27a8a00ec5541131f1cc2e402eee9243a9a0
5e65ee0056c18f709a7ffa98aeadd98b76895ffca4fc7651ffda3ebf3017b2a5
78fc949728c62ed94eb5a4c298f1f7548c0f41b78a595a97ca0200270e88f2a5
83f022dbfa5a686b80d6802ae1e573ccb5e13fb3dc0377939c085a50a05decb9
d1091f0c7dc2341c7383e37f31e8973b40075c62d761407377cb656e38627c5c
c75b44f23fc62ff1b7b96e1525c0eeb0a05cc3b26a3ac5ca831f7f59acb38ef2
be5caf65d545c0a11544db51e845f22094ced94441aaa100a4ef50d15176db86
fb97070aa6f6fe5fde17a1a1356cfde46fc3b4dfb23966aa640763c93f363161
```

Historical hash regression passes. In particular:

```text
1559ee2ab0a7d2fa26834bc0bfd226aaa2b8d6d7dad62dcdac85ca2e83293eb4
  M4.4 visible scenario
78be277362ac060c7cb77c5d2215836cb914a95bd81a5ed9221f0db4bc62a188
  M4.4 two-light scenario
3b9badc92cf63739f65662158999e3c2aab71761f790e3f360be9a52e6f38688
  V6 selected repeats
8ecc1a231efec24401d74fef3cd5139d48c6029f88e71d044cefdf2fd14c5bef
  historical centered validation world
88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf
  shifted corner-origin validation world
```

The Phase 08 historical immutability manifest, all historical normalized
scenario keys/hashes, M4.3, M4.4, and V6 regressions pass. The Phase 05
`record_run.py` and `validate_run.py` are byte-unchanged from `HEAD`.
Canonical topics, cost sign/units, sole custom-controller `/cmd_vel`
ownership, physical-room faces, wall margin, collision rules, exact one-fill
cardinality, and final-zero/cleanup remain unchanged.

`validate_phase_context.sh 08 implement` passes. Fresh evidence roots do not
exist. No Gazebo, scenario runner, recorder, or rosbag process is active. ROS
domain `165` is empty with the daemon disabled, and display `:0` is
available. No physical, Phase 09, three-light, or M4.5 Gazebo action occurred.

## Current milestone

**Phase 08.7 M4.5 — IMPLEMENTED / NO-GAZEBO QUALIFICATION PASS / FRESH
VISIBLE AND SUITE INPUTS FIXED / NO SIMULATION DISPATCHED.**

### Next criterion

Checkpoint and commit this independently qualified implementation boundary.
Then record, checkpoint, and commit the exact fixed visible command; reconfirm
the clean evidence/process/domain boundary; and execute only the one visible
radius-2.0 probe. The headless suite remains gated on a complete visible pass.
The optional three-light probe, Phase 09, and physical hardware remain
unauthorized.

## Phase 08.7 M4.5 committed visible-dispatch boundary

The exact default-off source-continuity correction, staged-budget runner,
idempotent controller helper, regressions, fresh fixed scenarios, status, and
precommit checkpoint were committed at:

```text
f89e989bbad5645cd4ec3fe8f781577c50e6d4bb
phase 08.7: qualify M4.5 recovery corrections
```

The post-commit worktree is clean and
`validate_phase_context.sh 08 implement` passes. Source and isolated-install
scenario bytes remain identical:

```text
3653a46c5a0ee4cf866cd257c6df2d9c18c745335f93b4fac400d0d51a313f97
  visible scenario
0eecc1337371ba75d8a6ae80e766415f8bdabe2a925d0034eaa2c6f2af34e384
  conditional suite scenario
```

Both fresh evidence roots remain absent. No Gazebo, runner, recorder, rosbag,
or matching launch process is active. ROS domain `165` is empty with the CLI
daemon disabled. `DISPLAY=:0` passes `xdpyinfo`, and the evidence filesystem
has `310 GiB` available.

Exactly one fresh visible attempt is predeclared:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m4_5_qual/install/setup.bash
export ROS_DOMAIN_ID=165
export ROS_LOG_DIR=/tmp/phase08_7_m4_5_probe_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m4_5_probe_mpl
export TURTLEBOT3_MODEL=burger
export DISPLAY=:0
timeout --signal=INT --kill-after=90s 780s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m4_5_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m4_5_visible_probe.yaml \
  --operator Codex \
  --case-id v7_m4_5_probe_r2p0_a45_h25_18508 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_5_probe \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_5_probe/\
phase08_v7_m4_5_visible_probe_summary.yaml \
  --gui
```

The attempt will be retained without retry or in-run changes. The fixed
eight-case headless suite remains gated on a complete `48/48`, cleanup,
collision, forbidden-evidence, Stage A, exact one-fill, primary `1.20 m`
Stage B, final-zero, and combined visible pass. The optional three-light
probe, Phase 09, and physical hardware remain unauthorized.

## Current milestone

**Phase 08.7 M4.5 — QUALIFIED IMPLEMENTATION COMMITTED / ONE FIXED VISIBLE
TWO-LIGHT PROBE PREDECLARED / NO M4.5 SIMULATION YET.**

### Next criterion

Refresh the Phase 08 checkpoint against `f89e989`, commit this exact dispatch
record, reconfirm the clean process/evidence/domain boundary, and execute only
the bounded visible probe. Do not dispatch the headless suite unless that
visible attempt passes every declared predicate.

## Phase 08.7 M4.5 retained visible-probe failure

The one committed fixed visible attempt ran on ROS domain `165` from
`2026-07-30T12:48:48.771600Z` through
`2026-07-30T12:54:25.580679Z`. The outer timeout did not fire. The record
process returned `0`; the runner returned `1` because the combined behavioral
gate failed.

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_5_probe/
  2026-07-30/
  20260730T124849713987Z_simulation_phase08_v7_m4_5_visible_probe-
  v7_m4_5_probe_r2p0_a45_h25_18508-robust_gaussian_v_b36220b0
```

The immutable result is:

```text
controller startup and readiness: PASS
recording completeness:           PASS, 48/48
cleanup:                          PASS
collision expectation:            PASS, no collision
forbidden states/events:           PASS, none
final zero/readiness false:        PASS
Stage A local recovery:            PASS, 1 episode
unique fill cardinality:           PASS, exactly 1
Stage A time budget:               PASS
complete Stage B opportunity:      PASS, 120.020 s observed
Stage B global proximity:          FAIL
combined result:                   FAIL
```

Stage A completed at the live `155.119 s` sample. The full Stage B window
ended at `275.139 s`, position `(1.3800558824, 0.5554794317) m`, distance
`3.6282729279 m` from the global. None of `3533` valid post-Stage-A
noninterpolated samples entered the unchanged `1.20 m` primary radius or
the non-gating `1.00 m` radius.

The infrastructure corrections worked: the transient helper loaded,
configured, and activated both controllers in fixed order and exited
cleanly. The staged runner reserved and reported the full independent Stage B
budget. No wall stop, collision stop, physical-room violation, startup retry,
algorithm `TIMEOUT`, or `FAILSAFE` occurred.

The behavioral miss is a source-continuity trigger-calibration defect. The
source-led window moved `0.1784262940 m`, reduced global distance from
`2.9999382809 m` to `2.8880476402 m`, and ended with radial/source dot
`-0.8412123478`. The frozen M4.5 trigger required at most `-0.90`, so the
bypass correctly remained inactive and the unchanged radial fallback
`(-0.9252604036, -0.3793325526)` reversed the useful displacement. Because
continuity never armed, it also did not survive the later recoverable
recenter.

Read-only reconstruction of every retained M4.4 behavioral source window
shows that an explicit fresh `-0.80` threshold catches both radius-2
reversals (`-0.999969`, `-0.841212`) while leaving every retained passing
case outside the trigger; the nearest passing negative values are
`-0.336356` and repeat-18412's `-0.192921`. Pure replay at `-0.80` selects a
finite hard-safe outward/tangential forward-half-plane candidate and clears
the declared bypass release radius within the fixed lookahead.

Read-only SQLite `PRAGMA quick_check` returned `ok` for `582137` messages
across 34 topics. The standard analyzer ran exactly once into
`analysis/phase07`, wrote eight plots and eleven tables, and returned
`analysis_status: partial` with no analysis failures. The partial status is
limited to one AlgorithmState duration gap and unavailable generic
aggregate-target metrics; fresh Phase 05 validation passes and the direct
scenario result is complete.

Full report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_5_visible_probe_report.md
SHA-256
cd8c96e30cfe56e748147f2b5c28bc29af9b2cb50b7760b07f0c496e350f71b5
```

Retained hashes:

```text
c4f7da06667aa57f21c87d51d5a9c3cd1188bd55010dfe94cd39cc7ee6105e99
  visible summary
5d39fbcbf68c720ca35eb86a8e8aa2669445a20e42c8ad531ccd7cd0e065fd47
  completeness
0256fbce2cb2a302c1d7681febc6f103317d867d6198942b3ab88ebea23694fc
  scenario result
dfa0765978f67a4c317edc8e088fe62d29971da0ffb93ec348d5b8ac858f63be
  bag
197848518999cf2981007a1baa767ca8c33e0ae144f66a93d298c133ec6d0df7
  analysis completeness
caa56a51d65e75fe49721f15d35a89113765db6ee24b03a670955b5c901aa7c9
  analysis metrics
```

Cleanup reconfirmed no Gazebo, runner, recorder, analyzer, rosbag, or matching
launch process, and ROS domain `165` is empty with the CLI daemon disabled.
The conditional M4.5 headless suite did not run. No retry, in-run change,
three-light, Phase 09, physical, or hardware action occurred.

## Current milestone

**Phase 08.7 M4.5 — CLOSED / VISIBLE GATE BEHAVIORAL FAIL /
INFRASTRUCTURE, STAGE A, ONE-FILL, SAFETY, AND FULL-BUDGET PASS /
STAGE B FAIL / SUITE NOT RUN / NOT SIMULATION-READY.**

### Next criterion

Checkpoint and commit this immutable M4.5 result. Any further correction must
use a fresh reviewed version and fresh identities. The smallest supported
M4.6 correction is to preserve all M4.5 code and gates, explicitly move only
the enabled reversal threshold from `-0.90` to `-0.80`, add the exact
M4.5 geometry regression, qualify without Gazebo, and checkpoint/commit
before one fresh visible attempt. The optional three-light probe, Phase 09,
and physical hardware remain unauthorized.

## Phase 08.7 M4.6 Plan-only threshold boundary

The immutable M4.5 failure report/status/checkpoint were committed at:

```text
e86b5476313397d1bca5dd78524fdde9ccc5a6ad
phase 08.7: retain M4.5 visible failure
```

A fresh append-only M4.6 amendment is saved for review in:

```text
docs/codex/gesc_gaussian/plans/phase_08_7_plan.md
SHA-256
ddcc67c77c644f916dd3486c5ca71448f0224e84ba4d643015ad673bf9032dff
```

The Plan preserves all M4.5 production code and gates. It proposes no
production-source change: only fresh M4.6 scenarios explicitly select
`post_recovery_source_reversal_dot_threshold=-0.80`, while the default
remains `-0.90`, the feature remains default-off, and M4.5/historical inputs
remain byte-identical. Focused tests must bind the exact M4.5 geometry,
full M4.4 cross-case dot table, bypass release/persistence, normalized
scenario delta, staged budgets, startup recovery, and historical hashes.

After no-Gazebo qualification and commits, the fresh paired visible probe
would reuse seed `18508` under a new M4.6 identity/root so the threshold is
the only behavioral delta. A passing visible gate would conditionally open
one fresh eight-case headless suite using seeds `18609..18612`. Neither
stage is authorized merely by saving this Plan.

`validate_phase_context.sh 08 plan` passes. The only post-M4.5 checkout
change is this Plan amendment. No M4.6 source, test, scenario, build,
checkpoint beyond the Plan boundary, Gazebo, suite, three-light, Phase 09,
physical, or hardware action has started.

## Current milestone

**Phase 08.7 M4.6 — PLAN-ONLY EVIDENCE-CALIBRATED `-0.80` AMENDMENT SAVED /
NOT APPROVED / IMPLEMENTATION AND SIMULATION NOT STARTED.**

### Next criterion

Checkpoint and commit this Plan-only boundary for review. Do not implement or
run M4.6 until the user explicitly approves the fresh amendment. The optional
three-light probe, Phase 09, and physical hardware remain unauthorized.

## Phase 08.7 M4.6 authorization and no-Gazebo qualification

The user explicitly approved M4.6 implementation. The approved correction
has been implemented without production-source drift. Two fresh fixed inputs
were added:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v7_m4_6_visible_probe.yaml
  phase08_v7_m4_6_two_light_suite.yaml
```

Only those fresh scenarios explicitly select:

```text
post_recovery_source_reversal_dot_threshold: -0.80
```

The launch/supervisor default remains `-0.90`; the feature remains
default-off. M4.5 and every historical scenario remain byte-identical. No
production source, central launch, world, recorder, validator, controller,
modified-cost node, or spawner helper changed.

Exact retained M4.5 replay proves `-0.90` does not trigger at
`-0.8412123475`, while `-0.80` selects the declared finite hard-safe
direction `(-0.1814078764, -0.9834079430)`, with zero source reversal,
`0.5407048977` radial outward alignment, and a `0.8707616102 m` lookahead
fill distance beyond the `0.7086747487 m` release radius. The full retained
M4.4/M4.5 alignment table proves only the two observed radius-2 reversals
trigger; every retained pass remains outside the trigger.

No-Gazebo test evidence:

```text
targeted M4.6:
  14 passed in 1.10 s
  /tmp/phase08_7_m4_6_targeted.xml
  e974aa5ec9461b488de4d4c60b043bfb572a5c51fd9d099c69eb630e4b594581

focused:
  390 passed, 1 skipped in 54.99 s
  /tmp/phase08_7_m4_6_focused.xml
  de8fc93abeb31be8487957660bba7e7b3ce1c8670fa61f92e5ab582fd72195e5

broad ROS-independent:
  669 passed, 3 skipped, 1 deselected in 116.43 s
  /tmp/phase08_7_m4_6_broad_functional.xml
  a87e9078549f9f66e1148c79526d340579650a012838c8f894a56601f7d5aa03
```

The skips are unchanged environment-conditional cases; the deselection is
the documented retired V4 population-adoption assertion. There were no
failures or errors. Fatal changed-file lint, modified-Python compilation,
fresh YAML parsing, launch XML/Python parsing, `git diff --check`, and
`validate_phase_context.sh 08 implement` pass.

The fresh isolated three-package build at
`/tmp/phase08_7_m4_6_qual` passed in `11.8 s`. Source/install byte parity
passes for the supervisor helper/node, schema/runner, both fresh scenarios,
Gazebo launch, control launch, and idempotent spawner. Direct installed
`OpaqueFunction` resolution proves the legacy two-spawner path when recovery
is false and the one idempotent helper path when true. Installed launch
defaults still resolve continuity false, reversal threshold `-0.90`,
controller recovery false, and maximum one fill.

Installed dry-runs resolve one visible and eight headless cases with zero
unsupported cases:

```text
/tmp/phase08_7_m4_6_visible_installed_dry_run.yaml
4a33eada6b084435c0d44b3215fb5807b86af58783ff793631571c8109653d33
/tmp/phase08_7_m4_6_suite_installed_dry_run.yaml
4344ba59098cb96bae870a6a9b21806950134ca0852c57ab01b4d0537f0935ee
```

Every case preserves `480 + 120 <= 600 s`, the `780 s` wall timeout,
exactly one declared local and global, maximum one fill, the primary
`1.20 m` global proximity, and the non-gating `1.00 m` closer diagnostic.
The paired visible case key is
`0adae0a552ae5f715240dcc22d1478e710711e8e82429e6752daa7c45f6045a4`.

All sealed M4.5 summary, completeness, scenario-result, bag, analysis, and
report hashes match. Read-only SQLite `PRAGMA quick_check` remains `ok` for
`582137` messages and `34` topics. The full evidence record is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_6_no_gazebo_qualification.md
SHA-256
a3c649ba1ec3187b7d4918e1a937835ae0c5cdd7b3d47e13c22d33c31150eaee
```

No Gazebo or ROS runtime process started. Both M4.6 evidence roots remain
absent. No suite, three-light, Phase 09, physical, or hardware action
occurred.

## Current milestone

**Phase 08.7 M4.6 — IMPLEMENTED / NO-GAZEBO QUALIFICATION PASS /
READY TO CHECKPOINT AND COMMIT / GAZEBO NOT STARTED.**

### Next criterion

Checkpoint and commit this independently qualified no-Gazebo boundary.
After that commit, record and checkpoint the exact visible paired dispatch
command, then run only:

```text
suite: phase08_v7_m4_6_visible_probe
case:  v7_m4_6_probe_r2p0_a45_h25_18508
seed:  18508
root:  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_6_probe
```

The fixed eight-case headless suite remains closed unless that one visible
attempt passes every declared gate.

## Phase 08.7 M4.6 committed visible-dispatch boundary

The fresh explicit `-0.80` inputs, exact replay and retained-table
regressions, no-Gazebo validation report, live status, and precommit
checkpoint were committed at:

```text
957b7e448814b2e743ac49aba8f36ebfd5e94a36
phase 08.7: qualify M4.6 continuity calibration
```

The post-commit worktree is clean and
`validate_phase_context.sh 08 implement` passes. Source and isolated-install
visible-scenario bytes remain identical:

```text
deb08439f285a1bcff7e7b5fe763acbf095e7175d995367c626f9d83d7b30e11
```

Both fresh evidence roots remain absent. No Gazebo, runner, recorder, rosbag,
analyzer, or matching launch process is active. ROS domain `166` is empty
without a localhost restriction and with the CLI daemon disabled.
`DISPLAY=:0` passes `xdpyinfo`, the temporary ROS/MPL roots are absent, and
the evidence filesystem has `310 GiB` available.

Exactly one fresh visible attempt is predeclared:

```text
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m4_6_qual/install/setup.bash
export ROS_DOMAIN_ID=166
export ROS_LOG_DIR=/tmp/phase08_7_m4_6_probe_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m4_6_probe_mpl
export TURTLEBOT3_MODEL=burger
export DISPLAY=:0
timeout --signal=INT --kill-after=90s 780s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m4_6_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m4_6_visible_probe.yaml \
  --operator Codex \
  --case-id v7_m4_6_probe_r2p0_a45_h25_18508 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_6_probe \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_6_probe/\
phase08_v7_m4_6_visible_probe_summary.yaml \
  --gui
```

The attempt will be retained without retry or in-run changes. The fixed
eight-case headless suite remains gated on a complete `48/48`, cleanup,
collision, forbidden-evidence, Stage A, exact one-fill, primary `1.20 m`
Stage B, final-zero, and combined visible pass. The optional three-light
probe, Phase 09, and physical hardware remain unauthorized.

## Current milestone

**Phase 08.7 M4.6 — QUALIFIED IMPLEMENTATION COMMITTED / ONE FIXED VISIBLE
TWO-LIGHT PROBE PREDECLARED / NO M4.6 SIMULATION YET.**

### Next criterion

Refresh the Phase 08 checkpoint against `957b7e4`, commit this exact dispatch
record, reconfirm the clean process/evidence/domain boundary, and execute
only the bounded visible probe. Do not dispatch the headless suite unless
that visible attempt passes every declared predicate.

## Phase 08.7 M4.6 retained visible-probe failure

The one committed M4.6 visible attempt ran exactly once on ROS domain `166`
from `2026-07-30T18:15:54.073631Z` through
`2026-07-30T18:21:26.298012Z`. The outer timeout did not fire, the recorder
returned `0`, and the runner returned `1` because the combined behavioral
gate failed.

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_6_probe/
  2026-07-30/
  20260730T181555011761Z_simulation_phase08_v7_m4_6_visible_probe-
  v7_m4_6_probe_r2p0_a45_h25_18508-robust_gaussian_v_0a93dbb1
```

The immutable result is:

```text
controller startup/readiness:       PASS
recording and fresh validation:     PASS
cleanup:                            PASS
collision expectation:              PASS, no collision
forbidden evidence:                 PASS
final zero/readiness false:         PASS
Stage A local recovery:             PASS, exactly 1 episode
unique fill cardinality:            PASS, exactly 1
Stage A budget:                      PASS
complete Stage B opportunity:        PASS, 120.020 s
Stage B primary 1.20 m proximity:    FAIL
non-gating 1.00 m diagnostic:        FAIL
combined result:                     FAIL
conditional M4.6 headless suite:     NOT RUN
```

Stage A completed at simulation time `152.814 s`. All `3534` post-Stage-A
noninterpolated odometry samples were valid. The best Stage B sample was at
`225.336 s`, position `(1.7009517630, 1.5989658704) m`, distance
`2.6173470005 m` from the global. At the full Stage B boundary the robot was
`2.6388175166 m` from the global; the final recorded distance was
`2.6359799256 m`.

M4.6 did correct the M4.5 detector miss. At `164.700 s` the committed
`-0.80` threshold armed on a measured radial/source dot of
`-0.9383691118`. The downstream generic hard-safe selector then chose the
only initially safe nonnegative-source-half-plane candidate:

```text
direction:        (0.1339360130, -0.9909899820)
source alignment: approximately 0.0
source rotation:  -90 degrees
affine weight:     0.50
```

That tangent was safe but made no projected source progress. The bypass
increased global distance by `0.1656946276 m` and released at fixed fill
clearance at `172.200 s`. Release cleared the retained directions, ended
continuity/liveness guidance, and reduced affine weight from `0.50` to
`0.0`. Ordinary search then traveled `5.5220164059 m` with only
`0.4954968315 m` net displacement and never approached the global.

The retained geometry rules out wall and collision failsafes as the cause:

```text
Stage B x range:                    [1.1608383976, 1.8063755164] m
Stage B y range:                    [1.0444790512, 1.7015756466] m
minimum physical-wall clearance:    1.2944790512 m
minimum configured-inset clearance: 1.0944790512 m
```

No collision, algorithm `TIMEOUT`, in-readiness `FAILSAFE`, or room-boundary
event occurred. Relaxing the `1.20 m` operator-equivalent stop also cannot
convert the retained best distance of `2.6173470005 m` into a pass.

The bounded defect is downstream of the calibrated detector:

```text
detector and threshold:  PASS
hard safety:             PASS
continuity topology:     INCOMPLETE
selector priority:       permits a zero-progress tangent
release semantics:       clearance-only and premature
post-release liveness:   absent
affine persistence:      ends at clearance release
```

Pure reconstruction at the live arm geometry shows that the stored source
direction becomes hard-safe after approximately `0.425 m` of the necessary
tangential contour. A fresh correction therefore needs dynamic hard-safe
source-direction reacquisition, a source-resume leg with positive projected
progress before release, and continued affine/liveness assistance through
that leg. It must preserve the room/collision hard gates, default-off
behavior, V6 and every historical scenario, exact one-fill cardinality,
staged budgets, the `1.20 m` primary stop, final zero, and cleanup.

Standard analysis ran exactly once into `analysis/phase07`, completed with no
failures, and retained eight plots plus eleven tables. Fresh Phase 05
validation and the installed standalone validator pass. Read-only SQLite
`PRAGMA quick_check` returns `ok` for `579958` messages and `34` topics.

Retained hashes:

```text
b746f1083f006b20fed97e9a584ef480b615dac0126027683d21343d1cd6e93c  visible summary
a095e8e1c6046b65cc2d1d45e9cf2ea48d864003f34a555ba4a70ad9e2c323cc  completeness
fe3d5010c39282fdd104345a32680986cd0775d73a51c800ecb700fe7ec63aa2  scenario result
d52be6874dec45810949689b8e0ab0635526cb334fd8f122e492d95ffea2080b  bag
36687623660234baee372a448658965ec31d7c6cc90863ce73f0c18df7c8e79f  analysis completeness
81e9f44683872ba64249c73a80e95e5f6ee3193fc6229f3fc0c11847c25e7268  analysis metrics
db0a514252f83ba0b4eab379677bda237a2564fd5040f37bd3865de95589c112  resolved scenario
deb08439f285a1bcff7e7b5fe763acbf095e7175d995367c626f9d83d7b30e11  scenario definition
```

The complete result and diagnosis are retained in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_6_visible_probe_report.md
SHA-256
4a2f6b25c0098476f50e6eefe09f070805c77dc28c7c719707c5cf6b623b8836
```

Cleanup reconfirmed no Gazebo, runner, recorder, analyzer, rosbag, validator,
or matching launch process, and ROS domain `166` is empty with the CLI
daemon disabled. The conditional M4.6 suite root remains absent. No retry,
in-run change, suite case, three-light case, Phase 09, physical, or hardware
action occurred.

## Current milestone

**Phase 08.7 M4.6 — CLOSED / VISIBLE GATE BEHAVIORAL FAIL /
INFRASTRUCTURE, STAGE A, ONE-FILL, SAFETY, AND FULL-BUDGET PASS /
STAGE B FAIL / SUITE NOT RUN / NOT SIMULATION-READY.**

### Next criterion

Checkpoint and commit this immutable M4.6 result. Any further correction must
use a fresh reviewed version, fresh identities, complete no-Gazebo
qualification, and a committed dispatch boundary. The evidence supports a
dynamic source-reacquisition and source-resume corridor; it does not support
relaxing wall, collision, room, or global-proximity gates. The optional
three-light probe, Phase 09, and physical hardware remain unauthorized.

## Phase 08.7 M4.7 Plan-only dynamic source-resume boundary

The immutable M4.6 failure report, live status, and Phase 08 checkpoint were
committed at:

```text
75f8f2373f70e19661d8106622da0ea2e53c9a84
phase 08.7: retain M4.6 visible failure
```

The conditional M4.6 headless suite remains not run and its evidence root
remains absent. M4.6 cannot be retried, changed, relabelled, or counted in a
future denominator.

A fresh append-only M4.7 amendment is saved for review in:

```text
docs/codex/gesc_gaussian/plans/phase_08_7_plan.md
SHA-256
94027653dbd4f4fad158da5612bbdd2d3dad8c5dec4c5b420ff45906d0770236
```

The Plan introduces one fresh default-off corridor switch and one positive
distance:

```text
post_recovery_source_resume_enabled: false
post_recovery_source_resume_min_progress_m: 0.20
```

Fresh M4.7 inputs alone would enable the switch while retaining M4.6's
explicit `-0.80` detector threshold. Historical omission preserves the exact
M4.6/M4.5 fixed-clearance behavior, selector ordering, events, affine
behavior, and scenario bytes.

When enabled, the corridor uses a hard-safe source-half-plane selector that
ranks measured source alignment before excess clearance and recomputes on
every new pose. Fixed fill clearance becomes a transition to a
source-resume stage rather than guidance release. Normal release requires:

```text
signed measured-source progress: at least 0.20 m
live fill distance:              at least the fixed clearance target
existing outward/taper progress: at least 0.60 + 0.50 = 1.10 m
```

Affine support remains `0.50` until source progress is proved, then uses the
existing taper to zero. Liveness remains active through the corridor and one
bounded recoverable recenter; recenter displacement cannot count as source
progress. The algorithm receives no global coordinate or declared source
role.

M4.7 preserves the `0.20 m` wall margin, collision and physical-room hard
checks, exact one-fill topology, staged `480 + 120 <= 600 s` budgets, the
primary `1.20 m` operator-equivalent stop, non-gating `1.00 m` diagnostic,
final zero, cleanup, cost sign/units, canonical topics, and sole `/cmd_vel`
ownership.

The Plan predeclares a fresh paired visible identity at radius `2.0 m`,
angle `45 degrees`, and seed `18508`, followed only on a complete visible
pass by a fresh eight-case headless suite using seeds `18709..18712`.
Neither simulation stage is authorized by this Plan-only boundary.

`validate_phase_context.sh 08 plan` passes. The only post-M4.6 checkout
changes are the Plan amendment and this live-status record. No M4.7 source,
test, scenario, build, no-Gazebo qualification, runtime, Gazebo, suite,
three-light, Phase 09, physical, or hardware action has started.

## Current milestone

**Phase 08.7 M4.7 — PLAN-ONLY DEFAULT-OFF DYNAMIC SOURCE-RESUME CORRIDOR
SAVED / NOT APPROVED / IMPLEMENTATION AND SIMULATION NOT STARTED.**

### Next criterion

Checkpoint and commit this Plan-only boundary for review. Do not implement,
build, or run M4.7 until the user explicitly approves the fresh amendment.
After approval, implementation must pass every no-Gazebo gate and be
checkpointed and committed before a visible Gazebo process may start. The
conditional suite remains passing-gated; the optional three-light probe,
Phase 09, and physical hardware remain unauthorized.

## Phase 08.7 M4.7 authorization and no-Gazebo qualification

The user explicitly approved M4.7 implementation. The reviewed default-off
dynamic source-resume corridor is implemented in the existing helper,
supervisor, schema, and Gazebo-launch owners. The implementation adds:

```text
post_recovery_source_resume_enabled: false
post_recovery_source_resume_min_progress_m: 0.20
```

Fresh M4.7 inputs alone set the Boolean true and retain M4.6's explicit
`-0.80` reversal threshold:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v7_m4_7_visible_probe.yaml
  SHA-256
  1da37b5cdb8158723a937969447806e4d5e9e12b8f458e72fbb5764a0cb237ca

  phase08_v7_m4_7_two_light_suite.yaml
  SHA-256
  654b8fcb65fe565e340c4ee08250c036635bfb4e87a66ecbbc0654716c47f2f4
```

When enabled, the corridor recomputes a hard-safe source-aligned candidate
on every new pose, changes fixed clearance into a source-resume anchor,
requires `0.20 m` signed source progress plus live clearance and the
existing `1.10 m` outward/taper completion, holds affine weight at `0.50`
until source progress is acquired, and preserves liveness/source direction
through one bounded recenter while excluding recenter translation.
Duration exhaustion remains a finite typed release to ordinary search, not
a new failsafe.

No-Gazebo test evidence:

```text
targeted M4.7:
  15 passed, 275 deselected in 1.29 s
  /tmp/phase08_7_m4_7_targeted.xml
  0998bfad6e7666943772e61e27c4ea2e6d36eeea5cde4d83386cb26731808f29

focused:
  405 passed, 1 skipped in 53.98 s
  /tmp/phase08_7_m4_7_focused.xml
  33b08592d7ea9c2cf63570e715f3d871e2dfbf5976763653cf4ebd948145a914

broad ROS-independent:
  684 passed, 3 skipped, 1 deselected in 117.25 s
  /tmp/phase08_7_m4_7_broad_functional.xml
  8252faa82e50669c9c144da4de11449e1def6345940575cfb197541adb79ae70
```

Fatal changed-file lint, Python compilation, YAML/schema expansion, launch
XML parsing, `git diff --check`, and
`validate_phase_context.sh 08 implement` pass.

The fresh isolated three-package build at
`/tmp/phase08_7_m4_7_qual` passed in `12.0 s`. Source/install byte parity
passes for the helper/node, schema/runner, both fresh scenarios, Gazebo
launch, control launch, and controller-spawner helper. Installed defaults
resolve resume false, resume distance `0.20`, continuity false, threshold
`-0.90`, recovery false, and maximum one fill. Both installed controller
branches resolve exactly as before.

Installed dry-runs resolve one visible and eight headless cases with zero
unsupported cases:

```text
/tmp/phase08_7_m4_7_visible_installed_dry_run.yaml
f7c439366e5fefab3b16ed82e130be17de4bb623a51e71fe105f55dae9e3363d

/tmp/phase08_7_m4_7_suite_installed_dry_run.yaml
b48fc12cb96ef52f289b939a971e8c58760c3a9181552f232b7253e925d4c2e9
```

Every case preserves one local/global, maximum one fill, staged
`480+120<=600 s`, the primary `1.20 m` operator-equivalent stop, non-gating
`1.00 m` diagnostic, collision false, final zero, and cleanup. Normalized
M4.7 cases differ from M4.6 only by fresh identity/seed and the two explicit
resume fields.

The immutable M4.6 report, summary, completeness, scenario result, bag,
analysis, resolved scenario, and installed scenario hashes all match.
Read-only SQLite `PRAGMA quick_check` remains `ok` for `579958` messages
and `34` topics. M4.6, M4.5, M4.4, M4.3, V6, shifted/historical worlds,
historical scenarios, cost sign/units, canonical topics, sole `/cmd_vel`
ownership, recorder/validator ownership, and retained evidence remain
unchanged.

The durable qualification report is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_7_no_gazebo_qualification.md
SHA-256
bb802b789020ae6756f67d9253c0a7d993092073a50852e1f6c1553802d4c089
```

Both M4.7 production evidence roots remain absent. No Gazebo, scenario
runner, recorder, rosbag, analyzer, or matching ROS process is active. No
Gazebo, suite, three-light, Phase 09, physical, or hardware action occurred.

## Current milestone

**Phase 08.7 M4.7 — IMPLEMENTED / NO-GAZEBO QUALIFICATION PASS /
READY TO CHECKPOINT AND COMMIT / GAZEBO NOT STARTED.**

### Next criterion

Checkpoint and commit this independently qualified no-Gazebo boundary.
After that commit, record and checkpoint the exact fixed visible paired
dispatch command before starting Gazebo. Run only:

```text
suite: phase08_v7_m4_7_visible_probe
case:  v7_m4_7_probe_r2p0_a45_h25_18508
seed:  18508
root:  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_7_probe
```

The fixed eight-case headless suite remains closed unless that one visible
attempt passes every declared predicate. The optional three-light probe,
Phase 09, and physical hardware remain unauthorized.

## Phase 08.7 M4.7 committed visible-dispatch boundary

The default-off source-resume implementation, fresh fixed inputs, complete
no-Gazebo qualification, durable report, live status, and Phase 08
precommit checkpoint were committed at:

```text
22877724bb2e31d444f2af7c09df5f108688a6c0
phase 08.7: qualify M4.7 source-resume corridor
```

The post-commit worktree is clean,
`validate_phase_context.sh 08 implement` passes, the isolated qualified
install remains available, both M4.7 production evidence roots are absent,
the visible display socket is available, and no Gazebo, runner, recorder,
rosbag, analyzer, or matching ROS process is active.

The one allowed visible dispatch is fixed to:

```text
suite:       phase08_v7_m4_7_visible_probe
version:     phase08-v7-m4-7-probe
case:        v7_m4_7_probe_r2p0_a45_h25_18508
case key:    e48c200b54a7a9d9049b5965ef9c773b166e6672df155f0d9ccff459da83f3e8
local:       (1.4142135623730951, 1.4142135623730950)
global:      (3.5, 3.5)
seed:        18508
ROS domain:  167
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_7_probe
```

The exact bounded dispatch command is:

```bash
source /opt/ros/humble/setup.bash
source /tmp/phase08_7_m4_7_qual/install/setup.bash
export ROS_DOMAIN_ID=167
export ROS_LOG_DIR=/tmp/phase08_7_m4_7_probe_ros_logs
export MPLCONFIGDIR=/tmp/phase08_7_m4_7_probe_mpl
export TURTLEBOT3_MODEL=burger
export DISPLAY=:0
timeout --signal=INT --kill-after=90s 900s \
  ros2 run ros_esc run_scenario \
  /tmp/phase08_7_m4_7_qual/install/ros_esc/share/ros_esc/\
scenario_runner/scenarios/phase08_v7_m4_7_visible_probe.yaml \
  --operator Codex \
  --case-id v7_m4_7_probe_r2p0_a45_h25_18508 \
  --runs-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_7_probe \
  --summary-output \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_7_probe/\
phase08_v7_m4_7_visible_probe_summary.yaml \
  --gui
```

The scenario owns the declared `780 s` wall bound; the outer `900 s`
envelope exists only to retain a bounded cleanup opportunity. This command
may run once without parameter changes or retry. Any result is retained.
The fixed headless suite remains closed unless this visible attempt passes
all infrastructure, behavioral, staged, safety, final-zero, and cleanup
predicates.

## Current milestone

**Phase 08.7 M4.7 — QUALIFIED IMPLEMENTATION COMMITTED / ONE FIXED VISIBLE
TWO-LIGHT PROBE PREDECLARED / NO M4.7 SIMULATION YET.**

### Next criterion

Checkpoint and commit this exact dispatch boundary, then execute the command
once. Preserve the attempt and stop on any failure. Do not dispatch the
headless suite unless the visible combined result passes every predicate.

## Phase 08.7 M4.7 retained visible-probe failure

The exact visible-dispatch boundary was checkpointed and committed before
execution at:

```text
e7fb0832f1367f25720da78ef42ecc1a96c87da7
phase 08.7: checkpoint M4.7 visible dispatch
```

The one predeclared visible attempt then ran exactly once on ROS domain
`167`. It is retained at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_7_probe/
  2026-07-30/
  20260730T192901277523Z_simulation_phase08_v7_m4_7_visible_probe-
  v7_m4_7_probe_r2p0_a45_h25_18508-robust_gaussian_v_97a8eeda
```

The outer timeout did not fire. Recording returned `0`; the runner returned
`1` because the combined behavioral gate failed. Infrastructure,
readiness, cleanup, no collision, forbidden-state/event absence, final
zero/readiness false, the required recovery path/events, Stage A, exactly
one created/typed/active fill, and the complete `120.020 s` Stage B
opportunity all pass.

Stage B fails. Its timeout sample was
`(1.5263398997, 1.3052441668) m`, `2.9516584082 m` from the global.
There were `3534` valid post-Stage-A noninterpolated odometry samples, zero
invalid samples, and none within the primary `1.20 m` or diagnostic
`1.00 m` radius. The reconstructed best post-Stage-A distance was
`2.7448591895 m`.

M4.7's new source-resume corridor did not arm. The live source-led handoff
started at `157.500 s` and stalled at `169.500 s`. At that stall boundary,
the reconstructed radial/source dot was `+0.0141931043`, correctly outside
the explicit `-0.80` reversal detector. The measured source-led direction
was global-opposing with global-direction alignment `-0.5248527808`.
There is no source-continuity bypass, source-resume corridor,
direction-change, clearance, projected-progress, corridor completion, or
corridor exhaustion event. The retained generic fallback instead refreshed
direction, requested one recoverable recenter, then released to ordinary
search.

This was not a wall, collision, failsafe, room-boundary, staged-budget, or
global-stop failure. Minimum physical-wall clearance during Stage B was
`0.7866039955 m`; no collision, algorithm `TIMEOUT`, in-readiness
`FAILSAFE`, or room-boundary event occurred. The stop was the planned
post-Stage-A boundary.

The standard analyzer ran exactly once and completed with zero failures,
eight plots, and eleven tables. Fresh Phase 05 and standalone installed
validation pass. Read-only SQLite validation returns `quick_check=ok` for
`587675` messages and `34` topics. The bag hash remained unchanged.

The durable report is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_7_visible_probe_report.md
SHA-256
35c5c0efb896e9864c48c8957a495f696e3c40f96a86f20a12ad60f67f563684
```

No retry or parameter change occurred. The fixed headless suite did not run
and its evidence root remains absent. No three-light, Phase 09, physical, or
hardware action occurred.

## Current milestone

**Phase 08.7 M4.7 — CLOSED / VISIBLE GATE BEHAVIORAL FAIL /
INFRASTRUCTURE, STAGE A, ONE-FILL, SAFETY, FULL-BUDGET PASS /
STAGE B FAIL / CORRIDOR NOT ARMED / SUITE NOT RUN /
NOT SIMULATION-READY.**

### Next criterion

Finalize the report hash, checkpoint this retained failed boundary, and
commit it. Any further correction requires a fresh reviewed version, fresh
identities, complete no-Gazebo qualification, checkpoint, and commit before
another simulation. Do not retry M4.7 or dispatch its headless suite.

## Phase 08.7 M4.8 retained-success reproduction authority

On 2026-07-30 the user authorized fresh reproduction attempts for all `17`
retained Phase 08.7 runs whose robot behavior previously passed Stage A,
exact fill cardinality, Stage B, collision, and forbidden-state/event gates.
The durable campaign amendment is appended to
`plans/phase_08_7_plan.md`, SHA-256:

```text
22b63bf0fff114b65b351f573139173ec0d85967704d6fb5d9da3781e215cece
```

M4.8 changes no algorithm or scenario. It will re-execute the exact sealed
case definitions and seeds under fresh run IDs, summary paths, ROS domains,
logs, and the absent campaign root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_v7_success_reproduction_1
```

The selected population contains one M2.3 case, one M3 case, the M4, M4.2,
M4.3, and M4.4 visible cases, six passing M4.3 suite cases, and five passing
M4.4 suite cases. The original five visible contexts remain visible; the
suite cases remain headless. All use the original `400/1600` relative-lumen
inputs. M3 retains its `1.00 m` primary Stage B boundary; the other sixteen
retain `1.20 m`.

Every repeat will be retained without parameter changes or retry. Behavioral,
formal, or infrastructure failure does not rewrite the original successful
result. Cleanup failure stops later dispatch. At least `9/17` fresh formal
combined passes is reported as the user's literal “most pass again”
observation, not as broad spatial robustness or retroactive repair of a
failed suite.

No Gazebo process has started for M4.8. The campaign root is absent and the
worktree contained no pre-existing change before this Plan amendment.

### Physical termination clarification

On 2026-07-30 the user explicitly clarified that the simulation
`1.20 m`/`1.00 m` global-proximity stops must not apply to real physical
testing. Physical termination remains under operator control: the robot
continues until the operator judges it sufficiently close to the global and
presses `Ctrl+C`.

The current ownership supports that separation without an algorithm fork:
`run_scenario.py` hard-codes `record_run --mode simulation`, exposes no
physical mode, and owns the live post-recovery distance monitor that cancels
the scoped simulation process. Future Phase 09 physical execution must use
the audited physical launch/recording path without an automatic
global-proximity termination monitor. The distance may be retained as a
diagnostic. Manual `Ctrl+C` must enter the existing ordered recorder
shutdown/final-zero path. No physical source or hardware action was taken for
this clarification.

## Phase 08.7 M4.8 no-Gazebo qualification

The complete no-Gazebo qualification passed on 2026-07-30. The retained
machine-readable manifest is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_8_success_reproduction_manifest.json
SHA-256
69d946c64718fdc725485fdffe5d41878b72825341d17f50777dddef3e13cc1f
```

Read-only original-evidence discovery found exactly one source run for every
selected case: `17/17` behavioral passes, `15/17` formal passes, and
`17/17` cleanup passes. The two non-formal results are the preserved M4 and
M4.2 recording-evidence failures; both still passed Stage A, exact one-fill
cardinality, Stage B, collision, and forbidden-state/event behavior. No
historical result was rewritten.

Qualification evidence:

```text
focused:
  405 passed, 1 skipped in 56.28 s
  c1d87e369d3e32d8e6ec46ae084cd7fb9d452cf1adba58c0c47ded0602907157
broad ROS-independent:
  684 passed, 3 skipped, 1 deselected in 118.88 s
  3e5436b35d27006e4c3f64778f6d024697e1e3d27cf41ea6c6c200c03fbe824c
isolated build:
  ros_esc_interfaces, ros_esc, turtlebot3_rotating_sensor
  3 packages finished in 12.0 s
source/install parity:
  22 owner pairs PASS
installed dry-run expansion:
  8 dispatches, 17 exact cases, 0 unsupported
```

Fatal Python lint, Python compilation, JSON/YAML/XML parsing,
`git diff --check`, current Phase 08 context validation, installed launch
argument/description resolution, shifted-world parity, exact case keys,
simulation-only mode, declared GUI/headless modes, stop radii, and fresh
root routing all pass. The dry-runs did not create the campaign root.

The fixed dispatch table is:

| Order | Label | Domain | GUI | Outer bound | Cases | Fresh child |
|---:|---|---:|---|---:|---:|---|
| 1 | `m2_3` | 168 | yes | 660 s | 1 | `m2_3` |
| 2 | `m3` | 169 | no | 660 s | 1 | `m3` |
| 3 | `m4` | 170 | yes | 660 s | 1 | `m4` |
| 4 | `m4_2` | 171 | yes | 900 s | 1 | `m4_2` |
| 5 | `m4_3_probe` | 172 | yes | 900 s | 1 | `m4_3_probe` |
| 6 | `m4_3_suite` | 173 | no | 4500 s | 6 | `m4_3_suite` |
| 7 | `m4_4_probe` | 174 | yes | 900 s | 1 | `m4_4_probe` |
| 8 | `m4_4_suite` | 175 | no | 3900 s | 5 | `m4_4_suite` |

Each invocation uses the scenario and repeated `--case-id` values sealed in
the manifest, operator `phase08_7_m4_8`, isolated install
`/tmp/phase08_7_success_reproduction_qual/install`, distinct `/tmp` ROS log
and MPL roots, and a summary in its fresh child. The sole campaign root is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_v7_success_reproduction_1
```

The durable qualification report is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_8_no_gazebo_qualification.md
SHA-256
cf65583e809e1003ead331a0c43ee7732ba9e6385a53692dfb42c3b96ff52b55
```

At qualification close the campaign root is absent,
`/tmp/.X11-unix/X0` is available, and no matching Gazebo, scenario runner,
recorder, rosbag recorder, or analyzer process is active. No physical or
hardware action occurred.

## Current milestone

**Phase 08.7 M4.8 — NO-GAZEBO QUALIFICATION PASS /
17 EXACT HISTORICAL SUCCESS DEFINITIONS SEALED /
8 INSTALLED DISPATCHES DRY-RUN PASS / CAMPAIGN ROOT ABSENT /
GAZEBO DISPATCH CHECKPOINT AND COMMIT PENDING.**

### Next criterion

Checkpoint Phase 08, inspect and commit this qualified dispatch boundary,
then execute all eight invocations serially. Retain every attempt without
retry. Continue after behavioral/formal/infrastructure failure only when
the case evidence is readable and scoped cleanup passes; stop later
dispatch for cleanup leak, evidence corruption, or source drift.

## Phase 08.7 M4.8 reproduction progress

### Dispatch 1 — M2.3 visible

The exact visible M2.3 reproduction ran once on ROS domain `168` from the
qualified installed scenario. The outer `660 s` timeout did not fire.

```text
case:
  v7_m2_3_diagonal_r1p5_h25_18001
run ID:
  20260730T202517751818Z_simulation_phase08_v7_m2_3_assisted_recovery_stop_probe-v7_m2_3_diagonal_r1p5_h25_18001-rob_57557390
fresh root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
    phase08_v7_success_reproduction_1/m2_3
```

Result:

```text
formal combined:                PASS
recording/completeness:         PASS
cleanup:                        PASS
Stage A local recovery:         PASS
exact one-fill cardinality:     PASS
Stage B <= 1.20 m:              PASS at 1.1996881207 m
collision/forbidden evidence:   PASS
SQLite quick_check:             ok
bag messages/topics:            505819 / 34
```

The observed recovery path was direct
`SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE ->
RECENTER -> SEARCH`. No retry or parameter change occurred. Scoped process
cleanup passed before the next dispatch.

## Current milestone

**Phase 08.7 M4.8 — 1/17 REPRODUCTIONS EXECUTED /
1/1 FORMAL PASS / CLEANUP PASS / SERIAL CAMPAIGN CONTINUES.**

### Next criterion

Execute the one selected M3 case once on ROS domain `169`, retain its
stricter `1.00 m` result, validate readable evidence and cleanup, then
continue only if the stop conditions permit.

### Dispatch 2 — M3 headless

The selected M3 case ran once on ROS domain `169`. The outer `660 s`
timeout did not fire.

```text
case:
  v7_m3_r1p0_a45_h25_18101
run ID:
  20260730T203049438017Z_simulation_phase08_v7_m3_spatial_suite-v7_m3_r1p0_a45_h25_18101-robust_gaussian_v1-75d0c27b_8c0d4a9b
fresh root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
    phase08_v7_success_reproduction_1/m3
```

Result:

```text
formal combined:                PASS
recording/completeness:         PASS
cleanup:                        PASS
Stage A local recovery:         PASS
exact one-fill cardinality:     PASS
non-gating 1.20 m approach:     PASS at 1.1973876036 m
primary Stage B <= 1.00 m:      PASS at 0.9997559645 m
collision/forbidden evidence:   PASS
SQLite quick_check:             ok
bag messages/topics:            436263 / 34
```

The recovery path was direct. No retry or parameter change occurred, and
scoped process cleanup passed.

## Current milestone

**Phase 08.7 M4.8 — 2/17 REPRODUCTIONS EXECUTED /
2/2 FORMAL PASS / CLEANUP PASS / SERIAL CAMPAIGN CONTINUES.**

### Next criterion

Execute the M4 visible behavioral-success/evidence-failure source case once
on ROS domain `170`. Judge the fresh run under its current unchanged
scenario contract; do not rewrite the original failed completeness result.

### Dispatch 3 — M4 visible

The selected M4 case ran once on ROS domain `170`. The outer `660 s`
timeout did not fire. The fresh run is a behavioral Stage B failure; it is
not a retry or relabel of the original behavioral-pass/evidence-fail result.

```text
case:
  v7_m4_probe_r1p5_a45_h25_18201
run ID:
  20260730T203530694811Z_simulation_phase08_v7_m4_visible_probe-v7_m4_probe_r1p5_a45_h25_18201-robust_gaussian_v1-a7_9bbd365c
fresh root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
    phase08_v7_success_reproduction_1/m4
```

Result:

```text
formal combined:                     FAIL
infrastructure/recording/completeness: PASS
cleanup:                             PASS
Stage A local recovery:              PASS
exact one-fill cardinality:          PASS
primary Stage B <= 1.20 m:           FAIL
valid post-Stage-A samples:          1949
final global distance:               2.3113715830 m
collision/forbidden evidence:        PASS
SQLite quick_check:                  ok
bag messages/topics:                 769758 / 34
```

The recovery path was direct. No retry or parameter change occurred.
Because the bag, completeness document, scenario result, SQLite database,
and scoped cleanup are valid, the M4.8 contract permits continuing while
retaining this failed reproduction.

## Current milestone

**Phase 08.7 M4.8 — 3/17 REPRODUCTIONS EXECUTED /
2 FORMAL PASS, 1 BEHAVIORAL FAIL / ALL 3 CLEANUP PASS /
SERIAL CAMPAIGN CONTINUES.**

### Next criterion

Execute the selected M4.2 visible case once on ROS domain `171`; preserve
the M4 failure above and every original result.

### Dispatch 4 — M4.2 visible

The selected M4.2 case ran once on ROS domain `171`. The outer `900 s`
timeout did not fire. Unlike its historical behavioral-pass/evidence-fail
attempt, the fresh evidence is formally complete.

```text
case:
  v7_m4_2_probe_r1p5_a45_h25_18208
run ID:
  20260730T204335759244Z_simulation_phase08_v7_m4_2_visible_probe-v7_m4_2_probe_r1p5_a45_h25_18208-robust_gaussian_v_d68fb585
fresh root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
    phase08_v7_success_reproduction_1/m4_2
```

Result:

```text
formal combined:                PASS
recording/completeness:         PASS
cleanup:                        PASS
Stage A local recovery:         PASS
exact one-fill cardinality:     PASS
primary Stage B <= 1.20 m:      PASS at 1.1992809523 m
non-gating <= 1.00 m:           not reached
collision/forbidden evidence:   PASS
SQLite quick_check:             ok
bag messages/topics:            609578 / 34
```

The recovery path was direct. No retry or parameter change occurred, and
scoped process cleanup passed.

## Current milestone

**Phase 08.7 M4.8 — 4/17 REPRODUCTIONS EXECUTED /
3 FORMAL PASS, 1 BEHAVIORAL FAIL / ALL 4 CLEANUP PASS /
SERIAL CAMPAIGN CONTINUES.**

### Next criterion

Execute the selected M4.3 visible case once on ROS domain `172`, then
validate its evidence and cleanup before the six-case headless invocation.

### Dispatch 5 — M4.3 visible

The selected M4.3 visible case ran once on ROS domain `172`. The outer
`900 s` timeout did not fire.

```text
case:
  v7_m4_3_probe_r1p5_a45_h25_18308
run ID:
  20260730T204959182242Z_simulation_phase08_v7_m4_3_visible_probe-v7_m4_3_probe_r1p5_a45_h25_18308-robust_gaussian_v_2544bb99
fresh root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
    phase08_v7_success_reproduction_1/m4_3_probe
```

Result:

```text
formal combined:                PASS
recording/completeness:         PASS
cleanup:                        PASS
Stage A local recovery:         PASS
exact one-fill cardinality:     PASS
primary Stage B <= 1.20 m:      PASS at 1.1979801903 m
non-gating <= 1.00 m:           not reached
collision/forbidden evidence:   PASS
SQLite quick_check:             ok
bag messages/topics:            573469 / 34
```

The recovery path was direct. No retry or parameter change occurred, and
scoped cleanup passed.

## Current milestone

**Phase 08.7 M4.8 — 5/17 REPRODUCTIONS EXECUTED /
4 FORMAL PASS, 1 BEHAVIORAL FAIL / ALL 5 CLEANUP PASS /
SERIAL CAMPAIGN CONTINUES.**

### Next criterion

Execute the six selected M4.3 headless cases serially in their one fixed
runner invocation on ROS domain `173`. Preserve each outcome once and stop
later dispatch only on the declared cleanup/evidence-integrity conditions.

### Dispatch 6 — M4.3 six-case headless subset

The single fixed M4.3 invocation executed all six selected cases serially on
ROS domain `173`. The outer `4500 s` timeout did not fire. The runner
returned `1` because one behavioral predicate and one independent recording
evidence predicate failed; every case executed once.

| Case | Stage A / fill | Stage B | Completeness | Cleanup | Fresh result |
|---|---|---|---|---|---|
| `v7_m4_3_r1p5_a45_h25_18309` | pass / pass | pass, `1.1999686228 m` | pass | pass | formal pass |
| `v7_m4_3_r1p5_a67p5_h25_18309` | pass / pass | pass, `1.1972467912 m` | pass | pass | formal pass |
| `v7_m4_3_r2p0_a45_h25_18309` | pass / pass | fail, final `1.2138798751 m` | pass | pass | behavioral fail |
| `v7_m4_3_repeat_r1p5_a45_h25_18310` | pass / pass | pass, `1.1983976710 m` | pass | pass | formal pass |
| `v7_m4_3_repeat_r1p5_a45_h25_18311` | pass / pass | pass, `1.1973676652 m` | fail | pass | behavior pass / evidence fail |
| `v7_m4_3_repeat_r1p5_a45_h25_18312` | pass / pass | pass, `1.1977328460 m` | pass | pass | formal pass |

Subset totals:

```text
formal combined:                4/6 PASS
behavioral Stage B:             5/6 PASS
Stage A / one-fill:             6/6 PASS
recording completeness:         5/6 PASS
collision/forbidden evidence:   6/6 PASS
cleanup:                        6/6 PASS
SQLite quick_check:             6/6 ok
```

The radius-2.0 case retained `3533` valid post-Stage-A samples but no sample
inside `1.20 m`. The seed-18311 repeat passed every behavioral predicate,
final zero, clean shutdown metadata, and bag readability; its sole
completeness failure was this retained console marker:

```text
[spawner-4]: process has died ... spawner velocity_controller ...
exit code 1
```

The case still produced `539383` readable messages on `34` topics and
scoped cleanup passed, so the declared M4.8 continuation condition remained
satisfied. The other per-case message counts were `560691`, `352528`,
`582491`, `629764`, and `447639`, each on `34` topics. No retry, parameter
change, or post-outcome correction occurred.

## Current milestone

**Phase 08.7 M4.8 — 11/17 REPRODUCTIONS EXECUTED /
8 FORMAL PASS, 1 BEHAVIORAL-PASS/EVIDENCE-FAIL,
2 BEHAVIORAL FAIL / ALL 11 CLEANUP PASS /
SERIAL CAMPAIGN CONTINUES.**

### Next criterion

Execute the selected M4.4 visible case once on ROS domain `174`, validate
its evidence and cleanup, then proceed to the final five-case headless
invocation only if the declared continuation conditions remain satisfied.

### Dispatch 7 — M4.4 visible

The selected M4.4 visible case ran once on ROS domain `174`. The outer
`900 s` timeout did not fire.

```text
case:
  v7_m4_4_probe_r1p5_a45_h25_18408
run ID:
  20260730T212658986946Z_simulation_phase08_v7_m4_4_visible_probe-v7_m4_4_probe_r1p5_a45_h25_18408-robust_gaussian_v_e00e619d
fresh root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
    phase08_v7_success_reproduction_1/m4_4_probe
```

Result:

```text
formal combined:                PASS
recording/completeness:         PASS
cleanup:                        PASS
Stage A local recovery:         PASS
exact one-fill cardinality:     PASS
primary Stage B <= 1.20 m:      PASS at 1.1992401437 m
non-gating <= 1.00 m:           not reached
collision/forbidden evidence:   PASS
SQLite quick_check:             ok
bag messages/topics:            512023 / 34
```

The recovery path was direct. No retry or parameter change occurred, and
scoped cleanup passed. This result raises the fresh formal-pass count to
`9/12`, satisfying the user-defined literal “most pass again” threshold of
at least `9/17`. It does not stop or redefine the authorized 17-case
campaign.

## Current milestone

**Phase 08.7 M4.8 — 12/17 REPRODUCTIONS EXECUTED /
9 FORMAL PASS, 1 BEHAVIORAL-PASS/EVIDENCE-FAIL,
2 BEHAVIORAL FAIL / USER-DEFINED MOST THRESHOLD REACHED /
ALL 12 CLEANUP PASS / FINAL FIVE CASES PENDING.**

### Next criterion

Execute all five selected M4.4 headless cases serially in their one fixed
invocation on ROS domain `175`. Preserve each outcome once, then close
Gazebo dispatch and begin whole-campaign validation and analysis.

### Dispatch 8 — M4.4 five-case headless subset

The single fixed M4.4 invocation executed all five selected cases serially
on ROS domain `175`. The outer `3900 s` timeout did not fire. The runner
returned `1` because one case did not complete Stage A; every case executed
once.

| Case | Stage A / fill | Stage B | Completeness | Cleanup | Fresh result |
|---|---|---|---|---|---|
| `v7_m4_4_r1p0_a45_h25_18409` | fail / fail | unavailable; final `3.7207540935 m` | pass | pass | behavioral fail |
| `v7_m4_4_r1p5_a45_h25_18409` | pass / pass | pass, `1.1993091417 m` | pass | pass | formal pass |
| `v7_m4_4_r1p5_a67p5_h25_18409` | pass / pass | pass, `1.1996182415 m` | pass | pass | formal pass |
| `v7_m4_4_repeat_r1p5_a45_h25_18411` | pass / pass | pass, `1.1997388853 m` | pass | pass | formal pass |
| `v7_m4_4_repeat_r1p5_a45_h25_18412` | pass / pass | pass, `1.1998614311 m` | pass | pass | formal pass |

Subset totals:

```text
formal combined:                4/5 PASS
behavioral Stage A:             4/5 PASS
behavioral Stage B:             4/5 PASS, one unavailable
recording completeness:         5/5 PASS
collision/forbidden evidence:   5/5 PASS
cleanup:                        5/5 PASS
SQLite quick_check:             5/5 ok
```

The radius-1.0 case remained in `SEARCH`, produced only two
`CONVERGENCE_CANDIDATE` events, created no fill, and never opened Stage B.
Its recording still contains `1027534` readable messages on `34` topics.
The four passing cases contain `460651`, `353730`, `552298`, and `620166`
messages respectively, each on `34` topics. No retry or parameter change
occurred.

### Completed raw campaign tally

All `17` selected definitions executed exactly once in the sealed order:

```text
formal combined pass:                 13/17
behavioral pass, evidence fail:        1/17
behavioral failure:                    3/17
Stage A local recovery:               16/17
exact one-fill cardinality:           16/17
Stage B, all cases:                   14 pass, 2 fail, 1 unavailable
Stage B after completed Stage A:      14/16 pass, 2 fail
collision/forbidden evidence:         17/17 pass
cleanup:                              17/17 pass
SQLite quick_check:                   17/17 ok
user-defined most threshold:          PASS (13 >= 9)
```

The three behavioral failures are:

1. M4 visible: Stage A passed, Stage B missed, final `2.3113715830 m`;
2. M4.3 radius-2.0: Stage A passed, Stage B missed, final
   `1.2138798751 m`;
3. M4.4 radius-1.0: Stage A never completed, final `3.7207540935 m`.

The independent evidence failure is M4.3 repeat seed `18311`: all
behavioral gates passed at `1.1973676652 m`, but completeness rejected a
controller-spawner exit marker. Original results remain immutable.

At dispatch close no matching Gazebo, runner, recorder, or rosbag process
remains. No automatic retry, three-light case, Phase 09 action, physical
command, or hardware command occurred.

## Current milestone

**Phase 08.7 M4.8 — ALL 17 REPRODUCTIONS EXECUTED ONCE /
13 FORMAL PASS / MOST THRESHOLD PASS /
17 SQLITE INTEGRITY AND CLEANUP PASS /
STANDARD VALIDATION, ANALYSIS, FINAL REPORT, CHECKPOINT PENDING.**

### Next criterion

Run the standard standalone validator and analyzer once against every
complete/readable fresh run, diagnose the three behavioral disagreements
and one evidence-only failure, write the durable M4.8 report, checkpoint,
and commit the retained campaign result.

## Phase 08.7 M4.8 standalone validation, analysis, and retained result

The standard installed completeness validator was invoked exactly once
against each of the `17` fresh run directories from the qualified isolated
install. Its outcome agrees with the runner evidence:

```text
return code 0 / completeness pass: 16/17
return code 1 / completeness fail:  1/17
unexpected validator result:        0
```

The sole failure remains M4.3 repeat seed `18311`. Its only failed check is
`console_clean`; final commands zero, final readiness false, clean shutdown
metadata, readable bag, Stage A, one fill, Stage B, collision, forbidden
states/events, and cleanup all pass.

The standard installed analyzer was then invoked exactly once for every
completeness-passing bag, with a per-run `600 s` subprocess bound and
outputs below each run at `analysis/phase07`:

```text
analyzer return code 0:            16/16
analysis complete:                 14/16
analysis partial:                   2/16
analysis failure:                   0/16
recording failure in analyzed bag:  0/16
outputs per analyzed bag:            8 plots, 11 tables
```

The M4.3 `r=1.5, 67.5 deg` analysis is partial because two
`/algorithm_state` gaps exceed `0.150000 s`, invalidating only derived
state durations. The M4.4 radius-1.0 failure is partial because Stage A
never opened; its applicable escape duration, orbit count, and radial
progress are consequently unavailable. The completeness-failed seed-18311
bag was not forced through a weaker analyzer path.

The corrected full tally is:

```text
formal combined pass:                  13/17
behavioral pass, evidence fail:         1/17
behavioral failure:                     3/17
Stage A local recovery:                16/17
exact one-fill cardinality:            16/17
Stage B, all cases:                    14 pass, 2 fail, 1 unavailable
Stage B after completed Stage A:       14/16 pass, 2 fail
collision/forbidden evidence:          17/17 pass
final command zero:                    17/17 pass
cleanup:                               17/17 pass
SQLite quick_check:                    17/17 ok
formal classification agreement:      13/17
behavioral agreement:                  14/17
user-defined most threshold:           PASS (13 >= 9)
```

All `16` completed Stage A paths were direct; none entered
`ESCAPE_ASSIST`. Visible cases were `4/5` formal and `4/5` behavioral.
Headless cases were `9/12` formal and `10/12` behavioral.

The three fresh behavioral disagreements are distinct:

1. M4 visible completed Stage A at simulation time `294.834 s`. Its fixed
   total horizon ended at `361.644 s`, leaving `66.810 s` after recovery.
   It improved from `2.719234 m` to a best `2.270542 m`, then ended at
   `2.311372 m`. No wall, collision, or failsafe stopped it.
2. M4.3 radius-2.0 completed Stage A, used the full `120.020 s` Stage B
   budget, and stopped with a live timeout sample at `1.221840 m`. Its
   final recorded pose after ordered shutdown was `1.213880 m`, only
   `0.013880 m` outside the unchanged gate. This is a retained time-budget
   near miss.
3. M4.4 radius-1.0 stayed in `SEARCH` for the full run and traveled
   `29.129297 m` around the local field. It emitted candidates at
   `73.1 s` and `124.8 s` but never the third confirmation, so no fill or
   Stage A was produced. The original same-seed run confirmed at
   `127.6 s`; the fresh failure is detector-to-supervisor confirmation
   sensitivity, before recovery or global guidance.

The seed-18311 evidence-only failure is also bounded. The controller
reported activation success, but the controller manager failed to deliver
the switch-service response. Thirty seconds later the spawner retried an
already-active controller and exited `1`. Motion preflight and the full
behavior then passed. The strict `console_clean` failure is retained.

The durable report is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_8_success_reproduction_report.md
SHA-256
f385abf9030ad1f1cc2c26850cfda7b860da3a74df632a72b167ea306ee9c63a
```

Its manifest-order result/completeness/analysis hash-inventory digest is:

```text
4445e970ba77b879798cfda841941442dcfbc6c48c108a92bb5e6480db861f73
```

No matching Gazebo, scenario runner, recorder, rosbag recorder, validator,
or analyzer process remains. No retry, parameter correction, three-light
case, Phase 09 action, physical command, or hardware action occurred.

The physical boundary is explicit and unchanged: automatic global-distance
termination is simulation-only. Physical testing must have no automatic
`1.20 m`, `1.00 m`, or other proximity stop. The robot continues until the
operator judges it close enough and presses `Ctrl+C`; that signal must use
the ordered readiness-false, stop, final-zero, recording-finalization, and
scoped-cleanup path.

Final static validation passed:

```text
validate_phase_context.sh 08 implement: pass
git diff --check:                         pass
retained-evidence verifier:
  runs/formal/complete/analyzed:          17 / 13 / 16 / 16
  inventory digest:                      pass
  report digest/status binding:          pass
physical auto-stop manifest predicate:   false, pass
matching active runtime processes:       none, pass
```

The first small report/status semantic smoke asserted the literal lowercase
word `manual` before that word appeared in the report and stopped on that
assertion. The physical policy was already explicit, but the report wording
was made even more direct as “manual operator control,” its hash was
updated above, and the complete corrected verifier passed. This was a
documentation-check assertion, not a simulation, validator, analyzer, or
product failure.

## Current milestone

**Phase 08.7 M4.8 — RETAINED RESULT QUALIFIED /
17/17 EXECUTED EXACTLY ONCE / 13 FORMAL PASS /
14 BEHAVIORAL PASS / USER-DEFINED MOST THRESHOLD PASS /
17 SQLITE, FINAL-ZERO, AND CLEANUP PASS /
DURABLE REPORT COMPLETE / CHECKPOINT AND COMMIT PENDING.**

### Next criterion

Run final context/diff validation, write the Phase 08 material-boundary
checkpoint, inspect the exact diff, and commit the retained M4.8 result.
The separately requested whole-Phase-08 report remains outside M4.8 and
must start from this committed boundary.

## Phase 08.7 M4.8 committed closeout

The complete retained campaign result, durable report, live evidence
record, and material-boundary checkpoint were committed at:

```text
7dbdd6606a3d775318d8c741a1fe83de8bd3808a
phase 08.7: retain successful-run reproduction
```

Immediately after that commit the worktree was clean, the branch was
`100` commits ahead of its tracked remote,
`validate_phase_context.sh 08 implement` passed, the report remained:

```text
f385abf9030ad1f1cc2c26850cfda7b860da3a74df632a72b167ea306ee9c63a
```

and no Gazebo, scenario runner, recorder, validator, or analyzer process
was active.

M4.8 is closed. Its result is `13/17` formal and `14/17` behavioral passes
from the retrospective known-success population, with all `17` SQLite,
final-zero, and cleanup checks passing. The result clears only the
user-defined “most pass again” observation. It does not reopen a failed
suite, declare broad simulation readiness, or authorize three-light or
physical execution.

For physical work, the controlling requirement remains manual termination:
no automatic global-proximity stop is authorized, and the operator presses
`Ctrl+C` when the robot is sufficiently close.

## Current milestone

**Phase 08.7 M4.8 — CLOSED AND COMMITTED /
17 EXACT REPRODUCTIONS RETAINED / 13 FORMAL PASS /
14 BEHAVIORAL PASS / MOST THRESHOLD PASS /
PHYSICAL AUTO-DISTANCE STOP PROHIBITED.**

### Next criterion

Begin the separately scoped whole-Phase-08 report only when requested.
Reconstruct it from the current code, Git history, plans, status,
checkpoints, handoffs, and retained validation artifacts. Do not infer
Phase 09 implementation, three-light execution, or physical-hardware
authorization from this M4.8 closeout.

## Whole-Phase-08 final report and handoff

The user requested the final report for the entirety of Phase 08. The report
was reconstructed from the current implementation, Git history, every
Phase 08 Plan, the version-specific handoffs, this live status, the current
checkpoint, retained validation reports, and the final M4.8 evidence. No
Gazebo, ROS scenario, analyzer, physical command, or hardware process was
started.

Authoritative closeout documents:

```text
docs/codex/gesc_gaussian/validation/phase_08_final_report.md
SHA-256
a884577d7d844f24b554f461543e15c9a2aa527f61e41f1c18141cea6a3a2306

docs/codex/gesc_gaussian/handoffs/phase_08_final_handoff.md
SHA-256
a082e23b58345eb7d418822b409824122ffc185530d7285e6e16c6defb7f5727
```

The terminal whole-phase disposition is:

```text
Phase 08 development/diagnostic work:       CLOSED
broad simulation-ready objective:           FAILED
70-unique-case acceptance denominator:      NOT RUN
simulation-ready tag:                        NOT CREATED
three-light readiness:                       NOT ESTABLISHED
physical hardware during Phase 08:           NOT RUN
M4.8 known-success reproduction:             13/17 formal
                                               14/17 behavioral
```

The report records the complete chronology:

- v1's `81` training runs, failed 12-run exposed holdout, and safely stopped
  partial 519-run pass;
- v2's failed `1/10` mandatory activation gate;
- Phase 08.1's detector/fill/verification/readiness corrections and mixed
  two-probe diagnosis;
- Phase 08.2's passing recenter-only development probe;
- v3's contact, behavioral, executor, and recorder-finalization failures;
- V4's safe direct-goal but unexercised robustness branch;
- V5's `0/8` blocker-encounter result despite four complete recovery paths;
- V6's selected H25 ratio, `1/3` full-record repeats, and `2/3` first-recovery
  episodes;
- Phase 08.7 M1-M4.7's shifted geometry, known topology, staged contract,
  evidence corrections, successful probes, failed suites, and bounded
  post-recovery diagnoses;
- M4.8's final `13/17` formal, `14/17` behavioral, `17/17` final-zero,
  cleanup, collision/forbidden, and SQLite result.

The final Phase 09 proposal is deliberately narrow and non-authorizing:
inventory and plan a two-light physical commissioning path around the
simulator-relative `400/1600` or measured `1:4` response condition, starting
with the radius-1.5, 45-degree layout and retaining the 67.5-degree layout as
a secondary case. Three-light work remains deferred.

The physical termination policy is explicit:

```text
automatic physical distance stop: PROHIBITED
global distance:                  DIAGNOSTIC ONLY
termination:                      OPERATOR CTRL+C WHEN SUFFICIENTLY CLOSE
shutdown:                         readiness false -> stop -> final zero
                                  -> bag finalization -> scoped cleanup
```

Navigation was updated so `START_HERE.md` and `implementation_sequence.md`
point to the final report/handoff instead of the obsolete Phase 08.2/v3
active-subphase boundary.

Initial closeout document checks:

```text
report local Markdown links:     20 checked, 0 missing
key terminal-claim assertions:   pass
git diff --check:                pass
```

## Current milestone

**PHASE 08 WHOLE-PHASE REPORT — WRITTEN /
BROAD SIMULATION-READY OBJECTIVE FAILED /
FINAL HANDOFF WRITTEN /
CLOSEOUT VALIDATION AND CHECKPOINT PENDING.**

### Next criterion

Run the final source-to-report consistency audit, context validation, document
link/parse checks, `git diff --check`, and historical-hash spot checks. Then
write the material Phase 08 checkpoint, inspect the complete diff, and commit
the closeout documents. Do not start Phase 09 implementation, Gazebo,
three-light execution, or physical hardware.

## Whole-Phase-08 report qualification

The closeout documents passed the complete non-runtime qualification:

```text
validate_phase_context.sh 08 implement:
  PASS; active subphase phase_08_7_plan.md

validate_required_docs.sh:
  PASS; all required Phase 00 audit documents exist

report Markdown links:
  20 checked, 0 missing

source-to-report consistency:
  PASS for v1, v2, 08.1, 08.2, v3, V4, V5, V6, and M4.8
  PASS for machine-readable V6 selected_case=H25, selected_ratio=0.25
  PASS for final report terminal values and manual Ctrl+C policy

historical hash spot checks:
  M4.8 report:
    f385abf9030ad1f1cc2c26850cfda7b860da3a74df632a72b167ea306ee9c63a
  M1 immutability manifest:
    34f20a3bd66893be295c44f860e85645f6c9c182d82a658ee47bc785f3b42dba
  historical world:
    8ecc1a231efec24401d74fef3cd5139d48c6029f88e71d044cefdf2fd14c5bef
  shifted world:
    88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf

retained external root audit:
  16 major roots checked, 0 missing

matching Gazebo/scenario/recorder/validator/analyzer processes:
  none

matching Phase 08 or simulation-ready tag:
  none

tool Python compilation:
  PASS

git diff --check:
  PASS
```

The first two ad hoc consistency-smoke invocations used overly literal
assertions: one looked for `400` in the prose V6 report instead of the
machine-readable selection file, and the next looked for the exact uppercase
phrase `OPERATOR CTRL+C` rather than the report's explicit sentence
`operator presses Ctrl+C`. Both stopped only on those test-script assertions.
The corrected source-aware check above passed completely. These were
closeout-test assertion mistakes, not documentation-content, algorithm, ROS,
Gazebo, evidence, or product failures.

No source, launch, scenario, algorithm, test, world, retained report, or
external evidence artifact changed during report qualification.

## Current milestone

**PHASE 08 WHOLE-PHASE REPORT — QUALIFIED /
FINAL HANDOFF COMPLETE /
BROAD SIMULATION-READY OBJECTIVE FAILED /
MATERIAL CHECKPOINT AND COMMIT PENDING.**

### Next criterion

Run `checkpoint_phase.sh 08`, inspect the resulting checkpoint and complete
six-file closeout diff, rerun context and whitespace checks, and commit the
report/handoff/navigation/status/checkpoint boundary. Do not run Gazebo,
Phase 09 implementation, three-light simulation, or physical hardware.

## Whole-Phase-08 committed boundary

The qualified whole-phase report, final handoff, navigation updates, live
status evidence, and material checkpoint were committed at:

```text
b1d1e7c7a619f308765e1d913ed1b891610df2c3
phase 08: publish final development report
```

Immediately after that commit:

```text
worktree:                         clean
branch:                           feature/gesc-gaussian-robustness-v1
ahead of tracked remote:          102 commits
validate_phase_context.sh 08:     pass
final report SHA-256:
  a884577d7d844f24b554f461543e15c9a2aa527f61e41f1c18141cea6a3a2306
final handoff SHA-256:
  a082e23b58345eb7d418822b409824122ffc185530d7285e6e16c6defb7f5727
```

The report commit does not create a simulation-ready tag, reopen any failed
experiment, authorize three-light execution, begin Phase 09 implementation,
or authorize physical hardware. It closes Phase 08 with the broad
simulation-ready objective failed and the narrower M4.8 known-success
reproduction retained.

## Current milestone

**PHASE 08 — CLOSED /
FINAL REPORT AND HANDOFF COMMITTED AT B1D1E7C /
BROAD SIMULATION-READY OBJECTIVE FAILED /
PHYSICAL AUTO-DISTANCE STOP PROHIBITED.**

### Next criterion

Wait for a separate user request to plan Phase 09. Begin with current physical
interface inventory and a two-light `1:4` measured-response commissioning
proposal. Planning does not authorize hardware motion. Preserve manual
operator `Ctrl+C`, final-zero, recording-finalization, and scoped-cleanup
requirements; do not infer three-light readiness.

## Phase 08.8 approved implementation boundary — 2026-07-30

Phase 08.8 is a separately versioned development and reproducibility iteration.
It does not reopen, overwrite, or add to any Phase 08 v1-v6, Phase 08.7, or
whole-phase acceptance denominator.

User authority:

```text
Phase 08.8 plan:             approved
bounded Plan/code fixes:     authorized
Gazebo after M1-M2 gate:     authorized
physical hardware:           not authorized
```

The approved Plan is:

```text
docs/codex/gesc_gaussian/plans/phase_08_8_plan.md
```

The user requested repeatable two-source behavior across differing positions
and intensities. The Plan now preserves the frozen primary/secondary `1:4`
qualification first, then permits a versioned broadening matrix within the
physically observable distinct-extrema envelope. Coincident, zero-strength, or
aggregate single-basin declarations cannot truthfully be counted as
local-escape passes.

Implementation preflight:

```text
branch:
  feature/gesc-gaussian-robustness-v1
starting HEAD:
  bc25fef phase 08: close final report boundary
starting tracked state:
  ahead 103
starting worktree:
  only the untracked Phase 08.8 Plan
matching Gazebo/scenario/recorder processes:
  none
tools/validate_phase_context.sh 08 implement:
  PASS
active subphase plan:
  docs/codex/gesc_gaussian/plans/phase_08_8_plan.md
```

No Gazebo process may start until the counted-source policy, detector,
open-field recovery wiring, focused regressions, isolated build, installed
launch instantiation, scenario dry-runs, validation record, and material
checkpoint all qualify.

### Current milestone

**PHASE 08.8 M1 — IN PROGRESS / NO GAZEBO AUTHORIZED BEFORE M1-M2 GATE.**

### Next criterion

Implement the selectable counted-source candidate policy and raw-cost
rotation summary in the existing supervisor owner. Pass its ROS-independent
two-source, three-source, invalid-input, revisit, fill-cardinality, and
historical-default tests without weakening existing behavior.

## Phase 08.8 M1-M2 no-Gazebo qualification — 2026-07-30

M1 and M2 implementation is complete and technically qualified. The durable
records are:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_baseline_audit.md
  phase_08_8_no_gazebo_qualification.md
```

Implemented selectable behavior:

```text
known total source count
-> qualified-dwell candidate confirmation
-> two complete-rotation raw-cost minima
-> median/MAD interval
-> exactly N-1 distinct typed fills
-> direct Gaussian repulse to SEARCH
-> active-fill revisit suppression
-> strict terminal comparison against every filled candidate
-> ranked GOAL_REACHED
```

Historical defaults remain absolute source-score classification,
crossing-count confirmation, enabled operating bounds, and their existing
recenter/affine selections. The new profile is explicit and defaults off.

The fixed Phase 08.8 scenarios resolve through schema version 8 under the
installed names:

```text
phase08_v8_primary_visible_probe.yaml:     1 GUI case
phase08_v8_primary_repeats.yaml:          10 headless cases
phase08_v8_secondary_visible_probe.yaml:   1 GUI case
phase08_v8_secondary_repeats.yaml:         5 headless cases
```

All 17 installed dry-run expansions are supported. They use two positive
direct sources, known count two, one fill, empty world, no contacts, no
operating bounds, no recenter, no affine bias, no recoverable navigation, and
no post-recovery guidance. The dry-run root remains absent.

Final no-Gazebo evidence:

```text
focused controller/detector:
  180 passed in 7.32 s

scenario/schema/Phase 08 validation:
  380 passed, 1 Gazebo-only skip in 92.54 s

candidate analysis:
  13 passed in 0.75 s

broad ROS-independent functional:
  735 passed, 2 Gazebo-only skips in 134.05 s

fatal changed-file lint:
  PASS

changed-Python compilation:
  PASS

fresh isolated build:
  3 packages passed in 13.0 s

source/install parity:
  12/12

installed launch:
  show-args PASS
  exact print-description PASS
  detector construction PASS
  supervisor construction PASS

validate_phase_context.sh 08 implement:
  PASS

git diff --check:
  PASS
```

The repository-wide style test files remain non-gating legacy debt:
14,397 flake8 and 1,842 pep257 findings outside this behavioral change.
Fatal syntax/name errors in changed files are zero.

The runner's `0.50 m` terminal check is evaluator-only and causally follows a
valid controller-ranked goal. The supervisor and physical path receive no
global coordinate or distance stop. Physical termination remains manual
operator `Ctrl+C`.

No Gazebo, scenario execution, recorder, rosbag recorder, analyzer, Phase 09,
three-light run, or physical process has occurred. No tracked historical
scenario or world changed. V6 remains preserved.

## Current milestone

**PHASE 08.8 M1-M2 — QUALIFIED /
MATERIAL CHECKPOINT AND COMMIT PENDING /
GAZEBO STILL PROHIBITED.**

## Next criterion

Run `checkpoint_phase.sh 08`, inspect the checkpoint plus complete M1-M2 diff,
rerun context/whitespace checks, and create the authorized bounded commit.
Only then dispatch the primary visible probe exactly once.

## Phase 08.8 M1-M2 committed boundary — 2026-07-30

The qualified counted-source/open-field implementation, tests, fixed
scenarios, baseline audit, no-Gazebo record, live status, and material
checkpoint were committed at:

```text
78b0f4d phase 08.8: qualify counted-source open-field profile
```

Post-commit verification:

```text
branch:
  feature/gesc-gaussian-robustness-v1
tracked remote:
  ahead 104
worktree:
  clean
validate_phase_context.sh 08 implement:
  PASS
matching Gazebo/scenario/recorder/analyzer processes:
  none
```

This satisfies the explicit M1-M2 prerequisite for Gazebo. It does not imply a
behavioral simulation pass.

## Current milestone

**PHASE 08.8 M3 — AUTHORIZED FOR ONE VISIBLE PRIMARY DISPATCH.**

## Next criterion

Execute `phase08_v8_primary_visible_probe.yaml` once from the qualified
installed graph with GUI enabled. Retain the complete outcome, do not retry the
same fixed version, run the authoritative validator/analyzer if recording is
complete, checkpoint the result, and stop later dispatch if any M3 gate fails.

## Phase 08.8 M3 fixed primary visible probe — 2026-07-30

**FIXED EXPERIMENT FAIL / INFRASTRUCTURE COMPLETE / RETAINED.**

The one authorized visible execution of the installed
`phase08_v8_primary_visible_probe.yaml` was dispatched exactly once. The
scenario returned exit 1 after the live Stage A monitor reached its fixed
`360.0 s` budget without observing the required direct recovery path.

Retained suite summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_primary_probe/scenario_summaries/20260731T040555626244Z_phase08_v8_primary_visible_probe.yaml
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_primary_probe/2026-07-31/20260731T040556569481Z_simulation_phase08_v8_primary_visible_probe-v8_primary_probe_r1p5_a45_h25_18801-robust_gaus_5fa57e59
```

Infrastructure remained healthy:

```text
record process:
  return_code 0
  timed_out false
recording complete:
  true
authoritative completeness:
  PASS
cleanup:
  PASS
remaining nodes/processes:
  none
analysis:
  command exit 0
  partial only because behavior failed
  analysis failures none
```

Behavioral result:

```text
observed path:
  SEARCH
  -> VERIFY_EXTREMUM
  -> DESIGN_OR_MERGE_FILL
  -> ESCAPE_REPULSE
  -> DESIGN_OR_MERGE_FILL
  -> ESCAPE_ASSIST
  -> SEARCH
  -> VERIFY_EXTREMUM
  -> SEARCH
  -> VERIFY_EXTREMUM
  -> SEARCH

required v8 recovery path:
  SEARCH
  -> VERIFY_EXTREMUM
  -> DESIGN_OR_MERGE_FILL
  -> ESCAPE_REPULSE
  -> SEARCH

fill cardinality:
  PASS, exactly one created/active cluster
Stage A:
  FAIL
Stage B:
  not started / FAIL
controller ranked goal:
  false
terminal state:
  SEARCH
terminal position:
  (1.255092, 1.140857) m
distance to declared evaluator global:
  3.256557 m
```

The first confirmed candidate and fill were correct. Its complete-rotation raw
estimate was `-2.339437`, MAD `0.506357`, uncertainty `1.519071`, and interval
`[-3.858508, -0.820366]`. The fill was associated `0.273508 m` from the
declared local and `0.166811 m` from the convergence point.

The escape stalled, redesigned/merged the same fill, entered the legacy assist
state, and achieved only `0.213563 m` of sustained radial progress. It then met
the small historical exit radius and returned to ordinary search while still
close enough to fall back into the same local basin. Later confirmations were
correctly rejected as active-fill revisits; no false candidate two or false
global decision occurred.

The bounded diagnosis and all plot/table paths are recorded in:

```text
docs/codex/gesc_gaussian/validation/phase_08_8_primary_probe.md
```

The failed fixed v8 input is closed. It will not be retried, mutated, or
included as a pass. Primary repeats, secondary runs, and broader dispatch are
stopped at the M3 gate.

## Current milestone

**PHASE 08.8 M3 — FIXED V8 PROBE FAILED /
FAILURE EVIDENCE CHECKPOINTED / COMMIT PENDING /
NO FURTHER GAZEBO AUTHORIZED UNTIL A VERSIONED CORRECTION QUALIFIES.**

## Next criterion

Commit the checkpointed fixed M3 failure evidence. Then amend the Phase 08.8
Plan for a new, opt-in open-field escape-assist version; qualify its state
semantics, supervisor command ownership, schema, validator, historical
defaults, launch graph, build, and dry-run expansion without Gazebo. Only a
successful material checkpoint and commit may authorize one new visible probe.

## Phase 08.8 M3.1 versioned correction — 2026-07-30

The fixed v8 failure was committed at:

```text
8ebb9cd phase 08.8: retain failed primary probe
```

The approved Phase 08.8 Plan now contains a separately versioned M3.1
correction. It does not mutate or retry the failed v8 input.

Implemented opt-in behavior:

```text
ESCAPE_REPULSE measured stall
-> ESCAPE_ASSIST without fill redesign
-> radial outward direction from frozen fill center and current odometry
-> existing bounded supervisor/controller command arbitration
-> Gaussian retained, affine disabled
-> enlarged finite exit boundary and hold
-> supervisor zero
-> ordinary GESC SEARCH
```

Defaults and historical behavior:

```text
open_field_escape_assist_enabled:
  false by default
historical ESCAPE_ASSIST weights:
  (0, 1, 1), unchanged
v8.1 opt-in weights:
  (0, 1, 0)
new node/topic/publisher/planner:
  none
controller evaluator geometry:
  none
```

The four new fixed scenario definitions resolve:

```text
phase08_v8_1_primary_visible_probe.yaml:     1 GUI case, seed 18901
phase08_v8_1_primary_repeats.yaml:          10 headless, 18911..18920
phase08_v8_1_secondary_visible_probe.yaml:   1 GUI case, seed 18951
phase08_v8_1_secondary_repeats.yaml:         5 headless, 18961..18965
```

They require:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD

required:
  ESCAPE_STALLED
forbidden:
  FILL_MERGED
  FILL_SUPERSEDED
  RECENTER
  TIMEOUT
  FAILSAFE
```

Final no-Gazebo qualification:

```text
focused controller/detector:
  188 passed in 7.11 s

scenario/schema/Phase 08 validation:
  386 passed, 1 Gazebo-only skip in 94.39 s

candidate analysis:
  13 passed in 0.79 s

broad ROS-independent functional:
  749 passed, 2 Gazebo-only skips in 133.87 s

fatal changed-file lint:
  PASS

changed-Python compilation:
  PASS

fresh isolated build:
  3 packages passed in 12.1 s

source/install parity:
  9/9

installed launch:
  show-args PASS
  exact print-description PASS
  supervisor construction PASS
  Gaussian fill exit-sigma construction PASS

installed dry-runs:
  1 + 10 + 1 + 5 resolved
  0 unsupported
  no campaign root created

validate_phase_context.sh 08 implement:
  PASS

git diff --check:
  PASS
```

The durable qualification record is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m3_1_no_gazebo_qualification.md
```

No Gazebo or physical process occurred during correction qualification. V6,
all historical scenarios, the failed v8 case, physical manual `Ctrl+C`
termination, and controller/evaluator separation remain preserved.

## Current milestone

**PHASE 08.8 M3.1 — NO-GAZEBO QUALIFIED /
MATERIAL CHECKPOINT AND COMMIT PENDING /
GAZEBO STILL PROHIBITED.**

## Next criterion

Run the Phase 08 material checkpoint, inspect the complete M3.1 diff, rerun
context and whitespace checks, and commit the versioned correction. Only then
execute `phase08_v8_1_primary_visible_probe.yaml` once from
`/tmp/phase08_8_1_release_qual/install` with Gazebo GUI enabled.

## Phase 08.8 M3.1 material checkpoint — 2026-07-30

The qualified v8.1 correction received the required precommit material
checkpoint:

```text
docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt

generated:
  2026-07-31T04:59:36+00:00
base HEAD:
  8ebb9cde00901d392357eb13b6be045d9be33c51
active subphase plan:
  docs/codex/gesc_gaussian/plans/phase_08_8_plan.md
diff check:
  PASS
```

The checkpoint captures the complete implementation and qualification
boundary before commit. No Gazebo, scenario, recording, analyzer, or physical
process was started while creating it.

## Current milestone

**PHASE 08.8 M3.1 — NO-GAZEBO QUALIFIED AND CHECKPOINTED /
COMMIT PENDING /
GAZEBO STILL PROHIBITED.**

## Next criterion

Regenerate the checkpoint so it includes this checkpoint-status update, rerun
the context and whitespace checks, inspect the final commit scope, and create
the authorized bounded commit. Only then execute the fixed v8.1 primary
visible probe exactly once.

## Phase 08.8 M3.1 committed dispatch boundary — 2026-07-30

The qualified, checkpointed v8.1 correction was committed at:

```text
4bdaba8 phase 08.8: qualify outward escape assist
```

Post-commit verification:

```text
branch:
  feature/gesc-gaussian-robustness-v1
tracked remote:
  ahead 106
worktree:
  clean
validate_phase_context.sh 08 implement:
  PASS
matching Gazebo/scenario/recorder/analyzer processes:
  none
```

This authorizes exactly one installed visible execution of
`phase08_v8_1_primary_visible_probe.yaml`. It does not authorize a retry of
v8 or v8.1, primary repeats, secondary dispatch, or a broader matrix unless
the preceding fixed gate passes.

## Current milestone

**PHASE 08.8 M3.1 — AUTHORIZED FOR ONE FIXED V8.1 PRIMARY VISIBLE
DISPATCH.**

## Next criterion

Execute the installed v8.1 primary visible probe exactly once. Retain its
complete recording, authoritative validation, analysis, plots, and cleanup
evidence. Stop later dispatch if any fixed behavioral, evidence, final-zero,
or cleanup gate fails.

## Phase 08.8 M3.1 fixed v8.1 primary visible probe — 2026-07-30

**FIXED EXPERIMENT FAIL / INFRASTRUCTURE COMPLETE / STAGE A PASS /
RAW-CANDIDATE CHARACTERIZATION FAIL / RETAINED.**

The one authorized installed execution of
`phase08_v8_1_primary_visible_probe.yaml`, seed `18901`, ran once with the
Gazebo GUI. It will not be retried or changed in place.

Retained summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_1_primary_probe/scenario_summaries/20260731T050129680474Z_phase08_v8_1_primary_visible_probe.yaml
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_1_primary_probe/2026-07-31/20260731T050130632538Z_simulation_phase08_v8_1_primary_visible_probe-v8_1_primary_probe_r1p5_a45_h25_18901-robust__c2e42fbd
```

Infrastructure:

```text
record process:
  return_code 0
  timed_out false
recording complete:
  true
authoritative completeness:
  PASS
final-zero:
  PASS
cleanup:
  PASS
remaining nodes/processes:
  none
analyze_run:
  exit 0
  partial only because behavior failed
  analysis failures none
```

Behavior:

```text
Stage A assisted local recovery:
  PASS at simulation time 221.128 s
fill cardinality:
  PASS, exactly one cluster
required ESCAPE_STALLED:
  observed
ESCAPE_ASSIST -> SEARCH:
  PASS, stable assisted escape exit
fill merge/supersession:
  none
failsafe/timeout event:
  none
terminal physical distance to evaluator global:
  0.155960 m
controller-ranked goal:
  FAIL
ranked-goal-gated Stage B:
  FAIL
terminal state:
  SEARCH
```

The terminal comparison was rejected:

```text
retained local estimate:
  -2.845372822
post-confirmation second estimate:
  -0.021174297 +/- 0.000304351
decision:
  counted candidate not strictly stronger; resume search
```

The bag proves the actual raw-field ordering was available:

```text
strongest repeated local-basin raw cost:
  -2.846198587
strongest repeated global-basin raw cost:
  -3.837209302
global source score:
  1.0
```

The estimator reset its raw rotation window only after the convergence
confirmation. It discarded the stronger repeated global-basin samples that
preceded the event and characterized only a later weak directional slice.
This is a detector-to-candidate-estimator timing defect, not an escape,
topology, sign, wall, collision, recorder, or cleanup failure.

Complete diagnosis and all plot/table paths:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m3_1_primary_probe.md
```

The v8.1 primary repeats, secondary cases, and broader matrix were not
dispatched. No physical or three-light process occurred.

## Phase 08.8 M3.2 versioned correction boundary — 2026-07-30

The approved Plan now contains a new default-off, separately versioned v8.2
correction. It retains six complete `SEARCH`-epoch raw rotation minima before
confirmation, freezes them at `VERIFY_EXTREMUM`, combines them with three
verification rotations, and applies the unchanged median/MAD strict
comparison to the three most negative repeated minima.

This bounded memory is raw-signal history only. It uses no route, pose,
declared source position, source role, Vicon input, evaluator proximity, room
geometry, waypoint, or planner. A zero default preserves v8.1 and all
historical behavior.

Fresh v8.2 scenario identities use seeds `19001`, `19011..19020`, `19051`, and
`19061..19065`. No v8.2 Gazebo process is authorized until the correction,
tests, fresh installed graph, all seventeen dry-run expansions, validation
record, material checkpoint, and commit qualify.

## Current milestone

**PHASE 08.8 M3.1 — FIXED V8.1 PROBE FAILED AND RETAINED /
M3.2 PLAN AMENDED /
FAILURE EVIDENCE CHECKPOINT AND COMMIT PENDING /
NO FURTHER GAZEBO AUTHORIZED.**

## Next criterion

Checkpoint and commit the complete v8.1 failure plus M3.2 amendment. Then
implement and qualify the default-off pretrigger raw-rotation history without
Gazebo. Only a successful M3.2 checkpoint and commit can authorize one new
visible v8.2 probe.

## Phase 08.8 M3.1 failure checkpoint — 2026-07-30

The fixed v8.1 failure, complete retained-run diagnosis, plots/tables, and
separately versioned M3.2 amendment received the required material checkpoint
against base HEAD `4bdaba8`.

## Current milestone

**PHASE 08.8 M3.1 — FIXED FAILURE RETAINED AND CHECKPOINTED /
M3.2 AMENDMENT RECORDED /
COMMIT PENDING /
GAZEBO PROHIBITED.**

## Next criterion

Regenerate the checkpoint with this status, rerun context and whitespace
checks, and commit the bounded evidence/amendment. Then begin M3.2
implementation without Gazebo.

## Phase 08.8 M3.1 failure committed boundary — 2026-07-30

The retained v8.1 failure, complete diagnosis, plot/table index, M3.2 Plan
amendment, status, and material checkpoint were committed at:

```text
c11ad74 phase 08.8: retain failed v8.1 primary probe
```

Post-commit checks passed with a clean worktree, complete Phase 08
implementation context, and no matching Gazebo or scenario process. That
commit authorized M3.2 implementation without Gazebo; it did not authorize a
v8.1 retry or any v8.2 dispatch.

## Phase 08.8 M3.2 no-Gazebo qualification — 2026-07-30

The separately versioned, default-off pretrigger raw-cost correction is
implemented and qualified.

Implementation:

```text
new parameter:
  candidate_cost_pretrigger_rotations
default:
  0
v8.2 value:
  6
required repeated rotations:
  3
bounded raw history:
  18.0 s
ranking:
  unchanged median/MAD strict nonoverlap
```

Only complete `SEARCH`-epoch raw-cost rotation minima are retained. The latest
six freeze on `SEARCH -> VERIFY_EXTREMUM`, the normal three verification
rotations must still complete, and the three most-negative repeated minima
from the pooled evidence are ranked. All history resets for the next search
epoch. No modified cost, route, pose, source coordinate, role, evaluator
geometry, Vicon value, or planner enters the estimator.

Final no-Gazebo evidence:

```text
focused controller/detector/core/legacy:
  199 passed in 7.24 s
  /tmp/phase08_8_2_focused_final.xml
  b11b2c7e9fc2d7b53480140be0a33ca11d667aa145ffaee4eb60b6e6951f7125

scenario/schema/Phase 08 validator:
  395 passed, 1 skipped in 96.17 s
  /tmp/phase08_8_2_scenario.xml
  dcd8042885b2a1dd77fb0b045dc05a89054e740cbc4ff4b67ba7086e4a876dc6

analyzer/plots:
  18 passed in 6.29 s
  /tmp/phase08_8_2_analysis.xml
  629d0481f36c7a3adf2ec568c1fd1cc63c6fb5ec3404a2cadc8233632eabc3a3

broad ROS-independent:
  769 passed, 2 skipped in 134.10 s
  /tmp/phase08_8_2_broad.xml
  2083878c4169171926e310a4e8b36bc0c88dd2d089b6ec63903275d1500634e7
```

The skips are the unchanged environment-conditional Gazebo integrations.
Fatal changed-Python lint, compilation, launch XML, all four YAML files,
`git diff --check`, and Phase 08 implementation context pass.

The fresh isolated build at `/tmp/phase08_8_2_release_qual` finished all three
packages in `12.0 s`. Source/install parity passes for all `8/8` final runtime
owners. Both a default and opted-in installed supervisor constructed without
startup error under bounded five-second checks.

Installed nonexecuting launch evidence:

```text
/tmp/phase08_8_2_release_show_args.txt
  ed13d87d3dea6005b1697a17136f21287823cf9204fe7642d1696fbaaa0499b0

/tmp/phase08_8_2_release_launch_description.txt
  c373685f6c729df3170e110a88a6d89cec0350896a640e50e0f0503328ffd555
```

All seventeen installed dry-run cases resolve with zero unsupported cases:

```text
primary visible:
  1 / 0
  f5a9805dd44494c6871e3a01a4edb34e0d8a48cdb0577da50f1ce8b5700347e5
primary repeats:
  10 / 0
  1ed3f5a504e0f7d538e7948326aa43e4c791c578f4dce3ee10530d8f6b27a148
secondary visible:
  1 / 0
  f39b69aa06b662ea7f4a9e853afbc438e187da17ec75344ae60693754a315d2a
secondary repeats:
  5 / 0
  fae1e60b0c1593d95049977afd0337b03137c22f179c340436d638909e3f85c5
```

Dry resolution created no campaign root. Historical world and V6 selection
hashes remain exact. The failed v8 and v8.1 evidence remains failed and
unchanged.

Durable qualification:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m3_2_no_gazebo_qualification.md
```

No Gazebo, scenario recording, analyzer, or physical process occurred during
M3.2 qualification.

## Current milestone

**PHASE 08.8 M3.2 — NO-GAZEBO QUALIFIED /
MATERIAL CHECKPOINT AND COMMIT PENDING /
GAZEBO STILL PROHIBITED.**

## Next criterion

Run the Phase 08 material checkpoint, include this status and the durable M3.2
qualification, inspect the final diff, and create the authorized bounded
commit. Only then execute the installed v8.2 primary visible probe, seed
`19001`, exactly once.

## Phase 08.8 M3.2 material checkpoint — 2026-07-30

The qualified M3.2 implementation and its complete no-Gazebo validation record
received the required precommit material checkpoint:

```text
docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt

generated:
  2026-07-31T05:40:49+00:00
base HEAD:
  c11ad74a1b8000d802c52b04dd53c7579fd13a55
active subphase plan:
  docs/codex/gesc_gaussian/plans/phase_08_8_plan.md
diff check:
  PASS
```

No Gazebo, scenario, recording, analyzer, or physical process ran while
creating the checkpoint.

## Current milestone

**PHASE 08.8 M3.2 — NO-GAZEBO QUALIFIED AND CHECKPOINTED /
COMMIT PENDING /
GAZEBO STILL PROHIBITED.**

## Next criterion

Regenerate the checkpoint so it includes this status update, rerun context and
whitespace checks, inspect the complete commit scope, and create the authorized
bounded commit. Only the committed boundary authorizes the one fixed v8.2
visible probe.

## Phase 08.8 M3.2 committed dispatch boundary — 2026-07-30

The qualified, checkpointed v8.2 correction was committed at:

```text
e88f2aa phase 08.8: qualify pretrigger raw-cost ranking
```

Post-commit verification:

```text
branch:
  feature/gesc-gaussian-robustness-v1
tracked remote:
  ahead 108
worktree:
  clean
validate_phase_context.sh 08 implement:
  PASS
matching Gazebo/scenario/recorder/analyzer processes:
  none
```

This boundary authorizes exactly one installed visible execution of
`phase08_v8_2_primary_visible_probe.yaml`, seed `19001`. It does not authorize
a retry, the ten primary repeats, either secondary input, a broader matrix, or
physical hardware unless the preceding fixed gate passes.

## Current milestone

**PHASE 08.8 M3.2 — AUTHORIZED FOR ONE FIXED V8.2 PRIMARY VISIBLE
DISPATCH.**

## Next criterion

Commit this post-commit dispatch record, verify a clean worktree and no stale
runtime, and execute the installed v8.2 primary visible probe exactly once.
Retain its recording, authoritative validation, analysis, plots, and cleanup
evidence. Stop all later dispatch if any fixed gate fails.

## Phase 08.8 M3.2 fixed v8.2 primary visible probe — 2026-07-30

**FORMAL PASS / INFRASTRUCTURE COMPLETE / STAGE A PASS / EXACT ONE FILL /
STRICT SECOND-CANDIDATE RAW RANKING PASS / STAGE B PASS / RETAINED.**

The one authorized installed execution of
`phase08_v8_2_primary_visible_probe.yaml`, seed `19001`, ran exactly once with
the Gazebo GUI.

Retained summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_2_primary_probe/
  scenario_summaries/
  20260731T054259986753Z_phase08_v8_2_primary_visible_probe.yaml
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_2_primary_probe/
  2026-07-31/
  20260731T054300954593Z_simulation_phase08_v8_2_primary_visible_probe-v8_2_primary_probe_r1p5_a45_h25_19001-robust__7abc89e2
```

Infrastructure:

```text
record process:
  return code 0
  timed out false
recording complete:
  true
authoritative completeness:
  PASS
final readiness false:
  PASS
final-zero:
  PASS
cleanup:
  PASS
remaining nodes/processes:
  none
analyze_run:
  complete
analysis failures:
  none
```

Behavior:

```text
observed state path:
  SEARCH
  -> VERIFY_EXTREMUM
  -> DESIGN_OR_MERGE_FILL
  -> ESCAPE_REPULSE
  -> ESCAPE_ASSIST
  -> SEARCH
  -> VERIFY_EXTREMUM
  -> GOAL_HOLD

Stage A:
  PASS at simulation time 167.235 s
fill cardinality:
  PASS, exactly one cluster
required ESCAPE_STALLED:
  observed
assisted departure:
  PASS
fill merge/supersession:
  none
failsafe/timeout:
  none
```

Both candidate decisions report six frozen pretrigger rotations, three
verification rotations, nine available rotations, and three selected repeated
minima.

Raw ranking:

```text
local candidate:
  -2.8453728221821186
global candidate:
  -3.8372093023255816
strict separation margin:
  0.9918364801434629
candidate ordinal:
  2 of known total 2
decision:
  GOAL_REACHED
```

The ranked event preceded the first accepted evaluator proximity sample. That
later noninterpolated sample was `0.139463 m` from `(3.5, 3.5)` at simulation
time `289.805 s`. The final retained distance is `0.139441 m`. Stage B passed
within its fixed `180.0 s` post-Stage-A budget.

Complete report and all plot/table paths:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m3_2_primary_probe.md
```

Nine plots were generated under the retained run's
`analysis/phase07/plots/`, including trajectory, candidate ranking, cost,
components, state/events, weights, commands, radial escape, and Gaussian
history.

No primary repeat, secondary case, broader matrix, physical process, or
three-light process has yet been dispatched.

## Current milestone

**PHASE 08.8 M3.2 — FIXED V8.2 PRIMARY VISIBLE PROBE PASSED /
M3.2 EVIDENCE CHECKPOINT AND COMMIT PENDING /
PRIMARY REPEATS NOT YET AUTHORIZED.**

## Next criterion

Checkpoint and commit the complete fixed-probe evidence. Then execute the ten
precommitted primary repeats serially and headlessly from the same isolated
install, stopping dispatch immediately on the first behavioral, evidence,
final-zero, or cleanup failure.

## Phase 08.8 M3.2 visible-pass checkpoint — 2026-07-30

The complete fixed v8.2 visible-probe pass, retained run diagnosis, plot/table
index, and M3.2 gate disposition received the required material checkpoint
against base HEAD `551a626`.

## Current milestone

**PHASE 08.8 M3.2 — FIXED VISIBLE PASS RETAINED AND CHECKPOINTED /
EVIDENCE COMMIT PENDING /
PRIMARY REPEATS NOT YET AUTHORIZED.**

## Next criterion

Regenerate the checkpoint with this status, rerun context and whitespace
checks, and commit the bounded M3.2 pass evidence. Only that clean committed
boundary authorizes M4's sealed ten-run primary gate.

## Phase 08.8 M3.2 pass committed / M4 dispatch boundary — 2026-07-30

The fixed v8.2 visible-probe pass, analysis, plots, status, and material
checkpoint were committed at:

```text
5d1d54b phase 08.8: retain passing v8.2 primary probe
```

Post-commit verification found a clean worktree, complete Phase 08 context,
and no matching Gazebo, scenario, recorder, or analyzer process.

This authorizes the sealed
`phase08_v8_2_primary_repeats.yaml` population only:

```text
seeds:
  19011..19020
execution:
  serial
  headless
retry:
  prohibited
first failure:
  stop remaining dispatch
```

It does not authorize either secondary input, a broader matrix, physical
hardware, or three lights until the preceding gate passes and is retained.

## Current milestone

**PHASE 08.8 M4 — AUTHORIZED FOR THE SEALED TEN-RUN V8.2 PRIMARY GATE.**

## Next criterion

Commit this dispatch record, verify the dedicated M4 run root is absent and
the worktree/runtime are clean, then execute the installed ten-case primary
suite once. Analyze every completed recording and stop immediately on the
first fixed failure.

## Phase 08.8 M4 fixed v8.2 primary repeat gate — 2026-07-30

**FIXED GATE FAILED / 1 OF 10 DISPATCHED / FIRST CASE FAILED STAGE B /
REMAINING 9 NOT DISPATCHED / INFRASTRUCTURE COMPLETE / RETAINED.**

The sealed `phase08_v8_2_primary_repeats.yaml` population began serial,
headless execution from the qualified isolated install. Seed `19011`, the
first fixed case, was executed once and was not retried. It failed Stage B, so
the runner stopped immediately and seeds `19012` through `19020` did not run.

Retained summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_2_primary_repeats/
  scenario_summaries/
  20260731T055403171613Z_phase08_v8_2_primary_repeats.yaml
SHA-256:
  d51eb7887ec39becfaf032c2209745da86179524ea0a7d79ff4bc88635974447
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_2_primary_repeats/
  2026-07-31/
  20260731T055404130734Z_simulation_phase08_v8_2_primary_repeats-v8_2_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_d33decfa
```

Infrastructure and Stage A:

```text
record return code / timed out: 0 / false
recording completeness:         PASS
final readiness false:          PASS
final-zero:                     PASS
cleanup / leftovers:            PASS / none
analysis status:                partial because behavior failed
analysis/recording failures:    none
Stage A:                        PASS at 296.710 s
fill cardinality:               exactly one
escape stalled / assisted:      true / true
escape success:                 true
fill merge/supersession:        none
in-readiness failsafe/timeout:  none
```

Stage B:

```text
fixed budget:                  180.0 s
observed elapsed:              180.030 s
controller GOAL_REACHED:      absent
post-recovery proximity:      absent
final global distance:        3.180001 m
terminal state:               SEARCH
```

After the completed outward escape, the robot returned to the active filled
local. The detector confirmed that same basin twice; the supervisor correctly
rejected both confirmations as active-fill revisits.

The retained local candidate lower bound was `-2.442228` cost units, but the
accepted adaptive fill was only `0.10` high with
`sigma_major=sigma_minor=0.169558 m`. The eight-second orientation-level basin
window collapsed depth to the configured `0.02` minimum, whereas candidate
classification retained repeated complete-rotation minima. This mismatch left
the old raw attraction dominant after the finite assist. Gaussian contribution
was `+0.10`, affine contribution was zero, and no wall, bound, collision,
recenter, or failsafe caused the miss.

Complete report, hashes, diagnosis, and all plot paths:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_primary_repeats.md
```

The fixed v8.2 repeat profile is closed. Its secondary and broad gates remain
undispatched.

## Approved Phase 08.8 M4.1 / v8.3 correction amendment — 2026-07-30

The Plan's approved bounded-correction authority has been applied to a new
v8.3 version. It will pass the already frozen rotation-stable local candidate
interval through a versioned robust fill request and use its conservative
negative raw-cost lower bound as a bounded amplitude floor. The existing
adaptive estimator remains authoritative for center, covariance, association,
and validation.

The v8.3 profile will keep affine, recenter, recoverable navigation, operating
bounds, walls, source coordinates, source roles, Vicon, and evaluator geometry
outside controller motion. It will use an amplitude scale of `1.25`, a finite
amplitude cap of `6.25`, a `0.50 m` sigma floor, and `exit_sigma=2.70`.
Direct repulsion success or the existing finite outward assist will be
accepted; a return to the filled candidate will not.

No v8.3 Gazebo process is authorized until the implementation receives full
no-Gazebo qualification, checkpoint, and committed dispatch boundary.

## Current milestone

**PHASE 08.8 M4 — V8.2 PRIMARY REPEAT GATE CLOSED FAILED /
M4.1 V8.3 CORRECTION PLANNED /
GAZEBO PROHIBITED.**

## Next criterion

Checkpoint and commit the fixed v8.2 failure plus the v8.3 amendment. Then
implement and qualify the default-off candidate-informed fill contract without
Gazebo, checkpoint it, and commit it before authorizing one fresh v8.3 visible
primary probe.

## Phase 08.8 M4 failure/amendment material checkpoint — 2026-07-30

The retained v8.2 fixed-gate failure, complete M4 report, and approved v8.3
correction amendment received the required precommit material checkpoint
against base HEAD `951d5f4`.

No Gazebo, scenario, recorder, analyzer, or physical process ran while
creating this checkpoint.

## Current milestone

**PHASE 08.8 M4 — V8.2 FAILURE AND V8.3 AMENDMENT CHECKPOINTED /
EVIDENCE COMMIT PENDING /
GAZEBO PROHIBITED.**

## Next criterion

Commit the bounded failure/amendment evidence. Then implement and fully
qualify M4.1 without Gazebo before any v8.3 dispatch can be authorized.

## Phase 08.8 M4 failure/amendment commit boundary — 2026-07-30

The retained v8.2 fixed-gate failure, complete diagnosis, and approved v8.3
correction amendment were committed at:

```text
937c6d441bc3a03c1d160d1d40fac9c0b13ec7db
phase 08.8: retain failed primary repeat gate
```

V8.2 remains closed failed. Its undispatched repetitions, secondary suite, and
broad characterization were not run.

## Phase 08.8 M4.1 implementation and no-Gazebo qualification — 2026-07-30

The default-off candidate-informed fill contract is implemented. For a newly
confirmed counted candidate, the supervisor appends the validated
rotation-stable raw-cost estimate, MAD, uncertainty, lower interval bound, and
selected rotation count to a versioned robust fill request. The Gaussian owner
uses only that negative raw-cost lower bound to impose a bounded amplitude
floor. Its existing adaptive center, covariance, anisotropy, association,
validation, escalation, and fill registry remain authoritative.

The fixed v8.3 profile uses:

```text
candidate_informed_fill_enabled:          true
candidate_informed_fill_amplitude_scale: 1.25
gaussian_fill_amplitude_max:              6.25
gaussian_fill_sigma_floor_m:              0.50
gaussian_fill_sigma_ceiling_m:            1.25
gaussian_fill_exit_sigma:                 2.70
```

It retains source count two, one-fill cardinality, `400/1600` direct inputs,
strict raw ranking, open-field motion, no contacts, no operating bounds, no
affine bias, no recenter, no post-recovery guidance, no recoverable navigation,
the evaluator-only `0.50 m` simulation stop, and the physical `Ctrl+C`
contract. No controller receives a source coordinate, source role, global
coordinate, room geometry, Vicon value, or evaluator proximity.

Direct Gaussian repulsion and the existing finite outward fallback are both
valid recovery paths for v8.3. The schema permits exactly those two paths only
for opted-in candidate-informed counted suites. Historical counted profiles
retain their existing single-path and event contracts.

Final source-tree evidence:

```text
focused controller/detector/fill/core/legacy:
  213 passed in 7.34 s
  /tmp/phase08_8_3_focused.xml
  a5585325a1caca01bc3f0974fc83de872df27a2bc17441e9e5a683a466ed238e

scenario/schema/Phase 08 validator:
  403 passed, 1 Gazebo-only skip in 94.30 s
  /tmp/phase08_8_3_scenario.xml
  1dc086718083595dba6d7cc72e658e7836898b51c1a0a07c8d31ff352c927c15

analyzer/integration:
  18 passed in 6.10 s
  /tmp/phase08_8_3_analysis.xml
  ae5f364b361e0a6520f36443c425f08c71291daf3334a032cd5de341a55907ae

broad ROS-independent functional:
  791 passed, 2 Gazebo-only skips in 135.75 s
  /tmp/phase08_8_3_broad.xml
  597fdccfaf97c93d6d93b80f77ec14759684cef67f19f5177218aaa682936624
```

Fatal changed-Python lint, compilation, launch XML, all four v8.3 YAML
documents, `git diff --check`, and Phase 08 implementation-context validation
pass.

The fresh isolated build at `/tmp/phase08_8_3_release_qual` finished
`ros_esc_interfaces`, `ros_esc`, and `turtlebot3_rotating_sensor` in `13.0 s`.
Source/install parity passes for all `10/10` runtime artifacts. Installed
launch argument and description construction pass. Default and opted-in
supervisor and Gaussian nodes construct from the isolated install under
bounded five-second checks.

An initial direct opted-in supervisor construction command omitted the
existing counted-source `max_fill_clusters=1` parameter and was correctly
rejected. The corrected command matched `known_source_count=2` with
`max_fill_clusters=1` and passed. No source or scenario changed in response.

Installed dry-run resolution passes:

```text
primary visible:    1 resolved / 0 unsupported
primary repeats:   10 resolved / 0 unsupported
secondary visible:  1 resolved / 0 unsupported
secondary repeats:  5 resolved / 0 unsupported
```

None of the four declared campaign roots was created. Historical world and V6
selection hashes remain exact, and no historical scenario changed.

Complete implementation, compatibility, test, build, installed-graph, dry-run,
hash, and dispatch evidence:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_1_no_gazebo_qualification.md
```

No Gazebo, recording, new-bag analysis, or physical process ran during M4.1
implementation or qualification.

## Current milestone

**PHASE 08.8 M4.1 — V8.3 IMPLEMENTED / NO-GAZEBO QUALIFICATION PASS /
MATERIAL CHECKPOINT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Run the Phase 08 material checkpoint, inspect its bounded diff, and commit the
exact qualified v8.3 boundary. Only that committed boundary can authorize one
visible primary probe at seed `19101`.

## Phase 08.8 M4.1 material checkpoint — 2026-07-30

The fully qualified v8.3 implementation, tests, scenarios, live status, and
durable validation record received the required precommit Phase 08 checkpoint
against base HEAD `937c6d4`.

```text
checkpoint:
  docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt
status sha256:
  fdee18e366b815d0f04cb241ec6d28cd8a1a9c54141a053e88b474d3cd446f4c
unstaged diff sha256:
  7e7df65fc3fd45336f959810d0e77dc7261a6286353a69ee76acb6d4a7b98d74
diff check:
  PASS
```

No Gazebo, scenario, recorder, analyzer, or physical process ran while
creating the checkpoint.

## Current milestone

**PHASE 08.8 M4.1 — V8.3 IMPLEMENTED / NO-GAZEBO QUALIFICATION PASS /
MATERIAL CHECKPOINT PASS / COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact qualified boundary, verify the commit and clean worktree,
then record a separate committed dispatch boundary before executing the single
visible primary probe at seed `19101`.

## Phase 08.8 M4.1 qualified implementation commit — 2026-07-30

The exact candidate-informed fill implementation, tests, four fresh v8.3
scenario inputs, no-Gazebo qualification record, live status, and material
checkpoint were committed at:

```text
ddcdbf621a26201ba4d3b8b5c2e3397372d4edec
phase 08.8: qualify candidate-informed fill
```

The post-commit worktree is clean. The four v8.3 campaign roots remain absent,
and no Gazebo process is active. This commit fixes the executable bytes for the
single visible primary probe; it does not claim behavioral success.

## Current milestone

**PHASE 08.8 M4.1 — QUALIFIED V8.3 INPUT COMMITTED / DISPATCH CHECKPOINT
PENDING / GAZEBO PROHIBITED.**

## Next criterion

Refresh the Phase 08 checkpoint against commit `ddcdbf6`, commit this dispatch
record, reconfirm the clean process/evidence boundary, and then execute exactly
one installed visible run of `phase08_v8_3_primary_visible_probe.yaml`, seed
`19101`.

## Phase 08.8 M4.1 committed-input dispatch checkpoint — 2026-07-30

The dispatch record received a fresh Phase 08 checkpoint against committed
implementation HEAD `ddcdbf6`.

```text
status sha256:
  d2c72ec3adffbd56064d50b8d549e8878a2e1c1b867fb7611a5aed7f1ec5d9d8
unstaged diff sha256:
  f759c50011f3e9b1c6cb9c9a09b57cfb28035be11659dbc39179342d539af09f
diff check:
  PASS
```

No Gazebo, scenario, recorder, analyzer, or physical process ran while
creating this checkpoint.

## Current milestone

**PHASE 08.8 M4.1 — QUALIFIED V8.3 INPUT COMMITTED / DISPATCH CHECKPOINT
PASS / DISPATCH-RECORD COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact two-document dispatch boundary. Then verify a clean tree,
inactive Gazebo process set, absent primary evidence root, and isolated-install
scenario parity before running the one authorized visible seed-`19101` probe.

## Phase 08.8 M4.1 dispatch-record commit boundary — 2026-07-30

The committed-input dispatch checkpoint and its live-status record were
committed at:

```text
77bb447e22f335dc0b748f1c4b465f8d57e49913
phase 08.8: authorize v8.3 primary probe
```

Preflight confirmed a clean tree, exact committed scenario hash, exact
source/install scenario parity, available X display, absent evidence root, and
inactive Gazebo process set.

## Phase 08.8 M4.1 fixed v8.3 primary visible probe — 2026-07-30

**FORMAL PASS / INFRASTRUCTURE COMPLETE / STAGE A PASS / EXACT ONE FILL /
CANDIDATE-INFORMED AMPLITUDE FLOOR PASS / STRICT SECOND-CANDIDATE RAW RANKING
PASS / STAGE B PASS / ANALYSIS COMPLETE / CLEANUP PASS / RETAINED.**

Exactly one installed execution of
`phase08_v8_3_primary_visible_probe.yaml`, seed `19101`, ran with Gazebo GUI on
ROS domain `228`. It was not retried.

Retained summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_3_primary_probe/
  scenario_summaries/
  20260731T065341485714Z_phase08_v8_3_primary_visible_probe.yaml
SHA-256:
  f9bc1e98ea5169e9e14c00564c189dc9f6ceaa61b1f96a578f646b73a037a511
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_3_primary_probe/
  2026-07-31/
  20260731T065342440883Z_simulation_phase08_v8_3_primary_visible_probe-v8_3_primary_probe_r1p5_a45_h25_19101-robust__f966a38d
```

Infrastructure and validation:

```text
record return code / timed out: 0 / false
recording completeness:         PASS
completeness failures/warnings: none / none
final readiness false:          PASS
final-zero:                     PASS
cleanup / leftovers:            PASS / none
analysis status/failures:       complete / none
```

The complete required path passed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Stage A completed at simulation time `286.917 s`, within `360.0 s`, with
exactly one created, typed, active fill and no merge or supersession.

The candidate-informed correction bound the same raw interval across the
detector and fill owner:

```text
candidate-one estimate / MAD:   -2.066566929 / 0.109025122
candidate-one uncertainty:       0.327075365
candidate-one lower bound:      -2.393642294
amplitude scale:                 1.25
requested/applied floor:         2.992052867 / 2.992052867
amplitude capped:                false
accepted fill amplitude:         2.992052867
sigma major/minor:               0.506211 / 0.506211 m
exit radius:                     1.366771 m
```

The prior v8.2 failure used a `0.10` fill. This run's accepted amplitude equals
the bounded candidate-informed floor, proving the intended integration was
live. The initial repulsion crossed its unchanged stall gate, the allowed
finite assist ran, and escape completed successfully in `29.000459 s`.

Strict terminal ranking passed:

```text
candidate-two estimate/lower:   -3.837209302 / -3.837209302
filled candidate lower:         -2.393642294
strict separation margin:        1.443567009
candidate ordinal / count:       2 / 2
```

Stage B stopped only after controller ranking and the first valid later
proximity sample:

```text
GOAL_REACHED simulation time: 415.8 s
proximity sample time:        415.913 s
position:                     (3.606833, 3.550034) m
global distance:              0.117969 m
interpolation:                false
Stage B elapsed:              128.996 s of 180.0 s
```

The physical contract remains manual `Ctrl+C`; the evaluator coordinate and
automatic proximity stop remain simulation-only.

Analyzer evidence:

```text
synchronized samples: 53,516
path length:          25.320732 m
goal time:            416.390855 s
escape attempts:      1
escape successes:     1
failsafe/timeout:     false / false
terminal state:       GOAL_HOLD
```

Evidence hashes:

```text
7528317aebcaa7c9ddd2b277888b55b26e26cba4c78374764edae34f3685fce2  bag
773b2345bd882c655b22d9c5f1d4a283f72716e9b9dacd119e5a5f5d9370c7ac  completeness
f7e0bd349863b35786d3c19404615e8b63fab1bcab47799e94dd993e80e8bd8e  scenario result
28379327d17c4f60ddab4374afae3dd00c14ea5d495885d7f137b7ef2dde37e2  analysis completeness
70e536001c2d9f9914e62995d66867b9f0ec05eeadb70ffc0ff45101466c6836  summary metrics
```

All nine standard plots and their machine-readable tables are retained under
`analysis/phase07`. The trajectory visibly shows local capture, one fill,
escape, open-field transit, and global capture. The candidate plot visibly
shows candidate two below candidate one's retained lower bound.

Complete report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_1_primary_probe.md
```

## Current milestone

**PHASE 08.8 M4.1 — FIXED V8.3 PRIMARY VISIBLE PROBE FORMAL PASS /
RESULT CHECKPOINT PENDING / PRIMARY REPEATS PROHIBITED UNTIL RESULT COMMIT.**

## Next criterion

Checkpoint and commit this immutable visible-probe result. Then create and
commit the separate primary-repeat dispatch boundary before running the sealed
ten seeds `19111..19120` serially and headlessly under first-failure stop.

## Phase 08.8 M4.1 visible-result material checkpoint — 2026-07-31

The retained formal pass, complete report, live status, evidence hashes, and
plot paths received the required Phase 08 checkpoint against committed
dispatch HEAD `77bb447`.

```text
status sha256:
  50ed095ec4d1f0588a50ec6dda344ab4b045b7f5737c9689e29c9bec7e933af5
unstaged diff sha256:
  e58e4409213d725b8c12b4d3f737e422f5bee3aeac9df8ed4e3a0094f86f0b8c
diff check:
  PASS
```

No Gazebo or matching runtime process remained during the checkpoint.

## Current milestone

**PHASE 08.8 M4.1 — FIXED V8.3 PRIMARY VISIBLE PROBE FORMAL PASS /
RESULT CHECKPOINT PASS / RESULT COMMIT PENDING / PRIMARY REPEATS PROHIBITED.**

## Next criterion

Commit this exact result boundary and verify it. Then record, checkpoint, and
commit authorization for the fixed primary-repeat suite before dispatching any
of seeds `19111..19120`.

## Phase 08.8 M4.1 retained visible-result commit — 2026-07-31

The immutable passing result, complete evidence report, live status, and
checkpoint were committed at:

```text
c3f0d4820bbcaa0767437e681c71deca5f28d9f2
phase 08.8: retain passing v8.3 primary probe
```

Post-commit verification passes: the worktree is clean, no Gazebo process is
active, the primary-repeat evidence root is absent, and the committed
`phase08_v8_3_primary_repeats.yaml` hash and isolated-install bytes match
exactly.

## Phase 08.8 M4.2 fixed v8.3 primary-repeat dispatch boundary — 2026-07-31

The visible gate authorizes the already committed fixed primary population:

```text
scenario:
  phase08_v8_3_primary_repeats.yaml
scenario SHA-256:
  51456d960af47a1942033e80e38a049a74b848345c091e1cda257b04c0ac30bc
case:
  v8_3_primary_repeat_r1p5_a45_h25
seeds:
  19111..19120
resolved runs:
  10
execution:
  serial, headless, stop on first run or cleanup failure
evidence root:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_3_primary_repeats
```

No parameter, source, seed, acceptance predicate, timeout, or stop rule may
change during this gate. Every executed case is retained. The first formal
failure closes the population immediately, leaves later seeds undispatched,
and prohibits the secondary campaign. No retry is authorized.

## Current milestone

**PHASE 08.8 M4.2 — FIXED TEN-RUN V8.3 PRIMARY POPULATION DECLARED /
DISPATCH CHECKPOINT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Checkpoint and commit this exact dispatch boundary. Then reconfirm the clean
tree, inactive process set, absent evidence root, and installed scenario hash
before executing the ten seeds serially and headlessly under the sealed
first-failure rule.

## Phase 08.8 M4.2 primary-repeat dispatch checkpoint — 2026-07-31

The fixed ten-run population and first-failure dispatch contract received the
required Phase 08 checkpoint against retained-result HEAD `c3f0d48`.

```text
status sha256:
  1d900007ea8f7ef18cf19cc008c470a68c2883ac446de2136d9c2be88f87076c
unstaged diff sha256:
  2790f6a2cb3403dba7faec7da913aada2ab7e450abe8d045b2f5e3e1445631e3
diff check:
  PASS
```

No Gazebo, scenario, recorder, analyzer, or physical process ran while
creating this checkpoint.

## Current milestone

**PHASE 08.8 M4.2 — FIXED TEN-RUN V8.3 PRIMARY POPULATION DECLARED /
DISPATCH CHECKPOINT PASS / DISPATCH COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact two-document dispatch boundary. Only that clean committed
state authorizes the fixed ten-run primary gate.

## Phase 08.8 M4.2 fixed v8.3 primary-repeat result — 2026-07-30

**FIXED POPULATION FAIL / FOUR OF FIVE DISPATCHED PASS / SEED `19115` STAGE B
FAIL / FIVE LATER SEEDS NOT DISPATCHED / INFRASTRUCTURE COMPLETE / EVIDENCE
RETAINED.**

The committed headless population ran serially from dispatch HEAD `ec21cda` on
ROS domain `229`. Exactly seeds `19111..19115` executed once. Seeds
`19111..19114` passed the complete counted-candidate path, strict second
candidate ranking, and the `0.50 m` post-recovery evaluator stop. Seed `19115`
passed Stage A at simulation time `346.924 s`, created exactly one typed active
fill, completed `ESCAPE_REPULSE -> ESCAPE_ASSIST -> SEARCH`, but did not find
or rank candidate two within its independent `180.0 s` Stage B budget.

```text
seed       formal result   Stage A (s)   Stage B (s)   final global distance
19111      PASS             191.010       115.294       0.141761 m
19112      PASS             200.825       121.006       0.155023 m
19113      PASS             202.227       133.382       0.119478 m
19114      PASS             190.634       164.390       0.185826 m
19115      FAIL             346.924       180.030       5.167727 m
19116-20   NOT DISPATCHED
```

The runner stopped at the first formal failure with
`stopped_early_reason: run_failure`; seed `19115` was not retried. All five
executed recorders returned zero without timeout, authoritative completeness
passed, final-zero and final-readiness-false passed, cleanup passed with no
leftovers, and no Gazebo process remains.

Retained summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_3_primary_repeats/
  scenario_summaries/
  20260731T070914746817Z_phase08_v8_3_primary_repeats.yaml
SHA-256:
  596b93d0fa07a63be2bc9b38691fb879b017ff8e1b5d21ade9bfffc8a99c2ec8
```

Complete report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_2_primary_repeats.md
```

Cross-seed diagnosis isolates direction rather than fill strength. Seed
`19115` used the same `3.557` fill amplitude and approximately the same
candidate-one lower bound as three passing seeds. The offline dot product from
fill center to assisted exit against fill center to the declared global was
positive for all four passes (`+0.906`, `+0.751`, `+0.559`, `+0.159`) and
exactly opposite for the failure (`-1.000`). It escaped through the
arrival-side corridor and ended at `(0.11484, -0.40462) m`; it did not revisit
the filled local.

Both escape states currently exclude raw sensor cost. The Gaussian supplies
radial repulsion but cannot distinguish which outward hemisphere contains the
stronger unseen source; open-field assist freezes the radial side occupied at
the stall sample. Merely weakening the fill or extending Stage B does not
correct that symmetry defect.

## Current milestone

**PHASE 08.8 M4.2 — FIXED V8.3 PRIMARY POPULATION CLOSED FAIL / SECONDARY AND
BROAD V8.3 DISPATCH PROHIBITED / RESULT CHECKPOINT PENDING.**

## Next criterion

Checkpoint and commit the immutable v8.3 failure report and status. Then save
and review a fresh default-off amendment that restores a sensor-derived
directional asymmetry during escape without source coordinates, Vicon, room
geometry, global pose, route planning, or changes to historical behavior.
No further Gazebo process is authorized until that correction passes complete
no-Gazebo qualification, checkpointing, and a bounded commit.

## Phase 08.8 M4.2 retained-result checkpoint — 2026-07-30

The fixed-population failure, five immutable run records, complete diagnostic
report, evidence hashes, plot paths, live status, and first-failure gate
disposition received the required Phase 08 material checkpoint against
dispatch HEAD `ec21cda`.

```text
status sha256:
  1eeadf7fd8d9dd5ecf335692ebce679620ce39e7e086295e38e152d956747d2f
unstaged diff sha256:
  2d422673b46973bdffd3a7c2acad8456a9c59d44adceb5daf35277af664c3078
diff check:
  PASS
```

No Gazebo, scenario, recorder, analyzer, or physical process remained during
the checkpoint.

## Current milestone

**PHASE 08.8 M4.2 — FIXED V8.3 PRIMARY POPULATION CLOSED FAIL / RETAINED
RESULT CHECKPOINT PASS / RESULT COMMIT PENDING / ALL V8.3 DISPATCH
PROHIBITED.**

## Next criterion

Commit this immutable result boundary and verify a clean tree. Only then may a
fresh versioned correction amendment be saved and qualified without Gazebo.

## Phase 08.8 M4.3 v8.4 Plan amendment — 2026-07-30

The immutable v8.3 failure boundary was committed at:

```text
ed49369
phase 08.8: retain failed v8.3 primary repeats
```

The fresh v8.4 amendment is now saved in
`docs/codex/gesc_gaussian/plans/phase_08_8_plan.md`. It adds one default-off,
escape-scoped approach-continuity vector selected from the existing supervisor
odometry history and frozen fill exit geometry. It does not add a route map,
waypoint, source/global coordinate, Vicon input, room geometry, or persistent
post-escape direction.

The correction selects the newest recorded pose outside the fill's frozen exit
radius, points from that pre-basin anchor toward the fill center, and chooses
the most aligned existing fill-safe candidate. The robust affine term follows
that typed direction only during `ESCAPE_REPULSE`/`ESCAPE_ASSIST`; ordinary
`SEARCH` remains raw plus Gaussian with affine zero.

Offline replay of all five retained v8.3 primary fill geometries produces
positive evaluator-only initial selected/global alignments from `+0.883` to
`+0.999`. At failed seed `19115`'s stall pose, the old radial alignment is
about `-0.852`; revalidation of the frozen approach direction selects a safe
tangent aligned `+0.472`. The global coordinate was used only to describe this
offline diagnostic and is not an implementation input.

Fresh v8.4 identities and seeds are fixed at `19201`, `19211..19220`, `19251`,
and `19261..19265`. No v8.4 source or scenario has been implemented, and no
Gazebo process is authorized.

## Current milestone

**PHASE 08.8 M4.3 — V8.4 APPROACH-CONTINUITY PLAN AMENDMENT SAVED /
PLAN CHECKPOINT PENDING / IMPLEMENTATION NOT STARTED / GAZEBO PROHIBITED.**

## Next criterion

Validate and checkpoint this bounded amendment, inspect its exact diff, and
commit the Plan boundary. Then implement and fully qualify v8.4 without
Gazebo. Only a later qualified implementation checkpoint and commit may
authorize a fresh visible probe.

## Phase 08.8 M4.3 v8.4 Plan checkpoint — 2026-07-30

The approach-continuity amendment and live status received the required
preimplementation Phase 08 checkpoint against retained v8.3 result HEAD
`ed49369`.

```text
active subphase plan sha256:
  f489a657d6ac584d0a9f072dfdd7047e6f7c5780552025c2e76fa1ae5275b845
status sha256:
  585b22393afb07b12d771d6b77bc711cfdff540284f7b53e8a36e8f1e2fbb899
unstaged diff sha256:
  19707a7fded7c4bcf084634d4c2e8ef3f9703f9794607a068b99634b5146c0ad
diff check:
  PASS
```

No Gazebo, scenario, recorder, analyzer, or physical process ran while
creating the checkpoint.

## Current milestone

**PHASE 08.8 M4.3 — V8.4 APPROACH-CONTINUITY PLAN CHECKPOINT PASS /
PLAN COMMIT PENDING / IMPLEMENTATION NOT STARTED / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact Plan boundary and verify a clean tree. Then implement the
default-off correction and fresh v8.4 inputs, followed by every declared
no-Gazebo qualification gate.

## Phase 08.8 M4.3 v8.4 implementation qualification — 2026-07-30

Plan boundary commit:

```text
31a90c9
phase 08.8: plan v8.4 approach continuity
```

The default-off v8.4 correction and all four fresh fixed inputs are
implemented. The supervisor now freezes one escape-scoped direction from the
newest existing odometry-history pose strictly outside the accepted fill's
frozen exit radius. It selects and revalidates the most aligned fill-safe
forward candidate, publishes `(0, 1, 1)` weights through
`ESCAPE_REPULSE`/`ESCAPE_ASSIST`, and clears the direction plus affine
authority on measured escape completion, reset, or fault.

The robust modified-cost owner accepts the typed direction/revision in both
escape states. Supervisor translation remains zero in `ESCAPE_REPULSE`; the
existing bounded translation is available only after measured stall. Ordinary
`SEARCH` remains raw plus Gaussian with affine zero.

The enabled escape/configuration evidence records the qualified history
anchor, age, displacement, exit radius, continuity vector, selected direction,
rotation, and revision. Default-off historical event payloads remain
unchanged. No source/global coordinate, Vicon pose, room dimension, evaluator
truth, proximity result, waypoint, route map, or persistent post-escape
direction was introduced.

Exact replay of all five retained v8.3 fill-acceptance geometries is
fill-safe and forward. The exact failed-seed first-assist replay corrects the
preliminary continuous-tangent diagnostic:

```text
old radial:
  (-0.9596900359, -0.2810605541)
enabled fixed candidate:
  (-0.3364241478, 0.9417105674)
evaluator-only global alignment:
  -0.914 -> +0.351
```

The Plan now distinguishes the preliminary continuous tangent from the exact
executable `45-degree` candidate fixture.

Fresh identities:

```text
primary visible:
  phase08_v8_4_primary_visible_probe.yaml
  seed 19201
primary repeats:
  phase08_v8_4_primary_repeats.yaml
  seeds 19211..19220
secondary visible:
  phase08_v8_4_secondary_visible_probe.yaml
  seed 19251
secondary repeats:
  phase08_v8_4_secondary_repeats.yaml
  seeds 19261..19265
```

Final source qualification:

```text
focused controller/geometry/supervisor/modified-cost/legacy:
  285 passed
focused schema/runner/validator/recording/analysis:
  504 passed, 1 expected Gazebo-opt-in skip
broad ROS-independent functional:
  819 passed, 2 expected Gazebo-opt-in skips
fatal changed-file lint:
  PASS
Python compilation, XML/YAML parse, git diff check:
  PASS
phase context:
  PASS
```

Final fresh installed qualification:

```text
root:
  /tmp/phase08_8_m4_3_release_qual
build:
  3 packages finished in 11.9 s
source/install parity:
  10/10
installed supervisor construction:
  expected bounded timeout 124; no error
installed modified-cost construction:
  expected bounded timeout 124; no error
installed dry-runs:
  1 + 10 + 1 + 5 resolved
  0 unsupported
  no configured run root created
```

V6, all historical scenarios/worlds, every fixed failed run, and retained
plots/bags remain unchanged. The exact validation record is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_3_no_gazebo_qualification.md
```

No Gazebo, recorder, analyzer, or physical process ran during implementation
or qualification.

Several bounded defects were found and corrected before runtime: missing
repulse-state affine exposure, a duplicate staged-schema affine prohibition,
copied v8.3 case labels, a preliminary non-executable tangent value, and
unconditional configuration-event exposure. All affected gates were repeated
on the exact final source.

## Current milestone

**PHASE 08.8 M4.3 — V8.4 IMPLEMENTED / NO-GAZEBO QUALIFICATION PASS /
IMPLEMENTATION CHECKPOINT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Checkpoint and commit the exact qualified implementation plus validation
record. Then create and commit a separate dispatch boundary. Only that clean
installed boundary may authorize one visible primary probe at seed `19201`.
No repeat or secondary dispatch is authorized.

## Phase 08.8 M4.3 v8.4 implementation checkpoint — 2026-07-30

The exact final implementation, four fixed inputs, tests, qualification
record, Plan evidence correction, and live status received the required
precommit Phase 08 material checkpoint against Plan HEAD `31a90c9`.

```text
status sha256:
  04b1791b289f09de92d29ebeb7e20e8da6da3f24152bcd860d5f22554afbb8a3
active subphase plan sha256:
  f8864cda6cda530cabb5b572d8cad86834de2a7e82bb69b382e04c6e3451018f
qualification record sha256:
  3f523b9a9c022d9d0214d328d981349e9d83f14f40e153f7548c1c7aaa74f162
staged implementation diff sha256:
  dc4bf1a56333a24e2cfa55d298e6bcfbb1843cc14751e92fcec85096a8f54184
unstaged and staged diff check:
  PASS
```

No Gazebo, scenario, recorder, analyzer, or physical process ran during the
checkpoint.

## Current milestone

**PHASE 08.8 M4.3 — V8.4 IMPLEMENTED / NO-GAZEBO QUALIFICATION PASS /
IMPLEMENTATION CHECKPOINT PASS / IMPLEMENTATION COMMIT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Commit this exact qualified implementation boundary and verify a clean tree.
Then save, checkpoint, and commit a separate visible-probe dispatch boundary.
Only that later boundary may authorize seed `19201`; repeats and secondary
runs remain prohibited.

## Phase 08.8 M4.3 qualified implementation commit — 2026-07-30

The exact v8.4 implementation, four fixed inputs, complete no-Gazebo
qualification, Plan evidence correction, live status, and material checkpoint
were committed at:

```text
c8fe788e781daece98993a223c5aa71fd1d5b7a9
phase 08.8: qualify v8.4 approach continuity
```

Post-commit preflight is clean:

```text
worktree:
  clean
primary visible evidence root:
  absent
matching Gazebo/scenario/recorder/analyzer processes:
  none
DISPLAY:
  :0
xdpyinfo:
  PASS
source primary-visible scenario sha256:
  3c876eddb86196b54207204b975f64930bcf8f99697e86f2524fd4168f7e66d8
installed primary-visible scenario sha256:
  3c876eddb86196b54207204b975f64930bcf8f99697e86f2524fd4168f7e66d8
source/install parity:
  PASS
```

This fixes the executable bytes but does not yet authorize Gazebo.

## Current milestone

**PHASE 08.8 M4.3 — QUALIFIED V8.4 IMPLEMENTATION COMMITTED / VISIBLE
DISPATCH CHECKPOINT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Checkpoint and commit this exact two-document dispatch boundary against
`c8fe788`. Only that clean committed record may authorize one installed
visible run of `phase08_v8_4_primary_visible_probe.yaml`, seed `19201`.
No retry, primary repeat, secondary run, or broad characterization is
authorized.

## Phase 08.8 M4.3 visible-dispatch checkpoint — 2026-07-30

The committed-input dispatch record received a fresh Phase 08 checkpoint
against qualified implementation HEAD `c8fe788`.

```text
status sha256:
  b76b12d963ac3bf87cc6def7038f76541a5616f265778aa5c7ca8fcd9c7bb222
unstaged dispatch diff sha256:
  8cbf368ffe8d6c8e73fd3f48e1df2d3dbd379086531935a5e1391059306a2f89
unstaged and staged diff check:
  PASS
```

No Gazebo, scenario, recorder, analyzer, or physical process ran during this
checkpoint.

## Current milestone

**PHASE 08.8 M4.3 — QUALIFIED V8.4 IMPLEMENTATION COMMITTED / VISIBLE
DISPATCH CHECKPOINT PASS / DISPATCH-RECORD COMMIT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Commit this exact two-document dispatch boundary. Then reconfirm the clean
tree, inactive runtime process set, absent primary evidence root, installed
scenario parity, and GUI display immediately before executing the one
authorized seed-`19201` visible probe. All later dispatch remains prohibited.

## Phase 08.8 M4.3 fixed v8.4 primary visible probe — 2026-07-30

**FORMAL PASS / INFRASTRUCTURE COMPLETE / STAGE A PASS / EXACT ONE FILL /
APPROACH-CONTINUITY ESCAPE PASS / STRICT SECOND-CANDIDATE RANKING PASS /
STAGE B PASS / FINAL ZERO PASS / CLEANUP PASS.**

The one authorized visible execution ran once from dispatch HEAD `8e9acef`;
seed `19201` was not retried.

```text
scenario:
  phase08_v8_4_primary_visible_probe.yaml
case:
  v8_4_primary_probe_r1p5_a45_h25_19201
run:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_4_primary_probe/
  2026-07-31/
  20260731T084942744556Z_simulation_phase08_v8_4_primary_visible_probe-v8_4_primary_probe_r1p5_a45_h25_19201-robust__c341bb3f
scenario summary:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_4_primary_probe/
  scenario_summaries/
  20260731T084941800046Z_phase08_v8_4_primary_visible_probe.yaml
scenario summary sha256:
  0ffebd184a0df830568d3031853ac576eee920d1a3d1fc48d2ed8323721c6c9c
```

The authoritative state path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Stage A completed at simulation time `236.127 s`, within its fixed `360.0 s`
budget. The first candidate was `0.305871 m` from the declared local; one
typed active cluster was created at `(0.919344, 1.206038) m`; no fill was
merged, superseded, or rejected.

The v8.4 escape froze the onboard-history continuity vector
`(0.511779, 0.859117)` and selected the fill-safe direction
`(0.969370, 0.245605)`. Both escape states recorded weights `(0, 1, 1)`.
The assisted escape completed in `29.193833 s`; on the first returned
`SEARCH` sample the weights were `(1, 1, 0)` and the safe direction was
invalid, proving that affine authority did not persist after recovery.

The second candidate raw-cost interval was
`[-3.8372093023255816, -3.8372093023255816]`, strictly below the first
candidate's retained lower bound `-2.438816425126134`, with margin
`1.3983928771994476`. The controller emitted `GOAL_REACHED` before the first
valid evaluator-only proximity sample at simulation time `351.217 s`,
position `(3.572528, 3.626830) m`, distance `0.146104 m`. Stage B took
`115.090 s`, within its independent `180.0 s` budget. The final retained
distance is `0.146083 m`.

Recording, authoritative Phase 05 completeness, final readiness false,
final-zero commands, and cleanup all pass. There was no in-readiness failsafe,
timeout, recenter, forbidden state/event, or remaining process.

The analyzer retained all nine plots and every table. Its top-level status is
honestly `partial` with no analysis failures: contacts and generic aggregate
truth metrics are intentionally unavailable for this open-field staged
scenario, and one `0.20 s` state sample gap during post-recovery `SEARCH`
invalidates only reconstructed duration totals. The authoritative scenario
acceptance, transition/event sequences, candidate ranking, Stage A, Stage B,
and completeness remain passed.

Evidence hashes:

```text
5af1b2d8c53b51ae8e19946a3a93639582cc39c96a987eb6e546b4f681e6f3db  bag
5bb9de40208460fed17e3aa381be983886fbfd51c52b29208ef8a3794d9b7f45  completeness
9677a65b30778f560bfc7ce07627e057d9296e0bb3710e189ba35b7beebf4e5a  scenario result
73ecfacc0b83e439e97f25a755cf87f1fe498fb3bfc8af002d093ca8c25eed76  analysis completeness
8131fda72481894249e96721f6052c6781641723c87aa08a028ec902886c882d  summary metrics
```

Complete report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_3_primary_probe.md
```

## Current milestone

**PHASE 08.8 M4.3 — FIXED V8.4 PRIMARY VISIBLE PROBE FORMAL PASS /
RESULT CHECKPOINT PENDING / PRIMARY REPEATS PROHIBITED.**

## Next criterion

Checkpoint and commit this immutable visible-probe result. Then create,
checkpoint, and commit a separate dispatch boundary for the fixed seeds
`19211..19220`. Only that later clean committed boundary may authorize the
headless serial repeat gate. Secondary and broad runs remain prohibited.

## Phase 08.8 M4.5 visible-result material checkpoint — 2026-07-31

The immutable formal pass, complete analyzer output, report, live status,
evidence hashes, tables, and plot paths received the required Phase 08
material checkpoint against committed dispatch HEAD `5113e5b`.

```text
base HEAD:
  5113e5be0facf93371d36339f8b19a1301942df6
status sha256 before this checkpoint note:
  2983c4ef0917bab8bd1df7263f09ca161b78d96cd91dd6658a4397cb758ffbec
validation report sha256:
  1bddf399e9394749fc0e2e9d5915daac970cec77feee81a9e833a433127225d7
tracked unstaged diff sha256:
  8de0e6062bd344314e88a94ade9d571a7d03bdaebd5863c5a7880f979b3a16c4
combined status-plus-untracked-report diff sha256:
  431fc37f8a420dc5069cbb592adcaddf08c9949dc4701fcdb983f4ca8df5b68a
checkpoint sha256 before this checkpoint note:
  81d97f495cfbd264465a04c45c8623f722252f3dc66b68f5814b9da95f25d0e7
unstaged and staged diff checks:
  PASS
phase context:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or physical process
remained during this result checkpoint.

## Current milestone

**PHASE 08.8 M4.5 — FIXED V8.5 PRIMARY VISIBLE PROBE FORMAL PASS /
RESULT CHECKPOINT PASS / RESULT COMMIT PENDING / PRIMARY REPEATS
PROHIBITED.**

## Next criterion

Stage and commit this exact result boundary, then verify the commit and clean
tree. Only afterward may a separate checkpointed and committed dispatch
boundary authorize the fixed primary repeat seeds `19311..19320`.

## Phase 08.8 M4.3 visible-result material checkpoint — 2026-07-30

The immutable formal pass, complete report, live status, evidence hashes, and
plot paths received the required Phase 08 material checkpoint against
committed dispatch HEAD `8e9acef`.

```text
status sha256:
  034618a778f2c80f90f3a74a24905fac5a7f163127323e289110dfb89c9ebd4e
validation report sha256:
  4a037d8e6603df3718a76f769606f81e36416c042eedbbbc7ef098ac45d852ac
unstaged diff sha256:
  410d62f55f54b9e268910cdf130b9f3ef661e4be33609f0b764bb0cdd8b43c9a
diff check:
  PASS
```

No Gazebo, scenario, recorder, analyzer, or physical process remained during
the checkpoint.

## Current milestone

**PHASE 08.8 M4.3 — FIXED V8.4 PRIMARY VISIBLE PROBE FORMAL PASS /
RESULT CHECKPOINT PASS / RESULT COMMIT PENDING / PRIMARY REPEATS
PROHIBITED.**

## Next criterion

Commit this exact result boundary and verify it. Then record, checkpoint, and
commit the separate fixed-primary-repeat dispatch boundary before executing
any of seeds `19211..19220`.

## Phase 08.8 M4.4 fixed v8.4 primary-repeat dispatch boundary — 2026-07-30

The immutable passing visible result was committed at:

```text
800274d
phase 08.8: retain passing v8.4 primary probe
```

Post-commit verification passes: the worktree is clean, no matching Gazebo or
scenario process is active, the repeat evidence root is absent, and the
committed source scenario exactly matches the previously qualified isolated
install.

The passing visible gate authorizes this already committed fixed population:

```text
scenario:
  phase08_v8_4_primary_repeats.yaml
scenario SHA-256:
  ef822e73c13f1e78d94c60ae10a11438caae8137507aae837495d84109699407
case:
  v8_4_primary_repeat_r1p5_a45_h25
seeds:
  19211..19220
resolved runs:
  10
execution:
  serial, headless, stop on first run or cleanup failure
per-run limits:
  540.0 s simulation, 720.0 s wall
evidence root:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_4_primary_repeats
```

No source, start, intensity, profile value, acceptance predicate, timeout,
seed, cleanup rule, or stop rule may change during this gate. Each seed may
execute at most once and every executed result must be retained. The first
formal behavioral, infrastructure, recording, or cleanup failure closes the
population immediately, leaves later seeds undispatched, and prohibits the
secondary campaign. No retry is authorized.

## Current milestone

**PHASE 08.8 M4.4 — FIXED TEN-RUN V8.4 PRIMARY POPULATION DECLARED /
DISPATCH CHECKPOINT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Checkpoint and commit this exact dispatch boundary. Then immediately reconfirm
the clean tree, inactive runtime process set, absent evidence root, and
source/install scenario parity before running the ten seeds serially and
headlessly under the sealed first-failure rule.

## Phase 08.8 M4.4 primary-repeat dispatch checkpoint — 2026-07-30

The fixed ten-run population and first-failure dispatch contract received the
required Phase 08 checkpoint against retained visible-result HEAD `800274d`.

```text
status sha256:
  ab2ed1bc860ace3fe2333eb37bd147fcf94d97f938645f13118adf20a451a041
unstaged diff sha256:
  26a6dc3296d06d2087efa7876055f4d890f84e49f6dd20c639e5d6cb3df96b0e
diff check:
  PASS
```

No Gazebo, scenario, recorder, analyzer, or physical process ran while
creating this checkpoint.

## Current milestone

**PHASE 08.8 M4.4 — FIXED TEN-RUN V8.4 PRIMARY POPULATION DECLARED /
DISPATCH CHECKPOINT PASS / DISPATCH COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact dispatch boundary. Only that later clean committed state
authorizes the sealed ten-run primary gate.

## Phase 08.8 M4.4 fixed v8.4 primary-repeat result — 2026-07-30

**FIXED POPULATION FAIL / ONE OF TWO DISPATCHED PASS / SEED `19212` STAGE B
FAIL AFTER ESCAPE-DIRECTION REVERSAL / EIGHT LATER SEEDS NOT DISPATCHED /
INFRASTRUCTURE COMPLETE / EVIDENCE RETAINED.**

The committed headless population ran serially from dispatch HEAD `31a99ed`
on ROS domain `231`. Exactly seeds `19211` and `19212` executed once. Seed
`19211` passed the complete counted-candidate path, strict second-candidate
ranking, and the `0.50 m` post-recovery evaluator stop. Seed `19212` passed
Stage A at simulation time `167.513 s`, created exactly one typed active fill,
and completed `ESCAPE_REPULSE -> ESCAPE_ASSIST -> SEARCH`, but did not find or
rank candidate two within its independent `180.0 s` Stage B budget.

```text
seed       formal result   Stage A (s)   Stage B (s)   final global distance
19211      PASS             193.419       165.988       0.119298 m
19212      FAIL             167.513       180.030       4.679383 m
19213-20   NOT DISPATCHED
```

The runner stopped at the first formal failure with
`stopped_early_reason: run_failure`; seed `19212` was not retried. Both
recorders returned zero without timeout, authoritative completeness passed,
final-zero and final-readiness-false passed, cleanup passed with no leftovers,
and no Gazebo process remains.

Retained summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_4_primary_repeats/
  scenario_summaries/
  20260731T090629163024Z_phase08_v8_4_primary_repeats.yaml
SHA-256:
  5b464fa8c405c4651d863949839d161d00dfd4bd44bc415d4d54cf02fa4ee381
```

Complete report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_4_primary_repeats.md
```

The failed run's onboard-history vector was valid and aligned `+0.911`
against the evaluator-only fill-to-global direction. The active-fill
hard-avoidance rule rejected that direct vector because the robot was only
about `0.001758 m` from the estimated fill center and the direct vector
momentarily reduced that millimetric offset. It selected a tangent instead.

During the Gaussian-only repulse interval, the robot crossed to the opposite
side of the estimated center. Revalidation changed the direction from
`(0.915820, -0.401588)` to `(-0.363617, 0.931549)` and then to
`(-0.915820, 0.401588)`. The final vector is the exact negative of the first.
The robot completed a valid radial escape westward, returned to `SEARCH` near
`(-0.380863, 1.327148) m`, and ended at `(-0.731250, 1.501713) m`.

Seed `19211` retained directional continuity and passed. The active Gaussian
fill is mathematical basin memory rather than a physical obstacle; treating
it as hard avoidance during its own escape permits a millimetric estimator
offset to override and eventually reverse the correct frozen intent.

A fresh correction must latch the direct approach-continuity direction for
the active escape, exclude only the active mathematical fill from
direction-reversal logic, retain avoidance of any other fill, fail rather than
reverse, and clear authority at measured escape completion. Extending Stage B,
weakening the fill, or increasing affine gain alone does not correct a typed
direction that the supervisor itself reverses.

## Current milestone

**PHASE 08.8 M4.4 — FIXED V8.4 PRIMARY POPULATION CLOSED FAIL / SECONDARY AND
BROAD V8.4 DISPATCH PROHIBITED / RESULT CHECKPOINT PENDING.**

## Next criterion

Checkpoint and commit the immutable v8.4 failure report, two executed run
records, analysis bundles, and live status. Then save and review a fresh
default-off amendment for active-fill corridor locking. No further Gazebo
process is authorized until that correction passes complete no-Gazebo
qualification, checkpointing, and a bounded commit.

## Phase 08.8 M4.4 retained-result checkpoint — 2026-07-30

The fixed-population failure, two immutable run records, analysis/plot
bundles, complete diagnostic report, live status, and first-failure
disposition received the required Phase 08 material checkpoint against
dispatch HEAD `31a99ed`.

```text
status sha256:
  d52ebdeecabba502f745c0cd7a9c76a12cc0681c1adc1f109531026b9817a6c8
validation report sha256:
  03a889f58600287159800fcbe90ec8c447979d79da83f21ecaaa0623a224bc10
unstaged diff sha256:
  57edd4ae9e74595a8da9ce6dda1bf30c083a3b08188dcb00338546f090567037
diff check:
  PASS
```

No Gazebo, scenario, recorder, analyzer, or physical process remained during
the checkpoint.

## Current milestone

**PHASE 08.8 M4.4 — FIXED V8.4 PRIMARY POPULATION CLOSED FAIL / RETAINED
RESULT CHECKPOINT PASS / RESULT COMMIT PENDING / ALL V8.4 DISPATCH
PROHIBITED.**

## Next criterion

Commit this immutable result boundary and verify a clean tree. Only then may a
fresh versioned active-fill corridor-lock amendment be saved and qualified
without Gazebo.

## Phase 08.8 M4.5 v8.5 Plan amendment — 2026-07-30

The immutable v8.4 failure boundary was committed at:

```text
546001f
phase 08.8: retain failed v8.4 primary repeats
```

The fresh v8.5 amendment is now saved in
`docs/codex/gesc_gaussian/plans/phase_08_8_plan.md`. It adds one default-off
active-fill corridor lock to the existing approach-continuity escape.

The direct onboard-history direction remains latched through repulse and any
measured-stall assist. The active Gaussian stays in modified cost and the
typed fill registry, but is not treated as a solid obstacle during its own
escape. Every other retained fill remains a hard direction constraint. An
unsafe corridor fails explicitly instead of selecting an alternate or
reversing direction.

The correction is scoped to the active escape and clears on measured
completion, reset, terminal state, stale/fault path, or explicit stop. It adds
no source/global coordinate, Vicon pose, room geometry, wall model, route map,
waypoint, or persistent post-recovery direction.

Fresh identities and seeds are fixed at `19301`, `19311..19320`, `19351`, and
`19361..19365`. No v8.5 source or scenario has been implemented, and no
Gazebo process is authorized.

## Current milestone

**PHASE 08.8 M4.5 — V8.5 ACTIVE-FILL CORRIDOR-LOCK PLAN AMENDMENT SAVED /
PLAN CHECKPOINT PENDING / IMPLEMENTATION NOT STARTED / GAZEBO PROHIBITED.**

## Next criterion

Validate and checkpoint this bounded amendment, inspect its exact diff, and
commit the Plan boundary. Then implement and fully qualify v8.5 without
Gazebo. Only a later qualified implementation checkpoint and commit may
authorize a fresh visible probe.

## Phase 08.8 M4.5 v8.5 Plan checkpoint — 2026-07-30

The active-fill corridor-lock amendment and live status received the required
preimplementation Phase 08 checkpoint against retained v8.4 result HEAD
`546001f`.

```text
active subphase plan sha256:
  bf88830c4a039a456bf31d3d10835a3e6c6225063f1833b3710c751eb4b628df
status sha256:
  a4f27a47d3417968a0b5e5f7f5eec8be1db56de3871e514d576d102dc029af43
unstaged diff sha256:
  0aef609e105bdbcd84d5da98a6e885ea15fb54c634052dc36b4c157f1ea2384f
diff check:
  PASS
```

No Gazebo, scenario, recorder, analyzer, or physical process ran while
creating the checkpoint.

## Current milestone

**PHASE 08.8 M4.5 — V8.5 ACTIVE-FILL CORRIDOR-LOCK PLAN CHECKPOINT PASS /
PLAN COMMIT PENDING / IMPLEMENTATION NOT STARTED / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact Plan boundary and verify a clean tree. Then implement the
default-off correction and fresh v8.5 inputs, followed by every declared
no-Gazebo qualification gate.

## Phase 08.8 M4.5 v8.5 implementation qualification — 2026-07-31

The v8.5 default-off active-fill corridor lock and four fresh schema-v9
inputs are implemented. No Gazebo, scenario execution, recorder, analyzer,
or physical process ran.

Enabled v8.5 freezes the existing direct approach-history vector at revision
one. The active Gaussian stays in modified cost and the typed registry but is
excluded from direction and command-sweep hard avoidance only for its own
escape. Every other retained fill remains a hard constraint. Repulse and
assist revalidate the exact vector on every update and fail rather than
reselect or reverse it. Measured completion, `SEARCH`, reset, terminal,
explicit stop, and failsafe paths clear the authority.

All eight retained primary geometries reproduce their default-off v8.4
direction and produce the exact direct vector under v8.5. The seed `19212`
fill-acceptance and former reversal geometries retain
`(0.4015882066, 0.9158203494)` at direction revision one. A second
intersecting fill fails explicitly. The active fill remains visible to the
registry and modified-cost owner.

Fresh fixed inputs and hashes:

```text
f8b7be764bb7d7024753cf64b8633944ff70055e9a4a88a97ab8e462b8a5ac6c
  phase08_v8_5_primary_repeats.yaml
39f807c055d5ea0217b6f3510ac34bb1a068316da4cc18841911f428371dae28
  phase08_v8_5_primary_visible_probe.yaml
141916047195f351ff78c524c02fafe6f3af81840a97b55d38148b69f26a8145
  phase08_v8_5_secondary_repeats.yaml
0749ba218bd79212f93946f8e55601e95727e195e8ef8fecd5d192e81a88ee70
  phase08_v8_5_secondary_visible_probe.yaml
```

Exact qualification:

```text
focused controller:
  301 passed in 8.71 s
  /tmp/phase08_8_m4_5_focused_controller_final.xml
  f2a4f6f25fe2359103f3bb5c963845ed3a3fce3f858e57c0cc8bed3ef84de4ad
focused evidence:
  541 passed, 2 skipped in 130.82 s
  /tmp/phase08_8_m4_5_focused_evidence_final.xml
  59d35ddcd54ff0dd56c29d72cdd4551ed154ff02a2b2019b7f959de6ceb7a23b
broad ROS-independent:
  842 passed, 2 skipped in 136.58 s
  /tmp/phase08_8_m4_5_broad_functional_final.xml
  92b429f0fb3aa453271c0d280289940106fde1f27bd71aac99b4d75c9539fee4
```

The two skips are the unchanged explicit Gazebo/recording opt-ins. Fatal
changed-file lint, Python compilation, launch XML, four YAML parses, context
validation, and `git diff --check` pass.

The fresh isolated release build at
`/tmp/phase08_8_m4_5_release_qual` finished all three packages in `12.7 s`.
Source/install parity is `10/10`. Installed `--show-args` and
`--print-description` expose and bind the switch. Default supervisor, fully
enabled v8.5 supervisor, and robust modified-cost construction each reached
the expected bounded timeout `124` without startup error.

All four installed dry-runs resolve with no unsupported cases and do not
create a run root:

```text
primary visible:    1 run,  seed 19301
primary repeats:   10 runs, seeds 19311..19320
secondary visible:  1 run,  seed 19351
secondary repeats:  5 runs, seeds 19361..19365
```

The qualification caught and corrected two bounded pre-Gazebo issues. First,
mechanical seed renumbering had also changed one digit in the secondary local
source coordinate; both fresh secondary files now exactly retain v8.4
`y_m=1.38581929876693`, and the four-pair freeze test plus broad suite pass.
Second, per-tick exact-corridor revalidation was extended from assist to
zero-command repulse. The superseded broad run remains recorded as
`840 passed, 2 failed, 2 skipped`; no empirical attempt was affected.

Complete record:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_5_no_gazebo_qualification.md
```

V6, v8-v8.4, all historical scenarios, worlds, failed evidence, bags, plots,
and results remain unchanged and selectable. The four v8.5 evidence roots
remain absent. No Gazebo or ROS runtime process remains.

## Current milestone

**PHASE 08.8 M4.5 — V8.5 IMPLEMENTED / COMPLETE NO-GAZEBO QUALIFICATION
PASS / IMPLEMENTATION CHECKPOINT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Inspect the complete diff, checkpoint Phase 08, and commit the exact qualified
implementation. Then save and commit a separate dispatch boundary for only
the installed visible primary probe at seed `19301`. Do not dispatch repeats
or any secondary case.

## Phase 08.8 M4.5 v8.5 implementation checkpoint — 2026-07-31

The complete qualified v8.5 implementation, four fresh inputs, tests, report,
and live status received the required material Phase 08 checkpoint against
Plan HEAD `f1dd5d6`.

```text
base HEAD:
  f1dd5d6f75f118e359f5198b1f62cab374e85b48
status sha256 before this checkpoint note:
  2555a8a879e2fba5bbacb63c76abffa7da860d793f3f28768af1db4bd7101368
qualification report sha256:
  9600a4d181e456aece11ff9ab7de5f9d807a498972f4ef20103071c59f9b6f7c
staged implementation diff sha256:
  1800fc88e9fd203eae0f3c6d700f34a4114c4075e752cfe43412cd004fb0f5a9
checkpoint sha256 before this checkpoint note:
  ee7ca258142296956df63183632d40593ecb87733221048467b944e6f8c8513f
unstaged and staged diff checks:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or physical process
was active at checkpoint time. All v8.5 run roots remain absent.

## Current milestone

**PHASE 08.8 M4.5 — V8.5 IMPLEMENTED / NO-GAZEBO QUALIFICATION PASS /
IMPLEMENTATION CHECKPOINT PASS / IMPLEMENTATION COMMIT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Stage this checkpoint note and checkpoint file, commit the exact qualified
implementation, and verify a clean tree. Then create a separate committed
dispatch boundary authorizing only the installed visible primary seed
`19301`.

## Phase 08.8 M4.5 v8.5 visible-dispatch boundary — 2026-07-31

The exact qualified v8.5 implementation was committed at:

```text
9e65952919f26d7ec62a9e1dd0fbd630b9e56424
phase 08.8: qualify v8.5 active-fill transit
```

Post-commit preflight passes:

```text
worktree:
  clean
phase context:
  PASS
primary visible evidence root:
  absent
matching Gazebo/scenario/recorder/analyzer processes:
  none
DISPLAY:
  :0
xdpyinfo:
  PASS
source primary-visible scenario sha256:
  39f807c055d5ea0217b6f3510ac34bb1a068316da4cc18841911f428371dae28
installed primary-visible scenario sha256:
  39f807c055d5ea0217b6f3510ac34bb1a068316da4cc18841911f428371dae28
source/install parity:
  PASS
```

This record proposes exactly one installed GUI execution:

```text
scenario:
  phase08_v8_5_primary_visible_probe.yaml
case:
  v8_5_primary_probe_r1p5_a45_h25_19301
seed:
  19301
profile:
  robust_gaussian_v1
ROS domain:
  230
execution:
  serial, Gazebo GUI visible, one attempt, no retry
scenario run timeout:
  540.0 s
scenario wall timeout:
  720.0 s
outer process timeout:
  900 s
evidence root:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_probe
```

No source, start, source position, intensity, profile value, acceptance
predicate, timeout, seed, cleanup rule, or stop rule may change during the
attempt. The fixed run must demonstrate candidate one, exactly one typed
active fill, one latched direction at revision one, completed local escape,
ordinary affine-free `SEARCH`, strict raw-cost ranking of candidate two,
`GOAL_REACHED`, a later evaluator-only `0.50 m` simulation proximity sample,
final readiness false, final zero, complete recording, and clean shutdown.

Any behavioral, evidence, recording, final-zero, cleanup, or infrastructure
failure closes v8.5 immediately. The attempt is retained regardless of
outcome and cannot be retried. Primary repeats, the secondary probe,
secondary repeats, broad characterization, three lights, physical motion,
and Phase 09 remain prohibited.

## Current milestone

**PHASE 08.8 M4.5 — QUALIFIED V8.5 IMPLEMENTATION COMMITTED / ONE FIXED
VISIBLE PRIMARY PROBE DECLARED / DISPATCH CHECKPOINT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Checkpoint and commit this exact status plus checkpoint dispatch boundary.
Then immediately reconfirm the clean tree, inactive runtime process set,
absent evidence root, installed scenario parity, and GUI display before
executing the one authorized seed-`19301` visible probe.

## Phase 08.8 M4.5 v8.5 visible-dispatch checkpoint — 2026-07-31

The one-attempt visible dispatch contract received the required Phase 08
checkpoint against qualified implementation HEAD `9e65952`.

```text
base HEAD:
  9e65952919f26d7ec62a9e1dd0fbd630b9e56424
status sha256 before this checkpoint note:
  c4540d904cd9c9fe036b92ceeb4ef9c527b87a3072ea28fad5a19b3ebba03dfb
staged dispatch diff sha256:
  b8a072988a7c396055785288a4db2217b6e0f091bc46195d06db3adaf0fea093
checkpoint sha256 before this checkpoint note:
  829f5c0eea12d7c622c2b4ca517227ab25a6789c68f33b615b54c92acfb7fbd1
unstaged and staged diff checks:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or physical process
ran during the dispatch checkpoint. The primary evidence root remains absent.

## Current milestone

**PHASE 08.8 M4.5 — QUALIFIED V8.5 IMPLEMENTATION COMMITTED / ONE FIXED
VISIBLE PRIMARY PROBE DECLARED / DISPATCH CHECKPOINT PASS / DISPATCH COMMIT
PENDING / GAZEBO PROHIBITED.**

## Next criterion

Stage this checkpoint note and checkpoint file, commit the exact dispatch
boundary, and verify a clean tree. Then repeat the fixed preflight and execute
the one installed GUI seed-`19301` attempt without retry or in-run change.

## Phase 08.8 M4.5 fixed v8.5 primary visible probe — 2026-07-31

**FORMAL PASS / INFRASTRUCTURE COMPLETE / STAGE A PASS / EXACT ONE FILL /
ACTIVE-FILL-TRANSIT ESCAPE PASS / STRICT SECOND-CANDIDATE RANKING PASS /
STAGE B PASS / FINAL ZERO PASS / COMPLETE ANALYSIS / CLEANUP PASS.**

The one authorized visible execution ran once from dispatch HEAD `5113e5b`;
seed `19301` was not retried or changed in flight.

```text
scenario:
  phase08_v8_5_primary_visible_probe.yaml
case:
  v8_5_primary_probe_r1p5_a45_h25_19301
run:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_probe/
  2026-07-31/
  20260731T101027547991Z_simulation_phase08_v8_5_primary_visible_probe-v8_5_primary_probe_r1p5_a45_h25_19301-robust__20e2e3be
scenario summary:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_probe/
  scenario_summaries/
  20260731T101026602592Z_phase08_v8_5_primary_visible_probe.yaml
scenario summary sha256:
  d6b0184d89dc768dff3894d74421c616f86bc2b6f8b9225cd909ddf6958d25e7
```

The authoritative state path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Stage A ran from simulation time `0.329 s` through `175.905 s`, within its
fixed `360.0 s` budget. The first candidate was `0.263837 m` from the
declared local; exactly one typed active cluster was created at
`(0.963847, 1.239747) m`; no fill was merged, superseded, rejected, or
escalated.

The v8.5 escape froze the onboard-history continuity vector
`(0.458521, 0.888684)` and selected that exact direct vector with zero
rotation and revision one. The active fill remained active in the typed
registry and modified cost while being excluded only from collision-like
direction eligibility for its own escape; the retained-other-fill count was
zero. Both escape states recorded weights `(0, 1, 1)`. The assisted escape
completed successfully in `29.935893 s` without tangent selection,
reselection, reversal, failsafe, or timeout. On the first returned `SEARCH`
sample the weights were `(1, 1, 0)` and safe-direction validity was false,
proving that affine authority did not persist after recovery.

The second candidate raw-cost interval was
`[-3.8372093023255816, -3.8372093023255816]`, strictly below the first
candidate's retained lower bound `-3.136025629958682`, with margin
`0.7011836723668994`. The controller emitted `GOAL_REACHED` before the first
valid evaluator-only proximity sample at simulation time `300.311 s`,
position `(3.551734, 3.635997) m`, distance `0.145504 m`. Stage B took
`124.406 s`, within its independent `180.0 s` budget. The final retained
distance is `0.145494 m`.

Recording, authoritative Phase 05 completeness, final readiness false,
final-zero commands, and cleanup all pass. There was no in-readiness recenter,
failsafe, timeout, forbidden state/event, or remaining new process. The
analyzer completed with no failures and produced every standard table and all
nine plots. Its three warnings are only the declared assumed fallbacks for
channel index, synchronization tolerance, and supervisor publication rate.

Evidence hashes:

```text
6aa3fc901f5a31354517ba077d44b4bb6e7a18492048f51f6969afdeba3c9e7b  bag
99723594a06b2ba620ddf600eec4231acc9929f3e5351d76ed143cdcaa937a28  completeness
d47cbf8f46f5bf9ec971a5277e2e65ab25a795dbb34498b4226d75a48f6c7bc3  scenario result
57e852481b0449bee876054de47ac97b807f74bb01c9d97f4ebb53f9061d1f27  analysis completeness
202eb994e90e7b9537243dd75d6aad5ad69c67625ae2fb93ce461407f87caf07  summary metrics
```

Complete report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_5_primary_probe.md
SHA-256:
  1bddf399e9394749fc0e2e9d5915daac970cec77feee81a9e833a433127225d7
```

Plot directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_probe/
  2026-07-31/
  20260731T101027547991Z_simulation_phase08_v8_5_primary_visible_probe-v8_5_primary_probe_r1p5_a45_h25_19301-robust__20e2e3be/
  analysis/phase07/plots/
```

The directory contains `trajectory_sources_fills.png`,
`candidate_ranking.png`, `cost.png`, `components.png`, `state_events.png`,
`weights.png`, `command_saturation.png`, `radial_escape.png`, and
`gaussian_history.png`.

This result supports one fixed primary two-source, `400/1600`,
radius-`1.5 m`, angle-`45 deg` open-field case. It is not yet a ten-run
reproducibility, secondary-layout, three-light, or broad arbitrary-layout or
intensity claim.

## Current milestone

**PHASE 08.8 M4.5 — FIXED V8.5 PRIMARY VISIBLE PROBE FORMAL PASS /
RESULT CHECKPOINT PENDING / PRIMARY REPEATS PROHIBITED.**

## Next criterion

Checkpoint and commit this immutable visible-probe result. Then create,
checkpoint, and commit a separate dispatch boundary for the fixed seeds
`19311..19320`. Only that later clean committed boundary may authorize the
headless serial repeat gate. Secondary and broad runs remain prohibited.

## Phase 08.8 M4.5 result-record chronology note — 2026-07-31

The committed M4.5 visible-result material-checkpoint entry appears earlier
in this file, immediately after the historical v8.4 visible result, because a
nonunique append anchor selected that older matching criterion. The checkpoint
content, hashes, committed report, and commit `ae83360` are valid; this note
restores the live append position without rewriting that committed evidence.

## Phase 08.8 M4.6 fixed v8.5 primary-repeat dispatch boundary — 2026-07-31

The immutable passing v8.5 visible result was committed at:

```text
ae83360ae367cd6d86aa9efc831fa4b26caa0056
phase 08.8: retain passing v8.5 primary probe
```

Post-commit verification passes:

```text
worktree:
  clean
matching Gazebo/scenario/recorder/analyzer processes:
  none
repeat evidence root:
  absent
source primary-repeat scenario sha256:
  f8b7be764bb7d7024753cf64b8633944ff70055e9a4a88a97ab8e462b8a5ac6c
installed primary-repeat scenario sha256:
  f8b7be764bb7d7024753cf64b8633944ff70055e9a4a88a97ab8e462b8a5ac6c
source/install parity:
  PASS
installed qualification dry-run:
  10 resolved runs, seeds 19311..19320, zero unsupported cases
dry-run output sha256:
  48737e675da2b27726c0a3ee30f0770f905aef48e9efb0cf43c88dcd4dae17db
```

The passing visible gate proposes this already committed fixed population:

```text
scenario:
  phase08_v8_5_primary_repeats.yaml
case:
  v8_5_primary_repeat_r1p5_a45_h25
seeds:
  19311..19320
resolved runs:
  10
execution:
  serial, headless, stop on first run or cleanup failure
per-run limits:
  540.0 s simulation, 720.0 s wall
outer process timeout:
  8100 s
ROS domain:
  231
evidence root:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_repeats
```

No source, start, source position, intensity, profile value, acceptance
predicate, timeout, seed, cleanup rule, or stop rule may change during this
gate. Each seed may execute at most once and every executed result must be
retained. The first formal behavioral, infrastructure, recording, final-zero,
or cleanup failure closes the population immediately, leaves later seeds
undispatched, and prohibits the secondary campaign. No retry is authorized.

Each executed run must reproduce candidate one, exactly one typed active fill,
the unchanged revision-one direct escape direction through repulse/assist,
completed escape, ordinary affine-free `SEARCH`, strict raw-cost ranking of
candidate two, `GOAL_REACHED`, a later noninterpolated evaluator-only
`0.50 m` proximity sample, final readiness false, final-zero commands,
complete recording, and clean shutdown.

## Current milestone

**PHASE 08.8 M4.6 — FIXED TEN-RUN V8.5 PRIMARY POPULATION DECLARED /
DISPATCH CHECKPOINT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Checkpoint and commit this exact dispatch boundary. Then immediately
reconfirm the clean tree, inactive runtime process set, absent evidence root,
and source/install scenario parity before running the ten seeds serially and
headlessly under the sealed first-failure rule.

## Phase 08.8 M4.6 primary-repeat dispatch checkpoint — 2026-07-31

The fixed ten-run v8.5 population and first-failure dispatch contract received
the required Phase 08 checkpoint against retained visible-result HEAD
`ae83360`.

```text
base HEAD:
  ae83360ae367cd6d86aa9efc831fa4b26caa0056
status sha256 before this checkpoint note:
  f62190e4879689c69393dfa00282107a950d2cc649446dddabc876a1bf8e17db
unstaged dispatch diff sha256:
  64a548e530ea1bc9c818c171457b0a70aa484aad07e10a1db3d97f801623728b
checkpoint sha256 before this checkpoint note:
  b27f465643f7e2b88263f2e972c5f00d9cb70a7a01d5a1cb86947003f86a197a
unstaged and staged diff checks:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or physical process
ran while creating this dispatch checkpoint. The primary-repeat evidence root
remains absent.

## Current milestone

**PHASE 08.8 M4.6 — FIXED TEN-RUN V8.5 PRIMARY POPULATION DECLARED /
DISPATCH CHECKPOINT PASS / DISPATCH COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Stage and commit this exact dispatch boundary. Only that clean committed state
authorizes the sealed ten-run primary gate.

## Phase 08.8 M4.6 fixed v8.5 primary-repeat result — 2026-07-31

**FIXED POPULATION FAIL / FIVE OF SIX DISPATCHED PASS / SEED `19316`
STAGE B FAIL / FOUR LATER SEEDS NOT DISPATCHED / INFRASTRUCTURE COMPLETE /
EVIDENCE AND PLOTS RETAINED.**

The committed headless population ran serially from dispatch HEAD `89946b9`
on ROS domain `231`. Exactly seeds `19311..19316` executed once. Seeds
`19311..19315` passed the complete counted-candidate path, strict
second-candidate ranking, and the `0.50 m` post-recovery evaluator stop. Seed
`19316` passed Stage A, exactly one-fill cardinality, and assisted escape, but
did not find or rank candidate two within its independent `180.0 s` Stage B
budget.

| Seed | Formal result | Stage A (s) | Stage B (s) | Final global distance |
|---:|---|---:|---:|---:|
| 19311 | PASS | 259.525 | 124.882 | 0.147096 m |
| 19312 | PASS | 141.614 | 123.012 | 0.120690 m |
| 19313 | PASS | 191.332 | 134.096 | 0.299232 m |
| 19314 | PASS | 203.921 | 161.602 | 0.164801 m |
| 19315 | PASS | 234.604 | 141.304 | 0.123232 m |
| 19316 | FAIL | 177.532 | 180.030 | 2.149315 m |
| 19317..19320 | NOT DISPATCHED | — | — | — |

The runner stopped at the first formal failure with
`stopped_early_reason: run_failure`; seed `19316` was not retried. Every
recorder returned zero without timeout, authoritative completeness passed,
final-zero and final-readiness-false passed, cleanup passed, and no Gazebo,
scenario, recorder, analyzer, rosbag recorder, or physical process remains.

Retained summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_repeats/
  scenario_summaries/
  20260731T102730662971Z_phase08_v8_5_primary_repeats.yaml
SHA-256:
  b6f563206de201654264de12d2fadf694e0d34f0bf47cac9614271dd479484ea
```

Complete report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_6_primary_repeats.md
SHA-256:
  73fa00d3599085aa22024de761f7f576ea451c32361eac6f2dd82c90943d9543
```

The standard analyzer was executed exactly once for all six retained runs and
produced all nine plots for each. Seeds `19311`, `19313..19316` have complete
analysis with no failures. Seed `19312` remains honestly `partial` with no
analysis failure because one ordinary state sample gap invalidates only the
generic reconstructed state-duration metric; its formal acceptance remains
passed.

The selected v8.5 direction did not change or reverse. For seed `19316`, it
was `(0.485035, 0.874495)`, revision one, with evaluator-only alignment
`+0.943` against the fill-to-global direction. The physical escape-completion
pose was `(0.780608, -0.139229) m`; its radial exit direction had dot product
`-0.925` against the selected direction and `-0.746` against the offline
fill-to-global direction.

The defect is command arbitration. V8.5 adds the oscillatory GESC command and
bounded supervisor direction command before saturation. Across the failed
seed's `2,860` synchronized assist samples:

```text
nonzero supervisor angular request samples:      2,847
|GESC angular| > |supervisor angular| samples:   2,640
combined turn opposite supervisor samples:       1,605
mean |GESC angular request|:                       7.095 rad/s
mean |supervisor angular request|:                 0.398 rad/s
nonzero supervisor linear request samples:        0
```

The GESC angular request kept heading outside the supervisor's drive cone, so
the nominal outward assist supplied no linear translation. The robot escaped
under the competing GESC command on a seed-dependent side of the fill.
Across all six runs, actual exit-direction dot product against the selected
direction ranged from `+0.960` through `-0.925`.

After the wrong-side exit, seed `19316` was not stuck. Ordinary affine-free
search reduced global distance by `1.979 m` in the final `60 s` with path
efficiency `0.912`; the scenario-only Stage B evidence clock expired while it
was still approaching. More time could admit that one trajectory but would
not correct the defeated supervisor direction. The next version must give
the bounded supervisor exclusive command ownership during assist; Stage B
may also be relaxed as evidence slack, not as the primary algorithmic fix.

Failed-seed plot directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_5_primary_repeats/
  2026-07-31/
  20260731T110116556773Z_simulation_phase08_v8_5_primary_repeats-v8_5_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_3d6091a5/
  analysis/phase07/plots/
```

The directory contains `trajectory_sources_fills.png`,
`candidate_ranking.png`, `cost.png`, `components.png`, `state_events.png`,
`weights.png`, `command_saturation.png`, `radial_escape.png`, and
`gaussian_history.png`. Identical plot filenames are retained under every
executed run directory.

This failure closes v8.5. It prohibits the v8.5 secondary probe, secondary
repeats, broad characterization, three-light testing, and physical motion.
It does not modify or relabel the passing visible probe or five passing repeat
runs.

## Current milestone

**PHASE 08.8 M4.6 — FIXED V8.5 PRIMARY POPULATION CLOSED 5/6 /
COMMAND-ARBITRATION DEFECT DIAGNOSED / RESULT CHECKPOINT PENDING /
GAZEBO PROHIBITED.**

## Next criterion

Checkpoint and commit this immutable v8.5 result and diagnosis. Then write and
commit a fresh default-off v8.6 correction amendment before changing code or
dispatching any Gazebo run.

## Phase 08.8 M4.6 v8.5 primary-result checkpoint — 2026-07-31

The immutable fixed-population failure, six retained run artifacts, six
offline analysis bundles, complete report, live status, plot paths, and
command-arbitration diagnosis received the required Phase 08 checkpoint
against dispatch HEAD `89946b9`.

```text
base HEAD:
  89946b9fb1e73386c02bb3584ad9dcca3cbb5b6e
status sha256 before this checkpoint note:
  1bea2465b22c9daaa7a076ba19daa60370bfc4320077bd0e657830e144389439
validation report sha256:
  73fa00d3599085aa22024de761f7f576ea451c32361eac6f2dd82c90943d9543
tracked unstaged diff sha256:
  8b532a901c2063e0068ce640b206f02452f8eae11b39f8cdc0a30fecb353bfb3
combined status-plus-untracked-report diff sha256:
  b153407700ab4e401eeb6654afe3571ab60d4eb627c91d2bc0703c00df0339f8
checkpoint sha256 before this checkpoint note:
  cce50e361b2a394ea32dc020e0966215a52071161668bd2d3cc161b24687afaf
unstaged and staged diff checks:
  PASS
phase context:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or physical process
remained during this result checkpoint.

## Current milestone

**PHASE 08.8 M4.6 — FIXED V8.5 PRIMARY POPULATION CLOSED 5/6 /
COMMAND-ARBITRATION DEFECT DIAGNOSED / RESULT CHECKPOINT PASS /
RESULT COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Stage and commit this exact v8.5 result boundary. Then verify the clean tree
before writing the fresh v8.6 plan amendment.

## Phase 08.8 M4.7 v8.6 correction amendment — 2026-07-31

The fresh v8.6 plan amendment is now written against immutable v8.5 closeout
commit:

```text
99924dc0c52c34590f03a530319f5af99f5c168c
phase 08.8: retain failed v8.5 primary repeats
```

The amendment adds one default-off
`open_field_escape_supervisor_owned_assist_enabled` contract. When enabled,
REPULSE remains GESC-owned, but the existing controller gives the bounded
supervisor command exclusive actuator authority in `ESCAPE_ASSIST`; the GESC
proposal remains computed and recorded but cannot defeat the latched
direction before saturation. Ordinary GESC ownership resumes at the first
post-exit `SEARCH` sample.

Schema v10 adds an explicit `supervisor_owned_escape_assist` result predicate
using recorded supervisor commands, control diagnostics, state, odometry, and
escape events. It must prove command ownership, nonzero bounded linear
assistance, revision-one direction continuity, fill-to-exit alignment of at
least `+0.80`, and complete authority clearing after exit. Extra time alone
cannot pass the predicate.

Fresh staged inputs retain the two fixed `400/1600` layouts and use a relaxed
simulation-only Stage B evidence budget of `300.0 s`, `720.0 s` simulation
run limit, and `900.0 s` wall limit. Physical behavior remains coordinate-free
with manual operator `Ctrl+C`.

The first visible v8.6 probe intentionally reuses deterministic seed `19316`
under a fresh version/schema/root as a regression fixture for the committed
v8.5 command-arbitration failure. Fresh primary repeats use `19411..19420`;
secondary visible/repeats use `19451` and `19461..19465`.

Plan:

```text
docs/codex/gesc_gaussian/plans/phase_08_8_plan.md
SHA-256:
  767e3e8ffb3dbfa6744048ceed275367e3028f4ac647e969c478466f621fa6ec
```

Plan-context validation passes. No production code, interface, launch graph,
scenario input, test, installed artifact, or runtime evidence root has
changed. No Gazebo or physical process is authorized.

## Current milestone

**PHASE 08.8 M4.7 — FRESH V8.6 SUPERVISOR-OWNED ASSIST AMENDMENT
DRAFTED / PLAN CHECKPOINT PENDING / IMPLEMENTATION AND GAZEBO PROHIBITED.**

## Next criterion

Checkpoint and commit the exact v8.6 amendment. Only that clean committed plan
may authorize implementation and no-Gazebo qualification.

## Phase 08.8 M4.7 v8.6 plan checkpoint — 2026-07-31

The fresh supervisor-owned-assist correction amendment received the required
Phase 08 checkpoint against immutable v8.5 result HEAD `99924dc`.

```text
base HEAD:
  99924dc0c52c34590f03a530319f5af99f5c168c
status sha256 before this checkpoint note:
  3d8e660484027b4e0d0983f9d5d267caac5b5bcbce950dae766e1e0ddaf11fb5
active plan sha256:
  767e3e8ffb3dbfa6744048ceed275367e3028f4ac647e969c478466f621fa6ec
unstaged plan/status diff sha256:
  c7089b767f49e96b66251c1898c85bce4532b17fee5f98a554f146a28dc7ee31
checkpoint sha256 before this checkpoint note:
  d6de9137ef56b7487c1a0aa5ce27d06aa69db101dfbdb65c1a5febb40d432cf4
unstaged and staged diff checks:
  PASS
plan context:
  PASS
```

No production code, interface, launch graph, scenario, test, installed
artifact, runtime evidence root, Gazebo process, or physical process changed
during this plan checkpoint.

## Current milestone

**PHASE 08.8 M4.7 — FRESH V8.6 SUPERVISOR-OWNED ASSIST AMENDMENT /
PLAN CHECKPOINT PASS / PLAN COMMIT PENDING / IMPLEMENTATION AND GAZEBO
PROHIBITED.**

## Next criterion

Stage and commit this exact plan boundary, verify the clean tree, and then
begin only the declared implementation and no-Gazebo qualification.

## Phase 08.8 M4.7 v8.6 implementation and no-Gazebo qualification — 2026-07-31

**IMPLEMENTATION QUALIFICATION PASS / BEHAVIOR NOT YET RUN /
GAZEBO PROHIBITED.**

The fresh default-off
`open_field_escape_supervisor_owned_assist_enabled` correction is
implemented through the existing state-machine, supervisor, controller,
central launch, scenario-schema, and scenario-runner owners. No message,
second `/cmd_vel` publisher, pose estimator, planner, source/global
coordinate, evaluator input, Vicon input, room-map input, simulation/physical
algorithm fork, or physical stop was added.

With the switch enabled, repulse remains GESC-owned and zero-supervisor.
After the existing measured stall enters assist, the controller continues to
compute and record the GESC proposal but authorizes the fresh supervisor
command exactly. It never falls back to GESC on an invalid assist input.
Enabled `SEARCH` restores GESC ownership directly from the state boundary so
a delayed assisted command on the separate supervisor topic cannot leak
post-exit. Default-off and every historical path retain the prior
combination rule.

Schema v10 adds the mandatory
`supervisor_owned_escape_assist` predicate for the four v8.6 inputs. The
recorded state, event, supervisor-command, control-diagnostic, and odometry
evidence must prove revision-one direction continuity, exact command
ownership, a nonzero suppressed GESC proposal, positive bounded supervisor
translation, correct saturation, measured fill-to-exit alignment of at least
`+0.80`, and complete post-exit authority clearing.

Read-only replay of the committed failed v8.5 seed-`19316` bag proves:

```text
switch disabled:
  outcome_error=None; no owner-result key
steady assist samples:
  2,860
default-disabled commands equal recorded combined:
  2,860
enabled commands equal supervisor:
  2,860
enabled commands suppress competing nonzero GESC:
  2,860
old v8.5 evidence under the new formal predicate:
  FAIL — GESC leaked into the supervisor-owned command
retained replay:
  /tmp/phase08_8_m4_7_seed19316_replay.log
SHA-256:
  cfe1f3d17245457cc17e458516f3c324887a270f403b273959588bb518c15ff4
```

Final retained tests:

```text
focused controller/supervisor/state/geometry:
  305 passed in 8.35 s
  /tmp/phase08_8_m4_7_focused_controller_final.xml
  cf1545dfd47072e20b1e0da036ef9970dca15637aafd619478f93e4018f984df
focused schema/runner/evidence:
  555 passed, 1 skipped in 125.55 s
  /tmp/phase08_8_m4_7_focused_evidence_final.xml
  8f743f84836158329741945486b1e59b1437a58f92af546608972e1d7cc6b84c
broad ROS-independent:
  866 passed, 2 skipped in 137.56 s
  /tmp/phase08_8_m4_7_broad_functional_final.xml
  a80a7242ca301d8c92fb971a3ed7a87afbecd5ea1414c7d41b051536f46656bb
```

The skips are the unchanged explicit visible/headless Gazebo opt-ins. Fatal
changed-file lint, Python compilation, launch XML and four YAML parses,
historical tracked-scenario bytes, `git diff --check`, context validation,
sole-`/cmd_vel` ownership, and physical/evaluator separation pass.

The fresh isolated build at
`/tmp/phase08_8_v8_6_release_qual.qth8ZZ` finished
`ros_esc_interfaces`, `ros_esc`, and `turtlebot3_rotating_sensor` in
`11.9 s`. Source/install parity is `10/10`. Installed `--show-args`,
`--print-description`, default supervisor, fully enabled v8.6 supervisor,
robust affine modified-cost, and fully enabled controller construction all
pass. All 17 installed dry-run expansions are supported:

```text
primary visible:    1 run,  seed 19316
primary repeats:   10 runs, seeds 19411..19420
secondary visible:  1 run,  seed 19451
secondary repeats:  5 runs, seeds 19461..19465
```

All four v8.6 evidence roots were absent before and after dry-run. V6,
v8-v8.5, all historical scenarios, worlds, failed evidence, bags, plots, and
results remain unchanged and selectable. No Gazebo, scenario, recorder,
analyzer, rosbag recorder, or physical process remains.

Complete qualification:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_7_no_gazebo_qualification.md
```

## Current milestone

**PHASE 08.8 M4.7 — V8.6 IMPLEMENTED / COMPLETE NO-GAZEBO
QUALIFICATION PASS / IMPLEMENTATION CHECKPOINT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Inspect the complete diff, checkpoint Phase 08, and commit the exact qualified
implementation. Then save and commit a separate dispatch boundary authorizing
only the installed visible primary probe at seed `19316`. Do not dispatch
primary repeats or either secondary case.

## Phase 08.8 M4.7 v8.6 implementation checkpoint — 2026-07-31

The complete qualified v8.6 implementation, schema-v10 evidence predicate,
four fixed inputs, final test records, isolated build, installed graph,
dry-run summaries, compatibility evidence, and no-Gazebo qualification
received the required Phase 08 checkpoint against immutable v8.6 plan HEAD
`d389a01`.

```text
base HEAD:
  d389a01fbcb4fb1f30c02ed0cf8b41e42492dc27
status sha256 before this checkpoint note:
  3da63a130cd7ad1cb8b5be15948fc8a60baad4957b97b0e44fd6ed10b4b2fa3f
active plan sha256:
  767e3e8ffb3dbfa6744048ceed275367e3028f4ac647e969c478466f621fa6ec
qualification report sha256:
  8eaa5efe00a232fd0df81a1128ae909a3d97c6fc1bc898f1d423e80bec913ca5
unstaged tracked diff sha256:
  845491eadfc360faac239c24ddd9c68fc269b5661281615700523dd71f039d36
checkpoint sha256 before this checkpoint note:
  271a6d67d366a2128638a11341b80db6a73fa62af8c37d38e00eb9e495bf32ac
unstaged and staged diff checks:
  PASS
phase context:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or physical process
remained during this implementation checkpoint. All four fresh v8.6 run
roots remain absent.

## Current milestone

**PHASE 08.8 M4.7 — V8.6 IMPLEMENTED / COMPLETE NO-GAZEBO
QUALIFICATION PASS / IMPLEMENTATION CHECKPOINT PASS / IMPLEMENTATION
COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Stage and commit this exact qualified v8.6 implementation boundary. Verify a
clean tree, then write, checkpoint, and commit a separate dispatch boundary
authorizing only the installed visible primary seed-`19316` probe. Do not
dispatch primary repeats or either secondary case.

## Phase 08.8 M4.7 v8.6 visible-dispatch boundary — 2026-07-31

The exact qualified v8.6 implementation was committed at:

```text
fb3c2648adca4931471d68b502cf8bf7f2fc9827
phase 08.8: qualify v8.6 supervisor-owned assist
```

Post-commit preflight passes:

```text
worktree:
  clean
phase context:
  PASS
primary visible evidence root:
  absent
matching Gazebo/scenario/recorder/analyzer processes:
  none
DISPLAY:
  :0
xdpyinfo:
  PASS
source primary-visible scenario sha256:
  47faf45f4cd1464dde02e727ea4cfcfc7b7dd77139ac4a355a2366e229884fc9
installed primary-visible scenario sha256:
  47faf45f4cd1464dde02e727ea4cfcfc7b7dd77139ac4a355a2366e229884fc9
source/install parity:
  PASS
```

This record proposes exactly one installed GUI execution:

```text
scenario:
  phase08_v8_6_primary_visible_probe.yaml
case:
  v8_6_primary_probe_r1p5_a45_h25_19316
seed:
  19316
profile:
  robust_gaussian_v1
ROS domain:
  230
execution:
  serial, Gazebo GUI visible, one attempt, no retry
scenario run timeout:
  720.0 s
scenario wall timeout:
  900.0 s
outer process timeout:
  1080 s, INT then 60 s kill-after
evidence root:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_6_primary_probe
```

No source, start, source position, intensity, profile value, acceptance
predicate, timeout, seed, cleanup rule, or stop rule may change during the
attempt. The fixed run must demonstrate candidate one, exactly one typed
active fill, one latched direction at revision one, `ESCAPE_STALLED`,
supervisor-owned assisted control with a nonzero suppressed GESC proposal,
positive bounded supervisor translation, measured fill-to-exit alignment of
at least `+0.80`, completed local escape, ordinary affine-free `SEARCH`,
strict raw-cost ranking of candidate two, `GOAL_REACHED`, a later
evaluator-only `0.50 m` simulation proximity sample, final readiness false,
final zero, complete recording, and clean shutdown.

The run must be analyzed exactly once after recording closes and must produce
all nine standard plots:

```text
trajectory_sources_fills.png
candidate_ranking.png
cost.png
components.png
state_events.png
weights.png
command_saturation.png
radial_escape.png
gaussian_history.png
```

Any behavioral, formal ownership, recording, final-zero, cleanup, or
infrastructure failure closes v8.6 immediately. The attempt is retained
regardless of outcome and cannot be retried. Primary repeats, the secondary
probe, secondary repeats, broader characterization, three lights, physical
motion, and Phase 09 remain prohibited.

## Current milestone

**PHASE 08.8 M4.7 — QUALIFIED V8.6 IMPLEMENTATION COMMITTED / ONE FIXED
VISIBLE PRIMARY PROBE DECLARED / DISPATCH CHECKPOINT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Checkpoint and commit this exact status plus checkpoint dispatch boundary.
Then immediately reconfirm the clean tree, inactive runtime process set,
absent evidence root, installed scenario parity, and GUI display before
executing the one authorized seed-`19316` visible probe.

## Phase 08.8 M4.7 v8.6 visible-dispatch checkpoint — 2026-07-31

The one-attempt visible dispatch contract received the required Phase 08
checkpoint against qualified implementation HEAD `fb3c264`.

```text
base HEAD:
  fb3c2648adca4931471d68b502cf8bf7f2fc9827
status sha256 before this checkpoint note:
  44cf34937b3b5be5b0a65c4710b8fb3de19dee3d63ada9dd9a0890e8bc82da69
unstaged dispatch diff sha256:
  c64190f20b48d475d5283f24c7e5ce9c1a6cdb6cedbf1120ab65e616b138c368
checkpoint sha256 before this checkpoint note:
  f5d8c5c04e823451c48392b7b3c803ea1ee0132b835024ced077f472aec7f15f
unstaged and staged diff checks:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or physical process
ran during the dispatch checkpoint. The primary evidence root remains absent.

## Current milestone

**PHASE 08.8 M4.7 — QUALIFIED V8.6 IMPLEMENTATION COMMITTED / ONE FIXED
VISIBLE PRIMARY PROBE DECLARED / DISPATCH CHECKPOINT PASS / DISPATCH
COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Stage this checkpoint note and checkpoint file, commit the exact dispatch
boundary, and verify a clean tree. Then repeat the fixed preflight and execute
the one installed GUI seed-`19316` attempt without retry or in-run change.

## Phase 08.8 M4.7 fixed v8.6 primary visible result — 2026-07-31

**FORMAL PASS / SUPERVISOR-OWNED EXIT PASS / STAGE B PASS /
INFRASTRUCTURE COMPLETE / ALL NINE PLOTS RETAINED.**

The one committed visible seed-`19316` attempt ran exactly once from dispatch
HEAD `378804f` on ROS domain `230` with Gazebo GUI enabled. It was not retried
or changed in flight.

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_6_primary_probe/
  2026-07-31/
  20260731T122710523689Z_simulation_phase08_v8_6_primary_visible_probe-
  v8_6_primary_probe_r1p5_a45_h25_19316-robust__c4156158
```

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_6_primary_probe/
  scenario_summaries/
  20260731T122709562239Z_phase08_v8_6_primary_visible_probe.yaml
SHA-256:
  de5b739c2aeb57750655c391dd427b25fef54f80a30cd7de1d8c5ac9d1fdfdb3
```

All required predicates pass:

```text
recording_complete:                 true
cleanup_complete:                   true
controller_goal:                    true
ground_truth_goal:                  true
expected_terminal_state:            true
required_state_path:                true
required_events:                    true
required_event_sequence:            true
no_forbidden_states:                true
no_forbidden_events:                true
local_recovery_stage:               true
supervisor_owned_escape_assist:     true
post_recovery_global_proximity:     true
fill_cardinality:                   true
```

The exact state path is:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Stage A completed at simulation time `184.532 s`, within `360.0 s`, with one
local candidate, exactly one typed revision-one fill, no merge or
supersession, and no recenter/failsafe/timeout. The selected direct
onboard-history direction was `(0.752446653, 0.658653198)`, revision one.

The formal v8.6 command-owner evidence is:

```text
evaluated assist control samples:      1,876
fresh matching supervisor commands:    1,876
nonzero GESC proposals suppressed:     1,876
positive supervisor linear samples:    1,876
measured fill-to-exit distance:         1.478864 m
selected/actual-exit alignment:         0.999977987
post-exit supervisor zero:              PASS
post-exit ordinary GESC ownership:      PASS
```

Candidate two's strict raw interval was
`[-3.8372093023255816, -3.8372093023255816]`, below candidate one's retained
lower bound `-2.8453728221821186` by `0.9918364801434629`. `GOAL_REACHED`
preceded the evaluator sample at simulation time `291.530 s`,
`(3.607557, 3.569383) m`, `0.127995 m` from the declared global. Stage B
took `106.998 s`, within `300.0 s`. Final retained distance is `0.127973 m`.

The record process returned zero without timeout. Authoritative completeness,
final readiness false, final commands zero, and cleanup pass with no
remaining node or process.

Offline analysis ran exactly once and returned zero. It produced every
expected table and all nine plots with `analysis_failures=[]`. The summary
status is honestly `partial` only because the optional generic state-duration
metric invalidated itself for three isolated pre-Stage-A `SEARCH` sample
gaps (`0.220447 s`, `0.162486 s`, and `0.338401 s`). No critical input,
formal state, acceptance event, command-owner sample, terminal evidence, or
plot is missing. The active plan now clarifies that a complete analysis
bundle means successful analyzer completion, all expected artifacts and
plots, and no analysis failure; optional generic metrics do not become
unstated formal predicates.

Plot directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_6_primary_probe/
  2026-07-31/
  20260731T122710523689Z_simulation_phase08_v8_6_primary_visible_probe-
  v8_6_primary_probe_r1p5_a45_h25_19316-robust__c4156158/
  analysis/phase07/plots/
```

It contains `trajectory_sources_fills.png`, `candidate_ranking.png`,
`cost.png`, `components.png`, `state_events.png`, `weights.png`,
`command_saturation.png`, `radial_escape.png`, and
`gaussian_history.png`.

Complete report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_7_primary_probe.md
```

The evaluator coordinate was used only for the post-ranked simulation stop.
Physical behavior remains coordinate-free and operator-stopped with
`Ctrl+C`. No physical process ran.

This one pass does not authorize immediate repeat execution. The result,
analysis clarification, report, status, and checkpoint must be committed,
then a separate fixed ten-run primary-repeat dispatch boundary must be
checkpointed and committed.

## Current milestone

**PHASE 08.8 M4.7 — FIXED V8.6 PRIMARY VISIBLE PROBE PASS / FORMAL
COMMAND OWNER PASS / ALL NINE PLOTS RETAINED / RESULT CHECKPOINT PENDING /
GAZEBO PROHIBITED.**

## Next criterion

Checkpoint and commit this immutable visible result and analysis-bundle
clarification. Then write, checkpoint, and commit a separate dispatch boundary
for exactly seeds `19411..19420`, serial/headless, stop on first failure, no
retry. Do not dispatch the secondary probe or repeats.

## Phase 08.8 M4.7 v8.6 primary-visible result checkpoint — 2026-07-31

The immutable one-attempt visible pass, formal command-owner evidence,
complete nine-plot analysis bundle, honestly partial optional metric, report,
plan clarification, and live status received the required Phase 08 checkpoint
against dispatch HEAD `378804f`.

```text
base HEAD:
  378804f529ec900fa90b9f5c7ac2e118dc58d81f
status sha256 before this checkpoint note:
  1c2588033a3e933ac0ae5b0e00530f7da0dad6afc3236a704b4779ed6a995d7b
active plan sha256:
  0e1494c96dfab88bf0c2640b1a1abfdaf5d976bd11be25f4c74ff593458404e9
visible report sha256:
  04779e0b6b6dda9176d296a84c80498328c39f4f3e7c5bfd09a6b0777c765f5b
unstaged tracked diff sha256:
  b87be7794234dfa27f2eb1e7ee08d08b622831a6203e2f72c8ec3c2f631c8d46
checkpoint sha256 before this checkpoint note:
  87bcb5666de7eb5677b7357dbc11e54e02ef85b1bd04da1d347994ffdffd21d8
unstaged and staged diff checks:
  PASS
phase context:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or physical process
remained during this result checkpoint.

## Current milestone

**PHASE 08.8 M4.7 — FIXED V8.6 PRIMARY VISIBLE PROBE PASS / FORMAL
COMMAND OWNER PASS / ALL NINE PLOTS RETAINED / RESULT CHECKPOINT PASS /
RESULT COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Stage and commit this exact visible-result boundary. Verify a clean tree, then
write, checkpoint, and commit a separate fixed primary-repeat dispatch
boundary for exactly seeds `19411..19420`, serial/headless, stop on first
failure, no retry. Do not dispatch the secondary probe or repeats.

## Phase 08.8 M4.7 fixed v8.6 primary-repeat dispatch boundary — 2026-07-31

The immutable passing visible result and analysis clarification were committed
at:

```text
56ad1de603e7b1965b8cdc1d5af75a2e3489c469
phase 08.8: retain passing v8.6 primary probe
```

Post-commit preflight passes:

```text
worktree:
  clean
phase context:
  PASS
primary-repeat evidence root:
  absent
matching Gazebo/scenario/recorder/analyzer processes:
  none
source primary-repeat scenario sha256:
  641e60c3382afca6b3f499bd1f8abc6609df30eb2dfbbc20793dbfaabab57efe
installed primary-repeat scenario sha256:
  641e60c3382afca6b3f499bd1f8abc6609df30eb2dfbbc20793dbfaabab57efe
source/install parity:
  PASS
```

This boundary proposes exactly one installed serial/headless population:

```text
scenario:
  phase08_v8_6_primary_repeats.yaml
case:
  v8_6_primary_repeat_r1p5_a45_h25
seeds:
  19411, 19412, 19413, 19414, 19415,
  19416, 19417, 19418, 19419, 19420
profile:
  robust_gaussian_v1
ROS domain:
  228
execution:
  serial, Gazebo headless, one attempt per dispatched seed, no retry
stop policy:
  stop on first run or cleanup failure; later seeds are not dispatched
per-run simulation timeout:
  720.0 s
per-run wall timeout:
  900.0 s
outer population timeout:
  9,600 s, INT then 60 s kill-after
evidence root:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_6_primary_repeats
```

No source, start, light position, intensity, seed, profile value, acceptance
predicate, evidence budget, cleanup rule, or stop rule may change after
dispatch. Every executed run must pass the complete visible-probe contract,
including exactly one fill, revision-one direction, supervisor-owned assist,
positive translation, exit alignment at least `+0.80`, strict second-candidate
raw ranking, later evaluator-only `0.50 m` proximity, final zero, readiness
false, complete recording, and clean shutdown.

After the population closes, the standard analyzer may run exactly once for
each dispatched run. All outputs, including a first failure and any optional
metric limitation, are retained honestly. No failed seed is retried.

Only a formal `10/10` result may authorize the v8.6 secondary visible probe.
The secondary probe, secondary repeats, broader characterization, three
lights, physical motion, and Phase 09 remain prohibited during this
population.

## Current milestone

**PHASE 08.8 M4.7 — PASSING V8.6 PRIMARY PROBE COMMITTED / FIXED TEN-RUN
PRIMARY POPULATION DECLARED / REPEAT DISPATCH CHECKPOINT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Checkpoint and commit this exact status plus checkpoint repeat-dispatch
boundary. Then reconfirm the clean tree, inactive runtime process set, absent
evidence root, and installed scenario parity before executing the one fixed
serial/headless population.

## Phase 08.8 M4.7 v8.6 primary-repeat dispatch checkpoint — 2026-07-31

The sealed ten-run primary-repeat dispatch boundary received the required
Phase 08 checkpoint against visible-result HEAD `56ad1de`.

```text
base HEAD:
  56ad1de603e7b1965b8cdc1d5af75a2e3489c469
status sha256 before this checkpoint note:
  fe4915d110b759c1668bcedfb28a2a5407cbef1716e46e9415d4469f205dbf7a
active plan sha256:
  0e1494c96dfab88bf0c2640b1a1abfdaf5d976bd11be25f4c74ff593458404e9
unstaged tracked diff sha256:
  b871122c629d0267f3f85b89996ad0d6ff6c96562c2cb9a67c98500c37effe4c
checkpoint sha256 before this checkpoint note:
  deca2e43ee5e7db62085d4f0ced3f2beed3f593d06950ceb3db701b21db8e4dd
unstaged and staged diff checks:
  PASS
phase context:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or physical process
ran during this checkpoint.

## Current milestone

**PHASE 08.8 M4.7 — PASSING V8.6 PRIMARY PROBE COMMITTED / FIXED TEN-RUN
PRIMARY POPULATION DECLARED / REPEAT DISPATCH CHECKPOINT PASS / DISPATCH
COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Stage and commit exactly this status plus checkpoint boundary. Then reconfirm
the clean tree, inactive runtime process set, absent evidence root, and
installed scenario parity before executing the one fixed serial/headless
population. Do not dispatch the secondary probe or repeats.

## Phase 08.8 M4.7 fixed v8.6 primary-repeat disposition — 2026-07-31

Dispatch boundary commit:

```text
4207b73 phase 08.8: authorize v8.6 primary repeats
```

The sealed population stopped after seed `19411`, exactly as required. Seed
`19411` was not retried, and seeds `19412..19420` were not dispatched.
Runner return code was `1`; the outer `9,600 s` timeout did not fire.

The run completed the intended behavior:

```text
record process:                         return 0 / no timeout
recording completeness:                 PASS
state path:                              SEARCH -> VERIFY -> DESIGN ->
                                         REPULSE -> ASSIST -> SEARCH ->
                                         VERIFY -> GOAL_HOLD
Stage A:                                 PASS at 228.826 s
fill cardinality:                        exactly one
direction revision:                      one
selected/actual-exit alignment:          0.994041292
assist control samples:                  2,769
fresh supervisor matches:                2,769
nonzero GESC proposals suppressed:       2,769
positive supervisor-linear samples:      2,058
strict candidate separation margin:      0.9918364801434629
GOAL_REACHED:                            PASS
evaluator proximity:                     0.123633 m at 339.224 s
Stage B:                                 110.398 s / 300.0 s
FAILSAFE/TIMEOUT:                        absent
final readiness false / commands zero:   PASS
```

It failed two of fourteen mandatory predicates:

```text
supervisor_owned_escape_assist:  FAIL
cleanup_complete:                FAIL
```

The ownership failure was one cross-topic delivery-order sample. The first
post-exit `SEARCH` state was recorded at `1785501942470570252`; zero
supervisor command followed `0.777583 ms` later. One diagnostic `0.554917 ms`
after that zero publication still reflected the prior assist command. The
next diagnostic, `6.363998 ms` later, had combined command equal to GESC and
zero supervisor contribution. All `13,069` subsequent diagnostics through
the next state transition retained ordinary GESC ownership.

The cleanup audit found no session process but did find
`/_ros2cli_282407`. This was the external `ros2 topic echo --once` progress
monitor issued on ROS domain `228` during the active sealed run. The runner
correctly treated it as graph contamination. No future sealed run may be
monitored by joining its ROS domain; use retained files and process state
only. The cleanup predicate remains mandatory and unchanged.

The standard analyzer ran exactly once after closure, returned zero, produced
all expected tables and all nine plots, and reported
`analysis_failures=[]`. Its `partial` summary is limited to one optional
generic state-duration gap above `0.150 s`.

Retained evidence:

```text
run:
  /home/mattb/Experiments/GESC-Gaussian/runs/
    phase08_8_6_primary_repeats/2026-07-31/
    20260731T124148715876Z_simulation_phase08_v8_6_primary_repeats-
    v8_6_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_35b235c3
scenario summary:
  /home/mattb/Experiments/GESC-Gaussian/runs/
    phase08_8_6_primary_repeats/scenario_summaries/
    20260731T124147695682Z_phase08_v8_6_primary_repeats.yaml
report:
  docs/codex/gesc_gaussian/validation/
    phase_08_8_m4_7_primary_repeats.md
plots:
  <run>/analysis/phase07/plots/
```

The fixed v8.6 repeat gate is closed at `0/1` formal passes with one of ten
declared seeds dispatched. Its secondary and broader gates were not
dispatched. This does not alter the independent passing v8.6 visible result
or any historical evidence.

## Current milestone

**PHASE 08.8 M4.7 — FIXED V8.6 PRIMARY REPEAT GATE CLOSED FAIL / BEHAVIORAL
OBJECTIVE REACHED / FORMAL HANDOFF AND CLEANUP FAILURES RETAINED / FAILURE
CHECKPOINT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Checkpoint and commit the immutable v8.6 primary-repeat failure evidence.
Then review and commit a separately versioned correction plan. Do not retry
seed `19411`; do not dispatch v8.6 seed `19412` or any later v8.6 gate.

## Phase 08.8 M4.7 v8.6 primary-repeat failure checkpoint — 2026-07-31

The immutable stopped population, one retained behavioral success/formal
failure, one-time analysis, complete plot bundle, diagnosis, report, and live
status received the required Phase 08 checkpoint against dispatch HEAD
`4207b73`.

```text
base HEAD:
  4207b73fa900b941026fa30c75461b412a9fa89b
status sha256 before this checkpoint note:
  c9c7d157854482828a870ecd919669ec96dcbbdc2c9d8c6cedb49587f9687a25
active plan sha256:
  0e1494c96dfab88bf0c2640b1a1abfdaf5d976bd11be25f4c74ff593458404e9
failure report sha256:
  3653b165038b6e80cc40bd56d3b6c1a11a4d16feee1b0a21b0ddc3f74979ccbc
unstaged tracked diff sha256:
  49b7c22f0c2e4b11a5966c7a61f3146883e0bd714ea57af825871f70814e4aa5
checkpoint sha256 before this checkpoint note:
  5f77fd1abefee271ba3c57d2467202746e7a23a0c76e7a281de757e73e735c12
unstaged and staged diff checks:
  PASS
phase context:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or physical process
remained during this failure checkpoint.

## Current milestone

**PHASE 08.8 M4.7 — FIXED V8.6 PRIMARY REPEAT GATE CLOSED FAIL / BEHAVIORAL
OBJECTIVE REACHED / FORMAL HANDOFF AND CLEANUP FAILURES RETAINED / FAILURE
CHECKPOINT PASS / FAILURE COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Stage and commit exactly this failure boundary. Then review and commit a
separately versioned correction plan. Do not retry seed `19411`; do not
dispatch v8.6 seed `19412` or any later v8.6 gate.

## Phase 08.8 M4.8 v8.7 correction plan — 2026-07-31

The fixed v8.6 primary-repeat failure was committed at:

```text
e9dbc23 phase 08.8: retain failed v8.6 primary repeats
```

The active Plan now defines v8.7 as a fresh evidence-causality correction.
It changes no controller motion, source layout, intensity, detector, fill,
affine, candidate ranking, timeout, final-zero, or cleanup behavior.

Schema v11 retains the predicate name
`supervisor_owned_escape_assist` but replaces the cross-topic publication
order assumption with a bounded causal handoff proof:

```text
handoff deadline:                       0.15 s
allowed pre-handoff diagnostic:         finite ordinary, zero/failsafe, or
                                        the final proven assist command
forbidden:                              GESC leak, arbitrary command,
                                        bad arithmetic/saturation,
                                        nonzero later supervisor command
required after handoff:                 every diagnostic through the next
                                        state remains ordinary GESC
schema <=10 behavior:                   unchanged
```

The fresh v8.7 scenarios use seeds `19501`, `19511..19520`, `19551`, and
`19561..19565`. All v8.6 controller and evaluator inputs are otherwise
unchanged.

Sealed-run monitoring is also corrected operationally: no ROS CLI or other
DDS participant may join the active run domain. Progress inspection is
limited to process state and retained files. Cleanup remains strict and gains
no node allowlist.

## Current milestone

**PHASE 08.8 M4.8 — V8.6 FAILURE COMMITTED / V8.7 CAUSAL HANDOFF AND
UNCONTAMINATED EXECUTION PLAN WRITTEN / PLAN COMMIT PENDING / NO-GAZEBO
QUALIFICATION PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit the v8.7 Plan amendment. Then implement schema-v11 evidence and fresh
scenarios, qualify entirely without Gazebo, checkpoint, and commit before any
new runtime dispatch.

## Phase 08.8 M4.8 v8.7 correction-plan checkpoint — 2026-07-31

The separately versioned causal-handoff and uncontaminated-execution Plan
amendment received the required Phase 08 checkpoint against immutable v8.6
failure HEAD `e9dbc23`.

```text
base HEAD:
  e9dbc237a73e410015520ca1521a7babe869658a
status sha256 before this checkpoint note:
  826daa6f019cc484c23c90db14e30397e879fab8a04bc2f20d18f619ced201b1
active plan sha256:
  8c063ed44514bd9a84e0601f5cb73e56aeecabddce7cabda0d6c65fe80077694
unstaged tracked diff sha256:
  debeb68915684b00d5ed3aa202e297c7a6e6d128e8ce23fd8b8ca9892ff86582
checkpoint sha256 before this checkpoint note:
  be162ea06f839a3721f3f35a57c2b35ea74440b8aa3a8abf812d9986ced24d06
unstaged and staged diff checks:
  PASS
phase context:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or physical process
ran during this Plan checkpoint.

## Current milestone

**PHASE 08.8 M4.8 — V8.6 FAILURE COMMITTED / V8.7 CAUSAL HANDOFF AND
UNCONTAMINATED EXECUTION PLAN CHECKPOINT PASS / PLAN COMMIT PENDING /
NO-GAZEBO QUALIFICATION PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact Plan boundary. Then implement schema-v11 evidence and fresh
scenarios, qualify entirely without Gazebo, checkpoint, and commit before any
new runtime dispatch.

## Phase 08.8 M4.8 v8.7 no-Gazebo qualification — 2026-07-31

The evidence-only v8.7 correction and four fresh fixed inputs are implemented
and qualified without Gazebo.

Schema v11 retains every schema-v10 assisted-escape ownership requirement and
adds one evaluator-only field:

```text
supervisor_owned_assist_handoff_timeout_sec: 0.15
```

The post-exit predicate now validates the complete returned-`SEARCH`
interval. Every state must have weights `(1,1,0)` and no escape authority;
every supervisor publication must be finite zero; every diagnostic must have
valid contribution arithmetic and saturation. Before ordinary GESC ownership
is causally observed, only ordinary GESC, zero/failsafe, or the final fresh
assist command already proven by pre-exit control evidence is accepted.
Ordinary ownership must occur within `0.15 s` and may never revert.

Schema versions through v10 retain the original first-sample branch.
Controller, supervisor, detector, fill, modified-cost, launch, world, motion,
source, ranking, timeout, final-zero, and cleanup behavior are unchanged.

The immutable seed-`19411` v8.6 bag was replayed read only:

```text
schema v10:
  false
  post-exit SEARCH did not restore ordinary GESC ownership
schema v11:
  true
recognized transition samples:
  1
handoff delay:
  0.007696498 s
handoff deadline:
  0.15 s
ordinary diagnostics in complete recorded SEARCH interval:
  13,109
outcome_error:
  null
log:
  /tmp/phase08_8_m4_8_seed19411_causal_replay.log
SHA-256:
  87072d0f2826605356e849f4e38b70b15a96cf07ffad09e82cd7da80183d00de
```

Whole-document pair normalization proves each fresh v8.7 scenario is equal
to its v8.6 parent after removing only the declared schema/evidence field,
version identities, root, descriptions, and seeds. Source geometry and
intensities, start, all launch inputs, the one-fill/two-source contract,
budgets, simulation stop, final-zero, cleanup, and first-failure rules are
unchanged.

Fresh inputs:

```text
f654f51a3cc445359b1f94c81512f25471d0c388267126bd8923791a1d2b542b
  phase08_v8_7_primary_repeats.yaml
5c5f40dd77005fea3f44faa1c7f425e709b245ffcd1279f9f7979505d3059910
  phase08_v8_7_primary_visible_probe.yaml
f555b99f892746a9898f9c71c5c428cf2c018ebdca15d9a83deddb764ec2cc8b
  phase08_v8_7_secondary_repeats.yaml
1424eb1ca3823f6481eac46481a7aa08a2480331e4e653313becac44702dba83
  phase08_v8_7_secondary_visible_probe.yaml
```

Final no-Gazebo evidence:

```text
focused controller/supervisor/detector/geometry/legacy:
  305 passed in 8.44 s
focused schema/runner/validator/analyzer/recording:
  582 passed, 1 skipped in 126.91 s
broad ROS-independent:
  893 passed, 3 skipped in 146.61 s
complete schema/runner:
  296 passed, 1 skipped in 55.76 s
fatal changed-file lint:
  PASS
changed-Python compilation:
  PASS
XML and four YAML parses:
  PASS
Phase 08 implementation context:
  PASS
git diff --check:
  PASS
```

The focused skip and two broad runtime skips are unchanged explicit Gazebo
opt-ins. The additional broad skip is the repository copyright-template
check. There are no failures or errors.

A fresh isolated release build at:

```text
/tmp/phase08_8_v8_7_release_qual.krosar
```

finished all three packages in `14.6 s`. Source/install parity passes for
`10/10` owners. Default supervisor, fully enabled counted-source supervisor
with exact one-fill cardinality, robust affine modified-cost, and robust
controller all constructed from the install on isolated ROS domain `230` and
reached the expected bounded timeout `124`.

All four installed dry-runs resolve the sealed `1 + 10 + 1 + 5` cases with
zero unsupported cases and create no run root. The enabled supervisor-owner
switch appears in every launch/record command. The evaluator-only handoff
timeout appears in none.

The complete durable record is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_8_no_gazebo_qualification.md
```

Historical scenarios, V6, worlds, results, bags, plots, and fixed failures
are unchanged. No Gazebo, scenario, recorder, analyzer, rosbag recorder, or
physical process ran during qualification. At close, all v8.7 run roots are
absent and no runtime process is active.

Bounded corrections retained in the report include causal fixture repairs,
advancing the unsupported-schema test from 11 to 12, strengthening the held
tail to require a pre-exit proven command, correcting a pre-build shell
wrapper, and supplying the omitted exact one-fill parameter to the installed
construction probe. Every final gate passes.

## Current milestone

**PHASE 08.8 M4.8 — V8.7 SCHEMA-V11 CAUSAL HANDOFF IMPLEMENTED /
NO-GAZEBO QUALIFICATION PASS / IMPLEMENTATION CHECKPOINT PENDING /
GAZEBO PROHIBITED.**

## Next criterion

Run the Phase 08 material-boundary checkpoint and commit exactly the qualified
implementation, four fixed inputs, report, status, and checkpoint. Then write,
checkpoint, and commit a separate visible-dispatch boundary before executing
the installed primary visible seed `19501` once. Do not join the sealed run's
ROS domain.

## Phase 08.8 M4.8 v8.7 implementation checkpoint — 2026-07-31

The complete schema-v11 implementation, causal replay, four fixed v8.7
inputs, no-Gazebo qualification, report, and live status received the required
Phase 08 material-boundary checkpoint against Plan HEAD `b8c11f1`.

```text
base HEAD:
  b8c11f162d34383691f1c1e025394bca4e071e19
status sha256 before this checkpoint note:
  3fca103f8b3580b51b3b50de5b66e7b1938ff9f9014a6f41fe0d54968bbc21f2
active plan sha256:
  8c063ed44514bd9a84e0601f5cb73e56aeecabddce7cabda0d6c65fe80077694
qualification report sha256:
  42c6e51f0e5fabe625e0c51f5de14f4e41ffcc4638c15dc984ed8f3e9b2121bb
unstaged tracked diff sha256:
  b63c6b3fa2a643a8c407e3cf8c00707e443e84cbf14e9bd4adf6e4d40c81e60c
checkpoint sha256 before this checkpoint note:
  f1d2e6498c646f51ba90d4e9cdfa13043b3aed94c6d4fed7d0bda776a8a96711
unstaged and staged diff checks:
  PASS
phase context:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or physical process
ran during this checkpoint. All four v8.7 run roots remain absent.

## Current milestone

**PHASE 08.8 M4.8 — V8.7 SCHEMA-V11 CAUSAL HANDOFF IMPLEMENTED /
NO-GAZEBO QUALIFICATION PASS / IMPLEMENTATION CHECKPOINT PASS /
IMPLEMENTATION COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Stage and commit exactly this qualified implementation boundary. Then create,
checkpoint, and commit a separate visible-dispatch authority before executing
installed primary visible seed `19501` once without any ROS-domain monitor.

## Phase 08.8 M4.8 v8.7 primary-visible dispatch boundary — 2026-07-31

The qualified v8.7 implementation is committed:

```text
2391133 phase 08.8: qualify v8.7 causal handoff evidence
```

The only next runtime authorized is the installed, visible, single-run
primary probe:

```text
install:
  /tmp/phase08_8_v8_7_release_qual.krosar/install
scenario:
  <install>/ros_esc/share/ros_esc/scenario_runner/scenarios/
    phase08_v8_7_primary_visible_probe.yaml
scenario SHA-256:
  5c5f40dd77005fea3f44faa1c7f425e709b245ffcd1279f9f7979505d3059910
case:
  v8_7_primary_probe_r1p5_a45_h25_19501
seed:
  19501
GUI:
  visible
ROS_DOMAIN_ID:
  231
ROS_LOCALHOST_ONLY:
  1
outer timeout:
  1050 s, INT then 30 s kill bound
dispatch log:
  /tmp/phase08_8_m4_8_v8_7_primary_probe_dispatch.log
```

The run executes once with no retry and no parameter change. No `ros2 topic`,
`ros2 node`, `ros2 service`, `ros2 param`, RViz, plotter, or other DDS
participant may join domain `231` while the sealed run is active. Progress
inspection is limited to the dispatch process, console file, run-directory
creation, bag-file growth, and final scenario summary.

The runner retains strict graph and session-process cleanup. No node allowlist
or cleanup exception exists. The run must pass every v8.6 behavioral
predicate, schema-v11 causal ownership, complete recording, final readiness
false, final zero, and uncontaminated cleanup. The standard analyzer may run
exactly once only after the sealed run is fully closed.

At this boundary:

```text
branch:
  feature/gesc-gaussian-robustness-v1
HEAD:
  2391133
worktree:
  clean before this status amendment
active Gazebo/scenario/recorder/analyzer:
  none
primary v8.7 run root:
  absent
```

## Current milestone

**PHASE 08.8 M4.8 — V8.7 IMPLEMENTATION COMMITTED / PRIMARY VISIBLE
SEED 19501 DISPATCH BOUNDARY WRITTEN / DISPATCH CHECKPOINT PENDING /
GAZEBO NOT YET STARTED.**

## Next criterion

Checkpoint and commit this exact dispatch boundary. Then execute the installed
visible primary probe once. Do not join ROS domain `231`. A formal failure
closes the visible gate; a pass must be analyzed once, produce all nine plots,
and be checkpointed and committed before any primary repeat dispatch.

## Phase 08.8 M4.8 v8.7 primary-visible dispatch checkpoint — 2026-07-31

The exact single-run primary-visible authority received the required Phase 08
checkpoint against qualified implementation HEAD `2391133`.

```text
base HEAD:
  2391133c32c00a74149d0eeaab7ac62efcf7aa4e
status sha256 before this checkpoint note:
  e4ae19bb37a4230d06fad9140aa850401fd872d826491780c2a0cc097f77d581
active plan sha256:
  8c063ed44514bd9a84e0601f5cb73e56aeecabddce7cabda0d6c65fe80077694
unstaged tracked diff sha256:
  a9815a409fc3c55aca8ed9fd71399641c423f7bfad0c6faf85c912e6e5dbfafc
checkpoint sha256 before this checkpoint note:
  29c98102bf74d7d618f3094b9cf854b68fdf413b28d41eeb2088c4ea22b97f29
unstaged and staged diff checks:
  PASS
phase context:
  PASS
```

No Gazebo or run process had started, and the primary v8.7 run root remained
absent during this checkpoint.

## Current milestone

**PHASE 08.8 M4.8 — V8.7 IMPLEMENTATION COMMITTED / PRIMARY VISIBLE
SEED 19501 DISPATCH CHECKPOINT PASS / DISPATCH COMMIT PENDING /
GAZEBO NOT YET STARTED.**

## Next criterion

Commit this exact dispatch boundary, then execute installed visible seed
`19501` once on isolated domain `231` with no ROS-domain monitor and no retry.

## Phase 08.8 M4.8 v8.7 primary-visible result — 2026-07-31

The one committed installed primary-visible seed `19501` execution ran once
on isolated domain `231`, with Gazebo GUI visible and no external ROS/DDS
monitor. It passed formally.

```text
scenario runner return code:      0
record process return code:       0
record timeout:                   false
recording complete:               true
cleanup complete:                 true
remaining new nodes:              none
remaining run-session processes:  none
final readiness false:            true
final commands zero:              true
formal predicates:                14/14
classification:                   passed
```

The required path was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Stage A completed at simulation time `118.409 s` with exactly one created,
typed, active fill. The local convergence point was
`(1.201810,1.046505) m`; the accepted fill center was
`(1.331634,1.073696) m`.

The assisted escape selected direction `(0.677977943,0.735082246)`, exited at
`(2.368352,2.115668) m`, and achieved measured fill-to-exit alignment
`0.999283312`. It had `1,889` evaluated assist controls, `1,889` fresh
matching supervisor commands, `1,889` suppressed nonzero GESC proposals, and
`1,889` positive supervisor-linear samples.

The fresh schema-v11 causal handoff passed without needing a transition tail:

```text
recognized transition samples:   0
handoff delay:                    0.005919394 s
handoff deadline:                 0.15 s
ordinary post-exit samples:       13,316
later authority reappearance:     none
```

Candidate two's exact raw interval `-3.8372093023255816` was strictly below
candidate one's retained lower bound `-2.8823354819629783`, with margin
`0.9548738203626033`. `GOAL_REACHED` preceded the evaluator-only proximity
sample.

Stage B completed at simulation time `230.405 s`, `111.996 s` after Stage A
and within its `300.0 s` budget. The first valid sample was
`(3.521410,3.610254) m`, `0.112314 m` from the declared global; final retained
distance was `0.112286 m`.

Retained evidence:

```text
run:
  /home/mattb/Experiments/GESC-Gaussian/runs/
    phase08_8_7_primary_probe/2026-07-31/
    20260731T133025467173Z_simulation_phase08_v8_7_primary_visible_probe-
    v8_7_primary_probe_r1p5_a45_h25_19501-robust__4b9033ba
scenario summary:
  /home/mattb/Experiments/GESC-Gaussian/runs/
    phase08_8_7_primary_probe/scenario_summaries/
    20260731T133024465291Z_phase08_v8_7_primary_visible_probe.yaml
report:
  docs/codex/gesc_gaussian/validation/
    phase_08_8_m4_8_primary_probe.md
```

The standard analyzer ran exactly once after closure, returned zero, and
reported:

```text
analysis_status:       complete
analysis_failures:     []
controller_success:    true
fill count:            1
escape successes:      1/1
failsafe:              false
timeout:               false
escape time:           17.863802 s
path length:           13.513125 m
goal convergence time: 229.772090 s
plots:                 9/9
```

Plot directory:

```text
<run>/analysis/phase07/plots/
```

The trajectory, candidate-ranking, and cost plots were visually inspected.
They show the expected local capture, one fill, northeast escape and transit,
global capture, and strict second-candidate raw-cost improvement. All nine
plots and machine-readable tables are retained.

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or run-session
process remains. The physical contract is unchanged: manual operator
`Ctrl+C`, with no coordinate-based physical stop.

## Current milestone

**PHASE 08.8 M4.8 — V8.7 PRIMARY VISIBLE SEED 19501 FORMAL PASS /
ANALYSIS COMPLETE / NINE PLOTS RETAINED / RESULT CHECKPOINT PENDING /
PRIMARY REPEATS PROHIBITED.**

## Next criterion

Checkpoint and commit this immutable passing visible result. Then create,
checkpoint, and commit a separate exact ten-seed primary-repeat dispatch
boundary before any repeat runs.

## Phase 08.8 M4.8 v8.7 primary-visible result checkpoint — 2026-07-31

The immutable formal pass, one-time complete analysis, nine plots, report,
and live status received the required Phase 08 checkpoint against dispatch
HEAD `0b0fb68`.

```text
base HEAD:
  0b0fb68dd18d1302fbb9ee68a166c819b3dbb7db
status sha256 before this checkpoint note:
  7ce12647de2f910473e14db5e186c64ef4e310c3660e6cfeaac71e41d4468821
active plan sha256:
  8c063ed44514bd9a84e0601f5cb73e56aeecabddce7cabda0d6c65fe80077694
visible report sha256:
  4533fb3bd201d112d24bc2d20e727697959fac239bf8a22a14589cb33ee87e41
unstaged tracked diff sha256:
  a0871438164cc4644d5aa32d2f51d871edba9d5b8ab5fddd437a261168b74dbf
checkpoint sha256 before this checkpoint note:
  0a2af847426e6804bde1f7d96a842cc370fe51b96230e6d8889a2b2c123322df
unstaged and staged diff checks:
  PASS
phase context:
  PASS
```

No Gazebo, scenario, recorder, analyzer, rosbag recorder, or run-session
process remained during this result checkpoint.

## Current milestone

**PHASE 08.8 M4.8 — V8.7 PRIMARY VISIBLE SEED 19501 FORMAL PASS /
ANALYSIS COMPLETE / NINE PLOTS RETAINED / RESULT CHECKPOINT PASS /
RESULT COMMIT PENDING / PRIMARY REPEATS PROHIBITED.**

## Next criterion

Commit this exact visible result. Then create, checkpoint, and commit a
separate exact ten-seed primary-repeat dispatch boundary before executing the
headless population serially with first-failure stop and no ROS-domain
monitor.

## Phase 08.8 M4.8 v8.7 primary-repeat dispatch boundary — 2026-07-31

The immutable v8.7 primary-visible pass is committed:

```text
9f177ea phase 08.8: retain passing v8.7 primary probe
```

The only next runtime authorized is the installed ten-seed primary population:

```text
install:
  /tmp/phase08_8_v8_7_release_qual.krosar/install
scenario:
  <install>/ros_esc/share/ros_esc/scenario_runner/scenarios/
    phase08_v8_7_primary_repeats.yaml
scenario SHA-256:
  f654f51a3cc445359b1f94c81512f25471d0c388267126bd8923791a1d2b542b
case:
  v8_7_primary_repeat_r1p5_a45_h25
seeds:
  19511, 19512, 19513, 19514, 19515,
  19516, 19517, 19518, 19519, 19520
GUI:
  headless
execution:
  serial, max_parallel_runs=1
first-failure policy:
  stop_on_run_failure=true
  stop_on_cleanup_failure=true
retry:
  none
ROS_DOMAIN_ID:
  232
ROS_LOCALHOST_ONLY:
  1
outer suite timeout:
  10500 s, INT then 30 s kill bound
dispatch log:
  /tmp/phase08_8_m4_8_v8_7_primary_repeats_dispatch.log
```

No parameter, source, position, intensity, detector, fill, affine, evaluator,
budget, or evidence change is permitted after dispatch. Every seed executes
at most once.

No `ros2 topic`, `ros2 node`, `ros2 service`, `ros2 param`, RViz, plotter, or
other external DDS participant may join domain `232` while the sealed suite
is active. Progress inspection is limited to process state, the dispatch
console file, run directories, bag-file growth, and runner-written scenario
summaries.

Each run must pass all `14` predicates, including schema-v11 causal ownership,
Stage A, exact one-fill cardinality, strict candidate ranking, Stage B,
recording, final readiness false, final zero, and cleanup. The runner stops
before the next seed on any behavioral or cleanup failure. A stopped
population remains stopped and failed; no seed is retried or relabeled.

At this boundary:

```text
branch:
  feature/gesc-gaussian-robustness-v1
HEAD:
  9f177ea
worktree:
  clean before this status amendment
active Gazebo/scenario/recorder/analyzer:
  none
primary-repeat v8.7 run root:
  absent
```

## Current milestone

**PHASE 08.8 M4.8 — V8.7 PRIMARY VISIBLE PASS COMMITTED /
TEN-SEED PRIMARY-REPEAT BOUNDARY WRITTEN / REPEAT DISPATCH CHECKPOINT
PENDING / REPEATS NOT YET STARTED.**

## Next criterion

Checkpoint and commit this exact population boundary. Then execute the
installed suite once on isolated domain `232` without external ROS/DDS
monitoring. Stop on the runner's first failure and never retry a seed.

## Phase 08.8 M4.8 v8.7 primary-repeat dispatch checkpoint — 2026-07-31

The exact serial ten-seed primary population authority received the required
Phase 08 checkpoint against visible-result HEAD `9f177ea`.

```text
base HEAD:
  9f177ea5a5bd20a5b0375da7d58ca805e72f259b
status sha256 before this checkpoint note:
  18397950686b9e77b86389e6730a896aba36dca197495549cd1326ef1fd5b0ad
active plan sha256:
  8c063ed44514bd9a84e0601f5cb73e56aeecabddce7cabda0d6c65fe80077694
unstaged tracked diff sha256:
  b968be3fe3c8510ca4ed50f00e31f4ec1d9d763b9f4c34bb324c699236260e7a
checkpoint sha256 before this checkpoint note:
  1b4bcef1d3224e07a47513e7073fe2fd97f55c099e7e52d3bb720c56e6bef10f
unstaged and staged diff checks:
  PASS
phase context:
  PASS
```

No Gazebo or run process had started, and the v8.7 primary-repeat root
remained absent during this checkpoint.

## Current milestone

**PHASE 08.8 M4.8 — V8.7 PRIMARY VISIBLE PASS COMMITTED /
TEN-SEED PRIMARY-REPEAT DISPATCH CHECKPOINT PASS / REPEAT DISPATCH
COMMIT PENDING / REPEATS NOT YET STARTED.**

## Next criterion

Commit this exact population boundary, then execute the installed suite once
on isolated domain `232`, serially, without external ROS/DDS monitoring and
without retries.

## Phase 08.8 M4.8 fixed v8.7 primary-repeat disposition — 2026-07-31

Dispatch boundary commit:

```text
308d8c9 phase 08.8: authorize v8.7 primary repeats
```

The fixed serial population executed seeds `19511`, `19512`, `19513`, and
`19514` exactly once. Seeds `19511..19513` passed all `14` predicates. Seed
`19514` completed the scientific behavior but failed the formal
`supervisor_owned_escape_assist` predicate, so the runner stopped before seed
`19515`. Seed `19514` was not retried, and seeds `19515..19520` were not
dispatched.

```text
formal result:                       3/4 pass
behavioral result:                   4/4 pass
recording completeness:              4/4 pass
cleanup:                             4/4 pass
exact one-fill cardinality:          4/4 pass
local recovery / Stage A:            4/4 pass
strict raw candidate ranking:        4/4 pass
post-recovery global proximity:      4/4 pass
final readiness false / zero:        4/4 pass
FAILSAFE / TIMEOUT:                  absent 4/4
```

The original runner completed normally and wrote:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_7_primary_repeats/scenario_summaries/
  20260731T134126836619Z_phase08_v8_7_primary_repeats.yaml
SHA-256:
  fbf5ea9110fa1aef2fd585690a1bb9f7fa4658d6679e759eb8b93139c741c1ca
```

The interactive console channel detached while the suite remained active, so
the outer shell return code was not recoverable. The process was not
terminated, restarted, or replaced. The original sealed runner continued,
closed at seed `19514`, retained all four results, and left no Gazebo,
scenario, recorder, analyzer, or run-session process. The truncated console
log is retained with SHA-256
`b2a2d6ccff54427cac5c6bba8048c871e4fe021bd52087175fbbdceba01e1963`.

Seed `19514` followed:

```text
SEARCH -> VERIFY -> DESIGN -> REPULSE -> ASSIST -> SEARCH ->
VERIFY -> GOAL_HOLD
```

It completed Stage A at simulation time `173.919 s`, ranked the second raw
candidate `0.9913900325777076` below the first candidate's retained lower
bound, and reached a valid noninterpolated sample `0.112068 m` from the
declared global at `293.803 s`. Its measured fill-to-exit direction alignment
was `0.999671269`. Recording, final zero, readiness false, and cleanup all
passed.

The message-level audit proves the failed ownership predicate was not
persistent additive control:

```text
recorded ESCAPE_ASSIST state:        1785506493834865483
recorded nonzero authority command:  1785506493837615474
first evaluated diagnostic:          1785506493841327810
first supervisor-owned diagnostic:   1785506493851741071
entry handoff from authority:         0.014125597 s
ordinary transition diagnostics:     1
GESC plus nonzero supervisor:         0
steady supervisor-owned diagnostics: 2,678
later ownership fallback:             0
```

The one transition diagnostic had combined command equal to GESC and exactly
zero supervisor contribution. It is the controller's previous
`ESCAPE_REPULSE` ownership before its separate state subscription consumed
the externally recorded `ESCAPE_ASSIST` update. Every subsequent diagnostic
through escape completion matched a fresh supervisor command and suppressed
the nonzero GESC proposal. Schema v11 already uses bounded causal settling on
assist exit but still assumes external bag order equals controller
consumption order at assist entry. The fixed schema-v11 run remains failed;
this diagnosis does not relabel it.

The standard analyzer ran exactly once for every dispatched seed. All four
invocations returned zero, had `analysis_failures=[]`, and produced all nine
plots. Seeds `19512` and `19513` reported `complete`; seeds `19511` and
`19514` reported `partial` only for optional generic analysis
applicability/gap handling. No critical input, formal event, recording check,
or plot is missing.

Durable report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_8_primary_repeats.md
```

Plots:

```text
<each retained run>/analysis/phase07/plots/
```

The fixed v8.7 primary gate is closed at `3/4` formal passes with four of ten
seeds dispatched. The v8.7 secondary and broad gates are prohibited. A fresh
evidence version may add a bounded causal entry-handoff proof while changing
no controller, supervisor, detector, fill, modified cost, source, world,
motion, ranking, timeout, cleanup, or stop behavior.

## Current milestone

**PHASE 08.8 M4.8 — FIXED V8.7 PRIMARY REPEAT GATE CLOSED FAIL /
3/4 FORMAL AND 4/4 BEHAVIORAL PASSES / ENTRY-HANDOFF DEFECT DIAGNOSED /
FAILURE CHECKPOINT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Checkpoint and commit the immutable v8.7 population, one-time analyses,
plots, diagnosis, report, and status. Then write and checkpoint a separately
versioned bounded causal assist-entry amendment. Do not retry any v8.7 seed or
dispatch a v8.7 secondary gate.

## Phase 08.8 M4.8 v8.7 primary-repeat failure checkpoint — 2026-07-31

The immutable stopped population, three formal passes, one behavioral
success/formal failure, four one-time analysis bundles, message-level causal
diagnosis, durable report, and live status received the required Phase 08
checkpoint against dispatch HEAD `308d8c9`.

```text
base HEAD:
  308d8c9da8394c4efd7172ac911fb09b8d9dbd2b
status sha256 before this checkpoint note:
  7d412212e0d5a43580168189222a80ac4bc119f941f58564c47ea7731e36f118
active plan sha256:
  8c063ed44514bd9a84e0601f5cb73e56aeecabddce7cabda0d6c65fe80077694
failure report sha256:
  59ddabf3db5487fe7bcb83c017cb3b204b65f956d53ed5fababf37f0f0afc90f
checkpoint sha256 before this checkpoint note:
  f1629a904b2a5ee9c04cb374e040c59f7274e282dd29d1e1ae49a4adb3670b84
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active Gazebo/scenario/recorder/analyzer:
  none
```

## Current milestone

**PHASE 08.8 M4.8 — FIXED V8.7 PRIMARY REPEAT GATE CLOSED FAIL /
3/4 FORMAL AND 4/4 BEHAVIORAL PASSES / ENTRY-HANDOFF DEFECT DIAGNOSED /
FAILURE CHECKPOINT PASS / FAILURE COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact v8.7 failure boundary. Then write and checkpoint a fresh
bounded causal assist-entry evidence amendment before any implementation or
Gazebo action. V8.7 remains closed and must not be retried.

## Phase 08.8 M4.9 v8.8 correction plan — 2026-07-31

The fixed v8.7 primary-repeat failure is committed:

```text
3616b68 phase 08.8: retain failed v8.7 primary repeats
```

The active Plan now defines v8.8 as a fresh schema-v12 causal assist-entry
evidence correction. It changes no controller, supervisor, detector, fill,
modified cost, launch, world, source, motion, ranking, time budget,
simulation stop, final-zero, or cleanup behavior.

Schema versions through v11 retain their existing interpretation. Schema v12
uses the existing evaluator-only `0.15 s` handoff timeout at assist entry as
well as exit. Before the first owned entry diagnostic it permits only finite,
arithmetically valid, correctly saturated ordinary GESC with a fresh zero
supervisor command, or valid zero/failsafe output. It then requires a fresh
supervisor-only diagnostic within the bound and uninterrupted
supervisor-only ownership through escape completion. True GESC plus nonzero
supervisor, unknown/stale/late evidence, invalid arithmetic/saturation, or
later fallback still fails.

Fresh fixed inputs use:

```text
primary visible:    seed 19601
primary repeats:    seeds 19611..19620
secondary visible:  seed 19651
secondary repeats:  seeds 19661..19665
```

The retained seed-`19514` bag is the immutable causal replay fixture. V8.8
must prove schema v11 still fails it and schema v12 recognizes exactly one
ordinary entry-transition diagnostic, a `14.125597 ms` handoff, and all
`2,678` later supervisor-owned diagnostics. Adversarial late, additive,
unknown, stale-zero, nonfinite, arithmetic, saturation, no-ownership, and
fallback fixtures must fail.

No Gazebo execution is authorized until the complete no-Gazebo
qualification, validation report, Phase 08 checkpoint, and implementation
commit pass. V8.7 remains closed; no v8.7 seed may be retried.

## Current milestone

**PHASE 08.8 M4.9 — V8.7 FAILURE COMMITTED / V8.8 CAUSAL ASSIST-ENTRY
PLAN AMENDMENT SAVED / PLAN CHECKPOINT PENDING / NO GAZEBO AUTHORIZED.**

## Next criterion

Checkpoint and commit the exact v8.8 correction Plan and live-status
boundary. Then implement schema-v12 evidence, tests, and the four fresh
scenario inputs without launching Gazebo.

## Phase 08.8 M4.9 v8.8 correction-plan checkpoint — 2026-07-31

The fresh schema-v12 causal assist-entry Plan and live-status boundary
received the required Phase 08 checkpoint against committed v8.7 failure
HEAD `3616b68`.

```text
base HEAD:
  3616b684da995b2af58f8e64cb4c658de3fbe61f
active plan sha256 before this checkpoint note:
  c6c16cdf8c8d4513171d1d2fde7d2793f730dd1033e955768ff3857518347dc5
status sha256 before this checkpoint note:
  00a34ac0665ea111b2e38c3daf08ba9f4f7231c515b8263f3b1919d43a469467
checkpoint sha256 before this checkpoint note:
  cb8a2d06bd6c0db4cea2089d300f7acf60dfc2f9a3b2b0e96d162fa985772178
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active Gazebo/scenario/recorder/analyzer:
  none
```

## Current milestone

**PHASE 08.8 M4.9 — V8.8 CAUSAL ASSIST-ENTRY PLAN CHECKPOINT PASS /
PLAN COMMIT PENDING / NO GAZEBO AUTHORIZED.**

## Next criterion

Commit this exact Plan boundary. Then implement and qualify schema v12 plus
fresh v8.8 scenarios entirely without Gazebo.

## Phase 08.8 M4.9 v8.8 no-Gazebo implementation qualification — 2026-07-31

The correction Plan is committed:

```text
789298c phase 08.8: plan v8.8 causal assist entry evidence
```

The separately versioned v8.8 evidence correction is implemented and
qualified without Gazebo. It changes no controller, supervisor, detector,
fill, modified-cost, launch, world, source, motion, ranking, time budget,
stop, final-zero, or cleanup behavior.

The scenario parser now exports schema 12 as the current version while
retaining support for versions 1 through 12. The runner keeps schema
versions through 11 on the exact old assist-entry branch. Schema 12 adds a
bounded causal entry proof using the already-declared evaluator-only
`supervisor_owned_assist_handoff_timeout_sec: 0.15`.

Before first ownership, schema 12 accepts only a finite, arithmetically
valid, correctly saturated ordinary GESC diagnostic supported by a fresh
zero supervisor command, or equivalently valid zero/failsafe output. It
then requires a fresh nonzero supervisor-only owner within `0.15 s` and
uninterrupted ownership through escape completion. It continues to reject
true GESC plus nonzero supervisor, unknown/stale/late evidence, nonfinite
data, arithmetic or saturation corruption, missing ownership, and later
fallback.

The retained seed-`19514` bag was replayed read only. Schema v11 still
fails on:

```text
GESC leaked into the supervisor-owned command
```

Schema v12 passes with:

```text
ordinary entry-transition diagnostics: 1
entry authority stamp:                  1785506493837615474
first owned diagnostic stamp:           1785506493851741071
entry handoff:                          0.014125597 s
steady owned diagnostics:               2,678
fresh supervisor diagnostics:           2,678
suppressed nonzero GESC diagnostics:     2,678
positive linear supervisor diagnostics: 2,109
post-exit handoff:                       0.006192330 s
post-exit ordinary diagnostics:          14,339
Stage A / fill cardinality / Stage B:    PASS / PASS / PASS
outcome error:                           null
```

This replay also corrects a prior arithmetic transcription:

```text
1785506493851741071 - 1785506493837615474
= 14,125,597 ns
= 14.125597 ms
```

The Plan, live status, and retained v8.7 report now record an explicit
erratum from `13.125597 ms` to `14.125597 ms`. No immutable sample,
predicate, result, or timeout comparison changes.

The adversarial schema-v12 fixtures reject late ownership, missing fresh
zero support, additive GESC plus supervisor, unknown command, nonfinite
command, contribution corruption, saturation corruption, missing
ownership, and fallback after ownership. Schema v11's original failure is
also regression-tested.

Final test evidence:

```text
new causal-entry selection:
  17 passed, 301 deselected in 1.62 s
schema and runner:
  318 passed, 1 skipped in 52.86 s
focused controller/supervisor/detector/legacy:
  310 passed in 8.33 s
focused runner/validator/recorder/analyzer evidence:
  604 passed, 2 skipped in 130.92 s
final broad ROS-independent functional gate:
  915 passed, 3 skipped in 135.14 s
final current-schema assertion:
  1 passed in 0.61 s
```

The three broad skips are the unchanged copyright-template check and two
explicit Gazebo opt-ins. Changed-file fatal lint
`E9,F63,F7,F82`, Python compilation, central-launch XML parsing, four YAML
parses, `git diff --check`, and Phase 08 implementation context all pass.
Full changed-file `ament_flake8` reports only the inherited D202 at the
unchanged `run_scenario.py:2410`.

The final fresh isolated build:

```text
root:
  /tmp/phase08_8_v8_8_release_final.L0zEGg
packages:
  ros_esc_interfaces
  ros_esc
  turtlebot3_rotating_sensor
result:
  3 packages finished in 11.8 s
source/install runtime parity:
  10/10 PASS
```

Installed `--show-args` and `--print-description` both pass, and the
evaluator-only handoff field is absent from the launch graph. Default
supervisor, fully enabled counted-source supervisor with exact one-fill
cardinality, robust affine modified cost, and robust controller all
construct on isolated domain `226` and reach the expected timeout `124`.
No process survives. The modified-cost owner records normal startup before
the bounding timeout produces its expected executor shutdown exception.

The four final installed dry-runs pass:

```text
primary visible:    1 run,  seed 19601
primary repeats:   10 runs, seeds 19611..19620
secondary visible:  1 run,  seed 19651
secondary repeats:  5 runs, seeds 19661..19665
unsupported cases:  0
created run roots:  0
```

Fresh scenario hashes:

```text
003230a00ddc0ab07adad5957012c3c28539119fbbb885a3edcd5f594b4298ca
  phase08_v8_8_primary_repeats.yaml
e48f8f6fd1e2e8377f13d5e621ad6df2017b663b8f35a977d01af5d14605b5e1
  phase08_v8_8_primary_visible_probe.yaml
ff2da3610f977e8f239f67ed9e1d586705894fb84e1821d87d817b6b9f479884
  phase08_v8_8_secondary_repeats.yaml
5a0b18609a7e4abb87858d36575d0fa9c10fd0837b259d84bf357aea83ce31f7
  phase08_v8_8_secondary_visible_probe.yaml
```

Pairwise normalization proves all runtime inputs remain identical to v8.7
except schema/evidence identities, prose, roots, and seeds. Historical v8.7
scenario hashes, the three retained worlds, V6 selection, all old inputs,
and all old results remain unchanged. V8.7 stays failed and closed.

Bounded qualification corrections are retained in the report: missing ROS
interface overlays, advancing the unsupported-version fixture to 13,
advancing the current schema constant to 12, lint invocation and
new-test-format corrections, one overbroad diagnostic that included
non-gating historical style suites, invalid DDS domain 237, missing dry-run
operator, and an initially misspelled controller parity path. Every
corrected declared gate passes; none involved algorithm motion or an
empirical result.

Durable record:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_9_no_gazebo_qualification.md
SHA-256:
  28f3666fd8626f2bf6d87b46f59f4b903277f28abc359f6a35f39ff6ef5bd128
```

At close, no Gazebo, scenario runner, recorder, analyzer, rosbag recorder,
controller, supervisor, modified-cost, or physical process is active. All
four v8.8 run roots are absent. Gazebo remains prohibited until this
implementation boundary is checkpointed and committed and a separate
visible-probe dispatch boundary is checkpointed and committed.

## Current milestone

**PHASE 08.8 M4.9 — V8.8 SCHEMA-V12 CAUSAL ASSIST-ENTRY IMPLEMENTATION /
NO-GAZEBO QUALIFICATION PASS / MATERIAL CHECKPOINT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Run the Phase 08 material checkpoint, inspect and commit the exact v8.8
implementation boundary. Then write, checkpoint, and commit a separate
seed-`19601` visible-primary dispatch record before starting Gazebo.

## Phase 08.8 M4.9 v8.8 implementation checkpoint — 2026-07-31

The schema-v12 implementation, adversarial tests, immutable causal replay,
four fresh scenarios, complete no-Gazebo qualification, arithmetic erratum,
durable report, and live status received the required Phase 08 material
checkpoint against correction-Plan HEAD `789298c`.

```text
base HEAD:
  789298cd18724b4430d41aaecaa88b87de4d5bb8
active plan sha256 before this checkpoint note:
  c761c3aec53531931abf3a1f0edfd2b9366bbcbef53cfa1266cdb8b2f1aa211d
status sha256 before this checkpoint note:
  e7974e75ed1294fc648278d80916ba1c3ef5db4f43339ca07485a20f1695fe22
no-Gazebo report sha256:
  28f3666fd8626f2bf6d87b46f59f4b903277f28abc359f6a35f39ff6ef5bd128
unstaged diff sha256:
  66a3bb9529772446a2b7d9e0e009723c4652b1a99280fb6e0e270d0707a6bf3b
checkpoint sha256 before this checkpoint note:
  5eac86de4f7e7e97e90554ade2475592efbe4573ab29026217da7c7a58e133f2
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active Gazebo/scenario/recorder/analyzer:
  none
v8.8 run roots:
  all four absent
```

## Current milestone

**PHASE 08.8 M4.9 — V8.8 SCHEMA-V12 CAUSAL ASSIST-ENTRY IMPLEMENTATION /
NO-GAZEBO QUALIFICATION PASS / MATERIAL CHECKPOINT PASS / IMPLEMENTATION
COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Inspect and commit this exact implementation boundary. Then write,
checkpoint, and commit a separate seed-`19601` visible-primary dispatch
record before starting Gazebo.

## Phase 08.8 M4.9 v8.8 visible-primary dispatch boundary — 2026-07-31

The complete schema-v12 no-Gazebo implementation boundary is committed:

```text
1b56bd2 phase 08.8: qualify v8.8 causal assist entry evidence
```

The worktree is clean, Phase 08 implementation context passes, and no
Gazebo, scenario runner, recorder, analyzer, rosbag recorder, or physical
process is active. The fresh final release snapshot remains:

```text
/tmp/phase08_8_v8_8_release_final.L0zEGg
```

Source/install byte parity is exact for the one authorized scenario:

```text
e48f8f6fd1e2e8377f13d5e621ad6df2017b663b8f35a977d01af5d14605b5e1
  phase08_v8_8_primary_visible_probe.yaml
```

The sealed dispatch is exactly:

```text
scenario:
  /tmp/phase08_8_v8_8_release_final.L0zEGg/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_8_primary_visible_probe.yaml
suite:
  phase08_v8_8_primary_visible_probe
case:
  v8_8_primary_probe_r1p5_a45_h25_19601
seed:
  19601
profile:
  robust_gaussian_v1
Gazebo GUI:
  true
ROS_DOMAIN_ID:
  225
operator:
  Codex
run root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_8_primary_probe
preflight timeout:
  150.0 s
scenario timeout:
  720.0 s
wall timeout:
  900.0 s
shutdown grace:
  45.0 s
stop on behavioral failure:
  true
stop on cleanup failure:
  true
retry:
  prohibited
```

The run root is absent. No external ROS or DDS participant may join domain
`225` while the sealed run is active. Observation is limited to OS process
state and retained files. The standard analyzer may run exactly once only
after the scenario and all descendants close.

The probe must pass all declared behavioral predicates, including one local
candidate, exactly one fill, completed Stage A, schema-v12 causal assist
entry and schema-v11 causal exit ownership, ordinary post-recovery GESC,
strictly lower second raw-cost interval, Stage B proximity, recording,
final readiness false, final zero, and uncontaminated cleanup. It must then
produce all nine plots. Any behavioral, evidence, recording, final-zero, or
cleanup failure closes this visible gate with no retry and prohibits the
primary repeats.

No primary repeat, secondary probe, secondary repeat, broad matrix, or
physical run is authorized by this boundary.

## Current milestone

**PHASE 08.8 M4.9 — V8.8 IMPLEMENTATION COMMITTED / VISIBLE PRIMARY
SEED 19601 DECLARED / DISPATCH CHECKPOINT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Run the Phase 08 dispatch checkpoint, commit this exact record, and only
then execute the installed visible seed-`19601` probe once on domain `225`
without any external ROS/DDS monitoring.

## Phase 08.8 M4.9 v8.8 visible-primary dispatch checkpoint — 2026-07-31

The exact installed seed-`19601` GUI dispatch authority received the
required Phase 08 checkpoint against implementation HEAD `1b56bd2`.

```text
base HEAD:
  1b56bd2c31c26ccdf71a81cdb2999e87dc4fe1a2
status sha256 before this checkpoint note:
  0baa0a652c33f595ec6f4edc87bd99b8822f188e21182591ee801a849caa40be
active plan sha256:
  c761c3aec53531931abf3a1f0edfd2b9366bbcbef53cfa1266cdb8b2f1aa211d
unstaged diff sha256:
  a15c209e1624f82c5a2f7449beb29e210265b9af801b4a29778d11250472de62
checkpoint sha256 before this checkpoint note:
  b8e086a13faa7e6e2ff74e5d0383737cf929a99fc9a79ee084f0d458e62317f6
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active Gazebo/scenario/recorder/analyzer:
  none
v8.8 primary-visible run root:
  absent
```

## Current milestone

**PHASE 08.8 M4.9 — V8.8 IMPLEMENTATION COMMITTED / VISIBLE PRIMARY
SEED 19601 DISPATCH CHECKPOINT PASS / DISPATCH-RECORD COMMIT PENDING /
GAZEBO PROHIBITED.**

## Next criterion

Commit this exact dispatch boundary. Then execute the installed visible
seed-`19601` probe once on domain `225` without external ROS/DDS
monitoring and with no retry.

## Phase 08.8 M4.9 v8.8 primary visible result — 2026-07-31

The dispatch boundary is committed:

```text
31bc585 phase 08.8: authorize v8.8 visible primary probe
```

The installed seed-`19601` primary probe executed exactly once on isolated
domain `225` with Gazebo GUI enabled. It was not retried or externally
monitored through ROS/DDS.

The sealed runner and record process both returned zero. The run stopped on
the first valid noninterpolated post-ranking odometry sample within the
simulation-only `0.50 m` global-proximity radius. Recording, final readiness
false, final commands zero, read-only sqlite quick check, and cleanup all
pass. No new node or session process remained.

Formal result:

```text
classification:                    PASS
infrastructure:                    completed
required predicates:               14/14 PASS
Stage A local recovery:             PASS
exact fill cardinality:             PASS, one cluster
schema-v12 assist entry ownership:  PASS
schema-v11 assist exit ownership:   PASS
strict candidate ranking:           PASS
Stage B global proximity:           PASS
recording / final zero / cleanup:    PASS / PASS / PASS
```

The exact required state path occurred:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Stage A completed at simulation time `222.212 s`:

```text
fill center:                  (1.038667, 1.321887) m
convergence point:            (1.202823, 1.341585) m
distance to declared local:   0.314848 m
fill-to-convergence distance: 0.165334 m
created / typed / active:     [1] / [1] / [1]
merge or supersession:        none
```

The assisted exit passed:

```text
selected direction:       (0.406061599, 0.913845708)
measured exit:            (1.485387, 2.724966) m
fill-to-exit distance:     1.472478 m
exit alignment:            0.993966806
escape duration:          23.644374 s
failsafe / timeout:        false / false
```

Schema-v12 entry evidence was direct on this fresh run:

```text
entry transition diagnostics:           0
entry handoff:                           0.011493195 s
entry bound:                             0.15 s
steady owned diagnostics:               2,652
fresh supervisor diagnostics:           2,652
suppressed nonzero GESC diagnostics:     2,652
positive linear supervisor diagnostics: 2,031
entry evidence mode:                     bounded_causal_schema_v12
```

The post-exit causal proof also passed:

```text
transition diagnostics:          1
ordinary-owner handoff:          0.012090783 s
handoff bound:                   0.15 s
ordinary post-exit diagnostics: 14,040
later authority reappearance:    none
evidence mode:                   bounded_causal_schema_v11
```

Candidate raw-cost ranking was strict:

```text
candidate one lower bound: -2.8453728221821186
candidate two upper bound: -3.8372093023255816
strict separation margin:   0.9918364801434629
candidate two ordinal:       2
filled candidates:           1
known source count:          2
decision:                    GOAL_REACHED
```

The first valid post-ranking global-proximity sample was:

```text
simulation time:      339.818 s
position:             (3.574407, 3.611028) m
declared global:      (3.5, 3.5) m
distance:             0.133655 m
interpolation:        none
Stage B duration:     117.606 s
Stage B budget:       300.0 s
```

The coordinate was evaluator-only and did not direct motion. Physical
arrival remains manually operator-stopped with `Ctrl+C`.

The standard analyzer ran exactly once after every run descendant closed.
It returned zero, produced all nine plots and all expected tables, reported
`analysis_failures=[]`, and passed fresh Phase 05 validation. Its overall
status is `partial` only because one optional generic state-duration gap
exceeded `0.150000 s`; no critical input or formal behavior evidence is
missing.

Retained paths:

```text
summary:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_8_primary_probe/scenario_summaries/
  20260731T150756478627Z_phase08_v8_8_primary_visible_probe.yaml
run:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_8_primary_probe/2026-07-31/
  20260731T150757443879Z_simulation_phase08_v8_8_primary_visible_probe-
  v8_8_primary_probe_r1p5_a45_h25_19601-robust__5c73451a
plots:
  <run>/analysis/plots/
```

Evidence hashes:

```text
summary:
  c494dc23589c47b363a1af5e8cc1a2b280c7499fb096ca10a3ad000d3d523526
scenario_result.yaml:
  8f47afb3730276b41a81163566719ce14fc9b8a790b108bb1c5799b8726cab9c
completeness.json:
  a5a4e94003389d76487d583e403bbe4d2c502eb710b23eb168783f025f02d89a
raw bag:
  fe09b9602375af52b372200961ad5e2af62f5e51b353ef4df4b97ba7a1cdba8c
analysis completeness:
  f1572482e85bb5b22398a24cf4918e68b06267bb2b33d9b68a1ab016d68d107e
analysis summary:
  ecc153b302bc0a3b37971362f3b3a9c5ac4d31a8a7ef2fa51941eca9ddcef715
```

Durable report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_9_primary_probe.md
SHA-256:
  2d9a890f91b67b35146a3acb2b822bb537c57accc158934c7d109c4498a4eb66
```

At result close, no Gazebo, scenario runner, recorder, analyzer, rosbag
recorder, or physical process is active. The visible gate is a formal pass.
The ten-run primary repeat gate remains prohibited until this exact result
is checkpointed and committed and a separate repeat-population dispatch
boundary is checkpointed and committed.

## Current milestone

**PHASE 08.8 M4.9 — V8.8 PRIMARY VISIBLE FORMAL PASS / 14 OF 14
PREDICATES PASS / ALL NINE PLOTS RETAINED / RESULT CHECKPOINT PENDING /
PRIMARY REPEATS PROHIBITED.**

## Next criterion

Run the Phase 08 result checkpoint and commit this immutable visible result.
Then write, checkpoint, and commit the exact ten-seed v8.8 primary-repeat
population before dispatching any repeat.

## Phase 08.8 M4.9 v8.8 primary-visible result checkpoint — 2026-07-31

The immutable seed-`19601` run, suite summary, formal scenario result,
complete recording, clean shutdown, one-time analysis, nine plots, durable
report, and live status received the required Phase 08 checkpoint against
dispatch HEAD `31bc585`.

```text
base HEAD:
  31bc585172b35cdad16ee15d350832e0f5a71ebc
status sha256 before this checkpoint note:
  0d1a811a4c01c7b7fb89b855a3c348c31980955267f2bac75ba4c930717eb073
active plan sha256:
  c761c3aec53531931abf3a1f0edfd2b9366bbcbef53cfa1266cdb8b2f1aa211d
visible-result report sha256:
  2d9a890f91b67b35146a3acb2b822bb537c57accc158934c7d109c4498a4eb66
unstaged diff sha256:
  cbb40f94eac9dbd7391a7ebd1c82f0342a07a40fce1f7309c36d53718e18ed65
checkpoint sha256 before this checkpoint note:
  9c8d9ef221a2acab157a98f6be6553c168399687e78761c20fd02bb67c7c9620
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active Gazebo/scenario/recorder/analyzer:
  none
```

## Current milestone

**PHASE 08.8 M4.9 — V8.8 PRIMARY VISIBLE FORMAL PASS / ALL NINE PLOTS
RETAINED / RESULT CHECKPOINT PASS / RESULT COMMIT PENDING / PRIMARY
REPEATS PROHIBITED.**

## Next criterion

Commit this exact visible-result boundary. Then write, checkpoint, and
commit the exact ten-seed v8.8 primary-repeat population before dispatching
any repeat.

## Phase 08.8 M4.9 v8.8 primary-repeat population boundary — 2026-07-31

The passing visible-primary result is committed:

```text
61adc3c phase 08.8: pass v8.8 visible primary probe
```

The worktree is clean, Phase 08 implementation context passes, and no
Gazebo, scenario runner, recorder, analyzer, rosbag recorder, or physical
process is active. The primary-repeat run root is absent.

The source and installed population inputs are byte-identical:

```text
003230a00ddc0ab07adad5957012c3c28539119fbbb885a3edcd5f594b4298ca
  phase08_v8_8_primary_repeats.yaml
```

The sealed population is exactly:

```text
scenario:
  /tmp/phase08_8_v8_8_release_final.L0zEGg/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_8_primary_repeats.yaml
suite:
  phase08_v8_8_primary_repeats
case:
  v8_8_primary_repeat_r1p5_a45_h25
profile:
  robust_gaussian_v1
seeds:
  19611
  19612
  19613
  19614
  19615
  19616
  19617
  19618
  19619
  19620
Gazebo GUI:
  false
serial:
  true
ROS_DOMAIN_ID:
  223
operator:
  Codex
run root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_8_primary_repeats
per-run preflight timeout:
  150.0 s
per-run scenario timeout:
  720.0 s
per-run wall timeout:
  900.0 s
per-run shutdown grace:
  45.0 s
stop on first behavioral failure:
  true
stop on first cleanup failure:
  true
retry:
  prohibited
```

Every run must independently pass the same fourteen predicates as the
visible probe. The runner must stop before the next seed on any behavioral,
evidence, recording, final-zero, or cleanup failure. A stopped population
remains stopped and failed; no seed may be retried or relabeled.

No external ROS/DDS participant may join domain `223` while the sealed
suite is active. Observation is limited to OS process state and retained
files. After the population closes, the standard analyzer may run exactly
once for each dispatched run. Analysis must not run concurrently with
dispatch.

Only a complete `10/10` formal pass authorizes the secondary visible probe.
No secondary, broad-matrix, three-light, or physical run is authorized by
this boundary.

## Current milestone

**PHASE 08.8 M4.9 — V8.8 PRIMARY VISIBLE RESULT COMMITTED / EXACT
TEN-SEED PRIMARY POPULATION DECLARED / REPEAT DISPATCH CHECKPOINT PENDING /
GAZEBO PROHIBITED.**

## Next criterion

Run the Phase 08 dispatch checkpoint, commit this exact population, and
only then execute the installed serial suite once on domain `223`, stopping
on the runner's first failure with no retry.

## Phase 08.8 M4.9 v8.8 primary-repeat dispatch checkpoint — 2026-07-31

The exact ten-seed primary-repeat population received the required Phase 08
checkpoint against visible-result HEAD `61adc3c`.

```text
base HEAD:
  61adc3c4b11d5eaecbc89033f058b1d529035134
status sha256 before this checkpoint note:
  b9a2addbdc5bd8004a069071b5380736c6ed9430410510849e2b79a0be7e7a2c
active plan sha256:
  c761c3aec53531931abf3a1f0edfd2b9366bbcbef53cfa1266cdb8b2f1aa211d
unstaged diff sha256:
  5d8b141e72b37f95414199a891089f5aea797449116ae44b34f41dc44d4c1a0f
checkpoint sha256 before this checkpoint note:
  915e7830826894786afe936f17efe8dd8b18e56ee228333a7f2d7d1ac4585710
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active Gazebo/scenario/recorder/analyzer:
  none
primary-repeat run root:
  absent
```

## Current milestone

**PHASE 08.8 M4.9 — EXACT TEN-SEED V8.8 PRIMARY POPULATION /
REPEAT DISPATCH CHECKPOINT PASS / DISPATCH COMMIT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Commit this exact population boundary. Then execute the installed serial
suite once on domain `223`, stopping on the runner's first failure with no
retry.

## Phase 08.8 M4.9 fixed v8.8 primary-repeat disposition — 2026-07-31

The primary-repeat dispatch boundary is committed:

```text
5e69f11 phase 08.8: authorize v8.8 primary repeats
```

The installed ten-seed suite executed serially and headlessly on isolated
domain `223` with no external ROS/DDS monitoring and no retry. Seeds
`19611..19615` passed all fourteen predicates. Seed `19616` executed once,
failed the fixed formal contract, and caused the runner to stop. Seeds
`19617..19620` were not dispatched.

```text
resolved:             10
executed:              6
formal pass:           5
formal fail:           1
scientific behavior:   6/6 complete
recording complete:    6/6
cleanup pass:          6/6
sqlite quick_check:    6/6 ok
runner return code:    1, expected first-failure stop
retry:                 none
```

Retained scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_8_primary_repeats/scenario_summaries/
  20260731T152229585403Z_phase08_v8_8_primary_repeats.yaml
SHA-256:
  088e54b95af59f4941be93b869c033e7e34a9ae9c61d42ca4b93f353c77aa6e9
```

Seed `19616` did not fail to navigate. It found the first/local candidate,
created exactly one typed active fill, escaped that fill, resumed search,
found the second candidate, ranked its raw-cost interval strictly below the
first by `0.9888651478968238`, emitted `GOAL_REACHED`, and finished
`0.104056 m` from the declared global.

Its successful recovery was the architecture's direct branch:

```text
ESCAPE_REPULSE -> SEARCH
```

The fixed v8.8 evaluator and scenario required the fallback branch:

```text
ESCAPE_REPULSE -> ESCAPE_ASSIST -> SEARCH
```

Seed `19616` maintained measured radial progress above the fixed stall
threshold, so it correctly emitted no `ESCAPE_STALLED` event and never
entered `ESCAPE_ASSIST`. The direct interval lasted `23.328587 s`; its
measured exit displacement was `1.401137 m` against a `1.366771 m` exit
radius, with `0.947517529` alignment to the frozen revision-one direction.
Across `3,015` synchronized repulse control samples, supervisor contribution
was exactly zero and combined command equaled ordinary GESC exactly. No
sample reported stalled.

Stage A nevertheless accepted only the assisted topology whenever assist was
enabled. It withheld its completion stamp, causing the required-path,
required-event, local-recovery, ownership, controller-goal, ground-truth,
and post-recovery predicates to cascade false. The live monitor then
requested the fixed Stage A evidence stop at simulation time `360.256 s`,
after controller-ranked `GOAL_REACHED` at `314.7 s`.

This is an evaluator-topology integration defect. It is not a controller,
supervisor, detector, fill, affine, raw-cost-ranking, or navigation defect.
V8.8 remains formally failed and closed.

The standard analyzer ran exactly once for each of the six dispatched runs
after the population closed. All six invocations returned zero, reported
`analysis_failures=[]`, passed fresh Phase 05 validation, produced all
expected tables, and produced all nine plots with `analysis_status=complete`.
Visual inspection of seed `19616` confirms local capture, one fill, monotonic
direct radial escape, transit to the second source, strict candidate ranking,
and final global capture.

Durable report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_9_primary_repeats.md
SHA-256:
  0f8b916e069e9b2f09d73c00ec2e82f0e7bb9f2262fb76bf85cf113c9153c216
```

At result close, no Gazebo, scenario runner, recorder, analyzer, rosbag
recorder, or physical process is active. The v8.8 secondary visible probe,
secondary repeats, broader matrix, three-light execution, and physical
motion are prohibited.

## Current milestone

**PHASE 08.8 M4.9 — FIXED V8.8 PRIMARY POPULATION CLOSED / 5 OF 6
DISPATCHED FORMAL PASSES / 6 OF 6 SCIENTIFIC BEHAVIORS COMPLETE /
DIRECT-RECOVERY EVIDENCE-TOPOLOGY DEFECT DIAGNOSED / RESULT CHECKPOINT
PENDING / ALL LATER V8.8 GATES PROHIBITED.**

## Next criterion

Run the Phase 08 result checkpoint and commit this immutable v8.8 failure.
Then plan a separately versioned correction that accepts both declared
recovery topologies while requiring positive geometry and command-ownership
proof on the direct branch and retaining the complete schema-v12 ownership
proof on the assisted branch. Do not relabel or retry v8.8.

## Phase 08.8 M4.9 v8.8 primary-repeat failure checkpoint — 2026-07-31

The immutable six-run population, stopped-early scenario summary, six
per-run results, complete recordings, clean shutdown, six one-time analysis
bundles, fifty-four plots, durable diagnosis, and live status received the
required Phase 08 checkpoint against dispatch HEAD `5e69f11`.

```text
base HEAD:
  5e69f11c380203ba28f609458e4c9795c330245a
status sha256 before this checkpoint note:
  46ec49efcd639ba489092b1a8463a45baf07d76c6702ceaeee663dd400533c92
active plan sha256:
  c761c3aec53531931abf3a1f0edfd2b9366bbcbef53cfa1266cdb8b2f1aa211d
v8.8 failure report sha256:
  0f8b916e069e9b2f09d73c00ec2e82f0e7bb9f2262fb76bf85cf113c9153c216
unstaged diff sha256:
  1899d2b6cbaa818918ac156cb0923bf304c9934f774f6a8c51991b18cacc6a9e
checkpoint sha256 before this checkpoint note:
  6d9a224b1b7e7954ebd3b3435ef56d07356fb128a2df5bfedc956ec1b2382b87
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active Gazebo/scenario/recorder/analyzer:
  none
```

## Current milestone

**PHASE 08.8 M4.9 — FIXED V8.8 PRIMARY POPULATION CLOSED AND
CHECKPOINTED / 5 OF 6 FORMAL PASSES / 6 OF 6 SCIENTIFIC BEHAVIORS
COMPLETE / RESULT COMMIT PENDING / ALL LATER V8.8 GATES PROHIBITED.**

## Next criterion

Commit this exact v8.8 failure boundary. Then add and checkpoint a separately
versioned dual-topology evidence amendment before changing any evaluator or
scenario input. Do not dispatch Gazebo from the uncommitted diagnosis.

## Phase 08.8 M4.10 v8.9 dual-topology correction plan — 2026-07-31

The immutable v8.8 primary-repeat failure is committed:

```text
ec1645c phase 08.8: retain failed v8.8 primary repeats
```

The active Plan now defines v8.9 as a fresh schema-v13 evidence correction.
It changes no controller, supervisor, detector, fill, modified cost, launch
argument, world, source, motion, ranking, timeout, final-zero, cleanup, or
stop behavior.

Schema v13 adds:

```text
escape_command_ownership
```

and accepts exactly the two recovery topologies already declared by the
architecture:

```text
direct:
  ESCAPE_REPULSE -> SEARCH

measured-stall fallback:
  ESCAPE_REPULSE -> ESCAPE_ASSIST -> SEARCH
```

The predicate is conditional but nonvacuous. If assist occurs, the complete
schema-v12 causal supervisor-ownership proof remains mandatory. If assist
does not occur, the evaluator must positively prove frozen revision-one
geometry, mature radial progress, no stall, zero supervisor command and
contribution, ordinary GESC command ownership, valid arithmetic and
saturation, a stable measured exit beyond the frozen radius, alignment at
least `+0.80`, and returned-search cleanup. Entering assist permanently
selects the assisted proof; a failed assisted interval cannot use the direct
branch.

The live Stage A monitor and offline Stage A evaluator will accept the same
two exact paths only for schema v13. Schema versions through v12 retain their
existing assisted-only interpretation when supervisor-owned assist is
enabled.

Fresh fixed inputs are:

```text
primary visible:  seed 19701
primary repeats:  seeds 19711..19720
secondary visible: seed 19751
secondary repeats: seeds 19761..19765
```

The two fixed local-first, two-source, open-field `400/1600` layouts and
every motion/configuration input remain unchanged. Physical stopping remains
manual operator `Ctrl+C`.

Before Gazebo, retained seed `19616` must remain failed under schema v12 and
pass a schema-v13 direct-branch replay with its immutable message set.
Retained assisted seed `19611` must select the schema-v13 assisted branch and
reproduce its schema-v12 entry/exit evidence. Negative direct and assisted
fixtures, focused/broad tests, isolated build, installed construction,
source/install parity, and four installed dry-runs must all pass. The
qualification requires a durable report, checkpoint, and implementation
commit.

Only a fresh passing visible primary probe authorizes v8.9 primary repeats.
Only `10/10` primary repeats authorizes the secondary visible probe. Only a
passing secondary visible probe authorizes five secondary repeats. Only
`5/5` secondary repeats authorizes M6. Every dispatched run remains
one-time/no-retry and the first failure closes its population.

Active plan SHA-256:

```text
5dde1f6be543939e27145ac7fc0a0b32da47b2613b0e60901030652d95e24892
```

No Gazebo, scenario runner, recorder, analyzer, rosbag recorder, or physical
process is active.

## Current milestone

**PHASE 08.8 M4.10 — V8.8 FAILURE COMMITTED / V8.9 SCHEMA-V13
DUAL-TOPOLOGY CORRECTION PLANNED / PLAN CHECKPOINT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Checkpoint and commit the exact v8.9 correction Plan and live-status
boundary. Then implement and qualify the schema-v13 evaluator, tests, and
fresh scenarios entirely without Gazebo.

## Phase 08.8 M4.10 v8.9 correction-plan checkpoint — 2026-07-31

The separately versioned dual-topology correction Plan and live-status
boundary received the required Phase 08 checkpoint against v8.8 failure
HEAD `ec1645c`.

```text
base HEAD:
  ec1645c
status sha256 before this checkpoint note:
  18da28174837e6e4c8591d3129f8f669b2091c15015ce6e04ecf19ed619145bd
active plan sha256:
  5dde1f6be543939e27145ac7fc0a0b32da47b2613b0e60901030652d95e24892
checkpoint sha256 before this checkpoint note:
  b10ea7f755652a14105360afa31166ef7f1fc46ac2a1a8c79fb23bdd0eb313f6
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active Gazebo/scenario/recorder/analyzer:
  none
```

## Current milestone

**PHASE 08.8 M4.10 — V8.9 SCHEMA-V13 DUAL-TOPOLOGY CORRECTION PLAN /
CHECKPOINT PASS / PLAN COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact Plan boundary. Then implement schema-v13 direct and
assisted command-ownership evidence, historical compatibility, tests, and
fresh v8.9 scenarios. Gazebo remains prohibited until the complete
no-Gazebo qualification is checkpointed and committed.

## Phase 08.8 M4.10 v8.9 no-Gazebo implementation qualification — 2026-07-31

The schema-v13 dual-topology evaluator, compatibility guards, negative
fixtures, and four fresh fixed inputs are implemented and qualified without
Gazebo.

Schema v13 adds:

```text
escape_command_ownership
```

and accepts exactly the measured direct and stall-triggered assisted recovery
paths. Direct recovery requires positive frozen-geometry, mature-progress,
ordinary-GESC ownership, stable-cleanup, measured-distance, and alignment
proof. Any assist state selects the complete unchanged schema-v12 entry and
schema-v11 exit proof; a failed assist cannot use the direct branch. Schema
versions through 12 retain their existing behavior.

Immutable replay results:

```text
seed 19616 under original schema 12:
  Stage A / ranking / proximity: false / false / false
  unchanged assist-only formal failure

same messages under schema 13:
  branch: direct_repulse
  Stage A / ranking / proximity / ownership: true / true / true / true
  raw states / diagnostics / commands: 466 / 3,010 / 466
  synchronized analyzer rows: 3,015
  supervisor contribution and combined-GESC error: 0.0 / 0.0
  mature state/analyzer samples: 407 / 2,640
  exit distance / radius: 1.4011374666 / 1.3667708294 m
  alignment: 0.9475175293

seed 19611 under schemas 12 and 13:
  assisted proof: true / true
  schema-v13 branch: assisted
  entry / exit modes: bounded_causal_schema_v12 /
                      bounded_causal_schema_v11
  non-wrapper evidence differences: none
```

Retained replay:

```text
/tmp/phase08_8_m4_10_v8_9_retained_replay.log
e064ae7e4b59d75c87ece6970e0ab77dd3194f940037ff5eb25b3fdbfac87300
```

Final tests:

```text
schema + runner:
  356 passed, 1 skipped in 55.62 s
focused controller/supervisor/detector/legacy:
  310 passed in 8.49 s
focused evidence/recording/analysis:
  643 passed, 2 skipped in 131.53 s
broad ROS-independent functional:
  953 passed, 3 skipped in 142.17 s
fatal changed-file lint:
  PASS
Python/YAML/XML/diff/context:
  PASS
```

The broad skips are the unchanged copyright-template check and two explicit
Gazebo opt-ins. Full changed-file style reports only the inherited D202 in
`run_scenario.py`; no required fatal lint code is present.

Fresh installed qualification:

```text
root:
  /tmp/phase08_8_v8_9_release_qual.2fWDxv
build:
  3 packages finished in 11.9 s
source/install parity:
  10/10
installed schema:
  13, supported 1..13
installed launch checks:
  2/2 pass
installed node construction:
  4/4 expected bounded timeout 124, no startup error
installed dry-runs:
  primary visible / repeats:   1 / 10, zero unsupported
  secondary visible / repeats: 1 / 5, zero unsupported
sealed roots after dry-run:
  absent 4/4
```

All four v8.9/v8.8 pairs have explicit whole-document normalization proof.
Only schema/evidence paths and events, predicate identity, versioned
identities/descriptions/roots, and fresh seeds differ. Sources, starts,
`400/1600` intensities, launch overrides, controller behavior, Stage A/Stage
B budgets, evaluator-only `0.50 m` simulation stop, final-zero, cleanup, and
first-failure rules are unchanged.

Durable qualification:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_10_no_gazebo_qualification.md
```

Historical V6, v8-v8.8 scenarios, worlds, results, and failures remain
unchanged and selectable. No Gazebo, scenario runner, recorder, analyzer,
rosbag recorder, or physical process is active. All four v8.9 run roots are
absent. Physical stopping remains manual operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M4.10 — V8.9 SCHEMA-V13 DUAL-TOPOLOGY IMPLEMENTATION /
NO-GAZEBO QUALIFICATION PASS / IMPLEMENTATION CHECKPOINT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Run the Phase 08 implementation checkpoint and commit the exact qualified
source, scenarios, tests, report, and live status. Then create a separate
checkpointed and committed visible-dispatch boundary. Do not start Gazebo
from the uncommitted implementation.

## Phase 08.8 M4.10 v8.9 implementation checkpoint — 2026-07-31

The qualified schema-v13 evaluator, four fresh inputs, negative and
compatibility tests, retained-replay record, no-Gazebo qualification, and
live status received the required Phase 08 checkpoint against correction-plan
HEAD `1ce890d`.

```text
base HEAD:
  1ce890de78d3fe83de01a008e63d8e087938dd03
status sha256 before this checkpoint note:
  deabac612c2c66e35f17c424c8c0da6c3a446bf62c860a84318089f1bbc1dd1f
active plan sha256:
  5dde1f6be543939e27145ac7fc0a0b32da47b2613b0e60901030652d95e24892
no-Gazebo qualification sha256:
  a6919f2949ba722dfc36bad9ac949901a468f2b85a6c9a1f5c238061fcae8dc0
checkpoint sha256 before this checkpoint note:
  fbc78db300f10adc25f4b5843adccaed7390010faf99fe61f938f22ffb01d0dd
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active Gazebo/scenario/recorder/analyzer:
  none
sealed v8.9 run roots:
  absent 4/4
```

## Current milestone

**PHASE 08.8 M4.10 — V8.9 SCHEMA-V13 DUAL-TOPOLOGY IMPLEMENTATION /
NO-GAZEBO QUALIFICATION PASS / IMPLEMENTATION CHECKPOINT PASS /
IMPLEMENTATION COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact qualified implementation boundary. Then write, checkpoint,
and commit a separate dispatch authorization naming only the installed
visible primary seed `19701`. Do not start Gazebo before both commits exist
and the worktree is clean.

## Phase 08.8 M4.10 v8.9 primary-visible dispatch boundary — 2026-07-31

The complete no-Gazebo-qualified implementation is committed:

```text
270bba0 phase 08.8: qualify v8.9 dual recovery evidence
```

The worktree was clean immediately after that commit. This boundary
authorizes exactly one installed visible primary dispatch:

```text
installed scenario:
  /tmp/phase08_8_v8_9_release_qual.2fWDxv/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_9_primary_visible_probe.yaml
installed scenario SHA-256:
  2131b9b77587c7326e31acb63a6922ce4fbd81655b711f0b119f1c97be4c736c
seed:
  19701
GUI:
  enabled
ROS_DOMAIN_ID:
  224
scenario run timeout:
  720.0 s
scenario wall timeout:
  900.0 s
outer process bound:
  960 s with bounded interrupt/kill escalation
run root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_9_primary_probe
attempts:
  one
retry:
  prohibited
```

During the sealed run, observation is limited to OS process state and
retained files. No external ROS/DDS participant may join domain `224`.
After population closure and cleanup, the dispatched run must be analyzed
exactly once and all nine plots retained.

A behavioral, schema-v13 command-ownership, required-path/event,
strict-ranking, global-proximity, recording, final-zero, readiness, or
cleanup failure closes this visible gate. Only a formal pass authorizes the
ten primary repeats. No repeat, secondary, three-light, broader, or physical
execution is authorized by this boundary.

## Current milestone

**PHASE 08.8 M4.10 — V8.9 IMPLEMENTATION COMMITTED AT `270bba0` /
PRIMARY VISIBLE SEED `19701` DISPATCH BOUNDARY WRITTEN / DISPATCH
CHECKPOINT PENDING / GAZEBO NOT YET AUTHORIZED.**

## Next criterion

Checkpoint and commit this exact dispatch boundary. Verify the worktree is
clean, the installed scenario hash still matches, the run root remains
absent, and no runtime process is active. Then execute seed `19701` exactly
once with visible Gazebo and no ROS-domain monitoring.

## Phase 08.8 M4.10 v8.9 primary-visible dispatch checkpoint — 2026-07-31

The installed seed-`19701` one-time/no-retry visible-dispatch boundary
received the required Phase 08 checkpoint against implementation HEAD
`270bba0`.

```text
base HEAD:
  270bba0c5222b3562d4a2f4db5e5e388f65dbc79
status sha256 before this checkpoint note:
  5d3a565d5c633210a740615ab1724bc5f64fd3cf1fd50a23a836b8c34a796802
active plan sha256:
  5dde1f6be543939e27145ac7fc0a0b32da47b2613b0e60901030652d95e24892
installed scenario sha256:
  2131b9b77587c7326e31acb63a6922ce4fbd81655b711f0b119f1c97be4c736c
checkpoint sha256 before this checkpoint note:
  5c1fb40d0a8e0c3d9b83486b5a155dcdc1e0b9b5fe72d3b1c348e3a56438d8d7
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active runtime:
  none
primary visible run root:
  absent
```

## Current milestone

**PHASE 08.8 M4.10 — V8.9 IMPLEMENTATION COMMITTED / PRIMARY VISIBLE
SEED `19701` DISPATCH BOUNDARY CHECKPOINT PASS / DISPATCH COMMIT PENDING /
GAZEBO NOT YET AUTHORIZED.**

## Next criterion

Commit this exact dispatch boundary. Reverify a clean worktree, installed
scenario hash, absent root, and inactive runtime. Then dispatch visible seed
`19701` exactly once on domain `224`, with no retry and no ROS-domain
monitoring.

## Phase 08.8 M4.10 fixed v8.9 primary-visible result — 2026-07-31

The one authorized installed seed-`19701` attempt closed before Gazebo or the
recording graph started:

```text
runner return:          1
record_run return:      2
classification:         failed / runner_or_recorder_failure
recording complete:     false
cleanup:                pass
bag:                    absent
behavioral predicates:  unavailable
retry:                  prohibited
```

`record_run` failed while constructing Git metadata:

```text
git rev-parse --show-toplevel
return code 128
```

The installed runner had been invoked after `cd /tmp`. Although
`run_scenario.py` resolves and retains `REPOSITORY_ROOT`, its staged
global-proximity recorder owner launched the child without a working
directory. The child inherited `/tmp`, and `record_run.py` called
`git_state(Path.cwd())`. A read-only invocation of the same Git command from
`/tmp` reproduces return code `128`. No Gazebo process ever started.

The fixed retained evidence is:

```text
run:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_9_primary_probe/2026-07-31/
  20260731T165942441730Z_simulation_phase08_v8_9_primary_visible_probe-
  v8_9_primary_probe_r1p5_a45_h25_19701-robust__59eb6408
summary:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_9_primary_probe/scenario_summaries/
  20260731T165941455647Z_phase08_v8_9_primary_visible_probe.yaml
dispatch log:
  /tmp/phase08_8_m4_10_v8_9_primary_visible_dispatch.log
```

Hashes:

```text
scenario definition: 2131b9b77587c7326e31acb63a6922ce4fbd81655b711f0b119f1c97be4c736c
summary:             c1f322e48eb06132a9dcf065d9d11f039dd5275842bf42caa19318ad47f7cdf7
scenario result:     9f4a5318c63f1d4d4ba4751fefd5e92c995e420dcffc418c1949e28430b78daa
resolved scenario:   8fb444ff46d98e47ad3781829355cade828f94ea37b572cc8debc66b1bae1296
notes:               b5b0ce3e05f57f6c6b7e53f6cf03a7d46426b403efc13b5ea39ed72cc3d8fa11
dispatch log:        324afa05e4491f930b47af517efe631c1663c201d6cb6b585d5516be76f2900f
```

The required analyzer was invoked once after closure. Its manually
transcribed target omitted `_19701`, so it returned `2` before analysis.
No second invocation is made; no bag existed to analyze in either case.

```text
/tmp/phase08_8_m4_10_v8_9_primary_visible_analysis.log
64414c17fef8838ad148dec1b4d911e733271dc8bbcb5dad992dc8f2c31102b0
```

Durable result:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_10_primary_probe.md
```

V8.9 is closed as an infrastructure failure. Seed `19701` is not retried,
and all later v8.9 gates remain prohibited. This is not a behavioral result
and does not change the completed schema-v13 retained-replay qualification.
No active Gazebo, scenario-runner, recorder, rosbag-recorder, analyzer, or
physical process remains.

## Current milestone

**PHASE 08.8 M4.10 — V8.9 PRIMARY VISIBLE FIXED PRE-GAZEBO
INFRASTRUCTURE FAIL / NO RETRY / RESULT CHECKPOINT PENDING / ALL LATER
V8.9 GATES PROHIBITED.**

## Next criterion

Checkpoint and commit the exact failed v8.9 result. Then plan a fresh v8.10
runner/recorder working-directory correction with new scenario identities,
roots, and seeds. Gazebo remains prohibited until the new version is
implemented, qualified without Gazebo, checkpointed, and committed.

## Phase 08.8 M4.10 v8.9 failed-result checkpoint — 2026-07-31

The fixed pre-Gazebo infrastructure failure, retained artifact references,
one failed analyzer invocation, causal diagnosis, no-retry disposition, and
fresh-version correction boundary received the required Phase 08 checkpoint
against dispatch HEAD `95efaa5`.

```text
base HEAD:
  95efaa5b4ae980d3fcbfef5687b7f82568176590
status sha256 before this checkpoint note:
  d1b56829e440bd27c5a65aec3f791f730f28d57d160d42703b30f2344eb0c89a
active plan sha256:
  5dde1f6be543939e27145ac7fc0a0b32da47b2613b0e60901030652d95e24892
failed-result report sha256:
  034c6136a1701295539b3cd4d36c3914cbd6d64e7084dd9e3350301162a04b49
checkpoint sha256 before this checkpoint note:
  ca1f1abcc5f97589496ce1a3624581017312a5fd77c256d2e23b381e78007f0e
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active runtime:
  none
```

## Current milestone

**PHASE 08.8 M4.10 — V8.9 PRIMARY VISIBLE FIXED PRE-GAZEBO
INFRASTRUCTURE FAIL / NO RETRY / RESULT CHECKPOINT PASS / RESULT COMMIT
PENDING / ALL LATER V8.9 GATES PROHIBITED.**

## Next criterion

Commit this exact failed-result boundary. Then write and checkpoint the fresh
v8.10 correction Plan before changing runner code or scenario inputs.
Gazebo remains prohibited.

## Phase 08.8 M4.11 v8.10 recorder-CWD correction plan — 2026-07-31

The fixed v8.9 failure is committed:

```text
4690b3a phase 08.8: retain failed v8.9 primary probe
```

The active Plan now defines v8.10 as a fresh infrastructure-corrected
experiment. It will pass the already-resolved `REPOSITORY_ROOT` as the child
working directory in all three scenario-runner recorder owners:

```text
normal
boundary-observed
staged local-recovery/global-proximity
```

`record_run.py`, the controller, supervisor, detector, fills, affine term,
costs, ranking, schema-v13 evidence, source model, world, motion behavior,
timeouts, final-zero, cleanup, and physical path remain unchanged. Focused
tests must prove all three child launches receive the checkout root while
retaining existing process and lifecycle semantics.

Four fresh schema-v13 inputs are planned:

```text
primary visible:     seed 19801 / root phase08_8_10_primary_probe
primary repeats:     seeds 19811..19820 / root phase08_8_10_primary_repeats
secondary visible:   seed 19851 / root phase08_8_10_secondary_probe
secondary repeats:   seeds 19861..19865 / root phase08_8_10_secondary_repeats
```

They copy all v8.9 scientific inputs and gates. Only identities,
descriptions, roots, and seeds change. Runtime domains are reserved as
`225..228`.

Analysis must read each `run_directory` from the exact runner-emitted
scenario summary and may never manually reconstruct a run ID. Each complete
run receives one analyzer invocation after population closure.

No Gazebo process is authorized until the runner correction, tests, four
fresh scenarios, complete regression envelope, isolated build,
source/install parity, and installed `/tmp` dry-runs are documented,
checkpointed, and committed. The first later dispatch boundary may authorize
only visible seed `19801`.

The v8.10 claim remains limited to the two fixed obstacle-free,
two-source, local-first layouts at relative `400/1600`; it does not claim
arbitrary layout/intensity or three-light robustness. Physical stopping
remains manual operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M4.11 — V8.9 FAILURE COMMITTED / V8.10 RECORDER-CWD
CORRECTION PLAN WRITTEN / PLAN CHECKPOINT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Checkpoint and commit the exact v8.10 correction Plan and status boundary.
Then implement only the declared runner, tests, and fresh scenario inputs
and complete the no-Gazebo qualification.

## Phase 08.8 M4.11 v8.10 correction-plan checkpoint — 2026-07-31

The fresh recorder-working-directory correction, three-path test contract,
summary-owned analysis rule, four versioned inputs, no-Gazebo qualification,
and gated runtime sequence received the required Phase 08 checkpoint against
fixed-v8.9-result HEAD `4690b3a`.

```text
base HEAD:
  4690b3abf8e8736ea6bdb6d1d255c780eb4b6047
status sha256 before this checkpoint note:
  3032d2c49a24def268f4da233742eb978dc0f145d630f44dcc403e696f2a44ec
active plan sha256:
  9d7a7ea410c43dfc1e404c6bba30453dfd4d2d593fe74eb72c2648913246dcbb
checkpoint sha256 before this checkpoint note:
  1fb7567fd04d0a85bb5311460318abf05f04507a6281f22967e57e7c42304d65
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active runtime:
  none
```

## Current milestone

**PHASE 08.8 M4.11 — V8.10 RECORDER-CWD CORRECTION PLAN / PLAN
CHECKPOINT PASS / PLAN COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact Plan boundary. Then implement the three recorder-child
working-directory arguments, focused tests, and four fresh v8.10 scenarios.
Do not start Gazebo before complete no-Gazebo qualification, checkpoint, and
implementation commit.

## Phase 08.8 M4.11 v8.10 no-Gazebo implementation qualification — 2026-07-31

The narrow scenario-runner/recorder correction is implemented and qualified
without Gazebo. All three `record_run` process owners now pass the already
resolved checkout as:

```text
cwd=REPOSITORY_ROOT
```

Focused tests prove the normal, boundary-observed, and staged
global-proximity child paths use that root while preserving process,
timeout, private-context, signal, and lifecycle behavior. An arbitrary
caller directory is not propagated.

The four fresh schema-v13 inputs are:

```text
c41eea1e6e10d8f736bb669fdf13db46eb8a6ed23b512a5827e8675d2d5c501b
  phase08_v8_10_primary_visible_probe.yaml
cdb5e05339745d89afc632388af2e8bae45de75159c514f3d85832732361c796
  phase08_v8_10_primary_repeats.yaml
a0f9c7032be4e2540e3937cd741c9271c7358bba48dd5e6d41a23208a488f3ed
  phase08_v8_10_secondary_visible_probe.yaml
f7c54e8213f288b54051d69b06ae6ba1e75daf328763488ea970ebaffe550b3e
  phase08_v8_10_secondary_repeats.yaml
```

Whole-document normalization proves only identities, descriptions, roots,
and fresh seeds differ from v8.9. Controller behavior, sources,
`400/1600` intensities, topology, schema-v13 evidence, Stage A/Stage B,
evaluator-only `0.50 m` stop, final-zero, cleanup, and first-failure rules
are unchanged.

Final tests:

```text
targeted correction:
  10 passed, 357 deselected in 1.31 s
schema + runner:
  366 passed, 1 skipped in 56.24 s
focused controller/supervisor/detector/legacy:
  310 passed in 8.50 s
focused evidence/recording/analysis:
  653 passed, 2 skipped in 133.17 s
broad ROS-independent functional:
  963 passed, 3 skipped in 141.73 s
fatal changed-file lint:
  PASS
Python/YAML/XML/diff/context:
  PASS
```

The broad skips are the unchanged copyright-template check and two explicit
Gazebo opt-ins. Package-style lint reports only the inherited D202 in
`run_scenario.py`.

The read-only retained replay passes:

```text
seed 19616 original schema 12:
  Stage A / ranking / proximity / assisted:
  false / false / false / false
same immutable bag with v8.10 schema 13:
  direct ownership / Stage A / ranking / proximity:
  true / true / true / true
  states / controls / commands / mature progress:
  466 / 3,010 / 466 / 407
  exit distance / radius / alignment:
  1.4011374666 / 1.3667708294 / 0.9475175293
seed 19611:
  assisted ownership passes schemas 12 and 13
  entry / exit:
  bounded_causal_schema_v12 / bounded_causal_schema_v11
```

Replay:

```text
/tmp/phase08_8_m4_11_v8_10_retained_replay.log
b24fa96e9f0aadbaf57e618f1a82c9da8d16cd2b34e4e49b18b7a03bd6287ba5
```

Fresh installed qualification:

```text
root:
  /tmp/phase08_8_v8_10_release_qual.VIowrN
build:
  3 packages finished in 11.8 s
source/install parity:
  10/10
installed schema:
  13, supported 1..13
installed launch checks:
  2/2 pass
installed node construction:
  4/4 expected bounded timeout 124, no startup error
installed /tmp dry-runs:
  primary visible / repeats:   1 / 10, zero unsupported
  secondary visible / repeats: 1 / 5, zero unsupported
fresh roots after dry-run:
  absent 4/4
```

Durable qualification:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_11_no_gazebo_qualification.md
```

Historical V6, shifted worlds, v8-v8.9 scenarios, results, plots, and fixed
failures remain unchanged and selectable. No Gazebo, scenario runner,
recorder, analyzer, rosbag recorder, or physical process is active. Physical
stopping remains manual operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M4.11 — V8.10 RECORDER-CWD IMPLEMENTATION / NO-GAZEBO
QUALIFICATION PASS / IMPLEMENTATION CHECKPOINT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Run the Phase 08 implementation checkpoint and commit the exact correction,
tests, scenarios, qualification, and status. Then create a separate
checkpointed and committed dispatch boundary for only installed visible seed
`19801`.

## Phase 08.8 M4.11 v8.10 implementation checkpoint — 2026-07-31

The qualified three-path recorder working-directory correction, four fresh
inputs, tests, retained replay, isolated build, installed dry-runs,
no-Gazebo report, and live status received the required Phase 08 checkpoint
against correction-plan HEAD `8edf6e3`.

```text
base HEAD:
  8edf6e3a97ea09c5900eaa153f189ab2479d8cf5
status sha256 before this checkpoint note:
  dc50920ac746aa13eb8e7c092e0c0fe68c2ce2ac414b5dab8b8426145e9af646
active plan sha256:
  9d7a7ea410c43dfc1e404c6bba30453dfd4d2d593fe74eb72c2648913246dcbb
no-Gazebo qualification sha256:
  ad5aa62eb37c30fa56d8422cf8748f98509c066f6689d84664432a0eca4b221d
checkpoint sha256 before this checkpoint note:
  f40035903b6336c03caa4531c77b5e11d7830cd55bf523a12dc2afe544793e21
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active runtime:
  none
fresh v8.10 run roots:
  absent 4/4
```

## Current milestone

**PHASE 08.8 M4.11 — V8.10 RECORDER-CWD IMPLEMENTATION / NO-GAZEBO
QUALIFICATION PASS / IMPLEMENTATION CHECKPOINT PASS / IMPLEMENTATION
COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact qualified implementation boundary. Then write, checkpoint,
and commit a separate visible-dispatch authorization naming only the
installed seed `19801`. Do not start Gazebo from the uncommitted
implementation.

## Phase 08.8 M4.11 v8.10 primary-visible dispatch boundary — 2026-07-31

The complete no-Gazebo-qualified implementation is committed:

```text
77dd443 phase 08.8: qualify v8.10 recorder cwd correction
```

The worktree was clean immediately after that commit. This boundary
authorizes exactly one installed visible primary dispatch:

```text
installed scenario:
  /tmp/phase08_8_v8_10_release_qual.VIowrN/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_10_primary_visible_probe.yaml
installed scenario SHA-256:
  c41eea1e6e10d8f736bb669fdf13db46eb8a6ed23b512a5827e8675d2d5c501b
seed:
  19801
GUI:
  enabled
ROS_DOMAIN_ID:
  225
scenario run timeout:
  720.0 s
scenario wall timeout:
  900.0 s
outer process bound:
  960 s with bounded interrupt/kill escalation
run root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_probe
attempts:
  one
retry:
  prohibited
```

During the sealed run, observation is limited to OS process state and
retained files. No external ROS/DDS participant may join domain `225`.
After closure and cleanup, the exact `summary_path` emitted by the runner
must be read. Its sole `run_directory` must be validated below the declared
root and used verbatim for the one analyzer invocation; no run ID may be
manually reconstructed.

The finalized recorder metadata must identify working directory
`/home/mattb/dsim-lab`, committed dispatch HEAD `77dd443`, and an initially
clean tree. A behavioral, schema-v13 command-ownership,
required-path/event, strict-ranking, global-proximity, recording, Git
metadata, final-zero, readiness, analysis, or cleanup failure closes this
visible gate.

Only a formal pass and complete nine-plot analysis authorize the ten v8.10
primary repeats. No repeat, secondary, three-light, broader, or physical
execution is authorized by this boundary.

## Current milestone

**PHASE 08.8 M4.11 — V8.10 IMPLEMENTATION COMMITTED AT `77dd443` /
PRIMARY VISIBLE SEED `19801` DISPATCH BOUNDARY WRITTEN / DISPATCH
CHECKPOINT PENDING / GAZEBO NOT YET AUTHORIZED.**

## Next criterion

Checkpoint and commit this exact dispatch boundary. Verify the worktree is
clean, installed scenario hash still matches, the run root remains absent,
and no runtime process is active. Then execute seed `19801` exactly once
with visible Gazebo and no ROS-domain monitoring.

## Phase 08.8 M4.11 v8.10 primary-visible dispatch checkpoint — 2026-07-31

The installed seed-`19801` one-time/no-retry visible-dispatch boundary
received the required Phase 08 checkpoint against implementation HEAD
`77dd443`.

```text
base HEAD:
  77dd443a5e24f340b106a48c5ea4e4d8859c3040
status sha256 before this checkpoint note:
  63ff453d5e69a9bb61106d2917fda6408136805e428fa81ba0abc0318a46efad
active plan sha256:
  9d7a7ea410c43dfc1e404c6bba30453dfd4d2d593fe74eb72c2648913246dcbb
installed scenario sha256:
  c41eea1e6e10d8f736bb669fdf13db46eb8a6ed23b512a5827e8675d2d5c501b
checkpoint sha256 before this checkpoint note:
  8c8bcb4e9362588f86b24644fc2d9d676380fb266a7493591c8b680bb8d3e6f4
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active runtime:
  none
primary visible run root:
  absent
```

## Current milestone

**PHASE 08.8 M4.11 — V8.10 IMPLEMENTATION COMMITTED / PRIMARY VISIBLE
SEED `19801` DISPATCH BOUNDARY CHECKPOINT PASS / DISPATCH COMMIT PENDING /
GAZEBO NOT YET AUTHORIZED.**

## Next criterion

Commit this exact dispatch boundary. Reverify a clean worktree, installed
scenario hash, absent root, and inactive runtime. Then dispatch visible seed
`19801` exactly once on domain `225`, with no retry and no ROS-domain
monitoring.

## Phase 08.8 M4.11 v8.10 primary-visible result — 2026-07-31

The one authorized installed visible seed `19801` execution is a formal
pass. It ran once from `/tmp` with Gazebo GUI enabled on isolated domain
`225`, with no retry and no external ROS/DDS monitoring.

```text
committed dispatch HEAD:
  f96edfd302fbd6fed7f48263ace766d0b425a20a
installed scenario:
  /tmp/phase08_8_v8_10_release_qual.VIowrN/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_10_primary_visible_probe.yaml
scenario sha256:
  c41eea1e6e10d8f736bb669fdf13db46eb8a6ed23b512a5827e8675d2d5c501b
started:
  2026-07-31T17:30:55.946255Z
completed:
  2026-07-31T17:36:48.717776Z
runner / recorder:
  0 / 0
recording / completeness / final zero / cleanup:
  PASS / PASS / PASS / PASS
formal predicates:
  14/14 PASS
```

The exact summary is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_probe/
  phase08_v8_10_primary_visible_probe_summary.yaml
sha256:
  f37e9cab4ab790e647897118c576635ad6011bba211d882da84f2ba7c78b6a73
```

It contains exactly one selected/resolved case and supplied the exact run
directory used for the sole analyzer invocation:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_probe/2026-07-31/
  20260731T173056885644Z_simulation_phase08_v8_10_primary_visible_probe-
  v8_10_primary_probe_r1p5_a45_h25_19801-robus_d984451c
```

The recorder-CWD correction is proven in fresh runtime metadata:

```text
working_directory / repository_root:
  /home/mattb/dsim-lab
commit:
  f96edfd302fbd6fed7f48263ace766d0b425a20a
dirty / untracked:
  false / []
```

The exact behavioral path passed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Stage A completed at `168.713 s` with exactly one created, typed, and active
fill. The convergence was `0.341375 m` from the declared local and the fill
was `0.158120 m` from that convergence.

Schema-v13 selected the assisted branch and passed both command-ownership
topologies:

```text
assist entry:
  bounded_causal_schema_v12, 0.003215288 s, 2,731 steady owned samples
exit:
  bounded_causal_schema_v11, 0.011156662 s, 15,024 ordinary samples
selected/actual alignment:
  0.993861949
fill-to-exit distance:
  1.471256 m
failsafe / timeout:
  false / false
```

The second raw-cost interval
`[-3.8372093023255816, -3.8372093023255816]` was strictly below the first
candidate lower bound `-2.938548817736818`, with margin
`0.8986604845887634`. The controller emitted ranked `GOAL_REACHED` for
ordinal two with one filled candidate and known source count two.

The first valid post-ranking evaluator sample was noninterpolated, at
simulation time `293.935 s` and distance `0.104594 m` from `(3.5, 3.5)`.
The retained final distance is `0.104573 m`. Approximate Stage B duration
was `125.222 s`.

Analysis ran exactly once after closure from the summary-owned path:

```text
analysis log:
  /tmp/phase08_8_m4_11_v8_10_primary_visible_analysis.log
sha256:
  4d3c1fa9b383d5f273b81e1a2c5b7c804a5ddf8f9e504cf8029de1a65d89e08d
status / failures / fresh validator:
  complete / [] / PASS
plots:
  9/9
```

The trajectory plot was visually inspected and agrees with the formal path.
The complete result is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_11_primary_probe.md
```

Level B evidence erratum: the prior dispatch text called implementation
commit `77dd443` the "committed dispatch HEAD." The actual clean committed
dispatch tree, correctly captured by runtime metadata, is `f96edfd`. This is
a documentation-only correction and changes no runtime evidence or gate.

The GUI, scenario runner, recorder, analyzer, rosbag recorder, and their
descendants are inactive. Physical motion did not occur. The evaluator-only
simulation stop remains absent from the physical path; physical stopping is
manual operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M4.11 — V8.10 PRIMARY VISIBLE SEED `19801` FORMAL PASS /
ONE-TIME ANALYSIS COMPLETE / NINE PLOTS COMPLETE / RESULT CHECKPOINT
PENDING / PRIMARY REPEATS NOT YET AUTHORIZED.**

## Next criterion

Checkpoint and commit this exact visible result. Then write, checkpoint, and
commit a separate serial/headless primary-repeat boundary for installed
seeds `19811..19820`. Do not dispatch any repeat before that clean committed
boundary.

## Phase 08.8 M4.11 v8.10 primary-visible result checkpoint — 2026-07-31

The formal visible result, summary-owned one-time analysis, nine plots,
recorder-CWD proof, Level B dispatch-HEAD wording erratum, and inactive
runtime received the required Phase 08 checkpoint against committed
dispatch HEAD `f96edfd`.

```text
base HEAD:
  f96edfd302fbd6fed7f48263ace766d0b425a20a
status sha256 before this checkpoint note:
  d61b0e02dba971220c630722d0c23926ef29c1d6237c79614710f090a696d807
active plan sha256:
  9d7a7ea410c43dfc1e404c6bba30453dfd4d2d593fe74eb72c2648913246dcbb
primary-visible report sha256:
  6421d1fed9fbbafb2e47bec0723d4bb66789c69f44e7d49128a749ca392a4dc4
checkpoint sha256 before this checkpoint note:
  5da39cabbaad769ba8c97d2dc0048476530132377aa338092021fc8e82275c20
installed scenario sha256:
  c41eea1e6e10d8f736bb669fdf13db46eb8a6ed23b512a5827e8675d2d5c501b
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active runtime:
  none
```

## Current milestone

**PHASE 08.8 M4.11 — V8.10 PRIMARY VISIBLE SEED `19801` FORMAL PASS /
ONE-TIME ANALYSIS COMPLETE / NINE PLOTS COMPLETE / RESULT CHECKPOINT
PASS / RESULT COMMIT PENDING / PRIMARY REPEATS NOT YET AUTHORIZED.**

## Next criterion

Commit this exact visible result. Then write, checkpoint, and commit a
separate serial/headless primary-repeat boundary for installed seeds
`19811..19820`. Do not dispatch any repeat from an uncommitted boundary.

## Phase 08.8 M4.11 v8.10 primary-repeat dispatch boundary — 2026-07-31

The primary visible result is sealed in:

```text
de2e10a phase 08.8: pass v8.10 primary visible probe
```

The worktree was clean immediately after that commit. The formal visible
pass authorizes this separate fixed primary-repeat boundary:

```text
installed scenario:
  /tmp/phase08_8_v8_10_release_qual.VIowrN/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_10_primary_repeats.yaml
installed scenario SHA-256:
  cdb5e05339745d89afc632388af2e8bae45de75159c514f3d85832732361c796
seeds:
  19811, 19812, 19813, 19814, 19815,
  19816, 19817, 19818, 19819, 19820
execution:
  one installed suite invocation, serial, headless
ROS_DOMAIN_ID:
  226
scenario run timeout:
  720.0 s per run
scenario wall timeout:
  900.0 s per run
outer suite bound:
  9,600 s with bounded interrupt/kill escalation
run root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_repeats
stop on first run or cleanup failure:
  true
retry:
  prohibited
```

The installed scenario resolves exactly ten supported runs, uses no GUI,
and retains the same fixed primary source layout, `400/1600` inputs,
schema-v13 direct-or-assisted ownership contract, exact one-fill
cardinality, Stage A/Stage B budgets, strict two-candidate raw ranking,
evaluator-only `0.50 m` stop, forbidden states/events, final-zero rule, and
cleanup rule as the passing visible probe.

During the sealed suite, observation is limited to OS process state and
retained files. No external ROS/DDS participant may join domain `226`.
Dispatch stops at the first behavioral, formal, infrastructure, recording,
metadata, or cleanup failure. An interrupted or failed seed is retained and
is not retried; undispatched later seeds remain undispatched.

After the population closes and cleanup is proven, analysis preparation
must read this exact runner-emitted summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_repeats/
  phase08_v8_10_primary_repeats_summary.yaml
```

It must require the exact executed count and ordered case/seed identities,
read every `run_directory` directly from the summary, verify each directory
is below the fresh root and has a complete bag, and invoke `analyze_run`
exactly once per dispatched complete run. No target may be selected by
modification time or reconstructed from a run ID.

Every finalized recorder metadata file must identify working directory and
repository root `/home/mattb/dsim-lab`, the eventual clean committed
repeat-dispatch HEAD, and no untracked path. A summary-target, analyzer,
fresh-validator, or plot failure closes the population after the required
one-time analyzer invocations; it is not repaired by rerunning analysis.

Only a `10/10` formal population pass, complete one-time analysis of all ten
runs, and uncontaminated cleanup authorize the secondary visible seed
`19851`. No secondary repeat, three-light, broader, physical, or Phase 09
execution is authorized by this boundary.

## Current milestone

**PHASE 08.8 M4.11 — V8.10 PRIMARY VISIBLE RESULT COMMITTED AT `de2e10a` /
TEN-RUN PRIMARY-REPEAT BOUNDARY WRITTEN / REPEAT CHECKPOINT PENDING /
PRIMARY REPEATS NOT YET AUTHORIZED.**

## Next criterion

Checkpoint and commit this exact repeat boundary. Reverify a clean
worktree, unchanged installed scenario hash, absent repeat root, and
inactive runtime. Then invoke the installed ten-run suite once from `/tmp`
on domain `226`.

## Phase 08.8 M4.11 v8.10 primary-repeat dispatch checkpoint — 2026-07-31

The fixed ten-seed, one-invocation, serial/headless, stop-on-first-failure,
no-retry primary-repeat boundary received the required Phase 08 checkpoint
against primary-visible result HEAD `de2e10a`.

```text
base HEAD:
  de2e10a6ce93f9d37b7cd9a06cfe562df5e87b54
status sha256 before this checkpoint note:
  8297eafa45d5e2a8befae16e6d7bfdbc6f59a77156d21c00f79f84b9a62633b2
active plan sha256:
  9d7a7ea410c43dfc1e404c6bba30453dfd4d2d593fe74eb72c2648913246dcbb
checkpoint sha256 before this checkpoint note:
  fa9f7eefd61545e647dfa616d8b057db506fd9fc0ba8bf7fc627cda8f6bf5bdd
installed scenario sha256:
  cdb5e05339745d89afc632388af2e8bae45de75159c514f3d85832732361c796
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active runtime:
  none
primary-repeat run root:
  absent
```

## Current milestone

**PHASE 08.8 M4.11 — V8.10 PRIMARY VISIBLE RESULT COMMITTED / TEN-RUN
PRIMARY-REPEAT BOUNDARY CHECKPOINT PASS / REPEAT COMMIT PENDING / PRIMARY
REPEATS NOT YET AUTHORIZED.**

## Next criterion

Commit this exact repeat boundary. Reverify a clean worktree, unchanged
installed scenario hash, absent root, and inactive runtime. Then invoke the
installed suite once from `/tmp` on domain `226`, with no retry and no
ROS-domain monitoring.

## Phase 08.8 M4.11 v8.10 primary-repeat result — 2026-07-31

The sole installed primary-repeat suite invocation completed all ten seeds
in order with a `10/10` formal population pass.

```text
dispatch commit:
  ccf75cda3cd154737d02c619ad8ab60e30b827cf
installed scenario sha256:
  cdb5e05339745d89afc632388af2e8bae45de75159c514f3d85832732361c796
started:
  2026-07-31T17:46:46.863081Z
completed:
  2026-07-31T18:48:21.153945Z
resolved / executed / unsupported:
  10 / 10 / 0
formal:
  10 PASS / 0 FAIL
recording / completeness / final zero / cleanup:
  10/10 / 10/10 / 10/10 / 10/10
bag sqlite quick_check:
  10/10 ok
```

A pre-dispatch shell wrapper exited while sourcing ROS because Bash
`nounset` was already enabled. It invoked no runner, seed, or Gazebo process
and created neither run root nor dispatch log. The corrected wrapper then
made the sole installed suite invocation. No seed was retried.

The runner-emitted summary is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_primary_repeats/
  phase08_v8_10_primary_repeats_summary.yaml
sha256:
  4689b2d225ebc707dd41408417a4156123b1f74afa9ee02f4e499c478cd91b91
dispatch log:
  /tmp/phase08_8_m4_11_v8_10_primary_repeats_dispatch.log
sha256:
  f13e57d74b3b4ee42eaa9d36930f73951fc0cc720191d06ee27a2325f6abda14
```

The child wrapper captured runner return code `0`. The hosted execution
channel surfaced code `1` after printing that zero; the retained runner
summary, ten per-run results, complete recordings, and inactive process
audit are authoritative.

Every recorder metadata file identifies working directory and repository
root `/home/mattb/dsim-lab`, clean committed dispatch HEAD `ccf75cd`, and no
untracked path.

All ten seeds used:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Every run completed exactly one local-recovery episode, created exactly one
typed active fill, passed the schema-v13 assisted entry and exit ownership
contracts, restored ordinary GESC after exit, strictly ranked candidate two
below the retained candidate-one bound, and produced a noninterpolated
post-ranking sample inside the evaluator-only `0.50 m` radius.

Population ranges:

```text
Stage A:
  121.634 to 294.024 s
Stage B:
  100.402 to 127.704 s
global-proximity sample:
  0.106370 to 0.188827 m
final retained distance:
  0.106346 to 0.188818 m
strict ranking margin:
  0.094916 to 2.475247
selected/actual exit alignment:
  0.991816 to 0.999946
assist-entry / exit handoff maximum:
  9.999 / 11.238 ms
```

No run entered `RECENTER`, `FAILSAFE`, or `TIMEOUT`; no fill was rejected,
merged, superseded, or failed.

After population closure, every exact run path was read directly from that
summary and analyzed exactly once:

```text
analyze_run return zero:
  10/10
fresh Phase 05 validation:
  10/10
analysis failures:
  0
critical inputs:
  10/10
analysis status:
  9 complete / 1 partial
plots:
  90/90
```

Seed `19812` is `partial` only because one state-sampling gap exceeded
`0.150000 s`, invalidating the optional generic `state_durations` metric.
All core scientific metrics, formal evidence, critical inputs, fresh
validation, and nine plots are complete. Per the active plan's explicit
analysis interpretation, this is not a formal or analysis-bundle failure.
The analyzer was not rerun.

All ten trajectory plots were visually inspected and show start-to-local
capture, one fill, assisted exit, ordinary transit, and global capture.

The complete result and artifact hashes are:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_11_primary_repeats.md
```

No GUI, scenario runner, recorder, analyzer, rosbag recorder, or descendant
remains active. Physical motion did not occur. The evaluator-only simulation
stop remains absent from the physical path; physical stopping is manual
operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M4.11 — V8.10 PRIMARY REPEATS `10/10` FORMAL PASS / TEN
ONE-TIME ANALYSES COMPLETE / NINETY PLOTS COMPLETE / RESULT CHECKPOINT
PENDING / SECONDARY VISIBLE NOT YET AUTHORIZED.**

## Next criterion

Checkpoint and commit this exact primary-repeat result. Then write,
checkpoint, and commit a separate visible secondary-layout boundary naming
only installed seed `19851`. Do not dispatch the secondary probe before that
clean committed boundary.

## Phase 08.8 M4.11 v8.10 primary-repeat result checkpoint — 2026-07-31

The `10/10` formal population pass, ten summary-owned one-time analyses,
ninety plots, optional seed-`19812` analysis limitation, artifact hashes,
and inactive runtime received the required Phase 08 checkpoint against
committed repeat-dispatch HEAD `ccf75cd`.

```text
base HEAD:
  ccf75cda3cd154737d02c619ad8ab60e30b827cf
status sha256 before this checkpoint note:
  af3dd56af3b29bbce1dabe9688c34ddc60f84474a4688b817a695eaae5aea17e
active plan sha256:
  9d7a7ea410c43dfc1e404c6bba30453dfd4d2d593fe74eb72c2648913246dcbb
primary-repeat report sha256:
  8c0ae77de7813d3c55893c60058cd2b57c0a367437e959b3ccbebde586abfc61
checkpoint sha256 before this checkpoint note:
  daa73d69677419a922bb9f6ae1cea17b0624df491563d07d65262a8418d3ca79
summary sha256:
  4689b2d225ebc707dd41408417a4156123b1f74afa9ee02f4e499c478cd91b91
installed scenario sha256:
  cdb5e05339745d89afc632388af2e8bae45de75159c514f3d85832732361c796
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active runtime:
  none
```

## Current milestone

**PHASE 08.8 M4.11 — V8.10 PRIMARY REPEATS `10/10` FORMAL PASS / TEN
ONE-TIME ANALYSES COMPLETE / NINETY PLOTS COMPLETE / RESULT CHECKPOINT
PASS / RESULT COMMIT PENDING / SECONDARY VISIBLE NOT YET AUTHORIZED.**

## Next criterion

Commit this exact primary-repeat result. Then write, checkpoint, and commit
a separate visible secondary-layout boundary naming only installed seed
`19851`. Do not dispatch the secondary probe from an uncommitted boundary.

## Phase 08.8 M4.11 v8.10 secondary-visible dispatch boundary — 2026-07-31

The complete primary-repeat result is sealed in:

```text
512a898 phase 08.8: pass v8.10 primary repeats
```

The worktree was clean immediately after that commit. The `10/10` fixed
primary population pass authorizes exactly one installed visible secondary
dispatch:

```text
installed scenario:
  /tmp/phase08_8_v8_10_release_qual.VIowrN/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_10_secondary_visible_probe.yaml
installed scenario SHA-256:
  a0f9c7032be4e2540e3937cd741c9271c7358bba48dd5e6d41a23208a488f3ed
seed:
  19851
case:
  v8_10_secondary_probe_r1p5_a67p5_h25_19851
GUI:
  enabled
ROS_DOMAIN_ID:
  227
scenario run timeout:
  720.0 s
scenario wall timeout:
  900.0 s
outer process bound:
  960 s with bounded interrupt/kill escalation
run root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_secondary_probe
attempts:
  one
retry:
  prohibited
```

The fixed secondary layout is:

```text
start:
  (0.0, 0.0)
local:
  (0.5740251485476348, 1.38581929876693), input 400
global:
  (3.5, 3.5), input 1600
known topology:
  one local plus one global; maximum one active typed fill
```

Every controller override, schema-v13 direct-or-assisted ownership contract,
Stage A/Stage B budget, strict raw ranking rule, evaluator-only `0.50 m`
stop, forbidden state/event, final-zero rule, and cleanup rule is unchanged
from the passing primary population.

During the sealed run, observation is limited to OS process state and
retained files. No external ROS/DDS participant may join domain `227`.
After closure and cleanup, analysis must read the exact runner-emitted
summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_secondary_probe/
  phase08_v8_10_secondary_visible_probe_summary.yaml
```

Its sole `run_directory` must be validated below the declared root and used
verbatim for exactly one analyzer invocation. No run ID may be manually
reconstructed. The finalized recorder metadata must identify checkout
working directory/repository root `/home/mattb/dsim-lab`, the eventual clean
committed secondary-dispatch HEAD, and no untracked path.

A behavioral, formal, infrastructure, metadata, recording, fresh-validator,
plot, analysis-bundle, or cleanup failure closes this visible gate with no
retry. Only a formal pass and complete nine-plot analysis authorize the five
v8.10 secondary repeats `19861..19865`.

No secondary repeat, three-light, broader, physical, or Phase 09 execution
is authorized by this boundary.

## Current milestone

**PHASE 08.8 M4.11 — V8.10 PRIMARY REPEATS COMMITTED AT `512a898` /
SECONDARY VISIBLE SEED `19851` BOUNDARY WRITTEN / DISPATCH CHECKPOINT
PENDING / SECONDARY GAZEBO NOT YET AUTHORIZED.**

## Next criterion

Checkpoint and commit this exact secondary-visible boundary. Reverify a
clean worktree, unchanged installed scenario hash, absent run root, and
inactive runtime. Then execute seed `19851` exactly once with visible Gazebo
on domain `227`.

## Phase 08.8 M4.11 v8.10 secondary-visible dispatch checkpoint — 2026-07-31

The installed seed-`19851` one-time/no-retry visible secondary boundary
received the required Phase 08 checkpoint against primary-repeat result HEAD
`512a898`.

```text
base HEAD:
  512a8980efbb5c439a0e1b58c1eb95154ab5240d
status sha256 before this checkpoint note:
  ab3c43dde0386e761baa56631b29a647fdd62bb0b6ff1eea5dac77d428f6a2ea
active plan sha256:
  9d7a7ea410c43dfc1e404c6bba30453dfd4d2d593fe74eb72c2648913246dcbb
checkpoint sha256 before this checkpoint note:
  227f359e8f4db58f22cb89c360396abde02f5696441d11b5594d4397d92b53ee
installed scenario sha256:
  a0f9c7032be4e2540e3937cd741c9271c7358bba48dd5e6d41a23208a488f3ed
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active runtime:
  none
secondary-visible run root:
  absent
```

## Current milestone

**PHASE 08.8 M4.11 — V8.10 PRIMARY REPEATS COMMITTED / SECONDARY VISIBLE
SEED `19851` BOUNDARY CHECKPOINT PASS / DISPATCH COMMIT PENDING / SECONDARY
GAZEBO NOT YET AUTHORIZED.**

## Next criterion

Commit this exact secondary-visible boundary. Reverify a clean worktree,
unchanged installed scenario hash, absent run root, and inactive runtime.
Then execute seed `19851` exactly once with visible Gazebo on domain `227`.

## Phase 08.8 M4.11 v8.10 secondary-visible result — 2026-07-31

The one authorized installed seed `19851` execution is closed as a fixed
formal failure with no retry. The scientific local-recovery-to-global
behavior completed, but the declared-source Stage A geometry produced a
false negative.

```text
dispatch commit:
  f3bfb1fcdd42c58e00581644a36ebe3fbdd2f9f2
installed scenario sha256:
  a0f9c7032be4e2540e3937cd741c9271c7358bba48dd5e6d41a23208a488f3ed
started:
  2026-07-31T19:14:32.804136Z
completed:
  2026-07-31T19:21:45.435149Z
runner / recorder:
  1 / 0
recording / completeness / final zero / cleanup:
  PASS / PASS / PASS / PASS
formal predicates:
  10/14 PASS
```

The exact summary and run are:

```text
summary:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_secondary_probe/
  phase08_v8_10_secondary_visible_probe_summary.yaml
summary sha256:
  6857aaa727b63079aa3910ecbdd110f51ae9dc68f5a9b63295358d7976d1f4e1
run:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_10_secondary_probe/2026-07-31/
  20260731T191433826976Z_simulation_phase08_v8_10_secondary_visible_probe-
  v8_10_secondary_probe_r1p5_a67p5_h25_19851_5cffc8a7
```

Recorder metadata identifies checkout working directory/repository root
`/home/mattb/dsim-lab`, clean dispatch HEAD `f3bfb1f`, and no untracked
path. Bag SQLite integrity passed, and no runtime descendant remains.

The controller behavior was:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Schema v13 selected the direct branch and passed command ownership:

```text
branch / evidence:
  direct_repulse / bounded_direct_repulse_schema_v13
repulse state / control samples:
  438 / 2,833
mature radial-progress samples:
  378
maximum radial distance / exit radius:
  1.429333 / 1.366771 m
fill-to-exit distance:
  1.440018 m
selected/actual alignment:
  0.973428466
returned SEARCH samples:
  2,170
ordinary GESC restored / supervisor authority cleared:
  true / true
```

The four failed formal predicates share one evaluator root cause:

```text
local_recovery_stage:            false
fill_cardinality:                false
post_recovery_global_proximity:  false
ground_truth_goal:               false
```

The detector's first observed convergence was
`(1.1932522798, 1.8213642373)`. The one fill was
`(1.1854262109, 1.8223420991)`, only `0.0078869239 m` from that convergence.
The declared local lamp was `(0.5740251485, 1.3858192988)`, making the
convergence and fill respectively `0.7570611822 m` and `0.7512412491 m`
from the lamp. Both exceed the fixed declared-source association maximum
`0.60 m`.

The evaluator therefore left the one created/typed/active cluster
unassigned, never credited Stage A or fill cardinality, and never opened
Stage B. The controller nevertheless:

```text
completed direct local recovery:
  approximately 115.6 sim s
candidate-one raw lower:
  -0.2312067119
candidate-two interval:
  [-3.8372093023, -3.8372093023]
strict ranking margin:
  3.6060025904
GOAL_REACHED:
  233.2 sim s
final position:
  (3.5843550796, 3.5634411591) m
final global distance:
  0.1055488518 m
```

The live evaluator waited until its Stage A timeout at `360.154 s`, then
stopped the run. The shutdown `FAILSAFE` state occurred after readiness
became false and is not a forbidden accepted-motion state.

The one required analysis used the exact summary-owned run path:

```text
return code / status / failures:
  0 / complete / []
fresh Phase 05 validation:
  PASS
plots:
  9/9
analysis log:
  /tmp/phase08_8_m4_11_v8_10_secondary_visible_analysis.log
analysis log sha256:
  1e016f46d4515e229b19a492cf74a8d3b360e3ae458181cddeecf5bd189ffbc2
```

The trajectory plot was visually inspected and confirms the shifted first
basin, one fill, direct escape, ordinary transit, and global capture.

The complete fixed result is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_11_secondary_probe.md
```

This is an evaluator-geometry failure under the fixed contract, not a
controller escape/ranking/convergence failure. It remains a formal failure.
The v8.10 secondary repeats `19861..19865` and M6 broader matrix are not
authorized. The independently passing primary visible run and `10/10`
primary repeats remain valid.

No physical motion occurred. The evaluator coordinate and simulation stop
remain absent from the physical controller; physical stopping is manual
operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M4.11 / M5 — V8.10 SECONDARY VISIBLE SEED `19851` FIXED
FORMAL FAIL / SCIENTIFIC BEHAVIOR PASS / ONE-TIME ANALYSIS COMPLETE /
SECONDARY REPEATS AND M6 PROHIBITED / RESULT CHECKPOINT PENDING.**

## Next criterion

Checkpoint and commit this fixed secondary result. Do not dispatch seed
`19851` again, seeds `19861..19865`, or M6. Then perform no-Gazebo M7 bounded
closeout: final report, handoff, final static validation, status close, and
Phase 08 checkpoint.

## Phase 08.8 M4.11 secondary-visible result checkpoint — 2026-07-31

The fixed formal failure, successful scientific behavior, declared-source
geometry diagnosis, one-time complete analysis, nine plots, and inactive
runtime received the required Phase 08 checkpoint against committed
secondary-dispatch HEAD `f3bfb1f`.

```text
base HEAD:
  f3bfb1fcdd42c58e00581644a36ebe3fbdd2f9f2
status sha256 before this checkpoint note:
  17e21ee419f2ad6d3425030fe9387e0b916015c4bede0fae14542021cd379224
active plan sha256:
  9d7a7ea410c43dfc1e404c6bba30453dfd4d2d593fe74eb72c2648913246dcbb
secondary report sha256:
  329df4720ec8a7792238ae6b675cba3c7d6b370da0c0a82c3cb7d91bef71441f
checkpoint sha256 before this checkpoint note:
  4403cacf14c94ff52af38e310c96ae3c5c85ecc40c08b2bba6675d4a46c1135e
summary sha256:
  6857aaa727b63079aa3910ecbdd110f51ae9dc68f5a9b63295358d7976d1f4e1
installed scenario sha256:
  a0f9c7032be4e2540e3937cd741c9271c7358bba48dd5e6d41a23208a488f3ed
unstaged and staged diff checks:
  PASS
phase context:
  PASS
active runtime:
  none
```

## Current milestone

**PHASE 08.8 M4.11 / M5 — V8.10 SECONDARY VISIBLE SEED `19851` FIXED
FORMAL FAIL / SCIENTIFIC BEHAVIOR PASS / ONE-TIME ANALYSIS COMPLETE /
RESULT CHECKPOINT PASS / RESULT COMMIT PENDING / SECONDARY REPEATS AND M6
PROHIBITED.**

## Next criterion

Commit this exact fixed secondary result. Do not dispatch seed `19851`
again, seeds `19861..19865`, or M6. Then perform no-Gazebo M7 bounded
closeout: final report, handoff, final static validation, status close, and
Phase 08 checkpoint.

## Phase 08.8 M7 closeout drafting — 2026-07-31

The fixed secondary result was committed at:

```text
6f42040b2166a5f0784926cf70706dcb68e1edd3
phase 08.8: retain failed v8.10 secondary probe
```

The clean committed boundary preserves the independent primary visible and
`10/10` primary-repeat passes. The secondary repeat seeds `19861..19865` and
M6 remain prohibited and were not dispatched.

M7 adds the following no-Gazebo closeout documents:

```text
docs/codex/gesc_gaussian/validation/phase_08_8_final_report.md
docs/codex/gesc_gaussian/handoffs/phase_08_8_handoff.md
```

Navigation now points to this additive Phase 08.8 boundary while preserving
the earlier whole-Phase-08 report through Phase 08.7.

The report separates:

```text
primary fixed-layout formal result:       11/11 PASS
secondary scientific behavior:             1/1 COMPLETE
secondary formal result:                    0/1 FAIL
secondary repeatability:                    NOT RUN
v8.10 raw candidate ranking:              12/12 PASS
v8.10 recording/final-zero/cleanup:       12/12 PASS
v8.10 one-time analysis and plots:        12/12 and 108/108
M6 broader matrix:                         NOT RUN
three-light Gazebo:                        NOT RUN
wall/obstacle claim:                       NONE
physical automatic coordinate stop:       PROHIBITED
physical motion:                           NOT RUN
```

No source, launch, scenario, test, world, retained run, analysis, or plot was
changed while drafting M7. No Gazebo, ROS, analyzer, or physical process was
started.

## Current milestone

**PHASE 08.8 M7 — FINAL REPORT AND HANDOFF WRITTEN / NAVIGATION UPDATED /
FINAL STATIC VALIDATION AND MATERIAL CHECKPOINT PENDING / NO GAZEBO
AUTHORIZED.**

## Next criterion

Run the bounded final static consistency, link, syntax, YAML/XML, focused
regression, context, historical-preservation, artifact-presence, inactive
runtime, and complete-diff checks. Record exact outcomes, checkpoint Phase
08, inspect the complete closeout diff, and commit. Do not run Gazebo,
secondary repeats, M6, three-light simulation, Phase 09 implementation, or
physical hardware.

## Phase 08.8 M7 final static qualification — 2026-07-31

The no-Gazebo M7 closeout qualification passed against fixed empirical-result
HEAD `6f42040`.

Focused source-precedence regressions against the qualified v8.10 overlay:

```text
state machine + qualified dwell detector + all three recorder-CWD owners:
  108 passed in 0.87 s
  JUnit:
    /tmp/phase08_8_m7_closeout_focused.xml
  SHA-256:
    4991a132462ebc1bbfb38dda1f2876e40a3502a0367b6dd65976a1a330ca226c

schema-v1..v13 compatibility + all v8.10 scenarios + legacy behavior:
  218 passed in 52.93 s
  JUnit:
    /tmp/phase08_8_m7_closeout_schema_legacy.xml
  SHA-256:
    6f7a210c42293c3f21ae812d46904326dc1a00531806cda3e81cae4b1168aab5
```

Static source and installation checks:

```text
Phase 08 implement context:                  PASS
required Phase 00 documents:                PASS
new Markdown links:                         12 checked / 0 missing
changed Phase 08.8 Python source compile:   12/12
v8.10 scenario YAML parse:                   4/4
central launch XML parse:                    PASS
source/install byte parity:                 10/10
physical/shared launch coordinate-stop refs: 0
scenario schema mode boundary:              simulation only
known-count three-source state test:         present and passed
git diff --check:                            PASS
matching simulation/analysis/physical runtime: none
Phase 08 or simulation-ready Git tag:        none
```

Read-only summary-owned evidence audit:

```text
retained v8.10 run directories:              12/12 present
primary formal result:                       11/11
secondary formal result:                      0/1
controller ranked goal:                      12/12
exact one created/typed/active cluster:      12/12
schema-v13 branch selection:                 11 assisted + 1 direct
authoritative completeness:                  12/12
analysis failures:                            0
analysis status:                             11 complete + 1 partial
plots:                                      108/108
SQLite PRAGMA quick_check:                   12/12 ok
strict ranking margin range:                 0.094916 to 3.606003
```

The one partial analysis remains seed `19812`'s already documented optional
generic state-duration sampling gap. Its critical inputs, formal result,
scientific metrics, fresh validator, and nine plots remain complete.

Historical-preservation hashes still match the v8.10 qualification:

```text
gazebo_empty.world:
  3085542f9dc1d13fdf9368a24808a226908d1a2c5a7a4ffd07bc6f374ca14b43
gesc_gaussian_validation.world:
  8ecc1a231efec24401d74fef3cd5139d48c6029f88e71d044cefdf2fd14c5bef
gesc_gaussian_corner_origin_validation.world:
  88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf
phase_08_v6_selection.json:
  dcdbf937fe3de0cab9449c2b01af79fd938e1d3f9791b4897937875d0747590d
```

The four v8.10 scenario hashes also remain exactly:

```text
primary visible:
  c41eea1e6e10d8f736bb669fdf13db46eb8a6ed23b512a5827e8675d2d5c501b
primary repeats:
  cdb5e05339745d89afc632388af2e8bae45de75159c514f3d85832732361c796
secondary visible:
  a0f9c7032be4e2540e3937cd741c9271c7358bba48dd5e6d41a23208a488f3ed
secondary repeats:
  f7c54e8213f288b54051d69b06ae6ba1e75daf328763488ea970ebaffe550b3e
```

No source, launch, scenario, test, world, retained run, bag, analysis, or plot
changed during M7. No Gazebo, ROS graph, analyzer, three-light, M6, Phase 09,
or physical process ran.

## Current milestone

**PHASE 08.8 M7 — FINAL REPORT/HANDOFF COMPLETE / STATIC QUALIFICATION PASS /
PRIMARY `11/11` FORMAL PASS / SECONDARY FIXED FORMAL FAIL / MATERIAL
CHECKPOINT AND CLOSEOUT COMMIT PENDING.**

## Next criterion

Run `checkpoint_phase.sh 08`, inspect the generated checkpoint and complete
six-file closeout diff, rerun context and whitespace checks, and commit the
qualified Phase 08.8 closeout. Then write a post-commit receipt naming the
exact commit and clean worktree. Do not dispatch any simulation or physical
process.

## Phase 08.8 M7 material checkpoint — 2026-07-31

The qualified final report, handoff, navigation updates, static validation,
and inactive runtime received the required Phase 08 material checkpoint:

```text
base HEAD:
  6f42040b2166a5f0784926cf70706dcb68e1edd3
status sha256 before this checkpoint note:
  ea72e709a5ef2ff35617bded90d211bc8b8638d0e47059bdd87d70707c40696c
active plan sha256:
  9d7a7ea410c43dfc1e404c6bba30453dfd4d2d593fe74eb72c2648913246dcbb
final report sha256:
  1e2fba7fb8d7d0ed60b9975ff8f916178ea87593dc422ecd38c21dbc8fbe5c4d
handoff sha256 after final EOF-whitespace correction:
  55397d2e39aa322632b225b6936435e91586067e893027ccc64f6b07faee27cb
checkpoint sha256 before this checkpoint note:
  0d3a586a1d0e23299f8a63a582b50a462e04bc75b41d911fe64b3c070166f568
unstaged and staged diff checks:
  PASS
Phase 08 implement context:
  PASS
active simulation/analysis/physical runtime:
  none
```

## Current milestone

**PHASE 08.8 M7 — CLOSEOUT QUALIFIED / MATERIAL CHECKPOINT PASS /
PRIMARY `11/11` FORMAL PASS / SECONDARY FIXED FORMAL FAIL / BOUNDED
CLOSEOUT COMMIT PENDING.**

## Next criterion

Stage only the six reviewed M7 files, inspect the cached diff and whitespace,
and commit the qualified closeout. Then append a post-commit receipt and make
the final bounded receipt commit. Do not launch Gazebo, ROS, an analyzer,
Phase 09, or physical hardware.

## Phase 08.8 committed closeout boundary — 2026-07-31

The qualified final report, handoff, navigation updates, live-status
qualification, and material checkpoint were committed at:

```text
4def9905189e9d2ee189212cd2c1629417982ab6
phase 08.8: publish counted-source closeout
```

Immediately after that commit:

```text
worktree:                       clean
branch:                         feature/gesc-gaussian-robustness-v1
ahead of tracked remote:        160 commits
Phase 08 implement context:     PASS
git diff --check:               PASS
final report SHA-256:
  1e2fba7fb8d7d0ed60b9975ff8f916178ea87593dc422ecd38c21dbc8fbe5c4d
final handoff SHA-256:
  55397d2e39aa322632b225b6936435e91586067e893027ccc64f6b07faee27cb
material checkpoint SHA-256:
  0d3a586a1d0e23299f8a63a582b50a462e04bc75b41d911fe64b3c070166f568
active simulation/analysis/physical runtime:
  none
```

This commit closes the bounded Phase 08.8 iteration with:

```text
primary fixed layout:                  11/11 formal pass
secondary visible:                      0/1 formal pass
secondary scientific behavior:          1/1 complete
secondary repeats:                      NOT RUN
M6 broader matrix:                      NOT RUN
three-light Gazebo:                     NOT RUN
broad simulation readiness:            NOT ESTABLISHED
automatic physical coordinate stop:    PROHIBITED
physical motion:                        NOT RUN
```

No simulation-ready tag was created. No failed version was reopened or
reclassified. V6 and all historical scenarios, worlds, results, and plots
remain preserved.

## Current milestone

**PHASE 08.8 — CLOSED / FINAL REPORT AND HANDOFF COMMITTED AT `4DEF990` /
PRIMARY FIXED LAYOUT `11/11` FORMAL PASS / SECONDARY SCIENTIFIC PASS BUT
FORMAL EVALUATOR FAIL / BROAD CLAIM NOT ESTABLISHED / NO PHYSICAL MOTION.**

## Next criterion

Wait for a separate user request to plan Phase 09. Begin with a static
physical-interface and sensor-response calibration inventory around the
primary two-source `1:4` condition. Planning does not authorize hardware
motion. Preserve manual operator `Ctrl+C`, final-zero, recording
finalization, open-field assumptions, and scoped cleanup. Do not infer
secondary-layout, arbitrary-intensity, three-light, wall, obstacle, or broad
simulation readiness.

## Phase 08.8 active-goal continuation / v8.11 Plan — 2026-07-31

The automatic goal remains active because the bounded v8.10 closeout did not
complete the previously approved secondary repeat or varied-layout/intensity
work. Commit `5d76841` and every v8.10 result remain immutable; this is a
fresh versioned continuation, not a reclassification.

Repository reconstruction found one smallest coherent correction. Retained
secondary seed `19851` completed one fill, direct measured escape, strict raw
ranking of candidate two, `GOAL_HOLD`, and final global distance
`0.1055488518 m`. Its formal failure came solely from associating the
aggregate-field convergence to the individual local lamp with a `0.60 m`
gate. The convergence-to-fill distance was `0.0078869239 m`, while the
convergence-to-lamp distance was `0.7570611822 m`.

The fresh subplan is:

```text
docs/codex/gesc_gaussian/plans/phase_08_8_v8_11_plan.md
```

It freezes a schema-v14, evaluator-only, hashed two-source topology
qualification and reuses the existing counted-candidate `verified_trap`
association. No controller, detector, fill, affine term, modified cost, raw
ranking, source-count policy, motion parameter, wall behavior, launch graph,
recorder, or physical path changes. Source geometry and topology proof remain
outside the controller graph.

After complete no-Gazebo qualification and a committed implementation
boundary, v8.11 plans exactly:

```text
secondary visible:  seed 19901
secondary repeats:  seeds 19911..19915
sealed matrix:       seeds 19931..19934
matrix ratios:       1:3 and 1:5
matrix placements:   radii 1.25, 1.50, 1.75 m; angles 45 and 60 degrees
```

The retained v8.10 secondary bag will be replayed only as no-Gazebo evidence;
its historical formal result remains failed because its original live runner
did not perform a graceful global-proximity stop. Every fresh dispatched case
is one-time/no-retry and remains subject to recording, final-zero, cleanup,
strict ranking, exact one-fill, staged recovery, and post-recovery proximity
gates. All nine standard plots are required for every complete run.

No Gazebo, ROS graph, analyzer, or physical process was started while writing
this Plan. The worktree before the Plan edit was clean at `5d76841`.

## Current milestone

**PHASE 08.8 M8.1 — V8.11 TOPOLOGY-BOUND EVALUATOR CORRECTION PLANNED /
PLAN CHECKPOINT AND COMMIT PENDING / NO GAZEBO AUTHORIZED.**

## Next criterion

Run Plan-only static validation and Phase 08 context, inspect the three-file
Plan/status diff, checkpoint Phase 08, and commit the bounded amendment. Then
implement M8.1-M8.2 and complete the full no-Gazebo qualification before any
fresh simulation dispatch. Do not modify or relabel v8.10, run Gazebo, invoke
the analyzer, launch Phase 09, or move physical hardware.

## Phase 08.8 v8.11 Plan checkpoint — 2026-07-31

The fresh topology-bound continuation Plan received its required Plan-only
checkpoint against clean committed base `5d76841`.

```text
Phase 00 required documents:       PASS
Phase 08 implement context:        PASS
git diff --check:                  PASS
active simulation/analysis/physical runtime: none
v8.11 subplan sha256:
  6d5d8446cf3dc56de77a34a62eb7e28e30e9e6d9e422ef9556ff990acaebd644
parent Phase 08.8 Plan sha256:
  cae634bd2d19bac0de442635520790d916d816d4160cea226b8d22b82c891641
status sha256 before this checkpoint note:
  4bb0a4604920c68c87f0917c2b8da88b60e86639200e4813b24b15bf8dbe1c80
checkpoint sha256 before this checkpoint note:
  7928992369b1a069808c3009e3f2be6f8780ed35b54c5180af6c35dbf0ea1a50
```

No code, scenario, world, run, bag, report, plot, controller input, or
physical path changed in this Plan milestone. No Gazebo, ROS graph, analyzer,
or hardware process ran.

## Current milestone

**PHASE 08.8 M8.1 — V8.11 TOPOLOGY-BOUND EVALUATOR CORRECTION PLANNED /
PLAN CHECKPOINT PASS / PLAN COMMIT PENDING / NO GAZEBO AUTHORIZED.**

## Next criterion

Commit the reviewed four-file Plan/status/checkpoint boundary. Then implement
schema v14 and the evaluator-only topology record, add fresh v8.11 scenarios
and tests, and complete the full M8.2 no-Gazebo qualification, checkpoint,
and implementation commit before any Gazebo dispatch.

## Phase 08.8 M8.1-M8.2 v8.11 no-Gazebo qualification — 2026-07-31

The Plan boundary is committed at:

```text
e39ef24 phase 08.8: plan topology-bound v8.11 continuation
```

Schema v14 and its evaluator-only two-source topology record are implemented.
The canonical record binds the source list, evaluator source IDs, start,
bounds, disturbances, authoritative light model, sensor transform, sensor
geometry, local/global basin solutions, local ring depth, raw-cost ordering,
basin separation, route geometry, frozen thresholds, and final result hash.
Schema v1-v13 behavior remains covered and unchanged.

The existing `verified_trap` Stage A owner now has a schema-bound topology
precondition. It accepts the measured convergence/fill cluster without using
individual local-lamp distance as a gate, while retaining exact one-fill,
fill-to-convergence, distance-from-global, complete recovery path, strict
later ranking, and post-recovery proximity requirements. No topology record,
source geometry, intensity, role, or evaluator stop coordinate enters the
controller graph. No motion owner or controller behavior changed.

Fresh frozen inputs:

```text
ce6b80c83cd52b5e665d22bc2867b1a8046d6c6a817f8427dd94ea062a9b76c0
  phase08_v8_11_secondary_visible_probe.yaml
01466b3c350b4e37693eaffb0c40fe15591d28a8d09ee14f4b60aa00f200ce1d
  phase08_v8_11_secondary_repeats.yaml
b0ac9ff6582deecb56970d38f0a3f7d08f09aa8518343dd0477ae953d2a04b02
  phase08_v8_11_broad_matrix.yaml
```

All six embedded topology records pass the frozen preflight. The final
secondary topology hash is `eb749f0cb86f7b35231bdc308365f3008c6168df07b0188c03a97f339f364d71`;
the four matrix hashes are recorded in the qualification report.

Read-only retained replay:

```text
primary visible + repeats:             11/11 PASS
secondary seed 19851 under v8.11:      PASS
total:                                 12/12 PASS
historical seed-19851 formal result:   failed and unchanged
replay log:
  /tmp/phase08_8_v8_11_retained_replay.log
replay sha256:
  7a5c1b9ab3a3fe9e855b82ae625a7ee24e1f982754369b7e3152aa04b9f1a212
```

Final qualification:

```text
topology/schema/runner focus:
  387 passed, 1 skipped in 134.73 s
controller/supervisor/detector/legacy focus:
  310 passed in 8.42 s
evidence/recording/analysis focus:
  663 passed, 2 skipped in 165.64 s
sealed broad functional rerun:
  974 passed, 3 skipped in 185.74 s
fatal changed-file lint:
  PASS
Python/YAML/XML/diff/context:
  PASS
```

The first final broad invocation reported two late supervisor-integration
timing failures after `972` passes. Both exact tests then passed `2/2`, their
complete owner passed `60/60`, and the exact full suite passed on a sealed
localhost DDS domain without a source change. The failed invocation remains
retained and is classified as DDS/process-order test flakiness, not silently
discarded evidence.

Fresh installed qualification:

```text
root:
  /tmp/phase08_8_v8_11_release_qual.AdUc5v
build:
  3 packages finished in 11.5 s
source/install parity:
  10/10 PASS
installed schema:
  14, supported 1..14
installed launch construction:
  2/2 PASS
installed node construction:
  4/4 expected timeout 124, no startup error
installed dry-runs:
  visible / repeats / matrix = 1 / 5 / 4, zero unsupported
fresh roots after dry-run:
  absent 3/3
```

Historical preservation passes for `94/94` tracked scenario files, all three
world anchors, V6 selection, and the fixed v8.10 secondary summary/result.
V6, shifted worlds, all historical failures, runs, bags, reports, and plots
remain unchanged and selectable.

Durable qualification:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m8_2_v8_11_no_gazebo_qualification.md
```

No Gazebo, analyzer, scenario runner, recorder, controller, supervisor, or
physical process remains active. No fresh v8.11 run root exists. Physical
stopping remains manual operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M8.1-M8.2 — V8.11 TOPOLOGY-BOUND EVALUATOR IMPLEMENTED /
NO-GAZEBO QUALIFICATION PASS / IMPLEMENTATION CHECKPOINT PENDING / GAZEBO
PROHIBITED.**

## Next criterion

Run the Phase 08 material checkpoint, inspect the complete implementation,
scenario, test, report, and status diff, and commit this exact qualified
boundary. Then write, checkpoint, and commit a separate dispatch boundary
authorizing only the installed visible seed `19901`. Do not start Gazebo from
the uncommitted implementation.

## Phase 08.8 M8.1-M8.2 v8.11 implementation checkpoint — 2026-07-31

The schema-v14 evaluator correction, three fresh inputs, expanded tests,
retained read-only replay, isolated build, installed dry-runs, no-Gazebo
qualification, and live status received the required Phase 08 material
checkpoint against Plan HEAD `e39ef24`.

```text
base HEAD:
  e39ef2403baf6bcbd2a4f6322dec382be906b698
status sha256 before this checkpoint note:
  c17583f135e9cc7e8a5045b99539edd232dda7873061de35fd02d583e1f93008
active subphase plan sha256:
  6d5d8446cf3dc56de77a34a62eb7e28e30e9e6d9e422ef9556ff990acaebd644
no-Gazebo qualification sha256:
  567f7f7829f9b3ad26870e3ecba494d1610cb8f06505c79976897a20c2cc328a
checkpoint sha256 before this checkpoint note:
  0141acac197ef551e801085605c47846912f4c300361e3e95da2261db419d63b
unstaged and staged diff checks:
  PASS
Phase 08 implement context:
  PASS
active runtime:
  none
fresh v8.11 run roots:
  absent 3/3
```

## Current milestone

**PHASE 08.8 M8.1-M8.2 — V8.11 TOPOLOGY-BOUND EVALUATOR IMPLEMENTED /
NO-GAZEBO QUALIFICATION PASS / IMPLEMENTATION CHECKPOINT PASS /
IMPLEMENTATION COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact qualified implementation boundary. Then write, checkpoint,
and commit a separate visible-dispatch boundary naming only the installed
seed `19901`. Do not start Gazebo from an uncommitted or undispatched state.

## Phase 08.8 M8.3 v8.11 secondary-visible dispatch boundary — 2026-07-31

The complete no-Gazebo-qualified implementation is committed:

```text
d3e752d phase 08.8: qualify topology-bound v8.11 evaluator
```

The worktree was clean immediately after that commit. This boundary
authorizes exactly one installed visible dispatch:

```text
installed scenario:
  /tmp/phase08_8_v8_11_release_qual.AdUc5v/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_11_secondary_visible_probe.yaml
installed scenario sha256:
  ce6b80c83cd52b5e665d22bc2867b1a8046d6c6a817f8427dd94ea062a9b76c0
case:
  v8_11_secondary_probe_r1p5_a67p5_h25_19901
seed:
  19901
ROS_DOMAIN_ID:
  222
ROS_LOCALHOST_ONLY:
  1
presentation:
  visible Gazebo GUI
attempts / retries:
  1 / 0
run root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_11_secondary_probe
```

The run must use the isolated install qualified at `d3e752d`, be invoked from
`/tmp`, and remain bounded by the scenario's `720.0 s` simulation,
`900.0 s` wall, and `45.0 s` shutdown-grace limits plus an outer
`1020 s` timeout. No source-worktree `PYTHONPATH`, external DDS monitor, or
second invocation is permitted.

Acceptance remains all-or-nothing: recording and completeness, final zero,
scoped cleanup, expected state/event path, exact one-fill cardinality,
schema-v14 topology hash, direct or strictly owned assisted recovery, strict
second-candidate raw-cost ranking, graceful post-recovery `0.50 m` proximity
stop, SQLite integrity, and all nine plots. A formal failure is retained and
closes v8.11; it is not retried or tuned in place.

No Gazebo, scenario runner, recorder, analyzer, or physical process was
started while writing this boundary. The fresh run root is absent. Physical
stopping remains manual operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M8.3 — V8.11 SECONDARY VISIBLE SEED `19901` BOUNDARY WRITTEN /
DISPATCH CHECKPOINT AND COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Validate context and diff, prove installed scenario parity and inactive
runtime, run the Phase 08 dispatch checkpoint, and commit this exact boundary.
Only then execute seed `19901` once with visible Gazebo. Do not invoke the
analyzer until the runner emits a complete summary-owned run path.

## Phase 08.8 M8.3 v8.11 secondary-visible dispatch checkpoint — 2026-07-31

The installed seed-`19901` one-time/no-retry visible boundary received the
required Phase 08 checkpoint against implementation HEAD `d3e752d`.

```text
base HEAD:
  d3e752de3ae990bbdece5fd935714b3571b09fbb
status sha256 before this checkpoint note:
  d41c116d73cecb111efa02bde5bb2e33678f5f38a53021c6398b1e9c9fd8b479
active subphase plan sha256:
  6d5d8446cf3dc56de77a34a62eb7e28e30e9e6d9e422ef9556ff990acaebd644
checkpoint sha256 before this checkpoint note:
  11517d94bf61e2876cd85f759a005ae6c54bfa5569226f8f564fc89d4e91bf20
installed/source scenario parity:
  PASS
installed/source scenario sha256:
  ce6b80c83cd52b5e665d22bc2867b1a8046d6c6a817f8427dd94ea062a9b76c0
Phase 08 implement context:
  PASS
git diff --check:
  PASS
ROS_DOMAIN_ID 222 visible nodes:
  none
active simulation/analysis/physical runtime:
  none
fresh run root:
  absent
```

## Current milestone

**PHASE 08.8 M8.3 — V8.11 SECONDARY VISIBLE SEED `19901` BOUNDARY /
DISPATCH CHECKPOINT PASS / DISPATCH COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact two-file dispatch boundary. Then execute the installed
seed `19901` once on domain `222` with visible Gazebo and no retry. Preserve
the runner summary and all descendants whether the formal result passes or
fails.

## Phase 08.8 M8.3 v8.11 secondary-visible result — 2026-07-31

The one authorized installed seed `19901` executed once and passed every
formal gate.

```text
dispatch commit:
  66c7e8e462dafe33e2cf5c3b6df4a14c60758940
started / completed:
  2026-07-31T21:00:56.130307Z / 2026-07-31T21:05:41.464572Z
runner / recorder:
  0 / 0
attempts / retries:
  1 / 0
recording / completeness / final zero / cleanup:
  PASS / PASS / PASS / PASS
formal predicates:
  14/14 PASS
```

The exact summary and summary-owned run are:

```text
summary:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_11_secondary_probe/scenario_summaries/
  20260731T210056130307Z_phase08_v8_11_secondary_visible_probe.yaml
summary sha256:
  4f038f241e35d0e25de0a7e1f5b61b1fa01222f21f718b3c1e2cf7fccd13dd98
run:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_11_secondary_probe/2026-07-31/
  20260731T210056770365Z_simulation_phase08_v8_11_secondary_visible_probe-
  v8_11_secondary_probe_r1p5_a67p5_h25_19901_c0544b8e
```

Observed behavior:

```text
state path:
  SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE
  -> SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD
convergence / fill center:
  (1.1937773, 1.8373593) / (1.1844564, 1.8233879) m
fill-to-convergence:
  0.0167952 m
convergence-to-local diagnostic / lamp gate applied:
  0.7667992 m / false
created / typed / active fills:
  1 / 1 / 1
Stage A completion:
  116.032 sim s
escape branch / duration:
  direct_repulse / 21.709817 s
strict ranked-goal margin:
  3.6023806470 raw-cost units
Stage B sample time / distance:
  237.412 sim s / 0.1858370 m
final global distance:
  0.1858108 m
graceful proximity stop:
  true
```

The topology hash is
`eb749f0cb86f7b35231bdc308365f3008c6168df07b0188c03a97f339f364d71`.
The local-lamp distance remains diagnostic while the measured
convergence/fill association, topology qualification, exact cardinality,
recovery path, strict ranking, and Stage B proximity all gate.

The single analysis completed with fresh Phase 05 validation, no failures,
SQLite `quick_check=ok`, unchanged raw bag hash, and all nine plots:

```text
analysis:
  complete / failures []
plots:
  9/9
analysis log:
  /tmp/phase08_8_v8_11_secondary_visible_analysis.log
analysis log sha256:
  b69deff2b0b655a6149fa272716d0f176d083cb97c90bb872b19ed17a67bb74a
```

The trajectory, cost, and candidate-ranking plots were visually inspected
and show the intended shifted-basin recovery, ordinary transit, global
capture, and strict cost ordering.

Durable result:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m8_3_v8_11_secondary_visible_probe.md
```

No Gazebo, runner, recorder, analyzer, rosbag recorder, or physical process
remains active. No repeat or matrix case has been dispatched. Physical
stopping remains manual operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M8.3 — V8.11 SECONDARY VISIBLE SEED `19901` FORMAL PASS /
ONE-TIME ANALYSIS COMPLETE / 9/9 PLOTS / RESULT CHECKPOINT PENDING /
REPEATS AND MATRIX PROHIBITED.**

## Next criterion

Run the Phase 08 result checkpoint and commit this exact visible evidence.
Then write, checkpoint, and commit a separate one-time/no-retry dispatch
boundary for installed seeds `19911..19915`. Do not start the repeat
population before both commits exist.

## Phase 08.8 M8.3 v8.11 secondary-visible result checkpoint — 2026-07-31

The fixed seed-`19901` formal pass, one-time analysis, nine plots, durable
result, live status, and inactive runtime received the required Phase 08
result checkpoint against dispatch HEAD `66c7e8e`.

```text
base HEAD:
  66c7e8e462dafe33e2cf5c3b6df4a14c60758940
status sha256 before this checkpoint note:
  f22bc3e847cf73dc8493935b52b645d7beb61d0b8c355f03ae70c1cc442890fd
visible-result report sha256:
  758e87c0fa5d72ee145b77a6ba2932f2adf774cd87ba23f25396e271499f5aa7
checkpoint sha256 before this checkpoint note:
  a83472d3617de29f349a28340d94f266da173a0ebe1aaf9d8f0708d152cbc13d
Phase 08 implement context:
  PASS
git diff --check:
  PASS
active simulation/analysis/physical runtime:
  none
attempts / retries:
  1 / 0
formal predicates / plots:
  14/14 / 9/9
```

## Current milestone

**PHASE 08.8 M8.3 — V8.11 SECONDARY VISIBLE SEED `19901` FORMAL PASS /
ONE-TIME ANALYSIS COMPLETE / 9/9 PLOTS / RESULT CHECKPOINT PASS /
RESULT COMMIT PENDING / REPEATS AND MATRIX PROHIBITED.**

## Next criterion

Commit this exact visible-result boundary. Then write, checkpoint, and commit
the fixed `19911..19915` repeat dispatch boundary before starting any repeat.

## Phase 08.8 M8.3 v8.11 secondary-repeat dispatch boundary — 2026-07-31

The fixed visible result is committed:

```text
6bad670 phase 08.8: record v8.11 visible pass
```

The worktree was clean immediately afterward. This boundary authorizes one
installed serial invocation containing exactly five fixed headless cases:

```text
installed scenario:
  /tmp/phase08_8_v8_11_release_qual.AdUc5v/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_11_secondary_repeats.yaml
installed/source scenario sha256:
  01466b3c350b4e37693eaffb0c40fe15591d28a8d09ee14f4b60aa00f200ce1d
case:
  v8_11_secondary_repeats_r1p5_a67p5_h25
seeds:
  19911, 19912, 19913, 19914, 19915
ROS_DOMAIN_ID:
  221
ROS_LOCALHOST_ONLY:
  1
presentation:
  headless Gazebo, serial execution
attempts / retries per seed:
  1 / 0
run root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_11_secondary_repeats
```

The runner must stop at the first formal or cleanup failure. It may not skip,
retry, replace, or tune a seed. The population gate is `5/5` formal passes,
five complete recordings, final zeros and cleanups, five exact one-fill
recoveries, five strict rankings, five graceful proximity stops, and `45/45`
plots after one analysis per complete dispatched run.

The installed runner is invoked from `/tmp` with no source-worktree
`PYTHONPATH` and an explicit outer `5100 s` bound. No Gazebo, scenario runner,
recorder, analyzer, or physical process was started while writing this
boundary. The repeat root is absent.

## Current milestone

**PHASE 08.8 M8.3 — V8.11 SECONDARY REPEATS `19911..19915` BOUNDARY
WRITTEN / DISPATCH CHECKPOINT AND COMMIT PENDING / REPEATS AND MATRIX
PROHIBITED.**

## Next criterion

Validate source/install parity, root absence, inactive runtime, context, and
diff; checkpoint Phase 08; and commit this exact boundary. Only then invoke
the installed repeat suite once. Do not authorize the matrix unless all five
fixed repeats pass and are analyzed.

## Phase 08.8 M8.3 v8.11 secondary-repeat dispatch checkpoint — 2026-07-31

The exact installed `19911..19915` serial, headless, first-failure-stop,
one-time/no-retry boundary received the required Phase 08 checkpoint against
visible-result HEAD `6bad670`.

```text
base HEAD:
  6bad670
status sha256 before this checkpoint note:
  904b8d81601e47afe854ba1389a8a94f46e6cee74fec111bd08fc71452823caf
checkpoint sha256 before this checkpoint note:
  5630a659c828bc954f416682e756986ddd2bec29b9f3584dfaa948f49b489782
installed/source scenario parity:
  PASS
installed/source scenario sha256:
  01466b3c350b4e37693eaffb0c40fe15591d28a8d09ee14f4b60aa00f200ce1d
Phase 08 implement context / git diff check:
  PASS / PASS
active runtime:
  none
repeat root:
  absent
```

## Current milestone

**PHASE 08.8 M8.3 — V8.11 SECONDARY REPEATS `19911..19915` BOUNDARY /
DISPATCH CHECKPOINT PASS / DISPATCH COMMIT PENDING / REPEATS AND MATRIX
PROHIBITED.**

## Next criterion

Commit this exact two-file repeat boundary. Then invoke the installed suite
once on domain `221`, preserve every dispatched result, and stop without a
retry if any fixed case fails.

## Phase 08.8 M8.3 v8.11 secondary-repeat result — 2026-07-31

The fixed repeat dispatch boundary is committed:

```text
13ccb8b phase 08.8: authorize v8.11 secondary repeats
```

The one authorized installed suite ran all five fixed seeds serially on
`ROS_DOMAIN_ID=221` with `ROS_LOCALHOST_ONLY=1`, stopped at no intermediate
failure, and exited `0`. Each seed ran once; retries, replacements, tuning,
and outcome-based omissions were all zero.

```text
started / completed:
  2026-07-31T21:12:44.723799Z / 2026-07-31T21:37:40.960812Z
resolved / unsupported:
  5 / 0
attempts / retries per seed:
  1 / 0
runner return code:
  0
formal predicates:
  70/70 PASS
```

Exact summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_11_secondary_repeats/scenario_summaries/
  20260731T211244723799Z_phase08_v8_11_secondary_repeats.yaml
SHA-256:
  a05e6d4de1863324af1cd09178b7a0b7165e9f2776e76bb626481018b0b16f5c
```

Per-seed behavior:

```text
seed   Stage A s   branch           strict margin   Stage B s   final global m
19911  115.722     direct_repulse   3.607655        237.306     0.165580
19912  201.122     assisted         0.991836        327.534     0.128708
19913  116.035     direct_repulse   3.595674        235.613     0.130621
19914  115.834     direct_repulse   3.597580        236.704     0.124299
19915  115.718     direct_repulse   3.605789        232.610     0.135716
```

All five created, typed, and retained exactly one active fill. Four runs
confirmed the shifted aggregate-field basin about `0.76..0.77 m` from the
individual local lamp and completed direct repulse. Seed `19912` confirmed
near the local lamp, exercised the supervisor-owned assisted branch, restored
ordinary GESC, and still strictly ranked candidate two. All five topology
bindings used hash
`eb749f0cb86f7b35231bdc308365f3008c6168df07b0188c03a97f339f364d71`.

Population evidence:

```text
formal classifications:             5/5 PASS
recording / completeness:            5/5 / 5/5 PASS
fresh Phase 05 validation:           5/5 PASS
final zero / final readiness false:  5/5 / 5/5 PASS
cleanup:                             5/5 PASS
SQLite quick_check:                  5/5 ok
analysis status / failures:          5/5 complete / []
plots:                               45/45
```

The first analysis shell wrapper exited `1` before invoking any analyzer
because ROS setup referenced unset `AMENT_TRACE_SETUP_FILES` under shell
`nounset`. No analysis directory existed at that point. The corrected bounded
wrapper omitted `nounset` and analyzed each summary-owned run exactly once.
The five analyzer logs are retained under `/tmp` using each run ID followed by
`_analysis.log`. All trajectory plots and representative candidate-ranking
plots were visually inspected. They show exact one-fill recovery, outward
escape, ordinary transit, global capture, and strict candidate ordering; seed
`19912` visibly includes its longer local orbit and assisted exit.

Durable result and complete run/analysis/plot/hash manifest:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m8_3_v8_11_secondary_repeats.md
```

No Gazebo, scenario runner, recorder, analyzer, rosbag recorder, or physical
process remains active. Physical stopping remains manual operator `Ctrl+C`.
No matrix case has been dispatched.

## Current milestone

**PHASE 08.8 M8.3 — V8.11 SECONDARY REPEATS `19911..19915` 5/5 FORMAL
PASS / DIRECT AND ASSISTED RECOVERY QUALIFIED / ONE-TIME ANALYSES COMPLETE /
45/45 PLOTS / RESULT CHECKPOINT PENDING / MATRIX PROHIBITED.**

## Next criterion

Run the Phase 08 result checkpoint, inspect and commit the exact repeat report,
status, and checkpoint boundary. Only after that commit may a separately
checkpointed and committed dispatch boundary authorize the fixed matrix seeds
`19931..19934`.

## Phase 08.8 M8.3 v8.11 secondary-repeat result checkpoint — 2026-07-31

The fixed five-seed pass, one-time analyses, 45 plots, complete hash manifest,
live status, absent matrix root, and inactive runtime received the required
Phase 08 material checkpoint against dispatch HEAD `13ccb8b`.

```text
base HEAD:
  13ccb8b4c890c93d4363f1f2e7609a3b5f473168
status sha256 before this checkpoint note:
  c97e1c027f901dc71c75b64bf99ed962abd19d3453b9d59f6409a96d0de48471
repeat-result report sha256:
  50674a53ee864833b65a4f651ebf976d6ebac30eda54ee54790c6493b7ecbea1
checkpoint sha256 before this checkpoint note:
  142db403186d4e276a7a4e980a4f8156c51e53d86262948894705a48dedc1748
Phase 08 implement context / git diff check:
  PASS / PASS
installed/source repeat scenario parity:
  PASS
active simulation/analysis/physical runtime:
  none
matrix root:
  absent
formal population / plots:
  5/5 / 45/45
```

## Current milestone

**PHASE 08.8 M8.3 — V8.11 SECONDARY REPEATS `19911..19915` 5/5 FORMAL
PASS / DIRECT AND ASSISTED RECOVERY QUALIFIED / ONE-TIME ANALYSES COMPLETE /
45/45 PLOTS / RESULT CHECKPOINT PASS / RESULT COMMIT PENDING / MATRIX
PROHIBITED.**

## Next criterion

Commit this exact three-file repeat-result boundary. Then write, checkpoint,
and commit a separate one-time/no-retry dispatch boundary for installed matrix
seeds `19931..19934`. Do not start the matrix from this uncommitted result.

## Phase 08.8 M8.4 v8.11 broad-matrix dispatch boundary — 2026-07-31

The qualified repeat population is committed:

```text
4209c1a phase 08.8: qualify v8.11 secondary repeats
```

The worktree was clean immediately afterward. This boundary authorizes one
installed serial invocation containing exactly four fixed headless cases:

```text
installed scenario:
  /tmp/phase08_8_v8_11_release_qual.AdUc5v/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/phase08_v8_11_broad_matrix.yaml
installed/source scenario sha256:
  b0ac9ff6582deecb56970d38f0a3f7d08f09aa8518343dd0477ae953d2a04b02
seeds:
  19931, 19932, 19933, 19934
ROS_DOMAIN_ID / ROS_LOCALHOST_ONLY:
  220 / 1
presentation / execution:
  headless Gazebo / serial
attempts / retries per case:
  1 / 0
run root:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_11_broad_matrix
```

Frozen cases:

| Seed | Local position m | Local/global input | Topology hash |
|---:|---|---|---|
| `19931` | `(0.8838834765, 0.8838834765)` | `533.3333333333 / 1600` (`1:3`) | `da4e64008b2950c93ccbf08e31b6ead65c4fe6cc5791991965b9ceb156006bd6` |
| `19932` | `(1.0606601718, 1.0606601718)` | `320 / 1600` (`1:5`) | `14f52589f05b2dc62f8b12122f823fb97b8e897b304462e37087c1100944560c` |
| `19933` | `(0.7500000000, 1.2990381057)` | `533.3333333333 / 1600` (`1:3`) | `faafb05e4b004ef7d444c56badec3ea55f88107fcd052fef8c094782e7a82e26` |
| `19934` | `(0.8750000000, 1.5155444566)` | `320 / 1600` (`1:5`) | `47dd95926a4c9345770a0303ac83287c1f26a41afee108e6c6dc5d089e36837b` |

All cases use start `(0.0, 0.0)`, global `(3.5, 3.5)` at input `1600`,
schema v14, known source count two, evaluator-only topology qualification,
exact one-fill cardinality, accepted direct or strictly owned assisted
recovery, strict raw ranking, and a post-recovery evaluator radius of
`0.50 m`. The controller receives no source location, role, intensity,
topology record, or evaluator coordinate.

The installed dry-run was invoked from `/tmp` and resolved `4` runs with
`0` unsupported cases. It created no run root:

```text
/tmp/phase08_8_v8_11_matrix_boundary_dry_run.log
SHA-256:
  b4f9274d8b68d10dbcd1ab63681bc9a4060a92f2c8b4913427927c850ccaf2be
```

The runner must stop at the first formal or cleanup failure. It may not skip,
retry, replace, or tune a case. The population gate is `4/4` formal passes,
four complete recordings, final zeros and cleanups, four exact one-fill
recoveries, four strict rankings, four graceful proximity stops, SQLite
integrity, one analysis per complete dispatched run, and `36/36` plots.

The installed runner must be invoked from `/tmp` with no source-worktree
`PYTHONPATH`, under the scenario's finite `720.0 s` simulation, `900.0 s`
wall, and `45.0 s` shutdown-grace limits plus an explicit outer `4200 s`
timeout. No Gazebo, scenario runner, recorder, analyzer, rosbag recorder, or
physical process was started while writing this boundary. The matrix root is
absent. Physical stopping remains manual operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M8.4 — V8.11 FOUR-CASE MATRIX BOUNDARY WRITTEN / INSTALLED
DRY-RUN 4/4 / DISPATCH CHECKPOINT AND COMMIT PENDING / MATRIX PROHIBITED.**

## Next criterion

Validate source/install parity, root absence, inactive runtime, context, and
diff; checkpoint Phase 08; and commit this exact boundary. Only then invoke
the installed matrix once. Preserve every dispatched case and stop without a
retry if any fixed case fails.

## Phase 08.8 M8.4 v8.11 broad-matrix dispatch checkpoint — 2026-07-31

The exact installed four-case serial, headless, first-failure-stop,
one-time/no-retry boundary received the required Phase 08 checkpoint against
repeat-result HEAD `4209c1a`.

```text
base HEAD:
  4209c1a839100d41c5a813c8b88d78e9de38aebd
status sha256 before this checkpoint note:
  d68ec87acd55094257393f609f8c70debfcff72d433e9b069e87f2a4717bb122
checkpoint sha256 before this checkpoint note:
  0c4de520abb1cd9cf9dccc8bc963aee918ad8eee901d41d8d95c5f00df4e29c9
installed/source scenario parity:
  PASS
installed/source scenario sha256:
  b0ac9ff6582deecb56970d38f0a3f7d08f09aa8518343dd0477ae953d2a04b02
installed dry-run / unsupported:
  4 / 0
Phase 08 implement context / git diff check:
  PASS / PASS
active simulation/analysis/physical runtime:
  none
matrix root:
  absent
```

## Current milestone

**PHASE 08.8 M8.4 — V8.11 FOUR-CASE MATRIX BOUNDARY / INSTALLED DRY-RUN
4/4 / DISPATCH CHECKPOINT PASS / DISPATCH COMMIT PENDING / MATRIX
PROHIBITED.**

## Next criterion

Commit this exact two-file dispatch boundary. Then invoke the installed matrix
once on domain `220`, preserve every dispatched result, and stop without a
retry if any fixed case fails.

## Phase 08.8 M8.4 v8.11 broad-matrix result — 2026-07-31

The fixed matrix dispatch boundary is committed:

```text
39b73f9 phase 08.8: authorize v8.11 broad matrix
```

The one authorized installed suite dispatched seed `19931` once. It failed
the formal Stage A gate, so the runner stopped exactly as declared. Seed
`19931` was not retried, tuned, or reclassified; seeds `19932..19934` were not
dispatched.

```text
started / completed:
  2026-07-31T21:55:07.749994Z / 2026-07-31T22:02:16.204028Z
runner / recorder return code:
  1 / 0
stopped reason:
  run_failure
resolved definitions / dispatched:
  4 / 1
attempts / retries:
  1 / 0
```

Exact summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_11_broad_matrix/scenario_summaries/
  20260731T215507749994Z_phase08_v8_11_broad_matrix.yaml
SHA-256:
  6504450fbd404bb4adea04a7d29ad92605ddd11a05201ce5d39f1d75335d235d
```

Seed `19931` correctly confirmed candidate one and created exactly one valid
typed fill. The controller emitted a transition to `ESCAPE_REPULSE` and then
immediately forced `FAILSAFE` before a publishable escape interval:

```text
convergence confirmed:             77.4 sim s
fill created / escape transition:  86.7 / 86.7 sim s
failsafe reason:
  open-field escape approach continuity has no pose outside the frozen exit radius
collapsed state path:
  SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> FAILSAFE
Stage A timeout sample:            360.638 sim s
formal predicates:                 3/14 PASS
```

The fill center was `(1.069961, 0.760591) m`, the fill-to-convergence distance
was `0.185510 m`, and created/typed/active cardinality was `1/1/1`. The frozen
exit radius was `1.366770829 m`. Across `2,536` pre-escape odometry samples,
the maximum distance from the fill center was only `1.315565112 m`; zero
samples were outside and the shortfall was `0.051205717 m`.

The schema-v14 topology preflight admitted `start_to_local_m=1.25` but did not
bind the runtime supervisor's requirement for one pose outside the
data-derived fill radius. This is a fill/topology/supervisor integration gap.
It is not a wall, collision, source-count, cardinality, fill-validity, affine-
disablement, recording, or cleanup failure.

Evidence boundary:

```text
classification / matrix population:  FAIL / NOT ESTABLISHED
recording / completeness:             PASS / PASS
final zero / readiness false:         PASS / PASS
cleanup / SQLite quick_check:         PASS / ok
analysis status / failures:           partial / []
plots:                                9/9
raw bag SHA-256:
  15a91e7edc924d5bb98c974261e6f31aa67a5c41a1d276a3153f056e415bc901
```

The analyzer's `partial` status is expected because no valid escape or goal
interval exists; recording and analysis failure lists are empty. The
trajectory, state/event, and radial-escape plots were visually inspected and
show the approach/orbit, one fill, immediate persistent failsafe, and absence
of escape evidence.

Durable failure, exact run, diagnosis, artifact hashes, plot hashes, and
fresh-version correction boundary:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m8_4_v8_11_broad_matrix.md
```

V8.11 is closed for the broad matrix. Its fixed secondary `1/1 + 5/5` result
remains passed only for that exact layout. No broad varied-layout/intensity
claim is established. No Gazebo, runner, recorder, analyzer, rosbag recorder,
or physical process remains active. Physical stopping remains manual operator
`Ctrl+C`.

## Current milestone

**PHASE 08.8 M8.4 — V8.11 MATRIX FORMAL FAIL ON FIRST FIXED CASE / 19931
RETAINED WITHOUT RETRY / 19932..19934 NOT DISPATCHED / ROOT CAUSE IS
INSIDE-EXIT-RADIUS APPROACH-CONTINUITY CONTRACT GAP / RESULT CHECKPOINT
PENDING / V8.11 BROAD CLAIM CLOSED.**

## Next criterion

Run the Phase 08 failure-result checkpoint and commit the exact retained
report/status/checkpoint boundary. Then, under the user's existing bounded-
correction authority, write and checkpoint a fresh versioned Plan for a
legacy-default-off, odometry-only interior approach-anchor fallback. Do not
rerun seed `19931`, dispatch `19932..19934`, or change v8.11 in place.

## Phase 08.8 M8.4 v8.11 broad-matrix failure checkpoint — 2026-07-31

The retained first-case formal failure, stopped population, one-time partial
analysis, nine plots, exact root-cause diagnosis, live status, and inactive
runtime received the required Phase 08 material checkpoint against dispatch
HEAD `39b73f9`.

```text
base HEAD:
  39b73f947e490febe8b496a37dee767193d64835
status sha256 before this checkpoint note:
  e28f86cb7e5e755808b8c393ef7402fbb081de9f1b0f61f2b298009127e78195
matrix-failure report sha256:
  a21f831d6c0aad602d47818f3fa0ffd1d7d20d802bcfb9f9c0e42cbf0db82fd5
checkpoint sha256 before this checkpoint note:
  9d2697f6f54660d0d9310657d4ffa65bc573a0b26468c4b0195d588a32833610
Phase 08 implement context / git diff check:
  PASS / PASS
active simulation/analysis/physical runtime:
  none
dispatched / retries / plots:
  1 / 0 / 9
matrix disposition:
  FAIL / v8.11 broad claim closed
```

## Current milestone

**PHASE 08.8 M8.4 — V8.11 MATRIX FORMAL FAIL ON FIRST FIXED CASE / 19931
RETAINED WITHOUT RETRY / 19932..19934 NOT DISPATCHED / ROOT CAUSE IS
INSIDE-EXIT-RADIUS APPROACH-CONTINUITY CONTRACT GAP / RESULT CHECKPOINT PASS /
FAILURE COMMIT PENDING / V8.11 BROAD CLAIM CLOSED.**

## Next criterion

Commit this exact three-file failure boundary. Then write, validate,
checkpoint, and commit a fresh v8.12 Plan before changing code or dispatching
any fresh simulation.

## Phase 08.8 active-goal continuation / v8.12 Plan — 2026-07-31

The complete v8.11 matrix failure boundary is committed:

```text
cff0178 phase 08.8: retain failed v8.11 broad matrix
```

The worktree was clean immediately afterward. The fresh authoritative subplan
is:

```text
docs/codex/gesc_gaussian/plans/phase_08_8_v8_12_plan.md
```

It freezes one legacy-default-off, odometry-only correction:

```text
open_field_escape_interior_anchor_fallback_enabled:    false
open_field_escape_interior_anchor_min_displacement_m:  0.50
```

The original newest-outside-radius approach anchor retains priority and exact
default behavior. Only when enabled and no outside pose exists may the helper
select the farthest historical pose, require at least `0.50 m` displacement,
and label it `interior_farthest`. Empty, tiny, unordered, nonfinite, and
degenerate history remain failsafe. No source, global, map, room, Vicon, or
evaluator coordinate enters the controller.

The existing schema-v14 topology record remains unchanged. New optional
scenario validation cross-checks the enabled minimum against the recorded
`start_to_local_m`; the runtime history/fill-radius test remains
authoritative. Historical scenarios omit the option and retain their case
keys, launch commands, and behavior.

After full no-Gazebo qualification and a committed implementation boundary,
v8.12 plans exactly:

```text
visible corrective probe:
  seed 20001, GUI, failed-v8.11 geometry with fresh version/seed
fresh matrix:
  seeds 20031..20034, headless serial, ratios 1:3 and 1:5
```

No code, scenario, launch graph, run, bag, or historical result changed while
writing this Plan. No Gazebo, ROS graph, analyzer, or physical process was
started. Physical stopping remains manual operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M8.6 — V8.12 INTERIOR APPROACH-ANCHOR CORRECTION PLANNED /
PLAN CHECKPOINT AND COMMIT PENDING / CODE AND GAZEBO PROHIBITED.**

## Next criterion

Run Plan-only context and diff validation, inspect the Plan/status boundary,
checkpoint Phase 08, and commit. Only then implement M8.6-M8.7. No v8.12
Gazebo process is authorized before the complete no-Gazebo implementation
qualification is checkpointed and committed.

## Phase 08.8 v8.12 Plan validation — 2026-07-31

The fresh subplan, parent amendment, live-status record, and corrected durable
navigation were inspected against clean base HEAD
`cff0178ffe94ec6e9d8ac128482b436aaf9fa463`.

```text
Phase 08 Plan context:                PASS
unstaged/staged git diff check:       PASS / PASS
active simulation/analysis/physical: none
code/scenario/launch/runtime changes: none
v8.12 Plan sha256:
  95fa59b4c9d098b1ecfb41dd3dfe619c6a3030c615a502f28095ac6eae7c89d8
parent Phase 08.8 Plan sha256:
  1f7b93e86a5280423e175faa0fbbf82a8063c75f7a5e1b0c3db5687849570827
implementation navigation sha256:
  8ff06e375c73f2d0dcf0f269e5f869a4c79084a7fb62252ec98f982d2d2d5c9f
status sha256 before this validation note:
  b9f0aeef2f07d770b67702e648fc51421be709ff8ce0d11a4af1e06296c61684
```

The navigation correction distinguishes the historical Phase 08.8 closeout
from the subsequently approved additive continuation and points fresh context
recovery to v8.12. It changes no earlier result or readiness claim.

## Current milestone

**PHASE 08.8 M8.6 — V8.12 PLAN VALIDATED / PLAN CHECKPOINT AND COMMIT
PENDING / CODE AND GAZEBO PROHIBITED.**

## Next criterion

Checkpoint Phase 08 and commit the exact Plan-only boundary. Only that commit
authorizes M8.6-M8.7 implementation; v8.12 Gazebo remains prohibited until the
separate complete no-Gazebo implementation boundary passes and is committed.

## Phase 08.8 v8.12 Plan checkpoint — 2026-07-31

The Plan-only continuation received the required Phase 08 material-boundary
checkpoint against base HEAD `cff0178ffe94ec6e9d8ac128482b436aaf9fa463`.

```text
status sha256 before this checkpoint note:
  33eab2ec724f658f5ed307357cf608082809c5078a46e3f12e8ed0fe755de507
v8.12 Plan sha256:
  95fa59b4c9d098b1ecfb41dd3dfe619c6a3030c615a502f28095ac6eae7c89d8
parent Phase 08.8 Plan sha256:
  1f7b93e86a5280423e175faa0fbbf82a8063c75f7a5e1b0c3db5687849570827
implementation navigation sha256:
  8ff06e375c73f2d0dcf0f269e5f869a4c79084a7fb62252ec98f982d2d2d5c9f
checkpoint sha256 before this checkpoint note:
  213c347bd5ff858c78b30a8e82ce2087626614edbdff9c7815796005b35304ae
Phase 08 Plan context / git diff check: PASS / PASS
active simulation/analysis/physical runtime: none
```

## Current milestone

**PHASE 08.8 M8.6 — V8.12 PLAN CHECKPOINT PASS / PLAN COMMIT PENDING /
CODE AND GAZEBO PROHIBITED.**

## Next criterion

Commit this exact five-file Plan boundary. Then implement and completely
qualify M8.6-M8.7 without Gazebo. Do not create a dispatch boundary or start
v8.12 simulation before that implementation is checkpointed and committed.

## Phase 08.8 M8.6-M8.7 v8.12 no-Gazebo qualification — 2026-07-31

The Plan boundary is committed at:

```text
7c9d5e9 phase 08.8: plan v8.12 interior anchor fallback
```

The legacy-default-off odometry-only interior approach-anchor fallback is
implemented in the existing supervisor owner. The newest pose strictly
outside the frozen fill exit radius retains priority and mode `0`. Only when
no outside pose exists and the fresh option is enabled may the helper select
the earliest farthest finite history pose, require at least `0.50 m`, and
emit mode `1`. Empty, nonfinite, unordered, degenerate, and below-minimum
history remains failsafe.

Schema v14 binds the option to counted-candidate recovery, approach
continuity, active-fill transit, supervisor-owned assist, affine assistance,
and a valid topology record whose start-to-local route meets the minimum. The
optional expected mode is evaluator-only and is absent from controller launch
arguments. No source, role, intensity, declared global, map, Vicon/GPS, wall
sensor, or evaluator stop coordinate entered the controller.

The exact seed-`19931` replay fixture proves:

```text
default-off evidence:          none
enabled anchor mode:           interior_farthest
displacement:                  1.3155651121858971 m
direction:                     (0.8147816323190298,
                                0.5797679636160810)
outside-radius branch priority: retained
```

Fresh inputs and resolved case keys:

```text
phase08_v8_12_interior_anchor_visible_probe.yaml
  sha256 d4607649546f8301112a0cbbb5ded10a2a167146efed143dbfff64e4d5810c65
  seed 20001
  key 5d8ed8295d910a52c28561e7d9f8172cb63d7158debef9eb7597b8befe285dbb

phase08_v8_12_broad_matrix.yaml
  sha256 311667e8c8d330732ea32c894bb78fed43b63cd23ef86f486ca25c86fe727bdc
  seeds 20031..20034
  keys 331c7bd7aca41ef2373d6c58300d8073b5185a4c9195254754709c6dfe86c868
       941720dabb4f49053e87ec64b2ba597003aee436bda1855e70032448da25db40
       14dde5e389e4e6b767d93a34210633bbf76744c6d8b9fb49d3046a94b2160573
       4e8006c1d102711de1cc31839cf0280ab3927a61f4a19bb75f9fd38e4e63ac64
```

Final source qualification:

```text
helper/state/supervisor/observability:
  240 passed in 6.55 s
schema:
  198 passed in 74.83 s
schema + runner after fresh inputs:
  396 passed, 1 skipped in 115.78 s
sealed broad functional on valid localhost domain 218:
  1012 passed, 3 skipped in 221.91 s
fatal changed-file lint:
  PASS
Python/YAML/XML/diff/context:
  PASS
```

The unfiltered broad collector reported only the repository-wide flake8 and
pep257 wrappers. Two later functional attempts stopped after exactly `48`
pure tests because invalid DDS domains `233` and `234` were assigned; the
first ROS-node construction made the middleware exit without a pytest
traceback. A valid-domain boundary passed `14/14`, followed by the complete
sealed pass above. These command failures changed no source and are retained
in the durable report.

Read-only historical qualification:

```text
tracked scenarios at Plan HEAD:      97/97 byte-identical
retained v8.11 artifact files:       248 hashed read-only
v8.11 passing secondary bags:        6/6 outcomes unchanged
v8.11 failed seed 19931 bag:         historical failure unchanged
total retained replay:               7/7
V6/world anchors:                    unchanged
```

Fresh installed qualification:

```text
root:
  /tmp/phase08_8_v8_12_release_qual.HnEptF
build:
  3 packages finished in 11.9 s
source/install parity:
  8/8 PASS
installed schema:
  14, supported 1..14
installed launch construction:
  2/2 PASS
installed node construction:
  4/4 expected bounded timeout 124, no startup error
installed dry-runs:
  visible / matrix = 1 / 4, zero unsupported
fresh roots after dry-run:
  absent 2/2
```

Durable qualification:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m8_7_v8_12_no_gazebo_qualification.md
```

No Gazebo, scenario runner, recorder, analyzer, controller, supervisor, or
physical process is active. No v8.12 run root exists and no analyzer or plot
was produced. Physical stopping remains manual operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M8.6-M8.7 — V8.12 INTERIOR APPROACH-ANCHOR FALLBACK
IMPLEMENTED / NO-GAZEBO QUALIFICATION PASS / IMPLEMENTATION CHECKPOINT
PENDING / GAZEBO PROHIBITED.**

## Next criterion

Run the Phase 08 material checkpoint, inspect the complete implementation,
scenario, test, report, and status diff, and commit this exact qualified
boundary. Then write, checkpoint, and commit a separate boundary authorizing
only the installed visible seed `20001`. Do not start Gazebo from the
uncommitted implementation.

## Phase 08.8 M8.6-M8.7 v8.12 implementation checkpoint — 2026-07-31

The default-off supervisor correction, two fresh inputs, expanded tests,
retained read-only replay, isolated build, installed dry-runs, durable
no-Gazebo qualification, and live status received the required Phase 08
material checkpoint against Plan HEAD
`7c9d5e9ebc24aaf2595597bc4a85a7b179cfa860`.

```text
status sha256 before this checkpoint note:
  ef22273b621556d517fcbd8c14729cf8530f093b05d1185be9e26308ced05218
active subphase plan sha256:
  1f028088939e0a71eceb755329e8e5238bcb6fdb3c4f0eda4901571c872c9cbb
no-Gazebo qualification sha256:
  742b91a5d652117fda0aa3c7acf5a707408c20320428e231ef27ebb4e71304e5
checkpoint sha256 before this checkpoint note:
  dc56fe6f114310365b7327f6672ec8201ea04e8293c325e835e5251c7ec024ab
unstaged and staged diff checks:
  PASS
Phase 08 implement context:
  PASS
active runtime:
  none
fresh v8.12 run roots:
  absent 2/2
```

## Current milestone

**PHASE 08.8 M8.6-M8.7 — V8.12 INTERIOR APPROACH-ANCHOR FALLBACK
IMPLEMENTED / NO-GAZEBO QUALIFICATION PASS / IMPLEMENTATION CHECKPOINT PASS /
IMPLEMENTATION COMMIT PENDING / GAZEBO PROHIBITED.**

## Next criterion

Commit this exact qualified implementation boundary. Then write, validate,
checkpoint, and commit a separate visible-dispatch boundary naming only the
installed seed `20001`. Do not start Gazebo from an uncommitted or
undispatched state.

## Phase 08.8 M8.8 v8.12 visible-probe dispatch boundary — 2026-07-31

The completely no-Gazebo-qualified implementation is committed:

```text
0263f1c phase 08.8: qualify v8.12 interior anchor fallback
```

The worktree was clean immediately after that commit. This boundary
authorizes exactly one installed visible dispatch:

```text
installed scenario:
  /tmp/phase08_8_v8_12_release_qual.HnEptF/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_12_interior_anchor_visible_probe.yaml
installed/source scenario sha256:
  d4607649546f8301112a0cbbb5ded10a2a167146efed143dbfff64e4d5810c65
case:
  v8_12_interior_anchor_r1p25_a45_ratio1to3_20001
case key:
  5d8ed8295d910a52c28561e7d9f8172cb63d7158debef9eb7597b8befe285dbb
seed:
  20001
ROS_DOMAIN_ID:
  219
ROS_LOCALHOST_ONLY:
  1
presentation:
  visible Gazebo GUI
attempts / retries:
  1 / 0
run root:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_12_interior_anchor_probe
```

The installed runner must be invoked from `/tmp` with the isolated v8.12
install first in the overlay, no source-worktree `PYTHONPATH`, and an explicit
outer `1020 s` bound. The scenario retains its `720.0 s` simulation,
`900.0 s` wall, and `45.0 s` shutdown-grace bounds.

The run is one-time/no-retry. It must produce exactly one complete local
recovery and one valid fill, an `ESCAPE_STARTED` event with
`interior_farthest` mode `1` and displacement at least `0.50 m`, strict
candidate-two raw-cost ranking, a graceful first post-recovery `0.50 m`
global-proximity stop, complete recording, final zero, SQLite integrity, and
clean scoped shutdown. Every formal predicate must pass. Any formal,
recording, final-zero, integrity, or cleanup failure closes v8.12 without a
retry or in-place tuning.

Only after a complete formal pass may the summary-owned run be analyzed
exactly once for all nine standard plots. The four-case matrix remains
prohibited until the visible result and plots are retained, checkpointed, and
committed.

No Gazebo, scenario runner, recorder, analyzer, or physical process was
started while writing this boundary. Both v8.12 run roots remain absent.

## Current milestone

**PHASE 08.8 M8.8 — V8.12 VISIBLE SEED `20001` BOUNDARY WRITTEN /
DISPATCH CHECKPOINT AND COMMIT PENDING / GAZEBO AND MATRIX PROHIBITED.**

## Next criterion

Validate installed/source parity, root absence, inactive runtime, context,
and diff; checkpoint Phase 08; and commit this exact one-run boundary. Only
then invoke the installed visible suite once. Do not authorize or dispatch
the matrix unless seed `20001` formally passes and is analyzed.

## Phase 08.8 M8.8 v8.12 visible dispatch checkpoint — 2026-07-31

The exact installed seed-`20001` visible, one-time/no-retry boundary received
the required Phase 08 checkpoint against qualified implementation HEAD
`0263f1c8ca32777a6ae42812c33660d2d52ea8d0`.

```text
status sha256 before this checkpoint note:
  928bd90ca8f3661cdfcb060132a19c29088d2ddf986b5f50b38fa51a943b81e6
checkpoint sha256 before this checkpoint note:
  045e0e482c94f6dc9f1c49a2793d425e8f96bf1658a00675b2c1fc24ade05884
installed/source scenario parity:
  PASS
installed/source scenario sha256:
  d4607649546f8301112a0cbbb5ded10a2a167146efed143dbfff64e4d5810c65
Phase 08 implement context / git diff check:
  PASS / PASS
active runtime:
  none
visible root / matrix root:
  absent / absent
```

## Current milestone

**PHASE 08.8 M8.8 — V8.12 VISIBLE SEED `20001` BOUNDARY /
DISPATCH CHECKPOINT PASS / DISPATCH COMMIT PENDING / GAZEBO AND MATRIX
PROHIBITED.**

## Next criterion

Commit this exact two-file dispatch boundary. Then invoke the installed
visible suite once on domain `219`, preserve the result, and stop without a
retry if any fixed gate fails.

## Phase 08.8 M8.8 v8.12 visible corrective result — 2026-07-31

The committed installed seed-`20001` visible boundary executed exactly once
without a retry:

```text
dispatch HEAD:
  40940877a67920653cca2378c91336803cfd5761
scenario summary:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_12_interior_anchor_probe/scenario_summaries/
  20260731T231350696332Z_phase08_v8_12_interior_anchor_visible_probe.yaml
scenario summary sha256:
  b9e3f9711600dd36a9d897bf550cf432ce8dcdb9f34ba444921ad030c1322cde
attempts / retries:
  1 / 0
formal predicates:
  14/14 PASS
recording / final zero / readiness false / SQLite / cleanup:
  PASS / PASS / PASS / ok / PASS
```

The behavior exercised the intended v8.12 correction and complete two-source
contract:

```text
Stage A completion:                 106.609 sim s
created / active fills:             1 / 1
fill-to-convergence:                0.099527192962 m
approach anchor mode / value:       interior_farthest / 1
anchor displacement / minimum:      1.330954903938 / 0.50 m
escape branch / duration:           assisted / 17.55953105 s
escape-stalled event:               observed
escape succeeds / fails:            1 / 0
ordinary GESC ownership restored:   true
candidate one raw lower:            -3.188705462004
candidate two raw upper:            -3.837209302326
strict separation margin:            0.648503840321
Stage B proximity:                  222.719 sim s
post-Stage-A elapsed:               116.110 s
first live proximity distance:      0.116717368350 m
final global distance:              0.116706544674 m
graceful proximity stop:            true
```

The exact summary-owned run was analyzed once. Analysis completed with zero
failures, both fresh and stored Phase 05 validation passed, all nine standard
plots exist, and visual inspection of trajectory, candidate ranking, and cost
confirmed the local basin/fill, recovery/transit, final global approach, and
strict raw-cost ordering. The follow-up plot check first named the wrong
`analysis/plots` directory; it then inspected the already-complete standard
`analysis/phase07/plots` output without rerunning the analyzer.

Durable report:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m8_8_v8_12_visible_probe.md
```

No Gazebo, runner, recorder, analyzer, rosbag recorder, or physical process
remains active. The four-case matrix has not been dispatched. The simulation
coordinate stop remains evaluator-only; physical arrival remains manual
operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M8.8 — V8.12 VISIBLE SEED `20001` FORMAL PASS / EXPECTED
INTERIOR ANCHOR AND ASSISTED RECOVERY PASS / ONE-TIME ANALYSIS COMPLETE /
9/9 PLOTS / RESULT CHECKPOINT PENDING / MATRIX PROHIBITED.**

## Next criterion

Run the Phase 08 result checkpoint and commit this exact visible evidence.
Then write, checkpoint, and commit a separate one-time/no-retry boundary for
the installed headless seeds `20031..20034`. Do not start the matrix before
both commits exist.

## Phase 08.8 M8.8 v8.12 visible-result checkpoint — 2026-07-31

The fixed seed-`20001` formal pass, expected interior anchor, assisted local
recovery, strict ranking, one-time analysis, nine plots, durable result, and
inactive runtime received the required Phase 08 result checkpoint against
dispatch HEAD `4094087`.

```text
base HEAD:
  40940877a67920653cca2378c91336803cfd5761
status sha256 before this checkpoint note:
  9c6fee1d703ddd0d88e501925eb485bd57a59d3d7046d71190d826b37802f154
visible-result report sha256:
  a915a9086302c77ca1dea48123bb61026e3395dfa91ae18096b06411b315f150
checkpoint sha256 before this checkpoint note:
  6dd9ecaf88f448c66c03f54b607638d9345b60b7adb9868d2b729f3c1eea623a
Phase 08 implement context:
  PASS
git diff --check:
  PASS
bag SQLite quick_check using read-only Python sqlite3 fallback:
  ok
active simulation/analysis/physical runtime:
  none
attempts / retries:
  1 / 0
formal predicates / plots:
  14/14 / 9/9
```

The `sqlite3` command-line program is unavailable on this host, so the
read-only `file:...?mode=ro` Python sqlite3 fallback performed the same
`PRAGMA quick_check` without mutating the retained bag.

## Current milestone

**PHASE 08.8 M8.8 — V8.12 VISIBLE SEED `20001` FORMAL PASS / EXPECTED
INTERIOR ANCHOR AND ASSISTED RECOVERY PASS / ONE-TIME ANALYSIS COMPLETE /
9/9 PLOTS / RESULT CHECKPOINT PASS / RESULT COMMIT PENDING / MATRIX
PROHIBITED.**

## Next criterion

Commit this exact visible-result boundary. Then write, validate, checkpoint,
and commit the fixed `20031..20034` matrix dispatch boundary before starting
any matrix case.

## Phase 08.8 M8.9 v8.12 broad-matrix dispatch boundary — 2026-07-31

The fixed v8.12 visible result is committed:

```text
24170d2 phase 08.8: record v8.12 visible pass
```

The worktree was clean immediately afterward. This boundary authorizes one
installed serial invocation containing exactly four fixed headless cases:

```text
installed scenario:
  /tmp/phase08_8_v8_12_release_qual.HnEptF/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/phase08_v8_12_broad_matrix.yaml
installed/source scenario sha256:
  311667e8c8d330732ea32c894bb78fed43b63cd23ef86f486ca25c86fe727bdc
seeds:
  20031, 20032, 20033, 20034
ROS_DOMAIN_ID / ROS_LOCALHOST_ONLY:
  220 / 1
presentation / execution:
  headless Gazebo / serial
attempts / retries per case:
  1 / 0
run root:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_8_12_broad_matrix
```

Frozen cases:

| Seed | Local position m | Local/global input | Case key | Topology hash |
|---:|---|---|---|---|
| `20031` | `(0.8838834765, 0.8838834765)` | `533.3333333333 / 1600` (`1:3`) | `331c7bd7aca41ef2373d6c58300d8073b5185a4c9195254754709c6dfe86c868` | `da4e64008b2950c93ccbf08e31b6ead65c4fe6cc5791991965b9ceb156006bd6` |
| `20032` | `(1.0606601718, 1.0606601718)` | `320 / 1600` (`1:5`) | `941720dabb4f49053e87ec64b2ba597003aee436bda1855e70032448da25db40` | `14f52589f05b2dc62f8b12122f823fb97b8e897b304462e37087c1100944560c` |
| `20033` | `(0.7500000000, 1.2990381057)` | `533.3333333333 / 1600` (`1:3`) | `14dde5e389e4e6b767d93a34210633bbf76744c6d8b9fb49d3046a94b2160573` | `faafb05e4b004ef7d444c56badec3ea55f88107fcd052fef8c094782e7a82e26` |
| `20034` | `(0.8750000000, 1.5155444566)` | `320 / 1600` (`1:5`) | `4e8006c1d102711de1cc31839cf0280ab3927a61f4a19bb75f9fd38e4e63ac64` | `47dd95926a4c9345770a0303ac83287c1f26a41afee108e6c6dc5d089e36837b` |

All cases use start `(0.0, 0.0)`, global `(3.5, 3.5)` at input `1600`,
schema v14, known source count two, evaluator-only topology qualification,
the enabled `0.50 m` interior-anchor fallback, exact one-fill cardinality,
accepted direct or strictly owned assisted recovery, strict raw ranking, and
a post-recovery evaluator radius of `0.50 m`. The controller receives no
source location, role, intensity, topology record, or evaluator coordinate.

The installed dry-run was invoked from `/tmp` through the isolated release
overlay. The final wrapper explicitly removed inherited parent-workspace
prefixes, resolved all `4` runs and `0` unsupported cases, and created no run
root:

```text
/tmp/phase08_8_v8_12_matrix_boundary_dry_run.log
SHA-256:
  3495f7c2bf000beed1541de8ac97ef653482358efea100652a508f555a89281e
```

Three earlier shell-wrapper preflights reached no scenario execution and
created no run root. The first enabled nounset before sourcing ROS; the next
two correctly detected inherited parent-workspace Python/prefix paths before
the final wrapper removed them. Their retained log hashes are respectively
`8e1897c5e8601d54ab323b996c58cf689eba7afb53430d60b2cd025a21083673`,
`f6e36d719f9f3462d854506ba2ab0e7f81406bac7c0a5ca3929bd0e8c2876677`,
and `f6e36d719f9f3462d854506ba2ab0e7f81406bac7c0a5ca3929bd0e8c2876677`.
They are boundary-command corrections, not dispatched cases or retries.

The runner must stop at the first formal or cleanup failure. It may not skip,
retry, replace, or tune a case. The population gate is `4/4` formal passes,
four complete recordings, final zeros and cleanups, four exact one-fill
recoveries, four valid approach anchors, four strict rankings, four graceful
proximity stops, SQLite integrity, one analysis per complete dispatched run,
and `36/36` plots.

The installed runner must be invoked from `/tmp` with the same sanitized
isolated environment, under the scenario's finite `720.0 s` simulation,
`900.0 s` wall, and `45.0 s` shutdown-grace limits plus an explicit outer
`4200 s` timeout. No Gazebo, scenario runner, recorder, analyzer, rosbag
recorder, or physical process was started while writing this boundary. The
matrix root is absent. Physical stopping remains manual operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M8.9 — V8.12 FOUR-CASE MATRIX BOUNDARY WRITTEN / INSTALLED
DRY-RUN 4/4 / DISPATCH CHECKPOINT AND COMMIT PENDING / MATRIX PROHIBITED.**

## Next criterion

Validate source/install parity, root absence, inactive runtime, context, and
diff; checkpoint Phase 08; and commit this exact boundary. Only then invoke
the installed matrix once. Preserve every dispatched case and stop without a
retry if any fixed case fails.

## Phase 08.8 M8.9 v8.12 broad-matrix dispatch checkpoint — 2026-07-31

The exact installed four-case serial, headless, first-failure-stop,
one-time/no-retry boundary received the required Phase 08 checkpoint against
visible-result HEAD `24170d2`.

```text
base HEAD:
  24170d2ba9b6725f52ca071917c24636416b16e3
status sha256 before this checkpoint note:
  ac370eda26d49d5677734dcb2d67b946cd6dd906e9c3cc07fdc9e2bba17d87f4
checkpoint sha256 before this checkpoint note:
  79a1ac93cdde28e9e35a78f2fbd60aa48b1c13d54cf43b9a7bd4cdedb218e8f3
installed/source scenario parity:
  PASS
installed/source scenario sha256:
  311667e8c8d330732ea32c894bb78fed43b63cd23ef86f486ca25c86fe727bdc
installed dry-run / unsupported:
  4 / 0
Phase 08 implement context / git diff check:
  PASS / PASS
active simulation/analysis/physical runtime:
  none
matrix root:
  absent
```

## Current milestone

**PHASE 08.8 M8.9 — V8.12 FOUR-CASE MATRIX BOUNDARY / INSTALLED DRY-RUN
4/4 / DISPATCH CHECKPOINT PASS / DISPATCH COMMIT PENDING / MATRIX
PROHIBITED.**

## Next criterion

Commit this exact two-file dispatch boundary. Then invoke the installed matrix
once on domain `220`, preserve every dispatched result, and stop without a
retry if any fixed case fails.

## Phase 08.8 M8.9 v8.12 broad-matrix result — 2026-07-31

The committed installed matrix boundary executed exactly once from clean
dispatch HEAD `dd2185dba1b9e1f979a72cf1b5b4a960912ee35d`. The serial runner
dispatched seed `20031`, classified it as a formal failure, and stopped before
seeds `20032..20034` exactly as required. There was no retry, replacement, or
tuning.

```text
summary:
  /home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_12_broad_matrix/scenario_summaries/
  20260731T233137289914Z_phase08_v8_12_broad_matrix.yaml
summary sha256:
  01cd46bed898afbd229abd2c0fda6db4d0e70487f6cb7716c4a409aec3182216
resolved / dispatched / retries:     4 / 1 / 0
runner return / stop reason:         1 / run_failure
formal predicates:                   13/14 PASS
sole failed predicate:               escape_command_ownership
exact failure:
  direct measured fill-to-exit alignment is below 0.80
Stage A / Stage B:                   PASS / PASS
created / typed / active fills:      1 / 1 / 1
anchor mode / displacement:          interior_farthest / 1.318197736 m
escape branch / successes:           direct / 1
candidate-two separation margin:     2.518884161
first proximity / final distance:    0.127753592 / 0.127721319 m
recording / final zero / cleanup:    PASS / PASS / PASS
SQLite quick_check:                  ok
```

The direct branch cleared the `1.366770829 m` exit radius and reached
`1.425082539 m` maximum radial distance. Its measured returned-`SEARCH` exit
was `1.439287647 m` from the fill center, but its curved direction alignment
was `0.735562525`, below the fixed `0.80` threshold by `0.064437475`
(`42.6452` versus `36.8699` maximum degrees).

This remains a formal acceptance failure. The completed local recovery,
ordinary returned search, strict raw-cost ranking, `GOAL_HOLD`, and final
global proximity remain scientific behavior evidence. No gate was weakened
or reclassified.

The exact run was analyzed once. Critical inputs, fresh and stored Phase 05
validation, and `9/9` plots are complete with zero analysis failures. Analyzer
status is `partial` only because one optional generic `state_durations` metric
observed one state gap over `0.150 s`, independently of the formal failure.

Durable result:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m8_9_v8_12_broad_matrix.md
```

No simulation, analysis, or physical process remains active. The v8.12 stop
condition is reached. Seeds `20032..20034` remain undispatched, and no v8.13
is authorized. Simulation stopping remains evaluator-only; physical arrival
remains manual operator `Ctrl+C`.

## Current milestone

**PHASE 08.8 M8.10 — V8.12 TERMINAL CLOSEOUT / FIRST MATRIX CASE FORMAL
13/14 FAIL WITH SCIENTIFIC LOCAL-TO-GLOBAL COMPLETION / REMAINING CASES NOT
DISPATCHED / NO RETRY / NO V8.13 / CLOSEOUT QUALIFICATION, CHECKPOINT, AND
COMMITS PENDING.**

## Next criterion

Recheck every dispatched result and undispatched definition, retained plots,
historical preservation, context, diff, infrastructure, and inactive runtime.
Then checkpoint Phase 08 and commit the bounded final report, handoff,
navigation, result report, and live-status closeout. Do not start Gazebo or
physical hardware.

## Phase 08.8 M8.10 terminal closeout qualification — 2026-07-31

The terminal no-Gazebo closeout rechecked the current documentation, retained
v8.10-v8.12 fixed results, terminal bag and analysis, historical anchors,
process boundary, and Git scope. No source, launch, scenario, world, test, run,
bag, result, analysis, plot, simulator, ROS graph, analyzer, or physical
execution changed after dispatch HEAD `dd2185d`.

```text
required Phase 00 audit documents:             PASS
Phase 08 implement context:                    PASS
changed paths outside Phase 08.8 docs:         0
relative Markdown links:                       38/38
staged git diff --check:                       PASS

v8.10 retained results / plots:                12 / 108
v8.11 retained results / plots:                 7 / 63
v8.12 retained results / plots:                 2 / 18
v8.12 matrix summary run entries:               1
v8.12 matrix seed 20031 entries:                1
v8.12 matrix seed 20032-20034 entries:           0
terminal bag SQLite PRAGMA quick_check:         ok
terminal analysis failures / plots:             0 / 9

historical V6 / three world hashes:             unchanged / unchanged
active simulation, analysis, or physical:      none
```

Document hashes before this qualification note:

```text
implementation_sequence.md:
  bced1672af9e132341aeb3699b36c8535022e740a60d06df04a34feed91751cb
phase_08_8_handoff.md:
  4d66bf71e229920177323c93217dabc10ae126f3efc92d8c4b9d5ae2aca22ec1
phase_08_status.md:
  dd36d733374a75c3d481de7de77401b5f8dad4b7ec7c8aea00c34b7d4c609339
phase_08_8_final_report.md:
  552bdcf465de35ac76cc190547881d2f4ff9076dc6bacdd86c1e58699d80a55a
phase_08_8_m8_9_v8_12_broad_matrix.md:
  1923c697ef4491f3ee41603f023faf27d1af03d3030c22d676a35ae51739555e
```

Retained anchors remain:

```text
gazebo_empty.world:
  3085542f9dc1d13fdf9368a24808a226908d1a2c5a7a4ffd07bc6f374ca14b43
gesc_gaussian_validation.world:
  8ecc1a231efec24401d74fef3cd5139d48c6029f88e71d044cefdf2fd14c5bef
gesc_gaussian_corner_origin_validation.world:
  88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf
phase_08_v6_selection.json:
  dcdbf937fe3de0cab9449c2b01af79fd938e1d3f9791b4897937875d0747590d
```

## Current milestone

**PHASE 08.8 M8.10 — TERMINAL CLOSEOUT QUALIFICATION PASS / V8.12 CLOSED /
NO V8.13 / PHASE 08 CHECKPOINT AND CLOSEOUT COMMITS PENDING.**

## Next criterion

Run the Phase 08 material checkpoint, record its receipt, and commit this exact
terminal result and closeout. Then record the clean post-commit receipt and
complete the approved goal. Do not start Gazebo or physical hardware.

## Phase 08.8 M8.10 terminal closeout checkpoint — 2026-07-31

The terminal v8.12 result, one-time analysis, undispatched-case accounting,
amended final report, handoff, navigation, historical preservation, and
inactive runtime received the required Phase 08 material checkpoint against
dispatch HEAD `dd2185d`.

```text
base HEAD:
  dd2185dba1b9e1f979a72cf1b5b4a960912ee35d
generated UTC:
  2026-07-31T23:54:53+00:00
status sha256 before this checkpoint note:
  29c8a106c80960a3b3a61ccd0e76affccbb1eeee0bdc2ab46e9ec8bf08774dd5
checkpoint sha256 before this checkpoint note:
  dade9a29fdb4b1bc93d638093c388579970a2723a2bc8b09bc67dae21895ce92
active subphase Plan sha256:
  1f028088939e0a71eceb755329e8e5238bcb6fdb3c4f0eda4901571c872c9cbb
Phase 08 implement context:
  PASS
staged and unstaged diff check:
  PASS
active simulation/analysis/physical runtime:
  none
```

## Current milestone

**PHASE 08.8 M8.10 — TERMINAL CLOSEOUT QUALIFICATION AND CHECKPOINT PASS /
V8.12 CLOSED / NO V8.13 / CLOSEOUT COMMIT PENDING.**

## Next criterion

Commit this exact terminal boundary. Then verify the commit and clean
worktree, add the bounded post-commit status receipt, commit that receipt, and
complete the approved goal. Do not start Gazebo or physical hardware.

## Phase 08.8 M8.10 terminal closeout post-commit receipt — 2026-07-31

The bounded terminal result and closeout were committed:

```text
9335da2057ac488944578af9f941d8d8fb6164ae
  phase 08.8: close v8.12 terminal boundary
```

Immediate post-commit verification:

```text
branch:
  feature/gesc-gaussian-robustness-v1
ahead of matching origin branch:
  176 commits
tracked and untracked worktree changes:
  none
active simulation/analysis/physical runtime:
  none
matrix report sha256:
  1923c697ef4491f3ee41603f023faf27d1af03d3030c22d676a35ae51739555e
final report sha256:
  552bdcf465de35ac76cc190547881d2f4ff9076dc6bacdd86c1e58699d80a55a
handoff sha256:
  4d66bf71e229920177323c93217dabc10ae126f3efc92d8c4b9d5ae2aca22ec1
checkpoint sha256:
  dade9a29fdb4b1bc93d638093c388579970a2723a2bc8b09bc67dae21895ce92
```

## Current milestone

**PHASE 08.8 M8.10 COMPLETE / V8.12 TERMINALLY CLOSED / V8.12 VISIBLE
FORMAL PASS / V8.12 MATRIX FIRST CASE SCIENTIFICALLY COMPLETE BUT FORMAL
13/14 FAIL / REMAINING CASES NOT RUN / NO RETRY / NO V8.13 / NO PHYSICAL
MOTION.**

## Next criterion

There is no remaining Phase 08.8 criterion. Start only a separately planned
and authorized Phase 09 boundary. Physical motion remains unauthorized until
that future phase receives explicit motion authority; physical arrival remains
manual operator `Ctrl+C`.
