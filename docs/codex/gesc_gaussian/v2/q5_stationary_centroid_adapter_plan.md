# Q5 detector-only Arm B integration

Status: CLOSED_SOURCE_VALIDATION_PASS under the approved simulation-only V2
goal. See q5_stationary_centroid_adapter_handoff.md and validation/q5_stationary_centroid_adapter.md. Q3 and Q4 source work is closed. Read AGENTS.md, plan.md, status.md and
validation/arm_b_adapter_design_note.md before editing. No scientific rerun.

## Scope and source issue

Arm B selects robust_gaussian_v1, centroid_windows_v2 and stationary_v1.
The detector emits a typed centroid confirmation, but the stationary supervisor
accepts only eight-value PDE/event confirmation and has no typed consumer. Its
fill request also assumes the legacy array. Complete the two adapters inside
the existing supervisor and Gaussian nodes so B retains stopped verification,
existing RotationCostWindow/ranking, receipt-ended robust fitting and escape.
A stays legacy stationary; C/D stay on the moving transaction route.

Preserve legacy public arrays and units. Never put the metre centroid score
into r_mean_m2 or invent PDE values. No new estimator, controller, supervisor
node, recorder, worker, scientific model or physical branch. Positional
settling remains a candidate, not a fill/goal decision.

## Frozen typed request contract

Add StationaryFillRequest.msg on
`/gesc_gaussian/v2/stationary_fill_requests`:

```text
uint32 schema_version
builtin_interfaces/Time stamp
builtin_interfaces/Time time_origin
builtin_interfaces/Time expires_at
builtin_interfaces/Time confirmation_received_at
builtin_interfaces/Time confirmation_accepted_at
uint64 request_sequence
uint8 CREATE=1
uint8 TARGETED_REDESIGN=2
uint8 operation
uint64 target_fill_id
uint64 target_cluster_id
uint32 target_revision
ros_esc_interfaces/CentroidConvergenceDiagnostics confirmation
bool candidate_evidence_valid
float64 candidate_cost_estimate
float64 candidate_cost_mad
float64 candidate_cost_uncertainty
float64 candidate_cost_lower
uint32 candidate_rotation_count
float64 source_timestamp
string request_sha256
```

Schema version1; hash every field except request_sha256 using the existing
canonical message/hash helpers. Nested confirmation supplies run/frame/topic,
detector epoch/sequence, center and untouched original history. CREATE has zero
target fields; REDESIGN names the exact active fill/cluster/revision and sets
candidate_evidence_valid=False, preserving the inherited absence of a
candidate-derived amplitude floor on redesign. CREATE preserves the selected
candidate-informed evidence required/forbidden policy and scalar units.

Use the actual selected Timekeeper origin. B's source_timestamp is explicitly
the new request correlation `(stamp_ns - origin_ns) * 1e-9`, computed once and
echoed by existing GaussianFill/AlgorithmEvent results. It is not a replacement
for the nested detector source/history stamps. A/C/D correlation stays unchanged.
Never dispatch distinct request identities whose correlation collides within
the existing1ns result-matching tolerance. Wait for genuine clock advance within
the original DESIGN deadline; never synthesize or adjust a source stamp.
The bounded sequence/hash ledger (existing4096 lifecycle limit) makes retries
idempotent: original receipts/snapshots persist, no refit/recommit, cached
terminal outcomes can be replayed. Conflicting/reordered identities reject.

## Shared contract and runtime owners

Move the existing centroid_diagnostic_errors function unchanged into the pure
convergence_detector_node/centroid_contract.py module; re-export it through the
existing validator import. Runtime and offline checks reuse this one arithmetic
contract, without importing the recorder/bag analyzer into running nodes.

Add a small common stationary_fill_protocol.py for selection, schema/hash and
static request validation, reusing that centroid contract, CandidateFillEvidence
and existing time/hash helpers. Required shared exports:
`STATIONARY_FILL_REQUEST_TOPIC`, `stationary_request_sha256(message)`,
`stationary_request_errors(message, expected_run_id=None,
expected_frame_id=None, expected_pose_topic=None, origin_ns=None,
maximum_source_gap_sec=0.5, pose_freshness_sec=0.5)`, and
`stationary_candidate_evidence(message)`. Static validation checks original
confirmation admission times; current live authority belongs to the adapters.

