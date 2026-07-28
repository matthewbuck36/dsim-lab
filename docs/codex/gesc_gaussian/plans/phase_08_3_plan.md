# Phase 08.3 Plan — Fresh v3 Robustness Acceptance

Target path:
`docs/codex/gesc_gaussian/plans/phase_08_3_plan.md`

## Status, authority, and planning boundary

This is the authorized, decision-complete Plan for a new Phase 08 v3
robustness-acceptance experiment. It does not authorize v1 or v2 resumption,
runtime execution in this Plan chat, physical hardware, Phase 09, or a
simulation-ready claim before every v3 gate passes.

Planning preflight passed on 2026-07-27:

```text
Phase 08 plan context is complete.
```

Verified planning state:

- branch: `feature/gesc-gaussian-robustness-v1`;
- planning HEAD: `bc4b420d`
  (`phase 08.2: retain passing recenter recovery`);
- worktree before this Plan: clean and 15 commits ahead of
  `origin/feature/gesc-gaussian-robustness-v1`;
- active historical status: `COMPLETE — PHASE 08.2 RECENTER RECOVERY
  VALIDATED; NO V3 ACCEPTANCE`;
- current retained broad functional baseline:
  `289 passed, 2 skipped, 3 deselected`;
- current retained focused Phase 08.2 source/state baseline: `112 passed`;
- most recent repository-standard global baseline:
  `1040 tests, 0 errors, 836 inherited failures, 3 skipped`;
- no simulation-ready tag exists;
- `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3` does not exist;
- available disk at planning time: approximately `327 GiB`.

This Plan was based on current source, tests, scenario schema, launch and
offline command owners, the closed Phase 08 status, the Phase 07/07.5 and
08/08.1/08.2 handoffs, v2 reports and gate artifacts, retained-evidence
summaries, package specifications, and current Git state. Current code, tests,
resolved interfaces, and future observed evidence remain authoritative.

Historical evidence is immutable and excluded:

| Evidence | Disposition |
|---|---|
| v1 root `/home/mattb/Experiments/GESC-Gaussian/runs/phase08` | failed historical evidence; never resume, overwrite, relabel, or count |
| v2 root `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2` | ten activation attempts; Gate 2 failed `1/10`; later 110 planned runs did not execute |
| Phase 08.1 root `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6` | two development probes; not acceptance |
| Phase 08.2 root `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_2_recenter` | one passing recenter development probe; not acceptance |

Relevant immutable source hashes at planning time:

```text
historical v2 activation YAML
  a5e91d2132b3dacccedc24aba13bdacd9ef5ba4ec7c8ae7b69ced6eadaf47d72
Phase 08.1 diagnostic suite
  1e030602ecee99c2d1f563a0ae19e65b1c8e6608662e178eb52b8766edc5a9a7
Phase 08.2 recenter suite
  1b116ef7984d8a679f69da919576125a1ad066da3d55098466da9afac2bae017
Phase 08.1 handoff
  cdd9ebd2c0649eb8d8e6fa603695aad4afab0c3147d6522ceefd7c615f00a7c2
Phase 08.2 handoff
  7f97d6bed7e8a28eccdd60298a52c1cdcd8b94cca70038d91f2b6007d3a05261
closed Phase 08 status
  2ec7af29796b599bce8a49a27e28e2ec706cc79e2b889414ab40ab45565cc075
```

## Amendment A1 — fixed cleartext acceptance population

Authorized by the user on 2026-07-27 before M2 and before any v3 suite was
generated or any v3 Gazebo simulation ran.

This amendment removes the GPG/encryption and selection-blindness requirement.
`v3-prepare` instead generates the complete 70 unique cases plus ten repeat
references before activation, serializes them canonically to the tracked
cleartext file
`phase08_v3_acceptance_suite.json`, and binds that exact file through SHA-256,
the commitment document, the M2 checkpoint/commit, the later freeze, and the
sealed acceptance contract. The case allocation, generator, historical
exclusion, aggregate qualification, thresholds, denominators, candidate
selection, stage order, replacement limits, early-stop rules, and behavioral,
safety, evidence, completeness, collision, cleanup, final-zero, timestamp, and
causality gates are unchanged.

The scientific claim is correspondingly narrowed: v3 is a predeclared,
researcher-visible evaluation, not a selection-blind evaluation. The suite may
not be edited or regenerated after its M2 commitment, and development outcomes
may not be used to change its cases, partition, or repeats. Every later
reference in this Plan to GPG, a recipient fingerprint, ciphertext,
decryption, hidden or unexposed identities, an encrypted envelope, or
selection-blindness is superseded by this amendment. Operational paths,
commands, milestones, and stop conditions below are updated to match.

## Objective, success claim, and non-claims

### Objective

Using the corrected Phase 08.2 implementation, select one bounded parameter
bundle from fresh development evidence, freeze one implementation/profile and
one precommitted scenario population, then evaluate that fixed system over a
new predeclared holdout, a fixed additional unique validation sample, and
predeclared repeats.

### Permitted success claim

If and only if every gate in this Plan passes, the supported claim is:

> One fixed `robust_gaussian_v1` implementation and parameter profile met the
> sealed v3 behavioral, evidence-integrity, safety, completeness, collision,
> cleanup, timing, causality, and reproducibility gates over the declared
> bounded family of simulator-relative multi-light fields, starts, headings,
> noise, delays, boundaries, saturation conditions, and lifecycle cases.

The claim is a stratified empirical result for the sealed v3 sample. It is not
a proof for arbitrary nonconvex functions or untested environments.

### Explicit non-claims

V3 does not establish:

- correctness or optimality of v1, v2, Phase 08.1, or Phase 08.2 evidence;
- universal convergence;
- absolute photometric/lux calibration;
- physical TurtleBot, Vicon, lamp, or emergency-stop readiness;
- acoustic-source behavior;
- Heavy-Ball ESC behavior;
- validity outside the sealed source counts, intensities, geometries,
  disturbances, starts, constraints, and runtime limits;
- selection-blind, blinded, or independently administered evaluation;
- Phase 09 authorization.

## Run-allocation decision

The fresh 120-declared-run structure is retained:

| Stage | Declared runs | Acceptance denominator? |
|---|---:|---|
| Fresh activation | 10 | No; mandatory pre-tuning gate |
| Bounded development/tuning | 30 = 3 candidates × 10 common cases | No; selection only |
| Fresh predeclared researcher-visible holdout | 20 | Yes |
| Additional unique validation | 50 | Yes |
| Targeted reproducibility repeats | 10 | No; separate reproducibility gate |
| **Total** | **120** | **70 unique acceptance cases** |

This retains the user's preferred total because the repository now supports
serial deterministic execution, collision truth, disturbance truth, complete
recording, offline analysis, lifecycle contracts, and a corrected full
recenter path. No repository evidence justifies reducing the six-family
70-case denominator or the ten repeats.

It is not a mechanical copy of v2:

1. v3 uses new schema-v4 contracts and new identities, seeds, starts, and
   geometries.
2. V3 derives goal truth from the realized aggregate field. A source
   `evaluation_role` never establishes the target.
3. Every acceptance case is prequalified to have a threshold-reachable
   aggregate target; deliberately doomed safe-timeout behavior is tested in
   activation, not spent as a known failure inside the 70-case goal
   denominator.
4. V3 seals one machine-readable contract with exact thresholds,
   denominators, N/A rules, hashes, and replacement limits.
5. V3 precommits the full researcher-visible 70-case population and ten repeat
   references before activation. Their canonical file and SHA-256 are fixed at
   M2 and cannot change after development.
6. V3 evaluates per-attempt escape durations/orbits instead of relying only on
   one run-level aggregate.
7. V3 fixes the v2 not-run representation: `outcome: "not_run"` and
   `passed: null`.

The 120 declared slots do not include objectively pre-readiness invalid
replacement attempts. Every attempt is retained and reported; the bounded
replacement caps below prevent an unbounded empirical budget.

## Repository findings and existing owners

### Corrected implementation to reuse unchanged

The v3 starting implementation is the current Phase 08.2 code:

- `ros_esc/supervisor_node/state_machine.py` owns the eight-state policy,
  post-entry rotation evidence, fill timeout, escape deadline, and recenter
  timeout.
- `ros_esc/supervisor_node/escape_recenter.py` owns frozen escape geometry,
  measured radial progress, unchanged `ESCAPE_ASSIST` selection, recenter-only
  target-progress ranking, wall/fill eligibility, and actual-command sweep
  suppression.
- `ros_esc/supervisor_node/supervisor_node_script.py` owns state, escape,
  assist, recenter, and stop policy.
- `ros_esc/gaussian_fill_node/` owns bounded synchronized basin estimation,
  fill design, merging, revisions, and typed fill publication.
- `ros_esc/modified_cost_node/`, `filter_node/`, and `controller_node/` retain
  cost composition, GESC filtering, and sole `/cmd_vel` ownership.
- `turtlebot3_rotating_sensor/launch/gazebo.launch.xml` remains the central
  simulation graph.

No v3 algorithm-source change is presently required before activation. A
failed pre-activation test or aggregate-field qualification is not permission
to change the controller silently; it stops the milestone for a documented
Plan review.

### Existing infrastructure to extend

- `scenario_schema.py` is the sole scenario-schema and deterministic identity
  owner. It supports versions 1–3 but schema 3 still uses manually named goal
  source IDs.
- `run_scenario.py` is the sole serial scenario orchestrator. It composes
  `record_run`, `validate_run`, `gazebo.launch.xml`, classification, and
  cleanup.
- `record_run.py` and `validate_run.py` remain the sole recorder and
  completeness validator. Their sqlite3, readiness, required-topic,
  parameter-snapshot, timestamp, causality, final-readiness, final-zero, and
  shutdown contracts are retained.
- `gesc_gaussian_bag_analysis.py` is the sole bag analyzer. It already writes
  per-attempt `escape_attempts.csv`, but its run summary collapses escape time
  and retains manually named source ground truth.
- `phase08_validation.py` is the sole Phase 08 workflow owner. It can read v1
  and v2 evidence, seal v2 manifests, calculate Wilson intervals, and enforce
  stage order, but its constants, gates, thresholds, and CLI are v2-specific.
- `simulation_disturbance_node.py`, the validation world, contact sensors, and
  delayed topics already provide seeded noise, sensor/pose delay, collision
  evidence, and positive/negative contact support.
- The live multi-source simulator owner is
  `Multi_Light_Source_Cost`; it combines conductance contributions before
  converting to the existing negative-voltage minimization cost. V3 ground
  truth must call this owner rather than duplicate its curve.

### Current contract gaps that must close before activation

1. Phase 08 Implement context validation hardcodes
   `phase_08_2_plan.md`.
2. The closed live status must be reopened append-only for v3.
3. The checkpoint already finds the numerically latest subphase Plan, but it
   does not include a machine-readable freeze state.
4. The context bundle lists all Plans but does not designate the active v3
   Plan or current freeze/contract hashes.
5. Schema 3 and both online/offline ground-truth paths use manually assigned
   `goal_source_ids`.
