# Phase 08.8 M4.10 Fixed V8.9 Primary-Visible Result

## Disposition

**CLOSED / PRE-GAZEBO INFRASTRUCTURE FAIL / NO BEHAVIORAL EVIDENCE /
NO RETRY.**

The one authorized v8.9 primary-visible seed `19701` attempt was dispatched
from the qualified installed scenario and terminated before Gazebo or the
recording graph started. The recorder returned `2` while constructing run
metadata because its Git lookup inherited `/tmp` as the current working
directory:

```text
record_run: CalledProcessError: Command '['git', 'rev-parse',
  '--show-toplevel']' returned non-zero exit status 128.
```

The runner therefore classified the attempt as
`runner_or_recorder_failure`, set `recording_complete=false`, retained no
bag, and reported every behavioral predicate unavailable. Cleanup passed
with no new node or session process remaining. This is not a controller,
detector, fill, command-ownership, ranking, convergence, or Gazebo result.

Seed `19701` is not retried. The ten v8.9 primary repeats, secondary visible
probe, secondary repeats, M6, three-light execution, and physical motion
remain prohibited by the fixed v8.9 gate.

## Frozen dispatch and retained evidence

Dispatch HEAD:

```text
95efaa5 phase 08.8: authorize v8.9 primary visible probe
```

Installed scenario:

```text
/tmp/phase08_8_v8_9_release_qual.2fWDxv/install/ros_esc/share/
  ros_esc/scenario_runner/scenarios/
  phase08_v8_9_primary_visible_probe.yaml
SHA-256:
  2131b9b77587c7326e31acb63a6922ce4fbd81655b711f0b119f1c97be4c736c
```

The sealed attempt used visible presentation, `ROS_DOMAIN_ID=224`, a
`720.0 s` scenario bound, a `900.0 s` runner wall bound, and a `960 s`
outer bound. It began at `2026-07-31T16:59:41.455647Z` and closed at
`2026-07-31T16:59:43.362061Z`.

Scenario summary:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_9_primary_probe/scenario_summaries/
  20260731T165941455647Z_phase08_v8_9_primary_visible_probe.yaml
SHA-256:
  c1f322e48eb06132a9dcf065d9d11f039dd5275842bf42caa19318ad47f7cdf7
```

Retained run directory:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/
  phase08_8_9_primary_probe/2026-07-31/
  20260731T165942441730Z_simulation_phase08_v8_9_primary_visible_probe-
  v8_9_primary_probe_r1p5_a45_h25_19701-robust__59eb6408
```

Retained file hashes:

```text
scenario_result.yaml
  9f4a5318c63f1d4d4ba4751fefd5e92c995e420dcffc418c1949e28430b78daa
resolved_scenario.yaml
  8fb444ff46d98e47ad3781829355cade828f94ea37b572cc8debc66b1bae1296
scenario_definition.yaml
  2131b9b77587c7326e31acb63a6922ce4fbd81655b711f0b119f1c97be4c736c
notes.md
  b5b0ce3e05f57f6c6b7e53f6cf03a7d46426b403efc13b5ea39ed72cc3d8fa11
dispatch console
  /tmp/phase08_8_m4_10_v8_9_primary_visible_dispatch.log
  324afa05e4491f930b47af517efe631c1663c201d6cb6b585d5516be76f2900f
```

No `bag/`, recording metadata, completeness record, validation bundle, or
plot bundle exists. The only baseline node was the domain-224 ROS CLI
daemon; cleanup retained no new nodes and no session descendants. No active
Gazebo, scenario-runner, recorder, rosbag-recorder, analyzer, or physical
process remained at closure.

## Required analyzer invocation

The analyzer was invoked once after population closure, but the manually
transcribed target omitted `_19701` from the case portion of the directory
name. It consequently returned `2` with:

```text
analysis failed: FileNotFoundError: run directory does not exist
```

Log:

```text
/tmp/phase08_8_m4_10_v8_9_primary_visible_analysis.log
SHA-256:
  64414c17fef8838ad148dec1b4d911e733271dc8bbcb5dad992dc8f2c31102b0
```

No second invocation is made. Even with the correct path, analysis could
not produce scientific results because the recorder failed before creating
a bag. A fresh version must derive the analysis target directly from the
retained scenario summary rather than manually reconstructing the run ID.

## Root cause

The installed scenario runner resolves its own repository root correctly
through `_repository_root()` and stores it in `REPOSITORY_ROOT`. However,
all three recorder-process owners launch `record_run` without a `cwd`:

```text
_run_record_to_boundary
_run_record_to_global_proximity
run_record_process
```

The child therefore inherits the caller's current directory. The v8.9
dispatch intentionally invoked the installed runner after `cd /tmp`.
`record_run` constructs metadata with:

```text
git_state(Path.cwd())
```

and `git_state` runs `git rev-parse --show-toplevel` in that requested
directory. The same command returns `128` from `/tmp`, reproducing the
failure without ROS or Gazebo.

This is a runner/recorder integration defect. It is independent of schema
v13 and does not invalidate the completed no-Gazebo schema-v13 qualification
or retained replay evidence.

## Fresh correction boundary

A separately planned v8.10 may:

1. launch `record_run` with `cwd=REPOSITORY_ROOT` in all three runner-owned
   process paths;
2. add focused tests that prove the working directory for normal, boundary,
   and staged-global-proximity recording;
3. copy the four fixed v8.9 inputs to fresh v8.10 identities, roots, and
   seeds without changing algorithm or evidence semantics; and
4. require post-run analysis targets to be read from the generated scenario
   summary.

It must preserve the failed v8.9 attempt, every historical scenario and
result, controller behavior, schema-v13 dual-topology evidence, fixed
`400/1600` two-source inputs, manual physical `Ctrl+C` stop, and all existing
behavioral gates. No Gazebo process is authorized until the fresh correction
is planned, implemented, fully qualified without Gazebo, checkpointed, and
committed.
