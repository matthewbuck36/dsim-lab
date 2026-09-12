# Q1 subordinate label and nomination owner

Date: 2026-09-09. Status: source implementation and synthetic focused checks
PASS; no Q1 bags, field calculations, spatial labels, nomination or confirmation
results were generated in this task. This record does not release acquisition
or M4. Parent owns the frozen contract, dispatch and final checkpoint.

## Scope and APIs

`ros2_ws/src/ros_esc/ros_esc/plotting_scripts/q1_study.py` extends the existing
analysis pipeline as a subordinate helper, without another CLI or recorder:

- `verify_q1_geometry(contract, resolved_scenario=None, *, runs=())` checks the
  numerical recovery chain and selected inputs before acquisition or labeling.
- `freeze_q1_study_labels(study_manifest_path, output_directory, *, partition,
  nomination_manifest=None)` verifies the fixed run population and inputs,
  then saves independent labels and source traces without importing a detector.
- `evaluate_q1_study_partition(frozen_labels_path, output_directory, *,
  nomination_manifest=None)` evaluates exactly nine discovery pairs or the
  single previously nominated confirmation pair.

The helper delegates numerical work to the existing `CentroidWindowDetector`,
`MovingRawEvidence`, enclosure membership and central analyzer. Actual selected
Odometry header stamps and XY provide centroid knots and spatial labels; the
interpolated XY in synchronized observations is used only by raw M3 evidence.
The existing bag reader loads all eight selected descriptor channels plus
direction diagnostics, algorithm state and clock; it automatically includes
recording readiness. Unused PDE arrays and visualization topics are omitted.
First pose receipts survive duplicate suppression. Conflicts, regressions,
invalid coordinates and frame changes cannot silently create valid knots.

The geometry verifier rehashes the preserved recovery manifest, original
analyzer snapshot and all original recovery receipts through the existing
recovery owner. It verifies the exact `_v2_enclosure_geometry_task` AST source
segment against the retained snapshot and its declared hash. Other numerical
owners must remain unchanged. The selected group must match ordered source IDs,
positions/inputs, bounds, model hash and recorded sensor/URDF geometry; each
selected numerical point must remain in the contract's receipt population.
Current model and sensor/URDF files are also rehashed. This checks lineage and
unchanged numerical meaning; it does not recompute or improve an old enclosure.
The original geometry holes and ambiguous boundaries remain unchanged.

## Fixed gates and timing

Spatial residence/progress labels are frozen before applying SEARCH/readiness
admission or evaluating detector output. The shared Q1 admission helper keeps
actual pose knots and original bag receipts while projecting admission onto the
first covering recorded clock within the declared0.5s bounds. Its evidence is
explicitly a recorded-clock/bag-receipt proxy, not a detector callback or steady
clock reconstruction. Global typed source ambiguity makes the run unavailable.

The existing common-support owner uses an explicit42s minimum for this fixed
W=6s study; its historical54s default is unchanged. A short/interrupted first
residence cannot be joined or replaced by a later favorable residence in the
same SEARCH epoch. For negative exposure, the helper separately requires at
least one continuous qualified6s actual-pose/SEARCH-generation span inside a
declared spatial negative. This prevents an unavailable detector from passing
an empty negative denominator. All original spatial negative intervals still
veto any flag, including a flag ambiguously overlapping positive truth.

Each numerical confirmation records the six-window end and the last actual
pose acquisition C that completed that support. Candidate evidence uses the
fixed deadline C+12s, a conservative proxy for the later live acceptance
deadline. Only raw observations whose first recorded diagnostic publication is
available by an evaluation time may enter evidence. Source order is retained;
later favorable repeated output is never selected. The current raw sample,
its first publication and the latest actual pose must be source-fresh within
0.5s at evaluation. Raw evidence before C remains usable within the same epoch.
Augmented objective/confidence resets alone do not erase the raw verifier.

The completing pose and every subsequent actual pose are checked against the
frozen candidate center and radius. Departure wins ties with raw publication
and terminates the candidate: leaving and returning cannot revive it. Existing
moving-evidence code chooses the latest three measured informative cycles and
its cycle/sector comparison; no oracle center or older favorable triple is used.
An accepted replay result is not retroactively canceled by later departure.
Missing support remains unavailable, while a measured detector or verification
failure remains FAIL. Neither can become an empty-denominator PASS.