6. V2 gates omit exact metric-applicability and minimum-denominator rules.
7. V2's workflow cannot bind a schema-v4 cleartext population and its exact
   canonical hash through prepare, freeze, contract, and terminal reporting.
8. V2 summary logic does not expose one valid scalar duration and orbit value
   per escape attempt to the acceptance evaluator.

These are bounded workflow, evidence-contract, and offline-analysis changes.
They add no node, package, message, service, action, algorithm topic, physical
adapter, or simulation/physical fork.

## Aggregate-field ground truth

### Authoritative field

For every schema-v4 development or acceptance case, construct the noise-free
field from the exact resolved source list and the installed
`multi_light_source_photoresistor.json` parameters:

```text
mode = Voltage
scale_map = 1.0
apply_adc = false
reference_intensity_lumens = 1000.0
```

Evaluate it only through the existing `Multi_Light_Source_Cost` class.
The objective is the most negative raw voltage over robot-center position and
sensor yaw:

```text
min J_raw(x, y, yaw)
```

The position domain is the configured room bounds inset by the frozen
`wall_margin_m=0.35`. The sensor-yaw domain is `[0, 2π)`.

### Deterministic target solver and qualification

The new pure helper `aggregate_field_truth.py` shall:

1. evaluate two offset three-dimensional lattices:
   - position spacing `0.10 m`, yaw spacing `5 degrees`;
   - the second lattice is offset by `0.05 m`, `0.05 m`, and `2.5 degrees`;
2. retain the best 32 distinct lattice basins from each scan;
3. refine every retained basin with bounded SciPy optimization against the
   authoritative cost owner;
4. merge refined targets within `0.05 m` and `1e-4 V`;
5. retain every global-equivalent target within `1e-4 V` of the best result;
6. require the two offset scans to agree within `1e-4 V`; disagreement rejects
   the case before sealing;
7. calculate the peak controller `source_score` at each retained target;
8. require a lower reachability bound of at least `0.95`, where the noise
   margin is:
   - zero for no-noise cases;
   - the declared voltage bound for uniform noise;
   - three declared standard deviations for Gaussian noise;
9. record the model-config hash, source-list hash, domain, lattice settings,
   optimizer settings, targets, raw costs, scores, noise margin, and solver
   result hash inside the resolved case.

The existing final-position tolerance remains `0.35 m`. Ground-truth goal
success means the terminal pose is within `0.35 m` of any global-equivalent
aggregate target. Controller success independently requires
`GOAL_REACHED` plus `GOAL_HOLD`. End-to-end success requires both.

Any solver disagreement, sub-threshold target, missing target, nonfinite
result, source/config hash drift, or unavailable terminal pose makes the case
invalid before runtime or fails the corresponding evidence gate. A source
role label is retained only as descriptive metadata and is never an
acceptance input.

### Ordered two-source level coverage

All 25 ordered level pairs remain in the 70-case sample. For each ordered
`(level_a, level_b)` pair, the sealed generator assigns the two levels to
opposite sides of a rotated pair axis. It chooses the largest separation from:

```text
[1.20, 1.00, 0.80, 0.60, 0.40, 0.25, 0.10] m
```

that passes the aggregate-target solver and the noise-adjusted `0.95`
reachability rule. The choice depends only on the fixed field model and level
pair, never on development outcomes. This preserves low/low coverage without
falsely requiring a manually labeled weak source to be a calibrated goal.
For example, the live model shows that a `450 + 450` pair needs approximately
`0.10 m` separation to cross the calibrated threshold; wider low/low
geometries are valid below-target diagnostics but not end-to-end goal cases.

## Fresh activation gate

### Common activation settings

Activation is a fresh development gate under
`phase08_v3_activation.yaml`, schema version 4:

```text
max_parallel_runs = 1
gazebo_gui = true
preflight_timeout_sec = 150.0
run_timeout_sec = 240.0
wall_timeout_sec = 600.0
shutdown_grace_sec = 30.0
stop_on_cleanup_failure = true
bounds = [-2, 2] x [-2, 2] m
wall_margin_m = 0.35
contacts = enabled
validation world = enabled
```

Seeds `9301`–`9310`, IDs, starts, and geometries are new. The qualification
step must prove that none of their normalized case keys matches any v1, v2,
Phase 08.1, or Phase 08.2 case key.

Schema v4 adds two named result scopes:

- `activation_window`: anchored at the first `VERIFY_EXTREMUM` and ending at a
  declared branch boundary;
- `full_lifecycle`: readiness through orderly shutdown.

Branch-only cases may request graceful stop after their activation boundary.
That does not hide later safety: collision, timeout/failsafe forbiddens unless
explicitly expected, completeness, cleanup, timestamps, causality, final
readiness, and final zero are always evaluated over the full lifecycle.
Acceptance cases never use branch-only termination.

### Ten cases

| ID / seed | Start and sources `(x, y, relative input)` | Required behavior |
|---|---|---|
| `v3a_goal_aggregate_direct` / `9301` | start `(-1.20,-0.80,0.35)`; goal `(1.05,0.65,2500)` | full `SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD`; two fresh rotations, dwell, controller and aggregate truth |
| `v3a_below_target_fill` / `9302` | start `(-0.85,-0.10,0)`; local `(-0.85,-0.10,700)`, goal `(1.45,1.25,2500)` | activation window through `DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE`; correlated `FILL_CREATED`, `ESCAPE_STARTED`; graceful stop |
| `v3a_pure_escape_recenter` / `9303` | start `(-0.90,0.55,0)`; local `(-0.90,0.55,700)`, goal `(1.35,-1.15,2500)` | full below-target fill, `ESCAPE_REPULSE`, `RECENTER`, `RECENTER_COMPLETE`, `SEARCH`; no assist |
| `v3a_stalled_assist` / `9304` | start `(-0.65,-0.55,0)`; local `(-0.65,-0.55,800)`, goal `(1.35,1.15,2500)` | activation window through one stall/redesign and `ESCAPE_ASSIST`; branch-only overrides `stall_window_sec=1.0`, `minimum_radial_progress_m=5.0`; graceful stop |
| `v3a_fill_merge` / `9305` | start `(-0.45,0.05,0)`; locals `(-0.45,0.05,650)`, `(0.05,0.15,700)`, goal `(1.45,1.25,2500)` | activation window through ordered `FILL_SUPERSEDED -> FILL_MERGED` and assist entry; branch-only merge/stall overrides; graceful stop |
| `v3a_full_lifecycle_goal` / `9306` | start `(-1.00,-0.30,0)`; local `(-1.00,-0.30,700)`, goal `(1.25,0.95,2500)` | full first-verification below target, fill, escape, recenter, resumed search, later aggregate goal and `GOAL_HOLD` |
| `v3a_revisit_guard` / `9307` | start `(-0.90,0.65,-0.2)`; local `(-0.90,0.65,700)`, goal `(1.25,-0.90,2500)` | full escape-to-goal with active fill, valid revisit denominator, `revisit_count=0` |
| `v3a_boundary_saturation` / `9308` | start `(-1.45,-1.25,0.7)`; local `(-1.25,-0.85,700)`, goal `(0.95,1.15,2500)` | wall/corner-safe full path, at least one saturation sample, zero non-ground contacts |
| `v3a_noise_delay` / `9309` | start `(-0.75,0.70,-0.5)`; local `(-0.75,0.70,700)`, goal `(1.15,-1.00,2500)` | full path under Gaussian `std_dev=0.01`, `0.05 s` sensor delay, and `0.05 s` pose delay; measured delays within tolerance |
| `v3a_safe_timeout` / `9310` | start `(-1.00,0.00,0)`; goal `(1.00,0.00,2500)` | explicit development-only safe-timeout contract with `verification_max_sec=8.0`; direct `VERIFY_EXTREMUM -> FAILSAFE`, ordered `TIMEOUT -> FAILSAFE`, full cleanup/final zero |

The source model was checked during planning at the local coordinates above.
The observed maximum local scores for cases 2–9 were between approximately
`0.903` and `0.946`, below the fixed `0.95` classification threshold, while
the declared 2500-input targets reached score `1.0`. The implementation-time
aggregate solver remains the binding qualification.

Activation passes only if all ten declared contracts, all full-scope safety
predicates, and the retained functional suite pass. A valid behavioral miss is
not replaced. All ten cases still run after an ordinary behavioral miss so
the lifecycle coverage diagnosis is complete; cleanup contamination,
collision where forbidden, corrupt evidence, duplicate ownership, or a
frozen-input/hash failure stops further dispatch immediately. Any activation
miss stops before development.

### Retained-evidence and runtime-probe boundary

The retained Phase 08.1/08.2 bags, completeness files, summaries, and handoffs
are the diagnosis that justifies starting from the current implementation.
They are read-only and receive no v3 score. M2 source tests, isolated build,
launch instantiation, schema resolution, aggregate qualification, and
installed dry runs are the pre-runtime smoke gate.

No additional unregistered Gazebo smoke case is allowed. The ten declared
activation cases are the only v3 runtime probes before development: cases 1,
2, and 3 provide the minimal goal/fill/full-recenter progression; the
remaining seven extend the branch and evidence envelope only after the same
serial workflow remains clean. This avoids an informal, tunable pre-sample
while still requiring bounded runtime proof before the 30-run comparison.

## Bounded 30-run development and tuning

Development is a serial batch using the same `150 s` preflight, `240 s`
scenario, `600 s` wall, `30 s` shutdown-grace, contact, validation-world,
cleanup, and evidence settings as activation. It sets `gazebo_gui=false`
because it is a repeated matrix rather than a one-off interactive probe. All
three candidates execute under that same runtime presentation.

### Ten common development cases

Each candidate executes the same ten schema-v4 cases with seeds `9401`–`9410`.
All are retained and excluded from acceptance:

| Slot | Purpose and fixed geometry |
|---|---|
| `v3d_ordered_11_close` | ordered level `(1,1)`, sources `(-0.05,0,450)` and `(0.05,0,450)`, start `(-1.30,-1.00,0.5)` |
| `v3d_ordered_25_local` | weak local `(-0.80,0,800)`, strong target `(0.90,0.40,2500)`, start at weak basin |
| `v3d_ordered_52_mirror` | strong target `(-0.90,0.40,2500)`, weak local `(0.90,-0.40,800)`, start at weak basin |
| `v3d_three_source_overlap` | locals `(-0.70,-0.30,700)`, `(0,0.20,800)`, target `(1.20,1.10,2500)` |
| `v3d_pure_escape` | local `(-0.80,0,700)`, target `(1.30,0.80,2200)`; require nominal pure-repulsion escape |
| `v3d_assist_nominal` | local `(-0.65,-0.25,800)`, target `(1.35,0.90,2200)`; require nominal stall/assist without branch-forcing overrides |
| `v3d_merge_nominal` | locals `(-0.45,0,700)`, `(0.05,0.12,750)`, target `(1.45,1.25,2500)`; require nominal merge |
| `v3d_corner_recovery` | local `(-1.15,-1.00,750)`, target `(0.90,0.90,2500)`, start `(-1.45,-1.35,0.8)` |
| `v3d_noise_delay` | local `(-0.80,0.60,700)`, target `(1.20,-0.90,2500)`, Gaussian `0.01`, sensor/pose delay `0.05 s` |
| `v3d_saturation_recenter_revisit` | local `(-0.90,-0.50,750)`, target `(1.20,1.20,2500)`, far start, saturation, recenter, and valid revisit evidence |

