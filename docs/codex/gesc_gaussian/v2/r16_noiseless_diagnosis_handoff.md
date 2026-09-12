# R16: motion-related direction error isolated in retained model controls

Study COMPLETE, 2026-09-11 UTC. Independent cached review PASS; material
closure is recorded below. The [prospective plan](r16_noiseless_diagnosis_plan.md)
remains frozen. R15's two candidates remain REJECTED and unwired to runtime.

Removing measurement noise does not resolve the large direction errors of the
moving fits. Holding model and fit position fixed at each original anchor, with
the same recorded sensor-phase/time history, gives small errors across all six
inputs. This supports a motion-related model or identifiability problem in the
selected field. The fixed-anchor control changes both cost geometry and copied XY nuisance
design. It does not uniquely identify omitted spatial coefficients,
harmonic truncation, or nuisance projection as the cause, and does not establish
a corrected continuous-motion estimator.

## Reconstruction and direction measurements

The actual raw-cost provenance model reproduces all four noise-free recordings
to RMS 1.36e-15 through 4.96e-15 V. Every run passes the unchanged reconstruction
premise. Residual RMS in noisy C and D is 0.014951681 and 0.015004140 V,
respectively, consistent with the selected Gaussian standard deviation 0.015 V.
These are selected-path reconstruction results, not general model qualification.

There are 144 original scheduled targets, 46 eligible, and the same 40 supported
eligible matrices as R15. Six eligible excursion failures remain unavailable.
The following median/P90 direction errors use all supported matrices before
signal admission, relative to the existing observed-phase stationary GESC
reference. The first three columns use the linear spatial variant. Fixed-anchor
direction results agree between the linear and quadratic variants to roundoff.

| Input | Supported / eligible | R15 recorded, degrees | Noiseless at recorded sensor provenance, degrees | Noiseless fixed anchor, degrees |
| --- | ---: | ---: | ---: | ---: |
| C development | 3/4 | 68.384 / 155.349 | 68.384 / 155.349 | 0.115 / 3.558 |
| D development | 6/7 | 46.907 / 91.675 | 46.907 / 91.675 | 1.875 / 6.138 |
| C nominal confirmation | 5/6 | 4.318 / 56.001 | 4.318 / 56.001 | 0.148 / 0.616 |
| D nominal confirmation | 4/5 | 14.857 / 75.119 | 14.857 / 75.119 | 0.337 / 0.912 |
| C noisy confirmation | 11/12 | 68.170 / 111.882 | 69.213 / 114.883 | 0.090 / 0.769 |
| D noisy confirmation | 11/12 | 16.261 / 98.554 | 17.197 / 96.337 | 0.194 / 4.048 |

Quadratic moving-fit noiseless median/P90 errors in the same row order are
155.493/157.352, 77.358/168.940, 6.569/88.950, 37.033/143.589,
8.731/154.094 and 20.929/146.728 degrees. Noise removal improves some quadratic
medians substantially but leaves large upper-tail errors. Adding spatial
quadratic nuisance terms alone therefore does not resolve the retained problem.

The other moving control evaluates the model at synchronized base XY instead
of recorded sensor XY. Most aggregate direction results are nearly identical.
Sensor-position discrepancy is about 34–37 micrometres RMS by run; rare sharp
cost differences reach 0.063714 V, so alignment is not literally zero. Complete
per-run residual distributions, paired changes, covariance and admission reasons
are retained in result.json and partials/.

Frozen R15 admission yields 15/46 linear and 11/46 quadratic usable targets for
each noiseless moving control, and 31/46 linear and 30/46 quadratic for the
fixed-anchor control. These counterfactual counts are descriptive; they do not
inherit the noisy synthetic calibration or qualify a runtime method. In
particular, small fixed-anchor errors do not erase the original availability
failures or authorize mandatory stopped sweeps.

## Verification is separately sensitive to noise

For each spatial variant, the projected raw-information rule passes:

- 1/8 actual noisy R15 supports: only D epoch 2;
- 6/8 noiseless moving supports under either geometry interpretation: C epochs
  2 and 3 and all four D epochs; C epochs 1 and 4 still fail;
- 8/8 noiseless fixed-anchor supports.

All 48 counterfactual verification fits are finite. These are projected signal
checks only. Original geometry, minima, negative-cost guards and the two
historical terminal-diagnostic mismatches are preserved. No counterfactual
creates a recorded fill, escape or global arrival. Noise matters for verification
even though removing it alone does not cure broad moving direction error.

## Execution and retained evidence

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r16_noiseless_diagnosis_v1/`.

Sole session 4214 is terminal/reaped with exit 0: 15.398277635 seconds outer,
14.172489873 seconds in the helper. All 71 execution pins are stable; errors and
subprocess events are empty. Six detached models used 34,520 scalar evaluations,
including 11,702 fixed-anchor evaluations, and 288 fits. Target support uses
total 9,775 samples; verification uses 1,927. The two source-geometry model paths
share 11,409 unique complete source identities, without cross-run cache reuse.
Bounds were 36,000 model evaluations, 288 fits and 120 seconds inclusive.

- `prepared.json`: frozen source/input pins and exact command;
  SHA256 `98309ced3affadc05191bd1838d94858aa7f83a900544eec529400942ff1bbad`.
- `execution.json`: actual argv, terminal exit and elapsed time;
  SHA256 `9efbc1a145c58455ccf09f9f8e3e5a7573720430e3858829c9c02ca99aa4a938`.
- `result.json`: all six runs, 144 targets, eight verification supports and
  reconstruction diagnostics;
  SHA256 `f0028b107117ae5a36bf44388496d475174a5ecb40a6972261a8c4e9cb3c0d6a`.
- `partials/`: original target identities, copied counterfactual inputs, fits,
  cached map compositions and unique-source residuals.
- [Validation record](validation/r16_noiseless_diagnosis.md): exact commands,
  static review, execution, independent review and material closure receipts.

Independent cached review PASS in 0.880103918s outer (0.860566120s helper),
with 181 stable selected review inputs. It checks 164 partials, all original
populations and summaries, 240 cached q/Cq compositions and model/fit accounting;
14,804 assertions include per-source residual arithmetic and identity checks.
No numerical owner was imported or executed. Review SHA256:
`081909873b48553156321a8253942afccebde8f37d4f080dfb514a38c0ac9760`.

No production source change, new reference quadrature, geometry solve, bag read,
noise regeneration or ROS/Gazebo execution occurred. All original R15 fits and
reference maps were reused where specified, with no rerun of recorded fits.

## Next incomplete criterion

Prospectively choose and test a method or continuous-collection change that
addresses motion-dependent angular response and identifiability. R14's richer
interaction model lost identifiability; R15's reduced model retains deterministic
moving error. Simply relaxing confidence gates, pooling more cycles or adding
harmonics is not justified as a correction by these results. A promising method
still needs independent controls and a bounded visible integrated case before
another frozen comparison. No R17 plan or runtime change is adopted here.

M4v12 remains CLOSED_INCOMPLETE: twelve complete acquisitions, nine observed
arrivals, three nonarrivals, and four unstarted delay cases. Arrival within the
existing evaluator-only 0.5 m global region suffices; GOAL_HOLD is optional.
This offline study does not change any of those recorded outcomes.

Branch `feature/gesc-gaussian-robustness-v2`, HEAD
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`; task changes remain uncommitted.
No physical/Pi/snapshot/V1, commit or push action occurred. The full research
goal remains incomplete.


R16 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r16_noiseless_diagnosis_v1/`: 624 verified source
members in 0.990254893s; manifest SHA256
`e28bbb50514e475fa699d698715885d52339f6da8082b02fa7ff39bf534998bf`.
This live receipt postdates the immutable archive. All retained measurements and
candidate failures remain preserved. No new runtime, commit or push occurred.
