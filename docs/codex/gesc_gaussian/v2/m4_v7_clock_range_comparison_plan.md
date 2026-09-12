# Prospective M4v7 comparison after recorder clock-range correction

Status: ADOPTED FOR SIMULATION IMPLEMENTATION,2026-09-10 UTC, after completed
clock-range source and selected retained-recording validation plus material
archive. The active user goal authorizes recommended bounded corrections.
This amendment admits implementation of fresh V7 routes; it does not itself
release preparation or acquisition. Both research goals remain open.

Verified prerequisite: clock-range source171PASS on633 stable pins/21bindings;
one write_report=False validation49.042393395 s, exact48-check report and8input
hashes unchanged, inclusive52.046186101 s/180 s. Retained receipt SHA256
0ab9b5a69517c282b5a36981a97d3a2c3b070ce73a7236aa726878534d529a03.
Material archive manifest SHA256
5befd6c9408e7aeda174cabc647e00e58a800643ad0f3bca5912fd03a2a0e1e7
(checkpoints/m4_v7_recording_clock_range_source_v1/,393files63refs1542140bytetar).
External draft remains unchanged at SHA256
5cf7577b387fa52203c55ac5107a39bb257e4c61d77e62efae26b4674c758546.

## Prerequisite and evidence boundary

Close docs/codex/gesc_gaussian/v2/m4_v7_recording_clock_range_plan.md first:
retain the expected scan-count baseline failure, successful corrected and
relevant source gates, stable installed/source bindings, and the single retained
V6 recording validation. That validation must use write_report=False, return an
entire report exactly equal to the original48-check completeness record, and
retain original input hashes unchanged. Its selected target is <=60 seconds;
180 seconds bounds the one job. If equality, safety, source integrity or the
selected time target is not met, retain the result and resolve its implications
in a separate saved scope before acquisition; do not repeat the job under this
comparison plan. The earlier115.12-second finalization interval includes writes
and is not a controlled benchmark.

Require the completed clock-range handoff, validation and material archive
manifest with exact hashes before implementing these version routes. Bind those
receipts, not an assumed success. Preserve the closed V6 contract
815b2e3c0c832f296320471af118e59ba8d189b555d978d45de342b13664b4e0 and closure archive
14fcd13e0c19c9b5aeab4f1cfd1708541463d5dca4b9ecd15d4015a82f011773. V6 remains
1 INCOMPLETE/15 UNSTARTED despite recorder48/48 and outer cleanup passing.
No replay, reclassification, replacement or resumed V6 dispatcher is permitted.

The only intended runtime change from the frozen V6 implementation is the
already qualified local clock min/max hoist inside validate_run_directory.
Every read, deserialization, completeness predicate and report field remains.
No nested deadline, process-owner, shutdown-grace or scientific-method change
belongs to this comparison.

## Exact unchanged comparison and fresh identity

Admit only experiment m4-pilot-v7, suite m4_pilot_v7, root
/home/mattb/Experiments/GESC-Gaussian/v2/pilot/m4_pilot_v7, case prefix m4_v7_,
and run IDs m4-pilot-v7-slotNN-ARM-SEED. Keep method_version m4-pilot-v1 and
process_ownership_mode subreaper_group_v3, its exact declared
initial_unreaped_root_group_sigint_then_adopted_pidfd strategy, all eight kernel
proof fields, performed cleanup and final-zero requirements unchanged.

Reuse the existing JSON, without copying or renaming it:
ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage_m4_v6_gain_half.json.
Its SHA256 is e94ea14af0ececd559902d950806ed2934e30099c61a2f867b76f8b1e88f0606.
Reuse profile_id m4_gain_half_control_v6 and v6_controller_configuration(); those
identify the unchanged configuration rather than the new experiment. Preserve
the original JSON hash3f255699385cc16d830fd79f560d91f1206321606b763be2971bdbc9bf6912a1.
All16 slots retain k_vx0.5, k_wz5.0, maximum vx0.1 m/s, maximum wz0.5 rad/s,
wheel radius0.033 m, wheel distance0.158 m and wheel speed70 RPM. B/D retain
centroid_invalid_status_heartbeat_enabled=True; A/C build no such override
(the existing validator may accept explicitFalse). Do not add a new profile,
JSON, controller policy, centering assist or field-truth control input.

A remains stationary/PDE; B stationary/two-block centroid; C moving/PDE;
D moving/two-block centroid. Keep W6 s, epsilon0.18 m, maximum radius0.5 m,
all dwell/source-gap guards, C/D moving_cycle_coherence_v1, candidate radius0.75 m,
epsilon0.15 m, three-cycle sector/information requirements and VERIFY12 s.
Keep all-arm interior-anchor fallbackTrue/minimum0.50 m, approach continuity,
disabled RECENTER, selected escape35 s with1 s exit hold and3 s/0.05 m progress.
The exact whole effective control map remains frozen, including inherited case
overrides; do not introduce other allowlisted overrides.

