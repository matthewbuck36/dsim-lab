# Phase 08.8 M4.10 v8.9 no-Gazebo qualification

Date: 2026-07-31 local and UTC

## Disposition

**PASS — SCHEMA-V13 DUAL-TOPOLOGY RECOVERY EVIDENCE AND ALL FOUR
FRESH V8.9 INPUTS ARE QUALIFIED WITHOUT GAZEBO.**

This record qualifies the v8.9 evaluator/evidence correction and fixed
scenario inputs. It does not claim a new Gazebo behavior result. No Gazebo,
scenario execution, recorder, analyzer, rosbag recorder, or physical process
ran during this qualification.

The first possible runtime action remains the single installed visible
primary probe:

```text
phase08_v8_9_primary_visible_probe.yaml
seed 19701
```

It remains prohibited until this implementation, report, live status, Phase
08 checkpoint, and implementation commit pass, followed by a separately
checkpointed and committed dispatch boundary.

## Qualified correction

V8.9 changes no controller, supervisor, convergence detector, Gaussian-fill
owner, modified-cost owner, launch argument, launch graph, world, source
field, motion, candidate ranking, timeout, stop, final-zero, or cleanup
behavior.

The current schema constant and supported set are:

```text
SCHEMA_VERSION:             13
SUPPORTED_SCHEMA_VERSIONS:  1 through 13
```

Schema versions through 12 retain their prior path selection, predicate set,
live Stage A behavior, offline outcome behavior, and
`supervisor_owned_escape_assist` interpretation. Schema 13 adds:

```text
escape_command_ownership
```

and accepts exactly:

```text
direct:
  SEARCH
  -> VERIFY_EXTREMUM
  -> DESIGN_OR_MERGE_FILL
  -> ESCAPE_REPULSE
  -> SEARCH
  -> VERIFY_EXTREMUM
  -> GOAL_HOLD

measured-stall fallback:
  SEARCH
  -> VERIFY_EXTREMUM
  -> DESIGN_OR_MERGE_FILL
  -> ESCAPE_REPULSE
  -> ESCAPE_ASSIST
  -> SEARCH
  -> VERIFY_EXTREMUM
  -> GOAL_HOLD
```

The common event sequence omits conditional `ESCAPE_STALLED`. If any valid
assist state occurs, the complete schema-v12 causal entry and schema-v11
causal exit proof remains mandatory; a failed assisted episode cannot use
the direct proof.

Without assist, the predicate positively proves:

- exactly one causally bound, finite, unit, revision-one
  `ESCAPE_STARTED` geometry;
- unchanged repulse weights `(0, 1, 1)`, center, direction, radius, and
  failsafe state;
- no stalled event or valid stalled sample;
- mature radial progress at or above the declared threshold and radial
  distance through the frozen exit radius;
- zero supervisor command and contribution;
- finite, arithmetically consistent, correctly saturated ordinary GESC
  control with at least one nonzero proposal;
- stable return to `(1, 1, 0)` `SEARCH` with escape authority cleared; and
- measured exit distance through the frozen radius and alignment at least
  `+0.80`.

The event may precede the first repeated repulse-state bag sample only within
the already-declared `supervisor_command_stale_sec` freshness bound. This is
a cross-topic causal binding, not an unbounded event search.

## Immutable retained replays

Final replay artifact:

```text
/tmp/phase08_8_m4_10_v8_9_retained_replay.log
SHA-256:
  e064ae7e4b59d75c87ece6970e0ab77dd3194f940037ff5eb25b3fdbfac87300
```

### Direct seed 19616

The immutable v8.8 seed-`19616` bag and original resolved schema-v12 input
remain unchanged. Current source reproduces the fixed historical result:

```text
schema-v12 Stage A:       false
schema-v12 ranking:       false
schema-v12 proximity:     false
schema-v12 assisted proof:false
schema-v13 result key:    absent
outcome_error:            null
```

The same immutable message set under the fresh schema-v13 fixture passes:

```text
branch:                              direct_repulse
Stage A:                             true
fill cardinality:                    true
strict raw ranking:                  true
post-recovery global proximity:      true
escape command ownership:            true

ESCAPE_STARTED to state lag:         0.000275934 s
raw repulse state samples:           466
raw supervisor command samples:      466
raw control diagnostic messages:     3,010
raw mature progress state samples:   407
frozen exit radius:                  1.3667708293638696 m
measured exit distance:              1.4011374665770484 m
selected/exit alignment:             0.9475175293061029
```

