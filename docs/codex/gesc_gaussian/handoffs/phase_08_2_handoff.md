# Phase 08.2 Handoff

## Terminal disposition

**PHASE 08.2 COMPLETE — RECENTER RECOVERY VALIDATED; NO V3 ACCEPTANCE,
SIMULATION-READY TAG, PHASE 09, OR PHYSICAL WORK.**

Phase 08.2 corrected the one observed Phase 08.1 algorithm failure and passed
its declared deterministic, integration, build, dry-run, and fresh full-path
Gazebo gates. The retained development run reached:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

It created one typed fill, completed one escape, completed recenter in about
`8.61 s`, and returned to search without timeout, failsafe, collision,
recording, cleanup, or final-zero failure.

This validates recenter recovery only. It is not a v3 parameter freeze,
selection-blind holdout, robustness denominator, reproducibility result, or
simulation-readiness claim.

## Authority and preserved evidence

- Branch: `feature/gesc-gaussian-robustness-v1`.
- Phase 08.2 base: `db8bd66`
  (`phase 08.1: close mixed diagnostic recovery`).
- Phase 08.2 commits before terminal closeout:
  - `1858f1e` — `phase 08.2: plan bounded recenter recovery`
  - `8cefbfc` — `phase 08.2: correct bounded recenter selection`
  - `204d1a1` — `phase 08.2: validate recenter probe candidate`
  - `f084803` — `phase 08.2: seal recenter development probe`
- Candidate implementation commit:
  `204d1a1c9efad3d7d3b9f81315437fa8f671bdae`.
- Historical v1, v2, and Phase 08.1 evidence was not resumed, overwritten,
  relabeled, or counted.
- No simulation-ready tag exists.
- No physical hardware ran.

Related durable artifacts:

- [Phase 08.2 Plan](../plans/phase_08_2_plan.md)
- [Phase 08.1 handoff](phase_08_1_handoff.md)
- [Phase 08 live status](../status/phase_08_status.md)
- [test command record](../test_commands.md)

## Implemented correction

The correction stays inside the existing supervisor and launch owners:

- `escape_recenter.py` separates hard fill/wall safety eligibility from
  direction preference.
- `ESCAPE_ASSIST` retains its preferred hemisphere, clearance-first score,
  fixed candidate order, and cached selection.
- `RECENTER` considers every fixed `pi/4` candidate that passes hard safety,
  then ranks by predicted center-distance reduction, center alignment,
  clearance, minimum rotation, and original candidate order.
- Recenter selection is recomputed on every supervisor update and increments
  the observable direction revision for each successful reselection.
- The bounded command is checked using actual current-yaw translation over
  the existing `supervisor_command_stale_sec=0.50` horizon.
- Unsafe forward translation becomes zero while the bounded angular command
  remains available for rotation-only recovery.
- The existing `0.5 m` lookahead, fill radius, wall margin, gains, velocity
  caps, `0.25 m` tolerance, `1.0 s` hold, and `30.0 s` timeout remain
  unchanged.

The existing launch argument is passed additively into the supervisor. No
node, topic, message, dependency, recorder, analyzer, or
simulation/physical algorithm fork was added.

## Deterministic and source-state validation

The exact retained M6 pose/fill regression uses explicit Euler at `0.1 s`,
current-yaw translation followed by wrapped-yaw update, the unchanged safety
geometry, and the `0.50 s` command horizon. It must remain safe, enter and
hold the `0.25 m` tolerance for one second, and complete within `20.0 s`.

Final results:

- Focused source/state suite: `112 passed in 3.56 s`, compared with the
  pre-change `101 passed` baseline.
- Broad non-linter functional suite:
  `289 passed, 2 skipped, 3 deselected in 15.57 s`, compared with
  `278 passed, 2 skipped, 3 deselected` before Phase 08.2.
- The two skips are the explicit visible-Gazebo recording and
  recorded-headless-Gazebo opt-in tests.
- The three deselections are repository linter markers.
- Isolated build: existing packages `ros_esc_interfaces`,
  `turtlebot3_rotating_sensor`, and `ros_esc` passed.
- Installed one-case dry run: one resolved run, zero unsupported cases.
- Installed launch arguments and supervisor instantiation passed.
- Modified Python compilation and `git diff --check` passed.
- Same-configuration `ament_flake8` findings improved from `623` at
  `db8bd66` to `613`; `ament_pep257` remained `7/7`. Changed-line comparison
  reports zero new flake8 and zero new pep257 findings.

