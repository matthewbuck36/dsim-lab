# Phase 08.8 M8.2 v8.11 No-Gazebo Qualification

Date: 2026-07-31 local and UTC

## Disposition

**PASS — THE SCHEMA-V14 TOPOLOGY-BOUND EVALUATOR, THREE FRESH V8.11
INPUTS, RETAINED-BAG REPLAY, REGRESSION ENVELOPE, AND FRESH ISOLATED
INSTALL ARE QUALIFIED WITHOUT GAZEBO.**

This is an evaluator correction and experiment-definition milestone. It is
not a new behavioral result and does not reclassify the fixed v8.10
secondary failure. No v8.11 Gazebo process is authorized until this record,
the live Phase 08 status, and the material checkpoint are committed, followed
by a separate committed dispatch boundary for visible seed `19901`.

## Qualified implementation

Schema version `14` adds one evaluator-only
`success.staged_recovery.topology_qualification` contract for the existing
counted-candidate `verified_trap` association mode. The record is recomputed
at scenario resolution and binds:

- exactly two unique, positive, finite source inputs;
- the local and global evaluator source identifiers;
- source-list, start, bounds, disturbance, light-model, sensor-transform,
  and sensor-geometry SHA-256 values;
- deterministic yaw-resolved local and global basin solutions;
- local ring depth, raw-cost ordering, basin separation, and route geometry;
- every frozen topology threshold; and
- one canonical result SHA-256 over the complete record.

The shared live/offline Stage A owner continues to require one complete
recovery episode, one unique convergence, exactly one created/typed/active
fill, fill-to-convergence distance at most `0.50 m`, convergence at least
`0.75 m` from the declared global, no second fill, later strict raw-cost
ranking, and post-Stage-A global proximity. Individual local-lamp distance is
retained as a diagnostic and is not a `verified_trap` gate.

The scenario runner adds only a concise topology summary to Stage A evidence.
The full record is not forwarded into the launch graph. Tests prove that no
topology hash, source-list hash, source coordinate, intensity, evaluator role,
or global stop coordinate is added to controller launch arguments. The only
source-count controller input remains `known_source_count=2`.

Schema versions `1..13` retain their prior normalization and evaluation
semantics. No controller, supervisor state machine, detector, Gaussian-fill
owner, affine term, modified-cost equation, raw-cost ranking, motion
parameter, launch graph, world, recorder, analyzer, or physical path changed.

## Frozen topology thresholds

```text
source count:                              exactly 2
source input:                              finite and > 0
local search half-width:                   0.40 m
local grid points per axis:                9
local yaw spacing:                         5 degrees
local ring radius / samples:               0.50 m / 48
ring yaw spacing:                          2 degrees
minimum noise-adjusted basin depth:        0.05 raw-cost units
local source-score upper bound:            < 0.95
global source-score lower bound:           >= 0.95
minimum raw-cost separation:               0.05
minimum basin-center separation:           1.00 m
maximum start-to-local distance:           1.75 m
minimum global distance advantage:         1.50 m
minimum forward alignment:                 0.80
evaluator valid-domain wall margin:        0.35 m
```

The wall margin is a topology-preflight domain bound only. It is not a wall
avoidance controller, collision guarantee, or physical operating limit.

## Bounded implementation corrections

Two corrections were made before any Gazebo execution:

1. The initial deterministic grid plus differential-evolution search could
   miss a narrow sensor-centered basin. The evaluator now includes
   deterministic source-aligned sensor poses in the candidate set and selects
   the best finite candidate. All five unique planned layouts and the retained
   primary layout then passed the frozen topology gates.
2. Final contract review found that start and bounds values were protected by
   the overall result hash but lacked the separately named SHA-256 fields
   promised by the Plan. Explicit `start_sha256` and `bounds_sha256` fields
   were added, all six embedded topology records were regenerated, and
   positive and binding-drift tests were expanded.

Neither correction changes controller inputs or motion behavior.

## Fresh fixed scenarios

```text
ce6b80c83cd52b5e665d22bc2867b1a8046d6c6a817f8427dd94ea062a9b76c0
  phase08_v8_11_secondary_visible_probe.yaml
01466b3c350b4e37693eaffb0c40fe15591d28a8d09ee14f4b60aa00f200ce1d
  phase08_v8_11_secondary_repeats.yaml
b0ac9ff6582deecb56970d38f0a3f7d08f09aa8518343dd0477ae953d2a04b02
  phase08_v8_11_broad_matrix.yaml
```

The six resolved topology bindings are:

