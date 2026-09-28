# Selected V3 numerical helpers

These modules contain pure selected mathematics extracted from
`archive/pre-v3-refactor-20260928` (`e7267740fc64f1a1c06bcb09ad25a60c57d1f72e`).
They do not import archived owners, ROS, lifecycle messages, source joins,
publication hashes, launch settings, or physical interfaces. The V3 core owns
observation admission, epochs, availability, commands and registry commits.

- `gesc.InstantaneousGesc`: measured-phase full-rotation washout/demodulation.
  Output uses the pre-Euler state; the first observation has zero integration
  duration. Returns `Demodulation`; a source gap clears filter history.
- `rolling.RollingGesc`: body-to-world rotation, source-time trapezoidal
  full-cycle mean, three-cycle warmup, and immediate instantaneous fallback.
  The selected 5 Hz policy has no rolling sector-density gate. A qualified
  mean contributes 0.75 and the instantaneous vector 0.25. Original source,
  receipt and output-pose timestamps determine freshness.
- `rolling.coherence_job/compute_coherence/apply_coherence`: immutable worker
  snapshot, bounded worker quadrature, then exact source/reset/objective match.
  Main-thread update/evaluate performs no quadrature. A job recomputes current
  window segments instead of retaining the old callback's mutable norm cache;
  each segment keeps a 2048-evaluation budget and the complete window keeps
  20000. Results keep their original observation time. Unavailable coherence
  leaves the instantaneous direction available if it is meaningful and fresh.
- `recurrent.RecurrentGeometryDetector`: causal static, circle and oscillation
  models with the original 6-second evaluation schedule and persistence.
  `start_epoch(str, start_ns)` rearms a nomination; `update(ns, xy, frame)`
  returns evaluations. Nomination observes confinement, not source identity.
- `evidence.MovingRawEvidence`: immutable `RawObservation` records, actual
  measured revolutions, geometric comparability and raw-cost summaries.
  Selected defaults require one actual sample per sector and three qualified
  cycles under `recurrent_trapping_v1`. This is research evidence, not motion
  admission. Original base coordinates/yaw support fitting; objective cost is
  evaluated separately at the measured sensor coordinates.
- `verification.tracking_command`: unchanged moving centered-collection law,
  delegated through the original directional-controller numerical API.
- `basin`, `fill_design`, `registry`, `fill`: robust bounded fitting, adaptive
  anisotropic Gaussian construction, association, immutable preparation and
  staged local commit. `PreparationInput` is worker input;
  `compute_fill_proposal` returns `PreparedProposal`. The main owner calls
  `stage_commit(dict(proposal.version_values), proposal.samples,
  cluster_id=proposal.cluster_id, expected_generation=proposal.registry_generation,
  exact_target=proposal.exact_target, strict=True)` and `commit_staged(plan)`.
  Failed preparation consumes no registry identity. The fit cap is 4000.
- `objective.compose_cost`: signed weighted raw + positive Gaussian +
  decaying negative affine-dot objective, with explicit immutable affine terms.
- `escape`: approach-continuity direction, direct corridor checks, measured
  radial progress and the existing bounded command law. Optional rectangular
  bounds remain pure geometry; the selected open-field path passes none.
  The unchanged command law can return zero translation at a large heading
  error. That is an interruption of continuous translation, not success.
  Centered verification/design retain the 0.5-second measured-yaw sweep against
  active fill support radii plus a 0.1-metre margin, accounting for reverse
  translation. This guards mathematical fill regions, not physical collisions.
  Blocked guidance cancels the candidate and resumes fresh GESC control; it
  does not introduce stationary acquisition.

The two-block/six-centroid detector, old three-cycle angle-agreement direction
policy, attraction probe, stationary collection, old supervisor state machine,
post-recovery route planner, source synchronization joins and fill wire
transaction protocol are not extracted.

Portable golden values in `test/fixtures/test_v3_numerics_golden.json` were
captured directly from the original owners before removal, with source hashes.
`test/test_v3_numerics.py` checks those values using only active imports and
covers original age, stale worker results, source gaps, duplicate evidence,
registry staging and finite quadrature budgets. This is numerical/source
qualification; it does not qualify Gazebo behavior or physical operation.
