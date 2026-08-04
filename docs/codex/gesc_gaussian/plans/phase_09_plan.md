# Phase 09 Plan — Selected-Scenario Physical Snapshot Integration

## Document status and authority

This is the reviewable Plan for Phase 09 no-hardware implementation. It was
prepared on 2026-07-31 from the live checkout and the source-only physical
TurtleBot3 snapshot. It is not implementation approval and does not authorize
access to the live Raspberry Pi, motor commands, rotating-sensor operation,
lamp tests, or any other physical execution.

Planning base:

```text
repository: /home/mattb/dsim-lab
branch: feature/gesc-gaussian-robustness-v1
HEAD: c04c222dfeac525197bf0542cbde64f1421dc664
Phase 08 terminal commit: 9335da2057ac488944578af9f941d8d8fb6164ae
Phase 08 receipt commit: c04c222dfeac525197bf0542cbde64f1421dc664
snapshot Pi home: /home/mattb/physical_TB3_files_snapshot/pi
snapshot source root: /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src
live-Pi mount point reserved for later use: /home/mattb/tb3-pi
```

The mandatory Plan preflight passed:

```text
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/
  validate_phase_context.sh 09 plan

Phase 09 context covers selected-scenario planning and static snapshot
integration only.
This validator does not authorize live Pi access or physical motion.
Phase 09 plan context is complete.
```

The checkout was already intentionally dirty before this Plan was created.
Nine user-owned files—the Phase 09 package documents/prompts plus the context
validator—are modified. Their aggregate package diff SHA-256 was
`dadf2a8241ee7a87301310b6e0852836b17cd0e4c5bb356218c9111e7fc343d5`
before this file was added. The user subsequently authorized bounded alignment
edits to `prompts/09_physical_PLAN.md` and
`prompts/09_physical_IMPLEMENT.md`; both now freeze the same cumulative v8.12
selection rule as this Plan. At this review boundary, the aggregate package
diff SHA-256 is
`fc6117f5748a922c2ff67ae841b024f765efabda21ee402161c055c533fabf4f`.
Those prompt edits do not authorize source or hardware actions. Phase 09 work
must preserve all existing edits unless the user separately authorizes further
changes.

### Shared-lab legacy compatibility amendment

On 2026-07-31, after the initial M3 implementation, the user explicitly
strengthened the compatibility requirement because the TurtleBot3 is shared
across the laboratory: Phase 09 must not alter any pre-existing ESC method's
launch behavior or break its Bash entry point. This is a bounded Level B scope
correction that strengthens the existing legacy-preservation objective without
changing the selected v8.12 algorithm, owners, interfaces, sign, units, or
safety gates.

The existing
`light_gesc_gaussian_fill_experiment.launch.xml` and every pre-existing Bash
wrapper must therefore remain byte-for-byte equal to the M0 snapshot manifest.
Phase 09 uses a new dedicated
`gesc_gaussian_two_source.launch.xml`; only the new managed
Phase 09 wrapper and the physical recorder target contract may reference it.
Static qualification must check every Bash file with `bash -n`, verify each
wrapper's launch arguments against the launch description it names, and prove
the baseline hashes for all pre-existing wrappers and the old launch. This
amendment supersedes later wording that says to extend the old launch in place.

### M7.1 operator-entry, recording, and final-audit amendment

On 2026-07-31, after the sealed M7 snapshot closeout, the user requested one
final full implementation audit and simpler operator-facing names. This is a
bounded Level B continuation of the no-hardware snapshot milestone. It does
not authorize the live Pi, serial devices, a ROS hardware graph, calibration,
motors, the rotating frame, lamps, or motion.

The new-only selected entry point becomes:

```text
turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/
  voltage_cost_values/gesc_gaussian_two_source_voltage.bash
```

and it launches:

```text
turtlebot3_vehicle_nodes/launch/gesc_gaussian_two_source.launch.xml
```

The superseded Phase 09-only names must be absent from the final snapshot and
installed package. This rename does not alter any M0 asset: all 26 historical
Bash files, eight historical launches, six historical controller/filter/
rotation configurations, and their launch mappings remain byte-identical.

The existing `ros_esc record_run` remains the sole recorder, readiness owner,
and shutdown/completeness owner. The selected wrapper must continue to create
one unique date/run-ID directory and one sqlite3 rosbag containing the legacy
sensor, encoder, odometry, filter, and command streams plus the typed
GESC/Gaussian cost, filter, control, state, event, fill, readiness, IMU, and
supporting streams declared by `topic_manifest.yaml`. It must retain metadata,
resolved topics, resolved parameters, `console.log`, notes, and
`completeness.json`; it must not start the legacy CSV collector or a second
recorder.

Because the source-only physical workspace is not necessarily a Git checkout,
each selected run must additionally retain byte-for-byte copies and SHA-256
provenance for every file-backed input that determines the run: calibration,
selected profile, scenario metadata, controller, filter, and rotation
configuration, plus the selected wrapper/launch and recorder topic/QoS
contracts. The wrapper may create new-only temporary controller/rotation
copies solely to resolve the reviewed workspace's dynamic Python-object paths;
both used copies and their immutable templates must be retained, and temporary
copies must be removed after the managed run. These copies live inside the
same unique run directory under a configuration subdirectory with a
machine-readable manifest. Invalid,
missing, duplicate, or ambiguous evidence-file inputs must fail before rosbag
or the target graph starts. This is the rosbag-era replacement for the legacy
collector's configuration text in `comments.txt`; it does not add a second
recorder or claim CSV-format compatibility.

For operator visibility, the selected wrapper must opt into terminal streaming
from the existing recorder and a bounded one-second live summary. The terminal
summary is diagnostic only and must report readiness, source voltage/raw cost,
augmented-cost components, filter output, algorithm state/fill count, pose,
and final `vx`/`wz` when available. The same lines remain in `console.log`, and
all authoritative data remain in the rosbag. Simulation and legacy defaults
remain unchanged unless their callers explicitly opt in.

The final audit must also prove `record_run` can capture provenance when its
working directory is a Git checkout and can start safely with explicit
`git.available=false` provenance when the physical workspace is not a Git
checkout. A missing Git worktree must not abort a physical run before bag or
target startup. The run directory must be printed at startup as well as at
completion so interrupted evidence is discoverable.

M7.1 acceptance requires focused tests for the non-Git fallback, retained and
hashed configuration evidence, terminal tee, rate-limited diagnostic
rendering, renamed target coupling, exact bag topic superset, run-directory
artifacts, shutdown/final-zero/completeness behavior, and absent superseded
installed names. Repeat the isolated three-package build,
all Phase 09 tests, shared/core/recording/legacy regressions, every Bash syntax
check, every wrapper launch-argument check, and the legacy M0 hash guard. Then
regenerate the 51-path transfer manifest, 339-file after hashes, 425-entry
after inventory, reviewable patch, forward/reverse recovery proof, status,
qualification evidence, handoff, and checkpoint. Preserve all earlier M7
results as historical evidence rather than silently relabeling them.

### M8A live-Pi transfer and manual-entry amendment

On 2026-08-01 the user mounted the real Pi home at `/home/mattb/tb3-pi` and
explicitly authorized applying the reviewed Phase 09 snapshot changes to the
physical source tree. That authorization covers source/configuration transfer
and host-side static checks only; it does not authorize a remote/on-Pi command,
ROS launch, serial access, calibration, mechanism actuation, or motion.

The user's manual workflow additionally requires the selected
`gesc_gaussian_two_source_voltage.bash` entry point to perform its own bounded
three-package build and then source the resulting workspace. The live-transfer
audit found that M7.1 only sourced an already-built workspace. The bounded
correction adds a commented build of exactly `ros_esc_interfaces`, `ros_esc`,
and `turtlebot3_vehicle_nodes` before source, documents the behavior, and adds
a build-before-source regression assertion. It changes only three existing
Phase 09 transfer-manifest paths and does not touch a historical wrapper,
launch, or configuration.

M8A must retain the original 51-path transfer scope, create and verify the
scoped live-Pi rollback backup before writing, suppress unrelated parent-
directory/owner/group metadata changes, require zero final snapshot-to-Pi dry-
run differences, reseal the snapshot hashes/inventory/patch, and record every
unrun on-Pi/hardware gate honestly. The exact receipt is
`docs/codex/gesc_gaussian/validation/phase_09_pi_transfer_receipt.md`.

### M8B evaluation-only Vicon and single-entry commissioning amendment

On 2026-08-01 the user clarified the required physical data boundary after
reviewing `DSIM - TurtleBot3 Vicon Setup.pdf` and the ONR interim report. The
TurtleBot wheel/IMU-backed `/odom` stream remains the only pose input to the
controller, supervisor, PDE/history, modified-cost, Gaussian-fill placement,
and escape logic. Vicon is required ground-truth/evaluation evidence for a
selected two-source trial, but it must be published as
`geometry_msgs/msg/PoseStamped` on the separate canonical topic
`/gesc_gaussian/evaluation/vicon_pose` and must never be remapped,
forwarded, or copied into an algorithm pose input. A missing, malformed, or
stale Vicon stream may keep recorder readiness false or close an evidence-
incomplete run; Vicon data may not determine velocity, fill placement,
candidate ranking, stopping geometry, or any other control calculation.

This is a bounded Level B physical evidence and operator-UX correction. It
supersedes the earlier statements that Vicon is optional, not required by the
selected manifest, and absent from the selected launch. The existing generic
`odometry_node_script.py`, its legacy Vicon/dead-reckoning CLI, and both legacy
Vicon client/server sources remain byte-identical. The historical native
seven-float UDP packet cannot prove subject identity, segment identity,
occlusion state, or advancing Tracker frames and is therefore not sufficient
for selected-trial evidence. Add an independent Phase-09-only Windows Vicon
server plus `phase09_vicon_evidence_node` inside the existing odometry package.
The versioned JSON protocol requires an explicit commissioned subject and
segment, client nonce, server session identifier, strictly advancing packet
sequence and Tracker frame number, translation/rotation occlusion flags,
finite millimetre pose, and a normalized quaternion. Wrong identity, malformed
or nonfinite data, occlusion, duplicate/regressing frame or sequence, session
change, or stale input fails closed. The Pi uses its ROS receipt time for the
pose stamp and converts millimetres to metres exactly once.