The raw evaluator count and retained analyzer count are intentionally
distinguished. The evaluator proves all `3,010` distinct raw diagnostic
messages whose bag stamps lie inside the strict repulse interval. The
retained analyzer synchronizes control records to higher-rate cost samples
and contains:

```text
synchronized ESCAPE_REPULSE control rows: 3,015
maximum |supervisor contribution|:        0.0
maximum |combined - GESC|:                 0.0
synchronized mature progress rows:        2,640
minimum mature progress:                   0.0596847334142062 m
maximum mature progress:                   0.22554332237301575 m
```

Both views positively prove ordinary GESC ownership. The difference is
sampling/synchronization grain, not missing evidence.

The first `59` repeated state messages precede maturity of the fixed
three-second progress window and correctly report
`escape_stalled_valid=false`. The next `407` report valid
`escape_stalled=false` with mature progress above `0.05 m`. Schema 13
therefore forbids a valid stalled sample without incorrectly requiring stall
validity before the window exists.

### Assisted seed 19611

The immutable passing assisted seed `19611` was evaluated under its original
schema-v12 input and the fresh schema-v13 fixture:

```text
schema-v12 assisted proof:     true
schema-v13 ownership proof:    true
schema-v13 selected branch:    assisted
entry evidence mode:           bounded_causal_schema_v12
exit evidence mode:            bounded_causal_schema_v11
non-wrapper evidence changes:  none
Stage A / ranking / proximity: true under both schemas
```

Every schema-v12 entry and schema-v11 exit evidence field is reproduced
exactly. No historical result was rewritten, retried, or reclassified.

## Negative and compatibility evidence

Schema-v13 fixtures reject:

- an exit inside the frozen radius;
- alignment below `+0.80`;
- missing or below-threshold mature progress;
- state distance that never reaches the exit radius;
- a stalled state or `ESCAPE_STALLED` event without assist;
- nonzero repulse or returned-search supervisor command;
- GESC-plus-supervisor combination;
- all-zero GESC control;
- nonfinite event or control data;
- contribution arithmetic or final-saturation corruption;
- geometry or direction-revision mismatch;
- retained search authority or missing returned `SEARCH`; and
- every attempt to use the direct proof after assist entry.

The complete pre-existing assisted-branch negative fixtures also pass
unchanged. The schema requires the new predicate in both top-level and
result-scope contracts, requires both exact recovery paths, and rejects its
use below schema 13.

## Fixed scenario inputs

The four fresh schema-v13 inputs are:

```text
e088a4a6b84f40834db46f8eb1714566a502e75bfbbe636cbaa5f10a8d98fd3f
  phase08_v8_9_primary_repeats.yaml
2131b9b77587c7326e31acb63a6922ce4fbd81655b711f0b119f1c97be4c736c
  phase08_v8_9_primary_visible_probe.yaml
f7c91a3fadcc860a82a91e1a50164eb2631bd6c1669ff2ac1cae040eda455a6d
  phase08_v8_9_secondary_repeats.yaml
aa542de3e244bf7720de7ca3cd4ebf1247f1cf0e5fb53acc204df6244b4846b2
  phase08_v8_9_secondary_visible_probe.yaml
```

Whole-document normalization tests prove all four v8.9/v8.8 pairs differ
only in schema/evidence semantics, the two declared paths, conditional
events, predicate identity, versioned identifiers, descriptions, run roots,
and fresh seeds. Every source, start, intensity, topology, launch override,
controller value, Stage A/Stage B budget, simulation-only `0.50 m` evaluator
stop, final-zero rule, cleanup rule, and first-failure rule is unchanged.

The retained v8.8 input hashes remain:

```text
003230a00ddc0ab07adad5957012c3c28539119fbbb885a3edcd5f594b4298ca
  phase08_v8_8_primary_repeats.yaml
e48f8f6fd1e2e8377f13d5e621ad6df2017b663b8f35a977d01af5d14605b5e1
  phase08_v8_8_primary_visible_probe.yaml
ff2da3610f977e8f239f67ed9e1d586705894fb84e1821d87d817b6b9f479884
  phase08_v8_8_secondary_repeats.yaml
5a0b18609a7e4abb87858d36575d0fa9c10fd0837b259d84bf357aea83ce31f7
  phase08_v8_8_secondary_visible_probe.yaml
```

