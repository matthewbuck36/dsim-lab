# GESC Gaussian Implementation Sequence

This sequence maps Phases 01-10 to the audited repository. Each phase requires
a new saved Plan and implementation handoff. Exact later-phase proposals may
be narrowed by the authoritative phase Plan, but responsibilities must remain
with the owners identified here.

## Compatibility strategy for all phases

1. Keep `use_pde_extensions=False` as the unchanged legacy launch path.
2. Keep all existing topics and positional array layouts.
3. Add typed observability alongside legacy topics before changing behavior.
4. Keep GESC robust behavior opt-in; do not change Heavy-Ball files or defaults
   as a side effect.
5. Keep the negative-voltage minimization sign and current units.
6. Extend the existing cost, filter, controller, convergence, Gaussian, and
   modified-cost owners.
7. Use `ros_esc_interfaces` for new messages.
8. Use the same algorithm owners for simulation and physical operation; only
   adapters may differ.
9. Do not plan physical filenames or topics until the Phase 09 inventory.
10. Serialize declared ROS floating-point parameters with floating-point XML
    or YAML literals and verify their runtime types; `--show-args` alone does
    not prove that a node will accept an override.
11. Preserve the Phase 04 signal-safe controller/supervisor lifecycle: final
    zero must publish while the rclpy context is valid, followed by clean
    executor/node/context teardown under controlled SIGINT.

## Phase 00 - audit

Status: implemented by the five audit documents plus
`handoffs/phase_00_handoff.md`.

No algorithm, launch, configuration, or generated files are in the Phase 00
edit set.

## Phase 01 - common observability contract

Goal: expose the complete current data flow without changing its numerical
behavior.

### Exact Phase 01 planning edit set

Extend the interface package:

- modify `ros2_ws/src/ros_esc_interfaces/CMakeLists.txt`;
- create
  `ros2_ws/src/ros_esc_interfaces/msg/CostBreakdown.msg`;
- create
  `ros2_ws/src/ros_esc_interfaces/msg/GescDiagnostics.msg`;
- create
  `ros2_ws/src/ros_esc_interfaces/msg/ControlDiagnostics.msg`;
- create
  `ros2_ws/src/ros_esc_interfaces/msg/GaussianFill.msg`;
- create
  `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmState.msg`;
- create
  `ros2_ws/src/ros_esc_interfaces/msg/AlgorithmEvent.msg`.

Instrument existing owners:

- modify
  `ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py`;
- modify
  `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`;
- modify
  `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_node_script.py`;
- modify
  `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`;
- modify
  `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py`;
- modify
  `ros2_ws/src/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py`;
- modify
  `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`;
- modify
  `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`;
- modify `ros2_ws/src/ros_esc/package.xml` to declare effective ROS/runtime
  dependencies used by the changed nodes.

Add focused tests and documentation:

- create
  `ros2_ws/src/ros_esc/test/test_observability_contract.py`;
- create `ros2_ws/src/ros_esc/test/test_legacy_behavior.py`;
- create `docs/codex/gesc_gaussian/topic_dictionary.md`;
- create `docs/codex/gesc_gaussian/handoffs/phase_01_handoff.md`.

Do not modify the user-edited
`gesc_gaussian_full_rotation_voltage.bash` in Phase 01. New launch arguments
must have compatible defaults so that wrapper continues to work unchanged.

### Required ownership

- `cost_function_node`: simulation source kind, raw sensor-like value, raw
  minimization cost, and explicitly unavailable source score.
- `modified_cost_node`: raw, Gaussian, affine, augmented values and current
  weights.
- `filter_node`: filter input, output, and internal state diagnostics.
- `Directional_Controller` plus `controller_node`: pre-saturation command,
  post-saturation command, limits, and flags without changing the existing
  returned command.
- `convergence_detector_node` and `gaussian_fill_node`: typed event mirrors.
- `gaussian_fill_node`: typed fill mirror while retaining `/cost_bias`.
- `modified_cost_node`: unavailable-state marker plus current legacy mode until
  Phase 02 owns real states.
- `/odom`: remains the canonical simulation measured-pose/velocity source.

Every unavailable value must have an explicit validity flag; no numeric
source-score or physical data may be invented.

### Change-size split

