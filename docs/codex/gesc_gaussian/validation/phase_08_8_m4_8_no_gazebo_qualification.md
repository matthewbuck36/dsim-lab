# Phase 08.8 M4.8 v8.7 no-Gazebo qualification

Date: 2026-07-31 local and UTC

## Disposition

**PASS — SCHEMA-V11 CAUSAL HANDOFF EVIDENCE AND FIXED V8.7 INPUTS ARE
QUALIFIED WITHOUT GAZEBO.**

This record qualifies the evidence-only v8.7 correction and its four fresh
scenario inputs. It does not claim a new Gazebo behavioral result. No Gazebo,
scenario execution, recorder, analyzer, rosbag recorder, or physical process
ran during this qualification.

Only after this implementation, report, status, and checkpoint are committed,
and a separate dispatch boundary is checkpointed and committed, may the one
installed visible primary probe run:

```text
phase08_v8_7_primary_visible_probe.yaml
seed 19501
```

## Qualified correction

V8.7 changes no controller, supervisor, detector, fill, modified-cost, launch,
world, source, motion, candidate-ranking, timeout, final-zero, or cleanup
behavior. The controller remains the sole `/cmd_vel` publisher.

Schema v11 retains the existing predicate:

```text
supervisor_owned_escape_assist
```

and adds one evaluator-only field:

```text
supervisor_owned_assist_handoff_timeout_sec: 0.15
```

The field is normalized under `success.controller`; it is not a launch
override and cannot enter controller or supervisor arguments.

Schema versions through v10 retain the exact existing first-recorded-sample
branch. Schema v11 keeps every assisted-escape ownership requirement and
replaces only the post-exit cross-topic ordering assumption. For the complete
recorded returned-`SEARCH` interval it now requires:

1. every state sample is valid `SEARCH`, has weights `(1,1,0)`, and has no
   active escape fill, escape geometry, safe direction, or direction
   revision;
2. at least one post-boundary supervisor command exists and every supervisor
   command in the interval is finite zero;
3. every control diagnostic is finite, has exact
   `combined - GESC = contribution` arithmetic, and has a final command equal
   to its recorded saturation;
4. before causal ordinary ownership, a diagnostic may be ordinary GESC, a
   zero/failsafe command, or the final fresh assist command already proven by
   a pre-exit control diagnostic;
5. ordinary GESC with zero supervisor contribution appears within `0.15 s`;
6. every later diagnostic until the next recorded non-`SEARCH` state remains
   ordinary GESC.

An arbitrary or stale tail, GESC-plus-supervisor leak, nonfinite command,
invalid contribution, invalid saturation, nonzero post-exit supervisor
publication, late handoff, invalid returned state, or later authority
reappearance fails.

The result records:

```text
post_exit_transition_control_sample_count
post_exit_handoff_delay_sec
post_exit_handoff_timeout_sec
post_exit_control_bag_stamp
post_exit_ordinary_control_sample_count
post_exit_handoff_evidence_mode
```

## Retained seed-19411 causal replay

The immutable v8.6 failure bag was read only:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_6_primary_repeats/2026-07-31/
  20260731T124148715876Z_simulation_phase08_v8_6_primary_repeats-
  v8_6_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_35b235c3/
```

The original resolved schema-v10 input remains failed exactly as required:

```text
passed:       false
outcome_error: null
reason:       post-exit SEARCH did not restore ordinary GESC ownership
SEARCH stamp: 1785501942470570252
```

The same immutable records evaluated through the schema-v11 evidence fixture
pass:

```text
passed:                           true
recognized transition samples:   1
first ordinary stamp:             1785501942478266750
handoff delay:                    0.007696498 s
handoff deadline:                 0.15 s
ordinary samples in full
recorded SEARCH interval:         13,109
later authority reappearance:     none
outcome_error:                    null
```

The formal schema-v11 count includes the first ordinary sample and every
later diagnostic before the first recorded non-`SEARCH` state. Every one
passes the arithmetic and saturation checks.

Retained replay:

```text
/tmp/phase08_8_m4_8_seed19411_causal_replay.log
SHA-256:
  87072d0f2826605356e849f4e38b70b15a96cf07ffad09e82cd7da80183d00de
```

No historical result was rewritten or reclassified.

## Fixed scenario inputs

The four fresh schema-v11 inputs are:

```text
f654f51a3cc445359b1f94c81512f25471d0c388267126bd8923791a1d2b542b
  phase08_v8_7_primary_repeats.yaml
5c5f40dd77005fea3f44faa1c7f425e709b245ffcd1279f9f7979505d3059910
  phase08_v8_7_primary_visible_probe.yaml
