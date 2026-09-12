# M4 execution and evaluation amendment

Status: ADOPTED FOR IMPLEMENTATION under the user's approved16-run comparison
and current continuation request, 2026-09-09. Q7 source is closed PASS; its
archive is `checkpoints/q7_two_block_closed_v1/manifest.json`, SHA256
`16dbe96dec7a1f177965e8f047d429d39a44fcb46531e93e02998854c96bc158`.
This resolves the prospective definitions in `m4_plan.md` without replacing
the parent research objectives or changing any closed study outcome.

Active bounded source clarifications: `m4_implementation_clarifications.md`.

## Adopted population, settings and evidence rules

Adopt the exact16-slot order, geometry, matching, GUI, seeds and disturbances
in `m4_plan.md`. B/D explicitly select `centroid_two_block_v2`, W6s,
epsilon0.18m, confinement radius0.50m. A/C retain the inherited PDE settings.
C/D retain Q2 `moving_cycle_coherence_v1` (fixed0.75 mean weighting) and its
held explicit M3 neighborhood radius0.75m/epsilon0.15m. These latter two
values are development settings, not calibrated acceptance results; do not
substitute detector epsilon for the distinct moving-evidence tolerance.
Disable qualification-observation-only mode so actual intervention is allowed.
Every other selected inherited control/geometry/clock/command limit stays fixed.

Adopt the finite prospective label, direction, objective, topology, execution
and release definitions in `validation/m4_prerequisite_audit.md`, with the
precise clarifications below. That document's recommendations are now the
selected contract, subject to source validation and frozen receipt generation
before dispatch. No acquisition is released by this markdown alone.

Independent labels retain the existing qualified finite-grid model regions,
annular holes, exclusions and12s sustained residence. They are model-based
near-minimum residence regions, not certified attraction dynamics. Freeze
position-only intervals before joining detector outputs; never select labels
using confidence, confirmation, fill or goal outcomes. Preserve the first
opportunity, left/right censoring and unknown boundary/timing cases. An
objective-changing intervention ends the unmodified-objective observation;
continued SEARCH is not required after a valid pre-intervention confirmation.
Do not borrow Q1/Q2's42/54-second opportunity gate. Report completed and
censored intervals separately, without changing the original basin-entry claim.

Primary latency comparison uses the six predeclared holdout pairs B/A and D/C
across three conditions. Original30% acceptance requires all12 independently
eligible first endpoints observed; otherwise show any descriptive subset with
its denominator and mark target EVIDENCE_UNAVAILABLE. Compare medians with
positive control denominator; zero/absent control median is unavailable.
Development and per-condition/per-arm pairs remain separately reportable.
No favorable subset can establish acceptance. Wrong fills and terminal
decisions use existing evaluator-grounded event geometry/ranking evidence;
unknown attribution cannot count as zero errors.

Confirmation latency ends at the recorded absolute ROS publication/decision
stamp of the confirmed diagnostic/event, not its earlier history/source support
end. Preserve those support stamps as separate diagnostics. Pose entry uses
original source time in the same simulation clock. Only actual committed fill/
objective intervention bounds observation; PREPARED is not activation.

Direction targets:24 fixed source-time offsets15+30*k, k=0..23 per C/D run,
192 scheduled slots total. First admitted input in[target,target+0.05s], no
replacement. Preserve terminated/unexposed/invalid/uninformative slots and
report every denominator. Actual versus aligned instantaneous output shares
each recorded C/D trajectory/reference. A/B do not gain a synthetic moving
stream. Preserve all numerical reference/phase/sector/informativeness guards.
Targets after fills must bind recorded complete augmented objective; no raw-only
substitution. The reference remains a stationary periodic GESC response under
recorded phase, not a spatial gradient or delayed-motion ground truth.

Whole-run fallback, source/publication delay, goal/path, failures and the
predeclared operational heading jitter/relative smoothing lag in the audit
remain supplemental. Do not call relative lag ground-truth response time.
Mandatory stopped acquisition is distinct from natural reversals, safety stops
and final goal stops. The combined D fill/escape/SEARCH/stronger-candidate
sequence must be evaluated separately in every holdout condition.

## Existing owners and bounded source work

Extend the existing analyzer's policy-input adapter with an explicit M4 route
that reconstructs recorded Gaussian/affine law using the existing numerical
evaluator. Preserve Q1/Q2 observation-only rejection and fixed study capacities.
Permit a separate bounded M4 extraction capacity40000 unique observations per
run; oversized/partial inputs remain unavailable, never silently truncated.
Reuse a single filtered union-of-aliases BagData read inside each M4 science
job and share it across labels/lifecycle/direction normalization where possible.
The inherited run_scenario child may itself invoke ordinary analysis/validation;
do not misrepresent this as only one total decode of a recorded bag.

A subordinate M4 helper in the existing `plotting_scripts` package may own the
finite contract/metric aggregation, as `q1_study.py` does for its closed study.
It must call existing bag reader, label/enclosure, objective/numerical reference,
and lifecycle owners; no parallel model, recorder or control graph. Thin docs
tools may orchestrate bounded child jobs, exclusive receipts and freeze checks.

Source clarification from live owner inspection, before edits: permit an
optional `minimum_residence_sec=12.0` argument on the shared label owner, with
finite nonnegative validation and unchanged default results. M4 may request0
solely to retain every raw spatial interval before censoring; it must mark and
enforce sustained>=12s separately before accepting a primary endpoint. Short
raw intervals are not positive sustained-residence evidence.

