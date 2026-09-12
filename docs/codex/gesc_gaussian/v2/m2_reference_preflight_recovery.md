# M2 reference preflight reader correction — 2026-09-09 UTC

The first Python invocation of the frozen reference study failed before output
creation, target freezing, replay or field evaluation. Preserve its source in
the M2 pre-reference snapshot and its command/log as recorded in
`validation/m2_reference_launcher_note.md`.

Read-only diagnosis found complete live robot-description captures in all
eight development inputs. Each `resolved_parameters.yaml` contains four
identical XML copies under node `parameters` plus the separate type label
`parameter_types.robot_description: string`. The generic `_find_parameter`
searched both trees, correctly reported an ambiguity between XML and the type
label, and returned None. The new M2 caller supplied the wrong search scope.
All 32 XML captures parse and match the required two joint geometries.

Authorize this bounded implementation correction within the approved plan:
the M2 caller searches only each node's `parameters` values. Preserve the
generic helper and its ambiguity semantics. Add a realistic regression with
both value and type trees; verify all eight binding preflights without field
evaluation. Do not remove live-capture, path/hash, geometry or conflict checks.

Before the first scientific execution, record the corrected source/test hashes
and a new material checkpoint. Use a separate launcher `m2_reference_command_v1b.sh`
and fresh output `m2_references_v1_recovery1/`. The original output namespace
remains absent and is never reused. The same fixed 192-anchor population,
reference protocol, numerical settings and one timeout300s calculation bound
apply. This repairs the reader without changing labels, denominators or gates.

Observed XML SHA256 groups (all four node captures agree within each run):

- Seeds19801/19811/19851:
  `037758dd657fe9f66f098d222557d86071a16376a9fb9953c41aafaa9a20417f`.
- Seeds19901/19911/19931:
  `8121b3cee804b0045e42568924e0cfe3766d0892f206cf69f7ccd1a0d7939c35`.
- Seeds20001/20031:
  `cbdf5e2e917fd0163dd7621f6d40f82c50db78b93a579571e33ffdcafdb60941`.

These are captured-data/parser findings, not direction-quality results.
