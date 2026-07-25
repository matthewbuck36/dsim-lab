You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_00_plan.md`
- every previous phase handoff.

Before editing, initialize the live status, verify it against Git, and run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 00
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 00 implement
```

The saved Phase 00 plan is the authoritative handoff from Plan mode. Verify its
claims against the current repository before editing. If the repository has
changed or contradicts the plan, stop and document the exact contradiction
rather than silently replacing the plan.

Long-run continuity:
- Maintain `docs/codex/gesc_gaussian/status/phase_00_status.md` throughout execution.
- After each verified milestone, record exact evidence and run `checkpoint_phase.sh 00`.
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
8. Keep the change bounded. If it exceeds roughly 10 implementation files, split it into coherent subcommits and explain why.
9. Update documentation and parameter references.
10. Write the required phase handoff under `docs/codex/gesc_gaussian/handoffs/`.
11. End with Git status, tests, unresolved issues, and a recommended commit message.


# Phase 00 implementation: write the read-only audit artifacts

Do not change algorithm source code.

Inspect the repository and create:

- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/handoffs/phase_00_handoff.md`

The audit must include exact paths, node names, topic names, message types, launch files, parameter files, and test commands.

Run only read-only discovery commands and any safe build/list commands that do not command hardware. Record Git status. Do not modify generated build/install/log directories.

The handoff must state:
- what is already implemented,
- what is missing,
- the exact Phase 01 edit set,
- any assumptions from the package documents that the real repository disproves.
