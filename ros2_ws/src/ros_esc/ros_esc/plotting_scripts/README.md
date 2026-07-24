# Offline plotting and bag analysis

This folder contains the repository's existing plotting helpers and the
standard Phase 07 analysis owner.

Analyze one Phase 05/06 run directory after building and sourcing the
workspace:

```bash
ros2 run ros_esc analyze_run RUN_DIRECTORY
```

The default output is `RUN_DIRECTORY/analysis/phase07`. Use `--output-dir`,
`--channel-index`, or `--sync-tolerance-sec` to select a new output location
or explicitly override the values captured in `resolved_parameters.yaml`.
Existing output directories are rejected; raw bags and the root
`completeness.json` are never rewritten.

The analyzer:

- reads the run's sqlite3 bag and real resolved message types;
- retains bag, typed/header ROS, and legacy source timestamps in CSV;
- uses cost samples as synchronization anchors;
- matches pose, source cost, GESC, and control samples by nearest typed stamp;
- matches algorithm state causally;
- never interpolates, extrapolates, or forward-fills missing critical data;
- writes eleven CSV tables, eight separate PNG figures,
  `summary_metrics.json`, `summary_metrics.csv`, and
  `analysis_completeness.json`.

Every metric contains `value`, `status`, `unit`, `reason`, and `provenance`.
Statuses are `valid`, `not_applicable`, `unavailable`, or `invalid`. A readable
failed experiment still exits successfully after producing partial or invalid
evidence; only analysis-process failures return exit code 2.

Aggregate already-analyzed runs with:

```bash
ros2 run ros_esc summarize_matrix \
  RUN_OR_ANALYSIS_DIRECTORY [...] \
  --output-dir NEW_MATRIX_OUTPUT
```

This produces `matrix_summary.csv` and `matrix_summary.json`. It does not run
per-run analysis, change individual summaries, or replace Phase 05 validation
or Phase 08 acceptance.
