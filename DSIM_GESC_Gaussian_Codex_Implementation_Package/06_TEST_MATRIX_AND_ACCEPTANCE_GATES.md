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

### Level 4 — Two-source light-level coverage

When levels 1–5 exist, cover all ordered combinations at least once:

\[
5 \times 5 = 25
\]

The staged validation design does not take the Cartesian product of every
combination, start, and seed. Assign starts/headings and deterministic seeds
across the 25 ordered pairs using a predeclared balanced schedule. Additional
start/seed repetitions belong in the targeted reproducibility subset.

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

## Staged Phase 08 validation design

The former 519-run pass repeated three times is retired for future acceptance.
It remains historical Phase 08 v1 evidence and must not be deleted, relabeled,
or counted toward the amended gate.

The amended empirical workflow contains exactly 120 declared runs:

1. **Activation proof — 10 runs.** Exercise easy goal hold, local-minimum
   classification, fill creation, pure repulsion, assisted escape, fill merge,
   recenter/resume, boundary/contact evidence, disturbance evidence, and Phase
   07 lifecycle recognition. Every intended state and event is mandatory.
2. **Bounded tuning — 30 runs.** Run three predeclared candidates on the same
   ten training cases. Select by the frozen lexicographic metric and commit one
   parameter set before any holdout is opened.
3. **Hidden holdout — 20 runs.** Use new cases/seeds not used by the failed v1
   sweep or by v2 tuning. Seal their manifest hash before tuning and prevent
   the validation command from opening them until after freeze. "Hidden" means
   selection-blind, not a security boundary. At least 18/20 must succeed end to
   end, all recording and collision evidence must be valid, and no required
   lifecycle coverage may be missing. Failure stops the remaining empirical
   stages.
4. **Additional unique validation — 50 runs.** Together with the 20 holdouts,
   this produces a 70-run unique fixed-profile acceptance denominator.
5. **Reproducibility — 10 repeats.** Repeat a predeclared cross-family subset
   from the 70 unique runs. Require the same categorical outcomes, state/event
   coverage, and gate disposition with numerical metrics inside declared
   tolerances.

The 70 unique validation runs use this fixed family allocation:

| Family | Hidden holdout | Additional validation | Unique total | Repeats |
|---|---:|---:|---:|---:|
| All 25 ordered two-source level pairs | 7 | 18 | 25 | 2 |
| Multi-source, close, and overlapping fields | 3 | 6 | 9 | 2 |
| Wall and corner boundary cases | 2 | 6 | 8 | 1 |
| Noise and sensor/pose delay | 2 | 6 | 8 | 1 |
| Saturation, timeout, and safe-failure constraints | 2 | 6 | 8 | 1 |
| Escape, assist, merge, recenter, and revisit lifecycle | 4 | 8 | 12 | 3 |
| **Total** | **20** | **50** | **70** | **10** |

The 20 hidden holdouts are a predeclared subset of those family allocations;
the additional 50 runs complete the table. The ten reproducibility repeats are
reported separately and never inflate the unique-run success denominator.

This is a stratified empirical claim over the declared scenario sample, not an
exhaustive claim over every start/seed Cartesian product. Report observed rates
and two-sided 95% Wilson score confidence intervals overall and by family.

Activation and holdout are explicit early-stop gates. A failed early stage is a
Level C result: preserve its evidence, write the failure report, and do not
spend the remaining run budget.

## Simulation-ready gate

All must be true with one fixed code commit and one fixed parameter set:

1. All unit and integration tests pass.
2. The 10-run activation gate passes before tuning.
3. The 20-run hidden holdout gate passes before the additional validation runs.
4. No required-topic, analysis-completeness, cleanup, or frozen-hash failure
   occurs in the 70 unique validation runs or ten repeats.
5. Collision evidence is valid and contains no non-ground collision.
6. At least 95% local-escape success is observed across all valid designated
   escape attempts; designated cases must actually exercise the lifecycle.
7. At least 90% end-to-end goal success is observed over the 70 unique runs.
8. No required scenario family is below 80% end-to-end goal success.
9. Median escape time is no greater than 20 seconds.
10. 95th-percentile escape time is no greater than 45 seconds.
11. Median post-fill orbit count is no greater than 1.5.
12. No run circles indefinitely; every run completes or fails safely by timeout.
13. Previously filled minima are revisited in fewer than 5% of successful runs.
14. All ten reproducibility repeats retain their
    goal/timeout/failsafe/collision categorical outcomes and required
    state/event coverage. Relative to the corresponding unique run, escape and
    convergence times differ by no more than the greater of 2 seconds or 10%,
    path length by no more than the greater of 0.25 m or 10%, orbit count by no
    more than 0.25, and final goal-distance by no more than 0.10 m.
15. Git commit is tagged as simulation-ready only after gates 1–14 pass.

The exact physical time thresholds may be revised once the repository's current
velocity limits are audited, but any revision must be written, justified,
versioned, and frozen before the 20-run holdout begins.

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
