# Physical GESC + Gaussian V3 — continuation handoff

Updated 2026-10-09 local time. Start in `/home/mattb/dsim-lab`. This is the
current continuation summary; follow the linked evidence instead of rebuilding
context from every historical phase. The 2026-10-09 review used read-only Pi
inspection; a subsequent user-authorized physical gain comparison follows below. Remote
state below is **last verified**, not a claim
that the robot is currently online, idle or unchanged.

### Latest update: two lights, 2026-10-09

The user cleared the floor and selected a current-V3 trial before any rollback.
Read the [new two-light review](/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/two_light_review_20261009_run1267/REVIEW.md)
and the dated section in `physical_deployment_status.md` before the older
one-light discussion below. Read-only Pi retrieval confirmed a closed89 s
SEARCH-only run with Vicon, no candidate/fill and final zero. Commands heavily
saturate and alternate; replay supports a steering/blending/saturation issue.
The older gain5→7.5 suggestion is no longer the recommended first response.
The review itself changed no tuning; the subsequent authorized gain comparison
is recorded below. Lamps are at lab-grid(1,1)/(3,3) m;
Vicon's first position is the requested origin, but axis alignment is unknown.
Five selected runtime source/install files match the host analysis code.
The older full393-file parity statements below retain their original dates.

### Installed gain comparison — 2026-10-09

The user authorized a common0.1 gain scaling: physical k_vx0.05/k_wz0.5
(previously0.5/5). Only the selected physical controller JSON and the matching
existing integration-test expectation changed on Pi. Ordinary build/check-only
passed;17 native focused checks passed;117 runtime files,7configs and12interfaces
match source. Caps0.05/0.30,75%/25% blend, detector, affine2, assistance off,
fixed5Hz, nominal20RPM and54-degree calibration remain unchanged. Gazebo retains
its own gains0.5/5 and caps0.10/0.50. No actual hardware was launched.

Evidence: `/home/mattb/Experiments/GESC-Gaussian/v3/physical_gains_20261009_trial02`.
Pi backup: `/home/pi/mbuck_backups/physical_gains_20261009_trial02`.
The operator will run the usual Bash command after restarting the Vicon server.
This is an unqualified physical tuning comparison, not a convergence fix claim.
**Offline mirror refresh is explicitly deferred until the user says testing is
done for today.** It still contains the prior gains/test expectation; do not
copy them back onto the live Pi or refresh the mirror prematurely.

### Latest floor outcome — lower gains did not fix source seeking

Read the [lower-gain run review](/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/two_light_review_20261009_run2626/REVIEW.md).
Run `20261009T181236_873027Z-2626` stayed SEARCH for103.93 s. Turn saturation
dropped to4.28%, with none after15 s, but the broad path remained. No fill/escape.
The user confirms both lamps/brightness unchanged and robot initially pointing
directly at the weaker lamp; do not repeatedly ask for these same setup facts.
That heading supports an approximate lamp-bearing comparison, not surveyed
Vicon alignment. The early averaged direction differs from local-light bearing
by about84.5 degrees clockwise; raw-light harmonic phase also differs substantially.
Next recommendation is a physical zero/reference and signal-phase check before
more tuning. This is not proof that the54-degree offset is wrong and does not
authorize a guessed correction or hardware diagnostic. No further Pi/mirror
changes were made; gains0.05/0.5 remain installed, mirror refresh still deferred.

### Encoder reference correction — 2026-10-09

After the preceding direction diagnosis, the operator held the arm straight
forward and the calibration script displayed 298–300 degrees. Live inspection
confirmed that reading already subtracts the old 54-degree offset. The implied
raw forward angle is 352–354 degrees; the user authorized 353 degrees as the
new offset. This supersedes the preceding proposal-only calibration discussion.
The physical legacy reader and V3 acquisition now subtract 353 once; startup,
profile metadata and regression expectations agree. Physical gains remain
0.05/0.5 and caps remain 0.05/0.30. Shared simulation code is unchanged.

Evidence: `/home/mattb/Experiments/GESC-Gaussian/v3/physical_encoder_20261009_353`.
Pi backup: `/home/pi/mbuck_backups/physical_encoder_20261009_353`.
Build/check-only and final validation are recorded in deployment status.
Operator next step: repeat the same stationary forward-angle check, expecting
approximately 359–1 degrees (near zero), before the next floor trial. The
correction is not yet physically rechecked and does not establish convergence.
Offline mirror still has the previous calibration/gains and remains untouched
until the operator declares today's tests complete.


## Corrected-reference floor outcome — 2026-10-09

The operator verified forward readings near 359–1 degrees, then ran
`20261009T182811_021920Z-4810`. They report much better steering and a direct
approach to the weaker hanging lamp, whose final robot position was almost
underneath it. Lamp hangs about one foot above the robot; preserve this setup.
[Latest run review](/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/two_light_review_20261009_run4810/REVIEW.md)
and its `slowdown.png` explain the remaining issue.

