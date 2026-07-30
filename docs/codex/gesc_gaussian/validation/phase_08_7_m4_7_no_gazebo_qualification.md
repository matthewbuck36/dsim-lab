# Phase 08.7 M4.7 no-Gazebo qualification

Date: 2026-07-30
Result: PASS
Gazebo processes started: none

## Scope and authorization

The user explicitly approved M4.7 implementation. This boundary implements
only the reviewed default-off dynamic source-resume corridor. It extends the
existing supervisor, helper, schema, launch, and test owners and adds two
fresh fixed inputs:

```text
post_recovery_source_resume_enabled: false
post_recovery_source_resume_min_progress_m: 0.20

ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/
  phase08_v7_m4_7_visible_probe.yaml
  phase08_v7_m4_7_two_light_suite.yaml
```

The fresh inputs alone select `true`, `0.20`, and the retained M4.6
`post_recovery_source_reversal_dot_threshold=-0.80`. Their SHA-256 hashes
are:

```text
1da37b5cdb8158723a937969447806e4d5e9e12b8f458e72fbb5764a0cb237ca
  phase08_v7_m4_7_visible_probe.yaml
654b8fcb65fe565e340c4ee08250c036635bfb4e87a66ecbbc0654716c47f2f4
  phase08_v7_m4_7_two_light_suite.yaml
```

No global coordinate, source role, light identity, simulation truth, future
pose, or desired outcome is passed to the supervisor. M4.6 and all historical
inputs remain byte-identical and omit the new Boolean, preserving their
selector, fixed-clearance release, affine, liveness, and event behavior.

## Qualified behavior

The enabled corridor:

- retains the measured source-led displacement direction after the calibrated
  reversal detector arms;
- ranks only hard-safe forward-half-plane candidates by source alignment,
  clearance, absolute rotation, and deterministic candidate order;
- recomputes that selection on every new valid pose and increments the
  published revision only when the selection changes;
- changes fixed clearance from a guidance release into a source-resume anchor;
- measures signed odometry progress along the retained source direction;
- requires source progress `>=0.20 m`, live fill clearance, and the existing
  `0.60+0.50=1.10 m` outward/taper boundary before normal release;
- holds affine weight at `0.50` until source progress is acquired, then uses
  the existing spatial taper to zero;
- preserves the corridor and source direction through one bounded recenter,
  resetting the source-resume anchor after recenter so recenter translation is
  excluded;
- keeps liveness active after that recenter until normal completion or the
  existing `90.0 s` duration boundary;
- publishes finite corridor events and releases to ordinary GESC search,
  without a new failsafe, if the duration expires.

The unchanged hard-safe command sweep, stale/finite-data checks, physical-room
inset, fill avoidance, controller/graph ownership, explicit stop, collision,
final-zero, and cleanup contracts remain in force.

Exact retained geometry proves the source-specific selections:

```text
arm:                       -90 degrees
after 0.200 m tangent:     -45 degrees
after 0.425 m tangent:       0 degrees
generic M4.6 at 0.200 m:   -90 degrees
generic M4.6 at 0.425 m:   -90 degrees
```

A non-collinear supervisor regression separately proves that source-resume
recomputation uses the retained source direction rather than the fill-radial
direction.

## Test evidence

Formal targeted M4.7 contract:

```text
timeout --signal=INT --kill-after=20s 180s python3 -m pytest -q \
  test_escape_recenter.py test_supervisor_integration.py \
  test_scenario_schema.py test_scenario_runner.py \
  test_observability_contract.py \
  -k 'm4_7 or launch_file_declares_observability_defaults_and_wiring' \
  --junitxml=/tmp/phase08_7_m4_7_targeted.xml

15 passed, 275 deselected in 1.29 s
JUnit SHA-256:
0998bfad6e7666943772e61e27c4ea2e6d36eeea5cde4d83386cb26731808f29
```

Focused helper, supervisor, state-machine, schema, runner, observability,
recording, and controller-startup regression:

```text
timeout --signal=INT --kill-after=20s 300s python3 -m pytest -q \
  test_escape_recenter.py test_state_machine.py \
  test_supervisor_integration.py test_scenario_schema.py \
  test_scenario_runner.py test_observability_contract.py \
  test_experiment_recording.py test_controller_spawner_recovery.py \
  --junitxml=/tmp/phase08_7_m4_7_focused.xml

405 passed, 1 skipped in 53.98 s
JUnit SHA-256:
33b08592d7ea9c2cf63570e715f3d871e2dfbf5976763653cf4ebd948145a914
```

