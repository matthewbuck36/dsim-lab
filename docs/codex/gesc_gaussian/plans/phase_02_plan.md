# Phase 02 Plan — Explicit GESC/Gaussian Hybrid State Machine

## Post-implementation Amendment 1 — shutdown-zero proof (2026-07-21)

The Phase 04 visible Gazebo smoke showed that Phase 02's shutdown-zero
requirement was correct but its original evidence was incomplete. Calling a
node's `destroy_node()` directly while ROS is valid proves the zero-publish
method, but does not prove the executable's real SIGINT lifecycle. With
rclpy's automatic signal handlers, the context was already invalid when the
controller and supervisor cleanup paths attempted their final publish.

This amendment strengthens the Phase 02 contract without changing its state
machine, command arbitration, watchdog, topics, cost semantics, or legacy
behavior:

- shutdown zero is a process-level requirement for both the supervisor command
  owner and the final `/cmd_vel` owner;
- their executable entrypoints must keep the rclpy context valid through final
  zero publication and perform node, executor, and context cleanup in a
  deterministic order;
- focused tests must verify cleanup order, and a controlled SIGINT integration
  check must show final zero publication and clean process exit without an
  invalid-context `RCLError`;
- this correction was implemented and live-validated in Phase 04 commit
  `63744b0` after the saved Phase 04 plan was explicitly amended.

Historical Phase 02 test counts and its no-Gazebo-motion boundary remain
unchanged. A no-hardware process-level signal test is sufficient for this
contract; the later Phase 04 Gazebo smoke supplies end-to-end confirmation.

## Objective and scope

Implement an opt-in `robust_gaussian_v1` supervisor that owns the eight required logical states, cost-term weights, goal verification, fill-request sequencing, timeouts, and failsafe authorization. Preserve the current pipeline as the default `legacy` profile.

Phase 02 will:

- make `SEARCH`, `VERIFY_EXTREMUM`, `DESIGN_OR_MERGE_FILL`, `ESCAPE_REPULSE`, `ESCAPE_ASSIST`, `RECENTER`, `GOAL_HOLD`, and `FAILSAFE` explicit and observable;
- switch raw, Gaussian, and affine cost weights independently;
- compute a simulation source score without using source ground-truth positions;
- route fill creation through the existing Gaussian implementation;
- keep the existing controller as the sole `/cmd_vel` publisher while making it enforce supervisor authorization;
- publish zero commands on invalid/stale data, exceptions, state timeouts, explicit stop, shutdown, or loss of supervisor state.

This phase will not implement adaptive fill design/merging, measured radial progress, stall detection, assisted-direction selection, boundary handling, or recenter motion. Those remain Phases 03 and 04. Their transition inputs will exist in the pure state-machine interface, but the Phase 02 ROS supervisor will not synthesize them from timers or guessed geometry.

No Gazebo motion run or physical-hardware command is permitted.

The required preflight passed:

```text
Phase 02 plan context is complete.
```

## Repository findings and ownership

- No existing node owns state coordination, command authorization, timeouts, or a unified failsafe. A new `supervisor_node` is therefore justified inside the existing `ros_esc` package.
- Existing responsibilities will be retained:

  - `cost_function` remains the simulation source/cost adapter.
  - `modified_cost_2d` remains the sole evaluator of Gaussian and affine terms and the robust final `/cost_modified` owner.
  - `convergence_detector` remains the convergence-metric owner.
  - `gaussian_fill` remains the fill-design ROS owner and continues publishing legacy `/cost_bias`.
  - `custom_filter` remains the GESC estimator.
  - `Directional_Controller` and `custom_controller` remain the controller, saturation, diagnostic, and sole final-command publishers.

- Phase 01 already supplied the required `AlgorithmState`, `AlgorithmEvent`, `CostBreakdown`, `GaussianFill`, and `ControlDiagnostics` message fields. No new message definition or package is needed.
- Current implicit behavior to migrate only in the robust profile:

  - convergence is converted to a fill trigger inside `convergence_detector` after three threshold crossings;
  - `gaussian_fill` subscribes directly to `/convergence_event`;
  - every accepted fill immediately creates both Gaussian and affine terms;
  - raw, Gaussian, and affine terms are always active;
  - no owner can stop `/cmd_vel` because of algorithm state or stale data.

