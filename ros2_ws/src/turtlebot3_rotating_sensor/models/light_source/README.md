# Gazebo Light Source Model

This model is the visible marker used for light-source experiments. It contains
a small base, a glowing globe, and a warm Gazebo point light. Collision blocks
are disabled so the marker does not physically block the robot.

The model's SDF point light is not the source of the ROS cost value. For
source-seeking experiments, `gazebo.launch.xml` passes
`number_of_lights` and `light_N_x`, `light_N_y`, and
`light_N_brightness_percent` (0–100) into `cost_function_node`.
100% maps to a nominal 1600 lumens; legacy lumen flags remain supported. Cost configs that use
`Multi_Light_Source_Cost` convert those values into the simulated rotating
photoresistor cost map.

This separation keeps the old hardcoded equation configs working while allowing
the visible light markers and the source-seeking cost map to be configured from
the same launch or HeavyBall bash arguments.
