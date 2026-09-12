# Detector clock admission before fresh V2 qualification

Status: CLOSED SOURCE VALIDATION PASS under the approved V2 goal.
See q3_detector_clock_admission_handoff.md and validation/q3_detector_clock_admission.md.
Read AGENTS.md, plan.md, status.md and the completed Q2 diagnostic reports.
This milestone changes clock admission only, not the centroid formula, windows,
thresholds, independent labels, GESC policy, moving evidence or qualification.
All Q2 science and diagnostics remain closed, with confirmation sealed.

## Evidence and source issue

Recorded residence diagnostics contain `stale_or_future_algorithm_state` notices
at56.8/85.6s and three subsequent `outside_search` notices. They do not prove
which incoming state caused a reset or whether it was stale or future. All20
valid complete histories across both runs separately fail the numerical score.

Current source immediately invalidates centroid history when an AlgorithmState
publication leads this subscriber's held simulation clock by any amount. The
stationary centroid pose route has the same issue; rolling pose admission already
uses bounded source-clock coverage. A synthetic real-owner case can demonstrate
the fragility without claiming it caused the recorded notices. The existing
controller clock-admission owner provides the intended original-receipt pattern.

## Required behavior and ownership

Correct the existing centroid detector adapter. Keep legacy pde_mean_v1 paths
unchanged and rolling pose admission under its existing V2 binding. Reuse the
existing bounded admission helper where its semantics fit; do not duplicate
controller computation or create a node/global clock-default change. A small
detector-specific subordinate adapter is acceptable only for needed identity
and reset ownership, with the shared receive/coverage semantics reused.

For AlgorithmState in centroid mode and selected pose in stationary centroid
mode, retain a bounded near-future message until this node's ROS clock covers its
original source/publication stamp. Never admit early. Preserve the previously
admitted valid state/pose while a future replacement waits, subject to its
unchanged freshness and recording authorization. Do not feed a second pose queue
into the rolling V2 binding.

Use original ROS and steady-clock receipt times; draining a queue must not
refresh either. Preserve existing0.5s source/receipt freshness limits, finite
pending capacity, source order and exact duplicate behavior. Identical repeated
messages cannot keep paused/stale evidence fresh. Distinct valid same-clock
state publications retain singleton publisher order; conflicting same-source
poses fail. Excessively future, stale, nonfinite/invalid, regressed, wrong-frame
or wrong-run inputs must still reject or invalidate as appropriate.
The selected study limits remain0.5s. Preserve the existing positive stale_sec
parameter overrides as declared; do not silently clamp a reported configuration
to a different hardcoded effective limit. A stationary nonempty frame change
retains the existing reset/reseed behavior and confirmation latch, with pending
old-frame samples discarded at the appropriate admission boundary. Rolling
frame identity stays under its existing stricter stream binding.

Keep identity, SEARCH entry, confirmation latch and invalidation ownership
coherent. A deferred state cannot retroactively relabel history or rearm a
confirmed epoch. Preserve actual epoch-start source semantics, original
state_elapsed interpretation and run-change handling. Invalid state/recording
loss and real non-SEARCH transitions revoke authorization. Flush pending
messages on applicable identity/safety/clock-reset boundaries; a delayed old
message cannot resurrect revoked data. The existing watchdog must drain covered
messages before checking current support even if the search gate is presently
inactive, without bypassing startup readiness.

No broad extraction of additional Q2 topics or new Gazebo acquisition is needed.
The recorded resets remain an unresolved cause distinction; the claim is source
robustness to a demonstrated allowed callback ordering, not retroactive repair.

## Focused validation and completion

Freeze a source checkpoint before edits. Add meaningful actual-owner regressions
for a100ms leading SEARCH publication and stationary pose: no early use, no
unnecessary history reset while prior evidence remains fresh, original receipt
retained after clock coverage, and no duplicate refresh. Exercise paused-clock
steady expiry, stale/excessively future inputs, rollback, non-SEARCH transition,
recording revocation, run/epoch changes, conflict/reorder and finite capacity.
Ensure late draining cannot confirm outside SEARCH or after the original lease.

Keep the selected recorder contract consistent with original receipts as well.
The selected standalone centroid route has no rolling stream identity; attach
an explicit centroid admission marker and its existing parsed pose-freshness
limit to the resolved topic entry. The canonical validator may then accept a
receipt before source only after publication covers both within that limit.
Preserve strict unselected ordering, existing rolling behavior, and invalid
marker/limit rejection. Test real emitted confirmation and selected validation.

Run bounded existing centroid/node/binding/epoch/clock tests, then the relevant
actual DDS centroid transport and controller admission regression. Preserve all
old test results and report unavailable checks honestly. Build only affected
installed package resources when necessary; no numerical reference or fixed
calibration rerun. Broaden tests only for an observed changed-owner concern.

Record exact commands, outcomes, skips, source hashes and retained paths in
`validation/q3_detector_clock_admission.md`, live status and a source handoff.
Inspect diff, run context/checkpoint and archive at the validated boundary. No
new commit/push is implied by this milestone.

## Remaining work after this boundary

The Arm B centroid/stationary confirmation-to-fill adapter and separate composer
future-clock admission for already committed fills remain M4 source prerequisites.
Detector window/period sensitivity and an independent prospective settling oracle
need one finite development decision; held direction error targets remain open.
Do not silently tune them while correcting clock admission. Reuse completed
M0–M3/Q2 source work and preserve the original16-run pilot and its outcome ledger.
