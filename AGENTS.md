# DSIM-Lab Agent Instructions

These instructions apply to the entire repository.

## Durable source of truth

Do not rely on conversation memory to determine project state. Reconstruct it
from, in order:

1. current code, tests, resolved ROS interfaces, and launch graph;
2. current Git status, diff, and recent commits;
3. completed phase handoffs;
4. the current phase plan;
5. the current live phase status;
6. Phase 00 audit documents and the Phase 00-05 knowledge bridge;
7. package specifications;
8. chat exports or experimental memory.

For GESC/Gaussian work, read the current navigation/workflow documents, current
phase plan (including any active amendment or subphase plan), and current live
status. Use the knowledge bridge, dependency handoffs, audits, and older
handoffs through targeted lookup when the current milestone depends on them;
do not load every historical artifact by default. Before phase work, run the
package's `tools/validate_phase_context.sh` with `XX plan` or `XX implement`.

## Start or recovery checklist

Before editing, and again after any context compaction:

1. reread this file, the current phase plan, and any active amendment/subphase
   plan;
2. read `docs/codex/gesc_gaussian/status/phase_XX_status.md`;
3. inspect `git status --short --branch`, `git diff --stat`, and the relevant
   diff;
4. verify the next incomplete acceptance criterion;
5. confirm that the proposed work does not repeat a recorded failed approach or
   cross a stop condition.

If the status file is absent at implementation start, run the package's
`tools/init_phase_status.sh XX`. Never overwrite a nonempty status file with a
new template.

## Milestone discipline

Work one declared milestone at a time. Before moving on:

- run the milestone-specific test and relevant focused regressions;
- record exact commands, outcomes, skips, and artifact paths in the live status
  and durable validation record;
- inspect the diff for unintended scope changes;
- run the package's `tools/checkpoint_phase.sh XX` at material evidence,
  expensive empirical, or independently reviewable implementation boundaries;
- create a bounded Git commit when the milestone is independently validated and
  the user has authorized commits.

Do not revert, rewrite, or substantially restructure completed milestone work
without recorded evidence. A failed fixed experiment version remains failed,
but it does not prohibit diagnosis, bounded correction, or a fresh versioned
experiment.

## Contradictions and workspace state

- Stop for Level A safety, objective, cost-sign/unit, ownership, compatibility,
  physical-authorization, or overlapping-user-change conflicts.
- Treat bounded runtime, readiness, evidence-contract, scenario-contract, and
  performance corrections as Level B when they preserve the research
  objective and public architecture.
- A Level C gate closes that experiment version honestly. Preserve it, then
  allow a separately planned diagnostic/development iteration.
- Preserve unrelated dirty changes and continue when work is non-overlapping.
  Stop only when they overlap or cannot be preserved safely.
- Report unavailable required tests honestly. Continue other safe diagnostics
  and tests unless the missing result is necessary for the next risky action.
- Bound scope by coherent ownership, reviewability, risk, and tests rather than
  an arbitrary file count.

## Runtime and evidence safety

- Bound every Gazebo, ROS, test, and batch command with an explicit timeout or
  finite scenario duration.
- Keep verbose logs and large run artifacts out of conversation and Git; record
  their exact retained path and a concise result instead.
- Never rerun an expensive matrix merely to recover context. Read the status,
  manifests, completeness files, and prior results first.
- Preserve failed runs and distinguish infrastructure completeness from
  behavioral acceptance.
- Do not launch physical hardware during Phases 00-08.
- Preserve selectable legacy behavior, cost sign and units, canonical topics,
  controller ownership, and simulation/physical algorithm parity.

## Completion

A phase is complete only when its declared criteria are verified, exact
validation evidence is recorded, the live status is closed, the phase handoff
is written, and Git state plus remaining limitations are reported.