Phase 01 is expected to exceed ten implementation files because message
definitions and owner instrumentation are both required. Its Plan should split
implementation into two coherent subcommits:

1. interface definitions, generation, serialization tests, and topic
   dictionary skeleton;
2. existing-owner instrumentation, launch wiring, and legacy-equivalence
   tests.

## Phase 02 - state machine and switchable terms

Goal: add explicit state coordination and independently controlled
raw/Gaussian/affine weights.

Extend:

- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`;
- `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`;
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`;
- Phase 01 state/event interfaces.

Proposed new distinct owner, because no current node coordinates states:

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/__init__.py`;
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py`;
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py`.

Modify `ros2_ws/src/ros_esc/setup.py` for its console entry point. Add legacy
and `robust_gaussian_v1` parameter profiles at exact paths approved by the
Phase 02 Plan. Test every state transition, timeout, weight output, source
verification branch, and zero-command failsafe. Do not add fill redesign yet.
The Phase 02 Plan's post-implementation amendment requires a no-hardware
process-level SIGINT test in addition to direct zero-publish unit coverage.

## Phase 03 - robust basin estimation and fill registry

Goal: replace the fragile isotropic fit internals while retaining the existing
Gaussian ROS owner and `/cost_bias` compatibility output.

Extend:

- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py`;
- `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`;
- typed fill/event interfaces from Phase 01;
- supervisor integration from Phase 02.

Proposed internal modules:

- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/basin_estimator.py`;
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_designer.py`;
- `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/fill_registry.py`.

Implement synchronized valid samples, robust center/covariance estimation,
regularized local fitting, amplitude/width coupling, residual-minimum checks,
bounded escalation, association, merging, revision, supersession, and
confidence. Add deterministic numerical unit tests before Gazebo tests.
The Phase 03 Plan's post-implementation amendment requires `10.0` and `80.0`
for the double-valued percentile launch/YAML defaults plus runtime parameter
instantiation coverage.

## Phase 04 - measured escape and recenter

Goal: implement bounded, measurable escape and indoor center return.

Extend:

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/state_machine.py`;
- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py`;
- controller diagnostics and state/event interfaces;
- `ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml`.

Proposed internal module:

- `ros2_ws/src/ros_esc/ros_esc/supervisor_node/escape_recenter.py`.

No planner exists in this checkout. The Phase 04 Plan must approve the smallest
bounded waypoint/room-center behavior, including wall margin, invalid-pose
stop, escape progress, stall, timeout, and deterministic assist direction.

## Phase 05 - unified experiment recording

Goal: add rosbag2, metadata, topic preflight, and completeness checks while
preserving CSV collection.

Proposed files under the existing `ros_esc` package:

- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/__init__.py`;
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/record_run.py`;
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/validate_run.py`;
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/topic_manifest.yaml`;
- `ros2_ws/src/ros_esc/ros_esc/experiment_recording/experiment_metadata.yaml`.

Modify `ros2_ws/src/ros_esc/setup.py` and its install data as required. Use
sqlite3 unless the Phase 05 environment audit finds another registered
backend. Keep
`ros_esc/ros_esc/data_collection_node/data_collection_node_script.py`
available as the legacy CSV path.
Recording completeness must include the final zero produced by the corrected
Phase 04 shutdown lifecycle; recording code must not replace or bypass that
lifecycle. Parameter snapshots use the recorder node's native parameter-service
clients. Required-topic publishers receive three bounded attempts; optional
short-lived nodes receive one. Coordinated simulation shutdown signals live
leaf executables with a 0.1-second stagger, and Python algorithm owners defer
signals until the active callback returns before executor/node/context
teardown.

## Phase 06 - deterministic scenario runner

Goal: execute serial, seeded, timeout-bounded Gazebo scenarios without adding a
physical path.

Proposed files:

- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/__init__.py`;
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py`;
- `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py`;
- Phase-06-approved YAML suites under
  `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/`.

Reuse `turtlebot3_rotating_sensor/launch/gazebo.launch.xml`. Do not create a
second Gazebo algorithm launch graph.
Runner shutdown acceptance must distinguish Gazebo Classic's interrupt exit
from ROS node failures and require final-zero evidence, clean controller and
supervisor exits, and no invalid-context `RCLError`.

## Phase 07 - bag analysis and plots

