# Q1 source and acquisition preflight

Status: source/configuration/frontend checks PASS; checkpoint and explicit
dispatch receipt are the final acquisition prerequisites. This file alone is
not a dispatch release.
No Q1 run or numerical reference has been evaluated at this boundary.

## Existing-owner checks

- Observation policy:25 focused and270 combined checks pass;
  `q1_observation_policy.md` records default-off behavior, both detector kinds,
  no consumed candidate IDs, preserved safety/recovery and final zero.
- Simulated duration:129 checks pass in4.10s, `q1_sim_duration.md`. The
 125s observation starts at the first successful ready clock; paused/rollback
  clocks, early target/bag exit and cleanup have explicit outcomes.
- Runner wiring:76 checks pass in1.09s, `q1_runner_contract.md`.
- Acquisition purpose/safety:52 final focused checks pass in2.53s,
  `q1_acquisition_safety.md`. The earlier broad attempt printed446 passes,
  one Gazebo opt-in skip and one failure but exited124; it is not a clean broad
  pass. The sole failed legacy execution-shape assertion is corrected and
  explicitly included in the52-check final run.
- Typed inputs/references:153 checks pass in20.92s,
  `q1_direction_adapter.md`. This includes the unchanged100 numerical/replay
  regressions and exact planned-run linkage. No selected field was evaluated.

Each owner document retains the exact source/log hashes and failed attempts.
The finite label/neighborhood helper passed141 combined checks in5.97s;
its final narrow input-reader change passed29 helper checks in3.46s.
All197 Q1 checks then passed together in23.96s, exit0, no warnings, using:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
ROS_DOMAIN_ID=192 PYTHONPATH="ros2_ws/src/ros_esc:ros2_ws/src/ros_esc/test:extremum-seeking/src${PYTHONPATH:+:$PYTHONPATH}" timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_q1_*.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_integrated_v1.log 2>&1
```

Log SHA256: `426fd014b8518a437946d6641b993180b41778747c423d58fb00370e153c74ef`.
The final acquisition-event fixture permits a detector-only confirmation while
rejecting actual fill/goal/safety events;45 tests pass in2.41s in its focused
v3 check, also included in the197-check integration.

## Build and installed assets

From the repository root, base ROS only:

```bash
source /opt/ros/humble/setup.bash
timeout 180s colcon --log-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/log build --base-paths ros2_ws/src --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor --build-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/build --install-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install --symlink-install --event-handlers console_cohesion+ > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_build_v1.log 2>&1
```

Result:three packages finished in2.37s, exit0. This incremental symlink build
installs the Q1 scenario and direct rcl_interfaces dependency. Later Python
owner edits resolve through the same source symlinks and are separately tested.

After sourcing its `install/local_setup.bash`, a bounded30s Python check used
`ament_index_python.packages.get_package_share_directory` and byte equality
against checkout source for the launch XML, robot URDF, empty world, Q1 scenario,
recorder topic manifest and QoS file. Imports of runner, recorder and Q1 helper
resolve inside this checkout. Exact installed/source paths and SHA256 values
are retained in `builds/initial/q1_installed_binding_v1.json` under the external
V2 artifact root. This confirms selected assets, not actual loaded runtime.
The coordinate-specific plugin/source evidence is `q1_coordinate_preflight.md`.

`timeout 5s xdpyinfo -display :0` succeeds against X.Org display:0.
`pgrep -af 'gzserver|gzclient|ros2 launch|ros_esc/record_run'` found no running
matching processes at the preflight check. No existing Gazebo process was killed.
The first recorded case remains visible; later cases use batch mode.

## Frozen population and orchestration

`q1_primary_shadow_v1.yaml` resolves exactly four cases, seeds26090911–26090914,
with no unsupported case. It uses schema2 and explicit
`purpose: qualification_observation`; all selected primary controls are retained
in the frozen profile. Safety and unexpected intervention events are forbidden
inside the recorded ready interval. Existing formal schemas remain unchanged.

The fresh seed scan read923 existing simulation metadata/scenario-result files,
6,421,403bytes, and found no occurrence of any selected seed. Its exact root,
file-list digest and result are retained in `builds/initial/q1_seed_preflight_v1.json`.
This supplements the broader static proposal audit and does not inspect old
held-out trajectories or reevaluate their scientific outcomes.

The three fixed study scripts under `../tools/` compose existing owners:

- `freeze_q1_contract.py`: exact sources/configuration/geometry receipts,
  planned starts/run identities and resolved commands; no dispatch/model calls.
- `acquire_q1.py`: existing single-case runner, recording/cleanup/safety checks,
  first pre-ready pose/spawn comparison and captured configuration binding;
  stop dispatch on any acquisition failure. No scientific selection.
- `evaluate_q1.py`: one label/nomination job, opening confirmation only after
  a frozen passing discovery choice; one separate48-slot reference job.

They add no controller, recorder, bag loader or numerical model. The contract
binds their exact source. Temporary recorder metadata paths are declared command
templates; the actual retained launch argv and resolved scenario must equal the
frozen planned values. Existing output paths/IDs are never overwritten.

## First freeze withheld by the actual launch frontend

The first pure source/geometry freeze completed without field calculations:
532 source files and2869 geometry receipts, with full preserved numerical
lineage verification. Its contract remains unchanged at
`qualification/q1_primary_shadow_v1/preflight/contract.json`, SHA256
`0921e90a3d705fe1ff46abcd47f4116b559c9f542d0dd59ad7cc8d418c5a1e05`.
The explicit domain guard was checked using ROS_DOMAIN_ID190: acquisition
rejected it before output creation or ROS work, as intended.

The following actual frontend check then failed, exit1:

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
ROS_DOMAIN_ID=191 timeout 30s ros2 launch turtlebot3_rotating_sensor gazebo.launch.xml --show-args > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_launch_parse_v1.log 2>&1
```