Discovery ordering is fixed smallest radius(.25,.50,.75m), then smallest
per-cycle/sector tolerance(.05,.10,.15m), with W6s and score epsilon0.30m.
Every pair must pass both discovery runs. Confirmation requires a hash-bound
PASS discovery receipt before child inputs are read, evaluates only its pair,
and cannot retune. Exclusive output files retain incomplete attempts and each
setting receipt. Final publication rechecks the label manifest, original study
manifest, every child label receipt, actual run inputs and frozen contract.
Canonical JSON hashes use explicitly named canonical fields; the nomination's
`contract_sha256` is the actual frozen contract-file hash.

The old detector was not running in this shadow acquisition: its latency is
`NOT_OBSERVED`. The helper reports only new source-acquisition proxy delay.
It does not invent an old censoring time, matched latency, actual publication,
activation, erroneous fill rate or counterfactual trajectory. The>=30% latency,
wrong-fill and GOAL targets remain M4 outcomes.

## Focused evidence

Repository preflight passed:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
```

First focused attempt: `q1_study_v1.log`,26 passed and one failed in3.31s.
The failed fixture expected `flag_on_declared_negative`; the correct owner
reason was `detector_flag_on_declared_negative`. The actual ambiguous-negative
veto already passed. Corrected that assertion and added full label-freeze,
sealed-confirmation and all-unavailable-grid fixtures; the failed log remains.

Combined command, exit0, **141 passed in5.97s**, no warnings:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
export PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc:/home/mattb/dsim-lab/ros2_ws/src/ros_esc/test:$PYTHONPATH
timeout 180s python3 -m pytest -q \
  ros2_ws/src/ros_esc/test/test_q1_study.py \
  ros2_ws/src/ros_esc/test/test_q1_direction_inputs.py \
  ros2_ws/src/ros_esc/test/test_v2_moving_evidence.py \
  ros2_ws/src/ros_esc/test/test_centroid_windows.py \
  > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_study_v2.log 2>&1
```

After that pass, the parent approved narrowing the reader aliases to the exact
required source streams above. The loader fixture now asserts that complete
set and excludes unneeded PDE/plot arrays. No numerical or gate changed.
With the same sourced environment, final focused command exited0,
**29 passed in3.46s**, no warnings:

```bash
timeout 180s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_study.py \
  > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_study_v3.log 2>&1
```

The29 new helper cases cover exact pose knots, independent labeling, unchanged
historical support, first opportunity censoring, actual completing-pose timing,
stationary/circular/directed synthetic traces, once-epoch behavior, informative
and constant raw profiles, pretrigger support, publication delay, deadline,
departure/tie priority, fixed candidate center, missing negative exposure,
ambiguous-negative veto, all nine ordered choices, sealed single-pair
confirmation, mid-job file mutation and geometry lineage tampering. File-level
freeze/selection fixtures replace acquisition/binding I/O with declared
synthetic inputs; the separate central input tests exercise actual typed wires.
No assertion claims empirical Q1 success or exact DDS callback reconstruction.

## Recorded hashes

| File | SHA256 |
| --- | --- |
| `plotting_scripts/q1_study.py`, final v3 | `59978b3d5db8955c7c1184d64ced1067c5009e38889bf606d8e11b0ac1131670` |
| `test/test_q1_study.py`, final v3 | `41861c114abeb35af9685d7cf8ca048013399d9152082ecf15abd32df05313a7` |
| `builds/initial/q1_study_v1.log` | `259fa80660ea683c02765ee6a76d27c325aaf8f1c0d5ffb6837b631399b509b9` |
| `builds/initial/q1_study_v2.log` | `33ef9bf78f67ea13733cb99664f3502e836d82216c89459d2c64186cd7023641` |
| `builds/initial/q1_study_v3.log` | `269700046de6d9fa14193790637415490321dce6bcd498a0b1c90c65aacd3637` |

Build/log paths are rooted at `/home/mattb/Experiments/GESC-Gaussian/v2/`.
Source paths are rooted at `ros2_ws/src/ros_esc/ros_esc/` except the test path,
which is relative to `ros2_ws/src/ros_esc/`.
