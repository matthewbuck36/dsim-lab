# Discovery direction diagnostic — 2026-09-09 UTC

Status: ACTIVE SOURCE/PREFLIGHT under the approved V2 implementation scope.
This explicitly selects a separate diagnostic after Q1's CLOSED
EVIDENCE_UNAVAILABLE result. No new Gazebo acquisition or pilot is released.
Read `plan.md`, `status.md`, `q1_handoff.md` and
`validation/q1_discovery_diagnosis.md` before editing.

Q1 and the completed discovery diagnostics are preserved at
`checkpoints/q1_closed_v1/manifest.json`, SHA256
`78659061686d43c75217ba1ade254ead9b0474cccbab681cc5c59e8741f6dd7b`:
212 task files,899224-byte verified archive,160 retained artifact hashes.
Its analyzer is the unchanged Q1 executor, SHA256
`072c239e6ba6041f2a0b753ec1e422fa9fbc400759f895413e276de32ac6a1c6`.

## Question and fixed population

Does the already implemented direction averaging improve the local stationary
GESC direction estimate on these two recorded discovery trajectories, and is
averaging actually available? The bounded orbit and high centroid scores do
not establish that direction error caused the behavior. Evaluate that question
before tuning either component or changing the positional-settling definition.

Version: `q1-discovery-direction-diagnostic-v1`. Exclusive external root:
`/home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_discovery_direction_diagnostic_v1/`.
Use exactly the already frozen24 targets in recovery4
`analysis/discovery_targets/targets.json`, SHA256
`b5d84cf2bb4f8900a940389ec16e5aa2608cbd76222907cdfeecb9a64cc4b1aa`:
seeds26090911/26090912, target numbers1–12, original T0+10k and50ms source
selection. Preserve missing/weak/fallback/rate-invalid slots; no replacements,
new targets, favorable subintervals or reopening of confirmation.

This is a separately declared24-target development diagnostic. The original
48-target Q1 qualification remains withheld because its nomination failed.
Do not change Q1's labels, targets, contracts, inputs, output or classification.
No detector/M3 evaluation, geometry recomputation, parameter sweep or controller
change is included. No diagnostic result can nominate settings or release M4.

## Existing analytical owner and explicit source lineage

Extend only the existing `evaluate_q1_direction_references` batch owner with an
explicit diagnostic-contract argument. The default call still requires both
partitions, all48 identities and a passing nomination before confirmation.
The diagnostic route requires exactly one unchanged discovery manifest and
the fixed24 identities. Share its existing target verification, numerical loop,
paired outputs and summary owner; do not copy a separate analysis pipeline.

Preserve every numerical owner/equation, selected model/filter/sensor geometry,
cost sign/objective reconstruction, measured signed world phase rate, twelve
sectors with two samples, rate CV0.10, quadrature/error bounds, informative
floor and output availability definition. Both aligned instantaneous and actual
recorded rolling outputs are compared at the same frozen anchors.

Changing the analyzer changes its source hash. Require a fresh diagnostic
contract binding the original Q1 contract, closed study, checkpoint and original
discovery targets/traces as immutable historical receipts, plus an exact
old/new analyzer transition and an original-source snapshot whose hash equals
the old receipt. Verify every old source file other than this one analyzer
normally; no old numerical/runtime/launch/configuration source may change.
Freeze current diagnostic source/test/workflow receipts too. New files are
limited to this diagnostic's tests and V2 workflow; no removed old source path.

Do not waive `_q1_contract` freshness globally, edit historical target manifests,
or pretend the new analyzer has its old digest. A separate strict diagnostic
verifier may construct an explicit effective validation contract using the
verified current analytical receipt and all unchanged old source receipts.
The unchanged `_q1_verify_run` then checks recorded acquisition bindings against
that explicit contract; analyzer lineage is separate from runtime equivalence.
Revalidate receipts before output, before model evaluation and after the job.

## Tests, freeze and finite execution

Cover default one-partition rejection and unchanged48 confirmation gates;
exact24 discovery-only acceptance with no confirmation reads; per-anchor parity
between default discovery portion and diagnostic for analytic/weak/fallback
fixtures; incorrect lineage, modified target/source/numerical owner, duplicate/
missing/extra identities or changed timing rejected before model construction;
and timeout/partial/exclusive output behavior with no false final result.
Run the existing focused numerical/source/reference regressions. These are
tests of a consequential scientific analysis boundary, not implementation-only
assertions. Record all failures and exact final commands.

Inspect the precise analyzer diff, freeze the new contract and sources, and
checkpoint before one numerical job under external timeout300s. A timeout or
unavailable numerical result remains an outcome; never rerun this fixed job.
Each processed anchor has its own immutable receipt. Final completion reports
`qualification_status: NOT_EVALUATED`, nomination null, confirmation SEALED,
pilot_released false, per-run/pooled denominators and both paired errors.
Use a diagnostic completion status, never Q1 or M4 PASS. No fresh simulation,
tuning or additional target is authorized by successful preflight.

Close with exact evidence and a bounded next decision. Any detector redesign,
direction tuning, revised independent operational label or fresh qualification
study requires a subsequent prospective amendment. Preserve the original
four-arm pilot population, conditions, caps and acceptance targets.
