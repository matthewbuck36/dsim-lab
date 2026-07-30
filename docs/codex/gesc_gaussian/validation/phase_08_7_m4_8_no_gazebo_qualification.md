# Phase 08.7 M4.8 no-Gazebo qualification

## Result

**PASS — the exact 17-case retained-success reproduction campaign is
qualified for serial Gazebo dispatch.**

Qualification completed against Git commit
`426f82b11f23290f2c44bb48c7bf3b9b323ff91c`. No algorithm, launch,
scenario, world, controller, recorder, validator, or historical evidence
file changed. The only M4.8 additions before dispatch are the reviewed plan
amendment, live-status record, and machine-readable dispatch manifest.

No Gazebo, scenario-runner execution, recorder, rosbag recorder, analyzer,
or physical-hardware process ran during qualification. Dry-runs expanded
commands only. The fresh campaign root remains absent:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_v7_success_reproduction_1
```

## Fixed authority and artifacts

The campaign is governed by:

```text
docs/codex/gesc_gaussian/plans/phase_08_7_plan.md
SHA-256
22b63bf0fff114b65b351f573139173ec0d85967704d6fb5d9da3781e215cece

docs/codex/gesc_gaussian/validation/
  phase_08_7_m4_8_success_reproduction_manifest.json
SHA-256
69d946c64718fdc725485fdffe5d41878b72825341d17f50777dddef3e13cc1f
```

The manifest resolves eight serial invocations and exactly 17 unique
historical case definitions. All use fixed start `(0,0)`, global
`(3.5,3.5)`, local/global simulator-relative inputs `400/1600`, one
declared local, one declared global, maximum one fill, and
`collision_expected=false`. M3 retains its original `1.00 m` primary
Stage B boundary. The other 16 cases retain `1.20 m`.

The proximity cancellation monitor is simulation-only. The user explicitly
requires future physical testing to have no automatic `1.20 m`, `1.00 m`,
or other distance stop. Physical operation must continue until the operator
judges the robot sufficiently close and presses `Ctrl+C`; distance remains
diagnostic only. The current owner separation supports that requirement:
`run_scenario` hard-codes `record_run --mode simulation` and exposes no
physical mode.

## Original evidence binding

Read-only discovery found exactly one retained original
`scenario_result.yaml` for every selected case and no duplicate. All 17
case keys equal the manifest. All 17 original runs passed Stage A, exact
fill cardinality, Stage B, collision expectation, forbidden-state/event,
and cleanup predicates. Fifteen were formal combined passes; M4 and M4.2
were behavioral passes whose original recording evidence failed. Those two
historical formal failures remain failed and immutable.

Original evidence roots:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m2_3
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m3
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_probe
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_2_probe
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3_probe
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_3
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4_probe
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v7_m4_4
```

The exact original run IDs are:

