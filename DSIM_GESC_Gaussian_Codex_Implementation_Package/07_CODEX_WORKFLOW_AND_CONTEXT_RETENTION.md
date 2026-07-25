# Codex Workflow and Context Retention

## One phase per Codex context

Use a new chat for each Plan prompt and each Implement prompt.

Treat every new chat as fresh context. Do not ask one Codex session or
experimental memory to preserve exact decisions from earlier phases. Make the
repository carry the memory.

## Four-part repository memory

Phase 00 creates:

```text
docs/codex/gesc_gaussian/repo_audit.md
docs/codex/gesc_gaussian/repo_map.md
docs/codex/gesc_gaussian/interface_map.md
docs/codex/gesc_gaussian/test_commands.md
docs/codex/gesc_gaussian/implementation_sequence.md
```

Every Plan chat produces a self-contained response that the user saves as:

```text
docs/codex/gesc_gaussian/plans/phase_XX_plan.md
```

Every implementation phase creates:

```text
docs/codex/gesc_gaussian/status/phase_XX_status.md
docs/codex/gesc_gaussian/handoffs/phase_XX_handoff.md
```

These files have distinct responsibilities:

1. **Audit documents** describe how the repository was structured at Phase 00.
2. **Plan documents** preserve what was approved for the current implementation.
3. **Live status and checkpoints** record verified execution state while the
   phase is underway.
4. **Implementation handoffs** record what was actually changed and tested at
   phase close.

Later handoffs are authoritative for completed repository changes. The current
phase plan is authoritative for the approved implementation intent. Git history
and the current checkout remain authoritative for actual file contents.

## Required phase workflow

For Phase `XX`:

1. Start a new Plan-mode chat and paste `prompts/XX_*_PLAN.md`.
2. Run the prompt's `validate_phase_context.sh XX plan` preflight.
3. Review the final self-contained Plan response.
4. Save it verbatim as
   `docs/codex/gesc_gaussian/plans/phase_XX_plan.md`.
5. Start a new implementation/goal chat and paste
   `prompts/XX_*_IMPLEMENT.md`.
6. Run `init_phase_status.sh XX`, verify the generated live status against the
   current checkout, then run `validate_phase_context.sh XX implement`.
7. Verify the saved plan and live status against the current checkout.
8. Implement milestone by milestone. Update the live status and run
   `checkpoint_phase.sh XX` after every verified milestone.
9. Test and write
   `docs/codex/gesc_gaussian/handoffs/phase_XX_handoff.md`.
10. Close the live status, review, and commit the bounded phase before starting
    Phase `XX+1`.

Do not open the Implement chat until the saved Plan artifact exists and passes
validation.

## What a fresh chat must read

A phase Implement chat reads:

```text
START_HERE.md
+ master and phase specifications
+ Phase 00 audit documents
+ previous implementation handoffs
+ current phase saved plan
+ current live phase status
+ current repository state and Git history
= complete working context
```

For Phases 06-10, add both of these durable Phase 05.5 artifacts:

```text
docs/codex/gesc_gaussian/knowledge_bridge_phase_00_05.md
docs/codex/gesc_gaussian/handoffs/phase_05_5_handoff.md
```

Every remaining Implement chat must explicitly read all five Phase 00 audit
files, the knowledge bridge, every prior implementation handoff including
Phase 05.5, and its saved `phase_XX_plan.md`. Every remaining Plan chat is
read-only and must return a complete plan artifact suitable for manual saving.

The Implement chat must verify the plan and live status against the current
checkout before editing and apply the three-level contradiction policy below.

## Live status and milestone checkpoints

