# Phase 08.8 M4.7 v8.6 no-Gazebo qualification

Date: 2026-07-31 local and UTC

## Disposition

**PASS — IMPLEMENTATION QUALIFIED WITHOUT GAZEBO.**

This record qualifies the fresh v8.6 supervisor-owned assisted-escape
implementation, schema-v10 evidence contract, and four fixed scenario inputs.
It does not claim Gazebo behavioral success. No Gazebo, scenario execution,
recorder, analyzer, rosbag recorder, or physical process ran during this
qualification.

Only after the implementation checkpoint, bounded implementation commit, and
a separate visible-dispatch checkpoint and commit may one installed visible
execution start:

```text
phase08_v8_6_primary_visible_probe.yaml
seed 19316
```

## Qualified behavior

The implementation adds one default-off parameter:

```text
open_field_escape_supervisor_owned_assist_enabled: false
```

It is valid only with the complete v8.5 counted-candidate,
candidate-informed, approach-continuity, active-fill-transit, open-field
assist contract. When enabled by the fixed v8.6 profile:

1. `ESCAPE_REPULSE` is unchanged: GESC retains actuator ownership, the
   supervisor command is zero, the active typed fill remains in modified
   cost, and the direct revision-one onboard-history direction remains
   latched and revalidated;
2. the existing measured `3.0 s / 0.05 m` radial-stall rule alone enters
   `ESCAPE_ASSIST`;
3. GESC continues to compute and publish its proposal in assist, but the
   controller's authorized unsaturated actuator command is exactly the fresh
   supervisor command rather than `GESC + supervisor`;
4. a zero, stale, missing, nonfinite, or direction-invalid supervisor input
   produces zero/failsafe behavior and never falls back to GESC in assist;
5. `ControlDiagnostics` records the suppressed GESC proposal, the exact
   supervisor-owned combined command, `combined - GESC` as the supervisor
   contribution, and the existing final saturation;
6. the existing supervisor rotates in place until the robot enters its drive
   cone, then commands positive bounded translation along the exact latched
   world-frame direction;
7. the active fill remains excluded only from its own open-field command
   sweep; every other retained fill remains a hard command-sweep constraint;
8. enabled `SEARCH` authorizes GESC directly. This state-bound handoff
   prevents a delayed nonzero assist command on the separate supervisor topic
   from leaking through the first post-exit sample;
9. the first synchronized post-exit evidence must also contain supervisor
   zero, weights `(1, 1, 0)`, no valid safe direction, ordinary GESC
   arithmetic, and valid saturation;
10. terminal, reset, explicit-stop, stale/fault, and missing-history paths
    retain the existing zero-output behavior.

The controller remains the sole `/cmd_vel` publisher. The supervisor still
publishes only `/gesc_gaussian/supervisor_command`; no interface message,
second controller, planner, pose estimator, launch graph, simulation/physical
fork, source coordinate, source role, global coordinate, Vicon pose, room
dimension, or evaluator result was added.

Historical defaults, V6, and every v8-v8.5 scenario retain the prior
combination rule because the new switch defaults false.

## Formal schema-v10 evidence

Schema v10 adds:

```text
supervisor_owned_escape_assist
```

For enabled v8.6 scenarios the predicate gates the full lifecycle and proves,
from recorded supervisor commands, control diagnostics, algorithm state,
escape events, and odometry:

- a complete assisted interval and later `SEARCH` boundary;
- one finite, unit, revision-one direction and one frozen fill center;
- agreement with the preceding `ESCAPE_STARTED` event;
- fresh exact supervisor ownership for every steady assist control sample;
- at least one nonzero suppressed GESC proposal;
- at least one positive supervisor linear command;
- correct contribution arithmetic and final saturation;
- measured fill-to-exit alignment of at least `+0.80`;
- complete return to ordinary affine-free GESC ownership after exit.

The steady ownership interval begins with the first recorded nonzero assist
command. This excludes only the cross-topic transport boundary between the
publisher's first assist state and the controller's receipt of its first
assist command. Once assistance has authority, every control sample is
mandatory. Missing, stale, nonfinite, zero-linear-only, leaked-GESC,
wrong-revision, changed-direction, wrong-exit, or persistent-post-exit
fixtures fail.

Schema validation also requires version 10 when the predicate appears in a
top-level or result-scope `all_of`, requires a Boolean switch, requires
active-fill transit and its prerequisite chain, requires the exact assisted
counted-source state path, and requires `ESCAPE_STALLED`.

## Retained seed-19316 replay

The committed v8.5 failure bag was read only:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_5_primary_repeats/2026-07-31/
  20260731T110116556773Z_simulation_phase08_v8_5_primary_repeats-
  v8_5_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_3d6091a5/
```

The current source with the new switch disabled reproduces the historical
outcome with `outcome_error=None` and no new owner-result key. Pure
arbitration replay of all `2,860` steady assist samples gives:

```text
default-disabled commands equal recorded v8.5 combined command: 2,860
enabled commands equal the recorded supervisor contribution:    2,860
enabled commands suppress a nonzero competing GESC proposal:     2,860
```

Running the new formal predicate against the old v8.5 combined commands
fails, as required:

```text
GESC leaked into the supervisor-owned command
```

Retained replay:

```text
/tmp/phase08_8_m4_7_seed19316_replay.log
SHA-256:
  cfe1f3d17245457cc17e458516f3c324887a270f403b273959588bb518c15ff4