| Case | Topology SHA-256 | Basin depth | Raw separation | Basin separation m | Alignment |
|---|---|---:|---:|---:|---:|
| secondary visible/repeats | `eb749f0cb86f7b35231bdc308365f3008c6168df07b0188c03a97f339f364d71` | 0.859534 | 0.988770 | 3.644390 | 0.851271 |
| seed 19931, r1.25 a45, 1:3 | `da4e64008b2950c93ccbf08e31b6ead65c4fe6cc5791991965b9ceb156006bd6` | 0.877091 | 0.646477 | 3.613011 | 1.000000 |
| seed 19932, r1.50 a45, 1:5 | `14f52589f05b2dc62f8b12122f823fb97b8e897b304462e37087c1100944560c` | 0.869019 | 1.263855 | 3.363033 | 1.000000 |
| seed 19933, r1.50 a60, 1:3 | `faafb05e4b004ef7d444c56badec3ea55f88107fcd052fef8c094782e7a82e26` | 0.774585 | 0.646162 | 3.812557 | 0.931514 |
| seed 19934, r1.75 a60, 1:5 | `47dd95926a4c9345770a0303ac83287c1f26a41afee108e6c6dc5d089e36837b` | 0.922126 | 1.263460 | 3.213722 | 0.921108 |

All cases retain the v8.10 controller profile, open-field assumptions,
`720.0 s` simulation bound, `900.0 s` wall bound, evaluator-only `0.50 m`
post-recovery stop, final-zero, scoped cleanup, recording, and plot contract.

## Retained-bag replay

The final replay opened all bags read-only:

```text
/tmp/phase08_8_v8_11_retained_replay.log
SHA-256:
  7a5c1b9ab3a3fe9e855b82ae625a7ee24e1f982754369b7e3152aa04b9f1a212
```

Results:

```text
retained primary visible + repeats:  11/11 PASS
retained secondary seed 19851:        replay PASS
total:                                12/12 PASS
unique topology records:              2
historical results changed:            false
```

For all twelve bags, the replay proves controller goal, simulation truth,
Stage A, exact one-fill cardinality, strict counted-candidate ranking,
post-recovery proximity, and no outcome error. The retained primary topology
hash is:

```text
d15b32fc048195900fd6f2d2633cc48793a81e433f9257ecbcbcabc823c88ca2
```

Seed `19851` specifically reports:

```text
historical formal result:                 failed and unchanged
v8.11 read-only replay:                   PASS
convergence-to-declared-local diagnostic: 0.757061 m
declared-local distance gate applied:     false
fill-to-convergence:                       0.007887 m
final global distance:                    0.105549 m
```

The original v8.10 runner did not perform a graceful Stage B proximity stop,
so its immutable formal failure is not relabeled.

## Source tests

Final topology/schema/runner focus:

```text
387 passed, 1 skipped in 134.73 s
JUnit:
  /tmp/phase08_8_v8_11_focused.xml
  ccd4b0139d6886ffd58a9eb77781237345f5749e144f3b819c198975da8ac1e3
log:
  /tmp/phase08_8_v8_11_focused_final.log
  4ab95b59d939797fc508aad8475ff1e5de07c9d71b44fd996b5d8fb5e864beb7
```

Controller, supervisor, detector, escape, modified-cost, search-history,
observability, controller-spawner, and legacy focus:

```text
310 passed in 8.42 s
```

Runner, schema, validator, recorder, analyzer, aggregate-field, disturbance,
and shutdown focus:

```text
663 passed, 2 skipped in 165.64 s
```

The first final broad invocation completed `972` passes and three expected
skips but reported two late supervisor-integration timing failures. Those
same tests passed `2/2` immediately in isolation and the complete supervisor
integration file passed `60/60`. The exact broad suite was then rerun on a
sealed localhost DDS domain and passed completely:

```text
974 passed, 3 skipped in 185.74 s
JUnit:
  /tmp/phase08_8_v8_11_broad_functional_rerun.xml
  71ab62703a0d24bcb3f6f5cf79ddc532c636ddff99d58278c3d0adc30a6466ac
log:
  /tmp/phase08_8_v8_11_broad_functional_rerun.log
  e25f243c4a8e041125d31b5d8517c1a27f8c62721081e3ff29b05d2a35c8f4fa
```

The failed invocation is retained at:

```text
/tmp/phase08_8_v8_11_broad_functional.xml
  b6241a6d283f8af34e61bbaca0ea104c418b2da1b8243c37ee33d7b3f4f8ac0e
/tmp/phase08_8_v8_11_broad_functional_final.log
  a4b2cbf454102c179880265bb1b48747564c1c0740f0ca04c86d9beb87a85b37
```

This is classified as DDS/process-order test flakiness, not a functional
regression, because both exact failures, the complete owning file, the prior
focused controller envelope, and the sealed full rerun pass without a source
change.

