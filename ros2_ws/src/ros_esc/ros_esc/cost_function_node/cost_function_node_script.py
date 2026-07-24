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
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
import rclpy.parameter
from rclpy.signals import SignalHandlerOptions
from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    CostBreakdown,
    StampedFloat64MultiArray,
    StampedTransformMultiArray,
    Timekeeper,
)
from ros_esc.config_parsing import parse_object_config
from ros_esc.supervisor_node.state_machine import ROBUST_PROFILE, VALID_PROFILES


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
        parser.add_argument("--enable_observability", default="False")
        parser.add_argument("--algorithm_profile", default="legacy")
        parser.add_argument(
            "--source_cost_topic",
            default="/gesc_gaussian/source_cost",
        )
        parser.add_argument(
            "--publish_final_breakdown",
            default="False",
        )
        parser.add_argument(
            "--cost_breakdown_topic",
            default="/gesc_gaussian/cost_breakdown",
        )
        parser.add_argument(
            "--algorithm_state_topic",
            default="/gesc_gaussian/algorithm_state",
        )
        parser.add_argument(
            "--algorithm_event_topic",
            default="/gesc_gaussian/algorithm_events",
        )
        parser.add_argument(
            "--observability_source_mode",
            default="simulation",
        )
        args = parser.parse_args()

        # Initialize variables
        self.start_time = None
        self.timekeeping_mode = None
        self.transforms = None
        self.transforms_tstamp = None
        self.algorithm_profile = str(args.algorithm_profile).strip()
        if self.algorithm_profile not in VALID_PROFILES:
            raise ValueError(
                f"algorithm_profile must be one of {VALID_PROFILES}; "
                f"received {self.algorithm_profile!r}"
            )
        self.robust_profile = self.algorithm_profile == ROBUST_PROFILE
        self.enable_observability = (
            _as_bool(args.enable_observability) or self.robust_profile
        )
        self.publish_final_breakdown = _as_bool(args.publish_final_breakdown)
        self.observability_source_mode = _source_mode(
            args.observability_source_mode
        )
        self.observability_configuration_published = False

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
        self.cost_model_name = type(self.cost_function).__name__
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

        self.cost_breakdown_publisher = None
        self.source_cost_publisher = None
        self.algorithm_state_publisher = None
        self.algorithm_event_publisher = None
        if self.enable_observability:
            self.algorithm_event_publisher = self.create_publisher(
                AlgorithmEvent, args.algorithm_event_topic, 10
            )
            self.source_cost_publisher = self.create_publisher(
                CostBreakdown, args.source_cost_topic, 10
            )
            if self.publish_final_breakdown:
                self.cost_breakdown_publisher = self.create_publisher(
                    CostBreakdown, args.cost_breakdown_topic, 10
                )
            if self.publish_final_breakdown and not self.robust_profile:
                self.algorithm_state_publisher = self.create_publisher(
                    AlgorithmState, args.algorithm_state_topic, 10
                )

    def configure_light_source_cost(self, args):
        """Pass launch-time light source settings to compatible cost objects."""
        light_sources = []
        for light_idx in range(1, 6):
            light_sources.append({
                "x": getattr(args, f"light_source_{light_idx}_x"),
                "y": getattr(args, f"light_source_{light_idx}_y"),
                "intensity_lumens": getattr(
                    args, f"light_source_{light_idx}_intensity_lumens"
                ),
            })

        self.configured_light_source_count = args.light_source_count
        self.configured_light_sources = light_sources

        if not hasattr(self.cost_function, "configure_light_sources"):
            return

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

            if self.enable_observability:
                self.publish_observability(
                    cost_values,
                    source_timestamp=publish_time,
                )

    def publish_observability(self, cost_values, source_timestamp):
        """Publish opt-in typed mirrors after the unchanged legacy output."""

        stamp = self.get_clock().now().to_msg()
        if not self.observability_configuration_published:
            self.publish_configuration_events(stamp)
            self.observability_configuration_published = True

        values = [float(value) for value in np.asarray(cost_values).tolist()]
        channel_count = len(values)
        unavailable = [float("nan")] * channel_count
        zeros = [0.0] * channel_count
        source_scores = [
            float(self.cost_function.source_score(value)) for value in values
        ]
        source_score_valid = bool(
            len(source_scores) == channel_count
            and np.all(np.isfinite(source_scores))
        )

        breakdown = CostBreakdown()
        breakdown.stamp = stamp
        breakdown.source_timestamp = float(source_timestamp)
        breakdown.source_timestamp_valid = bool(np.isfinite(source_timestamp))
        breakdown.source_mode = self.observability_source_mode
        breakdown.source_name = self.cost_model_name
        breakdown.channel_count = channel_count
        breakdown.raw_sensor_value = unavailable
        breakdown.filtered_sensor_value = unavailable
        breakdown.raw_cost = values
        breakdown.source_score = source_scores if source_score_valid else unavailable
        breakdown.gaussian_cost = zeros
        breakdown.affine_cost = zeros
        breakdown.augmented_cost = values
        breakdown.sensor_weight = 1.0
        breakdown.gaussian_weight = 0.0
        breakdown.affine_weight = 0.0
        breakdown.raw_sensor_valid = False
        breakdown.filtered_sensor_valid = False
        breakdown.raw_cost_valid = bool(np.all(np.isfinite(values)))
        breakdown.source_score_valid = source_score_valid
        breakdown.gaussian_cost_valid = True
        breakdown.affine_cost_valid = True
        breakdown.augmented_cost_valid = breakdown.raw_cost_valid
        breakdown.weights_valid = True
        if self.source_cost_publisher is not None:
            self.source_cost_publisher.publish(breakdown)
        if self.cost_breakdown_publisher is not None:
            self.cost_breakdown_publisher.publish(breakdown)

        if self.algorithm_state_publisher is None:
            return

        state = AlgorithmState()
        state.stamp = stamp
        state.source_timestamp = float(source_timestamp)
        state.source_timestamp_valid = bool(np.isfinite(source_timestamp))
        state.run_id = ""
        state.run_id_valid = False
        state.algorithm_profile = self.algorithm_profile
        state.state = AlgorithmState.STATE_UNAVAILABLE
        state.state_name = "UNAVAILABLE"
        state.state_valid = False
        state.previous_state = AlgorithmState.STATE_UNAVAILABLE
        state.previous_state_name = "UNAVAILABLE"
        state.previous_state_valid = False
        state.transition_reason = ""
        state.transition_reason_valid = False
        state.state_elapsed_sec = float("nan")
        state.state_elapsed_valid = False
        state.active_fill_count = 0
        state.active_fill_count_valid = True
        state.active_escape_fill_id = 0
        state.active_escape_fill_id_valid = False
        state.escape_center_x = float("nan")
        state.escape_center_y = float("nan")
        state.escape_exit_radius = float("nan")
        state.escape_geometry_valid = False
        state.radial_distance = float("nan")
        state.radial_distance_valid = False
        state.radial_progress = float("nan")
        state.radial_progress_valid = False
        state.escape_exit_hold_elapsed_sec = float("nan")
        state.escape_exit_hold_elapsed_valid = False
        state.escape_stalled = False
        state.escape_stalled_valid = False
        state.safe_direction_x = float("nan")
        state.safe_direction_y = float("nan")
        state.safe_direction_clearance_m = float("nan")
        state.safe_direction_valid = False
        state.safe_direction_revision = 0
        state.safe_direction_revision_valid = False
        state.recenter_target_x = float("nan")
        state.recenter_target_y = float("nan")
        state.recenter_target_valid = False
        state.recenter_distance = float("nan")
        state.recenter_distance_valid = False
        state.sensor_weight = 1.0
        state.gaussian_weight = 0.0
        state.affine_weight = 0.0
        state.weights_valid = True
        state.failsafe = False
        state.failsafe_valid = False
        self.algorithm_state_publisher.publish(state)

    def publish_configuration_events(self, stamp):
        """Publish source configuration and unavailable capability status."""

        names = []
        values = []
        if self.configured_light_source_count is not None:
            names.append("source_count")
            values.append(float(self.configured_light_source_count))
            active_sources = self.configured_light_sources[
                :max(0, self.configured_light_source_count)
            ]
            for index, source in enumerate(active_sources, start=1):
                entries = (
                    ("x_m", source["x"]),
                    ("y_m", source["y"]),
                    ("relative_intensity_input", source["intensity_lumens"]),
                )
                for suffix, value in entries:
                    if value is not None and np.isfinite(value):
                        names.append(f"source_{index}_{suffix}")
                        values.append(float(value))

        event = AlgorithmEvent()
        event.stamp = stamp
        event.source_timestamp = float("nan")
        event.source_timestamp_valid = False
        event.event_type = AlgorithmEvent.EVENT_CONFIGURATION
        event.state = AlgorithmState.STATE_UNAVAILABLE
        event.state_name = "UNAVAILABLE"
        event.state_valid = False
        event.fill_id = 0
        event.fill_id_valid = False
        event.reason_code = 0
        event.detail = (
            f"source_mode={_source_mode_name(self.observability_source_mode)}; "
            f"cost_model={self.cost_model_name}; relative simulator intensity "
            "inputs are not absolute photometric calibration"
        )
        event.value_names = names
        event.values = values
        self.algorithm_event_publisher.publish(event)

        unavailable = AlgorithmEvent()
        unavailable.stamp = stamp
        unavailable.source_timestamp = float("nan")
        unavailable.source_timestamp_valid = False
        unavailable.event_type = AlgorithmEvent.EVENT_CAPABILITY_UNAVAILABLE
        unavailable.state = AlgorithmState.STATE_UNAVAILABLE
        unavailable.state_name = "UNAVAILABLE"
        unavailable.state_valid = False
        unavailable.fill_id = 0
        unavailable.fill_id_valid = False
        unavailable.reason_code = 1
        if self.cost_model_name in {
            "Photoresistor_Interpolated_Map",
            "Multi_Light_Source_Cost",
        }:
            unavailable.detail = (
                "raw_sensor_value and filtered_sensor_value are unavailable; "
                "source_score uses simulated photoresistor model endpoints"
            )
        else:
            unavailable.detail = (
                "raw_sensor_value, filtered_sensor_value, and source_score are "
                "unavailable for this simulation cost model"
            )
        unavailable.value_names = []
        unavailable.values = []
        self.algorithm_event_publisher.publish(unavailable)


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


def _as_bool(value):
    """Parse existing launch-style string booleans without changing defaults."""

    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _source_mode(value):
    """Map a platform adapter name to the common source enum."""

    normalized = str(value).strip().lower()
    if normalized == "simulation":
        return CostBreakdown.SOURCE_SIMULATION
    if normalized == "physical":
        return CostBreakdown.SOURCE_PHYSICAL
    return CostBreakdown.SOURCE_UNKNOWN


def _source_mode_name(value):
    """Return a stable readable name for a source enum."""

    if value == CostBreakdown.SOURCE_SIMULATION:
        return "simulation"
    if value == CostBreakdown.SOURCE_PHYSICAL:
        return "physical"
    return "unknown"


def main(args=None):
    """This will initialize and launch the cost function node."""

    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = CostFunction()
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    try:
        while rclpy.ok():
            executor.spin_once(timeout_sec=0.05)
    except KeyboardInterrupt:
        pass
    finally:
        executor.remove_node(node)
        try:
            node.destroy_node()
        finally:
            executor.shutdown()
            rclpy.try_shutdown()


if __name__ == "__main__":
    main()
