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

## Baseline-speed / no-verification-deadline amendment — active

User requested higher caps matching baseline full-rotation light GESC,
removal of arbitrary approach timing, and restoration of visible lights.
See the [plan amendment](gazebo_plan.md). Evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v3/gazebo_speed_lights_20260928T231502Z`.
Starting commit `58ddec7`, clean tree before edits; no physical operations.

- Archived `gesc_controller_full_rotation_voltage.json` has 0.10 m/s and
  0.50 rad/s caps. Selected V3 controller JSON now matches these. Its gain
  remains 0.5/5, while baseline linear gain is 1.0. The same portable V3
  development profile is available to either environment adapter, but has
  never been deployed to the Pi; its restored V1 source/settings are unchanged.
- Removed 8 s approach, 20 s total verification, and 12 s coverage cancellation,
  plus unused configuration/constants. Fresh moving evidence can take as long
  as needed. The 8 cm entry radius, neighborhood, translation, freshness and
  bounded worker computations remain. The existing 35 s escape policy was
  audited and is unchanged; it is not a FAILSAFE transition.
- Light spawning was omitted in refactor `73d1975`: the XML spawn actions were
  removed without replacements in the Python launch. Original SDF and modeled
  field were preserved. Restored one-shot Gazebo spawners use positions directly
  from selected light-cost JSON; acoustic fields do not gain fictitious lights.
  No persistent observer/control node or duplicated source configuration added.
- Focused deadline tests: 67 PASS, 1.49 s. Light tests: 5 PASS, 0.13 s; earlier
  fixture naming errors retained. Build: all three packages PASS, 2.21 s.
  Installed full suite: **236 PASS**, no skips, 372 existing warnings, 16.59 s.
  Receipts: `approach_deadline_tests.log`, `light_marker_test_receipt.json`,
  `build.log`, `installed_tests.log`. Full test command is the 75 s installed
  invocation used above, with `--basetemp` at this root's `installed_tests`.
- Run06 active: GUI/live plot/recording, nominal 20 RPM, selected 5 Hz and
  600 s wall bound plus 20 s shutdown grace. Exact manifest, changed-source
  archive, source diff, archived baseline JSON and selected controller/cost
  JSON are retained under `run06_baseline_caps_no_verification_deadline`.
  This is a multi-change development pilot, not isolated speed attribution.
- Both `manual_light_1` and `manual_light_2` spawned successfully. Read-only
  Gazebo model poses match (0.574025, 1.38582, 0) and (3.5, 3.5, 0); original
  noncolliding marker visible in `gazebo_lights.png`. Full behavior pending.

### Run06 outcome — fill, measured escape and stronger-source approach observed

The agent interrupted the run after observing approximately one minute near
the stronger source, rather than waiting for the maximum 600 s budget.
`operator_stop.json` records the exact launch PID/start identity and SIGINT.
This observational stop was not a predeclared statistical convergence gate.
Exit 0; bag closed; all owned processes ended cleanly. The separate read-only
event echo was also stopped. `cleanup.json` records no remaining graph process.

Closed bag chronology (`pilot_analysis.json`):

| Simulated time | Observed transition |
| --- | --- |
| 78.7 s | Candidate confirmed; moving VERIFY |
| 89.8 s | DESIGN, 41 source evidence samples |
| 90.0 s | Fill 1 committed; ESCAPE begins |
| 93.9 s | Radial-progress stall invokes existing escape assistance |
| 108.8 s | `escape_complete` |
| 109.0 s | Fresh observation applies return to SEARCH |
| 217.1–233.2 s | Another moving verification/ranking, then SEARCH |
| 269.3 and 323.4 s | Further candidate ranking returns to SEARCH |
| 349.4 s | Agent SIGINT; STOPPED/final zero |

- Fill center (0.657987, 1.427387), about 9.37 cm from the configured local
  source. Amplitude 0.1, principal widths 0.5062 m, exit radius 1.3668 m,
  fitted sample count 30. This is an actual committed fill, not a proposal.
- First VERIFY lasted 11.1 s with 0.366 m measured path; 21 offline translation
  windows all exceeded 1 mm (minimum 8.86 mm). DESIGN lasted 0.2 s, with
  3.25 mm measured translation over its recorded 0.17 s odometry segment.
  Neither state had zero commands. Short DESIGN cannot support a full 0.5 s
  translation window; report that evidence limit explicitly.
- Escape completed after 18.8 s, before the then-active 35 s deadline. Its
  outcome was `escape_complete`, not `escape_timeout`; assistance was used.
- Whole run: 14.951 m path, 4.803 m net displacement; 1,710 valid observations,
  no invalid notices; 4.902 Hz cost, 19.985 RPM mean arm, RTF 0.9946. Recorded
  commands respect the selected 0.10/0.50 caps.
- Closest stronger-source distance 0.865 mm at 241.318 s; final distance
  146.4 mm. A finite live interval 228.262–287.966 s stayed near it while
  moving. No `best_source` event occurred; physical observation/agent stopping
  is separate from internal source ranking or automatic goal hold.
- Final zero/STOPPED and process shutdown are confirmed, but no odometry after
  the final zero was recorded. Actual final stationary duration is unavailable.

This selected Gazebo case now demonstrates Gaussian filling, assisted escape,
return to SEARCH and arrival near the stronger source. It does not establish
general robustness, independent effect of each change, a faithful Arduino/
servo/timing model, or physical qualification. The previous failed cases remain
unchanged. Closed-bag plots/CSV are in `offline_analysis/`.

### Remaining elapsed escape cutoff removed after Run06

Further source audit confirmed that ESCAPE's 35 s return-to-SEARCH transition
and the coupled 35 s affine-age cutoff were behavioral policies, not freshness
or command-authority requirements. The user's general instruction applies to
both. They are removed from the selected V3 core; generic affine helper defaults
and mathematical decay remain unchanged. Escape now waits for measured stable
exit, actual control invalidity or operator interruption. Existing stalled-
progress assistance and its measurement windows remain.

Run06 predates this final edit; its escape finished at 18.8 s, so neither removed
cutoff had fired in that case. Later long-escape regressions are separate evidence
and do not rewrite Run06's source snapshot. Final test results follow below.

### Spatial corroboration and final checkpoint

`run06_baseline_caps_no_verification_deadline/outcome_geometry.json` supplies
additional independent odometry measurements:

- Exit radius 1.36677 m was crossed at 107.630 s. Replaying the retained
  progress tracker reaches stable exit at 108.650 s after 1.020 s outside,
  with 0.30071 m radial gain over its 3 s window. This corroborates the runtime
  `escape_complete` event at 108.8 s; the exact callback subset is not replayed.
- ESCAPE has 384 mapped commands with no zero translation/turn-only samples.
  All 37 offline translation windows exceed 1 mm, minimum 5.187 mm. Thus this
  case preserves observed translation during VERIFY, short DESIGN and ESCAPE.
- First stronger-source distance crossings: 0.15 m at 220.884 s, 0.10 m at
  221.870 s. These are descriptive measurements, not predeclared acceptance
  thresholds. Strict internal source ranking remains uncorroborated because
  no `best_source` event occurred.
- Replayed candidate center (0.621410, 1.397905); recorded path first enters
  its 8 cm radius at 83.184 s, 4.484 s after the candidate event. The old
  eight-second approach limit therefore would not demonstrably bind this
  higher-cap path. Its improvement cannot be credited solely to timer removal.

After the final escape-policy edit, focused core/numerics/worker regressions:
**71 PASS**, 1.90 s (`escape_deadline_tests.log`). The installed full suite:
**240 PASS**, no skips, 372 existing NumPy matrix warnings, 17.00 s
(`final_installed_tests.log`, artifacts `final_installed_tests/`). Exact command:

```bash
timeout 75s bash -c 'source /opt/ros/humble/setup.bash; source ros2_ws/install/setup.bash; export ROS_LOCALHOST_ONLY=1; python3 -m pytest -q ros2_ws/src/ros_esc/test --basetemp=/home/mattb/Experiments/GESC-Gaussian/v3/gazebo_speed_lights_20260928T231502Z/final_installed_tests'
```

Tests retain a valid moving candidate/escape beyond the old deadlines, then
admit later real evidence/spatial exit, and verify that stale inputs, operator
stop and integrity faults still remove motion/escape authority. Generic affine
defaults/decay and finite numerical budgets remain intact. The symlink install
resolves current Python source; no build dependency/interface changed after
the successful three-package build.

The user-requested speed, deadline and light restoration changes are complete
for this iteration. `git diff --check` passes; the bounded source/test/doc
checkpoint is committed on `refactor/esc-v3`, with final Git status and unchanged
frozen refs recorded in external `checkpoint.json`. No push or physical action.
All runs/tests/temporary observers have ended. Broader V3 qualification remains
open: realistic acquisition/serial/servo/pose timing, noise and load, repeatability,
and internal ranking still need separate evidence. Preserve working physical V1.

## Direct-assistance-disabled pilot — selected-case success

User authorized testing V3 without direct heading assistance on 2026-09-28;
see the new plan amendment. Starting HEAD `8b7c383`, clean tree and no active
Gazebo/control/recording processes. Evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v3/escape_no_assist_20260929T005416Z`.
This is one selected 5 Hz/20 RPM pilot, preserving affine magnitude 0.5,
gains 0.5/5, caps 0.10/0.50, field and start. The 15 s fallback-window and
shorter-distance suggestions are conditional future comparisons, not applied.
No physical operation is included.

