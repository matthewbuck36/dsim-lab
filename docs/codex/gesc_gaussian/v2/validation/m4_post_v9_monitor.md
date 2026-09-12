# Post-V9 D2 monitor validation

Status: SOURCE_VALIDATION_PASS, 2026-09-10 UTC, simulation only.
Read the [adopted source plan](../m4_post_v9_monitor_plan.md).

Entry recovery verified AGENTS, current plans/status/handoff, Git status/diff and
the existing context validator. Branch remains feature/gesc-gaussian-robustness-v2
at3369cfc83a64ff5d8354827fd5310caaf0c8e945 with task work uncommitted. D1 archive
db9c3e1262eb176418fdabc573ce8e401b0da3613c9e4f3206e538c6446538e7 is present;
all645 prior source pins still match. The previous turn materially closed D1,
so it was progress. No old dispatcher or diagnostic job is resumed or repeated.

D2 implements the independently established live monitor correction before
the still unresolved startup transport correction. This preserves movement
toward the comparison while the exact recording mechanism is designed. Current
source drops completed Stage A when a later typed pair is incomplete, allowing
the old Stage A deadline to terminate Stage B early. Current final classification
also ignores the retained `staged_monitor_error` when final bag extraction passes.

Pre-edit runner SHA256:
0bf6914cb7d286e16a0b97d804cc2cb2487febadca25962abf7d4f6f4d061272.
Exact bytes and all645 source pins are preserved at external
`builds/m4_post_v9_monitor_v1/run_scenario_before.py` and
`source_before_v1.json`. The test author owns only the new focused module until
root has retained the failing baseline. No production edit or test has run yet.

Independent plan/source review agrees on separate historical timing proof versus
current strict evidence, including pending before the first Stage B odometry,
goal during pending evidence, malformed fill with evidenceNone, additional valid
cluster with cardinalityFalse, callback ordinals versus odometry seconds and
unchanged exact timeout/proximity precedence. These are required regression
cases, not reasons to loosen the matcher or hide later evidence.

## Prospective finite source jobs

Reuse the previous root source-validation owner, adapted externally as
`builds/m4_post_v9_monitor_v1/root_source_validation.py`. It uses the existing
`collect_sources` and installed entry-point validation, pins the new D2 plan,
retains each log/JUnit/receipt exclusively and checks source/bindings before/after.
Resolve clean Humble -> Q2 -> Q5 with domain201/localhost1 and bytecode disabled;
unset inherited Python/ament/colcon/library/RMW shell paths before setup.

| Job | Modules | Inclusive wall cap |
| --- | --- | --- |
| baseline_v1 | test_m4_monitor_progression.py on unchanged runner | 120 s |
| focused_v1 | new monitor module; test_m4_centroid_event_evaluation.py | 180 s |
| relevant_v1 | test_scenario_runner.py; test_m4a_execution_deadline.py | 240 s |

The deadline filename is singular, verified with `rg --files` before any job.
The inherited M4A module contains bounded local process/session lifecycle
fixtures; the scenario/monitor tests use existing mocked ROS/executor seams.
No Gazebo, daemon, actual ROS node, old bag read or simulation run is released.
The wrapper excludes the separately marked recorded short headless E2E if present;
any actual exclusion/skip is counted in the retained receipt rather than hidden.

Root wraps each sourced invocation in `timeout --signal=SIGINT --kill-after=2s`
with118/178/238 seconds respectively. The inherited inner pytest timeout reserves
15 seconds for termination/hash reporting; exact argv, environment, elapsed time,
unique cases and every exit outcome are retained externally. An unchanged failed
job is not retried. A demonstrated correction uses a fresh job/version and keeps
the prior evidence. Baseline failures must reproduce the stated monitor behavior;
collection/import errors do not count as a behavioral reproducer.

Full V2 and both original research goals remain open. D2 requires current-source
focused/relevant evidence, independent review and material checkpoint/archive.

## Baseline v1

The sole baseline command is terminal1/reaped:5 PASS/22 FAIL across27 identified
cases,4.013373132 s outer under120,2.067308636 s wrapper. All647 source/plan pins
and installed bindings are unchanged before/after. Exact command/output is
`builds/m4_post_v9_monitor_v1/baseline_v1_outer.json`; full log/JUnit/source
receipt and held test bytes are retained alongside it. Test SHA256
50306aa0f170ae268702d61e23f43c2e6dbce4a8fa29eb48998d56c07c1cb854.

Several failures reproduce premature termination with undelivered companions or
odometry, and both selected arms incorrectly retain passing terminal
classification despite a live error. Other failures occur in the new blanket
serialized-byte immutability assertion, including the otherwise valid exact
deadline case. These require fixture diagnosis; do not count all22 as independently
demonstrated production defects. Production source remains unchanged while the
fixture assertion is corrected. Preserve v1 and run a fresh bounded baseline_v2
on revised held tests before releasing the source edit.

## Corrected baseline v2 and source release

The v1 failure categories are5 serialized-byte assertions,15 premature callback
stops and2 incorrect terminal classifications. The aggregate byte assertion did
not identify padding versus semantic mutation, so no serializer fault is claimed.
The revised fixture checks full canonical message payloads with explicit
NaN/infinity tags, per-message identity diagnostics, unchanged public event
timestamp fields and a canonical decode of its single original CDR capture.
All27 behavioral cases are unchanged; v1 bytes remain retained externally.