Humble tokenizes static command fragments before resolving substitutions;
V2 quotes crossing a substitution produced `ValueError: No closing quotation`.
The XML parser and old substitute-then-shlex fixtures did not represent that
behavior. No nodes or Gazebo started. The first contract is explicitly
UNRELEASED_PREFLIGHT_FAILURE in `preflight/contract_v1_unreleased.json`.
The bounded correction is described in `../q1_plan.md`; replacement freeze,
frontend argv checks and checkpoint must precede release. Acquisition and
evaluation now require an explicit --contract file so the old receipt can
remain at its original path. Inputs, tuning and study population are unchanged.


## Corrected frontend and replacement source freeze

The existing XML now uses atomic CLI substitutions and independently closed
static quote fragments for YAML single-quoted string parameters. Real Humble
frontend/RCL checks pass96 tests in9.05s; final installed --show-args exits0.
See `q1_launch_frontend.md` for the exact valid descriptor grammar and all
retained failed attempts. Algorithm settings and scientific rules are unchanged.
The final installed/source asset recheck is `q1_installed_binding_v3.json`.

Replacement pure freeze, exit0, after sourcing the same overlay:

```bash
ROS_DOMAIN_ID=191 timeout 90s python3 docs/codex/gesc_gaussian/v2/tools/freeze_q1_contract.py --output /home/mattb/Experiments/GESC-Gaussian/v2/qualification/q1_primary_shadow_v1/preflight/contract_v2.json > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/q1_contract_freeze_v2.log 2>&1
```

It binds533 source/configuration files and2869 geometry receipts, four exact
reserved cases, and verifies the preserved numerical chain without new field
calculations. Contract SHA256:
`570b335c95b034c9da6d350f73fa20c9b7d6be9c8a77b8c14bf2ba714626f1bf`.
The old contract and unreleased-failure receipt remain at their original paths.
All three orchestration scripts compile. Context validation and diff checks pass.
