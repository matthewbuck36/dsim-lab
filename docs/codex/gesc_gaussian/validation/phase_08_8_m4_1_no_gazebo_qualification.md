# Phase 08.8 M4.1 No-Gazebo Qualification

Date: 2026-07-30
Branch: `feature/gesc-gaussian-robustness-v1`
Base commit: `937c6d441bc3a03c1d160d1d40fac9c0b13ec7db`
Scope: default-off candidate-informed Gaussian-fill amplitude floor

## Result

**PASS — the v8.3 correction is qualified for the required material
checkpoint and bounded commit. This is not a behavioral result. Gazebo remains
prohibited until that checkpoint and commit are complete.**

The sealed v8.2 primary repeat gate proved that the detector retained a
rotation-stable local raw-cost interval while the adaptive fill designer
created only a `0.10`-amplitude fill from its shorter orientation-level sample
window. M4.1 closes that detector-to-fill scale mismatch without adding source
coordinates, source roles, evaluator geometry, Vicon, room geometry,
dead-reckoned routes, affine guidance, recenter, wall behavior, or a second
controller.

No Gazebo, scenario recording, analyzer-on-new-bag, or physical process ran
during this qualification.

## Implemented contract

Both the supervisor and Gaussian node expose:

```text
candidate_informed_fill_enabled
```

Its default is `False`. The Gaussian node additionally exposes:

```text
candidate_informed_fill_amplitude_scale
```

Its default is `1.0`. The v8.3 scenarios opt into `True` and `1.25`
respectively.

For one newly confirmed counted candidate:

1. the existing supervisor still estimates and ranks only
   `CostBreakdown.raw_cost`;
2. the already frozen rotation-stable `CandidateCostSummary` is validated;
3. the existing eight-value convergence snapshot is extended by a versioned
   five-value evidence suffix containing estimate, MAD, uncertainty, lower
   interval bound, and selected rotation count;
4. the Gaussian node accepts that suffix only when its matching opt-in is
   enabled;
5. both nodes reject missing, malformed, nonfinite, nonnegative,
   nonintegral-count, or interval-inconsistent evidence;
6. the fill designer computes:

   ```text
   requested floor = 1.25 * max(0, -candidate_raw_cost_lower)
   applied floor   = min(requested floor, 6.25)
   ```

7. the existing adaptive center, covariance, anisotropy, association,
   validation, escalation, and immutable fill registry remain authoritative;
   and
8. the accepted fill reports the raw-cost evidence, scale, requested floor,
   applied floor, and cap status in existing Gaussian diagnostics.

The historical `ROBUST_FILL_CREATE` header and eight-value payload remain
unchanged when the feature is off. The correction introduces no ROS interface,
topic, sign, unit, node, launch graph, physical/simulation fork, or fill owner.

## Fixed v8.3 profile and scenarios

The corrected profile fixes:

```text
candidate_informed_fill_enabled:          True
candidate_informed_fill_amplitude_scale: 1.25
gaussian_fill_amplitude_max:              6.25
gaussian_fill_sigma_floor_m:              0.50
gaussian_fill_sigma_ceiling_m:            1.25
gaussian_fill_exit_sigma:                 2.70
gaussian_fill_max_fills:                  1
known_source_count:                       2
candidate_cost_required_rotations:        3
candidate_cost_pretrigger_rotations:      6
```

Affine assistance, recenter, operating bounds, post-recovery guidance, and
recoverable navigation remain disabled. Direct
`ESCAPE_REPULSE -> SEARCH` and the existing finite
`ESCAPE_REPULSE -> ESCAPE_ASSIST -> SEARCH` fallback are both valid. The schema
requires exactly those two paths only for opted-in candidate-informed counted
scenarios. Every earlier counted profile retains its original exact
single-path contract and `ESCAPE_STALLED` requirement where applicable.

The four fresh inputs are:

```text
phase08_v8_3_primary_visible_probe.yaml
  seed 19101
  local radius/angle: 1.5 m / 45 deg
  GUI
  1 run

phase08_v8_3_primary_repeats.yaml
  seeds 19111..19120
  local radius/angle: 1.5 m / 45 deg
  headless
  10 runs

phase08_v8_3_secondary_visible_probe.yaml
  seed 19151
  local radius/angle: 1.5 m / 67.5 deg
  GUI
  1 run

phase08_v8_3_secondary_repeats.yaml
  seeds 19161..19165
  local radius/angle: 1.5 m / 67.5 deg
  headless
  5 runs
```

Every case retains the fixed `400/1600` direct-input pair, source count two,
one-fill cardinality, open-field world, disabled contacts, strict raw-cost
ranking, evaluator-only `0.50 m` simulation stop, and physical `Ctrl+C`
contract.

Scenario source SHA-256:

```text
763a3691a37c9705129d371653f362724dd54b47b654b401a8330b339af887b8
  phase08_v8_3_primary_visible_probe.yaml
51456d960af47a1942033e80e38a049a74b848345c091e1cda257b04c0ac30bc
  phase08_v8_3_primary_repeats.yaml
c6db9d0300e17f13cf22d64b7c643ecb57ac1823864ba06193b024f8c70a751c
  phase08_v8_3_secondary_visible_probe.yaml
8a29802c66ffcf1e070e35ae92841b163773663e86240d9772969e44c984e8ba
  phase08_v8_3_secondary_repeats.yaml
```

