# Q1 recovery3 preflight — 2026-09-09 UTC

Attribution correction tests PASS115 in4.31s; recovery routing tests PASS36 in
2.39s. Exact commands and hashes: `q1_event_attribution.md` and
`q1_recovery3_paths.md`. The separately saved corrected validation of recovery2
passes all60 checks; all15 original retained artifacts remain unchanged.
The original acquisition remains CLOSED INCOMPLETE.

The deferred acquisition-only diagnostic passes all7 checks: original run ID,
exact target argv/resolved scenario,125s readiness duration, safety/cleanup,
first pre-ready spawn and original input-binding receipts. Position error is
0.000026675512m and wrapped yaw error0.000038546346rad; no fitted offset or later
sample substitution. Exact source/command/log are under recovery2 `diagnostics/`.
`acquisition_preflight.json` SHA256
`8d9e2dc194462a18d1afc749174f60b2f7ccdfe54da50856e342e48fbaf4545b`.
The original full source set correctly reports intentional validator/workflow
changes; the diagnostic independently verifies the unchanged five launch,
geometry and selected-config receipts with the existing binding API. This is
not a qualified-input import or a relaxation of default source verification.

Recovery3's exact contract was frozen with:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=191 timeout 60s python3 docs/codex/gesc_gaussian/v2/tools/freeze_q1_contract.py --acquisition-version q1-primary-shadow-v1-recovery3 > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_contract_freeze_recovery3.log 2>&1
```

Exit0;544 source receipts,2869 unchanged geometry receipts and21 actual installed
console targets. External qualification root is
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/`.
Contract `q1_primary_shadow_v1_recovery3/preflight/contract.json` SHA256
`01ffc684d20a68b9e155b78ec8b4bd1cf3466667d1bac4b6c7476df1b2fdf9d4`.
Adjacent `source_equivalence.json` SHA256
`0eda455e3ab429742856aa086f778d0143c717ea9fba82cfa598969bb54a2946`
records direct equality of scientific keys, resolved cases, geometry and caps.
The only changed existing receipts are validator, routing/freezer and routing
test. Runtime, IDL, model, gains, launch/assets and packaging are unchanged.
The existing symlink build and21 actual installed targets resolve correctly;
no unchanged build or Gazebo launch check was repeated.

Display`:0` passes `timeout 10s xdpyinfo -display :0`. No Gazebo or recorder
process remained before release (process search exit1 means none found).
Context validator and `git diff --check` pass. Checkpoint/dispatch receipt in
live status completes the material boundary and defines execution authority.
No component research qualification or M4 release is implied.