The exact YAML must include full starts/headings, contracts, aggregate truth,
metric applicability, and expected lifecycle. Qualification rejects any local
coordinate whose full aggregate score is not below `0.95` or any target whose
noise-adjusted score is not at least `0.95`.

### Eligible tuning factors

Only these five existing launch parameters vary:

| Factor | `V3-C0` baseline | `V3-C1` compact/patient | `V3-C2` broad/reactive |
|---|---:|---:|---:|
| `gaussian_fill_covariance_scale` | 2.5 | 2.0 | 3.0 |
| `gaussian_fill_amplitude_depth_scale` | 1.5 | 1.2 | 1.8 |
| `gaussian_fill_exit_sigma` | 2.50 | 2.25 | 2.75 |
| `stall_window_sec` | 3.0 s | 4.0 s | 2.0 s |
| `minimum_radial_progress_m` | 0.05 m | 0.03 m | 0.08 m |

These endpoints retain the bounded v2 design range because v2 never executed
tuning and therefore produced no evidence that invalidates the range.
`V3-C0` is the current profile used by the passing Phase 08.2 development
path. V3 candidate outcomes are entirely fresh; the historical v1 C8 and
unexecuted v2 candidate declarations confer no selection credit.

This is a comparison of three coherent parameter bundles, not a claim that
the 30 runs estimate independent effects for five factors.

### Parameters frozen from the start

All other code and parameters are fixed across candidates, including:

- cost sign, units, source model, score definition, and
  `goal_score_threshold=0.95`;
- two `3.0 s` post-entry score rotations;
- `goal_hold_sec=3.0`, `undesired_score_hold_sec=3.0`,
  `verification_max_sec=12.0`;
- `fill_design_timeout_sec=5.0`;
- `escape_max_sec=20.0`, `escape_exit_hold_sec=1.0`;
- all estimator windows, sample rules, kernels, covariance bounds, quadratic
  fit, validation-grid, escalation, and merge settings;
- all Phase 08.2 recenter logic and parameters:
  `30.0 s` timeout, `0.25 m` tolerance, `1.0 s` hold, gains, velocity caps,
  `0.5 m` lookahead, `π/4` candidates, `0.35 m` wall margin, `0.10 m` fill
  margin, and `0.50 s` command horizon;
- controller/filter configuration and saturation limits;
- readiness, topic, timestamp, causality, recording, collision, cleanup, and
  final-zero contracts;
- development case identities, starts, sources, disturbances, and seeds;
- acceptance-suite generator, family allocation, thresholds, and cleartext
  population commitment.

### Development eligibility and selection

An attempt is evidence-valid only when recording, analysis, required topics,
parameter capture, bag readability, cleanup, collision truth, final zero,
readiness history, timestamp/clock checks, event freshness, fill-request
causality, strict JSON, and aggregate-truth extraction are valid.

A candidate is eligible only when:

- all ten declared slots have valid evidence after permitted
  infrastructure-only replacement;
- there is no collision, orphan, outer wall timeout, corrupted bag, missing
  final zero, or unexpected failsafe;
- at least 9/10 cases pass end to end;
- every declared nominal lifecycle branch is reached;
- there are at least eight observed escape attempts and all are successful;
- all applicable delay, saturation, orbit, and revisit metrics are valid.

Among eligible candidates select lexicographically:

1. most end-to-end successes;
2. most full behavior-contract passes;
3. highest local-escape success rate;
4. highest minimum development-family end-to-end rate;
5. lowest successful-escape p95, then median;
6. lowest median per-attempt orbit count;
7. lowest revisit rate;
8. lowest median convergence time;
9. lowest median path length;
10. candidate ID (`V3-C0`, `V3-C1`, `V3-C2`).

All 30 declared slots execute unless a hard safety/evidence/cleanup stop
occurs. If no candidate is eligible, development closes v3 with a failure
report before freeze. Development attempts remain in their original paths and
never enter the 70-case or ten-repeat results.

## Precommitted, researcher-visible acceptance population

### Commitment mechanism

Before activation, `v3-prepare` shall:

1. generate a fresh 256-bit seed with Python `secrets.token_bytes(32)` and
   retain it only in process memory;
2. deterministically generate the complete 70-case population, the
   20/50 partition, and ten repeat references;
3. aggregate-field-qualify every goal and reject/re-generate any invalid case;
4. reject every normalized case key found in v1, v2, Phase 08.1, Phase 08.2,
   activation, or development inputs;
5. serialize the complete suite canonically in memory as UTF-8 JSON with
   sorted keys, separators `(",", ":")`, `ensure_ascii=false`,
   `allow_nan=false`, and schema-formatted finite numeric values;
6. calculate its SHA-256;
7. write the exact canonical cleartext suite and commitment document to the
   repository;
8. record explicitly that the population is researcher-visible and not
   selection-blind;
9. checkpoint and commit those exact bytes before activation.

Tracked pre-activation paths:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v3_acceptance_suite.json
docs/codex/gesc_gaussian/validation/
  phase_08_v3_suite_commitment.json
```

The commitment records schema/generator versions, total counts, family counts,
historical-exclusion hashes, the suite SHA-256, visibility, the explicit
`selection_blind=false` value, and the canonical-JSON SHA-256 mechanism. The
tracked suite exposes cases, starts, sources, seeds, the 20/50 partition, and
repeat references by user authorization. Their visibility does not permit
post-commit changes.

After the clean freeze, `v3-seal` verifies the same suite hash and every
qualification, then copies the exact already committed bytes with mode `0400`
under:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3/
  sealed/phase08_v3_acceptance_suite.json
```

The root and `sealed/` directory use mode `0700`; the sealed copy is an atomic
same-directory create/rename. No key, credential, decryption step, or GPG
dependency exists.

### Fixed 70-case allocation

| Acceptance family | Holdout | Additional validation | Unique total | Repeats |
|---|---:|---:|---:|---:|
| All 25 ordered two-source level pairs | 7 | 18 | 25 | 2 |
| 3/4-source, close-minimum, and overlapping fields | 3 | 6 | 9 | 2 |
| Wall and corner recovery | 2 | 6 | 8 | 1 |
| Noise and sensor/pose delay | 2 | 6 | 8 | 1 |
| Saturation and bounded constraint recovery | 2 | 6 | 8 | 1 |
| Escape, assist, merge, recenter, and revisit lifecycle | 4 | 8 | 12 | 3 |
| **Total** | **20** | **50** | **70** | **10** |

The generator templates are fixed:

- ordered pairs: all ordered `5 × 5` level combinations, with the
  aggregate-qualified separation rule above;
- multi/close/overlap: three 3-source, two 4-source, two close-minimum, and two
  overlap cases;
- boundary: one case for each wall and one for each corner;
- disturbance: two uniform-noise, two Gaussian-noise, two single-delay, and
  two combined sensor/pose-delay cases at `0.05` or `0.10 s`;
- constraints: three linear-saturation, two angular-saturation, and three
  combined-saturation/far-start recovery cases;
- lifecycle: three nominal pure-repulsion, three nominal assisted escape, two
  merge, two recenter/resume, and two post-fill revisit-evidence cases.

Every acceptance case:

- uses the one frozen profile with no scenario-specific algorithm override;
- runs serially with `gazebo_gui=false`, `preflight_timeout_sec=150.0`,
  `run_timeout_sec=240.0`, `wall_timeout_sec=600.0`,
  `shutdown_grace_sec=30.0`, and `stop_on_cleanup_failure=true`;
- is expected to terminate in `GOAL_HOLD`;
- is aggregate-target reachable;
- enables the validation world and contacts;
- binds full-lifecycle required and forbidden states/events;
- declares metric applicability and a family bucket;
- contributes exactly once to the 70-run end-to-end denominator.

Starts use a generator-fixed balanced schedule over five positions, four
heading quadrants, source-layout rotations, and fresh random seeds. The
20/50 split is sampled before activation subject only to the fixed family
counts. It cannot be changed after observing development.

### Reproducibility references

The precommitted suite preselects:

- two ordered-pair references;
- two multi/close/overlap references;
- one boundary reference;
- one disturbance reference;
- one constraint reference;
- three lifecycle references.

Each repeat has the same resolved sources, start, heading, disturbances,
profile, seed, aggregate truth, and contract as its unique reference, but a
new run ID. Repeats never enter the 70-case success numerator or denominator.

## Freeze and acceptance contract

### Clean implementation/profile/scenario freeze

After development selects one eligible candidate:

1. generate `phase08_v3_frozen_parameters.yaml`;
2. generate `phase_08_v3_parameter_selection.json`;
3. verify the cleartext acceptance suite and commitment are byte-identical to
   their pre-activation forms;
4. run the complete qualification/test/build/dry-run gate;
5. update and checkpoint the live status;
6. create the one implementation/parameter/scenario freeze commit only when a
   future Implement chat explicitly authorizes commits;
7. require a clean worktree before binding the acceptance suite into the
   contract.

The freeze identity includes:

- exact implementation commit and tree;
- frozen parameter file and canonical override hash;
- activation/development/candidate YAML hashes;
- cleartext acceptance-suite and commitment hashes;
- generator, schema, runner, validator, analyzer, cost-model config, launch,
  supervisor, fill, filter, controller, topic-manifest, and package hashes;
- installed package build provenance;
- historical-exclusion hashes.

Post-freeze evidence-only commits may change only the live status, checkpoint,
v3 contract/manifest/results/reports, handoff, and final navigation docs. The
v3 workflow compares every runtime input to the freeze and refuses any drift.
The worktree must be clean before each empirical stage.

### One machine-readable contract

After freeze and suite verification, generate:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3/sealed/
  phase_08_v3_acceptance_contract.json
docs/codex/gesc_gaussian/validation/
  phase_08_v3_acceptance_contract.json
