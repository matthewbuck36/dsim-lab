You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_07_plan.md`
- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`
- every previous phase handoff, including `phase_05_5_handoff.md`.

Before editing, initialize the live status, verify it against Git, and run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 07
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 07 implement
```

The saved Phase 07 plan is the authoritative handoff from Plan mode. Verify its
claims against the current repository and prior implementation handoffs before
editing. Apply the Level A/B/C policy in
`07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`; bounded corrections require
handoff evidence and failed data/acceptance gates require honest failure reports.

Long-run continuity:
- Maintain `docs/codex/gesc_gaussian/status/phase_07_status.md` throughout execution.
- After each verified milestone, record exact evidence and run `checkpoint_phase.sh 07`.
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
12. Report global baseline trend, focused/new tests, diff/syntax/import/style checks, exact skips/unexecuted tests, and final totals.


# Phase 07 implementation: standard bag analysis pipeline

Implement the approved analysis pipeline.

Requirements:
1. Read the actual bag backend used in Phase 05.
2. Map actual message types using the audit/interface map.
3. Synchronize with explicit tolerances and preserve original timestamps.
4. Export CSV by default.
5. Generate each required plot as a separate figure.
6. Calculate escape time, path length, radial progress, revisits, fill count, merge count, state durations, saturation time, and success/failure.
7. Mark incomplete data rather than silently interpolating critical missing topics.
8. Add a command that analyzes one run and another that summarizes a matrix.
9. Add tests with a small known bag or generated fixture.
10. Retain raw bags and analyze failed runs as first-class evidence.

Write:
- `docs/codex/gesc_gaussian/handoffs/phase_07_handoff.md`

Recommended commit message:
`phase 07: add rosbag analysis and standard diagnostics`