```

## Fixed scenario inputs

Each fresh input is schema version 10. Source declarations, start, topology,
candidate/fill/detector values, affine values, Stage A budget,
simulation-only `0.50 m` evaluator stop, cleanup gates, and first-failure
rules are copied from v8.5. The only behavioral correction is the true owner
switch. Versioned identities, roots, and seeds are fresh; Stage B evidence is
relaxed from `180.0 s` to `300.0 s`, with a `720.0 s` simulation limit and
`900.0 s` wall limit.

```text
641e60c3382afca6b3f499bd1f8abc6609df30eb2dfbbc20793dbfaabab57efe
  phase08_v8_6_primary_repeats.yaml
47faf45f4cd1464dde02e727ea4cfcfc7b7dd77139ac4a355a2366e229884fc9
  phase08_v8_6_primary_visible_probe.yaml
005f1c8c0a631bac66430f28f4cf1a208d4ebc94f71647e462747c569f631a9e
  phase08_v8_6_secondary_repeats.yaml
3cc0679a00a3fcd3a307f4380888b74f1922abcf8f4fc91f125fd0b188177026
  phase08_v8_6_secondary_visible_probe.yaml
```

Every resolved run has:

```text
known_source_count:                                      2
gaussian_fill_max_fills:                                 1
candidate_informed_fill_enabled:                         true
operating_bounds_enabled:                                false
open_field_escape_assist_enabled:                        true
open_field_escape_approach_continuity_enabled:           true
open_field_escape_active_fill_transit_enabled:           true
open_field_escape_supervisor_owned_assist_enabled:       true
modified_cost_enable_affine_bias:                        true
modified_cost_affine_gain:                               0.50
modified_cost_affine_decay_rate:                         0.0000005
modified_cost_affine_max_age:                            35.0
modified_cost_affine_direction_sign:                     1.0
recenter_after_escape:                                   false
recoverable_navigation_enabled:                          false
post_recovery_guidance_enabled:                          false
simulation_contacts_enabled:                             false
validation_world:                                        false
stage_a_timeout_sec:                                     360.0
post_stage_a_timeout_sec:                                300.0
```

The simulation evaluator sees the declared source geometry so it can place
lights and score the run. Launch-contract tests prove source roles, the
declared global coordinate, and evaluator outcomes do not enter controller
arguments. The physical contract remains coordinate-free with manual
operator `Ctrl+C`; it has no Stage B or coordinate-proximity stop.

## Final source tests

Focused state-machine, controller, supervisor, detector, escape geometry,
modified-cost, search-history, observability, and legacy command:

```text
305 passed in 8.35 s
JUnit:
  /tmp/phase08_8_m4_7_focused_controller_final.xml
SHA-256:
  cf1545dfd47072e20b1e0da036ef9970dca15637aafd619478f93e4018f984df
log:
  /tmp/phase08_8_m4_7_focused_controller_final.log
SHA-256:
  4d25aad4b9963a2362872d10f6cf8ee7d56b9358e3a296df272b1a3d3533d8ce
```

Focused schema, runner, Phase 08 validator, recorder, bag analysis, aggregate
truth, disturbance, shutdown, and evidence-support command:

```text
555 passed, 1 skipped in 125.55 s
JUnit:
  /tmp/phase08_8_m4_7_focused_evidence_final.xml
SHA-256:
  8f743f84836158329741945486b1e59b1437a58f92af546608972e1d7cc6b84c
log:
  /tmp/phase08_8_m4_7_focused_evidence_final.log
SHA-256:
  852094d7bd7aa05e19c614e320ff25f53d62f4bd3ad2e8743832f2620bc62996
```

Complete ROS-independent functional regression, excluding the repository's
separate style and copyright files:

```text
866 passed, 2 skipped in 137.56 s
JUnit:
  /tmp/phase08_8_m4_7_broad_functional_final.xml
SHA-256:
  a80a7242ca301d8c92fb971a3ed7a87afbecd5ea1414c7d41b051536f46656bb
log:
  /tmp/phase08_8_m4_7_broad_functional_final.log
SHA-256:
  7f876dc428ff80b44a1773215795af4e40aef6da65b2843184161eb814edcbf1
```

The two broad skips are unchanged explicit opt-ins for a visible Gazebo
recording smoke and a recorded headless Gazebo end-to-end test. The focused
evidence command contains the latter skip. There are no final failures or
errors.

Fatal changed-file lint (`E9,F63,F7,F82`), changed-Python compilation,
central-launch XML parsing, all four YAML parses, `git diff --check`,
historical tracked-scenario byte comparison, and:

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/
  validate_phase_context.sh 08 implement
```

all pass.

## Fresh isolated build and installed graph

The from-scratch release build used:

```text
root:
  /tmp/phase08_8_v8_6_release_qual.qth8ZZ
packages:
  ros_esc_interfaces
  ros_esc
  turtlebot3_rotating_sensor
result:
  3 packages finished in 11.9 s
```

