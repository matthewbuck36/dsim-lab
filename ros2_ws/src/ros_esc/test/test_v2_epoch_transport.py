"""Real PDE/detector subscriptions bind both modes across supervisor epochs."""

import time

import pytest
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from nav_msgs.msg import Odometry
from rosgraph_msgs.msg import Clock
from ros_esc_interfaces.msg import (
    AlgorithmState, CentroidConvergenceDiagnostics, DetectorConfirmation,
    SearchEpochContext, Timekeeper,
)

from ros_esc.convergence_detector_node.convergence_detector_node_script import ConvergenceDetector
from ros_esc.pde_history_node.pde_history_script import PDEHistory
from ros_esc.v2_stream import canonical_json, set_time, stream_contract_id, time_to_ns
from test_v2_stream import descriptor


@pytest.mark.parametrize('metric,source_lead_ns', [
    ('pde_mean_v1', 0), ('centroid_windows_v2', 0),
    ('centroid_windows_v2', 33_333_333),
])
def test_real_owners_preserve_metrics_and_bind_each_authoritative_epoch(metric, source_lead_ns):
    config = descriptor(2)
    config['pose_topic'] = '/epoch_transport/pose'
    config['timekeeper_topic'] = '/epoch_transport/timekeeper'
    rclpy.init(args=[
        '--ros-args', '-p', 'use_sim_time:=true',
        '-p', 'algorithm_profile:=robust_gaussian_v1',
        '-p', 'continuous_search_mode:=rolling_gesc_v2',
        '-p', 'v2_run_id:=epoch-transport',
        '-p', 'v2_stream_config_json:=|-\n  ' + canonical_json(config),
        '-p', 'state_gating_enabled:=true',
        '-p', 'robust_search_epoch_reset_enabled:=true',
        '-p', 'convergence_metric_mode:=' + metric,
        '-p', 'pose_topic:=/epoch_transport/pose',
        '-p', 'algorithm_state_topic:=/epoch_transport/state',
        '-p', 'centroid_window_sec:=0.1', '-p', 'centroid_epsilon_m:=0.3',
        '-p', 'n_buffer:=12', '-p', 'k_periods:=3',
        '-p', 'min_fill_periods:=0.01', '-p', 'decay_rate:=15.0',
        '-p', 'convergence_confirmation_policy:=qualified_dwell',
        '-p', 'convergence_confirmation_dwell_sec:=0.2',
        '-r', '/odom:=/epoch_transport/pose',
    ])
    detector = ConvergenceDetector()
    pde = PDEHistory()
    driver = Node('epoch_transport_driver', use_global_arguments=False)
    executor = SingleThreadedExecutor()
    for node in (detector, pde, driver): executor.add_node(node)
    outputs = []
    diagnostics = []
    clock_pub = driver.create_publisher(Clock, '/clock', 10)
    pose_pub = driver.create_publisher(Odometry, config['pose_topic'], 10)
    keeper_pub = driver.create_publisher(Timekeeper, config['timekeeper_topic'], 10)
    state_pub = driver.create_publisher(AlgorithmState, '/epoch_transport/state', 10)
    epoch_pub = driver.create_publisher(SearchEpochContext, '/gesc_gaussian/v2/search_epoch', 10)
    driver.create_subscription(DetectorConfirmation, '/gesc_gaussian/v2/detector_confirmation', outputs.append, 10)
    driver.create_subscription(CentroidConvergenceDiagnostics,
                               '/gesc_gaussian/v2/convergence_diagnostics', diagnostics.append, 10)

    def until(predicate, seconds=2.):
        deadline = time.monotonic() + seconds
        while not predicate() and time.monotonic() < deadline:
            executor.spin_once(timeout_sec=.01)
        assert predicate(), 'bounded DDS delivery failed'

    try:
        until(lambda: all(pub.get_subscription_count() for pub in
                          (clock_pub, pose_pub, keeper_pub, state_pub, epoch_pub)))
        keeper_pub.publish(Timekeeper(mode='sim time', start_time=0.))
        until(lambda: detector.v2_binding.binding.origin_ns == pde.v2_evidence.binding.origin_ns == 0)
        sequence = 0
        for epoch in (1, 2):
            start = epoch * 2_000_000_000
            for index in range(13):
                stamp_ns = start + index * 100_000_000
                clock = Clock()
                set_time(clock.clock, stamp_ns)
                clock_pub.publish(clock)
                until(lambda: detector.get_clock().now().nanoseconds == stamp_ns
                      and pde.get_clock().now().nanoseconds == stamp_ns)
                state = AlgorithmState(state=1, state_valid=True, run_id='epoch-transport',
                                       run_id_valid=True, algorithm_profile='robust_gaussian_v1',
                                       state_elapsed_sec=index / 10., state_elapsed_valid=True)
                set_time(state.stamp, stamp_ns)
                state_pub.publish(state)
                until(lambda: detector.search_gate.active and (
                    not detector.centroid_mode or detector.centroid_state_source_ns == stamp_ns))
                sequence += 1
                context = SearchEpochContext(schema_version=1, run_id='epoch-transport',
                                             stream_contract_id=stream_contract_id(config, 0),
                                             frame_id='odom', search_epoch=epoch,
                                             context_sequence=sequence, algorithm_state=1, valid=True)
                set_time(context.stamp, stamp_ns)
                set_time(context.started_at, start)
                epoch_pub.publish(context)
                until(lambda: detector.v2_binding.binding.last_sequence == sequence
                      and pde.v2_evidence.binding.last_sequence == sequence)
                sample = Odometry()
                source_ns = stamp_ns + source_lead_ns
                set_time(sample.header.stamp, source_ns)
                sample.header.frame_id = 'odom'
                sample.pose.pose.position.x, sample.pose.pose.position.y = float(epoch), 2.
                sample.pose.pose.orientation.w = 1.
                pose_pub.publish(sample)
                if source_lead_ns:
                    until(lambda: bool(detector.v2_binding.pending)
                          and bool(pde.v2_evidence.pending))
                    assert detector.centroid_pose_source_ns != source_ns
                    set_time(clock.clock, stamp_ns + 100_000_000)
                    clock_pub.publish(clock)
                if detector.centroid_mode:
                    until(lambda: detector.centroid_pose_source_ns == source_ns)
                else:
                    until(lambda: detector.v2_binding.history is not None
                          and time_to_ns(detector.v2_binding.history.input_end) == stamp_ns)
            until(lambda: any(result.search_epoch == epoch for result in outputs))
        assert [result.search_epoch for result in outputs] == [1, 2]
        assert detector.sub is None  # No unbound canonical array enters arm C.
        assert [result.center_x_m for result in outputs] == pytest.approx([1., 2.])
        if source_lead_ns:
            assert detector.centroid_pose_receipt_ns < detector.centroid_pose_source_ns
            until(lambda: any(diagnostic.confirmed for diagnostic in diagnostics))
            for diagnostic in diagnostics:
                if diagnostic.metric_valid:
                    assert time_to_ns(diagnostic.receipt_stamp) < time_to_ns(diagnostic.source_stamp)
                    assert time_to_ns(diagnostic.source_stamp) <= time_to_ns(diagnostic.stamp)
        for result in outputs:
            assert time_to_ns(result.history_start) >= result.search_epoch * 2_000_000_000
            assert result.source_stamp_kind == 'pose_input'
            assert result.history_kind == ('centroid_windows' if detector.centroid_mode else 'pde_input_support')
            assert result.legacy_r_mean_valid != result.convergence_score_valid
    finally:
        for node in (detector, pde, driver): executor.remove_node(node)
        executor.shutdown(timeout_sec=2.)
        for node in (detector, pde, driver): node.destroy_node()
        rclpy.shutdown()
