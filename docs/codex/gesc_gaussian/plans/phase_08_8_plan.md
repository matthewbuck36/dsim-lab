# Phase 08.8 Plan — Counted-Source Open-Field Reproducibility

## Status and authority

**APPROVED FOR IMPLEMENTATION AND BOUNDED GAZEBO EXECUTION (2026-07-30).**

The user authorized implementation of this Plan, bounded corrections needed to
make it work, and Gazebo execution after the M1-M2 no-Gazebo qualification and
checkpoint. Physical hardware remains unauthorized in Phase 08.

This is a separately versioned diagnostic and reproducibility iteration after
the closed Phase 08 boundary. It does not reopen, overwrite, relabel, or add to
the acceptance denominator of any Phase 08 v1-v6 or Phase 08.7 result. In
particular, it preserves the final Phase 08 disposition that broad simulation
readiness failed.

The normal Phase 09 Plan preflight currently fails because no prior experiment
declared `simulation_ready=true`. Phase 08 Plan context passes. This work is
therefore intentionally planned as Phase 08.8 rather than being hidden inside
physical integration. Phase 09 physical-interface work remains a separate
future request.

This Plan records the user's following research and experiment decisions:

- the controller may know the **total number of signal sources** in the field;
- source positions, source roles, the global source position, room dimensions,
  and global robot position remain unavailable to the controller;
- Vicon and simulator ground truth are evaluation-only;
- every confirmed extremum is initially an unknown candidate;
- with two known sources, the first distinct confirmed candidate in the
  selected experiment must be filled and escaped, and the next distinct
  candidate must be compared against it using raw cost;
- the physical and simulated operating region for this iteration may be
  treated as open and obstacle-free;
- autonomous wall and obstacle avoidance is not part of this assignment;
- walls are an operator-managed physical concern and future research task;
- no new dead-reckoned route map, room map, waypoint planner, or traveled-path
  memory is to be introduced in this iteration;
- raw cost is authoritative for extremum comparison, while augmented cost is
  used for Gaussian-assisted motion;
- direct convergence to the global without a completed local recovery is not
  an accepted result;
- physical arrival will remain operator-terminated with `Ctrl+C`; no physical
  coordinate-distance stop is allowed.

## Objective and scope

Implement and qualify one minimal, selectable GESC-plus-Gaussian behavior that
reliably reproduces:

```text
find first distinct extremum candidate
-> characterize its raw cost over complete sensor rotations
-> create exactly one adaptive Gaussian fill
-> escape it without recentering or wall guidance
-> resume ordinary GESC on raw + Gaussian cost
-> find the second distinct extremum candidate
-> compare the two rotation-stable raw-cost summaries
-> verify that the second candidate is the stronger minimum
-> hold for evaluation / operator Ctrl+C
```

The first empirical target is exactly two sources at the retained
simulator-relative `400/1600` (`1:4`) input ratio in one primary and one
secondary fixed layout. Those frozen demonstrations remain the qualification
gate before broader testing.

The implementation must make the first layout pass ten consecutive fresh
process-level repeats and the second layout pass five consecutive fresh
process-level repeats. A direct route to the global, a missing fill, a fill at
the second/global candidate, a duplicate fill, or failure to compare the
candidate costs is not a behavioral pass.

### Approved execution amendment — broader supported envelope

The user additionally authorized bounded Plan and code amendments while
executing Phase 08.8 and requested that every dispatched simulation pass across
different light positions and intensities. After the frozen primary and
secondary gates pass, this iteration may therefore add a versioned broadening
matrix for two-source, open-field layouts and intensity ratios.

“Any layout or intensity” cannot be a literal guarantee over continuous,
unbounded inputs. Some declarations do not produce two observable extrema in
the aggregate field—for example, coincident sources, a zero-strength source,
or sufficiently merged fields. In those cases no sensor-only algorithm can
demonstrate escape from a local extremum that does not exist. The supported
envelope must consequently require:

- exactly two positive, finite source inputs;
- two distinct aggregate-field extrema detectable by the same onboard signal
  and confirmation contract available to the controller;
- both extrema within the declared finite test horizon and obstacle-free
  operating region;
- a strict raw-cost ordering resolvable beyond measured uncertainty;
- no use of declared source positions, intensities, roles, evaluator geometry,
  or simulator ground truth by the controller.

Every scenario admitted to the final versioned broadening matrix must pass; it
may not be silently omitted, retried, or relabeled after dispatch. Scenarios
that fail the observable-topology preflight are reported as outside the
supported envelope, not as algorithm passes. The exact matrix and preflight
method may be amended only after the fixed `1:4` gates establish a stable
baseline, and any broad claim must match the executed evidence.

### In scope

- a known-total-source-count extremum-classification policy in the existing
  supervisor;
- rotation-stable raw-cost summaries for candidate comparison;
- use of the existing active fill registry to reject revisits to the already
  filled candidate;
- a deterministic convergence-confirmation option that is based on qualified
  dwell rather than a timing-sensitive count of threshold crossings;
- an opt-in open-field mode that disables configured room-bound and recenter
  behavior;
- a direct `ESCAPE_REPULSE -> SEARCH` recovery path;
- exact evidence for candidate order, candidate raw costs, fill count, local
  recovery, final ranked candidate, final-zero, recording, and cleanup;
- one visible primary probe followed by a sealed primary repeat suite;
- one visible secondary probe followed by a sealed secondary repeat suite;
- ROS-independent tests of the same policy with `known_source_count=3`, without
  executing a three-light Gazebo scenario.

### Explicitly out of scope

- physical hardware motion or physical launch execution;
- Phase 09 adapter implementation;
- Vicon, GPS, global-pose, source-position, or room-map input to the controller;
- a new dead-reckoning, SLAM, route-memory, waypoint, coverage, or planner
  subsystem;
- autonomous wall, collision, or obstacle avoidance;
- log/control barrier functions;
- automatic physical distance-to-global termination;
- Heavy-Ball, RMSprop, AdaGrad, or another ESC core;
- a three-light Gazebo run;
- tuning the frozen primary or secondary `1:4` gates after dispatch;
- a selection-blind holdout, simulation-ready tag, or general robustness
  claim;
- an unbounded or topology-blind claim over arbitrary source declarations;
- changing or deleting any historical world, scenario, run, report, or
  result.

## Repository findings

### Current durable boundary

At Plan creation:

```text
branch: feature/gesc-gaussian-robustness-v1
HEAD:   bc25fef phase 08: close final report boundary
tree:   clean
remote: local branch is 103 commits ahead of
        origin/feature/gesc-gaussian-robustness-v1
```

`validate_phase_context.sh 08 plan` passes. The Phase 09 Plan validator stops
because Phase 08 never declared simulation readiness. This Plan must not be
used to bypass that gate.

### Retained evidence that justifies this iteration

The Phase 08.7 M4.8 retained-success reproduction executed seventeen selected
two-light definitions exactly once:

```text
formal combined pass:                 13/17
behavioral pass:                      14/17
Stage A local recovery:               16/17
exact one-fill cardinality:           16/17
Stage B after completed Stage A:      14/16
collision/forbidden evidence:         17/17
final command zero:                   17/17
cleanup:                              17/17
```

All sixteen completed recoveries used the direct state path. None entered
`ESCAPE_ASSIST`. The fixed `400/1600` ratio is therefore the strongest
retained condition for a simple two-light demonstration.

The three behavioral disagreements were bounded:

1. one old profile completed Stage A very late and had only `66.810 s` of its
   fixed total horizon left;
2. one radius-2.0 case missed the old `1.20 m` boundary by `0.013880 m` after
   consuming its full Stage B budget;
3. one radius-1.0 case received only two of the detector's three required
   threshold crossings, so Stage A never started even though the historical
   same-seed execution had confirmed.

The first two were not wall, collision, or failsafe stops. The third was a
detector-confirmation repeatability defect upstream of Gaussian recovery.

### Baseline Git-history finding

The first commit unique to the branch after `main` is:

```text
2af9064 Add heavy-ball ESC work and supporting ROS nodes
```

It is not a valid rollback target because it introduces Heavy-Ball behavior,
which this project has explicitly retired.

The last pre-phased repository boundary, `e0c693e`, contains the simpler
pre-supervisor GESC/Gaussian structure that the user remembers: convergence
counter, event-triggered Gaussian fill, modified cost, PDE history, and no
robust room-recenter state machine. Phase 08.8 will not revert to that commit.
It will reproduce the useful simple flow as a new opt-in policy while retaining
the current typed fills, adaptive estimator, validated recorder, shutdown
behavior, and selectable historical behavior.

### Current owners

The current repository already has one owner for each required function:

- convergence confirmation:
  `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/`
  `convergence_detector_node_script.py`;
- state transitions and source verification:
  `ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py`;
- ROS cost/pose/fill adaptation and evidence:
  `ros2_ws/src/ros_esc/ros_esc/supervisor_node/`
  `supervisor_node_script.py`;
- geometry helpers:
  `ros2_ws/src/ros_esc/ros_esc/supervisor_node/escape_recenter.py`;
- raw basin estimation:
  `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/basin_estimator.py`;
- adaptive anisotropic fill design:
  `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_designer.py`;
- fill identities, revisions, and associations:
  `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_registry.py`;
- ROS fill adapter:
  `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/`
  `gaussian_fill_script.py`;
- raw + Gaussian + affine decomposition:
  `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/`
  `modified_cost_script.py`;
- launch graph:
  `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`;
- scenario schema, execution, and staged validation:
  `ros2_ws/src/ros_esc/ros_esc/scenario_runner/`;
- authoritative recorder and validator:
  `ros2_ws/src/ros_esc/ros_esc/experiment_recording/`;
- bag analysis:
  `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/`
  `gesc_gaussian_bag_analysis.py`.

No new node, package, message, topic, dependency, recorder, validator, or
launch graph is justified.

### Existing adaptivity to preserve

The current fill implementation already:

- synchronizes pose, raw cost, and source-score samples;
- filters invalid, excessive-speed, and MAD-outlier samples;
- estimates an event-centered basin and covariance;
- constructs an anisotropic Gaussian from basin depth and curvature;
- validates residual minima on a bounded grid;
- escalates amplitude and width together;
- merges associated observations as immutable revisions.

Phase 08.8 must not replace this with the original fixed scalar fill. The
remaining planned adaptation is in confirmation and classification, upstream
of fill design.

## Adopted controller contract

### Information boundary

The algorithm may consume:

- rotating photoresistor-derived raw cost and source score;
- rotating-frame encoder/transform information already used by GESC;
- the existing relative `/odom` stream required by PDE history and Gaussian
  fill placement;
- active typed Gaussian fills;
- the integer `known_source_count`.

It may not consume:

- declared source coordinates or evaluation roles;
- Vicon pose;
- global source proximity;
- room dimensions or a room center in the new open-field mode;
- simulator contact or ground-truth outcome as a control input.

The use of existing `/odom` is unchanged. Phase 08.8 does not add a second
pose estimator or use odometry to plan routes.

### Known-count candidate policy

Add a selectable supervisor policy:

```text
extremum_classification_mode = absolute_source_score | counted_candidates
```

The existing default remains `absolute_source_score`.

For `counted_candidates`:

```text
known_source_count = N
required_local_fill_count = N - 1
max_fill_clusters = N - 1
```

The implementation must reject contradictory values before authorizing
motion. `N` must be at least `2` for this policy.

For each distinct confirmed candidate:

1. collect complete-rotation raw-cost evidence;
2. calculate and retain a robust raw-cost summary and uncertainty;
3. if fewer than `N - 1` distinct fill clusters exist, classify the candidate
   as recoverable without consulting the absolute goal threshold;
4. design or merge exactly one fill for that candidate and complete escape;
5. when `N - 1` fills exist, do not create another fill;
6. reject/suppress a convergence event associated with an already active fill
   cluster as a revisit rather than counting it as another source;
7. compare a new distinct terminal candidate to all retained filled
   candidates;
8. for minimization, accept it as the final best candidate only when its
   uncertainty interval lies strictly below every retained candidate interval;
9. otherwise resume search until the bounded scenario timeout, without
   creating an extra fill or falsely claiming a global.

This policy deliberately handles the approved layout order:

```text
first encountered source(s) = local candidate(s)
last distinct source = stronger global candidate
```

It does not solve the case where the global is encountered and filled first.
That would require reversible fills and return-to-best navigation, which is
outside this no-new-dead-reckoning iteration.

### Rotation-stable raw-cost comparison

The existing `RotationScoreWindow` must not be used as an instantaneous proxy
for raw cost. Extend the same owner with a raw-cost window:

- one window equals one complete physical sensor rotation;
- record the minimum valid raw cost observed during each rotation because this
  is a minimization problem with a directional photoresistor;
- require two complete rotations by default;
- use the median of completed-rotation minima as the candidate estimate;
- use MAD-based dispersion as the uncertainty term;
- compare candidates using nonoverlapping uncertainty intervals;
- record the estimate, dispersion, rotation count, candidate ordinal, filled
  candidate count, and known total in `AlgorithmEvent.value_names/values`;
- continue recording source score as a diagnostic, but do not use the absolute
  `goal_score_threshold` in counted-candidate mode.

No declared source intensity or position participates in this comparison.

### Raw and augmented cost roles

The following contract is mandatory:

```text
raw CostBreakdown.raw_cost:
    convergence-candidate characterization
    candidate ranking
    retained scientific evidence

raw /pde_cost_history:
    basin estimation and fill design

typed Gaussian fills:
    persistent memory of already recovered basins

/cost_modified:
    GESC motion after applying active Gaussian cost
```

The candidate comparison must never use augmented cost. Fill estimation must
not silently switch to a history already altered by the fill being estimated.

### Open-field direct recovery

Add a backward-compatible launch/supervisor switch:

```text
operating_bounds_enabled = True
```

Historical behavior keeps the `True` default. New Phase 08.8 scenarios set it
to `False`.

With bounds disabled:

- the supervisor does not instantiate or enforce the configured virtual room
  inset;
- no boundary-triggered recenter request is generated;
- no safe-direction candidate is rejected because of a configured wall;
- invalid/stale pose and sensor data remain failsafe conditions;
- explicit stop, controller watchdog, fill-design timeout, final-zero, and
  shutdown behavior remain unchanged.

The new scenarios additionally set:

```text
recenter_after_escape = False
post_recovery_guidance_enabled = False
recoverable_navigation_enabled = False
modified_cost_enable_affine_bias = False
```

The primary local-recovery path becomes:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> SEARCH
```

This is not a deletion of recenter or affine behavior. Those mechanisms remain
selectable and unchanged for all historical scenarios.

### Deterministic convergence confirmation

The current detector's default three-crossing counter remains unchanged for
historical scenarios. Add:

```text
convergence_confirmation_policy =
    crossing_count | qualified_dwell
