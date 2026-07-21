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
