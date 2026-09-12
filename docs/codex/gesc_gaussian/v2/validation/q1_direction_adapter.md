# Q1 typed direction adapter — source validation

Status: implementation and focused source tests complete at the boundary below.
This record does not execute or qualify the four-run study or release the M4
pilot. The active contract is [q1_plan.md](../q1_plan.md). Earlier M1/M1a
calibration failures and the unavailable192-slot historical reference remain
unchanged.

## Existing owner and APIs

The existing `ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py` owns all
new entry points; the existing numerical helper/evaluator remain unchanged.

- `prepare_q1_direction_inputs(bag_data, metadata, *, contract, run_spec)`
  returns JSON-safe normalized rows and an input qualification receipt. It uses
  the recorder's schema2 identity and strict typed-stream validator, preserving
  acquisition/publication times, pose/encoder brackets, original input receipts,
  admission, observed sensor geometry and complete atomic objective metadata.
  An ambiguous source/objective/observation chain quarantines the run's anchor
  inputs. First publication is the first retained publication from the direction
  publisher; it does not claim the supervisor received that publication first.
- `q1_observation_from_row(row)` reconstructs the exact serialized
  `SynchronizedObservation`, including original receipts, for the existing
  `MovingRawEvidence` owner. Normalized rows expose source stamp/sequence,
  source XY/raw cost/world phase and first diagnostic state/publication time.
- `q1_recorded_binding(run_directory, *, source_files)` verifies selected
  recorded argv/configuration against the dirty-source checkpoint's file hashes
  and the captured robot description. It does not use HEAD blobs or evaluate
  the field. Geometry remains the selected .355m joint/.18m radial/.015m sensor
  binding with identity mount rotation and vertical axis.
- `freeze_q1_direction_targets(study_manifest_path, output_directory, *,
  partition, nomination_manifest=None)` writes exclusive input and target
  receipts for one partition. The shared manifest fixes all four runs;
  confirmation requires a passing hashed discovery nomination with matching
  contract and one allowed parameter pair before its bags are read.
- `evaluate_q1_direction_references(frozen_targets_paths, output_directory, *,
  contract_path)` accepts the two partition `targets.json` paths and performs
  the single48-slot reference job. The caller must impose `timeout300s`.
  It rechecks source/config/input/geometry receipts, nomination and target
  selection before model construction and at completion. Each anchor is written
  atomically and exclusively; timeout leaves the started/completed receipts.

The acquisition manifest schema is the one agreed with the study owner:
`version`, `contract:{path,sha256}`, and four `runs`, each containing
`run_id`, `seed`, `partition`, `exposure`, `run_directory`, `input_files`,
`binding` and `model_configuration`. Input receipts must cover metadata,
resolved topics/scenario/parameters, bag metadata and all SQLite bag files.
The contract binds `source_files`, `geometry_receipts` and fixed `reference`
parameters. The label owner verifies that the declared geometry receipts form
the complete original numerical/recovery chain; this adapter rehashes that
declared set and never recalculates enclosures.

When the production contract contains its reserved `runs`, central run
verification also requires the unique reserved run ID, seed, partition and
exposure, exact retained `resolved_scenario`, and exact `metadata.target_argv`
against its planned `launch_argv`. Thus input hashes alone cannot silently
substitute a different spawn or control setting. Minimal synthetic test
contracts may omit the acquisition population; the production freeze binds it.

## Input population and comparator

`qualified` in a normalized row means input validity, independent of averaging
confidence, method magnitude or output validity. T0 is the first qualified row
whose first diagnostic bag receipt lies inside the recorded readiness interval.
Each of12 offsets10,20,...,120s selects the first such input within50ms afterward.
Missing targets remain missing. A readiness transition starts a new input
context so a reference revolution cannot bridge preflight/shutdown support.
Exact source identities freeze before reference calculations; confirmation
identities freeze only after discovery nomination.

The paired vectors are the recorded aligned instantaneous GESC component and
the recorded final rolling output rotated by its recorded output yaw. Repeated
diagnostics cannot replace the first output with a later favorable one.
There is no reconstruction of inherited subscriber callback scheduling.
The observation-only study requires an explicit complete objective law with
empty active fill/affine sets and matching zero component values. The reference
still uses its recorded weights and `augmented_objective`; equality with a raw
objective cannot be assumed merely from SEARCH or absent event messages.

Unchanged reference owners determine latest complete measured revolution,
two actual observations per sector, signed rate, CV<=0.10, cadence sensitivity,
dual adaptive quadrature, coefficient error<=1e-6 and the informative-reference
floor. The eligible denominator consists of independently informative,
input-cycle-qualified anchors in a recorded valid allowed state. Missing and
weak method outputs remain denominator outcomes. Usable averaging requires
`output_valid`, blend weight0.5 and a finite final world-vector norm>1e-6.
The report also retains the raw blend-applied count, unavailable reasons,
fallback counts and conditional angular quantiles. Empty or insufficient
confirmation exposure is `EVIDENCE_UNAVAILABLE`; measured unmet targets are
`FAIL`, with no synthetic direction substituted.

## Q1 pose admission and common support

`q1_pose_search_eligibility(samples, bag_data)` preserves actual selected pose
knots and original bag receipts. It projects pose/state support to the first
recorded covering clock subject to the original0.5s source/clock/bag-receipt
bounds, then applies the existing SEARCH/readiness mask. Missing coverage,
clock rollback, invalid state, stale input and a readiness interruption while
pending make support unavailable. It records `admission_bag_timestamp_ns`,
`original_receipt_clock_ns`, `admission_unavailable_reason`, SEARCH epoch/start
and history generation. It does not resample positions or derive spatial labels
from detector outputs.

