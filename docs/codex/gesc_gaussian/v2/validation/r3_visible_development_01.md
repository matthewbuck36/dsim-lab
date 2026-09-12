# R3 visible attempt01: startup failure retained

INCOMPLETE/infrastructure_invalid, terminal and reaped, 2026-09-10. The sole
420s attempt ended in33.809723272s. No recording readiness or authorized motion;
no detector/verification behavioral result. Outer and inner scoped cleanup PASS,
all209 source/configuration/preparation pins unchanged during execution.

Exact command:

```bash
env -u PYTHONPATH ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 bash -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_runtime_v2/environment.sh; timeout --signal=INT --kill-after=2s 420s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_01/run_attempt.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_01/root_execution.log 2>&1'
```

External `development/20260910/visible_integrated_01/` retains prepared/source
pins, exact nested command, root/runner logs, attempt_result.json and scenario
summary. The partial bag, console, metadata and failed completeness are at
`runs/2026-09-10/v2_method_development_D_20260910_01/`. The failed gates remain.
The root wrapper's ATTEMPT_RETAINED means the failure and cleanup were saved;
it is not recording or behavioral acceptance.

Actual GaussianFill and SupervisorNode constructors both raised
`ValueError: unsupported convergence_metric_mode` in the shared
`stationary_fill_protocol.stationary_centroid_selected` allowlist before their
moving branch was reached. The recorder detected this at graph preflight and
stopped the target. GUI/server were started, then cleaned up. The small partial
bag does not justify full behavioral/direction analysis or promotion.

The startup omission is a bounded routing correction. Before a fresh attempt,
extend that existing helper to explicitly recognize recurrent robust rolling
simulation while leaving its stationary selection false and preserving old
selectors. Test the actual selected node constructors. Recurrent stationary
and physical/legacy combinations remain rejected. Do not rerun attempt01 or
rewrite any source pins/artifacts. A separately planned02 will use corrected
source, a new run identity and the unchanged development hypothesis/budgets.

Material pre-run source checkpoint:480 files,
`checkpoints/r2_recurrent_centered_source_v1/manifest.json`, SHA256
`1491ec08b5578b3d4960340dc8d01c2af7cf6dd0a9358b8453a1cca2c19da0bc`.
Git remains V2 HEAD3369cfc with uncommitted task work; no commit/push or physical
work. The fullblock analysis timeout still blocks a comparison.
