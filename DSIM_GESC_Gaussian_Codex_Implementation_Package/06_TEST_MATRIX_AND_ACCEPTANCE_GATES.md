# Test Matrix and Acceptance Gates

## Robustness envelope

The final claim is limited to the documented scenario family. The controller is not claimed to solve every arbitrary nonconvex function.

## Test hierarchy

### Level 1 — Unit tests

- cost composition,
- state transitions,
- timeout behavior,
- source-score verification,
- kernel weights,
- center estimate,
- covariance,
- quadratic fit,
- adaptive amplitude/width,
- residual-minimum check,
- merge logic,
- fill gradient sign,
- wall-direction rejection,
- zero command on failure,
- message serialization.

### Level 2 — Synthetic cost fields

At minimum:

1. Single quadratic minimum.
2. Broad shallow minimum.
3. Narrow deep minimum.
4. Asymmetric quartic basin.
5. Two close minima.
6. Cluster of shallow minima.
7. Basin near wall.
8. Basin near corner.
9. Desired global minimum plus multiple local minima.
10. Noisy and delayed measurements.

### Level 3 — Single Gazebo integration cases

- one source,
- one local plus one desired source,
- local minimum near wall,
- fill merge case,
- pure-repulsion success,
- pure-repulsion stall and assisted escape,
- recenter and resume.

### Level 4 — Two-source light-level matrix

When levels 1–5 exist, run all ordered combinations:

\[
5 \times 5 = 25
\]

For each combination:

- at least 5 starting poses/headings,
- at least 3 deterministic seeds if stochastic noise is enabled.

### Level 5 — Multi-source cases

- 3 sources,
- 4 sources,
- overlapping fields,
- close minima,
- multiple prior fills,
- differing source strengths.

### Level 6 — Constraint cases

- velocity saturation,
- angular-rate saturation,
- sensor noise,
- sensor delay,
- pose delay,
- stale-data rejection,
- wall and corner proximity.

## Metrics

Per run:

- global/source success,
- local escape success,
- collision,
- total convergence time,
- escape time,
- path length,
- radial progress,
- approximate orbit count after fill,
- number of revisits,
- number of fill creations,
- number of fill merges,
- fill-design escalation count,
- timeout/failsafe,
- data-completeness status.

## Simulation-ready gate

All must be true with one fixed code commit and one fixed parameter set:

1. All unit and integration tests pass.
2. No required-topic or completeness failures.
3. No collisions in the required matrix.
4. At least 95% local-escape success over the required matrix.
5. At least 90% end-to-end goal success over the required matrix.
6. No individual baseline scenario family below 80% goal success.
7. Median escape time no greater than 20 seconds.
8. 95th-percentile escape time no greater than 45 seconds.
9. Median post-fill orbit count no greater than 1.5.
10. No run circles indefinitely; every run completes or fails safely by timeout.
11. Previously filled minima are revisited in fewer than 5% of successful runs.
12. Three consecutive full-suite executions pass without code or parameter changes.
13. Git commit is tagged as simulation-ready.

The exact physical time thresholds may be revised once the repository's current velocity limits are audited, but any revision must be written, justified, versioned, and frozen before the final matrix.

## Physical-ready gate

All simulation-ready requirements, plus:

1. Canonical physical topics match the simulation data contract.
2. Required-topic preflight passes on the physical robot.
3. Vicon and sensor timestamps are synchronized.
4. Emergency stop and zero-command shutdown are tested.
5. One-source low-speed calibration runs succeed.
6. Source-score calibration is documented.
7. A dry run records a complete bag.
8. Dr. Nili or the designated lab supervisor authorizes progression.

## Physical progression

1. Stationary sensor calibration.
2. Low-speed one-source convergence.
3. One artificial local basin.
4. Two-source cases with large separation.
5. Two-source light-level matrix.
6. Reduced separation.
7. Boundary cases.
8. Multi-source cases only after prior stages pass.

Do not alter parameters within one declared experiment matrix. A parameter change creates a new version and restarts the applicable matrix.
