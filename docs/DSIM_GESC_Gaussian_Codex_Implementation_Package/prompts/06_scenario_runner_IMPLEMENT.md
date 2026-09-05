You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_06_plan.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`
- the Phase 05.5 bridge/handoff and latest relevant dependency handoff(s), with older handoffs consulted on demand.

Before editing, initialize the live status, verify it against Git, and run:

```bash
docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 06
docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 06 implement
```

The saved Phase 06 plan is the authoritative handoff from Plan mode. Verify its
claims against the current repository and prior handoffs. Apply the three-level
policy in `07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`: stop for Level A;
document and test a local Level B correction; complete evidence and report a
Level C acceptance failure without weakening the gate.

Long-run continuity:
- Maintain `docs/codex/gesc_gaussian/status/phase_06_status.md` throughout execution.
- Record exact evidence continuously and run `checkpoint_phase.sh 06` at material or independently reviewable boundaries.
- After compaction or interruption, reread the plan/status, inspect Git status and diff, and resume from the next incomplete criterion.
- Bound long commands and retain verbose logs by path rather than in chat.
- Do not repeat a recorded failed approach or restructure validated milestone work without failing-test evidence.

Rules:
1. Follow the repository's existing conventions exactly.
2. Reuse and modify current nodes/classes where practical.
3. Keep legacy behavior selectable.
4. Do not silently change cost sign, units, public topics, or physical/simulation semantics.
5. Do not run physical hardware.
6. Add focused tests for every new behavior.
7. Run the repository-standard format/lint/build/test commands relevant to changed packages.
8. Keep changes coherent, reviewable, owner-aligned, and independently tested; split only at meaningful review/test boundaries.
9. Update documentation and parameter references.
10. Write the required phase handoff under `docs/codex/gesc_gaussian/handoffs/`.
11. End with Git status, tests, unresolved issues, and a recommended commit message.
12. Report global status/baseline trend, focused and newly added tests, `git diff --check`, Python syntax/import checks, focused lint/style, exact skips and unexecuted tests, and final totals.


# Phase 06 implementation: Gazebo scenario runner

Implement a deterministic serial scenario runner using repository conventions.

Requirements:
1. Scenario YAML supports all dimensions in the test plan.
2. Every run has unique ID and deterministic seed.
3. Inspect first for an existing scenario/matrix runner. Extend it when appropriate; otherwise add only a distinct orchestration owner.
4. Compose the existing `ros2 run ros_esc record_run` entry point, its manifest/validator, and the existing `gazebo.launch.xml`; do not create a second recorder, run format, validator, launch graph, or algorithm node.
5. Use the existing supervisor and `legacy`/`robust_gaussian_v1` profiles plus actual source, start-pose, bounds, and environment configuration mechanisms.
6. Run serially by default; enforce timeout, deterministic seeds, unique run IDs, and cleanup/ROS-graph checks after every run.
7. Record every run, preserve failures, save scenario metadata, and distinguish controller-observable goal success from simulation-only ground truth.
8. Include example suites when supported by the existing simulator:
   - smoke,
   - two-source levels,
   - multi-source,
   - boundary,
   - noise-delay,
   - ablation.
   - source separation/overlap and close-minimum cases,
   - multiple starts/headings and velocity saturation,
   - pure repulsion, stalled assisted escape, fill merge, and recenter/resume,
   - legacy-versus-robust and component ablations.
9. Document unsupported dimensions and missing infrastructure; do not force them into the simulator.
10. No physical launch path in this runner.
11. Add tests for scenario parsing and at least one recorded short end-to-end run.

Write:
- `docs/codex/gesc_gaussian/handoffs/phase_06_handoff.md`

Recommended commit message:
`phase 06: add deterministic Gazebo robustness runner`
