# Phase 08.7 Plan — Corner-Origin Diagonal-Sector Geometry

## Status and authority

**M1 IMPLEMENTED AND QUALIFIED; M2, M2.1, AND M2.2 EXECUTED AND
RETAINED AS FAILED; M2.3 EXECUTED AND RETAINED AS PASSED; M3 EXECUTED
AND RETAINED AS FAILED AT 1/5; M4 RETAINED AS EVIDENCE FAIL;
M4.1 EVIDENCE CORRECTION PASSED AND VISIBLE PROBE RETAINED AS STAGE B
FAIL; M4.2 BEHAVIOR PASSED AND FORMAL EVIDENCE FAILED; M4.3 EXECUTED
AND RETAINED AS A CLEAN TWO-LIGHT BEHAVIORAL FAIL AT 6/8.**

The user approved the geometry in this Plan on 2026-07-29. M1 was implemented,
qualified without Gazebo execution, checkpointed, and committed at `7c87e5a`.
The user separately authorized the one-run M2 visible geometry probe on
2026-07-29. That one attempt is complete: geometry/infrastructure, Stage A,
and exact fill cardinality passed; Stage B and the combined behavioral result
failed. It was not retried. This authority does not extend to M3, physical
hardware, a 120-run campaign, Phase 09, or a simulation-readiness claim, and
it does not modify the sealed Phase 08.6 scenarios, world, evidence, results,
or handoff.

The bounded M2.1, M2.2, and M2.3 corrections were subsequently authorized and
executed as separately versioned fixed experiments. M2.1 and M2.2 remain
failed and immutable. The single M2.3 development probe passed Stage A, Stage
B at the committed `1.20 m` operator-equivalent boundary, exact one-fill
cardinality, collision, recording, completeness, and cleanup predicates. It
establishes the prerequisite for, but does not authorize, M3.

M4 later passed every behavioral predicate but remains a formal evidence
failure. M4.1 corrected that evidence model without relabelling M4: its fresh
probe passed all evidence, Stage A, fill, collision, and cleanup gates but
failed Stage B after looping near the recenter region. No M4 suite or
three-light run was executed. On 2026-07-30 the user authorized a fresh M4.2
correction and its conditional two-light qualification sequence. M4.2 does
not reopen or relabel any prior attempt.

The one fixed M4.2 visible probe subsequently passed Stage A, exact one-fill
cardinality, post-recovery translation, Stage B at `1.20 m`, collision,
final-zero, and cleanup. Its formal result remains failed because two new
supervisor-owned `post-recovery ` configuration events were absent from the
recording validator's closed producer-prefix map. On 2026-07-30 the user
authorized the fresh M4.3 correction below. M4.3 changes evidence attribution
and fresh experiment identity only; it does not alter M4.2 navigation or
acceptance values and does not relabel the immutable M4.2 result.

M4.3 corrected the attribution defect and its visible probe passed. Its
conditional eight-case suite then retained six behavioral passes and two
behavioral failures with complete `48/48` evidence and cleanup in every case.
The corner-radius case entered `FAILSAFE` when a fixed `0.50 m` recenter
lookahead produced no candidate inside a wall/fill pinch. The `22.5 degree`
case completed Stage A but its maximum-clearance post-recovery direction
pointed away from the global route and exhausted the `120.0 s` Stage B
budget. M4.3 is closed and immutable; it does not authorize retries or the
optional three-light probe.

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

## M2.3 assisted-recovery and operator-stop amendment

M2.2 is closed and immutable as failed. It empirically passed the corrected
detector, exact one-cluster topology, local convergence association, assisted
escape, recenter, and post-recovery affine activation. It failed the formal
combined result for two independent evidence-contract reasons:

1. the Stage A reporter and singular controller path accepted only the direct
   `ESCAPE_REPULSE -> RECENTER` topology, although the supervisor legally
   executed its existing one-redesign
   `ESCAPE_REPULSE -> DESIGN_OR_MERGE_FILL -> ESCAPE_ASSIST -> RECENTER`
   branch;
2. the fixed `0.60 m` stop remained unobserved before the controller's
   wall-margin failsafe and later east-wall contact.

The retained M2.2 run proves the bounded stop correction. After assisted
recovery and recenter, the first noninterpolated odometry sample within
`1.20 m` of the global occurred at ROS time `306.030 s`, pose
`(3.369462640, 2.308150068) m`, actual distance `1.198977173 m`. At that
sample the robot remained `0.180537360 m` inside the east controller inset.
The wall-margin failsafe followed `4.77 s` later and first east-wall contact
approximately `5.85 s` later.

M2.3 is a fresh development version, not an M2.2 retry or relabel. It preserves
every M2.2 algorithm and launch value while making only these two corrections:

- schema-v5 scenarios may add `controller.required_state_paths`, whose first
  path must equal the existing singular `required_state_path`; the declared
  paths must be nonempty, unique, transition-valid, and classify the first
  verification identically;
- the Phase 08.7 staged reporter, live monitor, controller predicate, and
  scoped result evaluation accept either of the two exact legal paths:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

or:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_ASSIST
-> RECENTER
-> SEARCH
```

- the opt-in post-recovery-guidance profile permits a prospectively declared
  proximity from `0.60 m` through the evidence-backed `1.20 m` ceiling;
- staged and ground-truth proximity declarations must remain identical;
- M2.3 fixes both declarations at exactly `1.20 m`.

Absent `required_state_paths`, schema-v5 normalization and singular-path
evaluation remain unchanged. Schema-v1 through schema-v4 reject the new field.
Post-recovery guidance disabled retains the original exact `0.35 m` geometry
profile boundary. M2.1 and M2.2 remain exact `0.60 m` inputs. Historical case
keys, scenario/world bytes, V6 evidence, topics, controller ownership,
cost signs/units, and algorithm behavior remain unchanged.

Before Gazebo, M2.3 must pass:

1. direct and assisted Stage A episode tests, exact fill-cardinality tests,
   and live graceful-stop tests for both legal paths;
2. schema rejection of empty, duplicate, unreachable, misclassified, or
   singular-path-inconsistent alternatives;
3. schema rejection of stop mismatches, radii below `0.60 m`, and radii above
   `1.20 m`;
4. strict comparison proving all M2.2 launch arguments and algorithm inputs
   are unchanged;
5. complete schema/runner, detector/supervisor, legacy/V6, recording,
   final-zero, shifted-world, and Phase 08 validation regressions;
6. isolated build, installed dry-run, nonexecuting launch instantiation,
   source/install hash identity, context validation, diff inspection,
   live-status update, checkpoint, and clean commit.

Only after those gates pass may one bounded visible-Gazebo M2.3 attempt use:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_3
```

The attempt is retained without automatic retry. M3 remains unauthorized
unless M2.3 independently passes infrastructure, Stage A, Stage B, exact
cardinality, collision, forbidden-state/event, and combined predicates.

The M2.3 input is frozen as:

```text
suite:              phase08_v7_m2_3_assisted_recovery_stop_probe
experiment version: phase08-v7-m2.3
case:               v7_m2_3_diagonal_r1p5_h25_18001
case key:           13cf3a091db9f9e72fff3abc0c1885b4e64033766f5317ee628490e468e10cbd
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
recovery paths:     direct or one-redesign assisted
affine guidance:    enabled, 60.0 s maximum age
recovery retries:   3
wall margin:        0.20 m
global proximity:   1.20 m
run timeout:        360 s
wall timeout:       540 s
shutdown grace:     45 s
```

The exact scenario is
`ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
phase08_v7_m2_3_assisted_recovery_stop_probe.yaml`, SHA-256
`f03db4462527620321eb299656d9f56fe32e10362664e595f7d3850fc3f53eca`.
Any byte change requires a new hash and repetition of the complete no-Gazebo
boundary.

## M2.3 execution result

The one predeclared visible-Gazebo M2.3 attempt passed. It confirmed the
intended local at `(1.3938876873, 1.1160647584) m`, created exactly one typed
fill cluster centered at `(1.3945263243, 1.2521809924) m`, completed the
direct legal escape/recenter path, and returned to `SEARCH`. The staged
reporter correctly retained Stage A.

Post-recovery affine guidance was active with
`(sensor, Gaussian, affine) = (1, 1, 1)`. After Stage A and exact-cardinality
completion, the live monitor stopped on the first noninterpolated sample
within `1.20 m` of the declared global:

```text
position:           (3.4433011933, 2.3021489031) m
distance to global: 1.1991922303 m
interpolation used: false
collision observed: false
```

Recording, final-zero, final-readiness-false, validation, sqlite integrity,
analysis, and cleanup all passed. The runner exited `0`, all declared
classification predicates are true, and the combined result is **PASS**.
The controller-goal diagnostic remains false because the operator-equivalent
boundary intentionally does not require `GOAL_REACHED` or `GOAL_HOLD`.

The immutable evidence and full report are retained at:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_3/
docs/codex/gesc_gaussian/validation/
  phase_08_7_m2_3_assisted_recovery_stop_probe_report.md
```

This is one development result, not repeatability or readiness evidence. At
the M2.3 closeout boundary, M3 remained unauthorized.

## M3 stricter-arrival spatial-suite amendment

On 2026-07-30 the user authorized the M3 amendment and its complete execution.
The user judged the M2.3 `1.20 m` stop to be a useful safe approach result but
visually looser than the desired global convergence. M3 therefore makes
`1.00 m` the primary Stage B and combined-success boundary while retaining
`1.20 m` only as a separately reported, non-gating global-region approach
diagnostic.

M3 is a fixed spatial-validation suite, not a tuning sweep. It holds the fresh
Gazebo seed and every M2.3 algorithm, topology, world, start, source-output,
timing, affine, retry, fill, and wall-margin value constant. Only the
prospectively listed local-source position changes across cases. The five
positions are the examples already recorded in this Plan before any
corner-origin outcome:

| Case | Radius | Angle | Exact local `(x, y)` | Seed |
|---|---:|---:|---|---:|
| `v7_m3_r1p0_a45_h25_18101` | 1.0 m | 45° | `(0.7071067811865476, 0.7071067811865475)` | 18101 |
| `v7_m3_r1p5_a22p5_h25_18101` | 1.5 m | 22.5° | `(1.38581929876693, 0.5740251485476346)` | 18101 |
| `v7_m3_r1p5_a45_h25_18101` | 1.5 m | 45° | `(1.0606601717798214, 1.0606601717798212)` | 18101 |
| `v7_m3_r1p5_a67p5_h25_18101` | 1.5 m | 67.5° | `(0.5740251485476348, 1.38581929876693)` | 18101 |
| `v7_m3_r2p0_a45_h25_18101` | 2.0 m | 45° | `(1.4142135623730951, 1.414213562373095)` | 18101 |

This cross covers both approved radial endpoints, the diagonal midpoint, and
equal angular offsets on both sides of the direct start-to-global line. Holding
seed `18101` fixed isolates the spatial-placement question; it does not test
multi-seed repeatability.

Each case retains:

```text
start:                    (0.0, 0.0), yaw 0
global:                   (3.5, 3.5), 1600.0 relative input
local:                    listed point, 400.0 relative input
known topology:           1 local, 1 global
maximum fills:            1
detector gate:            SEARCH-only, 0.20 m path, 0.50 efficiency
recovery paths:           direct or one-redesign assisted
affine guidance:          enabled, 60.0 s maximum age, gain 0.5
recovery retries:         3
wall margin:              0.20 m
primary Stage B radius:   1.00 m
approach diagnostic:      1.20 m
run timeout:              360 s
wall timeout:             540 s
shutdown grace:           45 s
```

### Additive approach diagnostic

Schema-v5 staged recovery may add:

```yaml
global_approach_radius_m: 1.20
```

This field is optional and non-gating. When present:

- post-recovery guidance must be enabled;
- it must be strictly greater than `global_proximity_radius_m`;
- it must not exceed the existing corrected-profile `1.20 m` ceiling;
- the reporter records the first finite, noninterpolated post-Stage-A odometry
  sample inside it;
- the reporter rejects an approach claim if a non-ground collision occurred
  before that sample;
- the live monitor may retain the first approach sample but must continue until
  the primary `1.00 m` boundary, timeout, or safety termination;
- `post_recovery_global_approach` is diagnostic only and cannot satisfy Stage B,
  ground truth, a required predicate, or combined success.

Absent the field, schema-v5 normalization and result shape remain unchanged.
Schema-v1 through schema-v4, all historical scenarios, and every historical
case key remain unchanged.

### Per-case and suite acceptance

Every fixed case receives exactly one attempt. Runs execute serially and
headless because M3 is a batch; failures are retained and do not stop later
cases, while cleanup failure remains a hard dispatch stop.

Per-case combined success requires:

```text
Stage A local recovery = PASS
Stage B post-recovery distance <= 1.00 m = PASS
exact one-fill cardinality = PASS
collision/forbidden-state/event evidence = PASS
recording/completeness/final-zero/cleanup = PASS
```

The `1.20 m` approach diagnostic is reported independently for every case,
including a case that approaches the global region but fails the stricter
primary boundary.

M3 passes only if all five fixed cases pass Stage A, primary Stage B, exact
cardinality, collision, infrastructure, and combined classification. Any
fixed-case miss makes M3 a retained failure; thresholds, positions, seeds, and
algorithm values will not be changed or retried inside M3.

The fresh suite identity is:

```text
suite:              phase08_v7_m3_spatial_suite
experiment version: phase08-v7-m3
partition:          validation
resolved runs:      5
execution:          serial, headless
evidence root:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m3
```

The qualified pre-dispatch identities are:

```text
scenario SHA-256:
  1221d8cb9d7235218d4f3da710f10d41284632a93712bd89d763d938a0437dae

