# M4v10 source handoff

2026-09-10: source and retained-motion validation PASS. The next action is
exclusive V10 preparation and review through the existing workflow; no M4v10
preparation, acquisition or full comparison has run. All test/helper sessions
are terminal/reaped. Branch V2 at3369cfc, uncommitted; no push or physical work.

Read [the adopted plan](m4_v10_arrival_comparison_plan.md) and
[exact validation](validation/m4_v10_source_validation.md). They supersede the
R4 handoff's pending comparison-source work. The current implementation uses
method `recurrent_arrival_v10`, experiment `m4-pilot-v10`, and release policy
`usable_four_arm_analysis_v1`. A/B use PDE/recurrent stationary verification;
C/D use PDE/recurrent with the same rolling and centered package. Global arrival
within the evaluator-only0.5m tolerance is success; GOAL_HOLD is optional.
Safety, actual local fill/escape and restored SEARCH remain required.

Four primary nominal development slots use seed26091011; twelve secondary
confirmation slots use26091012/13/14 for nominal/noise/delay. Conditions and
geometry are previously exposed; these are fresh confirmation runs, not unseen
conditions. The historical internal `holdout` partition spelling remains.
All old V1–V9 and selected D02/D03/B02 evidence stays unchanged.

Runtime environment:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh`.
Use `env -u PYTHONPATH` and source this script. It preserves Q5's21 installed
entry points/canonical source plus the new request and schema2 guidance overlay.
Do not use the old pairing test environment that caused B01's entry-point failure.

Source validation root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/m4_v10_source_v1/`.
`source_validation_combined.json` is the passing receipt for608 unique checks:
607 initially passed, one new V9 byte-parity fixture failed because of key
ordering, then the corrected32-check module passed. Production and installed
hashes were unchanged across jobs. The failure and both raw receipts remain.
Cached D02 motion passed the actual new owner in4.244722s with full original
artifact/hash binding and no bag decode. Real installed and comparison CLI
help checks all passed in5.850403s. No further test or retained-data scan is
needed solely to recover this source boundary.

The consistent frozen prospective budgets are240s labels per block,45s per C/D
reference,10s summary,40s total freeze/report (20s each),1400s total science and
15800s suite. Keep900s cases,720s recorder,45s shutdown,30s cleanup,360s Stage A
and300s Stage B. Do not copy the short one-case180/120s stages into the comparison.
The extra release reserve was adopted before tests from the old4.066s release
measurement and the new repeated source/input checks. Actual V10 timing remains
to be measured. The old120s labels benchmark remains failed.

Preparation should use the existing `m4_workflow.py prepare --experiment-version
m4-pilot-v10` under its finite600s envelope, in a separately recorded invocation
with explicit environment/domain and helper/source pins. Check its CLI spelling
from the retained help log before dispatch. Freeze the actual topology/schema/
launch/recording selections and review all16 resolved cases. Preserve the
exclusive root `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v10/`:
check for any existing started/prepared receipt before invoking; never retry
an attempted preparation or case unchanged.

The existing public dispatcher requires reviewed preparation, passing source
validation and a verified source archive. The archive wrapper passed through
`source_checkpoint` must expose the existing `archive_verified=True` contract;
do not mistake a source tarball alone for that release receipt. Record the
exact new preparation/audit/initial-development release before execution.

The new gate requires four COMPLETE development acquisitions, completed labels,
both complete24-target reference products, completed summary, exact selected
analysis/authority/measurement checks, late immutable source/input receipts,
at least B/D local recovery through arrival, and D observed continuous
verification/design. Complete baseline failure and censored/unexposed outcomes
are valid results. Missing inputs/authority, analysis timeout, incomplete
recording or failed cleanup blocks confirmation. No method tuning or replacement
is permitted after freeze. Keep all16 outcomes, including unstarted slots.

Prior empirical evidence: [B02](validation/r4_stationary_integrated_02.md) reached
the global region at172.634s and analyzed in43.391s; [R3 moving evidence](r3_arrival_development_handoff.md)
records D02/D03 arrival and paired direction references. The frozen detector
passed36 positive and48 negative controls with12 gray histories. These selected
results support comparison development; full V2 qualification and broad claims
remain open. Current `status.md` records the material archive after creation.
