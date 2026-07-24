# Phase 03 Plan — Robust Basin Estimation and Gaussian Fill Redesign

## Post-implementation Amendment 1 — ROS parameter typing (2026-07-21)

The first Phase 04 visible Gazebo smoke exposed a Phase 03 launch-contract
defect that `--show-args` did not detect. XML defaults `10` and `80` were
inferred as integers, while `GaussianFill` declares
`center_cost_percentile` and `shoulder_cost_percentile` as doubles. The node
therefore rejected the robust launch before startup.

This amendment changes only the serialized type of those two defaults:

- use `10.0` and `80.0` in launch XML, canonical YAML defaults, parameter
  tables, and tests;
- retain the numerical percentile values, units, estimator formulas, and
  legacy behavior exactly;
- require at least one runtime node/launch instantiation check for declared
  parameter types; launch parsing alone is not sufficient evidence.

The runtime correction and regression test were implemented in Phase 04 commit
`63744b0`. No other Phase 03 parameter has a discovered type mismatch.

## Objective and scope

Implement the `robust_gaussian_v1` basin estimator, adaptive anisotropic fill designer, and revision-aware fill registry inside the existing `gaussian_fill` owner. Extend `modified_cost_2d` and the Phase 02 supervisor to consume the authoritative typed fill lifecycle without changing legacy behavior.

Phase 03 includes:

- timestamp-synchronized pose/raw-cost buffering;
- invalid, stale, jump, and MAD outlier rejection;
- kernel/cost-weighted center refinement;
- weighted covariance and regularized quadratic fitting;
- depth/curvature amplitude and width selection;
- local-grid residual-minimum detection and bounded escalation;
- soft association plus a mandatory overlap gate;
- cluster revisions, supersession, and atomic registry updates;
- confidence and structured diagnostics.

Phase 03 does not implement escape-progress measurement, assisted direction, recentering, physical adapters, rosbag recording, scenario automation, or Heavy-Ball ESC.

The required planning gate passed:

```text
Phase 03 plan context is complete.
```

This planning turn is read-only. Before implementation, save this document verbatim as:

```text
docs/codex/gesc_gaussian/plans/phase_03_plan.md
```

Then require `validate_phase_context.sh 03 implement` to pass.

## Repository findings and reuse

- Repository: `/home/mattb/dsim-lab`
- Branch: `feature/gesc-gaussian-robustness-v1`
- Planning HEAD: `8cf93f5`
- The Phase 02 handoff exists and preserves the correlated `/gesc_gaussian/fill_requests` → `GaussianFill`/rejection boundary specifically for Phase 03.
- Current focused baseline passes: `44 passed`.
- The pre-existing user modification to `ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash` remains out of scope.

Existing behavior to reuse rather than duplicate:

- `gaussian_fill_script.py` already owns fill requests, legacy convergence triggers, isotropic least-squares fitting, event-mean anchoring, fit-center bounds, cooldown, fill limits, typed fill publication, and `/cost_bias`.
- `modified_cost_script.py` already owns Gaussian/affine evaluation, retained terms, state weights, `/cost_modified`, and cost diagnostics.
- The supervisor already correlates fill results by exact request `source_timestamp`.
- `GaussianFill.msg` already contains covariance, principal widths, support/exit radii, confidence, revision, cluster, activity, and supersession fields.
- `/gesc_gaussian/source_cost` already provides stamped raw cost and optional source score.
- `/odom` is the audited simulation pose source.
- `/pde_history` remains needed by convergence detection and affine-direction estimation. `/pde_cost_history` and the old independently updated histories remain available for the legacy Gaussian fit but will not be used by the robust estimator.

The current robust path is still incomplete:

- Pose and cost histories are independently updated and unsynchronized.
- The fit is isotropic and uses configured amplitude.
- `modified_cost_2d` stores append-only four-tuples, so it cannot replace a revision or evaluate anisotropic covariance.
- The supervisor increments active-fill count for every successful result, including a future revision.
- `/cost_bias` cannot represent covariance or supersession.

