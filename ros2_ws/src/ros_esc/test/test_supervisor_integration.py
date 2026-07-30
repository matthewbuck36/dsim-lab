"""Synthetic ROS integration coverage for Phase 04 supervisor behavior."""

import math
import threading
import time

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import pytest
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from ros_esc.supervisor_node import supervisor_node_script
from ros_esc.supervisor_node.escape_recenter import Pose2D, recenter_command
from ros_esc.supervisor_node.state_machine import (
    State,
    TransitionInputs,
)
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
        time.sleep(0.005)
    return False


class Recorder:
    """Minimal publisher replacement retaining shutdown output."""

    def __init__(self):
        self.messages = []

    def publish(self, msg):
        self.messages.append(msg)


def _pose(x, y=0.0, yaw=0.0):
    msg = Odometry()
    msg.pose.pose.position.x = float(x)
    msg.pose.pose.position.y = float(y)
    msg.pose.pose.orientation.z = math.sin(float(yaw) / 2.0)
    msg.pose.pose.orientation.w = math.cos(float(yaw) / 2.0)
    return msg


def _source(score=0.2):
    msg = CostBreakdown()
    msg.source_timestamp = 7.0
    msg.source_timestamp_valid = True
    msg.channel_count = 1
    msg.raw_cost = [-1.0]
    msg.raw_cost_valid = True
    msg.source_score = [float(score)]
    msg.source_score_valid = True
    return msg


def _convergence():
    msg = StampedFloat64MultiArray()
    msg.header = "CONVERGENCE_STATUS"
    msg.timestamp = 42.0
    msg.data = [-0.1, 0.0, 0.0, 0.2, 0.0, 0.3, 0.0, 3.0]
    return msg


def _confirmed_convergence():
    msg = AlgorithmEvent()
    msg.event_type = AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED
    msg.source_timestamp = 42.0
    msg.source_timestamp_valid = True
    msg.value_names = [
        "metric",
        "r_mean_m2",
        "decay",
        "fill_center_x_m",
        "fill_center_y_m",
        "mean_old_x_m",
        "mean_old_y_m",
        "count_remaining",
    ]
    msg.values = [-0.1, 0.0, 0.0, 0.2, 0.0, 0.3, 0.0, 0.0]
    return msg


def _fill(source_timestamp, fill_id=1, revision=1, exit_radius=0.3):
    msg = GaussianFill()
    msg.source_timestamp = float(source_timestamp)
    msg.source_timestamp_valid = True
    msg.frame_id = "odom"
    msg.fill_id = int(fill_id)
    msg.cluster_id = 1
    msg.revision = int(revision)
    msg.active = True
    msg.covariance_valid = True
    msg.principal_widths_valid = True
    msg.support_radius_valid = True
    msg.exit_radius_valid = True
    msg.center_x = 0.0
    msg.center_y = 0.0
    msg.sigma_major = 0.10
    msg.sigma_minor = 0.10
    msg.support_radius = 0.05
    msg.exit_radius = float(exit_radius)
    return msg


