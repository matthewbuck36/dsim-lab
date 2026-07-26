You are working inside the existing `dsim-lab` Git repository. This repository already has a structured ROS 2 workspace and may already implement portions of the requested behavior.

Read these files before doing anything:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/00_MASTER_IMPLEMENTATION_PLAN.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md`
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`;
- `handoffs/phase_05_5_handoff.md`, the latest relevant dependency handoff,
  and older artifacts only when a current claim depends on them.

Rules:
1. Preserve the repository's package organization, node conventions, topic naming, parameter style, launch style, and test conventions.
2. Reuse or extend current nodes and classes. Do not create a parallel replacement because understanding the existing code is inconvenient.
3. Preserve legacy behavior behind an explicit legacy profile or feature flag.
4. Do not introduce Heavy-Ball ESC work.
5. Do not run or command physical hardware.
6. Do not guess exact filenames, topics, or message types. Inspect the repository.
7. In this Plan task, do not edit source code.
8. Produce a file-level plan with exact paths, interfaces, tests, and migration effects.
9. Identify anything already implemented and explain how it will be extended rather than duplicated.
10. Apply the Level A/B/C contradiction policy in `07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`; never weaken an analysis or completeness gate silently.


Before planning, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 07 plan
```

If validation fails, stop and report the missing durable context.

# Phase 07 task: plan bag extraction and diagnostics

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/05_DATA_COLLECTION_AND_ROSBAG_SPEC.md`

Plan a Python analysis package/script using dependencies already available in the repository/ROS environment.

Required outputs:
- synchronized CSV tables,
- cost plot,
- component plot,
- state/event timeline,
- weight timeline,
- trajectory with sources/fills,
- command saturation plot,
- radial escape plot,
- Gaussian history,
- summary metrics,
- completeness report.

Use `rosbag2_py` when available in the audited environment. Avoid a new heavy dependency unless justified.
Use the actual Phase 05 sqlite3 backend, installed topic manifest, and real
message definitions. Preserve every raw bag and raw timestamp. Critical missing
data must invalidate or mark the affected metric rather than be silently
interpolated. Plan synchronized outputs plus escape, state, fill, command,
revisit, saturation, success, and failure metrics for both passed and failed
runs.

# Required durable Plan artifact

At the end of this Plan task, produce one self-contained Markdown document
suitable for review and persistence as:

`docs/codex/gesc_gaussian/plans/phase_07_plan.md`

The document must contain:
- objective and scope,
- repository findings relevant to this phase,
- existing implementations that will be reused or modified,
- exact files proposed for modification,
- exact files proposed for creation,
- justification for any new node, package, message, topic, or dependency,
- public interfaces affected,
- parameter additions and defaults,
- backward-compatibility strategy,
- implementation sequence,
- tests to add and commands to run,
- stop conditions and risks,
- assumptions requiring verification during implementation.

Do not edit source code in Plan mode. Make the final Plan response complete
enough to save without relying on the chat history. Before opening the Phase 07
Implement chat, save that response at the exact path above.
