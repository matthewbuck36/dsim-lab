# M4 V9 combined budget correction and comparison validation

Status: SOURCE_VALIDATION_PASS / COMPARISON_CLOSED_INCOMPLETE, 2026-09-10 UTC.
The terminal comparison and closure section at the end supersedes earlier live
observations. Full V2 and both research performance goals remain IN_PROGRESS.
Read [adopted amendment](../m4_v9_budget_comparison_plan.md).
External build: /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v9_budget_comparison_v1/.
V8 remains CLOSED_INCOMPLETE and archived5544a2cf...02ed5; no original evidence
is resumed, replaced or reclassified. Both original research goals remain open.

## Pre-edit actual dispatcher baseline

The unchanged existing run_m4.py and existing frozen_dispatch fixture were
exercised once with the reviewed13-case test_m4_v9_budget.py, SHA256
3e4bf1597a1fc5e63d867cec3935c9dd67e5001ab4d5abd5a7fcdfd15d775cbd.
Root session57405 is terminal: expected exit1, 10PASS/3FAIL, no skipped or
unidentified cases. Pytest3.63s / wrapper4.264451156s / outer6.142417290s
under60. All642 sources and21 installed bindings match before/after.
Source command/helper independent static review and root fixture review PASS.
No ROS graph, acquisition, numerical owner or retained bag ran.

The three exact failed identities are:
- test_exact_fit_all_sixteen_is_independent_of_retained_monotonic_origin[retained_v8_origin]:
  actual first-slot admission produces the same envelope TimeoutError.
- test_next_representable_block_admission_boundary_is_strict[after-after_development]:
  old admission incorrectly permits the one-ULP excess.
- test_next_representable_block_admission_boundary_is_strict[after-after_nominal_holdout]:
  old admission incorrectly permits the one-ULP excess.

The full16 schedules at100 and the recordedV7 origin pass, as do the221s
science-overrun rejection and all other declared representable boundaries.
These are retained expected baseline failures, not a passing corrected result.
Exact clean domain201 command is baseline_release_v1.json, SHA256
 d7693da2397c30e0f8fe2ab3a4ec7401367f0d80376de0b4fd0580df799d68f7;
source receipt baseline_v1_receipt.json SHA256
4a3f652d059c5cbfdfe5af7317908a7994cb400cac9a6ecfa54e4db54711ed1f.
Raw console and JUnit are retained beside it. Outer59+1s encloses clean
Humble/Q2/Q5 setup and wrapper; inner45+10s bounds pytest. The baseline is
not included in final corrected-source pass totals.

Pre-edit V1-V8 capture precedes the one combined production edit. Source tests,
CLI, source closure, preparation/frozen audit/archives and dispatch are pending.

## Pre-edit legacy capture and correction

One pure capture PASS: all8 prior versions/128 schema-expanded launch/metadata
rows with exact YAML order;642 source pins unchanged. Root session55731 terminal0,
5.178039795s helper/5.574152867s outer under30. The helper forbids models,
ROS initialization and acquisitions; no topology was rederived. Receipt
version_routes/capture_preedit_v1_receipt.json SHA256
 a7776dda9a0d6abbefcb8886fabb4be8c676449d3ad259d3c82618857bbca11a.
Independent static capture/hold review PASS; preserved originals cover all four
production owners, eight affected old fixture modules and the prior641 map.

After the expected baseline/capture were accepted, the existing dispatcher
admission predicate was changed to compare case_start-started against the
exact remaining allowance15300-((16-index)*900+remaining_science). All other
absolute deadline/science/cleanup/source/holdout predicates are unchanged.
FreshV9 selection routes and compatibility fixtures are in progress in the same
source milestone. No final corrected-source tests, preparation or acquisition
yet; source results follow only after held-source review.

## Held source and execution admission

Exactly16 source differences from closedV8: four production owners, eight
existing future-negative fixture modules, three new test modules and adopted
plan. Source hold009ae8df4973860972db15a962f9b4e63a757b7d5a681ef9d60a89d43def5cb8
binds645 files, with changed-source copies under held_source_v1/. The two JSONs,
V6 controller/profile/template helper, stationary causality validator, numerical
model, detector/direction implementations and cleanup owner remain unchanged.
Budgetguard SHA144ad4512c4266c6d266f854bcfe1e6a754b8b42142e6beb8df7d5973e337d83;
scenarioa79d6c21c7cd8ef0b042cfb0984ae4cbd68002db00dac0e28240f232a1e623ce;
runner0bf6914cb7d286e16a0b97d804cc2cb2487febadca25962abf7d4f6f4d061272;
workflow5716f5f08ec18f8c0d410e7cc72b71f3b303ab7e491c34b508ae3bdf1ee580f8.
Independent root/peer static reviews PASS for all scopes. Three new fixture
populations are prospectively13 budget/81 versions/150 workflow; actual collected
counts and results must come from retained JUnit, not these predictions.

Root session27106 runs focused_v1 once under180s (outer179+1/inner165+10),
with exact eleven-module command in source_commands_draft_v1.json and
focused_release_v1.json. Source/helpers are held until terminal receipts.
Relevant seven-module240s and actualCLI60s are still pending and conditional
on the focused result. No current Gazebo E2E/build/model/retained-bag job is
admitted by these source tests.

Prospective preparation helper set was reviewed independently and by root:
preparation_helpers_hold_v1.json SHA256
fdec8c09c7f43a7d3a083cb3b1a28dd073ba03130aa65e8fcd754db1aa347d5a.
The unchanged600/30/30/60/60 bounds, clean domain201, exact645-source guards,
V8 closure/source/prepared chain and V7clock/V8stationary references are held.
Source archive and all dependent execution remain unreleased at this point.

V9 focused_v1 terminalPASS1136 unique cases,645sources/21bindingsstable,
0fail/skip/unidentified:137.49s pytest/138.224169301s wrapper/140.132669052s
outer under180. Root session22506 now owns one relevant240 plus conditional
CLI60 after same-source/relevantPASS admission. Source/helpers held; read
exclusive currentbuild receipts before recovery. No preparation/acquisition.


## Final current-source validation

V9 combined source milestone CLOSED_SOURCE_VALIDATION_PASS:1333 unique
current-source cases across18 modules;645 identical source pins/21installed
bindings. Focused1136 PASS140.132669052s/180; relevant197 PASS19.113068034s/240;
actualCLI PASS3.576528164s/60. No failed/skipped/unidentified current cases.
Aggregate e65ef0e6e0a7c3751213d3a4e6b21e4fa6cf4a7bd02982695b175bfd1c93c98a;
CLI d5cafb6f0f33d2e061b788ded1e3d2a1092b0bf8c92e6c7b85c0a941a15e601e.
The preserved pre-correction baseline10PASS/3FAIL is excluded from these totals.
All source jobs terminal. Material source archive then one600s preparation is
next; source/helpers held and no acquisition released. Both goals remain open.

Relevant pytest16.41s/wrapper17.201818225s; CLI helper3.164512164s.
The one30s composer passed0.347552920s helper/0.400147990s outer, comparing
raw named JUnit with both receipts, disjoint module sets, unique identifiers,
exact source delta/holds/capture and all CLI bindings. It does not rerun tests.
Source commands, exact releases, outer execution logs/receipts and raw JUnit
remain external. HistoricalV8 source1232 and old325/1422 proof counts are not
added to the new1333. No Gazebo E2E, rebuild, bag replay or numerical model was
run in this source milestone. Preparation performs its own bounded topology
work only after archive closure.

This repairs admission arithmetic and adds freshV9 selection. It does not prove
faster detection, direction accuracy/availability, zero mandatory stops in
acquisition, or combined fill/escape behavior. Those retain the original M4
comparison gates. The firstV8 attempt remains all16UNSTARTED; its source and
all35pilotfiles/192unavailable targets remain preserved.

Material source archivePASS6b111c76dccff165ad45038f35839730cb9684a6be203cfa7b3af98ecbdee980:
checkpoints/m4_v9_budget_comparison_source_v1/manifest.json under externalV2,
417repository files/160externalrefs/1636987-byte verified tar;0.763491120s/60.
Context/diff/checkpoint PASS. This live receipt postdates the immutable archive.

