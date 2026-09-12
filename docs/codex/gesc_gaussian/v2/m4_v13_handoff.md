# M4v13 closeout: three arrivals, unavailable D motion measurement

Status: **CLOSED_INCOMPLETE**,2026-09-11UTC. Sole dispatcher session9544 is
terminal/reaped1 after1559.393681570s outer (about26minutes); native dispatcher
elapsed1554.627737746s. Four development acquisitions are COMPLETE; all twelve
confirmation slots are UNSTARTED. The existing gate withheld confirmation after
the D motion measurement was unavailable. Do not restart this fixed version,
replace its slots, alter its report or promote its unavailable measurement.
The full detector/continuous-direction goal remains open.

The [adopted plan](m4_v13_integrated_comparison_plan.md) and frozen contract govern
this experiment. Arrival within the evaluator-only0.5m global region after valid
local recovery is sufficient; GOAL_HOLD remains optional.

## Retained results

| Development arm | Recovery and arrival | Exact recorded arrival time | Motion measurement |
| --- | --- | ---: | --- |
| A: PDE, stationary | No confirmation/fill/recovery before360s Stage A limit | No arrival | Not applicable |
| B: recurrent, stationary | One fill, assisted escape, return to SEARCH, arrival |314.098s| Not applicable |
| C: PDE, moving | One fill, direct escape, return to SEARCH, arrival |136.567s| Continuous acquisition;0 mandatory stops |
| D: recurrent, moving/trapping verification | One fill, assisted escape, return to SEARCH, arrival |147.998s| EVIDENCE_UNAVAILABLE: command pairing failed |

All four recordings, integrity and strict cleanup checks pass. B/C/D pass all
eleven primary run predicates. Every arrival is bound by recorded_pose_arrival_v1
without binding errors; optional controller-goal failures remain preserved.
The recorded-pose time joins confirm the live times shown above.

| Direction product | Median error | P90 error | Usable averaging / eligible | Observed / scheduled | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| C |16.839333°|21.180857°|3/3|4/24|PASS|
| D |12.519443°|25.224003°|4/4|5/24|PASS|

All48 scheduled development targets remain:9 observed and39 unexposed. C improves
on instantaneous direction for3/3 paired targets; D for3/4, with one degraded
target retained. Reference scope is the observed-phase stationary periodic GESC
response, not a general spatial gradient. Development is separate from the
twelve unstarted confirmation runs and their144 planned direction targets.

All four development runs have known zero wrong-fill/goal counts with no
attribution errors. This is a selected finite observation, not a general false
detection rate. The original independently labelled30% basin-entry latency
target remains UNACHIEVED/UNAVAILABLE. R10's separate same-SEARCH response and
synthetic controls retain their original evidence scope; integrated arrival
differences do not isolate detector speed.

## Why dispatch stopped

The label job, both C/D reference jobs and summary job all returned0, without
timeout or process-integrity failure. Block processing took127.474274578s:
labels100.457599557s, C reference7.496080291s, D reference8.451591495s,
summary6.188649624s. Block complete/integrity flags are true, while
scientific_analysis_complete is false: A/B/C pass all nine measurement checks;
D fails only motion_measurement_complete. Final report generation completed.

D's readiness interval contains7398 final-command records and7399 diagnostic
records. Both full streams contain8041 records, with pre-readiness counts312/311
and post-readiness331/331. The existing evaluator cuts each topic independently
to readiness and then pairs by position; it records3233 vector/pair mismatches.
The controller emits the command and diagnostic sequentially, without a shared
sequence identifier. A boundary between their receipts is a plausible cause,
not yet proof that all full-stream pairs correspond correctly.

Both D acquisition segments have positive measured displacement and complete
pose coverage in the retained partial diagnostics: VERIFY84.2–98.8s and
DESIGN98.8–99.5s. They remain unqualified because command pairing failed. Do not
assign a zero mandatory-stop count from these partial observations.

The normalized direction cache does not retain complete command/diagnostic
records, so it cannot prove the exact boundary-pair stamps or8041 full-vector
matches. The next useful work is a separately planned, finite filtered read
through the existing bag reader to test that explanation. No new simulation is
needed for this diagnosis. Any correction needs its own prospective validation
and must preserve the original V13 failure and untouched confirmation slots.

## Evidence and workspace

External root: `/home/mattb/Experiments/GESC-Gaussian/v2/`.

- `pilot/m4_pilot_v13/acquisition/acquisition.json` and slot1–16 receipts retain
  the failed release, all dispositions and no replacements.
- `pilot/m4_pilot_v13/analysis/block_0/` retains every label/metric, both direction
  products, all finite job receipts, result and block receipt.
- `pilot/m4_pilot_v13/report/report.md`,result.json,report_receipt.json are the
  immutable native report. Report SHA256
  `8cfd93729b0c31920b11fad5d3b81afada0b339e66c388135aaaa32f48a589ea`;
  result SHA256`a8dd9a00fca91fc705ab9d4843a874b008083e7987b6f2bc7a24387452da3fc7`.
- `development/20260911/m4_v13_source_v1/acquisition_execution_v1.json` records
  terminal exit1,error=null and the hash-bound command/console. The unchanged
  driver checks all963 source-validation pins after dispatch returns.
- [Source validation](validation/m4_v13_source.md),
  [frozen preparation](validation/m4_v13_preparation.md) and
  [execution](validation/m4_v13_execution.md) retain exact commands and receipts.

Source validation passed640/640 in the second fixed bundle; the first bundle's
637passes/3new-fixture failures remain retained. No production source changed
between those bundles or during the comparison. Branch
feature/gesc-gaussian-robustness-v2 at3369cfc83a64ff5d8354827fd5310caaf0c8e945;
task changes remain uncommitted. No physical/Pi/snapshot/V1/commit/push actions.
Terminal independent review and material checkpoint receipts follow in the live
execution record; preserve this closeout before the next method/analysis edit.
