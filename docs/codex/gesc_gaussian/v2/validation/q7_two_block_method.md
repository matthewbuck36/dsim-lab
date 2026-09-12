# Q7 two-block method source validation

Status: CLOSED_SOURCE_VALIDATION_PASS. Authority:
`../q7_two_block_method_plan.md`, explicitly selected by the user on 2026-09-09.
This remains work toward the two original goals: earlier circling/oscillation
convergence detection and improved direction while searching continuously.

## Result

The existing detector now admits explicit `centroid_two_block_v2`. Six equal
6-second position means form two adjacent 18-second means; their Euclidean
distance is compared strictly against 0.18m, with the unchanged inclusive
0.50m full-trajectory confinement guard. These are explicit prospective pilot
settings, not global default changes. Historical `centroid_windows_v2` retains
its sum of five adjacent distances; `pde_mean_v1` remains the default.

Core integration, interpolation, source-time admission, resets, latch, radius
and supporting five displacement values remain shared. The common score owner
recomputes the formula selected by typed `metric_mode`. Actual detector
configuration/publication, moving confirmation and candidate identity,
stationary Supervisor/Gaussian requests, recorder metadata/validation and
offline lifecycle joins bind the exact selected mode. Existing analyzer owners
receive the extended mode-aware contract through their current calls.

IDL fields/order are unchanged (comments only). No generated-schema rebuild
was needed. Q5 installed Python/resource symlinks resolve the current checkout.
The selected Gaussian stationary pose route admits both centroid modes, with
the existing disturbance relay routing. Q1/Q2 YAMLs and M4A source are unchanged.
No physical file, Pi/device, hardware, V1 branch or retained study was changed.

## Exact validation and retained evidence

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/q7_two_block_method_v1/`.
Each test process was bounded at 300s or less. Environment: clean PYTHONPATH,
Humble, Q2 local_setup, Q5 local_setup, then append the canonical
`extremum-seeking/src`; no source-package root prepended. DDS domains were
77/78/79 for separate workers; some transport fixtures explicitly select 78.

Definitive combined result: **400 PASS, 83.91s**, exit0. The exact selected-file
command, before/after hashes of source/interfaces/launch and selected tests,
elapsed time and log hash are in `root_final_v2_receipt.json`.
All hashed bytes were stable throughout the run. Invocation:

```bash
# After the environment setup in fresh_chat_handoff.md:
ROS_DOMAIN_ID=77 timeout 260s python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/q7_two_block_method_v1/root_final_validation_v2.py
```

That retained script invokes `timeout 240s python3 -m pytest -q` on all five
Q7 test files plus centroid core/policy/transport, Q3 admission/recording,
old detector contract, moving Supervisor/epoch binding, moving DDS and Q5
stationary DDS. Final log `root_final_v2.log` SHA256:
`40db54f798c575321ce7e6cbc0efd0978595ffe2c305b4ce6aa66bf91ce7fc4c`.

Additional focused evidence (overlapping, not additive independent trials):

- `core_v1.log`: 189 PASS,7.46s, under180s. Independent analytic two-block
  means, Q6 ideal-circle/fore-aft challenge samples, translated/large-loop
  negatives, unequal sampling/interpolation, threshold/radius and reset/latch
  cases, inherited detector and original-receipt admission.
- `transport_contract_v1.log`: 81 PASS,6.02s, under120s. Real detector DDS uses
  selected source/clock with a nonzero circling response and confirms once at
  36s; its score differs from the five-shift sum on the same support.
- `consumer_contract_v2.log`: 237 PASS,34.45s. Stationary request/fit selection,
  exact mode/score substitution rejection, moving candidate/12s expiry,
  recorded joins and legacy regressions.
- `consumer_dds_v1.log`: new-mode stationary fit/ack and moving activation/
  worker cancellation,3 PASS,23.84s. `consumer_legacy_dds_v1.log`: same retained
  old-mode routes,3 PASS,23.26s. Synthetic DDS inputs establish integration;
  the stationary fixture uses W3/.06 and is not the selected pilot setting.
- `recording_selection_v2.log`: 211 PASS,51.54s, including46 new cases;
  `recording_scenario_roundtrip_v1.log`: two appended full scenario
  roundtrips PASS,.84s. Final selection test files contain48 new cases.
  Actual frontend checks cover12 mode/readiness and12 disturbance combinations
  plus inherited defaults/explicit parameters.
- `recording_selection_installed_binding_v1.json`: Python owners and installed
  XML resolve current source; PASS,.89s, under30s. Agent exact commands, pins
  and source scope are in `recording_selection_receipt_v1.json` and
  `consumer_receipt.md` with associated command files.

Independent source review compared core and consumers against the pre-edit
archive and found no blocking arithmetic/identity/compatibility issue. Root
confirmed message field/order parity and unchanged M4A source hash
`9c57f7992cbbf3829f7cd70ac94944a1147c3c6eba23fa271ffeae13f9131b83`.
Context validator and staged/unstaged diff checks pass; checkpoint/archive
receipts are recorded in current status.

## Preserved failures and limits

`recording_selection_v1.log` retains33PASS/13FAIL: new fixtures incorrectly
expected five-shift averaging and a different string representation of0.50;
only those fixtures changed. `consumer_contract_v1.log` retains235PASS/2 setup
errors: the new fixture disabled bounds without disabling recenter; the existing
startup guard correctly refused it. The corrected fixture preserves that guard.

`root_final_v1_receipt.json` retains stable source with397PASS/2FAIL: two old
epoch-binding fixtures supplied an empty diagnostic mode. The new production
guard correctly rejected them. Fixtures now supply explicit historical identity,
and publication identity is additionally tested for the new mode. Production
was unchanged between the two integrated runs; only that test file changed.

The separate new and old DDS runs and first combined run emitted an unfetched
executor Future `Destroyable` teardown diagnostic despite successful DDS
assertions and process exit. It also occurred with the old metric in the same
teardown path; earlier retained Q5 logs did not show it. The exact callback
origin is not established. No owned process remained after those runs. The
final400-case log does not contain that diagnostic. Do not call all validation
attempts warning-free or infer real-world cleanup from this synthetic evidence.

No Gazebo pilot, fresh field acquisition, calibration replay, label/reference
evaluation or direction-performance job was run for Q7. The 36s history is not
measured basin-entry latency. Q6 ideal bounds still assume <=0.10s source gaps
and no pose noise; inherited0.5s runtime gap admission is not covered by that
proof. Original30% latency, direction targets and full combined holdout behavior
remain unestablished. Overall V2 remains IN_PROGRESS.
