You are implementing one bounded phase in the existing `dsim-lab` Git repository.

Read:
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
- the phase specification named in this prompt,
- `docs/codex/gesc_gaussian/plans/phase_06_plan.md`
- `docs/codex/gesc_gaussian/repo_audit.md`
- `docs/codex/gesc_gaussian/repo_map.md`
- `docs/codex/gesc_gaussian/interface_map.md`
- `docs/codex/gesc_gaussian/test_commands.md`
- `docs/codex/gesc_gaussian/implementation_sequence.md`
- `docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md`
- every previous phase handoff, including `phase_05_5_handoff.md`.

Before editing, run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 06 implement
```

The saved Phase 06 plan is the authoritative handoff from Plan mode. Verify its
claims against the current repository and prior handoffs. Apply the three-level
policy in `07_CODEX_WORKFLOW_AND_CONTEXT_RETENTION.md`: stop for Level A;
document and test a local Level B correction; complete evidence and report a
Level C acceptance failure without weakening the gate.

Rules:
1. Follow the repository's existing conventions exactly.
2. Reuse and modify current nodes/classes where practical.
3. Keep legacy behavior selectable.
4. Do not silently change cost sign, units, public topics, or physical/simulation semantics.
5. Do not run physical hardware.
6. Add focused tests for every new behavior.
7. Run the repository-standard format/lint/build/test commands relevant to changed packages.
8. Keep the change bounded. If it exceeds roughly 10 implementation files, split it into coherent subcommits and explain why.
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
