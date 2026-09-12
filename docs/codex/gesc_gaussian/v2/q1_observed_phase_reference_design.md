# Prospective observed-phase reference review — 2026-09-09

Status: PROPOSAL ONLY. This note contains source inspection, interpretation of
already saved discovery receipts, and an analytical derivation. No reference,
field, geometry, filter replay, confirmation, or Gazebo job was run. No source
or retained evidence was changed. Phase V2 plan context check passed.

The existing reference can be extended soundly to the measured nonuniform
world phase without changing the runtime filter. The useful counterfactual is
the same complete augmented objective evaluated at the anchor's fixed base
position, driven by a periodic repetition of the observed phase-time profile.
It requires a separately named reference version. Raising the existing CV0.10
gate or replacing the observed profile by its mean rate would not compute this
reference and would change the closed diagnostic improperly.

The subsequently completed fixed24-anchor confidence decomposition confirms
both magnitude and direction variation. A new reference is now a useful next
diagnostic before tuning: it would address missing accuracy comparisons while
a predeclared algebraic50/50 blend sensitivity could test the usefulness of the
averaging rejected by the current gate. Neither calculation would change the
runtime branch or demonstrate a new robot trajectory.

## Evidence supporting this direction

The completed24-target diagnostic remains COMPLETE_DIAGNOSTIC, qualification
NOT_EVALUATED, confirmation SEALED and M4 unreleased. All24 anchors are causal
with valid outputs. Twenty references fail the unchanged constant-rate
approximation; four are informative, all residence. Averaging is usable at
one of those four. Across all24, four outputs blend,18 use weak-cycle fallback,
and two use cycle-disagreement fallback. On the only reference-eligible blended
anchor, recorded error decreases from42.824683 to21.478464 degrees. The other
three eligible anchors fall back. This does not establish improvement over the
whole population or accuracy on the approach run.

Galileo's saved rate audit finds actual34ms source intervals, sequential keys,
one context/objective, readiness-qualified samples and full twelve-sector
coverage in every saved cycle. World phase equals base yaw plus encoder phase
to within1.5425e-8rad; world-rate/base-yaw-rate correlation is at least0.9999329.
Encoder means are2.094024–2.094683rad/s with standard deviations
0.001554–0.003440rad/s, while yaw standard deviations0.143068–0.408894rad/s
account for the much larger world-rate variation. This supports an unsuitable
constant-world-rate reference assumption for normal recorded turning, rather
than a source-clock or large encoder-rate fault. It is not proof of the cause
of the orbit. Actual cycle duration spans2.701500–3.009248s, CV0.067427–0.185027.

