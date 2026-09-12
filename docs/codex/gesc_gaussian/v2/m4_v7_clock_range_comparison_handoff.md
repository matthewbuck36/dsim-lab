# V7 comparison source handoff

Status: CLOSED_SOURCE_VALIDATION_PASS; material source archive pending.
Read [the adopted plan](m4_v7_clock_range_comparison_plan.md) and
[exact validation record](validation/m4_v7_clock_range_comparison.md).
No V7 preparation or acquisition has run. Both research goals remain open.

V7 uses the existing scenario, workflow, runner and analysis owners with fresh
experiment, suite, case and run identities. Its only intended runtime change
from V6 is the separately validated recording clock-range optimization. The
V6 controller JSON, profile, common translation gain, B/D heartbeat, detector
thresholds, moving evidence rules, topology, control limits and all experiment
budgets are unchanged. Earlier V1–V6 generated scenario YAML, launch arguments
and metadata remain byte-identical for their original inputs.

The original comparison is still four visible primary development runs,
followed only under the saved gates by twelve secondary holdout runs. All
sixteen outcomes and 192 direction targets must remain reportable. No failed
version can be resumed, substituted or reclassified; all retained runs remain.

## Source evidence

A pre-edit capture preserved six earlier populations and 96 launch/metadata
rows in 4.083 seconds under its 30-second cap. Independent reviews verified
three production owners contain only the required V7 selections. The existing
configuration identity remains m4_gain_half_control_v6, with the same JSON hash.

The source acceptance inventory contains 1,422 unique tests across the original
27 modules. Exact passing coverage is composed from:

- 620 focused tests: 62.50 seconds of pytest, 63.206 seconds in the wrapper.
- 608 unaffected named passes retained from the incomplete broader attempt.
- 194 continuation tests: 131.52 seconds of pytest, 132.336 seconds in the wrapper.

The first broader attempt remains failed and incomplete: 646 named passes,
two obsolete V6-negative fixture failures, and interruption at the fixed
225-second inner limit. Completed case durations account for 218.983 seconds;
there is no evidence of a hanging fixture. Its anonymous JUnit placeholder
was falsely counted by the old wrapper and is excluded from every pass total.
All tested source, wrapper, logs, JUnit and original receipts are preserved.

The correction changed one unsupported-future token to V8 in each of two test
files. It also made the external wrapper retain unidentified JUnit elements
and invalid inventory outcomes honestly. It changed no runtime source or test
wait. The continuation reran those two complete modules and the five modules
without complete results. The final collect-only job listed all 1,422 IDs in
1.63 seconds, and the union audit found no missing, extra or overlapping IDs.

This is composed evidence across recorded source maps. Current runtime and
focused fixture inputs are unchanged; the earlier complete maps differ only
at those two other test files and the appended correction plan. The exact
three-path difference is checked. Do not describe all tests as one execution
on one identical historical whole-source map.

Installed run_scenario and record_run help checks passed in 3.167 seconds
under the original 60-second cap. All 21 installed bindings and 636 current
source hashes remained stable. No ROS graph or acquisition was started.
The previous 171 recording checks retain their separate source milestone
and are not added to the current 1,422-test total.

## Retained paths and next action

External build root:
/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v7_clock_range_comparison_v1/.

- source_coverage_v1.json SHA256
  72c36168917e31c889539dd6717b6bb93b32f65a7c47ec9e217cc86666de2e9d.
- actual_entrypoints_v1.json SHA256
  65ae7a6249cc9550dc5e612ec5ca504fb0fd7d74816c5c67f0c3c040e8ba5372.
- relevant_v1_source/manifest.json SHA256
  27f8f468a0275deb84ddb6ea2b0d8d98263327e676c188dcd0b0c3a5cbd8c022.
- preparation_helpers_hold_v1.json SHA256
  9d98d80f6f6e0ae136375272350a3b320dbdb8378693b34d7adb21dbbc951782.

Finish the reviewed composed source receipt, context/diff/checkpoint and material
source archive. Then allow exactly one preparation under 600 seconds and one
frozen audit under 30 seconds, followed by a prepared archive and exact release.
The existing dispatcher owns all sixteen slots and the one-time holdout gate.
Reserve domain 198, localhost only, DISPLAY=:0, with clean Humble→Q2→Q5 and the
existing library path. Preserve every recording, case, suite and science limit.

Git remains feature/gesc-gaussian-robustness-v2 at
3369cfc83a64ff5d8354827fd5310caaf0c8e945. All task changes are saved uncommitted;
no commit, push, V1, physical snapshot, Pi or hardware action occurred.

## Composed source closure

Composed source validation PASS, 2026-09-10 UTC: 1,422 unique tests across
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

## Source archive and preparation boundary

Material V7 source archive PASS: `checkpoints/m4_v7_clock_range_comparison_source_v1/manifest.json`
under the external V2 root, SHA256
`3ad6855d44397c485845e4d47bfa62e6b39867524d631a915df72221ae17b08c`;
398 repository files, 756 external references, 1,564,211-byte verified tar.
Context validation, diff check and checkpoint PASS. Actual composition receipt
and five preparation helpers independently match existing consumer contracts.
The single reviewed 600-second V7 preparation is now released; read its
exclusive receipt/log before recovery and never duplicate it. Source/helpers
held. Frozen audit and acquisition remain dependent on preparation PASS.

## Frozen preparation outcome

V7 preparation PASS in 52.617003256 seconds under600; independent frozen
audit PASS in4.324617603 seconds under30. Both processes terminal; no repeat.
Contract SHA256 `12865711f2f7e5cd1c7527dd84220333a44e5a8875489e09796caedf71dc7a7a`;
preparation receipt `2e5edc08e61522d55753ac188d45539fe23d2a9d347928a159ebac4f1824d3c6`;
frozen audit `a3197497a2411cf4a9fe812efb553ccaa1fadffe775f438e7d92aa6eb4024a76`.
Exact16 slots,192 direction targets, four topology receipts, V6 controller
selection, domain198,21 installed bindings and636 source hashes verified.
Prepared material archive and exact dispatch release follow; acquisition has
not started. All source and helpers remain held; both research goals open.

## Prepared archive and acquisition release

V7 prepared archive PASS: manifest SHA256
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