This is expressly `recorded_clock_and_original_bag_receipt_proxy`, with
`subscriber_timing_reconstructed=False`. A bag cannot establish the detector's
actual callback order or steady receipt timestamps. It supplies a declared
prospective replay approximation and explicit unknown support, not new runtime
transport qualification. The initial read-only concern about leading poses
being rejected by the historical mask was corrected: that mask uses a maximum
of pose source and recorded clock per pose. Its state-entry check and synthetic
clock projection still differ from explicit clock-covered Q1 admission.

The historical `_v2_search_eligibility` policy is unchanged; an additive returned
`search_epoch_start_ns` exposes its existing derived boundary. The existing
`_v2_common_positive_support` now accepts `minimum_duration_sec`, default54s.
Q1 explicitly passes42s. Its one-first-opportunity/censoring behavior remains;
the added fixture proves the closed historical default still censors43s while
the separately declared Q1 duration can accept it.

## Exact source validation commands and retained outcomes

All commands ran from `/home/mattb/dsim-lab`. The common sourced prefix was:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
```

The initial command was:

```bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_direction_inputs.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_direction_inputs_v1.log 2>&1
```

It passed17 tests in1.98s, exit0. Adapter v1 used:

```bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_direction_inputs.py ros2_ws/src/ros_esc/test/test_q1_direction_references.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_direction_adapter_v1.log 2>&1
```

It retained33 passes/3 failures in10.28s, exit1. The analytic reference fixture
exposed NumPy boolean scalars that the JSON writer could not serialize. A Q1
adapter conversion now retains their values as ordinary JSON scalars; numerical
functions and tolerances did not change.

Versions v2/v3/v4/v5 used the identical following command, with only the output
filename's version changed:

```bash
PYTHONPATH=ros2_ws/src/ros_esc:extremum-seeking/src:$PYTHONPATH timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_direction_inputs.py ros2_ws/src/ros_esc/test/test_q1_direction_references.py ros2_ws/src/ros_esc/test/test_v2_direction_reference.py ros2_ws/src/ros_esc/test/test_v2_bag_replay.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_direction_adapter_v5.log 2>&1
```

| Version | Result | Meaning |
| --- | --- | --- |
| v2 |136 PASS,15.50s, exit0 | New adapter and inherited reference/M1 regressions |
| v3 |138 PASS/1 FAIL,21.02s, exit1 | Added captured-parameter fixture used the wrong YAML nesting; retained failure |
| v4 |149 PASS,20.75s, exit0 | Correct actual recorder-shaped parameter fixture, post-readiness target and Q1 admission cases included |
| v5 |153 PASS,20.92s, exit0 | Added reserved-run/scenario/control binding and four focused fixtures |

Fixtures use actual ROS wire serialization, detached in-memory streams and
analytic angular functions. They do not launch ROS nodes, open real bags or
evaluate the selected light field. They cover exact schema2 timing, immutable
repeats/revocations, cross-topic receipt order, readiness-independent confidence,
sealed confirmation, fixed missing slots, changed provenance, current captured
geometry, usable averaging/weak fallback, unavailable constant reference,
exclusive artifacts and retained partial output on timeout. Existing100
reference/replay regressions remain included in the final153-test result.

Additional commands passed:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
git diff --check -- ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py ros2_ws/src/ros_esc/test/test_q1_direction_inputs.py ros2_ws/src/ros_esc/test/test_q1_direction_references.py
timeout 15s python3 -m py_compile ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py ros2_ws/src/ros_esc/test/test_q1_direction_inputs.py ros2_ws/src/ros_esc/test/test_q1_direction_references.py
```

## Hash boundary

Logs are under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.

| Artifact | SHA256 |
| --- | --- |
| `q1_direction_inputs_v1.log` | `b8ff800a9decc2bea51d2f33b0d841a19db91b5d4216a206c4130687d8ff1363` |
| `q1_direction_adapter_v1.log` | `aa56e95cde1bfbdf77e62b25b98475e36c1b636dc10582877982b7a4577da10f` |
| `q1_direction_adapter_v2.log` | `01b89858d737eb9343cb541f348d4a63173b2f67fdad3a095b58da1c5495c2e1` |
| `q1_direction_adapter_v3.log` | `4697b337eb92e9506a0d559d9761d8e69c5cfb59dcdaa8122ad6a0d7217c6ea3` |
| `q1_direction_adapter_v4.log` | `07454b8f1d8e09269cce81619608c420128d8377f18a2d184ff9e2bd11737272` |
| `q1_direction_adapter_v5.log` | `137bb7c8596e5df370fab734f79282a87ea6f8357c124ef49c7dbb3b4c738070` |
| `gesc_gaussian_bag_analysis.py` | `072c239e6ba6041f2a0b753ec1e422fa9fbc400759f895413e276de32ac6a1c6` |
| `test_q1_direction_inputs.py` | `99e98c131627df68d7f890db9b4555991dbd79b8ae6b47fe501e8420a88e9a04` |
| `test_q1_direction_references.py` | `e18251320cc4aeddd26c4fe3d177b2da695bdb497e86dfde3dd902d4a41a3ba1` |

This is a focused source boundary. Root still owns the integrated contract,
geometry-chain proof, label/nomination orchestration, launch/build checks,
acquisition release and all scientific qualification decisions.
