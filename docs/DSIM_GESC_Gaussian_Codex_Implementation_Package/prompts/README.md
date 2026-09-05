# Prompt Sequence

Use each pair in numeric order. The Plan must be persisted and reviewed at the
listed path before implementation; chat boundaries and manual verbatim copying
are not gates.

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

Each prompt runs the phase-aware context preflight. Current Plan/status and core
safety/research context are hard requirements; older audits and handoffs are
targeted history and become hard requirements only with `--strict-history`.
Before an Implement preflight, initialize or resume
`docs/codex/gesc_gaussian/status/phase_XX_status.md`. The Implement check
requires both the saved Plan and live status for its own phase.

For Phases 06-10 the preflight also requires:

```text
docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md
docs/codex/gesc_gaussian/handoffs/phase_05_5_handoff.md
```

Every Plan must become a complete durable Markdown artifact. Implementations
read the active Plan/status, current repository state, bridge, and latest
relevant dependency handoffs, then consult older artifacts on demand and apply
the Level A/B/C policy.

Phase 00 must not be skipped. It converts generic logical names in this package into the real repository's names and file paths.

On the current branch, Phases 00-07.5 are implemented. Phase 08 v1 and v2 are
closed failed historical evidence. Phase 08.1 completed its bounded recovery
with a mixed diagnostic result, and Phase 08.2 subsequently validated the
bounded recenter correction; read
`docs/codex/gesc_gaussian/handoffs/phase_08_1_handoff.md` and
`docs/codex/gesc_gaussian/handoffs/phase_08_2_handoff.md`. No successor is
authorized merely by this prompt sequence. Create and review a separate v3
acceptance Plan before development/tuning, freeze, holdout, or validation, and
do not rerun historical evidence or advance to physical work.
