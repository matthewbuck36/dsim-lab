#!/usr/bin/env python3

"""The filter node which allows custom filters to be used with ROS2 communication.
The user will pass in a custom filter configuration that is written out in a json
configuration file, or passed in as a string. This node will construct that
configuration, making use of filters and parameter ODEs built in the extremum
seeking package.
"""

# pylint: disable=wildcard-import

import os
import time
import json
import argparse
import rclpy
import numpy as np
from rclpy.node import Node
import rclpy.parameter
from ros_esc_interfaces.msg import (
    GescDiagnostics,
    StampedFloat64MultiArray,
    Timekeeper,
)
from ros_esc.config_parsing import parse_filter_config
from ros_esc.supervisor_node.state_machine import ROBUST_PROFILE, VALID_PROFILES

class CustomFilter(Node):
    """This class creates a custom filter for use in Gazebo simulation."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        super().__init__("custom_filter")

        # Tell this node to use simulation time by setting this parameter
        # This means anytime we use the command 'self._clock.now()' it returns
        # the current simulation time, rather than the current system time.
        self.set_parameters([
            rclpy.parameter.Parameter('use_sim_time',rclpy.Parameter.Type.BOOL, True)
        ])

        # For parsing the input arguments
        description_msg = "\n".join([
            "This filter node is used to create a custom filter to operate on input values. ",
            "Custom filter architecture must make use of base filter and parameter ODE ",
            "objects from the extremum seeking package. These filters are used to compute ",
            "derivative estimates which will be used in the extremum seeking controller."
            ])
        inp_value_topic_msg = "\n".join([
            "Please enter the input topic that is sending values to evaluate with the ",
            "custom filter, e.g. '/cost_value_chatter'."
        ])
        inp_encoder_topic_msg = "\n".join([
            "Please enter the input topic that is sending encoder data to evaluate with the ",
            "custom filter, e.g. '/encoder_chatter'."
        ])
        inp_timekeeping_topic_msg = "\n".join([
            "Please enter the input topic that is sending timekeeping information to reference ",
            "e.g. '/timekeeper_chatter'."
        ])
        out_topic_msg = "\n".join([
            "Please enter the output topic you want this node to publish to, ",
            "e.g. '/filter_value_chatter'."
        ])
        file_msg = "\n".join([
            "Please input the filepath to a .json file that describes the architecture ",
            "of the custom filter."
        ])
        # string_msg = "\n".join([
        #     "Please input a string that fully describes the architecture of the custom filter.",
        # ])
        encoder_inp_msg = "\n".join([
            "Use this option to combine encoder data with cost value data and input the combined ",
            "vector into the custom filter as the input, please select: 'True' or 'False'."
        ])
        parser = argparse.ArgumentParser(description=description_msg)
        parser.add_argument('inp_value_topic', type=str, help = inp_value_topic_msg)
        parser.add_argument('inp_encoder_topic', type=str, help = inp_encoder_topic_msg)
        parser.add_argument('inp_timekeeping_topic', type=str, help=inp_timekeeping_topic_msg)
        parser.add_argument('out_topic', type=str, help=out_topic_msg)
        parser.add_argument('--filter_file', type=str, dest="json_config",
                            help=file_msg)
        # parser.add_argument('--filter_string', type=str, dest="string_config",
        #                     help=string_msg)
        parser.add_argument('--append_encoder_data', type=str, dest="combine_enc_data",
                            help=encoder_inp_msg)
        parser.add_argument("--enable_observability", default="False")
        parser.add_argument("--algorithm_profile", default="legacy")
        parser.add_argument(
            "--gesc_diagnostics_topic",
            default="/gesc_gaussian/gesc_diagnostics",
        )
        args = parser.parse_args()

        # Initialize variables
        self.prev_time = 0
        self.start_time = None
        self.timekeeping_mode = None
        self.input_value = None
        self.input_value_timestamp = None
        self.encoder_value = None
        self.algorithm_profile = str(args.algorithm_profile).strip()
        if self.algorithm_profile not in VALID_PROFILES:
            raise ValueError(
                f"algorithm_profile must be one of {VALID_PROFILES}; "
                f"received {self.algorithm_profile!r}"
            )
        self.enable_observability = (
            _as_bool(args.enable_observability)
            or self.algorithm_profile == ROBUST_PROFILE
        )

        # Specify if we want to combine cost values and encoder values
        self.combine_data = False
        if args.combine_enc_data == 'True':
            self.combine_data = True

        # Parse custom filter input
        if args.json_config is not None:
            # Expand the filepath if the ~ character is used
            config_filepath = os.path.expanduser(args.json_config)
            # Open the json file
            with open(config_filepath, encoding='utf-8') as file:
                # Convert into a dictionary
                config_dict = json.load(file)
                # Parse that configuration dictionary into a filter object
                self.custom_filter, self.z_vec = parse_filter_config(config_dict, [])

        # elif args.string_config is not None:
        #     # Convert into a dictionary
        #     config_dict = json.load(args.string_config)
        #     # Parse that configuration dictionary into a filter object
        #     self.custom_filter, self.z_vec = parse_filter_config(config_dict, [])

        # # If no filter input is given, raise an exception
        # elif args.string_config is None and args.json_config is None:
        #     raise Exception("No filter configuration specified,"+
        #                     "please input a json file or a dictionary string to parse.")

        # Create a subscriber to the user input topic
        # This will give us the input values our custom filter will operate on
        self.cost_subscriber = self.create_subscription(
            StampedFloat64MultiArray, args.inp_value_topic, self.input_value_callback, 10
        )

        # Create a subscriber to the user input encoder topic
        # This will give us the input values our custom filter will operate on
        self.encoder_subscriber = self.create_subscription(
            StampedFloat64MultiArray, args.inp_encoder_topic, self.encoder_value_callback, 10
        )

        # Create a subscriber to the timekeeping topic
        # This will give us timekeeping information to reference
        self.timekeeping_subscriber = self.create_subscription(
            Timekeeper, args.inp_timekeeping_topic, self.timekeeping_callback, 10
        )

        # Create a publisher
        # This will publish the output of our custom filter to the output topic
        self.filter_publisher = self.create_publisher(
            StampedFloat64MultiArray, args.out_topic, 10
        )
        self.gesc_diagnostics_publisher = None
        if self.enable_observability:
            self.gesc_diagnostics_publisher = self.create_publisher(
                GescDiagnostics, args.gesc_diagnostics_topic, 10
            )

    def input_value_callback(self, msg: StampedFloat64MultiArray):
        """This collects the input value, then uses the filter, then publishes the result."""

        # Get the input value
        input_value = msg.data
        # Get the input timestamp
        self.input_value_timestamp = msg.timestamp
        # Convert the input value to a numpy array
        self.input_value = np.array(input_value)
        # Evaluate with the custom filter and publish
        self.publish_filter_value()

    def encoder_value_callback(self, msg: StampedFloat64MultiArray):
        """This collects the encoder value."""

        # Get the encoder value
        encoder_value = msg.data
        # Convert the encoder value to a numpy array
        self.encoder_value = np.array(encoder_value)

    def timekeeping_callback(self, msg: Timekeeper):
        """This function collects the information from the input timekeeping topic."""

        # Get the start time from the message
        self.start_time = msg.start_time
        # Get the timekeeping mode from the message
        self.timekeeping_mode = msg.mode

    def publish_filter_value(self):
        """This function publishes the output value coming from the custom filter."""

        # Ensure we have the data we need to publish
        # pylint: disable=line-too-long
        if (self.start_time is not None) and (self.input_value is not None) and (self.encoder_value is not None):
            # Initialize the current time
            current_time = float(self.input_value_timestamp)
            # Initialize the current input
            filter_input = np.array(self.input_value)

            # If we want to combine with encoder data
            if self.combine_data:
                input_val = np.concatenate([filter_input, self.encoder_value])
            else:
                input_val = self.input_value

            state_before = np.array(self.z_vec, dtype=np.float64, copy=True)

            # Input the cost value into the filter, save the result
            filter_output = self.custom_filter.filter_output(
                self.z_vec,
                input_val,
                current_time
            )
            # Convert the values to floats
            output = [float(x) for x in filter_output]

            # Calculate the change in filter state
            z_vec_dot = self.custom_filter.differential_equation(
                current_time, self.z_vec, input_val
            )

            # Check if this is a valid filter state
            # Update the filter state vector z with a forward euler step
            self.z_vec = self.check_filter_valid_state(
                self.prev_time, current_time, input_val, self.z_vec, z_vec_dot
            )

            # Update the previous timestamp
            self.prev_time = current_time

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

            # Create the message
            msg = StampedFloat64MultiArray()
            # Create the header
            msg.header = "Filter Value"
            # Add the timestamp
            msg.timestamp = publish_time
            # Add the data
            msg.data = output
            # Publish the message
            self.filter_publisher.publish(msg)

            if self.enable_observability:
                self.publish_gesc_diagnostics(
                    current_time,
                    input_val,
                    output,
                    state_before,
                    z_vec_dot,
                    self.z_vec,
                )

    def publish_gesc_diagnostics(
        self,
        source_timestamp,
        filter_input,
        filter_output,
        state_before,
        state_derivative,
        state_after,
    ):
        """Publish the values used by the unchanged filter evaluation."""

        input_values = _float_list(filter_input)
        output_values = _float_list(filter_output)
        before_values = _float_list(state_before)
        derivative_values = _float_list(state_derivative)
        after_values = _float_list(state_after)

        diagnostics = GescDiagnostics()
        diagnostics.stamp = self.get_clock().now().to_msg()
        diagnostics.source_timestamp = float(source_timestamp)
        diagnostics.source_timestamp_valid = bool(
            np.isfinite(source_timestamp)
        )
        diagnostics.valid = bool(
            np.all(np.isfinite(input_values))
            and np.all(np.isfinite(output_values))
            and np.all(np.isfinite(before_values))
            and np.all(np.isfinite(derivative_values))
            and np.all(np.isfinite(after_values))
        )
        diagnostics.filter_input = input_values
        diagnostics.filter_output = output_values
        diagnostics.filter_state_before = before_values
        diagnostics.filter_state_derivative = derivative_values
        diagnostics.filter_state_after = after_values

        if self.combine_data and self.encoder_value.size > 0:
            diagnostics.dither_phase_rad = float(self.encoder_value.flat[0])
            diagnostics.dither_phase_valid = bool(
                np.isfinite(diagnostics.dither_phase_rad)
            )
        else:
            diagnostics.dither_phase_rad = float("nan")
            diagnostics.dither_phase_valid = False
        diagnostics.dither_amplitude_m = float("nan")
        diagnostics.dither_amplitude_valid = False
        diagnostics.dither_angular_frequency_rad_sec = float("nan")
        diagnostics.dither_angular_frequency_valid = False
        self.gesc_diagnostics_publisher.publish(diagnostics)

    # pylint: disable=too-many-arguments
    # pylint: disable=line-too-long
    def check_filter_valid_state(self, previous_time, current_time, orig_input_val, orig_z_vec, orig_z_vec_dot):
        """This function checks if the filter states are valid.

        If the filter state is invalid, we loop through and check if
        using smaller dt timesteps causes the filter state to be valid
        and then update the filter state with a the timestep that works.
        """

        # Calculate the origional change in time
        orig_dt = current_time - previous_time
        # Calculate the next filter state
        z_vec_new = orig_z_vec + orig_dt * orig_z_vec_dot
        # If we have an invalid state
        if not self.custom_filter.valid_state(z_vec_new):
            # Create a counting variable
            m = 1 # pylint: disable=invalid-name
            # Continue looping while we have an infeasible result
            while not self.custom_filter.valid_state(z_vec_new):
                # Increment the count
                m += 1 # pylint: disable=invalid-name
                # Redefine the change in time
                time_increment = orig_dt / m
                # Initialize another counting variable
                p = 0 # pylint: disable=invalid-name
                # Compare p to m
                while p < m:
                    # On first iteration, this runs
                    if p == 0:
                        # Calculate the change in filter state
                        dz_value = self.custom_filter.differential_equation(
                            current_time, orig_z_vec, orig_input_val
                        )
                        # Increment the new filter state
                        z_vec_new = orig_z_vec + time_increment * dz_value

                    # On all other iterations
                    else:
                        # Calculate the change in filter state
                        dz_value = self.custom_filter.differential_equation(
                            current_time + p*time_increment, z_vec_new, orig_input_val
                        )
                        # Increment the new filter state
                        z_vec_new += time_increment * dz_value

                    # Increment p
                    p += 1 # pylint: disable=invalid-name

        # Return the new filter state
        return z_vec_new


def _as_bool(value):
    """Parse existing launch-style string booleans."""

    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _float_list(values):
    """Flatten numeric filter data into ROS-compatible Python floats."""

    return [float(value) for value in np.asarray(values).reshape(-1)]


def main(args=None):
    """This will initialize and launch the custom filter node."""

    rclpy.init(args=args)
    node = CustomFilter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
