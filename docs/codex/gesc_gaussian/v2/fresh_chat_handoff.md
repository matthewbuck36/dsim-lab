# V2 fresh-chat handoff: 16-run comparison closed with limits

Git closeout: the accepted implementation and retained research record are included in the commit containing the [closeout validation](validation/git_closeout_20260912.md). Earlier references to3369cfc and uncommitted work describe precommit history; use the live branch HEAD for the synchronized source. External closeout receipts preserve exact checks and remote identity.

## Simulation complete; physical integration discussion next

The user explicitly closed Test D simulation work on 2026-09-11 and will use a
fresh chat to discuss integration into the real robot's source and runtime.
This is completion of the user-accepted simulation scope with recorded limits.
Keep Test D's recurrent detector, rolling GESC and moving verification as the
accepted baseline. The 30% target is retired, previous bugs are deferred, and
runtime GOAL_HOLD stays available but is not required for arrival success.
Do not automatically restart simulation studies or the deferred diagnostics.

Begin the next discussion with root `AGENTS.md`, the current plan/status and
[acceptance record](acceptance_retirement_20260911.md), then
[environment parameters](../../../environment_parameters.md) and the always-visible
[Pi instructions](../../../environment_guides/tb3_pi_AGENTS.md) /
[Pi guide](../../../environment_guides/tb3_pi_README.md).
The environment guide describes inherited V1/Phase 09 selections; re-resolve the
actual physical wrapper, launch overrides and JSON before treating them as V2
runtime configuration. This turn did not inspect or modify physical source.

Physical integration needs an explicit compatibility audit of shared algorithm
owners and real sensor/rotation/pose adapters. Use physical algorithm clocks
(`use_sim_time=False`, including supervisor; controller/filter strict
`--use-sim-time False`), preserving shared startup overrides and separate
recorder/watchdog timing. Keep OpenCR `/odom` as algorithm pose, Vicon evaluation
only, physical speed ceilings and Pi-rooted JSON paths.

Changing a clock flag alone does not enable physical Test D. Current
`ros_esc/v2_stream.py:validate_mode_identity` and
`ros_esc/v2_lifecycle.py:validate_verification_evidence_policy` explicitly require
simulation for the selected V2 modes. Also inspect the timekeeper/source-time
contracts and `supervisor_node/centered_verification.py:tracking_controller`,
which checks the selected simulation controller limits. Plan proper physical
support through existing owners rather than merely removing admission checks.

Canonical source is `/home/mattb/dsim-lab/ros2_ws/src`; offline physical source is
`/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src`. Check the exact
`/home/mattb/tb3-pi` mount before interpreting that path. The next-chat request is
discussion/planning, not authorization for transfers, Pi builds, ROS/devices or
motion. No such action occurred here. V1 remains closed; V2 is at `3369cfc` with
substantial uncommitted source and records, so HEAD alone is not the implemented
baseline. Preserve and verify the live checkout before any future edits.

Latest user decision: Test D is accepted as the working baseline; the current
improvement/demonstration work is settled. A/B/C are comparison arms, not pending
repair targets. No further task is scheduled. Revisit deferred issues only if
later evidence or a new user request warrants it. This supersedes the diagnostic
priorities below: defer the
test-related bug investigations; retain existing runtime GOAL_HOLD, optional for
arrival acceptance. Do not automatically resume repairs or remove GOAL_HOLD.
The [five-run review](acceptance_retirement_20260911.md) confirms latest D/A
arrivals at 158.053/210.823 simsec, both 11/11 PASS. All five recent runs arrived;
two earlier D ownership failures remain, while all three D lifecycle counts have
zero terminal fill failures. These observations support the user's deferral,
not a claimed repair. The 30% target stays retired. No new work is scheduled.

Normal-speed baseline A is terminal and passed: arrival210.823simsec, all11 runtime predicates including escape-command ownership PASS, recording/native/outer cleanup/source stability PASS. Session31714 terminal/reaped0. Latest matched pair is A210.823 vsD158.053simsec: D52.770s (25.0305%) less arrival time for these two examples, with the same seed26091152, field, start, controller and normal pacing. No simulation remains running. See [demonstrations](visible_advisor_demos_20260911.md) and `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260912T000449Z_A_nominal_visible_normal_speed/demonstration_report.md`. Earlier failures remain unresolved; no source edit or new scientific qualification.

