"""Actual Arm B DDS: supplied centroid candidate, real verification and fit.

Synthetic pose/raw-cost inputs reuse the small-bowl shape from the independent
Gaussian parity fixture. No detector, estimator, transition or fill-result
output is replaced. No simulator, controller, hardware or cmd_vel consumer runs.
"""
from copy import deepcopy
import json
import math
import threading
import time

from builtin_interfaces.msg import Time
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rosgraph_msgs.msg import Clock
from std_msgs.msg import Bool
from ros_esc.gaussian_fill_node.gaussian_fill_script import GaussianFill as GaussianOwner
from ros_esc.supervisor_node.supervisor_node_script import SupervisorNode
from ros_esc.supervisor_node.state_machine import State, SupervisorStateMachine
from ros_esc.stationary_fill_protocol import stationary_request_errors
from ros_esc.v2_stream import set_time, time_to_ns
from ros_esc_interfaces.msg import (
    AlgorithmEvent, AlgorithmState, CentroidConvergenceDiagnostics, CostBreakdown,
    GaussianFill, StampedFloat64MultiArray, StationaryFillRequest, Timekeeper,
)
from test_q5_stationary_fill_protocol import ORIGIN_NS, confirmation

NS = 1_000_000_000
PREFIX = '/q5_stationary_transport'


def stamp(value):
    return set_time(Time(), int(value))