| Case | Original run ID | Original disposition |
|---|---|---|
| `v7_m2_3_diagonal_r1p5_h25_18001` | `20260730T005434366368Z_simulation_phase08_v7_m2_3_assisted_recovery_stop_probe-v7_m2_3_diagonal_r1p5_h25_18001-rob_fe3286c1` | formal pass |
| `v7_m3_r1p0_a45_h25_18101` | `20260730T025330587588Z_simulation_phase08_v7_m3_spatial_suite-v7_m3_r1p0_a45_h25_18101-robust_gaussian_v1-75d0c27b_c2f44d09` | formal pass |
| `v7_m4_probe_r1p5_a45_h25_18201` | `20260730T054527662523Z_simulation_phase08_v7_m4_visible_probe-v7_m4_probe_r1p5_a45_h25_18201-robust_gaussian_v1-a7_e99d857b` | behavior pass / evidence fail |
| `v7_m4_2_probe_r1p5_a45_h25_18208` | `20260730T081058251159Z_simulation_phase08_v7_m4_2_visible_probe-v7_m4_2_probe_r1p5_a45_h25_18208-robust_gaussian_v_56b72dfe` | behavior pass / evidence fail |
| `v7_m4_3_probe_r1p5_a45_h25_18308` | `20260730T085116266752Z_simulation_phase08_v7_m4_3_visible_probe-v7_m4_3_probe_r1p5_a45_h25_18308-robust_gaussian_v_91c59c52` | formal pass |
| `v7_m4_3_r1p5_a45_h25_18309` | `20260730T091551844993Z_simulation_phase08_v7_m4_3_two_light_suite-v7_m4_3_r1p5_a45_h25_18309-robust_gaussian_v1-89_75b50f64` | formal pass |
| `v7_m4_3_r1p5_a67p5_h25_18309` | `20260730T092034201319Z_simulation_phase08_v7_m4_3_two_light_suite-v7_m4_3_r1p5_a67p5_h25_18309-robust_gaussian_v1-_968012f5` | formal pass |
| `v7_m4_3_r2p0_a45_h25_18309` | `20260730T092348439805Z_simulation_phase08_v7_m4_3_two_light_suite-v7_m4_3_r2p0_a45_h25_18309-robust_gaussian_v1-71_e099d4ea` | formal pass |
| `v7_m4_3_repeat_r1p5_a45_h25_18310` | `20260730T092756923876Z_simulation_phase08_v7_m4_3_two_light_suite-v7_m4_3_repeat_r1p5_a45_h25_18310-robust_gaussia_5656cae0` | formal pass |
| `v7_m4_3_repeat_r1p5_a45_h25_18311` | `20260730T093256378999Z_simulation_phase08_v7_m4_3_two_light_suite-v7_m4_3_repeat_r1p5_a45_h25_18311-robust_gaussia_6953e120` | formal pass |
| `v7_m4_3_repeat_r1p5_a45_h25_18312` | `20260730T093715858897Z_simulation_phase08_v7_m4_3_two_light_suite-v7_m4_3_repeat_r1p5_a45_h25_18312-robust_gaussia_26702e74` | formal pass |
| `v7_m4_4_probe_r1p5_a45_h25_18408` | `20260730T104556725279Z_simulation_phase08_v7_m4_4_visible_probe-v7_m4_4_probe_r1p5_a45_h25_18408-robust_gaussian_v_86533a18` | formal pass |
| `v7_m4_4_r1p0_a45_h25_18409` | `20260730T105520880193Z_simulation_phase08_v7_m4_4_two_light_suite-v7_m4_4_r1p0_a45_h25_18409-robust_gaussian_v1-69_ad44f391` | formal pass |
| `v7_m4_4_r1p5_a45_h25_18409` | `20260730T105936555786Z_simulation_phase08_v7_m4_4_two_light_suite-v7_m4_4_r1p5_a45_h25_18409-robust_gaussian_v1-ca_80fbb930` | formal pass |
| `v7_m4_4_r1p5_a67p5_h25_18409` | `20260730T110632219249Z_simulation_phase08_v7_m4_4_two_light_suite-v7_m4_4_r1p5_a67p5_h25_18409-robust_gaussian_v1-_372ea556` | formal pass |
| `v7_m4_4_repeat_r1p5_a45_h25_18411` | `20260730T112643925666Z_simulation_phase08_v7_m4_4_two_light_suite-v7_m4_4_repeat_r1p5_a45_h25_18411-robust_gaussia_21eeeeae` | formal pass |
| `v7_m4_4_repeat_r1p5_a45_h25_18412` | `20260730T113225097653Z_simulation_phase08_v7_m4_4_two_light_suite-v7_m4_4_repeat_r1p5_a45_h25_18412-robust_gaussia_02ffd2fb` | formal pass |

## Regression evidence

The focused helper, supervisor, state-machine, scenario-schema/runner,
observability, recorder/validator, final-zero, and controller-spawner
envelope ran from `ros2_ws/src/ros_esc` against the current source over the
last qualified ROS overlay:

```text
timeout --signal=INT --kill-after=20s 300s python3 -m pytest -q \
  test_escape_recenter.py test_state_machine.py \
  test_supervisor_integration.py test_scenario_schema.py \
  test_scenario_runner.py test_observability_contract.py \
  test_experiment_recording.py test_controller_spawner_recovery.py \
  --junitxml=/tmp/phase08_7_m4_8_focused.xml

405 passed, 1 skipped in 56.28 s
JUnit SHA-256:
c1d87e369d3e32d8e6ec46ae084cd7fb9d452cf1adba58c0c47ded0602907157
```

The skip is the explicit opt-in recorded headless Gazebo integration. It
remained disabled because this boundary prohibits Gazebo.

The broad ROS-independent functional envelope:

```text
timeout --signal=INT --kill-after=20s 300s python3 -m pytest -q \
  ros2_ws/src/ros_esc/test \
  --ignore=ros2_ws/src/ros_esc/test/test_flake8.py \
  --ignore=ros2_ws/src/ros_esc/test/test_pep257.py \
  -k 'not v4_population_adoption_is_exact_and_unused' \
  --junitxml=/tmp/phase08_7_m4_8_broad_functional.xml

684 passed, 3 skipped, 1 deselected in 118.88 s
JUnit SHA-256:
3e5436b35d27006e4c3f64778f6d024697e1e3d27cf41ea6c6c200c03fbe824c
```

The skips are the generated-source copyright check and the two explicit
Gazebo integrations. The deselection is the documented retired V4
population-adoption assertion.

Fatal Python lint (`E9,F63,F7,F82`), Python compilation, all eight YAML
loads, dispatch-manifest JSON validation, launch XML parsing,
`git diff --check`, and
`validate_phase_context.sh 08 implement` pass. These checks retain V6,
legacy behavior, every historical scenario, the shifted world, known fill
cardinality, staged local-recovery reporting, the simulation-only global
stop, recording, final zero, and cleanup.

## Isolated build and installed graph

The fresh build used:

```text
timeout --signal=INT --kill-after=30s 300s colcon \
  --log-base /tmp/phase08_7_success_reproduction_qual/log build \
  --base-paths ros2_ws/src \
  --build-base /tmp/phase08_7_success_reproduction_qual/build \
  --install-base /tmp/phase08_7_success_reproduction_qual/install \
  --packages-select ros_esc_interfaces ros_esc \
    turtlebot3_rotating_sensor \
  --event-handlers console_direct+

Summary: 3 packages finished [12.0 s]
```

Source/install byte parity passes for 22 owner pairs: the schema, runner,
Phase 08 validator, recorder, completeness validator, supervisor node,
recovery helper, state machine, all eight selected scenarios, central
Gazebo launch, empty-world launch, control launch, robot-description
launch, idempotent controller-spawner helper, and shifted validation world.

Installed nonexecuting launch checks passed:

```text
central --show-args:
  4b44f244b0d3089b9675d9f6cd3bb597b7f87f668fbfab4b90015987e3ad8ade
central --print-description:
  603aa80d54c86444eed19e39039ff77fa8ce01e4e4428a18f100e7e67cfa2b2a
control recovery false --print-description:
  042ad66a28bd19117be32c9fb19428057dcd1ba45a0cfbd00b1a44c29eb4bf8a
control recovery true --print-description:
  7935611197c61c6bda1eea9fa2118e89f0da53a28de8fd2a3456daa279425bde
```

The final hash above was independently checked from captured output; no
launch process was executed.

## Installed dry-runs

All dry-runs used the isolated install, operator `phase08_7_m4_8`, the
fresh child roots, exact selected case IDs, and their declared GUI/headless
modes. They resolve zero unsupported cases:

| Invocation | Domain | Mode | Cases | Dry-run artifact SHA-256 |
|---|---:|---|---:|---|
| `m2_3` | 168 | visible | 1 | `bed83aa7e6042fea5238f23c0753ae388d205c044568b3825638a9a40c9d2015` |
| `m3` | 169 | headless | 1 | `ca8acbcce4241eef884b97eedb9345ec9d0ad9825b3d8fb59c670fc6c0943b21` |
| `m4` | 170 | visible | 1 | `eedf469aa68a943533cf90986fdd11f3f0e1eefeb0a5a6fb5355832f656745bc` |
| `m4_2` | 171 | visible | 1 | `f922f06872baf6c6f962dc02c1fa48095b0bf2d85f09108182cb97c4ee6d5217` |
| `m4_3_probe` | 172 | visible | 1 | `f28f124a19f77f672f7b1a8df7591c7a2e5f1f6aea0f4ac0b9a8a2d64dccd9ab` |
| `m4_3_suite` | 173 | headless | 6 | `64b01a5d0502980d56ea8d86c01d17005e3a15e0000015838bb818627e57ade9` |
| `m4_4_probe` | 174 | visible | 1 | `285957b1cc1f3f70102a807ab9c30a00d44faaa8302f217350b5f575f2cde103` |
| `m4_4_suite` | 175 | headless | 5 | `8ef6014b717ae3afe97f42fb37ff02496a2b31705afcc9649ce41d200b087747` |

Every dry-run record command contains `--mode simulation`, the expected
fresh child root, exact case key and seed, and the declared stop radius.
The five historical standalone probes remain visible; the M3 and suite
invocations remain headless. The campaign root remained absent after all
eight expansions.

## Bounded qualification corrections

No correction below started Gazebo or changed a product artifact:

- The first focused-test command sourced only base ROS, so collection
  stopped before tests because generated `ros_esc_interfaces` was absent.
  The current qualified overlay was sourced and the complete focused set
  passed.
- The first manifest helper unpacked an internal expansion return value
  incorrectly. The verifier was corrected and proved eight dispatches and
  17 exact cases.
- One combined syntax-check shell enabled unset-variable errors before
  sourcing ROS; the next named an obsolete launch filename. Sourcing first
  and resolving the current XML owners produced the passing final check.
- The first remaining-dry-run loop lost quoted dictionary keys inside a
  nested shell string and raised `NameError` before invoking a runner.
  The corrected bounded loop produced all seven remaining dry-run
  summaries. The separately executed M2.3 dry-run had already passed.

These are qualification-command errors, not ROS, algorithm, recording, or
simulation failures.

## Pre-dispatch boundary

At qualification close:

- the campaign root and all eight child roots are absent;
- `/tmp/.X11-unix/X0` exists for the five visible invocations;
- no matching Gazebo, scenario runner, recorder, rosbag recorder, or
  analyzer process is active;
- original failed and successful evidence remains unchanged;
- no automatic-retry path exists;
- no three-light, Phase 09 implementation, physical command, or hardware
  command occurred.

The next permitted action is to update the live status, checkpoint Phase 08,
inspect the exact diff, and commit this qualification boundary. Gazebo must
remain closed until that commit exists. Afterward, execute all eight
invocations serially, retain every outcome once, and stop later dispatch
only for cleanup/evidence corruption/source-drift conditions declared in
the M4.8 plan.
