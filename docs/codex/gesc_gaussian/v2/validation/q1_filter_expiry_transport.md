# Q1 filter expiry: independent transport and adversarial validation

2026-09-09 UTC. **PASS at this bounded source boundary: 47 tests in 1.45s.**
This implements the independent test assignment in
[`q1_filter_expiry_recovery_plan.md`](../q1_filter_expiry_recovery_plan.md).
The actual `CustomFilter` ROS node recovered fresh output after an intentionally
missing first raw-cost delivery. This is source recovery evidence, not a field
experiment, direction-quality result, or acquisition release. Recovery3 remains
closed incomplete; its failed confirmation input is not reused here.

## Exercised behavior and ownership

`test_q1_filter_expiry_transport.py` creates the actual selected filter node and
one synthetic publisher/subscriber driver on isolated `ROS_DOMAIN_ID=186`.
It uses real ROS wire types, DDS subscriptions, the node's simulated clock and
timer, the existing synchronization/adapter owners, and the unchanged
`gesc_filter_full_rotation.json` numerical filter. It does not instantiate the
source, objective composer, controller, supervisor, or Gazebo. The typed
objective fixture declares a consistent empty-fill objective and finite
synthetic costs; it is not a sampled field or stationary reference.

The finite fixture sends 108 distinct acquisition timestamps at 30Hz while
advancing `/clock` at 10Hz. Each group of three source headers leads the held
clock until its next covering tick. The first raw component is deliberately
omitted while its provenance, augmented value and objective metadata arrive;
later complete bundles use alternating component orders. Checks establish:

- Expiry retires the incomplete joins and resets numerical history. Pose and
  encoder support survives with its original source and receipt timestamps.
- The first recovered published diagnostic has at most one rolling sample,
  zero completed revolutions, no qualification and zero averaging blend; its
  finite instantaneous fallback output is available.
- Healthy publication continues for the remaining 30 clock ticks, with at least
  90 total outputs and recovered source times reaching at least4.5s. Source,
  admission, original oldest receipt and output publication remain within the
  unchanged500ms bounds.
- Valid retired bundles retransmitted at three later clock times do not recreate
  either owner's pending entries or cause another numerical reset.

`test_q1_filter_expiry_adversarial.py` independently exercises the actual pure
synchronizer and real adapter with the existing fake-node numerical fixture.
All24 cost-component permutations remain inert when valid retired messages are
resent after500ms. Original pose/encoder receipts are unchanged; no output or
pending join is manufactured. Wrong run/frame/origin, source-key mismatch,
nonfinite geometry/cost, empty arrays, invalid objective revision/hash/arithmetic,
invalid/future receipts, and explicit source revocation retain hard fault
behavior. A revocation using the source owner's next sequence poisons the same
model-time key and is idempotent. Clock rollback clears support, and a genuinely
new context clears the previous retirement set. These checks complement the
owner's broader regression suite; they are not DDS tests of every permutation.

## Exact retained commands and outcomes

All commands ran from `/home/mattb/dsim-lab`. Each invocation sourced ROS and the
isolated overlay; none prepended the package source directory to `PYTHONPATH`.
The DDS fixture also has an internal45s overall wall deadline and bounded
per-delivery waits. There were no skips.

First actual transport run, **1 passed in1.31s**, exit0:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
ROS_DOMAIN_ID=186 PYTHONPATH=extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_filter_expiry_transport.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_filter_expiry_transport_v1.log 2>&1
```

Initial adversarial run, **43 passed, 2 failed in0.87s**, exit1, retained:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
PYTHONPATH=extremum-seeking/src:$PYTHONPATH timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_filter_expiry_adversarial.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_filter_expiry_adversarial_v1.log 2>&1
```

One failure was a fixture assumption: pure `ObjectiveIdentity(revision=0)` is
permitted, so the malformed-revision fixture now uses−1. The second exposed a
real omission: a retired typed objective with internally inconsistent weighted
arithmetic bypassed the check formerly reached during joining. The adapter
owner restored the existing finite/arithmetic tolerance before benign retired
discard. An independent future-receipt case was also added. Neither correction
changes numerical gains or accepted scientific criteria.

Final independent combined run, **47 passed in1.45s**, exit0:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
ROS_DOMAIN_ID=186 PYTHONPATH=extremum-seeking/src:$PYTHONPATH timeout 90s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_filter_expiry_transport.py ros2_ws/src/ros_esc/test/test_q1_filter_expiry_adversarial.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_filter_expiry_transport_v2.log 2>&1
```

Context validation passed with
`timeout 20s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`.
The preceding uppercase `V2` invocation was rejected by the phase-name parser
and did no work. Scoped `git diff --check` passed. Only the two new test files
and this record were edited by the independent transport-test owner.

## Hash boundary

Log paths below are relative to
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/`.

| Retained log | Bytes | SHA256 |
| --- | ---: | --- |
| `q1_filter_expiry_transport_v1.log` | 98 | `b632ba3b5d75d336650a26fbf5403abf707ec37cfb411ae61bc5620f7427d6ca` |
| `q1_filter_expiry_adversarial_v1.log` | 4716 | `d3776f3829ee8b4db2a465469dcf1c254bf2fc5cca1c80d104252700697f1ee5` |
| `q1_filter_expiry_transport_v2.log` | 99 | `1189773ad23f4a7ef1ebc2bcbeac874ca9dd4bb301ec9e6bd792ae3b52ff594a` |

Source paths are relative to `ros2_ws/src/ros_esc/`. These hashes were captured
after the final independent test and are an explicit boundary, not a claim
about subsequent owner changes or the later integrated checkpoint.

| Source | SHA256 |
| --- | --- |
| `test/test_q1_filter_expiry_transport.py` | `5c1ced5c399ffe7d36c52a48de9b1c528fc47e37f4a8da96e45fe0ab7b0a3183` |
| `test/test_q1_filter_expiry_adversarial.py` | `08d1e29af77da04a2abef2987f33cd3b66d8db2f1b66a94e8fc2550509290790` |
| `ros_esc/filter_node/rolling_gesc.py` | `4661a66500065f651b7def10de42c91acb51890de920e722720a56365512014e` |
| `ros_esc/filter_node/v2_runtime.py` | `9a82e7035d43c1c7cb3d1cf34e34deb73823993507fc287dc1e4cd815945edec` |
| `ros_esc/filter_node/filter_node_script.py` | `715d90fc8758669a7c80156ce16d0f40635fb269da5e8befeae41ce6aff930ab` |
| `ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json` | `f1cfd23a9c60e08780a4477f23cacc80a9e0c75b127448291e321756de7a2dce` |

The injected omission is controlled test input. This result does not establish
which callback or scheduling event triggered the preserved failed simulation;
recorder ordering cannot establish the filter subscriber's callback order.
No historical scientific data, detector parameters, labels or reference results
were evaluated or revised by this validation.
