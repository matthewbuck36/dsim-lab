# Phase 08.1 Plan — Activation Failure Diagnosis and Recovery

## Status and authority

This plan is the authorized diagnostic successor to the closed failed Phase 08
v2 activation experiment. Current code, tests, retained v2 bags and reports,
Git state, and completed handoffs remain authoritative. Historical Phase 08 v1
and v2 evidence is read-only and cannot count toward a future acceptance
claim.

Phase 08.1 is engineering development, not acceptance. It may change algorithm
implementation, provisional policy, scenarios, evidence semantics, and
parameters when retained evidence and focused tests justify the change.
Any later acceptance attempt must use a new version, clean commit, sealed
manifest, and fresh evidence root.

## Objective

Resolve the five evidence-backed activation defects without weakening safety or
scientific integrity:

1. eliminate unbounded fill-sample synchronization latency;
2. start rotation-aware goal evidence at entry to `VERIFY_EXTREMUM`;
3. replace unreachable goal activation expectations with calibrated,
   scenario-specific lifecycle expectations;
4. prevent recording readiness before the simulation graph and required data
   publishers are operational;
5. eliminate startup watchdog/pose ordering failures before behavioral time
   begins.

Then prove each correction with offline evidence, focused unit/integration
tests, and the smallest useful bounded simulation probes. Do not dispatch a
large matrix during Phase 08.1.

## Retained evidence diagnosis

### Fill computation and event ordering

In six v2 runs, the fill request was followed by 5.5–15.7 seconds of blocked
computation. `synchronize_samples` sorted all remaining poses for every cost
sample before the estimator filtered to its recent window. The supervisor's
five-second fill-design timeout therefore fired first. Because the fill node
uses a single-threaded executor, its `/clock` processing also stopped; the late
fill and event were emitted with the request-era ROS stamp after newer
supervisor/detector events.

This is one performance/causality defect, not evidence that the completeness
timestamp tolerance should simply be relaxed.

### Goal-contract reachability

The adopted controller contract defines `source_score=1` as the calibrated
near-source sensor condition, not simulation ground-truth global optimality.
The v2 activation suite nevertheless required `GOAL_HOLD` for low, medium,
boundary, and disturbed sources that did not sustain `source_score >= 0.95`.
The low source cannot theoretically reach that threshold under the current
absolute normalization. Ground-truth proximity and controller goal
classification must remain separate.

### Verification boundary

The supervisor currently accumulates per-rotation maxima during `SEARCH`.
The high-source run entered `GOAL_HOLD` too early to contain two complete
post-confirmation rotations plus the configured dwell. Approach evidence must
not classify a converged extremum.

### Simulation readiness

The stalled-assist attempt began parameter capture while
`gazebo_ros2_control` was still initializing and
`/controller_manager/list_controllers` was unavailable. It is an
infrastructure-invalid startup attempt, not a stalled-assist behavioral
outcome.

The recenter/resume attempt entered failsafe before behavioral startup because
the controller watchdog observed missing/stale pose evidence. Readiness must
cover operational data heartbeats and controller/supervisor startup, not only
endpoint existence.

## Research invariants versus provisional policies

Hard invariants:

- preserve cost sign, units, canonical topics, controller ownership, and
  selectable legacy behavior;
- keep simulation and physical algorithm logic shared;
- keep raw sensing and structured observability active;
- publish final zero on invalid data, stop, timeout, exception, and shutdown;
- retain every run and distinguish infrastructure validity from behavior;
- keep formal holdout/acceptance data selection-blind and fixed after freeze;
- do not tag or run physical motion before a declared fixed-profile acceptance
  contract passes.

Provisional, testable policies:

- pure-repulsion-first sequencing;
- exactly one redesign before assisted escape;
- automatic recenter after every escape;
- current estimator, fit, grid, escalation, timeout, and threshold values;
- current fill-retention and merge policy.

The source discussions proposed these mechanisms for testing; they did not make
them immutable research requirements.

## Milestones

### M1 — Durable diagnosis and workflow correction

- Record the retained-evidence diagnosis and v2 acceptance-contract erratum.
- Amend the master/workflow documents so a failed experiment version permits
  versioned diagnosis and correction.
- Remove mandatory fresh chats, verbatim Plan saving, all-history rereads,
  blanket dirty-tree/test-unavailable stops, and the arbitrary file-count cap.
- Preserve physical-safety, evidence-integrity, compatibility, freeze, holdout,
  and no-tag gates.

