You are working inside the existing `dsim-lab` Git repository. This repository already has a structured ROS 2 workspace and may already implement portions of the requested behavior.

Read these files before doing anything:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/00_MASTER_IMPLEMENTATION_PLAN.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`
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
10. Apply the three-level contradiction policy in `07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`: stop for Level A, plan and require documentation for testable Level B corrections, and require honest Level C failure reports without weakened gates.


Before planning, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 06 plan
```

If validation fails, stop and report the missing durable context.

# Phase 06 task: plan repeatable Gazebo scenario execution

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/06_TEST_MATRIX_AND_ACCEPTANCE_GATES.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/templates/scenario_example.yaml`

Plan:
- scenario YAML schema,
- deterministic seed handling,
- source count/position/level configuration,
- starting pose/headings,
- bounds,
- noise/delay,
- algorithm profile and ablations,
- run timeout and success criteria,
- automatic rosbag start,
- reset/cleanup,
- summary output,
- safe parallelism or explicit serial execution.

First inspect the repository for any scenario, sweep, matrix, or batch runner.
Extend an appropriate owner if one exists. The current Phase 05 architecture
must be composed through `ros2 run ros_esc record_run` and
`ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`; do not plan a
second recorder, run-directory format, completeness validator, algorithm node,
or launch graph. Use the existing supervisor, robust/legacy profiles, source
arguments, and environment/bounds arguments.

Plan serial execution by default, deterministic seeds, unique run IDs, cleanup
verification after every run, preservation of failed runs, scenario metadata,
and separate controller goal success from simulation-only ground truth. Cover,
where the existing simulator supports them: smoke; ordered two-source light
levels; separations and overlapping attraction regions; three-source cases;
wall/corner minima; close minima; starting poses/headings; noise/delay;
velocity saturation; pure-repulsion success; repulsion stall plus assistance;
fill merge; recenter/resume; legacy-versus-robust regression; and component
ablations. Record unsupported dimensions and missing infrastructure instead of
silently inventing it.

Prefer serial execution initially to protect simulation stability and Codex/debug clarity.

# Required durable Plan artifact

At the end of this Plan task, produce one self-contained Markdown document
suitable for review and persistence as:

`docs/codex/gesc_gaussian/plans/phase_06_plan.md`

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
enough to save without relying on the chat history. Before opening the Phase 06
Implement chat, save that response at the exact path above.