convergence_confirmation_dwell_sec = 6.0
convergence_confirmation_exit_threshold_scale = 1.5
```

The Phase 08.8 scenarios select `qualified_dwell`.

In qualified-dwell mode:

- state gating and search-epoch reset remain mandatory;
- the existing motion/path qualification must be satisfied;
- the convergence metric must enter below the existing threshold;
- evidence accumulates while it remains below the threshold;
- the evidence is reset only after the metric exceeds the larger hysteresis
  exit threshold;
- one confirmation is published after `6.0 s`, corresponding to two complete
  three-second sensor rotations;
- a search-epoch change, backward clock, invalid/nonfinite sample, or loss of
  the qualifying motion contract resets the dwell;
- the old convergence-candidate events remain diagnostic;
- exactly one confirmation may be emitted for one uninterrupted qualified
  episode.

This replaces timing-sensitive crossing cardinality only in the new scenario
profile. It must not weaken spatial association, fill validation, or the
requirement that the first confirmation occur near the declared local in
evaluation.

## Public interfaces and parameters

### Topics and messages

No topic or message is added.

Continue using:

```text
/gesc_gaussian/cost_breakdown
/gesc_gaussian/source_cost
/gesc_gaussian/convergence_status
/gesc_gaussian/gaussian_fills
/gesc_gaussian/algorithm_state
/gesc_gaussian/algorithm_events
/gesc_gaussian/supervisor_command
/gesc_gaussian/stop_requested
/pde_history
/pde_cost_history
/cost_modified
/cmd_vel
```

Use the existing `AlgorithmEvent` fields to report counted-candidate evidence.
Use the existing `EVENT_GOAL_REACHED` only after the count and raw-cost ranking
contract passes. No event emitted from simulator ground truth may cause that
controller event.

### New parameters and launch arguments

All new defaults preserve current behavior:

| Parameter / launch argument | Type | Default | Phase 08.8 value | Owner |
|---|---|---:|---:|---|
| `extremum_classification_mode` | string | `absolute_source_score` | `counted_candidates` | supervisor |
| `known_source_count` | integer | `0` | `2` | supervisor |
| `candidate_cost_rotation_period_sec` | double | `3.0` | `3.0` | supervisor |
| `candidate_cost_required_rotations` | integer | `2` | `2` | supervisor |
| `candidate_cost_mad_scale` | double | `3.0` | `3.0` | supervisor |
| `operating_bounds_enabled` | boolean | `True` | `False` | supervisor |
| `convergence_confirmation_policy` | string | `crossing_count` | `qualified_dwell` | detector |
| `convergence_confirmation_dwell_sec` | double | `6.0` | `6.0` | detector |
| `convergence_confirmation_exit_threshold_scale` | double | `1.5` | `1.5` | detector |

The implementation must validate types and finite ranges at startup. The
scenario resolver must require:

```text
known_source_count =
    expected_local_minima + expected_global_minima
expected_global_minima = 1
gaussian_fill_max_fills = known_source_count - 1
max_fill_clusters = known_source_count - 1
```

Only the total integer is passed to the controller. Declared roles and
positions remain evaluator-only.

### Simulation termination

The scenario runner may stop a passing simulation only after both:

1. the controller has emitted a valid post-recovery `GOAL_REACHED` event from
   counted-candidate raw-cost ranking; and
2. a noninterpolated simulator odometry sample is within `0.50 m` of the
   declared global source.

The coordinate proximity check is evaluator-only. It must not be exposed as a
supervisor input.

Physical mode must continue to ignore this stop and run until operator
`Ctrl+C`.

## Backward compatibility and migration

- `legacy` remains unchanged and selectable.
- Historical `robust_gaussian_v1` defaults remain unchanged.
- Every historical Phase 08 scenario retains its current parameters, world,
  contacts, required state path, results, and hashes.
- Absolute source-score classification remains the default.
- Crossing-count convergence confirmation remains the default.
- Operating bounds remain enabled by default.
- Recenter and affine implementations are retained.
- The new behavior is activated only by explicit Phase 08.8 launch overrides.
- Cost sign, cost units, `/cmd_vel` ownership, canonical topic names, and the
  raw/Gaussian/affine decomposition do not change.
- Simulation and later physical execution will use the same counted-source
  supervisor logic; only ground-truth evaluation and simulation stop logic are
  simulation-specific.

No migration of saved runs is permitted.

## Files to modify during implementation

### Algorithm owners

1. `ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py`
   - add counted-candidate configuration and deterministic transitions;
   - retain candidate summaries and filled-candidate count;
   - require `N - 1` local fills before `GOAL_HOLD`;
   - preserve absolute-score behavior as the default.

2. `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py`
   - add complete-rotation raw-cost aggregation;
   - validate the known-count/fill-budget invariant;
   - associate convergence centers with active fill clusters;
   - expose counted-candidate evidence in existing events;
   - bypass operating-bound geometry only when explicitly disabled.

3. `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/`
   `convergence_detector_node_script.py`
   - add the opt-in hysteretic qualified-dwell confirmation policy;
   - preserve crossing-count behavior byte-for-behavior under its default.

4. `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
   - expose and type the new detector/supervisor parameters;
   - keep all existing defaults.

### Scenario and evidence owners

5. `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py`
   - allow and validate the new launch overrides;
   - bind known total to declared topology without exposing positions;
   - support the direct no-recenter recovery contract;
   - support a controller-goal-event prerequisite for simulation proximity
     stopping.

6. `ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py`
   - pass only the known total to the controller;
   - require both ranked controller goal and evaluator proximity for the new
     scenario stop;
   - use the existing `gazebo_empty.world` through the normal launch default.

7. `ros2_ws/src/ros_esc/ros_esc/scenario_runner/phase08_validation.py`
   - validate candidate order, raw-cost ranking, exact fill count, direct
     escape-to-search recovery, ranked goal, and post-recovery proximity;
   - report wall/collision behavior as not applicable for the new open-field
     contract rather than as a behavioral pass.

8. `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/`
   `gesc_gaussian_bag_analysis.py`
   - extract the existing event value arrays into a candidate comparison table;
   - keep all historical analysis outputs readable.

### Tests

9. `ros2_ws/src/ros_esc/test/test_state_machine.py`
10. `ros2_ws/src/ros_esc/test/test_supervisor_integration.py`
11. `ros2_ws/src/ros_esc/test/test_convergence_detector_policy.py`
12. `ros2_ws/src/ros_esc/test/test_scenario_schema.py`
13. `ros2_ws/src/ros_esc/test/test_scenario_runner.py`
14. `ros2_ws/src/ros_esc/test/test_phase08_validation.py`
15. `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`
16. `ros2_ws/src/ros_esc/test/test_robust_gaussian_algorithm.py`

Tests must cover two-source execution, ROS-independent three-source state
logic, revisits, ambiguous ranking, invalid count/fill combinations, detector
hysteresis, default compatibility, and final-zero behavior.

## Files to create during implementation

No source package, node, message, topic, dependency, world, recorder, or
validator will be created.

Create only versioned scenarios and durable evidence:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v8_primary_visible_probe.yaml
  phase08_v8_primary_repeats.yaml
  phase08_v8_secondary_visible_probe.yaml
  phase08_v8_secondary_repeats.yaml

docs/codex/gesc_gaussian/validation/
  phase_08_8_baseline_audit.md
  phase_08_8_no_gazebo_qualification.md
  phase_08_8_primary_report.md
  phase_08_8_secondary_report.md
  phase_08_8_final_report.md

docs/codex/gesc_gaussian/handoffs/
  phase_08_8_handoff.md
```

The shorter installed scenario names above replace the provisional
`phase08_v8_counted_*` filenames from the initial draft. Their fixed
definitions, profile identity, seeds, and acceptance contract are unchanged.
Any later broadening matrix receives a separate versioned scenario filename
and report rather than mutating these four files.

At implementation start, append a new Phase 08.8 section to the existing
`docs/codex/gesc_gaussian/status/phase_08_status.md`; do not rewrite its closed
Phase 08 history.

## Fixed scenario definitions

All Phase 08.8 Gazebo scenarios use:

```text
world:                  existing gazebo_empty.world
validation walls:       disabled
simulation contacts:    disabled
start:                  (0.0, 0.0), yaw 0
global evaluator point: (3.5, 3.5)
local/global inputs:    400/1600
known_source_count:     2
required fills:         1
sensor noise:           none
sensor delay:           0.0 s
pose delay:             0.0 s
global proximity:       0.50 m, evaluation-only
post-Stage-A budget:    180.0 s
```

### Primary layout

```text
local evaluator point:
    (1.0606601717798214, 1.0606601717798212)
    radius 1.5 m, angle 45 degrees

visible probe seed: 18801
repeat seeds:       18811 through 18820
```

### Secondary layout

```text
local evaluator point:
    (0.5740251485476348, 1.38581929876693)
    radius 1.5 m, angle 67.5 degrees

visible probe seed: 18851
repeat seeds:       18861 through 18865
```

The controller receives neither coordinate nor role. These definitions are
fixed now to avoid outcome-selected geometry changes.

## Implementation sequence

### M1 — Baseline audit and counted-source policy

1. Reconstruct the pre-phased simple behavior from `e0c693e` and explicitly
   document why `2af9064` is not a GESC rollback target.
2. Record a file-level semantic diff against current owners.
3. Add the counted-candidate pure state-machine contract.
4. Add raw-cost rotation aggregation and active-fill revisit suppression.
5. Add startup invariants for known count and fill cardinality.
6. Add ROS-independent two- and three-source tests.
7. Do not run Gazebo.

Next criterion: all counted-candidate unit tests and unchanged absolute-score
tests pass.

### M2 — Qualified detector and open-field direct recovery

1. Add the opt-in qualified-dwell detector policy and hysteresis.
2. Add the opt-in operating-bound bypass.
3. Wire a direct `ESCAPE_REPULSE -> SEARCH` path with recenter/affine disabled
   only in the new scenarios.
4. Extend schema, runner, validator, and analyzer contracts.
5. Create and resolve the four fixed scenario files.
6. Verify they use `gazebo_empty.world` and do not start a Gazebo process.
7. Run focused tests, broad functional regressions, isolated three-package
   build, installed launch instantiation, scenario dry-runs, and
   `git diff --check`.
8. Write `phase_08_8_no_gazebo_qualification.md`, update live status,
   checkpoint Phase 08, and commit if separately authorized.

Next criterion: M1-M2 must be qualified and checkpointed before any Gazebo
execution.

### M3 — One visible primary probe

After explicit Gazebo authorization:

1. launch the primary probe once with Gazebo GUI and normal-speed simulation;
2. do not retry;
3. retain the complete bag, result, logs, plots, and cleanup evidence;
4. require the first candidate to be associated with the local evaluator
   point, exactly one fill, direct recovery to `SEARCH`, a distinct second
   candidate, a strictly lower raw-cost interval, ranked `GOAL_REACHED`, and
   evaluator proximity within `0.50 m`;
5. stop on any behavioral, formal, recording, or cleanup failure.

Next criterion: one complete visible formal pass.

### Executed M3 disposition and approved M3.1 correction amendment

The fixed M3 execution of `phase08_v8_primary_visible_probe.yaml`, seed
`18801`, is closed as a retained behavioral failure. Recording, final-zero,
analysis, and cleanup passed. The first candidate, raw-cost summary, one-fill
cardinality, local association, and revisit suppression were correct. The
short direct escape stalled, entered the historical redesign/assist path, and
returned to the local basin before finding candidate two.

The complete fixed result and diagnosis are retained in
`phase_08_8_primary_probe.md` and commit `8ebb9cd`. The scenario is not to be
retried, tuned, renamed, or counted as a pass. Its original M4-M5 successors
are not dispatched.

The user's implementation authority permits a bounded, separately versioned
correction. M3.1 adds the missing finite open-field departure behavior without
changing the counted-source policy, detector, adaptive fill, GESC core, or any
historical default:

1. Add `open_field_escape_assist_enabled`, default `false`.
2. Permit it only in the opt-in unbounded/no-recenter/no-recoverable-navigation
   profile.
3. When `ESCAPE_REPULSE` reports a measured stall, transition directly to
   `ESCAPE_ASSIST` in the same escape episode; do not request a redesign and do
   not supersede or merge the accepted fill.
4. In that assist state, retain Gaussian cost and disable affine cost with
   weights `(raw=0, Gaussian=1, affine=0)`.
5. Select the supervisor direction radially outward from the frozen accepted
   fill center using current odometry. Publish a bounded differential-drive
   command through the existing supervisor/controller arbitration; do not add
   a node, publisher, planner, global coordinate, source role, source
   coordinate, Vicon pose, or room geometry.
6. Continue only until the measured frozen-fill exit criterion has held. Then
   zero the supervisor command and return to ordinary GESC `SEARCH`.
7. Use a larger fixed `exit_sigma=8.0` and `escape_max_sec=35.0` so the exit
   represents a durable departure rather than the failed v8 `0.423896 m`
   release. This is a versioned empirical correction, not a mutation of v8.
8. Record `ESCAPE_STALLED` and the assisted state path as required evidence.
   Continue to forbid fill merge/supersession, recenter, timeout, and failsafe.

The corrected Stage A path is:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
```

The terminal path adds:

```text
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

The new fixed inputs are:

```text
phase08_v8_1_primary_visible_probe.yaml
  seed 18901
  visible
  runs root phase08_8_1_primary_probe

phase08_v8_1_primary_repeats.yaml
  seeds 18911 through 18920
  headless
  runs root phase08_8_1_primary_repeats

phase08_v8_1_secondary_visible_probe.yaml
  seed 18951
  visible
  runs root phase08_8_1_secondary_probe

phase08_v8_1_secondary_repeats.yaml
  seeds 18961 through 18965
  headless
  runs root phase08_8_1_secondary_repeats
```

Source positions, `400/1600` inputs, start, topology, evaluator proximity,
Stage A and Stage B budgets, and every non-escape policy setting remain the
same as the corresponding v8 files.

Before a new Gazebo process:

- add pure transition/weight/default compatibility tests;
- add supervisor radial-direction, bounded-command, and zero-on-exit tests;
- add schema, live/offline Stage A, validator, launch, and dry-run tests;
- verify the controller still receives no evaluator geometry;
- run the same focused, scenario, analyzer, and broad no-Gazebo suites;
- perform a fresh isolated three-package build and installed graph
  instantiation;
- write a separate M3.1 no-Gazebo qualification record;
- update live status, checkpoint Phase 08, and commit the bounded correction.

Only then may `phase08_v8_1_primary_visible_probe.yaml` be launched once. A
failure closes that exact version and stops the corrected repeats. A pass
authorizes the v8.1 primary repeat gate, followed by the v8.1 secondary gate.
The original no-retry and first-failure rules remain in force.

### Executed M3.1 disposition and approved M3.2 correction amendment

The fixed v8.1 visible probe, seed `18901`, is closed as a retained behavioral
failure. It passed recording, final-zero, cleanup, one-fill cardinality, local
association, the required repulse stall, the new assisted departure, Stage A,
and physical approach to `0.155960 m` from the declared evaluator global. It
failed only because the controller rejected its second raw-cost candidate and
therefore correctly withheld `GOAL_REACHED`.

The retained raw bag resolves the discrepancy:

```text
strongest repeated local-basin raw cost:
  approximately -2.8462
strongest repeated global-basin raw cost:
  -3.837209302
raw ordering:
  global is strictly lower than local
controller's post-confirmation global estimate:
  -0.021174297
