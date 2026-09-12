# Visible advisor demonstrations, 2026-09-11

User requested a visible successful D demonstration for screen recording, with A to follow only after a separate request. These are presentation repeats, separate from the closed R25 study. No algorithm parameters, production source, physical workspace, V1, commits or pushes changed. A has not been launched.

## First visible attempt: failed

Artifact root: `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260911T210019Z_D_nominal_visible`.
Run ID: `advisor-demo-D-20260911T210019Z`. Original nominal secondary D case/seed26091152, same selected source/controller and field; GUI and fresh run identity were the only launch-argument differences. Context validation and installed entry-point checks passed. Source comparison confirmed only the already-completed R23 offline validator/test changes from V14.

Three fill cancellations occurred at98.7,165.4,238.1 simulated seconds. Reasons were `stale or invalid state`, then twice `stale or changed epoch context`. No committed fill, escape or arrival was observed. Thus the detector triggered, but activation failed and the robot continued circling. Screen capture used approximately7.3 of12CPU cores; timing pressure is a hypothesis, not a proven sole cause.

The agent queried the actively written SQLite bag to inspect those fill results. The recorder subsequently aborted with `SQLite error (5): database is locked`; this inspection likely caused recorder termination. Do not query an active SQLite recording again; use live ROS subscriptions. The earlier three cancellations preceded that diagnostic and remain a separate runtime problem. Recording is incomplete; both scoped cleanup checks passed. A later playback command found Gazebo already absent, so no pacing change was applied to this run.

Two initial preparation assertions failed before any simulation: one expected the wrong R23 validator filename; another expected a resolved-scenario field absent from the dry-run result. The first whole-suite dry-run exceeded40s while recomputing topology; extracting the unchanged selected D case completed. The final dry-launch comparison showed only GUI and run-ID differences. These were preparation errors, not empirical runs.

## Slower presentation attempt: arrival observed, qualification withheld

Artifact root: `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260911T211235Z_D_nominal_visible_half_speed`.
Run ID: `advisor-demo-D-20260911T211235Z`. Same nominal D algorithm, geometry, start, seed and controller. Gazebo target physics update rate was set to500Hz during startup, preserving physics step size and algorithm parameters. This presentation pacing change is explicitly outside frozen-study equivalence. The pacing command and receipt are retained in `playback_pacing.json`.

State sequence: SEARCH → VERIFY_EXTREMUM → DESIGN_OR_MERGE_FILL → ESCAPE_REPULSE → SEARCH. One fill committed; local recovery and global-region arrival were observed. First live, noninterpolated post-recovery arrival:150.807 simulated seconds at(3.5105651530,3.0004416516),0.4996700570m from global source. GOAL_HOLD was optional. Total bounded wrapper wall time358.296491s. Recording completeness, graceful arrival stop, source stability and native/outer cleanup passed. All Gazebo processes are terminal.

Ten of eleven required runtime predicates pass. `escape_command_ownership` fails with `direct repulse command is not ordinary GESC ownership`; its precise cause has not been diagnosed. Do not promote this observed arrival to a fully qualified behavioral pass or a direction-quality qualification. No new direction analysis ran. The arrival fulfills the visible source-reaching demonstration boundary, while timing reliability and this command-evidence failure remain unresolved. Slower-playback success does not isolate the cause of the first failure.

An intermediate helper attempt at `20260911T211140Z_D_nominal_visible_half_speed` was blocked before spawning the ROS/Gazebo child: its pacing thread violated the existing exclusive subreaper child baseline. It is retained. Pacing was moved to a separate bounded tool process without changing the runner or relaxing cleanup.

## Follow-up boundary

No further D run or A run is scheduled. For the requested later comparison, use original nominal A slot5 from the same V14 contract, secondary geometry and seed26091152; disclose and match presentation pacing. Preserve all failed attempts and original R25 evidence. These demonstration results add a live reproducibility limitation; they do not rewrite the16-run study.

Commands and run products: each root contains `prepared.json`, `command.json`, `run_attempt.py`, the unchanged selected `scenario.yaml`, `scenario_summary.yaml`, and `attempt_result.json`. The successful-arrival view is `demonstration_result.json`; the first failure is `demonstration_failure.json`.

## Subsequently authorized A demonstration

The user explicitly requested A at the same speed as the most recent D presentation. Prepared and dispatched one visible nominal A run: `advisor-demo-A-20260911T213153Z`, root `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260911T213153Z_A_nominal_visible_half_speed/`. The earlier no-A-launch statements above describe the preceding turn.

The original nominal A slot5 and D slot8 match seed26091152, secondary geometry, initial pose, sources, disturbances, frozen controller profile and speed ceilings. A selects `pde_mean_v1` and `stationary_v1`: GESC plus Gaussian with existing detector and stationary direction acquisition. It is a baseline mode in the shared current implementation, not an old Git checkout.