The broad skips are the unchanged copyright-template check and two explicit
Gazebo opt-ins. Fatal changed-file lint `E9,F63,F7,F82`, Python compilation,
three YAML parses, four XML parses, `git diff --check`, and Phase 08 implement
context all pass. Full changed-file `ament_flake8` reports only the inherited
`D202` at `run_scenario.py:2447`, whose function predates this diff.

## Fresh isolated build and installed graph

```text
root:
  /tmp/phase08_8_v8_11_release_qual.AdUc5v
build result:
  3 packages finished in 11.5 s
build log:
  /tmp/phase08_8_v8_11_build.log
  7c7c735990589798cf076ebdab674b7bbdf7b68b0d24f1b85e2f9daf2ddfd102
source/install byte parity:
  10/10 PASS
installed schema:
  14, supported 1..14
```

Nonexecuting installed launch construction passes:

```text
/tmp/phase08_8_v8_11_release_show_args.txt
  6767727b287980df76daa5e79aac985c38d8e89622d8389aa2a979f8ef64156a
/tmp/phase08_8_v8_11_release_launch_description.txt
  00888238784b35568a4312e60d31bba0bd60b90ba647b83e19ad4bd6ddf3e268
```

Direct installed construction used isolated domains `229..232`. The default
supervisor, fully enabled counted-source supervisor with
`max_fill_clusters=1`, robust affine modified-cost owner, and fully enabled
robust controller all reached the expected bounded timeout `124` without a
startup error. No child survived.

Three qualification-command issues were corrected without source changes:

- setting `PYTHONNOUSERSITE=1` hid the repository's existing
  `extremum_seeking` user-site path; the normal qualified runtime environment
  imported the isolated `ros_esc` package correctly;
- the first enabled-supervisor command omitted the existing
  `candidate_informed_fill_enabled=true` invariant required by approach
  continuity; the corrected complete command constructed successfully; and
- SIGTERM made the modified-cost executor print an external-shutdown
  traceback; a bounded SIGINT rerun produced only its two normal startup
  messages.

## Installed dry-run expansion

All installed runners were invoked from `/tmp`; no source package shadowing
or run-root creation occurred.

| Input | Runs | Seeds | Unsupported | Evidence SHA-256 |
|---|---:|---|---:|---|
| secondary visible | 1 | `19901` | 0 | `a785261fca9e1fcafc435343b979a16d628b1ecd3f22b0ed585ba27cdf557d4e` |
| secondary repeats | 5 | `19911..19915` | 0 | `9126a369c2c952232c2def0f57150b973152b50e3075edb52253d93b8ce421e0` |
| broad matrix | 4 | `19931..19934` | 0 | `77b1152a663f4093422eaec7bd3aff2fc76ddc4d2da174f16e67f4d92ca50e51` |

All ten case keys are unique and deterministic. Visible GUI mode is true only
for seed `19901`; repeats and matrix cases are headless.

## Historical preservation

All `94/94` scenario files tracked at Plan HEAD `e39ef24` match their Git
bytes. The three v8.11 files are additive. Retained anchors remain:

```text
gazebo_empty.world:
  3085542f9dc1d13fdf9368a24808a226908d1a2c5a7a4ffd07bc6f374ca14b43
gesc_gaussian_validation.world:
  8ecc1a231efec24401d74fef3cd5139d48c6029f88e71d044cefdf2fd14c5bef
gesc_gaussian_corner_origin_validation.world:
  88b10b39aa24a6430f6f031c750334ed34e6835e54c84de8d36f4cc6a26444bf
phase_08_v6_selection.json:
  dcdbf937fe3de0cab9449c2b01af79fd938e1d3f9791b4897937875d0747590d
v8.10 fixed secondary summary:
  6857aaa727b63079aa3910ecbdd110f51ae9dc68f5a9b63295358d7976d1f4e1
v8.10 fixed secondary scenario_result.yaml:
  0a1e643ab211835053731e60fd7e0c5b6b9af1a4d35fd1680d1bc363ac8660a7
```

V6, shifted worlds, all historical scenarios, results, failures, bags,
reports, and plots remain unchanged and selectable.

## Runtime boundary

At qualification close:

- no Gazebo, scenario runner, recorder, analyzer, rosbag recorder,
  controller, supervisor, or physical process is active;
- all three fresh v8.11 run roots are absent;
- no analyzer ran and no new plot or behavior claim was produced;
- simulation stopping remains evaluator-only after valid recovery and strict
  ranking; and
- physical arrival remains manual operator `Ctrl+C`, with no coordinate stop
  in the physical controller.

The next action is the Phase 08 implementation checkpoint and commit. A
separate checkpointed and committed boundary must then authorize only the
installed visible seed `19901` dispatch.