```

The current estimator resets its rotation window on
`SEARCH -> VERIFY_EXTREMUM`. The convergence confirmation arrived after the
strong directional global-basin samples had already occurred, so its later
six-second slice no longer represented the basin peak. This is an
estimator-timing defect; no change to motion, source count, cost sign, fill
behavior, or strict ranking is justified.

The user's bounded-correction authority permits a new v8.2 version:

1. Add `candidate_cost_pretrigger_rotations`, integer, default `0`.
2. A value of `0` preserves v8.1 and every historical behavior exactly.
3. When positive in counted-candidate mode, collect complete raw-cost
   rotation-bin minima during the current `SEARCH` epoch.
4. Retain only the latest configured number and freeze them when convergence
   enters `VERIFY_EXTREMUM`.
5. Continue collecting the normal complete verification rotations.
6. Select the configured `candidate_cost_required_rotations` most negative
   minima from the bounded frozen-plus-verification pool, then compute the
   existing median/MAD interval.
7. Reset both live and frozen history for every new search epoch; do not
   retain route, position, or cross-candidate motion history.
8. Report frozen pretrigger, verification, total available, and selected
   rotation counts through existing `AlgorithmEvent` value arrays.
9. Keep strict nonoverlap as the only terminal raw-cost comparison.

The v8.2 fixed profile uses:

```text
candidate_cost_pretrigger_rotations: 6
candidate_cost_required_rotations:   3
candidate_cost_rotation_period_sec:  3.0
candidate_cost_mad_scale:             3.0
verification_max_sec:                12.0
```

The six pretrigger bins bound sensor history to `18.0 s`. The three selected
minima require repeated evidence; one isolated sample cannot determine a
candidate. The three `9.0 s` post-confirmation bins still fit inside the
unchanged `12.0 s` verification budget. Raw cost remains authoritative.

The new fixed inputs are:

```text
phase08_v8_2_primary_visible_probe.yaml
  seed 19001
  visible
  runs root phase08_8_2_primary_probe

phase08_v8_2_primary_repeats.yaml
  seeds 19011 through 19020
  headless
  runs root phase08_8_2_primary_repeats

phase08_v8_2_secondary_visible_probe.yaml
  seed 19051
  visible
  runs root phase08_8_2_secondary_probe

phase08_v8_2_secondary_repeats.yaml
  seeds 19061 through 19065
  headless
  runs root phase08_8_2_secondary_repeats
```

Their source layouts, `400/1600` inputs, topology, start, assisted escape,
Stage A and Stage B budgets, evaluator-only `0.50 m` stop, required path, and
forbidden evidence match v8.1. Only the bounded raw-candidate estimator and
fresh version identities/seeds change.

Before another Gazebo process:

- retain and commit the complete v8.1 failure record;
- add pure raw-history selection, reset, backward-time, invalid-input, and
  default-off tests;
- add supervisor adapter tests proving raw rather than augmented cost enters
  both pretrigger and verification histories;
- add event-evidence, schema, launch, scenario, validator, and analyzer tests;
- run focused, scenario, analyzer, and broad no-Gazebo suites;
- perform a fresh isolated three-package build and installed graph
  instantiation;
- resolve all seventeen v8.2 cases without creating a run root;
- verify controller/evaluator separation and every historical hash;
- write a separate M3.2 no-Gazebo qualification record;
- update live status, checkpoint Phase 08, and commit.

Only then may `phase08_v8_2_primary_visible_probe.yaml` execute once. Failure
closes v8.2 and stops later dispatch. A formal pass authorizes its ten primary
repeats, then its secondary gate, under the unchanged no-retry rules.

### M4 — Ten consecutive primary repeats

Only after M3 passes:

1. execute the ten precommitted primary cases serially and headlessly;
2. use fresh processes and unique run IDs;
3. do not retry or change parameters between cases;
4. stop dispatch on the first behavioral or cleanup failure;
5. retain all dispatched attempts;
6. run the authoritative validator and analyzer on every complete recording.

Gate:

```text
formal pass:                 10/10
Stage A direct local escape: 10/10
exact one-fill cardinality:  10/10
ranked second candidate:     10/10
Stage B within 0.50 m:       10/10
FAILSAFE/TIMEOUT:             0/10
recording/final-zero:        10/10
cleanup/SQLite integrity:    10/10
```

Any miss closes this fixed profile as failed. Do not weaken the gate or select
only successful repeats.

### M5 — Secondary visible probe and five repeats

Only after M4 passes:

1. execute the secondary visible probe once;
2. if it passes formally, execute its five precommitted headless repeats;
3. use the same no-retry and first-failure stop rules;
4. validate and analyze every retained attempt.

Gate:

```text
visible formal pass:          1/1
repeat formal pass:           5/5
Stage A direct local escape:  6/6
exact one-fill cardinality:   6/6
ranked second candidate:      6/6
Stage B within 0.50 m:        6/6
FAILSAFE/TIMEOUT:             0/6
recording/final-zero:         6/6
cleanup/SQLite integrity:     6/6
```

### Executed M4 disposition and approved M4.1 / v8.3 correction amendment

The sealed v8.2 primary population is closed as a fixed gate failure. Seed
`19011`, the first of ten serial cases, completed recording, authoritative
validation, Stage A, exact one-fill cardinality, final-zero, analysis, and
cleanup, but failed Stage B. The runner stopped immediately; seed `19011` was
not retried and seeds `19012` through `19020` were not dispatched.

After the finite assisted exit, ordinary GESC returned to the filled local and
the detector confirmed it twice more. The supervisor correctly suppressed both
revisits. The retained fill was only `0.10` cost units high with
`sigma=0.169558 m`, while the candidate classifier's conservative repeated
raw-cost lower bound was `-2.442228`. No wall, collision, recenter, bounds, or
failsafe behavior caused the failure.

The complete fixed result is retained in
`phase_08_8_m4_primary_repeats.md`. The v8.2 secondary and broad gates are not
dispatched.

The approved execution amendment permits a separately versioned correction.
M4.1 / v8.3 fixes the detector-to-fill signal-summary mismatch without adding
affine guidance, dead-reckoned route memory, source coordinates, source roles,
evaluator geometry, Vicon, room geometry, or another controller:

1. Add `candidate_informed_fill_enabled`, boolean, default `False`, to the
   existing supervisor and Gaussian-fill owners.
2. When explicitly enabled in counted-candidate mode, the supervisor appends
   its frozen rotation-stable candidate raw-cost summary to a versioned robust
   create request. The request contains scientific signal evidence only; it
   contains no pose, source, role, or evaluator declaration beyond the
   convergence payload already used for fill creation.
3. The Gaussian-fill owner validates the request version, finite interval,
   repeated-rotation count, and consistency of
   `lower = estimate - uncertainty`. Malformed or nonnegative minimization
   evidence is rejected rather than silently weakened.
4. Add `candidate_informed_fill_amplitude_scale`, positive double, default
   `1.0`. When the feature is enabled, apply the conservative amplitude floor

   ```text
   amplitude floor =
       candidate_informed_fill_amplitude_scale
       * max(0, -candidate_raw_cost_lower)
   ```

   before the existing bounded design validation and escalation. The existing
   `amplitude_max` remains a hard cap. Report the candidate interval, scale,
   requested floor, applied floor, and cap status in the existing
   `AlgorithmEvent` value arrays.
5. Preserve the existing orientation-level basin estimator for center,
   covariance, anisotropy, association, validation, and immutable fill
   registry. The candidate evidence augments only the amplitude floor; it does
   not replace the adaptive fill or use augmented cost for ranking.
6. The v8.3 profile uses:

   ```text
   candidate_informed_fill_enabled:          True
   candidate_informed_fill_amplitude_scale:  1.25
   gaussian_fill_amplitude_max:              6.25
   gaussian_fill_sigma_floor_m:              0.50
   gaussian_fill_sigma_ceiling_m:            1.25
   gaussian_fill_exit_sigma:                 2.70
   ```

   `6.25` is the finite `1.25 * 5 V` ceiling for the selected negative-voltage
   cost convention. The `0.50 m` width floor prevents the last eight seconds
   of a tight local orbit from collapsing persistent basin memory to the
   failed `0.169558 m` footprint. With the observed covariance it preserves
   approximately the same `1.36 m` exit radius as v8.2 rather than enlarging
   the assisted travel requirement.
7. A strong accepted fill may complete `ESCAPE_REPULSE -> SEARCH` before the
   stall timer. The existing finite `ESCAPE_ASSIST` remains an allowed fallback
   if repulsion stalls. Both paths are valid local recovery; `ESCAPE_STALLED`
   is evidence only when the fallback actually runs and is no longer mandatory
   for v8.3.
8. The raw candidate history, strict final ranking, one-fill cardinality,
   evaluator-only `0.50 m` simulation stop, physical `Ctrl+C` contract,
   open-field mode, and all safety/completeness gates remain unchanged.

The new fixed inputs are:

```text
phase08_v8_3_primary_visible_probe.yaml
  seed 19101
  visible
  runs root phase08_8_3_primary_probe

phase08_v8_3_primary_repeats.yaml
  seeds 19111 through 19120
  headless
  runs root phase08_8_3_primary_repeats

phase08_v8_3_secondary_visible_probe.yaml
  seed 19151
  visible
  runs root phase08_8_3_secondary_probe

phase08_v8_3_secondary_repeats.yaml
  seeds 19161 through 19165
  headless
  runs root phase08_8_3_secondary_repeats
```

Every source declaration, start, intensity, topology, evidence predicate,
Stage A/Stage B budget, and no-retry rule matches v8.2. Only the versioned
candidate-to-fill amplitude/width correction, optional direct escape path,
fresh identities, and fresh seeds change.

Before another Gazebo process:

- retain, checkpoint, and commit the complete v8.2 M4 failure;
- add pure request-codec, interval-validation, amplitude-floor, cap, default-off,
  and design-regression tests;
- add supervisor adapter tests proving only raw candidate evidence enters the
  versioned request;
- add Gaussian adapter/event tests proving the floor is applied and reported;
- add schema, launch, runner, validator, analyzer, and historical-default
  regressions;
- run focused, scenario, analyzer, and broad no-Gazebo suites;
- perform a fresh isolated three-package build and installed graph
  instantiation;
- resolve every v8.3 fixed case without creating a run root;
- write a separate M4.1 no-Gazebo qualification record;
- update live status, checkpoint Phase 08, and commit.

Only that committed boundary authorizes one execution of
`phase08_v8_3_primary_visible_probe.yaml`. A failure closes v8.3 and prevents
its repeats. A formal pass authorizes the fresh v8.3 ten-run primary gate, then
the fresh v8.3 secondary gate under the unchanged first-failure rules.

### M6 — Bounded broader-envelope characterization

Only after M5 passes, add and seal the approved broader
two-source matrix described in the execution amendment. The matrix must:

1. use an offline aggregate-field topology preflight that depends only on
   declared evaluator inputs and cannot enter the controller graph;
2. include multiple positions and positive intensity ratios beyond `1:4`;
3. declare every admitted case before dispatch;
4. run each admitted case once with no retry or outcome-based omission;
5. retain and report every dispatched result;
6. state the exact tested envelope rather than “any layout or intensity.”

The matrix is a development characterization after the frozen gates, not a
simulation-ready acceptance denominator. A dispatched failure remains a
failure and requires a separately versioned correction if work continues.

### M7 — Bounded closeout

1. Write the Phase 08.8 final report and handoff.
2. State separately:
   - primary repeatability result;
   - secondary repeatability result;
   - controller candidate-ranking result;
   - infrastructure/evidence result;
   - untested three-light status;
   - prohibited physical automatic stop;
   - absence of wall/obstacle claim.
3. Update and checkpoint status.
4. Run final static validation and inspect the complete diff.
5. Commit only with user authorization.

Even a complete pass establishes only:

> Repeatable local-fill escape and convergence to a rotation-ranked stronger
> second source in two fixed open-field, zero-disturbance, two-light layouts at
> the simulator-relative `1:4` input ratio.

It does not establish broad simulation readiness.

## Milestones and checkpoints

| Milestone | Runtime boundary | Required checkpoint | Stop later work when |
|---|---|---|---|
| M1 | no Gazebo | after counted policy/tests | compatibility, count, ranking, or three-source unit logic fails |
| M2 | no Gazebo | after build/dry-run qualification | launch instantiation, schema, default regression, or cleanup preflight fails |
| M3 | one visible run | before and after the probe | any probe gate fails |
| M4 | at most ten headless runs | after retained primary report | any dispatched case fails behavior or cleanup |
| M5 | one visible + at most five headless | after retained secondary report | visible or any dispatched repeat fails |
| M6 | sealed broader matrix | after broad-envelope report | topology preflight leaks into control, dispatch set drifts, or evidence is incomplete |
| M7 | no new Gazebo | final closeout checkpoint | evidence cannot support the narrow stated claim |

Every ROS, Gazebo, build, test, and batch command must be bounded. Large logs
and run artifacts stay outside Git; exact paths and concise outcomes go in live
status and validation reports.

## Tests and acceptance criteria

### Focused pure and adapter tests

From `ros2_ws` with source checkout precedence and isolated logs:

```bash
timeout 300s python3 -m pytest -q \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_convergence_detector_policy.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_legacy_behavior.py
```

Required new cases:

- `known_source_count=2`, first candidate always enters fill design;
- absolute score cannot classify the first counted candidate as global;
- one accepted fill is required before the second candidate can reach
  `GOAL_HOLD`;
- second candidate with a strictly lower raw-cost interval is accepted;
- ambiguous/higher second candidate resumes search and is not called global;
- revisit associated with the active fill is not counted as source two;
- extra fill is impossible after the `N - 1` budget;
- `known_source_count=3` requires two distinct fill/escape episodes before a
  terminal candidate;
- invalid `N`, fill budget, nonfinite raw cost, or incomplete rotations fail
  safely;
- qualified dwell confirms once with hysteresis;
- epoch reset and invalid evidence clear partial dwell;
- default crossing-count behavior remains unchanged;
- bounds-enabled defaults retain historical geometry behavior;
- bounds-disabled mode does not suppress stale-input or explicit-stop safety.

### Scenario/evidence tests

```bash
timeout 300s python3 -m pytest -q \
  src/ros_esc/test/test_scenario_schema.py \
  src/ros_esc/test/test_scenario_runner.py \
  src/ros_esc/test/test_phase08_validation.py
```

Required new cases:

- scenario topology passes only the total source count to launch;
- source coordinates remain evaluator-only;
- open-field scenarios resolve without validation walls or contacts;
- direct no-recenter Stage A validates;
- proximity alone cannot pass without ranked `GOAL_REACHED`;
- ranked goal alone cannot pass without post-Stage-A evaluator proximity;
- wall/collision is `not_applicable`, not fabricated as a pass;
- physical-mode resolution cannot inherit the simulation proximity stop;
- historical schema fixtures resolve identically.

### Broad regression and build

Use the final focused totals recorded in live status rather than guessing them
in advance:

```bash
timeout 600s python3 -m pytest -q \
  src/ros_esc/test \
  --ignore=src/ros_esc/test/test_flake8.py \
  --ignore=src/ros_esc/test/test_pep257.py \
  --ignore=src/ros_esc/test/test_copyright.py

timeout 900s colcon --log-base /tmp/phase08_8_colcon \
  build --packages-select \
  ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
