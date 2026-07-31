# Phase 08.8 M1-M2 no-Gazebo qualification

Date: 2026-07-30

## Result

**PASS — M1 and M2 are qualified for checkpoint and commit before the first
visible Gazebo probe.**

No Gazebo, scenario execution, recorder, rosbag recorder, analyzer, or physical
hardware process ran during this boundary. Installed dry-runs expanded
commands only, and `/tmp/phase08_8_installed_dryrun` remained absent.

The qualification implements the approved selectable counted-source
open-field profile while preserving V6, every historical scenario, legacy
behavior, cost sign/units, canonical topics, the sole controller `/cmd_vel`
publisher, recording final-zero, and cleanup contracts.

## Implemented controller contract

The existing supervisor now supports:

```text
extremum_classification_mode:
  absolute_source_score   # unchanged default
  counted_candidates      # Phase 08.8 opt-in
```

For counted candidates:

- `known_source_count=N` requires `N>=2`;
- `max_fill_clusters` must equal `N-1`;
- each candidate uses the minimum raw cost from each complete physical-sensor
  rotation;
- the default summary uses two rotation minima, their median, and a
  `3*MAD` uncertainty interval;
- the first `N-1` distinct candidates require exactly one accepted fill each,
  irrespective of the old absolute goal-score threshold;
- a confirmed center associated with an active fill is treated as a revisit;
- no additional fill can be accepted after the count budget;
- the terminal candidate is accepted only when its raw-cost upper bound is
  strictly below every retained filled-candidate lower bound;
- ambiguous or higher candidates return to `SEARCH` without a false global
  declaration.

The existing detector now has a default-compatible
`crossing_count|qualified_dwell` selector. Qualified dwell accumulates only
while the existing robust motion and state gates are satisfied, pauses in the
hysteresis band, rearms only beyond the exit threshold, resets on invalid
evidence/search boundaries/backward time, and emits at most one confirmation
per episode.

The new `operating_bounds_enabled=false` path does not instantiate or enforce
virtual room bounds. The fixed Phase 08.8 profile also disables recenter,
recoverable navigation, post-recovery guidance, and affine bias, yielding:

```text
SEARCH
-> VERIFY_EXTREMUM
-> DESIGN_OR_MERGE_FILL
-> ESCAPE_REPULSE
-> SEARCH
```

Invalid/stale pose or sensor data, explicit stop, controller watchdog,
fill-design timeout, final-zero, and shutdown behavior remain active.

## Raw and augmented data separation

The selected graph preserves these roles:

```text
CostBreakdown.raw_cost:
  rotation-stable candidate characterization and ranking

/pde_cost_history:
  raw basin estimation and adaptive fill design

typed Gaussian fills:
  recovered-basin identity and spatial revisit memory

/cost_modified:
  raw plus active Gaussian cost used by ordinary GESC motion
```

Declared light coordinates and roles are present only in simulator and
evaluation records. The supervisor receives onboard cost/score, the existing
relative odometry stream, typed fills, state/events, and the integer total
source count. It receives no global coordinate or evaluator proximity.

## Simulation-only terminal evidence

A schema-v8 run may be stopped early only after:

1. a valid post-recovery `GOAL_REACHED` event reports candidate ordinal `N`,
   `N-1` filled candidates, the known total `N`, and a positive strict
   raw-cost interval separation; and
2. a later, finite, noninterpolated simulator odometry sample is within
   `0.50 m` of the evaluator-only declared global.

Offline validation enforces the same ordering by bag timestamp. Proximity
alone cannot pass. The supervisor and physical launch receive no coordinate
stop; later physical operation remains manual and continues until the operator
presses `Ctrl+C`.

## Fixed installed scenarios

The initial draft used provisional `phase08_v8_counted_*` filenames. The
approved geometry, seeds, and contract are installed under the following
shorter names, now recorded in the amended Plan:

```text
phase08_v8_primary_visible_probe.yaml
phase08_v8_primary_repeats.yaml
phase08_v8_secondary_visible_probe.yaml
phase08_v8_secondary_repeats.yaml
```

Their source SHA-256 values are:

```text
aab76b1dea9e7284f0943e56e9620592bbafdb5fe810375447be73e337da6416
  phase08_v8_primary_visible_probe.yaml
17e6c89772c93986b6147711722847afdef7aa518fbafbff3ef6fd942ad568a8
  phase08_v8_primary_repeats.yaml
557ede2e6961438d18b309bb886d97cfdd376d236624dc4531e6fb3d0c5d1edc
  phase08_v8_secondary_visible_probe.yaml
07a0fb79fbcdbf08160b05d07d5ef9e629170d68ab6ff478d5a80a7188b983ae
  phase08_v8_secondary_repeats.yaml
```

Installed dry-runs resolved all 17 planned invocations and no unsupported
case:

| Scenario | Mode | Runs | Unsupported | Dry-run SHA-256 |
|---|---|---:|---:|---|
| primary visible | GUI | 1 | 0 | `9989a98f183d9e9eb5a54ff435a9804c128c2abe4ee53c95938487e7108f768a` |
| primary repeats | headless | 10 | 0 | `2032952c9fe4e1176a14a83512f25408cee575aeebbccb341e31a19f5e9a0c80` |
| secondary visible | GUI | 1 | 0 | `cfdd15b094db0060b7fd4b47d6f8faa41dc3f2001cc6d0cc1f20fcd92d35563d` |
| secondary repeats | headless | 5 | 0 | `0d162232768636b7af1a28f3af83ccbfa314aee5a3d2884b4e0954109332c4e3` |

