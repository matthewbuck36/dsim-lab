# R4 stationary recurrent adapter validation — 2026-09-10

Implemented under the adopted [pairing plan](../r4_stationary_recurrent_pairing_plan.md).
The existing supervisor and Gaussian stationary adapters now select the exact
diagnostic/request classes and topics from `stationary_fill_protocol`.
Recurrent selection uses the existing recurrent validator and checks both
history and persistence against the original Timekeeper origin at initial
admission. Centroid parameter arithmetic remains exclusive to centroid modes.
The redundant supervisor moving-only guard was removed; centered motion still
requires rolling simulation. Constructors declare the recurrent topic inputs.

Original receipt/steady leases, accepted evidence, stopped verification,
candidate cost evidence, request/result ledgers, duplicate behavior, frozen
pose/cost deques, fit deadline, redesign fields, authority revocation and atomic
commit remain in their existing owners. No estimator, controller, sampler or
message from the old mode was changed by this adapter work.

Focused result: **PASS119/119**, including **14 new recurrent owner cases**,
3.61 s pytest / **4.474455028 s inclusive**, exit0, all12 scoped source/test pins
stable. This covers actual constructors using retained selected startup
parameters plus explicit stationary/legacy-verification overrides; a numerical
recurrent circle confirmation serialized through its actual generated type;
real stopped verification and typed request; preserved original clock-leading
receipt and candidate evidence; duplicate lease; persistence-before-origin,
cross-type and stop rejection; actual shared fit from original frozen deques;
completed duplicate replay; and deadline/stop/origin/run revocation during the
real estimator before commit. Existing stationary and recurrent moving startup
regressions passed. The superseded recurrent/stationary rejection assertion was
updated while physical, nonrobust and stationary+centered rejection remain.

Exact command (repository root):

```sh
env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/environment.sh; timeout --signal=TERM --kill-after=5s 115s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_r4_stationary_recurrent_owners.py ros2_ws/src/ros_esc/test/test_r3_recurrent_startup.py ros2_ws/src/ros_esc/test/test_q5_stationary_centroid_adapter.py ros2_ws/src/ros_esc/test/test_q5_stationary_gaussian_contract.py ros2_ws/src/ros_esc/test/test_q5_stationary_fill_protocol.py'
```

The external orchestration imposed an inclusive120 s timeout, retained stdout
and stderr, and compared pre/post SHA256s. Artifacts are under
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/`:

- `owners_focused_v1.command.json`: exact argv/cwd/cap and12 original source pins;
  SHA256 `a08c5f5d287850bf783abe7fe70ac5fc09f715ac752925def68357611b7db00f`.
- `owners_focused_v1.log`: full test output;
  SHA256 `d9429a2256183ecd47894eb2b7e5e5ba824798a2082d5eea88214ed07c9d652a`.
- `owners_focused_v1.result.json`: elapsed/exit and original/final source pins;
  SHA256 `07132266e326a5a1313e21033d0e73c96487c441255df5a070a453771765f41f`.
- `owners_scope.patch`: reviewed four-owner diff against the immutable
  `checkpoints/r3_arrival_source_v1/source.tar.gz` baseline. This captures the
  existing untracked adapters that plain `git diff` omits.

Scoped `git diff --check` passed. No Gazebo, bag scan, matrix or physical work
was dispatched. These results establish the adapter source boundary; empirical
stationary recurrent Arm B behavior remains pending the separate integrated
development case. Root owns common evidence integration, navigation and final
milestone checkpoint.
