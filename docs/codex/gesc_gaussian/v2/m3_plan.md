# M3 moving verification and fill transactions — 2026-09-09 UTC

Status: COMPLETED within independent source/validation scope under the approved V2 plan.
See `m3_handoff.md` and `validation/m3_validation.md`; scientific gates remain open.
M2's implementation handoff/checkpoint is saved. M1 neighborhood calibration and
M2 same-trajectory research qualification remain unachieved. This milestone
authorizes source, bounded synthetic/ROS tests and recording integration; it
does not release Gazebo or replace the frozen pilot. Legacy/default paths remain.

## Frozen implementation contract

The M0 `validation/interface_audit.md` message/lifecycle proposal applies with
the following explicit clarifications. New lifecycle messages use protocol
schema1, independent of nested acquisition observations' stream schema2.
All common envelopes bind run/stream/origin/frame and authoritative SEARCH epoch.

1. The existing supervisor publishes `SearchEpochContext` on
   `/gesc_gaussian/v2/search_epoch`. It increments a uint64 epoch only on entry
   to SEARCH, including rejection/recovery, and retains its absolute start.
   Its heartbeat includes state, validity, and publication sequence/time.
   The existing detector publishes `DetectorConfirmation` on
   `/gesc_gaussian/v2/detector_confirmation` for either metric in continuous mode.
   It echoes fresh authoritative context and includes metric, local diagnostic
   epoch/sequence, absolute history/source bounds, center, and explicit metric
   validity. Arm C keeps the immutable eight-value legacy snapshot and existing
   decision algorithm. Arm D keeps the timed centroid metric. The supervisor
   accepts once per epoch, only matching fresh confirmations whose complete
   source history starts at/after epoch start. Local epochs are diagnostic only.
2. A bounded supervisor helper retains actual M2 synchronized observations and
   the first valid filter-output state/stamp accompanying each observation.
   This is publication-state provenance, not acquisition-state knowledge.
   Repeat diagnostics cannot refresh receipts or overwrite provenance; conflicting
   reuse or explicit source revocation invalidates affected candidate evidence.
   Raw verification never gates on augmented direction confidence/magnitude.
3. Freeze candidate ID, epoch, center, radius R, centroid tolerance epsilon,
   confirmation source time, accepted time and original12s verification deadline.
   R/epsilon must be explicit positive finite inputs for continuous mode; default
   zero means unconfigured and refuses startup. Tests declare synthetic values;
   no value is promoted to calibrated merely by passing those tests.
4. Use latest3 complete individually qualified nonoverlapping revolutions,
   including pretrigger support after epoch start. Reuse M2's actual world-phase
   shortest-angle unwrapping, first-arrival interpolated boundaries, reversal
   reset, maximum0.5s gap/30s cycle and12sectors with2actual observations each.
   Interpolated points support integration only, never raw minima or counts.
   Every represented base-position vertex stays within R; each time-weighted
   cycle centroid stays within epsilon of frozen center. Retain at most20000
   observations; final snapshot at most4000 actual observations, reject excess
   without sorting conflicts away or decimation. Supply boundary brackets and
   integer revolution bounds, half-open actual-sample indices. Shared support
   is stored once; each actual raw sample is assigned to at most one cycle.
5. Compare trajectory coverage using12 time-weighted base-position centroids
   per absolute world-phase sector. Every corresponding centroid in the3cycle
   pairs must be within epsilon. Select the latest qualified triplet before
   this comparison; never search older triplets for a favorable cost outcome.
   This conservative operational rule does not prove identical spatial sampling.
6. Take one minimum from actual raw observations per selected revolution; pass
   exactly3 minima to existing `summarize_minima`. Preserve negative-cost units,
   median/MAD spread and strict counted-candidate interval ranking. Compare
   repeated neighborhood observations, not exact centroid cost or statistical
   confidence intervals. Before either fill or GOAL, require informative raw
   profiles:12 raw sector medians per cycle, demean each cycle; A is RMS of
   mean profile and D RMS of cross-cycle profile differences. Require
   A > max(3D, delta), delta=max(1e-6 raw-cost units,64*max raw-value ULP), and
   negative raw baseline and candidate upper bound below -delta. Constant/zero
   and declared incoherent-noise fixtures fail. Phase-locked noise can resemble
   signal and constant-response extrema remain uninformative; no universal
   source/noise classification claim. This floor is a numerical development
   guard, not physical calibration or a changed objective normalization.
7. Missing/incomparable/uninformative evidence may wait for newer cycles only
   until original deadline, then SEARCH/new epoch without a stopped sweep.
   Departure/identity/revocation cancels immediately; safety retains FAILSAFE.
   Freeze the successful full snapshot before PREPARE. Later observations cannot
   rewrite it. Initial DESIGN keeps SEARCH-equivalent weights.
