# Physical V3 deployment handoff — 2026-09-29

**Continuation point, updated 2026-10-01:** read
[physical fresh-chat handoff](physical_fresh_chat_handoff.md) first. It includes
the post-steering-fix floor run and the user's physical-first experiment
priorities. The dated sections below preserve their original evidence limits;
the latest sections of [status](physical_deployment_status.md) supersede earlier
claims that no post-fix floor observation exists.

## Initial deployment outcome and qualification

Deployment into the original `/home/pi/ros2_ws` is complete. Native software,
legacy compatibility, ordinary build/source/install selection, backups and
source parity passed. The operator confirmed wheels raised, arm clear and active
observation, then confirmed that wheels and arm stopped in all six checks:
normal Ctrl+C; controller crash and freeze; acquisition freeze; local guard
crash and freeze. No floor trial or physical Gaussian fill/escape/global
approach occurred. Precise actuator stopping latency was not instrumented.

Read [deployment status](physical_deployment_status.md) for exact results and
[physical usage](../../../esc_physical_v3.md) for the operator command. The
[accepted plan](physical_deployment_plan.md) owns scope and remaining promotion.

## Selected installation

- Original Pi workspace, ordinary copied installations. The new 12-line Bash
  runner builds the three packages, sources installation, then launches V3.
- Physical acquisition/rotation/bringup remain in `turtlebot3_vehicle_nodes`
  outside dsim-lab. One shared V3 controller owns velocity commands; one private
  numerical worker does optional expensive calculations.
- Gains 0.5/5; physical caps 0.05 m/s and 0.30 rad/s after the user-authorized
  first floor-run review (initial deployment/Gazebo: 0.10/0.50); affine magnitude 2.0. Direct
  assistance off; `--assist` selects the optional 15-second stall window and
  one nominal 20 cm measured-path pulse per escape.
- Original fixed 5 Hz UNO firmware untouched; nominal arm 20 RPM, original
  54-degree calibration once. Complete-line host receipt is honest timing;
  unknown ADC conversion uncertainty is not fabricated.
- System time, OpenCR `/odom`, no Vicon control input. Optional ordinary rosbag,
  no physical plot/duplicate CSV/recorder gate. No SSH/session-loss monitor.
- Bad data does not renew freshness. Essential input expiry commands temporary
  zero and resumes when usable input returns. Committed escape geometry and
  original affine decay survive ordinary same-frame/time data gaps; stale
  pending fit/direction/progress evidence does not. True ownership/frame/time
  and actuator/process failures stop the run.
- No approach, verification, escape, goal-hold or overall operator-run deadline.
  The finite raised-wheel harness bounds were test bounds only.

## Evidence

External evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v3/physical_deployment_20260929T210229Z`.

- `raised_wheels/normal_ctrlc_02/REVIEW.md`: 46/46 valid observations, 4.9724 Hz,
  observed arm 17.95 RPM, about 9.136 seconds uninterrupted nonzero commands,
  final zero and STOPPED/SEARCH; no fill/escape. Raised-wheel wheel odometry is
  not physical translation. Bag, plots, timing metrics and copy hashes retained.
- `raised_wheels/FAULT_CHECKS.md`: five injected process-fault cases with
  observer JSONL, exact identities/signals, software receipts and separate
  operator confirmations. Driver process exit was observed about 0.05 seconds
  after crashes and 1.01–1.03 seconds after freezes, not measured wheel latency.
- `pi_receipts/final_post_hardware_audit.json`: all 393 source hashes/modes
  match; no control processes; serial ports unowned; servo output 1500 us.
  pigpiod remains running. A killed guard can leave an inert HALTED script slot.
- Pi native: 222 retained legacy tests and 170 V3 tests passed; after review,
  5 terminal-fault tests plus 17 real ROS/control/closed-bag tests passed.
  Final shared suite: 297 passed. Installed 117 Python runtime files and
  12 physical interfaces match. All 26 legacy Bash methods and the probed
  original numerical/configuration results remain unchanged.
- The first raised-wheel attempt failed before device startup because the
  daemon path was wrong. Corrected to the existing permitted
  `/usr/local/bin/pigpiod`, rebuilt and reverified. `normal_ctrlc_01.log` remains
  failed startup evidence. No privilege policy changed.
- Expected interrupted-worker/process tracebacks and queue-resource warnings
  during forced stops are retained. They did not leave active control processes.
- `source_archive_closeout.json`: final archive and 393-file manifest verified
  on host, Pi backup and offline backup. Initial candidate and review patch,
  previous final archive, failed checks and all earlier V2 evidence preserved.

## Preservation and restoration

Pi backup:
`/home/pi/mbuck_backups/gesc_v3_deployment_20260929T210229Z`.

Complete original source/build/install are in `prior_workspace/` and the
verified `before_workspace.tar`; the original editable numerical dependency is
also archived. `RESTORE.md` describes whole-workspace restoration. The old
V1-only symlink-building wrapper is retained in backup; its active file gives
an informational notice and exits. V3 has an explicit separate command until
physical acceptance. Legacy methods keep their original code and Bash scripts.

Pre-deployment V1 archive SHA256:
`9b2297fdaeaef9958f7f6fa99cc15098ebc6979e8fa8f0a771ed79dee3985691`.

Final V3 source archive SHA256:
`12b3f235466e133141756489a34b1c9385f3bdcb75a48c4455d19d0bf876d1e8`.

Offline physical source under
`/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src` matches the final
manifest. Its previous source and old root guidance are preserved in the
mirror's deployment backup. Firmware, ROS underlays, original numerical
library and user-managed Pi clock were not changed. Pi clock still reads
August 13 while the host deployment date is September 29; do not confuse its
run-directory dates with the host evidence identifier.

## Next boundary

The explicit V3 command is ready for an operator-controlled floor trial with
continuous motion and Ctrl+C judged by the operator near the global source.
That trial must establish moving verification, Gaussian fill, local escape,
global approach and long-run timing/CPU behavior. Actual recovery during a
physical sensor interruption has not been deliberately exercised. Kernel,
pigpiod or electrical failures were not qualified by the process tests.
Promote V3 to the generic Gaussian command only after physical acceptance;
do not delete V1 backups or legacy dependency closure during commissioning.

Shared source/tests/docs remain as intentional uncommitted changes on
`refactor/esc-v3`, starting at `a702cd2ed5df300379c5c62629562d466957a155`.
No commit or push was made. Frozen V1/V2/archive refs remain unchanged.

## Vicon follow-up — 2026-09-29 local / 2026-09-30 UTC

After the initial handoff the user began floor trials and reported the Vicon
server still waiting. Those floor runs were not analyzed during this correction.
The V3 launcher had omitted the passive client and recording topic. The user
authorized restoring both, with unavailable Vicon never blocking control.
The existing client is now enabled by default on
`/gesc_gaussian/evaluation/vicon_odom`; OpenCR `/odom` remains the control input.
Use the same V3 command; `--no-vicon` optionally disables the client. Restart
the lab UDP server before the next run because it retains one client per launch.
See [physical usage](../../../esc_physical_v3.md) and the latest status.

The source patch and pre-change files are preserved at
`/home/pi/mbuck_backups/vicon_restore_20260930T032350Z` and in the matching host
evidence directory. The preceding 393-file deployment archive remains the
historical pre-Vicon checkpoint; the new manifest records the four changed
V3 source/test files. The original legacy client, scripts, algorithm, firmware,
tuning and earlier backups remain unchanged.

## Worker follow-up — 2026-09-30

After seven SEARCH-only floor runs, recorded-input and isolated Pi probes
reproduced a cold SciPy import consuming each first coherence job's deadline.
The authorized fix now loads numerical dependencies before worker readiness;
control remains available on fresh instantaneous inputs during initialization.
Job deadlines and original data-age limits are unchanged. The corrected shared
worker is installed in the original Pi workspace and mirrored offline.

An initially stale incremental installation was caught by the new regression.
Preserved generated `ros_esc` directories and a fresh ordinary package build
resolved it. Pi native101 tests pass. Real-time recorded5Hz replay now completes
46 numerical jobs without error or restart and uses averaged steering, compared
with zero completed jobs before. See the latest
[status](physical_deployment_status.md) and
[review](/home/mattb/Experiments/GESC-Gaussian/v3/worker_init_20260930T215232Z/REVIEW.md).

Current physical caps are0.05/0.30; affine2, assist off, fixed5Hz, nominal20RPM
and54-degree calibration remain selected. Earlier initial-deployment caps and
clock observations above are historical; the user adjusted the Pi clock during
this task. Only one of393 physical source files changed; all legacy sources and
V1 backups remain intact. No hardware test followed this software correction,
so physical convergence, fill and escape remain open.


## Steering follow-up — 2026-09-30 local / 2026-10-01 UTC

The subsequent one-light review reproduced a distinct pending-coherence
handoff defect and an artificial initial washout direction. The authorized
corrections are now installed: preserve an accepted snapshot only within its
original freshness/context during replacement work; prime initial washout from
the first cost, without sleeps or zeroing at moving objective transitions.
Host305/Pi114 checks passed. Installed real-time replay reduced150 blend-mode
switches to0, with95 completed jobs/no errors and final zero; the next changing
sample starts control after priming. Physical behavior is still untested.

Exactly2 of393 physical source files changed; installed/mirror parity verified,
legacy/V1 preserved. Fresh ordinary build and the usual Bash check-only passed.
Caps0.05/0.30 and all other selected physical settings remain unchanged. Source,
old generated package output and validation receipts are retained under
`~/mbuck_backups/steering_handoff_20261001T040328Z`; see the latest
[status](physical_deployment_status.md) and its linked review. Use the same V3
operator command. The next floor observation must assess the startup hook and
arc; these software checks do not establish convergence or Gaussian escape.
