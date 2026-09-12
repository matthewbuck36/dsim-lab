# M4A source handoff

Status: CLOSED_SOURCE_VALIDATION_PASS. The existing plain process owner now has
an optional inclusive monotonic deadline with grace/escalation reserved inside
it and the same original end used during exception cleanup. Legacy defaults and
specialized scenario routes remain unchanged. Selected strict procfs inspection
and PID-start-time checks keep incomplete inspection, survivors, expiry and audit
truncation from being reported as successful cleanup.

Final source: run_scenario.py SHA256
9c57f7992cbbf3829f7cd70ac94944a1147c3c6eba23fa271ffeae13f9131b83.
Independent final checks: 47 PASS (30 new,17 inherited),178 deselected,2.67s;
installed binding, root scoped AST review, compile/context/diff PASS.
[Validation](validation/m4a_execution_deadline.md) records exact commands, prior
versions, final hashes and limitations. All intermediate results are retained.

This source capability does not release M4 or prove its full900s case contract.
The future wrapper must put the existing one-case run_scenario CLI inside this
plain child envelope, reserve additional cleanup before the case/suite end,
validate inner recorder/session receipts, and implement the frozen scientific
and safety/completeness continuation contract. Normal process completion does
not prove descendants are gone; child exit1 may be a safe behavioral failure.

No ROS/Gazebo/science/hardware ran. Q5 algorithm sources and Q6 proposal are
unchanged. Branch feature/gesc-gaussian-robustness-v2, HEAD3369cfc; task work is
uncommitted. No commit or push was made. Full V2 remains IN_PROGRESS.

The user requested a fresh-chat boundary before two-block work. Start with
[fresh_chat_handoff.md](fresh_chat_handoff.md), verify live state, then document
the method amendment after the user's explicit selection. No additional
milestone or experiment is running from this chat. Current status records the
material source archive/checkpoint; the two-block runtime is not implemented.
