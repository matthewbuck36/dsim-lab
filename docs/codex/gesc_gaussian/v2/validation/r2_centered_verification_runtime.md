# R2 centered verification source validation

SOURCE_VALIDATION_PASS, 2026-09-10. Implements the separately adopted
[runtime plan](../r2_centered_verification_runtime_plan.md), following the
12/12 required ideal-kinematic result. No Gazebo, physical run, new comparison,
raw-profile qualification or behavioral pass is implied.

## Implemented behavior

The default `rolling_neighborhood_v1` retains moving GESC and its 12-second
verification deadline. Selected `centered_tracking_v1` freezes first observed
arrival within .08 m of the candidate center no later than acceptance+8 s,
records that exact time, then permits collection until min(arrival+12 s,
acceptance+20 s). Re-entry cannot renew admission. Existing raw cycles,
pretrigger support, profile comparability, ranking and Gaussian-fill guards
remain authoritative. The state-machine cap and adapter deadlines both select
the new mode explicitly; initial DESIGN retains its separate preparation cap.

The supervisor evaluates the measured moving-target law with the existing
Directional_Controller and exact selected .5/5 gains, .1/.5 speed limits. It
publishes a typed `VerificationGuidance` proposal bound to the exact state,
run/stream/frame, candidate/epoch, admitted pose and immutable stage clocks.
The controller alone publishes cmd_vel. Missing, conflicting, stale, expired,
wrong-identity or malformed guidance yields zero; valid guidance applies only
to VERIFY and initial DESIGN. An admission later than its exact state stamp is
also rejected. Every proposal passes the existing operating-bounds/active-fill
command sweep, with yaw+pi/abs(v) for reverse motion; unsafe or invalid geometry
cancels the candidate and publishes invalid zero guidance.

The optional new topic becomes recorder-required only for selected centered
mode. Launch forwards one controller configuration to both numerical consumers.
Recurrent detector forwarding uses `/gesc_gaussian/v2/recurrent_convergence_diagnostics`;
the supervisor accepts its separate typed confirmation contract and explicitly
rejects recurrent+stationary startup pending that adapter. Recurrent detection
is not inserted into the legacy centroid mode tuple or arithmetic.

AlgorithmEvent adds constant 12, with exact detail `moving verification
collection admitted`, VERIFY state and named candidate/epoch values. Existing
serialized fields are unchanged. `wire_compatibility.json` compares generated
AlgorithmState, CandidateSnapshot and AlgorithmEvent field maps with the retained
Q5 generated types: all three exactly match. No old bag was reopened for this
check. The D3 owner separately validates event/admission/snapshot and guidance
joins with explicit selected metadata; see its lifecycle validation receipt.

## Retained execution

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_runtime_v1/`.
`result.json` SHA256:
`55f4dcdd77972dbb9b1cf43fe91b608b7206b4b613be93af890eaa347c1edca5`.

Each invocation ran from repository root via
`env -u PYTHONPATH PYTHONDONTWRITEBYTECODE=1 bash <external-root>/<job>/command.sh`,
with stdout/stderr retained as `<job>/pytest.log` (build: `build.log`). Exact
commands, JUnit receipts and artifact hashes are retained under each job.

| Job | Finite command | Result |
| --- | --- | --- |
| `build_interfaces_v1` | `timeout --signal=TERM --kill-after=5 240 colcon ... build --base-paths ros2_ws/src/ros_esc_interfaces ... --symlink-install` | Exit 0; one package; 27.9 s total |
| `focused_v1` | `timeout --signal=TERM --kill-after=5 180 python3 -m pytest -q .../test_centered_verification_runtime.py --junitxml=...` | Exit 0; 41 pass; 4.059 s |
| `focused_v2` | Same explicit finite owner after constructor/DESIGN/freshness cases | Exit 0; 47 pass; 4.327 s |
| `focused_v3` | Same owner after future-admission guard/case | Exit 0; 48 pass; 4.650 s; 12 scoped pins unchanged before/after |
| `regression_v1` | `timeout --signal=TERM --kill-after=5 240 python3 -m pytest -q` on the six files below | Exit 0; 214 pass; 118.723 s |

The repeated focused versions are overlapping development checks, not additive
independent evidence. The regression list is `test_v2_controller_motion.py`,
`test_v2_supervisor.py`, `test_v2_moving_evidence.py`,
`test_m4_v5_moving_escape.py`, `test_m4_v5_typed_fill_authority.py` and
`test_m4_v6_controller_selection.py`. Its interpreter imported source before
the final selected-only future-admission guard; the final focused invocation
then verified that guard. Legacy branches were unchanged between them. No
failure, skip or timeout occurred, and all sessions are terminal/reaped.

The isolated overlay deliberately builds only changed interfaces; existing
source-symlink overlays provide current Python/launch owners. The verified
environment is `<external-root>/environment.sh`, sourcing ROS Humble, retained
Q2/Q5 source overlays and the new interface overlay in that order. Runtime
imports resolve supervisor/controller to this checkout, both new generated
messages to `build_interfaces_v1/build/.../rosidl_generator_py/`, and installed
Gazebo launch to this checkout. The current context validator and scoped diff
whitespace check pass. Parent owns final source checkpoint/status/handoff.

## Remaining empirical boundary

This is a selectable implementation with source-level evidence. Real raw-profile
repeatability, correct fill/ranking, escape, continued seeking and direction
performance remain for the prospective visible development case. Exact state
and guidance may arrive in either order; a missing companion briefly commands
zero until it arrives, so integrated analysis must measure any sustained stop
or guidance gap. The inherited command-sweep owner checks its current-heading
persistence projection; this milestone does not claim a new curved-trajectory
collision proof. No comparison or stationary recurrent arm is released here.
