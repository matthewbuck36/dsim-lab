# Fresh Q2 primary qualification plan

Status: original q2-primary-shadow-v1 CLOSED_INCOMPLETE after the dated-directory
workflow rejection. Its scientific settings below are preserved. The separately
versioned continuation of the user goal is specified in
q2_acquisition_path_correction_plan.md; no original attempt is reopened.
Q2 runtime source closed at checkpoint
`checkpoints/q2_policy_runtime_closed_v1/manifest.json`, SHA256
`7df68a0af0b4fb953fc0631a4a5d0f9572d718a5ba74818deed025b583327863`:
252files,1045977-byte archive,482 retained hashes. Runtime has1167 held integrated
checks plus fixed performance and actual DDS validation. Adopt the reviewed
proposal below with the explicit sealing/branch clarifications at the end.
Source/workflow implementation is authorized first; acquisition requires its
concrete preflight freeze/release after focused tests and isolated build. No
old confirmation or M4 release. Read plan.md, status.md, the Q2 runtime handoff
and this amendment before editing.

## One fresh four-case study

Use exclusive version `q2-primary-shadow-v1`, output root
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q2_primary_shadow_v1/`.
Reserve fresh IDs and verify seed/output nonuse from manifests before dispatch.
Verify these seeds and output roots are unused before reserving or dispatching them.

| Partition / exposure | Seed | x m | y m | yaw rad |
| --- | ---: | ---: | ---: | ---: |
| Discovery residence, visible | 26090921 | 0.8497226717798214 | 1.3184726717798212 | -0.8850668158886104 |
| Discovery approach | 26090922 | 0 | 0 | 0.7853981633974482 |
| Confirmation residence, sealed | 26090923 | 1.2715976717798214 | 0.8028476717798212 | 2.256525837701183 |
| Confirmation approach, sealed | 26090924 | 0 | 2.1213203435596424 | -0.7853981633974482 |

These are exactly Q1's input-derived starts. Retain its primary sources,
400/1600 relative-lumen inputs, bounds, gains, sensor geometry, 20rpm nominal
rotor, speed ceilings 0.1m/s and 0.5rad/s, zero introduced noise/delay, robust
rolling source-schema2 simulation and existing observation-only supervisor.
Select live `moving_cycle_coherence_v1` with its immutable .75/.25 policy and
descriptor; no tuning within this study. Keep existing shadow detector
W6/epsilon.30/R.75 and inactive M3 R.75/tolerance.15.

Reuse Q1's 125 simulated seconds after readiness, 240s per-case wall ceiling,
and 1200s whole acquisition ceiling with existing cleanup budgets. First case
visible, subsequent batch cases permitted. Check first finite selected pre-ready
odom against requested spawn (position <=.02m, wrapped yaw <=.05rad). Do not
fit a coordinate offset from outcomes. Preserve recording, exact launch/source/
policy companion binding, safety, no forbidden interventions and final-zero/
cleanup gates. Any acquisition integrity/safety/cleanup failure halts dispatch.
All four recordings may be collected and sealed before scientific evaluation;
confirmation inspection is limited to the declared acquisition integrity checks.

Fresh nominal seeds do not establish independent stochastic replicates: these
are two prospectively withheld cases on a known primary field, not broad
robustness evidence. No old confirmation recording is imported or opened.

## Keep detector and neighborhood gates intact

Reuse the verified primary geometry receipt
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1/geometry_1.json`,
SHA256 `8f4f7fc53b67144317dd2e4640871c29ac5eb6c0d7e2cbc6ca3521a6c24788dd`,
with its original full receipt chain, task-body/model/geometry bindings and
qualified masks. No new enclosure optimization is needed when those inputs
match. The hole remains outside the certified positive region. This label is
near-minimum residence, not proof that all spatial confinement is convergence.

Freeze input-only labels before detector outputs. Preserve the 12s genuine
residence definition, unknown/boundary semantics and actual selected-pose
knots. For each SEARCH epoch the **first eligible segment of the first genuine
opportunity** must supply42 uninterrupted seconds:36s history plus6s alignment
allowance. If short or interrupted, censor that opportunity and later same-
epoch residences; do not join or replace them. Each residence partition needs
at least one such uncensored opportunity. Preserve one confirmation per epoch.

