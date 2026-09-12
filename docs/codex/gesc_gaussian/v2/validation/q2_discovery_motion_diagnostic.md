# Q2v2 saved motion and timing diagnostic

Status: COMPLETE_DESCRIPTIVE_DIAGNOSTIC. Scope was frozen in
`../q2_discovery_motion_diagnostic_plan.md`; the closed Q2v2 experiment and all
qualification results are unchanged. The single job exited0 in9.135096s:

```bash
timeout 60s python3 /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q2_primary_shadow_v2/diagnostics/motion_timing_v1/report.py
```

The exact source/Humble environment and explicit input hashes are preserved in
the reporting freeze. No field/model, filter, detector, raw-bag or confirmation
read was performed. Source/input hashes remained unchanged and all24 existing
discovery anchors were retained. This is saved-row geometry and timing arithmetic.

## Findings

Both discovery trajectories develop repeated local loops. The residence trace
has total represented path10.504809m over127.228s, endpoint displacement0.412292m
and whole-trace x/y extents0.561384/0.558617m. The approach travels into the local
region and then loops there; neither trace visits the global positive mask.
The fixed6s bins and complete trajectories are retained in the report/figure.

Local annular-mask occupancy is fragmented. Left-sample positive occupancy is
approximately77.418s for residence and72.590s for approach; these sample sums
are not continuous-residence durations. Longest guaranteed whole-positive
source-segment chains are9.486s and9.996s, below the unchanged12s genuine-positive
label requirement. The unchanged saved labels therefore contain no positive
episode. Existing segment predicates supply conservative bounds; no region,
center or circle was fitted to relabel motion. Annular holes remain outside the
positive mask. The conservative exclusion dilation does not fill every hole.

Each run has124.882s uninterrupted qualified SEARCH history, no original pose
faults, maximum source gap0.034s and zero policy reset transitions during
readiness. Startup/terminal admission exclusions are retained separately. These
data rule out absence of usable history as the explanation for missing spatial
residence; they do not yet identify which numerical detector gate rejected.
This describes admitted pose/history and policy continuity, not the live
detector's separate state-callback history. The subsequent recorded extraction
in `q2_recorded_detector_diagnostic.md` found five residence state-related reset
notifications and score rejection of all20 complete snapshots across both runs.

All24 exact anchor identity/time joins pass. Recorded phase-basis residual is
at most2.45e-16rad and instantaneous phase-collinearity residual at most8.49e-16.
Source, admission and publication ordering is internally consistent. Recorded
within-cycle path lengths range about0.091–0.284m. Endpoint displacement alone
can hide looping. These are self-consistency checks and a stationary-reference
limitation, not proof of a causal explanation for every large angular error.
No lag, blend weight, new model or replacement reference was fitted.

Continuous detector score/radius values are not present in the saved label
JSONs. The justified follow-up is the already recorded diagnostic extraction in
`../q2_recorded_detector_diagnostic_plan.md`; no detector/grid rerun is needed.

## Retained receipts and presentation correction

All paths below are relative to external
`qualification/q2_primary_shadow_v2/diagnostics/motion_timing_v1/`:

- Freeze `freeze.json`: SHA256
  `2f8671981235451a282b15d05bcf67789d39112bf6e7b348db6b42561997691f`.
- Reporting script `report.py`: SHA256
  `27faeceb715299475b17f1a86c37c816f9f71caf928b801d9e3f92c797e18e6e`.
- Original `result.json`: SHA256
  `ea4555da78c9ecc9dc77c05dfa495e6a6dbf65d7d6c1bea8caa0b60ba0d0de3f`.
- Corrected wording `result_clarified.json`: SHA256
  `94bba4291bd924e2b526407ee2e3adc3688577f3d003c1c5e6c51cb9bab763b5`.
- Exact24-row `anchors.csv`: SHA256
  `e04ae4bf0873ebfc5a182f1c0abc3430ec8e5c07238aa4c1f309f473199b1b55`.
- Visually checked `motion_timing_layout_v2.png`: SHA256
  `95c829b9110783d27afd250d45880b0bef700d2d827714b358624af8fbe935c0`.
- `final_manifest.json`: SHA256
  `0f80c2903d0b9519a74b0fa47a1ef31d7572fc06b94bfdf40124cc852f14f72c`.

The initial plot footer overlapped its axis labels, and its caption/report
claimed generically that holes were in the exclusion mask. A saved-metric-only
render fixed the layout; a text-only report correction accurately describes
the existing mask. Original files are preserved, numeric parity was verified,
and no reporting/scientific computation was repeated. The final figure is the
presentation artifact; the original and corrected manifests retain provenance.

## Next research boundary

The approved objective is sustained positional settling, including circling;
a detector candidate is not proof of an extremum, fill or terminal goal.
Prospective confinement calibration can preserve that objective while keeping
Q2 annular truth unchanged. It must define labels independently of detector
outputs, use a fixed region or a prospectively frozen prefix-derived center,
and preserve explicit directed-drift/large-loop negatives and unknown support.
Changing labels alone cannot make an unresponsive score pass.

A later finite joint study should evaluate detector/neighborhood support and
direction quality independently on declared held inputs, reusing the validated
owners. The matched30% latency target, wrong fill/GOAL comparisons and actual
fill/escape/SEARCH/ranking are M4 outcomes. They are not prerequisite successes
that must already exist before its development arms. M4 and broad readiness
remain unqualified; no new study is dispatched by this diagnostic report.
