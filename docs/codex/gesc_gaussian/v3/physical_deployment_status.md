# V3 physical deployment status

**Deployment and operator-observed raised-wheel checks complete.** Physical
Gaussian fill, escape and global approach were untested at that checkpoint.
The user subsequently began floor trials; their analysis is pending.
See the [handoff](physical_deployment_handoff.md) for the current state.

Implementation authorized 2026-09-29; see `physical_deployment_plan.md`.
Starting simulation HEAD `a702cd2ed5df300379c5c62629562d466957a155`, clean.
Read AGENTS, active plan/status, usage/architecture and environment guides.
V46 handoff and rollback rationale re-read; historical speed limits superseded
for V3 only by the user's explicit 0.10/0.50 instruction.

Initial live preflight: SSH to `tb3-6` works; approximately 95 GB available. No matching
ROS/control/rotation/pigpio processes. Existing src/build/install present.
Pi clock still reads 2026-08-13; not adjusted. No devices were opened or actuated during that initial preflight.

- Backup and live-source parity: PASS. All347 original V46 files match live Pi.
  Complete src/build/install archive verified against2054 entries on Pi and
  independently copied/hash-verified on host. Pi backup:
  `/home/pi/mbuck_backups/gesc_v3_deployment_20260929T210229Z`.
  Archive SHA256 `9b2297fdaeaef9958f7f6fa99cc15098ebc6979e8fa8f0a771ed79dee3985691`.
  Original editable numerical dependency also archived on Pi/host, SHA256
  `4b2ae602faf3b3dc79a1410b1b93ddd1452fa59b5b6c7e9a312c580233352e3e`.
  Restoration guidance saved beside both copies. No firmware access/change.
- Shared recovery/optional assistance:164 focused tests PASS; first full shared
  suite287 PASS in17.98s (`shared_full_suite_01.log`). Subsequent worker/process
  guard changes require final focused validation before deployment.
- Physical acquisition:18 mocked tests PASS plus1 real ROS transport integration
  test with fake devices PASS (5.72s). Actual raised-wheel evidence follows below.
- Local actuator/process protection:26 process/worker and daemon-program tests
  PASS (13.96s). Review fixed premature startup lease arming and servo close
  ordering. Native process and later hardware receipts are below. No network/session monitor.
- Legacy preservation:342 original files byte-identical; only two package setup
  files, additive interface registration/constant, and retired V1-only wrapper
  differ. All26 original legacy Bash methods are byte-identical. Before-deploy
  native numerical/config/import probe PASS for26 scripts and7 core modules.
- Native deployment/build/compatibility: PASS; detailed closeout below.
- Offline mirror: PASS; final source archive and hardware handoff retained.
- Raised-wheel stopping: operator-authorized checks PASS for the cases below.
  Floor behavior remains untested.

Exact receipts retained outside Git at
`/home/mattb/Experiments/GESC-Gaussian/v3/physical_deployment_20260929T210229Z`.

## Installed deployment and validation

Installed393 source files in the original `/home/pi/ros2_ws`; no sibling
workspace, firmware, ROS underlay, numerical-library or Pi-clock change.
Preserved original src/build/install together in the backup's `prior_workspace`.
Normalized incoming source mtimes to the Pi's unchanged clock before the fresh
build, avoiding future-dated copied sources/caches. Receipt:
`pi_receipts/source_mtime_receipt.json`.

- Fresh ordinary build: all3 packages PASS in1m26s (`build_01.log`). Intentional
  disabled byte-compilation warnings were reported, not hidden.
- Pi-native retained legacy regression:222 PASS in18.42s. Original selected-V1
  wrapper/count policy tests are not V3 criteria; the retired wrapper is backed
  up. All26 actual legacy scripts/configurations/numerical probe results equal
  the pre-deployment Pi results; all7 probed installed legacy module hashes
  unchanged (`legacy_before_after.json`).
- Pi-native V3 core/numerical/observation/worker/acquisition/bringup/process
  tests:170 PASS in39.82s (`pi_receipts/native_tests_01.log`). Device I/O mocked;
  Linux process fault tests use real dummy child processes, not actuators.