Evaluate only the nine shared R/tolerance pairs: R in{.25,.50,.75}m and M3
tolerance in{.05,.10,.15}m; W6 and detector epsilon.30 stay fixed. Each approach
partition needs an eligible complete6s directed-negative chain outside the
unchanged exclusions, net displacement >=.12m and net/path >=.80. Require zero
flags on all declared negatives, detection of all supported required positives,
and valid informative candidate-centered latest-three-cycle M3 evidence.

Use actual completing-pose source time C, original C+12s deadline, first
recorded diagnostic availability, and departure cancellation including the
completing pose. Keep spatial truth separate from SEARCH/readiness/source masks.
Select the smallest passing R, then tolerance, from discovery; freeze its exact
receipt before any confirmation scientific read. Confirmation applies that
single pair with identical requirements. Preserve positive, negative, unknown,
censored and unavailable counts. Missing exposure is not zero false positives.

## Prospectively adapt the reference, not its numerical gates

Freeze 12 targets per run, T0+10k (k=1..12), 48 planned slots. T0 is the first
input-qualified source observation whose first diagnostic receipt is inside
readiness, independent of confidence/magnitude/output. Choose the first
input-qualified source sample within50ms after each target, requiring its
original receipt/readiness. Assess full-cycle support only after that fixed
selection; missing support remains unavailable, never a reason to choose a later
sample. No replacements or later diagnostic substitution. Freeze exact source
identities before model work.

For this new study explicitly select the existing `observed_phase_cycle` and
`observed_phase_reference`: stationary anchor position, complete recorded
augmented objective, periodic repetition of the actual source-time phase
waveform, alpha1/s and d.18m. Keep signed phase/sector/source/context/freshness
checks, dual quadrature, all knots/angular splits, 25,000 distinct evaluations
per target, normalized component error <=1e-6, closure/DC checks and informative
norm >max(1e-6,20E_q). World-rate CV becomes descriptive because this declared
model represents its variation; old Q1/D1's CV.10 and old results are unchanged.
No raw-cost substitution, phase smoothing or extrapolation is allowed.

Primary comparison is recorded aligned instantaneous GESC versus the actual
recorded .75-policy output in world coordinates on this newly acquired path.
It is not an old-controller trajectory replay or a latent blend. Keep the
existing confirmation targets: at least six eligible informative anchors in
each confirmation run, pooled actual median error <=30deg, p90 <=60deg and
usable averaging >=80% of eligible informative anchors. Usable averaging
requires actual valid .75 application and meaningful finite output. Missing/
weak outputs remain in availability's denominator; angular quantiles remain
explicitly conditional on meaningful recorded vectors. Report all48 planned
slots, missing reasons, per-run coverage/errors, actual fallback, and the
aligned instantaneous comparison. Do not select another weight from Q2 data.

Recommend one predeclared branch to avoid another avoidable diagnostic cycle:
reserve one300s reference job. If discovery detector nomination passes, evaluate
all48 slots after its receipt unlocks confirmation. If it fails/is unavailable,
evaluate only the fixed discovery24 as a diagnostic; mark the other24 SEALED
without reading their inputs. Preserve a genuine discovery FAIL as FAIL; only
insufficient evidence yields EVIDENCE_UNAVAILABLE. The discovery-only branch is diagnostic. The48-slot branch may satisfy
direction gates; it cannot overwrite a detector failure or independently
release M4.
Discovery direction results then remain useful without weakening detector gates
or opening confirmation. This branch must be declared in the fresh contract
before acquisition; it is not a fallback population selected by reference errors.
Keep the single600s label/nomination job and incremental exclusive receipts.

## Narrow implementation and honest release branches

Extend existing Q1 acquisition/label/target/reference owners with an explicit
new study version/population and policy-input normalization. Reuse
`prepare_moving_policy_direction_inputs`, existing geometry verifier, label
and moving-evidence owners, and observed-phase numerical owner. The current
D2 diagnostic wrapper is tied to old lineage/24 targets: do not forge that
lineage or waive old contract freshness to process Q2. Preserve old APIs and
results; test the new version/48-or-sealed24 dispatch and strict companion joins
with synthetic fixtures before freezing current source/config/installed hashes.

- Acquisition integrity/safety/cleanup failure: stop; preserve incomplete inputs
  and diagnose before any separately authorized version. No automatic retries.
