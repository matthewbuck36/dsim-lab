# Phase 08.7 Plan — Corner-Origin Diagonal-Sector Geometry

## Status and authority

**M1 IMPLEMENTED AND QUALIFIED; M2 VISIBLE GEOMETRY PROBE AUTHORIZED;
M3 AND LATER EXECUTION NOT AUTHORIZED.**

The user approved the geometry in this Plan on 2026-07-29. M1 was implemented,
qualified without Gazebo execution, checkpointed, and committed at `7c87e5a`.
The user separately authorized the one-run M2 visible geometry probe on
2026-07-29. This authority does not extend to M3, physical hardware, a
120-run campaign, Phase 09, or a simulation-readiness claim, and it does not
modify the sealed Phase 08.6 scenarios, world, evidence, results, or handoff.

The user resolved the V6 acceptance-window ambiguity on 2026-07-29. Each run
must report local-recovery success separately from post-recovery global
proximity, and end-to-end success requires both. The algorithm may use the
declared number of local and global minima as known topology.

## User-approved coordinate contract

All new GESC/Gaussian simulation tests after V6 use a `4 m x 4 m` room whose
southwest inner corner is `(-0.25, -0.25)`:

```text
x bounds: [-0.25, 3.75] m
y bounds: [-0.25, 3.75] m
room center: (1.75, 1.75) m
```

The fixed robot start is:

```text
position: (0.0, 0.0) m
yaw: 0 rad
```

The fixed stronger global source is:

```text
position: (3.5, 3.5) m
distance from start: sqrt(24.5) = 4.949747... m
```

The robot start and global source are each `0.25 m` from their two nearest
inner wall faces.

## Local-source placement region

The direct start-to-global centerline has polar angle:

```text
theta_center = atan2(3.5, 3.5) = pi/4 = 45 degrees
```

Every new two-light test must place its declared lower-output local source in
the closed annular sector:

```text
1.0 m <= r <= 2.0 m
abs(wrap(theta - pi/4)) <= pi/4
```

For this room and start, the equivalent polar bounds are:

```text
0 degrees <= theta <= 90 degrees
```

and the Cartesian coordinates are:

```text
x_local = r * cos(theta)
y_local = r * sin(theta)
```

This region includes direct-diagonal cases at `theta=45 degrees` and
off-diagonal cases up to `45 degrees` on either side. It is a quarter-annulus,
not a rectangular box. Inclusive boundaries permit cases on the positive
`x` or `y` axes.

Example valid placements, before any suite is frozen:

| Radius | Angle | Approximate `(x, y)` |
|---:|---:|---:|
| 1.0 m | 45° | `(0.707, 0.707)` |
| 1.5 m | 22.5° | `(1.386, 0.574)` |
| 1.5 m | 45° | `(1.061, 1.061)` |
| 1.5 m | 67.5° | `(0.574, 1.386)` |
| 2.0 m | 45° | `(1.414, 1.414)` |

These examples illustrate the region only. Exact development/holdout
coordinates and seeds must be committed before their runs, must include more
than one angle, and must not be selected from observed outcomes.

## Meaning of “local minimum”

Geometry declares a lower-output local **source candidate**. A scenario may
call it an accepted local recovery only when runtime evidence proves that
unchanged GESC converged near that declared source, away from the global
source, and then followed the required Gaussian fill/recovery lifecycle.

An off-diagonal source that the robot never encounters is a valid attempted
placement but not a successful local-recovery case. Direct convergence to the
global source cannot satisfy the local-recovery predicate.

## Known topology and exact fill cardinality

Each scenario declares its extrema before execution:

```text
expected_local_minima
expected_global_minima = 1
```

The initial two-light campaign has:

```text
1 declared local source
1 declared global source
gaussian_fill_max_fills = 1
```

A future three-light campaign may have:

```text
2 declared local sources
1 declared global source
gaussian_fill_max_fills = 2
```

The configured fill limit must equal the declared local-minimum count. This is
an allowed use of known problem topology, not outcome-selected steering.

“One fill” means one unique accepted active fill cluster, established by a
valid `FILL_CREATED` event and typed `GaussianFill` identity. It does not mean
one raw message publication: lifecycle observability may publish multiple
messages for the same identity.

Every accepted local recovery must satisfy all of the following:

- exactly one unique fill cluster is associated with that declared local;
- its causal convergence and fill center satisfy the committed local spatial
  tolerances;
- it is not associated with the global source;
- no other declared local is assigned the same active cluster;
- the escape, recenter, and resumed-search path completes.