The evidence node publishes the evaluation pose as
`geometry_msgs/msg/PoseStamped` and a canonical JSON status heartbeat as
`std_msgs/msg/String` on `/gesc_gaussian/evaluation/vicon_status`. The status
retains protocol/session/sequence/frame/identity/occlusion and rejection
counters so a stationary but advancing Tracker stream is distinguishable from
a frozen replay. Both topics are required physical evidence. The dedicated
Phase 09 launch receives inert Vicon defaults and starts only these selected
owners when the selected wrapper explicitly enables them. The different topics
and `PoseStamped` type provide defense in depth against an accidental `/odom`
control remap. Every historical launch, Bash wrapper, configuration, topic
mapping, source owner, and legacy entry point remains byte-identical.

The selected physical manifest and sole `record_run` owner must require fresh,
finite pose and valid advancing status heartbeats in physical mode, record both
in the same sqlite3 rosbag, show wheel/IMU odometry and Vicon evaluation data
with unambiguous labels in the live terminal summary, and validate identity,
session continuity, frame/sequence progression, occlusion state, and run-
interval coverage offline. Metadata must state `role: evaluation_only`,
`required: true`, the canonical topics, reviewed Vicon endpoint, versioned
protocol, subject, segment, server-script hash, and `algorithm_visible: false`.
The actual subject and segment are not present in either supplied PDF and must
remain null in shipped templates until discovered with Tracker live. Static
target-coupling tests must prove that all four algorithm pose arguments remain
exactly `/odom` while Vicon appears only in the evaluation node, recorder
contract, live diagnostics, and metadata.

The calibration gate is immutable rather than self-declared. It freezes the
exact Arduino protocol, `9600` baud, firmware SHA-256, zero parser errors with a
nonzero denominator, strictly increasing sample timestamps, maximum sample gap
below `0.50 s`, the selected three-second rotation window, at least five
complete encoder-confirmed rotations per condition, the exact 4.0 target and
`[3.6, 4.4]` bounds, retained median/MAD/`3*MAD` calculations, strictly
separated strong/weak raw-cost intervals, path-plus-SHA evidence, and a valid
UTC calibration review. Shipped calibration and scenario templates remain
entirely inert; no PDF-derived or synthetic measurement may be written into
them.

The laboratory operator workflow is also frozen here. The shipped templates
must never be edited in place. Before the first stationary preflight, create
mutable copies of the calibration and primary/secondary scenario metadata
under `${XDG_CONFIG_HOME:-$HOME/.config}/dsim-lab/phase09`; the same site
metadata bytes used by that preflight are later hash-coupled to the separate
approval. The selected audit profile remains the installed frozen input, not
a mutable commissioning file.
After the ordered commissioning gates below have populated and reviewed the
site calibration and readiness fields, running
`gesc_gaussian_two_source_voltage.bash` with no arguments is the normal primary
scenario entry point and reads the reviewed stable serial device from the
calibration document. `--scenario secondary` and explicit path overrides
remain available only for separately reviewed use. Immediately before a real
run, the wrapper must require the typed `RUN` confirmation covering the
assigned operator and observer, clear/open floor, independent emergency stop,
and ready Vicon server. It then creates a temporary run-specific metadata copy
containing those per-run attestations; neither the inert source templates nor
the reviewed persistent site copy is silently marked ready. `record_run`
retains the exact run metadata, site inputs, and immutable scenario template as
evidence. There is no noninteractive motion bypass.

Add `--check-only` so an operator can perform the bounded build/source and
configuration/commissioning audit without creating run metadata, opening a
serial device, starting the Vicon client, launching ROS nodes, or publishing a
command. It must list any remaining one-time commissioning blockers and state
that live Vicon, ROS ownership, final-zero, and physical checks are still
deferred to the appropriate authorized rehearsal. The user's current request
authorizes offline-snapshot source/configuration changes plus a reviewed,
backed-up SSHFS source transfer; it does not authorize an on-Pi command, ROS
graph, serial/GPIO access, calibration, lamp operation, mechanism actuation, or
robot motion.

Add a separately explicit `--stationary-preflight` commissioning mode to close
the historical `stationary_graph_verified` ordering gap. It requires a named
operator and observer plus a `PREFLIGHT` attestation and consumes the mutable
site metadata copy created before this step. It retains a run-specific copy but
does not mutate the site metadata; every motion-readiness boolean remains
false. It launches a Phase-09-only passive real-time timekeeper instead of the
servo-command owner and invokes `record_run` for a fixed finite window with
readiness held false.
The recorder must never call its authorization method in this mode, must fail
on any nonzero base command or robust lifecycle advance, and must retain full
graph, parameter, odom, IMU, source, Vicon, recording, shutdown, and final-zero
evidence. Offline validation uses the explicit stationary hold interval and
requires that readiness was never true. A retained PASS must be reviewed and
hash-coupled before a separate approval action may set the persistent
`stationary_graph_verified` field; the approval must verify the exact same
site-metadata bytes used by the preflight, and the preflight must not
self-certify its own gate. The passive timekeeper and special recorder mode are
selected-only and leave every legacy rotate-frame path unchanged.

M8B acceptance requires a fresh pre-edit snapshot backup, focused unit tests
proving legacy Vicon and rotation sources remain unchanged, versioned UDP/JSON
schema and identity checks, clean retry/shutdown, malformed/nonfinite/
occluded/frozen-stream rejection, evaluation-topic isolation, pose/status
heartbeat readiness and revocation, stationary-preflight no-authorization and
no-actuation selection, offline semantics/coverage, live diagnostic labels,
strict calibration mutation tests, wrapper defaults/check-only/PREFLIGHT/RUN/
runtime-metadata behavior, exact legacy hash guards, all Bash syntax and
wrapper-launch argument checks, an isolated three-package host build, the
complete Phase 09 regression set, updated snapshot recovery evidence, a fresh
scoped Pi backup, zero-difference final snapshot-to-Pi dry run, status/handoff/
checkpoint updates, and explicit retention of every unrun on-Pi/hardware gate.

## Objective

Integrate the selected counted-candidate GESC plus adaptive Gaussian behavior
into the existing physical TurtleBot3 source owners, first in the local
source-only snapshot and with no hardware. The implementation will:

- port the current shared algorithm and typed interfaces without creating a
  simulation/physical algorithm fork;
- extend the existing photoresistor, command, and Phase 05 recording owners,
  while isolating the selected graph in a new Phase 09 launch file;
- use rotating-photoresistor measurements, wheel/IMU-backed `/odom`, active
  typed fills, and configured source count as the only control inputs;
- preserve the negative-voltage minimization convention and legacy topics;
- make all snapshot edits recoverable despite the snapshot not being Git;
- qualify everything possible with bounded host-side static/offline checks;
  and
- leave every live-Pi, serial, sensor, motor, emergency-stop, lamp, and floor
  check explicitly unexecuted.

Phase 09 snapshot implementation succeeds only as a static integration
milestone. It cannot declare physical readiness. A later physical run requires
a reviewed handoff, an available robot, live calibration, a successful
emergency-stop/final-zero rehearsal, and separate explicit user authorization.

## Accepted evidence and nonclaims

The user accepts these fixed simulation results as sufficient to prepare a few
selected physical demonstrations:

| Evidence | Accepted result | Phase 09 use |
|---|---:|---|
| v8.10 primary fixed two-light layout | `11/11` formal pass | retained primary geometry and cumulative counted-profile evidence |
| v8.11 secondary fixed two-light layout | `6/6` formal pass | retained secondary geometry and evaluator-contract evidence; no controller-runtime change |
| v8.12 interior-anchor visible probe | `1/1` formal pass | latest runtime addition and successful corrective evidence; enable it in the selected physical profile |
| v8.12 first broad-matrix case | scientific local-to-global completion, formal `13/14` fail | user-accepted behavior with the frozen formal hiccup retained; no broad claim |

The v8.12 failure is immutable. There is no v8.13 and no broad
`simulation_ready=true` result. Phase 09 must not claim arbitrary
layout/intensity, three-light, wall, obstacle, collision-avoidance, global
localization, or broad physical robustness. The initial field is open,
obstacle-free, and continuously operator-managed.

Simulator `400/1600` values are relative model inputs, not physical lumens,
lux, voltage, PWM settings, or calibration constants. Physical lamp settings
must be selected from measured photoresistor response and frozen before any
motion trial.

### Cumulative version-selection rule

Phase 09 ports one cumulative algorithm source boundary; it does not
cherry-pick or blend three competing algorithm versions. V8.10, v8.11, and
v8.12 are successive experiment/evidence versions in one Git history:

- v8.10 retained the counted-candidate controller profile and corrected the
  scenario runner/recorder working-directory boundary;
- v8.11 changed the simulation evaluator and schema so the shifted aggregate
  basin could be associated correctly, but did not change the controller,
  filter, Gaussian-fill, modified-cost, convergence-detector, or supervisor
  runtime owners; and
- v8.12 made the only later core-runtime change: it added the opt-in
  `interior_farthest` odometry-history fallback to the three existing
  supervisor files.

The shared core runtime has not changed between the qualifying v8.12 source
commit `0263f1c` and the Phase 08 terminal HEAD `c04c222`. Implementation must
therefore port the current terminal shared files exactly, not reconstruct an
algorithm from old commits. The selected physical wrapper enables the v8.12
fallback with its frozen `0.50 m` minimum displacement. The shared node and
launch default remains `False` solely for legacy compatibility. V8.11
evaluator topology and source geometry remain recorder/evaluator metadata and
never enter physical control.

## Repository and snapshot findings

### Current shared implementation in `dsim-lab`

The current repository contains the selected behavior in existing owners:

- final command and sole `/cmd_vel` publisher:
  `ros2_ws/src/ros_esc/ros_esc/controller_node/controller_node_script.py`;
- state, counted-candidate ranking, recovery, stale-input policy, and stop:
  `ros2_ws/src/ros_esc/ros_esc/supervisor_node/`;
- adaptive basin estimation, fill design, registry, and typed fill lifecycle:
  `ros2_ws/src/ros_esc/ros_esc/gaussian_fill_node/`;
- raw/Gaussian/temporary-affine composition:
  `ros2_ws/src/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py`;
