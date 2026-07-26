You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_02_plan.md`
- latest relevant dependency handoff(s), with older handoffs consulted on demand.

Before editing, initialize the live status, verify it against Git, and run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 02
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 02 implement
```

The saved Phase 02 plan is the authoritative implementation intent. Verify its
claims against the current repository and relevant handoffs, then triage
differences through Level A/B/C rather than stopping on every bounded drift.

Long-run continuity:
- Maintain `docs/codex/gesc_gaussian/status/phase_02_status.md` throughout execution.
- Record exact evidence continuously and run `checkpoint_phase.sh 02` at material or independently reviewable boundaries.
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
8. Keep changes coherent, reviewable, owner-aligned, and independently tested; split only at meaningful review/test boundaries.
9. Update documentation and parameter references.
10. Write the required phase handoff under `docs/codex/gesc_gaussian/handoffs/`.
11. End with Git status, tests, unresolved issues, and a recommended commit message.


# Phase 02 implementation: hybrid state machine and switchable components

Implement the state machine in `04_STATE_MACHINE_SPEC.md` using the exact audited repository architecture.

Requirements:
1. Add `legacy` and `robust_gaussian_v1` profiles.
2. Make raw cost, Gaussian, and affine weights explicit, published, parameterized, and testable.
3. Keep raw sensor acquisition active when raw-cost weight is zero.
4. Add source-score goal verification and dwell.
5. Add state timeouts and zero-command failsafe.
6. Use the current fill function behind a clear fill-designer interface until Phase 03.
7. Do not yet add recenter motion; provide the state/interface stub without unsafe command behavior.
8. Add transition unit tests and at least one launch/integration test.
9. Confirm legacy profile reproduces current behavior within test tolerance.

Write:
- `docs/codex/gesc_gaussian/handoffs/phase_02_handoff.md`

Recommended commit message:
`phase 02: add robust Gaussian supervisor state machine`
