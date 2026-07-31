# Phase 08.8 M3.2 No-Gazebo Qualification

Date: 2026-07-30
Branch: `feature/gesc-gaussian-robustness-v1`
Base commit: `c11ad74`
Scope: default-off, bounded pretrigger raw-cost ranking correction

## Result

**PASS — M3.2 is qualified for the required material checkpoint and bounded
commit. Gazebo remains prohibited until both are complete.**

The v8.1 primary probe proved that the motion system escaped the local basin,
reached `0.155960 m` from the evaluator global, and encountered the correct
raw-field ordering, but its candidate estimator discarded the repeated
global-basin minima that occurred immediately before convergence
confirmation. This correction retains a bounded raw-cost history across that
detector boundary without changing motion, source count, cost sign, fill
design, strict ranking, or evaluator separation.

No Gazebo, scenario recording, analyzer, or physical process ran during this
qualification.

## Implemented contract

The supervisor now exposes:

```text
candidate_cost_pretrigger_rotations
```

Its default is `0`. The default preserves v8.1, V6, and every historical
profile. A positive value is accepted only in counted-candidate mode and must
be at least `candidate_cost_required_rotations`.

For an opted-in counted-source search epoch:

1. the existing supervisor collects only `CostBreakdown.raw_cost`;
2. each complete sensor rotation contributes its minimum raw cost;
3. only the latest configured number of complete `SEARCH` rotations remain;
4. that bounded tuple freezes on `SEARCH -> VERIFY_EXTREMUM`;
5. the existing post-confirmation verification window must still complete;
6. the configured number of most-negative repeated minima are selected from
   the frozen-plus-verification pool;
7. the existing median, MAD, uncertainty, and strict nonoverlap comparison
   remain authoritative; and
8. all live and frozen history resets on a new search epoch.

The v8.2 profile fixes the values at:

```text
candidate_cost_pretrigger_rotations: 6
candidate_cost_required_rotations:   3
candidate_cost_rotation_period_sec:  3.0
candidate_cost_mad_scale:             3.0
verification_max_sec:                12.0
```

The controller must therefore complete three post-confirmation rotations even
when pretrigger history exists. One isolated strong sample cannot rank a
candidate. The bounded pretrigger horizon is six complete rotations, or
`18.0 s`.

## Evidence and compatibility

Pure state-machine tests prove:

- selecting three repeated strongest minima from a larger bounded pool;
- median/MAD calculation over only those selected rotations;
- complete-window timing;
- reset on backward time and large input gaps;
- rejection of nonfinite or invalid input;
- provenance counts for pretrigger, verification, available, and selected
  rotations;
- invalid configuration rejection; and
- unchanged default-off behavior.

Supervisor adapter tests prove:

- raw cost, not augmented/modified cost, enters both histories;
- the frozen six-plus-verification-three pool produces the intended
  three-rotation estimate;
- event evidence reports all four rotation counts;
- rejected-candidate return to `SEARCH` clears both histories; and
- a default node does not instantiate the pretrigger window.

The launch, scenario schema, scenario runner, and observability tests bind the
new argument end to end. Schema-v8 validation rejects the opt-in outside
counted mode, negative and Boolean values, and a retained count smaller than
the required repeated count.

The change stores no pose, route, basin coordinate, source coordinate,
evaluation role, room geometry, Vicon value, or global identifier.

## Fixed v8.2 scenarios

The fresh versioned inputs are:

```text
phase08_v8_2_primary_visible_probe.yaml
  seed 19001
  GUI
  1 run

phase08_v8_2_primary_repeats.yaml
  seeds 19011..19020
  headless
  10 runs

phase08_v8_2_secondary_visible_probe.yaml
  seed 19051
  GUI
  1 run

phase08_v8_2_secondary_repeats.yaml
  seeds 19061..19065
  headless
  5 runs
```

All retain the v8.1 two-source layouts, `400/1600` inputs, known source count
two, one-fill maximum, qualified dwell, finite outward assist, required staged
path, no contacts, no validation walls, no affine bias, no recenter, no
post-recovery guidance, no recoverable navigation, and evaluator-only
ranked-goal-plus-`0.50 m` simulation stop.

No source coordinate, evaluator role, global coordinate, or proximity target
appears in the supervisor launch arguments. Those values remain confined to
simulation field construction and offline/runtime evaluation.

## Final test evidence

Focused state-machine, detector, supervisor, core, and legacy behavior:

```text
199 passed in 7.24 s
JUnit:
  /tmp/phase08_8_2_focused_final.xml
SHA-256:
  b11b2c7e9fc2d7b53480140be0a33ca11d667aa145ffaee4eb60b6e6951f7125
```

