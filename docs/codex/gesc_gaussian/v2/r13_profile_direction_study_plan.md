# R13: retained profile and direction measurements

ADOPTED prospectively, 2026-09-11 UTC, after the completed
[R12 correction](r12_measurement_correction_handoff.md). This is an exposed
development study, not confirmation, a runtime method change or a new matrix.
All V12 files and unavailable/failed verdicts remain immutable.

Work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r13_profile_direction_study_v1/`.
Root owns one execution of each named job. Reuse the existing normalized inputs,
raw-cycle owner, reference numerical owner and angular-error/summary owners.
No bag read is planned. Preserve source/input hashes and exclusive partial outputs.

## A. Noisy raw profiles, 60 seconds inclusive

Read the two V12 noisy normalized caches and R11's retained event/state/guidance
projection. Restore observations with the existing q1_observation_from_row and
feed MovingRawEvidence with recorded first-filter state/stamp. Derive candidate
identity, center, recorded SEARCH boundaries and collection deadlines from R11;
read radius/centroid tolerance from the actual captured selection. Do not use a
normalizer context_id as search_epoch or invent a missing confirmation clock.

Use source samples at or after the recorded epoch start and first-publication
stamps strictly before cancellation. Evaluate once per retained cancellation;
do not search over clock shifts or reset choices to force parity. Save the actual
selected cycles/profiles and the existing owner's amplitude, disagreement,
counts, raw-cost guards and reason. Compare with all eight terminal snapshots.
The first publisher timestamp is not the supervisor's DDS receipt, and the last
evaluation timestamp/revocations are not fully recorded. Any mismatch therefore
remains a mismatch; it does not replace historical evidence or establish exact
callback replay. Fixed-cache development measurements may still be reported with
that limitation, without causal claims about the entire original attempt.

For the last 3, 6 and 9 eligible cycles, where available, report sample counts,
within-sector raw spread, centered mean-profile RMS amplitude, between-cycle
disagreement and maximum sector-trajectory distance. Retain geometry failures
and unavailable windows. For comparable windows, report the descriptive
cycle/sector signal-to-residual ratio:
`F = n*(n-1)*sum(mean_profile**2) / sum(centered_profile_residual**2)`.
Handle zero residual/flat signal explicitly. No p-value or calibrated confidence
claim follows from this statistic: sector medians, correlation and motion can
violate the usual model assumptions. Within-sector spread is also not a pure
noise estimate. This measures whether a future uncertainty-based method is
worth testing; it does not lower a runtime threshold or accept a new fill.

Decision: record replay agreement and the signal/noise/geometry measurements for
all eight attempts, or explicit unavailable evidence. Choose the next candidate
method only after independent noisy-flat, known-signal and changing-profile
controls are prospectively specified. Keep the existing negative-cost guards;
their passing values alone are not proof of a true extremum.

## B. D/noise reference component, 45 seconds inclusive

The historical D/noise reference process failed integrity. Produce one new,
separately named component product from its unchanged 24 target anchors using
the existing evaluate_direction_targets, observed-phase reference and raw-cost
model owners. Reuse the exact original model/binding/objective/normalized inputs;
do not repeat acquisition, labels or field geometry preparation.

Bind those original inputs and unchanged numerical-owner sources explicitly,
plus the current R12-validated import path. Do not call the old frozen-contract
verifier and suppress its intentional post-version source differences. Use the
existing finite_science_job with subreaper_group_v3 and the unchanged single-
process gate. A worker audit hook also rejects subprocess launches, including
imports, so a short child cannot hide between ownership polls. Parent and child
retain input/source checks and current source-validation receipt bindings.

Require complete 24-row numerical output, all original target identities, clean
termination, no subprocess attempt and unchanged hashes. Compare the new numerical
rows/summary with the old unqualified product, retaining any differences. The new
qualified component does not change the old V12 verdict or complete block 2.

## C. Same-confidence direction projection, 30 seconds inclusive

After B qualifies, use six fixed V12 inputs: C/D development, C/D nominal and
C/D noise. Reuse their original reference products, except the newly qualified
D/noise component. Preserve all 144 scheduled targets across these six inputs:
48 original development and 96 formerly-confirmation targets, now all exposed.
The four unstarted delay runs and remaining 48 original confirmation targets
remain unavailable in the original 16-slot ledger.

Compare the recorded output with a 100% current-cycle mean only where the
recorded blend weight is exactly 0.75. Recover that vector algebraically from
the recorded world output and instantaneous vector, verify recomposition and
the stored mean magnitude with an explicit numerical tolerance, and retain
roundoff limitations. The normalized cache does not contain the original mean
vector at weight zero; do not infer it from a magnitude. Preserve the recorded
fallback output elsewhere. Confidence, eligibility and availability do not change.
This is a weight-only diagnostic, not an unrestricted new estimator.

Use the existing angular-error and summary owners. Report each original target,
paired changes on the originally blended subset, per-run error quantiles and all
scheduled/exposed/eligible/usable denominators. Retain projection-unavailable
rows. It cannot solve D/noise's 7/12 averaging availability by construction.
Do not invent a three-cycle mean: that vector is not in these caches.

## Execution, interpretation and closure

The three inclusive ceilings total 135 seconds: A uses work55/kill5, B uses the
existing 45-second inclusive owner within a 55-second outer receipt allowance,
and C uses work25/kill5. Thus the total outer command allowance is 145 seconds,
excluding bounded preparation/review. No runtime or matrix is released.

Primary methodological context: [NIST least-squares residual uncertainty](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd431.htm)
explains separating a fitted mean from residual variability under model
assumptions. [Zengin and Fidan's RLS extremum-seeking study](https://arxiv.org/abs/2003.03891)
motivates investigating noise-aware estimation; its convergence claims do not
qualify this robot or these proposed diagnostics. No RLS implementation is
selected by this plan.

Close with exact measured outcomes, small independent reviews, validation,
handoff and checkpoint. A promising direction projection or profile statistic
requires a separate controlled method study and fresh integrated development
before another comparison. No physical/Pi/snapshot/V1, commit, push, old-version
resume or historical result rewrite belongs to R13.
