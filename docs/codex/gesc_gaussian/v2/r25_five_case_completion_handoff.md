# R25 closeout: full 16-run comparison

The finite simulation comparison is finished. D, the combined recurrent detector
and continuous-search method, has four verified global-region arrivals and zero
mandatory stopped acquisitions in all four runs. The retained R10 component
evidence supports faster detection with fewer false detections in its fixed test
population. These are selected simulation results, not broad robustness proof.

Strict combined D qualification passes nominal and delay confirmation. Noise
remains EVIDENCE_UNAVAILABLE because one scheduled direction sample is missing,
despite passing median/P90 error gates on the five eligible samples. The original independently
labelled 30% trapping-onset improvement remains unachieved/unavailable. Study
completion does not turn these scientific limitations into passes.

## All sixteen outcomes

Times are simulated seconds from the recorded origin to the first qualifying
post-recovery sample within 0.5 m of the global source. GOAL_HOLD is optional.
Each cell is a separate run. A dash is measured nonarrival, not an unstarted run.

| Population / condition | A | B | C | D |
|---|---:|---:|---:|---:|
| Retained development, nominal; slots 1–4 | — | 314.098 | 136.567 | 147.998 |
| Confirmation, nominal; slots 5–8 | — | 286.132 | 135.953* | 171.882 |
| Confirmation, noise; slots 9–12 | — | 329.232 | — | 197.253 |
| Confirmation, 100 ms delay; slots 13–16 | 257.501 | 251.628 | 203.792 | 177.585 |

All arms retain GESC + Gaussian. A uses the PDE detector with stationary
verification; B uses recurrent geometry with stationary verification. C combines
PDE detection with rolling GESC and moving verification. D combines recurrent
geometry, rolling GESC, moving verification and authenticated recurrent trapping.
Noise is the frozen 0.015 V sensor-noise condition. Delay applies the frozen
0.10 s sensor and algorithm-pose delays.

*C7 has a native observed arrival at 135.953 s, but its command-consistency check
failed. Its qualified arrival time remains unavailable. This distinction is
preserved in the original data and final result; optional goal holding is not the
reason for withholding qualification.

There are 12 native observed arrivals and 11 qualified arrivals. All 16 effective
recording envelopes are complete; behavior is 11 PASS and 5 FAIL. Per-run
scientific measurements are complete for 15/16; C7 remains incomplete. All
recorded wrong-fill and wrong-goal counts are zero. This is not a general
false-detection guarantee.

## Continuous direction results

Errors use the existing qualified observed-phase stationary GESC reference under
the recorded objective. They are not errors against an arbitrary spatial-gradient
oracle or direct source bearing. Error statistics use eligible samples; all
scheduled, unexposed, ineligible and missing targets remain in the products.

| Run | Median / P90 error, degrees | Usable averaging / eligible | Mandatory stopped acquisitions | Coverage / interpretation |
|---|---:|---:|---:|---|
| C development | 16.839 / 21.181 | 3/3 | 0 | Complete product; angle gate PASS |
| D development | 12.519 / 25.224 | 4/4 | 0 | Complete product; combined PASS |
| C nominal confirmation | 19.578 / 21.163 | 3/3 | 0 | Direction PASS; C7 arrival qualification withheld |
| D nominal confirmation | 20.501 / 23.992 | 4/4 | 0 | Complete product; combined PASS |
| C noise | 27.922 / 98.918 | 11/12 | Unavailable | Complete product; angle gate FAIL; continuous VERIFY only |
| D noise | 7.060 / 33.445 | 5/5 | 0 | One missing anchor; strict combined qualification unavailable |
| C delay | 15.834 / 40.876 | 6/6 | 0 | Complete product; angle gate PASS |
| D delay | 4.494 / 32.538 | 5/5 | 0 | Complete product; combined PASS |

Each C/D product contains all 24 scheduled rows: 48 development and 144
confirmation targets, 192 total. D12 target 7 at offset 195 s,
target_ns=197229000000, is missing_anchor. Its observation, qualification and
error fields remain unavailable; it is not relabelled unexposed or supplied with
a replacement reference. D12 therefore fails strict product completeness under
the unchanged owner, while its available-sample angle summary passes.

C11's mandatory-stop count remains None: four continuous VERIFY segments were
observed, but no DESIGN acquisition occurred. None is not converted to zero.

## Detection evidence and remaining limits

The retained R10 study detected 36/36 positive histories with recurrent geometry,
versus 19/36 with PDE; negative-control confirmations were 0/48 versus 4/48.
Twelve gray histories remain separate. On one retained uninterrupted SEARCH
input, recurrent detection occurred at 102.008 s while PDE remained censored at
360.8 s. This supports a finite component improvement, not a universal detector
or independently labelled basin-entry latency claim.

The original comparison endpoint has 0/12 observed independent-onset latencies
and 0/6 observed pairs. Its 30% reduction remains EVIDENCE_UNAVAILABLE. Arrival
improvements and R10 response times do not substitute for that endpoint.