Supervisor B adapter:

- Latch actual Timekeeper origin; malformed/changed origins fence acceptance.
  Use current supervisor run and SEARCH entry, selected pose topic/frame, full
  six-window arithmetic, score/radius, source/publication/receipt ordering and
  original ROS/steady freshness. B ignores legacy convergence status/events as
  confirmation authority. A's helper and behavior remain selectable unchanged.
- Defer bounded future confirmations until clock coverage, retaining original
  receipts. This new subscriber admission lease is fixed500ms, separate from
  configured nested detector pose freshness and live state freshness. Bind each
  detector epoch/confirmation once to current SEARCH; old
  epochs/replays cannot rearm it. Accepted history persists through VERIFY,
  DESIGN and targeted redesign without a new0.5s historical-data expiry.
- Use a neutral candidate-center accessor for existing active-fill association.
  Feed the existing transition inputs; retain stopped VERIFY/DESIGN commands,
  candidate cost windows, classification and timeouts. Dispatch a typed request
  at the existing stationary DESIGN branch, with expires_at fixed to original
  DESIGN entry plus the existing fill_design_timeout_sec.

Gaussian B adapter:

- Freeze first ROS/steady request receipts and tuple(pose_snapshots) /
  tuple(cost_snapshots) before any clock/state wait. Preserve that receipt-ended
  fit window; even late-arriving samples stamped earlier cannot enter it.
- Add bounded original-receipt Timekeeper/state/request admission. A request
  can precede matching DESIGN state across DDS topics; wait for matching live
  authority without renewing receipts. Later SEARCH/GOAL/FAILSAFE, run/origin
  faults and deadline expiry revoke pending work. Validate exact redesign target.
- Normalize both entry routes into one internal robust request context, retaining
  legacy insufficient-samples-before-decode rejection order. Share the existing
  synchronization, estimator, designer, association, registry and publication.
  Robust fitting currently derives its center from synchronized samples: the
  centroid center is provenance/association data, not a new numerical constraint.
- Keep synchronous fitting in the existing serialized fill callback group.
  Put lightweight B state/Timekeeper authority updates in a separate group on
  the existing two-thread executor, with an immutable guarded generation/token.
  Check matching live authority/deadline immediately before registry mutation
  under the authority lock so a delivered revocation can stop a late commit.
  Do not pretend the original serialized state callback can refresh during fit;
  do not introduce an estimator worker or hold authority locks during fitting.

## Wiring, evidence and bounded validation

Extend existing IDL/CMake, launch, recorder/topic manifest, bag reader, validator
and analyzer only for selected B needs. Bind Gaussian B pose to the selected
algorithm pose and both adapters to the existing selected Timekeeper. Preserve
the current stationary odom-frame restriction. Expose/pass the existing centroid
freshness parameters so recorded limits match actual selected node values.
Record typed request identity, nested confirmation and relative result joins;
deduplicate retry outcomes by request identity. No candidate/request is a valid
outcome: recording presence/type must not require a fill event. Historical goal
convergence_time and A/C/D evidence behavior remain unchanged.

Save pre-edit source and an actual-node typed-consumer absence baseline before
runtime changes. Build the new interface in an isolated external overlay, then
verify selected imports and all four launch modes. Independent tests cover
typed confirmation through real supervisor transitions, stationary command
authorization, legacy-event bypass, nonzero origin, future callback ordering,
original snapshot/receipt preservation, full support/identity/hash/sequence,
clock/recording/authority revocation, correlation collision, CREATE/REDESIGN,
pipeline numerical parity and deadline/revocation during fitting before commit.
Reuse existing retained-redesign and stationary supervisor regressions. Then
run bounded actual DDS B transport through confirmation/verification/request/
fill/result correlation and focused C/D regressions, including final zero.

Every ROS/build/test command is explicitly bounded. Record exact commands,
outcomes, failures/skips, source/test pins and artifact paths in
validation/q5_stationary_centroid_adapter.md and live status. Inspect diffs,
context/checkpoint and archive at the independently validated source boundary.
No commit/push is implied. This releases a source prerequisite only: one finite
settling/direction development decision and the unchanged16-run pilot/report
still remain. Preserve all closed scientific versions and sealed confirmation.
