# Phase 08.8 v8.12 Plan — Interior Approach-Anchor Continuation

## Status and authority

**APPROVED BOUNDED GOAL CONTINUATION / FRESH EXPERIMENT VERSION
(2026-07-31).**

The user approved Phase 08.8 implementation, bounded Plan amendments and code
corrections needed during execution, fresh simulation after complete
no-Gazebo qualification, and generation of the standard plots. This subplan
uses that authority after the fixed v8.11 matrix failure retained at commit
`cff0178`.

V8.12 is a new experiment version. It does not retry or reclassify v8.11 seed
`19931`, dispatch v8.11 seeds `19932..19934`, alter the v8.11 secondary
`1/1 + 5/5` pass, or modify V6, historical scenarios, worlds, reports, runs,
bags, plots, and failures. Physical motion remains prohibited in Phase 08.

## Evidence-based correction

V8.11 seed `19931` performed the intended first-candidate detection and fill
design:

```text
convergence confirmed
-> counted candidate one required a fill
-> exactly one valid typed fill created
-> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE transition emitted
-> immediate FAILSAFE before a valid escape interval
```

The exact failure was:

```text
open-field escape approach continuity has no pose outside the frozen exit radius
```

The runtime fill center was `(1.0699606542, 0.7605913521) m`; its exit radius
was `1.3667708294 m`. Among `2,536` pre-escape odometry samples, the farthest
pose was only `1.3155651122 m` from that center. There were zero outside-radius
samples and a `0.0512057172 m` shortfall. The farthest pose still supplied a
finite, well-conditioned measured approach direction toward the fill center:
`(0.8147816323, 0.5797679636)`.

The v8.11 topology preflight admitted the declared `1.25 m` start-to-local
route but did not bind the supervisor's stronger runtime requirement for one
pose outside a data-derived fill radius. This is an approach-history policy
gap between topology, fill geometry, and the supervisor. It is not a wall,
collision, detector, cardinality, affine-disablement, ranking, recorder, or
cleanup failure.

## Scientific and controller boundary

The correction uses only the supervisor's existing time-ordered odometry pose
history, the accepted fill center, and the accepted fill exit radius. It uses
no source coordinate, source role, source intensity, declared global,
aggregate-field solution, room map, Vicon/GPS value, wall sensor, or evaluator
stop coordinate.

The controller continues to know only total source count two for this
experiment. Raw rotational cost remains the ranking owner. Gaussian fill
remains the local-basin memory. Affine assistance and supervisor-owned escape
retain their existing roles. Physical arrival remains operator `Ctrl+C`; no
physical coordinate stop is added.

The v8.12 claim remains limited to the exact executed two-source,
obstacle-free, zero-disturbance, topology-admitted cases. It is not a claim
for arbitrary continuous light fields, unknown source count, coincident or
merged extrema, unresolved cost ties, three lights, noise/delay, walls,
obstacles, or physical-coordinate stopping.

## M8.6 — Legacy-default-off supervisor contract

### Parameters

Extend the existing supervisor owner with exactly these parameters:

```text
open_field_escape_interior_anchor_fallback_enabled:       false
open_field_escape_interior_anchor_min_displacement_m:     0.50
```

Both are public launch parameters with simulation/physical shared-node
semantics. Historical scenarios omit them and retain the exact default-off
path. The fallback may be enabled only when open-field approach continuity,
active-fill transit, affine assistance, and counted-candidate recovery are
already enabled.

### Deterministic selection

Extend `approach_continuity_evidence()` without changing its three-argument
default behavior:

1. validate finite, strictly time-increasing pose history and positive finite
   radii/thresholds;
2. first select the newest pose strictly outside the frozen exit radius,
   exactly as before, with mode `outside_radius`;
3. only if no outside pose exists and the new option is enabled, select the
   farthest pose from the fill center;
4. resolve an exact-distance tie by the earliest history index;
5. require displacement at least the configured `0.50 m` minimum;
6. normalize the anchor-to-fill-center vector and label it
   `interior_farthest`; and
