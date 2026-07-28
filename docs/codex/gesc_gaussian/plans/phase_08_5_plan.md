# Phase 08.5 Plan — V5 Obstructing-Local-Minimum Robustness

## Status and authority

**APPROVED FOR IMPLEMENTATION AND EXECUTION.**

The user directed Codex on 2026-07-28 to conduct V5 with a narrower research
question:

- direct convergence to the global minimum is outside scope;
- every case must place a lower-intensity local minimum directly on the route
  from the robot start to the stronger global minimum;
- every case must use exactly two or three lights, never more;
- successful behavior must demonstrate Gaussian fill, escape, recenter,
  resumed GESC search, and convergence to the global minimum.

This Plan authorizes bounded V5 implementation, qualification, visible-Gazebo
activation, headless development, freeze, formal execution, reporting, and
milestone commits. It does not authorize physical hardware, Phase 09, a
readiness claim before all gates pass, deletion or relabelling of historical
evidence, or any encryption/GPG requirement.

Planning preflight:

```text
branch
  feature/gesc-gaussian-robustness-v1
planning HEAD
  028e14682718c8caede9dfff654b9d955f2ef601
worktree
  clean; 36 commits ahead of origin
Phase 08 plan context
  complete
V4
  CLOSED / FAIL / NOT SIMULATION-READY
```

Current code, tests, resolved ROS graph, Git state, and retained evidence
remain authoritative.

## Research objective

V5 asks only:

> When a verified sub-goal local light minimum obstructs the route to a
> stronger global light minimum, does fixed GESC plus the robust Gaussian
> mechanism identify the undesired minimum, create a valid typed fill, escape
> it, recenter safely, resume search, and reach the realized aggregate-field
> global minimum?

The permitted success claim is limited to the predeclared two- and
three-light simulator-relative scenario population. It is not a claim about
direct source seeking, arbitrary nonconvex fields, absolute photometry,
physical TurtleBot readiness, or more than three lights.

## Historical boundary

All V1-V4 roots remain immutable historical evidence, including:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v4r2b
```

No historical attempt enters a V5 numerator, denominator, replacement, or
repeat comparison. V5 uses the absent fresh root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5
```

V4's direct-goal run remains a valid V4 failure. V5 does not reclassify or
rerun it.

## Existing owners

V5 extends only:

- `scenario_runner/aggregate_field_truth.py` for deterministic route-barrier
  truth;
- `scenario_runner/run_scenario.py` for the corresponding retained predicate;
- `scenario_runner/phase08_validation.py` for V5 specification, workflow, and
  terminal reporting;
- the existing scenario YAML/JSON owners and focused tests;
- existing package-data installation.

The sole recorder remains `record_run.py`; the sole completeness validator
remains `validate_run.py`; the sole analyzer remains
`gesc_gaussian_bag_analysis.py`; `gazebo.launch.xml` remains the sole
simulation graph; and `custom_controller` remains the sole `/cmd_vel`
publisher.

No duplicate controller, supervisor, fill node, runner, recorder, validator,
analyzer, launch graph, package, simulation fork, or physical fork is
allowed.

## Mandatory V5 scenario invariant

Every activation, development, holdout, validation, and repeat case must pass
the following static proof before any V5 Gazebo run:

1. The source list contains exactly two or three lights.
2. Exactly one source is the declared global source and has strictly greater
   intensity than every local/context source.
3. At least one lower-intensity source is the designated route blocker.
4. The blocker lies between start and the realized aggregate-field global
   target:
   - segment projection fraction in `[0.25, 0.70]`;
   - perpendicular distance from the start-to-global corridor at most
     `0.15 m`;
   - start-to-blocker distance at least `0.50 m`;
   - blocker-to-global-target distance at least `0.90 m`.
5. The authoritative light model has a numerically refined local basin near
   the blocker:
   - optimized basin center no more than `0.35 m` from the blocker source;
   - basin center remains in the route corridor and between start/global;
   - noise-adjusted source-score upper bound is strictly below `0.95`;
   - the minimum cost on a `0.25 m` enclosing ring exceeds the basin cost by
     at least `0.015` raw-cost units after the declared noise margin.
