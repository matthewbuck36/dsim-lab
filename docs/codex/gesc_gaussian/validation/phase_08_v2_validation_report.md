# Phase 08 v2 Simulation Validation Report

Outcome: **FAIL (EARLY STOP)**.

Stopped after `activation`. No later empirical stage was authorized.

Executed declared runs: `10`.

No v2 parameter profile was selected or frozen.

## Gates

- `1_functional`: PASS; value `True`; threshold `all retained functional tests pass`.
- `2_activation`: FAIL; value `1/10`; threshold `all ten activation proofs`.
- `3_holdout`: NOT RUN; threshold `at least 18/20 with complete valid evidence`.
- `4_completeness`: NOT RUN; threshold `70/70 complete unique runs`.
- `5_collision`: NOT RUN; threshold `zero collisions with valid evidence`.
- `6_local_escape`: NOT RUN; threshold `all declared local-minimum escapes succeed`.
- `7_end_to_end`: NOT RUN; threshold `at least 63/70 end-to-end successes`.
- `8_family_minimum`: NOT RUN; threshold `every family success rate is at least 0.80`.
- `9_median_escape_time`: NOT RUN; threshold `median escape time is at most 20 s`.
- `10_p95_escape_time`: NOT RUN; threshold `p95 escape time is at most 35 s`.
- `11_median_orbit_count`: NOT RUN; threshold `median orbit count is at most 2`.
- `12_normal_termination`: NOT RUN; threshold `no unexplained timeout or failsafe`.
- `13_revisit_rate`: NOT RUN; threshold `revisit rate is at most 0.10`.
- `14_reproducibility`: NOT RUN; threshold `all ten categorical and numeric comparisons`.

## 95% Wilson score intervals

Not applicable: the 70-run acceptance denominator was not executed.

Retained evidence root: `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2`.

No physical hardware was run.
