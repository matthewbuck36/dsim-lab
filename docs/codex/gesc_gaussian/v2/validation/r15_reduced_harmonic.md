# R15 reduced harmonic validation

Prospective plan adopted; source/control preparation only. Previous goal turn
made progress by completing R14 independent review and material closure.
No R15 numerical study, simulation or runtime integration has executed.

## Source implementation and focused validation

Independent pre-measurement review identified an exact ambiguity: half-rate
circular base motion through quadratic spatial cost can imitate an angular
first harmonic. The plan was amended before tests/studies to compare two fixed
spatial nuisance variants, linear and quadratic, on identical controls. Both
omit position-times-harmonic interactions; no threshold was chosen from data.

Implemented separate `fit_reduced_profile(..., spatial_degree=1/2)` in the
existing harmonic owner. R14 entrypoint retains its prior behavior; shared
linear fit only adds influence/leverage arrays to its internal return. Added
`observed_phase_harmonic_map` in the existing reference owner; all prior
reference function bodies are byte-identical. Both remain unwired to runtime.

Sole focused bundle session82259 terminal/reaped0:57/57 PASS in1.58s pytest,
2.269873966s outer. Seven source/test/plan/environment pins unchanged.
`focused_prepared.json`, `focused_console.log` and `focused_result.json` under
R15 external work root retain exact55s SIGINT+5s kill argv and receipts.
Selection:24 prior R14 regressions,16 reduced-fit mathematical cases and17
analytic/reference-map cases. This validates math and compatibility only;
independent synthetic and retained scientific measurements are still pending.

## Synthetic execution

Static independent fit/map reviews passed. Root rechecked all16 prepared pins,
validated the exact two-variant calibration/eligibility logic and shared-input
control generation. Sole synthetic session21463 dispatched under145s SIGINT+5s
kill, internal135s work cap; one1628-input generation and3256 variant episodes.
Source/plan/config remain held. No retained job or simulation has started.
Prepared SHA256 `2822c416331eae91e7fecadea64bf1b1632b5216ea5ad60ae5ecafa9e83614e8`.

Synthetic session21463 now terminal/reaped0. Complete1628 shared inputs,
3256 variant episodes/6512 looks in20.211445231s outer;17.181601943s result
helper and19.589329105s closed receipt. Seventeen pins including prepared self
remain stable. No timeout, retry or source change.

| Result | Linear spatial | Quadratic spatial |
| --- | ---: | ---: |
| Frozen score cutoff |5.6386213743 |6.5900914904 |
| Separate null false accepts |0/512 |0/512 |
| Stronger stable detection |60/64 PASS |53/64 FAIL |
| Accepted positive count |67 |57 |
| Accepted direction median/P90 degrees |3.0433/8.5218 |2.7145/8.6146 |
| Hard reversal/loss accepts |0/32 |1/32 |
| Exact phase-position confounding |16/16 unavailable |16/16 unavailable |
| Quadratic spatial null false accepts |7/64 FAIL |1/64 PASS |
| Half-phase curvature null |6/16 accepted |16/16 unavailable |
| Mature late-change false accepts |0/16 |0/16 |

Both candidates FAIL their independent complete criteria. Linear detects the
strong signals but cannot distinguish the declared spatial-curvature ambiguity.
Quadratic handles that ambiguity, but loses detection power. This is not a
runtime release. Gray smooth changes and partial-cycle transients stay gray;
their accepted current-time errors are retained in the full results.

Result SHA256 `e566789b9247cff82622449c45bf07c219eecb5f4cec0e749d5758f17077d6fe`.
Receipt SHA256 `f355fe50c0d760a3df0cadd7e440a8bb881116254fd9e0dd91c5132c92d9bab4`.
Execution SHA256 `5ad3430a96fd09e8d00175a5e23bc6c38435dbd0f7c85e073b3b1fd813c34d3d`.
Independent cached review and prospectively allowed retained descriptive job
follow; no numerical result is being retuned or omitted.

Independent cached synthetic review PASS in2.86s, SHA256
`ad04206c0ac9bf1aa54abb97fc3e3b9266d3bf4b636e59d4a1663e95fdd32ed6`.
All1628 input fingerprints/spec/seed bindings,3256 variant records and6512 look
scores/gates were checked without refitting. Quadratic misses are nine
latest-cycle prediction rejections and two score rejections; all five missed
amplitude0.030 controls are curved and pass the score at both looks. This
locates the next correction in the prediction guard, not insufficient score.