- The active GESC wrapper contains a pre-existing user modification and will not be edited.
- The current branch is `feature/gesc-gaussian-robustness-v1` at Phase 01 commit `2ba43f3`. The only tracked working-tree modification is the user-owned wrapper.

## State-machine design

### State owner and clock

`ros_esc/ros_esc/supervisor_node/state_machine.py` will contain a ROS-independent deterministic state machine. `supervisor_node_script.py` will be the sole robust-profile ROS owner of `/gesc_gaussian/algorithm_state`.

All durations will use the node’s ROS clock:

- Gazebo launch sets `use_sim_time=true`, so paused simulation pauses state timers.
- A future physical launch can use ROS system time without changing the state machine.
- The pure state machine receives `now_sec` explicitly for deterministic tests.
- Message freshness is based on local ROS receipt time, not the repository’s mixed legacy float timestamps.
- A backward clock jump or negative elapsed duration enters `FAILSAFE`.

The supervisor publishes state and a supervisory command at 20 Hz and immediately after every transition.

### State policy

| State | Weights `(sensor, Gaussian, affine)` | Command arbitration | Transitions |
|---|---:|---|---|
| `SEARCH` | `(1, 1, 0)` | GESC command allowed; supervisor contribution zero | Continuous convergence condition for 2 s → `VERIFY_EXTREMUM` |
| `VERIFY_EXTREMUM` | `(1, 1, 0)` | Final command zero while sensing continues | Score ≥ 0.95 for 3 s → `GOAL_HOLD`; score < 0.95 for 3 s → `DESIGN_OR_MERGE_FILL`; invalid/stale data or 10 s indecision → `FAILSAFE` |
| `DESIGN_OR_MERGE_FILL` | `(0, 1, 0)` | Final command zero | Matching fill success → `ESCAPE_REPULSE`, or `ESCAPE_ASSIST` when returning from the single redesign path; rejection/5 s timeout → `FAILSAFE` |
| `ESCAPE_REPULSE` | `(0, 1, 0)` | Weighted-cost GESC allowed | Abstract stable-exit input → `RECENTER` or `SEARCH`; first stall input → redesign; total escape timeout → `FAILSAFE` |
| `ESCAPE_ASSIST` | `(0, 1, 1)` | Weighted-cost GESC allowed | Abstract stable-exit input → `RECENTER` or `SEARCH`; invalid data or total escape timeout → `FAILSAFE` |
| `RECENTER` | `(0, 1, 0)` | GESC suppressed; supervisor-command interface selected, but Phase 02 publishes zero | Abstract recenter-complete input → `SEARCH`; invalid data/30 s timeout → `FAILSAFE` |
| `GOAL_HOLD` | `(0, 1, 0)` | Final command zero | Latched until shutdown; safety failure or explicit stop → `FAILSAFE` |
| `FAILSAFE` | `(0, 0, 0)` | Final command zero | Latched; no automatic restart |

The raw source pipeline and source-score publication continue in every state, including states whose raw-cost weight is zero.

### Transition details

- `SEARCH` consumes a continuous convergence-status stream rather than interpreting the current three-crossing counter as a dwell timer. A false or stale convergence condition resets the 2-second hold.
- `VERIFY_EXTREMUM` uses symmetric dwell:

  - three uninterrupted seconds at or above the threshold accepts the goal;
  - three uninterrupted seconds below the threshold classifies an undesired minimum;
  - crossing the threshold resets the opposite dwell;
  - ten seconds without either result fails safely.

- On entry to `DESIGN_OR_MERGE_FILL`, the supervisor publishes exactly one request containing the latest convergence snapshot. It accepts only a fill success/rejection whose `source_timestamp` matches that request; late responses are ignored.
- A future Phase 04 stall input causes one redesign attempt: `ESCAPE_REPULSE → DESIGN_OR_MERGE_FILL → ESCAPE_ASSIST`. A second escalation is not allowed.
- `escape_max_sec=20` is one deadline beginning with the first entry into `ESCAPE_REPULSE`; redesign does not reset it.
- `recenter_after_escape=true` selects `RECENTER` after a future stable-exit signal. When false, the transition goes directly to `SEARCH`.
- Phase 02 will not create a fixed-time “successful escape.” Until Phase 04 supplies measured exit/progress inputs, an actual robust run that reaches escape will remain safe and eventually enter `FAILSAFE` at the escape timeout. Phase 02 is therefore not an end-to-end simulation-ready release.

