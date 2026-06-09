# HeavyBall ESC vs Gaussian Fill Master Experiment Plan

## 0. Purpose Of This Document

This is the master handoff plan for the HeavyBall ESC versus Gaussian fill study in
the local `dsim-lab` repository. It combines:

- the original Plan Mode prompt requirements,
- the inspected repository-backed `PLAN.md`,
- the Goal Mode implementation requirements,
- the later quartic, `vx`/`wz`, and HBESC gain-sensitivity requirements, and
- the broader thesis characterization direction suggested in the Claude discussion.

The local repository is the source of truth. Do not assume file names, class
names, launch arguments, controller equations, or algorithm details that conflict
with the repo. Re-inspect the repo at the start of implementation because these
paths and configs are checkout-specific.

The central research goal is not just to run a few case studies. The goal is to
characterize when HeavyBall ESC succeeds, when it fails, when Gaussian fill
helps, when Gaussian fill hurts or is unnecessary, and which TurtleBot3 Burger
physical limits constrain mathematically successful behavior.

The existing 15 baseline tests should be treated as a pilot study. They are useful
evidence, but they are not yet a broad characterization. A thesis-grade study
should sweep clean axes of cost-landscape geometry, initial condition, controller
limits, and gains.

## 1. Research Questions

The professor-facing tasks are:

1. Identify scenarios where baseline HeavyBall ESC can help, but Gaussian fill
   cannot or underperforms.
2. Identify scenarios where baseline HeavyBall ESC cannot help, but Gaussian fill
   can.
3. For scenarios where HBESC can help, identify the physical limitations that
   exist for the TurtleBot3 Burger.

The broader master's research framing is:

1. What properties of the cost landscape determine whether HeavyBall ESC succeeds
   or fails?
2. What minimum robot speed or command authority is needed to escape a local
   basin of a given barrier height?
3. How does convergence rate on single-well functions depend on local curvature,
   especially for quartic versus quadratic objectives?
4. How gracefully does HBESC degrade as the landscape gets flatter, steeper,
   more asymmetric, more cross-coupled, or more multimodal?
5. Which HBESC gains matter most, and how do they trade convergence speed,
   oscillation, saturation, noise sensitivity, and physical feasibility?
6. Does Gaussian fill solve failure modes that baseline HBESC cannot solve, or
   does it sometimes distort an otherwise useful HBESC trajectory?

## 2. Operational Definitions

Baseline HBESC:

- `use_pde_extensions:=False`
- `escape_policy:=none`
- raw cost signal from cost function node feeds the GESC filter
- filter output feeds `Rotating_Frame_Directional_Controller`
- controller dynamic state uses `HeavyBallODE`
- no `modified_cost_node`, `pde_history_node`, `convergence_detector_node`, or
  `gaussian_fill_node`

Gaussian fill method:

- HBESC plus PDE/modified-cost extension
- `use_pde_extensions:=True`
- `escape_policy:=conditional_gaussian_fill` for the primary one-fill study
- `escape_policy:=multi_gaussian_fill` only after one-fill behavior is understood
- `convergence_detector_node` detects convergence or trapping from `/pde_history`
- `gaussian_fill_node` publishes `/cost_bias` as `[A, mu_x, mu_y, sigma]`
- `modified_cost_node` adds positive Gaussian bias to the cost field before
  filtering, effectively discouraging return to the filled basin

Success:

- the robot enters the target success radius and remains well behaved afterward
- primary success radius: `2.0 m`, matching the existing analyzer convention
- stricter final-report radius: `1.0 m`, reported separately
- final and tail-mean distance to target decrease substantially from the start
- cost improves, logs are finite, and the result is not dependent on
  simulation-only physical violations

Failure:

- never enters target success radius
- remains trapped near local basin, commonly within `1.0 m` of `(2,2)` where a
  local basin exists
- final or tail distance remains large
- unstable, oscillatory, or wide-orbit behavior prevents clean final tracking
- missing, non-finite, or incomplete logs
- success only occurs under nonphysical command limits

Improvement:

- lower final distance to target/source
- lower tail-mean distance
- lower final or best cost value
- faster first entry into success radius
- higher percent of run inside success radius
- shorter or more efficient path, when consistent with convergence
- fewer saturation events or more physically plausible command profile

Physical infeasibility:

- commanded translational speed exceeds or sits at the TurtleBot3 Burger limit
- commanded yaw rate exceeds or sits at the configured or real robot limit
- reconstructed wheel RPM exceeds the physical wheel limit
- behavior relies on fast simulation-only controller configs
- Gazebo diff-drive acceleration or torque limits hide unrealistic demanded
  behavior
- rotating sensor assumptions are not realistic for hardware

