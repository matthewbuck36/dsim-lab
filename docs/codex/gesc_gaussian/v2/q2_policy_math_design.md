# Q2 moving-cycle coherence implementation proposal

Status: prospective source/test design, 2026-09-09. No runtime edits, new
recorded-data calculations, model evaluations, tests, or acquisitions were
performed for this note. Parent owns the amendment and release.

The closed finite diagnostic nominated mean weight 0.75. Its saved result is
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_direction_policy_diagnostic_v1/analysis/result.json`.
This supports a development implementation, not qualification, an optimum
weight claim, or a new trajectory claim. Original confirmation remains sealed.

## Selected behavior and finite-zero clarification

Extend the existing rolling owner with selector `v2_direction_policy`:
default `three_cycle_v1`, optional `moving_cycle_coherence_v1`. Preserve the
default's numerical behavior and the existing wire binary layout. Bind the
selected policy in dispatch/configuration/recorded metadata; interpret the
existing `qualified` field under that exact policy. Keep `cycles_valid` and
the old inter-cycle statistics as their original controls.

The new policy uses the same current, complete world-phase revolution and
three completed covered cycles after the actual filter reset. Require current
coverage, finite support, original source/context/objective/frame identities,
gap and freshness constraints. Warmup is coverage, not agreement among three
old means. Keep the current mean magnitude floor 1e-6 cost/metre and the
coherence lower-bound threshold 0.25. The selected mixture is
`q = 0.25*q_instant_world + 0.75*q_mean_world`.

Explicit prospective clarification: a fresh finite instantaneous vector may
be zero or below the magnitude floor while a qualified mean and the mixture
are meaningful. Permit that mixture. This preserves the established behavior
demonstrated by `test_zero_instantaneous_value_does_not_suppress_mean` in
`ros2_ws/src/ros_esc/test/test_rolling_gesc.py`. Only instantaneous fallback
requires its norm to exceed 1e-6. A weak/nonfinite mixture falls back only to
a valid meaningful instant; if both alternatives are weak, output is invalid.
Invalid underlying input never becomes a fresh fallback. Preserve the old
policy's existing zero/weak behavior unchanged.

The frozen diagnostic harness additionally required a meaningful instant
before applying its gate. The continuity clarification is therefore an
explicit new runtime edge-case rule, not a claim that the diagnostic tested
that case. All original 24 anchors had meaningful instants, so their closed
results and nomination are untouched. Do not reevaluate D3 to erase this
distinction.

## Exact norm calculation with bounded cached work

Port the reviewed external D3 norm kernel into a private helper within the
existing runtime owner. Do not import a study directory at runtime or create
another node/pipeline. Keep the immutable external helper as an independent
test oracle. A scoped/lazy SciPy import for the selected new policy avoids
changing old-policy import/runtime behavior; verify the selected installed
dependency before node startup.

For each adjacent source segment with world vectors a,b, compute
`L(a,b) = integral_0^1 norm((1-s)*a+s*b) ds` using the D3 rule: split at the
internal norm minimum; epsabs=1e-12, epsrel=1e-10, limit=64. Integrating a
linear interpolation of endpoint norms would change the selected method.

Cache each full segment's unit-interval integral, error estimate, evaluation
count and failure receipt once when new source input arrives. Bind it to the
actual adjacent observations and current context/reset. Precompute during
warmup. At each new eligible input, reuse all full segments and evaluate only
the newly clipped first segment. Reuse a full segment at an exact boundary.
The clipping vector must come from the existing phase-fraction `_crossing`
and rounded integer source timestamp, matching `_summarize`; do not substitute
a time-fraction interpolation that changes that represented boundary.

Normalize each cached/full or clipped contribution by its integer duration
over the current cycle duration and combine with `math.fsum`. Retain this
simple O(n) sum alongside the existing mean scan; avoid long-run prefix
subtraction and its cancellation. Only expensive integration work is O(1)
new segments per input. Timer publications and repeated observations perform
no integration.

Freeze both limits: at most 2,048 **new** integrand calls per update, and at
most 20,000 calls represented by the active window's cached plus clipped
receipts. The second limit preserves the D3 per-window numerical budget;
caching is not a waiver. Exhaustion, warning, nonfinite result, or unresolved
error makes coherence unavailable with a distinct reason and permits only
the valid instantaneous fallback above. Cache failed full-segment receipts
too; repeated publication must not retry unchanged failed math.

Prune cache entries with the exact source-point history. Clear them on every
real history/context/objective/frame/phase/source reset and capacity reset.
An old failed segment can cease to affect a genuinely later window after it
leaves support. Preserve existing bounded point memory. Recheck publication
freshness after computation so CPU work cannot refresh a stale input.

Require normalized denominator error <=1e-10 cost/metre. Preserve D3's
numerator guard: component margin `1e-10 + 1e-8*norm(mean)`, norm margin
sqrt(2) times that value. With N=norm(mean), D=mean norm, and errors eN,eD,
use lower `max(0,N-eN)/(D+eD)` and upper
`min(1,(N+eN)/(D-eD))`, requiring D>eD and the triangle-inequality checks.
Only lower>=0.25 admits averaging; a threshold-straddling interval does not.
These are numerical error estimates, not a confidence probability or a
physical-model certificate. Online there is no independent saved mean to
reconstruct; the retained numerator margin is a conservative numerical guard.

An analytic antiderivative is unnecessary in this milestone: nearly constant
and collinear segments require careful scaling and cancellation branches plus
a new roundoff argument. Cached bounded quadrature preserves the already
tested numerical definition with much less implementation risk.

## Finite source checks before any Gazebo release

1. Compare cached rolling results against the immutable uncached D3 oracle on
   synthetic constant, collinear, zero-crossing, turning, tiny-change and
   broad finite-scale vectors. Include variable/cw phase, clipped boundaries,
   and source-time rounding. Check mean/denominator/error and gate agreement.
2. Advance and prune windows; count full-segment calls, clipped calls, timer
   calls (zero), cached failure reuse, reset invalidation, and both budgets.
   Preserve focused old-policy regressions and absence of norm work there.
3. Test three-cycle warmup, missing sectors, source gaps, context changes and
   finite-zero continuity explicitly. Include harmonic zero instants with a
   strong mean, just-above-floor vectors, mixture cancellation, and all-weak
   input. Never fabricate a fresh zero or fallback.
4. Use finite analytic input fixtures to expose limitations: DC washout
   startup can remain coherent; warmup does not reject arbitrary offsets.
   Balanced alternating noise can cancel, but phase-synchronous/correlated
   interference can pass. High harmonics or useful changing directions can
   have low coherence. Record counterexamples without fitting another gate.
5. Run one bounded synthetic performance check (for example 1,000 updates,
   command timeout 60 s), report integrand calls and callback p50/p99/max,
   and verify headroom against the selected 30 Hz input period. The 0.5 s
   freshness limit is not an acceptable target computation latency. Use the
   existing finite 30 Hz source/10 Hz held-clock transport fixtures for
   admission, reset, stale/future and final-zero regressions.

Only after source tests, installed dependency checks, durable receipts and
checkpoint should a separately frozen fresh closed-loop experiment measure
actual output accuracy/availability, motion and convergence. Changing weight
changes command magnitude and lag as well as direction. Neither cached math
agreement nor the latent diagnostic qualifies those effects or releases M4.