The sealed v8.9 dispatches are:

| Gate | GUI | Seeds | Run root |
|---|---:|---|---|
| primary visible | yes | `19701` | `phase08_8_9_primary_probe` |
| primary repeats | no | `19711..19720` | `phase08_8_9_primary_repeats` |
| secondary visible | yes | `19751` | `phase08_8_9_secondary_probe` |
| secondary repeats | no | `19761..19765` | `phase08_8_9_secondary_repeats` |

The claim remains limited to the two fixed local-first, two-source,
open-field layouts at simulator-relative `400/1600`. The physical contract
remains coordinate-free and operator-stopped with `Ctrl+C`.

## Source qualification

Every final pytest command used repository source first while retaining the
isolated ROS/interface overlay:

```bash
source /opt/ros/humble/setup.bash
source /tmp/phase08_8_v8_8_release_final.L0zEGg/install/setup.bash
export PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc:$PYTHONPATH
```

Final schema and runner:

```text
356 passed, 1 skipped in 55.62 s
JUnit:
  /tmp/phase08_8_m4_10_v8_9_schema_runner_exact_final.xml
SHA-256:
  71a3a2bdd19c4a7370ac0ade49572f48f255ef99d10b55a0c4c8ac83d0ee1da6
```

Focused controller, supervisor, detector, geometry, observability, search
history, controller-spawner, and legacy regression:

```text
310 passed in 8.49 s
JUnit:
  /tmp/phase08_8_m4_10_v8_9_focused_controller_final.xml
SHA-256:
  42d2c00a5b377f836db9f6be8fc905b7aac8eb66a787a045f03e1e78175eb604
```

Focused runner, schema, validator, recorder, analyzer, aggregate-truth,
disturbance, and shutdown regression:

```text
643 passed, 2 skipped in 131.53 s
JUnit:
  /tmp/phase08_8_m4_10_v8_9_focused_evidence.xml
SHA-256:
  9493da77b651f0f00af26096a1e972ea191cbb72916855cd28baee209b15775a
```

Final broad ROS-independent functional regression across all nineteen
functional modules plus the copyright check:

```text
953 passed, 3 skipped in 142.17 s
JUnit:
  /tmp/phase08_8_m4_10_v8_9_broad_functional.xml
SHA-256:
  f356ae9799f40bdb9a9e99db36992b68aec09941de9716788956b3541d7f077e
```

The broad skips are the unchanged copyright-template check and the two
explicit Gazebo opt-ins. There are no functional failures or errors.

Changed-file `ament_flake8` reports only the inherited D202 at
`run_scenario.py:2420`; additions above it shifted the old line number but
did not change that function. The required fatal selection
`E9,F63,F7,F82` is empty.

Changed-Python compilation, all four YAML parses, central-launch XML parsing,
Python launch compilation, `git diff --check`, and:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/
  validate_phase_context.sh 08 implement
```

all pass.

## Fresh isolated build and installed graph

The final fresh build used:

```bash
colcon --log-base "$qual_root/log" build \
  --base-paths /home/mattb/dsim-lab/ros2_ws/src \
  --build-base "$qual_root/build" \
  --install-base "$qual_root/install" \
  --packages-select \
    ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
```

Result:

```text
root:
  /tmp/phase08_8_v8_9_release_qual.2fWDxv
result:
  3 packages finished in 11.9 s
```

Source/install byte parity passes for `10/10` runtime owners: controller,
scenario runner, scenario schema, supervisor state machine, supervisor
adapter, central launch, and all four v8.9 scenarios.

Installed nonexecuting launch checks:

```text
/tmp/phase08_8_m4_10_v8_9_release_show_args.txt
  43e0728a91f7cbd66947786e688055e3fa7acd228e46568d6bd32ad432d0661f
/tmp/phase08_8_m4_10_v8_9_release_launch_description.txt
  61e89732134b238d6fd2ed806e8e307661f2e83f792b16dfe1df015c90f0d2ed