- GESC filter and diagnostics:
  `ros2_ws/src/ros_esc/ros_esc/filter_node/filter_node_script.py`;
- sole recorder/readiness owner and sole completeness validator:
  `ros2_ws/src/ros_esc/ros_esc/experiment_recording/record_run.py` and
  `validate_run.py`; and
- six robust typed messages in `ros2_ws/src/ros_esc_interfaces/msg/`.

The controller already gates motion on fresh recorder readiness, fresh pose,
fresh filter input, fresh supervisor state/command, valid state, and shutdown
zero. The selected counted profile compares complete-rotation raw-cost minima
using a median/MAD interval, permits exactly one fill for two known sources,
keeps Gaussian memory active, and clears temporary assistance after recovery.

### Physical snapshot

The snapshot source root contains `306` regular files, occupies approximately
`79 MiB`, contains no symlinks, and has no `.git` directory beneath the source
root. Its three packages are:

```text
ros_esc
ros_esc_interfaces
turtlebot3_vehicle_nodes
```

It already has the correct physical owner locations:

- serial photoresistor:
  `turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/photoresistor_node/`;
- rotating-frame encoder/servo:
  `turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/encoder_node/` and
  `rotate_frame_node/`;
- TurtleBot bringup:
  `turtlebot3_vehicle_nodes/launch/vehicle_bringup.launch.py`;
- wheel-odometry/Vicon relay:
  `turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/odometry_node/`;
- physical light GESC plus Gaussian launch:
  `turtlebot3_vehicle_nodes/launch/light_gesc_gaussian_fill_experiment.launch.xml`;
- physical GESC voltage controller and filter configurations; and
- a physical `ros_esc` package with the legacy GESC/PDE/Gaussian owners.

The snapshot is older than the typed robust implementation:

- `ros_esc_interfaces` has only the five legacy messages;
- no supervisor, typed fill registry/designer, deferred shutdown helper,
  search-epoch helper, or Phase 05 recorder/validator exists;
- the physical GESC+Gaussian launch defaults its PDE/fill pose to a Vicon
  relay, uses broad `pkill -9` commands, starts the legacy CSV collector, and
  does not gate `/cmd_vel` on Phase 05 recording readiness;
- the wrapper requests two fills even though the launch default is one;
- the photoresistor node hard-codes `/dev/ttyUSB0`, parses Arduino text in an
  unbounded thread, silently catches all parse/serial errors, and publishes
  only legacy `StampedFloat64MultiArray`; and
- its voltage convention is already correct: positive measured voltage is
  multiplied by `-1` so stronger light is a lower raw minimization cost.

The installed host TurtleBot3 Burger configuration sets
`diff_drive_controller.odometry.use_imu: true`. The selected controller path
will therefore consume wheel/IMU-backed `/odom`; it will not subscribe to
Vicon. The expected raw IMU topic is `/imu` with
`sensor_msgs/msg/Imu`, but that exact live topic/type and its publisher must be
verified on the Pi before it may be treated as passed.

The current physical directional-controller configuration limits linear and
angular commands to `0.10 m/s` and `0.50 rad/s`. Phase 09 will add a separate
lower-speed selected-profile configuration rather than overwrite this legacy
configuration.

## Fixed ownership and data-flow contract

No new ROS package, controller node, supervisor node, recorder node, validator,
or public message is justified. The six existing typed messages are ported.
One pure helper module may be added inside the existing photoresistor owner to
make parsing/calibration unit-testable; it is not a ROS node or topic owner.

```text
Arduino photoresistor
  -> existing photoresistor_node
       -> /turtlebot3/cost_value_chatter       legacy raw cost (-V)
       -> /gesc_gaussian/source_cost            typed physical CostBreakdown
              |
              v
       existing modified_cost -> existing filter -> existing controller
              ^                        ^                 |
              |                        |                 v
        typed active fills      rotating encoder     sole /cmd_vel
              ^                                          |
              |                                          v
        existing Gaussian <- existing supervisor <- wheel/IMU-backed /odom

existing record_run
  -> /gesc_gaussian/recording_ready
  -> /gesc_gaussian/stop_requested
  -> final readiness false, final zero, bag finalization, scoped cleanup

scenario coordinates and lamp roles/settings
  -> recorder/evaluator metadata only
required Vicon PoseStamped + advancing identity/status heartbeat
  -> evaluation evidence and recorder readiness/completeness only
  -X-> controller, supervisor, fill design, escape direction, or stopping
```

The selected graph has exactly one `/cmd_vel` publisher: the existing
`ros_esc` controller. TurtleBot3 bringup consumes that topic. No teleop,
navigation, second controller, relay, mux, or emergency-stop publisher may be
silently added to the selected run graph.

## Exact file scope

In this section, `S` means:

```text
/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src
```

### Shared interface files to update or create under `S`

Modify:

```text
S/ros_esc_interfaces/CMakeLists.txt
S/ros_esc_interfaces/package.xml
```

Create by porting the current definitions byte-for-byte:

```text
S/ros_esc_interfaces/msg/AlgorithmEvent.msg
S/ros_esc_interfaces/msg/AlgorithmState.msg
S/ros_esc_interfaces/msg/ControlDiagnostics.msg
S/ros_esc_interfaces/msg/CostBreakdown.msg
S/ros_esc_interfaces/msg/GaussianFill.msg
S/ros_esc_interfaces/msg/GescDiagnostics.msg
```

The five existing legacy messages remain present and unchanged.

### Shared algorithm files to update or create under `S`

These runtime owners must match their current `dsim-lab` counterparts
byte-for-byte after the port unless this Plan explicitly classifies a file as
physical packaging, adapter, or recorder configuration:

```text
S/ros_esc/ros_esc/deferred_signal_shutdown.py
S/ros_esc/ros_esc/search_epoch.py
S/ros_esc/ros_esc/controller_node/controller_node_script.py
S/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py
S/ros_esc/ros_esc/convergence_detector_node/convergence_detector_node_script.py
S/ros_esc/ros_esc/filter_node/filter_node_script.py
S/ros_esc/ros_esc/gaussian_fill_node/__init__.py
S/ros_esc/ros_esc/gaussian_fill_node/basin_estimator.py
S/ros_esc/ros_esc/gaussian_fill_node/fill_designer.py
S/ros_esc/ros_esc/gaussian_fill_node/fill_registry.py
S/ros_esc/ros_esc/gaussian_fill_node/gaussian_fill_script.py
S/ros_esc/ros_esc/modified_cost_node/modified_cost_script.py
S/ros_esc/ros_esc/pde_history_node/pde_history_script.py
S/ros_esc/ros_esc/pde_cost_history_node/pde_cost_history_script.py
S/ros_esc/ros_esc/supervisor_node/__init__.py
S/ros_esc/ros_esc/supervisor_node/escape_recenter.py
S/ros_esc/ros_esc/supervisor_node/state_machine.py
S/ros_esc/ros_esc/supervisor_node/supervisor_node_script.py
```

`S/ros_esc/ros_esc/config_parsing.py` is already byte-identical and must remain
so. Existing physical controller/filter/rotation JSON files are not replaced
wholesale because their source-root paths and hardware settings are physical
configuration, not shared algorithm code.

### Existing Phase 05 owner to port and extend under `S`

Create the current recorder assets, then make only the declared physical-mode
extensions:

```text
S/ros_esc/ros_esc/experiment_recording/__init__.py
S/ros_esc/ros_esc/experiment_recording/record_run.py
S/ros_esc/ros_esc/experiment_recording/validate_run.py
S/ros_esc/ros_esc/experiment_recording/topic_manifest.yaml
S/ros_esc/ros_esc/experiment_recording/experiment_metadata.yaml
S/ros_esc/ros_esc/experiment_recording/qos_overrides.yaml
S/ros_esc/setup.py
S/ros_esc/package.xml
```

`validate_run.py`, the metadata template, and QoS file should remain
byte-identical unless a focused test demonstrates a bounded physical-mode gap.
Such a gap requires a recorded Level B amendment before editing. The planned
physical extensions belong in the existing `record_run.py` and
`topic_manifest.yaml`; there will still be one readiness publisher, recorder,
manifest contract, and validator.

Snapshot `ros_esc/setup.py` and `package.xml` are physical packaging files, so
they will intentionally differ from simulation packaging: install the Phase 05
assets and shared runtime entry points, but do not add the Gazebo scenario
runner, simulation analysis entry points, `gazebo_msgs`, or a dependency on
`turtlebot3_rotating_sensor`.

### Physical adapter, launch, configuration, and test files under `S`

Modify:

```text
S/turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/photoresistor_node/
  photoresistor_node_script.py
S/turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/photoresistor_node/README.md
S/turtlebot3_vehicle_nodes/setup.py
S/turtlebot3_vehicle_nodes/package.xml
S/turtlebot3_vehicle_nodes/README.md
```

Create:

```text
S/turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/photoresistor_node/
  photoresistor_adapter.py
S/turtlebot3_vehicle_nodes/config_files/gesc_gaussian/
  phase09_photoresistor_calibration.yaml
S/turtlebot3_vehicle_nodes/config_files/gesc_gaussian/
  phase09_selected_profile.yaml
S/turtlebot3_vehicle_nodes/config_files/gesc_gaussian/
  phase09_primary_metadata.yaml
S/turtlebot3_vehicle_nodes/config_files/gesc_gaussian/
  phase09_secondary_metadata.yaml
S/turtlebot3_vehicle_nodes/config_files/controller_config_files/
  phase09_gesc_controller_full_rotation_voltage.json
S/turtlebot3_vehicle_nodes/launch/
  gesc_gaussian_two_source.launch.xml
S/turtlebot3_vehicle_nodes/bash_scripts/light_esc_experiments/
  voltage_cost_values/gesc_gaussian_two_source_voltage.bash
S/turtlebot3_vehicle_nodes/test/test_photoresistor_adapter.py
S/turtlebot3_vehicle_nodes/test/test_phase09_physical_launch.py
S/ros_esc/test/test_phase09_shared_parity.py
S/ros_esc/test/test_phase09_physical_recording.py
```

M8B extends that original scope only through the existing owners and the
following selected-only files. It modifies the selected wrapper/launch,
photoresistor calibration helper and inert site templates, package entry-point
metadata, and the existing `record_run.py`, `validate_run.py`, and
`topic_manifest.yaml` recorder contract. It creates:

```text
S/turtlebot3_vehicle_nodes/tools/phase09_vicon_evidence_server.py
S/turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/odometry_node/
  phase09_vicon_evidence_node.py
S/turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/rotate_frame_node/
  phase09_rotation_node.py
S/turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes/rotate_frame_node/
  phase09_stationary_timekeeper_node.py
S/turtlebot3_vehicle_nodes/test/test_phase09_vicon_evidence.py
S/turtlebot3_vehicle_nodes/test/test_phase09_rotation_gate.py
```

These are evaluation-evidence, selected-rotation authorization, and passive
stationary owners, not duplicate controller, odometry, legacy rotation,
recorder, or validator owners.

The existing `light_gesc_gaussian_fill_experiment.launch.xml`, its
`gesc_gaussian_fill_full_rotation_voltage.bash` entry point, every other
pre-existing Bash wrapper, Vicon client/server files, generic odometry relay,
Arduino firmware, Heavy-Ball launch/wrappers, legacy CSV collector, and
nonselected experiment wrappers remain byte-identical and selectable. The new
selected wrapper is an operator entry point, not a new graph owner; it invokes
the existing `record_run` around the dedicated Phase 09 launch.

### Durable `dsim-lab` artifacts to create during implementation

Only durable planning/evidence files are written in Git. Create:

```text
docs/codex/gesc_gaussian/status/phase_09_status.md
docs/codex/gesc_gaussian/validation/phase_09_snapshot_backup_receipt.md
docs/codex/gesc_gaussian/validation/phase_09_snapshot_inventory_before.tsv
docs/codex/gesc_gaussian/validation/phase_09_snapshot_before.sha256
docs/codex/gesc_gaussian/validation/phase_09_shared_source_manifest.tsv
docs/codex/gesc_gaussian/validation/phase_09_snapshot_inventory_after.tsv
docs/codex/gesc_gaussian/validation/phase_09_snapshot_after.sha256
docs/codex/gesc_gaussian/validation/phase_09_snapshot.patch
docs/codex/gesc_gaussian/validation/phase_09_transfer_manifest.txt
docs/codex/gesc_gaussian/validation/phase_09_legacy_compatibility.md
docs/codex/gesc_gaussian/validation/phase_09_static_qualification.md
docs/codex/gesc_gaussian/validation/phase_09_pi_transfer_and_rollback.md
docs/codex/gesc_gaussian/handoffs/phase_09_handoff.md
```

`docs/codex/gesc_gaussian/checkpoints/phase_09_checkpoint.txt` is generated by
the existing checkpoint tool at material boundaries. Large archives and logs
remain outside Git; their exact path and hash go in the receipt/status.

### Explicitly out of scope for modification

The following list is the original M0-M7 snapshot boundary. The dated M8A/M8B
amendments supersede only the explicitly reviewed selected-only source and
evidence paths; they do not broaden modification authority elsewhere.

- all `dsim-lab/ros2_ws/src` simulation or shared source in this selected
  snapshot implementation;
- all Phase 08 scenarios, reports, bags, plots, status, handoffs, and commits;
- `/home/mattb/tb3-pi` and every live-Pi file, except a separately authorized,
  receipt-backed M8 source-only transfer;
- legacy snapshot Vicon clients/servers and their launch paths;
- snapshot Arduino firmware;
- generated `build`, `install`, `log`, cache, editor, Git-metadata, and runtime
  paths; and
- any motor, OpenCR, serial, servo, lamp, or physical-process state.

## Public interfaces and adapter behavior

### Canonical selected physical topics

| Topic | Type | Owner/use |
|---|---|---|
| `/turtlebot3/cost_value_chatter` | `ros_esc_interfaces/msg/StampedFloat64MultiArray` | photoresistor legacy `-V`; preserved |
| `/gesc_gaussian/source_cost` | `ros_esc_interfaces/msg/CostBreakdown` | photoresistor typed physical source |
| `/gesc_gaussian/cost_breakdown` | `ros_esc_interfaces/msg/CostBreakdown` | existing modified-cost owner |
| `/gesc_gaussian/gesc_diagnostics` | `ros_esc_interfaces/msg/GescDiagnostics` | existing filter owner |
| `/gesc_gaussian/control_diagnostics` | `ros_esc_interfaces/msg/ControlDiagnostics` | existing controller owner |
| `/gesc_gaussian/gaussian_fills` | `ros_esc_interfaces/msg/GaussianFill` | existing fill owner |
| `/gesc_gaussian/algorithm_state` | `ros_esc_interfaces/msg/AlgorithmState` | existing supervisor owner |
| `/gesc_gaussian/algorithm_events` | `ros_esc_interfaces/msg/AlgorithmEvent` | existing event owners |
| `/gesc_gaussian/convergence_status` | `StampedFloat64MultiArray` | existing detector owner |
| `/gesc_gaussian/fill_requests` | `StampedFloat64MultiArray` | existing supervisor owner |
| `/gesc_gaussian/supervisor_command` | `geometry_msgs/msg/Twist` | existing supervisor owner |
| `/gesc_gaussian/recording_ready` | `std_msgs/msg/Bool` | sole `record_run` readiness owner |
| `/gesc_gaussian/stop_requested` | `std_msgs/msg/Bool` | recorder/operator stop input |
| `/odom` | `nav_msgs/msg/Odometry` | TurtleBot wheel/IMU-backed pose; sole algorithm pose input |
| `/imu` | `sensor_msgs/msg/Imu` | TurtleBot evidence/readiness heartbeat; exact live owner must be verified |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | sole existing `ros_esc` controller output |
| `/gesc_gaussian/evaluation/vicon_pose` | `geometry_msgs/msg/PoseStamped` | required selected-trial evaluation evidence; never an algorithm input |
| `/gesc_gaussian/evaluation/vicon_status` | `std_msgs/msg/String` | required identity/session/sequence/frame/occlusion/freshness evidence |

Vicon is required evidence for an accepted selected two-source trial, but it
is evaluation-only. It is required by the physical manifest and recorder
readiness/completeness contract on the two canonical evaluation topics above;
it may not be remapped, forwarded, or copied to `/odom` or any other control
input. A missing or invalid Vicon stream prevents an evidence-complete run; it
does not become an alternative localization source.

### Photoresistor extension

Preserve the existing positional CLI and legacy publication. Add named options
with these defaults:

| Option | Default | Contract |
|---|---|---|
| `--serial-port` | `/dev/ttyUSB0` for direct legacy compatibility | selected wrapper must pass a reviewed `/dev/serial/by-id/...` path |
| `--baud-rate` | `9600` | matches frozen Arduino firmware |
| `--serial-timeout-sec` | `0.50` | bounded read; no five-second shutdown stall |
| `--publish-source-cost` | `False` | selected robust launch passes `True` |
| `--source-cost-topic` | `/gesc_gaussian/source_cost` | canonical typed topic |
| `--source-name` | `rotating_photoresistor_voltage` | metadata only, no source role |
| `--calibration-file` | empty/unconfigured | selected readiness cannot pass until a validated file is supplied |
| `--source-score-enabled` | `False` | diagnostic only; counted ranking remains raw-cost-owned |

The pure helper must:

- parse exactly `v: <float>, r: <float>` with finite values;
- publish `raw_sensor_value=[V]`, `raw_cost=[-V]`, source mode physical,
  channel count one, and identical monotonic experiment timestamps on legacy
  and typed messages;
- publish a dimensionless source score only when a validated calibration file
  enables it; otherwise publish unavailable values and
  `source_score_valid=false`;
- reject malformed, nonfinite, out-of-calibrated-range, regressed, or stale
  readings without reusing the last value;
- stop its reader thread, close serial, and join within the shutdown bound; and
- expose no coordinate, lamp role, declared intensity, or Vicon field.

Broad `except:` is removed. Error counts/logs remain diagnostic; missing fresh
publication causes the existing supervisor/controller and recorder readiness
paths to fail closed.

### Pose and IMU boundary

The selected launch uses `/odom` directly for controller, supervisor, PDE
history, modified cost, Gaussian fill, and recording. It does not start the
snapshot `odometry_node`, does not select its Vicon mode, and does not create a
second odometry publisher.

TurtleBot3 bringup remains the `/odom` owner. The installed Burger parameters
use IMU in odometry. `/imu` is additionally recorded and monitored so a
missing/stale required IMU prevents or revokes recorder readiness. No IMU
integration or global localization is added to `ros_esc`.

### Recorder/readiness extension

Extend physical mode in the existing manifest/recorder to require fresh:

```text
source_cost
pose
imu
filter_output_legacy
timekeeper
algorithm_state
supervisor_command
```

Use `0.50 s` as the initial physical heartbeat-stale bound, matching existing
pose/sensor/controller watchdog defaults. Static tests must prove:

- physical source mode and finite raw cost;
- finite `/odom` pose/quaternion and valid timestamp;
- finite IMU timestamp/data under the frozen live convention;
- finite filter output;
- valid robust state and supervisor command;
- readiness cannot become true until every required topic/type/owner,
  recorder subscription, metadata input, and fresh heartbeat passes; and
- any later missing/stale heartbeat publishes readiness false and stop true.

The recorder remains the only readiness publisher. The controller remains the
only `/cmd_vel` publisher. The final shutdown sequence remains:

```text
operator Ctrl+C or emergency stop
-> recording readiness false
-> stop requested true
-> supervisor/controller zero command
-> recorded final zero on Twist, legacy command, and ControlDiagnostics
-> target descendants stop
-> rosbag finalizes
-> validate_run and SQLite integrity check
-> scoped cleanup proof
```

The operator's `Ctrl+C` ends the physical run. Counted-candidate terminal
ranking may place the algorithm in zero-command `GOAL_HOLD`, but it does not
terminate the process and no coordinate/proximity signal is used. There is no
automatic physical global-distance stop.

## Configuration defaults and selected profile

### Conservative launch defaults

The dedicated Phase 09 physical GESC+Gaussian launch has inert,
legacy-compatible defaults. The pre-existing launch remains byte-identical as
required by the shared-lab compatibility amendment:

```text
algorithm_profile=legacy
use_pde_extensions=False
enable_observability=False
observability_source_mode=physical
use_sim_time=False
supervisor_use_sim_time=False
recording_ready_required=True
known_source_count=0
extremum_classification_mode=absolute_source_score
gaussian_fill_max_fills=1
open_field_escape_assist_enabled=False
open_field_escape_approach_continuity_enabled=False
open_field_escape_interior_anchor_fallback_enabled=False
open_field_escape_interior_anchor_min_displacement_m=0.50
open_field_escape_active_fill_transit_enabled=False
open_field_escape_supervisor_owned_assist_enabled=False
recenter_after_escape=True
operating_bounds_enabled=True
controller_odom_topic=/odom
algorithm_pose_topic=/odom
gaussian_fill_pose_topic=/odom
```

The launch must not contain an automatic `pkill`, Vicon control remap,
coordinate stop, or robust-mode legacy CSV recorder. Direct launch without the
Phase 05 readiness owner cannot produce nonzero selected-profile motion.

### Frozen cumulative Phase 08 terminal profile

The new selected wrapper explicitly chooses `robust_gaussian_v1`, enables
typed observability and Phase 05 gating, uses physical time, and applies the
cumulative terminal controller profile: the v8.10/v8.11 counted-candidate
base plus the v8.12 interior-anchor fallback. The audit configuration records
`phase08_v8_12_interior_anchor_counted_open_field_v1` as its
`simulation_profile_origin`:

```text
convergence_min_fill_periods=2.0
convergence_state_gating_enabled=True
convergence_minimum_path_length_m=0.20
convergence_maximum_path_efficiency=0.50
convergence_confirmation_policy=qualified_dwell
convergence_confirmation_dwell_sec=6.0
convergence_confirmation_exit_threshold_scale=1.5
robust_search_epoch_reset_enabled=True
gaussian_fill_covariance_scale=2.5
gaussian_fill_sigma_floor_m=0.50
gaussian_fill_sigma_ceiling_m=1.25
gaussian_fill_amplitude_depth_scale=1.5
gaussian_fill_amplitude_max=6.25
gaussian_fill_exit_sigma=2.70
gaussian_fill_max_fills=1
max_fill_clusters=1
gaussian_fill_minimum_valid_samples=40
gaussian_fill_reuse_retained_samples_on_redesign=True
extremum_classification_mode=counted_candidates
known_source_count=2
candidate_cost_rotation_period_sec=3.0
candidate_cost_required_rotations=3
candidate_cost_pretrigger_rotations=6
candidate_cost_mad_scale=3.0
candidate_informed_fill_enabled=True
candidate_informed_fill_amplitude_scale=1.25
operating_bounds_enabled=False
open_field_escape_assist_enabled=True
open_field_escape_approach_continuity_enabled=True
open_field_escape_interior_anchor_fallback_enabled=True
open_field_escape_interior_anchor_min_displacement_m=0.50
open_field_escape_active_fill_transit_enabled=True
open_field_escape_supervisor_owned_assist_enabled=True
modified_cost_affine_gain=0.50
modified_cost_affine_decay_rate=0.0000005
modified_cost_affine_max_age=35.0
modified_cost_affine_direction_sign=1.0
post_recovery_guidance_enabled=False
recoverable_navigation_enabled=False
recenter_after_escape=False
stall_window_sec=3.0
minimum_radial_progress_m=0.05
goal_score_threshold=0.95
goal_score_rotation_period_sec=3.0
goal_score_required_rotations=2
goal_hold_sec=3.0
undesired_score_hold_sec=3.0
verification_max_sec=12.0
fill_design_timeout_sec=5.0
escape_max_sec=35.0
escape_exit_hold_sec=1.0
fill_avoidance_margin_m=0.10
approach_history_window_sec=0.5
stale_pose_sec=0.50
stale_sensor_sec=0.50
supervisor_state_stale_sec=0.50
supervisor_command_stale_sec=0.50
recording_ready_stale_sec=0.50
zero_command_on_shutdown=True
```

The selected physical profile therefore runs the latest v8.12 supervisor
policy. The original `outside_radius` anchor always retains priority, so the
fallback does not alter a run that already has a qualified outside-radius
history pose. It engages only when that original anchor is unavailable and a
finite odometry-history pose is at least `0.50 m` from the fill center. Legacy
and nonselected wrappers continue to inherit the shared default-off behavior.

Create the Phase 09 controller configuration from the existing physical
Directional Controller with the same wheel geometry and gains, but freeze
initial floor-motion ceilings at:

```text
set_max_vx=0.05 m/s
set_max_wz=0.30 rad/s
```

These are hard ceilings, not permission to move. Stationary and
nontranslating checks occur first under later authority. Raising either value
requires a new reviewed configuration and experiment version.

## Calibration and selected physical scenario definitions

### Calibration file state

`phase09_photoresistor_calibration.yaml` is created with
`status: uncalibrated`, `motion_ready: false`, the frozen voltage sign/unit,
schema/version fields, serial-device placeholder, and empty measurement/hash
fields. Host qualification validates the schema only; it must not fill live
values or mark calibration complete.

Calibration is step 6 of the exact M9 sequence; it may begin only after the
separate on-Pi installed-static gate, site-copy creation, retained stationary
preflight plus hash-coupled approval, and independent emergency-stop/
nontranslating final-zero rehearsal have passed. It then proceeds without base
translation:

1. record dark/ambient and room-light conditions;
2. verify serial device identity, `9600` baud, parser error rate, actual sample
   period, timestamp monotonicity, and full sensor-rotation period;
3. record each lamp alone at its selected location/settings for at least five
   complete rotations;
4. calculate the same per-rotation minimum raw cost used by the controller,
   then its median, MAD, and `3*MAD` interval;
5. calculate ambient-subtracted peak-voltage response and freeze lamp settings
   whose strong/weak response ratio is within `[3.6, 4.4]`;
6. require the strong-source raw-cost upper interval to be strictly below the
   weak-source lower interval; and
7. hash the raw calibration bag, resolved configuration, calculation output,
   and final calibration YAML before any floor trial.

Failure to achieve stable, finite, nonoverlapping response bands closes that
calibration version. Do not reinterpret simulator relative lumens as measured
physical intensity or weaken the interval rule.

### Evaluation-only selected scenarios

Both metadata files are consumed by `record_run` only. No launch/node parameter
is sourced from their `robot_starting_pose`, `sources`, coordinates, roles,
lamp settings, or environment fields.

Primary selected scenario:

```text
scenario_id: phase09_selected_primary_r1p5_a45_ratio1to4
start: (0.0, 0.0, yaw 0.0)
local lamp: (1.0606601718, 1.0606601718) m
global lamp: (3.5, 3.5) m
controller-visible source count: 2
controller-visible lamp coordinates/roles/settings: none
physical response target: calibrated weak/strong 1:4 band
stop: manual operator Ctrl+C
```

Secondary selected scenario:

```text
scenario_id: phase09_selected_secondary_r1p5_a67p5_ratio1to4
start: (0.0, 0.0, yaw 0.0)
local lamp: (0.5740251485, 1.3858192988) m
global lamp: (3.5, 3.5) m
controller-visible source count: 2
controller-visible lamp coordinates/roles/settings: none
physical response target: calibrated weak/strong 1:4 band
stop: manual operator Ctrl+C
```

The coordinates are the full-scale target geometry and evaluation metadata.
If the open field cannot safely reproduce them, stop. A scaled or relocated
layout is a new scenario version and cannot be described as the selected
reproduction without separate review.

## Milestone sequence

Work only one milestone at a time. Each milestone updates the live status with
exact commands, outcomes, skips, retained paths, hashes, and the next gate.

### M0 — Recover context and seal the pre-edit snapshot baseline

Actions:

1. reread `AGENTS.md`, this Plan, current Phase 09 status if present, Phase
   08.8 final report/handoff, terminal Phase 08 status/checkpoint, and the
   current Git/snapshot state;
2. initialize status only if absent with `tools/init_phase_status.sh 09`;
3. run `validate_phase_context.sh 09 implement` and stop if it fails;
4. inspect the mount table without reading the reserved mount path and prove
   `/home/mattb/tb3-pi` is not mounted;
5. create a UTC-named external backup directory:

   ```text
   /home/mattb/physical_TB3_files_snapshot/phase09_backups/
     <UTC>/ros2_ws_src.tar.gz
   ```

6. record a sorted inventory with relative path, type, mode, size, and symlink
   target plus a sorted SHA-256 manifest for every regular source file;
7. validate the archive listing and extract it into a bounded `mktemp -d`
   location to prove its hashes reproduce the baseline; and
8. write the Git-side baseline/backup receipt and checkpoint Phase 09.

No snapshot edit occurs before the archive, inventory, hashes, extraction
test, and receipt all pass. Failure to create or validate a recoverable backup
is a hard stop.

### M1 — Freeze the package/interface/ownership diff

Actions:

- compare current `dsim-lab` and snapshot `ros_esc`/interfaces by relative
  path and SHA-256;
- classify every planned file as byte-identical shared algorithm, physical
  packaging, physical adapter/configuration, recorder physical extension,
  unchanged legacy, or excluded simulation/generated content;
- confirm one owner for source cost, augmented cost, filter, fill,
  supervisor, `/cmd_vel`, readiness, recorder, and validator;
- confirm no selected launch path starts Vicon or the legacy CSV collector;
- write `phase_09_shared_source_manifest.tsv` and
  `phase_09_transfer_manifest.txt`; and
- checkpoint before applying source edits.

An unclassified overlap or a live-Pi/snapshot change made by another actor is
a hard stop until reviewed.

### M2 — Port shared interfaces and algorithm owners

Actions:

- add the six current typed messages and their CMake/package dependencies;
- port the exact shared algorithm files listed above;
- preserve all legacy messages/topics/configurations;
- adapt only physical `setup.py`/`package.xml` entry points and dependencies;
- prove every shared-algorithm file matches its `dsim-lab` source SHA-256;
- run interface generation, Python compilation, import, state-machine,
  controller, fill, supervisor, and legacy tests; and
- checkpoint the independently reviewable parity boundary.

Do not copy scenario-runner, Gazebo analysis, worlds, simulation packages, or
generated artifacts merely to make the directory resemble `dsim-lab`.

### M3 — Extend the physical sensor owner and isolate the selected launch

Actions:

- add the pure photoresistor parser/calibration helper and extend the existing
  node for dual legacy/typed publication and bounded shutdown;
