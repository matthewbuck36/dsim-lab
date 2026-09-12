# Recorder clock-range source validation

Status: IN_PROGRESS. Read ../m4_v7_recording_clock_range_plan.md.
V6 closure is immutable; no new acquisition/experiment identity is released.

## Prospective source commands

External root: /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v7_recording_clock_range_v1/.
The adapted existing root_source_validation.py captures exact pytest argv,
installed entrypoint bindings, full source before/after hashes and JUnit cases.
It has no Gazebo or retained-bag invocation. Command environment is clean
Humble->Q2->Q5, extremum-seeking/src appended, domain189/localhost1.

| Label/group | Inclusive cap | Selection |
| --- | ---: | --- |
| baseline_v1 baseline |60 s|New whole-validator clock-range fixture, original validator; expected scan-count failure only|
| focused_v1 focused |120 s|Same full fixture module after exact local optimization|
| relevant_v1 relevant |240 s|test_experiment_recording.py, test_q1_single_source_graph.py, test_q7_recording_selection.py, test_m4_v6_centroid_heartbeat_selection.py|

The inner pytest timeout reserves15 seconds; use outer timeout SIGINT at cap-1
with1-second kill allowance, so the full command remains bounded by its cap.
Exclude only the existing recorded_short_headless_end_to_end Gazebo test.
Do not start a bundle until its source/helper/fixture hashes and scope have
been reviewed. No concurrent ROS tests, simulations or decoding jobs.
Failures and tested source are retained; corrections receive new exclusive
labels. Exact release JSON precedes each command.

The source collector's one-line addition pins the adopted plan. It does not
change launch, execution, validation predicates or a historical experiment.
Fixture extraction/scan instrumentation is being prepared and reviewed before
baseline release. Validator remains unchanged at SHA256
71b1d3636f89f59b796806fdf66e6ae12ce2af33c56efd24ae844e5653678306.

## Retained recording prerequisite

Only after corrected source gates pass, a separate reviewed180-second release
may call the existing validator once with write_report=False on the retained
V6 slot1. It must preserve every original input hash and require exact whole
report equality, with <=60-second selected timing target. No such validation
has been executed or released at this entry.

## Baseline result and exact correction

Baseline_v1 is terminal1,9PASS/1 expected scan-count FAIL in0.60 s pytest,
1.196556448 s wrapper/60 s cap,633 unchanged source pins. JUnit records
64 min and64 max calls for64 admitted stamps. Retained record_property/xunit2
warning affects JUnit convention only; properties are present. Original
validator and fixture are preserved in source_fixture_before/. Receipt SHA256
b24592c2468824bc9b9bf3ffb8cc4ddb333e74a4d7f33ad321254d57b48fe7a8.

Root applied only two local min/max assignments within the existing simulation
nonempty-clock branch and substituted those bounds in the unchanged predicate.
Independent review precedes focused_v1 under120 s and relevant_v1 under240 s.
No retained recording validation or acquisition has started.

## Corrected source gates

Focused_v1 PASS10 in0.46 s pytest/1.070608062 s wrapper (120 s cap).
Relevant_v1 PASS161 in12.36 s pytest/13.124226782 s wrapper (240 s cap).
All171 cases are unique and pass on the same633 before/after source hashes;
21 actual installed console bindings match. The unchanged E2E exclusion filter
selected no deselected case in this bundle. No build or simulation was needed.
The focused JUnit retains the single record_property/xunit2 warning, with
clock_min_scans=1,clock_max_scans=1,admitted_typed_stamps=64 present.

Consolidated source_validation_v1.json SHA256
7e501c81b71b97b1a0dbc1c68f28a4a8ac60ba28a90f507b60c13edf33bbc994.
Production validator SHA256
4165c89d00adf62fc7f0b49ca7d00f40a5f3c94be0048756b83e3fad3ffb5414.
Exact release argv/environment and all receipts are retained in the external
build root; source wrappers use clean Humble->Q2->Q5 plus library path/domain189.
No runtime semantics, deadline, old experiment or physical source changed.

The reviewed retained-validation helper initially omitted the new test path
from its approved source-difference list. Before any execution, the exact
fifth path was added; old helper/drafts are retained under
retained_helper_before_allowlist_v1/. Corrected helper SHA256
3286bd4821b57af2a12b289d012bd3722f337e76be760792d70a9e06b3a60902.

Actual exclusive retained_validation_release_v1.json SHA256
e89b0dcbffdc3a505e80b7d8c3b6426f5f7542f56ea232a27255bcd3cfed004c
binds the final source gate, exact five differences against the V6 closure,
8 original files, existing48-check report, helper, clean argv and environment.
One retained validation is released under180 s after final actual-receipt
review; no field model, replay, acquisition or V7 identity route is admitted.

## Single retained validation: PASS

The only released retained_validation_v1 finished exit0. Existing validator
runtime49.042393395 s, inclusive diagnostic52.046186101 s/180 s; selected60 s
target PASS. Entire returned report equals the original completeness.json,
including all48 checks/details/counts/order/warnings/failures and finalPASS.
All8 original input hashes (including524685312-byte bag),633 source hashes,
helper and proof hashes match before/after. No original file was written.

Retained receipt SHA256
0ab9b5a69517c282b5a36981a97d3a2c3b070ce73a7236aa726878534d529a03,
under retained_validation_v1/receipt.json. The exact clean-shell/timeout argv
was read from the pinned release and executed once; no alternate validator,
field model, replay or simulation ran. The database log explicitly records
READ_ONLY. The worker used write_report=False, and its full returned report
is external retained_validation_v1/report.json.

This demonstrates unchanged validation output and practical selected runtime
for one retained recording. The earlier115.12 s interval included writes and
was not a controlled benchmark; do not infer a universal speedup or deadline
guarantee. V6 remains CLOSED_INCOMPLETE: one incomplete/15unstarted, no scenario
classification or science. Both original research targets remain unestablished.

Source milestone validation is CLOSED_PASS. Context/diff/checkpoint and the
reviewed material source archive precede a separate prospective V7 comparison
amendment. No V7 identity/preparation/acquisition has been admitted here.

Material source archive PASS: checkpoints/m4_v7_recording_clock_range_source_v1/manifest.json
SHA256 5befd6c9408e7aeda174cabc647e00e58a800643ad0f3bca5912fd03a2a0e1e7;393 files,63 externalrefs,1542140-byte verifiedtar.
Context/diff/checkpoint PASS. This live receipt postdates immutablearchive.
