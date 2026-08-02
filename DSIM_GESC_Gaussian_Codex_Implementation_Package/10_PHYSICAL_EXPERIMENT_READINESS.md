# Physical Experiment Readiness Checklist

This checklist distinguishes safe snapshot integration from later live
physical motion. Phase 09 snapshot planning, source integration, and static
qualification do not require a broad `simulation_ready` tag. They do not
authorize the robot to move.

Physical motion requires every applicable live item below, an available robot,
a reviewed Phase 09 handoff, and separate explicit user authorization. The
initial claim is limited to the two selected, demonstrated, local-first,
two-source layouts; it is not broad field readiness.

Historical M8A evidence: the reviewed 51-path source/configuration transfer and
rollback backup passed, with exact M8A snapshot-to-Pi parity and legacy
selection preserved. Current M8B snapshot implementation, host-side
qualification, and reviewed real-Pi source sync also passed. The M8B rollback
backup is `/home/mattb/tb3-pi/phase09_backups/20260802T031409Z_m8b`; snapshot
and Pi match `345/345` regular-file hashes and `432/432` inventory entries.
The separate on-Pi build/installed-static gate and every live Vicon, sensing,
safety, calibration, mechanism, and motion checkbox below remain unverified. See
`docs/codex/gesc_gaussian/validation/phase_09_pi_transfer_receipt.md` and the
current Phase 09 status. Nothing in this checklist is `PHYSICAL READY`.

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
- [ ] Initial M0-M7 snapshot-only evidence confirms
  `/home/mattb/tb3-pi` was not mounted or accessed during that historical
  boundary; later source transfers have separate receipts and authorization.
- [ ] Generated build/install/log/cache/editor/runtime content is excluded.

## Shared software and interfaces

- [ ] Physical launch uses the same shared algorithm owners as simulation.
- [ ] No parallel controller, supervisor, recorder, or validator was added.
- [ ] The existing physical `/cmd_vel` owner remains unique.
- [ ] Legacy and selected counted-source profiles remain selectable.
- [ ] Cost sign, units, canonical topics, and message semantics are unchanged.
- [ ] Photoresistor raw cost is timestamped on the canonical interface.
- [ ] Wheel/IMU-backed `/odom` is available as the sole algorithm pose
  interface.
- [ ] Required IMU data is available without adding global localization.
- [ ] No GPS, Vicon, source position/role/intensity, room map, or evaluator
  coordinate enters controller logic.
- [ ] Required Vicon evaluation pose is available only on
  `/gesc_gaussian/evaluation/vicon_pose` as `PoseStamped` and cannot affect
  motion, fill placement, ranking, or stopping.
- [ ] Required Vicon status on `/gesc_gaussian/evaluation/vicon_status` proves
  the reviewed subject/segment, server-script hash, protocol/session,
  advancing sequence/Tracker frame, nonocclusion, freshness, and run coverage.
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
- [ ] The separate bounded on-Pi build/source and installed-static gate passes
  without starting a ROS graph, opening serial/GPIO, or commanding an actuator.
- [ ] Mutable calibration and primary/secondary metadata copies exist under
  `${XDG_CONFIG_HOME:-$HOME/.config}/dsim-lab/phase09`; installed inert
  templates and the frozen selected profile remain unchanged.
- [ ] `--stationary-preflight` passes while calibration is uncalibrated,
  readiness remains false, and neither the base nor rotating frame actuates.
- [ ] A reviewer runs `--approve-stationary RUN_DIR --reviewer NAME` only after
  reviewing the retained PASS, using the exact same site-metadata bytes and
  hash-coupled evidence.
- [ ] Stationary photoresistor voltage/range/polarity calibration is complete.
- [ ] Ambient light and lamp-response measurements are recorded.
- [ ] Sensor rotation timing and complete-window sampling are verified.
- [ ] Wheel odometry timestamp, sign, scale, and freshness are verified.
- [ ] IMU timestamp, orientation convention, and freshness are verified.
- [ ] Source-count configuration and selected two-light layout are frozen.
- [ ] Lamp positions/intensities are recorded for evaluation only and are not
  exposed to the controller.
- [ ] The Windows Vicon evidence server and Pi evidence client use the reviewed
  endpoint, protocol, subject, segment, and exact server-script SHA-256.

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
- [ ] A mechanically safe nontranslating command/final-zero rehearsal passes
  only after the independent emergency stop is tested.
- [ ] The assigned observer remains close enough to stop the robot throughout
  the run and is distinct from the assigned operator when required by the lab
  procedure.
- [ ] Separate explicit user authorization for physical motion is recorded.

## Recording

- [ ] The existing Phase 05 `record_run`/`validate_run` workflow is reused.
- [ ] Run ID and immutable configuration metadata are created before motion.
- [ ] Rosbag and console capture start before readiness can become true.
- [ ] Required topics publish with one expected owner each.
- [ ] Wheel/IMU odometry and both required evaluation-only Vicon streams are
  captured in the same sqlite3 bag with unambiguous live terminal labels.
- [ ] Final readiness false and final zero are recorded.
- [ ] Bag completeness and SQLite integrity pass.
- [ ] Run notes distinguish operator stop from controller failure.

## Strict M9 progression after each required authorization

Do not reorder or collapse these gates:

1. [ ] Complete the separate on-Pi build/installed-static gate; it is currently
   `NOT RUN`.
2. [ ] Create the mutable calibration and primary/secondary metadata copies
   under the exact XDG/home path above.
3. [ ] Run `gesc_gaussian_two_source_voltage.bash --stationary-preflight`
   while uncalibrated, readiness false, and no actuation is possible.
4. [ ] Review the retained PASS and run
   `gesc_gaussian_two_source_voltage.bash --approve-stationary RUN_DIR
   --reviewer NAME` against the same metadata bytes.
5. [ ] Test the independent emergency stop, then complete the separately
   authorized safe nontranslating/final-zero rehearsal.
6. [ ] Complete and freeze the real stationary photoresistor calibration.
7. [ ] Run `gesc_gaussian_two_source_voltage.bash --check-only`; treat it as a
   configuration/static audit, not a live-safety pass.
8. [ ] Invoke the bare `gesc_gaussian_two_source_voltage.bash` for the primary
   scenario, verify the assigned operator and observer, and type `RUN` only
   after all displayed live conditions are true.

The bare wrapper is the eventual normal primary entry point. Consider the
selected secondary scenario only after the primary is fully accepted and a
separate progression decision is reviewed. Stop after any safety, ownership,
Vicon identity/session/freshness, stale-input, recording, final-zero,
emergency-stop, or cleanup failure.

Arbitrary intensity/layout matrices, three lights, boundaries, walls,
obstacles, and broad robustness remain future work unless separately planned
and authorized.
