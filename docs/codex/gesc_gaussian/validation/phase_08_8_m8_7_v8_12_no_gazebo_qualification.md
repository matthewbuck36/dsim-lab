# Phase 08.8 M8.7 v8.12 No-Gazebo Qualification

Date: 2026-07-31 local and UTC

## Disposition

**PASS — THE LEGACY-DEFAULT-OFF INTERIOR APPROACH-ANCHOR FALLBACK, TWO
FRESH V8.12 INPUTS, RETAINED V8.11 REPLAY, REGRESSION ENVELOPE, AND FRESH
ISOLATED INSTALL ARE QUALIFIED WITHOUT GAZEBO.**

This is an implementation and experiment-definition milestone, not a new
behavioral result. No v8.12 Gazebo process is authorized until this report,
the live Phase 08 status, and the material checkpoint are committed. A
separate committed boundary must then authorize only visible seed `20001`.

## Qualified correction

The supervisor now has two shared-node parameters:

```text
open_field_escape_interior_anchor_fallback_enabled:       false
open_field_escape_interior_anchor_min_displacement_m:     0.50
```

The original three-argument helper path and all historical scenarios keep the
fallback disabled. The original newest pose strictly outside the frozen fill
exit radius remains the first-choice anchor and is labeled `outside_radius`.
Only when no such pose exists and the option is explicitly enabled may the
helper select the farthest finite pose in its existing odometry history,
resolve an exact-distance tie to the earliest sample, require the configured
minimum displacement, and label the result `interior_farthest`.

Empty, nonfinite, unordered, degenerate, and below-minimum histories remain
failsafe. The enabled mode is allowed only with counted-candidate recovery,
candidate-informed fill, open-field approach continuity, active-fill transit,
supervisor-owned assist, affine assistance, and a schema-v14 topology record
whose declared start-to-local route is at least the fallback minimum.

The supervisor's existing safe-direction, repulse, stall, transit, assist,
ordinary-GESC handoff, raw-cost ranking, Gaussian-fill memory, and final-zero
owners are unchanged. The enabled `ESCAPE_STARTED` event adds one numeric
field:

```text
approach_corridor_anchor_mode: 0 outside_radius / 1 interior_farthest
```

The schema-v14 evaluator validates the complete anchor geometry inside the
existing `escape_command_ownership` predicate. The optional
`success.controller.expected_approach_anchor_mode` field is acceptance
metadata only and is never rendered into launch arguments.

No source coordinate, source role, intensity, declared global, topology hash,
room map, Vicon/GPS value, wall sensor, or evaluator proximity coordinate was
added to the controller. Physical arrival remains manual operator `Ctrl+C`;
the simulation-only post-recovery proximity stop is unchanged.

## Critical retained geometry

The exact v8.11 seed-`19931` geometry is covered by a source fixture:

```text
fill center:                  (1.0699606541859803, 0.7605913520944112) m
frozen exit radius:          1.3667708293638696 m
farthest retained pose:      (-0.0019376353428124755,
                              -0.0021311540019673843) m
farthest displacement:       1.3155651121858971 m
direction toward fill:       (0.8147816323190298,
                               0.5797679636160810)
default-off result:          no evidence
enabled result:              interior_farthest
minimum displacement:        0.50 m
```

The fixture also proves the historical outside-radius branch retains priority
when both policies could otherwise supply evidence.

## Fresh fixed inputs

```text
d4607649546f8301112a0cbbb5ded10a2a167146efed143dbfff64e4d5810c65
  phase08_v8_12_interior_anchor_visible_probe.yaml
311667e8c8d330732ea32c894bb78fed43b63cd23ef86f486ca25c86fe727bdc
  phase08_v8_12_broad_matrix.yaml
```

Installed dry-run resolution is deterministic:

| Input | Seed | Case key |
|---|---:|---|
| visible | `20001` | `5d8ed8295d910a52c28561e7d9f8172cb63d7158debef9eb7597b8befe285dbb` |
| matrix | `20031` | `331c7bd7aca41ef2373d6c58300d8073b5185a4c9195254754709c6dfe86c868` |
| matrix | `20032` | `941720dabb4f49053e87ec64b2ba597003aee436bda1855e70032448da25db40` |
| matrix | `20033` | `14dde5e389e4e6b767d93a34210633bbf76744c6d8b9fb49d3046a94b2160573` |
| matrix | `20034` | `4e8006c1d102711de1cc31839cf0280ab3927a61f4a19bb75f9fd38e4e63ac64` |

