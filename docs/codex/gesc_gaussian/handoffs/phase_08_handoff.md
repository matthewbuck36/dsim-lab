# Phase 08 Handoff

## Terminal outcome

**FAILED — LEVEL C.**

The staged Phase 08 v2 restart implemented and tested the corrected
detector-to-supervisor activation contract, rotation-aware goal verification,
sealed 120-run orchestration, and partial/final reporting. The mandatory
ten-run activation stage then failed its early gate: only 1/10 runs satisfied
the complete integrity and declared lifecycle contract.

Per the saved plan, execution stopped before tuning. No v2 parameter set was
selected or frozen; no holdout, 70-run validation denominator,
reproducibility stage, physical command, or simulation-ready tag was executed.
Phase 08 does not establish simulation robustness readiness.

## Authoritative context and commits

- Branch: `feature/gesc-gaussian-robustness-v1`.
- V2 implementation start: clean HEAD
  `787350e38522856f6463e645714dcc512ad2a5e5`.
- Historical v1 closeout:
  `5a26638e655e136e154dc16fa13a0ee2b3c39726`.
- Phase 08a staged-v2 implementation:
  `8aab27c` (`phase 08a: add staged robustness validation v2`).
- Required preflight:
  `Phase 08 implement context is complete.`
- Historical v1 evidence remained immutable and was not counted.
- No simulation-ready tag exists.

## Implemented interfaces

The existing owners were extended; no parallel recorder, analyzer,
orchestrator, validator, controller, or physical path was created.

- Detector confirmation now owns supervisor activation through typed
  `EVENT_CONVERGENCE_CONFIRMED` events carrying the canonical eight-value
  snapshot. Continuous convergence status remains diagnostic.
- Historical six-value v1 events can use exact-timestamp status replay only;
  this compatibility path is regression input, not v2 evidence.
- Goal verification uses the minimum of per-rotation maxima over two complete
  three-second rotations. Missing first-score evidence waits within the
  existing timeout; observed invalid evidence fails safe.
- `validate_robustness` seals the v2 manifest before tuning, enforces exact
  stage order and early stops, contains the three predeclared candidates,
  verifies freeze commit/tree/input hashes, calculates all 70-run gates and
  Wilson intervals only when their denominator exists, and compares ten
  repeats without inflating that denominator.
- A retained Level C state now produces a partial validation report with
  unexecuted gates marked `NOT RUN` and a failing exit status.
- Historical v1 execution commands remain retired.

Legacy defaults, selectable legacy behavior, cost sign, units, canonical
topics, controller ownership, and physical/simulation parity were preserved.

## V2 activation evidence

Executed once, bounded by 7200 seconds:

```bash
ros2 run ros_esc validate_robustness activation \
  --operator phase08_v2 \
  --evidence-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2
```

Result: exit 1, ten retained runs, Level C early stop.

| Measure | Result |
|---|---:|
| Run count | 10/10 |
| Full integrity/lifecycle pass | 1/10 |
| Recording complete | 3/10 |
| Analysis complete | 3/10 |
| Classification pass | 1/10 |
| Cleanup pass | 10/10 |
| Controller plus ground-truth success | 1/10 |
| Valid no-collision evidence | 9/10 |
| Typed fills | 7 |
| Escape attempts | 1 |

`activation_goal_high` was the sole complete pass. Six cases failed recording
completeness when a late stale-source `FILL_CREATED` followed timeout/failsafe
and regressed typed ROS time by more than 0.150 seconds.
`activation_stalled_assist` had a separate required publisher-parameter
snapshot failure. `activation_recenter_resume` and `activation_noise_delay`
had complete recording/analysis but missed their designated lifecycle; the
noise/delay case did prove one real escape and recenter sequence.

The evidence root is
`/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2` (1.8 GiB). It contains
ten completeness documents and ten sqlite3 bags. Read-only
`PRAGMA quick_check` passed for 10/10 bags. No process contamination remained.

The sealed workflow manifest hash is
`66c17005f67dd056e41673a0754e838f5ee22a0280b0f5d649043ad3c461cd71`.

## Durable reports

- `docs/codex/gesc_gaussian/validation/phase_08_v1_failure_closeout.md`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_run_manifest.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_gate_results.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_validation_report.md`
- `docs/codex/gesc_gaussian/validation/phase_08_v2_failure_report.md`
- `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2/workflow_state/v2_activation.json`
- `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2/workflow_state/v2_failure.json`

Gate outcome:

- Gate 1 functional regression: PASS.
- Gate 2 activation: FAIL, `1/10`.
- Gates 3–14: NOT RUN.
- Wilson intervals: not applicable because the 70-run denominator did not run.
- Simulation ready: false.

## Tests and checks

- Selected-package build: `3 packages finished`.
- Phase 08a focused activation/orchestration: `91 passed, 1 skipped`.
- Pre-runtime retained functional suite: `188 passed, 2 skipped`.
- Activation-owned retained functional suite:
  `189 passed, 2 skipped in 10.44s`.
- Closure retained functional suite after partial-report coverage:
  `190 passed, 2 skipped in 11.70s`.
- Focused partial-report test file: `14 passed in 3.98s`.
- Recorded robust/legacy infrastructure smoke:
  `1 passed in 34.69s`.
- Synthetic supervisor integration: three consecutive `5 passed` runs.
- Python compilation, fatal and focused flake8, `ament_flake8`,
  `ament_pep257`, JSON/YAML/schema parsing, and `git diff --check`: passed.
- Global package result before empirical activation:
  `1040 tests, 0 errors, 836 failures, 3 skipped`.
  The inherited flake8, pep257, and `ros_esc_interfaces` lint-cmake failures
  were 36 below the documented Phase 07 baseline of 872.

Exact closure skips:

- Phase 06 recorded headless Gazebo E2E remains gated by
  `RUN_GESC_PHASE06_GAZEBO_E2E=1`; it was also run explicitly and passed.
- Phase 05 visible Gazebo recording remains gated by
  `DSIM_RUN_GAZEBO_RECORDING_TEST=1`.
- The third package-global skip is inherited copyright checking.

The tuning, freeze, holdout, unique-validation, reproducibility, and physical
tests are unexecuted by design after Gate 2 failed.

## Go/no-go and next phase

**NO-GO** for further Phase 08 v2 empirical execution, a parameter freeze,
simulation-ready tagging, or Phase 09 physical execution.

The smallest justified next work is a newly planned, bounded Phase 08.1
diagnosis using the retained activation bags and logs. It should isolate typed
event timestamp ordering, fill-design timeout/failsafe behavior,
stalled-assist publisher snapshot reliability, and the pre-verification
rotation-window boundary before proposing any correction or new evidence
budget.

Do not rerun or relabel these activation runs, weaken the gates, resume v1,
start tuning from this failed state, or treat infrastructure completeness as
behavioral success.

No physical hardware was run.

Recommended closure commit:

```text
phase 08: close failed v2 activation gate
```
