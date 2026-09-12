# R13 retained measurements: longer pooling and blend weight are insufficient

Status: COMPLETE, 2026-09-11 UTC. All measurements and independent reviews
passed their declared evidence checks. All executions are terminal/reaped, with no active
simulation. This is exposed development evidence under the unchanged
[prospective plan](r13_profile_direction_study_plan.md), not a new integrated
experiment or retrospective completion of V12.

## Findings and decision

Eight noisy verification attempts were measured using existing observation and
raw-cycle owners. All eight reproduced the recorded `uninformative_raw_profiles`
reason; six terminal diagnostic snapshots matched exactly. Initial C/D epochs
retain explicit mismatches. The fixed publication-clock replay cannot establish
exact supervisor DDS receipt/reset history.

All eight three-cycle windows passed the existing geometry criterion, but signal
amplitude was below inter-cycle disagreement. Every available six/nine-cycle
window failed the unchanged sector-trajectory tolerance; three requested longer
windows lacked enough eligible cycles. Descriptive signal/residual F ranged
1.368–3.722, without calibrated confidence or a noise-only interpretation.
Extending the averaging window alone is unsupported on these retained attempts.

The new D/noise reference component completed with zero subprocess attempts,
clean native process ownership/reaping and stable inputs. All 24 target rows,
summary and supplemental values exactly match the old numerical product.
Historical V12 process failure remains unchanged. The separately qualified
component confirms direction failure: median/P90 33.273/116.266 degrees and
averaging available at seven of 12 eligible targets.

The direction projection retained all 144 scheduled targets: 48 original
development and 96 former confirmation targets, all now exposed. At 40 eligible
anchors with recorded blend weight 0.75, the current-cycle mean was recovered
and checked against stored magnitude. No consistency failure occurred. Recorded
fallback, eligibility and averaging availability were preserved; 23 paired
errors improved and 17 degraded. No completed-cycle vector at weight zero or
three-cycle vector was invented.

| Input | Recorded median/P90 (degrees) | Mean-only projection median/P90 | Eligible / scheduled | Averaging / eligible | Projection |
| --- | ---: | ---: | ---: | ---: | --- |
| C development | 14.025 / 34.586 | 6.661 / 36.057 | 4/24 | 4/4 | PASS |
| D development | 8.249 / 24.130 | 20.232 / 24.242 | 7/24 | 7/7 | PASS |
| C nominal | 32.658 / 72.531 | 2.930 / 64.571 | 6/24 | 6/6 | FAIL |
| D nominal | 5.683 / 25.495 | 3.370 / 17.042 | 5/24 | 5/5 | PASS |
| C noise | 24.626 / 77.419 | 25.841 / 59.096 | 12/24 | 11/12 | PASS |
| D noise | 33.273 / 116.266 | 29.526 / 116.266 | 12/24 | 7/12 | FAIL |

C/noise's summary crosses the existing thresholds while seven of its 11 paired
errors worsen. D/noise still fails P90 and availability; C/nominal still fails
P90. A blend-weight change alone cannot establish the intended direction goal.
These projections do not predict changed closed-loop arrivals.

Next work should prospectively evaluate a noise-aware estimator that accounts
for motion, using independent noisy-flat, known-signal and changing-profile
controls with explicit identifiability and false-acceptance checks. No particular
regression/model, lowered verification threshold or new runtime estimator is
selected by R13. Reuse existing numerical/runtime owners where practical, retain
the negative-cost guards and selectable GESC/Gaussian baseline, then test a
promising correction in a bounded visible integrated case before another matrix.

## Current 16-slot comparison boundary

V12 remains [CLOSED_INCOMPLETE](m4_v12_handoff.md). Its four arms are A PDE plus
stationary measurement, B recurrent detector plus stationary measurement,
C PDE plus moving measurement, and D recurrent detector plus moving measurement.
All preserve Gaussian escape. Arrival within the evaluator-only 0.5 m global
region suffices; GOAL_HOLD is optional.

| Condition | A | B | C | D |
| --- | --- | --- | --- | --- |
| Development | Recovery timeout | Arrived 173.049 s | Arrived 151.858 s | Arrived 251.313 s |
| Nominal confirmation | Arrived 230.504 s | Arrived 302.605 s | Arrived 211.539 s | Arrived 192.075 s |
| Noise confirmation | Arrived; block science incomplete | Arrived; separate R12 time 283.167 s | No fill, escape or arrival | No fill, escape or arrival |
| Delay confirmation | Unstarted | Unstarted | Unstarted | Unstarted |

Acquisition outcomes are nine arrivals and three nonarrivals in 12 complete
recordings; four runs remain unstarted. Development is three arrivals/one failure;
the planned confirmation population is six observed arrivals/two nonarrivals/
four unstarted. Only V12 blocks 0 and 1 completed scientific analysis. R12's
separate corrected B/noise timing and R13's component reference do not rewrite
the incomplete noisy-block aggregate. No unstarted delay case was acquired.

## Validation, evidence and Git

External work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r13_profile_direction_study_v1/`.
The [validation record](validation/r13_profile_direction_study.md) contains
exact outcomes, counts, limits and receipt hashes. Each ready/execution receipt
contains the complete argv and source/input binding.

- A session 79372: exit0, 14.405137075 s outer, 22 stable pins.
  `profile_result.json`: `609aff8d9af2c60093231260febcce4a60aab67aea58508c59f61419e788ff4d`.
- B session 93454: exit0, 15.159683679 s outer, native13.230852252 s,
  559 stable pins. `job_b/component_receipt.json`:
  `555d7e4078e4695c07212f7a77b3f6253b3070d108628c6155a17f46190a6620`.
- C session 65311: exit0, 11.178807759 s outer, 38 stable pins.
  `direction_result.json`: `6810cf280ada6704c1cdfe3c926aca903a55726c3aa6245baffcdd88317f1d95`.

The three outer executions total 40.743628513 s, within the planned combined
145-second outer allowance. No bag read, ROS/Gazebo launch, source method edit
or test rerun occurred. Source remains at the R12-validated correction; all
historical experiment data and failed verdicts are retained.

Independent cached reviews passed: A14 checks/eight stable refs in0.025856s,
B/C54 checks/15 stable refs in0.058606s. The latter receipt is
`direction_reference_review.json`, SHA256
`6a6bcf809d01e737a5965d6ad6c54e3a9118db593bd75d3b337bd51696a7606b`.
Native summary paired improvements compare against instantaneous direction;
the23/17 counts above instead compare recorded blend against the projection.
Reviews use saved scalar arithmetic/receipts without additional owner replay.

Context validator, diff check and existing material checkpoint passed. Archive
`checkpoints/r13_profile_direction_study_v1/` verified all611 source members in
0.902479s; manifest SHA256
`842d44bdb75b4525787b981cc2290e21b91e8c034f6bb9bff35eeb688f97a294`.
This receipt postdates the immutable archive; no production source changed.

Branch `feature/gesc-gaussian-robustness-v2`, HEAD
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`. Task changes remain uncommitted.
No physical, Pi, snapshot, V1, commit or push action was performed.
The full research goal remains incomplete.
