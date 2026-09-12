# Q1 simulation source correction — 2026-09-09 UTC

Status: SOURCE/VALIDATION COMPLETE; material checkpoint receipt in `status.md`
closes this source boundary. Both prior Q1 acquisition attempts remain CLOSED
INCOMPLETE; this plan does not release a replacement acquisition or the M4 pilot.
Approved scope remains simulation-only V2 implementation. Exact validation and
handoff: `validation/q1_simulation_source_correction.md` and
`q1_simulation_source_handoff.md`.
Read `plan.md`, `status.md`, `q1_plan.md` and
`validation/q1_acquisition_recovery1_failure.md` before editing.

## Evidence and unchanged objective

Recovery1 completed125 simulated seconds and clean shutdown, but the controller
raised its first FAILSAFE at simulated2.7s after a2.721s odometry header arrived
between held2.7s and next2.8s clock ticks. Its V2 callback overwrote the current
pose immediately; the watchdog rejected a future source. The first recorded
event explicitly reports `V2 pose source missing, stale or future`. The
supervisor entered permanent FAILSAFE at2.8s, which explains the later centroid
diagnostic gap. Do not repair that gap by weakening completeness or admitting
outside-SEARCH data. This is not measured slow convergence.

Separately, two joint-state publishers each have ordered source streams but
their merged topic has six source reversals. The existing30Hz Gazebo plugin and
100Hz controller broadcaster publish the same rotating joint. The first merged
reversal9.011s ->9.008s propagates through strict source invalidation. It occurs
after the first FAILSAFE and is not its cause.

Correct these actual graph/clock integration defects. Preserve detector formulas,
filter equations/gains, costs/units, speed ceilings, stale limits, source
integrity rules, supervisor safety, final zero and all historical outcomes.
No physical source or hardware action is included.

## Controller clock admission

Extend the existing V2 controller owner to retain covered fresh data while
bounded near-future source samples wait for the local simulation clock to cover
their original timestamps. Apply the same requirement to selected stamped pose,
filter input and supervisor state, because each can arrive before a local clock
callback. Reuse established source-admission conventions; add no control node.

Do not command from queued future data or re-stamp it. Keep original receipt
times so queue residence cannot refresh stale input. Preserve strict source and
receipt age, run identity, state/weight validity, source ordering, clock rollback,
origin changes and immediate zero on explicit stop/readiness/safety loss. Bound
queue size and future allowance by the existing500ms freshness ceiling; genuine
excessive future/stale/invalid data must still fail. Rollback or origin change
clears active and pending authorization. No larger watchdog threshold or arbitrary
startup grace is authorized. Legacy/default controller behavior is unchanged.

Cover ordinary30Hz pose headers ahead of10Hz clock ticks, pending state/filter
ordering, unchanged receipts, duplicate/regressed samples, bounded overflow,
stale clocks and reset/stop/final-zero behavior. Test actual controller ROS
transport under the recorded held-clock pattern, with no Gazebo required for
this source milestone. Preserve current moving VERIFY/DESIGN authorization and
escape command ownership.

## Single selected simulation joint source

Pass the existing `continuous_search_mode` through the selected Gazebo include
to `control.launch.py`. For `rolling_gesc_v2`, start the velocity controller while
omitting the redundant joint-state broadcaster in both ordinary and idempotent
spawner paths. The Gazebo plugin remains the sole `/joint_states` publisher;
sensor geometry, plugin rate and canonical topic remain unchanged. The separate
velocity controller uses hardware state interfaces and does not depend on that
broadcaster. Preserve both controllers/publishers in default `stationary_v1`.

Adapt the existing recorder's selected-mode readiness and resolved publisher
contract to match this graph. V2 requires active velocity control and exactly
`/turtlebot3_joint_state` on `/joint_states`, with single-source timestamp ordering.
Default/legacy and physical contracts remain unchanged. Validate manifest and
mode selection before deriving these requirements; never silently accept a
missing required controller or an unexpected second publisher. Keep the old
multi-publisher recorded-bag interpretation for historical runs.

Test actual launch action selection for both modes and both spawner paths;
recording readiness, captured exact publisher contract and wrong-publisher
rejection; focused old-manifest/old-bag/legacy launch compatibility checks.

## Completion and next acquisition

Run focused regressions and necessary build/installed-asset checks, record exact
results and retained failures, inspect diff, and checkpoint the source boundary.
Document each root cause separately and preserve the fixed recovery1 bag/hash.
Then freeze a separately declared acquisition version before Gazebo. No edits
during a fixed run, no repeated old IDs, no replacement or rescoring of its
failed outcome. Scientific geometry/labels/finite-grid/direction targets remain
unchanged; any later seed reuse must be justified as technical recovery and must
not claim independence from the exposed discovery attempt. Confirmation remains
unopened and cannot guide any correction.