6. The existing aggregate-field solver proves at least one global target with
   noise-adjusted score at least `0.95`, beyond the blocker along the route.
7. All sources, starts, refined basins, and accepted global targets remain
   inside the existing room bounds and wall margin.

The proof is stored as `route_barrier_qualification` inside the existing
aggregate-field truth record and bound into its result SHA-256. Validation
recomputes the bounded local proof and rejects drift.

The local optimizer uses fixed bounds, fixed ring samples, fixed yaw samples,
fixed seed, and the existing authoritative model/sensor geometry. It does not
use Gazebo outcomes.

## Mandatory runtime lifecycle

Every V5 case must observe, in order:

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

An explicitly designated assisted case may additionally require
`ESCAPE_ASSIST` between `ESCAPE_REPULSE` and `RECENTER`.

Required events include:

```text
CONVERGENCE_CONFIRMED
FILL_CREATED
ESCAPE_STARTED
RECENTER_STARTED
RECENTER_COMPLETE
GOAL_REACHED
```

The first accepted fill center or causally correlated fill request must lie
within `0.35 m` of the precomputed route-blocker basin. This proves the
Gaussian fill was applied to the obstructing local minimum rather than an
unrelated extremum.

Direct `SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD` is a valid V5 behavioral
failure, even when collision-free and globally correct, because it does not
answer the declared research question.

Forbidden outcomes include unexpected `FAILSAFE`, `TIMEOUT`,
`FILL_REJECTED`, `FILL_DESIGN_FAILED`, collision, corrupt/incomplete evidence,
missing final zero, unclean shutdown, or an unavailable applicable metric.

## Light and geometry envelope

V5 uses only:

- two-light cases: one route-blocking local source and one stronger global
  source;
- three-light cases: the same blocking local/global pair plus either one
  weaker lateral context source or a second declared weak local source.

No light may be added merely to make activation pass. Fixed generation ranges:

```text
global intensity
  1800, 2200, or 2500 relative lumen input
blocking local intensity
  450, 550, or 650
optional third intensity
  300, 400, or 500
start-to-blocker distance
  0.55, 0.70, or 0.85 m
blocker-to-global-source distance
  1.20, 1.40, or 1.60 m
route lateral blocker offset
  0.00, 0.05, or 0.10 m
```

The generator uses fixed rotations/reflections and rejects any candidate that
does not pass the route-barrier truth. Rejection happens before suite
commitment and is recorded; it may not be replaced after runtime behavior is
observed.

## Fresh V5 inputs

Before any V5 Gazebo execution, create and commit:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v5_activation.yaml
  phase08_v5_development.yaml
  phase08_v5_candidates.yaml
  phase08_v5_acceptance_suite.json
  phase08_v5_frozen_parameters.yaml

docs/codex/gesc_gaussian/validation/
  phase_08_v5_suite_commitment.json
```

Identity and seeds:

```text
activation
  v5a_*; seeds 11001..11010; visible Gazebo
development
  v5d_*; seeds 11101..11110; headless Gazebo
formal unique
  v5h_*/v5v_*; seeds 11201..11270
reproducibility
  ten preselected references with fresh repeat seeds 11301..11310
