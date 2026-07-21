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
