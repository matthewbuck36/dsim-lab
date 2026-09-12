# R14: motion-aware harmonic estimation and independent controls

ADOPTED prospectively, 2026-09-11 UTC. R13 is complete and remains immutable.
This is an exposed component-development study, not a runtime release or a new
comparison. The previous goal turn made progress: three measured jobs established
that longer pooling fails geometry and blend weight alone is insufficient.

## Candidate and owners

Add one pure mathematical owner under `filter_node/harmonic_gesc.py`, initially
unwired to ROS/runtime. Reuse existing source observations, phase/cycle admission,
augmented-objective composition, observed-phase GESC operator and direction-error
owners. No new nodes, topics, recorder, launch graph or reference field model.

Fit original raw samples from three complete cycles with ordinary least squares:

`raw = Z gamma + H beta + P eta + residual`,

where `Z=[1, (t-t*)/3s, (x-x*)/0.15m, (y-y*)/0.15m]`, H contains cosine/sine
pairs for harmonics1,2,3 of actual WORLD sensor phase, and P contains first-
harmonic interactions with each scaled position offset. The center/time are the
current target (or recorded verification center/end), so H beta is the fitted
angular profile there. Three harmonics represent non-sinusoidal sensor response;
first-harmonic position interactions represent a changing local directional
component. This is a bounded local approximation, not a global field model.

SVD removes only linearly dependent nuisance directions at relative1e-10.
It must not remove a supported nuisance column to create apparent angular
information. Residualize H against [Z,P]; require all six harmonic directions
identifiable, with minimum eigenvalue of H_residual' H_residual divided by sample
count at least0.05 (one tenth of uniform-phase information0.5). Keep unavailable
rank/conditioning outcomes. Maximum support12s and maximum excursion from the
target0.5m; each cycle retains12 sectors with at least2 real samples per sector.
Actual within-cycle phase span allows one observed phase step at each clipped
boundary; raw endpoints are never interpolated or duplicated. Source gaps stay
at most0.5s and phase must remain monotonic without an ambiguous pi step.
No synthetic interpolation of raw costs or tuning after seeing these results.

For each held-out cycle, fit the other two. Independently remove Z from held-out
raw values and from the predicted angular component H beta + P eta, then compute
normalized squared-error reduction; the score T is the minimum of the three
held-out gains. A positive score therefore requires predictive benefit on every
cycle. Training folds require full residual harmonic rank; the0.05 information
screen applies to the full three-cycle target fit, while held-out predictive gain
measures each fold's extrapolation error. Save all gains, ranks, residuals and coefficients. HC3 first-harmonic
coefficient uncertainty is a descriptive proxy only; directional usability also
requires coefficient norm at least3 times its trace-standard-deviation proxy.
Do not call that proxy a calibrated confidence region under correlated noise.

## Independent synthetic controls

One finite job generates12s episodes at20Hz, three-second continuous sensor
revolutions, and only the declared9s/12s looks using the latest three cycles.
Motion varies slowly across straight, curved and stationary-base designs, with
independent fixed phase/heading/noise draws. The sensor keeps rotating in every
case. Seeds and the complete generating equations are saved before execution.

Use199 calibration and128 separate evaluation episodes for each of four null
noise laws: IID Gaussian, AR1 coefficient0.6, phase-dependent variance and rare
bursts. Noise nominal standard deviation0.015; flat negative-baseline controls
include linear position/time trends, independent of angular phase. Retain each
episode's maximum score over both looks, including unavailable decisions.
The cutoff is the largest null calibration maximum across all four families,
floored at zero so accepted fits always predict positive held-out benefit.
Equivalent family rank p is `(1 + count(null_max >= T))/200`; require worst-
family p<=0.005. This rule covers the two fixed looks under the declared
exchangeable episode laws. It does not certify the real retained trajectories,
unknown noise, different designs, or unlimited retries. At most eight attempts
would give a0.04 union bound under those laws, not a general robot guarantee.

