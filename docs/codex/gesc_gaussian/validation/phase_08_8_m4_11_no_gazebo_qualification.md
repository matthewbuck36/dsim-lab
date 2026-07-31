# Phase 08.8 M4.11 v8.10 No-Gazebo Qualification

Date: 2026-07-31 local and UTC

## Disposition

**PASS — ALL THREE RECORDER CHILD PATHS ARE ANCHORED TO THE RESOLVED
CHECKOUT, ALL FOUR FRESH V8.10 INPUTS ARE QUALIFIED, AND NO GAZEBO
PROCESS RAN.**

This record qualifies the narrow v8.10 scenario-runner/recorder integration
correction. It is not a new behavioral result. The first possible runtime
action remains one separately checkpointed and committed installed visible
primary probe:

```text
phase08_v8_10_primary_visible_probe.yaml
seed 19801
```

## Qualified correction

The production change is exactly three additions to
`run_scenario.py`. Each owner of the sole Phase 05 `record_run` child now
passes:

```text
cwd=REPOSITORY_ROOT
```

The three owners are:

```text
_run_record_to_boundary
_run_record_to_global_proximity
run_record_process
```

The runner already resolved `REPOSITORY_ROOT`; it previously failed to give
that root to its child. Consequently, an installed runner called from
`/tmp` launched a recorder whose `git_state(Path.cwd())` lookup also used
`/tmp`. The v8.9 seed-`19701` recorder stopped before Gazebo with Git return
code `128`.

V8.10 changes no recorder implementation, Git metadata semantics, controller,
supervisor, convergence detector, Gaussian fill, affine term, modified cost,
raw-cost ranking, schema-v13 evaluator, source model, world, launch
parameter, state machine, motion behavior, timeout, stop, final-zero,
cleanup, or physical path.

Focused process tests prove:

```text
normal recorder child:              checkout cwd
boundary-observed recorder child:   checkout cwd
staged global-proximity child:      checkout cwd
arbitrary caller cwd:               not propagated
start_new_session and timeout:      unchanged
boundary and staged lifecycle:      unchanged
```

The visible run must still verify that its finalized metadata records the
committed checkout. No empirical metadata claim is made before that run.

## Fresh fixed scenarios

The four schema-v13 files and hashes are:

```text
c41eea1e6e10d8f736bb669fdf13db46eb8a6ed23b512a5827e8675d2d5c501b
  phase08_v8_10_primary_visible_probe.yaml
cdb5e05339745d89afc632388af2e8bae45de75159c514f3d85832732361c796
  phase08_v8_10_primary_repeats.yaml
a0f9c7032be4e2540e3937cd741c9271c7358bba48dd5e6d41a23208a488f3ed
  phase08_v8_10_secondary_visible_probe.yaml
f7c54e8213f288b54051d69b06ae6ba1e75daf328763488ea970ebaffe550b3e
  phase08_v8_10_secondary_repeats.yaml
```

Whole-document tests and independent normalized byte comparisons prove that
each v8.10/v8.9 pair differs only in its versioned identities, descriptions,
run root, and fresh seeds. Scientific inputs remain:

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
  one local, one global, maximum one active typed fill
simulation-only global proximity:
  0.50 m after valid Stage A and strict second-candidate ranking
```

Controller behavior, schema-v13 direct/assisted recovery paths, every
predicate, Stage A/Stage B budgets, `720.0 s` run bound, `900.0 s` wall
bound, final-zero, cleanup, and first-failure rules are unchanged.

## Retained-bag replay

The final read-only replay is:

```text
/tmp/phase08_8_m4_11_v8_10_retained_replay.log
SHA-256:
  b24fa96e9f0aadbaf57e618f1a82c9da8d16cd2b34e4e49b18b7a03bd6287ba5