```

All case keys must be fresh and disjoint from V1-V4.

## V5 run allocation

The 120-run structure remains:

| Stage | Runs | Formal denominator |
|---|---:|---|
| Visible activation | 10 | No |
| Headless development | 30 = 3 candidates x 10 cases | No |
| Headless holdout | 20 | Yes |
| Headless additional validation | 50 | Yes |
| Headless reproducibility | 10 | No |
| **Total** | **120** | **70 unique** |

Every one of the 120 slots is a two- or three-light obstructing-local-minimum
case. There are no direct-convergence control cases in V5.

## Population allocation

The fresh 70-case unique population is generated and committed before
activation:

| Family | Unique cases |
|---|---:|
| two-light collinear blocker | 20 |
| two-light offset-corridor blocker | 12 |
| three-light lateral context | 12 |
| three-light sequential weak blockers | 8 |
| wall/corner route | 8 |
| noise/delay route | 10 |
| **Total** | **70** |

Holdout/validation assignment is fixed before activation and stratified
across every family. Ten repeat references are fixed before activation and
cover two- and three-light, wall, noise/delay, pure-escape, and assisted
cases.

## Development candidates

The same ten headless development cases are run for:

| Parameter | V5-C0 | V5-C1 | V5-C2 |
|---|---:|---:|---:|
| fill covariance scale | 2.5 | 2.0 | 3.0 |
| amplitude-depth scale | 1.5 | 1.2 | 1.8 |
| fill exit sigma | 2.50 | 2.25 | 2.75 |
| stall window | 3.0 s | 4.0 s | 2.0 s |
| minimum radial progress | 0.05 m | 0.03 m | 0.08 m |

No other behavior parameter is tuned after activation.

Candidate eligibility requires:

- `10/10` evidence-valid development cases;
- `10/10` complete mandatory lifecycles;
- every applicable escape succeeds;
- every route-blocker encounter passes;
- zero collision, unexpected failsafe, cleanup/orphan, bag/completeness,
  final-zero, timestamp, causality, or unavailable-applicable-metric failure.

Eligible candidates use the existing deterministic lexicographic selection
rule. A tie ends with candidate ID. No candidate is selected by inspecting
formal outcomes.

## Formal acceptance gates

After exactly one candidate is frozen and the contract is sealed:

- `70/70` unique cases pass the mandatory full lifecycle and reach the
  aggregate global target;
- `70/70` route-blocker encounter predicates pass;
- `70/70` Gaussian fill, escape, recenter, resumed-search, and second
  verification predicates pass;
- all family cases pass; a family miss is a V5 failure;
- all applicable escapes succeed;
- at least 70 valid escape durations and orbit values exist;
- median escape duration is at most `20.0 s`, p95 at most `45.0 s`;
- median orbit count is at most `1.5`;
- fewer than 5% revisits over all applicable successful cases;
- all 70 unique cases and ten repeats pass recording, sqlite3, completeness,
  collision, cleanup, final zero, final readiness false, timestamp, causality,
  strict JSON, ownership, and frozen-hash gates;
- zero non-ground contacts;
- all ten repeats match categorical outcomes and the existing numeric
  tolerances;
- two-sided 95% Wilson intervals are reported but do not replace point gates.

These strict gates reflect the user's stated objective: V5 is accepted only
if the robust recovery mechanism is actually exercised and succeeds.

## Workflow commands and artifacts

Extend the existing `validate_robustness` entry point:

```text
v5-prepare
v5-qualify
v5-activation
v5-development
v5-freeze
v5-seal
v5-holdout
v5-validation
v5-reproducibility
v5-report
```

Reuse and parameterize the existing workflow engine; do not copy it.

Tracked terminal artifacts:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_v5_parameter_selection.json
  phase_08_v5_freeze_state.json
  phase_08_v5_acceptance_contract.json
  phase_08_v5_gate_results.json
  phase_08_v5_run_manifest.json
  phase_08_v5_validation_report.md
  phase_08_v5_failure_report.md

docs/codex/gesc_gaussian/handoffs/
  phase_08_5_handoff.md
```

External state lives below:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5/
  workflow_state/v5_<stage>.json
