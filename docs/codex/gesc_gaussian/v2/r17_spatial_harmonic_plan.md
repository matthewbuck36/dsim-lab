# R17: estimate the angular response at the current position

ADOPTED prospectively, 2026-09-11 UTC, after R16 material closure.
The previous goal turn made progress by completing independent R16 review and
preserving its measurements and handoff. No runtime is active. The next
incomplete criterion is a credible correction for motion-related direction
error, followed by continuous integrated behavior and a frozen comparison.

## Hypothesis and ownership

R16 reproduces nominal raw costs to floating precision, finds large noiseless
moving-fit errors, and small fixed-anchor errors. Its cached adequacy supplement
finds dense phase coverage and larger errors on supports with more travel.
These observations support a spatially changing angular model; they do not
prove its adequacy or identify a unique failure mechanism. R14 modeled x/y
interactions only for H1; R15 omitted all such interactions. R17 includes them
for H1–H3 and addresses variance with explicitly calibrated regularization.

Extend the existing unwired `filter_node/harmonic_gesc.py` with one separate
`fit_spatial_profile` entrypoint. Preserve R14/R15 entrypoints and runtime paths.
No new node, recorder, controller, reference owner or runtime selection is added.
Use the same causal Nx6 source arrays and existing support guards: three actual
cycles, maximum 12 seconds and 0.5 m excursion, real sector coverage, ordering,
finite data and unchanged source/context admission. Preserve all original
scheduled, eligible, unsupported and unexposed populations.

Let d=(position-anchor)/0.15 m, tau=(time-anchor_time)/3 s and h contain the
six cosine/sine H1–H3 columns. Fit

`y = Z gamma + H beta + P b`,

where `Z=[1,tau,dx,dy,dx^2,dx*dy,dy^2]` and
`P=[dx*H1c,...,dx*H3s,dy*H1c,...,dy*H3s]`. Minimize
`mean((y-prediction)^2) + lambda*sum(b^2)`; neither Z nor anchor beta is
penalized. Implement by an augmented least-squares system, not squared normal
equations. The three prospective lambda candidates are 1e-4, 1e-3 and 1e-2.
Their scale is tied to the explicit 0.15 m position normalization. Selection
uses generated calibration data below, before retained fits are examined.

For a supplied finite nonzero 2x6 output map M, the desired raw output is M beta.
Before regularization, check that `[0,M,0]` annihilates the full design's numerical
null space: SVD relative tolerance 1e-10 and relative output-null tolerance 1e-8.
An exactly confounded output stays unavailable even when ridge yields a number.
Nuisance-only null directions are allowed. Also retain rank, singular values
and unregularized output noise gain as diagnostics. This numerical estimability
test is distinct from statistical uncertainty or model adequacy.

Compute the regularized fit's actual coefficient influence from the augmented
pseudoinverse. Use its fitted-value leverage and residuals for the existing
one-second physical-time Bartlett HAC diagnostic, then propagate through M.
The raw-output score is `norm(M beta)/max(sqrt(max_eigenvalue(Cq)),1e-12)`.
Covariance does not bound shrinkage bias or model error. Reject nonfinite fits,
materially non-PSD covariance and leverage at one. Return anchor coefficients,
their covariance, raw output/covariance, score, support and rank diagnostics.
Compute the latest-cycle predictive gain as a diagnostic using the same model
on prior cycles, with held-out Z projection, but do not make it an admission
gate. R15 demonstrated that this held-out nuisance projection can remove power.
Instead, independent noise, nonlinear-null and late-change controls below must
test the proposed score-only admission explicitly; failure rejects this version.

## Independent controls and freeze

Reuse the independent R15 synthetic generator equations and cohort definitions,
with fresh deterministic seed base 260917000, and preserve every generated input.
No retained field model, reference error or trajectory outcome enters generation
or calibration. Default synthetic M selects H1c/H1s; focused tests also exercise
general maps with H2/H3 contributions and rotated/scaled output coordinates.

First generate 96 spatially varying positive calibration episodes: amplitudes
0.0075/0.015/0.03, straight/curved/accelerated/S-curve trajectories,
eight seeds per combination. The S-curve uses u=0.003*t and v=0.012*sin(0.55*t),
then the same independent heading rotation. A pre-execution design review
replaced the initially proposed near-phase-locked positive with this S-curve:
near-confounding has no justified positive availability assumption. Existing
exact/near-confounding stress populations and gates remain unchanged; no fit or
generated numerical outcome motivated this correction.
Add independent x/y interactions for all six
harmonics to the existing signal generator, with coefficient norm at each
spatial axis equal to 0.5 times its base H1 amplitude. Evaluate at the existing
two causal looks, 9 and 12 seconds; the true anchor coefficients include the
known spatial offset at that look. For each lambda minimize mean absolute
direction error across all looks, assigning 180 degrees to unavailable fits.
Select the smallest loss; exact ties within 1e-9 degrees prefer larger lambda.
Freeze that one lambda before all subsequent score calibration and evaluation.