Latest user-requested D repeat is terminal: arrival158.053simsec, one committed fill, zero cancelled/rejected/expired results, and all11 runtime predicates PASS including escape-command ownership. Recording, native/outer cleanup and source stability PASS; session31884 terminal/reaped0. The observed hesitation was back-and-forth SEARCH motion after escape. See the latest [demonstration review](visible_advisor_demos_20260911.md) and `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260911T235211Z_D_nominal_visible_normal_speed_repeat/post_run_motion_review/report.md`. Conditional quick repair was not triggered because the check passed; no production patch. Earlier intermittent failures remain unresolved. No simulation remains running.

Phone-recording D demonstration is terminal: same nominal seed26091152 at normal Gazebo speed, zero cancelled/rejected/expired fill results, one committed fill98.3simsec, escape completed120.1simsec, global-region arrival164.15simsec. Recording and both cleanup owners pass;10/11 runtime predicates pass, with the existing escape-command ownership failure still present. Session50565 terminal/reaped0; no simulation remains running. See the latest [demonstration review](visible_advisor_demos_20260911.md) and `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260911T234202Z_D_nominal_visible_normal_speed_phone/post_run_fill_review/report.md`. Source unchanged; cancellation cause remains unresolved.

Current authority: [2026-09-11 acceptance retirement and issue triage](acceptance_retirement_20260911.md).
The user accepts the selected 16-run improvement and explicitly retired the
>=30% independent-onset detector-delay target. Do not resume that target or
treat its historical unavailability as a blocker. Begin with D cancellation
diagnosis, then shared C/D command-consistency investigation; D/noise missing
coverage is lower priority and remains a scientific limitation. No bug has
been declared fixed and runtime GOAL_HOLD remains implemented. See the
amendment for initial compact-record findings, validation and the scope boundary.

Earlier transfer and milestone statements below are retained history.

Fresh-chat transfer prepared: [restart prompt](restart_prompt_20260911.md). It prioritizes retained-data diagnosis of D stale-input fill cancellations and post-run command attribution, preserves the A/D presentation and R25 evidence, and distinguishes arrival from full qualification. This turn prepared the handoff only; no diagnostic, algorithm change or new simulation was dispatched.

Current presentation work is terminal: [matched visible A/D demonstrations](visible_advisor_demos_20260911.md). Both reached the global region: A313.450simsec (all11 runtime predicates and recording/cleanup PASS), D150.807simsec (arrival observed, escape-command ownership failed). D took51.888% less arrival time in these two examples at the same configured500Hz playback rate. The first failed D demo remains recorded. No simulation remains running; no new qualification, source change or follow-up run is scheduled.

Earlier D presentation work: [visible D demonstrations](visible_advisor_demos_20260911.md), terminal. First run had three stale-input fill cancellations and an agent diagnostic likely caused a recording database-lock abort. Slower-playback D reached the global region at150.807simsec; recording/cleanup passed, but escape-command ownership failed, so full qualification is withheld. No algorithm changes or A launch. R25 study remains closed unchanged; live reproducibility requires follow-up.

Current closure: R25 full16 study/report COMPLETE WITH LIMITATIONS; no empirical process or automatic follow-up experiment remains. D4/4qualified arrivals and0mandatory stopped acquisitions; strict nominal/delay PASS, noiseEVIDENCE_UNAVAILABLE for one missing direction anchor. Original30%onset target remains unachieved. Final sciencePASS54/integrityPASS202 and material archive693source members/89selected evidence files complete. See [full16 closeout](r25_five_case_completion_handoff.md) and [validation](validation/r25_five_case_completion.md). Archive manifest00a79dbdbab353dc9b1cd75b873f7eacd4c9c88adef6dc36e6c14f7192bc47c6. Original frozen plan/validation-note bytes are archived; their current administrative annotations postdate study closure. V2 at3369cfc, uncommitted task changes, no commit/push or physical action.