- Installed verification:117 runtime Python files match source, all12 physical
  interfaces resolve, selected installed profile resolves system time, OpenCR
  odom, caps0.10/0.50, gains0.5/5, affine2.0, assistancefalse/15s/0.20m.
  Original non-package research helper files are explicitly reported as source
  helpers rather than wrongly required as installed modules. The initial
  verifier mismatch and correction are retained in `installed_verify_01_failure.txt`.
- Real original legacy ordinary build command followed by the new V3 Bash
  `--check-only` build/source/inspect path: PASS. Source/install equality again
  PASS (`legacy_build_02.log`, `v3_wrapper_check_only_02.log`,
  `installed_verify_after_switch.json`). No command started devices or a ROS
  hardware graph; tests used localhost-only domains.

## Final review correction

Review identified a real ownership-stop gap: terminal physical FAULTED still
renewed process authorization, allowing a competing publisher to retain an
active driver. After best-effort zero, physical FAULTED now exits without lease
renewal; critical-child death/expiry stops the owned driver. WAITING_INPUT
continues renewing and automatically recovers. Callback ownership faults,
control exceptions and frame faults are tested. This is not a data/readiness gate.

The analyzer also now uses valid SensorObservation phase/cost when legacy
encoder/cost topics are absent. RPM excludes source changes, invalid samples
and long gaps, reports accepted/excluded pairs and angle-aliasing limits, and
does not claim ADC timestamp knowledge. No runtime logging node was added.

Both corrections were installed as one preserved, hash-verified three-file
review patch. Ordinary rebuild PASS in12.4s; final117-file installed/source
parity PASS. Pi follow-up:5 terminal-fault/lease tests PASS in3.00s,17 real ROS
control/shutdown/closed-bag analysis tests PASS in26.05s. The native test copy
changes only the executable selector to `gesc_v3_controller`, preserving the
legacy `controller_node` entrypoint. Exact copies/commands are in `validation/`.
Final shared simulation suite:297 PASS in18.18s,372 pre-existing NumPy matrix
warnings (`shared_final_review.log`). No Gazebo research rerun occurred.

Final source archive SHA256:
`1b7493a847b94947bddd1f57ceb8d764a0f6132353c4f70543ce16ccb230af83`.
Initial candidate, review patch, final manifest and full final source are all
retained; no failed/intermediate evidence was overwritten.

## Pre-hardware checkpoint

The pre-hardware live audit verified all393 source hashes/modes, no unexpected non-generated
source, no physical ROS/rotation/control processes, pigpiod absent, both serial
ports unowned. No hardware was opened or actuated. Original fixed5Hz firmware
was left untouched; firmware identity is inherited from V46, not a new readback.

Offline mirror393 files match the final manifest. Its prior V2-era source and
old root guidance were preserved under its new deployment backup before refresh;
all earlier backups/sync records/failed experiments remain. Snapshot README and
AGENTS now point to current V3 guidance rather than selecting old V2 rate logic.

At this pre-hardware checkpoint, software deployment was verified; hardware
checks awaited operator readiness. Subsequent authorized results are below. No generic Gaussian promotion
or removal of V1 dependencies occurs before physical acceptance. Working shared
changes remain on `refactor/esc-v3`; frozen references are unchanged, no commit
or push has been made during deployment.

## Raised-wheel checks — complete

The operator explicitly confirmed wheels raised, arm clear and active observation.
`normal_ctrlc_01` failed before hardware startup because the permitted pigpiod
path is `/usr/local/bin/pigpiod`, not `/usr/bin/pigpiod`. The path was corrected
in staged/live/offline source and rebuilt (12.4s); installed parity passed.
No sudo policy or firmware changed. Preserve this failed startup separately.
The previous final-source archive hash above predates this correction.

`normal_ctrlc_02` ran on the actual Pi for a bounded 20-second check, then the
harness sent SIGINT (expected timeout status124). OpenCR reached Run, both
wheels and arm moved, and the operator confirmed both stopped promptly.
Post-stop inspection found no remaining control processes and GPIO18 at1500us.
The daemon remains running. The ordinary bag closed with metadata. A private
numerical worker printed KeyboardInterrupt during group SIGINT; cleanup still
completed. Precise physical stopping latency was not instrumented.
Process-failure checks and closed-bag analysis also completed, below. No floor trial has run.

