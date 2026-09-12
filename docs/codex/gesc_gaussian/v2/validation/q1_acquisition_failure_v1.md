# Q1 acquisition v1 — closed infrastructure failure

Outcome: INCOMPLETE, zero verified input runs; no scientific result.
Started `2026-09-09T09:59:33.431521+00:00`; elapsed2.028807308s.
The first reserved run `q1-primary-shadow-v1-discovery-residence-26090911`
failed in the installed `record_run` wrapper with `StopIteration` before a run
directory was created. Its process exited1 without timeout. Later cases stopped;
cleanup passed with no new nodes or session processes remaining.

Retained root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1/`.
Authoritative files are `acquisition/acquisition.json`, `acquisition/started.json`,
`acquisition/summary_26090911.yaml` and `acquisition_console.log`.
No `study_manifest.json` or bag was created. Confirmation results were not opened.

The frozen contract was `preflight/contract_v2.json`, SHA256
`570b335c95b034c9da6d350f73fa20c9b7d6be9c8a77b8c14bf2ba714626f1bf`;
release `preflight/dispatch_release.json`, SHA256
`d2d062dd8f9f423ec3ed380de88d1d4a70aec4443c20f8fd209eafa91e7f1710`.
The source checkpoint remains `checkpoints/q1_preacquisition_v1/manifest.json`,
SHA256 `9a1dd6dd09eda9b8f0f4b1c28464d1b5ec203cb8e89f54380fc923856e82b309`.

Exact invocation after sourcing base Humble and the isolated local overlay:

```bash
ROS_DOMAIN_ID=191 PYTHONPATH="/home/mattb/dsim-lab/ros2_ws/src/ros_esc:/home/mattb/dsim-lab/extremum-seeking/src${PYTHONPATH:+:$PYTHONPATH}" timeout --signal=INT --kill-after=60s 1140s python3 docs/codex/gesc_gaussian/v2/tools/acquire_q1.py --contract /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1/preflight/contract_v2.json > /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1/acquisition_console.log 2>&1
```

Result: exit1. The passing module/import and launch-frontend checks did not
validate distribution lookup by the installed console wrapper. Diagnosis and
any new dispatch belong to `../q1_acquisition_recovery_plan.md`. This fixed
attempt remains failed; no algorithm failure or improvement is inferred.
