# Node Description:

This node is used to subscribe to active ROS2 topics, collect the data published there, and then save to a csv file for documentation. This node subscribes to odometry data which is used to record the vehicle's movement in the environment. This node subscribes to sensor transform data, cost value data, filter output data, and controller command data to record time histories of these values of interest. In addition to recording data to csv files, this node also creates a comments file where config files and objects used for this simulation are all recorded for reference. All files are saved in a folder marked "Test" and appended with the date and time the simulation was conducted. The user can select the directory to store these "Test" folders in by editing the main gazebo launch file.

In addition to data collection, this node also creates live animations of selected data streams for reference during an active simulation. This can be configured with the input argument for the live plotting mode, select either: '2D', '3D', or 'None'.

## ROS Communication:

Input Topic Subscriptions:

- Input Timekeeper Topic: Used to collect Float64 messages which contain timekeeping information to reference.

- Input Odom Topic: Used to collect Odometry messages that will be converted to a position (x,y,z) and quaternion angles (qw,qx,qy,qz) which will be saved with a timestamp to a csv file.

- Input Sensor Transform Topic: Used to collect StampedTransformMultiArray messages that contain the transformation matrices of the sensors which will be saved with a timestamp to a csv file.

- Input Cost Topic: Used to collect StampedFloat64MultiArray messages containing cost value data which will be saved with a timestamp to a csv file.

- Input Filter Topic: Used to collect StampedFloat64MultiArray messages containing filter value data which will be saved with a timestamp to a csv file.

- Input Control Topic: Used to collect StampedFloat64MultiArray messages containing controller data which will be saved with a timestamp to a csv file.

## Launch Command For This Node:

The following terminal command launches this node. This can be put into a launch file to automatically run this node in an experiment.

```
ros2 run ros_esc data_collection_node {filepath} {rotate_frame_config} {transform_config} {cost_funct_config} {filter_node_config} {controller_config} {inp_timekeeper_topic} {inp_odom_topic} {inp_sensor_pose_topic} {inp_cost_topic} {inp_filter_topic} {inp_control_topic} {live_plot_mode}
```
