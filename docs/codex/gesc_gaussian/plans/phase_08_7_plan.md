# Phase 08.7 Plan — Corner-Origin Diagonal-Sector Geometry

## Status and authority

**PLAN-ONLY — GEOMETRY APPROVED; IMPLEMENTATION AND EXECUTION NOT YET
AUTHORIZED.**

The user approved the geometry in this Plan on 2026-07-29. This Plan makes the
geometry durable and reviewable without modifying the sealed Phase 08.6
scenarios, world, evidence, results, or handoff. It does not yet authorize
Gazebo execution, physical hardware, a 120-run campaign, Phase 09, or a
simulation-readiness claim.

Before implementation or execution, this Plan still requires a prospective
choice between:

1. first local-recovery episode through resumed `SEARCH`; and
2. stable multi-cycle behavior across the complete recording window.

That choice affects the acceptance window but not the geometry below.

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

Exact positions, ratios, seeds, run count, success window, and stopping rules
belong in an execution amendment. No outcome-derived placement may be added to
the same fixed experiment version.

## Milestones

### M0 — geometry contract

Save this Plan, validate Phase 08 Plan context, update the live status without
reopening V6, checkpoint, and commit the Plan-only boundary.

### M1 — additive world/profile support

After explicit implementation approval, add and test the shifted world and
backward-compatible scenario profile. Instantiate the launch graph and verify
physical wall poses, resolved bounds, fixed points, wall margin, contacts, and
historical case-key immutability. Do not launch a behavioral run.

### M2 — visible geometry probe

After execution approval, commit one fresh two-light case and run one bounded
visible-Gazebo probe. Verify wall placement, robot spawn, light coordinates,
contacts, cleanup, and evidence completeness separately from behavior.

### M3 — fixed spatial suite

Only after M2 passes, commit a fresh multi-position suite covering the approved
sector. Run serially, preserve every attempt, and apply the prospectively
chosen first-episode or full-record contract.

## Stop conditions

Stop before Gazebo if:

- the shifted physical wall faces do not match the declared bounds;
- the robot or global point violates the selected wall margin;
- any local source falls outside the radial or angular sector;
- historical worlds, scenarios, normalized case keys, or evidence are changed;
- the success window is still unresolved;
- a second controller, launch graph, recorder, validator, or algorithm fork
  would be required;
- required contacts or cleanup evidence are unavailable.