### Global fault inputs

Any nonterminal state enters `FAILSAFE` on:

- stale pose;
- stale source/cost sample;
- nonfinite pose, quaternion, raw cost, source score, weight, fill, or command;
- source-array length inconsistent with `channel_count`;
- invalid source score during verification;
- explicit `True` on the stop topic;
- controller-reported `EVENT_FAILSAFE`;
- state-specific timeout;
- backward ROS-clock movement;
- an exception caught by the supervisor.

`FAILSAFE` and `GOAL_HOLD` never restart automatically.

## Source-score verification

The current simulator exposes raw minimization cost but no calibrated score. Phase 02 will extend the existing simulation cost classes rather than use source ground truth.

For compatible photoresistor models:

\[
s = \operatorname{clip}
\left(
\frac{J_{\mathrm{raw}}-J_{\mathrm{dark}}}
     {J_{\mathrm{near}}-J_{\mathrm{dark}}},
0,1
\right)
\]

- The score is computed from the post-noise raw-cost sample.
- Endpoints are derived from the existing model’s audited resistance limits, not light positions:

  - dark resistance: `337260 Ω`;
  - near-source resistance: `100 Ω`;
  - current voltage-mode endpoints:
    `J_dark=-0.004887585532746823`,
    `J_near=-3.8372093023255816`.

- The same formula handles resistance mode because the endpoint ordering is retained.
- The current multi-light intensity normalization remains relative and is not described as lux calibration.
- `source_score=1` means the simulated photoresistor model reached its near-source range, not that a global optimum was obtained from source ground truth.
- Unsupported generic/symbolic cost objects publish `NaN` with `source_score_valid=false`; `robust_gaussian_v1` refuses goal verification and fails safely.
- With multiple channels, the supervisor uses the maximum finite channel score for the “at least one sensor sees a near-source condition” rule. The current audited rotating-sensor configuration has one channel.
- Phase 09 may replace the adapter’s endpoint provider with physical calibration while retaining the same score range, topic, message field, and supervisor logic.

The source adapter publishes a robust source sample as `CostBreakdown` on `/gesc_gaussian/source_cost`. This keeps raw cost and score synchronized in one message. `modified_cost_2d` consumes that message in the robust profile and propagates the score into the canonical final `/gesc_gaussian/cost_breakdown`.

## Cost weights and command pipeline

### Modified-cost behavior

In `legacy`, `modified_cost_2d` retains the current calculation exactly:

```text
raw + Gaussian + enabled affine
```

In `robust_gaussian_v1`, it subscribes to `AlgorithmState` and calculates:

```text
augmented =
    sensor_weight   * raw_cost
  + gaussian_weight * Gaussian contribution
  + affine_weight   * affine contribution
```

Each unweighted component is evaluated once and remains observable even when its weight is zero. Stateful affine-term expiry must not be evaluated a second time for diagnostics.

Existing fills remain persistent. The existing fill callback may still create an affine term immediately, but the robust state weights keep it inactive until `ESCAPE_ASSIST`.

### Command ownership and arbitration

`custom_controller` remains the only publisher of:

- `/cmd_vel`;
- `/turtlebot3/control_value_chatter`;
- `/gesc_gaussian/control_diagnostics`.

The supervisor owns state and command authorization. It publishes a `geometry_msgs/msg/Twist` contribution on `/gesc_gaussian/supervisor_command`.

Robust arbitration is:

- `SEARCH`, `ESCAPE_REPULSE`, `ESCAPE_ASSIST`: combine unsaturated GESC command with the supervisor contribution, then saturate once;
- `RECENTER`: suppress GESC and use only the supervisor contribution;
- `VERIFY_EXTREMUM`, `DESIGN_OR_MERGE_FILL`, `GOAL_HOLD`, `FAILSAFE`, invalid state, or stale supervisor data: force the combined and final commands to zero.

Phase 02’s supervisor contribution is always zero. The topic is created now so Phase 04 can add recenter/assist motion without changing final-command ownership.

`Directional_Controller` will expose one reusable saturation method. Its existing `controller_output()` will call that method, preserving the exact legacy result.

For robust diagnostics:

- `gesc_command_unsaturated` records the core GESC result;
- `supervisor_contribution` records the received contribution, or the cancelling contribution when state gating forces zero;
- `combined_command_unsaturated` records the actual pre-saturation arbitration result;
- `final_command` matches both legacy controller chatter and `/cmd_vel`;
- saturation flags describe the combined command.

### Independent zero-command protection

The controller will maintain its own robust watchdog:

- missing/invalid supervisor state;
- state older than 0.5 s;
- supervisor command older than 0.5 s;
- stale pose or filter input;
- nonfinite data;
- controller exception.

Any condition publishes a zero `Twist` immediately and keeps publishing zero at the watchdog rate until valid authorization returns or the supervisor’s failsafe latches.

The controller publishes zero:

- immediately when a disallowed/failsafe state arrives;
- on watchdog failure;
- from caught callback exceptions;
- once during orderly `destroy_node()` before destroying publishers.

Controller-local faults also emit `AlgorithmEvent.EVENT_FAILSAFE`; the supervisor consumes that event and latches the global state.

## Fill interface and convergence-timing migration

### Robust convergence status

`convergence_detector` will add `/gesc_gaussian/convergence_status` using the existing `StampedFloat64MultiArray` type and this eight-value layout:

```text
[metric, r, decay,
 mean_recent_x, mean_recent_y,
 mean_old_x, mean_old_y,
 count_remaining]
```

It is published on every valid post-startup metric evaluation. Existing `/convergence_metric`, `/convergence_r`, `/convergence_count`, `/convergence_event`, counter resets, and threshold-crossing behavior remain unchanged for legacy consumers.

### Fill request/result contract

`gaussian_fill` gains a parameterized trigger topic:

- legacy default: `/convergence_event`;
- robust: `/gesc_gaussian/fill_requests`.

The request retains the existing `StampedFloat64MultiArray` eight-value convergence-event layout, so the current fit and event-mean center logic are reused unchanged.

Results are:

- success: existing `/gesc_gaussian/gaussian_fills` `GaussianFill`, followed by unchanged `/cost_bias`;
- failure: existing `AlgorithmEvent.EVENT_FILL_REJECTED`;
- correlation: request/result `source_timestamp` equality, with only one request in flight.

Phase 03 may replace the fill estimator and registry internals while retaining this supervisor request/result boundary. No covariance estimation, merge rule, support radius, exit radius, or adaptive escalation is added here.

## Public interfaces

### New topics

| Topic | Type | Owner | Purpose |
|---|---|---|---|
| `/gesc_gaussian/source_cost` | `ros_esc_interfaces/msg/CostBreakdown` | `cost_function` | Synchronized raw cost and simulation source score for robust composition |
| `/gesc_gaussian/convergence_status` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | `convergence_detector` | Continuous convergence condition and current means |
| `/gesc_gaussian/fill_requests` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | supervisor | Single-flight request to the existing fill owner |
| `/gesc_gaussian/supervisor_command` | `geometry_msgs/msg/Twist` | supervisor | Phase 02 zero contribution and Phase 04 extension point |
| `/gesc_gaussian/stop_requested` | `std_msgs/msg/Bool` | external experiment operator/runner | `True` latches `FAILSAFE`; `False` is ignored |

### Existing interfaces with new robust semantics

- `/gesc_gaussian/algorithm_state`: the supervisor becomes the sole publisher in the robust profile. Legacy cost owners retain Phase 01 placeholder publication.
- `/gesc_gaussian/algorithm_events`: the supervisor adds state-transition, goal, timeout, stop, and failsafe events.
- `/gesc_gaussian/cost_breakdown`: source score and state-driven weights become valid in robust mode.
- `/gesc_gaussian/control_diagnostics`: supervisor contribution and combined-command fields become valid in robust mode.
- `/gesc_gaussian/gaussian_fills`, `/cost_bias`, `/cost_modified`, filter topics, controller chatter, `/cmd_vel`, `/odom`, and all positional layouts remain unchanged.

Add `AlgorithmEvent.EVENT_STATE_TRANSITION=3` to `AlgorithmEvent.msg`. This is additive; no existing constant or field changes.

No new ROS package, service, message file, or dependency is required. `geometry_msgs`, `std_msgs`, `nav_msgs`, and `ros_esc_interfaces` are already declared dependencies.

