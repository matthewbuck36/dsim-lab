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
130 seconds because `record_run` launched two `ros2 param` subprocesses for
every node. Bounded subprocess workers reduced latency but made required
Gazebo/supervisor snapshots intermittently fail. Those attempts and their
failed bags remain preserved; they are not Phase 08 selection evidence.

The final recorder path uses the native `ListParameters`, `GetParameters`, and
`DescribeParameters` services from the existing recording coordinator.
Capture remains deterministically serial, preserves nested YAML and exact ROS
types, and gives required-topic publishers three attempts separated by
0.25 seconds. Optional nodes receive one attempt so transient launch helpers
cannot multiply preflight latency. Any exhausted required-publisher attempt
still fails completeness.

The same stress exposed a pre-existing ROS 2 Python teardown race: simultaneous
process-group SIGINT could interrupt native DDS work and intermittently produce
exit 245 in different algorithm nodes. The recorder now snapshots the target
process tree and sends SIGINT only to live leaf executables, in PID order, with
a 0.1-second stagger. At this Phase 07.5 evidence boundary, the six Python
owners in this launch graph deferred SIGINT/SIGTERM until the current
single-threaded callback returned, then shut down the executor before destroying
the node while the ROS context remained valid. Phase 08.1 M4 later moved only
the Gaussian-fill executable to a two-thread executor while keeping its mutable
callbacks serialized. Launch/controller ownership, final-zero publication,
cost semantics, topics, and algorithm parameters are unchanged. Both controller
spawners use the supported 30-second service-call timeout to tolerate bounded
Gazebo startup latency.

Focused result after the final correction:

```text
63 passed in 1.87s
3 selected packages built successfully
python compile, fatal flake8 selection, and git diff check: pass
```

The focused set covers deferred signals, parameter snapshot values/types and
required retries, descendant-leaf signaling/stagger, legacy final-zero order,
simulation disturbances, launch ownership, and the controller-spawner timeout.

Retained runtime proof:

```text
/tmp/phase08-staggered-leaf-repeat.ZhYIlm
/tmp/phase08-final-correction-smoke.NhthzD
/tmp/phase08-final-correction-repeat.bZq9Ma
/tmp/phase08-poststyle-smoke.WlvBG6
```

The first 60-run stagger probe produced 58 complete runs, one controller
spawner startup timeout, one required `/gazebo/list_parameters` response
timeout, and zero exit-245/139, segmentation-fault, or forced-termination
matches. After the bounded timeout and retry corrections, the installed-path
smoke passed every completeness check with readiness at 8.14 seconds. The
unchanged final correction then passed 60/60 consecutive 20-second recorder
cycles: all had complete bags, required parameter snapshots, clean target and
bag exits, and final-zero evidence. There were zero former fault-string
matches, zero required-publisher parameter failures, one Git diff hash, one
target argument vector, and no leaked ROS/Gazebo process. Optional short-lived
spawner/light nodes remained explicitly marked unavailable when they exited
before snapshot; these do not satisfy or weaken any required-publisher gate.
After formatting the touched controller launch owner, one rebuilt installed-path
smoke again passed all completeness, final-zero, clean-exit, and fault-log
checks.

### Phase 08 analysis throughput correction

The clean C0 training suite completed all nine recordings before candidate
aggregation. During aggregation, Phase 07 synchronization rebuilt each source,
GESC, pose, control, and state timestamp list for every cost anchor. One
180-second bag required about ten minutes of CPU analysis, projecting the
required matrix into multiple days beyond recording time. The sweep was
interrupted only after all nine C0 bags and `scenario_summary.yaml` had been
atomically finalized; no C0 raw evidence was removed or relabeled.

This bounded Level B correction adds one immutable timestamp index per stream
and reuses the existing bisect selection logic. One-shot `nearest_record` and
`causal_record` behavior remains available and delegates to the same indexed
implementation. Focused analysis, integration, and Phase 08 harness tests:

```text
16 passed in 4.89s
python compile, fatal flake8 selection, and git diff check: pass
```

The first completed C0 bag was analyzed into a separate comparison directory:

```text
elapsed=48.72 user=49.19 system=2.51 max_rss_kb=1120880
```

The pre-correction and indexed outputs have byte-identical
`summary_metrics.json`, summary CSV, analysis completeness report, all eleven
CSV tables, and complete relative file set. The raw bag remained unchanged.
This establishes metric/gate equivalence while removing repeated timestamp-list
construction.

### Phase 08 training selection and freeze

The authoritative sweep executed 81/81 training runs at clean commit
`d073f2b479a9510d999c72b90aecd20fab2bbdb7`. The harness functional precheck
reported `171 passed, 2 skipped in 8.23s`; the skips are the two explicit
opt-in Gazebo recording tests.

Candidates C0-C5, C7, and C8 were infrastructure-eligible. C6 was ineligible
because one preserved three-source run exhausted the required
`/gazebo/list_parameters` response attempts, failed recording completeness,
and retained valid cleanup evidence. All nine candidates had 0% end-to-end
success and zero escape attempts. The declared tie-break selected C8 by its
lowest median path length, `13.228608734409306 m`; this is not an acceptance
pass.

The frozen validation-only profile is:

```text
gaussian_fill_covariance_scale=3.0
gaussian_fill_amplitude_depth_scale=1.8
gaussian_fill_exit_sigma=2.75
stall_window_sec=2.0
minimum_radial_progress_m=0.08
sha256=b1531988de3eb650fbced657555532baf1eb66056c0203dd21908c4def8f093e
```

No launch default, cost sign/unit, public topic, legacy behavior, or physical
semantics changed.

## Phase 08 staged-validation amendment (2026-07-25)