case keys:
  v7_m3_r1p0_a45_h25_18101
    75d0c27b3cf3b0a88aff539723a907d7bd48c26f218eee2baae89487364b1712
  v7_m3_r1p5_a22p5_h25_18101
    67d7c6d4959f5656e81394a31509a4a66a516d4fe3cc4625b91b31e2dbba1d0a
  v7_m3_r1p5_a45_h25_18101
    0bbd09a8898e7bfaafa6fe75b4cd813c286c9d0a378d90df11685393b5100115
  v7_m3_r1p5_a67p5_h25_18101
    474302bb0c69f67e0efe875bc9031a38dc33f4cd89506d615b7a6e3b1804acf1
  v7_m3_r2p0_a45_h25_18101
    94deae52e7c35eb428663e4eb099d8078d23f5dda8561b357998a71d46b43614
```

Before Gazebo, implementation must pass focused schema/runner tests for the
non-gating approach diagnostic, all five exact geometry/case identities,
M2.3 launch-value preservation, historical normalization/case-key
immutability, the complete M2.3 functional regression envelope, isolated
build, installed dry-run, source/install identity, nonexecuting launch
instantiation, context validation, diff inspection, checkpoint, and a clean
commit of the exact suite.

The implementation passes that no-Gazebo qualification boundary. The declared
functional envelope produced `556 passed, 2 skipped, 1 deselected`; the
focused M3/M2.3 contract selection produced `24 passed, 116 deselected`.
Direct compilation, flake8, and pep257 checks pass on all four changed Python
files. A fresh isolated build completed all three packages, the installed
suite resolved the same five case keys with zero unsupported cases, source and
install hashes match, and nonexecuting central-launch description generation
completed without starting Gazebo. The evidence root remained absent and the
Gazebo/runner/recorder process set remained inactive through qualification.

### Retained execution result

The qualified five-case batch executed once and is retained as **FAIL**:

```text
infrastructure / recording / cleanup: 5 / 5
formal Stage A local recovery:         2 / 5
exact associated fill cardinality:    4 / 5
non-gating 1.20 m approach:            2 / 5
primary 1.00 m Stage B:                1 / 5
collision expectation:                 4 / 5
combined success:                       1 / 5
required M3 gate:                       5 / 5
```

The radius-1.0 diagonal case passed end to end. The other cases respectively
failed during a one-sample-short redesign, after passing Stage A and the
`1.20 m` diagnostic but missing `1.00 m` before wall/collision evidence,
after completing a lifecycle outside the declared-local association
tolerance, and during recenter timeout.

All five runs are infrastructure-complete and independently validate and
analyze successfully. No retry or in-suite correction occurred. The immutable
report is
`docs/codex/gesc_gaussian/validation/phase_08_7_m3_spatial_suite_report.md`.

M3 establishes bounded five-position spatial evidence only. It does not
authorize parameter tuning, automatic retries, multi-seed repeatability, the
120-run campaign, physical hardware, Phase 09, or a simulation-readiness
claim.

## M4 recoverable-navigation and two-light-readiness amendment

On 2026-07-29 the user explicitly authorized planning, implementation,
qualification, and execution of Phase 08.7 M4. M4 is a fresh correction
version after the immutable M3 `1/5` result. It may replay M3 evidence
read-only and may use the same geometric positions in new case identities,
but it cannot alter, retry, relabel, or count M3, M2.3, V6, or any historical
scenario or result.

M4 addresses the four independent M3 runtime defects and the overly strict
source-association acceptance rule:

1. entry into the virtual wall-margin inset is terminal even while the robot
   remains inside the physical room;
2. recenter can target the room center even when that target lies inside an
   active fill-avoidance region, and its per-cycle greedy selector can change
   circumnavigation side;
3. post-recovery affine guidance rejects every direction in the backward
   half-plane and turns an empty candidate set into a terminal failure;
4. targeted redesign reconstructs an old convergence window from moving live
   buffers instead of reusing the accepted cluster's immutable samples;
5. Stage A requires proximity to the declared lamp coordinate even though a
   verified low-score controller trap can be displaced from that coordinate.

The M4 correction is opt-in and robust-profile-only. Defaults and normalized
behavior for schema versions 1 through 5 remain unchanged. M4 uses schema
version 6 for its new recovery controls and evidence fields.

### Safety classification

M4 retains latched zero-output `FAILSAFE` for:

- explicit stop;
- controller/watchdog or command-authorization fault;
- invalid, stale, or nonfinite pose or source data;
- ROS clock reversal;
- invalid room/fill geometry or supervisor exception;
- a robot-center pose outside the declared physical room faces;
- exhausted bounded recovery after the M4 recovery limit;
- actual non-ground collision as a failed run-level safety predicate.

M4 changes these valid-data algorithmic conditions from immediate terminal
failures into bounded recovery:

- entering or approaching the wall-margin inset;
- an empty post-recovery affine candidate set;
- a retryable fill rejection caused only by insufficient synchronized samples;
- verification timeout with an otherwise fresh valid source stream;
- escape or recenter timeout while finite geometry remains available.

No invalid fill is ever applied. A recovery can be attempted at most three
times per episode; repeated exhaustion remains an honest terminal failure.

### Wall-margin recovery

The physical wall margin remains exactly `0.20 m`. The rotating sensor
collision geometry is `0.39 m` wide, so reducing this margin would remove
real hardware clearance and is forbidden.

M4 adds separate physical-room and wall-margin-inset predicates inside the
existing supervisor geometry owner:

- physical-room violation remains terminal;
- boundary recovery is requested when inset clearance is at most `0.025 m`;
- forward motion that decreases inset clearance is blocked;
- the existing `RECENTER` controller turns and moves inward;
- inward motion from just outside the inset is allowed only when it strictly
  improves inset clearance and remains inside the physical room;
- normal search resumes only after the recovered pose has at least `0.10 m`
  inset clearance or completes its selected safe recenter target.

The wall margin remains a motion constraint and run diagnostic, not a
collision surrogate.

### Safe recenter target and persistent routing

Room center remains the preferred recenter target. If it lies inside any
active fill-avoidance circle, M4 deterministically selects the nearest
finite in-bounds proxy target outside every active fill plus `0.05 m`
clearance. Recenter completion additionally requires the robot pose itself to
be outside every active fill-avoidance circle.

When the direct segment to the frozen target intersects a fill, the selector
chooses a deterministic clockwise or counterclockwise route and locks that
side until direct line-of-sight clears. It cannot switch sides every timer
cycle. Target and route state are reset only on a new recenter episode.

M4 scenarios use:

```text
recenter maximum:                 60.0 s
recenter target tolerance:        0.35 m
recenter target fill clearance:   0.05 m
boundary trigger clearance:       0.025 m
boundary release clearance:       0.10 m
```

An escape timeout with an accepted fill falls back to this safe recenter
route. A finite recenter timeout may return to Gaussian-retaining `SEARCH`
once per bounded recovery attempt; the third exhausted recovery latches
`FAILSAFE`.

### Bounded affine assistance

Affine assistance remains enabled. It is not the long-term memory of an old
basin; the accepted Gaussian fill provides that memory.

M4 retains full affine authority in `ESCAPE_ASSIST`. During post-recovery
`SEARCH`:

- the state-level affine weight is `0.50`;
- the term decays at `0.05 s^-1`;
- maximum age is `20.0 s`;
- affine weight tapers to zero over `0.50 m` after leaving the active fill
  support;
- wall recovery and recenter always override affine;
- post-recovery selection uses hard wall/fill segment safety instead of the
  blanket nonnegative preferred-direction dot-product gate;
- no safe affine candidate requests recenter; if guidance remains unavailable
  after recenter, affine is cleared and raw-plus-Gaussian `SEARCH` continues.

Global coordinates remain evidence-only and are not provided to the detector,
supervisor, modified-cost node, or controller.

### Immutable targeted redesign

Each accepted fill cluster already retains bounded immutable basin samples.
With the M4 redesign-reuse control enabled, a targeted redesign resolves the
requested fill to its active cluster and redesigns from those retained
samples. It does not reconstruct the old convergence window from live buffers
and does not lower the global `40`-sample estimator floor.

An initial create request still requires the unchanged minimum. An
insufficient-sample initial request is retryable only through a fresh
SEARCH/verification episode; malformed geometry, an absent target cluster,
or an invalid result remains terminal.

### Trap-based Stage A evidence

Schema-v6 staged recovery adds:

```yaml
local_association_mode: verified_trap
```

The default remains `declared_source`, preserving schema-v1 through v5.
`verified_trap` requires:

- the same verified below-threshold `VERIFY_EXTREMUM` decision;
- one unique preceding convergence per created fill cluster;
- fill center within the declared fill-to-convergence tolerance;
- convergence outside the declared global exclusion distance;
- the accepted direct or one-redesign recovery path;
- the complete convergence, fill, escape, recenter-start, and
  recenter-complete event set;
- exact fill-cluster cardinality equal to known local topology.

Nearest declared-local distance remains reported for every assignment but is
diagnostic rather than the Stage A validity gate. This mode does not permit a
global convergence to count as local recovery and does not weaken exact
cardinality.

Schema-v6 may also declare:

```yaml
global_closer_radius_m: 1.00
```

It is a non-gating post-Stage-A diagnostic strictly smaller than the primary
operator-equivalent radius. M4 two-light readiness uses `1.20 m` as the
primary Stage B and collision-scope boundary and reports `1.00 m` separately.
M3 retains its original inverse relationship: `1.00 m` primary and `1.20 m`
approach diagnostic.

### M4 fixed implementation values

All M4 two-light attempts retain:

```text
room bounds:                       [-0.25, 3.75] x [-0.25, 3.75] m
room center:                       (1.75, 1.75) m
start:                             (0.0, 0.0), yaw 0
global:                            (3.5, 3.5), input 1600.0
local input:                       400.0
known topology:                    1 local, 1 global
maximum fill clusters:             1
detector path / efficiency gate:   0.20 m / 0.50
wall margin:                       0.20 m
fill minimum valid samples:        40
recovery paths:                    direct or one-redesign assisted
primary Stage B:                   1.20 m
closer diagnostic:                 1.00 m
collision expected:                false
run / wall / shutdown bounds:      360 / 540 / 45 s
```

### No-Gazebo qualification

Before any M4 Gazebo process starts:

1. replay the retained `39/40` redesign boundary and prove one same-cluster
   replacement from immutable accepted samples;
2. replay boundary pressure and prove outward motion is blocked while inward
   recovery is nonterminal;
3. replay the M3 recenter geometry whose room center lies inside the fill and
   prove a finite safe proxy target and eventual completion without side
   switching;
4. replay the post-recovery empty-candidate geometry and prove
   recenter/fallback without `FAILSAFE`;
5. prove hard faults and physical-room violations still latch zero output;
6. prove schema-v1 through v5 normalization and case keys, V6 artifacts, M1
   historical hashes, topics, cost sign/units, and sole `/cmd_vel` ownership
   are unchanged;
7. run focused and broad functional tests, an isolated three-package build,
   installed dry-run, and nonexecuting launch instantiation;
8. update live status, checkpoint Phase 08, and commit the exact source plus
   scenarios before dispatch.

### Fixed M4 execution sequence

The first fresh attempt is one visible-Gazebo two-light probe:

```text
suite:       phase08_v7_m4_visible_probe
version:     phase08-v7-m4-probe
case:        v7_m4_probe_r1p5_a45_h25_18201
local:       (1.0606601717798214, 1.0606601717798212)
seed:        18201
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_probe
```

If and only if that probe passes infrastructure, Stage A, exact cardinality,
primary Stage B, collision, forbidden state/event, and combined predicates,
run the fixed serial headless two-light qualification suite:

| Case | Local position | Seed | Role |
|---|---|---:|---|
| `v7_m4_r1p0_a45_h25_18202` | `(0.7071067811865476, 0.7071067811865475)` | 18202 | spatial |
| `v7_m4_r1p5_a22p5_h25_18202` | `(1.38581929876693, 0.5740251485476346)` | 18202 | spatial |
| `v7_m4_r1p5_a45_h25_18202` | `(1.0606601717798214, 1.0606601717798212)` | 18202 | spatial |
| `v7_m4_r1p5_a67p5_h25_18202` | `(0.5740251485476348, 1.38581929876693)` | 18202 | spatial |
| `v7_m4_r2p0_a45_h25_18202` | `(1.4142135623730951, 1.414213562373095)` | 18202 | spatial |
| `v7_m4_repeat_r1p5_a45_h25_18203` | `(1.0606601717798214, 1.0606601717798212)` | 18203 | repeat |
| `v7_m4_repeat_r1p5_a45_h25_18204` | `(1.0606601717798214, 1.0606601717798212)` | 18204 | repeat |
| `v7_m4_repeat_r1p5_a45_h25_18205` | `(1.0606601717798214, 1.0606601717798212)` | 18205 | repeat |

The evidence root is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4
```

