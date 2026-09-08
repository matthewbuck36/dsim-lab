# Documentation relocation

This maintenance change consolidates documentation under `docs/`. It does not
reopen a research phase or change any experiment outcome. The August 18 M8O
physical validation boundary remains as recorded in the Phase 09 status.

| Previous location | Canonical location |
|---|---|
| `DSIM_GESC_Gaussian_Codex_Implementation_Package/` | `docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/` |
| `writing/README.md` | `docs/README.md` |
| `writing/gaussian_fill_light_source_sweep_report.md` | `docs/gaussian_fill_light_source_sweep_report.md` |
| `writing/gesc_gaussian_source_fix_report.md` | `docs/gesc_gaussian_source_fix_report.md` |
| `writing/heavy_ball_PDE_ESC/` | `docs/heavy_ball_PDE_ESC/` |

## Root shortcut removal — 2026-09-08

At the user's request, the two root compatibility symlinks have now been
removed. Their target directories and contents remain under `docs/`; this
step moves or deletes no document payload. The clean starting commit was
`43f5520`. This is repository maintenance, not a reopened research phase.

The audit found one active dependency on an alias: `validate_phase_context.sh`
still assigned its package directory to the old root path. It now uses
`$ROOT/docs/DSIM_GESC_Gaussian_Codex_Implementation_Package`. The status
initializer already used that location. Agent instructions, documentation
navigation, and the baseline Heavy-Ball report README now reflect the removal.
No current ROS/Gazebo source, launch, or build dependency on either alias was
found in the tracked-file audit.

The intentional compatibility impact is limited to historical paths:

- Old shell commands, saved bookmarks, coverage-table paths, and commands
  copied from phase records need the prefix substitutions in the table above.
- Five source-material/readiness links in the frozen V1 report now require
  manual path translation. In its Markdown/LaTeX source, replace the leading
  `../../../DSIM_GESC_Gaussian_Codex_Implementation_Package/` with
  `../../DSIM_GESC_Gaussian_Codex_Implementation_Package/` when locating a
  target. The PDF retains the same old link destinations. The frozen report
  set remains byte-identical.
- Archived Heavy-Ball scenario JSON files and historical report commands
  retain `~/dsim-lab/writing/...` paths. For any future reuse, translate these
  to `~/dsim-lab/docs/...` in a working copy. These scenarios are provenance
  for a retired runner, not the current simulation workflow.

All five report-link targets remain available:

- [Source-material README](DSIM_GESC_Gaussian_Codex_Implementation_Package/source_material/README.md)
- [Gaussian-escape whiteboard](DSIM_GESC_Gaussian_Codex_Implementation_Package/source_material/whiteboard_gaussian_escape.jpg)
- [Switchable-cost/recenter whiteboard](DSIM_GESC_Gaussian_Codex_Implementation_Package/source_material/whiteboard_switchable_cost_recenter.jpeg)
- [Consolidated meeting decisions](DSIM_GESC_Gaussian_Codex_Implementation_Package/source_material/CONSOLIDATED_MEETING_DECISIONS.md)
- [Physical-readiness document](DSIM_GESC_Gaussian_Codex_Implementation_Package/10_PHYSICAL_EXPERIMENT_READINESS.md)

Validation after removal:

- Strict Phase 08, 09, and 10 implementation-context checks pass using the
  three canonical commands recorded below. The Phase 00 required-documents
  check and context-bundle generation also pass.
- All five package shell tools pass `bash -n`.
- The 2,063 tracked regular files present before removal remain present;
  SHA-256 comparison confirms all except the six intended maintenance files
  are unchanged, including all ROS source and frozen research evidence.
- The before/after local-link audit finds ten newly unresolved references:
  the same five historical targets in each of the frozen Markdown and LaTeX
  reports. No other previously resolving Markdown/LaTeX link is lost.
- `git diff --check` passes. No build, ROS graph, Gazebo experiment, physical
  snapshot edit, or hardware operation is needed for this cleanup.

