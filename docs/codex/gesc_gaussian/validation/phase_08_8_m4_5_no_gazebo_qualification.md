# Phase 08.8 M4.5 v8.5 no-Gazebo qualification

Date: 2026-07-31 local and UTC

## Disposition

**PASS — IMPLEMENTATION QUALIFIED WITHOUT GAZEBO.**

This record qualifies the fresh v8.5 active-fill corridor-lock
implementation and its four fixed scenario inputs. It does not claim Gazebo
behavioral success. No Gazebo, scenario execution, recorder, analyzer, or
physical process ran during implementation qualification.

Only after the implementation checkpoint, bounded implementation commit, and
a separate visible-dispatch checkpoint and commit may one installed visible
execution start:

```text
phase08_v8_5_primary_visible_probe.yaml
seed 19301
```

## Qualified behavior

The implementation adds one default-off parameter:

```text
open_field_escape_active_fill_transit_enabled: false
```

It is valid only with the complete v8.4 counted-candidate,
candidate-informed, open-field assist and approach-continuity contract. When
enabled by the fixed v8.5 profile:

1. the existing approach-continuity evidence freezes the direct unit vector
   from the newest supervisor-history pose outside the accepted fill's exit
   radius toward that fill center;
2. that exact direct direction is latched at revision one;
3. the active typed Gaussian remains in the fill registry and modified cost,
   but is excluded from collision-like direction eligibility for its own
   escape episode;
4. every other retained fill remains a hard direction and command-sweep
   constraint;
5. an unsafe other-fill corridor, missing active fill, missing geometry, or
   direction mismatch fails explicitly instead of selecting or reversing a
   direction;
6. the corridor is revalidated on every zero-command `ESCAPE_REPULSE` update
   and every bounded `ESCAPE_ASSIST` update;
7. both escape states publish
   `(raw, Gaussian, affine) = (0, 1, 1)`, and the modified-cost owner binds
   exactly one affine term to the same fill and direction revision;
8. supervisor translation remains zero in repulse; measured-stall assist
   follows the same direct vector;
9. measured escape completion, `SEARCH`, terminal, reset, explicit stop, and
   failsafe paths clear the corridor, direction, command, and affine
   authority.

The enabled escape event appends the excluded active fill ID, other-fill
count, already-existing latched vector, and revision. The enabled
configuration event appends the new switch. Default-off event payloads and
all historical direction-selection behavior remain unchanged.

No source position, source role, declared global coordinate, Vicon pose, room
geometry, wall model, simulation truth, waypoint, route map, or persistent
post-recovery direction enters the controller.

## Retained-geometry qualification

Pure tests replay all eight retained primary fill-acceptance geometries: the
five executed v8.3 geometries and the three executed v8.4 geometries.

For each fixture:

- default-off selection reproduces the retained v8.4 output;
- enabled v8.5 latches the exact direct approach-history vector;
- rotation is zero and direction revision remains one.

The failed v8.4 seed `19212` is replayed at fill acceptance and at the
previous reversal geometry:

```text
fill center:
  (1.0694882817937204, 1.314024891709896)
fill-acceptance pose:
  (1.070101672495912, 1.3123173373351547)
direct approach vector:
  (0.4015882065675672, 0.9158203493840072)
previous post-reversal position:
  (-0.3808628950823218, 1.3271483177165915)
```

The active fill rejects the direct vector under the retained v8.4
collision-like rule, while v8.5 retains the direct vector at both positions.
An added second fill intersecting the same look-ahead corridor is rejected
explicitly. Integration coverage proves the full active-fill avoidance list
still contains the active fill while the direction-only set excludes exactly
that fill and retains the added second fill.

The existing modified-cost regression proves the active Gaussian remains
present, one affine term is bound once in repulse, the same term persists
through assist without restarting, and `SEARCH` clears it.

## Fixed scenario inputs

Each new input is schema version 9. The sources, start, topology, candidate
and fill parameters, detector settings, affine settings, Stage A and Stage B
budgets, simulation-only proximity stop, cleanup gates, and first-failure
rules are identical to the corresponding v8.4 input. Only fresh identity,
seed, evidence root, and the new true switch differ.