Both geometry stages retain stage_a_timeout_sec360, post_stage_a_timeout_sec300,
global_proximity_radius_m0.5, convergence_to_global_min_m0.75,
convergence_to_local_max_m0.6 and fill_to_convergence_max_m0.5. Keep verified_trap
association, original starts/bounds/maps/source strengths/cost sign and source
geometry chains. Fresh preparation derives four receipts through the unchanged
owner: primary nominal and secondary nominal/noise/delay. No model, topology,
label or reference redefinition.

The fixed slots remain development primary nominal A/B/C/D seed26090801;
holdout secondary nominal seed26090802, noise seed26090803, delay seed26090804,
each A/B/C/D. Noise stays0.015 and delays0.10 s. The first4 are visible; the
12 holdouts retain their saved visibility setting. All denominator rules remain:
16 reserved runs, six holdout pairs for the original30-percent latency target,
and192 direction targets,24 per C/D slot at15+30k seconds (k=0..23).

## Minimal owner changes and source acceptance

Retain exact affected source/test copies and V1-V6 pure generated scenario,
launch and metadata evidence in a fresh external build directory before edits.
Proposed implementation directory: builds/m4_v7_clock_range_comparison_v1.
Do not modify source-archived helpers or old evidence. Pure fixture capture has
a30-second cap; mock numerical owners rather than deriving fields.

1. m4_scenario.py: add V7 to the central allowlist and mode mapping; extend the
   existing V5 topology/interior and V6 controller/heartbeat/exact-control
   selections to V7. Retain old-version defaults, helper names and outputs.
2. m4_workflow.py: extend the same topology preparation, controller receipt and
   frozen source/profile/argv/metadata verification selections; pin the new
   adopted comparison amendment alongside the clock-range amendment.
3. run_scenario.py: add m4_pilot_v7 to its centroid-event selection and strict
   process-mode suite allowlists only. The general controller resolver and
   schema need no changes.
4. run_m4.py, evaluate_m4.py and m4_pilot.py already derive experiment versions
   from the central owner. Verify consumers with fixtures; change them only if
   an actual remaining explicit guard is demonstrated. Do not edit numerical
   reference, metric, recorder or detector owners for version routing.

Add focused V7 version/workflow tests using existing synthetic setups. Prove
all16 exact IDs, profile/JSON/heartbeat controls, primary/secondary receipts,
unchanged budgets and method identity; launch reconstruction and parameter-file
selection must agree before dispatch. Reject missing/wrong/cross-arm config,
extra controls, launch-only divergence, wrong method/mode/proof, and any V1-V6
root/slot/summary/analysis/release substitution. Preserve full192 target output
and withheld original-goal decisions for missing science. Require exact V6
configuration/stage/argv equivalence after explicit experiment/path substitutions,
and byte-for-byte unmodified V1-V6 generated outputs for their original inputs.

Six existing unsupported-future tokens require only preserved V7->V8 updates:
test_m4_v3_versions.py:211; test_m4_v4_versions.py:135,158;
test_m4_v5_versions.py:167,190; test_m4_v6_versions.py:147. Leave all other
assertions intact and add exact V8 rejection to new V7 tests.

After independent held-source review, run one focused bundle under180 seconds:
new V7 route/workflow tests plus retained V6 version/workflow tests for the
shared configuration route. Then one broader consumer bundle under240 seconds:
all other test_m4*.py modules (exclude already-passing whole modules from the
focused bundle) and test_q7_recording_selection.py; keep actual DDS/subreaper,
legacy recording and command-ownership fixtures, excluding only their explicitly
saved Gazebo E2E case if present. Freeze exact unique test selection before each
call. Reuse the completed clock-range recording regressions when their inputs
are unchanged; aggregate their exact receipts instead of rerunning passing
suites. Save failures; no cap increase, dropped failure or automatic retry.
A bounded, newly reviewed changed-source correction needs a fresh receipt label.

Use existing pytest/wrapper owners and a prospectively reserved clean simulation
ROS domain; no concurrent test or acquisition graph. The final source gate
aggregates current matching pins and exact outcomes, checks installed Q5 source
links/entrypoints, and runs actual run_scenario/record_run --help under one
60-second inclusive CLI cap. No rebuild follows solely from changed Python
context. Preserve clean Humble->Q2->Q5 environment, localhost1, DISPLAY:0 and
existing explicit clock overrides. Save domain/environment/argv before release.
Record context/diff verification, source handoff and material source archive.

## One preparation and one dispatcher

Copy reviewed external preparation/audit/archive/release helpers into the fresh
comparison build, preserving original helper/provenance and adopting exactV7
paths. Reuse finalizer, science hooks and report owners. Source archive must bind
current validated sources/tests/plans, both controller JSONs, installed ros2run
wrapper, exact helper bytes, completed clock-range receipts/archive and V6
closure chain. New frozen contract must bind all16 resolved scenarios/launch and
runner argv, exact controller receipt, four topology receipts, geometry receipts,
expected cost bytes, installed owner/environment and full source hash map.

