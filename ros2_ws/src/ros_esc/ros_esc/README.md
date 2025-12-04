# Nodes Description:

This package contains several ROS2 nodes built to run with ROS communication. A basic description of these nodes is given here, see the README files within each subfolder for more information.

## Rotate Sensor Frame:

The rotate frame node is responsible for rotating the sensor frame on the vehicle. This node uses gazebo ros2 controllers to send velocity commands to the revolute joint which connects the rotating frame to the vehicle's body. These commands set the angular velocity of this joint. The instant the rotating frame(s) starts to turn is considered the "start time" of an experiment. This node publishes timekeeping information using this start time. This is necessary to sync up any time dependent cost functions, filters, or controllers used.

## Frame Angular Position Readings:

The encoder node is responsible for reading the state of revolute joints where rotating sensor frames are attached to the vehicle, then continuously publishing their angular positions. This node mimics the readings one would get by using absolute rotary encoders on these revolute joints.

## Sensor Transform Readings:

The sensor pose node is responsible for reading odometry data and encoder readings which then are used to calculate transformation matrices describing the position and orientation of the sensors attached to the rotating frames. This node uses a forward kinematic method to compute these transformation matrices.

## Cost Value Readings:

The cost function node is responsible for reading sensor transformation matrices and generating cost values using a custom cost function.

## Filter Readings:

The filter node is responsible for reading input values and operating on them with a custom filter design, then publishing the output. This node creates a custom filter using base filter objects written in the extremum-seeking package.

## Controller Readings:

The controller node is responsible for reading input values and operating on them with a custom control function, then publishing the output. The output is used to command the velocities of the vehicle, enabling it to move.

## Data Collection:

The data collection node is responsible for documenting information from an active gazebo simulation. This node saves odometry information, sensor transform values, cost values, filter outputs, and controller outputs to csv files. This node also generates a text file where all the configuration files and objects used for that simulation are written out and recorded for reference. These files are all saved in a test folder.