8. Existing Gaussian owner performs one bounded pure preparation worker using
   detached snapshot/config/registry inputs and existing estimator/designer.
   No worker publication, ID allocation, live-buffer reads or registry mutation.
   Owner callbacks remain serialized and responsive; completion is polled.
   Exact command IDs/sequences/hashes/deadline/generation and target revision
   bind PREPARE, ACTIVATE and CANCEL. At most one uncommitted preparation;
   at most4096 distinct command identities per run, then reject further commands
   without dropping tombstones. Identical retries return immutable outcomes.
9. Registry staging preconstructs all immutable versions/maps/retained support
   without consuming IDs. Immediately before serialized commit recheck matching
   state/epoch, candidate, hashes, original deadline, exact registry target and
   own fresh selected pose (source+receipt <=0.5s) inside frozen neighborhood.
   Commit has no yield and increments generation once; cache ACTIVATED before
   publishing. CANCEL before commit is terminal; after commit it returns
   ALREADY_ACTIVATED and preserves accepted fill. PREPARED allocates no IDs and
   never appears on canonical lifecycle topic. Final snapshots reject conflicting
   timestamps/excess support before legacy retention helpers can normalize them.
10. Combined ACTIVATED contains new and optional superseded fill, before/after
    active-registry digests and result hash. Existing modified-cost owner validates
    both and atomically replaces Gaussian/affine maps, rejecting skipped generation
    or digest mismatch. In continuous mode canonical fill mirrors are observational,
    not activation authority. Publish mirrors after owner commit. Supervisor waits
    for existing objective/direction registry-digest acknowledgement before escape
    authorization. Count each accepted commit once even if its motion epoch ended;
    a delayed accepted result may update the ledger but cannot return the robot.
11. Redesign fixes exact active target and retains old fill, escape owner,
    direction and original timeout during preparation. Initial DESIGN is identified
    by valid previous_state=VERIFY; redesign by previous_state=ESCAPE_REPULSE.
    Failed/cancelled redesign retains bounded escape; accepted revision returns
    ASSIST only if exit has not completed. Preserve selectable legacy redesign.
12. Existing controller uses one motion-authorized predicate at immediate state
    callback, combiner and watchdog. Opt-in fresh selected-run VERIFY/initial
    DESIGN returns GESC alone, so delayed escape/recenter commands cannot leak.
    Redesign follows its escape policy. Preserve saturation, receipt/source
    freshness, recorder wall-clock interlock, GOAL/FAILSAFE and final-zero routes.

## Interfaces and ownership

Root owns common IDL/hash/validation helpers, detector epoch binding, launch/
runner/recorder/analyzer integration. Supervisor helper/state machine/node belong
to the supervisor task. Gaussian preparation/registry and atomic composer belong
to the fill task. Controller and focused motion tests belong to the controller
task. Existing source/filter M2 code changes require evidence of an integration
defect, not speculative refactoring. No new node, recorder or control publisher.

`CandidateSnapshot` additionally contains metric mode, legacy score/validity,
per-observation first filter state/stamp, information amplitude/disagreement/floor
and validity. `FillResult` adds before/after registry digests and committed hash.
Exact wire definitions are the common API and must be reviewed before consumers.
Canonical hashes use sorted compact finite JSON and integer nanoseconds; omit
own digest and outer publication stamp, retain actual source/admission/receipt
evidence. Unknown optional metrics are null in hashes with explicit wire flags.

## Validation and completion boundary

- Pure evidence: pretrigger reuse, cadence changes, boundaries/phase wraps,
  reversals, large loops/drift, comparable versus shifted sector trajectories,
  zero/constant/noise, negative ranking/known-count1, caps, stale/old epochs,
  duplicate conflicts, source revocations and all deadlines.
- Transaction/registry: inactive preparation, generation/target/hash mismatch,
  cancel before/during/after worker, departure/safety/deadline races, identical
  retries/conflicting ID reuse, atomic supersession, no ID consumption on failure,
  accepted result after exit, retained old fills and original escape time.
- Controller: all3 gates, both modes/design purposes, stale selected run/state,
  delayed Twist, recorder readiness/staleness, GOAL/FAILSAFE, saturation and
  process-level SIGINT final zero, with bounded isolated ROS domains.
- Build interfaces; real DDS lifecycle transport through actual existing owners;
  focused legacy/M1/M2 regressions and recorder/runner integration checks.
- Record exact commands, retained failed attempts, outcomes and hashes in
  `validation/m3_validation.md`; update acceptance ledger/status, inspect diff,
  checkpoint and write M3 handoff. Synthetic correctness cannot qualify detector
  neighborhoods, angular performance, natural trajectories or pilot readiness.

## Arm C provenance correction before owner edits