Earlier milestone history (retain failures and context; current closure above controls):

R24 material checkpoint COMPLETE: 691 verified source members in 0.951133s at
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/r24_retained_c11_validation_closed_v1/`;
manifest SHA256 `f3edc3a102d975dde7ad8045a2ce2dbe4ec93f1b34476c473d101fdb659d8e38`.
The archive predates this receipt annotation. Context validation and diff check passed.
R25 independent prerequisite review PASS31; only the declared R23 validator/test
and current root plan differ among 836 selected source/runtime/config pins.
Five unused IDs have no matching original run directories. No empirical job is running.

Current active milestone: [R25 five-case completion](r25_five_case_completion_plan.md), ADOPTED. Prepare the existing-owner follow-up and first scientific analysis of retained9–11 before releasing only missing12–16. Original V14 remains immutable; no simulation is running.

Latest completed milestone: [R24 retained C11 validation](r24_retained_c11_validation_handoff.md), COMPLETE. Sole92663terminal0 in43.668513s; all61checksPASS, only2changed and59identical,0warnings. All567pins/rawstats stable. Independent cached review PASS27. Corrected recording view is separately qualified; original C11/V14 failure unchanged. No simulation is running.

Latest completed milestone: [R23 guidance/admission correction](r23_guidance_admission_handoff.md), COMPLETE.
One filtered C11 capture sole56208 terminal0 in2.945496s exposed exactly one
APPROACH3234 then COLLECT3235 at162s; identical candidate/epoch/pose/state,
correct deadlines,0regressions. Independent capture review PASS31.
The existing validator now accepts this equality boundary only with a later first
fully validated same-tick COLLECT witness; all prior state/pose/deadline/sequence
checks remain. No runtime change. Independent source review PASS. Focused sole32887
terminal0:187passed in48.55s,13new cases,0failures/skips,4focused input pins stable.
Validation5628194dc82f6a520b132306871fed28e987941fc533f51da428559b7cb79413.
Exactly validator+existing lifecycle test changed, before bytes and patch retained.
Old C11/V14 failures remain immutable; no full retained revalidation or simulation
ran. Next: bounded existing-owner retained C11 requalification into a NEW evidence
view before completing missing noise/delay conditions with explicit provenance.
Do not rerun complete recordings or reopen V14. No new matrix is scheduled.
Source material archive COMPLETE:688individually verified members in1.002444s;
checkpoints/r23_guidance_admission_closed_v1/manifest.json SHA
91e4e9f3f885a76d24b4ca1c93413a3019064ef15fc33fc92fa90db4431d91f2.
Context/diff checks pass; full research goal remains open.

Latest comparison: [M4v14](m4_v14_handoff.md), CLOSED_INCOMPLETE. Sole40999 is
terminal/reaped1 after2976.356462s (49.61min). Ten complete recordings comprise
four retained V13 development runs and six fresh V14 confirmations; slot11/C noise
is INCOMPLETE and slots12–16 remain UNSTARTED. Seven fresh cases were attempted.
No live acquisition remains; no retries, replacements or post-freeze tuning ran.

Fresh nominal B/D have qualified arrivals286.132/171.882simsec. C nominal has
native arrival135.953 but command-consistency failure; qualified arrival remains
withheld. D nominal passes all11runtime/all9per-run science checks, continuous
acquisition with0mandatory stops, direction median20.500886/P9023.992154deg and
4/4usable eligible targets. C direction also passes with0mandatory stops.
Noise B passes all11runtime predicates and native arrival329.232; its block science
was not run. All three completed A recordings have no arrival.

Slot11 failed v2_lifecycle_contract and cascading algorithm_event_source_causality:
"guidance approach hides an admitted collection". Finalzero/readiness and native/
outer cleanup passed. Native Stage A expired360.026simsec, four verification
attempts, no fill/escape/arrival. Exact offending guidance remains unresolved;
no valid behavioral/scientific outcome is manufactured from this incomplete row.
Diagnosis4aac8942780c1bf7ab8de5a1c1c188e9dd4c6e6dc2aa03535760f84145ad6ae1.

Native nominal summary failed on final hashing; its unavailable result is retained.
Native final report completed7.560121s. Separate cached supplement sole99679 is
terminal/reaped0 in0.805374s,50directpins stable, using saved labels/references
through existing aggregation/rendering owners; no bag/array/model/science reruns.
Supplement receipt434179ac2d85f609376a8eacb9f42b24fcebbbd631e67c39a92b86e6e1ed525d.
All16dispositions,4/12populations,48/144targets, original block failures and C's
withheld qualified arrival remain visible. D noise/delay are unavailable.
Terminal integrity review PASS31:1129small frozen pins stable,28large/array/archive
pins explicitly skipped,308recorded owned process identities absent,0inspection
errors. Review07f3638f511360783237d4417e3642701b14f48d90b30f68186e039bce02e3a7.
This proves closure integrity, not full scientific qualification.

Artifacts under external development/20260911/m4_v14_source_v1/ and
pilot/m4_pilot_v14/. See linked handoff for full16table, exact report/receipt paths,
source validation776PASS, constraints and preserved failures. Archived V14 source/contract/helpers/rootplan and execution/runtime records remain
preserved. The current validator and phase-plan updates belong to R23. No physical,
Pi, snapshot, V1, commit or push changes. Branch remains V2 at3369cfc with task changes.

Full research goal remains open, including original independently labelled30%
latency:0/12observed endpoints,0/6pairs. Next incomplete criterion is a bounded
retained-data diagnosis of C11's rejected guidance/admission ordering through
existing owners before any repair. No new matrix is scheduled. Supplemental
independent review PASS28 in0.179235s, all50pins stable; review
6761417b7e452f4216f232cacdbe91e861a3ac5e8f677d5ebe4a500d132dff26.
Material closeout archive COMPLETE:684individually verified source members in
0.975124s at checkpoints/m4_v14_closed_v1/; manifest
c93292e8121d1c1732cc035c531779e23ddc544ce545bbe6314909b8411ca5c5.
Comparison closeout is complete; full research goal and C11 diagnosis remain open.

Previous milestone: [R22 retained command pairing](r22_readiness_command_pairing_plan.md).
Capture COMPLETE: sole session2295 terminal/reaped0 in6.627780s, exactly one
filtered read each of D and C. All8041 D and7319 C full ordinal pairs match;
D has exactly one zero pair crossing readiness by1.544751ms, no interior fault.
Independent capture review PASS,23 checks and144 stable execution pins.
The conditional offline correction is implemented with historical default
unchanged. Focused session47479 terminal/reaped0:91 tests PASS in1.63s;
independent static source review PASS. Cached session28620 terminal/reaped0 in
6.045165s: D/C both OBSERVED_CONTINUOUS_ACQUISITION, zero mandatory stopped
acquisitions; historical defaults exactly reproduced and C original fields
unchanged. All11 checks and179 execution pins pass. Independent cached result
review PASS39 checks, SHA256
26f04870988809a1160c550098fde24a1b370041b46be8ab5987bf2835b62a89.
R22 COMPLETE. Material archive verified673 source members in0.961338s;
manifest21385d3af80c3818b581475cbc26db3cb7c381d35eaf488fc394558365a34049
at checkpoints/r22_readiness_command_pairing_closed_v1/.
Next: a new prospective comparison reusing these four exposed development
recordings and reserving twelve fresh confirmations.
See [R22 handoff](r22_readiness_command_pairing_handoff.md). No matrix released.

Previous milestone: [M4v13 closeout](m4_v13_handoff.md), CLOSED_INCOMPLETE.
Sole session9544 terminal/reaped1 after1559.394s outer. Four development
acquisitions COMPLETE: A no confirmation/recovery by360s; B/C/D valid recovery
and recorded arrivals314.098/136.567/147.998s. All recordings and cleanup pass.
C/D direction gates PASS: median16.839/12.519 degrees, P9021.181/25.224,
availability3/3 and4/4 eligible targets. GOAL_HOLD is optional.

All four block science jobs completed cleanly, but D motion pairing is unavailable:
7398 commands versus7399 diagnostics within readiness;8041 each in full streams.
C has qualified continuous acquisition and zero mandatory stops. D's original V13 stop count
remains unknown; R22's separate corrected measurement is reported above. The automatic gate withheld all twelve confirmation slots;
no release, retries or replacements. Preserve V13 and its reports unchanged.

Independent terminal cached review PASS:57 checks, all963 source pins stable,
all owned processes absent and cleanup proven. Review SHA256
3d0d70a850546639c4532660badf4d80fac70b45ddcf0ac51c7f2b0254590300.
This is closure integrity, not scientific qualification. See
[execution](validation/m4_v13_execution.md) for exact receipts. Material closure
archive COMPLETE:669verified members, manifest
f393c5ab1786127c84b17fa5a35b4d95e370b616b172b1a3c2e8e4d2d0b21e58. Full research goal remains open, including the unachieved/unavailable
original30% independently labelled basin-entry endpoint. The next useful task is
a separately planned retained-command readiness-boundary diagnosis; no new
simulation or matrix is released. Preserve all old evidence and legacy modes.

Latest completed development: [R21 recurrent trapping verification](r21_recurrent_trapping_plan.md).
The fresh [D02 visible case](r21_visible_d02_plan.md) passed acquisition, full
native analysis, continuous-motion and numerical direction gates. Independent
cached review PASS:34 checks,1.828369s, without scientific reruns. R21 development
is COMPLETE. Full research goal remains open; V13 is closed incomplete as described above.

D02 detected trapping, committed one bounded fill, completed an owned assisted
escape, returned to SEARCH and reached the global region at **197.18 simulation
seconds**, distance **0.499521338 m**. Recording is COMPLETE, all eleven primary
predicates and both cleanup owners pass. The exact recorded pose/Timekeeper join
agrees with the live evaluator. GOAL_HOLD is optional.

Motion is OBSERVED_CONTINUOUS_ACQUISITION with **zero mandatory stopped
acquisitions**. Both verification/design segments have measured positive motion,
complete command pairing and authority. Direction median **23.531 degrees**,
P90 **39.475 degrees**, usable averaging **5/5 eligible informative targets**;
all five improve on instantaneous direction. All 24 scheduled targets remain:
6 observed, 18 unexposed. This is one exposed noisy development case, using the
observed-phase stationary GESC reference; broad robustness is not established.

Acquisition session93267, analysis6585 and reference29000 are terminal/reaped0.
Analysis completed in77.092s outer with exactly two native scans and one captured
BagData; reference completed in7.450s outer. All prepared source/input hashes
remained stable. See [D02 validation](validation/r21_visible_d02.md) for commands,
artifacts, clock basis, support limits and retained source-fixture failure.
All 607 prepared source/helper files remained unchanged through independent review.

D01 separately reached the region at151.897s and passed its cached direction
diagnostic (median23.597/P9029.905 degrees,4/4 eligible). Its fixed-duration
recording failure, partial native analysis and unavailable original motion
remain preserved. D02 is a fresh case with corrected recording configuration
and explicit simulation-publication state durations; it does not rewrite D01.
V12 remains CLOSED_INCOMPLETE:12 acquisitions,9 arrivals,4 unstarted delay slots.

Previous milestone: [R20 local-attraction study](r20_local_attraction_handoff.md),
COMPLETE and independently reviewed; candidate REJECTED. Strong-positive
admission50/128 versus116 required, with0/512 false accepts. All208 focused
checks and three tracking components pass; selected-field admission0/8 noiseless
and0/8 noisy. All three scientific/test jobs are terminal/reaped0. Cached reviews
pass; the first controls-review serialization failure is preserved. New helpers
remain unwired. [Next-method boundary](r20_method_boundary.md): verify actual
pre-intervention trapping without assuming a stationary-field attracting zero.
This was the R20 closure boundary; R21 is now adopted above. The full goal remains incomplete.

Read AGENTS.md, [plan](plan.md), [status](status.md), the
[V12 plan](m4_v12_integrated_comparison_plan.md), and
[V12 closeout](m4_v12_handoff.md). Run the context validator before edits.

## Current work and runtime

Previous milestone: [R19 retained-noise check](r19_retained_noise_handoff.md),
COMPLETE and independently reviewed. Sole scientificsession51515 terminal/reaped0
in3.070531238s:48 valid fits,58 stable execution pins. Under fixed-anchor cost
plus actual recorded noise, C/D noisy direction median/P90 are1.823/13.777 and
3.235/7.481degrees. Frozen admission22/46 and raw verification2/8 leave the
prospective motion-only sufficiency decision FAILED. Full goal remains incomplete.
Next is a prospective method redesign separating full-vector SEARCH confidence
from evidence of a local raw-field well; see handoff and purpose audit. R20 has since been prospectively adopted; see its current milestone above. Material archive receipt follows.

Previous milestone: [R18 crossed cost/design diagnosis](r18_crossed_design_handoff.md).
Scientific job COMPLETE: sole session 43287 terminal/reaped0 in 6.579207011s;
432 fits, 49 stable execution pins, no new model/reference/map/bag calls.
Deleting XY alone leaves large errors; fixed cost with moving XY makes the
R15 linear fit accurate by numerical error limits on all six inputs. Actual
recorded cost with fixed design admits only13/46 targets and2/8 raw verification
supports under R15 linear. Full goal remains incomplete. Independent cached
review PASS; the study is COMPLETE. The next bounded question is fixed-anchor
cost with actual retained noise, as described in the handoff. No R19 fit, runtime
or matrix is released. Material archive receipt follows.

Previous milestone: [R17 spatial harmonic study](r17_spatial_harmonic_plan.md),
adopted prospectively after R16 closure. New unwired spatial H1–H3 fit passes
89 focused/regression cases; source session 19866 is terminal/reaped 0.
Controls session 80109 and retained session 99659 are terminal/reaped 0.
Frozen lambda 0.01 gives 59/64 strong stable and 63/64 strong spatially varying
positive detections, but AR1 and loss-of-signal rejection fail. Retained recorded
admission is 3/46 and every run fails availability; large noiseless moving errors
remain. Study COMPLETE, candidate REJECTED. Both independent cached reviews
PASS. See [R17 handoff](r17_spatial_harmonic_handoff.md) for exact measurements,
limits and the next method/collection question. No runtime is active.
No simulation or matrix is released. Prior completed R16 evidence follows.

Previous completed milestone: [R16 retained noise-free diagnosis](r16_noiseless_diagnosis_handoff.md).
Study COMPLETE; independent cached review PASS.
Sole session 4214 is terminal/reaped 0. All four nominal raw streams
reconstruct to RMS below 5e-15 V. Large moving-fit errors persist without noise,
while fixed-anchor controls give per-run median/P90 errors of 0.09–1.88 / 0.62–6.14
degrees. Projected verification passes 1/8 actual noisy supports, 6/8 noiseless
moving and 8/8 fixed-anchor supports. This isolates a motion-related difference;
it does not establish a corrected continuous-motion method. No runtime is active.
Next work must address motion-dependent angular response and identifiability,
with independent controls and visible integrated development before a matrix.

Previous completed milestone: [R15 reduced harmonic study](r15_reduced_harmonic_handoff.md).
Study COMPLETE; both candidates REJECTED.57 source checks pass; independent
1628-input study finds linear60/64 stronger detections but7/64 quadratic-null
false accepts, quadratic53/64 stronger detections but1/64 quadratic-null accepts.
Retained usability is10/46 linear and6/46 quadratic; every run fails availability.
Only one of eight noisy verification supports passes the projected signal rule.
Both cached independent reviews pass; all three sessions terminal/reaped0.
Source remains unwired. Next work must separate retained model bias from noise
through the R16 existing-model diagnostic reported above.
No simulation or matrix is released; full research goal remains incomplete.

Latest completed milestone: [R14 harmonic method study](r14_harmonic_method_handoff.md).
The study is COMPLETE; the candidate is REJECTED.24 source checks passed, but
strong synthetic detection is26/64 versus90% required, and retained usability is
0/46 original eligible targets. Both independent reviews passed. All eight noisy
verification supports fail angular information. Read the R14 handoff/validation
before new work; preserve the fixed failure and all raw/partial artifacts.
Sessions44490 and21676 are terminal/reaped0. The pure mathematical owner remains
unwired; no simulation or next study is active. Next incomplete criterion is a
prospective method revision addressing motion-model identifiability, uncertainty
in the required GESC output and lost predictive-test power. Independent controls
and a credible bounded visible integrated case must precede another comparison.

Previous completed milestone: [R13 retained profile/direction study](r13_profile_direction_study_handoff.md),
COMPLETE; all measurements and independent reviews passed their declared
evidence checks. Read its handoff and validation before further development.
All three bounded sessions (79372, 93454, 65311) are terminal/reaped0. Do not
repeat the jobs. No simulation is active and no new matrix is released.

All eight noisy attempts reproduce the raw-profile rejection reason; six terminal
diagnostic snapshots match exactly. Every available six/nine-cycle window fails
geometry. The new D/noise reference component passes process qualification with
zero subprocess attempts, while retaining its numerical direction failure.
The fixed-weight projection retains all144 targets and unchanged availability;
C/nominal and D/noise still fail. Longer pooling and blend weight alone are
insufficient. Next incomplete criterion is a prospective controlled noise-aware
method study, then a promising bounded visible integrated case before a matrix.

[R12](r12_measurement_correction_handoff.md) is complete:129 focused checks
passed, import is subprocess-free, and the separate corrected B/noise arrival
time is283.167s. A future experiment must explicitly select the new recorded
arrival binding; old versions do not auto-select it. No method correction is
implemented by R12/R13.

M4v12 remains [CLOSED_INCOMPLETE](m4_v12_handoff.md). Dispatcher53920 exited1
and was reaped after5081.954558s. Twelve recordings completed; delay slots13–16
are permanently UNSTARTED in this version. Acquisition outcomes are nine arrivals
and three nonarrivals: development3/4, confirmation6arrivals/2nonarrivals/4unstarted.
Only scientific blocks0/1 completed. R12/R13 component corrections do not rewrite
that aggregate or qualify the old D/noise process. GOAL_HOLD is optional; global
arrival within the existing evaluator-only0.5m region is sufficient.

R10 remains completed selected detector-response evidence; the original30%
basin-entry latency target remains unavailable. The full research goal remains
incomplete. The user authorizes justified simulation-only method development;
no physical/Pi/snapshot/V1/commit/push action is authorized.

## Durable evidence

R15 material closure: context validator, diff check and existing checkpoint PASS.
Archive `checkpoints/r15_reduced_harmonic_v1/`:621 verified source members,
1.113313046s; manifest SHA256
`ed0a9afa2a38cedb6786001e76b0a788e86b829682663bfc96878dc72c0ae06d`.
This live receipt postdates the immutable archive. Both candidate failures and
all raw/cached measurements retained; no simulation, commit or push performed.

R14 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r14_harmonic_method_v1/` contains616 verified source
members, completed in0.990166671s; manifest SHA256:
`4da7470b0cdff23d384033e88bee6e97a5230b6a2a9329005f51aac6e1b20237`.
This live receipt postdates the immutable archive. Study COMPLETE, candidate
REJECTED; no active simulation, commit or push. Full research goal remains open.