## Parameters and defaults

Use the repository’s current launch-argument plus ROS-parameter style. Do not add an unrelated YAML configuration hierarchy.

| Parameter/launch argument | Default |
|---|---:|
| `algorithm_profile` | `legacy` |
| `supervisor_publish_rate_hz` | `20.0` |
| `startup_timeout_sec` | `5.0` |
| `convergence_hold_sec` | `2.0` |
| `goal_score_threshold` | `0.95` |
| `goal_hold_sec` | `3.0` |
| `undesired_score_hold_sec` | `3.0` |
| `verification_max_sec` | `10.0` |
| `fill_design_timeout_sec` | `5.0` |
| `escape_max_sec` | `20.0` |
| `recenter_after_escape` | `True` |
| `recenter_max_sec` | `30.0` |
| `stale_pose_sec` | `0.50` |
| `stale_sensor_sec` | `0.50` |
| `supervisor_state_stale_sec` | `0.50` |
| `supervisor_command_stale_sec` | `0.50` |
| `command_watchdog_rate_hz` | `20.0` |
| `zero_command_on_shutdown` | `True` |
| `source_cost_topic` | `/gesc_gaussian/source_cost` |
| `convergence_status_topic` | `/gesc_gaussian/convergence_status` |
| `fill_request_topic` | `/gesc_gaussian/fill_requests` |
| `supervisor_command_topic` | `/gesc_gaussian/supervisor_command` |
| `supervisor_stop_topic` | `/gesc_gaussian/stop_requested` |

The central launch validates profile names. `robust_gaussian_v1` requires PDE/Gaussian nodes and `Directional_Controller`; an incompatible graph must fail safely rather than silently falling back to legacy.

Robust mode makes Phase 01 observability mandatory even when the existing `enable_observability` argument is false. Legacy retains `enable_observability=False` as its default.

Phase 04 parameters such as stall window, radial progress, exit hold, bounds, wall margin, and recenter tolerance are intentionally not added as unused Phase 02 settings.

## Exact files proposed for modification

- `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmEvent.msg`
  - Add the state-transition event constant only.

- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/cost_function_objects.py`
  - Add an optional source-score method with an unavailable default.
  - Implement model-range normalization in the existing photoresistor classes.

- `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py`
  - Publish robust synchronized source `CostBreakdown`.
  - Keep legacy raw-cost publication unchanged and publish source metadata/calibration diagnostics.

- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`
  - Add robust source/state subscriptions and state-driven composition.
  - Propagate source score and stop publishing placeholder algorithm state when the supervisor owns it.
  - Preserve the exact legacy callback and arithmetic.

- `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py`
  - Publish continuous convergence status without changing legacy crossing/counter/event behavior.

- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`
  - Parameterize the request topic and force typed results in robust mode.
  - Keep fitting, cooldown, duplicate checks, IDs, and `/cost_bias` unchanged.

- `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_node_script.py`
  - Accept `algorithm_profile` so robust mode enables the existing typed diagnostics without changing filtering.

- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`
  - Subscribe to supervisor state/contribution, arbitrate robust commands, add watchdog/zero-command handling, and report local faults.

- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py`
  - Extract reusable saturation from `Directional_Controller` while retaining legacy numerical results.

- `ros2_ws/src/ros_esc/setup.py`
  - Register the `supervisor_node` console entry point.

- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
  - Add profile, supervisor, timeout, topic, and watchdog arguments.
  - Launch the supervisor only for `robust_gaussian_v1`.
  - Route legacy and robust fill/source/state ownership without duplicate publishers.

- `ros2_ws/src/ros_esc/test/test_observability_contract.py`
  - Extend public-interface, score-validity, topic-default, event-constant, and publisher-ownership tests.

- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`
  - Extend numerical equivalence coverage across weighted-cost, saturation, fill-trigger, controller, and launch profiles.

- `docs/codex/gesc_gaussian/topic_dictionary.md`
  - Document new topics, state ownership, weights, score definition, timers, command arbitration, and legacy mapping.

- `docs/codex/gesc_gaussian/test_commands.md`
  - Add Phase 02 focused and package-level commands/results.

