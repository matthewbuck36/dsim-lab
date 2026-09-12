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
import math
import re
import rclpy
import numpy as np
from rclpy.executors import SingleThreadedExecutor
from rclpy.clock import Clock, ClockType
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
import rclpy.parameter
from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    ControlDiagnostics,
    StampedFloat64MultiArray,
    Timekeeper,
)
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool
from ros_esc.deferred_signal_shutdown import DeferredSignalShutdown
from ros_esc.config_parsing import parse_object_config
from ros_esc.supervisor_node.state_machine import ROBUST_PROFILE, VALID_PROFILES
from ros_esc.v2_stream import (ROLLING_MODE, STATIONARY_MODE, relative_stamp_ns,
                              time_to_ns, stream_contract_id, validate_stream_config)
from ros_esc.controller_node.clock_admission import ClockAdmission, FRESHNESS_NS
from ros_esc.v2_lifecycle import hash_payload, message_payload
from ros_esc.supervisor_node.centered_verification import (
    APPROACH_NS, CENTERED_MODE, COLLECTION_NS, GUIDANCE_TOPIC, LEGACY_MODE, MODES, TOTAL_NS)

CENTERED_EXPIRY_WAIT = 'centered verification expired; waiting for supervisor state'

class CustomController(Node):
    """This class creates a custom controller for use in experimentation."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        args = parse_controller_arguments()
        super().__init__("custom_controller")
        # MBuck 2026-08-04: retain the historical simulation-time default while
        # allowing the Phase 09 physical wrapper to select wall time without
        # forwarding ROS arguments into this node's strict legacy CLI parser.
        self.set_parameters([
            rclpy.parameter.Parameter(
                "use_sim_time",
                rclpy.Parameter.Type.BOOL,
                bool(args.use_sim_time),
            )
        ])

        # Initialize variables
        self.input_value = None
        self.state_value = None
        self.start_time = None
        self.input_value_timestamp = None
        self.timekeeping_mode = None
        self.algorithm_profile = str(args.algorithm_profile).strip()
        if self.algorithm_profile not in VALID_PROFILES:
            raise ValueError(
                f"algorithm_profile must be one of {VALID_PROFILES}; "
                f"received {self.algorithm_profile!r}"
            )
        self.robust_profile = self.algorithm_profile == ROBUST_PROFILE
        self.v2_enabled = args.continuous_search_mode == ROLLING_MODE
        self.v2_run_id = args.v2_run_id
        self.verification_motion_mode = args.v2_verification_motion_mode
        self.verification_stream_config = (validate_stream_config(args.v2_stream_config_json)
            if self.verification_motion_mode == CENTERED_MODE else None)
        self.verification_guidance = {}
        self.verification_guidance_frontier = None
        self.verification_guidance_input_fault = None
        self.verification_expired_lease = None
        self.v2_clock_sec = None
        self.v2_origin_ns = None
        self.v2_origin_fault = False
        self.v2_last_state_source_ns = None
        self.v2_pose_source_ns = None
        self.v2_input_source_ns = None
        self.v2_admission = ClockAdmission() if self.v2_enabled else None
        self.v2_admission_faults = {}
        self.v2_active_steady = {}
        self.v2_state_fenced = False
        self.v2_pose_frame = None
        self.v2_admission_generation = 0
        self.open_field_escape_supervisor_owned_assist_enabled = _as_bool(
            args.open_field_escape_supervisor_owned_assist_enabled
        )
        if (
            self.open_field_escape_supervisor_owned_assist_enabled
            and not self.robust_profile
        ):
            raise ValueError(
                "supervisor-owned escape assist requires "
                f"algorithm_profile={ROBUST_PROFILE}"
            )
        self.enable_observability = (
            _as_bool(args.enable_observability) or self.robust_profile
        )
        self.supervisor_state_stale_sec = max(0.0, args.supervisor_state_stale_sec)
        self.supervisor_command_stale_sec = max(
            0.0, args.supervisor_command_stale_sec
        )
        self.stale_pose_sec = max(0.0, args.stale_pose_sec)
        self.stale_filter_sec = max(0.0, args.stale_filter_sec)
        self.zero_command_on_shutdown = _as_bool(args.zero_command_on_shutdown)
        self.startup_timeout_sec = max(0.0, args.startup_timeout_sec)
        self.controller_started_sec = self._now_sec()
        self.input_receipt_sec = None
        self.pose_receipt_sec = None
        self.supervisor_state_receipt_sec = None
        self.supervisor_command_receipt_sec = None
        self.robust_inputs_ready = False
        self.latest_algorithm_state = None
        self.supervisor_command = np.zeros(6, dtype=np.float64)
        self.last_local_fault = None
        self.recording_ready_required = _as_bool(args.recording_ready_required)
        self.recording_ready_stale_sec = max(0.0, args.recording_ready_stale_sec)
        self.recording_ready = False
        self.recording_ready_receipt_monotonic = None

        # Expand the filepath if the ~ character is used
        config_filepath = os.path.expanduser(args.config)

        # Open the json file
        with open(config_filepath, encoding='utf-8') as file:
            # Convert into a dictionary
            config_dict = json.load(file)

        # Get the initialized controller object
        self.controller_obj = parse_object_config(config_dict)
        self.robust_controller_compatible = (
            type(self.controller_obj).__name__ == "Directional_Controller"
            and hasattr(self.controller_obj, "saturate_command")
        )
        if self.verification_motion_mode == CENTERED_MODE and (
                not self.robust_controller_compatible or
                (self.controller_obj.k_vx, self.controller_obj.k_wz,
                 self.controller_obj.max_vx, self.controller_obj.max_wz) != (.5, 5., .1, .5)):
            raise ValueError('centered verification requires validated .5/5 controller with .1/.5 limits')

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
        self.control_diagnostics_publisher = None
        self.algorithm_event_publisher = None
        if self.enable_observability:
            self.control_diagnostics_publisher = self.create_publisher(
                ControlDiagnostics, args.control_diagnostics_topic, 10
            )
        self.algorithm_state_subscriber = None
        self.supervisor_command_subscriber = None
        self.recording_ready_subscriber = None
        self.watchdog_timer = None
        if self.robust_profile:
            self.algorithm_event_publisher = self.create_publisher(
                AlgorithmEvent, args.algorithm_event_topic, 10
            )
            self.algorithm_state_subscriber = self.create_subscription(
                AlgorithmState,
                args.algorithm_state_topic,
                self.supervisor_state_callback,
                10,
            )
            self.supervisor_command_subscriber = self.create_subscription(
                Twist,
                args.supervisor_command_topic,
                self.supervisor_command_callback,
                10,
            )
        if self.recording_ready_required:
            self.recording_ready_subscriber = self.create_subscription(
                Bool,
                args.recording_ready_topic,
                self.recording_ready_callback,
                10,
            )
        self.verification_guidance_subscriber = None
        if self.verification_motion_mode == CENTERED_MODE:
            from ros_esc_interfaces.msg import VerificationGuidance
            self.verification_guidance_subscriber = self.create_subscription(
                VerificationGuidance, GUIDANCE_TOPIC, self.verification_guidance_callback, 50)
        if self.robust_profile or self.recording_ready_required:
            watchdog_rate = max(1e-6, float(args.command_watchdog_rate_hz))
            self.watchdog_timer = self.create_timer(
                1.0 / watchdog_rate, self.watchdog_callback
            )
        # A held simulation clock must not hold the receipt watchdog. This
        # timer only admits covered samples and enforces the existing bounds.
        self.v2_admission_timer = None
        if self.v2_enabled:
            self.v2_admission_timer = self.create_timer(
                .02, self._v2_admission_tick,
                clock=Clock(clock_type=ClockType.STEADY_TIME))

    def input_value_callback(self, msg: StampedFloat64MultiArray):
        """This function collects the input values."""

        if self.v2_enabled:
            self._v2_receive('filter', msg)
            return
        self._admit_input_value(msg, None)

    def _admit_input_value(self, msg, receipt):
        # Get the input values
        self.input_value = msg.data
        # Get the input timestamp
        self.input_value_timestamp = msg.timestamp
        self.input_receipt_sec = receipt if receipt is not None else self._now_sec()
        # Use the controller and publish the result
        self._evaluate_control_safely()

    def _evaluate_control_safely(self):
        try:
            self.publish_control_value()
        except Exception as exc:
            if not self.robust_profile:
                raise
            self._publish_zero(
                f"controller exception: {type(exc).__name__}: {exc}",
                report_fault=True,
            )

    def state_callback(self, msg: Odometry):
        """This function collects the robot's state."""

        if self.v2_enabled:
            self._v2_receive('pose', msg)
            return
        self._admit_pose(msg, None)

    def _admit_pose(self, msg, receipt):
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
        self.pose_receipt_sec = receipt if receipt is not None else self._now_sec()

    def supervisor_state_callback(self, msg: AlgorithmState):
        """Receive command authorization from the robust supervisor."""

        if self.v2_enabled:
            self._v2_receive('state', msg)
            return
        self.latest_algorithm_state = msg
        self.supervisor_state_receipt_sec = self._now_sec()
        if not self._motion_authorized(self.latest_algorithm_state):
            self._publish_zero("supervisor state disallows motion", report_fault=False)

    def supervisor_command_callback(self, msg: Twist):
        """Receive the Phase 02 zero command and future Phase 04 extension."""

        receipt = self._v2_now_sec() if self.v2_enabled else None
        steady = time.monotonic_ns() if self.v2_enabled else None
        self.supervisor_command = _twist_to_six(msg)
        self.supervisor_command_receipt_sec = receipt if receipt is not None else self._now_sec()
        if self.v2_enabled:
            self.v2_active_steady['command'] = steady

    def verification_guidance_callback(self, message):
        """Retain exact state companions without refreshing repeated receipts."""
        from copy import deepcopy
        now = round(self._v2_now_sec()*1e9)
        steady = time.monotonic_ns()
        try:
            stamp = time_to_ns(message.state_stamp)
            if not -FRESHNESS_NS <= now-stamp <= FRESHNESS_NS:
                return
            if (message.schema_version != 2 or message.publication_sequence <= 0
                    or re.fullmatch(r'[0-9a-f]{64}', message.state_sha256) is None):
                raise ValueError('centered guidance revision identity invalid')
            # Preserve an expired original VERIFY lease before a new revision
            # can replace its companion. This grants no command authorization.
            self._verification_guidance_fault(self.latest_algorithm_state)
            fingerprint = hash_payload(message_payload(message))
            previous = self.verification_guidance_frontier
            if previous is not None:
                if message.publication_sequence < previous[0]:
                    raise ValueError('centered guidance sequence regressed')
                if message.publication_sequence == previous[0]:
                    if fingerprint != previous[1]:
                        raise ValueError('conflicting centered guidance sequence')
                    self._evaluate_control_safely()
                    return
            self.verification_guidance = {k: v for k, v in self.verification_guidance.items()
                                          if now-k[0] <= FRESHNESS_NS}
            key = (stamp, message.state_sha256)
            if key not in self.verification_guidance and len(self.verification_guidance) >= 64:
                raise ValueError('centered guidance capacity')
            self.verification_guidance[key] = (deepcopy(message), now, steady, fingerprint)
            self.verification_guidance_frontier = (message.publication_sequence, fingerprint)
            self.verification_guidance_input_fault = None
            self._evaluate_control_safely()
        except (ValueError, TypeError, OverflowError) as error:
            self.verification_guidance_input_fault = str(error)
            self._publish_zero('centered guidance invalid: '+str(error), report_fault=True)

    @staticmethod
    def _guidance_state_key(state):
        return (time_to_ns(state.stamp), hash_payload(message_payload(state)))

    def _centered_state(self, state):
        return bool(getattr(self, 'verification_motion_mode', LEGACY_MODE) == CENTERED_MODE
            and state is not None and (state.state == AlgorithmState.STATE_VERIFY_EXTREMUM
                or (state.state == AlgorithmState.STATE_DESIGN_OR_MERGE_FILL
                    and state.previous_state_valid
                    and state.previous_state == AlgorithmState.STATE_VERIFY_EXTREMUM)))

    def _verification_guidance_fault(self, state):
        if not self._centered_state(state):
            return None
        now = round(self._v2_now_sec()*1e9)
        key, state_hash = self._guidance_state_key(state)
        if self.verification_guidance_input_fault is not None:
            return self.verification_guidance_input_fault
        item = self.verification_guidance.get((key, state_hash))
        if item is None:
            return ('startup waiting for centered guidance' if 0 <= now-key <= FRESHNESS_NS
                    else 'centered guidance missing')
        message, receipt, steady, _ = item
        if (not message.valid and message.reason == 'centered_preparation_pending'
                and state.state == AlgorithmState.STATE_DESIGN_OR_MERGE_FILL):
            return 'startup waiting for centered preparation'
        try:
            source = time_to_ns(message.pose_stamp)
            accepted = time_to_ns(message.accepted_at)
            admitted = time_to_ns(message.collection_admitted_at)
            verification_end = time_to_ns(message.verification_expires_at)
            command_end = time_to_ns(message.command_expires_at)
            expected_end = (min(admitted+COLLECTION_NS, accepted+TOTAL_NS)
                            if message.collection_started else accepted+APPROACH_NS)
            if (message.schema_version != 2 or not message.valid or message.mode != CENTERED_MODE
                    or message.run_id != self.v2_run_id or message.algorithm_state != state.state
                    or time_to_ns(message.stamp) != key
                    or message.stream_contract_id != stream_contract_id(
                        self.verification_stream_config, self.v2_origin_ns)
                    or message.frame_id != self.v2_pose_frame
                    or message.candidate_id <= 0 or message.search_epoch <= 0
                    or not accepted <= key < command_end
                    or verification_end != expected_end
                    or (message.collection_started and not accepted <= admitted <= min(key, accepted+APPROACH_NS))
                    or (not message.collection_started and admitted != 0)
                    or (state.state == AlgorithmState.STATE_VERIFY_EXTREMUM and command_end != verification_end)
                    or (state.state == AlgorithmState.STATE_DESIGN_OR_MERGE_FILL and
                        (not message.collection_started or command_end > verification_end+5_000_000_000))
                    or not all(0 <= now-v <= FRESHNESS_NS for v in (key, source, receipt))
                    or not 0 <= time.monotonic_ns()-steady <= FRESHNESS_NS
                    or not all(math.isfinite(v) for v in (message.center_x_m, message.center_y_m,
                                                          message.linear_x_mps, message.angular_z_radps))
                    or abs(message.linear_x_mps) > self.controller_obj.max_vx
                    or abs(message.angular_z_radps) > self.controller_obj.max_wz):
                return 'centered guidance identity, validity, bounds or deadline invalid'
            if state.state == AlgorithmState.STATE_VERIFY_EXTREMUM:
                lease = (message.run_id, message.stream_contract_id, message.search_epoch,
                         message.candidate_id, accepted,
                         admitted if message.collection_started else None)
                previous = getattr(self, 'verification_expired_lease', None)
                if previous is not None:
                    if lease[:5] != previous[:5] or (previous[5] is not None and lease[5] != previous[5]):
                        return 'centered verification expired lease identity changed'
                    # The existing once-only admission may arrive after approach
                    # expiry; its original accepted/admitted clocks stay fixed.
                    self.verification_expired_lease = lease
                if now >= command_end:
                    if now-command_end > FRESHNESS_NS:
                        return 'centered guidance identity, validity, bounds or deadline invalid'
                    self.verification_expired_lease = lease
                    return CENTERED_EXPIRY_WAIT
            elif now >= command_end:
                return 'centered guidance identity, validity, bounds or deadline invalid'
        except (ValueError, TypeError, OverflowError):
            return 'centered guidance malformed'
        return None

    def recording_ready_callback(self, msg: Bool):
        """Accept a fresh true recorder heartbeat or immediately force zero."""

        self.recording_ready = bool(msg.data)
        self.recording_ready_receipt_monotonic = time.monotonic()
        if not self.recording_ready:
            self._publish_zero("recording readiness is false", report_fault=False)

    def timekeeping_callback(self, msg: Timekeeper):
        """This function collects the information from the input timekeeping topic."""

        if self.v2_enabled:
            self._v2_now_sec()
            try:
                origin = relative_stamp_ns(0, msg.start_time)
                if msg.mode != 'sim time' or (self.v2_origin_ns is not None and origin != self.v2_origin_ns):
                    raise ValueError('changed or invalid time origin')
                self.v2_origin_ns = origin
            except (ValueError, TypeError, OverflowError):
                self.v2_origin_fault = True
                self._v2_clear_authorization()
                self._publish_zero('changed or invalid V2 time origin', report_fault=False)
                return
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
            gesc_unsaturated = np.asarray(
                getattr(self.controller_obj, "last_command_unsaturated", output),
                dtype=np.float64,
            )
            supervisor_report = None
            combined_unsaturated = None
            recording_fault = self._recording_fault_reason()
            if self.robust_profile:
                fault = self._robust_fault_reason()
                if fault is None:
                    combined_unsaturated = self._authorized_combination(
                        gesc_unsaturated, self.supervisor_command
                    )
                    supervisor_report = combined_unsaturated - gesc_unsaturated
                    output = self.controller_obj.saturate_command(
                        combined_unsaturated
                    )
                    self.last_local_fault = None
                else:
                    if (
                        recording_fault is None
                        and not fault.startswith("startup waiting")
                        and fault != CENTERED_EXPIRY_WAIT
                    ):
                        self._emit_local_fault_once(fault)
                    combined_unsaturated = np.zeros(6, dtype=np.float64)
                    supervisor_report = -gesc_unsaturated
                    output = self.controller_obj.saturate_command(
                        combined_unsaturated
                    )
            if recording_fault is not None:
                combined_unsaturated = np.zeros(6, dtype=np.float64)
                supervisor_report = -gesc_unsaturated
                output = np.zeros(6, dtype=np.float64)
            if self.v2_enabled:
                # Computation may span a clock/readiness boundary. Authorize
                # again immediately before constructing the outgoing command.
                final_fault = self._robust_fault_reason()
                if (final_fault is not None or self._recording_fault_reason() is not None
                        or not self._motion_authorized(self.latest_algorithm_state)):
                    combined_unsaturated = np.zeros(6, dtype=np.float64)
                    supervisor_report = -gesc_unsaturated
                    output = np.zeros(6, dtype=np.float64)
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

            if self.enable_observability:
                self.publish_control_diagnostics(
                    current_time,
                    output,
                    gesc_unsaturated=gesc_unsaturated,
                    supervisor_contribution=supervisor_report,
                    combined_unsaturated=combined_unsaturated,
                )

    def publish_control_diagnostics(
        self,
        source_timestamp,
        output,
        gesc_unsaturated=None,
        supervisor_contribution=None,
        combined_unsaturated=None,
    ):
        """Publish pre/post-saturation values retained by compatible controllers."""

        unavailable = [float("nan")] * 6
        controller = self.controller_obj
        unsaturated = (
            gesc_unsaturated
            if gesc_unsaturated is not None
            else getattr(controller, "last_command_unsaturated", None)
        )
        saturated = getattr(controller, "last_command_saturated", None)
        saturation_flags = getattr(controller, "last_saturation_flags", None)
        limit_valid = getattr(controller, "last_limit_valid", None)
        lower_limits = getattr(controller, "last_lower_limits", None)
        upper_limits = getattr(controller, "last_upper_limits", None)
        diagnostics_available = all(
            value is not None
            for value in (
                unsaturated,
                saturated,
                saturation_flags,
                limit_valid,
                lower_limits,
                upper_limits,
            )
        )

        msg = ControlDiagnostics()
        msg.stamp = self.get_clock().now().to_msg()
        msg.source_timestamp = float(source_timestamp)
        msg.source_timestamp_valid = bool(np.isfinite(source_timestamp))
        msg.controller_type = type(controller).__name__
        if diagnostics_available:
            msg.gesc_command_unsaturated = _six_float_list(unsaturated)
            msg.gesc_command_unsaturated_valid = bool(
                np.all(np.isfinite(unsaturated))
            )
            msg.combined_command_unsaturated = _six_float_list(unsaturated)
            msg.combined_command_unsaturated_valid = (
                msg.gesc_command_unsaturated_valid
            )
            msg.saturation_flags = [
                bool(value) for value in np.asarray(saturation_flags)
            ]
            msg.limit_valid = [bool(value) for value in np.asarray(limit_valid)]
            msg.lower_limits = _six_float_list(lower_limits)
            msg.upper_limits = _six_float_list(upper_limits)
        else:
            msg.gesc_command_unsaturated = unavailable
            msg.gesc_command_unsaturated_valid = False
            msg.combined_command_unsaturated = unavailable
            msg.combined_command_unsaturated_valid = False
            msg.saturation_flags = [False] * 6
            msg.limit_valid = [False] * 6
            msg.lower_limits = unavailable
            msg.upper_limits = unavailable

        if supervisor_contribution is None:
            msg.supervisor_contribution = unavailable
            msg.supervisor_contribution_valid = False
        else:
            msg.supervisor_contribution = _six_float_list(supervisor_contribution)
            msg.supervisor_contribution_valid = bool(
                np.all(np.isfinite(supervisor_contribution))
            )
        if combined_unsaturated is not None:
            msg.combined_command_unsaturated = _six_float_list(combined_unsaturated)
            msg.combined_command_unsaturated_valid = bool(
                np.all(np.isfinite(combined_unsaturated))
            )
        msg.final_command = _six_float_list(output)
        msg.final_command_valid = bool(np.all(np.isfinite(output)))
        k_vx = getattr(controller, "k_vx", None)
        k_wz = getattr(controller, "k_wz", None)
        if k_vx is not None and k_wz is not None:
            msg.k_vx = float(k_vx)
            msg.k_wz = float(k_wz)
            msg.gains_valid = bool(np.isfinite([k_vx, k_wz]).all())
        else:
            msg.k_vx = float("nan")
            msg.k_wz = float("nan")
            msg.gains_valid = False
        self.control_diagnostics_publisher.publish(msg)

    def _now_sec(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def _v2_clear_authorization(self):
        self.latest_algorithm_state = None
        self.supervisor_state_receipt_sec = None
        self.supervisor_command_receipt_sec = None
        self.pose_receipt_sec = None
        self.input_receipt_sec = None
        self.v2_pose_source_ns = None
        self.v2_input_source_ns = None
        self.v2_last_state_source_ns = None
        self.state_value = self.input_value = None
        self.v2_admission.clear()
        self.v2_admission_faults.clear()
        self.v2_active_steady.clear()
        self.v2_state_fenced = False
        self.v2_pose_frame = None
        self.v2_admission_generation += 1
        self.verification_guidance.clear()
        self.verification_guidance_input_fault = None

    def _v2_limit_ns(self, kind):
        seconds = {'pose': self.stale_pose_sec, 'filter': self.stale_filter_sec,
                   'state': self.supervisor_state_stale_sec}[kind]
        return min(FRESHNESS_NS, round(seconds * 1e9))

    def _v2_reject(self, kind, reason):
        self.v2_admission.discard(kind)
        self.v2_admission_faults[kind] = str(reason)
        self.v2_active_steady.pop(kind, None)
        if kind == 'state':
            self.latest_algorithm_state = self.supervisor_state_receipt_sec = None
            self.v2_state_fenced = True
        elif kind == 'pose':
            self.state_value = self.pose_receipt_sec = self.v2_pose_source_ns = None
        else:
            self.input_value = self.input_receipt_sec = self.v2_input_source_ns = None
        self._publish_zero(str(reason), report_fault=self._recording_fault_reason() is None)

    def _v2_receive(self, kind, msg):
        # Capture both clocks before parsing/copying. Polling never refreshes
        # these original receipts, including when the source initially leads.
        receipt_ns = round(self._v2_now_sec() * 1e9)
        steady_ns = time.monotonic_ns()
        try:
            if self.v2_origin_fault:
                raise ValueError('V2 time origin changed')
            if kind == 'filter':
                source_ns = relative_stamp_ns(self.v2_origin_ns, msg.timestamp)
                if len(msg.data) != 2 or not all(math.isfinite(value) for value in msg.data):
                    raise ValueError('V2 filter input invalid')
            elif kind == 'pose':
                source_ns = time_to_ns(msg.header.stamp)
                p, q = msg.pose.pose.position, msg.pose.pose.orientation
                values = (p.x, p.y, p.z, q.x, q.y, q.z, q.w)
                if (not msg.header.frame_id or not all(math.isfinite(v) for v in values)
                        or not math.isclose(sum(v*v for v in values[3:]), 1., abs_tol=1e-6)
                        or (self.v2_pose_frame is not None and msg.header.frame_id != self.v2_pose_frame)):
                    raise ValueError('V2 pose frame or values invalid')
            else:
                source_ns = time_to_ns(msg.stamp)
                fault = self._v2_state_payload_fault_reason(msg)
                if fault:
                    raise ValueError(fault)
            if source_ns < (self.v2_origin_ns or 0):
                raise ValueError(f'V2 {kind} source before time origin')
            added = self.v2_admission.receive(
                kind, source_ns, receipt_ns, steady_ns, msg, limit_ns=self._v2_limit_ns(kind),
                fingerprint=hash_payload(message_payload(msg)))
            if added and kind == 'pose':
                self.v2_pose_frame = msg.header.frame_id
            if kind == 'state' and not self._state_allows_motion(msg):
                # A future stop revokes authority immediately. Older queued
                # SEARCH samples cannot override this fence on their admission.
                self.v2_state_fenced = True
                if source_ns > receipt_ns or not added:
                    self._publish_zero('supervisor state disallows motion', report_fault=False)
            self._v2_drain()
            if not added and kind == 'filter':
                # A duplicate may arrive after another authorization input or
                # readiness changes. Reevaluate only the admitted sample; its
                # original receipts remain unchanged, including while pending.
                self._evaluate_control_safely()
        except (ValueError, TypeError, OverflowError) as error:
            self._v2_reject(kind, str(error))

    def _v2_drain(self):
        # Authorize all covered state revisions before any filter can command.
        # Same-tick publication revisions retain their original receive order.
        for kind in ('state', 'pose', 'filter'):
            now_ns, steady_ns = round(self._v2_now_sec() * 1e9), time.monotonic_ns()
            generation = self.v2_admission_generation
            try:
                items = self.v2_admission.covered(
                    kind, now_ns, steady_ns, limit_ns=self._v2_limit_ns(kind))
            except ValueError as error:
                self._v2_reject(kind, str(error))
                continue
            for item in items:
                # Recheck after earlier admissions/copies/controller work.
                current_ns, current_steady = round(self._v2_now_sec()*1e9), time.monotonic_ns()
                if generation != self.v2_admission_generation:
                    return
                if (item.source_ns < (self.v2_origin_ns or 0)
                        or not 0 <= current_ns-item.source_ns <= self._v2_limit_ns(kind)
                        or not 0 <= current_ns-item.receipt_ns <= self._v2_limit_ns(kind)
                        or not 0 <= current_steady-item.steady_ns <= self._v2_limit_ns(kind)):
                    self._v2_reject(kind, f'V2 {kind} admission expired')
                    break
                self.v2_admission_faults.pop(kind, None)
                self.v2_active_steady[kind] = item.steady_ns
                if kind == 'state':
                    # Observe old authority before accepting a later state at
                    # the same deadline; a phase revision cannot renew it.
                    self._verification_guidance_fault(self.latest_algorithm_state)
                    self.latest_algorithm_state = item.message
                    if item.message.state != AlgorithmState.STATE_VERIFY_EXTREMUM:
                        self.verification_expired_lease = None
                    self.supervisor_state_receipt_sec = item.receipt_ns * 1e-9
                    self.v2_last_state_source_ns = item.source_ns
                    self.v2_state_fenced = any(
                        not self._state_allows_motion(entry.message)
                        for entry in self.v2_admission.pending['state'])
                    if not self._motion_authorized(item.message):
                        self._publish_zero('supervisor state disallows motion', report_fault=False)
                elif kind == 'pose':
                    self.v2_pose_source_ns = item.source_ns
                    self._admit_pose(item.message, item.receipt_ns * 1e-9)
                else:
                    self.v2_input_source_ns = item.source_ns
                    self._admit_input_value(item.message, item.receipt_ns * 1e-9)

    def _v2_admission_tick(self):
        self._v2_drain()
        self.watchdog_callback()

    def _v2_now_sec(self):
        now = self._now_sec()
        if (not math.isfinite(now) or now < 0 or
                (self.v2_clock_sec is not None and now < self.v2_clock_sec)):
            self._v2_clear_authorization()
        self.v2_clock_sec = now
        return now

    def _v2_state_payload_fault_reason(self, state):
        try:
            if (state is None or not state.state_valid or not state.weights_valid
                    or state.algorithm_profile != ROBUST_PROFILE
                    or not state.run_id_valid or state.run_id != self.v2_run_id
                    or not state.failsafe_valid
                    or state.failsafe != (state.state == AlgorithmState.STATE_FAILSAFE)
                    or state.state not in range(1, 9)
                    or not all(math.isfinite(v) for v in
                               (state.sensor_weight, state.gaussian_weight, state.affine_weight))):
                return 'V2 selected supervisor state invalid'
        except (ValueError, TypeError, OverflowError):
            return 'V2 selected supervisor state invalid'
        return None

    def _v2_state_fault_reason(self, state, now):
        fault = self._v2_state_payload_fault_reason(state)
        if fault is not None:
            return fault
        try:
            stamp = time_to_ns(state.stamp)
            if ((self.v2_origin_ns is not None and stamp < self.v2_origin_ns)
                    or not 0 <= now-stamp*1e-9 <= min(.5, self.supervisor_state_stale_sec)
                    or (self.v2_last_state_source_ns is not None
                        and stamp < self.v2_last_state_source_ns)):
                return 'V2 supervisor source stale, future or regressed'
        except (ValueError, TypeError, OverflowError):
            return 'V2 supervisor source invalid'
        return None

    def _motion_authorized(self, state):
        """One state authorization policy for callbacks, combination and watchdog."""
        if not getattr(self, 'robust_profile', True):
            return True
        if state is None:
            return False
        if getattr(self, 'v2_enabled', False):
            now = self._v2_now_sec()
            receipt = self.supervisor_state_receipt_sec
            if (self.v2_origin_fault or self.v2_origin_ns is None
                    or self.v2_state_fenced
                    or self._v2_state_fault_reason(state, now) is not None
                    or receipt is None or not 0 <= now-receipt <= min(.5, self.supervisor_state_stale_sec)):
                return False
        return self._state_allows_motion(state) and self._verification_guidance_fault(state) is None

    def _state_allows_motion(self, state):
        if getattr(self, 'v2_enabled', False):
            if state.state == AlgorithmState.STATE_VERIFY_EXTREMUM:
                return True
            if state.state == AlgorithmState.STATE_DESIGN_OR_MERGE_FILL:
                return state.previous_state_valid and state.previous_state in (
                    AlgorithmState.STATE_VERIFY_EXTREMUM, AlgorithmState.STATE_ESCAPE_REPULSE)
        return state.state in (
            AlgorithmState.STATE_SEARCH, AlgorithmState.STATE_ESCAPE_REPULSE,
            AlgorithmState.STATE_ESCAPE_ASSIST, AlgorithmState.STATE_RECENTER)

    def _robust_fault_reason(self):
        now_sec = self._v2_now_sec() if getattr(self, 'v2_enabled', False) else self._now_sec()
        if not self.robust_controller_compatible:
            return "robust profile requires Directional_Controller"
        if getattr(self, 'v2_enabled', False) and self.v2_admission_faults:
            return next(iter(self.v2_admission_faults.values()))
        startup_elapsed_sec = now_sec - self.controller_started_sec
        startup_waiting = (
            not self.robust_inputs_ready
            and 0.0 <= startup_elapsed_sec <= self.startup_timeout_sec
        )
        freshness = (
            ("supervisor state", self.supervisor_state_receipt_sec, self.supervisor_state_stale_sec),
            ("supervisor command", self.supervisor_command_receipt_sec, self.supervisor_command_stale_sec),
            ("pose", self.pose_receipt_sec, self.stale_pose_sec),
            ("filter input", self.input_receipt_sec, self.stale_filter_sec),
        )
        for name, receipt, limit in freshness:
            if (
                receipt is None
                or now_sec - receipt > limit
                or now_sec < receipt
            ):
                if startup_waiting:
                    return f"startup waiting for {name}"
                return f"{name} missing or stale"
        state = self.latest_algorithm_state
        guidance_fault = self._verification_guidance_fault(state)
        if guidance_fault is not None and guidance_fault != CENTERED_EXPIRY_WAIT:
            return guidance_fault
        if getattr(self, 'v2_enabled', False):
            if self.v2_origin_fault or self.v2_origin_ns is None:
                return 'V2 time origin unavailable or changed'
            state_fault = self._v2_state_fault_reason(state, now_sec)
            if state_fault is not None:
                return state_fault
            for name, source, limit in (
                    ('pose', self.v2_pose_source_ns, self.stale_pose_sec),
                    ('filter input', self.v2_input_source_ns, self.stale_filter_sec)):
                if (source is None or source < self.v2_origin_ns
                        or not 0 <= now_sec-source*1e-9 <= min(.5, limit)):
                    return f'V2 {name} source missing, stale or future'
            steady = time.monotonic_ns()
            for kind, limit in (('pose', self.stale_pose_sec), ('filter', self.stale_filter_sec),
                                ('state', self.supervisor_state_stale_sec),
                                ('command', self.supervisor_command_stale_sec)):
                receipt = self.v2_active_steady.get(kind)
                if receipt is None or not 0 <= steady-receipt <= min(FRESHNESS_NS, round(limit*1e9)):
                    return f'V2 {kind} original steady receipt missing or stale'
        if (
            state is None
            or not state.state_valid
            or state.algorithm_profile != ROBUST_PROFILE
        ):
            return "supervisor state invalid"
        if (
            getattr(
                self,
                "open_field_escape_supervisor_owned_assist_enabled",
                False,
            )
            and state.state == AlgorithmState.STATE_ESCAPE_ASSIST
            and (
                not state.safe_direction_valid
                or not state.safe_direction_revision_valid
                or state.safe_direction_revision != 1
                or not np.all(
                    np.isfinite(
                        [state.safe_direction_x, state.safe_direction_y]
                    )
                )
                or not np.isclose(
                    math.hypot(
                        state.safe_direction_x,
                        state.safe_direction_y,
                    ),
                    1.0,
                    rtol=0.0,
                    atol=1e-9,
                )
            )
        ):
            return "supervisor-owned escape direction invalid"
        valid_states = {
            AlgorithmState.STATE_SEARCH,
            AlgorithmState.STATE_VERIFY_EXTREMUM,
            AlgorithmState.STATE_DESIGN_OR_MERGE_FILL,
            AlgorithmState.STATE_ESCAPE_REPULSE,
            AlgorithmState.STATE_ESCAPE_ASSIST,
            AlgorithmState.STATE_RECENTER,
            AlgorithmState.STATE_GOAL_HOLD,
            AlgorithmState.STATE_FAILSAFE,
        }
        weights = np.array(
            [state.sensor_weight, state.gaussian_weight, state.affine_weight],
            dtype=np.float64,
        )
        if (
            state.state not in valid_states
            or not state.weights_valid
            or not np.all(np.isfinite(weights))
        ):
            return "supervisor state invalid"
        numeric = np.concatenate([
            np.asarray(self.input_value, dtype=np.float64).reshape(-1),
            np.asarray(self.state_value, dtype=np.float64).reshape(-1),
            np.asarray(self.supervisor_command, dtype=np.float64).reshape(-1),
        ])
        if not np.all(np.isfinite(numeric)):
            return "nonfinite controller input"
        self.robust_inputs_ready = True
        return guidance_fault

    def _authorized_combination(self, gesc_command, supervisor_command):
        if not self._motion_authorized(self.latest_algorithm_state):
            return np.zeros(6, dtype=np.float64)
        state = self.latest_algorithm_state.state
        if getattr(self, 'v2_enabled', False):
            if (state == AlgorithmState.STATE_VERIFY_EXTREMUM
                    or (state == AlgorithmState.STATE_DESIGN_OR_MERGE_FILL
                        and self.latest_algorithm_state.previous_state == AlgorithmState.STATE_VERIFY_EXTREMUM)):
                if self._centered_state(self.latest_algorithm_state):
                    message = self.verification_guidance[self._guidance_state_key(self.latest_algorithm_state)][0]
                    return np.array([message.linear_x_mps, 0., 0., 0., 0., message.angular_z_radps])
                return np.asarray(gesc_command, dtype=np.float64)
            if state == AlgorithmState.STATE_DESIGN_OR_MERGE_FILL:
                # Redesign entered from REPULSE keeps its existing escape
                # objective/command owner; the supervisor retains its deadline.
                state = AlgorithmState.STATE_ESCAPE_REPULSE
        supervisor_owned_assist = getattr(
            self,
            "open_field_escape_supervisor_owned_assist_enabled",
            False,
        )
        if supervisor_owned_assist:
            if state == AlgorithmState.STATE_ESCAPE_ASSIST:
                return np.asarray(supervisor_command, dtype=np.float64)
            if state == AlgorithmState.STATE_SEARCH:
                # The first SEARCH update after escape can arrive before the
                # zero supervisor command published beside it on a different
                # ROS topic.  Restore ordinary GESC ownership from the state
                # boundary itself so a delayed ASSIST command cannot leak
                # through that cross-topic handoff.
                return np.asarray(gesc_command, dtype=np.float64)
        if state in (
            AlgorithmState.STATE_SEARCH,
            AlgorithmState.STATE_ESCAPE_REPULSE,
            AlgorithmState.STATE_ESCAPE_ASSIST,
        ):
            return np.asarray(gesc_command) + np.asarray(supervisor_command)
        if state == AlgorithmState.STATE_RECENTER:
            return np.asarray(supervisor_command, dtype=np.float64)
        return np.zeros(6, dtype=np.float64)

    def _recording_fault_reason(self):
        if not self.recording_ready_required:
            return None
        receipt = self.recording_ready_receipt_monotonic
        if receipt is None:
            return "recording readiness heartbeat is missing"
        age = time.monotonic() - receipt
        if age < 0.0 or age > self.recording_ready_stale_sec:
            return "recording readiness heartbeat is stale"
        if not self.recording_ready:
            return "recording readiness is false"
        return None

    def watchdog_callback(self):
        """Continuously enforce zero output whenever robust authorization is absent."""

        fault = self._robust_fault_reason() if self.robust_profile else None
        recording_fault = self._recording_fault_reason()
        if recording_fault is not None:
            fault = recording_fault
        state = self.latest_algorithm_state
        motion_authorized = self._motion_authorized(state)
        if fault is not None and recording_fault is None:
            if not fault.startswith("startup waiting") and fault != CENTERED_EXPIRY_WAIT:
                self._emit_local_fault_once(fault)
        if fault is not None or not motion_authorized:
            self._publish_zero(fault or "supervisor state disallows motion", report_fault=False)

    def _publish_zero(self, reason, report_fault=True):
        zero = np.zeros(6, dtype=np.float64)
        self.twist_publisher.publish(Twist())
        if self.start_time is not None and self.timekeeping_mode in ("sim time", "real time"):
            out = StampedFloat64MultiArray()
            out.header = "Controller Value"
            out.timestamp = self._relative_publish_time()
            out.data = [0.0] * 6
            self.controller_publisher.publish(out)
        if self.control_diagnostics_publisher is not None:
            gesc = getattr(self.controller_obj, "last_command_unsaturated", None)
            if gesc is None or not np.all(np.isfinite(gesc)):
                gesc = zero
            self.publish_control_diagnostics(
                float("nan"),
                zero,
                gesc_unsaturated=gesc,
                supervisor_contribution=-np.asarray(gesc),
                combined_unsaturated=zero,
            )
        if report_fault:
            self._emit_local_fault_once(reason)

    def _relative_publish_time(self):
        if self.timekeeping_mode == "sim time":
            return self._now_sec() - self.start_time
        return float(time.time()) - self.start_time

    def _emit_local_fault_once(self, reason):
        if reason == self.last_local_fault or self.algorithm_event_publisher is None:
            return
        self.last_local_fault = reason
        event = AlgorithmEvent()
        event.stamp = self.get_clock().now().to_msg()
        event.source_timestamp = float("nan")
        event.source_timestamp_valid = False
        event.event_type = AlgorithmEvent.EVENT_FAILSAFE
        event.state = AlgorithmState.STATE_FAILSAFE
        event.state_name = "FAILSAFE"
        event.state_valid = True
        event.fill_id = 0
        event.fill_id_valid = False
        event.reason_code = 1
        event.detail = f"controller watchdog: {reason}"
        event.value_names = []
        event.values = []
        self.algorithm_event_publisher.publish(event)

    def destroy_node(self):
        if self.robust_profile and self.zero_command_on_shutdown:
            self._publish_zero("controller shutdown", report_fault=False)
        return super().destroy_node()


def _argument_bool(value):
    """Parse an explicit command-line boolean without silently accepting typos."""

    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"invalid boolean value: {value!r}")


