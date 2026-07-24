You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_05_plan.md`
- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- every previous phase handoff.

Before editing, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 05 implement
```

The saved Phase 05 plan is the authoritative handoff from Plan mode. Verify its
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


# Phase 05 implementation: unified rosbag2 recording

Implement the approved recording architecture.

Requirements:
1. One recording entry point for simulation and physical modes.
2. Explicit required and optional topic manifest using actual audited topic names.
3. Preflight required-topic/type validation before motion.
4. Run metadata including Git state and resolved parameters.
5. Rosbag2 recording using currently installed ROS 2 Humble capabilities.
6. Console log capture.
7. Clean shutdown and final zero-command verification.
8. Run-completeness validator.
9. Short automated simulation recording test.
10. Documentation for starting/stopping and recovering a failed run.

Write:
- `docs/codex/gesc_gaussian/handoffs/phase_05_handoff.md`

Recommended commit message:
`phase 05: unify rosbag experiment recording`
