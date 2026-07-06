#!/usr/bin/env python3

"""The cost function node computes cost values for each sensor in an experiment.
This node computes the cost value based on the sensor's transformation matrix
and the current experiment time. The user has the ability to create a custom
cost function in a cost function configuration file. In this file, they must
initialize both a cost function object, and a noise object. The cost funciton
object computes a cost value given the sensor transformation matrix and the
current time. The noise object adds noise to this computed cost value, this
noise may or may not be a function of time.

Please note this node is setup only for use in Gazebo simulation.
"""

import os
import time
import json
import argparse
import numpy as np
import rclpy
from rclpy.node import Node
import rclpy.parameter
from ros_esc_interfaces.msg import Timekeeper, StampedFloat64MultiArray, StampedTransformMultiArray
from ros_esc.config_parsing import parse_object_config

class CostFunction(Node):
    """This class creates a cost function for use in Gazebo simulation."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        super().__init__("cost_function")

        # Tell this node to use simulation time by setting this parameter
        # This means anytime we use the command 'self._clock.now()' it returns
        # the current simulation time, rather than the current system time.
        self.set_parameters([
            rclpy.parameter.Parameter('use_sim_time',rclpy.Parameter.Type.BOOL, True)
        ])

        # For parsing the input arguments
        description_msg = "\n".join([
            "This cost function node is used to calculate cost values for sensors from ",
            "a user specified cost function. The user can configure this cost value ",
            "computation by configuring a cost value object and a noise object in a ",
            "configuration file. The cost function object computes a cost value based ",
            "the sensor's transformation matrix and the current time. The noise object ",
            "can add noise to this cost value signal which may or may not be a funciton ",
            "of time. Note all rotating sensor frames will utilize the same cost function ",
            "and noise objects."
        ])
        inp_transform_topic_msg = "\n".join([
            "Please enter the input topic that is sending sensor transformation matrices to ",
            "evaluate the cost function with, e.g. '/sensor_transform_chatter'."
        ])
        inp_timekeeping_topic_msg = "\n".join([
            "Please enter the input topic that is sending timekeeping information to reference ",
            "e.g. '/timekeeper_chatter'."
        ])
        out_topic_msg = "\n".join([
            "Please enter the output topic you want this node to publish to, ",
            "e.g. '/cost_value_chatter'."
        ])
        cost_funct_msg = "\n".join([
            "Please input the filepath to a config file that describes the architecture ",
            "of the cost function and noise objects."
        ])
        parser = argparse.ArgumentParser(description=description_msg)
        parser.add_argument('input_transform_topic', type=str, help=inp_transform_topic_msg)
        parser.add_argument('input_timekeeping_topic', type=str, help=inp_timekeeping_topic_msg)
        parser.add_argument('output_topic', type=str, help=out_topic_msg)
        parser.add_argument('config', type=str, help=cost_funct_msg)
        parser.add_argument(
            "--light_source_count",
            "--number_of_lights",
            dest="light_source_count",
            type=int,
            default=None,
        )
        for light_idx in range(1, 6):
            parser.add_argument(f"--light_source_{light_idx}_x", type=float, default=None)
            parser.add_argument(f"--light_source_{light_idx}_y", type=float, default=None)
            parser.add_argument(
                f"--light_source_{light_idx}_intensity_lumens",
                type=float,
                default=None,
            )
        args = parser.parse_args()

        # Initialize variables
        self.start_time = None
        self.timekeeping_mode = None
        self.transforms = None
        self.transforms_tstamp = None

        # Expand the filepath if the ~ character is used
        config_filepath = os.path.expanduser(args.config)

        # Open the json file
        with open(config_filepath, encoding='utf-8') as file:
            # Convert into a dictionary
            config_dict = json.load(file)

        # Assert that there are cost function and noise keys in this dictionary
        warn_msg = "There must be a 'CostFunction' key in file: "+config_filepath
        assert 'CostFunction' in config_dict, warn_msg
        warn_msg = "/n".join([
            "There must be a 'Noise' key in file: "+config_filepath+" \n",
            "If the user desires no noise to be added to the cost value ",
            "signal, please use the NoNoise object as a placeholder."
        ])
        assert 'Noise' in config_dict, warn_msg

        # Get the cost function object
        self.cost_function = parse_object_config(config_dict["CostFunction"])
        self.configure_light_source_cost(args)
        # Get the noise object
        self.noise_obj = parse_object_config(config_dict["Noise"])

        # Create a subscriber to the input transforms topic
        # This allows us to extract transforms to evaluate the cost function with
        self.transform_subscriber = self.create_subscription(
            StampedTransformMultiArray, args.input_transform_topic,
            self.transform_callback, 10
        )

        # Create a subscriber to the timekeeping topic
        # This will tell us timekeeping information to reference
        self.timekeeping_subscriber = self.create_subscription(
            Timekeeper, args.input_timekeeping_topic, self.timekeeping_callback, 10
        )

        # Create a publisher
        # This will publish the cost value with the given sensor transform information
        self.cost_publisher = self.create_publisher(
            StampedFloat64MultiArray, args.output_topic, 10
        )

    def configure_light_source_cost(self, args):
        """Pass launch-time light source settings to compatible cost objects."""

        if not hasattr(self.cost_function, "configure_light_sources"):
            return

        light_sources = []
        for light_idx in range(1, 6):
            light_sources.append({
                "x": getattr(args, f"light_source_{light_idx}_x"),
                "y": getattr(args, f"light_source_{light_idx}_y"),
                "intensity_lumens": getattr(
                    args, f"light_source_{light_idx}_intensity_lumens"
                ),
            })

        self.cost_function.configure_light_sources(
            args.light_source_count,
            light_sources,
        )

    def transform_callback(self, msg: StampedTransformMultiArray):
        """This function collects the array of transformation matrices from the input topic"""

        # Get the array of transformation matrices from the message
        self.transforms = msg.transform_array
        # Get the timestamp from the message
        # This is what gets used as the current time when using the cost function
        self.transforms_tstamp = msg.timestamp
        # Publish the cost values
        self.publish_cost_value()

    def timekeeping_callback(self, msg: Timekeeper):
        """This function collects the information from the input timekeeping topic."""

        # Get the start time from the message
        self.start_time = msg.start_time
        # Get the timekeeping mode from the message
        self.timekeeping_mode = msg.mode

    def publish_cost_value(self):
        """This function publishes the cost values to the output topic."""

        # Ensure we have the data we need to publish
        if (self.start_time is not None) and (self.transforms is not None):

            # Initialize cost value array
            cost_values = []
            # Calculate the cost for each sensor transformation matrix in the array
            for transform in self.transforms:
                # Convert the transform object into a transformation matrix
                tform_matrix = create_transform_matrix(transform)
                # Plug the transformation matrix and the current time into the cost function
                cost_val = self.cost_function.cost_output(
                    self.transforms_tstamp, tform_matrix
                )
                # Convert result to float and append to list
                cost_values.append(float(cost_val))

            # Plug the cost value into the noise object
            cost_values = self.noise_obj.add_noise(
                self.transforms_tstamp, np.array(cost_values)
            )

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

            # Create message
            msg = StampedFloat64MultiArray()
            # Create the header
            msg.header = "Cost Values"
            # Add the data
            msg.data = cost_values
            # Add the timestamp
            msg.timestamp = publish_time
            # Publish the message
            self.cost_publisher.publish(msg)

def create_transform_matrix(transform_object):
    """This converts a transform object into a transformation matrix."""

    # Get the translation portion in the transform object
    x_pos = transform_object.translation.x
    y_pos = transform_object.translation.y
    z_pos = transform_object.translation.z
    # Get the quaternions in the transform object
    quat_w = transform_object.rotation.w
    quat_x = transform_object.rotation.x
    quat_y = transform_object.rotation.y
    quat_z = transform_object.rotation.z

    # Package this position and orientation data into a homogeneous transformation matrix
    # Note this transformation matrix represents the position & orientation of the vehicle
    # in the stationary odometry frame. The rotation matrix was constructed using eqn (7b):
    # https://danceswithcode.net/engineeringnotes/quaternions/quaternions.html
    transform_matrix = np.array([
        [
            1-2*quat_y**2-2*quat_z**2,
            2*quat_x*quat_y-2*quat_w*quat_z,
            2*quat_x*quat_z+2*quat_w*quat_y,
            x_pos
        ],
        [
            2*quat_x*quat_y+2*quat_w*quat_z,
            1-2*quat_x**2-2*quat_z**2,
            2*quat_y*quat_z-2*quat_w*quat_x,
            y_pos
        ],

        [
            2*quat_x*quat_z-2*quat_w*quat_y,
            2*quat_y*quat_z+2*quat_w*quat_x,
            1-2*quat_x**2-2*quat_y**2,
            z_pos
        ],
        [0,0,0,1]
    ])

    return transform_matrix

def main(args=None):
    """This will initialize and launch the cost function node."""

    rclpy.init(args=args)
    node = CostFunction()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
