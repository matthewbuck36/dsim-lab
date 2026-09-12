# M1a validation record

Status: numerical enclosures and recovered label publication PASS; fixed
calibration completed with **no qualifying setting**. The original label
attempt remains INCOMPLETE (600 s timeout). Technical recovery is separately
recorded under [its frozen plan](../m1a_recovery_plan.md).
This is the bounded correction in [the frozen M1a plan](../m1a_plan.md), within
M1 of the approved simulation-only V2 plan. The original calibration remains
failed and no detector setting is selected.

## Frozen protocol

- Contract: `m1a_contract_v1.json`, SHA256
  `ae4a7fb242c20fb5f1ee410eb1bb261a12c49e9ee059d1567ff7d5ef733fb40f`.
- Plan SHA256:
  `fb1e6462efa51c5004a7032ee3fa607707403280cee67b4cd70d97499a492ce3`.
- Root checked the four referenced inventory, prior-label, synthetic and plan
  hashes against their live files before implementation. All match.
- The independent mathematical review found the one-time threshold
  recomputation consistent: adding checked cell centers can only lower the
  minimum upper estimate and the midpoint level. It cannot admit an untested
  four-corner-low cell. The quadrature error estimates and spatial witnesses
  remain finite numerical evidence, not a continuous-domain certificate.
- Review clarified exact six-second interpolation for negative travel before
  any fresh output. This avoids treating 0.12 m over an irregular interval
  longer than six seconds as the intended >=0.02 m/s progress. The frozen
  contract and plan both contain this clarification.

`timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`
passed. `git diff --check` passed. The existing checkpoint tool captured the
contract review boundary; a further checkpoint must capture tested owners
before the first fresh geometry execution.

The three independent geometry groups may run in at most three worker
processes under the single unchanged 600-second outer timeout. Each owns a
disjoint receipt directory. Group/source ordering in the manifest remains
deterministic; this changes scheduling only, with no additional locations,
numerical retries or contract changes. The host reports twelve logical CPUs.

## Focused implementation validation

From the repository root, source `/opt/ros/humble/setup.bash` and
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash`.

```bash
timeout 180s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_enclosure.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m1a_enclosure_tests_final.log 2>&1
timeout 180s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_bag_replay.py ros2_ws/src/ros_esc/test/test_bag_analysis.py > /home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_replay_tests_final.log 2>&1
```

PASS: 27 enclosure tests in 6.65 s; 44 analyzer/replay tests in 1.71 s.
Root inspected both final logs. Independent review found no unresolved
material issue. The existing detector core is unchanged by M1a; its final M1
regressions remain recorded in `m1_validation.md`.

The implementation includes the actual light-cost owner in provenance,
records Python/NumPy/SciPy versions, preserves integer-valued fixture inputs
through floating interpolation, and rejects scaled-coordinate overflow.
Contract file digests and canonical-content digests use distinct field names.
Context validation and full `git diff --check` passed before execution.

## First empirical attempt

Root executed the proposed label command in `m1a_integration_validation.md`
after checking the final tests and recording the checkpoint. The exact executed
command is saved as
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_label_command.json`.
It used `timeout --signal=TERM --kill-after=5s 600s` with exclusive output/logs.
The command exited **124** at the fixed timeout. No complete `labels.json` was
published and no detector calibration followed it.

All six source enclosures completed and qualified, with 8,625 point receipts.
The independent audit checked every point hash, accepted five-point stencil,
mask connectivity/dilation, bounds and retained holes. No numerical warning or
exception occurred. Global error estimates remain below, but close to, the
1e-6 ceiling. See `m1a_enclosure_audit.md` for the quantitative audit.
The existing log reached the first input's five spatial labels; those labels
were not published as a complete eight-input dataset and cannot be calibrated.

Read-only complexity diagnosis found up to 23,960,490 negative-exclusion queries
for 67,685 six-second windows across 69,222 poses. Exact full-segment caching
plus the clipped first segment reduces that bound to 273,798 queries; positive
membership remains additional unchanged work. This is
the basis for technical recovery, not a change to scientific thresholds.

The recovery input manifest preserves and hashes 8,642 old JSON receipts and
an exact old-analyzer snapshot. Its SHA256 is
`ac8165d721cc3557b06f84c85c0fa42ab0a98dea45ba076c1539dce38f4a2cfd`.
The original incomplete attempt and log remain immutable.

