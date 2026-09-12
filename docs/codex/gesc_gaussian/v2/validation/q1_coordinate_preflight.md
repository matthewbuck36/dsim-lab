# Q1 nonzero-spawn coordinate preflight — 2026-09-09

Result: the selected source/plugin contract preserves world x/y and world yaw
in `/odom` at nonzero spawn positions. Frozen world-coordinate masks therefore
need no spawn-offset transform under this contract. This is a read-only source
and installed-package preflight, not a live spawn/recording result. Q1 remains
prospective; no Gazebo, model evaluation, package installation, physical action,
or runtime-source change occurred.

## Installed plugin and coordinate semantics

The isolated V2 overlay resolves `gazebo_plugins` and `gazebo_ros` to
`/opt/ros/humble`; its selected robot URDF resolves to the current repository
file. Installed versions are:

| Package | Installed version |
| --- | --- |
| `ros-humble-gazebo-plugins` | `3.9.0-1jammy.20260804.195543` |
| `ros-humble-gazebo-ros` | `3.9.0-1jammy.20260726.134039` |
| `ros-humble-gazebo-ros-pkgs` | `3.9.0-1jammy.20260804.212537` |
| `gazebo`, `libgazebo11` | `11.10.2+dfsg-1` |

`turtlebot3_rotating_sensor.urdf:424–455` selects
`libgazebo_ros_diff_drive.so`, publishes odometry at 30 Hz, names `odom` and
`base_footprint`, and omits `odometry_source`. The installed header declares the
plugin but does not contain its implementation. Matching official 3.9.0 source
defines `WORLD=1` and defaults the omitted selector to 1. Its
`UpdateOdometryWorld()` directly copies `model_->WorldPose()` position and
quaternion; it subtracts no initial pose. Publication labels that payload with
the configured frame names. Linear twist is separately rotated into the child
frame; that does not change pose coordinates. See the official
[3.9.0 diff-drive implementation](https://github.com/ros-simulation/gazebo_ros_pkgs/blob/3.9.0/gazebo_plugins/src/gazebo_ros_diff_drive.cpp#L338),
especially lines 338–342, 563–575 and 605–625. Local Gazebo
`/usr/include/gazebo-11/gazebo/physics/Entity.hh:100–105` identifies `WorldPose()`
as the absolute entity pose. The installed library exports the corresponding
`UpdateOdometryWorld()` symbol; `dpkg -V ros-humble-gazebo-plugins` reports no
package-file mismatch.

The launch passes requested x/y/yaw to `spawn_entity.py` without a reference
frame override (`gazebo.launch.xml:377–393`). Installed
`/opt/ros/humble/lib/gazebo_ros/spawn_entity.py:67,212–221,282–283` supplies the
empty reference frame and requested pose. Installed
`/opt/ros/humble/share/gazebo_msgs/srv/SpawnEntity.srv` specifies that an empty
reference frame uses Gazebo world. The selected URDF's root is `base_footprint`;
its fixed base joint adds only 0.010 m in z, with no x/y/yaw offset.

Thus initial `/odom` x/y and quaternion yaw should match requested world spawn
x/y/yaw (yaw modulo 2π), subject to actual motion/settling before sampling. This
conclusion follows coordinate operations, not the string `odom`.

## Sensor, cost, and mask paths

- `scenario_runner/run_scenario.py:219–224` passes the resolved start directly
  into launch x/y/yaw. The selected Q1 proposal uses `/odom` with zero introduced
  delay. `gazebo.launch.xml:506–516` gives the sensor owner `/odom` directly.
- `sensor_pose_node_script.py:149–167,249–267` copies odometry position and
  quaternion, then publishes the configured transform. Its existing
  `Transform_Odom_To_Sensor_Pose.transform_output()` multiplies odometry pose,
  rotating joint pose, and sensor mount; it never subtracts a spawn origin.
  The selected JSON has joint x/y 0, joint z 0.355 m, sensor x 0.18 m and z 0.015 m.
  For a level robot, sensor world position is
  `(x + 0.18 cos(ψ+φ), y + 0.18 sin(ψ+φ))`, where ψ is base world yaw and φ
  the measured joint angle. Sensor world orientation includes both rotations.
- `cost_function_node_script.py:447–469` passes that matrix to the selected
  `Multi_Light_Source_Cost`. Its `_source_radius_beta()` at
  `cost_function_objects.py:487–513` subtracts sensor x/y from configured source
  x/y and uses the matrix's sensor x-axis. These are the same source coordinates
  passed by the runner/launch; no TF lookup or origin correction intervenes.
- The frozen geometry evaluator's `_sensor_transform()` at
  `scenario_runner/aggregate_field_truth.py:479–504` places base x/y directly in
  the translation and sweeps sensor world angle with the same mount. Its masks
  classify **base** world x/y, not the displaced sensor point. Therefore apply
  those masks to selected odometry x/y directly when the recorded model/source/
  geometry bindings match. Preserve annular holes and all temporal label gates.

The proposed nonzero residence starts and confirmation approach start in
`qualification_release_review.md:300–310` are compatible with this mapping.
No retrospective offset fitting or shifting of frozen masks is justified.

## Reproduction and retained identity

Read-only checks, from `/home/mattb/dsim-lab`:

```bash
timeout 30s docs/DSIM_GESC_Gaussian_Codex_Implementation_Package/tools/validate_phase_context.sh v2 plan
dpkg-query -W -f='${Package}\t${Version}\n' ros-humble-gazebo-plugins ros-humble-gazebo-ros ros-humble-gazebo-ros-pkgs gazebo libgazebo11
dpkg -V ros-humble-gazebo-plugins
nm -DC /opt/ros/humble/lib/libgazebo_ros_diff_drive.so | rg 'UpdateOdometryWorld|PublishOdometryMsg'
```

The context check returned `Phase v2 plan context is complete.` All above
commands returned 0. A bounded 30 s Python/ament inspection after sourcing
`/opt/ros/humble/setup.bash` and the isolated
`/home/mattb/Experiments/GESC-Gaussian/v2/builds/initial/install/local_setup.bash`
confirmed package prefixes and byte equality of the selected/source URDF.
SHA-256 identities inspected:

| Input | SHA-256 |
| --- | --- |
| Installed diff-drive `.so` | `fe11171946bec08186777005aa7321d223bf7d97bc417897965dfd5b051e1b9e` |
| Installed diff-drive header | `8e66ea1471a6c8dea72e01272bbab3e0db7dff5b371ca051f5c66eb8d8d0263a` |
| Installed `spawn_entity.py` | `d255171750600a025d2fb5b1e2a641a95b55c4668a1a25af0455cc9b63b9d4ee` |
| Selected/source robot URDF | `6a49d4ea96315e9d81cfddd30ad2ab9e1210c809af1e301f188f861760ebf425` |
| Sensor transform JSON | `8fcfb1e2c9e7a8d1463936ab525c2a1533b60bc0548391ca8cf3b3941ffc99b5` |
| Transform object source | `69d9e01443f40a24bdf6ca359fe6619236ded11bd739fe53a53bfb541dfd1fc0` |
| Sensor node source | `027c2633274ec1f58b1b70045b0e7ddef4444b35fab9226bde63fd0f86e44f7e` |
| Cost node source | `2bccf998b56967e91ea090d3aad56e55273abe5243f047cfdf867581130be29e` |
| Cost model source | `b54cf0baa3e068c471c424b2f629d3fa896c30187040769ca27808d5c7f77886` |
| Geometry evaluator source | `b9b0e8b483dc4d7ac2fd392b7ef7ed57a8cb95ebb600124dc5d964b4cf0190c5` |

The source matches the installed package's declared upstream version; this is
not a reproducible binary-build proof or observation of a loaded live library.
The prospective run must still retain selected assets/library identity and
check an early qualified pose against requested spawn x/y/yaw before treating
world masks as run evidence. A mismatching pose/asset binding remains an input
qualification failure, not permission to infer an offset from detector outcomes.
