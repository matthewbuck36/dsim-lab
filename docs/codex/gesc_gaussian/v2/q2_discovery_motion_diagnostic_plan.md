# Q2v2 discovery motion and timing diagnostic

Status: ADOPTED bounded diagnostic under the approved simulation-only V2 goal.
Q2v2 remains CLOSED_EVIDENCE_UNAVAILABLE, closure SHA256
`51d73de197aa24f2aba8cb9f1eac576aaaa38e7519d6abc672f5113a9acfa137`;
material checkpoint SHA256
`014149d7d4a3f91a7f4797f43429ea13cadd3cf893645b88367c3ea21ee66d28`.
This is a descriptive report on saved discovery rows, not another qualification
study, parameter search, numerical reference run or reinterpretation of truth.

## Fixed scope and inputs

One60s reporting job, exclusive output
`qualification/q2_primary_shadow_v2/diagnostics/motion_timing_v1/` under the
external V2 experiment root. Save the script and input hashes before execution,
then JSON, a24-row anchor CSV and one figure. Original source, observations,
labels, geometry and results remain unchanged. Confirm input hashes after the
job. No Gazebo, ROS initialization, raw bag or confirmation scientific reads.

Allow only the closed study's discovery files:

- `analysis/discovery_labels/labels_26090931.json` and `labels_26090932.json`;
- `analysis/discovery_targets/inputs_26090931.json` and `inputs_26090932.json`;
- `analysis/references/references.json` and its existing24 discovery anchors;
- the saved `replay/m1a_labels_v1/geometry_1.json` with its unchanged positive
  and exclusion cells, plus closure/contract/target metadata for identity checks.

The report script reuses the existing enclosure membership owner; it does not
implement a new model, detector, filter, labeler, recorder or analysis pipeline.
All motion measures below are descriptive geometry/time arithmetic on fixed
saved rows. No parameters, trajectories, targets or reference vectors are fitted.

## Questions and fixed calculations

1. Plot both full saved discovery trajectories over the unchanged positive and
   exclusion cells, colored by source time. Keep the annular holes visible.
   For every consecutive6s bin from the first recorded pose (including a marked
   final partial bin), report net displacement, piecewise-linear path length,
   axis-aligned extent and endpoint source support. Report time in each existing
   mask using only consecutive valid source segments, with explicit boundary
   uncertainty and no extrapolation. Do not convert short visits into new
   positive labels or fit an orbit/enclosure to create a favorable region.
2. Summarize original pose faults, `qualified`, admission reasons, source gaps,
   SEARCH epochs and history generations. Report uninterrupted qualified support
   spans under the original0.5s gap cap and recorded policy reset transitions.
   Missing spatial residence precedes readiness/history masking: a history reset
   alone cannot explain absent genuine12s annular residence. Continuous detector
   scores/radii are not in these JSONs; do not infer which gate rejected a window.
3. Preserve all24 saved anchors and angles. Tabulate their recorded cycle bounds,
   duration, net displacement, within-cycle path length/extent, phase/yaw change,
   source/filter/publication/admission timing, reset/coherence state and objective
   identity. Match source indices/identities exactly. Existing `translation_m`
   means endpoint net displacement and may hide looping. No reference/model
   calls, candidate weights, lag fitting, alternate anchors or smoothed phases.

Use exact existing mask membership. If exact continuous segment mask occupancy
is not provided by the existing owner, report left/right sample occupancy with
the total duration of membership-changing segments as uncertainty instead of
inventing an interpolated residence claim. Field evaluations are forbidden.

## Stop and interpretation

Stop after this single diagnostic with an identified mechanism or a precise
missing observable. Verify the figure and saved arithmetic/identity joins;
bounded report fixes may correct an identified implementation mistake without
rerunning the frozen scientific study. Keep failed diagnostic artifacts.

A demonstrated timestamp/frame/history implementation defect supports a bounded
Level B correction, documented before source changes. If fixed saved data show
confinement with sufficient history but no score information, the next justified
action is extraction of the already recorded centroid diagnostics, under its own
bounded declaration; no detector/grid rerun. Redefining confinement in an excluded
hole as convergence or replacing the stationary-cycle reference objective is a
Level A research choice, not a repair to Q2. It requires a separate prospective
definition and explicit user decision where it changes the approved objective.
No automatic new experiment, threshold/weight change, confirmation access or M4
release follows. The full approved plan and16-run pilot remain incomplete.