```

Then instantiate the installed launch graph with bounded runtime and perform
scenario dry-runs. `--show-args` alone is insufficient to validate ROS
parameter types.

### Non-runtime qualification

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/\
validate_phase_context.sh 08 implement
git diff --check
```

Also verify:

- no active Gazebo/ROS process before each dispatch;
- no historical scenario hash changed;
- no physical launch includes a coordinate-based global stop;
- no new `/cmd_vel` publisher exists;
- canonical topic counts and types remain unchanged;
- raw candidate history and augmented controller history are not silently
  swapped;
- new scenario dry-runs create no run root.

## Risks and stop conditions

### Level A — stop before continuing

- the controller receives a source coordinate, source role, Vicon pose, room
  map, or evaluator proximity;
- counted-source behavior requires a new pose estimator or planner;
- physical and simulation algorithm semantics would diverge;
- cost sign/units or canonical topics would change;
- another node would publish `/cmd_vel`;
- the new policy cannot coexist with historical defaults;
- a physical process or command would be required;
- user changes overlap and cannot be preserved.

### Fixed-experiment failure — retain and stop

- the visible probe fails;
- a repeat fails Stage A, fill cardinality, candidate ranking, Stage B,
  final-zero, recording, or cleanup;
- a candidate is accepted from an absolute score rather than the counted
  policy;
- the global evaluator coordinate influences controller motion;
- a failed attempt would need a parameter change or retry to pass.

Preserve the evidence and write a bounded failure diagnosis. A correction
requires a newly reviewed amendment/version; it must not mutate the failed
fixed experiment.

### Known limitations to report, not “fix” in this iteration

- global-first encounter is unsupported;
- unknown source count is unsupported;
- three-light behavior is unit-tested but not demonstrated in Gazebo;
- no obstacle or wall avoidance is claimed;
- the simulator-relative `400/1600` ratio is not physical photometric
  calibration;
- the physical photoresistor can saturate outside its informative range;
- zero-noise and zero-delay repeats do not establish disturbance robustness;
- Gazebo is not bitwise deterministic;
- no finite search proves an unseen stronger source is absent outside the
  tested field.

## Implementation-time verification

Before editing, the Implement chat must:

1. reread `AGENTS.md`, this Plan, `phase_08_status.md`, the final Phase 08
   report/handoff, and the Phase 08 checkpoint;
2. run `validate_phase_context.sh 08 implement`;
3. verify branch, HEAD, working tree, diff, and recent commits;
4. verify the exact current state-machine transitions and event producers;
5. verify `/pde_cost_history` receives raw rather than augmented cost in the
   selected graph;
6. verify the existing `GaussianFill` registry exposes enough association data
   to suppress revisits without adding a route map;
7. verify `gazebo_empty.world` has no wall models relevant to the robot;
8. verify the runner can resolve `validation_world=false` and
   `simulation_contacts_enabled=false` without inventing collision success;
9. verify the physical launch/runner cannot receive the simulation proximity
   stop;
10. verify no current uncommitted user work overlaps the listed files.

If any of these assumptions is false, record the exact evidence and apply the
Level A/B/C policy before proceeding.

## Executed M4.2 disposition and M4.3 v8.4 correction amendment

### Fixed v8.3 primary-repeat disposition

The committed v8.3 primary population is closed. Exactly seeds
`19111..19115` executed once under the sealed first-failure rule. Seeds
`19111..19114` passed. Seed `19115` passed Stage A, candidate-informed fill
creation, exact one-fill cardinality, and assisted escape, but failed the
independent `180.0 s` Stage B gate. Seeds `19116..19120` were not dispatched.

The immutable report is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_2_primary_repeats.md
```

The retained cross-seed evidence rejects fill strength and timeout as the
primary defect. The failed seed used the same approximately `3.557` fill
amplitude as three passing seeds. Its assisted exit was aligned `-1.000`
against the evaluator-only fill-to-global direction, while the four passes
were aligned `+0.906`, `+0.751`, `+0.559`, and `+0.159`. It escaped through
the start-side hemisphere and searched southwest without revisiting the filled
local.

Both v8.3 escape states suppress the raw sensor term. Gaussian repulsion is
radially symmetric, and the open-field supervisor freezes whichever radial
side the stochastic controller occupies when the stall sample arrives. The
stronger unseen source therefore cannot break the outward-direction symmetry
during that decision.

Re-enabling raw cost alone is not adopted. Offline evaluation of the retained
fill/stall geometries shows that immediate raw-plus-Gaussian descent is not
uniformly aligned with the remaining stronger basin because the unfilled raw
local attraction can still dominate near the fill center. Weakening the fill
would reintroduce that basin; extending Stage B would permit more travel in an
already wrong direction.

The correction below is a fresh version. It does not mutate, retry, relabel,
or reopen v8.3.

### M4.3 objective

Version v8.4 adds one bounded approach-continuity vector to the existing
open-field escape. The vector uses only the odometry history already retained
by the supervisor and the accepted fill geometry already available to the
controller. It is not a global pose, route map, waypoint, source declaration,
or evaluator input.

The intended behavior is:

```text
ordinary raw-plus-Gaussian SEARCH reaches candidate one
-> freeze one pre-basin approach-continuity vector
-> use Gaussian plus bounded affine bias to leave through the forward
   fill-safe hemisphere
-> clear affine authority at the measured escape boundary
-> resume ordinary raw-plus-Gaussian SEARCH
-> rank candidate two from raw rotational evidence
```

This is deliberately narrower than a persistent dead-reckoning or traveled
route system:

- it summarizes existing pose history into one unit vector;
- it is created only after a typed fill is accepted;
- it is scoped to that one escape episode;
- it is cleared on `SEARCH`, terminal state, reset, or fault;
- it cannot select a waypoint or retain a route after escape;
- it receives no source position, source role, global coordinate, room
  dimension, Vicon pose, simulator truth, or proximity result.

### Default-off controller contract

Add:

```text
open_field_escape_approach_continuity_enabled: false
```

The new control is valid only when all of these are true:

```text
algorithm profile:                  robust_gaussian_v1
extremum classification:            counted_candidates
candidate-informed fill:            enabled
open-field escape assist:           enabled
affine implementation:              enabled
operating bounds:                   disabled
recenter:                           disabled
recoverable navigation:             disabled
post-recovery guidance:              disabled
```

Historical defaults, v8-v8.3 inputs, V6, and every prior scenario retain their
existing weights, event payloads, selector behavior, launch arguments, and
resolved bytes.

When the new control is enabled:

1. At the accepted fill transition, search the existing time-ordered
   supervisor pose history from newest to oldest for the newest finite pose
   strictly outside the frozen escape exit radius.
2. Define the approach-continuity direction as the normalized vector from
   that historical anchor to the frozen fill center. The history must contain
   at least one qualified anchor and a nonzero finite displacement. Absence of
   qualified evidence is an explicit run failure in v8.4; it may not silently
   fall back to the failed radial-only policy.
3. Store only the anchor, displacement, exit radius, age, and unit direction
   for the active escape. Do not copy the trajectory into a new map or retain
   it after escape.
4. Select the existing hard fill-safe direction candidate with greatest
   alignment to the frozen approach direction. A direct forward candidate is
   preferred; when the robot is on the wrong side of the fill, a tangent in
   the forward half-plane may be selected until a direct candidate becomes
   safe.
5. Freeze and revalidate the selected direction using the existing fill
   avoidance geometry and revision contract. Any re-selection remains in the
   same forward half-plane. No operating-bound or wall candidate enters this
   open-field profile.
6. Publish `(raw, Gaussian, affine) = (0, 1, 1)` in both
   `ESCAPE_REPULSE` and `ESCAPE_ASSIST`. The existing robust modified-cost
   owner binds its affine term to the typed safe direction and revision.
7. Use the fixed affine values:

   ```text
   gain:            0.50
   direction sign:  1.0
   decay rate:      0.0000005 s^-1
   maximum age:     35.0 s
   ```

   The state transition clears affine weight and the robust affine term at
   the first measured escape completion or any terminal/reset path. There is
   no post-recovery affine guidance.
8. Keep supervisor translation zero during `ESCAPE_REPULSE`. If measured
   radial progress still stalls, the existing finite `ESCAPE_ASSIST`
   translation uses the same approach-continuity direction and existing
   differential-drive limits.
9. Preserve the frozen exit-radius/hold criterion and shared `35.0 s` escape
   deadline. A direct `ESCAPE_REPULSE -> SEARCH` path and an assisted
   `ESCAPE_REPULSE -> ESCAPE_ASSIST -> SEARCH` path are both valid.
10. Append the qualified history anchor, displacement, age, exit radius,
    frozen continuity vector, selected direction, selected rotation, and
    direction revision to existing typed event/state evidence only when the
    new feature is enabled.

Raw sensor cost remains authoritative for candidate summaries and resumes with
Gaussian memory in ordinary `SEARCH`. It is intentionally not mixed into the
bounded escape state, where the affine term has the single role of breaking
the Gaussian radial symmetry.

### Retained-geometry prequalification

The five v8.3 primary runs provide a fixed offline replay set. At their
fill-acceptance poses, the proposed selector uses the newest recorded odometry
pose outside the frozen `1.366771 m` exit radius. The following global
alignments are evaluator-only diagnostics; the global coordinate cannot enter
the implementation or runtime graph.

| Seed | History anchor `(x,y)` | Frozen approach direction | Initial selected direction | Selected/global alignment |
|---:|---:|---:|---:|---:|
| 19111 | `(0.197, 0.017)` | `(0.518, 0.855)` | `(0.971, 0.238)` | `+0.883` |
| 19112 | `(0.349, 0.062)` | `(0.706, 0.708)` | `(0.706, 0.708)` | `+0.998` |
| 19113 | `(0.297, 0.035)` | `(0.729, 0.684)` | `(0.729, 0.684)` | `+0.995` |
| 19114 | `(0.250, 0.025)` | `(0.706, 0.708)` | `(0.706, 0.708)` | `+0.999` |
| 19115 | `(0.317, 0.039)` | `(0.428, 0.904)` | `(0.942, 0.336)` | `+0.934` |

The preimplementation continuous-tangent diagnostic at seed `19115`'s later
stall pose produced `(-0.207, 0.978)`, aligned `+0.472` with the
evaluator-only global direction. M4.3 qualification corrected that value
before dispatch: it is not one of the executable selector's fixed
`45-degree` candidates. Exact replay at the first retained
`ESCAPE_ASSIST` state/odometry sample gives old radial direction
`(-0.960, -0.281)`, evaluator-only global alignment `-0.914`, and the actual
fill-safe forward candidate `(-0.336, 0.942)`, alignment `+0.351`. The
continuous-tangent value remains preliminary diagnostic evidence; the exact
discrete replay is the acceptance fixture.

### Fresh fixed inputs

Create four new scenario files. Every source declaration, start, intensity,
topology, candidate policy, fill value, detector value, Stage A/Stage B
budget, simulation-only stop, cleanup gate, and first-failure rule is copied
from v8.3. Only the default-off approach-continuity/affine correction, fresh
identities, fresh roots, and fresh seeds change.

```text
phase08_v8_4_primary_visible_probe.yaml
  seed 19201
  visible
  runs root phase08_8_4_primary_probe

phase08_v8_4_primary_repeats.yaml
  seeds 19211 through 19220
  headless
  runs root phase08_8_4_primary_repeats

phase08_v8_4_secondary_visible_probe.yaml
  seed 19251
  visible
  runs root phase08_8_4_secondary_probe

phase08_v8_4_secondary_repeats.yaml
  seeds 19261 through 19265
  headless
  runs root phase08_8_4_secondary_repeats
```

The new profile explicitly sets:

```text
open_field_escape_approach_continuity_enabled: true
modified_cost_enable_affine_bias:               true
modified_cost_affine_gain:                      0.50
modified_cost_affine_decay_rate:                0.0000005
modified_cost_affine_max_age:                   35.0
modified_cost_affine_direction_sign:            1.0
```

The scenario ablation `affine_assist_enabled` is `true`; recenter remains
`false`. Scenario validation permits affine in counted open-field mode only
for this explicit approach-continuity contract. A counted scenario with
affine enabled but without the new flag remains rejected exactly as before.

### No-Gazebo qualification

Before any v8.4 Gazebo process:

1. add pure history-selection tests for finite ordered history, newest
   outside-exit anchor, strict boundary behavior, zero displacement,
   nonfinite data, missing evidence, and deterministic direction;
2. replay all five retained v8.3 fill-acceptance geometries and the seed
   `19115` stall geometry exactly, proving the default-off radial result is
   unchanged and the enabled selector stays fill-safe and forward;
3. prove default state weights are unchanged and enabled
   `ESCAPE_REPULSE`/`ESCAPE_ASSIST` weights are exactly `(0, 1, 1)`;
4. prove one typed direction revision binds one affine term, no duplicate
   term is stacked, and `SEARCH`, reset, fault, stale pose, missing fill, or
   missing history clears authority;
5. prove the supervisor command remains zero in `ESCAPE_REPULSE`, remains
   bounded in `ESCAPE_ASSIST`, and the controller remains the sole
   `/cmd_vel` publisher;
6. prove event/state evidence contains the frozen anchor/vector only when the
   feature is enabled and leaks no source/global/evaluator fields;
7. prove scenario validation requires candidate-informed fill, open-field
   assist, affine enablement, bounds off, recenter off, recoverable navigation
   off, and post-recovery guidance off;
8. prove every v8-v8.3 and historical normalized scenario remains byte- and
   behavior-compatible, including the counted-mode affine rejection when the
   new flag is absent;
9. run focused state-machine, escape geometry, supervisor integration,
   modified-cost, launch, schema, runner, validator, analyzer, observability,
   and legacy tests;
10. run the broad ROS-independent suite, fatal lint, Python compilation,
    isolated three-package build, installed launch instantiation, source/install
    parity, all four dry-runs without creating a run root, context validation,
    `git diff --check`, and inactive-process checks;
11. write a separate v8.4 no-Gazebo qualification record, update live status,
    checkpoint Phase 08, and commit the exact qualified implementation.

No parameter sweep or Gazebo tuning is authorized. A no-Gazebo failure must be
corrected and requalified before runtime.

### V8.4 runtime gates

Only a clean committed qualification and separate committed dispatch boundary
authorize one installed visible execution of
`phase08_v8_4_primary_visible_probe.yaml`, seed `19201`.

- A visible failure closes v8.4 immediately.
- A visible pass must be analyzed, plotted, checkpointed, and committed before
  the primary repeats.
- The ten primary repeats run serially and headlessly, stop at the first
  behavioral or cleanup failure, and never retry a seed.
- Only a complete `10/10` primary population authorizes the secondary visible
  probe.
- Only a passing secondary visible probe authorizes the five secondary
  repeats.
- Only a complete `5/5` secondary population authorizes any broader-envelope
  characterization.

Every run continues to require:

```text
one distinct local candidate
-> exactly one typed active fill
-> completed local escape
-> ordinary SEARCH with affine cleared
-> distinct second candidate
-> strict raw-cost interval improvement
-> GOAL_REACHED
-> later evaluator-only 0.50 m simulation proximity
-> final zero, readiness false, complete recording, clean shutdown
```

The physical contract remains manual operator `Ctrl+C`. No coordinate-based
physical stop, wall behavior, obstacle behavior, Vicon input, or global pose
is introduced.

### Claim boundary

Even if all v8.4 gates pass, the result supports only the two fixed
route-blocking, local-first, two-source open-field layouts at the
simulator-relative `400/1600` ratio. Approach continuity is not proof that an
arbitrary first basin lies between the start and the stronger basin. Broader
positions or intensity ratios require the separately sealed M6 matrix, and
three lights remain untested in Gazebo.

## Executed M4.4 disposition and M4.5 v8.5 correction amendment

### Fixed v8.4 primary-repeat disposition

The committed v8.4 primary population is closed. Exactly seeds `19211` and
`19212` executed once under the sealed first-failure rule. Seed `19211`
passed. Seed `19212` passed Stage A, exact one-fill cardinality, and assisted
escape, but failed the independent `180.0 s` Stage B gate. Seeds
`19213..19220` were not dispatched.

The immutable report is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_4_primary_repeats.md
```