Live events show SEARCH for all 87.50 seconds, no candidate, VERIFY, DESIGN,
ESCAPE or fill. All 438 observations valid at 4.980 Hz. Odometry and Vicon both
show about 1.569 m net displacement. Final 30-second commands averaged 1.224 cm/s
forward magnitude; actual odometry path speed about 0.63 cm/s. It was creeping,
not paused for a calculation. Last static-detector replay support radius was
9.33 cm (limit 4 cm), drift 0.608 cm/s (limit 0.5); no qualifying orbit either.

Next proposal: gains 0.05/0.5 -> 0.10/1.0 with unchanged 0.05/0.30 caps,
353-degree calibration and detector. Fixed-input command rescaling suggests
more response near the lamp, not a proven trajectory or detection improvement.
**Not authorized or installed:** gains remain 0.05/0.5. No Pi/mirror changes.
Closed bag hashes and five selected source/install/host files verified.
Physical source approach improved in this observed trial; fill/escape/global
approach remain unqualified. Offline-mirror refresh remains deferred.


## Post-calibration gain comparison installed — 2026-10-09

The user authorized the run4810 review's proposed doubling. Physical gains are
now **0.10/1.0**, superseding the prior proposal-only statement and0.05/0.5
selection. Caps0.05/0.30, calibration353 degrees, detector, blend, firmware,
arm speed and assistance are unchanged. Gazebo gains remain0.5/5.

Evidence/commands: `/home/mattb/Experiments/GESC-Gaussian/v3/physical_gains_20261009_trial04/RECEIPT.md`.
Pi backup: `/home/pi/mbuck_backups/physical_gains_20261009_trial04`.
Idle preflight, independently verified laptop originals, ordinary build/check-only
and installed configuration validation passed. **17 focused native checks passed
in8.58 seconds**. Exactly controller JSON and its existing integration-test gain
assertion changed;391/393 source entries unchanged.136 installed runtime/config/
interface files match source; no active control/recording/build/test processes.

Next operator trial uses the same Bash command and a restarted Vicon server.
No hardware launched, offline mirror refreshed, commit or push performed.
Floor outcome is pending; stronger response is not yet evidence of an orbit,
Gaussian fill, escape or global-source approach. Offline refresh remains deferred.


## Latest floor run: confined but undetected — 2026-10-09

Run `20261009T183636_203123Z-6323` used gains0.10/1.0, caps0.05/0.30,
calibration353. Operator reports promising near-light behavior but no escape.
[Review](/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/two_light_review_20261009_run6323/REVIEW.md)
and `confinement.png` supersede run4810 as the latest floor evidence.

279.88s SEARCH-only; no candidate, verification, design, fill or escape.
1395 consecutive valid observations at4.979Hz; Vicon present. After80s, odometry
stayed within16.5x14.8cm but commands alternated forward/reverse (49.3% reverse)
and turning reached its cap53.5% of the time. This is confined irregular motion,
not the earlier slow creep. Detector replay: all30 static evaluations after100s
fail4cm radius (median5cm);29/30 already pass the drift limit. Circle/oscillation
models never achieve persistence. No escape action actually started.

Recommendation, **not authorized or installed**: retain current gains/caps,
compare static support radius4->6cm with30s window/drift/other criteria intact.
Retained-window sweep first passes at90s from epoch in this run and never in
three earlier runs; this is selected retrospective evidence, not qualification.
Avoid interpreting increased speed as a demonstrated remedy for detection.

Live original GESC baseline is gains1.0/5.0, caps0.10/0.50; initial V3 was
0.5/5.0 with those caps, so it was not an exact baseline gain match.
No Pi/mirror changes during review. Current gains0.10/1.0 remain installed.
Any proposed detector correction needs focused validation and explicit handling
of shared simulation/physical parity. Fill/escape/global approach unqualified.


## Static-confinement correction installed — 2026-10-09

The user authorized the run6323 recommendation. Shared V3 static support radius
is now **0.06m**, replacing0.04m in both host source and installed Pi code.
This supersedes the preceding proposal-only status. Thirty-second support,
0.005m/s drift, all circle/oscillation conditions, moving verification and
fill/escape behavior are unchanged. Gains0.10/1.0, caps0.05/0.30, encoder353,
arm/firmware settings are unchanged. This shared threshold also applies to
Gazebo; no new simulation run or behavioral qualification is claimed.

- Host numerical/core regression: **118 passed in2.50s**, including six new
  radius boundary, retained drift rejection and full30s support checks.
- Changed detector replay on four retained traces: run6323 confirms at90s
  from epoch; runs1267/2626/4810 do not confirm. No closed-loop outcome claim.
