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
10. Apply the Level A/B/C contradiction policy in `07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`; acceptance failures and unsupported claims remain visible results.


Before planning, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 10 plan
```

If validation fails, stop and report the missing durable context.

# Phase 10 task: plan final documentation and cleanup

Plan repository documentation for:
- architecture,
- algorithm equations,
- state machine,
- topic dictionary,
- parameter reference,
- simulation launch,
- physical launch,
- data recording,
- analysis,
- validation results,
- known limitations,
- reproducibility,
- migration from legacy behavior,
- thesis-facing methods summary.

The required Phase 10 report deliverables are the exact, case-sensitive paths:

```text
docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.pdf
docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.tex
docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.md
```

Plan a LaTeX-typeset PDF as the canonical reader-facing report, with the `.tex`
source and `.md` audit companion carrying the same substantive content. It
must be a self-contained report on the complete implementation package and all
Phases 00-10 results, not a short README or selected-success summary. Include
clear architecture/state/sequence diagrams and evidence graphs wherever they
improve comprehension without pooling incompatible denominators.
Also plan a machine-readable coverage matrix for every package-manifest entry,
phase/subphase, material experiment version, result, and retained evidence
class, plus a documentation-validation record. The final claim must preserve
the failed broad simulation/physical readiness gates; selected v8.10 `11/11`,
v8.11 `6/6`, v8.12 visible `14/14`, varied `13/14`, the three withheld cases,
and Phase 09 eighth-run `61/62` result must retain their exact scopes.

Identify stale or contradictory documentation that must be updated.
Use the final live repository state and validated commands. Keep Heavy-Ball
material only as clearly historical context; remove it from the active GESC +
Gaussian workflow. Preserve honest limitations and failed acceptance results.

# Required durable Plan artifact

At the end of this Plan task, produce one self-contained Markdown document
suitable for review and persistence as:

`docs/codex/gesc_gaussian/plans/phase_10_plan.md`

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

The Plan must keep all work on `feature/gesc-gaussian-robustness-v1`, prohibit
hardware/runtime execution, and treat a future
`feature/gesc-gaussian-robustness-v2` branch as out of scope.

Do not edit source code in Plan mode. Make the final Plan response complete
enough to save without relying on the chat history. Before opening the Phase 10
Implement chat, save that response at the exact path above.
