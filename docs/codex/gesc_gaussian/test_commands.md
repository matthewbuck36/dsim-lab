# GESC Gaussian Build and Test Commands

All commands assume the repository root
`/home/mattb/dsim-lab` unless a `cd` is shown. Physical hardware must remain
disconnected/uncommanded through Phase 08.

## Phase 00 commands run

### Context validator

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 00 implement
```

Result:

```text
Phase 00 implement context is complete.
```

### Initial repository status

```bash
git status --short --branch
```

Result before Phase 00 edits:

```text
## feature/gesc-gaussian-robustness-v1
 M ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash
?? DSIM_GESC_Gaussian_Codex_Implementation_Package/
?? docs/
```

### Package discovery

Use a temporary colcon log path so discovery does not create repository logs:

```bash
source /opt/ros/humble/setup.bash
COLCON_LOG_PATH=/tmp/dsim_phase00_colcon_log \
  colcon list --base-paths ros2_ws/src
```

Result:

```text
ros_esc                         ros2_ws/src/ros_esc                         (ros.ament_python)
ros_esc_interfaces              ros2_ws/src/ros_esc_interfaces              (ros.ament_cmake)
turtlebot3_rotating_sensor      ros2_ws/src/turtlebot3_rotating_sensor      (ros.ament_cmake)
```

### Installed executable and interface discovery

```bash
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
ros2 pkg executables ros_esc | sort
ros2 interface list | rg '^    ros_esc_interfaces/msg/'
```

Result: all 13 console executables and all five custom messages listed in
`repo_audit.md` were present in the existing install tree.

### Shell syntax

```bash
bash -n \
  ros2_ws/src/turtlebot3_rotating_sensor/bash_scripts/gradient_methods/gesc_gaussian_full_rotation_voltage.bash
```

Result: passed with no output.

### Python, JSON, and XML syntax

This command parses source without importing nodes or writing bytecode:

```bash
python3 -B - <<'PY'
from pathlib import Path
import ast
import json
import xml.etree.ElementTree as ET

roots = [
    Path("ros2_ws/src/ros_esc"),
    Path("ros2_ws/src/turtlebot3_rotating_sensor/launch"),
]
py_files = [
    path
    for root in roots
    for path in root.rglob("*.py")
    if "__pycache__" not in path.parts
]

for path in py_files:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
for path in Path("ros2_ws/src").rglob("*.json"):
    json.loads(path.read_text(encoding="utf-8"))
for path in Path("ros2_ws/src").rglob("*.xml"):
    ET.parse(path)

print(f"AST syntax OK: {len(py_files)} Python files")
print(f"JSON syntax OK: {sum(1 for _ in Path('ros2_ws/src').rglob('*.json'))} files")
print(f"XML syntax OK: {sum(1 for _ in Path('ros2_ws/src').rglob('*.xml'))} files")
PY
```

Result:

```text
AST syntax OK: 61 Python files
JSON syntax OK: 62 files
XML syntax OK: 5 files
```

### Stored test-result inspection

The current test results were inspected, not regenerated:

```bash
source /opt/ros/humble/setup.bash
COLCON_LOG_PATH=/tmp/dsim_phase00_colcon_log \
  colcon test-result \
    --test-result-base ros2_ws/build \
    --all \
    --verbose
```

Result:

```text
Summary: 885 tests, 0 errors, 875 failures, 1 skipped
```

Dominant failures:

- pre-existing `ros_esc` flake8 and pep257 failures;
- 714 `turtlebot3_rotating_sensor` flake8 failures;
- 153 of 154 `turtlebot3_rotating_sensor` pep257 cases failing;
- three `ros_esc_interfaces` lint-cmake failures.

The stored XML also shows passing XML checks. This is baseline evidence, not a
Phase 00 regression.

### Rosbag capability discovery

```bash
source /opt/ros/humble/setup.bash
ros2 bag list storage
python3 -B -c 'import rosbag2_py; print(rosbag2_py.get_registered_writers())'
```

Result: sqlite3 is available and `rosbag2_py` imports. MCAP is not registered.

## Commands intentionally not run in Phase 00

No build, test execution, launch, Gazebo simulation, or hardware command was
run during Phase 00 implementation. The six changed files are Markdown only,
and the prompt prohibits modifying existing generated build/install/log
directories.

The saved Phase 00 plan records that this build passed during planning:

```bash
source /opt/ros/humble/setup.bash
colcon build --base-paths ros2_ws/src \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
```

Phase 00 implementation verified its source/configuration inputs and inspected
the resulting stored tests without rewriting generated artifacts.

## Repository-standard package commands for later phases

The active wrapper builds from the workspace root. Later source phases should
use:

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
```

