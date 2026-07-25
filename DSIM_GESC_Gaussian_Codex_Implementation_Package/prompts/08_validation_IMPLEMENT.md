You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `AGENTS.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_08_plan.md`
- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`
- `docs/codex/gesc_gaussian/status/phase_08_status.md`
- every previous phase handoff, including `phase_05_5_handoff.md`.

Before editing, initialize or resume the live status, verify it against Git,
and run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 08
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 implement
```

The saved Phase 08 plan is the authoritative handoff from Plan mode. Verify its
claims against the current repository and prior implementation handoffs before
editing. Apply the Level A/B/C policy in
`07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`. A missed acceptance gate is a
Level C result and must not be hidden by retuning the frozen final matrix.

Long-run continuity:
- Maintain `docs/codex/gesc_gaussian/status/phase_08_status.md` throughout execution.
- After each verified milestone, record exact evidence and run `checkpoint_phase.sh 08`.
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


# Phase 08 implementation: execute and document simulation validation

Do not change algorithm design after the v2 parameter freeze.

Tasks:
1. Run smoke and unit/integration tests.
2. Close and preserve the failed/incomplete Phase 08 v1 evidence; never resume
   or overwrite its 519-run matrix directories.
3. Prove the ten-run activation gate, including real detector-to-supervisor
   transitions and rotation-aware goal verification. Stop on any missing
   required state/event.
4. Run three predeclared candidates on the same ten training cases: 30 runs.
5. Select one parameter set using the declared metrics and freeze it in a clean
   commit.
6. Run 20 new hidden holdouts. Require at least 18/20 end-to-end successes plus
   complete infrastructure, valid collision evidence, and required lifecycle
   coverage. Stop if this gate fails.
7. Run 50 additional unique stratified validation cases. Combine them with
   holdout for the 70-run acceptance denominator.
8. Run ten predeclared fixed-profile reproducibility repeats.
9. Generate a validation report with every amended acceptance gate, observed
   rates, and two-sided 95% Wilson score confidence intervals overall and by
   family.
10. If gates fail, do not tag simulation-ready. Write a failure report and the
    smallest justified next engineering phase.
11. If gates pass, create the simulation-ready tag recommended by repository
    conventions.

Write:
- `docs/codex/gesc_gaussian/validation/phase_08_v1_failure_closeout.md`
- `docs/codex/gesc_gaussian/handoffs/phase_08_handoff.md`
- a validation report under `docs/codex/gesc_gaussian/validation/`

Recommended commit message:
`phase 08: validate and freeze robust Gaussian profile`
