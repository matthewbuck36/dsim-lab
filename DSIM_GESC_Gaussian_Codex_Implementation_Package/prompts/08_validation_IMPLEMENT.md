You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `AGENTS.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_08_plan.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`
- `docs/codex/gesc_gaussian/status/phase_08_status.md`
- `docs/codex/gesc_gaussian/handoffs/phase_08_1_handoff.md` when it exists
- the Phase 05.5 bridge/handoff, Phase 07/07.5 handoffs, and older handoffs only when a current claim depends on them.

Before editing, initialize or resume the live status, verify it against Git,
and run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 08
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 implement
```

The saved Phase 08 plan and any approved active amendment/subphase Plan are the
authoritative implementation intent. Verify their claims against the current
repository and relevant implementation handoffs before editing. Apply the
Level A/B/C policy in
`07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`. A missed acceptance gate is a
Level C result and must not be hidden by retuning the frozen final matrix.

Long-run continuity:
- Maintain `docs/codex/gesc_gaussian/status/phase_08_status.md` throughout execution.
- Record exact evidence continuously and run `checkpoint_phase.sh 08` at material, expensive empirical, or independently reviewable boundaries.
- After compaction or interruption, reread the plan/status, inspect Git status and diff, and resume from the next incomplete criterion.
- Bound long commands and retain verbose logs by path rather than in chat.
- Do not repeat a recorded failed approach or restructure validated milestone work without failing-test evidence.

Rules:
1. Follow the repository's existing conventions exactly.
2. Reuse and modify current nodes/classes where practical.
3. Keep legacy behavior selectable.
4. Do not silently change cost sign, units, public topics, or physical/simulation semantics.
5. Do not run physical hardware.
6. Add focused tests for every new behavior.
7. Run the repository-standard format/lint/build/test commands relevant to changed packages.
8. Keep changes coherent, reviewable, owner-aligned, and independently tested; split only at meaningful review/test boundaries.
9. Update documentation and parameter references.
10. Write the required phase handoff under `docs/codex/gesc_gaussian/handoffs/`.
11. End with Git status, tests, unresolved issues, and a recommended commit message.
12. Report global baseline trend, focused/new tests, diff/syntax/import/style checks, exact skips/unexecuted tests, and final totals.


# Phase 08 implementation: execute and document simulation validation

Do not change algorithm design after the v2 parameter freeze.

Tasks:
1. Run smoke and unit/integration tests.
2. Close and preserve the failed/incomplete Phase 08 v1 evidence; never resume
   or overwrite its 519-run matrix directories.
3. Treat the historical v2 activation as closed failed evidence. Diagnose it
   offline; never rerun, overwrite, relabel, or count it.
4. Under an approved Phase 08.1 Plan, correct bounded implementation,
   readiness, evidence, and scenario-contract defects with focused tests and
   minimal development-only simulation probes.

At the current repository checkpoint, Phase 08.1 ends with its M7 handoff.
Tasks 5-12 below are requirements for a separately planned and approved future
experiment version; this prompt does not authorize executing them directly.

5. For a future experiment version, prove diagnostic infrastructure and
   scenario-specific lifecycle reachability before formal freeze.
6. Run a separately declared bounded development/tuning design; development
   attempts never enter the acceptance denominator.
7. Select one parameter set using the declared metrics and freeze it in a clean
   commit.
8. Run new sealed holdouts only under one hashed machine-readable acceptance
   contract. Require the declared end-to-end, infrastructure, collision, and
   lifecycle gates.
9. Run the separately declared additional unique validation and
   reproducibility sets without post-freeze changes.
10. Generate a validation report with every amended acceptance gate, observed
   rates, and two-sided 95% Wilson score confidence intervals overall and by
   family.
11. If gates fail, do not tag simulation-ready. Write a failure report and the
    smallest justified next engineering phase.
12. If gates pass, create the simulation-ready tag recommended by repository
    conventions.

Write:
- `docs/codex/gesc_gaussian/validation/phase_08_v1_failure_closeout.md`
- `docs/codex/gesc_gaussian/handoffs/phase_08_handoff.md`
- `docs/codex/gesc_gaussian/handoffs/phase_08_1_handoff.md` for the bounded
  recovery closeout
- a validation report under `docs/codex/gesc_gaussian/validation/`

Use a result-specific commit message. Do not claim validation or freeze when
the executed stage failed or did not reach freeze.