To isolate a later phase's test results from older stored results:

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose
```

When only one package changes, narrow both commands with
`--packages-select <package>`.

Do not treat the legacy lint total as newly introduced failure. Later handoffs
must report:

1. focused new tests separately;
2. package test command results;
3. whether failures are new or match the Phase 00 baseline.

## Focused safe checks for Phase 01

The Phase 01 plan should add non-hardware tests for:

- generated typed-message import and serialization;
- cost breakdown field validity and unavailable-value flags;
- legacy `/cost_modified` numerical equivalence;
- legacy `/cost_bias` layout preservation;
- filter diagnostics matching the existing filter output/state;
- controller pre/post-saturation diagnostics with unchanged post-saturation
  command;
- structured convergence/fill event emission;
- launch argument parsing with legacy observability disabled/enabled profiles.

Focused invocation after the Phase 01 plan confirms this handoff's test paths:

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
python3 -m pytest -q \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
```

Phase 01 must use the exact focused test files above unless its saved Plan
stops and documents a repository contradiction. Tests must follow existing
pytest/ament conventions and must not require Gazebo or physical hardware.

## Phase documentation checks

After Phase 00 files exist:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_required_docs.sh
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 01 plan
git diff --check
git status --short --branch
```

These are the required final Phase 00 checks.

## Phase 02 commands run

### Context validation

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 02 implement
```

Result: `Phase 02 implement context is complete.`

### Build

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
COLCON_LOG_PATH=/tmp/dsim_phase02_build_log \
  colcon build --packages-select \
    ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
```

Result: all three packages finished successfully.

### Focused unit and ROS integration tests

```bash
python3 -m pytest -q \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
```

Result: `44 passed`. No Gazebo or physical hardware was used. Coverage includes
all logical transitions and weights, high/low score dwell, timeouts, latches,
request/result correlation, source-score endpoints, raw acquisition with zero
raw weight, one-pass cost decomposition, command arbitration/watchdogs, and
legacy numerical equivalence.

### Launch and generated-interface checks

```bash
ros2 interface show ros_esc_interfaces/msg/AlgorithmState
ros2 interface show ros_esc_interfaces/msg/AlgorithmEvent
ros2 interface show ros_esc_interfaces/msg/CostBreakdown
ros2 interface show ros_esc_interfaces/msg/ControlDiagnostics
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
  algorithm_profile:=robust_gaussian_v1 \
  use_pde_extensions:=True \
  --show-args
```

Result: both profiles parse; the default remains `algorithm_profile=legacy`
and all Phase 02 topics/timers/watchdog arguments are exposed.

### Repository-standard package tests

```bash
COLCON_LOG_PATH=/tmp/dsim_phase02_test_log \
  colcon test --packages-select \
    ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose
```

Result: `929 tests, 0 errors, 875 failures, 1 skipped`. The failing-test
count is unchanged from the Phase 00/01 baseline. The 44 Phase 02/retained
focused behavior tests pass; the remaining failures are the existing flake8,
pep257, and lint-cmake debt.

## Phase 03 commands run

### Context and pre-edit baseline

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 03 implement
```

Result: `Phase 03 implement context is complete.`

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
source install/setup.bash
python3 -m pytest -q \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
```

Pre-edit result: `44 passed in 1.03s`.

### Build

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
COLCON_LOG_PATH=/tmp/dsim_phase03_build_log \
  colcon build --packages-select \
    ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
```

Result: all three packages finished successfully.

### Focused deterministic and integration tests

```bash
python3 -m pytest -q \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
```

Result: `65 passed in 2.40s`. This includes all 13 specification categories,
the three required synthetic claims, exact stable-weight/escalation fixtures,
sample filtering and synchronization, immutable registry revisions, robust
owner merge publication, anisotropic modified-cost replacement, supervisor
cluster accounting, launch defaults, and retained legacy numerical behavior.

### Generated interfaces and launch parsing

```bash
ros2 interface show ros_esc_interfaces/msg/GaussianFill
ros2 interface show ros_esc_interfaces/msg/AlgorithmEvent
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
  algorithm_profile:=robust_gaussian_v1 \
  use_pde_extensions:=True \
  --show-args
```

Result: both interfaces include the Phase 03 lifecycle fields/constants; both
profiles parse and expose all robust estimator/designer/registry defaults. The
source launch contract contains one Gaussian owner, one modified-cost owner,
one supervisor, and one controller/`/cmd_vel` owner.

### Repository-standard package tests

```bash
COLCON_LOG_PATH=/tmp/dsim_phase03_test_log \
  colcon test --packages-select \
    ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose
```

Result: `950 tests, 0 errors, 875 failures, 1 skipped`. The failing count is
unchanged from the Phase 00–02 baseline. Phase 03 adds 21 passing focused tests
over the Phase 02 total; remaining failures are the existing flake8, pep257,
and lint-cmake debt. No Gazebo motion or physical hardware was run.

### Final documentation and repository checks

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_required_docs.sh
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 04 plan
git diff --check
```

Result: required Phase 00 documents exist, the Phase 04 planning context is
complete, and `git diff --check` passes with no output.

## Phase 04 commands run

### Context and pre-edit baseline

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 04 implement
```

Result: `Phase 04 implement context is complete.` Branch and HEAD matched the
saved plan (`feature/gesc-gaussian-robustness-v1`, `8789693a82a6771eefb99b77ef3af95e3a0f0bca`),
and no planned file overlapped the pre-existing user wrapper modification.

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
source install/setup.bash
python3 -m pytest -q \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
```

Pre-edit result: `65 passed in 2.29s`.

### Build and focused suite

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
COLCON_LOG_PATH=/tmp/dsim_phase04_build_log \
  colcon build --packages-select \
    ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
```