Initialize the current phase once:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh XX
```

The initializer refuses to overwrite a nonempty status file. The live status
is a concise semantic shift log, not a second plan or final handoff. It records:

- verified branch, HEAD, working tree, and plan;
- completed and current milestones;
- next incomplete acceptance criterion;
- current problem or blocker;
- files relevant now;
- decisions, rationale, and rejected approaches;
- exact validation commands, results, skips, and artifact paths;
- attempts and expensive actions not to repeat;
- remaining work and active stop conditions.

After each meaningful milestone:

1. run milestone-specific and relevant regression tests;
2. update the live status from observed evidence;
3. inspect the diff for unintended scope changes;
4. run `checkpoint_phase.sh XX`;
5. create a bounded commit if the milestone is independently validated and
   commits are authorized.

The checkpoint contains status/plan hashes, Git state, recent commits,
`git diff --check`, changed-file summaries, and a live-status snapshot. It does
not claim tests passed; exact test results must come from the verified live
status and validation record.

## Recovery after compaction or interruption

Before making another change after compaction, model switch, interruption, or
long wait:

1. reread `AGENTS.md`, the phase plan, and live phase status;
2. inspect `git status --short --branch`, the diff stat, and relevant diff;
3. compare completed milestones to objective evidence and retained artifacts;
4. identify the next incomplete acceptance criterion;
5. confirm that the proposed action is not listed under attempts not to repeat;
6. continue only from the reconstructed repository state.

Do not rely solely on conversation memory or a compacted summary to determine
project state. If the live status conflicts with Git, code, tests, or artifacts,
correct the status and record the discrepancy before proceeding.

## Bounded commands and context hygiene

- Give every ROS, Gazebo, test, and batch command a finite duration or external
  timeout.
- Redirect verbose output to a retained log/artifact path and record the exact
  path plus concise outcome; do not keep full batch logs in conversation.
- Read only files relevant to the current milestone after the required context
  set is loaded.
- Do not rerun an expensive batch to recover context. Inspect its manifests,
  completeness reports, analysis outputs, and status record first.

## Reasoning effort and execution surface

Use reasoning effort deliberately:

- Medium for decision-complete implementation, documentation, targeted fixes,
  and individual tests.
- High for architecture choices, cross-package failures, unfamiliar runtime
  bugs, or acceptance diagnosis.
- The highest available effort only for genuinely ambiguous, sustained
  investigation where deeper exploration is worth faster context consumption.

Reasoning effort does not replace durable status or verification. Prefer
several evidence-backed milestones over one uncheckpointed long run.

Use the local IDE/CLI agent for work that depends on this exact ROS 2 Humble,
Gazebo, DSIM, local run evidence, or later authorized hardware environment.
Delegate only self-contained tasks to a cloud environment, and only when their
dependencies and tests are reproducible there. Never treat an unavailable
cloud simulation or hardware result as a pass.

## Source-of-truth order

When documents disagree, use this order:

1. Current repository code and tests.
2. Current resolved ROS interfaces and launch graph.
3. Completed implementation handoffs.
4. Saved phase plans.
5. Current live phase status and verified checkpoints.
6. Phase 00 audit and repository maps.
7. Package design specifications.
8. Saved chat transcripts.
9. Experimental Codex memory.

When implementation differs from a plan, record what changed, why, whether it
was bounded, the supporting tests, and the now-authoritative artifact.

## Three-level contradiction policy

### Level A — hard contradiction: stop

Stop and report before editing further if cost sign/units or the research
objective would change; public architecture would become incompatible; a
required dependency is unavailable; physical safety or authorization is
involved; unrelated user changes cannot be preserved; major scope expansion or
architectural redesign is required; a new node/package would violate the reuse
policy; simulation and physical algorithms would diverge; or the plan depends
on a nonexistent component that has no compatible bounded replacement.

### Level B — bounded implementation correction: document and continue

Continue only when the research objective and public architecture remain
unchanged, the correction is local and testable, the issue could only be found
during implementation/runtime work, and acceptance criteria are not weakened.
Examples include launch parameter typing, QoS, signal/executor ordering,
lifecycle sequencing, stale-process cleanup, endpoint counts, readiness
semantics, test-harness corrections, launch ownership, evidence-based timing
tolerances, and parameter-service snapshots.

The handoff must state the original assumption, observed contradiction, exact
correction, changed files, tests, and why it remained in scope.

### Level C — acceptance or research failure: complete with a failure report

Do not disguise a missed algorithm/scenario gate as incomplete implementation
or silently weaken the threshold. Complete the current declared stage, retain
successful and failed evidence, and obey any predeclared early-stop gate before
dispatching a later expensive stage. Write a structured failure report and
identify the smallest justified next engineering step. Phase 08 must not create
a simulation-ready tag unless every declared gate passes.

## Plan artifact requirements

Each saved phase plan must include:

- objective and scope;
- repository findings relevant to the phase;
- existing implementations to reuse or extend;
- exact files to modify and create;
- justification for every new node, package, message, topic, or dependency;
- public interfaces and parameter defaults;
- backward compatibility and migration;
- implementation sequence;
- milestone/checkpoint boundaries and the next acceptance criterion after each;
- tests, commands, and acceptance criteria;
- stop conditions and risks;
- assumptions requiring implementation-time verification.

Use `templates/codex_phase_plan.md` as the canonical structure.

## Context validation

Run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh XX plan
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh XX implement
```