class SupervisorHarness:
    """Run one supervisor with typed publisher/subscriber peers."""

    def __init__(self, overrides=None, name="phase04_supervisor_test_peer"):
        values = [
            Parameter("supervisor_publish_rate_hz", value=200.0),
            Parameter("startup_timeout_sec", value=0.5),
            Parameter("convergence_hold_sec", value=0.03),
            Parameter("goal_score_rotation_period_sec", value=0.01),
            Parameter("goal_score_required_rotations", value=1),
            Parameter("goal_hold_sec", value=0.03),
            Parameter("undesired_score_hold_sec", value=0.03),
            Parameter("verification_max_sec", value=0.5),
            Parameter("fill_design_timeout_sec", value=0.5),
            Parameter("escape_max_sec", value=2.0),
            Parameter("escape_exit_hold_sec", value=0.03),
            Parameter("stall_window_sec", value=0.20),
            Parameter("minimum_radial_progress_m", value=0.02),
            Parameter("approach_history_window_sec", value=0.05),
            Parameter("direction_lookahead_m", value=0.20),
            Parameter("fill_avoidance_margin_m", value=0.01),
            Parameter("recenter_hold_sec", value=0.03),
            Parameter("stale_pose_sec", value=2.0),
            Parameter("stale_sensor_sec", value=2.0),
        ]
        values.extend(overrides or [])
        self.supervisor = SupervisorNode(parameter_overrides=values)
        self.peer = Node(name)
        self.executor = MultiThreadedExecutor(num_threads=2)
        self.executor.add_node(self.supervisor)
        self.executor.add_node(self.peer)
        self.states = []
        self.requests = []
        self.commands = []
        self.events = []
        self.peer.create_subscription(
            AlgorithmState,
            "/gesc_gaussian/algorithm_state",
            self.states.append,
            10,
        )
        self.peer.create_subscription(
            StampedFloat64MultiArray,
            "/gesc_gaussian/fill_requests",
            self.requests.append,
            10,
        )
        self.peer.create_subscription(
            Twist,
            "/gesc_gaussian/supervisor_command",
            self.commands.append,
            10,
        )
        self.peer.create_subscription(
            AlgorithmEvent,
            "/gesc_gaussian/algorithm_events",
            self.events.append,
            10,
        )
        self.pose_pub = self.peer.create_publisher(Odometry, "/odom", 10)
        self.source_pub = self.peer.create_publisher(
            CostBreakdown, "/gesc_gaussian/source_cost", 10
        )
        self.convergence_pub = self.peer.create_publisher(
            StampedFloat64MultiArray,
            "/gesc_gaussian/convergence_status",
            10,
        )
        self.event_pub = self.peer.create_publisher(
            AlgorithmEvent,
            "/gesc_gaussian/algorithm_events",
            10,
        )
        self.fill_pub = self.peer.create_publisher(
            GaussianFill, "/gesc_gaussian/gaussian_fills", 10
        )
        self.stop_pub = self.peer.create_publisher(
            Bool, "/gesc_gaussian/stop_requested", 10
        )
        self.thread = threading.Thread(target=self.executor.spin, daemon=True)
        self.thread.start()
        matched = _wait_for(
            lambda: (
                self.pose_pub.get_subscription_count() >= 1
                and self.source_pub.get_subscription_count() >= 1
                and self.convergence_pub.get_subscription_count() >= 1
                and self.event_pub.get_subscription_count() >= 1
                and self.fill_pub.get_subscription_count() >= 1
                and self.stop_pub.get_subscription_count() >= 1
                and self.supervisor.state_publisher.get_subscription_count()
                >= 1
                and self.supervisor.fill_request_publisher.get_subscription_count()
                >= 1
                and self.supervisor.command_publisher.get_subscription_count()
                >= 1
            )
        )
        if not matched:
            raise RuntimeError("synthetic supervisor ROS graph did not match")

    def publish_inputs(
        self, pose, convergence=None, duration=0.08, score=0.2
    ):
        deadline = time.monotonic() + duration
        source = _source(score)
        while time.monotonic() < deadline:
            self.pose_pub.publish(pose)
            self.source_pub.publish(source)
            if convergence is not None:
                self.convergence_pub.publish(convergence)
                self.event_pub.publish(_confirmed_convergence())
            time.sleep(0.005)

    def close(self):
        self.executor.shutdown()
        self.thread.join(timeout=1.0)
        self.executor.remove_node(self.peer)
        self.executor.remove_node(self.supervisor)
        self.peer.destroy_node()
        self.supervisor.destroy_node()


def test_pure_repulsion_exits_without_redesign_and_recenter_completes():
    rclpy.init()
    harness = SupervisorHarness(name="phase04_pure_escape_peer")
    try:
        convergence = _convergence()
        harness.publish_inputs(_pose(0.2), convergence, duration=0.25)
        assert _wait_for(lambda: len(harness.requests) == 1)
        assert harness.requests[0].header == "ROBUST_FILL_CREATE"
        harness.fill_pub.publish(_fill(harness.requests[0].timestamp))
        assert _wait_for(
            lambda: any(
                state.state == AlgorithmState.STATE_ESCAPE_REPULSE
                for state in harness.states
            )
        )

        harness.publish_inputs(_pose(0.5), duration=0.28)
        assert _wait_for(
            lambda: any(
                state.state == AlgorithmState.STATE_RECENTER
                for state in harness.states
            )
        )
        assert any(
            state.state == AlgorithmState.STATE_ESCAPE_REPULSE
            and state.radial_distance_valid
            and state.radial_progress_valid
            and state.escape_geometry_valid
            for state in harness.states
        )
        assert len(harness.requests) == 1
        assert not any(
            event.event_type == AlgorithmEvent.EVENT_ESCAPE_STALLED
            for event in harness.events
        )
        assert _wait_for(
            lambda: any(
                abs(command.linear.x) > 0.0 or abs(command.angular.z) > 0.0
                for command in harness.commands
            )
        )
        assert harness.supervisor.active_fill_records
        configuration = next(
            event
            for event in harness.events
            if event.event_type == AlgorithmEvent.EVENT_CONFIGURATION
        )
        diagnostics = dict(
            zip(configuration.value_names, configuration.values)
        )
        assert 'room_bounds_x_min_m' in diagnostics
        assert diagnostics['supervisor_command_stale_sec'] == 0.5
        assert diagnostics['goal_score_evidence_duration_sec'] == 0.01
        assert math.isclose(
            diagnostics['goal_score_verification_margin_sec'],
            0.46,
            rel_tol=0.0,
            abs_tol=1e-12,
        )
        assert (
            diagnostics['goal_score_verification_timing_sufficient'] == 1.0
        )

        harness.publish_inputs(_pose(0.1), duration=0.08)
        assert _wait_for(
            lambda: any(
                event.event_type == AlgorithmEvent.EVENT_RECENTER_COMPLETE
                for event in harness.events
            )
        )
        assert any(
            state.state == AlgorithmState.STATE_SEARCH
            for state in harness.states
        )
    finally:
        harness.close()
        rclpy.shutdown()