This documentation-only amendment retires the 519-run pass repeated three
times as a future acceptance design and preserves every v1 command/result
above as historical evidence. No ROS build, pytest suite, Gazebo run, bag
recording, parameter freeze, acceptance gate, or tag was executed for this
amendment.

The approved v2 plan declares exactly 120 runs: 10 activation, 30 tuning
(three candidates over the same ten cases), 20 new hidden holdouts, 50
additional unique validation cases, and 10 targeted reproducibility repeats.
The installed `validate_robustness` command remains the historical v1
implementation until the v2 interface and scenario files are implemented and
tested.

Documentation checks run for this amendment:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 plan
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 implement
git diff --check
```

Exact outcomes:

```text
Phase 08 plan context is complete.
Phase 08 implement context is complete.
git diff --check: pass
```

`validate_required_docs.sh` also reported
`All Phase 00 audit documents exist.` Do not infer a runtime or behavioral pass
from these documentation/context checks.

## Compaction-safe context-retention hardening (2026-07-25)

The repository now carries live execution state between the saved plan and
final handoff. This change added root `AGENTS.md`, a phase-status template and
initializer, required Implement-context status validation, semantic milestone
checkpoints, post-compaction recovery instructions, and live-status content in
the context bundle. All Implement prompts now require live status updates,
bounded logs/commands, milestone checkpoints, and repository-based recovery.

Commands run:

```bash
bash -n \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/make_codex_context_bundle.sh \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh

DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/init_phase_status.sh 08
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 plan
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh 08 implement
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_required_docs.sh
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh 08
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/make_codex_context_bundle.sh \
  /home/mattb/dsim-lab /tmp/dsim_phase08_context_bundle.txt
git diff --check
```

Exact results:

```text
shell syntax checks: pass
existing Phase 08 status non-overwrite check: pass
fresh temporary-repository Phase 09 status initialization: pass
fresh status second-call preservation: pass
invalid phase 11 exit: 2
Phase 08 plan context is complete.
Phase 08 implement context is complete.
All Phase 00 audit documents exist.
Phase 08 checkpoint written with plan/status hashes and live-status snapshot.
context bundle contains AGENTS.md and Phase 08 live status/recovery sections.
git diff --check: pass
```

No ROS build, pytest suite, Gazebo run, bag recording, parameter freeze,
acceptance gate, physical command, commit, or tag was executed by this
documentation/tooling hardening.

## Phase 08 v2 activation and staged harness implementation (2026-07-25)

The historical v1 root was inventoried read-only and closed separately. The
Phase 08a implementation gives detector confirmation sole robust-supervisor
activation ownership, aggregates source score over complete rotating-sensor
revolutions, installs the staged v2 validator interface, and adds five
schema-v2 suites. Historical v1 execution commands now fail closed; its report
reader remains available.

Build and retained functional regression:

```bash
colcon --log-base /tmp/dsim_phase08_v2_m2_harness_build build \
  --symlink-install \
  --packages-select ros_esc_interfaces ros_esc \
  turtlebot3_rotating_sensor

python3 -m pytest -q -rs \
  src/ros_esc/test/test_simulation_disturbances.py \
  src/ros_esc/test/test_phase08_validation.py \
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

Final results:

```text
3 packages finished
188 passed, 2 skipped in 9.49s
```

The skipped tests remain the explicit
`RUN_GESC_PHASE06_GAZEBO_E2E=1` and
`DSIM_RUN_GAZEBO_RECORDING_TEST=1` recording gates. An earlier retained-suite
attempt produced `187 passed, 2 skipped, 1 failed`: the synthetic ROS peer
stopped publishing just as its callback executor was delayed by the larger
suite. Extending only the test input-publication interval corrected that
scheduling race. Three consecutive focused integration runs then each
reported `5 passed`.

The representative v1 replay fixture is a compact value excerpt from
`20260725T085905912016Z_simulation_phase08_holdout-holdout_tuple_low_high-robust_gaussian_v1-622b56111b_923463df`.
It is regression input only and is never referenced by the v2 manifest or
counted as v2 evidence.

Scenario dry-runs:

```bash
ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_activation.yaml \
  --operator phase08_v2 --dry-run \
  --summary-output /tmp/phase08_v2_activation_dry.yaml

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_training.yaml \
  --operator phase08_v2 --dry-run \
  --summary-output /tmp/phase08_v2_training_dry.yaml

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_holdout.yaml \
  --operator phase08_v2 --dry-run \
  --summary-output /tmp/phase08_v2_holdout_dry.yaml

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_validation.yaml \
  --operator phase08_v2 --dry-run \
  --summary-output /tmp/phase08_v2_validation_dry.yaml

ros2 run ros_esc run_scenario \
  src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_reproducibility.yaml \
  --operator phase08_v2 --dry-run \
  --summary-output /tmp/phase08_v2_reproducibility_dry.yaml
```

Resolved/unsupported counts were `10/0`, `10/0`, `20/0`, `50/0`, and
`10/0`. The validator expands the ten training cases over exactly three
candidates, producing the declared 30 tuning executions and 120 total runs.
The unique holdout/validation IDs are disjoint, the family allocation is
`7/3/2/2/2/4` plus `18/6/6/6/6/8`, and all ten repeat definitions match their
predeclared references exactly.

Static validation:

```bash
python3 -m compileall -q \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner \
  ros2_ws/src/ros_esc/ros_esc/supervisor_node \
  ros2_ws/src/ros_esc/test

python3 -m flake8 --select=E9,F63,F7,F82 <touched Python files>
python3 -m flake8 --select=E,W,F --ignore=E501,W503 \
  <touched Python files>
git diff --check
```

All listed static checks passed. No Phase 08 v2 Gazebo batch, bag recording,
parameter freeze, behavioral acceptance gate, physical command, or tag was
executed in this implementation milestone.

### Post-commit package baseline and recorded smoke