Root rendered the saved numerical receipts without any new field evaluation:

```bash
timeout 60s python3 /home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_plot_enclosures.py
```

PASS, exit 0. The figure is
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_visualization_v1/enclosures.png`;
its adjacent `provenance.json` binds the input manifest, script and image hashes.
Root visually inspected all six panels: the displayed masks retain annular
holes, and the derived area centroids lie within those holes. Display contours
are explicitly approximate; saved cell masks remain authoritative.

## Technical recovery implementation

The existing analyzer now caches complete-segment membership and checks each
clipped first segment separately. Per-window NumPy distance/path arithmetic
is unchanged. Recovery verifies the original snapshot/task text, all 8,642
receipts, exact group/input bindings and unchanged numerical owners. Original
geometry provenance remains intact; the new label owner is recorded separately.
Calibration rechecks the old manifest/snapshot/receipt chain before importing
the detector. Logged reuse paths name actual retained geometry files.

In the Humble plus isolated source overlay:

```bash
timeout 180s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_bag_replay.py ros2_ws/src/ros_esc/test/test_bag_analysis.py > /home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_recovery_tests_final.log 2>&1
```

PASS: **61 tests in 4.60 s**. Root inspected the final log. Seven fixture
families produce exactly the same labels as the retained old function,
including clipped-away exclusion and just-below/above threshold drift.
Tests cover the query bound, immutable-geometry reuse without evaluation,
changed evidence rejection and provenance rejection before detector import.
Independent review, full diff check and context validation passed. The
unchanged geometry-task text SHA256 is
`ab02e5cd019210be0307ba09f3305700df2fa73f71c8de0d209768bdadcd5b38`.

## Recovered label result

Root executed the command saved in
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_recovery_command.json`
after the recovery checkpoint. **PASS, exit 0**; started-to-manifest time
31.818 s. The completed label manifest is
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1_recovery1/labels.json`,
SHA256 `2ae8c6e53446ec2ce176f43436d47b726c7c5d8107990a486f021ff787e9620b`.
It records 8,642 verified old receipts, all 8,625 reused points, three geometry
groups/six source enclosures, and **zero numerical field evaluations** during
recovery. New label-owner SHA256:
`cd4bde8aa38a2be17d3138b4c2eff8972f5d0bb44a7573ae4c89fc9e2c58b51f`.

All eight unchanged development inputs have complete spatial labels: 31 total,
including seven positive residence intervals and 24 directed-progress intervals.
The positive durations are 16.116, 22.746, 33.218, 34.136, 30.498, 15.504 and
12.070 s. **None can satisfy the fixed 54-second common positive support.**
This missing retained positive denominator cannot be reported as a successful
calibration regardless of the upcoming synthetic or negative-interval outcomes.
The complete labels permit the separately bounded fixed grid; selection gates
remain unchanged and the lack of positive support must remain explicit.

## Fixed M1a calibration outcome

Root executed the command saved in
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_calibration_command.json`
under `timeout --signal=TERM --kill-after=5s 300s`. **Exit 0**, all 36 grid
receipts and final summary published. Scientific status **failed**;
`selected=null`. The summary SHA256 is
`a7d83b70fcf664432c4bb881fd7a7a59486378ec827e00b2274702b88cbddd67`.

Fifteen settings pass all 79 synthetic cases. Every row has zero available
retained common positives, preventing selection. Three W=3 s / epsilon=.36 m
rows each yield one retained negative-interval event; unknown-event counts
range from zero to twelve across rows. These are detector-candidate replay
events, not fill/goal outcomes. No retained sensitivity or latency claim is
available. Full grid/provenance: `m1a_calibration.md` and its manifest.

M1 implementation/evaluation has concluded without research qualification.
Independent M2 sequencing is specified in `../m1_to_m2_sequencing.md`.

## Scope and limitations

The new helper belongs to the existing bag analyzer. Runtime detector,
recording, numerical core and legacy behavior are unchanged by M1a. The same
eight development traces and 79 synthetic traces remain immutable; thirteen
retrospective holdouts remain excluded from calibration. All required positive
detections, zero negative events and a nonempty retained positive denominator
remain necessary for selection. Unknown events never become true positives.

No Gazebo, hardware, physical snapshot, branch commit or push is part of this
corrective numerical step. M2 direction and M3 moving pipeline remain pending.