R13 material archive: `checkpoints/r13_profile_direction_study_v1/`,611 verified
source members; manifest `842d44bdb75b4525787b981cc2290e21b91e8c034f6bb9bff35eeb688f97a294`.
R13 is COMPLETE; all three execution sessions are terminal/reaped. R14 subsequently completed and rejected its candidate. Do not repeat R13 or
R14 merely to recover context; a further prospective method revision is needed.

R11 material archive: `checkpoints/r11_retained_diagnosis_v1/`, 603 verified
source members; manifest `5ac24e647705426067b14b9a4b64c1011b73b5dfb1d3cbae583529daf5a7929b`.
All R11 execution sessions are terminal/reaped. The import/arrival correction was subsequently completed by R12; R13/R14
completed retained and controlled method measurements. These historical R11
results remain unchanged.

External root: `/home/mattb/Experiments/GESC-Gaussian/v2/`.

- `pilot/m4_pilot_v12/acquisition/acquisition.json` and all sixteen `slot_N.json`
  receipts retain completed, failed and unstarted dispositions.
- `pilot/m4_pilot_v12/report/report.md` and `result.json` are immutable.
- `development/20260911/m4_v12_source_v1/acquisition_execution_v1.json` is terminal
  exit 1; all known owner PIDs are gone. `closure_runtime_v1.json` records the
  post-exit snapshot; shared ROS daemon PID 24080 remains untouched.
