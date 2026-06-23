# Final Report Outline

Phase 6 status as of 2026-06-23: the report outline is ready for thesis/report
drafting from the completed Phase 3, Phase 4, Phase 5A, and Phase 5B artifacts.

## 1. Introduction

- State the research problem: characterize when HeavyBall ESC succeeds, when it
  fails, when Gaussian fill helps, and when TurtleBot3 Burger physical limits
  make a mathematically successful run questionable.
- Define the three professor-facing scenario classes:
  - Class A: HBESC helps but Gaussian fill does not.
  - Class B: Gaussian fill helps when HBESC does not.
  - Class C: HBESC helps, but TurtleBot3 physical limits matter.
- Summarize the completed evidence base: Phase 3 minimal quartic matrix, Phase
  4 gain-sensitivity matrix, Phase 5A bounded characterization, and Phase 5B
  expanded 84-scenario characterization.

Primary sources:

- `MASTER_PLAN.md`
- `phase3_results.md`
- `phase4_results.md`
- `phase5_results.md`
- `phase5_expanded_results.md`
- `final_summary.md`

## 2. Background On ESC, HBESC, And Gaussian Fill

- Explain ESC as a measurement-driven optimization method.
- Explain the local repo's baseline HBESC path:
  `controller_node_script.py` -> `Rotating_Frame_Directional_Controller` ->
  `HeavyBallODE`.
- Explain Gaussian fill as the PDE/modified-cost extension:
  `pde_history_node`, `convergence_detector_node`, `gaussian_fill_node`, and
  `modified_cost_node`.
- Clarify that Gaussian-shaped cost maps are not the same thing as the
  Gaussian-fill method.

Primary sources:

- `code_trace.md`
- `hbesc_gain_trace.md`

## 3. Simulation Platform And TurtleBot3 Burger Limits

- Describe the ROS2 Humble + Gazebo Classic setup and TurtleBot3 rotating-sensor
  model.
- Report the repo/controller physical metadata:
  - wheel radius: `0.033 m`
  - wheel distance: `0.158 m`
  - wheel max RPM: `70`
  - real-speed forward command limit computed from wheel RPM: about `0.242 m/s`
  - real-speed yaw cap: `0.75 rad/s`
- Define the physical-feasibility label used in the result tables.
- Explain why real-speed baseline HBESC often exceeds the TurtleBot3 Burger
  wheel RPM reference even when it converges.

Primary sources:

- `hbesc_gain_trace.md`
- `phase3_results.md`
- `phase4_results.md`
- `phase5_expanded_results.md`

## 4. Code And Algorithm Trace

- Present the end-to-end data path:
  - Gazebo/diff-drive publishes `/odom`.
  - Rotating sensor state comes from `/joint_states`.
  - Sensor pose is computed by the sensor pose node.
  - Cost is computed by the cost-function node.
  - GESC filter processes cost and encoder data.
  - HBESC dynamic state generates `vx` and `wz`.
  - Controller limits commands and publishes `/cmd_vel`.
- Distinguish robot yaw `wz` from rotating sensor spin rate.
- Explain normal data outputs and the Gaussian-fill diagnostic recording gap.

Primary source:

- `code_trace.md`

## 5. Experimental Design

- Describe the phase structure:
  - Phase 3: minimal quartic matrix and `vx`/`wz` sensitivity.
  - Phase 4: one-at-a-time HBESC gain sensitivity.
  - Phase 5A: bounded quartic curvature and double-well barrier/speed matrix.
  - Phase 5B: expanded 84-scenario characterization.
- Explain controlled comparison rules:
  - same cost functions, starts, stop rules, and success radius where paired
    comparisons are made;
  - dry-run before execute;
  - bounded sim-time stop rules;
  - manifest-backed metrics and plots.

Primary sources:

- `experiment_plan.md`
- `results_manifest.csv`
- `configs/scenarios/phase5_expanded_characterization_matrix.csv`

## 6. Pilot And Minimal Quartic Results

