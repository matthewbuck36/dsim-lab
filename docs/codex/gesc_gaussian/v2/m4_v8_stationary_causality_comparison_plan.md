# M4 V8 comparison after stationary causality correction

Status: ADOPTED FOR SIMULATION IMPLEMENTATION, 2026-09-10 UTC.
The active user goal authorizes recommended bounded corrections and continued
comparison work. This plan admits fresh V8 routing and source validation;
preparation/acquisition remain dependent on the gates below.

## Verified prerequisites

The stationary causality source milestone is closed: 325 current-source tests
and actual installed CLI PASS; one retained V7 B verification passes 52/52,
with only the declared causal check and consequent passed/failures differences.
All 11 original inputs and 638 source files remain unchanged. Read
[m4_v8_stationary_causality_handoff.md](m4_v8_stationary_causality_handoff.md)
and its validation record. Material source archive:
checkpoints/m4_v8_stationary_causality_source_v1/manifest.json, SHA256
6d35c50356baa29201d77b019a1d521a4d0e32f1147ceff5aa8c373c7752f476.
All source jobs are terminal. The draft adopted here is retained unchanged at
builds/m4_v8_stationary_causality_v1/next_comparison_plan_draft_v1.md, SHA256
a4787bdc645992ae700b24de3f7020479d85364ab572b6d05d2e31de71502de3.

V7 remains 1 COMPLETE / 1 INCOMPLETE / 14 UNSTARTED, no science or holdout
release; closure manifest SHA256
ea3fa730800fc55d7d07878b2794c9c39e578a113b80e876898f65061d4f1359.
Both research goals remain open. The correction establishes recording authority,
not recovery behavior: both V7 development trajectories hit the 360 s Stage A
limit. Do not add historical V7 test counts to newly executed source totals.

## Exact fresh identity and unchanged comparison

Use experiment m4-pilot-v8, suite m4_pilot_v8, exclusive root
/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v8, case prefix m4_v8_,
and run IDs m4-pilot-v8-slotNN-ARM-SEED. Keep default experiment/method
m4-pilot-v1. Keep subreaper_group_v3, its exact graceful signal strategy and
all existing kernel/process/recording/cleanup gates. Use a new build directory
builds/m4_v8_stationary_causality_comparison_v1 for this amendment. Domain200 is a
prospective environment reservation only; finalize its exact clean command
before execution and require all domain199 source work terminal first.

All16 slots retain the V7 arm/geometry/condition/seed/visibility order:
development primary nominal A/B/C/D seed26090801; holdout secondary nominal
26090802, noise26090803, delay26090804, each A/B/C/D. Retain all four topology
receipts and existing geometry, model, source/start/bounds, .015 noise/.10s delay.
Reuse v6_controller_configuration(), profile m4_gain_half_control_v6 and the
existing gain-half JSON SHA256
 e94ea14af0ececd559902d950806ed2934e30099c61a2f867b76f8b1e88f0606.
No renamed controller helper/profile or new JSON: k_vx=.5, k_wz=5,
max_vx=.1, max_wz=.5 remain fixed. B/D heartbeat stays True; A/C remains False.
Retain centroid_two_block_v2 W6/epsilon.18/radius.5, the C/D moving direction
policy/.75/.15 guards and VERIFY12s, all-arm interior fallback/min.50, disabled
RECENTER, original stage/goal/fill predicates and all scientific methods.
No new gains, algorithm, producer, schema, model, thresholds or gates.

## Minimal source ownership

Source locations verified at draft time; line numbers may move.

- m4_scenario.py:26,50-61: admit exactly V8 and map8 to existing group owner.
  Extend the eight existing V5/V6/V7 inherited-control selections at87,94,111,
  207,217,277,294,315 to include V8. Preserve per-call template hashing/cache,
  exact effective-control validation, boolean types and mapping insertion order.
- m4_workflow.py:120,125,256,318: extend primary topology/controller preparation
  and verification selections. Add only the newly adopted comparison-plan pin
  to collect_sources; preserve the already-pinned causality source amendment.
- run_scenario.py:2895,6218: add m4_pilot_v8 to the existing centroid selector and
  strict suite/process-mode mapping. No changes to the general recorder,
  controller resolver, cleanup, topology or classifier owners.
- run_m4.py, evaluate_m4.py and m4_pilot.py already derive experiment identity
  from the central owner; no explicit V7 production literal was found there.
  Verify their boundaries with fixtures; do not edit them without a demonstrated
  remaining guard. The completed causality validator stays held, unchanged.

## All unsupported-future fixture tokens