```

Seed `19616` remains unchanged under its original schema-v12 input:

```text
Stage A:                         false
strict ranking:                  false
post-recovery proximity:         false
assisted ownership:              false
outcome error:                   null
```

The same immutable bag with the v8.10 schema-v13 contract passes:

```text
branch:                          direct_repulse
Stage A / ranking / proximity:   true / true / true
escape command ownership:        true
repulse states:                  466
raw repulse controls:            3,010
supervisor commands:             466
mature progress states:          407
measured exit distance:          1.4011374665770484 m
frozen exit radius:              1.3667708293638696 m
exit alignment:                  0.9475175293061029
outcome error:                   null
```

Retained assisted seed `19611` passes both versions:

```text
schema-v12 assisted ownership:   true
schema-v13 command ownership:    true
schema-v13 branch:               assisted
entry evidence mode:             bounded_causal_schema_v12
exit evidence mode:              bounded_causal_schema_v11
Stage A / ranking / proximity:   true / true / true
outcome errors:                  null
```

All four database opens were read-only. No retained result, bag, analysis,
or plot was rewritten.

## Source tests

Every pytest command used repository source first while retaining the
qualified v8.9 ROS/interface overlay:

```bash
source /opt/ros/humble/setup.bash
source /tmp/phase08_8_v8_9_release_qual.2fWDxv/install/setup.bash
export PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc:$PYTHONPATH
```

Targeted correction:

```text
10 passed, 357 deselected in 1.31 s
JUnit:
  /tmp/phase08_8_m4_11_v8_10_targeted.xml
  14f2f81504040a6dedddd74821da72eb62ca620992a00df862d328d9b41362f6
```

Complete schema and runner:

```text
366 passed, 1 skipped in 56.24 s
JUnit:
  /tmp/phase08_8_m4_11_v8_10_schema_runner.xml
  040c676c5b20becc2e2f60389b74463100ff8dad8e57348210367c5b821c7880
```

Controller, supervisor, detector, escape, modified-cost, search-history,
observability, controller-spawner, and legacy:

```text
310 passed in 8.50 s
JUnit:
  /tmp/phase08_8_m4_11_v8_10_focused_controller.xml
  7eb7057aa59b217b55fd9adb6aa8f1bd2ad5ea7cb5a6d7dd1b6e6033b093d084
```

Runner, schema, validator, recorder, analyzer, aggregate-field,
disturbance, and shutdown:

```text
653 passed, 2 skipped in 133.17 s
JUnit:
  /tmp/phase08_8_m4_11_v8_10_focused_evidence.xml
  fb37dcb17fefdbd0462191fd8f3cb5410e931524f0bb31345dfabc481afcd1ab
```

Final broad ROS-independent functional envelope:

```text
963 passed, 3 skipped in 141.73 s
JUnit:
  /tmp/phase08_8_m4_11_v8_10_broad_functional.xml
  9df9dd0abc29943e4b892157cace093c67148153caddb9e3d90b66862d4d135c
```

The broad skips are the unchanged copyright-template check and two explicit
Gazebo opt-ins. There are no functional failures or errors.

Changed-file `ament_flake8` reports only the inherited D202 in
`run_scenario.py`; the three inserted production lines shift its line number
to `2423` but do not touch the function. Fatal `E9,F63,F7,F82` selection is
empty.

Python compilation, four YAML parses, central-launch XML parsing, Phase 08
context validation, and `git diff --check` pass.

## Fresh isolated build and installed graph

Build:

```text
root:
  /tmp/phase08_8_v8_10_release_qual.VIowrN
command:
  colcon build --packages-select
    ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
result:
  3 packages finished in 11.8 s
log:
  /tmp/phase08_8_m4_11_v8_10_build.log
  e9b372d5ba43a3e60bed330cf9b3a96b4d9a6713435cfa0ff0a902cb2a32374a