The closed normal-stop bag contains 46/46 valid observations at **4.9724 Hz**
(249.5 ms maximum gap), observed-phase arm speed **17.95 RPM**, and 183
consecutive nonzero commands spanning approximately **9.136 seconds**, followed
by final zero and `STOPPED/SEARCH`. No fill or escape occurred. `/odom` was
approximately 20.05 Hz. Raised-wheel odometry is not physical translation.
Only the first valid sample approached the 50 ms phase-support tolerance
(48.706 ms; overall median 0.528 ms); this is not sustained timing failure.
ADC conversion time remains unknown. See external
`raised_wheels/normal_ctrlc_02/REVIEW.md` and its analysis JSON/plots.

Each process-fault test first observed approximately three seconds of valid
5 Hz input, fresh odometry and nonzero commands before one exact-PID signal.
The operator separately confirmed that wheels and arm stopped on their own
in **all five** cases. Each receipt observed neutral1500us and all owned
processes gone before harness cleanup; no harness kill was needed to stop them.

| Case | Injected fault | Observed driver exit after injection | Operator observed wheels/arm stop |
| --- | --- | --- | --- |
| `controller_kill_01` | Controller SIGKILL | about 0.05 s | Yes |
| `controller_freeze_01` | Controller SIGSTOP | about 1.03 s | Yes |
| `acquisition_freeze_01` | Acquisition SIGSTOP | about 1.01 s | Yes |
| `guard_kill_01` | Local guard SIGKILL | about 0.05 s | Yes |
| `guard_freeze_01` | Local guard SIGSTOP | about 1.01 s | Yes |

Driver process-exit times are observer measurements, **not measured actuator
stopping latency**. The acquisition-freeze case first recorded a zero command
about 0.45 s after input stopped, then local process protection stopped the
driver. Frozen child cleanup took up to about 3.94 s, after driver termination.
Forced-stop logs contain expected interrupted-process/queue-resource messages;
the process and neutral checks passed. A hard guard kill may leave an inert
HALTED daemon-script slot; kernel, pigpiod or electrical failure was not tested.

The bounded 20-second normal test and 30-second fault observation limits belong
to the commissioning harness, not the ordinary V3 operator run. No arbitrary
research/run deadline or SSH-loss stop condition was added.

## Final checkpoint

Final source archive SHA256 after the daemon-path correction:
`12b3f235466e133141756489a34b1c9385f3bdcb75a48c4455d19d0bf876d1e8`.
The preceding archive is preserved as `final_source_before_daemon_path.tar`.
All 393 staged source files are covered by the final manifest.

Post-hardware live audit: all 393 source hashes/modes match, no unexpected
source files or control processes, both serial ports unowned, GPIO18 at1500us.
The existing pigpiod remains running. See
`pi_receipts/final_post_hardware_audit.json`. V1 and older V2 archives remain
intact. No firmware, clock, ROS underlay or legacy numerical dependency changed.

Deployment and these raised-wheel checks are complete. Sustained timing/CPU
headroom under Gaussian fitting, physical recovery during deliberate sensor
loss, moving verification/fill/escape and global-source approach still need
physical evaluation. The explicit V3 command is ready for an operator-controlled
floor trial; generic Gaussian promotion awaits that acceptance.

## Optional Vicon restoration — complete

User authorized restoring independent tracking while keeping absent Vicon
nonfatal. Initial read-only Pi check: idle; V3 source/install agree and contain
no Vicon launch/record topic. Baseline GESC explicitly selects `odom_method=vicon`
and retained Gaussian launch uses the evaluation topic. Earlier floor recordings
are preserved; no Vicon data can be retroactively recovered from absent topics.
No numerical, firmware, acquisition or baseline-client changes are planned.

Restored the unchanged physical `odometry_node` client by default, isolated as
an optional process. It publishes only the dedicated evaluation topic; V3
control retains OpenCR `/odom`. The ordinary physical bag now includes
`/gesc_gaussian/evaluation/vicon_odom`. Optional missing/spawn-failed/exited/
frozen Vicon cannot gate or stop control; `--no-vicon` is available. Observer
cleanup occurs after actuator stopping. No original client, server, baseline
script, control mathematics, firmware or tuning was changed.