- Ordinary Pi build/check-only passed. **23 native checks passed in8.50s**.
- Exactly1/393 source entries changed;392 unchanged.136 installed runtime/
  config/interface files match source; shared recurrent.py hash matches host.
  Idle before/after; no hardware started. `git diff --check` passed.

Evidence and exact commands:
`/home/mattb/Experiments/GESC-Gaussian/v3/physical_static_radius_20261009_6cm/RECEIPT.md`.
Pi backup: `/home/pi/mbuck_backups/physical_static_radius_20261009_6cm`;
redundant laptop original verified before deployment. Only shared numerical
source, focused tests and current documentation changed in the host checkout.
No commit/push; existing documentation work preserved.

Operator next trial uses the usual Bash script after restarting the Vicon server.
Physical recognition/verification/fill/escape remains pending. Offline mirror
is untouched and intentionally retains4cm/older gains/calibration until the
user declares today's tests complete.


## Selected physical fill/escape success — 2026-10-09

Latest run `20261009T185541_391452Z-1262` follows battery replacement/reboot.
Operator reports local escape and arrival near the stronger lamp, stopping just
before contact. [Successful-run review](/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/two_light_review_20261009_run1262/REVIEW.md)
and `successful_escape.png` now supersede the earlier SEARCH-only qualification
boundary for this selected physical trial.

Live events: candidate/VERIFY90.05s, DESIGN90.10s with54 samples, fill1 and
ESCAPE90.45s, escape_complete124.47s, SEARCH124.60s, operator stop165.06s.
One active fill, no retries/escalations or optional assistance. Escape completed
in34.02s; at return to SEARCH the robot was1.427m from the fitted center versus
exit radius1.367m. Vicon/odom show continued approach afterward and total net
travel4.225/4.263m. Operator-observed global arrival is trajectory-supported;
no automatic best_source/global-confinement event occurred before stopping.

822 consecutive valid samples at4.979Hz, maximum gap0.251s.826 invalid-status
notices are817 pending pose support and9 encoder notices:820 precede the same
valid sequence by about50ms,6 reference already published valid sequences.
No lost valid sequences, mid-run WAITING_INPUT or internal zero command.
Valid-only measured arm17.51RPM; generic analyzer arm output has too few adjacent
valid pairs because notices alternate and must not be treated as a full-run rate.

All393 source entries match the6cm deployment; seven selected runtime files
match host/Pi source/install. Closed original files SHA256 verified. No Pi edits,
hardware startup or mirror refresh. Keep gains0.10/1.0, caps0.05/0.30,
calibration353 and static radius0.06m for a repeat run. Battery change prevents
calling this a strict single-variable A/B experiment. Selected physical local
fill/escape is now demonstrated; repeatability, automatic global ranking,
sustained global behavior and broad physical qualification remain open.
Offline mirror remains deferred until the user ends today's testing.


## Second consecutive physical success — 2026-10-09

Run `20261009T190351_141387Z-2037` repeats the fill/escape success with unchanged
settings. Operator again observes arrival at the global lamp. Recorded candidate
90.04s, DESIGN90.08s, fill/ESCAPE90.35s, escape_complete121.88s, operator stop
159.49s. Escape31.52s versus34.02s in the first success. One fill,56 samples,
no design escalation/rejection, optional assistance off. No mid-run WAITING_INPUT
or internal zero commands; final zero.795 consecutive valid observations at
4.980Hz, maximum gap0.251s and **zero invalid-status notices**.

[Latest review](/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/two_light_review_20261009_run2037/REVIEW.md)
and `repeat_comparison.png` show closely overlapping Vicon paths. Vicon net
4.156m; endpoint8.3cm from the first success. These are two consecutive selected
physical local fill/escape successes, with operator-observed global approach.
No automatic best_source/global-confinement event before either stop; broad
robustness and sustained global behavior remain unqualified. Preserve the exact
current settings; no new tuning proposed.

Closed originals SHA256 verified;393 source entries unchanged since deployment,
seven selected runtime files match host/Pi source/install. No Pi/mirror changes,
new hardware tests, commit or push. Offline mirror remains deferred until the
user says today's testing is complete.


## Higher-cap comparison installed — 2026-10-09

After runs1262/2037 succeeded at lower caps, the user authorized **0.10m/s /
0.50rad/s** for the next comparison, replacing0.05/0.30. Gains remain0.10/1.0,
encoder353, static radius0.06m,30s support/0.005m/s drift; all other numerical,
firmware and assistance selections remain unchanged. Prior success belongs to
the lower-cap configuration; higher-cap behavior is pending operator testing.

