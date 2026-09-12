# M4A execution deadline validation

Status: CLOSED_SOURCE_VALIDATION_PASS. Authority: ../m4a_execution_deadline_plan.md.
Independent execution prerequisite for the approved pilot; this is not an answer
to the Q6 method question, a pilot dispatch, or scientific qualification.

## Final result

The existing plain run_record_process accepts optional absolute_deadline in
monotonic seconds. It reserves configured grace plus three escalation intervals
inside that end, accounts for elapsed launch time, and passes the same end through
work, cancellation and exception cleanup. No positive blocking wait starts after
expiry. Selected audit records work/cancellation timing and known owned identities;
normal completion does not itself establish descendant cleanup. Selected private
cancellation returns a dictionary with stdout and audit; the default still returns
its historical stdout and default run result fields remain unchanged.

Optional strict procfs inspection now distinguishes missing processes from
unreadable/malformed evidence. Incomplete enumeration retains known identities
without replacing their original start ticks, permits only identity-checked
signals, and cannot claim complete cleanup. Audit truncation and expired deadlines
also prevent that claim. All specialized routes and execute_suite are unchanged.

## Exact evidence

Retained root:
/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4a_execution_deadline_v1/.

Final independent receipt: independent_receipt_v3.json, SHA256
4045565cbe79d7b5672f5d239771ea106c3e2289d2abe08d4d60c6a399558db6.
It contains exact shell commands, environment, original/final snapshots, import
binding and log hashes. Final result: 47 PASS (30 independent plus17 inherited),
178 deselected, exit0, 2.67s under60s. final_v3.log SHA256
75cd79d008c0839dfc955df407884d90f3c9a87fd97fe2db3400e35bf9ad76fd.

Final runtime source SHA256:
9c57f7992cbbf3829f7cd70ac94944a1147c3c6eba23fa271ffeae13f9131b83.
New test_m4a_execution_deadline.py SHA256:
88a2529c5afe15d2a4ee908e78779f2f66ca3dd77d581c6d77feded2e8279313.
Original runtime source SHA256:
c7fcc5ac21b83ebecadc4d62a0f74eea9d9401bc6b5b5c245d8f81e4c71710c3.

The final test command, from the repository root after the Humble/Q2/Q5 setup
documented in fresh_chat_handoff.md, was:

```bash
timeout 60s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_m4a_execution_deadline.py ros2_ws/src/ros_esc/test/test_scenario_runner.py -k "test_m4a_execution_deadline or boundary_setup_failure or live_boundary_stop or live_global_stop or normal_record_process or v8_live_stop or schema_v7_live_post_stage_a or schema_v7_live_stage_a or boundary_stop_cleans_nested or record_interrupt_cleans_nested or record_timeout_cleans_nested or boundary_base_exception"
```

Coverage includes decreasing work/grace/escalation budgets, original-end exception
retry, expired nonwaiting cleanup, permission/parse/vanished-process cases,
post-snapshot unreadable live identity, partial snapshot/PID reuse, unchanged
legacy signatures/results/exceptions, actual child exit1, and one finite actual
nested setsid child with an unrelated live sentinel. Installed import binding
PASS under20s; the fixture forbids ROS initialization. No source rebuild is
needed for the verified live-source binding.

Root independent AST review under30s: root_scope_review_v1.json PASS. Exactly
nine existing functions changed (six procfs-chain helpers plus wait/cancel/run),
one deadline helper added, none removed. Every other function/class, including
both specialized routes and execute_suite, is AST-identical to the original.
Source review, compile, context validator and staged/unstaged diff checks PASS.

## Preserved intermediate evidence and limits

First source334131f1 passed21 new checks in2.50s plus17 inherited in0.73s, but
review then found swallowed procfs errors could overstate completeness. Its
source/test/commands remain in independent_receipt_v1.json; it is superseded.
Corrected source d734a5d4 crossed a final one-line PID-reuse correction while its
46-case run was in flight. That passing run is retained as intermediate evidence
in intermediate_v2_boundary.json and is not treated as final hash-bound evidence.
The definitive47-case run above pinned stable final bytes before and after.

This is bounded source/process evidence. OS scheduling and procfs operation time
are not hard real-time guarantees; exact wait allocation is separately exercised
with a controlled clock. Known-identity cleanup is not proof about unobserved
future descendants. The future wrapper must still verify inner recorder cleanup,
child summary, safety/completeness, source binding and reserved case/suite limits.
No dispatcher, full-exposure contract or scientific gate is implemented here.
No ROS graph, Gazebo, bag/model/label/reference job, physical action or M4 pilot
ran for this milestone. Those are outside this source scope, not missing tests
required for this source closeout. Two-block choice/implementation and full M4
remain pending. Material checkpoint and transfer archive receipts are in status.md.