Single-case dry launch passed; only GUI differs from the original A launch. Existing installed bindings and runtime source hashes match the preceding D preparation. GUI and gzserver are visible; a separate bounded `gz physics --update-rate 500` command succeeded, matching D pacing without changing the physics step. No active recording database is read.

Dispatch session90368 owns the existing finite wrapper (1120s internal bound,1125s external INT timeout plus5s kill grace). Original scenario budgets are retained. The process records final results and scoped cleanup under `attempt_result.json` and `scenario_summary.yaml` when it ends; read those files to recover terminal status rather than relaunching. This entry records verified dispatch, not a terminal success or failure. At the same simulation timestamp150.807s, the preceding D had reached the global-source region.

Commands, one-case scenario, source receipts and pacing receipt are retained in the A root. No production algorithm change, new study qualification, physical action, commit or push.

## A terminal outcome and paired presentation result

Session90368 is terminal/reaped0 after692.492776 wall seconds. A succeeded: all11 runtime predicates, recording completeness, native/outer cleanup and source stability pass. State sequence SEARCH → VERIFY_EXTREMUM → DESIGN_OR_MERGE_FILL → ESCAPE_REPULSE → ESCAPE_ASSIST → SEARCH. Live, noninterpolated arrival at313.450simsec, position(3.4390803395,3.0055686314),distance0.498170235m. GOAL_HOLD was not required.

Both presentations reached the global region: A313.450simsec and D150.807simsec, a51.888% reduction in D arrival time. Same nominal field, seed, start, controller limits and500Hz Gazebo target update rate. This is an integrated arrival-time comparison of two presentation examples, not an isolated detector-latency measurement or broad reliability estimate. D's escape-command ownership failure and the earlier failed D attempt remain recorded. A's success does not replace the original frozen nominal A nonarrival.

A's compact result and comparison are saved at `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260911T213153Z_A_nominal_visible_half_speed/demonstration_result.json`. Both GUI/server processes are absent. No additional simulation is scheduled. Context validation, diff check and checkpoint pass; no source/parameter/physical/commit/push change.

## Original-speed D repeat for phone filming: dispatched

The user explicitly requested the original visible D again, at normal Gazebo speed, to film the physical monitor. Artifact root: `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260911T234202Z_D_nominal_visible_normal_speed_phone`. Run ID `advisor-demo-D-20260911T234202Z`, session50565. Same case `m4_v14_holdout_nominal_D_26091152`, seed26091152, field, start, controller and scenario bytes as the first visible D. Every original prepared source hash matched before launch. Only run identity and artifact paths changed. The world has no physics override and no pacing command was issued.

Existing bounded wrapper:1120s internal deadline,1125s external INT timeout plus5s kill grace. Native scenario and outer cleanup remain enabled. Gazebo GUI is visible; recording preflight passed and motion readiness became true at2026-09-11T23:42:29.186839Z. This records dispatch, not a terminal outcome. The wrapper saves `attempt_result.json` and `scenario_summary.yaml`; inspect them after completion rather than relaunching. Live monitoring uses ROS topics and text logs only; no active database query. This repeat leaves the acceptance-retirement amendment, closed R25 results, prior failed demonstrations and pending diagnostics unchanged.

## Original-speed D terminal review: no cancelled or rejected fills

Session50565 is terminal/reaped0, wrapper215.790637wallsec. The same nominal D at normal Gazebo pacing committed one fill98.3simsec, completed escape and resumed SEARCH120.1simsec, and reached the global-source region164.15simsec atdistance0.499775797m. The complete fill-result stream contains PREPARED98.2, ACTIVATED98.3 and ALREADY_ACTIVATED110.6 for the same preparation, with zero CANCELLED/EXPIRED/REJECTED results. Existing lifecycle validation independently records one commit, zero terminal failure results and zero errors. The explicit-stop FAILSAFE164.3s follows arrival shutdown and lies outside the motion interval.

Ten of11 runtime predicates pass. The remaining `escape_command_ownership` failure has the same reason as the slower D: `direct repulse command is not ordinary GESC ownership`. Recording completeness, native/outer cleanup, observed local recovery/arrival and source stability pass. No new numerical direction analysis. The original stale-input cancellations did not recur; source was unchanged, so this is not a claimed bug repair or proof of their cause.

Closed-record review only, through one30s-bounded existing-reader extraction of fill results, states, events and readiness; elapsed0.440906s, exit0. All protected input hashes and bag file size/mtime identities unchanged. Exact scope/script/JSON and readable report: `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260911T234202Z_D_nominal_visible_normal_speed_phone/post_run_fill_review`. No new simulation, source change, commit, push or physical action. Context validation and diff check pass; checkpoint records this terminal review.

## One further original-speed D repeat: dispatched

