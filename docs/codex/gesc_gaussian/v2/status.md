# GESC Gaussian V2 Live Status

Git closeout: the accepted implementation and retained research record are included in the commit containing the [closeout validation](validation/git_closeout_20260912.md). Earlier references to3369cfc and uncommitted work describe precommit history; use the live branch HEAD for the synchronized source. External closeout receipts preserve exact checks and remote identity.

**Simulation scope COMPLETE by user acceptance, 2026-09-11.** Test D is the
accepted simulation baseline. Next discussion: physical source integration and
compatibility planning, using the [fresh-chat handoff](fresh_chat_handoff.md).
No new simulation, deferred-bug investigation or physical operation is scheduled.
Physical implementation/validation and the recorded broader research limitations
are not claimed complete.

Latest user decision: Test D is accepted as the working baseline and the current
practical improvement/demonstration work is settled. A/B/C are comparison arms;
repairing their historical failures is not required. Defer the earlier
intermittent issues unless later evidence or a new user request warrants review.
Defer the test-related bug investigations and retain
runtime GOAL_HOLD with optional arrival acceptance. The 30% target stays retired.
The [five-run review and updated decision](acceptance_retirement_20260911.md)
confirm all five arrivals, latest D/A both 11/11 PASS, and zero moving-fill
terminal failures in the three D runs; two earlier D ownership failures remain.
Earlier diagnostic priorities below are superseded. No bug is declared repaired,
no GOAL_HOLD removal is planned, and no investigation or experiment is scheduled.

Normal-speed baseline A is terminal and passed: arrival210.823simsec, all11 runtime predicates including escape-command ownership PASS, recording/native/outer cleanup/source stability PASS. Session31714 terminal/reaped0. Latest matched pair is A210.823 vsD158.053simsec: D52.770s (25.0305%) less arrival time for these two examples, with the same seed26091152, field, start, controller and normal pacing. No simulation remains running. See [demonstrations](visible_advisor_demos_20260911.md) and `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260912T000449Z_A_nominal_visible_normal_speed/demonstration_report.md`. Earlier failures remain unresolved; no source edit or new scientific qualification.

Latest user-requested D repeat is terminal: arrival158.053simsec, one committed fill, zero cancelled/rejected/expired results, and all11 runtime predicates PASS including escape-command ownership. Recording, native/outer cleanup and source stability PASS; session31884 terminal/reaped0. The observed hesitation was back-and-forth SEARCH motion after escape. See the latest [demonstration review](visible_advisor_demos_20260911.md) and `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260911T235211Z_D_nominal_visible_normal_speed_repeat/post_run_motion_review/report.md`. Conditional quick repair was not triggered because the check passed; no production patch. Earlier intermittent failures remain unresolved. No simulation remains running.

Phone-recording D demonstration is terminal: same nominal seed26091152 at normal Gazebo speed, zero cancelled/rejected/expired fill results, one committed fill98.3simsec, escape completed120.1simsec, global-region arrival164.15simsec. Recording and both cleanup owners pass;10/11 runtime predicates pass, with the existing escape-command ownership failure still present. Session50565 terminal/reaped0; no simulation remains running. See the latest [demonstration review](visible_advisor_demos_20260911.md) and `/home/mattb/Experiments/GESC-Gaussian/v2/demonstrations/20260911T234202Z_D_nominal_visible_normal_speed_phone/post_run_fill_review/report.md`. Source unchanged; cancellation cause remains unresolved.

Current decision: [2026-09-11 acceptance retirement and issue triage](acceptance_retirement_20260911.md).
The >=30% independent-onset detector-delay target is RETIRED prospectively by
explicit user instruction; the original unavailable endpoint and closed study
remain unchanged. The user accepts the selected 16-run improvement. No other
research measurement blocks beginning bug diagnosis. Priorities: D cancelled
fills, C/D command consistency, then D/noise missing-anchor investigation.
Initial compact-record triage confirms three primary cancellations and three
follow-up terminal-preparation rejections; the exact causes remain undiagnosed.
Runtime GOAL_HOLD removal is not implemented. No runtime source or experiment
changed in this documentation milestone; validation is recorded in the amendment.

The earlier handoff and milestone statements below describe their saved history.

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

Last verified: `2026-09-11 UTC`; complete D02 development and V13 source validation640/640PASS. Source review/checkpoint precede preparation. No V13 acquisition.
Status: `IN_PROGRESS`

## Objective

Implement the full approved simulation-only V2 convergence and continuous GESC
plan, qualify each component, execute the bounded four-arm 16-run pilot, and
close with exact acceptance evidence. A saved plan or partial implementation
does not satisfy the full objective.

## Verified repository state

- Branch: `feature/gesc-gaussian-robustness-v2`
- HEAD: `3369cfc83a64ff5d8354827fd5310caaf0c8e945`
- Working tree at start: clean; all current edits belong to this task.
- Plan: `docs/codex/gesc_gaussian/v2/plan.md`
- Material M4v10 source archive PASS: `checkpoints/m4_v10_source_v1/`,
  all536 members verified in0.833149s; manifest SHA256
  `8ba625f90ec499328cc52c53172191e930356aead2e856f74391aa802b645803`.
  Context/diff/checkpoint PASS. This receipt postdates the immutable archive.
- Previous completed material archive: `checkpoints/r4_stationary_integrated_source_v1/`
  under the external V2 experiment root; all526 source members verified in0.796468s.
  Manifest SHA256: `45a4761d92f2dee1ea377b8f427c1c7de07e7ab1a9093ae686b7f50b11cdbc3d`.
  Context validator, diff check and material checkpoint PASS. This receipt is
  appended after the immutable archive; no production source changed.
  Previous completed pairing archive: `checkpoints/r4_stationary_recurrent_source_v1/`
  (518 paths; manifest `add614e3fe51c8b1fe1a3bfcb9a56814acdf86b813bef1237f0279879efa148f`).
  `checkpoint.txt` records the corresponding repository material boundary.
  This captures dirty source/evidence, not research qualification.
  A material M1 source snapshot is retained before further owner changes at
  `/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m1_boundary_v1/`
  (`source_and_evidence.tar.gz`, staged/unstaged patches and manifest). Manifest
  SHA256: `cafd08fcd3d37fb571493b2e14723ef42f7047d6abf3b75986167717c617ef4c`.
- M2 pre-reference snapshot: `/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m2_pre_reference_v1/`,
  76 files, manifest SHA256 `22de2c6fc4032bfbee87ab9be1182de59e9b5deca3db44dd91e77823eca67059`.
- Corrected M2 snapshot: `/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m2_pre_reference_recovery1/`,
  80 files, manifest SHA256 `7cd41134614401905a1f5e853e4f1d22ec9a8bef3d0a1473844df6f3f9a290a6`.

- Final M2 source archive: `/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m2_clock_boundary_v1/`,
  93 files, manifest SHA256 `3039aeda1ebbe9b9cc447d3cf002254a88a7160aa6c8bfed53cf26443715fb4f`.
  `m2_handoff.md` records completed implementation and unavailable scientific qualification.

- Final M3 source archive: `/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/m3_boundary_v1/`,
  142changed/untracked files,706691-byte verified archive and54retained log hashes.
  Manifest SHA256: `0e144f64d392741f5388a2eaef4c0b98dd1f9068669eb1de1b3533e644602920`.
  The context validator, diff check and existing checkpoint tool PASS. This live
  archive receipt was appended after the immutable boundary; no source changed.

## Completed milestones

- M0 COMPLETE: workflow context and ten regressions, frozen 21-bag inventory,
  interface/lifecycle audit, isolated three-package build and 13 inherited
  detector regressions. Exact evidence is in `validation/`.

## Current milestone

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


R15 material closure: context validator, diff check and existing checkpoint PASS.
Archive `checkpoints/r15_reduced_harmonic_v1/`:621 verified source members,
1.113313046s; manifest SHA256
`ed0a9afa2a38cedb6786001e76b0a788e86b829682663bfc96878dc72c0ae06d`.
This live receipt postdates the immutable archive. Both candidate failures and
all raw/cached measurements retained; no simulation, commit or push performed.

Latest completed milestone: [R14 harmonic method study](r14_harmonic_method_handoff.md).
Study COMPLETE; candidate REJECTED under its unchanged prospective criteria.
24/24 focused mathematical checks passed. Independent controls:0/512 null false
accepts, but26/64 stronger stable signals detected, below90%. Retained applicability:
0/46 originally eligible targets usable; all eight noisy verification supports
fail angular information. Independent reviews PASS17 synthetic/58 retained checks.
Sessions44490 and21676 terminal/reaped0; no ROS/Gazebo runtime is active. New pure
source remains unwired. Next work needs a prospective method revision addressing
identifiability and output-relevant uncertainty, then independent controls and
credible visible integrated development. No new matrix is released.


R14 material closure: context validator, diff check and existing phase checkpoint
PASS. Archive `checkpoints/r14_harmonic_method_v1/` contains616 verified source
members, completed in0.990166671s; manifest SHA256:
`4da7470b0cdff23d384033e88bee6e97a5230b6a2a9329005f51aac6e1b20237`.
This live receipt postdates the immutable archive. Study COMPLETE, candidate
REJECTED; no active simulation, commit or push. Full research goal remains open.

Previous completed milestone: [R13 retained profile/direction study](r13_profile_direction_study_handoff.md),
COMPLETE; retained measurements and independent reviews passed. All three bounded
sessions are terminal/reaped. All eight noisy attempts match the rejection reason,
six exactly match terminal diagnostics; longer pooling fails geometry. New
D/noise reference process qualification passes, retaining numerical failure.
All 144 projected targets are retained: weight-only correction leaves C/nominal
and D/noise direction failures. No source method change, bag read or simulation.
Next incomplete criterion is a prospective controlled noise-aware method study,
followed by credible visible integrated development before another comparison.

Earlier milestone notes below are historical; current evidence is in the R14
handoff and validation record.

R13 closure: context/diff/checkpoint PASS,611-member verified archive
`checkpoints/r13_profile_direction_study_v1/`, manifest
`842d44bdb75b4525787b981cc2290e21b91e8c034f6bb9bff35eeb688f97a294`.
This receipt postdates the immutable archive. No method correction or simulation
was made in R13; the full research goal remains incomplete.

Current completed milestone: [R12 measurement correction](r12_measurement_correction_handoff.md).
129 focused checks passed; selected import is subprocess-free. Separate retained
B/noise arrival is 283.167 s, with historical default/unavailable time preserved.
Both component sessions are terminal/reaped, source/input pins stable, and
independent review passed. No simulation or matrix is released. Next work is a
prospective retained profile/direction study; no method correction is implemented.

Current completed milestone: [R11 retained diagnosis](r11_retained_diagnosis_handoff.md).
Import-only subprocess confirmed in 1.408772 s; both noisy cancellation traces
extracted in 3.032655 s; arrival exact-equality rejection diagnosed from cached
records without another bag read. No production correction or simulation was
executed. Next work requires a prospective bounded correction/method study;
no matrix is released. V12 remains closed as recorded below.

M4v12 is **CLOSED_INCOMPLETE**. The sole dispatcher session 53920 exited 1
and was reaped after 5081.954558 seconds. Twelve acquisitions are COMPLETE;
delay slots 13–16 are UNSTARTED. No runtime is active. Preserve all V12 files
and never resume that dispatcher or substitute cases.

Read [V12 closeout](m4_v12_handoff.md) and
[execution validation](validation/m4_v12_execution.md). Confirmation acquisition
outcomes are six arrivals, two nonarrivals and four unstarted cases out of twelve.
Development has three arrivals and one nonarrival. Only scientific blocks 0 and 1
completed. D passed nominal direction thresholds and continuous acquisition;
C failed nominal direction thresholds. Noisy C/D produced no fill or escape.
The D/noise reference worker had an unexpected child process, so its process
integrity failed despite normal numerical completion. B/noise also lacks an
exact offline/live arrival timestamp match. These are separate unresolved issues.

R10 remains completed selected detector-response evidence; the original 30%
basin-entry latency target remains unavailable. The full research goal is not
complete. R11 diagnosed the import subprocess, noisy verification signal heuristic and
arrival equality mismatch. Next work is a prospective bounded correction and
profile-method study; see the R11 handoff.
Do not start another matrix. The user authorizes justified simulation-only
method development; no physical/Pi/snapshot/V1/commit/push action is authorized.

## Earlier M4v12 progress (historical; closed above)

V12 live: 12 acquisitions COMPLETE. Eight of 12 confirmation cases have
completed: six arrivals and C/noise plus D/noise failures, with no fill or
escape. Owned block 2 science is running; four delay cases remain. Nominal
C direction FAIL and D direction PASS are retained. Sole dispatcher session
53920 / owner PID 93189 remains active; never restart it. Source, helpers
and contract remain frozen. Current detailed evidence is in
validation/m4_v12_execution.md and immutable acquisition/slot_N.json receipts
under pilot/m4_pilot_v12. The goal is not complete.

V12 current:noise slot9 A RUNNING via sole dispatcher53920/PID93189.
All8earlier acquisitions COMPLETE. Nominal confirmation all4arrived;
block1science COMPLETE. CdirectionFAIL(32.6581deg median/72.5314P90),
DdirectionPASS(5.68316/25.4949),bothcontinuous0mandatory stops.
Nominalarrival A/B/C/D230.504/302.605/211.539/192.075s. No tuning or
retry; preserve failures. Noise9–12 anddelay13–16remain. Frozen source/
helpers/contract unchanged; continue existing session,not a new dispatch.

V12 live:8acquisitions COMPLETE. All4nominal confirmation cases(A/B/C/D)
arrived andpassed mandatorybehavior/recording checks. Development remained
AFAIL,B/C/DPASS; block0science+release verified. Dispatcher53920/PID93189
is running block1science, thennoise9–12/delay13–16. Eightconfirmation
cases remain; goalnotcomplete. Preserve source/helpers andactive session.
See validation/m4_v12_execution.md for exact retained receipts/progress.

V12 CONFIRMATION RELEASED after complete development science. AFAIL; B/C/D
arrived173.049/151.858/251.313s. C/DdirectionPASS andobservedcontinuous
acquisition(no mandatory stops),medians14.0247/8.2487deg. All4science rows
complete,bothrefs andsummaryPASS,R10prerequisitePASS. Sole dispatcher53920/
PID93189is active for slots5–16; do not launch/resume another. Source/helpers/
contract remain frozen. See validation/m4_v12_execution.md and small external
`development_readonly_summary.json`. Goal remains incomplete pending12cases.

V12 live:all4development acquisitions COMPLETE. AFAIL(lateStageA recovery
timeout); B/C/DPASSglobal arrival andall11predicates. Dispatcher53920/PID93189
is running owned block0science; confirmation not yet released. Source/helpers
remain frozen. Do not duplicate analysis or dispatch. See execution record.

V12 live progress:slots1–2 COMPLETE. A baseline failed late local recovery;
B recurrent stationary reached the global region(0.498723m) and passed all11
mandatory predicates. Sole dispatcher53920/PID93189remains active for C/D then
owned block science. Confirmation remains gated. Frozen source/helpers intact.
See [execution record](validation/m4_v12_execution.md); no retries or extra
analysis/recorders. Preserve this active session across recovery.

V12 DISPATCH RUNNING: sole root tool session53920, dispatcher ownerPID93189,
started2026-09-11T03:08:13.975588+00:00. Do not launch or resume another dispatcher.
External owner `development/20260911/m4_v12_source_v1/acquisition_owner_v1.json`,
console `acquisition_console_v1.log`; terminal receipt will be
`acquisition_execution_v1.json`. Initial visible slots1–4; confirmation slots5–16
remain gated by the existing complete-development/R10 release policy.
Outer GNUtimeout SIGINT15680s plus120s kill (15800s total maximum).
ReleaseSHA `504e1015d2e9a0a810700d1d1f0d702ae16dbc679c3c04892f59064c1bc86502`.
Prepared archive24files verified0.137232s; manifestSHA
`2af4056db71f9a27e9f02a1f73f1e878c444a67d3860226399952182c09d892e`.
All source, helpers, contract and archived preparation validation are frozen;
update only live status/handoff or separate runtime notes during acquisition.
Poll the existing session and inspect small completed receipts; never read an
active bag or repeat numerical analysis merely to recover context.

V12 PREPARATION COMPLETE; dispatcher not released. Session65738 terminal0,
54.859354s,866source/helper pins stable. ContractSHA
`32401f17366124a7b2406876c39aa594cd0a246b8acfd8dcd0a5c7fd71194162`;
[source/preparation evidence](validation/m4_v12_preparation.md). Independent
frozen scenario/workflow audits then prepared archive are next. No runtime
is active. All source and orchestration helpers are held.

V12 source boundary VALIDATED2026-09-11UTC. First bundle784PASS/2obsolete
version-test failures retained,179.030068s; exact two-function correction10/10
PASS in2.876825s with866stable pins/21entries. No production change after
full bundle. See [source validation](validation/m4_v12_source.md).
Material checkpoint/archive then600s exclusive preparation and frozen audits
are next. No simulation is active or dispatched.

V12 source implementation in progress2026-09-11UTC. Scenario/schema and science
owners are held with before copies and patches under
`development/20260911/m4_v12_source_v1/`. Workflow tests and adapted existing
orchestrators are being finalized. No focused test, preparation or V12
simulation has run. Next:sole230s focused bundle, review/archive, exclusive
preparation and frozen-contract audits before staged dispatch.

M4v12 ADOPTED: [plan](m4_v12_integrated_comparison_plan.md). Source implementation
is next;no V12 code,test,preparation or simulation has executed. Primary scope
is integrated arrival/direction with R10 component response prerequisites. Keep
the old30% basin-entry endpoint secondary and unchanged. V12-only first-path
diagnostic selection preserves all existing completed-recovery/safety predicates.

R10 material archive COMPLETE:592 verified source/docs members,48 focused
evidence refs,source stable in0.874871s. ManifestSHA
`df23819df6c4f013f8790e414ce045e2b8d7a1b03959ee40f97ec550a349625d`
at `checkpoints/r10_paired_response_v1/`. Receipt appended after immutable archive.

R10 COMPLETE: [handoff](r10_paired_response_handoff.md). Both bounded studies,
independent reviews and all eight joint decision checks PASS. Empirical response
102.008s new vsPDEcensored360.8s;synthetic36/36 positives and0/48 negatives new
vsPDE19/36 and4/48. Full-positive capped median42.024s vs73.3635s.
No runtime active;all children reaped. Next is prospective16-run integrated
arrival/direction comparison design. No new comparison adopted/released yet.
Original30% basin-entry latency remains unavailable. Full goal IN_PROGRESS.

### Earlier current-milestone entries (superseded)

R10 both jobs COMPLETE. Empiricalnew102.008s/PDEcensored360.8s,reviewPASS.
Synthetic:all96 histories/114560 points completed in100.629278s outer,34 stable
pins;new36/36 positives and0/48 negatives versusPDE19/36 and4/48.
Full36-positive capped median42.024s vs73.3635s. Session14723 terminal/reaped0;
no runtime active. Synthetic independent review and joint closure pending.

R10 empirical COMPLETE:102.008s recurrent circle response;PDE right-censored
at360.8s without confirmation on the same uninterrupted trajectory.37 stable
pins,8.350992s outer,one filtered read;session90317 terminal/reaped0.
Synthetic comparator now active as session14723 under180s inclusive,34 prepared
pins/16 historical input hashes. Independent cached empirical review is ongoing.
All reviewed source/helpers/plan are held. No new simulation/comparison released.

R10 active empirical job session90317 under120s inclusive.34/34 focused adapter
checks passed in0.719459s outer with24 stable pins; terminal/reaped0.
Empirical preparation binds37 inputs/sources,including13 original input hashes.
Synthetic study remains unstarted. All reviewed source/helpers/plan are held.

R10 paired response study ADOPTED: [plan](r10_paired_response_plan.md),
[validation](validation/r10_paired_response.md). Helpers are being prepared;
no adapter check or empirical/synthetic replay has executed.
Only retained V9 B and unchanged R4 controls are selected. No new matrix released.

R9 material archive COMPLETE:589 verified members,34 evidence receipts,
source stable in0.842456s. External `checkpoints/r9_motion_readiness_v1/manifest.json`
SHA256 `bb07b5d61fc546b4a34fcecd64a6d208391a0ea51be3471e2b09df0823ea86ee`.
Receipt appended after immutable archive; validated source unchanged.

R9 COMPLETE: [handoff](r9_motion_readiness_handoff.md).59 focused checks PASS,
selected C component OBSERVED_CONTINUOUS_ACQUISITION with11493 exact pairs,
independent review PASS. Sessions54276/69875 terminal/reaped0; source/helpers held.
No runtime active. Next detector-measurement design is pending and unreleased;
V11 and its twelve unstarted confirmations remain closed unchanged.


R9 private motion-evaluator readiness correction is active under
[r9_motion_readiness_plan.md](r9_motion_readiness_plan.md). Both V11 measurement
diagnoses and independent reviews passed. Job1 session74919 reaped0 (2.870768s),
Job2 session56873 reaped0 (3.933934s); no application runtime remains.
R9 source/tests are being prepared; no R9 tests or C reassessment have executed.
The detector measurement question remains pending; no new comparison is released.



M4v11 CLOSED_INCOMPLETE; dispatcher59849terminal/reapedexit1,1478.291230s,
all806pinsstable. Allfourarrivals PASS; C retains11/12state-pathfailure.
C/Dselecteddirection references PASS(7/24 and4/24eligible); DcontinuousPASS.
Ccommandpairing unavailable(12119actual/12118diagnostics); all4firstresidence
latencies unavailable(0/2pairs). Gatewithheldall12confirmation. Sourceheld;
no runtime active. [V11 closure](m4_pilot_v11_handoff.md) is current authority.
Next separatelybounded measurementdiagnosis; no newmatrix or qualificationclaim.

Historical progress entries below are superseded by this terminal boundary.

V11 slots1/A,2/B,3/C COMPLETE with successful global arrival at298.959,
167.367,226.755s respectively. C frozen behavior FAIL11/12 only for initial
rejected VERIFY->SEARCH before successful later recovery; arrival/safety/
ownership/recording/cleanup PASS. D active under sole dispatcher59849.
Fourrun science/release pending; source/tests/helpers remain held.
Details: [execution record](validation/m4_v11_execution.md).


V11 slots1/A and2/B COMPLETEbehaviorPASS(all12requiredpredicates). Arrival
A298.959s,B167.367s;Bfinaldistance0.480612m,elapsed274.685528s. Recording/
cleanupPASS. Dispatcher59849active,slot3/Cstarting. Fourrunscience/latencypair
releasepending;no source/helperchange. Areadonlyauditstoredwithfourstableinputs.


V11 slot1/A COMPLETEbehaviorPASS412.728963s;firstarrival298.959s at0.499472m,
full localfill/escape/SEARCH, recording/cleanupPASS. GOAL_HOLDnotrequired.
Dispatcher59849 remainsactive, continuingtowardsB; independent4runscience
andlatencypairreleasepending. No source/helper changes or reruns.


M4v11 sole dispatcher ACTIVE session59849. GNUtimeout15680s SIGINT+120s kill
inside exact saved command,15800s maximum. Initial4visibledevelopment then12
confirmation onlyafterusableanalysis/BorDarrival/Dcontinuous/bothobservable
latencypairs. No replacements/tuning. Source/tests/helpersandfrozenpreparation
validation remain unchanged. Read external `m4_v11_source_v1/acquisition_owner_v1.json`,
`acquisition_console_v1.log`, andpilot/m4_pilot_v11/acquisition/ beforecontinuing;
neverlaunchasecondcopy. Dispatchrelease session88425terminal0,SHA
`d6ebc1ceac5f16c23620bbb41d8884665402561f432190d7331a02cd2598c02e`.
Preparationarchive24filesverified0.156347s,manifest
`768eaa35553e66d56c8e1efba280c1ff8569abce097424624eae221ba17b2031`.
BothfrozenauditsPASS;initialscenarioauditcomparisonfailure retained separately.


V11 preparation PASS54.797726s,session66863 terminal/reaped0,all806pinsstable.
Contract3b1a4b5de2ee1eb5a9352561732cb349788f46f14dc8a4b7b0a776f5175b18ba,
797sourcefiles/16slots/21entries. Independent frozen scenario/workflow audits
in progress; no acquisition or application runtime. Source/tests/helpersheld.


M4v11 source archive PASS580 members0.942779s;manifest
`1772d7d15c749e4d9c4ed724a901f137a34f56f4339a43918212ba63415c0dbf`
at external `checkpoints/m4_v11_source_v1/`. Sole preparation ACTIVE session66863 under
595s SIGINT+5s kill; no acquisition. Source/tests/helpers remain held.


M4v11 SOURCE_VALIDATED:676 unique checks PASS160.293120s,806 stable pins/21
installed entries;session4096 terminal/reaped0. [Source handoff](m4_v11_source_handoff.md).
Source/tests/helpers HELD. Next material checkpoint/archive then sole frozen
preparation under600s. No Gazebo/application runtime or V11 acquisition yet.


M4v11 six owners/tests/helpers HELD; source bundle ACTIVE session4096 under230s pytest,
260s inclusive cap. Read external `m4_v11_source_v1/focused_v1/` and
`focused_outer_v1.log`; do not launch another copy. Exact source/helper and
independent review receipts retained there. No preparation/acquisition yet.


M4v11 plan ADOPTED after R8 archive574 verified members0.890614s,manifest
`d7a432e11d5ea5f8c9a6794f3ac97a6c15399ab9e210ccca619b4ba145e4a593`
at external `checkpoints/r8_pde_evaluator_source_v1/`. New source boundary
`development/20260910/m4_v11_source_v1/` retains all6 before owners. Next
minimal registration and focused validation; no preparation/acquisition yet.


R8 COMPLETE at declared source/cached boundary.147 unique checks PASS16.709488s,
770 stable pins/21 entries; cached C03 reassessment PASS1.751833s. Corrected local
recovery/cardinality/arrival=True; first actual arrival152.519s at0.499493m,
nearest0.218300m andfinal0.256424m. Public payloads unchanged; originalC03FAIL,
StageA timeout and no livearrivalstop remain retained. Sessions8141/39012 terminal0;
no application runtime active. [R8 handoff](r8_pde_evaluator_timestamp_handoff.md).
Next material checkpoint then prospective V11 adoption; no V11 dispatch yet.
The chronological entries below retain earlier in-progress states.


[R8 private PDE timestamp plan](r8_pde_evaluator_timestamp_plan.md) ADOPTED after
C03 empirical source archive. Main owner/test integration and lean adversarial
fixtures are in progress; no R8 source test or cached reevaluation has run.
No application runtime active. Rootplan navigation updated after all C03 jobs;
old pinned source/evidence stays retained. Fresh handoff rebuilt around this
current boundary; prior transient status stack is preserved in C03 source archive.

