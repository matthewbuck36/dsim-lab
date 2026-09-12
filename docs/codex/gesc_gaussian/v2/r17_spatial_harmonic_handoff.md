# R17: spatial harmonic candidate rejected

Study COMPLETE, 2026-09-11 UTC. Candidate REJECTED.
Both independent cached reviews PASS; material closure is recorded below.
The [prospective plan](r17_spatial_harmonic_plan.md) and all frozen decisions
remain unchanged. The new pure fit is unwired; no runtime experiment occurred.

The richer model detects and estimates the independent spatially varying
synthetic signals well, but fails correlated-noise/loss-of-signal rejection.
It also fails the retained trajectory study: only 3/46 eligible recorded targets
pass its score, every run fails availability, and large noiseless moving errors
remain. This particular model and calibration rule are not a solution to the
continuous-direction objective. Its failure does not prove that every spatial
model is inadequate or separate local approximation from regularization bias.

## Implemented and source-validated

Existing `filter_node/harmonic_gesc.py` adds `fit_spatial_profile` with full x/y
interactions for all six H1–H3 coefficients, quadratic spatial nuisance, an
unregularized requested-output null-space check, and a ridge penalty only on
the twelve interactions. The actual augmented-system influence supplies HAC
covariance and the mapped raw-output score. Latest-cycle predictive gain is
retained diagnostically. It is not a runtime admission gate in this candidate.
Historical R14/R15 source is an exact unchanged byte prefix.

Sole focused session 19866 exited/reaped 0: 89/89 checks passed in 1.77s pytest,
2.569950144s outer, with nine stable pins. This covers 57 prior cases and 32 new
algebra/support cases, including output versus nuisance confounding, equivariance,
mean-SSE penalty scaling, actual influence, covariance and legacy preservation.
The checks establish implementation behavior, not research acceptance.

Core SHA256 `449f4403edef7867b11a22f1715d346158f5ff8d719ec949fde084ac18604b1a`.
New test SHA256 `875a645a8ef4c49eeddf85b2feecadd2f8ff55f2ef0834597b75a5340aae460d`.

## Independent generated controls

Sole controls session 80109 exited/reaped 0 in 16.000572940s outer; result work
time 13.873499347s and closed receipt time 15.751918414s. All 1,884 unique inputs,
2,076 episode-fit records and 4,152 public fit calls completed. Eighteen execution
pins remained stable; errors and subprocess events are empty. All inputs and
intermediate lambda/score freezes are retained, with no rerun or retuning.

The 96 separate positive calibration episodes select lambda=0.01. Capped mean
angle losses for 1e-4/1e-3/1e-2 are 20.552775/13.576789/8.316221 degrees.
Selection is saved after 576 calls, before null calibration. Four independent
199-episode noise families then freeze score cutoff=6.449624183670948 at call
2,168, before evaluation fits. The synthetic output map selects H1c/H1s.

| Fixed evaluation population | Result | Decision |
| --- | --- | --- |
| Ordinary nulls | 3/512 accepted; all three AR1, 3/128 in that family | FAIL per-family cap 2; total cap 5 passes |
| Stronger stable positives | 59/64 detected | PASS, minimum 58 |
| All accepted stable positives | 71/96; median/P90 3.360/12.295 degrees | PASS accuracy |
| Stronger spatially varying positives | 63/64 detected | PASS, minimum 58 |
| All accepted spatial positives | 78/96; median/P90 4.992/14.265 degrees | PASS accuracy |
| Exact phase/pose-confounded stress | 16/16 unavailable | PASS |
| Near-confounded stress | 16/16 unavailable | Descriptive |
| Quadratic spatial nulls | 0/64 accepted; 16 half-phase cases unavailable | PASS |
| Hard reversal/loss stress | 4/32 accepted, all four from loss-of-signal | FAIL cap 2 |
| Mature late-change looks | 0/16 accepted | PASS |

Late-change pre-transition 16/16 accepts are valid; 21/32 transient accepts are
gray. Smooth-change gray controls admit 59/64, median/P90 10.493/23.033 degrees;
quadratic-angular gray controls admit 62/64, median/P90 3.784/14.066 degrees.
These do not override hard failures. Noise cutoff calibration is limited to its
stated H1-selector generators; it is not a universal probability certificate.

## Retained trajectory measurements

Sole retained session 99659 exited/reaped 0 in 3.921781497s outer, 3.218837949s
helper. All 54 execution pins are stable; errors and subprocess events are empty.
The job performed 192 fits: four signals at the same 40 supported eligible
target matrices and eight verification supports. All 144 scheduled targets and
46 original eligible targets remain; six original excursion failures remain
unavailable. No field model, quadrature, geometry solve, bag read or new harmonic
map was executed. All 160 supported target fits and 32 verification fits are
finite; the new output null-space check does not reject these retained supports.

Direction errors below use all supported fits before score admission and the
unchanged observed-phase stationary GESC reference, including the original known
augmented contribution. The noise-free column uses recorded sensor provenance.

