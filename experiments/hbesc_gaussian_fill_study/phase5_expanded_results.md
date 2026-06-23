# Phase 5 Expanded Characterization Results

Status as of 2026-06-23: the expanded Phase 5 characterization matrix is
complete.

The prior 7-run bounded Phase 5A matrix remains documented in
`phase5_results.md`. This document covers the expanded Phase 5B matrix derived
from `MASTER_PLAN.md` section 13.

## Scope

The expanded matrix contains 84 scenarios:

- 15 existing pilot baseline replications.
- 5 Gaussian-fill pilot pairs.
- 10 quartic curvature and shape cases.
- 25 baseline double-well alpha-by-speed cases.
- 5 Gaussian-fill double-well alpha cases.
- 4 double-well beta cases.
- 4 double-well gamma cases.
- 10 starting-position grid cases.
- 6 deterministic cost-noise seed cases.

The matrix source is:

`configs/scenarios/phase5_expanded_characterization_matrix.csv`

The generated scenario/config source is reproducible through:

`scripts/generate_phase5_expanded_matrix.py`

## Execution

The expanded matrix was dry-run first:

`results/batches/phase5_expanded_dry_run/`

Dry-run status:

- planned scenarios: 84
- failure count: 0
- result statuses: all succeeded

Execution used a canary batch first:

`results/batches/phase5_expanded_execute_canary/`

The controlling execute batch then used `--resume`, skipped the successful
canary scenario, and ran the remaining 83 scenarios:

`results/batches/phase5_expanded_execute/`

Execution status:

- total successful Phase 5B execute scenarios in `results_manifest.csv`: 84
- unique successful Phase 5B scenario IDs: 84
- execute status for all 84: `sim_time_reached`
- controlling execute batch failure count: 0

## Aggregate Artifacts

- Metrics CSV:
  `results/batches/phase5_expanded_execute/phase5_expanded_metrics.csv`
- Summary JSON:
  `results/batches/phase5_expanded_execute/phase5_expanded_summary.json`
- Figures:
  `results/batches/phase5_expanded_execute/figures/phase5b_success_by_axis.png`
  `results/batches/phase5_expanded_execute/figures/phase5b_alpha_speed_final_distance.png`
  `results/batches/phase5_expanded_execute/figures/phase5b_alpha_speed_final_distance_heatmap.png`
  `results/batches/phase5_expanded_execute/figures/phase5b_axis_method_success_heatmap.png`
  `results/batches/phase5_expanded_execute/figures/phase5b_start_grid_final_distance.png`
  `results/batches/phase5_expanded_execute/figures/phase5b_physical_feasibility.png`
- Aggregation script:
  `scripts/aggregate_phase5_expanded.py`

## Aggregate Counts

All 84 rows reached sim-time.

Success here means the run entered the 2 m target radius at least once.

| Group | Successes | Runs |
|---|---:|---:|
| pilot replication | 7 | 15 |
| pilot Gaussian-fill pairs | 2 | 5 |
| quartic curvature and shape | 5 | 10 |
| double-well alpha speed | 0 | 25 |
| double-well alpha Gaussian fill | 0 | 5 |
| double-well beta | 0 | 4 |
| double-well gamma | 0 | 4 |
| starting-position grid | 0 | 10 |
| noise seed | 0 | 6 |

By method:

| Method | Successes | Runs |
|---|---:|---:|
| baseline HBESC | 12 | 57 |
| Gaussian fill | 2 | 27 |

Physical feasibility labels:

| Label | Runs |
|---|---:|
| within TurtleBot3 Burger reference limits | 48 |
| exceeds TurtleBot3 Burger reference limits | 36 |

## Main Findings

- The expanded matrix did not find a baseline HBESC escape boundary for the
  tested quartic double-well family. None of the alpha-speed, beta, gamma,
  start-grid, or noise-seed double-well cases entered the 2 m target radius.
- Increasing `set_max_vx` did not rescue the double-well cases. Final distance
  stayed roughly in the 10.85 m to 11.94 m range across the baseline
  alpha-speed sweep.
- Higher alpha increased saturation burden. For example, at `alpha=0.04`, vx
  saturation ranged from about 75.6% to 84.3% across tested speed settings, and
  the real-speed row exceeded TurtleBot3 Burger reference limits.
- Gaussian fill executed one fill in every Gaussian-fill row, but it did not
  rescue the tested quartic double-well cases. In the double-well slices, final
  distance commonly remained about 12.5 m to 14.0 m from the target.
- Gaussian fill helped one Gaussian two-basin pilot case: `P5B-PILOT-GF-G2_GLOBALW40_START1_REAL`
  ended at 0.159 m from the target and stayed within TurtleBot3 Burger reference
  limits.
- Gaussian fill also entered the 2 m radius on the quadratic pilot pair, but it
  ended at 5.196 m, so that run is not a clean final-tracking success.
- Baseline HBESC remained strongest on single-well quadratic/quartic cases and
  quartic curvature/shape variants. The baseline quartic curvature/shape rows
  entered the target radius in all five tested cases.
- Real-speed baseline successes are still physically questionable when wheel
  RPM exceeds the TurtleBot3 Burger reference limit; this remains a primary
  thesis result, not a plotting detail.

## Interpretation

The fully expanded Phase 5 result strengthens the Phase 5A conclusion. The
tested double-well family is a robust local-basin failure mode for baseline
HBESC under the sampled speed, alpha, beta, gamma, start-position, and noise
conditions. Gaussian fill, with the current conservative one-fill settings,
does not solve that failure mode in this matrix.

The useful next research step is not to rerun this same matrix. It is to inspect
Gaussian-fill placement and modified-cost diagnostics for the double-well rows,
then tune fill amplitude/sigma/detection timing or test multi-fill behavior in
a smaller targeted follow-up.
