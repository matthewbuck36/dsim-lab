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
10. Supports a selectable, simulation-tested bounded-indoor recenter strategy
    before resuming search; the exact strategy remains a provisional research
    policy rather than a fixed invariant.
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

Inspect a dirty working tree before editing. Preserve and work around
non-overlapping user changes; stop only when intended edits overlap or cannot
be preserved safely.

---

## How to use Codex

For every phase:

1. Inspect current code, tests, Git, the active Plan/status, retained evidence,
   and latest relevant dependency handoffs.
2. Run the phase's Plan context validator.
3. Create or amend the durable Plan at
   `docs/codex/gesc_gaussian/plans/phase_XX_plan.md`; a manual verbatim chat
   export is not required.
4. Review the file-level Plan and remain on the same Git branch.
5. Initialize or resume
    `docs/codex/gesc_gaussian/status/phase_XX_status.md`; verify it against Git,
    then run the implementation preflight.
6. Implement milestone by milestone in the same or a new chat. Update live
   status continuously and create a checkpoint at material evidence, expensive
   empirical, or independently reviewable implementation boundaries.
7. Run the tests named in the Plan and write
    `docs/codex/gesc_gaussian/handoffs/phase_XX_handoff.md`.
8. Close the live status and commit the coherent phase before beginning the
   next one.

Use the phases in numeric order. Do not skip Phase 00.

Treat each new chat and every post-compaction continuation as fresh context.
Experimental Codex memory may be useful, but `AGENTS.md`, the version-controlled
audit documents, saved phase plan, live phase status, implementation handoffs,
current repository state, and Git history are the source of truth.

For Phases 06-10, use these as the default historical summary:

```text
docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md
docs/codex/gesc_gaussian/handoffs/phase_05_5_handoff.md
```

The bridge is the current cross-phase summary; the Phase 00 audit remains the
historical baseline. Read older audits and handoffs through targeted
dependency/conflict lookup rather than reloading all of them by default.

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

## Current checkpoint after Phase 08.2

Phases 00-07.5 are implemented. Phase 08 v1 and v2 are closed failed historical
evidence. Phase 08.1 completed its bounded diagnosis, implementation recovery,
and two development-only runtime probes. Phase 08.2 corrected and validated
recenter recovery in one separately versioned development probe. Read:

```text
docs/codex/gesc_gaussian/plans/phase_08_1_plan.md
docs/codex/gesc_gaussian/handoffs/phase_08_1_handoff.md
docs/codex/gesc_gaussian/plans/phase_08_2_plan.md
docs/codex/gesc_gaussian/handoffs/phase_08_2_handoff.md
```

The calibrated-goal probe passed; the Phase 08.1 fill/escape prefix passed but
timed out during recenter. Phase 08.2 preserved that evidence, corrected the
recenter-only policy, and passed the fresh full
`SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE ->
RECENTER -> SEARCH` contract. Simulation readiness is still not established:
the next justified work is a separately reviewed v3 acceptance Plan. Do not
resume or relabel historical evidence, rerun completed probes unchanged, start
v3 tuning/freeze/acceptance without that Plan, launch physical motion, or
proceed to Phase 09.

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