```

Large bags, plots, and logs remain outside Git.

## Qualification

Before Gazebo:

1. require clean Git and empty ROS/Gazebo process sets;
2. validate normal and strict-history Phase 08 implementation context;
3. prove the fresh root is absent and create it transactionally;
4. validate every source count and route-barrier proof;
5. prove all V5 case keys are fresh and formal slots have zero prior
   execution;
6. run the complete retained functional suite;
7. isolated-build the three ROS packages;
8. validate installed V5 resources and entry point;
9. instantiate supervisor/fill graphs and central launch;
10. run installed activation/development dry runs;
11. pass the recorder boundary-finalization smoke;
12. verify disk forecast and empty process sets.

Only a passing immutable qualification may start Gazebo.

## Milestones

### M0 — open V5

Save this Plan, update live status, validate plan/implementation context,
checkpoint, and commit.

### M1 — implement route-barrier truth and retained predicate

Add deterministic truth derivation/validation and runtime
route-blocker-encounter classification inside existing owners. Add focused
unit and retained-analysis tests. Preserve all legacy/V1-V4 behavior.

### M2 — implement and precommit V5 workflow/population

Add V5 specification, CLI, fresh activation/development/candidate/formal
inputs, suite commitment, installed resources, state/hash/report fixes, and
focused tests. Commit exact inputs before runtime observation.

### M3 — prepare and qualify

Create `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v5`
transactionally and pass every source/build/installed/runtime-smoke/dry-run
gate.

### M4 — run ten visible-Gazebo activation cases

Execute serially and retain/analyze each once. `10/10` must pass before
development.

### M5 — run 30 headless development cases

Run all three candidates on the same ten cases. Select exactly one eligible
winner or close V5.

### M6 — freeze and seal

Commit the selected implementation/profile/input freeze, require clean Git,
and seal the new precommitted 70+10 population.

### M7 — run 20 headless holdout cases

All must pass.

### M8 — run 50 headless additional validation cases

All must pass.

### M9 — run ten headless repeats

All categorical and numeric comparisons must pass.

### M10 — terminal closeout

Always generate gate JSON, manifest, report, status, checkpoint, and V5
handoff with exact executed/skipped/not-run counts.

On success only, create a local annotated tag after the terminal tested
commit:

```text
gesc-gaussian-simulation-ready-v5
```

Never move, force, overwrite, or push the tag automatically.

## Bounds and early stops

Every ROS, Gazebo, test, build, and batch command has an explicit timeout or
finite scenario duration.

- Activation: the first valid behavior miss or hard integrity/safety failure
  stops remaining activation and closes V5 before development.
- Development: a hard integrity/safety failure stops immediately; complete
  all candidates otherwise. No eligible candidate closes V5.
- Holdout/validation: because `70/70` is required, the first valid behavior,
  family, route, integrity, or safety miss stops later formal slots.
- Reproducibility: the first mismatch stops remaining repeats.

Infrastructure-invalid replacements retain the V4 caps `1/3/1/2/1`, total
eight, with at most one replacement per slot. Eligibility requires readiness
never true, no nonzero command, no non-`SEARCH` lifecycle, an external startup
cause, and clean retained cleanup evidence.

Free space must remain at least:

```text
25 GiB + 512 MiB x remaining declared slots
```

Retained bags are checked read-only; failed evidence is never repaired in
place.

## Contradictions and corrections

Level A — stop and request direction:

- cost sign/units, controller ownership, canonical topics, shared algorithm,
  physical boundary, compatibility, or the user's two-/three-light obstructing
  objective would have to change;
- a duplicate owner, new package, physical fork, or unavailable required
  dependency becomes necessary;
- overlapping user changes cannot be preserved.

Level B — document, test, checkpoint, and continue:

- bounded truth, scenario, runner, workflow, packaging, evidence, reporting,
  timeout, or performance corrections that preserve the objective and
  predeclared gates.

Level C — close V5 honestly:

- valid activation, candidate, holdout, validation, or reproducibility
  failure;
- route-barrier proof, frozen contract, or denominator cannot be satisfied;
- replacement cap is exceeded.

Do not weaken a gate, rerun a valid behavioral failure, modify committed
geometry after observing V5 behavior, or begin V6 automatically.

## Immediate next criterion

Implement M1 route-barrier truth and its focused tests without creating the
V5 evidence root or launching Gazebo.