M4's two-light gate requires the visible probe, all five spatial cases, and
all three repeats to pass. Every attempt is retained; no case is retried and
no value changes inside either fixed input.

### Optional three-light development probe

Only after the complete two-light gate passes may one visible three-light
development attempt run:

```text
suite:       phase08_v7_m4_three_light_probe
version:     phase08-v7-m4-three-light
case:        v7_m4_three_light_sequential_18206
start:       (0.0, 0.0), yaw 0
local 1:     (1.1086554390135441, 0.4592201188381077), input 400.0
local 2:     (0.6888301782571618, 1.662983158520316), input 400.0
global:      (3.5, 3.5), input 1600.0
topology:    2 local, 1 global
max fills:   2
seed:        18206
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_three_light_probe
```

This optional attempt is development evidence only. Failure does not erase a
passing two-light gate and success does not establish three-light
repeatability or physical readiness.

M4 authorizes simulation only. Phase 09 and all physical commands remain
unauthorized.

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

### M2.3 — assisted-path and operator-stop correction

Preserve the fixed failures through M2.2. Add only the schema-v5 alternative
recovery-path evidence contract and the evidence-backed `1.20 m`
post-recovery operator stop. Qualify and commit the exact fresh input before
one bounded visible probe with no automatic retry.

### M3 — fixed spatial suite

Commit and qualify the five fixed positions and the additive `1.20 m` approach
diagnostic before Gazebo. Then run exactly one serial headless attempt per
case. Preserve every attempt and require the stricter `1.00 m` primary Stage B
boundary for each combined result and for the all-five suite gate.

### M4 — recoverable navigation and two-light readiness

Implement the opt-in recovery policy and schema-v6 evidence contract above.
Qualify and commit without Gazebo, run the one visible probe, and only after a
passing probe run the fixed eight-case spatial/repeatability suite. Run the
single optional three-light probe only after the complete two-light gate
passes.

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

## M4.1 multi-publisher timestamp-evidence amendment

On 2026-07-29 the user explicitly authorized the correction identified by the
retained M4 visible-probe result. M4.1 is a fresh, versioned Level B
evidence-contract correction. It does not reopen, retry, relabel, overwrite,
or count the formally failed M4 attempt, and it does not change any M4
navigation, detector, fill, affine, recenter, wall, collision, stop, geometry,
light, or runtime value.

The retained M4 bag established:

- simulation `/clock` was monotonic;
- all typed stamps stayed inside the recorded `/clock` range;
- `/joint_states` had exactly two resolved publishers,
  `/joint_state_broadcaster` and `/turtlebot3_joint_state`;
- its merged bag receipt order had one apparent `225 ms` rollback;
- its `33,181` effort-present and `9,769` effort-empty message signatures were
  independently monotonic;
- every Stage A, exact cardinality, Stage B, collision, forbidden-state/event,
  final-zero, and cleanup predicate passed.

The existing validator treats every non-`AlgorithmEvent` topic as one
source-time stream. That assumption is invalid for a deliberate
multi-publisher topic because rosbag messages do not retain a usable publisher
identity. Raising the global `0.150 s` tolerance is forbidden; it would weaken
every singleton algorithm and control stream while leaving the structural
model defect intact.

### Exact evidence contract

The existing Phase 05 manifest and recorder/validator owners are extended
additively. No recorder, validator, launch graph, or algorithm fork is added.

Topic entries may declare:

```yaml
expected_publishers:
  - /publisher_a
  - /publisher_b
timestamp_ordering: multi_publisher_within_clock
```

The default when `timestamp_ordering` is absent remains `single_stream`.
Schema version and historical entries remain valid.

`expected_publishers` must be a nonempty, unique list of absolute ROS node
names. Preflight and offline completeness both require the resolved publisher
multiset to match it exactly. A missing, duplicate, or unexpected endpoint is
an infrastructure failure.

`multi_publisher_within_clock` is legal only when:

- the topic is simulation-only;
- at least two exact expected publishers are declared;
- `singleton_publisher` is false;
- the topic remains required and typed.

For that mode the validator:

- does not claim that the merged receipt sequence is a source-time sequence;
- excludes only that merged sequence from per-stream nonregression;
- still requires every typed message stamp to lie inside monotonic simulation
  `/clock` within the unchanged `0.150 s` tolerance;
- reports the exact expected and resolved owners plus the ordering scope;
- keeps strict nonregression for every default singleton/per-topic stream;
- keeps the existing independently identified per-producer
  `AlgorithmEvent` nonregression check.

The canonical `/joint_states` entry alone adopts this mode with:

```yaml
expected_publishers:
  - /joint_state_broadcaster
  - /turtlebot3_joint_state
timestamp_ordering: multi_publisher_within_clock
```

It remains required and recorded. The correction does not delete either
publisher, change the controller graph, or ignore `/joint_states`.

### Qualification boundary

Before any M4.1 Gazebo process starts:

1. prove manifest rejection of malformed owners, unknown ordering modes,
   singleton conflicts, and an underdeclared multi-publisher contract;
2. prove preflight accepts exactly the two declared owners and rejects a
   missing, duplicate, or unexpected endpoint;
3. prove a delayed merged multi-publisher sequence passes nonregression scope
   while every message remains within `/clock`;
4. prove an unexpected resolved owner, a singleton-stream rollback, an
   `AlgorithmEvent` producer rollback, and an out-of-clock multi-publisher
   stamp still fail;
5. replay the retained M4 run read-only and prove its immutable original
   contract/result remain failed rather than being retroactively relabeled;
6. run the recording/scenario focused tests and relevant broad regressions;
7. run an isolated three-package build and installed executable dry-run;
8. preserve historical worlds, scenarios, case keys, topics, cost sign/units,
   sole `/cmd_vel` ownership, and all M4 behavior inputs;
9. update live status, checkpoint, and commit the exact correction plus fresh
   scenario before dispatch.

### Fixed M4.1 visible probe

Exactly one new visible two-light attempt is authorized after qualification:

```text
suite:       phase08_v7_m4_1_visible_probe
version:     phase08-v7-m4-1-probe
case:        v7_m4_1_probe_r1p5_a45_h25_18207
local:       (1.0606601717798214, 1.0606601717798212)
seed:        18207
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_1_probe
```

Every M4 geometry and behavior value remains byte-for-byte equivalent after
identity, seed, suite, version, and evidence-root fields are excluded. The new
attempt is not an M4 retry.

The probe must pass recording completeness, exact publisher ownership,
Stage A, exact one-fill cardinality, primary `1.20 m` Stage B, collision,
forbidden state/event, final-zero, cleanup, and combined predicates. It is
retained without automatic retry or in-run value changes.

The fixed eight-case suite and optional three-light probe are outside this
authorization. A passing M4.1 probe establishes only the corrected visible
prerequisite. Phase 09 and every physical command remain unauthorized.

### M4.1 milestone

Save, validate, checkpoint, and commit this amendment. Then implement and
qualify the shared evidence correction plus exact fresh scenario without
Gazebo, checkpoint and commit the dispatch boundary, and run only the one
fixed visible probe.

## M4.2 progress-coupled post-recovery amendment

On 2026-07-30 the user explicitly authorized the fresh correction needed
after the immutable M4.1 Stage B failure. M4.2 is a schema-v7, robust-only,
opt-in Level B correction. It preserves M4.1's passing evidence model and
does not retry, overwrite, relabel, or count M4.1, M4, M3, M2.3, V6, or any
historical scenario or evidence.

M4.2 corrects the complete observed integration defect:

- recenter completion creates a new post-recovery guidance epoch;
- safe direction, affine authorization, and bounded supervisor motion share
  that epoch instead of relying on escape-era or fill-support distance alone;
- measured outward progress controls assistance release;
- a bounded translation-liveness monitor detects loops and recovers without
  treating valid-data low progress as an immediate safety failure;
- supervisor-owned motion is removed from the robust paired PDE search
  histories at each typed SEARCH boundary;
- the runner reserves a complete post-Stage-A behavioral window independent
  of variable local-detection latency.

### Compatibility and ownership

M4.2 extends the existing supervisor, custom controller command path, paired
PDE-history owners, convergence detector, launch graph, scenario schema, and
scenario runner. It adds no node, recorder, validator, controller, `/cmd_vel`
publisher, simulation/physical fork, or ground-truth input to the algorithm.

All new launch controls default off. Schema versions 1 through 6 retain their
existing normalized values and behavior. The `legacy` profile never
subscribes to or applies the new reset/guidance path. Existing M4 and M4.1
scenario bytes and case keys remain immutable.

The custom controller remains the sole `/cmd_vel` publisher. The supervisor
continues to publish only on `/gesc_gaussian/supervisor_command`; its SEARCH
contribution is combined and saturated by the existing custom controller.
Every positive supervisor translation is checked by the existing physical
room, wall-inset, active-fill, and command-persistence sweep before
publication. An unsafe translation is reduced to zero while safe angular
alignment/replanning continues; it is not itself a `FAILSAFE`.

Hard faults remain terminal:

- invalid/stale pose or source data;
- controller/graph fault or explicit stop;
- a robot-center pose outside the physical room faces;
- nonfinite geometry or command data;
- exhausted existing bounded recovery for a hard navigation failure.

Low post-recovery progress, wall-margin pressure while still physically
inside the room, and a temporarily blocked translation are recoverable
algorithmic conditions and do not directly enter `FAILSAFE`.

### New post-recovery guidance epoch

The new opt-in control is:

```text
post_recovery_progress_enabled: true
```

At every `RECENTER -> SEARCH` transition with an accepted active fill and
exhausted known-local fill budget, the supervisor must:

1. snapshot the current finite pose and active fill center as a fresh epoch;
2. discard any carried safe-direction object;
3. recompute the hard-safe post-recovery direction from that pose;
4. increment the typed `safe_direction_revision`;
5. start progress and liveness tracking from the same pose;
6. publish the existing typed state/command streams without adding a
   controller or command owner.

Let:

```text
p0             = epoch start position
c              = active fill center
p(t)           = current position
net(t)         = ||p(t) - p0||
outward(t)     = ||p(t) - c|| - ||p0 - c||
path(t)        = accumulated path length since p0
```

During SEARCH, the existing bounded differential-drive recenter gains and
velocity caps turn and translate along the selected safe direction while:

```text
outward(t) < post_recovery_guidance_min_progress_m
```

The M4.2 fixed value is `0.60 m`. The supervisor contribution becomes zero
after that progress is demonstrated, while ordinary GESC and Gaussian
navigation continue.

Affine weight is no longer reduced merely because a well-centered fill lies
far from the recenter endpoint. With M4.2 enabled it remains at the configured
post-recovery weight through `0.60 m` of measured outward progress, then
tapers linearly over the existing
`post_recovery_affine_taper_distance_m = 0.50 m`. The guidance epoch is
released after `1.10 m` outward progress or its bounded maximum time,
whichever occurs first. Negative or zero outward progress cannot consume the
affine budget.

### Translation-liveness recovery

The opt-in tracker evaluates exact-window motion over:

```text
post_recovery_liveness_window_sec:             12.0 s
post_recovery_liveness_min_path_length_m:       0.60 m
post_recovery_liveness_max_displacement_m:      0.20 m
post_recovery_direction_refresh_limit:          1
```

It declares a low-net-progress loop only when a complete `12.0 s` window has
both at least `0.60 m` path length and at most `0.20 m` net displacement.
Ordinary slow but translating motion does not qualify.

The first loop invalidates and recomputes the current safe direction,
increments its typed revision, renews the affine binding, and resets only the
liveness window. It does not reset accumulated outward progress.

If a new complete window still loops after the one refresh, M4.2 requests one
recoverable recenter through the existing state machine. On the next
`RECENTER_COMPLETE`, it starts a fresh epoch and recomputes direction again.
If low-net-progress recurs after that recenter, M4.2 releases the extra
post-recovery guidance and continues ordinary valid-data SEARCH rather than
entering `FAILSAFE`. Existing hard-fault and physical-room gates remain
unchanged.

Each refresh, recenter request, and guidance release is reported through the
existing typed `AlgorithmEvent` owner with measured path, displacement,
outward progress, window, thresholds, direction revision, and retry counts.
No new message type or event enum is required.

### Robust search-history reset

The new default-off control is:

```text
robust_search_epoch_reset_enabled: true
```

When enabled with `robust_gaussian_v1`, the existing position and cost
PDE-history nodes observe the canonical typed AlgorithmState. On each new
SEARCH epoch after supervisor-owned escape or recenter motion:

- the position PDE buffer initializes from the next finite current pose;
- the cost PDE buffer initializes from the next finite current modified-cost
  sample;
- their transport timestamps restart at those samples;
- the existing convergence detector starts its already supported fresh
  SEARCH counter/decay epoch.

The fill registry and accepted Gaussian fill remain intact. Legacy behavior,
filter equations, dither phase, cost sign/units, source score, and historical
recording topics remain unchanged.

### Recenter and time-budget correction

M4.2 changes only its fresh fixed inputs:

```text
recenter_tolerance_m:          0.15 m
recenter_hold_sec:             1.0 s
post_recovery_guidance_max_sec: 90.0 s
post_stage_a_timeout_sec:      120.0 s
run_timeout_sec:               480.0 s
wall_timeout_sec:              660.0 s
shutdown_grace_sec:             45.0 s
```

