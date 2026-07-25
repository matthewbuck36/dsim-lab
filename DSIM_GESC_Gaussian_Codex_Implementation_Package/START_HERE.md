# START HERE — DSIM GESC + Robust Gaussian Implementation Package

This package is designed to be copied into the root of the existing `dsim-lab` Git repository and used with the Codex extension in VS Code.

## The intended outcome

Implement a backward-compatible **GESC + robust Gaussian local-minimum escape system** that:

1. Uses the existing GESC implementation as the baseline.
2. Keeps raw light-sensor data measured and logged continuously.
3. Separately switches the controller contributions from:
   - the raw sensor cost,
   - Gaussian repulsion,
   - the affine/directional term.
4. Detects an undesired local minimum.
5. Estimates the basin center and size from recent data without requiring many complete orbits.
6. Creates or enlarges one smooth fill for the entire basin instead of repeatedly creating narrow overlapping fills.
7. Temporarily disables raw-cost attraction while escaping.
8. Retains past fills so the robot does not return to known minima.
9. Uses a deterministic assisted-escape fallback when pure repulsion stalls.
10. Returns to the center of a bounded indoor environment before resuming search.
11. Records every important input, output, parameter, event, command, and state with synchronized ROS timestamps.
12. Uses the same algorithm and logging interfaces in Gazebo and on the physical TurtleBot.
13. Does not proceed to new physical trials until the simulation acceptance gates are met.

Heavy-Ball ESC is outside the scope of this implementation.

---

## Where to put this package

Extract this folder into the repository root so the structure resembles:

```text
dsim-lab/
├── ros2_ws/
├── ...
└── DSIM_GESC_Gaussian_Codex_Implementation_Package/
```

Do not move individual prompt files into source packages. Keep this package intact as the implementation record.

---

## Git setup

From the repository root:

```bash
git status
git switch -c feature/gesc-gaussian-robustness-v1
```

Do not begin from a dirty working tree unless the current changes are intentionally committed or stashed.

---

## How to use Codex

For every phase:

1. Start a **new Codex chat**.
2. Use **Plan mode** first.
3. Paste the phase's `*_PLAN.md` prompt.
4. Let the prompt's context validator confirm that the required audit and
   prior-handoff files exist.
5. Review the exact file-level plan that Codex produces.
6. Save the complete final Plan response at
   `docs/codex/gesc_gaussian/plans/phase_XX_plan.md`.
7. Stay on the same Git branch.
8. Start a new Codex chat in implementation/goal mode.
9. Paste the corresponding `*_IMPLEMENT.md` prompt.
10. Initialize or resume
    `docs/codex/gesc_gaussian/status/phase_XX_status.md`; verify it against Git,
    then let the implementation preflight verify the saved plan, live status,
    Phase 00 audit documents, and prior handoffs.
11. Require Codex to update the live status and create a repository checkpoint
    after every verified milestone.
12. Require Codex to run the tests named in the prompt and write
    `docs/codex/gesc_gaussian/handoffs/phase_XX_handoff.md`.
13. Close the live status and commit the phase before beginning the next one.

Use the phases in numeric order. Do not skip Phase 00.

Treat each new chat and every post-compaction continuation as fresh context.
Experimental Codex memory may be useful, but `AGENTS.md`, the version-controlled
audit documents, saved phase plan, live phase status, implementation handoffs,
current repository state, and Git history are the source of truth.

For Phases 06-10, every Plan and Implement chat must also read:

```text
docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md
docs/codex/gesc_gaussian/handoffs/phase_05_5_handoff.md
```

The bridge is the current cross-phase summary; the Phase 00 audit remains the
historical baseline. Implement chats must read all previous handoffs and their
saved current-phase plan. Plan chats are read-only and must end with a complete
Markdown plan suitable for manual saving at the documented path.

---

## First prompt

Open:

```text
prompts/00_repo_audit_PLAN.md
```

Paste its entire contents into Codex Plan mode.

Phase 00 is intentionally read-only. It forces Codex to discover the repository's real packages, topics, nodes, launch files, message types, tests, and naming conventions before any implementation is attempted.

The completed Phase 00 Plan has been saved at:

```text
docs/codex/gesc_gaussian/plans/phase_00_plan.md
```

The Phase 00 Implement chat must read and verify that file before creating the
audit documents.

## Current checkpoint at Phase 08

Phases 00-07.5 are implemented. Phase 08 v1 failed/incompletely executed and is
retained as historical evidence. The amended staged Phase 08 v2 plan is saved.
The next implementation prompt for the current branch is:

```text
prompts/08_validation_IMPLEMENT.md
```

Before using it, read the saved Phase 08 plan and
`docs/codex/gesc_gaussian/status/phase_08_status.md`, then inspect Git state.
Do not resume the retired v1 full-pass workflow.

---

## Non-negotiable rules

- Reuse and extend existing nodes rather than creating parallel duplicate systems.
- Preserve legacy behavior behind an explicit legacy profile or feature flag.
- Do not silently change the sign or units of the existing cost.
- Do not stop measuring the sensor when its controller weight is zero.
- Do not rely on terminal text as the experimental record.
- Do not let Gazebo and physical runs use different algorithm logic.
- Do not hard-code topic names that already have a repository convention.
- Do not launch the physical robot during Phases 00–08.
- Stop safely and publish zero velocity on exceptions, invalid data, or timeouts.

## Contradiction policy

- **Level A — hard contradiction:** stop before further edits when cost sign or
  units, the research objective, public compatibility, dependency availability,
  physical safety/authorization, preservation of unrelated changes, shared
  simulation/physical algorithm behavior, or the approved architecture would
  be violated, or when major redesign/scope expansion is required.
- **Level B — bounded implementation correction:** continue only for a local,
  testable runtime or implementation correction that preserves the research
  objective and public architecture and does not weaken acceptance criteria.
  The handoff must record the original assumption, observed contradiction,
  exact correction, files, tests, and scope justification.
- **Level C — acceptance or research failure:** finish the current declared
  stage, obey predeclared early-stop gates before later expensive stages,
  report the failed gate honestly, preserve failed runs, and name the smallest
  justified next step. Do not relabel failure as incomplete work or weaken a
  threshold without a versioned justification.

## Test reporting contract

Every Implement handoff reports the global build/test result and baseline
trend, focused changed-package tests, tests added by the phase,
`git diff --check`, modified-Python syntax/import checks, focused lint/style
checks when global lint has inherited debt, and exact skipped or unexecuted
tests with reasons. A phase is not described as fully tested when a required
test was not executable.

---

## Addendum

Reuse or extend an existing node when that node already owns the responsibility. A new node may be created only when
the repository audit shows that no existing node is an appropriate owner, the feature has a distinct ROS responsibility
and interface, and the new node follows the repository’s established architecture. Do not create duplicate,
simulation-specific, physical-specific, or replacement implementations of existing algorithm behavior.
