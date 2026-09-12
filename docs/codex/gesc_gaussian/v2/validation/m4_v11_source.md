# M4v11 source registration validation

Status: SOURCE_VALIDATED; no V11 preparation or acquisition yet.
Authority: [adopted V11 plan](../m4_v11_draft_plan.md), including the prospective
V11-only development latency measurement-feasibility condition. Six production
owners are shared with previous versions. No numerical detector/direction or
control tuning is part of this milestone. Arrival remains sufficient; GOAL_HOLD
optional. C01/C02/C03/V10 originals remain retained.

External owner:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v11_source_v1/`.
All six before owners are pinned in `before_receipt.json`. Root orchestration
helpers reuse prior version preparation/release/dispatch/archive wrappers;
validation pins their exact code before/after. The selected environment and21
installed bindings must remain stable.

Sole source command executed from repository root:

```sh
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; export ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0; timeout --signal=INT --kill-after=5s 255s python3 -B /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v11_source_v1/validate_source.py --version focused_v1 --tests /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v11_source_v1/tests_v1.json > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v11_source_v1/focused_outer_v1.log 2>&1'
```

Internal230s pytest/5s termination,260s inclusive outer. Exact unique module
selection is retained in tests_v1.json and all entries were reviewed before execution. Preparation
requires passing source validation and verified source archive; no acquisition
is authorized by a source-only pass before frozen preparation/review/release.

## Completed evidence

Session4096 terminal/reaped0.676 unique checks PASS,160.293120485s inclusive
(pytest157.89s).806 source/helper/evidence pins stable;21 installed entries stable.
No skips/failures. Receipt `focused_v1/source_validation.json` SHA256
`70155ecffd11de4a2382e54e338677dd5d9c6063221fcf23ee4ded949994edcb`.
Full log/JUnit and six-owner before/after patches retained externally.

Root six-owner review, independent workflow review and independent root-helper
review PASS. Includes actual retained V10 YAML byte parity, all16 V11 schema/
launch selections, exact budgets/seeds, R8 private PDE binding on V11, original
first-opportunity/censor/median metrics, both observed development contrasts
without improvement demand, refusal of unavailable or forged endpoint evidence,
late nested receipt corruption, finite science failure, missing references,
shared daemon/strict process admission and missing/failed final reports.
Existing V10 censored-development release remains selectable and passing.

No detector/reference/control numerical tuning or new runtime mechanism was
introduced. Existing spawner recovery is selected only for V11. No ROS/Gazebo
acquisition, raw bag read or numerical qualification was part of this bundle.
Context validator and diff whitespace checks PASS. Source checkpoint/archive
precedes preparation; source, tests and all helpers remain held.
