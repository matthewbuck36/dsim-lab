# Detector clock-admission correction validation

Status: CLOSED SOURCE VALIDATION PASS; scientific qualification remains open.
Authority: `../q3_detector_clock_admission_plan.md`.
Pre-correction source checkpoint:
`checkpoints/q2_v2_discovery_diagnostics_closed_v1/manifest.json`, SHA256
`add832e4fd397e1bf8b643a0b12784190fc243b47b260ee0e77bebcb73953745`.
It retains272 files,1111223-byte verified archive and264 external artifact hashes.

Independent actual-owner tests first demonstrate bounded leading state/pose
behavior against held source. Preserve their failures before implementation.
Runtime owner: existing centroid detector adapter; independent tests: the new
focused Q3 clock-admission suite. External logs live in
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/q3_detector_clock_admission_v1/`.
Use source Humble then the existing external Q2 overlay; append only
extremum-seeking/src to PYTHONPATH. Test ROS domain193 is reserved for this
bounded milestone. No Gazebo, scientific model/grid rerun or physical action.

The scientific result stays CLOSED_EVIDENCE_UNAVAILABLE. All20 recorded complete
histories fail the score independently of state-history loss. Source inspection
shows a possible callback-order fragility, but the recorded stale-or-future
notifications do not establish their exact incoming state. Passing new source
tests will not retroactively qualify the detector or direction policy.

Append exact baseline/final commands, pinned source hashes, focused regressions,
actual DDS outcomes, failures/skips and material closeout here as work completes.

## Held baseline reproduction

Three actual-node callback tests fail in0.40s under timeout60s/domain193:
the100ms-leading valid SEARCH revokes the prior valid state; leading standalone
pose replaces the admitted source prematurely; first leading SEARCH never drains
when the search gate is inactive. These reproduce the source ordering weakness,
not the unknown exact cause of historical Q2 reset notifications.

Original node SHA256
`09e189f65d4c9e7f6b95e8b6f9e9612ffefdbfa27009a0c129769a5de4679a9b`;
baseline test SHA256
`723fc802653a993a1ac3e42b549d4fedfb7c2d1be7d58e966defea305399ba42`.
Retained log under external `builds/q2_policy_runtime_v1/`,
`q3_detector_clock_admission_v1.log`, SHA256
`6e97d96db211ddb11ccc2448d41a727756d1214afbbd55b298962b3c7920ecc1`.
The exact test snapshot and command are preserved in that directory's
`q3_detector_clock_admission_baseline/receipt.json` and adjacent test file.
Subsequent logs use the new Q3 build directory above. Source implementation
was released only after these baseline receipts. Baseline command as retained:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/install/local_setup.bash
PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" ROS_DOMAIN_ID=193 timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q3_centroid_clock_admission.py
```

## Node correction and focused results

Held corrected node SHA256
`56f0d9b2c74af6bbbbf7ab3f05c738e921aded2e02b63807e06e6b14e81c7d78`.
The node reuses ClockAdmission, retaining original ROS and steady receipts.
Covered states drain before poses, including while the SEARCH gate is inactive;
the centroid watchdog uses a steady clock to expire paused-clock support.
Identity, recording revocation, non-SEARCH transitions, rollback and bounded
pending queues fence old support. Exact duplicates do not refresh history or
receipts. Standalone frame changes reset/reseed while preserving the epoch latch.
Rolling poses retain their existing binding and original steady receipt.
The positive configured stale limits remain effective; selected defaults stay
0.5s. The centroid core, shared helper and rolling binding are unchanged.

First expanded suite: `focused_v2.log`, **220 PASS / 5 FAIL in6.50s**.
Three new assertions inspected the logical SEARCH gate rather than effective
state authorization; queued non-SEARCH still fenced history. Two inherited
fixtures reused a previously received acquisition after a reset and expected
it to seed a new full18s history. The corrected fixtures begin at the next
genuine100ms acquisition and keep the full18s and latch assertions. No source
lease, window, numerical threshold or acceptance gate was relaxed.

Corrected suite: `focused_v3.log`, **226 PASS in6.70s**, timeout60s/domain193.
It covers the new clock admission tests plus existing convergence policy,
centroid windows, V2 epoch binding/origin and controller clock regressions.
Existing actual DDS centroid, epoch and controller-clock transport:
`transport_v1.log`, **5 PASS in2.51s**, timeout60s/domain193.
The new100ms adversarial ordering cases exercise actual node callbacks; the
separate DDS suite checks existing transport integration. Neither is a new
Gazebo experiment or scientific qualification.