## Implementation design and public interfaces

### Robust sample buffer

In `robust_gaussian_v1`, `gaussian_fill` will subscribe to the existing:

- `/odom` (`nav_msgs/msg/Odometry`);
- `/gesc_gaussian/source_cost` (`CostBreakdown`);
- `/gesc_gaussian/algorithm_state` (`AlgorithmState`);
- `/gesc_gaussian/fill_requests` (`StampedFloat64MultiArray`).

Pose and cost snapshots will be kept in time-ordered deques and paired one-to-one by the closest absolute ROS stamp within `sample_sync_tolerance_sec`. The cost stamp becomes the synchronized sample stamp. The most recent valid algorithm state is copied into the sample.

Each internal `BasinSample` contains:

```text
stamp_sec
x
y
yaw
raw_sensor_value
raw_sensor_valid
raw_cost
source_score
source_score_valid
algorithm_state
```

The current simulator has no separate raw sensor value. Its invalid `raw_sensor_value` remains `NaN`; robust estimation requires valid raw cost and does not invent a sensor value.

At each fill request, freeze samples satisfying both:

```text
request_ros_time - estimation_window_sec <= sample_time <= request_ros_time
sample_age <= maximum_sample_age_sec
```

Use the node’s absolute ROS clock for this window, not the legacy float request timestamp. Preserve the request timestamp solely for supervisor result correlation.

Reject:

- invalid/nonfinite pose, quaternion/yaw, selected raw-cost channel, or stamp;
- missing/invalid controller mode;
- timestamp regression or duplicate timestamps;
- unmatched pose/cost samples;
- samples older than the configured window/age;
- motion exceeding `maximum_position_speed_mps`;
- cost or position-increment MAD outliers.

MAD uses the modified score `0.67448975 * abs(value - median) / MAD`. If MAD is effectively zero, skip that MAD dimension instead of rejecting all subsequent nonzero motion. Require `minimum_valid_samples` after all rejection.

### Basin estimator

Use raw minimization cost for the model and preserve its sign and units.

1. Normalize cost only for center weighting:

   ```text
   span = max(percentile90(raw_cost) - minimum(raw_cost), 1e-12)
   normalized_cost = clip((raw_cost - minimum(raw_cost)) / span, 0, 1)
   ```

2. Initialize the center at the valid sample with minimum raw cost.

3. Apply up to five log-sum-exp-normalized mean-shift iterations:

   ```text
   log_weight =
       -distance_squared / (2 * position_kernel_bandwidth_m²)
       -normalized_cost / cost_temperature_normalized
   ```

4. Stop at `center_tolerance_m`.

5. Compute weighted sample covariance, symmetrize it, eigen-decompose it, and clip eigenvalues to the configured range.

6. Fit:

   ```text
   J(delta) =
       c + gx*dx + gy*dy
       + 0.5*Hxx*dx² + Hxy*dx*dy + 0.5*Hyy*dy²
   ```

   using the final center weights. Ridge regularization applies to all coefficients except the intercept. Record weighted RMS residual, matrix rank, and the unregularized weighted-design condition number.

7. Symmetrize `H`. Clip negative Hessian eigenvalues to zero only for curvature/amplitude calculations; retain the finite fitted model for grid validation.

8. Treat curvature as invalid when rank is below six, condition exceeds the limit, or coefficients are nonfinite. Continue with depth-only amplitude. If no finite quadratic predictor can be obtained, use a constant center-cost predictor for validation, set fit confidence components to zero, and emit a low-confidence diagnostic.

9. Compute center cost as the weighted 10th percentile. Compute shoulder cost as the ordinary 80th percentile outside Mahalanobis radius 1.0. If no outside samples exist, use the overall 80th percentile and mark the fallback. Basin depth remains in raw-cost units:

   ```text
   depth = max(shoulder_cost - center_cost, minimum_basin_depth)
   ```