- Implemented `controller.json` parameter `direct_escape_assistance_enabled`.
  Selected V3 sets false; omitted values retain true for older comparisons.
  Only the stalled-progress transition to direct commands is gated. Both
  selections preserve the objective, measured exit and stopping conditions.
- Focused core/profile/ROS-boundary tests: 115 PASS, 2.64 s. Existing prolonged
  escape/late spatial exit and stop tests now cover both selections; disabled
  mode proves commands still come from GESC while progress is stalled.
- Fresh installed build: all three packages PASS, 2.34 s. Installed suite:
  249 PASS, no skips, 372 existing warnings, 17.40 s. Exact invocations/results:
  `no_assist_focused_receipt.json`, `build.log`, `installed_tests.log` at the
  evidence root. Independent source/install review found no blocker.
- Visible run started with GUI, automatic Matplotlib and ordinary bag recording.
  Manifest pins 215 source files, selected config, source diff and prior HEAD.
  Tool session80810, exact launch identity in `started.json`; maximum600 s
  wall plus20 s shutdown grace. Closed results follow; no active bag was inspected.

The agent sent SIGINT to the verified launch PID after sustained observed
stronger-source proximity (`live_probe_03.json`, `operator_stop.json`). This
was an observation stop, not statistical convergence or an automatic goal gate.
Session80810 exited0. The bag finalized, every runtime process has a clean-exit
receipt, no SIGTERM/SIGKILL escalation occurred, and no domain191 process remains.
Matplotlib emitted a KeyboardInterrupt traceback during SIGINT, then exited
cleanly; there was no pre-stop traceback. All215 source pins stayed unchanged.
See `cleanup.json` and `shutdown_review.json`.

