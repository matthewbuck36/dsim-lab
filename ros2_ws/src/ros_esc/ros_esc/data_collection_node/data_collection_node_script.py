#!/usr/bin/env python3

"""The data collection node subscribes to active ROS2 nodes,
collects the data they are publishing, and then saves to a csv file
for documentation. This node creates a "Test" folder which is appended
with the date and time the experiment was conducted. Within this test
folder, there will be csv files which contain odometry data, sensor
transform data, cost value data, filter output data, and controller output data.
In addition, there will be a comments text file where the transform config,
cost function configuration, filter configuration, and control function
used to conduct the experiment will be written out and recorded for future
reference. The user can select a directory to put these "Test" folders in by
editing the main gazebo launch file.

In addition to data collection, this node also creates live animations of
selected data streams for reference during an active simulation. This can be
configured with the input argument for the live plotting mode,
select either: '2D', '3D', or 'None'.
"""

import os
import csv
import argparse
import threading
import time
from datetime import datetime
from functools import partial
import rclpy
if os.environ.get("ROS_ESC_HEADLESS_PLOTS", "").lower() in ["1", "true", "yes", "on"]:
    import matplotlib
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rclpy.node import Node
from ros_esc_interfaces.msg import Timekeeper, StampedFloat64MultiArray, StampedTransformMultiArray
from ros_esc.helper_functions import create_comment_file, create_experiment_parameters_dict
from ros_esc.data_collection_node.live_plot_animation import initialize_animation, update_plot
from nav_msgs.msg import Odometry
from matplotlib import animation