Every expansion selects two lights, known count two, one maximum fill,
qualified dwell, direct open-field recovery, no contacts, no validation
walls, a 540-second finite run, a 720-second wall bound, and a simulation-only
ranked-goal-plus-`0.50 m` stop.

## Focused and broad tests

The exact Plan-focused controller/detector set:

```text
timeout 300s python3 -m pytest -q
  test_state_machine.py
  test_convergence_detector_policy.py
  test_supervisor_integration.py
  test_robust_gaussian_algorithm.py
  test_legacy_behavior.py

180 passed in 7.32 s
JUnit: /tmp/phase08_8_focused.xml
SHA-256:
1b320fc0019de2507e9b7df8c92999cb80676c850bfc16a209f0e9fb9ce975a9
```

The scenario/schema/Phase 08 validation set:

```text
380 passed, 1 skipped in 92.54 s
JUnit: /tmp/phase08_8_scenario.xml
SHA-256:
8381c68352cfaa5d79a9f46fbfe73edfee6808448df0d2db4309e91ea6475783
```

The skip is the explicit Gazebo integration, disabled at this no-Gazebo
boundary.

The candidate-table/plot unit set:

```text
13 passed in 0.75 s
JUnit: /tmp/phase08_8_analysis.xml
SHA-256:
e6779c129061878f03d312b435339b969160715fdde03869bd8e6ccdad580cc9
```

The complete ROS-independent functional regression, excluding the repository's
separate style/copyright test files:

```text
735 passed, 2 skipped in 134.05 s
JUnit: /tmp/phase08_8_broad.xml
SHA-256:
9e0211b741f86993bfa1eab403774733c54c6fdb037b7c2982d7a6861cf27599
```

The unchanged skips are environment-conditional Gazebo integrations.

Fatal changed-file Python lint (`E9,F63,F7,F82`), changed-Python compilation,
YAML resolution, launch XML parsing, `git diff --check`, and
`validate_phase_context.sh 08 implement` pass.

The repository-wide style test files were also attempted. They report 14,397
legacy flake8 findings and 1,842 legacy pep257 findings in the existing
math-simulation code; copyright is environment-skipped. Those pre-existing,
non-gating repository debts are not Phase 08.8 behavioral failures. Fatal
syntax/name errors in every changed Python file are zero.

## Fresh isolated build and installed graph

The final clean isolated build used:

```text
timeout 900s colcon
  --log-base /tmp/phase08_8_qual_final/log
  build --base-paths ros2_ws/src
  --build-base /tmp/phase08_8_qual_final/build
  --install-base /tmp/phase08_8_qual_final/install
  --packages-select
    ros_esc_interfaces ros_esc turtlebot3_rotating_sensor

Summary: 3 packages finished in 13.0 s
```

Source/install byte parity passes for 12/12 final owners: seven Python
implementation owners, four fixed scenarios, and the central Gazebo launch.

Installed nonexecuting launch checks:

```text
/tmp/phase08_8_show_args.txt
e6785a2e39a902f5c4d45fa5cfaa2257f2f24d5762372bced3702ca7e03ec530

/tmp/phase08_8_launch_description.txt
abc182d208745038f147a2408451f8756da673263ad1ef6e8675d80600f3985f
```

The launch description instantiated the exact counted/open-field arguments.
`--show-args` exposes all nine new public arguments. Direct installed node
instantiation kept both nodes alive for the bounded five-second check:

```text
detector:   timeout 124, clean startup log, qualified-dwell policy reported
supervisor: timeout 124, no startup error
```

A timeout status is expected because these are long-running ROS nodes; the
outer command intentionally interrupted them after successful construction.

## Historical preservation

No tracked historical scenario or world is modified. Retained hashes:

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

One latent V4 validation assertion previously treated every later scenario
filename as historical drift. It is now correctly scoped to the filenames
sealed in the V4 commitment itself. The committed V4 hashes and population are
unchanged; the formerly latent test now passes when V8 files are present.

`setup.py` was corrected to install `phase08_v8_*` scenarios. This was caught
by source/install parity before any simulation dispatch.

## Bounded qualification corrections

- The first context recheck used a nonexistent repository-root `tools/` path.
  The package-qualified
  `DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/` path passed.
- An early direct detector instantiation selected ROS domain 241, above the
  DDS-supported maximum 232. Domain 218 passed.
- An early launch-description invocation placed ROS arguments after
  `--print-description`. The corrected arguments-before-option form passed.
- One adapter test initially replaced rather than extended `PYTHONPATH`; the
  corrected source-precedence environment passed.
- One synthetic adapter history was too short for its declared interval and
  was extended from 0.20 to 0.35 seconds; no product threshold changed.
- Initial schema/live-stop fixtures omitted required counted evidence. The
  fixtures were corrected to exercise the intended strict contract.

These stopped before Gazebo and are qualification-command or test-fixture
corrections, not retained simulation attempts.

## Pre-dispatch boundary

At qualification close:

- no Gazebo, scenario runner, recorder, rosbag recorder, analyzer, or physical
  process is active;
- the dry-run root is absent;
- the physical controller has no coordinate-distance termination;
- no controller source-position, role, Vicon, room-map, or evaluator input was
  introduced;
- no second `/cmd_vel` publisher was introduced;
- all historical scenarios remain selectable;
- the exact primary visible scenario is the next permitted action only after a
  material Phase 08 checkpoint and bounded Git commit.
