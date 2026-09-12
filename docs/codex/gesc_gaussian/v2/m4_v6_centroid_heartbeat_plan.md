# V6 centroid invalid-status heartbeat source amendment

Status: ADOPTED FOR SIMULATION SOURCE IMPLEMENTATION, 2026-09-10 UTC,
under the active V2 goal and the user's existing authority for recommended
bounded corrections. The separate conditional C/D reconstruction is complete:
all11 windows/70 evaluations retained,147.992578867s/305s. External hold
`builds/m4_v6_raw_evidence_reconstruction_v1/diagnostic_hold_v1.json` SHA256
`6984b2b34791326d551e39c68e3d32a0d83ad618191d2d6857cac69c7ee20f43`.
All623 v5 source pins were verified unchanged at that sealed boundary.

Implement the following independent reporting correction and bounded tests.
This releases neither a detector-parameter/moving-motion change nor a new
preparation or acquisition. Preserve the external draft and all retained
M4v1-v5 failures. M4v5 remains CLOSED_INCOMPLETE. This correction cannot
reclassify D or establish either research target.

## Problem and strict boundary

The selected recorder requires centroid diagnostics throughout the first
readiness-True to first subsequent readiness-False interval. Its unchanged
maximum publication gap is centroid_maximum_gap_sec + centroid_pose_stale_sec,
currently 0.5 + 0.5 = 1.0 simulated second. Invalid diagnostics already count.

Moving V2DetectorBinding admits poses only in authoritative SEARCH. Outside
SEARCH it resets numerical support without publishing a diagnostic. The node
emits a transition invalidation once, then its existing watchdog returns while
inactive; waiting for the first admitted pose and repeated stale states also
have silent paths. This amendment addresses that publication mismatch only.
Exact recorded gap endpoints belong to the approved descriptive extraction.

Do not weaken centroid_stream_errors, shorten the authorized interval, exclude
VERIFY, raise the gap threshold, admit non-SEARCH poses, refresh old source
receipts, change a method threshold, or claim valid history from a heartbeat.
No new node, topic, timer, IDL, recorder, model, or analysis implementation.

## Explicit parameter and existing owners

Add strict ROS boolean centroid_invalid_status_heartbeat_enabled, default False,
owned by ConvergenceDetector in convergence_detector_node_script.py. Absent
and explicit False preserve the old runtime publication and numerical paths.
True is allowed only with an existing CENTROID_METRIC_MODES selection, robust
profile/state gating, and the resolved use_sim_time=True. Reject True on PDE or
resolved non-simulation clocks at startup; do not silently ignore it or rewrite
clock defaults. A malformed boolean is rejected, not converted by truthiness.
No physical source, launch profile, or shared clock-default edit is included.

Source footprint:

1. ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/
   convergence_detector_node_script.py: declaration/admission, selected
   watchdog status publication, last-publication bookkeeping, and selected
   startup configuration evidence. Keep the default-off configuration-event
   payload unchanged; record the enabled policy only when explicitly selected.
2. ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml:
   add one default-false argument and forward it ONLY into the existing
   convergence_detector_node executable stanza. Do not forward a detector-only
   parameter to the supervisor/Gaussian owners merely because their existing
   centroid parameters share names.
3. ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py:
   add the override name to LAUNCH_OVERRIDES; validate with the existing strict
   _boolean helper and require an existing centroid mode for True. This schema
   is simulation-only; runtime and recorder independently reject non-simulation
   use. Preserve all existing topology, readiness and algorithm gates.
4. ros2_ws/src/ros_esc/ros_esc/experiment_recording/record_run.py:
   extend require_selected_algorithm_topics to parse/bind this explicit choice
   and reject incompatible mode/environment before the PDE early return.
   Retain the exact enabled selection in the centroid resolved-topic descriptor
   (algorithm_invalid_status_heartbeat_enabled=True). Reject a contradictory
   previously recorded descriptor rather than relabeling it. Omitted/False
   selection does not add new keys to legacy records. The full validator already
   invokes this same helper; no new validator path or coverage-rule edit is needed.

