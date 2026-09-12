# Read-only M3 preparation notes — 2026-09-09 UTC

M2 remains the active implementation milestone. These independent source audits
were performed while M2 evaluation was pending. They authorize no M3 edits or
experiment and do not resolve the missing calibrated detector neighborhood.
Reverify line references against current source before implementation.

## Supervisor and motion ownership

- Prefer a bounded supervisor-owned `MovingCandidateEvidence` helper with
  begin-search, add-observation, accept-confirmation, snapshot and invalidation
  operations. Freeze run/stream/frame, authoritative SEARCH epoch, confirmation,
  candidate ID, center, neighborhood and original deadline.
- Support both detector modes under rolling GESC, preserving arm C. The legacy
  eight-value confirmation snapshot needs a binding to the current run/epoch;
  centroid diagnostics supply run, detector-local epoch and confirmation
  sequence. Do not assume local and supervisor epochs are interchangeable.
- M2 direction diagnostics carry synchronized observations, but timer messages
  repeat observation IDs. Deduplicate exact IDs, reject conflicting reuse.
  Maintain three cycles of raw evidence in the supervisor; M2 rolling buffers
  intentionally retain less. Direction-vector confidence must not gate raw
  candidate verification: a weak direction is expected near an extremum.
- Select the latest three phase/time/neighborhood-qualified cycles first, then
  reuse the existing three-minimum median/MAD summary and strict counted ranking.
  The old `RotationCostWindow` selects strongest minima from a larger pool and
  cannot be reused unchanged. Current receipt-time update is near supervisor
  line815; mutable confirmation handling near1015; fill publication near1278.
- V2 evidence insufficiency at the 12 s deadline returns to SEARCH, while
  genuine safety faults retain FAILSAFE. The current state machine's timeout
  near1070 enters FAILSAFE and requires a scoped alternative.
- Controller motion has **three** stop/authorization sites: immediate state
  callback around234, combination around561, and watchdog around601. One opt-in
  predicate must cover all three. The controller remains sole cmd_vel owner.
- Initial V2 DESIGN preparation needs SEARCH-equivalent weights instead of
  inherited (0,1,0); escape redesign keeps its existing objective/command owner.
- `CandidateCostSummary.valid` accepts zero and a known count of one makes the
  terminal comparison vacuous. Freeze an explicit uninformative-source veto
  before ranking so zero/constant-field confinement cannot cause fill/GOAL_HOLD.
- Still to freeze: calibrated neighborhood inputs, cycle trajectory-comparison
  rule, exact epoch binding and information criterion. Synthetic lifecycle
  fixtures cannot satisfy the missing detector research qualification.

## Fill preparation and activation

- Existing `_robust_trigger_cb` performs freeze/estimate/associate/design around
  gaussian_fill_script lines605–914, then commits/publishes around915–976. Split
  pure preparation from commit using existing estimator/designer/registry.
- Pose, source, state and request callbacks share one mutually exclusive group.
  A second executor thread therefore cannot make cancellation responsive during
  current blocking design. Submit one bounded pure worker and return; only the
  existing serialized owner polls completion, validates and publishes/commits.
- Preparation holds immutable snapshot/config/registry inputs and allocates no
  IDs. A cancel tombstone invalidates eventual completion even if computation
  continues. Original deadlines include computation and activation.
- At ACTIVATE, revalidate identity/hash/deadline/current registry generation,
  exact redesign target, state and fresh selected pose/neighborhood. Commit
  without yielding, increment generation once, cache the combined ACTIVATED
  result before publication. Post-commit CANCEL preserves accepted fills.
- `FillRegistry.commit_new/commit_revision` currently increment `_next_id`
  before constructing the version. Prevalidate/prospectively construct before
  mutation and add generation/expected-target checks for V2.
- Existing revision publication sends old supersession then new activation.
  V2 modified cost must consume the combined ACTIVATED envelope atomically;
  canonical legacy lifecycle mirrors follow. PREPARED never appears there.
- Do not substitute `freeze_sample_window`'s receipt-ending eight-second window
  for the immutable three-cycle snapshot. Registry helpers silently decimate
  above4000 samples; V2 must reject excess before invoking them.
- Preserve legacy historical-fill-ID alias resolution; V2 redesign requires
  the exact active fill/cluster/revision. Build new wire frames from the validated
  candidate rather than the existing hardcoded odom value.
- Existing `BasinSample` fits raw cost against synchronized **base XY** and
  requires algorithm-state provenance. Changing to sensor XY changes inherited
  fit semantics. Retain or explicitly bind per-observation state; do not invent
  one state for an entire three-cycle snapshot. Raw-sensor/source-score values
  may remain explicitly unavailable because the estimator uses raw cost.

Paths above are under `ros2_ws/src/ros_esc/ros_esc/`. This audit includes no
source edit, test, ROS/Gazebo operation or field calculation.