The frozen onboard-history direction was not the failure. For seed `19212`,
it was `(0.401588, 0.915820)`, with evaluator-only alignment `+0.911010`
against fill center to the declared global. The active-fill hard-avoidance
rule rejected that direct direction because the robot was approximately
`0.001814 m` from the estimated fill center and the direct vector's radial
projection was `-0.001317 m`.

The selector chose tangent `(0.915820, -0.401588)`. During Gaussian-only
repulsion the robot crossed to the other side of the estimated center.
Revalidation changed the direction through
`(-0.363617, 0.931549)` to `(-0.915820, 0.401588)`, the exact negative of the
initial tangent. The robot completed a valid radial escape westward and ended
`4.679383 m` from the global without a second candidate.

This is not corrected by more Stage B time, less fill amplitude, or a larger
affine gain. The supervisor changed the typed direction itself. The active
Gaussian fill is mathematical basin memory rather than a physical obstacle,
and the robot necessarily begins escape inside it.

The correction below is a fresh version. It does not mutate, retry, relabel,
or reopen v8.4.

### M4.5 objective

Version v8.5 adds one default-off active-fill corridor lock to the existing
approach-continuity escape:

```text
ordinary raw-plus-Gaussian SEARCH reaches candidate one
-> freeze the direct pre-basin approach-continuity vector
-> keep the active Gaussian in modified cost
-> do not treat that active mathematical fill as a solid obstacle
-> latch the direct vector through REPULSE and any measured-stall ASSIST
-> fail rather than reselect or reverse the vector
-> clear the vector at measured escape completion
-> resume ordinary raw-plus-Gaussian SEARCH
```

No source/global coordinate, Vicon pose, room geometry, wall model, waypoint,
route map, or persistent post-recovery direction enters this contract.

### Default-off controller contract

Add:

```text
open_field_escape_active_fill_transit_enabled: false
```

The new control is valid only when all v8.4 approach-continuity prerequisites
are true:

```text
algorithm profile:                            robust_gaussian_v1
extremum classification:                      counted_candidates
candidate-informed fill:                      enabled
open-field escape assist:                     enabled
open-field escape approach continuity:        enabled
affine implementation:                        enabled
operating bounds:                             disabled
recenter:                                     disabled
recoverable navigation:                       disabled
post-recovery guidance:                       disabled
```

Historical defaults, v8-v8.4 inputs, V6, and every prior scenario retain
their existing direction selection, revalidation, weights, event payloads,
launch arguments, and resolved bytes.

When the new control is enabled:

1. Derive `ApproachContinuityEvidence` exactly as v8.4 does: the newest
   existing supervisor-history pose strictly outside the frozen active-fill
   exit radius points toward the accepted fill center.
2. Latch that direct unit vector as the escape direction with revision one.
   Do not rotate it to a tangent merely because the current pose is inside or
   millimetrically offset from the active fill center.
3. Keep the active Gaussian fill in `/cost_modified`; only remove that active
   fill from collision-like direction eligibility for its own escape episode.
   This does not deactivate, delete, weaken, or supersede the fill.
4. Continue hard direction checks against every other retained active fill.
   If the latched corridor is unsafe with respect to another fill, stale pose,
   missing geometry, or nonfinite evidence, enter the existing explicit
   failure path. Do not select an alternate direction.
5. On every repulse/assist update, require the published safe direction to
   equal the frozen direct vector within the existing numerical tolerance.
   Direction revision must remain one. Any mismatch is an explicit failure;
   no re-selection or accumulated turn is allowed.
6. Continue publishing `(raw, Gaussian, affine) = (0, 1, 1)` in both
   `ESCAPE_REPULSE` and `ESCAPE_ASSIST`. The robust affine term binds to the
   same latched typed vector and revision.
7. Keep supervisor translation zero in `ESCAPE_REPULSE`. If measured radial
   progress stalls under the unchanged `3.0 s / 0.05 m` contract, the
   existing bounded `ESCAPE_ASSIST` translation follows the same direct
   vector.
8. Preserve the same measured radial exit radius, `1.0 s` hold, and `35.0 s`
   escape deadline.
9. Clear the corridor, safe direction, affine term, and weights at the first
   measured escape completion, terminal state, reset, stale/fault path, or
   explicit stop. Ordinary `SEARCH` remains `(1, 1, 0)` with no supervisor
   translation.
10. Append active-fill-transit enablement, excluded active fill identity,
    retained-other-fill count, latched vector, and revision to existing
    escape/configuration evidence only when v8.5 is enabled. No
    source/global/evaluator field may be added.

This is not obstacle avoidance. The operating region remains explicitly open
and obstacle-free. A Gaussian fill is not promoted to a physical collision
object.

### Retained-geometry prequalification

The five retained v8.3 primary geometries and three executed v8.4 primary
geometries provide eight immutable direct-corridor fixtures. Their direct
approach vectors have evaluator-only fill-to-global alignments from
approximately `+0.911` to `+1.000`. The global coordinate is used only to
describe the offline relationship and cannot enter implementation or runtime.

For the failed seed `19212` start geometry:

```text
robot-to-fill-center distance:
  0.001814 m
direct approach vector:
  (0.401588, 0.915820)
direct radial projection:
  -0.001317 m
initial Gaussian outward-gradient magnitude estimate:
  0.025183 cost units/m
fixed affine gradient magnitude:
  0.500000 cost units/m
```

The direct affine gradient is approximately `19.85` times the estimated
initial Gaussian outward gradient. This is a source-independent offline
sanity check, not a behavioral pass prediction.

The secondary fixed layout also satisfies the declared route-blocking
geometry: nominal start-to-local and local-to-global directions have dot
product approximately `+0.852`. That value is evaluator-only and not a
controller input.

### Fresh fixed inputs

Create four new scenario files. Every source declaration, start, intensity,
topology, candidate/fill/detector value, affine value, Stage A/Stage B budget,
simulation-only stop, cleanup gate, and first-failure rule is copied from
v8.4. Only the default-off active-fill transit correction, fresh identities,
fresh roots, and fresh seeds change.

```text
phase08_v8_5_primary_visible_probe.yaml
  seed 19301
  visible
  runs root phase08_8_5_primary_probe

phase08_v8_5_primary_repeats.yaml
  seeds 19311 through 19320
  headless
  runs root phase08_8_5_primary_repeats

phase08_v8_5_secondary_visible_probe.yaml
  seed 19351
  visible
  runs root phase08_8_5_secondary_probe

phase08_v8_5_secondary_repeats.yaml
  seeds 19361 through 19365
  headless
  runs root phase08_8_5_secondary_repeats
```

The new profile explicitly sets:

```text
open_field_escape_approach_continuity_enabled: true
open_field_escape_active_fill_transit_enabled: true
modified_cost_enable_affine_bias:               true
modified_cost_affine_gain:                      0.50
modified_cost_affine_decay_rate:                0.0000005
modified_cost_affine_max_age:                   35.0
modified_cost_affine_direction_sign:            1.0
```

### No-Gazebo qualification

Before any v8.5 Gazebo process:

1. replay all eight retained primary geometries, proving default-off v8.4
   outputs remain unchanged and enabled v8.5 latches the exact direct vector;
2. replay seed `19212` at fill acceptance, both revalidation samples, and
   escape completion, proving the direction never changes or reverses;
3. prove the active fill remains in modified cost and typed registry while it
   is excluded only from its own direction-eligibility set;
4. prove every other retained fill remains a hard eligibility constraint and
   an intersecting corridor fails explicitly without alternate selection;
5. prove direction revision remains one and robust modified cost maintains
   exactly one affine term for that revision;
6. prove REPULSE command remains zero, ASSIST remains bounded along the direct
   vector, and the controller remains the sole `/cmd_vel` publisher;
7. prove `SEARCH`, reset, terminal, explicit stop, stale pose, missing fill,
   and missing history clear all authority;
8. prove enabled-only event evidence contains the active-fill exclusion and
   latched vector but no source/global/evaluator field;
9. prove scenario validation requires the complete v8.4 contract and rejects
   active-fill transit without approach continuity;
10. prove every v8-v8.4 and historical normalized scenario remains byte- and
    behavior-compatible;
11. run focused state-machine, geometry, supervisor, modified-cost, launch,
    schema, runner, validator, analyzer, observability, and legacy tests;
12. run the broad ROS-independent suite, fatal lint, Python compilation,
    isolated three-package build, installed node construction, source/install
    parity, all four dry-runs without creating a run root, context validation,
    `git diff --check`, and inactive-process checks;
13. write a separate v8.5 no-Gazebo qualification record, update live status,
    checkpoint Phase 08, and commit the exact qualified implementation.

No parameter sweep or Gazebo tuning is authorized.

### V8.5 runtime gates

Only a clean committed qualification and separate committed dispatch boundary
authorize one installed visible execution of
`phase08_v8_5_primary_visible_probe.yaml`, seed `19301`.

- A visible failure closes v8.5 immediately.
- A visible pass must be analyzed, plotted, checkpointed, and committed before
  primary repeats.
- The ten primary repeats execute serially/headlessly, stop at the first
  behavioral or cleanup failure, and never retry a seed.
- Only `10/10` primary passes authorize the secondary visible probe.
- Only a passing secondary visible probe authorizes five secondary repeats.
- Only `5/5` secondary passes authorize any broader-envelope characterization.

Every run continues to require:

```text
one distinct local candidate
-> exactly one typed active fill
-> one latched direct escape direction with no revision
-> completed local escape
-> ordinary SEARCH with affine cleared
-> distinct second candidate
-> strict raw-cost interval improvement
-> GOAL_REACHED
-> later evaluator-only 0.50 m simulation proximity
-> final zero, readiness false, complete recording, clean shutdown
```

The physical contract remains manual operator `Ctrl+C`.

### V8.5 claim boundary

Even if all v8.5 gates pass, the result supports only the two fixed
route-blocking, local-first, two-source open-field layouts at the
simulator-relative `400/1600` ratio. Active-fill transit is not proof that an
arbitrary approach direction leads to an unseen stronger basin. Broader
positions or intensities require the separately sealed M6 matrix; three lights
remain untested in Gazebo.

## Executed M4.6 disposition and M4.7 v8.6 correction amendment

### Fixed v8.5 primary-repeat disposition

The committed v8.5 primary population is closed. Exactly seeds
`19311..19316` executed once under the sealed first-failure rule. Seeds
`19311..19315` passed. Seed `19316` passed Stage A, exact one-fill
cardinality, revision-one active-fill transit, and assisted local escape, but
failed the independent `180.0 s` Stage B gate. Seeds `19317..19320` were not
dispatched.