Actuator saturation:

- controller output is clipped by `set_max_vx`, `set_max_wz`, or computed wheel
  RPM-derived limits
- saturation threshold for analysis: at or above `98%` of configured limit
- saturation is a primary result, not just a plotting detail
- analysis must determine whether saturation changes convergence, causes
  failure, hides unrealistic commands, or makes a mathematically successful
  HBESC result physically questionable

Poor localization / poor final tracking:

- robot reaches the right basin but maintains a large orbit or high tail
  standard deviation near the target
- first target entry occurs, but percent time inside success radius is low
- final position is worse than best position

Unstable or oscillatory behavior:

- repeated large excursions after entering target basin
- high tail distance standard deviation
- high path length after first target entry
- velocity commands remain aggressive near optimum

## 3. Repository Findings To Re-Verify

These findings came from the previous repo inspection. Re-verify them at the
start of Goal Mode because the repo is the source of truth.

Baseline HBESC implementation:

- Controller node entry point:
  `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`
- Controller object:
  `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py`
- HBESC ODE object:
  `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_ode_objects.py`
- Baseline controller configs:
  `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/hbesc_baseline_slow_full_rotation.json`
  `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/hbesc_baseline_real_full_rotation.json`
  `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/hbesc_baseline_fast_sim_full_rotation.json`

Gaussian fill implementation:

- Fill policy and `/cost_bias` publisher:
  `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`
- Modified cost wrapper:
  `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`
- PDE history:
  `ros2_ws/src/ros_esc/ros_esc/pde_history_node/pde_history_script.py`
- Convergence detector:
  `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py`
- Gaussian-fill controller config:
  `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/accelerated_methods/hbesc_gaussian_conservative_full_rotation.json`

Launch and scenario infrastructure:

- Gazebo launch file:
  `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
- Scenario runner:
  `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_scenario_acoustic.bash`
- Direct baseline scripts:
  `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_acoustic.bash`
  `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_escape_shallow_acoustic.bash`
- Direct Gaussian-fill script:
  `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/accelerated_methods/hb_gaussian_fill_acoustic.bash`
- Important scenario-runner constraint:
  `hb_scenario_acoustic.bash` has a whitelist of launch keys. If new launch
  arguments are added, update this whitelist or scenario JSONs will fail with
  unknown-key errors.

Cost fields:

- HeavyBall cost maps:
  `ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/`
- Existing families:
  `polynomial_quadratic_bowl_center10.json`
  `polynomial_quartic_bowl_center10.json`
  `polynomial_quartic_double_well_local2_global10.json`
  `gaussian_two_basin_original.json`
  `gaussian_two_basin_localA1p0.json`
  `gaussian_two_basin_localA2p0.json`
  `gaussian_two_basin_localA3p0.json`
  `gaussian_two_basin_globalW25.json`
  `gaussian_two_basin_globalW30.json`
  `gaussian_two_basin_globalW40.json`

Filter and sensor rotation:

- Main filter used by HBESC scenarios:
  `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json`
- Full rotation config:
  `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json`
- Acoustic full rotation variant:
  `ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation_acoustic.json`
- Sensor transform:
  `ros2_ws/src/ros_esc/ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json`

Data logging:

- Data collection node:
  `ros2_ws/src/ros_esc/ros_esc/data_collection_node/data_collection_node_script.py`
- Existing logged CSVs:
  `odometry.csv`
  `sensor_transform.csv`
  `cost_value.csv`
  `filter_value.csv`
  `control_value.csv`
  `comments.txt`
- Current gap:
  PDE/Gaussian mode logs modified cost as `cost_value.csv`, but raw cost,
  `/cost_bias`, `/convergence_event`, `/convergence_metric`, and
  `/convergence_r` are not part of the normal data collection output. Add a
  lightweight diagnostic recorder or extend logging before full runs.

Physical model:

- TurtleBot URDF:
  `ros2_ws/src/turtlebot3_rotating_sensor/urdf/turtlebot3_rotating_sensor.urdf`
- Controller config:
  `ros2_ws/src/turtlebot3_rotating_sensor/controller_config/joint_controller.yaml`
- Diff-drive plugin publishes `/odom`, listens to `/cmd_vel`, uses wheel
  separation around `0.160 m`, wheel diameter `0.066 m`, update rate `30 Hz`,
  max wheel torque `20`, and max wheel acceleration `1.0`.
- Controller configs use wheel radius `0.033 m`, wheel distance `0.158 m`,
  wheel max RPM `70`.

Gaussian-related candidates that are not the Gaussian fill implementation:

- `gaussian_two_basin_*.json` are Gaussian-shaped cost maps.
- `static_2D_gaussian.json` is a static cost function config.
- `hbesc_gaussian_conservative_full_rotation.json` is controller tuning.
- The actual fill logic is the combination of `gaussian_fill_node`,
  `modified_cost_node`, `pde_history_node`, and `convergence_detector_node`.

## 4. Code Understanding / Algorithm Trace Requirements

Before running the full experiment sweep, create:

`experiments/hbesc_gaussian_fill_study/code_trace.md`

This document must explain, with exact file/function references from the local
repo:

- full ROS2/Gazebo node pipeline
- how robot pose is obtained from `/odom`
- how rotating sensor angle is obtained from `/joint_states`
- how rotating sensor pose is computed from odometry, encoder, and transform
  config
- where the cost function is computed
- how cost noise is added
- how the filter uses cost and encoder data
- how baseline HBESC computes its control action
- how Gaussian fill changes the cost signal
- where `vx` and `wz` are generated
- where `vx` and `wz` are limited or saturated
- where the final `Twist` is published to `/cmd_vel`
- what changing `vx` physically means for the TurtleBot3 Burger
- what changing `wz` physically means for the TurtleBot3 Burger
- whether `wz` affects the robot yaw rate, the rotating sensor speed, or both
  in the current implementation
- how sensor rotation speed affects sampling and gradient information
- which logged topics/files verify each step
- which data streams must be added for Gaussian-fill diagnostics

Important distinction:

- `vx` and `wz` in `control_value.csv` are robot body linear and angular command
  values from the controller.
- Rotating sensor angular velocity is commanded separately by the rotate-frame
  node and its spin profile. Do not conflate robot yaw command `wz` with rotating
  sensor spin rate.

## 5. HBESC Gain Interpretation And Sensitivity Requirements

Before running the full sweep, create:

`experiments/hbesc_gaussian_fill_study/hbesc_gain_trace.md`

This document must identify all baseline HBESC tunable parameters from the local
repo, not from memory. For each parameter include:

- variable/config name
- file and function where it appears
- default value in each active config
- mathematical role in the controller or ODE
- physical/control interpretation
- expected effect of increasing it
- expected effect of decreasing it
- possible failure modes if too small
- possible failure modes if too large
- expected effect on convergence speed
- expected effect on oscillation/stability
- expected effect on velocity saturation and wheel RPM feasibility
- expected effect on noise sensitivity
- whether to include it in the experiment sweep

Known parameters to re-verify:

- vehicle feedback gains:
  `k_vx`, `k_wz`
- HeavyBall ODE parameters:
  `k`, `beta`, `input_gain`
- dynamic-state initial values:
  `initial_values`
- physical/controller constraints:
  `wheel_radius`, `wheel_distance`, `wheel_max_rpm`, `set_max_vx`, `set_max_wz`
- filter parameters:
  washout `omega` and filter function constants in the active GESC filter config
- sensor rotation parameters:
  `spin_rpm`, rotation profile type, and back-and-forth bounds if used
- Gaussian-fill parameters, for comparison but not as baseline HBESC gains:
  `pde_omega`, convergence threshold, decay rate, min fill periods,
  fill amplitude, min/max sigma, min points, recent fraction, max fills,
  cooldown, and min distance between fills

The gain study should not be a huge random sweep. Use a low/default/high design
for the most important gains on one representative quartic field first.

Suggested first gain-sensitivity set:

- baseline real-speed config as default
- `k_vx`: low, default, high
- `k_wz`: low, default, high
- HeavyBall `k`: low, default, high
- HeavyBall `beta`: low, default, high
- keep all other parameters fixed while sweeping one variable at a time
- only test interaction pairs after one-at-a-time results show a clear effect

Each gain trial must record:

- gain values used
- scenario/cost function
- final distance to optimum/source
- time to convergence
- path length
- cost vs time
- oscillation near optimum
- commanded `vx`
- commanded `wz`
- estimated left/right wheel RPM
- saturation events
- convergence/non-convergence label
- failure mode if applicable

Final report must directly answer:

- which HBESC gains matter most
- what each important gain appears to do
- which gains improve quartic convergence
- which gains cause oscillation, saturation, or physical infeasibility
- how gain choice changes the comparison between HBESC and Gaussian fill

## 6. Cost Landscape Characterization Strategy

The 15 prior tests are a pilot study, not a full characterization. They include
useful cases, but they mostly show selected case studies:

- single-well quadratic sanity checks
- single-well quartic sanity checks
- quartic double-well local trapping
- Gaussian two-basin local/global behavior
- slow, real, and fast simulation-only speed regimes

For a master's thesis, the stronger framing is to sweep meaningful axes of the
cost landscape and controller limits. The main scientific question becomes:

What cost-landscape properties and controller settings determine whether HBESC
succeeds, fails, or degrades?

The most important landscape axes are:

- barrier height between local and global basin
- basin width asymmetry
- tilt magnitude or global drift strength
- local curvature near a minimum
- flatness/plateau strength
- cross-coupling and asymmetry
- starting position relative to basin
- speed or command authority
- noise and sensing degradation

The double-well family should become a parameterized characterization tool,
not only a single named cost map. Use a family such as:

```text
u = (x + y) / 2
J(x,y; alpha, beta, gamma) =
  alpha * (u - 2)^2 * (u - 10)^2
  + beta * (x - y)^2
  - gamma * u