Reuse the R15 null-score calibration population: four noise families with 199
independent episodes each, maximum score over two looks per episode, then the
maximum over all families as cutoff. A fit must be supported and output
identifiable; the latest-cycle gain does not filter this population. This
defines a limited empirical rule for the stated null generators, not a universal
confidence interval. Evaluate the unchanged R15 populations on fresh seeds:
512 independent null episodes, 96 stable positives, 64 hard/identifiability
stress cases, 64 quadratic spatial nulls, 64 smooth-change gray cases and 32
late loss/reversal episodes. Add 96 independent spatially varying positives
with the same factorial design as calibration and new seeds, plus 64 quadratic
spatially varying angular profiles as explicitly out-of-model gray controls.

R17's prospective decision limits are at most 5/512 ordinary null false accepts
and at most 2/128 in each noise family,
at most 2/32 hard-null accepts, exact-confounding controls unavailable,
at most 1/64 quadratic-null accepts, at least 58/64 stronger stable positives
detected, and accepted direction median <=15 degrees/P90 <=30 degrees.
For the new moving-positive population require the same 58/64 stronger detections
and error limits. These retain R15's stricter synthetic accuracy limits; the
total-null and quadratic-null limits are prospectively stricter in R17.
Mature late-change false accepts must remain <=2/16; early
transition looks and quadratic-angular gray controls are descriptive. Preserve
all failures without retuning lambda, score, labels or thresholds.

## Retained development comparison

After the source checks and the one controls job, perform one fixed retained
development comparison even if controls reject the candidate; this is diagnosis,
not a route to override rejection. Reuse the six R15/R16 cached inputs, 144
scheduled targets, 46 eligible and the same 40 supported target matrices, plus
eight verification supports. For targets evaluate recorded raw cost and all
three cached R16 model controls with the frozen selected lambda. Reuse each
original exact harmonic map M and known augmented contribution. Map raw
covariance through the actual M; keep reference floating error separate.
No new model evaluation, bag read, quadrature, geometry solve or recorded
reference qualification is needed. Verification uses the H1c/H1s selector
for raw angular information; original non-signal guards and historical
diagnostic mismatches remain unchanged.

The synthetic cutoff is calibrated with the H1c/H1s selector. Applying it to
the retained observed-phase maps is a prospective development projection; it
does not prove the same null false-acceptance rate for every possible map or
real-data noise law. Retained numerical error and availability must be measured
directly, and any later runtime qualification must address that scope.

Report all-supported and frozen-score-admitted direction errors/availability,
paired R15 changes, support and estimability failures, output covariance,
predictive diagnostics and all eight verification projections. Original per-run
direction gates remain median <=30/P90 <=60 degrees and >=80% usable averaging
among eligible targets. Counterfactual admission remains descriptive; no noise
calibration claim transfers to model-generated controls. A projected verification
pass is not a recorded fill, escape or arrival. No result qualifies runtime by
itself, and no R17 result rewrites V12 or earlier candidate failures.

## Finite execution and release boundary

Work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r17_spatial_harmonic_v1/`.

Three root-owned sequential jobs: focused source/regression bundle <=60s;
synthetic study <=240s inclusive (235s SIGINT plus 5s kill, internal 210s,
at most 5,000 public fit calls); cached retained study <=120s inclusive
(115s plus 5s, internal 105s, at most 192 fits). Use BLAS threads1 and exclusive
outputs, source/input hash pins, exact argv and terminal receipts. Preserve all
partials and independently review cached arithmetic without refitting. Archive
the reviewed material boundary using existing phase tools.

No production runtime wiring, Gazebo, new matrix, hardware/Pi/snapshot/V1, commit
or push is released. If the method is promising, prospectively plan a bounded
visible integrated case. If rejected, use the measurements to choose a collection
or method correction; do not merely relax acceptance gates. The full goal remains
faster reliable detection and reliable direction during continuous source seeking.

Method context: local time-varying harmonic models and least-squares ESC are
documented in the primary papers linked below, but R17's spatial model, penalty,
HAC score and finite tests are project-specific design choices; no theorem from
those papers is asserted for this implementation.

- https://arxiv.org/abs/2202.04150
- https://arxiv.org/abs/2107.01176