Held v2 fixture SHA256:
fc488fd5ee07d3129a546445c50880b1b0e81985acad0334b0f87904687cf7b8.
The sole fresh baseline_v2 command is terminal1/reaped:6 PASS/21 FAIL,
4.081726023 s outer under120,2.115083687 s wrapper. There are no collection,
identity or immutability failures:19 schedules stop before their declared callback
boundary and2 terminal classifications incorrectly pass. Both source snapshots
contain the same647 pins and installed bindings remain stable. All old645 pins,
including runner0bf6914c...61272, remain unchanged. Exact argv/log/JUnit/receipts
and the revised fixture copy are under the same external D2 build root.

Root now releases the bounded production correction described in the D2 plan.
Only the existing selected monitor/classification owner and its focused tests
may change; full-history matching, old evidence and all experiment caps remain.

## Implemented correction and current validation

Only `_run_record_to_global_proximity` and `classify_result` changed in the
existing runner. The selected monitor deep-copies its first valid recovery
evidence for temporal progression and reports it as
`stage_a_completion_evidence_live`. Current stage/cardinality/error verdicts
still refresh from the full accumulated histories. A pending later pair cannot
restart Stage A or suspend the original Stage B timer; invalid current evidence
withholds new approach/closer/proximity acceptance.

Selected terminal live errors become `live_monitor_evidence_failed`, after the
existing extraction, recording and cleanup failure priorities. A current false
stage/cardinality verdict with retained completion also fails even when the final
bag facts pass and no error string exists. The actual extra-fill callback fixture
checks this final-classification discrepancy. Absent new completion evidence and
nonselected/legacy routes preserve their old behavior and result shape.

| Held final source | SHA256 |
| --- | --- |
| run_scenario.py | 92aa2b07c5d66e00fd6af54b7c6fed850265411836f33e4b706119fddbc4789c |
| test_m4_monitor_progression.py | 9194e8e3af51462872cbe515b38c3314bfcdf9f1c1c0b2c754a032e307a8d77f |
| monitor_correction_hold_v1.json | 2e3bfb8b678a00c7985d6953b6f155430014c18301f6fcf5af536c94b7e266ed |
| monitor_correction_v1.patch | af2b56b2e353e671c88ff9bfdf39ee50414c422d3515b8d93e05b6929a740406 |

The source author's AST comparison and independent review PASS: exactly the two
planned functions changed, strict matcher/publication bounds remain untouched,
and current evidence is never replaced by the historical timing snapshot. Two
initial author static commands used unavailable `python` and exited127 before
an interpreter ran; these are retained in the hold receipt. AST checks then
passed with `/usr/bin/python3`. No hidden agent test or runtime job occurred.

| Root job | Unique PASS | Outer elapsed / cap | Wrapper elapsed |
| --- | --- | --- | --- |
| focused_v1 | 57 | 4.178370166 / 180 s | 2.225954677 s |
| relevant_v1 | 224 | 31.767350547 / 240 s | 29.783664443 s |

All281 current-source cases pass, with no failure/error/skipped/unidentified
JUnit cases. Exact module totals:27 new monitor schedules,30 existing centroid
event tests,194 scenario-runner regressions and30 execution-deadline regressions.
One existing `test_scenario_runner.py::test_recorded_short_headless_end_to_end`
was explicitly deselected because no Gazebo acquisition belongs to D2.
Both jobs are terminal/reaped. All647 current source/plan pins and21 installed
entry-point bindings match before/after and across both jobs. Of the645 prior
pins, only run_scenario.py changes;644 remain identical. No generated interface,
build, physical source, detector/control tuning or retained run changes.

Aggregate exact evidence:
`builds/m4_post_v9_monitor_v1/source_validation_v1.json`, SHA256
0feb3a36cd69bd36ba0ce7b797b4d758f50ded6f24c967c06b6eda4d343bda78.
It binds the two final job receipts and281 unique results; earlier baseline
passes/failures are retained separately and excluded from that total. Each job's
outer receipt preserves the complete sourced shell argv, stdout/stderr and timing.

Context/diff/checkpoint and one material archive close this source milestone.
The reviewed archive helper SHA256 is
c1eed69bc244e3ada1667f3c5a37797b8b20df9e1d54e34d6da6ebd8ed527a79.
It requires the final aggregate and both passing job receipts before retaining
dirty source and all D2 artifacts plus D1/V9 references. Exact archive command:
`timeout --signal=SIGINT --kill-after=2s 58s python3
/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_post_v9_monitor_v1/archive_source_v1.py`
within60s inclusive. No bag is read and no simulation is released by this step.

Both original research goals remain empirically unproven. D2 repairs lost
observation time and evidence classification; it does not retroactively supply
the missing V9 Stage B exposure. Startup retention, daemon baseline discovery,
labels throughput and a fresh comparison/report remain outstanding.

## Material closeout

Context validator and diff check PASS. The existing `timeout 30s .../tools/
checkpoint_phase.sh v2` completed0.220877727 s; exact argv/output in
checkpoint_execution_v1.json. Independent final receipt audit verified all281
unique passing JUnit cases,647 current pins,21 installed bindings and their44
wrapper/module/metadata references, with all final source hashes unchanged.

The sole reviewed archive command is terminal0/reaped,1.143492353 s under60.
External checkpoint `checkpoints/m4_post_v9_monitor_source_v1/manifest.json`
SHA256 d5df2e6049b15ea99515426dfd17448f31260412ea161b5e55c7310c4f2ff814.
It retains428 repository files,35 external artifact references and1708498-byte
verified tar. Entry/exit source hashes, repository hashes, build inventory and
artifact signatures PASS. Exact archive_execution_v1.json retains command,
stdout/stderr/elapsed/returncode and postdates the immutable archive. D2 source
milestone is materially closed; all production source remains held until the
next saved amendment. No new simulation comparison or scientific result.
