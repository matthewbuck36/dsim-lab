# M0 isolated simulation-source qualification

Verified on 2026-09-08 (America/Los_Angeles), baseline `3369cfc`.
No Gazebo or physical graph was launched. The selected source packages built
successfully and their inherited detector tests passed. This is environment
and baseline qualification, not V2 algorithm acceptance.

## Commands and retained logs

From the repository root:

```bash
mkdir -p /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial
source /opt/ros/humble/setup.bash
timeout 600s colcon --log-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/log build --base-paths ros2_ws/src --packages-select ros_esc_interfaces ros_esc turtlebot3_rotating_sensor --build-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/build --install-base /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install --symlink-install --event-handlers console_cohesion+ > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/build.log 2>&1
```

Exit 0: `3 packages finished [15.8s]`. The build/install/log directories are
outside Git. Source changes and new interfaces require an incremental rebuild;
the symlink install is not an immutable code snapshot.

```bash
source /opt/ros/humble/setup.bash
source /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash
timeout 120s python3 -m pytest -q ros2_ws/src/ros_esc/test/test_convergence_detector_policy.py > /home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/detector_baseline_tests.log 2>&1
```

Exit 0: `13 passed in 0.28s`.

## Import verification

In the sourced isolated overlay, `Path(module.__file__).resolve()` was checked
against `ros2_ws/src/ros_esc/<module dotted path>.py` for the following modules;
all three assertions passed. Source SHA-256 at this qualification:

| Module | SHA-256 |
| --- | --- |
| `ros_esc.convergence_detector_node.convergence_detector_node_script` | `97fe1d703e86357dbf5dd7879f43b00be7d50f5f5b5525869b148378af88b903` |
| `ros_esc.scenario_runner.run_scenario` | `d842015ad298ca76dc7cc40fdef16aa1685f82bdea0467248c71f4476f225f0a` |
| `ros_esc.scenario_runner.scenario_schema` | `0987d7cbe9faf46913846e7c882e79bbc7d7724f1a9a2392f2d8de0d0ed4f5ee` |

The normal workspace install was found stale during the independent baseline
inventory. Qualify V2 against this freshly built overlay and source provenance;
do not treat the old normal install as the implementation under test.