Result: all three packages finished successfully.

```bash
python3 -m pytest -q \
  src/ros_esc/test/test_escape_recenter.py \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
```

Result: `91 passed in 3.11s`. This includes pure escape, exact rolling
progress, stall and one targeted redesign, assisted direction/revision,
wall/fill rejection, recenter command/completion, controller arbitration and
saturation, bounds/stop failsafe, and shutdown-zero unit coverage.

### Generated interfaces and launch parsing

```bash
ros2 interface show ros_esc_interfaces/msg/AlgorithmState
ros2 interface show ros_esc_interfaces/msg/AlgorithmEvent
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
  algorithm_profile:=robust_gaussian_v1 \
  use_pde_extensions:=True \
  --show-args
```

Result: both interfaces resolve, both profiles parse, and the robust launch
lists every Phase 04 argument. Parsing alone did not detect the runtime ROS
parameter-type contradiction described below.

### Repository-standard package tests

```bash
COLCON_LOG_PATH=/tmp/dsim_phase04_test_log \
  colcon test --packages-select \
    ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose
```

Result: `976 tests, 0 errors, 875 failures, 1 skipped`. The failure count is
unchanged from the Phase 00-03 baseline. Phase 04 adds 26 passing focused tests
over the Phase 03 total; the 875 failures remain the documented flake8,
pep257, and lint-cmake debt.

### Required visible Gazebo smoke: blocked

The exact saved-plan launch was run visibly on `DISPLAY=:0`. Gazebo, the robot,
ros2_control, joint-state broadcaster, and velocity controller started, but
the robust Gaussian fill node exited before the smoke gate:

```text
rclpy.exceptions.InvalidParameterTypeException:
Trying to set parameter 'center_cost_percentile' to '10' of type 'INTEGER',
expecting type 'DOUBLE'
```

The current launch defaults are lexical integers `10` and `80`, while the
Phase 03 fill owner declares both percentile parameters as doubles. The saved
Phase 04 plan did not include this runtime correction.

On the required controlled SIGINT shutdown, the controller and supervisor
both attempted their zero-command publish after the ROS context was invalid:

```text
rclpy._rclpy_pybind11.RCLError:
Failed to publish: publisher's context is invalid, at ./src/rcl/publisher.c:389
```

Both processes exited with code 1. This directly contradicts the saved plan's
claim that the existing controller shutdown-zero path could be reused without
editing `controller_node_script.py`. Per the prompt's stop rule, no unplanned
controller signal/shutdown redesign or launch-type repair was made. No
physical hardware was run.

### Read-only shutdown-sequencing diagnosis

An isolated local ROS probe reproduced the existing default sequence:

```text
rclpy.init() + SIGINT
caught=KeyboardInterrupt context_ok=False
publish_after_signal=RCLError: Failed to publish: publisher's context is invalid
```

Disabling rclpy's signal handlers by itself did not make `rclpy.spin()` return.
A bounded `SingleThreadedExecutor.spin_once(timeout_sec=0.05)` loop with
`SignalHandlerOptions.NO` did preserve the required order:

```text
caught=KeyboardInterrupt context_ok=True
publish_after_signal=success
```

This establishes that a clean final zero requires changing process-level spin
and shutdown sequencing in both the supervisor and the final controller. The
supervisor is an approved Phase 04 owner, but
`controller_node/controller_node_script.py` is explicitly excluded by the
saved plan, so no in-plan source resolution exists.

### Amendment 1 repair and final Phase 04 validation

The user amended the saved plan on 2026-07-21 to authorize float-typed launch
literals and signal-safe controller/supervisor process sequencing. The blocked
results above are retained as the historical reason for the amendment.

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 04 implement
```

Result: `Phase 04 implement context is complete.`

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon --log-base /tmp/dsim_phase04_amend_log build \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor \
  --build-base /tmp/dsim_phase04_amend_build \
  --install-base /tmp/dsim_phase04_amend_install
source /tmp/dsim_phase04_amend_install/setup.bash
```

Result: all three packages finished successfully.

```bash
python3 -m pytest -q \
  src/ros_esc/test/test_escape_recenter.py \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py
```

Result: `93 passed in 3.12s`. The two additional passing cases cover
controller and supervisor SIGINT cleanup order. Launch-contract coverage now
requires percentile defaults `10.0` and `80.0`.

```bash
ros2 interface show ros_esc_interfaces/msg/AlgorithmState
ros2 interface show ros_esc_interfaces/msg/AlgorithmEvent
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args
ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml \
  algorithm_profile:=robust_gaussian_v1 \
  use_pde_extensions:=True \
  --show-args
```

Result: both interfaces resolve, both launch profiles parse, and robust launch
defaults now report `10.0` and `80.0` for the two percentile parameters.

