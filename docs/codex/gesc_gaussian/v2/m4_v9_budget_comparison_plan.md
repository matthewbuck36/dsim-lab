# M4 V9 budget comparison amendment

Status: ADOPTED FOR SIMULATION IMPLEMENTATION, 2026-09-10 UTC.
The active user goal authorizes recommended bounded corrections. V8 closure
audit PASS1e470d3da35035f092a57a7973853ae4a4ef581752a5f835e63185e2ab48751c,
context/checkpoint PASS, and material closure archive PASS
5544a2cf123c69fc77a0bb1e04550ac87f7a1640e193f09167b470ee68502ed5
satisfy adoption prerequisites. That archive retains411 repository files,
200 external references and a verified1614974-byte tar in1.058293623s/60.
Source baseline/correction/routing are admitted; later stages remain gated.
One coherent source milestone combines the demonstrated admission arithmetic
correction with fresh V9 routing; there is no separate correction-only release.

## Closed evidence and verified prerequisite

The V8 comparison source evidence remains 1,232 unique PASS cases on 641 stable
source hashes and 21 installed bindings, including actual installed CLI PASS.
Its source_validation_v1.json SHA256 is
 ae68f367d4df0142c4b44e171d9837677500491e0527c5db62a99fafa8b61867.
Focused: 1,035 cases / 132.999971240 s outer under180; relevant:197 cases /
19.177910140 s outer under240. These are retained evidence, not V9 test counts.
All paths in this draft are relative to /home/mattb/Experiments/GESC-Gaussian/v2
unless identified as repository paths.

The sole V8 dispatcher is terminal: all16 UNSTARTED, zero actual acquisitions,
zero bags, no block science or holdout release. All35 finalized pilot files are
retained under pilot/m4_pilot_v8. The internal acquisition elapsed time is
1.0280601029953687 s; the enclosing command took approximately4.740 s. Do not
merge these timing scopes. Its original acquisition.json SHA256 is
8fa63547100fa671b1c1301cd961dc1318004fe8ffb390cfaba2b01fbbcf8f46.
The frozen contract is
76bc335518f936e26f2d5f8cac1591d3f28cdfee0e37b94467a4e3ea777a1a9a.
Both original research goals remain unproven. V8 must remain failed/unstarted;
no old root or reserved slot is resumed or replaced. The exact V8 closure manifest at checkpoints/m4_v8_closed_incomplete_v1/manifest.json
is verified by the hash above. The original unadopted draft remains retained,
SHA2566a0b41ff84a7592cd79fb3ea7a83efdc529b826483cc7130d377986d4c25b0e9.

## Demonstrated source defect and bounded correction

Existing repository owner docs/codex/gesc_gaussian/v2/tools/run_m4.py SHA256
621af734f0b182ee166d594b22c90ada16721feca7a6ec232d6dc065393b9093 sets
started at line224, suite_end=started+15300 at225, and first case_start=started
and case_end=case_start+900 at232-233. Line234 subtracts the rounded absolute
case end from the separately rounded suite end before comparing reserved time.

V8 recorded started60906.478755597 and suite_end76206.478755597; first case_end
is61806.478755597. Python arithmetic gives14399.999999999993, less than14400
by7.275957614183426e-12 s, exactly one ULP at started. No elapsed acquisition
work caused this rejection. V7 started56063.905715417 gives exactly14400 and
its first slot was admitted. Original started.json receipt hashes are
V8 14e6271867363a7fdc972f85fe4775481d9141ef3111183f35d4fd9831b6c724 and
V7 848ee29a066c0116dec64542936633ac8502e630d520bed9598129e2d9e90566.

Replace only the admission comparison with the algebraically equivalent elapsed
budget predicate, directly in the existing dispatcher:

```python
if case_start - started > 15300. - ((16-index)*900. + remaining_science):
    raise TimeoutError('M4 remaining case/science envelopes do not fit suite deadline')
```

The right-hand side is the allowed elapsed time after reserving this and every
remaining case plus remaining science. The selected budgets are exact integers:
remaining_science is900,680,460,240,20, reduced by220 only after each completed
four-case science ledger. At first admission both sides are exactly0. No epsilon,
rounding tolerance, first-slot bypass, shortened reserve, deadline extension,
clock-origin reset or duplicated budget helper is introduced. Absolute suite_end,
case_end, cleanup deadlines, post-case checks and final inclusive deadline checks
remain byte-identical. The correction applies through the existing common owner;
legacy selectable controls and output schemas remain unchanged. It corrects only
roundoff-sensitive admission behavior and still rejects actual budget overruns.

## Before-edit proof and baseline

After adoption and before production edits, preserve all four production owners,
all affected existing tests and exact 641-source map in a fresh external build
builds/m4_v9_budget_comparison_v1. Keep the original V8 source/evidence immutable.
Once under30 s, adapt the existing pure pre-edit capture to V1-V8:128 expanded
rows with exact scenario YAML ordering, launch and metadata bytes. Existing
numerical qualification is mocked; model, ROS and acquisition owners are forbidden.
No field derivation or expensive past matrix is used for recovery.

