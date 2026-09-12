# V6 matched gain source and comparison validation

Implementation in progress under the
[adopted amendment](../m4_v6_matched_gain_plan.md). The first focused source
bundle is closed with a fixture failure and timeout; no preparation or
acquisition has run.

The new JSON changes only k_vx from1.0 to0.5, identically for all16 slots.
Angular gain5.0 and speed ceilings0.1 m/s /0.5 rad/s remain unchanged. B/D
select the independently validated invalid-status heartbeat; numerical evidence
and scientific gates remain fixed. This is an untested engineering hypothesis.

## Retained first focused attempt and bounded correction

`focused_v1` terminated124 at its fixed inner165-second timeout: 335 PASS,
1 FAIL, pytest164.90 s; wrapper165.717996563 s within180 s. All631 source
pins remained unchanged. Its JUnit includes336 executed cases; the unexecuted
remainder is not counted as passing. The source/plan/helper snapshot is retained
exclusively under `builds/m4_v6_matched_gain_v1/focused_v1_source/`.

The observed failure is a fixture assumption: the existing `recorded_profile`
resource expands to two runs, while the new frontend fixture asserted one.
Correct the fixture to exercise both existing resolved cases. The timeout
interrupted YAML parsing. Review of the actual held source corrected the initial
diagnosis: V6 already caches its two templates within each validation call;
only its first primary-topology check rereads primary once. Reuse that existing
local snapshot there, preserving fresh hash checks on every new call and the
legacy path. This small source change alone is not expected to resolve timing.

The new mutation fixture rebuilds and expands the same sixteen-case YAML for
each test. Retained JUnit records roughly0.55-0.68 s per mutation case. Adopt
a fixture-only setup correction: create one immutable synthetic16-slot contract
per module with numerical owners still mocked, then give every test a fresh
deep copy and restore its expected PILOT_ROOT binding. Preserve every mutation,
arm, assertion and actual-schema population check. Never share mutable test
state or cache production validation results. No cases, gates or budgets change.

After preserving the tested source and independently reviewing these bounded
corrections, release one new `focused_v2 focused` attempt under the same180 s
cap and exact module selection. Retain the failed attempt; do not extend it,
discard cases or count the first partial pass as full source qualification.
Relevant and final integrated bundles remain pending.

## Pre-release frozen JSON ordering correction

Independent helper review identified a source blocker before focused_v2:
preparation constructs launch arguments in scenario YAML override order, while
atomic_exclusive_json sorts mapping keys in the saved contract. Rebuilding
arguments directly from that reloaded mapping can reject the unchanged command.
The existing prepared fixture already reloads this file, but focused_v1 timed
out before reaching it; this is a source-review finding, not a failed run.

For V6 only, reconstruct override order from the hash-verified original
scenario's frozen_profile followed by its case overrides, matching the existing
schema merge and retained frozen audit. Require exact value equality with the
validated resolved scenario before reconstructing; leave every other resolved
field unchanged. Keep exact whole-argv comparison, controller/metadata hashes,
all sixteen slots and earlier version paths. Explicitly verify sorted-JSON
roundtrip and reject command reordering or changed overrides in focused tests.
This correction joins the reviewed fixture changes in the same180 s focused_v2
attempt; no source or simulation budget changes.

## Prospective source commands

