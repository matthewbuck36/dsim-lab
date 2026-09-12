# M2 source-clock correction — 2026-09-09 UTC

Status: COMPLETED implementation correction within M2; see `m2_handoff.md`. The closed
`m2_reference_v1` evidence remains unavailable; no replay retry, historical
retiming, new field calculation or Gazebo experiment is part of this correction.

## Evidence and cause

Read-only seed19801 diagnosis found a10Hz Gazebo clock and38,092 joint messages.
Their acquisition headers have no duplicates and one1ms receipt-order regression;
the encoder discards them, producing35,147 conflicting same-stamp readings.
The sensor-transform owner restamps again; raw cost independently has34,953
conflicting publication-key duplicates. Joint headers lead the latest recorded
clock for38,088 messages (maximum101ms, a bag-order proxy). Two existing joint
publishers share the stream; frame IDs alone are not publisher authority.

Retained evidence lives in
`/home/mattb/Experiments/GESC-Gaussian/v2/diagnostics/m2_timestamp_19801_v1/`.
`clock_joint_diagnosis.json` SHA256:
`678f507b9e45ca9648c21543a0d114c1116f49a5679fbf2e703d8a4e62ccd045`.
Its saved inspection command ran under timeout90s in2.760s, exit0. No field or
method output was evaluated. Upstream owners were absent from earlier DDS tests.

## Prospective source contract

1. Existing encoder and sensor-pose owners receive the opt-in continuous mode.
   Legacy/default behavior remains byte/layout/clock compatible. V2 encoder
   publishes relative JointState.header acquisition time. V2 sensor transform
   preserves that exact relative key; its pose remains explicitly cached,
   not simultaneous acquisition. Preserve mixed-source receipt order and reject
   or reset on actual regressions/conflicts; do not sort or infer authority from
   frame_id. Do not change physical trees or Gazebo clock rates.
2. The runner emits static descriptor schema2 with
   `cost_key_basis=model_input_time`. Typed source/objective/direction/observation envelopes use the matching
   schema version. Schema1/publication-time descriptors remain readable for preserved development fixtures/evidence. Schema2's exact float
   raw, source-cost, augmented and metadata key represents model-input time.
   Actual integer cost publication time remains separate and can be identical
   for several distinct acquisitions. ULP consistency checks bind the key to
   its declared time basis. Never synthesize timestamp increments.
3. Source-cost buffers a detached transform while its acquisition stamp leads
   local ROS clock; evaluate only after clock covers it. Bound pending inputs
   by1024 entries and0.5s original-receipt/source freshness; repeated packets
   cannot refresh age. Conflicting/rollback input is explicit, discarded and
   logged, with bounded tombstones. Actual publications retain observed clocks.
4. Schema2 synchronization may buffer support/source metadata up to0.5s ahead
   of its locally held clock. This is clock-delivery admission, not future
   numerical use: clock must cover all source/publication/bracket stamps before
   creating an observation, and all existing50ms bracket/freshness bounds remain.
   Preserve original callback ROS receipt times, which may precede source time;
   add an explicit synchronization admission stamp instead of relabeling receipt.
   Current output pose is the latest already admitted fresh pose. No fabricated
   heartbeat, extrapolation, outcome-dependent duplicate arbitration or future
   output. Clock rollback/context changes reset numerical history and queues. Source
   owners retain their emitted-key frontier; old keys are not reassigned after
   rollback. A changed Timekeeper origin requires a new run. Ordinary rollback
   alone does not permanently latch the composer once new valid evidence resumes.
5. Composer and filter joins wait for clock coverage within the same bounded
   original-receipt lifetime. Preserve exact value/hash/sequence identity and
   objective arithmetic checks. Recorder/validator distinguish acquisition,
   publication, original receipts and admission, with explicit schema semantics.

## Focused validation and next boundary

Add a bounded full upstream ROS fixture: real encoder, sensor pose, source cost,
existing delay, composer and filter; only field/noise functions are analytic
fixtures. Drive distinct source-stamped JointState and Odometry observations
under held100ms /clock ticks, including source-before-clock and cost metadata
before consumer clock catch-up. Assert distinct exact join keys, separate actual
publication stamps, valid bounded recovery, enough observed revolutions and
stale-input inhibition. Include duplicate/conflict/regression and legacy checks.
The fixture owns an isolated domain, publishes no command and starts no Gazebo.

Run focused core/runtime/source/config/recorder regressions, rebuild changed
interfaces in the isolated overlay and record exact commands/results. Preserve
any failed fixture runs. Review and checkpoint the correction before independent
M3 implementation. This correction does not calibrate detector parameters,
qualify natural trajectories, release the16-run pilot or change research targets.

## Review corrections within this version

- Preserve first receipt per raw/provenance/augmented/objective component. The
  synchronized extrema include every actual contribution; the augmented join
  carries both earliest and latest constituent receipts. Duplicate messages
  cannot refresh either original age.
- Same-stamp conflicting pose/encoder support retains bounded tombstones across
  numerical resets, so retransmission cannot rehabilitate an ambiguous stamp.
- Recorder checks schema2 acquisition-key consistency and requires admission
  after source, publication, right brackets and original receipts.

## Contradictory source packets and invalidation ordering

Suppressing a contradictory packet solely at the encoder hid the ambiguity
from downstream confidence. Forward its first finite measured phase with its
original key; forward the corresponding finite transform once. Tombstone later
repeats. The source owner cancels the disputed key and emits an invalid schema2
provenance envelope through its existing publisher: both validity flags false,
empty geometry, next notification sequence, current notification stamp. Retain
the original cost-publication stamp if known, otherwise zero under invalid
flags; this notification does not claim another evaluated or published cost.
The finite original reading reaches the existing rotation owner; no shared
NaN input or additional node/topic is introduced.

Composer and filter validate notification identity and immediately tombstone
the exact disputed key. Filter numerical history resets; pending or late valid
raw/objective/provenance packets cannot restore that key. Repeated invalidation
is idempotent. Past publications remain recorded; invalidation does not rewrite
their history or make an integrity fault a successful source sample. Genuine
regressions follow the same explicit rejection path; no source-time sorting.