7. return no evidence for empty, nonfinite, unordered, degenerate, or
   below-threshold history, preserving the failsafe.

The original outside-radius path always has priority. Enabling the fallback
does not change a run that already has qualified outside-radius evidence.

### Escape ownership and observability

`_begin_escape()` passes the new policy to the shared helper, then uses the
existing safe-direction, active-fill-transit, repulse, stall, and
supervisor-owned-assist owners unchanged.

For v8.12-enabled runs, the existing `ESCAPE_STARTED` event additionally
records:

```text
approach_corridor_anchor_mode:  0 outside_radius / 1 interior_farthest
```

The existing anchor position, stamp, displacement, history age, exclusion
radius, direction, selected direction, revision, and active-fill fields remain
authoritative. The configuration event records the enabled flag and minimum
displacement. Historical default-off event payloads remain unchanged.

### Scenario/topology binding

Add the two optional launch overrides to the existing schema-v14 owner. When
the fallback is enabled, schema validation requires:

- counted-candidate open-field mode;
- approach continuity, active-fill transit, supervisor-owned assist, and
  affine assistance enabled;
- an explicit positive finite minimum displacement;
- a non-null, valid schema-v14 topology qualification; and
- `topology_qualification.route.start_to_local_m` greater than or equal to
  that minimum.

The route cross-check only proves that a meaningful odometry approach can
exist. The runtime fill-radius/history test remains authoritative. The
topology record and all source data stay evaluator-side and never enter the
controller graph.

Schema v1-v14 inputs that omit the new option must retain their normalized
inputs, case keys, launch commands, and behavior. No schema version bump is
needed because this is an optional, default-off controller policy whose
values are already retained in the frozen-profile case key.

## M8.7 — No-Gazebo qualification

Before any v8.12 Gazebo process:

1. preserve and hash every historical scenario, V6 selection, world anchor,
   v8.11 result, bag, report, and plot;
2. add helper tests for original outside selection, enabled fallback,
   outside priority, exact tie behavior, minimum equality, below-minimum,
   empty, nonfinite, unordered, and zero-displacement histories;
3. replay the exact v8.11 seed-`19931` odometry/fill geometry and prove the
   default returns no evidence while the enabled fallback selects
   `interior_farthest`, displacement `1.3155651122 m`, and direction
   `(0.8147816323, 0.5797679636)`;
4. add supervisor integration tests proving default-off retains the immediate
   failsafe and enabled mode reaches a valid `ESCAPE_REPULSE` interval plus
   `ESCAPE_STARTED` with mode `1`;
5. prove an outside-radius retained fixture still selects mode `0` and keeps
   its direction and ownership evidence;
6. add state-machine parameter type/dependency tests, scenario positive and
   negative route-binding tests, launch construction tests, observability
   tests, and source/install parity tests;
7. create fresh v8.12 visible and matrix scenarios; do not edit v8.11 files;
8. run focused helper, supervisor, state-machine, schema, runner, evaluator,
   detector, fill, controller, analyzer, recording, final-zero, launch,
   legacy, V6, shifted-world, and historical-immutability tests;
9. run the broad ROS-independent suite, fatal changed-file lint, compilation,
   YAML/XML parsing, `git diff --check`, and Phase 08 context;
10. perform a fresh isolated three-package build, installed graph
    construction, source/install parity, and installed dry-runs from `/tmp`;
11. replay retained v8.11 secondary passing bags and the failed seed-`19931`
    bag read-only; no historical result changes;
12. prove no active simulation, analysis, or physical process and no fresh
    v8.12 run root; and
13. write a no-Gazebo report, update live status, checkpoint Phase 08, inspect
    the complete diff, and commit.

No v8.12 Gazebo process is authorized before the qualified implementation is
checkpointed and committed. A separate dispatch boundary is still required.

## M8.8 — Fresh visible corrective probe

Create and freeze:

```text
scenario:   phase08_v8_12_interior_anchor_visible_probe.yaml
seed:       20001
GUI:        true
run root:   phase08_8_12_interior_anchor_probe
start:      (0.0, 0.0)
local:      (0.8838834764831844, 0.8838834764831843), input 533.3333333333334
global:     (3.5, 3.5), input 1600
ratio:      1:3
fallback:   enabled, minimum 0.50 m
```

This matches the v8.11 failed geometry but uses a fresh seed and fresh version.
After a separate checkpointed and committed dispatch boundary:

1. run seed `20001` visibly once, installed and sealed, with no retry;
2. require one valid fill and one complete local recovery;
3. require `ESCAPE_STARTED` with `interior_farthest` mode `1`, anchor
   displacement at least `0.50 m`, and no immediate failsafe;
4. require strict candidate-two raw-cost ranking and the first valid
   post-recovery `0.50 m` proximity sample;
5. require complete recording, final zero, readiness false, cleanup, SQLite
   integrity, and all formal predicates;
6. analyze the summary-owned run exactly once and retain all nine plots; and
7. checkpoint and commit the fixed outcome.

A formal failure closes v8.12. It is retained and not retried or tuned in
place.

## M8.9 — Fresh four-case varied-layout/intensity matrix

Only a passing seed `20001` authorizes one fresh installed serial matrix:

| Seed | Local placement | Local/global input | Expected anchor mode |
|---:|---|---|---|
| `20031` | `(0.8838834765, 0.8838834765)` | `533.3333333333 / 1600` (`1:3`) | either valid mode; interior expected |
| `20032` | `(1.0606601718, 1.0606601718)` | `320 / 1600` (`1:5`) | either valid mode |
| `20033` | `(0.7500000000, 1.2990381057)` | `533.3333333333 / 1600` (`1:3`) | either valid mode |
| `20034` | `(0.8750000000, 1.5155444566)` | `320 / 1600` (`1:5`) | either valid mode |

All use start `(0.0, 0.0)`, global `(3.5, 3.5)`, obstacle-free
zero-disturbance simulation, known source count two, and the unchanged v8.11
topology records plus the new route/fallback cross-contract.

After a separate checkpointed and committed matrix boundary, dispatch all
four in order once, headlessly and serially. Stop at the first formal or
cleanup failure. Do not retry, replace, omit, or tune a dispatched case.

The population gate is:

```text
formal pass:                         4/4
exact one-fill recovery:             4/4
valid anchor mode and displacement:  4/4
escape ownership:                    4/4
strict raw-cost ranking:             4/4
graceful global proximity:           4/4
recording/final-zero/cleanup:         4/4
SQLite integrity:                    4/4
one-time analyses / plots:           4 / 36
```

## M8.10 — Closeout

Close only after every dispatched result and non-dispatched definition is
accounted for, all analyses and plots are retained, historical preservation
still passes, context and diff checks pass, runtime is inactive, and the
final report states the exact tested envelope and exclusions.

The final v8.12 result must distinguish:

- v8.11 secondary fixed-layout repeatability;
- v8.11 broad-matrix failure and root cause;
- v8.12 corrective visible outcome;
- v8.12 varied-layout/intensity population outcome;
- infrastructure completeness versus behavior; and
- simulation evaluator stopping versus physical manual `Ctrl+C`.

No simulation-ready or field-wide robustness tag is implied beyond the exact
passing population.

## Stop conditions

Stop immediately for source/intensity/role/global coordinates entering the
controller graph, Vicon/GPS use, a new motion owner, cost sign/unit drift,
physical motion, historical mutation, overlapping user edits, unbounded
runtime, simulation/physical algorithm divergence, or a fallback that accepts
empty/degenerate history.

Retain and close the current version for any fixed visible or matrix formal
failure, incomplete bag, missing final zero, cleanup contamination, analyzer
ambiguity, or need to change a dispatched case. Safe diagnosis and another
separately planned fresh version remain allowed; in-place retry does not.
