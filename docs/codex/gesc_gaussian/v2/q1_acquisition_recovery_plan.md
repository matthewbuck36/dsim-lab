# Q1 acquisition recovery 1 — 2026-09-09 UTC

Status: ACTIVE bounded infrastructure recovery under the approved simulation-only
implementation scope. This amendment supersedes the dispatch status of
`q1_plan.md`; its scientific method and all earlier failed results are unchanged.

## Closed first acquisition

The first Q1 acquisition version is closed INCOMPLETE. The recorder console
entry point exited with `StopIteration` while resolving
`load_entry_point('ros-esc', 'console_scripts', 'record_run')`. It failed before
creating a run directory, initializing the recorder, or starting Gazebo.
The first reserved case was attempted; the other three were not dispatched.
Cleanup passed with no remaining new nodes or session processes. No trajectory,
bag, source observation, detector result, or confirmation result was obtained.

The original contract, release, checkpoint, console log and acquisition result
remain immutable under `qualification/q1_primary_shadow_v1/` and
`checkpoints/q1_preacquisition_v1/` in the external V2 artifact root.
`validation/q1_acquisition_failure_v1.md` records the exact evidence.
Do not retry that acquisition directory or reuse its run IDs.

## Bounded correction and preflight

1. Diagnose the Python distribution selected by the installed console wrapper
   under the exact released environment. Compare it with the isolated colcon
   overlay without manually shadowing its package path. Preserve diagnostic
   receipts. Correct only the demonstrated packaging/environment cause.
2. Verify the actual installed `record_run --help` exits successfully before
   any simulator is dispatched. Verify installed console entry-point resolution
   for every selected Python node without calling node entry points. Existing
   frontend, source, typed interface and asset checks remain prerequisites.
3. Give acquisition its own explicit version, separate from the unchanged
   scientific contract `q1-primary-shadow-v1`. Freeze recovery identity
   `q1-primary-shadow-v1-recovery1`, new exclusive artifact root
   `qualification/q1_primary_shadow_v1_recovery1/`, and new run IDs containing
   that recovery identity. Reuse the existing runner's `runs_root` override;
   keep the original saved scenario and all numerical/control owners.
4. Bind the actual selected entry-point metadata and corrected environment in
   the new contract/release. Reject mismatches before output creation or ROS
   dispatch. Test root/identity/environment rejection and actual runner dry-run
   command equivalence, then checkpoint before release.

## Population and evidence limits

Preserve exactly the four starts, seeds26090911–26090914, discovery/confirmation
partitions, visibility,125 simulated seconds after readiness,240s process and
1200s suite limits. The same seeds are justified only because the original
recorder failed before any simulated exposure; they are not replacement samples
chosen from observed trajectories. This is a new acquisition attempt, not a
successful rerun of the closed version. The old scientific method/version
identifies unchanged labels, finite grid and reference rules; every new outcome
also binds the new acquisition contract hash and run IDs.

Do not alter timing, tuning, labels, geometry, thresholds, source validity,
cleanup or safety gates to obtain a run. Stop later dispatch on the first
infrastructure/safety/input failure. Preserve any fresh failed attempt before
considering a further separately justified correction. Confirmation remains
sealed until a passing frozen discovery nomination. The M4 pilot remains
unreleased; infrastructure recovery establishes no scientific acceptance.

## Completion

Record exact correction and checks, dispatch receipt/checkpoint, each acquisition
outcome and any analysis allowed by the unchanged Q1 gates. Close recovery with
a handoff and current Git state. Full V2 implementation remains active until
the original pilot and acceptance audit are completed.