Backup: `/home/pi/mbuck_backups/physical_caps_20261009_010_050`.
Laptop originals, exact commands and receipts:
`/home/mattb/Experiments/GESC-Gaussian/v3/physical_caps_20261009_010_050/RECEIPT.md`.
Idle preflight and independently verified backups passed. Ordinary build/check-only
reports installed caps0.10/0.50. **17 native checks passed in8.42s**, including
selected configuration, command ceilings and mocked input-loss/recovery/stop.
Exactly controller JSON and two existing test files changed;390/393 source
entries unchanged.136 installed runtime/config/interface files match source;
no active control/recording/build/test processes remain. Diff checks pass.

Operator will restart Vicon and use the same V3 Bash command. No hardware
launched, offline mirror refreshed, commit or push performed. The successful
lower-cap configuration and both successful runs remain preserved. Offline
mirror refresh remains deferred until the user ends today's testing.

### Higher-cap success with longer confinement delay — 2026-10-09

Run `20261009T191502_046584Z-3461` also completed local escape, with operator-
observed global arrival. Candidate138.046s versus90s for both lower-cap runs;
VERIFY+DESIGN0.406s; escape21.129s versus31.524–34.021s. The delay is in SEARCH.
Pre-candidate detector replay shows drift passing from66s, but30s support radius
remaining above6cm until138s (7.77cm at90s,6.14cm at132s,5.962cm at138s).
Near the fitted center, forward commands reverse41.5% of the time: small bounded
motion rather than a commanded full orbit. Physical gains remain five times
lower than current Gazebo gains; its XY light model omits overhead lamp height.
These differences explain why identical-looking circles are not required or
expected; the precise contribution of each physical effect is not isolated.

[Latest review and comparison](/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/two_light_review_20261009_run3461/REVIEW.md)
records the third selected escape, one fill/no escalation/assistance, consecutive
valid samples and no internal pause. No automatic global recognition before
operator stop.393 source entries match higher-cap deployment; seven runtime
files match host/Pi source/install. Higher caps0.10/0.50 remain installed.
Lower caps0.05/0.30 are recommended as the better-supported reference, **not
restored**. This review changed only analysis/documentation; no Pi/mirror edits,
hardware launch, commit or push. Mirror refresh remains deferred.

### Lower caps restored for third repeat — 2026-10-09

The user subsequently authorized returning to **0.05m/s /0.30rad/s**, now
installed and verified. This supersedes the preceding proposal-only state.
Gains0.10/1.0, encoder353, static radius6cm and other settings stay fixed.
[Receipt](/home/mattb/Experiments/GESC-Gaussian/v3/physical_caps_20261009_restore_005_030/RECEIPT.md):
initial stale installed config caught by tests, timestamp corrected and ordinary
check-only build repeated; final17 native checks pass,136 installed files match
source, Pi idle. Exact backups retained on Pi/laptop. No hardware launch,
mirror refresh, commit or push. Operator will run a third lower-cap trial.

### Third lower-cap success — 2026-10-09

Run5245 again confirms local fill/escape, with operator-observed global arrival:
candidate90.03s, escape32.57s, return SEARCH123.10s. Three lower-cap successes
now retained plus higher-cap3461. [Latest review](/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/two_light_review_20261009_run5245/REVIEW.md)
explains the repeat rightward departure/left bend: deterministic approach-derived
affine direction, likely clockwise washout phase rotation, then removal of affine
and restoration of raw-light steering at measured exit. The four-path overlay
shows bends after return to SEARCH. No fixed route/global coordinates are used.
Isolated phase probe supports the explanation without fully isolating moving-
robot effects. Current settings unchanged; offline mirror still deferred.


### End-of-testing offline mirror refresh — 2026-10-09

The user ended testing and authorized the deferred Pi-to-laptop refresh.
[Sync receipt](/home/mattb/physical_TB3_files_snapshot/sync_records/20261010T024420Z_pi_refresh/README.md) records verified direct-SSH Pi identity, established
filters, full pre-refresh archive outside pi/, transfer and source audits.
All eight floor runs and trial backups are included.393 source files match by
path/SHA256/size/mode; final scoped checksum dry run has zero changes. No Pi
writes, hardware launch, build, shutdown, commit or push. Current physical
caps0.05/0.30, gains0.10/1.0, encoder353 and6cm detector are mirrored.
Previous statements that refresh is deferred are historical and superseded.

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
- Physical trial forward/angular gains **0.10 / 1.0** (2026-10-09), trial speed caps **0.10 m/s / 0.50 rad/s** (authorized after two lower-cap successes).
  Gazebo retains **0.10 / 0.50**. Affine magnitude **2.0**.
- Fixed **5 Hz** original UNO application, nominal arm **20 RPM**, encoder
  calibration **353 degrees** once (authorized 2026-10-09 after the stationary
  forward-angle measurement). Historical 54/354-degree and optional10/15Hz
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
