#!/usr/bin/env python3
"""Adapt observed cost/pose/encoder messages into one timestamped observation."""

import math
import uuid

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter

from ros_esc.profiles import resolve_profile
from .observation import ObservationBuilder
from .records import Pose


def seconds(stamp):
    if not 0 <= int(stamp.nanosec) < 1_000_000_000:
        raise ValueError('invalid ROS nanoseconds')
    value = int(stamp.sec) + int(stamp.nanosec) * 1e-9
    if not math.isfinite(value) or not 0 <= value < 2_147_483_647:
        raise ValueError('invalid ROS time')
    return value


def set_stamp(target, value):
    if not math.isfinite(value) or not 0 <= value < 2_147_483_647:
        raise ValueError('invalid ROS time')
    nanoseconds = round(value * 1_000_000_000)
    target.sec, target.nanosec = divmod(nanoseconds, 1_000_000_000)


def pose_from_message(message):
    position = message.pose.pose.position
    quaternion = message.pose.pose.orientation
    values = (position.x, position.y, quaternion.x, quaternion.y, quaternion.z, quaternion.w)
    if not all(math.isfinite(value) for value in values):
        raise ValueError('nonfinite pose')
    norm = math.sqrt(sum(value * value for value in values[2:]))
    if not math.isfinite(norm) or norm <= 1e-9 or not message.header.frame_id.strip():
        raise ValueError('invalid pose frame or quaternion')
    x, y, z, w = (value / norm for value in values[2:])
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return Pose(seconds(message.header.stamp), position.x, position.y, yaw,
                message.header.frame_id)