Current audit artifacts are retained under `/tmp/dsim_remove_doc_aliases/`:
`before.json`, `after.json`, `phase08.log`, `phase09.log`, `phase10.log`, and
`context_bundle.txt`. These temporary artifacts supplement this durable record.

On 2026-09-08, the user authorized committing this cleanup as the final change
to `feature/gesc-gaussian-robustness-v1`. The commit containing this closure
note is the final branch boundary; resolve its hash from Git. Future work
belongs on a separate branch. Historical phase reports, statuses, checkpoints,
failed results, and outstanding physical-validation requirements remain
unchanged; this administrative closure makes no new research-readiness claim.

## Original relocation record (before shortcut removal)

The following describes the initial move and its validation at that time.
Its compatibility-link claims and old-path invocation no longer describe the
current checkout; use the current mapping above.

All 58 tracked implementation-package files and 74 tracked writing files were
moved. There were no destination-name conflicts. The root package path is a
relative symlink to its canonical directory; `writing` is a relative symlink
to `docs`. These preserve local historical paths, including links embedded in
the frozen V1 PDF and paths in archived commands/manifests. New references use
the canonical locations. Git web viewers may display symlinks as files; use
the canonical documentation navigation when browsing online.

Updated maintained references include root/package navigation, phase prompts,
the context-validator package path, the status-initializer template path,
and the older Heavy-Ball analysis script's default manifest/output locations.
The frozen V1 PDF/LaTeX/Markdown, phase plans/statuses/handoffs/checkpoints,
validation evidence, and historical writing payloads remain byte-identical,
except for the former writing README, which now provides the docs index.

The pre-move checkout was clean at `eeabd91`. A recoverable local archive and
before-file hashes are retained at
`/tmp/dsim_docs_relocation_audit/documentation_before.tar.gz` and
`/tmp/dsim_docs_relocation_audit/before_hashes.json`. The archive is temporary;
tracked originals also remain recoverable from Git. No commit is created by
this maintenance task.

Validation passed:

- All 2,219 previously tracked files are present at their original or mapped
  locations. All frozen phase artifacts and historical writing payloads retain
  their original SHA-256 hashes. The 39 content changes are confined to
  maintained navigation, prompts, helper paths, and the analysis default paths.
- The local Markdown audit checked 275 links in previously linked documents
  with zero newly broken links. All five relocated-target links in the frozen
  V1 LaTeX report resolve through the compatibility paths.
- All five package Bash tools pass `bash -n`. Strict implementation-context
  checks pass for Phases 08, 09, and 10; the Phase 00 required-documents check
  passes; the old package-path invocation still works.
- Context-bundle generation passes with output outside the repository.
- The status initializer creates a populated status and preserves an existing
  status; checkpoint generation passes in an isolated temporary Git fixture.
  No live phase status or checkpoint was regenerated.
- The analysis script parses, its default manifest and figures directory
  exist, and its `--help` invocation passes without generating report products.

Commands (from the repository root):

```bash
timeout 30 bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 implement --strict-history
timeout 30 bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 09 implement --strict-history
timeout 30 bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 10 implement --strict-history
timeout 30 bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_required_docs.sh
timeout 30 bash DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 10 plan
timeout 30 bash docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/make_codex_context_bundle.sh /home/mattb/dsim-lab /tmp/dsim_docs_relocation_audit/context_bundle.txt
timeout 30 python3 /tmp/dsim_docs_relocation_audit/check_helpers.py
timeout 30 python3 ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/analysis/analyze_baseline_hb_logs.py --help
git diff --check
```

Hash/link/AST results are retained in
`/tmp/dsim_docs_relocation_audit/validation.json`; fixture results are in
`/tmp/dsim_docs_relocation_audit/helper_fixture_result.json`. The exact relocation
script is `/tmp/dsim_docs_relocation.py`. No ROS build, Gazebo run, experiment
rerun, snapshot edit, or hardware operation was required or performed.