def test_recenter_suppresses_inward_translation_while_continuing_rotation():
    rclpy.init()
    node = SupervisorNode(
        parameter_overrides=[
            Parameter('supervisor_command_stale_sec', value=0.5),
        ]
    )
    try:
        node.machine.state = State.RECENTER
        node.latest_pose = Pose2D(
            0.0,
            -0.922899286,
            0.299448541,
            0.244951597,
        )
        node.latest_pose_valid = True
        node.active_fill_records = {
            1: {
                'fill_id': 1,
                'center': [-0.625781953, -0.056395888],
                'support_radius': 0.508674749,
            }
        }

        assert node._update_recenter(node._now_sec()) is None
        raw_linear, _ = recenter_command(
            node.safe_direction.direction,
            node.latest_pose.yaw,
            node.recenter_distance,
            node.recenter_config,
        )
        assert raw_linear > 0.0
        assert node.current_supervisor_command.linear.x == 0.0
        assert abs(node.current_supervisor_command.angular.z) > 0.0
        assert node.safe_direction_revision == 1

        safe_yaw = math.atan2(
            node.safe_direction.y,
            node.safe_direction.x,
        )
        node.latest_pose = Pose2D(
            0.1,
            node.latest_pose.x,
            node.latest_pose.y,
            safe_yaw,
        )
        assert node._update_recenter(node._now_sec()) is None
        assert node.current_supervisor_command.linear.x > 0.0
        assert node.safe_direction_revision == 2
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_post_recovery_search_publishes_safe_affine_authorization():
    rclpy.init()
    node = SupervisorNode(
        parameter_overrides=[
            Parameter("max_fill_clusters", value=1),
            Parameter("post_recovery_guidance_enabled", value=True),
            Parameter("post_recovery_guidance_max_sec", value=60.0),
            Parameter("post_recovery_retry_limit", value=3),
            Parameter("room_bounds_x_min_m", value=-0.25),
            Parameter("room_bounds_x_max_m", value=3.75),
            Parameter("room_bounds_y_min_m", value=-0.25),
            Parameter("room_bounds_y_max_m", value=3.75),
            Parameter("room_center_x_m", value=1.75),
            Parameter("room_center_y_m", value=1.75),
            Parameter("wall_margin_m", value=0.20),
        ]
    )
    recorder = Recorder()
    node.state_publisher = recorder
    try:
        node.latest_pose = Pose2D(10.0, 1.75, 1.75, 0.0)
        node.latest_pose_valid = True
        node.active_fill_records = {
            1: {
                "fill_id": 4,
                "revision": 1,
                "center": [1.22, 1.44],
                "support_radius": 0.51,
                "exit_radius": 0.42,
            }
        }
        node.machine.state = State.SEARCH
        node.machine.active_fill_count = 1
        node.machine.post_recovery_fill_id = 4
        node.machine.active_escape_fill_id = 4
        node.machine.post_recovery_guidance_active = True
        node.machine.post_recovery_guidance_started_sec = node._now_sec()

        assert node._ensure_post_recovery_direction() is None
        outward = node.latest_pose.position - [1.22, 1.44]
        assert (
            float(node.safe_direction.direction @ outward) > 0.0
        )

        node._publish_state_and_command(node._now_sec())
        state = recorder.messages[-1]
        assert state.state == AlgorithmState.STATE_SEARCH
        assert state.active_escape_fill_id == 4
        assert state.active_escape_fill_id_valid is True
        assert state.safe_direction_valid is True
        assert state.safe_direction_revision_valid is True
        assert state.sensor_weight == 1.0
        assert state.gaussian_weight == 1.0
        assert state.affine_weight == 1.0
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_post_recovery_affine_weight_tapers_after_fill_support():
    rclpy.init()
    node = SupervisorNode(
        parameter_overrides=[
            Parameter('max_fill_clusters', value=1),
            Parameter('post_recovery_guidance_enabled', value=True),
            Parameter('post_recovery_guidance_max_sec', value=60.0),
            Parameter('post_recovery_retry_limit', value=3),
            Parameter('recoverable_navigation_enabled', value=True),
            Parameter('recovery_retry_limit', value=3),
            Parameter('post_recovery_affine_weight', value=0.50),
            Parameter(
                'post_recovery_affine_taper_distance_m',
                value=0.50,
            ),
        ]
    )
    recorder = Recorder()
    node.state_publisher = recorder
    try:
        node.active_fill_records = {
            1: {
                'fill_id': 4,
                'revision': 1,
                'center': [0.0, 0.0],
                'support_radius': 0.50,
                'exit_radius': 0.40,
            }
        }
        node.machine.state = State.SEARCH
        node.machine.active_fill_count = 1
        node.machine.post_recovery_fill_id = 4
        node.machine.active_escape_fill_id = 4
        node.machine.post_recovery_guidance_active = True
        node.machine.post_recovery_guidance_started_sec = node._now_sec()

        node.latest_pose = Pose2D(10.0, 0.50, 0.0, 0.0)
        node.latest_pose_valid = True
        assert node._ensure_post_recovery_direction() is None
        node._publish_state_and_command(node._now_sec())
        assert recorder.messages[-1].affine_weight == 0.50

        node.latest_pose = Pose2D(10.1, 0.75, 0.0, 0.0)
        node._publish_state_and_command(node._now_sec())
        assert recorder.messages[-1].affine_weight == 0.25

        node.latest_pose = Pose2D(10.2, 1.00, 0.0, 0.0)
        node._publish_state_and_command(node._now_sec())
        assert recorder.messages[-1].affine_weight == 0.0
        assert node.machine.post_recovery_guidance_active is True
        assert node.active_fill_records
    finally:
        node.destroy_node()
        rclpy.shutdown()


