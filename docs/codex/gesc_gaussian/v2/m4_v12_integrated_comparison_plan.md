# M4v12: integrated arrival and continuous-direction comparison

ADOPTED prospectively2026-09-11UTC after [R10](r10_paired_response_handoff.md)
completed with independent reviews and a verified material archive. Simulation
only under the user's method/development authorization. No previous experiment,
contract,result,denominator or unstarted slot is reopened.

## Scientific scope and evidence

R10 establishes selected same-input detector response benefit and finite control
coverage:102.008s recurrent response versus PDE censored360.8s on retained V9 B;
36/36 positives and0/48 negatives recurrent versus19/36 and4/48 PDE in the fixed
synthetic stratum. Its full-positive capped medians are42.024s and73.3635s.
This is exposed component evidence,not true empirical trapping-onset latency or
broad reliability. The old30% independent basin-entry target remains unavailable.

V12 is a new integrated arrival/direction study. Primary outcomes are measured
post-recovery global arrival and arrival time by arm,valid completed local
recovery,actual continuous acquisition,and direction error/availability under
the unchanged observed-phase stationary GESC reference. Preserve median<=30deg,
P90<=60deg and averaging availability>=0.8. The reference is not a general
spatial gradient. Integrated trajectories diverge after intervention;their
arrival differences do not isolate detector speed. R10 supplies that separate
component comparison. Preserve all old latency calculations and censored rows
as an explicitly secondary endpoint;never substitute R10 seconds into them.

Keep every planned confirmation run in its denominator,including arrival failures,
censored times and unavailable measurements. There are12 confirmation runs,
three per arm,with144 scheduled direction targets (72C,72D). Report the four
development runs and48 development direction targets separately. Retain all
exposure,eligibility,usable-output,averaging and paired-direction denominators.
Report per-arm/condition outcomes as well as existing pooled direction/continuous
acquisition and combined recovery summaries. Preserve distinctions between an
observed failure,valid censoring,no acquisition,and incomplete evidence.

## Prospective arrival clarification

GOAL_HOLD remains optional. A cancelled first verification does not invalidate
a later completed recovery followed by global arrival. V11 C supplies the
recorded rationale:one completed recovery episode,one active fill,owned escape
and arrival passed;only the first-verification path predicate failed.

For V12 only,retain the historical first-verification path declarations,
calculation and output as a diagnostic,while removing `required_state_path` from
success.all_of and each result-scope all_of. Keep all other11 predicates
mandatory:recording,cleanup,required events/event order,forbidden-state/event
absence,typed local recovery,fill cardinality,escape command ownership,
ground-truth goal association and post-recovery proximity. Existing
`local_recovery_stage` independently requires a complete contiguous recovery
path and existing typed fill/convergence requirements. Arrival rechecks recovery
evidence before the arrival sample. No stronger episode-specific timestamp join
is claimed. An incomplete escape,missing returned SEARCH,missing/ambiguous fill,
extra active cluster,invalid ownership or invalid source evidence still fails.

Make only the two necessary V12/schema14 predicate-binding exceptions in the
existing schema's declared-controller and staged-core sets. Preserve schema4
formal acceptance and every old version. No new matcher,interface,controller,
runner or runtime behavior is introduced. The old V11 C failure stays retained.

## Population and frozen runtime

Identity `m4-pilot-v12`,suite `m4_pilot_v12`,method
`recurrent_integrated_arrival_v12`,exclusive root
`/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v12/`.
Both this root and the source-work directory were absent on adoption.

| Arm | Detector | Acquisition package |
| --- | --- | --- |
| A | existing PDE | stationary |
| B | recurrent_geometry_v3 | stationary recurrent request |
| C | existing PDE | rolling GESC,moving-cycle coherence,centered verification |
| D | recurrent_geometry_v3 | same continuous package as C |

Reserve four visible primary nominal development cases,seed26091131. Reserve
twelve fresh secondary confirmation cases:nominal26091132,Gaussian sensor noise
std0.015 seed26091133,and sensor/pose delay0.10s seed26091134. Keep A/B/C/D order
within each block. Internal partition spelling `holdout` remains for compatibility;
these are fresh seeds on previously exposed conditions,not unseen geometries.
No replacements,retries or tuning after freeze.

