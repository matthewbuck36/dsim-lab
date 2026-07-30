# Phase 08.7 M4.6 no-Gazebo qualification

Date: 2026-07-30
Result: PASS
Gazebo processes started: none

## Scope and authorization

The user explicitly approved M4.6 implementation. This boundary implements
only the reviewed evidence calibration:

```text
post_recovery_source_reversal_dot_threshold: -0.80
```

The value is explicit only in the two fresh M4.6 inputs. The launch and
supervisor default remains `-0.90`; source continuity and controller-spawner
recovery remain default-off. No production source, launch file, world,
recorder, validator, controller, modified-cost node, M4.5 input, or
historical input changed.

Fresh inputs:

```text
ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v7_m4_6_visible_probe.yaml
  phase08_v7_m4_6_two_light_suite.yaml
```

SHA-256:

```text
deb08439f285a1bcff7e7b5fe763acbf095e7175d995367c626f9d83d7b30e11
  phase08_v7_m4_6_visible_probe.yaml
c005e2c921f588b1363c231df9c0562591ea9c42671a0c8a1470dcf233a537cf
  phase08_v7_m4_6_two_light_suite.yaml
```

## Exact calibration replay

The exact retained M4.5 geometry gives:

```text
anchor:                   (1.1809160175, 1.5969815630) m
source-led end:           (1.3563818523, 1.5646136279) m
fill center:              (1.8117325336, 1.7511796132) m
displacement:              0.1784262940 m
radial/source dot:        -0.8412123475
```

At `-0.90`, the pure detector returns no evidence. At explicit `-0.80`, it
returns evidence and the hard-safe forward-half-plane selector returns:

```text
direction:                (-0.1814078764, -0.9834079430)
source alignment:          0.0 within 1e-12
radial outward alignment:  0.5407048977
lookahead fill distance:   0.8707616102 m
bypass release radius:     0.7086747487 m
```

The full retained table was replayed. Both observed radius-2 reversals
(`-0.9999689709`, `-0.8412123478`) trigger at `-0.80`. Every retained pass,
including visible central `-0.336356` and repeat `18412` at `-0.192921`,
does not trigger. Repeat `18410` also remains outside the trigger.

Existing M4.5 tests continue to prove default-off radial fallback, exact
bypass release, one-recenter continuity, sub-`0.05 m` displacement,
nonfinite/undefined geometry, no safe candidate, room/collision/ownership
faults, and exhausted bounded recovery.

## Test evidence

Targeted M4.6 contract:

```text
timeout 180s python3 -m pytest -q \
  test_supervisor_integration.py::test_m4_6_exact_failed_geometry_uses_only_calibrated_threshold \
  test_supervisor_integration.py::test_m4_6_calibration_replays_retained_alignment_table \
  test_scenario_schema.py::test_m4_6_fixed_inputs_change_only_identity_seed_and_threshold \
  test_scenario_schema.py::test_m4_6_preserves_m4_5_m4_4_m4_3_v6_and_world_hashes \
  test_scenario_runner.py::test_m4_6_launch_changes_only_explicit_continuity_threshold \
  --junitxml=/tmp/phase08_7_m4_6_targeted.xml

14 passed in 1.10 s
JUnit SHA-256:
e974aa5ec9461b488de4d4c60b043bfb572a5c51fd9d099c69eb630e4b594581
```

Focused supervisor, state-machine, schema, runner, observability, recording,
and controller-startup regression:

```text
timeout --signal=INT --kill-after=20s 300s python3 -m pytest -q \
  test_escape_recenter.py test_state_machine.py \
  test_supervisor_integration.py test_scenario_schema.py \
  test_scenario_runner.py test_observability_contract.py \
  test_experiment_recording.py test_controller_spawner_recovery.py \
  --junitxml=/tmp/phase08_7_m4_6_focused.xml

390 passed, 1 skipped in 54.99 s
JUnit SHA-256:
de8fc93abeb31be8487957660bba7e7b3ce1c8670fa61f92e5ab582fd72195e5
```

