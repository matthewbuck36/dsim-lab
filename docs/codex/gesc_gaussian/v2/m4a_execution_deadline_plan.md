# M4A inclusive execution deadline

Status: CLOSED_SOURCE_VALIDATION_PASS under the already approved16-run M4 goal.
Result: m4a_execution_deadline_handoff.md and validation/m4a_execution_deadline.md.
This work is independent of the pending Q6 detector-method choice. Q6 analytic
comparison is complete; its alternative metric remains unselected. Q5 algorithm
sources stay held. No empirical dispatch, model/label job, scenario population
change or new scientific gate is released here.

## Source issue and selected architecture

The existing run_record_process timeout bounds working time, then separately
allows shutdown/escalation. Specialized routes additionally allow120s recorder
finalization and contain native executor teardown and synchronous bag analysis.
Thus the inherited900s wall_timeout alone cannot prove an inclusive900s case.

Add one opt-in absolute monotonic deadline to the existing plain process owner
and its existing scoped cancellation/wait helpers. The eventual M4 wrapper will
run the existing one-case run_scenario CLI as this child, so setup, specialized
callbacks, native teardown, bag extraction and summary writes are all inside
one supervised process envelope. Do not rewrite execute_suite or its specialized
stop paths. No parallel recorder/runner/node or unsafe Python-thread interruption.

With no deadline, preserve existing call signatures, result fields, timing and
exception behavior. With a deadline, reject invalid/nonfinite/expired inputs
before launch and reserve the configured graceful interval plus three existing
escalation intervals inside the deadline. The eventual case wrapper separately
reserves bounded cleanup inside case_end=min(case_start+900,suite_end), where
suite_end has the unchanged15300s ceiling. Recorder720s remains a maximum,
not permission to extend a case after late startup.

Pass the same absolute end through normal timeout and exception cleanup; never
renew grace in an exception handler. Recompute remaining time immediately before
every blocking wait. At exhaustion, perform only identity-validated nonwaiting
escalation/reaping attempts, retaining explicit incomplete/survivor evidence.
Preserve PID start-time/process-group/nested-session ownership checks. Do not
kill by process name or infer successful cleanup from an unavailable inspection.
The selected result records actual deadline/work/cleanup outcomes and bounded
owned-descendant evidence. Do not change existing result layouts for unselected
callers. The optional deadline is for the outer plain-child envelope; reject
combining it directly with the old specialized callback routes before launch.

## Scope and validation

Owner: ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py, restricted to
run_record_process, _cancel_scoped_process, _wait_for_cancelled_tree and a small
shared deadline validation/remaining-time helper if needed. Preserve the original
file in the external build receipt directory before editing. Tests live beside
existing scenario_runner tests; root owns documents/receipts, runtime owner and
independent test reviewer are separate agents.

Final-review amendment: the inherited procfs identity/children helpers swallow
read/parse errors into absent identities or empty child lists. The first tested
deadline implementation could therefore overstate inspection completeness.
Permit optional strict inspection in those existing helpers and their existing
snapshot/matching/live callers for the selected deadline route only. Preserve
legacy defaults and identity-checked signaling. Retain the first tested source
and its results, add adversarial inspection-failure checks, and validate the
corrected source before closeout. This is a bounded evidence-correctness fix,
not a new process supervisor or scientific release.

Meaningful focused evidence: optional deadline rejection before spawning;
remaining budgets decrease across work/grace/escalation; exception cleanup uses
the same original end; no blocking wait after expiry; legacy default paths and
exceptions remain intact. Run one finite real subprocess case with a nested
session and an unrelated sentinel to prove bounded scoped escalation/reaping.
No ROS graph/Gazebo/hardware is needed. Every command has an explicit timeout.
Then relevant existing scenario process/cancellation regressions, source diff
review, context validation and material checkpoint/handoff close this source
milestone. Do not broaden tests without a concrete change or unresolved failure.

## Remaining M4 work and evidence boundaries

This source capability alone does not release any run or prove the full case
contract. The later thin dispatcher must preserve exact16slot matching, source
and installed binding checks, one-time holdout freeze and exact child summaries.
A child scenario CLI exit1 may be a safe behavioral failure; only complete
recording/lifecycle/final-zero/cleanup plus frozen safety predicates authorize
continuation. Verify inner recorder session cleanup too; outer SID alone misses
nested sessions. Fixed simulation-duration expectations cannot be borrowed from
Q1: M4's eventual full-exposure/graceful-goal rules remain prospectively defined.

Methodology, independent label/reference definitions, scientific budgets and
full dispatcher admission stay pending in m4_plan.md. This bounded independent
execution capability replaces only that draft's read-only preparation status
for the named owner above; it does not authorize the pending detector change.
Record exact commands, outcomes/failures, source/test pins and limitations in
validation/m4a_execution_deadline.md and status.md before closeout.
