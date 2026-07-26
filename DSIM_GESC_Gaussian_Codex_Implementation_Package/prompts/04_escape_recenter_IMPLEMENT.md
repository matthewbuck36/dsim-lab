You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_04_plan.md`
- latest relevant dependency handoff(s), with older handoffs consulted on demand.

Before editing, initialize the live status, verify it against Git, and run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 04
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 04 implement
```

The saved Phase 04 plan is the authoritative implementation intent. Verify its
claims against the current repository and relevant handoffs, then triage
differences through Level A/B/C rather than stopping on every bounded drift.

Long-run continuity:
- Maintain `docs/codex/gesc_gaussian/status/phase_04_status.md` throughout execution.
- Record exact evidence continuously and run `checkpoint_phase.sh 04` at material or independently reviewable boundaries.
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