Closed bag: `bags/20260929T005716.079166Z-47151`. Existing installed ordinary-bag
analysis generated `analysis/trajectory.png`, `signals.png`, `summary.json`
and CSVs. Existing external `analyze_pilot.py` used the captured controller/cost
JSON explicitly; exact output is `pilot_analysis.json` with no decode errors.

| Simulated time | Recorded behavior |
| --- | --- |
| 78.5 s | Moving VERIFY begins |
| 94.1 s | DESIGN begins, 40 evidence samples |
| 94.3 s | One Gaussian committed; ESCAPE begins |
| 116.1 s | Measured `escape_complete` |
| 116.3 s | Next real sample applies return to SEARCH |
| 194.4–206.5 s | Moving candidate verification/ranking; return to SEARCH |
| 236.9 s | Agent SIGINT; STOPPED and final zero |

- **Zero direct-assistance events.** All444 mapped ESCAPE commands have nonzero
  translation; no turn-only command. ESCAPE measured2.001 m path and1.601 m net
  displacement. Both VERIFY intervals have nonzero commanded translation and
  all0.5 s measured-motion screens exceed1 mm. DESIGN measured5.48 mm path;
  its0.2 s duration cannot support a full0.5 s motion screen.
- Actual1160 valid observations at4.90196 Hz, no invalid notices or source
  gaps above0.5 s. Measured mean arm19.9954 RPM. Selected gains/caps and affine
  magnitude0.5 remained unchanged; Gaussian amplitude0.1, widths0.5062 m.
- Final recorded stronger-source distance22.38 mm. Final zero is present,
  but no subsequent odometry proves a stationary interval after that command.
  No `best_source` event occurred; physical/internal ranking is not qualified.

`outcome_geometry.json` independently corroborates measured exit: the1.36677 m
radius was crossed114.914 s, offline stable exit115.934 s, and the recorded
completion at116.1 s has nearest-pose radius1.47321 m and0.28185 m outward
progress over3 s. This uses recorded odometry, not the exact callback subset.
The old3 s/5 cm stall rule first flags this same trajectory at98.322 s
(4.903 cm progress), yet continued GESC completed escape. A short stall therefore
does not establish that direct assistance is necessary.

