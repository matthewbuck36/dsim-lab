# Phase 4 HBESC Gain Sensitivity Results

Status as of 2026-06-10: Phase 4 HBESC gain sensitivity is complete. The full
minimal one-at-a-time low/default/high matrix was dry-run first, then executed
headless through the bounded harness.

All 9 Phase 4 execute runs reached their 500 s sim-time stop rule, passed the
required output checks, regenerated `summary_metrics.json`, and regenerated the
topographic trajectory plot at `figures/trajectory.png` in each run directory.
The aggregate metrics file is:

`experiments/hbesc_gaussian_fill_study/results/batches/phase4_gain_execute/phase4_metrics.csv`

## Matrix

The representative field was the convex quartic bowl:

`~/dsim-lab/ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/polynomial_quartic_bowl_center10.json`

The non-swept settings were fixed to the real-speed baseline: `k_vx=0.2`,
`k_wz=2.0`, HeavyBall `k=1.0`, `beta=0.1`, `input_gain=-1.0`, full rotation
sensor config, GESC full-rotation filter, initial pose `(0,0,0)`, and the same
wheel metadata and velocity limits as `hbesc_baseline_real_full_rotation.json`.

| ID | Run ID | k_vx | k_wz | HB k | beta | Final dist m | Success time s | Tail mean m | Tail std m | Path m | Max vx | Max wz | Max wheel rpm | vx sat % | wz sat % | Physical label |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| QRT-GAIN-DEFAULT | `20260610T200359Z_phase4_gain_default_execute` | 0.2 | 2.0 | 1.0 | 0.1 | 0.564215 | 148.750 | 0.584715 | 0.012172 | 26.456634 | 0.241903 | 0.750000 | 87.145328 | 16.92 | 5.27 | `exceeds_turtlebot3_burger_reference_limits` |
| QRT-GAIN-KVX-LOW | `20260610T201236Z_phase4_gain_k_vx_low_execute` | 0.1 | 2.0 | 1.0 | 0.1 | 0.993320 | 137.734 | 1.015614 | 0.013055 | 23.873786 | 0.241903 | 0.750000 | 87.145328 | 15.93 | 5.98 | `exceeds_turtlebot3_burger_reference_limits` |
| QRT-GAIN-KVX-HIGH | `20260610T202112Z_phase4_gain_k_vx_high_execute` | 0.4 | 2.0 | 1.0 | 0.1 | 0.430393 | 122.536 | 0.443483 | 0.007902 | 30.306126 | 0.241903 | 0.750000 | 87.145328 | 18.30 | 5.21 | `exceeds_turtlebot3_burger_reference_limits` |
| QRT-GAIN-KWZ-LOW | `20260610T202949Z_phase4_gain_k_wz_low_execute` | 0.2 | 1.0 | 1.0 | 0.1 | 0.567684 | 141.168 | 0.584798 | 0.010259 | 25.135884 | 0.241903 | 0.750000 | 87.145328 | 15.44 | 0.40 | `exceeds_turtlebot3_burger_reference_limits` |
| QRT-GAIN-KWZ-HIGH | `20260610T203825Z_phase4_gain_k_wz_high_execute` | 0.2 | 4.0 | 1.0 | 0.1 | 0.573646 | 149.260 | 0.596448 | 0.013600 | 26.686918 | 0.241903 | 0.750000 | 87.145328 | 17.21 | 9.90 | `exceeds_turtlebot3_burger_reference_limits` |
| QRT-GAIN-HBK-LOW | `20260610T204702Z_phase4_gain_hb_k_low_execute` | 0.2 | 2.0 | 0.5 | 0.1 | 1.043711 | 140.148 | 1.072433 | 0.016782 | 23.705953 | 0.241903 | 0.750000 | 87.145328 | 15.67 | 0.98 | `exceeds_turtlebot3_burger_reference_limits` |
| QRT-GAIN-HBK-HIGH | `20260610T205538Z_phase4_gain_hb_k_high_execute` | 0.2 | 2.0 | 2.0 | 0.1 | 0.400297 | 122.502 | 0.418008 | 0.010589 | 29.758121 | 0.241903 | 0.750000 | 87.145328 | 18.34 | 9.67 | `exceeds_turtlebot3_burger_reference_limits` |
| QRT-GAIN-BETA-LOW | `20260610T210415Z_phase4_gain_beta_low_execute` | 0.2 | 2.0 | 1.0 | 0.05 | 0.723886 | 268.974 | 0.774894 | 0.028801 | 60.361838 | 0.241903 | 0.750000 | 87.145328 | 38.24 | 11.45 | `exceeds_turtlebot3_burger_reference_limits` |
| QRT-GAIN-BETA-HIGH | `20260610T211252Z_phase4_gain_beta_high_execute` | 0.2 | 2.0 | 1.0 | 0.2 | 0.940454 | 137.530 | 0.995440 | 0.031876 | 16.392159 | 0.241903 | 0.750000 | 87.145328 | 10.15 | 0.69 | `exceeds_turtlebot3_burger_reference_limits` |