```

Interpretation:

- `alpha` controls barrier height and basin steepness along the main valley.
- `beta` controls cross-valley stiffness and penalizes deviation from `x = y`.
- `gamma` controls global tilt toward the larger-`u` basin.

This family supports thesis-grade questions:

- What is the minimum speed needed to escape a double-well of a given barrier
  height?
- Does escape follow a threshold curve in speed versus barrier height?
- How strong must global tilt be before HBESC escapes reliably?
- How does cross-coupling affect oscillation and final tracking?
- How do Gaussian fills change the escape boundary?

Practical expanded scope:

- 2 to 3 cost function families
- 2 to 3 internal parameters per family
- 5 to 8 speed settings per selected condition
- 3 to 5 starting positions per selected condition
- roughly 100 to 200 total runs only after automation is reliable

The primary thesis output should shift from a yes/no table to curves and maps:

- escape probability versus barrier height and speed
- critical speed for escape versus barrier height
- convergence rate versus local curvature
- final tracking quality versus speed/gain
- saturation burden versus success probability
- Gaussian-fill benefit region in the same landscape parameter space

## 7. Quartic Function Emphasis

Quartic functions must be a primary focus, not an afterthought. Include quartic
test cases before or alongside quadratic cases.

Minimum quartic family requirements:

- one convex quartic well
- one shallow quartic well
- one steep quartic well
- one shifted quartic minimum
- one asymmetric or cross-coupled quartic case
- one direct quadratic-versus-quartic comparison using similar initial
  conditions
- one quartic double-well local-escape case

Why each quartic matters:

- Convex quartic well:
  tests basic convergence when the landscape is smooth but flatter near the
  optimum than a quadratic.
- Shallow quartic well:
  tests weak-gradient/plateau behavior, slow convergence, and noise sensitivity.
- Steep quartic well:
  tests aggressive gradients, saturation, overshoot, and oscillation.
- Shifted quartic minimum:
  tests sensitivity to source distance and whether behavior changes with travel
  distance.
- Asymmetric quartic:
  tests unequal curvature along axes and whether the controller follows the
  easier direction or oscillates.
- Cross-coupled quartic:
  tests whether the gradient-estimation and body-frame conversion handle
  rotated valleys and non-axis-aligned geometry.
- Quartic double-well:
  tests local trapping, barrier crossing, and motivation for Gaussian fill.
- Quadratic-versus-quartic pair:
  isolates curvature/flatness while holding start, target, and physical limits
  constant.

Candidate quartic formulas to implement as configs after verifying parser
support:

- convex quartic center `(10,10)`:
  `a*((x-10)^4 + (y-10)^4)`
- shallow quartic:
  smaller `a`, such as `0.0001` around the existing `0.0005`
- steep quartic:
  larger `a`, such as `0.001` or `0.002`
- shifted quartic:
  `a*((x-x0)^4 + (y-y0)^4)` for several `(x0,y0)`
- asymmetric quartic:
  `a_x*(x-x0)^4 + a_y*(y-y0)^4`
- cross-coupled quartic:
  `a*((x+y)/sqrt(2)-u0)^4 + b*((x-y)/sqrt(2)-v0)^4`
- double-well family:
  parameterized `alpha`, `beta`, `gamma` expression above

Do not invent final parameter values blindly. Start from existing configs and
derive small, controlled variations. Document the chosen values in generated
scenario metadata and copied configs.

## 8. vx / wz Sensitivity Study

Add a dedicated `vx`/`wz` sensitivity study. This is not just a plotting
exercise. It must determine whether command limits change controller behavior,
cause failure, hide unrealistic commands, or make a mathematically successful
HBESC case physically questionable.

Clarify first:

- In controller outputs, `vx` is the robot forward linear velocity command.
- In controller outputs, `wz` is the robot yaw-rate command.
- Rotating sensor spin speed is controlled separately by rotate-frame configs.

The study should vary:

- translational command authority through `set_max_vx` and/or `k_vx`
- robot yaw command authority through `set_max_wz` and/or `k_wz`
- sensor spin rate through rotate-frame `spin_rpm`, as a separate factor

Do not make a large grid at first. Use a representative quartic case and a small
controlled grid, such as:

- `set_max_vx`: `0.05`, `0.10`, `0.15`, `0.20`, real/controller default,
  `0.30`, fast sim-only
- `set_max_wz`: `0.25`, `0.50`, `0.75`, `1.00`, `1.25`
- sensor `spin_rpm`: `10`, `20`, possibly `30` only after smoke tests

For each selected scenario, record:

- convergence or non-convergence
- final distance to source/minimum
- time to convergence
- path length
- oscillation near the minimum
- commanded translational velocity
- commanded angular velocity
- estimated wheel RPM
- saturation events
- percent of samples near or beyond physical limits
- whether behavior is physically feasible for TurtleBot3 Burger

Scientific failure modes to reveal:

- insufficient `vx` prevents escape from local basin
- excessive `vx` causes overshoot or wide orbit
- insufficient `wz` prevents alignment or produces slow turning
- excessive `wz` causes oscillation and poor final tracking
- sensor spin too slow gives poor gradient information
- sensor spin too fast may exceed hardware realism or degrade filter timing
- saturation makes different gain settings look artificially similar

## 9. Physical Limitation Analysis

Use repo values where available and compare against known TurtleBot3 Burger
limits.

Known comparison values from the goal prompt:

- max translational speed: `0.22 m/s`
- max angular speed: `2.84 rad/s`
- wheel radius: expected around `0.033 m`, use repo value when available
- wheel separation: expected around `0.158 m`, use repo/controller value when
  available
- wheel max RPM: expected around `70 RPM`, use repo value when available

Existing controller-derived values to verify:

- `wheel_radius = 0.033`
- `wheel_distance = 0.158`
- `wheel_max_rpm = 70`
- real-speed controller `set_max_vx = null`, so forward speed is computed from
  wheel radius and RPM
- real-speed controller `set_max_wz = 0.75`
- slow controller `set_max_vx = 0.05`, `set_max_wz = 0.25`
- fast simulation-only controller `set_max_vx = 0.40`, `set_max_wz = 1.25`

Wheel reconstruction:

```text
omega_left_rad_s  = (v - omega * L / 2) / r
omega_right_rad_s = (v + omega * L / 2) / r
rpm = omega_rad_s * 60 / (2*pi)
```

For every run compute:

- max commanded linear velocity
- max commanded angular velocity
- max left and right wheel RPM
- percent of samples exceeding known TurtleBot3 limits
- percent of samples at or near configured saturation
- duration of saturation or violation
- whether the result is physically plausible on real TurtleBot3 Burger
- whether a success depends on fast simulation-only settings
- whether saturation changes behavior or hides what the unconstrained controller
  would have commanded

Physical limitations to discuss:

- maximum translational speed
- maximum angular speed
- wheel RPM limit
- acceleration/aggressiveness of commands
- turning radius and tight oscillatory maneuvers
- payload and sensor mounting assumptions
- simulation commands that exceed real specs
- finite battery/runtime implications
- rotating sensor hardware realism
- Gazebo diff-drive acceleration and torque behavior

## 10. Metrics And Data Products

For every run measure:

- final distance to optimum/source
- minimum distance to optimum/source over time
- time to enter success radius
- percentage of run spent inside success radius
- final cost value
- best cost value
- convergence rate estimate
- path length
- commanded linear velocity `vx`
- commanded angular velocity `wz`
- estimated wheel RPMs
- number and duration of saturation events
- oscillation amplitude near optimum
- tail-mean distance and tail standard deviation
- failure mode label
- wall-clock runtime
- sim-time duration
- data quality and missing-log checks
- Gaussian fill event time and parameters, when applicable
- convergence metric and `r` history, when applicable
- raw cost and modified cost, when applicable

Plots:

- trajectory over cost/source field
- cost versus time
- raw and modified cost versus time for Gaussian-fill runs
- distance to optimum/source versus time
- commanded `vx` and `wz` versus time
- estimated wheel RPM versus time
- saturation-event timeline
- convergence metric timeline
- fill event markers on cost/distance plots
- comparison bar plots
- escape probability heatmaps for characterization sweeps
- critical speed curves
- failure-mode summary plots
- representative Gazebo screenshots if feasible

Tables:

- results manifest
- trial metadata table
- summary metrics table
- failure-mode table
- physical-limit table
- scenario classification table
- gain-sensitivity table
- speed/barrier sweep table

## 11. Controls And Fair Comparison Rules

For paired HBESC versus Gaussian-fill comparisons:

- same initial condition
- same yaw
- same source/cost field
- same noise setting and seed when noise exists
- same simulation duration
- same success criteria
- same filter config
- same controller physical constraints unless testing controller differences
- same sensor transform
- same sensor rotation strategy unless testing spin sensitivity
- same logging format
- same post-processing
- same target and local-basin metadata
- same manually placed visual light sources, if used

Noise policy:

- first matrix should use `No_Noise`
- introduce noise only after deterministic behavior is understood
- use explicit seed values
- repeat noisy trials across multiple seeds

Gaussian-fill policy:

- primary comparison uses `conditional_gaussian_fill` with `max_fills = 1`
- multi-fill is a separate study because prior work noted that repeated fills
  can be injected near the global optimum, which may be undesirable

Physical feasibility policy:

- physically valid conclusions must use real-speed limits
- slow and fast configs are diagnostic sweeps
- fast simulation-only results must be labeled simulation-only

## 12. Minimal Trial Matrix

The minimal matrix must work end-to-end before any expanded sweep. It should
prioritize quartic cases, as requested.

Every trial must record:

- scenario ID
- method
- purpose
- initial x/y/yaw
- cost field/config
- controller config
- filter config
- Gaussian fill parameters, if applicable
- HBESC parameters, if applicable
- simulation duration
- expected outcome
- actual outcome
- success/failure label
- output directory
- required output files

Minimum required cases:

| ID | Research purpose | Method | Init | Cost family | Duration | Expected role |
|---|---|---|---|---|---:|---|
| QRT-A-HB | quartic case where HBESC helps | baseline real | matched | convex or favorable quartic | 500 | baseline success |
| QRT-A-GF | paired fill underperformance test | conditional fill | same | same | 500 | Gaussian fill neutral or worse |
| QRT-B-HB | quartic local-basin baseline failure | baseline real | near local basin | quartic double-well | 700 | trapped/fail |
| QRT-B-GF | fill rescue on quartic local basin | conditional fill | same | same | 700 | fill improves escape |
| QRT-C-SLOW | physical limit lower-bound | baseline slow | same | representative quartic | 700 | too slow or marginal |
| QRT-C-REAL | physical limit valid case | baseline real | same | same | 700 | physically valid benchmark |
| QRT-C-FAST | simulation-only upper-bound | baseline fast | same | same | 700 | success or wide orbit, not real |
| QRT-VWZ | `vx`/`wz` sensitivity mini-grid | baseline | same | representative quartic | 500 | identify command sensitivity |
| QRT-GAIN | HBESC gain low/default/high | baseline | same | representative quartic | 500 | identify important gains |
| QVQ-1 | quadratic-vs-quartic comparison | baseline real | same | quadratic | 500 | curvature baseline |
| QVQ-2 | quadratic-vs-quartic comparison | baseline real | same | quartic | 500 | flatness/curvature contrast |

Keep the first Goal Mode implementation even smaller:

1. create docs and harness skeleton
2. run one smoke test
3. run one quartic baseline trial
4. analyze that one trial
5. stop and summarize before expanding

## 13. Expanded Characterization Matrix

Only expand after the minimal matrix works end-to-end.

Recommended expanded studies:

1. Existing pilot replication:
   - run all 15 existing baseline scenarios or import their prior results
   - add paired Gaussian-fill variants for relevant local-basin and single-well
     cases

2. Quartic curvature sweep:
   - shallow, default, steep convex quartics
   - same start positions
   - same speed limits
   - compare convergence rate, final orbit, saturation

3. Parameterized quartic double-well sweep:
   - sweep barrier height via `alpha`
   - sweep cross-valley stiffness via `beta`
   - sweep tilt via `gamma`
   - measure escape probability and critical speed

4. Speed-limit sweep:
   - 5 to 8 `set_max_vx` values
   - 3 to 5 `set_max_wz` values only for selected cases
   - produce critical speed curves

5. Starting-position grid:
   - 3 to 5 starts per selected cost map
   - map effective basin of attraction
   - report escape probability, not just single-run success

6. Noise/seeding study:
   - add noise only after deterministic characterization
   - 3 to 5 seeds per important condition
   - report confidence/variability

7. Gaussian fill comparison:
   - one-fill policy first
   - multi-fill only after one-fill results are understood
   - explicitly test whether fill placement near target creates harm

## 14. Automation And Harness Plan

Create or update:

`experiments/hbesc_gaussian_fill_study/`

Suggested structure:

```text
README.md
MASTER_PLAN.md
experiment_plan.md
code_trace.md
hbesc_gain_trace.md
configs/
  cost_functions/
  controllers/
  filters/
  scenarios/