### Fill design and residual-minimum validation

Build the initial covariance:

```text
Sigma_fill = covariance_scale * Sigma_sample + sigma_floor_m² * I
```

Clip its principal standard deviations to `[sigma_floor_m, sigma_ceiling_m]`, reconstruct the covariance, and canonicalize orientation to `[-pi/2, pi/2)`. Use orientation zero for numerically isotropic covariance.

Compute:

```text
A_depth = amplitude_depth_scale * depth
A_curvature =
    amplitude_curvature_scale
    * maximum_positive_Hessian_eigenvalue
    * maximum_fill_covariance_eigenvalue
A = clip(max(amplitude_min, A_depth, A_curvature),
         amplitude_min, amplitude_max)
```

Publish:

```text
support_radius = support_sigma * sigma_major
exit_radius = exit_sigma * sigma_major
```

Validate the fitted augmented model on a `41 x 41` grid spanning ±3 principal standard deviations. A residual minimum is a non-boundary point within Mahalanobis radius `exit_sigma` whose value is no greater than all eight neighbors and is lower than at least one neighbor by `grid_minimum_tolerance`.

Escalate for at most five rounds:

1. Multiply amplitude by 1.5, cap it, and revalidate.
2. If minima remain and either width can grow, multiply both standard deviations by 1.25 with ceiling clipping, multiply amplitude by `1.25²` with cap clipping, and revalidate.
3. Stop immediately when no residual minimum remains.

`design_escalations` is the number of escalation rounds. Events additionally report amplitude-step and width-step counts.

If validation still fails:

- emit `EVENT_FILL_DESIGN_FAILED`;
- publish no active `GaussianFill` and no `/cost_bias`;
- leave any existing cluster revision active;
- let the supervisor treat the event as the correlated rejected result and enter its existing controlled failsafe path.

### Association, registry, and supersession

Association happens after the candidate estimate and initial width calculation but before committing a fill.

For every active cluster:

```text
log_score_j = -distance(candidate, cluster_j)² / (2 * merge_bandwidth_m²)
```

Normalize across all active clusters with log-sum-exp. Select the highest probability, breaking exact ties by the lowest `cluster_id`. Merge only if both hold:

```text
probability >= minimum_merge_probability
distance <= merge_radius_scale
            * max(existing_sigma_major, candidate_sigma_major)
```

This prevents a single distant cluster from receiving probability one and forcing a merge.

For a merge:

- combine the cluster’s retained inlier samples with the new inlier window;
- de-duplicate equal stamps;
- retain at most `maximum_cluster_samples`, using deterministic evenly spaced indices over the time-sorted set;
- rerun center, covariance, quadratic, depth, fill design, and validation over the combined samples;
- commit only after the merged design passes.

Identity rules:

- `cluster_id` identifies one basin and never changes.
- `fill_id` identifies one concrete fill version and is globally monotonic.
- A new cluster starts at revision 1 with `fill_id == cluster_id`.
- A redesign receives a new `fill_id`, retains `cluster_id`, and increments revision.
- Publish the old version once more as `active=false, superseded=true`, preserving its original request timestamp.
- Publish the new version as `active=true, superseded=false`, carrying the current request timestamp.
- Emit merge and supersession events.
- Revisions do not consume another `max_fills` slot. In robust mode, existing `max_fills` limits active clusters; legacy retains its current accepted-fill-count meaning.
- A failed redesign does not mutate the registry.

`modified_cost_2d` will use the typed fill stream only in `robust_gaussian_v1`. It will:

- validate positive-semidefinite covariance and cache its inverse;
- key active Gaussian terms by `fill_id` and enforce one active version per cluster;
- remove superseded versions before adding the replacement;
- evaluate `A * exp(-0.5 * deltaᵀ Sigma⁻¹ delta)`;
- replace, rather than stack, the associated affine term on revision;
- use `sigma_major` for the existing PDE-history exclusion radius.

