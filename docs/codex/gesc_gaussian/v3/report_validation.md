# V3 master report validation and handoff — 2026-10-05

**Status: COMPLETE / PASS for the documentation milestone.** This closes the
[report plan](report_plan.md), using the accepted V3 plan/status/diff/receipt
checkpoint equivalent. It is not a new research experiment or physical
qualification. The user's simulation/Gazebo acceptance is recorded as a project
decision and supported by the retained selected affine-2.0 run.

## Delivered scope

- [Reader-facing PDF](../FINAL_PROJECT_REPORT_V3.pdf): 55 letter-size pages,
  62 navigation bookmarks, 42 display equations and seven vector figures.
- [Editable narrative](../FINAL_PROJECT_REPORT_V3.md): approximately 27,600
  whitespace-delimited words, repository/package architecture, all eight message
  schemas, selected settings, original methods, V3 mathematics and state, a
  full observation-to-command walkthrough, teaching descriptions, questions and
  worked study exercises.
- [LaTeX source](../FINAL_PROJECT_REPORT_V3.tex), three authoring helpers in
  `report_support/`, and seven SVG/PDF figure pairs plus generator in
  `report_figures/`.
- [File coverage](report_coverage.tsv): 391 attributed source/evidence rows,
  285 distinct files, including 91 explicitly inventory-only files. Counts are
  file/claim accounting, not independent experiments. The report states what
  was substantively reviewed and what was inventoried.
- [Parameter index](report_parameters.tsv): 839 source-attributed entries,
  comprising 774 JSON leaves and 65 defaults/declarations. Effective runtime
  precedence is explained separately; the index is not executable configuration.
- Updated `docs/README.md` navigation. V1 Markdown, LaTeX and PDF remain byte
  identical to the baseline Git versions.

All required acceptance items in the report plan passed: causal implementation
explanation; selected-configuration ownership; source/test/retained-evidence
audit; source paths, parameters and final rendered layout; bounded checks and
documentation-only Git scope.

## Baseline and authority

Started from a clean `refactor/esc-v3` at
`2be0bad33a314f7b383d65f4bab876d401b7c888`. Current source, tests, selected JSON,
interfaces and launch graph take precedence over historical prose. Read the
accepted refactor plan/status, active architecture/usage/environment guides,
Gazebo plan/status, physical deployment records and the 2026-10-01 physical
fresh-chat handoff. Used frozen V1 as a breadth/style reference, while tracing
current V3 claims to present source and retained records. Memory supplied
teaching preferences, not unverified implementation claims.

Independent delegated reviews covered repository/architecture/configuration,
mathematics/state/code, and empirical/physical evidence. The author integrated
and checked their source citations and corrected configuration/call-site
ambiguities before final typesetting. Retained failures remain failed; historical
Phase 08 experiment versions named v3 are not presented as the current V3.

No algorithm code, selected tuning, physical workspace, firmware or deployment
was changed. No Pi access, hardware motion, new Gazebo run, expensive matrix,
commit or push was performed. The only new runtime verification was the bounded
local software suite, including its existing isolated localhost ROS tests.

## Exact software verification

Executed from `/home/mattb/dsim-lab`:

```bash
timeout 90s bash -c 'source /opt/ros/humble/setup.bash; source ros2_ws/install/setup.bash; export ROS_LOCALHOST_ONLY=1; python3 -m pytest -q ros2_ws/src/ros_esc/test --basetemp=/home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/software_test_artifacts' > /home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/current_software_tests.log 2>&1
```

**PASS: 311 tests, no skips, 21.81 s.** Pytest reported 372 inherited NumPy
matrix deprecation warnings. The process also reported a resource-tracker
cleanup warning about six semaphore objects at shutdown; the exact output is
retained. These warnings are not treated as physical or behavioral evidence.
The suite was not broadened or repeated after documentation-only figure/layout
changes. Artifacts are retained in `software_test_artifacts/` under the external
report evidence directory.

## Authoring and structural checks

External authoring/QA root throughout this receipt:

`/home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/`

Pandoc 3.8.2.1 and Tectonic 0.17.0 were retained in its `tools/` directory.
The final build command, from the repository root, was:

```bash
PANDOC_BIN=/home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/tools/pandoc-3.8.2.1/bin/pandoc \
TECTONIC_BIN=/home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/tools/tectonic \
REPORT_BUILD_DIR=/home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/build \
bash docs/codex/gesc_gaussian/v3/report_support/build_report.sh \
  > /home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/report_build.log 2>&1
```

The checked-in helper bounds Pandoc to 60 s and Tectonic to 180 s. It starts
no ROS, Gazebo or devices. **PASS:** final PDF/TeX synchronized with Markdown;
no overfull boxes, missing glyphs, undefined controls or undefined references.
Two nonfatal underfull-box warnings remain in the initial evidence-vocabulary
table; rendered text and spacing were inspected and are legible.

