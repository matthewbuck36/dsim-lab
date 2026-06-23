# Final Summary

Phase 6 status as of 2026-06-23: the study has enough data for a final summary
and report outline. This document answers the required Phase 6 questions from
the completed Phase 3, Phase 4, Phase 5A, and Phase 5B artifacts.

## Evidence Base

- Phase 3 minimal quartic matrix: 11 valid execute runs, plus one invalidated
  run retained for audit and superseded.
- Phase 4 HBESC gain sensitivity: 9 execute runs, all completed.
- Phase 5A bounded characterization: 7 host-level execute runs, all completed.
- Phase 5B expanded characterization: 84 execute scenarios, all reached
  `sim_time_reached`.
- Phase 5B aggregate counts:
  - baseline HBESC: 12 success-radius entries out of 57 rows;
  - Gaussian fill: 2 success-radius entries out of 27 rows;
  - total success-radius entries: 14 out of 84;
  - physical labels: 48 within TurtleBot3 Burger reference limits and 36
    exceeding reference limits.

Primary aggregate artifacts:

- `results_manifest.csv`
- `results/batches/phase4_gain_execute/phase4_metrics.csv`
- `results/batches/phase5_characterization_execute_host/phase5_metrics.csv`
- `results/batches/phase5_expanded_execute/phase5_expanded_metrics.csv`
- `results/batches/phase5_expanded_execute/phase5_expanded_summary.json`

## 1. What Scenarios Show HBESC Helping When Gaussian Fill Does Not?

The strongest supported case is the convex quartic single-well scenario from
Phase 3.

Evidence:

- `QRT-A-HB` reached the target region with final distance `0.565 m`.
- `QRT-A-GF` did not enter the 2 m success radius and ended at `5.786 m`.
- Phase 5B reinforced the same pattern: baseline HBESC succeeded on all five
  baseline quartic curvature/shape rows, including shallow, default, steep,
  asymmetric, and cross-coupled quartic variants.

Interpretation:

Baseline HBESC is the better method on clean single-well quartic landscapes in
this study. Conservative one-fill Gaussian fill is unnecessary there and can
distort the useful HBESC trajectory.

## 2. What Scenarios Show Gaussian Fill Helping When HBESC Does Not?

No strong pure Class B scenario was proven.

The best B-adjacent result is the Gaussian two-basin pilot case
`P5B-PILOT-GF-G2_GLOBALW40_START1_REAL`.

Evidence:

- Gaussian fill ended at `0.159 m`, entered the 2 m radius, and stayed within
  TurtleBot3 Burger reference limits.
- The paired real-speed baseline row also entered the 2 m radius, ending at
  `1.394 m`, but exceeded TurtleBot3 Burger reference limits.

Interpretation:

This is evidence that Gaussian fill can improve physical plausibility and final
tracking in a selected Gaussian two-basin case. It is not evidence that baseline
HBESC could not help at all, because the paired baseline did enter the target
radius. The Phase 3 and Phase 5B quartic double-well cases did not show Gaussian
fill rescuing a baseline HBESC failure.

## 3. What TurtleBot3 Burger Physical Limitations Appear When HBESC Is Successful?

The dominant limitation is wheel RPM / forward command authority.

Evidence:

- Phase 3 `QRT-C-SLOW` converged within TurtleBot3 Burger reference limits but
  took `267.308 s` to enter the 2 m radius.
- Phase 3 `QRT-C-REAL` and `QRT-C-FAST` converged faster, at `144.670 s` and
  `146.608 s`, but exceeded TurtleBot3 Burger reference wheel limits.
- Phase 4 all nine gain variants converged on the representative convex quartic
  field, and all nine exceeded TurtleBot3 Burger reference limits.
- Phase 5B had 14 success-radius entries; 11 exceeded TurtleBot3 Burger
  reference limits.

Interpretation:

HBESC can solve single-well objectives in simulation, but many successful
real-speed baseline runs demand more wheel RPM than the TurtleBot3 Burger
reference limit. Lower speed authority can remain physically plausible but
slows convergence. Increasing speed authority did not rescue the tested
double-well failure mode.

## 4. Which Results Are Strong, Weak, Or Inconclusive?

Strong results:

- Baseline HBESC succeeds on clean single-well quadratic/quartic landscapes.
- Baseline HBESC outperforms conservative Gaussian fill on the Phase 3 convex
  quartic pair.
- The tested quartic double-well family is a robust local-basin failure mode:
  all alpha-speed, alpha Gaussian-fill, beta, gamma, start-grid, and noise-seed
  double-well slices failed to enter the 2 m target radius.
- Physical feasibility is central: most baseline successes exceed TurtleBot3
  Burger reference limits.
- `k_vx`, HeavyBall `k`, and `beta` materially affect convergence quality,
  trajectory shape, and saturation burden.

Weak or limited results:

- Gaussian fill helped one Gaussian two-basin pilot case strongly, but this is
  not enough to claim broad benefit.
- The Gaussian-fill quadratic pilot entered the success radius but ended at
  `5.196 m`, so it is not a clean final-tracking success.
- Phase 4 gain sensitivity used one representative convex quartic field; it
  should not be treated as a global gain optimization.

Inconclusive results:

- No proven case yet where baseline HBESC cannot enter the target radius but
  Gaussian fill cleanly succeeds.
