# Q1 filter expiry recovery — 2026-09-09 UTC

Status: IMPLEMENTED AND VALIDATED;233 final combined core/adapter/legacy/ROS
transport/adversarial checks PASS5.38s. Exact evidence is in
`validation/q1_filter_expiry_core.md` and `validation/q1_filter_expiry_transport.md`.
The material checkpoint receipt in `status.md` closes this bounded source
correction under approved simulation-only V2 implementation.
Read `plan.md`, `status.md`, `q1_plan.md` and
`validation/q1_acquisition_recovery3_failure.md` before editing. No acquisition
or pilot is released. Preserve all accepted and failed inputs unchanged.

## Evidence and mechanism

The failed third case never became ready. Origin remained0.0, raw/source/
provenance/objective streams each supplied1659 messages, and pose/encoder each
1660. The filter produced three valid outputs at0.8s, then reported
`pending_receipt_expired` at0.9s and repeated `pending_expired` from1.4s onward.
The controller activated successfully; the final service deadline message
does not demonstrate a controller-manager outage. Do not extend startup or
freshness thresholds to make the run pass.

A10s admission-only replay uses recorded source timing/bag order and synthetic
constant signal payloads through actual adapter/synchronizer owners. Complete
bag-order input admits288 observations without faults. A separately saved
diagnostic withholding exactly the first raw callback admits14 observations,
then none after expiry through10s. An older in-flight key becomes the earliest
joined key after reset, with no remaining left pose/encoder bracket; its next
expiry again destroys rebuilt support. This demonstrates a liveness defect.
The actual runtime trigger is not proven: bag ordering is not callback ordering,
and the recorder's complete prefix does not prove the filter received it.
No numerical filter, geometry, detector, direction quality or confirmation
performance was evaluated in these diagnostics.

## Bounded correction through existing owners

Distinguish pending cost-join expiry from corrupt support or global context
invalidation in `SourceSynchronizer` and `RollingFilterAdapter`. Expiry still
discards pending cost joins, retires every discarded core/adapter partial key,
emits no observation in the fault batch, and resets numerical integration and
rolling/cycle history. It preserves independently valid pose/encoder support
caches with their ORIGINAL source/receipt times and source-order frontiers.
The unchanged500ms freshness,50ms bracketing tolerance and no-extrapolation
rules still decide whether any retained support can be used. Expired support
does not become fresh by surviving a cost-join reset.

Coordinate core and adapter cleanup: retire adapter-only partial keys too,
and do not perform a second global reset after a core expiry. Late components
for an expiry-retired key cannot recreate pending joins, refresh receipts or
repeat the reset. Keep retirement bounded and distinct from used-key payload
conflicts or explicitly poisoned/revoked sources. Malformed keys/context,
actual consumed-payload conflicts, source revocation, support conflict/frame
change, clock rollback and origin/context replacement keep their existing
strict invalidation behavior. Never advance a retirement frontier from invalid
or far-future input. Preserve source/sequence order across expiry; only the
integration/rolling history is restarted.

No filter equations/gains, controller, publisher ownership, source schema,
launch/configuration, scientific thresholds/labels or output qualification
rules change. The legacy/default publication-time path remains selectable;
scope new recovery semantics to the selected schema2 model-input-time path.
Fresh recovery begins with instantaneous output and empty confidence history.

## Required evidence and continuation boundary

Cover missing first startup component then healthy30Hz inputs/held10Hz clocks,
late retired components in multiple orders, first rebuilt target without an
old left bracket, repeated retired packets beyond500ms, duplicate receipt
preservation, stale support rejection, invalid/far-future keys, true consumed
conflicts/revocations, clock/context reset and fresh empty-history recovery.
Use an actual bounded ROS transport test in addition to core/adapter tests.
Run focused existing source/filter/clock/legacy regressions. Preserve the
original complete-prefix and failed prefix-loss diagnostic outputs; use a
fresh corrective diagnostic output rather than overwrite either.

Record exact commands, counts, skips and hashes, inspect the diff and checkpoint
before acquisition. Recovery3 remains CLOSED INCOMPLETE. A prospective finite
continuation may import only its two already accepted discovery inputs if exact
provenance, unchanged scientific bindings and valid-path equivalence are proved;
never import the failed pre-ready third case. Declare that continuation in a
separate amendment after this correction is validated. No scientific result
or M4 release follows from successful source recovery alone.