Legacy continues consuming `/cost_bias` and its current isotropic tuple list.

The supervisor will maintain an active typed registry and pass the number of unique active clusters into the pure state machine. Supersession records are lifecycle updates, not rejected design results. The new active revision remains the correlated result and becomes `active_escape_fill_id`.

### Confidence and diagnostics

Compute six scores in `[0,1]` and publish their arithmetic mean:

1. Sample count:
   `min(1, valid_samples / (2 * minimum_valid_samples))`.
2. Coverage:
   average of occupied fraction across eight angular bins and
   `min(1, sample_sigma_major / position_kernel_bandwidth_m)`.
3. Fit condition:
   `max(0, 1 - log10(max(condition,1)) / log10(condition_limit))`, or zero when invalid.
4. Fit residual:
   `max(0, 1 - RMS / max(P90-P10, minimum_basin_depth))`.
5. Cap use:
   `1 - mean(amplitude_at_cap, any_width_at_cap, escalation_limit_reached)`.
6. Residual validation: one on success, zero on failure/unavailable validation.

An accepted confidence below `low_confidence_threshold` remains usable but emits `EVENT_FILL_LOW_CONFIDENCE`.

`GaussianFill` fields become valid for robust fills:

- covariance and principal widths;
- support and exit radii;
- confidence;
- sample count;
- fit residual/condition when available;
- design escalation count;
- active/superseded lifecycle state.

Structured fill events report finite values for input/valid/rejected sample counts, rejection categories, center, covariance, basin depth, maximum curvature, fit validity/residual/condition, residual-minimum count, escalation steps, confidence components, association probability, cluster ID, revision, and superseded/new fill IDs.

### Public interface effects

No new node, package, message file, topic, or dependency is justified.

Add these constants to `AlgorithmEvent.msg`:

```text
EVENT_FILL_MERGED=22
EVENT_FILL_SUPERSEDED=23
EVENT_FILL_DESIGN_ESCALATED=24
EVENT_FILL_DESIGN_FAILED=25
EVENT_FILL_LOW_CONFIDENCE=26
```

No existing constant or message field changes.

Existing topic effects:

- `/gesc_gaussian/gaussian_fills` becomes the authoritative robust fill registry and modified-cost input.
- `/cost_bias` remains exactly `[A, center_x, center_y, sigma]`; robust mode publishes `sigma_major` as its conservative isotropic compatibility projection.
- `/cost_bias` cannot express covariance or supersession and is not authoritative in robust mode. Existing legacy consumers need no migration; robust registry consumers must use `/gesc_gaussian/gaussian_fills`.
- `/cost_modified`, cost weights, `/cmd_vel`, request correlation, and all other legacy layouts remain unchanged.
- The existing live cost-surface plotter remains a legacy `/cost_bias` consumer and may show a lossy append-only projection after robust revisions. Authoritative computation and later analysis must use the typed registry.

## Exact file changes

### Modify

- `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmEvent.msg`
  - Add the five Phase 03 event constants.

- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`
  - Split legacy and robust trigger paths.
  - Preserve the legacy fitting and publication path.
  - Add robust pose/cost/state subscriptions and synchronization callbacks.
  - Orchestrate estimator, designer, association, registry commit, lifecycle publications, compatibility output, and events.

- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`
  - Keep legacy `/cost_bias` behavior unchanged.
  - In robust mode subscribe to `GaussianFill`, maintain revision-aware anisotropic terms, replace cluster affine terms, and prevent double counting.

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py`
  - Accept an authoritative active-cluster count with a successful fill result instead of blindly incrementing for every revision.

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py`
  - Track typed lifecycle records, ignore supersession tombstones as design failures, correlate only the new active version, and publish accurate active-cluster count and escape fill ID.

- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`
  - Expose and pass robust estimator/designer/registry parameters.
  - Serialize double-valued percentile defaults as `10.0` and `80.0` so ROS
    launch does not infer integer overrides.
  - Pass the existing pose, source-cost, state, fill-diagnostics, and event topics to their existing owners.
  - Do not add a second launch graph.

- `ros2_ws/src/ros_esc/test/test_observability_contract.py`
  - Check event constants, robust fill validity/lifecycle semantics, and
    runtime-compatible parameter types.

- `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`
  - Prove the original isotropic fit, `/cost_bias`, legacy Gaussian sum, affine creation, and timestamps remain unchanged.
  - Add robust anisotropic evaluation and no-double-count regression cases.

- `ros2_ws/src/ros_esc/test/test_state_machine.py`
  - Cover cluster-count replacement on revisions.

- `ros2_ws/src/ros_esc/test/test_supervisor_integration.py`
  - Cover supersession followed by an active revision and verify one active cluster.

- `docs/codex/gesc_gaussian/topic_dictionary.md`
  - Document robust synchronization, fill identity/lifecycle, authoritative typed consumption, confidence, events, parameters, and `/cost_bias` limitations.

- `docs/codex/gesc_gaussian/test_commands.md`
  - Record Phase 03 commands and exact results.

### Create

- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/basin_estimator.py`
  - Pure dataclasses and deterministic synchronization, filtering, weighting, covariance, depth, quadratic, and confidence inputs.

- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_designer.py`
  - Pure covariance/amplitude design, Gaussian evaluation/gradient, grid validation, escalation, and confidence aggregation.

- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_registry.py`
  - Pure association, cluster/sample retention, IDs, revisions, supersession, and active-registry logic.

- `ros2_ws/src/ros_esc/test/test_robust_gaussian_algorithm.py`
  - ROS-independent deterministic numerical tests.

- `docs/codex/gesc_gaussian/handoffs/phase_03_handoff.md`
  - Implementation record with commits, tests, limitations, and Phase 04 boundary.

No `setup.py`, `package.xml`, CMake, new configuration hierarchy, Heavy-Ball file, physical file, data collector, PDE-history node, or user-owned wrapper change is required.

## Parameters and defaults

Each new node parameter is exposed by `gazebo.launch.xml` with the listed `gaussian_fill_...` launch argument. Existing `source_cost_topic`, `algorithm_state_topic`, `gaussian_fill_diagnostics_topic`, and `algorithm_event_topic` arguments are reused.

