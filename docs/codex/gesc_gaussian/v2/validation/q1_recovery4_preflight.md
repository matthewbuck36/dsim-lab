# Q1 recovery4 preflight — 2026-09-09 UTC

Source correction passes233 final combined checks in5.38s; continuation routing
passes49 in2.64s. Exact commands, failures and hashes are in
`q1_filter_expiry_core.md`, `q1_filter_expiry_transport.md` and
`q1_recovery4_paths.md`. The final source handoff is
`../q1_filter_expiry_handoff.md`. No scientific qualification is claimed.

External V2 root: `/home/mattb/Experiments/GESC-Gaussian/v2/`.
The source-equivalence creator is retained at recovery4
`preflight/source_equivalence_creator.py`, identical to the invoked
`/tmp/dsim_q1_recovery4_equivalence.py`. Exact invocation from repository root:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 30s python3 /tmp/dsim_q1_recovery4_equivalence.py /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_filter_expiry_core_v6.log /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_recovery4_paths_v3.log /home/mattb/dsim-lab/docs/codex/gesc_gaussian/v2/q1_filter_expiry_handoff.md /home/mattb/dsim-lab/docs/codex/gesc_gaussian/v2/validation/q1_filter_expiry_transport.md /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery3/diagnostics/filter_startup_confirmation_residence/corrective_v1/equivalence.json > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_recovery4_equivalence_v1.log 2>&1
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 90s python3 docs/codex/gesc_gaussian/v2/tools/freeze_q1_contract.py --acquisition-version q1-primary-shadow-v1-recovery4 > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_contract_freeze_recovery4.log 2>&1
```

Both commands exit0. Contract binds549 source files,2869 unchanged geometry
receipts and21 actual installed console targets. All old source paths remain
represented. Exactly11 source receipts changed/added: two expiry-only runtime
owners and nine workflow/test/plan entries. Numerical `_evaluate_filter` source
was directly compared to the recovery3 archive and is byte-identical. Earlier
clean-prefix parity remains applicable after the final queue-capacity closeout;
the replay population is below both the old and new bounds, and final tests
exercise the changed capacity explicitly.

Paths relative to `qualification/q1_primary_shadow_v1_recovery4/`:

| Receipt | SHA256 |
| --- | --- |
| `preflight/source_equivalence.json` | `bd9c792f25bb24bc9843591cb9a229ded27a6a344363fac1981c5ef4dfc23fda` |
| `preflight/contract.json` | `8cd4db25ef3c70528df3b52066af18429cf554fe4aabb0eb370bf08c55619c64` |
| `preflight/installed_import_preflight.json` | `4006988030953bcf713619c134eb5d3248aa33b9f622da51eb01d13b5469dd7c` |

Actual read-only import preflight called `_q1_contract`,
`validate_acquisition_layout`, `imported_inputs` and `installed_entry_points`
from the sourced domain191 environment under timeout30s. Both original discovery
rows pass the unchanged analytical input validator, exact PASS safety/cleanup/
duration/spawn checks and expiry-free audit. All41 recovery3 closure artifacts
were rehashed unchanged. Neither metadata/bag/report copies nor new scientific
results were created. Captured environment is in the installed/import receipt.

The isolated symlink build resolves current Python sources and all21 targets.
There is no changed IDL, packaging, launch or installed configuration asset,
so an unchanged colcon build was not repeated. Context validation and diff
checks pass; process search finds no Gazebo or recorder process remaining.

Checkpoint/live dispatch receipt supplies the final release boundary. Exactly
two new confirmation runs are permitted, each125 simulated seconds after
readiness and240s process cap, with600s total (540s interrupt plus60s kill).
Only four qualified total inputs permit the unchanged analytical jobs. Prior
failed acquisitions and the independent confirmation-selection boundary remain
preserved. M4 is unreleased.