- leave the existing physical GESC+Gaussian launch byte-identical and add a
  dedicated Phase 09 launch with the current robust owners and explicit
  physical-time/topic arguments;
- route every pose consumer to `/odom` and omit the Vicon relay;
- add the selected low-speed controller config and new selected wrapper;
- make the selected wrapper explicitly enable the v8.12 interior-anchor
  fallback while preserving the shared legacy default `False`;
- preserve every old wrapper, old launch, and old configuration byte-identical;
- exclude legacy CSV recording in selected robust mode;
- remove broad `pkill -9` behavior from the selected path;
- run `bash -n` over every existing and new Bash wrapper, resolve wrapper launch
  names/arguments statically, prove the old launch and all pre-existing
  wrappers still match their M0 hashes, and prove exactly one `/cmd_vel`
  publisher with no controller-visible coordinate/role/intensity/Vicon field;
- checkpoint the adapter/launch boundary.

### M4 — Extend Phase 05 physical readiness and shutdown evidence

Actions:

- port the sole recorder/validator/assets;
- add physical topic requirements and heartbeat validation to the existing
  manifest/recorder;
- test missing, invalid, regressed, nonfinite, and stale source/odom/IMU/filter/
  supervisor inputs;
- test readiness false and stop true on each fault;
- test SIGINT ordering, controller final zero, recorder finalization, and
  descendant cleanup with fakes only;
- verify `validate_run` still enforces final readiness false, all three final
  zero forms, sqlite3 integrity, and physical source mode; and
- checkpoint the safety/recording boundary.

No test may create a second readiness or `/cmd_vel` publisher.

### M5 — Add inert calibration and selected-scenario configuration

Actions:

- create the uncalibrated calibration template;
- create the frozen cumulative v8.12 selected-profile audit file and two
  evaluator-only metadata files;
- validate schemas, units, sign, selected geometry, source count, and strict
  separation formulas offline;
- prove the wrapper passes metadata only to `record_run`, not the launched
  controller graph;
- prove both scenarios remain blocked by uncalibrated/live-readiness fields;
- require the managed wrapper to validate the calibration document and every
  declared physical-readiness field before it reaches the serial-device check
  or starts `record_run`;
  and
- checkpoint the configuration boundary.

No physical measurement or lamp value is fabricated during this milestone.

### M6 — Host-side static/offline qualification

Run all applicable checks from an isolated build rooted under `/tmp`, not the
snapshot's `build`, `install`, or `log` directories:

```bash
PHASE09_QUAL_ROOT="$(mktemp -d /tmp/phase09_static_qual.XXXXXX)"
export PYTHONPYCACHEPREFIX="${PHASE09_QUAL_ROOT}/pycache"

timeout --signal=INT --kill-after=5s 60s \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh \
  09 implement

timeout --signal=INT --kill-after=5s 60s python3 -m compileall -q \
  /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/ros_esc/ros_esc \
  /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/turtlebot3_vehicle_nodes/turtlebot3_vehicle_nodes

timeout --signal=INT --kill-after=5s 30s python3 -c "import xml.etree.ElementTree as ET; ET.parse('/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/turtlebot3_vehicle_nodes/launch/gesc_gaussian_two_source.launch.xml')"

timeout --signal=INT --kill-after=5s 30s python3 -c "import pathlib,yaml; files=sorted(pathlib.Path('/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/turtlebot3_vehicle_nodes/config_files/gesc_gaussian').glob('*.yaml')); assert files; [yaml.safe_load(p.read_text()) for p in files]"

source /opt/ros/humble/setup.bash
timeout --signal=INT --kill-after=10s 900s colcon \
  --log-base "${PHASE09_QUAL_ROOT}/colcon_log" build \
  --base-paths /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src \
  --build-base "${PHASE09_QUAL_ROOT}/build" \
  --install-base "${PHASE09_QUAL_ROOT}/install" \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_vehicle_nodes

source "${PHASE09_QUAL_ROOT}/install/setup.bash"
timeout --signal=INT --kill-after=5s 300s python3 -m pytest -q \
  /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/ros_esc/test/test_phase09_shared_parity.py \
  /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/ros_esc/test/test_phase09_physical_recording.py \
  /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/turtlebot3_vehicle_nodes/test/test_photoresistor_adapter.py \
  /home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src/turtlebot3_vehicle_nodes/test/test_phase09_physical_launch.py

timeout --signal=INT --kill-after=5s 60s ros2 launch \
  turtlebot3_vehicle_nodes gesc_gaussian_two_source.launch.xml \
  --show-args

timeout --signal=INT --kill-after=5s 30s git diff --check
```

Also run the current ROS-independent shared regression owners against the
snapshot overlay where dependencies permit:

```text
test_state_machine.py
test_supervisor_integration.py
test_observability_contract.py
test_legacy_behavior.py
test_robust_gaussian_algorithm.py
test_escape_recenter.py
test_deferred_signal_shutdown.py
test_search_epoch_history.py
test_convergence_detector_policy.py
test_experiment_recording.py
test_recording_integration.py
```

Commands and large logs must be bounded and retained outside Git, with concise
results and exact paths recorded in the static qualification report. A
`--show-args` pass does not prove ROS parameter types; host-compatible node
construction with fake/no-device dependencies must be added where safe.
Serial, GPIO, OpenCR, servo, TurtleBot driver, and motor nodes are not
instantiated.

### M7 — Seal the recoverable no-hardware handoff

Actions:

- create after-inventory/hashes and the reviewable snapshot patch;
- compare before/after and require every changed path to be in the frozen
  manifest;
- apply the reverse patch to an extracted temporary baseline and prove it
  reconstructs the before hashes without touching the real snapshot;
- verify the external backup still matches its receipt;
- verify no simulation, analyzer, live-Pi, SSHFS, serial, ROS graph, or
  physical process was started;
- write the static qualification and Phase 09 handoff;
- run `checkpoint_phase.sh 09`, inspect all Git and external snapshot diffs,
  and commit only if the user has authorized commits; and
- report the result as either `SNAPSHOT STATIC INTEGRATION PASS — HARDWARE
  DEFERRED` or an honest failure. Never report `PHYSICAL READY`.

### M8 — Live-Pi source-transfer history and M8B follow-on

The original 51-path M8A source/configuration transfer is retained as
historical evidence in the transfer receipt. M8B adds reviewed selected-only
Vicon, stationary-preflight, calibration-evidence, recorder, validator, and
operator-entry paths to the snapshot. The M8B snapshot changes and host-side
qualification passed. The later scoped real-Pi M8B source synchronization also
passed under explicit user authorization: the verified rollback backup is
`/home/mattb/tb3-pi/phase09_backups/20260802T031409Z_m8b`, snapshot and Pi
match `345/345` regular-file hashes and `432/432` inventory entries, and the
final scoped dry run is empty. These are source-transfer results only, as
recorded in the live status and transfer receipt.

Any M8B source synchronization must repeat the M8A controls: resolve the exact
mounted source root, compare only reviewed manifest paths, stop on overlapping
Pi changes, create and verify a new UTC-scoped rollback backup before writing,
use checksum-based `rsync --dry-run --itemize-changes --files-from=...` with no
delete behavior, exclude generated/editor/runtime/Git content, transfer only
the reviewed source/configuration set, rehash every target, and require an
empty final dry run. There is no whole-home mirror, recursive delete, blind
snapshot overwrite, remote command, ROS launch, serial/GPIO access, mechanism
actuation, or motion in this transfer boundary.

The separate on-Pi build/source and installed-static gate has not run. It is
the first future commissioning action below, not evidence that can be inferred
from a host build or a host reading the SSHFS tree.

Rollback restores the exact pre-transfer files from the applicable live-Pi
backup and removes only manifest-declared additions after their names are
verified. If the backup, transfer scope, parity, or rollback evidence cannot be
proven without risk, synchronization stops and no commissioning gate begins.

### M9 — Later hardware commissioning and selected trials

Every item below remains `NOT RUN` until its retained evidence says otherwise.
The milestone requires the applicable separate user authorization and a
reviewed live-readiness checklist. Run in this exact order, stopping at the
first failure:

1. Run a separate bounded on-Pi build/source and installed-static gate with no
   ROS graph, serial device, actuator, or motion. This gate is currently
   `NOT RUN`; host-side builds do not satisfy it.
2. Create mutable calibration and primary/secondary scenario-metadata copies
   under
   `${XDG_CONFIG_HOME:-$HOME/.config}/dsim-lab/phase09`. Never commission by
   editing the installed inert templates; keep the installed selected profile
   frozen.
3. Run `gesc_gaussian_two_source_voltage.bash --stationary-preflight` while the
   site calibration remains uncalibrated, readiness remains false, and the
   selected passive timekeeper permits no base or rotating-frame actuation.
4. Review the retained stationary run and offline `PASS`, then execute
   `gesc_gaussian_two_source_voltage.bash --approve-stationary RUN_DIR
   --reviewer NAME`. Approval must consume the same metadata bytes used by the
   preflight and remain hash-coupled to that retained evidence.
5. Test the independent emergency-stop method, then perform a separately
   authorized, mechanically safe nontranslating command/final-zero rehearsal.
6. Perform the stationary rotating-photoresistor calibration, retain the real
   sqlite3 bag/calculation/configuration hashes, and freeze the accepted
   response bands. A synthetic or PDF-derived value is forbidden.
7. Run `gesc_gaussian_two_source_voltage.bash --check-only` against the
   reviewed site inputs. A pass is a configuration/static gate only; it does
   not prove the live graph, Vicon stream, final-zero path, or motion safety.
8. For the first selected primary two-source experiment, run the bare
   `gesc_gaussian_two_source_voltage.bash`, verify the assigned operator and
   observer shown by the wrapper, and type `RUN` only after all live prompts
   are true. The bare wrapper is the eventual normal primary entry point.

Every stationary or experiment invocation uses the existing
`record_run --mode physical`, immutable/hash-coupled metadata, a unique run ID,
one complete sqlite3 bag, manual operator `Ctrl+C` for physical arrival,
final-zero validation, SQLite integrity, and scoped descendant cleanup. Vicon
is required evaluation-only evidence, while wheel/IMU-backed `/odom` remains
the sole algorithm pose. A safety, ownership, identity/session/freshness,
stale-input, recording, final-zero, emergency-stop, cleanup, strict-ranking,
or one-fill failure stops progression. Failed bags are retained and never
retried under the same experiment version. The secondary selected scenario is
considered only after a fully accepted primary run and a separately reviewed
progression decision.