Initial authoring problems were corrected rather than hidden. The first
typesetting attempt failed on a Unicode approximation symbol in inline code
and exposed long-identifier table overflow. The Lua filter now renders math
symbols appropriately and wraps long literal paths. The first attempt remains
in `first_failed_typesetting.log`; it is an authoring failure, not a research
experiment result. Subsequent figure/float/listing polish corrected crowded
labels, excess figure-page whitespace and an empty listing border at a page
break.

Executed final structural/citation checks:

```bash
PYTHONPATH=/home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/python \
python3 /home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/validate_report.py
python3 /home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/final_architecture_audit.py
python3 /home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/final_documentation_audit.py
```

**PASS:** all 391 coverage hashes and attributed line bounds; 217 full/shorthand
inline citations resolve uniquely within bounds; all 839 parameter values match
their JSON pointers or exact Python AST declarations; 48 report-local links;
22 paired Markdown fence markers; 41 mapped empirical source IDs; PDF text,
55 nonempty pages and 62 bookmarks. No replacement characters were found.
Seven SVGs parse and each has its vector PDF counterpart. Figure-generator
Python syntax and authoring-helper Bash syntax pass. Navigation/plan/receipt
links and fences pass. `git diff --check` passes. No runtime file has a diff.

Exact machine receipts: `structural_validation.json`,
`final_architecture_audit.json`, and `final_documentation_audit.json`. The
structural receipt records final SHA-256 values for Markdown, TeX and PDF.
Large logs, test products, chapter drafts and page images stay outside Git.

Delivered artifact SHA-256 values:

```text
Markdown 00854e24bbebc20efbe9f11127ba12fdcfd46042f23a87eaa9e39da50373412d
LaTeX    21b27020afaa5e235a3008a4f7db7912dade0f720918a0db4181cace3d23284b
PDF      1350187bb8541d0062b3ba592819e6770c6022ca02a203cf7f3c641b8c3a0486
```

## Figure data and visual review

Figure regeneration command:

```bash
timeout 30s python3 docs/codex/gesc_gaussian/v3/report_figures/generate_figures.py
```

Five figures are explicitly explanatory schematics. The two measured trajectory
figures read these closed retained exports, rooted at
`/home/mattb/Experiments/GESC-Gaussian/v3/`:

- `affine_2_20260929T013558Z/analysis/csv/%2Fodom.csv` and
  `affine_2_20260929T013558Z/outcome_geometry.json` for the selected Gazebo route
  and fill exit circle. Annotated source coordinates were checked against that
  run's captured cost configuration; they are evaluator data, not controller input.
- `physical_runs/20260930T211613_989126Z-3555/analysis/csv/%2Fodom.csv` for the
  latest reviewed OpenCR-odometry route. No Vicon, lamp-centered radius or
  source-distance claim is added.

Final render command:

```bash
timeout 90s pdftoppm -r 100 -png \
  docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V3.pdf \
  /home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/delivery_pages/page
```

**PASS:** all 55 rendered pages inspected. The author reviewed pages 1–20 in
contact sheets and detailed views of the architecture/interface/parameter
pages; independent reviewers inspected pages 21–40 and 41–55 individually at
original resolution. The last architecture-label correction changed only
page 7; pixel comparison confirmed the other 54 pages identical to the fully
reviewed revision, and the author re-inspected final page 7. Equations, tables,
paths, captions, figures, headers, footers and pagination are readable without
clipping or label collisions. Figure-only pages carry full explanatory figures
and are not blank pages.

Receipts: `qa_math_pages_revised.md`, `final_qa_pages41_55.md`,
`final_render_comparison.json`, and `final_visual_qa.md`. The first two pin the
prior reviewed PDF; the comparison/final receipt pins the delivered version.

## Final handoff and limits

Report, companions and navigation are ready to read; no acceptance item remains
open for this documentation milestone. The worktree contains only the intended
report/authoring/receipt files and the documentation-navigation edit. No commit
was requested or made. The baseline HEAD and frozen V1 files remain unchanged.

The report preserves these practical boundaries:

- The selected Gazebo run demonstrates a fill, unassisted measured escape,
  restored searching and stronger-source vicinity. It is not a general global
  convergence or statistical robustness proof. Later shared software corrections
  postdate that run and have no new Gazebo behavioral run in the retained records.
- The latest physical floor run remains SEARCH-only, with no candidate/fill or
  Gaussian escape. Selected raised-wheel stopping observations are operator
  evidence within their tested scope, not quantified universal hardware stopping.
- Physical caps 0.05/0.30, affine 2.0, fixed 5 Hz, nominal 20 RPM, 54-degree
  calibration and angular gain 5.0 are the last verified selection. Proposed
  gain 7.5 and longer detector windows remain undeployed. No current remote
  process state is asserted.

Continue learning from the report's three-pass reading route, worked equations,
code walkthrough and study exercises. Any next physical work still starts from
the physical fresh-chat handoff and its separate authority/evidence boundary.