The tighter tolerance must place the robot reliably near the selected center
or safe proxy while keeping the existing safe route planner. It does not
shrink the physical room or increase the `0.20 m` wall margin.

Schema v7 adds the required positive staged-recovery field
`post_stage_a_timeout_sec`. The live runner starts this clock only after Stage
A and exact fill cardinality have been observed. It retains the existing
operator-equivalent global stop immediately upon a valid post-Stage-A sample
within `1.20 m`. If the complete `120.0 s` Stage B window elapses first, the
runner performs the same scoped graceful cancellation/finalization but
classifies Stage B and combined behavior as failed, not as an infrastructure
wall timeout. This budget cannot weaken or substitute for the proximity gate.

### Fixed M4.2 values

Every M4.2 two-light attempt retains:

```text
room bounds:                         [-0.25, 3.75] x [-0.25, 3.75] m
room center:                         (1.75, 1.75) m
start:                               (0.0, 0.0), yaw 0
global:                              (3.5, 3.5), input 1600.0
local input:                         400.0
known topology:                      1 local, 1 global
maximum fill clusters:               1
detector path / efficiency gate:     0.20 m / 0.50
wall margin:                         0.20 m
fill minimum valid samples:          40
recenter tolerance / hold:           0.15 m / 1.0 s
guidance outward hold / taper:       0.60 m / 0.50 m
liveness window/path/net:            12.0 s / 0.60 m / 0.20 m
direction refresh / recenter:        1 / 1
primary Stage B:                     1.20 m
closer diagnostic:                   1.00 m
collision expected:                  false
post-A / run / wall / shutdown:      120 / 480 / 660 / 45 s
```

### No-Gazebo qualification

Before any M4.2 Gazebo process starts:

1. prove exact-window progress, liveness, outward hold/taper, duplicate-stamp,
   backward-time, and parameter validation behavior with ROS-independent
   tests;
2. prove `RECENTER_COMPLETE` creates a fresh anchor and a new direction
   revision, safe SEARCH command, progress release, one refresh, one
   recoverable recenter, and nonterminal final fallback;
3. prove every guidance translation passes the existing command sweep and
   wall/fill pressure yields zero/replan rather than outward motion;
4. prove physical-room violation, invalid data, hard controller faults, and
   explicit stop still latch zero-output `FAILSAFE`;
5. prove paired robust PDE histories reset once per typed SEARCH boundary,
   remain paired, and do not reset under legacy/default-off operation;
6. prove schema-v7 requires and normalizes the new controls and positive
   post-A budget while schema-v1 through v6 normalization and case keys remain
   unchanged;
7. prove live Stage A starts the independent budget, global proximity wins
   immediately, budget expiry is a graceful behavioral failure, and the wall
   timeout remains an infrastructure failure;
8. replay retained M4/M4.1 geometry, direction, wall, command-sweep, evidence,
   ownership, and timestamp regressions without changing their artifacts;
9. run focused and broad functional tests, isolated three-package build,
   installed dry-run, and nonexecuting launch instantiation;
10. verify V6 and historical scenario/world hashes, topics, cost sign/units,
    sole `/cmd_vel` ownership, and all retained evidence hashes;
11. update live status, checkpoint, and commit the exact implementation plus
    fixed fresh inputs before dispatch.

### Fixed visible probe

If and only if no-Gazebo qualification passes, run one visible two-light
attempt:

```text
suite:       phase08_v7_m4_2_visible_probe
version:     phase08-v7-m4-2-probe
case:        v7_m4_2_probe_r1p5_a45_h25_18208
local:       (1.0606601717798214, 1.0606601717798212)
seed:        18208
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_2_probe
```

The probe must pass recording completeness, exact publisher ownership,
timestamp evidence, Stage A, exact one-fill cardinality, primary `1.20 m`
Stage B, collision, forbidden state/event, final-zero, cleanup, and combined
predicates. It is retained without retry or in-run tuning.

### Conditional two-light qualification

Only after the fixed visible probe passes may the serial headless M4.2
two-light suite run:

| Case | Local position | Seed | Role |
|---|---|---:|---|
| `v7_m4_2_r1p0_a45_h25_18209` | `(0.7071067811865476, 0.7071067811865475)` | 18209 | spatial |
| `v7_m4_2_r1p5_a22p5_h25_18209` | `(1.38581929876693, 0.5740251485476346)` | 18209 | spatial |
| `v7_m4_2_r1p5_a45_h25_18209` | `(1.0606601717798214, 1.0606601717798212)` | 18209 | spatial |
| `v7_m4_2_r1p5_a67p5_h25_18209` | `(0.5740251485476348, 1.38581929876693)` | 18209 | spatial |
| `v7_m4_2_r2p0_a45_h25_18209` | `(1.4142135623730951, 1.414213562373095)` | 18209 | spatial |
| `v7_m4_2_repeat_r1p5_a45_h25_18210` | `(1.0606601717798214, 1.0606601717798212)` | 18210 | repeat |
| `v7_m4_2_repeat_r1p5_a45_h25_18211` | `(1.0606601717798214, 1.0606601717798212)` | 18211 | repeat |
| `v7_m4_2_repeat_r1p5_a45_h25_18212` | `(1.0606601717798214, 1.0606601717798212)` | 18212 | repeat |

The evidence root is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_2
```

The two-light readiness gate requires the visible probe plus all five spatial
and all three repeat cases to pass every fixed predicate. Every attempt is
retained. No failed case is retried or changed inside M4.2.

### Optional three-light development probe

Only after the complete two-light gate passes may one separately fixed visible
three-light development probe be committed and run, using the retained M4
three-light geometry with fresh identity and seed `18213`. It remains
development evidence only; it cannot weaken the two-light gate or establish
three-light repeatability.

M4.2 authorizes simulation only. Phase 09 and every physical hardware command
remain unauthorized.

### M4.2 milestone

Save, validate, checkpoint, and commit this amendment. Implement and qualify
the full correction plus exact fixed inputs without Gazebo, checkpoint and
commit the dispatch boundary, and then run only the conditional sequence
above.

## M4.3 AlgorithmEvent producer-attribution amendment

The one fixed M4.2 visible probe is closed as a formal evidence failure even
though every behavioral predicate passed. Its `completeness.json`, result,
summary, bag, analysis, scenario bytes, case identity, seed, and evidence root
remain immutable. M4.3 is the fresh, user-authorized Level B evidence-contract
correction for the single diagnosed defect.

### Narrow implementation boundary

The existing Phase 05 recorder and validator remain the sole recording and
completeness owners. In
`ros_esc.experiment_recording.validate_run.algorithm_event_producer_stream`,
extend the existing `EVENT_CONFIGURATION` prefix table with exactly:

```text
("post-recovery ", "supervisor")
```

This recognizes the M4.2 supervisor's typed configuration-event family,
including:

```text
post-recovery guidance epoch started
post-recovery outward progress completed
```

No wildcard producer fallback is allowed. Unknown event types, malformed
watchdog signatures, and unrecognized configuration details must continue to
fail producer identification. The correction changes no ROS message, node,
topic, publisher, timestamp, recording field, navigation behavior, safety
behavior, cost sign or unit, launch value, scenario schema, or acceptance
threshold.

### Compatibility and immutable replay

Before any new Gazebo process starts, tests and read-only validation must
prove:

1. both observed `post-recovery ` signatures classify as `supervisor`;
2. a post-recovery event participates in the same per-producer timestamp
   stream as every other supervisor event, including a deliberate regression
   fixture;
3. an unknown configuration signature remains unidentified;
4. the retained M4.2 bag would pass all `48/48` completeness checks with the
   corrected code and `write_report=False`;
5. the retained M4.2 failed `completeness.json`, suite summary, scenario
   result, bag, and analysis files remain byte-identical;
6. retained M4 and M4.1 read-only replays preserve their recorded formal
   outcomes, and their retained completeness files remain byte-identical;
7. all M4.2 scenario files, V6 scenarios, historical scenarios/worlds,
   canonical topics, cost sign/units, and sole `/cmd_vel` ownership remain
   unchanged.

The read-only M4.2 replay is counterfactual diagnosis only. It cannot relabel
M4.2 as passed or count M4.2 toward the fresh M4.3 gate.

### Frozen M4.3 behavior

M4.3 copies the complete M4.2 visible and two-light behavioral contracts.
Every algorithm, source, start, geometry, topology, fill, recenter, affine,
post-recovery liveness, wall, collision, Stage A, Stage B, stop, and timeout
value remains identical. Only suite IDs, experiment versions, case IDs,
seeds, descriptions, repeat references, and evidence roots are fresh.

The fixed visible attempt is:

```text
suite:       phase08_v7_m4_3_visible_probe
version:     phase08-v7-m4-3-probe
case:        v7_m4_3_probe_r1p5_a45_h25_18308
local:       (1.0606601717798214, 1.0606601717798212)
seed:        18308
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3_probe
```

It must use visible Gazebo and pass all `48/48` recording checks, exact
publisher ownership, timestamp evidence, Stage A, exact one-fill
cardinality, primary noninterpolated `1.20 m` Stage B, collision, forbidden
state/event, final-zero, cleanup, and combined predicates. It is retained
without retry or in-run tuning.

### Conditional M4.3 two-light qualification

Only after the fixed visible M4.3 probe passes every formal and behavioral
predicate may this serial headless suite run:

| Case | Local position | Seed | Role |
|---|---|---:|---|
| `v7_m4_3_r1p0_a45_h25_18309` | `(0.7071067811865476, 0.7071067811865475)` | 18309 | spatial |
| `v7_m4_3_r1p5_a22p5_h25_18309` | `(1.38581929876693, 0.5740251485476346)` | 18309 | spatial |
| `v7_m4_3_r1p5_a45_h25_18309` | `(1.0606601717798214, 1.0606601717798212)` | 18309 | spatial |
| `v7_m4_3_r1p5_a67p5_h25_18309` | `(0.5740251485476348, 1.38581929876693)` | 18309 | spatial |
| `v7_m4_3_r2p0_a45_h25_18309` | `(1.4142135623730951, 1.414213562373095)` | 18309 | spatial |
| `v7_m4_3_repeat_r1p5_a45_h25_18310` | `(1.0606601717798214, 1.0606601717798212)` | 18310 | repeat |
| `v7_m4_3_repeat_r1p5_a45_h25_18311` | `(1.0606601717798214, 1.0606601717798212)` | 18311 | repeat |
| `v7_m4_3_repeat_r1p5_a45_h25_18312` | `(1.0606601717798214, 1.0606601717798212)` | 18312 | repeat |

The suite uses:

```text
suite:       phase08_v7_m4_3_two_light_suite
version:     phase08-v7-m4-3
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3
```

The two-light readiness gate requires the visible probe plus all five spatial
and all three repeat cases to pass every unchanged predicate. Every attempt
is retained. A behavioral or formal failure is not retried inside M4.3.
Cleanup failure stops further dispatch.

### No-Gazebo qualification and dispatch

Before the visible M4.3 probe, the exact implementation and fresh scenarios
must pass:

1. focused producer-classification, per-producer timestamp, recording,
   scenario-schema, scenario-runner, and M4.2 behavioral regressions;
2. broad ROS-independent functional tests;
3. fatal lint and Python compilation;
4. isolated three-package build;
5. installed scenario dry-runs and nonexecuting launch instantiation;
6. the immutable read-only replay and hash checks above;
7. source/install byte parity for the corrected validator and fresh scenario;
8. live-status update, checkpoint, and bounded Git commit.

The scenario hashes and deterministic case keys are frozen and recorded at
that dispatch commit. Any byte change requires a new hash and repetition of
the complete no-Gazebo qualification.

M4.3 authorizes only the conditional two-light simulation sequence above.
The optional three-light development probe remains unexecuted and requires a
complete M4.3 two-light gate plus separate user authorization. Phase 09 and
every physical hardware command remain unauthorized.

### M4.3 milestone

Save, validate, checkpoint, and commit this amendment. Implement and qualify
the exact evidence correction plus fixed fresh inputs without Gazebo,
checkpoint and commit the dispatch boundary, then execute only the fixed
visible probe and its passing-gated serial two-light suite.

## M4.4 adaptive-recenter and source-led-handoff amendment

The active user goal is to fix the two-light behavior fully. M4.3 is closed
at `6/8` with complete evidence and cannot be retried or changed. M4.4 is the
fresh Level B behavior-correction version for the two defects established by
the retained M4.3 suite:

1. a physically valid robot in the southwest wall/fill pinch received an
   immediate `FAILSAFE` because the recenter selector required a full fixed
   `0.50 m` candidate horizon;
2. after a successful local recovery, maximum fill clearance selected a
   westward direction and gave both supervisor translation and affine bias
   authority before ordinary source-driven GESC could establish motion.

M4.4 does not reopen, retry, overwrite, relabel, or count M4.3, M4.2, M4.1,
M4, M3, M2.3, V6, or any historical attempt. It changes no source geometry,
light value, start pose, fill estimator, detector threshold, local topology,
Stage A path, Stage B radius, collision contract, cost sign/unit, canonical
topic, controller ownership, or physical-hardware path.

### Compatibility and ownership

M4.4 extends only the existing supervisor, recenter geometry helper, central
launch graph, scenario schema/runner binding, tests, and fresh fixed scenario
inputs. It adds no node, controller, `/cmd_vel` publisher, recorder,
validator, launch graph, algorithm profile, or simulation/physical fork.

The custom controller remains the sole `/cmd_vel` publisher. The supervisor
continues to publish only `/gesc_gaussian/supervisor_command`, and the
controller retains the existing bounded combination and saturation.

Two new controls default `false`:

```text
adaptive_recenter_lookahead_enabled
post_recovery_source_led_handoff_enabled
```

The `legacy` profile and every scenario that omits these controls retain
byte-for-byte normalized behavior. M4.3 and all earlier scenarios remain
immutable. Enabling either control outside robust recoverable navigation is
invalid.

Hard stops remain unchanged:

- nonfinite or stale pose/source data;
- controller, graph, ownership, or explicit-stop fault;
- a robot-center pose outside the physical room faces;
- non-ground collision;
- nonfinite target, fill, command, or geometry;
- exhausted bounded recovery after a genuinely unavailable route.

Wall-margin pressure while the robot remains inside the physical room and a
temporarily empty finite-horizon route are recoverable navigation conditions,
not immediate safety violations.

### Adaptive recenter lookahead

With `adaptive_recenter_lookahead_enabled=true`, the existing deterministic
recenter route planner first evaluates the unchanged configured
`direction_lookahead_m = 0.50 m`. If no candidate exists, it retries the same
ordered direction set at successively halved finite horizons down to one
supervisor-command persistence distance:

```text
minimum horizon =
  recenter_max_linear_velocity_mps * supervisor_command_stale_sec
  = 0.10 m/s * 0.50 s
  = 0.05 m