Broad ROS-independent functional regression:

```text
timeout --signal=INT --kill-after=20s 300s python3 -m pytest -q \
  ros2_ws/src/ros_esc/test \
  --ignore=ros2_ws/src/ros_esc/test/test_flake8.py \
  --ignore=ros2_ws/src/ros_esc/test/test_pep257.py \
  -k 'not v4_population_adoption_is_exact_and_unused' \
  --junitxml=/tmp/phase08_7_m4_7_broad_functional.xml

684 passed, 3 skipped, 1 deselected in 117.25 s
JUnit SHA-256:
8252faa82e50669c9c144da4de11449e1def6345940575cfb197541adb79ae70
```

The skips are unchanged environment-conditional cases. The deselection is
the documented retired V4 population-adoption assertion. Fatal changed-file
lint (`E9,F63,F7,F82`), modified-Python compilation, YAML/schema expansion,
launch XML parsing, `git diff --check`, and
`validate_phase_context.sh 08 implement` pass.

The focused and broad regressions also preserve historical normalized case
keys and hashes, cost sign/units, canonical topics, sole `/cmd_vel` ownership,
the existing explicit-stop path, nonfinite/stale-data handling, recording and
final-zero contracts, V6, and all historical scenarios.

## Isolated build, installed parity, and launch resolution

The fresh isolated three-package build:

```text
timeout --signal=INT --kill-after=30s 300s colcon \
  --log-base /tmp/phase08_7_m4_7_qual/log build \
  --base-paths ros2_ws/src \
  --build-base /tmp/phase08_7_m4_7_qual/build \
  --install-base /tmp/phase08_7_m4_7_qual/install \
  --packages-select ros_esc_interfaces ros_esc \
    turtlebot3_rotating_sensor \
  --event-handlers console_direct+
```

passed all three packages in `12.0 s`.

Source/install byte parity passes for the supervisor helper/node,
schema/runner, both fresh scenarios, Gazebo launch, control launch, and
idempotent controller-spawner helper.

Installed nonexecuting launch artifacts:

```text
/tmp/phase08_7_m4_7_installed_show_args.txt
  4bd1c6a62c06f0219ff320ffee7a6bb1188011ac42247e3934c6aef8c2b87e6d
/tmp/phase08_7_m4_7_installed_launch_description.txt
  9290d3c7656a787ebc1a42de00d917c10d0a5a9e6118601fd01894537659ec3d
/tmp/phase08_7_m4_7_installed_control_description.txt
  7c37142e2d48040c1951d8eac250ea68f35dd4966000cb096d332f5788f836b5
/tmp/phase08_7_m4_7_installed_control_resolution.txt
  086abce698f071dcdcde71ef88c1f6d7580804689eb54c2c320092f18f3de886
```

Installed defaults resolve to:

```text
gaussian_fill_max_fills:                       1
post_recovery_source_continuity_enabled:       False
post_recovery_source_resume_enabled:           False
post_recovery_source_resume_min_progress_m:    0.20
post_recovery_source_reversal_dot_threshold:  -0.90
controller_spawner_load_recovery_enabled:      False
```

Direct installed controller resolution proves the unchanged two-spawner path
when recovery is false and the single idempotent helper path when recovery is
true.

## Installed dry-runs and fixed identities

Installed-executable dry-runs resolve one visible and eight headless cases
with zero unsupported cases:

```text
/tmp/phase08_7_m4_7_visible_installed_dry_run.yaml
  f7c439366e5fefab3b16ed82e130be17de4bb623a51e71fe105f55dae9e3363d
/tmp/phase08_7_m4_7_suite_installed_dry_run.yaml
  b48fc12cb96ef52f289b939a971e8c58760c3a9181552f232b7253e925d4c2e9
```

Every resolved case has resume enabled at `0.20 m`, explicit `-0.80`
continuity, `480+120<=600 s`, a `780 s` wall bound, exactly one declared
local and global, maximum one fill, unchanged primary `1.20 m`
operator-equivalent global stop, unchanged non-gating `1.00 m` diagnostic,
collision expected false, final zero, and cleanup.

Fixed case keys:

```text
e48c200b54a7a9d9049b5965ef9c773b166e6672df155f0d9ccff459da83f3e8
d6b696af48a722e6427bca42ac04a862d50a6fa6689134b16278382326eca48b
bbbddb2f326b455b30db9fa90d5d1ca8cd8cc75d1b9d86c1a95fce581dfbcc87
382a4903d6128d43293ae583df072bd5f446f51fd0dc8ec76a7157f0fae9ef6b
1c225b8cf109a134d41818c2044ee7c6843bce69f4530bd8e821b0836fb4283a
8d98c2754cd8496fde985ac28a1f31178989e734c1021f1edfe20559df751c6d
386f6ccd6d1ddad5ad530e9cfe7a4083e66f3d9756d7f8e5fe97e8fe6fbfade6
65b61f3c8070f7cfb973424ed5aaf26e434c1dbe9761b3d7ad40d7f26b324781
593ecd33bb05cb90b065b2896707b3c1c3c2c2b858347a67cffb4c0503e9b33c
```

Normalized M4.7 cases equal their M4.6 counterparts after removing fresh
suite/case/contract identity, seed, description, case key, repeat-reference
key, and the two explicit source-resume fields.

## Sealed M4.6 and historical evidence

The immutable M4.6 visible failure remains:

```text
Stage A:                       PASS
one-fill cardinality:          PASS
complete 120 s Stage B:        PASS
primary 1.20 m proximity:      FAIL
best global distance:          2.6173470005 m
conditional headless suite:    NOT RUN
```

The M4.6 report and retained evidence hashes still match:

```text
b746f1083f006b20fed97e9a584ef480b615dac0126027683d21343d1cd6e93c
  visible summary
a095e8e1c6046b65cc2d1d45e9cf2ea48d864003f34a555ba4a70ad9e2c323cc
  completeness
fe3d5010c39282fdd104345a32680986cd0775d73a51c800ecb700fe7ec63aa2
  scenario result
d52be6874dec45810949689b8e0ab0635526cb334fd8f122e492d95ffea2080b
  bag database
36687623660234baee372a448658965ec31d7c6cc90863ce73f0c18df7c8e79f
  analysis completeness
81e9f44683872ba64249c73a80e95e5f6ee3193fc6229f3fc0c11847c25e7268
  analysis metrics
db0a514252f83ba0b4eab379677bda237a2564fd5040f37bd3865de95589c112
  resolved scenario
deb08439f285a1bcff7e7b5fe763acbf095e7175d995367c626f9d83d7b30e11
  installed scenario definition
4a2f6b25c0098476f50e6eefe09f070805c77dc28c7c719707c5cf6b623b8836
  M4.6 visible report
```

Read-only SQLite validation remains:

```text
PRAGMA quick_check: ok
messages: 579958
topics: 34
```

M4.6, M4.5, M4.4, M4.3, V6, the shifted world, and the historical world
hashes pass their committed regressions.

## Bounded implementation corrections

An initial signed-progress assertion exposed binary floating-point boundary
rounding; the implementation now uses the same `1e-12` numerical tolerance
as the deterministic geometry comparisons. Two initial combined-test
commands overwrote the overlay Python path and failed during ROS message
collection; the final commands prepend the source package to the intact
overlay and pass.

Schema and liveness test fixtures initially omitted their own prerequisite
fields; those fixtures were corrected without weakening production gates. A
manual production diff review then found that resume-stage recomputation
could use radial preference after the bypass flag cleared. The source
condition was corrected before final qualification and is covered by a
non-collinear regression. The final targeted, focused, broad, isolated-build,
parity, and dry-run results above all use that corrected source.

Installed controller introspection initially used an obsolete private
executable field and then accessed a pre-execution node-name property. It was
rerun with this ROS install's public package/executable properties and
current private argument storage; both branches resolve as declared. None of
these bounded corrections started ROS nodes or Gazebo or changed acceptance
gates.

## Pre-dispatch boundary

At qualification close:

- both fresh production evidence roots are absent;
- no Gazebo, scenario runner, recorder, rosbag, analyzer, or matching ROS
  process is active;
- no Gazebo process was started during M4.7 implementation or qualification;
- M4.6 remains immutable and its conditional suite remains not run;
- no three-light, Phase 09, physical, or hardware action occurred.

The next allowed action is to checkpoint and commit this exact no-Gazebo
boundary. Gazebo remains closed until that commit exists. Afterward, only the
one fixed visible paired M4.7 case may be prepared for dispatch; the
eight-case suite remains passing-gated by that visible result.
