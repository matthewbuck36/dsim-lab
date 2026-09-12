# R4 stationary recurrent pairing and integrated handoff

Verified 2026-09-10. The missing recurrent/stationary Arm B now has working
source, a successful visible simulation, and complete native analysis. The
user's success criterion is arrival within the existing evaluator-only 0.5 m
global-source region; GOAL_HOLD and a second ranking are optional. The full
four-arm 16-run comparison remains open. No experiment is currently running.

## Completed boundary

The existing detector, stationary supervisor/fill adapters, recorder, validator,
analyzer and scenario runner support `recurrent_geometry_v3` with `stationary_v1`.
The separate `StationaryRecurrentFillRequest` carries the full recurrent
diagnostic; historical centroid messages and topics remain selectable. Original
receipt leases, frozen samples, source/clock guards, shared Gaussian fitting,
revocation and controller ownership remain effective. Numerical methods did
not change. See [pairing validation](validation/r4_stationary_recurrent_pairing.md)
and [runner validation](validation/r4_stationary_recurrent_runner.md).

Visible `v2_method_development_B_20260910_02` confirmed a local circle at 102.1 s,
completed three stationary verification rotations, requested a fill at 111.2 s,
activated one fill at 111.3 s, escaped with assistance, restored SEARCH at
131.8 s, and reached the global region at **172.634 simulated seconds** /
**0.499270 m**. Live and retained arrival poses agree. All required predicates,
recording completeness and strict owned cleanup pass; all 284 acquisition pins
remained stable. Acquisition session43518 is terminal/reaped after219.483315 s.

One native analysis completed in **43.390555 s** within120 s, with two native
decoder scans, complete fresh/stored validation, a valid stationary recurrent
pipeline and zero join errors. All124 source/input pins remained stable, with
no production analysis-owner changes since acquisition. Session24153 is
terminal/reaped, exit0. Twenty-nine artifacts include the confirmation/request/
outcome/timing tables and nine native plots. Cached CSV measurements confirm
zero commanded vehicle motion during stationary VERIFY and DESIGN. The
trajectory plot was visually inspected. Exact commands, measurements, hashes
and limitations: [integrated validation](validation/r4_stationary_integrated_02.md).

External evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_02/`.
Read `attempt_result.json`, `analysis_v1/receipt.json`,
`analysis_v1/analyzer/summary_metrics.json`, and
`stationary_motion_assessment.json`; no bag decode is needed for recovery.

Attempt01 remains INCOMPLETE before Gazebo/recording/motion. Its source-root
PYTHONPATH prepend selected stale source egg-info with seven entry points.
All260 pins stayed stable and cleanup passed; no bag exists. Preserve its
environment and [failure](validation/r4_stationary_integrated_01.md).

## Required runtime environment

Use the separate, verified runtime environment:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh`.
Invoke through `env -u PYTHONPATH bash --noprofile --norc` and source that file.
It preserves the Q5 installation's21 callable entry points and canonical source
symlink, then overlays the new interfaces (stationary recurrent request and
schema2 centered guidance). Actual scenario/recorder help passed before02.
The pairing directory's original `environment.sh` is a retained test environment
that fails installed console-script dispatch; do not use it for acquisition.
Do not rewrite source egg-info or substitute the older centered-only overlay.

## Next declared milestone

Save and implement a distinct prospective comparison contract through existing
owners. Do not dispatch a full matrix from this handoff alone.

1. Preserve four arms: A PDE/stationary, B recurrent/stationary, C PDE/rolling
   with centered verification, D recurrent/rolling with centered verification.
   C/D share the continuous package; A/C compares a package, not averaging alone.
   Add a new version in `m4_scenario.py` and its schema/contract/reservation
   paths; preserve frozen M4v1–v9 methods, budgets and identities.
2. Extend `m4_pilot.science_aliases` for recurrent diagnostics, stationary
   recurrent requests and centered guidance. Update `evaluate_m4.py` selected
   confirmation inputs and stationary authority. Report actual arrival time
   separately from GOAL_REACHED; local recovery and safety remain required.
3. Extend the existing continuous-motion metric with exact state, guidance,
   command and measured-motion coverage. Retain zero publications and reasons.
   Same-stamp zero pulses and missing ordinary-GESC per-heartbeat diagnostics
   must not automatically erase demonstrated moving acquisition.
4. Add an explicit new-version development release policy. Current historical
   `m4_workflow.release_holdouts` accepts complete acquisition/outcome ledgers
   even when `analyze_block` reports `scientific_analysis_complete=False` after
   a clean analysis timeout. Preserve the V9 behavior and its regression test;
   require usable completed four-arm science for the new version.
5. Successful `evaluate_m4.summary_stage` currently omits explicit scientific
   completion and can summarize missing reference files. Derive completion
   from actual selected inputs, not merely the outer job's clean termination.
   Require four COMPLETE acquisitions with cleanup/identity checks, completed
   labels, both C/D references and summary within prospective caps, four valid
   selected authorities/label results, all24 scheduled reference targets per
   moving arm with explicit eligibility/exposure, and intact nested receipts
   and late hashes. Require credible integrated local-fill/escape/SEARCH/arrival
   development evidence before releasing the twelve confirmation slots.
6. Complete behavioral failures, short residence, censored latency and
   unexposed reference targets are valid comparison results. Missing inputs,
   invalid authority, timeouts, changed source/receipts or incomplete cleanup
   block release. Do not require every baseline to succeed or every metric to
   have an observed endpoint. Preserve the original30% paired-latency target as
   unestablished when paired endpoints are absent; define any new estimand
   prospectively.
7. Adopt new analysis budgets prospectively from retained timing evidence. The
   old four-bag120 s labels benchmark remains failed. Single-run analyses now
   work; the retained profile estimated169–186 s for that old full block and
   suggested a future240 s cap, which this handoff does not adopt. Propagate
   any new cap through science budgets, reservation and the suite envelope.
8. Freeze before confirmation and describe exposure honestly. All prior
   V1–V9, R1/R2, D02/D03 and B02 data are development; fresh seeds do not make
   previously examined geometry unseen. First obtain usable analysis of the
   new four-run development block, then consider the twelve confirmation runs.

Focused new-policy checks should accept complete failed/censored behavior and
reject missing references, timeout, invalid selected authority, changed nested
receipts and already-started confirmation slots. Keep historical V9 timeout
release behavior unchanged. This is a coherent source milestone before any
new comparison acquisition.

## Evidence and Git limits

The [R3 handoff](r3_arrival_development_handoff.md) retains D02/D03 moving
verification, arrival and paired direction-reference measurements. Its Arm B
implementation and environment next steps are superseded here. Frozen detector
confirmation remains36/36 positives and0/48 negative confirmations, with12 gray
histories; finite controls are not arbitrary-field robustness. The historical
30% detector-latency claim and broader direction reliability remain open.

Branch `feature/gesc-gaussian-robustness-v2`, HEAD
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`; task source remains uncommitted.
No commit, push, physical robot, Pi, snapshot or V1 action was performed.
The material source archive is recorded in current `status.md` after the
context/checkpoint/diff checks; preserve all earlier archives and failed runs.