Later fresh-version selection, after source validation, belongs
in the existing m4_scenario.py builder/contract owner: True for centroid arms B/D
in every block, absent/False for PDE A/C. Both stationary and moving centroid
frontends must support it. m4_workflow.py supplies only the adopted-plan source
pin and existing frozen argv/receipts; run_scenario.py forwards the existing
allowlisted override and needs no new dispatch/cleanup behavior. Exact fresh
version IDs and any separate method amendment are deliberately not chosen here.
Retain v1-v5 generated selectors/settings/evidence and all failures unchanged.

## Selected watchdog algorithm

Reuse the existing steady timer, min(0.10, centroid_pose_stale_sec / 2.0).
Retain existing clock admission, pending drain and one-time invalidation logic.
There is no configurable second cadence or new scheduling owner.

After ordinary health handling, the selected path may emit status when the
detector is inactive, waiting for an admitted state/epoch/pose after a reset,
persistently stale, or not recording-authorized. Healthy SEARCH remains
pose-driven. Existing successful diagnostics suppress redundant heartbeats.
Use bounded scalar bookkeeping for the last successful publication ROS stamp,
steady receipt and status reason as needed; do not maintain a growing queue.

Construct a fresh empty immutable CentroidResult with stamp_ns=None, no support,
no centroids/score/radius, and the current core reset_sequence. Set a truthful
availability reason: outside_search only for an observed non-SEARCH state;
otherwise waiting_for_search/state/pose, stale state/pose, or unavailable rolling
binding as actually observed. Do not invent an unrecorded detailed rejection
reason when the binding only exposes unavailable context/support.

Call the existing _publish_centroid_result with source_ns=None and
source_valid=False. Its empty result produces history_valid=False,
metric_valid=False, confinement_valid=False, eligible=False, confirmed=False,
zero represented support and NaN numerical values. It cannot publish a typed
DetectorConfirmation or legacy convergence event. Keep the source stamp zero
with unavailable validity, and the actual cached original pose receipt or zero
when none exists. Never replace either with the heartbeat publication time.
Use the last actually admitted run/frame/local SEARCH epoch; empty identity and
epoch zero are legitimate unavailable startup status, not invented authority.

Never call core.invalidate, start_epoch or reset merely to send a heartbeat;
never update latest numerical support, reset counters, confirmation counters,
pose/state receipt leases, source frontiers, epoch state or pending queues from
heartbeat construction. Existing callbacks may still perform their legitimate
resets, including rejected non-SEARCH poses. Heartbeats add no further resets.
Never reuse or copy a full/confirmed latest result as the status payload.

Use actual nonnegative ROS publication time. Suppress repeated same-stamp status
while /clock is held; a changed unavailable reason may be reported once. Keep
the existing steady watchdog's bounded rate. On resumed time, publish current
status only; no fabricated catch-up stamps or past samples. A real clock
rollback or jump may still fail existing recording gates and is not repaired
by this feature. Cadence evidence is measured under the fixture/runtime clock
schedule, not promised for arbitrary simulator leaps or scheduler starvation.

## Existing consumer and validator compatibility

centroid_diagnostic_errors permits zero epoch/empty run only when no valid
metric or confirmation is claimed, while still requiring exact metric mode and
selected source-pose topic. Generic timestamp checks audit publication time.
The stationary live adapter and stationary recorded audit ignore
confirmed=False; moving lifecycle joins require confirmed valid diagnostics.
The current coverage owner explicitly includes invalid-history publications.
Exercise these actual consumers/gates; do not implement alternate assertions
that silently exempt heartbeat messages from existing checks.

## Finite source validation

Before editing, retain exact affected source/test copies and manifests under a
fresh external heartbeat source directory. Retain the old-route failing cadence
fixture/log separately. A baseline regression may assert the observed old gap
without pretending it passes the required coverage gate. No old bag replay or
Gazebo acquisition is required.

Adopted bounded commands in clean Humble -> Q2 local_setup -> Q5 local_setup,
with extremum-seeking/src appended afterward, localhost-only and a separately
reserved ROS domain chosen by the root agent:

- One baseline actual-node/DDS gap reproduction: 45 seconds inclusive.
- One focused source/launch/recording/actual-DDS validation bundle: 240 seconds
  inclusive, each DDS fixture at most 30 seconds with bounded spin and cleanup.
