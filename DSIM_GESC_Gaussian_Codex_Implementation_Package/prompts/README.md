# Prompt Sequence

Use each pair in numeric order. Start a new Codex chat for every table cell.
After each Plan chat, save its final self-contained response at the listed path
before starting the Implement chat.

| Phase | Plan chat | Saved Plan artifact | Implement chat |
|---|---|---|---|
| 00 | `00_repo_audit_PLAN.md` | `docs/codex/gesc_gaussian/plans/phase_00_plan.md` | `00_repo_audit_IMPLEMENT.md` |
| 01 | `01_observability_PLAN.md` | `docs/codex/gesc_gaussian/plans/phase_01_plan.md` | `01_observability_IMPLEMENT.md` |
| 02 | `02_state_machine_PLAN.md` | `docs/codex/gesc_gaussian/plans/phase_02_plan.md` | `02_state_machine_IMPLEMENT.md` |
| 03 | `03_gaussian_fill_PLAN.md` | `docs/codex/gesc_gaussian/plans/phase_03_plan.md` | `03_gaussian_fill_IMPLEMENT.md` |
| 04 | `04_escape_recenter_PLAN.md` | `docs/codex/gesc_gaussian/plans/phase_04_plan.md` | `04_escape_recenter_IMPLEMENT.md` |
| 05 | `05_rosbag_PLAN.md` | `docs/codex/gesc_gaussian/plans/phase_05_plan.md` | `05_rosbag_IMPLEMENT.md` |
| 06 | `06_scenario_runner_PLAN.md` | `docs/codex/gesc_gaussian/plans/phase_06_plan.md` | `06_scenario_runner_IMPLEMENT.md` |
| 07 | `07_analysis_PLAN.md` | `docs/codex/gesc_gaussian/plans/phase_07_plan.md` | `07_analysis_IMPLEMENT.md` |
| 08 | `08_validation_PLAN.md` | `docs/codex/gesc_gaussian/plans/phase_08_plan.md` | `08_validation_IMPLEMENT.md` |
| 09 | `09_physical_PLAN.md` | `docs/codex/gesc_gaussian/plans/phase_09_plan.md` | `09_physical_IMPLEMENT.md` |
| 10 | `10_documentation_PLAN.md` | `docs/codex/gesc_gaussian/plans/phase_10_plan.md` | `10_documentation_IMPLEMENT.md` |

Each prompt runs the phase-aware context preflight. A Plan chat requires the
Phase 00 audit documents and all prior handoffs after Phase 00. An Implement
chat additionally requires the saved Plan artifact for its own phase.

For Phases 06-10 the preflight also requires:

```text
docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md
docs/codex/gesc_gaussian/handoffs/phase_05_5_handoff.md
```

Every remaining Plan prompt is read-only and must end with a complete durable
Markdown plan for manual saving. Every remaining Implement prompt reads the
five Phase 00 audit files, the bridge, all previous handoffs, and its saved
current-phase plan, then applies the Level A/B/C contradiction policy in
`07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`.

Phase 00 must not be skipped. It converts generic logical names in this package into the real repository's names and file paths.

On the current branch, Phases 00-05 and the Phase 05.5 knowledge consolidation
are complete. The next workflow step is `06_scenario_runner_PLAN.md`; save its
final response as `docs/codex/gesc_gaussian/plans/phase_06_plan.md` before
opening the Phase 06 Implement chat.
