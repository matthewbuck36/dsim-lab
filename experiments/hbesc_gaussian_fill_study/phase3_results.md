# Phase 3 Minimal Quartic Matrix Results

Status as of 2026-06-10: Phase 3 minimal quartic execution is complete. All
valid Phase 3 execute runs reached their sim-time stop rule and passed required
output checks. One earlier `QRT-B-HB` run was invalidated because its first
odometry sample did not match the configured initial pose; the corrected rerun
supersedes it.

Gazebo was configured with `real_time_update_rate=3000` in
`ros2_ws/src/turtlebot3_rotating_sensor/worlds/gazebo_empty.world`. The harness
cleanup now terminates the whole runner process session after each execute run
so `gazebo`, `gzserver`, and `gzclient` do not accumulate between trials.

## Valid Run Matrix

| ID | Run ID | Status | Final dist m | Min dist m | Success time s | Tail mean m | Path m | Max vx | Max wz | Max wheel rpm | Physical label | Fill count |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| QRT-A-HB | `20260609T230734Z_phase3_qrt_a_hb_execute` | `smoke_sim_time_reached` | 0.5647089062127876 | 0.5647089062127876 | 150.10999999999999 | 0.5868783841987824 | 26.71618536045787 | 0.2419026343264141 | 0.75 | 87.14532796035418 | `exceeds_turtlebot3_burger_reference_limits` |  |
| QRT-A-GF | `20260609T233218Z_phase3_qrt_a_gf_execute` | `sim_time_reached` | 5.78644565068586 | 3.391138794201055 |  | 5.875869460025924 | 18.05698556730699 | 0.05 | 0.25 | 20.183740510290367 | `within_turtlebot3_burger_reference_limits` | 1 |
| QRT-B-HB | `20260610T013008Z_phase3_qrt_b_hb_execute` | `sim_time_reached` | 11.261485822126843 | 10.565667257012725 |  | 11.308872180152804 | 27.388319460457858 | 0.2419026343264141 | 0.75 | 87.14532796035418 | `exceeds_turtlebot3_burger_reference_limits` |  |
| QRT-B-GF | `20260609T235245Z_phase3_qrt_b_gf_execute` | `sim_time_reached` | 13.311762218216508 | 11.028274122129273 |  | 13.370102859252787 | 8.920825703616684 | 0.05 | 0.25 | 20.183740510290367 | `within_turtlebot3_burger_reference_limits` | 1 |
| QRT-C-SLOW | `20260610T000449Z_phase3_qrt_c_slow_execute` | `sim_time_reached` | 0.5172835279028847 | 0.5172835279028847 | 267.308 | 0.5343204637064289 | 15.041314077644879 | 0.05 | 0.25 | 20.183740510290367 | `within_turtlebot3_burger_reference_limits` |  |
| QRT-C-REAL | `20260610T001649Z_phase3_qrt_c_real_execute` | `sim_time_reached` | 0.4386075881667177 | 0.4386075881667177 | 144.67000000000002 | 0.4547494270978948 | 25.95162094141649 | 0.2419026343264141 | 0.75 | 87.14532796035418 | `exceeds_turtlebot3_burger_reference_limits` |  |
| QRT-C-FAST | `20260610T002850Z_phase3_qrt_c_fast_execute` | `sim_time_reached` | 0.6091050873722549 | 0.6091050873722549 | 146.608 | 0.62471366366037 | 44.40906750685881 | 0.4 | 1.25 | 144.3245961219687 | `exceeds_turtlebot3_burger_reference_limits` |  |
| QVQ-1 | `20260610T004052Z_phase3_qvq_1_quadratic_execute` | `sim_time_reached` | 0.5725264423357845 | 0.5725264423357845 | 101.184 | 0.574483885082472 | 64.01182239331919 | 0.2419026343264141 | 0.75 | 87.14532796035418 | `exceeds_turtlebot3_burger_reference_limits` |  |
| QVQ-2 | `20260610T004932Z_phase3_qvq_2_quartic_execute` | `sim_time_reached` | 0.566523954342404 | 0.566523954342404 | 150.756 | 0.5887815987440707 | 26.93929891882063 | 0.2419026343264141 | 0.75 | 87.14532796035418 | `exceeds_turtlebot3_burger_reference_limits` |  |
| QRT-VWZ-LV-RW | `20260610T010918Z_phase3_qrt_vwz_low_vx_real_wz_execute` | `sim_time_reached` | 0.6547592992063592 | 0.6547592992063592 | 267.784 | 0.6833732296852681 | 15.063736603419722 | 0.05 | 0.75 | 31.613959150526483 | `within_turtlebot3_burger_reference_limits` |  |
| QRT-VWZ-RV-LW | `20260610T011816Z_phase3_qrt_vwz_real_vx_low_wz_execute` | `sim_time_reached` | 0.5543288953050887 | 0.5543288953050887 | 142.392 | 0.5752632974994959 | 25.230460619573158 | 0.2419026343264141 | 0.25 | 75.71510932011807 | `exceeds_turtlebot3_burger_reference_limits` |  |

## Classification

- A result: supported. `QRT-A-HB` converged to the convex quartic target within
  2 m, while paired `QRT-A-GF` did not. This supports the case where baseline
  HBESC helps and Gaussian fill is neutral or worse.
- B result: not supported by this minimal matrix. `QRT-B-HB` and `QRT-B-GF`
  both failed to reach the global target on the double-well quartic, and the
  one-fill Gaussian-fill run was worse by final and tail distance.
- C result: supported. `QRT-C-REAL` and `QRT-C-FAST` converged faster but
  exceeded TurtleBot3 Burger reference wheel limits. `QRT-C-SLOW` stayed within
  reference limits and converged more slowly, so physical command limits matter.
- QVQ result: quadratic and quartic both converged under the same real-speed
  controller; the quadratic case reached the success radius faster.
- VWZ result: reducing `vx` while keeping real `wz` remained physically valid
  but slowed convergence. Reducing only `wz` still exceeded wheel RPM due to
  forward command limits.

## Invalidated Run

- `20260609T234054Z_phase3_qrt_b_hb_execute` is retained in the manifest with
  status `invalid_start_mismatch`. It is not used as Phase 3 evidence.

## Next Command

Phase 4 should start with HBESC gain-sensitivity scenario scaffolding before
execution. No Phase 4 execute command is ready until low/default/high gain
scenario configs are added.