D reached the region about 40% sooner than B in nominal and noisy confirmation,
and about 29% sooner with delay. The trajectories differ, so these integrated
arrival times do not isolate detector speed. No claim about arbitrary fields,
acoustic experiments, physical hardware or universal reliability follows.

## Execution and retained evidence

The population is four retained V13 development recordings, seven retained V14
confirmation recordings, and five first executions of previously unused V14
reservations. It is not sixteen new recordings or untouched-condition validation.
Only output locations changed for the last five; seeds, cases, launch settings,
controller, cost/geometry and clocks stayed frozen. No simulation/runtime source
change was made for R25. R23's reviewed validator/test correction is the only
production source delta from V14; the phase-plan change is recorded separately.

Original V14 remains CLOSED_INCOMPLETE: ten COMPLETE, one INCOMPLETE and five
UNSTARTED. C11's separate R24 recording view passed all 61 checks, but its original
metadata, acquisition failure and no-arrival behavior remain unchanged. The
missing original independent-inner cleanup receipt is explicitly not fabricated.
C7's command failure and the earlier nominal summary timeout remain preserved.

R25 prelude session19704 terminated/reaped0 in119.060895 s, using the retained
9–11 bags for their first science and the C11 reference. Its independent review
passed56 checks. Continuation session56533 terminated/reaped1 in1803.878391 s
(30.065 min): all five acquisitions and all eight first-science/reference jobs
completed cleanly. Only report assembly rejected D12's incomplete coverage.
That failed report/job remains immutable.

The separate cached report admits the exact incomplete product for reporting
and uses unchanged aggregation to withhold the strict D/noise claim. Session62101
terminated/reaped0 in3.723035 s; no bags, labels, models or references were rerun.
Its report receipt is REPORTED, with all original failure provenance attached.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r25_five_case_completion_v1/`.

- Full existing-owner report: `final_cached_report_v1/report.md`.
- Machine-readable full comparison: `final_cached_report_v1/result.json` and `rows.json`.
- Cached report receipt: `final_cached_report_v1/receipt.json`, SHA256
  `f365789762a2a392e066faecd59d1b3b63b15b4b5dd4fde94b066760ab890b3a`.
- Result SHA256: `c2e8a394d460e59179b0f389eafb38a30ab746f364ef135be066fdd07adf8ccf`.
- Report SHA256: `ec68b31ce40a3856017f74992f6d7d7be13e8f73165b88b516053f9925dcffd1`.
- Terminal integrity review: `final_integrity_review_v1.json`, PASS202;
  all1273 pins matched and721 recorded process identities were absent.
  SHA256 `d09915325d7af850a51c43ff994dde7db7294548155af08956c023aa997e47e0`.
- Commands, initial failed environment preparation, source reviews and execution
  details: [R25 validation](validation/r25_five_case_completion.md).

The initial setup failure was an omitted ROS environment selection in the root
invocation. Six unsealed setup files were preserved before the same unchanged
helper successfully prepared under domain201/localhost1. No empirical attempt
was repeated. The full report's inherited native block count describes the old
V14 ledger; use its explicit follow-up rows and coverage fields for this closeout.

Git remains `feature/gesc-gaussian-robustness-v2` at `3369cfc` with uncommitted
task changes. No physical, Pi, snapshot, V1, commit or push action occurred.
All empirical processes are terminal. Final independent science review and
material archive receipts are recorded below before administrative closeout.

Final independent science review PASS54: `final_science_review_v2.json`, SHA256
`360af7c549ffd33998e574d48256983bcab5c2cbae4da7c7a86a99cf4b0dfd2d`.
All1273 prepared pins and44 cached-report pins matched. The initial review file
is retained; its sole false failure expected the original failed report job to
have integrity_passed=True, whereas its correctly retained value is False.
Only that review expectation changed. No source or data product changed.
The final handoff claim review found no substantive overclaim; the noise error
wording explicitly refers to median/P90 gates, not an individual30-degree bound.

The authorized finite study is closed with these limitations. Selected simulation
evidence supports the two qualitative method improvements; strict all-condition
qualification and the secondary30% onset target are not declared achieved.
No additional experiment, method iteration or background simulation is scheduled.

Material checkpoint COMPLETE:693 individually verified source members in1.079614s,
plus89 selected source/receipt/metric/report files (32,936,559bytes) staged with
original-path/hash mapping. Raw bags and normalized/label arrays were not reread.
Archive: `/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/r25_full_comparison_closed_v1/`;
manifest SHA256 `00a79dbdbab353dc9b1cd75b873f7eacd4c9c88adef6dc36e6c14f7192bc47c6`.
The source archive preserves the exact root plan and validation-note bytes used
through final source/science review. This receipt annotation and administrative
root-plan closure were written afterward; they do not change the frozen study.
Do not rerun the original frozen contract against subsequently updated docs.
Context validation, checkpoint tooling and diff checks passed. V2 remains at
3369cfc with the uncommitted task changes; no commit/push or physical action.
