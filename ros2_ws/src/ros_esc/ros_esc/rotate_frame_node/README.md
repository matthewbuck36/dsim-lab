# Node Description:

The rotate frame node is responsible for controlling the spin of the rotating sensor frame. The user has the freedom to alter the parameters of the rotating sensor frame's spinning in a config file. The user must configure a spin profile object that describes the desired velocity of the rotating sensor frame as a function of the current time, the frame's angular position, and the frame's current spin direction.

## ROS Communication

Input Topic Subscriptions:

- Input Encoder Topic: Used to collect StampedFloat64MultiArray messages which contain the angular positions of rotating sensor frames.

Output Topic Publishing:

- Output Timekeeper Topic: The instant the sensor frame starts to rotate is considered the start time of the experiment, this node publishes Float64 messages which contain timekeeping information which is used to sync up any time dependent cost functions, filters, or controllers.


- Output Velocity Commands Topics: The node publishes Float64MultiArray messages containing velocity commands to the appropriate velocity controller topics.


## Example Configuration File

An example of a rotating frame config file is given below. More examples can be found in the [rotate frame config files](/ros_esc/rotate_frame_node/rotate_frame_config_files) directory.

```
{
    "velocity_controller_one":{
        "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/spin_profile_objects/spin_profile_objects.py",
        "object_name": "Four_Section_Back_And_Forth_Rotation",
        "params":{
            "spin_rpm_section_one": 20,
            "spin_rpm_section_two": 5,
            "spin_rpm_section_three": -20,
            "spin_rpm_section_four": -5,
            "cw_bound_deg": -90,
            "ccw_bound_deg": 90,
            "swap_velo_bound_deg": 0
        }
    },
    "velocity_controller_two":{
        "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/spin_profile_objects/spin_profile_objects.py",
        "object_name": "Constant_Back_And_Forth_Rotation",
        "params":{
            "spin_rpm": 20,
            "cw_bound_deg": -90,
            "ccw_bound_deg": 90
        }
    },
    "velocity_controller_three":{
        "filepath": "~/dsim-lab/ros2_ws/src/ros_esc/ros_esc/rotate_frame_node/spin_profile_objects/spin_profile_objects.py",
        "object_name": "Constant_Full_Rotation",
        "params":{
            "spin_rpm": -10
        }
    }
}
```

Please note that each individual velocity controller (e.g. 'velocity_controller_one', 'velocity_controller_two', 'velocity_controller_three' as seen above) need to have that exact name setup in the robot's controller setup yaml file. This is because this node will publish to the commands topic described with this name. A velocity controller named "velocity_controller_one" in the robot's yaml file should have that exact name in the rotate sensor frame config file, and this ROS node will publish velocity commands to the topic: "/velocity_controller_one/commands". For multiple rotating sensor frames, multiple velocity controllers must have distinct names, note that they all can be configured individually with different spin profile objects.

## Launch Command For This Node:

The following terminal command launches this node. This can be put into a launch file to automatically run this node in an experiment.

```
ros2 run ros_esc rotate_frame_node {input_encoder_topic} {output_timekeeper_topic} {rotate_frame_config}
```
