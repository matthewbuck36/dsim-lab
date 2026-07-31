# Phase 08.8 M4.9 v8.8 no-Gazebo qualification

Date: 2026-07-31 local and UTC

## Disposition

**PASS — SCHEMA-V12 CAUSAL ASSIST-ENTRY EVIDENCE AND THE FOUR FRESH
V8.8 INPUTS ARE QUALIFIED WITHOUT GAZEBO.**

This record qualifies only the v8.8 evidence correction and fixed scenario
inputs. It does not claim a new Gazebo behavior result. No Gazebo, scenario
execution, recorder, analyzer, rosbag recorder, or physical process ran
during this qualification.

The first possible runtime action remains the single installed visible
primary probe:

```text
phase08_v8_8_primary_visible_probe.yaml
seed 19601
```

It remains prohibited until this implementation, report, live status, Phase
08 checkpoint, and implementation commit pass, followed by a separately
checkpointed and committed dispatch boundary.

## Qualified correction

V8.8 changes no controller, supervisor, convergence detector, Gaussian-fill
owner, modified-cost owner, launch graph, world, source field, motion,
candidate-ranking, timeout, stop, final-zero, or cleanup behavior. It adds
schema 12 support and changes only the evaluator's assist-entry
cross-topic-ordering interpretation.

The current schema constant and supported set are now:

```text
SCHEMA_VERSION:             12
SUPPORTED_SCHEMA_VERSIONS:  1 through 12
```

Schema versions through 11 retain the exact previous entry behavior. Schema
12 retains all prior assist geometry, direction, measured exit, positive
translation, GESC suppression, freshness, arithmetic, saturation, returned
state, returned command, and causal exit requirements. At entry, before the
first supervisor-owned diagnostic, it permits only:

- finite ordinary GESC with zero supervisor contribution and a fresh zero
  supervisor command; or
- finite zero/failsafe output with valid contribution arithmetic and a fresh
  zero supervisor command.

It then requires supervisor-only ownership within the existing evaluator-only
`0.15 s` handoff bound and uninterrupted supervisor-only ownership through
escape completion. It still rejects:

- GESC plus a nonzero supervisor command;
- an unknown transition or missing/stale zero-command support;
- nonfinite, arithmetic, or saturation corruption;
- missing or late supervisor ownership; and
- any fallback after ownership is established.

The new evidence fields are:

```text
assist_entry_transition_control_sample_count
assist_entry_first_owned_control_bag_stamp
assist_entry_handoff_delay_sec
assist_entry_handoff_timeout_sec
assist_entry_steady_owned_control_sample_count
assist_entry_handoff_evidence_mode
```

The existing post-exit evidence remains
`bounded_causal_schema_v11`; v8.8 does not alter it.

## Retained seed-19514 causal replay

The immutable failed v8.7 bag was read only:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_7_primary_repeats/2026-07-31/
  20260731T135855335566Z_simulation_phase08_v8_7_primary_repeats-
  v8_7_primary_repeat_r1p5_a45_h25-robust_gaussian_v1_238e5bb0/
```

Its original schema-v11 interpretation remains failed:

```text
passed:        false
reason:        GESC leaked into the supervisor-owned command
outcome_error: null
```

The same immutable message records evaluated through the schema-v12 fixture
pass:

```text
recorded nonzero authority stamp:    1785506493837615474
first owned diagnostic stamp:        1785506493851741071
entry handoff delay:                 0.014125597 s
entry handoff bound:                 0.15 s
ordinary transition diagnostics:    1
steady supervisor-owned diagnostics: 2,678
fresh supervisor samples:            2,678
suppressed nonzero GESC samples:      2,678
positive linear supervisor samples:  2,109
post-exit handoff delay:              0.006192330 s
post-exit ordinary diagnostics:       14,339
fill cardinality:                     pass
Stage A:                              pass
Stage B:                              pass
outcome_error:                        null
```

The entry arithmetic is:

```text
1785506493851741071 - 1785506493837615474
= 14,125,597 ns
= 14.125597 ms
```

The earlier `13.125597 ms` transcription in the committed v8.7 report, Plan,
and status is corrected as an arithmetic erratum. No retained sample,
predicate, pass/fail disposition, or timeout comparison changes.

Replay artifact:

```text
/tmp/phase08_8_m4_9_seed19514_causal_entry_replay.log
SHA-256:
  516b543b578c97f1e6a79971d11c024e43559f3c7eca49ed15ac6c530f7efb54
