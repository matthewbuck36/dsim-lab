# Node Description:

The purpose of this node is to create a controller node which allows custom control functions to be used with ROS2 communication. The user will pass in a filepath to a controller config file which describes how they want to initialize a controller object for their vehicle. Once initialized, this controller object will be stored in the controller node, and used to operate on input information.

Controller objects are scripts written for specific robotic vehicles. The kinematic models for various ground, aquatic, and subaquatic vehicles are different, and they require different control logic to operate them correctly. Within each vehicle specific script, there could be many controller objects that can be used. 

If the user wants to design a new controller with unique controller logic, they would have to write a new controller object of their own. Every controller object must have the controller output method which gets called by the controller node. The controller node will always pass in the time, the vehicle states, and input values for the controller object to use. The controller object must output an array of commanded velocities in the following format:

[vx, vy, vz, wx, wy, wz]

This will be converted to a Twist message, and sent off via the controller node to command the movement of the vehicle.

## ROS Communication:

Input Topic Subscriptions:

- Input Value Topic: Used to collect StampedFloat64MultiArray messages that contain input values for the controller to operate on. These values may come from a filter or may be taken directly from the cost function node.

- Input State Topic: Used to collect Odometry messages that will be converted to a position (x,y,z) and oreintation (r,p,y) and are passed into the control function.

- Input Timekeeper Topic: Used to collect Timekeeper messages which contain timekeeping information to reference.

Output Topic Publishing:

- Output Control Topic: The node publishes StampedFloat64MultiArray messages which contain the same data as the Twist message, but with an additional timestamp.

- Output Twist Topic: The node publishes Twist messages containing velocity commands to move the vehicle.

## Example of Controller Config File:

```
{
    "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/controller_node/controller_objects/turtlebot_vehicle.py",
    "object_name": "Directional_Controller",
    "gains":{
        "k_v": 1.0,
        "w_z": 1.0
    },
    "params":{
        "wheel_radius": 0.033,
        "wheel_distance": 0.158,
        "wheel_max_rpm": 70,
        "set_max_vx": null,
        "set_max_wz": null
    }
}
```

Note that this config file contains four keys. The filepath key describes the absolute filepath to the desired controller objects script. These scripts are different for different vehicles, they can be found within the [controller objects](/ros_esc/controller_node/controller_objects) folder. The object name key denotes the name of the controller object the user wants to use within that script. Finally, the gains and params keys contain dictionaries, and they are used to initialize the desired controller object. For tuning controllers during experimentation, the user should adjust the values within the gains and params dictionaries. More examples of controller config files can be found within the [controller config files](/ros_esc/controller_node/controller_config_files) folder.

## Launch Command For This Node:

The following terminal command launches this node. This can be put into a launch file to automatically run this node in an experiment.

```
ros2 run ros_esc control_node {input_value_topic} {input_state_topic} {input_timekeeper_topic} {output_control_topic} {output_twist_topic} {controller_config_filepath}
```
