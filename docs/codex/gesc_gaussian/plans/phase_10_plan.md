# Phase 10 Plan — V1 Final Project Report and Documentation Closeout

## Objective and scope

Phase 10 will close the current
`feature/gesc-gaussian-robustness-v1` line as an understandable, reproducible,
and scientifically defensible V1 record. Its required report deliverables are:

```text
docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.pdf
docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.tex
docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.md
```

The PDF is the canonical reader-facing report, the LaTeX file is its
authoritative typesetting source, and the Markdown file is the repository-
native content/audit companion. All three must carry the same substantive V1
claims and evidence boundary. The report must be a self-contained,
thesis-facing account of the complete
`DSIM_GESC_Gaussian_Codex_Implementation_Package` effort and its results. It
must cover every meaningful requirement, source decision, implementation
phase, public interface, experiment version, retained failure, selected
success, validation result, limitation, and reproducibility boundary from
Phases 00 through 10. Supporting READMEs and reference documents must lead to
this report and must agree with the final live repository state.

The report must be comprehensive without copying raw binary or high-volume
evidence into Markdown. Audio, images, source files, bags, CSVs, logs, and
machine-readable results must be summarized faithfully and linked or indexed
by exact retained path. A coverage matrix will prove that each implementation-
package manifest entry and each declared phase/result artifact was considered.
The report itself, not the coverage matrix, remains the substantive narrative.

Success requires all of the following:

1. `FINAL_PROJECT_REPORT_V1.pdf`, `FINAL_PROJECT_REPORT_V1.tex`, and
   `FINAL_PROJECT_REPORT_V1.md` exist at the exact case-sensitive paths above;
   the PDF compiles from the LaTeX source and passes text plus representative
   page inspection.
2. Each report representation contains the complete chapter and appendix
   contract in this Plan.
3. Every file listed by
   `DSIM_GESC_Gaussian_Codex_Implementation_Package/MANIFEST.md` is represented
   in the coverage matrix and is either discussed directly or identified as a
   raw/template/tool input with its role explained.
4. Every completed phase and material subphase has an outcome, evidence path,
   and honest status: proposed, implemented, passed, failed, partial, skipped,
   withheld, superseded, historical, or not run.
5. Phase 08 broad-readiness failures and selected-scenario successes remain
   separate; selected evidence is not converted into an unbiased broad claim.
6. Phase 09 static, transfer, failed-run, repair, and physical behavioral
   evidence is chronological and preserves the exact algorithm/evaluation and
   safety boundaries.
7. The report explicitly concludes that V1 demonstrated selected two-basin
   behavior but did not establish broad simulation robustness, broad physical
   robustness, or a formally complete second-extremum physical acceptance run.
8. All documented commands, links, source owners, topics, message types,
   parameters, signs, units, defaults, and artifact paths are checked against
   live source or retained authoritative evidence.
9. Real repository READMEs are updated; the report is not a disconnected note.
10. Phase 10 validation, live status, checkpoint, and handoff are complete.

Phase 10 is documentation and cleanup only. It will not redesign, tune, or
change the GESC/Gaussian algorithm; change ROS runtime behavior; run a new
Gazebo matrix; access the Pi; command hardware; repeat physical trials; delete
or rewrite retained evidence; or claim that an unavailable artifact was
verified.

## V1 closure and future V2 branch boundary

All Phase 10 work remains on the current
`feature/gesc-gaussian-robustness-v1` branch. Phase 10 must record the exact V1
closeout commit and dirty-state boundary in the report and handoff.

The user intends to create a future branch named:

```text
feature/gesc-gaussian-robustness-v2
```

That future branch must be created on top of the completed V1 closeout commit,
but branch creation, checkout, planning, tuning, implementation, and testing
for V2 are outside Phase 10. Phase 10 may document evidence-backed V2 research
questions and remaining robustness gaps, but it must not preselect fixes,
alter V1 gates, or start a new experiment version.

The `FINAL_PROJECT_REPORT_V1` PDF/LaTeX/Markdown set is the immutable V1
report. Future V2 work must create separately versioned Plans, statuses,
evidence, handoffs, and an eventual V2 report rather than rewriting V1
outcomes.