The visible input alone freezes `interior_farthest`; the varied matrix accepts
either fully evidenced mode. All five cases keep known source count two,
obstacle-free zero-disturbance simulation, one-fill cardinality, strict later
raw-cost ranking, the evaluator-only `0.50 m` post-recovery proximity stop,
complete recording, final zero, scoped cleanup, and one-time/no-retry rules.

## Source qualification

Focused helper, state-machine, supervisor, and observability tests:

```text
240 passed in 6.55 s
```

Schema focus:

```text
198 passed in 74.83 s
```

Final schema and runner focus after adding both fresh inputs:

```text
396 passed, 1 skipped in 115.78 s
```

The sealed ROS-independent functional command was:

```text
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
cd ros2_ws
ROS_DOMAIN_ID=218 ROS_LOCALHOST_ONLY=1 \
PYTHONPATH="$PWD/src/ros_esc${PYTHONPATH:+:$PYTHONPATH}" \
python3 -m pytest -q src/ros_esc/test \
  --ignore=src/ros_esc/test/test_flake8.py \
  --ignore=src/ros_esc/test/test_pep257.py \
  --junitxml=/tmp/phase08_8_v8_12_broad_functional_valid.xml
```

Result:

```text
1012 passed, 3 skipped in 221.91 s
log:
  /tmp/phase08_8_v8_12_broad_functional_valid.log
  897b95d27645bd2f8686ddc3d92b155b830892519b76efd18734fd54161aff93
JUnit:
  /tmp/phase08_8_v8_12_broad_functional_valid.xml
  36eab346ed947136ee8f344f881f60e9e6ee74608fc72e18d092b7d033c4ab9a
```

The three skips are the unchanged copyright-template check and two explicit
Gazebo opt-ins. Fatal changed-file lint `E9,F63,F7,F82`, Python compilation,
both fresh YAML parses, all relevant package XML parses, `git diff --check`,
and Phase 08 implement context pass.

Package-style `ament_flake8` over all eleven changed Python files remains a
non-gating historical-style signal: it reports `1,311` findings (`1,273`
quote-style, `30` docstring-style, and `8` import-order) across owners that
already use mixed historical conventions. The required fatal-code selection
is clean:

```text
/tmp/phase08_8_v8_12_ament_flake8_changed.log
  f2cdc08b7790de46ab7455a35d53eb498d558894cba214a47086bde469a27874
/tmp/phase08_8_v8_12_fatal_changed_flake8.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Retained-bag replay

All six passing v8.11 secondary bags and failed seed `19931` were opened
read-only with the current source evaluator. Every recomputed outcomes mapping
equals its stored historical mapping:

```text
seed 19901: historical PASS / replay unchanged
seed 19911: historical PASS / replay unchanged
seed 19912: historical PASS / replay unchanged
seed 19913: historical PASS / replay unchanged
seed 19914: historical PASS / replay unchanged
seed 19915: historical PASS / replay unchanged
seed 19931: historical FAIL / replay unchanged
total:      7/7 PASS
```

Evidence:

```text
/tmp/phase08_8_v8_12_v8_11_retained_replay.log
  aa32bf1b80b891274d304b6453d5a0fa6a62a572aa4a9c7185897caeaee57bdd
```

V8.11 seed `19931` remains failed and is not retried, relabeled, or counted as
a v8.12 result.

## Fresh isolated build and installed graph

```text
root:
  /tmp/phase08_8_v8_12_release_qual.HnEptF
build result:
  3 packages finished in 11.9 s
build log:
  /tmp/phase08_8_v8_12_build.log
  d03b669b137789b3c47ab5350b2fc090db6eb53fda381bd1e5f35395c745c8b3
source/install byte parity:
  8/8 PASS
installed import:
  /tmp/phase08_8_v8_12_release_qual.HnEptF/install/ros_esc/
  lib/python3.10/site-packages/ros_esc/__init__.py
installed schema:
  14, supported 1..14
