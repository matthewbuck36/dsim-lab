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

## Launch Command For This Node:

The following terminal command launches this node. This can be put into a launch file to automatically run this node in an experiment.

```
ros2 run ros_esc cost_function_node {input_transform_topic} {input_timekeeper_topic} {output_topic} {cost_function_config}
```
