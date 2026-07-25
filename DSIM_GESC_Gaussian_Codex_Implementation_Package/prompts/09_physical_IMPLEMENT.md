You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_09_plan.md`
- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`
- every previous phase handoff, including `phase_05_5_handoff.md`.

Before editing, initialize the live status, verify it against Git, and run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 09
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 09 implement
```

The saved Phase 09 plan is the authoritative handoff from Plan mode. Verify its
claims against the current repository and prior implementation handoffs before
editing. Apply the Level A/B/C policy in
`07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`. Missing physical authorization,
safety prerequisites, or compatible adapters is a Level A stop.

Long-run continuity:
- Maintain `docs/codex/gesc_gaussian/status/phase_09_status.md` throughout execution.
- After each verified milestone, record exact evidence and run `checkpoint_phase.sh 09`.
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


# Phase 09 implementation: physical integration and readiness workflow

Proceed only when the simulation-ready tag and approval exist.

Implementation tasks:
1. Wire physical sensor/Vicon adapters to the same canonical topics.
2. Do not fork the algorithm.
3. Add physical preflight and readiness checks.
4. Add source-score calibration workflow.
5. Add low-speed physical parameter profile.
6. Add emergency-stop and zero-command verification.
7. Add complete recording workflow.
   Compose the existing Phase 05 `record_run` workflow, manifest, run format,
   readiness gate, and validator; do not create a second recorder.
8. Add operator-facing checklist and run notes.
9. Perform only the explicitly authorized staged tests.
10. Preserve every bag and metadata file.

Write:
- `docs/codex/gesc_gaussian/handoffs/phase_09_handoff.md`

Recommended commit message:
`phase 09: integrate physical light-source experiment workflow`
