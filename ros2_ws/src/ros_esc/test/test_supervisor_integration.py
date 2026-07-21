"""Non-Gazebo ROS integration coverage for the Phase 02 supervisor."""

import threading
import time

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    CostBreakdown,
    GaussianFill,
    StampedFloat64MultiArray,
)
from std_msgs.msg import Bool


def _wait_for(predicate, timeout=3.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return False


def test_supervisor_request_result_and_stop_failsafe():
    rclpy.init()
    overrides = [
        Parameter("supervisor_publish_rate_hz", value=100.0),
        Parameter("startup_timeout_sec", value=1.0),
        Parameter("convergence_hold_sec", value=0.05),
        Parameter("goal_hold_sec", value=0.05),
        Parameter("undesired_score_hold_sec", value=0.05),
        Parameter("verification_max_sec", value=0.5),
        Parameter("fill_design_timeout_sec", value=0.5),
        Parameter("stale_pose_sec", value=0.5),
        Parameter("stale_sensor_sec", value=0.5),
    ]
    supervisor = SupervisorNode(parameter_overrides=overrides)
    peer = Node("phase02_supervisor_test_peer")
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(supervisor)
    executor.add_node(peer)

    states = []
    requests = []
    commands = []
    events = []
    peer.create_subscription(
        AlgorithmState, "/gesc_gaussian/algorithm_state", states.append, 10
    )
    peer.create_subscription(
        StampedFloat64MultiArray,
        "/gesc_gaussian/fill_requests",
        requests.append,
        10,
    )
    peer.create_subscription(
        Twist, "/gesc_gaussian/supervisor_command", commands.append, 10
    )
    peer.create_subscription(
        AlgorithmEvent, "/gesc_gaussian/algorithm_events", events.append, 10
    )
    pose_pub = peer.create_publisher(Odometry, "/odom", 10)
    source_pub = peer.create_publisher(
        CostBreakdown, "/gesc_gaussian/source_cost", 10
    )
    convergence_pub = peer.create_publisher(
        StampedFloat64MultiArray, "/gesc_gaussian/convergence_status", 10
    )
    fill_pub = peer.create_publisher(
        GaussianFill, "/gesc_gaussian/gaussian_fills", 10
    )
    stop_pub = peer.create_publisher(Bool, "/gesc_gaussian/stop_requested", 10)

    thread = threading.Thread(target=executor.spin, daemon=True)
    thread.start()
    try:
        odom = Odometry()
        odom.pose.pose.orientation.w = 1.0
        source = CostBreakdown()
        source.source_timestamp = 7.0
        source.source_timestamp_valid = True
        source.channel_count = 1
        source.raw_cost = [-1.0]
        source.raw_cost_valid = True
        source.source_score = [0.2]
        source.source_score_valid = True
        convergence = StampedFloat64MultiArray()
        convergence.header = "CONVERGENCE_STATUS"
        convergence.timestamp = 42.0
        convergence.data = [-0.1, 0.0, 0.0, 1.0, 2.0, 0.9, 1.9, 3.0]

        deadline = time.monotonic() + 0.3
        while time.monotonic() < deadline and not requests:
            pose_pub.publish(odom)
            source_pub.publish(source)
            convergence_pub.publish(convergence)
            time.sleep(0.01)

        assert _wait_for(lambda: len(requests) == 1)
        assert any(
            state.state == AlgorithmState.STATE_DESIGN_OR_MERGE_FILL
            for state in states
        )
        assert requests[0].timestamp == convergence.timestamp
        assert list(requests[0].data) == list(convergence.data)

        fill = GaussianFill()
        fill.source_timestamp = requests[0].timestamp
        fill.source_timestamp_valid = True
        fill.fill_id = 1
        fill.active = True
        fill.covariance_valid = True
        fill.principal_widths_valid = True
        fill.sigma_major = 0.4
        fill.sigma_minor = 0.4
        fill_pub.publish(fill)
        assert _wait_for(
            lambda: any(
                state.state == AlgorithmState.STATE_ESCAPE_REPULSE
                for state in states
            )
        )

        stop = Bool()
        stop.data = True
        stop_pub.publish(stop)
        assert _wait_for(
            lambda: states and states[-1].state == AlgorithmState.STATE_FAILSAFE
        )
        assert states[-1].failsafe is True
        assert commands
        assert all(
            command.linear.x == 0.0 and command.angular.z == 0.0
            for command in commands
        )
        transition_events = [
            event
            for event in events
            if event.event_type == AlgorithmEvent.EVENT_STATE_TRANSITION
        ]
        assert len(transition_events) >= 4
        assert _wait_for(
            lambda: any(
                event.event_type == AlgorithmEvent.EVENT_FAILSAFE
                for event in events
            )
        )
    finally:
        executor.shutdown()
        thread.join(timeout=1.0)
        executor.remove_node(peer)
        executor.remove_node(supervisor)
        peer.destroy_node()
        supervisor.destroy_node()
        rclpy.shutdown()
