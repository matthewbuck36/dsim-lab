You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_03_plan.md`
- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- every previous phase handoff.

Before editing, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 03 implement
```

The saved Phase 03 plan is the authoritative handoff from Plan mode. Verify its
claims against the current repository and prior implementation handoffs before
editing. If the repository has changed or contradicts the plan, stop and
document the exact contradiction rather than silently replacing the plan.

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


# Phase 03 implementation: adaptive wider fills and fill merging

Implement `03_ROBUST_GAUSSIAN_ALGORITHM_SPEC.md`.

Requirements:
1. Refactor/extend the current Gaussian code rather than creating an unconnected duplicate.
2. Preserve the legacy fill path.
3. Implement the robust sample buffer, estimator, fill designer, validation, and registry.
4. Use numerically stable weight normalization.
5. Publish every fill parameter and diagnostic.
6. Merge overlapping candidates into one revised fill; do not double-count superseded fills.
7. Freeze published fill revisions and keep history for logging.
8. Add deterministic tests for all 13 required unit-test categories in the specification.
9. Add synthetic tests showing:
   - current/narrow behavior can leave a residual minimum,
   - robust design removes the fitted interior minimum,
   - amplitude scales when width increases.

Write:
- `docs/codex/gesc_gaussian/handoffs/phase_03_handoff.md`

Recommended commit message:
`phase 03: add adaptive basin fill design and merging`