## Exact files proposed for creation

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/__init__.py`
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py`
  - Pure enums, profile defaults, transition inputs/results, timers, weight table, escalation context, and latch behavior.

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py`
  - ROS subscriptions/publications, validation, freshness checks, request correlation, state/event publication, and zero supervisor contribution.

- `ros2_ws/src/ros_esc/test/test_state_machine.py`
  - Deterministic unit coverage for every transition, timer, weight set, clock regression, and latch.

- `ros2_ws/src/ros_esc/test/test_supervisor_integration.py`
  - Non-Gazebo ROS integration test using fake source, convergence, pose, fill-result, stop, and command subscribers.

- `docs/codex/gesc_gaussian/handoffs/phase_02_handoff.md`
  - Created only during implementation with exact repository state, changes, tests, limitations, and next-phase contract.

No profile YAML is created because the audited algorithm nodes use XML launch arguments and inline ROS parameters; adding a separate configuration convention would be inconsistent.

## Backward compatibility and migration effects

- `algorithm_profile=legacy` remains the default.
- The existing wrapper is unchanged and therefore continues its current PDE/Gaussian behavior.
- Legacy convergence events continue to trigger the existing fill node directly.
- Legacy fixed weights remain `(1,1,enable_affine_bias)`.
- Legacy controller output, saturation, timestamps, topic names, queue depths, and array layouts must remain numerically identical.
- Legacy `enable_observability=False` behavior remains unchanged.
- Robust typed interfaces are mandatory because they are control inputs, not optional logging.
- Existing consumers need no migration. Robust consumers rebuild the two changed packages and use the new `/gesc_gaussian/*` topics.
- The Phase 01 algorithm-state placeholder remains available in legacy mode; only robust mode transfers sole ownership to the supervisor.
- Physical calibration, hardware launch, and hardware command handling remain outside Phase 02.
- Heavy-Ball files, profiles, controllers, wrappers, and tests are untouched.

## Implementation sequence

1. Add the transition event constant and pure state machine.
2. Add complete state-transition/weight/timer unit tests before ROS wiring.
3. Add simulation photoresistor score normalization and synchronized source-cost publication.
4. Add continuous convergence status and parameterized fill requests while preserving legacy trigger behavior.
5. Add robust weighted composition to `modified_cost_2d` with exact legacy-equivalence tests.
6. Implement the supervisor ROS node, request correlation, state/events, freshness validation, and zero contribution.
7. Refactor reusable directional-controller saturation and add robust arbitration/watchdogs.
8. Wire profile selection and topics through `gazebo.launch.xml`, ensuring one state owner and one `/cmd_vel` owner.
9. Add the ROS integration test and expand Phase 01 contract/regression tests.
10. Update the topic dictionary and test-command record.
11. Run focused tests, package build/tests, launch parsing, and repository checks.
12. Write the Phase 02 handoff with the explicit Phase 03/04 extension boundaries.

## Tests and acceptance criteria

### State-machine unit tests

Cover:

- initial/bootstrap `SEARCH`;
- convergence dwell, reset, and exact threshold boundary;
- high-score goal dwell;
- low-score undesired-minimum dwell;
- noisy threshold alternation and verification timeout;
- fill success, rejection, late result, duplicate result, and design timeout;
- normal escape success for bounded and unbounded modes via injected Phase 04 inputs;
- single redesign path into `ESCAPE_ASSIST`;
- escape total timeout across redesign;
- assisted-exit and assisted-timeout paths;
- recenter completion and timeout;
- invalid/stale pose and sensor in every active state;
- explicit stop and controller fault;
- backward clock movement;
- `GOAL_HOLD` and `FAILSAFE` latching;
- weights for every state;
- active-fill count/ID and previous-state/transition-reason reporting.

### Source, cost, and legacy tests

Cover:

- photoresistor resistance- and voltage-mode endpoint normalization;
- score clipping, noise-path use, and unsupported-model invalidity;
- no dependence on configured light positions;
- robust propagation from source `CostBreakdown` to final breakdown;
- exact weighted recombination in every state;
- raw/source publication while sensor weight is zero;
- one evaluation of stateful affine pruning per sample;
- exact legacy `/cost_modified` output and timestamp;
- unchanged `/cost_bias` layout and current fill fit;
- legacy convergence counter and direct trigger behavior;
- robust fill request single-flight behavior;
- exact legacy `Directional_Controller` saturation.

### Controller/failsafe tests

Cover:

- GESC-only, supervisor-only, combined, and zero-gated command paths;
- `RECENTER` suppressing GESC;
- final saturation after combination;
- diagnostics matching actual chatter and Twist;
- zero command on each disallowed state;
- stale state, stale supervisor command, stale pose, nonfinite input, explicit stop, exception, and shutdown;
- controlled SIGINT preserving a valid context through supervisor and
  controller shutdown-zero publication, followed by clean teardown;
- controller fault event causing supervisor `FAILSAFE`;
- one and only one `/cmd_vel` publisher in both profiles.

### ROS integration test

Using shortened test dwell parameters and no Gazebo/hardware:

1. publish valid odometry, source cost/score, and convergence status;
2. observe `SEARCH → VERIFY_EXTREMUM`;
3. hold a sub-threshold score and observe `DESIGN_OR_MERGE_FILL`;
4. verify exactly one fill request with the cached convergence payload;
5. publish a matching `GaussianFill` and observe `ESCAPE_REPULSE`;
6. publish stop and observe latched `FAILSAFE`, zero supervisor command, and valid transition events.

### Commands

From `/home/mattb/dsim-lab`:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 02 implement
```

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
```

```bash
python3 -m pytest -q \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
```

```bash
ros2 interface show ros_esc_interfaces/msg/AlgorithmState
ros2 interface show ros_esc_interfaces/msg/AlgorithmEvent
ros2 interface show ros_esc_interfaces/msg/CostBreakdown
ros2 interface show ros_esc_interfaces/msg/ControlDiagnostics
```

```bash
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
  algorithm_profile:=robust_gaussian_v1 \
  use_pde_extensions:=True \
  --show-args
```

```bash
colcon test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose
```

```bash
cd ..
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_required_docs.sh
git diff --check
git status --short --branch
```

Acceptance requires all focused tests to pass, launch XML to parse, no duplicate state/final-command owner, a controlled no-hardware SIGINT check proving final zero before context invalidation, and no new package-test failure beyond the documented Phase 01 baseline of 875 pre-existing lint failures. No Gazebo motion test is required in this phase.

## Stop conditions and risks

Stop implementation and report exact evidence if:

- the Phase 02 implementation validator or saved-plan validator fails;
- required files no longer match the Phase 01 handoff;
- source-score normalization would require source ground-truth position or an invented physical calibration;
- the audited photoresistor models cannot expose a deterministic score without changing raw cost;
- robust launch selection creates duplicate `/gesc_gaussian/algorithm_state`, `/gesc_gaussian/cost_breakdown`, or `/cmd_vel` publishers;
- weighted composition changes legacy output, timestamps, channel layout, or affine evaluation order;
- controller arbitration changes legacy saturation;
- fill requests cannot be correlated without changing `/cost_bias`;
- safe zero publication cannot be demonstrated for stale supervisor state and shutdown;
- a physical or Heavy-Ball change is required;
- required files overlap new unrelated user modifications;
- focused tests cannot run or pass.

Principal risks are:

- accidental duplicate state ownership during profile selection;
- treating the simulation score as absolute photometric calibration;
- stale-data false positives from mixed legacy timestamp bases;
- double evaluation of the stateful affine term;
- unsafe command gaps when callbacks stop;
- late fill responses changing the wrong state;
- mistakenly claiming Phase 02 escape/recenter completion before Phases 03–04.

## Implementation-time verification assumptions

- Verify XML string-profile conditions with `ros2 launch ... --show-args`; if the frontend cannot express them reliably, use mutually exclusive executable declarations rather than allowing duplicate owners.
- Verify the optional source-score method does not break the repository’s cost-object documentation parser.
- Verify the active robust path still selects `Directional_Controller`; other controller classes must fail safely until explicitly supported.
- Verify photoresistor score endpoints against the live class calculations before freezing tests.
- Verify DDS delivery does not affect fill correlation; correlation is by source timestamp, not arrival order.
- Verify robust observability is enabled independently of the legacy `enable_observability` default.
- Treat the current one-channel sensor mapping as confirmed; retain channel-safe array validation.
- Treat `RECENTER`, stable-exit, and stall inputs as Phase 04 stubs. Do not add timer-based success or guessed geometry.
- Preserve the user-owned wrapper modification and all unrelated untracked documentation.
