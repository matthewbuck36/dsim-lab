# Bounded recorder clock-range optimization

Status: ADOPTED FOR SIMULATION SOURCE VALIDATION,2026-09-10 UTC. The user's
active goal authorizes recommended bounded corrections without renewed
questions. This is a Level B performance correction preserving every integrity
predicate, numerical result, control setting and deadline. It does not release
a new acquisition or reopen M4v6.

Prerequisite: [V6 handoff](m4_pilot_v6_handoff.md) and
[result](validation/m4_pilot_v6_result.md). V6 closure archive is verified:
`checkpoints/m4_v6_closed_incomplete_v1/manifest.json`, SHA256
`14fcd13e0c19c9b5aeab4f1cfd1708541463d5dca4b9ecd15d4015a82f011773`;
388 files,195 external refs,1515652-byte verified source tar. The raw bag and
all incomplete evidence remain retained. Closure audit SHA256
`2d59c4e00ccb25a1d83ad9c1873ae8842a0fbc29e1f5de2a3d9f8f3908b55d1b`.

## Evidence and exact change

The recorder's successful validation/final writes took about115.12 seconds
after clean wall_end. The enclosing work deadline interrupted its inner runner
shortly before publication, leaving no scenario classification despite48/48
recording completeness and outer cleanup passing. This is a selected timing
collision; no validator function has been runtime-profiled.

Current validate_run.py SHA256
`71b1d3636f89f59b796806fdf66e6ae12ce2af33c56efd24ae844e5653678306`.
Within validate_run_directory, lines1052-1058 recompute min(clock_values) and
max(clock_values) for each typed timestamp. That is O(T*C) work for T admitted
typed stamps and C recorded clock values. Retained counts show C=6236 and at
most434394 timestamp-bearing messages across nine topics before readiness
filtering, permitting about5.417 billion redundant comparisons. Actual filtered
T and the runtime share remain unmeasured. _read_bag decodes each record once;
do not invent duplicate decoding or blame the later, unreached _bag_outcomes.

Compute the minimum and maximum once inside the existing simulation/nonempty
clock branch and reuse those exact integers in the unchanged per-item
timestamps_within_clock predicate. Keep min/max rather than assuming ordered
endpoints. Preserve tolerance, readiness slicing, topic/diagnostic order,
duplicates, rollback checks, empty-clock and physical behavior, all report
fields and every completeness check. No sampling, dropped decoding, new
validator/helper pipeline, caching across calls, deadline/grace changes or
algorithm tuning. Reuse the existing validator owner and relevant tests.

## Finite source milestone

Retain the source/test originals under a fresh external
`builds/m4_v7_recording_clock_range_v1/` before edits. Extend the existing
workflow collector's explicit plan list to pin this amendment. Keep V6 source
and acquisition archives immutable; no V7 identity/scenario route is admitted
in this source milestone.

1. Add a meaningful whole-validator fixture using existing synthetic recording
   setup. Instrument clock-list scans to expose repeated traversal without
   flaky wall-time assertions. Preserve output equality and strict timestamp
   boundaries, ordering, duplicate/regressing values and non-simulation/empty
   clocks. Review it before one baseline attempt, capped60 s, against unchanged
   validator source. Retain the expected performance-regression failure.
2. Make only the stated local optimization. Independently review the exact diff,
   then run the focused corrected fixture under120 s. No production refactor.
3. Run relevant existing recording/timestamp/clock/selection tests under240 s:
   test_experiment_recording.py, test_q1_single_source_graph.py,
   test_q7_recording_selection.py and
   test_m4_v6_centroid_heartbeat_selection.py, excluding existing Gazebo E2E.
   Bind complete source/test before-after hashes and installed Q5 owners.
   Retain any failure; a correction gets a fresh label and reviewed scope.

Use clean Humble->Q2->Q5, extremum-seeking/src appended, localhost domain189;
no concurrent ROS tests or simulations. Save exact commands/fixtures/caps and
immutable receipts before execution. No build is indicated for this Python-only
change; verify installed source binding. Do not rerun the old full matrix.

## One retained-recording validation

Only after focused/relevant source gates pass and a durable release is saved,
run the existing validate_run_directory exactly once on V6's retained slot1
with **write_report=False**, under an inclusive180-second cap. Save its result,
timing and wrapper/source/input hashes externally. Never call the default
writing CLI or replace original completeness.json/metadata/notes. Retain input
file hashes before/after, including the524685312-byte bag against the V6 closure
manifest. No field model, direction reference, label job or counterfactual replay.

Require exact equality of the entire returned report to retained completeness
(all48 checks, details, counts, warnings/failures and final passed flag). The
report has no dynamic timing field requiring exclusions. A practical selected
finalization target is <=60 s; the180 s cap only bounds diagnostic completion.
An over-target result remains evidence, not permission for repeated attempts.
The old115-second interval includes writes and is not a controlled speedup
benchmark. A passing result demonstrates this recording only, not a universal
maximum or retrospective V6 acquisition success.

After source and retained-recording validation, update live status/validation,
checkpoint and archive this source milestone. A separate prospective V7
identity/preparation/release amendment is then required for another fresh
16-slot comparison using the unchanged matched-gain and heartbeat settings.
Preserve720/900/15300-second maxima, all science budgets,192 targets, original
denominators and development-to-holdout gates. Both research goals remain open.
No physical/Pi, V1, commit or push work belongs to this milestone.