- Source and preparation archives are `checkpoints/m4_v12_source_v1/` and
  `checkpoints/m4_v12_prepared_v1/`. The execution validation records closeout
  reviews and any later material archive.
- [R10 handoff](r10_paired_response_handoff.md) retains same-input detector
  response and finite synthetic controls. [R9 handoff](r9_motion_readiness_handoff.md)
  retains the readiness-scoped motion correction. V11 and all older failures
  remain closed; do not resume their unstarted slots.

## Repository and claim boundaries

Branch `feature/gesc-gaussian-robustness-v2`, HEAD
`3369cfc83a64ff5d8354827fd5310caaf0c8e945`; task changes remain uncommitted.
No commit or push was made. Verify current Git and source before a new iteration.
Pre-closeout navigation copies are retained in
`development/20260911/m4_v12_source_v1/closure_before/`.

Arrival within the evaluator-only 0.5 m global region counts; GOAL_HOLD is optional.
Safety, ownership and completed recovery remain required. C/D share a moving
GESC package; direction is measured against an observed-phase stationary GESC
reference, not a general spatial gradient. The twelve planned confirmation runs
and 144 targets include failures and unavailable measurements. The four development
runs and 48 targets remain separate. Conditions were previously exposed; fresh
seeds do not establish broad robustness or unseen-condition validation.