The seven lint findings and remaining flake8 findings are inherited
whole-file style debt; Phase 08.2 did not add to them.

## Sealed Gazebo development probe

Suite:
`ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_2_recenter.yaml`

Suite SHA-256:

```text
1b116ef7984d8a679f69da919576125a1ad066da3d55098466da9afac2bae017
```

The suite contains one GUI-enabled schema-v3 case:

- case: `recenter_retained_fill_create`
- seed: `8304`
- case key:
  `6eb811130559703b3253b7eb49d842165037902b12ad47b4d8747d408da70c47`

Evidence root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_2_recenter
```

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_2_recenter/2026-07-26/20260726T075031828248Z_simulation_phase08_2_recenter-recenter_retained_fill_create-robust_gaussian_v1-6eb8111305_92a4911a
```

Run summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_2_recenter/recenter_retained_fill_create_summary.yaml
```

The runner returned exit `0`. `record_run` returned `0` without timeout;
recording completed; cleanup retained no new node or session process; and all
seven schema-v3 predicates passed:

- recording complete;
- cleanup complete;
- required contiguous state path;
- required event membership;
- no forbidden state;
- no forbidden event;
- no collision.

Observed required events included `CONVERGENCE_CONFIRMED`, `FILL_CREATED`,
`ESCAPE_STARTED`, `RECENTER_STARTED`, and `RECENTER_COMPLETE`.
`TIMEOUT`, `FAILSAFE`, `FILL_REJECTED`, and `FILL_DESIGN_FAILED` were absent.

No replacement or additional probe ran.

## Retained behavioral and recording evidence

The one-time standard analyzer completed successfully and wrote 22 files,
including 11 tables and eight plots, to the run-local `analysis/` directory.
It was not rerun.

Key retained metrics:

- fill count: `1`;
- escape attempts/successes/failures: `1/1/0`;
- escape duration: `7.532641327 s`;
- recenter duration: `8.610255022 s`;
- observed recenter distance: first `0.365533 m`, maximum `0.397381 m`,
  final/minimum `0.238489 m`;
- maximum valid direction revision observed during recenter: `151`;
- terminal algorithm state: `SEARCH`;
- collision: `false`;
- final goal distance: `0.277956 m`;
- simulation ground-truth result: passed.

The analyzer reports controller goal success as `false` because this
development contract required return to `SEARCH`, not a subsequent
`EVENT_GOAL_REACHED`/`GOAL_HOLD` cycle. That metric is retained and is one
reason this single development run cannot be treated as v3 acceptance.

Recording completeness passed with no failures or warnings. In particular:

- final zero passed on the final command, command-array, and control-diagnostic
  streams;
- final readiness was false;
- pre-readiness motion and lifecycle checks passed;
- typed timestamps were nonregressing and within `/clock`;
- algorithm-event emission and source causality passed;
- strict finite JSON passed;
- the bag was readable and all required topics were present.

The analyzer retained `23,243` synchronized anchors. Raw bag SHA-256:

```text
47e06cb865f6cb9b5976d2387d9ad479fa90b17bd1efc5ef46df15627c2f226c
```

## Level B correction and compatibility

The original shared selector was safe but could choose and retain tangential
recenter directions indefinitely. The retained Phase 08.1 full-contract
failure demonstrated that contradiction. Phase 08.2 treated it as a bounded
Level B implementation correction: it changed only recenter selection and
actual-command safety filtering, preserved assist behavior and public
architecture, added focused tests, and did not weaken any runtime or
acceptance gate.

Legacy remains selectable and retains controller ownership, cost sign/units,
topics, messages, and final-zero behavior. The same supervisor logic remains
shared by simulation and future physical use.

## Remaining limitations and next step

Phase 08 v1 and v2 remain failed. Phase 08.1 remains a mixed diagnostic
closeout. Phase 08.2 proves one bounded recenter recovery path; it does not
prove the full robustness envelope.

The next justified action is to create and review a separate v3 acceptance
Plan. That Plan must declare development/tuning limits, a clean freeze,
selection-blind holdout, unique validation denominator, reproducibility
stage, completeness/collision/behavioral gates, and a fresh evidence root.
Phase 08.2 code and evidence may inform that Plan but must not be counted in
its acceptance denominator.

Do not start v3 execution, create a simulation-ready tag, enter Phase 09, or
run physical hardware merely from this handoff.

## Git closeout

The terminal documentation/checkpoint commit follows this handoff. At handoff
authoring, the implementation and sealed probe commits were clean and the
branch was ahead of origin. The final closeout must report the exact terminal
commit and `git status`.