def test_actual_stationary_centroid_verification_fill_and_result_acknowledgment(
        metric_mode='centroid_windows_v2'):
    parameters = dict(
        use_sim_time='true', algorithm_profile='robust_gaussian_v1',
        convergence_metric_mode=metric_mode, continuous_search_mode='stationary_v1',
        pose_topic=PREFIX+'/pose', source_cost_topic=PREFIX+'/source',
        timekeeper_topic=PREFIX+'/origin', algorithm_state_topic=PREFIX+'/state',
        algorithm_event_topic=PREFIX+'/events', gaussian_fill_diagnostics_topic=PREFIX+'/fills',
        fill_request_topic=PREFIX+'/unused_legacy_request',
        convergence_diagnostics_topic=PREFIX+'/centroid', supervisor_command_topic=PREFIX+'/command',
        supervisor_stop_topic=PREFIX+'/stop', recording_ready_required='true',
        recording_ready_topic=PREFIX+'/ready', operating_bounds_enabled='false',
        extremum_classification_mode='counted_candidates', known_source_count='2', max_fill_clusters='1',
        candidate_cost_rotation_period_sec='0.25', candidate_cost_required_rotations='2',
        candidate_informed_fill_enabled='true', recenter_after_escape='false',
    )
    arguments = ['--ros-args']
    for name, value in parameters.items():
        arguments.extend(['-p', name+':='+value])
    rclpy.init(args=arguments)
    executor, nodes = MultiThreadedExecutor(num_threads=4), []
    deadline = time.monotonic()+35.
    stop_producer, producer_errors = threading.Event(), []
    producer = None
    try:
        supervisor = SupervisorNode(); nodes.append(supervisor)
        # The run starts at a nonzero simulated epoch. Hold only the main timer
        # while the actual ROS clock and initial sensor inputs are initialized;
        # no transition is substituted once the real input flow begins.
        supervisor.timer.cancel()
        gaussian = GaussianOwner(); nodes.append(gaussian)
        driver = Node('q5_stationary_transport_driver', use_global_arguments=False)
        nodes.append(driver)
        for node in nodes:
            executor.add_node(node)
        states, requests, fills, events, commands, legacy_requests = [], [], [], [], [], []
        for kind, topic, destination in (
            (AlgorithmState, PREFIX+'/state', states),
            (StationaryFillRequest, '/gesc_gaussian/v2/stationary_fill_requests', requests),
            (GaussianFill, PREFIX+'/fills', fills), (AlgorithmEvent, PREFIX+'/events', events),
            (Twist, PREFIX+'/command', commands),
            (StampedFloat64MultiArray, PREFIX+'/unused_legacy_request', legacy_requests),
        ):
            driver.create_subscription(kind, topic, destination.append, 100)
        pub = {name: driver.create_publisher(kind, topic, 100) for name, kind, topic in (
            ('clock', Clock, '/clock'), ('origin', Timekeeper, PREFIX+'/origin'),
            ('pose', Odometry, PREFIX+'/pose'), ('source', CostBreakdown, PREFIX+'/source'),
            ('ready', Bool, PREFIX+'/ready'), ('stop', Bool, PREFIX+'/stop'),
            ('confirmation', CentroidConvergenceDiagnostics, PREFIX+'/centroid'),
        )}

        def until(predicate, limit=3.):
            end = min(deadline, time.monotonic()+limit)
            while not predicate() and time.monotonic() < end:
                assert not producer_errors, producer_errors
                executor.spin_once(timeout_sec=.001)
            assert not producer_errors, producer_errors
            assert predicate(), dict(state=supervisor.machine.state.name,
                transition=supervisor.machine.transition_reason,
                supervisor=supervisor.stationary_centroid.last_reason,
                gaussian=gaussian.stationary_fill.last_reason,
                generation=gaussian.fill_registry.generation,
                requests=len(requests), fills=len(fills),
                events=[(e.event_type, e.reason_code, e.detail) for e in events[-5:]])

        def sample(value):
            pub['clock'].publish(Clock(clock=stamp(value)))
            pub['ready'].publish(Bool(data=True))
            phase = 2*math.pi*((value-ORIGIN_NS)/NS)/3.
            radius = .06+.008*math.cos(3*phase)
            x, y = radius*math.cos(phase), .8*radius*math.sin(phase)
            pose = Odometry()
            pose.header.frame_id, pose.header.stamp = 'odom', stamp(value)
            pose.pose.pose.position.x, pose.pose.pose.position.y = x, y
            pose.pose.pose.orientation.w = 1.
            pub['pose'].publish(pose)
            source = CostBreakdown()
            source.stamp = stamp(value)
            source.source_timestamp = (value-ORIGIN_NS)/NS
            source.source_timestamp_valid = source.raw_cost_valid = True
            source.channel_count, source.raw_cost = 1, [-1.+x*x+.5*y*y]
            pub['source'].publish(source)

        def tick(value):
            sample(value)
            until(lambda: supervisor.get_clock().now().nanoseconds == value
                and gaussian.get_clock().now().nanoseconds == value
                and gaussian.pose_snapshots
                and abs(gaussian.pose_snapshots[-1].stamp_sec-value/NS) < 1e-8
                and gaussian.cost_snapshots
                and abs(gaussian.cost_snapshots[-1].stamp_sec-value/NS) < 1e-8)

        until(lambda: all(p.get_subscription_count() for p in pub.values()), 8.)
        until(lambda: gaussian.gaussian_fill_diagnostics_publisher.get_subscription_count() >= 2)
        tick(ORIGIN_NS)
        supervisor.machine = SupervisorStateMachine(
            now_sec=ORIGIN_NS/NS, config=supervisor.machine.config)
        supervisor.started_sec = ORIGIN_NS/NS
        pub['origin'].publish(Timekeeper(mode='sim time', start_time=ORIGIN_NS/NS))
        until(lambda: supervisor.stationary_centroid.origin_ns == ORIGIN_NS
            and gaussian.stationary_fill.origin_ns == ORIGIN_NS
            and supervisor.stationary_centroid.ready())
        supervisor.timer.reset()
        for index in range(1, 191):
            tick(ORIGIN_NS+index*100_000_000)
            assert supervisor.machine.state == State.SEARCH
        until(lambda: gaussian.latest_algorithm_state is not None
            and gaussian.latest_algorithm_state.state == AlgorithmState.STATE_SEARCH)
        candidate = confirmation()
        candidate.metric_mode = metric_mode
        candidate.run_id, candidate.source_pose_topic = supervisor.run_id, PREFIX+'/pose'
        candidate.center_x_m = candidate.center_y_m = 0.
        candidate.centroid_x_m = candidate.centroid_y_m = [0.]*6
        original_candidate = deepcopy(candidate)
        pub['confirmation'].publish(candidate)  # One supplied detector candidate.
        until(lambda: supervisor.stationary_centroid.accepted is not None)
        tick(ORIGIN_NS+19_100_000_000)
        until(lambda: supervisor.machine.state == State.VERIFY_EXTREMUM)
        assert not requests and not fills and gaussian.fill_registry.generation == 0
        assert supervisor.current_supervisor_command.linear.x == 0.
        assert supervisor.current_supervisor_command.angular.z == 0.

        # Source and clock delivery continue independently through verification
        # and synchronous fitting. Authority updates use their real DDS group.
        def produce():
            try:
                for index in range(1, 81):
                    if stop_producer.wait(.02):
                        return
                    sample(ORIGIN_NS+19_100_000_000+index*50_000_000)
            except BaseException as error:
                producer_errors.append(repr(error))
        producer = threading.Thread(target=produce, daemon=True)
        producer.start()
        until(lambda: len(requests) == 1 and any(f.active for f in fills), 10.)
        until(lambda: supervisor.machine.state == State.ESCAPE_REPULSE
            and len(supervisor.active_fill_records) == 1, 5.)
        request = requests[0]
        assert request.confirmation == original_candidate
        assert request.candidate_evidence_valid and request.candidate_rotation_count == 2
        assert stationary_request_errors(request, expected_run_id=supervisor.run_id,
            expected_frame_id='odom', expected_pose_topic=PREFIX+'/pose', origin_ns=ORIGIN_NS,
            expected_metric_mode=metric_mode) == []
        assert time_to_ns(request.confirmation_received_at) == ORIGIN_NS+19*NS
        assert request.source_timestamp == (time_to_ns(request.stamp)-ORIGIN_NS)*1e-9
        active = next(f for f in fills if f.active)
        assert active.source_timestamp == request.source_timestamp
        assert active.sample_count > 30 and active.amplitude > 0.
        assert gaussian.fill_registry.generation == 1 and not legacy_requests
        assert len(gaussian.stationary_fill.requests) == 1
        entry = next(iter(gaussian.stationary_fill.requests.values()))
        assert entry.status == 'complete'
        assert abs(time_to_ns(request.stamp)-entry.receipt_ns) <= 500_000_000
        assert entry.receipt_ns < time_to_ns(request.expires_at)
        assert time_to_ns(active.stamp) >= time_to_ns(request.stamp)
        assert any(s.state == AlgorithmState.STATE_VERIFY_EXTREMUM for s in states)
        assert any(s.state == AlgorithmState.STATE_DESIGN_OR_MERGE_FILL for s in states)
        # Real supervisor stop input must terminate its escape command authority.
        stop_producer.set(); producer.join(timeout=1.)
        assert not producer.is_alive()
        command_count = len(commands)
        pub['stop'].publish(Bool(data=True))
        tick(supervisor.get_clock().now().nanoseconds+100_000_000)
        until(lambda: supervisor.machine.state == State.FAILSAFE
            and len(commands) > command_count
            and commands[-1].linear.x == commands[-1].angular.z == 0.)
        print('Q5_STATIONARY_ACK '+json.dumps(dict(
            metric_mode=metric_mode, origin_ns=ORIGIN_NS,
            confirmation_source_ns=time_to_ns(candidate.source_stamp),
            request_source_ns=time_to_ns(request.stamp), first_request_receipt_ns=entry.receipt_ns,
            request_correlation_sec=request.source_timestamp, result_correlation_sec=active.source_timestamp,
            requests=len(requests), actual_fit_samples=active.sample_count,
            registry_generation=gaussian.fill_registry.generation,
            supervisor_acknowledged=True, final_zero=True,
            scope='actual DDS Supervisor verification -> typed request -> Gaussian fit -> result acknowledgment; supplied synthetic inputs',
        ), sort_keys=True))
    finally:
        stop_producer.set()
        if producer is not None:
            producer.join(timeout=1.)
        for node in nodes:
            executor.remove_node(node)
        executor.shutdown(timeout_sec=2.)
        for node in reversed(nodes):
            node.destroy_node()
        rclpy.try_shutdown()