C03 source/evidence archive PASS570 members1.475846s; manifest SHA256
`a5bd6d63a6a836e51d39ce97968d144a47a5623810679150a36902995d93d73e`
at external `checkpoints/r7_c03_observed_arrival_v1/`. Cached association audit
postdates that archive: `cached_association_audit_v1.json`,21 stable input/source
hashes, SHA256 `d13c094540488a69c10ce65f7e6269ae736e761f44271791c801dd28b746ac33`.
All6 reviewed source pins match C03 preparation/native receipts.

C03 acquisition/native/reference all terminal/reaped (67868/10152/57790).
Complete recording and both cleanup PASS234.281428s; native COMPLETE72.273257s,
source/input pins stable; full continuous VERIFY+DESIGN observed. ReferencePASS
6.248689s,4 eligible/24 scheduled,median10.8613deg/P9020.3482deg,4/4 improved.
Actual final global distance0.256424m after fill/escape/SEARCH satisfies the user
arrival objective. Frozen evaluator stillFAIL8/12 because public PDEevent85.0s
is later than typedconfirmation/fill support84.927s, preventing local association.
Original verdict retained. Next strict private evaluator timestamp correction
and separate cached reevaluation; no production edit or V11 release yet.

C03 acquisition terminal/reaped session67868,234.281428s; recording/inner+outer
cleanup PASS and776 prepared pins stable. Frozen behavior FAIL:8/12 predicates;
full required state/event path and ownership/safety pass, but fill association
unassigned (local-recovery/cardinality fail), so StageA expired and arrival was
not admitted by evaluator. No verdict rewrite. Native two-scan analysis ACTIVE
session10152,110s work/120s max; do not duplicate. Read analysis_v1 receipts.

C03 sole visible acquisition ACTIVE, session67868,415s SIGINT plus5s kill
grace. Read external `visible_integrated_C_03/` started/command/attempt receipts
and acquisition_outer.log; never start another copy. Prepared source/helpers
held; no outcome or V11 release yet. C02 remains closed startup failure.

C03 startup validation PASS38 checks7.416883s (session8757 terminal/reaped0),
766 stable pins/21 entries. Preparation PASS3.842385s (session84696 terminal0),
776 stable pins combining both source receipts. Actual recovery override=True
and arrival-only criterion verified. Prepared SHA256
`f13c7a2b82df163e10b7d48470ddc60a197a55254a52ad4e0cd1a303eb3e4682`.
Next sole visible acquisition under420s; source/helpers held, no V11 release.

C03 [plan](r7_visible_c03_plan.md) ADOPTED: existing idempotent spawner override
only; no production or scientific-setting change. Source/helper review PASS.
Next existing startup tests45s/60s, then preparation conditioned on both receipts.
C02 closure archive566 verified; no application runtime active.

C02 CLOSED_INCOMPLETE at startup; session95566 terminal/reaped0,33.076955s.
771 prepared pins stable; inner and outer scoped cleanup PASS. Recording never
reached readiness and is INCOMPLETE; final-zero evidence is unavailable. Upstream
velocity_controller spawner lost a load response, retried, then failed because
the controller was already loaded. No candidate/admission/fill/arrival exposure;
R7 behavior is untested. Native analysis/reference NOT_STARTED because required
recording gate failed. [Failure handoff](r7_visible_c02_handoff.md).

C02 sole visible acquisition ACTIVE, session95566,415s SIGINT plus5s kill
grace. Do not start another copy. Read external `visible_integrated_C_02/`
started/command/attempt receipts and acquisition_outer.log for live ownership.
No outcome yet; prepared source/helpers held, full comparison unreleased.

C02 preparation PASS3.766192s; session43362 terminal/reaped0.771 source pins
and21 installed entries verified; prepared SHA256
`d1de9a41247bb8ee61650a4adcb9741849d17f8166eba8b84f7b067e406e29f8`.
Root resolved-scenario review PASS. Next sole visible acquisition under420s cap;
source/helpers remain held. No empirical outcome or V11 release yet.

C02 [visible plan](r7_visible_c02_plan.md) ADOPTED after R7 source validation
and564-member verified source archive. Exact exposed seed/settings/budgets and
identity-only helper/scenario differences reviewed. Next sole preparation under
90s; no acquisition yet. Source/tests/helpers held; no V11 release.

R7 source archive PASS:564 members verified0.888729s; manifest SHA256
`ba29d5b2dfe05166e1cc35fc740f93feb49cea5c67c0261ca15886963d7e0fae`
at external `checkpoints/r7_approach_runtime_source_v1/`. This receipt postdates
the immutable source archive. Source/test files remain unchanged.

R7 SOURCE_VALIDATED:332 unique checks PASS52.822781s (pytest50.58s),
764 stable pins and21 unchanged installed bindings; session89193 terminal/reaped0.
[Source handoff](r7_approach_runtime_handoff.md) records the two-owner change and
independent review. Receipt SHA256
`7251d316bcecd729ebd97df716035e2d6a3d9528574766b7959dcc1313995118`.
No new acquisition or empirical qualification. Next source checkpoint, then
adopt and prepare the already-reviewed C02 draft. Source/test files remain held.

R7 source/tests HELD; sole focused bundle ACTIVE, session89193,240s work within
260s total. Read external `r7_runtime_validation_v1/focused_v1/` and
`focused_outer_v1.log` before any continuation; do not start a second copy.
Independent source review PASS. C02 draft ready, no preparation/acquisition.

[R7 runtime integration](r7_approach_runtime_plan.md) ADOPTED after prototype
archive558 members, manifest90170528009905ea0781231b563473afe767fea52ccad1fbcaf6def80c86812c.
Implementation and adversarial fixtures are in progress through the existing2
owners. The single named bundle and checkpoint helpers are prepared under
external `development/20260910/r7_runtime_validation_v1/`; no test job has run.
C02 plan/materials are being drafted; preparation/acquisition await source
validation and separate plan adoption. Rootplan navigation was updated
prospectively after R6/R7 receipts; historical evidence is unchanged.

R7 prototype nomination PASS, session14834 terminal/reaped;138 trajectories,
383 stable pins, finalsummary45.201062s. Both laws63/63required; baseline4/6hard,
prototype6/6hard. No pass-to-fail regression;28 readinessslowdowns<=0.6s retained.
[Prototype handoff](r7_approach_feasibility_handoff.md) records limitations: ideal
baseline did not reproduce C01failure; realfield/directionquality unestablished.
Next archive modelboundary and adopt bounded phase-aware runtime source change.
No new runtime or V11 release.

[R7 approach feasibility](r7_approach_feasibility_plan.md) ADOPTED after R6
validated source archive555 members, manifestfa2fcdc72e72920577f5f87b123c07539903db09047788f413ec4cabe2b7af29.
Next prepare/freeze69 starts and compare2 laws through existing ideal unicycle/
controller/collector owners in one90s job. No production change or runtime release.
No R7 helper/preparation/numerical job has run at this boundary.

R6 SOURCE_VALIDATED:312 unique focused checks PASS50.074988s (pytest47.80s),
762 sourcepins/21 installedbindings unchanged; session10905 terminal/reaped.
Independent static review PASS; [source handoff](r6_verification_expiry_handoff.md).
Receipt SHA256 `3f182a9572f346317c086b1c456d386a2b47fc9d0c91b71e5ac1d022bb975e96`.
No application runtime active. Next source archive, then adopt R7 bounded approach
prototype. No arrival/direction qualification or V11 comparison release.

R6 source/tests HELD; one9-module final source bundle ACTIVE, session10905,
240s work within260s maximum. Read external `r6_validation_v1/focused_v1/`
and `focused_outer_v1.log` before continuation; never start a second copy.
Controller hash521d33e75696e71657e80394f117715304aed11b1e48081fa22adf62d7701759.
Main14 plus51 new adversarial cases and focused existing regressions selected.
Independent review running read-only; no Gazebo or R7 numerical job.

R6 unchanged-controller baseline REPRODUCED in1.757365s: valid79.0 VERIFY
guidance expired79.1, actual zero plus erroneous hard fault;128 source/runtime
pins and21 installedbindings stable. Session25015 terminal/reaped, isolated
fixture domain218 cleaned up. Baseline result SHA256
`7a1751b3069518f82790897d541bbdf496adc771aa406ea65d1156925ec40475`.
Bounded controller correction is now in progress; no finalbundle/newruntime.

[R6 verification expiry handoff](r6_verification_expiry_plan.md) ADOPTED after
C01 closure archive549 paths, manifestec3d42b4fc8556a65733f1b0f90358be5548e19c977c346ebfd01fc16981f634.
Next unchanged-controller regression, then bounded zero-output wait correction
without extending any motion lease. No source edit/test/runtime started yet.
Approach-law diagnosis remains a separate next milestone; V11 NOT_ADOPTED.

C01 closed with behavioral failure before DESIGN/fill/escape. Sessions97648,
19870 and90322 terminal/reaped; acquisition229.426403s, nativeanalysis64.377794s,
reference6.283701s. [Current handoff](r5_visible_c01_handoff.md) records the distinct
approach failure and ordinary deadline fault race. Native analysis PARTIAL from
missing required escape applicability, while freshrecording/lifecycle and measured
motion/arrival evidence are valid. Reference executes but scientific summary FAIL
(median22.061854deg,P9073.223806deg,3eligible/24scheduled). No runtime active.
Source remains held. Next prospectively plan bounded deadline handoff correction
and approach-law diagnosis. V11 draft NOT_ADOPTED; fullgoal remains IN_PROGRESS.

C01 acquisition terminal/reaped, session97648,229.426403s. Recording and inner/
outer cleanup PASS,767 source pins stable; behavior FAIL. PDE confirmed71.1s,
but no fill/escape and Stage A expired at180.333s; final robot stayed near local.
Attempt receipt SHA256 `2156dd608365f4bb8cab0ba8826b758106e3be2f7a1970a5eaf5c4b5178a20ab`.
Native analysis is active once, session19870, under120s maximum; no raw reread
outside this existing two-scan job. Read `visible_integrated_C_01/analysis_v1/`.
No new runtime or source correction released; V11 draft remains NOT_ADOPTED.

C01 single visible acquisition ACTIVE, session97648,415s SIGINT plus5s kill
grace. Never launch a second copy. Read external
`visible_integrated_C_01/{started.json,command.json,attempt_result.json}` and
`acquisition_outer.log` for live/terminal ownership. Prepared archive9 members
verified, manifest `1c81b85722e7213c264203b1d64fe75af9594b30fc6a0ed0e2ba9690e7879b3f`.
No behavioral result yet; source/helpers held, fullcomparison unreleased.

C01 preparation PASS3.754784s, session98659 terminal/reaped;767 source pins
including all760 validated R5 pins and21 installed entries stable. Prepared SHA256
`e0d71e22461082dd6eaa3ed9b8d657b5242cb2dc2ecde127e7dd30c30b87a024`.
Root resolved selector/topic/identity review PASS. Acquisition may proceed once
this material checkpoint is saved; source/helpers stay held.

C01 exclusive preparation started, session98659,85s SIGINT plus5s kill grace.
Read external `visible_integrated_C_01/preparation_receipt.json` before any
continuation; never repeat the preparation. All scenario/analysis helpers are held.
No C01 acquisition has started.

R5 C01 helpers/scenario are being prepared under the adopted
[runtime protocol](r5_visible_c01_plan.md). R5 production/tests remain held;
all760 validated hashes still match. A point-in-time procfs audit found no
selected simulation runtime active. No C01 preparation or acquisition has run.

R5 SOURCE_VALIDATED and archived:272PASS49.247001s,760pins/21installedbindings
stable,session51226terminal/reaped. [Source handoff](r5_centered_commit_handoff.md).
Archive545 members0.809607s, manifest `6092ea4f838cfea12013ef0987f4aa2d4cb99b9e82961234d440735b5c7d1758`.
Next [short visible C01](r5_visible_c01_plan.md) is prospectively adopted;
preparation/acquisition have not started. Same exposed seed26091011, newdevelopment
identity, bounded420s visible case then native analysis/reference. No fullmatrix.

R5 source/test HOLD; focused validation session51226 is active (one8-module
bundle,240s work and260s maximum). External receipts/logs:
`development/20260910/r5_validation_v1/focused_v1/` and `focused_outer_v1.log`.
Independent review found no blocker. Only production delta is75added/1removed
in MovingSupervisor; hash4b411fc9d52c21115d7ea860114d7845d84dfe25eb853bfe8d96d4662a70dffa.
No new simulation is released. Read terminal receipt before further tests/work.

R5 unchanged-source reproduction PASS1.198057s, session61366 terminal/reaped:
retained C geometry, actual typed activation/fill callback, unchanged proposal
v0.0320559805/w0.1267490962 then self-fill cancellation/invalid guidance/SEARCH.
Receipt `development/20260910/r5_centered_handoff_v1/baseline_v2/result.json`,
SHA256 `2b141dad9d14fe90495262962b838b361c23218ce200a2f77712422b5996acc9`.
Earlier baseline_v1 generated-array fixture failure0.959449s stays retained;
only fixture assignment changed before the passing reproducer. Original production
hashbbb5d6e8bdccad119881603576734fac213562f874cde990aad10fbd3ea1b593.
The bounded supervisor correction is now being implemented; final bundle pending.

R5 source correction ADOPTED: [centered activation handoff plan](r5_centered_commit_handoff_plan.md).
Confirmed C self-fill avoidance cancellation86.0s and subsequent watchdog fault;
cached typed export6.753600s PASS, no repeat decode needed. V10 closure archive
PASS540 members2.587828s, manifest `444694a647ec726895d4ff5f580ee20fbe764a755c9090ec36b63897dfddfc67`.
Next unchanged-source reproducer, one bounded supervisor correction and focused
validation. No ROS/Gazebo active; no new acquisition released. Fullgoal active.

M4v10 CLOSED_INCOMPLETE: dispatcher66016 is terminal/reaped exit1 after
1268.120640s (wrapper1271.949431s). Slots1/A and2/B COMPLETE/PASS; slot3/C
INCOMPLETE because actual forbidden FAILSAFE state/events failed the safety
gate. C recording and inner/outer cleanup passed; independent second inner
inspection was not reached. Slots4–16 UNSTARTED, no block science, no
confirmation release. All16-slot report retained at `pilot/m4_pilot_v10/report/`.
Failure: `ValueError: M4 safety state/event evidence is absent or failed`.
Do not restart, replace slots or weaken the safety gate. Source remains held.
Next is retained C failure diagnosis through existing read-only owners.

Latest: slot2/B COMPLETE, all12 predicates PASS,357.904877s wall. One recurrent
local fill -> REPULSE -> ASSIST -> SEARCH -> global arrival0.497651743m;
final0.486047402m, terminal SEARCH, recording and both cleanup checks PASS.
Slot1/A also COMPLETE/PASS. Slot3/C is next under the same active session66016;
block science and exact detector-latency/arrival-time measurements remain pending.

Latest acquisition update: slot1/A COMPLETE, behavioral/all12 predicates PASS,
recording and outer/independent-inner cleanup PASS,417.122410s inclusive wall.
One local fill and assisted escape restored SEARCH; actual arrival distance
0.498021974m. Slot2/B is dispatched by the same active session66016. Science
has not run yet; source held, no restart or confirmation release.

M4v10 acquisition STARTED under one dispatcher, session66016. Do not restart.
Root owner receipt: external `development/20260910/m4_v10_source_v1/acquisition_owner_v1.json`;
console `acquisition_console_v1.log`; live authoritative slots/results under
`pilot/m4_pilot_v10/acquisition/`. Initial development release SHA256
`027a80b3e8b6ae150a8f54664ee8e8dfe430208c4d9f298735175ba8f87b5dcf`.
Prepared material archive PASS24 files in0.144049s, manifest SHA256
`11912c2f3348862ed4ff9e624ffc49a41e73c9809125694463254c8d5ffb80f0`
at `checkpoints/m4_v10_prepared_v1/manifest.json`. Source is held. Four visible
development cases plus usable science precede12 confirmation release. The same
existing dispatcher enforces this gate; no tuning, retry or replacement.
Full research objective remains IN_PROGRESS; no new behavioral result yet.

M4v10 preparation PASS56.435649s, session8888 terminal/reaped,755 source pins
unchanged. Read [preparation](validation/m4_v10_preparation.md). Contract SHA256
`501a04748edfb47c3848e6ac2b84e512144ce09810875f3b73728b13dad84a3f` under
`pilot/m4_pilot_v10/preflight/`. Preparation must not be repeated. Independent
frozen review and material preparation archive precede exact initial release.
No V10 acquisition has started at this boundary. The following source milestone
account predates preparation; read any newer receipt before acting.

M4v10 comparison source is validated: [current handoff](m4_v10_source_handoff.md)
and [exact validation](validation/m4_v10_source_validation.md). No preparation
or M4v10 acquisition has run. Next is exclusive preparation and resolved-contract
review through the existing workflow, then four visible development cases and
usable completed science before any confirmation release.

All608 unique source checks have passing outcomes after a fixture-only repair:
first607PASS/1FAIL in131.639977s, affected module32PASS in9.894771s; all production
and21 installed entry-point bindings were unchanged between jobs. The old failure
is retained. Cached D02 motion passed in4.244722s with exact original artifact
hashes,764 stable pins, full9419 command pairs and complete moving VERIFY/DESIGN.
Five real installed/comparison CLI help checks passed in5.850403s with756 stable
pins. Sessions14599,5593,72036 and93843 are terminal/reaped. No process is active.

The user requires global arrival within the existing evaluator-only0.5m
region; GOAL_HOLD and a second ranking are optional. B02 reached that region
at172.634s after valid local fill/escape/SEARCH, with all required predicates,
recording and cleanupPASS; native analysis completed in43.390555s. Earlier
D02/D03 moving arrival/reference evidence and frozen detector controls remain.
These are selected development results; the full V2 phase and broader four-arm
comparison remain IN_PROGRESS. Historical V1–V9 and original failed verdicts stay.

Use the verified external runtime environment
`development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh`
under `/home/mattb/Experiments/GESC-Gaussian/v2/`, with `env -u PYTHONPATH`.
It preserves Q5's21 installed entry points/canonical source and new interfaces.
The original pairing test environment caused B01's retained startup failure.

V10 now binds method `recurrent_arrival_v10`, fresh seeds26091011–14 and the
`usable_four_arm_analysis_v1` gate. Budgets:240s block labels,45s references,
10s summary,40s freeze/report,1400s science and15800s suite;900s cases/720s
recorder and360/300s simulation stages. Conditions/geometry are previously
exposed. A complete baseline failure or censored reference/latency is valid;
missing authority/analysis, timeout, incomplete recording or cleanup blocks
confirmation. Read the handoff before preparation; do not rerun tests/bags for
context. Its completed source work supersedes the R4 prospective next-owner list.

## Earlier milestone entries (historical; latest state above)

R3 visible attempt01 is INCOMPLETE at graph preflight in33.81s: shared
stationary-selector allowlist rejected recurrent mode in GaussianFill and
SupervisorNode. No readiness/authorized motion; all sourcepins stable and
cleanupPASS. [Retained result](validation/r3_visible_development_01.md).
Next finish bounded actual-constructor correction and freeze/run new
[attempt02](r3_visible_development_02_plan.md); no unchanged retry.
The fullblock analysis timeout still blocks comparison release.

R2 final combined runtime replay PASS:57/57 positives and0/142 negative
confirmations across200 distinct histories, one gray trace withheld. Static30s
and.04m confinement replace the failed static12 branch; all old failures remain.
See [combined runtime evidence](validation/r2_combined_runtime_replay.md),
[detector source](validation/r2_recurrent_detector_runtime.md),
[recording/scenario source](validation/r2_recurrent_recording.md), and
[centered guidance schema2 correction](validation/r2_centered_guidance_revisions.md).
The full four-bag labels benchmark TIMEOUT117.552s: A/B/C complete, D decoding
started113.586s, no final labels result. Cleanup/integrity passed; this still
blocks the comparison. Use retained timings, never retry unchanged.
Schema2 lifecycle validation PASS58 selected cases; static30 fixture PASS15.
Next: freeze/checkpoint the prepared
[R3 visible development case](r3_visible_development_01_plan.md), then execute
one bounded GUI case and reuse its one loaded bag for saved analysis inputs.
Current selected interface overlay is external centered_runtime_v2/environment.sh.
No new Gazebo has run. Research qualification and final four-arm confirmation
remain open. New recurrent Arm B still requires a compatible request adapter.

R2 component development now nominates a combined selectable recurrent detector
and centered moving verification for source integration. The arc-center/static
component detects32/32 positives and rejects58/58 negatives; the corrected
oscillation component detects22/22 and rejects68/68, including all54 spiked
supports. These are overlapping finite component populations, not additive
independent trials. See [arc evidence](validation/r2_arc_center_detector.md) and
[oscillation evidence](validation/r2_oscillation_detector.md). Ideal centered
motion passes12/12 required cases with an8s approach and once-only12s additional
collection allowance; see [verification evidence](validation/r2_centered_verification.md).
Runtime integration is active in existing detector, supervisor, controller,
recorder and validator owners, with new opt-in typed diagnostics/guidance and
unchanged old wire layouts. First fresh visible development will use moving
Arm D after focused source/transport/build checks. Recurrent stationary Arm B
needs an explicit compatible fill-request adapter before a four-arm comparison.
No new Gazebo or full comparison has run. R1 is complete; research goals remain
open. Retain the existing rolling direction estimator based on selected C
development results, not broad direction qualification.

R1 measured-development boundary is complete and saved in
[validation/r1_development_boundary.md](validation/r1_development_boundary.md).
Detector controls FAIL both W6 (9/11 positives,1/17 false detections) and W3
(7/11 positives,7/17 false detections); B has54 distinct supports/no candidate.
New C direction diagnostic PASS on12 exposed informative targets:
median27.506842deg, p9031.614203deg, averaging12/12;12 other targets unexposed.
D3 analysis corrections and cancellation-reason observability are implemented.
Retain the estimator while developing detector/verification methods. Next is
R2 bounded geometric/recurrence prototype plus retained V9 B/D development
input extraction before runtime nomination. No full comparison is released.
Earlier R1 progress notes below are historical, including preserved helper
failures; read the boundary record for current exact evidence/limits.

R1 progress: moving rejection observability is source-validated (54 focused
checks; [evidence](validation/r1_verification_diagnostics.md)). D3's redundant
work corrections pass their focused/relevant checks; final handoff is pending.
Retained B detector/control measurements are being prepared under
[r1_detector_diagnostic_plan.md](r1_detector_diagnostic_plan.md). The first C
direction diagnostic ended in 7.080 seconds at JSON serialization of a NumPy
boolean, before target publication; it remains failed under
`development/20260910/direction_c_v1/`. A bounded native-scalar correction is
being adopted in the existing analysis owner, including summary denominators.
No new simulation or comparison has run. Source-test passes are not research
measurements; the fixed numerical reference and targets remain unchanged.

R1 measured development is ACTIVE under the user's broadened authorization:
[method/development amendment](method_development_20260910.md). Finish useful D3
corrections and obtain retained-development component measurements before
runtime method selection. Read the current handoff. No new matrix is released;
analysis failure blocks future holdouts. Both research goals remain open.
On entry: branch/HEAD verified, inherited dirty work preserved, no ROS/Gazebo/
scenario/analysis/test process active; 30-second plan/implement context PASS.

The D3-only milestone snapshot below predates this sequencing amendment.

D3 analysis throughput is ADOPTED in [the exact plan](m4_post_v9_analysis_plan.md).
Next retain focused redundant-work reproducers, remove the confirmed immediate
artifact rehashes/discarded objective snapshot, and validate unchanged outputs.
Full120s-block feasibility then needs a separately saved retained-data benchmark.
No new acquisition, old V9 job retry or scientific promotion is released.

Post-V9 D2 monitor correction is SOURCE_VALIDATION_PASS:281 unique current-source
tests (57 focused/224 relevant),647 stable pins/21 installed bindings and independent
review PASS. Only the existing runner's monitor/classification functions changed;
644 of645 prior pins remain unchanged. Completed recovery retains its original
Stage B deadline while current errors/cardinality still block acceptance. Both
jobs are terminal/reaped; one Gazebo E2E was explicitly deselected. Read the
[D2 handoff](m4_post_v9_monitor_handoff.md) and
[validation](validation/m4_post_v9_monitor.md). Material checkpoint/archive PASS:
manifestd5df2e6049b15ea99515426dfd17448f31260412ea161b5e55c7310c4f2ff814,
428 repository files/35 artifact references,1708498-byte verified tar,
1.143492353 s under60. Startup, daemon discovery, throughput and fresh comparison remain open;
no new acquisition or research pass follows. D1 is materially closed below.

The following D1 completion snapshot predates the D2 source correction.

Post-V9 D1 is DIAGNOSTIC_ONLY_COMPLETE. The sole fixture passed28/28 in2.865 s
under45; the sole read-only extraction retained63856 records in11.807 s under90.
All21 missing joins are the recorded startup prefix (source sequences1–21);
no later objective lacks a required exact member. All645 source pins and12
original files/inventory remain unchanged. Both jobs are terminal/reaped.
Read the [D1 handoff](m4_post_v9_integrity_handoff.md) and
[exact validation](validation/m4_post_v9_integrity.md). D1 material checkpoint/
archive PASS: db9c3e1262eb176418fdabc573ce8e401b0da3613c9e4f3206e538c6446538e7,
423 repository files/35 artifact references,1691320-byte verified tar,
3.724403036 s under60. Next is a concrete startup-admission repair and its tests;
endpoint visibility alone was found insufficient to prove producer matching.
No production correction or new acquisition is released. V9 remains failed;
both research goals and all A01–A05 empirical requirements remain open.

V9 material closure COMPLETE: archivefc818ab0...ad759,420repositoryfiles/398refs/
1680256-byte verifiedtar,10.210715831s under60. All206pilotfiles/11rawbags hashed
and retained. Closureaudit/context/diff/checkpoint/linkchecksPASS. No live runtime.
Both research goals/fullV2 remainopen. Next is a saved bounded post-V9 amendment
for the demonstrated blockers; no new experiment or source edit is yet adopted.
Earlier closure preparation and acquisition observations below are history.

Closure audit PASS f3a30ae3...81a07:645 current pins/101 smallrefs/490 recorded
identities absent,0.515175102 s outer under30. Context/diff PASS. Material
checkpoint/archive follows; V9 remains CLOSED_INCOMPLETE and full V2 open.

