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
