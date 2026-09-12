# V7 comparison source and release validation

Status: IN_PROGRESS. Read ../m4_v7_clock_range_comparison_plan.md.
Clock-range milestone closed and archived: manifest5befd6c9...e1e7;
171sourcePASS plus one retained validation49.042393395 s with exact48-check
report/all8inputs unchanged. V6 remains CLOSED_INCOMPLETE.

## Prospective source groups

External root: /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v7_clock_range_comparison_v1/.
Use source_wrapper_draft_v1.json for exact file selections and helper hashes.
Clean Humble->Q2->Q5 plus extremum-seeking/src, ROS_DOMAIN_ID198,
ROS_LOCALHOST_ONLY1, DISPLAY:0. Source/tests must be held/reviewed before release.
No concurrent tests/ROS/acquisition. Preserve a failed label before correction.

Focused180 s: test_m4_v7_versions.py, test_m4_v7_workflow.py, test_m4_v6_versions.py, test_m4_v6_workflow.py.

Relevant240 s: test_m4_centroid_event_evaluation.py, test_m4_dispatch.py, test_m4_evaluation_cli.py, test_m4_objective_inputs.py, test_m4_pilot_metrics.py, test_m4_science_job.py, test_m4_v2_subreaper_adversarial.py, test_m4_v2_subreaper_routes.py, test_m4_v2_versions.py, test_m4_v3_recorder_shutdown.py, test_m4_v3_shutdown_routes.py, test_m4_v3_versions.py, test_m4_v4_confirmation_mirror.py, test_m4_v4_versions.py, test_m4_v5_moving_escape.py, test_m4_v5_typed_fill_authority.py, test_m4_v5_versions.py, test_m4_v6_centroid_heartbeat_selection.py, test_m4_v6_centroid_heartbeat_transport.py, test_m4_v6_controller_selection.py, test_m4_workflow.py, test_m4a_execution_deadline.py, test_q7_recording_selection.py.

This is all other current M4 modules plusQ7recording selection, excluding the
unchanged clock-range module already validated in the closed source milestone;
its exact owner/fixture input hashes and receipts will be bound at closure.
No recorded failure is excluded. Existing Gazebo E2E filter stays unchanged.
The wrappers record full source before/after and21 installed before/after
bindings. Use outer timeout at cap-1 with1-second kill allowance, inner pytest
at cap-15/10-second kill allowance. Actual run_scenario and record_run --help
share one60-second inclusive CLI cap after source tests. No build indicated.

One30-second preedit pure capture of V1–V6 scenario/population/identity and96
expanded launch/metadata rows must pass before production edits. Numerical
qualification is mocked, field-model/ROS initialization forbidden. Source
copies and captured bytes remain external immutable evidence.

No capture/source test/preparation/acquisition has executed at this entry.

## Preedit capture PASS; implementation started

One capture root88426 terminal0,4.082757622 s/30 s: six populations and96
expanded launch/metadata rows,633sourcepins/copies/plan/topology inputs stable.
Receipt version_routes/capture_preedit_v1_receipt.json SHA256
68c450ff6274005f39138ae3954f1b4c8e3d3d58c197378d3b84d7bb63bd844e.
Actual root capture_release_v1.json SHA256
2745d420c4d9e3fccbb5a3df4347f2fff7cd5f4acd6e146e4dc7e6c5212e3926
uses29-second SIGINT/1-second kill over the entire clean shell (30 s inclusive).
The owner's later capture_hold_v1.json proposed28/2; that alternate argv was
never executed. Same independently reviewed d280651f... capture helper; no retry.

Existing workflow now includes V7 in its four topology/controller preparation
and frozen-verification branches, plus the adopted-plan pin. No helper/config/
launch reconstruction behavior changed. Other owners are implementing the
reviewed route and negative-fixture changes; source tests remain unreleased.

## Held source and first focused release

Three production owners changed only the reviewed version selections; no
controller/validator/numerical/deadline code changed. Exact runtime holds:
m4_scenario dbae35268ebc9c28e53390d9f2d8e95b006fc0f2b33a766cd85e20faa6237ecb;
run_scenario48795cf7c4fdea7269d78d27aba44a223b01a7f49acc5a3e7616b030ce9371cc;
workflowa1c92717a51bf19f13f1902ceb5ba21fd05ba75162d95368a521a25bea6639fe.
Six future-negative tokens across four retained files now use unsupportedV8.