Goal: read the actual Phase 05 bags, synchronize topics, calculate metrics, and
produce standard figures/tables.

Extend the existing plotting area:

- create
  `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/bag_reader.py`;
- create
  `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py`;
- reuse plotting helpers in
  `ros2_ws/src/ros_esc/ros_esc/plotting_scripts/`.

Add small known bag fixtures or generated fixtures at Phase-07-approved test
paths. Preserve timestamps and flag incomplete runs.
Missing final-zero evidence or an unclean controller/supervisor shutdown must
be one of the explicit incomplete-run conditions.
For matrix throughput, build each timestamp lookup index once per topic stream
and reuse the existing nearest/causal bisect semantics for every anchor.
Optimization must retain byte-identical metrics, completeness, and table
outputs on a recorded reference bag.

## Phase 08 - simulation validation, diagnosis, and freeze

Terminal status as of 2026-07-30: Phase 08 is closed. The broad
simulation-ready objective failed; no 70-unique-case acceptance denominator
or simulation-ready tag exists. The final Phase 08.7 retrospective
known-success reproduction produced `13/17` formal and `14/17` behavioral
passes at simulator-relative `400/1600`, but it is not an unbiased robustness
claim. Read the
[whole-Phase-08 final report](validation/phase_08_final_report.md) and
[final handoff](handoffs/phase_08_final_handoff.md) before Phase 09 planning.
The detailed history below remains useful but its earlier active-subphase
language is superseded by those closeout documents.

Historical disposition: v1 and v2 are closed failed experiment versions. V1
retains its incomplete large-matrix evidence. V2 retains ten activation
attempts and stopped before tuning at Gate 2. Neither may be resumed,
overwritten, relabeled, or counted toward a future claim.

Phase 08.1 completed its bounded retained-evidence diagnosis, corrected fill
latency, verification boundaries, startup readiness, evidence semantics, and
unreachable scenario expectations, then ran two development-only probes. The
calibrated goal contract passed. The fill/create/escape activation prefix
passed, but its full lifecycle failed when the shared clearance-first recenter
selector orbited until timeout. See
[the Phase 08.1 handoff](handoffs/phase_08_1_handoff.md).

Phase 08.2 preserved that failed evidence, kept the current hard wall/fill
rejection rules and assistance behavior, added recenter-only target-progress
guidance plus nonholonomic command-sweep suppression, and validated the exact
retained geometry deterministically. Its one fresh development probe passed
the full fill/create/escape/recenter/search path without timeout, failsafe,
collision, completeness, cleanup, or final-zero failure. See
[the Phase 08.2 handoff](handoffs/phase_08_2_handoff.md).

The reviewed
[Phase 08.3 Plan](plans/phase_08_3_plan.md) is now the active implementation
authority, including its user-authorized Amendment A1. Its 10 activation, 30
bounded-development, 20 predeclared researcher-visible holdout, 50 additional
unique validation, and 10 reproducibility slots use
the fresh root
`/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3`. Its first activation
run is now retained as the closed, instrumentation-contaminated V3A lineage:
the schema-v4 runner spawned its physical contact positive control in an
expected-false case. The append-only M3A Plan amendment permits only the
bounded probe-dispatch correction and a fresh V3B root at
`/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3b`. V3B reuses the exact
committed population bytes, reruns qualification against the corrected source,
and reruns all ten GUI-visible activation cases from the beginning.
The 70 unique acceptance cases and ten repeat references are generated,
canonically hashed, checkpointed, and committed in cleartext before
activation, then evaluated through one hashed machine-readable contract. This
is not a selection-blind claim. Phase 08.2 evidence validates recenter recovery
but does not enter that denominator or establish simulation readiness. Phase
09 remains blocked until the v3 handoff and machine-readable gate results both
establish `simulation_ready=true`.

Phase 08.1 diagnostic scenarios use schema-v3 binding contracts: a contiguous
activation path anchored at the first `VERIFY_EXTREMUM`, required event
membership, selected terminal/forbidden predicates, and explicit
rotation/dwell timing. Cross-producer event receipt order is not treated as a
causal clock. The isolated 450/800-input cases prove below-target classification,
while the 2500-input case proves the calibrated goal branch. Multi-source
ground truth for a future v3 must come from the realized aggregate field or a
justified dominant-target geometry, not a source-role label alone.

