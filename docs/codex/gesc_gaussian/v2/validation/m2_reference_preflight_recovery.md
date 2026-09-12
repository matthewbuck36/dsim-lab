# M2 reference reader recovery validation — 2026-09-09 UTC

The bounded caller correction is implemented and verified. The M2 binding
reader now searches each node's `parameters` subtree for `robot_description`,
excluding the separate `parameter_types.robot_description: string` metadata.
The generic `_find_parameter` and its ambiguity semantics are unchanged.

This follows `../m2_reference_preflight_recovery.md`. The original failed
launcher, Python invocation, source snapshot and absent original output namespace
remain as recorded in `m2_reference_launcher_note.md`. No scientific reference
job was run during this correction, and no numerical setting, population,
denominator, live-capture requirement or geometry check was relaxed.

## Focused checks

From `/home/mattb/dsim-lab`, the context check passed:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
```

The exact retained launcher is
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_reference_preflight_recovery_checks_v1.sh`.
It uses `set -eo pipefail`, sources `/opt/ros/humble/setup.bash` and the retained
`builds/initial/install/local_setup.bash`, and prepends the repository's
`ros2_ws/src/ros_esc` and `extremum-seeking/src` to `PYTHONPATH`.

```bash
timeout 180s bash /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_reference_preflight_recovery_checks_v1.sh tests > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_reference_preflight_recovery_tests_v1.log 2>&1
```

Exit 0: **100 tests passed in 5.86 s**. The launcher executes:

```bash
python3 -m pytest -q ros2_ws/src/ros_esc/test/test_v2_direction_reference.py ros2_ws/src/ros_esc/test/test_v2_bag_replay.py
```

The four new realistic capture fixtures exercise the full binding caller with
value/type metadata together, absent values, conflicting values and incorrect
captured geometry. They use temporary configuration files and a synthetic Git
blob owner; no recorded bag or field model is evaluated. The successful fixture
also asserts that the unchanged generic helper still treats an unrestricted
value/type search as ambiguous. AST-extracted `_find_parameter` source is
identical to HEAD, SHA256
`80f6011945eedd25bd92034399ee9f7cec383f9f9a7482621ecd53af28a114b5`.

## Eight-input configuration preflight

```bash
timeout 180s bash /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_reference_preflight_recovery_checks_v1.sh bindings > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_reference_binding_preflight_v1.log 2>&1
```

Exit 0: **all eight bindings passed in 1.458169621 s**. The retained script is
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/m2_reference_binding_preflight_v1.py`.
It verifies the frozen inventory hash and exact development seed list, calls
only `_v2_direction_recorded_binding`, and records each run's parameter-file,
recorded-launch, selected configuration, URDF and captured XML hashes. It replaces
`truth._model`, `truth.evaluate_raw_cost` and the harmonic integration entry point
with functions that raise if called. The final receipt reports zero model
constructions, zero field evaluations and zero holdout inputs opened.

Passed seeds: 19801, 19811, 19851, 19901, 19911, 19931, 20001, 20031. All checks
retain the recorded launch selection, filter/model/transform file hashes,
historical URDF and captured live robot geometry requirements. No bag messages,
reference targets, paired method outputs or field values were generated.

## Frozen source and artifact identities

All values below are SHA256 of exact file bytes. Source paths are relative to
`/home/mattb/dsim-lab`; artifact basenames are under
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.

| File | SHA256 |
| --- | --- |
| `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py` | `17b9231d0d8ada8835a61574f15d3492d3c4b780b153be9873b7e283260df7cb` |
| `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/v2_direction_reference.py` | `614332ebbaa0d654b11b8f0c7304bf980ea3e7d693172e471dc999d703f51aed` |
| `ros2_ws/src/ros_esc/test/test_v2_direction_reference.py` | `f293a75165979e6cc0af7b62d4cbff0ed0464bb4b5cee732d40a58da36baccf2` |
| `docs/codex/gesc_gaussian/v2/m2_reference_plan.md` | `cb1493928c5bbb03f9ca787156c55b0a380bdfc2b445295d21d7a65cbda4a225` |
| `m2_reference_preflight_recovery_checks_v1.sh` | `60bc6480942629f5dff537271b118c398f6c4892b604bfe9fc74251beae234df` |
| `m2_reference_binding_preflight_v1.py` | `5f93cf57e4b55e4f7a7f54a63841e332980a91981e4fe92793f9d1cdfc3d6117` |
| `m2_reference_preflight_recovery_tests_v1.log` | `3b0276895199f2853252766d006226bd48270cb4e36f89f2ce2b5e8131e24794` |
| `m2_reference_binding_preflight_v1.log` | `045909299bef76b2b9c9f78dcb19dc8c5023db16d8bf000f944282d40a664eda` |

`git diff --check -- ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py`
passed. The caller and regression files are fixed for the root owner's next
checkpoint. The separately planned fresh scientific execution remains pending;
these checks establish reader/configuration correctness, not direction quality.