Validation and deployment receipts:
`/home/mattb/Experiments/GESC-Gaussian/v3/vicon_restore_20260930T032350Z`.

- Host focused bringup/runtime regressions: **43 passed, 20.95 s**.
- Native ordinary three-package build: **PASS, 12.4 s**.
- Pi native bringup/runtime plus real ROS/loopback UDP test: **44 passed,
  34.91 s**. Silent server data did not fabricate poses; later packets converted
  mm to metres and carried wall receipt time without a timekeeper publisher.
- Retained legacy Vicon source/protocol/cleanup regressions: **13 passed,
  0.81 s**. Original Vicon code and all legacy scripts remain byte-identical.
- Stationary Vicon-only lab connection: **123 poses observed at 9.499 Hz**,
  all finite, and **124 poses in the closed bag**. Client and recorder exited0.
  This launched no controller, OpenCR driver, acquisition node or servo owner.
  The lab's selected tracked object was nearly stationary; no floor behavior
  or moving-source algorithm acceptance is inferred.
- Full source comparison: **393 files**, exactly four changed V3 source/test
  files; **389 unchanged**. Both installed runtime files and the original
  installed Vicon client match source. No remaining control/observer processes;
  both serial ports unowned. All393 offline source hashes/modes match.
  The user's executable permission on the V3 Bash script was preserved.

Pre-change source/installed files, patch, manifests and receipts are backed up
at `/home/pi/mbuck_backups/vicon_restore_20260930T032350Z`, with redundant host
and offline-mirror copies. Original deployment/V1/V2 backups remain intact.
The previous full final-source archive is a pre-Vicon historical checkpoint;
use this follow-up manifest for current parity. Shared source code did not
change in this task; repository updates are documentation only. Git changes
remain intentionally uncommitted and frozen refs unchanged.

The inherited client sends one greeting; the server retains one client endpoint
per launch. Restart the Vicon UDP server before the next run to clear the
stationary probe's connection, and between subsequent runs. If the server is
off, V3 still runs without Vicon samples; starting it late does not resend the
legacy greeting. This optional evaluation path is not an SSH-loss monitor or
a new failsafe. Existing floor runs are preserved and await analysis.

## First reviewed mobile floor run — partial operator observation

Read-only retrieval and analysis of the latest closed run
`20260929T203345_844703Z-3962` is retained at
`/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/20260929T203345_844703Z-3962/REVIEW.md`.
The user stopped for obstacle clearance in a cramped room, reporting that the
robot passed the local light. Independent Vicon was recorded: 490 samples at
9.50 Hz, approximately4.12 m path and3.22 m net displacement. The recording
contains47.75 s of nonzero commands, with81.4% of moving time at the linear cap
and93.4% at the angular cap. All238 valid sensor observations are consecutive,
at4.979 Hz; diagnostic notices did not produce an internal zero-command interval.
The final command is zero and the event is `operator_stop`.

This run stayed in SEARCH with no Gaussian fill or escape. Physical light
coordinates were not recorded, so the reported pass and its cause cannot be
quantified against a known source location. Physical escape/global acceptance
remains open. Both bounded analysis commands completed; independent trajectory
and signal/command plots were reviewed. Pi remained idle during inspection.

Recommendation only: compare physical caps0.05/0.30, verified from the preserved
restored V1 profile, while retaining V3 gains0.5/5 and other settings. At the
focused encoder-derived17.64 RPM estimate, the potential displacement per arm
turn at the linear cap decreases from34 cm to17 cm. No Pi/simulation tuning,
source, build or firmware was changed during this review; installed V3 caps
remain0.10/0.50. Earlier short recordings remain preserved and unanalysed.

## Physical speed-cap reduction — installed 2026-09-30 UTC

The user subsequently authorized the proposed lower physical caps. Physical V3
now selects **0.05 m/s linear and 0.30 rad/s angular**. Gains0.5/5, affine2.0,
assistance off (optional15s/20cm), fixed5Hz, nominal20RPM and54-degree calibration
remain selected. Gazebo tuning remains0.10/0.50. No physical motion was started.

