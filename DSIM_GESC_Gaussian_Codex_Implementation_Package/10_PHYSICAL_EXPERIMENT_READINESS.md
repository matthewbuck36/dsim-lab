# Physical Experiment Readiness Checklist

No physical motion until every applicable item is checked.

## Repository and software

- [ ] Simulation-ready Git tag exists.
- [ ] Working tree is clean.
- [ ] Physical launch uses the same shared algorithm nodes as Gazebo.
- [ ] Vicon/physical adapters publish canonical topics.
- [ ] Legacy and robust profiles are selectable.
- [ ] Parameter file is frozen and archived.
- [ ] Required-topic preflight passes.
- [ ] Disk-space preflight passes.

## Sensor and source

- [ ] Raw light sensor is visible and timestamped.
- [ ] Raw minimization cost is visible.
- [ ] Source-score calibration is completed.
- [ ] Goal threshold and dwell are documented.
- [ ] New lamp levels and positions are recorded.
- [ ] Ambient light conditions are noted.
- [ ] Window shades/room-light controls are in the intended configuration.

## Safety

- [ ] Zero command is published on shutdown.
- [ ] Zero command is published on stale Vicon.
- [ ] Zero command is published on stale/invalid sensor.
- [ ] Velocity and angular-rate limits are conservative.
- [ ] Emergency stop procedure is tested.
- [ ] Room bounds and center are verified.
- [ ] Wall margin is verified.
- [ ] An observer can stop the robot.

## Recording

- [ ] Run ID created.
- [ ] Metadata generated.
- [ ] Rosbag starts before motion.
- [ ] All required topics have messages.
- [ ] Console log is captured.
- [ ] Final zero command is recorded.
- [ ] Bag completeness report passes.

## Experimental progression

- [ ] Stationary calibration.
- [ ] One-source low-speed test.
- [ ] One local-basin escape.
- [ ] Recenter test.
- [ ] Large-separation two-source test.
- [ ] Approved progression to matrix.