The saved-plan visible Gazebo command was rerun with the isolated install.
The complete robust graph started, including `gaussian_fill`,
`gesc_gaussian_supervisor`, and `custom_controller`. One-shot samples from
`/gesc_gaussian/algorithm_state`, `/gesc_gaussian/control_diagnostics`, and
`/cmd_vel` were finite and valid. Controlled SIGINT produced clean exits for
every ROS process with no `RCLError` or invalid-context publish. Gazebo Classic
itself returned its normal launch-interrupt code 255. The launch log is:

```text
/home/mattb/.ros/log/2026-07-21-15-19-00-809176-ubuntu-ssd-61214/launch.log
```

```bash
colcon --log-base /tmp/dsim_phase04_amend_test_log test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor \
  --build-base /tmp/dsim_phase04_amend_build \
  --install-base /tmp/dsim_phase04_amend_install
colcon test-result \
  --test-result-base /tmp/dsim_phase04_amend_build \
  --all --verbose
```

Result: `978 tests, 0 errors, 875 failures, 1 skipped`. The failure count is
unchanged; remaining failures are the documented repository-wide flake8,
pep257, and lint-cmake baseline. No physical hardware was run.

## Phase 05 commands run (blocked implementation)

`validate_phase_context.sh 05 implement` passed. The retained current-source
suite passed with `93 passed in 3.33s`. An isolated `/tmp` Humble probe proved
that an explicitly named topic appearing after recorder startup is discovered,
that `/rosbag2_recorder` is graph-visible as its subscriber, and that sqlite3
finalizes readably.

The partial implementation built all three packages and its focused suite
reported `108 passed, 1 skipped in 3.34s`. The skip is the environment-gated
visible Gazebo test; its exact command was then run directly three times with
retained run directories.

The final clean run is:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/2026-07-21/
20260721T230813124669Z_simulation_phase05-short-recording_1e5e6063
```

It passes every required topic/type/count, sqlite3 readability, source
semantics, parameter snapshot, coverage, final readiness false, and all three
post-stop final-zero checks. It fails the approved 50 ms typed-stamp gate due
wall/simulation clock mixing and 0.1-second regressions, and the clean-console
gate because existing `pde_cost_history_node` exits with code 245. Exact
evidence and required plan decisions are in `phase_05_handoff.md`. No physical
hardware was run.

### Amendment 1 completion

The user authorized the saved-plan amendment documented in
`phase_05_plan.md`. After applying the bounded clock, tolerance, readiness,
PDE shutdown, publisher-ownership, parameter-snapshot, and descendant-cleanup
corrections, the focused suite passed:

```text
113 passed, 1 skipped in 3.33s
```

The skip is the environment-gated visible Gazebo pytest. Its exact command was
run directly and produced this accepted artifact:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/2026-07-21/
20260721T232824094290Z_simulation_phase05-short-recording_92bb8be7
```

`completeness.json` reports `passed: true`, with zero failures and warnings.
All 19 required topics have messages. Target and rosbag exit codes are zero,
all three final-command representations contain a post-stop zero, and 21 of
23 nodes supplied exact parameter values/types. The two optional spawner
snapshot failures were recorded after those short-lived nodes exited. The
post-run process and ROS graph checks were empty. No physical hardware ran.

The repository-standard build passed for all three packages. The standard
package test result was:

```text
Summary: 999 tests, 0 errors, 875 failures, 2 skipped
```

The 875 failures are the same documented repository-wide flake8, pep257, and
lint-cmake baseline count from Phases 00-04. The functional `ros_esc` result
was `113 passed, 2 skipped`; the second skip is the normal package-run skip
accounting. Python compilation and `git diff --check` passed. The focused
pytest process printed two non-failing rclpy `Destroyable` teardown notices
after its result; they did not occur in the accepted recording console.

## Phase 05.5 commands run

### Build and focused Phase 00-05 suite

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon --log-base /tmp/dsim_phase055_build_log build \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash
python3 -m pytest -q \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_escape_recenter.py \
  src/ros_esc/test/test_experiment_recording.py \
  src/ros_esc/test/test_recording_integration.py
```

Result: build passed for all three packages; focused result was
`113 passed, 1 skipped in 3.93s`. The skip is the environment-gated visible
Gazebo pytest.

### Accepted Phase 05 bag revalidation

```bash
ros2 run ros_esc validate_run \
  /home/mattb/Experiments/GESC-Gaussian/runs/2026-07-21/20260721T232824094290Z_simulation_phase05-short-recording_92bb8be7