V9 terminal comparison/report closure. Sole dispatcher77764 terminal1/reaped:
10 COMPLETE/integrityPASS/overallbehaviorFAIL, slot11 INCOMPLETE, slots12–16
UNSTARTED after integrity abort. Slot11 outer graph baseline omitted the exact
shared daemon, while inner recording separately failed21 synchronized atomic-cost
joins (59/60). Both kernel ownership proofs/inner cleanup/finalzero pass; no
recorded owned processes remain. No failure is waived or reclassified.
All16 outcomes/192 targets are retained;0/12 observed latency endpoints and0/6
pairs, all144 holdout direction analyses unavailable. Both label-block timeouts
and all partial data remain retained. No A01–A05 qualification; full V2 stays open.
Read [closure handoff](m4_pilot_v9_handoff.md) and
[result](validation/m4_pilot_v9_result.md). Source645 unchanged; original1333
source passes remain distinct from empirical failures. Independent closure audit,
context/diff/checkpoint and one60s material archive are the next acceptance
boundary; no production edit/new experiment is released before that boundary.

Earlier observations below are history; dispatcher77764 is no longer live.

Slot10B COMPLETE/integrityPASS52/52/behaviorFAIL4/14. SEARCH only, zero confirmed
candidates/typed requests/fills/recovery before Stage A360.026 s timeout. Final
globaldistance3.614588 m; monitor errors absent. Finalzero/cleanup/durable noisy
JSON bindingPASS, case480.726527/900. No score/eligibility breakdown is available
from these receipts. Same dispatcher77764 remains live; slot11C records after
readiness15:16:36.581017Z with exact noisy moving settings verified. Source and
controls remain frozen, no non-detection cause inferred.

Slot9A COMPLETE/integrityPASS48/48/behaviorFAIL4/14. SEARCH only, no confirmations,
fill or recovery; Stage A360.026 s expires, finalglobaldistance3.769821 m. Finalzero,
cleanup and exact durable noiseJSON/witness87e2ea96...ffcb6 PASS, case475.598108/900.
Slot10B records after readiness15:08:33.651707Z; frozen noisy two-block/stationary
configuration verified. Same dispatcher77764 live; source/settings remain frozen.

Noise slot9A records after readiness15:00:36.844664Z. Frozen sigma.015/seed26090803,
zero delays/legacy selectors/control/clocks match; only expected noisy JSON path
relocation occurs, with exact87e2ea96...ffcb6 bytes. Final durable copy/witness is
pending until runner finalization. All645 current source hashes match at15:04:00Z.
Nominal evidence checkpoint under30 s PASS .245235998 s; context/diff PASS.
Same original comparison continues; both completed blocks' science stays unavailable.

Eight V9 recordings COMPLETE/integrityPASS; all overall behavioral targetsFAIL.
Nominal Dslot8 passes61/61 recordingchecks/7of14behavior, onefill/assistedescape,
but repeats live-monitor pending-join timeout and has no ranked goal. Nominal
block1 science is EVIDENCE_UNAVAILABLE after clean labels timeout112.657976764 s;
complete attempted-science ledger/integrityPASS118.631022823 s/220. References
and summary skipped; no retry or promotion of partial files. Same dispatcher77764
remains live and advances to the already released noise block. All gates/source
and controls stay frozen; both research goals remain unproven.

Slot7C COMPLETE/integrity PASS60/60/behavior FAIL6/14. Seven confirmations,
one snapshot/fill and direct-repulse recovery; full Stage B300.016 s observed.
Escape alignment fails the fixed .80 guard, and no ranked goal occurs. Finalzero,
cleanup and process budgets PASS; monitor error absent. Slot8D is recording after
readiness14:50:06.303617Z; same dispatcher77764 live14:50:52.061415Z. Nominal
block science awaits the fourth complete run. Source/settings remain frozen.

Slot6B COMPLETE: recording52/52 PASS, behavior7/14 FAIL. Four confirmations,
one typed stationary fill and assisted recovery; finalVERIFY/no ranked goal.
It repeats development D's live-monitor pending-join regression, so the full
300 s post-recovery window is unavailable despite final recording/cleanupPASS.
Slot7C is recording after readiness14:36:48.705885Z, with frozen nominal moving
settings verified. Same dispatcher77764 live14:38:14.577156Z; all645 source pins
match on the14:36:44Z read-only check. No source/controls/outcomes are revised.

Slot5A COMPLETE: recording48/48 PASS, behavior7/14 FAIL. One confirmation/fill
and assisted escape return to SEARCH; Stage B expires after300.016 s without
a valid ranked goal, despite final global distance .101494 m. Cleanup/finalzero
PASS, case658.991910/900 s; no monitor error. Slot6B now records after readiness
PASS14:28:12.765412Z. Same sole dispatcher77764 confirmed live14:29:12.228285Z.
The live result and validation retain the exact outcomes and hashes. No scientific
qualification or source/control change follows from this descriptive holdout result.

Slot5A, the first secondary nominal holdout, is recording with readiness PASS
at14:17:14.626100Z and exact released controls/geometry/seed26090802/domain201.
Root77764 remains live on direct polling at14:23:37.906422Z; no terminal receipt.
The [live all16 result draft](validation/m4_pilot_v9_result.md) and
[read-only development diagnosis](validation/m4_v9_development_diagnostics.md)
are saved. Existing checkpoint command under30 s PASS at this development
evidence boundary; context and diff checks PASS. No frozen source is edited.

Latest: development analysis ended EVIDENCE_UNAVAILABLE because its labels job
reached the saved work deadline. Cleanup/integrity PASS; partial outputs retained.
The existing one-time gate RELEASED all 12 frozen holdouts without tuning or
replacement (scientific pass is not a release prerequisite). Release SHA-256:
4d877ad7f72c632d7df93a88302cb1d36dd3f2576f091dbed3032fde522d0bf6.
Root session 77764 remains live; do not restart or change frozen source/controls.
D also retains a live centroid-event timestamp matching error despite final bag
integrity PASS; preserve that limitation when reporting its partial recovery.
Both original research goals remain unproven. Read current slot/release receipts.

Latest: all four V9 development runs are COMPLETE with recording integrity PASS.
Combined arm D passes 61/61 recording checks and fails overall behavior (7/14).
It records six confirmations, one fill and one escape; cleanup proofs pass.
The existing dispatcher has started development analysis under its original
220-second block budget. No finalized science result or holdout release exists
at this observation. Root session 77764 remains the sole live execution owner.
Both research goals remain open; the partial D sequence is not qualification.

Latest verified: V9 development slots 1A, 2B and 3C are COMPLETE with
recording integrity PASS and behavior FAIL. C passes 60/60 recording checks;
four PDE confirmations lead to VERIFY then SEARCH, with no candidate snapshot,
fill or escape. Its Stage A expires after 360.026 simulation seconds.
Slot 4D is recording after readiness PASS at 2026-09-10T14:06:46.886025Z;
its combined two-block/rolling settings match the frozen contract.
The same sole dispatcher session 77764 remains live; all 645 source pins match.
Development science and holdouts have not been released at this observation.
Both original email goals remain open: faster settling/trapping detection and
reliable GESC direction during continuous search without mandatory stopped sweeps.
Read current receipts before recovery; do not restart, replace or retune V9.

V9 slots1A and2B are COMPLETE withrecordingintegrityPASS andbehaviorFAIL.
B passes52/52checks, finalzero/cleanrecording; no confirmed detection/fill/escape
beforeStageA360.026simsec. Both endSEARCH; no faster-detection result established.
Slot3C nowrecording afterpreflight/motionreadinessPASS2026-09-10T13:58:32.849212Z.
Same sole dispatcher77764 remainslive with645sourcepins/configurationheld.
Development science andholdouts remainunreleased untilallfourdevelopmentgates.
Read finalslotreceipts before recovery; neverrestart/replace orretune thisversion.

V9 slot1A COMPLETE, recordingintegrityPASS48/48, behavioralFAIL4/14.
No confirmed detection/fill/escape beforeStageA360.026simsec; terminalSEARCH.
Finalzero,target/bag cleanexit and allthreeperformedcleanup checksPASS.
Case478.561413568s/900; no work/absolute deadline exhaustion. This is a complete
behavioral failure, not detector/combined research qualification. Slot2B is
recording afterpreflight+motionreadinessPASS2026-09-10T13:50:29.195711Z.
Same sole dispatcher77764 remainslive; all645sources/configuration held.
No developmentscience orholdout release yet; neverrestart/replace anyslot.

V9 live evidence: slot1A passed recording preflight and motion readiness
at2026-09-10T13:42:26.259721Z and is recording in
pilot/m4_pilot_v9/runs/2026-09-10/m4-pilot-v9-slot01-A-26090801/.
Root77764 remainslive; its original release/source/configuration stayfrozen.
The corrected firstbudget admission has reached real simulation. Live
completenessFalse/run-did-not-finalize is a placeholder, not a terminalfailure.
No finalcase/science/holdout result yet; both researchgoals remainunproven.

V9 acquisition LIVE: sole dispatcher root session77764, ownerPID105626,
timeoutPID105630, launched2026-09-10T13:41:14.151187+00:00.
Owner receipt29eadbe12b6416060dd82a02fc51953760965855d2a98a22d3deb31c5b615521,
release43dce36fc62feafd676782c170e7544e0ecf42c02aa14892b1707fd1eca6fd60,
contract623b6ffa1b8795582138d7d39374ae04f52788beb7c211278ab58a9ee3a0a022.
Independent actualrelease reviewPASS. All645 sourcepins/helpers frozen. Read
builds/m4_v9_budget_comparison_v1/acquisition_execution_v1.json and current
pilot/m4_pilot_v9/acquisition receipts before recovery; never restart or launch
a second dispatcher. Initialfour development slots precede one-timeholdout gates.
No edits/tests/otherROSgraph/Pi actions. Both research goals remain unproven.

V9 prepared archivePASS e07eaa2f3839d081f44e3c1fb42b7e866d0ef6d01c849df2ca960d5604dedbc2:
417repo files/181externalrefs/1638561-byte verified tar,1.115259849s/60.
Context/diff/checkpoint PASS. Exactdispatch releasePASS3.760565226s/30,
SHA43dce36fc62feafd676782c170e7544e0ecf42c02aa14892b1707fd1eca6fd60.
It binds contract623b6ffa...a0a022, source/CLI/preparation/audit andbotharchives,
fixedV6controls/645pins/21bindings/domain201, initial4developmentslots and
one15300s inclusive dispatcher. Holdouts need existing one-time science/release.
Root actualrelease/hashreviewPASS,254GiBfree andnooverlapping Gazebo/pytest/
dispatcher/scenario/recorder process. Independent actualrelease review thenone
attempt next. Source/helpers held; no source edits or newmethod changes.

V9 preparation/frozen audit terminalPASS, rootsession13378.
Preparation53.059032202s helper/53.332698139s outer under600, receipt
713231a26404182f49ded8f52e56cdd2fe5a653ef2a64bb5c9a8b31357a1a896.
Frozen audit4.323064959s helper/4.753220887s outer under30, receipt
 eeff4ed7001368aee97b7134ad25fcbc6dfc50857f441b62b9aeb33757f94bba.
Contract623b6ffa1b8795582138d7d39374ae04f52788beb7c211278ab58a9ee3a0a022.
All16 identities/controls/argv/topology and645sources/21bindings match the
frozen contract; actual fourtopology derivations belong to this sole preparation.
Do not repeat preparation or derive fields for context. Prepared checkpoint/
archive and exactdispatch release next; source/helpers held, no acquisition.

Material source archivePASS6b111c76dccff165ad45038f35839730cb9684a6be203cfa7b3af98ecbdee980:
checkpoints/m4_v9_budget_comparison_source_v1/manifest.json under externalV2,
417repository files/160externalrefs/1636987-byte verified tar;0.763491120s/60.
Context/diff/checkpoint PASS. This live receipt postdates the immutable archive.
One600s preparation and conditional30s frozen-audit LIVE: root session13378.
Source/helpers held. Read exclusive preparation_execution_v1.json and
preparation_v1_receipt.json before recovery; never duplicate preparation.
No acquisition has been released. Both research goals remain open.

V9 combined source milestone CLOSED_SOURCE_VALIDATION_PASS:1333 unique
current-source cases across18 modules;645 identical source pins/21installed
bindings. Focused1136 PASS140.132669052s/180; relevant197 PASS19.113068034s/240;
actualCLI PASS3.576528164s/60. No failed/skipped/unidentified current cases.
Aggregate e65ef0e6e0a7c3751213d3a4e6b21e4fa6cf4a7bd02982695b175bfd1c93c98a;
CLI d5cafb6f0f33d2e061b788ded1e3d2a1092b0bf8c92e6c7b85c0a941a15e601e.
The preserved pre-correction baseline10PASS/3FAIL is excluded from these totals.
All source jobs terminal. Material source archive then one600s preparation is
next; source/helpers held and no acquisition released. Both goals remain open.

V9 focused_v1 terminalPASS1136 unique cases,645sources/21bindingsstable,
0fail/skip/unidentified:137.49s pytest/138.224169301s wrapper/140.132669052s
outer under180. Root session22506 now owns one relevant240 plus conditional
CLI60 after same-source/relevantPASS admission. Source/helpers held; read
exclusive currentbuild receipts before recovery. No preparation/acquisition.

V9 focused source validation LIVE: sole root session27106, one180s command.
Source hold009ae8df4973860972db15a962f9b4e63a757b7d5a681ef9d60a89d43def5cb8:
645pins, exact16changedpaths, allsource/helpers held. Independent budget,
route/workflow/command reviewsPASS; expectedbaseline/capture retained. Read
external focused_execution_v1.json/focused_v1_receipt.json before recovery;
never duplicate. No preparation/acquisition released. Both goals remain open.

V9 pre-edit capture PASS128rows/8versions/642stable,5.574152867s/30.
The accepted baseline10PASS/3FAIL is preserved. Combined source implementation
now changes the dispatcher elapsed-budget predicate and freshV9routes only;
existing deadlines, controls, numerical methods and old evidence stay fixed.
Read m4_v9_budget_comparison_plan.md and validation/m4_v9_budget_comparison.md.
No source tests/preparation/acquisition running or released at this boundary.

V9 budget baseline terminal: expected10PASS/3FAIL in6.142417290s/60,
642sources/21bindingsstable. ExactV8 false rejection and firsttwo one-ULP
budget overruns reproduced. Read validation/m4_v9_budget_comparison.md.
Pre-edit capture then combined elapsed-guard/V9routing next; no acquisition.

V8 material closure PASS5544a2cf123c69fc77a0bb1e04550ac87f7a1640e193f09167b470ee68502ed5:
411 repository files/200 external references/1614974-byte verified tar,
1.058293623s under60. Independent closure audit PASS; V8 stays all16 UNSTARTED.
The combined [V9 amendment](m4_v9_budget_comparison_plan.md) is now adopted.
Next: preserve pre-edit source, capture V1-V8 outputs and execute one actual
dispatcher budget baseline before changing production. One source milestone
combines the elapsed-budget correction and freshV9 routes. No acquisition or
preparation is released; both original research goals remain open.

V8 TERMINAL: dispatcher94339 returned1 after4.740011332s; all16 slots UNSTARTED.
No scenario/ROS graph/recording/science/holdout launched. First-case admission
falsely rejected the exact budget by7.275957614183426e-12s due to absolute-time
subtraction. Source641 pins remain held. Read [V8 result](validation/m4_pilot_v8_result.md)
and [handoff](m4_pilot_v8_handoff.md). Independent closure audit/material archive
next; a future elapsed-budget correction needs its own adopted amendment.
Both original goals remain open. Never resume V8. Older live entries are history.

V8 acquisition LIVE: sole dispatcher root session94339, owner PID101675,
timeout PID101678, launched2026-09-10T13:10:52.852937+00:00. Exact release
6ff1953fb21ee2a3a94528abfdab28acb2c341bd3c33f5802f41ee8a7baa22d9,
contract76bc335518f936e26f2d5f8cac1591d3f28cdfee0e37b94467a4e3ea777a1a9a.
Independent actual-release review PASS. Runtime owner/command is retained in
builds/m4_v8_stationary_causality_comparison_v1/acquisition_owner_v1.json.
Source/helpers are frozen. Observe this session and pilot/m4_pilot_v8/
acquisition receipts; never start another dispatcher or repeat preparation.
Four development slots precede the existing one-time holdout/science gates.
Both research goals remain unproven. No edits, tests, Pi or other ROS graph.

V8 prepared checkpoint/archive PASS: manifest
9533fd0a01d722e5e9dba826d92367c81bbbad4577bef2a9fc017251cb7c45ab,
409 repository files / 154 external references / 1,610,235-byte verified tar;
1.094642424 s under 60 s. Exact dispatch release completed in 3.878563840 s
under 30 s, SHA256
6ff1953fb21ee2a3a94528abfdab28acb2c341bd3c33f5802f41ee8a7baa22d9.
Its contract is76bc335518f936e26f2d5f8cac1591d3f28cdfee0e37b94467a4e3ea777a1a9a.
The release permits slots 1-4 only; holdouts require the existing one-time
post-development gate. It binds source/CLI/preparation/audit/both archives,
unchanged controls, no source changes or replacements, clean domain 200 and
one full 15,180+120 s command enclosing environment setup. No nested 600 s
timeout remains. Root checked no overlapping Gazebo/test/dispatcher process
and 254 GiB filesystem space available before acquisition. All prerequisites
are terminal. Source/helpers are held; one dispatch attempt follows actual
release review. Read acquisition receipts before recovery; never restart.

V8 preparation and frozen audit are terminal PASS (root session37068).
Preparation: 53.971009246 s helper / 54.248191949 s outer under 600 s;
receipt4837c607d4839b7dd540817459953892ee0b349888a7a74d4f5704fee321f1d6.
Frozen audit: 4.323865556 s helper / 4.752669608 s outer under 30 s;
receiptf74be530a81b65936235ca724032d6838f6f4d00007ade5f5005fac3095e7af3.
The contract SHA256 is
76bc335518f936e26f2d5f8cac1591d3f28cdfee0e37b94467a4e3ea777a1a9a.
All 16 slots, four topology receipts, geometry/model/cost receipts, unchanged
V6 JSON/profile/controls, selected launch/recording parameters, original budgets,
641 source hashes and 21 installed bindings pass the frozen audit. No model
or topology calculation was repeated by the audit. No acquisition exists.
Prepared checkpoint/archive and the reviewed exact dispatch release are next;
source/helpers remain held. Four visible development runs precede holdout gates.

Preparation/conditional frozen-audit live owner: root session37068. Exact one600s preparation and dependent30s audit; source/helpers held. Current comparison source archive6570e908...9ae8. Never duplicate preparation or derive topology for context; inspect exclusive receipt before recovery.

V8 material source archive PASS6570e90809e5745d6d1543b51879a51c697c78b0b388f521a719627790359ae8:409repo files/130externalrefs/1608066-byte verifiedtar,0.754374515s under60. Context/diff/checkpoint PASS. One600s preparation now starts under reviewed full clean-domain200 command; one30s frozen audit follows only after preparationPASS. Source/helpers held; no acquisition released. Read exclusive newbuild preparation/frozen-audit receipts before recovery.

V8 comparison source validation CLOSED PASS: 1,232 unique tests across
16 modules, all on the same 641 source hashes and 21 installed bindings.
Focused: 1,035 PASS, 130.33 s pytest / 131.056963942 s wrapper /
132.999971240 s outer under 180 s. Relevant: 197 PASS, 16.49 s pytest /
17.248786757 s wrapper / 19.177910140 s outer under 240 s. No failures,
skips or unidentified JUnit rows. Actual installed CLI PASS: 3.145204276 s
helper / 3.558802363 s outer under 60 s. All processes are terminal.

source_validation_v1.json SHA256
ae68f367d4df0142c4b44e171d9837677500491e0527c5db62a99fafa8b61867;
actual_entrypoints_v1.json SHA256
70efb6f3ef7d0f04287988b3a892075f3cf0650f5f5185fbba395e16c36ea9a2.
The reviewed composer completed once in 0.406526689 s under 30 s. It verifies
raw JUnit equality, unique identities/all 16 modules, exact held commands,
current source and installed bindings, the 13 allowed changed paths and the
112-row pre-edit capture. Retained 325-case stationary-causality evidence and
all older totals are excluded from the new count. No old experiment changed.

Exact commands, logs, JUnit, release and execution receipts remain under
builds/m4_v8_stationary_causality_comparison_v1. Source handoff, context/diff,
repository checkpoint and reviewed material source archive precede one 600 s
preparation. Source/helpers remain held; no preparation/acquisition yet.

Relevant/conditional CLI live owner: root session97274. One relevant240 then CLI60 only after verified relevantPASS/current641 source and installed-binding equality. Source/helpers held; inspect exclusive receipts before recovery. No source/retained-validation reruns or acquisition.

V8 focused_v1 PASS1035 unique tests,641source/21bindingsstable,0unidentified:130.33s pytest/131.056963942s wrapper/132.999971240s outer under180. Relevant_v1 now runs once under240; actualCLI60 follows only after source/binding/PASS checks. Source/helpers held; no preparation/acquisition.

Focused live owner: root session38817, one180s command. Independent workflow peer review now PASS on hold681fa9... and full sourcehold2fad0795... . All641source hashes and helpers held; no other tests, preparation or acquisition. Read exclusive newbuild execution/receipt before recovery.

V8 comparison focused_v1 starts once under180s on641 held sources. Root complete workflow review and independent routes/command reviews PASS; additional peer workflow review read-only. Exact release and exclusive focused_v1_receipt.json under newbuild are recovery authority. No edits, preparation or acquisition released.

V8 routing source is held on 641 exact hashes, with precisely 13 changed
paths relative to the closed stationary-causality map: three routing owners,
seven existing fixture modules (nine future-negative token changes), two new
fixture modules and this comparison plan. Full source hold SHA256
2fad07959bd4d4b9e96e68bcca1123a3114ce6c42e1a8a313850ed08538661e9.
The route scope has independent review PASS; corrected workflow review is the
remaining prerequisite before the one focused bundle. The new workflow fixture
now removes only its added temporary directories as well as files, preventing
synthetic started-holdout state from contaminating later cases.

Preparation-helper review caught incorrectly renamed retained clock-range
references in its unexecuted drafts. All six literals are restored to V7;
original drafts and hold859531... are preserved in preparation_before_review_v1/.
Current preparation_helpers_hold_v1.json SHA256
c8e09a7053308d6843c227edd30ac0720ae9245e2443d2660bab3cb8754b4623
has independent static review PASS. No production correction or budget change
was needed for that draft issue. No test, preparation or acquisition executed.

Pre-edit capture PASS: seven versions, 112 expanded launch/metadata rows,
4.446648578 s helper / 4.840565322 s outer under 30 s (session 52916,
terminal 0). Receipt version_routes/capture_preedit_v1_receipt.json SHA256
6ea6bde7ae18f8a926ae1dbefffeb6d80ed15807a33d88a20b24338f9d9c9ffb.
All 638 source hashes and preserved inputs/copies match before/after. Existing
routing/test edits were released only after this capture. Independent reviews
of capture and exact source commands passed. New source helpers select only
nine focused modules under 180 s and seven consumers under 240 s; actual CLI
under 60 s. Domain 200 and all full clean-command caps are explicit.

Prospective preparation helpers are held unexecuted in
preparation_helpers_hold_v1.json (SHA256
859531d59f0a7053bbae591ac1e2b449fca731f28d6f06e159f33c9defb5353e).
They retain V6 controls and original budgets, bind V7 closure and the completed
stationary-causality archive, and include environment setup within the outer
command timeout. The future dispatcher command replaces the preparation's
600 s timeout prefix with the original 15,180+120 s prefix before env; no
nested preparation timeout remains. This is command binding, not a new
algorithm or deadline. No preparation or acquisition has executed.

The pure pre-edit V1-V7 capture is held for its single 30 s execution:
version_routes/capture_hold_v1.json SHA256
6828cdb5a0fae81b7bb8df3bdbb9fa2d7661b3883e9f784105a78fc5d8c03d30;
helper SHA2565152bad5fe62238df493d1983aefb4df29545f848ab2538030cf77e541f655bf.
The before manifest preserves all 638 source hashes and exact copies of the
three routing owners and seven affected fixture modules. Source is unchanged;
no models, ROS initialization, bag decoding or acquisition is admitted. The
capture command covers clean environment setup within 28+2 s, domain 200.
Its exclusive receipt, not this pre-execution note, determines completion.

Fresh V8 comparison plan ADOPTED: m4_v8_stationary_causality_comparison_plan.md,
SHA256 c33865af92f76aba6bd1eb8d145625e517754f1c8c9f3ba92790540d6cedc1d7.
Prior source/selected recording/archive prerequisites passed. Current work is
fresh identity routing and source validation under unchanged controls/gates.
External build: builds/m4_v8_stationary_causality_comparison_v1. Before edits,
preserve three production owners/seven affected fixture modules and capture
112 V1-V7 expanded rows once under 30 s. Source owners are held until that
capture passes. No V8 preparation/acquisition released; V7 remains closed.

Stationary causality source milestone and material archive are CLOSED PASS.
Context, diff and repository checkpoint passed. The sole reviewed 60 s archive
command completed in 0.725930041 s, exit 0, producing
checkpoints/m4_v8_stationary_causality_source_v1/manifest.json under the
external V2 root, SHA256
6d35c50356baa29201d77b019a1d521a4d0e32f1147ceff5aa8c373c7752f476:
404 repository files, 109 external references, 1,586,594-byte verified tar.
Original bag references are inherited from completed verification/closure;
the archive helper does not reopen those bags. Exact closeout commands and
outcomes are in this build's closeout_checks_v1.json; archive command/log are
in builds/m4_v8_stationary_causality_archive_execution_v1.json and
builds/m4_v8_stationary_causality_archive_v1.log. This live receipt postdates
the immutable archive; no source changed after validation.

Next incomplete criterion: separately adopt the reviewed prospective
builds/m4_v8_stationary_causality_v1/next_comparison_plan_draft_v1.md
(SHA256 a4787bdc645992ae700b24de3f7020479d85364ab572b6d05d2e31de71502de3).
It retains all controls, 16 slots, 192 targets and gates. Its read-only routing
sanity review passed: three production owners, nine unsupported-future test
tokens in seven existing modules. Do not create another source-validation or
retained-recording attempt. No V8 identity/preparation/acquisition is admitted
until the next plan is adopted and its prerequisites pass. No source, test or
simulation process is live. Both original research goals remain unproven.

The sole retained-B verification is terminal PASS (root session 51079,
exit 0): validator 30.570818027 s, helper 32.629807719 s, inclusive outer
32.909106865 s under the original 180 s cap. All 52 returned checks pass.
Only algorithm_event_source_causality and the consequent top-level passed/
failures differ from the original. Every other check, audit, count, warning
and report field is exactly equal. All 11 original inputs, 638 source hashes,
and helper/release/proof hashes remain unchanged before/after.

