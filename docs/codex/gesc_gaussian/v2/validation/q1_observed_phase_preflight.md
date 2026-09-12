# Observed-phase diagnostic preflight — 2026-09-09 UTC

Status: SOURCE/PREFLIGHT VALIDATED. No recorded-data model evaluation or new simulation has
run under this version. The prospective contract is
`../q1_observed_phase_reference_plan.md`; derivation is
`../q1_observed_phase_reference_design.md` (SHA256
`44f51f1aa627bb3dbfe2e8064202230a1fe6cc1f7d536c89be154553fb49ed59`).

The existing numerical owner now represents the recorded phase-time waveform
and computes its periodic washout reference with an exact piecewise adjoint.
The existing batch owner verifies the original24 targets and exact first
diagnostic supplement before evaluating any field. The existing workflow has
an explicit `--reference-version observed-phase-v1` selector; the default
stationary route remains available with its original gates.

Relative to the closed preceding diagnostic, only the numerical owner, analyzer
and diagnostic workflow may change. Their previous source is extracted from
the completed219-file checkpoint. The new source receipt set adds only the
prospective plan, saved derivation and two new test files. No runtime filter,
controller, detector, launch, objective composer or physical source changes are
part of this diagnostic.

## Review and in-progress verification

Independent review checked the periodic adjoint sign and boundary recurrence,
time weighting, dual partition integration, DC removal, error propagation and
objective-evaluation cap against the saved derivation. Independent forward ODE
tests exercise variable signed rotation and dwell without calling the adjoint
or its quadrature. Source extraction preserves the old cycle computation and
constant-rate numerical owners.

An initial exact AST review expected the old diagnostic verifier to remain one
function and failed on its explicit extraction. Inspection confirmed that the
historical lineage body moved unchanged to a private helper, while the old
wrapper still immediately applies the full live-source validator. The revised
review checks that exact composition and the old numerical functions; it does
not waive a behavioral or scientific gate. Both review logs are retained under
the external `builds/initial/q1_observed_phase_source_review_v*.log` paths.

Review corrected nonfinite latent-vector serialization: invalid means and
overflowing magnitudes must yield explicit unavailable fields, not NaN/Inf in
an otherwise complete JSON receipt. It also requires the supplement's recorded
units to equal `cost_units_per_metre`. The immutable source supplement remains
retained. These corrections precede any source freeze or model evaluation.

Initial numerical-only tests passed47 in3.33s. Two broader checks overlapped a
reviewed analyzer edit and correctly failed source freshness (65PASS/1FAIL in
34.21s and131PASS/1FAIL in19.34s). The latter includes54 passing new numerical
checks. These are retained preflight failures, not recorded-data numerical or
research outcomes. Final combined validation must run with all owners held
stable; its exact command and result will be recorded below before release.

Qualification remains NOT_EVALUATED; confirmation remains SEALED. No result of
this diagnostic can nominate settings, change runtime confidence or release M4.

## Final validation and freeze

