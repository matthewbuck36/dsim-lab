You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_09_plan.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`
- the Phase 05.5 bridge/handoff, latest simulation-readiness handoff, and older handoffs only when a current claim depends on them.

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
- Record exact evidence continuously and run `checkpoint_phase.sh 09` at material, safety-critical, or independently reviewable boundaries.
- After compaction or interruption, reread the plan/status, inspect Git status and diff, and resume from the next incomplete criterion.
- Bound long commands and retain verbose logs by path rather than in chat.
- Do not repeat a recorded failed approach or restructure validated milestone work without failing-test evidence.

Rules:
1. Follow the repository's existing conventions exactly.
2. Reuse and modify current nodes/classes where practical.
3. Keep legacy behavior selectable.
4. Do not silently change cost sign, units, public topics, or physical/simulation semantics.
5. Offline/read-only adapter and safety preparation is allowed before the simulation-ready tag. Physical motion requires the tag, explicit user authorization, audited stop path, and readiness preflight.
6. Add focused tests for every new behavior.
7. Run the repository-standard format/lint/build/test commands relevant to changed packages.
8. Keep changes coherent, reviewable, owner-aligned, and independently tested; split only at meaningful review/test boundaries.
9. Update documentation and parameter references.
10. Write the required phase handoff under `docs/codex/gesc_gaussian/handoffs/`.
11. End with Git status, tests, unresolved issues, and a recommended commit message.
12. Report global baseline trend, focused/new tests, diff/syntax/import/style checks, exact skips/unexecuted tests, and final totals.


# Phase 09 implementation: physical integration and readiness workflow

Offline adapter, metadata, test, and safety/readiness implementation may
proceed without commanding hardware. Proceed with physical motion only when
the simulation-ready tag, explicit user approval, audited emergency-stop path,
and live readiness preflight all exist.

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
