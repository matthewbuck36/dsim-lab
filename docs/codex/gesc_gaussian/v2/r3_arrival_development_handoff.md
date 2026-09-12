# R3 arrival development handoff — 2026-09-10

Later update: [R4 stationary integrated handoff](r4_stationary_integrated_handoff.md)
supersedes this historical handoff's pending Arm B implementation and runtime
environment advice. Its recorded D02/D03 observations and failed results remain.

The user clarified that reaching the global minimum is success; GOAL_HOLD is
not required. The adopted [arrival criterion](global_arrival_acceptance_20260910.md)
uses the existing evaluator-only 0.5 m global-source tolerance. Runtime safety
stops and holding behavior remain available. No physical, Pi, snapshot or V1 work.

## Established evidence

- The frozen recurrent detector passed a new 96-history component check: all
  36 positives detected, zero confirmations on 48 negative controls, and 12
  explicitly gray/unsupported histories excluded. Circle detection was 42 s;
  oscillation median 48 s/max 66 s; static median 30 s/max 42 s. Exact original
  vertices, irregular sampling and expanded translated-oscillation controls
  were retained. See [frozen component validation](validation/r4_frozen_component_confirmation.md).
- Visible attempt02 recorded a valid local candidate, three moving verification
  revolutions, one committed fill, assisted escape, restored ordinary search,
  and global arrival at 141.146 simulated seconds. Every subsequent recorded
  readiness pose stayed within the arrival radius for 39.066 s; closest distance
  0.199456 m, final 0.252970 m. Its lifecycle and cleanup pass. Actual measured
  motion continued through approach, verification and fill design; brief
  same-tick zero-command publications are retained, not hidden. See
  [acquisition](validation/r3_visible_development_02.md),
  [motion](validation/r3_visible_02_moving_collection.md), and
  [analysis/reference](validation/r3_visible_analysis_02.md).
- Attempt03 used a fresh nominal seed and the executable arrival criterion.
  It completed direct repulsion escape, resumed SEARCH, and stopped at actual
  global arrival at 155.971 s / 0.498596 m. Live and retained local-recovery and
  arrival evidence agree; lifecycle, complete recording and cleanup pass.
  Its inherited overall verdict remains failed only on a real geometric exit
  alignment miss (0.59137 versus 0.80), despite passing actual authority and
  exit checks. Separate that diagnostic from selected arrival success; preserve
  the old verdict. See [attempt03 evidence](validation/r3_visible_development_03.md).
- Independent recorded-position/observed-phase GESC references support the
  moving estimator on five eligible02 targets (median error 12.307 degrees,
  p90 34.940) and four eligible03 targets (median 5.324 degrees, p90 21.031).
  Every eligible estimate improved on its paired instantaneous estimate.
  Ineligible and unexposed targets remain in the denominator tables. These
  are selected development measurements, not arbitrary-field guarantees.

The source retains selectable legacy behavior and GESC/Gaussian ownership.
Current opt-in methods are `recurrent_geometry_v3`, `rolling_gesc_v2`,
`moving_cycle_coherence_v1` and `centered_tracking_v1`. The actual interface
environment is external `development/20260910/centered_runtime_v2/environment.sh`.
Use that schema2 overlay rather than the retained schema1 environment.

## Current corrections and evidence boundary

The actual constructor-routing correction is validated. The private recurrent
evaluator coordinate now uses the confirmed history endpoint, while retaining
the diagnostic's latest input pose and publication stamps; old centroid/public
message semantics remain unchanged. The selected arrival criterion no longer
requires terminal ranking or GOAL_HOLD. See
[arrival source validation](validation/r3_arrival_evaluator_correction.md).
The direct/assisted alignment diagnostic separation is also source-validated
(240 focused/legacy checks pass, one optional Gazebo check skipped). The actual
ownership, freshness, command limits, measured exit and later handoff checks
remain required; selected arrival success reports bearing alignment separately.
See [alignment source validation](validation/r3_arrival_alignment_separation.md).
This closes the bounded method-development/arrival-rule source work. No new Gazebo is needed solely to replace a failed label.

