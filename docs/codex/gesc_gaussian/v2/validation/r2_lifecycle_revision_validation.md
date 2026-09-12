# R2 lifecycle revision and static correction validation

SOURCE_VALIDATION_PASS, 2026-09-10. This is the current source boundary after
the [initial lifecycle tests](r2_lifecycle_validation.md), the adopted static
support correction in [the recurrent runtime plan](../r2_recurrent_detector_runtime_plan.md),
and [guidance publication revision](../r2_centered_guidance_revision_plan.md).
Earlier results remain retained at their original source boundaries.

The selected lifecycle validator now requires the new guidance schema2.
It indexes every full AlgorithmState revision by timestamp and the existing
canonical state hash. Monotone publication sequences distinguish legitimate
same-tick proposals, including invalid/zero DESIGN-before-PREPARE followed by
valid prepared guidance. An exact latest replay adds no authority; conflicting
sequence reuse and older rollback fail. Missing state hashes fail even for
invalid guidance, while the observed startup unbound stream contract remains
valid with zero commands. Existing candidate, pose, admission, VERIFY and
initial DESIGN expiry guards remain. The default12-second legacy lifecycle
and all old serialized message layouts remain unchanged.

The actual numerical recurrent fixture now uses the selected30-second static
support and its declared typed diagnostic. Only its15 affected cases were
rerun:15 passed,111 deselected,4.697 seconds, stable source. Evidence is
`centered_runtime_v1/lifecycle_validation_v1/focused_v4*` under the development
root below; the earlier12-second fixture/source result is retained separately.

The guidance correction selected58 relevant recording/analysis cases:
58 passed,77 deselected,17.774 seconds with stable scoped source. Cases cover
same-tick state and proposal revisions, exact replay, conflict/rollback,
preparation-pending zero, all prior timing/identity guards and the actual
recorder report/analyzer metadata route. The new interface overlay is
`centered_runtime_v2/environment.sh`; both jobs completed and were reaped under
the178-second bound. No new source-test failure occurred in this validator work.
The separate producer's original failing same-tick reproducer remains retained
by its owner.

Development root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/`.
Current validator evidence is `centered_runtime_v2/lifecycle_validation_v2/`:
`focused_v1_command.sh`, log/JUnit/receipt, actual `.before` copies with
`actual_preedit_v2.json`, and `validation_summary.json`. Summary SHA256:
`80f95a0d512eb71ac137a1ce1915bd34f1a142106c1c7ce42dc468af241b7e68`.
The full retained JUnit union contains206 distinct case names; this is not a
claim that every earlier test was rerun at the final source hash. Current
validator SHA256 is
`4a6abaeb4311e7940c42a640b83a75e586d93ac624c0fbc870638a0361af9676`.
`git diff --check` passes. Root owns final material checkpoint and visible
integration release; no empirical runtime acceptance follows from these tests.

The independent [four-arm labels benchmark](r2_labels_block_benchmark.md)
remains TIMEOUT and blocks comparison release. No unchanged retry is made.
