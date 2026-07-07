#!/usr/bin/env python3

"""The controller node allows custom control functions to be used with ROS2
communication. The user will pass in a configuration file which describes a
custom controller object. This object will be saved in the node, and used to
operate on input information. All custom controller objects must take in the
current time, the vehicle's state vector, and input values (likely coming from
a derivative estimation filter) to operate on to produce a set of velocity
commands to drive the vehicle.
"""

import os
import time
import json
import argparse
import rclpy
import numpy as np
from rclpy.node import Node
import rclpy.parameter
from ros_esc_interfaces.msg import Timekeeper, StampedFloat64MultiArray
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from ros_esc.config_parsing import parse_object_config

class CustomController(Node):
    """This class creates a custom controller for use in experimentation."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        super().__init__("custom_controller")

        # Tell this node to use simulation time by setting this parameter
        # This means anytime we use the command 'self._clock.now()' it returns
        # the current simulation time, rather than the current system time.
        self.set_parameters([
            rclpy.parameter.Parameter('use_sim_time',rclpy.Parameter.Type.BOOL, True)
        ])

        # For parsing the input arguments
        description_msg = "\n".join([
            "This controller node is used to create a custom controller to operate on input ",
            "values. All custom controller objects must take in the current time, the vehicle's ",
            "state vector, and input values (likely coming from a derivative estimation filter) ",
            "to operate on to produce a set of velocity commands to drive the vehicle."
            ])
        inp_value_msg = "\n".join([
            "Please enter the input topic that is sending values StampedFloat64MultiArray messages",
            "to evaluate with the custom controller, e.g. '/filter_value_chatter'."
        ])
        inp_state_msg = "\n".join([
            "Please enter the input topic that is sending Odometry messages to convert to a ",
            "robot state, e.g. '/odom'."
        ])
        inp_timekeeping_topic_msg = "\n".join([
            "Please enter the input topic that is sending Timekeeper messages to reference ",
            "e.g. '/timekeeper_chatter'."
        ])
        output_controller_topic_msg = "\n".join([
            "Please name a topic to publish output StampedFloat64MultiArray messages to. ",
            "Please write this topic name as a string, e.g. '/controller_chatter'."
        ])
        output_twist_topic_msg = "\n".join([
            "Please name a topic to publish output Twist messages to. Please write this topic ",
            "name as a string, e.g. '/cmd_vel'."
        ])
        config_file_msg = "\n".join([
            "Please input the filepath to a config file that describes the custom controller."
        ])
        parser = argparse.ArgumentParser(description=description_msg)
        parser.add_argument('inp_value_topic', type=str, help=inp_value_msg)
        parser.add_argument('inp_state_topic', type=str, help=inp_state_msg)
        parser.add_argument('inp_timekeeping_topic', type=str, help=inp_timekeeping_topic_msg)
        parser.add_argument('out_control_topic', type=str, help=output_controller_topic_msg)
        parser.add_argument('out_twist_topic', type=str, help=output_twist_topic_msg)
        parser.add_argument('config', type=str, help=config_file_msg)
        args = parser.parse_args()

        # Initialize variables
        self.input_value = None
        self.state_value = None
        self.start_time = None
        self.input_value_timestamp = None
        self.timekeeping_mode = None

        # Expand the filepath if the ~ character is used
        config_filepath = os.path.expanduser(args.config)

        # Open the json file
        with open(config_filepath, encoding='utf-8') as file:
            # Convert into a dictionary
            config_dict = json.load(file)

        # Get the initialized controller object
        self.controller_obj = parse_object_config(config_dict)

        # Create a subscriber to the input value topic
        # This will give us the input values our custom controller will operate on
        self.input_subscriber = self.create_subscription(
            StampedFloat64MultiArray, args.inp_value_topic, self.input_value_callback, 10
        )

        # Create a subscriber to the state topic
        # This will give us the robot's state to input into the controller
        self.state_subscriber = self.create_subscription(
            Odometry, args.inp_state_topic, self.state_callback, 10
        )

        # Create a subscriber to the timekeeping topic
        # This will give us timekeeping information to reference
        self.timekeeping_subscriber = self.create_subscription(
            Timekeeper, args.inp_timekeeping_topic, self.timekeeping_callback, 10
        )

        # Create a publisher to the output twist topic
        # This will publish the twist messages that move the robot
        self.twist_publisher = self.create_publisher(
            Twist, args.out_twist_topic, 10
        )

        # Create a publisher to the output controller topic
        # This will publish the timestamped output of our custom controller to the output topic
        self.controller_publisher = self.create_publisher(
            StampedFloat64MultiArray, args.out_control_topic, 10
        )

    def input_value_callback(self, msg: StampedFloat64MultiArray):
        """This function collects the input values."""

        # Get the input values
        self.input_value = msg.data
        # Get the input timestamp
        self.input_value_timestamp = msg.timestamp
        # Use the controller and publish the result
        self.publish_control_value()

    def state_callback(self, msg: Odometry):
        """This function collects the robot's state."""

        # Get the vehicle's position
        x_pos = msg.pose.pose.position.x
        y_pos = msg.pose.pose.position.y
        z_pos = msg.pose.pose.position.z

        # Note we have to use the quaternion angles given to us
        # by msg.pose.pose.orientation to calculate our r, p, y angles
        # For reference, see eqns (11a-c):
        # https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
        quat_w = msg.pose.pose.orientation.w
        quat_x = msg.pose.pose.orientation.x
        quat_y = msg.pose.pose.orientation.y
        quat_z = msg.pose.pose.orientation.z

        # Note these angles are in radians
        roll = np.arctan2(2*(quat_w*quat_x+quat_y*quat_z),quat_w**2-quat_x**2-quat_y**2+quat_z**2)
        pitch = np.arcsin(2*(quat_w*quat_y-quat_x*quat_z))
        yaw = np.arctan2(2*(quat_w*quat_z+quat_x*quat_y),quat_w**2+quat_x**2-quat_y**2-quat_z**2)

        # Update our state
        self.state_value = np.array([x_pos, y_pos, z_pos, roll, pitch, yaw])

    def timekeeping_callback(self, msg: Timekeeper):
        """This function collects the information from the input timekeeping topic."""

        # Get the start time from the message
        self.start_time = msg.start_time
        # Get the timekeeping mode from the message
        self.timekeeping_mode = msg.mode

    def publish_control_value(self):
        """This function publishes the output value coming from the controller."""

        # Ensure we have the data we need to publish
        # pylint: disable=line-too-long
        if (self.start_time is not None) and (self.input_value is not None) and (self.state_value is not None):
            # Initialize the current time
            current_time = float(self.input_value_timestamp)
            # Initialize the current input
            controller_inp = np.array(self.input_value)

            # Input the value into the controller, save the result
            output = self.controller_obj.controller_output(
                current_time, self.state_value, controller_inp
            )
            # Convert the values to floats
            output = [float(x) for x in output]

            # Create a twist message
            msg = Twist()
            # The controller output message should hold velocities in the form:
            # [vx, vy, vz, wx, wy, wz]
            msg.linear.x = output[0]
            msg.linear.y = output[1]
            msg.linear.z = output[2]
            msg.angular.x = output[3]
            msg.angular.y = output[4]
            msg.angular.z = output[5]

            # Get the publish time depending on the timekeeping mode
            # If the timekeeper message indicates we're using sim time
            if self.timekeeping_mode == "sim time":
                # Get the publish sim time
                t_publish = self._clock.now()
                # Subtract the reference start time from simulation time
                publish_time = float(t_publish.nanoseconds*1e-9) - self.start_time

            # If the timekeeper message indicates we're using real time
            elif self.timekeeping_mode == "real time":
                # Get the publish real time
                t_publish = time.time()
                # Subtract the reference start time from real time
                publish_time = float(t_publish) - self.start_time

            # Otherwise, raise an error
            else:
                warn_msg = "\n".join([
                    "Timekeeping mode must be either 'sim time' or ",
                    "'real time', invalid entry: "+str(self.timekeeping_mode)
                ])
                raise Exception(warn_msg)

            # Publish the twist message
            self.twist_publisher.publish(msg)

            # Create a new message to publish the
            # controller output with a timestamp
            msg = StampedFloat64MultiArray()
            # Create the header
            msg.header = "Controller Value"
            # Add the timestamp
            msg.timestamp = publish_time
            # Add the data
            msg.data = output
            # Publish the message
            self.controller_publisher.publish(msg)

def main(args=None):
    """This will initialize and launch the custom controller node."""

    rclpy.init(args=args)
    node = CustomController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == "__main__":
    main()
    
