# Phase 08.8 v8.11 Plan — Topology-Bound Counted-Candidate Continuation

## Status and authority

**APPROVED GOAL CONTINUATION / PLAN AMENDMENT (2026-07-31).**

The user approved Phase 08.8 implementation, bounded Plan amendments and code
corrections needed during execution, simulation execution after no-Gazebo
qualification, and generation of trajectory/cost plots. This subplan resumes
that still-active objective after the bounded v8.10 closeout at commit
`5d76841`.

This is a fresh experiment version. It does not reopen or relabel the fixed
v8.10 secondary formal failure, overwrite the Phase 08.8 closeout, add to a
historical denominator, or change V6 or any historical scenario, run, report,
bag, plot, world, or result. Physical motion remains prohibited in Phase 08.

## Evidence-based correction

The retained v8.10 secondary seed `19851` completed the intended scientific
behavior:

```text
first candidate confirmed
-> exactly one typed fill created at that candidate
-> direct measured local recovery
-> second candidate strictly ranked from raw rotational cost
-> GOAL_REACHED / GOAL_HOLD
-> final global distance 0.105549 m
```

Its formal failure was caused by evaluator topology. The first convergence and
fill were only `0.007887 m` apart, but the convergence was `0.757061 m` from
the declared local lamp, beyond the frozen `0.60 m` lamp-association gate. In
an overlapping direct-light field, the robot detects and orbits the aggregate
signal field; a confirmed candidate need not be centered on one lamp.

V8.11 corrects only that evaluator mismatch. The controller still receives
only onboard raw cost, wheel odometry/IMU-derived pose already used by GESC,
the typed fill registry, and total source count. It receives no light
coordinate, intensity, role, aggregate-field solution, global pose, room map,
Vicon value, or evaluator stop distance.

## Scientific claim boundary

The literal claim “any light position or intensity” is impossible over an
unbounded continuous domain. Coincident sources, zero or nonfinite strength,
merged fields with only one observable extremum, an unresolved raw-cost tie,
or a source outside the finite test horizon cannot support a two-extremum
local-recovery demonstration.

The v8.11 claim is therefore limited to the exact executed two-source,
obstacle-free, zero-disturbance envelope admitted by the deterministic
topology preflight below. Every admitted and dispatched case must pass once;
no dispatched case may be retried, omitted, or relabeled based on outcome.
Rejected candidate definitions remain recorded as outside the admitted
observable topology, not as algorithm passes.

No wall, obstacle, collision-avoidance, unknown-source-count, three-light,
noise/delay, arbitrary continuous-domain, or physical-coordinate-stop claim is
made. Physical arrival remains manual operator `Ctrl+C`.

## M8.1 — Schema-v14 evaluator topology contract

Extend the existing owners rather than adding a controller, planner, launch
graph, recorder, or analyzer.

### Deterministic two-source topology qualification

Add one pure evaluator function to
`scenario_runner/aggregate_field_truth.py`. Given the declared sources,
start, bounds, disturbance record, local/global evaluator IDs, and the same
authoritative light/sensor model used by simulation, it produces a canonical,
hashed record with:

- exactly two unique, positive, finite source inputs;
- source/model/sensor-geometry/start/bounds/disturbance hashes;
- a deterministic local search around each declared source using the existing
  authoritative scalar cost owner and fixed optimization settings;
- the non-global basin position, yaw, raw cost, score, source distance, and a
  `0.50 m` ring-depth proof;
- the global candidate position, yaw, raw cost, score, and source distance;
- finite basin separation and strict raw-cost ordering;
- start-to-local and local-to-global route geometry used only to define the
  admitted experiment envelope; and
- one result hash over the complete record.

Freeze these admission thresholds before any Gazebo run:

```text
local/global source count:                 exactly 2
minimum source input:                      > 0 and finite
local search half-width:                   0.40 m
local grid points per axis:                9
local yaw grid spacing:                    5 degrees
ring radius / position samples:            0.50 m / 48
ring yaw spacing:                          2 degrees
minimum noise-adjusted local basin depth:  0.05 raw-cost units
local noise-adjusted source-score upper:   < 0.95
global noise-adjusted source-score lower:  >= 0.95
minimum local/global raw-cost separation:  0.05
minimum basin-center separation:           1.00 m
maximum start-to-local distance:           1.75 m
minimum global/start distance advantage:   1.50 m farther than local
minimum forward route alignment:           +0.80
valid-domain wall margin for preflight:     0.35 m
```

The topology solver is evaluator-only. The scenario launcher must continue to
pass only `known_source_count=2`, never the topology record or any field
geometry, into the ROS controller graph.

### Schema-v14 binding

Add `topology_qualification` to `success.staged_recovery` for schema v14.
For counted-candidate open-field cases using
`local_association_mode: verified_trap`, schema v14 must require a non-null
record, validate its canonical hash and every binding against the resolved
sources/start/bounds/disturbances/model/sensor inputs, and retain it in the
deterministic case key. Missing, stale, malformed, topology-failing, or
controller-forwarded qualification data is a resolution failure.

Schema versions v1 through v13, including historical `verified_trap` cases,
must retain their exact normalized inputs and behavior.

### Runtime association semantics

Use the existing `verified_trap` counted-candidate evidence contract. For the
one expected local candidate it requires:

1. one unique preceding `CONVERGENCE_CONFIRMED` event;
2. exactly one created, typed, and active fill cluster;
3. fill-to-convergence distance at most `0.50 m`;
4. convergence at least `0.75 m` from the declared global source;
5. one complete accepted direct or assisted local-recovery state/event path;
6. no second fill; and
7. later strict raw-cost ranking and `GOAL_REACHED` before the independent
   post-recovery global-proximity sample.

The individual local-lamp distance remains a diagnostic but is not a gate.
The schema-bound topology qualification prevents this from becoming a
topology-blind relaxation. Live stopping and offline classification must call
the same shared Stage A evidence function.

## M8.2 — No-Gazebo qualification and retained replay

Before any v8.11 Gazebo process:

1. preserve and hash every historical scenario and the fixed v8.10 result;
2. add positive, binding-drift, topology-rejection, model/sensor-drift,
   source-count, intensity, ring-depth, raw-order, separation, route, and
   controller-nonleak tests;
3. prove schema v1-v13 compatibility and default behavior;
4. replay all eleven retained passing v8.10 primary bags through the shared
   Stage A function and prove the v8.11 association still passes;
5. replay retained secondary seed `19851` and prove v8.11 Stage A, exact
   one-fill cardinality, strict ranked goal, and post-Stage-A `0.50 m`
   proximity evidence pass while its immutable v8.10 formal result remains
   failed because its original live process did not perform a graceful
   proximity stop;
6. add fresh schema-v14 secondary visible/repeat scenarios with controller,
   sources, start, world, profile, time budgets, stop radius, final-zero,
   recorder, cleanup, and plot contract copied from v8.10;
7. run focused schema, runner, validator, analyzer, state-machine,
   supervisor, detector, fill, launch, legacy, V6, shifted-world, recording,
   final-zero, and historical-immutability tests;
8. run the broad ROS-independent suite, fatal lint for changed Python,
   compilation, YAML/XML parsing, `git diff --check`, and Phase 08 context;
9. perform a fresh isolated three-package build, installed launch
   instantiation, source/install parity checks, and installed dry-runs from
   outside the repository without creating run roots;
10. prove no active ROS/Gazebo/analysis/physical process and no pre-existing
    fresh run root;
11. write a no-Gazebo qualification record, update live status, checkpoint
    Phase 08, inspect the complete diff, and commit.

No v8.11 Gazebo process is authorized before that qualified committed
boundary.

## M8.3 — Fresh secondary-layout qualification

Create and freeze:

```text
phase08_v8_11_secondary_visible_probe.yaml
  seed:       19901
  GUI:        true
  run root:   phase08_8_11_secondary_probe

phase08_v8_11_secondary_repeats.yaml
  seeds:      19911 through 19915
  GUI:        false
  run root:   phase08_8_11_secondary_repeats
```

Both use the fixed secondary layout:

```text
start:   (0.0, 0.0)
local:   (0.5740251485476348, 1.38581929876693), input 400
global:  (3.5, 3.5), input 1600
```

After a separate committed dispatch boundary:

1. run seed `19901` visibly once, sealed from external DDS monitors, with no
   retry;
2. require a formal pass, complete recording, final zero, cleanup, strict
   raw-cost ranking, exact one-fill cardinality, valid topology hash, graceful
   post-recovery `0.50 m` stop, and all nine plots;
3. checkpoint and commit that result;
4. only then run `19911..19915` serially/headlessly, stopping at the first
   failure and never retrying;
5. analyze each dispatched complete run exactly once using its
   summary-owned run path; and
6. require `5/5` formal passes before the broader matrix.

Every command remains bounded by the scenario timeouts. A failed fixed run is
retained and closes this versioned gate; a correction requires another
reviewed version.

## M8.4 — Sealed varied-layout/intensity matrix

After `1/1 + 5/5` fresh secondary passes, run exactly these four predeclared
headless cases once each, with global source `(3.5, 3.5)` at input `1600`,
start `(0.0, 0.0)`, fresh seeds `19931..19934`, and the unchanged v8.11
controller/evidence profile:

| Seed | Local polar placement | Local Cartesian placement | Input ratio local:global |
|---:|---:|---:|---:|
| `19931` | `r=1.25 m`, `45 deg` | `(0.8838834765, 0.8838834765)` | `533.3333333333:1600` (`1:3`) |
| `19932` | `r=1.50 m`, `45 deg` | `(1.0606601718, 1.0606601718)` | `320:1600` (`1:5`) |
| `19933` | `r=1.50 m`, `60 deg` | `(0.7500000000, 1.2990381057)` | `533.3333333333:1600` (`1:3`) |
| `19934` | `r=1.75 m`, `60 deg` | `(0.8750000000, 1.5155444566)` | `320:1600` (`1:5`) |

All four must pass the frozen topology preflight before the scenario file is
committed. Once committed, dispatch all four in order, once each, with no
retry or outcome-based omission. The population gate is `4/4` formal passes,
`4/4` strict rankings, `4/4` exact one-fill recoveries, `4/4` graceful global
stops, `4/4` recording/final-zero/cleanup, and `36/36` plots.

If a topology definition fails before dispatch, record it outside the
admitted set and do not substitute another case without a new committed Plan
amendment. If a dispatched case fails, retain it as a failed v8.11 result and
stop broad-claim closeout; do not tune or retry it in place.

## M8.5 — Analysis, plots, and closeout

For every new complete run, use the existing Phase 08 analyzer exactly once
and retain its nine standard plots, including trajectory, raw/modified cost,
controller state, events, fill geometry, command contributions, and staged
recovery diagnostics. Record the exact summary, run directory, analysis
directory, plot paths, hashes, and concise metrics in live status and a new
v8.11 report.

Close only after:

- secondary visible/repeats and the entire admitted matrix have their fixed
  outcomes;
- every dispatched recording, final-zero, cleanup, SQLite integrity, and
  analysis result is accounted for;
- all historical preservation checks still pass;
- the final report states the exact tested layout/intensity envelope and all
  exclusions;
- Phase 08 context, focused/broad regression, source/install parity,
  `git diff --check`, inactive runtime, and material checkpoint pass; and
- the reviewed report/status/checkpoint boundary is committed.

No simulation-ready tag is implied. No physical coordinate stop may be added;
the physical robot continues until operator `Ctrl+C`.

## Stop conditions

Stop immediately for a source/intensity/role/global coordinate entering the
controller launch graph, a new motion owner, cost sign/unit drift, physical
motion, Vicon/GPS use, historical mutation, overlapping user changes, or
simulation/physical algorithm divergence.

Retain and close the current experiment version for any fixed visible,
repeat, or matrix formal failure; topology hash/binding drift; incomplete bag;
missing final zero; contaminated cleanup; analyzer ambiguity; or need to
change a dispatched case. Safe diagnosis and a separately planned fresh
version remain allowed under the user's bounded-correction authority.