Final combined source held stable: **325PASS in59.69s**, exit0, no warnings or
skips, under120s. This includes56 new numerical and46 independent diagnostic
checks plus223 original numerical/reference/input/study/recovery regressions.
No further source changes followed the passing suite. Exact command:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=192 timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_observed_phase_reference.py ros2_ws/src/ros_esc/test/test_q1_observed_phase_diagnostic.py ros2_ws/src/ros_esc/test/test_q1_discovery_direction_diagnostic.py ros2_ws/src/ros_esc/test/test_q1_direction_references.py ros2_ws/src/ros_esc/test/test_v2_direction_reference.py ros2_ws/src/ros_esc/test/test_q1_direction_inputs.py ros2_ws/src/ros_esc/test/test_q1_study.py ros2_ws/src/ros_esc/test/test_q1_recovery_paths.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_observed_phase_integrated_v1.log 2>&1
```

The independent46-test command uses the same sourced overlays, PYTHONPATH with
only extremum-seeking/src added, ROS_DOMAIN_ID192, timeout90s and only
`test_q1_observed_phase_diagnostic.py`; log `q1_observed_phase_diagnostic_v1.log`.
The56-test numerical command and all its retained versions are recorded in
`q1_observed_phase_numeric.md`.

Source comparison to the completed archive PASS25 exact old functions or
explicitly checked extraction compositions:
`timeout 20s python3 /tmp/q1_observed_phase_source_review.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_observed_phase_source_review_v3.log 2>&1`.
The exact script and first failed literal-comparison script are retained at
`qualification/q1_observed_phase_direction_diagnostic_v1/preflight/`.
Independent workflow review found no material issue; `source_review.md` records
its scope. No models or confirmation bags were opened by review.

The sourced freeze command (same overlays/PYTHONPATH, ROS_DOMAIN_ID191) was
`timeout 60s python3 docs/codex/gesc_gaussian/v2/tools/q1_discovery_direction.py freeze --reference-version observed-phase-v1 > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_observed_phase_freeze_v1.log 2>&1`.
It PASSED:556 source files, unchanged2869 geometry receipts, two actual
recorded discovery run bindings,24 exact first diagnostic joins and21 installed
entry points. Frozen contract SHA256:
`d9ed31f52c9f088199fdf700076424b730e0248a143f9ace2495c8666527b45e`.
Historical originals and all three archived owner snapshots remain bound.

A separate input-only preflight checks every represented waveform and latent
vector without a kernel or objective call. Its first helper reached JSON
publication but omitted the existing analyzer's NumPy-scalar normalization;
it failed with `bool_ is not JSON serializable`, retaining script/log and no
published final receipt. The separately named helper v2 applies existing
`_q1_plain`, as the real batch already does. No frozen source changed and no
numerical field job was retried.

The same sourced domain191 command was
`timeout 60s python3 /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_observed_phase_direction_diagnostic_v1/preflight/check_inputs_v2.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_observed_phase_inputs_v2.log 2>&1`.
It PASSED:24/24 qualified observed input cycles,24/24 finite covered latent
vectors, four actual-blend matches within1e-12. These are input checks, not
reference accuracy or direction qualification. Original helper/log v1 remain.

Retained final receipts (paths relative to external V2 experiment root):

- `builds/initial/q1_observed_phase_integrated_v1.log`, SHA256 `479624f3108c9e7dc5301b3f63a9768131b544682f095e7d0d763b0176d79d78`.
- `builds/initial/q1_observed_phase_diagnostic_v1.log`, SHA256 `83a977097911113d5988be630d5a559674943d7274b6c9f480726ad10f437f4e`.
- `builds/initial/q1_observed_phase_source_review_v3.log`, SHA256 `1c464e4f5be722346c0f5e877b20571ff3cd96806eea2673944ed16d35569d0d`.
- `builds/initial/q1_observed_phase_freeze_v1.log`, SHA256 `ec2642e7de7119eabae93b5b59b3ce131d114f18b968216c0bf8fd230f60174c`.
- `builds/initial/q1_observed_phase_inputs_v2.log`, SHA256 `c6fb433b0b8d14c8fba026d8290802e58c3d1d98e43a26b3f5c474cc23b4b66e`.
- `qualification/q1_observed_phase_direction_diagnostic_v1/preflight/installed_preflight.json`, SHA256 `109c90c7df0e2970bf583fd4e4dd96396a73fb35e359eaec94294c2ec06d698b`.
- `qualification/q1_observed_phase_direction_diagnostic_v1/preflight/input_preflight.json`, SHA256 `f2891eea2e9db8638d7b7bb3aef9a6906af9aeb92227cd41c0ad65d912df1a8d`.
- `qualification/q1_observed_phase_direction_diagnostic_v1/preflight/source_review.md`, SHA256 `94d98d67edc3ac993a8f6e591d8f89386f5f1483e3d9de334e6dbd5cb7ab6cbf`.

Material checkpoint and exact dispatch release precede the single300s numerical
job. No qualification, confirmation opening, runtime tuning or M4 release is
authorized by this source/preflight pass. Read the new exclusive analysis
directory and later result record for the eventual numerical outcome.