After reviewing the164.15s arrival, the user explicitly requested one additional visible same-seed run to see whether arrival returns to approximately150simsec. Root: `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260911T235211Z_D_nominal_visible_normal_speed_repeat`; run ID `advisor-demo-D-20260911T235211Z`, session31884. Seed26091152, scenario bytes and all prepared source hashes match the preceding normal-speed D. No field, start, gain, algorithm or pacing changes. Normal fresh-world physics, no update-rate override.150s is a comparison target, not a timeout or guaranteed outcome.

Gazebo GUI visibility and activation verified; recording preflight passed and motion readiness true at2026-09-11T23:52:36.260988Z. Existing1120s internal/1125s external bounds and scoped cleanup retained. This records dispatch only. Read `attempt_result.json` and `scenario_summary.yaml` after completion; no additional repeat is scheduled. No active recording database queried, no source change, no study rerun, physical action, commit or push. Context validation, diff check and checkpoint pass.

## Latest D terminal review: all11 predicates pass

Session31884 terminal/reaped0,207.819173wallsec. Arrival158.053simsec atdistance0.498589024m; one fill98.8simsec, SEARCH resumed120.2simsec. Zero cancelled/expired/rejected fills. All11 native runtime predicates PASS, including escape-command ownership (1047 nonzero ordinary GESC escape samples). Recording, both cleanup owners and source stability PASS; no numerical direction requalification. The user conditionally authorized a small ownership fix if failure recurred; it did not recur, so no production patch was made. Prior failures remain unresolved and preserved.

The apparent pause was ordinary SEARCH motion:120.2–124s travelled0.308m with only0.0498m net displacement, including reverse commands;124–134s mean translational speed0.0365m/s. No second verification or fill, no all-zero linear/angular commands, and zero supervisor contribution in the inspected post-escape intervals. Convergence confirmation was84.1simsec in all three successful D demos; the latest7.246s gap from150.807s comprises1.908s before the escape-completion monitor and5.338s afterward. Exact cause of trajectory variation not isolated; earlier150.807s presentation used500Hz pacing.

Evidence-only review: one40s-bounded filtered existing-reader extraction, session82787 exit0; lifecycle capture1.586565s. Source/input hashes and bag file size/mtime identities unchanged. Scope/script/results/report: `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260911T235211Z_D_nominal_visible_normal_speed_repeat/post_run_motion_review`. No simulation rerun or active bag query; no source/physical/commit/push change. Context/diff checks and checkpoint pass.

## Normal-speed baseline A matched to latest D: dispatched

The user explicitly requested visible Test A at the same speed, seed, initial pose and field as latest D. Root `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260912T000449Z_A_nominal_visible_normal_speed`; run ID `advisor-demo-A-20260912T000449Z`, session31714. Same baseline case `m4_v14_holdout_nominal_A_26091152` and scenario bytes as earlier A. Source hashes unchanged; saved preflight comparison proves shared launch arguments identical to latest D, with only the declared baseline/V2 algorithm selections differing. A uses `pde_mean_v1` and `stationary_v1` with GESC+Gaussian. Seed26091152, same controller and field/start.

Normal fresh-world Gazebo pacing; no500Hz override. GUI visible/activated; recording preflight passed and motion readiness true at2026-09-12T00:05:15.241844Z. Existing1120s internal/1125s external bounds and scoped cleanup retained. Exactly one attempt. This is verified dispatch, not a terminal outcome. Read attempt_result.json and scenario_summary.yaml to recover terminal status. No active database queried, runtime source edit, build, study rerun, physical action, commit or push. Context validation/diff check/checkpoint pass.

## Normal-speed A terminal result and latest matched comparison

Session31714 terminal/reaped0; wrapper259.176917wallsec. A reached the global-source region210.823simsec, distance0.499347574m. All11 required runtime predicates including escape-command ownership PASS; recording, native/outer cleanup and source stability PASS, zero completeness warnings/failures. A completed local recovery through ESCAPE_REPULSE → ESCAPE_ASSIST → SEARCH. Arrival triggered graceful stop; GOAL_HOLD was optional.

Latest matched normal-speed pair: A210.823simsec vsD158.053simsec. D used52.770s less, a25.0305% arrival-time reduction for these two examples. Same seed26091152, field, start, controller limits and normal Gazebo pacing; intentional baseline/V2 algorithm differences only. Both11/11 PASS. Earlier timings/failures and the closed16-run study remain unchanged; this is not a guaranteed speedup or a new numerical direction/detector qualification.

Compact evidence and report: `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260912T000449Z_A_nominal_visible_normal_speed/demonstration_result.json` and `demonstration_report.md` in the same root. Terminal receipts and source hashes verified; no raw bag read or source edit. No process remains running or additional experiment scheduled. Context/diff checks and terminal checkpoint pass; no physical action, commit or push.
