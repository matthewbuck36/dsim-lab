# R9: restrict motion attribution to the recorded readiness interval

ADOPTED2026-09-11UTC after the completed V11 command diagnosis. Simulation-only
private evaluator correction; no controller, recorder, interface, public topic,
scientific threshold or runtime behavior changes.

## Evidence and hypothesis

[V11 closure](m4_pilot_v11_handoff.md) retains C's original unavailable motion
measurement. The [separate diagnosis](validation/m4_v11_measurement_diagnosis.md)
reproduced12119 commands/12118 diagnostics and5197 positional mismatches. Every
one of312 consistent single-removal candidates is a zero command before readiness.
During readiness11493/11493 pairs match exactly; afterward314/314 also match.
No matched pair crosses a readiness boundary; source stamps are monotonic.
The exact extra startup row cannot be identified, and does not need to be.

The existing `_v10_motion_metrics` includes all recorded startup commands in its
global positional pairing, even though acquisition segments are readiness-scoped.
An irrelevant startup count difference therefore invalidates later exact evidence.
The correction is to restrict both streams to the same already recorded readiness
interval before the unchanged pairing checks. It does not delete a guessed row.

## Implementation and validation

Extend only the existing `evaluate_m4.py` motion projection owner, with focused
tests. Apply to its selected arrival-family/development routes; preserve the
non-arrival legacy owner. Reuse reader readiness flags and require usable recorded
readiness bounds. Keep nonempty/equal counts, exact six-vector equality, finite
commands, valid diagnostic output, inclusive0.5s bag-time bound and monotonic
diagnostic source stamps. Missing, unequal, invalid, out-of-order or mismatching
in-interval evidence remains unavailable. Do not guess across an interval boundary.
Retain full/pre/within/post counts and an explicit pairing scope for audit.

Preserve actual command zero durations, guidance, pose motion, segment completeness,
authority checks and safety/final-zero/cleanup owners. Excluding startup from this
scientific motion metric does not assert startup safety or override another verdict.

Before editing, preserve the existing owner and exact diff outside the repository.
Run one named focused motion bundle under90s work/100s inclusive maximum. Cover
the observed startup-only count difference, exact in-interval matches, unmatched
in-interval data, boundary-straddling records, missing readiness, invalid/nonfinite
commands, vector/time mismatch and source regression. Run existing arrival-motion
regressions; no broad source-test campaign or simulation is needed.

Then one separately named C component reassessment through the corrected existing
motion owner. Use the existing filtered reader for command, diagnostics, state,
guidance and selected pose plus automatic readiness, with the unchanged retained
intervention evidence. No full native, label, reference, behavior or report rerun.
Maximum60s inclusive (55s SIGINT+5s kill), preserving any failed result without retry.
Require source/input hashes before/after and exact reader/owner identity. Save all
new component outputs separately under
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r9_motion_readiness_v1/`.

## Completion boundary

Report focused source checks and the selected C reassessment separately. Preserve
all V11 outputs, twelve unstarted confirmations, latency censoring and the original
30% target as unavailable. This correction alone cannot release a new comparison;
the detector measurement question remains a separately planned method decision.
Save validation/handoff and a material checkpoint. No physical/Pi/snapshot/V1,
commit or push action is part of R9.