- One relevant unchanged regression bundle: 240 seconds inclusive. Include
  centroid method/clock admission/recording, epoch transport, actual frontend
  selection, stationary confirmation consumers and moving confirmation bindings.
- Root's final integrated source gate remains a separately declared single
  bounded command after all implementation owners hold source. Do not repeat
  expensive bundles without a changed source, failure or unresolved concern.

Keep every failure and intermediate source receipt; a finite test timeout is a
failure, not permission to silently rerun. Any required correction gets a new
exclusive log/receipt. No preparation, numeric derivation, label/reference job,
physical work, commit, or acquisition is authorized by these source-test caps.

Meaningful cases, reusing test_v2_epoch_transport.py and
 test_centroid_detector_transport.py patterns in a new focused test file:

1. Actual simulation /clock, Timekeeper, SearchEpochContext, AlgorithmState,
   readiness and selected pose subscriptions/publishers; epoch-zero startup
   and readiness with missing state/pose longer than one simulated second.
2. Real eligible SEARCH support produces exactly one confirmation; VERIFY lasts
   over two simulated seconds with continuing poses. Status coverage satisfies
   the unchanged one-second gate, all heartbeat flags are invalid, and no
   non-SEARCH pose enters the numerical core.
3. Return to a fresh SEARCH epoch, withhold poses for over two seconds, then
   supply complete fresh support. Old windows do not survive and exactly one
   subsequent epoch confirmation is allowed. Include both centroid laws and
   stationary/moving selection as applicable; no numerical estimator is mocked.
4. Persistent stale pose/state/rolling context, future queued pose with its
   original receipt, and paused/resumed clock. Assert heartbeat-only calls add
   no reset/confirmation increments and refresh no leases/frontiers. Compare
   with the same callback schedule when disabled to distinguish existing resets.
5. Existing centroid_diagnostic_errors and centroid_stream_errors consume the
   captured actual wire messages and clock/readiness rows. Confirm full selected
   recording integration accepts status coverage while unrelated missing
   full-run evidence remains explicitly unavailable.
6. Default/False legacy output parity, True-PDE/non-simulation and malformed
   selector rejection, actual XML frontend forwarding, scenario roundtrip and
   contradictory retained-metadata rejection. Removing heartbeat records must
   reproduce the original coverage failure; lowering the gate is forbidden.

Required review points: exact admission policy, accurate unavailable
status reasons, startup/zero-epoch evidence, suppression while clocks are held,
absence of counter/receipt mutations, existing consumer behavior, source scope,
and finite test commands. This source amendment is not research qualification or dispatch
release and does not select a raw-evidence algorithm change.

## Review correction: pure readiness observation

Adopted 2026-09-10 UTC after the first focused/relevant bundles and before
the correction's source edit. Independent review traced the new status calls
through `V2DetectorBinding.centroid_ready()` to `EpochBinding.ready()` and
`EpochBinding.now()`. The latter updates `last_now_ns` and may invoke a rollback
boundary. An empty status must not cause that additional frontier update/reset.
Retain all previous source snapshots and test receipts; they are intermediate.

Extend the source footprint narrowly to the existing
`convergence_detector_node/v2_binding.py` readiness method. Add optional captured
ROS and steady timestamps to `centroid_ready`, retaining its existing no-argument
behavior for every old caller. The new heartbeat and its provably empty
selected publication path pass captured timestamps, so the existing readiness
and original pose-receipt predicate can be reused without calling binding.now.
Do not duplicate binding authority, bypass valid-history publication admission,
or change ordinary callback/watchdog rollback handling. Other owners stay held.

Before editing, finish the live strengthened-cycle test and preserve its
source/test version and receipt. Add a focused state-preservation regression
that checks binding frontier/context, core reset/confirmation state and cached
receipts across heartbeat-only calls, including a captured rollback time.
Keep the independent ordinary rollback test to prove reset behavior still runs
through its existing owner. After this actual production correction, allow one
new exclusive 240-second focused heartbeat bundle and one 120-second relevant
binding/clock/epoch regression bundle. These replace neither old results nor
root's separately declared final integration gate. A failure is retained and
requires a bounded correction; no simulation is released.
