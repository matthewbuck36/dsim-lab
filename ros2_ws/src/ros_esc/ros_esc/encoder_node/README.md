# Node Description:

This node is used to the angular positions of the rotating sensor frames. Upon execution, this node publishes the angular positions of the sensor frames in units of radians. 

It is often the case that the input topic is a joint state publisher.
Note that the joint state publisher is specified in the robot's URDF file.
To ensure that one or more joint states are being read correctly, check that
any joints of interest are named where the joint state publisher gazebo
plugin is initialized in the URDF file. The names of these joints of interest must be passed as
input arguments (string separated by spaces) to this node after the --joint_names tag

## ROS Communication:

Input Topic Subscriptions:
- Input Joint States Topic: Used to collect JointState messages that will be used to gather the angular position of rotating sensor frames.

- Input Timekeeper Topic: Used to collect Timekeeper messages which contain timekeeping information, this is used to create timestamps for output data.

Output Topic Publishing:
- Output Topic: The node publishes StampedFloat64MultiArray messages which contain an array of encoder angular positions.

## Launch Command For This Node:

The following terminal command launches this node. This can be put into a launch file to automatically run this node in an experiment.

```
ros2 run ros_esc encoder_node {input_joint_states_topic} {input_timekeeper_topic} {output_topic}  --joint_names {joint_names_as_strings}
```