```

Source/install byte parity passes for `10/10` required owners: controller,
scenario runner, scenario schema, supervisor state machine, supervisor node,
central launch, and all four v8.10 scenarios.

Installed inspection from `/tmp` reports:

```text
schema version:             13
supported schema versions:  1 through 13
launch --show-args:         pass
launch --print-description: pass
```

Launch artifacts:

```text
/tmp/phase08_8_m4_11_v8_10_release_show_args.txt
  5119431dc451f2afce4a8ed41d4a26dbdbdd9ed4a469047ca4cd1ea3f1012eee
/tmp/phase08_8_m4_11_v8_10_release_launch_description.txt
  4ecc667f260cf2cdc6c0eae4a2e70b41a38a1d1cecaef43ea76562d1608b2f9b
```

Direct installed construction used isolated domains `229..232`. The default
supervisor, fully enabled counted-source supervisor with
`max_fill_clusters=1`, robust affine modified-cost owner, and fully enabled
robust controller each reached expected timeout return code `124` without a
startup error. The modified-cost log contains only its two normal startup
messages; the other three logs are empty. No construction process survived.

## Installed dry-run expansion

All four installed runners were invoked from `/tmp` with:

```bash
ros2 run ros_esc run_scenario SCENARIO --operator Codex --dry-run
```

Results:

| Scenario | GUI | Runs | Seeds | First case key | Dry-run SHA-256 |
|---|:---:|---:|---|---|---|
| primary visible | yes | 1 | `19801` | `4e9ec74e17028e69b7d73d291654af0dfb2c875d397265c01ae887ad3ca8aaf2` | `c0b3b5c262634104773512740179a7fdc89724796219e2bffdab05295f603078` |
| primary repeats | no | 10 | `19811..19820` | `fec1b6dd2217a17d48ac6b02f844e01fa875834c1649959033776820bf04bafc` | `fe0ba43e03b4d1b8c4702cf2a2a48d1f98c15bded60fe52ff4bcb654de6ac4cc` |
| secondary visible | yes | 1 | `19851` | `4a7ffd4da063dce09eb74f2fb4d56a55dc2e6b7d77e2766ac10aa77468284c9c` | `a391ea9ed59b5ec808ee36b2807c7adf4032c48cad4ee5d555dfa9e7a6788d90` |
| secondary repeats | no | 5 | `19861..19865` | `c03aee83c124b694e9dd779c6546ee1d784065b26cc8f1913fd87ed37ecc5d25` | `b0e64ad75405cc74f76d3f091bdcccbc91346ec9b29e5b00abd43747377332b4` |

Every expansion has zero unsupported cases and the expected schema,
predicates, topology, bounded timings, GUI mode, roots, and seeds. All four
fresh run roots were absent before and after dry-run.

## Historical preservation

Retained anchors remain:

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

The four v8.9 scenario hashes match their prior qualification exactly. V6,
shifted worlds, v8-v8.9 scenarios, every historical run and plot, and every
fixed failure remain unchanged and selectable.

## Bounded qualification corrections

Two read-only assertion scripts initially named the wrong in-memory key:

- the dry-run audit looked for `runs[*].success` rather than the retained
  `runs[*].metadata.scenario_runner.success`; and
- the retained replay looked for `exit_distance_m` rather than
  `fill_to_exit_distance_m`.

Both stopped without changing source or evidence. The corrected bounded
audits above pass. These are qualification-script corrections, not code,
scenario, algorithm, or acceptance changes.

## Runtime boundary

At qualification close:

- no Gazebo, scenario runner, recorder, analyzer, rosbag recorder,
  controller, supervisor, or physical process is active;
- all four v8.10 roots are absent;
- no historical evidence changed;
- the physical contract remains manual operator `Ctrl+C`; and
- analysis targets must be read from the exact runner-emitted summary, never
  manually reconstructed.

The next action is the implementation checkpoint and commit, followed by a
separate checkpointed and committed dispatch boundary naming only installed
visible seed `19801`. No Gazebo process is authorized before both boundaries
are complete.
