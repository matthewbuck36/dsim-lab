# R4 stationary recurrent comparison pairing — 2026-09-10

Status: SOURCE_VALIDATION_PASS; [exact evidence](validation/r4_stationary_recurrent_pairing.md).
Simulation only. This is the next
incomplete comparison prerequisite in [the arrival handoff](r3_arrival_development_handoff.md),
under the user's [method authorization](method_development_20260910.md).
It does not release a matrix or change any historical contract/result.

## Purpose and fixed method

The four-arm comparison needs PDE/stationary, recurrent/stationary,
PDE/rolling with centered verification, and recurrent/rolling with centered
verification. The recurrent/stationary pairing is presently rejected at runtime.
Implement that pairing to measure the detector change with the stationary
acquisition method held fixed. Do not retune the frozen recurrent detector,
change stationary evidence collection, or introduce a second fill/controller
owner. Global arrival remains the user's success criterion; GOAL_HOLD remains
available but optional. The comparison version, arrival metrics and release
gate are subsequent work.

## Implementation contract

1. Add a distinct `StationaryRecurrentFillRequest` schema1 message and canonical
   `/gesc_gaussian/v2/stationary_recurrent_fill_requests` topic. Preserve the old
   stationary request fields, hash/correlation/admission/deadline semantics, but
   embed the full `RecurrentConvergenceDiagnostics` in this distinct envelope.
   Keep the old centroid message/topic unchanged; never manufacture centroid
   windows, epsilon or arithmetic for recurrent evidence.
2. Extend `stationary_fill_protocol.py` to own selected diagnostic/request types,
   topics and validation. Recurrent validation uses its existing fixed branch,
   fit, confinement and persistence contract. Confirmed history **and persistence**
   must be at or after the immutable Timekeeper origin. Unsupported selection,
   cross-type evidence and changed request hashes fail closed.
3. Extend the existing supervisor stationary adapter and Gaussian stationary
   adapter. Preserve original ROS and steady receipt leases, exact duplicate
   behavior, source SEARCH entry, one candidate per epoch, candidate evidence,
   request/result ledgers, redesign targets, frozen pose/cost samples, deadline,
   revocation and commit guards. Once admitted, historical detector support
   remains valid during the authorized stationary sweep/design; replay never
   refreshes the original admission lease. No moving epoch lifecycle in Arm B.
4. Admit the explicit robust simulation recurrent/stationary selection through
   the existing detector, constructors and launch graph. Keep recurrent/rolling
   working and old defaults unchanged. Forward actual diagnostic/request topic
   parameters to their consumers. Algorithm nodes retain simulation time.
5. Extend the existing recorder, stationary stream validator and analyzer with
   selected recurrent aliases/types. Require exact recorded diagnostic hash to
   nested request to existing GaussianFill/AlgorithmEvent result joins. Preserve
   source/clock/coverage validation and typed presence for zero-event outcomes.
   Use recurrent-specific reported names; legacy centroid output is unchanged.
   A failed selected recurrent audit cannot fall back to legacy interpretation.

## Validation and decision

Reuse the existing isolated schema2 runtime environment as build underlay;
build the extended interfaces in a new external directory, bounded by180 s.
Run meaningful focused tests and relevant existing stationary/recurrent
regressions with explicit per-command caps no greater than120 s (up to480 s
total test allowance). Exercise actual ROS message serialization and node
constructors, protocol cross-type/hash failures, fixed recurrent branch checks,
origin/persistence admission, duplicate/original-receipt behavior, stationary
historical support, frozen samples, authority loss during fit, request/result
joins and recorder selection. Preserve any failed test/build logs.

Source acceptance requires passing those actual owner boundaries and unchanged
legacy contracts. It is implementation evidence, not an empirical Arm B result.
After source acceptance, plan one finite integrated stationary recurrent
development case through the existing runner; its geometry, budgets, measurements
and decision rule must be saved before dispatch. Do not run a full comparison
to discover startup or analysis defects. Continue toward the four-arm comparison
only after this pairing and the remaining science/release contracts work.

Root owns recorder/validator/analyzer and navigation updates. Detector agent
owns common protocol, interfaces, detector and launch. Direction agent owns
stationary supervisor/Gaussian adapters and constructors. Independent review
checks coverage and runtime ownership. Coordinate shared API changes before
edits; retain all pre-existing dirty work. At the material boundary record exact
commands/results, review the diff and run existing context/checkpoint tools.
No physical, Pi, snapshot, V1, commit or push is part of this milestone.