Inherit V11's validated R5–R8 runtime,half-gain V6 controller,starts,fields,
speed limits,costs,fills,escape and disturbance settings. Include R9's validated
readiness-scoped motion attribution. Explicitly select existing controller-spawner
load recovery for V11 and V12 only;preserve V10 serialization. The0.5m arrival
tolerance stays evaluator-only. Preserve selectable legacy behavior and shared
controller/safety ownership. No algorithm parameter or numerical method changes.

## Existing owners and release contract

Register V12 in `m4_scenario.py` through the shared arrival-family lookup,exact
identity/method/seeds and version-specific release policy. Existing schema/runner
selectors inherit the family;verify all resolved arms. Preserve old outputs and
V11's first-opportunity feasibility gate exactly.

Use release policy `component_response_integrated_arrival_v1` for V12. Extend
existing `m4_workflow.py`, `m4_pilot.py` and `evaluate_m4.py` selections/reporting.
No parallel analyzer or acquisition pipeline. Bind R5–R8 source/integrated
receipts,R9 source/component validation,and R10 decision,job results,independent
reviews and material archive. Verify the exact R10 decision has all eight
criteria true and its selected nested input receipts match. Bind actual current
recurrent/PDE method sources/configuration to the unchanged component evidence.
Missing,changed,forged,failed or incomplete prerequisite evidence blocks V12.

Retain the existing four-development-run usable-analysis gate:four COMPLETE
acquisitions,all nine per-run scientific completeness checks,successful label/
both reference/summary jobs,exact24-target C/D products,authority/cleanup and
late nested hashes. At least B or D must complete valid recovery through arrival;
D must establish OBSERVED_CONTINUOUS_ACQUISITION. No-acquisition evidence cannot
satisfy that requirement. Require pinned R10 PASS in addition. Censored secondary
basin-entry latency is valid reported science in this new primary scope;it does
not satisfy or replace the old latency target. V11 still withholds on missing
development latency pairs. All twelve V12 confirmation cases remain untouched
until the single release succeeds. Incomplete development science closes V12.

## Finite validation,preparation and execution

Source work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/m4_v12_source_v1/`.
Preserve before copies and exact source diff. Run one named focused bundle with
230s work,5s termination allowance and260s inclusive maximum. Cover all16
resolved selections,seeds/budgets,new-policy enforcement,V11 byte parity and
unchanged feasibility denial,R10 missing/altered receipts,late nested mutations,
missing references/authority/D motion,R9 startup/zero-pulse pairing,and V12
successful later recovery versus historical first-path failure. Use existing
fixtures/owners and relevant historical version regressions;no whole-workspace
test campaign. Bind the selected runtime/environment/21 entry points and source
population before/after. Review,checkpoint and archive before preparation.

One exclusive preparation through existing owners has a600s ceiling. Audit the
resolved16-row contract and source bindings before dispatch. Use unchanged
`development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh`
with clean PYTHONPATH,domain201,localhost1,DISPLAY:0 and preserved shared daemon.
Python selection/evaluator edits require no build.

Keep720s recorder,900s inclusive case,45s shutdown grace,30s independent cleanup.
Each four-run block gets240s labels,45s each C/D reference,10s summary. Freeze/
report retain20s each,total science1400s and full suite15800s (4h23m20s).
Outer SIGINT15680s plus120s kill remains within that maximum. These are ceilings;
report actual elapsed time. The recent four-development-run block took about25
minutes,so the full comparison is a substantial additional simulation job.

Dispatch four visible development cases first;confirmation is a repeated batch
using existing rendering policy. Preserve every partial/failed outcome. Freeze
before confirmation;stop dispatch on required infrastructure/integrity failures.
Report all16 dispositions,actual denominators,scope and remaining limitations.
No physical/Pi/snapshot/V1,commit or push action is authorized here.
