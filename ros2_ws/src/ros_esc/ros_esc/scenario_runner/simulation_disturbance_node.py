#!/usr/bin/env python3

"""Relay simulation inputs after deterministic ROS-time delays."""

from collections import deque
from dataclasses import dataclass

from gazebo_msgs.srv import SpawnEntity
from nav_msgs.msg import Odometry

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions

from ros_esc.deferred_signal_shutdown import DeferredSignalShutdown
from ros_esc_interfaces.msg import CostBreakdown, SourceSampleProvenance
from ros_esc_interfaces.msg import StampedFloat64MultiArray
from std_msgs.msg import Bool


NANOSECONDS_PER_SECOND = 1_000_000_000


@dataclass(frozen=True)
class PendingMessage:
    """One message awaiting its deterministic release time."""

    release_time_ns: int
    sequence: int
    message: object


class DelayQueue:
    """FIFO delay queue for a single ordered ROS topic."""

    def __init__(self, delay_sec):
        """Create a queue with a nonnegative fixed delay."""
        self.delay_ns = round(float(delay_sec) * NANOSECONDS_PER_SECOND)
        if self.delay_ns < 0:
            raise ValueError('delay_sec must be nonnegative')
        self._messages = deque()
        self._sequence = 0

    def append(self, message, arrival_time_ns):
        """Queue a message relative to its ROS-time arrival."""
        self._messages.append(PendingMessage(
            release_time_ns=int(arrival_time_ns) + self.delay_ns,
            sequence=self._sequence,
            message=message,
        ))
        self._sequence += 1

    def pop_ready(self, now_ns):
        """Return all messages due at or before ``now_ns`` in input order."""
        ready = []
        while (
            self._messages
            and self._messages[0].release_time_ns <= int(now_ns)
        ):
            ready.append(self._messages.popleft().message)
        return ready

    def __len__(self):
        """Return the number of messages awaiting release."""
        return len(self._messages)