def _m4_2_progress_node(**overrides):
    values = {
        'max_fill_clusters': 1,
        'post_recovery_guidance_enabled': True,
        'post_recovery_guidance_max_sec': 90.0,
        'post_recovery_retry_limit': 3,
        'recoverable_navigation_enabled': True,
        'recovery_retry_limit': 3,
        'post_recovery_affine_weight': 0.50,
        'post_recovery_affine_taper_distance_m': 0.50,
        'post_recovery_progress_enabled': True,
        'post_recovery_guidance_min_progress_m': 0.60,
        'post_recovery_liveness_window_sec': 4.0,
        'post_recovery_liveness_min_path_length_m': 0.60,
        'post_recovery_liveness_max_displacement_m': 0.20,
        'post_recovery_direction_refresh_limit': 1,
        'room_bounds_x_min_m': -0.25,
        'room_bounds_x_max_m': 3.75,
        'room_bounds_y_min_m': -0.25,
        'room_bounds_y_max_m': 3.75,
        'room_center_x_m': 1.75,
        'room_center_y_m': 1.75,
        'wall_margin_m': 0.20,
        'recenter_tolerance_m': 0.15,
    }
    values.update(overrides)
    return SupervisorNode(
        parameter_overrides=[
            Parameter(name, value=value)
            for name, value in values.items()
        ]
    )


def _activate_m4_2_guidance(node, pose_value=None):
    pose_value = pose_value or Pose2D(10.0, 1.75, 1.75, 0.0)
    node.latest_pose = pose_value
    node.latest_pose_valid = True
    node.latest_pose_sequence += 1
    node.active_fill_records = {
        1: {
            'fill_id': 4,
            'revision': 1,
            'center': [1.0, 1.0],
            'support_radius': 0.30,
            'exit_radius': 0.25,
        }
    }
    node.machine.state = State.SEARCH
    node.machine.active_fill_count = 1
    node.machine.post_recovery_fill_id = 4
    node.machine.active_escape_fill_id = 4
    node.machine.post_recovery_guidance_active = True
    node.machine.post_recovery_guidance_started_sec = node._now_sec()
    assert node._start_post_recovery_epoch(node._now_sec()) is None


