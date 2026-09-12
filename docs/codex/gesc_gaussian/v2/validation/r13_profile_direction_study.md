# R13 retained profile/direction study validation

Adopted [plan](../r13_profile_direction_study_plan.md) after R12's 608-member
verified archive. No new simulation or production method change. All six V12
trajectories are exposed development inputs; original populations/results remain
unchanged. Work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r13_profile_direction_study_v1/`.

## Prospective execution

Root owns three exclusive jobs: A noisy cached profile reconstruction, B fresh
D/noise reference component through existing numerical/process owners, then
C same-confidence direction weight projection. A/B may run independently; C
requires B's qualified output. Inclusive caps: A60s, B45s work-owner within55s
outer allowance, C30s. No bag read, labels rerun or field geometry preparation.

Current production code is the R12-validated source; old V12 numerical owners
and original normalized/reference/model inputs stay immutable. Any new profile
reconstruction mismatch, reference difference or missing recovered mean remains
explicit. Current preparation is not an empirical result.

## A: retained profile measurements

One execution, session 79372 terminal/reaped 0: 14.405137075 s outer,
13.672080197 s helper. Exact argv is in `profile_execution.json` and
`profile_ready.json`: sourced selected runtime, `python3 -B profile_probe.py`,
GNU timeout SIGINT55s plus kill5s. All 22 pins remained stable; no bag or model
read. All eight attempts are MEASURED. The existing owner returns
`uninformative_raw_profiles` in all eight, matching every recorded rejection.
Six terminal diagnostic snapshots match exactly. C/epoch1 and D/epoch1 retain
their explicit numerical mismatches; no clock search or callback-parity claim.
D's confirmation source coordinate is traced from the retained history-end
binding through pinned `v2_binding.publish_centroid` and `_confirmation`.

All eight three-cycle windows meet the existing 0.15 m sector-trajectory bound.
Mean-profile amplitudes are 0.005124–0.007513, disagreement 0.008140–0.011804,
with descriptive F 1.368196–3.722473. Every available longer window fails the
geometry bound: seven of seven six-cycle and six of six nine-cycle windows.
The other three requested longer windows have insufficient eligible cycles.
Thus extending the averaging window alone is unsupported on these retained
attempts. Raw spread and F remain descriptive, not calibrated noise/confidence.

`profile_result.json` SHA256:
`609aff8d9af2c60093231260febcce4a60aab67aea58508c59f61419e788ff4d`.
Execution receipt SHA256:
`dee51f46af108c984a42ad473ba2f55057167844ce8ca8f35fcbd43eefa452f4`.

## B: new D/noise reference component

One execution, session 93454 terminal/reaped 0: 15.159683679 s outer,
14.679746403 s parent and 13.230852252 s native science owner. Exact sourced
argv is in `reference_execution.json`/`reference_ready.json`: SIGINT50s plus
kill5s outer; existing `finite_science_job` 45s inclusive, subreaper_group_v3.
All 559 prepared/self pins remained stable. The worker audited zero subprocess
attempts; native process inspection, cleanup and kernel reaping passed.

All 24 original target identities, numerical rows, summary and supplemental
results exactly match the old numerical product. New component process
qualification PASS does not rewrite historical V12 process failure. The
direction result remains FAIL: median 33.273126 degrees, P90 116.266039 degrees,
12/24 eligible, 7/12 usable averaging and 12/12 usable outputs.

Component receipt SHA256:
`555d7e4078e4695c07212f7a77b3f6253b3070d108628c6155a17f46190a6620`.
New product SHA256:
`4a29cea1ac1e84c9ed63fecc30421b70609d62079e865ec96a1a274bf507545d`.
Native job SHA256:
`107cac89e68cc3a0a439b21a2a5a72a9f9e539c7a351afb5ec5520ea1d800267`.

## C: fixed-confidence direction projection

One execution, session 65311 terminal/reaped 0: 11.178807759 s outer,
10.736212232 s helper. Exact sourced argv is in `direction_execution.json`
and `direction_execution_ready.json`: `python3 -B direction_probe.py --prepared
direction_prepared.json`, GNU timeout SIGINT25s plus kill5s. All 38 pins were
stable. All 144 scheduled targets across six inputs remain present; 48 original
development and 96 formerly-confirmation targets are now exposed development.
No bag/model/reference-owner replay was performed by this projection.

At all 40 eligible originally blended anchors, the recovered current-cycle mean
passed the fixed recomposition and independently stored magnitude tolerances
(absolute1e-10 + relative1e-8). No consistency-unavailable projection occurred.
All original eligibility, usable-output and averaging counts stayed unchanged.
Twenty-three paired errors improved and 17 degraded relative to the recorded
blend. These pairs are nested in six different trajectories; no pooled
independence or new confirmation claim follows.

| Input | Recorded median/P90 (degrees) | Mean-only projection median/P90 | Averaging / eligible | Projection result |
| --- | ---: | ---: | ---: | --- |
| C development | 14.025 / 34.586 | 6.661 / 36.057 | 4/4 | PASS |
| D development | 8.249 / 24.130 | 20.232 / 24.242 | 7/7 | PASS |
| C nominal | 32.658 / 72.531 | 2.930 / 64.571 | 6/6 | FAIL |
| D nominal | 5.683 / 25.495 | 3.370 / 17.042 | 5/5 | PASS |
| C noise | 24.626 / 77.419 | 25.841 / 59.096 | 11/12 | PASS |
| D noise | 33.273 / 116.266 | 29.526 / 116.266 | 7/12 | FAIL |

C/noise crosses the existing summary thresholds, but seven of its 11 paired
errors worsen (four improve). D/noise still fails P90 and averaging
availability. C/nominal still fails P90. Weight-only correction therefore does
not establish reliable continuous direction. No runtime parameter was changed.

## Review and closure

A independent cached review PASS: 14 checks, eight stable small refs,
0.025855521 s; `profile_review.json` SHA256
`5295d6e9b6041f0e47ab64614310f25d602a5d44ed9b5c8cc514d8419f489b99`.
Review used saved arithmetic and receipts, not an additional observation replay.
B/C independent cached review PASS:54 checks,15 stable selected refs,
0.058606s. `direction_reference_review.json` SHA256
`6a6bcf809d01e737a5965d6ad6c54e3a9118db593bd75d3b337bd51696a7606b`.
All144 identities/counts, fallback, availability and scalar error summaries were
checked; no new normalized-cache read, owner/model replay or test run. Native
summary pairs compare against instantaneous direction; the23/17 diagnostic
counts compare recorded blend against projection.

Direction result SHA256:
`6810cf280ada6704c1cdfe3c926aca903a55726c3aa6245baffcdd88317f1d95`.
Execution receipt SHA256:
`da6438e34c212a6507ac9b17bd353e38e8e50861898bcac1349b212490a6e2f3`.
The three outer executions total40.743628513s within145s combined allowance.
R13 COMPLETE; see the [handoff](../r13_profile_direction_study_handoff.md).
No production source changed and no simulation or matrix has been released.

Context/diff/checkpoint PASS. Material archive
`checkpoints/r13_profile_direction_study_v1/` verified611 members in0.902479s;
manifest SHA256
`842d44bdb75b4525787b981cc2290e21b91e8c034f6bb9bff35eeb688f97a294`.
This receipt postdates the immutable archive and changes no production source.