A search across ros_esc/test/*.py found exactly nine V8 negative literals in
seven existing modules. Preserve originals, then replace only these unsupported
future V8 tokens by V9; retain all positive cases and assertions:

| Module | Current line(s) | Literal |
| --- | --- | --- |
| test_m4_v2_subreaper_routes.py |96| m4_pilot_v8 |
| test_m4_v3_shutdown_routes.py |75| m4_pilot_v8 |
| test_m4_v3_versions.py |211| m4-pilot-v8 |
| test_m4_v4_versions.py |135,158| m4-pilot-v8; m4_pilot_v8 |
| test_m4_v5_versions.py |167,190| m4-pilot-v8; m4_pilot_v8 |
| test_m4_v6_versions.py |147| m4-pilot-v8 |
| test_m4_v7_versions.py |128| m4-pilot-v8 |

The new stationary-causality module name is not a future-version negative.
Do not globally replace historical V8 references or existing cross-version faults.
Repeat the literal-only source search at the actual edit boundary, not a test run.

## Small meaningful source acceptance

Before any routing edit, preserve the three production owners, seven affected
fixture modules and final source map. Once under30s, adapt the retained pure
capture owner to record V1-V7 scenario YAML plus112 schema-expanded launch and
metadata rows. Mock topology qualification and forbid model/ROS/acquisition
owners. Preserve exact output hashes, including YAML insertion order, not only
unordered mapping equality. Read retained topology receipts; do not derive fields.

Add test_m4_v8_versions.py and test_m4_v8_workflow.py using the existing V7
synthetic setups. Use module-scoped pristine baselines and deepcopy per fault;
prepare mocked V7/V8 once each, not per case. Require exact V1-V7 generated
bytes and V7-to-V8 all16 resolved controls/stages/launch/metadata equivalence
with substitutions restricted to experiment/root/case/run identities and their
case keys. Keep the V6 controller/profile strings untouched. Exercise all16
config/heartbeat/effective-control/launch-only/metadata faults, receipt/hash
substitution, V1-V7 context rejection, V9 rejection, selected process proof and
original method/budgets. Preserve all192 targets and unavailable original-goal
status when science is absent; reject wrong-version acquisition/analysis/release.

After held-source review, run one180s focused bundle containing the two new
V8 modules and all seven changed old fixture modules above. This directly tests
every changed future-negative fixture. Retained V7 named-case times suggest
approximately100-120s for comparable coverage, not a runtime guarantee. Avoid
another entire test_m4 matrix: the previous broad bundle exhausted its cap.
One240s consumer bundle contains exactly test_m4_dispatch.py,
test_m4_evaluation_cli.py, test_m4_pilot_metrics.py, test_m4_science_job.py,
test_m4_workflow.py, test_m4_centroid_event_evaluation.py and
test_q7_recording_selection.py. Reuse the just-completed stationary causality,
clock-range and unchanged producer/transport evidence under exact source-delta
bindings; distinguish that retained evidence from newly executed totals.
Record exact unique named JUnit cases; failures/skips/unidentified rows remain
visible. No invented inventory run, cap extension, automatic retry or dropped
failure. A fresh issue needs a saved bounded amendment. Keep actual installed
run_scenario/record_run --help under60s and exact clean Humble-Q2-Q5 environment.

## Frozen execution and final report

After source/CLI PASS, handoff/checkpoint/archive: one600s preparation, one30s
frozen audit, prepared archive and exact one-time dispatch release. Bind new
source/test/plan bytes, selected controller JSON, installed wrapper/entrypoints,
all16 argv/scenarios, four topology receipts and geometry/model/cost receipts,
plus V7 closure and completed causality source archive. No rebuild solely for
Python context. Never reuse an old pilot root or resume an old reserved slot.

One existing dispatcher remains15300s inclusive:720 recording,900 case,
45 shutdown and30 cleanup reserve. Science remains900s total: labels120/block,
references45/C-D slot, summary10/block, freeze/report20; maximum40000 observations.
Initial release permits four development slots only. Four safe complete
acquisitions plus attempted-science outcome ledger and held configuration may
release12 still-unstarted holdouts once. Scientific failure/unavailability is an
honest outcome; integrity failure closes V8. No tuning/replacements after freeze.
Retain16 outcomes, six holdout latency pairs/12 endpoints and192 direction
targets (24 per C/D run at15+30k). Original goal predicates and supplementary
sequence/stopped-acquisition checks remain unchanged. This plan does not establish research qualification. Execute each finite
command only after its stated source/evidence prerequisites pass.
