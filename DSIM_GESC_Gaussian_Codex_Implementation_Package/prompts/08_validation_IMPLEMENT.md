You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_08_plan.md`
- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`
- every previous phase handoff, including `phase_05_5_handoff.md`.

Before editing, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 implement
```

The saved Phase 08 plan is the authoritative handoff from Plan mode. Verify its
claims against the current repository and prior implementation handoffs before
editing. Apply the Level A/B/C policy in
`07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`. A missed acceptance gate is a
Level C result and must not be hidden by retuning the frozen final matrix.

Rules:
1. Follow the repository's existing conventions exactly.
2. Reuse and modify current nodes/classes where practical.
3. Keep legacy behavior selectable.
4. Do not silently change cost sign, units, public topics, or physical/simulation semantics.
5. Do not run physical hardware.
6. Add focused tests for every new behavior.
7. Run the repository-standard format/lint/build/test commands relevant to changed packages.
8. Keep the change bounded. If it exceeds roughly 10 implementation files, split it into coherent subcommits and explain why.
9. Update documentation and parameter references.
10. Write the required phase handoff under `docs/codex/gesc_gaussian/handoffs/`.
11. End with Git status, tests, unresolved issues, and a recommended commit message.
12. Report global baseline trend, focused/new tests, diff/syntax/import/style checks, exact skips/unexecuted tests, and final totals.


# Phase 08 implementation: execute and document simulation validation

Do not change algorithm design while running the final matrix.

Tasks:
1. Run smoke and unit/integration tests.
2. Perform a bounded parameter sweep on training scenarios.
3. Select one parameter set using the declared metrics.
4. Freeze it.
5. Run holdout scenarios.
6. Run the required full matrix.
7. Run three consecutive full-suite passes with no code/parameter changes.
8. Generate a validation report with acceptance-gate calculations.
9. If gates fail, do not tag simulation-ready. Write a failure report and the smallest justified next engineering phase.
10. If gates pass, create the simulation-ready tag recommended by repository conventions.

Write:
- `docs/codex/gesc_gaussian/handoffs/phase_08_handoff.md`
- a validation report under `docs/codex/gesc_gaussian/validation/`

Recommended commit message:
`phase 08: validate and freeze robust Gaussian profile`
