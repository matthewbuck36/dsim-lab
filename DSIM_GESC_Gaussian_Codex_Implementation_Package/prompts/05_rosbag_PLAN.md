You are working inside the existing `dsim-lab` Git repository. This repository already has a structured ROS 2 workspace and may already implement portions of the requested behavior.

Read these files before doing anything:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/00_MASTER_IMPLEMENTATION_PLAN.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md`
- current Plan/status files and any older artifact needed to resolve a specific current claim.

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
10. Stop and report a blocking issue if the required prior-phase handoff is absent.


Before planning, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 05 plan
```

If validation fails, stop and report the missing durable context.

# Phase 05 task: plan unified experiment recording

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/05_DATA_COLLECTION_AND_ROSBAG_SPEC.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/templates/topic_manifest.yaml`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/templates/experiment_metadata.yaml`

Plan a repository-native recording workflow that works in Gazebo and physical modes.

Specify:
- launch/script entry point,
- rosbag2 backend available in the environment,
- required-topic manifest,
- preflight validation,
- metadata collection,
- parameter snapshots,
- Git state,
- console capture,
- shutdown/final-zero handling,
- completeness validation,
- run directory naming,
- tests using a short simulated run.

Do not add a second algorithm implementation.

# Required durable Plan artifact

At the end of this Plan task, produce one self-contained Markdown document
suitable for review and persistence as:

`docs/codex/gesc_gaussian/plans/phase_05_plan.md`

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
enough to save without relying on the chat history. Before opening the Phase 05
Implement chat, save that response at the exact path above.
