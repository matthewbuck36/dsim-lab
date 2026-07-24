You are working inside the existing `dsim-lab` Git repository. This repository already has a structured ROS 2 workspace and may already implement portions of the requested behavior.

Read these files before doing anything:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/00_MASTER_IMPLEMENTATION_PLAN.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md`
- the five Phase 00 audit files under `docs/codex/gesc_gaussian/`;
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`;
- every prior handoff, including `handoffs/phase_05_5_handoff.md`.

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
10. Apply the Level A/B/C contradiction policy in `07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`; Phase 08 gate misses are Level C results, not permission to weaken thresholds.


Before planning, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 plan
```

If validation fails, stop and report the missing durable context.

# Phase 08 task: plan robustness validation and parameter freeze

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/06_TEST_MATRIX_AND_ACCEPTANCE_GATES.md`
- all prior phase handoffs.

Plan the exact test execution order using the repository's implemented scenario suites.

Specify:
- smoke tests,
- parameter sweep ranges,
- selection criterion,
- holdout scenarios,
- full matrix,
- three-pass regression,
- acceptance calculation,
- parameter freeze,
- Git tag,
- generated validation report.

Avoid tuning on every scenario. Reserve a holdout subset to detect overfitting.
Freeze one parameter set before the final matrix, require three repeated
full-suite passes without code or parameter changes, preserve failed runs, and
plan a structured failure report. A simulation-ready tag is permitted only if
every declared gate passes.

# Required durable Plan artifact

At the end of this Plan task, produce one self-contained Markdown document
suitable for saving verbatim as:

`docs/codex/gesc_gaussian/plans/phase_08_plan.md`

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
enough to save without relying on the chat history. Before opening the Phase 08
Implement chat, save that response at the exact path above.
