# R20: verify spatial restoring response during continuous collection

ADOPTED prospectively on 2026-09-11 UTC, after reviewed R19 closure and before
R20 implementation, generated controls, fits or field-model evaluations.
The preceding turn made progress with R18/R19 measurements. No runtime is live;
the full detector/direction/source-seeking goal remains incomplete.

## Verification functional and scope

Angular amplitude does not establish a minimum. A phase-average cost well is
also not automatically the potential followed by the selected directional light
sensor's GESC. R20 instead tests **local attraction of the raw stationary-GESC
direction field**, preserving the backbone's actual demodulation sign and keeping
existing raw rotation-minimum ranking separate. This is not a global-minimum
certificate, a general scalar Hessian test, or a closed-loop unicycle proof.
Flat, constant-direction slope, saddle and repelling fields must fail.

At fixed base position define Q as the selected continuous stationary GESC mean
at20rpm, washout alpha1 and sensor radius0.18m. Reuse the existing reference
owner's transfer T=i*omega/(alpha+i*omega), omega=2*pi/3. Its H1 map is
`M1 = -[[Re(T),Im(T)],[-Im(T),Re(T)]]/0.18`; H2/H3 columns are zero for this
constant-rate functional. Do not negate it again. This new verification
functional does not rewrite existing observed-phase direction references.

## Numerical owner and decision

Extend `filter_node/harmonic_gesc.py` with a separate pure affine-field entrypoint,
reusing its spatial design and SVD solve with zero regularization. Preserve all
R14/R15/R17 APIs and runtime selection. Inputs are synchronized rows of source
time, base XY, actual world sensor phase and raw cost. Fit the existing25-column
model: spatial DC quadratic plus linear time nuisance, H1–H3 anchor coefficients,
and XY interactions for every harmonic, normalized by ell=0.15m.

For beta0 and its6x2 normalized spatial coefficients G, estimate
`q0=M*beta0`, `B=M*G/ell`, so `Q(c+d) = q0+B*d`. Require all six q/B functionals
to annihilate the unregularized numerical null space (relative SVD1e-10,
relative output-null1e-8). Nuisance-only rank loss is allowed; ridge cannot
manufacture attraction evidence. Preserve full6x6 q/B cross-covariance using
the actual centered-data influence, HC3 leverage adjustment and existing
one-second physical-time Bartlett HAC calculation.

Fit support: finite strictly increasing times, finite XY/cost, monotone unwrapped
world phase, gaps<=0.1s, at least3 actual world rotations, at least4 observations
in each of12 phase sectors, at most1024 samples/30s and0.25m anchor excursion.
Return unavailable for unsupported or nonestimable inputs. Do not apply old
exactly-three-cycle IDs to this longer collection. Report design rank, singular
values, residual and uncertainty without claiming a complete model-error bound.

Extend the existing pure basin-estimation owner with the attraction decision
and observed spatial-support calculation. For calibrated multiplier k, let
`bq=k*sqrt(maxeig(Cq))`, `bB=k*sqrt(maxeig(CvecB))` (Frobenius bounds spectral
error), and `mu=-maxeig((B+B.T)/2)-bB`. Require mu>0 and an estimated zero
`dhat=-solve(B,q0)` whose uncertainty radius
`(bq+bB*norm(dhat))/mu` lies strictly within the actually observed XY convex
hull. Never use clipped Hessians or floored basin depths as evidence.

The full window and its two chronological halves use the same frozen anchor/map.
The halves need estimable q/B but need not individually enclose the candidate.
Reject a statistically inconsistent half-to-half field using their covariance
sum and a separately frozen calibration cutoff. Retain both fits and all
cross-covariances; zero H1 at the candidate is allowed when B restores toward it.
HAC intervals remain empirical noise diagnostics, excluding unmodeled spatial
variation and harmonic truncation. Local-model adequacy must also be checked
on the actual selected field component below.

## Continuous collection component

Add opt-in pure reference/command helpers to the existing
`supervisor_node/centered_verification.py`, without wiring a runtime mode yet.
For u=2*pi*t/28, use r=0.14-0.025*cos(2u)m and
`p=c+r*[cos(theta0+u),sin(theta0+u)]`. This prospectively increases the proposed
small orbit to0.115–0.165m to obtain spatial restoring information under the
measured0.015V noise. Freeze theta0 independently of sensor phase.
Use analytic position, velocity and signed yaw-rate feedforward through the
existing .5/5 Directional_Controller and its .1m/s/.5rad/s saturation owner.
Preserve the current default circle and all old8/12/20s contracts.