def test_m4_2_progress_epoch_commands_then_holds_and_tapers_affine():
    rclpy.init()
    node = _m4_2_progress_node()
    states = Recorder()
    commands = Recorder()
    node.state_publisher = states
    node.command_publisher = commands
    try:
        _activate_m4_2_guidance(node)
        first_revision = node.safe_direction_revision
        direction = node.safe_direction.direction
        node.latest_pose = Pose2D(
            10.1,
            node.latest_pose.x,
            node.latest_pose.y,
            math.atan2(direction[1], direction[0]),
        )
        node.latest_pose_sequence += 1
        assert node._update_post_recovery_guidance(node._now_sec()) is None
        node._publish_state_and_command(node._now_sec())

        assert first_revision > 0
        assert commands.messages[-1].linear.x > 0.0
        assert states.messages[-1].affine_weight == 0.50

        anchor = node.post_recovery_progress_tracker.anchor_pose.position
        node.latest_pose = Pose2D(
            11.0,
            *(anchor + 0.60 * direction),
            node.latest_pose.yaw,
        )
        node.latest_pose_sequence += 1
        assert node._update_post_recovery_guidance(node._now_sec()) is None
        node._publish_state_and_command(node._now_sec())
        assert commands.messages[-1].linear.x == 0.0
        assert states.messages[-1].affine_weight == pytest.approx(0.50)

        node.latest_pose = Pose2D(
            12.0,
            *(anchor + 0.85 * direction),
            node.latest_pose.yaw,
        )
        node.latest_pose_sequence += 1
        assert node._update_post_recovery_guidance(node._now_sec()) is None
        node._publish_state_and_command(node._now_sec())
        assert states.messages[-1].affine_weight == pytest.approx(0.25)

        node.latest_pose = Pose2D(
            13.0,
            *(anchor + 1.10 * direction),
            node.latest_pose.yaw,
        )
        node.latest_pose_sequence += 1
        assert node._update_post_recovery_guidance(node._now_sec()) is None
        assert node.machine.post_recovery_guidance_active is False
        assert node.machine.active_escape_fill_id is None
        assert node.active_fill_records
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_2_liveness_refreshes_recenters_then_falls_back_nonterminal():
    rclpy.init()
    node = _m4_2_progress_node()
    node.event_publisher = Recorder()
    try:
        _activate_m4_2_guidance(node)
        anchor = node.latest_pose.position.copy()

        def feed_loop(first_stamp):
            offsets = (
                (0.2, 0.0),
                (0.2, 0.2),
                (0.0, 0.2),
                (0.0, 0.0),
            )
            for index, offset in enumerate(offsets):
                node.latest_pose = Pose2D(
                    first_stamp + index,
                    anchor[0] + offset[0],
                    anchor[1] + offset[1],
                    0.0,
                )
                node.latest_pose_sequence += 1
                assert (
                    node._update_post_recovery_guidance(node._now_sec())
                    is None
                )

        initial_revision = node.safe_direction_revision
        feed_loop(11.0)
        assert node.post_recovery_direction_refresh_count == 1
        assert node.safe_direction_revision > initial_revision
        assert node.recenter_recovery_requested is False

        feed_loop(15.0)
        assert node.recenter_recovery_requested is True
        assert node.post_recovery_recenter_attempted is True
        transition = node.machine.step(
            node._now_sec(),
            TransitionInputs(recenter_recovery_requested=True),
        )
        assert transition.current == State.RECENTER
        node._handle_transition(transition, node._now_sec())

        transition = node.machine.step(
            node._now_sec(),
            TransitionInputs(recenter_complete=True),
        )
        assert transition.current == State.SEARCH
        node._handle_transition(transition, node._now_sec())
        assert node.post_recovery_recenter_attempted is True
        anchor[:] = node.latest_pose.position

        feed_loop(19.0)
        assert node.machine.state == State.SEARCH
        assert node.machine.post_recovery_guidance_active is False
        assert node.machine.state != State.FAILSAFE
        details = [
            event.detail for event in node.event_publisher.messages
        ]
        assert sum('direction refreshed' in detail for detail in details) == 1
        assert any('requested recoverable recenter' in detail for detail in details)
        assert any('ordinary search' in detail for detail in details)
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_2_guidance_sweep_suppresses_unsafe_translation(monkeypatch):
    rclpy.init()
    node = _m4_2_progress_node()
    checked = []

    def reject_sweep(
        position,
        yaw,
        linear,
        horizon,
        fills,
        bounds,
        **kwargs,
    ):
        checked.append({
            'position': tuple(position),
            'yaw': yaw,
            'linear': linear,
            'horizon': horizon,
            'fills': tuple(fills),
            'bounds': bounds,
            'kwargs': kwargs,
        })
        return False

    monkeypatch.setattr(
        supervisor_node_script,
        'command_sweep_is_safe',
        reject_sweep,
    )
    try:
        _activate_m4_2_guidance(node)
        direction = node.safe_direction.direction
        node.latest_pose = Pose2D(
            10.1,
            node.latest_pose.x,
            node.latest_pose.y,
            math.atan2(direction[1], direction[0]),
        )
        node.latest_pose_sequence += 1

        assert node._update_post_recovery_guidance(0.1) is None
        assert checked
        assert checked[-1]['linear'] > 0.0
        assert checked[-1]['fills']
        assert checked[-1]['bounds'] is node.bounds
        assert checked[-1]['kwargs']['allow_inward_from_margin'] is True
        assert node.current_supervisor_command.linear.x == 0.0
        assert node.machine.state == State.SEARCH
        assert node.machine.state != State.FAILSAFE
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_2_maximum_duration_releases_with_typed_report():
    rclpy.init()
    node = _m4_2_progress_node()
    node.event_publisher = Recorder()
    try:
        _activate_m4_2_guidance(node)
        started = node.machine.post_recovery_guidance_started_sec

        assert node._update_post_recovery_guidance(started + 90.0) is None
        assert node.machine.post_recovery_guidance_active is False
        assert node.machine.active_escape_fill_id is None
        assert node.current_supervisor_command.linear.x == 0.0
        report = next(
            event
            for event in node.event_publisher.messages
            if 'maximum duration elapsed' in event.detail
        )
        assert all(math.isfinite(value) for value in report.values)
        diagnostics = dict(zip(report.value_names, report.values))
        assert diagnostics['window_valid'] == 0.0
        assert diagnostics['window_sec'] == 4.0
        assert diagnostics['minimum_window_path_m'] == 0.60
        assert diagnostics['maximum_window_displacement_m'] == 0.20
        assert diagnostics['post_recovery_retry_count'] == 0.0
        assert diagnostics['recovery_retry_count'] == 0.0
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_2_direction_failure_after_recenter_does_not_recenter_twice():
    rclpy.init()
    node = _m4_2_progress_node()
    node.event_publisher = Recorder()
    try:
        _activate_m4_2_guidance(node)
        node.post_recovery_recenter_attempted = True

        assert node._recover_post_recovery_direction_failure(
            20.0,
            'no safe post-recovery direction candidate',
        ) is None
        assert node.recenter_recovery_requested is False
        assert node.machine.post_recovery_guidance_active is False
        assert node.machine.active_escape_fill_id is None
        assert node.machine.state == State.SEARCH
        assert node.machine.state != State.FAILSAFE
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_2_progress_configuration_requires_refresh_capacity():
    rclpy.init()
    try:
        with pytest.raises(ValueError, match='positive direction refresh'):
            _m4_2_progress_node(
                post_recovery_direction_refresh_limit=0,
            )
    finally:
        rclpy.shutdown()


