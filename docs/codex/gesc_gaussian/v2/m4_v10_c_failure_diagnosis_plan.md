# Retained M4v10 C safety failure diagnosis

ADOPTED prospectively2026-09-10 after the terminal V10 dispatcher. This bounded
development diagnostic preserves the failed experiment and its safety gate.
A/B reached the global region without GOAL_HOLD. C entered VERIFY and DESIGN,
published FILL_CREATED, returned SEARCH and entered FAILSAFE. Small retained
results do not contain the event payload explaining the first safety transition.

Use the existing `bag_reader.read_run_bag(..., aliases=...)` once on the complete
C recording, selecting algorithm events/state, epoch, detector confirmation,
candidate snapshot, verification guidance, fill command/result, Gaussian fills
and stop request (plus the owner's required readiness). Save typed message
payload JSONL and exact timestamps to a new external diagnosis directory.
No new decoder, ROS node, model, controller, label definition or production
source is introduced. Do not decode large PDE histories or run the full matrix
again. Preserve every selected record so follow-up inspection needs no new read.

Work cap25s plus5s final receipt allowance under30s external timeout (3s kill
grace only for forced termination). Hash contract, full C bag and small retained
results before/after; source pins must still match V10 and use its exact runtime
environment. Completeness and performed cleanup are prerequisites for read-only
admission; C behavioral acceptance is explicitly failed. Save partial output
and terminal/error status on failure. Success means an intact causal record,
not a repaired or scientifically accepted case.

Decision: identify the first actual FAILSAFE reason and preceding typed state,
fill/admission/expiry sequence. Distinguish a justified safety response, invalid
method behavior and an implementation/ownership fault. Only a separately saved
prospective correction may follow this diagnosis; no correction or new run is
authorized by the diagnosis result alone beyond the user's broader development
authorization and repository milestone process.