## Retained execution

Independent static review caught a final count assertion using nonexistent
`eligible_count`; actual frozen summaries use `counts.eligible_informative`.
No job had run. Preserved the original helper/manifests under
`retained_preparation_before_key_fix/`, corrected that single field lookup,
and created versioned v2 preparation/ready receipts. Cached counts are
4+7+6+5+12+12=46. No scientific input, method, cutoff or budget changed.

Root rechecked all64 final pins, corrected assertion, absent exclusive outputs
and matching exact `command` lists. Sole retained session1768 dispatched with
145s SIGINT+5s kill/internal135s. Prepared v2 SHA256:
`5fb8df24b5867218d45d19b56253e8d741329e0c428c8bb0f3e9ee5203e7024b`.
Ready v2 SHA256:
`e189b54967381587a20a249ee2433227a26f5613ac469f6082fcf5aa9b719fa5`.
No simulation or true-field query is involved.

Retained session1768 terminal/reaped0:16.349236564s outer/15.525118109s helper.
All65 pins stable (64 prepared plus prepared self).40 shared harmonic maps and
40 raw-zero known-term integrals; zero bag reads/true-field model queries.
Both variants preserve144 targets/46 original eligible;40 supported estimates,
six eligible excursion rejections. No original qualification or denominator
changes. Independent cached review follows.

| Retained input | Eligible | Linear admitted; median/P90 degrees | Quadratic admitted; median/P90 degrees |
| --- | ---: | --- | --- |
| C development |4 |0; unavailable |0; unavailable |
| D development |7 |2;16.352/17.021 |0; unavailable |
| C nominal |6 |3;0.812/3.616 |3;3.380/5.931 |
| D nominal |5 |2;10.103/15.326 |0; unavailable |
| C noise |12 |2;4.761/5.095 |2;3.672/3.992 |
| D noise |12 |1;4.285/4.285 |1;1.482/1.482 |

Linear usability10/46;19 latest-prediction rejections,11 score rejections,
six excursion failures. Quadratic usability6/46;17 prediction rejections,
17 score rejections,six excursion failures. Every per-run admitted-method summary
fails availability; accepted accuracy does not qualify the omitted population.
The unscreened40-estimate population has large errors in several runs (e.g
linear C/noise median68.170/P90111.882 degrees; quadratic68.502/P90146.494
on D/noise). Thus relaxing admission alone is unsupported; both model bias and
noise/geometry information remain relevant hypotheses.

All eight verification supports fit finitely with both variants. Only D/noise
epoch2 passes both score and latest prediction in either variant: linear score
6.249639 versus5.638621; quadratic9.844790 versus6.590091. Original R13 geometry,
minima, negative-cost guards and historical replay mismatches remain unchanged.
This projected raw-information admission is not a new accepted fill or escape.

Retained result SHA256:
`954dc9e25bbe9c8436bca0e43156b6364ad6f33340d79ebff129c4b8e02e4960`.
Execution SHA256:
`67ee4f5a00d65dc26983a96abd913b61583e259b769279d4043d7765123ac33d`.

Independent retained review PASS:1124 cached checks in0.806624s, SHA256
`d5563548d01232d36a43646a672d72af708cff0ebf998d41c3198d7f060e71de`.
All152partials, both144-target populations, original46 eligible targets and
8supports unchanged;80 cached map/covariance/error compositions and all scalar
summaries agree. Both41 finite fits include one original-ineligible anchor;
40 mapped eligible directions per variant. Only D/noise candidate2 passes the
projected raw-information test. No new numerical fit/model call/bag or runtime.
R15 study COMPLETE and both candidate failures preserved. Next work must
separate retained model bias from noise before changing confidence gates.

R15 material closure: context validator, diff check and existing checkpoint PASS.
Archive `checkpoints/r15_reduced_harmonic_v1/`:621 verified source members,
1.113313046s; manifest SHA256
`ed0a9afa2a38cedb6786001e76b0a788e86b829682663bfc96878dc72c0ae06d`.
This live receipt postdates the immutable archive. Both candidate failures and
all raw/cached measurements retained; no simulation, commit or push performed.
