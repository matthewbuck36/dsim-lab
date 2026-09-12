# R22: continuous acquisition established from retained D recording

Measurement, source validation and independent result review COMPLETE on
2026-09-11 UTC. R22 is closed COMPLETE with a verified material archive. This milestone follows the
[adopted plan](r22_readiness_command_pairing_plan.md); exact commands and evidence
are in the [validation record](validation/r22_readiness_command_pairing.md).

The corrected, separately retained D measurement is
**OBSERVED_CONTINUOUS_ACQUISITION with zero mandatory stopped acquisitions**.
C retains the same qualified result and every original common motion field.
The historical evaluator reproduces both original results exactly, including
D's unavailable V13 measurement. V13 remains CLOSED_INCOMPLETE with four complete
development acquisitions and twelve unstarted confirmation slots.

## What changed and why

The controller publishes a final Twist and its diagnostic consecutively. D's
recording-readiness boundary falls between the two receipts for one all-zero
publication. Independently cutting the streams to readiness displaced their
positional pairing and produced 3,233 mismatches.

The single filtered capture verified every full ordinal pair: 8,041 for D and
7,319 for C. There were no interior vector, count, receipt-gap or timestamp-order
failures. D's zero pair 311 straddles readiness by 1.544751 ms; C has no split.
Singleton publisher records and the controller's publication order support this
correspondence, but headerless Twist has no shared sequence identifier.

The existing `evaluate_m4._v10_motion_metrics` now accepts the explicit opt-in
`pairing_basis='full_publication_order_v1'`. It validates complete streams before
admitting only pairs whose two original receipts are within readiness. Full,
within-interval and admitted counts, exclusions and failures remain separate.
Missing/extra records, invalid vectors, mismatches, receipt gaps and timestamp
reversals still invalidate the measurement. Motion thresholds, authority checks,
pose coverage, runtime source and historical caller/version routing are unchanged.

## Measured result

| Arm | Admitted pairs | Boundary exclusions | VERIFY path | DESIGN path | Mandatory stopped acquisitions |
| --- | ---: | ---: | ---: | ---: | ---: |
| D | 7,398 | 1 zero pair | 0.515313 m | 0.016482 m | 0 |
| C | 6,840 | 0 | 0.476943 m | 0.004112 m | 0 |

All four acquisition segments have positive motion and complete coverage. D has
an isolated 0.1 s zero-command overlap during DESIGN, retained below the unchanged
0.5 s sustained-stop threshold. Neither arm has a sustained stationary interval.

Combined with the unchanged earlier development evidence, D reached the evaluator's
global region at 147.998 simulation seconds and passed direction error/availability
with median 12.519 degrees, P90 25.224 degrees and 4/4 eligible averaging targets.
GOAL_HOLD is optional. These are selected development results, not a completed
confirmation comparison or a general reliability guarantee.

## Validation and retained artifacts

All jobs are terminal: capture session 2295 returned 0 in 6.627780 s; focused test
session 47479 returned 0 with 91 passes in 1.63 s; cached component session 28620
returned 0 in 6.045165 s. No failed scientific/test attempt or skipped focused test.
Unexecuted helper drafts and a review-only alias-schema correction remain saved.

Capture used exactly one filtered read each of D and C. The cached component
restored 53,601 captured records, called the motion owner four times, and passed
all 11 historical/control/accounting checks. It made no bag, model, reference,
full-analysis or runtime calls. All 179 execution pins remained stable.
Independent static source review passed; all AST outside the selected function
is identical to its saved original. The 91 tests include 32 new cases plus 59
existing regressions, covering both readiness boundaries, default/C parity,
full-stream faults and actual sustained-stop controls.

Independent cached result review passed all 39 checks without scientific replay.
Both original default objects match V13 exactly; all 20 common C fields remain
unchanged. All 179 current execution pins and eight component output hashes match.
D's three zero-publication reports describe the same 98.8–98.9 s DESIGN interval;
they are not three additive stops. Review SHA256:
`26f04870988809a1160c550098fde24a1b370041b46be8ab5987bf2835b62a89`.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r22_readiness_command_pairing_v1/`.

- `capture/result.json`, `capture/receipt.json` and `capture_cached_review_v1.json`
  retain the structural proof, original-record bindings and independent review.
- `evaluate_m4.before_r22.py`, `evaluator_change.patch`, `focused_tests.xml`,
  `focused_test_receipt.json` and `source_review.json` retain implementation proof.
- `component_prepared.json`, `component_execution.json`, `cached_component/result.json`
  and `cached_component/receipt.json` retain the bounded cached execution.
- `cached_component/slot_4_default.json` and `slot_3_default.json` preserve exact
  historical reproduction; `slot_4_selected.json` and `slot_3_selected.json`
  contain the new measurements.

Selected evaluator SHA256:
`f6369cdd6a3d659cab5f10997945945050e868140f91bfadd09aeb5f54f6765c`.
Component result SHA256:
`02e07e19c34fdb97716c4570037e046f4cf7709bc5a1b700c3afd04205dc28af`.
Component receipt SHA256:
`7f2ae8a7d8077c9a6733918583aadc15702bdee13f302123b071141ddc76e09c`.

## Next boundary and workspace

Next, adopt a new comparison
contract that explicitly reuses the four development recordings and acquires
twelve fresh confirmation runs. Keep source IDs, original receipts and all failed
V13 results intact. New development summaries may substitute only the separately
qualified C/D motion measurements and recompute their completeness conjunctions.
Validate this path through existing orchestration owners before any dispatch.
R22 itself releases no simulation or matrix.

The full research goal remains open, including the unachieved/unavailable original
30% independently labelled basin-entry latency endpoint. Detector component
evidence retains its different, finite scope; integrated arrival differences do
not isolate detector speed.

Branch `feature/gesc-gaussian-robustness-v2` remains at
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`, with task changes uncommitted.
No physical robot, Pi, snapshot, V1, commit or push actions occurred.

Material closure archive COMPLETE: 673 source members individually verified,
source stable, 0.961338 s. Manifest:
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/r22_readiness_command_pairing_closed_v1/manifest.json`,
SHA256 `21385d3af80c3818b581475cbc26db3cb7c381d35eaf488fc394558365a34049`.
The archive retains source bytes, staged/unstaged patches and evidence hashes.
These final receipt paragraphs were added after the snapshot; runtime and
scientific source are unchanged. Context, diff and phase checkpoint checks pass.