| Node parameter | Launch argument | Default |
|---|---|---:|
| `pose_topic` | `gaussian_fill_pose_topic` | `/odom` |
| `estimation_channel_index` | `gaussian_fill_estimation_channel_index` | `0` |
| `sample_sync_tolerance_sec` | `gaussian_fill_sample_sync_tolerance_sec` | `0.05` |
| `maximum_position_speed_mps` | `gaussian_fill_maximum_position_speed_mps` | `0.20` |
| `outlier_mad_threshold` | `gaussian_fill_outlier_mad_threshold` | `3.5` |
| `maximum_cluster_samples` | `gaussian_fill_maximum_cluster_samples` | `4000` |
| `estimation_window_sec` | `gaussian_fill_estimation_window_sec` | `8.0` |
| `minimum_valid_samples` | `gaussian_fill_minimum_valid_samples` | `40` |
| `maximum_sample_age_sec` | `gaussian_fill_maximum_sample_age_sec` | `12.0` |
| `mean_shift_iterations` | `gaussian_fill_mean_shift_iterations` | `5` |
| `center_tolerance_m` | `gaussian_fill_center_tolerance_m` | `0.005` |
| `position_kernel_bandwidth_m` | `gaussian_fill_position_kernel_bandwidth_m` | `0.25` |
| `cost_temperature_normalized` | `gaussian_fill_cost_temperature_normalized` | `0.05` |
| `covariance_eigenvalue_min_m2` | `gaussian_fill_covariance_eigenvalue_min_m2` | `0.0025` |
| `covariance_eigenvalue_max_m2` | `gaussian_fill_covariance_eigenvalue_max_m2` | `0.25` |
| `quadratic_ridge_lambda` | `gaussian_fill_quadratic_ridge_lambda` | `1e-6` |
| `quadratic_condition_number_max` | `gaussian_fill_quadratic_condition_number_max` | `1e8` |
| `center_cost_percentile` | `gaussian_fill_center_cost_percentile` | `10.0` |
| `shoulder_cost_percentile` | `gaussian_fill_shoulder_cost_percentile` | `80.0` |
| `inner_mahalanobis_radius` | `gaussian_fill_inner_mahalanobis_radius` | `1.0` |
| `minimum_basin_depth` | `gaussian_fill_minimum_basin_depth` | `0.02` |
| `covariance_scale` | `gaussian_fill_covariance_scale` | `2.5` |
| `sigma_floor_m` | `gaussian_fill_sigma_floor_m` | `0.15` |
| `sigma_ceiling_m` | `gaussian_fill_sigma_ceiling_m` | `1.25` |
| `amplitude_depth_scale` | `gaussian_fill_amplitude_depth_scale` | `1.5` |
| `amplitude_curvature_scale` | `gaussian_fill_amplitude_curvature_scale` | `1.2` |
| `amplitude_min` | `gaussian_fill_amplitude_min` | `0.10` |
| `amplitude_max` | `gaussian_fill_amplitude_max` | `3.00` |
| `validation_grid_points_per_axis` | `gaussian_fill_validation_grid_points_per_axis` | `41` |
| `validation_support_sigma` | `gaussian_fill_validation_support_sigma` | `3.0` |
| `maximum_design_escalations` | `gaussian_fill_maximum_design_escalations` | `5` |
| `amplitude_escalation_factor` | `gaussian_fill_amplitude_escalation_factor` | `1.5` |
| `width_escalation_factor` | `gaussian_fill_width_escalation_factor` | `1.25` |
| `grid_minimum_tolerance` | `gaussian_fill_grid_minimum_tolerance` | `1e-9` |
| `support_sigma` | `gaussian_fill_support_sigma` | `3.0` |
| `exit_sigma` | `gaussian_fill_exit_sigma` | `2.5` |
| `merge_bandwidth_m` | `gaussian_fill_merge_bandwidth_m` | `0.50` |
| `merge_radius_scale` | `gaussian_fill_merge_radius_scale` | `2.0` |
| `minimum_merge_probability` | `gaussian_fill_minimum_merge_probability` | `0.60` |
| `low_confidence_threshold` | `gaussian_fill_low_confidence_threshold` | `0.60` |

Legacy parameters remain accepted and retain their present meanings under `algorithm_profile=legacy`. In robust mode, `max_fills` limits active clusters, while legacy-only amplitude, sigma, center-source, and duplicate-distance settings do not override robust design.

## Implementation sequence

1. Save this plan and pass the Phase 03 implementation validator.
2. Add event constants and the three pure internal modules.
3. Implement deterministic estimator/designer/registry tests before ROS wiring.
4. Split `gaussian_fill_script.py` into unchanged legacy orchestration and new robust orchestration.
5. Add robust synchronized subscriptions, request-time freezing, validation diagnostics, and atomic registry publication.
6. Convert robust `modified_cost_2d` to typed anisotropic lifecycle consumption while retaining the legacy callback unchanged.
7. Correct supervisor lifecycle handling and active-cluster accounting.
8. Wire parameters through the existing Gazebo launch.
9. Extend contract, legacy, state-machine, and non-Gazebo integration tests.
10. Update the topic dictionary and test-command record.
11. Run focused tests, build, launch/interface checks, package tests, and repository checks.
12. Write the Phase 03 handoff. Do not proceed to Phase 04 if the focused numerical or legacy-equivalence gates fail.

## Deterministic tests and expected numerical outcomes

Use absolute tolerance `1e-9` unless a row specifies otherwise.

