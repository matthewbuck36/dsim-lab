# M4v12 closeout: retained arrivals and unresolved noisy behavior

Status: **CLOSED_INCOMPLETE**, 2026-09-11 UTC. The sole dispatcher session
53920 terminated and was reaped with exit 1 after 5081.954558 seconds
(84 minutes 42 seconds). Twelve recordings are COMPLETE; four delay slots
are UNSTARTED. Do not resume this experiment or replace its failed cases.
The broader detector and continuous-direction research goal remains incomplete.

The adopted [V12 plan](m4_v12_integrated_comparison_plan.md) and its frozen
contract remain the authority for this version. Arrival within the existing
evaluator-only 0.5 m global region is sufficient; GOAL_HOLD is optional.
All other recovery, ownership and evidence requirements remain effective.

## What the experiment established

| Condition | A: PDE, stationary | B: recurrent, stationary | C: PDE, moving | D: recurrent, moving |
| --- | --- | --- | --- | --- |
| Development, nominal | No arrival; recovery timeout | Arrived, 173.049 s | Arrived, 151.858 s | Arrived, 251.313 s |
| Confirmation, nominal | Arrived, 230.504 s | Arrived, 302.605 s | Arrived, 211.539 s | Arrived, 192.075 s |
| Confirmation, noise | Arrived; block science incomplete | Arrived; exact time unavailable | No fill, escape or arrival | No fill, escape or arrival |
| Confirmation, delay | Unstarted | Unstarted | Unstarted | Unstarted |

Acquisition-level confirmation outcomes are six arrivals, two nonarrivals and
four unstarted cases out of twelve planned. Development remains separate:
three arrivals and one nonarrival out of four. Recording and cleanup passed
for all twelve acquired cases. Arrival times above come from the two completed
scientific blocks. The final aggregate deliberately leaves all noisy-block
scientific outcomes unavailable because that block did not complete; do not
confuse its four science-qualified confirmation arrivals with the six arrivals
observed in acquisition receipts.

| Completed direction analysis | Median error | P90 error | Usable averaging / eligible | Eligible / scheduled | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Development C | 14.025° | 34.586° | 4/4 | 4/24 | PASS |
| Development D | 8.249° | 24.130° | 7/7 | 7/24 | PASS |
| Nominal confirmation C | 32.658° | 72.531° | 6/6 | 6/24 | FAIL |
| Nominal confirmation D | 5.683° | 25.495° | 5/5 | 5/24 | PASS |

C and D use the same direction package. Both established continuous acquisition
with zero mandatory stopped acquisitions in the completed development and
nominal blocks. Their different direction errors arise on different integrated
trajectories. Nominal C improved on instantaneous direction at all six eligible
targets but still failed the absolute error thresholds. Availability is measured
within the eligible subset, not all scheduled targets. The reference is the
observed-phase stationary periodic GESC response, not a general spatial gradient.

The independent [R10 study](r10_paired_response_handoff.md) remains the detector
component result: recurrent response at 102.008 s versus PDE censored at 360.8 s
on the same retained uninterrupted SEARCH input; 36/36 positives and 0/48
negative confirmations versus PDE 19/36 and 4/48 on fixed synthetic controls.
This supports a selected response benefit. It does not establish true empirical
trapping-onset latency or the original unavailable 30% basin-entry target.
Integrated arrival improvement is not uniform: nominal B was slower than A.

## Why V12 stopped

The D/noise reference worker returned 0 in 14.896358 s and wrote its numerical
output, but its process receipt recorded an unexpected descendant. The existing
single-process requirement therefore failed. Cleanup and kernel reaping proofs
passed; no timeout occurred. The dispatcher correctly withheld slots 13–16,
saved its incomplete ledger, and generated its report. No frozen result was
changed and no replacement run was launched.

Read-only source diagnosis found an existing import-time subprocess:
`run_scenario._repository_root()` invokes `git rev-parse --show-toplevel`.
The reference worker imports that owner directly and through full frozen-source
verification. This is a plausible explanation for the intermittent process
failure, but the retained descendant identity lacks executable/command text:
it does not prove which command PID 109098 executed. Do not retrospectively
accept its process integrity or broaden the allowed child population.

Two further scientific issues remain independently:

- Noisy C and D repeatedly entered verification but created no fill or escape
  before the 360-second local-recovery limit. Four recorded verification-stage
  admissions and returns to SEARCH locate the failure after admission. The
  small console/outcome files do not retain the exact rejection reason.
- B/noise passed acquisition arrival, but its cached label metrics have
  `arrival_measurement_complete=false`: the offline first proximity sample
  does not match the live first sample. Do not assign the live timestamp as
  the missing offline arrival time.

Noisy C's completed reference product reports median/P90 24.626°/77.419° and
averaging 11/12, failing P90. D's numerical product reports 33.273°/116.266° and
7/12, but its process qualification failed. These are retained partial products,
not a completed noisy-block analysis or replacement for the final aggregate.

## Exact evidence and recovery boundary

External root: `/home/mattb/Experiments/GESC-Gaussian/v2/`.

- `pilot/m4_pilot_v12/acquisition/slot_1.json` through `slot_16.json` preserve
  every disposition; `acquisition/acquisition.json` records the terminal failure.
- `pilot/m4_pilot_v12/analysis/block_0/` and `block_1/` are complete. Block 2
  retains labels and both reference products, but has no completed block receipt.
- `pilot/m4_pilot_v12/report/report.md`, `result.json` and `report_receipt.json`
  are the immutable existing-owner final report and aggregate.
- `development/20260911/m4_v12_source_v1/acquisition_execution_v1.json` records
  terminal exit and successful post-dispatch source-pin verification.
- The same work root holds completed development/nominal independent reviews,
  small acquisition projections, and `closure_runtime_v1.json`.
- [Source validation](validation/m4_v12_source.md),
  [preparation](validation/m4_v12_preparation.md), and
  [execution record](validation/m4_v12_execution.md) retain exact commands,
  hashes, tests, failures and skips.

Source validation retained the original 784 passes and two obsolete future-version
fixture failures, then passed the corrected two parameterized functions (10/10;
eight overlap the original passes). This covers the 786-case selection; it is
not a claim of one 786-pass run. The 866 source/helper pins and 21 selected
entrypoints were stable. No production source changed during the comparison.

All known dispatcher/reference owner PIDs are gone. The post-exit procfs snapshot
found no Gazebo executables or selected installed ros_esc node processes. The
pre-existing shared ROS daemon PID 24080 remains untouched. No runtime is active.

Branch: `feature/gesc-gaussian-robustness-v2`; HEAD:
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`. All task changes remain uncommitted.
No physical, Pi, snapshot, V1, commit or push action was performed.

## Next bounded work

Preserve V12 as closed. Use a separately declared development iteration on retained
inputs to establish the subprocess cause and correct it through existing owners,
extract the exact noisy verification rejection evidence, and diagnose B's arrival
timestamp mismatch. Define budgets and decision rules before new execution.
Do not run another matrix to recover context or claim broad reliability from
these fresh seeds on previously exposed conditions. The four development runs
and 48 targets remain separate from all twelve planned confirmation runs and
144 targets, including failures and unavailable measurements.
