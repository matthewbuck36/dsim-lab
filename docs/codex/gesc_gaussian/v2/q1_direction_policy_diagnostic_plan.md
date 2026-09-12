# Finite direction-policy diagnostic — 2026-09-09 UTC

Status: ACTIVE DIAGNOSTIC PREPARATION under the approved simulation-only V2
goal. Read `plan.md`, `status.md`, `q1_observed_phase_handoff.md` and
`validation/q1_observed_phase_result.md`. This amendment is declared before
calculating any additional weights, coherence values or alternative gate.

The observed-phase diagnostic is closed at the227-file material checkpoint
`checkpoints/q1_observed_phase_closed_v1/manifest.json`, SHA256
`62127026e35140c9a0dc3a2821f760a1aa1e6a49c84d37f7f12e421dbf987be8`:
958647-byte archive,281 retained artifact hashes. Its24 references and original
50/50 sensitivity remain unchanged. The latter improves instantaneous error
at every target but has pooled p90=71.986722deg, above the original60deg level.

## Fixed question, population and arithmetic

Version: `q1-direction-policy-diagnostic-v1`. Exclusive external root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1/`.
Use exactly the same24 discovery targets (seeds26090911/26090912,numbers1–12),
their original first recorded instantaneous vectors and one-cycle means, and
the already computed observed-phase reference vectors. No new target,
reference/model integration, filter replay, bag acquisition or confirmation
access is included. All556 existing frozen source owners remain unchanged.

Predeclare exactly three mean weights `lambda in {0.5,0.75,1.0}`:
`q_lambda=(1-lambda)*q_instant_world+lambda*q_recorded_mean_world`.
Report all three ungated algebraic sensitivities. Separately report three
hypothetical gated outputs using the single coherence rule below; there is no
threshold sweep or intermediate weight. Preserve actual recorded output and
the prior declared0.5 sensitivity as fixed controls. Every unavailable or
degraded case remains in its original target slot.

## One predeclared current-cycle coherence rule

For the same linearly represented world demodulation vector q(t) over the
original rolling interval, define dimensionless
`kappa=norm(integral q(t) dt)/integral norm(q(t)) dt`.
The denominator integrates the norm of the linearly interpolated vector,
not linear interpolation of endpoint norms. It is positive for a usable
signal and kappa lies in[0,1]. Reject zero/nonfinite denominator.

The prospective rule requires:

- Existing source/context/objective/frame/readiness validity and freshness at
  each sample's original admission, a fresh original output and blend-allowed
  state. Historical cycle samples need not all be younger than0.5s at the end.
- One full current world-phase revolution, all twelve sectors with at least
  two actual samples, finite consistent support and the original gap bounds.
- Three completed covered cycles after reset as warmup; retain their coverage
  receipts, but do not require their means to agree in angle or magnitude.
- Current rolling mean norm>1e-6cost/metre and `kappa>=0.25`.

The old30deg inter-cycle angle and3sigma variability floor remain recorded
controls; they are not part of this newly declared hypothetical rule. The
warmup uses the runtime's original covered-cycle receipts: recorder readiness
does not retroactively reset the filter. Require current mean support and
target readiness; earlier warmup cycles may predate recorder readiness when
their original source admission was valid. Preserve that clock/owner distinction.
The
chosen0.25 is an engineering candidate, not a calibrated noise probability.
Ideal uniform first-harmonic demodulation has kappa=pi/4, but useful moving or
higher-harmonic signals can have lower coherence. Phase-synchronous
interference and washout startup transients can be coherent. Three-cycle
warmup does not prove transient rejection for arbitrary cost offsets.

When this proposed mean rule fails, use the original fresh finite meaningful
instantaneous vector as hypothetical fallback. A nonfinite or norm<=1e-6
mixture also falls back to that vector with its own reason. Invalid underlying
input never becomes a fresh fallback. Ungated sensitivities with unavailable
mean or weak mixture remain unavailable rather than silently using fallback.
Report gated averaging application and fallback separately from the ungated
vector's calculability. No hypothetical vector is a recorded runtime output.

## Exact support and numerical checks before any gate calculation

Recover the original rolling_start_ns/rolling_end_ns from the exact first
diagnostic supplement. Use the original frozen observations and first
diagnostic instantaneous-world vectors, source-time order and clipped boundary
interpolation without extrapolation. Require every supporting sample to have
matching source/context/objective/reset identities and original publication/
bag receipt no later than the target's original diagnostic. Preserve source
gaps/missing support as unavailable; never substitute a later publication.

First reproduce the saved rolling mean from the represented numerator, with
component tolerance `1e-10+1e-8*norm(saved_mean)`cost/metre. Failure makes
coherence unavailable and prohibits treating that support as a new mean. The
ungated sensitivity still uses the actual saved mean when its original
full/covered/finite conditions pass.

Integrate each linear segment's norm by bounded adaptive quadrature on its
unit interval, split at an internal norm minimum, with epsabs=1e-12,
epsrel=1e-10,limit64 and at most20,000 integrand calls per anchor. Normalize the
sum by the same cycle duration. Require aggregate normalized denominator error
<=1e-10cost/metre and no warnings/nonfinite results. Propagate that error and
the recorded-mean reconstruction tolerance into a coherence interval. Admit
only if its lower bound is>=0.25; a straddling interval is unavailable for the
gate. Retain scalar values, bounds, supports and all unavailable reasons.

Before evaluating these data, check constant vectors, changing collinear
magnitudes, exact opposite vectors crossing zero, a turning linear segment
with analytic norm integral, time scaling, clipped boundaries, pi/4 uniform
harmonic limit, zero/nonfinite values, missing/gapped/noncausal/mismatched
support, wrong units, warmup/coverage, weak-blend fallback and denominator
budget/error handling. Test that fixture rankings retain failures and every
target, and that no field model or confirmation file is opened.

## Finite selection and evidence boundary

Report each candidate at every target, per-run and pooled: angular error,
improvement/degradation versus both controls, vector magnitude/ratio to actual,
coherence, applicability, averaging/fallback and unavailable counts. Retain all
24 slots. Compare only informative fixed references; their original24/24
status may not be changed. Missing hypothetical errors count against complete
evidence rather than disappearing from a favorable quantile denominator.

Only gated candidates with all24 valid hypothetical errors, pooled averaging
application>=0.8, pooled median<=30deg and pooled p90<=60deg may be nominated
for further development. Rank qualifying candidates by the worse per-run p90,
then worse per-run median, then pooled median, then smaller lambda. There is
no rounding-based tie or post-result tolerance change. Ungated candidates are
reported separately and cannot bypass the declared confidence rule. If none
qualifies, record NO_NOMINEE and preserve this version before further diagnosis.

A nomination is development selection on two repeatedly studied trajectories,
not independent qualification or proof of a new path. Changing mean weight
changes both direction and command magnitude/lag. Runtime implementation,
transient/noise tests and fresh prospective closed-loop qualification require
a subsequent amendment. Original confirmation stays sealed; M4 stays unreleased.

## Reuse, freeze, execution and closeout

Use one externally retained finite diagnostic harness, as for the preceding
recorded-data audits. Reuse the existing analyzer's strict observed-phase
receipt validation and first-diagnostic joins, its scalar serialization helper,
and the existing numerical angular-error owner. This is scalar/vector analysis
of saved outputs, not a new bag-analysis pipeline or field/filter model. Do
not modify existing frozen numerical, analyzer, runtime or workflow owners.
The independently implemented support-norm calculation is an evaluator only;
no online confidence policy is changed by this harness.

Freeze this plan, the prospective review, harness/tests, all fixed parameters,
the completed checkpoint, D2 result/closure/contract and original targets/traces/
supplement hashes before the single arithmetic job. Required primary hashes:
D2 result `6c7ca706ed779df45003bccf909890e07e83b5ac1d4f84f9a2c637c7d8f357bf`;
D2 closure `52c8942e1f311ee4aae7659ee90b14e01c70136f532f2811229ebf98b197af04`;
D2 contract `d9ed31f52c9f088199fdf700076424b730e0248a143f9ace2495c8666527b45e`.
Check exact24 identities and source freshness before output and after the job.
Keep failed preflight attempts and partial per-target receipts. Run the one
arithmetic job under60s, with no automatic retry. Save complete/unavailable/
incomplete status, exact command, hashes, limitations and handoff/checkpoint.
Qualification is always NOT_EVALUATED and no runtime change is released by
this diagnostic alone.
