# R18: changing measurements remain the main correction target

Study COMPLETE; independent cached review PASS. Material archive receipt follows.
[Prospective plan](r18_crossed_design_plan.md), [validation](validation/r18_crossed_design.md).

Removing regression position terms alone does not cure the large direction
errors. Holding cost at the original anchor while retaining moving XY makes
the R15 linear fit accurate by the numerical error limits on all six inputs.
Changing measured response can therefore produce large error even without
spatial regression. The design also matters: R17 can be inaccurate on fixed
cost with moving XY. These hybrid controls do not uniquely identify physical
causes or divide error into additive percentages. Prior candidate failures stay
rejected; no runtime method is qualified by this study.

## Direction measurements

All 144 scheduled targets, 46 eligible and the same 40 supported targets remain.
The six original eligible support failures are not rescued by copied fixed XY.
The table gives all-supported median/P90 error in degrees, before admission.
The first three columns use R15 linear; fixed-XY point estimates agree among
all three methods to floating precision. The last column exposes the R17
design effect with the same fixed-anchor cost.

| Input | Fixed cost, moving XY (R15 linear) | Moving noiseless cost, fixed XY | Recorded cost, fixed XY | Fixed cost, moving XY (R17) |
| --- | ---: | ---: | ---: | ---: |
| C development | 6.590 / 25.346 | 63.705 / 143.960 | 63.705 / 143.960 | 5.592 / 15.879 |
| D development | 7.980 / 16.626 | 46.419 / 82.458 | 46.419 / 82.458 | 12.265 / 36.190 |
| C nominal | 0.554 / 6.188 | 3.617 / 57.804 | 3.617 / 57.804 | 5.615 / 80.366 |
| D nominal | 1.800 / 5.758 | 6.010 / 59.301 | 6.010 / 59.301 | 48.395 / 82.877 |
| C noisy | 0.303 / 2.086 | 71.652 / 128.548 | 70.256 / 126.344 | 2.326 / 27.169 |
| D noisy | 0.416 / 3.406 | 11.800 / 80.646 | 11.801 / 78.532 | 2.817 / 32.829 |

R15 quadratic fixed-cost/moving-XY median/P90 in row order: 7.039/38.280,
22.427/34.402, 0.679/13.535, 15.453/24.623, 1.103/5.989 and 1.441/25.358.
Previously cached fixed-cost/fixed-XY controls have medians 0.090–1.875 and
P90 0.616–6.138 degrees. Those diagonal fits were reused without refitting.

Frozen admission totals (R15 linear / R15 quadratic / R17): fixed cost with
moving design 27/46 / 21/46 / 18/46; moving noiseless cost with fixed design
18/46 for each; actual recorded cost with fixed design 13/46 for each.
Every run fails the original admitted availability/accuracy contract or has
no admitted evidence. The C development support ceiling is already 3/4, below
the 80% availability requirement; accuracy alone cannot close that criterion.
No synthetic calibration guarantee transfers to artificial crossed inputs.

Actual recorded cost with fixed design improves 26/40 directions relative to
R15 linear, 30/40 relative to quadratic, and 32/40 relative to R17; it degrades
the remaining 14/10/8 respectively. Large upper-tail errors remain. Fixed cost
with moving design improves 36/40, 35/40 and 35/40 compared with each method’s
noiseless moving/moving diagonal. Paired vectors and magnitudes are retained.

Across both fixed-design cells, all targets and verification supports, maximum
cross-method coefficient difference is 2.220446049250313e-16 and maximum mapped
raw-vector difference is 6.021370816038074e-16. This confirms that the three
methods collapse to the same DC/time/H1–H3 point fit when XY columns vanish.

## Raw verification evidence