## Checkpoints and commit boundaries

| Boundary | Required evidence | Checkpoint | Suggested bounded commit, only when authorized |
|---|---|---|---|
| M0 baseline | archive, extraction proof, inventory, before hashes, clean scope | Phase 09 | `phase 09: record physical snapshot baseline` |
| M2 shared parity | interface build, byte parity, focused legacy/robust tests | Phase 09 | `phase 09: port shared algorithm to physical snapshot evidence` |
| M4 safety/recording | adapter/launch tests, physical heartbeat faults, Ctrl+C/final-zero fakes | Phase 09 | `phase 09: integrate physical snapshot workflow` |
| M6 static qualification | isolated build, imports, tests, XML/YAML, manifest/diff checks | Phase 09 | `phase 09: qualify physical snapshot integration` |
| M7 handoff | before/after/reverse proof, final report, inactive runtime, explicit deferrals | Phase 09 | `phase 09: close no-hardware snapshot integration` |
| M8 source transfer | read-only diff, Pi backup, scoped transfer, hashes, empty final dry run, rollback; no on-Pi command | Phase 09 continuation | separate transfer receipt commit |
| future M9 installed-static gate | bounded on-Pi build/source and installed checks; no graph/device/actuation | Phase 09 continuation | separate commissioning evidence commit |

The non-Git snapshot is never described as committed. Git commits retain its
reviewed manifests, hashes, patch, receipts, status, checkpoint, and handoff.

## Acceptance criteria for the no-hardware implementation

All must pass:

- validated backup and reproducible before manifest exist before first edit;
- every snapshot change is declared and reversible;
- shared algorithm and message sources match the current `dsim-lab` hashes;
- legacy messages/topics/configurations remain selectable, every pre-existing
  Bash wrapper and the old GESC+Gaussian launch matches its M0 SHA-256, every
  Bash wrapper passes `bash -n`, and wrapper launch arguments resolve;
- negative voltage remains the raw minimization cost in volts;
- physical typed source messages are finite, timestamped, single-channel, and
  source mode physical;
- every algorithm pose consumer uses wheel/IMU-backed `/odom`; Vicon is
  required selected-trial evaluation evidence and remains absent from control;
- required IMU is recorded/heartbeat-gated without becoming a localization
  input;
- selected profile has known source count two and exactly one fill;
- Gaussian memory persists and affine/supervisor assistance is temporary;
- direct and assisted recovery retain one final command owner;
- interior-anchor fallback is present and tested, remains default-off for
  legacy/nonselected paths, and is explicitly enabled by the selected Phase 09
  wrapper;
- no source coordinate, role, lamp setting, room dimension, global start,
  evaluator topology, or proximity stop reaches the controller graph;
- exactly one `/cmd_vel`, readiness, recorder, and validator owner exists;
- missing/stale/invalid sensor, odom, IMU, Vicon evaluation, filter,
  supervisor, or recorder evidence forces readiness false/stop/zero;
- manual SIGINT ordering and all three final-zero forms pass offline tests;
- isolated host build, interface generation, compilation, imports, selected
  tests, launch-description construction, YAML/XML, diff, and manifest checks
  pass;
- uncalibrated configuration remains motion-blocking;
- all on-Pi build, live ROS, device, calibration, and hardware tests are listed
  as unexecuted; and
- final status/handoff clearly say static snapshot integration only.

## Explicit hardware-deferred checks

These cannot pass during snapshot implementation:

- live Pi OS/ROS/Python/package versions and CPU/memory/disk capacity;
- Pi-side installed artifacts and absence of any post-sync source divergence
  at the later build boundary;
- stable serial device-by-id, dialout permissions, Arduino firmware/protocol,
  voltage range, sample rate, parser error rate, and disconnect behavior;
- rotating encoder zero, direction, full-rotation period, and sample coverage;
- `/odom` publisher, frame IDs, wheel sign/scale, timestamp, drift, and
  freshness;
- `/imu` exact topic/type/publisher, orientation convention, covariance,
  timestamp, and freshness;
- live one-owner `/cmd_vel` graph and TurtleBot command consumption;
- base and rotating-frame stop behavior;
- real `Ctrl+C` descendant ordering and bag finalization;
- independent emergency stop and operator reachability;
- lamp identity, placement, electrical settings, ambient control, response
  intervals, and 1:4 calibration;
- stationary, lifted-wheel, one-source, local-recovery, primary, and secondary
  trials; and
- required Vicon subject/segment identity, server-script hash, protocol/session,
  advancing sequence/frame, nonoccluded pose, timestamp/freshness, full run
  coverage, and strict evaluation-only isolation.

Each remains `NOT RUN`, not `PASS`, in the Phase 09 handoff.

## Stop conditions and contradiction policy

### Level A — stop immediately

- live-Pi access, transfer, serial access, ROS hardware launch, or motor/servo
  command without the corresponding explicit authorization;
- missing/invalid snapshot backup or unreviewed overlapping snapshot/Pi edits;
- cost sign/unit/topic/message semantic change;
- source, role, intensity, coordinate, Vicon/GPS, room/map, or proximity input
  entering control;
- more than one `/cmd_vel`, supervisor, recorder, readiness, validator, or
  typed-fill lifecycle owner;
- a shared algorithm source that cannot remain byte-identical without an
  objective/architecture change;
- loss of legacy selection or final-zero/readiness guarantees;
- unknown physical stop method, unavailable observer, or unsafe/open-field
  contradiction before motion; or
- a transfer/rollback target that cannot be resolved to exact files.

### Level B — bounded correction with evidence

Host-only packaging/import differences, unavailable optional dependencies,
launch syntax, physical manifest validation, injected serial testability, and
Pi resource adaptations may be corrected if they preserve the objective,
owners, interfaces, sign/units, safety, and parity. Record the amendment,
focused regression, diff, and checkpoint before continuing.

### Level C — close the experiment version honestly

A static acceptance failure closes the snapshot qualification; a later
calibration or physical acceptance failure closes that physical experiment
version. Preserve artifacts and do not weaken thresholds, retry a fixed run,
or claim readiness. A new version requires a separately reviewed plan.

## Risks and mitigations

| Risk | Mitigation/gate |
|---|---|
| Snapshot has no Git history | verified archive, before/after manifests, patch, extraction and reverse-patch proof |
| Pi may diverge after the proven M8B source sync | recheck the final manifest and stop on overlap before the on-Pi build |
| Simulation package has Pi-incompatible dependencies | physical packaging manifest excludes Gazebo/scenario/analysis dependencies while shared runtime hashes stay equal |
| `/dev/ttyUSB0` may conflict with lidar or enumerate differently | require reviewed `/dev/serial/by-id/...`; live preflight stops on collision/change |
| Current sensor rate is about 5 Hz | measure actual rate; require complete 3 s rotation windows and no stale gap before readiness |
| Wall-time/ROS-time mismatch | one monotonic experiment timestamp for legacy and typed sensor data; physical `use_sim_time=false`; regression tests |
| Wheel odometry drift | limited selected layouts, IMU-backed odometry, live calibration, no global-coordinate control claim |
| IMU can be present but stale/invalid | physical recorder heartbeat validity and controller stop through revoked readiness |
| Signal/child cleanup may differ on Pi | fake host tests, later no-motion live rehearsal, final-zero and descendant audit before floor motion |
| Physical lamp response may not match simulator ratio | measured five-rotation intervals; freeze or fail calibration; never substitute nominal lumens |
| Open field lacks autonomous collision protection | obstacle-free setup, conservative speeds, observer and independent emergency stop |
| Pi compute load may violate 0.5 s watchdogs | bounded on-Pi profiling before motion; do not relax watchdogs without a versioned Level B amendment |

## Assumptions requiring implementation-time verification

- the snapshot still has exactly the audited three packages and no external
  changes when M0 starts;
- the live Pi later uses ROS 2 Humble and compatible TurtleBot3 Burger/OpenCR
  packages;
- `/odom` remains wheel/IMU-backed and `/imu` is the correct raw IMU topic;
- the rotating-frame physical configuration completes one rotation in about
  `3.0 s` and the photoresistor provides enough valid samples for the frozen
  windows;
- the selected open field can safely reproduce the full-scale coordinates;
- a stable device-by-id exists for the Arduino without conflicting with lidar
  or OpenCR;
- the user will supply separate authorization for the on-Pi build, no-motion
  hardware checks, calibration, and motion as distinct future boundaries; and
- an independent emergency-stop method and a second observer are available
  before any floor trial.

If any assumption fails, update the live status and apply the stop policy; do
not silently infer a replacement.

## Plan completion statement

The original Plan authorized local snapshot edits only. Later dated amendments
record the separately authorized M8A transfer and the approved M8B
snapshot/host-side implementation. They do not create standing authorization
for another Pi write or any on-Pi command. At this continuation boundary, M8B
snapshot/host qualification and the reviewed real-Pi M8B source synchronization
have passed, while the on-Pi build/installed-static gate, ROS graph,
serial/GPIO access, Vicon commissioning, calibration, lamps, mechanisms,
emergency-stop rehearsal, and motion all remain `NOT RUN`. Physical arrival
remains manual operator `Ctrl+C`, and the broad Phase 08 failure and nonclaims
remain unchanged.

### M8C lab-SOP one-command simplification amendment — 2026-08-03

The user supplied the laboratory Vicon SOP and the actual unchanged Windows
`vicon-tracker-server.py`, then explicitly corrected the M8B commissioning
model. The selected experiment is not to require a separate on-Pi build step,
site configuration copies, calibration approval, a stationary-preflight
review, operator/observer attestation, subject/segment entry, a server-file
SHA-256, a handoff approval, or a `PHYSICAL READY` tag before motion. The
selected Bash wrapper itself owns the three-package build and workspace source.
After the ordinary room/Vicon/TurtleBot setup in the lab SOP, any operator must
be able to start the selected experiment with the bare wrapper and stop it with
`Ctrl+C`.

