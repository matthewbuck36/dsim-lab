# ROS ESC

This package contains custom ROS2 messages and services built to run with nodes 
in the ros_esc package. This package is built as an ament_cmake package which is the
only build type that currently allows for custom messages or services to be created
and installed. The build type for ros_esc is ament_python, therefore the custom messages
and services must be imported from this directory to be used.

This package was created using [this documentation](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html) for reference.

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
user@machine:~$ cd ~/dsim-lab/ros2_ws/src
user@machine:~$ git clone https://gitlab.com/dsim-lab/ros-packages/ros_esc_interfaces.git
```

for those who have access to the DSIM Lab Gitlab group. Otherwise one will need to download
the package directly via some compressed file.

## Adding Custom Messages or Services

To add custom messages or services to this package, please create a new branch off of origin
main and then push any commits to the new branch. Once complete, please submit a merge request
so that a DSIM Lab Gitlab maintainer can evaluate the changes and complete a merge.

## Viewing Custom Messages or Services

Please ensure that ROS created the custom messages correctly by using the following terminal commands:
```
user@machine:~$ cd ~/dsim-lab/ros2_ws
user@machine:~$ colcon build --packages-select ros_esc_interfaces
user@machine:~$ source install/setup.bash
user@machine:~$ ros2 interface show ros_esc_interfaces/msg/{custom_msg_name}
```

Please ensure that ROS created the custom services correctly by using the following terminal commands:
```
user@machine:~$ cd ~/dsim-lab/ros2_ws
user@machine:~$ colcon build --packages-select ros_esc_interfaces
user@machine:~$ source install/setup.bash
user@machine:~$ ros2 interface show ros_esc_interfaces/src/{custom_srv_name}
```