```

Nonexecuting installed launch checks pass:

```text
--show-args:
  /tmp/phase08_8_v8_12_release_show_args.txt
  d34abf05d56221732de8fef76f87df4b9084a85b8a7ddd77ea5079bbd3df577a
--print-description:
  /tmp/phase08_8_v8_12_release_launch_description.txt
  6e31ae0648436c5e8e3a779f48a5f8cf9732cc3191d1cefdf5399f7d6e663b9e
```

Direct installed construction used isolated localhost domains `204..207`.
The default supervisor, fully enabled counted-source v8.12 supervisor,
affine-enabled modified-cost node, and robust controller each reached the
expected bounded timeout `124` without a startup error. No child survived.

Installed runners were invoked from `/tmp` with the isolated install first in
the overlay and no source-worktree `PYTHONPATH`:

| Input | Runs | Seeds | Unsupported | Evidence SHA-256 |
|---|---:|---|---:|---|
| visible | 1 | `20001` | 0 | `db4b5cd2bc47ee4a02f0fe2ef391f1d0b38a6306cc798a1da6b3cd024990b1bc` |
| matrix | 4 | `20031..20034` | 0 | `1dd8ef23f02c1268ad4f53f724a2ceca4f8e4b1f73ff17c42bda9b9314260f52` |

Dry-runs created neither fresh run root.

## Historical preservation

All `97/97` tracked scenario files at Plan HEAD `7c9d5e9` match their Git
bytes. The two v8.12 inputs are additive. Three retained v8.11 run roots
contain `248` files; every result, bag, completeness record, summary, report,
analysis, and plot was hashed read-only.

```text
historical scenario manifest:
  /tmp/phase08_8_v8_12_historical_scenarios.sha256
  0397b83e6fef5428f9d1a72b32b3e58e702b1aa9071dba0f7e77a09bf1905ad1
v8.11 artifact manifest:
  /tmp/phase08_8_v8_12_v8_11_artifacts.sha256
  b1dac9c277c26b7e874259b5645810090ce6990c514e22e3cc3e2dcaa9ddb1e0
anchor manifest:
  /tmp/phase08_8_v8_12_historical_anchors.sha256
  976d4a21b98b6bfbc56deaee1bc575db65b7a763cc2daabfa90d39c7fc12162d
```

Retained anchor hashes remain:

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

V6, shifted worlds, every historical scenario, result, failure, run, bag,
report, and plot remain unchanged and selectable.

## Corrected qualification-command issues

The following command issues produced no source or runtime change and are not
acceptance evidence:

- `pytest` was not directly installed on `PATH`; `python3 -m pytest` was used.
- an initial context command used a stale script path; the repository owner
  `DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/
  validate_phase_context.sh 08 implement` passed;
- the first unfiltered broad run included the repository-wide flake8 and
  pep257 collectors and therefore reported those two known style failures;
- two functional attempts used invalid DDS domain IDs `233` and `234`, which
  made the middleware exit at the first ROS node test after 48 pure tests;
  a valid-domain boundary run passed `14/14`, followed by the sealed full pass
  on domain `218`;
- Bash undefined-variable mode was removed before sourcing the standard ROS
  setup scripts, after which the isolated build passed;
- an installed diagnostic first referenced the wrong schema constant name;
  the corrected import proved schema `14`; and
- the first installed node helper passed no required positional arguments to
  modified-cost or controller and then printed an invalid aggregate line.
  That line is discarded. The strict sealed four-node rerun supplied the
  launch-equivalent positional arguments and passed `4/4`.

No Gazebo, analyzer, scenario runner, recorder, or physical hardware was
started by any correction.

## Runtime boundary

At qualification close:

- no Gazebo, scenario runner, recorder, analyzer, rosbag recorder,
  controller, supervisor, or physical process is active;
- both fresh v8.12 run roots are absent;
- no analyzer ran and no v8.12 plot or behavioral claim exists yet;
- simulation stopping remains evaluator-only after complete recovery and
  strict ranking; and
- physical arrival remains manual operator `Ctrl+C`, with no coordinate stop
  in the physical controller.

The next action is the Phase 08 implementation checkpoint and commit. A
separate checkpointed and committed boundary must then authorize exactly one
installed visible seed-`20001` dispatch.
