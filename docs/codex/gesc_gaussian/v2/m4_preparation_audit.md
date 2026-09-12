# M4 preparation audit — 2026-09-09 UTC

Read-only audit during frozen Q1 recovery3 acquisition. M4 remains unreleased;
no runtime/source change or scientific output was inspected for this audit.

The approved16-run matrix is in `plan.md`; no V2 M4 suite/freeze owner exists
yet. Existing `phase08_*m4*` scenarios are V1 artifacts. Extend the existing
scenario schema/runner for behavioral comparison: Q1's observation purpose
requires rolling mode and suppresses intervention, so it cannot be reused as
the pilot's behavior contract. Preserve approved primary/secondary fields,
seeds, disturbances, per-run/suite caps and safety/cleanup aborts.

After independent qualification, B/D use centroid W/score epsilon/nominated
radius; C/D use nominated candidate radius and per-cycle/sector epsilon.
Disable observation-only for pilot arms. The detector score epsilon and M3
trajectory tolerance are distinct quantities.

Concrete B compatibility gap: centroid+stationary currently emits the detector
confirmation event with `source_timestamp_valid=False` in
`convergence_detector_node_script.py` (around883). The inherited stationary
supervisor handler in `supervisor_node_script.py` (around85) rejects that event
and requires its inherited eight-value snapshot. There is no centroid snapshot
subscription on this path. B therefore cannot yet trigger inherited verification
and fill. Resolve through the existing owners with an explicit compatibility
adapter and four-arm integration checks; never put the metre-valued centroid
score into the inherited squared-distance metric. C/D already use typed epoch
binding for both detector modes. A must retain inherited behavior.

M4 next requires a bounded source amendment for this interface gap, qualified
settings integration, an exact scenario/acceptance contract and checkpoint.
Do not edit the currently frozen Q1 source boundary before its fixed acquisition
and analytical jobs have finished. This audit is not pilot readiness.
