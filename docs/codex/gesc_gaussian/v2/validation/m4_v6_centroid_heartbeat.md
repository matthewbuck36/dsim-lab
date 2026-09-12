# M4 v6 centroid invalid-status heartbeat validation

Source validation PASS, 2026-09-10 UTC. The adopted
[source amendment](../m4_v6_centroid_heartbeat_plan.md) adds a selectable
simulation reporting policy. It leaves numerical history, confirmation,
candidate evidence and the existing one-second coverage requirement unchanged.
M4v5 remains CLOSED_INCOMPLETE; this source work cannot reclassify its D run.

External evidence directory:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_centroid_heartbeat_v1/`.
Each named receipt contains the exact argv, environment, cap, log hash and
before/after source hashes. The baseline used the staged external test file;
subsequent bundles use the two new repository heartbeat test modules.

| Attempt | Result | Pytest time | Inclusive time / cap | Scope |
| --- | --- | ---: | ---: | --- |
| `baseline_v1` | 4 PASS, 12 deselected | 25.08 s | 25.919240719 s / 45 s | Actual old-default DDS route; assertions retain its required-coverage failure |
| `focused_v1` | 42 PASS, 5 FAIL, 4 deselected | 65.68 s | 66.6256 s / 240 s | New selection and enabled DDS cases; fixture failures retained |
| `focused_v2` | 47 PASS, 4 deselected | 65.64 s | 66.5306 s / 240 s | Corrected exception/selected-argv fixtures; production unchanged |
| `relevant_v1` | 369 PASS | 55.76 s | 56.937804596 s / 240 s | Existing detector/selection/consumer regressions plus four default-off cases |
| `focused_cycle_v3` | 4 PASS | 49.97 s | 50.781589065 s / 240 s | Strengthened continuing-pose VERIFY, configuration and confirmation-event assertions |
| `purity_before_v1` | 2 FAIL | 0.79 s | 1.651688227 s / 30 s | Retained real clock-frontier side effect before correction |
| `focused_pure_v4` | 56 PASS | 107.54 s | 108.430554233 s / 240 s | Final corrected heartbeat/selection source |
| `relevant_binding_v2` | 155 PASS | 5.84 s | 6.718143510 s / 120 s | Final binding/clock/epoch/transport regressions |
| `root_final_v1` | 4 PASS | 23.53 s | 24.450589563 s / 120 s | Actual stationary/moving two-block consumers and inherited fit |

Baseline tracked 623 runtime sources plus the external staged test. Both
focused bundles tracked 625 files. Each receipt reports stable before/after
pins. The first focused failures concerned Humble's exception for an empty
parameter value and missing Timekeeper/provenance arguments in full-validator
fixture metadata. Correcting those fixtures retained the actual coverage and
selected-contract assertions. The failed source/test snapshot is retained at
`focused_v1_source/manifest.json`; no failed attempt was overwritten.

| Receipt | SHA256 |
| --- | --- |
| Pre-edit manifest | `a4e5eee11717ded87d76564d5897c855e5a0ef43afb9ad7dc6d3e25c43b46cbc` |
| `baseline_v1_receipt.json` | `ed0efaecf2b55b53f2e5d84865dc94486e8a1d6559c7945d5f81951ebacf6a4b` |
| `focused_v1_receipt.json` | `3bdc7f47eb6dd890e08ad4a192de9c4400f1fc2db92371845eeab74c80721657` |
| Failed focused snapshot manifest | `1b62d8c26b9c633afd0598c8de8861deda3a0d2ada12effe3e20605b5a324aa1` |
| `focused_v2_receipt.json` | `b78ccedc9a46530aa5a34180e13fbf28e8458491961e225b648fc729da0128f5` |

The owner strengthened the enabled cycle fixture to exercise more than two
simulated seconds of VERIFY with continuing rejected poses, in addition to its
pose-withheld coverage interval. The previous fixture is retained in
`focused_v2_source/`, and only the four changed cases ran in `focused_cycle_v3`.
Those fixture edits did not change production.

Subsequent review identified a production issue beyond those fixture fixes:
the empty-status readiness check called the clock-mutating binding path.
The adopted plan now includes its narrow captured-time correction in the
existing `v2_binding.py` method. `purity_before_v1` retained two failing
assertions in 0.79 s (1.651688227 s inclusive), receipt SHA256
`c9e575c40f7ab916612f22f191e034e68390d791db1d4c4ea81414253068e77d`.
The seven-file pre-correction snapshot manifest SHA256 is
`81873b3fd2c6a2d65b5e3085ccb6eeed312e645c4f96b62a711806a756271dce`.
The captured-time correction then passed its new focused, relevant and root
gates: 215 checks on the final source, with stable 625-file before/after pins.
Across the milestone, 475 unique test identities passed (365 earlier unchanged
regressions, 56 new heartbeat checks, 50 additional epoch checks, and four root
consumer checks). This aggregate is not 475 tests rerun on the final source.
All failed attempts and intermediate source copies remain retained.

## Root integration gate and closure

After the source owner finished those checks, independent review passed and
all runtime sources were held, root ran the prospectively saved additional
120-second inclusive gate through the same exclusive receipt wrapper:

```
timeout --signal=INT --kill-after=1s 124s /usr/bin/python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_centroid_heartbeat_v1/run_tests.py root_final_v1 120 ros2_ws/src/ros_esc/test/test_q7_two_block_consumer_transport.py ros2_ws/src/ros_esc/test/test_q5_legacy_interface_compatibility.py
```

This exercises actual stationary/moving two-block consumers, delayed-worker
cancellation and the inherited fit path. It complements the heartbeat and
detector regressions rather than rerunning those bundles. The wrapper uses the
clean Humble/Q2/Q5 environment, localhost domain189; the existing two-block
consumer fixtures explicitly select domain78. Run sequentially after all other
DDS work. The outer 125-second bound includes wrapper exit; the test/receipt
allowance remains 120 seconds. A failed or timed-out command is retained and
requires a bounded correction before a differently named attempt.

Root verified the 625 current source pins, two supporting pins, all eight owner
receipt/log hashes and the final root receipt. Exactly five original sources
changed: detector node, its existing V2 binding readiness helper, Gazebo launch,
scenario schema and recorder selection. The other 618 original pins remain
unchanged, including numerical methods and strict coverage validators. Two
new test modules complete the seven-file implementation footprint. Independent
review closed the clock-frontier finding and found no remaining source blocker.

The final consumer log contains one asynchronous `Destroyable` exception
message; all four test bodies passed and pytest exited zero. Independent
read-only review found the same diagnostic in retained Q7 `consumer_dds_v1.log`
and `consumer_legacy_dds_v1.log`. Deferred teardown is consistent with the source,
but the exact callback/timing is unavailable and the existing fixture does not
assert executor.shutdown's return value. This is not warning-free transport,
exhaustive callback-drain proof or Gazebo cleanup qualification. The milestone
starts no Gazebo acquisition.

Final owner hold: `heartbeat_hold_v1.json`, SHA256
`2c51e6ec4761669bb62bd211996b39aea23ee8ef7affad62ab5ea7be59ef10ac`.
Root receipt: `root_final_v1_receipt.json`, SHA256
`913b73b4a649ca0321cd64b91d2510dc7439893d41871c6dc3752230a14b0d76`.
Corrected focused receipt SHA256
`92f66ca2b1317a6bf6bd03d16388b12116d5ecf6948323e5ce0b266312028b90`;
final binding receipt SHA256
`badfa7809f6f77128e097e6908eae8a2c58b2f22d6b93dce11e5644e8ea6ca9c`.

Context validation and `git diff --check` passed before the final root test;
the live status records the material checkpoint and archive after this report.
No detector/motion tuning, new simulation or holdout release follows solely
from passing these source checks. Both research goals remain open.
