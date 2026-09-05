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
