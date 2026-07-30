# Phase 08.7 Plan — Corner-Origin Diagonal-Sector Geometry

## Status and authority

**M1 IMPLEMENTED AND QUALIFIED; M2 EXECUTED AND RETAINED;
M3 AND LATER EXECUTION NOT AUTHORIZED.**

The user approved the geometry in this Plan on 2026-07-29. M1 was implemented,
qualified without Gazebo execution, checkpointed, and committed at `7c87e5a`.
The user separately authorized the one-run M2 visible geometry probe on
2026-07-29. That one attempt is complete: geometry/infrastructure, Stage A,
and exact fill cardinality passed; Stage B and the combined behavioral result
failed. It was not retried. This authority does not extend to M3, physical
hardware, a 120-run campaign, Phase 09, or a simulation-readiness claim, and
it does not modify the sealed Phase 08.6 scenarios, world, evidence, results,
or handoff.

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

The completed result is retained in
`docs/codex/gesc_gaussian/validation/
phase_08_7_m2_geometry_probe_report.md`. Its combined result is a failure, so
the M3 prerequisite below is not established.

## M2.1 correction amendment

On 2026-07-29 the user authorized a bounded correction of the retained M2
failure before M3. M2 remains immutable and failed. M2.1 is a fresh development
experiment version; it cannot relabel M2, count toward M3, or weaken the exact
one-fill topology.

The correction extends the existing convergence detector, supervisor, modified
cost owner, central launch graph, scenario runner, and current test owners. It
must not add another controller, state owner, launch graph, recorder,
validator, or simulation/physical algorithm fork.

### Detector lifecycle and motion qualification

The new behavior is opt-in and robust-profile-only:

- consume the existing typed `AlgorithmState`;
- process convergence only during a valid `SEARCH` epoch;
- reset the detector's history age, decay reference, crossing state, and
  counter on each entry into `SEARCH`;
- require the existing fresh-history delay after every reset;
- require at least `0.20 m` of analyzed path and a maximum
  net-displacement/path-length ratio of `0.35` before a crossing may decrement
  the convergence counter;
- retain the existing mean-position metric, event types, topics, units, and
  legacy behavior when the new gate is disabled.

Returning from verification to `SEARCH` provides the cooldown: the detector
must reacquire a completely fresh SEARCH-only epoch before another confirmed
event.

### Topology-aware supervisor recovery

The supervisor receives the same maximum-fill value already passed to the fill
owner. When post-recovery guidance is enabled and the active fill count equals
the nonzero configured maximum:

- a verified high source score retains the existing goal path;
- a verified low source score does not request another fill;
- the supervisor returns to `SEARCH`, re-arms bounded guidance, and records the
  topology-exhausted transition reason;
- at most three such post-recovery retries are allowed before an honest
  `FAILSAFE`;
- unexpected fill-design rejection, invalid geometry, stale data, controller
  faults, timeouts, and other existing safety failures remain failures.

This prevents the expected exact-cardinality boundary from becoming an
avoidable `FILL_REJECTED -> FAILSAFE` chain. Increasing
`gaussian_fill_max_fills` is forbidden.

### Bounded post-recovery affine guidance

For M2.1 only, affine evaluation is enabled. After the final local escape and
recenter:

- `SEARCH` retains the accepted fill identity and publishes
  `(raw, Gaussian, affine) = (1, 1, 1)` while guidance is authorized;
- the affine direction is selected by the existing wall/fill-safe selector
  from the current pose away from the accepted fill;
- each topology-exhausted retry creates a new direction revision;
- the affine term is bounded to `60.0 s`, retains the current gain and sign,
  and is cleared outside authorized assisted escape or post-recovery SEARCH;
- raw GESC, the accepted Gaussian fill, and the existing sole `/cmd_vel` owner
  remain unchanged.

The known global coordinates remain acceptance-only ground truth. They are not
provided to the detector, supervisor direction selector, modified-cost node, or
controller.