def test_m4_empty_post_recovery_direction_recenters_then_clears_affine(
    monkeypatch,
):
    rclpy.init()
    node = SupervisorNode(
        parameter_overrides=[
            Parameter('max_fill_clusters', value=1),
            Parameter('post_recovery_guidance_enabled', value=True),
            Parameter('post_recovery_guidance_max_sec', value=60.0),
            Parameter('post_recovery_retry_limit', value=3),
            Parameter('recoverable_navigation_enabled', value=True),
            Parameter('recovery_retry_limit', value=3),
            Parameter('room_bounds_x_min_m', value=-0.25),
            Parameter('room_bounds_x_max_m', value=3.75),
            Parameter('room_bounds_y_min_m', value=-0.25),
            Parameter('room_bounds_y_max_m', value=3.75),
            Parameter('room_center_x_m', value=1.75),
            Parameter('room_center_y_m', value=1.75),
            Parameter('wall_margin_m', value=0.20),
        ]
    )
    try:
        node.latest_pose = Pose2D(10.0, 3.50, 3.50, 0.0)
        node.latest_pose_valid = True
        node.active_fill_records = {
            1: {
                'fill_id': 4,
                'revision': 1,
                'center': [1.75, 1.75],
                'support_radius': 0.50,
                'exit_radius': 0.40,
            }
        }
        node.machine.state = State.SEARCH
        node.machine.active_fill_count = 1
        node.machine.post_recovery_fill_id = 4
        node.machine.active_escape_fill_id = 4
        node.machine.post_recovery_guidance_active = True
        node.machine.post_recovery_guidance_started_sec = node._now_sec()
        monkeypatch.setattr(
            supervisor_node_script,
            'select_post_recovery_direction',
            lambda *args, **kwargs: None,
        )

        assert node._prepare_geometry(node._now_sec()) is None
        assert node.recenter_recovery_requested is True
        transition = node.machine.step(
            node._now_sec(),
            TransitionInputs(recenter_recovery_requested=True),
        )
        assert transition.current == State.RECENTER
        node._handle_transition(transition, node._now_sec())

        transition = node.machine.step(
            node._now_sec(),
            TransitionInputs(recenter_complete=True),
        )
        assert transition.current == State.SEARCH
        node._handle_transition(transition, node._now_sec())
        assert node.post_recovery_direction_recovery_attempted is True

        assert node._prepare_geometry(node._now_sec()) is None
        assert node.machine.state == State.SEARCH
        assert node.machine.post_recovery_guidance_active is False
        assert node.machine.active_escape_fill_id is None
        assert node.active_fill_records
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m2_low_score_replay_does_not_publish_a_second_fill_request():
    rclpy.init()
    harness = SupervisorHarness(
        overrides=[
            Parameter("max_fill_clusters", value=1),
            Parameter("post_recovery_guidance_enabled", value=True),
            Parameter("post_recovery_guidance_max_sec", value=1.0),
            Parameter("post_recovery_retry_limit", value=3),
        ],
        name="phase08_m2_topology_replay_peer",
    )
    try:
        convergence = _convergence()
        harness.publish_inputs(_pose(0.2), convergence, duration=0.25)
        assert _wait_for(lambda: len(harness.requests) == 1)
        harness.fill_pub.publish(_fill(harness.requests[0].timestamp))
        assert _wait_for(
            lambda: any(
                state.state == AlgorithmState.STATE_ESCAPE_REPULSE
                for state in harness.states
            )
        )

        harness.publish_inputs(_pose(0.5), duration=0.28)
        assert _wait_for(
            lambda: any(
                state.state == AlgorithmState.STATE_RECENTER
                for state in harness.states
            )
        )
        harness.publish_inputs(_pose(0.1), duration=0.08)
        assert _wait_for(
            lambda: any(
                state.state == AlgorithmState.STATE_SEARCH
                and state.affine_weight == 1.0
                and state.safe_direction_valid
                for state in harness.states
            )
        )

        harness.convergence_pub.publish(convergence)
        harness.event_pub.publish(_confirmed_convergence())
        assert _wait_for(
            lambda: harness.supervisor.machine.state
            == State.VERIFY_EXTREMUM
        )
        harness.publish_inputs(_pose(0.1), duration=0.20, score=0.018)
        assert _wait_for(
            lambda: harness.supervisor.machine.state == State.SEARCH
            and harness.supervisor.machine.post_recovery_retry_count == 1
        )

        assert len(harness.requests) == 1
        assert harness.supervisor.machine.active_fill_count == 1
        assert harness.supervisor.machine.transition_reason == (
            "known local-fill budget exhausted; resume guided search"
        )
        assert any(
            state.state == AlgorithmState.STATE_SEARCH
            and state.affine_weight == 1.0
            for state in harness.states
        )
        assert not any(
            event.event_type == AlgorithmEvent.EVENT_FILL_REJECTED
            for event in harness.events
        )
    finally:
        harness.close()
        rclpy.shutdown()