```

The two files must be byte-identical. The contract contains:

- experiment and schema versions;
- freeze commit/tree and every frozen input hash;
- precommitted-suite and sealed-copy hashes;
- exact 70 identities, 20/50 partition, and ten repeat mappings;
- aggregate-field truth records and hashes;
- family allocations and metric-applicability sets;
- all thresholds and exact integer family floors;
- minimum denominators;
- replacement caps;
- early-stop rules;
- pass/fail/N/A/not-run semantics;
- evidence-root and output paths;
- proposed tag name.

The contract hash is:

```text
SHA256(canonical JSON with the top-level contract_sha256 field omitted)
```

The resulting value is inserted as `contract_sha256` and recomputed with the
same omission rule. That hash must appear in the run manifest, every stage
state, frozen snapshot, gate JSON, Markdown report, failure report if any, and
handoff.

Create and maintain:

```text
docs/codex/gesc_gaussian/validation/phase_08_v3_freeze_state.json
```

It records immutable freeze fields plus the current stage, contract hash,
execution commit, and permitted evidence-only commits. Checkpoint and context
bundle tools consume this file.

## Exact outcome semantics and denominators

### Status values

- `passed`: the declared predicate was applicable, evidence-valid, and true.
- `failed`: applicable evidence was valid and the predicate was false.
- `not_applicable`: the contract declared the metric irrelevant before
  execution, such as escape time in a direct-goal case. It never becomes a
  numeric zero.
- `unavailable`: applicable evidence could not be extracted. This fails run
  integrity and cannot be excluded from a denominator.
- `infrastructure_invalid`: the attempt failed objectively before readiness
  authorization, had no motion or robust lifecycle advance, and therefore has
  no behavioral outcome. It remains retained and may receive only the
  identical bounded replacement below.
- `not_run`: a later stage was prohibited by an earlier gate. Gate JSON uses
  `outcome: "not_run"` and `passed: null`.

No valid behavioral timeout, failsafe, collision, recording failure after
readiness, analysis failure, missing cleanup, or contract miss is
infrastructure-invalid.

### Fixed denominators

- end-to-end success: exactly 70 unique cases; minimum `63/70`;
- family end-to-end floors:
  - ordered pair: at least `20/25`;
  - multi/close/overlap: at least `8/9`;
  - wall/corner: at least `7/8`;
  - noise/delay: at least `7/8`;
  - constraint recovery: at least `7/8`;
  - lifecycle: at least `10/12`;
- designated escape cases: exactly 39 predeclared cases:
  `8 + 6 + 5 + 5 + 3 + 12` across the six families;
- local-escape rate: all observed valid escape attempts in the 39 designated
  cases, with at least 39 attempts and at least 95% success. Missing the
  designated attempt is a lifecycle failure. With 39 attempts, at most one
  failure can pass;
- escape-time statistics: one valid duration per successful attempt, minimum
  38 successful durations;
- orbit statistics: one valid orbit value per successful designated attempt,
  minimum 38;
- revisit rate: all successful end-to-end runs predeclared as post-fill
  revisit-applicable, minimum 24 valid runs; zero denominator fails rather
  than becoming N/A;
- collision, completeness, cleanup, final-zero, timestamp, causality,
  frozen-hash, and infrastructure integrity: all 70 unique cases and all ten
  repeats;
- reproducibility: exactly ten predeclared pairs.

If a case produces more than one escape attempt, every observed attempt enters
the escape rate and duration/orbit evidence; attempts are never selectively
dropped.

## Acceptance gates

All gates are conjunctive:

1. **Context and qualification:** active v3 Plan/status/freeze state agree;
   functional tests, isolated build, launch instantiation, schema
   qualification, historical exclusion, cleartext suite/commitment hash
   checks, and dry runs pass.
2. **Activation:** all ten fresh activation contracts pass.
3. **Development/freeze:** one eligible candidate is selected by the frozen
   lexicographic rule; freeze and contract hashes are valid and immutable.
4. **Holdout early gate:** all 20 slots are evidence-valid; at least `18/20`
   end-to-end successes; exact family floors are `6/7`, `3/3`, `2/2`, `2/2`,
   `2/2`, and `4/4`; all designated lifecycle predicates pass; no unexpected
   timeout/failsafe or collision.
5. **Completeness and analysis:** all 70 unique cases and ten repeats have
   `validate_run` pass, `analysis_status=complete`, readable sqlite3 bags,
   required files, and unchanged raw-bag hashes.
6. **Infrastructure and ownership:** all runs have one canonical controller,
   required singleton publishers/subscriptions/types, active readiness
   barriers, captured required publisher parameters, no pre-ready motion or
   lifecycle, clean session cleanup, no orphan, and no outer wall timeout.
7. **Final zero and shutdown:** all three final-command representations are
   zero after the shutdown boundary; final readiness is false; stop and bag/
   target process shutdown metadata pass.
8. **Timestamp and causality:** simulation clock monotonic; timestamp
   tolerance finite; typed streams nonregressing and within clock;
   `AlgorithmEvent` producer identified and emission fresh; exact fill
   request/result source causality; event value/name pairs valid; strict JSON
   finite.
9. **Collision:** contact evidence valid in all 80 formal acceptance/repeat
   runs and zero non-ground contacts.
10. **Behavior contracts:** all 70 unique cases satisfy their full-lifecycle
    required path/events, terminal `GOAL_HOLD`, aggregate truth, forbidden
    states/events, and metric applicability.
11. **End-to-end:** at least `63/70`.
12. **Per-family:** the exact integer floors above.
13. **Local escape:** at least 95% over at least 39 observed attempts, with
    every designated case exercising the branch.
14. **Escape time:** median at most `20.0 s`; p95 at most `45.0 s`; at least
    38 valid successful-attempt durations.
15. **Orbit count:** median at most `1.5` across at least 38 valid successful
    attempts.
16. **Revisit:** fewer than 5% of at least 24 valid post-fill successful goal
    runs have `revisit_count > 0`.
17. **Lifecycle coverage:** across the 70, at least 39 fill/repulse cases, six
    assist cases, four merge cases, 38 successful recenter completions, and 24
    valid revisit-applicable runs meet their exact contracts.
18. **Disturbance and constraint evidence:** every delayed case has measured
    raw/source/pose delay within `±0.02 s` of the declared delay; every
    saturation-designated case has at least one saturation sample and bounded
    post-saturation commands; every noise case retains its seed/model/std-dev
    or bound.
19. **Termination:** no indefinite circling, unexplained timeout/failsafe,
    missing terminal evidence, recorder timeout, cleanup failure, or orphan.
20. **Reproducibility:** all ten repeats retain
    goal/timeout/failsafe/collision categorical outcomes and required
    state/event coverage. Relative to the unique reference:
    - escape and convergence time: within `max(2.0 s, 10%)`;
    - path length: within `max(0.25 m, 10%)`;
    - orbit count: within `0.25`;
    - final aggregate-target distance: within `0.10 m`.
21. **Reporting:** observed end-to-end and escape rates are reported with
    two-sided 95% Wilson score intervals overall and by family. Wilson
    intervals are descriptive and never replace point gates.
22. **Legacy/regression:** selectable legacy behavior, current robust unit and
    integration behavior, parameter typing, and controlled shutdown
    regressions pass without worsening the documented inherited global debt.
23. **Tag gate:** only after Gates 1–22 pass may the terminal, tested,
    evidence-complete commit receive the annotated tag
    `gesc-gaussian-simulation-ready-v3`. Never force, move, or overwrite it;
    do not push automatically.

## Early-stop rules

### Activation

- Cleanup contamination, non-ground collision, duplicate canonical ownership,
  corrupt evidence, missing final zero, or hash drift stops dispatch
  immediately.
- An ordinary valid behavioral miss does not hide remaining activation
  questions: finish the ten-case activation set, report all branches, then
  stop before development.

### Development

- Run all 30 declared slots unless a hard safety/evidence/cleanup stop occurs.
- No eligible candidate, zero end-to-end success across candidates, or zero
  escape activation closes v3 before freeze.

### Holdout

- A zero-tolerance integrity, collision, cleanup, final-zero, contract-hash, or
  frozen-input failure stops immediately.
- After each valid run, compute the best attainable overall and family counts.
  Stop when `18/20` or any family floor is mathematically unreachable.
- Any holdout gate miss closes v3. Do not expose or run the additional 50
  merely for curiosity.

### Additional unique validation

- Start only after the holdout passes.
- Stop immediately on a zero-tolerance integrity/safety/hash failure.
- After each valid result, assume every remaining slot succeeds and recompute
  optimistic bounds for `63/70`, each family floor, 95% escape success,
  median/p95 escape, median orbit, and revisit rate. Stop only when a declared
  gate is mathematically impossible.
- Otherwise complete all 50 even if interim point estimates are low.

### Reproducibility

- Start only after every 70-case gate passes.
- Because all ten comparisons must pass, the first valid categorical or
  numeric mismatch, or any integrity failure, closes the version and stops
  remaining repeats.

Every early stop produces final partial gate artifacts with unrun gates
represented as `not_run`/`null`.

## Bounded infrastructure-invalid replacement

An attempt qualifies only when all of the following are proved from coordinator
and retained-bag evidence:

- readiness was never true;
- no nonzero command occurred;
- no non-`SEARCH` robust state, transition, active fill, or active escape
  occurred;
- the cause is external startup/readiness infrastructure rather than
  algorithm behavior;
- cleanup is complete enough to establish a clean next start;
- classification is recorded before redispatch.

The replacement must use the identical case, seed, profile, frozen hashes, and
contract. Both attempts remain linked to the declared slot.

Caps:

| Stage | Maximum replacement attempts |
|---|---:|
| Activation | 1 |
| Development | 3, no more than one per candidate |
| Holdout | 1 |
| Additional validation | 2 |
| Reproducibility | 1 |
| **V3 total** | **8** |

No slot receives more than one replacement. Exceeding a stage or total cap,
or a second invalid attempt for one slot, fails the infrastructure gate.
A valid behavioral failure is never replaced.

## Evidence roots and artifacts

Fresh root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3
```

Required layout:

```text
phase08_v3/
├── qualification/
├── activation/
├── development/
│   ├── V3-C0/
│   ├── V3-C1/
│   └── V3-C2/
├── sealed/
│   ├── phase08_v3_acceptance_suite.json
│   └── phase_08_v3_acceptance_contract.json
├── holdout/
├── validation/
├── reproducibility/
├── replacements/
├── logs/
└── workflow_state/
    ├── v3_prepare.json
    ├── v3_qualification.json
    ├── v3_activation.json
    ├── v3_development.json
    ├── v3_freeze.json
    ├── v3_contract.json
    ├── v3_holdout.json
    ├── v3_validation.json
    ├── v3_reproducibility.json
    └── v3_terminal.json
```

Run directories retain the Phase 05/06 contract:

```text
bag/
metadata.yaml
resolved_topics.yaml
resolved_parameters.yaml
resolved_scenario.yaml
console.log
completeness.json
notes.md
analysis/
```

No large bag, plot, or verbose log enters Git. The user-authorized canonical
cleartext suite and its commitment enter Git before activation.

## Files proposed for modification

### Context workflow and durable navigation

- `DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh`
  - discover and require the numerically highest Phase 08 subphase Plan;
  - identify `phase_08_3_plan.md` as active;
  - remove the hardcoded `_2` requirement;
  - for Phase 09, require the v3 handoff plus machine-readable
    `simulation_ready: true`.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh`
  - retain latest-Plan discovery;
  - include the v3 freeze-state path/hash and concise immutable freeze fields
    when present.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/make_codex_context_bundle.sh`
  - identify the active latest Plan;
  - include the current milestone, v3 freeze-state hash/fields, contract hash,
    next criterion, and terminal boundary without relying on the first 260
    status lines.
- `docs/codex/gesc_gaussian/status/phase_08_status.md`
  - reopen append-only as `IN PROGRESS — PHASE 08.3 V3 ACCEPTANCE`;
  - preserve all historical contents;
  - add the v3 authority/boundary, active Plan hash, current milestone,
    freeze state, commands/results, artifact paths, do-not-repeat entries, and
    next criterion.