```

No historical result was rewritten or reclassified.

## Fixed scenario inputs

The four fresh schema-v12 inputs are:

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

Whole-document normalization tests prove every v8.8/v8.7 pair is equal after
changing only schema/evidence version identities, descriptions, run roots,
and fresh seeds. The retained v8.7 hashes remain:

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

The sealed v8.8 dispatches are:

| Gate | GUI | Seeds | Run root |
|---|---:|---|---|
| primary visible | yes | `19601` | `phase08_8_8_primary_probe` |
| primary repeats | no | `19611..19620` | `phase08_8_8_primary_repeats` |
| secondary visible | yes | `19651` | `phase08_8_8_secondary_probe` |
| secondary repeats | no | `19661..19665` | `phase08_8_8_secondary_repeats` |

Every case retains two declared sources at `400/1600`, exact one-fill
cardinality, counted-candidate classification, candidate-informed fill,
approach continuity, active-fill transit, supervisor-owned assist, affine
escape assistance, no operating bounds, no recenter, no recoverable
navigation, no post-recovery guidance, no contacts, and the simulation-only
`0.50 m` evaluator stop.

The physical contract remains coordinate-free and operator-stopped with
`Ctrl+C`.

## Source qualification

All pytest commands used the repository source first while retaining the
isolated ROS/interface overlay:

```bash
source /opt/ros/humble/setup.bash
source /tmp/phase08_8_v8_8_release_qual.l9OTKJ/install/setup.bash
export PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc:$PYTHONPATH
```

The new causal-entry tests alone:

```text
17 passed, 301 deselected in 1.62 s
log:
  /tmp/phase08_8_m4_9_v8_8_initial_focused_corrected.log
  2f55f7fe9b79a50fc56f8cf5e0efbca619f597839a418f54320e68bd22989112
JUnit:
  /tmp/phase08_8_m4_9_v8_8_initial_focused_corrected.xml
  de0dd27e82647fc32913037e7fd9cd6674acc75b0aeae0ed0c2d8cd1650f9852
```

Final complete schema/runner subset after advancing the current schema
constant:

```bash
python3 -m pytest -q \
  test/test_scenario_runner.py \
  test/test_scenario_schema.py
```

```text
318 passed, 1 skipped in 52.86 s
log:
  /tmp/phase08_8_m4_9_v8_8_schema_runner_final.log
  94cef91fcdd27656ca4aa49cd96dfc9f4f6fb105059ef4adafbdd9342343d034
JUnit:
  /tmp/phase08_8_m4_9_v8_8_schema_runner_final.xml
  7d3018664203b5bebdf7e39a4497e3318b4b7387a240740814bef47bad91b34c
```

Focused controller, supervisor, detector, escape geometry, modified-cost,
search-history, observability, and legacy tests:

```text
310 passed in 8.33 s
log:
  /tmp/phase08_8_m4_9_v8_8_focused_controller.log
  2c4ba7c739964f86ec69bdaa97becf6ea1243c6eee07c899bea41db190762413
JUnit:
  /tmp/phase08_8_m4_9_v8_8_focused_controller.xml
  e06386cb22005a32b3262e41d02d2c0c7d883b62333b863d3d84b0d1bbaa1470
```

Focused runner, schema, validator, recorder, analyzer, aggregate-truth,
disturbance, and shutdown tests before the final schema-constant assertion:

```text
604 passed, 2 skipped in 130.92 s
log:
  /tmp/phase08_8_m4_9_v8_8_focused_evidence.log
  252136459141882a17da08e41c76dd51ba60f684603329db4d15d2708a879d02
JUnit:
  /tmp/phase08_8_m4_9_v8_8_focused_evidence.xml
  8eec075e2e25ab33456521d55bb71fc3f06552a20dd7bc8469f14babb76aab6b
```

Final broad ROS-independent functional regression included those nineteen
functional modules plus the repository copyright check:

```text
915 passed, 3 skipped in 135.14 s
log:
  /tmp/phase08_8_m4_9_v8_8_broad_functional_final.log
  37f2995ae325d2ba50a507ca7877cf52b48f7eab3a43973e1ee809e7f17b2d16
JUnit:
  /tmp/phase08_8_m4_9_v8_8_broad_functional_final.xml
  f1f540233a36bfefef6c8529cf8d457dfa5b2300bdb9c8279b7a366636580fbb
```

The three broad skips are the unchanged copyright-template check and the two
explicit Gazebo opt-ins. There are no functional failures or errors.

The final installed/source schema-constant assertion separately passes:

```text
1 passed in 0.61 s
installed SCHEMA_VERSION: 12
installed supported set:  1 through 12
```

Changed-file `ament_flake8` reports only the inherited D202 at unchanged
`run_scenario.py:2410`. The required fatal selection
`E9,F63,F7,F82` is empty:

```text
/tmp/phase08_8_m4_9_v8_8_ament_flake8_changed_final_corrected.log
SHA-256:
  3309cb20c8d52085895ff9c559571c791250ee0bac0883c1ef3dae56b4d3adf2
```

Changed-Python compilation, central-launch XML parsing, all four YAML parses,
`git diff --check`, and:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/
  validate_phase_context.sh 08 implement
```

all pass.

## Fresh isolated build and installed graph

The final fresh build command was:

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
  /tmp/phase08_8_v8_8_release_final.L0zEGg
result:
  3 packages finished in 11.8 s
log:
  /tmp/phase08_8_m4_9_v8_8_release_build_final.log
  89543bd283da4bc645229cba255c7ee71ead647c5287a2bfff3b4bcd32987f1a