## Conclusions

- All gain variants converged within the 2 m success radius on this convex
  quartic field, so this Phase 4 matrix is a convergence-quality and physical
  feasibility study, not a success/failure separator.
- `k_vx` matters. Increasing `k_vx` from 0.2 to 0.4 improved success time
  from 148.750 s to 122.536 s and final distance from 0.564 m to 0.430 m, but
  path length increased from 26.457 m to 30.306 m and wheel RPM remained
  infeasible. Lowering `k_vx` produced the weakest final localization in this
  axis at 0.993 m.
- `k_wz` has a smaller effect than `k_vx` on this field. Low `k_wz` slightly
  improved success time and greatly reduced yaw saturation, while high `k_wz`
  increased yaw saturation to 9.90% without improving final distance.
- HeavyBall `k` matters similarly to `k_vx`. Raising it to 2.0 gave the best
  final distance in the matrix, 0.400 m, and the fastest success time,
  122.502 s. Lowering it to 0.5 degraded final distance to 1.044 m.
- `beta` is the most sensitive stability/trajectory parameter in this set.
  Low `beta=0.05` caused the slowest convergence, 268.974 s, the longest path,
  60.362 m, and the highest saturation burden. High `beta=0.2` shortened the
  path to 16.392 m and lowered saturation, but final localization worsened to
  0.940 m.
- Every Phase 4 run exceeded TurtleBot3 Burger reference limits because the
  real-speed baseline permits forward commands up to about 0.242 m/s and the
  reconstructed wheel RPM reached 87.145 RPM versus the 70 RPM reference.
  Gain tuning alone did not make this real-speed baseline physically feasible.

## Failures Or Unresolved Questions

- No Phase 4 dry-run or execute-run failures occurred.
- No stale `gazebo`, `gzserver`, `gzclient`, `run_one_trial.sh`,
  `monitor_sim_time.py`, or `hb_scenario_acoustic` processes were found after
  the batch.
- The Gazebo logs include `Could not open file[worlds/gazebo_empty.world]` and
  fallback to Gazebo's installed empty world. This did not block data collection
  or completion, but it should be fixed before Phase 5 if the study depends on
  the custom `gazebo_empty.world` physics settings.

## Phase 5 Handoff

Next exact command for a Phase 5 dry-run after Phase 5 scenario CSVs are added:

```bash
experiments/hbesc_gaussian_fill_study/scripts/run_batch.py --csv experiments/hbesc_gaussian_fill_study/configs/scenarios/phase5_characterization_matrix.csv --batch-id phase5_characterization_dry_run
```

Suggested Phase 5 prompt:

```text
Execute Phase 5 only: Expanded Characterization. Start from MASTER_PLAN.md,
phase3_results.md, phase4_results.md, hbesc_gain_trace.md, and
results_manifest.csv. First fix or explicitly route the Gazebo world path so the
intended custom world is used, then create a bounded, non-expanded first Phase 5
characterization matrix for quartic curvature/barrier and speed authority using
the existing harness. Dry-run the full list first. If dry-runs pass, execute only
the minimal bounded Phase 5 batch, analyze outputs, regenerate plots, update the
manifest, and create phase5_results.md with exact metrics and conclusions.
```