Add one focused test_m4_v9_budget.py using the actual existing frozen_dispatch
fixture from test_m4_dispatch.py. Reuse its synthetic complete-run owner and mock
clock; do not reproduce the admission formula in a separate function or accept
AST inspection as the behavioral proof. Preserve existing fixture bytes; if a
minimal fixture exposure is necessary, retain it and every original assertion.
Before changing run_m4.py or version routing, run this held module once under60 s
against the unchanged dispatcher. Expected failure: the actual retained V8 origin
cannot dispatch its first slot. Preserve every baseline outcome and whole tested
source, with no xfail or rewritten old result. Require the expected cause, not
merely a nonzero exit, before implementing the one combined correction/routing.

Finite meaningful cases:
- Actual dispatcher at saved V8 and V7 origins, retaining all16 synthetic outcomes
  and fixed absolute suite/case/cleanup deadlines; the V8 case exposes the defect.
- Exact full case900/science220 fit at fixture origin100, requiring all16 slots,
  all four block ledgers and one development release, with original total15300.
- Before/equal/next-representable-after the first development-science boundary:
  origin100, four cases consume3600, allowed next clock is3920. Set fixture
  science_elapsed to target_clock-3700 so addition does not swallow the fault.
  The just-after case must stop before slot5, with4 completed/12 unstarted.
- Keep the existing case900/science221 overrun rejection and relevant per-case,
  source, integrity and exclusive-output failures. Add no flaky wall-time test.

Review the baseline and source diff before correction. A different failure or
unavailable required result stops the dependent edit/release pending a saved
bounded amendment; it does not justify an automatic retry or larger cap.

## Fresh identity and four production owners

Admit exactly experiment m4-pilot-v9, suite m4_pilot_v9, exclusive
pilot/m4_pilot_v9, case prefix m4_v9_ and run IDs m4-pilot-v9-slotNN-ARM-SEED.
Default experiment and scientific method remain m4-pilot-v1. Prospective domain201
is reserved for the full clean Humble/Q2/Q5 command only after domain200 work is
confirmed terminal; finalize exact commands before execution.

1. m4_scenario.py: add V9 to the central version allowlist and mode mapping; extend
   the eight existing inherited topology/controller/interior/profile selections.
   Keep helper v6_controller_configuration(), per-call template freshness, exact
   effective controls and boolean checks. Do not rename the profile/controller.
2. m4_workflow.py: extend its four inherited topology/controller prepare/verify
   selections and pin this adopted comparison amendment in collect_sources.
3. run_scenario.py: extend only the centroid suite allowlist and strict suite/mode
   mapping to V9. General controller, lifecycle, recorder and cleanup owners stay
   unchanged.
4. run_m4.py: the elapsed-budget predicate above only. All other dispatcher gates,
   public release, shutdown ownership, holdout seal and finalizer remain unchanged.

No evaluate_m4.py or m4_pilot.py edit is planned: their version boundaries derive
from the central owner. Prove their V9 behavior through existing-owner fixtures.

Read-only literal search found exactly10 unsupported-future V9 tokens in8 modules:

| Existing test module | Current line(s) | Tokens to change to future V10 only |
| --- | --- | --- |
| test_m4_v2_subreaper_routes.py |96| m4_pilot_v9 |
| test_m4_v3_shutdown_routes.py |75| m4_pilot_v9 |
| test_m4_v3_versions.py |211| m4-pilot-v9 |
| test_m4_v4_versions.py |135,158| m4-pilot-v9; m4_pilot_v9 |
| test_m4_v5_versions.py |167,190| m4-pilot-v9; m4_pilot_v9 |
| test_m4_v6_versions.py |147| m4-pilot-v9 |
| test_m4_v7_versions.py |128| m4-pilot-v9 |
| test_m4_v8_versions.py |129| m4-pilot-v9 |

Repeat the narrow literal search at the edit boundary. Preserve malformed-version,
old-context and every positive fixture exactly; no global replacement. All old
V1-V8 generated YAML/launch/metadata bytes must match the pre-edit128-row capture.

## Unchanged experiment and finite source acceptance

Reuse exact V8 16-case order, geometry/source/start/bounds, four topology receipts,
seeds26090801-04 and visibility. Preserve original controller JSON plus selected
V6 gain-half JSON SHA e94ea14af0ececd559902d950806ed2934e30099c61a2f867b76f8b1e88f0606,
profile m4_gain_half_control_v6, k_vx.5/k_wz5/max_vx.1/max_wz.5. B/D heartbeatTrue,
A/Cfalse; centroid_two_block_v2 W6/.18/.5; moving C/D .75/.15 and VERIFY12;
all-arm interior fallback/min.50, RECENTERfalse, .015noise/.10sdelay and all
stage360+300/goal/fill/scientific predicates remain fixed. Keep subreaper_group_v3,
strategy initial_unreaped_root_group_sigint_then_adopted_pidfd and all eight kernel
proof flags, strict recording/source authority and performed cleanup checks.