def test_convergence_candidate_alone_does_not_activate_supervisor():
    rclpy.init()
    harness = SupervisorHarness(name="phase08_candidate_only_peer")
    try:
        convergence = _convergence()
        deadline = time.monotonic() + 0.12
        source = _source()
        while time.monotonic() < deadline:
            harness.pose_pub.publish(_pose(0.2))
            harness.source_pub.publish(source)
            harness.convergence_pub.publish(convergence)
            time.sleep(0.005)

        assert harness.requests == []
        assert all(
            state.state == AlgorithmState.STATE_SEARCH
            for state in harness.states
        )
    finally:
        harness.close()
        rclpy.shutdown()


def test_search_score_cannot_satisfy_fresh_verification_rotations():
    rclpy.init()
    harness = SupervisorHarness(
        overrides=[Parameter('verification_max_sec', value=1.0)],
        name='phase08_fresh_rotation_peer',
    )
    try:
        harness.publish_inputs(_pose(0.2), duration=0.08, score=1.0)
        assert harness.supervisor.machine.state == AlgorithmState.STATE_SEARCH
        assert harness.supervisor.goal_score_window.ready is False

        harness.event_pub.publish(_confirmed_convergence())
        assert _wait_for(
            lambda: harness.supervisor.machine.state
            == AlgorithmState.STATE_VERIFY_EXTREMUM
        )
        time.sleep(0.08)
        assert harness.supervisor.machine.state == (
            AlgorithmState.STATE_VERIFY_EXTREMUM
        )
        assert not any(
            state.state == AlgorithmState.STATE_GOAL_HOLD
            for state in harness.states
        )

        harness.publish_inputs(_pose(0.2), duration=0.20, score=1.0)
        assert _wait_for(
            lambda: harness.supervisor.machine.state
            == AlgorithmState.STATE_GOAL_HOLD
        )
    finally:
        harness.close()
        rclpy.shutdown()


