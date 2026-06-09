# HBESC Gain Trace

This trace was verified from the local repo on 2026-06-09.

## Active Controller Config Values

| Config | k_vx | k_wz | HB k | beta | input_gain | initial_values | wheel_radius | wheel_distance | wheel_max_rpm | set_max_vx | set_max_wz |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| `hbesc_baseline_slow_full_rotation.json` | 0.2 | 2.0 | 1.0 | 0.1 | -1.0 | `[0.0, 0.0]` | 0.033 | 0.158 | 70 | 0.05 | 0.25 |
| `hbesc_baseline_real_full_rotation.json` | 0.2 | 2.0 | 1.0 | 0.1 | -1.0 | `[0.0, 0.0]` | 0.033 | 0.158 | 70 | null | 0.75 |
| `hbesc_baseline_fast_sim_full_rotation.json` | 0.2 | 2.0 | 1.0 | 0.1 | -1.0 | `[0.0, 0.0]` | 0.033 | 0.158 | 70 | 0.4 | 1.25 |
| `hbesc_gaussian_conservative_full_rotation.json` | 1.0 | 5.0 | 0.1 | 1.0 | -1.0 | `[0.0, 0.0]` | 0.033 | 0.158 | 70 | 0.05 | 0.25 |

With `wheel_radius = 0.033` and `wheel_max_rpm = 70`, the computed non-overridden forward limit is about `0.242 m/s`. With `wheel_distance = 0.158`, the computed non-overridden in-place yaw limit is about `3.063 rad/s`. The real-speed baseline overrides yaw to `0.75 rad/s` and leaves forward speed computed from wheel RPM.

## Baseline HBESC Parameters

### k_vx

- Config key: `gains.k_vx`.
- File/function: `turtlebot_vehicle.py:Rotating_Frame_Directional_Controller.controller_output`.
- Role: maps HBESC relative update direction component 0 to robot forward velocity `vx`.
- Increase: faster forward motion, more basin-escape authority, higher saturation risk, higher wheel RPM burden, more overshoot risk near optimum.
- Decrease: slower motion, lower saturation, potentially unable to escape local basins or reach target in allotted sim time.
- Sweep: yes. Use low/default/high around baseline real `0.2`.

### k_wz

- Config key: `gains.k_wz`.
- File/function: `turtlebot_vehicle.py:Rotating_Frame_Directional_Controller.controller_output`.
- Role: maps HBESC relative update direction component 1 to robot yaw command `wz`.
- Increase: faster heading correction, but more oscillation and yaw saturation risk.
- Decrease: gentler turning, but may prevent alignment with the estimated descent/update direction.
- Sweep: yes. Use low/default/high around baseline real `2.0`.

### HeavyBall k

- Config key: `dynamic_states.ode.k`.
- File/function: `turtlebot_ode_objects.py:HeavyBallODE.__init__`, then `HeavyBallODE.differential_equation`.
- Role: gradient gain passed to `HeavyBallFlow(k, beta)`.
- Increase: stronger response to gradient estimate, faster apparent convergence if stable, higher velocity saturation and oscillation risk.
- Decrease: slower response, less saturation, more failure risk in flat quartic regions.
- Sweep: yes. Use low/default/high around baseline real `1.0`.

### beta

- Config key: `dynamic_states.ode.beta`.
- File/function: `turtlebot_ode_objects.py:HeavyBallODE.__init__`.
- Role: momentum damping coefficient passed to `HeavyBallFlow(k, beta)`.
- Increase: more damping, potentially less oscillation but slower progress and less escape energy.
- Decrease: less damping, potentially faster escape but more oscillation, overshoot, and saturation.
- Sweep: yes. Use low/default/high around baseline real `0.1`.

### input_gain

- Config key: `dynamic_states.ode.input_gain`.
- File/function: `turtlebot_ode_objects.py:HeavyBallODE.differential_equation`.
- Role: multiplies the first two filter outputs before interpreting them as gradient estimates. Current configs use `-1.0` because the filter output is a descent-direction estimate rather than raw `grad J`.
- Increase in magnitude: stronger effective gradient signal before HB flow.
- Sign change risk: likely reverses descent/ascent convention and should not be swept casually.
- Sweep: no for initial study; keep fixed unless debugging sign convention.

### initial_values

