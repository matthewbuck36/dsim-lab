You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_10_plan.md`
- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`
- every previous phase handoff, including `phase_05_5_handoff.md`.

Before editing, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 10 implement
```

The saved Phase 10 plan is the authoritative handoff from Plan mode. Verify its
claims against the current repository and prior implementation handoffs before
editing. Apply the Level A/B/C policy in
`07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`; do not erase Level C failures or
claim unsupported acceptance.

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


# Phase 10 implementation: final documentation and cleanup

Implement the approved documentation plan.

Requirements:
1. Update the repository's real READMEs rather than adding disconnected notes only.
2. Include diagrams or Mermaid state/architecture figures where repository conventions permit.
3. Document exact commands verified in prior phases.
4. Document every robust-profile parameter.
5. Document raw versus augmented cost and all logged signals.
6. Document acceptance results and limitations honestly.
7. Remove stale Heavy-Ball experiment instructions from the active research workflow while preserving historical records when appropriate.
8. Verify all documentation links and commands.

Write:
- `docs/codex/gesc_gaussian/handoffs/phase_10_handoff.md`

Recommended commit message:
`phase 10: finalize GESC Gaussian documentation and reproducibility`
