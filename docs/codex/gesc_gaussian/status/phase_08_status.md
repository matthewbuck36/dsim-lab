# Phase 08 Live Status

Last verified: `2026-07-25T16:48:05-07:00`
Status: `NOT_STARTED`

## Objective

Implement the amended staged Phase 08 v2 workflow, repair and prove the
activation and rotation-aware goal-verification contracts, freeze one selected
profile, and evaluate the declared 120-run empirical design without mutating or
counting historical v1 evidence.

## Verified repository state

- Branch: `feature/gesc-gaussian-robustness-v1`
- HEAD: verify again at implementation start; this status does not freeze the
  current uncommitted documentation work.
- Working tree: the staged-plan and context-retention changes were prepared as
  one bounded documentation/tooling commit. Verify the clean state and current
  HEAD again at Phase 08 implementation start.
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

## Current milestone

- Milestone: durable v1 failure closeout and v2 implementation preflight.
- Implementation complete: `no`
- Next acceptance criterion: preserve and inventory v1 evidence, then add
  focused regressions that prove the corrected detector-to-supervisor
  activation and rotation-aware goal dwell before any new batch.

## Current problem or blocker

- The installed `validate_robustness` command and Phase 08 scenarios still
  implement the retired v1 workflow.
- The v2 activation repair, scenario manifests, stages, and gates have not been
  implemented or run.

## Files currently relevant

- `docs/codex/gesc_gaussian/plans/phase_08_plan.md`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/phase08_validation.py`
- the existing convergence-detector and supervisor owners identified during
  implementation preflight
- the existing rotation-aware goal-verification owner identified during
  implementation preflight
- `ros2_ws/src/ros_esc/test/test_phase08_validation.py`

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
- No Phase 08 v2 build, pytest, Gazebo run, bag recording, freeze, acceptance
  gate, or tag has been executed.

## Attempts not to repeat

- Do not resume or overwrite the v1 partial full pass.
- Do not reuse exposed v1 holdouts as v2 holdouts.
- Do not accept the historical C8 tie-break as a v2 selection result.
- Do not run planned v2 commands until their interface and scenario files are
  implemented and tested.
- Do not infer behavioral success from recording completeness or cleanup.

## Remaining work

1. Start a fresh Phase 08 Implement chat from the clean committed checkout.
2. Reread `AGENTS.md`, the Phase 08 plan, this status, and the current Git state.
3. Rerun Phase 08 implementation preflight.
4. Write `phase_08_v1_failure_closeout.md` from immutable v1 evidence.
5. Implement and test the activation and goal-verification corrections.
6. Implement the v2 staged scenarios and extend the existing validator.
7. Run only the next eligible stage and update this file after every milestone.

## Stop conditions

- Stop for any Level A architectural, safety, ownership, cost-sign/unit, or
  unrelated-work contradiction.
- Stop before tuning if any activation case lacks its required state/event.
- Stop after holdout if fewer than 18/20 runs succeed end to end or any required
  evidence/collision/lifecycle gate is invalid.
- Never create the simulation-ready tag unless every amended gate passes.

## Compaction recovery

Before further changes, reread the Phase 08 plan and this file, inspect Git
status and the current diff, identify the next incomplete acceptance criterion,
and continue only from that verified state.
