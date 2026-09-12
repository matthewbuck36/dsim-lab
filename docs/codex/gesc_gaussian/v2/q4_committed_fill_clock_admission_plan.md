# Q4 committed-fill clock admission

Status: CLOSED SOURCE VALIDATION PASS under the approved simulation-only V2
goal. See q4_committed_fill_clock_admission_handoff.md and its validation record. No numerical/scientific study or hardware action.
Read AGENTS.md, plan.md, status.md and the Q3 handoff before editing.

## Demonstrated source issue and required behavior

AtomicFillActivation.accept currently treats committed_at ahead of the local
ROS clock as an invalid envelope and discards the result. Gaussian runtime
commits and caches the authoritative result before publishing; redelivery needs
a repeated command, and the supervisor has no periodic automatic retry. The
supervisor can therefore accept the commit while unable to obtain the
composer/direction registry acknowledgments without another delivered result. Reproduce this ordering in bounded
actual-owner tests before editing; preserve the source and failing receipts.

Correct the existing AtomicFillActivation and V2ObjectiveComposer owners only
where needed. A valid next-generation committed result with a bounded clock
lead must remain detached and pending until the clock covers committed_at.
Preserve the existing500ms maximum near-future admission allowance used by the
composer; excessively future messages remain invalid. This allowance limits
the initial lead, not the lifetime of an accepted durable commit. Pending
coverage or delivery after500ms and after expires_at must not expire a commit
whose original prepared_at <= committed_at <= expires_at was valid.

Validate original run, frame, origin, contract, hash, preparation/candidate and
registry generation/digests before accepting pending authority. A single valid
next generation is sufficient for the existing serialized supervisor protocol;
do not add out-of-order registry reconstruction. Existing MAX_COMMANDS bounds
the commit ledger. Preserve original committed_at and first receipt, stable
commit_identity across ACTIVATED/ALREADY_ACTIVATED retries, conflict rejection
and once-only application. A duplicate must not overwrite pending authority.

Poll pending activation from the existing composer poll before state/sensor
freshness gates and before objective composition. Never apply early or report
the new digest before application. Revalidate and rebuild the existing staged
swap from current state at admission: retaining a precomputed affine dictionary
would incorrectly erase intervening unrelated affine updates. Preserve active
fills during waiting and atomic registry/terms/cluster/affine swap behavior.

Committed results are durable, unlike sensor samples or readiness leases.
An origin fault fences pending use. A same-origin clock rollback retains the
ledger and pending commit, waits for coverage, and suppresses composition while
now precedes an already applied commit; do not let a future fill affect an
output stamped in its past. No global clock default, publisher retry protocol,
new topic/IDL/node, source-sample lease, controller policy or fill mathematics.

## Focused validation and closure

Freeze a recoverable source checkpoint before edits. Baseline actual-owner
cases: a100ms-leading valid committed result is not an envelope fault, and the
one delivered result applies once after clock coverage without redelivery.
Then cover no early registry/objective acknowledgment, durable delayed coverage
and delivery after the preparation deadline, duplicate/retry identity,
conflicting generation/digest, ordering/capacity, supersession with intervening
affine updates, wrong origin/run/frame/hash, rollback and resumed coverage.
Preserve malformed-envelope and commit-after-deadline rejection.

Use existing transaction fixtures and existing composer/supervisor transport
owners. Run bounded focused fill transaction and objective-source regressions,
then a bounded actual ROS transport case for deferred application and matching
acknowledgment. Reuse installed symlink resources after verifying bindings;
build only if a changed installed resource requires it. No Gazebo, old matrix,
field evaluator or scientific parameter rerun.

Record exact commands, failures, source/test hashes and retained log paths in
validation/q4_committed_fill_clock_admission.md and live status; inspect diff,
run context/checkpoint and write a source handoff at closure. No commit/push is
implied. Arm B remains the following source prerequisite, with its proposal in
validation/arm_b_adapter_design_note.md. Settling/direction development and the
unchanged16-run pilot remain pending; source correctness is not qualification.
