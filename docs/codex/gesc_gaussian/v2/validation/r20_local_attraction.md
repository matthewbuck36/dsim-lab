# R20 local-attraction validation

Status: COMPLETE and independently reviewed. Candidate
REJECTED under the unchanged prospective strong-positive requirement. No runtime
selection or matrix is qualified by this component study.

Source owners: additive `fit_affine_gesc_field` in harmonic_gesc, empirical
q/B covariance and attraction decision in basin_estimator, opt-in 28-second probe
helpers in centered_verification. Existing numerical entrypoints, tracking modes,
8/12/20-second runtime timing and selected controller limits remain unchanged.
No runtime mode selects these new helpers. Static independent reviews found no
blocking mathematical or component-preparation defect.

## Finite execution

All exact argv/environment setup, elapsed times and output pins are retained in
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r20_local_attraction_v1`.

| Job | Sole session | Result | Outer seconds | Evidence |
| --- | --- | --- | ---: | --- |
| Focused and kinematic | 13069 | exit 0, 208 passed | 9.034610872 | focused_execution.json, focused.log |
| Fixed synthetic controls | 57261 | exit 0, complete; candidate rejected | 61.848894955 | controls_execution.json, controls_result.json |
| Selected-field component | 69180 | exit 0, complete | 28.172101010 | component_execution.json, component_result.json |

All sessions were polled to terminal/reaped exit 0. Bounds were 85s INT plus5s
kill (90 total),235+5 (240), and175+5 (180), respectively. One BLAS thread.
The source bundle selected the R14/R15/R17 numerical tests, all three R20 files
and centered-verification runtime regressions through the retained simulation
interface environment. No test or empirical attempt failed at execution; the
scientific candidate failed its acceptance criteria. There were no replacement
scientific attempts. Controls retained131 execution pins; component pins and
all before/after checks are in their results. No model/refit is part of review.

## Tracking measurement

All three fixed midpoint-unicycle cases passed with840 descriptive samples each.
Maximum tracking errors were 0.0000000650,0.025047255 and0.025031617m; final
errors0.0000000447,0.000071299 and0.000056235m. Longest stopped interval was zero.
Maximum linear command across cases0.039145250m/s; maximum yaw command
0.416045809rad/s, below0.1/0.5 limits. All phase sectors were sampled. This is
ideal kinematics, not Gazebo entry, lease, transport or hardware validation.

## Independent exact-model controls

All1660 prescribed inputs and4980 fits are retained. Calibration796 episodes
(2388 full/half fits) completed and was saved before evaluation inputs were
created. Frozen k=16.0581898910766; half-change cutoff12.75018952698795.
The generator config/hash/draw order was saved prospectively in the linked
preparation appendix. No thresholds were changed after observing results.

| Population | Accepted / scheduled | Fixed criterion |
| --- | ---: | --- |
| Flat/slope/saddle/repelling negatives | 0/512 | PASS |
| Attracting gain0.5 | 0/64 | descriptive |
| Attracting gain1 | 1/64 | part of strong-positive gate |
| Attracting gain2 | 49/64 | part of strong-positive gate |
| Combined strong positives | 50/128 | FAIL; required116 |
| Phase-only | 0/64 | PASS |
| Half-window loss/reversal | 0/64 | PASS |
| Exact-confounded | all32 unavailable | PASS |

All per-noise and per-negative-type false-accept gates pass. Accepted positive
zero error median0.002076459m/P900.004190108m passes its conditional accuracy
gate. This accuracy does not compensate for missed positive fields. The fixed
candidate is rejected. The uncertainty calibration covers stated noise on an
exact affine angular model; it does not bound arbitrary field/model error.

## Selected-field measurements

Same eight retained noisy candidate identities; new28-second trajectories and
fresh declared Gaussian realization.48 fits,136 independent stationary truth
locations and203171 model calls completed within cap. All eight tracking cases,
all eight full noiseless/noisy fits and all eight center/stencil references are
available. All16 attraction decisions reject `restoring_response_not_established`.

| Candidate | Truth largest symmetric-Jacobian eigenvalue | Max sampled path affine residual |
| --- | ---: | ---: |
| C1 | -0.554479771 | 0.594352053 |
| C2 | -0.027074875 | 0.341171420 |
| C3 | -0.023139717 | 0.346053544 |
| C4 | -0.014896033 | 0.348221942 |
| D1 | 0.018532745 | 0.009157451 |
| D2 | 0.018369440 | 0.070119555 |
| D3 | 0.020480538 | 0.009405890 |
| D4 | 0.008861001 | 0.248182585 |

All four D centers have nonzero stationary raw-GESC direction and a positive
largest symmetric-Jacobian eigenvalue. They do not meet the adopted sufficient
local-contraction condition at the center. This does not prove absence of any
nearby attracting state or establish closed-loop unicycle stability. C candidates
also show substantial variation beyond the affine field model over this path;
path residual maxima reach0.594352. Noiseless q/B estimation errors remain, so
noise threshold adjustment alone cannot justify this verifier. The two finite
stencil scales and quadrature receipts are numerical diagnostics, not complete
bounds on spatial truncation error. Original recorded results are unchanged.

## Remaining work and recovery

The next method question is verification of persistent trajectory trapping for
Gaussian escape; recurrence need not imply a stationary raw-GESC field zero.
That question is not implemented or qualified here. Keep raw-cost ranking and
full augmented SEARCH direction confidence as separate requirements. Do not
reduce the frozen R20 thresholds or claim detector/control success from its
negative rejection result. A prospective revision, component evidence and one
credible visible integrated case still precede any new16-run comparison.

No Gazebo/selected ros_esc runtime remained in the post-execution procfs snapshot.
No hardware/Pi/snapshot/V1/commit/push work occurred. Branch remains
`feature/gesc-gaussian-robustness-v2`,HEAD3369cfc83a64ff5d8354827fd5310caaf0c8e945;
all task changes are uncommitted. Context/diff/checkpoint and material archive
receipt follow closure review.

## Independent cached review and closure

Controls review_v2 PASS67,437 assertions in7.715970s;138 pins stable. It checked
all1660 gzip input hashes/specifications,4980 retained fits,796 calibration
records,2388 error scores and all cached covariance/hull/zero decisions without
production imports, fits, generated replacements or model calls. The first
review computed its checks but failed JSON serialization on a NumPy bool after
7.372638s; its helper, partial output and traceback are retained. The separately
named v2 review corrected serialization and made one bounded cached pass.
This was a review-output failure; the sole scientific controls job was not rerun.

Calibration maxima by full/first/second windows are7.598093/13.814683/16.058190;
the adopted common k is dominated by second-half AR1 calibration. Full-window
uncertainty is then conservative:75 positive episodes fail restoring margin,
66 fail zero-region containment,1 fails half consistency and50 pass. No alternate
cutoff was scored or adopted. This diagnoses the fixed synthetic failure; actual
field incompatibility remains separately evidenced by the component.

Selected-field cached review PASS1562 checks in1.151751s; source/input pins
stable. Verified all8 identities,48 full/half fits,136 qualified truth locations,
152 partials,203171 raw-model calls, cached finite-difference Jacobians and error
summaries. No fit/model/quadrature/regeneration occurred in review. All D local
affine zero predictions lie outside the observed neighborhood; positive maxsymB
alone is not a proof against every dynamical or unicycle attracting behavior.

Controls review SHA256:
`81f3fcc2d443dd251066577b2c8d4a0de2065689730ec89b0164dade2e4ada5b`.
Component review SHA256:
`0ac35f079960b849da0f9aba16ee76a5b6b4bfb437b8d8f7b58f8ac63a0178ef`.

Study COMPLETE, candidate REJECTED, full goal OPEN. Current source/diff/context
checks passed. Material source archive follows below, without commit or push.


R20 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r20_local_attraction_v1/` contains642 verified source
members, completed in1.312258089s; manifest SHA256
`2b5a65bb99ee17580004c62cba037dfbd03aab81eb0843788c5dfc37d1143349`.
This live receipt postdates the immutable archive. The study is COMPLETE and its
candidate REJECTED; source helpers remain unwired, full goal OPEN. No runtime,
new matrix, commit or push is active. All inputs, failed review-output attempt,
source/tests, fixed failures and independent reviews are retained.