Independent fixture review found a generated-YAML ordering coverage gap before
execution. Two lines (yaml import and exact safe_dump bytes assertion) were
added; originalheldfixture retained. Final versionhold SHA256
e4cdc585d967285d3e87110d3a580911baba16db5caa2251b5b31abe9ea6f260;
versiontest4d49317ca81184a22c86cd7c09225a5acf80e99505b6843428bb030f5060f32a
has79 intendedcases. Workflowtest5f9d59c74405d5881b6ff2027305078ca9da8ba2d1df2bbc618090bfaf67ff71
has105 intendedcases. These are prospective counts before pytest; no test
failure was dropped. Existing V6 versions/workflow modules complete the bundle.

First focused_release_v1.json SHA256
8cb6de4f5f26cf7ecd3d4b348b2330ae286dd009e25ae0c2f3cb1e13dccc0ba9
binds636sourcepins, reviewed holds/wrapper and exact command_argv. Root16869 is
running this single focused_v1 under180s. source_commands_v1.json places the
outer179s/1s timeout before the entire clean shell. Sources remain held.

Prospective preparation helper review also corrected a descriptive audit field:
V7 inherits V6 gains/heartbeat, so changes_from_parent became inherited_v6_selection.
This affected description only; copies of both drafts and pre-correction helpers
are retained. Final preparation_helpers_hold_v1.json SHA256
9d98d80f6f6e0ae136375272350a3b320dbdb8378693b34d7adb21dbbc951782
is reviewed with existing600/30 commands, samegates and V6 config/profile bytes.
No preparation/audit/archive/dispatch helper in this newbuild has executed.

## Focused PASS and broader release

Focused_v1 terminal0:620PASS in62.50 s pytest/63.206025104 s wrapper,636source
before/after equal and21 actual installed bindings unchanged. Release source
map equals both actualmaps. No warnings/failures/skips in its terminal output.

Relevant_v1 released once through source_commands_v1.json under240 s;
relevant_release_v1.json SHA256
c2cdb531894af2e504cec6ee7a0eeddf7b40a5a615d1f1c8d4ab4b6e0a758837.
Root74005 is live; no concurrent ROS test/acquisition. Read terminalreceipt
before the one actual CLI check. Preparation is still unreleased.

Independent non-importing source_delta_audit_v1.json SHA256
1d70d28396de76a1b6bed218c60b00434bd84ea033ff7ae7c451264779815c98
confirms633closedclock-range pins→636current:7changed (3owners+4future-test
files),3added (2V7tests+newplan),626unchanged and no removed source. Actual
validator/test_experiment_recording/newclock-range test and bothJSONs remain
byte-identical. The whole source map differs; the earlier171checks retain
their original scope/map and will not be added blindly to current test totals.

## Relevant_v1 CLOSED_INCOMPLETE

Root74005 terminal124. Existing inner pytest cap stopped the run after224.94 s;
wrapper225.749386093 s, within original240 s inclusive cap. Source636 and
installed bindings stayed unchanged. Terminal pytest:646PASS,2FAIL. Named
JUnit rows agree648 total/646PASS/2FAIL. A final anonymous testcase with no
name/class was incorrectly counted as PASS by the inherited external wrapper,
which prints647PASS/649elements; do not use that number. Original receipt/XML/
log remain unchanged, including this reporting discrepancy.

Failures are unsupported-future fixtures still expecting m4_pilot_v6 rejection:
test_m4_v2_subreaper_routes.py::test_centroid_evaluator_exact_version_allowlist,
test_m4_v3_shutdown_routes.py::test_evaluator_selector_exact_v3_admission.
The frozen V6 runner already admitted V6. Independent source review supports
only two literal future-token changes to m4_pilot_v8, retaining assertions and
positive cases. No runtime selector correction is indicated by these failures.

Completed named case durations sum218.983 s against224.931 s JUnit suite time,
so accumulated test cost explains exhaustion. No heartbeat transport testcase
completed; it is next in the selected module order, but the anonymous interrupted
record cannot identify its exact case. Do not claim a hanging fixture.

All636 tested source files plus actual wrapper are copied and hash-verified in
relevant_v1_source/. Its manifest SHA256
27f8f468a0275deb84ddb6ea2b0d8d98263327e676c188dcd0b0c3a5cbd8c022.
No test, source or runtime change has followed this failed attempt yet. No CLI,
preparation or acquisition released. A separate finite source-validation
correction will retain valid completed cases, correct the two stale tests and
anonymous-JUnit classification, and account for every remaining planned case.
Experiment/runtime/science budgets and all gates remain unchanged.

## Corrected finite continuation release

