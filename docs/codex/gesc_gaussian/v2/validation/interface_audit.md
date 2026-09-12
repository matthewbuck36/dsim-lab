# V2 interface and moving-lifecycle audit

M0 contract recorded 2026-09-08 from the live V2 checkout at baseline `3369cfc`.
This is an implementation contract and source audit, not an implemented or
validated runtime capability. It elaborates the approved [plan](../plan.md).
Only this document was written by the interface-audit subtask; no ROS/Gazebo
commands, source changes, runtime tests, hardware operations, or commits were
performed by that subtask.

## Verified existing ownership and gaps

| Concern | Live owner and finding |
| --- | --- |
| Candidate confirmation | `convergence_detector_node/convergence_detector_node_script.py:779-861` publishes an eight-value legacy snapshot and an event. The existing `r_mean_m2` is squared-distance evidence and must never carry the V2 metre-valued score. |
| Candidate classification | `supervisor_node/supervisor_node_script.py:804-856` accumulates raw-cost/score evidence; `state_machine.py:984-1074` owns counted-candidate decisions. The selected classifier uses raw minimization costs, not augmented costs. |
| Existing fill request identity | `supervisor_node_script.py:84-122` preserves the confirmation's relative source timestamp. `state_machine.py:1077-1132` matches the eventual fill result by timestamp; it has no run/epoch/candidate transaction identity. |
| Fill sample ownership | `gaussian_fill_node/gaussian_fill_script.py:605-653` currently freezes samples ending at request receipt time. A moving verification interval can separate that window from the original candidate. |
| Fill commit | `gaussian_fill_script.py:915-936` commits to the existing `FillRegistry`, publishes active geometry, and publishes compatibility bias immediately. There is no prepared-only stage. |
| Registry | `gaussian_fill_node/fill_registry.py:227-261` is the sole allocator of fill/cluster IDs and revisions. Revisions atomically supersede retained versions. Reuse this owner. |
| Cost activation | `modified_cost_node/modified_cost_script.py:485-567` immediately applies a valid active `GaussianFill`. Its legacy envelope has no run/candidate identity. A supervisor rejection after this callback is too late to prevent activation. |
| Base ownership | `controller_node/controller_node_script.py:561-623` independently gates command combination and watchdog authorization. Both currently stop VERIFY and DESIGN. The controller remains the only `/cmd_vel` publisher. |
| Escape direction | Robust affine terms use supervisor-authorized geometric `safe_direction` (`modified_cost_script.py:583-646`). This is separate from raw-source and augmented GESC improvement signals. |

Paths above are relative to `ros2_ws/src/ros_esc/ros_esc/`. Existing wire
definitions are under `ros2_ws/src/ros_esc_interfaces/msg/`.

## Time and stream identity

All new V2 evidence uses absolute ROS simulation time for integration,
synchronization, intervals, and deadlines. Publication/receipt times are
separate diagnostics and never replace evidence times. Wall monotonic time
remains appropriate for process watchdogs and command wall-time bounds.

The current source clocks are specifically:

- `Odometry.header.stamp`: absolute ROS pose time.
- `Timekeeper.start_time`: the absolute experiment origin; selected mode must
  be `sim time` for this simulation contract.
- Encoder `StampedFloat64MultiArray.timestamp`: publisher-relative experiment
  time, generated from ROS time minus the experiment origin
  (`encoder_node_script.py:120-140`).
- Sensor-transform `.timestamp`: its publisher-relative time, not a separately
  preserved timestamp of the odometry input (`sensor_pose_node_script.py:213-229`).
- Raw cost `.timestamp` and `CostBreakdown.source_timestamp`: raw-cost
  publication-relative time. The cost is evaluated using `transforms_tstamp`,
  but the published timestamp is newly generated afterward
  (`cost_function_node_script.py:267-319`). Thus the current raw-cost source
  timestamp must not be described as exact sensor acquisition time.
- Modified cost retains the incoming raw-cost relative timestamp
  (`modified_cost_script.py:741-744`). The simulation disturbance relay queues
  and republishes original messages, preserving their source timestamps
  (`simulation_disturbance_node.py:217-225`).

The canonical conversion is `absolute_ns = origin_ns + round(relative_sec *
1e9)`. Store integer ROS nanoseconds internally; retain the original relative
value for matching inherited recordings. Do not infer the origin from message
arrival. A changed origin, rollback, frame discontinuity, or run change
invalidates pending evidence and preparation. A ROS restart receives a new run
ID. The selected delayed pose/source streams must be used by every algorithm
consumer; undelayed evaluator streams must not repair algorithm evidence.

