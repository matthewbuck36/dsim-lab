# Q5 Arm B adapter validation

Status: CLOSED_SOURCE_VALIDATION_PASS. Scientific qualification remains open.
Authority: ../q5_stationary_centroid_adapter_plan.md.
Pre-edit runtime checkpoint: Q4 closure, SHA256
`6f13e59f52b0752a42651b6270c0c0a7e548888abc745ff8d9390534d35b8a33`.
External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/q5_stationary_centroid_adapter_v1/`.
Original supervisor, state machine and Gaussian runtime copies are retained.

## Actual-node absence baseline

Definitive v2 check:1 expected failure in0.34s, exit1, timeout60s/domain193.
The actual robust centroid/stationary SupervisorNode has no typed
CentroidConvergenceDiagnostics subscription on the existing canonical
/gesc_gaussian/v2/convergence_diagnostics topic. The first v1 fixture used an
incorrect expected topic label and is retained separately; it is not the
qualified absence result. Runtime owners remain unchanged through both checks.
Receipt baseline_receipt_v2.json SHA256
`32ea90a51d256cedeea993f581ac847841f26748e0a0c60ab533ab31d7a2b265`;
definitive log SHA256
`52a009aa2b9dc9793360e4c1da786b8746f6d4c6719216e2f52c61bbb6c211a0`;
exact test snapshot SHA256
`99c9020af4042c9fe903e82a773b6703bcb02f533003e955db67687339dfbff6`.
Exact command is retained in baseline_command_v2.txt and the receipt.

## Shared contract preparation

Root added the declared StationaryFillRequest IDL/CMake entry and moved
centroid_diagnostic_errors unchanged into centroid_contract.py; validate_run
re-exports the original public function. AST comparison PASS against original
validator bcf63a963..., with exact original bytes and extraction hashes in
centroid_contract_extraction.json. No runtime adapter was edited before the
actual-node absence baseline. New type build/binding and independent contract
regressions must pass before source qualification.

Record exact build/commands, final source/test pins, source/regression/DDS
outcomes, failures/skips and material closeout here as work completes. All
runtime/build/test commands are bounded; no scientific acquisition, old bag/
model/grid rerun or physical action. Q3/Q4 source and Q2 science remain closed.

## Interface, source and recording checks

The isolated new interface build passed in25.4s (package25.1s), exit0 under
180s. interface_build_v1.log retains the ordinary underlay override warning.
interface_binding_v1.json verifies all20fields, CREATE1/TARGETED_REDESIGN2,
exact IDL SHA6516196eb42e90fa962c17c1017eeff47957f68cf9ec673809c8b84138c0fea2
and generated CDR roundtrip without ROS initialization. No legacy IDL changed.

Independent source tests first passed77 in2.07s. Review then found bounded
correctness/compatibility details: B-only obsolete-DESIGN handling after an
adapter FAILSAFE; state elapsed computed from the same captured publication
stamp; pending same-tick predecessor-state delivery; precommit registry staging
outside the authority lock; and avoiding a new-message import in unselected
legacy fitting. The final independent suite passed210 in15.81s under120s,
domain193, including actual supervisor transitions, actual Gaussian numerical
parity, original sample snapshots, CREATE/REDESIGN, concurrent revocation,
readiness/clock/sequence/correlation/epoch edges and focused inherited stationary
and moving regressions. No corrected test failure occurred. Receipt
independent_receipt_v2.json SHA256
5e4f25c12cc1940456b1e6f9994a970a35c632ec42a7423f97543d95a7acf9b5
contains exact commands, source/test byte pins and retained logs. The prior
31-test Gaussian mathematical regression (1.38s) remains its earlier boundary.
A separate actual legacy fit on the Q2-only overlay, with the new message absent
and selected helper import forbidden, passes1 in0.80s; legacy_old_interface_v1.log.

Root recording checks pass40 in1.72s (timeout60/domain182). An appended actual
sqlite/CDR generic-reader check plus inherited Q3/centroid/rolling recording and
lifecycle regressions pass168 in28.27s (timeout90/domain182). Receipt
recording_receipt_v1.json SHA256
 dc34cbc857a53b6161f6a4254fe6055bb1332d6b62f0036d6f07ce0e9d3f797b
binds exact commands/logs and recording_source_v1/ snapshots, including the
first40 test bytes before the appended sqlite case. Tests use an actual emitted
Supervisor request, preserve nonzero-origin/history/receipts, check configuration,
DESIGN source-entry deadline and prior state, exact retries and unique CREATE
candidate use, target revisions and legacy result joins. Superseded old fill
publications keep their original request correlation; no new deadline is imposed
on that later lifecycle record. No-candidate/no-request/no-result outcomes remain
valid. The full-validator fixture intentionally lacks unrelated streams and
asserts only its scoped new check, never claims complete run acceptance.

The generic bag reader needs no Q5 source edit: it already decodes manifest
message types and preserves nested fields/publication stamps. The request has no
legacy source-valid boolean; its generic record retains false while the shared
B protocol explicitly validates correlation for scoped analysis. The existing
validator and analyzer share stationary_centroid_validation.py. Supplemental
request/outcome tables and intervals leave historical goal convergence_time
unchanged. Bag receipt order is not used as cross-topic callback authority;
recorded checks do not reconstruct the unrecorded steady-clock precommit guard.

Eight actual Humble frontend/RCL dry parses (A/B/C/D with defaultFalse and
explicitTrue readiness) pass with no nodes launched; frontend_four_arms_v1.py
and .log retain exact selected parameters. B Gaussian pose matches selected
algorithm pose; A/C/D retain inherited Gaussian pose. Both B adapters share
actual entity Timekeeper, metric parameters, freshness and DESIGN timeout.
The final isolated ros_esc+turtlebot3_rotating_sensor resource build passes
2packages in4.46s under180s, resource_build_v1.log. Installed binding and
actualDDS evidence follow below before Q5 closure.

## Installed binding and independent evidence review

Final build receipt build_receipt_v1.json SHA256
bdca0cf2152b299e39d40b83f29a4279f35ed2a155496d93096182dd4c7f48ba
records exact resource build/binding commands and logs. resource_binding_v2.json
SHA256 c074e35cfe3c05b2bd50509f7697b312674d460fea98139217e4f81fe183b497
confirms9 current source owners, installed launch resource and20-field generated
message on the Q5 overlay, without ROS initialization. The first binding fixture
failed because it incorrectly required the symlink-resolved generated message
under install; its actual target is correctly under Q5 build/rosidl_generator_py.
The retained resource_binding_v1_failure.txt explains that fixture-only error.
No source correction or rebuild followed; v2 checks installed and resolved paths
separately. The initial interface schema/CDR build result remains unchanged.

Two independent reviews of the shared recorded audit found no remaining material
issue after adding operation-specific DESIGN prior-state and distinct-CREATE
confirmation-use checks. Stable retries, target history, superseded original
correlation and unselected metrics behavior agree with the held runtime. These
are source/recording findings, not fresh scientific validation.

## Actual DDS and source closeout

Actual B transport passes1 in2.96s, timeout90/domain184. A supplied synthetic
centroid diagnostic passes through real DDS to the actual Supervisor, its raw
RotationCostWindow verification and stopped DESIGN, one typed request at1019.6s
with actual origin1000s, actual Gaussian77-sample fit/generation1, exact19.6s
legacy result correlation and Supervisor ESCAPE acknowledgment. The real stop
input produces an observed zero supervisor command. This is synthetic transport
and real owner/estimator evidence; no detector/Gazebo/controller process or
scientific field is running in that fixture.

Focused existing moving DDS passes3 in21.20s under90s, actual fixture domains
177/185 (command requested184). It covers prepare/commit/cancel/composer and
Supervisor acknowledgment, not a final-zero observer. The separate existing
actual controller subprocess moving-VERIFY/SIGINT check passes1 in1.63s under
60s/domain184 and observes its final zero. All first transport outcomes passed;
no transport fixture correction or runtime retry was needed. Receipt
gaussian_adapter_transport_receipt_v1.json SHA256
69182dbf6f9f9b5cf20f9634988d336af5f9d2c70cc21bf1853f2a6775e2e641
retains exact commands, logs, original/held source and test pins, frontend and
old-interface results, and the copied controller subprocess log.

Final root diff review, git diff --check and timeout30s context validator PASS.
The new selected IDL, common pure contract, adapters, shared stationary fit,
launch/config evidence and supplemental recorder/analyzer joins are complete.
Q3 detector/Q4 activation sources and all scientific parameters/models/studies
remain unchanged. Q5 is a source prerequisite, not achievement of detector,
direction or full-pipeline research targets. The unchanged16-run M4 pilot and
one finite prospective scientific development decision remain. No physical
files/devices, V1 source, Git commits or pushes were touched.

Handoff: ../q5_stationary_centroid_adapter_handoff.md. Material checkpoint and
immutable external archive receipt are recorded in live status after creation.
