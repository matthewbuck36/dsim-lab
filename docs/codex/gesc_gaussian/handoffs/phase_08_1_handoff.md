# Phase 08.1 Handoff

## Terminal disposition

**PHASE 08.1 COMPLETE — DIAGNOSTIC RECOVERY CLOSED; NO-GO FOR V3 ACCEPTANCE,
SIMULATION-READY TAGGING, PHASE 09, OR PHYSICAL WORK.**

Phase 08.1 completed the approved seven-milestone engineering recovery. It
corrected the five retained v2 activation defects, proved the calibrated goal
path in one fresh development run, and proved the fill/create plus
pure-repulsion escape activation prefix in a second run. The second run then
failed its full global contract when the provisional recenter policy orbited
until timeout and entered `FAILSAFE`.

This is a successful closeout of a bounded diagnostic phase, not simulation
robustness acceptance. Phase 08 remains not simulation-ready. No parameter
freeze, v3 tuning, holdout, unique validation denominator, reproducibility
stage, simulation-ready tag, Phase 09 work, or physical motion is authorized
or claimed.

## Authority and historical boundary

- Branch: `feature/gesc-gaussian-robustness-v1`.
- Phase 08.1 base: closed v2 commit `2d796dd`.
- M1–M6 commits:
  - `88634d6` — `phase 08.1: diagnose activation and unblock recovery`
  - `e2bdc83` — `phase 08.1: bound Gaussian fill synchronization`
  - `59a519f` — `phase 08.1: reset verification rotation evidence`
  - `2b3afb6` — `phase 08.1: harden simulation readiness evidence`
  - `8ca59d1` — `phase 08.1: bind diagnostic activation contracts`
  - `c959ce1` — `phase 08.1: retain minimal runtime probes`
- Historical Phase 08 v1 and v2 evidence remains immutable. No run was
  resumed, overwritten, relabeled, or counted toward Phase 08.1.
- The v2 activation YAML remained unchanged at SHA-256
  `a5e91d2132b3dacccedc24aba13bdacd9ef5ba4ec7c8ae7b69ced6eadaf47d72`.
- No simulation-ready tag exists.

The current checkout, tests, this handoff, the Phase 08/08.1 Plans, live
status, and retained M6 artifacts are authoritative. The M6 runs were
development diagnostics and never entered an acceptance denominator.

Related durable artifacts:

- [historical Phase 08 v2 handoff](phase_08_handoff.md)
- [Phase 08.1 Plan](../plans/phase_08_1_plan.md)
- [Phase 08.1 activation contract](../validation/phase_08_1_activation_contract.md)
- [Phase 08 live status](../status/phase_08_status.md)

## Completed objective

### M1 — durable diagnosis and workflow correction

- Audited all 58 implementation-package files, all 37 then-current
  `docs/` files, source material, current code, Git history, v2 reports, and
  retained artifacts.
- Separated direct research requirements from tentative policies. In
  particular, pure-repulsion-first, automatic recenter, one redesign, and
  their exact thresholds remain testable policies.
- Removed process-only hard limits that were blocking useful work: mandatory
  fresh chats, verbatim Plan copying, all-history rereads, blanket dirty-tree
  and unavailable-test stops, arbitrary file-count limits, and the rule that a
  failed experiment version forbids a new diagnostic version.
- Preserved the substantive gates: no hardware, cost sign/units, public
  ownership, shared simulation/physical algorithm logic, final zero,
  retained failed evidence, fixed holdouts after freeze, and no readiness tag
  without a complete acceptance pass.

### M2 — bounded fill synchronization

- Limited synchronization to samples that can enter the estimator window and
  replaced repeated full-set sorting with deterministic efficient one-to-one
  matching while preserving the existing tie semantics.
- Added request snapshot counts, candidate counts, and measured design wall
  duration to the existing event owner.
- Kept `fill_design_timeout_sec=5.0`; the fix removed avoidable work instead of
  weakening the timeout.

### M3 — post-entry verification evidence

- Reset rotation evidence on the actual transition into
  `VERIFY_EXTREMUM`; SEARCH-era maxima can no longer classify the extremum.
- Changed the robust verification default from `10.0` to `12.0` seconds so two
  3-second rotations plus a 3-second dwell have a 3-second margin.
