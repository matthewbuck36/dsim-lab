# Phase 08.4 Handoff

## Terminal disposition

**PHASE 08.4 / V4 CLOSED — FAILED CORRECTED GUI ACTIVATION; NOT
SIMULATION-READY.**

V4 repaired the recorder and scenario-runner shutdown path, packaged and
qualified a fresh workflow, and executed actual visible-Gazebo simulation.
The corrected activation then stopped after its first case because the robot
reached the aggregate optimum directly instead of exercising that slot's
predeclared fill, repulsive-escape, recenter, and second-verification
lifecycle.

That run was a safe controller and simulation-ground-truth success, but it was
a valid activation-contract failure. Its declared escape metrics were
unavailable because there was no escape attempt. The binding V4.1 rule closes
V4 before headless development; no gate was weakened and the run was not
rerun.

## Authority and Git lineage

- Branch: `feature/gesc-gaussian-robustness-v1`.
- V4 commits before terminal closeout:
  - `70d9cdc` — open fresh V4 acceptance;
  - `43a27b6` — make recorder shutdown signal-safe;
  - `de254b5` — precommit fresh V4 workflow;
  - `7689f2f` — fix transactional prepare publish;
  - `90b8c74` — qualify fresh V4 execution;
  - `e9c6369` — restart activation after runner fix;
  - `54559da` — package corrected activation suite;
  - `58e963e` — qualify corrected activation.
- Active plans:
  [Phase 08.4 Plan](../plans/phase_08_4_plan.md) and
  [Phase 08.4.1 amendment](../plans/phase_08_4_1_plan.md).
- Live record: [Phase 08 status](../status/phase_08_status.md).
- No tag was created or moved.
- No physical hardware or Phase 09 action occurred.

## Implemented V4 corrections

The existing recorder now guarantees signal-safe cleanup and final evidence
publication. The existing scenario runner gives a graceful activation
boundary a separate bounded recorder-finalization allowance, immediately
cleans retained nested-session survivors after the leader exits, and scopes
named activation evidence to the causal transition into its anchor. Wall
timeouts and exception paths retain immediate escalation.

The V4 workflow adds fresh activation/development/candidate identities,
transactional root preparation, population-adoption proof, installed-resource
qualification, stage ordering, immutable progress and state records, and
bounded CLI stages. It reuses the existing controller, supervisor, fill,
recorder, analyzer, launch graph, and scenario runner.

Compatibility, controller ownership, canonical topics, cost sign and units,
final-zero behavior, and shared simulation/physical algorithm logic were
preserved.

Focused and retained source gates passed:

```text
runner/workflow/recorder focused gate
  279 passed, 1 skipped

corrected-root functional qualification
  491 passed, 2 skipped in 89.20 s

post-activation retained functional gate
  491 passed, 2 skipped in 90.28 s
```

The skips are explicit opt-in Gazebo integration tests; the actual activation
was run separately through the workflow.

## Preserved failed roots

The following roots are immutable and must not be resumed, relabelled,
overwritten, or counted:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4
  original activation: 2 executed, 8 not run
  case 1 passed
  case 2 reached its behavioral branch but recorder finalization was killed
  by the then-shared 30-second outer grace

/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2
  corrected prelaunch qualification: failed installed-resource packaging
  0 Gazebo cases

/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2b
  corrected pass-eligible root: qualification passed
  corrected activation: 1 executed, 9 not run
```

The original V4 failure isolated the bounded finalization and evidence-scope
defects. Those defects were corrected and proven without modifying the
historical evidence.

## Corrected-root qualification

`phase08_v4r2b` prepared at clean implementation commit `54559da` with:

- exact formal suite SHA-256
  `d733ef9dffb372d2c60b57f83c2b96e1062a0a62818587de59a0166df4efe88e`;
- five prior records inspected and zero formal-population overlap;
- runtime-input SHA-256
  `4eb7ad904b5c9713ac1f27f369543d4abc23d498c502b247598bf1ce40164979`;
- complete functional, isolated-build, installed-resource, entrypoint,
  boundary-smoke, launch, graph-instantiation, dry-run, disk, and empty-process
  gates.

Retained workflow-state file SHA-256 values:

```text
v4_prepare.json
  63cc8834fd5ea8aa9ab97606ba68faa04ac4e54aa7a97985c4c502a2b69ee21c
