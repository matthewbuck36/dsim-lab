# Phase 08.6 Plan — V6 Two-Light Hue-Ratio Escape Demonstration

## Status and authority

**APPROVED FOR IMPLEMENTATION AND EXECUTION.**

The user directed Codex on 2026-07-28 to replace the overconstrained V5
acceptance campaign with a focused simulation demonstration:

- simulate two lights first, while retaining future three-light compatibility;
- model the available Philips Hue range as nominal `0-1600` lumen input and
  sweep multiple app-percentage ratios;
- preserve Nick's original GESC, robot startup orientation, rotating
  photoresistor/encoder path, filters, gains, topics, and controller ownership;
- do not aim, steer, or otherwise assist the robot toward the local light;
- use a laboratory-realistic `4 m x 4 m` room;
- define primary success as local convergence, Gaussian fill, escape,
  recenter, and resumed search;
- defer the 120-run robustness campaign and three-light execution until the
  two-light mechanism works.

This Plan authorizes bounded V6 implementation, four visible-Gazebo ratio
runs, selection of a genuine local-recovery ratio, three headless repeats of
that fixed ratio, reporting, checkpoints, and bounded commits. It does not
authorize physical hardware, Phase 09, a simulation-readiness tag, modification
or relabelling of V5, or changes to the original GESC control law.

## Claim boundary

V6 asks:

> In a two-light field that fits the physical laboratory, can unchanged GESC
> converge at the lower-output local light, create a Gaussian fill there,
> escape it using the robust extension, recenter, and resume GESC search?

A V6 success is a simulation development demonstration, not a universal
robustness result, three-light result, physical calibration, physical robot
authorization, or simulation-readiness claim. Reaching the stronger global
light after resumed search is recorded as a secondary outcome and is not part
of the primary V6 gate.

## Historical boundary

V1-V5 and all of their external roots remain immutable historical evidence.
V5's `0/8` intended-blocker result is not reclassified. V6 uses the absent
fresh root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v6
```

V6 case IDs, seeds, scenario bytes, and run IDs are fresh.

## Preserved implementation and ownership

V6 reuses:

- `gazebo.launch.xml` as the sole simulation graph;
- `custom_controller` as the sole `/cmd_vel` publisher;
- the existing GESC filter/controller configuration;
- the existing constant full-rotation photoresistor profile and encoder path;
- the existing robust supervisor, typed Gaussian-fill owner, recorder,
  completeness validator, bag analyzer, and serial scenario runner.

The GESC Gaussian wrapper's existing startup remains:

```text
init_yaw_angle=0
input_encoder_data_to_filter=True
Constant_Full_Rotation at 20 rpm
```

No orientation-specific launch value is selected from outcomes. No controller,
node, launch graph, recorder, validator, physical fork, or algorithm fork may
be added.

## Physical and simulation geometry

The existing room bounds remain:

```text
x: [-2.0, 2.0] m
y: [-2.0, 2.0] m
wall margin: 0.35 m
```

The fixed two-light geometry is:

```text
robot start:  (-1.30, -0.20) m, yaw 0
local light:  (-0.80,  0.00) m
global light: ( 1.30,  0.80) m
```

The local light lies approximately on the start-to-global segment and is about
`0.54 m` from the start. The source separation is about `2.25 m`. All points
fit the `4 m x 4 m` room and retained wall margin.

The fixed start yaw is the repository's ordinary zero default, not a
behavior-selected orientation. V6 does not randomize or tune orientation.

## Hue percentage and nominal lumen sweep

The simulator's value is a relative model input, not yet an absolute lux
calibration. Each case records both Hue percentage and nominal lumen input:

| Case | Local Hue | Local nominal | Global Hue | Global nominal | Ratio |
|---|---:|---:|---:|---:|---:|
| H25 | 25% | 400 | 100% | 1600 | 0.25 |
| H50 | 50% | 800 | 100% | 1600 | 0.50 |
| H70 | 70% | 1120 | 100% | 1600 | 0.70 |
| H85 | 85% | 1360 | 100% | 1600 | 0.85 |

H25 is a weak-local reference close to V5's failed intensity ratio. The sweep
is development evidence: some ratios are expected not to capture the robot.
All four execute unless an infrastructure, cleanup, collision, or safety hard
stop occurs.

## Runtime local-recovery evidence

V6 adds one evidence predicate inside the existing scenario schema and runner:
`observed_local_recovery`.

For the first typed active fill, the runner must locate its causal
`CONVERGENCE_CONFIRMED` event and extract the event's
`fill_center_x_m/fill_center_y_m`. The predicate passes only when:

- the first verification takes the below-target branch;
- the convergence point is within `0.60 m` of the declared local source;
- the convergence point is at least `0.75 m` from the declared global source;
- the first active fill center is within `0.50 m` of that convergence point;
- the required recovery path and events independently pass.

This replaces V5's brittle distance to a precomputed basin. It cannot accept
V5-style fills at the global light because a convergence point close to the
global source fails the explicit global-separation requirement.

The configuration is declared in each scenario under
`success.local_recovery` and bound into the resolved case key.

## Primary success and secondary outcomes

Every V6 case requires:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> RECENTER
-> SEARCH
```