Finish all source edits and independent review before execution. Use one
clean Humble -> Q2 -> Q5 shell, with extremum-seeking/src appended, localhost
only and ROS_DOMAIN_ID189. No other ROS tests run concurrently. The following
wrapper is retained at
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_matched_gain_v1/root_source_validation.py`.
Each command records exact pytest argv, JUnit case identities, installed
entrypoint bindings and the complete current collect_sources before/after map.

| Label / wrapper group | Inclusive source cap | Selected modules |
| --- | ---: | --- |
| `focused_v1 focused` | 180 s | New V6 controller selection, versions and workflow |
| `relevant_v1 relevant` | 240 s | Existing M4 workflow and v2-v5 versions, scenario runner, Q7 launch/recording and heartbeat selection |
| `root_final_v1 integrated` | 520 s | M4 dispatch, pilot metrics, science jobs, evaluation CLI, objective inputs, centroid event evaluation; two existing controller motion/assist ownership cases |

Exact wrapper calls after environment setup:

```
timeout --signal=INT --kill-after=1s 184s /usr/bin/python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_matched_gain_v1/root_source_validation.py focused_v1 focused
timeout --signal=INT --kill-after=1s 244s /usr/bin/python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_matched_gain_v1/root_source_validation.py relevant_v1 relevant
timeout --signal=INT --kill-after=1s 524s /usr/bin/python3 /home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v6_matched_gain_v1/root_source_validation.py root_final_v1 integrated
```

Outer commands include five seconds for wrapper exit beyond the source cap.
The wrapper reserves15 seconds before that source cap for timeout/exit work.
Existing Gazebo E2E is excluded. Historical entrypoint-context tests retain
their older contexts; current installed bindings are checked directly through
installed_entry_points(expected_build=Q5_BUILD). Unchanged full moving fill DDS
and the old1500-test suite are not repeated solely to recover context.

All preliminary source fixtures use temporary synthetic resources and mock
topology/model owners; they cannot create real preparation or field evidence.
Retain failures and before-edit snapshots. Release no next command after a
failed or unstable source result until a bounded correction is recorded with a
new exclusive receipt. Do not replace passing cases or retry an old experiment.
Preparation and dispatch require their separate source/checkpoint/archive and
frozen integrity prerequisites after this source milestone closes.

## Corrected focused source outcome

focused_v2 terminal0:473 PASS in34.61 s; inclusive35.422159493 s/180 s.
All631 before/after source pins identical. Receipt SHA256 `c03208b9937b5e740ca467d9ad3227c8779d6890c7b37a86b5e57b8f9142f2bb`.
Both profile fixtures, preserved mutation population, fresh template checks and
actual sorted-JSON roundtrip/tamper checks pass. Earlier focused_v1 remains
CLOSED_FAILED_TIMEOUT. Relevant_v1 is released next under240 s after current
source pin verification. No preparation/acquisition released.

## Relevant legacy test identity correction

relevant_v1 terminal1:609 PASS,3 FAIL,1 existing Gazebo E2E deselected in82.97 s;
inclusive83.794273341 s/240 s,631 stable before/after pins. All three failures
are old unsupported-future-version fixtures in test_m4_v3_versions.py and
test_m4_v4_versions.py that still reject v6, now explicitly adopted. Preserve
the failed receipt/log/JUnit and four tested owner/test copies in
builds/m4_v6_matched_gain_v1/relevant_v1_source before edits.

Change only those future negative tokens from v6 to v7, keeping assertions,
case count and production byte-for-byte unchanged. Independently review the
exact diff, then run relevant_v2 under the same240 s cap and module population.
The473 focused_v2 passes remain valid for unchanged production and selected
focused modules; record the two unrelated legacy-test pin changes explicitly
in final validation rather than rerunning that passing bundle. The final
integrated bundle must capture the complete corrected current source map.
No preparation or acquisition released.

relevant_v2 terminal0:612 PASS,1 existing Gazebo E2E deselected in84.14 s;
inclusive84.989520806 s/240 s,631 stable pins. Receipt SHA256 `21725d5cd6059af69d961cf532eea8fe63858cc0f79f35959cf94113e692a7fb`.
Only the reviewed two legacy test files differ from focused_v2 pins. All
production/current selected focused tests remain identical. Root final
integrated_v1 is released under520 s, with no preparation/acquisition yet.

## Source milestone closure

CLOSED_SOURCE_VALIDATION_PASS:473+612+200=1285 unique passing identities.
Final root_final_v1 terminal0:200 PASS18.63 s, inclusive19.400547016 s/520 s;
receipt SHA256 ade9bce71514e2347c2620556001add44de6a8c7994b28602597d4750a4b4939.
Installed CLI receipt actual_entrypoints_v1.json PASS3.056497822 s/60 s,
SHA256 a29b71dc7b0f8a3132328ea20b13f7c91e7ed2f47a21d4e91f7d0efbda12fae9.
Exact full clean command is retained in actual_entrypoints_release_v1.json;
Humble/Q2/Q5, domain197 localhost1 DISPLAY:0 RMW unset matches preparation.
Both parser exits,21 callable/wrapper bindings and all631 sources are stable.
The three passing bundles total139.812227315 inclusive seconds.

Consolidated source_validation_v1.json SHA256
`a9c77458bc0ce028c9d106e7da8f25f3d4f7868cd90244e25ca55986ec84904a` records
all1285 unique JUnit identities and current final map. Focused predates only
three future-negative tokens in two legacy tests; shared imported helper bodies
and all production/selected focused tests are unchanged. Relevant revalidated
those corrections. This is a composed source result, not1285 cases in one run
on one identical complete source map. No empirical target has been established.
See m4_v6_matched_gain_handoff.md. Material source archive is next; no
preparation/acquisition has started at this entry.

## Material source archive and preparation release

Source context/diff/checkpoint/archive PASS: manifest
checkpoints/m4_v6_matched_gain_source_v1/manifest.json SHA256
468966710ea77787eec847b61c9fbd7d77de6fd55002e1a7fc8e9769cf25414d,
386 files,126 external references,1509008-byte verified tar. The source archive
helper ran once under60 s. Single preparation is RELEASED under600 s with the
exact reviewed command/environment from preparation_helpers_draft_v1.json.
Source and helper files stay held. No acquisition released.

## Single preparation and frozen audit outcomes

The single V6 preparation is terminal0 (root session70448), inclusive
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

## Prepared archive and exact dispatch release

Material prepared archive PASS: checkpoints/m4_v6_matched_gain_prepared_v1/manifest.json
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
