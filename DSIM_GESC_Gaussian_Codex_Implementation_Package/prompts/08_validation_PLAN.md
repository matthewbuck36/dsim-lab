You are working inside the existing `dsim-lab` Git repository. This repository already has a structured ROS 2 workspace and may already implement portions of the requested behavior.

Read these files before doing anything:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/00_MASTER_IMPLEMENTATION_PLAN.md`
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md`
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`;
- `handoffs/phase_05_5_handoff.md`, the Phase 07/07.5 handoffs, the current
  Phase 08 status/failure report, and older artifacts only when a current claim
  depends on them.

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
10. Apply the Level A/B/C contradiction policy in `07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`; a gate miss closes that experiment version honestly but permits separately planned diagnosis, correction, and a new version.


Before planning, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 plan
```

If validation fails, stop and report the missing durable context.

# Phase 08 task: plan diagnostic development, robustness validation, and freeze

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/06_TEST_MATRIX_AND_ACCEPTANCE_GATES.md`
- the completed Phase 08.1 Plan, status, handoff, relevant retained evidence,
  and any separately approved successor Plan.

If v1 or v2 already failed, preserve them and plan a new version; never resume,
overwrite, relabel, or count their evidence.

Separate development from formal acceptance:

Specify:
- smoke tests,
- retained-evidence diagnosis and minimal runtime probes,
- diagnostic infrastructure/readiness checks and scenario-specific aggregate
  lifecycle reachability,
- bounded versioned development/tuning ranges,
- selection criterion,
- one machine-readable acceptance contract and its hash,
- a sealed selection-blind holdout,
- a fixed additional unique validation allocation,
- predeclared reproducibility repeats,
- minimum metric denominators and exact pass/fail/N/A semantics,
- bounded infrastructure-invalid replacement policy,
- acceptance calculation,
- early-stop criteria,
- bounded implementation/empirical milestones with focused checks, retained
  artifact paths, live-status updates, and checkpoint boundaries,
- parameter freeze,
- Git tag,
- generated validation report.

Avoid tuning on every scenario. Development attempts are retained and bounded
but do not enter the acceptance denominator. Freeze one parameter set before
holdout. A holdout or acceptance failure stops later stages in that experiment
version without weakening thresholds; a subsequent attempt requires a new
version and fresh evidence root. The former 519 x 3 v1 and exact 120-run v2
designs are historical evidence. A simulation-ready tag is permitted only if
every newly sealed gate passes.

# Required durable Plan artifact

The existing `phase_08_plan.md` and `phase_08_1_plan.md` are historical,
approved intent and must not be overwritten for a successor. At the current
closed checkpoint, this prompt performs orientation only unless the user
explicitly authorizes a new versioned subphase. An authorized successor must
use a new unambiguous versioned path selected and reported by the planner, for
example:

`docs/codex/gesc_gaussian/plans/phase_08_2_plan.md`

If no successor is authorized, stop after reporting the current boundary
rather than silently amending either historical Plan. The new document must
contain:
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
enough to save without relying on the chat history. Before opening a successor
Implement chat, save and review it at the newly authorized exact path.