After commit `8aab27c`, the repository-standard package command reported:

```text
1040 tests, 0 errors, 836 failures, 3 skipped
```

The 836 failures remain the inherited package-wide flake8, pep257, and
`ros_esc_interfaces` lint-cmake debt. This is 36 fewer failures than the
documented Phase 07 baseline (`1037 / 0 / 872 / 3`), so the global failure
count did not worsen.

The explicit opt-in two-profile smoke then ran:

```bash
RUN_GESC_PHASE06_GAZEBO_E2E=1 python3 -m pytest -q -s \
  ros2_ws/src/ros_esc/test/test_scenario_runner.py::\
test_recorded_short_headless_end_to_end
```

Result: `1 passed in 34.69s`. Both five-second runs passed recording
completeness, scenario classification, and cleanup:

```text
/tmp/pytest-of-mattb/pytest-10/test_recorded_short_headless_e0/runs/2026-07-26/20260726T003612653021Z_simulation_phase06_smoke-recorded_profile_smoke-robust_gaussian_v1-f562307ac8_92c0aa8e
/tmp/pytest-of-mattb/pytest-10/test_recorded_short_headless_e0/runs/2026-07-26/20260726T003629195830Z_simulation_phase06_smoke-recorded_profile_smoke-legacy-5d2c1438c0_13388f47
```

The robust smoke observed `SEARCH` only; its controller and ground-truth goals
were both false. Legacy controller goal remained `not_applicable` and its
ground-truth goal was false. This short smoke is infrastructure/compatibility
evidence only, not one of the ten activation proofs.

### Phase 08 v2 activation gate and Level C closeout

The separate v2 evidence root did not exist before runtime. The mandatory
activation stage ran once with an outer bound:

```bash
timeout 7200s ros2 run ros_esc validate_robustness activation \
  --operator phase08_v2 \
  --evidence-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2
```

Result: expected workflow failure exit 1 after all ten declared runs were
retained:

```text
run count:                         10/10
full integrity/lifecycle pass:      1/10
recording complete:                 3/10
analysis complete:                  3/10
classification pass:                1/10
cleanup pass:                       10/10
controller plus ground-truth:       1/10
valid no-collision evidence:         9/10
typed fills:                            7
observed escape attempts:               1
functional regression: 189 passed, 2 skipped in 10.44s
```

The workflow manifest SHA-256 is
`66c17005f67dd056e41673a0754e838f5ee22a0280b0f5d649043ad3c461cd71`.
The retained state files are:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2/workflow_state/v2_activation.json
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2/workflow_state/v2_failure.json
```

Six cases failed completeness with
`typed ROS timestamps regressed by more than 0.150 s`. A late stale-source
`FILL_CREATED` followed a later timeout/failsafe event. The stalled-assist case
had a separate required publisher-parameter snapshot failure. The high-level
goal case was the sole complete lifecycle pass. The noise/delay case observed
one real escape/recenter sequence but did not satisfy its declared goal
lifecycle.

All ten completeness documents and sqlite3 bags are retained under the 1.8 GiB
root. The `sqlite3` CLI is not installed on this host, so that first diagnostic
returned command-not-found and was not counted. A read-only standard-library
fallback opened every bag with `mode=ro` and ran `PRAGMA quick_check`:

```text
sqlite_quick_check=10/10
completeness_documents=10
```

No Phase 08, Gazebo, recording, scenario-runner, or rosbag process remained.
Representative v1 hashes matched the immutable v1 closeout after the v2 stage.

The plan requires partial reporting from a retained early-stop state. The
existing report path was extended without rerunning simulation and covered by
a focused regression. Report generation then ran:

```bash
ros2 run ros_esc validate_robustness report \
  --operator phase08_v2 \
  --evidence-root \
  /home/mattb/Experiments/GESC-Gaussian/runs/phase08_v2
```

Result: expected exit 1. Gate 1 passed; Gate 2 failed at `1/10`; Gates 3–14 are
`NOT RUN`; the 70-run denominator and Wilson intervals are explicitly not
applicable; `simulation_ready=false`.

Closure regression:

```bash
source install/setup.bash
timeout 300s python3 -m pytest -q -rs \
  src/ros_esc/test/test_simulation_disturbances.py \
  src/ros_esc/test/test_phase08_validation.py \
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

Result:

```text
190 passed, 2 skipped in 11.70s
```

Exact skips:

- `test_scenario_runner.py:306`: explicit
  `RUN_GESC_PHASE06_GAZEBO_E2E=1` gate; the test was run separately and
  passed during pre-activation smoke.
- `test_recording_integration.py:56`: explicit
  `DSIM_RUN_GAZEBO_RECORDING_TEST=1` visible-Gazebo gate.

The focused report file returned `14 passed in 3.98s`. Python compilation,
fatal and focused flake8, `ament_flake8`, `ament_pep257`, and
`git diff --check` passed on the changed validator and test.

Three setup/style invocations were not counted as test evidence: one pytest
call before sourcing the workspace could not import `ros_esc`; one used the
wrong relative test path and collected nothing; and
`python3 -m ament_flake8` reported that the package has no `__main__`.
The sourced pytest commands and the `ament_flake8`/`ament_pep257` executables
above are the corrected successful invocations.

The repository-standard package result remains the pre-activation
`1040 tests, 0 errors, 836 inherited failures, 3 skipped`; it was not rerun
after the two-file reporting-only correction. No tuning, parameter selection,
freeze, holdout, 70-run validation, reproducibility, physical test, or
simulation-ready tag was run after the activation early-stop.

## Phase 08.1 M4 readiness and evidence semantics

The retained v2 bags were inspected read-only; their stored metadata,
completeness reports, and bags were not regenerated. The six apparent
`AlgorithmEvent` regressions were cross-producer ordering on a shared bus, but
the same evidence also exposed real Gaussian event-emission lag of 4.0–15.6
seconds. The stalled-assist and recenter/resume failures separately exposed a
non-operational controller manager and a pre-readiness controller fault race.

