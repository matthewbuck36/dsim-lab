# Q4 committed-fill clock-admission validation

Status: CLOSED SOURCE VALIDATION PASS; scientific qualification remains open.
Authority: ../q4_committed_fill_clock_admission_plan.md.
Pre-edit material checkpoint is Q3 closeout, manifest SHA256
`d529084d92aa8038679d66fe3deda8ee0d1e7a642248d16cd9978a53af9c8616`.

External retained root:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/q4_committed_fill_clock_admission_v1/`.
Original two owner files are copied there with source_baseline.json. Independent
baseline failures must be preserved before implementation. Tests use existing
Q2 installed overlay after Humble; append only extremum-seeking/src. Focused
domain193 and independent transport184; every command has a finite timeout.
No old acquisition, bag, field/reference, threshold/grid or physical action.

A future committed_at currently rejects the envelope and discards an already
committed result. Producer cache/retry behavior requires a repeated command;
supervisor awaits composer and direction acknowledgments but sends no periodic
retry. This source issue is separate from Q2 score rejection and does not change
any closed scientific outcome. Q3 state/pose admission is CLOSED PASS.

## Held source baseline

`/home/mattb/dsim-lab/ros2_ws/src/ros_esc/ros_esc/modified_cost_node/v2_fill_activation.py`
SHA256 `0cf1d63372c0e5908c6f67688dc49a4a510b05c82c5cacf720b6695dbe97aafa`.

`/home/mattb/dsim-lab/ros2_ws/src/ros_esc/ros_esc/modified_cost_node/v2_objective.py`
SHA256 `ff27435e9358458e2387d9c2b8e820fabfd5a84b3f58a0f514658bfd1534cd83`.


## Baseline reproduction before source release

Two actual-owner cases fail as expected in0.45s, exit1, timeout60s/domain193.
A valid100ms-leading commit produces `activation envelope mismatch`; one delivered
result remains unapplied (generation0) after actual composer.poll reaches its
committed_at. No redelivery was supplied. Both original owner hashes above are
unchanged at this boundary.

`baseline_receipt.json`, SHA256
`7ea02b197c0e03e07c0b589d2781c0c7be4b4126b230c8682a6eac9a01f0f6de`.
Log SHA256 `f169799f06a9a422177345862fd4edfc9e77357dd4b1d153fd99f29898419eed`;
exact baseline test snapshot SHA256
`5b5caf82d44b7da624b3c7aebfd3ce84c757f27a1d7c8e9f9e5dab895b55e6d1`.
The baseline source copies, command and failing snapshot are retained externally.

```bash
env -u PYTHONPATH bash -c 'set -o noclobber; source /opt/ros/humble/setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/install/local_setup.bash && export PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" && export ROS_DOMAIN_ID=193 && timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q4_committed_fill_clock_admission.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/q4_committed_fill_clock_admission_v1/baseline_v1.log 2>&1'
```

## Corrected source and focused evidence

The existing activation owner holds one detached, fully validated next-generation
commit with its stable identity and first receipt. The initial clock lead is
bounded500ms; there is no pending sensor-style expiry. Admission rebuilds the
staged swap from current state, preserving unrelated affine updates. Original
commit/deadline provenance and bounded applied identity/receipt/stamp ledgers
remain intact. Same-origin rollback retains durable authority but suppresses
composition before an already installed commit's time. Origin faults fence use.
The existing composer polls admission before source/state gates and composition.

Held activation SHA256
`27ed8fc0663659046d2128252de951cf5e9afce42f7ea9629ed1e3a39a5a341c`;
composer SHA256
`4f41e6bef0f0228e236c42aaa6f8f64a6b670c30d6d65be300e531beaf4e389c`.
Only these two existing runtime owners changed; two Q4 tests are additive.
No fill geometry, registry mathematics, supervisor/controller, IDL, recorder,
scientific configuration or shared source-sample clock owner changed.

Independent focused suite **157 PASS in6.28s**, timeout60s/domain193, covering
new actual-owner callback cases plus inherited fill transactions, V2 objective
runtime and clock admission. Cases include durable coverage20s later and delivery
after the preparation deadline, original receipt and retry identity, exact lead
boundary, invalid envelopes/geometry/digests, capacity/ordering, supersession
with intervening affine updates, origin faults and rollback output suppression.
Old-law output continues while waiting; new digest appears only after coverage.

`focused_receipt_v1.json`, SHA256
`4d51ec207d075780df9dc66490654cda0dfed01a618308970bc8e4c6d4c9973a`,
retains exact commands, original/final test snapshots and all source/log hashes.
Focused log SHA256
`3fd13c39330a88fe93377e9a33c64c8bff5c4af65acd960645a492817a669f5a`.
Command, repository cwd:

```bash
env -u PYTHONPATH bash -c 'set -o noclobber; source /opt/ros/humble/setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/install/local_setup.bash && export PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" && export ROS_DOMAIN_ID=193 && timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q4_committed_fill_clock_admission.py ros2_ws/src/ros_esc/test/test_v2_fill_transactions.py ros2_ws/src/ros_esc/test/test_v2_runtime.py ros2_ws/src/ros_esc/test/test_v2_clock_admission.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/q4_committed_fill_clock_admission_v1/focused_v1.log 2>&1'
```

Installed import binding PASS under a20s cap, with no ROS initialization.
Activation, composer and existing Gaussian runtime resolve through the installed
Q2 symlinks to held source. `import_binding_v1.json`, SHA256
`b49e9363293665e9f316d55f030a4b89b5f88e90a953fd2eb6c9dc65b08aa987`.
No build is needed: there is no new interface or installed resource.

## Actual ROS transport

New DDS case **1 PASS in0.40s**, timeout60s/domain184, first attempt.
A supplied authoritative FillResult uses the existing registry/version/hash
owners, with origin1000s, receipt1010.0s and commit1010.1s. Exactly one result
is delivered to the real ModifiedCost2D node. Four real objective publications
show the empty digest before/during waiting and the matching committed digest
and new objective revision after clock-only drain; the ledger applies once.
This proves the composer acknowledgment. The synthetic result does not claim
new supervisor/worker candidate acquisition or scientific acceptance.
`transport_receipt_v1.json`, SHA256
`e48d12f6f377808cf319a5ea4757591c82700cf38fa3ee0a81ed5bfabc7ffac0`;
log SHA256 `a347fe86f0a684ec5e11a53edff4303c9e1bd2fd0addfeef1dc1aa39b7283c28`.

Existing fill and moving-pipeline DDS regression **3 PASS in21.33s**, timeout90s.
The command requests domain184; unchanged fixtures explicitly select177 and185.
It covers real worker/commit/composer behavior and existing supervisor
acknowledgments/cancellation separately from the new future-result ordering.
Exact command and runtime/test hashes are in transport_regression_receipt_v1.json,
SHA256 `b397d3c090f8387a2f32889f4d1ab265c654454060863c34cbba966f7ecb7979`.
Regression log SHA256
`7b95fd42c0af49ef263b3f44f1d38871e4ec378dddb16fc110a9d97a2efe61f3`.
No failed corrected run or test retry occurred. The original2 failing baseline
cases remain preserved. Root reviewed both diffs against exact saved originals;
context/diff/checkpoint and the material archive are recorded at closure.

## Limits and next work

Q3 remains closed sourcePASS; Q2 science stays CLOSED_EVIDENCE_UNAVAILABLE with
confirmation sealed. No Gazebo, bag/model/reference/grid rerun or hardware
occurred. This fixes durable source admission and does not qualify score,
direction or whole-run behavior. Next is the Arm B centroid/stationary adapter,
then one finite settling/direction development decision and the unchanged16-run
pilot. Handoff: ../q4_committed_fill_clock_admission_handoff.md.