def parse_controller_arguments(arguments=None):
    """Parse the preserved controller CLI plus its additive clock selector."""

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
    parser.add_argument("--enable_observability", default="False")
    parser.add_argument("--algorithm_profile", default="legacy")
    parser.add_argument(
        "--control_diagnostics_topic",
        default="/gesc_gaussian/control_diagnostics",
    )
    parser.add_argument(
        "--algorithm_state_topic", default="/gesc_gaussian/algorithm_state"
    )
    parser.add_argument(
        "--algorithm_event_topic", default="/gesc_gaussian/algorithm_events"
    )
    parser.add_argument(
        "--supervisor_command_topic",
        default="/gesc_gaussian/supervisor_command",
    )
    parser.add_argument("--supervisor_state_stale_sec", type=float, default=0.5)
    parser.add_argument("--supervisor_command_stale_sec", type=float, default=0.5)
    parser.add_argument(
        "--open_field_escape_supervisor_owned_assist_enabled",
        default="False",
    )
    parser.add_argument("--stale_pose_sec", type=float, default=0.5)
    parser.add_argument("--stale_filter_sec", type=float, default=0.5)
    parser.add_argument("--command_watchdog_rate_hz", type=float, default=20.0)
    parser.add_argument("--startup_timeout_sec", type=float, default=5.0)
    parser.add_argument("--zero_command_on_shutdown", default="True")
    parser.add_argument("--recording_ready_required", default="False")
    parser.add_argument(
        "--recording_ready_topic", default="/gesc_gaussian/recording_ready"
    )
    parser.add_argument("--recording_ready_stale_sec", type=float, default=0.5)
    parser.add_argument("--use-sim-time", type=_argument_bool, default=True)
    parser.add_argument('--continuous-search-mode', default=STATIONARY_MODE,
                        choices=(STATIONARY_MODE, ROLLING_MODE))
    parser.add_argument('--v2-run-id', default='')
    parser.add_argument('--v2-verification-motion-mode', default=LEGACY_MODE, choices=MODES)
    parser.add_argument('--v2-stream-config-json', default='')
    parsed = parser.parse_args(arguments)
    if parsed.v2_verification_motion_mode == CENTERED_MODE:
        if parsed.continuous_search_mode != ROLLING_MODE:
            parser.error('centered verification requires rolling_gesc_v2')
        validate_stream_config(parsed.v2_stream_config_json)
    if parsed.continuous_search_mode == ROLLING_MODE:
        if parsed.algorithm_profile != ROBUST_PROFILE or not parsed.use_sim_time:
            parser.error('rolling_gesc_v2 requires robust_gaussian_v1 simulation')
        if re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', parsed.v2_run_id) is None:
            parser.error('rolling_gesc_v2 requires an explicit valid shared v2_run_id')
    return parsed


def _as_bool(value):
    """Parse existing launch-style string booleans."""

    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _six_float_list(values):
    """Return a fixed six-element list of Python floats."""

    flattened = np.asarray(values).reshape(-1)
    if flattened.size != 6:
        raise ValueError("controller diagnostics require exactly six values")
    return [float(value) for value in flattened]


def _twist_to_six(msg):
    """Convert a Twist to the repository's six-value command convention."""

    return np.array(
        [
            msg.linear.x,
            msg.linear.y,
            msg.linear.z,
            msg.angular.x,
            msg.angular.y,
            msg.angular.z,
        ],
        dtype=np.float64,
    )


def main(args=None):
    """This will initialize and launch the custom controller node."""

    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = CustomController()
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