- Config key: `dynamic_states.initial_values`.
- File/function: `turtlebot_vehicle.py:Rotating_Frame_Directional_Controller.__init__`.
- Role: initial momentum/dynamic state vector for HBESC.
- Increase/change: could create initial motion bias and confound comparisons.
- Sweep: no for first matrix; keep `[0.0, 0.0]`.

## Physical And Controller Constraints

### wheel_radius, wheel_distance, wheel_max_rpm

- Config keys: `params.wheel_radius`, `params.wheel_distance`, `params.wheel_max_rpm`.
- File/function: `turtlebot_vehicle.py:Rotating_Frame_Directional_Controller.__init__`.
- Role: compute default `max_vx` and `max_wz`.
- Sweep: no. Treat as physical metadata unless testing model mismatch.

### set_max_vx

- Config key: `params.set_max_vx`.
- File/function: `turtlebot_vehicle.py:Rotating_Frame_Directional_Controller.__init__`.
- Role: overrides computed forward velocity limit when not null.
- Increase: can expose speed threshold for escape, but values above TurtleBot3 Burger real speed are simulation-only.
- Decrease: tests physical lower bounds and trapped behavior.
- Sweep: yes in `vx` sensitivity.

### set_max_wz

- Config key: `params.set_max_wz`.
- File/function: `turtlebot_vehicle.py:Rotating_Frame_Directional_Controller.__init__`.
- Role: overrides computed yaw-rate limit when not null.
- Increase: can improve turning authority but may cause oscillation and wheel RPM spikes.
- Decrease: tests alignment limits.
- Sweep: yes in `wz` sensitivity.

## Filter Parameters

Active config: `gesc_filter_full_rotation.json`.

- Washout `omega = 1.0`.
- Sensor lever-arm constant in trigonometric filter: `d = 0.18`.
- Final filter signs are `-1*u[0]*u[1]` and `-1*u[0]*u[2]`.

Sweep: not in the first gain matrix. Keep fixed while isolating HBESC gains and command limits.

## Sensor Rotation Parameters

Active configs:

- `full_rotation.json`: `Constant_Full_Rotation`, `spin_rpm = 20`.
- `full_rotation_acoustic.json`: `Constant_Full_Rotation`, `spin_rpm = 10`.

File/function: `spin_profile_objects.py:Constant_Full_Rotation.velocity_output`.

Interpretation:

- This controls rotating sensor joint speed, not robot yaw.
- Increasing spin speed changes sampling/excitation of the cost field and may improve gradient information up to hardware/timing limits.
- Decreasing spin speed may weaken gradient estimates or slow filter convergence.

Sweep: yes, but separately from `wz`.

## Gaussian-Fill Parameters For Comparison

These are not baseline HBESC gains.

Launch/config parameters:

- `pde_omega`, default launch value `5.0`.
- `convergence_threshold`, default `0.2`.
- `convergence_decay_rate`, default `0.15`.
- `convergence_min_fill_periods`, default `2.0`.
- `gaussian_fill_amplitude`, default `5.0`.
- `gaussian_fill_min_sigma`, default `3.16`.
- `gaussian_fill_max_sigma`, default `5.0`.
- `gaussian_fill_min_points`, default `50`.
- `gaussian_fill_use_recent_fraction`, default `0.2`.
- `gaussian_fill_max_fills`, default `1`.
- `gaussian_fill_cooldown_sec`, default `0.0`.
- `gaussian_fill_min_distance_between_fills`, default `0.0`.

Implementation:

- `pde_history_script.py:PDEHistory` uses `omega`, `n_buffer`, `k_periods`, and `cfl`.
- `convergence_detector_node_script.py:ConvergenceDetector` computes the trigger metric.
- `gaussian_fill_script.py:GaussianFill` controls fill policy, amplitude, sigma bounds, point count, recency, max fills, cooldown, and spacing.

Initial policy: keep `conditional_gaussian_fill` with `max_fills = 1` until one-fill behavior is understood.

## First Gain Sensitivity Recommendation

Use the real-speed baseline config on a representative quartic field. Sweep one variable at a time:

- `k_vx`: low/default/high.
- `k_wz`: low/default/high.
- HeavyBall `k`: low/default/high.
- HeavyBall `beta`: low/default/high.

Hold filter config, spin config, initial state, cost function, and physical limits fixed. Record final distance, time to convergence, path length, cost, `vx`, `wz`, estimated wheel RPM, saturation percentage, and failure mode.
