# R15 reduced harmonic study: improved signal detection, both candidates rejected

Study COMPLETE,2026-09-11 UTC; independent synthetic and retained reviews PASS.
Material closure receipt follows below. Both candidates remain REJECTED under the unchanged
[prospective plan](r15_reduced_harmonic_plan.md). Source is unwired to runtime;
no simulation was launched. The full research goal remains incomplete.

## Implemented and measured

The existing harmonic owner now offers a separate reduced fit with linear or
quadratic spatial nuisance terms, three angular harmonics, physical-time
Bartlett covariance and latest-cycle prediction. The existing reference owner
has an exact analytical harmonic-to-GESC map for the original observed phase.
Prior entrypoints remain selectable and behaviorally unchanged.57 focused
checks passed in1.58s pytest/2.269874s outer; these are mathematical evidence.

One independent synthetic job generated1628 inputs and evaluated both fixed
variants:3256 variant episodes/6512 looks,20.211445s outer. Own null cutoffs
were frozen independently for each variant. No tuning followed the results.

| Measurement | Linear spatial | Quadratic spatial |
| --- | ---: | ---: |
| Strong stable detection, amplitude>=0.015 |60/64 PASS |53/64 FAIL |
| Separate ordinary null false accepts |0/512 |0/512 |
| Accepted positive direction count |67 |57 |
| Accepted direction median/P90 degrees |3.043/8.522 |2.714/8.615 |
| Quadratic spatial null false accepts |7/64 FAIL |1/64 PASS |
| Half-phase curvature null |6/16 accepted |16/16 unavailable |
| Hard reversal/loss false accepts |0/32 |1/32 |
| Mature late-change false accepts |0/16 |0/16 |

Linear fails only the spatial false-acceptance criterion. Quadratic fails only
strong-signal detection; nine strong episodes fail latest-cycle prediction and
two fail the score. All five missed amplitude0.030 cases are curved, with scores
above cutoff at both looks. This identifies a prediction-gate power problem on
those independent controls. It does not prove that lowering the gate is valid
on the robot trajectories. Gray smooth changes/partial-cycle transients remain
gray; source timing and accepted current-time errors are retained.

One retained job completed in16.349237s outer, using the same144 scheduled
anchors/46 eligible targets and eight original noisy verification supports.
40 eligible target fits map to GESC in each variant; six supports exceed0.5m.
Only10/46 linear and6/46 quadratic estimates pass their frozen admission rules.

| Retained input | Eligible | Linear accepted; median/P90 degrees | Quadratic accepted; median/P90 degrees |
| --- | ---: | --- | --- |
| C development |4 |0; unavailable |0; unavailable |
| D development |7 |2;16.352/17.021 |0; unavailable |
| C nominal |6 |3;0.812/3.616 |3;3.380/5.931 |
| D nominal |5 |2;10.103/15.326 |0; unavailable |
| C noise |12 |2;4.761/5.095 |2;3.672/3.992 |
| D noise |12 |1;4.285/4.285 |1;1.482/1.482 |

Every per-run admitted-method result fails availability. The unscreened fits
also have large errors on several inputs, so unavailable estimates cannot simply
be promoted. Recorded fallback remains explicit and is never counted as new
averaging confidence.40 harmonic maps and40 known-term integrals were shared
across variants; no field truth was queried for the fits.

Both variants pass the proposed raw-information rule only on D/noise epoch2
among eight original verification attempts. Original geometry/minima/negative
cost and historical replay mismatches are retained. This is a projected signal
admission; no Gaussian fill, escape or arrival was newly established.

## Next substantive action

Separate retained model bias from measurement noise before another estimator
or gate change. A prospective bounded diagnostic can reconstruct noise-free raw
cost on the exact recorded pose/phase through the existing independent model
owner, then compare the same fitted directions with the original stationary
GESC references. This would be a development counterfactual with evaluator-only
truth, not runtime access to the field or a new qualification of old records.
No such job is yet adopted or executed; first resolve actual binding, cost
sign, sensor/base geometry and source alignment from current owners.

On independent controls, the quadratic latest-cycle predictive projection loses
power during curved motion. A future change detector should preserve earlier
nuisance information or explicitly assess cycle-to-cycle profile change, with
separate calibration and unchanged reversal/loss controls. The retained errors
also require testing local-profile approximation and motion/phase excitation;
statistical uncertainty alone cannot cover omitted spatial variation. Do not
simply reduce cutoffs, relabel difficult targets, or launch another matrix.

Promising components still require bounded visible integrated development,
then a frozen full comparison. Global-region arrival remains sufficient and
GOAL_HOLD optional. V12 remains CLOSED_INCOMPLETE; its four delay slots are
permanently unstarted in that version.

## Evidence and recovery

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r15_reduced_harmonic_v1/`.
Read [validation](validation/r15_reduced_harmonic.md) for exact argv, budgets,
receipt hashes and any post-archive closure receipt. Read the complete products
before new work; never regenerate them to recover context.

- `focused_result.json`:57 passes and seven stable source/test/plan/env pins.
- `synthetic_result.json`, `synthetic_receipt.json`, `synthetic_review.json`:
  complete paired study and independent cached review.
- `synthetic_inputs.jsonl.gz`, `synthetic_episodes.jsonl`: raw inputs and every fit.
- `retained_result.json`, `retained_partials/`, `retained_execution.json`:
 144 targets/eight verification supports, both variants and original identities.
- `retained_preparation_before_key_fix/`: unexecuted helper/manifests retained
  before correcting the final eligible-count field lookup. The only actual
  retained job used `retained_prepared_v2.json` after independent static review.

Synthetic result SHA256
`e566789b9247cff82622449c45bf07c219eecb5f4cec0e749d5758f17077d6fe`.
Retained result SHA256
`954dc9e25bbe9c8436bca0e43156b6364ad6f33340d79ebff129c4b8e02e4960`.
Execution sessions82259,21463,1768 are terminal/reaped0. No application runtime
is active. Branch `feature/gesc-gaussian-robustness-v2`, HEAD
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`; all task work remains uncommitted.
No physical/Pi/snapshot/V1, commit or push action was performed.

R15 material closure: context validator, diff check and existing checkpoint PASS.
Archive `checkpoints/r15_reduced_harmonic_v1/`:621 verified source members,
1.113313046s; manifest SHA256
`ed0a9afa2a38cedb6786001e76b0a788e86b829682663bfc96878dc72c0ae06d`.
This live receipt postdates the immutable archive. Both candidate failures and
all raw/cached measurements retained; no simulation, commit or push performed.
