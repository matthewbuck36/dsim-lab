# R19: retained noise permits accurate fixed-anchor direction, but verification still fails

Study COMPLETE; independent cached review PASS. [Prospective plan](r19_retained_noise_plan.md),
[validation](validation/r19_retained_noise.md). Material archive receipt follows.

Suppressing motion in the diagnostic while retaining the actual recorded additive
residual gives small direction errors, including on both noisy runs. However,
only two of eight raw-information verification projections pass the unchanged
rule. The prospective motion-only sufficiency decision therefore FAILS for this
method, evidence contract and realized noise. This does not prove that every
nonzero travel contraction fails, or establish a qualified continuous controller.

## Measurements

All144 scheduled/46 eligible/40 supported targets remain. The six original
eligible support failures are preserved. No noisy target is removed from the
all-supported error statistics. Each copied cost is
`model_fixed_anchor + recorded_raw - model_provenance`, with fixed XY at the
original anchor and unchanged source timestamps, phase and sample count.

| Input | All-supported median / P90 error, degrees | Frozen admitted / eligible | Admitted contract |
| --- | ---: | ---: | --- |
| C development | 0.115 / 3.558 | 2/4 | FAIL |
| D development | 1.875 / 6.138 | 4/7 | FAIL |
| C nominal | 0.148 / 0.616 | 5/6 | PASS |
| D nominal | 0.337 / 0.912 | 3/5 | FAIL |
| C noisy | 1.823 / 13.777 | 6/12 | FAIL |
| D noisy | 3.235 / 7.481 | 2/12 | FAIL |

Both noisy all-supported direction gates PASS (median<=30/P90<=60degrees), but
frozen signal/prediction admission totals22/46 across all six runs. Only C nominal
passes the full admitted per-run contract. C development's original support
ceiling is3/4, below80%, independently of accuracy. R15's independent
quadratic-null rejection remains unchanged; these results do not qualify it.

Raw verification passes2/8: C epoch1 and D epoch2. Four reject on score alone,
one on prediction alone (C3), and one on both (C4). All original geometry,
negative-cost, minima and source guards and both historical diagnostic mismatches
remain unchanged. No projected pass is a recorded fill, escape or arrival.

| Support | Raw score | Latest-cycle predictive gain | Frozen admission |
| --- | ---: | ---: | --- |
| C 1 | 5.799535 | 0.210126 | PASS |
| C 2 | 4.420543 | 0.002420 | FAIL |
| C 3 | 6.319900 | -0.006484 | FAIL |
| C 4 | 4.884422 | -0.056927 | FAIL |
| D 1 | 4.319398 | 0.119242 | FAIL |
| D 2 | 6.463670 | 0.076717 | PASS |
| D 3 | 3.928686 | 0.019854 | FAIL |
| D 4 | 4.487847 | 0.119025 | FAIL |

The frozen cutoff is5.638621374336838 with strictly positive latest-cycle gain.
No cutoffs, support gates, sample sets or old outcomes were retuned.

## Execution and review

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r19_retained_noise_v1/`.

Sole scientific session51515 is terminal/reaped0:3.070531238s outer,
2.353673327s helper. All48 fits are valid,58 execution pins remain stable,
errors/subprocess events are empty. No new model, bag, reference, map or diagonal
fit calls. All152 target/verification partials and11,702 transferred sample uses
remain retained. No numerical owner or runtime source changed.

A root prelaunch wrapper initially looked for `ready.json.command`, but this
receipt stores `command_key=prepared.json.command`. That KeyError occurred before
any scientific command, logs or fits. `prelaunch_wrapper_failure.json` preserves
it. Correcting only the wrapper's receipt lookup allowed the sole scientific
execution; no scientific experiment was retried.

Independent cached review PASS in0.944265s:214 stable selected inputs,
all residual-transfer rows,48 score/prediction gates,40 vector/covariance/error
compositions,720 cached diagonal comparisons and all denominators reviewed
without refits, model calls, bag reads or numerical owner imports.

- `run.py` SHA256 `195040b45d0b99cc28bb46d783f56fb7b1c20cdee586835942369d255f38723c`.
- `prepared.json` SHA256 `dd29198863ac8e94538a2968cc1825b51bb0c3c768d5dd68c08d9865a447ae61`.
- `ready.json` SHA256 `8990973b975343b3c58d570b78b254d3355a1ec8866eea9df242f15872447028`.
- `result.json` SHA256 `1b48fa90ffb9a2c8c5623873ca3b676b668ef9c86b925fc7d99983e623f9e871`.
- `execution.json` SHA256 `741703d2e72ea19f6861b9c0a4eb773040d9565cc69b90ac83c9f0b6abb1c977`.
- `cached_review.json` SHA256 `be3738c589f31926d904e2d46e85daca474dba13049af082e6149b8cfb617f3b`.
- `cached_review_receipt.json` SHA256 `6253cbea2ec13d50945e267d470e4e229a8ccc1d4216c7ac2d23f44c2e42fa4a`.

## Next method decision

The fixed-anchor/noise result supports reducing the spatial footprint as a
SEARCH-direction hypothesis. It also shows that simply reducing motion does
not close this raw-verification contract. The separate purpose audit in the
validation record matters: angular variation or H1 information does not certify
a spatial minimum, and a valid minimum can lack it. Cost consistency alone is
also insufficient because flat, sloping or saddle fields must not be accepted
as isolated wells.

Next work should prospectively separate direction confidence for the full
augmented steering vector from evidence of a local raw-field well. A minimum
verifier needs phase-comparable spatial excitation and a statistically supported
unclipped curvature/outward-rise test, using existing evidence/fit/controller
owners. Independent flat, slope, saddle, noisy well and changing-field controls
must precede a bounded visible integrated case. This is a proposed method
redesign, not an implemented or qualified replacement. No R20 plan or runtime
launch is adopted by this closeout. The original full goal is still incomplete.

This retained-noise transfer is conditional on the selected additive noise model
and uses one realized sequence, not independent replication. It is a limiting
control, not a proposed mandatory stopped sweep. Global-region arrival remains
sufficient; GOAL_HOLD is optional. V12 remains CLOSED_INCOMPLETE with nine
arrivals, three nonarrivals and four permanently unstarted delay slots.

Branch `feature/gesc-gaussian-robustness-v2`, HEAD
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`; task changes remain uncommitted.
No physical/Pi/snapshot/V1, commit or push action occurred. No runtime is active.


R19 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r19_retained_noise_v1/`:634 verified source members
in0.902510378s; manifest SHA256
`f7dd55bf5acb4eddcce25e51400f72b6ee865de5aa332228679364e4a015212a`.
This live receipt postdates the immutable archive. Sole scientificsession51515
is terminal/reaped0; independent cached review PASS. No estimator/runtime source,
physical/Pi/snapshot/V1, commit or push changes. Full goal remains incomplete.