The adopted correction is appended to the active comparison plan. Current
production is unchanged from focused620/relevant646; only2testtokens and the
append-only plan differ in the636source map. Exact test-only correction hold
legacy_selector_correction_v1/hold_receipt_v1.json SHA256
bea9030d3f8f90c2500ee6f52586810609c051f678d0bcd46e88389f1b3ec061.

External wrapper review additionally required empty/duplicate inventories to
retain a failed terminal receipt rather than exit before recording it, and
identity-invalid JUnit elements to remain unidentified. These changes preserve
raw XML and all planned pytest cases. Prior drafts/source are retained under
source_correction_before_review_v1/. Final wrapper SHA256
a3f9233debd8eb8dbc238ad4ac5c75f6d08bb0342f8098426e171d41f075d96c;
source_correction_hold_v1.json SHA256
9b14972111cb55c9388377535bda68e39d8937a1a0c440815cca2665ed5e2474.

Continuation_release_v1.json SHA256
7bd4a2b51f72819cd31477b3c4cfc4833a807247607974ee26901d6ba9c11e2f
binds reviewed636pins, exact7modules, source/test holds and fullclean198command.
Root65048 is running it once under240s (outer239+1 overentirebootstrap).
No fixturedeadline or runtime code changed, no passing fullbundle repeated.
Next only afterPASS: one30s collect-only inventory for27originalmodules,
exactunioncoverage receipt, thenoriginal60s actualCLIgate and composedsource
closure. Oldfailures/anonymousplaceholder remain retained outside passcounts.

## Continuation, exact coverage and installed CLI PASS

Continuation_v1: 194PASS, 131.52 s pytest/132.335975516 s wrapper,636 stable
source pins and21 stable installed bindings; zero unidentified elements.
Inventory_v1:1422 tests collected in1.63 s, wrapper2.362082663 s/30 s;
no test fixtures ran. Exact final coverage is620 focused+608 unaffected retained
passes+194 continuation passes,1422 unique IDs across27 modules. No missing,
extra or overlapping IDs. The two old failedV6 IDs and anonymous placeholder
are retained but never counted as passing evidence.

source_coverage_v1.json SHA256
72c36168917e31c889539dd6717b6bb93b32f65a7c47ec9e217cc86666de2e9d
binds each node to its receipt and verifies the exact two-test-token plus
append-only-plan difference from the earlier whole maps. Runtime/focused
inputs remained unchanged. This is composed source evidence, not one execution.

The original actual CLI gate passed: run_scenario and record_run --help,
3.166664562 s total helper runtime/60 s cap,636 source pins and21 installed
bindings stable, helper/environment stable, no graph or acquisition started.
actual_entrypoints_v1.json SHA256
65ae7a6249cc9550dc5e612ec5ca504fb0fd7d74816c5c67f0c3c040e8ba5372.

The composed source receipt and material archive remain pending. Source and
all helpers are held; no preparation or acquisition is released yet.

## Composed source closure

