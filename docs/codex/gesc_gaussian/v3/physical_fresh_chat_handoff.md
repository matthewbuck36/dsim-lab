# Physical GESC + Gaussian V3 — continuation handoff

Updated 2026-10-01 local time. Start in `/home/mattb/dsim-lab`. This is the
current continuation summary; follow the linked evidence instead of rebuilding
context from every historical phase. No Pi operation was performed while
preparing this handoff. Remote state below is **last verified**, not a claim
that the robot is currently online, idle or unchanged.

## Read next

- [Physical usage and operator command](../../../esc_physical_v3.md).
- [Deployment plan](physical_deployment_plan.md) and the latest sections of
  [live status](physical_deployment_status.md).
- [Environment parameters](../../../environment_parameters.md) and
  [Pi guide](../../../environment_guides/tb3_pi_README.md) /
  [Pi instructions](../../../environment_guides/tb3_pi_AGENTS.md).
- [Latest physical-run review](/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/post_steering_review_20261001T215339Z/REVIEW.md)
  and its [diagnostic plot](/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/post_steering_review_20261001T215339Z/run_diagnostics.png).

Read current source/configuration, Git diff and fresh remote inspection before
implementation. Old phase tools do not support V3; use plan/status/diff/receipts.

## User's current priorities

The user now wants **physical-led refinement**, without Gazebo as a prerequisite
for the next experiment. Favor reliable function and simple code over fast
completion or added orchestration. Continuous base motion remains a core
requirement, subject to essential input/process protections. The operator
watches floor trials and stops with Ctrl+C; a 20–30 cm global-source orbit is
acceptable. The comment that escape should not take ten minutes is a performance
expectation, **not authorization for a new run-ending timer**.

Ordinary recoverable data/research problems should not permanently end a run.
Keep the existing narrow stopping protections; do not restore a research
supervisor, recorder gate, SSH-loss monitor or additional convenience layers.
The user accepted the worker-initialization and averaging-handoff corrections
as justified bug fixes. Do not undo them merely to reduce line count.

The lab is cluttered/cramped, limiting floor tests. The user plans to contact
Student Services about a separate room and reports that larger Student Union
rooms can be reserved free of charge; no reservation has been made by the
assistant. The latest tests used one battery camping light whose brightness
the user reports declined over time. This is a plausible signal confounder,
not an isolated measurement of its contribution to the trajectory.

## Last verified installation and settings

- Pi `pi@192.168.1.36` / `tb3-6`, original `/home/pi/ros2_ws`; no new V3 workspace.
  Ordinary copied installations. The V3 Bash runner builds, sources and launches.
- Physical adapters stay in Pi/offline `turtlebot3_vehicle_nodes`, outside this
  simulation checkout. Shared algorithm source remains in `ros_esc`; avoid
  creating a second algorithm fork. Keep physical and Gazebo tuning distinct.
- Physical forward/angular gains **0.5 / 5.0**, speed caps **0.05 m/s / 0.30 rad/s**.
  Gazebo retains **0.10 / 0.50**. Affine magnitude **2.0**.
- Fixed **5 Hz** original UNO application, nominal arm **20 RPM**, encoder
  calibration **54 degrees** once. Older 354-degree and optional10/15Hz
  requirements are superseded. Actual arm speed in the latest run was17.07RPM.
- Direct escape assistance **off**. Optional assistance remains a single20cm
  measured-path pulse after less than5cm outward progress over15s. No approach,
  verification, escape or overall operator-run deadline.
- Physical system time and OpenCR `/odom` control pose. Optional Vicon is
  evaluation-only; its absence cannot gate control. Restart the legacy lab UDP
  server before each run because its client greeting/server lifetime is one-shot.
- All legacy methods remain preserved. V1 is backed up under
  `/home/pi/mbuck_backups/gesc_v3_deployment_20260929T210229Z`; do not delete or
  promote V3 as the generic Gaussian default before physical acceptance.

SSH uses `/home/mattb/.ssh/id_ed25519_tb3`, BatchMode=yes,
StrictHostKeyChecking=yes, IdentitiesOnly=yes and a bounded connection timeout.
Direct read-only SSH has been authorized. Check live processes before changes;
successful SSH is not authorization to move the robot. The operator controls
physical readiness. Do not inspect an actively written bag.

The offline mirror is `/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src`.
`/home/mattb/tb3-pi` is only a mount point: verify exact `findmnt --mountpoint`
before treating it as robot source. Do not mount it as a recovery side effect.
The user manages the Pi clock; UTC-labelled Pi run times have differed from
host UTC. Preserve clock provenance rather than changing the date automatically.

## Progress and installed corrections

V2 physical commissioning failed to qualify amid distinct sampling, timing,
synchronization and installation problems. Working physical V1 was restored
wholesale from the pre-V2 archive; its source/firmware/evidence remain backed up.
V3 then simplified the research runtime into one controller and one optional
numerical worker, with independent rosbag/Vicon evaluation. Selected Gazebo
trials achieved fill, unassisted local escape and stronger-source approach at
the approximately5Hz target with affine2.0. These are selected simulation
results, not physical qualification; see [Gazebo status](gazebo_status.md).

Physical deployment and six operator-observed raised-wheel stop checks passed:
normal Ctrl+C, controller crash/freeze, acquisition freeze, guard crash/freeze.
These do not quantify physical stopping latency or qualify OS/electrical faults.

Installed follow-ups, in order:

1. Restore optional independent Vicon client/recording; missing Vicon stays nonfatal.
2. Reduce only physical caps from0.10/0.50 to0.05/0.30 after clearance problems.
3. **Worker initialization:** preload numerical dependencies before announcing
   ready. Cold imports formerly consumed each first job's deadline, repeatedly
   restarting the worker. Control stays nonblocking; deadlines were not extended.
4. **Steering handoff:** retain one complete accepted rolling snapshot while a
   replacement is pending, only within original0.5s freshness and unchanged
   context; reproject with current fresh yaw. Expiry/rejection/reset still applies.
5. **Initial filter priming:** seed the first cost without inventing a direction.
   Start on a subsequent usable change; no sleep/full-cycle gate and no priming
   during moving objective transitions.

Averaging means combining estimated steering vectors over a full measured arm
rotation; once qualified, use75% mean and25% instantaneous estimate. It smooths
commands but can reduce responsiveness. The handoff fix does not add nodes or
run-ending conditions.

[Steering deployment evidence](/home/mattb/Experiments/GESC-Gaussian/v3/steering_handoff_20261001T040328Z/REVIEW.md):
305 host and114 Pi software checks passed. Installed fixed-input Pi replay
reduced150 handoff switches to0,95 jobs/no errors. Earlier incremental builds
had retained stale installed files after a Pi clock change; fresh ordinary
package build/install plus imported hashes resolved this. Do not trust build
exit status alone or mix symlink and copied caches. Previous generated trees
are retained in the corresponding `mbuck_backups` task directories.

## Latest floor run: what is actually proven

Latest run found during2026-10-01 read-only inspection:
`20260930T211613_989126Z-3555`. Closed original files and decoded data are under
`/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/`.

- 382.4s nonzero commands, SEARCH throughout, no candidate/verification/design,
  no fill/escape, no internal zero command or mid-run expiry event, final zero
  and operator_stop. No Vicon measurements in this run.
- 1913 sequential valid observations at4.9798Hz; maximum valid gap0.2503s;
  measured arm17.07RPM. Pending support notices were not lost valid sequences.
- OpenCR position path12.88m, net0.61m; roughly two broad circuits. Whole-path
  descriptive radius1.085m, later arc fits around0.8–1.0m. Lamp coordinates were
  unknown: these are odometry geometry, not measured lamp-centered radii.
- Mean command during15–80s was1.79cm/s versus4.80cm/s in the prior run, with
  substantially weaker sensor variation. Later commands averaged4.82cm/s.
  Old-handoff replay on these same inputs also predicts about1.78cm/s early:
  no hidden new speed limiter was introduced. Starting conditions/illumination
  differ, so these are not controlled physical A/B comparisons.
- All 117 complete circular evaluations in offline detector replay fail both
  radius (one half above0.5m) and angular coverage (one half below60degrees in
  15–18s). No confirmations. Merely running longer or increasing only radius
  does not resolve both requirements. A single lit source does **not** disable
  first-fill logic. Live events corroborate no candidate; gate details are
  reconstructed, not directly recorded detector telemetry.
- 393/393 physical source entries still matched the deployment manifest;
  installed core/rolling/worker matched source. Pi was idle then. This handoff
  makes no fresh remote-state claim.

Physical Gaussian fill, local escape and global-source approach remain
unqualified. The latest evidence improves the diagnosis; do not relabel it a
successful escape or claim the recent fixes solved the broad orbit.

## Proposed next steps — not installed or tested

Discussion favored controlled **one-light physical** comparisons with steady
illumination and repeatable Vicon start position/heading, plus lamp position,
height/orientation and brightness in a consistent evaluation frame. Tighten
source seeking first, then verify detector recognition, then test two lights
when space permits. Keep experimental metadata simple and use ordinary bags.

The suggested first tuning comparison was angular gain **5.0 → 7.5**, holding
forward gain0.5 and caps0.05/0.30 fixed. **The user has not authorized/applied
this specific change; 5.0 remains installed.** Larger angular response could
tighten turning, but could amplify an erroneous direction; it needs a controlled
comparison. The0.5m detector ceiling does not steer the robot. Raising the
angular cap alone affects little of the latest run (about3% saturation).

Longer existing detector observation windows were discussed, not implemented.
Retain meaningful geometric evidence; avoid stacking special cases or merely
loosening every threshold. Distinguish research observation windows from input
freshness, optional-job budgets and actuator/process stopping. No blanket
timeout relaxation, new safeguard layer or automatic ten-minute stop is selected.

## Git and resumption boundary

Branch `refactor/esc-v3`. The user subsequently requested a clean, published,
synchronized Git tree. Shared physical support, worker/steering corrections,
analysis and tests are committed in `3492799`; the accompanying documentation
checkpoint records this handoff and the deployment history. The prior Gazebo
checkpoint was `a702cd2`, not the complete physical implementation.

The Git closeout reran 311 local regression checks successfully. Its
[final receipt](/home/mattb/Experiments/GESC-Gaussian/v3/git_closeout_20261002T041241Z/final_receipt.json)
records commit IDs, publication and synchronization verification. No Pi operation
or tuning change was part of that closeout. Earlier dated references to
uncommitted work describe historical checkpoints. Inspect current Git status
before new edits, and do not assume the committed Gazebo speed caps are the
Pi's configuration. Frozen V1/V2/archive references remain preserved.

Resume with a concise verified-state summary and one concrete next experiment.
This handoff does not launch a run or authorize the proposed gain/detector edits.
Use current user instructions for further implementation and physical readiness.
