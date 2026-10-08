# V3 master report plan

Authorized by the user's 2026-10-05 request for a complete teaching and project
report modeled on `FINAL_PROJECT_REPORT_V1.pdf`. This is documentation work;
it does not change algorithm tuning or authorize a new experiment or deployment.

## Source and scope

- Baseline: clean `refactor/esc-v3` at `2be0bad`, with current source, interfaces,
  selected profiles, launch graph, tests and retained experiment evidence.
- Read accepted refactor plan/status, active usage/architecture/environment
  guidance, Gazebo plan/status, physical deployment records and the current
  2026-10-01 physical fresh-chat handoff before authoring.
- Explain the whole active repository and three ROS packages, the supporting
  numerical library, exact V3 equations and runtime state, parameters,
  observation/time/worker contracts, original methods, recording and analysis.
- Preserve V1/V2 and failed evidence. Distinguish current V3 from historical
  Phase 08 experiment versions also named v3.
- Record the user's decision that the simulation/Gazebo baseline is satisfactory
  while describing the scope of retained selected-case evidence precisely.
- Describe latest physical testing and undeployed suggestions without claiming
  fresh remote inspection or physical Gaussian escape qualification.

## Deliverables

- `../FINAL_PROJECT_REPORT_V3.md`, reader-editable source and source citations.
- `../FINAL_PROJECT_REPORT_V3.tex` and `../FINAL_PROJECT_REPORT_V3.pdf`, a
  synchronized typeset report with navigation, equations and explanatory figures.
- `report_coverage.tsv`, a file-level source/evidence audit with section mapping.
- `report_validation.md`, exact authoring and verification receipts and limits.
- Add concise links to existing documentation navigation.

## Acceptance

1. Explain every stage from a measured sensor observation to base command and
   retained evidence, with symbol definitions, rationale, worked examples and
   practical reading/teaching routes.
2. Verify reported defaults against actual selected configuration owners;
   distinguish Gazebo, physical selection, and helper defaults.
3. Audit material claims against source/tests or retained run records. Keep
   software, behavior, completeness and physical stopping evidence distinct.
4. Check source paths and line bounds, coverage, Markdown/code fences, figures,
   PDF text, bookmarks and all rendered pages; correct layout defects.
5. Inspect Git diff and record exact checks. No algorithm modification, costly
   matrix rerun, hardware action, or commit is included in this request.

The accepted V3 plan/status/diff/receipt checkpoint equivalent applies; retained
phase scripts have no V3 support and are not used to relabel old acceptance.

## Evidence storage

Intermediate chapters, figures, renderer logs and visual QA are retained in
`/home/mattb/Experiments/GESC-Gaussian/v3/report_20261005/` outside Git.