Exit: documentation checks, context validator tests, `git diff --check`, live
status update, and Phase 08 checkpoint pass.

### M2 — Fill latency correction

- Preselect only samples that could enter the estimator window.
- Replace repeated full-set sorting with deterministic efficient nearest
  one-to-one synchronization while preserving tie rules.
- Add large-input equivalence/latency coverage and measured per-request design
  latency diagnostics.
- Do not increase the five-second timeout merely to conceal avoidable
  computation.

Exit: focused estimator/fill tests pass and representative retained sample
sizes complete comfortably below the current timeout.

### M3 — Verification-boundary correction

- Reset rotation evidence on entry to `VERIFY_EXTREMUM`.
- Accumulate valid scores only while verifying.
- Prove that SEARCH-era maxima cannot satisfy goal classification.
- Check the verification timeout against required rotations plus dwell.

Exit: state-machine and synthetic ROS integration tests pass.

### M4 — Readiness and evidence semantics

- Add a bounded simulation readiness barrier covering controller-manager
  availability and required data heartbeats before parameter capture and
  motion readiness.
- Retain objectively infrastructure-invalid attempts and permit at most one
  identical, predeclared replacement attempt in development; never replace a
  valid behavioral failure.
- Report infrastructure invalidity separately.
- Validate typed timestamp monotonicity at the correct producer/stream
  granularity; retain source/request causality separately from emission and bag
  receipt time.

Exit: recorder/scenario tests cover slow startup, disappearing services,
multi-producer events, and readiness remaining false.

### M5 — Scenario-contract correction

- Replace impossible low/medium `GOAL_HOLD` proofs with explicit
  undesired-minimum classification/fill cases.
- Retain at least one calibrated goal case known to sustain the goal threshold.
- Make every expected and forbidden state/event scenario-specific.
- Require timing-sufficient rotation/hold configuration for GOAL and
  undesired-minimum classification cases; allow a timing-insufficient
  configuration only for a case explicitly declared to expect safe timeout.
- Keep controller success and simulation ground truth as separate metrics.

Exit: schema/dry-run checks pass and every activation expectation has a
documented reachability argument.

### M6 — Minimal runtime probes

Run serial, headless, finite simulation probes under a fresh development-only
root. Start with:

1. one calibrated goal-verification case;
2. one local-minimum fill/escape case;
3. one deliberately slow-start readiness case if unit/integration evidence is
   insufficient.

Each probe is declared before execution, retained regardless of outcome,
analyzed once, and followed by cleanup verification. Add another probe only
when the previous evidence identifies a distinct unresolved question.

Exit: corrected contracts are observed without timestamp regression,
pre-readiness motion, orphaned processes, collision, or missing final zero.

### M7 — v3 recommendation

Write a Phase 08.1 handoff that either:

- recommends a new v3 development/tuning design and machine-readable acceptance
  contract; or
- reports the remaining failure and the smallest next diagnostic change.

Do not execute v3 tuning, holdout, unique validation, reproducibility, tagging,
or physical motion in this milestone.

## Future acceptance requirements

Before a new formal attempt:

- freeze one code commit and parameter file;
- seal a machine-readable contract containing all thresholds and its hash;
- declare the unique-case denominator, family allocations, holdout subset,
  repeat set, minimum metric denominators, invalid-attempt policy, and exact
  pass/fail/N/A semantics;
- include the contract hash in the manifest, gate JSON, and report;
- use `outcome: not_run` and `passed: null` for gates never evaluated;
- preserve v1/v2/v2.1 development roots and exclude them by hash/path.

The historical v2 values conflict between its plan and generated gate
artifacts. That contradiction is documented as historical errata and is not
silently rewritten.

## Stop conditions

Stop for a Level A change to cost sign/units, canonical ownership, shared
simulation/physical semantics, physical safety, or preservation of unrelated
work. Stop a runtime probe on cleanup failure, duplicate publisher ownership,
corrupt recording, missing final zero, collision where forbidden, or
unbounded execution.

A failed focused test or probe is evidence for another bounded diagnostic
iteration; it is not permission to relabel v2 or weaken a future frozen gate.

## Required reporting

Maintain `docs/codex/gesc_gaussian/status/phase_08_status.md` and run
`checkpoint_phase.sh 08` at material evidence or independently reviewable
implementation boundaries. Report exact focused/global/skipped/unexecuted
totals, inherited lint debt separately, retained artifact paths, current Git
state, and physical work not performed.