The Phase 08.1 readiness correction remains inside the existing controller,
recorder, completeness validator, and scenario runner. Simulation uses two
fresh data/controller-manager barriers around bounded parameter capture and an
atomic final authorization. The barrier covers the controller's actual
pose/filter/timekeeper/state/command inputs, the supervisor's source semantics,
and a clean robust `SEARCH` startup state; delayed-input metadata must agree
with the canonical target's profile, relay gate, and all actual consumer-topic
arguments. Selected operational streams become run-specific required,
single-publisher, retained rosbag evidence. Physical mode is code-enforced not
to inherit Gazebo-specific checks. Shared `AlgorithmEvent` ordering is
validated per established producer, signed emission skew is checked against
receipt-ordered `/clock`,
and fill-request causality remains an exact source-timestamp contract. Strict
JSON evidence normalizes corrupt nonfinite diagnostics to `null` and fails an
explicit finiteness check. The fill node services `/clock` concurrently with
its serialized data/design callbacks in both profiles. A never-ready attempt
is infrastructure-invalid with unavailable behavioral outcomes and is never
retried automatically.

Proposed durable output area:

- `docs/codex/gesc_gaussian/validation/`.

Extend the Phase 06 runner and Phase 07 analysis; do not add another algorithm
implementation. Produce scenario manifests, frozen parameters, machine-readable
results, and a report. A failed gate must remain failed and must block Phase 09
trials.

The Phase 08 v2 budget was exactly 120 declared runs: 10 activation, 30 tuning,
20 new hidden holdouts, 50 additional unique validation cases, and 10 repeats.
It is historical v2 scope, not a permanent development cap. Future work
separates bounded, versioned development attempts from a preregistered
fixed-profile acceptance denominator and separately reported repeats.

The failed/incomplete v1 design of 81 training runs, 12 exposed holdouts, and
three 519-run passes is historical evidence only. Preserve its scenario files,
frozen profile, selection record, and run directories. A failed frozen
experiment version stops its later empirical stages but permits separately
planned diagnosis, engineering correction, and a new version.

Phase 08.1 is closed in
`docs/codex/gesc_gaussian/status/phase_08_status.md`. A successor must create or
approve its own durable Plan before edits or runtime. After compaction or
interruption, reconstruct state from the Plan, active subphase Plan, status,
Git diff, tests, and retained artifacts; do not repeat a batch merely to
recover conversation context.
The matrix must include the corrected runtime parameter-type startup gate and
controlled shutdown-zero/clean-exit gate. The controller spawners use a
30-second service-call timeout for bounded Gazebo startup latency; this is
launch reliability only and does not alter controller or algorithm parameters.

## Phase 09 - physical integration

Goal: inventory and then connect real adapters to the same canonical
interfaces. The Phase 09 inventory and Plan may be prepared after the closed
Phase 08 report, but physical motion remains prohibited until the Plan
explicitly resolves the failed broad simulation-readiness boundary and the
user authorizes hardware execution.

First required artifact:

- `docs/codex/gesc_gaussian/phase09_physical_interface_inventory.md`.

The current checkout does not provide exact Vicon, photoresistor, physical
launch, or hardware command paths. The Phase 09 Plan must stop instead of
guessing if the authoritative physical checkout is unavailable.

No algorithm fork is permitted. Only audited adapter/launch files may differ
from simulation.
Physical readiness must reverify final zero under the audited physical stop
path; it may not assume that simulation SIGINT evidence alone proves hardware
safety.

## Phase 10 - final documentation

Goal: update real repository documentation using verified prior artifacts.

Candidate existing files to update:

- `README.md`;
- `ros2_ws/src/ros_esc/README.md`;
- `ros2_ws/src/turtlebot3_rotating_sensor/README.md`.

Final durable documentation belongs under:

- `docs/codex/gesc_gaussian/`.

It must cover architecture, math, state transitions, topics, messages,
parameters, experiment execution, reproduction, results, compatibility,
physical limitations, and unsupported claims. All commands and links must be
verified against completed phases.

## Required handoff chain

Every implementation phase creates:

```text
docs/codex/gesc_gaussian/handoffs/phase_XX_handoff.md
```

Later work must read all earlier handoffs. The current phase Plan controls
approved intent; the handoffs and live repository control what was actually
implemented.
