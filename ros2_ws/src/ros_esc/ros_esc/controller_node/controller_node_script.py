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
from rclpy.executors import SingleThreadedExecutor
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
from ros_esc.config_parsing import parse_object_config
from ros_esc.supervisor_node.state_machine import ROBUST_PROFILE, VALID_PROFILES

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
        parser.add_argument("--stale_pose_sec", type=float, default=0.5)
        parser.add_argument("--stale_filter_sec", type=float, default=0.5)
        parser.add_argument("--command_watchdog_rate_hz", type=float, default=20.0)
        parser.add_argument("--startup_timeout_sec", type=float, default=5.0)
        parser.add_argument("--zero_command_on_shutdown", default="True")
        args = parser.parse_args()

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
        self.latest_algorithm_state = None
        self.supervisor_command = np.zeros(6, dtype=np.float64)
        self.last_local_fault = None

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
            watchdog_rate = max(1e-6, float(args.command_watchdog_rate_hz))
            self.watchdog_timer = self.create_timer(
                1.0 / watchdog_rate, self.watchdog_callback
            )

    def input_value_callback(self, msg: StampedFloat64MultiArray):
        """This function collects the input values."""

        # Get the input values
        self.input_value = msg.data
        # Get the input timestamp
        self.input_value_timestamp = msg.timestamp
        self.input_receipt_sec = self._now_sec()
        # Use the controller and publish the result
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
        self.pose_receipt_sec = self._now_sec()

    def supervisor_state_callback(self, msg: AlgorithmState):
        """Receive command authorization from the robust supervisor."""

        self.latest_algorithm_state = msg
        self.supervisor_state_receipt_sec = self._now_sec()
        if msg.state not in (
            AlgorithmState.STATE_SEARCH,
            AlgorithmState.STATE_ESCAPE_REPULSE,
            AlgorithmState.STATE_ESCAPE_ASSIST,
            AlgorithmState.STATE_RECENTER,
        ):
            self._publish_zero("supervisor state disallows motion", report_fault=False)

    def supervisor_command_callback(self, msg: Twist):
        """Receive the Phase 02 zero command and future Phase 04 extension."""

        self.supervisor_command = _twist_to_six(msg)
        self.supervisor_command_receipt_sec = self._now_sec()

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
            gesc_unsaturated = np.asarray(
                getattr(self.controller_obj, "last_command_unsaturated", output),
                dtype=np.float64,
            )
            supervisor_report = None
            combined_unsaturated = None
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
                    if not fault.startswith("startup waiting"):
                        self._emit_local_fault_once(fault)
                    combined_unsaturated = np.zeros(6, dtype=np.float64)
                    supervisor_report = -gesc_unsaturated
                    output = self.controller_obj.saturate_command(
                        combined_unsaturated
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

    def _robust_fault_reason(self):
        now_sec = self._now_sec()
        if not self.robust_controller_compatible:
            return "robust profile requires Directional_Controller"
        freshness = (
            ("supervisor state", self.supervisor_state_receipt_sec, self.supervisor_state_stale_sec),
            ("supervisor command", self.supervisor_command_receipt_sec, self.supervisor_command_stale_sec),
            ("pose", self.pose_receipt_sec, self.stale_pose_sec),
            ("filter input", self.input_receipt_sec, self.stale_filter_sec),
        )
        for name, receipt, limit in freshness:
            if receipt is None:
                if now_sec - self.controller_started_sec <= self.startup_timeout_sec:
                    return f"startup waiting for {name}"
                return f"{name} missing or stale"
            if now_sec - receipt > limit or now_sec < receipt:
                return f"{name} missing or stale"
        state = self.latest_algorithm_state
        if (
            state is None
            or not state.state_valid
            or state.algorithm_profile != ROBUST_PROFILE
        ):
            return "supervisor state invalid"
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
        return None

    def _authorized_combination(self, gesc_command, supervisor_command):
        state = self.latest_algorithm_state.state
        if state in (
            AlgorithmState.STATE_SEARCH,
            AlgorithmState.STATE_ESCAPE_REPULSE,
            AlgorithmState.STATE_ESCAPE_ASSIST,
        ):
            return np.asarray(gesc_command) + np.asarray(supervisor_command)
        if state == AlgorithmState.STATE_RECENTER:
            return np.asarray(supervisor_command, dtype=np.float64)
        return np.zeros(6, dtype=np.float64)

    def watchdog_callback(self):
        """Continuously enforce zero output whenever robust authorization is absent."""

        fault = self._robust_fault_reason()
        state = self.latest_algorithm_state
        motion_authorized = (
            state is not None
            and state.state in (
                AlgorithmState.STATE_SEARCH,
                AlgorithmState.STATE_ESCAPE_REPULSE,
                AlgorithmState.STATE_ESCAPE_ASSIST,
                AlgorithmState.STATE_RECENTER,
            )
        )
        if fault is not None:
            if not fault.startswith("startup waiting"):
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
