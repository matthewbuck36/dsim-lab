# Prospective direction-development review — 2026-09-09

Status: PROPOSAL ONLY. No new weight, error, coherence, gate, policy, model or
reference values were calculated. No confirmation data or new simulation was
opened. The completed D2 result and its predeclared0.5 sensitivity stay intact;
parent owns that closeout and any next prospective plan.

## Recommended finite next step

Freeze one development diagnostic on the same24 original targets and existing
D2 reference vectors. Evaluate only the proposed fixed weights0.5,0.75,1.0,
plus one predeclared within-cycle coherence candidate at0.25. Include that
candidate before seeing any new values; inspecting weights first and choosing
a favorable gate afterward would add avoidable selection. No threshold sweep,
intermediate weights, new reference integration or new targets are needed.

Keep two distinct outputs: ungated algebraic weight sensitivities, and gated
hypothetical outputs that use the instantaneous fallback when the proposed
eligibility rule fails. Preserve the actual recorded output and D2's original
0.5 result as unchanged controls. This separates the effects of the weight
and its admission rule. Neither hypothetical output is a policy replay or a
new closed-loop trajectory.

The parent reports D2 has24 informative references and the0.5 latent blend
improves instantaneous error at all24 targets. That supports studying stronger
mean contributions; it does not establish that0.5 is optimal, that greater
weight must help, or that removing every confidence safeguard is justified.
Its reported p90 remains above the original desired direction bound. Actual
averaging availability is still only4/24 on the recorded policy.

## A meaningful online eligibility rule, with an honest claim

Use a separately named moving-cycle policy, preserving the old selectable
three-cycle policy and its old diagnostic/validation interpretation. Retain
the three-complete-covered-cycle warmup after a reset, but do not make moving
estimates agree in magnitude or direction across those three cycles. That
stationarity assumption is precisely what the completed evidence challenges.
Keep collecting the three-cycle diagnostics for explanation and other owners.

For the new candidate require:

- The existing latest complete signed world-phase cycle, source-time weighting,
  twelve sectors/two actual samples, duration/gap limits and finite support.
- Consistent run, frame, origin, source/observation and effective augmented
  objective identity; all original samples must have passed causal admission.
  A true context/reset/contradiction invalidates support and restarts warmup.
- The latest observation, its original needed receipts and the output pose
  satisfy existing freshness/clock coverage. Do not require an entire completed
  cycle to be younger than0.5s: its older samples were validated when admitted.
- A finite informative rolling-mean magnitude above the existing absolute
  1e-6 floor, plus within-cycle coherence kappa at least0.25.

For the actual last-cycle demodulated world vector q(t), define

    kappa = || integral_cycle q(t) dt ||
            / integral_cycle ||q(t)|| dt.

Time weighting and normalization agree with the recorded rolling mean; kappa
is dimensionless and lies in[0,1] when the denominator is positive. Reject
zero/nonfinite denominator. There is no evaluator truth, field gradient,
future sample or confidence-cycle angle in this rule. For an ideal uniform
first-harmonic washout signal the familiar value is pi/4, but that is an
analytic special case, not a lower bound for arbitrary useful field signals.

Call this observable eligibility/coherence, not a probability that direction
is correct. It guards cancellation/poorly sustained direction in the present
support while allowing its mean to change as the robot moves. The chosen0.25
is a prospective engineering candidate, not a noise calibration or certified
confidence level. Do not immediately retune it if this fixed version rejects
helpful means; preserve the result and diagnose the specific assumption.

Instantaneous fallback remains available when the mean fails these conditions
and the instantaneous path itself is valid. Invalid/stale underlying input
must retain invalid output and controller watchdog/stop behavior, not fabricate
a fresh fallback. A nonfinite or near-zero blend requires an explicit policy
decision before implementation: do not normalize it into an arbitrary heading.
Retain the existing meaningful instantaneous path if used as fallback, and
record that reason separately from insufficient mean confidence.

## Denominator and source support must match the recorded mean

The existing rolling mean integrates a linearly represented vector between
actual source knots, including its exact clipped boundary. Its denominator
must integrate the norm of that same represented vector. Trapezoidal
integration of endpoint norms represents a different function and generally
overestimates this denominator by convexity, thereby lowering kappa. Freeze
one consistent definition; do not switch after observing near-threshold cases.

For a segment a+s*v,0<=s<=1, duration h, integrate
h*integral_0^1 ||a+s*v|| ds. An analytic norm integral or bounded independent
quadrature can handle this without any objective evaluation. The zero-length,
constant-vector, collinear/crossing-zero and nearly constant cases need stable
branches and tests. Both numerator and denominator must use original vector
knots; preserve all exact cycle boundaries and avoid temporal resampling.