```

The fixed evaluation sequence is therefore:

```text
0.50, 0.25, 0.125, 0.0625, 0.05 m
```

Full-horizon behavior remains preferred. Candidate order, fill radius,
fill-avoidance margin, wall-margin inset, frozen target, obstacle-side lock,
target-progress score, differential-drive command bounds, and command sweep
remain unchanged. A shorter candidate changes only the finite planning
resolution; the actual command is still checked over its complete persistence
horizon before publication.

If every adaptive horizon is empty while the robot center remains physically
valid, the supervisor publishes zero translation, retains angular
replanning, and lets the existing finite recenter timeout/retry budget
continue. It emits one typed configuration event for that episode instead of
immediately entering `FAILSAFE`. A later valid candidate clears the held
condition. Exhausting the existing bounded recenter recovery still enters
`FAILSAFE`.

The retained M4.3 failure pose must be an exact regression:

```text
pose:             (0.3963, 0.2401) m
fill center:      (0.5447780037, 0.8569669278) m
avoidance radius: 0.6086747487 m
target:           (1.75, 1.75) m
```

At this geometry, the fixed `0.50 m` selector returns no candidate and the
adaptive selector must return a finite hard-safe `0.25 m` candidate without
crossing the physical room, inset, or fill.

### Source-led post-recovery handoff

With `post_recovery_source_led_handoff_enabled=true`, every accepted
`RECENTER -> SEARCH` boundary after the known local-fill budget is exhausted
starts the existing post-recovery progress epoch but initially with:

```text
raw sensor weight:       1.0
Gaussian fill weight:    1.0
affine weight:           0.0
supervisor translation:  0.0
safe direction:          unavailable
```

This is not an open-loop pause. Ordinary GESC plus the accepted Gaussian fill
owns motion during the handoff, using the same rotating sensor, costs,
controller, PDE histories, and physical/simulation parity. The paired
position/cost histories are reset at the typed SEARCH boundary as already
implemented by M4.2. No global coordinates, global bearing, source role, or
simulation ground truth enters the algorithm.

M4.4 reuses the already fixed liveness values:

```text
handoff window:                    12.0 s
qualifying net displacement:       greater than 0.20 m
```

At the first complete `12.0 s` window:

- if net displacement is greater than `0.20 m`, the source-led handoff has
  demonstrated translation; extra post-recovery guidance is released and
  ordinary raw-plus-Gaussian SEARCH continues;
- if net displacement is at most `0.20 m`, the handoff is classified as
  stalled and the existing hard-safe fill-escape guidance becomes eligible;
  the liveness window resets before that fallback begins.

Reaching the existing `1.10 m` outward release boundary during the handoff
also releases guidance. The existing fallback may still refresh one
direction, request one recoverable recenter, and then release to ordinary
search. It cannot command during the source-led window.

Typed configuration events report:

```text
post-recovery source-led handoff started
post-recovery source-led handoff completed
post-recovery source-led handoff stalled; fallback guidance armed
recenter route temporarily unavailable; bounded recovery continues
```

They use the already corrected M4.3 `post-recovery ` or existing supervisor
producer families and require no recording-validator change.

### Fixed values and acceptance

All M4.4 attempts retain every M4.3 behavioral value:

```text
room bounds:                       [-0.25, 3.75] x [-0.25, 3.75] m
room center:                       (1.75, 1.75) m
start:                             (0.0, 0.0), yaw 0
global:                            (3.5, 3.5), input 1600.0
local input:                       400.0
known topology:                    1 local, 1 global
maximum fill clusters:             1
detector path / efficiency gate:   0.20 m / 0.50
wall margin:                       0.20 m
fill minimum valid samples:        40
recenter maximum / tolerance:       60.0 s / 0.15 m
post-recovery liveness:             12.0 s, 0.60 m path, 0.20 m net
primary Stage B:                    1.20 m
closer diagnostic:                 1.00 m
post-Stage-A budget:                120.0 s
collision expected:                false
```

The operator-equivalent stop remains the first valid, recorded,
noninterpolated post-Stage-A odometry sample within `1.20 m` of the global.
The runner then requests the same graceful stop, final zero, readiness false,
completeness validation, and cleanup. The `1.00 m` closer diagnostic remains
non-gating. A longer timeout or larger stop radius is not part of M4.4.

### No-Gazebo qualification

Before any M4.4 Gazebo process starts:

1. replay the exact M4.3 corner pose and its complete preceding route-side
   sequence; prove full-horizon failure, adaptive finite selection,
   hard-safe command sweep, and no immediate `FAILSAFE`;
2. prove a physically invalid pose, collision/graph/controller fault,
   nonfinite geometry, and exhausted bounded recovery remain terminal;
3. prove source-led handoff publishes zero supervisor command, zero affine
   weight, and no safe direction for a complete initial window;
4. prove greater-than-`0.20 m` source-led displacement releases to ordinary
   SEARCH without affine, while at-most-`0.20 m` displacement arms exactly
   one existing fallback path;
5. prove no global coordinate or source role is passed to the supervisor,
   modified-cost node, or controller;
6. prove both controls default off and M4.3, V6, and historical normalized
   cases, hashes, topics, cost sign/units, and sole `/cmd_vel` ownership are
   unchanged;
7. run focused supervisor geometry/integration, launch, schema, runner,
   recording, and M4.3 regression tests;
8. run broad ROS-independent functional tests, fatal lint, Python
   compilation, an isolated three-package build, installed dry-runs,
   nonexecuting launch instantiation, source/install parity, context
   validation, and immutable retained-evidence hash checks;
9. update live status, checkpoint Phase 08, and commit the exact source plus
   fixed fresh inputs.

### Fixed M4.4 visible probe

Only after every no-Gazebo gate passes may one fresh visible probe run:

```text
suite:       phase08_v7_m4_4_visible_probe
version:     phase08-v7-m4-4-probe
case:        v7_m4_4_probe_r1p5_a45_h25_18408
local:       (1.0606601717798214, 1.0606601717798212)
seed:        18408
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4_probe
```

It must use visible Gazebo and pass all `48/48` recording checks, Stage A,
exact one-fill cardinality, primary noninterpolated `1.20 m` Stage B,
collision, forbidden state/event, final-zero, cleanup, and combined
predicates. It is retained without retry or in-run tuning.

### Conditional M4.4 two-light qualification

Only after the fixed visible probe passes every formal and behavioral
predicate may this serial headless suite run:

| Case | Local position | Seed | Role |
|---|---|---:|---|
| `v7_m4_4_r1p0_a45_h25_18409` | `(0.7071067811865476, 0.7071067811865475)` | 18409 | spatial |
| `v7_m4_4_r1p5_a22p5_h25_18409` | `(1.38581929876693, 0.5740251485476346)` | 18409 | spatial |
| `v7_m4_4_r1p5_a45_h25_18409` | `(1.0606601717798214, 1.0606601717798212)` | 18409 | spatial |
| `v7_m4_4_r1p5_a67p5_h25_18409` | `(0.5740251485476348, 1.38581929876693)` | 18409 | spatial |
| `v7_m4_4_r2p0_a45_h25_18409` | `(1.4142135623730951, 1.414213562373095)` | 18409 | spatial |
| `v7_m4_4_repeat_r1p5_a45_h25_18410` | `(1.0606601717798214, 1.0606601717798212)` | 18410 | repeat |
| `v7_m4_4_repeat_r1p5_a45_h25_18411` | `(1.0606601717798214, 1.0606601717798212)` | 18411 | repeat |
| `v7_m4_4_repeat_r1p5_a45_h25_18412` | `(1.0606601717798214, 1.0606601717798212)` | 18412 | repeat |

The suite uses:

```text
suite:       phase08_v7_m4_4_two_light_suite
version:     phase08-v7-m4-4
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4
```

The two-light readiness gate requires the visible probe plus all five spatial
and all three repeat cases to pass every unchanged predicate. Every attempt
is retained. A behavioral or formal failure is not retried inside M4.4.
Cleanup failure stops later dispatch.

### Scope and stop conditions

M4.4 authorizes only the conditional two-light simulation sequence above,
after its exact implementation and inputs are qualified, checkpointed, and
committed. The optional three-light probe remains unauthorized and requires
a complete M4.4 two-light gate plus separate user authorization. Phase 09 and
every physical hardware command remain unauthorized.

Stop before Gazebo on any M4.3/V6/historical artifact drift, source/install
mismatch, ownership change, failed compatibility or safety regression,
existing fresh evidence root, active ROS/Gazebo process, or incomplete
no-Gazebo gate.

### M4.4 milestone

Save, validate, checkpoint, and commit this amendment. Implement and qualify
only the adaptive recenter and source-led handoff controls plus fresh fixed
inputs without Gazebo. Checkpoint and commit the exact dispatch boundary,
then execute only the one fixed visible probe and its passing-gated serial
two-light suite.

## M4.5 source-continuity, full-budget, and startup-recovery amendment

M4.4 is immutable and closed with five complete suite passes, two complete
behavioral failures, and one infrastructure-invalid startup attempt. Its
retained report is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_4_two_light_suite_report.md

SHA-256
7a36bf8a81e018d7cf007a6478d41df3e8d1b7236d53d4cfe49856df5c35636c
```

M4.4 proved that adaptive recenter corrected the retained wall/fill corner
failure. None of its seven behavioral attempts entered `FAILSAFE`, collided,
or violated a physical room face. The remaining M4.4 failures instead
establish three independent defects:

1. in the radius-2.0 case, the first fill-clearance fallback direction had
   dot product approximately `-1.000` with the measured source-led
   displacement and exactly reversed evidence that had reduced global
   distance;
2. a late Stage A completion left only `29.104 s` before a fixed `480 s`
   recording ended, so the declared `120 s` Stage B budget was not reserved;
3. Humble's controller spawner lost a successful load response, retried the
   non-idempotent load, then failed because the controller was already
   loaded.

M4.5 is the fresh Level B correction for only those retained defects. It does
not reopen, retry, overwrite, relabel, or count M4.4, M4.3, M4.2, M4.1, M4,
M3, M2.3, V6, or any historical attempt.

### Compatibility and ownership

M4.5 extends only:

- the existing supervisor and pure safe-direction helper ownership;
- the existing central Gazebo launch and rotating-sensor controller-spawner
  launch;
- the existing scenario schema/runner and live staged monitor;
- focused regression tests and fresh fixed M4.5 scenarios.

It adds no controller, persistent node, `/cmd_vel` publisher, recorder,
validator, algorithm profile, launch graph, cost source, message, or
simulation/physical algorithm fork. The custom controller remains the sole
`/cmd_vel` publisher. The supervisor continues to publish only
`/gesc_gaussian/supervisor_command`.

The behavior correction is controlled by:

```text
post_recovery_source_continuity_enabled = false
```

The infrastructure correction is controlled by:

```text
controller_spawner_load_recovery_enabled = false
```

Both default `false`. M4.4, M4.3, V6, legacy, and every historical scenario
that omits them preserve their normalized algorithm values and launch
behavior. The following inert numeric defaults are used only when source
continuity is enabled:

```text
post_recovery_source_continuity_min_displacement_m = 0.05
post_recovery_source_reversal_dot_threshold        = -0.90
post_recovery_source_bypass_clearance_m             = 0.10
```

The primary Stage B radius remains `1.20 m`; the closer `1.00 m` diagnostic
remains non-gating. Physical room faces, non-ground collision, stale or
nonfinite required data, graph/controller ownership, explicit stop, final
zero, and exhausted bounded recovery remain hard gates. M4.5 does not relax
the wall margin, collision rules, room bounds, stop radius, or cost
sign/units.