Source/install byte parity passes for `10/10` runtime owners: controller,
scenario runner, scenario schema, supervisor state machine, supervisor
adapter, central launch, and four fixed v8.6 scenarios.

Installed nonexecuting launch checks:

```text
/tmp/phase08_8_v8_6_release_show_args.txt
  c6e6d66ccebf26c77c66a0651621d57e2d846127eb7a1af2c727a9dac1fce25d
/tmp/phase08_8_v8_6_release_launch_description.txt
  226f7ba283a0828fac9b5217d960a78c36370ecdd2542a76498d893e230edbcd
```

Both expose and bind
`open_field_escape_supervisor_owned_assist_enabled`; the installed default is
`False`.

Direct installed construction on isolated ROS domain 229 reached the
expected bounded timeout `124` without startup error:

```text
default supervisor:
  /tmp/phase08_8_v8_6_release_supervisor_default.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
fully enabled v8.6 supervisor:
  /tmp/phase08_8_v8_6_release_supervisor_enabled.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
robust affine modified-cost owner:
  /tmp/phase08_8_v8_6_release_modified_cost.log
  2d97a8a97a14621ad3c33b0a2c1469d744604fb9d568cbf3a8d845667f3a3ac2
fully enabled robust controller:
  /tmp/phase08_8_v8_6_release_controller_enabled.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Installed dry-run expansion

All four planned invocations resolve from the isolated install with zero
unsupported cases:

| Scenario | GUI | Runs | Seeds | Dry-run SHA-256 |
|---|---:|---:|---|---|
| primary visible | yes | 1 | `19316` | `f3bb1abd1f076b8f20719ba5f1707e9b0350e02c4306a8b334b169b60841b90e` |
| primary repeats | no | 10 | `19411..19420` | `d4085ef2ddc8ff37acf86c9efe84107020bfffe6f9864e005cf09ecfcdcf779b` |
| secondary visible | yes | 1 | `19451` | `ac8ecdb1f332f2f6524692d984b43b3d6fabce1ef308f7e02c2db468489ace0f` |
| secondary repeats | no | 5 | `19461..19465` | `222673de6c8be020b49d5a9983332131170d031a5648ceb2b2630820ae3faa31` |

Every one of the 17 resolved cases binds the true owner switch, exact
one-fill budget, two-source count, open-field profile, no contacts, no
operating bounds, no recenter, and no post-recovery guidance. All four run
roots were absent before and after dry-run.

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

V6, v8-v8.5, shifted worlds, and all older scenarios remain selectable.
Fixed failed evidence remains failed and was not retried or relabeled.

## Bounded qualification corrections

The following issues were found and corrected before any Gazebo dispatch:

- compatibility-only pure tests construct controller objects without running
  `__init__`; the new switch lookup now preserves false as the missing-field
  default;
- the unsupported-schema fixture advanced from now-supported version 10 to
  version 11, and one normalized-state-path assertion was corrected to
  support the existing singular fallback;
- retained bag timing showed one publication-to-controller transport sample
  between the first assist state and first nonzero assist command; the formal
  predicate now starts steady ownership at the latter boundary and still
  rejects all 2,860 old leaking samples;
- enabled `SEARCH` now selects GESC directly so cross-topic delivery order
  cannot retain an old assisted command after the state boundary;
- schema-version detection now includes result-scope predicates as well as
  top-level predicates;
- an accidentally broad invocation of the repository style test scanned
  build/install/history and reported 15,087 pre-existing style findings; the
  declared fatal changed-file lint passed and is the applicable gate;
- the first installed-node command selected ROS domain 245, which this Fast
  DDS build rejects before node construction because its maximum is 232.
  The unchanged commands passed on valid isolated domain 229. A retained
  representative of the superseded preconstruction error is:

  ```text
  /tmp/phase08_8_v8_6_superseded_invalid_domain245.log
  75cada17571fecb7109a6f6851d08c4d6ac771a90c171ff677f9eaf34442fdce
  ```

The initial mixed focused run was therefore superseded at `463 passed,
3 failed, 1 skipped`; all corrected targeted tests and every final focused
and broad command pass. These were bounded Level B implementation,
test-fixture, evidence-boundary, or invocation corrections. No empirical run
was affected.

## Runtime boundary

This qualification establishes implementation and infrastructure readiness
only. It does not establish that v8.6 escapes or reaches candidate two in
Gazebo.

At qualification close:

- no Gazebo, scenario runner, recorder, analyzer, rosbag recorder, or physical
  process is active;
- all four v8.6 run roots remain absent;
- no historical input or result is changed;
- the physical contract remains operator `Ctrl+C`, with no physical
  coordinate-distance stop;
- the first visible run remains prohibited until this exact report, live
  status, implementation, and scenarios are checkpointed and committed, then
  a separate dispatch boundary is checkpointed and committed.

A behavioral, formal ownership, recording, final-zero, or cleanup failure in
the one visible seed-19316 probe closes v8.6 immediately. A formal visible
pass with all nine analysis plots is required before any primary repeat is
dispatched.