For `N` declared locals, the run must create exactly `N` unique local fill
clusters and establish a one-to-one local-source-to-cluster assignment.
Revisions, superseded versions, repeated messages, and `FILL_MERGED` events do
not increment the local-fill count. An extra distinct cluster, a missing
cluster, a fill at the global source, or two locals sharing one cluster fails
the fill-cardinality contract.

Entering global proximity before all `N` local recoveries are complete does
not satisfy the stop boundary or combined result: it does not prove the
required local-minimum escape sequence.

## Two-stage success contract

Every run reports two non-interchangeable results.

### Stage A — local Gaussian recovery

For one declared local, Stage A requires:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

and the causal events:

```text
CONVERGENCE_CONFIRMED
FILL_CREATED
ESCAPE_STARTED
RECENTER_STARTED
RECENTER_COMPLETE
```

The convergence and unique fill must be associated with the declared local,
not the global. Stage A passes as soon as the final required local episode
returns to `SEARCH`. A later global-stage failure does not erase this result;
it makes Stage B and end-to-end success fail.

For two declared locals, the same local-recovery episode must occur twice,
with distinct source assignments and distinct unique fill clusters, before
Stage A passes.

### Stage B — global proximity and operator-equivalent stop

After Stage A, the robot must:

```text
resumed SEARCH
-> approach the declared global
-> enter the committed global-proximity radius
-> graceful stop
```

Stage B requires:

- every required local recovery and unique fill is already complete;
- at least one valid, recorded, noninterpolated odometry sample is within
  `0.35 m` of `(3.5, 3.5)`;
- that sample occurs after Stage A's final resumed `SEARCH`;
- no non-ground collision or evidence-integrity failure occurs before the
  proximity boundary.

The first qualifying post-Stage-A sample triggers the scenario runner's
graceful stop, equivalent to the user's allowed physical `Ctrl+C` after
observing arrival. The recorder and controller still complete their existing
final-zero, final-readiness-false, completeness, and cleanup contracts.

Stage B does **not** require:

- `VERIFY_EXTREMUM` at the global;
- a `GOAL_REACHED` event;
- entry into or persistence in `GOAL_HOLD`;
- a dwell or stationary-observation interval;
- behavior after the proximity boundary.

Internal controller goal classification remains useful diagnostic evidence but
cannot turn an objectively near-enough arrival into a behavioral failure.

### End-to-end result

The combined run passes only when:

```text
Stage A local recovery = PASS
Stage B post-recovery global proximity = PASS
recording/completeness/cleanup/collision evidence = PASS
exact unique fill cardinality = PASS
```

Reports must retain Stage A independently. This prevents a later global-stage
failure from hiding proof that Gaussian local recovery worked while still
making the full navigation result fail honestly.

## Shifted Gazebo room

The current historical validation world has physical wall inner faces at
`x,y = -2.0` and `2.0`. Changing scenario bounds alone would leave those
physical wall collisions in the wrong location.

Implementation must therefore add a separately named corner-origin validation
world. It must not edit or replace
`gesc_gaussian_validation.world`.

The new wall geometry must have inner faces at:

```text
west:  x = -0.25
east:  x =  3.75
south: y = -0.25
north: y =  3.75
```

For the retained `0.10 m` wall thickness, corresponding wall centerlines are:

```text
west:  x = -0.30
east:  x =  3.80
south: y = -0.30
north: y =  3.80
```

The east/west walls are centered at `y=1.75`; the north/south walls are
centered at `x=1.75`. Contacts must remain recorded and evaluated.

## Wall margin

The historical `0.35 m` controller wall margin excludes both `(0,0)` and
`(3.5,3.5)` from the new room's allowed center domain. New corner-origin
scenarios therefore use:

```text
wall_margin_m = 0.20
```

This gives the allowed center domain:

```text
x,y in [-0.05, 3.55]
```

and admits both fixed points while retaining `0.20 m` center clearance.
Historical scenarios retain `0.35 m`.

## Backward-compatible implementation boundary

Implementation must:

- add, not overwrite, the shifted validation world;
- add an explicit scenario world/geometry profile for new scenarios;
- leave absent-profile and schema-v1 through schema-v4 normalization,
  deterministic case keys, launch bytes, and historical worlds unchanged;
- validate the exact room bounds, start, global point, local radius, and local
  angular sector before launch;
- record local radius and angle in resolved metadata;
- declare the known local/global counts and set the maximum unique active fill
  clusters equal to the local count;
- count and spatially associate distinct typed fill clusters rather than raw
  publications;
