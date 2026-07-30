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
