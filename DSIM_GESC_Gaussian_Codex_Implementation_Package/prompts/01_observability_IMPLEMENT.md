You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_01_plan.md`
- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- every previous phase handoff.

Before editing, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 01 implement
```

The saved Phase 01 plan is the authoritative handoff from Plan mode. Verify its
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


# Phase 01 implementation: common observability and data interfaces

Implement the approved Phase 01 plan.

Requirements:
1. Preserve current controller behavior.
2. Publish raw sensor, raw cost, source score, Gaussian contribution, affine contribution, augmented cost, weights, state/mode, Gaussian parameters, commands before/after saturation, and events using the repository's conventions.
3. If a value does not yet exist, publish a valid placeholder/status field only when the message explicitly marks it unavailable. Do not invent numerical data.
4. Ensure the same logical topics can be populated in Gazebo and physical modes.
5. Add timestamp and validity handling.
6. Add structured state/event publication in addition to console logs.
7. Add tests that instantiate or exercise publishers without physical hardware.
8. Document the resolved topic/message dictionary.

Write:
- `docs/codex/gesc_gaussian/handoffs/phase_01_handoff.md`

Recommended commit message:
`phase 01: add common GESC Gaussian observability interfaces`