class SensorObservationNode(Node):
    """No actuator publisher and no dependence on recording or field truth."""

    def __init__(self, **kwargs):
        super().__init__('sensor_observation_node', **kwargs)
        from nav_msgs.msg import Odometry
        from ros_esc_interfaces.msg import SensorObservation, StampedFloat64MultiArray, Timekeeper

        self.message_type = SensorObservation
        self.declare_parameter('profile', 'gesc_v3')
        self.declare_parameter('environment', 'gazebo')
        selected = resolve_profile(self.get_parameter('profile').value,
                                   self.get_parameter('environment').value)
        if selected['algorithm'] != 'gesc_v3':
            raise ValueError('sensor observation adapter requires the gesc_v3 algorithm')
        # Preserve an explicit startup override, rather than changing its clock
        # after ROS subscriptions are active. An incompatible override is an
        # explicit configuration error.
        if 'use_sim_time' not in self._parameter_overrides:
            self.set_parameters([Parameter('use_sim_time', value=selected['use_sim_time'])])
        if self.get_parameter('use_sim_time').value != selected['use_sim_time']:
            raise ValueError('use_sim_time disagrees with selected environment')
        settings = selected['v3']
        self.expected_mode = 'sim time' if selected['use_sim_time'] else 'real time'
        self.expected_frame = selected['frame_id']
        self.basis = 'estimated' if selected['use_sim_time'] else 'receipt'
        self.builder = ObservationBuilder(uuid.uuid4().hex, radius=settings['sensor_radius_m'],
                                          expiry=settings['input_expiry_sec'])
        self.origin = None
        self.last_clock = None
        self.fault = None
        self.last_notice = None
        self.publisher = self.create_publisher(SensorObservation, selected['topics']['observation'], 10)
        self.create_subscription(Odometry, selected['topics']['pose'], self.pose_callback, 10)
        self.create_subscription(StampedFloat64MultiArray, selected['topics']['encoder'], self.phase_callback, 10)
        self.create_subscription(StampedFloat64MultiArray, selected['topics']['cost'], self.cost_callback, 10)
        self.create_subscription(Timekeeper, selected['topics']['timekeeper'], self.timekeeper_callback, 10)
        self.create_timer(1 / settings['control_hz'], self.poll)

    def now_seconds(self):
        now = self.get_clock().now().nanoseconds * 1e-9
        if self.last_clock is not None and now < self.last_clock:
            self._fault('clock_discontinuity', now)
        self.last_clock = now
        return now

    def _notice(self, reason, now):
        if reason == self.last_notice:
            return
        self.last_notice = reason
        message = self.message_type()
        set_stamp(message.stamp, now)
        set_stamp(message.receipt_stamp, now)
        message.source_instance = self.builder.source_instance
        message.sequence = self.builder.sequence
        message.timestamp_basis = message.ESTIMATED_TIME if self.basis == 'estimated' else message.RECEIPT_TIME
        message.frame_id = self.expected_frame
        message.raw_cost = math.nan
        message.phase_rad = math.nan
        message.acquisition_uncertainty_sec = math.nan
        message.valid = False
        message.reason = reason
        self.publisher.publish(message)

    def _fault(self, reason, now):
        if self.fault is None:
            self.fault = reason
            self.builder.fault = reason
            self.builder.pending = None
            self._notice(reason, now)

    def timekeeper_callback(self, message):
        now = self.now_seconds()
        if self.fault:
            return
        value = float(message.start_time)
        # Initial /clock delivery may trail Timekeeper delivery. Binding the
        # finite origin does not authorize a sample: each input still needs a
        # nonfuture, fresh source stamp before it can be used.
        if message.mode != self.expected_mode or not math.isfinite(value) or not 0 <= value < 2_147_483_647:
            self._fault('clock_discontinuity', now)
            return
        if self.origin is not None and value != self.origin:
            self._fault('time_origin_changed', now)
        else:
            self.origin = value

    def _relative(self, value):
        value = float(value)
        if self.origin is None or not math.isfinite(value) or value < 0:
            raise ValueError('missing_origin_or_invalid_relative_time')
        stamp = self.origin + value
        if not math.isfinite(stamp) or stamp >= 2_147_483_647:
            raise ValueError('invalid_relative_time')
        return stamp

    def pose_callback(self, message):
        now = self.now_seconds()
        if self.fault:
            return
        try:
            pose = pose_from_message(message)
            if pose.frame != self.expected_frame:
                self._fault('pose_frame_changed', now)
                return
            if not 0 <= now - pose.stamp <= self.builder.expiry:
                raise ValueError('pose_stale_or_future')
            self.builder.add_pose(pose)
            self.poll()
        except (TypeError, ValueError, OverflowError) as error:
            self._notice(str(error), now)

    def phase_callback(self, message):
        now = self.now_seconds()
        if self.fault:
            return
        try:
            stamp = self._relative(message.timestamp)
            if len(message.data) != 1 or not math.isfinite(message.data[0]):
                raise ValueError('invalid_phase')
            if not 0 <= now - stamp <= self.builder.expiry:
                raise ValueError('phase_stale_or_future')
            # The environment's encoder owns its calibration; never apply the
            # 54-degree physical offset again to this already measured angle.
            self.builder.add_phase(stamp, float(message.data[0]))
            self.poll()
        except (TypeError, ValueError, OverflowError) as error:
            self._notice(str(error), now)

    def cost_callback(self, message):
        now = self.now_seconds()
        if self.fault:
            return
        try:
            stamp = self._relative(message.timestamp)
            if len(message.data) != 1 or not math.isfinite(message.data[0]):
                raise ValueError('invalid_cost')
            if not 0 <= now - stamp <= self.builder.expiry:
                raise ValueError('cost_stale_or_future')
            if not self.builder.add_cost(stamp, float(message.data[0]), now,
                                         basis=self.basis, uncertainty=math.nan):
                raise ValueError(self.builder.reason)
            self.poll()
        except (TypeError, ValueError, OverflowError) as error:
            self._notice(str(error), now)

    def poll(self):
        now = self.now_seconds()
        if self.fault:
            return
        pending = self.builder.pending
        observation = self.builder.take(now)
        if observation is None:
            if pending is not None and self.builder.pending is None:
                self._notice(self.builder.reason, now)
            return
        message = self.message_type()
        set_stamp(message.stamp, observation.stamp)
        set_stamp(message.receipt_stamp, observation.receipt_stamp)
        message.source_instance = observation.source_instance
        message.sequence = observation.sequence
        message.device_sequence_valid = False
        message.timestamp_basis = message.ESTIMATED_TIME if self.basis == 'estimated' else message.RECEIPT_TIME
        message.frame_id = observation.pose.frame
        message.source_pose.x, message.source_pose.y = observation.pose.x, observation.pose.y
        message.source_pose.theta = observation.pose.yaw
        message.raw_cost, message.phase_rad = observation.raw_cost, observation.phase
        message.sensor_x_m, message.sensor_y_m = observation.sensor_x, observation.sensor_y
        message.pose_support_age_sec = observation.pose_support_age
        message.phase_support_age_sec = observation.phase_support_age
        message.acquisition_uncertainty_sec = math.nan
        message.valid, message.reason = True, 'valid'
        self.last_notice = None
        self.publisher.publish(message)


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = SensorObservationNode()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