Lifecycle-history regression:

```bash
timeout 180s bash -lc '
  source /opt/ros/humble/setup.bash &&
  source ros2_ws/install/setup.bash &&
  export ROS_LOG_DIR=/tmp/dsim_phase08_1_m4_ros_logs &&
  python3 -m pytest -q \
    ros2_ws/src/ros_esc/test/test_experiment_recording.py \
    -k "preauthorization or atomic_authorization or run_validator_wires"'
```

Final result: `8 passed, 49 deselected in 0.41s`. The tests cover every
independent live and retained-bag lifecycle signal: non-`SEARCH`, failsafe,
prior transition, active fill, and active escape. They also observe
`VERIFY_EXTREMUM`, then clean `SEARCH`, reset the heartbeat epoch, and still
reject authorization. A never-authorized shutdown closes monitoring before
the explicit-stop `FAILSAFE`, and both bag state and command scans stop at the
first stop receipt, so post-stop evidence is not mislabeled as
pre-authorization behavior.

Focused recorder, runner, and controller regression:

```bash
timeout 240s bash -lc '
  source /opt/ros/humble/setup.bash &&
  source ros2_ws/install/setup.bash &&
  export ROS_LOG_DIR=/tmp/dsim_phase08_1_m4_ros_logs &&
  python3 -m pytest -q \
    ros2_ws/src/ros_esc/test/test_experiment_recording.py \
    ros2_ws/src/ros_esc/test/test_scenario_runner.py \
    ros2_ws/src/ros_esc/test/test_legacy_behavior.py'
```

Final source-state result: `104 passed, 1 skipped in 2.33s`. The skip is the
explicit `RUN_GESC_PHASE06_GAZEBO_E2E=1` recorded headless-Gazebo gate. A preceding
invocation without `ROS_LOG_DIR` produced `12 failed, 84 passed, 1 skipped`
after rclpy could not write under `/home/mattb/.ros`; that environment-invalid
attempt is not test evidence. The writable-log rerun above started a fresh
process and passed.

Broad M2–M4 recording/analysis/state regression:

```bash
timeout 300s bash -lc '
  source /opt/ros/humble/setup.bash &&
  source ros2_ws/install/setup.bash &&
  export ROS_LOG_DIR=/tmp/dsim_phase08_1_m4_ros_logs &&
  export MPLCONFIGDIR=/tmp/dsim_phase08_1_m4_matplotlib &&
  python3 -m pytest -q -rs \
    ros2_ws/src/ros_esc/test/test_experiment_recording.py \
    ros2_ws/src/ros_esc/test/test_recording_integration.py \
    ros2_ws/src/ros_esc/test/test_scenario_runner.py \
    ros2_ws/src/ros_esc/test/test_observability_contract.py \
    ros2_ws/src/ros_esc/test/test_legacy_behavior.py \
    ros2_ws/src/ros_esc/test/test_phase08_validation.py \
    ros2_ws/src/ros_esc/test/test_bag_analysis.py \
    ros2_ws/src/ros_esc/test/test_bag_analysis_integration.py \
    ros2_ws/src/ros_esc/test/test_state_machine.py \
    ros2_ws/src/ros_esc/test/test_supervisor_integration.py'
```

Final source-state result: `182 passed, 2 skipped in 12.08s`. The skips are the
explicit
`DSIM_RUN_GAZEBO_RECORDING_TEST=1` visible-Gazebo recording test and the
explicit recorded headless-Gazebo scenario test. Neither was enabled in M4.

The final tests cover:

- two fresh operational epochs around parameter capture, with readiness
  remaining false when the controller-manager service disappears;
- permanent rejection of robust pre-authorization non-`SEARCH`, failsafe,
  prior-transition, active-fill, and active-escape evidence even after a later
  clean `SEARCH` and a fresh epoch reset, with the same history checked from
  retained bag messages and coordinator metadata;
- an authorization-or-stop boundary that prevents expected post-stop state or
  command evidence from being mislabeled as pre-authorization behavior;
- an absolute-deadline crossing during the final service/authorization path;
- run-specific promotion of selected heartbeat streams to required graph,
  singleton-publisher, rosbag, parameter-owner, and minimum-count evidence;
- all four zero/nonzero sensor/pose delay combinations and exact canonical
  consumer-topic routing;
- a code-enforced physical-mode bypass of Gazebo/controller-manager checks;
- exact rather than near-equal fill request/source correlation;
- strict JSON rejection/normalization, invalid timestamp tolerance, nonfinite
  terminal odometry, and finite-coordinate distance overflow;
- the real Gaussian-fill callback under live `/clock`, plus the production
  two-thread executor add/spin/remove/shutdown lifecycle; and
- infrastructure-invalid, runtime-failed, evidence-extraction-failed,
  recording-invalid, and cleanup-failed runner classifications without an
  automatic retry.

Isolated selected-package build:

```bash
timeout 180s bash -lc '
  source /opt/ros/humble/setup.bash &&
  cd ros2_ws &&
  colcon --log-base /tmp/dsim_phase08_1_m4_colcon_logs_final build \
    --build-base /tmp/dsim_phase08_1_m4_build \
    --install-base /tmp/dsim_phase08_1_m4_install \
    --packages-select ros_esc_interfaces ros_esc'
```

Final exact-source follow-up and installed smoke:

```bash
timeout 120s bash -lc '
  source /opt/ros/humble/setup.bash &&
  cd ros2_ws &&
  colcon --log-base /tmp/dsim_phase08_1_m4_colcon_logs_final_boundary build \
    --build-base /tmp/dsim_phase08_1_m4_build \
    --install-base /tmp/dsim_phase08_1_m4_install \
    --packages-select ros_esc'

timeout 60s bash -lc '
  source /opt/ros/humble/setup.bash &&
  source /tmp/dsim_phase08_1_m4_install/setup.bash &&
  export ROS_LOG_DIR=/tmp/dsim_phase08_1_m4_ros_logs &&
  ros2 run ros_esc record_run --help &&
  ros2 run ros_esc run_scenario --help &&
  python3 -c "from ros_esc.gaussian_fill_node.gaussian_fill_script import \
GaussianFill, main; assert GaussianFill and main"'
```

The clean isolated build completed `2 packages finished in 2min 30s`. A first
incremental rebuild after docstring-style and single-evaluation cleanup
completed in `31.2s`; the authorization/shutdown-boundary source rebuilt in
`31.0s`; and the final matching offline command boundary rebuilt `ros_esc` in
`30.9s` against that unchanged isolated interface install. From the final
isolated install, both
`ros2 run ros_esc record_run --help` and
`ros2 run ros_esc run_scenario --help` returned exit 0, and the actual
`GaussianFill` class plus production `main` imported successfully. A first
smoke command requested the nonexistent symbol `GaussianFillNode`; it failed
only that import after both help commands passed. Replacing the mistaken
symbol with the source-owned `GaussianFill` reran the complete smoke and
passed.

Same-configuration `ament_flake8` current/HEAD findings are:

```text
record_run.py:              371 / 375
validate_run.py:            191 / 193
run_scenario.py:              0 / 0
gaussian_fill_script.py:     410 / 410
controller_node_script.py:   134 / 135
test_experiment_recording.py: 259 / 259
test_scenario_runner.py:       0 / 0
test_legacy_behavior.py:     190 / 190
```

The remaining findings are inherited D/E/I/Q debt; M4 adds none and removes
seven. `ament_pep257` reports inherited findings in the older owners
(`record_run.py` 13, `validate_run.py` 5, `gaussian_fill_script.py` 11, and
`controller_node_script.py` 22) and no problems in the three changed test
files or `run_scenario.py`. Fatal pyflakes/parse selection
`E9,F63,F7,F82` passed over all eight changed Python owners.

Final repository/document checks:

```bash
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh \
  08 implement
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh \
  08 implement --strict-history
DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_required_docs.sh
git diff --check
```

Both normal and strict context validation returned
`Phase 08 implement context is complete`; required-doc validation returned
`All Phase 00 audit documents exist`; shell syntax, Python compile, package
XML, topic-manifest YAML, fatal flake8, and `git diff --check` passed.

No Gazebo process, physical command, tuning, holdout, acceptance run,
simulation-ready tag, or historical-v1/v2 evidence rewrite occurred in M4.

## Phase 08.1 M5 scenario-contract correction

Focused schema and runner regression:

```bash
timeout 60s bash -lc '
  source /opt/ros/humble/setup.bash &&
  source /tmp/dsim_phase08_1_m4_install/setup.bash &&
  export ROS_DOMAIN_ID=65 &&
  export ROS_LOG_DIR=/tmp/dsim_phase08_1_m5_focused_ros_logs &&
  export PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc:$PYTHONPATH &&
  python3 -m pytest -q \
    ros2_ws/src/ros_esc/test/test_scenario_schema.py \
    ros2_ws/src/ros_esc/test/test_scenario_runner.py'
```

Final result: `64 passed, 1 skipped in 1.98s`. The skip is the explicit
`RUN_GESC_PHASE06_GAZEBO_E2E=1` recorded headless-Gazebo test; it was not
enabled.

Full non-linter package regression:

```bash
timeout 120s bash -lc '
  source /opt/ros/humble/setup.bash &&
  source /tmp/dsim_phase08_1_m4_install/setup.bash &&
  export ROS_DOMAIN_ID=66 &&
  export ROS_LOG_DIR=/tmp/dsim_phase08_1_m5_full_ros_logs &&
  export MPLCONFIGDIR=/tmp/dsim_phase08_1_m5_full_mpl &&
  export PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc:$PYTHONPATH &&
  python3 -m pytest -q ros2_ws/src/ros_esc/test -m "not linter"'
```

Final result: `278 passed, 2 skipped, 3 deselected in 15.38s`. The skips are
the explicit `DSIM_RUN_GAZEBO_RECORDING_TEST=1` visible-Gazebo recording test
and the recorded headless-Gazebo test above. The three deselections are the
repository linter markers. Neither Gazebo nor physical hardware ran.

An earlier identical full sweep without a writable `ROS_LOG_DIR` ended
`20 failed, 258 passed, 2 skipped, 3 deselected in 13.79s`: the first rclpy
initialization could not open `/home/mattb/.ros/log/...` in the sandbox, then
left the process-global context initialized for the remaining ROS tests. This
was an environment-invalid test attempt. The fresh-process bounded rerun above
isolated logs under `/tmp` and passed.

Python and focused style checks:

```bash
python3 -m py_compile \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py \
  ros2_ws/src/ros_esc/test/test_scenario_runner.py \
  ros2_ws/src/ros_esc/test/test_scenario_schema.py \
  ros2_ws/src/ros_esc/test/test_legacy_behavior.py \
  ros2_ws/src/ros_esc/setup.py

ament_flake8 \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py \
  ros2_ws/src/ros_esc/test/test_scenario_runner.py \
  ros2_ws/src/ros_esc/test/test_scenario_schema.py

ament_pep257 \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner/run_scenario.py \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py \
  ros2_ws/src/ros_esc/test/test_scenario_runner.py \
  ros2_ws/src/ros_esc/test/test_scenario_schema.py
```

Compilation passed; both focused linters reported no problems. The changed
legacy-test and setup owners retain inherited same-configuration flake8 debt
at `190/190` and `23/23`; M5 adds none.