Verified read-only receipts under
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_discovery_direction_diagnostic_v1/`:

- `analysis/references.json`, SHA256
  `845a549849295082fe2d3b82f95ff81f788979898e52f47646f228704258a00c`.
- `diagnostics/rate_and_fallback_v1/result.json`, SHA256
  `4e5abc4033433cbd7d84e630ad981c5e5cab86c7ef83cd201f62b5b5d5aaa280`;
  its adjacent README records the bounded0.58s arithmetic audit and all24 rows.
- `diagnostics/cycle_confidence_v1/result.json`, reported SHA256
  `4a2c39e84c1c6ada74b5b4cc193af83f928b9f49e8ea12be07f4e77a32293edf`;
  its adjacent README records24 exact original diagnostic joins and the5.75s
  targeted discovery-only bag extraction. This audit completed during review.

## The stationary-position, observed-phase periodic reference

Use the existing signed, unwrapped, complete source-time revolution, clipped
at exactly the existing boundary. Set local time s=0 at its start, duration T,
and retain every original phase knot and linear interpolation between knots:
theta(T)=theta(0)+sigma*2pi, sigma in {-1,+1}. Extend
theta(s+T)=theta(s)+sigma*2pi. This periodic extension is a declared
counterfactual; successive physical cycles need not actually repeat.

Freeze the existing complete augmented objective at anchor base position p*:
u(s)=J*(theta(s)). J* uses the selected raw numerical model, the same rotating
sensor geometry, and all effective Gaussian/affine terms and weights at that
anchor. Keep negative cost sign and selected d=0.18m. No substitution of raw
for augmented cost or of a spatial gradient for the GESC response is allowed.
Fixed position does not require constant yaw; observed world phase already
contains yaw plus joint phase. Rotation of the selected body demodulation into
world coordinates gives exactly the basis [cos(theta),sin(theta)].

The selected washout is

    z'(s) = alpha * (u(s) - z(s)),  alpha = 1 / second,
    y(s)  = u(s) - z(s).

Its unique periodic solution is specified without arbitrary burn-in:

    z(0) = alpha / (1-exp(-alpha*T))
           * integral_0^T exp(-alpha*(T-s)) * u(s) ds,
    z(s) = exp(-alpha*s)*z(0)
           + alpha*integral_0^s exp(-alpha*(s-r))*u(r) dr.

The reference world vector is

    q_ref = -2/(d*T) * integral_0^T y(s)
                                   * [cos(theta(s)),sin(theta(s))] ds.

This is time-weighted, matching the selected rolling owner. It has units of
cost/metre and preserves the selected sign, gain and washout dynamics. A
constant subtraction c from u, with the same subtraction from z, changes
nothing and can improve numerical conditioning. Nonuniform phase speed changes
both dwell weights and washout lag, allowing higher angular harmonics of J* to
affect the result. Therefore the old first two Fourier coefficients and mean
omega alone are insufficient. A DC objective still gives exactly zero for any
phase schedule.

This is an ideal periodic GESC response at a fixed position, not an assertion
that the actual moving filter has reached that state, a noise-free true spatial
gradient, or an expected command under a new controller. Translation and
washout transients remain possible causes of differences from recorded output.

## Efficient evaluation through an exact periodic adjoint kernel

The periodic ODE need not be integrated repeatedly around the expensive field.
Let e(s)=exp(i*theta(s)) and define periodic complex r(s) by

    -r'(s) + alpha*r(s) = e(s),  r(T)=r(0).

Periodic integration by parts gives integral(z*e)=alpha*integral(u*r), hence

    q_x + i*q_y = -2/(d*T) * integral_0^T u(s)*K(s) ds,
    K(s) = e(s) - alpha*r(s).

For a phase-linear segment i of duration h_i and signed rate omega_i, the
backward recurrence is exact for the represented phase:

    A_i = exp(-alpha*h_i),
    B_i = exp(i*theta_i)
          * (1-exp((-alpha+i*omega_i)*h_i))/(alpha-i*omega_i),
    r_i = A_i*r_(i+1) + B_i.

First recurse backwards with terminal value zero to obtain B_total. The full
recurrence has multiplier exp(-alpha*T), so

    r_0 = B_total/(1-exp(-alpha*T)).

Set r_N=r_0 and recurse backwards once more to retain all endpoints. Inside
segment i, for remaining duration h to its endpoint,

    r(s) = exp(-alpha*h)*r_(i+1)
           + exp(i*theta(s))
             * (1-exp((-alpha+i*omega_i)*h))/(alpha-i*omega_i).

Use stable expm1 forms when their arguments are small. Zero-rate dwell segments
are well-defined because alpha>0; negative rotation is also supported. The
kernel is dimensionless, r has units of seconds, and integral(K)=0. Only the
final two real quadratures query J*. No nested field quadrature, ODE burn-in,
resampled cost trace or new analysis pipeline is necessary.

## Uniform-rate and discrete limits

For theta=theta0+omega*s, r=e/(alpha-i*omega) and
K=conj(Hc)*e, where Hc=i*omega/(alpha+i*omega). If
J*(theta)=c+a*cos(theta)+b*sin(theta), then

    q_ref = -[(Re(Hc)*a + Im(Hc)*b),
              (Re(Hc)*b - Im(Hc)*a)] / d.

This is exactly the existing continuous_transfer/_reference_vector result for
either signed rotation, independent of phase start. Uniform higher harmonics
have zero first-harmonic mean. Their possible contribution under variable rate
must not be mistaken for a sign error in the generalized reference.

For uniform actual Euler steps h with output before state update,
z_(k+1)=(1-alpha*h)*z_k+alpha*h*u_k gives

    Hd = (exp(i*omega*h)-1)/(exp(i*omega*h)-1+alpha*h),
    0 < alpha*h < 2,  Hd -> Hc as h -> 0.

Retain this as a uniform-limit regression and the old version's optional
sensitivity. Do not label Hd at mean omega an exact nonuniform reference.
The source-clipped cycle boundary is not an actual Euler update, and T need
not be an integer multiple of actual h. A general periodic discrete sensitivity
would need its own explicit sample/update-boundary contract; it is unnecessary
for this first continuous reference diagnostic.

## Numerical acceptance and existing owner reuse

Extend `plotting_scripts/v2_direction_reference.py` with one explicitly
versioned observed-phase function. Factor the existing reference_cycle's exact
kinematic extraction into a shared helper that can return the phase/time knots;
preserve the legacy wrapper, CV0.10 and outputs with parity tests. All prior
source-gap, identity/context/objective, finite, phase ambiguity/reversal,
duration, readiness and actual twelve-sector coverage gates still apply.
Observed rate CV becomes descriptive input to the new physical model, rather
than being silently waived inside the old approximation.

Reuse the existing augmented_objective owner and dual adaptive quadrature
approach. Split at every actual phase-time knot and at the existing angular
breakpoints mapped to time, with the existing independent shifted partition.
Do not replace narrow angular field features by costs interpolated only at
34ms samples. Reuse cached objective calls and retain the25,000 distinct
objective-evaluation cap per anchor, nonfinite/warning/error rejection and
exclusive partial receipts. Expensive model evaluation may still exhaust the
overall300s budget on24 newly eligible anchors; no completion guarantee or
automatic retry is implied.

For C=(2/T)*integral((u-c)*K), each component has cost units. Require normalized
component error estimates <=1e-6, including both pass error estimates and
disagreement. Propagate E_q=hypot(E_Cx,E_Cy)/d and retain the informative floor
max(1e-6,20*E_q). Record kernel periodic-closure/DC residuals and a conservative
floating-point contribution instead of calling quadrature estimates rigorous
certificates. Phase interpolation/model uncertainty is separate from numerical
integration error. The independent direct periodic-ODE analytic tests below
are essential to catch algebra, complex-conjugation or boundary mistakes.

Use the same `evaluate_q1_direction_references` batch/paired-summary owner with
an explicit new reference selector and fresh diagnostic contract. Preserve all
24 original targets, first recorded outputs, readiness/input provenance, and
missing slots. Bind old closed receipts and original numerical/analyzer source
snapshots; permit only the declared numerical-owner/analyzer transition plus
new workflow/test receipts. All other source hashes remain exact. Do not
modify historical contracts, targets or source hashes, and do not loosen the
default48-target qualification route. Recheck lineage before output, before
each first model evaluation and after the job as the current owner does.

## Required bounded analytic checks before any data evaluation

1. Constant objective under nonuniform phase/dwell gives zero; DC offset changes
   neither vector nor informative classification beyond declared error bounds.
2. Arbitrary first harmonics at both signed uniform rates reproduce old Hc;
   phase-origin rotation/cyclic time-origin changes are consistent. Uniform
   higher harmonics give zero. Hd converges to Hc as h decreases.
3. Piecewise variable-rate analytic objectives agree with an independent direct
   periodic washout ODE solve, including first/higher harmonics and dwell. Test
   periodic closure, narrow segments, stable exponentials and complex signs.
4. Coordinate rotation rotates the world vector covariantly; freeze transformed
   field and geometry together. No body/world mismatch is hidden by norms.
5. Exact old numerical/cycle outputs remain unchanged. Malformed clocks, phase
   gaps/reversals, context/objective changes, weak reference, quadrature warning,
   budget exhaustion and timeout retain invalid/partial results appropriately.
6. The new route retains exactly24 discovery IDs and rejects confirmation,
   changed targets or unapproved source transitions before model evaluation.

## Confidence diagnosis should precede a runtime change

Current RollingGesc uses three completed cycle means m_i, their center m_bar,
sigma=sqrt(sum_i ||m_i-m_bar||^2/3), and floor=max(1e-6,3*sigma). Every cycle
norm and the current rolling-mean norm must exceed that floor; only then is
the30-degree pairwise direction test applied. Thus deterministic changes in
magnitude can cause weak-cycle fallback even for collinear directions. For
example, collinear magnitudes1,1.5,2 give sigma=sqrt(1/6) and3*sigma>1, so
the first magnitude fails. This mathematical example is not an attribution of
the18 actual weak flags.

Sagan has now joined all24 original first diagnostics exactly, including the
source, observation hash, publication and bag-receipt identity. All24 effective
floors come from3*sigma. Among the18 weak cases, cycle-magnitude CV has
median0.276912; the median of each target's maximum pairwise separation is
54.743042degrees, spanning26.820987–96.117275degrees. Fifteen of the18 have
derived maximum separation above30degrees, though the actual weak cases return
before that angle calculation. Longitudinal variance dominates eight and
transverse variance ten; median transverse fraction is0.555438. These are
descriptive decompositions, not a unique causal division into amplitude noise
and direction error. They disfavor a simple claim that magnitude variation
alone makes a useful stable direction fail the gate.

The audit resolves the missing floor data without an objective/reference job
or tuning. It does not establish whether the separately recorded last-cycle
mean is useful at the instantaneous anchor position: the three anchored cycle
means and that rolling mean have different support. That accuracy question
justifies the observed-phase reference rather than relaxing the gate now.

## One optional, predeclared algebraic blend sensitivity

Include this only if frozen in the next diagnostic contract before new model
values are evaluated. At each of the same24 targets define

    q_latent = 0.5*q_instant_world + 0.5*q_recorded_rolling_world.

The weight0.5 is the already selected runtime weight, not a new fitted value.
Use the original first diagnostic's actual one-revolution rolling mean, never
the mean of the three confidence-cycle means or a later favorable publication.
Require that original mean to be full, covered, finite and joined to the same
immutable source/observation. Preserve all slots, including weak-confidence
ones; their reason is part of this diagnostic question. A missing mean or
zero/too-small resulting vector yields unavailable angular error, not a
replacement. Use the same1e-6 output norm floor and explicitly named paired
denominators as the primary comparison.

The primary outputs remain the aligned recorded instantaneous and actual
runtime vectors. q_latent is a separately named algebraic sensitivity, not a
recorded output, simulated policy, accuracy qualification, or replacement for
the actual4/24 blend count. At the four actually blended anchors it must match
the recorded vector within an explicit floating-point tolerance; add this as
an evidence consistency check. Elsewhere it tests only what the current
instantaneous mixture would have been on the already recorded trajectory.
An altered online gate would change future motion, objective input and filter
state, so favorable latent errors cannot predict that new trajectory.

Bind the confidence audit and exact retained diagnostic payload/source hash
chain in the new contract; retain first-publication identities. Recheck these
new inputs before and after model work. Keep primary and latent summaries
separate, report paired improvements and degradations at every eligible target,
and disclose missing/weak references. Do not select a subset or a new blend
weight based on the resulting errors.

This sensitivity is inexpensive once the reference exists and can distinguish
an unavailable comparison from a conservative gate discarding helpful means.
Its tradeoff is that it adds a development-only comparison whose causal scope
is strictly smaller than a new closed-loop trial. Actual three-cycle direction
variation makes it especially important to retain worse cases, rather than
using the best latent anchors as a gate design.

One prospectively frozen24-target observed-phase reference diagnostic under300s,
with this sensitivity declared beforehand if desired, is therefore a bounded
next step. Keep qualification NOT_EVALUATED regardless of numerical coverage
or apparent improvement. No runtime tuning, new target, confirmation opening
or pilot release follows automatically.

Source hashes inspected for this proposal:

- `plotting_scripts/v2_direction_reference.py`:
  `614332ebbaa0d654b11b8f0c7304bf980ea3e7d693172e471dc999d703f51aed`.
- `filter_node/rolling_gesc.py`:
  `7914b8aac889182f4440844c27678076074577328df2586eb87c4dc7947811fb`.

These are proposal inputs, not a released new contract or numerical result.