| Test | Fixture | Expected result |
|---|---|---|
| Synchronization | Pose stamps `1.00, 1.10`; cost stamps `1.03, 1.18`; tolerance `0.05` | Only `1.00 ↔ 1.03` pairs; synchronized stamp `1.03`; second pair is rejected as `0.08 > 0.05` |
| Stable weights | Equal spatial distance, normalized costs `[0.0, 0.05]`, temperature `0.05` | Weights `[0.7310585786, 0.2689414214]`; sum `1.0` |
| Underflow safety | Distances `[0, 1000] m`, bandwidth `0.25` | Finite weights, sum `1.0`, effectively `[1.0, 0.0]` |
| Outlier rejection | Symmetric samples about `(1,2)` plus a high-cost distant point | Distant sample rejected; final center `(1.0,2.0)` within `1e-6` |
| Covariance | Equal weights at `(±0.1,0)` and `(0,±0.2)` | Covariance `diag(0.005,0.020)`, zero cross-term, nonnegative eigenvalues |
| Covariance/width bounds | Clipped sample eigenvalues `[0.0025,0.25]` | Fill eigenvalues `[0.02875,0.6475]`; widths `0.1695582496` and `0.8046738470` |
| Quadratic recovery | `J=2+3x-2y+2x²+xy+y²`, 3x3 grid, ridge disabled for fixture | `c=2`, `g=[3,-2]`, `H=[[4,1],[1,2]]`, RMS `<1e-12`; Hessian eigenvalues `3±sqrt(2)` |
| Amplitude | Depth `0.4`, `H=diag(4,2)`, fill covariance `diag(0.25,0.09)` | `A_depth=0.6`, `A_curvature=1.2`, selected amplitude `1.2` |
| Support radii | `sigma_major=0.5` | Support `1.5 m`; exit `1.25 m` |
| Grid minimum present | `H=0.1I`, `Sigma=0.25I`, `A=0.1`, default 41-point grid | At least one residual interior minimum |
| Escalation success | Same model, test caps `amplitude_max=10`, `sigma_ceiling=2`; five rounds | Success after round 5 with `sigma=1.220703125`, `A=4.5262277126`, zero residual minima |
| Bounded failure | Same model with default caps | After five rounds: `sigma=1.25`, `A=3.0`, residual minima remain; one design-failed event; registry unchanged |
| Association | Clusters `(0,0)` and `(1,0)`, candidate `(0.1,0)`, bandwidth `0.5` | Probability for first cluster `0.8320183851`; merge when sigma-major gate radius is at least `0.1` |
| Soft-gate rejection | Candidate `(0.5,0)` between the same clusters | Probabilities `[0.5,0.5]`; no merge because `0.5 < 0.6` |
| Hard-gate rejection | One cluster `(0,0)`, candidate `(5,0)`, sigma majors `0.3` | Soft probability `1.0`, hard radius `0.6`; no merge |
| Revision lifecycle | Old `fill_id=1`, new `fill_id=2`, same `cluster_id=1` | Old record becomes inactive/superseded; new record active at revision 2; active-cluster count remains 1 |
| No double count | Old amplitude 1 and replacement amplitude 2, same center/covariance | Robust Gaussian value at center is `2.0`, not `3.0` |
| Outward minimization direction | `A=2`, `Sigma=I`, point `(1,0)` | Fill `1.2130613194`; gradient `(-1.2130613194,0)`; descent direction `(1.2130613194,0)` points outward |
| Confidence aggregation | Component scores `[1,.75,.5,.8,2/3,1]` | Confidence `0.7861111111`; no low-confidence event at threshold `0.60` |

Also test:

- exact window/age boundary inclusion;
- timestamp regression and speed-jump rejection;
- minimum-sample failure;
- covariance symmetry and eigenvalue clipping;
- depth-only fallback and invalid condition reporting;
- width/amplitude cap behavior;
- anisotropic orientation canonicalization;
- cluster sample de-duplication and deterministic 4000-sample retention;
- monotonic IDs/revisions;
- out-of-order/stale lifecycle record rejection;
- correlated design-failed handling;
- legacy fill/cost outputs with bit-for-bit retained numerical behavior.