This explicit amendment supersedes the M8B/M9 manual-authorization sequence and
the matching motion-blocking acceptance criteria. It authorizes the bounded
snapshot implementation, host qualification, and backed-up source-only SSHFS
synchronization needed to implement that operator workflow. It does not ask
Codex to start a ROS graph, access serial/GPIO, illuminate lamps, actuate the
sensor frame, or move the robot during this implementation pass.

The supplied server is the existing laboratory protocol:

- it binds UDP `192.168.1.6:12346` and waits for one ordinary client greeting;
- it selects Tracker's first subject and uses that same name as the segment;
- it sends native `struct.pack('7f')` packets containing millimetre xyz and an
  xyzw quaternion at approximately 10 Hz; and
- it contains no identity, segment, sequence, Tracker-frame, occlusion, JSON,
  metadata, or hash fields.

Accordingly, M8C shall leave the supplied server and all historical
Vicon/odometry sources byte-identical, remove the incompatible Phase-09 JSON
server/client protocol from the selected path, and launch the existing
`odometry_node --odom_method vicon` client on an evaluation-only
`nav_msgs/msg/Odometry` topic. Wheel/IMU-backed `/odom` remains the sole pose
used by the controller, supervisor, PDE/history, modified cost, Gaussian-fill,
escape, ranking, and stopping logic. The Vicon topic is recorded and displayed
for trajectory evaluation only.

The selected bare wrapper shall:

1. default to the primary two-source scenario and `/dev/ttyUSB0`;
2. build exactly `ros_esc_interfaces`, `ros_esc`, and
   `turtlebot3_vehicle_nodes`, then source `install/setup.bash`;
3. start `pigpiod` through `sudo` only when the daemon is not already running;
4. require no typed confirmation or separately edited readiness/calibration
   artifact;
5. start the sole `ros_esc record_run` owner, which opens the sqlite3 rosbag
   before its automatic ROS/data-plane startup synchronization releases the
   selected graph;
6. stream the managed child output and one-second diagnostics in the same
   terminal; and
7. use ordinary `Ctrl+C` for readiness false, stop request, final-zero dwell,
   rosbag finalization, offline completeness reporting, and scoped cleanup.

The automatic recorder/graph sequencing is not a user authorization gate and
requires no separate command or retained approval. It waits only for actual
control dependencies before sensor rotation/base readiness begins. Vicon is
launched, recorded, and shown in terminal diagnostics but is never a startup or
runtime motion heartbeat: missing or interrupted Vicon is retained as visibly
incomplete evaluation evidence rather than being allowed to block, enter, or
steer the algorithm. Algorithm-critical freshness and final-zero protections
remain automatic.

Uncalibrated physical voltage remains usable as the algorithm's raw input with
the established `raw_cost = -voltage` convention. Calibration and normalized
source score remain optional future analysis features, not prerequisites for
the counted-candidate v8.12 two-source controller. The fixed speed ceilings,
one `/cmd_vel` owner, one recorder/validator owner, source/role/coordinate
isolation, selected v8.12 parameters, and every historical Bash/launch/config
selection remain unchanged.

M8C acceptance requires:

- an internal source-preservation check that the attached
  `vicon-tracker-server.py` remains unchanged (never an operator key or runtime
  input);
- a wire-contract regression proving the selected client consumes the existing
  seven-float server format without operator identity/hash inputs;
- a bare-wrapper regression proving build-before-source, no typed/manual
  commissioning prompt, default `/dev/ttyUSB0`, automatic `pigpiod` handling,
  and exactly one managed recorder/launch path;
- recording/validation tests for raw uncalibrated physical cost, separate
  `/odom` and evaluation-only Vicon odometry, console diagnostics, Ctrl+C,
  final zero, sqlite3 integrity, and retained run artifacts;
- the focused Phase 09, shared recording/core, Bash/XML/YAML/Python, selected
  launch, and legacy M0 hash regressions; and
- a fresh snapshot backup, reviewed source-only Pi backup/transfer, exact
  post-transfer parity, updated status/handoff/operator directions, and a clean
  repository closeout.

### M8D familiar runtime CSV export amendment — 2026-08-03

<!-- MBuck 2026-08-03: Add familiar post-run CSV artifacts without reviving the historical live CSV collector or adding a second recorder. -->

The user additionally requires the selected GESC+Gaussian two-source run to
leave the familiar CSV files in the same retained runtime data directory as its
bag and validation evidence. M8D extends the existing `validate_run` owner so
that, after the sole sqlite3 rosbag has finalized, validation reads that bag and
atomically materializes the CSV views. It does not start a live CSV collector,
create a second recorder, change any historical wrapper, or make CSV files an
independent source of truth.

The selected wrapper run root shall contain these headerless familiar files:

| File | Bag source and columns |
|---|---|
| `encoder.csv` | `encoder`: `[timestamp, angle]` |
| `cost_value.csv` | `augmented_cost_legacy` (`/cost_modified`): `[timestamp, augmented_cost]` |
| `filter_value.csv` | `filter_output_legacy`: timestamp plus exactly two values |
| `control_value.csv` | `command_array_final`: timestamp plus exactly six values |
| `odometry.csv` | evaluation-only Vicon odometry in the legacy `[timestamp, x, y, z, qw, qx, qy, qz]` layout |

M8D also retains algorithm-specific evidence beside those files:

- `raw_cost_value.csv` records the legacy raw-cost view with
  `raw_cost = -voltage`;
- `algorithm_odometry.csv` records the algorithm's `/odom` pose independently
  of evaluation-only Vicon; and
- `legacy_csv_manifest.json` records resolved aliases/topics, semantics, row
  counts, file sizes, SHA-256 values, and bounded export errors.

Export is idempotent and per-file atomic: repeated final validation replaces
the derived files rather than appending duplicate rows. Final validation now
requires a complete export and may fail the run's completeness result when a
required input is absent or malformed. Read-only/dry validation deliberately
does not write CSVs and emits an explicit warning. The familiar files are
column-compatible with the legacy low-level plotting reader, but the old
one-level `Test_*` browser does not automatically discover this selected
wrapper's nested dated run root; operators may consume a run directory
directly without changing or misleading the legacy browser.

The bounded source change is two replacements
(`validate_run.py` and `test_phase09_physical_recording.py`) plus one new owner
module (`legacy_csv_export.py`). Pre-transfer recovery copies are retained at
`/home/mattb/physical_TB3_files_snapshot/phase09_backups/20260804T023735Z_m8d_legacy_csv_export`
and
`/home/mattb/tb3-pi/phase09_backups/20260804T023735Z_m8d_legacy_csv_export`.
The reviewed SSHFS synchronization must transfer only those three paths with no
delete behavior and finish with exact snapshot/Pi source parity.

M8D acceptance requires focused source and installed-overlay recording tests,
the full five-file Phase 09 regression set, functional `ros_esc` and vehicle
node regressions with inherited package-wide style meta-tests reported
separately, a clean isolated three-package build, mounted-source revalidation,
and exact full-tree hash/inventory parity with no generated caches or symlinks.
These are static/source-transfer gates only. No on-Pi build/source, Vicon or
calibration session, safety rehearsal, serial/GPIO access, actuation, or motion
is authorized or claimed by this amendment.

### M8E real-Pi runtime-repair amendment — 2026-08-04

<!-- MBuck 2026-08-04: Convert the first real-Pi startup failure into a bounded, legacy-preserving runtime repair and nonlaunching on-Pi qualification. -->

The user subsequently authorized the reviewed snapshot changes on the mounted
Pi, a human-operated `--check-only`, package-manager repair, and the normal
physical experiment workflow. M8E records the bounded correction required by
the first bare-wrapper attempt; it does not reopen or retune the cumulative
v8.12 algorithm.

The first attempt must remain failed commissioning evidence. It started the
managed recorder but never reached readiness because the established
`~/turtlebot3_ws` underlay was absent from the wrapper environment and selected
installed Python was stale. Preserve the run directory and its no-motion
shutdown evidence. Do not relabel it as a selected experiment.

M8E implementation shall:

1. recover both snapshot and Pi source to timestamped backups and move, rather
   than destroy, the stale selected build/install package directories;
2. source `/opt/ros/humble`, then the established Pi TurtleBot3 underlay,
   before the selected workspace build;
3. build exactly `ros_esc_interfaces`, `ros_esc`, and
   `turtlebot3_vehicle_nodes` with `--symlink-install`;
4. resolve the wrapper evidence path before changing directory;
5. construct the selected vehicle and complete experiment launch descriptions
   before recorder ownership;
6. prove byte-for-byte installed Python/source parity before hardware access;
7. verify distinct readable/writable photoresistor and OpenCR character
   devices automatically inside the wrapper;
8. add a selected-only no-lidar base helper because `/scan` is outside the
   selected open-field algorithm and LDS-02 otherwise competes with the
   historical photoresistor `/dev/ttyUSB0`; retain all historical launch files
   byte-for-byte;
9. restore the exact historical sound-profile source module already required
   by the pre-existing package entry point and launch; and
10. keep normal operation as one bare wrapper with no new operator
    authorization file, typed confirmation, or repeated check-only ritual.

M8E acceptance requires a clean host build, selected launch construction,
focused wrapper/launch/legacy tests, mounted snapshot/Pi full-tree parity, a
human-operated on-Pi clean build, installed-source parity, and a nonlaunching
`--check-only` result. `--check-only` may inspect device type and permissions
but must not open serial, start pigpio, connect Vicon, create a ROS graph, start
the recorder, or command motion.

The accepted M8E result is `345/345` source hashes, `433/433` inventory entries,
three on-Pi `colcon_build.rc=0` results, and installed Python parity
`ros_esc=63`, `turtlebot3_vehicle_nodes=21`. The final seal and validation are:

```text
/home/mattb/physical_TB3_files_snapshot/phase09_backups/
  20260804T234034Z_m8e_post_runtime_repair
docs/codex/gesc_gaussian/validation/phase_09_pi_runtime_repair.md
```

M8E does not claim a live photoresistor sample, `/odom`, Vicon, servo/motor,
recorder/final-zero, CSV, or physical search result. Before the first real run,
correct the Pi's approximately seven-hour absolute clock error once and verify
time against the operator computer. After that OS correction, the next planned
action is the ordinary lab SOP and bare selected wrapper; the passing
check-only does not become a per-run gate.
