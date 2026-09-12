# Q1 recovery3 acquisition paths — 2026-09-09

Status: bounded source and focused tests PASS. No contract was frozen, no
acquisition dispatched, and no retained bag revalidated by this task.
The selected `q1_acquisition_recovery3_plan.md` requires four fresh runs;
there is no import/resume exception or analytical input-schema change.

`q1_acquisition_layout.py` now admits exactly the additional acquisition version
`q1-primary-shadow-v1-recovery3`, rooted at
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery3/`.
Scientific version, four seeds/partitions, acquisition bounds and strict
single-root/run-ID rules remain unchanged. Original/recovery1/recovery2 paths
retain their previous validation behavior; unknown versions still fail.

The freeze owner binds recovery3's amendment, `q1_event_attribution_plan.md` as
`source_correction`, and recovery2's exact prior acquisition/closure receipts.
Before any output, recovery3 additionally requires the prior one-case
INCOMPLETE boundary, zero qualified inputs, no later/confirmation dispatch,
passed safety/cleanup, complete125s exposure and final zero. It verifies the
closure's hash-bound original completeness file and requires the sole failed
check to be producer identification for exactly the CONFIG detail
`centroid_windows_v2 source-time configuration`. Neither the original report
nor its failed classification is overwritten or accepted as a new Q1 input.

The inspected recovery2 closure remains SHA256
`7dea4e42af6acb843b3b896f7928e20705c65521d4757d9b13ba34e0053e6335` at
`qualification/q1_primary_shadow_v1_recovery2/acquisition_closed.json` under
the external V2 artifact root.

## Validation

Context preflight and scoped `git diff --check` PASS. Exact focused command:

```bash
env -u PYTHONPATH bash -c 'source /opt/ros/humble/setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash && export PYTHONPATH=/home/mattb/dsim-lab/extremum-seeking/src:$PYTHONPATH && timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_recovery_paths.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_recovery3_paths_v1.log 2>&1'
```

Exit0; **36 passed in2.39s**, no warnings. The environment uses the sourced
isolated overlay without prepending the stale `ros_esc` source package metadata.
Tests exercise actual existing `execute_suite(..., dry_run=True)` command and
metadata equivalence for all four cases under each permitted acquisition
version. Synthetic receipt fixtures verify old behavior, exact recovery3
lineage, refusal of extra failures, another unidentified event, unsafe closure,
opened confirmation or altered original report. The freeze-main fixture checks
the distinct geometry and acquisition recovery receipts and exact plan paths.
No test initializes ROS nodes, evaluates numerical fields or runs Gazebo.

## Source boundary

| File | SHA256 |
| --- | --- |
| `tools/q1_acquisition_layout.py` | `91ccbe5718f483b8403262b3a7d9b593669b022bae456e8cd0066decce762a6a` |
| `tools/freeze_q1_contract.py` | `973469339960a3ad6e160591c0357e6fc19dcd8def990026831e9d92a331eb59` |
| `ros2_ws/src/ros_esc/test/test_q1_recovery_paths.py` | `0c7e188ee8362aadf1948ed9f55816cff688a64a50d82a8e7b5885e6012fe2f2` |
| `builds/initial/q1_recovery3_paths_v1.log` | `c3eca1fb9e49b4395a1d978f82ed48cf02eba752fd367feb1056840bcad5b205` |

Tool paths are relative to `docs/codex/gesc_gaussian/v2/`; log paths are relative
to `/home/mattb/Experiments/GESC-Gaussian/v2/`. Parent owns diagnostic validation,
source freeze/checkpoint and dispatch release. These path checks establish no
scientific qualification or M4 readiness.