### Evidence-led anti-reversal bypass

The source-led window remains exactly the M4.4 raw/Gaussian-only window:

```text
raw sensor weight:       1.0
Gaussian fill weight:    1.0
affine weight:           0.0
supervisor translation:  0.0
safe direction:          unavailable
window:                  12.0 s
```

At an at-most-`0.20 m` stalled handoff, the supervisor computes only from its
recorded pose history and active fill:

```text
source displacement =
  current pose - source-led anchor pose

radial outward direction =
  current pose - active fill center
```

If source displacement is at least `0.05 m` and the normalized dot product
between those vectors is at most `-0.90`, the radial fallback would strongly
reverse measured source-led motion. With source continuity enabled, that
direction is forbidden.

The supervisor then evaluates the unchanged ordered hard-safe candidate set
relative to the measured source-led direction and admits only its forward
half-plane. This naturally selects a tangential/outward bypass when the
direct source-led direction intersects the known fill. Every candidate must
still pass the complete fill-segment, wall-inset, physical-room, finite
geometry, and command-persistence sweep checks. Candidate order and
differential-drive command limits remain deterministic.

The bypass retains bounded supervisor and affine assistance only until:

```text
current fill distance >=
  active fill avoidance radius + 0.10 m
```

It then releases both assistance paths and returns to ordinary
raw-plus-Gaussian SEARCH. Direction refresh retains the same measured
source-continuity half-plane. If a recoverable recenter is required, the
continuity constraint survives that one recenter and cannot silently fall
back to the forbidden radial reversal. Existing retry, release, and terminal
hard-fault bounds remain finite.

When the source displacement is below `0.05 m`, or the dot product is greater
than `-0.90`, the unchanged M4.4 fallback executes. This preserves the
passing M4.4 cases, including repeat `18412`, whose retained dot product was
only `-0.192921`.

The exact retained radius-2.0 regression is:

```text
source-led anchor:       (1.2320122160, 1.4710422281) m
source-led end:          approximately (1.3775, 1.5451) m
fill center:             (1.8278297781, 1.7700514862) m
fill avoidance radius:   0.6086747487 m
source/radial dot:       -0.9999689709
old fallback:            (-0.8943280105, -0.4474119016)
old fallback/source dot: approximately -1.000
```

The old fallback must remain the default-off result. With source continuity
enabled, the old fallback must be rejected and a finite hard-safe candidate
with nonnegative source-direction alignment must be selected. No global
coordinate, global bearing, source role, or simulation ground truth may
enter this decision.

Typed events report:

```text
post-recovery source-continuity bypass armed
post-recovery source-continuity bypass completed
```

They use the already accepted `post-recovery ` producer family and do not
change the Phase 05 recorder/validator.

### Full staged-budget reservation

M4.5 adds an optional staged-recovery field:

```text
stage_a_timeout_sec
```

Historical scenarios that omit it retain their exact schema and runner
behavior. When present, schema validation requires:

```text
stage_a_timeout_sec > 0
post_stage_a_timeout_sec > 0
stage_a_timeout_sec + post_stage_a_timeout_sec
  <= execution.run_timeout_sec
```

The live monitor anchors the Stage A budget at its first finite odometry
sample. If Stage A and exact fill cardinality have not completed when that
budget expires, the runner requests the same graceful stop and reports an
explicit Stage A timeout sample. If Stage A completes at the boundary, Stage
A takes precedence and the complete independent Stage B budget remains
available. The existing rule that a qualifying global sample wins at the
exact Stage B boundary is unchanged.

Every M4.5 case uses:

```text
stage_a_timeout_sec:       480.0
post_stage_a_timeout_sec:  120.0
run_timeout_sec:           600.0
wall_timeout_sec:          780.0
```

This is not an unbounded timeout increase. It converts the previous
ambiguous total duration into a fixed `480 + 120 s` staged contract. A run
that has not completed Stage A by `480 s` stops and fails rather than
consuming the Stage B reserve.

### Idempotent controller-load recovery

With `controller_spawner_load_recovery_enabled=true`, the existing
rotating-sensor control launch substitutes one transient, package-owned
spawner executable for the two concurrent upstream spawner processes. It
loads, configures, and activates the same two controllers in fixed order:

```text
joint_state_broadcaster
velocity_controller
```

The executable reuses Humble's controller-manager APIs and the same
`30.0 s` service-call bound. Its load operation issues at most one
`/load_controller` request per observed unloaded state. If that response is
missing or reports failure, it queries `/list_controllers` before any further
load. A controller confirmed loaded is treated idempotently and proceeds to
the unchanged configure/activate operations. If it is not confirmed loaded,
the executable exits nonzero and the existing preflight hard failure
remains.

This correction prevents the exact retained sequence:

```text
successful load
-> lost response
-> duplicate load
-> "already loaded"
-> fatal spawner exit
```

Operational readiness still requires both controllers active, exact topic
and publisher ownership, readiness true, and clean console evidence. The
helper is transient and does not publish commands or alter controller
behavior.

### Fixed values and acceptance

All M4.5 attempts preserve the M4.4 geometry, behavior, and acceptance values
except for the declared anti-reversal control and staged duration
reservation:

```text
room bounds:                       [-0.25, 3.75] x [-0.25, 3.75] m
room center:                       (1.75, 1.75) m
start:                             (0.0, 0.0), yaw 0
global:                            (3.5, 3.5), input 1600.0
local input:                       400.0
known topology:                    1 local, 1 global
maximum fill clusters:             1
detector path / efficiency gate:   0.20 m / 0.50
wall margin:                       0.20 m
fill minimum valid samples:        40
recenter maximum / tolerance:       60.0 s / 0.15 m
post-recovery liveness:             12.0 s, 0.60 m path, 0.20 m net
primary Stage B:                    1.20 m
closer diagnostic:                 1.00 m
Stage A budget:                     480.0 s
post-Stage-A budget:                120.0 s
collision expected:                false
```

The operator-equivalent stop remains the first valid, recorded,
noninterpolated post-Stage-A odometry sample within `1.20 m` of the global,
followed by graceful stop, final zero, readiness false, completeness
validation, and cleanup.

### No-Gazebo qualification

Before any M4.5 Gazebo process starts:

1. replay the exact retained M4.4 radius-2.0 anchor/end/fill geometry;
   prove the old radial direction is an at-most-`-0.90` reversal, the
   default-off result is unchanged, and enabled selection returns a finite
   hard-safe nonreversing candidate;
2. prove the retained repeat-18412 geometry does not trigger the correction
   and preserves its existing fallback;
3. prove bypass assistance releases at the exact avoidance-radius-plus-
   `0.10 m` boundary, persists across at most one recoverable recenter, and
   cannot reauthorize the forbidden reversal;
4. prove source displacement below `0.05 m`, no safe candidate, nonfinite
   geometry, stale pose/source, physical-room violation, collision/graph/
   controller fault, and exhausted recovery retain their declared bounded
   outcomes;
5. prove no global coordinate, source role, or simulation truth is passed to
   the supervisor, modified-cost node, or controller;
6. prove `stage_a_timeout_sec + post_stage_a_timeout_sec <=
   run_timeout_sec`, exact boundary precedence, graceful Stage A timeout,
   full Stage B reservation, and historical omission behavior;
7. prove the idempotent spawner performs no duplicate load after a lost
   response, accepts only a confirmed loaded state, preserves both active
   controller requirements, and remains default-off;
8. prove M4.4, M4.3, V6, shifted/historical worlds, all historical normalized
   scenarios and hashes, topics, cost sign/units, sole `/cmd_vel` ownership,
   recorder, and validator are unchanged;
9. run focused supervisor geometry/integration, launch, schema, runner,
   recording, and historical regression tests;
10. run broad ROS-independent functional tests, fatal lint, Python
    compilation, isolated three-package build, installed dry-runs,
    nonexecuting launch instantiation, source/install parity, context
    validation, and retained-evidence hash checks;
11. update live status, checkpoint Phase 08, and commit the exact source plus
    fixed fresh inputs.

### Fixed M4.5 visible probe

Only after every no-Gazebo gate passes may one fresh visible radius-2.0 probe
run:

```text
suite:       phase08_v7_m4_5_visible_probe
version:     phase08-v7-m4-5-probe
case:        v7_m4_5_probe_r2p0_a45_h25_18508
local:       (1.4142135623730951, 1.4142135623730950)
seed:        18508
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_5_probe
```

It must use visible Gazebo and pass `48/48` recording, active controller
preflight, Stage A, exact one-fill cardinality, primary noninterpolated
`1.20 m` Stage B, complete staged budgets, collision, forbidden
state/event, final-zero, cleanup, and combined predicates. It is retained
without retry or in-run tuning.

### Conditional M4.5 two-light qualification

Only after the fixed visible M4.5 probe passes every formal and behavioral
predicate may this serial headless suite run:

| Case | Local position | Seed | Role |
|---|---|---:|---|
| `v7_m4_5_r1p0_a45_h25_18509` | `(0.7071067811865476, 0.7071067811865475)` | 18509 | spatial |
| `v7_m4_5_r1p5_a22p5_h25_18509` | `(1.38581929876693, 0.5740251485476346)` | 18509 | spatial |
| `v7_m4_5_r1p5_a45_h25_18509` | `(1.0606601717798214, 1.0606601717798212)` | 18509 | spatial |
| `v7_m4_5_r1p5_a67p5_h25_18509` | `(0.5740251485476348, 1.38581929876693)` | 18509 | spatial |
| `v7_m4_5_r2p0_a45_h25_18509` | `(1.4142135623730951, 1.4142135623730950)` | 18509 | spatial |
| `v7_m4_5_repeat_r1p5_a45_h25_18510` | `(1.0606601717798214, 1.0606601717798212)` | 18510 | repeat |
| `v7_m4_5_repeat_r1p5_a45_h25_18511` | `(1.0606601717798214, 1.0606601717798212)` | 18511 | repeat |
| `v7_m4_5_repeat_r1p5_a45_h25_18512` | `(1.0606601717798214, 1.0606601717798212)` | 18512 | repeat |

The suite uses:

```text
suite:       phase08_v7_m4_5_two_light_suite
version:     phase08-v7-m4-5
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_5
```

The two-light readiness gate requires the visible probe plus all five spatial
and all three repeat cases to pass every unchanged predicate. Every attempt
is retained. A behavioral, formal, infrastructure, or cleanup failure is not
retried inside M4.5. Cleanup failure stops later dispatch.

### Scope and stop conditions

M4.5 authorizes only the fixed visible probe and its passing-gated serial
two-light suite after the exact implementation and fresh inputs pass every
no-Gazebo gate, are checkpointed, and are committed.

Stop before Gazebo on any M4.4/M4.3/V6/historical artifact drift,
source/install mismatch, ownership change, recorder/validator change, failed
compatibility or safety regression, existing fresh evidence root, active
ROS/Gazebo process, or incomplete no-Gazebo gate.

The optional three-light probe remains unauthorized and requires a complete
M4.5 two-light gate plus separate user authorization. Phase 09 and every
physical hardware command remain unauthorized.

### M4.5 milestone

Save, validate, checkpoint, and commit this amendment. Implement and qualify
only the source-continuity anti-reversal bypass, full staged-budget
reservation, idempotent controller-load recovery, and fresh fixed inputs
without Gazebo. Checkpoint and commit the exact dispatch boundary, then
execute only the fixed visible probe and its passing-gated serial two-light
suite.

## M4.6 evidence-calibrated continuity-trigger amendment

M4.5 is immutable and closed. Its one fixed visible attempt passed
controller startup/readiness, `48/48` recording, cleanup, collision,
forbidden-evidence, final-zero, Stage A, exact one-fill cardinality, the
`480 s` Stage A bound, and the complete independent `120 s` Stage B
opportunity. It failed Stage B at `3.6282729279 m` from the global, so its
conditional headless suite did not run.

The retained M4.5 report is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_5_visible_probe_report.md