Add96 stable known harmonic controls spanning amplitudes0.0075,0.015,0.030;
half include second/third harmonics and position-dependent first-harmonic terms.
Add64 stress controls: hard phase/profile reversal, loss of signal, and exact/
near phase-position collinearity. Reversal/loss are invalid changing-profile
controls; collinearity must be unavailable. Mild amplitude change, if included,
is explicitly gray, never silently counted as a negative. Truth generation is
independent of the fit implementation. Total1468 episodes. Save exact per-family
false accepts, stable detections, directional errors and unavailable counts.
No claim of a1% empirical false-acceptance bound follows from128 checks.

Prospective candidate decision: no more than2 false accepts per128 null family;
at least90% detection for amplitude>=0.015 stable controls; accepted first-
harmonic coefficient directions median<=15 degrees and P90<=30 degrees;
all exact-confounded designs unavailable and at most2 hard-changing accepts.
Preserve the result if any criterion fails; no threshold retuning in R14.

## Retained applicability and fair GESC comparison

One second bounded job uses the same six normalized inputs and qualified
references as R13 (144 scheduled targets, all exposed). Extract the latest three
complete causal world revolutions at the original anchor, honoring source gaps,
readiness, context/objective boundaries and first-publication availability.
Use the actual retained anchor; some anchors are up to50ms after nominal target
time. Normalizer context IDs are not SEARCH epochs. No exact DDS replay claim.
Keep all missing/short/rank-failed windows explicit.

Fit RAW cost, then reuse `augmented_objective` with the anchor's complete frozen
weights, Gaussians and affine terms. This adds known controller contributions to
the fitted raw profile without fitting changing historical augmented costs.
Pass that fitted angular objective through existing `observed_phase_reference`
using the original one-cycle phase waveform, with no ground-truth field call.
The reference remains stationary-position periodic GESC under observed phase,
including washout sign/phase and higher-harmonic effects at variable rate.
Do not substitute a direct spatial gradient or constant-rate approximation.

Report per-run errors/availability for all originally eligible anchors, new
usable subset and paired old/new outputs. Also report the estimate with recorded
fallback where unavailable, without claiming the fallback improves confidence.
Map every valid supported fit at an originally eligible anchor even when the
score/proxy rejects it, and retain those errors as an explicitly unscreened
descriptive summary. This separates a poor estimate from a restrictive usability
gate; it does not change the candidate decision or eligible population.
New-method usability requires the frozen score cutoff, directional proxy and
qualified informative fitted GESC response. Existing direction thresholds remain
median30/P9060 degrees and80% averaging availability among original eligibility.

For all eight R13 noisy verification supports, reuse their selected three cycles
and original normalized sample stamps, fit raw cost at the recorded center, and
report the score. Retain R13 geometry/minima/negative-cost guards unchanged.
The score is only a replacement-information-test development projection, not a
new accepted fill or proof of a true minimum. Preserve original replay mismatches.

## Validation, budgets and next action

Before execution, root reviews held source and controls; focused deterministic
checks cover exact harmonic recovery, coordinate/time offset invariance, cost
sign, rank/confounding rejection and malformed/missing support. Limit these to
45s inclusive. Synthetic job120s inclusive (115+5); retained job95s inclusive
(90+5). Set BLAS threads1 for small-matrix work. Root owns one execution of each;
all source/seed/input identities and exclusive partial outputs are retained.
No new bag read, field model replay, geometry preparation, simulation or matrix.

A failed synthetic criterion does not prohibit the declared retained descriptive
job, but prevents runtime release. A promising component still needs a separately
planned runtime integration and bounded visible development case before another
16-run comparison. Full research completion remains unproven.

Primary methodological context: [NIST model-adequacy checks](https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd446.htm)
distinguish fitted residual variation from independent noise information.
[Danielson, Bortoff and Chakrabarty](https://arxiv.org/abs/2107.01176) motivate
using estimator error in extremum-seeking decisions; their model and theorem do
not qualify this harmonic prototype. The chosen equations are this project's
prospective design, not an attribution of those equations to either source.

Work root: `/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r14_harmonic_method_v1/`.
No physical/Pi/snapshot/V1, commit, push or historical-result rewrite is authorized.