External build builds/m4_v8_stationary_causality_v1 retains:
- retained_validation_v1/receipt.json SHA256
  22d0f6f9ddbac978401c69349b5c3c6c772203e5da8f4d7d045f5dd8ad467314;
- retained_validation_v1/report.json SHA256
  15cd7ec5e950820ebf9bcc8c1755686f84fdc73e5f910a0b305a238cb343d9d5;
- retained_validation_execution_v1.json SHA256
  b5cec66bdfc340f0350acff5140858b42956cbe270b6bc1514e415de63d25e92.

This closes the selected validator correction, not V7 acquisition integrity
or either research goal. V7 remains 1 COMPLETE / 1 INCOMPLETE / 14 UNSTARTED;
no slot is replaced or reclassified. No labels, direction references, model
analysis, replay or acquisition ran. All processes for this source milestone
are terminal; source remains held for context/checkpoint/material archive.
The next comparison draft is still unadopted.

Retained verification live owner: root session 51079, exact release75a6ae46...93c1c. Independent actual-release review PASS. Read retained_validation_execution_v1.json and retained_validation_v1/receipt.json before recovery; never duplicate.

The current source gate is PASS: 325 unique tests across 10 modules, with
638 unchanged source hashes and 21 installed bindings. The composed receipt
source_validation_v1.json has SHA256
80eca1b9ee666812130d4c0fec1a76a8648a2fe3a23c309cb36f118d1e3461d5;
composition completed in 0.377399198 s under 30 s. Baseline failures remain
excluded. The first composer draft was preserved; review corrected only its
baseline validator-binding comparison before its sole execution.

The exact retained-B release is saved at builds/m4_v8_stationary_causality_v1/
retained_validation_release_v1.json under the external V2 root, SHA256
75a6ae46d9b070effb7ad9c902d611ac3c62653a6396fb6e1d77deca2d393c1c.
One write_report=False verification starts under the reviewed inclusive 180 s
command, clean domain 199. Its exclusive retained_validation_v1/ receipt is
the recovery authority; never duplicate the job. All 11 original inputs and
638 source files are bound before/after. Only the returned causality check and
consequent top-level passed/failures may change. Source and helpers are held.
V7 remains closed incomplete; no V8 acquisition or science is released.

- Current-source tests PASS325 unique across10modules:115focused plus
210relevant. Relevant pytest29.34s/wrapper30.072996808s/outer31.962972371s
under240.638samefinalpins/21bindingsstable,0unidentified or failed cases.
The inherited xunit2 record_property warning remains; actual XML properties
show1clockmin/1clockmax scan for64typed timestamps. Actual CLI PASS3.084157386s
helper/3.496716773souter under60, receipt
8bbea7b7e2c639e31a63a21cf9701ae0ecbeb4044864c0c744c5bac9ce139bdc.
All tests/CLI terminal. Source aggregate composition review next, then exact
retained-B release only after aggregatePASS. No acquisition or replay released.


- Focused_v1 PASS115 in2.40spytest/3.210831036swrapper/5.161008011souter,
638source and21bindingsstable,0unidentified. All25newrouting cases nowPASS;
original18expected baseline failures remain retained. Relevant_v1 starts once
under240s for the adopted7modules including actual stationaryDDS and moving/
legacy recording regressions. Source/test held; no retained job released.


- Validator correction independently reviewed PASS, SHA256
73f897af6460d7ce77512ce27651acaf68237e596c689b85ddfe2ee9234a8ebd;
hold e8983cdc87bab1ac7ca3fd1cc2fd50a343a5de210cfd67175f826577f609df86.
Only validate_run_directory changed since baseline: typed tri-state authority,
malformed/unavailable failclosed, movingfirst/stationarynext/legacyfallback.
Typed checker, fixtures and legacy helper unchanged. Focused_v1 starts once
under180s for the adopted3modules;638source held. Read exclusive receipts
before recovery; no retained verification or acquisition released.


- V8 baseline_v1 reproduced exact18expectedroutingFAIL/7PASS (25cases),
2.54spytest/3.219150343swrapper/5.127563895souter under60.638source/21bindings
stable,0unidentified. Receipt e5f8b628...f520; exactidentityauditPASS. Read
validation/m4_v8_stationary_causality.md. Bounded validator correction now
in progress; tests/typedchecker held. Source review precedes focused/relevant
checks. No test/ROS/acquisition process live and no retained validation released.


- V8 fixture independent review PASS:25cases, held SHA
 af13775cad41703a49cc1c18ecbbe24ad5d1e52e7787c16ed8f4a60da3d79593.
Exact baseline expectation18routingFAIL/7legacy-movingPASS, receipt
0b8d663832ccbdac8db3431c626364cdcdcca6d9bc53e851ea6c5a0904ed6655.
Baseline_v1 is starting once under60s on unchanged validator4165c89d...5414,
clean domain199. Source/test held; no production correction or retained
verification released. Read exclusive baseline receipt/log before recovery;
never duplicate or count expected failures as source acceptance.


- V8 source preparation: root_preedit_v1/manifest.json preserves the636
closed V7 source map and exact validator/workflow/plan copies, SHA256
2175e2ee9718998aa0bd32e09d11bf3b7725863b02355d1f41335fc086de92c0
under builds/m4_v8_stationary_causality_v1. Workflow now has only the
adopted source-plan pin (SHA2fd0e77ba1bb63d42e23e8c50ef450e4440267541fc7a7b1d541146b1396b5c4).
Validator remains4165c89d00adf62fc7f0b49ca7d00f40a5f3c94be0048756b83e3fad3ffb5414.
Source/CLI helpers and exact clean-domain199 commands independently reviewed
PASS, but unexecuted: root_source_helpers_draft_v1.json a160b3f7...e252 and
source_commands_draft_v1.json9426a607...9bf4. Fixture owner is drafting the new
full-validator regression; fixture review and exact expected baseline gap IDs
are pending. No tests, retained verification or new acquisition has run.
Retained-B verification helper is a prospective draft only; never execute it
before final source/CLI evidence and exact release. Both research goals open.


- V7 material closure PASS: checkpoints/m4_v7_closed_incomplete_v1/manifest.json
SHA256ea3fa730800fc55d7d07878b2794c9c39e578a113b80e876898f65061d4f1359,
400repository files/860refs/1571813-byte verified tar. Original2recordings,
16outcomes/192targets remain unchanged. New source amendment ADOPTED:
m4_v8_stationary_causality_plan.md. Reuse selected typed stationary authority
in the existing validator before legacy fallback; preserve strict legacy/moving
checks. Baseline fixtures and source tests precede one read-only retained-B
verification. No V8 identity/preparation/acquisition admitted; no process live.


- Finalized closure audit PASS (not experiment acceptance),0.660437915s/60:
`builds/m4_v7_clock_range_comparison_v1/pilot_closure_audit_v1.json`
under the external V2 root, SHA256
`e5eac2ddd288d15600b2b7c17778b9e08bf1a858d72393fb571429a9b2e9bf9f`.
All636 frozen sources match; exact1COMPLETE/1INCOMPLETE/14UNSTARTED and
all192targets are retained. B has saved successful scenario-inner and outer
cleanup, but no later independent_inner_cleanup receipt; do not claim all
three passes for B. Original completeness, metadata and reports are unchanged.
Material closure checkpoint/archive is next; no source correction yet.


- V7 dispatcher5888 terminal1 after966.142382783s. Slot1 COMPLETE
integrityPASS/behaviorFAIL; slot2 INCOMPLETE due typed stationary request omitted
from legacy event-causality check;14UNSTARTED. No science/holdouts/replacements.
Both recorder finalizations, final zero and inner/outer cleanup completed.
Read m4_pilot_v7_handoff.md and validation/m4_pilot_v7_result.md. Current task:
read-only closure audit/material archive, then a separately saved bounded
validator authority correction. Source held; no ROS/tests/acquisition running.
Both original goals remain open; never restart V7.


- V7 slot1 A terminal COMPLETE, integrity PASS, behavior FAIL;479.304932790s
case elapsed. Slot receipt SHA256
`905431f1e613193a82b6a0bb4f1d4def9df2e60052b18b02aa176d50cf04087e`.
The runner stopped at the unchanged360s Stage A limit without the required
local recovery sequence; its recorder and inner/outer cleanup completed.
This is one valid behavioral failure, not either original-goal result.
Slot2 B has passed recording preflight/motion readiness and is recording.
Same dispatcher root5888 remains live, source/helpers held;14later slots
unstarted and holdouts unreleased. No rerun or parameter change.


- LIVE OWNER: V7 single dispatcher root session5888; release12e2e58f...8756.
Read terminal receipts before recovery; never duplicate. Source/helpers held.


- V7 prepared archive PASS: manifest SHA256
`40a47242060164da79e696cf24cce8c7f07cb71fbde0ce2a4ab3aec8e286b094`,
398 repository files,780 external references,1,565,700-byte verified tar.
Exact dispatch release PASS under60s (3.854682715s), SHA256
`12e2e58fd567d892f294374755cce86c0eff91fde042d00c6cbf584d9e068756`
at `pilot/m4_pilot_v7/preflight/dispatch_release.json` under the external V2 root.
The one dispatcher is starting from its exact saved argv,15300s inclusive,
domain198; initial slots1–4 only, holdouts through existing one-time gates.
All636 source pins and helpers are frozen. Never restart this version or
substitute old runs. Live status is not a terminal result; read acquisition
receipts and run console before recovery. Both scientific goals remain open.


- V7 preparation PASS in 52.617003256 seconds under600; independent frozen
audit PASS in4.324617603 seconds under30. Both processes terminal; no repeat.
Contract SHA256 `12865711f2f7e5cd1c7527dd84220333a44e5a8875489e09796caedf71dc7a7a`;
preparation receipt `2e5edc08e61522d55753ac188d45539fe23d2a9d347928a159ebac4f1824d3c6`;
frozen audit `a3197497a2411cf4a9fe812efb553ccaa1fadffe775f438e7d92aa6eb4024a76`.
Exact16 slots,192 direction targets, four topology receipts, V6 controller
selection, domain198,21 installed bindings and636 source hashes verified.
Prepared material archive and exact dispatch release follow; acquisition has
not started. All source and helpers remain held; both research goals open.


- Material V7 source archive PASS: `checkpoints/m4_v7_clock_range_comparison_source_v1/manifest.json`
under the external V2 root, SHA256
`3ad6855d44397c485845e4d47bfa62e6b39867524d631a915df72221ae17b08c`;
398 repository files, 756 external references, 1,564,211-byte verified tar.
Context validation, diff check and checkpoint PASS. Actual composition receipt
and five preparation helpers independently match existing consumer contracts.
The single reviewed 600-second V7 preparation is now released; read its
exclusive receipt/log before recovery and never duplicate it. Source/helpers
held. Frozen audit and acquisition remain dependent on preparation PASS.