Integration review identified an additional selected recorder contract mismatch:
standalone centroid legitimately emits an original receipt before source after
clock coverage, but the validator enabled that ordering only for rolling stream
identity. The bounded correction records explicit selected centroid admission
and its existing pose-freshness limit, with strict default and invalid-bound
checks preserved. Independent selected/full-validator tests pass below.

## Exact node and transport receipts

`test_receipt.json`, SHA256
`a1b29e53ef92918bcf9b41cb7fc98757c292d2137121defbc8d9f166c5df0d5e`,
retains every exact argv/cwd/log hash and the preceding failure boundary.
Commands for the passing node and transport checks, from repository root:

```bash
env -u PYTHONPATH bash -c 'set -o noclobber; source /opt/ros/humble/setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/install/local_setup.bash && export PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" && export ROS_DOMAIN_ID=193 && timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q3_centroid_clock_admission.py ros2_ws/src/ros_esc/test/test_convergence_detector_policy.py ros2_ws/src/ros_esc/test/test_centroid_windows.py ros2_ws/src/ros_esc/test/test_v2_epoch_binding.py ros2_ws/src/ros_esc/test/test_v2_epoch_origin.py ros2_ws/src/ros_esc/test/test_q1_controller_clock.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/q3_detector_clock_admission_v1/focused_v3.log 2>&1'
```

```bash
env -u PYTHONPATH bash -c 'set -o noclobber; source /opt/ros/humble/setup.bash && source /home/mattb/Experiments/GESC-Gaussian/v2/builds/q2_policy_runtime_v1/install/local_setup.bash && export PYTHONPATH="$PYTHONPATH:/home/mattb/dsim-lab/extremum-seeking/src" && export ROS_DOMAIN_ID=193 && timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_centroid_detector_transport.py ros2_ws/src/ros_esc/test/test_v2_epoch_transport.py ros2_ws/src/ros_esc/test/test_q1_controller_clock_transport.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/q3_detector_clock_admission_v1/transport_v1.log 2>&1'
```

Installed import check PASS for node, shared helper, recorder and validator;
all four resolve to the current source via the existing Q2 overlay.
`import_binding_v1.json`, SHA256
`e9c491170a0c1d450c42d9979448722be3691a69621d8136c4c69daaba50cab1`.
No rebuild was necessary: this correction adds no IDL or installed resources.
The receipt also verifies unchanged numerical core and shared-admission hashes
against the closed Q2 contract; it does not require the edited node to match old
scientific source. No old scientific inputs or models were rerun.

## Completed recorder and configured-limit checks

Explicit1s node limits: **2 PASS / 43 deselected in0.48s**, timeout60s/domain193.
Both750ms-leading state and standalone pose wait for clock coverage and retain
original receipts; a lead above the configured1s bound rejects. This is a
synthetic startup override, not a change to selected0.5s defaults.
`override_receipt_v1.json`, SHA256
`51e5dcd61ab08f0e571a230767335891825cf66cb3feeee171116e604d8e7317`,
retains the exact command, original226-test snapshot and final test pin.
Only the two new cases ran; no prior suite or DDS repeat.

Selected recorder contract: **24 PASS in4.10s**, timeout90s/domain184.
An actual node/core18s confirmation passes CDR serialization with original
receipt1017.9s before source/publication1018s. The canonical full validator
accepts the selected metadata, rejects unselected early receipts, premature
publication, stale source/receipt, wrong run/topic and malformed marker/limits.
Existing detector and rolling recorder contracts: **81 PASS in1.94s**.
The bag/YAML transport is substituted for this narrow contract fixture; missing
unrelated streams deliberately prevent a claim of full recording completeness.
`recording_contract_receipt_v1.json`, SHA256
`ea8c11065fbd27b4cfedfe73301ca08f2461fa790e20cda4400bdfe6c4af4d42`,
retains both exact commands and source/test/log hashes. New log SHA256
`0f4805912c3d4f3d863fc581e2aa51415caaabea4ad8f2f8d5b6e41679a613d1`;
regression log SHA256
`6fc086ae32f5cc9f601dcd22a94daee397cf6ffee817e5ed34c48e88d09f27c8`.

Held recorder SHA256
`8cc3b97cca64c32e1513e5faf8c896127c104aa569a5541b81a413ad8870f5c5`;
validator SHA256
`bcf63a963f178d4f2bf51b6b10fd27e5e49103aaa6e6349d8bbd954a051ab8d6`.
Root compared the pre-Q3 material archive: only the node, recorder, validator
and two inherited test-fixture start points changed among its ROS files.
Two new Q3 test files are additive. The numerical core, shared admission helper,
rolling binding and all other existing ROS source remain unchanged.
Context and diff checks pass. Handoff: `../q3_detector_clock_admission_handoff.md`.
Material checkpoint receipt is recorded in live status after archiving.
