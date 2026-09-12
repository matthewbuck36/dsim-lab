# Q1 prospective qualification — 2026-09-09 UTC

Status: ACTIVE SOURCE/PREFLIGHT MILESTONE under the approved full implementation
scope. This selects a separately versioned, bounded prerequisite study after M3;
it does not change earlier labels/grids/results or release the M4 pilot.
Gazebo dispatch requires the source checks, exact machine-readable contract and
pre-acquisition checkpoint below. No Q1 run has started.

M3 is closed at the verified source archive
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m3_boundary_v1/`, manifest
SHA256 `0e144f64d392741f5388a2eaef4c0b98dd1f9068669eb1de1b3533e644602920`.
The proposal `qualification_release_review.md`, SHA256
`a14902692d127914f72083e12afbb16139eba7b6497f193d491ddf0afc781f4f`, supplies the
frozen primary geometry, deterministic starts, receipt-chain requirements and
methodological rationale. This active plan selects that four-run design with
explicit timing/comparator clarifications below. Physical work remains excluded.

## Purpose and finite version

Acquire source-correct natural continuous-GESC trajectories for the missing
positive residence and same-trajectory direction reference evidence. Suppress
candidate-triggered intervention during observation through the existing
supervisor; never hold the robot inside a region or suppress a safety stop.
Keep detector/Gaussian scientific outcomes separate from recording integrity.
Use exclusive version `q1-primary-shadow-v1` and new artifact directories under
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1/`.
Never overwrite an existing output, substitute failed inputs or run until success.

| Order/partition/exposure | Seed | world x m | world y m | yaw rad |
| --- | ---: | ---: | ---: | ---: |
| 1 discovery residence, visible | 26090911 | 0.8497226717798214 | 1.3184726717798212 | -0.8850668158886104 |
| 2 discovery approach | 26090912 | 0 | 0 | 0.7853981633974482 |
| 3 confirmation residence, sealed | 26090913 | 1.2715976717798214 | 0.8028476717798212 | 2.256525837701183 |
| 4 confirmation approach, sealed | 26090914 | 0 | 2.1213203435596424 | -0.7853981633974482 |

Use exactly the primary source positions,400/1600 relative-lumen inputs and
bounds in the proposal; preserve selected gains, washout/demodulation, speed
ceilings0.1m/s and0.5rad/s, sensor geometry and20rpm nominal rotor. Measured
world phase remains authoritative. Select zero introduced noise/delay, robust
profile, rolling GESC and explicit shared run identity/source schema2. These
are development model inputs, not physical calibration. Verify source/model/
installed assets and world/odom coordinate correspondence before dispatch;
record first qualified pose versus requested spawn before using spatial labels.
The fixed coordinate check uses the first finite selected `/odom` pose before
recording readiness, frame `odom`, position error<=0.02m and wrapped yaw
error<=0.05rad. Missing pre-ready pose or mismatch is an input failure; do not
fit an offset or substitute a later favorable sample.

Each run ends after **125 simulated seconds from recording readiness**, with
independent240s overall wall limit and existing bounded shutdown. The extra5s
relative to the proposal's120s is a prospective fixed tail for the12th reference
target and its50ms causal anchor window. It is not run-until-input or a shifted
reference population. If first input arrives too late, missing targets remain
missing. All four acquisitions and cleanup have an outer1200s ceiling. The
first run is visible; remaining runs may use batch mode. Record both clocks.
Keep existing `--duration-sec` wall semantics; add an optional simulated-time
completion condition to the existing recorder/runner rather than a second
recorder or unbounded external loop. Paused clock still reaches wall timeout;
clock rollback, target exit and cleanup retain explicit failure semantics.

The240s recorder-process ceiling comprises180s for acquisition/finalization,
45s shutdown grace and at most15s of the existing three escalation waits.
The preflight timeout is60s within the180s budget. Suite setup, result checking
and dispatch share the1200s outer ceiling; no deadline is restarted after a
failed case. This fixes the implementation meaning of the prospective cap,
without increasing it. Retained primary seed19801 recorded clock0.1–294.5s
between wall receipts296.593s apart; recorder ready-to-end lasted300.352s.
That approximately real-time historical run supports trying this bounded
125s exposure, but does not guarantee current runtime speed or completeness.

Safety, recording/source-integrity or cleanup failure stops dispatch. A finite
behavior/exposure failure remains an outcome. Confirmation source integrity may
be checked while collecting/sealing, but its detector/direction results may not
be used for nomination. Never modify code/tuning from confirmation outcomes.

## Source milestone and ownership

1. Existing supervisor/state machine: startup-only default-false
   `v2_qualification_observation_only`, allowed only in robust rolling simulation.
   Reject candidate acceptance before IDs/epochs/snapshots/commands are consumed;
   suppress convergence transition only inside SEARCH. Preserve earlier clock,
   explicit stop, controller, pose/source and recovery checks, SEARCH weights,
   state/epoch publications and controller final zero. Unexpected non-SEARCH
   safety/recovery intervals are reported/interrupted, not suppressed.
