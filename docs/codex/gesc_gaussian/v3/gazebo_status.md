# V3 Gazebo pilot status — 2026-09-28

Active: user authorized Gazebo runs after Git cleanup. See [plan](gazebo_plan.md).
Initial source `73d1975`, clean at dispatch, frozen V1/V2 refs preserved.
No physical operations. Evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v3/gazebo_20260928T211359Z`.

## Preflight

- Read AGENTS, current refactor plan/status, usage, architecture, environment
  and software-test guidance. No active Gazebo/algorithm processes found.
- GUI display `:0` available; isolated ROS domain191, localhost only, private
  Gazebo master port11431. Initial disk headroom approximately218GiB.
- Selected source has 5Hz modeled cost, nominal20RPM, physical-target velocity
  caps0.05/0.30. ADC disabled/no noise; this is an idealized integration baseline.
- Next incomplete criterion: actual installed Gazebo startup and base motion.

## Run log

Entries and closed-bag analyses are added as runs finish. Retain each command,
manifest, launch log, exit code and ordinary bag outside Git. No running SQLite
bag will be inspected directly.

### Run01 — prelaunch shell failure

`run01_visible_baseline`: shell `set -u` rejected an unset optional variable in
ROS setup before any graph launched. Exit1; corrected the external dispatch
script to source ROS without nounset. Original attempt remains retained.

### Run02 — failed integrated baseline, preserved

`run02_visible_baseline`: visible Gazebo and Matplotlib launched, nominal180s
wall bound. Stopped with SIGINT after persistent zero commands were diagnosed.
Closed bag has3,228 commands, all zero, no ACTIVE transition, only2 valid
observations and9,972 invalid notices (mostly pose/phase future). Cost4.902Hz,
arm19.976RPM, command20.010Hz wall. The0.0522m odometry drift over159.324s is
not commanded movement. See `pilot_analysis.json` and `live_probe.json`.

Read-only clock probe observed92/92 odometry samples ahead of local `/clock`;
Gazebo published clock at10Hz while odometry arrived around30Hz. Probe RTF
was0.995. Independent ROS topic delivery makes otherwise healthy source stamps
look future to strict callback admission. This is an integrated clock-delivery
failure, not a Gaussian trapping/escape result.

Two separate infrastructure findings:

- Recorder precreated reliable subscriptions before Gazebo's best-effort
  `/clock` publisher appeared; clock recording is absent. RTF is therefore
  available only from the live probe, not reconstructed from that bag.
- `ros2 run` launch wrappers exited without all children receiving SIGINT.
  Seven run-owned leftovers were identified by PID/start identity and exact
  domain/master environment, then stopped. `cleanup.json` confirms none remain.
  Controller STOPPED/finalzero is recorded; this failed stationary run does not
  demonstrate stopping from motion or clean whole-launch shutdown.

### Bounded corrections in progress

- Launch original CLI executables directly using installed package resolution,
  preserving argparse interfaces, so launch owns the process receiving SIGINT.
- Recorder waits for actual publisher discovery before selecting QoS; removes
  `--include-unpublished-topics`. Actual late best-effort clock regression and
  focused profile/recording suite:33PASS,372 existing warnings,7.58s. Receipt
  `recording_launch_tests.log`; no control gate or clock forcing introduced.
- Simulation clock-leading inputs wait boundedly for actual clock delivery,
  retaining source and first-receipt ages. Physical future rejection and core
  0.5s freshness admission remain unchanged. Regression and rerun results follow.

### Run03 — motion observed; Gaussian behavior and clean shutdown failed

Bounded simulation clock delivery is implemented without a new ROS node:125ms
maximum lead and32 records per stream, never consumed until actual `/clock`
catches up. Original stamps/first receipt and steady expiry are preserved;
all queued odometry is retained within bounds. Core admission/math are unchanged.
Focused clock regressions81PASS; first fixture-only failure is retained.
Three packages rebuilt in3.78s; full installed suite213PASS,372 existing warnings,
14.95s. Receipts: `clock_delivery_focused_tests_final.log`,
`clock_correction_build.log`, `clock_correction_full_tests.log`.

`run03_visible_clock_correction` has a360s wall bound plus20s shutdown grace.
Same selected algorithm/profile, GUI/plot/recording enabled. Exact changed source
snapshot/diff/hashes are stored with its manifest. Live read-only probe at
sim38.7–46.7s observed39/39 valid measurements,160 nonzero commands,0.3708m net
translation and RTF0.995. This establishes initial motion only; complete-run
state transitions and recording were subsequently analyzed from the closed bag.

- Full run:1,744 valid observations, no invalid notices,4.902Hz; mean arm19.996RPM,
  RTF0.9953,8.706m path and1.541m net displacement over356.354 simulated seconds.
  ACTIVE at0.2s; caps0.05/0.30 respected. Controller STOPPED/finalzero recorded.
- No candidate, VERIFY, DESIGN, fill or escape occurred. Global closest3.315m;
  local closest0.0049m. This is not Gaussian escape/global-source success.
- Offline detector replay also produced no candidate: circle models passed9
  evaluations but reached only2 consecutive passes of3 required; static and
  oscillation branches never qualified. No source gap in the recorded odometry.
  Keep this failed360s case; do not relax thresholds or extend it into a pass.
- A separate source-level counterexample found that deferred first-receipt
  steady time was also used as current evaluation time. It can falsely skip
  detector or fresh-pose work. This is being corrected independently; replay
  does not establish it as the cause of this run's missing candidate.
- Deadline group SIGINT plus launch forwarding interrupted controller cleanup
  with a repeated signal. Gazebo's `gazebo` wrapper left server/client children;
  exact owned PIDs were stopped and `cleanup.json` confirms none remain. These
  are additional shutdown findings, despite the bag recording a final zero.
- Actual workstation CPU counters during sampled coverage: controller+worker
  about0.153core, adapters0.402, recorder0.0566, liveplot1.009. These exclude
  unsampled startup/exit tails and do not qualify Raspberry Pi headroom.

Receipts: `pilot_analysis.json`, `detector_replay.json`,
`historical_steady_probe.json`, `cpu_analysis.json`, `cleanup.json`.

### Further corrections / next bounded run

- Deferred signal handlers now remain active through V3 finalzero and worker/
  executor cleanup. A real subprocess/DDS regression sends repeated SIGINTs
  during cleanup:3 focused ROS tests PASS6.86s.
- Gazebo launch now owns `gzserver` and `gzclient` directly. Automated timeout
  dispatch will signal only launch (`--foreground`) so launch forwards once.
- Rebuilt3packages in2.26s; installed suite215PASS,372 warnings,16.66s before
  the separate steady-time correction. See `shutdown_correction_*` receipts.
- Next:120s headless recorded recovery case, with exactly one2s pause of the
  isolated simulated cost process after20s wall time. The injector always
  resumes its own verified process; this is a process/data-outage experiment,
  not an Arduino acquisition model. Behavior/cleanup evidence remain pending.

### Run04 — selected interruption recovered; clean headless shutdown

The separate steady-time correction now evaluates freshness at the current
monotonic time while retaining each deferred input's original receipt. Focused
tests: 74 PASS in 1.16 s. Installed suite: **222 PASS**, no skips, 372 existing
warnings, 16.45 s. See `steady_evaluation_tests.log` and
`pre_recovery_full_tests.log`. Exact full command:

```bash
timeout 75s bash -c 'source /opt/ros/humble/setup.bash; source ros2_ws/install/setup.bash; export ROS_LOCALHOST_ONLY=1; python3 -m pytest -q ros2_ws/src/ros_esc/test --basetemp=/home/mattb/Experiments/GESC-Gaussian/v3/gazebo_20260928T211359Z/pre_recovery_full_tests'
```

`run04_cost_pause_recovery`: 120 s headless deadline, nominal 20 RPM, unchanged
algorithm mathematics. Only the verified cost process was suspended for
2.0015 s and resumed; exact PID/start identity and signal times are retained.

- First zero command/WAITING occurred 0.361 s after suspension. After resuming
  the publisher, a valid observation arrived in 0.00161 s and a nonzero command
  in 0.00934 s. These are host signal-marker to **bag receipt** latencies, not
  exact callback execution times. Zero commands persisted for 1.650 s.
- No terminal FAULTED event. The first resumed observation retained 0.238 s
  source-to-receipt age, within the existing 0.5 s expiry. No thresholds changed.
- Odometry moved 1.325 mm during the zero-command interval, including
  deceleration, and 0.369 mm during its final second; then 39.51 mm during the
  first second after resumption. This supports measured stop/restart behavior
  for this selected simulated outage.
- Entire run: 570 valid observations, no invalid notices, 3.638 m path,
  1.693 m net displacement and RTF 0.9976. Final STOPPED/zero recorded; all
  launch processes exited cleanly and the bag closed. No odometry after the
  final zero was recorded, so measured final shutdown stopping is unavailable.
- Expected timeout exit 124 is the planned deadline. This demonstrates
  selected software-outage recovery, not Arduino timing fidelity, Raspberry Pi
  resource headroom, Gaussian escape or physical stopping.

Receipts: `run04_cost_pause_recovery/{run.sh,manifest.json,injection.json,`
`recovery_analysis.json,pilot_analysis.json,cleanup.json,exit_code.txt}`.

### Run05 — moving verification cancelled recoverably; clean visible shutdown

`run05_measured_mean_arm_speed`: visible Gazebo/live plot, fixed 360 s wall
deadline, recording enabled. A retained custom profile changes only the
rotation JSON and descriptive arm RPM to 17.2, approximating the mean measured
in the preserved physical V1 run. Acquisition remains the idealized nominal
5 Hz model, not a calibrated physical sensor. Physical nominal 20 RPM remains
unchanged. Algorithm gains, caps, detector guards and finite deadline are fixed.

The closed bag records 1,743 valid observations, no invalid notices, 4.902 Hz,
mean arm speed 17.194 RPM, RTF 0.9946, 8.707 m path and 1.721 m net displacement.

- Candidate/VERIFY began at simulated 144.3 s. At 152.3 s the candidate was
  cancelled with `verification_approach_timeout`, returning to SEARCH rather
  than terminal failure. It never reached the verification collection radius;
  this exercised moving approach, not complete verification evidence. No
  DESIGN, Gaussian fill, escape or global ranking.
- During those eight seconds, odometry records 0.285 m path and 0.226 m net
  translation. The 163 commands mapped to that interval are all nonzero.
  Fifteen offline windows of at least 0.5 s each all exceed 1 mm displacement
  (minimum 4.736 mm). These offline anchors approximate the actual callback
  anchors; they support moving verification for this selected interval.
- Closest local-source distance 15.9 mm; final distance 299.7 mm. Closest global
  distance 3.279 m. The fixed six-minute case did not demonstrate Gaussian
  escape or global convergence and remains unsuccessful for that behavior.
- STOPPED and final zero recorded; both Gazebo server/client, the live plot,
  algorithm and recorder exited cleanly. Bag metadata finalized, no owned
  processes remained and no extra cleanup signals were required. Only one
  odometry sample followed final zero, insufficient to establish measured
  final stopping. Expected timeout exit 124 records the declared bound.

This is not an isolated causal comparison with Run03: the steady-time and
shutdown fixes also intervened. Run04/05 source hashes match; Run04 has its own
shorter deadline and explicit outage. Candidate emergence cannot be attributed
solely to the RPM change. No thresholds were relaxed.

Receipts: `run05_measured_mean_arm_speed/{manifest.json,pilot_analysis.json,`
`cleanup.json,exit_code.txt}`; closed-bag plots/CSV in `offline_analysis/`.

Offline detector replay found a circle30 endpoint at 144.229 s with persistence
three, consistent with the runtime candidate event at 144.3 s. Using its
inferred center (0.606419, 1.409906), recorded VERIFY distance decreased from
186.3 to 109.1 mm, never entering the selected 80 mm approach radius. Heading
error began at 1.582 rad; yaw changed 2.390 rad over 7.956 s, approximately the
0.30 rad/s cap. This supports a moving-approach/turning-limit explanation for
the eight-second timeout, rather than missing data or a stationary base. The
replay does not reconstruct exact runtime callback admission or directly
observe the unpublished candidate center. See `candidate_approach_replay.json`.

## Next research boundaries

The initial integrated pilots have exercised motion, selected input-outage
recovery, moving candidate cancellation and headless/visible shutdown. They
have **not** established Gaussian filling, escape, global convergence or
physical qualification. The nominal 20 RPM case and measured-mean case remain
separate retained behavioral failures; software corrections do not rewrite
their results.

Before independent delay/backlog/ADC experiments, separate latent field
acquisition from perturbed observed pose/phase. Current cost timing is a
transform-driven throttle (4.902 Hz), with idealized angle/support and no
noise/quantization. Delaying the same pose that generates the field is not an
independent physical odometry-delay model. A 17.2 RPM constant command also
does not represent measured nonuniform servo rotation.

The other bounded research question is whether the retained moving approach
law and fixed eight-second admission are feasible at the physical-target
turning/translation caps. Diagnose that geometry explicitly before a separately
versioned correction; do not simply extend Run05 or loosen its failed gate.
Preserve continuous translation, source freshness and protected physical V1.

### Final source review after Run05

Two bounded integration issues were found in source review, independently of
the retained behavioral failures:

- Distinct source samples sharing a quantized receipt time were conflated by
  the controller's clock buffer duplicate key. Source stamp now owns identity,
  order and source expiry; a separate threshold waits for both source and
  receipt clocks. No early use, invented timestamp or renewed age is allowed.
- A new observation-frame callback precheck ran before stale-input rejection.
  Removed that precheck, restoring core admission order: stale observations
  are discarded; eligible fresh frame conflicts still fault. The existing
  physical pose-frame policy is unchanged.

Focused regressions: **94 PASS**, 1.29 s; receipt
`post_run05_delivery_review_tests.log`. These edits happened after all Run05
processes stopped. Run04/05 retain their exact earlier source snapshots; their
results do not empirically qualify these later edge-case corrections.

## Initial pilot checkpoint / continuation handoff

- Initial Gazebo iteration cycle is complete: prelaunch failure, failed
  stationary baseline, corrected moving baseline, selected outage recovery,
  and visible measured-mean arm-speed case are all retained separately.
- Final installed suite: **228 PASS**, no skips, 372 existing NumPy matrix
  warnings, 16.35 s. Command is the earlier 75 s full-suite invocation with
  `--basetemp` ending in `final_integration_tests`; receipt
  `final_integration_tests.log`. Latest source-only Python changes resolve via
  the verified symlink installation. The last three-package build passed;
  no entrypoint/interface/build dependency changed afterward.
- `git diff --check` passes. Source, tests and this evidence checkpoint are
  committed on `refactor/esc-v3`; the external `integration_checkpoint.json`
  records the resulting commit, final status and frozen-ref checks. No push.
- All Gazebo pilots and tests ended. Run05 cleanup has no owned processes
  remaining. Working physical V1, its fixed 5 Hz firmware/54-degree offset,
  nominal 20 RPM and external physical package are unchanged. No Pi operation.
- V3 remains behaviorally and physically unqualified. The broader model and
  behavior plan remains open. Next incomplete criterion is a truthful,
  independently perturbed acquisition/pose/phase model; retained moving
  approach evidence also needs a separately scoped feasibility correction.
  Do not restart old fixed experiments or relabel their failures.

## Operator clarification

The agent starts, evaluates and terminates automated Gazebo iterations using
their declared finite bounds. The user need not press Ctrl+C in simulation,
though they can interrupt an interactive run. Future physical runs remain
operator-observed: the user presses Ctrl+C at the global source or earlier if
behavior is wrong. Best-source telemetry does not stop a run automatically.
Recoverable data loss should permit automatic recovery; this does not remove
essential motion inhibition when safe control is unavailable. No V3 hardware
deployment or physical test is authorized by these Gazebo results.