The immutable report is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_6_primary_repeats.md
```

The v8.5 selected direction was not revised or reversed. For seed `19316`, it
was `(0.485035, 0.874495)`, with evaluator-only alignment `+0.943` against
the fill-to-global direction. The physical escape occurred on the opposite
side of the fill: the measured exit direction had dot product `-0.925`
against the selected vector.

The reason is command arbitration. In `ESCAPE_ASSIST`, the robust controller
currently adds the oscillatory GESC command to the bounded supervisor
direction command and saturates the sum. In the failed run:

```text
valid synchronized assist samples:                 2,860
nonzero supervisor angular samples:                2,847
|GESC angular| > |supervisor angular| samples:     2,640
combined turn opposite supervisor samples:         1,605
mean |GESC angular request|:                         7.095 rad/s
mean |supervisor angular request|:                   0.398 rad/s
nonzero supervisor linear samples:                  0
```

The GESC angular request repeatedly kept heading outside the supervisor drive
cone. The nominal assist therefore supplied no linear translation; the robot
escaped under the competing GESC command on a seed-dependent side of the
fill.

The failed run was still approaching the global after recovery. It reduced
global distance by `1.979 m` in its final `60 s` with path efficiency
`0.912`. A longer Stage B evidence clock could admit this trajectory, but
would not correct the defeated direction owner or the observed actual-exit
alignment range of `+0.960` through `-0.925`.

The correction below is a fresh experiment version. It does not retry,
relabel, mutate, or reopen v8.5.

### M4.7 objective

Version v8.6 adds one default-off supervisor-owned assisted-escape command
mode:

```text
ordinary raw-plus-Gaussian SEARCH reaches candidate one
-> create exactly one typed active fill
-> freeze the direct onboard-history direction
-> let Gaussian-plus-affine GESC initiate zero-supervisor REPULSE
-> detect measured radial stall
-> in ASSIST, keep computing and recording GESC cost/control diagnostics
-> give the bounded supervisor command exclusive actuator authority
-> rotate toward the frozen world-frame direction
-> translate along that direction until measured exit plus hold
-> clear direction, affine, and supervisor authority
-> resume ordinary raw-plus-Gaussian SEARCH
```

This is a command-ownership correction, not GPS guidance, global navigation,
wall avoidance, source-coordinate guidance, or a persistent post-recovery
route.

### Default-off command-owner contract

Add:

```text
open_field_escape_supervisor_owned_assist_enabled: false
```

The new control is valid only when all v8.5 active-fill-transit prerequisites
are true:

```text
algorithm profile:                            robust_gaussian_v1
extremum classification:                      counted_candidates
candidate-informed fill:                      enabled
open-field escape assist:                     enabled
open-field escape approach continuity:        enabled
open-field escape active-fill transit:        enabled
affine implementation:                        enabled
operating bounds:                             disabled
recenter:                                     disabled
recoverable navigation:                       disabled
post-recovery guidance:                       disabled
```

Historical defaults, V6, every v8-v8.5 input, and all prior scenarios retain
their current command combination, weights, direction selection, launch
arguments, event payloads, normalized bytes, and resolved behavior.

When the new control is enabled:

1. `ESCAPE_REPULSE` remains unchanged. The supervisor command remains zero;
   GESC computes from weights `(raw, Gaussian, affine) = (0, 1, 1)` and
   remains the actuator command owner.
2. The existing measured `3.0 s / 0.05 m` stall rule alone enters
   `ESCAPE_ASSIST`.
3. In `ESCAPE_ASSIST`, modified cost and the GESC controller continue to
   compute with weights `(0, 1, 1)` for observability and algorithm-state
   continuity, but the controller's authorized unsaturated actuator command
   is exactly the fresh supervisor command. The GESC command is not added to
   it.
4. The controller remains the sole `/cmd_vel` publisher. Supervisor
   ownership means command arbitration inside that existing controller, not
   a second publisher or bypass node.
5. The supervisor uses the already latched revision-one world-frame
   direction and existing odometry yaw. It rotates in place while heading is
   outside the existing drive cone, then applies the existing bounded linear
   command along the same direction.
6. The active fill stays in typed memory and modified cost. It remains
   excluded only from its own open-field command-sweep check. Every other
   retained fill remains a hard command-sweep constraint.
7. A missing, stale, nonfinite, mismatched, or unsafe supervisor command
   follows the existing zero/failsafe path. The controller must never fall
   back to the competing GESC command while enabled assist ownership is
   active.
8. `ControlDiagnostics` remains arithmetically honest:
   `combined_command_unsaturated` is the authorized supervisor command,
   `gesc_command_unsaturated` is the suppressed GESC proposal, and
   `supervisor_contribution` is the complete correction
   `combined - GESC`.
9. At the first measured exit completion, explicit stop, terminal state,
   reset, stale/fault path, or missing fill/history path, supervisor-owned
   authority, safe direction, affine term, and weights clear under the
   existing rules.
10. The first returned `SEARCH` sample must again be `(1, 1, 0)`, have no
    valid safe direction, have zero supervisor command, and authorize the
    ordinary GESC command exactly as v8.5 does.
11. Append enabled-only configuration evidence for supervisor-owned assist.
    Do not add a source/global/evaluator coordinate or any hidden target.

The supervisor may use wheel-odometry/IMU pose and yaw already permitted by
the project. Vicon, GPS, declared light positions, room dimensions, and the
evaluator-only global coordinate remain unavailable to controller runtime.

### Formal command-ownership evidence

Schema v10 adds the optional result predicate:

```text
supervisor_owned_escape_assist
```

When required, the authoritative validator must use recorded
`/gesc_gaussian/supervisor_command`, `ControlDiagnostics`,
`AlgorithmState`, odometry, and escape events to prove:

1. at least one valid `ESCAPE_ASSIST` interval exists;
2. every evaluated assist control sample has a fresh supervisor command;
3. pre-saturation combined command equals the held fresh supervisor command
   on all six axes within numerical tolerance;
4. the recorded GESC proposal is independently finite and at least one
   sample proves it was nonzero but did not leak into the combined command;
5. supervisor contribution equals `combined - GESC`;
6. the final command equals the existing saturation of the combined command;
7. direction validity and revision one persist throughout assist;
8. at least one positive supervisor linear command occurs before exit;
9. the measured fill-to-exit unit vector has dot product at least `+0.80`
   against the latched selected direction;
10. the first post-exit `SEARCH` control sample returns to ordinary GESC
    ownership with affine and supervisor authority cleared.

Unmatched, stale, missing, nonfinite, zero-linear-only, GESC-leaking,
wrong-direction, wrong-revision, or post-exit-persistent evidence fails the
predicate. There is no evaluator/global-coordinate term in this predicate.

### Relaxed simulation-only Stage B evidence budget

Fresh v8.6 staged scenarios use:

```text
stage_a_timeout_sec:       360.0
post_stage_a_timeout_sec:  300.0
run_timeout_sec:           720.0
wall_timeout_sec:          900.0
```

This does not change controller behavior, convergence detection, candidate
ranking, physical stopping, or escape timing. It prevents the simulation
evidence harness from terminating a healthy open-field search solely because
a longer approach is needed after a valid local recovery. The physical
contract remains manual operator `Ctrl+C`; there is no physical
coordinate-distance stop or Stage B timer.

The command-owner predicate remains mandatory. A run cannot pass merely by
using the extra time.

### Fresh fixed inputs

Create four schema-v10 scenario files. Source declarations, starts,
intensities, topology, candidate/fill/detector values, affine values, Stage A
budget, simulation-only proximity stop, cleanup gates, and first-failure rules
are copied from v8.5. Only the supervisor-owned assist correction, Stage B
evidence budget, fresh identities/roots, and declared seeds change.

```text
phase08_v8_6_primary_visible_probe.yaml
  seed 19316
  visible
  runs root phase08_8_6_primary_probe

phase08_v8_6_primary_repeats.yaml
  seeds 19411 through 19420
  headless
  runs root phase08_8_6_primary_repeats

phase08_v8_6_secondary_visible_probe.yaml
  seed 19451
  visible
  runs root phase08_8_6_secondary_probe

phase08_v8_6_secondary_repeats.yaml
  seeds 19461 through 19465
  headless
  runs root phase08_8_6_secondary_repeats
```

Seed `19316` is intentionally reused only in the fresh v8.6 visible
correction probe so the committed v8.5 command-arbitration failure is a
deterministic regression fixture. The scenario identity, schema, controller
behavior, evidence root, and experiment version are new. This does not retry
or alter the v8.5 result.

The new profile explicitly sets:

```text
open_field_escape_approach_continuity_enabled:        true
open_field_escape_active_fill_transit_enabled:        true
open_field_escape_supervisor_owned_assist_enabled:    true
modified_cost_enable_affine_bias:                     true
modified_cost_affine_gain:                            0.50
modified_cost_affine_decay_rate:                      0.0000005
modified_cost_affine_max_age:                         35.0
modified_cost_affine_direction_sign:                  1.0
```

No parameter sweep is authorized.

### No-Gazebo qualification

Before any v8.6 Gazebo process:

1. freeze all historical and v8-v8.5 scenario bytes and prove the new switch
   defaults false everywhere;
2. replay the recorded seed-`19316` assist control fixtures with the switch
   disabled, proving the existing v8.5 combined commands are unchanged;
3. replay the same fixtures with the switch enabled, proving every assist
   combined command equals the supervisor command and never the competing
   GESC-plus-supervisor sum;
4. prove REPULSE, SEARCH, VERIFY, DESIGN, terminal, reset, explicit-stop,
   stale/fault, and legacy RECENTER arbitration remain unchanged;
5. prove enabled ASSIST never falls back to GESC on a zero, stale, missing,
   nonfinite, or unsafe supervisor command;
6. prove existing command saturation, watchdog, final-zero, readiness, and
   sole-`/cmd_vel`-publisher contracts remain intact;
7. prove supervisor yaw gating produces rotate-only then positive bounded
   linear motion toward the exact latched vector;
8. prove all other retained fills remain hard command-sweep constraints;
9. prove enabled-only configuration evidence contains command-owner
   enablement but no source/global/evaluator field;
10. prove schema-v10 dependency checks and the new formal predicate reject
    missing, stale, leaked-GESC, zero-linear-only, wrong-revision,
    wrong-exit-direction, and persistent-post-exit evidence;
11. prove v8.6/v8.5 source pairs differ only in declared versioned fields,
    the new switch, evidence budget, identities, roots, and seeds;
12. run focused state-machine, supervisor, controller, modified-cost,
    geometry, launch, schema, runner, validator, analyzer, observability, and
    legacy tests;
13. run the broad ROS-independent suite, fatal lint, Python compilation,
    launch XML and YAML parsing, isolated three-package build, installed node
    construction, source/install parity, all four installed dry-runs without
    creating a run root, context validation, `git diff --check`, and inactive
    process checks;
14. write a separate v8.6 no-Gazebo qualification record, update live status,
    checkpoint Phase 08, and commit the exact qualified implementation.

No Gazebo process is authorized until the complete qualification,
checkpoint, and implementation commit pass.

### V8.6 runtime gates

Only a clean committed qualification and separate committed dispatch boundary
authorize one installed visible execution of
`phase08_v8_6_primary_visible_probe.yaml`, seed `19316`.

- A visible failure closes v8.6 immediately.
- A visible pass must include the formal command-owner predicate, complete
  analysis, all nine plots, a measured exit-alignment value, checkpoint, and
  commit before primary repeats.
- The ten fresh primary repeats execute serially/headlessly, stop at the
  first behavioral, command-owner, recording, final-zero, or cleanup failure,
  and never retry a seed.
- Only `10/10` primary passes authorize the secondary visible probe.
- Only a passing secondary visible probe authorizes five secondary repeats.
- Only `5/5` secondary passes authorize any M6 broader-envelope
  characterization.

Every run continues to require:

```text
one distinct local candidate
-> exactly one typed active fill
-> one latched direct escape direction with no revision
-> supervisor-owned measured assisted exit aligned with that direction
-> ordinary SEARCH with affine and supervisor authority cleared
-> distinct second candidate
-> strict raw-cost interval improvement
-> GOAL_REACHED
-> later evaluator-only 0.50 m simulation proximity
-> final zero, readiness false, complete recording, clean shutdown
```

### V8.6 claim boundary

Even if every v8.6 gate passes, the result supports only reproducible
behavior in the two fixed route-blocking, local-first, two-source open-field
layouts at the simulator-relative `400/1600` ratio. Supervisor-owned assist
proves deterministic execution of an onboard-history escape direction; it
does not prove that this direction reveals an arbitrary unseen stronger
source.

Broader light positions or intensity ratios require the separately sealed M6
matrix and may require deliberate exploration with persistent basin/route
memory. Three lights remain untested in Gazebo. Wall/obstacle avoidance is
out of scope, and physical stopping remains manual operator `Ctrl+C`.

### Executed M4.7 visible disposition and analysis-bundle clarification

The one committed v8.6 primary visible probe, seed `19316`, passed every
formal scenario predicate, including the schema-v10 command-owner predicate.
It produced all expected analysis tables and all nine required plots from one
successful `analyze_run` invocation with `analysis_failures=[]`.

The analyzer summary status is `partial` only because its optional generic
state-duration metric conservatively invalidated itself for three isolated
pre-Stage-A `SEARCH` sampling gaps of `0.220447 s`, `0.162486 s`, and
`0.338401 s`. Critical inputs, fresh Phase 05 validation, the typed state
path, Stage A episode, all `1,876` evaluated assist control samples,
post-exit handoff, terminal state, final zero, and every formal predicate are
complete and valid.

For the v8.6 runtime gates, the already-written phrase “complete analysis”
means a successful one-time analyzer execution with the complete expected
artifact bundle, all nine plots, and no `analysis_failures`. It does not make
every optional generic metric an unstated acceptance predicate. Any missing
critical input, analyzer failure, missing plot, incomplete formal evidence,
or recording failure remains a fixed-experiment failure.

This is an evidence interpretation clarification, not a parameter, code,
scenario, timeout, acceptance-predicate, or result change. The run was not
retried or reanalyzed.

## Executed M4.7 repeat disposition and M4.8 v8.7 correction amendment

### Fixed v8.6 primary-repeat disposition

The sealed v8.6 primary population is closed as a fixed formal gate failure.
Seed `19411`, the first of ten serial cases, executed once. It was not
retried, and seeds `19412..19420` were not dispatched.

Seed `19411` completed the scientific behavior:

```text
one local candidate
-> exactly one typed fill
-> revision-one supervisor-owned aligned assisted exit
-> ordinary raw-plus-Gaussian SEARCH
-> strictly lower second raw-cost interval
-> GOAL_REACHED
-> evaluator sample 0.123633 m from the declared global
```

Recording, Stage A, fill cardinality, candidate ranking, Stage B, terminal
state, final readiness false, final commands zero, and run-session process
cleanup all passed. The formal result failed two mandatory predicates:

1. the schema-v10 command-owner predicate interpreted one `6.363998 ms`
   cross-topic handoff tail as failed post-exit ownership; and
2. an external `ros2 topic echo --once` progress inspection joined the active
   ROS domain and left `/_ros2cli_282407` in discovery during the cleanup
   audit.

The first ordinary post-exit control diagnostic occurred `7.696498 ms` after
the recorded `SEARCH` state boundary. Every one of the next `13,069`
diagnostics through the following state transition had combined command equal
to GESC and zero supervisor contribution. The one tail diagnostic exactly
matched the last finite revision-one assist command; it was not a GESC leak,
invalid command, reversal, or continuing supervisor authority.

The complete immutable result is retained in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_7_primary_repeats.md
```

The external monitoring contamination is an operator/workflow defect, not a
reason to weaken cleanup. The schema-v10 timestamp rule is an evidence
causality defect: publication order across separate ROS topics is not proof
of the order in which the controller consumed those messages.

### M4.8 objective

Version v8.7 changes no controller, supervisor, detector, fill, modified-cost,
launch, world, source, motion, ranking, timeout, final-zero, or cleanup
behavior. It adds a schema-v11 causal post-exit handoff contract and a sealed
execution protocol that forbids external ROS graph participants.

This is a fresh formal-evidence version. It does not retry, relabel, mutate,
or reopen v8.6.

### Schema-v11 causal handoff contract

The existing predicate name remains:

```text
supervisor_owned_escape_assist
```

Schema versions through v10 retain their existing first-recorded-sample
semantics byte-for-behavior. Schema v11 adds the evaluator-only controller
evidence field:

```text
supervisor_owned_assist_handoff_timeout_sec: 0.15
```

This field is never passed to the launch graph or controller. It bounds
cross-topic delivery settling in the offline formal validator.

For schema v11, the assist-interval ownership, fresh supervisor match,
suppressed nonzero GESC proposal, contribution arithmetic, saturation,
revision-one direction, positive translation, measured exit, and alignment
requirements remain unchanged. Post-exit evidence must additionally prove:

1. the first and every recorded `SEARCH` state sample before the next state
   have weights `(1,1,0)`, no safe-direction validity, and no escape
   geometry/authority;
2. a zero supervisor command is recorded after the `SEARCH` boundary, and
   every later supervisor command within that `SEARCH` interval is zero;
3. any diagnostic between the recorded `SEARCH` boundary and causal ordinary
   ownership is finite, arithmetically consistent, correctly saturated, and
   equals either:
   - ordinary GESC with zero contribution,
   - a zero/failsafe command, or
   - the final fresh supervisor command proven valid during the immediately
     preceding assist interval;
4. a diagnostic with combined command equal to GESC and zero supervisor
   contribution occurs within `0.15 s` of the `SEARCH` boundary;
5. every later diagnostic through the next state transition remains ordinary
   GESC ownership with valid saturation; and
6. the result records the transition-sample count, handoff delay, first
   ordinary diagnostic stamp, and steady ordinary sample count.

An unrecognized transient command, GESC-plus-supervisor leak, stale or
nonfinite command, invalid contribution arithmetic, invalid saturation,
nonzero post-boundary supervisor publication, handoff later than `0.15 s`,
or any later reappearance of supervisor contribution fails.

This contract does not excuse persistent authority. It replaces a bag
publication-order assumption with a bounded causal proof and is stronger
after the handoff because it validates the complete returned `SEARCH`
interval, not only one selected diagnostic.

### Sealed-run observation protocol

Once a v8.7 Gazebo dispatch starts:

- no `ros2 topic`, `ros2 node`, `ros2 service`, `ros2 param`, RViz, plotter,
  or other DDS participant may join that run's ROS domain;
- progress may be observed only from process state, console files, run
  directories, bag-file growth, and scenario summaries;
- the runner's graph audit continues to fail on every new node and every
  surviving run-session process;
- no node-name allowlist or cleanup exception is added;
- an operator-caused graph contaminant remains a fixed-run failure.

### Fresh fixed inputs

