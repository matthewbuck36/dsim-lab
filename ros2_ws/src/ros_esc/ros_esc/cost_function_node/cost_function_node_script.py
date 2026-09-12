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
from collections import OrderedDict
from copy import deepcopy
import json
import argparse
import math
import numpy as np
from ros_esc.cost_function_node.light_brightness import (
    add_brightness_arguments,
    light_sources_from_arguments,
)
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.clock import Clock, ClockType
import rclpy.parameter
from rclpy.signals import SignalHandlerOptions
from ros_esc.deferred_signal_shutdown import DeferredSignalShutdown
from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    CostBreakdown,
    StampedFloat64MultiArray,
    StampedTransformMultiArray,
    SourceSampleProvenance,
    Timekeeper,
)
from ros_esc.config_parsing import parse_object_config
from ros_esc.supervisor_node.state_machine import ROBUST_PROFILE, VALID_PROFILES
from ros_esc.v2_stream import (
    ROLLING_MODE, relative_stamp_ns, sensor_geometry_descriptor, set_time,
    stream_contract_id, validate_mode_identity,
)


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
        add_brightness_arguments(parser)
        parser.add_argument("--enable_observability", default="False")
        parser.add_argument("--algorithm_profile", default="legacy")
        parser.add_argument('--continuous-search-mode', default='stationary_v1')
        parser.add_argument('--v2-run-id', default='')
        parser.add_argument('--v2-stream-config-json', default='')
        parser.add_argument('--v2-sensor-geometry-config', default='')
        parser.add_argument('--v2-provenance-topic', default='/gesc_gaussian/v2/source_sample_provenance')
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
        self.v2_config = validate_mode_identity(
            args.continuous_search_mode, self.algorithm_profile,
            args.v2_run_id, args.v2_stream_config_json,
        )
        self.v2_enabled = args.continuous_search_mode == ROLLING_MODE
        self.v2_run_id = args.v2_run_id
        self.v2_origin_ns = None
        self.v2_origin_invalid = False
        self.v2_stream_id = None
        self.v2_sequence = 1
        self.v2_last_model_ns = None
        self.v2_pending = OrderedDict()
        self.v2_seen = OrderedDict()
        self.v2_publications = OrderedDict()
        self.v2_last_input_ns = None
        self.v2_last_clock_ns = None
        self.v2_active_packet = None
        self.v2_last_fault = None
        self.v2_fault_count = 0
        self.v2_steady_now_ns = time.monotonic_ns
        if self.v2_enabled:
            geometry = sensor_geometry_descriptor(args.v2_sensor_geometry_config)
            if any(self.v2_config[key] != value for key, value in geometry.items()):
                raise ValueError('source sensor geometry differs from V2 stream contract')
            if self.resolve_topic_name(args.input_timekeeping_topic) != self.v2_config['timekeeper_topic']:
                raise ValueError('source Timekeeper differs from V2 stream contract')
        self.v2_provenance_publisher = (
            self.create_publisher(SourceSampleProvenance, args.v2_provenance_topic, 100)
            if self.v2_enabled else None
        )
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
        if self._v2_acquisition_keys():
            # A held/paused ROS clock must not suspend original-receipt expiry.
            self.v2_admission_clock = Clock(clock_type=ClockType.STEADY_TIME)
            self.v2_admission_timer = self.create_timer(
                .01, self.poll_v2_pending, clock=self.v2_admission_clock
            )

    def _v2_acquisition_keys(self):
        return bool(getattr(self, 'v2_enabled', False)
                    and self.v2_config.get('cost_key_basis') == 'model_input_time')

    def _v2_discard(self, reason, *, clear_pending=False, key=None):
        """Keep faults explicit and retransmissions unable to refresh evidence."""
        self.v2_last_fault = str(reason)
        self.v2_fault_count += 1
        if clear_pending:
            self.v2_pending.clear()
        if key is not None:
            self.v2_seen[key] = None
            self.v2_pending.pop(key, None)
        while len(self.v2_seen) > 1024:
            self.v2_seen.popitem(last=False)
        self.get_logger().warning(f'V2 source transform discarded: {reason}')

    def _v2_check_clock(self, now):
        if self.v2_last_clock_ns is not None and now < self.v2_last_clock_ns:
            self.v2_last_clock_ns = now
            self.v2_last_input_ns = None
            self.v2_last_model_ns = None
            self._v2_discard('clock_rollback', clear_pending=True)
            return False
        self.v2_last_clock_ns = now
        return True

    def _v2_queue_transform(self, message):
        now = self._clock.now().nanoseconds
        if not self._v2_check_clock(now):
            return
        if self.v2_origin_ns is None or self.v2_origin_invalid:
            self._v2_discard('unavailable_time_origin', clear_pending=True)
            return
        key = float(message.timestamp)
        try:
            model_ns = relative_stamp_ns(self.v2_origin_ns, key)
            values = tuple(tuple(float(v) for v in (
                t.translation.x, t.translation.y, t.translation.z,
                t.rotation.x, t.rotation.y, t.rotation.z, t.rotation.w,
            )) for t in message.transform_array)
            if (len(values) != 1 or not all(math.isfinite(v) for row in values for v in row)
                    or abs(sum(v*v for v in values[0][3:])-1.) > 1e-3
                    or key < 0 or not -500_000_000 <= now-model_ns <= 500_000_000):
                raise ValueError('invalid_or_out_of_window_transform')
        except (ValueError, TypeError, OverflowError) as exc:
            self._v2_discard(str(exc))
            return
        if key in self.v2_seen:
            if self.v2_seen[key] is not None and self.v2_seen[key] != values:
                self._v2_discard('conflicting_transform_key', key=key)
                self._v2_publish_disputed_key(key, model_ns, now)
            return
        if self.v2_last_input_ns is not None and model_ns <= self.v2_last_input_ns:
            self._v2_discard('transform_source_regression', key=key)
            self._v2_publish_disputed_key(key, model_ns, now)
            return
        if len(self.v2_pending) >= 1024:
            self._v2_discard('transform_capacity', clear_pending=True, key=key)
            return
        self.v2_last_input_ns = model_ns
        self.v2_seen[key] = values
        while len(self.v2_seen) > 1024:
            self.v2_seen.popitem(last=False)
        self.v2_pending[key] = (model_ns, deepcopy(message.transform_array),
                                now, self.v2_steady_now_ns())
        self.poll_v2_pending()

    def _v2_publish_disputed_key(self, key, model_ns, notification_ns):
        """Invalidate evidence for one key without inventing another cost sample."""
        message = SourceSampleProvenance()
        message.schema_version = 2
        set_time(message.stamp, notification_ns)
        set_time(message.time_origin, self.v2_origin_ns)
        set_time(message.model_input_stamp, model_ns)
        set_time(message.cost_publication_stamp, self.v2_publications.get(key, 0))
        message.run_id = self.v2_run_id
        message.stream_contract_id = self.v2_stream_id
        message.frame_id = self.v2_config['frame_id']
        message.source_sequence = self.v2_sequence
        self.v2_sequence += 1
        message.legacy_cost_source_timestamp_sec = key
        # Both validity flags stay false and geometry/channel count stay empty.
        self.v2_provenance_publisher.publish(message)

    def _v2_packet_expired(self, packet, now):
        model_ns, _, receipt_ns, receipt_steady_ns = packet
        return (now-receipt_ns > 500_000_000 or now-model_ns > 500_000_000
                or self.v2_steady_now_ns()-receipt_steady_ns > 500_000_000)

    def poll_v2_pending(self):
        """Admit detached transforms in received source order after clock coverage."""
        now = self._clock.now().nanoseconds
        if not self._v2_check_clock(now):
            return
        if self.v2_origin_ns is None or self.v2_origin_invalid:
            self.v2_pending.clear()
            return
        while self.v2_pending:
            key, packet = next(iter(self.v2_pending.items()))
            if self._v2_packet_expired(packet, now):
                self._v2_discard('transform_original_receipt_expired', key=key)
                continue
            if packet[0] > now:
                break
            self.v2_pending.pop(key)
            self.transforms_tstamp = key
            self.transforms = packet[1]
            self.v2_active_packet = packet
            try:
                self.publish_cost_value()
            except (ValueError, ArithmeticError) as exc:
                self._v2_discard(f'transform_evaluation_failed: {exc}', key=key)
            finally:
                self.v2_active_packet = None
            now = self._clock.now().nanoseconds
            if not self._v2_check_clock(now):
                return

    def configure_light_source_cost(self, args):
        """Pass launch-time light source settings to compatible cost objects."""
        light_sources = light_sources_from_arguments(args)

        self.configured_light_source_count = args.light_source_count
        self.configured_light_sources = light_sources

        if not hasattr(self.cost_function, "configure_light_sources"):
            return

        self.cost_function.configure_light_sources(
            args.light_source_count,
            light_sources,
        )
        if args.light_source_count is not None or any(
            "brightness_percent" in source
            for source in self.cost_function.light_sources
        ):
            self.configured_light_sources = self.cost_function.light_sources
            self.configured_light_source_count = len(self.configured_light_sources)

    def transform_callback(self, msg: StampedTransformMultiArray):
        """This function collects the array of transformation matrices from the input topic"""

        if self._v2_acquisition_keys():
            self._v2_queue_transform(msg)
            return

        # Get the array of transformation matrices from the message
        self.transforms = msg.transform_array
        # Get the timestamp from the message
        # This is what gets used as the current time when using the cost function
        self.transforms_tstamp = msg.timestamp
        # Publish the cost values
        self.publish_cost_value()

    def timekeeping_callback(self, msg: Timekeeper):
        """This function collects the information from the input timekeeping topic."""

        if getattr(self, 'v2_enabled', False):
            try:
                origin_ns = relative_stamp_ns(0, msg.start_time)
                if msg.mode != 'sim time':
                    raise ValueError('V2 requires simulation Timekeeper')
                if self.v2_origin_ns is None:
                    self.v2_origin_ns = origin_ns
                    self.v2_stream_id = stream_contract_id(self.v2_config, origin_ns)
                elif origin_ns != self.v2_origin_ns:
                    raise ValueError('V2 Timekeeper origin changed')
            except (ValueError, TypeError, OverflowError):
                self.v2_origin_invalid = True
                if self._v2_acquisition_keys():
                    self._v2_discard('invalid_time_origin', clear_pending=True)
                return

        # Get the start time from the message
        self.start_time = msg.start_time
        # Get the timekeeping mode from the message
        self.timekeeping_mode = msg.mode

    def publish_cost_value(self):
        """This function publishes the cost values to the output topic."""

        acquisition_keys = self._v2_acquisition_keys()
        if acquisition_keys and self.v2_active_packet is None:
            self._v2_discard('transform_requires_clock_admission')
            return

        # Ensure we have the data we need to publish
        if (self.start_time is not None) and (self.transforms is not None):

            # Initialize cost value array
            cost_values = []
            evaluated_matrices = []
            # Calculate the cost for each sensor transformation matrix in the array
            for transform in self.transforms:
                # Convert the transform object into a transformation matrix
                tform_matrix = create_transform_matrix(transform)
                evaluated_matrices.append(tform_matrix)
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

            if acquisition_keys:
                # Model evaluation may take time or coincide with clock rollback.
                if (self.v2_origin_invalid or not self._v2_check_clock(t_publish.nanoseconds)
                        or self.v2_active_packet[0] > t_publish.nanoseconds
                        or self._v2_packet_expired(self.v2_active_packet, t_publish.nanoseconds)):
                    self._v2_discard('transform_expired_during_evaluation', key=self.transforms_tstamp)
                    return
            source_key = self.transforms_tstamp if acquisition_keys else publish_time
            # Create message
            msg = StampedFloat64MultiArray()
            # Create the header
            msg.header = "Cost Values"
            # Add the data
            msg.data = cost_values
            # Add the timestamp
            msg.timestamp = source_key
            # Publish the message
            self.cost_publisher.publish(msg)
            if acquisition_keys:
                self.v2_publications[source_key] = t_publish.nanoseconds
                while len(self.v2_publications) > 1024:
                    self.v2_publications.popitem(last=False)

            if getattr(self, 'v2_enabled', False):
                self.publish_v2_provenance(evaluated_matrices, source_key, t_publish.nanoseconds)

            if self.enable_observability:
                self.publish_observability(
                    cost_values,
                    source_timestamp=source_key,
                )

    def publish_v2_provenance(self, matrices, legacy_timestamp, publication_ns):
        """Describe exactly the geometry and time used by the preceding raw sample."""
        if self.v2_origin_ns is None or self.v2_origin_invalid:
            return
        message = SourceSampleProvenance()
        message.schema_version = 2 if self._v2_acquisition_keys() else 1
        set_time(message.stamp, publication_ns)
        set_time(message.cost_publication_stamp, publication_ns)
        set_time(message.time_origin, self.v2_origin_ns)
        message.run_id = self.v2_run_id
        message.stream_contract_id = self.v2_stream_id
        message.frame_id = self.v2_config['frame_id']
        message.source_sequence = self.v2_sequence
        self.v2_sequence += 1
        message.legacy_cost_source_timestamp_sec = float(legacy_timestamp)
        message.channel_count = len(matrices)
        message.model_input_stamp_valid = False
        try:
            model_ns = relative_stamp_ns(self.v2_origin_ns, self.transforms_tstamp)
            valid = (self.v2_origin_ns <= model_ns <= publication_ns and
                     (self.v2_last_model_ns is None or model_ns >= self.v2_last_model_ns))
            set_time(message.model_input_stamp, model_ns)
            message.model_input_stamp_valid = valid
            self.v2_last_model_ns = model_ns
        except (ValueError, TypeError, OverflowError):
            pass
        message.sensor_transform_valid = len(matrices) == 1 and all(
            np.asarray(matrix).shape == (4, 4) and np.isfinite(matrix).all()
            for matrix in matrices
        )
        if message.sensor_transform_valid:
            message.sensor_x_m = [float(matrix[0, 3]) for matrix in matrices]
            message.sensor_y_m = [float(matrix[1, 3]) for matrix in matrices]
            message.sensor_world_phase_rad = [float(np.arctan2(matrix[1, 0], matrix[0, 0])) for matrix in matrices]
        self.v2_provenance_publisher.publish(message)

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
                    ("brightness_percent", source.get("brightness_percent")),
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
    with DeferredSignalShutdown() as shutdown:
        try:
            while rclpy.ok() and not shutdown.requested:
                executor.spin_once(timeout_sec=0.05)
        except KeyboardInterrupt:
            shutdown.request()
        finally:
            executor.remove_node(node)
            try:
                executor.shutdown()
            finally:
                try:
                    node.destroy_node()
                finally:
                    rclpy.try_shutdown()


if __name__ == "__main__":
    main()
