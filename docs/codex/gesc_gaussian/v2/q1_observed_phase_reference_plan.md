# Observed-phase direction diagnostic — 2026-09-09 UTC

Status: ACTIVE SOURCE/PREFLIGHT under the approved simulation-only V2 goal.
Read `plan.md`, `status.md`, `q1_discovery_direction_handoff.md`, and
`validation/q1_discovery_direction_result.md` first. This is a new diagnostic,
not a reopening of Q1 qualification or the closed constant-rate diagnostic.

## Evidence and selected question

The preceding diagnostic completed all24 targets, but20 references were
inapplicable under their unchanged constant-rate CV<=0.10 assumption. Recorded
source cadence and encoder rotation are intact; actual base turning accounts
for variable world rate. The exact first-diagnostic confidence audit finds
both magnitude and direction changes. These findings justify measuring the
reference with the observed timing before any runtime confidence adjustment.

The closed source/evidence checkpoint is
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/q1_discovery_direction_closed_v1/manifest.json`,
SHA256 `6eb47b32197fa21c5800a49332a47f42783d240203468e2f94e5a2b3f7b17e4c`:
219 files,917306-byte verified archive,213 retained artifact hashes. The old
analyzer hash is `738d9a02e0f35d9a0dfacfe7a617a5a459c489d84c2657b7dd032d21e24e9e45`;
the old numerical owner is
`614332ebbaa0d654b11b8f0c7304bf980ea3e7d693172e471dc999d703f51aed`.

Version: `q1-observed-phase-direction-diagnostic-v1`. Exclusive external root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_observed_phase_direction_diagnostic_v1/`.
Use exactly the original24 discovery targets, seeds26090911/26090912 and
numbers1–12. Their manifest SHA256 remains
`b5d84cf2bb4f8900a940389ec16e5aa2608cbd76222907cdfeecb9a64cc4b1aa`.
Preserve every missing, weak or invalid slot; no replacement target or later
publication. Confirmation remains sealed, qualification NOT_EVALUATED, and M4
unreleased regardless of the result. No simulation acquisition is included.

## Numerical method selected before evaluation

Adopt the derivation in `q1_observed_phase_reference_design.md`: fixed anchor
base position and the complete recorded augmented objective, evaluated under
a periodic repetition of the latest complete observed source-time world-phase
waveform. Preserve every phase knot with linear phase interpolation and exact
clipped cycle boundaries. The periodic washout has alpha=1/s and d=0.18m.

Compute `q_ref = -2/(d*T) integral (u-z)[cos(theta),sin(theta)] dt` using the
exact periodic adjoint for the represented piecewise-linear phase. This retains
time weighting, sign, geometry, and washout lag. It is an ideal local periodic
GESC response, not a spatial gradient or a prediction of a new moving trajectory.
Translation, phase interpolation and filter transients remain model limitations.

Keep the old `reference_cycle`, stationary reference, CV0.10 and default48
qualification behavior unchanged. Share cycle extraction through an internal
helper if needed. The new method models rate variation explicitly; its CV is
descriptive. All source-time/gap/context/objective/phase-reversal/readiness and
twelve-sector/two-observation requirements still apply.

Use two adaptive quadrature partitions split at every phase-time knot and
existing source-bearing/angular breakpoints mapped to time. Cache actual
objective evaluations, with at most25,000 distinct angles per target. Do not
interpolate costs from the recorded34ms samples. Require normalized component
error estimates<=1e-6, including pass errors and disagreement; propagate
`E_q=hypot(E_Cx,E_Cy)/d` and preserve informative floor `max(1e-6,20*E_q)`.
Record periodic closure, DC residual and floating-point contributions. These
are numerical estimates, not rigorous model-error certificates. Reject
nonfinite values, warnings or exhausted budgets and retain partial receipts.

## Predeclared algebraic sensitivity

In addition to the primary actual-output and aligned-instantaneous comparisons,
explicitly select `q_latent=.5*q_instant_world+.5*q_recorded_rolling_world` at
the same24 anchors. The weight is the previously selected runtime weight; no
fit, sweep or data-dependent subset is allowed. Use the actual one-revolution
mean from the original first diagnostic, not the three-cycle confidence mean.

Bind `diagnostics/cycle_confidence_v1/result.json` under the prior diagnostic,
SHA256 `4a2c39e84c1c6ada74b5b4cc193af83f928b9f49e8ea12be07f4e77a32293edf`,
and its manifest SHA256
`58581ea042cd37e91eefed15bb349fe15cb967d0e16387a8a442225192227b6f`.
Verify exact run, target, source, observation hash, diagnostic sequence,
publication and bag-receipt identity against frozen inputs before evaluating
any model. Require the mean to be full, covered and finite; retain weak or
disagreement confidence as descriptive. Missing/invalid mean or latent norm
<=1e-6 gives an unavailable comparison. At actually blended anchors require
componentwise agreement with recorded output within1e-12.

Report primary and latent results separately, with explicit paired counts and
every improvement/degradation. The latent vector is hypothetical algebra on
the recorded trajectory, not an observed output or a new policy/trajectory.
Favorable latent error cannot qualify a relaxed runtime gate automatically.

## Ownership and immutable source lineage

Extend existing `v2_direction_reference.py`, the existing
`evaluate_q1_direction_references` owner, and the existing
`tools/q1_discovery_direction.py` workflow with an explicit new version selector.
Do not create a parallel analyzer, recorder, numerical model or runtime owner.

The new contract binds the original Q1 contract/closure/targets, the preceding
diagnostic contract/closure, the completed checkpoint, and confidence audit.
Preserve snapshots of every changed previously frozen owner. Relative to the
preceding552-source contract, allow exactly the numerical owner, analyzer and
diagnostic workflow to change. Keep every other old source path/hash exact.
New receipts are limited to this plan, its saved derivation, and the new
numerical/diagnostic tests. Freeze the exact allowed set before dispatch.
Verify both old source lineage and current files; never falsify old hashes or
waive freshness in `_q1_contract` or the old diagnostic. Use the existing
recorded-run verifier with an explicitly verified effective source contract.

Validate identities before following input traces, and recheck all source,
input, supplement and closure receipts before output, before each run's first
model evaluation, and after the job. Do not follow confirmation bag receipts.

## Acceptance and bounded execution

Before any new recorded-data model work, independently verify DC and offset
invariance, signed uniform first-harmonic agreement with old Hc, uniform higher
harmonics, Hd's continuous limit, variable-rate/dwell agreement with a direct
periodic washout ODE, yaw covariance, cyclic time origin, tiny segments, closure,
malformed inputs, warnings, numerical budget and weak-reference handling.
Verify exact24 identity and supplement joins, unauthorized source changes,
no confirmation access, unchanged default48/old diagnostic behavior, and
exclusive/partial outputs. Run relevant focused old numerical/reference tests.

Record exact commands/outcomes, inspect the diff, freeze sources and inputs,
then checkpoint. Only after these checks may the single24-target numerical
job run under external timeout300s. No automatic retry or continuation after
timeout. Preserve per-anchor receipts and close complete, unavailable or
incomplete honestly. No runtime tuning, new detector metric, label change,
confirmation opening or pilot release is part of this amendment. A subsequent
bounded development decision must use these results and preserve old failures.