f555b99f892746a9898f9c71c5c428cf2c018ebdca15d9a83deddb764ec2cc8b
  phase08_v8_7_secondary_repeats.yaml
1424eb1ca3823f6481eac46481a7aa08a2480331e4e653313becac44702dba83
  phase08_v8_7_secondary_visible_probe.yaml
```

Pairwise whole-document normalization proves each v8.7/v8.6 pair is exactly
equal after removing only:

- schema version and the new evidence timeout;
- suite, profile, case, contract, experiment, and description identities;
- fresh run root and seeds;
- version-specific operator and reachability prose.

Therefore all source positions and intensities, start poses, topology,
algorithm launch overrides, detector/fill/affine values, Stage A and Stage B
budgets, simulation-only proximity stop, final-zero and cleanup contracts,
and first-failure rules remain unchanged.

The sealed v8.7 dispatches are:

| Gate | GUI | Seeds | Run root |
|---|---:|---|---|
| primary visible | yes | `19501` | `phase08_8_7_primary_probe` |
| primary repeats | no | `19511..19520` | `phase08_8_7_primary_repeats` |
| secondary visible | yes | `19551` | `phase08_8_7_secondary_probe` |
| secondary repeats | no | `19561..19565` | `phase08_8_7_secondary_repeats` |

Every resolved case retains two declared sources, the exact one-fill budget,
the `400/1600` intensities, counted-candidate classification,
candidate-informed fill, approach continuity, active-fill transit,
supervisor-owned assist, affine escape assistance, no operating bounds, no
recenter, no recoverable navigation, no post-recovery guidance, no contacts,
and the simulation-only `0.50 m` evaluator stop.

The physical contract remains coordinate-free and operator-stopped with
`Ctrl+C`.

## Source tests

Final focused controller, supervisor, detector, escape geometry,
modified-cost, search-history, observability, and legacy tests:

```text
305 passed in 8.44 s
JUnit:
  /tmp/phase08_8_m4_8_focused_controller_final.xml
  0508eb23471cfeb5a535a2984aae9a0d47e7b5bbf7b0e8df6ba4fdcba3d0aaba
log:
  /tmp/phase08_8_m4_8_focused_controller_final.log
  190d9cbff40a71f6e2cf5ebc40ccf409de78b2d50df727ba3dd567b7f1b2498a
```

Final focused schema, runner, validator, recorder, bag-analysis,
aggregate-truth, disturbance, shutdown, and evidence tests:

```text
582 passed, 1 skipped in 126.91 s
JUnit:
  /tmp/phase08_8_m4_8_focused_evidence_final.xml
  76f9ded04a528e5c698d4ff52eb7f4183944ae342d94279e9379d528e12ff41e
log:
  /tmp/phase08_8_m4_8_focused_evidence_final.log
  d24b38f8bd327f3289d7c2f55b572760c8219390b75b34078c03d7e36098ca55
```

The one focused skip is the unchanged explicit headless Gazebo end-to-end
opt-in.

Final broad ROS-independent functional regression:

```text
893 passed, 3 skipped in 146.61 s
JUnit:
  /tmp/phase08_8_m4_8_broad_functional_final.xml
  b2d0a0b7303ec61714c410d1900322c4a8618f6146cb934f606fa02e793b5c24
log:
  /tmp/phase08_8_m4_8_broad_functional_final.log
  01d95fd8a046753c73bdcdeb810991abb327fa7cad8302ea04412fbf9c4b9ad6
```

The broad skips are the repository copyright-template check and the two
unchanged explicit visible/headless Gazebo opt-ins. There are no failures or
errors.

The final complete schema/runner subset independently produced:

```text
296 passed, 1 skipped in 55.76 s
JUnit:
  /tmp/phase08_8_v8_7_schema_runner_final.xml
  25d0299e4dffe3e5a0a30bde1516ef3405346c45e83ba8a2e76fd32a3eb0720c
log:
  /tmp/phase08_8_m4_8_schema_runner_final.log
  f5f3d9cb93a04a5b0951131a013193f50ea55c40bba311afb662004d2a538650
```

Changed-file fatal lint (`E9,F63,F7,F82`), changed-Python compilation,
central-launch XML parsing, all four YAML parses, `git diff --check`, and:

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/
  validate_phase_context.sh 08 implement
```

all pass.

## Fresh isolated build and installed graph

The fresh release build used:

```text
root:
  /tmp/phase08_8_v8_7_release_qual.krosar
packages:
  ros_esc_interfaces
  ros_esc
  turtlebot3_rotating_sensor
result:
  3 packages finished in 14.6 s
```

