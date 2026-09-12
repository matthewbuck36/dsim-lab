# Q1 recovery4 finite continuation — 2026-09-09 UTC

Status: SELECTED FOR SOURCE/PREFLIGHT; no acquisition release. Require completed
`q1_filter_expiry_recovery_plan.md`, focused/actual-transport validation, exact
source/equivalence freeze and checkpoint before dispatch. Original science
remains `q1-primary-shadow-v1` in `q1_plan.md`. No pilot release is implied.

## Preserve two accepted inputs and the failed acquisition

Recovery3 is CLOSED INCOMPLETE with two accepted discovery inputs, one third-case
pre-readiness failure and an undispatched fourth case. Its immutable closure
binds41 files at `qualification/q1_primary_shadow_v1_recovery3/acquisition_closed.json`,
SHA256 `79de12268086546592cba04beb937fd428dec1ee7542beb37a81255c9f51327e`.
Never overwrite old bags, metadata, reports, IDs or acquisition classification.

Import exactly the already accepted `input_26090911.json` and
`input_26090912.json` rows byte-for-byte, retaining their recovery3 run IDs,
directories, original PASS completeness/classification, input receipts and
spawn checks. These are accepted inputs, not reclassified failures. Exclude
the failed third run. No generic resume, arbitrary import or replacement loop.

An integrity-only audit finds no `pending_expired` or `pending_receipt_expired`
in either accepted discovery bag, before/during/after readiness. Diagnostic
sequences are contiguous and reset sequences do not skip or regress; during
readiness the6171/6174 diagnostic records retain reset_sequence2 throughout.
The new expiry recovery branch was therefore not exercised on their recorded
accepted path. Audit: recovery3 `diagnostics/discovery_expiry_audit_v1/result.json`,
SHA256 `1f01e293c3a97b44bf789356b8c1f4117ec36184c5d73a2afaeb5a614fd14fc4`.
This audit does not use detector scores, trajectory/cost/vector values, spatial
labels, direction confidence or scientific confirmation performance.

Require source review/tests proving unchanged behavior for the valid non-expiry
path, original equations/gains/thresholds and unchanged launch/IDL/model/filter/
sensor configuration bindings. Hash the old contract as historical evidence;
do not run its old all-source freshness check against changed files and waive
the resulting mismatch. Bind a new explicit source-equivalence receipt with
the reviewed expiry-only runtime change plus workflow/test amendments. If the
old normal input rows fail the existing `_q1_verify_run` under the new contract,
stop; never rewrite their saved bindings to the new source hash.

## Exact continuation and bounded owner changes

Acquisition version: `q1-primary-shadow-v1-recovery4`. New root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1_recovery4/`.
The new contract's first two planned entries are exact copies of recovery3's
discovery entries. Only the final two get recovery4 IDs/root, preserving their
original confirmation seeds26090913/26090914, starts, scenario controls and
batch visibility. No new discovery acquisition is dispatched.

Extend the existing acquisition layout/freezer/runner wrapper only. The exact
import block binds prior contract, acquisition, closure, both accepted input
files, integrity audit and source-equivalence receipt. Before any output or
dispatch: verify every receipt, exact accepted-ledger equality, original PASS
recording/safety/cleanup/spawn and125s duration, untouched scientific boundary,
and the normal analytical input validation. Permit old IDs/root only in those
two declared discovery slots. Reject another imported seed, extra input, wrong
root/ID, changed or failed report, unverified source change or opened outcome.

Seed the new acquisition with those two unchanged normal input rows. Dispatch
only the two new confirmation cases through the existing `execute_suite` owner.
Report imported_inputs2 and newly_dispatched0–2 explicitly; on failure preserve
that finite version and stop. A complete manifest has four normal input rows
plus explicit import provenance. Keep analytical input schema and all existing
label/nomination/confirmation/reference owners unchanged.

Each new case still requires125 simulated seconds after readiness and240s
process ceiling. Two-case continuation has a600s outer cap:540s interrupt plus
60s kill allowance. Reserve one240s case and60s cleanup before each dispatch;
do not restart the deadline on failure. No failed case is automatically retried.
The earlier visible first discovery run remains the first study case.

Only a complete four-input manifest unlocks the unchanged one600s label/
nomination job, conditional confirmation opening and one300s48-slot reference
job. Original finite grid, targets, missing-data outcomes and independent
scientific gates remain fixed. Startup failure exposed no scientific
confirmation result; no tuning or selection is based on that failed run.

## Validation and release

Test exact2import/2dispatch routing, provenance tampering/failure rejection,
unchanged prior roots/versions, timeout reserve and no output before invalid
input rejection. Use existing dry-run/scenario fixtures; do not launch Gazebo
for routing tests. Record commands/hashes, direct source/science equivalence,
checkpoint and exact dispatch receipt before running the continuation.
