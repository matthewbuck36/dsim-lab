# M4 v6 conditional moving raw-evidence reconstruction

Adopted prospectively 2026-09-10 UTC under the active V2 goal and the user's
existing authority for recommended bounded corrections. This authorizes the
plan and external helper/fixture implementation now. Execution remains HELD
until root review and explicit release of the concrete helper and commands.
It adds no source correction, acquisition, scientific evaluation or tuning.
M4v5 remains CLOSED_INCOMPLETE and immutable.

## Purpose and evidence boundary

The completed descriptive extraction under
`builds/m4_v6_development_diagnostic_v1/` retained four C and seven D
confirmations entering VERIFY, with no candidate snapshots. A deadline does not
identify the preceding unpublished M3 readiness reason. Diagnose which unchanged
moving raw-evidence predicates block under ONE declared conditional delivery
schedule. This is neither exact callback replay nor an upper/lower bound on
runtime readiness; different delivery can change admissions, resets and cycles.
Do not relabel the failed experiment, claim research success, widen the 12 s
verification interval, change the fixed center, or optimize any parameter.

Inputs are the existing extracted gzip JSONL payloads and small closed
metadata/configuration receipts only. No SQLite/bag read, reindex, model/field/
topology evaluation, primary endpoint, reference job or physical action.
All 623 v5 source pins from `builds/m4_v5_moving_fill_v1/root_final_v1_receipt.json`
(SHA256 `4d68036db37e934c43d1dedbcedc3dcc37e40ea927aa2037a82e1a66353ba210`)
must remain unchanged before/after/exit. The closure audit remains authoritative
for small original metadata bytes; do not hash or reopen the closed bag here.

## Frozen population and configuration

Before ANY readiness evaluation, restore and validate C and D confirmation,
epoch and AlgorithmState payloads and freeze all eleven windows into one
exclusive `candidate_windows_v1.json`. Require one matching valid SEARCH epoch
and referenced context for every confirmation, exact run/stream/origin/frame/
selected metric, one corresponding SEARCH-to-VERIFY transition and a last
VERIFY publication. Classify an observed later VERIFY-to-SEARCH transition as
`closed_return`. D's seventh window instead remains `right_censored`: bind its
endpoint to the recorded readiness exit or explicit terminal state stop,
whichever occurs first in recorder order. Preserve the incomplete D status;
never invent a return, discard this candidate, or extend beyond the stop.
Preserve each full
confirmation and exact input row indices/timestamps. Missing, ambiguous or extra
population members abort rather than select a convenient subset. Do not allocate
synthetic public candidate IDs or accepted-at fields.

Use each recorded confirmation center, epoch start and source stamp unchanged.
Bind `v2_stream_config_json`, selected mode, candidate radius/epsilon and MAD
scale to actual recorded `target_argv`. Resolve absent readiness-topic/staleness
and direction-topic launch arguments from the held actual gazebo launch defaults,
recording that source explicitly; verify their manifest topic matches. Preserve
the selected 0.75 m radius, 0.15 m epsilon, MAD scale 3, raw-owner capacities
20000/4000, three-cycle criterion, 12 sectors, 500 ms source/freshness limit,
30 s maximum cycle, and existing information comparison without substitution.

Acceptance is not recorded because there is no snapshot. Save the conditional
causal interval
`[confirmation publication, min(first VERIFY publication, source+500ms,
confirmation publication+500ms, referenced context publication+500ms)]`.
Require a nonempty interval; record its provenance and assumption of comparable
monotone publisher clocks. Deadline is this interval plus exactly 12 s. An
evaluation before its earliest endpoint is pre-deadline; one within its bounds
is deadline-ambiguous; at/after its latest endpoint is outside the admissible
deadline and cannot support a runtime-readiness inference.

## One deterministic conditional delivery schedule

Use **recorder order with publication catch-up**. Merge streams by original
bag timestamp, then the fixed alias order stored in the helper, then original
per-stream row index. Require nondecreasing bag timestamps within each stream;
never sort by source time, coalesce repeats, or repair publisher regressions.
The export lacks publisher GIDs; the resolved manifest's selected single-owner
topics and retained per-topic ordering are the available publisher-order witness.

The detached ROS clock begins at zero. At each delivered row it advances to
the maximum of its previous value, a recorded /clock value on a clock row,
and that row's explicit top-level publication `stamp`, where present. A pose
header is a source stamp and DOES NOT advance this clock. This catch-up is a
declared conditional assumption, not the recorder's or supervisor's real clock.
Record every catch-up and any publication regression. The detached steady clock
is `1 second + (bag timestamp - first merged bag timestamp)`; it preserves the
recorded spacing only, not unrecorded supervisor callback receipts or wall-clock
adjustments. Ties follow the fixed ordering and are counted explicitly.

