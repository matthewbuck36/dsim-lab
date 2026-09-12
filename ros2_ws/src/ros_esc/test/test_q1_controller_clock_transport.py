"""Finite actual controller DDS fixture; scoped topics and no Gazebo/hardware."""

import sys
import time

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rosgraph_msgs.msg import Clock
from std_msgs.msg import Bool

from ros_esc.controller_node import controller_node_script as controller
from ros_esc.v2_stream import set_time
from ros_esc_interfaces.msg import AlgorithmEvent, AlgorithmState, StampedFloat64MultiArray, Timekeeper
from test_v2_controller_motion import arguments, state, pose, command, PREFIX


def test_real_controller_transport_holds_future_30hz_pose_between_10hz_clock_ticks(monkeypatch):
    rclpy.init(args=[])
    monkeypatch.setattr(sys, 'argv', ['controller_node', *arguments(),
                                    '--recording_ready_required', 'True',
                                    '--recording_ready_topic', PREFIX+'/ready'])
    node = controller.CustomController()
    driver = Node('q1_controller_clock_driver')
    executor = SingleThreadedExecutor()
    executor.add_node(node)
    executor.add_node(driver)
    types_topics = {
        'clock': (Clock, '/clock'), 'origin': (Timekeeper, PREFIX+'/timekeeper'),
        'pose': (Odometry, PREFIX+'/odom'), 'state': (AlgorithmState, PREFIX+'/state'),
        'command': (Twist, PREFIX+'/supervisor'), 'ready': (Bool, PREFIX+'/ready'),
        'filter': (StampedFloat64MultiArray, PREFIX+'/filter'),
    }
    publishers = {key: driver.create_publisher(cls, topic, 20)
                  for key, (cls, topic) in types_topics.items()}
    commands, events = [], []
    driver.create_subscription(Twist, PREFIX+'/cmd_vel', commands.append, 100)
    driver.create_subscription(AlgorithmEvent, '/gesc_gaussian/algorithm_events', events.append, 100)

    def until(predicate, seconds=3.):
        deadline = time.monotonic()+seconds
        while not predicate() and time.monotonic() < deadline:
            executor.spin_once(timeout_sec=.005)
        assert predicate(), 'bounded controller DDS delivery failed'

    def clock(ns):
        msg = Clock()
        set_time(msg.clock, ns)
        publishers['clock'].publish(msg)
        until(lambda: node.get_clock().now().nanoseconds == ns)

    def ready():
        publishers['ready'].publish(Bool(data=True))
        publishers['command'].publish(command())

    try:
        until(lambda: all(p.get_subscription_count() for p in publishers.values()))
        clock(2_600_000_000)
        publishers['origin'].publish(Timekeeper(mode='sim time', start_time=0.))
        until(lambda: node.v2_origin_ns == 0)
        publishers['state'].publish(state(AlgorithmState.STATE_SEARCH, stamp=2.6))
        publishers['pose'].publish(pose(2.585))
        publishers['filter'].publish(StampedFloat64MultiArray(timestamp=2.6, data=[.08, .04]))
        publishers['command'].publish(command())
        until(lambda: node.latest_algorithm_state is not None and node.state_value is not None
              and node.input_value is not None and node.supervisor_command_receipt_sec is not None)
        ready()
        until(lambda: node.recording_ready)
        publishers['filter'].publish(StampedFloat64MultiArray(timestamp=2.6, data=[.08, .04]))
        until(lambda: any(m.linear.x > 0 for m in commands))
        events.clear()
        pending_receipts = []
        for tick in range(9):
            held = 2_600_000_000+tick*100_000_000
            clock(held)
            ready()
            future_state = state(AlgorithmState.STATE_SEARCH, stamp=(held+50_000_000)*1e-9)
            publishers['state'].publish(future_state)
            until(lambda: bool(node.v2_admission.pending['state']))
            for offset in (19_000_000, 53_000_000, 87_000_000):
                source = held+offset
                publishers['pose'].publish(pose(source*1e-9))
                publishers['filter'].publish(StampedFloat64MultiArray(timestamp=source*1e-9,
                                                                      data=[.08, .04]))
                until(lambda: node.v2_admission.frontier.get('pose', (None,))[0] == source
                      and node.v2_admission.frontier.get('filter', (None,))[0] == source)
                entry = node.v2_admission.pending['pose'][-1]
                pending_receipts.append((entry.source_ns, entry.receipt_ns))
                assert entry.receipt_ns == held < entry.source_ns
                assert node.v2_pose_source_ns <= held
                assert node.v2_input_source_ns <= held
                assert node.latest_algorithm_state.stamp.sec*1_000_000_000+node.latest_algorithm_state.stamp.nanosec <= held
                assert not node.v2_admission_faults
        clock(3_500_000_000)
        ready()
        until(lambda: node.v2_pose_source_ns == 3_487_000_000
              and node.v2_input_source_ns == 3_487_000_000)
        assert len(pending_receipts) == 27
        assert round(node.pose_receipt_sec*1e9) == 3_400_000_000
        assert not events, [event.detail for event in events]
        assert any(m.linear.x > 0 for m in commands)

        # Excessive future input is still a hard stop. No simulator or robot
        # exists in this fixture; only this observer receives command messages.
        publishers['pose'].publish(pose(4.001))
        until(lambda: 'pose' in node.v2_admission_faults)
        until(lambda: bool(events))
        until(lambda: commands[-1].linear.x == commands[-1].angular.z == 0.)
        assert any('excessively future' in event.detail for event in events)

        # Fresh source recovery does not reuse revoked pending data.
        ready()
        publishers['state'].publish(state(AlgorithmState.STATE_SEARCH, stamp=3.5))
        publishers['pose'].publish(pose(3.5))
        until(lambda: node.v2_pose_source_ns == 3_500_000_000)
        previous_count = len(commands)
        publishers['filter'].publish(StampedFloat64MultiArray(timestamp=3.5, data=[.08, .04]))
        until(lambda: any(m.linear.x > 0 for m in commands[previous_count:]))
        assert not node.v2_admission_faults

        # No new /clock: the steady admission timer still forces zero when
        # original input/readiness receipts expire, without a ROS timer tick.
        previous_count = len(commands)
        until(lambda: len(commands) > previous_count and commands[-1].linear.x == 0., seconds=2.)
        assert 'steady receipt' in node._robust_fault_reason()
        node.destroy_node()
        executor.remove_node(node)
        node = None
        until(lambda: commands[-1].linear.x == commands[-1].angular.z == 0.)
    finally:
        if node is not None:
            executor.remove_node(node)
            node.destroy_node()
        executor.remove_node(driver)
        executor.shutdown(timeout_sec=2.)
        driver.destroy_node()
        rclpy.try_shutdown()
