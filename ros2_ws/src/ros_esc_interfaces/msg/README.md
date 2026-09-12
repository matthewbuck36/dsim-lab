# Description

This folder contains ROS2 messages intended to be used with the ros_esc package.

`CentroidConvergenceDiagnostics` is the simulation opt-in V2 detector output.
Its absolute ROS source/window timestamps and metre-valued five-shift score
are separate from the inherited relative-time arrays and squared-metre score.
Six complete time-weighted windows provide persistence. `confirmed` is emitted
once in each detector SEARCH epoch; `eligible` describes the current history.
Consumers bind the confirmation to its run, epoch and sequence and check the
explicit validity flags before acting. A positional candidate alone does not
authorize a Gaussian fill or a terminal decision.

The opt-in `rolling_gesc_v2` simulation path adds four typed records without
changing legacy message layouts:

- `SourceSampleProvenance` preserves the actually evaluated sensor transform,
  its model-input time, and the separate raw-cost publication time. Cached
  odometry acquisition time is not implied.
- `ObjectiveCostSample` is the modified-cost owner's atomic receipt: exact
  raw/augmented values and sensor geometry, weights, fill/affine law identity,
  composition time and objective revision.
- `SynchronizedObservation` records source-time pose/encoder brackets, observed
  world phase, reconstructed body demodulation phase and oldest/latest input
  receipt times and the separate synchronization admission stamp. It is nested
  in direction diagnostics and later snapshots.
- `GescDirectionDiagnostics` separates instantaneous filter internals from the
  world-frame rolling mean and current-body output, including actual sector
  counts, three cycle means, variability, confidence and fallback. Invalid
  startup/stale diagnostics do not authorize control. Unavailable numeric
  values use NaN plus explicit validity flags.

All share an explicit run and source-stream contract bound to the simulation
Timekeeper origin. `m2_plan.md` in the V2 documentation defines the exact
synchronization, units, resource bounds and confidence rules. These interfaces
alone do not establish experimental qualification or hardware readiness.

The runner selects stream descriptor and typed-envelope schema 2, whose
`cost_key_basis=model_input_time` binds exact legacy-array join keys to joint
acquisition/model-input time. Multiple distinct acquisitions can share one
actual publication stamp. Schema 1 retains the earlier publication-key semantics
for saved development fixtures and evidence; it is not the selected V2 runner
contract. Legacy/default runtime behavior remains unchanged.

Under schema 2, source headers may lead a subscriber's held simulation clock.
Original callback receipt stamps are preserved and can precede source stamps.
Numerical use waits until the clock covers source, publication and both bracket
endpoints; `admission_stamp` records that boundary without changing receipts.
The oldest actual input receipt still bounds freshness. See
`m2_source_clock_correction.md` for the bounded queues and failure behavior.

An invalid schema2 source-provenance notification (both source/geometry flags
false) can revoke a disputed exact key. It is not a newly evaluated cost. Its
notification stamp is current; its cost-publication stamp is the known original
one, or zero if unavailable. Consumers tombstone the key and cannot rebuild it
from late previously valid packets. Previous outputs remain recorded.


V2 moving lifecycle messages use protocol schema1 independently of nested
schema2 acquisition observations: `SearchEpochContext`, `DetectorConfirmation`,
`PdeHistoryEvidence`, `CandidateSnapshot`, `FillCommand`, and `FillResult`.
The existing supervisor owns SEARCH epochs and fill commands; the existing
Gaussian owner alone commits activation. PREPARED is inactive and is never a
canonical Gaussian lifecycle event. A combined ACTIVATED envelope atomically
names new/superseded versions and before/after registry digests. The PDE wrapper
records actual admitted input support around the inherited transport-filter
state, without claiming exact source times for its numerical bins. See
`docs/codex/gesc_gaussian/v2/m3_plan.md` for the frozen contract and evidence limits.

Q2 adds `GescDirectionPolicyDiagnostics` from the existing filter publisher
owner on `/gesc_gaussian/v2/direction_policy_diagnostics`. Its policy protocol
schema1 is separate from acquisition schema1/2. The companion copies the
direction diagnostic's exact publication/run/stream/reset/source/observation
and objective identities; it never takes a second clock reading to invent a
new publication identity. Existing direction and nested message layouts remain
unchanged so retained bags keep their original CDR decoding.

`three_cycle_v1` names the default0.5/three-cycle policy; selected
`moving_cycle_coherence_v1` binds the shared canonical policy descriptor/hash
and fixed0.75 mean weight. Norm denominator/error are duration-normalized
cost/metre quantities; coherence and its bounds are dimensionless. Invalid or
unavailable values use NaN with explicit flags/reasons. `selected_policy_qualified`
matches the existing direction `qualified` field under explicitly declared
policy metadata. Existing `cycles_valid` and inter-cycle statistics retain
their old control meaning. Default/old policy assertions remain unchanged.
The companion is required evidence only for selected new-policy runs; missing
or mismatched companions cannot authorize a new interpretation of old flags.
No new control publisher or controller policy is introduced.
Norm call counters describe the last accepted update and represented current
window. Repeated publications of the same observation do not count as new
integration work.

