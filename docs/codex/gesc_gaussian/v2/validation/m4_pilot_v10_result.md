# M4v10 closed incomplete and retained C diagnosis

2026-09-10: CLOSED_INCOMPLETE. Dispatcher session66016 terminal/reaped exit1,
1268.120640s; outer wrapper1271.949431s. Source frozen at755 exact pins throughout.
The16-slot report is retained at external `pilot/m4_pilot_v10/report/report.md`.

| Slot | Acquisition | Behavior | Inclusive wall | Arrival |
| --- | --- | --- | ---: | --- |
| 1 A | COMPLETE | PASS, all12 predicates |417.122410s |0.498021974m; final0.491901755m |
| 2 B | COMPLETE | PASS, all12 predicates |357.904877s |0.497651743m; final0.486047402m |
| 3 C | INCOMPLETE at safety gate | FAILSAFE |490.693147s |No valid local recovery/arrival |
| 4–16 | UNSTARTED | Not evaluated |— |— |

A/B each committed one local fill, completed REPULSE/ASSIST/SEARCH and reached
the evaluator-only0.5m global region. Both finished SEARCH, without ranked goal
or GOAL_HOLD. C's recording/completeness/final zero and inner/outer process
cleanup passed; its actual forbidden safety events caused the dispatch failure.
The additional dispatcher inner-cleanup inspection was not reached for C.
No four-case science block or confirmation release ran; all13 later slots stay
unstarted and none will be replaced. No comparative latency/direction result is
inferred from this interrupted pilot.

Independent closure audit PASS4.579931s, session32116 terminal/reaped: all16
receipts/report agree,755 source pins unchanged,138 recorded process identities
absent, five owner PIDs absent and12 owned sessions empty. Receipt external
`development/20260910/m4_v10_source_v1/closure_audit_v1.json`, SHA256
`22b6cbf49d2007611af9d7cb689b1c561d9f0ed97eeec844af1c3fe28ff5a008`.

## C failure mechanism

The [prospective diagnostic](../m4_v10_c_failure_diagnosis_plan.md) selected only
existing reader aliases for lifecycle/state/command evidence. Initial export
failed after its1.817492s read (5.134974s total) because an optional invalid
source timestamp remained nonfinite outside the already-normalized message.
Original helper, partial output and failed receipt remain. A new helper v2
normalized that optional value using existing `message_payload`, preserving its
false validity flag. Its single selected read took1.807089s; total6.753600s,
all source/input hashes stable, under25s work/30s external cap. Both helper
sessions91495/40985 are terminal/reaped. No production source changed.

Exports at external `development/20260910/m4_v10_source_v1/c_failure_export_v2/`
retain18 events,7228 states,7228 epochs, one confirmation, one snapshot,
7227 guidance messages, three fill commands, three fill results, one Gaussian
fill, one stop request and3748 readiness messages. Use these exports for
follow-up; no repeat bag read is needed. Receipt SHA256
`3e64ef344d0c587ae71df127d0300798e0426dea650c049406105e69a55c14a3`.

Actual sequence (ROS simulation time): PDE confirmation70.2s; VERIFY70.3;
collection76.5; three-cycle snapshot/DESIGN85.5; PREPARE85.5 (expiry90.5);
ACTIVATE command85.8; ACTIVATED and FILL_CREATED85.9. At86.0, guidance1721 was
invalid with reason `centered_command_sweep_unsafe`, with DESIGN and one active
fill. CANCEL command3 cites the same reason. The controller emitted
`centered guidance identity, validity, bounds or deadline invalid`; the supervisor
returned SEARCH citing the cancellation, then entered FAILSAFE86.1 on the
controller fault. The cancellation result retains the already committed fill.
Later95.4/95.5 stale-filter watchdog messages are downstream, not the first cause.

Current source installs the authenticated committed fill in active fill records
before the objective/direction acknowledgement handoff. Centered DESIGN guidance
then checks its ongoing command against all active fills, including its own new
fill. That newly introduced avoidance can reject a command that was valid before
commit, cancel the transaction after irreversible activation and prevent escape.
The recorded reason confirms this handoff defect; successful typed lifecycle
validation alone did not establish executable escape behavior.

The safety gate remains correct and this experiment remains failed. Next is a
separately recorded bounded handoff correction and focused source validation,
then a short visible C development case and usable analysis. No unchanged matrix
retry, new qualification release, physical action, V1 change, commit or push.
