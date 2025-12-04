#!/usr/bin/env python3

"""The rotate frame node is responsible for commanding the velocity
of the rotating sensor frames. This node subscribes to the user specified
input topic which sends the frames' angular position information. This
node then creates several publishers that run continuously. The first
publisher sends timekeeping information in a Timekeeper message, this is
used to publish the start time of the experiment for other nodes to reference.
The remaining publishers send velocity commands to the user specified
velocity controller command topics. Each rotating sensor frame will have
its own unique velocity controller command topic.

The user has the freedom to alter the parameters of the rotating
sensor frame's spinning in a configuration file. The user can select
a spin profile object and instantiate it with various parameters.

Please note this node is setup only for use in Gazebo simulation.
"""

import os
import json
import argparse
import numpy as np
import rclpy
import rclpy.duration
from rclpy.node import Node
import rclpy.parameter
from std_msgs.msg import Float64MultiArray
from ros_esc_interfaces.msg import Timekeeper, StampedFloat64MultiArray
from ros_esc.config_parsing import parse_object_config

class RotateFrame(Node):
    """This class enables the rotation of the sensor frames in Gazebo simulation."""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-locals

    def __init__(self):
        super().__init__("rotate_arm")

        # Tell this node to use simulation time by setting this parameter
        # This means anytime we use the command 'self._clock.now()' it returns
        # the current simulation time, rather than the current system time.
        self.set_parameters([
            rclpy.parameter.Parameter('use_sim_time',rclpy.Parameter.Type.BOOL, True)
        ])

        # For parsing the input arguments
        description_msg = "\n".join([
            "This node is used to control the velocity of the rotating sensor frames ",
            "attached to a robot. The user can configure the velocity of the rotating ",
            "frames using a rotate frame configuration file and initializing a spin ",
            "profile object. This node always gives the current time, the frame's ",
            "angular position, and the current spin direction to the spin profile object, ",
            "and the node always calls the object's 'velocity_output' method expecting a ",
            "float representing the commanded velocity. Note each rotating sensor frame ",
            "will have its own unique velocity controller command topic, these can be ",
            "configured individually in the config file."
            ])
        input_enc_msg = "\n".join([
            "Please enter the input topic that is sending rotating sensor frame angular ",
            "position data, e.g. '/encoder_chatter'."
        ])
        output_timekeeper_msg = "\n".join([
            "Please enter the output topic that to publish timekeeping information to, ",
            "e.g. '/timekeeper_chatter'."
        ])
        rotate_frame_config_msg = "\n".join([
            "Please enter the filepath to a rotate frame config json file as a string, ",
            "this file should describe the spin characteristics of the rotating sensor frames."
        ])
        parser = argparse.ArgumentParser(description=description_msg)
        parser.add_argument('input_enc_topic', type=str, help=input_enc_msg)
        parser.add_argument('output_timekeeper_topic', type=str, help=output_timekeeper_msg)
        parser.add_argument('config', type=str, help=rotate_frame_config_msg)
        args = parser.parse_args()

        # Initialize variables
        self.angular_positions = None

        # Initialize a list to hold topic names
        controller_names = []
        # Initialize a list to hold spin profile objects
        self.objects_list = []
        # Expand the filepath if the ~ character is used
        config_filepath = os.path.expanduser(args.config)

        # Open the json file
        with open(config_filepath, encoding='utf-8') as file:
            # Convert into a dictionary
            config_dict = json.load(file)
        # Loop through the entries in the config dict
        for entry in config_dict:
            # Get the velocity controller dictionary
            velo_controller_dict = config_dict[entry]
            # Each entry name denotes the name of the velocity controller
            controller_names.append(entry)
            # Parse the spin profile configuration
            spin_profile_obj = parse_object_config(velo_controller_dict)
            # Append to list
            self.objects_list.append(spin_profile_obj)

        # Create a list of publishers
        self.publishers_list = []
        # Create a list of ROS velocity controller command topics
        self.topic_names = []

        # Loop through the names of the velocity controllers
        # Create publishers to each of the velocity controller's command topics
        for entry in controller_names:
            # Format the entry name into the topic name
            topic_name = '/'+entry+"/commands"
            # Append to the topic names list
            self.topic_names.append(topic_name)
            # Create a publisher to the velocity controller commands topic
            # This allows us to publish our commanded velocity to the joint we want to control
            self.publishers_list.append(
                self.create_publisher(
                    Float64MultiArray, topic_name, 10
                )
            )

        # Create a list to denote the spin directions of the rotating frames
        self.spin_directions = []
        # pylint: disable=unused-variable
        for i in range(len(self.objects_list)):
            # Append with None to denote an uninitialized spin direction
            self.spin_directions.append(None)

        self.spin_directions = np.empty(len(self.topic_names))

        # Create a subscriber to the input encoder topic
        # This allows us to extract the rotating frame's angular positions
        self.encoder_subscriber = self.create_subscription(
            StampedFloat64MultiArray, args.input_enc_topic, self.encoder_callback, 10
        )

        # Create a publisher to the output timekeeper topic
        # This allows us to publish timekeeping information.
        self.timekeeper_publisher = self.create_publisher(
            Timekeeper, args.output_timekeeper_topic, 150
        )

        # Collect the start time
        current_time = self._clock.now()
        # Format as a float
        self.start_time = float(current_time.nanoseconds*1e-9)

        # Create a timer to publish the timekeeper information
        self.start_timer = self.create_timer(1/30, self.publish_timekeeper_reading)

    def encoder_callback(self, msg: StampedFloat64MultiArray):
        """This function returns the arm's angular position from the input encoder topic."""

        # Note the encoder angles are in radians
        self.angular_positions = msg.data
        # Publish the velocity commands
        self.publish_velocity_cmds()

    def publish_velocity_cmds(self):
        """This function publishes velocity commands to our velocity controllers."""

        # Ensure we have the data we need to publish
        if self.angular_positions is not None:
            # Loop through all the publishers in the publishers list
            for entry in enumerate(self.publishers_list):
                # Get the index
                index = entry[0]
                # Get the publisher
                publisher = entry[1]
                # Get the spin profile object
                spin_profile_object = self.objects_list[index]

                # Get the current time
                time = self._clock.now()
                # Subtract the reference start time from simulation time
                current_time = float(time.nanoseconds*1e-9) - self.start_time
                # Get the angular position
                phi = self.angular_positions[index]
                # Get the spin direction
                direction = self.spin_directions[index]

                # Get the velocity to publish
                speed = spin_profile_object.velocity_output(current_time, phi, direction)

                # Update the spin direction knowing the speed value
                if np.sign(speed) == 1:
                    # Positive sign denotes counterclockwise rotation
                    self.spin_directions[index] = True
                elif np.sign(speed) == -1:
                    # Negative sign denotes clockwise rotation
                    self.spin_directions[index] = False

                # Create the message
                msg = Float64MultiArray()
                msg.layout.dim = []
                msg.layout.data_offset = 0
                # Add this data to the message
                msg.data = [speed]
                # Publish the message
                publisher.publish(msg)

    def publish_timekeeper_reading(self):
        """This function publishes timekeeper information."""

        # Construct the message
        msg = Timekeeper()
        # Add the start time of the experiment
        msg.start_time = self.start_time
        # Add the timekeeping mode for a Gazebo simulation
        msg.mode = "sim time"
        # Publish the message
        self.timekeeper_publisher.publish(msg)

def main(args=None):
    """This will initialize and launch the node."""

    rclpy.init(args=args)
    node = RotateFrame()

    try:
        rclpy.spin(node)
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
