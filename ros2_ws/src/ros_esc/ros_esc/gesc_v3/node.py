"""ROS shell for the sole V3 command owner."""

import json
import math
import time

import rclpy
from rclpy.clock import Clock, ClockType
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.signals import SignalHandlerOptions
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from ros_esc_interfaces.msg import (
    AlgorithmEvent, GaussianFill, SensorObservation, StampedFloat64MultiArray, Timekeeper,
)

from ros_esc.config_parsing import parse_object_config
from ros_esc.deferred_signal_shutdown import DeferredSignalShutdown
from ros_esc.profiles import resolve_profile
from .clock_delivery import ClockDelivery
from .core import V3Core
from .observation_node import pose_from_message, seconds, set_stamp
from .records import CoreConfig, Observation, Pose
from .worker import NumericalWorker


def observation_from_message(message):
    bases = {message.DEVICE_TIME: 'device', message.ESTIMATED_TIME: 'estimated',
             message.RECEIPT_TIME: 'receipt'}
    if not message.valid or message.timestamp_basis not in bases:
        raise ValueError('invalid observation')
    stamp = seconds(message.stamp)
    pose = Pose(stamp, message.source_pose.x, message.source_pose.y,
                message.source_pose.theta, message.frame_id)
    return Observation(message.source_instance, message.sequence, stamp,
        seconds(message.receipt_stamp), pose, message.phase_rad, message.raw_cost,
        message.sensor_x_m, message.sensor_y_m, bases[message.timestamp_basis],
        message.acquisition_uncertainty_sec, message.pose_support_age_sec,
        message.phase_support_age_sec,
        message.device_sequence if message.device_sequence_valid else None)


