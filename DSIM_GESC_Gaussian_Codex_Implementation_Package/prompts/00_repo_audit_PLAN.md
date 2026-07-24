You are working inside the existing `dsim-lab` Git repository. This repository already has a structured ROS 2 workspace and may already implement portions of the requested behavior.

Read these files before doing anything:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/00_MASTER_IMPLEMENTATION_PLAN.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md`
- all prior files under `docs/codex/gesc_gaussian/`, if they exist.

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
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 00 plan
```

If validation fails, stop and report the missing durable context.

# Phase 00 task: complete read-only repository audit

Perform a deep audit of the repository without changing source files.

Find and document:

1. Workspace roots and every ROS package.
2. Build types, package dependencies, and interface packages.
3. Existing GESC implementation:
   - nodes/classes,
   - inputs/outputs,
   - gains and parameters,
   - dither/filter/internal estimates,
   - command generation and saturation.
4. Existing Gaussian/fill implementation:
   - generation,
   - fill center,
   - amplitude/width,
   - how fills are stored and summed,
   - convergence trigger,
   - affine term,
   - whether raw cost is always active,
   - whether fills differ between Gazebo and physical.
5. Existing convergence detector and event timing.
6. Existing source/light simulation and physical photoresistor path.
7. Gazebo odometry versus Vicon/physical pose wiring.
8. Launch files and mode switches.
9. Data-saving nodes, CSV writers, rosbag scripts, logging, and recorded topics.
10. Existing tests and how to run them.
11. Existing code that already implements any part of:
    - switchable cost weights,
    - state machine,
    - source verification,
    - adaptive fill,
    - wider fill,
    - fill merging,
    - recentering,
    - rosbag recording,
    - bag parsing.
12. Public interfaces that must remain compatible.
13. Exact files proposed for Phases 01–10.

Create a proposed audit document structure in your response using these exact future paths:

- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`

Do not create them yet in Plan mode. Give enough detail that the implementation prompt can create them.

# Required durable Plan artifact

At the end of this Plan task, produce one self-contained Markdown document
suitable for saving verbatim as:

`docs/codex/gesc_gaussian/plans/phase_00_plan.md`

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

Do not edit source code or create the audit documents in Plan mode. Make the
final Plan response complete enough to save without relying on the chat
history. Before opening the Phase 00 Implement chat, save that response at the
exact path above.