Attempt01 remains startup INCOMPLETE. Original02 and03 frozen overall verdicts
remain failed under their historical contracts. Their independently valid
arrival observations remain usable under the user's explicitly revised success
criterion. V9 remains CLOSED_INCOMPLETE; no old result, run, label or holdout is
reopened or promoted. No full comparison or unseen-condition confirmation ran.

## Analysis feasibility and next comparison work

Single-run integrated analysis is working:02 completed in 71.974 s,03 in57.958 s,
each within120 s with two native scans and full lifecycle validation. Reference
jobs completed in6.762 and5.765 s within45 s, without additional bag scans.

The historical four-run labels benchmark still times out at its original120 s
cap. A one-C profile reproduced41.943 s analysis plus15.908 s decode, with exact
output parity. Mandatory hash, history and source validation dominate. No
speculative cache/optimization was implemented. D3 estimates169–186 s for the
retained full block; this is an inference, not measured completed block timing.
Its suggested240 s future block budget is not yet adopted. See
[profile evidence](validation/r3_c_analysis_profile.md).

Before any new four-arm16-run release, save a new prospective comparison
contract and retain these boundaries:

1. Arm A is PDE/stationary, B recurrent/stationary, C PDE/rolling+centered and
   D recurrent/rolling+centered. Matching the continuous acquisition package
   across C/D preserves the detector contrast. A/C is a package comparison,
   not an averaging-only causal claim.
2. Recurrent stationary Arm B is not implemented. Reuse existing stationary
   adapters with a distinct `StationaryRecurrentFillRequest` envelope embedding
   the full recurrent diagnostic; preserve the old request/type/topic. Extend
   exact recorder/analyzer joins, original receipt leases and frozen samples.
3. The comparison's existing science aliases omit recurrent diagnostics and
   centered guidance. Its fixed arm mapping, stationary authority and legacy
   GOAL_REACHED timing require explicit new-version integration. Do not edit
   frozen M4 identities or reinterpret old centroid wires.
4. Report recorded arrival timing separately from controller-recognized goal.
   The existing motion metric wrongly equates every zero publication or missing
   per-heartbeat diagnostic with unavailable continuous acquisition. Extend that
   owner using exact guidance/state/command and measured-motion evidence; retain
   zeros, coverage gaps and safety reasons rather than waiving them.
5. A complete baseline behavioral failure or explicitly censored latency is a
   valid comparison outcome. Analysis timeout, missing authority/inputs, changed
   source, incomplete recording or failed cleanup blocks confirmation release.
   Require usable completed development analysis and credible integrated behavior
   before the twelve confirmation slots. The old ledger alone is insufficient.
6. Existing first-residence latency may legitimately be unobserved (C's first
   residence lasted7.786 s and later opportunities were excluded). Preserve the
   original30% latency claim as unestablished if its paired endpoints are absent;
   define any new estimand before freeze. Do not manufacture a latency number.
7. All exposed V1–V9, R1/R2 and visible02/03 data remain development. Reserve
   fresh confirmation data/identities and describe condition exposure honestly.
   Fresh seeds do not make previously examined geometry an unseen condition.
8. Adopt any fresh analysis/acquisition budgets prospectively from measurements.
   Keep full validation and late hashes. Do not rerun the old failed benchmark
   unchanged or launch another large matrix solely to repair bookkeeping.

The full V2 phase and four-arm qualification remain in progress. Selected
arrival/component evidence is established; broad robustness and the historical
30% latency target are not established by this handoff.

## Repository recovery

Branch `feature/gesc-gaussian-robustness-v2`, HEAD
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`. Changes remain uncommitted; no push.
The source/evidence checkpoint at this boundary is recorded in the live status
and `checkpoint.txt`. Before further edits read AGENTS, current plan/amendments,
status and Git diff, then run the existing V2 context validator. Retain all
external evidence under `/home/mattb/Experiments/GESC-Gaussian/v2/`.