- Kept explicitly declared safe-timeout diagnostic cases possible rather than
  globally rejecting every timing-insufficient configuration.

### M4 — readiness and evidence semantics

- Extended the existing recorder, controller, validator, launch graph, and
  topic manifest; no parallel readiness owner was created.
- Simulation readiness now requires two fresh operational epochs around
  bounded parameter capture, active Gazebo controllers, the actual
  pose/source/filter/timekeeper/state/command heartbeats, a clean robust
  `SEARCH` lifecycle, a pre-ready zero command, and one final authorization.
- Delayed-input metadata, relay state, canonical target arguments, actual
  consumer routes, required bag streams, graph types, and singleton publishers
  must agree. Physical mode is code-enforced not to inherit Gazebo controller
  checks.
- Typed event timestamp regression is checked per established producer;
  emission freshness and exact fill request/result source causality are
  separate checks.
- Evidence is strict JSON. Corrupt nonfinite values become `null` only with an
  explicit failed check.
- Gaussian-fill mutable callbacks are serialized in one callback group while a
  two-thread executor continues servicing `/clock`.

### M5 — diagnostic scenario contracts

- Added a separate schema-v3 development suite; historical v2 YAML was not
  edited.
- Bound contracts to case identity, the first contiguous
  `VERIFY_EXTREMUM` path, typed state values, selected required/forbidden
  predicates, terminal state, and rotation/dwell timing.
- Replaced unreachable isolated 450/800-input `GOAL_HOLD` expectations with
  explicit below-target classifications and kept one calibrated 2500-input
  goal case.
- Kept controller goal and simulation ground truth independent.
- Recorded that future multi-source ground truth must derive from the realized
  aggregate field or a justified dominant target.

### M6 — two retained runtime probes

Both probes ran serially, headlessly, for one finite 180-second scenario under
fresh root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6
```

The committed M5 suite SHA-256 was
`1e030602ecee99c2d1f563a0ae19e65b1c8e6608662e178eb52b8766edc5a9a7`.

| Probe | Bounded result | Retained conclusion |
|---|---|---|
| `activation_goal_high` | exit 0; full contract pass | `SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD`; controller and ground-truth goal, recording, analysis, collision, readiness, timestamps, cleanup, strict JSON, and final zero passed |
| `activation_fill_create` | exit 1; activation subclaim pass, full global contract fail | Correct below-target classification; typed fill in about 0.09 s; successful 8.714 s pure-repulsion escape; later `RECENTER -> FAILSAFE` at the 30 s timeout |

Probe 1 run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6/2026-07-26/20260726T060431139250Z_simulation_phase08_1_diagnostic_activation-activation_goal_high-robust_gaussian_v1-5ca0c583_860f0907
```

Raw bag SHA-256:
`9b9905db133be446039570a8d6c9897726d87e00830625326af48cdc7c9bb652`.