- Composed source validation PASS, 2026-09-10 UTC: 1,422 unique tests across
27 modules, 636 current source pins and 21 installed bindings verified. The
single read-only composition took 0.709 seconds under 30 seconds. Receipt:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v7_clock_range_comparison_v1/source_validation_v1.json`,
SHA256 `397852cb02aaa14017238db6a21a82346f9f31a93dcc725912da5cba83eff164`.
The exact command, held helper, execution result and log are retained beside it
in `composition_release_v1.json`, `composition_execution_v1.json` and
`composition_v1.log`. Independent static review passed before execution.
This is the documented mixed-source-map union, not one test execution;
all failed attempts and their source copies remain unchanged. Current source
validation is closed PASS. Material source checkpoint/archive follows before
one preparation. No preparation or acquisition has run; both goals remain open.


- Source coverage PASS1422 unique tests across27modules, exact620+608+194
union; one actualCLI gate PASS3.166664562s,21bindings/636source stable.
Read m4_v7_clock_range_comparison_handoff.md and validation for mixedmap
scope/retainedfailures. Composedreceipt andmaterialsourcearchive next.
Allprocesses terminal; source held; no preparation/acquisition released.

- Final27module inventoryPASS1422nodes (1.63scollect/2.362082663swrapper).
Exactunioncoverage PASS1422 =620focused+608unaffectedretained+194continuation,
no missing/extra/overlap/anonymouspasses. Receipt72c36168...e2e9d. Current636
sourcepins held; mixedhistoricalmaps explicitly bound byexact3pathdelta.
Original one60s actualCLIgate starting; no ROS/acquisition/prep released.

- Continuation_v1 terminalPASS194 in131.52spytest/132.335975516swrapper,
636pins/21bindingsstable,0unidentifiedJUnit. Root65048terminal0. One
inventory_v1 collect-only for27modules starting under30s; no fixtures/ROS
initialization. Exactcoverageunion required beforeCLI/sourcearchive.
No preparation/acquisition released.

- Boundedsource correction ADOPTED/reviewed:2futureV6→V8 testtokens only,
no runtimechange. Externalwrapper preservesanonymousJUnit asunidentified.
Onecontinuation_v1 starting under240s for2corrected+5unfinishedmodules;
636sourcepins held. Originalfailedrelevant preserved;620focused and
unaffected646broaderPASS retained for exactfinal27moduleinventory audit.
No CLI/prep/acquisition released.

- Broader relevant_v1 CLOSED_INCOMPLETE:root74005terminal124 after225.749s,
646namedPASS/2obsoletefutureV6negativeFAIL; anonymousJUnitplaceholder falsely
countedPASS byoldwrapper (647claim is not valid).636source/21bindingsstable.
Fullfailedsource preserved manifest27f8f468...c022. Namedcasecost218.983s
explains225sinnerbudget; heartbeattransport/tailuncompleted. No runtime
defect established. Boundedtest/receipt correction next after savedamendment;
no tests/CLI/prep/acquisition live or released. Focused620 remainsPASS.

- Broader relevant_v1 remainslive(root74005,240scap) and has reportedtwo
 failures beforeterminaltraceback. Preserve completeboundedrun; no source
 changes or prep/CLI release until outcome/diagnosis. Focused620 remainsPASS.

- V7 focused_v1 terminalPASS620,62.50spytest/63.206025104swrapper;636
 sourcepins and21installedbindings stable. Broader relevant_v1 startingonce
 under240s with23plannedmodules; source held. No preparation released.

- V7 routes/workflow/fixtures independently reviewed PASS. GeneratedYAML
 ordering parity assertion added before tests; priorheldtest preserved.
 Focused_v1 starting once under180s,636sourcepins held; fourplannedmodules
 include79newversion+105newworkflow cases andretainedV6 sourcefixtures.
 Read exclusive receipt before recovery; no prep/acquisition released.

- V1–V6 preeditcapture PASS6populations96launch/metadata rows in4.082757622s
 /30s,633pinsstable. Root88426terminal0,receipt68c450ff...844e. FreshV7
 routing implementation started in existing3owners plus focusedtests;
 no tests/preparation/acquisition released. Capturedoldoutputs immutable.

- Clock-range source milestone is CLOSED/ARCHIVED, manifest5befd6c9...e1e7.
 Fresh m4_v7_clock_range_comparison_plan.md ADOPTED: unchangedV6 gains,
 heartbeat and all controls/gates, freshV7 identities using qualifiedvalidator.
 Before source edits: preserve exact owners and V1–V6 puregeneratedoutputs
 under30 s, no field model. No preparation/acquisition released.

- Clock-range retained validation terminalPASS:49.042393395 s validator,
 52.046186101 s inclusive/180 s;selected<=60s PASS. Whole48-check report
 exactly equal,8originalinputs/633source/helperproofs unchanged. Receipt
 0ab9b5a6...9a03. Source gates171PASS; read new clock-range handoff/validation.
 Material context/checkpoint/archive next; no V7 route/preparation admitted.

- Actual retained release/source aggregate independently reviewed PASS.
 One retained_validation_v1 is starting under180 s using exact release argv.
 Source/helper/input files held. Read exclusive retained_validation_v1/receipt.json
 before recovery; never duplicate. No ROS/acquisition or V7 route released.

- Clock-range source gates PASS171 unique (10focused+161relevant),633same
 stable pins and21bindings. Consolidated receipt7e501c81...c994. One retained
 validation releasee89b0dcb...004c saved for final actual-receipt review;
 command not yet started. It is strictly write_report=False under180 s,
 selected<=60 s, exact48-check report equality plus8input hashes. No V7
 acquisition/identity released; V6 remains closed incomplete.

- Focused_v1 terminal PASS10 (0.46 s pytest/1.070608062 s wrapper),633stable.
 Relevant_v1 is starting once under240 s with the four planned modules;
 original Gazebo E2E excluded. Source held; no retained validation released.

- Baseline_v1 terminal expected9PASS/1scanFAIL (64min/64max),633stable.
 Exact production hoist independently reviewed PASS, validator4165c89d...5414.
 Focused_v1 is starting once under120 s; source held. Read its exclusive
 receipt before recovery; no retained validation or acquisition released.

- Clock-range fixture independent review PASS; original validator remains
 SHA71b1d363...8306. Baseline_v1 is starting under60 s, expected9 semantic
 passes and one scan-count failure (64min/64max vs1each). No production
 optimization or retained-bag validation has been released. Source/tests held.

- V6 material closure archive PASS: checkpoints/m4_v6_closed_incomplete_v1/manifest.json
 SHA25614fcd13e0c19c9b5aeab4f1cfd1708541463d5dca4b9ecd15d4015a82f011773,
 388 files195 external refs1515652-byte verified tar. Closure audit SHA256
 2d59c4e00ccb25a1d83ad9c1873ae8842a0fbc29e1f5de2a3d9f8f3908b55d1b.
 New bounded source amendment ADOPTED: m4_v7_recording_clock_range_plan.md.
 Existing validator rescans all clock values twice per typed timestamp; hoist
 the same min/max once, preserving every predicate and deadline. Next is a
 retained failing scan-count fixture, exact source correction/review, focused
 and relevant validation, then one explicitly write_report=False retained-bag
 validation under180 s after source gates (selected <=60 s target). No runtime
 edits/tests or new acquisition released yet; V6 remains closed incomplete.

- Terminal V6 audit now confirms recorder completeness48/48/final-zero and
 clean target/bag exits PASS, plus full outer ownership/performed cleanup PASS.
 Inner scenario_result/summary/independent cleanup remain absent. Source and
 timestamps support a finalization timing collision: record_run synchronously
 validates after clean wall_end, and completeness publication followed115.12 s
 later; outer workdeadline interrupted inner cancellation shortly before that
 publication. The validator hot path is unmeasured. See
 m4_pilot_v6_handoff.md and validation/m4_pilot_v6_result.md for exact facts,
 unavailable192target/allslotreport and source631 audit. Closure archive helper
 independently reviewed; next archive after durable receipt audit. No new
 experiment/source correction/revalidation or bag replay has been released.

- V6 dispatcher87498 is TERMINAL1 after818.281188141 s. Slot1 A INCOMPLETE:
 outer timed_out=True/return_code254/work_timed_out=True; remaining15 slots
 UNSTARTED. Outer absolute deadline was not exhausted; owned-descendant
 cleanup proof and performed outer graph/identity/session cleanup PASS.
 Recorded runner traceback shows KeyboardInterrupt while inner subreaper
 cancellation awaited shutdown; exact underlying finalization cause is being
 audited from existing logs only. No claim of final-zero/completeness/behavior
 pending those receipts. No block science or holdout release occurred.
 Existing final allslot/192target report is retained REPORTED; no retry or
 replacement. Source/helpers remain held. Read validation/result before any
 new work. Both research goals open; V6 is closed incomplete.

- Slot1 A is recording after motion-readiness preflight PASS. A bounded
 read-only audit of metadata.yaml and resolved_parameters.yaml confirms exact
 full frozen launch argv/new JSON/profile and all algorithm use_sim_time=True;
 recorder/coordinator/evaluator watchdog clocks retain False. Parameter capture
 reports failures=[]. Live completeness still says run did not finalize, as
 expected before termination; no final integrity/behavior/cleanup claim.
 Evidence: pilot/m4_pilot_v6/runs/2026-09-10/m4-pilot-v6-slot01-A-26090801/.
 Same dispatcher87498; all later slots still reserved, holdouts unreleased.

- Single V6 dispatcher live in root session87498, exact release7a69d2e4...
 and contract815b2e3c.... It owns all16 reserved slots and first four visible
 development starts. No other test/ROS/helper may run concurrently; source
 held. Read fresh acquisition receipts and this session before recovery; never
 start another dispatcher. Holdouts remain unreleased pending existing gates.

- Material prepared archive PASS: checkpoints/m4_v6_matched_gain_prepared_v1/manifest.json
  SHA2567712b563463ee5e09ae2442866a69cadb55c8d869adf096d3dd1e8bee66a853d,
  386 files,145 external refs,1510473-byte verified tar. Context/diff/checkpoint
  PASS; independent static archive/release reviews PASS against actual receipts.
  The exact dispatch release helper (session50686) is terminal0/RELEASED:
  preflight/dispatch_release.json SHA256
  7a69d2e465abdbca4511af6110fa0849a7216707abe53564c509223bb09aff09.
  Contract remains815b2e3c0c832f296320471af118e59ba8d189b555d978d45de342b13664b4e0.

  The single existing dispatcher is starting using precisely release.command,
  with exclusive acquisition_dispatch_console_v1.log under the matched gain
  build directory. Source/helpers remain held. Never start a second dispatcher,
  repeat preparation, replace slots or tune after freeze. Initial release is
  slots1-4; twelve holdouts require the existing later science/ledger/freeze
  release. All ceilings and science budgets unchanged. Both goals remain open.

- The single V6 preparation is terminal0 (root session70448), inclusive
  53.815496526 s/600 s. Receipt preparation_v1_receipt.json SHA256
  183e0a6f90a97f8d3e30af9db5339593256aea01b652993498689b6499283829.
  All631 source pins stable and all16 exact slots/four topology receipts frozen.
  Contract SHA256815b2e3c0c832f296320471af118e59ba8d189b555d978d45de342b13664b4e0.
  The one frozen audit (session31823) is terminal0/PASS4.199699212 s/30 s;
  preflight/frozen_audit_v1.json SHA256
  8aab5f12994552ec2744d7aa88f9477a770b017a20a2aad5b12125faf71f2cd1.
  Exact commands are in the separately retained preparation/audit release JSONs.

  No acquisition has started. Preparation/audit must never be repeated. Next is
  the reviewed material prepared archive and exact dispatch release; source and
  helper bytes stay held. Static topology receipts are not behavioral acceptance.
  Both research goals remain open.

- V6 preparation session70448 terminal0:53.815496526 s/600 s, source stable.
 Contract SHA256815b2e3c0c832f296320471af118e59ba8d189b555d978d45de342b13664b4e0.
 The single frozen audit is starting under30 s; preparation must not repeat.
 No acquisition released. Source/helpers remain held.

- The one V6 preparation is live in root session70448 under its600 s cap.
 Source/helper bytes held. Do not rerun preparation or start simulations.
 Next action is consume its terminal receipt, then the single30 s frozen audit
 only if preparation passes. Earlier release/result entries remain history.

- Source context/diff/checkpoint/archive PASS: manifest
  checkpoints/m4_v6_matched_gain_source_v1/manifest.json SHA256
  468966710ea77787eec847b61c9fbd7d77de6fd55002e1a7fc8e9769cf25414d,
  386 files,126 external references,1509008-byte verified tar. The source archive
  helper ran once under60 s. Single preparation is RELEASED under600 s with the
  exact reviewed command/environment from preparation_helpers_draft_v1.json.
  Source and helper files stay held. No acquisition released.

- Matched gain milestone CLOSED_SOURCE_VALIDATION_PASS:1285 unique checks
 across473 focused/612 relevant/200 integrated; actual installed CLI and21
 bindings PASS3.056497822 s. Final631 pins stable. Consolidated receipt SHA256
 a9c77458bc0ce028c9d106e7da8f25f3d4f7868cd90244e25ca55986ec84904a;
 see m4_v6_matched_gain_handoff.md and validation for exact mixed-fixture-pin
 scope, retained failures and all commands. No tests running. Material source
 checkpoint/archive next, before any preparation or simulation. Both goals open.

- Relevant_v2 terminal0:612 PASS/1 Gazebo E2E deselected84.14 s;
 inclusive84.989520806 s/240 s,631 stable pins. Final integrated source
 gate root_final_v1 starting under520 s. No preparation/simulation released.

- Relevant_v2 RELEASED under240 s after independent review verified exactly
 three future-negative tokens across two tests; production unchanged. Read
 exclusive latest receipt before recovery. No preparation/acquisition released.

- Relevant_v1 terminal1:609 PASS/3 FAIL/1 Gazebo E2E deselected82.97 s,
 inclusive83.794273341 s/240 s;631 stable pins. Three obsolete future-negative
 V6 test identities in v3/v4 modules are retained then changed only to V7;
 all assertions/cases and production unchanged. New relevant_v2 held pending
 narrow review under the same240 s cap. Focused473 passes remain applicable
 to unchanged selected source. Exact failure and correction in matched-gain
 validation; no test or simulation now running. No preparation released.

- Corrected focused_v2 terminal0:473 PASS34.61 s, inclusive35.422159493 s/180 s,
 all631 pins stable. Relevant_v1 is starting under240 s; no duplicate tests or
 source edits until receipt. No preparation or simulation released.

- Corrected focused_v2 source bundle RELEASED under the same180 s cap.
 Both owner hold maps and final workflow/test hashes match independent review.
 Read its exclusive receipt/log before recovery; never repeat focused_v1 or
 start a duplicate attempt. No preparation or simulation released.

- Both corrected owner holds pass independent review with current hashes.
 Root workflow additionally restores original hash-bound YAML override order
 when verifying sorted contract JSON; exact resolved values and full launch
 argv equality remain required. Two new tamper cases and explicit JSON
 roundtrip assertions are held for final review before focused_v2 under180 s.
 No test or simulation process is running at this note. Earlier focused_v1
 remains terminal124 and preserved. External preparation/archive helpers are
 being drafted only; no preparation or acquisition has been released.

- First matched gain focused bundle CLOSED_FAILED_TIMEOUT: session2933
 terminal124,335 PASS/1 FAIL in164.90 s, wrapper165.717996563 s/180 s,
631 stable pins. Receipt SHA256
 `184478b9d09c070b9bc68e651fb8cc9e76cdc3ff96cf8a0945654b78a4e457a0`.
 Exact reviewed source/helper/plan snapshot retained12 files, manifest SHA256
 `ac5f3d2b5a4b007df44bfbb3eb91424c540989ee9ba6905057e11ecbf7af3f9e`.
 The fixture expected one recorded_profile expansion but the resource has two;
 correct it to cover both. The fixed timeout interrupted YAML parsing. Reading
 the held source corrected the initial diagnosis: V6 already caches both
 templates per call, with just one redundant primary reread. Reuse that local
 snapshot and preserve fresh hashes on each call. The repeated full16-case
 schema fixture setup is being moved to one pristine module fixture, with
 fresh deep copies/identity binding per test and every assertion retained.
 This bounded correction is saved in `validation/m4_v6_matched_gain.md`.
 Source owners are correcting; no tests running. New focused_v2 remains held
 pending review under the same180 s cap. Remaining cases are not passes;
 no preparation/acquisition or scientific qualification is released.

- Matched gain source edits and independent review are complete; the first
 focused180-second bundle is live in root session2933. Source/plan files held;
 read `builds/m4_v6_matched_gain_v1/` receipts before recovery and never duplicate
 a test attempt. Controller hold SHA256
 `af7f315d372be77d4340cda66f0a70e490fbff4ad5961089de5f5f50b718267d`;
 version hold v3 SHA256
 `7b1087252102ffa63b9efd3718aedc1ac191fb855255d52c807f2d261220a87f`.
 Review closed exact full override/launch/metadata binding, including rejection
 of extra freshness/gap overrides. The two earlier untested version holds remain
 retained. Root workflow adds exact controller receipt and all16 launch/metadata
 verification. No source qualification, preparation or acquisition yet.

- Fresh comparison source amendment ADOPTED: `m4_v6_matched_gain_plan.md`.
 Select one new simulation JSON with k_vx=0.5 (from1.0), unchanged k_wz=5.0
 and speed ceilings0.1 m/s,0.5 rad/s, matched across all16 V6 slots; B/D select
 the validated invalid-status heartbeat. Existing detector/M3/science gates,
 v5 topology/interior fallback, seeds and caps remain unchanged. This is an
 unproven motion hypothesis. Source implementation is next; preparation and
 acquisition are not released. No centering assist or shared-ceiling change.
 Heartbeat context/diff/checkpoint/archive all PASS before adoption: manifest
 `checkpoints/m4_v6_centroid_heartbeat_source_v1/manifest.json` SHA256
 `0ad0ce175057d6ec5e732246f021295757e12285849c2b76f92fb528897c69a3`,
 379 files,65 external references,1484811-byte verified archive. That source
 boundary remains immutable; new edits belong to the matched gain milestone.

- Heartbeat source milestone CLOSED_SOURCE_VALIDATION_PASS, 2026-09-10 UTC.
 Final corrected source: 56 focused + 155 binding/clock + 4 root consumer
 checks PASS (215); 475 unique passing identities across retained source
 versions. Root gate completed23.53 s / 24.450589563 s inclusive, within120 s;
 session8325 is terminal0. Root receipt SHA256
 `913b73b4a649ca0321cd64b91d2510dc7439893d41871c6dc3752230a14b0d76`.
 Owner hold SHA256
 `2c51e6ec4761669bb62bd211996b39aea23ee8ef7affad62ab5ea7be59ef10ac`.
 All625 final pins stable; exactly5 old source files changed,618 unchanged.
 Independent review closes the clock-frontier blocker. Final actual consumer
 assertions/process pass with a retained inherited asynchronous Destroyable
 diagnostic; exact callback timing/drain proof is unavailable. See
 `m4_v6_centroid_heartbeat_handoff.md` and its validation for exact evidence.
 No simulation is released. Next is material checkpoint/archive, then a
 separately adopted fresh matched gain comparison; no research target is met.
 Earlier live tests/correction notes are retained history.

- Heartbeat independent review found a real status-only purity defect:
 `centroid_ready()` called the binding clock owner and could advance its
 frontier or trigger a rollback reset. The pre-correction regression retained
 2 FAIL / 0.79 s with stable pins; receipt SHA256
 `c9e575c40f7ab916612f22f191e034e68390d791db1d4c4ea81414253068e77d`.
 The narrow `v2_binding.py` captured-time readiness extension is now adopted
 at the end of `m4_v6_centroid_heartbeat_plan.md`, implemented and under a new
 240-second focused bundle, session12324. Existing no-argument behavior is
 preserved. Seven-file pre-correction manifest SHA256
 `81873b3fd2c6a2d65b5e3085ccb6eeed312e645c4f96b62a711806a756271dce`.
 Earlier focused/relevant passes are intermediate: relevant_v1 had 369 PASS
 in 55.76 s, and the strengthened four-cycle fixture passed before this
 correction. Read newest receipts; do not repeat or edit live source.
 Root's final 120-second consumer gate is prospectively saved in
 `validation/m4_v6_centroid_heartbeat.md` and remains pending. No simulation
 is released. A gain-only matched configuration is a next-version proposal,
 not an implemented or validated motion improvement.

- Heartbeat source tests, 2026-09-10 UTC: the single old-default DDS baseline
 completed with 4 PASS / 12 deselected in 25.08 s (25.919240719 s / 45 s).
 Those assertions retain the expected existing coverage failure; they do not
 classify the old publication route as complete. All 623 runtime pins plus
 the staged test were stable. Baseline receipt SHA256
 `ed0efaecf2b55b53f2e5d84865dc94486e8a1d6559c7945d5f81951ebacf6a4b`.
 The first implemented focused bundle is terminal: 42 PASS, 5 FAIL,
 4 deselected in 65.68 s, 66.6256 s / 240 s, with 625 stable pins.
 Receipt SHA256 `3bdc7f47eb6dd890e08ad4a192de9c4400f1fc2db92371845eeab74c80721657`
 under `builds/m4_v6_centroid_heartbeat_v1/`. The owner is correcting the
 retained fixture failures (Humble exception type and missing selected argv
 bindings), with production unchanged and a new exclusive focused receipt.
 Independent source review is active. No new simulation is released.

- Active source amendment `m4_v6_centroid_heartbeat_plan.md` adopted after
 conditional reconstruction closure. Default-off invalid-status heartbeat
 through existing detector/watchdog, selected launch/scenario/recording binding
 and actual DDS/legacy tests; strict coverage and numerical guards unchanged.
 Source owner released to retain the45s old-gap baseline, implement and run
 finite240s focused/240s relevant regression bundles on reserved ROS domain189.
 No fresh version/acquisition released. Read later test receipts before recovery.
 Source changes now belong to this amendment; the prior623-pin diagnostic
 boundary remains immutable evidence, not a prohibition on this released fix.

- C/D conditional reconstruction CLOSED_DIAGNOSTIC_COMPLETE: fixture21PASS,
 C81.303188809s andD64.256769546s, total147.992578867s/305s. All11 windows/
70 evaluations retained, all623 source+5 helper+51 input pins stable. Hold
 SHA256 `6984b2b34791326d551e39c68e3d32a0d83ad618191d2d6857cac69c7ee20f43`.
 D session91783 terminal0, result SHA256
 `0b2bc60cb5999619ff18ade0e5ec0566a09cf5538357d4d60e6b237f2bb44c46`;
 receipt SHA256 `2adaa756ecdd39c947e6a3b650a0f48d5ef11b112dde57c3b4d1d227da1b2926`.
 All42 D evaluations lack qualifying neighborhood cycles despite complete
 sensor revolutions; no D cycle passed both neighborhood guards. C first
 candidate lacks3; later3 fail raw-profile information. Conditional schedule
 limits remain; no exact callback causality or research result is inferred.
 Root rechecked all623 pins before releasing the independent heartbeat fix.
 See `validation/m4_v6_raw_evidence_reconstruction.md`; no retries or bag reads.

- Conditional C reconstruction terminalPASS, session32526,81.303188809s/130s;
 all pins stable. Frozen11-window SHA256
 `639927e680b8cff0a961c9887c7ffb27d16b10a5329af4c55f67b948bfd9f964`.
 C result SHA256 `cf8204333ca369fb993a31bafd5f510c7005dd7ca71a33317a9081d6d89bce3a`;
 wrapper receipt SHA256 `1c38bb4cd451be99ef23cbeecf46346450d182ccf3c6bdc21828b0da8e5c7990`.
 Each of4 candidates has7 scheduled evaluations: first candidate always
 lacks3 qualified neighborhood cycles (maximum2); later3 always fail raw
 profile information. These are conditional reconstructed guards, not recorded
 callback causes or research outcomes. One D reconstruction is live in
 session91783,130s inclusive; never repeat either arm. Source623pins held.

- Conditional reconstruction exact review/release complete. Fixture21PASS
 1.38s, wrapper2.432620512s/45s,623 source+5 helper+51 input pins stable.
 Fixture receipt SHA256 `19adffe199c497386a86061baad9c1bab36f7af21bbb3f30b3f314381307feaf`.
 One C job started in session32526 under the prospective130s inclusive cap;
 do not duplicate it. D remains conditional on this C job's terminal PASS.
 Read `builds/m4_v6_raw_evidence_reconstruction_v1/` execution receipts first.
 Reviewed manifest SHA256 `2e9753a7e58f0e59cfc7715f4657222a7a5343f67a56bb32985cb7d87ed34744`.
 Source held; no runtime correction or acquisition released. Earlier held-
 execution notes below are superseded by this exact single-attempt release.

- B recorded-motion diagnostic plot COMPLETE: one finite30s command exits0
 in4.345530599s; all10617 pose+10718 diagnostic rows represented,623 source
 pins unchanged. Rendered PNG inspected: repeated loops after approach while
 the score stays above0.18m despite passing confinement through much of the
 later motion. No period fit, basin labels, new threshold or research claim.
 See `validation/m4_v6_b_motion_plot.md`; original evidence stays unchanged.
 The separate C/D reconstruction remains the active next execution boundary.

- Active V6 conditional reconstruction: adopted separate
 `m4_v6_raw_evidence_reconstruction_plan.md`; external helper/fixture work only
 under `builds/m4_v6_raw_evidence_reconstruction_v1/`. Execution HELD pending
 root review/release. All4C+7D windows, including finalD censoring, must be
 frozen before evaluating unchanged moving owners under one explicit assumed
 delivery schedule. No original bag read or runtime source edit;623pins held.
 No exact callback-causality or research claim may follow from this diagnostic.
 A separate external invalid-status heartbeat source draft is prepared; it is
 not yet an adopted runtime amendment. Earlier diagnostic extraction is closed.

- V6 descriptive diagnostic CLOSED_DIAGNOSTIC_COMPLETE,2026-09-10UTC:
 all three single B/C/D extractions are terminal PASS;176845 full recorded
 rows retained,62.487642523s total including fixtures within255s. No retries.
 All623 source pins and33 original files match before/after/exit. Hold receipt
 `builds/m4_v6_development_diagnostic_v1/diagnostic_hold_v1.json` SHA256
 `42e32d584ed83aeab934ac5d2739cf2451af2ca0707b4e2909a14f93f6b2be24`;
 result SHA256 `67a7138755429f39f9ef58e93d6763dc4034a29e295dc3b3224514cf31754104`.
 B's9442 valid histories all fail score<0.18m (minimum0.289676733m).
 C/D retain generic cancellation reasons; precise M3 guards remain unrecorded.
 D's unchanged coverage check reproduces six12s gaps and one9.6s exit gap,
 descriptively aligned with VERIFY. See `validation/m4_v6_development_diagnostic.md`.
 Root rechecked39 hold references and all623 current pins: no mismatch.
 `timeout 30s .../validate_phase_context.sh v2 implement`, `git diff --check`
 and `timeout 30s .../checkpoint_phase.sh v2` PASS at this material boundary.
 Next: separate finite existing-owner reconstruction of all4C+7D candidate
 windows from extracted payloads, before selecting evidence-based corrections.
 Source remains held; no runtime correction or fresh simulation released.
 Both original goals remain open. Earlier released/running notes are history.

- V6 diagnostic export fixtures PASS10 checks0.319s (wrapper1.149968581s,
 45s allowance),623 source+3 helper/fixture/driver pins stable. Receipt
 `builds/m4_v6_development_diagnostic_v1/fixture_receipt_v1.json` SHA256
 `b4d6f7f2e287409b8fce7e503efc176e6d8ea97e398a3c9ad5382491f6102e2c`.
 Root independently reviewed final helper/fixtures/alias metadata. Finalhelper
 SHA256 `06cc810f2f907486224a22107df69a71705bf00ca71047ac70e6801d5a2c8e6c`.
 Released exactly one read-only B/C/D extraction each under the adopted plan,
 sequential70s inclusive limits/no retries. Read newest external execution/
 per-arm receipts before recovery; do not duplicate attempts. All623pins held.
 No new source correction, scientific evaluation or simulation is released.

- M4v5 closure archive complete: context/diff/checkpoint PASS,368 files,
 291 external artifact references,1441482-byte verified tar. Manifest SHA256
 `e8d66d8f801f96a0223ef19aa2658f9fc73921f57a030d9b3fa759f09a334a12`.
 Adopted `m4_v6_development_diagnostic_plan.md` before new bag reads: one
 bounded existing-reader extraction each of closed B/C/D, exact original/source
 hashes and explicit nonfinite serialization. Diagnose B score eligibility,
 C/D recorded verification reasons and D publication gaps separately. No
 scientific rerun, source correction or acquisition released;623pins held.

- M4v5 CLOSED_INCOMPLETE: dispatcher21069 terminal exit1 after1923.637061631s.
  A completePASS14/14; B/C completeFAIL; D incomplete,12holdouts unstarted.
  D sole completeness failure is centroid publication coverage; finalzero/
  target/bag shutdown/performed cleanup/both kernel proofs pass. Seven D
  confirmations, zero snapshots/fills; no cause inferred for missing M3 evidence.
  No block science/holdout release/replacements. All16 outcomes/192targets
  retained with unavailable research metrics. Read `m4_pilot_v5_handoff.md`
  and `validation/m4_pilot_v5_result.md`. Closure audit623pins/87files stable,
  SHA256 `b4b7f13c5250ef8243e8c5a7205d38f2ee94c6cce899ae22cd72d464968bd109`.
  Next: closure archive and separate bounded diagnostic/source correction.
  Source remains held through archive; never restart the closed dispatcher.

- Independent closed-v5-C audit confirms exact bindings/all8 input hashes,
 60/60 completeness checks, finalzero/recording/all3 cleanups/both8/8 kernel
 proofs PASS. Four typed/legacy confirmations; zero candidate snapshots,
 fill commands/results/Gaussian fills/legacy requests. Typed lifecycle/event
 causality passes but committed-fill authority is unexercised. Existing small
 summaries do not give a specific M3 rejection reason; no cause invented.
 Slot4D live under dispatcher21069; source/settings held and science pending.

- M4v5 slot3C COMPLETE/integrityPASS/behaviorFAIL:507.923945731s,4/14
  predicates pass. Four convergence confirmations each lead VERIFY→SEARCH;
  no fill/escape, terminalSEARCH. Fixed StageA360.026simsec expires
  (0.495→360.521). Slot receipt SHA256
  `d12975279e3e7001980f26b677d6f5db258e8df2f25b80c188d4bf65d67ca292`.
  Same live dispatcher21069 proceeds to slot4D with held source/settings.
  Detailed verification rejection cause is not inferred from state sequences.
  No block science/holdout release yet; both research goals remain open.

- Independent closed-v5-B receipt audit confirms COMPLETE/integrityPASS,
  behaviorFAIL. Exact summary/identity/settings and all8 closed input hashes
  match. All52 completeness checks pass, including10718 centroid diagnostics;
  zero confirmations/fills/escape starts, terminalSEARCH. Finalzero, finalized
  recording, target/bag exit0, all3 cleanups and both8/8 kernel proofs pass.
  Recording375.411s/720s; outer exit1 is the retained behavioral failure.
  Slot3C is live under dispatcher21069; no scientific analysis has run yet.

- M4v5 slot2B COMPLETE/integrityPASS/behaviorFAIL:507.67642889s,4/14
  predicates pass. Fixed StageA elapsed360.026simsec (0.527→360.553) expires;
  no completed local recovery or goal. Receipt SHA256
  `2efc7621f68b5070b2ea07dacedd67045e420e4e789346e00ad6c1efc81b052c`.
  Same live dispatcher21069 proceeds to slot3C under frozen source/settings.
  Complete behavioral failure remains an outcome; no replacement/tuning.
  Independent block science and both research targets remain pending.

- Independent closed-v5-A receipt audit PASS: exact identity/config/summary,
  all8 closed input hashes,14/14 predicates and48/48 completeness checks.
  Finalzero, finalized recording, target/bag exit0, all3 performed cleanups
  and both8/8 kernel proofs pass. Case401.905s/900s; recording289.311s/720s.
  GOAL_HOLD, final distance0.1413m;2 confirmations/1 fill/assisted escape.
  Preferred outside-radius anchor used; interior fallback unnecessary in A.
  Contact evidence unavailable, so no whole-trajectory clearance claim.
  Slot2B recording under same dispatcher21069; source623pins remains held.

- M4v5 slot1A COMPLETE/integrityPASS/behaviorPASS: all14 predicates pass,
  elapsed401.904648893s. Slot receipt SHA256
  `81cfcb96da819556813d018c59369f8a426ed45104b4e52d9131a30c55005cfd`.
  The same live dispatcher21069 proceeds to slot2B; never restart. All
  controls/source remain frozen. Baseline success is selected-case evidence;
  block science, two-goal comparisons and holdout release remain pending.

- Live M4v5 dispatcher session21069 owns the single released attempt.
  Console: `builds/m4_v5_moving_fill_v1/acquisition_dispatch_console_v1.log`.
  Do not restart on an empty poll; observe terminal process/receipts first.
  The initial case is baselineA. Source623pins/settings held throughout.

- M4v5 exact dispatch release saved and validated. Preparation archive SHA256
  `557397cd2d94526c12139bd1c95b23a41ae19e46c28c2d4f374f2aa28700ddbb`
  binds366 files/214 artifacts/1435978-byte verified tar; context/diff/checkpoint
  PASS. Independent read-only preparation review verified623 pins, four exact
  topology records, original sources/start/bounds and5730 geometry point hashes.
  Release SHA256
  `c4b5038975acc7b9c71b1eaab4731a17f24fd7c081b1edb748f09bed9eba3853`.
  The single released dispatcher is starting under15180s SIGINT+120s kill cap,
  clean Q2→Q5/domain186/localhost1/DISPLAY=:0. Read fresh v5 acquisition receipts
  before recovery; never start another dispatcher. Source/settings held.
  Four visible development slots precede one-time twelve-holdout release.
  Both original goals remain unproven; earlier release-pending notes are history.

- M4v5 single preparation PASS52.284768937s (session98742 terminal0),
  frozen audit PASS3.061765128s (session25341 terminal0). No retry/numerical
  re-audit. Contract SHA256
  `42a7b57afcec26e8e4b643cacc0d71895e037c7b3129cb66cd37e26d0580f08e`;
  audit SHA256 `27ab78221405ffc61fb225694ba482aad99d7a770da4ef3c84d92f66f103f19e`.
  All623 pins/16 exact slots/four topology records/original geometry match.
  Real primary static topology admission passed unchanged numerical/schema
  thresholds; optimizer flags and limited static meaning retained in validation.
  Next: preparation archive and exact release. No acquisition started;
  preparation must not repeat. Source held; both research goals remain open.

- M4v5 source archive complete: context/diff/checkpoint PASS;366 source files,
  199 external artifact references,1434455-byte verified tar. Manifest
  `checkpoints/m4_v5_source_closed_v1/manifest.json` SHA256
  `35329d0a6fd68d813797a9e7328877581d8eadc5003efd2c42e3a2281844fe26`.
  Independent read-only reviews matched all623 current pins,1500 JUnit outcomes,
  final authority/version holds and copied drivers; no source blocker.
  Starting the single600s preparation using the reviewed exclusive helper,
  clean Humble→Q2→Q5/domain186/localhost1. Source remains held; no acquisition.
  Check `builds/m4_v5_moving_fill_v1/preparation_v1_receipt.json` and fresh
  `pilot/m4_pilot_v5/preflight/` before recovery; never repeat preparation.

- M4v5 source CLOSED_SOURCE_VALIDATION_PASS: session51864 terminal0,
  1500 unique tests PASS337.01s,1 existing Gazebo E2E deselected; wrapper
  337.978001067s within520s cap. All623 pins unchanged before/after/current.
  Final receipt SHA256
  `4d68036db37e934c43d1dedbcedc3dcc37e40ea927aa2037a82e1a66353ba210`.
  Actual installed CLI and21 Q5 entrypoint checks PASS. Read
  `m4_v5_source_handoff.md` and `validation/m4_v5_moving_fill.md`.
  Next: source checkpoint/archive, one600s real preparation, frozen audit
  and exact release. No v5 preparation/acquisition yet; source held.
  Both research targets remain unproven. Earlier running entries are history.

- M4v5 final integrated source validation RUNNING in session51864 under outer
  timeout520s / pytest480s plus10s kill allowance. Command: clean Humble→Q2→Q5,
  domain186/localhost1, external `root_source_validation.py root_final_v1`.
  Do not start another suite or edit pinned source while it runs. No actual
  topology preparation or acquisition has started. Scope audit v2 PASS:
  623 pins,608/618 prior files unchanged,10 expected prior changes and5 new
  pins; SHA256 `24f0f2aa924a6ddf1fbb9bfcfd01918ad4d80b596e84c4e9924429e8c1c6a57d`.
  Latest typed authority hold v3 SHA256
  `20d375708160d25ca04c263027c9f1b8e770838071d10f03da4096ec13818f49`
  preserves184PASS56.85s and affected11PASS7.41s after final strictly newer
  retry-sequence correction; all reproduced failures retained. Final combined
  suite covers the final bytes. Existing schema/numerics/runtime owners held.

- Independent M4v5 review found a selected retry-consistency gap before source
  release: repeated registry generations were accepted on commit payload before
  checking new-sequence ALREADY_ACTIVATED semantics/original transaction identity.
  Preserve the172PASS intermediate hold; add a failing fixture then the minimal
  selected-only correction within the adopted conflicting-retry contract.
  Distinct old/new confirmation-source redesign coverage is also added.
  Moving escape production/tests remain held. Primary topology/schema routes
  pass373 focused checks58.90s with numerical/geometry work explicitly mocked;
  final route/source checks remain pending. No preparation/acquisition started.

- M4v5 typed-fill authority source/tests held after172PASS46.98s with stable
  pins. Receipt `builds/m4_v5_moving_fill_v1/typed_authority/consumer_hold_receipt_v1.json`
  SHA256 `cce3136e18b70b3751bbae7e37cd59b5f310881ec14282059acb586673c95a8a`.
  Strict selected lifecycle/source/event chain passes actual-owner/transport
  and adversarial fixtures; legacy helper/default and historical transport
  test bytes remain unchanged. All baseline/fixture failures retained.
  Guarded escape78PASS remains held. Primary topology route, independent review,
  combined source validation and source archive still precede preparation.
  See `validation/m4_v5_moving_fill.md`; no v5 numerical or acquisition job ran.

- M4v5 scenario prerequisite adopted before correction/numerical execution:
  `m4_v5_primary_topology_amendment.md`. Actual unchanged schema14 requires
  verified-trap topology when interior fallback is selected; primary v8.10
  still used declared_source. Add one exact v5 primary nominal record through
  the unchanged numerical owner inside the same600s preparation; no new
  label geometry or relaxed gate. All4 primary arms share the stricter binding.
  No matching retained primary receipt was found, and no preparation started.
  Guarded moving integration passes78 checks86.25s with stable source/test
  pins; source release still awaits topology route and recording validation.

- M4v5 source amendment adopted before edits: `m4_v5_moving_fill_plan.md`.
  The initial diagnostic export failed on invalid-field NaN serialization;
  its original outputs/failed receipt remain under `diagnostic/`. Separate
  `m4_v5_diagnostic_export_correction.md` extraction PASS 4.424504s (read1.119386s),
  all11 C inputs/618 source pins unchanged. Receipt SHA256
  `d1ac26282e4282dcfebab19e889e6c72c68f6d5c2605bcb0a36da745f4b4e8ef` under
  `builds/m4_v5_moving_fill_v1/diagnostic_export_v2/receipt_v1.json`.
  First FAILSAFE152.2s explicitly reports no retained pose outside frozen exit
  radius; commit152.0/bothACK152.1 precede it, later stale-input events follow.
  Implement strict typed event/source causality and prospectively select the
  existing >=0.50m bounded interior-anchor alternative for all4 v5 arms.
  Defaults/old versions/safety guards/science thresholds stay fixed. Actual
  producer/transport/shared-transition validation precedes new release.
  No v5 preparation/acquisition started; full two-goal comparison remains open.

- M4v4 material closure archived: SHA256
 `21243aa35a666896d59ec6bbb748985487aa0855d58d9bab765f80a017ab529b`,
 356files/137artifacts/1399475-byte verified tar. Context/diff/checkpoint PASS.
 Adopted `m4_v5_moving_fill_diagnostic_plan.md` before any diagnostic bag read:
 one finite existing-reader extraction of closedC event/transition/transaction
 details, exact hashes before/after, no science reevaluation or result change.
 Source/controls stay held; no escape alternative selected or new acquisition
 released. A precise implementation amendment follows recorded diagnosis.

- M4v4 CLOSED_INCOMPLETE: dispatcher terminal exit1 after1598.156786s.
 A/B complete with behaviorFAIL, C incomplete,13unstarted; no block science,
 holdout release or replacements. C canonical mirror/lifecycle check PASS;
 one candidate/fill committed and both acknowledgements observed. Only
 completeness event-request-source causality fails59/60; selected moving
 route has no legacy fillrequest. Finalzero/recording finalization/kernel/
 performed cleanup PASS; independent-inner not reached. Runtime then FAILSAFE
 with no escape; exact reason requires bounded recorded-detail diagnosis.
 See `m4_pilot_v4_handoff.md` and `validation/m4_pilot_v4_result.md`.
 Closure audit SHA256
 `70218bb13c270e37406537927e5870f6d12249a885f6b3195bf5e1ee075f561a`
 binds618 unchanged pins and73files/981393641bytes. Source held until closure
 and separate amendment; never restartv4. Both research goals remain unavailable.

- M4v4 slot2B COMPLETE/integrityPASS, behaviorFAIL in491.238070s.
 Exact two-block/stationary settings and frozen bindings match. Typed centroid
 diagnostics10654; no confirmations, stationary requests or fills. SEARCH ends
 at fixed StageA cap360.060sim seconds; behavior4/14. Completeness52/52,
 finalzero/target/bag, both eight-flag kernel proofs and all three performed
 cleanup checks PASS. One guarded groupSIGINT, no escalation. Slot SHA256
 `0da46ff69109020d741916c470bfb503ae994b3ebb93e9776affea6bd02ac249`.
 Same dispatcher continues slot3C. Source/settings held; this complete failure
 is retained, with primary science/latency qualification still pending.

- M4v4 slot1A COMPLETE/integrityPASS, behaviorFAIL in627.797797s.
 Local assisted recovery/one fill/command ownership pass, but fixed300.016s
 post-recovery window (sim176.415→476.431) ends without accepted ranked goal.
 Behavior7/14; final monitor proximity0.281699m is not an admitted goal result.
 Recording/finalzero/target/bag pass, completeness48/48, both eight-flag kernel
 proofs and all three performed cleanup inspections PASS. One guarded inner
 groupSIGINT, no TERM/KILL. Slot SHA256
 `780a41eb35c429cc2528a50fb37347109ca8d9a541fcd5937f506483f50660b9`.
 Root finalized-input/source audit PASS2.005012s,8inputhashes and618sourcepins:
 `builds/m4_v4_confirmation_mirror_v1/first_slot_audit_v1.json` SHA256
 `78a987e7c1610ed3a5eecb66cf19d16e9ebdd24235c105fa552a27741c1d6ce9`.
 ArmB slot2 is running under the same dispatcher; no source/settings change,
 replacement or extra science. Primary targets await frozen block analysis.

- M4v4 exact dispatch RELEASED; its single acquisition is starting. Release
 `pilot/m4_pilot_v4/preflight/dispatch_release.json` SHA256
 `9bbd3ff4dd3ea56abb2141b721e7e7491ad76465891a00fab1508ab05fa75135`
 binds exact contract/source validation/CLI/frozen audit/source/preparation
 archives and initial slots1–4. Preparation archive SHA256
 `d4642c4abca9116f1b67d577db47653a3458065920bff70073bd6e5484c23a43`;
 354files/73artifacts/1394155-byte verified tar. Context/diff/checkpoint PASS.
 Canonical command SIGINT15180s/kill-after120s bounds15300s maximum. Console
 `builds/m4_v4_confirmation_mirror_v1/acquisition_dispatch_console_v1.log`.
 Source stays held. Read fresh acquisition started/slot/final receipts before
 recovery; never restart or replace a slot. Holdout release remains separate.

- M4v4 single preparation PASS43.964598s within600s; independent frozen audit
 PASS3.060121s, no model reevaluation/bag decoding/acquisition. Contract SHA256
 `4ab2883e73654bbd2c1a5626fcf296316f790f7c1c3a11de063f8e85d8cf055d`;
 prepared receipt SHA256
 `5eb675d8922a37028574322a259e1e954a1bd1e364d444faa3f1b4c9618fc66d`;
 frozen audit SHA256
 `12d74401f0d169a52512413c50caa5e678a30ce9534437c025081edc45ad49d8`.
 It verifies618 source pins, actual wrapper/entrypoints, all16 exact versioned
 launch commands/controls/geometry/noise/delay and all budgets. No source or
 scientific gate changes. Preparation cannot be repeated. Next: material
 preparation checkpoint/archive and exact dispatch release; source stays held.

- M4v4 source archive saved: `checkpoints/m4_v4_source_closed_v1/manifest.json`,
 SHA256 `cbd486518b660b5b166b19a327846d9132d2f23db7342c6e13efc448f6ffd1da`;
 354 dirty/untracked files,59 artifact references,1392888-byte verified tar.
 Context/diff/checkpoint PASS;618 source pins remain held. This live receipt
 postdates the archive. Single600s preparation is next; read external
 `builds/m4_v4_confirmation_mirror_v1/preparation_v1*` and freshpilot preflight
 before recovery. No acquisition released; no preparation retry permitted.

- M4v4 source CLOSED_SOURCE_VALIDATION_PASS:1042 unique tests PASS172.63s,
 618 identical before/after source pins,21 actual Q5 console bindings and two
 actual CLI checks. Canonical publication is consistent through actualcallback
 and realDDS tests; strict validation and stationary behavior remain unchanged.
 See `m4_v4_source_handoff.md` and `validation/m4_v4_confirmation_mirror.md`.
 Final source receipt SHA256
 `6e66944e5cacfbf1558372f6c11bcf8483205ba717e7ff64cbfc7b4d0d60576a`.
 All old evidence retained. Next: material source archive, one600s preparation,
 independent frozen audit and exact release. No v4 acquisition started;
 both original research goals remain open. Source/tests are held.

- M4v4 publication-consistency amendment ACTIVE:
 `m4_v4_confirmation_mirror_plan.md`, adopted before source edits. Preserve
 strict canonical mirror validation and all scientific/control settings; fix
 selected moving/PDE status ordering with actual callback/serialized lifecycle
 tests, then fresh16-slot v4 source/preparation/audit/release. No acquisition
 released. M4v3 closure archive SHA256
 `1553acb3257e96c612193c94d8460b37fbbd239384638020e59b0557cc7c9895`
 binds349 files/141 artifact references/1378951-byte verified tar. Context,
 diff and checkpoint PASS; all old failures remain immutable. This live
 receipt postdates the archive. Full original comparison/report remains active.

- M4v3 CLOSED_INCOMPLETE: single dispatcher terminal exit1 in1394.491043s.
 Two complete slots(A behaviorPASS/BFAIL), one incompleteC and13unstarted.
 C finalzero/metadata/target/bag and kernel/performed cleanup PASS, but four
 legacy confirmation snapshots lack an exact canonical observation mirror;
 completeness59/60. Independent-inner cleanup was not reached. No block
 science/holdout release/replacements. All16-slot/192-target report retained;
 both research goals remain unavailable. See `m4_pilot_v3_handoff.md` and
 `validation/m4_pilot_v3_result.md`. Closure audit SHA256
 `04c263b617a6681621279bbbf6130e5926c4f732201d6077d00f7ca04c2a1a86`
 binds615 unchanged source pins and73pilotfiles/942803553bytes. Source held
 until material archive and separate publication-consistency amendment.
 All earlier acquisition entries below are history; never restart M4v3.

- M4v3 slot2 B COMPLETE/integrity PASS, behavior FAIL in491.340042s.
 Selected two-block/stationary settings match frozen launch and captured values.
 There were10702 typed diagnostics and no confirmations, stationary requests
 or fills; SEARCH continued to the fixed StageA timeout360.026sim seconds.
 Completeness52/52, final zero, both eight-flag kernel proofs and all three
 performed cleanup checks PASS; recorder/target/bag exit0. Behavioral predicates
 pass4/14. This is a retained complete behavioral failure, not a recording
 abort or a qualified primary latency result. Slot receipt SHA256
 `b0ce431669ccebdd3e7d5be007f2b2e05609a1c3a093dda35b74f98dbfb9dbb3`.
 Independent read-only finalized-input audit PASS1.110308s, all8 input hashes:
 external `builds/m4_v3_recorder_shutdown_v1/second_slot_audit_v1.json`, SHA256
 `6b9df013f63cb3bdaad1472455897073805b9bd51fa83d28985a823402cc2e07`.
 ArmC slot3 is running under the same dispatcher. Source/settings remain held;
 no active bag reads, replacements, retuning or additional science occurred.

- M4v3 slot1 A COMPLETE/integrity and behavior PASS in413.875127s.
 Actual recorder finalizes target/bag exit0 and final zero; completeness48/48,
 behavioral predicates14/14. Inner/outer kernels and performed inner/outer/
 independent-inner cleanup all PASS. Exactly one guarded groupSIGINT and no
 TERM/KILL escalation. Slot receipt SHA256
 `c9b10118da40ae9428125b72a315b576a2fafb63f8274225e5270c3909372b6e`.
 Read-only first-slot audit SHA256 `0832d70451d6aa6f6581a4901483e6fe730b46f047c3d5c046f10fddef98ba6b`,
 external `builds/m4_v3_recorder_shutdown_v1/first_slot_audit_v1.json`, binds
 completed input hashes and615 unchanged source pins. No science rerun or
 active-slot bag inspection. ArmB slot2 is recording; same dispatcher remains
 active. No M4 block science/research acceptance yet; source stays held.

- M4v3 DISPATCH RELEASED; its single acquisition is starting. Release
 `pilot/m4_pilot_v3/preflight/dispatch_release.json`, SHA256
 `e6c9fbd007783814c4ba25af078116a36f7d9fb93769de4aab3adf71b43785c0`,
 binds exact contract, source validation, actual CLI, frozen audit, archives
 and initial slots1-4. Preparation archive SHA256
 `76b770e35e244e07c0c1939228d95ca314a700d9a51bad4c06bd4b8a1bdec0e1`;
 347 files,76 artifacts,1374180-byte verified tar. Canonical dispatcher command
 uses SIGINT15180s/kill-after120s,15300s maximum. Source stays held.
 Console: `builds/m4_v3_recorder_shutdown_v1/acquisition_dispatch_console_v1.log`.
 Read fresh acquisition started/slot/final receipts before recovery. Never
 restart this dispatcher or replace a slot; holdout release remains separate.

- M4 v3 preparation and frozen audit PASS, 2026-09-10 UTC.
 The single preparation finished in43.008776s within its600s maximum.
 Contract `pilot/m4_pilot_v3/preflight/contract.json` SHA256:
 `f035a5c7de675d505f10952d06e55ad77166ee235512f8e10f5069cbf92918fb`.
 Prepared receipt SHA256:
 `27afb2847c0ab5a7a96bd6fe4e32b892feb75326851675f8003d13a76d74aa46`.
 Independent frozen audit PASS2.953708s, no field reevaluation or bag decoding.
 It verifies615 source pins, the installed wrapper against the retained baseline,
 all16 exact slots/commands, selectors, controls, geometry/topology/configuration,
 noise/delay receipts and every execution/science cap. Audit receipt SHA256:
 `5f6c86e1c26e271e4bde843cd1d09011f0e1de694fe21fa1306d48bb7cf87295`.
 Source is held; no acquisition or holdout release has started.
 Next: material preparation archive and exact dispatcher release.


- M4v3 material source archive saved: external
 `checkpoints/m4_v3_source_closed_v1/manifest.json`, SHA256
 `d4915b01763251bd40d01bab9006568f68d8847f3e76646fcc8192698dfe4d79`;
 347 dirty/untracked files,62 artifact references,1372937-byte verified tar.
 Context/diff/links/checkpoint PASS;615 source pins held. This live receipt
 postdates the immutable archive. Single600s preparation is next; read external
 `builds/m4_v3_recorder_shutdown_v1/preparation_v1*` and fresh pilot preflight
 before recovery. No acquisition is released yet.

- M4v3 source CLOSED_SOURCE_VALIDATION_PASS:872 unique tests PASS146.48s,
 615 identical before/after pins including actual installed ros2run wrapper,
 21 console bindings and two actual CLI checks. Final receipt SHA256
 `c27a49b0489d7c6005c1ec8337e380ba046730bacc7dcfbb778bdb58794331d3` under external
 `builds/m4_v3_recorder_shutdown_v1/root_final_v1_receipt.json`.
 Actual-wrapper shutdown passes with unchanged timing; old failures and all
 selectable legacy modes retained. See `m4_v3_source_handoff.md` and validation.
 Next: material source checkpoint/archive, one600s preparation and exact audit/
 release. No v3 acquisition yet; both research goals remain unestablished.

- M4v3 recorder-shutdown correction ACTIVE under
 `m4_v3_recorder_shutdown_plan.md`, adopted before new source edits. Select
 guarded unreaped-root-group initial SIGINT in existing owner, preserve old
 observed-tree/direct-child modes, pidfd escalation and every original gate.
 Actual installed-wrapper finite fixture must reproduce v2 failure and prove
 ordered recorder finalization before source release. Fresh16-slot v3 follows
 only after source/preparation/audit/release; no acquisition started.

- M4v2 material closure archived: external
 `checkpoints/m4_v2_closed_incomplete_v1/manifest.json`, SHA256
 `846f535e46e86389fd632cbb1dcf094d9d640f9dc2596ded374b65bd2765f492`;
 341 dirty/untracked files,102 retained artifact references,1351984-byte
 verified source archive. All610 source pins held through closure;46 pilot
 files/403938081bytes including raw bag independently hashed. Context/diff/
 checkpoint PASS; read-only procfs confirms no active case owner. This receipt
 postdates the immutable archive. Next bounded correction needs its own plan.

- M4v2 CLOSED_INCOMPLETE: dispatcher terminal exit1 after536.403020s.
 One A incomplete,15 unstarted; no science/holdout release or replacement.
 Both kernel ownership proofs and performed inner/outer cleanup PASS, but
 graceful SIGINT reached only the ros2-run wrapper. Later recorder TERM/KILL
 prevented bag/metadata finalization; completeness and final-zero are unproved.
 All16-slot/192-target report saved with unavailable research targets. See
 `m4_pilot_v2_handoff.md` and `validation/m4_pilot_v2_result.md`.
 Closure audit SHA256 `28c0bfd8e276aeed54700915bacf9ca073e89ee4e82ed1c32f3e91f38d80af34`
 binds610 unchanged source pins and46pilotfiles/403938081bytes. Source held
 until material closure and separately recorded graceful-delivery amendment.
 No restart of this fixed version. Full comparison/report goal stays active.

- M4v2 DISPATCH RELEASED, single acquisition starting. Release
 `pilot/m4_pilot_v2/preflight/dispatch_release.json`, SHA256
 `4df11bdebb54831a2cab48f25293fba63dba21861ebcc79c3d4ed177f04a22e5`,
 binds contract/source validation/actual CLI/audit/archives and exact initial
 slots1-4. Preparation checkpoint SHA256
 `ca2d7dab98beadaa0704455f5e3fdd73a62f8247b5cc9c65db0a8808975dc865`.
 Exact outer command SIGINT15180s/kill-after120s caps15300s total; source is held.
 Console: `builds/m4_v2_recovery_v1/acquisition_dispatch_console_v1.log`.
 Read fresh `acquisition/started.json`, slot receipts and `acquisition.json`
 before recovery. Never restart or replace a slot; holdout release is separate.

- M4v2 preparation and independent frozen audit PASS,2026-09-10 UTC.
 Single preparation completed43.516013s inside the600s cap; no acquisition.
 Contract `pilot/m4_pilot_v2/preflight/contract.json`, SHA256
 `f2bff98bab52b29e0d8cb6ae56a20dec62baa51c9b980b6cdb8e275c8617a352`;
 prepared receipt SHA256
 `48c1d447278ae766237dead8772125b4f8abe3aaf283ea80c1da0bd0fda4883f`.
 External `builds/m4_v2_recovery_v1/preparation_v1_receipt.json` retains exact
 command/log/time. The independent audit ran once under30s (2.898473s), without
 bag decoding or field reevaluation, and matched all610 validated source pins,
 all16 exact versioned slots/launch commands, Q7/Q2 selections, original geometry,
 secondary topology/noise/delay/configuration receipts and all execution/science
 budgets. `preflight/frozen_audit_v1.json`, SHA256
 `82ec70831e6e5b845c0adfc5d39dcefb3f2fffb0e2e57b7fb367a6ad3836b603`.
 Environment is clean Q2 then Q5 overlays, domain182/local-only, DISPLAY0.
 Exact audit command is `timeout 30s /usr/bin/python3` on external
 `builds/m4_v2_recovery_v1/frozen_audit_v1.py`, in the validation environment above.
 No preparation retry, science result, holdout release or acquisition is implied.
 Next: material preparation archive and exact dispatcher release, then the
 single approved four-development/twelve-holdout comparison.


- M4 v2 material source archive saved: external
 `checkpoints/m4_v2_source_closed_v1/manifest.json`, SHA256
 `4f3d88fed0af4e473bde7bcc94432e489a37bc72f06fe5bf16f5de50ef32da0a`;
 339 dirty/untracked files,51 artifact references,1346407-byte verified tar.
 Context/diff/links/checkpoint PASS;610 source pins remain held. This live
 receipt postdates the immutable archive. Single600s preparation is next;
 inspect external `builds/m4_v2_recovery_v1/preparation_v1*` and fresh pilot
 preflight before recovery. No fresh acquisition is released yet.

- M4 v2 source CLOSED_SOURCE_VALIDATION_PASS:794 unique tests PASS118.94s,
 610 identical before/after source pins,21 installed console bindings and two
 actual CLI help checks. External `builds/m4_v2_recovery_v1/root_final_v1_receipt.json`
 SHA256 `ea4b3673ab5a4321558898e2f62cd08a2aea1678ee0f87090c4e8e0941a47c25`. Legacy defaults and old evidence retained;
 see `m4_v2_source_handoff.md` and `validation/m4_v2_recovery.md`.
 Next: material source checkpoint, single600s preparation and exact audit/release.
 No fresh acquisition started; both research improvements remain unestablished.

- M4 v2 RECOVERY ACTIVE under `m4_v2_recovery_plan.md`. User resumed the full
 goal and authorizes recommended fixes without further questions. Reverified
 branch/HEAD and all606 prior frozen source pins before edits; v1 is terminal,
 archived and unchanged. Adopt optional child-subreaper proof in the existing
 inner/outer owners, preserve old tracking behavior, and parameterize a fresh
 exclusive16-slot version. Source/process tests and exact preparation/release
 must pass before Gazebo. No algorithm retuning is justified by the baseline
 ownership failure; original science/controls/gates and finite budgets stay held.

- M4 v1 material closure archived: external
 `checkpoints/m4_pilot_closed_incomplete_v1/manifest.json`, SHA256
 `31e01fcf9bfe5c341391a93f896ffc0ff4f33bc8371f3deecef25c5430409e4d`;
 333 dirty/untracked files,163 retained artifact hashes,1320061-byte verified
 source/evidence archive. The closure audit additionally binds all50 pilot
 files including the retained bag (264687338 bytes). Context/diff/checkpoint
 and22 local links PASS; all606 frozen source pins remain unchanged.
 This live receipt postdates the immutable archive. Source remains held;
 no further dispatcher, correction, commit, push or physical action occurred.

- M4 v1 CLOSED_INCOMPLETE: single dispatcher exit 1 after424.712260195s.
 One INCOMPLETE baseline A development slot,15 UNSTARTED; no replacements,
 block science or holdout release. Existing inner result passes14/14 required
 predicates, ranked GOAL_HOLD, recording/final zero and strict inner cleanup.
 Outer ownership inspection failed on a disappearing-process exception; its
 empty remaining arrays were uninspected defaults, not final cleanup proof.
 The all16-slot report and192 direction targets remain unavailable honestly.
 See `m4_pilot_v1_handoff.md` and `validation/m4_pilot_v1_result.md`.
 Closure audit `builds/m4_pilot_runtime_v1/pilot_closure_audit_v1.json`, SHA256
 `5e84418252b2a95aa7d2a646bdbc2f0bc2b10b19a18ee0c92b3f0df2d0f53c6e`,
 verifies606 unchanged source pins and50 retained pilot files including bag.
 Next: separately planned tracker correction and finite validation; do not
 restart v1, replace slots or silently expand the approved comparison budget.
 Full V2 IN_PROGRESS; neither original research improvement is established.
 All entries below this one describe earlier boundaries unless dated later.

- M4 DISPATCH RELEASED / acquisition starting. Independent frozen audit
 `preflight/frozen_audit_v2.json` SHA256
 `e0b50039a64c18aceff793368c18363444ecefaaabda320b15c1e3b41829f89c`
 PASS: exact16 slots and original-YAML-ordered launch commands,606 source pins,
 original geometry, all topology/noise/configuration and budget bindings.
 Its first audit's JSON mapping-order reconstruction error is retained in
 `frozen_audit.json`; source, frozen commands and numerics were unchanged.
 Material preparation archive `checkpoints/m4_preparation_complete_v1/manifest.json`
 SHA256 `42ff3aeb08e96a8675eae8e045fff6f195c528b46e1e10ce53bc72073050d44d`.
 Exact `preflight/dispatch_release.json` SHA256
 `ce44b8158674a5d336abdea136600cead88e18d7fa5749054279ad2146b75f8e`
 binds prepared contract, source validation/archives, audits and initial slots1–4.
 External console log: `builds/m4_pilot_runtime_v1/acquisition_dispatch_console_v1.log`.
 The first shell redirection collided with the existing source-test
 `dispatch_v1.log`; noclobber preserved it before any dispatcher or acquisition
 launched. `preflight/console_destination.json` records this naming correction.
 The released executable argv and experiment population are unchanged.
 Outer command SIGINT15180s/kill-after120s caps total15300s; per-caseM4A bounds
 and strict cleanup stay active. Read `pilot/m4_pilot_v1/acquisition/started.json`,
 `slot_N.json`, `acquisition.json` and analysis/report receipts before recovery.
 Never start a second dispatcher or replace any slot. Holdouts require the
 separate one-time release after complete safe development and attempted science.

- M4 preparation PASS: single attempt completed45.713929s inside600s cap;
 no acquisition. `pilot/m4_pilot_v1/preflight/contract.json` SHA256
 `b6366e66a8d2bfc8c05e428a2214dbfe5b0e5578164f5b1328d8dc36a50a9e77`
 binds16 exact slots,606 source receipts, original primary/secondary geometry,
 fresh secondary nominal/noise/delay topology and explicit selected environment.
 `preflight/prepared.json` SHA256
 `224d5335e932fda4a83daad5915875f4ad2638bbd5b7f3eee54c543f12d1420f`.
 The noisy static topology receipt has0.045 raw-cost three-sigma margin;
 delay hashing is not dynamic qualification. Preparation log/receipt are
 external `builds/m4_pilot_runtime_v1/preparation_v1*`. Do not repeat this job.
 Independent frozen audit and exact initial development release are next.

- M4 material source archive saved: `checkpoints/m4_source_closed_v1/manifest.json`,
 SHA256 `5e16a861e2e484527bbe34457b7736427d05352f7b872c4d25174d430580ba33`;
 330 files,105 retained artifacts,1310249-byte verified archive. Context,
 diff and existing V2 checkpoint checks PASS. This live receipt postdates the
 immutable archive; executable source remains held.
 The single bounded preparation is next/dispatched through external
 `builds/m4_pilot_runtime_v1/run_preparation_v1.py`:600s inclusive wrapper,
 fresh ROS domain181/local-only, existing Q2/Q5 overlays, exclusive
 `pilot/m4_pilot_v1` root. Read `preparation_v1.log`,
 `preparation_v1_receipt.json` and that root's `preflight/` before any recovery.
 No retry, overwrite or acquisition is implied by a partial preparation.

- M4 execution/evaluation source is CLOSED_SOURCE_VALIDATION_PASS. Final
 `builds/m4_pilot_runtime_v1/root_final_composed_v2_receipt.json`, SHA256
 `8bc1014a01241c1364d966f19a462c5bbf9576c99b55577faa2d17429f360207`,
 binds767 unique passing tests across their declared installation contexts,
 two actual Q5 CLI help checks,21 installed targets and606 unchanged source
 hashes. The initial combined invocation's745 PASS/3 FAIL/19 ERROR is retained;
 all22 rejected historical installation cases pass with the expected initial/
 Q2 ros_esc package selections, without source/test edits or rebuilds.
 See `validation/m4_source_validation.md` and `m4_source_handoff.md`.
 Next: material source checkpoint, one600s preparation attempt, exact frozen
 release, then the approved four visible development slots. No M4 case has run.

- M4 IMPLEMENTATION ACTIVE under adopted `m4_execution_evaluation_plan.md`:
 exact16 population and original two goals preserved; finite independent
 labels/direction/objective/cleanup/freeze definitions saved before source work.
 No case dispatch until source tests and immutable preparation receipts pass.
 Active source note `m4_implementation_clarifications.md` covers the measured
 large-input eligibility bottleneck and typed centroid/legacy Stage A evaluator
 timestamp compatibility; neither changes scientific labels or public messages.

- Q7 final archive: `checkpoints/q7_two_block_closed_v1/manifest.json`, SHA256
 `16dbe96dec7a1f177965e8f047d429d39a44fcb46531e93e02998854c96bc158`;
 313files/45 retained artifact hashes, archive bytes verified. Source/test pins
 match final400-case receipt; context/diff/repository checkpoint PASS. This live
 receipt and M4 adopted plan postdate the immutable Q7 archive.

- Q7 CLOSED_SOURCE_VALIDATION_PASS: user-selected two-block detector implemented
 under `q7_two_block_method_plan.md`. Final400 integrated checks PASS83.91s,
 stable source/test hashes; exact commands/logs/failures/limits in
 `validation/q7_two_block_method.md`. Actual detector/stationary/moving DDS,
 mode-aware recording and installed launch selection PASS; five-shift/PDE and
 old studies preserved. `q7_two_block_method_handoff.md` is the source boundary.
 No M4 case or research acceptance result yet. Next: finish/adopt/implement
 saved M4 evaluator, labels, finite dispatch and one-time holdout prerequisites.
 Read-only prospective audit: `validation/m4_prerequisite_audit.md`.

- Q7 pre-source archive: `checkpoints/q7_pre_source_v1/manifest.json`, SHA256
 `b8c839e62b6de2fd4a18f4face0368b8dc48669e9478b1858b08a260b70aee6d`;
 305 files. Original Q5/Q6/M4A manifest hashes verified against handoff.

- Q7 ACTIVE: user explicitly chose Q6 two-block means on 2026-09-09.
 `q7_two_block_method_plan.md` records the adopted exact method, compatibility,
 finite source validation and unchanged M4 prerequisites before source edits.
 New selector `centroid_two_block_v2`; selected W6s/epsilon0.18m/radius0.50m.
 PDE default and existing five-shift mode remain selectable. Context validator
 PASS; branch/HEAD match this status, saved dirty V2 work present, no ROS/Gazebo
 process left by the interrupted turn. No pilot or new research result yet.

- FRESH-CHAT TRANSFER: see fresh_chat_handoff.md. M4A source is CLOSED PASS:
 47 focused checks (30 new,17 inherited),178 deselected,2.67s; strict procfs
 correction, same-end cancellation, installed binding and scoped AST review
 PASS. m4a_execution_deadline_handoff.md and its validation retain exact source,
 command and intermediate evidence. No M4 case or two-block implementation ran.
 Q6 comparison is complete; explicit method choice remains pending. The restart
 prompt chooses two-block only when the user sends it. All Q5 algorithm sources
 and old studies stay held; full M4 remains prospective. Agents finished their
 assigned work and hold source/tests; no new milestone is launched in this chat.

- Q6 DECISION checkpoint: external
 `checkpoints/q6_method_decision_pending_v1/manifest.json`, SHA256
 `39d3752ff7d1e162d6893af5929c1c71a5aff6af0a02ccbde031d32e2c665e1e`.
 10verified decision/preparation files; references the unchanged Q5 source
 archive. Analytic comparison is complete; one methodological choice remains
 pending. This receipt postdates the immutable decision checkpoint.

- M4A / FRESH-CHAT SOURCE archive: external
 `checkpoints/m4a_closed_fresh_chat_v1/manifest.json`, SHA256
 `02d57e5074011a2f185162b4c5eb14596c4ccdfd2cdcea7160bba5bb3caa4094`.
 304 changed/untracked files,1208121-byte verified archive,31 retained artifact
 hashes including Q5/Q6 parent manifests. Context/diff/repository checkpoint
 PASS; all10 local handoff links resolve, final source/test hashes match the
 tested bytes, all three agents completed, and no matching Gazebo/test/runner
 process remains. Exact read-only receipt: builds/m4a_execution_deadline_v1/
 root_transfer_checks_v1.json. This live receipt postdates the immutable archive;
 source and tests remain held. No commit/push, method selection or M4 release.

- Q5 SOURCE CLOSEOUT archive: external
 `checkpoints/q5_stationary_centroid_adapter_closed_v1/manifest.json`, SHA256
 `308f86a68339b1430bf0e76b88e4617570c06be89f735a55004c351b94dc4a57`.
 296files/1182225-byte verified archive/348retained hashes. Context, diff and
 repository checkpoint PASS. This receipt and the following prospective Q6
 decision plan postdate the immutable source archive; Q5 source remains held.

- COMPLETED: Arm B centroid/stationary adapter under
 `q5_stationary_centroid_adapter_plan.md`. Typed original confirmation through
 stopped verification/request/shared Gaussian fit/result acknowledgment;
 210focused and208recording/inherited checks, actualB DDS1, moving DDS3 and
 controller finalzero1PASS. Eight frontend combinations, old-interface legacy
 fit, isolated interface/resource builds and final installed binding PASS.
 Handoff `q5_stationary_centroid_adapter_handoff.md`; exact failure/baseline/
 source pins in validation/q5_stationary_centroid_adapter.md. Overall research
 targets and M4 remain open. Material source archive receipt follows creation.

- Q4 SOURCE CLOSEOUT archive: external
 `checkpoints/q4_committed_fill_clock_admission_closed_v1/manifest.json`, SHA256
 `6f13e59f52b0752a42651b6270c0c0a7e548888abc745ff8d9390534d35b8a33`.
 281files/1140268-byte verified archive/296retained hashes; context, diff and
 repository checkpoint PASS. This receipt and the subsequently adopted Q5 plan
 postdate the immutable source archive; no Q5 source changed before that archive.

- COMPLETED: committed-fill clock admission under
 `q4_committed_fill_clock_admission_plan.md`. Preserve durable next-generation
 results until source-clock coverage and apply before objective composition;
 no sensor-style expiry. Two actual-owner baseline failures are preserved (0.45s); the bounded
 source correction passes157 focused,1 new actualDDS and3 existing pipelineDDS
 checks, with installed source binding verified. Handoff:
 `q4_committed_fill_clock_admission_handoff.md`. Arm B and scientific development
 remain pending.

- Q3 SOURCE CLOSEOUT archive: external
 `checkpoints/q3_detector_clock_admission_closed_v1/manifest.json`, SHA256
 `d529084d92aa8038679d66fe3deda8ee0d1e7a642248d16cd9978a53af9c8616`.
 277files/1127645-byte verified archive/280retained hashes; context, diff and
 repository checkpoint PASS. It includes Q3 source/tests/docs and prospective
 Q4 plan before source edits. This receipt postdates the immutable archive.

- COMPLETED: bounded detector state/standalone-pose clock admission under
 `q3_detector_clock_admission_plan.md`. Three held actual-node baseline tests
 failed in0.40s as expected, demonstrating premature state/pose invalidation and
 inactive-gate drain failure. Corrected node226 focused checks and5 existing DDS
 checks PASS; installed import binding PASS. Selected recorder24 new +81
 existing regressions and2 explicit configured-freshness checks PASS.
 Handoff: `q3_detector_clock_admission_handoff.md`; all baseline/failure receipts
 retained. Source milestone closed; scientific qualification remains open.
 Correct near-future callback ordering with original receipt/0.5s limits;
 preserve formula/parameters and all closed scientific results. Arm B design
 remains pending in `validation/arm_b_adapter_design_note.md`.
 Pre-correction checkpoint SHA256
 `add832e4fd397e1bf8b643a0b12784190fc243b47b260ee0e77bebcb73953745`:
 272files/1111223-byte verified archive/264retained hashes. Context/diff/checkpoint
 PASS; paired diagnostics and all source are recoverable before new edits.

- COMPLETED: bounded recorded detector extraction under
 `q2_recorded_detector_diagnostic_plan.md`, PASS3.175s. All20 valid first complete
 snapshots fail the0.30m score; residence5/5 score-only, approach12/15 score-only
 plus3 both. Residence also has five state-related reset notifications reducing
 live detector history; their exact stale/future cause is not established.
 `validation/q2_recorded_detector_diagnostic.md` records hashes/limits.
 The preceding saved-data motion
 diagnostic completed in9.14s: both runs loop near the local source with124.882s
 uninterrupted qualified history, no pose faults/gaps and no post-readiness
 policy resets. Saved24-anchor phase/time checks found no demonstrated defect;
 within-cycle motion remains a stationary-reference limitation. Exact recorded
 score/radius extraction identified the numerical gate without rerunning it.
 The Q2v2 scientific boundary is closed.
 Acquisition is COMPLETE4/4; detector qualification EVIDENCE_UNAVAILABLE,
 discovery direction COMPLETE_DIAGNOSTIC, confirmation SEALED, M4 unreleased.
 Both discovery runs have zero positive/censored residence episodes; all nine
 settings are unavailable with no nominee and no detector events/M3 evaluations.
 Actual direction is usable at24/24 fixed targets, pooled median31.664092deg,
 p90113.393071deg (aligned instantaneous median58.560725deg). These are diagnostic
 results, not held-case qualification. Do not retune or rerun this fixed study.

- Dated-path correction source checks PASS: actual recorder/contract122,
 acquisition family102 across both required environments, study routing92 and
 legacy input/reference/policy210. Independent source review confirms unchanged
 numerical loop, acceptance tail and runtime owners. New scenario resource
 build/binding PASS; checkpoint saved and31-series Q2v2 contract frozen/released.
 The single bounded acquisition completed4/4 accepted inputs, exit0 in641.103s
 including wrapper overhead. All acquisition gates passed; source remains held.
 Material acquisition checkpoint saved; single600s label and300s reference jobs
 both completed with exit0. The predeclared24-discovery branch preserved all24
 confirmation slots sealed. Independent14-receipt label audit passes; reference
 arithmetic audit PASS347 checks; immutable scientific closeout saved.
 Source evidence: `validation/q2_acquisition_path_correction.md`.
 Current acquisition/scientific evidence: `validation/q2_qualification_v2_result.md`.
 Closure SHA25651d73de197aa24f2aba8cb9f1eac576aaaa38e7519d6abc672f5113a9acfa137;
 material checkpoint SHA256014149d7d4a3f91a7f4797f43429ea13cadd3cf893645b88367c3ea21ee66d28,
 265files/1098058-byte verified archive/241retained hashes. Context/diff/checkpoint
 PASS. Handoff `q2_qualification_v2_handoff.md`; scientific source remains held.

- Q2 v1 remains CLOSED_INCOMPLETE: exactly1dispatch and0acceptedinputs. Its first
 case passed125sim/recording/spawn/final-zero/cleanup, then incorrect direct-path
 admission rejected the recorder's dated layout. No case2 or science was run.
 The separate Q2v2 correction above resolves source admission without rewriting
 the failed attempt, importing that run, or changing any scientific gate.

- Q2 qualification workflow: held integration344PASS/3deselected60.36s with18
 unchanged pins; independent contract69PASS20.27s. The3 old-environment cases
 passed separately. New scenario packaging corrected in the existing explicit
 installation list; installed21-entry/interface/resource binding PASS, final
 wrapper65PASS3.99s and independent review PASS. Material checkpoint saved;
 fresh contract frozen at a1b3b0b1d76e373e7a340a8749c898724d1f731a51eb90cd536e48f96b1fb7a3.
 Final contract/environment audit PASS, but the acquisition exposed a missing
 recorder-layout integration check. Failure and source correction are recorded
 above. Confirmation scientific outputs remained sealed.

- Q2 SOURCE VALIDATION PASS: fixed75% moving-cycle policy and compatible
 evidence routing implemented, selected legacy preserved. Final40-file integration
 **1167PASS162.63s**,426 source pins unchanged, no failures/errors/skips and one
 inherited sqrt warning. Focused core/adapter/recording and actual DDS checks
 pass; dedicated-domain3 and original-overlay23 remain separately validated.
 Source milestone CLOSED; handoff `q2_policy_runtime_handoff.md`.
 Fresh Q2 science is adopted in `q2_qualification_plan.md`; source/workflow
 implementation precedes any acquisition release.

- Snapshot correction validated under `q2_snapshot_structural_clone_plan.md`:
 106 ownership/97 independent checks PASS; fixed structural timing v2 PASS4.582815x,
 selected maximum46.180069ms. Actual DDS21PASS, whole timer<=79.667692ms and exact
 published/retained context joins valid with readiness ages<=82.150036ms.
 Hashes, all copy boundaries, freshness500ms and deadlines preserved.
 CDR timing v1 remains CLOSED FAILED_TIMING_GATE (1.475264x<2x); no rerun.
 Complete history/commands: `validation/q2_snapshot_serialization.md`.

- Q2 implementation receipts: three-package build PASS25.7s; core107PASS,
 adapter/frontend79PASS, independentcontract30PASS, policyDDS2PASS, recording
 173PASS, new environment19PASS. Original1000-update core performance stays
 closed PASSmax0.950311ms, core unchanged. Refreshed installed21entries/6message
 bindings; D3 scope17changed/539unchanged/12additive files. Earlier integrated
 failures, source-starvation fixture diagnosis and runtime callback cancellation
 remain retained; the final integrated check resolves source validation only.
 `validation/q2_policy_runtime.md` is the exact evidence record. No scientific
 qualification, old confirmation access or M4 release follows.

- Direction-policy result audit COMPLETE: 607 hashes unchanged; all 24 saved
  joins/vectors/angles/bounds and exact nomination agree independently. CSV and
  paired error/magnitude plot visually verified. Audit manifest SHA256
  `caab8a832d16c09e1cfa70768159d26fc53324406a5c9bebe4eef10337432708`.
  Next: close material boundary, then explicit runtime implementation amendment
  for the nominated policy. No additional candidate or reference calculation.

- Direction-policy arithmetic CLOSED COMPLETE_DIAGNOSTIC: nominee weight0.75,
  current coherence threshold0.25, averaging24/24, median20.526919deg and
  P9034.946685deg. Single job exit0 in10.18s; 23 improved versus actual and one
  worsened. Closure SHA256
  `88a1767f80135c98dbec416a7768206b1b046e20100828aa37146723a4b231df`.
  Independent saved-result audit/material closeout precedes a runtime
  implementation amendment. No runtime change or independent qualification;
  original confirmation sealed and M4 unreleased. See
  `q1_direction_policy_handoff.md` and `validation/q1_direction_policy_result.md`.

- Direction-policy preflight VALIDATED: 79 synthetic tests pass in 29.91s;
  independent final source review passes. Frozen contract SHA256
  `917d10eb90effac6005593448ae324e2b63bfbb74d62dffef4fbecb0a5315a41`
  binds 556 unchanged owners, six new diagnostic files and the original 24
  targets/references. No new recorded-data weight/coherence values yet.
  Next: material checkpoint/release and one 60s arithmetic job. Exact evidence:
  `validation/q1_direction_policy_preflight.md`. No qualification/M4 release.

- ACTIVE DIAGNOSTIC PREPARATION: `q1_direction_policy_diagnostic_plan.md`
  predeclares weights0.5/0.75/1 and one current-cycle coherence candidate0.25,
  using existing24 references with no model/filter rerun. Existing556 frozen
  source owners remain unchanged. Tests/source/input freeze precede one60s
  arithmetic job; no runtime change or qualification release. Prior observed-
  phase boundary CLOSED at `checkpoints/q1_observed_phase_closed_v1/manifest.json`,
  SHA256 `62127026e35140c9a0dc3a2821f760a1aa1e6a49c84d37f7f12e421dbf987be8`:
  227 files,958647-byte archive,281 retained artifact hashes.

- Independent observed-phase result audit COMPLETE:602 files unchanged,
  all24 exact source/diagnostic joins and saved arithmetic agree. Latent
  improvements24/24 vsinstant,20vsactual+4equal. PairedPNG/PDF and24-rowCSV
  visually reviewed; auditmanifest
  `e111892b1e5e18a534271de806f0168f0af2e4ca4b40ee8c42a2dfb675ae2741`.
  No newreference/weight/policy calculation. Next is a prospectively declared
  finite weight/coherence diagnostic on these existing receipts, after closing
  this material source/evidence boundary. No runtime change or pilot release.

- Observed-phase diagnostic CLOSED COMPLETE_DIAGNOSTIC, qualification
  NOT_EVALUATED:24/24 informative references,24.32s,exit0. Actualmedian55.34deg,
 p90103.69deg,averaging4/24; predeclaredlatent improvesinstant24/24,
 median23.01deg,p9071.99deg. The upper tail remains above60deg; no runtime
 qualification. Closure70 artifacts SHA256
 `52c8942e1f311ee4aae7659ee90b14e01c70136f532f2811229ebf98b197af04`.
 Handoff `q1_observed_phase_handoff.md`; exactevidence
 `validation/q1_observed_phase_result.md`. Next: independent saved-result audit
 and prospective direction-development decision; no extraweight or policy
 evaluation before that amendment. Confirmation sealed,M4 unreleased.

- Observed-phase diagnostic RELEASED and single job dispatched under300s.
  Prefield checkpoint `checkpoints/q1_observed_phase_preflight_v1/manifest.json`,
  SHA256 `23f54d7e2684083d4394243f2cbe7ea1c8187d39b2b2405a2a5fcf28145dc8bd`:
  225 files,954046-byte archive,240 retained artifact hashes. Dispatch release
  SHA256 `57425c8434d15043a6dd169b707c31c6039489b1975909f8b00c0b6bfc8b23e0`
  binds source/input checks, environment and exact300s argv. This live receipt
  postdates the immutable checkpoint. Read the exclusive observed-phase
  diagnostic root for current job status. Qualification NOT_EVALUATED,
  confirmation sealed, no runtime tuning or M4 release.

- Observed-phase source/preflight VALIDATED:325 combined checks PASS59.69s;
 556-source contract SHA256
 `d9ed31f52c9f088199fdf700076424b730e0248a143f9ace2495c8666527b45e`,
 two actual discovery bindings/21 installed entry points and24 original
 waveform/supplement joins pass; four actualblend matches. Exact evidence:
 `validation/q1_observed_phase_preflight.md` and numerical owner note. No
 recorded-data model job yet. Next criterion: material checkpoint/release and
 one300s24-target diagnostic. Qualification NOT_EVALUATED, confirmation sealed,
 no runtime tuning or M4 release.

- ACTIVE SOURCE/PREFLIGHT: `q1_observed_phase_reference_plan.md` selects one
  separately versioned24-target observed-phase reference and predeclared
  algebraic50/50 blend sensitivity. The prior diagnostic source boundary is
  closed at `checkpoints/q1_discovery_direction_closed_v1/manifest.json`, SHA256
  `6eb47b32197fa21c5800a49332a47f42783d240203468e2f94e5a2b3f7b17e4c`:
  219 files,917306-byte archive,213 retained artifact hashes. Next criterion:
  independent analytic/default-route/source-lineage checks and freeze before
  any new model evaluation. No runtime tuning or pilot release.

- Recorded rate/confidence interpretation COMPLETE: all24 source cycles are
  intact; stableencoder~2.094rad/s and variable base yaw explain world-rateCV.
  Exact first-message confidence extraction finds both magnitude and direction
  change:15/18 weak cases also have descriptive pair-angle>30deg. Evidence is
  appended to `validation/q1_discovery_direction_result.md`; no runtime/gate
  tuning is justified yet. Next selected diagnostic will use a separately
  derived periodic observed-phase reference and predeclared algebraic50/50
  sensitivity on the same24 targets, subject to new source checks/freeze.

- Discovery direction diagnostic CLOSED COMPLETE_DIAGNOSTIC, qualification
  NOT_EVALUATED:24/24 causal anchors,20 constant-rate reference exclusions,
  four informative references all in residence; median55.27deg,p9076.57deg,
  averaging1/4. Approach0eligible. Across all24 targets:4blended,18weak-cycle
  fallback,2cycle-disagreement fallback. No target replacement or source change.
  Closure57 artifacts SHA256
  `91188431df0160ca89da42c91d2785f7ff05cead0184cdeda265cbb787f913cc`;
  handoff `q1_discovery_direction_handoff.md`, exact evidence
  `validation/q1_discovery_direction_result.md`. Active follow-through is
  recorded phase-rate/fallback interpretation and a prospective next decision.
  Confirmation stays sealed; Q1 unavailable and M4 unreleased.

- Discovery direction diagnostic RELEASED after material checkpoint
  `checkpoints/q1_discovery_direction_preflight_v1/manifest.json`, SHA256
  `5369b36742e2bf9b3b7ce91dcb8d81065fdbe7abae59fc7f385b5f5acd35fe84`:
  217 files,913218-byte verified archive,173 retained artifact hashes. Dispatch
  receipt SHA256 `b341f2c1789f66aacdfe1b4beaa7e03e0cd427d2cccd9d2253de91ba2bd3df42`
  binds exact300s command, sourced installed environment and validation receipts.
  This live receipt postdates the immutable checkpoint. Read the exclusive
  diagnostic root for current job status. One24-target discovery job only;
  confirmation sealed, qualification NOT_EVALUATED, no M4 release.

- Discovery direction diagnostic source/preflight IMPLEMENTED/VALIDATED:
  223 combined checks PASS40.74s, including40 new guarded-route checks and78
  original numerical/reference regressions. Exact scope/evidence:
  `validation/q1_discovery_direction_preflight.md`. Frozen552-source contract
  SHA256 `2957ddfedf24b6c41df87f781df9e02958a5514291edac76b5d4b2179923fcd7`;
  all2869 geometry receipts unchanged and both original discovery bindings PASS.
  One analyzer-only transition, exact24 targets, no numerical/runtime changes.
  Next criterion is checkpoint/release then one300s diagnostic; no field job
  yet, confirmation sealed, Q1 unavailable and M4 unreleased.

- Q1 source/evidence boundary CLOSED at `checkpoints/q1_closed_v1/manifest.json`,
  SHA256 `78659061686d43c75217ba1ade254ead9b0474cccbab681cc5c59e8741f6dd7b`:
  212 files,899224-byte verified archive,160 artifact hashes. This live receipt
  postdates the archive. Next ACTIVE SOURCE/PREFLIGHT:
  `q1_discovery_direction_plan.md`, a separate24-target discovery-only direction
  diagnostic with explicit old/new analytical source lineage. No field job yet;
  confirmation sealed; no numerical/runtime changes or M4 release.

- Discovery diagnosis COMPLETE within its read-only scope:
  `validation/q1_discovery_diagnosis.md`. Source input is continuous; the bounded
  orbit repeatedly enters the saved annular hole. At W6/R0.75, all15 full
  residence histories pass confinement but score0.777775–1.158211m exceeds0.30m.
  Enlarging epsilon alone would admit the declared0.02m/s straight-drift
  negative (score0.60m). Preserve Q1; next proposed development step is the
  unchanged direction reference on only24 already frozen discovery targets.

- Q1 CLOSED EVIDENCE_UNAVAILABLE: four125s shadow inputs complete, all recording,
  safety, cleanup and source checks PASS; recovery4 imported2 and dispatched2
  in321.269s. One fixed label job completed; nine settings,zero nominees,
  zero flags. First19.924s positive residence is shorter than required42s;
  later29.716s remains censored. ConfirmationSEALED; reference job withheld;
  M4 unreleased. Handoff: `q1_handoff.md`; exact evidence:
  `validation/q1_study_v1.md`. Closure binds79 artifacts, SHA256
  `090a5b11c803cb0bd0b69b740f02630dacc19f9b84af3172687ba6cf978f61b7`.
  Active next criterion: discovery-only trajectory/unchanged-score diagnosis
  under `q1_discovery_diagnosis_plan.md`, then a prospective decision. Original
  Q1 outputs and sealed confirmation may not be retuned or reclassified.

- Filter expiry source boundary CLOSED at
  `checkpoints/q1_preacquisition_recovery4/manifest.json`, SHA256
  `ea79ea4e4dafccd8e39dc0655b5b25c9d7a875dc7b2536baba2bbb31f8753495`:
  208 changed/untracked files,892621-byte verified archive,125 retained hashes.
  Recovery4 continuation RELEASED: exact two accepted imports pass actual
  unchanged input validation, all41 prior artifacts remain unchanged, and only
  two new confirmation cases may dispatch. Contract SHA256
  `8cd4db25ef3c70528df3b52066af18429cf554fe4aabb0eb370bf08c55619c64`;
  adjacent dispatch receipt binds checkpoint, environment and540s interrupt/
  60s kill argv. This live receipt postdates the immutable checkpoint. Read
  recovery4 acquisition artifacts for runtime status; no science/M4 release.

- Filter expiry source correction IMPLEMENTED/VALIDATED:233 final combined
  checks PASS5.38s, including actual DDS/adversarial and full queue-union tests.
  Normal admission proxy remains288; controlled lost-startup-component proxy
  recovers287 after one expiry instead of the preserved14-then-stall result.
  Numerical `_evaluate_filter` body is unchanged. Handoff:
  `q1_filter_expiry_handoff.md`. Recovery4 routing checks PASS49 in2.64s.
  Next criterion is exact source equivalence/freeze/checkpoint, then only two
  new confirmation acquisitions; two accepted discovery inputs stay unchanged.

- Active source amendment: `q1_filter_expiry_recovery_plan.md`. Admission-only
  prefix-loss diagnostic reproduces a reset feedback loop:14 observations then
  no recovery through10s, while the complete-prefix proxy admits288. Actual
  runtime callback-loss trigger is unproven. Correct expiry cleanup/support
  retention without changing freshness, dynamics, confidence or launch.

- Recovery3 CLOSED INCOMPLETE after two qualified discovery inputs. The third
  case failed before readiness on missing filter heartbeat/controller-manager
  response deadline; fourth case not dispatched. All cleanup passed; no
  confirmation scientific result opened. Closure binds41 retained files at
  `qualification/q1_primary_shadow_v1_recovery3/acquisition_closed.json`, SHA256
  `79de12268086546592cba04beb937fd428dec1ee7542beb37a81255c9f51327e`.
  Active work: bounded read-only startup diagnosis recorded in
  `validation/q1_acquisition_recovery3_failure.md`. Preserve both accepted
  discovery input receipts and every failed artifact; no retry is released.

- CONFIG attribution boundary CLOSED at
  `checkpoints/q1_preacquisition_recovery3/manifest.json`, SHA256
  `f113e05975451a7fc2e98c146a9fb838b08398254fc752bfa906ef9886e5ddef`:
  196 changed/untracked files,858798-byte verified archive and80 artifact hashes.
  Recovery3 is RELEASED for four fixed shadow cases under its new IDs/root;
  exact contract SHA256
  `01ffc684d20a68b9e155b78ec8b4bd1cf3466667d1bac4b6c7476df1b2fdf9d4`.
  Its adjacent dispatch receipt binds this checkpoint, source checks and exact
  1140s interrupt/60s kill command/environment. This live receipt postdates the
  immutable checkpoint. All runtime/science controls equal recovery2; prior
  failed acquisitions remain unchanged and M4 remains unreleased.

- Exact CONFIG attribution correction IMPLEMENTED/VALIDATED:115 focused and
  inherited recorder tests PASS4.31s; separate corrected retained-bag validation
  PASS all60 checks with all15 original artifacts unchanged. Deferred acquisition
  spawn/config/duration diagnostic also PASS. Active preflight:
  `q1_acquisition_recovery3_plan.md`; only validator/workflow/test changes are
  permitted from recovery2. Runtime/scientific controls remain frozen unchanged.

- Q1 recovery2 CLOSED INCOMPLETE:125s SEARCH-only exposure, safety/source/coverage/
  final-zero/cleanup PASS; sole failure is unrecognized V2 detector CONFIG
  signature in the existing event producer validator. Zero qualified inputs;
  other three cases never dispatched. Closure binds15 original artifacts at
  `qualification/q1_primary_shadow_v1_recovery2/acquisition_closed.json`, SHA256
  `7dea4e42af6acb843b3b896f7928e20705c65521d4757d9b13ba34e0053e6335`.
  Active bounded amendment: `q1_event_attribution_plan.md`; diagnosis and
  preserved failure: `validation/q1_acquisition_recovery2_failure.md`.

- Q1 simulation source correction CLOSED at verified checkpoint
  `checkpoints/q1_preacquisition_recovery2/manifest.json`, SHA256
  `d76a851688d361c38d44a189b06bb5608a77ce8ae4db2afa8a1749c56186f345`.
 189 changed/untracked files,846464-byte verified archive,68 retained artifact
  hashes. This source boundary also captures recovery2's frozen prerequisites.
- Recovery2 acquisition RELEASED under `q1_acquisition_recovery2_plan.md`;
  source checks pass, but no scientific acceptance is implied. Read its
  exclusive acquisition artifacts for current runtime status.

- Q1 source correction IMPLEMENTED/VALIDATED:401 combined checks PASS41.90s;
  controller103 focused including actual held-clock ROS transport plus19 legacy,
  graph33 focused plus211 inherited regressions; three-package build PASS2.21s.
  Exact evidence: `validation/q1_simulation_source_correction.md`; handoff
  `q1_simulation_source_handoff.md`. Checkpoint and recovery2 freeze precede the
  next acquisition. No new detector/direction research result is claimed.

- Active source-correction contract: `q1_simulation_source_plan.md`. The first
  FAILSAFE at2.7s rejects a2.721s pose during a held clock tick; later detector
  silence is downstream of FAILSAFE. Separately, two joint-state publishers
  create six merged-stream regressions. Correct controller clock admission and
  selected V2 simulation source ownership without changing scientific tuning.

- Q1 recovery1 acquisition CLOSED INCOMPLETE: first discovery case recorded all
  125 simulated seconds and clean final-zero/shutdown/cleanup, but supervisor
  SEARCH->FAILSAFE and required centroid diagnostic coverage failed. The three
  later cases were not dispatched; zero qualified inputs or scientific results.
  Bounded read-only diagnosis of the first safety event and dual joint-state
  publishers is active. No source/tuning change occurred during the fixed run.

- Q1 acquisition v1 CLOSED INCOMPLETE: installed recorder entry-point resolution
  failed before creating a run directory or starting Gazebo; cleanup PASS;
  later cases not dispatched. Zero recorded trajectories or scientific outcomes.
- Active bounded recovery: `q1_acquisition_recovery_plan.md`, diagnosing the
  selected Python distribution and preparing a new acquisition identity only.
  Prior Q1 source/release entries below describe historical boundaries.
- Recovery1 source checks PASS: the source-path prepend selected stale tracked
  seven-entry metadata. The corrected overlay resolves all21 installed targets;
  the actual recorder help succeeds. Explicit acquisition root/ID and environment
  guards pass42 combined checks in2.91s. New freeze/checkpoint precede dispatch;
  `validation/q1_acquisition_recovery.md` records exact commands and receipts.

- M1 implementation and finite evaluation CONCLUDED; research qualification
  NOT ACHIEVED. No detector setting selected. Original M1/M1a scientific
  failures and the M1a label timeout remain retained.
- All M1a enclosures qualified; recovery produced31 spatial labels in31.818s.
  Fresh36-grid completed:15 settings pass79synthetics, zero retained common
  positives prevent selection. Three settings flag labeled negative travel.
- M2 correction closeout/checkpoint COMPLETE within implementation scope. Synchronized rolling
  GESC implementation and the finite historical reference attempt have concluded;
  direction research qualification remains NOT ACHIEVED. Reference v1 is closed
  EVIDENCE_UNAVAILABLE: all192 slots lack anchors after8 input rejections.
  See `validation/m2_reference_v1.md`; never retry that fixed version.
- The diagnosed upstream10Hz restamping defect is corrected under
  `m2_source_clock_correction.md`: schema2 acquisition keys, detached source
  admission, separate original receipts/admission, complete callback receipt
  capture, explicit source-key invalidation and bounded late-packet tombstones.
- Final integrated checks:433 PASS/1 inherited quaternion warning in9.27s,
  `builds/initial/m2_clock_integrated_v3.log`. Actual upstream ROS transport:
  2 PASS/3 inherited warnings in8.00s, `m2_upstream_transport_v8.log`;453 normal
  acquisitions share151 publication ticks,186 observations qualify after3cycles,
  and one fresh source recovers instantaneous fallback after deliberate faults.
  Warnings arise in an unused inherited quaternion intermediate; checked
  transforms and output values remain finite. No field/Gazebo result is implied.
- Preserve source-correct transport evidence separately from unavailable
  historical scientific evidence. A revoked previously valid key still fails
  the recorder's strict source-integrity check; runtime recovery cannot qualify
  ambiguous recordings. Full closed-loop and angular/availability targets remain.
- M3 COMPLETE within source/validation scope: `m3_handoff.md` records the
  authoritative epochs, raw-cycle moving verification/control and candidate-bound
  transactions. `m3_plan.md` remains the closed implementation contract.
- M3 final broad integration:812 PASS/1 inherited quaternion warning in53.36s,
  `builds/initial/m3_integrated_v2.log`; three-package build20.7s PASS.
- Selected detector source admission, same-epoch numerical reset, frame guard,
  original ROS/steady receipt and final-publication freshness are corrected;
  193 focused checks plus3actual PDE/detector DDS cases pass, including source
  headers33.333333ms ahead of held100ms clock ticks. Final integrated812 adds
  the publication-race regression. Exact commands: `validation/m3_common_contract.md`.
- Supervisor51focused, controller58focused/19legacy, Gaussian51finalfocused and
  prior76transport/regression checks, and recorder82checks pass. Actual moving
  supervisor/worker/composer pipeline2DDS cases pass: inactive PREPARED,
  atomic commit and digest acknowledgement; departure cancels pending worker.
- Final Arm C wrapper-publication admission68focused checks PASS0.43s,
 3actual epoch DDS cases PASS1.14s; `validation/m3_history_admission.md`.
  Final recorder/analyzer temporal consistency7PASS2.58s. Original failures
  remain retained; these focused corrections postdate the812-check boundary.
- Q1 ACTIVE SOURCE/PREFLIGHT: `q1_plan.md` selects the finite four-run primary
  shadow qualification study with125simulated seconds after readiness, fixed
 48direction slots and separate discovery/confirmation. No Gazebo dispatch yet;
 source checks, machine-readable freeze and checkpoint precede release.
- Q1 source integration:197 checks PASS23.96s; incremental three-package
  build PASS2.37s; actual installed assets/source bindings checked. The
  source/geometry freeze verifies532 files and2869 geometry receipts with no
  new field calculations. Exact records: `validation/q1_preflight.md`.
- Q1 first source contract0921e90a... is preserved UNRELEASED: actual Humble
  launch frontend found V2 quoting across substitution fragments. No Gazebo
  started. Bounded XML/frontend/RCL-string correction passes96 tests9.05s and
  actual installed --show-args. Replacement contract570b335c... binds533 source
  files and2869 geometry receipts. Checkpoint/release receipt remain before
  acquisition; no Gazebo run has started. Scientific
  parameters and four-run population remain unchanged.
- M4 pilot has not started and is not released by independent M3 tests.

## Current problem or blocker

- Q6 analytic comparison is complete, but the two-block methodological choice
  and runtime implementation remain pending. The user requested a fresh-chat
  transition; fresh_chat_handoff.md preserves the exact choice and resume point.
- M4A source review found swallowed procfs errors could overstate cleanup.
  The bounded strict-inspection correction is now CLOSED PASS, with intermediate
  source versions and the final47-case evidence retained.
- Q2 v2 is closed with no qualifying positive residence exposure, no detector
  nomination, and unavailable scientific qualification. Its direction discovery
  diagnostic does not establish the original accuracy targets. Old confirmation
  remains sealed; source integration tests do not replace empirical evidence.
- M4 independent labels/references, disturbance-bound receipts, analysis budgets
  and development/holdout release contracts remain prospective in m4_plan.md.

## Files currently relevant

- Start with `fresh_chat_handoff.md`, `plan.md`, this status and
  `validation/acceptance_ledger.md`; then Q6 plan/result, Q5 handoff, M4A
  plan/validation/handoff and the prospective `m4_plan.md`.
- Historical references below preserve provenance; their old use of "active"
  does not reopen completed work or supersede the current milestone above.
- Closed amendment: `q2_policy_runtime_plan.md`; implementation designs:
  `q2_policy_math_design.md`, `q2_policy_owner_audit.md`. Latest completed evidence:
  `q1_direction_policy_handoff.md`, `validation/q1_direction_policy_result.md`.
  Closed numerical contract: `q1_observed_phase_reference_plan.md` and its design.
  Original Q1 closure: `q1_handoff.md`, `validation/q1_study_v1.md`.
  Read-only M4 interface gap: `m4_preparation_audit.md`.
- Completed filter correction: `q1_filter_expiry_recovery_plan.md` and handoff;
  completed acquisition: `q1_acquisition_recovery4_plan.md`. Recovery3's failed
  acquisition and two accepted discovery inputs remain retained separately.
- Historical acquisition amendment: `q1_acquisition_recovery2_plan.md`; completed source
  correction `q1_simulation_source_plan.md`; prior acquisition
  recovery contract `q1_acquisition_recovery_plan.md`; unchanged method
  `q1_plan.md`; selected methodological/input proposal
  `qualification_release_review.md`.
- Active M1 clarification: `m1_implementation_clarifications.md`.
- Frozen: `m1a_plan.md`, `validation/m1a_contract_v1.json`.
- Closed technical recovery: `m1a_recovery_plan.md`.
- Active sequencing: `m1_to_m2_sequencing.md`; M1a final evidence in
  `validation/m1a_calibration.md` and `validation/m1a_calibration_manifest.json`.
- Active M2 implementation contract: `m2_plan.md`; reference protocol
  `m2_reference_plan.md`; accumulating evidence `validation/m2_validation.md`.
- Closed reader correction: `m2_reference_preflight_recovery.md` and its
  validation record. Current completed source correction:
  `m2_source_clock_correction.md`; validation records `m2_clock_admission.md`,
  `m2_clock_wiring.md`, `m2_upstream_clock.md`, `m2_upstream_transport.md`.
- Closed M3 contract: `m3_plan.md`; handoff `m3_handoff.md`; evidence `validation/m3_validation.md`.
  Prior read-only audit: `m3_preparation_audit.md`.
- Original failure: `validation/m1_replay_calibration.md`,
  `validation/m1_replay_calibration_manifest.json`, and the two diagnosis files.
- Existing package `tools/{validate_phase_context,init_phase_status,checkpoint_phase}.sh`.
- M0 `validation/baseline_inventory.{md,json}` and `validation/interface_audit.md`.

## Decisions and rationale

- User locked simulation-only implementation of both changes; no stationary
  acquisition fallback on uncertain direction; existing GESC enhancement;
  16 fresh Gazebo runs after offline qualification.
- Existing shared runtime profile and owners remain; new modes opt in.
- Existing V1 skill is scoped to V1; extend existing tools for `v2` without
  altering closed V1 records or inventing a reopened Phase 08/10.
- V1 branch remains at `1af67c6`; do not commit/amend that branch.
- Fill activation must be linearized at the fill owner's validated registry
  commit. A canceled preparation cannot activate; an already accepted fill
  persists and cannot be retroactively canceled by later candidate departure.

## Validation checkpoints

- `timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 10 plan`
  PASS: inherited baseline context only; no V2 runtime result.
- `timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 plan`
  PASS after new plan/tool support.
- `timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh v2`
  PASS: initialized this absent status with existing template semantics.
- Final M1 implementation checks: 132 node/core/history/legacy regressions,
  123 recorder/contract regressions, 33 analyzer/replay checks, and one real
  ROS transport test pass. The original calibration scientific gate FAILS.
- M1 records are in `validation/m1_validation.md`; all commands use the
  isolated source overlay. No Gazebo or closed-loop performance claim.
- M0 workflow regression suite: 10 passed; syntax/context/diff checks passed.
- Isolated colcon build: 3 packages passed; source imports verified.
- Inherited detector regression suite: 13 passed.
- Frozen inventory: 21 complete hashes/integrity/count checks passed, 273
  retained artifact hashes verified; no independent labels claimed yet.
- No Gazebo/hardware execution or runtime-source edit occurred during M0.
  See `validation/{workflow_validation,environment_validation,baseline_inventory,interface_audit}.md`.

## Attempts not to repeat

- Do not restart Q1 original/recovery1/recovery2/recovery3 acquisition directories
  or reuse their reserved run IDs for new dispatch. Their closure receipts and
  failed outcomes remain immutable. Recovery4 is a prospective finite import of
  exactly two already accepted discovery inputs plus two newly identified
  confirmation acquisitions; it is not yet released.

- Do not retry `q1_primary_shadow_v1/acquisition/` or its reserved run IDs.
  `validation/q1_acquisition_failure_v1.md` closes the packaging failure.
  Any acquisition recovery uses its own frozen contract, IDs and artifact root.

- Do not rerun or overwrite `m1_calibration_v1` or `m1_labels_v1a`: fixed
  calibration is failed, geometry labels unavailable; use a fresh amendment.
- Do not overwrite `/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1_labels_v1`
  or its log: its final JSON publication failed and remains failed.
- Do not run the stale normal installed modules as V2 qualification.
- Do not use failed/selected V1 outcomes or the old detector's flags as
  independent labels, or rerun frozen V1 experiments under their old identity.

## Remaining work

1. Resume from fresh_chat_handoff.md and the current Q6 decision. After explicit
   method choice, document and validate the bounded selectable detector amendment.
2. Complete the pending M4 independent label/reference, disturbance-receipt,
   execution/analysis-budget and development-to-holdout release contracts.
3. Use the approved four visible development and twelve frozen holdout runs,
   preserving all outcomes and integrity stop conditions; no extra qualification
   acquisition chain or reopening of Q1/Q2 confirmation is released here.
4. Complete acceptance audit, report and final handoff with honest scientific
   limits. Q2 v2 acquisition/scientific jobs are already closed as documented
   above; their qualification-unavailable result remains unchanged.

## Stop conditions

- Stop for objective/cost-sign/unit/ownership/compatibility/physical-authorization
  conflict or overlapping user change that cannot be preserved.
- Run no physical graph, device, transfer, mount, or snapshot mutation.
- Bound ROS/tests/Gazebo explicitly. Safety/completeness/cleanup failure aborts
  pilot dispatch. Preserve behavioral failures; never tune during the frozen
  pilot. Close failed versions before separately documented corrections.

## Compaction recovery

Before further changes, reread the plan and this file, inspect Git status and
the current diff, identify the next incomplete acceptance criterion, and
continue only from that verified state. Read the latest active amendment listed
above; older dated release entries are historical and do not reopen closed jobs.


## Q1 acquisition release — 2026-09-09 UTC

All source prerequisites pass at the corrected boundary. The immutable
pre-acquisition checkpoint contains167 changed/untracked files,796863-byte
verified archive and35 retained artifact hashes at
`/home/mattb/Experiments/GESC-Gaussian/v2/checkpoints/q1_preacquisition_v1/`.
Manifest SHA256:
`9a1dd6dd09eda9b8f0f4b1c28464d1b5ec203cb8e89f54380fc923856e82b309`.

Exact contract: `qualification/q1_primary_shadow_v1/preflight/contract_v2.json`,
SHA256 `570b335c95b034c9da6d350f73fa20c9b7d6be9c8a77b8c14bf2ba714626f1bf`.
The adjacent `dispatch_release.json` binds that contract, checkpoint, all source
checks and exact acquisition argv/environment. The wrong-domain guard rejects
before creating acquisition output. The original contract remains unreleased.

Released scope is exactly four fixed shadow simulations; first visible,
125 simulated seconds after readiness,240s per-process ceiling and1200s total.
Safety, completeness, cleanup or input-binding failure stops later dispatch.
This live receipt was appended after the immutable source checkpoint. No
scientific qualification or M4 release is implied. Acquisition results must be
read from the exclusive `acquisition/` artifacts; no fixed input is replaced.

## Q1 acquisition recovery1 release — 2026-09-09 UTC

Original acquisition v1 remains CLOSED INCOMPLETE before any recorded exposure.
The recovery contract binds539 source files,2869 preserved geometry receipts and
all21 actual installed console targets. Original scientific settings, geometry,
resolved cases and timing were compared directly and are unchanged.

External V2 root: `/home/mattb/Experiments/GESC-Gaussian/v2/`.
Contract: `qualification/q1_primary_shadow_v1_recovery1/preflight/contract.json`,
SHA256 `f4fca24e4e39f791396be76674d56eaa6c4ced4b6ba472ca0a7975da3b547b17`.
Checkpoint: `checkpoints/q1_preacquisition_recovery1/manifest.json`, SHA256
`85af0eca9eb2bc6d4c1a6f587a9d8b6a58e8f462cba771746c123fb06f17c963`;
174 source/evidence files,810328-byte verified archive,44 retained artifact hashes.
Adjacent contract `dispatch_release.json` SHA256
`516e4ad551b17491e268fb27abc8b5f650a478d72029cb04d9d8d05a0d86c72f`
binds corrected environment, source checks, checkpoint and exact1140s interrupt
plus60s kill command. Display check PASS; no prior Gazebo/recorder process found.
This live receipt postdates the immutable checkpoint. Read outcomes from the
recovery's exclusive `acquisition/` directory; release is not qualification.

## Q1 acquisition recovery2 release — 2026-09-09 UTC

External root: `/home/mattb/Experiments/GESC-Gaussian/v2/`.
Contract: `qualification/q1_primary_shadow_v1_recovery2/preflight/contract.json`,
SHA256 `fab39867d80562230ea78cfdb3f863f7b1c4899932cb478a16736f8373402ad4`;
543 source files,2869 preserved geometry receipts and21 console entry points.
The source checkpoint is recorded above. Adjacent `dispatch_release.json` SHA256
`6f6788bf1f1b877291c9005f6da8440cfd453edfaca44eabf4d81e54e2035671`
binds the exact environment, all source checks and1140s interrupt/60s kill argv.
Resolved cases, scientific settings/geometry and durations match recovery1;
new IDs/root distinguish the corrected source attempt from its retained failure.
Display check passes and no prior Gazebo/recorder process remains. This live
receipt postdates the immutable source checkpoint. Four complete inputs are
required before scientific analysis; any safety/completeness/input/cleanup
failure stops later dispatch. M4 remains unreleased.

## Q2 runtime material closure

Saved `checkpoints/q2_policy_runtime_closed_v1/manifest.json` under the external
V2 root, SHA256 `7df68a0af0b4fb953fc0631a4a5d0f9572d718a5ba74818deed025b583327863`:
252 files,1045977-byte verified archive,482 retained artifact hashes. Context,
diff and checkpoint checks PASS. This receipt was appended after the immutable
archive; runtime source stayed held. Q2 source/test milestone is CLOSED. Fresh
qualification proposal remains the next work; no M4 or scientific release yet.

## Q2 qualification material preflight

Saved `checkpoints/q2_qualification_preflight_v1/manifest.json` under the external
V2 root, SHA256 `bb853c7b8dd549d106ee885f1b369d5e38c84a7019acbf7a570ff5ffd7793d24`:
258 files,1079464-byte verified archive,69 retained artifact hashes including
the prior runtime closure. Context/diff/checkpoint checks PASS. This live
receipt postdates the immutable archive; source stays held.

Fresh `qualification/q2_primary_shadow_v1/preflight/contract.json`, SHA256
`a1b3b0b1d76e373e7a340a8749c898724d1f731a51eb90cd536e48f96b1fb7a3`,
binds4 planned runs,570 source receipts,2869 reused geometry receipts and48
symbolic target slots. Confirmation has no derived source identities before
nomination. Contract/environment audit and an explicit release receipt precede
the single bounded acquisition; scientific qualification and M4 remain open.

## Q2 acquisition release

Final frozen audit PASS, `builds/q2_policy_runtime_v1/q2_frozen_contract_audit_v1.json`,
SHA256 `f249d0e279174fbd37380c5f19e96450203db8d217f00e4841ae5574ca63c874`.
Exact4 rows/48 symbolic slots and all gates match;3464 receipts unchanged.
Adjacent contract `preflight/dispatch_release.json`, SHA256
`a76f33cc216bdea3235efa1a995ffd602752f7c4e0a1ccc9aa658417234faeca`,
binds the current source checkpoint, source/build/audit receipts, environment
and exact1140s interrupt plus60s kill argv. The single acquisition was dispatched
through its pinned bounded wrapper; first case visible. No automatic retry or
scientific qualification follows an acquisition pass. Read the exclusive
`acquisition/acquisition.json` and `preflight/dispatch_completion.json` for the
outcome when present; source remains held throughout.

## Q2 acquisition v1 closure

Single job exit1,167.246393s wrapper/164.732646s acquisition. One complete125s
recording passed infrastructure, spawn, final-zero and cleanup; zero inputs
accepted because of the direct-versus-dated directory mismatch. No second case
or scientific stage ran. `qualification/q2_primary_shadow_v1/acquisition_closed.json`,
SHA256 `672d5fee47ce41803b93827db04788b18839bfc35f2693a49ea4d2d0b0935c02`,
binds20 retained files and570 unchanged frozen source receipts. This version
is CLOSED_INCOMPLETE. Its separate prospective correction uses new31-series
identities and preserves all scientific gates and runtime/numerical owners.

Material failed-attempt archive:
`checkpoints/q2_acquisition_closed_v1/manifest.json`, SHA256
`670a20d983dd2919807e324c2a305258c9e4166853d34b8769ca26079bfaeb44`:
260files,1083715-byte verified archive,98retained hashes. Source correction starts
after this boundary under the new amendment. No Q2v2 acquisition is released.

## Q2 v2 preflight freeze

Material source checkpoint `checkpoints/q2_path_correction_preflight_v1/manifest.json`,
SHA256 `dd58bf51154efdfbfeff2240770c2c66a92abfde512882d6a3917d1685d4582d`:
263files,1092156-byte verified archive,109retained hashes. Context/diff/checkpoint
PASS. This live receipt postdates the archive; source remains held.

`qualification/q2_primary_shadow_v2/preflight/contract.json`, SHA256
`f3e31a16b6008e11ae953813f0188e52a451e275a653fb865d88d50922704fa6`,
binds573 source receipts,2869 geometry receipts, four31-series cases and48
symbolic slots. Current source/environment/installed/display checks PASS;
final frozen-case audit and release receipt precede dispatch. Original Q2v1
remains CLOSED_INCOMPLETE and no old recording is imported.

## Q2 v2 acquisition release

Frozen audit `q2_frozen_contract_audit_v2.json` SHA256
`c466038c07494d89de94c09cc056223551eb030386b2d7475481dcb8e5cf874e` PASS.
Exact31-series identities/48 slots and unchanged scientific controls/gates match.
Root reverified573 source receipts and2869 geometry receipts plus installed
environment. `qualification/q2_primary_shadow_v2/preflight/dispatch_release.json`,
SHA256 `be1a6a42a71e5b081614088b5ec0b58bba62873ce9981b1163d90a9be3327328`,
binds current checkpoint and all focused-source/build/audit receipts, environment
and exact1140s interrupt/60s kill command. Pinned run_q2_acquisition_v2.py dispatched
the single four-case acquisition, first visible. Source stays held; no automatic
retry. Read its acquisition and dispatch-completion receipts for final status.

## Q2 v2 complete acquisition boundary and labels

All4 inputs accepted, all runner/cleanup gates PASS, acquisition639.006260s and
wrapper641.103203s exit0. Material checkpoint
`checkpoints/q2_v2_acquisition_complete_v1/manifest.json`, SHA256
`6eb15eb0abc88e06dab7aaade3e9f26acb2686f011c5db9960a40cfd1ae26cac`:
264files,1094251-byte verified archive,182retained hashes. This live receipt
postdates the archive; source stays held. One600s existing evaluate_q1.py labels
job dispatched, with exclusive preflight/label_dispatch.json binding the
complete acquisition/manifest and preflight/labels.log retaining output.
No scientific result is inferred from acquisition success; wait for the
completed analysis/label_job.json to select the permitted reference branch.

Material source archive PASS: checkpoints/m4_v7_recording_clock_range_source_v1/manifest.json
SHA256 5befd6c9408e7aeda174cabc647e00e58a800643ad0f3bca5912fd03a2a0e1e7;393 files,63 externalrefs,1542140-byte verifiedtar.
Context/diff/checkpoint PASS. This live receipt postdates immutablearchive.

Current next milestone: [bounded measurement diagnosis](m4_v11_measurement_diagnosis_plan.md),
adopted2026-09-11UTC. One cached spatial job60s and one filtered two-topic command
job120s, each exclusive and no retries; no source correction or metric promotion.
V11 closure archive583 members verified0.997531s, manifest
`468bb21a08f13ae89014b372117833a987804c7152accc1616a0f7b84f89235f`.
Context/diff/checkpoint passed at the closure boundary.

Measurement diagnosis Job2 ACTIVE session56873 (115s SIGINT+5s kill), one filtered
read of C command/diagnostic/readiness topics. No simulation. Job1 not yet started.
See [diagnosis execution](validation/m4_v11_measurement_diagnosis.md).

Latest: Job2 terminal/reaped0(session56873),3.933934s,30stablepins. One filtered
read reproduced allcounts/errors;312equivalent extra-zero candidates all occur
before readiness. Later command alignment is consistent; no Cmetricpromotion.
Job1 cached diagnosis not yet dispatched. No application runtime active.

Job1 cachedresidence diagnosis ACTIVE session74919,55sSIGINT+5skill.
Job2 complete with independentreviewPASS: startup-only discrepancy,11493exact
in-readinesspairs and314exactpost-readinesspairs. No source or fixedmetric change.

Both measurement jobs now terminal/reaped0: Job1session74919PASS2.870768s,
27stablepins; Job2session56873COMPLETE3.933934s,30stablepins. Maskdiagnosis
reproducesalloriginalinput/residenceprefixes: everypointbreak remains inside
localexclusion, C has2segmentbreaks. No newlabels/qualification/sourcechanges.
No runtime active. IndependentJob1review and prospective nextmethoddecision pending.


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

R21 D01 material evidence checkpoint: context validator, diff check and existing
checkpoint tool PASS. Archive `checkpoints/r21_visible_d01_diagnostic_v1/`
verifies657 source members in1.471749100s; manifest SHA256
`be8c46cf8b63e8e0f64b7a5387c9a2ba4fd27d4d778a675831c0f066d41e0140`.
Exact invocation: `timeout --signal=INT --kill-after=5s 25s python3
/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r21_recurrent_trapping_v1/save_visible_checkpoint.py`.
Source archive and external evidence hashes retain this boundary; generated
interface intermediates and raw bag bytes are excluded from new enumeration,
with their prior receipts preserved. This live receipt postdates the immutable
archive. All scientific sessions are terminal/reaped; task changes remain
uncommitted on feature/gesc-gaussian-robustness-v2 at3369cfc.

D02 source validation is complete:62 checks passed in the initial63-case bundle;
the only failure was an incorrect expected unit in the new legacy-parity fixture.
Correcting that literal to the unchanged `s by state` passed the single case.
Production analyzer stayed fixed; this is combined evidence, not one63-pass run.
The cached D01 state component passed all8 checks, measuring149.4s over2.5–151.9s,
retaining the two legacy bag-clock failures and rejecting a real0.2s source gap.
Independent cached review passed19 checks. Fresh D02 preparation passed with
607 source pins and21 installed entrypoints; concrete dispatch is next.

D02 pre-visible material archive PASS:660 verified source members in1.474091725s;
manifest SHA256
`e4a6f4382fd447ed4387bf7d125f8b4f61718e486f4512e72f89b3c227043cac`
at `checkpoints/r21_d02_previsible_v1/`. Context/diff/checkpoint checks PASS.
This receipt postdates the immutable archive. The sole visible acquisition
session93267 is now RUNNING under the720-second inclusive root cap; exact
argv/start/prepared hash are retained in D02/execution_started.json. All607
prepared source/helper paths must remain unchanged until terminal analysis.
No other simulation or matrix is released.

## D02 terminal complete acquisition and active analysis

Session93267 terminal/reaped0,255.288028865outer/254.767491861helper seconds.
All607 sourcepins stable; both cleanup owners PASS. Native recording COMPLETE
with no failures/run_error and finalzero observed. All11primary predicates PASS.
State path SEARCH→VERIFY→DESIGN→ESCAPE_REPULSE→ESCAPE_ASSIST→SEARCH, one
committed fill and completed recovery. Live arrival197.18sim seconds,
0.499521337533m at(3.543455871,3.002372475); recorded exact pose join is pending
the sole analysis. Optional fixed simulationduration is absent as intended.
GOAL_HOLD not required. Exact outcome retained in acquisition_projection.json.

Analysis prepared617pins, SHA256
`8f814f69bef26d8b12e862aa45e1cff415e3c9eb2dbf336a921b770d4ed66321`;
sole session6585 RUNNING under120s inclusive, outputs analysis_v1/. Two native
scans only, new explicit simulation publication-duration basis, existing native
completeness/motion/arrival gates. No new reference or simulation yet.