- `docs/codex/gesc_gaussian/implementation_sequence.md`
  - identify v3 as the active successor and point to its sealed contract and
    terminal handoff.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/00_MASTER_IMPLEMENTATION_PLAN.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/06_TEST_MATRIX_AND_ACCEPTANCE_GATES.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`
  - record the approved v3 boundary, active-latest-subphase rule, exact
    contract reference, and final outcome only from verified evidence.

### Existing execution, analysis, and packaging owners

- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py`
  - add backward-compatible schema 4, named result scopes, aggregate truth,
    metric applicability, acceptance-family, repeat-reference, and
    full-lifecycle binding.
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py`
  - resolve aggregate truth, classify terminal distance to aggregate targets,
    report named scopes, allow development-only graceful boundary stop, and
    retain global safety through shutdown.
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/phase08_validation.py`
  - preserve v1/v2 read/report compatibility;
  - add the v3 prepare/qualify/activation/development/freeze/seal/holdout/
    validation/reproducibility/report workflow;
  - enforce cleartext commitments, stage order, replacements, freeze
    hashes, denominators, early stops, Wilson intervals, and partial/final
    artifacts.
- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py`
  - use resolved aggregate targets for v4 ground truth;
  - expose per-attempt duration/orbit rows and applicability in
    `summary_metrics.json` without changing existing v1–v3 analysis behavior.
- `ros2_ws/src/ros_esc/setup.py`
  - install the new v3 YAML/JSON inputs; retain the existing
    `validate_robustness` entry point.

### Tests and documentation

- `ros2_ws/src/ros_esc/test/test_phase08_validation.py`
- `ros2_ws/src/ros_esc/test/test_scenario_schema.py`
- `ros2_ws/src/ros_esc/test/test_scenario_runner.py`
- `ros2_ws/src/ros_esc/test/test_bag_analysis.py`
- `ros2_ws/src/ros_esc/test/test_bag_analysis_integration.py`
- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/topic_dictionary.md`
- `docs/codex/gesc_gaussian/recording_runs.md`

No modification is planned for controller, supervisor, recenter, Gaussian
design, recorder, completeness validator, message definitions, launch graph,
URDF/world, Heavy-Ball, or physical files. If live implementation evidence
requires one, stop for Plan review rather than expand this list silently.

## Files proposed for creation

### Pure helper and tests

- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/aggregate_field_truth.py`
  - pure deterministic adapter around `Multi_Light_Source_Cost`; no ROS node.
- `ros2_ws/src/ros_esc/test/test_aggregate_field_truth.py`

The helper is justified because aggregate target derivation is a distinct,
reusable scenario/evaluation responsibility. It does not duplicate the cost
formula and creates no ROS owner or interface.

### V3 scenario and freeze inputs

- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v3_activation.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v3_development.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v3_candidates.yaml`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v3_frozen_parameters.yaml`
  - generated only after selection.
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v3_acceptance_suite.json`
  - generated, hashed, and committed in cleartext before activation.

### Durable v3 evidence

- `docs/codex/gesc_gaussian/validation/phase_08_v3_suite_commitment.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v3_parameter_selection.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v3_freeze_state.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v3_acceptance_contract.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v3_run_manifest.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v3_gate_results.json`
- `docs/codex/gesc_gaussian/validation/phase_08_v3_validation_report.md`
- `docs/codex/gesc_gaussian/validation/phase_08_v3_failure_report.md`
  - create only for a terminal failed/blocked experiment.
- `docs/codex/gesc_gaussian/handoffs/phase_08_3_handoff.md`

## Public interfaces, parameters, and compatibility

No ROS topic, message, service, action, package, controller owner, physical
interface, or algorithm launch default changes.

Add flat offline subcommands to the existing command:

```text
ros2 run ros_esc validate_robustness v3-prepare
ros2 run ros_esc validate_robustness v3-qualify
ros2 run ros_esc validate_robustness v3-activation
ros2 run ros_esc validate_robustness v3-development
ros2 run ros_esc validate_robustness v3-freeze
ros2 run ros_esc validate_robustness v3-seal
ros2 run ros_esc validate_robustness v3-holdout
ros2 run ros_esc validate_robustness v3-validation
ros2 run ros_esc validate_robustness v3-reproducibility
ros2 run ros_esc validate_robustness v3-report
```

Every subcommand requires `--operator` and `--evidence-root`.
`v3-prepare` requires no encryption-key argument. `v3-seal` verifies and binds
the already committed suite without credential or key handling.

V1 execution remains retired. V2 remains terminally failed. Their report
readers and durable artifacts remain readable. Schema versions 1–3 retain
their current parsing, normalized identities, manual-goal compatibility, and
classification. Schema 4 is v3-only.

GPG is not a Phase 08.3 prerequisite or ROS runtime dependency. The aggregate
helper uses the repository environment's existing NumPy/SciPy and cost-model
implementation. V3 adds no package, ROS dependency, node, message, service,
action, topic, or launch owner.

## Milestones, checkpoints, and proposed commit boundaries

No commit is authorized by this Plan-only chat. Each boundary below requires
explicit authorization in the future Implement chat. After every material
milestone: update live status, inspect the diff, run focused checks, run
`checkpoint_phase.sh 08`, and commit only if authorized.

### M0 — Reopen context without rewriting history

Work:

- verify clean `bc4b420d` successor state;
- implement latest-subphase Plan discovery;
- reopen the existing status append-only;
- add freeze-state awareness to checkpoint/context bundle;
- preserve all historical Plan/status/handoff/evidence hashes.

Exit:

- normal and strict-history Phase 08 Implement checks pass;
- Phase 09 remains blocked;
- context tools identify `phase_08_3_plan.md`;
- shell syntax and focused tool tests pass;
- `git diff --check` passes.

Proposed commit:

```text
phase 08.3: open v3 acceptance workflow
```

Next criterion: schema-v4/aggregate/envelope implementation.

### M1 — Implement and test v3 evidence contracts

Work:

- add aggregate truth helper and schema 4;
- extend runner, analyzer, and existing workflow owner;
- add activation/development/candidate inputs;
- add encryption/commitment and replacement logic;
- add focused tests and docs.

Exit:

- new and retained functional tests pass;
- historical schema/case identities and v1/v2 reports remain byte-compatible;
- aggregate solver agreement/rejection tests pass;
- GPG round-trip tests use an ephemeral test key only;
- no controller/recorder/validator duplicate exists.

Proposed commit:

```text
phase 08.3: add aggregate-grounded v3 contracts
```

Next criterion: the user-authorized Amendment A1 boundary.

### M1A — Adopt the user-authorized cleartext precommit

This milestone records the post-M1 design amendment without rewriting the
historical M1 result. It occurs before M2, suite generation, or Gazebo.

Work:

- remove GPG, recipient, encryption, ciphertext, and decryption handling from
  the v3-only workflow;
- make `v3-prepare` write canonical cleartext suite bytes plus a hash
  commitment;
- require the suite and commitment to be checkpointed and tracked exactly in
  Git before M3 activation;
- retain every numeric gate, allocation, threshold, denominator, stage-order,
  replacement, and early-stop rule;
- update active operator guidance and append-only status without rewriting
  historical v1/v2/08.1/08.2 or M1 evidence.

Exit:

- focused v3 workflow, context, documentation, syntax, style, and compatibility
  checks pass;
- the CLI accepts no key or recipient argument;
- no acceptance suite, evidence root, Gazebo run, or hardware action exists;
- status and checkpoint identify the researcher-visible non-blind design.

Proposed commit:

```text
phase 08.3: adopt cleartext v3 precommit
```

Next criterion: pre-activation source/build/dry-run qualification.

### M2 — Pre-activation qualification and cleartext suite commitment

This is the required small pre-activation qualification milestone. It performs
no acceptance run.

Work:

- isolated build and installed entry-point checks;
- functional suite and schema-v4 dry runs;
- runtime parameter instantiation without Gazebo motion;
- generate and aggregate-qualify the cleartext 70+10 acceptance population;
- commit the canonical suite and hash commitment;
- verify activation/development counts `10` and `10`;
- verify acceptance counts/allocation `20/50/70/10`;
- verify all historical case keys are excluded;
- verify fresh root, process cleanliness, exact suite/commitment hashes, and
  disk forecast.

Exit:

- qualification state passes;
- cleartext acceptance identities and hashes are fixed and checkpointed;
- activation may start.

Proposed commit:

```text
phase 08.3: qualify and precommit fresh acceptance suite
```

Next criterion: all ten activation contracts.

### M3 — Execute ten fresh activation cases

Work:

- dispatch serial GUI-enabled activation;
- retain and analyze each attempt once;
- apply only the bounded infrastructure-invalid replacement policy;
- verify full-scope evidence and branch coverage.

Exit:

- `10/10` declared contracts and functional checks pass, or v3 closes failed
  before development.

Proposed evidence commit:

```text
phase 08.3: retain v3 activation evidence
```

Next criterion: 30-run development and eligible selection.

### M4 — Execute 30 development runs and select

Work:

- run candidates `V3-C0`, `V3-C1`, `V3-C2` serially over the same ten cases;
- analyze once;
- retain all attempts;
- calculate eligibility and lexicographic selection;
- write parameter-selection evidence.

Exit:

- exactly one deterministic winner exists and meets every eligibility floor,
  or v3 closes failed before freeze.

Proposed evidence commit:

```text
phase 08.3: select bounded v3 parameter bundle
```

Next criterion: clean implementation/profile/scenario freeze.

### M5 — Clean freeze and contract seal

Work:

- generate frozen YAML;
- rerun source/build/test/dry-run qualification;
- verify cleartext suite/commitment unchanged;
- commit the implementation/profile/scenario freeze;
- require clean Git;
- verify and bind the precommitted cleartext suite;
- generate and hash the one acceptance contract and run manifest;
- commit only evidence/contract/status changes;
- verify runtime input hashes still match the freeze.

Required freeze commit:

```text
phase 08.3: freeze v3 implementation profile and scenarios
```

Proposed evidence-only seal commit:

```text
phase 08.3: seal v3 acceptance contract
```

Next criterion: 20-run holdout early gate.

### M6 — Execute the 20-run holdout once

Work:

- serial execution under the frozen profile;
- read/analyze each run once;
- enforce early stops and replacement cap;
- calculate overall/family/lifecycle/evidence gates.

Exit:

- holdout passes every early gate, or v3 closes failed and the 50+10 later
  slots remain not run.

Proposed evidence commit:

```text
phase 08.3: retain v3 holdout evidence
```

Next criterion: 50 additional unique validation cases.

### M7 — Execute 50 additional unique cases

Work:

- dispatch only after M6 passes;
- maintain 70-case pooled counts and optimistic early-stop bounds;
- retain/analyze every dispatched attempt once;
- calculate all unique-case gates and Wilson intervals.

Exit:

- all 70-case gates pass, or v3 closes failed before repeats.

Proposed evidence commit:

```text
phase 08.3: retain v3 unique validation evidence
```

Next criterion: ten reproducibility comparisons.

### M8 — Execute ten targeted repeats

Work:

- dispatch predeclared references only;
- stop at the first valid mismatch;
- compare categorical and numeric results exactly as sealed.

Exit:

- `10/10` pass, or v3 closes failed without a tag.

Proposed evidence commit:

```text
phase 08.3: retain v3 reproducibility evidence
```

Next criterion: terminal report/handoff and conditional tag.

### M9 — Terminal success or failure closeout

Always:

- generate gate JSON, manifest, report, and handoff;
- close status `COMPLETE` or `FAILED`;
- checkpoint;
- verify historical evidence unchanged;
- report Git state, skips, unexecuted stages, limitations, and no hardware.

On failure:

- create the failure report;
- keep every passed and failed artifact;
- do not weaken/recompute the contract;
- do not tag;
- do not start v4 automatically;
- recommend the smallest v4 only if evidence justifies another engineering
  iteration.

On success only:

- verify every gate and contract hash;
- verify the proposed tag is absent;
- create the annotated local tag on the terminal tested commit:

```bash
git tag -a gesc-gaussian-simulation-ready-v3 \
  -m "GESC Gaussian simulation-ready v3: all sealed Phase 08.3 gates passed"
```

- do not push automatically.

Proposed terminal commit:

```text
phase 08.3: close fresh robustness acceptance
```

## Exact implementation and qualification commands

These commands are future commands; none ran in this Plan chat.

### Context, environment, and build

```bash
cd /home/mattb/dsim-lab
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 08
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 implement
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 implement --strict-history

source /opt/ros/humble/setup.bash
cd /home/mattb/dsim-lab/ros2_ws
export ROS_LOG_DIR=/tmp/dsim_phase08_v3_ros_logs
export MPLCONFIGDIR=/tmp/dsim_phase08_v3_mpl
timeout 600s colcon --log-base /tmp/dsim_phase08_v3_build_logs build \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source /home/mattb/dsim-lab/ros2_ws/install/setup.bash
```

### Focused functional gate

```bash
timeout 300s python3 -m pytest -q -rs \
  src/ros_esc/test/test_aggregate_field_truth.py \
  src/ros_esc/test/test_phase08_validation.py \
  src/ros_esc/test/test_bag_analysis.py \
  src/ros_esc/test/test_bag_analysis_integration.py \
  src/ros_esc/test/test_scenario_schema.py \
  src/ros_esc/test/test_scenario_runner.py \
  src/ros_esc/test/test_simulation_disturbances.py \
  src/ros_esc/test/test_experiment_recording.py \
  src/ros_esc/test/test_recording_integration.py \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_escape_recenter.py
```

Expected: all collected functional tests pass; only the two explicit Gazebo
opt-in tests may skip. Compare exact totals to `289 passed, 2 skipped,
3 deselected`; report additions rather than assuming the total.

### Installed dry runs

```bash
timeout 30s ros2 launch turtlebot3_rotating_sensor \
  gazebo.launch.xml --show-args

timeout --signal=INT --kill-after=5s 5s \
  ros2 run ros_esc supervisor_node --ros-args \
    -p algorithm_profile:=robust_gaussian_v1 \
    -p use_sim_time:=false \
    -p stall_window_sec:=3.0 \
    -p minimum_radial_progress_m:=0.05

timeout --signal=INT --kill-after=5s 5s \
  ros2 run ros_esc gaussian_fill_node --ros-args \
    -p use_sim_time:=false \
    -p covariance_scale:=2.5 \
    -p amplitude_depth_scale:=1.5 \
    -p exit_sigma:=2.5

timeout 120s ros2 run ros_esc run_scenario \
  /home/mattb/dsim-lab/ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v3_activation.yaml \
  --operator phase08_v3 --dry-run \
  --summary-output /tmp/phase08_v3_activation_dry.yaml

timeout 120s ros2 run ros_esc run_scenario \
  /home/mattb/dsim-lab/ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v3_development.yaml \
  --operator phase08_v3 --dry-run \
  --summary-output /tmp/phase08_v3_development_dry.yaml
```

The launch-argument check is descriptive only and does not validate parameter
types. The bounded supervisor and fill processes are the required runtime
instantiations; timeout-wrapper exit `124` is expected only after clean SIGINT
shutdown and zero surviving descendants. The scenario checks must resolve
`10` activation and `10` development cases, zero unsupported, schema 4,
positive normal verification margins, and all aggregate contracts qualified.

### V3 workflow

```bash
export PHASE08_V3_ROOT=/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3

timeout 1800s ros2 run ros_esc validate_robustness v3-prepare \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3_ROOT"

timeout 1800s ros2 run ros_esc validate_robustness v3-qualify \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3_ROOT"

timeout 10800s ros2 run ros_esc validate_robustness v3-activation \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3_ROOT"

timeout 28800s ros2 run ros_esc validate_robustness v3-development \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3_ROOT"

timeout 1800s ros2 run ros_esc validate_robustness v3-freeze \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3_ROOT"

timeout 1800s ros2 run ros_esc validate_robustness v3-seal \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3_ROOT"

timeout 21600s ros2 run ros_esc validate_robustness v3-holdout \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3_ROOT"

timeout 46800s ros2 run ros_esc validate_robustness v3-validation \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3_ROOT"

timeout 10800s ros2 run ros_esc validate_robustness v3-reproducibility \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3_ROOT"

timeout 1800s ros2 run ros_esc validate_robustness v3-report \
  --operator phase08_v3 \
  --evidence-root "$PHASE08_V3_ROOT"
```

Every command writes verbose output under
`$PHASE08_V3_ROOT/logs/`; live status records only the command, exit, concise
result, hashes, and retained paths. The outer stage bounds include the
stage-specific maximum replacement attempts plus bounded analysis and cleanup
overhead; they do not relax any per-run limit.

### Package/global and final static checks

```bash
cd /home/mattb/dsim-lab/ros2_ws
timeout 900s colcon --log-base /tmp/dsim_phase08_v3_test_logs test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
timeout 120s colcon test-result \
  --test-result-base /home/mattb/dsim-lab/ros2_ws/build \
  --all --verbose

timeout 120s python3 -m compileall -q \
  /home/mattb/dsim-lab/ros2_ws/src/ros_esc/ros_esc/scenario_runner \
  /home/mattb/dsim-lab/ros2_ws/src/ros_esc/ros_esc/plotting_scripts

cd /home/mattb/dsim-lab
timeout 120s bash -n \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/make_codex_context_bundle.sh
git diff --check
git status --short --branch
```

Focused `ament_flake8` and `ament_pep257` run over every changed Python file.
Repository-wide inherited lint debt is reported separately; no new changed-line
finding is permitted.

```bash
cd /home/mattb/dsim-lab/ros2_ws/src/ros_esc
timeout 180s ament_flake8 \
  ros_esc/scenario_runner/aggregate_field_truth.py \
  ros_esc/scenario_runner/scenario_schema.py \
  ros_esc/scenario_runner/run_scenario.py \
  ros_esc/scenario_runner/phase08_validation.py \
  ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py \
  setup.py \
  test/test_aggregate_field_truth.py \
  test/test_phase08_validation.py \
  test/test_scenario_schema.py \
  test/test_scenario_runner.py \
  test/test_bag_analysis.py \
  test/test_bag_analysis_integration.py \
  test/test_legacy_behavior.py

timeout 180s ament_pep257 \
  ros_esc/scenario_runner/aggregate_field_truth.py \
  ros_esc/scenario_runner/scenario_schema.py \
  ros_esc/scenario_runner/run_scenario.py \
  ros_esc/scenario_runner/phase08_validation.py \
  ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py \
  setup.py \
  test/test_aggregate_field_truth.py \
  test/test_phase08_validation.py \
  test/test_scenario_schema.py \
  test/test_scenario_runner.py \
  test/test_bag_analysis.py \
  test/test_bag_analysis_integration.py \
  test/test_legacy_behavior.py
```

### Read-only sqlite3 integrity

The `sqlite3` CLI is currently unavailable. The workflow must use Python's
standard `sqlite3` module read-only:

```text
connect("file:<bag.db3>?mode=ro", uri=True)
PRAGMA quick_check
```

Every formal bag must return `ok`. Never open a retained bag read-write.

## Disk-space and cleanup controls

Before each stage, require:

```text
free bytes >= 25 GiB + 512 MiB × remaining declared slots
```

After each completed stage, recompute using the larger of `512 MiB` or twice
the observed p95 attempt size. If the bound is not met, stop before dispatch;
do not delete or compress required evidence merely to continue.

Before and after each run/stage:

- capture the pre-existing ROS/Gazebo/session process set;
- require no new `run_scenario`, `record_run`, `ros2 bag`, `gzserver`,
  `gzclient`, supervisor, controller, fill, analyzer, or validation process;
- compare ROS node/topic ownership against the run-specific graph evidence;
- disable further dispatch before terminating a failed parent;
- inspect descendants repeatedly through the shutdown grace;
- preserve the attempt and cleanup report.

## Risks and stop conditions

### Level A — stop and request direction

- cost sign/units, controller ownership, canonical topics, selectable legacy
  behavior, or shared simulation/physical algorithm semantics would change;
- a new controller, recorder, validator, analyzer, algorithm node, package, or
  physical fork appears necessary;
- the cleartext acceptance suite or commitment cannot be kept byte-identical
  from M2 through freeze and terminal reporting;
- aggregate truth cannot call the authoritative cost owner without copying or
  changing its semantics;
- unrelated user changes overlap this scope and cannot be preserved;
- physical hardware or Phase 09 becomes necessary;
- required ROS/Gazebo dependencies are unavailable.

### Level B — bounded correction with evidence

Only local, testable context, schema, runner, analyzer, packaging,
readiness/evidence, or performance corrections that preserve architecture and
do not weaken gates may proceed. Record the original assumption, observed
contradiction, exact correction, files, tests, and scope in status and
handoff. Any algorithm behavior or scenario-population change after
precommit/freeze requires Plan review, not a silent Level B edit.

### Level C — terminal experiment failure

- activation, candidate eligibility, holdout, unique validation, or
  reproducibility gate fails;
- a valid behavior fails a frozen contract;
- a denominator, family floor, or immutable hash cannot be satisfied;
- replacement caps are exceeded.

Preserve evidence, generate the failure report, mark later stages not run,
close v3, do not tag, do not enter Phase 09, and do not start v4 automatically.

## Compaction-safe recovery

After every material boundary:

1. update `phase_08_status.md`;
2. atomically update external `workflow_state/v3_<stage>.json`;
3. update `phase_08_v3_freeze_state.json` after freeze without changing its
   immutable fields;
4. run `checkpoint_phase.sh 08`;
5. create a bounded commit only if authorized;
6. record exact run-summary, completeness, analysis, manifest, contract, and
   log paths.

After compaction/interruption, read:

```text
AGENTS.md
phase_08_3_plan.md
phase_08_status.md
phase_08_v3_freeze_state.json, if present
the current stage workflow_state JSON
the latest checkpoint
Git status/diff/log
```

Recover completed work from manifests, records, completeness files, analysis
summaries, contract/freeze hashes, and checkpoints. Never rerun a matrix,
repeat analysis, alter the precommitted suite, or rehash large retained bags
merely to recover chat context.

## Implementation-time assumptions to verify

- planning HEAD and historical hashes remain available;
- v3 root remains absent before M2 preparation;
- NumPy, SciPy, PyYAML, rosbag2 sqlite3, Gazebo contacts, and installed ROS
  message classes remain available;