- No uncensored residence/negative exposure, informative reference shortage or
  missing required M3 support: EVIDENCE_UNAVAILABLE. Keep the narrow annular
  label and42s gate. A later positional-confinement study would need a separate
  prospective definition and claim, not a Q2 repair.
- Missed supported positive, negative flag, invalid required verification, or
  measured direction threshold failure: FAIL. Preserve all settings/targets;
  confirmation may never select replacement parameters or a policy.
- Timeout: INCOMPLETE with partial receipts, not a favorable reduced sample.
- Both components pass held confirmation: selected-primary-field prerequisites
  are satisfied; review the remaining acceptance ledger before releasing M4.

Still unmeasured here: actual earlier-trigger closed-loop intervention, erroneous
fill/GOAL rate, >=30% matched latency improvement, fill/escape/SEARCH/stronger-
candidate ranking under holdout disturbances, and practical direction jitter/
lag/fallback duration. Shadow verification proves recorded evidence availability,
not an unobserved supervisor callback or successful fill activation. The periodic
reference remains a local stationary-response model, not a spatial-gradient or
translation/transient error certificate. These limitations and the original
four-arm16-run M4 comparisons remain; this study cannot silently replace them.

## Source preflight clarifications

Bind the closed Q2 runtime checkpoint and any declared serialization correction,
explicit Q2 expected_build, installed console wrappers/metadata/modules, generated
interfaces, exact environment and current source/config receipts before dispatch.
Both label and target bag readers must include the policy companion and select
the moving-policy normalizer. The expected_build helper is implemented; it is
not an outstanding acquisition source prerequisite. Original Q1 and D1/D2/D3
artifacts remain closed. This plan is adopted; no acquisition has been run.

## Adopted sealing and branch clarifications

- Reserve all48 symbolic (run,seed,anchor-number,offset) slots in the input
  contract. Confirmation T0/source stamps and input traces are computed only
  after a valid hashed discovery nomination permits those scientific reads.
  Before then its24 slots explicitly have SEALED status and no derived times.
- Existing select_causal_anchor already selects the first input-qualified ready
  sample within50ms. Preserve it unchanged; assess cycle support afterward.
  Add a case where the selected sample has no complete cycle but a later sample
  does, proving there is no favorable replacement.
- A completed discovery nomination receipt determines the one reference branch
  before numerical calculations. Only PASS unlocks48; completed FAIL or genuine
  EVIDENCE_UNAVAILABLE authorizes the fixed discovery24 diagnostic. Integrity
  errors, invalid/missing receipts, exceptions or timeout never authorize either
  diagnostic fallback or confirmation reads.
- Keep detector result, direction result and final combined qualification
  separately recorded. A successful48-reference direction result can satisfy
  direction gates only; combined qualification also needs held detector and
  neighborhood confirmation. Missing exposure stays EVIDENCE_UNAVAILABLE.

## Existing-owner implementation divisions

1. Acquisition owner: q1_acquisition_layout.py, freeze_q1_contract.py, acquire_q1.py
   and one fresh scenario. Explicit Q2 version/profile maps seeds/root/scenario/
   expected_build; original Q1/recovery import paths remain strict. Freeze Q2
   runtime checkpoint, selected policy descriptor and branch/slot contract.
2. Label/orchestration owner: q1_study.py and evaluate_q1.py. Dispatch by declared
   science version, add policy companion to the existing reader, use the new
   normalizer, preserve geometry/labels/nomination tests, and route completed
   discovery nomination to the predeclared reference branch.
3. Analyzer owner: gesc_gaussian_bag_analysis.py supplies explicit Q2 contract/
   partition validation, versioned existing target freezes and observed-phase
   reference dispatch. Reuse the numerical owner unchanged; do not pass Q2 as
   old D2 lineage or compute a latent blend. Preserve old APIs and contracts.
4. Independent source/workflow tests: valid/invalid versions, slots, companions,
   source/build binding, preflight seals, early causal selection, diagnostic-only
   versus full qualification and partial/incomplete receipt preservation.

Run bounded focused regressions including old Q1/D1/D2 paths and current
policy-normalizer tests, then build only affected installed package resources
and verify declared Q2 bindings. Freeze all source/config/IDs and exact argv
before acquisition. One1200s outer acquisition job, one600s label job and one300s
reference job; no automatic retries. Save checkpoint at material preflight and
completed evidence boundaries. User goal remains active after partial source
work or an inconclusive scientific study.