```

Result: `passed: true`, with no failures or warnings.

### Repository-standard package baseline

```bash
colcon --log-base /tmp/dsim_phase055_test_log test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --all --verbose
```

Result: `999 tests, 0 errors, 875 failures, 2 skipped`. The baseline stayed
constant; failures remain inherited flake8, pep257, and lint-cmake debt.

### Workflow/document validation

The final Phase 05.5 validation checked every Phase 06-10 prompt for its saved
plan path, all five Phase 00 audit files, the knowledge bridge, prior handoffs,
durable Plan output, and Level A/B/C policy; checked Phase 06's exact Phase 05
recorder/launch reuse constraints; ran the Phase 06 Plan context validator;
checked required paths and relative Markdown links; ran shell syntax and
recording-package Python compilation; checked trailing whitespace; and ran
`git diff --check`.

Result: all passed.

## Phase 06 commands run

### Context, ownership, and pre-edit baseline

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh \
  06 implement

source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
python3 -m pytest -q \
  ros2_ws/src/ros_esc/test/test_state_machine.py \
  ros2_ws/src/ros_esc/test/test_supervisor_integration.py \
  ros2_ws/src/ros_esc/test/test_observability_contract.py \
  ros2_ws/src/ros_esc/test/test_legacy_behavior.py \
  ros2_ws/src/ros_esc/test/test_robust_gaussian_algorithm.py \
  ros2_ws/src/ros_esc/test/test_escape_recenter.py \
  ros2_ws/src/ros_esc/test/test_experiment_recording.py \
  ros2_ws/src/ros_esc/test/test_recording_integration.py
```

The context validator passed. The focused pre-edit baseline was
`113 passed, 1 skipped in 3.74s`. Repository search confirmed there was no
active GESC scenario/matrix owner to extend; the only similarly named runners
are retired Heavy-Ball artifacts. `gazebo --help` and `gzserver --help`
confirmed `--seed` support. No deterministic Gaussian or delay owner was
present.

### Build and focused suite

```bash
source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
colcon --log-base /tmp/dsim_phase06_commit_build build \
  --base-paths ros2_ws/src \
  --build-base ros2_ws/build \
  --install-base ros2_ws/install \
  --packages-select \
    ros_esc_interfaces ros_esc turtlebot3_rotating_sensor

python3 -m pytest -q -rs \
  ros2_ws/src/ros_esc/test/test_scenario_schema.py \
  ros2_ws/src/ros_esc/test/test_scenario_runner.py \
  ros2_ws/src/ros_esc/test/test_experiment_recording.py \
  ros2_ws/src/ros_esc/test/test_recording_integration.py \
  ros2_ws/src/ros_esc/test/test_state_machine.py \
  ros2_ws/src/ros_esc/test/test_supervisor_integration.py \
  ros2_ws/src/ros_esc/test/test_observability_contract.py \
  ros2_ws/src/ros_esc/test/test_legacy_behavior.py \
  ros2_ws/src/ros_esc/test/test_robust_gaussian_algorithm.py \
  ros2_ws/src/ros_esc/test/test_escape_recenter.py
```

Build result: all three packages passed. Final focused result:
`143 passed, 2 skipped in 3.77s`. The skips were:

- `RUN_GESC_PHASE06_GAZEBO_E2E=1` was not set in the ordinary focused pass;
  that exact test was run separately and passed below.
- `DSIM_RUN_GAZEBO_RECORDING_TEST=1` was not set, so the older visible Phase 05
  smoke remained skipped.

The two new Phase 06 test modules contribute 29 ordinary tests plus one
environment-gated end-to-end test. They cover strict schema parsing, ordered
matrix expansion, deterministic keys/seeds, unsupported dimensions, metadata
and argv identity, no-shell composition, unique IDs, UTC-date-independent
lookup, Uniform-noise repeatability, cleanup scoping, failure retention,
stop-on-cleanup-failure, outcome separation, summaries, and dry runs.

### Installed dry runs and launch interface

```bash
ros2 run ros_esc run_scenario \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase06_smoke.yaml \
  --operator codex-automated-test \
  --dry-run

ros2 run ros_esc run_scenario \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase06_catalog.yaml \
  --operator codex-automated-test \
  --dry-run

ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args
```

Results:

- smoke: 2 resolved runs, 0 unsupported;
- catalog: 26 resolved executable-unverified runs, 7 unsupported records;
- direct launch defaults remained `gazebo_gui=True`,
  `gazebo_use_random_seed=False`, and `gazebo_random_seed=0`.

### Recorded headless robust and legacy smoke

```bash
RUN_GESC_PHASE06_GAZEBO_E2E=1 python3 -m pytest -q -s \
  ros2_ws/src/ros_esc/test/test_scenario_runner.py::\
test_recorded_short_headless_end_to_end
```

Result: `1 passed in 207.60s`. Both profiles ran serially through the existing
`gazebo.launch.xml`, `record_run`, manifest, and validator. Both
`completeness.json` files passed and both cleanup reports had no new nodes or
session processes:

```text
/tmp/pytest-of-mattb/pytest-8/test_recorded_short_headless_e0/runs/2026-07-24/20260724T203530142261Z_simulation_phase06_smoke-recorded_profile_smoke-robust_gaussian_v1-f562307ac8_ed189846
/tmp/pytest-of-mattb/pytest-8/test_recorded_short_headless_e0/runs/2026-07-24/20260724T203721764538Z_simulation_phase06_smoke-recorded_profile_smoke-legacy-5d2c1438c0_a06b57e6
```

The short smoke intentionally gates only recording and cleanup. The robust
case observed `SEARCH` and `CONVERGENCE_CANDIDATE`; its controller-goal and
final-pose ground-truth results were both `failed`. Legacy correctly reported
controller goal `not_applicable`; its final-pose ground truth was `failed`.
These separate fields are evidence, not Phase 08 robustness acceptance.