- The reason Gaussian fill failed on quartic double-well rows needs fill
  placement and modified-cost diagnostic analysis.
- Multi-fill behavior remains untested in the expanded characterization.

## 5. Which HBESC Gains Matter Most?

From Phase 4, the most important tested gains are:

1. HeavyBall `k`
2. `k_vx`
3. `beta`
4. `k_wz`, with smaller effect on the tested convex quartic field

Evidence:

- High HeavyBall `k=2.0` produced the best final distance, `0.400 m`, and the
  fastest success time, `122.502 s`.
- High `k_vx=0.4` produced final distance `0.430 m` and success time
  `122.536 s`.
- Low `beta=0.05` caused the slowest convergence, longest path, and highest
  saturation burden.
- Low/high `k_wz` changed yaw saturation more than final convergence quality.

## 6. What Does Each Important Gain Appear To Do?

`k_vx`:

- Higher `k_vx` increases forward response, improves convergence time and final
  localization on the tested convex quartic, and increases path length and
  saturation burden.
- Lower `k_vx` weakens final localization.

HeavyBall `k`:

- Higher HeavyBall `k` strengthens the response to the gradient estimate,
  improving success time and final distance on the tested convex quartic.
- Lower HeavyBall `k` weakens final localization.

`beta`:

- `beta` controls a major damping/trajectory tradeoff.
- Low `beta` produced slow convergence, long path length, and high saturation.
- High `beta` shortened the path and lowered saturation but worsened final
  localization.

`k_wz`:

- `k_wz` mainly affected yaw saturation on the tested field.
- High `k_wz` increased yaw saturation without improving final distance.
- Low `k_wz` reduced yaw saturation while preserving similar final distance.

## 7. Which Gains Improve Quartic Convergence?

On the representative convex quartic Phase 4 field:

- High HeavyBall `k=2.0` gave the fastest and best final convergence.
- High `k_vx=0.4` also improved convergence speed and final distance.
- Low `k_wz=1.0` slightly improved success time relative to default while
  reducing yaw saturation, but its effect was much smaller.
- High `beta=0.2` improved success time relative to default but worsened final
  distance, so it is not a clean convergence-quality improvement.

The best convergence-quality candidates are therefore high HeavyBall `k` and
high `k_vx`, with the caveat that both remained physically infeasible under the
real-speed baseline limits.

## 8. Which Gains Cause Oscillation, Saturation, Or Physical Infeasibility?

All Phase 4 gain variants were physically infeasible under TurtleBot3 Burger
reference limits because reconstructed wheel RPM reached the real-speed
baseline cap region.

Specific gain effects:

- High HeavyBall `k` improved final distance but increased yaw saturation to
  `9.67%`.
- High `k_vx` improved final distance but kept vx saturation high at `18.30%`.
- Low `beta` was the most concerning trajectory case: it produced the longest
  path, `60.362 m`, the slowest success time, `268.974 s`, and the highest vx
  saturation burden, `38.24%`.
- High `k_wz` increased yaw saturation to `9.90%` without improving final
  distance.

Interpretation:

Gain tuning can improve mathematical convergence, but in this setup it does not
by itself solve physical feasibility. Feasible HBESC tuning should start with a
speed-authority constraint, then tune gains inside that feasible envelope.

## 9. How Does Gain Choice Change The Comparison Between HBESC And Gaussian Fill?

Gain choice can make baseline HBESC look better on single-well quartic cases by
reducing final distance and success time. It can also make baseline HBESC look
better than Gaussian fill while hiding a physical-feasibility problem, because
the best-performing gain variants still exceeded TurtleBot3 Burger reference
limits.

For this study, Gaussian fill should not be compared only against the most
aggressive baseline HBESC. A fair comparison should include:

- the real-speed baseline;
- a physically feasible low-speed baseline;
- gain-tuned baseline variants inside TurtleBot3 Burger reference limits;
- Gaussian-fill variants with the same physical envelope.

This matters because the strongest Gaussian-fill result is not a pure success
versus failure win; it is a physically feasible final-tracking improvement in a
selected Gaussian two-basin pilot case.

## 10. What Should Be Run Next?

Do not rerun the full Phase 5B matrix immediately. The next work should be a
small targeted follow-up.

Recommended next steps:

1. Inspect Gaussian-fill placement and modified-cost diagnostics for failed
   double-well rows.
2. Run a small Gaussian-fill parameter matrix on the double-well family:
   fill amplitude, sigma bounds, convergence threshold/timing, and one-fill
   versus multi-fill.
3. Add a physically feasible HBESC baseline family that keeps wheel RPM within
   the TurtleBot3 Burger reference limit.
4. Repeat the most important gain tests inside that feasible speed envelope.
5. Preserve the existing Phase 5B matrix as the broad characterization baseline;
   use the next runs to explain mechanisms, not to produce another large table.

## Bottom Line

Baseline HBESC is reliable on the tested single-well quadratic/quartic
landscapes, but many successful real-speed runs exceed TurtleBot3 Burger
reference limits. Conservative one-fill Gaussian fill did not rescue the tested
quartic double-well local-basin failure mode. Gaussian fill produced one strong
physically feasible Gaussian two-basin pilot result, but the current evidence
does not yet prove a broad Class B region. The next thesis-grade step is a
targeted Gaussian-fill diagnostic and parameter study, combined with physically
feasible HBESC gain tuning.