### Relaxed operator-equivalent stop

M2.1 and any later Phase 08.7 experiment derived from this correction use a
committed post-Stage-A global-proximity radius of `0.60 m`. The historical M2
radius and result remain `0.35 m` and failed.

The first valid, recorded, noninterpolated post-Stage-A odometry sample within
the M2.1 radius triggers the existing scenario-runner graceful stop. It does
not require global convergence confirmation, `GOAL_REACHED`, `GOAL_HOLD`, or a
stationary dwell. This is the simulation equivalent of the user's permitted
physical `Ctrl+C` after observing sufficiently close global arrival. A future
physical workflow must distinguish an explicitly recorded operator-success
stop from a safety or abort stop; Phase 08 does not authorize hardware.

### Qualification and execution boundary

Before Gazebo, M2.1 must pass:

1. detector SEARCH-epoch/reset and translation/orbit qualification tests;
2. topology-exhausted supervisor replay of the retained M2 failure sequence;
3. bounded post-recovery affine authorization, sign, revision, and expiry
   tests;
4. schema/runner tests for the fresh `0.60 m` stop contract;
5. focused supervisor, convergence, scenario, legacy, V6, shifted-world,
   final-zero, and launch-instantiation regressions;
6. Phase 08 context validation, diff inspection, live-status update, and
   checkpoint.

Only after those gates pass may the exact fresh M2.1 scenario bytes and clean
Git commit be used for one bounded visible-Gazebo probe. The run must use the
same geometry, sources, seed, fill cardinality, wall margin, and bounded
durations as M2, with only the declared correction controls and `0.60 m` stop
radius changed. Its new evidence root is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_1
```

The exact suite, case key, scenario SHA-256, commit, and run command must be
recorded before dispatch. The attempt is retained without automatic retry.
M3 remains unauthorized unless M2.1's Stage A, Stage B, exact cardinality,
infrastructure, and combined results all pass.

The qualified M2.1 input is frozen as:

```text
suite:              phase08_v7_m2_1_correction_probe
experiment version: phase08-v7-m2.1
case:               v7_m2_1_diagonal_r1p5_h25_18001
case key:           2db8a5e49c8068373c22c621be13506419f9f2d7364ec50274f9f7d9895840eb
partition:          development
run count:          1
Gazebo presentation: visible GUI
seed:               18001
start:              (0.0, 0.0), yaw 0
local:              (1.0606601717798212, 1.0606601717798212)
local input:        400.0 nominal relative lumens
global:             (3.5, 3.5)
global input:       1600.0 nominal relative lumens
known topology:     1 local, 1 global
maximum fills:      1
detector gate:      SEARCH-only, 0.20 m path, 0.35 efficiency
affine guidance:    enabled, 60.0 s maximum age
recovery retries:   3
wall margin:        0.20 m
global proximity:   0.60 m
run timeout:        360 s
wall timeout:       540 s
shutdown grace:     45 s
```

The exact scenario is
`ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
phase08_v7_m2_1_correction_probe.yaml`, SHA-256
`541194d6152a8384c469f5bcc8573aef9afdb295bde6e148e5a82a692b8e4c8b`.
Any subsequent byte change requires recomputing this hash, repeating the full
no-Gazebo qualification, updating this amendment, and committing before
dispatch.

## M2.2 evidence-calibrated detector amendment

The fixed M2.1 experiment is closed and immutable as failed. Its
infrastructure passed, but it remained in `SEARCH` for the full run because
the frozen `0.35` maximum path efficiency prevented any convergence candidate.
M2.2 is a fresh development version, not an M2.1 retry or relabel.

Read-only replay establishes the bounded correction:

- the three retained M2 candidates that successfully identified the intended
  local had efficiencies `0.3639431494`, `0.4434453791`, and `0.3605826563`,
  all above the M2.1 cap;
- M2.1 reached within `0.0539395645 m` of the intended local and traveled
  `22.0617045159 m`, but its qualified windows fragmented, its minimum metric
  remained `+0.0657099110`, and its counter remained `3`;
- replay of the exact M2.1 PDE path with a `0.50` cap yields three candidates
  at `172.9`, `198.9`, and `220.7 s`, whose recent-window means are `0.19395`,
  `0.35529`, and `0.04452 m` from the local;
- the replay yields no candidate before `172.9 s`, and `0.50` remains
  materially below straight-line efficiency `1.0`.

M2.2 therefore changes only
`convergence_maximum_path_efficiency: 0.35 -> 0.50`. It retains byte-for-byte
implementation behavior and every other M2.1 scenario value:

- SEARCH-only typed state gating and fresh-history reset;
- minimum analyzed path `0.20 m`;
- shifted world, bounds, start, sources, hue ratio, and seed;
- exact one-fill known topology;
- three topology-exhausted retries;
- bounded `60.0 s` post-recovery affine guidance with gain `0.5`;
- `0.60 m` first-sample operator-equivalent global stop;
- visible GUI and the existing run, wall, and shutdown bounds.

No controller, state owner, recorder, validator, topic, interface, launch
owner, cost sign/unit, global-coordinate algorithm input, historical scenario,
V6 artifact, or physical fork changes.

Before Gazebo, M2.2 must pass:

1. a strict scenario comparison proving that the efficiency cap is the only
   behavioral difference from M2.1;
2. launch resolution proving the exact `0.50` binding while all topology,
   affine, geometry, and stop controls remain unchanged;
3. the complete schema/runner, detector/supervisor, legacy/V6, recording,
   final-zero, and shifted-world regression sets already required for M2.1;
4. installed dry-run and nonexecuting launch instantiation;
5. source/install hash identity, Phase 08 context validation, diff inspection,
   live-status update, checkpoint, and clean commit.

Only then may one bounded visible-Gazebo M2.2 attempt use the fresh root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_2
```