```

Source/install byte parity passes for `10/10` runtime owners: controller,
scenario runner, scenario schema, supervisor state machine, supervisor
adapter, central launch, and all four v8.8 scenarios.

Installed nonexecuting launch checks:

```text
/tmp/phase08_8_m4_9_v8_8_release_show_args_final.txt
  e252cc0f88308dd2236215d7bed206d2e5123051393bf2e6dfaa1f88bbcfe318
/tmp/phase08_8_m4_9_v8_8_release_launch_description_final.txt
  1ab580f14aa25de9bbb7c98e74a78e13884f284215fab3061ba511337e9564f4
```

Both return zero. The evaluator-only handoff timeout is absent from the
installed launch arguments and description.

Direct installed construction on isolated ROS domain `226` reached the
expected bounded timeout `124` for:

```text
default supervisor:
  /tmp/phase08_8_m4_9_v8_8_release_supervisor_default_final.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
fully enabled counted-source supervisor with max_fill_clusters=1:
  /tmp/phase08_8_m4_9_v8_8_release_supervisor_enabled_final.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
robust affine modified-cost owner:
  /tmp/phase08_8_m4_9_v8_8_release_modified_cost_final.log
  880639c43048c184845cd49ae726e72b5db2558542e89bfdfe4491b92a0d4f34
fully enabled robust controller:
  /tmp/phase08_8_m4_9_v8_8_release_controller_enabled_final.log
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

The modified-cost owner logs its two normal startup messages and the
`ExternalShutdownException` produced when the bounding `timeout` shuts down
the executor. This is post-start timeout termination, not a configuration or
construction failure. No construction process survived.

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
| primary visible | yes | 1 | `19601` | `f2a7df36a9e877e4df42d395c2737f2bfd1e304f36dc8ebc6e432828ab20ba47` |
| primary repeats | no | 10 | `19611..19620` | `09a8c2c0f2a23c01b1b310af21d8e7aee075e0eb0d811425e44ee75b596a11c9` |
| secondary visible | yes | 1 | `19651` | `51194703587f1479c59860a3a1b600301fc2d5546b8aeaca2f59a649cc0e2991` |
| secondary repeats | no | 5 | `19661..19665` | `5ec03aca0d8cf474ad54c6c09bf467fdce4285272cd3115f9597417c6c0f8257` |

All four run roots were absent before and after dry-run.

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

V6, v8-v8.7, shifted worlds, and every older scenario remain selectable.
Fixed failed evidence remains failed and was not retried or relabeled.

## Bounded qualification corrections

The following pre-runtime issues were preserved and corrected:

- the first focused invocation replaced rather than prepended
  `PYTHONPATH`, so ROS interfaces were unavailable at collection; the
  corrected command passed;
- the first complete schema/runner run ended at `316 passed, 1 failed,
  1 skipped` because the unsupported-version fixture still used newly
  supported schema 12; it now rejects schema 13;
- the causal audit initially transcribed the exact handoff as
  `13.125597 ms`; immutable replay proves `14.125597 ms`;
- the initial current-version implementation added 12 to the supported set
  but left `SCHEMA_VERSION=11`; it now exports 12 and has a regression test;
- the first final schema rerun lacked the isolated interface overlay and
  stopped during collection; the corrected command passed;
- one full-directory diagnostic included the repository's intentionally
  non-gating historical `flake8` and `pep257` suites. Functional tests were
  `915 passed, 3 skipped`; only those two legacy style suites failed. The
  exact declared functional gate then passed `915, 3 skipped`;
- initial lint invocation syntax was unsupported; the final full changed-file
  invocation has only one inherited D202 and no required fatal code;
- an initial construction wrapper used invalid Fast DDS domain `237`; the
  corrected domain-`227` qualification and final domain-`226` construction
  reached the expected bounds;
- the first dry-run invocation omitted required `--operator`; that argparse
  failure is retained separately, and all four corrected installed dry-runs
  pass;
- a parity recheck initially named a nonexistent `controller_script.py`;
  the actual `controller_node_script.py` matches, and the corrected complete
  parity is `10/10`.

These are Level B evidence, test-fixture, metadata, or qualification-invocation
corrections. No algorithm motion or empirical result was affected.

## Runtime boundary

At qualification close:

- no Gazebo, scenario runner, recorder, analyzer, rosbag recorder, controller,
  supervisor, or physical process is active;
- all four v8.8 run roots remain absent;
- no historical input or result is changed;
- the physical contract remains manual operator `Ctrl+C`;
- sealed-run monitoring may use only process state and retained files, never
  a ROS/DDS participant on the run domain.

The next authorized action is the implementation checkpoint and commit,
followed by a separate dispatch-boundary checkpoint and commit. Only then may
the visible seed-`19601` primary probe run once. A behavioral, schema-v12
entry/exit ownership, recording, final-zero, or cleanup failure closes that
visible gate. A formal pass and all nine analysis plots are required before
the primary repeat population may be dispatched.