```text
f8b7be764bb7d7024753cf64b8633944ff70055e9a4a88a97ab8e462b8a5ac6c
  phase08_v8_5_primary_repeats.yaml
39f807c055d5ea0217b6f3510ac34bb1a068316da4cc18841911f428371dae28
  phase08_v8_5_primary_visible_probe.yaml
141916047195f351ff78c524c02fafe6f3af81840a97b55d38148b69f26a8145
  phase08_v8_5_secondary_repeats.yaml
0749ba218bd79212f93946f8e55601e95727e195e8ef8fecd5d192e81a88ee70
  phase08_v8_5_secondary_visible_probe.yaml
```

Every resolved run has:

```text
known_source_count:                               2
gaussian_fill_max_fills:                          1
candidate_informed_fill_enabled:                  true
operating_bounds_enabled:                         false
open_field_escape_assist_enabled:                 true
open_field_escape_approach_continuity_enabled:    true
open_field_escape_active_fill_transit_enabled:    true
modified_cost_enable_affine_bias:                 true
modified_cost_affine_gain:                        0.50
modified_cost_affine_decay_rate:                  0.0000005
modified_cost_affine_max_age:                     35.0
modified_cost_affine_direction_sign:              1.0
recenter_after_escape:                            false
recoverable_navigation_enabled:                   false
post_recovery_guidance_enabled:                   false
simulation_contacts_enabled:                      false
validation_world:                                 false
```

Schema validation rejects use below schema version 9, non-Boolean values, and
active-fill transit without approach continuity. Launch tests prove the
switch reaches the supervisor while evaluator-only roles, global
coordinates, and simulation-truth outcomes remain outside controller
arguments.

## Source tests

Final focused controller, geometry, supervisor, modified-cost,
observability, detector, search-history, and legacy command:

```text
301 passed in 8.71 s
JUnit:
  /tmp/phase08_8_m4_5_focused_controller_final.xml
SHA-256:
  f2a4f6f25fe2359103f3bb5c963845ed3a3fce3f858e57c0cc8bed3ef84de4ad
```

Final schema, runner, Phase 08 validator, recorder, bag analysis, aggregate
truth, disturbance, shutdown, and evidence-support command:

```text
541 passed, 2 skipped in 130.82 s
JUnit:
  /tmp/phase08_8_m4_5_focused_evidence_final.xml
SHA-256:
  59d35ddcd54ff0dd56c29d72cdd4551ed154ff02a2b2019b7f959de6ceb7a23b
```

Final complete ROS-independent functional regression, excluding the
repository's separate style and copyright files:

```text
842 passed, 2 skipped in 136.58 s
JUnit:
  /tmp/phase08_8_m4_5_broad_functional_final.xml
SHA-256:
  92b429f0fb3aa453271c0d280289940106fde1f27bd71aac99b4d75c9539fee4
```

The two skips are the unchanged explicit visible-recording and recorded
headless-Gazebo opt-ins. There are no final failures, errors, or
deselections.

Fatal changed-file lint (`E9,F63,F7,F82`), changed-Python compilation,
central launch XML parsing, all four YAML parses, `git diff --check`, and:

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/
  validate_phase_context.sh 08 implement
```

all pass.

## Fresh isolated build and installed graph

The from-scratch release build used:

```text
log:
  /tmp/phase08_8_m4_5_release_qual/log
build:
  /tmp/phase08_8_m4_5_release_qual/build
install:
  /tmp/phase08_8_m4_5_release_qual/install
packages:
  ros_esc_interfaces
  ros_esc
  turtlebot3_rotating_sensor
result:
  3 packages finished in 12.7 s
```

Source/install byte parity passes for `10/10` runtime owners: the supervisor
state machine, escape geometry helper, supervisor adapter, scenario schema,
modified-cost owner, four fixed v8.5 scenarios, and central Gazebo launch.

Installed nonexecuting launch checks:

```text
/tmp/phase08_8_m4_5_release_show_args.txt
  4261c72e9315aac2595f2f51a942ce2c437b83e7bf56fb24cce775bb37b3691a
