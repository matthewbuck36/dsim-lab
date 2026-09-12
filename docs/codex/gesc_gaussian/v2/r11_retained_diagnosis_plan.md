# R11: diagnose the three retained V12 failures

ADOPTED prospectively, 2026-09-11 UTC, after V12 closed incomplete and its
600-member material archive was verified. This is bounded simulation-data
diagnosis under the user's existing development authorization. No simulation,
production correction, numerical reference rerun or confirmation release is
part of R11. V12 and all sixteen original dispositions remain immutable.

Evidence: [V12 closeout](m4_v12_handoff.md). Work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r11_retained_diagnosis_v1/`.
Use exclusive outputs, source/input hashes before and after, the selected ROS
environment, and existing readers/owners. Root owns the sole executions.

## Import subprocess

Hypothesis: importing the existing evaluator executes the runner's repository-root
Git command, contradicting the numerical worker's single-process requirement.
Run one import-only interpreter with a Python audit hook recording subprocess
executable, arguments, working directory and caller locations, excluding its
environment. No ROS initialization, numerical calculation or bag read.
Limit: 15 seconds work plus 5 seconds termination, 20 seconds inclusive.

Decision: record whether a subprocess is actually launched and which source
call launches it. This can establish a current import defect; it cannot identify
the historic PID 109098. Preserve V12's failed process verdict. A later correction
must retain the existing process gate and repository-selection compatibility.

## Noisy moving verification

Hypothesis: recorded candidate cancellation details distinguish insufficient
cycle support, trajectory disagreement, weak signal or another specific cause.
Read C/noise slot 11 and D/noise slot 12 exactly once each through
`bag_reader.read_run_bag`, selecting only algorithm events, algorithm state and
verification guidance (plus the reader's automatic readiness records).
Retain exact transition/candidate/epoch/time/detail fields and relevant guidance
boundaries. Summarize recorded causes without inventing unrecorded attribution.
No field reconstruction, direction reference or replay of the numerical model.
Limit: 55 seconds work plus 5 seconds termination, 60 seconds inclusive for both.

Decision: explain every retained VERIFY-to-SEARCH return from its recorded text
and context, or mark the missing/ambiguous evidence explicitly. Do not change
verification thresholds merely because an attempt failed. This is the next
research diagnosis; the process issue is not its explanation.

## B/noise arrival timestamp

Inspect the retained slot 10 metrics, live/recorded arrival evidence and exact
existing arrival-join owner first. If the source and cached records cannot
resolve the discrepancy, allow one filtered read of the necessary recorded pose
and readiness aliases through the existing reader; no full evaluator rerun.
Limit: 25 seconds work plus 5 seconds termination, 30 seconds inclusive.

Decision: identify whether the mismatch is distinct valid samples, missing source
timestamps, a frame/alias mismatch or another observed cause. Preserve the original
unavailable time. Any later correction must retain exact evidence binding and
must not replace the offline endpoint with a convenient live timestamp.

## Completion and next decision

Record each job's exact command, elapsed time, output and retained failure or
unavailable result. Review the small outputs and decide the smallest justified
next implementation or method experiment in a separate prospective amendment.
No full matrix, replacement acquisition, old-version resume, physical/Pi/snapshot,
V1, commit or push belongs to R11. The broader research goal stays incomplete.
