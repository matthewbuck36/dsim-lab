# ROS ESC

This package contains several ROS2 nodes built to run with ROS communication. These nodes
are useful for gazebo simulations or real life experiments with physical robots. This package
allows for the implementation of extremum seeking controllers using ROS for navigation of
robotic vehicles.

## Author Information

Nicholas Calkins

Dynamic Systems and Intelligent Machines (DSIM)

San Diego State University (SDSU)

email: ncalkins8746@sdsu.edu

## Installation Instructions

The following commands assume the user is downloading this package into a ROS workspace
named "ros2_ws" under their home directory "~". If the user is downloading this package
elsewhere, please update the terminal commands shown here accordingly.

This package can either be downloaded via git using 

```
user@machine:~$ cd ~/ros2_ws/src
user@machine:~$ git clone https://gitlab.com/dsim-lab/ros-packages/ros-esc.git
user@machine:~$ cd ros-esc
user@machine:~$ ~/ros2_ws/src/ros-esc$ pip install -e .
```

for those who have access to the DSIM Lab Gitlab group. Otherwise one will need to download
the package directly via some compressed file.

This package is designed to be used with
- Gazebo, RVIZ, and ROS2 Humble
```
user@machine:~$ cd ~
user@machine:~$ sudo apt install ros-humble-gazebo-ros-pkgs
user@machine:~$ sudo apt-get install ros-humble-rviz
```

This package has several dependencies that need to be installed prior to use 
- gazebo_ros2_control: can be downloaded by following the instructions at 
[this link](https://control.ros.org/rolling/doc/getting_started/getting_started.html).
- The extremum-seeking package from the DSIM Lab Gitlab, can be downloaded and installed via git using

```
user@machine:~$ cd ~
user@machine:~$ git clone https://gitlab.com/dsim-lab/extremum-seeking/extremum-seeking.git
user@machine:~$ cd extremum-seeking
user@machine:~$ ~/extremum-seeking$ pip install -e .
```

- The ros_esc_interfaces package from the DSIM Lab Gitlab, can be downloaded via git using
```
user@machine:~$ cd ~/ros2_ws/src
user@machine:~$ git clone https://gitlab.com/dsim-lab/ros-packages/ros_esc_interfaces.git
```

## Instructions for Use

There are many examples in this ros_esc package that are designed to work with a Turtlebot vehicle in Gazebo simulation. For new users wanting to learn this package, it is recommended to work with the following package: turtlebot3_rotating_sensor from the DSIM Lab Gitlab. Please download the following package via git using
```
user@machine:~$ cd ~/ros2_ws/src
user@machine:~$ git clone https://gitlab.com/dsim-lab/robots/turtlebot-3/turtlebot3_rotating_sensor.git
```

The differential drive plugin is commonly used by ground vehicles. This package includes several examples that work with a Turtlebot vehicle, and this plugin allows the vehicle to move in the simulation. Ensure this plugin is installed by navigating to the following directory and checking if a file named 'libgazebo_ros_diff_drive.so' exists.
```
user@machine:~$ cd /opt/ros/humble/lib
user@machine:~$ ls
```

This package provides several ROS nodes that are built to be implemented on robotic vehicles using ESC controllers. This package is designed to complement packages like turtlebot3_rotating_sensor and turtlebot3_vehicle_nodes on the DSIM Lab Gitlab, which use these ROS nodes for Gazebo and real life experiments respectively.

This package contains many examples of config files that are setup to work with these ROS nodes. For users with access to the DSIM Lab
Gitlab, one should first work with the turtlebot3_rotating_sensor package to become familiar with how this package's ROS nodes work. For new users wanting to see how this package works, please refer to the launch file called gazebo.launch.py under the directory {path_to_package}/turtlebot3_rotating_sensor/launch to become familiar with how these nodes are setup for an experiment. To use various config files, one should change their filepath location in a launch file similar to this one. For new users, the recommended config files to use are as follows:
- Rotate Frame Config: [full_rotation.json](/ros_esc/ros_esc/rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json)
- Transform Config: [turtlebot_rotating_sensor.json](/ros_esc/ros_esc/sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json)
- Cost Function Config: [static_2D_quadratic.json](/ros_esc/ros_esc/cost_function_node/cost_function_config_files/static_2D_quadratic.json)
- Filter Config: [rmsprop_filter_full_rotation.json](/ros_esc/ros_esc/filter_node/filter_config_files/turtlebot_vehicle/adaptive_methods/rmsprop_filter_full_rotation.json)
- Controller Config: [rmsprop_directional_controller.json](/ros_esc/ros_esc/controller_node/controller_config_files/turtlebot_vehicle/adaptive_methods/rmsprop_directional_controller.json)

## Additions to Package

If the user would like to use this package to test new ideas, they should create a new branch off of the main using the following command. Please note that this command was written for a generic ROS workspace named "ros2_ws". If the user wants to work with this package in a workspace not named "ros2_ws", they will have to rewrite the command accordingly.

```
user@machine:~$ cd ~/ros2_ws/src/ros_esc
user@machine:~$ git branch {new_branch_name}
```

Please contact a DSIM Lab Gitlab maintainer to evaluate new additions and merge requests to this package.

## Troubleshooting

For users with plugin errors, they may be coming from outdated versions of the above ROS and Gazebo packages. Consider reinstalling these packages, they may be broken or in need of an update.
```
user@machine:~$ sudo rm -rf /var/lib/apt/lists*
user@machine:~$ sudo apt update
user@machine:~$ sudo apt upgrade --fix-missing
user@machine:~$ sudo apt install --reinstall ros-humble-gazebo-ros-pkgs
user@machine:~$ sudo apt install --reinstall ros-humble-gazebo-ros2-control
```

For users that encounter a Gazebo process running error and are unable to start the server, use the following commands to kill all Gazebo processes running in the background. The user should then restart the experiment. The following commands finds all of the instances of Gazebo running in the background:
```
ps faux | grep gazebo
```
The user should look for the process with the libgazebo name and note the process ID. Knowing this process ID, the following command will kill the process. The user should then try and restart the simulation.
```
kill -9 {process_code_here}
```