Final isolated build and installed dry-run:

```bash
timeout 120s bash -lc '
  source /opt/ros/humble/setup.bash &&
  source /tmp/dsim_phase08_1_m4_install/setup.bash &&
  cd /home/mattb/dsim-lab/ros2_ws &&
  colcon --log-base /tmp/dsim_phase08_1_m5_colcon_logs_final3 build \
    --build-base /tmp/dsim_phase08_1_m5_build_final3 \
    --install-base /tmp/dsim_phase08_1_m5_install_final3 \
    --packages-select ros_esc'

timeout 60s bash -lc '
  source /opt/ros/humble/setup.bash &&
  source /tmp/dsim_phase08_1_m4_install/setup.bash &&
  source /tmp/dsim_phase08_1_m5_install_final3/setup.bash &&
  ros2 run ros_esc run_scenario \
    /tmp/dsim_phase08_1_m5_install_final3/ros_esc/share/ros_esc/scenario_runner/scenarios/phase08_1_diagnostic_activation.yaml \
    --operator phase08_1_m5 \
    --runs-root /tmp/dsim_phase08_1_m5_dry_runs \
    --summary-output /tmp/phase08_1_m5_installed_dry_run_final.yaml \
    --dry-run'
```

The isolated build completed one package in `1.32s`, using
`ros_esc_interfaces` from the final M4 isolated underlay. The installed
dry-run resolved 10 runs, 0 unsupported cases, 10 bound activation contracts,
and a `3.0 s` selected verification margin for every case. Retained summary:
`/tmp/phase08_1_m5_installed_dry_run_final.yaml`; verbose stdout:
`/tmp/phase08_1_m5_installed_dry_run_final.stdout`.

The new suite SHA-256 is
`1e030602ecee99c2d1f563a0ae19e65b1c8e6608662e178eb52b8766edc5a9a7`.
The reachability record SHA-256 is
`e787e226d3de4ef19e93867fcb148164d8c306dd7e0264d0354c519793ec3590`.
The historical v2 activation YAML remains
`a5e91d2132b3dacccedc24aba13bdacd9ef5ba4ec7c8ae7b69ced6eadaf47d72`,
and its normalized ten case keys are asserted unchanged.

Normal and strict-history Phase 08 Implement context validation both returned
`Phase 08 implement context is complete`; required-doc validation returned
`All Phase 00 audit documents exist`. Both activation YAML files parsed and
`git diff --check` passed.

`checkpoint_phase.sh 08` passed and refreshed the compact Phase 08
material-boundary snapshot.

No Gazebo process, physical command, formal acceptance run, tuning, holdout,
simulation-ready tag, or historical-v1/v2 evidence rewrite occurred in M5.

## Phase 08.1 M6 minimal runtime probes

### Probe 1 — calibrated goal verification

Predeclared case: `activation_goal_high`. Committed M5 HEAD: `8ca59d1`.
Suite SHA-256:
`1e030602ecee99c2d1f563a0ae19e65b1c8e6608662e178eb52b8766edc5a9a7`.
The fresh evidence root was absent before execution and 327 GiB was free.

```bash
timeout --signal=INT --kill-after=45s 600s bash -lc '
  source /opt/ros/humble/setup.bash &&
  source /home/mattb/dsim-lab/ros2_ws/install/setup.bash &&
  source /tmp/dsim_phase08_1_m4_install/setup.bash &&
  source /tmp/dsim_phase08_1_m5_install_final3/setup.bash &&
  export ROS_DOMAIN_ID=68 &&
  export ROS_LOG_DIR=/tmp/dsim_phase08_1_m6_goal_ros_logs &&
  export MPLCONFIGDIR=/tmp/dsim_phase08_1_m6_goal_mpl &&
  export TURTLEBOT3_MODEL=burger &&
  unset DISPLAY &&
  ros2 run ros_esc run_scenario \
    /tmp/dsim_phase08_1_m5_install_final3/ros_esc/share/ros_esc/scenario_runner/scenarios/phase08_1_diagnostic_activation.yaml \
    --operator phase08_1_m6 \
    --case-id activation_goal_high \
    --runs-root /home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6 \
    --summary-output /home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6/activation_goal_high_summary.yaml'
```

Result: exit 0; `record_run` returned 0 without timeout; recording,
classification, and cleanup passed. The collapsed state path was
`SEARCH -> VERIFY_EXTREMUM -> GOAL_HOLD`; all required predicates passed,
forbidden states/events were absent, collision was false, and no new node or
session process remained. Completeness passed no-motion-before-readiness,
clean-preauthorization-lifecycle, fresh/nonregressing typed timestamps,
event-source causality, final readiness false, strict finite JSON, and final
zero on all three command evidence streams.

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6/2026-07-26/20260726T060431139250Z_simulation_phase08_1_diagnostic_activation-activation_goal_high-robust_gaussian_v1-5ca0c583_860f0907
```

Standard one-time analysis:

```bash
timeout 300s bash -lc '
  source /opt/ros/humble/setup.bash &&
  source /home/mattb/dsim-lab/ros2_ws/install/setup.bash &&
  source /tmp/dsim_phase08_1_m4_install/setup.bash &&
  source /tmp/dsim_phase08_1_m5_install_final3/setup.bash &&
  export ROS_DOMAIN_ID=68 &&
  export ROS_LOG_DIR=/tmp/dsim_phase08_1_m6_goal_analysis_ros_logs &&
  export MPLCONFIGDIR=/tmp/dsim_phase08_1_m6_goal_analysis_mpl &&
  ros2 run ros_esc analyze_run \
    /home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6/2026-07-26/20260726T060431139250Z_simulation_phase08_1_diagnostic_activation-activation_goal_high-robust_gaussian_v1-5ca0c583_860f0907 \
    --output-dir \
    /home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6/2026-07-26/20260726T060431139250Z_simulation_phase08_1_diagnostic_activation-activation_goal_high-robust_gaussian_v1-5ca0c583_860f0907/analysis'