scripts/
  run_one_trial.sh
  run_sweep.py
  check_trial_outputs.py
  record_trial_metadata.py
results/
  runs/
  logs/
  summary_tables/
analysis/
  analyze_results.py
  make_plots.py
figures/
results_manifest.csv
final_report_outline.md
final_summary.md
```

Harness requirements:

- run one trial reproducibly
- run a controlled sweep only after smoke test passes
- run each full trial for target sim-time, default `500 s`, not wall-clock time
- use `700 s` where needed for local-basin comparisons
- save stdout/stderr logs
- save exact launch command
- save copied configs used by the trial
- save trial metadata
- save success/failure status
- avoid overwriting prior results
- cleanly terminate ROS/Gazebo processes
- retry failed trial at most once
- record failure details instead of silently skipping
- save notes on skipped simulations

Headless execution:

- preferred only if reliable in the local environment
- existing `empty_world.launch.py` launches `gazebo --verbose`, which is GUI
  oriented
- if true headless mode is needed, add a minimal approved launch path or wrapper
  using `gzserver`/headless Gazebo after verifying local ROS/Gazebo behavior
- do not modify core launch behavior unless necessary

Sim-time monitoring:

- watch `/clock` or another reliable sim-time source
- terminate after configured sim-time duration
- do not rely on `sleep 500`
- if sim-time monitoring is impossible, document it and use wall-clock fallback
  only with explicit warning

Runner safety:

- start with one short smoke test
- do not run full sweep until one trial works end-to-end
- do not delete existing results
- do not kill unrelated user processes
- if cleanup is needed, target only processes started by the runner when possible

## 15. Implementation Phases

### Phase 1: Repository Verification And Documentation

Goal:

- verify current implementation against this master plan
- create the experiment directory and foundational docs
- do not run long Gazebo simulations

Deliverables:

- `experiment_plan.md`
- `code_trace.md`
- `hbesc_gain_trace.md`
- initial trial matrix under `configs/scenarios/` or as a manifest
- `README.md`
- empty or initialized `results_manifest.csv`

Verify:

- baseline HBESC implementation
- Gaussian fill implementation
- Gazebo launch path
- scenario runner
- logging behavior
- sim time availability
- TurtleBot3 command generation
- velocity saturation
- wheel RPM reconstruction
- current cost/config/controller/filter paths

### Phase 2: Experiment Harness

Goal:

- create runnable harness scripts
- run no more than a short smoke test unless explicitly continuing

Deliverables:

- `scripts/run_one_trial.sh`
- `scripts/run_sweep.py`
- `scripts/check_trial_outputs.py`
- `analysis/analyze_results.py`
- `analysis/make_plots.py`
- one smoke-test log directory
- manifest row for the smoke test

### Phase 3: Minimal Quartic Matrix

Goal:

- run the minimal quartic-focused matrix
- classify at least one A, B, and C result if data supports it

Priorities:

1. quartic scenario where HBESC helps but Gaussian fill does not
2. quartic scenario where Gaussian fill helps but HBESC does not
3. quartic scenario where HBESC helps mathematically but physical limits matter
4. one `vx`/`wz` sensitivity study on a representative quartic case

### Phase 4: HBESC Gain Sensitivity

Goal:

- run low/default/high sensitivity for the most important gains
- use a representative quartic field
- avoid unmanageable grids

### Phase 5: Expanded Characterization

Goal:

- run parameterized sweeps only after minimal matrix and scripts are reliable
- produce characterization curves and heatmaps

Potential outputs:

- escape probability versus barrier height and speed
- critical speed versus barrier height
- convergence rate versus quartic curvature
- saturation burden versus success
- Gaussian-fill benefit region

### Phase 6: Final Report Draft

Create:

- `final_report_outline.md`
- `final_summary.md`, if enough data exists

The summary must answer:

1. What scenarios show HBESC helping when Gaussian fill does not?
2. What scenarios show Gaussian fill helping when HBESC does not?
3. What TurtleBot3 Burger physical limitations appear when HBESC is successful?
4. Which results are strong, weak, or inconclusive?
5. Which HBESC gains matter most?
6. What does each important gain appear to do?
7. Which gains improve quartic convergence?
8. Which gains cause oscillation, saturation, or physical infeasibility?
9. How does gain choice change the comparison between HBESC and Gaussian fill?
10. What should be run next?

## 16. Report Outline

1. Introduction
2. Background on ESC, HBESC, and Gaussian fill
3. Simulation platform and TurtleBot3 Burger physical limits
4. Code and algorithm trace
5. Experimental design
6. Pilot results from existing 15 baseline tests
7. Quartic cost-function characterization
8. Scenario class A: HBESC helps but Gaussian fill cannot
9. Scenario class B: Gaussian fill helps but HBESC cannot
10. Scenario class C: TurtleBot3 physical limitations
11. `vx`/`wz` and speed-limit sensitivity
12. HBESC gain sensitivity
13. Broader characterization: escape probability and critical speed
14. Results
15. Discussion
16. Limitations
17. Future work
18. Appendix: configs, commands, trial manifest, raw metrics

## 17. Risks And Open Questions

Resolve before full runs:

- exact current implementation details may drift; re-inspect repo first
- Gaussian fill diagnostics are not fully logged by default
- PDE mode logs modified cost instead of raw cost
- sim-time monitoring must be verified
- headless Gazebo support must be verified
- velocity saturation must be distinguished from real convergence behavior
- wheel RPM is reconstructed unless direct wheel commands are logged
- multi-fill can inject fills near the global optimum
- new launch args require scenario-runner whitelist updates
- automated cleanup must not kill unrelated ROS/Gazebo work
- large sweeps can become unmanageable; minimal matrix comes first
- exact quartic parameter values should be chosen scientifically and documented
- if noisy trials are used, random seed behavior must be verified

## 18. Safety And Execution Rules

- Start with one short smoke test before any full 500-second run.
- Do not run the full sweep until one trial works end-to-end.
- Do not delete existing experiment results.
- Do not modify core package files unless absolutely necessary.
- Prefer new experiment scripts/configs/docs under
  `experiments/hbesc_gaussian_fill_study/`.
- If modifying source code is necessary, explain why and keep the change minimal.
- Save all logs.
- Save exact configs and launch commands.
- Use clear commit-style summaries of changes.
- Keep the experiment reproducible.
- If the goal becomes too large, finish the minimal matrix first before expanding.
- If full simulations cannot be completed because of environment limits, token
  limits, Gazebo failures, or missing details, stop with a complete status
  summary, saved logs, and the next exact command/action needed.

## 19. Completion Checklist

- experiment directory exists
- master plan exists
- professor-facing `experiment_plan.md` exists
- `code_trace.md` exists
- `hbesc_gain_trace.md` exists
- trial matrix exists
- one-trial runner exists
- sweep runner exists or is documented
- output checker exists
- analysis scripts exist
- plot scripts exist
- at least one smoke test attempted
- full runs completed where possible
- results manifest populated
- plots generated where possible
- physical-limit analysis completed where possible
- gain analysis completed where possible
- final summary/report outline written
- failures/blockers documented

## 20. Recommended First Goal Mode Session

Use this as the first new-chat prompt:

```text
Read and follow:
- /home/mattb/dsim-lab/experiments/hbesc_gaussian_fill_study/MASTER_PLAN.md

