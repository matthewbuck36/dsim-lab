# Q4 committed-fill clock-admission source handoff

Q4 source work is complete. Two existing owners now retain a valid committed
result while its original committed_at leads the receiving clock, then apply it
once before objective composition. Initial lead remains bounded500ms; accepted
durable commits have no sensor-style expiry. Original identity/receipt/stamp
and generation/digest checks remain intact. Staging is rebuilt at admission so
intervening unrelated affine updates are preserved. Rollback retains the ledger
and suppresses composition before an installed commit's time; origin faults
fence pending use. No fill algorithm, controller, supervisor, IDL or numerical
scientific owner changed.

Independent evidence: two preserved actual-owner baseline failures;157 focused
checks PASS6.28s; one new actual composer DDS PASS0.40s; three existing worker/
composer/supervisor pipeline DDS PASS21.33s. Installed imports bind to the held
source with no rebuild. Source hashes, exact commands, test snapshots, logs and
coverage limits are in validation/q4_committed_fill_clock_admission.md and its
external receipts. The new DDS case proves composer acknowledgment from one
supplied authoritative result; existing transport separately covers supervisor
handling. It does not claim a new scientific candidate/trajectory experiment.

Material checkpoint and archive receipt are recorded in live status. Q3 source
stays closedPASS. Q2 science/diagnostics remain closed, confirmation sealed and
scientific targets open. Next resolve Arm B's typed centroid/stationary adapter,
then make one finite development decision on settling/direction and execute the
unchanged16-run pilot with honest behavioral outcomes. No closed study is rerun
or retuned by this correction. The full approved goal remains active.

Branch remains feature/gesc-gaussian-robustness-v2 at HEAD3369cfc, with task-owned
dirty source/evidence. No new commit/push, V1 edit, physical snapshot/Pi access
or hardware action occurred.