2. Existing schema/runner/launch/recorder: explicit mode wiring, resolved metadata,
   optional simulated observation duration and finite existing shutdown owner.
   Require healthy source registration/readiness; do not relax completeness to
   obtain a run. Keep positive M3 neighborhood startup requirements.
3. Existing analyzer/reference owner: strict schema2 input adapter, fixed target
   receipts, independent geometry labels, finite neighborhood nomination and
   immutable confirmation evaluation. No duplicate numerical/control owner.

During shadow acquisition, online diagnostic parameters are W=6s, detector
score epsilon0.30m and radius0.75m. Inactive candidate configuration is explicitly
radius0.75m and per-cycle/sector tolerance0.15m. Observation-only policy prevents
these unqualified values from authorizing any fill/GOAL; they are not calibrated.
Offline nomination evaluates the finite R/tolerance grid below from the same
recorded source, without treating online diagnostic timing as ground truth.

Acquisition uses the existing schema2 recording contract with explicit new
`purpose: qualification_observation`. This purpose admits the later selected
launch controls only when simulation, robust rolling observation-only mode,
positive simulated duration and both stop-on-failure flags are declared.
All merged algorithm controls retain their normal parameter checks. The three
acquisition predicates are recording_complete, cleanup_complete and
no_forbidden_events; FAILSAFE and RECENTER_STARTED are forbidden during the
recorded ready interval. Unexpected intervention events are forbidden too.
Normal shutdown falls outside that interval; ambiguous cross-topic receipt
ordering fails conservatively. This does not change any old schema/formal
lifecycle contract or turn acquisition completeness into scientific acceptance.
Detector-origin CONVERGENCE_CONFIRMED is permitted as the shadow observation;
it is not itself supervisor acceptance or an intervention. The new policy
blocks that downstream acceptance while preserving detector diagnostics.
Each case uses a reserved explicit run ID through the existing single-case
runner, recorder, launch and metadata. The first case adds the existing --gui
option; the other three retain batch mode. Exact resolved commands are frozen
before dispatch.

Before acquisition: focused default/opt-in/fault/final-zero owner tests; both
confirmation kinds produce no intervention; simulation duration tests cover
held/slow/backward clocks and cleanup; typed adapter rejects conflicting or
unbound source/objective identities, preserves first publication and original
receipts, and never qualifies from output confidence. Build/resolve launch and
installed bindings. Freeze complete code/config/IDL hashes, source/geometry
receipt chain, exact run IDs/scenarios/commands/caps and analysis definitions in
a machine-readable Q1 contract. Review diff, checkpoint, then record dispatch
release in the live status. Current plan alone does not start Gazebo.

## Detector and neighborhood nomination

W=6s and detector score epsilon0.30m are nominated analytically before data,
using the previously recorded0.272229375505m small-circle bound versus at least
0.542629797669m translating-circle bound. Straight-drift resolution is0.01m/s;
no claim covers arbitrarily slow drift. Preserve six full source-time windows,
strict score, original confinement and all source/epoch reset rules.

Discovery compares exactly nine pairs: shared detector/candidate R in
{0.25,0.50,0.75}m and M3 per-cycle/sector tolerance in{0.05,0.10,0.15}m. Detector
score epsilon and M3 tolerance have different meanings. Evaluate existing
moving-evidence code at actual frozen candidate centers and its latest three
qualified cycles within original12s; never use region centers, older favorable
cycles or augmented confidence as raw verification authority. Among pairs
passing all discovery requirements choose smallest R, then smallest tolerance.
Freeze one nomination/hash before opening confirmation data. No qualifying pair
means that finite nomination fails; do not inspect confirmation to choose another.

For offline M3 timing, retain both the centroid window end and the actual pose
source time C that first completes candidate eligibility. Use C+12s as the
conservative evidence deadline. An observation is available only at its first
recorded diagnostic publication, and must be available by the evaluation time
and deadline. Preserve source order and raw-buffer reset rules. Departure of
any actual admitted pose from the frozen candidate neighborhood, including the
completing pose, cancels before evidence acceptance; leaving and returning
cannot revive the candidate. This qualifies recorded evidence availability,
not an unobserved supervisor callback time or actual fill activation in shadow
operation. Missing raw cycles remain missing evidence.

Retain independently qualified cell masks and holes, segment-boundary uncertainty
and conservative possible-well exclusions. Freeze spatial labels before detector
outputs. Positive residence uses the established12s minimum; directed negatives
use a six-second segment chain outside exclusions, net>=0.12m and net/path>=0.80.
Unknown stays unknown. Readiness/SEARCH/input validity is a separate mask.
For this single-W study, each residence partition needs an uncensored first
opportunity with42s uninterrupted eligible support:36s numerical history plus
one6s lattice-alignment allowance. Shorter real residences are censored, never
joined or replaced by a later favorable opportunity. This does not alter the
closed historical54s comparison.