### Accepted Phase 05 artifact regression

```bash
ros2 run ros_esc validate_run \
  /home/mattb/Experiments/GESC-Gaussian/runs/2026-07-21/20260721T232824094290Z_simulation_phase05-short-recording_92bb8be7
```

Result: `passed: true`, with no failures or warnings after the profile-aware
validator change.

### Syntax, imports, XML/YAML, focused style, and diff

```bash
python3 -m compileall -q \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner \
  ros2_ws/src/ros_esc/ros_esc/experiment_recording \
  ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py \
  ros2_ws/src/turtlebot3_rotating_sensor/launch/empty_world.launch.py

python3 -c \
  'import ros_esc.scenario_runner.scenario_schema; import ros_esc.scenario_runner.run_scenario; import ros_esc.experiment_recording.record_run; import ros_esc.experiment_recording.validate_run'

python3 -c \
  'import xml.etree.ElementTree as ET; ET.parse("ros2_ws/src/turtlebot3_rotating_sensor/launch/gazebo.launch.xml")'

python3 -m flake8 --select=E,W,F --ignore=E501,W503 \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner \
  ros2_ws/src/ros_esc/ros_esc/experiment_recording/record_run.py \
  ros2_ws/src/ros_esc/ros_esc/experiment_recording/validate_run.py \
  ros2_ws/src/ros_esc/test/test_scenario_schema.py \
  ros2_ws/src/ros_esc/test/test_scenario_runner.py \
  ros2_ws/src/ros_esc/test/test_experiment_recording.py \
  ros2_ws/src/ros_esc/test/test_observability_contract.py \
  ros2_ws/src/ros_esc/test/test_legacy_behavior.py \
  ros2_ws/src/turtlebot3_rotating_sensor/launch/empty_world.launch.py

python3 -m flake8 --select=E9,F63,F7,F82 \
  ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_node_script.py

git diff --check
```

All listed focused checks passed. Both scenario YAML documents also loaded
with `yaml.safe_load`. The legacy cost-function file still has unrelated
historical E226/E231 style debt, so the focused check on that owner used the
fatal syntax/undefined-name selection rather than claiming the whole legacy
file is clean.

Before the Phase 06 checkpoint, an external review correctly identified that
the new modules/tests still contributed 1,413 findings to the repository's
strict style scan. The 1,331 quote findings were normalized mechanically, then
line length, imports, test docstrings, and function-docstring spacing were
corrected. Final unfiltered flake8 and ament pep257 checks on all new Phase 06
Python files pass with no findings. The unrelated legacy cost-function owner
continues to use its bounded fatal lint selection.

### Repository-standard package baseline

```bash
colcon --log-base /tmp/dsim_phase06_final_test_log test \
  --base-paths ros2_ws/src \
  --build-base ros2_ws/build \
  --install-base ros2_ws/install \
  --packages-select \
    ros_esc_interfaces ros_esc turtlebot3_rotating_sensor

colcon test-result --test-result-base ros2_ws/build --all
```

Result: `1027 tests, 0 errors, 872 failures, 3 skipped`. The authoritative
Phase 05.5 baseline was `999 tests, 0 errors, 875 failures, 2 skipped`, so the
trend is +28 test records, -3 inherited lint failures, and +1 explicit
environment-gated skip. All remaining failure records are package-wide
flake8, pep257, and lint-cmake results. The two existing `ros_esc` lint
meta-tests now contain no finding from the new Phase 06 runner/schema/tests;
the functional `ros_esc` result was `143 passed, 2 lint meta-test failures,
3 skipped`.

## Phase 07 commands run

### Context, backend, and pre-edit baseline

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh \
  07 implement

source /opt/ros/humble/setup.bash
source ros2_ws/install/setup.bash
python3 -m pytest -q -rs <Phase 00-06 focused suite>
```

The context validator passed. `rosbag2_py.get_registered_readers()` and
`get_registered_writers()` both contained `sqlite3`; all six generated typed
diagnostic imports resolved. The retained accepted and failed Phase 05 run
directories were readable. The pre-edit result was
`143 passed, 2 skipped in 3.72s`.

### Build, new tests, and retained focused suite

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon --log-base /tmp/dsim_phase07_build_log_final build \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash

python3 -m pytest -q -rs \
  src/ros_esc/test/test_bag_analysis.py \
  src/ros_esc/test/test_bag_analysis_integration.py

python3 -m pytest -q -rs \
  src/ros_esc/test/test_bag_analysis.py \
  src/ros_esc/test/test_bag_analysis_integration.py \
  src/ros_esc/test/test_scenario_schema.py \
  src/ros_esc/test/test_scenario_runner.py \
  src/ros_esc/test/test_experiment_recording.py \
  src/ros_esc/test/test_recording_integration.py \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_escape_recenter.py
```

Build result: all three packages passed. New Phase 07 result:
`10 passed in 4.38s`. Final retained focused result:
`153 passed, 2 skipped in 7.77s`.