- current broad/focused baselines remain reproducible in the intended
  environment with writable ROS/Matplotlib paths;
- schema 1–3 case keys and behavior remain unchanged;
- exact aggregate solver tolerances are stable under repeated orderings and
  installed/source imports;
- the ten activation and ten development geometries satisfy their aggregate
  reachability/classification contracts;
- the cleartext suite has 70 unique keys, the exact allocations, ten valid
  repeat references, and no historical/development collision;
- scenario run duration `240 s` and wall bound `600 s` remain finite and
  adequate without changing algorithm timeouts;
- current readiness, completeness, collision, cleanup, final-zero, timestamp,
  causality, and strict-JSON checks cover every formal run;
- current per-attempt analyzer rows support the declared minimum
  denominators after the planned additive summary change;
- proposed tag `gesc-gaussian-simulation-ready-v3` is absent before creation.

Any failed assumption is recorded with exact evidence and handled under the
Level A/B/C policy.

## Decisions requiring user approval before implementation can finish

The user has authorized the cleartext-suite amendment and the Implement
continuation with its declared checkpoint/commit boundaries. The conditional
simulation-ready tag remains unauthorized unless every v3 gate passes.

No unresolved scientific allocation, threshold, denominator, candidate,
family, freeze, early-stop, replacement, evidence-root, or tag-name decision
remains in this Plan.

## Terminal boundary

No physical hardware, Phase 09 work, v3 Gazebo stage, tuning, acceptance run,
reproducibility run, readiness tag, or source implementation is authorized or
performed by saving this Plan. The next action after review is a separately
authorized v3 Implement continuation beginning at M0.

## M3A amendment — contact-control contamination and fresh V3B lineage

This append-only amendment was added after the first M3 activation dispatch.
It supersedes only the evidence root and qualification lineage needed to
correct the observed validation-harness defect. It does not rewrite the
original M3 result or change the research objective, algorithm, activation
cases, scenario population, candidates, thresholds, denominators, family
floors, stage order, early stops, replacements, collision gate, or tag gate.

The user instructed Codex to continue the robustness implementation after
removing the unrelated encryption requirement. That authority includes this
documented bounded runner correction and a fresh corrected activation
lineage; it does not authorize physical hardware, Phase 09, a weakened gate,
or a readiness claim without all declared passes.

### Observed contradiction

The first GUI-visible run,
`v3a_goal_aggregate_direct` seed `9301`, executed once from clean committed
HEAD `d69407b`. The workflow retained the run and stopped with
`non-ground collision`, leaving the other nine activation IDs `not_run`.
Recording, final zero, and cleanup passed.

Read-only bag inspection found `105` non-ground contact states. Every state
involved the reserved
`phase08_contact_positive_control::probe::collision`; there was no other
non-ground pair. The first probe contact occurred approximately `0.154 s`
after readiness and the last approximately `0.388 s` after readiness. The
probe applied a real physical impulse, so the trajectory is contaminated and
cannot be reclassified as collision-free or treated as independent behavior
evidence.

The root cause is local and exact: schema-v4 launch construction enabled the
static physical positive-control probe whenever `collision_expected` was
non-null, including every formal `collision_expected=false` case. The
analyzer correctly classified the resulting contact and remains unchanged.

Durable evidence:

- failure report:
  `validation/phase_08_v3a_failure_report.md`;
- machine-readable audit:
  `validation/phase_08_v3a_contact_probe_contamination.json`;
- superseded immutable root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3`;
- activation state SHA-256:
  `5fa0b4e91746bfadca363a7cdb8438d46488f4009c0bd31ae33f81d8a2457cc2`;
- raw bag SHA-256:
  `bf07bcd3458e42b497d33fc302c2e018a68a1ce6636ab75b09af5ec26d405ae8`.

### V3A disposition

V3A is closed failed and is not simulation-ready. Its state, progress,
records, run, bag, analysis, and nine `not_run` IDs are immutable. It is not
eligible for the pre-readiness replacement policy because readiness became
true and lifecycle activity occurred. The old root is never resumed,
overwritten, combined with V3B, or counted.

### Bounded correction

The launch rule becomes:

```text
contact probe enabled iff collision_expected is true
```

Contact sensors remain enabled for every formal case. Expected-false runs
must still provide readiness contact messages and must contain zero real
non-ground contacts. Missing contact evidence remains invalid; any wall,
robot, or other non-ground contact remains a hard stop. The explicit
schema-v2 `contact_positive` support case continues to spawn the real static
probe. Retained Phase 07.5 runtime evidence already proves a valid positive
contact and valid no-probe negative contact.

Filtering the reserved probe out of analysis is prohibited because that would
hide a physical perturbation. No analyzer, completeness, collision-integrity,
or hard-stop threshold changes.

### Fresh V3B recovery contract

Corrected execution uses the absent fresh root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b
```

The new `v3-adopt-precommit` workflow action must:

1. require a clean committed corrected checkout and empty ROS/Gazebo process
   set;
2. verify the V3A activation state, records, attempt, metadata, scenario, and
   raw-bag hashes against the machine-readable contamination audit;
3. leave every V3A byte unchanged;
4. adopt the exact tracked
   `phase08_v3_acceptance_suite.json` and
   `phase_08_v3_suite_commitment.json` bytes without regeneration;
5. bind the V3A evidence hashes, correction-audit hash, current repository
   snapshot, fixed suite hash, fixed commitment hash, disk forecast, and
   operator into a recoverable fresh prepare transaction and prepare state;
6. reject any existing unowned V3B root, recovered-root or operator drift,
   suite/commitment drift from V3A, old-source snapshot, or corrected launch
   that still enables the probe for `collision_expected=false`.

V3B then reruns the complete M2 qualification against the corrected source.
Qualification must revalidate the V3A recovery proof and all ten installed
probe-off activation launch commands. Activation rehashes that retained dry
run and revalidates the recovery chain immediately before dispatch. Direct
non-dry `run_scenario` execution of the formal v3 activation/development
suites is prohibited; dry inspection remains permitted. Only a passing V3B
qualification may start activation. V3B reruns all ten
activation cases from the beginning with `gazebo_gui=true`; it does not run
only the nine previously undispatched cases. The exact original IDs, seeds,
geometries, profile, and contracts remain fixed.

If a V3B case has an ordinary valid behavioral miss, finish all ten as
originally declared and close before development. If it has a real
non-ground collision, evidence failure, cleanup contamination, hash drift, or
other original hard stop, stop immediately. M4 remains prohibited unless V3B
passes `10/10` activation contracts and every integrity check.

### Amended milestone sequence

#### M3A — retain V3A and validate the bounded correction

- preserve and hash V3A evidence;
- add the failure report and contamination audit;
- implement probe dispatch only for explicit positive controls;
- add negative-control, positive-control, V3A-preservation, fresh-root,
  exact-precommit-adoption, and new-snapshot tests;
- run focused/full functional, lint, syntax, context, document, and installed
  dry-run qualification;
- checkpoint and commit before empirical redispatch.

Exit: V3A is durably closed; corrected source and recovery workflow pass; the
worktree is clean at an independently reviewable commit.

#### M3B — adopt, qualify, and execute fresh activation

- create V3B through `v3-adopt-precommit`;
- run `v3-qualify` in V3B and checkpoint its exact state;
- execute all ten serial GUI-visible activation cases;
- retain and analyze each attempt once;
- apply only the unchanged pre-readiness infrastructure replacement policy.

Exit: `10/10` V3B contracts and all integrity checks pass, or Phase 08.3
closes failed before development.

This amendment is the required Plan review for the post-precommit
runner/evidence-lineage correction. It does not authorize an algorithm or
scenario-population change.

## M3C amendment — behavioral-miss routing and fresh V3C lineage

This append-only amendment was added after V3B executed its first
GUI-visible activation case. It supersedes only the immediate hard-stop
routing and recovery lineage needed to finish the ten-case activation
diagnosis. It does not rewrite V3A or V3B, change the research objective,
algorithm, profile, activation cases, seeds, geometry, suite, candidates,
thresholds, denominators, family floors, stage order, collision gate,
evidence-integrity gate, final behavior verdict, or readiness-tag gate.

The user authorized continued implementation and actual Gazebo simulation.
That authority includes this bounded validation-workflow correction and a
fresh corrected lineage. It does not authorize weakening the observed V3B
behavioral failure, physical hardware, Phase 09, post-outcome scenario
adaptation, or a simulation-readiness claim without every declared pass.

### Observed V3B result

V3B ran `v3a_goal_aggregate_direct`, seed `9301`, once from a clean
evidence-only successor of qualified runtime commit
`e9e1d500116fe884d06574d316143da94e25d920`. Gazebo used
`gazebo_gui=true`, passive contact sensors were enabled, and the physical
positive-control probe was disabled.

Recording, sqlite3 readability, fresh Phase 05 validation, cleanup, final
zero, final readiness false, timestamp/causality evidence, and collision
evidence passed. No timeout, failsafe, non-ground collision, analysis
exception, invalid metric, missing critical input, or raw-bag drift occurred.
The controller and aggregate-field goal both passed; the final aggregate
distance was `0.03908346942306904 m` and the terminal state was `GOAL_HOLD`.

The direct-path behavior contract nevertheless failed. It required:

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

This is a valid behavioral miss. The eventual recovery does not make the
predeclared direct-path contract pass.

### Observed routing contradiction

The direct case predeclared escape metrics as not applicable. The analyzer
correctly recorded the unexpected escape as:

```text
applicability_integrity.passed = false
analysis_status = partial
reason = "escape occurred in a case declared not applicable"
```

The outer V3 workflow then treated every non-`complete` analysis status as an
immediate corrupt-evidence hard stop. That stopped the other nine activation
cases. It contradicts the unchanged activation rule that an ordinary valid
behavioral miss must be retained, the remaining activation questions must
still run, and development must then stop.

Durable records:

- failure report:
  `validation/phase_08_v3b_failure_report.md`;
- machine-readable audit:
  `validation/phase_08_v3b_hard_stop_policy_misclassification.json`;
- audit omission SHA-256:
  `dbec6d73e23a7b590e99558e43ec57c99c68fbe5f6921301a8fc618407ebf56e`;
- superseded immutable root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b`;
- activation internal state SHA-256:
  `8d50df1cf6eed92a8829758357aacbc61503f816f65086a3f51120e1105c9a48`;
- raw bag SHA-256:
  `2d9b2813b2c15623f62fc44907dc391636e4cd53254d2d923ce13d71ac72453c`.

### V3B disposition

V3B is closed failed and is not simulation-ready. Its prepare, qualification,
activation state, progress, records, one attempt, raw bag, analysis, and nine
`not_run` IDs are immutable. The first attempt is not
infrastructure-invalid, is not eligible for replacement, and is not imported
as a passing V3C record. V3B is never resumed, overwritten, combined with
V3C, or counted.

### Bounded correction

The analyzer remains unchanged. The record's `analysis_status=partial`,
failed applicability integrity, failed final record-integrity result, and
failed direct behavior contract all remain unchanged.

Only immediate dispatch routing changes:

- a `partial` analysis caused solely by a predeclared metric-applicability
  violation is an ordinary behavioral miss for the activation early-stop
  decision when all critical inputs, Phase 05 validation, recording,
  cleanup, collision evidence, raw-bag hashes, and extracted metrics are
  otherwise valid;
- it does not make final record integrity or behavior pass;
- an analysis exception, invalid critical input or metric, recording failure,
  missing or drifting hash, collision, cleanup contamination, timeout,
  duplicate ownership, or other original hard-stop condition still stops
  dispatch immediately.

Focused tests must prove both sides: the retained V3B record is non-hard for
dispatch but remains final-integrity failed; a true incomplete/corrupt
analysis still hard-stops.

### Fresh V3C recovery contract

Corrected execution uses the absent fresh root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3c
```

