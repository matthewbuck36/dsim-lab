# Phase 08.8 M4.3 v8.4 no-Gazebo qualification

Date: 2026-07-30 local / 2026-07-31 UTC

## Disposition

**PASS — IMPLEMENTATION QUALIFIED WITHOUT GAZEBO.**

This record qualifies the fresh v8.4 approach-continuity implementation and
its four fixed scenario inputs. It does not claim behavioral success and does
not authorize a repeat population by itself. No Gazebo, recorder, analyzer,
or physical process ran during implementation qualification.

The next authorized runtime action, only after the implementation checkpoint,
bounded commit, and a separate dispatch checkpoint/commit, is one installed
visible execution of:

```text
phase08_v8_4_primary_visible_probe.yaml
seed 19201
```

## Qualified behavior

The implementation adds one default-off parameter:

```text
open_field_escape_approach_continuity_enabled: false
```

When enabled by the fixed v8.4 profile:

1. the supervisor searches its existing ordered odometry history for the
   newest pose strictly outside the accepted fill's frozen exit radius;
2. it freezes the unit vector from that anchor toward the fill center;
3. it selects and revalidates the most aligned existing fill-safe forward
   candidate;
4. `ESCAPE_REPULSE` and `ESCAPE_ASSIST` publish weights
   `(raw, Gaussian, affine) = (0, 1, 1)`;
5. the robust modified-cost owner binds exactly one affine term to the typed
   safe-direction revision;
6. supervisor translation remains zero in `ESCAPE_REPULSE` and uses the
   existing bounded assist command only after measured stall;
7. the escape reset, `SEARCH`, and terminal paths clear the continuity
   evidence, safe direction, and affine authority.

The escape event contains the frozen anchor, age, displacement, exclusion
radius, continuity vector, selected direction, rotation, and revision only
when the feature is enabled. The configuration event likewise appends the new
switch only when enabled. Default-off historical event payloads and state
weights remain unchanged.

The implementation consumes no source position, source role, declared global
coordinate, Vicon pose, room dimension, simulation truth, proximity result,
waypoint, route map, or persistent post-escape direction.

## Exact retained-geometry replay

Pure tests replay the five retained v8.3 primary fill-acceptance geometries.
For every seed, the default-off radial selector retains its pre-v8.4 result,
while the enabled candidate is finite, fill-safe, and in the frozen
approach-direction forward half-plane.

The failed seed `19115` replay also covers the first retained
`ESCAPE_ASSIST` state/odometry sample:

```text
fill center:
  (0.9024309599026483, 1.2748722127037169)
history anchor:
  (0.31732117094725015, 0.03934286786719746)
stall sample:
  (0.8512191620399492, 1.2598740198016434)
old radial direction:
  (-0.9596900358585478, -0.2810605541050169)
enabled fixed-candidate direction:
  (-0.33642414779413166, 0.9417105674149527)
```

The preliminary Plan value `(-0.207, 0.978)` was a continuous-tangent
diagnostic, not one of the executable selector's fixed `45-degree`
candidates. The Plan now records the exact correction. Evaluator-only global
alignment at this exact sample changes from `-0.914` for the old radial
choice to `+0.351` for the enabled choice. No global coordinate enters the
test subject or runtime implementation.

## Fixed scenario inputs

The four source inputs copy v8.3's sources, start, topology, candidate and fill
parameters, detector settings, time budgets, staged acceptance, simulation
proximity stop, cleanup gates, and first-failure rules. Only v8.4 identity,
fresh roots/seeds, and the default-off continuity/affine correction change.

```text
ef822e73c13f1e78d94c60ae10a11438caae8137507aae837495d84109699407
  phase08_v8_4_primary_repeats.yaml
3c876eddb86196b54207204b975f64930bcf8f99697e86f2524fd4168f7e66d8
  phase08_v8_4_primary_visible_probe.yaml
e94241cdea8fdd55000a81eb38de1eab36b80acd413d1313a85aecc78ce400b8
  phase08_v8_4_secondary_repeats.yaml
323f8ceee7d1b8c1275e4ad741edaf46e23d56364543e959c98ae113925e737f
  phase08_v8_4_secondary_visible_probe.yaml
```

Each profile resolves:

```text
known_source_count:                              2
gaussian_fill_max_fills:                         1
candidate_informed_fill_enabled:                 true
operating_bounds_enabled:                        false
open_field_escape_assist_enabled:                true
open_field_escape_approach_continuity_enabled:   true
modified_cost_enable_affine_bias:                true
modified_cost_affine_gain:                       0.50
modified_cost_affine_decay_rate:                 0.0000005
modified_cost_affine_max_age:                    35.0
modified_cost_affine_direction_sign:             1.0
recenter_after_escape:                           false
recoverable_navigation_enabled:                  false
post_recovery_guidance_enabled:                  false
simulation_contacts_enabled:                     false
validation_world:                                false
```

Schema tests prove all continuity dependencies and reject counted affine use
when the new switch is absent. The runner exposes no evaluator-only source
role, global coordinate, or simulation-truth control to the controller.

## Source tests

Final focused controller, geometry, supervisor, modified-cost, observability,
detector, and legacy command:

```text
285 passed in 8.09 s
JUnit:
  /tmp/phase08_8_m4_3_focused_controller_final.xml
SHA-256:
  34696afb6e54ae401e611e1048f93ef430e52e6ed7c71083382d66cef0ea1919
```