- Use Phase 3 as the first classification evidence.
- Highlight:
  - `QRT-A-HB` converged on the convex quartic while `QRT-A-GF` did not.
  - `QRT-B-HB` and `QRT-B-GF` both failed on the quartic double-well.
  - `QRT-C-SLOW`, `QRT-C-REAL`, and `QRT-C-FAST` show the speed/physical-limit
    tradeoff.
  - quadratic and quartic both converged under the real-speed controller, but
    the quadratic reached the success radius faster.

Primary source:

- `phase3_results.md`

## 7. Quartic Cost-Function Characterization

- Present Phase 5B quartic curvature and shape cases.
- Report that baseline HBESC entered the 2 m target radius in all five baseline
  quartic curvature/shape rows.
- Discuss the trend:
  - shallow quartic: slower, worse final distance;
  - default/steep quartic: better final localization and faster entry;
  - asymmetric/cross-coupled cases: still successful for baseline HBESC.
- Use this section to support the claim that baseline HBESC is strongest on
  single-well quadratic/quartic landscapes.

Primary sources:

- `phase5_expanded_results.md`
- `results/batches/phase5_expanded_execute/phase5_expanded_metrics.csv`

## 8. Scenario Class A: HBESC Helps But Gaussian Fill Does Not

- Main supported case: convex quartic.
- Phase 3 evidence:
  - `QRT-A-HB`: final distance `0.565 m`, entered the 2 m success radius.
  - `QRT-A-GF`: final distance `5.786 m`, did not enter the 2 m success radius.
- Phase 5B evidence:
  - baseline HBESC succeeded on all five quartic curvature/shape baseline rows;
  - Gaussian-fill quartic rows did not establish a stronger benefit region.
- Interpret this as Gaussian fill being unnecessary or harmful on clean
  single-well quartic cases under the tested conservative one-fill settings.

Primary sources:

- `phase3_results.md`
- `phase5_expanded_results.md`

## 9. Scenario Class B: Gaussian Fill Helps When HBESC Does Not

- State the evidence honestly: no strong Class B case was proven where baseline
  HBESC failed to enter the target radius and Gaussian fill cleanly succeeded.
- The best B-adjacent result is `P5B-PILOT-GF-G2_GLOBALW40_START1_REAL`:
  - Gaussian fill ended at `0.159 m` and stayed within TurtleBot3 Burger
    reference limits.
  - The paired real-speed baseline entered the success radius but exceeded
    TurtleBot3 Burger reference limits, so this is stronger evidence for
    Gaussian fill improving physical plausibility than for pure HBESC failure.
- The quadratic Gaussian-fill pilot entered the success radius but ended at
  `5.196 m`, so it is not a clean final-tracking success.
- The quartic double-well Gaussian-fill rows did not rescue local-basin failure.

Primary sources:

- `phase5_expanded_results.md`
- `results/batches/phase5_expanded_execute/phase5_expanded_metrics.csv`

## 10. Scenario Class C: TurtleBot3 Physical Limitations

- Present the strong physical-limit result:
  - Phase 3 `QRT-C-SLOW` converged within reference limits but more slowly.
  - Phase 3 `QRT-C-REAL` and `QRT-C-FAST` converged faster but exceeded wheel
    RPM reference limits.
  - Phase 4 all nine gain variants converged but all exceeded TurtleBot3 Burger
    reference limits.
  - Phase 5B had 14 success-radius entries; 11 exceeded TurtleBot3 Burger
    reference limits.
- Discuss the main limitation: forward command authority and reconstructed
  wheel RPM, not only yaw-rate saturation.

Primary sources:

- `phase3_results.md`
- `phase4_results.md`
- `phase5_expanded_results.md`

## 11. `vx`/`wz` And Speed-Limit Sensitivity

- Use Phase 3 `QRT-VWZ-*` rows:
  - reducing `vx` while keeping real `wz` remained physically valid but slowed
    convergence;
  - reducing only `wz` did not solve the wheel RPM issue because forward
    command authority still exceeded the reference limit.
- Use Phase 5B alpha-speed heatmap to show that increasing speed authority did
  not rescue the tested double-well family.

Figures:

- `results/batches/phase5_expanded_execute/figures/phase5b_alpha_speed_final_distance_heatmap.png`
- `results/batches/phase5_expanded_execute/figures/phase5b_alpha_speed_final_distance.png`

