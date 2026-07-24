# Phase 07.5 Handoff

## Objective completed

Implemented and proved the simulation-only prerequisite required by the saved
Phase 08 plan: schema-version-2 validation scenarios can use deterministic
Gaussian noise, ROS-time sensor and pose delays, a bounded four-wall world,
and real Gazebo contact evidence. All controls are default off, schema version
1 retains its prior parsing and deterministic case identity, and no physical
hardware was run.

This is implementation/readiness evidence only. It does not establish Phase 08
robustness acceptance or authorize a simulation-ready tag.

## Context and repository state

- Branch: `feature/gesc-gaussian-robustness-v1`.
- Starting HEAD: `8c85d8c` (`phase 08: add robustness validation plan`).
- Required pre-edit result: `Phase 08 implement context is complete.`
- The saved Phase 08 plan, package specification, Level A/B/C policy, five
  repository maps/audits, knowledge bridge, and every prior handoff through
  Phase 07 and Phase 05.5 were verified before editing.
- The Phase 08 context validator now requires this handoff during
  implementation.
- Evidence root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08/prerequisite`.

## Existing owners extended

- `run_scenario` remains the only simulation suite orchestrator and continues
  to compose the existing `record_run`, `validate_run`, and
  `gazebo.launch.xml` owners.
- `analyze_run` remains the only per-run bag analyzer.
- The existing cost noise owner now uses the configured Gaussian seed in the
  generator that actually samples noise; unseeded legacy behavior is
  unchanged.
- The existing robot description owns opt-in Gazebo contact sensors.
- One new simulation-only node owns delayed test-input publication and the
  contact positive-control spawn. It owns no control, algorithm state,
  recorder, validator, or physical behavior.

No custom message, public algorithm topic, cost sign, unit, controller owner,
source semantics, Heavy-Ball behavior, or legacy default changed.

## Interfaces and behavior

Schema version 2 adds validation-world, contact, delay, and frozen-profile
fields. Schema version 1 rejects those fields and retains the Phase 06 smoke
case key beginning `f562307ac8`.

The new optional simulation topics are:

| Topic | Type |
|---|---|
| `/gesc_gaussian/simulation/raw_cost_delayed` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` |
| `/gesc_gaussian/simulation/source_cost_delayed` | `ros_esc_interfaces/msg/CostBreakdown` |
| `/gesc_gaussian/simulation/pose_delayed` | `nav_msgs/msg/Odometry` |
| `/gesc_gaussian/simulation/contacts` | `gazebo_msgs/msg/ContactsState` |

Algorithm consumers alone are routed to delayed topics. Messages retain their
original stamps and are released against `/clock`; canonical publishers remain
recorded. Phase 07 delay metrics map paired bag receipt stamps through recorded
simulation clock, and collision metrics distinguish valid empty evidence from
non-ground contacts.

The four-wall world bounds `[-2, 2] x [-2, 2] m`. The contact positive control
spawns a static physical Gazebo collision after recording readiness. It does
not publish synthetic `ContactsState` data.

## Exact files

Created:

- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/simulation_disturbance_node.py`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_validation_support.yaml`
- `ros2_ws/src/ros_esc/test/test_simulation_disturbances.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/worlds/gesc_gaussian_validation.world`
- `docs/codex/gesc_gaussian/handoffs/phase_07_5_handoff.md`

Updated:

- `DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh`
- `ros2_ws/src/ros_esc/package.xml`
- `ros2_ws/src/ros_esc/setup.py`
- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/noise_objects.py`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py`
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py`
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/topic_manifest.yaml`
- `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py`
- `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_node_script.py`
- `ros2_ws/src/ros_esc/test/test_scenario_schema.py`
- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/robot_description.launch.py`
- `ros2_ws/src/turtlebot3_rotating_sensor/urdf/turtlebot3_rotating_sensor.urdf`
- `docs/codex/gesc_gaussian/recording_runs.md`
- `docs/codex/gesc_gaussian/topic_dictionary.md`
- `docs/codex/gesc_gaussian/test_commands.md`

The source/config/test/documentation split exceeds ten files because collision
truth, a physical validation world, delayed inputs, schema compatibility,
recording, analysis, launch plumbing, and durable evidence have separate
existing owners. This coherent prerequisite is checkpointed separately from
the Phase 08 harness, freeze, and final evidence as required by the saved plan.

## Bounded Level B corrections

Three runtime corrections were required without weakening an acceptance gate:

1. Gazebo fixed-joint lumping changes the base and rotating-frame collision
   names during URDF-to-SDF conversion. The contact sensors now reference the
   exact generated names. A focused regression asserts both strings.
2. One otherwise complete negative-contact run reported the rotating-frame
   process exiting with status 245 during recorder SIGINT shutdown. That legacy
   node now uses the same explicit executor and `SignalHandlerOptions.NO`
   teardown already established for the controller, cost, supervisor, and PDE
   history owners. The existing shutdown regression covers it.
3. Initial delay analysis used wall-clock bag receipt deltas and reported about
   60 ms because headless Gazebo ran faster than real time. The metric now maps
   paired receipts through recorded `/clock`; both configured 100 ms delays
   report 0.100 s in simulation time.

Failed diagnostic runs remain preserved under the evidence root. No failed
run was relabeled or deleted.

## Runtime evidence

Accepted runs:

| Probe | Run suffix | Recording/cleanup | Key metric |
|---|---|---|---|
| contact positive | `bdb7e4c828_88b20a0e` | pass/pass | collision `true`, valid |
| contact negative | `925907a927_679a425c` | pass/pass | collision `false`, valid |
| seeded Gaussian | `8f9764f2cb_27549de2` | pass/pass | collision `false`, seed `8003` retained |
| sensor delay | `3c1c885dad_49ca6486` | pass/pass | raw/source delay `0.100 s`, valid |
| pose delay | `b65df4d2f3_6e7657a5` | pass/pass | pose delay `0.100 s`, valid |

Every accepted run has Phase 07 analysis status `complete`. The seeded cost
configuration retained `std_dev: 0.01` and `seed_num: 8003`. Unit evidence
also proves two Gaussian instances with one seed produce identical samples.

## Tests and checks

- Build: three packages passed.
- Pre-edit focused baseline: `153 passed, 2 skipped`.
- Final Phase 00-07.5 focused suite:
  `162 passed, 2 skipped in 7.90s`.
- Exact focused skips:
  - Phase 06 recorded headless Gazebo E2E requires
    `RUN_GESC_PHASE06_GAZEBO_E2E=1`;
  - Phase 05 visible Gazebo recording requires
    `DSIM_RUN_GAZEBO_RECORDING_TEST=1`.
- Support dry-run: five resolved runs, zero unsupported.
- Contact-enabled xacro, `check_urdf`, generated SDF collision references,
  XML/YAML parsing, launch `--show-args`, Python compile/import, focused
  flake8/pep257, fatal legacy lint, and `git diff --check`: passed.
- Global package result:
  `1031 tests, 0 errors, 856 inherited failures, 3 skipped`.
- Phase 07 documented global baseline:
  `1037 tests, 0 errors, 872 inherited failures, 3 skipped`.
- Trend: -6 generated test records, no new errors, -16 inherited lint
  failures, unchanged skips. New and clean touched files contribute no lint
  finding.

No physical test, Vicon test, 81-run training sweep, 12-run holdout, 519-run
full pass, or three-pass acceptance matrix has run in this subphase.

## Go/no-go

**GO for Phase 08 harness implementation and the fixed training sweep.**

**NO-GO for a parameter freeze, holdout claim, full-matrix claim,
simulation-ready tag, or physical execution until their later gates actually
run and pass.**

Recommended checkpoint commit:

```text
phase 07.5: add deterministic validation disturbances and collision evidence
```