def test_stall_requests_one_targeted_redesign_then_activates_assist():
    rclpy.init()
    harness = SupervisorHarness(
        overrides=[Parameter("stall_window_sec", value=0.05)],
        name="phase04_stalled_escape_peer",
    )
    try:
        convergence = _convergence()
        harness.publish_inputs(_pose(0.2), convergence, duration=0.25)
        assert _wait_for(lambda: len(harness.requests) == 1)
        harness.fill_pub.publish(
            _fill(harness.requests[0].timestamp, exit_radius=0.5)
        )
        assert _wait_for(
            lambda: any(
                state.state == AlgorithmState.STATE_ESCAPE_REPULSE
                for state in harness.states
            )
        )
        harness.publish_inputs(_pose(0.2), duration=0.10)
        assert _wait_for(lambda: len(harness.requests) == 2)
        assert harness.requests[1].header == "ROBUST_FILL_REDESIGN:1"
        assert sum(
            event.event_type == AlgorithmEvent.EVENT_ESCAPE_STALLED
            for event in harness.events
        ) == 1

        replacement = _fill(
            harness.requests[1].timestamp,
            fill_id=2,
            revision=2,
            exit_radius=0.7,
        )
        harness.fill_pub.publish(replacement)
        assert _wait_for(
            lambda: any(
                state.state == AlgorithmState.STATE_ESCAPE_ASSIST
                and state.safe_direction_valid
                for state in harness.states
            )
        )
        assisted = next(
            state
            for state in reversed(harness.states)
            if state.state == AlgorithmState.STATE_ESCAPE_ASSIST
            and state.safe_direction_valid
        )
        assert assisted.active_escape_fill_id == 2
        assert assisted.escape_center_x == 0.0
        assert assisted.escape_exit_radius == 0.5
        assert assisted.safe_direction_revision == 1
        assert len(harness.requests) == 2
        harness.publish_inputs(_pose(0.2), duration=0.03)
        revisions = {
            state.safe_direction_revision
            for state in harness.states
            if state.state == AlgorithmState.STATE_ESCAPE_ASSIST
            and state.safe_direction_valid
        }
        assert revisions == {1}

        stop = Bool()
        stop.data = True
        harness.stop_pub.publish(stop)
        assert _wait_for(
            lambda: harness.states
            and harness.states[-1].state == AlgorithmState.STATE_FAILSAFE
        )
        assert harness.commands
        assert harness.commands[-1].linear.x == 0.0
        assert harness.commands[-1].angular.z == 0.0
    finally:
        harness.close()
        rclpy.shutdown()


def test_bounds_violation_fails_safe_and_publishes_only_zero():
    rclpy.init()
    harness = SupervisorHarness(name="phase04_wall_failsafe_peer")
    try:
        harness.publish_inputs(_pose(1.8), duration=0.08)
        assert _wait_for(
            lambda: harness.states
            and harness.states[-1].state == AlgorithmState.STATE_FAILSAFE
        )
        assert any(
            event.event_type == AlgorithmEvent.EVENT_FAILSAFE
            and "operating bounds" in event.detail
            for event in harness.events
        )
        assert harness.commands
        assert all(
            command.linear.x == 0.0 and command.angular.z == 0.0
            for command in harness.commands
        )
    finally:
        harness.close()
        rclpy.shutdown()


def test_m4_wall_margin_pressure_recenters_but_physical_violation_fails():
    rclpy.init()
    harness = SupervisorHarness(
        overrides=[
            Parameter('recoverable_navigation_enabled', value=True),
            Parameter('recovery_retry_limit', value=3),
            Parameter(
                'boundary_recovery_trigger_clearance_m',
                value=0.025,
            ),
            Parameter(
                'boundary_recovery_release_clearance_m',
                value=0.10,
            ),
        ],
        name='phase08_m4_boundary_recovery_peer',
    )
    try:
        harness.publish_inputs(_pose(1.64), duration=0.08)
        assert _wait_for(
            lambda: harness.supervisor.machine.state == State.RECENTER
        )
        assert not any(
            event.event_type == AlgorithmEvent.EVENT_FAILSAFE
            for event in harness.events
        )

        harness.publish_inputs(_pose(2.01), duration=0.08)
        assert _wait_for(
            lambda: harness.supervisor.machine.state == State.FAILSAFE
        )
        assert any(
            event.event_type == AlgorithmEvent.EVENT_FAILSAFE
            and 'physical room bounds' in event.detail
            for event in harness.events
        )
        assert harness.commands
        assert harness.commands[-1].linear.x == 0.0
        assert harness.commands[-1].angular.z == 0.0
    finally:
        harness.close()
        rclpy.shutdown()


def test_supervisor_shutdown_always_publishes_zero():
    rclpy.init()
    supervisor = SupervisorNode()
    recorder = Recorder()
    supervisor.command_publisher = recorder
    supervisor.destroy_node()
    try:
        assert len(recorder.messages) == 1
        assert recorder.messages[0].linear.x == 0.0
        assert recorder.messages[0].angular.z == 0.0
    finally:
        rclpy.shutdown()