Use the existing scenario schema/runner and a new explicit M4 resource for all
16 slots. Extend strict selected cleanup inspection inside its current helpers
with legacy defaults preserved. The thin dispatcher supervises exactly one
existing one-case `run_scenario` CLI through M4A as a plain child. Run any native
ROS cleanup probe in a separately bounded process; unavailable inspection cannot
look empty/successful. Verify exact child summary/run ID/directory, inner
recorder session and complete final-zero/recording/lifecycle/safety/cleanup.
Behavioral failure with complete integrity remains an outcome; integrity failure
aborts later slots. No generic retries or replacement runs.

The live secondary template uses schema14 (primary13); generated M4 uses14 to
retain the existing verified-trap topology gate. Permit optional strict process
ownership tracking in the existing inner runner polling/cancellation loops:
bounded observed PID/start-time/SID receipts, inspection failures/capacity
reported explicitly, legacy defaults untouched. Outer cleanup checks these
observed nested sessions/identities as well as its own child; this is not a
claim about unobserved future descendants. No process-name signaling.
The strict selected scenario result also retains exact actual `launch_argv`
from the existing command owner and a receipt for captured resolved cost JSON.
The M4 recorded binding cross-checks that argv against recorder metadata and
the predeclared noisy JSON bytes, preserving the old Q1 path-binding contract.

Reuse verified primary `replay/m1a_labels_v1/geometry_1.json` (SHA256
`8f4f7fc53b67144317dd2e4640871c29ac5eb6c0d7e2cbc6ca3521a6c24788dd`)
and secondary `geometry_2.json` (SHA256
`f76ec43e796092d37a862c7290a0d3bfc49857194689ade0ff9561be09dcea36`)
only after exact sources/bounds and original recovery/numerical-owner receipt
chains verify. Original analyzer task-body hash binds the unchanged geometry
function, not the entire necessarily amended analyzer file. Noise and delay
topology receipts must separately bind their exact scenario disturbances.
The initially considered optional topology memoization was withdrawn before
preparation: its numerical-owner file edit conflicted with the original
geometry receipt's byte binding. The speculative source/tests and their passing
checks are retained at `builds/m4_pilot_runtime_v1/removed_cache_source_v1`.
Restore the exact numerical-owner bytes and use the ordinary uncached validator
within the same600s preparation and900s case caps. No equivalence waiver or
new geometry derivation is substituted for the original receipt chain.
Existing noise margin is3sigma (0.045 cost units), not a deterministic Gaussian
bound; delay hashing is not dynamic qualification. No topology numerics change.

Before dispatch validate exact16 expansion/matching, selector propagation,
immutable source/configuration/IDL and noisy temporary-config content checks,
strict cleanup and parent/child deadline/summary integrity, sealed holdouts,
actual filled/affine objective reference arithmetic, missing-law handling,
labels/censoring/no-positive outcomes and all acceptance denominators.
Use meaningful finite fixtures and existing regressions; actual Gazebo next
belongs to the approved development slots, not an extra acquisition chain.

## Finite execution, freeze and reporting

Preparation model/receipt work gets a single600s cap, with failed/partial
artifacts retained. Cases retain720s recording and900s inclusive case ceilings;
reserve30s wrapper cleanup and pass case_end-30s to M4A, which reserves its
existing60s cancellation inside that end. Establish suite_end before case1;
it remains15300s including pilot science/release/report work. Do not start a
case unless its full envelope and remaining declared science budget fit.

Science allocation within that ceiling: four120s block label jobs, eight45s
C/D reference jobs, four10s block summary jobs, and20s total freeze/report
receipt work (900s maximum total). These are caps, not promised runtimes.
This prospective reallocation precedes all new data: the retained21000-pose
fixture fell from116.09s to6.25s after the semantics-preserving lookup fix;
four fixtures alone nearly consumed the draft30s block allowance before any
bag decoding or objective normalization. Existing24-target observed-phase
diagnostic runtime24.32s supplies limited context for the45s reference cap,
not a guarantee for new filled/noisy inputs. Total900s science and15300s suite
ceilings, target counts, methods and no-retry rules are unchanged.
Each child uses min(its cap, remaining absolute suite budget). Timeouts retain
unavailable results; no renewed budgets or extra cases. Partial/missing source
integrity aborts; a cleanly terminated analysis timeout is a scientific
unavailability outcome and cannot certify the affected target.

Four visible development cases must have complete safe recording/cleanup and
unchanged source/configuration, attempted analysis with a complete outcome
ledger, and no unresolved Level A/source defect requiring correction before
the one-time holdout release. Scientific failure/unavailability is reported;
it does not by itself erase an outcome or create a new qualification gate.
If correction is needed, stop at that development boundary without adding
development slots. Freeze exact reviewed bytes, development results and all
twelve unstarted slots once; no tuning or replacements after release.

Write the final report with all16 slot statuses (including unstarted after
abort), exact primary/supplemental denominators, failures, evidence limitations,
time/path/jitter/lag/fallback, source/configuration receipts and Git state. An
honestly failed comparison can be completed evidence; source validation alone
is not research success. Update acceptance ledger/status/handoff and checkpoint
at source release, expensive empirical and final report boundaries. No commit
or push is newly authorized. Simulation checkout only; physical and V1 stay held.
