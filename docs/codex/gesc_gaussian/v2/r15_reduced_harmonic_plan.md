# R15: reduced harmonic model with correlated-noise diagnostics

ADOPTED prospectively, 2026-09-11 UTC. R14 is COMPLETE with a REJECTED
candidate; its source archive and fixed results remain unchanged. The previous
goal turn made progress by completing independent review and material closure.
The next incomplete criterion is a usable moving direction method, not another
matrix or a retrospective change to V12/R14 acceptance.

## Hypothesis and implementation

Extend the existing unwired `filter_node/harmonic_gesc.py` owner with a separate
`fit_reduced_profile` entrypoint. Preserve R14 `fit_profile` behavior. Fit
`raw = Z gamma + H beta`, with world-phase cos/sin harmonics1..3. Compare two
prospectively named variants on identical generated inputs: `linear_spatial`
uses the same DC/time/x/y Z basis; `quadratic_spatial` also includes scaled
x^2, x*y and y^2. The exact phase/curvature null proposed in independent review
is analytically confounded for the linear model; the quadratic variant must
reject that rank loss. This pre-measurement design amendment addresses a known
structural ambiguity, not an observed-result or threshold correction. Remove position-times-harmonic interactions as an explicit
locally constant angular-profile approximation. This may reduce variance and
confounding, but omits spatially changing angular response: independent mixed
controls and retained current-position error must test that bias.

Reuse all R14 raw-support requirements: three actual ordered cycles,12s maximum,
0.5m target excursion,12 sectors with two samples per cycle,0.5s source gaps,
finite monotonic phase and source/context admission. Remove only the arbitrary
minimum-information-fraction acceptance screen. Retain exact full harmonic
rank and finite/leverage guards; report information fraction as a diagnostic.
Keep every full valid fit even if a prediction fold is unavailable, with explicit
null fold result and failed latest-prediction admission.

Let F be the residualized harmonic coefficient influence and e_i the full-fit
residual, h_i full-model leverage. Form a_i=F_i e_i/(1-h_i). The descriptive
covariance is `C=sum_ij max(0,1-|t_i-t_j|/1s) a_i a_j'`. The one-second time
Bartlett kernel is fixed before measurements and accommodates nonuniform stamps.
This is a positive-semidefinite correlated-noise diagnostic with an HC3 leverage
adjustment, not an exact finite-sample confidence interval or a bound on omitted
model/pose/phase error. Reject material negative covariance eigenvalues/nonfinite
calculations. Numerical roundoff may be symmetrized; denominator floor1e-12 in
raw-cost coefficient units is explicit, and zero signal has zero score.

Signal score is `norm(beta[:2])/max(sqrt(lambda_max(C[:2,:2])),1e-12)`.
Keep all three held-out-cycle predictive gains, but require positive gain only
on the latest cycle, trained on the preceding two. This tests present predictive
benefit separately from pooled noise evidence. A missing/failed latest fold
rejects admission. No score cutoff is chosen from positive or retained errors. Retain variant-specific
verdicts; a failed variant cannot borrow another variant's accepted subset.

Extend the existing observed-phase reference owner with an exact linear map
from six harmonic coefficients to the represented stationary periodic GESC
output. Reuse its waveform/periodic-adjoint owners and analytically integrate
harmonics on each linear-phase segment. Check the map independently against
constant signed-rate washout and numerical quadrature. Known frozen augmented
terms are evaluated once through the existing objective/reference owner with
raw=0. Then `q=w_raw M beta+q_known`, `Cq=w_raw^2 M C M'`. No field truth enters
this estimator. Keep raw-signal admission separate from known fill contributions.
The output covariance is descriptive; do not transfer synthetic rank guarantees
to arbitrary retained waveforms or a real robot.

## Independent controls and prospective decision

Reuse the independently written R14 generator equations and populations with
new disjoint fixed seed blocks:199 calibration and128 evaluation episodes for
each IID/AR1rho0.6/phase-heteroskedastic/rare-burst law;96 stable signals at
amplitudes0.0075/0.015/0.030, half with higher harmonics and spatial interactions;
64 hard reversal/loss/exact/near phase-pose confounding controls. Add64 quadratic
spatial null controls and64 smooth direction-change gray controls, with equations
and seeds frozen before execution. Add32 late reversal/loss diagnostics: change at7.5/10.5s, four noise
laws and two independent phases. Total1628 generated episodes, evaluated by both variants on identical inputs. Preserve all generated
samples and every9s/12s look, including unavailable/rejected outcomes.

Each variant has its own frozen null-calibrated cutoff; variants are development
comparisons, not untouched confirmation. Calibration score is each complete null episode's maximum score over looks
that pass support/rank and latest gain>0; unavailable maximum stays null. Cutoff
is the maximum finite calibration score across four families, or unavailable
if none exists. New admission requires score strictly above cutoff and positive
latest gain. Equivalent worst-family rank p<=0.005 at these two fixed looks is
conditional on the declared exchangeable episode laws; no universal guarantee.

Candidate criteria apply independently to each variant: at most2 false accepts per128 evaluation null family;
at least90% stronger stable signals (amplitude>=0.015) accepted; accepted stable
coefficient-direction median<=15/P90<=30 degrees; every exact-confounded design
unavailable; at most2 hard-changing accepts across reversal/loss. Added quadratic
nulls require at most2/64 accepts. Smooth changes are gray and report target-time
error and acceptance without being silently counted as positives or negatives.
For late changes, looks before the change are valid pre-change controls; looks
less than one complete3s sensor cycle after the change are transient gray.
At least3s after change, require at most2 accepted looks among the16 applicable
late-change cases. This is an explicit one-cycle response boundary, not an
instantaneous endpoint-stability guarantee.
Do not tune the candidate after seeing these fixed results. Failure permits the
retained descriptive job below, but blocks runtime release.

## Retained measurements and budgets

Reuse R14/R13 six normalized inputs and original references,144 scheduled targets,
46 original eligible targets, and all eight original noisy verification supports.
Reuse existing causal extraction and frozen augmentation. Keep all original
identities, eligibility, missing targets, minima, geometry and replay mismatches.
Report variant-specific all-supported and admitted direction errors, paired recorded fallback,
new availability, coefficient/output covariance and explicit rejection reasons.
Existing direction criteria median30/P9060 degrees and80% availability remain.
The eight verification projections are raw-information development diagnostics,
not newly accepted fills or proof of a local minimum.

Root owns exactly one focused source bundle (60s inclusive), one synthetic job
(150s inclusive,145s INT+5s kill), and one retained job (150s inclusive,145+5).
Set BLAS threads1. Exclusive preparation binds source/config/input identities;
retain failures and partial products. No new bag read, field model replay,
simulation, runtime wiring or matrix in R15. Independent cached reviews follow
without repeating fits. Promising results still require a separately planned
bounded visible integrated case and frozen comparison before full completion.

Work root: `/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r15_reduced_harmonic_v1/`.
No hardware/Pi/snapshot/V1, commit, push or historical-result rewrite.

Methodological context: [Newey and West's original covariance paper](https://www.ssc.wisc.edu/~bhansen/718/NeweyWest1987.pdf)
motivates a positive-semidefinite Bartlett construction. The fixed physical-time
bandwidth, HC3 adjustment, score and prediction guard are this prospective
project design; its asymptotic theory does not certify these short robot windows.

Pre-execution review amendment: two spatial variants were declared before any
R15 test/study. Generate controls and known objective contributions once, fit both
variants, preserve each full population and verdict. Existing150s study caps stay.