R16 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r16_noiseless_diagnosis_v1/`: 624 verified source
members in 0.990254893s; manifest SHA256
`e28bbb50514e475fa699d698715885d52339f6da8082b02fa7ff39bf534998bf`.
This live receipt postdates the immutable archive. All retained measurements and
candidate failures remain preserved. No new runtime, commit or push occurred.


R17 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r17_spatial_harmonic_v1/`:628 verified source members
in1.097555136s; manifest SHA256
`26bb7b63c3a09d2a523fcad9e61dd463c0722488b973855eff3a6c27bcec2624`.
This live receipt postdates the immutable archive. All three scientific/source
sessions are terminal/reaped0; both independent cached reviews pass. Candidate
remains REJECTED and unwired. No runtime, commit or push was performed.


R18 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r18_crossed_design_v1/`:631 verified source members
in0.944628473s; manifest SHA256
`ea96665137d8a66062afd3fb067441b386f705a14d3329f2da0d1d24fe2f985b`.
This live receipt postdates the immutable archive. Scientific session43287 is
terminal/reaped0; independent cached review PASS. No runtime or estimator source
changed, and no commit or push occurred. The full goal remains incomplete.


R19 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r19_retained_noise_v1/`:634 verified source members
in0.902510378s; manifest SHA256
`f7dd55bf5acb4eddcce25e51400f72b6ee865de5aa332228679364e4a015212a`.
This live receipt postdates the immutable archive. Sole scientificsession51515
is terminal/reaped0; independent cached review PASS. No estimator/runtime source,
physical/Pi/snapshot/V1, commit or push changes. Full goal remains incomplete.


R20 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r20_local_attraction_v1/` contains642 verified source
members, completed in1.312258089s; manifest SHA256
`2b5a65bb99ee17580004c62cba037dfbd03aab81eb0843788c5dfc37d1143349`.
This live receipt postdates the immutable archive. The study is COMPLETE and its
candidate REJECTED; source helpers remain unwired, full goal OPEN. No runtime,
new matrix, commit or push is active. All inputs, failed review-output attempt,
source/tests, fixed failures and independent reviews are retained.