Before M2 qualification, preserve the evaluated transform timestamp separately
in the opt-in V2 source provenance, keyed to the unchanged canonical raw-cost
timestamp. This distinguishes model-input time from raw-cost publication and
allows the existing filter/supervisor synchronizer to reject excessive hidden
skew. Retain input pose and encoder bracket timestamps and measured skew in
V2 observations. Do not silently relabel legacy messages. A provenance record
contains observations/geometry only, never source positions or field truth.

Pose/yaw and encoder interpolation must use bracketing observations, shortest
angular interpolation after unwrapping, no extrapolation, and the approved
50 ms synchronization tolerance. Preserve the actual model transform when
available; a reconstructed transform is labeled reconstructed. Detect the
0.10 s delayed-input pilot through source-versus-receipt age, not a fabricated
zero-delay timestamp. Future timestamps and nonfinite values are invalid.

The scenario runner assigns one nonempty `run_id` and an immutable
`stream_contract_id` to the run. The latter is a SHA-256 of the resolved
algorithm pose/raw-cost/encoder topic names, timekeeper topic/origin, frame,
selected channel, and sensor geometry configuration. It prevents accidentally
combining delayed and undelayed graphs. It is a configuration identity, not
field truth.

## Typed messages and immutable payloads

Add new V2 message types/topics while preserving existing message definitions
and array layouts. New publishers and subscriptions belong to existing nodes.
Do not overload `GaussianFill.active=false` to mean PREPARED on the canonical
fill topic: current consumers interpret inactive records as lifecycle removals.

Use the following common typed envelope wherever specified below:

| Field | Type / meaning |
| --- | --- |
| `schema_version` | `uint16`, initially 1 |
| `run_id`, `stream_contract_id`, `frame_id` | `string`; exact matches required, planar frame `odom` for the selected simulation |
| `search_epoch`, `candidate_id` | `uint64`; supervisor-owned monotonically increasing identifiers, zero means no candidate only on diagnostics |
| `objective_revision` | `uint64`; actual cost-composition identity, not a state-message sequence |
| `stamp`, `time_origin` | `builtin_interfaces/Time`; publication time and absolute experiment origin |

`SourceSampleProvenance.msg` is the opt-in source-publisher record on
`/gesc_gaussian/v2/source_sample_provenance`. It contains `run_id`,
`stream_contract_id`, `time_origin`, `uint64 source_sequence`, absolute
`model_input_stamp` and `cost_publication_stamp`,
`float64 legacy_cost_source_timestamp_sec`, `uint32 channel_count`, per-channel
`float64[] sensor_x_m`, `sensor_y_m`, `sensor_world_phase_rad`, and
`bool model_input_stamp_valid`, `sensor_transform_valid`. Existing source-cost
publication owns it; its geometry is the transform actually used to evaluate
the sample. Pair it to the unchanged canonical source-cost timestamp and
channel; reject duplicate conflicting keys. The existing disturbance owner
relays the provenance with the configured source delay. A provenance message
alone never admits a cost before the selected delayed raw-cost message arrives.
This preserves model-input versus publication timing without claiming the
sensor-transform publisher's cached odometry was sampled simultaneously.

`SynchronizedObservation.msg` contains:

- `builtin_interfaces/Time source_stamp`, `cost_source_stamp`,
  `pose_left_stamp`, `pose_right_stamp`, `encoder_left_stamp`,
  `encoder_right_stamp`, and `receipt_stamp`;
- `float64 legacy_cost_source_timestamp_sec`;
- `float64 base_x_m`, `base_y_m`, `base_yaw_rad`, `sensor_phase_rad`,
  `sensor_world_phase_rad`, `sensor_x_m`, `sensor_y_m`;
- `float64 raw_cost`, `augmented_cost`, `sync_error_sec`;
- `uint64 observation_id`, `objective_revision`; `uint32 channel_index`;
- `bool raw_cost_valid`, `augmented_cost_valid`, `synchronized_valid`,
  `sensor_transform_observed`; no invalid sample enters an accepted snapshot.

`CandidateSnapshot.msg` carries the common envelope plus:

- `uint64 detector_confirmation_sequence`, `snapshot_revision`;
- `builtin_interfaces/Time confirmation_stamp`, `evidence_start`,
  `evidence_end`;