SHA-256
cd8c96e30cfe56e748147f2b5c28bc29af9b2cb50b7760b07f0c496e350f71b5
```

M4.5 proves all three implemented mechanisms execute as declared. The
remaining failure is narrower: the fresh radius-2 source-led displacement
reduced global distance by `0.1118906407 m`, but its radial/source dot was
`-0.8412123478`, outside the fixed `-0.90` trigger. The bypass therefore did
not arm, and the unchanged radial fallback reversed the useful displacement.
This is an evidence-calibration miss, not a selector, staged-budget,
controller-startup, wall, collision, room-boundary, or failsafe defect.

M4.6 is Plan-only until reviewed and approved. It does not authorize an edit,
build, checkpoint beyond the Plan boundary, or simulation merely by existing.

### Exact bounded correction

M4.6 changes only the explicit enabled value in fresh M4.6 scenarios:

```text
post_recovery_source_reversal_dot_threshold: -0.80
```

The launch and supervisor numeric default remains `-0.90`, and
`post_recovery_source_continuity_enabled` remains default `false`.
M4.5 scenarios remain byte-identical and retain `-0.90`. M4.4, M4.3, V6,
legacy, and every historical scenario therefore preserve their exact
normalized behavior.

No production algorithm-source change is intended. The existing pure
evidence function, hard-safe forward-half-plane selector, bypass-release
radius, one-recenter persistence, affine/supervisor bounds, staged runner,
and idempotent spawner are reused unchanged. If implementation reveals that
a production change is required, stop as a Plan contradiction rather than
expanding M4.6 silently.

The evidence basis is the complete retained set:

| Retained case | Result | radial/source dot |
|---|---:|---:|
| M4.4 visible central | PASS | `-0.336356` |
| M4.4 radius 1.0 | PASS | `0.885685` |
| M4.4 radius 1.5, 45 deg | PASS | `0.201668` |
| M4.4 radius 1.5, 67.5 deg | PASS | `0.787593` |
| M4.4 radius 2.0 | FAIL | `-0.999969` |
| M4.4 repeat 18410 | budget-invalid formal FAIL | `0.413417` |
| M4.4 repeat 18411 | PASS | `0.953112` |
| M4.4 repeat 18412 | PASS | `-0.192921` |
| M4.5 radius 2.0 | FAIL | `-0.841212` |

`-0.80` catches both observed radius-2 reversals with `0.0412` margin on
the fresh failure. It leaves every retained passing M4.4 case outside the
trigger; the closest passing negative value is `-0.336356`. No threshold is
inferred from global coordinates at runtime. The runtime decision still
receives only measured poses and the active fill.

At the exact retained M4.5 geometry, pure replay at `-0.80` must return:

```text
anchor:                          (1.1809160175, 1.5969815630) m
source-led end:                  (1.3563818523, 1.5646136279) m
fill center:                     (1.8117325336, 1.7511796132) m
fill avoidance radius:           0.6086747487 m
source/radial dot:              -0.8412123478
selected direction:             (-0.1814078760, -0.9834079431)
source alignment:                approximately 0.0
radial outward alignment:        0.5407048973
lookahead endpoint fill distance: 0.8707616100 m
bypass release radius:           0.7086747487 m
```

The same geometry at `-0.90` must remain the immutable M4.5 non-trigger.
Default-off must retain the old radial fallback. The exact M4.4 radius-2
geometry must trigger at both `-0.90` and `-0.80`; repeat `18412` and every
retained passing window must not trigger at `-0.80`.

### Preserved acceptance and safety contract

M4.6 preserves all M4.5 values and gates other than the explicit enabled
threshold:

```text
room bounds:                       [-0.25, 3.75] x [-0.25, 3.75] m
room center:                       (1.75, 1.75) m
start:                             (0.0, 0.0), yaw 0
global:                            (3.5, 3.5), input 1600.0
local input:                       400.0
known topology:                    1 local, 1 global
maximum fill clusters:             1
detector path / efficiency gate:   0.20 m / 0.50
wall margin:                       0.20 m
fill minimum valid samples:        40
recenter maximum / tolerance:       60.0 s / 0.15 m
source-led window:                  12.0 s
post-recovery liveness:             0.60 m path / 0.20 m net
bypass clearance:                   avoidance radius + 0.10 m
primary Stage B:                    1.20 m
closer diagnostic:                 1.00 m, non-gating
Stage A / Stage B budgets:          480.0 s / 120.0 s
run / wall timeout:                 600.0 s / 780.0 s
collision expected:                false
```

Physical room faces, non-ground collision, stale/nonfinite required data,
graph/controller ownership, explicit stop, final zero, exhausted bounded
recovery, and cleanup remain hard gates. M4.6 does not relax wall margin,
collision, room bounds, the operator-equivalent `1.20 m` stop, cost
sign/units, exact one-fill cardinality, or sole `/cmd_vel` ownership.

### Intended implementation files

No production source file is intended to change.

Modify only focused regression/contract tests as required:

```text
ros2_ws/src/ros_esc/test/test_supervisor_integration.py
ros2_ws/src/ros_esc/test/test_scenario_schema.py
ros2_ws/src/ros_esc/test/test_scenario_runner.py
ros2_ws/src/ros_esc/test/test_observability_contract.py
```

Create fresh fixed inputs:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v7_m4_6_visible_probe.yaml
  phase08_v7_m4_6_two_light_suite.yaml
```

Update the live status, Phase 08 checkpoint, and a fresh M4.6 validation
report only at their declared evidence boundaries. Do not modify the Phase
05 recorder/validator, controller, modified-cost node, supervisor production
source, central launch, controller-spawner helper, world files, M4.5 inputs,
or any historical artifact.

### No-Gazebo qualification

Before any M4.6 Gazebo process starts:

1. seal the M4.5 report, summary, completeness, scenario result, bag, and
   analysis hashes;
2. replay the exact M4.5 anchor/end/fill geometry and prove `-0.90` does not
   trigger while `-0.80` returns the exact finite hard-safe candidate above;
3. prove exact bypass release at avoidance radius plus `0.10 m`, direction
   refresh in the retained source half-plane, and persistence through at
   most one recoverable recenter;
4. replay the full M4.4 dot table and prove both radius-2 failures trigger
   while every retained pass, especially repeat `18412`, does not;
5. prove default-off, historical omission, nonfinite/stale geometry,
   sub-`0.05 m` displacement, no safe candidate, room/collision/ownership
   fault, and exhausted recovery retain their bounded outcomes;
6. prove every fresh normalized M4.6 case differs from its M4.5 counterpart
   only by fresh experiment identity/seed and the explicit `-0.80` value;
7. prove `480 + 120 <= 600 s`, exact Stage A/Stage B boundary precedence,
   active-controller readiness, one load request, one-fill topology,
   primary `1.20 m` proximity, and final-zero/cleanup contracts remain
   unchanged;
8. run focused supervisor, schema, runner, observability, recording, and
   controller-startup regressions;
9. run broad ROS-independent functional tests, fatal lint, Python
   compilation, isolated three-package build, installed dry-runs,
   nonexecuting launch instantiation, source/install parity, context
   validation, and historical/evidence hash checks;
10. update live status, checkpoint Phase 08, and commit the exact tests plus
    fresh fixed inputs before recording a dispatch command.

Stop before Gazebo on any failed regression, production-source drift,
M4.5/historical drift, source/install mismatch, ownership change,
recorder/validator change, existing fresh evidence root, active ROS/Gazebo
process, or incomplete qualification.

### Fixed M4.6 paired visible probe

Only after every no-Gazebo gate passes may one fresh-version paired probe
reuse the failed M4.5 seed to isolate the threshold correction:

```text
suite:       phase08_v7_m4_6_visible_probe
version:     phase08-v7-m4-6-probe
case:        v7_m4_6_probe_r2p0_a45_h25_18508
local:       (1.4142135623730951, 1.4142135623730950)
seed:        18508
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_6_probe
```

Reusing the seed is a declared paired correction test, not an M4.5 retry:
the experiment version, case identity, input bytes, and evidence root are
fresh, and the only behavioral parameter delta is `-0.90 -> -0.80`.

The attempt must use visible Gazebo and pass active-controller preflight,
`48/48` recording, Stage A, exact one-fill cardinality, the primary
noninterpolated `1.20 m` Stage B gate, both complete staged budgets,
collision, forbidden state/event, final-zero, cleanup, and combined
predicates. It is retained without retry or in-run tuning.

### Conditional M4.6 two-light qualification

Only after the paired visible probe passes every declared predicate may this
fresh serial headless suite run:

| Case | Local position | Seed | Role |
|---|---|---:|---|
| `v7_m4_6_r1p0_a45_h25_18609` | `(0.7071067811865476, 0.7071067811865475)` | 18609 | spatial |
| `v7_m4_6_r1p5_a22p5_h25_18609` | `(1.38581929876693, 0.5740251485476346)` | 18609 | spatial |
| `v7_m4_6_r1p5_a45_h25_18609` | `(1.0606601717798214, 1.0606601717798212)` | 18609 | spatial |
| `v7_m4_6_r1p5_a67p5_h25_18609` | `(0.5740251485476348, 1.38581929876693)` | 18609 | spatial |
| `v7_m4_6_r2p0_a45_h25_18609` | `(1.4142135623730951, 1.4142135623730950)` | 18609 | spatial |
| `v7_m4_6_repeat_r1p5_a45_h25_18610` | `(1.0606601717798214, 1.0606601717798212)` | 18610 | repeat |
| `v7_m4_6_repeat_r1p5_a45_h25_18611` | `(1.0606601717798214, 1.0606601717798212)` | 18611 | repeat |
| `v7_m4_6_repeat_r1p5_a45_h25_18612` | `(1.0606601717798214, 1.0606601717798212)` | 18612 | repeat |

The suite uses:

```text
suite:       phase08_v7_m4_6_two_light_suite
version:     phase08-v7-m4-6
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_6
```

Two-light readiness requires the paired visible pass plus all five spatial
and all three repeat cases to pass every unchanged predicate. Every attempt
is retained. A behavioral, formal, infrastructure, or cleanup failure is not
retried inside M4.6. Cleanup failure stops later dispatch.

### M4.6 scope and milestone

M4.6 authorizes no three-light, Phase 09, physical, or hardware action. The
optional three-light probe remains separately user-authorized only after a
complete M4.6 two-light gate.

After approval, implement and qualify only the explicit `-0.80` fresh-input
calibration and its regressions. Checkpoint and commit the no-Gazebo
boundary, then checkpoint and commit the exact paired visible dispatch. Run
the paired visible attempt once; run the fixed serial headless suite only if
that visible gate passes completely.

## M4.7 dynamic source-resume corridor amendment

M4.6 is immutable and closed. Its one fixed visible attempt passed
controller startup/readiness, recording, fresh validation, cleanup,
collision, forbidden-evidence, final-zero, Stage A, exact one-fill
cardinality, the `480 s` Stage A bound, and the complete independent
`120 s` Stage B opportunity. It failed Stage B: the best post-Stage-A
distance was `2.6173470005 m`, so the conditional M4.6 headless suite did
not run.

The retained report is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_6_visible_probe_report.md

SHA-256
4a2f6b25c0098476f50e6eefe09f070805c77dc28c7c719707c5cf6b623b8836
```

M4.6 proves the evidence-calibrated detector arms. The downstream
source-continuity topology is incomplete:

- the generic safe selector ranks excess clearance before source alignment;
- an already-safe tangent is retained instead of being reconsidered as the
  robot moves;
- fixed fill clearance deactivates all guidance immediately;
- release requires neither projected source progress nor completion of the
  existing affine taper;
- post-recovery liveness and affine assistance end at that premature release.

The retained Stage B path stayed at least `1.2944790512 m` from every
physical wall face and at least `1.0944790512 m` inside the configured wall
inset. No collision, algorithm `TIMEOUT`, in-readiness `FAILSAFE`, or
room-boundary event occurred. M4.7 therefore does not relax wall, collision,
room, or global-proximity gates.

M4.7 is Plan-only until reviewed and explicitly approved. It does not
authorize a source edit, build, checkpoint beyond this Plan boundary,
Gazebo process, suite, three-light case, Phase 09 action, physical action,
or hardware action merely by existing.

### New default-off compatibility boundary

Add one Boolean and one finite positive distance:

```text
post_recovery_source_resume_enabled: false
post_recovery_source_resume_min_progress_m: 0.20
```

Both launch and supervisor defaults are exactly the values above. The new
mode is valid only when source-led handoff, source continuity, post-recovery
progress, recoverable navigation, and post-recovery guidance are enabled.

M4.5, M4.6, M4.4, M4.3, V6, legacy, and every historical scenario omit the
new Boolean. Omission must preserve the exact pre-M4.7 selector, fixed
clearance release, affine taper, liveness, event sequence, normalized
behavior, and defaults. Historical scenario bytes and retained evidence
remain immutable. Fresh M4.7 scenarios alone explicitly set:

```text
post_recovery_source_resume_enabled: true
post_recovery_source_resume_min_progress_m: 0.20
post_recovery_source_reversal_dot_threshold: -0.80
```

No global coordinate, declared source role, light identity, simulation
ground truth, future pose, or outcome is supplied to the supervisor. The
retained source direction remains derived only from the measured
source-led displacement already used by M4.5/M4.6.

### Source-continuity-specific hard-safe selector

Add a pure deterministic selector used only while the fresh corridor is
active. It enumerates the unchanged fixed candidates:

```text
0, +45, -45, +90, -90, +135, -135, 180 degrees
```

Every candidate first passes the unchanged finite geometry, physical-room
inset, active-fill segment, and forward source-half-plane checks. No unsafe
candidate may be rescued by scoring.

Among eligible candidates, rank lexicographically by:

1. greatest dot product with the retained measured source direction;
2. greatest hard-safe clearance;
3. smallest absolute rotation;
4. existing deterministic candidate order.

This is intentionally different from the generic M4.6 selector, which ranks
clearance first. The corridor selector must be recomputed on every new valid
pose. Retaining a previously safe candidate is insufficient. The published
safe-direction revision changes only when the selected candidate changes,
not on every callback.

At the retained M4.6 arm geometry:

```text
source-led anchor:          (1.2274432561, 1.4964333762) m
arm position:               (1.3411590516, 1.5118024925) m
fill center:                (1.8189935808, 1.7649913445) m
fill avoidance radius:       0.6086747487 m
source direction:           (0.9909899820, 0.1339360130)
```

the only initially eligible candidate remains the necessary `-90 degree`
tangent `(0.1339360130, -0.9909899820)`. This preserves hard safety rather
than pretending a direct route already exists.

Exact pure-geometry regressions must then prove:

```text
after 0.200 m on the initial tangent:
  -45 degree candidate: hard-safe
  source alignment:     0.7071067812
  corridor selection:   -45 degrees
  generic M4.6 choice:  -90 degrees

