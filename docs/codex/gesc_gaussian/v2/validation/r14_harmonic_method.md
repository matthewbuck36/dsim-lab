# R14 harmonic method validation

Prospective [plan](../r14_harmonic_method_plan.md) adopted after R13 completion.
Previous goal turn was progress: three measured jobs and independent reviews.
Study COMPLETE, candidate REJECTED. No runtime is active; source remains unwired.

Work root: `/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r14_harmonic_method_v1/`.
Root owns one bounded focused source test, one synthetic-control job and one
retained applicability job; exact prepared bindings precede execution. New pure
owner remains unwired to ROS/controller/supervisor. All older evidence retained.

## Source validation

Static review corrected two guards before execution: reject a cycle label
spanning multiple turns, and reject nonfinite covariance/uncertainty before
serialization. No empirical threshold was changed. Actual raw boundary samples
allow one observed phase step at each clipped edge; no endpoints are fabricated.

One focused bundle passed24/24 in0.10s pytest,0.768110724s outer, exit0.
Exact sourced argv and four stable source/test/plan/environment pins are in
`focused_prepared.json` and `focused_result.json`. GNU timeout SIGINT40s plus
kill5s; BLAS threads1. Covers independent exact recovery, moving interactions,
held-out gains, coordinate/time origin, cost sign/DC, exact/near confounding,
nonfinite/overflow input and malformed/missing support. No ROS launch or field
model was used. Pure source remains unwired to runtime.

Validated owner SHA256:
`bb2f9dc500678123ffa843dd59607daccc95023e183e0f609f84f4f88966bfe6`.
Test SHA256:
`1e18ce400d3140fb9f3d4a59c94417d73c3397ffec7a6c05ef6953bbb71b2c06`.

Before synthetic execution, the prospective cutoff definition was clarified to
`max(0, largest calibration maximum)` to require positive held-out predictive
benefit even when all null maxima are negative. The source fit and tests are
unchanged; no study result was seen before this bounded guard clarification.

## Independent controls: candidate rejected

Sole synthetic session44490 terminal/reaped0: all1468 episodes completed in
8.220024318s outer (7.190561090s helper;7.740024757s closed receipt). All15
source/config/seed/validation pins remained stable. Exact115+5s sourced BLAS1
argv is in `synthetic_execution.json`; all generated raw inputs,1468 per-episode
records and both9/12s looks are retained. No timeout, retry or source change.

The frozen null-calibration cutoff is0.20211134529019842; zero-floor inactive.
Separate null evaluation:0/128 false accepts in each of IID, AR1, phase-dependent
variance and rare-burst families (0/512 total). All16 exact and16 near phase/pose
confounded controls were unavailable. Hard reversal/loss controls had0/32 accepts.

Stable signal detection FAIL:0/32 at amplitude0.0075,5/32 at0.015,21/32 at0.030;
26/64 stronger signals detected, below the90% criterion. All26 accepted positive
directions had median4.875763 degrees/P908.623430 degrees error. Scheduled
response median/P90 was9s; the last actual input sample was8.95s. The good error
on that selected subset does not cure inadequate detection/availability.

Candidate verdict is FAIL, while the controlled measurement job is COMPLETE.
No runtime integration is released. The prospectively declared retained job
remains permitted as a descriptive accuracy-versus-availability diagnosis.

Synthetic result SHA256:
`d36514a1f06a55d555721d2f8e2cdafb74833a1d6184715c09c495ceaf36f99d`.
Receipt SHA256:
`ee5c1e308a4bc3f408a77e3f05bd6e6007796fa2891d9335b8994c102f3a7d46`.
Independent cached review PASS17 checks/eight stable refs in0.999189s,
`synthetic_review.json` SHA256
`7af3697712b1d9f4149ff1d4a8862e4c4fc2fbd6dd60cef7f43080bd9cf53a04`.
All2936 look decisions,1468 unique seed/input-spec bindings and population
counts were checked without regenerating inputs or replaying fits. Zero events
in128 trials gives one-sided95% upper bound0.0231324 per declared family, not1%.

All31 curved positive episodes were unavailable because their information
fraction0.05113199 was below0.10; none failed source/sector support. Of64 stronger
positives,18 were unavailable and20 failed CV, leaving26 accepted. SNR caused no
additional rejection after CV passed. Lowering SNR cannot address those misses.

## Retained applicability: no usable new direction

A root invocation wrapper first failed before subprocess creation because it
looked for `argv` in the ready receipt, whose exact key is `command`. No helper
or numerical work started. `retained_prelaunch_error.json` and the empty
`retained_prelaunch_console.log` preserve this bounded dispatch error. Root then
used the declared command unchanged; this was the sole numerical execution.

Session21676 terminal/reaped0:12.346496100s outer,11.681939245s helper.
All56 pins stable, all144 targets and eight R13 verification supports retained.
Exact90+5s sourced BLAS1 argv is in `retained_execution.json` and the ready
receipt. No bag read or true-field query; only one fitted GESC response was
evaluated, through the existing observed-phase numerical owner.

Among46 original eligible targets,39 failed the angular-information screen,
six exceeded the prospective0.5m support excursion, and one supported fit failed
the score/proxy gate. Thus new usability is0/46. Across all144 scheduled targets:
40 information failures, seven excursion failures, two context/readiness
boundaries, one score/proxy failure and94 unexposed anchors.

The one supported C/noise fit was target12, source347.936s. Its ungated direction
error was0.981585 degrees versus recorded15.717949 degrees, but CV gains were
[-16.221374,0.130769,-1.130772] and SNR2.375277, so it correctly remained unusable
under the frozen rule. One accurate point cannot qualify the estimator.
Fallback errors remain exactly the recorded values; new-method averaging
availability is0 in every run. No fallback is counted as new confidence.

All eight verification projections failed information, with fractions
0.0000403873–0.0556546904 against0.10. R13 geometry, raw minima/negative-cost
guards and the two original terminal replay mismatches remain unchanged.
No fill or runtime change was accepted.

Retained result SHA256:
`14c29685d2135d139320729aa393084ffc8e7d7caf97e6ffb2f3421bc5b2b5d6`.
Execution receipt SHA256:
`6c9ba2caf888dddf1b8b74a40c43a4bf1fcc4543f7ca79e9b0c566e1124d3c51`.
Independent retained review PASS58 checks in0.261437679s. All144 original target
identities,46 eligible/50 exposed/94 unexposed,152 partial products and eight
verification supports match. Before/after18 selected hashes and all56 execution
pins are stable. Exact old fallback errors, original qualifications, geometry,
minima and historical terminal mismatches remain intact. Review SHA256:
`9ddd3dcfdc33d02eeaffdf411479f5466a4fcc3d4fd9649c5df0cc25b2ed547f`.
No new numerical job, bag read, fit or field-model query was run for review.

R14 study is COMPLETE and its candidate remains REJECTED. Full research goal is
still incomplete. Next method revision requires a new prospective hypothesis;
no threshold retuning or runtime release follows this failed component. Root
recovery read current plan/status/handoff and checked Git/context; selected
procfs scan found no Gazebo or installed ros_esc application process.


R14 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r14_harmonic_method_v1/` contains616 verified source
members, completed in0.990166671s; manifest SHA256:
`4da7470b0cdff23d384033e88bee6e97a5230b6a2a9329005f51aac6e1b20237`.
This live receipt postdates the immutable archive. Study COMPLETE, candidate
REJECTED; no active simulation, commit or push. Full research goal remains open.