Scenario schema, runner, and Phase 08 validator:

```text
395 passed, 1 skipped in 96.17 s
JUnit:
  /tmp/phase08_8_2_scenario.xml
SHA-256:
  dcd8042885b2a1dd77fb0b045dc05a89054e740cbc4ff4b67ba7086e4a876dc6
```

The skip is the explicit Gazebo-only integration at this no-Gazebo boundary.

Analyzer and candidate-plot tests:

```text
18 passed in 6.29 s
JUnit:
  /tmp/phase08_8_2_analysis.xml
SHA-256:
  629d0481f36c7a3adf2ec568c1fd1cc63c6fb5ec3404a2cadc8233632eabc3a3
```

Complete ROS-independent functional regression, excluding the repository's
separate style/copyright files:

```text
769 passed, 2 skipped in 134.10 s
JUnit:
  /tmp/phase08_8_2_broad.xml
SHA-256:
  2083878c4169171926e310a4e8b36bc0c88dd2d089b6ec63903275d1500634e7
```

The two skips are unchanged environment-conditional Gazebo integrations.

Fatal changed-Python lint (`E9,F63,F7,F82`), changed-Python compilation, launch
XML parsing, all four YAML parses, `git diff --check`, and
`validate_phase_context.sh 08 implement` pass.

## Fresh isolated build and installed graph

The from-scratch build used:

```text
root:
  /tmp/phase08_8_2_release_qual
packages:
  ros_esc_interfaces
  ros_esc
  turtlebot3_rotating_sensor
result:
  3 packages finished in 12.0 s
```

Source/install byte parity passes for `8/8` final runtime owners: the state
machine, supervisor adapter, scenario schema, four v8.2 scenarios, and central
Gazebo launch.

Installed nonexecuting launch evidence:

```text
/tmp/phase08_8_2_release_show_args.txt
  ed13d87d3dea6005b1697a17136f21287823cf9204fe7642d1696fbaaa0499b0

/tmp/phase08_8_2_release_launch_description.txt
  c373685f6c729df3170e110a88a6d89cec0350896a640e50e0f0503328ffd555
```

Both expose the new argument and its supervisor binding. Direct installed
construction of an opted-in supervisor and a default supervisor each ran for
five bounded seconds, produced no startup error, and ended only through the
expected outer timeout code `124`.

## Installed dry-run evidence

All seventeen planned invocations resolve from the isolated install:

| Scenario | Resolved | Unsupported | Dry-run evidence SHA-256 |
|---|---:|---:|---|
| primary visible | 1 | 0 | `f5a9805dd44494c6871e3a01a4edb34e0d8a48cdb0577da50f1ce8b5700347e5` |
| primary repeats | 10 | 0 | `1ed3f5a504e0f7d538e7948326aa43e4c791c578f4dce3ee10530d8f6b27a148` |
| secondary visible | 1 | 0 | `f39b69aa06b662ea7f4a9e853afbc438e187da17ec75344ae60693754a315d2a` |
| secondary repeats | 5 | 0 | `fae1e60b0c1593d95049977afd0337b03137c22f179c340436d638909e3f85c5` |

Evidence files:

```text
/tmp/phase08_8_2_primary_probe_dry.yaml
/tmp/phase08_8_2_primary_repeats_dry.yaml
/tmp/phase08_8_2_secondary_probe_dry.yaml
/tmp/phase08_8_2_secondary_repeats_dry.yaml
```

Dry-run resolution created none of the four declared campaign roots.

## Historical preservation

No historical scenario or world changed. Retained hashes remain:

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

The failed v8 and v8.1 scenarios and evidence remain unchanged and failed. V6
and all historical behavior remain selectable.

## Bounded qualification corrections

- One initial changed-Python compilation invocation used a path relative to
  the wrong working directory and exited before compiling anything. The
  corrected path passed.
- One earlier passing focused run emitted an asynchronous ROS destruction
  warning after pytest had exited successfully. The implicated tests passed
  alone without the warning, and the final complete focused run above passed
  cleanly without it.

Neither item started Gazebo or changed an experiment result.

## Dispatch boundary

This qualification does not claim behavioral success. After checkpoint and
commit, it authorizes exactly one installed visible execution of
`phase08_v8_2_primary_visible_probe.yaml`, seed `19001`.

A fixed behavioral, recording, final-zero, evidence, or cleanup failure closes
v8.2 and prohibits its repeat and secondary campaigns. A formal pass is the
only authorization for the ten primary repeats.
