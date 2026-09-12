# R19: information remaining when motion is suppressed but noise is retained

ADOPTED prospectively on 2026-09-11 UTC after R18 reviewed material closure,
before any R19 fit. This is a small diagnostic using cached measurements.

R18 shows that removing XY terms alone leaves large errors, while fixed-anchor
cost is much more accurate. Those fixed-anchor costs were noise-free. Before
changing collection motion, determine whether the retained noise would still
prevent useful direction or raw verification evidence.

For every original supported target and verification matrix, construct
`epsilon = recorded_raw - model_provenance`, then
`test_raw = model_fixed_anchor + epsilon`. Copy XY to the original fixed anchor;
retain timestamps, world phases, cycles, source identities and anchor time.
This transfers one realized residual under the selected additive noise model;
it is not independent noise replication or an actual stationary acquisition.
The nominal streams' near-roundoff residuals are retained too.

Use the same six runs, all144 scheduled/46 eligible/40 supported targets and
eight verification supports. Preserve the six original eligible support failures,
all references/maps/known contributions and original verification guards and
mismatches. No new field, bag, reference or map calls. Use R15 linear only,
because R18's fixed-cost linear fit is the smallest adequate point model on
these inputs. This does not reverse its independent quadratic-null rejection.
Use its unchanged cutoff5.638621374336838 and latest-cycle prediction gate.
Reuse all recorded/noiseless moving/fixed-anchor diagonal fits without refitting.

Report per-run all-supported and admitted direction median/P90, original
availability denominators, paired diagonal vector/angle changes, raw score and
all eight verification projections. Existing direction limits remain30/60degrees
and80% availability among eligible targets. Original unsupported observations
cannot be rescued by artificial XY. In particular C development's3/4 support
ceiling remains a separate obstacle. No gate is retuned.

The prospective decision is whether motion suppression is a promising next
collection change under this realized noise. If either noisy run fails the
30/60-degree all-supported error limits or fewer than7/8 raw verification
supports pass the frozen R15 rule, reducing motion alone is insufficient for
this estimator/collection evidence contract. Prioritize the failing noise or
information mechanism before simulation. This is a development decision, not
proof that every nonzero contraction fails: motion can also change signal strength.
Otherwise a single nonzero travel
contraction may be planned next, preserving sample count and noise realization.
Even a favorable result is developmental and cannot qualify a failed estimator,
the original unavailable targets, runtime behavior or a comparison matrix.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r19_retained_noise_v1/`.
One root-owned job,48 public fits maximum,25-second internal budget,35seconds
to SIGINT plus5seconds to kill,one BLAS thread. Reuse the R18 helper and existing
owners through a small adapter; stable source/input/plan pins and exclusive
outputs. Preserve partials and terminal receipt. Independently check the cached
noise arithmetic, identities, mappings and summaries without refitting, then
save validation/handoff and checkpoint. No estimator source tests are required
because no numerical owner or runtime code changes.

No physical/Pi/snapshot/V1 change, commit, push, runtime launch or matrix is
released. Full goal remains reliable detection and continuous direction/source
seeking. Arrival within the evaluator-only0.5m global region suffices;
GOAL_HOLD is optional. Mandatory stopped sweeps remain excluded.