### Commands

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 03 implement
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
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
```

```bash
ros2 interface show ros_esc_interfaces/msg/GaussianFill
ros2 interface show ros_esc_interfaces/msg/AlgorithmEvent
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

Acceptance requires:

- every deterministic Phase 03 test passes;
- the existing 44 focused tests remain passing;
- no new package-test failure beyond the documented 875-test lint baseline;
- robust cost evaluation has no superseded or duplicate term;
- supervisor count reflects active clusters, not revisions;
- legacy profile numerical behavior and interfaces remain unchanged;
- launch parsing exposes all defaults with one Gaussian node, one modified-cost node, one supervisor, and one `/cmd_vel` owner;
- runtime instantiation accepts every launch-provided parameter with its
  declared ROS type, including double-valued percentile defaults;
- no physical-hardware or Heavy-Ball action occurs.

## Backward compatibility, risks, and stop conditions

Backward compatibility:

- `algorithm_profile=legacy` remains the default.
- Legacy Gaussian fitting, event-mean behavior, direct convergence trigger, rejection rules, `/cost_bias`, `/cost_modified`, affine behavior, timestamps, and launch arguments remain unchanged.
- Robust mode changes only the fill internals and typed fill consumption.
- Existing legacy consumers require no migration.
- Robust consumers must treat `GaussianFill` as authoritative; `/cost_bias` is a lossy isotropic compatibility projection.
- Existing PDE nodes remain launched and retain their current topics.

Stop implementation and report exact evidence if:

- the Phase 03 implementation validator fails or this saved plan is absent;
- required Phase 00–02 handoffs or source owners no longer match the checkout;
- unrelated user changes overlap a planned file;
- `/odom` and `/gesc_gaussian/source_cost` do not share a usable ROS time base;
- the current runtime cannot produce 40 synchronized valid samples in eight seconds at the configured tolerance;
- robust typed fill consumption cannot be isolated from legacy `/cost_bias` consumption without double counting;
- covariance/revision semantics require changing an existing message field or legacy array;
- the supervisor cannot distinguish supersession records from rejected results;
- legacy numerical tests change;
- SciPy/NumPy functionality used by the pure modules is unavailable;
- implementation would require a physical or Heavy-Ball change.

Runtime `fill_design_failed` is an expected controlled outcome, not an implementation blocker, provided no failed candidate is committed and the supervisor fails safely.

Principal risks:

- `minimum_basin_depth`, amplitude limits, and residual thresholds are in the current raw-cost units and may require later Phase 08 tuning.
- A 41-point grid with repeated escalations must complete within the existing five-second design timeout.
- Sparse trajectory coverage may produce low-confidence depth-only fills.
- Width expansion coupled to amplitude caps may still leave residual minima; the bounded failure path must remain honest.
- `/cost_bias` cannot retract revisions, so legacy live plots may not match the authoritative anisotropic registry after a merge.
- Mixed legacy timestamps remain elsewhere, but robust sample synchronization must use only absolute ROS stamps.

Implementation-time verification assumptions:

- `CostBreakdown.stamp` and `Odometry.header.stamp` both follow Gazebo `/clock`.
- The active rotating-sensor profile remains one channel, so channel index zero is valid; multi-channel execution must validate the configured index.
- The current configured maximum linear velocity remains `0.1 m/s`; the `0.20 m/s` sample guard intentionally allows a factor-of-two tolerance.
- Existing `GaussianFill` fields are sufficient; no message schema extension is needed.
- The existing `python3-scipy` dependency remains sufficient and no new dependency is introduced.
- The active wrapper remains user-owned and unchanged.
- Phase 04 will consume the published support/exit radii and frozen active fill ID; Phase 03 must not implement its geometry or motion transitions.
