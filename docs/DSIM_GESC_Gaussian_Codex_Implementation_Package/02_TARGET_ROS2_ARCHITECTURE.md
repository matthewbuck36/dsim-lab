# Target ROS 2 Architecture

The repository's actual package and node names are discovered in Phase 00. This document defines behavior and boundaries, not guessed filenames.

## Architecture principle

Simulation and physical runs must use the same algorithm graph.

Only adapters differ:

```text
Gazebo adapters                           Physical adapters
----------------                          -----------------
simulated light field                     photoresistor/light sensor
simulated odometry                        Vicon and/or onboard odometry
simulated clock                           wall clock / ROS system time
            \                              /
             \                            /
              canonical sensor + pose topics
                          |
                          v
                 shared GESC pipeline
                          |
                          v
                shared supervisor/state machine
                          |
                          v
                 canonical velocity command
                          |
              simulation or hardware adapter
```

## Required logical components

These may already exist as nodes or classes. Reuse them.

### 1. Sensor/cost adapter

Responsibilities:

- Receive raw sensor data.
- Preserve the raw value.
- Compute or expose the existing minimization cost.
- Compute a calibrated source score.
- Publish validity and timestamp information.
- Never change cost sign silently.

### 2. Gaussian fill manager

Responsibilities:

- Maintain the active fill registry.
- Store fill centers, covariance, amplitude, support radius, confidence, and history.
- Evaluate the total repulsion contribution.
- Merge overlapping fill candidates.
- Freeze the active escape fill during an escape attempt.
- Publish arrays and events.

### 3. Basin estimator and fill designer

Responsibilities:

- Buffer recent synchronized pose/cost samples.
- Robustly estimate basin center, covariance, depth, and curvature.
- Generate an adaptive fill.
- Validate the fitted augmented model for residual minima.
- Escalate within configured limits.
- Return diagnostics and confidence.

### 4. GESC algorithm

Responsibilities:

- Preserve existing GESC behavior.
- Accept the selected augmented cost.
- Publish internal estimates needed to reconstruct the controller.
- Publish unsaturated commands.
- Avoid mixing state-machine logic into the core estimator unless the repository already uses that pattern.

### 5. Supervisor/state machine

Responsibilities:

- Own algorithm mode and transitions.
- Set `w_s`, `w_g`, and `w_a`.
- Verify goal condition.
- Trigger fill design.
- Monitor escape progress and stall.
- Activate assisted escape.
- Trigger recentering.
- Enforce timeouts and failsafe.
- Publish final commands and state events.

### 6. Recenter/boundary safety component

Responsibilities:

- Use known room bounds and center.
- Prefer an existing planner if one is already integrated.
- Otherwise use a simple bounded waypoint controller.
- Maintain wall margin.
- Reject unsafe directional assistance.
- Stop on invalid pose.

### 7. Experiment recorder

Responsibilities:

- Validate required topics.
- Start rosbag2.
- Generate run metadata.
- Capture console output separately.
- Stop cleanly.
- Produce a run-completeness report.

### 8. Analysis pipeline

Responsibilities:

- Read bag data.
- Synchronize topics.
- Export tables.
- Generate standard plots.
- Calculate metrics.
- Mark incomplete runs.

## Compatibility requirements

- Add an explicit `legacy` profile that reproduces current behavior.
- Add a `robust_gaussian_v1` profile for the new behavior.
- Do not rename public topics without a compatibility remap or bridge.
- Do not duplicate a current Gaussian node merely to avoid understanding it.
- Do not create separate algorithm copies for simulation and physical use.
- New parameters must live in existing YAML/config conventions.
- New messages must go into the existing interface package, if present.
- If no interface package exists, create one interface-only package beside the existing packages.

## Addendum

Reuse or extend an existing node when that node already owns the responsibility. A new node may be created only when
the repository audit shows that no existing node is an appropriate owner, the feature has a distinct ROS responsibility
and interface, and the new node follows the repository’s established architecture. Do not create duplicate,
simulation-specific, physical-specific, or replacement implementations of existing algorithm behavior.
