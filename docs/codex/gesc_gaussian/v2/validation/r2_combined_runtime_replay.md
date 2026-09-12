# Final combined recurrent runtime replay

DEVELOPMENT_COMPONENT_PASS, 2026-09-10. The actual final production core passed
all200 distinct retained control histories:57/57 positives,0/142 negative
confirmations,0 repeated confirmations;1 gray drift remains outside pass/fail.
No production source or threshold changed. This supports bounded component
feasibility, not closed-loop or source/fill qualification.

Prospective authority:
[r2_combined_runtime_replay_plan.md](../r2_combined_runtime_replay_plan.md) and
[v2 bookkeeping correction](../r2_combined_runtime_replay_v2_plan.md).

## Preserved failure and exact execution

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/`.
V1 remains in `combined_runtime_replay_v1/`: terminal1 in.630189237s before ANY
production detector evaluation. Its population assertion caught the helper
checking `gray` instead of the exact retained `gray_drift` contract label.
It loaded the expected200 unique histories but incorrectly counted that one
withheld row as positive. V2 corrects only this scope spelling; no sample,
positive/negative truth label, model threshold or expected denominator changes.

```bash
timeout --signal=INT --kill-after=2s 118s env PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/combined_runtime_replay_v2/run.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/combined_runtime_replay_v2/execution.log 2>&1
```

Terminal0, COMPLETE,17.825662935s including fixture loading, actual core replay,
D-prefix replay and output writing. Internal110s deadline remained untriggered.
There was no unchanged numerical retry and no bag/model/Gazebo/holdout access.

## Population and measured outcomes

Raw population228 family rows: all99 arc fixtures, all96 oscillator-v2 fixtures,
all33 independently prescribed static-cancellation cases. Only28 shared exact
R1 fixture IDs were deduplicated; their original integer-nanosecond and XY sample
hashes agreed. `aliases.json` retains every original family/contract/label and
canonical identity. All original noise, irregular times and off-grid spikes
were supplied to production `RecurrentGeometryDetector.update` unchanged.

| Declared positive class | Distinct cases | Detected | First time min / median / max |
| --- | ---: | ---: | --- |
| Static | 3 | 3 | 30 / 30 / 30s |
| Circle | 29 | 29 | 42 / 42 / 84s |
| Oscillation | 25 | 25 | 48 / 48 / 66s |

Every positive first accepted through its corresponding branch. All142 distinct
negative histories had zero confirmation; the single gray .005m/s noisy drift
also had none and remains excluded from acceptance. Component-class grouping
is used only for positives; original kinds for negative/gray histories remain
in the alias contracts. Earlier arc-only unsupported-oscillation labels remain
visible and become in-scope under the prospectively declared combined method.

The core consumed240200 original source points and emitted20000 completed
branch-evaluation rows, including incomplete or rejected supports. All source
updates continued after first acceptance, testing the actual OR/confirmation
latch. No branch was replaced, disabled or pre-evaluated outside the core.
Every control has its own explicit epoch and fixed final RecurrentConfig.

## D first-SEARCH prefix limitation

The optional replay used only existing V9 DEVELOPMENT D exports. Its first
observed ready SEARCH epoch starts at ROS0s; first ready clock is2.4s. The
historical run exits SEARCH at68.6s, earlier than the declared122.4s ready+120
cutoff. Exactly1949 original readiness-admitted poses span2.365–68.597s;
55 support/status rows were retained. The new core produces no candidate
before that historical exit.

This positional counterfactual stops at the real first intervention. It cannot
establish whether the new detector would confirm within120s if SEARCH continued,
or reconstruct subsequent motion, live receipt admission or collection behavior.
No old D result is reclassified and no post-intervention history is pooled into
this first SEARCH epoch.

## Integrity and retained owners

Directory `combined_runtime_replay_v2/` contains `prepared.json`, exact
`control_contract.json`, `aliases.json`, `supports.jsonl`, `v9_d_supports.jsonl`,
`result.json`, `receipt.json`, helper and terminal log. All7 receipt-pinned
artifacts and20 selected production/fixture/input pins were independently
verified after completion; source remains unchanged. Runtime implementation
and prior focused/DDS evidence are in
[r2_recurrent_detector_runtime.md](r2_recurrent_detector_runtime.md).

Result SHA256:
`fbda85bd857ce5e94837bdbce5af767d20ebe9f5a7d0867d31936f90f2337bff`.
Receipt SHA256:
`e5dc518b6b78d2bfd038c91d13b2307a2a8bab941f49d54c5d6a201c406cb09b`.
Core SHA256 remains
`b10fa55d49373493327369385f1b5964d0fae8a7461111724745c5d9cf5c7920`.
No status/handoff edit, commit or integrated simulation was performed here;
root owns release/checkpoint and the next bounded empirical decision.
