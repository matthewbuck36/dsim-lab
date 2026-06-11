# Phase 5 Expanded Characterization Results

Status as of 2026-06-10: the first bounded, non-expanded Phase 5
characterization matrix is complete. The matrix was dry-run first, then executed
headless through the existing harness outside the sandbox so ROS2 DDS and Gazebo
could use local sockets.

The Gazebo world path is now explicitly routed. The execute logs show Gazebo
loading:

`/home/mattb/dsim-lab/ros2_ws/src/turtlebot3_rotating_sensor/worlds/gazebo_empty.world`

The controlling execute batch is:

`experiments/hbesc_gaussian_fill_study/results/batches/phase5_characterization_execute_host/`

Aggregate artifacts:

- Metrics CSV: `results/batches/phase5_characterization_execute_host/phase5_metrics.csv`
- Curvature plot: `results/batches/phase5_characterization_execute_host/figures/phase5_curvature_summary.png`
- Barrier-speed plot: `results/batches/phase5_characterization_execute_host/figures/phase5_barrier_speed_summary.png`

## Matrix

The matrix intentionally stayed small:

- 3 convex quartic curvature cases at real-speed HBESC authority.
- 4 quartic double-well barrier-speed cases: `alpha` in `{0.005, 0.02}` crossed
  with `low_vx_real_wz` and `real` speed authority.

All 7 host-level execute runs reached their sim-time stop rule and produced
complete data.

| ID | Run ID | Axis | Status | Final dist m | Min dist m | Success time s | Tail mean m | Tail std m | Path m | Max vx | Max wz | Max wheel rpm | vx sat % | wz sat % | Physical label |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| P5-CURV-SHALLOW-REAL | `20260610T225231Z_phase5_curv_shallow_real_execute` | quartic scale `0.0001` | `sim_time_reached` | 1.300776 | 1.300776 | 136.238 | 1.320981 | 0.011955 | 13.165067 | 0.241903 | 0.320509 | 77.326987 | 6.343589 | 0.000000 | `exceeds_turtlebot3_burger_reference_limits` |
| P5-CURV-DEFAULT-REAL | `20260610T225542Z_phase5_curv_default_real_execute` | quartic scale `0.0005` | `sim_time_reached` | 0.572339 | 0.572339 | 137.496 | 0.594656 | 0.013299 | 23.295057 | 0.241903 | 0.750000 | 87.145328 | 14.503805 | 3.097020 | `exceeds_turtlebot3_burger_reference_limits` |
| P5-CURV-STEEP-REAL | `20260610T225853Z_phase5_curv_steep_real_execute` | quartic scale `0.0015` | `sim_time_reached` | 0.345607 | 0.345607 | 53.108 | 0.354293 | 0.005216 | 24.211010 | 0.241903 | 0.750000 | 87.145328 | 12.518533 | 5.857859 | `exceeds_turtlebot3_burger_reference_limits` |
| P5-BARRIER-LOW-LOWVX | `20260610T230204Z_phase5_barrier_low_lowvx_execute` | alpha `0.005`, low vx | `sim_time_reached` | 11.223445 | 10.814495 |  | 11.299976 | 0.057339 | 11.625353 | 0.050000 | 0.750000 | 31.613959 | 9.647200 | 0.361589 | `within_turtlebot3_burger_reference_limits` |
| P5-BARRIER-LOW-REAL | `20260610T230621Z_phase5_barrier_low_real_execute` | alpha `0.005`, real | `sim_time_reached` | 11.371500 | 10.095704 |  | 11.298682 | 0.044369 | 15.027734 | 0.241903 | 0.750000 | 76.942992 | 0.870373 | 0.267377 | `exceeds_turtlebot3_burger_reference_limits` |
| P5-BARRIER-HIGH-LOWVX | `20260610T231033Z_phase5_barrier_high_lowvx_execute` | alpha `0.02`, low vx | `sim_time_reached` | 11.120530 | 10.811149 |  | 11.309666 | 0.115697 | 31.206897 | 0.050000 | 0.750000 | 31.613959 | 70.885963 | 16.293095 | `within_turtlebot3_burger_reference_limits` |
| P5-BARRIER-HIGH-REAL | `20260610T231444Z_phase5_barrier_high_real_execute` | alpha `0.02`, real | `sim_time_reached` | 11.827737 | 10.420347 |  | 11.327514 | 0.464387 | 118.416181 | 0.241903 | 0.750000 | 87.145328 | 41.585632 | 31.982320 | `exceeds_turtlebot3_burger_reference_limits` |

## Conclusions

- The custom Gazebo world routing is fixed for Phase 5. Host-level logs no
  longer show `Could not open file[worlds/gazebo_empty.world]`; they show the
  absolute custom world path being loaded.
- Quartic curvature matters in the convex single-well cases. The shallow
  quartic reached the 2 m success radius but ended at 1.301 m, while the default
  and steep cases ended at 0.572 m and 0.346 m. The steep case also reached the
  2 m radius much faster, 53.108 s versus about 136 to 137 s for the shallower
  cases.
- Real-speed HBESC remains physically questionable even when it converges.
  Every convex curvature case exceeded TurtleBot3 Burger reference limits. The
  shallow case exceeded the wheel RPM reference at 77.327 RPM even though yaw
  stayed below the configured 0.75 rad/s cap.
- The tested double-well barrier-speed slice did not identify an HBESC escape
  boundary. None of the 4 double-well runs entered the 2 m target radius. Tail
  mean distance stayed tightly clustered near 11.30 m for both alpha levels and
  both speed-authority settings.
- Increasing double-well barrier alpha increased saturation burden. At low vx,
  vx saturation rose from 9.647% to 70.886% and wz saturation rose from 0.362%
  to 16.293%. At real-speed authority, vx saturation rose from 0.870% to
  41.586% and wz saturation rose from 0.267% to 31.982%.
- Higher speed authority did not rescue the tested double-well cases and made
  the real-speed runs physically infeasible. The real-speed high-alpha run also
  produced the largest path length, 118.416 m, and the largest tail distance
  variability, 0.464 m.

## Invalid Environment Attempts

Before the host-level execute batch, the same execute command was run inside the
restricted sandbox. Those rows remain in `results_manifest.csv` for audit but
are not Phase 5 evidence:

- `20260610T221608Z_phase5_curv_shallow_real_execute`
- `20260610T223120Z_phase5_curv_default_real_execute`
- `20260610T224632Z_phase5_curv_steep_real_execute`

The sandboxed logs show DDS socket failures such as `Error creating socket:
Operation not permitted`, and `gzserver` died immediately. The corrected
host-level batch supersedes these attempts.

## Next Step

For the next bounded Phase 5 increment, keep the custom world routing and run a
Gaussian-fill paired barrier slice on the same `alpha=0.005` and `alpha=0.02`
double-well cases. The current baseline HBESC slice establishes that speed
authority alone did not escape these local-basin cases.
