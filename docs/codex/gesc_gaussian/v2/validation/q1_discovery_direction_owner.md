# Discovery direction diagnostic: analytical owner boundary

2026-09-09. Implemented the explicit diagnostic route under
[`q1_discovery_direction_plan.md`](../q1_discovery_direction_plan.md).
The original reference regressions pass: **78 tests in 16.68s**. No actual
field/reference job, confirmation access, acquisition, or parameter change
occurred in this source milestone.

The existing `evaluate_q1_direction_references` accepts the additive keyword
`diagnostic_contract_path=None`. Its default still requires both frozen
partitions, all48 targets and the passing nomination needed for confirmation.
The explicit route requires one unchanged discovery manifest, two discovery
traces and exactly24 original seed/target identities. It shares the existing
target validation, numerical loop, paired recorded-output comparison and
summary implementation. It returns `COMPLETE_DIAGNOSTIC`,
`qualification_status: NOT_EVALUATED`, `nomination: null`,
`confirmation: SEALED` and `pilot_released: false` after finite completion.
Missing or numerically unavailable anchors remain in the full population.

`_q1_discovery_direction_contract(diagnostic_ref, original_contract_ref,
target_files)` validates the exact historical closure/checkpoint/target/trace
receipts and the old analyzer snapshot. The checkpoint must bind the old
analyzer hash and the study closure; its archive/patch artifact hashes are
verified. Closure metadata must bind the original contract and selected
discovery receipts. Sealed confirmation artifacts are not recursively opened.
Every advertised trace/target must have an allowed discovery identity before
trace files are followed.

The effective validation contract retains the original scientific/acquisition
bindings and every original source path. Only the analyzer digest may change,
with explicit old/new lineage. The three new plan/workflow/test receipts are
mandatory; other new source paths and changes to other original owners reject.
`_q1_validate_contract` contains the same scientific/current-source checks
previously inside `_q1_contract`, which continues to verify its own receipt and
apply those checks without a waiver. The existing `_q1_verify_run` receives
the explicit effective contract. This avoids both an old-hash pretense and a
second input-validation pipeline.

All source/input receipts are checked before output creation, before each run's
first model instance, and after the batch. The pre-model check is outside the
numerical-error handler: integrity faults stop execution instead of becoming
missing-reference outcomes. Existing exclusive started/per-anchor/final
publication preserves partial evidence on a bounded failure.

The strict diagnostic JSON keys are `version`, `original_contract`,
`study_closed`, `checkpoint`, `old_analyzer_snapshot`, `frozen_targets`,
`analyzer_transition`, `current_source_files`, `input_traces`, `partition`,
`seeds`, `target_numbers`, `fixed_anchor_count`, `job_timeout_sec` and
`reference`. The version is `q1-discovery-direction-diagnostic-v1`; partition,
seeds, target numbers and cap are discovery,26090911/26090912,1–12 and300s.
Historical receipts preserve their original bytes. The actual freezer and
dispatch workflow belong to the parent task.

Exact original-regression command, cwd `/home/mattb/dsim-lab`, exit0:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH=extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_direction_references.py ros2_ws/src/ros_esc/test/test_v2_direction_reference.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_discovery_direction_owner_v1.log 2>&1
```

Log SHA256:
`820f38545eed9ca6712059cdf82453ef079a2ca2b8d194cac1b5f0be369a2c1c`.
There were no skips or failed attempts in this owner regression run.
`py_compile`, scoped `git diff --check` and the bounded v2 implementation-context
check passed. The independent reviewer compared the extension with the closed
source archive: the reference summary is unchanged, and the numerical loop
differs only by the added pre-model receipt check. Independent diagnostic
fixtures and parent integration/freeze evidence are separate validation work.

Analyzer source after this run:
`ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py`,
SHA256 `738d9a02e0f35d9a0dfacfe7a617a5a459c489d84c2657b7dd032d21e24e9e45`.
The original analyzer remains in the Q1 closed checkpoint with SHA256
`072c239e6ba6041f2a0b753ec1e422fa9fbc400759f895413e276de32ac6a1c6`;
the checkpoint manifest is
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/q1_closed_v1/manifest.json`,
SHA256 `78659061686d43c75217ba1ade254ead9b0474cccbab681cc5c59e8741f6dd7b`.
Only the analyzer and this source-validation note were edited by this owner.