Require detection within each required positive residence; at least one declared
negative interval in each approach partition and zero flags on every declared
negative; and valid candidate-centered informative M3 evidence for every required
positive detection. Confirmation must pass the identical frozen requirements.
Negative exposure additionally requires a complete6s chain with uninterrupted
eligible selected-pose/SEARCH-generation support inside a declared spatial
negative. Preserve the spatial labels and separately report eligible negative
exposure; unavailable detector input cannot establish zero false flags. This
uses the same pose/support rules, without a new raw-cost bracketing condition.
Report all positive/negative/unknown/censored outputs and support denominators.
Matched old/new latency is reported when observed, or with a censoring bound;
no synthetic median or erroneous-fill rate is inferred from shadow operation.
The actual>=30% improvement/wrong-fill/GOAL targets remain M4 outcomes.

## Direction targets, reference and comparator

Fix12 targets per run: T0+10k seconds for k=1..12,48 total. T0 is the first
input-qualified typed synchronized source observation after recorded readiness
(its first diagnostic bag receipt is inside that readiness interval), independent of filter
confidence, state of averaging, vector magnitude or field reference. At each
target use the first input-qualified source sample within50ms afterward;
no replacements. Freeze target definitions before acquisition, exact source
identities before field/reference evaluation, and confirmation identities only
after the nomination receipt unlocks that partition. Missing slots stay missing.

Use actual schema2 source sequence/model-input time, source/pose/encoder receipts,
observed sensor geometry and recorded augmented objective. Strict ambiguous-key
quarantine remains; no historical timestamp reconstruction or raw-objective
substitution repairs missing data. Use the first diagnostic publication for each
immutable observation, never a later repeat selected for qualification/output.

Primary paired comparator is the **aligned instantaneous GESC component** already
recorded before averaging (`instant_body/world`) versus actual recorded rolling
output transformed using its recorded output yaw. This preserves the selected
inherited equations/sign/gains on identical aligned input, without claiming to
reconstruct an old subscriber's callback timing from bag order. Any mathematical
replay is separately named sensitivity/parity evidence and is not the primary
runtime comparison. Output validity/weakness/fallback are denominator outcomes.

Reuse unchanged `v2_direction_reference.py`/evaluator numerical owners and the
M2 reference's actual sensor geometry, signed observed world angular rate,
continuous washout transfer, independent quadrature/error limits, informative
floor and rate CV<=0.10. Match the recorded augmented law even with zero fills.
No nominal phase, changed tolerance or discarded unfavorable anchor is allowed.
Require at least six informative input-covered anchors in each confirmation
bag; pooled confirmation median error<=30deg, p90<=60deg and averaging availability
>=80% over the full predeclared eligible denominator. Usable averaging requires
valid output, blend weight0.5 and finite world-output magnitude>1e-6; report
the separate blend-applied count. Missing or zero output never manufactures
an angular error or usable average. Report every bag and all
missing/weak/fallback reasons. This is selected primary-field evidence only.

Limit label/nomination analysis to one600s job, and reference evaluation to
one300s job with48 fixed slots. Retain per-anchor receipts and partial/final
outcomes on timeout. Fresh corrective versions need explicit diagnosis and an
amendment; never automatically rerun a closed fixed computation or add targets.

## Completion and pilot boundary

Q1 ends with exact source and acquisition evidence, a frozen discovery choice
or honest failed/unavailable outcome, untouched confirmation selection boundary,
qualification results with denominators, retained limitations and a handoff/
checkpoint. Missing natural exposure is EVIDENCE_UNAVAILABLE; measured failure
is FAIL. Neither is synthetic correctness or a permanent ban on development.

Release the unchanged four-arm16-run pilot only after the required source,
recording/cleanup and independent component qualification gates pass. Preserve
primary seed26090801, secondary seeds26090802–26090804, disturbances, wall caps,
held-out comparison and original outcome targets. A failed new study must be
closed and diagnosed, never presented as pilot readiness.

## Pre-acquisition launch correction

The first source contract at `preflight/contract.json`, SHA256
`0921e90a3d705fe1ff46abcd47f4116b559c9f542d0dd59ad7cc8d418c5a1e05`,
remains at its original path with `contract_v1_unreleased.json`. It was never
released or used for acquisition. The actual Humble launch frontend rejected
V2 argument quotes spanning substitution fragments, despite syntactically valid
XML. Correct those argument boundaries through the existing launch owner and
test the real frontend plus resolved legacy/rolling argv. Preserve YAML string
typing for ROS parameters and empty legacy defaults. This is a bounded startup
correction, with no scientific input/tuning change and no Gazebo attempt.
Use an exclusive replacement contract file after the corrected checks; the
acquisition/evaluation scripts now require its explicit --contract path.
