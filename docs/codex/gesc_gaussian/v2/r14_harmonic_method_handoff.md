# R14 harmonic prototype: rejected for inadequate availability

Study COMPLETE,2026-09-11 UTC; independent synthetic and retained reviews PASS.
Material checkpoint receipt follows below. The candidate FAIL is preserved under the unchanged
[prospective plan](r14_harmonic_method_plan.md). No runtime integration or new
simulation is released. The full research goal remains incomplete.

## Implementation and measured decision

The new pure `filter_node/harmonic_gesc.py` owner fits three angular harmonics,
position/time nuisance terms and first-harmonic position interactions. It uses
SVD identifiability checks, held-out-cycle prediction and a descriptive HC3
uncertainty proxy. It is unwired to ROS, the controller and supervisor; existing
GESC/Gaussian methods and selectable legacy behavior are unchanged.

Twenty-four deterministic mathematical checks passed in0.10s pytest,
0.768110724s outer. These establish implementation behavior, not empirical
reliability. The independent synthetic study completed1468 episodes in8.220024s:

| Measurement | Result |
| --- | --- |
| Null calibration |199 episodes per four noise laws;796 total |
| Separate null false accepts |0/128 per law;0/512 total |
| Stable amplitude0.0075 detection |0/32 |
| Stable amplitude0.015 detection |5/32 |
| Stable amplitude0.030 detection |21/32 |
| Stronger-signal criterion |26/64; FAIL against90% |
| Accepted coefficient-direction error |26 points; median4.876 degrees/P908.623 degrees |
| Hard reversal/loss false accepts |0/32 |
| Exact/near phase-position confounding |32/32 unavailable |

The cutoff0.20211134529019842 came from the maximum AR1 null episode score;
all declared looks and populations remain retained. It is not a real-robot
confidence guarantee. Zero false accepts per128 trials has one-sided95% upper
bound2.313% for that declared family, not1%.

The failure is specific: all31 curved positive episodes failed the information
screen (fraction0.05113 versus required0.10). Of64 stronger positives,18 were
unavailable and20 failed held-out prediction. SNR rejected no additional cases
after CV. Neither a clean job nor accurate accepted directions satisfies the
missing detection/availability target.

The retained job completed all144 scheduled targets and eight original noisy
verification supports in12.346496s. Of46 originally eligible targets,39 failed
angular information, six exceeded the0.5m support excursion, and one fit failed
the score/proxy gate: **zero usable new estimates**. Recorded fallback errors
remain unchanged, with new-method averaging availability correctly kept at zero.
The only supported ungated fit had0.982-degree error (C/noise target12), but
failed CV/SNR; it supplies no broader direction-quality claim.

Every noisy verification support also failed angular information. R13 geometry,
minima/negative-cost guards and historical replay mismatches were preserved.
The prototype does not fix noisy escape or qualify a new accepted fill.

## Next substantive work

Keep this candidate and all results failed. The next method iteration must
address the model's dimensionality and which uncertain coefficient combinations
actually affect the required GESC direction. Requiring uniformly strong
information for all six harmonics may discard a more identifiable output
functional; this is a hypothesis to measure, not a demonstrated correction.
First-harmonic position interactions can also be poorly distinguishable from
the angular signal over short curved arcs. A reduced or regularized model needs
explicit approximation assumptions and independent changing-profile controls.

Separately address the lost power of minimum held-out gain under correlated
noise. Consider uncertainty in the required output and noise dependence before
choosing another decision rule. Do not simply lower SNR, replace the0.10 guard
with an empirically convenient value, extend a timeout, or reclassify unavailable
fits. Keep all existing full-goal criteria and original denominators.

A new prospective controlled method study must precede runtime integration.
Promising corrected components still require a bounded visible integrated case
and a frozen full comparison. V12's four delay runs stay unstarted in its closed
version; no new matrix is authorized by this handoff alone.

## Evidence and recovery

Work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r14_harmonic_method_v1/`.
The [validation record](validation/r14_harmonic_method.md) contains exact commands,
limits, counts, failures and receipt hashes. Read these files before acting:

- `focused_result.json`:24 passes, stable source/test bindings.
- `synthetic_result.json`, `synthetic_receipt.json`, `synthetic_review.json`:
  all1468 episode/2936-look records; independent cached review.
- `synthetic_inputs.jsonl.gz`: generated raw inputs preserved without regeneration.
- `retained_result.json`, `retained_partials/`, `retained_execution.json`,
  `retained_review.json`: all144 target dispositions and eight original verification
  projections; independent review PASS58 checks in0.261438s.
- `retained_prelaunch_error.json`: root wrapper key error before subprocess
  creation; retained numerical job ran exactly once after correcting the key.

Source SHA256 `bb2f9dc500678123ffa843dd59607daccc95023e183e0f609f84f4f88966bfe6`.
Synthetic result `d36514a1f06a55d555721d2f8e2cdafb74833a1d6184715c09c495ceaf36f99d`.
Retained result `14c29685d2135d139320729aa393084ffc8e7d7caf97e6ffb2f3421bc5b2b5d6`.
Sessions44490 and21676 are terminal/reaped0; no simulation is active.

Branch `feature/gesc-gaussian-robustness-v2`, HEAD
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`; all task work remains uncommitted.
No physical, Pi, snapshot, V1, commit or push action was performed.

R14 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r14_harmonic_method_v1/` contains616 verified source
members, completed in0.990166671s; manifest SHA256:
`4da7470b0cdff23d384033e88bee6e97a5230b6a2a9329005f51aac6e1b20237`.
This live receipt postdates the immutable archive. Study COMPLETE, candidate
REJECTED; no active simulation, commit or push. Full research goal remains open.
