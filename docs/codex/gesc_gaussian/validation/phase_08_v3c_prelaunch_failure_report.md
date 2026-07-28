# Phase 08.3 V3C prelaunch failure report

## Disposition

V3C is **CLOSED / FAILED / PRELAUNCH INFRASTRUCTURE ERROR / NO SIMULATION
OUTCOME / NOT SIMULATION-READY**. Its root is immutable:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3c
```

The first required new slot, `v3a_below_target_fill`, retained:

```text
AttributeError: __enter__
```

It produced no simulation run directory below `runs/`, no attempt scenario
summary, no attempt record, no bag, and no scientific outcome.
`new_execution_count=0`; the sole composite record is the immutable V3B
direct-goal behavioral failure carried by pointer and hash. The composite
`run_count=1` is not a V3C simulation.

## Root cause

`run_scenario._run_record_to_boundary` created and initialized a private
`rclpy` context and created the observer node on it, but called
`rclpy.spin_once` without an executor. ROS 2 Humble therefore tried to create
the global executor on the uninitialized default context. Its guard condition
attempted to enter the absent default-context handle and raised
`AttributeError: __enter__`.

The later `SingleThreadedExecutor` `_sigint_gc` destructor warning is a
secondary symptom of the partially constructed global executor. It is not a
second cause or a simulation result.

## Retained evidence

All hashes below were recomputed read-only:

```text
activation/attempts/002_v3a_below_target_fill/attempt_01/
  execution_error.json
  233397500285c7c761bd09f9377d787d9dac7ce3b925a25db727402e1a56a891
activation/progress.json
  1a878ced1c18201f28b1d3caadd5ffa7631d8cb16c002b4d57b2dbb0b69503ba
activation/attempt_records.json
  37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570
activation/records.json
  731d87ab80559b20087c00319062648c582b47a2e19f2623563df573266e423c
activation/scenario_summary.yaml
  73bb4b3fd847b541391738d43adbaafd39dab47245d72da012875a51cabed789
activation/resolved_suite.yaml
  75134d172a44ef70b5ca4370a6e6b9fd91fbb6981f786ce71565749481882108
workflow_state/v3_activation.json
  54067b813957e7cd0e84b0388050dc972668499695bf87a583d7531d261f1186
```

Progress internal SHA-256:
`e31a27ee6f4ab649fef24dd470af6a12acc4b59a3fee90da0c2963fc9f48edf4`.
Activation-state internal SHA-256:
`bf0d085b31fa3b2e06c433743c507f89c21ea385f1d57fcc3047a0f8799cfcfe`.

## Fresh V3D boundary

The failed V3C infrastructure attempt is not resumed or overwritten. A fresh
V3D root is required and was absent when this report was written:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3d
```

After a focused private-context executor correction and full qualification,
V3D may execute the same nine previously undispatched cases exactly once:

```text
v3a_below_target_fill
v3a_pure_escape_recenter
v3a_stalled_assist
v3a_fill_merge
v3a_full_lifecycle_goal
v3a_revisit_guard
v3a_boundary_saturation
v3a_noise_delay
v3a_safe_timeout
```

V3D must carry the immutable V3B `v3a_goal_aggregate_direct` failure by its
original path and SHA-256, preserve V3C as failed infrastructure provenance,
and retain every original case, seed, profile, contract, safety, evidence,
collision, cleanup, and no-replacement rule.

V3D is diagnostic completion only. Its composite activation and Phase 08.3
verdict are forced failed regardless of the nine new outcomes. M4, freeze,
holdout, additional validation, reproducibility, readiness tagging, Phase 09,
and physical hardware remain prohibited.

## Correction and precommit verification

The bounded correction gives the boundary observer its own
`SingleThreadedExecutor` on the same private `rclpy` context as its node and
closes executor, node, subscription, context, process, and descendants
deterministically. It does not change a case, seed, profile, threshold,
behavior contract, collision rule, evidence rule, or scientific verdict.

The machine-readable correction audit is:

```text
docs/codex/gesc_gaussian/validation/
  phase_08_v3c_prelaunch_correction.json
```

Its retained file SHA-256 is
`b4ba3b2a270adc1eb399c995abc34472d874fc1f33691b9deea97c1e1847ae10`;
its self-omission SHA-256 is
`00bc460ced8fd8d2490a6ffc88e430b531b6eb11f9564f20aff069afd2c30b4c`.
The proof rehashed every regular file and excluded directory-symlink mapping
below the immutable V3A, V3B, and V3C roots and passed with exact file counts
`1574/1574/1540`.

The complete source-first functional gate passed with `475 passed, 2 skipped`;
both skips are explicit Gazebo opt-in tests. A focused independent gate passed
with `206 passed, 1 skipped`. Targeted changed-file lint, production
docstrings, compilation, strict JSON, context validation, standard
three-package build, installed entrypoint checks, and an installed real-ROS
no-Gazebo boundary smoke all passed. Independent review returned **GO** for a
clean checkpoint, commit, fresh V3D adoption, and full V3D qualification.

No V3D root or Gazebo simulation existed at this verification boundary.