## Repository findings

- Checkout at Plan creation:
  `feature/gesc-gaussian-robustness-v1`, HEAD `e3dd0ef`, ahead of its remote by
  195 commits, with a clean worktree before this Plan was created. The Implement
  chat must re-resolve branch, HEAD, status, and diffs.
- `validate_phase_context.sh 10 plan` passes. No Phase 10 status exists yet;
  `init_phase_status.sh 10` belongs to implementation start, after this Plan is
  saved.
- The canonical simulation workspace contains `ros_esc`,
  `ros_esc_interfaces`, and `turtlebot3_rotating_sensor`.
- The physical source snapshot is outside the Git worktree at
  `/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src` and contains
  `ros_esc`, `ros_esc_interfaces`, and `turtlebot3_vehicle_nodes`. Phase 10 may
  read it to verify documentation but must not edit it or transfer to the Pi.
- Existing owners remain authoritative: the cost, filter, controller,
  convergence, Gaussian-fill, supervisor, scenario, recorder, validator,
  analysis, Gazebo launch, and selected physical launch/wrapper owners must be
  documented rather than duplicated.
- `README.md` is currently only a two-line repository stub. The package and ROS
  package READMEs contain useful but incomplete or historical instructions.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`,
  `docs/codex/gesc_gaussian/implementation_sequence.md`, and
  `DSIM_GESC_Gaussian_Codex_Implementation_Package/10_PHYSICAL_EXPERIMENT_READINESS.md`
  stop at older Phase 09 checkpoints and must be reconciled with the appended
  Phase 09 handoff/status and eighth-run validation.
- Phase 08 is terminally closed for V1. Broad simulation readiness failed.
  Selected evidence includes v8.10 primary `11/11`, v8.11 secondary `6/6`, and
  the v8.12 visible probe `14/14`; the first varied v8.12 case failed one frozen
  predicate at `13/14`, and the remaining cases were withheld without retry.
- The eighth physical run is the first retained two-basin behavioral success:
  local convergence/classification, one Gaussian fill, repulsive plus assisted
  escape, return to `SEARCH`, and stronger-light reacquisition. It stopped
  before a second convergence or `GOAL_HOLD` and passed `61/62` completeness
  checks, with the sole failure isolated to cross-topic shutdown evidence
  ordering. This is not complete second-extremum or broad physical acceptance.
- Historical failed runs, failed experiment versions, errata, and superseded
  procedures are evidence. They must remain visible and must not be deleted,
  silently shortened, or rewritten as successes.
- Heavy-Ball ESC is historical context only. Its archival files remain intact,
  but active V1 instructions must lead to GESC + Gaussian workflows.

## Existing implementation and evidence to reuse

Phase 10 will extend documentation owners only. It will not add a node,
package, message, topic, recorder, validator, algorithm fork, or dependency.

The report will reuse and reconcile:

- all design/specification/source-material entries in
  `DSIM_GESC_Gaussian_Codex_Implementation_Package/MANIFEST.md`;
- Phase 00 audit/map documents and the Phase 00-05 knowledge bridge;
- every saved phase Plan and implementation handoff, including Phase 05.5 and
  Phase 07.5 dependency bridges;
- Phase 08 statuses, checkpoints, contracts, manifests, gate results,
  validation reports, failure reports, errata, final reports, and handoffs;
- Phase 09 Plan, status, checkpoint, handoff, snapshot/transfer/parity evidence,
  physical-run repair reports, and eighth physical-run validation;
- current Git history and the live simulation source, tests, interfaces,
  configurations, launch graph, scenario runner, recorder, validator, and
  analyzer;
- the read-only physical snapshot for final selected-launch, wrapper, sensor,
  recording, evaluation, and configuration verification;
- retained run artifacts that are locally available, without rerunning an
  expensive matrix merely to recover context.

The sole recorder remains `ros2 run ros_esc record_run`; the sole validator
remains `ros2 run ros_esc validate_run`. `/odom` remains the sole algorithm
pose in physical mode; Vicon remains evaluation-only. Raw physical cost remains
`-V`, and raw sensing remains recorded when its controller weight is zero.

## Required structure of `FINAL_PROJECT_REPORT_V1.md`

The master report must contain, at minimum, the following sections in a clear
thesis-ready narrative followed by technical appendices:

1. **Document identity and V1 evidence boundary**
   - branch, final commit, date, repository/snapshot scope, version meaning,
     claim vocabulary, and how to navigate the report;
   - a prominent statement that V1 is frozen evidence and V2 is future work.
2. **Executive summary and final conclusions**
   - problem, approach, what was built, strongest supported results, failed
     objectives, and exact claims that are and are not supported.
3. **Research motivation and supplied source material**
   - Dr. Nili and Patrick discussions, transcripts, audio, whiteboards,
     consolidated decisions, light-field scope, future acoustic motivation,
     and separation of source statements from adopted engineering hypotheses.
4. **Requirements, assumptions, and decision traceability**
   - every implementation-package specification and major invariant;
   - provisional versus frozen policy; Level A/B/C treatment; deviations and
     evidence-backed amendments.
5. **Repository baseline and final architecture**
   - Phase 00 findings; package and owner map; before/after architecture;
   - Mermaid architecture/data-flow diagrams for simulation and physical paths;
   - legacy and robust-profile selection boundaries.
6. **GESC and robust Gaussian mathematics**
   - raw, Gaussian, affine, and augmented costs with signs/units;
   - GESC/filter/controller flow; basin sampling, weighting, center/covariance,
     quadratic model, depth/curvature, fill width/amplitude, residual-minimum
     validation, escalation, soft association, hard overlap, merge/revision,
     support/exit geometry, confidence, and numerical safeguards;
   - equations must map to current implementation owners and parameters.
7. **Hybrid state machine and safety behavior**
   - all states, weights, actions, transitions, timeouts, stale/invalid-data
     behavior, final-zero ordering, escape progress, assist, recenter, goal hold,
     failsafe, and physical manual-stop boundary;
   - Mermaid state diagram matching current V1 behavior.
8. **ROS 2 implementation reference**
   - nodes/classes/owners, launch graphs, profiles, topics, messages, QoS where
     material, entry points, configuration files, and simulation/physical
     parity;
   - exact raw versus augmented cost and every logged/derived signal.
9. **Complete parameter reference**
   - every robust-profile, fill, recorder, scenario, evaluator, analysis, and
     selected physical parameter that affects documented behavior;
   - owner, type, default/selected override, unit, valid range or constraint,
     simulation/physical applicability, and source path;
   - no default may be copied from an old bridge without live verification.
10. **Implementation chronology: Phases 00-10**
    - objective, changes, files/owners, tests, result, correction, limitation,
      handoff, and commit boundary for every phase;
    - include material subphases and amendments such as 05.5, 07.5, Phase 08
      versions/subphases, and Phase 09 M0-M8L plus the eighth-run boundary.
11. **Simulation scenarios, methods, and complete V1 results**
    - scenario runner and recording methodology; deterministic seeds and
      evidence rules; development versus acceptance denominators;
    - chronological table for every Phase 08 experiment version and material
      probe/report, including failures, contamination, corrections, early
      stops, withheld cases, selected successes, and broad-readiness result;
    - selected trajectory/cost/metric artifact paths where retained.
12. **Physical integration, commissioning, and complete V1 results**
    - snapshot/backup/manifest/transfer/parity procedure; selected hardware and
      launch/data architecture; operator workflow and safety boundaries;
    - chronological table for all retained physical attempts, diagnoses,
      repairs, check-only results, motion/no-motion outcomes, recording status,
      and remaining limitations;
    - detailed eighth-run result, including the narrower behavioral claim and
      `61/62` evidence-order limitation.
13. **Recording, analysis, and artifact products**
    - sqlite3 bag as authority; metadata/configuration provenance; completeness
      and final-zero checks; CSV compatibility exports; analysis tables, plots,
      summaries, failure analysis, and storage/retention rules.
14. **Testing and validation evidence**
    - focused and global totals by phase, known inherited lint baseline,
      builds, runtime probes, skips, deselections, unexecuted checks, failures,
      and exact separation of infrastructure completeness from behavior.
15. **Verified operating instructions**
    - prerequisites, build/source commands, robust simulation launch and
      scenario commands, recorder/validator/analyzer commands, selected physical
      operator procedure, shutdown, retained output locations, and recovery;
    - physical commands are instructions only and are not executed by Phase 10.
16. **Backward compatibility and migration**
    - legacy default/profile, preserved topics/arrays/wrappers/configurations,
      Heavy-Ball archival boundary, robust opt-in behavior, and how V1 users
      select the correct path.
17. **Reproducibility checklist**
    - exact commit/dirty state, dependencies/environment, build, parameters,
      scenario/run IDs, seeds, artifacts, validation commands, expected outputs,
      failure preservation, and unavailable-artifact labeling.
18. **Limitations, threats to validity, and unsupported claims**
    - model and calibration limits; selected layouts; wall/reflection/shadow/
      noise/delay/source-count coverage; odometry/evaluation-frame limits;
      broad simulation and physical readiness failures; incomplete physical
      second-extremum evidence; inherited technical debt; and external artifact
      availability.
19. **Future V2 boundary**
    - evidence-backed unresolved robustness questions and candidate study areas;
    - explicit statement that the future
      `feature/gesc-gaussian-robustness-v2` branch begins from the completed V1
      closeout and requires new predeclared Plans and gates;
    - no V2 result, readiness, or implementation claim.
20. **Appendices**
    - complete implementation-package coverage index;
    - phase/handoff/validation/result index;
    - topic/message/parameter tables;
    - experiment/run/artifact table;
    - Git commit chronology and exact evidence paths;
    - glossary and acronym list.

## Files to create during Phase 10 implementation

- `docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.pdf`
  - Canonical reader-facing, LaTeX-typeset V1 report.
- `docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.tex`
  - Authoritative LaTeX source used to compile the PDF.
- `docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.md`
  - Repository-native content/audit companion described above.
- `docs/codex/gesc_gaussian/validation/phase_10_report_coverage.tsv`
  - Machine-checkable coverage proof with at least `artifact_class`, `path`,
    `authority`, `result_status`, `report_section`, and `notes` columns.
- `docs/codex/gesc_gaussian/validation/phase_10_documentation_validation.md`
  - Exact commands, link/coverage outcomes, command verification, skips,
    unavailable artifacts, diff checks, and final result.
- `docs/codex/gesc_gaussian/status/phase_10_status.md`
  - Created only with `init_phase_status.sh 10` at implementation start and
    updated continuously.
- `docs/codex/gesc_gaussian/checkpoints/phase_10_checkpoint.txt`
  - Created/updated through `checkpoint_phase.sh 10` at material milestones.
- `docs/codex/gesc_gaussian/handoffs/phase_10_handoff.md`
  - Final Phase 10 outcome, validation totals, Git state, limitations, V1
    closeout boundary, and future V2 branch instruction.

No new runtime source, node, package, message, topic, service, dependency,
recorder, validator, or analysis pipeline is justified or permitted.

## Files to modify during Phase 10 implementation

The following are the exact documentation entry points to update so the report
is discoverable and current:

- `README.md`
  - Replace the stub with a concise repository entry point, supported-claim
    boundary, package map, build/use links, and prominent V1 report link.
- `EXPERIMENT_STORAGE.md`
  - Reconcile simulation/physical V1 run roots, authoritative bag/derived CSV
    roles, retention, and report evidence references without moving raw data
    into Git.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/README.md`
  - Mark the V1 implementation-package outcome and link the final report.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md`
  - Replace stale Phase 09 “current” checkpoints with a compact V1 closeout and
    navigation path while retaining superseded details as history where useful.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/00_MASTER_IMPLEMENTATION_PLAN.md`
  - Record the exact Phase 10 V1 report deliverable and final result boundary;
    preserve earlier phase intent versus outcome distinctions.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/01_RESEARCH_DECISIONS_AND_ASSUMPTIONS.md`
  - Add the V1 evidence/claim closure and future-V2 versioning boundary without
    changing historical decisions.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/06_TEST_MATRIX_AND_ACCEPTANCE_GATES.md`
  - Add the terminal V1 gate outcome: failed broad readiness, qualified selected
    evidence, and exact nonclaims.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/09_RISK_REGISTER.md`
  - Reconcile risks with final V1 evidence and mark realized, mitigated,
    remaining, and V2-future risks.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/10_PHYSICAL_EXPERIMENT_READINESS.md`
  - Reconcile the operator checklist with the final M8L/eighth-run evidence,
    preserved manual `Ctrl+C`, and remaining acceptance limitations.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/10_documentation_PLAN.md`
  - Record `FINAL_PROJECT_REPORT_V1.md` as the required master-report output so
    the durable package contract matches this approved Plan.
- `DSIM_GESC_Gaussian_Codex_Implementation_Package/prompts/10_documentation_IMPLEMENT.md`
  - Add the exact V1 report and coverage-validation requirements for durable
    reproducibility of the Phase 10 workflow.
- `docs/codex/gesc_gaussian/implementation_sequence.md`
  - Reconcile stale Phase 09 state, specify final Phase 10 execution, and link
    the V1 report.
- `docs/codex/gesc_gaussian/interface_map.md`
  - Update the final live owner/interface map, including simulation versus
    selected physical and algorithm versus evaluation boundaries.
- `docs/codex/gesc_gaussian/topic_dictionary.md`
  - Verify and document the complete final topic/message/parameter surface.
- `docs/codex/gesc_gaussian/recording_runs.md`
  - Reconcile simulation and selected physical recording, validation, CSV,
    shutdown, artifact, and analysis instructions.
- `docs/codex/gesc_gaussian/test_commands.md`
  - Append exact Phase 10 documentation/coverage/link/command validation and
    final totals without rewriting earlier test history.
- `ros2_ws/src/ros_esc/README.md`
  - Add the current GESC + Gaussian owner/profile, recording/analysis entry
    points, compatibility boundary, and report links while preserving general
    package history.
- `ros2_ws/src/ros_esc_interfaces/README.md`
  - Document the final typed interface set and point to the exhaustive report/
    dictionary.
- `ros2_ws/src/turtlebot3_rotating_sensor/README.md`
  - Document the verified robust simulation entry points and separate legacy
    examples; remove Heavy-Ball from the active GESC + Gaussian path without
    deleting historical material.
- `writing/README.md`
  - Add the thesis-facing V1 report as the canonical project summary and label
    older writing artifacts by scope.

The Phase 00 audits, prior Plans, handoffs, checkpoints, validation/failure
reports, machine-readable gate results, source material, and retained run
evidence are immutable inputs. Do not edit them merely to make the final report
look consistent. If one contains a stale “current” statement, explain its
historical timestamp and superseding source in V1 documentation instead.

If implementation discovers a stale active document outside the exact list
above, stop that edit and record a bounded Plan amendment with the path,
contradiction, and reason before modifying it.

## Public interfaces and parameters

Phase 10 changes no ROS or runtime interface. It adds only documentation
interfaces:

- canonical V1 report path:
  `docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.md`;
- coverage proof:
  `docs/codex/gesc_gaussian/validation/phase_10_report_coverage.tsv`;
- Phase 10 validation/status/checkpoint/handoff paths listed above.

No topic, message, service, action, parameter, default, sign, unit, rate, launch
argument, command-line option, data format, package dependency, or runtime
owner may change. The Implement chat must derive the documented parameter
reference from current launch/config/source definitions and distinguish:

- legacy default versus `robust_gaussian_v1` opt-in;
- canonical defaults versus selected Phase 08/09 overrides;
- simulation-only, physical-only, evaluation-only, and shared parameters;
- raw sensor value, raw minimization cost, normalized score, Gaussian/affine
  contributions, augmented cost, and command outputs;
- `/odom` algorithm pose versus Vicon evaluation evidence.

## Backward compatibility and migration

- Preserve `legacy` as the default wherever current source defines it.
- Preserve all legacy topics, arrays, wrappers, launch files, configurations,
  and historical documents; clearly route new readers to the robust V1 path.
- Preserve Heavy-Ball content as labeled archive/history, not active GESC +
  Gaussian instruction.
- Preserve raw-cost sign/units and every simulation/physical semantic boundary.
- Preserve failed and superseded evidence exactly; use links and dated
  supersession notes rather than rewriting it.
- No current user must migrate runtime code because Phase 10 is documentation
  only.
- Future V2 work starts from the V1 closeout commit on a new branch and creates
  versioned evidence. It must not overwrite `FINAL_PROJECT_REPORT_V1.md`.

## Implementation sequence

### M0 — initialize and freeze the documentation evidence boundary

1. Reread `AGENTS.md`, this Plan, the Phase 10 prompts, Phase 09 status/handoff,
   Phase 08 final reports/handoffs, and the Phase 00-05 bridge.
2. Inspect `git status --short --branch`, `git diff --stat`, relevant diffs, and
   recent commits. Stop for overlapping user changes.
3. Run:

   ```bash
   DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 10
   DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 10 implement
   ```

4. Record branch, HEAD, dirty state, available repositories/snapshot, and the
   exact authoritative evidence hierarchy in Phase 10 status.
5. Build the initial coverage inventory from the package manifest, Git-tracked
   phase artifacts, live source/launch/config/tests, Git history, and retained
   experiment paths. Do not write to or mount the Pi.

Checkpoint after the evidence inventory is reviewable. A missing source needed
for a material numerical claim stops that claim, not unrelated documentation;
mark it unavailable instead of reconstructing data from memory.

### M1 — reconcile source of truth and classify every outcome

1. Resolve active versus historical statements across current source, Git,
   handoffs, statuses, final reports, and package specifications.
2. Populate `phase_10_report_coverage.tsv` with one row per package-manifest
   entry, phase Plan/handoff/status/checkpoint, material validation artifact,
   experiment version/run, and final implementation owner.
3. Assign explicit status and authority to every result. Never blend development,
   selected demonstration, formal acceptance, infrastructure completeness, or
   broad readiness.
4. Record discrepancies such as stale M8E/M8L navigation text versus the
   eighth-run evidence; preserve original artifacts and choose the superseding
   source transparently.
5. Audit the exact robust parameter surface from live source/config/launch,
   including selected V1 overrides and physical evaluation-only fields.

Checkpoint after all coverage rows have a report destination and unresolved
claim gaps are listed. Any unresolved cost sign/unit, control ownership,
simulation/physical parity, or evidence-status conflict is Level A and stops
drafting the affected claim.

### M2 — write architecture, methods, interfaces, and parameter chapters

1. Draft report Sections 1-9 using current owners and source-backed equations.
2. Add Mermaid simulation architecture, selected physical architecture, data
   flow, and state-machine figures.
3. Map each equation and state transition to implementation owner and parameter.
4. Complete topic/message/logged-signal and parameter tables.
5. Update interface/topic/ROS package documentation from the same verified
   inventory; do not create parallel explanations with conflicting defaults.

Checkpoint after the technical reference is internally linked and source-
traceable. No runtime edit is allowed to “make documentation true.”

### M3 — write the complete chronology and results chapters

1. Draft the Phase 00-10 chronology.
2. Add exhaustive Phase 08 version/probe/result tables with all failures,
   corrections, selected successes, early stops, and withheld cases.
3. Add exhaustive Phase 09 milestone/run/result tables, including zero-motion,
   partial-motion, recorder/evidence failures, repairs, check-only outcomes, and
   eighth-run behavioral success.
4. Add testing totals, skips/deselections, inherited lint debt, artifacts, and
   commit boundaries without summing incompatible denominators.
5. Add selected plots/trajectory/cost artifact links where retained and
   verified. Do not regenerate expensive runs or fabricate absent figures.

Checkpoint after a coverage audit shows every result row has a report section,
status, and evidence path.

### M4 — write operating, reproducibility, compatibility, limitation, and V2 chapters

1. Draft report Sections 13-20, including exact verified commands and expected
   outputs.
2. Update root/package/ROS READMEs, storage guidance, package navigation,
   physical checklist, and thesis-writing index.
3. State all nonclaims and threats to validity prominently.
4. Record the future `feature/gesc-gaussian-robustness-v2` branch boundary and
   unresolved study questions without implementing or promising V2 outcomes.
5. Check that every active instruction uses GESC + Gaussian and that Heavy-Ball
   links are historical only.

Checkpoint after a new reader can navigate from root `README.md` to the V1
report, reproduce supported offline/simulation workflows, understand the
physical operator procedure, and identify all unsupported claims.

### M5 — validate and close V1 documentation

1. Generate the complete LaTeX source, compile
   `FINAL_PROJECT_REPORT_V1.pdf`, and inspect extracted text, document
   metadata/fonts, and representative rendered pages.
2. Run every documentation, coverage, command, link, diff, and repository check
   below.
3. Correct documentation-only defects. Any proposed runtime/source correction
   is outside Phase 10 and stops for user review.
4. Write `phase_10_documentation_validation.md` with exact outputs, skips,
   unavailable evidence, and limitations.
5. Close Phase 10 status, run `checkpoint_phase.sh 10`, and write
   `phase_10_handoff.md`.
6. Record the exact V1 closeout Git boundary and recommend—but do not create—the
   future V2 branch from that completed commit.
7. Inspect final diff and Git status. Do not commit unless the user separately
   authorizes a commit.

## Tests and acceptance criteria

### Context and required-document checks

```bash
timeout 30s DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 10 implement
timeout 30s DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_required_docs.sh
```

Both must pass. The implement validator must resolve this saved Plan and a
nonempty Phase 10 status with required headings.

### Coverage checks

Use a bounded read-only checker to verify:

- every nonblank manifest entry in
  `DSIM_GESC_Gaussian_Codex_Implementation_Package/MANIFEST.md` has exactly one
  coverage row;
- every `docs/codex/gesc_gaussian/plans/phase_*_plan.md`,
  `handoffs/phase_*_handoff.md`, status, checkpoint, and validation report has a
  coverage row or an explicitly grouped row with a lossless pattern and count;
- each material Phase 08 experiment version and Phase 09 physical run has a
  report result row with status and evidence path;
- all required report section headings exist;
- no coverage row has an empty authority, result status, or report section.

Record exact item counts and failures in
`phase_10_documentation_validation.md`. Grouping may reduce appendix length but
must not hide individual failed/partial results.

### Markdown-link and retained-path checks

Run a bounded local Markdown checker over every changed Markdown file. It must:

- resolve repository-relative links and anchors;
- reject links to missing Git-side files;
- distinguish retained absolute external/run paths from clickable repository
  links and label unavailable external artifacts honestly;
- verify balanced fenced code/Mermaid blocks;
- verify that root and package READMEs link to the canonical
  `FINAL_PROJECT_REPORT_V1.pdf` and identify the `.tex` and `.md` companions.

The command and exact pass/fail counts must be retained in the Phase 10
validation record. No network checker is required for historical external URLs.

### Live interface, parameter, and command verification

Verify documented names against source rather than prose with bounded `rg`,
structured YAML/XML/JSON parsing, `ros2 interface show`, installed entry-point
inspection, and launch argument inspection where the current environment
supports them. At minimum verify:

- all six robust typed messages;
- simulation and selected physical launch filenames/arguments;
- `record_run`, `validate_run`, scenario-runner, and analysis entry points;
- every parameter table row against its source/config owner;
- raw physical `-V`, `/odom` algorithm pose, evaluation-only Vicon, manual
  `Ctrl+C`, and final-zero semantics.

Any command not executable in the current environment must be reported as
unexecuted and sourced to its last retained successful evidence. Do not call it
currently verified.

### Claim-specific acceptance checks

Search the final active documentation and manually review surrounding context
to ensure:

- no statement calls V1 broadly simulation-ready or broadly physical-ready;
- no statement calls the eighth run a complete second-extremum acceptance;
- v8.10 `11/11`, v8.11 `6/6`, v8.12 visible `14/14`, varied `13/14`, withheld
  cases, and Phase 09 `61/62` are labeled with their correct scopes;
- no failed or partial run is silently omitted from result tables;
- no Vicon/GPS/evaluator geometry is described as a physical control input;
- no V2 behavior/result is stated as implemented;
- Heavy-Ball is absent from active GESC + Gaussian instructions except labeled
  historical/archive references.

### Diff, syntax, and repository checks

```bash
git diff --check
git diff --stat
git status --short --branch
```

Markdown/YAML/TSV structure must parse, added links must resolve, and no
unintended runtime source or retained historical evidence may be modified.

Because the declared Phase 10 change set is documentation-only, a new Gazebo
run, physical run, expensive matrix, full ROS build, or full ROS regression is
not required. If implementation changes runtime code, launch behavior, config
values, or interface definitions, stop: that exceeds this Plan and requires a
new reviewed amendment plus proportional tests.

### Final acceptance result

Phase 10 passes only when:

- the exact V1 PDF, LaTeX source, Markdown companion, coverage, validation,
  status, checkpoint, and handoff artifacts exist and are nonempty;
- all required chapters and indexes are complete;
- all package-manifest entries and material result artifacts are accounted for;
- active READMEs lead to the report and use current commands;
- links, structure, coverage, claim-specific searches, and `git diff --check`
  pass;
- every skip/unavailable command/artifact is explicit;
- no runtime, physical, historical-evidence, or V2-scope mutation occurred.

## Risks and stop conditions

- **Level A — stop:** cost sign/unit conflict; controller/recorder/topic owner
  conflict; simulation/physical algorithm divergence; `/odom`/Vicon role
  conflict; proposal to weaken or relabel a failed gate; missing authority for a
  material conclusion; overlapping user changes; physical/Pi action; runtime
  source change; or V2 implementation/branch creation.
- **Level B — document and continue:** bounded stale link, command spelling,
  current-navigation, parameter-table, supersession-label, or report-coverage
  correction that preserves evidence and runtime behavior.
- **Level C — honest documentation outcome:** a required historical artifact or
  command is unavailable. Retain the gap, identify the last authoritative
  evidence, mark the claim unverified/currently unavailable, and continue other
  documentation. Do not rerun an expensive experiment solely to fill the gap.
- Do not rewrite prior Plans, handoffs, statuses, reports, manifests, bags, or
  results to produce a cleaner narrative.
- Do not edit the physical snapshot or mounted Pi. If snapshot inspection is
  unavailable, rely on retained hashes/handoffs and label the verification date.
- Do not convert the report into a V2 design document. Future-work discussion
  is bounded to evidence-backed questions and prerequisites.

## Implementation-time verification

Before editing, the Implement chat must verify:

1. the current branch is still `feature/gesc-gaussian-robustness-v1` and no V2
   branch has been entered;
2. current HEAD, working-tree ownership, and any user modifications;
3. this Plan, Phase 10 status, and `validate_phase_context.sh 10 implement`;
4. the latest Phase 08 and Phase 09 evidence, especially any post-Plan amendment
   or run that supersedes the current eighth-run boundary;
5. the exact package manifest and all currently tracked phase artifacts;
6. live source owners, launch names, entry points, message definitions, and
   parameter defaults;
7. physical snapshot availability and freshness before using it as current
   evidence; no mount or transfer is authorized;
8. local availability of retained run artifacts before claiming direct
   revalidation;
9. the inherited lint/test baseline versus focused behavior results;
10. that the proposed final diff contains documentation and Phase 10 durable
    artifacts only.

A contradiction must be recorded with exact repository evidence. The agent may
make a bounded documentation correction under Level B, but it must stop for any
runtime, objective, safety, ownership, evidence-integrity, or V2-scope change.