Source/install byte parity passes for `10/10` runtime owners: controller,
scenario runner, scenario schema, supervisor state machine, supervisor
adapter, central launch, and four v8.7 scenarios.

Installed nonexecuting launch checks:

```text
/tmp/phase08_8_v8_7_release_show_args.txt
  d6a5adc86beba6c23bd30f630dd439a4abb8a510ce4c1d8d0b7806718de12162
/tmp/phase08_8_v8_7_release_launch_description.txt
  8287419d96643b6f8c712c08cc03337dacbd9399f113857a6cb696706ff44a92
```

They retain the four open-field arguments, including
`open_field_escape_supervisor_owned_assist_enabled`. The schema-v11 handoff
timeout is absent because it is evaluator-only.

Direct installed construction on isolated ROS domain `230` reached the
expected bounded timeout `124` without startup error for:

```text
default supervisor:
  /tmp/phase08_8_v8_7_release_supervisor_default.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
fully enabled counted-source supervisor with max_fill_clusters=1:
  /tmp/phase08_8_v8_7_release_supervisor_enabled.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
robust affine modified-cost owner:
  /tmp/phase08_8_v8_7_release_modified_cost.log
  95839bfeabadd877d9350363f70f01201e8be2aad29577e295a9c9c7e812bf68
fully enabled robust controller:
  /tmp/phase08_8_v8_7_release_controller_enabled.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

No construction process survived.

## Installed dry-run expansion

All four installed invocations resolve with zero unsupported cases:

| Scenario | GUI | Runs | Seeds | Dry-run SHA-256 |
|---|---:|---:|---|---|
| primary visible | yes | 1 | `19501` | `b6d6b12de5d89911d8462fd1e1e0faa8674111a08d40da42a68be1757e7f8aee` |
| primary repeats | no | 10 | `19511..19520` | `e3f253fe3a78b6c7e00bc158a7c8858e78a3e8c909fc1e9291a4a70f86ce46a1` |
| secondary visible | yes | 1 | `19551` | `f37274e894fc53a2dd1965d4173b2229a33bf0b26784a50c57ead87497961ff3` |
| secondary repeats | no | 5 | `19561..19565` | `8206e64ce6be036b2a1e5e59f2d25edd7a7e2968ddfe59ca89918a4a7b21513d` |

The `17` resolved runs produce `34` launch/record launch-argument occurrences
of the enabled supervisor-owner switch and zero occurrences of the
evaluator-only handoff timeout. All four run roots were absent before and
after dry-run.

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

V6, v8-v8.6, shifted worlds, and every older scenario remain selectable.
Fixed failed evidence remains failed and was not retried or relabeled.

## Bounded qualification corrections

The following pre-runtime issues were corrected and requalified:

- initial causal tests retained old escape geometry/active-fill validity in a
  returned-`SEARCH` fixture and expected pre-v11 failure text; six fixture
  assertions failed until the v11 state contract was represented correctly;
- a second fixture used an assist publication older than the configured
  freshness window; three tests failed until a fresh final assist publication
  was modeled;
- the accepted held-assist tail was strengthened again so that its matching
  final command must itself have matched a pre-exit assist diagnostic;
- the first full schema/runner run ended at `293 passed, 1 failed, 1 skipped`
  because the unsupported-version negative fixture still used newly supported
  schema 11; it now correctly rejects schema 12;
- one build wrapper enabled shell noun checking before sourcing the ROS setup
  and stopped before creating a qualification root; the corrected bounded
  build completed from scratch;
- the first fully enabled supervisor construction omitted
  `max_fill_clusters=1` and correctly failed the counted-source invariant; the
  corrected exact one-fill invocation reached the expected bounded timeout.

Every final test and construction gate above passes. These were bounded
Level B test-fixture or qualification-invocation corrections. No algorithm
motion and no empirical run were affected.

## Runtime boundary

At qualification close:

- no Gazebo, scenario runner, recorder, analyzer, rosbag recorder, controller,
  supervisor, or physical process is active;
- all four v8.7 run roots remain absent;
- no historical input or result is changed;
- the physical contract remains manual operator `Ctrl+C`;
- sealed-run monitoring may use only process state and retained files, never
  a ROS/DDS participant on the run domain.

The next authorized action is the separate dispatch-boundary checkpoint and
commit. After that, the one visible primary seed-`19501` probe may run once.
A behavioral, schema-v11 ownership, recording, final-zero, or cleanup failure
closes that visible gate. A formal pass and all nine analysis plots are
required before any primary repeat is dispatched.