The existing `v3-adopt-precommit` public action is generalized internally by
recovery kind. For V3C it must:

1. require a clean committed corrected checkout, the exact operator, an
   absent fresh root, and an empty ROS/Gazebo process set;
2. verify V3B prepare, qualification, activation state, progress, records,
   attempt record, scenario summary, metadata, resolved scenario, scenario
   result, analysis summary/completeness, and raw-bag hashes against the new
   machine audit;
3. prove the exact V3B failure shape: completed infrastructure, good
   recording/cleanup/collision evidence, one record, nine `not_run`, a failed
   direct behavior contract, and the sole applicability-driven partial
   analysis;
4. recursively re-run the existing V3A contamination proof and require it to
   equal the recovery bound inside V3B prepare;
5. prove against corrected source that the retained V3B record no longer
   triggers an immediate hard stop while its final record-integrity check
   remains failed;
6. leave every V3A and V3B byte unchanged;
7. adopt the exact tracked suite and commitment bytes without regeneration;
8. bind the V3A-to-V3B-to-V3C recovery chain, current repository snapshot,
   fixed suite/commitment hashes, disk forecast, root, and operator into the
   fresh prepare transaction and state;
9. reject any source, operator, root, precommit, nested-recovery, audit, or
   retained-artifact drift.

V3C then reruns the complete qualification gate. Qualification must re-prove
both recovery generations, the full functional/build/runtime gate, all ten
installed GUI/contact/probe-off activation commands, and the unchanged
precommit. Activation repeats that proof immediately before dispatch.

V3C reruns all ten activation cases from the beginning with
`gazebo_gui=true`. It does not run only the nine V3B `not_run` cases, reuse
the V3B attempt, change a case, or regenerate the population. This is a
one-time validation-harness restart, not a behavioral retry budget.

If V3C has an ordinary valid behavioral miss, it finishes all ten and closes
before development. If it has collision, corrupt evidence, cleanup
contamination, hash drift, or another original hard stop, it stops
immediately. M4 remains prohibited unless V3C passes `10/10` activation
contracts and every integrity check.

### Amended milestone sequence

#### M3C — retain V3B and validate the hard-stop routing correction

- preserve and hash all V3B evidence;
- add the failure report and machine-readable routing audit;
- implement the pure-applicability behavioral-miss routing rule;
- generalize adoption/qualification/activation recovery by lineage kind;
- add V3B preservation, nested-recovery, fresh-root, exact-precommit,
  invocation-drift, policy, integrity, and true-corruption tests;
- run focused/full functional, lint, syntax, context, document, build, and
  installed dry-run qualification;
- checkpoint and commit before empirical redispatch.

Exit: V3B is durably closed; corrected source and the chained recovery
workflow pass; the worktree is clean at an independently reviewable commit.

#### M3D — adopt, qualify, and execute fresh V3C activation

- create V3C through `v3-adopt-precommit`;
- run `v3-qualify` in V3C and checkpoint its exact state;
- execute all ten serial GUI-visible activation cases;
- retain and analyze each attempt once;
- apply only the unchanged pre-readiness infrastructure replacement policy.

Exit: `10/10` V3C contracts and all integrity checks pass, or Phase 08.3
closes failed before development.

This amendment is the required Plan review for the post-outcome
validation-workflow correction. It does not authorize an algorithm,
parameter, analyzer-output, scenario, population, threshold, denominator, or
acceptance-gate change.

## M3C-A clarification — diagnostic completion without behavioral retry

This append-only clarification was added before M3C source implementation,
before V3C adoption, and before any V3C Gazebo dispatch. Independent review
found a scientific no-replacement conflict in the immediately preceding M3C
proposal to rerun all ten activation cases.

V3A justified an all-ten restart because its physical positive-control probe
contaminated the only trajectory. V3B is materially different: its first
trajectory is unperturbed, recording-complete, collision-free, cleanup-valid,
and behaviorally failed. It is valid evidence. Rerunning that same fixed slot
after seeing its failure would be a post-outcome retry and would contradict
the unchanged rule that a valid behavioral miss is never replaced.

Therefore the preceding M3C/M3D statements that V3C reruns all ten from the
beginning or may become a pass-eligible activation are retired. No code,
root, qualification, or V3C run was created under that proposal. The
machine-readable all-ten policy audit is retained as superseded planning
history:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_v3b_hard_stop_policy_misclassification.json
```

The binding diagnostic-completion audit is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_v3b_diagnostic_completion.json
```

Its omission SHA-256 is
`c7a8acb97755ee7d41b3bd7932e7d4181bc854b7ee310bf1d4325f365a385e8d`.

### Binding V3C disposition

V3C is a diagnostic-completion lineage, not a new pass-eligible activation
attempt:

1. carry the exact immutable V3B
   `v3a_goal_aggregate_direct` record by its original absolute path and
   SHA-256;
2. never copy over, rewrite, reanalyze, redispatch, replace, or relabel that
   slot;
3. explicitly record its provenance as one carried failed V3B record;
4. execute only the nine activation IDs that V3B retained as `not_run`;
5. retain the nine new GUI-visible results once each;
6. produce one composite ten-slot diagnostic report with
   `carried_record_count=1` and `new_execution_count=9`;
7. force the composite activation verdict to failed because the carried
   direct-path contract is failed;
8. close Phase 08.3 failed before M4 regardless of the nine new outcomes.

The fresh V3C root remains:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3c
```

Its progress and state must never claim ten fresh V3C simulations, `10/10`,
or simulation readiness. A future pass-eligible attempt would require a
separately precommitted new experiment version and is not authorized here.

### Chained recovery requirements

V3C adoption and qualification retain every M3C recovery proof, with these
additional requirements:

- the carried record path and SHA-256 must match V3B progress, records, the
  diagnostic-completion audit, and every pre-dispatch recheck;
- the carried record's full V3B run directory, raw bag, completeness,
  analysis, and nested V3A recovery remain immutable and hash-valid;
- V3C progress must distinguish `carried` from `executed` attempts;
- the serial executor must begin with the second activation slot and reject
  any attempt to dispatch the carried case;
- the corrected source may change only validation-workflow/test/documentation
  ownership; trajectory-affecting algorithm, profile, scenario, launch,
  source, seed, disturbance, and contract inputs must remain byte- or
  semantically identical;
- a pure applicability-driven behavioral miss may continue the remaining
  diagnostic dispatch only when all other evidence is valid;
- every collision, cleanup, recording, missing-evidence, true analysis,
  timeout, ownership, and hash failure remains an immediate hard stop.

### Clarified M3D exit

M3D does not have a passing exit. It completes when either:

- all nine previously undispatched cases have retained results, after which
  the composite ten-slot activation and Phase 08.3 close failed; or
- an unchanged hard-stop condition ends diagnostic dispatch earlier, after
  which Phase 08.3 closes failed with the remaining slots `not_run`.

M4, freeze, holdout, additional validation, reproducibility, the readiness
tag, Phase 09, and physical hardware remain prohibited.

## M3D-B amendment — close V3C prelaunch failure and use fresh V3D

This append-only amendment was added after the V3C activation command closed
and before any V3D root, qualification, or dispatch existed. It does not
change any behavior contract, case, seed, profile, threshold, denominator,
collision rule, evidence rule, no-replacement rule, or final acceptance
verdict.

V3C is **CLOSED / FAILED / PRELAUNCH INFRASTRUCTURE ERROR / NO SIMULATION
OUTCOME / NOT SIMULATION-READY**. Its evidence root is immutable:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3c
```

The first required new case, `v3a_below_target_fill`, did not produce a
simulation run directory below `runs/`, an attempt scenario summary, an
analyzed record, a bag, or a scientific outcome. V3C retained
`new_execution_count=0`; its sole record is the immutable V3B direct-goal
failure carried by pointer and hash. The V3C workflow's `run_count=1`
therefore describes that carried record, not a V3C Gazebo simulation.

The execution error is exactly:

```text
AttributeError: __enter__
```

The boundary observer created and initialized a private `rclpy` context and
created its node on that context, but called `rclpy.spin_once` without an
explicit executor. ROS 2 Humble then tried to construct the global executor
on the uninitialized default context. Its guard condition attempted to enter
the missing default-context handle and raised `AttributeError: __enter__`.
The later `_sigint_gc` destructor message is a secondary symptom of that
partially constructed executor, not a separate failure.

Because V3C produced no new simulation result, a fresh infrastructure
successor may execute the same nine previously undispatched cases once. That
successor is V3D, under the currently absent root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3d
```

### Binding V3D boundary

V3D must:

1. preserve V3A, V3B, and V3C byte-for-byte and prove the complete recovery
   chain before dispatch;
2. carry only the exact immutable V3B `v3a_goal_aggregate_direct` behavioral
   failure by its original path and SHA-256;
3. retain V3C solely as failed infrastructure provenance and never count its
   carried record or failed dispatch as a V3D execution;
4. make only the bounded validation-runner correction needed to bind the
   boundary observer's executor to the same private ROS context and close it
   deterministically;
5. rerun qualification against a clean committed source state and the exact
   unchanged suite and commitment;
6. execute exactly these nine cases, in this order, at most once each:
   `v3a_below_target_fill`, `v3a_pure_escape_recenter`,
   `v3a_stalled_assist`, `v3a_fill_merge`,
   `v3a_full_lifecycle_goal`, `v3a_revisit_guard`,
   `v3a_boundary_saturation`, `v3a_noise_delay`, and
   `v3a_safe_timeout`;
7. retain GUI-visible Gazebo, simulation contacts, the disabled physical
   contact probe, the enabled zero-probe control, serial dispatch, bounded
   cleanup, and every original hard stop;
8. report one carried failed V3B record plus at most nine new V3D records
   with unambiguous provenance;
9. force V3D activation and Phase 08.3 failed before M4 regardless of the
   nine new outcomes.

V3D is diagnostic completion only. It cannot pass Phase 08.3, establish
simulation readiness, authorize a tag, start Phase 09, or authorize physical
hardware. A future pass-eligible experiment remains outside this Plan.

### Amended milestone M3E

M3E implements and tests the private-context executor correction, records the
V3C prelaunch failure, checkpoints a clean source boundary, adopts and
qualifies fresh V3D, then executes only the exact nine cases above. It exits
when all nine have retained outcomes or an unchanged hard stop ends dispatch
earlier. Either exit closes Phase 08.3 failed with no M4.