v4_qualification.json
  bdf0646aedc7888c44cbda90d528836c856936704e1fa909c0bbd883ffb745c9
```

## Corrected visible-Gazebo activation result

Executed case:

```text
v4r2a_goal_aggregate_robust
seed 10601
case key 7fe7f614dc6efadffc37a2b8003ead458260311f6b4cc249848219fa0286b58e
```

Observed behavior:

```text
SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD
controller goal: passed
aggregate-field ground truth: passed
nearest aggregate target distance: 0.096979 m
collision: false
recording: complete
cleanup: complete
final zero/readiness/integrity checks: passed
fills: 0
escape attempts: 0
```

Predeclared lifecycle responsibility:

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

Because the observed direct goal omitted the required fill/escape/recenter
branch, `required_state_path` and `required_events` failed. The declared
escape-attempt, escape-duration, and orbit metrics were consequently
unavailable, so analysis remained partial. This is a behavioral reachability
miss for the activation responsibility, not a recorder, cleanup, collision,
or Gazebo infrastructure failure.

Retained hashes:

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

All nine remaining activation slots are `not_run`. No corrected-root
replacement was eligible or attempted because readiness, motion, and a valid
terminal behavior were observed.

## Terminal counts

For the corrected pass-eligible V4 workflow:

- actual Gazebo runs: `1/120`;
- activation: `1 executed`, `9 not_run`, `0 skipped/replaced`;
- development: `0 executed`, `30 not_run`;
- holdout: `0 executed`, `20 not_run`;
- validation: `0 executed`, `50 not_run`;
- reproducibility: `0 executed`, `10 not_run`;
- formal unique denominator entered: `0/70`;
- formal repeats entered: `0/10`.

The two original V4 activation attempts and the zero-run packaging root are
historical failed evidence and do not enter these counts.

## Terminal artifacts and reporting erratum

The required terminal gate JSON, run manifest, validation report, and failure
report were generated. Their hashes are:

```text
phase_08_v4_gate_results.json
  e083acc4cb852e418a8d855a9189286bbb09b8081c25aa3fdd2a4eda15b7261a
phase_08_v4_run_manifest.json
  b852398edc77f2cf03d699637e6b1e72243644a1263880318ef8181ce5764083
phase_08_v4_validation_report.md
  8f98b9769f0c493c842b1b43a3908c581e31edd85420f91c376ed04142b9d39a
phase_08_v4_failure_report.md
  0f96f59cd70cce4dd848701540d9933035186731b42b7b341d2238f8d7952d84
```

The generic terminal engine labels missing-stage diagnostics as `v3` and
expects a legacy prepare transaction field that the validated V4
population-adoption prepare state does not use. The generated artifacts are
retained unchanged; the
[terminal report erratum](../validation/phase_08_v4_terminal_report_erratum.md)
records why those two diagnostics do not overturn the independently proven
prepare/qualification passes or alter the failed activation outcome.

## Scientific interpretation and next step

V4 did run real Gazebo and proved that the selected controller can safely
reach the aggregate optimum for this seed. It did not prove the robustness
mechanism because the first activation slot did not enter the branch it was
assigned to exercise.

The next scientifically valid route is a separately reviewed V5 design that
predeclares branch-forcing activation geometries independently of observed V4
outcomes, or makes the activation responsibility explicitly accept either
direct safe goal or a fully valid recovery path while retaining separate
cases that must exercise fill/escape/recenter. That decision must be made
before any fresh V5 evidence is observed.

Do not resume V4, rerun this valid failure, enter the V4 headless development
stage, modify the formal population, create a readiness tag, start Phase 09,
or run physical hardware.

## Git closeout

The terminal documentation/checkpoint commit follows this handoff. The final
closeout must report that commit and the exact Git status.