Execute Phase 1 only.

Create or update:
- experiments/hbesc_gaussian_fill_study/README.md
- experiments/hbesc_gaussian_fill_study/experiment_plan.md
- experiments/hbesc_gaussian_fill_study/code_trace.md
- experiments/hbesc_gaussian_fill_study/hbesc_gain_trace.md
- experiments/hbesc_gaussian_fill_study/results_manifest.csv
- initial configs/scenarios structure if needed

Re-inspect the local repo before writing claims. The repo is the source of
truth. Do not run long Gazebo simulations. Do not run a full 500-second trial.
Only run lightweight validation, JSON/XML parsing, bash syntax checks, and
scenario dry-runs if useful.

Stop after Phase 1 with:
- files created/updated
- exact repo facts found
- unresolved questions
- next exact command for Phase 2 smoke test
```

Stop conditions for first Goal Mode session:

- stop if a required implementation path cannot be verified
- stop if a write requires editing core package files and the reason is not
  clear
- stop if scenario-runner or launch behavior is inconsistent with this plan
- stop before full simulation execution
- stop after foundational docs and skeleton are complete

## 21. Recommended Later Goal Mode Splits

Use separate sessions to preserve context and reduce risk:

1. Phase 1: docs, repo trace, gain trace, scenario skeleton
2. Phase 2: one short smoke test and harness fixes
3. Phase 3: minimal quartic matrix
4. Phase 4: `vx`/`wz` and gain sensitivity
5. Phase 5: expanded characterization sweeps
6. Phase 6: final plots, tables, report summary

Each new session should start by reading:

```text
experiments/hbesc_gaussian_fill_study/MASTER_PLAN.md
experiments/hbesc_gaussian_fill_study/README.md
experiments/hbesc_gaussian_fill_study/results_manifest.csv
```

Then it should read phase-specific files such as `code_trace.md`,
`hbesc_gain_trace.md`, current scenario configs, and current summary tables.