The event-receipt interval contains442 escape commands (the earlier clock-mapped
interval includes444 boundary samples); both methods find no zero translation.
There are25 signed command reversals. Commands spend84.16% at the linear cap and
64.71% at the angular cap, so simply increasing affine magnitude need not create
more useful motion. All43 half-second odometry windows exceed1 mm, minimum6.45 mm.
First stronger-source distance crossings are0.5 m at145.276 s,0.15 m at197.840 s,
and0.10 m at199.132 s, remaining inside each afterward to236.940 s. These are
descriptive thresholds, not a new statistical convergence criterion.

This case demonstrates escape through Gaussian-plus-affine GESC at nominal5 Hz
without direct heading assistance. It does not establish broad robustness,
causal sampling-rate superiority, identical pre-escape trajectories across
repeats, or physical qualification. Higher affine magnitude and the proposed
15 s/shorter-distance fallback are not needed for this observed outcome and
remain unapplied. Keep direct assistance disabled for subsequent V3 studies;
retain the selectable historical fallback and all earlier failed evidence.

## Tenfold affine-slope pilot — selected-case success

User requested one exploratory run with a much larger affine slope and direct
assistance off. Starting clean HEAD `240834c`; no Gazebo or recording active.
Evidence root: `/home/mattb/Experiments/GESC-Gaussian/v3/affine_10x_20260929T011129Z`.
The external custom profile selects 5.0 versus retained baseline 0.5;
ordinary V3 defaults remain unchanged. All other selected settings are preserved.
See the plan amendment; no Pi operations.

- `escape_affine_magnitude` now passes through the existing controller JSON,
  profile resolver and V3 node to the core. Default/built-in 0.5; only this
  external custom profile selects 5.0. The direction, decay, objective weights,
  exit criteria, caps/gains and direct-assistance setting remain unchanged.
- Focused tests: 126 PASS, no skips, 372 existing warnings, 2.63 s. Initial 125/1
  result was a new test's NumPy array-equality assertion; corrected comparator
  without runtime changes, retaining both logs and `affine_focused_receipt.json`.
- Three-package installed build passed in 2.19 s. Installed resolution and independent
  review confirm the external 5.0 and built-in 0.5 selections, both assistance
  false. `comparison_preflight.json` confirms all other controller fields and
  cost/rotation configuration match the preceding no-assist run.
- Exactly one visible Gazebo run: tool session 84326, recorded launch PID/start
  identity in `started.json`, maximum 600 s wall plus 20 s grace. `manifest.json`
  pins 215 runtime files and six external configuration files. GUI, live plot
  and bag enabled. No active SQLite inspection; all analysis used the closed bag.

The agent sent SIGINT after sustained observed stronger-source proximity,
checking launch PID/start identity first (`operator_stop.json`). This was an
observation stop, not statistical convergence. Session 84326 exited 0; all
runtime nodes exited cleanly, recording finalized, no tracebacks or escalation,
and no domain 191 processes remained. Runtime source and external configuration
pins were unchanged. See `cleanup.json` and `launch.log`.

Closed bag: `bags/20260929T011459.310299Z-50159`. The installed ordinary-bag
analyzer produced `analysis/trajectory.png`, `signals.png`, `summary.json` and
CSVs. Its exact invocation was:

```bash
timeout 120s bash -c 'source /opt/ros/humble/setup.bash; source ros2_ws/install/setup.bash; ros2 run ros_esc analyze_bag /home/mattb/Experiments/GESC-Gaussian/v3/affine_10x_20260929T011129Z/bags/20260929T011459.310299Z-50159 --output /home/mattb/Experiments/GESC-Gaussian/v3/affine_10x_20260929T011129Z/analysis --csv'
```

Existing offline pilot/geometry analysis used the captured controller/cost
configuration. Scripts, logs and results are retained beside `comparison.json`
and `comparison.md`; no decode errors. The focused test command and source
hashes are in `affine_focused_receipt.json`. The full suite was not rerun for
this bounded coefficient change; the preceding 249-test result belongs to the
previous checkpoint, not this one.

| Simulated time | Recorded behavior |
| --- | --- |
| 276.4 s | First candidate admitted; moving VERIFY begins |
| 279.3 s | DESIGN begins |
| 279.6 s | One Gaussian committed; ESCAPE begins |
| 300.0 s | Measured `escape_complete`; return to SEARCH |
| 384.1–397.3 s | Moving candidate verification/ranking; return to SEARCH |
| 413.1 s | Agent SIGINT; STOPPED and final zero |

