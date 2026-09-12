# R2 centered guidance publication revision validation

SOURCE_VALIDATION_PASS, 2026-09-10, under the
[prospective correction](../r2_centered_guidance_revision_plan.md).
The [earlier source boundary](r2_centered_verification_runtime.md) remains
retained. No Gazebo or behavioral result follows from this correction.

## Reproduced defect and bounded correction

The actual MovingSupervisor DESIGN transition calls the actual SupervisorNode
publication method before PREPARE. The timer publishes again after PREPARE at
the same ROS tick. The earlier guidance used that timestamp as unique identity;
the changed command expiry caused the actual controller to return
`conflicting centered guidance for exact state` and zero its command.
The retained pre-fix job has one failure and one diagnostics pass in 1.361 s.

VerificationGuidance now explicitly uses schema 2 with monotone
`publication_sequence` and canonical full-AlgorithmState `state_sha256`.
Same-tick publications remain legitimate; the controller requires the exact
state stamp/hash and retains each exact state's latest proposal. Identical
latest-sequence/payload repeats do not renew original receipts. Older sequence
rollback or conflicting same-sequence payload stops authorization; a later
fresh sequence may recover after the normal checks. The sequence frontier
survives clock authorization resets. Existing state/filter revision admission
and all numerical motion/stage/safety guards are unchanged.

DESIGN-before-PREPARE ordering is preserved. Its early guidance is invalid zero
with reason `centered_preparation_pending`; that bounded wait does not fabricate
a controller-fault event. The following publication carries the original
preparation expiry. Existing AlgorithmState, CandidateSnapshot and AlgorithmEvent
generated field maps in the new overlay exactly match retained Q5 types. The
new guidance schema had no retained simulation bag before this revision.

ControlDiagnostics already records the right quantities: nominal GESC remains
in its dedicated field; the supervisor adjustment plus GESC equals the centered
combined proposal; combined and final vectors equal the actual published
command. The real callback test verifies these values. No diagnostics source
change was needed. Final-controller saturation flags retain their existing
meaning; the supervisor proposal is already bounded by its selected controller.

## Exact retained executions

Root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_runtime_v2/`.
Result SHA256:
`5bbbbe4cd6b62445dc69d456c995ea85dc309a110b974c9b35af461cf113e938`.

Every job ran as
`env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 bash <root>/<job>/command.sh`.
Exact commands/logs/JUnit receipts and scoped hashes are retained per job.

| Job | Budget | Result |
| --- | --- | --- |
| `reproducer_v1` | `timeout --signal=TERM --kill-after=5 60 python3 -m pytest` on `test_centered_guidance_revisions.py`, earlier interface overlay | Exit 1; 1 failed/1 passed; 1.361 s; pre-fix source copies retained |
| `build_interfaces_v1` | `timeout --signal=TERM --kill-after=5 240 colcon ... build --base-paths ros2_ws/src/ros_esc_interfaces ... --symlink-install` | Exit 0; one package; 32.7 s |
| `focused_v1` | 90-second timeout, `test_centered_guidance_revisions.py` | Exit 0; 6 passed; 1.400 s; all 8 scoped pins unchanged |
| `regression_v1` | 180-second timeout, `test_centered_verification_runtime.py test_v2_controller_motion.py` | Exit 0; 106 passed; 6.667 s; all 8 scoped pins unchanged |

The final jobs cover the actual repeated DESIGN publication, pre-preparation
zero, both state/guidance arrival orders, distinct full-state revisions at one
tick, sequence rollback/conflict, original duplicate receipts, clock reset,
the complete centered timing/safety owner and legacy controller behavior.
The initial two-case reproducer overlaps these final checks and is not additive
evidence. All jobs are terminal/reaped; no skip or timeout occurred. Context and
scoped diff checks pass.

Use the new `<root>/environment.sh` for current selected runtime: it preserves
the prior Q2/Q5 source overlays and appends the fresh schema-2 interface overlay.
The earlier `centered_runtime_v1` overlay remains retained for its historical
source result. D3 owns the corresponding selected lifecycle sequence/hash audit
and its separately retained tests; that audit must pass before visible dispatch.
Root owns source checkpoint/status/handoff and any next empirical release.