- `float64 center_x_m`, `center_y_m`, `neighborhood_radius_m`,
  `centroid_tolerance_m`, `convergence_score_m`;
- `float64 candidate_cost_estimate`, `candidate_cost_mad`,
  `candidate_cost_uncertainty`, `candidate_cost_lower`, `candidate_cost_upper`;
- `uint32 completed_revolutions`, `pretrigger_revolutions`,
  `verification_revolutions`;
- `builtin_interfaces/Time[] revolution_start`, `revolution_end` and
  `uint32[] revolution_sample_start`, `revolution_sample_end` with equal
  lengths and half-open sample indices into the observations array;
- `SynchronizedObservation[] observations`, `string evidence_sha256`.

The supervisor allocates a candidate ID when accepting one detector
confirmation. Its center/frame/epoch/neighborhood are then immutable.
Verification may create newer immutable snapshot revisions containing complete
qualified cycles around that same center. The final preparation snapshot is
exactly the latest three qualifying complete revolutions from the approved
plan; no fill adapter may substitute a new trailing window. An observation is
used once per snapshot. Enforce the existing configured retained-sample cap;
reject excess rather than silently decimate phase/evidence coverage.

Candidate costs retain the selected negative-voltage minimization convention.
The selected source channel and units are recorded in the run manifest.
Uncertainty is the existing MAD spread rule, not a calibrated confidence
interval. Revolution windows are source-time and phase-qualified observations
of the same candidate neighborhood, not exact cost at its centroid.

`FillCommand.msg` on `/gesc_gaussian/v2/fill_commands` contains the common
envelope and:

- `uint8 operation` with `PREPARE=1`, `ACTIVATE=2`, `CANCEL=3`;
- `uint64 command_sequence`, `preparation_id`, `expected_registry_generation`;
- `builtin_interfaces/Time expires_at`;
- `uint64 target_fill_id`, `target_cluster_id`; `uint32 target_revision`;
- `string evidence_sha256`, `prepared_sha256`, `reason`;
- `CandidateSnapshot snapshot`, used only by PREPARE;
- `bool redesign`; `uint8 return_state`, restricted to the existing
  ESCAPE_REPULSE or ESCAPE_ASSIST destinations.

One supervisor publishes this reliable, ordered command stream. Sequence
numbers increase across all commands in the run. There is at most one
uncommitted preparation. IDs are never recycled; redesign targets are explicit.
ACTIVATE and CANCEL repeat identity/hash fields rather than changing payload.
For CANCEL, `prepared_sha256` may be empty if computation has not completed.

`FillResult.msg` on `/gesc_gaussian/v2/fill_results` contains the same envelope,
`command_sequence`, `preparation_id`, `expected_registry_generation`,
`evidence_sha256`, `prepared_sha256`, plus:

- `uint8 result` with `PREPARED=1`, `ACTIVATED=2`, `CANCELLED=3`,
  `EXPIRED=4`, `REJECTED=5`, `ALREADY_ACTIVATED=6`;
- `builtin_interfaces/Time prepared_at`, `committed_at`, `expires_at`;
- `uint64 registry_generation`; `string reason`;
- `GaussianFill fill`, `GaussianFill superseded_fill`;
- `bool has_superseded_fill`; `uint8 return_state`.

PREPARED geometry has `active=false`, zero unallocated fill/revision IDs, and
the explicit prospective cluster target when merging. It is never published
as a canonical lifecycle record. Only the registry allocates final IDs.
ACTIVATED contains the immutable active record and, for a revision, its old
superseded record in the same envelope. No new IDs are allocated on replay.

Hashes use canonical JSON with sorted keys, compact separators, finite numeric
values, integer nanosecond timestamps, and UTF-8 bytes, then SHA-256. Optional
invalid diagnostics are JSON null. Evidence hashing covers the immutable
snapshot excluding its own digest/publication stamp; prepared hashing adds
the proposed geometry, association, expected registry generation, return
state, and deadline. Publisher/receipt stamps of transport envelopes are not
part of the support hash.

## Lifecycle and activation linearization

1. During moving VERIFY, the supervisor gathers qualified evidence for one
   fixed candidate. It abandons insufficient evidence at the inherited
   12-second deadline, or on departure/frame/epoch/safety invalidation, and
   resumes SEARCH with a new observation epoch. It does not stop to collect
   evidence or convert confinement alone into a fill/goal decision.
