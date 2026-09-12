# M4 v2 recovery: owned descendants and fresh comparison

Status: ADOPTED FOR IMPLEMENTATION, 2026-09-10 UTC, under the user's resumed
full V2 goal and explicit instruction to make recommended changes without
further questions. This authorizes the bounded correction and a fresh 16-slot
simulation comparison after its source/preparation gates. It does not reopen,
replace or import any input from the closed M4 v1 attempt.

## Objective and preserved evidence

Both research goals and original acceptance targets remain as defined in
`plan.md`, with Q7's selected two-block detector and Q2/M3 moving-search work.
Q7 source is already validated. No algorithm retuning is justified by M4 v1:
its sole baseline run reached the goal but failed outer ownership proof.

The previous goal turn made progress by retaining that failed attempt, writing
its all-slot report/handoff and archiving source/evidence. Current verification
finds all 606 frozen source pins unchanged; no dispatcher remains active.
M4 v1 is CLOSED_INCOMPLETE, with one attempted baseline and fifteen unstarted
slots. Its archive is `checkpoints/m4_pilot_closed_incomplete_v1/manifest.json`
under `/home/mattb/Experiments/GESC-Gaussian/v2/`, SHA256
`31e01fcf9bfe5c341391a93f896ffc0ff4f33bc8371f3deecef25c5430409e4d`.
Preserve its contract, report, bag, all receipts and earlier closed studies.

## Selected correction and proof

The current strict procfs tree observer can lose a child-list observation when
an intermediate process disappears. This is incomplete proof, not a reason to
waive cleanup. Tree polling alone cannot recover the missed ancestry.

Add an explicit optional Linux child-subreaper ownership mode inside the
existing `scenario_runner/run_scenario.py` process owner. Preserve the old
observed-tree mode, strict failures and all default call behavior. Select the
new mode only for fresh M4 v2, in both outer plain-child and inner existing
specialized recorder routes; do not add another runner/node or launch graph.

Establish and verify subreaper state before launching the owned child. Require
an exclusive child/reaping scope, including explicit SIGCHLD and unsupported-
platform checks; reject incompatible preexisting child/reaper ownership before
launch. Keep the owner alive through all descendants. Synchronous auxiliary
children must finish through their existing Popen owners before any global
reaping; never steal the recorder/direct child's status from Popen.

After the main child is reaped, drain adopted descendants and require the
kernel's no-children result (ECHILD), rather than inferring exhaustion from an
empty procfs snapshot. A nested session does not release a descendant from
this ancestry witness. Retain bounded identities, adoption/reaping outcomes,
enumeration races and failure context. Missing/permission/parse errors,
capacity loss, unexpected reaper interference or an exhausted deadline cannot
become a pass. The new witness may discharge a transient tree-enumeration race
only when its complete kernel/ownership proof passes; the old path stays strict.

Use existing identity-validated scoped signaling and the same absolute end
for graceful shutdown and escalation. Newly adopted descendants must remain
eligible for bounded cleanup; never signal by name or a reused bare PID.
Keep the ROS graph/final-zero/recording checks and report skipped inspection
as unknown explicitly. Do not claim ECHILD proves unrelated graph absence.
Preserve subreaper state safely on incomplete cleanup and report that failure;
do not silently release a still-live owned tree.

Primary Linux semantics and their assumptions must be linked in the validation
record, with actual host checks and real finite process fixtures. Host read-only
inspection finds PR_GET_CHILD_SUBREAPER available (currently disabled); no
privilege escalation is required. User cgroup delegation is available as a
larger alternative, but no systemd unit/cgroup mutation is selected here.

## Fresh version and unchanged comparison

Extend existing workflow/scenario/analysis owners with explicit validated
experiment-version selection, retaining default v1 behavior. Fresh root:
`/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v2/`, version
`m4-pilot-v2`, unique run identities and versioned scenario metadata. Bind the
new ownership mode and this plan in its frozen contract. Every selected
consumer, including the runner's B/D centroid event adapter, must recognize
the exact fresh version. Distinguish experiment identity from unchanged
scientific method/schema identity. Reject cross-version/path/run substitutions.

Keep the same 16 matched A/B/C/D slots, geometry, seeds 26090801–26090804,
nominal/noise/delay conditions, controls, Q7 W6s/epsilon0.18m/radius0.50m,
Q2 mean weight0.75 and existing M3 information/comparability/12s safeguards.
Retain independent first-opportunity residence labels, publication-end latency,
all 192 direction targets, augmented-objective references and denominator rules
from `m4_execution_evaluation_plan.md` and `validation/m4_prerequisite_audit.md`.

This fresh comparison is additional to the retained single v1 acquisition;
none of that input is reused as a v2 slot. User's resumed authorization permits
this necessary versioned continuation, superseding the prior pending-release
note while preserving the no-replacement rule within each fixed experiment.

One exclusive preparation attempt gets 600s. Each new case retains 720s maximum
recording and 900s inclusive execution; suite 15300s inclusive. Existing 900s
science allocation and all cancellation reserves stay held. The first four
cases are visible development runs. Freeze once before twelve holdouts, with
no post-freeze tuning or replacements. Integrity failure stops that version;
complete behavioral/scientific failures remain reportable outcomes. Any later
correction requires another evidence-backed amendment, not an automatic retry.

## Validation and release sequence

1. Preserve v1 archive and record the new amendment before source edits.
2. Deterministically reproduce the old disappearing-child failure. Validate
   the new witness with real finite processes: fast intermediary exit, nested
   setsid/double fork, survivors ignoring graceful signals, normal completion,
   interruption, deadline exhaustion, unrelated sibling sentinel, unsupported
   reaper state, inspection failure and PID reuse. Test both actual runner paths
   and retain the failing baseline. Each process/test command has a timeout;
   fixture children have finite lifetimes plus scoped cleanup.
3. Validate fresh version/root/IDs and every selector/admission consumer,
   strict inner/outer receipts, all-slot aggregation and inherited regressions.
   Reuse existing source checks in their correct installation environments;
   do not rerun geometry/bags or rebuild merely to recover context.
4. Save exact validation/source hashes, review diff, run the V2 context and
   checkpoint tools, and archive one independently reviewable source boundary.
5. Prepare once, audit the frozen contract and exact installed commands, save
   release, then dispatch the fresh comparison under its original finite caps.
   Report all slots, failures, primary/supplemental denominators and limitations;
   update acceptance ledger/status/handoff and retain a material final archive.

No commit or push is newly authorized. Remain on the requested V2 branch and
preserve unrelated edits. No physical source, Pi, hardware, V1, global clock,
cost-sign/unit or controller-ownership change belongs to this work.