| Input | Supported / eligible | Recorded median/P90, degrees | Noiseless moving median/P90, degrees | Recorded score admits |
| --- | ---: | ---: | ---: | ---: |
| C development | 3/4 | 125.958 / 134.117 | 125.958 / 134.117 | 0/4 |
| D development | 6/7 | 80.256 / 161.536 | 80.256 / 161.536 | 1/7 |
| C nominal confirmation | 5/6 | 30.624 / 115.936 | 30.624 / 115.936 | 0/6 |
| D nominal confirmation | 4/5 | 79.008 / 147.380 | 79.008 / 147.380 | 1/5 |
| C noisy confirmation | 11/12 | 83.166 / 136.462 | 92.925 / 142.285 | 1/12 |
| D noisy confirmation | 11/12 | 31.632 / 155.181 | 9.759 / 167.012 | 0/12 |

The three admitted recorded errors are 13.569, 12.180 and 0.615 degrees. Every
recorded run fails the original availability gate, or has no admitted evidence.
Against R15 recorded fits on the same 40 supports, R17 improves 12 and degrades
28 relative to linear; it improves 16 and degrades 24 relative to quadratic.
These paired comparisons do not compare synthetic cohorts with different seeds.

Both noiseless moving geometry interpretations admit 10/46 targets. Fixed-anchor
controls admit 30/46, with all-supported per-run median/P90 ranges still
0.090–1.875 / 0.616–6.138 degrees. Only C nominal fixed-anchor passes its per-run
availability and accuracy gates; all other fixed-anchor inputs fail availability.
The counterfactual holds both model position and copied fit XY fixed, so it
changes cost geometry and nuisance design. Its small error is diagnostic and
does not qualify a continuous-motion method or transfer noise calibration.

Projected verification passes 1/8 recorded supports (D epoch 2 only), 6/8 under
either noiseless moving interpretation, and 8/8 fixed-anchor. C epochs 1 and 4
remain below cutoff without noise. Original geometry/minima/negative-cost guards
and historical diagnostic mismatches remain unchanged. These projected signal
checks do not create any recorded fill, escape or arrival.

## Evidence and next incomplete work

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r17_spatial_harmonic_v1/`.

- `source_ready.json`, before copy and patch: held additive implementation.
- `focused_prepared.json`, `focused_result.json`, `focused_console.log`:
  exact source test argv and terminal outcome.
- `synthetic_inputs.jsonl.gz`, `synthetic_episodes.jsonl`, lambda and score
  freeze files: complete independent generation and intermediate decisions.
- `synthetic_result.json` SHA256
  `ffb288abb2d853001f43b32f1d4e710d93b73695b8993d3655b5124a19022ba2`;
  receipt `0aa0e0bfb21a4d407c962fa9ec1240aa9c0156b6ed6467e604ebf97149b2e933`.
- `retained_result.json` SHA256
  `46a539884ef412a2d02ee63ce79823ba07f51e42e21b1c61e7e21189616f3d76`;
  execution `c395c4899381cf55443f1499aac9717f07561493e0ea7b6e2ab69c8f0737fd5b`.
- `retained_partials/`: all 144 target records and eight verification records.
- [Validation record](validation/r17_spatial_harmonic.md): exact commands,
  preparation, terminal outcomes, independent reviews and material closure.

Independent cached reviews PASS: synthetic in 2.608136548s with 72,435
arithmetic/identity assertions; retained in 1.381493s with 91,179 assertions
and 209 stable selected inputs. These include all original populations,
separate freezes, 152 retained partials, 160 q/Cq/error compositions and 192
retained score calculations, without any refit or model evaluation.
Synthetic review SHA256:
`9648dbba34a22e4606dc2f781d7c381500c5d7a30ceaf855dbf444b45b6a7f16`.
Retained review SHA256:
`1e088971bb0e7b58e8e669702ab9be504017fec99d0969f40bda67950755608f`.

The next method/collection change must address persistent moving-fit bias and
the separate loss-of-signal/noise rejection issue. More permissive confidence
alone cannot fix the large unscreened direction errors. A bounded change to
motion per measurement is a concrete next hypothesis, with the noise and travel
time tradeoffs measured. Before attributing the benefit uniquely to physical
motion reduction, a crossed cached control can hold cost fixed while retaining
moving XY nuisance, and vice versa: R16/R17 fixed-anchor controls changed both.
This can distinguish a regression-design effect without new field queries.
No R18 plan, runtime correction or simulation is adopted
here. Independent controls and credible visible integrated development remain
required before another frozen comparison.

M4v12 remains CLOSED_INCOMPLETE with twelve complete acquisitions and four
unstarted delay cases; nine observed arrivals and three nonarrivals are unchanged.
Entering the evaluator-only 0.5 m global region suffices; GOAL_HOLD is optional.

Branch `feature/gesc-gaussian-robustness-v2`, HEAD
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`; task changes remain uncommitted.
No physical/Pi/snapshot/V1, commit or push action occurred. No runtime is active;
all three R17 execution sessions are terminal/reaped. The full goal is incomplete.


R17 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r17_spatial_harmonic_v1/`:628 verified source members
in1.097555136s; manifest SHA256
`26bb7b63c3a09d2a523fcad9e61dd463c0722488b973855eff3a6c27bcec2624`.
This live receipt postdates the immutable archive. All three scientific/source
sessions are terminal/reaped0; both independent cached reviews pass. Candidate
remains REJECTED and unwired. No runtime, commit or push was performed.
