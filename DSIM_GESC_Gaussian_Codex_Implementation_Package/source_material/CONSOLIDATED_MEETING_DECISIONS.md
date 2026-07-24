# Consolidated Meeting Decisions

## Dr. Nili discussion

- Focus the project on making the GESC + Gaussian method robust.
- Existing physical demonstration may be shown as not yet robust.
- Treat cost value, Gaussian repulsion, and affine contribution as independently switchable.
- The raw sensor cost does not need to remain active during escape.
- Test pure repulsion to leave a local basin.
- Reactivate raw cost after leaving the undesired attraction region.
- Keep previous repulsion active so the robot does not return.
- Determine switching from extensive Gazebo tests.
- Do not continue physical experiments until Gazebo behavior is robust.
- In a bounded indoor environment, return to the center after discovering/escaping a local minimum.
- Keep prior repulsion active during recentering.
- Robustness must cover different local-minimum depths, source levels, source counts, and close local minima.
- Escaping after many repeated circles is not acceptable.
- Acoustic reflective environments are a future motivation; current experiments are light based.

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

Adopted engineering interpretation:

- Estimate the basin center from recent pose/cost samples with kernel weighting.
- Estimate basin spread/covariance.
- Use a wider fill that encompasses the whole attraction basin.
- Couple fill amplitude to width and local curvature/depth.
- Validate a fitted augmented model for residual minima.
- Merge nearby fill candidates instead of stacking overlapping narrow fills.
