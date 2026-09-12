# M4v10 scenario and dispatch source implementation

SOURCE_VALIDATED, 2026-09-10. Authority is the adopted
[M4v10 arrival comparison plan](../m4_v10_arrival_comparison_plan.md).
The parent's coordinated source validation is complete as recorded below.
This owner has not prepared, acquired or analyzed a comparison or run a numerical
model. Preparation and acquisition remain separate, subsequently released work.

`m4_scenario.py` now declares experiment `m4-pilot-v10`, suite `m4_pilot_v10`,
method `recurrent_arrival_v10`, and required top-level release selector
`usable_four_arm_analysis_v1`. Shared `experiment_method_version(version)` and
`experiment_execution_budgets(version)` supply exact values to workflow and
dispatch owners. Budget keys use existing contract names. V10 labels240s and
science1400s produce the15800s total; references45s, summary10s, freeze/report40s,
case900s, recorder720s, cleanup30s and shutdown45s remain fixed. Old versions
retain their original method identity and caps.

The population has four primary nominal development slots at seed26091011 and
twelve secondary confirmation slots at nominal26091012, noise26091013 and
delay26091014. Internal holdout partition spelling remains for compatibility;
new metadata calls these confirmation cases on exposed conditions. The new
version preserves matched V6 half-gain, topology, source/start/disturbance,
controller, Gaussian and escape selections. Existing360s local-recovery and300s
post-recovery stages remain. The short integration probes'180/120s stages are
not copied into this comparison.

Arms A/B use stationary acquisition with PDE/recurrent respectively. C/D use
the same rolling, moving-cycle-coherence and centered-verification package with
PDE/recurrent respectively. Recurrent diagnostics and B's distinct stationary
request topic are explicit. Old centroid-invalid heartbeat isFalse; recurrent
mandatory status behavior remains intrinsic. No artificial centroid W/epsilon
override or numerical detector change is introduced. Arrival selection removes
the required second ranking/GOAL_HOLD sequence, retaining local fill, owned
escape, SEARCH handoff, actual0.5m arrival and all original safety predicates.

`scenario_schema.py` admits this exact named schema14 suite for development and
internally named holdout partitions, retaining the existing standalone method
development scope and all old arrival restrictions. `run_scenario.py` selects
the same typed recurrent event/history-end/origin path and strict process-group
owner, with the proven shared-daemon baseline for V10. Legacy selection branches
are unchanged. `run_m4.py` uses version-bound execution/science reservations in
validation, elapsed admission, initial deadline and final inclusive check. Its
case/cleanup ownership remains the existing implementation.

Focused new tests are in `test_m4_v10_versions.py`: fixed identities and all
sixteen selections, schema expansion without model evaluation, nominal/delayed
actual Humble frontend routes, matched C/D package, arrival and budget mutation
rejections, exact retained V9 scenario bytes, strict owner selection and actual
dispatcher initial15800s reservation stopped deliberately before any runtime.
Existing V9 and earlier parity fixtures are retained unchanged. Nine existing
test modules used V10 as an unsupported future sentinel; only that sentinel is
advanced to V11 because V10 is now explicitly adopted. No earlier version's
accepted outputs or frozen evidence is changed.

Requested coordinated regressions: new V10 module; existing
`test_m4_v9_versions.py`, `test_m4_v9_budget.py`,
`test_recurrent_recording_selection.py`, `test_r3_arrival_evaluator.py`, and
`test_r4_stationary_recurrent_runner.py`, plus the other owners' focused V10
workflow/science modules. Older version sentinel regressions can be selected by
their allowlist/evaluator-route tests without rerunning finite process campaigns.
These are source fixtures, not comparison preparation or scientific qualification.

Current AGENTS, plan/status and R4 handoff were read. The existing implement
context validator passed under28+2s. Scoped diff review/check and AST syntax
parsing are the only checks by this owner before coordinated testing. Exact
implemented source/test pins are retained externally in
`development/20260910/m4_v10_source_v1/detector_source_ready_v1.json`.
Root owns final validation, source archive, preparation and release.

Before the first coordinated test, the parent saved a prospective budget
amendment: freeze/report40s gives20s each for development release and final
report, science1400s and suite15800s. This follows the retained V9 release
measurement4.065685725s plus V10's second full source/input verification and
nested hashes. The helper, exact contract validator, budget/rejection assertions
and this note adopt it only for V10. Old versions retain20/900/15300s. The
original implemented-but-untested source pins remain retained; amended pins are
`detector_source_ready_v2.json` in the same external source-validation directory.

## First coordinated source result and fixture correction

The parent's retained `focused_v1` bundle completed607passed/one failed out of608
in129.36s pytest /131.639977s inclusive wall. All selected source and21 installed
entry-point bindings stayed stable. The sole failure was the new exact V9 YAML
parity assertion, first differing at byte6616: the JSON topology fixture sorts
mapping keys (starting `basin_center_separation_m`), while original model-to-YAML
serialization starts `schema_version`. Read-only comparison confirms all four
topology mappings are semantically identical. The archived pre-V10 builder
deep-copies the supplied records without reordering, so the mismatch is in the
new test input ordering rather than an old-version production change.

The bounded correction now takes topology mappings from the original V9 scenario
after verifying its frozen contract hash and case identities. It separately
asserts equality with the existing JSON fixture, then retains the original exact
`yaml.safe_dump(..., sort_keys=False).encode() == retained_bytes` assertion.
No production code, original YAML, baseline fixture, model or bag changed.
`focused_v1` remains failed and retained. At that checkpoint the corrected test
awaited the parent's next bounded validation release, recorded below.

## Corrected validation and source closeout

Root released and completed only the affected module in `focused_v2`:
32/32passed in7.71s pytest /9.894771s inclusive wall. The original V9 byte-parity
assertion now passes with the original input key order. Source and all21
installed entry-point bindings stayed stable; production code was unchanged
between the original bundle and corrected module. Exact result:
`development/20260910/m4_v10_source_v1/focused_v2/source_validation.json`.

The first `focused_v1` remains607passed/one failed out of608, with its failure
log and source pins retained. `source_validation_combined.json` records the
union by test identity: **608 unique cases pass** after the corrected module.
The32 rerun cases overlap the first bundle and are not added to607 as separate
coverage. No unchanged numerical or acquisition job was rerun.

Five actual installed CLI help commands also pass in5.850403s, confirming the
selected environment reaches the existing entry points without acquisition.
This source milestone is validated; root owns the final checkpoint/archive and
prospective comparison preparation. All production and test files remain held,
and this documentation is complete before the material archive.