Create four schema-v11 scenarios:

```text
phase08_v8_7_primary_visible_probe.yaml
  seed 19501
  visible
  runs root phase08_8_7_primary_probe

phase08_v8_7_primary_repeats.yaml
  seeds 19511 through 19520
  headless
  runs root phase08_8_7_primary_repeats

phase08_v8_7_secondary_visible_probe.yaml
  seed 19551
  visible
  runs root phase08_8_7_secondary_probe

phase08_v8_7_secondary_repeats.yaml
  seeds 19561 through 19565
  headless
  runs root phase08_8_7_secondary_repeats
```

Every source declaration, start, intensity, topology, launch override,
controller profile, Stage A/Stage B budget, evaluator-only `0.50 m` stop,
forbidden state/event, final-zero rule, cleanup rule, first-failure rule, and
claim boundary is copied from v8.6. Only schema/evidence semantics, versioned
identities, roots, descriptions, and fresh seeds change.

### No-Gazebo qualification

Before any v8.7 Gazebo process:

1. preserve every historical and v8-v8.6 scenario byte and result;
2. prove schema versions through v10 retain the existing handoff predicate;
3. replay the retained seed-`19411` bag under its original schema-v10
   resolved input and prove it still fails the first-sample rule;
4. replay the same immutable records through a schema-v11 evidence fixture
   and prove exactly one recognized tail sample, a `7.696498 ms` handoff, and
   all later ordinary diagnostics pass;
5. prove schema v11 rejects late handoff, unrecognized tail, GESC leak,
   nonfinite data, contribution error, saturation error, nonzero later
   supervisor command, invalid returned state, and later authority
   reappearance;
6. prove the handoff timeout is evaluator-only and cannot enter the launch
   graph;
7. prove cleanup still rejects any external ROS CLI node or run-session
   survivor;
8. prove all four v8.7/v8.6 scenario pairs differ only in the declared
   versioned evidence, identities, roots, descriptions, and seeds;
9. run focused schema, runner, validator, analyzer, controller, supervisor,
   observability, and legacy tests;
10. run the broad ROS-independent suite, changed-file fatal lint, Python
    compilation, XML/YAML parsing, isolated three-package build, installed
    node construction, source/install parity, and all four installed dry-runs
    without creating a run root;
11. validate Phase 08 context, run `git diff --check`, verify no active
    runtime process, write a separate no-Gazebo qualification record, update
    live status, checkpoint, and commit.

No Gazebo process is authorized until that complete qualification,
checkpoint, and implementation commit pass.

### V8.7 runtime gates

After a separate clean committed dispatch boundary:

1. execute the primary visible probe once, with no ROS-domain monitoring and
   no retry;
2. require every v8.6 behavioral predicate plus schema-v11 causal ownership,
   recording, final zero, and uncontaminated cleanup;
3. analyze it exactly once and retain all nine plots;
4. checkpoint and commit the result before primary repeats;
5. execute ten primary repeats serially/headlessly, stopping at the first
   failure with no retry;
6. only `10/10` authorizes the secondary visible probe;
7. only a passing secondary visible probe authorizes five secondary repeats;
8. only `5/5` secondary repeats authorizes M6.

The v8.7 claim remains limited to the two fixed local-first, two-source,
open-field layouts at simulator-relative `400/1600`. Physical stopping
remains manual operator `Ctrl+C`. Three-light Gazebo execution, wall/obstacle
behavior, arbitrary intensity/layout claims, physical motion, and Phase 09
remain outside this correction.

## Executed M4.8 repeat disposition and M4.9 v8.8 correction amendment

### Fixed v8.7 primary-repeat disposition

The sealed v8.7 primary population is closed as a fixed formal gate failure.
Seeds `19511`, `19512`, `19513`, and `19514` executed exactly once. The first
three passed all fourteen predicates. Seed `19514` completed the full
scientific behavior but failed `supervisor_owned_escape_assist`; it was not
retried, and seeds `19515..19520` were not dispatched.

All four dispatched runs completed one local candidate, exactly one typed
fill, one measured aligned assisted exit, ordinary post-recovery search, one
strictly lower second raw-cost interval, `GOAL_REACHED`, and a later valid
global-proximity sample. Recording, final zero, readiness false, and cleanup
passed `4/4`.

The complete message-level audit of seed `19514` found:

```text
one ordinary GESC diagnostic with zero supervisor contribution
-> 14.125597 ms from recorded nonzero authority to first owned diagnostic
-> 2,678 consecutive supervisor-owned diagnostics
-> no later fallback
-> ordinary causal assist-exit handoff
```

There was no diagnostic equal to GESC plus a nonzero supervisor command. The
first sample is exactly the previous `ESCAPE_REPULSE` arbitration produced
while the controller's separate state subscription had not yet consumed the
externally recorded `ESCAPE_ASSIST` update. Schema v11 bounds the equivalent
cross-topic settling at assist exit but still treats external bag order as
controller-consumption order at assist entry.

The fixed result and all four one-time analysis bundles are retained in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_8_primary_repeats.md
```

V8.7 remains failed and closed. This diagnosis does not relabel it.

### M4.9 objective

Version v8.8 changes no controller, supervisor, detector, fill,
modified-cost, launch, world, source, motion, ranking, timeout, final-zero,
cleanup, or stop behavior. It adds a schema-v12 causal assist-entry evidence
contract while retaining schema v11's causal assist-exit contract unchanged.

This is a fresh formal-evidence version. It does not retry, reopen, mutate, or
add to v8.7.

### Schema-v12 causal assist-entry contract

The existing predicate and evaluator-only timeout remain:

```text
supervisor_owned_escape_assist
supervisor_owned_assist_handoff_timeout_sec: 0.15
```

No new launch/controller parameter is introduced. The same `0.15 s` bound
now applies to both cross-topic entry and exit settling for schema v12.
Schema versions through v11 retain their existing byte-for-behavior
interpretation.

For schema v12, all existing assist-state geometry, direction revision,
measured exit, alignment, positive translation, suppressed GESC, command
freshness, arithmetic, saturation, returned-state, returned-command, and
post-exit causal requirements remain mandatory.

Starting at the later of the first externally recorded `ESCAPE_ASSIST` state
and first externally recorded nonzero supervisor authority command, the
entry evidence must additionally prove:

1. every diagnostic is finite, complete, arithmetically consistent, and
   correctly saturated;
2. before causal ownership, a diagnostic may be only:
   - ordinary GESC with exactly zero supervisor contribution and a fresh
     recorded zero supervisor command; or
   - a zero/failsafe command with valid contribution arithmetic;
3. a diagnostic whose combined command exactly matches a fresh nonzero
   supervisor command occurs within `0.15 s` of the first recorded nonzero
   authority command;
4. every later diagnostic through the returned `SEARCH` boundary matches a
   fresh supervisor command and retains supervisor-only ownership;
5. at least one later nonzero GESC proposal is proven suppressed;
6. at least one later supervisor command has positive linear translation;
7. no diagnostic ever equals GESC plus a nonzero supervisor command; and
8. the result records the entry-transition sample count, entry-handoff delay,
   first-owned diagnostic stamp, steady owned sample count, and evidence
   mode.

An unrecognized transient, missing fresh zero-command support, invalid
command, nonfinite value, contribution error, saturation error, true
GESC-plus-nonzero-supervisor sum, handoff later than `0.15 s`, missing owned
sample, or any fallback after ownership fails.

This is not a general grace period and does not excuse additive assist or
persistent previous-state behavior. It is a bounded proof of asynchronous
delivery across the already-existing state, command, and diagnostic topics.

### Fresh fixed inputs

Create four schema-v12 scenarios:

```text
phase08_v8_8_primary_visible_probe.yaml
  seed 19601
  visible
  runs root phase08_8_8_primary_probe

phase08_v8_8_primary_repeats.yaml
  seeds 19611 through 19620
  headless
  runs root phase08_8_8_primary_repeats

phase08_v8_8_secondary_visible_probe.yaml
  seed 19651
  visible
  runs root phase08_8_8_secondary_probe

phase08_v8_8_secondary_repeats.yaml
  seeds 19661 through 19665
  headless
  runs root phase08_8_8_secondary_repeats
```

Every source, start, intensity, topology, launch override, controller profile,
Stage A/Stage B budget, evaluator-only `0.50 m` stop, forbidden state/event,
final-zero rule, cleanup rule, first-failure rule, and claim boundary is
copied from v8.7. Only schema/evidence semantics, versioned identities, roots,
descriptions, and fresh seeds change.

### No-Gazebo qualification

Before any v8.8 Gazebo process:

1. preserve every historical and v8-v8.7 scenario byte and result;
2. prove schema versions through v11 retain their exact existing entry and
   exit behavior;
3. replay retained seed `19514` under its original schema-v11 resolved input
   and prove it still fails on the first entry diagnostic;
4. replay the same immutable records through a schema-v12 fixture and prove
   exactly one recognized ordinary transition, a `14.125597 ms` entry
   handoff, all `2,678` later assist diagnostics owned, and the existing
   causal exit proof passes;
5. prove schema v12 rejects late entry, unknown entry, a stale or missing
   zero-command transition, GESC plus a nonzero supervisor command, nonfinite
   data, contribution error, saturation error, missing ownership, and later
   fallback;
6. prove the shared handoff timeout remains evaluator-only and cannot enter
   the launch graph;
7. prove all four v8.8/v8.7 scenario pairs differ only in the declared
   versioned evidence, identities, roots, descriptions, and seeds;
8. run focused schema, runner, validator, analyzer, controller, supervisor,
   observability, and legacy tests;
9. run the broad ROS-independent suite, changed-file fatal lint, Python
   compilation, XML/YAML parsing, isolated three-package build, installed
   node construction, source/install parity, and all four installed dry-runs
   without creating a run root; and
10. validate Phase 08 context, run `git diff --check`, verify no active
    runtime process, write a separate no-Gazebo qualification record, update
    live status, checkpoint, and commit.

No Gazebo process is authorized until that complete qualification,
checkpoint, and implementation commit pass.

### V8.8 runtime gates

After a separate clean committed dispatch boundary:

1. execute the primary visible probe once, with no ROS-domain monitoring and
   no retry;
2. require every v8.7 behavioral predicate plus schema-v12 causal entry and
   exit ownership, complete recording, final zero, and uncontaminated
   cleanup;
3. analyze it exactly once and retain all nine plots;
4. checkpoint and commit the result before primary repeats;
5. execute ten primary repeats serially/headlessly, stopping at the first
   failure with no retry;
6. analyze every dispatched repeat exactly once after the population closes;
7. only `10/10` authorizes the secondary visible probe;
8. only a passing secondary visible probe authorizes five secondary repeats;
9. analyze every dispatched secondary run exactly once; and
10. only `5/5` secondary repeats authorizes M6.

The sealed-run observation protocol from v8.7 remains mandatory. No external
ROS/DDS participant may join an active v8.8 domain.

The v8.8 claim remains limited to the same two fixed local-first, two-source,
open-field layouts at simulator-relative `400/1600`. Physical stopping
remains manual operator `Ctrl+C`. Three-light Gazebo execution, wall/obstacle
behavior, arbitrary intensity/layout claims, physical motion, and Phase 09
remain outside this correction.

## Executed M4.9 disposition and M4.10 v8.9 dual-topology amendment

### Fixed v8.8 primary-repeat disposition

The sealed v8.8 primary population is closed as a fixed formal gate failure.
Seeds `19611` through `19616` executed exactly once. Seeds `19611..19615`
passed all fourteen predicates. Seed `19616` completed the full scientific
behavior but failed the assist-only recovery topology. It was not retried,
and seeds `19617..19620` were not dispatched.

All six runs found the first/local candidate, created exactly one typed active
fill, escaped that basin, found a distinct second candidate, ranked the second
raw-cost interval strictly below the retained first-candidate bound, emitted
`GOAL_REACHED`, and converged inside the fixed simulation-only `0.50 m`
global-proximity radius. Recording, final zero, readiness false, and cleanup
passed `6/6`.

Seed `19616` followed:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Its direct repulse lasted `23.328587 s`, exited `1.401137 m` from the frozen
fill center against a `1.366771 m` exit radius, and aligned `0.947517529`
with the frozen revision-one direction. Every mature radial-progress sample
exceeded the `0.05 m` stall threshold. Across `3,015` synchronized repulse
control samples, supervisor contribution was zero and combined command
equaled ordinary GESC exactly. It therefore correctly emitted no
`ESCAPE_STALLED` event and never invoked the fallback assist.

The architecture already declares direct repulse completion and
stall-triggered assist as two valid recovery branches. The v8.8 Stage A
implementation instead selected only the assisted branch whenever assist was
enabled, while the scenario also required `ESCAPE_ASSIST`,
`ESCAPE_STALLED`, and `supervisor_owned_escape_assist` on every seed. Stage A
withheld its completion stamp, which cascaded into controller-goal,
ground-truth, ranking-scope, and global-proximity failures even though
seed `19616` reached `GOAL_HOLD` and ended `0.104056 m` from the global.

The fixed result and six one-time analysis bundles are retained in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_9_primary_repeats.md
```

V8.8 remains failed and closed. Its secondary and broad gates remain
prohibited.

### M4.10 objective

Version v8.9 changes no controller, supervisor, detector, fill, modified
cost, launch argument, world, source, motion, ranking, timeout, final-zero,
cleanup, or stop behavior. It adds a schema-v13 dual-topology recovery
evidence contract that matches the already-designed conditional control
flow:

```text
direct success:
  ESCAPE_REPULSE -> SEARCH

measured-stall fallback:
  ESCAPE_REPULSE -> ESCAPE_ASSIST -> SEARCH
```

This is a fresh formal-evidence version. It does not retry, reopen, mutate,
or add to v8.8.

### Schema-v13 conditional command-ownership predicate

Add the schema-v13-only result predicate:

```text
escape_command_ownership
```

It is valid only for the existing counted-candidate open-field profile with
candidate-informed fill, approach-continuity affine escape, active-fill
transit, supervisor-owned assist enabled, operating bounds disabled,
recenter disabled, recoverable navigation disabled, and post-recovery
guidance disabled.

Schema versions through v12 retain their exact existing path selection,
predicate set, normalization, live Stage A behavior, offline result behavior,
and `supervisor_owned_escape_assist` interpretation.

For schema v13, Stage A and full-lifecycle evidence accept exactly these two
paths:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD

SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

The common required event sequence is:

```text
CONVERGENCE_CONFIRMED
-> FILL_CREATED
-> ESCAPE_STARTED
-> CONVERGENCE_CONFIRMED
-> GOAL_REACHED
```

`ESCAPE_STALLED` is required by the command state machine before the assist
branch, forbidden on the direct branch, and not a common unconditional
event.

The new predicate is branch strict:

1. If any valid `ESCAPE_ASSIST` interval occurs, the result must execute the
   complete schema-v12 causal supervisor-ownership proof unchanged,
   including entry and exit handoffs, fresh commands, suppressed nonzero
   GESC, contribution arithmetic, saturation, revision-one geometry,
   positive translation, measured exit, alignment, and returned ordinary
   ownership. A failed assisted interval may not fall back to the direct
   proof.
