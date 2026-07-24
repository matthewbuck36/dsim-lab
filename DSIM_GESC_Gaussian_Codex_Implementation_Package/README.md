# DSIM GESC + Robust Gaussian Codex Implementation Package

This package converts the laboratory discussions with Dr. Nili and Patrick into a concrete, phased implementation plan for the existing ROS 2 `dsim-lab` repository.

It is intentionally **repository-adaptive**: the target architecture and behavior are fixed, but Phase 00 discovers the repository's actual node names, packages, topic conventions, launch patterns, parameters, and message definitions before Codex makes edits.

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

## Chosen working interpretation of the whiteboard discussions

The uncertain whiteboard ideas are resolved into the following implementation:

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

## Package sections

- `00_MASTER_IMPLEMENTATION_PLAN.md` — all phases and dependencies.
- `03_ROBUST_GAUSSIAN_ALGORITHM_SPEC.md` — adopted algorithm.
- `04_STATE_MACHINE_SPEC.md` — controller modes and transitions.
- `05_DATA_COLLECTION_AND_ROSBAG_SPEC.md` — complete observability plan.
- `06_TEST_MATRIX_AND_ACCEPTANCE_GATES.md` — required testing and readiness criteria.
- `prompts/` — copy/paste Plan and Implement prompts for Codex.
- `templates/` — starting Plan, handoff, YAML, and data-contract templates.
- `tools/` — repository-context validation and checkpoint helpers.
- `source_material/` — supplied transcripts, audio, whiteboards, and consolidated decisions.

## Why the phases are separated

The implementation touches controller logic, Gaussian generation, ROS interfaces, physical/simulation abstraction, rosbag recording, analysis, and automated tests. Combining all of that in one Codex chat would increase context loss and make regressions more likely.

Each phase produces:

1. A saved Plan artifact at
   `docs/codex/gesc_gaussian/plans/phase_XX_plan.md`.
2. A limited, reviewable change set.
3. Tests.
4. A Git checkpoint.
5. An implementation handoff at
   `docs/codex/gesc_gaussian/handoffs/phase_XX_handoff.md`.

Together, the Phase 00 audits, current saved plan, prior implementation
handoffs, repository state, and Git history carry context between fresh Codex
chats. Do not rely on experimental memory for exact interfaces or decisions.
