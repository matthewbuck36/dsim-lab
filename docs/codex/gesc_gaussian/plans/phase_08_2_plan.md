# Phase 08.2 Plan — Recenter Recovery

## Summary

- Recenter is the only currently observed algorithm failure remaining from M6.
  The calibrated-goal path passed, and the fill/create plus escape path worked
  before recentering.
- Fixing recenter does **not** make v3 successful. It closes the current
  engineering blocker and permits a separate v3 plan. V3 succeeds only after a
  frozen implementation passes activation, tuning/freeze, selection-blind
  holdout, unique validation, reproducibility, completeness, collision, and
  behavioral gates.
- Preserve all v1, v2, and Phase 08.1 evidence. Do not run formal v3 stages,
  create a readiness tag, enter Phase 09, or use physical hardware.

## Implementation changes

- Separate fill/wall safety eligibility from direction preference in
  `escape_recenter.py`. Preserve the current hemisphere restriction,
  clearance-first score, and cached behavior exactly for `ESCAPE_ASSIST`.
- Add a recenter-specific selector that considers all fixed `pi/4` candidates
  passing wall/fill safety, including candidates that temporarily move away
  from room center. Rank deterministically by:
  1. greatest predicted center-distance reduction at the existing `0.5 m`
     lookahead;
  2. center alignment;
  3. fill/wall clearance;
  4. minimum absolute rotation;
  5. existing candidate order.
- Recompute the recenter selection on every supervisor update instead of
  retaining a safe but tangential direction indefinitely. Increment the
  observable direction revision for each successful recenter reselection; do
  not alter assist revisions.
- After computing the bounded linear/angular command, validate the actual
  current-yaw translation rather than the desired world-frame direction:
  - while inside an active fill disk, forward translation must have
    nonnegative outward projection and must not reduce fill-center distance;
  - after leaving a disk, the projected segment must not intersect or re-enter
    it;
  - the projected endpoint must remain inside the wall-margin inset;
  - unsafe forward motion becomes zero linear velocity while retaining the safe
    angular command, allowing rotation in place instead of immediate failsafe.
- Use the existing `supervisor_command_stale_sec=0.50` launch value as the
  projection horizon by also declaring/passing it to the supervisor. This is
  an additive supervisor parameter, not a new launch argument.
- Keep the existing recenter settings unchanged: `30.0 s` timeout, `0.25 m`
  tolerance, `1.0 s` hold, current gains and velocity caps, `0.5 m` lookahead,
  `pi/4` candidate step, fill radius, and wall margin. Add no node, topic,
  message, dependency, recorder, analyzer, or physical/simulation fork.

## Validation and runtime evidence

- Extend geometry tests for deterministic ranking, temporary negative center
  progress, tie-breaking, multiple fills, walls, no-candidate failure, and
  unchanged `ESCAPE_ASSIST` selection.
- Add command-sweep tests covering inward motion while inside a fill, outward
  recovery, post-exit re-entry, wall crossing, rotation-only recovery, finite
  inputs, and bounded commands.
- Add the exact retained M6 geometry regression:
  - pose `(-0.922899286, 0.299448541)`, yaw `-0.395048403`;
  - fill center `(-0.625781953, -0.056395888)`, radius `0.608674749 m`;
  - room `[-2,2]^2`, margin `0.35 m`, target `(0,0)`;
  - explicit-Euler `dt=0.1 s`, current-yaw translation followed by wrapped yaw
    update.
- Require this deterministic trace to remain safe, enter and hold the `0.25 m`
  tolerance for one second, and finish within `20.0 s`. The planning prototype
  completed in approximately `17.6 s`; the test threshold provides `2.4 s`
  deterministic regression margin and remains `10 s` below the unchanged
  runtime timeout.
- Extend supervisor integration coverage for `RECENTER -> SEARCH`,
  `RECENTER_COMPLETE`, safe linear suppression with continued rotation,
  timeout behavior, observability, final zero, legacy arbitration, and
  unchanged assist behavior.
- Run:
  - focused tests, starting from the confirmed `101 passed` baseline;
  - the broad non-linter functional suite, comparing against
    `278 passed, 2 skipped, 3 deselected`;
  - isolated builds of the existing ROS packages;
  - runtime launch instantiation and a one-case scenario dry run.
- Commit the validated implementation before simulation.

## Gazebo probe and closeout

- Create a new one-case schema-v3 development suite based on the retained
  `activation_fill_create` geometry and seed `8304`; do not edit the Phase 08.1
  suite.
- Require the full contiguous path
  `SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE -> RECENTER -> SEARCH`,
  plus `FILL_CREATED`, `ESCAPE_STARTED`, `RECENTER_STARTED`, and
  `RECENTER_COMPLETE`. Globally forbid `TIMEOUT`, `FAILSAFE`, fill-design
  failure, collision, incomplete recording, missing cleanup, and missing final
  zero.
- Seal the suite hash and run one serial, finite Gazebo probe with GUI enabled
  under the fresh evidence root
  `~/Experiments/GESC-Gaussian/runs/phase08_2_recenter`. Analyze the retained
  bag exactly once and preserve the attempt regardless of outcome.
- Permit one identical replacement only for objectively pre-readiness
  infrastructure invalidity, declared before redispatch. A valid behavioral
  failure is never replaced. Additional probes require a separately recorded,
  distinct unresolved question.
- Phase 08.2 passes only when code tests/builds/dry-run pass and the fresh full
  Gazebo contract passes. Then close the status, checkpoint, write the
  Phase 08.2 handoff, and recommend a separate v3 acceptance Plan.
- If recenter still fails, preserve the evidence and close Phase 08.2 honestly;
  do not increase the timeout, shrink avoidance geometry, weaken forbidden
  evidence, or begin v3.

## Assumptions

- Clean starting point is commit `db8bd66`; historical evidence remains
  immutable.
- The current safety bounds and recenter parameters remain authoritative and
  are not tuning variables in Phase 08.2.
- Passing Phase 08.2 means "recenter recovery validated", not "v3 accepted" or
  "simulation-ready".

## Milestones

1. **M1 — plan and preflight:** persist this Plan, reopen the live status,
   validate context, record the baseline, and checkpoint the clean starting
   boundary.
2. **M2 — deterministic recenter correction:** implement safety-only
   eligibility, recenter ranking, per-update reselection, actual-command sweep
   suppression, and their focused deterministic/integration tests.
3. **M3 — source-state validation:** run the focused and broad functional
   suites, isolated build, runtime launch instantiation, one-case dry run, and
   commit the clean probe candidate.
4. **M4 — one retained Gazebo probe and closeout:** seal and execute the
   predeclared case once, analyze once, verify cleanup/final zero, close the
   status honestly, checkpoint, write the handoff, and commit the retained
   result.