2. After classification permits a fill, the supervisor sends PREPARE with the
   final immutable snapshot and the current registry generation. The existing
   Gaussian node validates the envelope and copies it into an immutable pure
   computation input. Preparation reuses the estimator/designer/association
   helpers but never calls `commit_new` or `commit_revision`.
3. Preparation computation must not prevent cancellation, fresh-pose receipt,
   state receipt, or heartbeat handling. A worker may compute a pure proposal;
   it must return to the serialized lifecycle owner and cannot publish or
   commit. The existing design deadline includes computation and activation;
   PREPARED does not restart it.
4. Before publishing PREPARED, the owner checks the live pending generation,
   terminal tombstone, evidence hash, deadline, and unchanged registry
   generation. The supervisor independently rechecks candidate association,
   state/epoch, fresh pose, and exact prepared hash before sending ACTIVATE.
5. On ACTIVATE receipt, the Gaussian lifecycle owner immediately checks the
   matching nonterminal run/stream/epoch/candidate/preparation/sequence, prepared
   hash, original deadline, current registry generation, latest valid state,
   and its own latest fresh pose from the selected algorithm pose stream.
   The pose must remain inside the frozen allowed neighborhood; use the
   inherited 0.50-second pose freshness limit for both source and receipt age.
   Redesign must still reference the exact active target revision.
6. **The linearization point is the existing fill owner's atomic registry
   commit after those checks.** There is no await, worker callback, or
   re-entrant dispatch between final validation and commit. Commit increments
   one `registry_generation`, allocates IDs once, and caches its immutable
   ACTIVATED result before publishing it. Both supersession and replacement
   are represented together. Existing fill-created/merged events now describe
   this commit, never preparation.
7. CANCEL before that point creates a terminal tombstone. Late worker results,
   duplicate activation, stale generation, and retries cannot resurrect it.
   A fresh preparation requires fresh identity, not mutation of the rejected
   snapshot. Exact duplicate commands return the cached outcome; reuse of an
   identity/sequence with differing payload is a protocol rejection.
8. CANCEL after commit returns ALREADY_ACTIVATED with the same committed fill.
   It does not delete or quietly undo an accepted persistent mathematical
   fill. Later candidate departure changes motion policy, not retained fill
   evidence. This causal guarantee does not claim knowledge of a cancellation
   still in transit; final freshness/neighborhood/deadline checks bound that
   interval. No old PREPARED response alone can ever activate a fill.

Terminal tombstones and commit results remain for the run. The run ID is
configured on every V2 consumer, so transient/replayed messages from an older
run are rejected before any state mutation. Source-time rollback cancels
pending preparation and uses the existing safety path, not an expiry timer
that unexpectedly grants a second lifetime.

## Active-fill consumers, escape, and return-to-assist

In `rolling_gesc_v2`, modified cost consumes only transaction-keyed ACTIVATED
results from the Gaussian owner. It does not apply unkeyed canonical
`GaussianFill` records as an independent authority. PREPARED/REJECTED/CANCELLED
envelopes cannot modify its objective. Apply each registry generation once,
with exact duplicate suppression and atomic replacement of superseded
geometry. Unexpected skipped generations require replay/recovery of the
missing typed committed result; do not silently construct a partial objective.
Use a reliable result stream with retained commit outcomes and idempotent
request replay. Mismatched-run or contradictory records never become costs.

Canonical `GaussianFill`, compatibility bias, and existing events remain
available after accepted commits for inherited recording/analysis. Legacy
mode keeps its original subscription and behavior. New V2 behavior is opt-in;
do not mix old control consumers into a V2 launch and assume a new message type
alone protects them. The recorder records both the typed protocol and the
inherited mirrors using its existing owner.

The supervisor consumes the same keyed commit envelope before incrementing
candidate/fill counts, appending retained ranking evidence, or starting an
escape. Accepted active fills remain valid across later SEARCH epochs. If a
matching result arrives after the robot already has stable exit evidence,
retain the fill and resume SEARCH; do not command a return to its old center.
If still associated, freeze escape geometry from that committed fill and
apply the existing ESCAPE_REPULSE policy.

For escape-fill redesign, `target_fill_id/cluster_id/revision` and
`return_state=ESCAPE_ASSIST` are fixed in the request. Preparation retains the
old active fill, current escape command owner, original escape timeout origin,
and frozen direction. A rejected/cancelled/expired preparation retains the old
fill and continues the existing bounded escape policy; it must not restart an
escape timer or re-enable raw-source attraction. On matching accepted revision,
replace the target atomically, retain escape provenance, and return to ASSIST
only if exit has not already completed. The selected v8.12 open-field path
normally goes directly to assist on stall; this redesign contract preserves
the existing selectable path without inventing an extra redesign attempt.