New test_m4_v9_versions.py and test_m4_v9_workflow.py use pristine module-scoped
baselines and deepcopy per mutation. Prepare mocked V8/V9 once each. Require
all16 identity-only control/stage/argv/metadata parity; every row's config/hash,
heartbeat, effective control, launch-only and metadata faults; earlier V1-V8
context rejection and unsupported V10; exact acquisition, science, public release
and 12 sealed holdout boundaries; full16-slot/192-target missing-science report.
No numerical owner or ROS graph is run by these synthetic fixtures.

After independent held-source review, one180 s focused bundle contains exactly:
- test_m4_v9_budget.py, test_m4_v9_versions.py, test_m4_v9_workflow.py;
- the eight changed existing modules in the table above.

The unchanged test_m4_v8_workflow.py is retained evidence rather than a duplicate
focused run: new V9 workflow fixtures exercise V8/V9 full preparation parity.
The current focused1035 count includes its143 cases/40.137 s of named-case time;
V8 versions contributes80 cases/6.606 s. Replacing the paired workflow population
and retaining every changed negative-token module suggests roughly140 s plus the
small budget module, based on the latest133 s outer receipt. This is a prospective
feasibility estimate, not a cap extension or guaranteed timing. Exact collected
named-case counts are reported only after execution; no invented inventory run.

One240 s relevant bundle contains exactly test_m4_dispatch.py,
test_m4_evaluation_cli.py, test_m4_pilot_metrics.py, test_m4_science_job.py,
test_m4_workflow.py, test_m4_centroid_event_evaluation.py and
 test_q7_recording_selection.py. These197 current cases took19.177910140 s outer;
the actual dispatcher fixture, rather than just a formula test, is mandatory.
Do not recover an entire historical matrix. Bind unchanged recording-causality,
clock-range, controller/producer/transport evidence to exact source deltas and
keep retained counts separate from new passes. Preserve all failed/skipped or
unnamed JUnit rows, enforce nonzero failures, and allow no silent retry/drop/cap
increase. Baseline60 and focused180 are distinct declared source jobs.

Run actual installed run_scenario/record_run --help once under60 s after source
PASS, with exact current installed/source bindings and full clean environment.
Source maps and installed bindings must stay unchanged across each final job and
agree across final focused/relevant/CLI evidence. No rebuild solely for Python
context, real Gazebo E2E, bag read, model job or new numerical replay is admitted
by this source milestone.

## One frozen execution after source closure

One source handoff/checkpoint/archive under60 s closes the combined correction
and V9 routing. Bind the exact V8 closure/source/prepared chains and all new
source/test/plan/helper bytes. Then one600 s existing preparation, one30 s frozen
audit, prepared checkpoint/archive under60 s and exact one-time release under30 s.
Bind all16 scenarios/argv, four topology receipts, original geometry/model/cost,
unchanged V6 selected JSON/profile, installed wrapper/entrypoints and final source
map. Do not reuse old prepared contracts or derive topology merely for context.

One existing dispatcher remains15300 s inclusive, enclosing environment setup:
recording720/case900/shutdown45/cleanup30; science900, labels120/block,
references45/C-D run, summary10/block, freeze/report20, maximum40000 observations.
No refreshed or extended deadline is permitted. Initial release covers only four
visible development slots. Four safe complete runs and their attempted-science
outcome ledger, frozen settings/source and12 unstarted holdouts may release the
holdouts once without tuning or replacement. Scientific failure/unavailability
remains distinct from integrity failure. A terminal gate closes V9 honestly.

Retain all16 outcomes, six holdout latency pairs/12 endpoints and192 direction
targets:24 per C/D run at15+30k. Preserve original goal denominators and all
supplementary fill/sequence/stopped-acquisition checks. No claim of either
research goal follows from fixing dispatcher admission. Execute no stage until
its stated source/evidence prerequisites pass.

## Baseline fixture clarification before execution

The reviewed fixture reuses frozen_dispatch with its valid V1 synthetic contract;
V7/V8 name the saved clock origins, not routes prematurely admitted for baseline.
Exactly13 cases are declared: full16 exact-fit schedules at100 and both saved
origins; the unchanged221s science overrun; nine before/at/after representable
clock positions following4/8/12 complete cases. For the latter set, origin0 and
explicit elapsed points3820/7640/11460 isolate strict admission: the injectable
science callback sets the observed fake clock directly so arithmetic addition
cannot erase the one-ULP fault before the dispatcher observes it. No production
budget formula is duplicated. This expands the first-block challenge to all
three subsequent-dispatch boundaries within the same60s baseline cap.
Prospective expected baseline:10PASS/3FAIL (savedV8 origin and the first two
one-ULP overrun rejections); record actual identities and causes before correction.
No prior result or source is changed by this clarification.