class V3Controller(Node):
    def __init__(self, *, worker=None, **kwargs):
        super().__init__('controller_node', **kwargs)
        self.declare_parameter('profile', 'gesc_v3')
        self.declare_parameter('environment', 'gazebo')
        selected = resolve_profile(self.get_parameter('profile').value,
                                   self.get_parameter('environment').value)
        if selected['algorithm'] != 'gesc_v3':
            raise ValueError('V3 owner requires a V3 profile')
        if 'use_sim_time' not in self._parameter_overrides:
            self.set_parameters([Parameter('use_sim_time', value=selected['use_sim_time'])])
        if self.get_parameter('use_sim_time').value != selected['use_sim_time']:
            raise ValueError('clock selection conflicts with environment')
        settings = selected['v3']
        config = CoreConfig(input_expiry=settings['input_expiry_sec'],
            control_hz=settings['control_hz'], max_vx=settings['max_vx'],
            max_wz=settings['max_wz'], k_vx=settings['k_vx'], k_wz=settings['k_wz'],
            sensor_radius=settings['sensor_radius_m'],
            preparation_timeout=settings['fill_timeout_sec'],
            maximum_snapshot=settings['maximum_fit_samples'])
        with open(selected['config_paths']['controller'], encoding='utf-8') as stream:
            controller = parse_object_config(json.load(stream))
        self.worker = worker or NumericalWorker()
        self.core = V3Core(controller, self.worker, config)
        self.delivery = ({kind: ClockDelivery(config.input_expiry)
                          for kind in ('pose', 'observation')}
                         if selected['use_sim_time'] else None)
        topics = selected['topics']
        self.command_topic = topics['command']
        self.command_publisher = self.create_publisher(Twist, topics['command'], 10)
        self.control_publisher = self.create_publisher(StampedFloat64MultiArray, topics['control'], 10)
        self.filter_publisher = self.create_publisher(StampedFloat64MultiArray, topics['filter'], 10)
        self.event_publisher = self.create_publisher(AlgorithmEvent, topics['events'], 10)
        self.fill_publisher = self.create_publisher(GaussianFill, topics['fills'], 10)
        self.create_subscription(Odometry, topics['pose'], self.pose_callback, 10)
        self.create_subscription(SensorObservation, topics['observation'], self.observation_callback, 10)
        self.create_subscription(Timekeeper, topics['timekeeper'], self.timekeeper_callback, 10)
        # A frozen /clock must not keep the last velocity command alive.
        self.steady_clock = Clock(clock_type=ClockType.STEADY_TIME)
        self.timer = self.create_timer(1/config.control_hz, self.tick, clock=self.steady_clock)
        self.ownership_timer = self.create_timer(1., self.check_ownership, clock=self.steady_clock)
        self.origin = None
        self.stopped = False
        self.get_logger().info(f'V3 {selected["environment"]}: one controller owner; optional recording/plots')

    def now_seconds(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def timekeeper_callback(self, message):
        # Only the relative plotting timestamps need this legacy origin.
        if math.isfinite(message.start_time) and message.start_time >= 0:
            self.origin = message.start_time

    def pose_callback(self, message):
        now = self.now_seconds()
        try:
            pose = pose_from_message(message)
        except (ValueError, TypeError, OverflowError):
            return
        steady = time.monotonic()
        if self.core.pose is not None and pose.frame != self.core.pose.frame:
            self.core.fault(now, 'pose_frame_changed')
            return
        if self.delivery is not None:
            self.delivery['pose'].add(pose.stamp, pose, now, steady)
            self._drain_delivery(now, steady)
        else:
            self.core.update_pose(pose, now, steady)

    def observation_callback(self, message):
        now = self.now_seconds()
        if not message.valid:
            if message.reason in ('time_origin_changed', 'clock_discontinuity', 'pose_frame_changed'):
                self.core.fault(now, message.reason)
            return
        try:
            observation = observation_from_message(message)
        except (ValueError, TypeError, OverflowError):
            return
        steady = time.monotonic()
        if self.delivery is not None:
            if observation.valid():
                self.delivery['observation'].add(observation.stamp, observation, now, steady,
                    available_at=max(observation.stamp, observation.receipt_stamp))
            self._drain_delivery(now, steady)
        else:
            self._ingest_observation(observation, now, steady)

    def _drain_delivery(self, now, steady):
        if self.delivery is None:
            return
        if self.core.last_tick is not None and now < self.core.last_tick:
            self.core.fault(now, 'clock_discontinuity')
        if self.core.terminal:
            for queue in self.delivery.values():
                queue.clear()
            return
        for record in self.delivery['pose'].ready(now, steady):
            self.core.update_pose(record.value, now, steady, receipt_steady=record.steady)
        for record in self.delivery['observation'].ready(now, steady):
            self._ingest_observation(record.value, now, steady, receipt_steady=record.steady)

    def _ingest_observation(self, observation, now, steady, *, receipt_steady=None):
        if self.core.ingest_observation(observation, now, steady, receipt_steady=receipt_steady):
            # Canonical plotting interfaces remain output-only. They cannot
            # feed another controller or serve as motion authorization.
            try:
                result = self.core.rolling.evaluate(round(now*1e9), observation.pose.yaw,
                                                    round(observation.pose.stamp*1e9))
                if result.output_valid and self.origin is not None:
                    diagnostic = StampedFloat64MultiArray()
                    diagnostic.timestamp = observation.stamp-self.origin
                    diagnostic.data = list(result.final_body)
                    self.filter_publisher.publish(diagnostic)
            except Exception as error:
                self.get_logger().warning(f'Optional filter telemetry unavailable: {error}')

    def check_ownership(self):
        # Only an actual competing command publisher is a conflict. Recorder,
        # plotter, subscriber presence or unavailable graph metadata are not gates.
        try:
            count = self.count_publishers(self.command_topic)
        except Exception as error:
            self.get_logger().warning(f'Command ownership inspection unavailable: {error}')
            return
        if count > 1:
            self.core.fault(self.now_seconds(), 'multiple_command_publishers')

    def tick(self):
        now = self.now_seconds()
        try:
            steady = time.monotonic()
            self._drain_delivery(now, steady)
            command = self.core.tick(now, steady)
        except Exception as error:
            command = self.core.fault(now, f'control_exception: {type(error).__name__}: {error}')
            self.get_logger().error(self.core.reason)
        try:
            self.publish_command(command, now)
        except Exception as error:
            self.core.fault(now, f'actuator_publish_error: {error}')
            self.get_logger().error(self.core.reason)
            # Best effort zero through the actual command endpoint.
            self.command_publisher.publish(Twist())
        try:
            self.publish_control_telemetry(command, now)
            self.publish_telemetry(now)
        except Exception as error:
            self.get_logger().warning(f'Optional telemetry unavailable: {error}')

    def publish_command(self, command, now):
        message = Twist()
        message.linear.x, message.angular.z = command.vx, command.wz
        self.command_publisher.publish(message)

    def publish_control_telemetry(self, command, now):
        control = StampedFloat64MultiArray()
        control.timestamp = max(0., now-(self.origin if self.origin is not None else now))
        control.data = [command.vx, 0., 0., 0., 0., command.wz]
        self.control_publisher.publish(control)

    def publish_telemetry(self, now):
        # No publication result or subscriber readiness participates in control.
        for event in self.core.drain_events():
            message = AlgorithmEvent()
            set_stamp(message.stamp, event.stamp)
            message.event_type = {
                'candidate': message.EVENT_CONVERGENCE_CANDIDATE,
                'fill_created': message.EVENT_FILL_CREATED,
                'best_source': message.EVENT_GOAL_REACHED,
                'escape_started': message.EVENT_ESCAPE_STARTED,
            }.get(event.kind, message.EVENT_STATE_TRANSITION)
            message.state_name = f'{self.core.availability}/{event.state}'
            message.state_valid = True
            message.detail = f'{event.kind}: {event.reason}'
            self.event_publisher.publish(message)
        for fill in self.core.drain_fills():
            message = GaussianFill()
            set_stamp(message.stamp, now)
            message.source_timestamp = fill.source_timestamp
            message.source_timestamp_valid = True
            message.frame_id = self.core.pose.frame
            for name in ('fill_id', 'cluster_id', 'revision', 'amplitude', 'sigma_major',
                         'sigma_minor', 'orientation', 'support_radius', 'exit_radius',
                         'confidence', 'sample_count', 'fit_residual',
                         'fit_condition_number', 'design_escalations', 'active', 'superseded'):
                setattr(message, name, getattr(fill, name))
            message.center_x, message.center_y = map(float, fill.center)
            message.covariance_xx = float(fill.covariance[0, 0])
            message.covariance_xy = float(fill.covariance[0, 1])
            message.covariance_yy = float(fill.covariance[1, 1])
            for name in ('covariance', 'principal_widths', 'support_radius', 'exit_radius',
                         'confidence', 'sample_count', 'fit_residual', 'design_escalations'):
                setattr(message, name+'_valid', True)
            message.fit_condition_number_valid = fill.fit_condition_number_valid
            self.fill_publisher.publish(message)

    def stop(self):
        if not self.stopped:
            self.stopped = True
            self.timer.cancel()
            now = self.now_seconds()
            try:
                self.publish_command(self.core.stop(now), now)
                try:
                    self.publish_telemetry(now)
                except Exception as error:
                    self.get_logger().warning(f'Optional shutdown telemetry unavailable: {error}')
            finally:
                self.worker.close()


def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = None
    executor = SingleThreadedExecutor()
    # Launchers may forward a second signal after the process group receives
    # the first one. Keep both signals deferred through final zero and worker /
    # executor cleanup, not only while callbacks are running.
    with DeferredSignalShutdown() as shutdown:
        try:
            node = V3Controller()
            executor.add_node(node)
            while rclpy.ok() and not shutdown.requested:
                executor.spin_once(timeout_sec=.05)
        finally:
            if node is not None:
                node.stop()
                executor.remove_node(node)
                node.destroy_node()
            executor.shutdown()
            rclpy.try_shutdown()


if __name__ == '__main__':
    main()