Broad ROS-independent functional regression:

```text
timeout --signal=INT --kill-after=20s 300s python3 -m pytest -q \
  ros2_ws/src/ros_esc/test \
  --ignore=ros2_ws/src/ros_esc/test/test_flake8.py \
  --ignore=ros2_ws/src/ros_esc/test/test_pep257.py \
  -k 'not v4_population_adoption_is_exact_and_unused' \
  --junitxml=/tmp/phase08_7_m4_6_broad_functional.xml

669 passed, 3 skipped, 1 deselected in 116.43 s
JUnit SHA-256:
a87e9078549f9f66e1148c79526d340579650a012838c8f894a56601f7d5aa03
```

The skips are unchanged environment-conditional cases. The deselection is
the documented retired V4 population-adoption assertion. There were no
failures or errors.

Fatal changed-file lint (`E9,F63,F7,F82`), modified-Python compilation,
fresh YAML parsing, launch XML/Python parsing, and `git diff --check` pass.
`validate_phase_context.sh 08 implement` passes.

## Isolated build, install parity, and launch resolution

The fresh isolated build:

```text
timeout --signal=INT --kill-after=30s 300s colcon \
  --log-base /tmp/phase08_7_m4_6_qual/log build \
  --base-paths ros2_ws/src \
  --build-base /tmp/phase08_7_m4_6_qual/build \
  --install-base /tmp/phase08_7_m4_6_qual/install \
  --packages-select ros_esc_interfaces ros_esc \
    turtlebot3_rotating_sensor \
  --event-handlers console_direct+
```

passed all three packages in `11.8 s`.

Source/install byte parity passes for the supervisor helper/node,
schema/runner, both fresh scenarios, Gazebo launch, control launch, and
idempotent controller-spawner helper.

Installed nonexecuting launch artifacts:

```text
/tmp/phase08_7_m4_6_installed_launch_description.txt
SHA-256 29f07d82de15038d01d1ea00040e0ba1afe3eb0f572b80d8c3dd6c3985fded04
/tmp/phase08_7_m4_6_installed_control_description.txt
SHA-256 3d9ec1f85abd1c5ae9d95186d2a627f9a0cd1af9fdf9554a2a224909e1eb7f55
/tmp/phase08_7_m4_6_installed_show_args.txt
SHA-256 2b2b6a9e8affc9fdef9de4d4a3ca4626e0327aab464cb194a66d33de2d96c3
```

Installed defaults resolve to:

```text
gaussian_fill_max_fills:                       1
post_recovery_source_continuity_enabled:       False
post_recovery_source_reversal_dot_threshold:  -0.90
controller_spawner_load_recovery_enabled:      False
```

Direct installed `OpaqueFunction` resolution proves:

```text
recovery false:
  controller_manager/spawner joint_state_broadcaster, 30.0 s
  controller_manager/spawner velocity_controller, 30.0 s
recovery true:
  turtlebot3_rotating_sensor/idempotent_controller_spawner.py
  joint_state_broadcaster, velocity_controller, 30.0 s
```

## Installed dry-runs and fixed identities

Installed dry-runs resolve one visible and eight headless cases, with zero
unsupported cases:

```text
/tmp/phase08_7_m4_6_visible_installed_dry_run.yaml
SHA-256 4a33eada6b084435c0d44b3215fb5807b86af58783ff793631571c8109653d33
/tmp/phase08_7_m4_6_suite_installed_dry_run.yaml
SHA-256 4344ba59098cb96bae870a6a9b21806950134ca0852c57ab01b4d0537f0935ee
```

Every resolved case has explicit `-0.80`, source continuity enabled,
controller-load recovery enabled, `480 + 120 <= 600 s`, `780 s` wall bound,
one declared local, one declared global, maximum one fill, unchanged
`1.20 m` primary proximity, and unchanged non-gating `1.00 m` diagnostic.