Evidence: `/home/mattb/Experiments/GESC-Gaussian/v3/physical_caps_20260930T034812Z`.
Pi backup: `/home/pi/mbuck_backups/physical_caps_20260930T034812Z`.
Pre-change source/installed files and manifests are retained on Pi, host and
offline mirror. The configuration changes only the two caps. The physical
startup message now displays resolved values; two existing physical test
expectations were updated. Legacy sources/scripts and the shared algorithm
implementation are unchanged by this follow-up.

- Ordinary three-package build through the existing Bash runner with
  `--check-only`: **PASS**, command elapsed18.76s; installed JSON resolves the
  new caps and preserves all other selected settings.
- Pi native focused bringup and mocked-device ROS acquisition/recovery checks:
  **17 passed in8.17s**, with localhost/domain191 and a100s bound. These tests
  do not open actual serial/GPIO devices or actuate the robot.
- Final audit: **393 source files**, exactly the four intended changes,
  **389 unchanged**; changed installed runtime/configuration match source;
  all393 offline mirror hashes/modes match. No remaining control processes.
- `git diff --check` passed. Existing unrelated Git changes remain preserved
  and uncommitted. The simulation controller JSON is byte-identical to its
  pre-change copy.

The usual V3 Bash command now uses these lower physical caps. Actual floor
behavior at these settings and Gaussian escape/global-source acceptance remain
untested; this is configuration/software verification only.

## Evening floor-run review — SEARCH-only; worker defect reproduced

The operator ran three additional lower-cap trials, changed start positions,
and stopped for obstacles. All seven evening closed bags were retrieved and
SHA256-verified read-only. Detailed review, plots, numerical replay and isolated
Pi/laptop probes are retained at
`/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/night_20260929_review/REVIEW.md`.

Every run stayed in SEARCH with zero fills, no recorded input-expiry/fault
event, no internal zero-command interval, final zero and `operator_stop`.
The lower-cap runs moved58.60/101.42/92.95s and still followed broad partial
arcs with descriptive fitted radii about1.7--2.3m. Offline recorded-odometry
replay confirms no detector candidate; all complete circle windows fail at
least the0.5m fitted-radius criterion. No Gaussian/affine escape was exercised.
All1,982 valid observations have consecutive per-run sequences at roughly5Hz;
diagnostic notices must not be counted as dropped costs.

A concrete Pi worker initialization defect was reproduced without ROS/devices:
three successive cold coherence jobs with the production0.5s allowance ended
in `numerical_deadline`, each restarting the worker. A diagnostic-only3s
allowance let the cold job finish in0.655s; the same warmed process then returned
within one50ms polling interval. Direct warm compute was about6--8ms. The
laptop's matching cold probe passed in0.201s. The worker announces ready before
the lazy SciPy import; timeout restarts can repeat that cold import indefinitely.
Coherence errors are silently discarded by the core, preserving instantaneous
fallback steering. Recorded commands favor that fallback over an immediate
averaged prediction in about99% of distinguishable selected comparisons.
This is strong causal evidence of lost averaging, not a completed proof that
correcting it alone will solve the physical trajectories.

Vicon position supports the broad trajectories, but raw path length/yaw need
jitter/outlier handling; the newer runs include large Vicon orientation jumps.
Vicon remains evaluation-only. Exact physical light positions and optical
field shape are unknown; user estimates5ft start-to-local and9ft source
separation, versus selected Gazebo1.50m and3.61m. Some first observation poses
also need separate startup inspection; later pose agreement is millimetric.

Recommended next work is a bounded worker-initialization correction and proof
that averaging participates with Pi timing, followed by simulation/physical
comparison; no forced fill or additional speed/affine tuning is justified yet.
No runtime source, build, firmware or tuning was changed during this review.
Pi idle at final inspection, physical caps remain0.05/0.30, and Gaussian
escape/global-source qualification remains open.

## Worker initialization correction — installed 2026-09-30

The user authorized the bounded correction above. The shared numerical worker
now imports selected coherence/fill dependencies before announcing ready, after
binding parent-death cleanup. Control remains nonblocking and can use fresh
instantaneous steering during initialization. Coherence0.5s/fill5s job budgets,
data-age checks, numerical formulas, physical tuning, guards and firmware are
unchanged. Only the physical worker source changed; no hardware was launched.