Final schema, runner, Phase 08 validator, recording, and analysis command:

```text
504 passed, 1 skipped in 103.05 s
JUnit:
  /tmp/phase08_8_m4_3_focused_evidence_final.xml
SHA-256:
  521d27a11f315a0ba7ac1bdfd642e78d932be0e7256966685f82ee5e6f2bce82
```

The skip is the explicit opt-in recorded headless Gazebo integration:
`RUN_GESC_PHASE06_GAZEBO_E2E=1`.

Final complete ROS-independent functional regression, excluding the
repository's separate style/copyright files:

```text
819 passed, 2 skipped in 137.12 s
JUnit:
  /tmp/phase08_8_m4_3_broad_functional_final.xml
SHA-256:
  c0e1d237a3956382e7020870ea4cf9781166f613cf291b479e44b8f83a9bb8bd
```

The two skips are the unchanged explicit visible-recording and recorded
headless Gazebo opt-ins. There are no failures, errors, or deselections.

Fatal changed-file lint (`E9,F63,F7,F82`), changed-Python compilation, launch
XML parsing, all four YAML parses, `git diff --check`, and:

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/
  validate_phase_context.sh 08 implement
```

all pass.

## Fresh isolated release build and installed graph

The final from-scratch build used:

```text
log:
  /tmp/phase08_8_m4_3_release_qual/log
build:
  /tmp/phase08_8_m4_3_release_qual/build
install:
  /tmp/phase08_8_m4_3_release_qual/install
packages:
  ros_esc_interfaces
  ros_esc
  turtlebot3_rotating_sensor
result:
  3 packages finished in 11.9 s
```

Source/install byte parity passes for `10/10` runtime owners: five Python
owners, four fixed v8.4 scenarios, and the central Gazebo launch.

Installed nonexecuting launch checks:

```text
/tmp/phase08_8_m4_3_release_show_args.txt
  015207ead5446f31c05b132d68d4b9b0c89b5a428a8f07faa8ad7b88cbbe1800
/tmp/phase08_8_m4_3_release_launch_description.txt
  d54fc98b62e79520d12a60be45c973f0b59c4335e06ba833d72cd97f56245c49
```

Both expose and bind the new switch. Direct installed supervisor and
modified-cost construction each reached the expected bounded timeout `124`
without startup errors:

```text
/tmp/phase08_8_m4_3_release_supervisor.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
/tmp/phase08_8_m4_3_release_modified_cost.log
  73b3b0459abdfb056ae5dbeb6ae2284c07b8406d82024303f98097ba13fe6104
```

## Installed dry-run expansion

All planned invocations resolve from the final installed package with zero
unsupported cases:

| Scenario | GUI | Runs | Unsupported | Dry-run SHA-256 |
|---|---:|---:|---:|---|
| primary visible | yes | 1 | 0 | `07f83b8f858c2e0daf9ec53afcf958262feaf647a49545c4e07390da696257e3` |
| primary repeats | no | 10 | 0 | `1a66d32b552ab7c0371f017e53197d4417ac22160134f62034b9ec6253baf43c` |
| secondary visible | yes | 1 | 0 | `bc1fcae3b6cf78afe2a01ea3d9d4b782be91309ccf3f1caa270e80a26988580e` |
| secondary repeats | no | 5 | 0 | `41788fe05be9fee0ce08dcc85549cb47e14b328c54811ebc84045aec96251a49` |

Every resolved case and controller contract has a fresh `v8_4` identity. The
four configured run roots were absent both before and after dry-run.

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

V6, v8, v8.1, v8.2, v8.3, and all older scenarios remain selectable. Fixed
failed evidence remains failed and was not retried or relabeled.

## Bounded qualification corrections

The following issues were found and corrected before any Gazebo dispatch:

- the first compile command named the schema's old path; the corrected
  resolved path compiled;
- the bare shell lacked the recorded ROS/Python test overlay; the qualified
  source-first overlay was restored without installing anything;
- the initial implementation exposed the safe direction and affine
  authorization in `ESCAPE_ASSIST` but not `ESCAPE_REPULSE`; both message
  owners now cover the planned pair of escape states;
- the later staged schema gate still hard-coded affine disabled; it now
  permits affine exactly when approach continuity is enabled and preserves
  the old rejection otherwise;
- copied case/contract labels retained `v8_3`; installed dry-run caught and
  corrected them to fresh `v8_4` identities;
- the preliminary continuous tangent was not an executable fixed candidate;
  the Plan and exact replay now distinguish those values;
- the new switch initially appeared in every configuration event; it is now
  appended only for enabled v8.4 runs, preserving default-off historical
  payloads.

All affected focused, broad, build, parity, instantiation, and dry-run gates
were repeated on the final source. None of these corrections started Gazebo
or altered an empirical result.

## Runtime boundary

This qualification establishes implementation and infrastructure readiness
only. It makes no claim that v8.4 escapes or reaches the second candidate in
Gazebo.

After checkpoint and commit, a separate dispatch boundary may authorize only
the visible primary probe at seed `19201`. A behavioral, evidence, recording,
final-zero, or cleanup failure closes v8.4 immediately. A formal pass is
required before any primary repeat is dispatched.