The new tests cover exact timestamp retention, bounded nearest and causal
matching, no interpolation, state-gap invalidation, validity statuses,
generated sqlite3 deserialization, all standard files, path/escape/radial/
revisit/fill/merge/saturation/success metrics, failed-run partial evidence,
critical-topic invalidation, placeholder figures, raw bag hash/mtime
preservation, atomic non-overwriting output, and complete/partial matrix
aggregation.

### Retained passed and failed bag analysis

```bash
ros2 run ros_esc analyze_run <accepted-phase05-run> \
  --output-dir <temporary-root>/accepted
ros2 run ros_esc analyze_run <failed-phase05-run> \
  --output-dir <temporary-root>/failed
ros2 run ros_esc summarize_matrix <temporary-root> \
  --output-dir <temporary-root>/matrix
```

Final temporary evidence root:

```text
/tmp/dsim_phase07_real_bags_final.WKZRlx
```

The accepted run reported `complete` with fresh Phase 05 validation passed.
The failed run reported `partial` and retained the Phase 05 timestamp-regression
and console-marker failures. Each produced 11 CSV tables and 8 separate PNG
figures. The matrix found two runs: one complete and one partial. Neither real
short smoke contained fill/escape behavior, so those metrics were explicitly
`not_applicable`. SHA-256 values for both `.db3` files and both root
`completeness.json` files were identical before and after analysis.

### Syntax, imports, focused style, and diff

```bash
python3 -m compileall -q \
  ros2_ws/src/ros_esc/ros_esc/plotting_scripts/bag_reader.py \
  ros2_ws/src/ros_esc/ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py \
  ros2_ws/src/ros_esc/test/test_bag_analysis.py \
  ros2_ws/src/ros_esc/test/test_bag_analysis_integration.py

python3 -c \
  'import ros_esc.plotting_scripts.bag_reader; import ros_esc.plotting_scripts.gesc_gaussian_bag_analysis'

ament_flake8 \
  ros_esc/plotting_scripts/bag_reader.py \
  ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py \
  test/test_bag_analysis.py \
  test/test_bag_analysis_integration.py

ament_pep257 \
  ros_esc/plotting_scripts/bag_reader.py \
  ros_esc/plotting_scripts/gesc_gaussian_bag_analysis.py \
  test/test_bag_analysis.py \
  test/test_bag_analysis_integration.py

git diff --check
```

All listed focused checks passed. The final package-wide flake8 and pep257
meta-test reports contain zero findings from the Phase 07 reader, analyzer, or
tests.

### Repository-standard package baseline

```bash
colcon --log-base /tmp/dsim_phase07_test_log_authoritative test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --test-result-base ros2_ws/build --all
```

Result: `1037 tests, 0 errors, 872 failures, 3 skipped`. Relative to Phase 06,
the trend is +10 test records, 0 new errors, 0 new failures, and 0 new skips.
The 872 failures remain inherited package-wide flake8, pep257, and lint-cmake
debt. The functional `ros_esc` result was `153 passed, 2 lint meta-test
failures, 3 skipped`.

The two focused skips were the guarded Phase 06 headless Gazebo E2E and Phase
05 visible Gazebo recording tests. Both have retained prior passing evidence;
Phase 07 did not rerun Gazebo, the 26-run Phase 08 behavioral matrix, unsupported
scenario dimensions, physical hardware, Vicon, or robot commands.

## Phase 07.5 commands run

### Context, build, focused tests, and dry-run

The Phase 08 pre-edit context validator passed before implementation. After
the prerequisite handoff was written, the validator was extended to require
that handoff for Phase 08 implementation.

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon --log-base /tmp/dsim_phase075_build_final build --symlink-install \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash

python3 -m pytest -q -rs \
  src/ros_esc/test/test_simulation_disturbances.py \
  src/ros_esc/test/test_bag_analysis.py \
  src/ros_esc/test/test_bag_analysis_integration.py \
  src/ros_esc/test/test_scenario_schema.py \
  src/ros_esc/test/test_scenario_runner.py \
  src/ros_esc/test/test_experiment_recording.py \
  src/ros_esc/test/test_recording_integration.py \
  src/ros_esc/test/test_state_machine.py \
  src/ros_esc/test/test_supervisor_integration.py \
  src/ros_esc/test/test_observability_contract.py \
  src/ros_esc/test/test_legacy_behavior.py \
  src/ros_esc/test/test_robust_gaussian_algorithm.py \
  src/ros_esc/test/test_escape_recenter.py

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_validation_support.yaml \
  --operator phase08 --dry-run \
  --summary-output /tmp/phase08_support_dry_final.yaml
```

Build result: three packages passed. Focused result:
`162 passed, 2 skipped in 7.90s`. The exact skips were the guarded Phase 06
headless Gazebo E2E and Phase 05 visible Gazebo recording tests. The dry-run
resolved five runs and zero unsupported records.

### Retained runtime prerequisite

Evidence root:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08/prerequisite
```

The accepted run IDs are:

```text
20260724T232457162985Z_simulation_phase08_validation_support-contact_positive-robust_gaussian_v1-bdb7e4c828_88b20a0e
20260724T233032110244Z_simulation_phase08_validation_support-contact_negative-robust_gaussian_v1-925907a927_679a425c
20260724T233225578431Z_simulation_phase08_validation_support-seeded_gaussian-robust_gaussian_v1-8f9764f2cb_27549de2
20260724T233430348055Z_simulation_phase08_validation_support-sensor_delay-robust_gaussian_v1-3c1c885dad_49ca6486
20260724T233631073890Z_simulation_phase08_validation_support-pose_delay-robust_gaussian_v1-b65df4d2f3_6e7657a5
```

All five passed Phase 05 completeness and process/graph cleanup. Phase 07
analysis was `complete` for every run. Collision was valid and true for the
static-contact positive control, and valid and false for the other four runs.
The configured 100 ms sensor delay measured 0.100 s on both raw-cost and
source-cost relays; the configured pose delay measured 0.100 s. Delay
measurement maps bag receipt through recorded `/clock`, so accelerated
headless simulation does not turn simulation time into wall time.

The seeded-Gaussian run retained `std_dev: 0.01` and `seed_num: 8003`.
Unit coverage separately verifies identical configured seeds generate
identical NumPy sequences.

Diagnostic failed runs were preserved. The decisive Level B corrections were:

- Gazebo fixed-joint lumping renamed monitored collisions, so contact sensors
  now reference the exact generated SDF names.
- The rotating-frame node used rclpy's default signal handling and once exited
  with status 245 during recorder shutdown; it now uses the established
  explicit executor and `SignalHandlerOptions.NO` teardown sequence.
- Initial delay analysis used wall-clock bag deltas; it now reports simulation
  delay by mapping paired retained stamps through `/clock`.

### Syntax, interface, focused style, and global trend

Python compile/import checks, XML/YAML parsing, contact-enabled xacro,
`check_urdf`, generated-SDF collision-name checks, launch `--show-args`,
unfiltered `ament_flake8` and `ament_pep257` on new/clean touched owners,
fatal-only flake8 on the inherited legacy rotate/test owners, and
`git diff --check` passed.

```bash
colcon --log-base /tmp/dsim_phase075_test_global test \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
colcon test-result --test-result-base build --all
```

Global result: `1031 tests, 0 errors, 856 failures, 3 skipped`. Relative to
the Phase 07 documented baseline (`1037 / 0 / 872 / 3`), this is -6 generated
test records, no new errors, -16 inherited lint failures, and unchanged skips.
The differing generated record count reflects current package lint
enumeration, not removed functional tests. All remaining failures are
inherited package-wide flake8, pep257, and lint-cmake debt; the new and clean
touched Phase 07.5 files contribute no findings.

## Phase 08 harness and suite checks

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon --log-base /tmp/dsim_phase08a_build build --symlink-install \
  --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor
source install/setup.bash

python3 -m pytest -q \
  src/ros_esc/test/test_phase08_validation.py \
  src/ros_esc/test/test_simulation_disturbances.py \
  src/ros_esc/test/test_scenario_schema.py \
  src/ros_esc/test/test_scenario_runner.py

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_full_matrix.yaml \
  --operator phase08 --dry-run \
  --summary-output /tmp/phase08_full_dry.yaml
```

Initial harness result: `42 passed, 1 skipped in 1.96s`; the skip is the
explicit Phase 06 recorded-headless-Gazebo environment gate. The build passed
all three packages. The installed command exposes `sweep`, `freeze`, `holdout`,
`full-pass`, and `report`. The full dry-run resolves exactly 519 runs and zero
unsupported records; pure schema arithmetic independently verifies 81
training runs, 12 holdouts, and a 483-run robust acceptance denominator.

Out-of-order negative controls return 2: `freeze` without a completed sweep
reports `sweep must complete before freeze`, and `full-pass` without holdout
reports `holdout must run before the full matrix`.

### Phase 08 recorder throughput correction

Before the training sweep, one 10-second Phase 07.5 probe still took about
130 seconds because `record_run` queried each parameter service serially.
Parameter snapshots are independent, so the recorder uses bounded workers
while preserving exact values/types, deterministic node/failure order, and
the unchanged required-publisher failure gate.

Focused recorder/harness result: `22 passed, 1 skipped in 1.36s`; the skip is
the visible Gazebo recording environment gate. A new negative test retains
unavailable-node markers and required-publisher failure details.

Retained runtime proof:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08/prerequisite_parallel/2026-07-25/20260725T000048254880Z_simulation_phase08_validation_support-contact_negative-robust_gaussian_v1-925907a927_990ce7ce
```

The one-source run passed recording completeness, final-zero, and cleanup.
Total wall time was 44 seconds; target start through readiness was about
27 seconds.

The first two-source C0 training attempts then failed honestly because four
workers caused the required `/gazebo` parameter dump to hit its original
5-second timeout. The failed bags were preserved under
`phase08/sweep/C0/runs`; no candidate checkpoint was written. The corrected
bound is two workers with a 15-second per-call timeout. This is a throughput
bound, not a relaxed snapshot gate: any required publisher still fails the run
if its values and types cannot be captured.