Detailed evidence and commands:
`/home/mattb/Experiments/GESC-Gaussian/v3/worker_init_20260930T215232Z/REVIEW.md`.
Pi backup: `/home/pi/mbuck_backups/worker_init_20260930T215232Z`.
The same source/receipt backup is retained in the offline mirror.

- Delayed real SciPy-import regression reproduces the old deadline failure and
  passes with the fix. Shared focused worker/core/node-fault tests: **133 passed**.
  Native Pi installed worker/core tests: **101 passed**.
- Three newly spawned Pi workers process the original recorded coherence job
  within the existing0.5s budget: initialization0.88–0.92s, job return about28ms
  including polling, no restarts.
- Real-time recorded5Hz/core replay: before, zero completed jobs,12 deadline
  errors and zero blended ticks; after, **46 completed jobs, zero errors and136
  blended ticks** out of400 control ticks. One worker PID. Control ACTIVE at
  0.150s precedes worker ready at1.000s; max measured core tick2.57ms. Correct
  physical caps and final zero pass. This fixes demonstrated loss of averaging;
  fixed recorded inputs do not establish a corrected trajectory or physical
  behavior under full ROS/device load.
- Initial incremental build returned success but kept old installed code due
  to future cached mtimes after a backward Pi clock change. The regression
  detected it:1failed/100passed. Preserve that failure. Old generated
  `build/ros_esc` and `install/ros_esc` are backed up intact; fresh ordinary
  package-only build passed in6.47s and installed imports/hash now match source.
  A preceding setup-path typo failed before moving/building; retained separately.
  The user adjusted the Pi clock during this work; no agent clock edit was made.
- The usual Bash runner's subsequent ordinary build with `--check-only` also
  passed (20.02s total). A repeated installed/source audit stayed identical;
  this confirms the next incremental build retains the corrected worker.
- Final audit:393 source files, exactly worker.py changed,392 unchanged;
  117 installed Python runtime files,7 configs and12 interfaces match source;
  all393 offline hashes/modes match. V1 backup exists; no control processes.
  Physical caps0.05/0.30, gains0.5/5, affine2, assist off, fixed5Hz, nominal20RPM,
  offset54 and evaluation-only Vicon remain selected. Legacy methods preserved.

The original Pi workspace and usual V3 Bash command remain in use. Shared Git
changes are intentional and uncommitted; no commit/push. No physical post-fix
trial was run. Gaussian fill/escape/global approach remains unqualified.
`git diff --check` passed; final receipts are redundantly retained in the Pi
and offline task backup as `validation.tar`.

## Post-fix one-light steering review — 2026-09-30 operator runs

User reported a startup hook and broad arc with one light and Vicon off.
Read-only Pi retrieval verified the closed `20260930T203848_419838Z-1257` and
`20260930T204014_854018Z-1510` bags, plus18 selected current-source hashes.
Evidence:
`/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/single_light_review_20261001T035033Z/REVIEW.md`.
No Pi/source/tuning/build changes or physical launches were made in this review.

Both runs stayed SEARCH, no fills, no input-expiry/fault event, final zero and
operator_stop. Moving durations29.91/80.66s;149/402 sequential valid observations
at4.975/4.978Hz, maximum gap0.251s. Vicon absent; onboard odometry remains the
control input. Pending pose/encoder notices in the second bag are not missing
valid samples. The longer path is a broad partial arc with fitted radius1.71m;
light coordinates were not recorded, so lamp-relative convergence is unknown.

The worker initialization fix is present and averaging participates. A separate
steering discontinuity is now demonstrated: each new observation rebuilds an
unqualified pending-coherence snapshot, dropping the blend to instantaneous
until its exact worker result returns. After15s, distinguishable early commands
5–60ms after receipt favor instantaneous steering (38/38 and137/137);60–180ms
commands favor blended steering (116/116 and284/284). Strict within-observation
comparison finds36/131 clear switches, including3/22 yaw-sign reversals without
another observation. Source and recorded commands support this mechanism;
asynchronous callback order is approximate and worker telemetry was not recorded.
It explains command choppiness, not yet the entire spatial path.

