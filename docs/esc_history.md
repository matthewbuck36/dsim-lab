# Preserved source and experimental evidence

The active checkout contains original ESC methods and V3. Historical Gaussian
implementations, fixed recipes, distributed runtime owners and their policy
tests are preserved outside the active package/install. Their prior failures
and acceptance limits have not been relabeled.

| Reference | Meaning |
| --- | --- |
| `main` at `acb59020ac96d8ec67e8764092c6c51c01b7ea07` | Original received repository; baseline method/configuration comparison |
| `feature/gesc-gaussian-robustness-v1` at `1af67c6` | Final frozen V1 |
| `feature/gesc-gaussian-robustness-v2` at `d1779b6` | Accepted selected V2 simulation closeout |
| `experiment/gesc-gaussian-v2-5hz-20260924` at `e726774` | Retained 5 Hz experiment source; not physical qualification |
| `archive/pre-v3-refactor-20260928` at `e726774` | Ref before this structural refactor |

The verified [pre-refactor archive and receipts](/home/mattb/Experiments/GESC-Gaussian/v3/refactor_20260928T195707Z)
retain the full working tree, including then-uncommitted files, plus old
build/install/log trees. `pre_refactor_worktree.tar.gz` has SHA256
`eea8ffecf5fbc9a21038b3e74d7c160dfb11c7ad0f606ea9f50177ee68ee4a3e`.
`retired_active_sources/` retains moved source/tests at their original relative
paths; `retirement_manifest.json` records verified destination hashes. Build
trees are evidence only and must not be sourced as the active overlay.

Inspect a historical file without switching the current checkout:

```bash
git show archive/pre-v3-refactor-20260928:ros2_ws/src/ros_esc/setup.py
```

Old reports may refer to source paths no longer active. Resolve them against
the report's recorded commit, the frozen ref or retained source directory;
do not infer that an archived implementation is currently installed.

## Physical V1 remains protected

The [V46 restoration handoff](/home/mattb/Experiments/GESC-Gaussian/physical_integration/physical_v1_wholesale_restore_20260924_v46/HANDOFF.md)
records wholesale restoration of all three physical packages and original
scripts from the pre-V2 archive `20260915T220724Z`, with a fresh build/install.
The authorized encoder offset is **54 degrees**, fixed Arduino sampling is
approximately **5 Hz**, and nominal arm speed is **20 RPM**. The prior
354-degree instruction and optional 10/15 Hz firmware are superseded.

The [970bc1b3 review](/home/mattb/Experiments/GESC-Gaussian/physical_integration/physical_v1_wholesale_restore_20260924_v46/operator_run_970bc1b3/REVIEW.md)
records completeness PASS, roughly 45 seconds of driving after readiness,
approximately 1.2 m net displacement, 4.98 Hz sampling, measured average arm
speed about 17.2 RPM and operator Ctrl+C stop. No Gaussian fill occurred; full
escape or global-source convergence was not tested. These are retained
observations, not a new live inspection or a V3 physical result.

The [autonomous physical ledger](/home/mattb/Experiments/GESC-Gaussian/physical_integration/arm_automation_20260922/LEDGER.md),
[V3 fault inventory](codex/gesc_gaussian/v3/fault_inventory.md), and
[initial physical-constraint plan](codex/gesc_gaussian/v3/plan.md) preserve the
failure history and design motivation. V2 physical commissioning remains
paused and unqualified. Prior source, firmware, failed runs and diagnostics
remain preserved. No Pi deployment or physical changes are part of this
repository refactor.

For the active work, use the [accepted refactor plan](codex/gesc_gaussian/v3/refactor_plan.md)
and [live status](codex/gesc_gaussian/v3/refactor_status.md). The earlier V1/V2
phase plans and their workflow scripts remain historical evidence, not the
active runtime or an extra V3 orchestration framework.