For initial preparation, SEARCH-equivalent weights continue during moving
VERIFY/DESIGN. Both controller authorization paths permit bounded GESC there.
The supervisor still never publishes `/cmd_vel`. Safety/recording stops and
GOAL_HOLD remain effective in every stage.

## Diagnostic contracts needed by M1-M4

Add `CentroidConvergenceDiagnostics.msg` on
`/gesc_gaussian/v2/convergence_diagnostics`, emitted by the existing detector.
It uses the common envelope with candidate ID zero until supervisor binding,
plus a monotonic detector confirmation sequence. Required fields are:

- `metric_mode`, `source_pose_topic`, absolute `source_stamp`, `receipt_stamp`,
  `epoch_started_at`, `history_start`, `history_end`;
- six window start/end times and six centroids, five displacement lengths;
- `window_duration_sec`, `epsilon_m`, `maximum_radius_m`, `score_m`,
  `confinement_radius_m`, six-window weighted `center_x_m/center_y_m`;
- sample counts, completed-window count, represented duration, maximum source
  gap, reset sequence/reason, history/metric/confinement validity, eligible and
  confirmed flags. Invalid or incomplete histories have explicit validity,
  not a synthetic score of zero.

Add `GescDirectionDiagnostics.msg` on
`/gesc_gaussian/v2/direction_diagnostics`, emitted by the existing filter. It
uses run/stream/frame/epoch/objective identity and contains:

- cost source/model-input time, pose/encoder bracketing times, receipt/output
  time, time origin, synchronization error and source age;
- synchronized body yaw, current output-frame yaw, sensor joint/world phase;
- instantaneous body/world two-vectors, world mean, final body two-vector,
  actual blend weight, vector magnitudes and units label;
- mean-window bounds/duration, completed revolution count, twelve sector
  counts, three completed-cycle vectors, agreement angle, cycle variability,
  effective magnitude threshold, sample count and maximum sample gap;
- qualification, fallback-used and output-valid flags, machine-readable
  fallback/reset reason, raw-versus-augmented stream selector, selected
  objective weights, and registry/affine direction revisions.

Keep raw-source diagnostics optional and visibly distinct from the augmented
control stream. Near-zero directions have invalid angle evidence. Do not label
these vectors spatial gradients. Original `GescDiagnostics` remains unchanged;
its existing arrays continue to describe the original filter internals, with
the V2 topic explicitly showing the additional world averaging/blend.

Protocol results provide prepare/activate/cancel timing. Existing analyzer
adds separate per-epoch `detector_confirmation_latency_sec`,
`verification_latency_sec`, `fill_prepare_latency_sec`,
`fill_activation_latency_sec`, mandatory-acquisition-stop duration, fallback
duration, and denominators. They are source/simulation-time metrics and do not
overwrite historical `convergence_time` (goal attainment). Ground-truth basin
entry labels and stationary-cycle direction references remain evaluator-only.

## Required later verification; not run in M0

- Identity mismatch, wrong delayed stream, time-origin mismatch, timestamp
  rollover/rollback, interpolation gaps and frame changes.
- PREPARE never emits an active or compatibility fill; work completes after
  CANCEL without committing; ACTIVATE with the wrong hash/deadline/pose/epoch
  is rejected; duplicate activation allocates no extra ID.
- Cancellation/activation ordering on both sides of the commit point;
  publisher/result ordering; old-run replay; missing registry generation;
  same-revision contradictory payloads; all accepted-fill consumers agree.
- Candidate movement during preparation, departed-but-accepted result,
  persistent old fills, atomic redesign, and return-to-assist without extending
  escape time or leaking raw attraction.
- Both controller combination/watchdog gates allow moving VERIFY/DESIGN;
  safety/final-goal stops still work. Missing averaging confidence uses fresh
  instantaneous GESC while truly stale control inputs retain safety handling.
- Centroid score units/windows and direction-frame/phase diagnostics support
  the fixed calibration and 16-run comparison without changing old layouts.

M0 preflight command run by this subtask:

`timeout 30s bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 implement`

Result: exit 0, `Phase v2 implement context is complete.` This is context
qualification only; all implementation and runtime checks above remain unrun.
