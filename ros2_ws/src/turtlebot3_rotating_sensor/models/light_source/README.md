# Gazebo Light Source Model

This model is the visible marker used for light-source experiments. It contains
a small base, a glowing globe, and a warm Gazebo point light. Collision blocks
are disabled so the marker does not physically block the robot.

The model's SDF point light is not the source of the ROS cost value.
`gazebo.launch.py` reads the selected cost JSON and spawns one marker per
`Multi_Light_Source_Cost.light_sources` entry. Legacy
`Photoresistor_Interpolated_Map` configurations use their `x_optimal` and
`y_optimal` source position. Acoustic and arbitrary equation fields have no
inferred light markers.

Source intensity belongs to the numerical cost configuration. The marker's
warm point-light appearance is illustrative; it does not calibrate modeled
photoresistor brightness. Coordinates are shared with the cost configuration
and remain outside the controller's inputs.