- expose separate Stage A, Stage B, fill-cardinality, and combined results;
- support a graceful evidence boundary at verified post-recovery global
  proximity;
- keep `custom_controller` as the sole `/cmd_vel` publisher;
- preserve Nick's original GESC, zero-yaw startup, rotating sensor/encoder
  behavior, filters, gains, cost sign/units, topics, and legacy selection;
- use exactly two lights initially, with future three-light support deferred;
- reuse the existing launch graph, scenario runner, recorder, validator,
  analyzer, and typed fill owner.

An additive schema version or explicitly optional profile may be used, but
sealed historical case keys must remain byte-for-byte unchanged.

## Prospective spatial coverage

A future development suite should cover both radial and angular variation,
including:

- at least one direct-diagonal case at `45 degrees`;
- at least one case below the diagonal;
- at least one case above the diagonal;
- more than one radius in the inclusive `1–2 m` band.

Exact positions, ratios, seeds, and run count belong in an execution amendment.
The success window is the approved Stage A plus immediate Stage B
global-proximity boundary above. No outcome-derived placement may be added to
the same fixed experiment version.

## M2 execution amendment

The one authorized M2 run is frozen before execution as:

```text
suite:              phase08_v7_m2_geometry_probe
experiment version: phase08-v7-m2
case:               v7_m2_diagonal_r1p5_h25_18001
case key:           d07a23d9a77f938038fbe58c5d2b312dd5e550394d4f60c56d22d6ead8ca2961
partition:          development
run count:          1
Gazebo presentation: visible GUI
seed:               18001
start:              (0.0, 0.0), yaw 0
local:              (1.0606601717798212, 1.0606601717798212)
local polar point:  radius 1.5 m, angle 45 degrees
local input:        400.0 nominal relative lumens
global:             (3.5, 3.5)
global input:       1600.0 nominal relative lumens
known topology:     1 local, 1 global
maximum fills:      1
wall margin:        0.20 m
global proximity:   0.35 m
run timeout:        360 s
wall timeout:       540 s
shutdown grace:     45 s
```

The exact scenario is
`ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
phase08_v7_m2_geometry_probe.yaml`, SHA-256
`9623b001d91a1216d35c037c2eeb46d4a0f05cdf46d3b3ea68c2b4ad7a0af442`.
The direct-diagonal midpoint is one of the Plan's examples and was selected
before any corner-origin Gazebo outcome. The H25 contrast is a development
diagnostic carried from V6 because it previously exposed the desired
mechanism; it does not change V6 and cannot tune, select, or count toward M3.

M2 has two separately reported outcomes:

1. geometry/infrastructure: shifted wall poses, robot and light spawns,
   contacts endpoint/evidence, recording completeness, final-zero/readiness,
   collision result, and cleanup;
2. behavior: Stage A local recovery, exact fill cardinality, Stage B global
   proximity and graceful stop, and the combined result.

Infrastructure success does not convert a behavioral miss into a pass. A
behavioral pass from this single development probe does not establish
repeatability or simulation readiness. The attempt is retained without
automatic retry regardless of its result.

## Milestones

### M0 — geometry contract

Save this Plan, validate Phase 08 Plan context, update the live status without
reopening V6, checkpoint, and commit the Plan-only boundary.

### M1 — additive world/profile support

After explicit implementation approval, add and test the shifted world and
backward-compatible scenario profile. Instantiate the launch graph and verify
physical wall poses, resolved bounds, fixed points, wall margin, contacts, and
historical case-key immutability. Add the known-topology, exact
fill-cardinality, two-stage result, and global-proximity stop contracts. Do
not launch a behavioral run.

### M2 — visible geometry probe

After execution approval, commit one fresh two-light case and run one bounded
visible-Gazebo probe. Verify wall placement, robot spawn, light coordinates,
contacts, cleanup, and evidence completeness separately from behavior.

### M3 — fixed spatial suite

Only after M2 passes, commit a fresh multi-position suite covering the approved
sector. Run serially, preserve every attempt, and apply the prospectively
approved Stage A, Stage B, and combined contracts.

## Stop conditions

Stop before Gazebo if:

- the shifted physical wall faces do not match the declared bounds;
- the robot or global point violates the selected wall margin;
- any local source falls outside the radial or angular sector;
- historical worlds, scenarios, normalized case keys, or evidence are changed;
- the configured maximum fill count differs from the declared local count;
- distinct fills cannot be associated one-to-one with declared locals;
- a second controller, launch graph, recorder, validator, or algorithm fork
  would be required;
- required contacts or cleanup evidence are unavailable.
