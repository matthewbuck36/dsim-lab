# M4 v3 recorder shutdown amendment

Status: ADOPTED FOR IMPLEMENTATION,2026-09-10 UTC, under the user's active
full V2 goal and explicit authority to perform recommended bounded corrections
without further questions. Simulation only. Preserve M4v1/v2 as immutable
failed versions; this is a fresh16-slot comparison after new source/process,
preparation, audit and release gates. No retry or replacement within a version.

## Evidence and purpose

M4v2 stopped after536.403020s with one incomplete baseline and15 unstarted.
Both kernel ownership proofs and performed cleanup pass. The initial graceful
SIGINT went only to the ros2-run wrapper. The recorder was later terminated/
killed before finalizing its bag, so final-zero and recording are unproved.
Read `validation/m4_pilot_v2_result.md` and `m4_pilot_v2_handoff.md` first.
Closure archive manifest SHA256
`846f535e46e86389fd632cbb1dcf094d9d640f9dc2596ded374b65bd2765f492`
binds dirty source and evidence references; closure audit binds all610 source
pins and46 pilot files/403938081bytes, including the unmodified raw bag.

Installed `/opt/ros/humble/lib/python3.10/site-packages/ros2run/api/__init__.py`
SHA256 `bdc67613b3e94a149f184f5a9adb03f08f6894a7f045ed02f0af5bef75d06c47`
spawns its executable in the same group and catches KeyboardInterrupt without
forwarding PID-only SIGINT. It expects group signal delivery. Source fixtures
that used only direct Python workers missed this wrapper integration boundary;
retain the passing narrow evidence and add the exact missing hierarchy.

Both original research goals, algorithm choices and scientific gates remain
unchanged. No detector/GESC retuning is justified by this infrastructure failure.

## Selected implementation and ownership proof

Add explicit `process_ownership_mode=subreaper_group_v3` within the same
existing runner/science ownership helpers. Preserve default `observed_tree_v1`
and selectable direct-child `subreaper_v2` behavior. Reuse the same subreaper,
exclusive wait ownership, native SIGCHLD admission, pidfd escalation and final
ECHILD witness; no parallel runner/recorder/node or new console entrypoint.
The existing `ros2 run` CLI commands and recorder ownership remain in place.

For the new mode's first graceful SIGINT only, signal the original process
group after proving the registered direct Popen root remains unreaped with
matching PID/start ticks, parent equal to this owner, and PID=SID=PGID.
Keep exclusive reaping and perform no poll/wait/reap between final guard and
group signal. A root that exits during that interval remains an unreaped child,
reserving its identity. An unrelated process outside this new session cannot
join its group. Bag/target children deliberately have separate sessions and
must remain under the recorder's ordered stop/finalization flow.

This is a guarded `killpg`, not a pidfd group signal. Record monotonic signal
time, phase, group/leader identity and delivery result truthfully. Guard or
permission errors are explicit failures, not a weaker success fallback. Never
signal a stale/reaped/replaced group. When the root was already reaped, retain
bounded adopted-child pidfd cleanup and report that separate context. Subsequent
TERM/KILL escalation remains identity-validated and scoped to owned processes.

Keep the original graceful allowance and absolute work/case/suite ends. Do not
renew deadlines or expand cleanup because of an incomplete recording. A signal
send receipt does not prove finalization: preserve actual recorder metadata,
final-zero, bag completeness, graph/session/identity cleanup and ECHILD gates.
The controlled caller must retain exclusive wait ownership; this does not
claim protection against a foreign native waiter violating that prerequisite.

Primary semantics: [setsid](https://man7.org/linux/man-pages/man2/setsid.2.html),
[setpgid](https://man7.org/linux/man-pages/man2/setpgid.2.html),
[wait](https://man7.org/linux/man-pages/man2/waitpid.2.html), and the installed
Humble wrapper above. New sessions begin with the caller alone, children inherit
the session, and group moves cannot cross sessions; unreaped children retain
kernel process state. These semantics support the guarded initial delivery.

## Fresh identity and unchanged comparison

Add the exact allowlisted experiment `m4-pilot-v3`, exclusive root
`/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v3/`, unique `m4_v3_...`
case IDs and `m4-pilot-v3-slotNN-ARM-SEED` run IDs. Select the new ownership mode
in outer runner, inner recorder and science routes; bind this plan, installed
wrapper bytes and every selected source/configuration/entrypoint receipt.
Reject wrong version/root/identity/mode or cross-experiment analysis input.
Preserve all v1/v2 default/output/selection contracts. Scientific method identity
remains `m4-pilot-v1`; numerical definitions and targets do not change.

Retain16 A/B/C/D slots, primary visible development seed26090801 and twelve
secondary nominal/noise/delay holdouts seeds26090802/3/4. B/D keep Q7 two-block
W6s/.18m/.50m; C/D keep Q2 mean weight.75 and all M3 evidence safeguards.
Keep geometry/controls/clocks/command limits, independent12s residence labels,
publication-based latency,12 endpoints/six pairs, all192 direction targets,
augmented-objective references, wrong-fill/goal and mandatory-stop attribution.
No extra qualification acquisitions or import of old failed data into new slots.

One exclusive600s preparation,720s recording/900s inclusive cases,15300s
suite including900s science. Four visible development cases precede one-time
holdout freeze; no post-freeze tuning/replacement. Integrity failure stops this
version; complete behavioral/scientific failure remains an outcome. Further
correction requires another evidence-backed amendment, never an automatic retry.

## Required validation and release

1. Retain exact M4v2 closure, installed wrapper and source copies before edits.
2. Reproduce PID-only shutdown failure once with actual installed
   `ros2run.api.run_executable` around a finite recorder fixture. The recorder
   starts separate-session target and bag fixtures, catches SIGINT, records a
   final-zero marker, then stops target, flushes/stops bag and writes finalized
   metadata. Its ordered shutdown must require more than the scaled escalation
   allowance, so late TERM/KILL cannot accidentally pass. No ROS graph/Gazebo.
3. Test the new mode against that same hierarchy: early SIGINT reaches recorder,
   final markers/status survive, target/bag receive no premature group signal,
   all kernel flags pass, unrelated sentinel survives and original end holds.
   Include reaped root, changed PID/start/parent/session/group, native wait
   interference, permission errors, interruption and forced escalation. No
   posthoc widening of fixture timing to obtain a pass; retain any failure.
4. Validate selected outer/plain, inner/specialized and science routes, fresh
   identity/rejection, legacy compatibility and relevant inherited regressions.
   Integrate with before/after source hashes and actual installed CLI checks.
   Review diff, update validation/status/handoff and material checkpoint/archive.
5. Prepare once; independently audit exact16 commands/source/configuration/
   geometry/noise/delay/budgets and release. Dispatch once, preserve every slot,
   produce all-slot report and full requirement audit, handoff and final archive.

External new source/test evidence root:
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v3_recorder_shutdown_v1/`.
No physical/Pi/V1 action, commit or push is newly authorized. Preserve unrelated
work and the existing public architecture, cost sign/units and controller owner.