```

Both return zero. Installed schema inspection reports version `13` and
supported versions `1..13`.

Direct installed construction on isolated ROS domains `225..228` reached
the expected bounded timeout `124` without startup errors:

```text
default supervisor:
  /tmp/phase08_8_m4_10_v8_9_supervisor_default.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
fully enabled counted-source supervisor with max_fill_clusters=1:
  /tmp/phase08_8_m4_10_v8_9_supervisor_enabled.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
robust affine modified-cost owner:
  /tmp/phase08_8_m4_10_v8_9_modified_cost.log
  6adca77c3105baed1df7ce01c52ea10252a1619923ae8e69de6a3aacedc06428
fully enabled robust controller:
  /tmp/phase08_8_m4_10_v8_9_controller_enabled.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

The modified-cost log contains only its two normal startup messages. No
construction process survived.

## Installed dry-run expansion

All four exact final-install invocations used:

```bash
ros2 run ros_esc run_scenario SCENARIO \
  --operator Codex \
  --dry-run
```

They resolve with zero unsupported cases:

| Scenario | GUI | Runs | Seeds | Dry-run SHA-256 |
|---|---:|---:|---|---|
| primary visible | yes | 1 | `19701` | `f57df97d865629e85b9a00e6f284e3caa045223d15772a99b53a14a6b02be00d` |
| primary repeats | no | 10 | `19711..19720` | `26fad9e203a8fc95fb5122e9dc338196fde6bd221e53b1cfe4efc56ec5a1faca` |
| secondary visible | yes | 1 | `19751` | `52533141216023fc0cc2f304ef4c853cfe6ba3b8d36bc041d1ae5ec78081213d` |
| secondary repeats | no | 5 | `19761..19765` | `f7230512f8e9cb98c4570bf6e3de41d05952acbb3ce951e43927755184006176` |

All four sealed run roots were absent before and after dry-run.

## Historical preservation

No historical scenario, world, V6 selection, result, plot, bag, or failed
evidence is modified. Retained anchors remain:

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

V6, v8-v8.8, shifted worlds, and every older scenario remain selectable.
Fixed failed evidence remains failed and was not retried or relabeled.

## Bounded qualification corrections

The following pre-runtime issues were preserved and corrected:

- the initial focused invocation sourced the immutable v8.8 install ahead of
  source and therefore loaded schema 12; source-first `PYTHONPATH` fixed the
  qualification environment without changing code;
- the retained direct event precedes the first repeated repulse-state bag
  sample by `0.275934 ms`; schema 13 now binds it within the existing
  freshness limit while keeping exact event cardinality and geometry;
- immature pre-window state samples correctly leave stall validity false;
  only a valid stalled sample or stalled event fails the direct branch;
- the generic unsupported-version fixture still used newly supported version
  13; it now rejects version 14;
- the pair-preservation test initially normalized the entire success mapping;
  it now names every allowed path, event, predicate, scope, identity, root,
  description, and seed difference explicitly;
- the final negative set added missing progress, insufficient distance,
  geometry/revision, stalled-event, nonfinite-event, returned-command, and
  missing-search cases;
- one static helper named a nonexistent historical launch path; the corrected
  central `gazebo.launch.xml` parse passes; and
- the retained analyzer's `3,015` synchronized rows and evaluator's `3,010`
  distinct raw diagnostic messages are now reported separately.

These are Level B evidence-contract, test-fixture, or qualification-invocation
corrections. No controller motion, source field, stop behavior, empirical
result, or acceptance threshold changed.

## Runtime boundary

At qualification close:

- no Gazebo, scenario runner, recorder, analyzer, rosbag recorder, controller,
  supervisor, or physical process is active;
- all four v8.9 run roots remain absent;
- no historical input or result is changed;
- the physical contract remains manual operator `Ctrl+C`; and
- sealed-run monitoring may use only process state and retained files, never
  a ROS/DDS participant on the run domain.

The next authorized action is the implementation checkpoint and commit,
followed by a separate dispatch-boundary checkpoint and commit. Only then may
the visible seed-`19701` primary probe run once. A behavioral, schema-v13
ownership, recording, final-zero, or cleanup failure closes that visible
gate. A formal pass and all nine analysis plots are required before the
primary repeat population may be dispatched.
