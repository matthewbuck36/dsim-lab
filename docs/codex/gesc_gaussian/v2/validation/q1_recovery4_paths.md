# Q1 recovery4 finite import routing — 2026-09-09 UTC

Status: wrapper implementation and focused tests PASS. This task did not freeze
a contract, dispatch Gazebo, read confirmation science, or qualify a study.
The selected `q1_acquisition_recovery4_plan.md` permits exactly two previously
accepted discovery inputs and two fresh confirmation acquisitions. Scientific
version remains `q1-primary-shadow-v1`; acquisition version is
`q1-primary-shadow-v1-recovery4`, with the exact corresponding external
`qualification/q1_primary_shadow_v1_recovery4` root.

The layout/freezer/acquisition wrappers preserve the two original recovery3
planned entries and normal input rows, including old run IDs, directories,
receipts and PASS reports. Only the final two planned entries receive recovery4
identities. Their resolved scenarios, visibility and launch argv must equal
the old plan, allowing only the exact run-ID substitution in launch argv.
Coordinate-preflight, geometry, detector and reference receipts/settings remain
equal. No analytical input schema, numerical owner or runtime owner changed.

Before output, before each dispatch, and after the last case, the wrapper
rehashes the imports and calls the existing `_q1_verify_run` on each original
row. It checks the exact accepted ledger, closure, original recording/safety/
cleanup/spawn PASS and 125-second completion. Changed inputs stop later
dispatch. The two new cases use the existing `execute_suite` owner. The
600-second budget starts at wrapper entry for recovery4; every dispatch
reserves one 240-second case and 60 seconds for cleanup, including a second
budget check after input/environment hashing. The original versions retain
their previous identities and timer semantics. Results explicitly report
`imported_inputs` and `newly_dispatched`; only four accepted normal rows produce
a study manifest.

## Explicit source-equivalence receipt

`freeze_q1_contract.collect_source_paths(acquisition_version)` is the shared
read-only collection API for preparing source equivalence and freezing the
contract. Recovery4 retains every recovery3 source path, rehashes current
contents, and adds current source/tests, tools and the two new amendments.
The separate `preflight/source_equivalence.json` is not included in its own
source set. Its required schema is:

```json
{
  "schema_version": 1,
  "version": "q1-recovery4-source-equivalence-v1",
  "status": "PASS",
  "prior_contract": {"path": "...", "sha256": "..."},
  "expiry_audit": {"path": "...", "sha256": "..."},
  "valid_nonexpiry_path_unchanged": true,
  "scientific_confirmation_opened": false,
  "source_changes": [
    {"path": "...", "old_sha256": null, "new_sha256": "...", "classification": "workflow_or_test"}
  ],
  "evidence": [{"path": "...", "sha256": "..."}]
}
```

The exact old/new source delta must match this proof, with no removed paths.
`runtime_expiry_only` is allowed only for filter `rolling_gesc.py` and
`v2_runtime.py`; other changes must be `workflow_or_test` within V2 documents/
tools or the existing ROS test directory. Every nonempty evidence receipt is
hashed. This validates the explicit reviewed change boundary; it does not
infer mathematical equivalence merely from filenames or a PASS string.
Parent-owned source review and correction tests supply that evidence before
freeze/release.

The import block also binds the exact prior contract/acquisition/closure,
`input_26090911.json`, `input_26090912.json`, and the integrity-only expiry audit.
Recovery3's preserved closure SHA256 is
`79de12268086546592cba04beb937fd428dec1ee7542beb37a81255c9f51327e`.
Its audit result SHA256 is
`1f01e293c3a97b44bf789356b8c1f4117ec36184c5d73a2afaeb5a614fd14fc4`,
at `diagnostics/discovery_expiry_audit_v1/result.json` below that original root.
That earlier read-only audit found contiguous diagnostics, no reset-counter
jumps/regressions, and zero instances of either pending-expiry reason. It
opened no cost/pose/vector/detector/performance values. No bag audit was repeated
for the routing implementation.

## Focused validation

Context preflight and `git diff --check` PASS. Exact final command:

```bash
env -u PYTHONPATH bash -c 'source /opt/ros/humble/setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash && export PYTHONPATH=/home/mattb/dsim-lab/extremum-seeking/src:$PYTHONPATH && timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_recovery_paths.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_recovery4_paths_v3.log 2>&1'
```

Exit0: **49 passed in 2.64 seconds**, no warnings. Tests cover exact import/
dispatch routing, unchanged original bytes, normal input-validation invocation,
changed/failed input or source-proof rejection before output, import changes
before the second dispatch, budget reserve, original-version behavior and
actual existing-runner dry-run argv equivalence. The final freezer assembly
fixture checks retained old source paths and the exact two imported plans.
Routing fixtures use synthetic files and mock runtime/environment/normal input
owners; the dry-run checks use the actual runner without starting ROS/Gazebo.
Actual retained-input binding and source-equivalence validation remain required
in parent-owned preflight.

All attempts remain under the external `builds/initial` directory. The initial
`q1_recovery4_paths_v1.log` records 48 PASS in 2.46 seconds. After adding the
freezer regression, `v2.log` records 48 PASS/1 FAIL: the mock intercepted the
new recovery3 contract read as though it were a historical recovery3 read.
Restricting that mock to the recovery4 case fixed the test; runtime/wrapper
source did not change for this failure. The `v3.log` command above differs from
the preceding test commands only in that retained log suffix.

## Stable source and log boundary

| File | SHA256 |
| --- | --- |
| `tools/q1_acquisition_layout.py` | `b0a43ad648354c58da4422ce0c6bea97e3d20ac71dbb1abeab788180cedc8be8` |
| `tools/freeze_q1_contract.py` | `904de51ef33206d588c092d3113880a24ce4d3d23bed49a7c72884ea2ce6c88d` |
| `tools/acquire_q1.py` | `dffcad7a657dc15a30dca58f3d6bae803152e20e44d001e00a8b6c33da0deece` |
| `ros2_ws/src/ros_esc/test/test_q1_recovery_paths.py` | `b64c355b700394e652c3b8f5af29d91951d4a503d13ea972b9d83c43292e51dd` |
| `builds/initial/q1_recovery4_paths_v1.log` | `3f8cf7d8ce22fd5b1cfd396c3a6ac8594852ae6ea01bfcd5174341022cb46e14` |
| `builds/initial/q1_recovery4_paths_v2.log` | `7988895133bf14bf08d7d0b49b4f92f475ca2b1f4db0ad9c391cb1e29e0bb9ab` |
| `builds/initial/q1_recovery4_paths_v3.log` | `b00ac6e23ffb7ea56bbe24b8dc7f811faae404e80cad78f69c7c4cf2283b7f6d` |
