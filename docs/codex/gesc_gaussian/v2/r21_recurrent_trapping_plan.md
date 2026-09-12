# R21: recurrent trapping verification through the existing escape lifecycle

ADOPTED prospectively on2026-09-11 UTC after reviewed R20 closure and before R21
implementation or scientific extraction/replay. R20 was progress: it implemented
and measured a candidate, then rejected it honestly. The full goal remains open.

## Method and hypothesis

A confined closed-loop trajectory need not be an attracting zero of the stationary
GESC direction field. R20 found this mismatch at all four retained D centers.
Use an explicit opt-in `recurrent_trapping_v1` evidence policy to verify sustained
trapping during actual SEARCH, then use the existing raw-cost ranking and bounded
Gaussian escape lifecycle. This policy does not claim a scalar local-minimum,
stationary-field root, or global-minimum certificate. Preserve the separate
continuous direction question and evaluator-only global-arrival criterion.

Default policy `angular_profiles_v1` keeps current behavior. The new policy is
valid only for robust simulation, rolling continuous search, recurrent_geometry_v3
and the current centered_tracking_v1 collection. The detector thresholds,
persistence, geometry and controller gains stay unchanged in this iteration.
Raw angular amplitude/disagreement remain measured diagnostics; do not set
`informative` true when its old amplitude test fails.

## Evidence authority and raw-cost decision

Before allocating a selected candidate, the supervisor must join the original
DetectorConfirmation and confirmed RecurrentConvergenceDiagnostics, in either
callback delivery order, against its fresh valid SEARCH context. Preserve exact
run/frame/source-topic/epoch/sequence/center/score identities, source-time and
history support, branch arithmetic, persistence and source-gap limits. Reuse the
existing recurrent diagnostic validator and detector state/epoch authority.
Require complete support and persistence inside the current SEARCH epoch, never
commanded VERIFY or escape histories. Missing, stale, conflicting, wrong-context,
wrong-metric or invalid diagnostic evidence cannot nominate a candidate. Retain
original receipts on duplicates; bounded pending joins expire without refreshing.

Keep source/profile collection safeguards: synchronized raw observations, three
actual complete rotations, source gaps, comparable spatial/sector trajectories,
bounded neighborhood and original8/12/20s timing, finite negative baseline/cost
intervals, uncertainty, frozen center, candidate/fill association and ranking.
For this selected policy, raw cost is usable when those quality conditions pass
and the authenticated recurrent trapping nomination exists. The new state-machine
input names verification acceptance independently of angular informativeness.
Unselected policies continue requiring the old informative gate exactly.

## Typed compatibility and ownership

Preserve existing CandidateSnapshot, FillCommand and other IDLs, CDR layouts,
legacy snapshot hashes, and clone-schema checks byte-for-byte. Add only two opt-in
wrapper messages through ros_esc_interfaces: RecurrentCandidateSnapshot carries
an old CandidateSnapshot plus policy_id, original DetectorConfirmation and original
RecurrentConvergenceDiagnostics; RecurrentFillCommand carries an old FillCommand
plus the same policy/certificate fields. The command already contains its raw
snapshot, so do not duplicate the observation array in another nested snapshot.
New selected topics are `/gesc_gaussian/v2/recurrent_candidate_snapshots` and
`/gesc_gaussian/v2/recurrent_fill_commands`.

The selected wrapper hash includes policy and full original certificate together
with immutable snapshot content, excluding publication/hash self-fields. That
hash is the selected nested snapshot/command evidence_sha256 carried through
PREPARE/ACTIVATE/CANCEL and the unchanged FillResult/registry/ACK chain. Use a
separate explicit selected hash/wrapper helper; old snapshot_sha256 remains
unchanged and would reject these hashes under the old policy. Publish/subscribe
only the selected topic/type through the existing supervisor and fill-runtime
owners. This avoids a second transaction pipeline or a cross-topic certificate
wait/ACK. Common command processing must include proof identity in deduplication
and immutable activation/cancellation checks. Reject foreign/unknown policies.

Keep the same fill worker, numerical basin/fill design, registry transaction,
count limit, freshness/pose/command lease, cancellation, final-zero and cleanup
owners. Do not interpret clipped curvature/floored depth as mathematical proof.
The recorder and lifecycle validator must select the new wrapper topics and
compare embedded certificates with the actually recorded diagnostic/confirmation
and SEARCH context. Preserve old topic/type validation and old bag decoding.

## Bounded development sequence and gates

1. Implement in the existing owners and add focused policy/authority/transaction
   tests. Build only the changed simulation interface package in a fresh external
   overlay,<=120s. Focused/regression suite<=120s. Cover old CDR/hash/clone parity;
   selected certificate hash/roundtrip/tampering; both callback orders; duplicate,
   stale, invalid, conflicting or wrong-epoch confirmation/diagnostic; commanded
   orbit, transient or interrupted SEARCH authority; raw geometry/negative-cost/
   ranking failures; PREPARE/ACTIVATE/CANCEL/expiry and record-to-certificate joins.
   Do not widen production freshness windows to make a test pass.
2. Retained input check<=90s. Existing caches lack full original diagnostic and
   confirmation messages. Permit one filtered extraction from the original D/noise
   bag through the existing bag owner: recurrent diagnostics, detector confirmations,
   SEARCH contexts and relevant state/readiness authority. Retain original CDR/
   type/topic/time or exact wire payload hashes, bounded row counts and all failures.
   This is not a new full analysis. Pair the four actual D nominations with their
   existing four raw-profile windows; preserve C's four windows as unselected
   comparison. Recompute raw evidence and selected certificate acceptance; require
   all four D nominated supports to be causally valid and keep old amplitude failures.
   Report nominated-support timing separately from true trapping onset.
3. Reuse R10's fixed independent detector controls unchanged; source preservation
   carries its measured36/36 positive and0/48 negative result. Add independent
   transport/authority controls above; a field label alone is not trajectory truth.
   The retained check must also exercise the actual fill proposal owner on selected
   immutable samples and report proposals, caps and rejection reasons,<=16 proposals.
4. Only after source/retained evidence works, freeze a preparation appendix for one
   visible noisy D integrated case, reusing the existing single-case scenario runner,
   recorder, validators and direction-reference owners. Fresh identity and noise
   seed260921001; selected two-light secondary layout and0.015V noise. Preserve
   source/model/controller settings except the explicit evidence policy. Goal is
   one authenticated continuous verification, a committed bounded fill, completed
   escape/recovery and global arrival without mandatory stopped sweeps. Capture
   detector timing, exact verification/proposal decisions, direction error and
   availability, final-zero/cleanup/completeness. Arrival within0.5m suffices and
   GOAL_HOLD is optional. Freeze the exact finite stage/simulation/root budgets,
   analysis target times and direction gates before dispatch; no more than600sim
   seconds/720wall seconds inclusive for this development case and its cleanup.

The visible-case appendix is required before dispatch because launch/types and
source-validation receipts are not available at plan adoption. There is no new
16-run matrix release. Failed fixed experiments remain failed. Diagnose and
version bounded corrections prospectively; do not replace a run or relax gates
inside this version. Keep logs/artifacts outside Git, exact commands and receipts,
independent cached reviews, live status and material checkpoints.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r21_recurrent_trapping_v1/`.

R21 is simulation-only. No physical/Pi/snapshot/V1/commit/push action. Full
augmented SEARCH direction confidence remains unproven until direct measurements;
R21 verification success alone cannot close the overall goal.
