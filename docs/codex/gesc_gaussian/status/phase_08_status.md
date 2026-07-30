# Phase 08 Live Status

Last verified: `2026-07-30T03:54:09-07:00`
Status: `PHASE 08.7 M4.4 VISIBLE PROBE PASS; CONDITIONAL EIGHT-CASE SUITE DISPATCH PENDING`

## Objective

Demonstrate with exactly two lights that unchanged GESC can converge at the
lower-output local light, create a Gaussian fill there, escape, recenter, and
resume search. Sweep physical Philips Hue-compatible nominal ratios inside the
`4 m x 4 m` laboratory envelope without steering or orienting the robot toward
the local light. Preserve controller ownership, cost sign and units, canonical
topics, selectable legacy behavior, original sensor rotation, and
simulation/physical algorithm parity. Treat global convergence as secondary,
defer three-light execution, and make no simulation-readiness claim.

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
