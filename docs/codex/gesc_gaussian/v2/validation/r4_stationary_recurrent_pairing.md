# R4 stationary recurrent pairing source boundary

SOURCE_VALIDATION_PASS, 2026-09-10. The missing recurrent/stationary pairing is
implemented through existing detector, supervisor, Gaussian-fill and evidence
owners under the [adopted plan](../r4_stationary_recurrent_pairing_plan.md).
No numerical method, old wire, objective, controller ownership or historical
run result changed. No Gazebo or comparison was dispatched at this boundary.

The new schema1 `StationaryRecurrentFillRequest` embeds the complete recurrent
diagnostic and has its own canonical topic. Original receipt/steady leases,
history and persistence origin, frozen stationary samples, bounded design,
revocation, redesign and exact request/result identity remain enforced. The
existing recorder requires the selected typed topic even when it has zero
events. The existing validator/analyzer joins recorded diagnostic hashes to
nested requests and existing fill/event results, reports recurrent-specific
names and cannot fall back to an unrelated legacy request on failure.

## Build and actual owner checks

External evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/`.
New `build_interfaces_v1/` was built with `colcon --packages-select
ros_esc_interfaces --allow-overriding ros_esc_interfaces` from the existing
schema2 environment, under180 s. Build PASS in27.2 s; `interface_build.log`
retains output. Its generated new request serializes/deserializes, and selected
VerificationGuidance retains the schema2 publication sequence. The new
`environment.sh` sources that overlay and prepends canonical repository source.

| Boundary | Result | Elapsed and retained evidence |
| --- | --- | --- |
| Protocol/interface/real stationary detector DDS | 85 passed | 3.52 s; `detector_tests_v1_receipt.json`, all11 pins stable |
| Actual launch selected/delayed pose routing and legacy frontend regressions | 64 passed | 18.47 s; `detector_launch_v2_receipt.json`, all5 pins stable |
| Actual supervisor/Gaussian constructors, stopped verification, fit and revocation | 119 passed | 4.474455 s; `owners_focused_v1.result.json`, all12 pins stable |
| Existing recorder/validator/recurrent regressions in root batch | 93 passed | Included in6.779629 s root v1; production pins stable |
| New recurrent recording/CDR/SQLite/full-validator/analyzer checks | 21 passed | 2.520079 s; `root_tests_v3.json`, all8 pins stable |

Rows are scoped job results; suites overlap and are not an aggregate unique
test count. The protocol and owner records contain exact commands and individual
coverage: [protocol](r4_stationary_recurrent_protocol.md),
[adapters](r4_stationary_recurrent_owners.md). All jobs are terminal/reaped.

Root jobs use the new environment and the retained exact commands in
`run_root_tests.py`, `run_root_tests_v2.py`, `run_root_tests_v3.py`:

```sh
env -u PYTHONPATH bash -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/environment.sh; timeout --signal=INT --kill-after=3s 120s python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/run_root_tests_v3.py'
```

Each wrapper bounds pytest by110 s, records exact argv, elapsed time, exit and
before/after hashes. Initial root v1 retained109 passes/4 fixture failures in
6.779629 s: generated Python equality treats branch-inapplicable NaNs as unequal.
Root v2 retained19 passes/1 fixture failure in2.922039 s: serialized CDR padding
bytes vary despite unchanged fields. Root v3 uses the protocol's existing full
canonical field representation for identity assertions and retains actual CDR
and SQLite execution. No production change was made to make these fixtures
pass. Original failures/logs/receipts remain intact. Only the changed new test
file was repeated; already-passing legacy suites were not rerun.

Independent read-only review checked selected configuration, exact joins,
zero-event authority, unavailable-audit failure, missing/changed nested evidence,
wrong request type and malformed diagnostic/request topic. It identified the
fixture identity issue and a malformed-topic analyzer gap; the resolver now
rejects that gap before analysis. Legacy analyzer reason spelling was preserved.
The final launch review also found that Gaussian's explicit pose-topic
conditional omitted recurrent stationary selection. It now forwards the selected
algorithm pose for that pairing; actual frontend checks cover explicit/delayed
topics and preserve the rolling fill-topic selection. No further blocking issue
was found. Full protocol and numerical-core source
identity are checked in the component receipts.

## Remaining empirical boundary

These checks prove selectable source/transport behavior, not a complete Arm B
simulation. The scenario schema and private event evaluator still reject
recurrent/stationary; extend those existing routes under the next prospective
single-case plan before dispatch. The full comparison also still needs its
new version, science aliases/metrics, finite budgets and completed-development
release gate. Existing two global-arrival observations remain valid selected
development evidence. GOAL_HOLD remains optional. No old result is promoted.

Branch `feature/gesc-gaussian-robustness-v2`, HEAD3369cfc; all work uncommitted.
The material checkpoint is `checkpoints/r4_stationary_recurrent_source_v1/`
under the external V2 root. No physical, Pi, snapshot, V1, commit or push.