For the eight original noisy verification supports, projected admission totals
(R15 linear / quadratic / R17) are fixed cost with moving XY 8/8 / 7/8 / 7/8;
moving noiseless cost with fixed XY 6/8 for each; actual recorded cost with fixed
XY 2/8 / 0/8 / 0/8. The two R15 linear passes are C epoch 3 and D epoch 2.
Original geometry, negative-cost and minima guards, source identities and both
historical diagnostic mismatches remain copied unchanged. These are projected
information checks, not actual fills, escapes or arrivals.

## Execution and next criterion

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r18_crossed_design_v1/`.

Sole session 43287 is terminal/reaped with exit 0, 6.579207011 seconds outer
and 5.180053881 seconds helper time. All 432 fits completed with finite results;
49 execution pins stayed stable, errors/subprocess events are empty. There were
zero new model, bag, reference or map calls. The 152 target/verification partials
preserve copied inputs, diagonal comparisons and every unavailable target.

- `prepared.json` SHA256 `dbab32885185a4ffe624d792d04e872a409097f27ef29cbbd2aa10b48f111990`.
- `ready.json` SHA256 `aa3b1910af34923cde6e0a2d51bbc243a05e27af0a6fd807f3efae5ffc1170f1`.
- `run.py` SHA256 `54298790cc07e2302d4b5cdc42548d838d52a29d62bd9eb01029f5a307e2b8b4`.
- `result.json` SHA256 `dbcd39c701db6d318fd6be2ced965390ef346bcf86361de87c55ba8d9db382de`.
- `execution.json` SHA256 `8ddb35acf5fadcb588bd2857eee3baf2db4cb5cc929b345965f5a4214cfe9a83`.

The next correction must address changing angular response over the measurement
window and raw verification under noise. Simply deleting XY or loosening the
score rule is insufficient. A shorter spatial measurement footprint and a local
profile that can change over time are concrete alternatives; neither is adopted
or qualified here. The separate full-vector admission issue is documented in
the validation record, without changing R18 gates. Independent controls and a
credible visible integrated case remain prerequisites for another comparison.

M4v12 remains CLOSED_INCOMPLETE: twelve acquisitions, nine arrivals, three
nonarrivals and four permanently unstarted delay slots. Arrival within the
evaluator-only 0.5 m global region is sufficient; GOAL_HOLD remains optional.

Branch `feature/gesc-gaussian-robustness-v2`, HEAD
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`; task changes remain uncommitted.
No physical/Pi/snapshot/V1, commit or push action occurred. No runtime is active;
full research goal remains incomplete.

## Independent review and continuation

Independent cached review PASS in1.604015667s outer (1.597297682s helper):
360 target vector/covariance compositions,432 scores,288 fixed-design agreement
pairs and all original denominators/152 partials checked without refits. Narrative
measurements match cached results. Review SHA256
`5153d0c2a8d636588ff52aca8c4a75163226fd394a15555e8bcce44ab4a61f21`;
receipt SHA256
`94d2a0f7e26a755031aa47684ede243a90cfc505276571a0e00c0fd41feb5df7`.

The next bounded diagnostic should retain the actual additive residual noise:
`y_test = model_fixed_anchor + recorded_raw - model_provenance`, with copied XY
fixed at the original anchor and all source timing/support/reference identities
preserved. This asks whether suppressing motion would leave enough information
under the recorded noise, without new model evaluations. It is a limiting
control, not a proposed stopped acquisition or independent replication. If it
still fails badly, slowing motion alone lacks support. If promising, a single
prospectively selected nonzero travel contraction can test collection feasibility.
No R19 plan, fit or runtime correction is adopted by this R18 closeout.


R18 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r18_crossed_design_v1/`:631 verified source members
in0.944628473s; manifest SHA256
`ea96665137d8a66062afd3fb067441b386f705a14d3329f2da0d1d24fe2f985b`.
This live receipt postdates the immutable archive. Scientific session43287 is
terminal/reaped0; independent cached review PASS. No runtime or estimator source
changed, and no commit or push occurred. The full goal remains incomplete.