V9 preparation/frozen audit terminalPASS, rootsession13378.
Preparation53.059032202s helper/53.332698139s outer under600, receipt
713231a26404182f49ded8f52e56cdd2fe5a653ef2a64bb5c9a8b31357a1a896.
Frozen audit4.323064959s helper/4.753220887s outer under30, receipt
 eeff4ed7001368aee97b7134ad25fcbc6dfc50857f441b62b9aeb33757f94bba.
Contract623b6ffa1b8795582138d7d39374ae04f52788beb7c211278ab58a9ee3a0a022.
All16 identities/controls/argv/topology and645sources/21bindings match the
frozen contract; actual fourtopology derivations belong to this sole preparation.
Do not repeat preparation or derive fields for context. Prepared checkpoint/
archive and exactdispatch release next; source/helpers held, no acquisition.


V9 prepared archivePASS e07eaa2f3839d081f44e3c1fb42b7e866d0ef6d01c849df2ca960d5604dedbc2:
417repo files/181externalrefs/1638561-byte verified tar,1.115259849s/60.
Context/diff/checkpoint PASS. Exactdispatch releasePASS3.760565226s/30,
SHA43dce36fc62feafd676782c170e7544e0ecf42c02aa14892b1707fd1eca6fd60.
It binds contract623b6ffa...a0a022, source/CLI/preparation/audit andbotharchives,
fixedV6controls/645pins/21bindings/domain201, initial4developmentslots and
one15300s inclusive dispatcher. Holdouts need existing one-time science/release.
Root actualrelease/hashreviewPASS,254GiBfree andnooverlapping Gazebo/pytest/
dispatcher/scenario/recorder process. Independent actualrelease review thenone
attempt next. Source/helpers held; no source edits or newmethod changes.


V9 acquisition LIVE: sole dispatcher root session77764, ownerPID105626,
timeoutPID105630, launched2026-09-10T13:41:14.151187+00:00.
Owner receipt29eadbe12b6416060dd82a02fc51953760965855d2a98a22d3deb31c5b615521,
release43dce36fc62feafd676782c170e7544e0ecf42c02aa14892b1707fd1eca6fd60,
contract623b6ffa1b8795582138d7d39374ae04f52788beb7c211278ab58a9ee3a0a022.
Independent actualrelease reviewPASS. All645 sourcepins/helpers frozen. Read
builds/m4_v9_budget_comparison_v1/acquisition_execution_v1.json and current
pilot/m4_pilot_v9/acquisition receipts before recovery; never restart or launch
a second dispatcher. Initialfour development slots precede one-timeholdout gates.
No edits/tests/otherROSgraph/Pi actions. Both research goals remain unproven.


## Selected live slot1 binding observation

During slot1 recording, independent read-only inspection of metadata.yaml,
resolved_parameters.yaml and resolved_topics.yaml found exact contract target_argv,
A/slot01/26090801 identity and22 captured scenario-runner fields matching their
frozen counterparts. Actual launch is turtlebot3_rotating_sensor/gazebo.launch.xml,
GUITrue; selected V6 controller JSON hash e94ea14a...0606 agrees with contract.
Its gains.5/5 and ceilings.1/.5 are established by selected file/argv/unchanged
loader, not exposed runtime ROSparameter values. Captured controller/filter and
algorithm use_sim_time areTrue; detector/fill/supervisor pde_mean_v1/stationary_v1,
heartbeatFalse, pose/odom, interiorfallbackTrue/min.5 and launchrecenterFalse.
Resolved topics identify Gazebo /clock and turtlebot3_diff_drive /odom publishers
and recorder subscriptions. Required controllers/readiness pass. At observation,
metadata remains recording/operational/failure_stagenull; completeFalse and
completenessFalse are live placeholders. These are startup-binding observations,
not a final integrity or behavioral result. No bag read, ROSquery, test, model
execution or source change was used by the audit.

## Development slot1 completed; comparison continues

V9 slot1A COMPLETE, recordingintegrityPASS48/48, behavioralFAIL4/14.
No confirmed detection/fill/escape beforeStageA360.026simsec; terminalSEARCH.
Finalzero,target/bag cleanexit and allthreeperformedcleanup checksPASS.
Case478.561413568s/900; no work/absolute deadline exhaustion. This is a complete
behavioral failure, not detector/combined research qualification. Slot2B is
recording afterpreflight+motionreadinessPASS2026-09-10T13:50:29.195711Z.
Same sole dispatcher77764 remainslive; all645sources/configuration held.
No developmentscience orholdout release yet; neverrestart/replace anyslot.

Independent descriptive audit used finalized receipts only, no additional bag
or model work. The summary's sole selected row and slot runner_result agree
with scenario_result. Fourteen required behavior predicates: recording, cleanup,
no forbidden state and no forbidden event PASS; other10 FAIL. Observed state
sequence onlySEARCH; eight canonical AlgorithmEvents, event-name set only
CONVERGENCE_CANDIDATE; confirmation/ESCAPE_STARTED/FILL_CREATED counts0,
fill requests/fills0 and1330legacy convergence status messages. No recovery
episode or StageB start. StageA spans.532 to360.558s; ranked/controller/groundtruth
goalFalse and finalglobaldistance3.271997m. Innerreturn0, outerreturn1 reflects
behavioral failure. Both process owners' eight kernel proof flags and performed
inner/outer/independent-inner cleanup PASS, empty errors/survivors. Retained
one-enumeration race and adopted descendant PID106002 wait_status9 mean this
must not be described as entirely natural exit or diagnostic-free. Completeness
has failures[]/warnings[]. Case retains421.438586432s of its900s envelope.

Immutable selected references:

| Evidence | SHA256 |
| --- | --- |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9/acquisition/slot_1.json` | `08996b159e755699d69b22c6dc98f334d705a5e497d9964a373aa0299bd69ab4` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9/acquisition/summary_1.yaml` | `a649e07be5ce0ee13c23360acf044bf69c5f8add0e32b7d65a5d89eff691d103` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9/runs/2026-09-10/m4-pilot-v9-slot01-A-26090801/metadata.yaml` | `932d4231292b6f4bbf10c4aabdbbd0395307e3f73dd0f70f2ddbf3cbf486373b` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9/runs/2026-09-10/m4-pilot-v9-slot01-A-26090801/completeness.json` | `47fbf4a316e954108e832da541030563c36ce9e09e4d771e9510f414acee0461` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9/runs/2026-09-10/m4-pilot-v9-slot01-A-26090801/scenario_result.yaml` | `9c0bc7b5dbc40d07d229f660b169b16109e0134aa7d96d15761018572303ae67` |

## Selected live slot2 binding observation

Independent read-only metadata/parameter/topic inspection at parameter snapshot
2026-09-10T13:50:27.592193Z matches exact slot2B/26090801 identity, frozenargv
and recorded scenariofields. Actual detector centroid_two_block_v2 W6/.18/.5,
invalidheartbeatTrue andstationary_v1; detector/fill/supervisor/controller/filter
use_sim_timeTrue. Fill+supervisor select /gesc_gaussian/v2/stationary_fill_requests,
whose required alias permits zero messages before a request; its solepublisher
is supervisor and recorder is subscribed. Q5 context includes source/odom,
timekeeper/turtlebot3/timekeeper_chatter anddesign5s. Centroiddiagnostics sole
publisher is detector, sourcegap.5/diagnosticgap1 and recorder subscribed.
The existing StationaryCentroidAdapter and Q5 installed owners remain selected.
V6 JSON/control/refhash matches; recenterFalse/interiorTrue/min.5, required
controllers andpre/post readinessPASS. This observed recording/operational state
is not a final completeness or research result. No bags/ROSqueries/tests/models
or source writes were used for this observation.

Read-only closeout-requirement review confirms adopted execution/V9 amendments
andledgerA01-A05/V01-V04/F01 control reporting. No V2 PDF/LaTeX/filename mandate
is present; V1 navigation requirements are V1-specific. Retain16outcomes,
6holdoutlatencypairs/12endpoints,192directiontargets/144holdouts, exactavailability
and error/censoring denominators, stationary-stop andcombinedsequence checks,
goaltime/path/jitter/lag/fallback/failures, finalacceptanceaudit andhandoff,
Git/status/navigation/checkpoint/archive. A negativecompletefixedpilot canclose
its experiment/report boundary, but failedresearchgates keepfullV2/usergoalopen.

## Development slot2 completed; moving arms continue

Slot2B is COMPLETE/integrityTrue/behaviorFalse, with matching slot/summary/scenario
results. All52 recordingchecks PASS, including stationaryauthority, centroid
consistency, causality andcoverage; failures[]/warnings[]. Finalmetadata is
complete, finalzeroTrue,target/bag cleanexit0 andcleanup_errors[]. Allthree
performedcleanup checks and inner/outer eightkernel flags PASS, with no wall
orabsolute deadline exhaustion. Case485.905062685s/900,414.094937315sremaining.
Retain inneroneenumerationrace andadopteddescendant107726 wait_status9; this is
not evidence that every process exitednaturally.

Behavior4/14PASS: recording,cleanup,no-forbidden-state,no-forbidden-event.
Other10FAIL. State sequenceonlySEARCH, StageA360.026simsec(.518→360.544),
no StageB/recovery. Finalglobaldistance3.390151916m. There are10711centroid
diagnostics and7canonicalevents; observed event-name set onlyCONFIGURATION.
Confirmations,fillrequests,fills,snapshots,typedcommands/results areallzero.
Stationaryaudit has6zerocounts andempty confirmation/request/outcome/timeline
lists. These savedreceipts do not provide centroidscore,candidate orvalid-versus-
heartbeat breakdown; zero confirmations alone does not diagnose the cause.
No additionalbag decode/model/science job was run for this descriptiveaudit.
Both originalgoals remainunproven. Slot3C passedpreflight/motionreadiness and
isrecording under the same sole dispatcher77764 and645frozenpins.

| Evidence | SHA256 |
| --- | --- |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9/acquisition/slot_2.json` | `cf1e7fd1e3b2b6904df8d44c6ea68f3ab76ae076608ad00c05bd37d5a97ee6a6` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9/acquisition/summary_2.yaml` | `996bc57e17b0242a1c1367c6c42c4f216d1f309904e8e42df873f3b14787aa7a` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9/runs/2026-09-10/m4-pilot-v9-slot02-B-26090801/metadata.yaml` | `ed35543cc9e77149b898d6640721141f4a243b572774c93bc26a79beacd79c0b` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9/runs/2026-09-10/m4-pilot-v9-slot02-B-26090801/completeness.json` | `02d4693160f9a127b03b28df5a6dc57e6575b695a9da4700312f18553edc4088` |
| `/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v9/runs/2026-09-10/m4-pilot-v9-slot02-B-26090801/scenario_result.yaml` | `b160c82587eb7e47a69e27e96fb3c6c6abac2ba3b623a7036cb87313a48a8a09` |

## Selected live slot3 binding observation

Independent read-only inspection at parameter snapshot13:58:31.609512Z matches
slot03C/26090801/primarynominal identity and exact frozen targetargv; extra
metadata direction_policy/v2_identity fields are expected moving-mode enrichments.
Selected rolling_gesc_v2 andmoving_cycle_coherence_v1 use meanweight.75,
3coveredcycles/12sectors/coherencethreshold.25. Separate movingcandidate guards
areradius.75m/epsilon.15m. Legacydetectorpde_mean_v1 andheartbeatFalse remain.
FiveROSparameterowners (detector/fill/supervisor/modifiedcost/PDE) share exact
run/stream binding: model_input_time/channel0/odom/encoder/timekeeper/raw/source/
provenance/objective/geometry. The.18m transform hash8fcfb1e2...99b5 matches.
Required typedtopic aliases and solepublisher/recordersubscription bindings match:
direction/policy fromfilter, epoch/candidate/commands fromsupervisor, confirmation
fromdetector, history fromPDE, results fromfill, provenance fromcost, objective
frommodifiedcost, odom fromdiffdrive andclock fromGazebo. Existing source selects
MovingSupervisor andcontroller/filterCLI mode/policy throughQ5bound launch.
AlgorithmclocksTrue andrecorderFalse are intentional distinct clock domains.
Selectedcontroller e94ea...0606/filterf1cfd...a2dce sourcepins match; readinessPASS.
Recording is operational withfinalcompletenesspending. This establishes selected
alignment configuration, not actual time-series alignment or scientificquality.
No bagread/ROSquery/test/model/sourcewrite was used by the audit.

## Development slot 3 completed; combined arm continues

Slot 3C is COMPLETE, integrity=True, behavior=False. Slot, summary and scenario
results agree. All 60 completeness checks pass; failures and warnings are empty.
Four PDE confirmations at 70.9, 150.8, 230.1 and 309.8 simulation seconds produce
four SEARCH -> VERIFY -> SEARCH sequences. The moving audit records five valid
epochs, 7,214 epoch heartbeats, 3,111 typed PDE histories and zero lifecycle errors.
Candidate snapshots, commands, preparations, commits, results and fills are zero.
No DESIGN, ESCAPE or recovery episode occurs. The canonical event topic contains
23 messages; the scoped outcome list contains 17 (four candidates, four
confirmations, eight state transitions and one configuration). Each direction
diagnostic topic contains 17,819 messages; counts do not establish direction
availability or accuracy.

Four of 14 behavioral predicates pass: recording, cleanup and absence of forbidden
states/events. Ten goal, terminal/path/event, recovery, escape, proximity and fill
predicates fail. Stage A expires after 360.026 simulation seconds, from 0.132 to
360.158; Stage B never starts. Final global distance is 3.495354376 m.
Final zero and clean target/bag exits are recorded. Both eight-flag kernel proofs
and all three performed cleanup checks pass. The case takes 494.555977638/900 s,
leaving 405.444022362 s; no wall deadline expires. Inner exit is 0 and outer exit
is 1 for behavior. The inner receipt retains one enumeration race and adopted
descendant PID 109469 with wait_status=9; this is not an all-natural-exit claim.

Evidence below is relative to external `pilot/m4_pilot_v9/`; run files are under
`runs/2026-09-10/m4-pilot-v9-slot03-C-26090801/`:

| Receipt | SHA-256 |
| --- | --- |
| acquisition/slot_3.json | 0b3609908cfcf0f8a8c99aa5a4ad852aa4edad7ca7e7f05a01a9b502f834ddbf |
| acquisition/summary_3.yaml | 958dbba65f8be4274f2b2f916ae8d31b07b4d0b22ba7b53798d8b205b54c02bc |
| metadata.yaml | 8ad492a0b4cf786e3fb18f545104533a78edd92bfa6d26ba7952ce138ce65f75 |
| completeness.json | 588b0f5db8bfb6438c4d1eae8a40372942d4201892744071eee06b4bb2faf3da |
| scenario_result.yaml | 63b35eafe80b29e004f7c676b99b0c4476e01d69fc2015cc48ad6aa60e529123 |

This is a descriptive receipt audit, not additional bag analysis or scientific
qualification. Both research goals remain open.

## Selected live slot 4 binding observation

Independent read-only inspection at parameter snapshot 14:06:45.525187Z matches
slot 04D/26090801/primary nominal and exact frozen argv/shared scenario fields.
Detector/fill/supervisor select two-block W6/.18/.5 and rolling_gesc_v2; detector
heartbeat is enabled. Moving policy mean weight is .75. Separate moving candidate
guards retain radius .75 m, epsilon .15 m and VERIFY 12 s, with qualification
False, interior fallback True/minimum .5, and RECENTER False.
Five parameter owners share the exact D run/stream identity and typed topics.
Required centroid diagnostics come from the detector and are recorded; heartbeat
is True and diagnostic coverage gap is 1 s. Moving epoch/candidates/FillCommand
come from supervisor; FillResult from fill; direction/policy from filter; objective
and provenance retain their existing owners. StationaryFillRequest is unselected
(not required, no publisher), consistent with the Q5-bound MovingSupervisor route.
Algorithm clocks are True; recorder/coordinator clocks are False. Controller
e94ea...0606, filter f1cfd...a2dce and geometry 8fcfb...99b5 match frozen pins.
Readiness passes with no errors. This checks configuration and topic bindings;
actual transaction payloads, time-series alignment and performance are unevaluated.
No bags, ROS queries, tests, models or source writes were used by the audit.

Recovery checks: context validator `timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`
passes. Branch/HEAD remain feature/gesc-gaussian-robustness-v2 / 3369cfc83a64ff5d8354827fd5310caaf0c8e945;
task source remains uncommitted. Read-only SHA-256 verification matches all 645
held source files. Session 77764 and original owner/timeout PIDs remain live;
terminal acquisition receipts are absent. No acquisition was restarted.

## Development block completed; planned analysis live

Slot 4D is COMPLETE/integrity PASS with 61/61 completeness checks and behavior
FAIL (7/14). Six confirmations, one fill and one escape are recorded, with no
FAILSAFE. Local fill -> escape -> SEARCH is observed, but the final recorded
state sequence ends at VERIFY. This is partial combined behavior, not a full
goal or holdout success. Case duration is 502.001615714/900 s. All eight kernel
flags pass in both owners, using the selected mode3 strategy; runner, outer and
independent inner cleanup checks are performed and PASS without errors.

External `pilot/m4_pilot_v9/acquisition/slot_4.json` SHA-256:
f8191fd8ee58c0f961bf511c42f952075075ef09be757803b73d36236cdca78c.
Run `runs/2026-09-10/m4-pilot-v9-slot04-D-26090801/completeness.json` SHA-256:
36729bf559e24450612eb930309435a520fba1079c19feef2dffbd851244c8e7.
Detailed finalized receipt audit follows separately; no new bag analysis was
performed by this observer.

The sole dispatcher has started planned development science. Its retained
`analysis/block_0/started.json` SHA-256 is
32c4eea7d1b6db09620fc7b7b9e3b04ee39c011949a3e5522ea572a8d3ca34b0,
with original monotonic interval 64688.846663993 -> 64908.846663993 (220 s).
No finalized science/block, holdout release or terminal acquisition receipt
exists at this observation. Source and controls remain frozen. All four complete
behavioral failures are preserved; neither research goal is yet demonstrated.

## Development science unavailable; original holdout gate released

The labels job reaches its saved work deadline and is terminated cleanly:
timed_out=True, return_code=-15, elapsed_wall_sec=113.39911132599809.
Its 120-second enclosing stage reserves setup and cleanup; the actual child cap
is 115.7966251359976 s, not an extended 120-second child allowance. All eight
kernel proofs pass with no remaining owned processes. Block elapsed time is
118.64892826900177 s under the original 220-second deadline. No retry occurred.
The complete attempted-science ledger marks all four runs EVIDENCE_UNAVAILABLE
with reason labels_analysis_timeout. Direction references and summary are skipped
for no_complete_frozen_label_inputs. Partial labels/metrics/normalized outputs
remain retained, without promotion to a completed scientific result. Unknown
wrong fills/goals, mandatory stops and combined qualification remain null.

Retained paths under external `pilot/m4_pilot_v9/` and SHA-256:

| Receipt | SHA-256 |
| --- | --- |
| analysis/block_0/block_receipt.json | bcfacffe508b75bedd3fd51a4ad3ad4d1072b467c51c996698b5f3f6243cb67f |
| analysis/block_0/labels_job.json | c6c4bd631836349c2292b0a531fe124ace919d632993a81f425272a6d1a3a13e |
| analysis/block_0/unavailable_result.json | 35165efda6c1492f7d1b7021dc2c28c4c621f538e30fff93cd819bf00b609dff |
| preflight/holdout_release.json | 4d877ad7f72c632d7df93a88302cb1d36dd3f2576f091dbed3032fde522d0bf6 |

The existing gate releases the 12 frozen holdouts once, binding contract623b6ffa...
and all four exact complete development receipts plus the attempted-science
ledger. Release elapsed is 4.065685724999639 s. scientific_pass_required=False,
tuning_performed=False and replacements_allowed=False match the adopted plan.
This is release authority to continue the fixed comparison, not scientific PASS.
The same root session 77764 remains live; no source/control change is made.

D monitoring caveat from the finalized receipt: staged_monitor_error is
`M4 centroid convergence timestamp binding: centroid convergence event lacks matching typed confirmation`.
stage_a_observed_live=False and graceful_stage_a_timeout_stop=True are retained.
Final bag-derived outcome binding error is None with six matched bindings;
local_recovery_stage=True and one direct-repulse episode are recorded. The
receipt has Stage B start142.411/latest364.465, but Stage A timeout .529 ->364.533
(364.004 s), terminal VERIFY. Do not claim a full 300-second post-recovery
observation or infer a cause without separately authorized bounded diagnosis.

## Final D descriptive audit details

The independent finalized receipt audit agrees across slot/summary/scenario.
Six confirmations publish at 68.5, 122.6, 220.5, 268.6, 316.7 and 364.8 s.
One valid transaction binds candidate2/revision1/epoch2, source122.531 s,
accepted122.6, snapshot/PREPARE122.7, original ACTIVATE command sequence2 and
fill1/generation1 commit123.3. Objective and direction acknowledgements first
appear123.4. Evidence is informative with three pretrigger and zero verification
revolutions. One snapshot, three command messages and three result messages yield
one preparation, one prepared transaction, one unique commit and zero lifecycle
errors. The separate inherited spatial recovery association picks the earlier
68.461 s confirmation; it is not transaction authority.

One SEARCH -> VERIFY -> DESIGN -> ESCAPE_REPULSE -> SEARCH recovery completes.
Outside-radius anchor1.367887 m and exit1.474702 m exceed frozenradius1.366771 m.
Returned SEARCH has 1,564 zero-supervisor-command samples and restored ordinary
GESC ownership; ASSIST is not required. Seven behavioral passes cover recording,
cleanup, no forbidden states/events, local recovery, escape ownership and fill
cardinality. Controller/ground-truth goal, terminal state, full required state
path/events/event sequence and qualified post-recovery proximity fail. Final
global distance .252151 m and first proximity .498352 m do not substitute for
the missing ranked GOAL_REACHED event. Final state remains VERIFY.

The live monitor binds five confirmations; final recorded-data evaluation binds
six. Stage B spans142.411–364.465, with the retained Stage A stop described above.
Twenty-nine canonical events differ from the 23 scoped outcome events (six
confirmations,13 transitions,two configurations,one fill,one escape). There are
9,053 centroid diagnostics and18,040 messages on each direction diagnostic
topic; these counts do not qualify performance. Final zero/clean target and bag
exits pass. Inner cleanup records descendantPID111074/wait_status9 and no
enumeration race. No process deadline expires.

Additional hashes, under the same external pilot and D run directory:

| Receipt | SHA-256 |
| --- | --- |
| acquisition/summary_4.yaml | 526434c225424bde3119a84803d7dae921abe7d92d2768a80794c0f516795f13 |
| metadata.yaml | f5e8b63c7699545b397847b37fcbab54349fbfe9e0580b1a70f772080b8bf2cf |
| scenario_result.yaml | 9fa43d3b23bdec22404588f66a5940e1101086c293889d31ffa62f8175174463 |

Observer scope remains finalized small receipts only: no new bag read, model,
test, source change or runtime intervention.

Independent block0/release review PASS: exact release/contract/four development
receipts/block/unavailable references and embedded labels-job equality verified.
All645 release pins equal contract/final source validation. The log ends with
KeyboardInterrupt in bag_reader.read_run_bag, consistent with recorded cancellation;
no new bag read was performed. Slots5–16 are exact, with no tuning/replacements.
The contract retains192 targets; the block's direction rows are empty and final
192-row output remains pending. Scientific unavailability is not an integrity pass
for the missing scientific measurements.

## First nominal holdout binding observation

Slot5A is recording after readiness PASS at2026-09-10T14:17:14.626100Z. Independent
read-only metadata/resolved-parameter review matches releasedslot5 and exact
frozen launch argv: secondary geometry, local(.5740251485476348,1.38581929876693),
global(3.5,3.5), start(0,0,0), seed26090802, nominal/no injected noise or delay,
headless/no--gui, domain201. PDE/stationary selectors and heartbeatFalse remain.
Algorithm clocks are True; recorder/coordinator False. Same V6 controller JSON
e94ea...0606 selects .5/5 gains and .1/.5 speed limits. All corresponding scenario
fields match; descriptive metadata omissions are expected. No parameter-capture
failure or readiness error. Final resolved_scenario.yaml and slot receipt are
pending; completenessFalse is a live placeholder, not terminal failure.

The [live result draft](m4_pilot_v9_result.md) retains all16 reserved rows and
explicit pending/unavailable denominators. [Development diagnostic notes](m4_v9_development_diagnostics.md)
record a static monitor progression defect and unresolved analysis cost, solely
for separately scoped work after V9 closes. Source/control/evidence remain frozen.

Development evidence boundary: `timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh v2`
PASS in .255512443 s, writing the existing checkpoint.txt; git diff --check PASS.
Direct write_stdin polling of the same session77764 at14:23:37.906422Z confirms
it remains live and slot5 has no final receipt. This checkpoint does not close the
comparison or replace the prepared material archive; final closure is pending.

## Nominal holdout slot 5 completed

Slot5A COMPLETE/integrity=True/behavior=False. Single summary row, slot runner
result and scenario result agree exactly; metadata targetargv matches launchargv.
All48 completeness checks pass, failures/warnings empty. One confirmation,
one legacy fill request, one fill and one assisted recovery are recorded:
SEARCH -> VERIFY -> DESIGN -> ESCAPE_REPULSE -> ESCAPE_ASSIST -> SEARCH.
ESCAPE_STALLED precedes assistance. Assist-entry handoff7.065 ms and return-to-
SEARCH handoff3.839 ms meet the150 ms bound; ordinary GESC ownership restores.

Seven of14 behavioral predicates pass: recording, cleanup, no forbidden states/
events, local recovery, escape ownership and fill cardinality. Goal, terminal
state, full required state path/events/event sequence and qualified post-recovery
proximity fail. Final state SEARCH, globaldistance .101494 m. Proximity .499508 m
is recorded but lacks a preceding valid ranked GOAL_REACHED. Stage A completes
without timeout; Stage B222.529 ->522.545 expires after300.016 simulationseconds.
Live Stage A stays valid and staged_monitor_error=None. This is full post-recovery
exposure within the selected stage budget, distinct from development D's caveat.

Eighteen canonical event messages differ from11 scoped outcomes: five transitions
and one each candidate, confirmation, configuration, fill creation, escape start
and escape stall. Legacy convergence-status count342. Final-zero and clean target/
bag exits pass; all eight inner/outer ownership flags and three performed cleanup
checks pass. Inner exit0, outer1 for behavior; neither process deadline expires.
Case658.991909884/900 s. One outer enumeration race remains recorded; there are
no adopted-descendant reaping entries. No new bag/model/runtime analysis is used
by this descriptive receipt audit.

Paths under external `pilot/m4_pilot_v9/`; run files under
`runs/2026-09-10/m4-pilot-v9-slot05-A-26090802/`:

| Receipt | SHA-256 |
| --- | --- |
| acquisition/slot_5.json | dd8917ec43ebed027a1320d420aa72e408b2f344d3ddfb889402efd2d5d9db93 |
| acquisition/summary_5.yaml | 8c169abfaed0ebfa7f73c78586b1a321798c2ce43cd5b430a67c21551178d025 |
| metadata.yaml | 71c3726095f5c9a660184cfadf9a9fc0312071595b3be354e08bb49d88150cac |
| completeness.json | bef890773d0e70ed9e47fb2d7b4af2025bcb3463fd384ebbd0bfa47d29931410 |
| scenario_result.yaml | 230a27ae8ceb9e977418a9ae1194cf08a5e02253876ce30eb1cdc29844f3d125 |

Slot6B recording/readiness PASS14:28:12.765412Z; dispatcher77764 remains live on
direct polling14:29:12.228285Z. All source/settings remain frozen. The independent
review of live report snapshot SHA0bf6eecbb0c52327ab21e2fd083e0a5eae868954ac307c2ca7a2adbc61fadadb
passes its five receipt references, development counts, caveats and denominators.
That review predates the above slot5 update and is not final report acceptance.

## Selected live slot 6 binding observation

Independent read-only audit matches exactslot06B/holdout nominal/secondary/
seed26090802/headless, actual launchargv and all shared scenario metadata fields.
Detector selects centroid_two_block_v2 W6/.18/.5, heartbeatTrue andstationary_v1.
Supervisor and fill select the canonical stationary typed request route; the
manifest records its one supervisor publisher and recorder subscription with
matching centroid parameters. SameV6 JSON e94ea14a...0606/gains.5/5/limits.1/.5
is selected. Algorithm/controller/filter clocksTrue, recording coordinatorFalse.
Console/recorded robot configuration bind the Q5 installed Gazebo/resources route.
Preflight/barriers/readiness PASS14:28:12.765412Z; parameter capture failures empty.
Metadata is still recording withcomplete=False as a live placeholder. Final
completeness, payload transactions and behavior remain pending. No ROS commands,
bag reads, tests, models or writes were used by this observer.

## Nominal holdout slot 6 completed

Slot6B COMPLETE/integrity=True/behavior=False. Slot/sole summary/scenario results
and metadata/recorded launchargv agree exactly. All52 completeness checks PASS,
failures/warnings empty. Four centroid confirmations publish at182.3,299.7,345.0
and390.3 s. One stationary typed request191.5 s produces activefill1/creation
event191.6 s, with no retries, terminal failures or unresolved requests.

One SEARCH -> VERIFY -> DESIGN -> REPULSE -> ASSIST -> SEARCH recovery completes;
later verification visits endVERIFY. Entry/exit handoffs3.466/8.550 ms pass and
ordinary GESC ownership restores. Seven of14 behavioral predicates pass:
recording, cleanup, no forbidden states/events, recovery, escape ownership and
fill cardinality. Goal/path/event/terminal/proximity requirements fail. Final
globaldistance .160397 m; proximity .499173 m lacks valid ranked GOAL_REACHED.

The live monitor repeats development D's missing-companion error. It clears live
Stage A/cardinality despite previous Stage B209.616 ->389.952 s. The retained
stop is Stage A timeout390.054−.108=389.946 s; final evaluation binds all four
confirmations successfully. Do not claim a full300-second Stage B observation.
Counts:10,553 centroid diagnostics,25 canonical events,one typed request,onefill.
The19 scoped outcome events comprise four confirmations,ten transitions,two
configurations,fill creation,escape start andescape stall. Counts do not qualify
latency or direction. Finalzero/clean target andbag exits pass, as do both
eight-flag ownership proofs and all three performed cleanup checks. Case
514.425923005/900 s; no process deadline expires. One inner enumeration race is
retained. Audit scope is small finalized receipts only, with no bag/model/runtime
operation or outcome revision.

Paths under external `pilot/m4_pilot_v9/`; run files under
`runs/2026-09-10/m4-pilot-v9-slot06-B-26090802/`:

| Receipt | SHA-256 |
| --- | --- |
| acquisition/slot_6.json | 242738613d928901156afe6a472d3eed4446c9a3cdd5f8b1f5709e499a3558c8 |
| acquisition/summary_6.yaml | a71983f8d05e8120c8709621298acc1963e76b799854c766f989e6ccb1d1c134 |
| metadata.yaml | 776fe46ccd338c348b73f4519a560923b5c099ff44b2656d0a06f3b670b098ee |
| completeness.json | 5587e1ff2f8ab3f7ec43d57fc171b865895d94b25102f3a61d3e82f81f9de7f7 |
| scenario_result.yaml | 3b10358f445198a2231a410e257422c2437b20cd1fcf361720af99cd763bf0fd |

## Selected live slot 7 binding observation

Independent read-only audit matches exactslot07C/nominal/secondary/holdout/
seed26090802/headless, actual launchargv and shared scenario metadata. Selected
rolling_gesc_v2/moving_cycle_coherence_v1 meanweight.75/policyhash30ed4c7b...75ff;
detector remains pde_mean_v1/heartbeatFalse. Moving owners share exact run and
schema2 stream identity (model-input time/channel0/odom/canonical raw/source/
encoder/objective/provenance); candidate guards remain .75 m/.15 m. Required
direction/policy/epoch/confirmation/candidate/fill-transaction topics have exact
single publishers and recorder subscriptions. SameV6 controller/hash, algorithm/
controller/filter simulation clocksTrue, recorder coordinatorFalse. Recorded
Gazebo/resources bind Q5 installation. Preflight/readiness PASS14:36:48.705885Z,
no parameter capture failures. Final completeness/behavior/payloads are pending.
No bag/ROS/test/model/sourcewrite was used by the observer.

Direct same-session77764 polling confirms live14:38:14.577156Z. Root read-only
SHA-256 check at14:36:44Z matches all645 held source files, no mismatches.

## Nominal holdout slot 7 completed

Slot7C COMPLETE/integrity=True/behavior=False. Slot/sole summary/scenario results
and metadata/recorded launchargv agree exactly. All60 completeness checks pass,
failures/warnings empty. Seven PDE confirmations/eight valid epochs, one candidate4
snapshot and one committed fill. Candidate evidence uses two pretrigger and one
verification revolution. PREPARE312.7 s, commit313.1, objective/directionACK313.2;
three command messages and three result messages, no lifecycle errors.

One direct-repulse recovery completes, but escape ownership fails with reason
`direct measured fill-to-exit alignment is below 0.80`. The failed numeric
alignment is not included in the outcome receipt. Selected anchor is
interior_farthest, displacement1.343568 m against exclusionradius1.377112 m.
Six of14 behavioral predicates pass: recording, cleanup, no forbidden states/
events, local recovery and fill cardinality. Escape ownership plus the seven
remaining goal/path/event/terminal/proximity predicates fail. Stage B runs
332.018 ->632.034 s, expires after300.016 s; live Stage A/cardinality stay True,
staged_monitor_error=None. Final stateSEARCH/globaldistance .251141 m; proximity
.497523 m lacks valid ranked GOAL_REACHED. Forty canonical events differ from34
scoped outcomes. Each direction diagnostic topic has31,251 messages; counts are
not scientific availability or accuracy.

Finalzero/clean target andbag exits pass, as do both eight-flag ownership proofs
and all three performed cleanup checks. Case801.423983474/900 s,98.576016526 s
remaining; no process deadline expires. Completeness console check passes and
its warnings list is empty, but root read the retained sensor-pose sqrt warning
in console.log during acquisition. The short scenario tail omits it; no claim
of a warning-free console or causal effect on performance is made. Receipt audit
and root console-tail observation use no bag/model/ROS/test/source modification.

Paths under external `pilot/m4_pilot_v9/`; run files under
`runs/2026-09-10/m4-pilot-v9-slot07-C-26090802/`:

| Receipt | SHA-256 |
| --- | --- |
| acquisition/slot_7.json | 3b651daf4ebe51c257ca800ba122dd3ff7da4250b21f989840ed972dd6402053 |
| acquisition/summary_7.yaml | 152bdc5004a1cd86fcaba34807d83d645921cd79e5e60b10e19be01c8dc9c923 |
| metadata.yaml | 604d23a031ffeea009ee28ed3e0837b05e7efb9b9078d3b80db043c7c0fc284f |
| completeness.json | 04d7656beab23aaed362b55b382f7d8c7a2c8cf11e4289461baa43645a1810bb |
| scenario_result.yaml | f71ea108d0332233bcdb3efcc59c1d485efd299123a947dea6eaffd898c111cf |

Slot8D readinessPASS14:50:06.303617Z/recordingoperational; direct same-session
77764 poll confirms live14:50:52.061415Z. Nominal block science is not yet started.

## Selected live slot 8 binding observation

Independent read-only startup audit matches exactslot08D/nominal/secondary/
holdout/seed26090802/headless, actual launchargv and shared scenario metadata.
Two-block W6/.18/.5 and heartbeatTrue combine with rolling_gesc_v2/
moving_cycle_coherence_v1 meanweight.75. Moving candidate guards .75/.15 and
VERIFY12 remain fixed. Detector/supervisor/fill/PDE/objective owners share exact
run/stream identity; required canonical topics have the expected sole publishers
and recorder subscriptions. SameV6 JSON/hash/gains.5/5/limits.1/.5 and simulation
algorithm/controller/filter clocks; recorder coordinator wall clock. Recorded
Gazebo resources bind Q5 installation. Preflight/readiness PASS14:50:06.303617Z,
no parameter-capture failures. Final completeness/behavior are pending. Observer
used startup metadata/parameters/topics/console only, with no bag/model/ROS/test
or source write.

The [diagnostic notes](m4_v9_development_diagnostics.md) distinguish slot7's
geometric .80 alignment failure from earlier passing command-ownership checks.
The rejected exit pose/stamp/alignment are absent from its outcome receipts;
no reconstruction from later finalpose or threshold change is made. A future
evidence-retention improvement remains unadopted while V9 is live.

## Nominal holdout slot 8 completed

Slot8D COMPLETE/integrity=True/behavior=False. Slot/sole summary/scenario and
metadata/launchargv agree exactly. Recording61/61 PASS, failures/warnings empty.
Five confirmations/five epochs, one candidate3 snapshot with three pretrigger/
zero verification revolutions, one fill. Snapshot/PREPARE206.9 s,commit207.3,
objective/directionACK207.4. Three command/result messages each, zero lifecycle
errors. One assisted recovery: alignment .996610, entry/exit handoffs14.908/
7.501 ms, ordinary GESC restored. Seven of14 behavioral predicates pass:
recording, cleanup, no forbidden states/events, recovery, escape ownership and
fill cardinality. No valid rankedGOAL_REACHED qualifies proximity .498932 m;
final stateVERIFY_EXTREMUM/globaldistance .245973 m.

The live monitor again has missing-companion error (four live/five final joins).
Stage B225.910 ->375.816 s precedes Stage A timeout375.884−.422=375.462 s elapsed.
It does not establish a full300 s post-recovery observation. Twenty-eight
canonical events differ from22 scoped events; each direction topic has18,593
messages, which do not qualify accuracy/availability. Finalzero/clean target and
bag exits and both eight-flag proofs/all three performed cleanup checks pass.
Case508.719747616/900 s; no process deadline expires. Two inner and one outer
enumeration races remain recorded. No new bag/model/runtime analysis by observer.

Paths under external `pilot/m4_pilot_v9/`; run files under
`runs/2026-09-10/m4-pilot-v9-slot08-D-26090802/`:

| Receipt | SHA-256 |
| --- | --- |
| acquisition/slot_8.json | 6a701263e06bb457f64ca7453e5a9755adba797113175d43d2eda97b876612f4 |
| acquisition/summary_8.yaml | 0adf19a1ac28dd0e5065caa869911d491fce397a037bfe7441f2650c368c4e50 |
| metadata.yaml | a832554423c5b96d9ee7e9a30e38dcaa7dc568fc54a7a12e090f83d74faee223 |
| completeness.json | 945077b5a55734f1a19ef9c6a739d8c211f1e67113adb5f7dac0a9178dedf255 |
| scenario_result.yaml | 5e2e542d24d7b0a31f75e21b4bf9cab918f1a48ac43201e7b78b2a8cf219ef22 |

## Nominal block analysis unavailable

Original block interval67296.238644023 ->67516.238644023 (220 s), started receipt
dc7df4dcd94a722334c677b03fa77d7e67b7f0a727bea09a136eac6b3a047b33, binds exact
complete slots5–8. Labels job timed_out=True/return_code=-15 with integrityPASS,
elapsed112.65797676400689 s; block elapsed118.63102282299951 s. The complete
attempted-science ledger retains allfour rows EVIDENCE_UNAVAILABLE with reason
labels_analysis_timeout. References and summary are skipped for
no_complete_frozen_label_inputs. No retry or extension; partial files stay retained.

| Receipt under external pilot | SHA-256 |
| --- | --- |
| analysis/block_1/labels_job.json | e82a0e3a908258c2c696b9075e57f2a8f3613059d906d2eaf407b48e3c42628e |
| analysis/block_1/block_receipt.json | b61415ba53611bf4735e9674941843fa461c8e50e2c88c104f028e5fbb411b17 |
| analysis/block_1/unavailable_result.json | 1bb60fa9f1959ef306c277e92921361040042733ca7d86cb01d5a00fc61f3a39 |

Direct poll77764 at14:59:52Z remains live. Existing source/evidence release permits
continuation to noise slots9–12 after this complete attempted-science ledger;
scientific unavailability is not a new holdout release or scientific pass.
Context validator under30 s PASS at this nominal evidence boundary. Independent
block audit and existing checkpoint follow, without frozen source edits.

Independent block1 audit PASS: exact slots5–8/receipt links and embeddedjob match.
Clean timeout uses groupSIGINT then pidfdSIGTERM; no failure/survivor/inspection
error and all eight kernel flagsPASS. Job completes67413.840729826 before cleanup
67415.988687581, jobend67416.238687581 and blockend67516.238644023. Partial
slot5/6 labels+metrics and slot7 labels remain; no slot7metrics, slot8 output,
aggregate labels, references or successful summary. Log cancellation occurs
during canonical JSON serialization. Existing release4d877ad7...d0bf6 remains
unchanged for slots5–16, with no new release/tuning/replacements. All645 stored
source maps match contract/final validation; the independent audit did not rescan
current source or read bags. Root observed noise slot9A recording/readinessPASS
15:00:36.844664Z; terminal acquisition receipt remains absent.

Nominal evidence boundary: all645 current source SHA-256 values match the original
hold at15:04:00.049787Z. Context validator and git diff --check PASS. Existing
`timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh v2`
PASS .245235998 s, updating checkpoint.txt. Final material archive remains pending
until this live fixed comparison closes; no source/helper or run artifact is edited.

## Selected live slot 9 noise binding observation

Independent read-only startup audit matches slot09A/secondary/noise/holdout/
seed26090803/headless. The only launch difference is the expected noisy JSON
relocation `/tmp/gesc_phase06_j7dv_c4l/resolved_cost_function.json`; bytes match
frozen `preflight/cost_slot_9.json` SHA-256
87e2ea96cb5bb05b9363e3338796cf2804be5a11102d6ee3cd374eb7345ffcb6.
It selects Gaussian sigma.015/seed26090803, sensor/pose delays0. Actual parameters
retain pde_mean_v1/stationary_v1/heartbeatFalse, V6 controllerhash/gains.5/5 and
ceilings.1/.5. Algorithm/controller/filter clocks are simulation time; coordinator
wall time. Recorded Gazebo/resources bind Q5 installation. Preflight/readiness
PASS15:00:36.844664Z, no parameter-capture failures.

The durable copied noisy JSON and captured_cost_configuration witness remain
pending until run_scenario finalization; dispatcher validates exact frozen hash/
path binding afterward. Startup hash equality is not the finalized witness.
Metadata says recording; final completeness/behavior remain pending. No bag,
ROS command, model, test or source write was performed by the observer.

## Noise holdout slot 9 completed

Slot9A COMPLETE/integrity=True/behavior=False. Slot/sole summary/scenario and
metadata/actual launchargv agree. Recording48/48 PASS with empty failures/warnings;
behavior4/14 PASS (recording,cleanup,no forbidden states/events), ten other
predicates fail. SEARCH only, zero confirmations/requests/fills/recovery,1,686
legacy convergence statuses. Seven canonical events, empty scoped outcome list.
Stage A .428 ->360.454 expires after360.026 s; Stage B never starts. Monitorerror
None, finalglobaldistance3.769821 m. Finalzero/clean target andbag exits/both
eight-flag ownership proofs/all three performed cleanup checks PASS. Case
475.598107817/900 s, no process deadline expires; two inner enumeration races.

Durable `resolved_cost_function.json` byte-equals frozen `preflight/cost_slot_9.json`,
SHA87e2ea96cb5bb05b9363e3338796cf2804be5a11102d6ee3cd374eb7345ffcb6,
Gaussian sigma.015/seed26090803. All100 actual argv tokens match except the single
cost path relocation `/tmp/gesc_phase06_j7dv_c4l/resolved_cost_function.json`.
Captured configuration witness preserves that argv path plus exact durable run
path/hash, and metadata/scenario argv match. Metadata parameter_files still lists
baseline cost source; actual noisy authority is the capturedJSON/argv/frozen
receipt, not that listing. No source/data change or bag/model/runtime analysis
was used by the observer.

Paths under external `pilot/m4_pilot_v9/`; run files under
`runs/2026-09-10/m4-pilot-v9-slot09-A-26090803/`:

| Receipt | SHA-256 |
| --- | --- |
| acquisition/slot_9.json | f4c819b057e206f71eb19c3a0046738428334696086b5b5539b0d21b44286edd |
| acquisition/summary_9.yaml | 7ee8d71f2f8ead3282b3042203f0be00f5fdab78a82bf753fdf1680bf5cf1d43 |
| metadata.yaml | 560fd176373a144075858f56e02af43b6750f1e37d578308d3781ec18d5d7476 |
| completeness.json | b10463b7afe0bf19193e7ce33ac64bcf910ad445c6ab60636949b752022de580 |
| scenario_result.yaml | 4ec7383f83809d7f16fd5d294add641c2952a8fa3cd71408eb97dc13fa69de83 |

## Selected live slot 10 noise binding observation

Independent read-only startup audit matches slot10B/noise/secondary/holdout/
seed26090803/headless. Actual temporary noisyJSON byte-equals frozen cost_slot_10
with same87e2ea96...ffcb6 hash/sigma.015/seed26090803 and zero sensor/pose delay;
relocation is the only launchargv difference. Two-block W6/.18/.5,heartbeatTrue,
stationary_v1 and matching typedstationary request route have expected supervisor
publisher and recorder subscription. SameV6 controller/hash/gains.5/5/limits.1/.5,
simulation algorithm/controller/filter clocks and Q5 resources. Preflight/readiness
PASS15:08:33.651707Z, no parameter-capture failures. Final completeness/durable
noisycopy/captured witness remain pending. No bags/ROS/models/tests/sourcewrites.

## Noise holdout slot 10 completed

Slot10B COMPLETE/integrity=True/behavior=False. Slot/sole summary/scenario and
metadata/actual launchargv agree exactly. Recording52/52 PASS, failures/warnings
empty; behavior4/14 PASS (recording,cleanup,no forbidden states/events), ten other
predicates fail. SEARCH only, zero confirmations/typedrequests/fills/recovery;
stationary audit lists empty and all six counts zero. There are10,651 centroid
diagnostics and seven canonical events versus one scoped CONFIGURATION event.
No score/eligibility breakdown is exposed here; non-detection cause is not inferred.

Stage A .258 ->360.284 expires after360.026 s; Stage B never starts. Final and
live timestamp-binding errors are absent. Finalglobaldistance3.614588 m.
Finalzero/clean target andbag exits, both eight-flag proofs and all three
performed cleanup checks PASS. Case480.726526626/900 s, no process deadline
expires; three inner enumeration races remain recorded.

Captured noisyJSON byte-equals frozen preflight/cost_slot_10.json, same
87e2ea96cb5bb05b9363e3338796cf2804be5a11102d6ee3cd374eb7345ffcb6 hash,
Gaussian sigma.015/seed26090803. All104 argv tokens match except the sole
cost-path relocation `/tmp/gesc_phase06_57mb_gcy/resolved_cost_function.json`.
Scenario/metadata/binding preserve that exact path and captured hash. No source
or data change, bag/model/runtime operation was performed by the receipt auditor.

Paths under external `pilot/m4_pilot_v9/`; run files under
`runs/2026-09-10/m4-pilot-v9-slot10-B-26090803/`:

| Receipt | SHA-256 |
| --- | --- |
| acquisition/slot_10.json | 5afe692d6d027ff41e8b31f0ce87a6c648b0ee8874dbb77dd37e6e0aa5c413fc |
| acquisition/summary_10.yaml | 63cdde774a96de1dbb5e57a0bb1f970bd0c600e983f17d5871b9da6d52f6cada |
| metadata.yaml | 54a5ad78fcc069768010cf09e8db2a792ea1fb182a5dad7bacd60c52f6c8df2e |
| completeness.json | 133d55b14bc360398bf10584ffb62959d84c3f0f53a6a9e1c04c8a7f1abf8d60 |
| scenario_result.yaml | c3d94a2fbce5a3ce8c23db54a776c65db975865e5907a55ba20e907aaad89bac |

Direct same-session77764 poll15:15:34.568661Z confirms the dispatcher live with
slot10 final and no terminal acquisition receipt. Moving noise slot11 follows
under the original release; no tuning, replacements or source changes.

## Selected live slot 11 noise binding observation

Independent startup audit matches exactslot11C/noise/secondary/holdout/
seed26090803/headless. Temporary noisyJSON byte-equals frozen cost_slot_11.json,
hash87e2ea96...ffcb6, Gaussian sigma.015/seed26090803 and delays0. Relocation is
the sole launch difference. PDE/heartbeatFalse combines with rolling_gesc_v2/
moving_cycle_coherence_v1 meanweight.75. Moving owners share exact run/schema2
stream identity; candidate guards .75/.15 and VERIFY12 remain. Required typed
streams have expected single publishers and recorder subscriptions. SameV6 hash/
gains.5/5/limits.1/.5, simulation algorithm/controller/filter clocks, recordedQ5
Gazebo resources. Preflight/readiness PASS15:16:36.581017Z; parameter capture
failures empty. Metadata is recording, with final completeness/copied noisyJSON
witness pending. Observer used no bags/ROS/models/tests/sourcewrites.
# Terminal comparison and closure boundary, 2026-09-10 UTC

The sole dispatcher77764 is terminal1 and directly reaped. This current account
supersedes live snapshots below. V9 is CLOSED_INCOMPLETE; full V2 remains open.
There are10 COMPLETE/integrityPASS/behaviorFAIL slots,1 INCOMPLETE and5 UNSTARTED.
No replacements/tuning/cap extensions. Acquisition elapsed6161.857533947994 s;
enclosing execution6165.657050621994 s; report1.2217872839974007 s. Their separate
scope remains within original budgets. All16 terminal rows/192 target rows exist.

Slot11 outer cleanup fails only its graph difference: baseline[] versus final
`/_ros2cli_daemon_201_43f547f7f0ec4c73834cdd093a15b9c9`. Owned/session lists are
empty, all inspections performed/error-free and both eight-flag kernel proofs
PASS. Inner baseline includes that daemon and cleanupPASS. Independent read-only
inspection found no486 retained V9 identities alive/reused; owner105626,
timeout105630 and actual dispatcher105631 are absent. The failed graph verdict
is not waived. No independent-inner cleanup is present after the outer exception.

Independently retained inner recording fails59/60:21
`V2 objective: atomic cost lacks selected raw/augmented/provenance join` details
in the sole failed v2_synchronized_stream_contract check. Inner classification
recording_evidence_invalid,3/14predicatesPASS. FourPDE confirmations/fiveepochs/
fourVERIFY visits returnSEARCH;0snapshots/transactions/fills/recovery. StageA
360.026 s expires/noStageB;globaldistance3.595541 m. Finalzero and clean target/
bag exitsPASS; case516.167809 s/900, neitherprocessdeadline expired. Three retained
shutdown-time transform_original_receipt_expired warnings do not establish join
failure cause. Runmetadata/summary/scenario/capturednoiseJSON match; outer slot
lacks innerattachments because its exception preceded validation/binding.

All206 pilotfiles/11 rawbags (4155301888 bytes) and both partial science blocks
remain. All192 direction rows are analysis_unavailable,48development/144holdout.
Latency0/12 endpoints,0/6pairs; missing noise/delay endpoint objects remainempty,
not observedzeros. AllC/Dmandatory-stopcounts and3combinedholdoutresults arenull.
The immutable final report preserves every acquisitionfield and all16supplementary
rows. A01–A05remainunqualified. See [human result](m4_pilot_v9_result.md) and
[handoff](../m4_pilot_v9_handoff.md); recorded diagnoses do not adopt future fixes.

Root verified all645 current sourcepins unchanged. Independent small-receipt
review verified93 referenced hashes and fullreportdenominators; separate slot11
and discoveryowner reviews agree. No source/tests/build/ROS/model/bagreplay ran
for recovery. One read-only inspection initially assumed completeness.checks was
a list and raised TypeError; it is a mapping. Corrected inspection confirmed the
21 failures. This was an observer query, not a scenario/validator rerun.

Terminal hashes (pilot paths relative to externalpilot/m4_pilot_v9):

| Path | SHA256 |
| --- | --- |
| acquisition/acquisition.json | f7c27eefe94e8f1d987f05f8f1bfe5e57c85a7595bec58da0eac5b303419ca8a |
| acquisition/slot_11.json | f6278450f32c5edb6fce3c4318ed2006a33c86b04e758ed7b9bb0169f9ffec8f |
| acquisition/summary_11.yaml | 683e1fb2e5c031e256dc961c4df84ecfc815123bfa7407cb9373f19a4c510eb7 |
| runs/2026-09-10/m4-pilot-v9-slot11-C-26090803/metadata.yaml | e172bf89f7e841576f3a054cd53e6b4e41e31ca43e916dbdd11b23392f09d0be |
| runs/2026-09-10/m4-pilot-v9-slot11-C-26090803/completeness.json | 549b82678fc1a6e9da94848ca08763d5a5475b9df0712857482d68206193cdd1 |
| runs/2026-09-10/m4-pilot-v9-slot11-C-26090803/scenario_result.yaml | 52b3ca2eea5af2e16b6a984d5d72476f83d825ce17bd1351b07447adef61e2fb |
| runs/2026-09-10/m4-pilot-v9-slot11-C-26090803/console.log | ebfb00dfaf3048736bdb0c76da1c391b558434a20c74220972c66fe199c5dc66 |
| report/result.json | 8258857924192c9e3ac294960fd70638737f5a7ca3df1b7cb1823ef58e9ea323 |
| report/report.md | 2fbe3c6b73e044e70acb5556fde04ea7fd4996f445609c738de78166cc9b1037 |
| report/report_receipt.json | b4564b2474420aae9efee407b9cbee308163b4673388213b9a80aa36146ae4f8 |

Execution receipt under externalbuilds/m4_v9_budget_comparison_v1:
acquisition_execution_v1.json SHA25627fb4954b96cd19dbdb0344fc5271cd4a915e3f45bb83877a85058ff62b93192.
Full command remains in acquisition_owner_v1.json, unchanged29eadbe1...1521.

Prospective closure-only commands, each once after independent helper review:

```bash
timeout 30s python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v9_budget_comparison_v1/audit_closure_v1.py
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement
git diff --check
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh v2
timeout 60s python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v9_budget_comparison_v1/archive_closed_v1.py
```

Audit checks selectedterminalsmallreferences/current645sourcepins, all16/192rows,
independent slot11 failure and processidentityabsence. Archive streams rawbagbytes
only forSHA256, verifies existing recordedbagreceipts and preserves all206pilotfiles
as externalreferences alongside dirtysourcearchive. No numerical or behavioral
reclassification. Existing V8archiveowner is adapted with explicitV9assertions;
allhistoricalreferences remain intentional. Review caught a preexecution holdout
receipt-field mismatch and overlybroadrecursivehashscope; corrected before any
auditexecution. Inclusivewrapper timing is recorded separately fromhelper time.
Failure of either job remainsretained and doesnot automaticallyadmit aretry.

Closure audit PASS, 2026-09-10 UTC: external
builds/m4_v9_budget_comparison_v1/closure_audit_v1.json SHA256
f3a30ae3c128ab0d6e0e402009a8564a6c697d621ca195f01a72981ff4881a07.
The sole audit took0.452959323 s internally/0.515175102 s enclosing under30 s.
It verifies645 current source pins,101 selected small-file references and490
receipt-owned PID/start identities with none remaining or reused. The identity
population includes analysis children as well as acquisition owners; the separate
486-identity run-only review and43-identity slot11 review have narrower scopes.
All206 pilot files/11 bags,16 outcomes/192 targets and both slot11 failures are
accounted for. Raw bag hashes are deferred to the material archive, without any
bag decoding or reanalysis. Context validator and git diff --check PASS.

Existing checkpoint_phase.sh v2 PASS,0.216754284 s under30; exact command/result
in externalbuilds/m4_v9_budget_comparison_v1/closure_checkpoint_execution_v1.json.
One reviewed60-second material archive is next; no source or evidence changes.

Material closure archive PASS, 2026-09-10 UTC: external
checkpoints/m4_v9_closed_incomplete_v1/manifest.json SHA256
fc818ab0a7831dedeee25876fc65faa3b2142b1daf99b091f351ea16250ad759.
The sole archive completed10.210715831 s under60:420 repository files,
398 external references,1680256-byte verified source tar. Every206 pilot file
and all11 raw bag files are retained as hashed external references; existing
recorded bag hashes agree. Source645 pins and artifact inventories/signatures
remain stable. No bag decoding/reanalysis, source change or evidence rewrite.
Independent claim/helper audits, context/diff,26 local report/navigation links
and repository checkpoint PASS. Exact archive command/timing is in
builds/m4_v9_budget_comparison_v1/closure_archive_execution_v1.json.
This final receipt is appended after the immutable archive; it does not alter
archived evidence. Fixed V9 closure is complete; full V2 and both research goals
remain IN_PROGRESS. Next: adopt a bounded post-V9 correction/diagnostic plan
before source changes or retained-data analysis. No new comparison is released.