First run bounded midpoint-unicycle component tracking at5ms integration and
30Hz recorded sampling for28s, with ideal initial tangent state and two declared
perturbations (+/-0.02m lateral,+/-0.25rad heading). Require finite bounded
commands, no sustained stopped acquisition, maximum tracking error<=0.05m,
and final error<=0.02m. Report actual spatial/phase coverage. This is component
kinematics, not Gazebo or validated approach/entry. Actual world sensor phase
is declared rotor phase plus the simulated base yaw, never rotor phase alone.

## Independent controls and freeze

Use the ideal feasible trajectory with independent orientation/rotor phase and
the same30Hz/28s sampling. Generate raw costs from exactly the declared affine
angular field plus independent DC/time nuisance, with H2/H3 angular structure.
Map prescribed q/B to H1 through the invertible selected M1. Add the existing
four noise families: Gaussian, AR1rho0.6, phase heteroscedastic and rare bursts,
each normalized to sigma0.015V. Reuse R15 noise equations, with fresh seed base
260920000 and disjoint cohort offsets. Preserve every generated input.

Calibration:4 noise families x199 episodes. Cover flat, slope, attracting,
saddle and repelling affine fields with random orientation and interior zeros
where applicable. Freeze k as the maximum full/half joint standardized q/B
estimation error over these exact-model episodes. Freeze the half-consistency
cutoff as the maximum standardized half-difference over the same static inputs.
Singular covariance or unavailable fits cannot silently leave calibration;
retain them and fail calibration if a finite required cutoff cannot be formed.

Then evaluate512 negatives (4 noise x4 types x32 seeds),192 attracting positives
(restoring gains0.5/1/2 x isotropic/3:1 anisotropic x4 noise x8 seeds),32 exact
phase-position confounding controls,64 phase-only controls, and64 half-window
loss/reversal controls. Freeze nuisance coefficient scales and all draw order
in the saved generator configuration before generation. Positive zeros lie
within0.03m of the frozen center; nonzero slope offsets and arbitrary field
orientation must not use the reference location at runtime.

Decision limits: <=5/512 negative accepts and<=2/128 per noise family and field
type; >=116/128 positives with restoring gain>=1 accepted; accepted zero-location
median<=0.02m/P90<=0.04m; all exact-confounded controls unavailable; <=1/64
phase-only accepts and<=2/64 loss/reversal accepts. Weaker positives are reported
separately. Failure rejects this fixed candidate without retuning the cutoffs.

## Selected-field component and boundary

After source/kinematic checks and the one controls job, evaluate the same eight
retained noisy candidate centers using the resolved two-light model and the
new28s component path. Reuse R16 model construction; use a fresh explicitly
declared additive Gaussian draw order/seed. No bags or old references are reused
as new-phase truth. Even if controls fail, this component remains diagnosis.
Keep true models/reference calculations evaluator-only and preserve all eight
centers. Report q/B estimates, uncertainty, raw-attraction decisions and
independent stationary-field comparison, with numerical-reference limitations.
Freeze the exact component sample count, truth stencil/quadrature and evaluation
cap in a saved preparation appendix before any model call. No broad field grid.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r20_local_attraction_v1/`.
Sequential root-owned jobs: focused/kinematic bundle<=90s; controls<=240s and
5000 numerical fits; selected-field component<=180s with its model cap frozen
before execution. Use one BLAS thread, exclusive outputs, source/input pins,
terminal receipts and independent cached review. Keep documentation proportional
and reuse prior helpers; measurements and working behavior are the priority.

No runtime selection, Gazebo/matrix, physical/Pi/snapshot/V1, commit or push is
released here. A promising method must next pass an explicitly selected visible
integrated case, including continuous entry/lease/recording ownership. Full
augmented SEARCH confidence remains a separate incomplete criterion. Arrival
in the evaluator-only0.5m global region suffices; GOAL_HOLD remains optional.

Method context: [servo-based derivative estimation](https://arxiv.org/html/2509.16365v1)
motivates checking excitation and distinguishes its position-only theory from
directional photoresistor experiments; [error-aware least-squares ESC](https://arxiv.org/html/2107.01176v2)
motivates accounting for estimation error. R20's local-attraction statistic,
HAC calibration and finite controls are project-specific; no published theorem
is claimed for this implementation or the unicycle.
