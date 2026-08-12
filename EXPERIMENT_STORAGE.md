# Experiment Storage Protocol

Raw Gazebo and physical TurtleBot3 experiment data belongs outside this Git
repository under `~/Experiments`.

The canonical layout is:

```text
~/Experiments/
├── GESC-Gaussian/
│   └── runs/                           # managed simulation runs and suites
├── Gazebo-Simulations/
│   ├── Test_YYYY-MM-DD_HH-MM-SS/       # normal data-collection runs
│   ├── HBESC-Baseline-Tests/           # named Gazebo baseline campaign
│   └── Studies/
│       └── hbesc_gaussian_fill_study/  # Codex batch study and results
└── Physical-TurtleBot3/
    └── Jan-29-try-20260630T235703Z-3-001/
```

The selected Phase 09 physical wrapper uses a separate Pi-side managed root:

```text
${HOME}/turtlebot_rotating_sensor_tests/gesc_gaussian_two_source/
  <UTC-date>/<run-id>/
```

Why this is the canonical location:

- `gazebo.launch.xml` defaults `data_collection_filepath` to
  `~/Experiments/Gazebo-Simulations`.
- The inherited Gazebo bash wrappers pass the same path.
- `data_collection_node` creates a timestamped `Test_*` directory beneath the
  path supplied by the launch file.
- `ros2 run ros_esc record_run` defaults managed GESC/Gaussian work to
  `~/Experiments/GESC-Gaussian/runs` and creates a date/run-ID hierarchy.
- Keeping large, generated run data outside `dsim-lab` prevents accidental Git
  commits while keeping source, launch files, configs, and reusable analysis
  code in the repository.

For ordinary Gazebo runs, do not override `data_collection_filepath` unless a
campaign deliberately needs its own subdirectory. For batch studies, create a
named folder beneath `~/Experiments/Gazebo-Simulations/Studies` or route only
the generated results there.

The repository-level `/experiments/` path remains in `.gitignore` as a safety
guard, but no local experiment directory or compatibility link is required.
Old batch logs may record the former
`~/dsim-lab/experiments/hbesc_gaussian_fill_study` location; use the canonical
external study path shown above when adapting those commands. See
`~/Experiments/README.md` for the complete storage guide.

## V1 evidence authority and retention

The sqlite3 rosbag, resolved metadata/configuration/parameters, integrity and
completeness results, target/recorder console, and versioned scenario result
form one run record. Derived CSVs, summaries, and plots are reproducible views;
they do not replace the bag. Physical familiar-format CSVs are generated only
after clean bag finalization and remain subordinate to it.

Retain failed, partial, infrastructure-invalid, and successful run directories
under their original IDs. Never repoint a new execution at a closed Phase 08
root, overwrite a failed directory, or delete evidence merely because a later
version passed. Before any cleanup, inventory sizes/paths read-only and obtain
explicit deletion authority.

The Git-side evidence index is the LaTeX-typeset
[V1 final report](docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.pdf), with
its [Markdown audit companion](docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.md)
and
machine coverage in
[`phase_10_report_coverage.tsv`](docs/codex/gesc_gaussian/validation/phase_10_report_coverage.tsv).
The report records 56 retained Phase 08 roots currently available under the
managed simulation root and quotes exact Pi-side attempt paths from immutable
Phase 09 records. A quoted external path is not proof that another machine
currently has the payload; label unavailable artifacts honestly rather than
recreating them from prose.

Heavy-Ball study folders remain historical/archive evidence. Active V1
GESC + Gaussian work uses the managed roots above.