Composed source validation PASS, 2026-09-10 UTC: 1,422 unique tests across
27 modules, 636 current source pins and 21 installed bindings verified. The
single read-only composition took 0.709 seconds under 30 seconds. Receipt:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v7_clock_range_comparison_v1/source_validation_v1.json`,
SHA256 `397852cb02aaa14017238db6a21a82346f9f31a93dcc725912da5cba83eff164`.
The exact command, held helper, execution result and log are retained beside it
in `composition_release_v1.json`, `composition_execution_v1.json` and
`composition_v1.log`. Independent static review passed before execution.
This is the documented mixed-source-map union, not one test execution;
all failed attempts and their source copies remain unchanged. Current source
validation is closed PASS. Material source checkpoint/archive follows before
one preparation. No preparation or acquisition has run; both goals remain open.

## Source archive and preparation boundary

Material V7 source archive PASS: `checkpoints/m4_v7_clock_range_comparison_source_v1/manifest.json`
under the external V2 root, SHA256
`3ad6855d44397c485845e4d47bfa62e6b39867524d631a915df72221ae17b08c`;
398 repository files, 756 external references, 1,564,211-byte verified tar.
Context validation, diff check and checkpoint PASS. Actual composition receipt
and five preparation helpers independently match existing consumer contracts.
The single reviewed 600-second V7 preparation is now released; read its
exclusive receipt/log before recovery and never duplicate it. Source/helpers
held. Frozen audit and acquisition remain dependent on preparation PASS.

## Frozen preparation outcome

V7 preparation PASS in 52.617003256 seconds under600; independent frozen
audit PASS in4.324617603 seconds under30. Both processes terminal; no repeat.
Contract SHA256 `12865711f2f7e5cd1c7527dd84220333a44e5a8875489e09796caedf71dc7a7a`;
preparation receipt `2e5edc08e61522d55753ac188d45539fe23d2a9d347928a159ebac4f1824d3c6`;
frozen audit `a3197497a2411cf4a9fe812efb553ccaa1fadffe775f438e7d92aa6eb4024a76`.
Exact16 slots,192 direction targets, four topology receipts, V6 controller
selection, domain198,21 installed bindings and636 source hashes verified.
Prepared material archive and exact dispatch release follow; acquisition has
not started. All source and helpers remain held; both research goals open.

## Prepared archive and acquisition release

V7 prepared archive PASS: manifest SHA256
`40a47242060164da79e696cf24cce8c7f07cb71fbde0ce2a4ab3aec8e286b094`,
398 repository files,780 external references,1,565,700-byte verified tar.
Exact dispatch release PASS under60s (3.854682715s), SHA256
`12e2e58fd567d892f294374755cce86c0eff91fde042d00c6cbf584d9e068756`
at `pilot/m4_pilot_v7/preflight/dispatch_release.json` under the external V2 root.
The one dispatcher is starting from its exact saved argv,15300s inclusive,
domain198; initial slots1–4 only, holdouts through existing one-time gates.
All636 source pins and helpers are frozen. Never restart this version or
substitute old runs. Live status is not a terminal result; read acquisition
receipts and run console before recovery. Both scientific goals remain open.

## First development result and continued acquisition

V7 slot1 A terminal COMPLETE, integrity PASS, behavior FAIL;479.304932790s
case elapsed. Slot receipt SHA256
`905431f1e613193a82b6a0bb4f1d4def9df2e60052b18b02aa176d50cf04087e`.
The runner stopped at the unchanged360s Stage A limit without the required
local recovery sequence; its recorder and inner/outer cleanup completed.
This is one valid behavioral failure, not either original-goal result.
Slot2 B has passed recording preflight/motion readiness and is recording.
Same dispatcher root5888 remains live, source/helpers held;14later slots
unstarted and holdouts unreleased. No rerun or parameter change.

## Finalized slot1 receipt audit

Read-only review of the existing small receipts, without decoding the bag or
running analysis, confirms COMPLETE/integrityPASS and5/14 behavioral predicates.
All48 completeness checks pass; no warnings/failures. One confirmation, one
fill request, one Gaussian fill and17 AlgorithmEvents are already materialized.
The readiness-scoped outcome sequence includes confirmation, fill creation and
escape start. The terminal state is ESCAPE_ASSIST; there is no later SEARCH
boundary, no completed recovery episode, and Stage B never started.
The escape-command evaluator lacks its required later SEARCH boundary; its
zero sample fields must not be interpreted as independent evidence that no
assist commands occurred. The unchanged Stage A limit expires at360.026s
(simulation0.125 to360.151). Inner and outer processes did not time out; all
cleanup/kernel proofs and final zero pass. Outer exit1 is behavioral failure.

Full slot479.304932790s; inner recorder404.527s; graceful signal to inner
exit36.395s including shutdown/finalization, then8.306s to outer exit.
No separately measured validator duration is saved for this acquisition.
This shows selected completed finalization, not a controlled speedup benchmark.

Exact small-file hashes at the finalized run directory:
- completeness.json:4fb46d46db41be23e0a15f6544b443d880508126f9b31a304d111c511c399c14
- metadata.yaml:26abc1b6ea7959bdef6cfe0399f941b8d4dce416dd52353a9504cce6a92e9272
- scenario_result.yaml:a659706ff2a648b9e66e766eb40f21a880c630dea132be37859b26b76a13c5fd

Slot2 B continues under the same live dispatcher5888. A console-only quaternion
square-root RuntimeWarning is retained; its effect is not established without
terminal evidence. No source changes or unscheduled science are released.

Read-only warning trace: sensor_pose_node_script.py eagerly computes four
candidate quaternion magnitudes. NaN mag_q2 (and later mag_q1 warning) cannot
select its equality branch; other branches reconstruct quaternion components
from matrix entries rather than copying that candidate NaN. This warning alone
does not establish invalid output. The publisher has no final finite check;
moving-mode transform consumers reject nonfinite/nonnormalized input, while
stationary B does not select that moving consumer gate. B's centroid detector
separately admits finite algorithm-odometry XY. Earlier selected transport
fixtures retain this warning with finite/geometry assertions passing, which
is not certification of current samples. No runtime change, ROS inspection,
bag decoding or extra test was performed; current terminal evidence is pending.