After source closure: one preparation under600 seconds, one read-only frozen
audit under30 seconds, then a material prepared archive and exact dispatch
release. Verify no old root is reused and no new acquisition exists. Freeze the
new simulation domain and controller receipt across preparation/CLI/dispatch.
These maxima and required artifacts are unchanged from the V6 prerequisites.

Execute the single existing dispatcher once under15300 seconds inclusive.
Keep recording720 s, case900 s, shutdown45 s, cleanup reserve30 s, and existing
nested deadline accounting unchanged. Aggregate science stays900 s:
labels120 s/block, C/D references45 s/slot, summary10 s/block, freeze/report20 s;
maximum_observations40000. Every job remains finite and source/hash bound.

Initial release covers only4 development slots. After4 safe complete runs,
attempt and retain all planned development science outcomes, verify original
sources/configuration held and12 holdouts unstarted, then use the existing
one-time holdout release. Scientific failure or unavailable metrics are honest
outcomes; integrity failure closes V7. No tuning after freeze, replacement,
deadline extension or skipped integrity gate. Final reporting retains all16
slots and192 targets, separates recording/process integrity from behavior and
scientific availability, and evaluates both original research goals only from
their complete saved prerequisites. Completing this draft or source routing is
not evidence that either research goal has been met.

## Reserved environment

Reserve ROS_DOMAIN_ID=198,ROS_LOCALHOST_ONLY=1,DISPLAY=:0 for V7 source
checks, actual CLI, preparation and the prospective single dispatcher. The
previous terminal V6 used197; the completed clock-range fixture used189.
Use clean Humble->Q2->Q5 with extremum-seeking/src appended and existing
explicit simulation clocks. Verify no prior active graph before runtime.
This reservation is not an acquisition release.

## Adopted bounded source-validation correction after relevant_v1

The first fixed relevant_v1 is CLOSED_INCOMPLETE, never extended or restarted:
646 namedPASS/2 obsoleteV6-negativeFAIL, inner225 s cap,225.749386093 s wrapper.
All636 tested sources and wrapper are preserved in relevant_v1_source/manifest.json
SHA25627f8f468a0275deb84ddb6ea2b0d8d98263327e676c188dcd0b0c3a5cbd8c022.
The goal authorizes this Level B test/receipt correction; no algorithm,
recording, process-owner, scientific or experiment deadline change is adopted.

1. In test_m4_v2_subreaper_routes.py and test_m4_v3_shutdown_routes.py, replace
   only the one ('m4_pilot_v6',False) unsupported-future token by V8 per file.
   FrozenV6 already admittedV6. Retain every positivecase/assertion/runtime test.
2. The external source wrapper must label an unnamed/classless JUnit element
   unidentified, preserving it in the receipt and excluding it from passes.
   The failed run has one such placeholder; original rawreport remains unchanged.
3. After independent review, one fresh continuation_v1 under240 s runs exactly
   seven whole modules: test_m4_v2_subreaper_routes.py,
   test_m4_v3_shutdown_routes.py, test_m4_v6_centroid_heartbeat_transport.py,
   test_m4_v6_controller_selection.py, test_m4_workflow.py,
   test_m4a_execution_deadline.py and test_q7_recording_selection.py.
   These are the two changed modules and five modules without complete results.
   No passing module is rerun merely to recover context or produce a matching
   wholemap. No fixture waits, case assertions or original caps change.
4. One <=30 s pytest --collect-only inventory covers the original four focused
   plus23 broader modules, using the same E2E filter. Bind exact finalsource
   hashes, command and collected node IDs. Compose proof from focused620,
   unaffected namedcompleted broader passes and the corrected continuation.
   Require unique canonical IDs covering exactly the final inventory; no
   missing, duplicate-replacement, anonymous or failed row counts as a pass.
   Retain the two old failedV6 IDs outside the new finalinventory; their V8
   replacements must pass. Prefer fresh continuation evidence for its whole
   modules. This is composed source proof, not execution on one identical
   historical whole-source map: focused and unaffected broader production and
   fixture inputs remain byte-identical; only two other tests and this plan
   changed. Verify that exact difference at closure before using earlier proof.
5. Only after full coverage passes, the original one60 s actual CLI gate,
   source handoff/checkpoint/archive and600 s preparation/30 s frozenaudit
   prerequisites may proceed. All original16run/192target/science/holdout/
   recording720/case900/suite15300 limits remain untouched.

The timing choice uses retained evidence, not a weakened time predicate:
closed heartbeat selection+transport took108.430554233 s (not standalone
transport timing), with both current test hashes unchanged; the two route
modules just took22.082 s; controller/workflow/Q7 selection previously3.623 s.
The deadline tests have bounded3/2 s process envelopes and bounded cleanup.
A fresh240 s continuation has margin. In the failed run,218.983 s of namedcase
work against224.931 s suite explains exhaustion; no heartbeat case completed,
and no hang is established. Preserve any new failure before another amendment.
