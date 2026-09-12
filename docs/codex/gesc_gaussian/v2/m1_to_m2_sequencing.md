# M1 outcome and independent M2 sequencing — 2026-09-09 UTC

M1 implementation and its finite offline evaluation have concluded. **Detector
research qualification is not achieved and no configuration is selected.**
Original M1 and corrective M1a scientific failures, the incomplete M1a label
attempt, and its successful technical recovery remain separate retained records.

The approved plan defines M1's outcome as timed-centroid implementation,
synthetic checks, retained replay and a finite calibration outcome. It also
states that a failed research gate closes that experiment version, not the
full user goal. It does not require a selected detector configuration before
all independent direction implementation. The two mode selectors and arm C
(inherited detector plus new direction) explicitly separate these components.

Therefore, after the M1 records, review and checkpoint, declare **M2** as the
single active implementation milestone. Proceed with source synchronization,
rolling world-frame GESC, confidence/fallback and its independent validation.
Do not keep searching the closed M1/M1a grids for a passing outcome or rewrite
their labels. This sequencing corrects an overly restrictive interpretation
of the milestone ordering; it waives no scientific gate.

## Recorded M1a outcome

- All six finite modeled enclosures qualified; 8,625 point calculations and
  their original source/owner provenance are retained.
- Technical recovery produced 31 spatial intervals across the same eight
  development inputs without recomputing the field. Seven positives last
  12.070–34.136 s; none meets the fixed 54-second common positive support.
- The fresh 36-grid completed. Fifteen settings passed all 79 synthetic
  cases, but no setting qualified overall. Three W=3 s / epsilon=.36 m rows
  each produced one retained negative-interval flag; other rows produced none.
  Unknown outputs remain unknown. No retained positive sensitivity or latency
  estimate is available, and no threshold is selected.
- The calibration summary SHA256 is
  `a7d83b70fcf664432c4bb881fd7a7a59486378ec827e00b2274702b88cbddd67`.
  See `validation/m1a_calibration.md` and `validation/m1a_validation.md` for
  exact commands, artifact identities and the preserved evidence chain.

## Remaining dependencies

M2 is independent of detector W/epsilon/radius. M3 interface/lifecycle tests
can subsequently use explicitly synthetic fixtures, but the calibrated
candidate-neighborhood integration requirement remains unresolved. Test
fixtures cannot satisfy that research requirement.

This sequencing grants no runtime detector selection, Gazebo release,
additional experiment, changed label/denominator, reduced acceptance target,
physical action or full-plan completion claim. A future evidence correction
must be prospective and independently justified; longer observation support
cannot be manufactured by joining interrupted intervals or expanding regions
around observed detector flags.