Probe 2 run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6/2026-07-26/20260726T061155030660Z_simulation_phase08_1_diagnostic_activation-activation_fill_create-robust_gaussian_v1-66aad7_9bba343b
```

Raw bag SHA-256:
`f10924891a97478add654d373301a76047fce9921c0fb348ecd3a1987de1122e`.

Each run was analyzed exactly once into its run-local `analysis/` directory.
Both recordings, analyzers, readiness histories, applicable typed timestamp
checks, collision checks, strict-JSON checks, cleanup, and final-zero evidence
passed. Probe 2 additionally passed the exact fill request/result causality
check; Probe 1 created no fill. No new node or session process remained.

## Remaining failure and diagnosis

Probe 2 is an honest Level C failure for its fixed whole-run contract. Its
activation prefix passed, but the global forbidden `FAILSAFE` state and
`TIMEOUT`/`FAILSAFE` events occurred later and therefore correctly failed
classification. Neither conclusion is discarded.

The failure is a bounded Level B engineering question for a future version:

- fill center: `(-0.625782, -0.056396)`;
- active fill avoidance radius: `0.608675 m`;
- room-center distance from fill center: `0.628318 m`, leaving only
  `0.019643 m` clearance;
- recenter started inside that avoidance disk, about `0.970 m` from room
  center;
- the shared selector ranked clearance before center alignment and cached a
  safe direction until it became unsafe;
- 141 direction revisions and about `2.738 m` of travel produced a best center
  distance of only `0.658224 m`, outside the `0.25 m` tolerance;
- 300 unique recenter control samples were unsaturated and measured command
  tracking was close, so neither Gazebo nor actuator tracking explains the
  orbit.

The source material says to consider returning with "some type of planning"
while retaining useful repulsion. It does not mandate the current shared
clearance-first objective. The return-to-center mechanism and exact navigation
policy are provisional.

Do not increase `recenter_max_sec` or shrink the fill avoidance radius merely
to reclassify Probe 2, remove global safety forbiddens, rerun Probe 2
unchanged, or call the activation prefix a full pass. Any future parameter
change requires separate versioned evidence.

## M7 durable-policy amendments

- `START_HERE.md` now describes bounded recenter as selectable and provisional
  and points to this closed handoff.
- The Phase 04 Plan retains the historical implemented behavior but carries a
  Phase 08.1 erratum: clearance-first is not an invariant.
- The test-matrix contract now allows explicit activation-window and
  full-lifecycle diagnostic results. The full lifecycle remains authoritative
  and safety forbiddens remain global by default.
- The topic dictionary records the current shared selector and its known
  recenter limitation without claiming the future correction is implemented.
- The implementation sequence now blocks v3/Phase 09 and points first to a
  separately planned recenter correction.

These amendments remove counterproductive hard instructions without weakening
safety, evidence integrity, compatibility, or formal acceptance.

## Interfaces, defaults, and compatibility

- No ROS message definition, canonical topic, cost sign/unit, controller owner,
  recorder owner, analyzer owner, or physical algorithm fork was added.
- Scenario schema versions 1 and 2 remain supported. Schema 3 adds
  development-only binding fields including `contract_id`, first-verification
  `required_state_path`, required/forbidden state and event evidence,
  `expected_terminal_state`, expected verification outcome, and explicit
  timing contracts.
- `verification_max_sec` changed from `10.0` to `12.0` for the robust live
  default. The unchanged `fill_design_timeout_sec=5.0`,
  `recenter_max_sec=30.0`, fill avoidance margin, and safety limits were not
  relaxed.
- The simulation topic manifest adds operational-readiness requirements and a
  `0.5 s` heartbeat staleness limit. These are recording/evidence semantics,
  not new algorithm topics.
- `algorithm_profile=legacy` remains the default and retains legacy behavior.
- Existing v1/v2 bags remain readable; no interface migration is required.

## Tests and checks

The live status records the milestone outcomes, superseded attempts, retained
artifacts, and skips. `test_commands.md` contains the exact later-phase broad
regression, build, M4-M7 validation, and M6 runtime/analysis commands. Final
authoritative highlights:

- M2 estimator regression: `21 passed`; fill/legacy regression:
  `44 passed`; final fill/legacy/observability regression: `59 passed`; bag
  analysis: `11 passed`.
- M3 state-machine/supervisor/observability/validator/legacy regression:
  `89 passed`; the six-test synthetic integration passed twice more.
- M4 final focused recorder/runner/controller regression:
  `104 passed, 1 skipped`; broad recording/analysis/state regression:
  `182 passed, 2 skipped`.
- M5 focused schema/runner regression: `64 passed, 1 skipped`; full non-linter
  package sweep: `278 passed, 2 skipped, 3 deselected`.
- M5 final isolated `ros_esc` build passed and the installed dry-run resolved
  `10` cases, `0` unsupported cases, and positive timing margin in all ten.
- M6 Probe 1: full classification/completeness/cleanup pass.
- M6 Probe 2: infrastructure/completeness/cleanup pass; activation subclaim
  pass; full behavioral classification fail.
- Normal and strict-history Phase 08 Implement context validation,
  required-document validation, Python compilation where code changed,
  relevant XML/YAML/JSON parsing, focused lint/pep257, `git diff --check`, and
  material checkpoints passed at their recorded boundaries.

The latest repository-standard package result retained before Phase 08.1 was
`1040 tests, 0 errors, 836 failures, 3 skipped`; the failures were inherited
lint/pep257/lint-cmake debt. Phase 08.1 did not rerun that whole linter matrix.
Same-configuration owner comparisons recorded no new lint finding and removed
existing findings. The passing `278`-test non-linter sweep is the latest broad
functional result.

Exact final skips:

- visible Gazebo recording test gated by
  `DSIM_RUN_GAZEBO_RECORDING_TEST=1`;
- recorded headless Gazebo E2E gated by
  `RUN_GESC_PHASE06_GAZEBO_E2E=1`;
- the three M5 deselections were repository linter markers.

The formal v3 tuning, freeze, holdout, unique validation, reproducibility,
Wilson-interval, tag, Phase 09, and physical tests were unexecuted because
Phase 08.1 did not authorize them and recenter remains unresolved.

## Exact changed-file inventory

Phase 08.1 changed these 73 tracked files relative to closed-v2 base
`2d796dd`:

```text
AGENTS.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/00_MASTER_IMPLEMENTATION_PLAN.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/04_STATE_MACHINE_SPEC.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/05_DATA_COLLECTION_AND_ROSBAG_SPEC.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/06_TEST_MATRIX_AND_ACCEPTANCE_GATES.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/README.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/00_repo_audit_IMPLEMENT.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/00_repo_audit_PLAN.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/01_observability_IMPLEMENT.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/01_observability_PLAN.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/02_state_machine_IMPLEMENT.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/02_state_machine_PLAN.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/03_gaussian_fill_IMPLEMENT.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/03_gaussian_fill_PLAN.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/04_escape_recenter_IMPLEMENT.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/04_escape_recenter_PLAN.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/05_rosbag_IMPLEMENT.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/05_rosbag_PLAN.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/06_scenario_runner_IMPLEMENT.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/06_scenario_runner_PLAN.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/07_analysis_IMPLEMENT.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/07_analysis_PLAN.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/08_validation_IMPLEMENT.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/08_validation_PLAN.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/09_physical_IMPLEMENT.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/09_physical_PLAN.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/10_documentation_IMPLEMENT.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/10_documentation_PLAN.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/README.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/source_material/CONSOLIDATED_MEETING_DECISIONS.md
DSIM_GESC_Gaussian_Codex_Implementation_Package/templates/robust_gaussian_defaults.yaml
DSIM_GESC_Gaussian_Codex_Implementation_Package/templates/scenario_example.yaml
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh
docs/codex/gesc_gaussian/checkpoints/phase_08_checkpoint.txt
docs/codex/gesc_gaussian/handoffs/phase_08_1_handoff.md
docs/codex/gesc_gaussian/implementation_sequence.md
docs/codex/gesc_gaussian/interface_map.md
docs/codex/gesc_gaussian/plans/phase_04_plan.md
docs/codex/gesc_gaussian/plans/phase_08_1_plan.md
docs/codex/gesc_gaussian/plans/phase_08_plan.md
docs/codex/gesc_gaussian/recording_runs.md
docs/codex/gesc_gaussian/repo_map.md
docs/codex/gesc_gaussian/status/phase_08_status.md
docs/codex/gesc_gaussian/test_commands.md
docs/codex/gesc_gaussian/topic_dictionary.md
docs/codex/gesc_gaussian/validation/phase_08_1_activation_contract.md
docs/codex/gesc_gaussian/validation/phase_08_v2_contract_erratum.md
ros2_ws/src/ros_esc/package.xml
ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py
ros2_ws/src/ros_esc/ros_esc/experiment_recording/record_run.py
ros2_ws/src/ros_esc/ros_esc/experiment_recording/topic_manifest.yaml
ros2_ws/src/ros_esc/ros_esc/experiment_recording/validate_run.py
ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/basin_estimator.py
ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py
ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_1_diagnostic_activation.yaml
ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py
ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py
ros2_ws/src/ros_esc/setup.py
ros2_ws/src/ros_esc/test/test_experiment_recording.py
ros2_ws/src/ros_esc/test/test_legacy_behavior.py
ros2_ws/src/ros_esc/test/test_observability_contract.py
ros2_ws/src/ros_esc/test/test_robust_gaussian_algorithm.py
ros2_ws/src/ros_esc/test/test_scenario_runner.py
ros2_ws/src/ros_esc/test/test_scenario_schema.py
ros2_ws/src/ros_esc/test/test_state_machine.py
ros2_ws/src/ros_esc/test/test_supervisor_integration.py
ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml
```

Reproduce it with `git diff --name-only 2d796dd..HEAD` after the M7 commit.
No parallel node, package, recorder, validator, analyzer, controller, or
hardware path was created.

## Smallest justified successor

Create and review a bounded Phase 08.2 diagnostic Plan before editing code.
It should:

1. Keep `select_safe_direction` clearance-first behavior unchanged for
   `ESCAPE_ASSIST`.
2. For `RECENTER`, apply the existing wall/fill rejection predicates first,
   then rank accepted candidates by greatest predicted center-distance
   reduction/alignment, clearance, minimum rotation, and deterministic
   candidate order without adding a positive-progress eligibility predicate.
   Zero or negative center progress can be necessary during mandatory outward
   recovery while starting inside a fill disk.
3. Check the actual commanded nonholonomic swept segment, not only the
   selected world-frame direction. While starting inside any active fill disk,
   forward translation must not reduce fill-center distance; after exit, no
   commanded segment may re-enter or intersect the disk, and every pose must
   remain inside the wall-margin inset. These are configured eligibility
   predicates, not a physical collision claim.
4. Add deterministic geometry and closed-loop kinematic regression seeded from
   the retained Probe 2 geometry: pose
   `(-0.922899286, 0.299448541)`, yaw `-0.395048403 rad`; fill center
   `(-0.625781953, -0.056395888)`, avoidance radius `0.608674749 m`; room
   center `(0, 0)`; bounds `[-2, 2] x [-2, 2]`; wall margin `0.35 m`;
   lookahead `0.5 m`; and candidate step `pi/4`. Use the existing recenter
   gains, caps, tolerance, and hold with deterministic `dt=0.1 s` explicit
   Euler: select and compute the command at the current state, update `x,y`
   using the current yaw, then update and wrap yaw. Require center tolerance
   plus the existing 1-second hold within the unchanged 30-second runtime
   bound, with a justified deterministic margin selected in the successor
   Plan, the configured wall/fill eligibility predicates, bounded commands,
   and no change to escape-assist selection. Extend
   `test_escape_recenter.py` and `test_supervisor_integration.py`; retain the
   state-machine timeout, legacy arbitration, and observability regressions.
5. Continue reporting the activation prefix and full lifecycle separately.
   Add machine-readable named scopes only if a later diagnostic needs to
   evaluate both automatically; this is not a prerequisite for the recenter
   correction, and the current global default remains authoritative.
6. After code, focused regression, isolated build, dry run, and cleanup checks
   pass at a clean commit, predeclare one initial recenter-specific development
   probe under a new evidence root. Any further probe requires a separately
   declared distinct unresolved question. Preserve Probe 2 as failed evidence;
   it is not replaced.
7. A v3 design may be planned separately, but do not execute tuning, freeze,
   holdout, or acceptance until the recenter question is closed by passing
   evidence or a separately reviewed policy change. Any v3 acceptance Plan
   must still declare tuning ranges, a sealed contract, aggregate-field ground
   truth, selection-blind holdouts, a unique denominator, and repeats.

This successor reuses
`ros_esc/supervisor_node/escape_recenter.py`,
`supervisor_node_script.py`, the existing state/runner/recorder/analyzer
owners, and their focused tests. It does not need a new node, message, topic,
package, or dependency.

## Exact next prompt

Use:

```text
/goal Read and execute:

DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/08_validation_PLAN.md

Treat the repository, Phase 08/08.1 Plans, phase_08_status.md,
phase_08_handoff.md, phase_08_1_handoff.md, retained M6 artifacts, and current
Git state as authoritative. Plan only a bounded Phase 08.2 recenter recovery
using the smallest justified successor in the Phase 08.1 handoff. Preserve all
v1, v2, and Phase 08.1 evidence. Do not authorize v3 acceptance, Phase 09, a
simulation-ready tag, or physical hardware.

Save the reviewed successor Plan as:
docs/codex/gesc_gaussian/plans/phase_08_2_plan.md
```

## Git and recommended closeout commit

At M7 authoring start, M6 was cleanly committed at `c959ce1` and the branch was
nine commits ahead of its upstream. The M7 documentation/checkpoint diff must
be validated and committed before treating this handoff as the final Git
boundary.

Recommended M7 commit:

```text
phase 08.1: close mixed diagnostic recovery
```