## 12. HBESC Gain Sensitivity

- Present Phase 4 as a one-at-a-time gain study on a representative convex
  quartic field.
- Main conclusions:
  - `k_vx` matters for speed and final localization, but increases saturation
    burden.
  - HeavyBall `k` matters similarly and gave the best final distance when high.
  - `beta` is the strongest trajectory/stability tradeoff parameter.
  - `k_wz` had smaller impact on this field; high `k_wz` raised yaw saturation
    without improving final distance.
  - gain tuning alone did not make the real-speed baseline physically feasible.

Primary source:

- `phase4_results.md`

## 13. Broader Characterization: Escape Probability And Critical Speed

- Use Phase 5B expanded characterization.
- Report:
  - 84 total completed scenarios;
  - 14 success-radius entries;
  - no successes in alpha-speed, alpha Gaussian-fill, beta, gamma, start-grid,
    or noise-seed double-well slices;
  - final distance stayed roughly `10.85 m` to `11.94 m` across the baseline
    alpha-speed sweep.
- Interpret: the tested quartic double-well family is a robust local-basin
  failure mode under the sampled speed, alpha, beta, gamma, start-position, and
  noise conditions.

Figures:

- `results/batches/phase5_expanded_execute/figures/phase5b_axis_method_success_heatmap.png`
- `results/batches/phase5_expanded_execute/figures/phase5b_success_by_axis.png`
- `results/batches/phase5_expanded_execute/figures/phase5b_start_grid_final_distance.png`

## 14. Results

- Consolidate result tables from:
  - `phase3_results.md`
  - `phase4_results.md`
  - `phase5_results.md`
  - `phase5_expanded_results.md`
- Include a compact comparison table:
  - method;
  - cost family;
  - success-radius entry;
  - final distance;
  - physical-feasibility label;
  - failure mode or interpretation.

## 15. Discussion

- Baseline HBESC is effective on single-well quadratic/quartic landscapes but
  often relies on command levels that exceed TurtleBot3 Burger reference limits.
- Conservative one-fill Gaussian fill did not solve the tested quartic
  double-well failure mode.
- Gaussian fill may improve physical plausibility in selected Gaussian two-basin
  cases, but this should be treated as a targeted follow-up rather than a
  broad conclusion.
- The double-well family may require different fill amplitude, sigma, detection
  timing, or multi-fill behavior.

## 16. Limitations

- Results are simulation-backed, not hardware-backed.
- Gaussian-fill diagnostics are better than the normal data logger through
  rosbag diagnostics, but raw cost and fill-placement analysis still need a
  focused follow-up.
- Phase 4 gain sensitivity is one-at-a-time on one representative quartic
  field; it does not prove global gain optimality.
- Some physically infeasible labels depend on TurtleBot3 Burger reference
  comparisons and reconstructed wheel RPM from command logs.

## 17. Future Work

- Inspect Gaussian-fill placement and modified-cost diagnostics for failed
  double-well rows.
- Run a small targeted fill-parameter sweep:
  - amplitude;
  - sigma bounds;
  - convergence detection threshold/timing;
  - one-fill versus multi-fill.
- Add hardware-feasible controller variants that keep wheel RPM within the 70
  RPM reference.
- Expand gain studies only after selecting physically feasible speed limits.
- Consider physical hardware validation for the strongest single-well and
  Gaussian two-basin findings.

## 18. Appendix

- Manifest: `results_manifest.csv`
- Phase 4 metrics: `results/batches/phase4_gain_execute/phase4_metrics.csv`
- Phase 5A metrics: `results/batches/phase5_characterization_execute_host/phase5_metrics.csv`
- Phase 5B metrics: `results/batches/phase5_expanded_execute/phase5_expanded_metrics.csv`
- Phase 5B summary: `results/batches/phase5_expanded_execute/phase5_expanded_summary.json`
- Scenario matrix: `configs/scenarios/phase5_expanded_characterization_matrix.csv`
- Generated scenario/config source: `scripts/generate_phase5_expanded_matrix.py`
- Aggregation source: `scripts/aggregate_phase5_expanded.py`
