"""Exercise the real V2 subscriptions, simulated clock and typed publisher."""

import time
import math

from nav_msgs.msg import Odometry
import pytest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rosgraph_msgs.msg import Clock
from std_msgs.msg import Bool

from ros_esc.convergence_detector_node.convergence_detector_node_script import ConvergenceDetector
from ros_esc.experiment_recording.validate_run import centroid_diagnostic_errors
from ros_esc_interfaces.msg import AlgorithmState, CentroidConvergenceDiagnostics


@pytest.mark.parametrize('metric_mode,window,epsilon,history', [
    ('centroid_windows_v2', 3., .06, 18),
    ('centroid_two_block_v2', 6., .18, 36),
])
def test_centroid_transport_uses_selected_pose_and_simulated_time_without_pde(
        metric_mode, window, epsilon, history):
    rclpy.init(args=[
        '--ros-args', '-p', 'use_sim_time:=true',
        '-p', 'algorithm_profile:=robust_gaussian_v1',
        '-p', 'state_gating_enabled:=true',
        '-p', 'convergence_metric_mode:=' + metric_mode,
        '-p', f'centroid_window_sec:={window}',
        '-p', f'centroid_epsilon_m:={epsilon}',
        '-p', 'pose_topic:=/centroid_transport/pose',
        '-p', 'algorithm_state_topic:=/centroid_transport/state',
        '-p', 'convergence_diagnostics_topic:=/centroid_transport/diagnostics',
        '-p', 'recording_ready_required:=true',
        '-p', 'recording_ready_topic:=/centroid_transport/ready',
    ])
    detector = ConvergenceDetector()
    driver = Node('centroid_transport_driver', use_global_arguments=False)
    executor = SingleThreadedExecutor()
    executor.add_node(detector)
    executor.add_node(driver)
    messages = []
    clock = driver.create_publisher(Clock, '/clock', 10)
    pose = driver.create_publisher(Odometry, '/centroid_transport/pose', 10)
    state = driver.create_publisher(AlgorithmState, '/centroid_transport/state', 10)
    ready = driver.create_publisher(Bool, '/centroid_transport/ready', 10)
    driver.create_subscription(
        CentroidConvergenceDiagnostics, '/centroid_transport/diagnostics',
        messages.append, 10,
    )

    def spin_until(predicate, seconds=2.0):
        deadline = time.monotonic() + seconds
        while not predicate() and time.monotonic() < deadline:
            executor.spin_once(timeout_sec=0.01)
        assert predicate(), 'bounded ROS delivery did not complete'

    try:
        spin_until(lambda: all(pub.get_subscription_count() for pub in (clock, pose, state, ready)))
        assert detector.sub is None
        assert detector.pose_subscriber.topic_name == '/centroid_transport/pose'
        for index in range(history * 10 + 1):
            stamp_ns = 1_000_000_000 + index * 100_000_000
            stamp = detector._centroid_time(stamp_ns)
            clock.publish(Clock(clock=stamp))
            spin_until(lambda: detector.get_clock().now().nanoseconds == stamp_ns)
            ready.publish(Bool(data=True))
            current = AlgorithmState()
            current.stamp = stamp
            current.run_id, current.run_id_valid = 'transport-run', True
            current.algorithm_profile = 'robust_gaussian_v1'
            current.state, current.state_valid = AlgorithmState.STATE_SEARCH, True
            current.state_elapsed_sec, current.state_elapsed_valid = index / 10, True
            state.publish(current)
            spin_until(lambda: detector._centroid_state_ready(stamp_ns)
                       and detector.centroid_state_receipt_ns == stamp_ns
                       and detector._centroid_recording_authorized())
            sample = Odometry()
            sample.header.stamp, sample.header.frame_id = stamp, 'odom'
            sample.pose.pose.position.x, sample.pose.pose.position.y = 1.0, 2.0
            if metric_mode == 'centroid_two_block_v2':
                angle = 2 * math.pi * (index / 10) / 12.2819299136
                sample.pose.pose.position.x += .35 * math.cos(angle)
                sample.pose.pose.position.y += .35 * math.sin(angle)
            sample.pose.pose.orientation.w = 1.0
            pose.publish(sample)
            spin_until(lambda: any(
                msg.source_valid and detector._centroid_stamp_ns(msg.source_stamp) == stamp_ns
                for msg in messages[-3:]
            ))
        confirmed = [message for message in messages if message.confirmed]
        assert len(confirmed) == 1
        result = confirmed[0]
        assert detector._centroid_stamp_ns(result.history_end) == (1+history)*1_000_000_000
        assert result.represented_duration_sec == pytest.approx(float(history))
        assert result.metric_mode == metric_mode
        assert detector.centroid_config.metric_mode == metric_mode
        if metric_mode == 'centroid_windows_v2':
            assert result.center_x_m == pytest.approx(1.0)
            assert result.center_y_m == pytest.approx(2.0)
            assert result.score_m == pytest.approx(0.0, abs=1e-12)
        else:
            # Nonzero orbit response distinguishes the actual selected law
            # from a renamed five-shift score over the same observed support.
            assert .14 < result.score_m < .16
            assert result.score_m != pytest.approx(sum(result.displacement_m))
        assert centroid_diagnostic_errors(messages, expected_metric_mode=metric_mode) == []
    finally:
        executor.remove_node(detector)
        executor.remove_node(driver)
        executor.shutdown(timeout_sec=2.0)
        detector.destroy_node()
        driver.destroy_node()
        rclpy.shutdown()