The inherited PDE node publishes absolute node-clock timestamps, not relative
Timekeeper times; its values are a transport-filter state, not exact trajectory
samples with nominal grid timestamps. Merely echoing detector context cannot
bind an old delayed buffer to the current epoch. Therefore the existing PDE
owner also receives opt-in authoritative epoch context and the shared identity.
It resets the inherited buffer on the first admitted post-epoch finite selected
pose, preserves the existing numerical update and adds `PdeHistoryEvidence` on
`/gesc_gaussian/v2/pde_history_evidence`: exact legacy payload plus hash, epoch,
first/latest actual admitted pose source bounds and original latest receipt.
The continuous-mode legacy detector consumes that wrapper; the canonical array
continues as a compatibility mirror. Default PDE behavior remains unchanged.
No nominal PDE-bin source times are invented. DetectorConfirmation explicitly
names `history_kind=pde_input_support` and `source_stamp_kind=pose_input` for
arm C, versus `centroid_windows`/`pose_input` for arm D. Matching context and
actual input-support bounds provide epoch binding; neither claims that the PDE
filter is a finite exact-time-window statistic. Future source stamps wait for
clock coverage within0.5s original receipt/source age and1024 pending inputs.

Verification's12s deadline ends at classification. Initial PREPARE receives the
separate inherited DESIGN-entry + `fill_design_timeout_sec` deadline (default5s).
Redesign uses a new preparation ID and snapshot revision of the original
candidate association, exact active target, and qualifying latest3cycles frozen
at redesign entry. Missing evidence abandons redesign into its bounded escape
policy; there is no additional12s acquisition. Redesign expiry is the earlier
of DESIGN-entry + design timeout and original escape-start + escape maximum.
Preparation completion never extends either deadline or restarts escape time.

## Integration clarifications from bounded source review

- D uses all3 unordered cycle pairs'12 demeaned-profile differences (36 values).
- Snapshot boundary brackets retain original raw evidence for interpolation
  and hashing. Only the union of half-open revolution sample-index ranges
  enters raw minima and the Gaussian estimator. An actual bracket outside the
  selected time intervals need not lie inside R; the represented interpolated
  boundary and all actual points assigned to each cycle must. This prevents
  out-of-window raw costs from changing fit geometry or amplitude.
- PDE gap/conflict reset emits an explicit invalid typed wrapper retaining
  actual prior support under `valid=false`; its nested header names the reason,
  with no new canonical numerical history. The detector clears persistence;
  duplicate old valid wrappers cannot restore it. This is a runtime rejection,
  not qualified candidate evidence.
- Normal selected pose headers can lead the held10Hz Gazebo clock. Supervisor
  and Gaussian activation guards retain the latest already admitted fresh pose
  while buffering bounded future support with original ROS/steady receipts.
  Neither future inputs nor duplicate packets refresh authorization age.
- The Gaussian owner binds the first actual Timekeeper origin independently.
  Same-stamp AlgorithmState transitions can legitimately occur within one clock
  tick; preserve that stamp's original first receipts across such transitions,
  require fresh matching context/purpose, and cancel immediately on terminal
  states. Actual source regressions invalidate authorization.
- Supervisor honors the existing `recording_ready_required` selector (default
  false), shared topic and stale interval. When required by the selected recorder
  run, its own readiness lease gates confirmation/activation and cancels on
  false/stale input; standalone legacy/default selection remains intact.
- Publish each successful immutable `CandidateSnapshot` once per candidate/
  revision from the existing supervisor on
  `/gesc_gaussian/v2/candidate_snapshots`, before classification. This retains
  the exact raw/information/phase evidence for verified GOAL/no-fill decisions
  as well as fills. PREPARE embeds that same snapshot; redesign publishes its
  new immutable revision. The recorder registers the event stream with zero
  minimum occurrences, since constant/uninformative fields may have none.
- Per-observation state/stamp binds the first valid filter diagnostic received
  by the supervisor. Different DDS subscribers can join or receive differently;
  the recorder cannot equate its first globally recorded diagnostic with the
  supervisor's first callback. Validate an exact recorded observation/state/stamp
  match and consistent binding across snapshot revisions. Runtime caches retain
  the first received metadata without refreshing it on repeats. This is an
  explicit limit of bag evidence, not invented acquisition-state knowledge.
- Rolling centroid pose admission also buffers source stamps ahead of a held
  clock (at most1024 pending,0.5s original ROS/steady receipt age). It preserves
  the selected frame, detaches inputs, retains source-order/tombstones, and
  admits only after clock coverage. Standalone centroid admission is unchanged.
  Centroid diagnostics retain the original receipt; in this selected mode it
  may precede source time, while both must precede actual publication and stay
  within0.5s. No fabricated admission stamp replaces that receipt.
- An authenticated PDE revocation advances the history sequence watermark;
  unseen older valid histories cannot revive pre-revocation persistence.

- Arm C also distinguishes sender publication from receiver clock coverage.
  Matching future PDE wrappers wait in a1024-entry queue, retaining original
  receiver ROS/steady receipts within0.5s. Sequence fences/tombstones cover
  pending/expired/conflicted/revoked inputs; a revocation cannot grant authority
  and immediately fences older support. Actual history/dwell admission waits
  for local clock and matching authoritative context coverage. Original sender
  receipts can precede experiment origin, but source support cannot precede
  epoch start; both sender and receiver receipt freshness remain bounded.
