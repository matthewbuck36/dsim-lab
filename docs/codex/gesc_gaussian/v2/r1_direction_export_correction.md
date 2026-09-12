# R1 direction C v2: native scalar publication correction

Status: ADOPTED, 2026-09-10 UTC, under the user's revised development authority.
The original [R1 diagnostic](r1_direction_diagnostic_plan.md) remains failed
only at publication; preserve `direction_c_v1/` and its exact failure/closure.

The first existing numerical result contains a NumPy `bool_`. Neither the
orchestration writer nor the existing atomic writer accepts it directly. Reuse
the existing analyzer `_q1_plain` conversion before publication, exactly as Q1
does: numerical scalars become native scalars, recursively, without changing
any computed value. Pin that function's exact source separately because the
concurrent D3 correction changes an unrelated adapter in the same module.
Importing this helper must not invoke the adapter, labels or bag reader.

Use new exclusive root
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/direction_c_v2/`.
Keep the same fixed development C normalized receipt, all 24 original targets,
reference definition, numerical sources and 90-second inclusive execution cap.
Only diagnostic identity and publication normalization change. Use the existing
atomic exclusive writer after conversion. Retain incremental target files and
all existing integrity, finite-value, duplicate-publication and final-row checks.

Before the new numerical attempt, one 15-second source-only fixture checks
recursive boolean/integer/float scalar conversion, JSON native-type preservation,
actual atomic publication and refusal to replace an existing file, and nonfinite
rejection. Bind helper/function/writer/source/input receipts prospectively.
Then one new attempt through `run_once.py`, with SIGINT at 80 s, forced cleanup
at 87 s and the original 90 s inclusive ceiling. No automatic retry follows.

Decision/reporting rules are unchanged from R1. This is a corrected development
diagnostic, not a V9 science completion, fresh simulation or qualification.

## Pre-dispatch denominator correction

Before the v2 numerical attempt, source review found that converting only at
publication is insufficient: `summarize_direction` counts reference flags with
`is True`, which excludes NumPy booleans. The existing M4 numerical orchestration
owner must convert its completed result row through `_q1_plain` before retaining
the row, invoking the publication callback or summarizing. D3's retained actual
numeric fixture also exposed a nested NumPy boolean in the cycle result, so
reference-only conversion was insufficient. Whole result-row conversion covers
both outputs while leaving every numerical input unchanged. The D3 owner
implements and tests this minimal correction; numerical equations and target
selection remain unchanged. Source is released for that edit because no v2
numeric job has started.

The initial `prepared.json` and helper/plan copies remain retained as unstarted
preparation. A new `prepared_v2.json` binds the corrected owner, current helper
and this amendment before the sole v2 attempt. The passing native-scalar/writer
fixture remains valid because its conversion/writer owners are unchanged.
No v2 reference calculation occurred under the superseded preparation.