## Source-tree test evidence

Focused state-machine, detector, supervisor, fill-design, and legacy behavior:

```text
213 passed in 7.34 s
JUnit:
  /tmp/phase08_8_3_focused.xml
SHA-256:
  a5585325a1caca01bc3f0974fc83de872df27a2bc17441e9e5a683a466ed238e
```

Scenario schema, runner, and Phase 08 validator:

```text
403 passed, 1 skipped in 94.30 s
JUnit:
  /tmp/phase08_8_3_scenario.xml
SHA-256:
  1dc086718083595dba6d7cc72e658e7836898b51c1a0a07c8d31ff352c927c15
```

The skip is the explicit Gazebo-only integration at this no-Gazebo boundary.

Bag analyzer and integration:

```text
18 passed in 6.10 s
JUnit:
  /tmp/phase08_8_3_analysis.xml
SHA-256:
  ae5f364b361e0a6520f36443c425f08c71291daf3334a032cd5de341a55907ae
```

The analyzer regression proves that raw `AlgorithmEvent.values` arrays remain
available for the new diagnostic evidence without changing recorded-message
semantics.

Complete ROS-independent functional regression, excluding the repository's
separate style and copyright wrappers:

```text
791 passed, 2 skipped in 135.75 s
JUnit:
  /tmp/phase08_8_3_broad.xml
SHA-256:
  597fdccfaf97c93d6d93b80f77ec14759684cef67f19f5177218aaa682936624
```

The two skips are unchanged environment-conditional Gazebo integrations.

Fatal changed-Python lint (`E9,F63,F7,F82`), changed-Python compilation,
launch XML parsing, all four YAML parses, `git diff --check`, and
`validate_phase_context.sh 08 implement` pass.

## Fresh isolated build and installed graph

The from-scratch build used:

```text
root:
  /tmp/phase08_8_3_release_qual
packages:
  ros_esc_interfaces
  ros_esc
  turtlebot3_rotating_sensor
result:
  3 packages finished in 13.0 s
```

Source/install byte parity passes for all `10/10` final runtime artifacts:
state machine, supervisor adapter, fill designer, Gaussian adapter, scenario
schema, four v8.3 scenarios, and central Gazebo launch.

Installed nonexecuting launch evidence:

```text
/tmp/phase08_8_3_release_show_args.txt
  e9592b80c727a042888e63443eebfa13be58664b39f25271e7e62b8d07a4e67a

/tmp/phase08_8_3_release_launch_description.txt
  ac91e6860962343f87f8b2f7ee6453ffc84c4714a7d668d679dea3b0c3bb14c5
```

Both candidate-informed arguments appear in the installed launch. Direct
installed construction of default and opted-in supervisor and Gaussian nodes
each ran for five bounded seconds, produced no startup error, and ended only
through the expected outer timeout.

The first opted-in supervisor construction command intentionally remained
incomplete because it omitted the existing `max_fill_clusters=1` counted-source
cardinality parameter. The node rejected it before spinning with:

```text
counted-candidate classification requires max_fill_clusters ==
known_source_count - 1
```

The corrected command bound `known_source_count=2` and
`max_fill_clusters=1`, then passed. This was a qualification-command
correction; it did not change source or experimental behavior.

## Installed dry-run evidence

All seventeen planned invocations resolve from the isolated install:

| Scenario | Resolved | Unsupported | Dry-run evidence SHA-256 |
|---|---:|---:|---|
| primary visible | 1 | 0 | `e00fdfcf3d654cef8f411a4b78651a0096d24aea54c3957e60c831d59e1685ff` |
| primary repeats | 10 | 0 | `9538978b2787d09bf0891b830f162e4d12e37932eaf32b74ca69fb145198fe9e` |
| secondary visible | 1 | 0 | `c9014e91c88eae0e8c835218546f2689b47959505f782792a6cf6c1e2dc6a5db` |
| secondary repeats | 5 | 0 | `038fac3c92e9706a8d7aac5d3b06441967cdf3b0e2e4681c148638e4a0f8710e` |

Evidence files:

```text
/tmp/phase08_8_3_primary_probe_dry.yaml
/tmp/phase08_8_3_primary_repeats_dry.yaml
/tmp/phase08_8_3_secondary_probe_dry.yaml
/tmp/phase08_8_3_secondary_repeats_dry.yaml
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

V6 remains selectable. The fixed v8, v8.1, and v8.2 scenarios and their failed
evidence remain unchanged, closed, and excluded from the v8.3 denominator.

## Dispatch boundary

This qualification does not claim local recovery, global convergence, or
repeatability. After the material checkpoint and bounded commit, it authorizes
exactly one installed visible execution of
`phase08_v8_3_primary_visible_probe.yaml`, seed `19101`.

A fixed behavioral, recording, final-zero, evidence, or cleanup failure closes
v8.3 and prohibits its repeats and secondary campaign. A formal visible-probe
pass is the only authorization for the ten primary repeats.