The attempt is retained without automatic retry. M3 remains unauthorized
unless M2.2 independently passes infrastructure, Stage A, Stage B, exact
cardinality, collision, forbidden-state/event, and combined predicates.

The M2.2 input is frozen as:

```text
suite:              phase08_v7_m2_2_efficiency_correction_probe
experiment version: phase08-v7-m2.2
case:               v7_m2_2_diagonal_r1p5_h25_18001
case key:           5078f6eff97d05419af1c59452fba15fb31b34c496e80f5ab3063ac091520e90
partition:          development
run count:          1
Gazebo presentation: visible GUI
seed:               18001
start:              (0.0, 0.0), yaw 0
local:              (1.0606601717798212, 1.0606601717798212)
local input:        400.0 nominal relative lumens
global:             (3.5, 3.5)
global input:       1600.0 nominal relative lumens
known topology:     1 local, 1 global
maximum fills:      1
detector gate:      SEARCH-only, 0.20 m path, 0.50 efficiency
affine guidance:    enabled, 60.0 s maximum age
recovery retries:   3
wall margin:        0.20 m
global proximity:   0.60 m
run timeout:        360 s
wall timeout:       540 s
shutdown grace:     45 s
```

The exact scenario is
`ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
phase08_v7_m2_2_efficiency_correction_probe.yaml`, SHA-256
`1f11448b37ef8fbfb146124a0141d91d3404ee614d6d33e3a30f58aa0a179439`.
Any byte change requires a new hash and repetition of the no-Gazebo boundary.

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

### M2.1 — bounded integration correction

After explicit correction approval, implement and qualify the opt-in detector,
topology, affine-guidance, and relaxed-stop amendment above. Preserve and
replay M2's failure evidence, checkpoint and commit the qualified correction,
then run exactly one fresh bounded visible probe.

### M3 — fixed spatial suite

Only after the current prerequisite probe passes, commit a fresh multi-position
suite covering the approved sector. Run serially, preserve every attempt, and
apply the prospectively approved Stage A, Stage B, and combined contracts.

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