Startup is a distinct issue: zero-initialized washout makes the first direction
depend on current arm phase and absolute brightness. First phases33/54degrees
produce saturated initial commands;49%/61% of first3s command samples request
reverse. Three-rotation averaging qualifies after10.45/11.05s in numerical
replay. Original-filter versus V3 instantaneous arithmetic agrees within1e-15
on identical inputs/dt. Runtime differences remain: baseline forward gain1.0
versus V3's0.5 (both angular gain5); different caps; baseline fixed arm startup
and callback commands versus V3's arbitrary-phase start/20Hz async blending.

Recommended, not authorized/implemented here: retain a still-fresh accepted
direction during replacement computation with original age/context intact;
test startup filter priming separately; then compare baseline and V3 SEARCH
with matched physical constraints. Do not assume gain or calibration changes
will solve the arc, restore arbitrary sleeps, or force Gaussian fill. The
current physical caps0.05/0.30 and all selected settings remain unchanged;
physical Gaussian escape/global-source acceptance remains open.


## Installed steering correction — 2026-09-30 local / 2026-10-01 UTC

User-authorized correction is deployed in the original Pi workspace and
mirrored offline. Evidence and exact commands:
[steering review](/home/mattb/Experiments/GESC-Gaussian/v3/steering_handoff_20261001T040328Z/REVIEW.md).

- Keep the whole accepted rolling direction during pending replacement work,
  only within original0.5s source/receipt ages and unchanged context; current
  fresh yaw reprojects it. Rejected/expired/invalid/context-changed evidence
  cannot persist as accepted steering. Fresh instantaneous fallback recovers.
- Prime the initial washout from the first valid cost; no invented first
  direction, sleep or rotation wait. Next usable change starts control. Do not
  prime at moving objective transitions; preserve original numerical helper.
- Host305 checks and Pi-native114 checks passed, including freshness/reset,
  rejected/late jobs, input recovery, worker failure and localhost ROS Ctrl+C.
  Original goldens pass. Tests needing motion now supply real cost variation.
- Actual installed Pi replay (150 recorded samples/~30s) reduced post15s
  instantaneous/blended switches150→0, blended fraction75.17%→100%;95 jobs,
  no errors, one worker in both. Initial command becomes zero; the next change
  starts control0.2s later. Original age stayed≤0.351s; final zero passed.
  Fixed-input replay is not a new trajectory or proof of lamp convergence.
- Separate deterministic variants on both recordings isolate each fix. Delayed
  worker fallback recovers and keeps original0.5s freshness. Startup priming
  does not eliminate every reverse/rightward command; broad arc remains open.
- Fresh ordinary ros_esc build6.50s; usual Bash build/check-only12.5s. Imported
  source parity and all117 installed Python runtime/7config/12interface matches
  verified after the usual build. Exactly2 of393 source files changed;391
  unchanged. All393 offline hashes/modes match. V1 backup intact, Pi idle.
- Backup: `~/mbuck_backups/steering_handoff_20261001T040328Z`, including original
  two-file source/install archive and intact previous generated ros_esc trees.
  Host and offline copies preserve receipts. Expected old-code failures,
  corrected test-fixture failures and one replay harness error are retained.

Only shared core.py and numerics/rolling.py changed on the Pi. Caps0.05/0.30,
gains0.5/5, affine2, assist off, fixed5Hz, nominal20RPM, offset54, Vicon evaluation
and legacy sources remain selected/unchanged. No device/actuator launch or
firmware/clock changes. No physical or Gazebo behavior test after this fix;
physical fill/escape/global approach remains unqualified. Same operator command.
Shared Git changes remain intentional and uncommitted; no commit/push.


## Post-steering floor run and continuation — 2026-10-01

Current recovery entrypoint: [physical fresh-chat handoff](physical_fresh_chat_handoff.md).
The earlier statement that no post-fix floor run exists is superseded by the
operator's latest one-light run `20260930T211613_989126Z-3555` and its read-only
[review](/home/mattb/Experiments/GESC-Gaussian/v3/physical_runs/post_steering_review_20261001T215339Z/REVIEW.md).