Q5 adds simulation Arm B `StationaryFillRequest` schema1 on
`/gesc_gaussian/v2/stationary_fill_requests`. The existing supervisor nests the
unchanged confirmed centroid diagnostic and its original subscriber admission
times, then binds a CREATE or exact-version TARGETED_REDESIGN to the original
stationary DESIGN deadline. SHA256 covers every field except itself. Its
`source_timestamp` is the new request publication minus the actual Timekeeper
origin, used only to correlate existing GaussianFill/AlgorithmEvent results;
the nested detector source/history stamps are never replaced. Distinct requests
cannot collide within the inherited1ns result-matching tolerance. A retry keeps
the same identity and original sample snapshots and cannot refit or recommit.

This request selects `robust_gaussian_v1` with either `centroid_windows_v2` or
`centroid_two_block_v2`, plus `stationary_v1`, in simulation. Legacy A arrays and moving C/D transactions remain
separate selectable routes in the same owners. The recorder requires the B
topic/type with zero events allowed. The existing generic bag reader preserves
the entire typed message and publication stamp; it does not infer a legacy
source-valid flag absent from this IDL. The shared B protocol validates the
relative correlation before the validator/analyzer joins it to results. Its
supplemental timing tables describe observed confirmation/request/result
intervals, never historical goal convergence or independent settling latency.

Q7 reuses the existing `CentroidConvergenceDiagnostics` layout. Its required
`metric_mode` distinguishes unchanged `centroid_windows_v2` (sum of five adjacent
centroid distances) from `centroid_two_block_v2` (distance between the means of
the oldest three and newest three centroids). Both retain six equal-duration
time-weighted windows and five adjacent `displacement_m` values as supporting
geometry. `score_m` is in metres in both modes. The selected Q7 setting supplies
6-second base windows, 0.18-metre threshold and 0.50-metre confinement radius
explicitly; global defaults do not change. Typed confirmations, stationary
requests, moving snapshots and selected recording metadata bind the exact mode.
Missing or historical modes never imply the new formula. No fields or CDR
layout were added or changed for Q7.
# Selected centered moving verification

`VerificationGuidance` schema 2 is an opt-in supervisor proposal on
`/gesc_gaussian/v2/verification_guidance`. It binds run, stream contract, frame,
SEARCH epoch and candidate to an exact `AlgorithmState.stamp` and canonical
`state_sha256`. Monotone `publication_sequence` distinguishes legitimate
same-tick publications; an identical repeat never renews its original receipts,
and sequence rollback/conflicting reuse rejects authorization. The controller
requires that exact fresh companion only in selected centered VERIFY and initial
DESIGN; it retains sole command publication and its speed/freshness gates.
The immutable accepted time, first collection admission and verification expiry
encode the 8-second approach, 12-second collection and absolute 20-second bound.
Initial DESIGN separately carries the existing preparation command expiry.
Invalid guidance carries zero velocities, including DESIGN before its initial
PREPARE exists. An `AlgorithmEvent` of type 12 and
detail `moving verification collection admitted` records the actual first
admission stamp and named candidate/epoch values. The old AlgorithmState,
CandidateSnapshot and AlgorithmEvent serialized field layouts are unchanged.

R4 adds `StationaryRecurrentFillRequest` schema1 on
`/gesc_gaussian/v2/stationary_recurrent_fill_requests` for the explicit robust
simulation pairing `recurrent_geometry_v3` plus `stationary_v1`. Its outer
request fields preserve the original stationary protocol while the distinct
envelope embeds the complete `RecurrentConvergenceDiagnostics`. The original
`StationaryFillRequest`, centroid diagnostic and topic layouts stay unchanged.
No centroid windows or thresholds are manufactured for recurrent evidence.

The original diagnostic's latest admitted pose stamp, model history endpoint,
full persistence support and publication remain distinct. Both history and
persistence must start at or after the immutable Timekeeper origin. Original
subscriber receipt/admission times retain their fixed lease; later authorized
stationary verification does not expire already accepted detector evidence.
The request's `source_timestamp` remains its own publication minus origin,
used for the existing GaussianFill/AlgorithmEvent correlation. SHA256 covers
the complete nested evidence and every outer field except `request_sha256`.
Configured mode selects the exact wire/type/topic and checker; cross-type or
cross-mode evidence cannot fall back to another stationary interpretation.