class SimulationDisturbanceNode(Node):
    """Delay raw cost, source-cost, and pose inputs in simulation only."""

    def __init__(self):
        """Declare the additive simulation-only relay contract."""
        super().__init__('gesc_gaussian_simulation_disturbance')
        self.declare_parameter('raw_cost_input_topic',
                               '/turtlebot3/cost_value_chatter')
        self.declare_parameter('source_cost_input_topic',
                               '/gesc_gaussian/source_cost')
        self.declare_parameter('pose_input_topic', '/odom')
        self.declare_parameter(
            'raw_cost_output_topic',
            '/gesc_gaussian/simulation/raw_cost_delayed',
        )
        self.declare_parameter(
            'source_cost_output_topic',
            '/gesc_gaussian/simulation/source_cost_delayed',
        )
        self.declare_parameter(
            'pose_output_topic',
            '/gesc_gaussian/simulation/pose_delayed',
        )
        self.declare_parameter('sensor_delay_sec', 0.0)
        self.declare_parameter('continuous_search_mode', 'stationary_v1')
        self.declare_parameter('provenance_input_topic', '/gesc_gaussian/v2/source_sample_provenance')
        self.declare_parameter('provenance_output_topic', '/gesc_gaussian/simulation/source_sample_provenance_delayed')
        self.declare_parameter('pose_delay_sec', 0.0)
        self.declare_parameter('publish_rate_hz', 100.0)
        self.declare_parameter('contact_probe_enabled', False)
        self.declare_parameter(
            'recording_ready_topic',
            '/gesc_gaussian/recording_ready',
        )

        sensor_delay = self._nonnegative('sensor_delay_sec')
        pose_delay = self._nonnegative('pose_delay_sec')
        publish_rate = float(self.get_parameter('publish_rate_hz').value)
        if publish_rate <= 0.0:
            raise ValueError('publish_rate_hz must be positive')

        self.raw_queue = DelayQueue(sensor_delay)
        self.source_queue = DelayQueue(sensor_delay)
        self.pose_queue = DelayQueue(pose_delay)
        mode = self._text('continuous_search_mode')
        if mode not in ('stationary_v1', 'rolling_gesc_v2'):
            raise ValueError('unsupported continuous_search_mode')
        self.provenance_queue = DelayQueue(sensor_delay) if mode == 'rolling_gesc_v2' else None
        if self.provenance_queue is not None:
            self.provenance_publisher = self.create_publisher(
                SourceSampleProvenance, self._text('provenance_output_topic'), 100,
            )
            self.create_subscription(
                SourceSampleProvenance, self._text('provenance_input_topic'),
                lambda message: self._enqueue(self.provenance_queue, message), 100,
            )
        self.latest_pose = None
        self.recording_ready = False
        self.contact_probe_requested = False
        self.raw_publisher = self.create_publisher(
            StampedFloat64MultiArray,
            self._text('raw_cost_output_topic'),
            100,
        )
        self.source_publisher = self.create_publisher(
            CostBreakdown,
            self._text('source_cost_output_topic'),
            100,
        )
        self.pose_publisher = self.create_publisher(
            Odometry,
            self._text('pose_output_topic'),
            100,
        )
        self.create_subscription(
            StampedFloat64MultiArray,
            self._text('raw_cost_input_topic'),
            lambda message: self._enqueue(self.raw_queue, message),
            100,
        )
        self.create_subscription(
            CostBreakdown,
            self._text('source_cost_input_topic'),
            lambda message: self._enqueue(self.source_queue, message),
            100,
        )
        self.create_subscription(
            Odometry,
            self._text('pose_input_topic'),
            self._pose_callback,
            100,
        )
        self.contact_probe_enabled = bool(
            self.get_parameter('contact_probe_enabled').value
        )
        if self.contact_probe_enabled:
            self.create_subscription(
                Bool,
                self._text('recording_ready_topic'),
                self._recording_ready_callback,
                10,
            )
            self.contact_probe_client = self.create_client(
                SpawnEntity, '/spawn_entity'
            )
        self.create_timer(1.0 / publish_rate, self._release_ready)

    def _text(self, name):
        return str(self.get_parameter(name).value)

    def _nonnegative(self, name):
        value = float(self.get_parameter(name).value)
        if value < 0.0:
            raise ValueError(f'{name} must be nonnegative')
        return value

    def _enqueue(self, queue, message):
        queue.append(message, self.get_clock().now().nanoseconds)

    def _pose_callback(self, message):
        self.latest_pose = message.pose.pose
        self._enqueue(self.pose_queue, message)

    def _recording_ready_callback(self, message):
        self.recording_ready = bool(message.data)

    @staticmethod
    def contact_probe_sdf():
        """Return the fixed static obstacle used by the positive control."""
        return """
<sdf version="1.6">
  <model name="phase08_contact_positive_control">
    <static>true</static>
    <link name="probe">
      <collision name="collision">
        <geometry><box><size>0.20 0.20 0.40</size></box></geometry>
      </collision>
      <visual name="visual">
        <geometry><box><size>0.20 0.20 0.40</size></box></geometry>
      </visual>
    </link>
  </model>
</sdf>
""".strip()

    def _spawn_contact_probe(self):
        if (
            not self.contact_probe_enabled
            or self.contact_probe_requested
            or not self.recording_ready
            or self.latest_pose is None
            or not self.contact_probe_client.service_is_ready()
        ):
            return
        request = SpawnEntity.Request()
        request.name = 'phase08_contact_positive_control'
        request.xml = self.contact_probe_sdf()
        request.initial_pose = self.latest_pose
        request.initial_pose.position.z = 0.20
        request.reference_frame = 'world'
        self.contact_probe_client.call_async(request)
        self.contact_probe_requested = True

    def _release_ready(self):
        now_ns = self.get_clock().now().nanoseconds
        self._spawn_contact_probe()
        for message in self.raw_queue.pop_ready(now_ns):
            self.raw_publisher.publish(message)
        for message in self.source_queue.pop_ready(now_ns):
            self.source_publisher.publish(message)
        if getattr(self, 'provenance_queue', None) is not None:
            for message in self.provenance_queue.pop_ready(now_ns):
                self.provenance_publisher.publish(message)
        for message in self.pose_queue.pop_ready(now_ns):
            self.pose_publisher.publish(message)


def main(args=None):
    """Run until interrupted, preserving normal ROS teardown."""
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = SimulationDisturbanceNode()
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


if __name__ == '__main__':
    main()
