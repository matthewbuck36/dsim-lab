# Consolidated Meeting Decisions and Engineering Hypotheses

## Direct research requirements from Dr. Nili

- Focus the project on making the GESC + Gaussian method robust.
- Existing physical demonstration may be shown as not yet robust.
- Treat cost value, Gaussian repulsion, and affine contribution as independently switchable.
- The raw sensor cost does not need to remain active during escape.
- Determine switching from extensive Gazebo tests.
- Do not continue physical experiments until Gazebo behavior is robust.
- Robustness must cover different local-minimum depths, source levels, source counts, and close local minima.
- Escaping after many repeated circles is not acceptable.
- Acoustic reflective environments are a future motivation; current experiments are light based.

## Tentative ideas to test

The transcript explicitly gives implementation freedom and presents these as
hypotheses rather than mandatory architecture:

- Try pure repulsion to leave a local basin.
- Reactivate raw cost after leaving the undesired attraction region.
- Keep useful previous repulsion active to reduce revisits.
- Consider returning to the center in a bounded indoor environment.
- Consider keeping prior repulsion active during recentering.
- Test a broader basin-scale fill when narrow fills leave residual minima.

Simulation evidence may replace or disable one of these policies before formal
parameter/code freeze without changing the research objective. Safety,
observability, shared simulation/physical semantics, and independently
switchable contributions remain invariant.

## Patrick data-collection discussion

- Record raw sensor/cost and augmented cost.
- Record inputs and outputs of every software block.
- Record commands, switching times, and controller modes.
- Record Gaussian parameters and timestamps.
- Publish values as ROS messages.
- Simulation and physical runs should share the same algorithm topics.
- Console logging and data logging are different.
- Prefer rosbag2 as the complete experimental record.
- Parse and plot after the run.
- Preserve enough data to diagnose whether a problem came from the light, sensor, augmentation, controller, or robot.

## Patrick Gaussian whiteboard

High-confidence visual interpretation:

- Solid black curve: original cost field.
- Faint red curve: imperfect current fill producing residual small minima.
- Blue curve: broader basin-scale fill/support concept.
- Dashed/spiral marks: repeated orbiting around the local minimum.
- Formula: softmax/normalized exponential of negative squared distance to candidate minima.

Current engineering hypotheses:

- Estimate the basin center from recent pose/cost samples with kernel weighting.
- Estimate basin spread/covariance.
- Use a wider fill that encompasses the whole attraction basin.
- Couple fill amplitude to width and local curvature/depth.
- Validate a fitted augmented model for residual minima.
- Merge nearby fill candidates instead of stacking overlapping narrow fills.

These mechanisms are the current implementation, not direct meeting mandates.
They should remain configurable and may be revised by versioned evidence before
formal acceptance freeze.