after 0.425 m on the initial tangent:
  direct candidate:     hard-safe
  source alignment:     1.0
  corridor selection:   0 degrees
  generic M4.6 choice:  -90 degrees
```

These points establish candidate ordering and dynamic reacquisition; they
are not simulated waypoints and are never supplied to the live algorithm.

### Two-stage continuity corridor

When the existing M4.6 detector arms and the fresh resume mode is enabled,
the existing source-led anchor and measured source direction become an
immutable corridor record. The corridor has two internal stages while the
public supervisor state remains `SEARCH`.

#### Contour/reacquisition stage

The initial tangent is allowed only while it is the best hard-safe
source-half-plane candidate. The selector is recomputed for every new pose,
so a `-45 degree` or direct candidate replaces the tangent immediately when
it becomes hard-safe.

The unchanged clearance target remains:

```text
active support radius
+ fill avoidance margin
+ post_recovery_source_bypass_clearance_m
```

For the retained M4.6 fill this is `0.7086747487 m`. Reaching it no longer
deactivates guidance. It emits a bounded configuration event, transitions
to the source-resume stage, and records the current finite pose as the
source-resume anchor.

#### Source-resume stage

Define signed source progress from live odometry only:

```text
dot(current_position - source_resume_anchor, retained_source_direction)
```

Normal corridor completion requires:

```text
signed source progress >= 0.20 m
and live fill distance >= the fixed clearance target
and existing total outward progress
    >= post_recovery_guidance_min_progress_m
       + post_recovery_affine_taper_distance_m
```

With the frozen M4.7 values, the final conjunct remains the existing
`0.60 + 0.50 = 1.10 m` outward/taper boundary. Thus `0.20 m` is a minimum
source-resumption proof, not a replacement for the existing spatial
guidance completion.

At `0.20 m` signed source progress, the corridor records that source motion
has resumed but does not release early if the existing outward/taper
boundary is incomplete. The source-specific selector, hard-safe command
sweep, affine support, and liveness monitoring remain active until all
normal completion predicates hold. The runner's valid global-proximity stop
may preempt the corridor at any time after Stage A, as before.

If a recoverable recenter occurs during contour/reacquisition, preserve the
measured source direction and corridor stage. If it occurs during
source-resume, reset the resume anchor on the subsequent `RECENTER ->
SEARCH` boundary so recenter translation cannot be miscounted as source
progress. Only one bounded post-recovery recenter remains available under
the unchanged recovery limits.

### Affine, command, and liveness behavior

While contour/reacquisition or source-resume has not yet proved `0.20 m`
signed source progress:

- publish the configured `0.50` affine weight with no spatial taper;
- bind that affine term to the current hard-safe corridor direction;
- compute supervisor translation remaining from the missing signed source
  progress rather than fill-radial progress;
- retain the unchanged command-sweep, stale-data, room, fill, and finite-data
  checks.

After source progress is proved, retain the existing spatial taper from
`0.50` toward zero as outward progress moves from `0.60 m` through
`1.10 m`. Normal guidance release therefore occurs with the affine term
already at zero rather than dropping it at fixed clearance.

The existing liveness window remains:

```text
12.0 s
0.60 m minimum path
0.20 m maximum net displacement
```

Dynamic direction reacquisition does not consume the one historical
direction-refresh count merely because a better candidate becomes safe.
If the corridor stalls, retain the existing bounded recoverable-recenter
path. After that one recenter, another stall keeps the hard-safe corridor
active until normal completion or the unchanged total
`post_recovery_guidance_max_sec=90.0` boundary; it does not silently drop
affine/liveness at the first post-recenter window. Duration exhaustion still
publishes explicit evidence, zeros the supervisor command and affine term,
and continues ordinary GESC search rather than introducing a new failsafe.

No corridor condition suppresses a non-ground collision, invalid/stale
required input, controller/graph ownership fault, explicit stop, physical
room-face violation, final-zero requirement, or cleanup failure.

### Required observability

The existing supervisor producer emits finite configuration events for:

```text
post-recovery source-resume corridor armed
post-recovery source-continuity direction changed
post-recovery source-bypass clearance acquired
post-recovery source progress acquired
post-recovery source-resume corridor completed
post-recovery source-resume corridor exhausted
```

Events report only measured or configured values, including the selected
direction and revision, source alignment, hard-safe clearance, fill
distance/target, signed source progress/threshold, outward progress/release
boundary, affine weight, liveness state, recenter state, and guidance
elapsed/maximum duration.

Do not add a new node, topic, message, recorder, validator, analyzer,
controller, launch graph, or producer namespace. Extend the existing
supervisor and current evidence-prefix attribution. The Phase 05 recorder
and validator remain the sole recorder/validator owners.

### Preserved acceptance and safety contract

M4.7 retains:

```text
room bounds:                       [-0.25, 3.75] x [-0.25, 3.75] m
room center:                       (1.75, 1.75) m
start:                             (0.0, 0.0), yaw 0
global:                            (3.5, 3.5), input 1600.0
local input:                       400.0
known topology:                    1 local, 1 global
maximum fill clusters:             1
detector path / efficiency gate:   0.20 m / 0.50
wall margin:                       0.20 m
fill minimum valid samples:        40
recenter maximum / tolerance:       60.0 s / 0.15 m
source-led window:                  12.0 s
post-recovery liveness:             0.60 m path / 0.20 m net
continuity reversal threshold:     -0.80
bypass clearance:                  avoidance radius + 0.10 m
source-resume minimum progress:     0.20 m
primary Stage B:                    1.20 m
closer diagnostic:                 1.00 m, non-gating
Stage A / Stage B budgets:          480.0 s / 120.0 s
run / wall timeout:                 600.0 s / 780.0 s
collision expected:                false
```

The first valid post-Stage-A noninterpolated odometry sample at or inside
`1.20 m` still triggers the operator-equivalent graceful stop. No
`GOAL_HOLD`, dwell, post-arrival stability, or closer-than-`1.20 m`
requirement is added.

### Intended implementation files

Extend only the existing owners:

```text
ros2_ws/src/ros_esc/ros_esc/supervisor_node/escape_recenter.py
ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py
ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml
```

Modify focused contract/regression tests as required:

```text
ros2_ws/src/ros_esc/test/test_escape_recenter.py
ros2_ws/src/ros_esc/test/test_supervisor_integration.py
ros2_ws/src/ros_esc/test/test_scenario_schema.py
ros2_ws/src/ros_esc/test/test_scenario_runner.py
ros2_ws/src/ros_esc/test/test_observability_contract.py
```

Create fresh fixed inputs:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v7_m4_7_visible_probe.yaml
  phase08_v7_m4_7_two_light_suite.yaml
```

Update the live status, Phase 08 checkpoint, and fresh M4.7 validation
records only at their declared boundaries. Do not modify the Phase 05
recorder/validator, robust or legacy controller, modified-cost node, central
algorithm graph, controller-spawner helper, world files, M4.6 inputs, or any
historical artifact.

### No-Gazebo qualification

Before any M4.7 Gazebo process starts:

1. seal the M4.6 report, summary, completeness, scenario result, bag,
   analysis, resolved-scenario, and installed-scenario hashes;
2. prove M4.6's generic selector and exact fixed-clearance release remain
   unchanged when the new mode is false;
3. replay the exact M4.6 live arm/fill/source geometry and prove the
   initial `-90`, later `-45`, and later direct source-specific selections
   above;
4. prove every corridor selection is finite, hard-safe, inside the room
   inset, outside forbidden fill segments, and in the nonnegative measured
   source half-plane;
5. prove clearance transitions into source-resume without clearing the
   retained direction, safe direction, affine term, liveness tracker, or
   general guidance;
6. prove `0.20 m` signed source progress has exact boundary behavior,
   excludes recenter displacement, and cannot release without live
   clearance plus the existing `1.10 m` outward/taper completion;
7. prove affine remains `0.50` before the source gate, then follows the
   existing taper to zero; prove supervisor translation uses the missing
   source progress and every nonzero command passes the unchanged sweep;
8. prove dynamic candidate upgrades do not spend the historical refresh
   budget, while stall, one recoverable recenter, post-recenter persistence,
   duration exhaustion, no-candidate, stale/nonfinite geometry, and
   explicit-stop paths remain bounded and observable;
9. prove the mode dependencies, Boolean and positive-double schema,
   DOUBLE launch value `0.20`, configuration evidence, producer attribution,
   scenario pass-through, and source/install parity;
10. prove M4.6, M4.5, M4.4, M4.3, V6, shifted/historical worlds, all
    historical normalized case keys, scenario files, retained summaries,
    cost sign/units, canonical topics, and sole `/cmd_vel` ownership remain
    unchanged;
11. prove every fresh normalized M4.7 case differs from its M4.6 counterpart
    only by fresh identity/seed plus the two explicit resume fields; preserve
    `480 + 120 <= 600 s`, one local/global, maximum one fill, the primary
    `1.20 m` stop, the non-gating `1.00 m` diagnostic, final zero, and cleanup;
12. run focused helper, supervisor, state-machine, schema, runner,
    observability, recording, and controller-startup regressions;
13. run broad ROS-independent functional tests, fatal changed-file lint,
    Python compilation, XML/YAML parsing, isolated three-package build,
    installed dry-runs, nonexecuting launch instantiation, source/install
    parity, context validation, and historical/evidence hash checks;
14. update live status and a fresh no-Gazebo validation report, checkpoint
    Phase 08, inspect the exact diff, and commit the qualified boundary
    before recording a simulation dispatch.

Stop before Gazebo on any failed regression, M4.6/historical drift,
source/install mismatch, ownership change, recorder/validator change,
existing fresh evidence root, active ROS/Gazebo process, or incomplete
qualification.

### Fixed M4.7 paired visible probe

Only after explicit M4.7 approval, complete no-Gazebo qualification, a
material checkpoint, and a bounded commit may one fresh-version paired probe
reuse the failed M4.6 seed to isolate the topology correction:

```text
suite:       phase08_v7_m4_7_visible_probe
version:     phase08-v7-m4-7-probe
case:        v7_m4_7_probe_r2p0_a45_h25_18508
local:       (1.4142135623730951, 1.4142135623730950)
seed:        18508
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_7_probe
```

Reusing the seed is a declared paired correction test, not an M4.6 retry:
the experiment version, case identity, input bytes, and evidence root are
fresh. The resume mode is the only behavioral delta from M4.6.

The attempt must use visible Gazebo and pass active-controller preflight,
`48/48` recording, Stage A, exact one-fill cardinality, the primary
noninterpolated `1.20 m` Stage B gate, both complete staged budgets,
collision, forbidden state/event, final-zero, cleanup, and combined
predicates. It is retained without retry or in-run tuning.

### Conditional M4.7 two-light qualification

Only after the paired visible probe passes every declared predicate may this
fresh serial headless suite run:

| Case | Local position | Seed | Role |
|---|---|---:|---|
| `v7_m4_7_r1p0_a45_h25_18709` | `(0.7071067811865476, 0.7071067811865475)` | 18709 | spatial |
| `v7_m4_7_r1p5_a22p5_h25_18709` | `(1.38581929876693, 0.5740251485476346)` | 18709 | spatial |
| `v7_m4_7_r1p5_a45_h25_18709` | `(1.0606601717798214, 1.0606601717798212)` | 18709 | spatial |
| `v7_m4_7_r1p5_a67p5_h25_18709` | `(0.5740251485476348, 1.38581929876693)` | 18709 | spatial |
| `v7_m4_7_r2p0_a45_h25_18709` | `(1.4142135623730951, 1.4142135623730950)` | 18709 | spatial |
| `v7_m4_7_repeat_r1p5_a45_h25_18710` | `(1.0606601717798214, 1.0606601717798212)` | 18710 | repeat |
| `v7_m4_7_repeat_r1p5_a45_h25_18711` | `(1.0606601717798214, 1.0606601717798212)` | 18711 | repeat |
| `v7_m4_7_repeat_r1p5_a45_h25_18712` | `(1.0606601717798214, 1.0606601717798212)` | 18712 | repeat |

The suite uses:

```text
suite:       phase08_v7_m4_7_two_light_suite
version:     phase08-v7-m4-7
evidence:
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_7
```

Two-light readiness requires the paired visible pass plus all five spatial
and all three repeat cases to pass every unchanged predicate. Every attempt
is retained. A behavioral, formal, infrastructure, or cleanup failure is not
retried inside M4.7. Cleanup failure stops later dispatch.

### M4.7 scope and milestone

M4.7 authorizes no three-light, Phase 09, physical, or hardware action. The
optional three-light probe remains separately user-authorized only after a
complete M4.7 two-light gate.

After explicit approval, implement and qualify only the default-off dynamic
source-resume corridor, regression coverage, and fresh fixed inputs without
Gazebo. Checkpoint and commit the exact no-Gazebo boundary. Only then record
and checkpoint the paired visible dispatch. Run the paired visible attempt
once; run the fixed serial headless suite only if that visible gate passes
completely.