2. If no valid `ESCAPE_ASSIST` interval occurs, the result must prove one
   direct `ESCAPE_REPULSE -> SEARCH` recovery episode and all of the direct
   evidence below.

The direct branch must prove:

1. exactly one matching `ESCAPE_STARTED` event supplies a finite positive
   exit radius, finite center, unit selected direction, and revision one;
2. every recorded repulse state through the returned `SEARCH` boundary
   retains that center, direction, radius, revision, valid geometry, weights
   `(raw, Gaussian, affine) = (0, 1, 1)`, and `failsafe=false`;
3. no `ESCAPE_STALLED` event, stalled state sample, `ESCAPE_ASSIST` state, or
   nonzero supervisor command occurs in the episode;
4. at least one mature finite radial-progress sample meets or exceeds the
   declared `minimum_radial_progress_m`, and the recorded radial distance
   reaches the frozen exit radius;
5. every evaluated repulse diagnostic is finite, complete, arithmetically
   consistent, correctly saturated, has zero supervisor contribution, and
   has combined command exactly equal to the GESC proposal;
6. at least one repulse diagnostic has a nonzero GESC proposal, so the proof
   cannot pass on an all-zero command interval;
7. the first returned `SEARCH` boundary identifies
   `ESCAPE_REPULSE -> SEARCH` stable exit, restores weights `(1,1,0)`, clears
   safe direction and escape authority, and retains zero supervisor command;
8. the first finite odometry sample at or immediately after that boundary
   has positive fill-to-exit displacement, distance at least the frozen exit
   radius, and unit-vector alignment at least `+0.80` against the frozen
   selected direction; and
9. the result records branch, interval stamps, repulse state/control counts,
   mature progress count/range, exit radius, measured exit, distance,
   alignment, ordinary-owner count, and evidence mode.

Missing or conflicting geometry, revision change, insufficient distance,
alignment below `+0.80`, missing mature progress, a stalled sample without
assist, any assist state on the direct branch, nonzero supervisor command,
GESC/supervisor addition, invalid command, nonfinite value, contribution
error, saturation error, all-zero control, wrong returned weights, retained
authority, or missing returned `SEARCH` fails.

The direct branch is not a vacuous “assist not observed” pass. It is a
positive measured recovery and command-ownership proof.

### Fresh fixed inputs

Create four schema-v13 scenarios:

```text
phase08_v8_9_primary_visible_probe.yaml
  seed 19701
  visible
  runs root phase08_8_9_primary_probe

phase08_v8_9_primary_repeats.yaml
  seeds 19711 through 19720
  headless
  runs root phase08_8_9_primary_repeats

phase08_v8_9_secondary_visible_probe.yaml
  seed 19751
  visible
  runs root phase08_8_9_secondary_probe

phase08_v8_9_secondary_repeats.yaml
  seeds 19761 through 19765
  headless
  runs root phase08_8_9_secondary_repeats
```

Every source, start, intensity, topology, launch override, controller profile,
Stage A/Stage B budget, evaluator-only `0.50 m` stop, forbidden state/event,
final-zero rule, cleanup rule, first-failure rule, and claim boundary is
copied from v8.8. Only schema/evidence semantics, the two declared recovery
paths, common conditional-event contract, predicate identity, versioned
identities, roots, descriptions, and fresh seeds change.

### No-Gazebo qualification

Before any v8.9 Gazebo process:

1. preserve every historical and v8-v8.8 scenario byte and result;
2. prove schema versions through v12 retain their exact existing behavior;
3. replay retained seed `19616` through its original schema-v12 resolved
   input and prove it remains failed on the assist-only topology;
4. replay the same immutable messages through a schema-v13 fixture and prove
   the direct branch passes with the retained state path, `3,015` ordinary
   repulse diagnostics, zero supervisor contribution, `1.401137 m` measured
   exit, `0.947517529` alignment, strict raw-cost ranking, and valid
   post-recovery global proximity;
5. replay retained passing assisted seed `19611` through schema v13 and prove
   the new predicate selects the assisted branch while reproducing the
   schema-v12 entry and schema-v11 exit evidence exactly;
6. prove schema v13 rejects direct-path insufficient distance, low
   alignment, missing/low progress, stalled-without-assist, nonzero
   supervisor command, GESC-plus-supervisor command, all-zero control,
   nonfinite data, arithmetic error, saturation error, geometry/revision
   mismatch, missing returned cleanup, and any attempt to use direct proof
   after entering assist;
7. retain and rerun every schema-v12 assisted-branch negative fixture;
8. prove all four v8.9/v8.8 scenario pairs differ only in the declared
   versioned evidence, paths/events, predicate, identities, roots,
   descriptions, and seeds;
9. run focused schema, runner, validator, analyzer, controller, supervisor,
   observability, and legacy tests;
10. run the broad ROS-independent suite, changed-file fatal lint, Python
    compilation, XML/YAML parsing, isolated three-package build, installed
    node construction, source/install parity, and all four installed dry-runs
    without creating a run root; and
11. validate Phase 08 context, run `git diff --check`, verify no active
    runtime process, write a separate no-Gazebo qualification record, update
    live status, checkpoint, and commit.

No Gazebo process is authorized until that complete qualification,
checkpoint, and implementation commit pass.

### V8.9 runtime gates

After a separate clean committed dispatch boundary:

1. execute the primary visible probe once, with no ROS-domain monitoring and
   no retry;
2. require every v8.8 behavioral predicate plus schema-v13 conditional
   command ownership, complete recording, final zero, and uncontaminated
   cleanup;
3. analyze it exactly once and retain all nine plots;
4. checkpoint and commit the result before primary repeats;
5. execute ten primary repeats serially/headlessly, stopping at the first
   failure with no retry;
6. analyze every dispatched repeat exactly once after the population closes;
7. only `10/10` authorizes the secondary visible probe;
8. only a passing secondary visible probe authorizes five secondary repeats;
9. analyze every dispatched secondary run exactly once; and
10. only `5/5` secondary repeats authorizes M6.

The sealed-run observation protocol from v8.8 remains mandatory. No external
ROS/DDS participant may join an active v8.9 domain.

The v8.9 claim remains limited to the same two fixed local-first, two-source,
open-field layouts at simulator-relative `400/1600`. Physical stopping
remains manual operator `Ctrl+C`. Three-light Gazebo execution, wall/obstacle
behavior, arbitrary intensity/layout claims, physical motion, and Phase 09
remain outside this correction.

## Executed M4.10 disposition and M4.11 v8.10 recorder-CWD amendment

### Fixed v8.9 primary-visible disposition

The one authorized v8.9 primary-visible seed `19701` attempt is closed as a
fixed pre-Gazebo infrastructure failure. The installed runner was invoked
from `/tmp`; its staged global-proximity process owner launched `record_run`
without a working directory; and the recorder's
`git_state(Path.cwd())` metadata step failed because `/tmp` is not a Git
checkout.

The runner returned before Gazebo or the recording graph started. No bag or
behavioral evidence exists, cleanup passed, and no runtime process remained.
The one post-closure analyzer invocation also failed because its manually
transcribed target omitted `_19701`. Seed `19701` is not retried, and no
later v8.9 gate is dispatched. The immutable result is retained in:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_8_m4_10_primary_probe.md
```

This failure does not alter the completed schema-v13 retained-replay
qualification. It reveals a scenario-runner/recorder integration defect and
an analysis-target transcription hazard, not a controller or evidence
algorithm defect.

### M4.11 objective

Version v8.10 makes the installed scenario runner independent of the shell
working directory and eliminates manual construction of analysis targets.
It changes no controller, supervisor, detector, fill, affine term, modified
cost, raw-cost ranking, launch argument, source, world, motion behavior,
schema-v13 recovery evidence, Stage A/Stage B logic, simulation stop radius,
final-zero rule, cleanup rule, or physical path.

V8.10 is a fresh infrastructure-corrected experiment version. It does not
retry, reopen, mutate, or add evidence to v8.9.

### Recorder child working-directory correction

`run_scenario.py` already resolves the live checkout into
`REPOSITORY_ROOT`. Pass that exact absolute path as
`cwd=REPOSITORY_ROOT` to the recorder child in all three owners:

```text
_run_record_to_boundary
_run_record_to_global_proximity
run_record_process
```

Do not change `record_run.py`, Git metadata semantics, process-group
ownership, signal escalation, output capture, timeouts, private ROS context,
or graceful-stop handling. The recorder remains the sole Phase 05 recorder
and validator owner. Its recorded `working_directory` must now identify the
checkout, and its Git metadata must describe the committed dispatch tree
regardless of the runner caller's directory.

Focused tests must intercept each `subprocess.Popen` owner and prove:

1. the normal record path receives `cwd=REPOSITORY_ROOT`;
2. the boundary-observed record path receives the same value;
3. the staged local-recovery/global-proximity path receives the same value;
4. every existing process, timeout, signal, lifecycle-cleanup, and return
   contract remains unchanged; and
5. an arbitrary caller working directory cannot be forwarded to
   `record_run`.

### Summary-owned analysis target

Every v8.10 dispatch log must retain the exact `summary_path` emitted by the
runner. After population closure and cleanup, analysis preparation must:

1. read that exact summary rather than select a summary by modification time;
2. require the expected executed-run count and case IDs;
3. read each `run_directory` directly from the summary;
4. verify that each directory is below the declared fresh v8.10 root and
   contains the expected complete bag before invoking analysis; and
5. invoke the analyzer exactly once per dispatched complete run, recording
   its command, return code, log, artifact paths, and hashes.

No run ID or run-directory suffix may be reconstructed manually. A missing,
ambiguous, out-of-root, incomplete, or mismatched summary entry stops
analysis and later dispatch. It is retained as an infrastructure failure and
is not repaired by a second analyzer invocation.

### Fresh fixed inputs

Create four schema-v13 scenarios:

```text
phase08_v8_10_primary_visible_probe.yaml
  seed 19801
  visible
  runs root phase08_8_10_primary_probe

phase08_v8_10_primary_repeats.yaml
  seeds 19811 through 19820
  headless
  runs root phase08_8_10_primary_repeats

phase08_v8_10_secondary_visible_probe.yaml
  seed 19851
  visible
  runs root phase08_8_10_secondary_probe

phase08_v8_10_secondary_repeats.yaml
  seeds 19861 through 19865
  headless
  runs root phase08_8_10_secondary_repeats
```

Every source, start, intensity, topology, controller override, Stage A/Stage B
budget, schema-v13 conditional recovery path, evaluator-only `0.50 m` stop,
forbidden state/event, final-zero rule, cleanup rule, and first-failure rule
is copied from v8.9. Only versioned identities, descriptions, evidence
roots, and fresh seeds change.

The two fixed layouts remain:

```text
primary:
  start (0.0, 0.0)
  local (1.0606601717798214, 1.0606601717798212)
  global (3.5, 3.5)
secondary:
  start (0.0, 0.0)
  local (0.5740251485476348, 1.38581929876693)
  global (3.5, 3.5)
relative source inputs:
  local/global = 400/1600
known topology:
  one local plus one global; maximum one active typed fill
```

### No-Gazebo qualification

Before any v8.10 Gazebo process:

1. preserve every historical and v8-v8.9 scenario, world, result, report,
   plot, and failure unchanged;
2. prove the production diff is limited to the three recorder-child
   `cwd=REPOSITORY_ROOT` arguments plus the four fresh scenario inputs;
3. prove normal, boundary, and staged recorder launches receive the resolved
   checkout working directory and retain their existing lifecycle behavior;
4. rerun schema-v13 direct and assisted retained replays and all schema-v12
   compatibility and negative fixtures;
5. prove all four v8.10/v8.9 scenario pairs differ only in versioned
   identities, descriptions, roots, and fresh seeds;
6. run focused schema, runner, validator, analyzer, controller, supervisor,
   observability, recording, final-zero, shifted-world, V6, legacy, and
   historical-immutability tests;
7. run the broad ROS-independent suite, changed-file fatal lint, Python
   compilation, XML/YAML parsing, and `git diff --check`;
8. build `ros_esc_interfaces`, `ros_esc`, and
   `turtlebot3_rotating_sensor` into a fresh isolated
   `/tmp/phase08_8_v8_10_release_qual.*` root;
9. prove source/install byte parity for the four scenarios and required
   launch/runtime owners, then run all four installed dry-runs from `/tmp`;
10. require exactly `1/10/1/5` supported resolved runs, the declared seeds,
    fresh roots, unchanged bounded timings and predicates, and no run-root
    creation;
11. verify all four fresh roots are absent, no active ROS/Gazebo process
    exists, and the worktree contains only the reviewed correction; and
12. write a durable no-Gazebo qualification, update live status, checkpoint,
    inspect, and commit.

No Gazebo process is authorized until the complete qualification,
checkpoint, and implementation commit pass. A separate clean committed
dispatch boundary must then name only the installed visible seed `19801`.

### V8.10 runtime gates

Use isolated domains and log roots:

```text
primary visible:    ROS_DOMAIN_ID 225
primary repeats:    ROS_DOMAIN_ID 226
secondary visible:  ROS_DOMAIN_ID 227
secondary repeats:  ROS_DOMAIN_ID 228
```

After the separate dispatch boundary:

1. execute primary visible seed `19801` once with GUI, no external ROS/DDS
   monitoring, and no retry;
2. require complete recording/Git metadata, every v8.9 behavioral predicate,
   schema-v13 conditional command ownership, final zero, and uncontaminated
   cleanup;
3. derive its run directory from the exact scenario summary, analyze it once,
   and retain all nine plots;
4. checkpoint and commit the result before primary repeats;
5. execute seeds `19811..19820` serially/headlessly, stopping at the first
   behavioral, formal, infrastructure, or cleanup failure with no retry;
6. after population closure, analyze every dispatched complete run exactly
   once from its exact summary-owned path;
7. only `10/10` primary-repeat passes authorize secondary visible seed
   `19851`;
8. only a passing secondary visible probe authorizes seeds `19861..19865`;
9. analyze each secondary run exactly once after its population closes; and
10. only `5/5` secondary-repeat passes authorize M6.

Every attempt is bounded by the unchanged scenario and wall timeouts. During
sealed execution, observation is limited to OS process state and retained
files; no external ROS/DDS participant may join an active domain.

The v8.10 claim remains limited to two reproducible, fixed local-first,
two-source, obstacle-free layouts at simulator-relative `400/1600`. It is
not evidence for arbitrary light position or intensity, three lights,
wall/obstacle behavior, or broad field robustness. The global coordinate
remains evaluator-only. Physical motion remains prohibited in Phase 08, and
the physical controller must continue until the operator presses `Ctrl+C`;
no simulation proximity stop may enter the physical path.

## Active goal-continuation amendment — v8.11

The bounded v8.10 closeout remains immutable, but it did not finish the
already-approved broader Phase 08.8 objective. The active continuation is now
defined by the separately reviewable subplan:

```text
docs/codex/gesc_gaussian/plans/phase_08_8_v8_11_plan.md
```

That subplan is authoritative for the fresh schema-v14 evaluator-topology
correction, retained evidence replay, secondary visible/repeat gate, and
sealed varied-layout/intensity matrix. It changes no v8.10 result and
authorizes no Gazebo process until its own no-Gazebo qualification,
checkpoint, and implementation commit pass.
