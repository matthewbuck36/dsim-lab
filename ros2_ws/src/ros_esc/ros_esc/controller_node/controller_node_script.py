#!/usr/bin/env python3
"""Original ESC controller adapter, or the single V3 owner selected by --v3."""

import argparse
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.clock import Clock, ClockType
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.signals import SignalHandlerOptions
from ros_esc_interfaces.msg import StampedFloat64MultiArray, Timekeeper

from ros_esc.config_parsing import parse_object_config
from ros_esc.deferred_signal_shutdown import DeferredSignalShutdown

INPUT_EXPIRY_SEC = .5
COMMAND_HZ = 20.


def _argument_bool(value):
    normalized = str(value).strip().lower()
    if normalized in {'1', 'true', 'yes', 'on'}:
        return True
    if normalized in {'0', 'false', 'no', 'off'}:
        return False
    raise argparse.ArgumentTypeError(f'invalid boolean value: {value!r}')


def parse_controller_arguments(arguments=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('inp_value_topic', 'inp_state_topic', 'inp_timekeeping_topic',
                 'out_control_topic', 'out_twist_topic', 'config'):
        parser.add_argument(name)
    parser.add_argument('--use-sim-time', type=_argument_bool, default=True)
    return parser.parse_args(arguments)


def state_from_odometry(message):
    position, quaternion = message.pose.pose.position, message.pose.pose.orientation
    values = np.asarray([position.x, position.y, position.z,
                         quaternion.x, quaternion.y, quaternion.z, quaternion.w], dtype=float)
    if not np.all(np.isfinite(values)) or not message.header.frame_id.strip():
        raise ValueError('invalid pose')
    norm = np.linalg.norm(values[3:])
    if not math.isfinite(norm) or norm <= 1e-9:
        raise ValueError('invalid pose quaternion')
    x, y, z, w = values[3:] / norm
    roll = math.atan2(2 * (w*x + y*z), 1 - 2 * (x*x + y*y))
    pitch = math.asin(max(-1., min(1., 2 * (w*y - x*z))))
    yaw = math.atan2(2 * (w*z + x*y), 1 - 2 * (y*y + z*z))
    stamp = message.header.stamp.sec + message.header.stamp.nanosec * 1e-9
    if not 0 <= message.header.stamp.nanosec < 1_000_000_000 or not math.isfinite(stamp) or stamp < 0:
        raise ValueError('invalid pose timestamp')
    return np.array([*values[:3], roll, pitch, yaw]), stamp, message.header.frame_id


class CustomController(Node):
    """Compute once per fresh input; a steady timer expires held commands."""

    def __init__(self, arguments=None, controller_obj=None, **kwargs):
        args = parse_controller_arguments(arguments)
        kwargs.setdefault('parameter_overrides', [Parameter('use_sim_time', value=args.use_sim_time)])
        super().__init__('custom_controller', **kwargs)
        if self.get_parameter('use_sim_time').value != args.use_sim_time:
            raise ValueError('use_sim_time disagrees with explicit controller CLI')
        self.expected_mode = 'sim time' if args.use_sim_time else 'real time'
        if controller_obj is None:
            with Path(args.config).expanduser().open(encoding='utf-8') as stream:
                controller_obj = parse_object_config(json.load(stream))
        self.controller_obj = controller_obj
        self.start_time = None
        self.input_value = self.state_value = None
        self.input_value_timestamp = None
        self.pose_stamp = self.input_stamp = None
        self.pose_receipt = self.input_receipt = None
        self.frame = self.last_clock = self.last_evaluated_stamp = None
        self.command = np.zeros(6)
        self.availability, self.reason = 'WAITING_INPUT', 'waiting for fresh pose and filter'
        self.twist_publisher = self.create_publisher(Twist, args.out_twist_topic, 10)
        self.controller_publisher = self.create_publisher(StampedFloat64MultiArray, args.out_control_topic, 10)
        self.create_subscription(StampedFloat64MultiArray, args.inp_value_topic, self.input_value_callback, 10)
        self.create_subscription(Odometry, args.inp_state_topic, self.state_callback, 10)
        self.create_subscription(Timekeeper, args.inp_timekeeping_topic, self.timekeeping_callback, 10)
        self.watchdog_timer = self.create_timer(1 / COMMAND_HZ, self.watchdog_callback,
                                               clock=Clock(clock_type=ClockType.STEADY_TIME))

    def _now(self):
        now = self.get_clock().now().nanoseconds * 1e-9
        if self.last_clock is not None and now < self.last_clock:
            self._fault('clock_discontinuity')
        self.last_clock = now
        return now

    def _terminal(self):
        return self.availability in {'FAULTED', 'STOPPED'}

    def _fresh(self, now, steady):
        return (self.start_time is not None and self.input_value is not None and self.state_value is not None
                and all(stamp is not None and 0 <= now - stamp <= INPUT_EXPIRY_SEC
                        for stamp in (self.input_stamp, self.pose_stamp))
                and all(receipt is not None and 0 <= steady - receipt <= INPUT_EXPIRY_SEC
                        for receipt in (self.input_receipt, self.pose_receipt)))

    def timekeeping_callback(self, message):
        self._now()
        if self._terminal():
            return
        origin = float(message.start_time)
        if message.mode != self.expected_mode or not math.isfinite(origin) or origin < 0:
            self._fault('invalid_time_origin')
        elif self.start_time is not None and origin != self.start_time:
            self._fault('time_origin_changed')
        else:
            self.start_time = origin

    def state_callback(self, message):
        now, steady = self._now(), time.monotonic()
        if self._terminal():
            return
        try:
            state, stamp, frame = state_from_odometry(message)
        except (ValueError, TypeError, OverflowError):
            return
        if self.frame is not None and frame != self.frame:
            self._fault('pose_frame_changed')
            return
        if not 0 <= now - stamp <= INPUT_EXPIRY_SEC or (self.pose_stamp is not None and stamp <= self.pose_stamp):
            return
        self.state_value, self.pose_stamp, self.pose_receipt, self.frame = state, stamp, steady, frame
        self.publish_control_value()

    def input_value_callback(self, message):
        now, steady = self._now(), time.monotonic()
        if self._terminal() or self.start_time is None:
            return
        relative = float(message.timestamp)
        values = np.asarray(message.data, dtype=float)
        stamp = self.start_time + relative
        if (not math.isfinite(relative) or relative < 0 or values.size == 0
                or not np.all(np.isfinite(values)) or not 0 <= now - stamp <= INPUT_EXPIRY_SEC
                or (self.input_stamp is not None and stamp <= self.input_stamp)):
            return
        self.input_value, self.input_value_timestamp = values, relative
        self.input_stamp, self.input_receipt = stamp, steady
        self.publish_control_value()

    def publish_control_value(self):
        now = self._now()
        if self._terminal():
            return
        if not self._fresh(now, time.monotonic()):
            self.availability, self.reason = 'WAITING_INPUT', 'waiting for fresh pose and filter'
            self._publish(np.zeros(6), now)
            return
        if self.last_evaluated_stamp != self.input_stamp:
            try:
                values = self.input_value.copy()
                # The inherited Lie Bracket recipe also filters encoder data;
                # its scalar law consumes only the first, cost component.
                # Other original/custom controllers retain their vector API.
                if type(self.controller_obj).__name__ == 'Lie_Bracket_Controller':
                    values = float(values[0])
                command = np.asarray(self.controller_obj.controller_output(
                    self.input_value_timestamp, self.state_value.copy(), values), dtype=float).reshape(-1)
                if command.size != 6 or not np.all(np.isfinite(command)):
                    raise ValueError('controller must return six finite velocities')
                self.command, self.last_evaluated_stamp = command, self.input_stamp
            except Exception as error:
                self._fault(f'controller error: {type(error).__name__}: {error}')
                return
        # Numerical work may have consumed the remaining freshness budget.
        now = self._now()
        if self._terminal():
            return
        if not self._fresh(now, time.monotonic()):
            self.availability, self.reason = 'WAITING_INPUT', 'input expired during computation'
            self._publish(np.zeros(6), now)
            return
        self.availability, self.reason = 'ACTIVE', 'fresh pose and filter'
        self._publish(self.command, now)

    def watchdog_callback(self):
        now = self._now()
        if self._terminal():
            self._publish(np.zeros(6), now)
        else:
            self.publish_control_value()

    def _publish(self, command, now):
        command = [float(value) for value in command]
        twist = Twist()
        twist.linear.x, twist.linear.y, twist.linear.z = command[:3]
        twist.angular.x, twist.angular.y, twist.angular.z = command[3:]
        self.twist_publisher.publish(twist)
        if self.start_time is not None and math.isfinite(now) and now >= self.start_time:
            self.controller_publisher.publish(StampedFloat64MultiArray(
                header='Controller Value', timestamp=now-self.start_time, data=command))

    def _fault(self, reason):
        if not self._terminal():
            self.availability, self.reason = 'FAULTED', reason
            self.get_logger().error(reason)
        self._publish(np.zeros(6), self.get_clock().now().nanoseconds * 1e-9)

    def stop(self):
        self.availability, self.reason = 'STOPPED', 'operator shutdown'
        self.watchdog_timer.cancel()
        self._publish(np.zeros(6), self.get_clock().now().nanoseconds * 1e-9)


def main(args=None):
    arguments = list(sys.argv[1:] if args is None else args)
    if '--v3' in arguments:
        arguments.remove('--v3')
        from ros_esc.gesc_v3.node import main as v3_main
        return v3_main(arguments)
    # Legacy arguments are intentionally strict; V3 alone accepts ROS args.
    parse_controller_arguments(arguments)
    rclpy.init(args=[], signal_handler_options=SignalHandlerOptions.NO)
    node = executor = None
    with DeferredSignalShutdown() as shutdown:
        try:
            node = CustomController(arguments)
            executor = SingleThreadedExecutor()
            executor.add_node(node)
            while rclpy.ok() and not shutdown.requested:
                executor.spin_once(timeout_sec=.05)
        except KeyboardInterrupt:
            shutdown.request()
        finally:
            try:
                if node is not None:
                    node.stop()  # Publish final zero while the ROS context is live.
            finally:
                try:
                    if executor is not None:
                        executor.shutdown(timeout_sec=1.)
                    if node is not None:
                        node.destroy_node()
                finally:
                    rclpy.try_shutdown()


if __name__ == '__main__':
    main()