Required events:

```text
CONVERGENCE_CONFIRMED
FILL_CREATED
ESCAPE_STARTED
RECENTER_STARTED
RECENTER_COMPLETE
```

Forbidden:

```text
ESCAPE_ASSIST
FAILSAFE
FILL_REJECTED
FILL_DESIGN_FAILED
TIMEOUT
collision
```

The affine-assist extension is disabled for this focused pure-Gaussian
demonstration. This does not change original GESC search behavior.

Recording completeness, cleanup, final command zero, final readiness false,
timestamp/causality integrity, readable sqlite3 evidence, and no collision
remain mandatory. Controller/global goal, orbit-count limits, revisit rate,
family floors, p95 duration, and exact numeric reproducibility are secondary
or deferred.

## Run allocation and selection

Visible ratio sweep:

```text
4 cases, one per ratio, visible Gazebo, fixed geometry and original startup
```

A ratio is eligible only if its recording/cleanup and complete primary
`observed_local_recovery` contract pass. If multiple ratios pass, select the
lowest local/global ratio. Selection does not tune GESC or Gaussian parameters.

If no ratio is eligible, close V6 failed without repeats. Do not enlarge a
distance threshold after observing the runs.

If a ratio is eligible, freeze that ratio in a fresh repeat scenario and
commit it before repeat execution:

```text
3 fresh seeds, same geometry/profile/parameters, headless Gazebo
```

V6 repeatability passes with at least `2/3` complete primary recoveries and no
integrity, cleanup, collision, or safety failure. All attempts remain visible
in the denominator.

Maximum V6 Gazebo executions: `7`.

## Fresh artifacts

Tracked:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v6_hue_sweep.yaml
  phase08_v6_selected_repeats.yaml

docs/codex/gesc_gaussian/validation/
  phase_08_v6_sweep_commitment.json
  phase_08_v6_selection.json
  phase_08_v6_validation_report.md
  phase_08_v6_failure_report.md

docs/codex/gesc_gaussian/handoffs/
  phase_08_6_handoff.md
```

The repeat scenario, selection, validation report, failure report, and handoff
are created only when their stage is reached. Large logs, bags, plots, and
summaries stay below the external root.

## Qualification

Before Gazebo:

1. require clean Git and no active ROS/Gazebo descendants;
2. validate Phase 08 implementation context;
3. require the V6 root to be absent;
4. validate strict schema, exactly two lights, Hue/lumen mapping, fixed
   geometry, source bounds, original startup, and no affine assist;
5. run focused schema/runner/analysis tests;
6. run the retained functional suite;
7. isolated-build `ros_esc_interfaces`, `turtlebot3_rotating_sensor`, and
   `ros_esc`;
8. verify installed entrypoints and V6 scenario resource;
9. instantiate the robust supervisor/fill graph and central launch;
10. run the installed V6 dry run;
11. verify disk and empty process boundaries.

The exact qualified isolated install must be sourced for Gazebo execution.

## Milestones

### M0 — open V6

Save this Plan, update live status, validate plan/implementation context,
checkpoint, and commit.

### M1 — implement local-recovery evidence and scenarios

Extend the existing schema/runner owners, add focused tests, generate the exact
four-case suite and commitment, and package it. Preserve V1-V5 and legacy
behavior.

### M2 — qualify

Create the fresh root transactionally and pass source, test, build, installed,
dry-run, process, and disk gates.

### M3 — visible ratio sweep

Execute all four cases serially with Gazebo visible unless a hard safety,
integrity, or cleanup stop occurs. Analyze each retained bag once.

### M4 — freeze and repeat

If eligible, select the lowest passing ratio, commit the three fresh repeat
cases, then run them headless from the exact qualified implementation.

### M5 — closeout

Write selection, report/failure report, status, checkpoint, handoff, exact
executed/not-run counts, Git state, and limitations. Do not create a readiness
tag.

## Stop conditions

Level A — stop and request direction if work would change original GESC,
controller ownership, cost sign/units, canonical topics, simulation/physical
parity, the two-light objective, or the physical boundary.

Level B — document, test, checkpoint, and continue for bounded schema, runner,
scenario, recording, launch, packaging, timeout, or reporting corrections
that preserve this Plan.

Level C — close V6 honestly if no sweep ratio demonstrates genuine local
recovery or fewer than two of three eligible repeats pass.

Every ROS, Gazebo, test, build, and batch command is finite or explicitly
timeout-bounded. Historical evidence is never repaired, overwritten, or
relabelled.

## Immediate next criterion

Implement and test `observed_local_recovery` plus the exact four-case V6 suite
without launching Gazebo or creating the V6 evidence root.