```

The analyzer returned `analysis_status=complete` with no recording or analysis
failures. It retained 11 tables, eight plots, and 23,261 synchronized rows.
Controller and ground-truth success were valid; convergence time was
`98.543209938 s`, terminal state was `GOAL_HOLD`, final goal distance was
`0.2803891005 m`, and collision/failsafe/timeout were false. Raw bag SHA-256:
`9b9905db133be446039570a8d6c9897726d87e00830625326af48cdc7c9bb652`.

Probe 1 cleanup satisfied the declared condition for the distinct
`activation_fill_create` Probe 2. No replacement or additional probe was
introduced.

### Probe 2 — fill creation and escape

Predeclared case: `activation_fill_create`. It ran serially only after Probe 1
cleanup passed, using the same committed M5 HEAD and suite hash.

```bash
timeout --signal=INT --kill-after=45s 600s bash -lc '
  source /opt/ros/humble/setup.bash &&
  source /home/mattb/dsim-lab/ros2_ws/install/setup.bash &&
  source /tmp/dsim_phase08_1_m4_install/setup.bash &&
  source /tmp/dsim_phase08_1_m5_install_final3/setup.bash &&
  export ROS_DOMAIN_ID=69 &&
  export ROS_LOG_DIR=/tmp/dsim_phase08_1_m6_fill_ros_logs &&
  export MPLCONFIGDIR=/tmp/dsim_phase08_1_m6_fill_mpl &&
  export TURTLEBOT3_MODEL=burger &&
  unset DISPLAY &&
  ros2 run ros_esc run_scenario \
    /tmp/dsim_phase08_1_m5_install_final3/ros_esc/share/ros_esc/scenario_runner/scenarios/phase08_1_diagnostic_activation.yaml \
    --operator phase08_1_m6 \
    --case-id activation_fill_create \
    --runs-root /home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6 \
    --summary-output /home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6/activation_fill_create_summary.yaml'
```

Result: exit 1 after about `216.7 s`. The process exit represents the retained
valid behavioral classification failure; it was not an infrastructure or
orchestration failure. `record_run` returned 0 without timeout, recording and
completeness passed, infrastructure status was `completed`, cleanup passed,
and no new node or session process remained.

Retained run:

```text
/home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6/2026-07-26/20260726T061155030660Z_simulation_phase08_1_diagnostic_activation-activation_fill_create-robust_gaussian_v1-66aad7_9bba343b
```

Standard one-time analysis:

```bash
timeout 300s bash -lc '
  source /opt/ros/humble/setup.bash &&
  source /home/mattb/dsim-lab/ros2_ws/install/setup.bash &&
  source /tmp/dsim_phase08_1_m4_install/setup.bash &&
  source /tmp/dsim_phase08_1_m5_install_final3/setup.bash &&
  export ROS_DOMAIN_ID=69 &&
  export ROS_LOG_DIR=/tmp/dsim_phase08_1_m6_fill_analysis_ros_logs &&
  export MPLCONFIGDIR=/tmp/dsim_phase08_1_m6_fill_analysis_mpl &&
  ros2 run ros_esc analyze_run \
    /home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6/2026-07-26/20260726T061155030660Z_simulation_phase08_1_diagnostic_activation-activation_fill_create-robust_gaussian_v1-66aad7_9bba343b \
    --output-dir \
    /home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6/2026-07-26/20260726T061155030660Z_simulation_phase08_1_diagnostic_activation-activation_fill_create-robust_gaussian_v1-66aad7_9bba343b/analysis'
```

The analyzer returned `analysis_status=complete` with no recording or analysis
failures. It retained one active fill, one successful escape, and eight plots.
Raw bag SHA-256:
`f10924891a97478add654d373301a76047fce9921c0fb348ecd3a1987de1122e`.

The activation subclaim passed:

- `SEARCH -> VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE`;
- required `CONVERGENCE_CONFIRMED`, `FILL_CREATED`, and `ESCAPE_STARTED`
  evidence;
- `0.091432122 s` reported fill-design wall time and approximately
  `0.092409 s` request-to-fill receipt latency against the unchanged `5.0 s`
  limit;
- exact request, result, and lifecycle source timestamp correlation;
- one successful `8.714248035 s` escape with `0.204169 m` maximum radial
  progress, no stall, no assist, and no collision;
- typed timestamp, readiness, pre-authorization, strict-JSON, cleanup, and
  final-zero completeness.

The full global contract correctly failed. The later path was
`RECENTER -> FAILSAFE`, with `TIMEOUT` and `FAILSAFE` events after
`30.046870124 s`. Recenter began inside the retained fill's `0.608675 m`
avoidance disk. The clearance-first shared direction selector accumulated 141
direction revisions and the robot traveled about `2.738 m`, but minimum room
center distance was only `0.658224 m`, outside the `0.25 m` tolerance. All 300
unique recenter control samples were unsaturated and command tracking was
close, so this was a guidance-policy failure rather than simulator or actuator
tracking failure.

No replacement, third M6 probe, timeout-only rerun, matrix, tuning, holdout,
GUI, tag, or physical command was run. Both predeclared M6 questions were
answered; another unchanged run would repeat diagnosed evidence.

## Phase 08.1 M7 diagnostic closeout

M7 changed documentation and workflow-context tooling only; it changed no ROS
or algorithm code. It did not rerun pytest, a build, Gazebo, either M6 probe,
or bag analysis because the M6 code/evidence boundary was already committed
at `c959ce1`.

Read-only retained-evidence assertions:

```bash
python3 -c "
import json, pathlib, yaml
root = pathlib.Path(
    '/home/mattb/Experiments/GESC-Gaussian/runs/phase08_1_m6'
)
goal = yaml.safe_load(
    (root / 'activation_goal_high_summary.yaml').read_text()
)
fill = yaml.safe_load(
    (root / 'activation_fill_create_summary.yaml').read_text()
)
assert goal['resolved_run_count'] == 1
assert goal['runs'][0]['classification']['passed'] is True
assert fill['resolved_run_count'] == 1
fill_run = fill['runs'][0]
assert fill_run['classification']['passed'] is False
predicates = fill_run['classification']['predicate_results']
assert predicates['required_state_path'] is True
assert predicates['required_events'] is True
assert predicates['no_forbidden_states'] is False
assert predicates['no_forbidden_events'] is False
runs = [
    pathlib.Path(goal['runs'][0]['run_directory']),
    pathlib.Path(fill_run['run_directory']),
]
expected = [
    '9b9905db133be446039570a8d6c9897726d87e00830625326af48cdc7c9bb652',
    'f10924891a97478add654d373301a76047fce9921c0fb348ecd3a1987de1122e',
]
for run, expected_hash in zip(runs, expected):
    completeness = json.loads((run / 'completeness.json').read_text())
    analysis = json.loads(
        (run / 'analysis/analysis_completeness.json').read_text()
    )
    assert completeness['passed'] is True
    assert completeness['failures'] == []
    assert completeness['warnings'] == []
    assert analysis['status'] == 'complete'
    assert analysis['recording_failures'] == []
    assert analysis['analysis_failures'] == []
    assert list(analysis['raw_bag_sha256'].values()) == [expected_hash]
