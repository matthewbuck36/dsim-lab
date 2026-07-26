# Phase 08 Live Status

Last verified: `2026-07-25T19:32:36-07:00`
Status: `IN PROGRESS — PHASE 08.1 DIAGNOSTIC RECOVERY`

## Objective

Diagnose the closed failed Phase 08 v2 activation evidence, correct bounded
implementation and scenario-contract defects, simplify obstructive workflow
rules, and prove the corrections with focused tests and minimal versioned
simulation probes. Historical v1 and v2 evidence remains immutable and cannot
count toward a future acceptance attempt.

## Verified repository state

- Branch: `feature/gesc-gaussian-robustness-v1`
- HEAD at v2 implementation start:
  `787350e38522856f6463e645714dcc512ad2a5e5`
  (`phase 08: stage validation v2 and harden context recovery`).
- Working tree at v2 implementation start: clean and matched
  `origin/feature/gesc-gaussian-robustness-v1`.
- Plan: `docs/codex/gesc_gaussian/plans/phase_08_plan.md`
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

## Current milestone

- Historical milestone: ten-run Phase 08 v2 activation gate — **FAILED and
  closed** at `2d796dd`.
- Completed milestone: Phase 08.1 M1 durable diagnosis and workflow correction.
- Completed milestone: Phase 08.1 M2 fill-latency correction.
- Completed milestone: Phase 08.1 M3 verification-boundary correction.
- Current milestone: Phase 08.1 M4 readiness and evidence-semantics correction.
- Current plan:
  `docs/codex/gesc_gaussian/plans/phase_08_1_plan.md`.
- Next criterion: add a bounded simulation readiness barrier for responsive
  controller-manager/data publishers, correct the controller startup-watchdog
  race, and validate event timestamps at producer/stream granularity without
  weakening source/request causality.

## Current problem or blocker

- No Level A blocker is present.
- V2 remains a Level C failure and cannot be resumed, retuned, relabeled, or
  counted toward a new claim.
- M2 removed the repeated full-history synchronization delay that blocked the
  fill node for 5.5–15.7 seconds. It does not claim formal timestamp
  monotonicity: the fill node still uses a single-threaded executor, so M4 must
  test producer/stream ordering and concurrent clock servicing separately.
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

## Files currently relevant

- `docs/codex/gesc_gaussian/plans/phase_08_plan.md`
- `docs/codex/gesc_gaussian/plans/phase_08_1_plan.md`
- `docs/codex/gesc_gaussian/validation/phase_08_v1_failure_closeout.md`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_run_manifest.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_gate_results.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_validation_report.md`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_failure_report.md`
- `docs/codex/gesc_gaussian/handoffs/phase_08_handoff.md`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/phase08_validation.py`
- `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py`
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/basin_estimator.py`
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`
- `ros2_ws/src/ros_esc/test/test_phase08_validation.py`
- `ros2_ws/src/ros_esc/test/test_state_machine.py`
- `ros2_ws/src/ros_esc/test/test_supervisor_integration.py`
- `ros2_ws/src/ros_esc/test/test_observability_contract.py`
- `ros2_ws/src/ros_esc/test/test_robust_gaussian_algorithm.py`
- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`

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

## Remaining work

Follow `phase_08_1_plan.md` milestones M1–M7:

1. durable diagnosis/workflow correction;
2. bounded fill-latency correction;
3. verification-boundary correction;
4. simulation readiness and timestamp/evidence semantics;
5. reachable scenario contracts;
6. minimal versioned simulation probes;
7. Phase 08.1 handoff and a separately reviewed v3 recommendation.

No v3 tuning, holdout, acceptance denominator, tag, or physical motion is
authorized in this plan.

## Stop conditions

- Stop for any Level A architectural, safety, ownership, cost-sign/unit, or
  unrelated-work contradiction.
- Stop before tuning if any activation case lacks its required state/event.
- Stop after holdout if fewer than 18/20 runs succeed end to end or any required
  evidence/collision/lifecycle gate is invalid.
- Never create the simulation-ready tag unless every amended gate passes.
- Gate 2 failed, so all later Phase 08 stages and the tag are forbidden.

## Compaction recovery

Phase 08 v2 is terminally closed; Phase 08.1 is active. Reread `AGENTS.md`,
`phase_08_plan.md`, `phase_08_1_plan.md`, and this status; inspect Git status
and the relevant diff; identify the next incomplete Phase 08.1 milestone; and
continue from retained evidence. Never resume or relabel v1/v2, and never rerun
their matrices merely to recover context.
