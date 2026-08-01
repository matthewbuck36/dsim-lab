# Physical Experiment Readiness Checklist

This checklist distinguishes safe snapshot integration from later live
physical motion. Phase 09 snapshot planning, source integration, and static
qualification do not require a broad `simulation_ready` tag. They do not
authorize the robot to move.

Physical motion requires every applicable live item below, an available robot,
a reviewed Phase 09 handoff, and separate explicit user authorization. The
initial claim is limited to the two selected, demonstrated, local-first,
two-source layouts; it is not broad field readiness.

## Snapshot integration boundary

- [ ] Phase 08.8 final report, handoff, status, and checkpoint are present.
- [ ] Selected simulation evidence is recorded without relabeling failures.
- [ ] Snapshot Pi home is resolved as
  `/home/mattb/physical_TB3_files_snapshot/pi`.
- [ ] Snapshot ROS source is resolved as
  `/home/mattb/physical_TB3_files_snapshot/pi/ros2_ws/src`.
- [ ] The snapshot is confirmed not to be Git-controlled.
- [ ] A recoverable pre-edit source backup exists.
- [ ] A complete source inventory and SHA-256 baseline exist.
- [ ] `/home/mattb/tb3-pi` is not mounted or accessed during snapshot work.
- [ ] Generated build/install/log/cache/editor/runtime content is excluded.

## Shared software and interfaces

- [ ] Physical launch uses the same shared algorithm owners as simulation.
- [ ] No parallel controller, supervisor, recorder, or validator was added.
- [ ] The existing physical `/cmd_vel` owner remains unique.
- [ ] Legacy and selected counted-source profiles remain selectable.
- [ ] Cost sign, units, canonical topics, and message semantics are unchanged.
- [ ] Photoresistor raw cost is timestamped on the canonical interface.
- [ ] Wheel odometry is available on the canonical pose interface.
- [ ] Required IMU data is available without adding global localization.
- [ ] No GPS, Vicon, source position/role/intensity, room map, or evaluator
  coordinate enters controller logic.
- [ ] Vicon, if later recorded, is evaluation-only and cannot affect motion or
  stopping.
- [ ] Required-topic static/preflight validation passes where host-compatible.
- [ ] Every Pi-only or hardware-only check is explicitly deferred, not passed.

## Selected algorithm behavior

- [ ] Known source count is configured explicitly.
- [ ] Candidate comparison uses complete-rotation raw cost and uncertainty.
- [ ] Exactly one adaptive typed Gaussian fill is allowed for two sources.
- [ ] Gaussian memory remains active after local recovery.
- [ ] Affine/approach assistance is temporary and clears after recovery.
- [ ] Direct and supervisor-assisted escape paths retain one motion owner.
- [ ] Revisits associated with the active fill resume search.
- [ ] No automatic physical coordinate-distance arrival stop exists.
- [ ] Physical arrival remains manual operator `Ctrl+C`.

## Calibration and live sensing

- [ ] The robot and Pi are physically available.
- [ ] The live Pi source is backed up before transfer.
- [ ] Snapshot-to-Pi source/configuration transfer manifest is reviewed.
- [ ] Stationary photoresistor voltage/range/polarity calibration is complete.
- [ ] Ambient light and lamp-response measurements are recorded.
- [ ] Sensor rotation timing and complete-window sampling are verified.
- [ ] Wheel odometry timestamp, sign, scale, and freshness are verified.
- [ ] IMU timestamp, orientation convention, and freshness are verified.
- [ ] Source-count configuration and selected two-light layout are frozen.
- [ ] Lamp positions/intensities are recorded for evaluation only and are not
  exposed to the controller.

## Safety and operator control

- [ ] The test region is open, obstacle-free, and operator-managed.
- [ ] Conservative linear and angular velocity limits are frozen.
- [ ] No wall, collision, or autonomous obstacle-avoidance claim is required.
- [ ] Readiness remains false until every live prerequisite passes.
- [ ] Invalid/stale photoresistor input produces a zero command.
- [ ] Invalid/stale odometry or required IMU input produces a zero command.
- [ ] Controller/supervisor fault produces a zero command.
- [ ] `Ctrl+C` shutdown ordering is verified: readiness false, stop, final
  zero, recording finalization, and scoped cleanup.
- [ ] A separate emergency-stop method is tested before floor motion.
- [ ] An observer remains close enough to stop the robot throughout the run.
- [ ] Separate explicit user authorization for physical motion is recorded.

## Recording

- [ ] The existing Phase 05 `record_run`/`validate_run` workflow is reused.
- [ ] Run ID and immutable configuration metadata are created before motion.
- [ ] Rosbag and console capture start before readiness can become true.
- [ ] Required topics publish with one expected owner each.
- [ ] Final readiness false and final zero are recorded.
- [ ] Bag completeness and SQLite integrity pass.
- [ ] Run notes distinguish operator stop from controller failure.

## Authorized progression after motion approval

- [ ] Stationary sensor and recording validation.
- [ ] Wheels-lifted or otherwise nontranslating command-path validation, if
  approved and mechanically safe.
- [ ] Low-speed one-source commissioning, reported as calibration rather than
  local-recovery evidence.
- [ ] One low-speed local-fill-and-escape trial.
- [ ] Selected primary two-source layout corresponding to the demonstrated
  simulator `400/1600` response condition.
- [ ] Selected secondary two-source layout only after the primary passes.
- [ ] Stop after any safety, ownership, stale-input, recording, final-zero, or
  cleanup failure.

Arbitrary intensity/layout matrices, three lights, boundaries, walls,
obstacles, and broad robustness remain future work unless separately planned
and authorized.