class DataCollection(Node):
    """This class creates a data collection node for use in Gazebo simulation."""
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-statements
    def __init__(self):
        super().__init__("data_collection_node")

        # Description messages for the input arguments
        description_msg = "\n".join([
            "This node is used to subscribe to active ROS2 topics, collect the data published ",
            "there, and then save to a csv file for documentation."
        ])
        filepath_msg = "Please enter the filepath where the test folder will be created and saved."
        rot_config_msg = "Please enter the filepath to the rotate frame config used for this test."
        tfrm_config_msg = "Please enter the filepath to the transform config used for this test."
        cost_funct_msg = "Please enter the filepath to the cost function used for this test."
        filter_filepath_msg = "Please enter the filepath to the filter used for this test."
        ctrl_filepath_msg = "Please enter the filepath to the controller config used for this test."
        inp_odom_topic_msg = "Please enter the input topic to take odometry data from."
        inp_tform_topic_msg = "Please enter the input topic to take sensor transform data from."
        inp_cost_topic_msg = "Please enter the input topic to take cost data from."
        inp_filter_topic_msg = "Please enter the input topic to take filter data from."
        inp_control_topic_msg = "Please enter the input topic to take control data from."
        inp_timekeeper_topic_msg = "Please enter the input topic to take timekeeper data from."
        live_plot_mode_msg = "Please enter '2D', '3D', or 'None' to select a live plot mode."

        # Add the arguments
        parser = argparse.ArgumentParser(description=description_msg)
        # This argument tells this node where to save test data
        parser.add_argument('filepath', type=str, help=filepath_msg)
        # These arguments tell the node some parameters used in the test
        # These parameters get printed into a comments file for reference
        parser.add_argument('rotate_frame_config_filepath', type=str, help=rot_config_msg)
        parser.add_argument('transform_config_filepath', type=str, help=tfrm_config_msg)
        parser.add_argument('cost_funct_config_filepath', type=str, help=cost_funct_msg)
        parser.add_argument('filter_config_filepath', type=str, help=filter_filepath_msg)
        parser.add_argument('controller_config_filepath', type=str, help=ctrl_filepath_msg)
        # These arguments tell this node what topics to collect data from
        parser.add_argument('input_timekeeper_topic', type=str, help=inp_timekeeper_topic_msg)
        parser.add_argument('input_odom_topic', type=str, help=inp_odom_topic_msg)
        parser.add_argument('input_sensor_transform_topic', type=str, help=inp_tform_topic_msg)
        parser.add_argument('input_cost_topic', type=str, help=inp_cost_topic_msg)
        parser.add_argument('input_filter_topic', type=str, help=inp_filter_topic_msg)
        parser.add_argument('input_control_topic', type=str, help=inp_control_topic_msg)
        parser.add_argument('live_plot_mode', type=str, help=live_plot_mode_msg)
        args = parser.parse_args()
        if args.live_plot_mode not in ["2D", "3D", "None"]:
            raise ValueError(live_plot_mode_msg)
        self.live_plot_enabled = args.live_plot_mode in ["2D", "3D"]
        self.live_plot_data = None

        # Get the current time
        now = datetime.now()
        # Edit the date time string
        self.date_time_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        # Create a default name for the new folder
        folder_title = f"Test_{self.date_time_str}"
        # Create the new folder to hold the test data
        save_to_filepath = os.path.expanduser(args.filepath)
        new_folder = f"{save_to_filepath}/{folder_title}"
        # Create the new folder in the desired filepath directory
        os.makedirs(new_folder, exist_ok=True)

        # Create a dictionary to hold csv and comment file filepaths
        self.filepaths = {}
        # Create a csv filepath to hold odometry information
        self.filepaths["odometry_csv"] = f"{new_folder}/odometry.csv"
        # Create a csv filepath to hold sensor transform information
        self.filepaths["sensor_transform_csv"] = f"{new_folder}/sensor_transform.csv"
        # Create a csv filepath to hold cost value information
        self.filepaths["cost_value_csv"] = f"{new_folder}/cost_value.csv"
        # Create a csv filepath to hold filter value information
        self.filepaths["filter_value_csv"] = f"{new_folder}/filter_value.csv"
        # Create a csv filepath to hold control value information
        self.filepaths["control_value_csv"] = f"{new_folder}/control_value.csv"
        # Create a comments file to hold relevant information
        self.filepaths["comments_txt"] = f"{new_folder}/comments.txt"

        # Organize the config filepaths into a dictionary
        config_files_dict = {}
        # Expand the filepath if the ~ character is used with expanduser
        config_files_dict["rotate_frame_config"] = os.path.expanduser(
            args.rotate_frame_config_filepath)
        config_files_dict["transform_config"] = os.path.expanduser(
            args.transform_config_filepath)
        config_files_dict["cost_function_config"] = os.path.expanduser(
            args.cost_funct_config_filepath)
        config_files_dict["filter_config"] = os.path.expanduser(
            args.filter_config_filepath)
        config_files_dict["controller_config"] = os.path.expanduser(
            args.controller_config_filepath)
        # Create a dictionary of the experiment parameters to use to write comments file
        self.exp_params = create_experiment_parameters_dict(config_files_dict)

        # Indicate that we havn't made the comment text file yet,
        # we wait until the first timekeeper callback to make the
        # file with the timekeeper information
        self.made_comment_file = False

        # If the user selects live plots
        if self.live_plot_enabled:
            # Use the number of transformation objects to
            # determine how many sensors will yield cost values
            # num_cost_vals = len(self.exp_params["transform_objects"])
            # Initialize the live plotting animation parameters
            self.fig, self.live_plot_data = initialize_animation(
                args.live_plot_mode
            )
            # Create animation object that uses the update plot function
            self.ani = animation.FuncAnimation(
                self.fig,
                partial(
                    update_plot,
                    live_plot_data = self.live_plot_data,
                ),
                interval=50
            )

        # Create a subscriber to the input timekeeper topic
        self.timekeeper_subscriber = self.create_subscription(
            Timekeeper, args.input_timekeeper_topic, self.timekeeper_callback, 10
        )

        # Create a subscriber to the input odometry topic
        self.odom_subscriber = self.create_subscription(
            Odometry, args.input_odom_topic, self.odom_callback, 10
        )

        # Create a subscriber to the input sensor position topic
        self.sensor_transform_subscriber = self.create_subscription(
            StampedTransformMultiArray, args.input_sensor_transform_topic,
            self.sensor_transform_callback, 10
        )

        # Create a subscriber to the input cost value topic
        self.cost_value_subscriber = self.create_subscription(
            StampedFloat64MultiArray, args.input_cost_topic, self.cost_callback, 10
        )

        # Create a subscriber to the input filter value topic
        self.filter_value_subscriber = self.create_subscription(
            StampedFloat64MultiArray, args.input_filter_topic, self.filter_callback, 10
        )

        # Create a subscriber to the input controller value topic
        self.control_value_subscriber = self.create_subscription(
            StampedFloat64MultiArray, args.input_control_topic, self.controller_callback, 10
        )

    def timekeeper_callback(self, msg=Timekeeper):
        """This function collects the timekeeper information.

        This is used to collect the experiment's start time, and the
        timekeeping mode. The first time these are gathered, this method
        will print the comments file for reference.
        """

        # Collect the experiment start time
        start_time = msg.start_time
        # Collect the timekeeping mode
        timekeeping_mode = msg.mode
        # If we havn't made the comments file yet, make it
        if self.made_comment_file is False:
            # Convert the timekeeper info into strings and save into list
            timekeeper_info = {
                "start_time": str(start_time),
                "timekeeper_mode": str(timekeeping_mode)
            }

            # Write the comment file to document the test
            create_comment_file(
                self.date_time_str, timekeeper_info,
                self.exp_params, self.filepaths["comments_txt"]
            )
            # Indicate we've created the comments file
            self.made_comment_file = True
        # Otherwise do nothing everytime this is called back
        else:
            pass

    def odom_callback(self, msg=Odometry):
        """This function collects the odometry information and writes to a csv file.

        This function will write data organized in the following columns:
        timestamp, x, y, z, qw, qx, qy, qz
        """

        # Get the vehicle's position
        x = msg.pose.pose.position.x # pylint: disable=invalid-name
        y = msg.pose.pose.position.y # pylint: disable=invalid-name
        z = msg.pose.pose.position.z # pylint: disable=invalid-name

        # Note we have to use the quaternion angles given to us
        # by msg.pose.pose.orientation to calculate our r, p, y angles
        # For reference, see eqns (11a-c):
        # https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
        qw = msg.pose.pose.orientation.w # pylint: disable=invalid-name
        qx = msg.pose.pose.orientation.x # pylint: disable=invalid-name
        qy = msg.pose.pose.orientation.y # pylint: disable=invalid-name
        qz = msg.pose.pose.orientation.z # pylint: disable=invalid-name

        # Get the timestamp from the message
        seconds = msg.header.stamp.sec
        nano_seconds = msg.header.stamp.nanosec
        odom_tstamp = seconds + nano_seconds*1e-9

        # Create our list of data
        data = [odom_tstamp, x, y, z, qw, qx, qy, qz]
        # Append the csv file with this data
        append_csv_file(self.filepaths["odometry_csv"], data)

        if self.live_plot_enabled:
            # Save data for the live plots
            self.live_plot_data["x_position"].append(float(x))
            self.live_plot_data["y_position"].append(float(y))
            self.live_plot_data["z_position"].append(float(z))
            self.live_plot_data["position_tstamps"].append(float(odom_tstamp))

    def sensor_transform_callback(self, msg=StampedTransformMultiArray):
        """This function collects the sensor transform information and writes to a csv file.

        The individual sensor transforms are given in a StampedTransformMultiArray message.
        This function will write data organized in the following way:
        tstamp, tform1_x, tform1_y, tform1_z, tform1_qw, tform1_qx, tform1_qy, tform1_qz, ...
        """

        # Get the timestamp from the message
        sensor_tform_tstamp = msg.timestamp

        # Initialize a list to hold the transform info
        transform_list = [sensor_tform_tstamp]
        # Collect the tranforms from the transform array
        for tform in msg.transform_array:
            # Append this point to the list
            transform_list = transform_list + [
                tform.translation.x, tform.translation.y, tform.translation.z,
                tform.rotation.w, tform.rotation.x, tform.rotation.y, tform.rotation.z
            ]

        # Append the csv file with this data
        append_csv_file(self.filepaths["sensor_transform_csv"], transform_list)

    def cost_callback(self,msg=StampedFloat64MultiArray):
        """This function collects the cost value information and writes to a csv file.

        The cost value is an array of variable length.
        The function will write data organized in the following columns:
        timestamp, cost_value_1, cost_value_2, cost_value_3, ....
        """

        if self.live_plot_enabled:
            # Save data for the live plots
            # Check if this is the first time we receive
            # a cost value, if so we must initialize things
            if self.live_plot_data["num_distinct_cost_values"] is None:
                # Note the amount of distinct cost values in the array
                self.live_plot_data["num_distinct_cost_values"] = len(msg.data)

                # Create new lists of data for each distinct cost value
                for i in range(self.live_plot_data["num_distinct_cost_values"]):
                    # Initialize these lists of data with the first cost values
                    self.live_plot_data[f"cost_value_{i}"] = [msg.data[i]]

                    # Initialize an object to represent this cost value line.
                    self.live_plot_data[f"cost_value_line_{i}"], = (
                        self.live_plot_data["ax3"].plot(
                            [], [], self.live_plot_data["colors"][i], markersize=5
                        )
                    )


            # With initialized cost value lists
            else:
                for i in range(self.live_plot_data["num_distinct_cost_values"]):
                    # Append these lists of data with the cost values
                    self.live_plot_data[f"cost_value_{i}"].append(msg.data[i])

            # Append the timestamp
            self.live_plot_data["cost_value_tstamps"].append(msg.timestamp)

        # Collect the timestamp from this message
        cost_tstamp = [msg.timestamp]
        # Collect the cost values
        cost_data = msg.data.tolist()
        # Add the two lists together
        data = cost_tstamp + cost_data
        # Append the csv file with this data
        append_csv_file(self.filepaths["cost_value_csv"], data)

    def filter_callback(self, msg=StampedFloat64MultiArray):
        """This function collects the filter value information and writes to a csv file.

        The filter value is an array of variable length.
        The function will write data organized in the following columns:
        timestamp, filter_value_1, filter_value_2, filter_value_3, ....
        """

        # Collect the timestamp from this message
        filter_tstamp = [msg.timestamp]
        # Collect the filter value
        filter_data = msg.data.tolist()
        # Add the two lists together
        data = filter_tstamp + filter_data
        # Append the csv file with this data
        append_csv_file(self.filepaths["filter_value_csv"], data)

    def controller_callback(self, msg=StampedFloat64MultiArray):
        """This function collects the controller output twist information and writes to a csv file.

        The control value is an array of variable length.
        The function will write data organized in the following columns:
        timestamp, vx, vy, vz, wx, wy, wz
        """

        # Collect the timestamp from this message
        control_tstamp = [msg.timestamp]
        # Collect the controller value
        control_data = msg.data.tolist()
        # Add the two lists together
        data = control_tstamp + control_data
        # Append the csv file with this data
        append_csv_file(self.filepaths["control_value_csv"], data)

def append_csv_file(filepath, data):
    """This function appends the csv file with the timestamped data."""

    # Check that the data variable isn't None, if there isn't data don't write anything
    if data is not None:
        # Append the csv file
        with open(filepath, mode="a", newline="", encoding="utf-8") as file:
            # Create the object
            log = csv.writer(file)
            # Write the data to the file
            log.writerow(data)

def ros_thread(node):
    """This function creates a thread where anything related to ROS will run."""
    try:
        while rclpy.ok():
            rclpy.spin_once(node)
    except KeyboardInterrupt:
        print("Shutting down ROS thread...")

def main(args=None):
    """This will initialize and launch the data collection node."""

    rclpy.init(args=args)
    node = DataCollection()

    # Create the ROS thread
    ros_thread_instance = threading.Thread(target=ros_thread, args=(node,))
    ros_thread_instance.start()

    try:
        if node.live_plot_enabled:
            plt.show()
        else:
            while rclpy.ok():
                time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        # We wait for a keyboard interrupt, and then run the following
        # Destroy our node
        node.destroy_node()
        # Shutdown ros2 communications
        rclpy.try_shutdown()

if __name__ == "__main__":
    main()
