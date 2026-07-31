# Phase 08.8 M3.1 No-Gazebo Qualification

## Disposition

**QUALIFIED FOR ONE VERSIONED V8.1 PRIMARY VISIBLE PROBE, SUBJECT TO MATERIAL
CHECKPOINT AND COMMIT.**

This record qualifies the bounded correction to the failed fixed v8 primary
probe. No Gazebo, recorder, rosbag recorder, analyzer, physical hardware, or
scenario execution occurred while producing this evidence.

The failed `phase08_v8_primary_visible_probe.yaml` and its retained run remain
unchanged and failed. The correction is available only in the four
`phase08_v8_1_*` scenario files.

## Corrected behavior

The fixed v8 failure established that the first candidate, candidate count,
raw-cost summary, one-fill cardinality, and revisit suppression worked. The
robot failed because the short Gaussian-only departure stalled, the historical
assist path redesigned the same fill, and ordinary search resumed while the
robot was still close enough to return to the local basin.

M3.1 adds one opt-in parameter:

```text
open_field_escape_assist_enabled: false by default
```

When selected in the v8.1 open-field profile:

```text
measured ESCAPE_REPULSE stall
-> ESCAPE_ASSIST in the same escape episode
-> no fill redesign, merge, or supersession
-> raw/Gaussian/affine weights = 0/1/0
-> select an outward direction from current odometry and frozen fill center
-> publish a bounded command through the existing supervisor/controller owner
-> retain the Gaussian repulsion
-> require the enlarged measured exit boundary and hold
-> zero the supervisor command
-> ordinary GESC SEARCH
```

The selected v8.1 fixed profile uses:

```text
gaussian_fill_exit_sigma:          8.0
escape_max_sec:                   35.0
escape_exit_hold_sec:              1.0
maximum supervisor linear speed:   0.10 m/s
maximum supervisor angular speed:  0.40 rad/s
operating bounds:                  disabled
recenter:                          disabled
recoverable navigation:            disabled
post-recovery guidance:            disabled
affine cost:                        disabled
known source count:                2
maximum fills:                     1
```

The assist direction uses only the pose stream already required for adaptive
fill geometry and the accepted fill center. It does not use a source
coordinate, source role, Vicon pose, global pose, room dimension, evaluator
proximity, waypoint, route map, planner, or persistent traveled-path map. It
does not add a node, message, topic, dependency, recorder, validator, launch
graph, or `/cmd_vel` publisher.

Historical `ESCAPE_ASSIST` behavior retains its `(0, 1, 1)` weights and
redesign path. The v8.1 opt-in behavior uses `(0, 1, 0)`. Every legacy and v8
default remains unchanged.

## Versioned fixed inputs

The installed scenarios resolve as:

```text
phase08_v8_1_primary_visible_probe.yaml
  1 GUI case
  seed 18901

phase08_v8_1_primary_repeats.yaml
  10 headless cases
  seeds 18911 through 18920

phase08_v8_1_secondary_visible_probe.yaml
  1 GUI case
  seed 18951

phase08_v8_1_secondary_repeats.yaml
  5 headless cases
  seeds 18961 through 18965
```

All source positions, `400/1600` inputs, starts, source topology, raw candidate
policy, confirmation policy, Stage A and Stage B budgets, and evaluator-only
`0.50 m` boundary match their corresponding v8 definitions. The only
behavioral correction is the versioned finite outward-departure policy and its
larger escape boundary/budget.

The required v8.1 controller path is:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> ESCAPE_ASSIST
-> SEARCH
-> VERIFY_EXTREMUM
-> GOAL_HOLD
```

Required events include `ESCAPE_STALLED`. `FILL_MERGED`,
`FILL_SUPERSEDED`, `RECENTER`, `TIMEOUT`, and `FAILSAFE` remain forbidden.

## Final test evidence

All test commands used source-checkout precedence over generated interfaces
from the isolated ROS environment and a valid isolated ROS domain.

Focused state-machine, detector, supervisor, core, and legacy behavior:

```text
188 passed in 7.11 s
JUnit:
  /tmp/phase08_8_1_focused.xml
SHA-256:
  b20dc38abfa1c2032544a488ca071bb92c594e48b0404d05febcc41b99711d50
```

Scenario schema, runner, and Phase 08 validator:

```text
386 passed, 1 skipped in 94.39 s
JUnit:
  /tmp/phase08_8_1_scenario.xml
SHA-256:
  2f9d226abdffadfa6ad1a5822f642856deca70e2d56c8109d2c451dd012a3062
```

The one skip is the explicit Gazebo-only integration at this no-Gazebo
boundary.

Analyzer/candidate plot tests:

```text
13 passed in 0.79 s
JUnit:
  /tmp/phase08_8_1_analysis.xml
SHA-256:
  60a27b624c3f2baf490ba2f1941ceb67931855acda19c2ff50e1cc43760a53c6
```

Complete ROS-independent functional regression, excluding the repository's
separate style/copyright files:

```text
749 passed, 2 skipped in 133.87 s
JUnit:
  /tmp/phase08_8_1_broad.xml
SHA-256:
  1feed992761584066f7baa6c66c76f07d1c05a0a5c2bdceb0a453b70c1bccdce
