# DSIM GESC + Robust Gaussian Codex Implementation Package

This package converts the laboratory discussions with Dr. Nili and Patrick into a concrete, phased implementation plan for the existing ROS 2 `dsim-lab` repository.

It is intentionally **repository-adaptive**: the target architecture and behavior are fixed, but Phase 00 discovers the repository's actual node names, packages, topic conventions, launch patterns, parameters, and message definitions before Codex makes edits.

## Phase 10 V1 closeout

The authoritative, thesis-facing account of the completed V1 effort is the
LaTeX-typeset [`FINAL_PROJECT_REPORT_V1.pdf`](../codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.pdf).
Its [`FINAL_PROJECT_REPORT_V1.tex`](../codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.tex)
source and [Markdown audit companion](../codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.md)
are retained with it.
It reconciles the design package, Phases 00-10, current implementation owners,
retained evidence, reproducibility instructions, and limitations. The
[coverage matrix](../codex/gesc_gaussian/validation/phase_10_report_coverage.tsv)
indexes the material considered by that report.

V1 did **not** establish broad simulation or physical robustness. Its strongest
selected simulation results were v8.10 primary `11/11`, v8.11 secondary `6/6`,
and the v8.12 visible probe `14/14`; the first varied v8.12 case was `13/14`
and the other three varied cases were withheld. The eighth retained physical
run demonstrated the selected two-basin behavior, but stopped before a second
convergence or `GOAL_HOLD` and passed `61/62` completeness checks. These scoped
results must not be relabeled as broad readiness.

Phase 10 is documentation-only: it authorizes no hardware run, runtime change,
or V2 work. A future `feature/gesc-gaussian-robustness-v2` branch may start from
the completed V1 closeout commit, but must use separately versioned plans,
evidence, and reports rather than revising the V1 result.

## Research direction captured here

The research baseline is now:

```text
Gradient-Descent Extremum Seeking Control (GESC)
+
Gaussian local-minimum escape
+
complete time-synchronized experimental data collection
```

The physical cost field is generated with light sources and measured with the existing light sensor/photoresistor system. Acoustic fields remain a future application and motivation.

## Current testable interpretation of the whiteboard discussions

The uncertain whiteboard ideas currently use the following implementation:

- The controller cost is decomposed into raw sensor cost, Gaussian repulsion, and affine/directional contributions.
- Those contributions are independently weighted and logged.
- Raw sensor attraction is temporarily disabled during escape.
- The initial escape attempt uses pure Gaussian repulsion.
- A deterministic assisted-escape direction is activated only after measured stall.
- Recent pose/cost samples are used in a kernel-weighted basin estimator.
- Patrick's softmax over negative squared distances is used for smooth association and merging of nearby local-minimum/fill estimates.
- Overlapping nearby fills are merged and redesigned as one broader fill.
- Fill width and amplitude are adapted together.
- The algorithm checks a fitted local model for residual minima and escalates the fill before publishing it.
- In bounded indoor mode, the robot returns to the configured room center after escape.
- A calibrated source-score threshold prevents the true source from being filled as though it were an undesired minimum.
- ROS bags and structured ROS messages are the authoritative experimental record.

The meeting source presents pure repulsion, recentering, and wider fills as
ideas to test and explicitly grants implementation freedom. The exact
estimator, fit, escalation, sequencing, and recenter policies are therefore
engineering hypotheses, not immutable research mandates. They may change under
versioned evidence before formal acceptance freeze while safety, interfaces,
observability, and shared simulation/physical semantics remain fixed.

## Package sections

- `00_MASTER_IMPLEMENTATION_PLAN.md` — all phases and dependencies.
- `03_ROBUST_GAUSSIAN_ALGORITHM_SPEC.md` — adopted algorithm.
- `04_STATE_MACHINE_SPEC.md` — controller modes and transitions.
- `05_DATA_COLLECTION_AND_ROSBAG_SPEC.md` — complete observability plan.
- `06_TEST_MATRIX_AND_ACCEPTANCE_GATES.md` — required testing and readiness criteria.
- `prompts/` — copy/paste Plan and Implement prompts for Codex.
- `templates/` — starting Plan, live-status, handoff, YAML, and data-contract
  templates.
- `tools/` — repository-context validation, status initialization, context
  bundle, and milestone checkpoint helpers.
- `source_material/` — supplied transcripts, audio, whiteboards, and consolidated decisions.

## Why the phases are separated

The implementation touches controller logic, Gaussian generation, ROS
interfaces, physical/simulation abstraction, rosbag recording, analysis, and
automated tests. Durable Plans, live status, focused checkpoints, and coherent
commits control that scope; a particular number of chats or files does not.

Each phase produces:

1. A saved Plan artifact at
   `docs/codex/gesc_gaussian/plans/phase_XX_plan.md`.
2. A continuously verified live status at
   `docs/codex/gesc_gaussian/status/phase_XX_status.md`.
3. A limited, reviewable change set.
4. Tests and retained evidence paths.
5. Milestone checkpoints and bounded Git commits.
6. An implementation handoff at
   `docs/codex/gesc_gaussian/handoffs/phase_XX_handoff.md`.

Together, root `AGENTS.md`, the Phase 00 audits, current saved plan and live
status, prior implementation handoffs, repository state, and Git history carry
context between fresh Codex chats and context compactions. Do not rely on
experimental memory for exact interfaces, decisions, or execution state.
