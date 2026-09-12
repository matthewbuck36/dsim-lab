# M4v10 preparation

2026-09-10: PREPARED, no acquisition at this boundary. Existing exclusive
`m4_workflow.prepare('m4-pilot-v10')` passed in56.435649s under600s cap, with
all755 frozen source/runtime pins stable and covered by the608-case passing
source validation union. Session8888 is terminal/reaped.

Contract: `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v10/preflight/contract.json`,
SHA256 `501a04748edfb47c3848e6ac2b84e512144ce09810875f3b73728b13dad84a3f`.
Preparation receipt: external
`development/20260910/m4_v10_source_v1/preparation_v1/receipt.json`.
The preparation driver and outer log are in the same `m4_v10_source_v1` root.

Exact preparation command:

```bash
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=TERM --kill-after=5s 600s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_source_v1/prepare_once.py > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_source_v1/preparation_outer_v1.log 2>&1'
```

The adopted [plan](../m4_v10_arrival_comparison_plan.md) fixes method
`recurrent_arrival_v10`, seeds26091011–14, four visible development and twelve
fresh confirmation cases on previously exposed conditions. Arrival within0.5m
is the success criterion after valid local recovery; GOAL_HOLD is optional.
The development release requires complete usable science, B/D local recovery
and arrival, and observed D continuous acquisition. Missing paired latency
endpoints remain unavailable. No tuning or slot replacement is permitted.

Suite budget15800s, scientific reservation1400s, block labels240s, references
45s each, summary10s, freeze/report40s. The public dispatcher remains the sole
acquisition owner and enforces the new completed-development release before
confirmation. Its outer invocation sends SIGINT at15680s with120s final kill
grace, preserving the15800s maximum. Cases remain900s including cleanup.

Independent frozen scenario audit PASS130 checks in1.267195s,20 pinned inputs
stable; receipt `scenario_frozen_audit_v1.json`, SHA256
`c9f25a34379ed25741a4cd21995fb39c1c452d9dad32b4b24afdf0eec973a98a`.
Independent workflow audit PASS4.386159s,755 source pins/21 entries unchanged;
receipt `workflow_frozen_audit_v1.json`, SHA256
`297234cb26daba76a9f206d8521a2f38359d7ba0d847d64475d17f1883264db1`.
Both receipts are in the external preparation root. Sessions10541/32275 are
terminal/reaped. Actual launch, selector, typed topics, source/runtime binding,
arrival, stage durations, populations, geometry receipts and budgets match
the adopted plan. A wrapper audit prompted only a prospective external helper
receipt-finally correction; source/contract bytes remain unchanged.

Preparation archive/release receipts follow in current live status. No
numerical method, production source, historical run,
physical environment, V1, commit or push changed during preparation.