```

The two skips are the unchanged environment-conditional Gazebo integrations.

Fatal changed-file Python lint (`E9,F63,F7,F82`), changed-Python compilation,
launch XML parsing, YAML resolution, `git diff --check`, and
`validate_phase_context.sh 08 implement` pass.

## Fresh isolated build and installed graph

The final from-scratch build used:

```text
install prefix:
  /tmp/phase08_8_1_release_qual/install
build prefix:
  /tmp/phase08_8_1_release_qual/build
log prefix:
  /tmp/phase08_8_1_release_qual/log
packages:
  ros_esc_interfaces
  ros_esc
  turtlebot3_rotating_sensor
result:
  3 packages finished in 12.1 s
```

Source/install byte parity passes for `9/9` final runtime owners: four Python
owners, four v8.1 scenarios, and the central Gazebo launch.

Installed nonexecuting launch evidence:

```text
/tmp/phase08_8_1_release_show_args.txt
  00768473b61bcb5bf7541c1e56a4318235636ec9e3000e872c7e1f981bcddcf0

/tmp/phase08_8_1_release_launch_description.txt
  abf2ab559d43110f1ff88cb0a7b815015f376aba7f73877ab6b240c0c7a0bf16
```

Both expose the v8.1 opt-in parameter and bind the exact counted-source,
no-affine, no-recenter, no-bounds, `exit_sigma=8.0`, and
`escape_max_sec=35.0` arguments.

Direct installed construction checks:

```text
supervisor:
  expected bounded timeout 124
  no startup error
  counted source count two
  one fill
  bounds/recenter/guidance/recoverable navigation disabled
  open-field escape assist enabled

Gaussian fill:
  expected bounded timeout 124
  no startup error
  exit_sigma 8.0
```

The timeout codes are expected because both are long-running ROS nodes and the
outer qualification command stopped them after five seconds.

Installed dry-run evidence:

```text
/tmp/phase08_8_1_release_primary_probe_dry.yaml
  1 resolved, 0 unsupported
  aff377a9c3c48044eca30379b0308bedcc119905707b9045b5fd5c08a2ae774f

/tmp/phase08_8_1_release_primary_repeats_dry.yaml
  10 resolved, 0 unsupported
  d6d5eec0d5d7c936026cd047b5f733dff8da8ed8278550905a8335bbefe28514

/tmp/phase08_8_1_release_secondary_probe_dry.yaml
  1 resolved, 0 unsupported
  4408c7f5b23bdaee8a562e106d63faaf0fc796a6062bcfe6edf9605d7d21d048

/tmp/phase08_8_1_release_secondary_repeats_dry.yaml
  5 resolved, 0 unsupported
  80931f0077ae69e88f66b0da019efdaa2b9b2518962846e398921a574eea447d
```

Dry-run resolution created none of the four declared campaign roots.

## Historical preservation

No historical scenario or world changed. Retained hashes remain:

```text
gazebo_empty.world:
  3085542f9dc1d13fdf9368a24808a226908d1a2c5a7a4ffd07bc6f374ca14b43

gesc_gaussian_validation.world:
  8ecc1a231efec24401d74fef3cd5139d48c6029f88e71d044cefdf2fd14c5bef

gesc_gaussian_corner_origin_validation.world:
  88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf

phase_08_v6_selection.json:
  dcdbf937fe3de0cab9449c2b01af79fd938e1d3f9791b4897937875d0747590d
```

The fixed v8 scenarios are also untouched. V6 and every historical profile
remain selectable and retain their recorded result status.

## Bounded qualification corrections

- One first test invocation used the wrong generated-interface Python path and
  stopped during collection. The corrected isolated environment passed.
- One pre-final broad invocation used ROS domain 233, above the DDS-supported
  maximum 232, and stopped before completing the test suite. The unchanged
  suite passed on valid domain 229, and the final retained JUnit suite passed
  on domain 222.
- One synthetic new assist test initially supplied state-machine timestamps
  older than the node's construction clock. The fixture now uses the node's
  clock and passes.
- One existing asynchronous adapter test observed `GOAL_HOLD` just before its
  subscribed `GOAL_REACHED` message arrived. Its fixture now waits for both
  independently required observations.
- An early parity command omitted the installed `ros_esc/` package directory.
  The corrected parity command and final from-scratch build pass `9/9`.

These are no-Gazebo environment/test-fixture corrections. No product gate was
weakened and no failed simulation was retried.

## Pre-dispatch boundary

At qualification close:

- no Gazebo server/client or scenario process is active;
- no v8.1 run root exists;
- all 17 v8.1 expansions are frozen and installed;
- source positions and evaluator geometry occur only in the runner/evidence
  contract, never in controller arguments;
- the simulator's `0.50 m` stop still requires a controller-ranked second
  candidate first;
- the physical controller still has no coordinate-distance termination and
  remains operator-terminated with `Ctrl+C`;
- no wall, collision, or obstacle-avoidance claim is introduced;
- the next allowed runtime action is exactly one visible execution of
  `phase08_v8_1_primary_visible_probe.yaml`, after checkpoint and commit.