The Plan check verifies the core specifications and, after Phase 00, all Phase
00 audit documents and previous phase handoffs. Before the Implement check,
initialize and verify the current live status. The Implement check adds the
saved Plan and live status artifacts and validates the required status
headings. Missing or empty context is a blocking error.

`tools/validate_required_docs.sh` remains available as the Phase 00 audit-only
compatibility check.

## Commit discipline

Recommended commit pattern:

```text
phase 00: audit dsim-lab GESC/Gaussian architecture
phase 01: add common algorithm observability contract
phase 02: add robust Gaussian supervisor state machine
phase 03: add adaptive basin fill design and merging
phase 04: add escape progress and indoor recentering
phase 05: unify rosbag experiment recording
phase 06: add Gazebo robustness scenario runner
phase 07: add bag analysis and standard plots
phase 08: validate and freeze robust Gaussian profile
phase 09: integrate physical light-source workflow
phase 10: finalize documentation and reproducibility
```

## Codex stop rules

Codex must stop and report instead of guessing when:

- the audit files are absent,
- the current phase plan is absent,
- a required previous handoff is absent,
- the repository contradicts the saved phase plan,
- current code contradicts the assumed cost sign,
- two active nodes publish the same canonical output,
- a required package dependency is unavailable,
- a message change would break an external package without a migration path,
- tests cannot be run,
- physical hardware would be required before Phase 09,
- the working tree contains unrelated uncommitted changes.

## Change-size control

A phase should normally change no more than:

- 6–10 implementation files,
- plus tests/config/docs.

If Codex predicts a larger change, it must split the phase into subphases and write that split into the Plan response.

## End-of-phase handoff

Every handoff must contain:

- objective completed,
- exact files changed,
- public interfaces added or changed,
- parameter names and defaults,
- tests run and outputs,
- remaining failures,
- known limitations,
- migration/backward-compatibility notes,
- exact next prompt,
- Git status and recommended commit message.

Before writing the final handoff, update the live status with the final
authoritative totals, remaining limitations, and `Status: COMPLETE` or
`Status: FAILED`. A handoff must not describe a phase as complete while its live
status still claims an unverified milestone is in progress.

Each handoff must also separate:

- global build/test status and whether the inherited baseline improved, stayed
  constant, or worsened;
- focused tests for changed packages and tests newly added by the phase;
- `git diff --check` and syntax/import checks for modified Python;
- focused lint/style checks when global lint contains inherited failures;
- exact skipped tests and reasons;
- exact unexecuted tests and reasons;
- final authoritative totals;
- Level A contradictions, Level B amendments, and Level C acceptance failures.

## Efficient context bundle

Run:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/make_codex_context_bundle.sh
```

This produces a compact repository summary for Codex without copying build/install/log directories.

The bundle includes `AGENTS.md` and live-status contents, then indexes audit
documents, saved plans, handoffs, and checkpoints separately. It supplements
the required direct file reads; it does not replace them.

## Experimental memory

Use experimental Codex memory as a convenience only. It must not be the source
of truth for:

- exact topic or message names;
- node and callback ownership;
- reasons for interface decisions;
- files intentionally left unchanged;
- test commands and results;
- parameter defaults;
- compatibility decisions;
- unresolved failures.

Those details belong in the version-controlled audit, plan, live status,
validation record, checkpoint, and handoff files.