| Escape metric | Previous magnitude 0.5 | Magnitude 5.0 |
| --- | ---: | ---: |
| Start to recorded completion | 21.8 s | 20.4 s |
| Measured path | 2.001 m | 1.880 m |
| Linear commands at cap | 84.16% | 96.11% |
| Angular commands at cap | 64.71% | 95.62% |
| Signed linear-command reversals | 25 | 27 |
| Reversals per ESCAPE event second | 1.136 | 1.324 |
| Returned SEARCH to first within 0.5 m of global source | 28.976 s | 25.746 s |

Reversal rates use start-to-SEARCH event intervals (22.0 s versus 20.4 s),
while completion elapsed uses the actual `escape_complete` event. Both runs
have zero direct-assistance events and no zero-translation/turn-only commands
during escape. In the new run, all 39 half-second measured escape-displacement
screens exceed 1 mm, minimum 2.57 mm; VERIFY and DESIGN also translated.
Signed command reversals remain ordinary GESC behavior, not direct assistance.

Recorded odometry corroborates the 1.36677 m escape radius: first crossing
298.886 s, offline stable exit 299.906 s, runtime completion 300.0 s with
nearest-pose radius 1.47592 m and 0.28910 m radial progress over three seconds.
This is an offline geometry check, not an exact callback-subset replay.

Actual 2024 valid observations at 4.90196 Hz, mean arm 19.9957 RPM, no invalid
observations, source gaps above 0.5 s, duplicate stamps or regressions. First
within 0.5 m of the stronger source at 325.746 s and within 0.10 m at 389.190 s;
remained inside each afterward through the final recorded pose at 413.126 s.
Final distance 0.08455 m, closest 0.05064 m. These are descriptive thresholds;
no `best_source` event occurred. Final zero is recorded, but the sole subsequent
odometry receipt followed it by only about 62 microseconds, insufficient to prove
a measured stationary interval.

The conspicuous longer initial circling preceded affine activation: first
candidate 276.4 s versus 78.5 s, with no earlier candidate, cancellation or
post-startup WAITING_INPUT. The affine term is applied only on ESCAPE entry;
the delay is in SEARCH/detector admission, not evidence of stronger affine
impeding verification. Its deeper cause was not isolated. Fill centers differ
by 0.115 m, retained fit samples 40 versus 30, and fit condition/residual differ;
amplitude 0.1 and width 0.506211 m match. Therefore this single pair cannot
isolate a general performance advantage from the coefficient alone.

The tenfold slope yielded much more command clipping and only a small observed
escape-time reduction. Keep the ordinary profile at 0.5 with direct assistance
off; the 5.0 experiment remains externally reproducible. Exactly one run was
performed. No further tests, Pi changes or physical qualification are implied.
The bounded source/test/documentation checkpoint is committed on `refactor/esc-v3`;
external `checkpoint.json` records clean Git state and unchanged frozen refs.

## Selected affine slope 2.0 — selected-case escape and global approach