Join every needed original first diagnostic to the frozen observation/source,
filter state/publication and reset/context identity. First verify that the
integrated numerator reproduces the saved rolling mean within the declared
floating-point tolerance. Missing source support, contradictory duplicate,
wrong reset generation, or a missing exact first publication makes coherence
unavailable; do not substitute a later diagnostic. Preserve24 slots and the
original eligibility/missing reasons in all comparisons.

## What coherence does not solve

- A repeatable phase-synchronous disturbance can be coherent even without a
  useful spatial direction. Coherence cannot distinguish it from signal by
  itself; known injected disturbances and fresh tests must examine this case.
- A constant-cost washout startup transient is not instantly zero. Under a
  uniform cycle its exponentially decaying rotating vector can have nonzero
  coherence; three-cycle warmup reduces transient scale but does not prove it
  falls below a fixed magnitude floor for every DC level. Include objective
  reset, offset scale and warmup transitions in component tests.
- Higher harmonics and nonuniform phase can change the relation between net
  direction and vector variation. A useful weak first harmonic can fail the
  candidate; a coherent but spatially biased signal can pass it.
- Correlated noise, drift and deterministic motion are not interchangeable
  with independent noise. Do not attach an SNR interpretation or confidence
  interval to0.25 without a separate validated noise model.
- A complete latest cycle is still a historical spatial/time average. Greater
  mean weight can reduce instantaneous oscillation while adding lag or changing
  commanded magnitude. The D2 reference is a fixed-position periodic GESC
  response, not a true gradient or proof of descent in the moving field.

These limits favor retaining the existing input/coverage safeguards and fresh
closed-loop qualification. They do not justify restoring the same rejected
three-cycle stationarity gate under another name. Avoid adding a new maximum
yaw change or translation threshold from these same24 outcomes without its
own prospective hypothesis and evidence.

## Predeclare the finite weight choice

The sensitivity should report each target and each run, not just a pooled
median: angular improvement/degradation, tail errors, missing/noninformative
vectors, mean admission/fallback counts, and vector magnitudes. Changing the
weight changes both direction and gain; record magnitude effects even though
this diagnostic cannot predict their later trajectory.

One defensible deterministic nomination rule is to rank fully specified gated
candidates by the worse of the two per-run p90 errors, then the worse per-run
median, then pooled median; prefer the smaller weight for an exact tie. Report
ungated rankings separately. Freeze the precise missing-vector handling and
any required availability floor beforehand so invalid vectors cannot disappear
from a favorable denominator. A candidate with less complete evidence must
not win because difficult targets are omitted. Retaining0.5 is a legitimate
result if alternatives do not improve the declared objective.

This is development selection over only three values on two correlated
trajectories, not an optimum estimate or independent validation. The same
trajectories already motivated the method; uncertainty summaries cannot make
them fresh holdout evidence. A development nomination does not satisfy the
original actual-runtime accuracy, availability, detector or pilot gates.

## Implementation and fresh evidence after the diagnostic

Only after the finite results, select and freeze one policy/weight. Extend the
existing rolling/filter owner and its validator with an explicit policy
identity. Preserve source provenance, objective reset behavior, controller
ownership, speed ceilings, recorder readiness, final zero, legacy defaults
and the other three comparison arms. Do not reinterpret previously recorded
qualified flags under new semantics.

Run bounded component tests for exact quadrature, normal rotating harmonic
signals, moving/turning means that should remain usable, zero/constant fields,
DC/reset transients, high harmonics, additive/correlated/phase-synchronous
noise, cancellation, clipping, time/frame/identity faults and fallback. These
establish implementation properties and failures, not research qualification.

Then acquire prospectively reserved fresh closed-loop development and
confirmation inputs under the existing scenario/recorder/analyzer owners.
Evaluate actual output accuracy/availability against the declared reference,
progress/orbit behavior, source integrity, safety and the separately required
detector/neighborhood evidence. Changing the policy changes the path, so none
of the algebraic sensitivities substitutes for these runs. Keep the old
confirmation partition sealed. Freeze the new independent confirmation
population before acquisition and never tune during it. The original16-run
four-arm M4 study remains unreleased until the complete prerequisite contract
is actually satisfied.

This review inspected current plans/status and the existing RollingGesc owner;
it performed no new diagnostic calculation. All numerical examples above are
definitions or analytic limiting cases, not measurements of the frozen targets.