Restore complete generated ROS messages with exact recursive field checking,
including nested messages, fixed arrays and the extractor's explicit
`__nonfinite_float__` tags. Unknown/missing fields or malformed tags fail.
Use no ROS initialization, node, subscription or publisher: a detached host
provides clock/parameter/transport stubs to the existing MovingSupervisor.
Call its unchanged `timekeeper`, `readiness`, `direction`, `provenance`,
`add_pose` and `drain_poses` methods. Temporarily supply the declared steady
clock only to that module in the external process. Transport stubs reject any
publication. Do not call `confirmation`, `inputs`, the state machine, snapshot
or preparation publication to fabricate accepted candidates or transactions.

Recorded AlgorithmState sets the detached machine state. Each new authoritative
SearchEpochContext applies its recorded epoch/start to the existing
`MovingRawEvidence.start_epoch`; repeated heartbeat contexts do not reset.
The constructor's provisional epoch is not recorded evidence: if the first
valid context has a different identity/start, explicitly initialize that recorded
identity. If it already matches, preserve start_epoch idempotence and all
pre-context records. Retain the comparison and any initialization/reset as an
audit row. A later same-epoch changed start remains an error. If the next
epoch context arrives before its SEARCH state row, close the prior conditional
window at its frozen recorder-order endpoint and do not evaluate that window
under the new epoch; record this cross-topic ordering ambiguity explicitly.
Preserve the first filter metadata across epochs as production does. A readiness
transition invokes the original reset behavior. Keep all pretrigger history
from that epoch, including SEARCH samples; do not reset at VERIFY entry.
Call the existing raw evaluator directly with the fixed recorded confirmation.
The detached owner has no synthetic active candidate, so record conditional
pose/readiness gates separately from raw-evidence readiness and do not claim
that a production cancellation was reconstructed.

## Evaluation schedule and retained guards

For every frozen window evaluate once at its first recorded VERIFY publication,
after each completed-cycle or reset change delivered while the recorded state
remains VERIFY in that window, and once at its final recorded VERIFY publication.
Coalesce schedule reasons only when they identify the exact same delivered row.
At most 256 evaluations per candidate; exceedance aborts without truncation.
Readiness changes alone without a raw reset are retained as admission/audit facts.
Keep per-stream 40000 and total 160000 input-row limits from extraction.

For each evaluation retain the original row identity, conditional ROS/steady
clock, acceptance/deadline relation, owner reset sequence/reason, observation
counts and fingerprints, owner-returned reason and readiness, readiness status,
pose age/distance margins, and complete raw-cycle source boundaries. Describe
the unchanged cycle predicates using sector counts/duration/qualification,
maximum vertex distance and radius margin, centroid distance and epsilon margin,
eligible-cycle count, latest-three chosen identity and sector-centroid mismatch
margin. For available profiles retain amplitude/disagreement/information floor,
`amplitude-max(3*disagreement,floor)`, baseline negativity and upper-cost-bound
margins, summary validity and support/capacity facts. Preserve nonfinite values
explicitly. These are guard diagnostics, not substitute primary metrics.
Save every candidate even if zero cycles/observations or no informative profile;
missing later guards remain unavailable rather than zero or guessed failure.

## External artifacts, bounds and release

Only new helper, fixtures, command wrappers and results belong under
`builds/m4_v6_raw_evidence_reconstruction_v1/`. This plan is the sole owned
repository edit. Root owns status, handoff, ledger and checkpoint updates.
Use exclusive file creation and an attempt marker for each job; preserve every
failure/partial result. No automatic retries or overwrite. Bind helper/fixture/
plan bytes in a reviewed release manifest before execution.

Prospective budget, amended before any execution following root's source review:
one 45 s fixture command, then one C and one D command each with 120 s work plus
10 s exit/hash allowance: 305 s inclusive total. C restores both runs' window
payloads before all C payloads and invokes generated-message round-trip checks
plus unchanged owner integration; this bounded offline allowance covers that
known work without another attempt or extra inputs. This is not a simulation
or scientific budget renewal. Freezing
all eleven windows is part of the C allowance and precedes its first evaluation;
D verifies and consumes the same immutable window file. C failure stops D.
Each wrapper records the exact clean Humble -> Q2 -> Q5 command, return code,
elapsed time, log hash and before/after source/input pins, including on failure.
Use finite subprocess deadlines; work stops at 120 s and process/hash cleanup
must finish within 130 s. No command executes until root releases it.

Fixtures must cover full generated-message/nonfinite round-trip, rejected
missing/extra fields and malformed tags, fixed population and acceptance bounds,
the seventh D right-censored window with an explicit recorded stop witness,
per-topic/tie schedule ordering, repeated epoch versus SEARCH reset, preserved
first metadata and duplicate/revocation admission through the actual owner,
unchanged neighborhood/sector/profile guards, zero-evidence candidates,
entry/reset/cycle/final evaluation retention and capacity/deadline labels.
Fixtures use synthetic messages only, no extracted evidence, ROS graph or bag.
