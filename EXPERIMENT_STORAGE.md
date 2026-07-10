# Experiment Storage Protocol

Raw Gazebo and physical TurtleBot3 experiment data belongs outside this Git
repository under `~/Experiments`.

The canonical layout is:

```text
~/Experiments/
├── Gazebo-Simulations/
│   ├── Test_YYYY-MM-DD_HH-MM-SS/       # normal data-collection runs
│   ├── HBESC-Baseline-Tests/           # named Gazebo baseline campaign
│   └── Studies/
│       └── hbesc_gaussian_fill_study/  # Codex batch study and results
└── Physical-TurtleBot3/
    └── Jan-29-try-20260630T235703Z-3-001/
```

Why this is the canonical location:

- `gazebo.launch.xml` defaults `data_collection_filepath` to
  `~/Experiments/Gazebo-Simulations`.
- The inherited Gazebo bash wrappers pass the same path.
- `data_collection_node` creates a timestamped `Test_*` directory beneath the
  path supplied by the launch file.
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
