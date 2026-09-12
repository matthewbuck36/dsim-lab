# R5 centered activation-to-escape handoff correction

ADOPTED prospectively2026-09-10 after [M4v10 closure](m4_pilot_v10_handoff.md).
The failed comparison and both narrow-export outcomes remain intact. Source
archive `checkpoints/m4_v10_closed_incomplete_v1/manifest.json` SHA256
`444694a647ec726895d4ff5f580ee20fbe764a755c9090ec36b63897dfddfc67`
contains540 verified source members and retained pilot/evidence hashes.

## Evidence and scope

C accepted a valid moving candidate and activated one Gaussian at85.9s. Its
centered DESIGN proposal at86.0s was checked against that newly active fill,
cancelled with `centered_command_sweep_unsafe`, invalidated guidance and caused
watchdog FAILSAFE before escape. Typed activation was valid; objective/direction
acknowledgements were recorded at86.0s, without a successful escape handoff.
The committed fill remained active after cancellation. The mechanism is a
bounded runtime ownership error, Level B: the just-created mathematical fill
became an avoidance constraint before its own escape handoff could finish.
Keep the safety response, failed experiment and all old artifacts unchanged.

## Owner correction

Extend the existing MovingSupervisor centered-guidance path only. During initial
centered DESIGN, omit exactly the current preparation's authenticated ACTIVATED
fill from the temporary centered-command avoidance list while awaiting the
existing acknowledgement/escape handoff. Require the same uncancelled current
candidate and preparation, accepted typed activation, matching current registry
generation/digest and exact active cluster/fill/revision identity, and the
original unexpired preparation lease. Any mismatch gets the full avoidance set.
PREPARED alone, another preparation/candidate, unrelated fill, stale generation,
changed revision, expired lease, cancellation or another state gets no exemption.

Use the unchanged tracking vector and existing command_sweep_is_safe. Preserve
all other fill avoidances, room/boundary checks, candidate neighborhood, pose and
readiness freshness, original8/12/20-second verification timing and5-second
preparation lease, typed acknowledgement rules, controller/watchdog guidance
identity checks and sole command ownership. Do not stop for a sensor sweep,
fall back to ordinary GESC, widen a gate, activate escape early, alter estimator/
detector/controller tuning, change IDL/topics/launch, or change stationary/legacy
routes. The exemption ends with the existing transition out of initial DESIGN.

## Validation and next boundary

Retain an unchanged-source reproducer before editing, under a separate30s cap
with2s kill grace included in that maximum. Use existing actual
MovingSupervisor/generated-message/control fixtures to reproduce commit before
the next guidance publication and ACK transition. Bind the retained C fill
geometry without copying large observation histories into Git. Demonstrate:

- Before repair the post-activation inward centered proposal cancels; after
  repair the identical nonzero proposal remains valid without cancellation.
- Missing/single acknowledgements stay DESIGN; both valid fresh original ACKs
  are still required for REPULSE. No delayed/duplicate activation shortcut.
- An unrelated obstructing fill and room boundary still reject the proposal.
- Identity/generation/revision/digest, freshness/readiness, cancellation, expiry,
  state or preparation mismatch cannot acquire the exemption.
- Existing guidance state hashes/publication ordering, legacy rolling modes,
  fill rollback/conflict and controller ownership regressions remain valid.

Use one finite focused source bundle (240s work plus10s receipt/cleanup reserve,
260s external maximum including forced termination); retain failures rather than
repeat unchanged. Record source/test/runtime hashes and actual commands. Existing
isolated ROS controller/supervisor test fixtures may run in the selected simulation
domain within this cap and must terminate. No application launch graph, Gazebo,
reference solve or raw bag read belongs to this source milestone.
Independent read-only review then source checkpoint closes R5 source validation.

Afterward save a separate short visible C development protocol using the exposed
condition, test the corrected activation/escape/arrival sequence and complete
its analysis through existing owners. Only then reconsider a new frozen four-arm
comparison. No new comparison or runtime acquisition is released by this source
plan. Simulation only; no physical/Pi/snapshot/V1 changes or commit/push.