/tmp/phase08_8_m4_5_release_launch_description.txt
  8de25f8704cf88168586b2cda615c52bbb13f9c40907b8833f5c0d57638f40ab
```

Both expose and bind
`open_field_escape_active_fill_transit_enabled`. Direct installed
construction of the default supervisor, the fully enabled v8.5 supervisor,
and the robust modified-cost node each reached expected bounded timeout
`124` without startup error:

```text
/tmp/phase08_8_m4_5_release_supervisor.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
/tmp/phase08_8_m4_5_release_supervisor_v8_5.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
/tmp/phase08_8_m4_5_release_modified_cost.log
  548b06f98040223cb124dedc088270a24b82950b0bb7628842e08d0554289a01
```

## Installed dry-run expansion

All four planned invocations resolve from the isolated install with zero
unsupported cases:

| Scenario | GUI | Runs | Seeds | Dry-run SHA-256 |
|---|---:|---:|---|---|
| primary visible | yes | 1 | `19301` | `7b503499ec6102ea165fdd05487c4ac2897bcf33eea49746e3b46496fad082be` |
| primary repeats | no | 10 | `19311..19320` | `48737e675da2b27726c0a3ee30f0770f905aef48e9efb0cf43c88dcd4dae17db` |
| secondary visible | yes | 1 | `19351` | `a74d8d276fc0a6450cba8de540956aa52b5dfbf4591dc3005a7b41976d0778c8` |
| secondary repeats | no | 5 | `19361..19365` | `5c536f42c9befe38bbba09280f9d48737633227d36787aaf2e03b587c76c554a` |

Every resolved case and controller contract has a fresh `v8_5` identity and
includes the true active-fill-transit launch argument. All four configured
run roots were absent before and after dry-run.

## Historical preservation

No historical scenario, world, V6 selection, result, plot, bag, or failed
evidence is modified. Retained hashes remain:

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

V6, v8-v8.4, shifted worlds, and all older scenarios remain selectable.
Fixed failed evidence remains failed and was not retried or relabeled.

## Bounded qualification corrections

The following issues were found and corrected before any Gazebo dispatch:

- the first recovery command used a nonexistent repository-root validation
  script; the package-qualified path passed;
- the first full regression reported two exact freeze-comparison failures
  because a mechanical `192` to `193` seed replacement also changed one
  digit in the secondary local source's `y_m` coordinate;
- both fresh secondary inputs were restored to the exact v8.4 coordinate
  `1.38581929876693`; the exact four-pair freeze test and the full regression
  were then rerun and passed;
- the per-tick contract initially revalidated the corridor in assist but not
  zero-command repulse; repulse now performs the same exact-direction and
  other-fill check, with focused and broad coverage;
- one unrelated timing-sensitive M2 integration test missed its short wait
  once; it had passed immediately before, passed alone on the unchanged
  source, and passed in every final focused and broad command.

The superseded broad run is preserved as local qualification evidence:

```text
840 passed, 2 failed, 2 skipped
/tmp/phase08_8_m4_5_broad_functional.xml
SHA-256:
  ebd94903d78c8789acc195f4e03af10e1aada2d9373fc57b7633c3b342dc6f97
```

These are Level B implementation or test-fixture corrections. They started no
Gazebo process and changed no empirical result.

## Runtime boundary

This qualification establishes implementation and infrastructure readiness
only. It does not establish that v8.5 escapes or reaches candidate two in
Gazebo.

At qualification close:

- no Gazebo, scenario runner, recorder, rosbag recorder, analyzer, or physical
  process is active;
- all four v8.5 run roots remain absent;
- no historical input or result is changed;
- the physical contract remains operator `Ctrl+C`, with no physical
  coordinate-distance stop.

After checkpoint and commit, a separate dispatch boundary may authorize only
the visible primary probe at seed `19301`. A behavioral, evidence, recording,
final-zero, or cleanup failure closes v8.5 immediately. A formal visible pass
is required before any primary repeat is dispatched.
