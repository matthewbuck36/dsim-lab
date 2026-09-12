# Stationary typed-event causality correction handoff

Status: CLOSED_SOURCE_AND_SELECTED_RECORDING_VALIDATION_PASS, 2026-09-10 UTC.
Full V2 remains IN_PROGRESS. Read [the source amendment](m4_v8_stationary_causality_plan.md)
and [exact validation](validation/m4_v8_stationary_causality.md).

The existing recording validator now uses its already-validated stationary
typed request authority for both centroid detector modes. Moving lifecycle
authority retains precedence; unselected legacy behavior retains its exact
request matching. Selected malformed or unavailable authority fails closed.
The typed checker, producers, numerical controls, clocks, report schema and
deadlines are unchanged. Only validate_run_directory changed in the validator;
the workflow owner also pins the new source amendment for provenance.

The new 25-case baseline reproduced exactly 18 expected routing failures and
7 passes on the old validator. After the correction, 115 focused and 210
relevant tests pass: 325 unique cases across 10 modules, with 638 stable source
hashes and 21 installed bindings. Actual installed run_scenario and record_run
help commands pass. Relevant coverage includes actual stationary DDS traffic,
legacy and moving recording contracts, both centroid selectors and the retained
one-minimum/one-maximum clock-scan regression. One inherited xunit2 property
warning remains; no case is unidentified, skipped or failed. Historical V7
passes and expected baseline failures are excluded from the new source total.

One write_report=False call on the retained V7 B recording passed all 52 checks.
Only algorithm_event_source_causality and consequent top-level passed/failures
changed in the newly returned copy. Every other report field is exactly equal.
The validator took 30.570818027 s; the whole job took 32.909106865 s under the
original 180 s cap. All 11 original inputs, 638 source files and helper/proof
hashes remained unchanged before/after. Root session 51079 is terminal, exit 0.
This is one selected recording verification, not a general runtime guarantee.

External build root:
/home/mattb/Experiments/GESC-Gaussian/v2/builds/m4_v8_stationary_causality_v1/.

- source_validation_v1.json SHA256
  80eca1b9ee666812130d4c0fec1a76a8648a2fe3a23c309cb36f118d1e3461d5.
- actual_entrypoints_v1.json SHA256
  8bbea7b7e2c639e31a63a21cf9701ae0ecbeb4044864c0c744c5bac9ce139bdc.
- retained_validation_release_v1.json SHA256
  75a6ae46d9b070effb7ad9c902d611ac3c62653a6396fb6e1d77deca2d393c1c.
- retained_validation_v1/receipt.json SHA256
  22d0f6f9ddbac978401c69349b5c3c6c772203e5da8f4d7d045f5dd8ad467314.
- retained_validation_v1/report.json SHA256
  15cd7ec5e950820ebf9bcc8c1755686f84fdc73e5f910a0b305a238cb343d9d5.

Final validator SHA256:
73f897af6460d7ce77512ce27651acaf68237e596c689b85ddfe2ee9234a8ebd.
The exact four-path source difference from V7 is recorded in the aggregate:
validator, provenance workflow pin, new fixture and source amendment. Preserved
source copies, exact command releases, failed baseline, JUnit, logs and the
corrected pre-execution composer draft remain external evidence.

V7 remains CLOSED_INCOMPLETE with 1 COMPLETE / 1 INCOMPLETE / 14 UNSTARTED,
no science or holdout release. Its original reports and recordings remain
unchanged. Both V7 trajectories hit the 360 s Stage A limit without completed
escape-to-SEARCH recovery; correcting recording validation proves neither
behavioral acceptance nor the two research improvements.

After context, diff, checkpoint and material archive, separately adopt the
prospective next_comparison_plan_draft_v1.md from this build. It proposes fresh
V8 identity routing through the existing owners, preserving all controls,
16 slots, 192 direction targets, deadlines and one-time holdout gates. No V8
experiment identity, preparation or acquisition is admitted by this source
milestone. Do not repeat any completed test, retained verification or old pilot
to recover context. Source remains held until the next saved amendment.

Git: feature/gesc-gaussian-robustness-v2 at
3369cfc83a64ff5d8354827fd5310caaf0c8e945. Task work is saved uncommitted.
No commit, push, V1, physical snapshot, Pi or hardware action occurred.

## Material archive and next boundary

Stationary causality source milestone and material archive are CLOSED PASS.
Context, diff and repository checkpoint passed. The sole reviewed 60 s archive
command completed in 0.725930041 s, exit 0, producing
checkpoints/m4_v8_stationary_causality_source_v1/manifest.json under the
external V2 root, SHA256
6d35c50356baa29201d77b019a1d521a4d0e32f1147ceff5aa8c373c7752f476:
404 repository files, 109 external references, 1,586,594-byte verified tar.
Original bag references are inherited from completed verification/closure;
the archive helper does not reopen those bags. Exact closeout commands and
outcomes are in this build's closeout_checks_v1.json; archive command/log are
in builds/m4_v8_stationary_causality_archive_execution_v1.json and
builds/m4_v8_stationary_causality_archive_v1.log. This live receipt postdates
the immutable archive; no source changed after validation.

Next incomplete criterion: separately adopt the reviewed prospective
builds/m4_v8_stationary_causality_v1/next_comparison_plan_draft_v1.md
(SHA256 a4787bdc645992ae700b24de3f7020479d85364ab572b6d05d2e31de71502de3).
It retains all controls, 16 slots, 192 targets and gates. Its read-only routing
sanity review passed: three production owners, nine unsupported-future test
tokens in seven existing modules. Do not create another source-validation or
retained-recording attempt. No V8 identity/preparation/acquisition is admitted
until the next plan is adopted and its prerequisites pass. No source, test or
simulation process is live. Both original research goals remain unproven.
