# R18: separate changing cost from regression position terms

ADOPTED prospectively on 2026-09-11 UTC, after R17 closure and before
any R18 fits. R17 remains rejected and unwired. Full goal remains incomplete.

R16/R17's successful fixed-anchor control changed both the measured cost and
the fit XY design. This study crosses those factors to identify a useful next
method or collection change. It is a cached diagnostic, not qualification.

## Frozen inputs and comparisons

Reuse R15/R16/R17's six C/D development, nominal and noisy inputs, all 144
scheduled targets, 46 eligible targets, the same 40 supported matrices, and
eight noisy verification supports. The six original eligible support failures
remain unavailable even when copied XY would satisfy excursion guards.
All source identities, timestamps, phases, cycle IDs, original support decisions,
anchor position/time, observed-phase maps, known augmented contributions and
references remain unchanged. Verification anchors remain frozen candidate
centers. No new field evaluation, bag extraction, quadrature or reference/map
computation is needed.

Three new cells are adopted:

| Cell | Raw cost column | Fit XY columns |
| --- | --- | --- |
| fixed_cost_moving_design | R16 model_fixed_anchor | original recorded XY |
| moving_cost_fixed_design | R16 model_provenance | original anchor XY |
| recorded_cost_fixed_design | actual recorded raw cost | original anchor XY |

Only these copied columns change. Original arrays are immutable. Fit each cell
with R15 linear, R15 quadratic, and R17 lambda 0.01: 3 cells x 48 supports x
3 methods = 432 new public fits maximum. Reuse completed diagonal fits from
R15/R16/R17 without refitting. The fixed-XY variants have zero spatial nuisance
and interaction columns; their estimates should agree to numerical precision,
although methods retain their own uncertainty and admission bookkeeping.

Use the existing owners and exact existing map/covariance composition. Frozen
R15 cutoffs are 5.638621374336838 (linear) and 6.590091490413824 (quadratic),
with their original latest-cycle prediction requirement. R17 uses score-only
admission above 6.449624183670948. No cutoff, model or support tuning is allowed
within this study. Counterfactual admission is descriptive; synthetic calibration
does not establish a false-acceptance guarantee for these copied inputs.

## Measurements and interpretation

Report per-run all-supported median/P90 direction error, frozen admitted
availability and errors, paired changes from cached diagonals, fit failures and
all eight verification projections. Retain paired mapped vectors and magnitudes;
angle differences are not additive percentages attributable to either factor.
Check that fixed-XY coefficients and mapped vectors agree across the three
methods to numerical tolerance. Preserve the original per-run direction
limits of median <=30 degrees, P90 <=60 degrees and >=80% averaging availability
among eligible targets. Report each method/cell separately; do not pool away
failures. Original verification non-signal guards and historical diagnostic
mismatches stay visible. A projected pass is not an actual fill or arrival.

Before execution, the development decision is:

- If fixed cost with moving design retains large errors, moving XY regression
  can create error even with a spatially stationary measured angular profile.
  Investigate nuisance projection, harmonic truncation and identifiability;
  this does not by itself distinguish those numerical mechanisms.
- If moving/recorded cost with fixed design substantially reduces those errors,
  consider a simpler angular/time fit as a candidate for independent nonlinear
  spatial-null and change controls. It cannot bypass those controls or use
  ground truth at runtime.
- If moving cost with fixed design retains large errors while fixed cost with
  fixed design is accurate, physical change of the angular profile remains a
  concrete reason to reduce motion per estimate or model that change differently.

Use the full paired distributions and original numerical limits; these are
diagnostic branches rather than a newly calibrated significance test. Multiple
mechanisms may be present. Artificial XY freezing changes statistical
estimability, leverage and uncertainty as well as nuisance coefficients. It
does not make the robot stationary, establish a causal physical experiment,
or guarantee that a time-only estimate equals the response at a frozen center.

## Bounded execution and completion

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r18_crossed_design_v1/`.

One root-owned scientific job: 115 seconds to SIGINT plus five seconds to kill,
105-second internal budget, one BLAS thread, maximum 432 fits. Prepare stable
source/input/plan pins and exact command before execution, use exclusive outputs,
retain partials, and record terminal exit and elapsed time. Independent cached
review must check copied inputs, mapping arithmetic, denominators and summaries
without refits. No new source tests are required because runtime/estimator source
is unchanged. Record results and next decision in a handoff and validation record,
update live navigation, and use the existing phase checkpoint at closure.

No runtime wiring, simulation, matrix, physical/Pi/snapshot/V1 change, commit
or push is released by R18. Independent controls and a credible visible
integrated case still precede another comparison. Arrival in the evaluator-only
0.5 m global region suffices; GOAL_HOLD is optional.
