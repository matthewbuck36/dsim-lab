# Project documentation

The implementation package and the former `writing/` contents are collected
here. Use these locations for new documentation references:

- [Implementation package](DSIM_GESC_Gaussian_Codex_Implementation_Package/START_HERE.md):
  specifications, phase prompts, templates, source material, and workflow tools.
- [Phase records](codex/gesc_gaussian/implementation_sequence.md): plans,
  statuses, handoffs, and retained validation evidence.
- [Simulated brightness percentages](simulation_brightness.md): new light
  settings, nominal 1600-lumen mapping, and historical compatibility.
- [Gaussian light-source sweep report](gaussian_fill_light_source_sweep_report.md).
- [GESC Gaussian source-fix report](gesc_gaussian_source_fix_report.md).
- [Heavy-Ball baseline report](heavy_ball_PDE_ESC/baseline_hb_report/README.md)
  and [archive](heavy_ball_PDE_ESC/archive/README.md).
- [Relocation record](documentation_relocation.md): path mapping and validation.

The old root shortcuts have been removed. Historical reports, commands, and
manifests may retain those old paths; use the [path mapping](documentation_relocation.md)
to locate their targets under `docs/`. Phase outcomes are unchanged;
the latest Phase 09 status still records physical validation outstanding after M8O.

## GESC + Gaussian V2 kickoff

On 2026-09-08, `feature/gesc-gaussian-robustness-v2` began from the final V1
commit `1af67c6` to re-attempt Gaussian algorithm robustness. This kickoff
records the branch start; the V2 plan and acceptance criteria remain to be
defined. V1 reports and retained results remain the inherited evidence
baseline, and no V2 implementation or validation result is claimed yet.

## Current GESC + Gaussian V1 report

The complete V1 project narrative and evidence boundary is the LaTeX-typeset
[FINAL_PROJECT_REPORT_V1.pdf](codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.pdf).
Its [LaTeX source](codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.tex) and
[Markdown audit companion](codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.md)
are retained beside it. This set is the authoritative report for the GESC +
Gaussian implementation and its Phase 00-10 results; source-facing package
READMEs link back to the same record.

The `heavy_ball_PDE_ESC/` material listed below is a preserved historical
baseline/archive. It is not the active `robust_gaussian_v1` workflow and should
not be used to characterize V1 robustness or acceptance. V1 supports selected
two-basin demonstrations, not broad simulation or physical robustness and not
a formally complete second-extremum physical run.

This folder holds written deliverables outside of `ros2_ws`.

Use this area for reports, drafts, figures intended for papers/writeups, and
future writing artifacts that do not need to live inside a ROS package.

The former `writing/` reports, scenarios, figures, manifests, and work logs
retain their internal directory structure under `heavy_ball_PDE_ESC/`.