- Closed bag: 382.41 seconds of nonzero commands, SEARCH throughout, no
  candidate or fill, final zero/operator_stop. No internal zero or mid-run
  input-expiry event. Vicon absent. OpenCR path12.88m, net0.61m, broad circuits.
- 1913 valid sequential samples at4.9798Hz, largest gap0.2503s, arm17.07RPM.
  Pending support notices do not represent missing valid sequence numbers.
- Early speed reduction follows smaller commands under weaker sensor variation;
  caps remain0.05/0.30. Recorded-input comparison with the old handoff also
  predicts about1.78cm/s early, versus1.79cm/s observed. Later requests reach
  about4.82cm/s. This is not a controlled physical A/B test.
- Detector replay: zero confirmations; all117 full circle evaluations violate
  both the0.5m fitted-radius limit and60-degree-per-half angular coverage. The
  observation halves are15/18s. Live events show no candidate. Longer total run
  duration or radius relaxation alone cannot resolve both criteria. Having
  one light does not disable first-fill logic.
- Read-only Pi audit:393/393 source hashes match the preceding steering manifest;
  installed core/rolling/worker match source; Pi idle at inspection. No code,
  configuration, build, firmware, device or motion changes in this review.

User subsequently explained that the camping light was battery powered and
faded over time. Its contribution is plausible but not isolated from robot
motion/setup. The user now prioritizes physical-led refinement and simple,
reliable code, without a Gazebo prerequisite. Allow research observation time
when useful; do not turn the ten-minute performance concern into a shutdown
rule. Essential input/process protection remains distinct from research gates.

Next discussion: controlled one-light comparisons with steady illumination,
measured lamp position/orientation and Vicon start pose/heading. Angular gain
5→7.5 and longer detector observation windows were **proposed only**; neither
is authorized as a specific next edit, installed or tested. Current gain is5.
No blanket timeout relaxation is selected. Two-light physical escape remains
unqualified; lab clutter/space limits have restricted tests. User plans to
contact Student Services about reportedly free larger Student Union rooms.

This fresh-chat documentation update changes only repository guides. No Pi
connection or hardware action was made for the handoff. Preserve the intentional
uncommitted deployment changes on `refactor/esc-v3`; no commit/push. Linked
receipts describe the last remote verification, not guaranteed current state.

## Git publication checkpoint — 2026-10-01 local / 2026-10-02 UTC

The user requested cleanup, publication and synchronization of the accumulated
working tree. Pending work was reviewed and preserved, not discarded. Shared
physical support, recoverable escape behavior, worker initialization, steering
handoff/initial priming, observation-only analysis and regression tests are
committed as `3492799`. The accompanying documentation commit preserves the
deployment plan, receipts, floor-run limitations and current continuation guide.
This supersedes earlier dated statements that the shared changes are uncommitted.

External checkpoint:
`/home/mattb/Experiments/GESC-Gaussian/v3/git_closeout_20261002T041241Z`.
It contains the complete pending-file archive and hash/mode manifest, original
Git status/diff/refs, staged changes, validation output and final publication
receipt. Large run artifacts and physical adapter sources remain outside Git.

Validation: after sourcing ROS Humble and this workspace's installation,
`ROS_LOCALHOST_ONLY=1 PYTHONDONTWRITEBYTECODE=1 timeout --signal=INT --kill-after=5s 150s python3 -m pytest -q -p no:cacheprovider ros2_ws/src/ros_esc/test/test_v3*.py ros2_ws/src/ros_esc/test/test_deferred_signal_shutdown.py ros2_ws/src/ros_esc/test/test_gazebo_light_markers.py`
completed with **311 passed in 21.23 seconds**, with 372 existing NumPy matrix
warnings. `git diff --check` and staged whitespace checks pass. Documentation
links and preservation of the runtime bytes are checked in the final receipt.

Publication targets only `origin/refactor/esc-v3`; its local/upstream/remote
hashes and ahead/behind count are retained in `final_receipt.json`. No merge to
main, frozen-ref changes, Pi connection/deployment, hardware action or new
Gazebo trial is part of this Git task. Gain5, physical caps0.05/0.30 and current
detector settings remain selected; proposed tuning is still unimplemented.
Physical Gaussian fill, local escape and global approach remain unqualified.
