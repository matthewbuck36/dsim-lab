# Node Description:

The purpose of this node is to calculate the cost values of sensors within an environment. The cost function node uses a custom cost function object based on the user's input configuration. This cost function is a function of the sensor's transformation matrix and time t. In addition, the user must configure a noise object to add noise to their cost function signal. This gives the ability to test designs with simulated "sensor noise".

## ROS Communication:

Input Topic Subscriptions:

- Input Transform Topic: Used to collect StampedTransformMultiArray messages which contain an array of transforms to evaluate.

- Input Timekeeper Topic: Used to collect Timekeeper messages which contain timekeeping information to reference.

Output Topic Publishing:

- Output Topic: The node publishes StampedFloat64MultiArray messages containing cost value data.

## Example Configuration File:

This configuration file was made to describe a quadratic cost function with
a minimum at (x, y) = (3, 3). More cost function configuration files can be found in the 
[cost function config files](/ros_esc/cost_function_node/cost_function_config_files) directory.

```
{
    "CostFunction":{
        "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/cost_function_objects.py",
        "object_name": "Position_Based_Sympy_Expression",
        "params":{
            "function": "a*(x-x_optimal)**2 + a*(y-y_optimal)**2",
            "symbols": ["t", "x", "y", "z"],
            "substitutions":{
                "a": 0.5,
                "x_optimal": 3,
                "y_optimal": 3
            }
        }
    },
    "Noise":{
        "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/noise_objects.py",
        "object_name": "No_Noise"
    }
}
```
Note that two objects are being specified in this config file, a cost function object, and a noise object. The cost function itself is written as a dictionary under the "CostFunction" key. The "filepath" key denotes the absolute path to a script, and the "object_name" denotes the object from that script to use. The remaining keys in this dictionary are used to initialize the cost function object. Examples of cost function objects can be found in the [cost function objects script](/ros_esc/cost_function_node/cost_function_objects/cost_function_objects.py) in this package.

In addition to the cost function, a noise object is also being configured under the "Noise" key. The "filepath" key denotes the absolute path to a script, and the "object_name" denotes the object from that script to use. The remaining keys in this dictionary are used to initialize the noise object. If the user would not like any noise to be added to their cost value, they should select the NoNoise object for unaltered data. Examples of noise objects can be found in the [noise objects script](/ros_esc/cost_function_node/cost_function_objects/noise_objects.py) in this package. 

## Light Source Cost Function

`Photoresistor_Interpolated_Map` remains the legacy single-light fitted
photoresistor map. `Multi_Light_Source_Cost` is the multi-light version for
Gazebo light-source tests. It uses the rotating sensor orientation, computes the
angle from the sensor x-axis to each light, evaluates the fitted photoresistor
curve for each source, and combines the sources in conductance space before
returning either resistance or negative voltage.

Each source has an `x` position, `y` position, and `intensity_lumens`. Lumens are
relative to `reference_intensity_lumens`; for example, 2000 lumens contributes
twice the conductance delta of the fitted reference light when
`reference_intensity_lumens` is 1000. This is not an absolute photometric
calibration.

Hardcoded equation configs using `Position_Based_Sympy_Expression` are still
supported and ignore the light-source launch overrides.

Example config:

```json
{
  "CostFunction": {
    "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/cost_function_objects.py",
    "object_name": "Multi_Light_Source_Cost",
    "params": {
      "mode": "Voltage",
      "scale_map": 1.0,
      "apply_adc": false,
      "reference_intensity_lumens": 1000.0,
      "light_sources": [
        {"x": 2.0, "y": 2.0, "intensity_lumens": 1000.0},
        {"x": 10.0, "y": 10.0, "intensity_lumens": 2500.0}
      ]
    }
  },
  "Noise": {
    "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/cost_function_node/cost_function_objects/noise_objects.py",
    "object_name": "No_Noise"
  }
}
```

When launched through `turtlebot3_rotating_sensor/launch/gazebo.launch.xml`,
the `number_of_lights` and `light_N_*` launch arguments override this config's
`light_sources` list for `Multi_Light_Source_Cost` only.

## Launch Command For This Node:

The following terminal command launches this node. This can be put into a launch file to automatically run this node in an experiment.

```
ros2 run ros_esc cost_function_node {input_transform_topic} {input_timekeeper_topic} {output_topic} {cost_function_config}
```