Fixed case keys:

```text
0adae0a552ae5f715240dcc22d1478e710711e8e82429e6752daa7c45f6045a4
62fa7a7915cedc4dd3081c3a3e5764e22e1880e971e32c70a744d2afdbbe4d54
06764d07ea8620a20278594a03fcab28d14f90d6259a9290a658c1bbb2e8b5b5
2a66c20df5b62dcde548ec5e3a824fc435459f30f403851c2027f2dcf1d0ff35
89a1676db7d053a044d4a2e93c753a0d16ed598dd4870caa75beaee84209cdb6
d220251e34434435b41fa16cd63fb7c78508e331b4de71dac5c48f209927a906
de71b4594bd24790fd216cb7ceee74cb08ef5a4275f8a3acc49d26c94137251e
bd7613efe4ece2a6f44602aa15fee0d8187aaae167966a7c9c61941690dd836e
27dc48ef6bf727776b89d519bb41794e3eedaaf0271ad788ba3938643884c09b
```

The normalized M4.6 cases equal their M4.5 counterparts after removing only
fresh suite/case/contract identity, seed, repeat-reference key,
human-readable description, case key, and the explicit threshold. The
visible seed remains paired at `18508`; the suite uses the fixed fresh seeds
`18609..18612`.

## Sealed M4.5 and historical evidence

The immutable M4.5 evidence hashes still match:

```text
c4f7da06667aa57f21c87d51d5a9c3cd1188bd55010dfe94cd39cc7ee6105e99
  visible summary
5d39fbcbf68c720ca35eb86a8e8aa2669445a20e42c8ad531ccd7cd0e065fd47
  completeness
0256fbce2cb2a302c1d7681febc6f103317d867d6198942b3ab88ebea23694fc
  scenario result
dfa0765978f67a4c317edc8e088fe62d29971da0ffb93ec348d5b8ac858f63be
  bag database
197848518999cf2981007a1baa767ca8c33e0ae144f66a93d298c133ec6d0df7
  analysis completeness
caa56a51d65e75fe49721f15d35a89113765db6ee24b03a670955b5c901aa7c9
  summary metrics
cd8c96e30cfe56e748147f2b5c28bc29af9b2cb50b7760b07f0c496e350f71b5
  M4.5 report
```

Read-only SQLite validation remains:

```text
PRAGMA quick_check: ok
messages: 582137
topics: 34
```

M4.5 scenario hashes remain:

```text
3653a46c5a0ee4cf866cd257c6df2d9c18c745335f93b4fac400d0d51a313f97
  M4.5 visible
0eecc1337371ba75d8a6ae80e766415f8bdabe2a925d0034eaa2c6f2af34e384
  M4.5 two-light suite
```

M4.4, M4.3, V6, and the shifted validation world also match their committed
hashes through the focused and broad hash regressions.

## Non-gating diagnostic corrections

An initial pure replay imported the older default workspace install and
therefore could not find the M4.5 helper. The replay was rerun against source,
then the fresh isolated build and byte-parity checks proved the installed
artifact. An initial launch parsing command used two obsolete launch
filenames; the current launch owners were resolved and both XML and Python
launch parsing passed. Installed `Node` introspection required this ROS
release's private argument storage rather than a public `arguments`
attribute; normalized direct resolution then passed. None of these
path/introspection corrections started ROS or Gazebo or changed the
acceptance contract.

## Pre-dispatch boundary

At qualification close:

- both fresh evidence roots are absent;
- no Gazebo, scenario runner, recorder, rosbag, analyzer, or matching ROS
  launch process is active;
- the only implementation files are the two fresh scenarios and three
  focused test files;
- no suite, three-light, Phase 09, physical, or hardware action has started.

The next allowed action is to checkpoint and commit this no-Gazebo boundary,
then record and commit the exact fixed visible dispatch command. Only the one
visible paired case may run. The eight-case headless suite remains
passing-gated by that visible result.
