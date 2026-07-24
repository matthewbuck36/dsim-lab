You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_04_plan.md`
- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- every previous phase handoff.

Before editing, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 04 implement
```

The saved Phase 04 plan is the authoritative handoff from Plan mode. Verify its
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


# Phase 04 implementation: measured escape and bounded recentering

Implement the approved Phase 04 plan.

Requirements:
1. Use pure repulsion first.
2. Track and publish radial distance, radial progress, stall status, and frozen escape geometry.
3. On stall, request one fill escalation/redesign, then activate assisted escape.
4. Select assisted direction safely using room bounds, active fills, and approach history.
5. Add recentering for bounded indoor mode.
6. Keep prior fills active while recentering.
7. Publish pre- and post-saturation commands.
8. Enforce zero command on stale pose, invalid data, timeout, and shutdown.
9. Add Gazebo/synthetic tests for:
   - pure escape,
   - stalled escape,
   - assisted escape,
   - wall rejection,
   - recenter completion,
   - timeout/failsafe.

Write:
- `docs/codex/gesc_gaussian/handoffs/phase_04_handoff.md`

Recommended commit message:
`phase 04: add escape progress and indoor recentering`