The user selected 2.0 and authorized exactly one more simulation run, retaining
direct assistance off. This updates the selected development profile; the
omitted-field compatibility default remains 0.5. Starting clean HEAD `a3383f0`,
no active Gazebo/recording processes. Evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v3/affine_2_20260929T013558Z`.

Only the controller JSON magnitude and two selected-profile test expectations
changed; no runtime algorithm code changed. Focused core/profile/node tests:
126 PASS, no skips, 372 existing warnings, 2.51 s. Three-package installed
build PASS in 2.22 s. Exact commands and configuration comparison: `validation.json`;
logs `focused_tests.log`, `build.log`. Installed and captured custom profiles
both select 2.0/assistance false, all other settings match the previous run.

Exactly one GUI/live-plot/recorded run started, tool session 73254, launch
PID/start identity in `started.json`. Outer bound 600 s wall plus 20 s shutdown
grace. Manifest pins 215 runtime files and six external configurations.
The agent stopped by SIGINT after sustained observed stronger-source vicinity;
the live trace was still orbiting about 0.21–0.33 m from the source. This is an
observation stop, not proof of source-center convergence. Launch PID/start/argv
were checked before signaling (`operator_stop.json`). Session 73254 exited 0.

Closed bag: `bags/20260929T013734.407314Z-52815`. Recording finalized; all runtime
nodes exited cleanly, no domain 191 processes remained, and all source/config
pins matched. No pre-stop traceback. Matplotlib/Tkinter emitted KeyboardInterrupt
during SIGINT and then exited cleanly. No SIGTERM/SIGKILL escalation: the generic
`signal_handler(SIGINT/SIGTERM)` label is not a sent SIGTERM. `cleanup.json`
retains the distinction. No physical operations or additional simulation runs.

The installed ordinary-bag analyzer completed with exit 0, producing trajectory,
signals, summary and CSVs in `analysis/`. Exact invocation:

```bash
timeout 120s bash -c 'source /opt/ros/humble/setup.bash; source ros2_ws/install/setup.bash; ros2 run ros_esc analyze_bag /home/mattb/Experiments/GESC-Gaussian/v3/affine_2_20260929T013558Z/bags/20260929T013734.407314Z-52815 --output /home/mattb/Experiments/GESC-Gaussian/v3/affine_2_20260929T013558Z/analysis --csv'
```

Closed-recording analysis corrects the last live-probe impression: the robot
moved inward after that probe and ended 0.023327 m from the stronger source.
It remained within 0.10 m for its final 21.352 s. No active bag was inspected.
The user then clarified that a roughly 20–30 cm global-source orbit is already
sufficiently close for the current testing goal. This run met that observed
arrival goal before its later inward approach; exact-center convergence is not
required. Record this preference for subsequent tests without adding a runtime
arrival gate or changing historical measurements.

| Simulated time | Recorded behavior |
| --- | --- |
| 144.7 s | First candidate admitted; moving VERIFY |
| 149.9 s | DESIGN, 46 evidence samples |
| 150.2 s | One fill committed; ESCAPE |
| 172.8 s | Measured `escape_complete` |
| 173.0 s | Return to SEARCH |
| 204.389 s | First within 0.5 m of stronger source, remaining inside afterward |
| 293.1–306.2 s | Moving verification/ranking near stronger source, then SEARCH |
| 297.991 s | First within 0.10 m, remaining inside afterward |
| 319.3 s | SIGINT; STOPPED and final zero |

| Escape metric | Magnitude 0.5 | Selected 2.0 | Magnitude 5.0 |
| --- | ---: | ---: | ---: |
| Start to completion | 21.8 s | 22.6 s | 20.4 s |
| Measured path | 2.001 m | 2.097 m | 1.880 m |
| Linear commands at cap | 84.16% | 92.79% | 96.11% |
| Angular commands at cap | 64.71% | 91.27% | 95.62% |
| Signed linear-command reversals | 25 | 32 | 27 |

Selected 2.0 produced the user's preferred higher saturation while still
escaping without direct assistance. It did not escape faster in this one
comparison. All three are single executions with different pre-escape histories
and fill centers; neither monotonic performance nor physical suitability is
established. First candidate times 78.5 / 144.7 / 276.4 s all precede affine
activation; the underlying detector-admission variability remains unresolved.

In the new run, all 458 event-bounded escape commands have nonzero translation,
with no turn-only commands or direct-assistance events. Measured escape path
2.09696 m, net displacement 1.43926 m; all 44 half-second displacement screens
exceed 1 mm, minimum 4.487 mm. There are 32 signed reversals over the 22.8 s
ESCAPE-to-SEARCH interval (1.4035/s); these are command changes, not measured
stops. Moving verification/design also translated. Offline geometry corroborates
the 1.36677 m exit radius: crossing 171.647 s, stable exit 172.667 s; radius
1.47917 m near runtime completion with 0.28447 m three-second radial progress.
This is recorded-odometry support, not an exact callback replay.

Actual 1563 valid observations at 4.90196 Hz; no invalid observations, duplicate
or regressing source stamps. Mean observed arm 19.9795 RPM. No `best_source`
event; proximity is descriptive, not broad convergence or internal-ranking
qualification. Final zero is recorded, but only one odometry receipt follows
about 9.67 ms later, insufficient to establish a measured stopping interval.

Detailed metrics, reproducible scripts and three-way trajectory comparison are
retained in the evidence root (`pilot_analysis.json`, `outcome_geometry.json`,
comparison report/JSON and `trajectory_comparison.png`). The selected profile
remains magnitude 2.0 with direct assistance off. This evening's authorized
single run is complete; no further simulation was launched. Focused checks,
build and diff review passed; the bounded checkpoint is committed on
`refactor/esc-v3`, with clean Git state/frozen refs in external `checkpoint.json`.
Working physical V1 and broader V3 qualification boundaries remain unchanged.