print('M7 retained-evidence assertions passed')
"
```

Result: `M7 retained-evidence assertions passed`. This parsed existing summary,
completeness, and analysis documents only. The sqlite3 bags were neither
rehashed nor reanalyzed.

Current document/suite hash check:

```bash
sha256sum \
  docs/codex/gesc_gaussian/validation/phase_08_1_activation_contract.md \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_1_diagnostic_activation.yaml \
  ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v2_activation.yaml
```

Result:

```text
71a3f8033996298c0d13cebc7efb8c25b98812a3dd80023bd4a2057736214b1e  phase_08_1_activation_contract.md
1e030602ecee99c2d1f563a0ae19e65b1c8e6608662e178eb52b8766edc5a9a7  phase08_1_diagnostic_activation.yaml
a5e91d2132b3dacccedc24aba13bdacd9ef5ba4ec7c8ae7b69ced6eadaf47d72  phase08_v2_activation.yaml
```

The activation-contract hash at committed M5 HEAD `8ca59d1` remains separately
recorded as
`e787e226d3de4ef19e93867fcb148164d8c306dd7e0264d0354c519793ec3590`;
the terminal M7 document is an additive retained-outcome amendment.

Context, shell, and required-document validation:

```bash
bash -n \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh
timeout 120s \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh \
  08 implement
timeout 120s \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh \
  08 implement --strict-history
timeout 120s \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh \
  09 plan
timeout 60s \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_required_docs.sh
```

Results:

```text
Phase 08 implement context is complete.
Phase 08 implement context is complete.
Phase 09 plan context is complete.
All Phase 00 audit documents exist.
```

The Phase 09 smoke proves the new required
`handoffs/phase_08_1_handoff.md` navigation boundary. It does not authorize
Phase 09.

M7 path, historical-evidence, tag, process, and diff checks:

```bash
python3 - <<'PY'
import pathlib
import re
import subprocess

files = subprocess.check_output(
    ['git', 'ls-files', '-m', '-o', '--exclude-standard'],
    text=True,
).splitlines()
errors = []
checked = 0
for name in files:
    path = pathlib.Path(name)
    if path.suffix.lower() != '.md' or not path.is_file():
        continue
    for match in re.finditer(
        r'(?<!!)\[[^]]+\]\(([^)]+)\)',
        path.read_text(encoding='utf-8'),
    ):
        target = match.group(1).strip().strip('<>')
        if not target or target.startswith(
            ('#', 'http://', 'https://', 'mailto:')
        ):
            continue
        target = target.split('#', 1)[0]
        resolved = (
            pathlib.Path(target)
            if target.startswith('/')
            else path.parent / target
        )
        checked += 1
        if not resolved.exists():
            errors.append(f'{path}: {target}')
if errors:
    raise SystemExit('missing Markdown targets:\n' + '\n'.join(errors))
print(f'M7 Markdown links passed: {checked} local targets')
PY
if git diff --name-only |
  rg -q '(^|/)(phase_08_handoff\.md|phase_08_v1|phase_08_v2|phase08_v2_)'
then
  exit 1
fi
if git tag --list 'gesc-gaussian-simulation-ready*' | rg -q .
then
  exit 1
fi
if pgrep -af \
  '[g]zserver|[g]zclient|[g]azebo|ros2 bag [r]ecord|[r]ecord_run|[r]un_scenario'
then
  exit 1
fi
git diff --check
```

Results: `M7 Markdown links passed: 5 local targets`; historical v1/v2 evidence
and the historical `phase_08_handoff.md` were unchanged; no simulation-ready
tag existed; no Gazebo, recorder, bag-record, or scenario-runner process
existed; and `git diff --check` passed.

M7 explicitly did not execute a new probe, replacement, matrix, tuning,
parameter freeze, holdout, unique validation denominator, reproducibility
repeat, Wilson interval, tag, GUI, Phase 09 action, or physical command.

Terminal checkpoint:

```bash
timeout 120s \
  DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/checkpoint_phase.sh 08
git diff --check
```

Result: the checkpoint passed at clean M6 base `c959ce1` and captured the
closed M7 status and full precommit diff. `git diff --check` passed again.
