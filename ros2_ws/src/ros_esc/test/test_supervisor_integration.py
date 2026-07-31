"""Synthetic ROS integration coverage for Phase 04 supervisor behavior."""

import math
import threading
import time

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import numpy as np
import pytest
import rclpy
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from ros_esc.supervisor_node import supervisor_node_script
from ros_esc.supervisor_node.escape_recenter import (
    DirectionConfig,
    EscapeGeometry,
    EscapeProgressTracker,
    FillAvoidance,
    OperatingBounds,
    Pose2D,
    SourceContinuityEvidence,
    recenter_command,
    select_safe_direction,
    source_continuity_evidence,
)
from ros_esc.supervisor_node.state_machine import (
    CANDIDATE_INFORMED_FILL_HEADER,
    CandidateCostSummary,
    State,
    Transition,
    TransitionInputs,
    decode_candidate_informed_fill_payload,
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


def _source(score=0.2, raw_cost=-1.0):
    msg = CostBreakdown()
    msg.source_timestamp = 7.0
    msg.source_timestamp_valid = True
    msg.channel_count = 1
    msg.raw_cost = [float(raw_cost)]
    msg.raw_cost_valid = True
    msg.source_score = [float(score)]
    msg.source_score_valid = True
    return msg


def _convergence(center_x=0.2, center_y=0.0):
    msg = StampedFloat64MultiArray()
    msg.header = "CONVERGENCE_STATUS"
    msg.timestamp = 42.0
    msg.data = [
        -0.1,
        0.0,
        0.0,
        float(center_x),
        float(center_y),
        0.3,
        0.0,
        3.0,
    ]
    return msg


def _confirmed_convergence(center_x=0.2, center_y=0.0):
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
    msg.values = [
        -0.1,
        0.0,
        0.0,
        float(center_x),
        float(center_y),
        0.3,
        0.0,
        0.0,
    ]
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
        self,
        pose,
        convergence=None,
        duration=0.08,
        score=0.2,
        raw_cost=-1.0,
        confirmation=None,
    ):
        deadline = time.monotonic() + duration
        source = _source(score, raw_cost)
        while time.monotonic() < deadline:
            self.pose_pub.publish(pose)
            self.source_pub.publish(source)
            if convergence is not None:
                self.convergence_pub.publish(convergence)
                self.event_pub.publish(
                    confirmation or _confirmed_convergence()
                )
            time.sleep(0.005)

    def close(self):
        self.executor.shutdown()
        self.thread.join(timeout=1.0)
        self.executor.remove_node(self.peer)
        self.executor.remove_node(self.supervisor)
        self.peer.destroy_node()
        self.supervisor.destroy_node()


def test_counted_candidate_adapter_fills_first_then_ranks_raw_cost():
    rclpy.init()
    harness = SupervisorHarness(
        overrides=[
            Parameter(
                "extremum_classification_mode",
                value="counted_candidates",
            ),
            Parameter("known_source_count", value=2),
            Parameter("max_fill_clusters", value=1),
            Parameter("candidate_cost_rotation_period_sec", value=0.01),
            Parameter("candidate_cost_required_rotations", value=1),
            Parameter("candidate_cost_mad_scale", value=3.0),
            Parameter("recenter_after_escape", value=False),
        ],
        name="phase088_counted_candidate_peer",
    )
    try:
        local_confirmation = _confirmed_convergence(0.0, 0.0)
        harness.publish_inputs(
            _pose(0.0),
            _convergence(0.0, 0.0),
            duration=0.20,
            score=1.0,
            raw_cost=-1.0,
            confirmation=local_confirmation,
        )
        assert _wait_for(lambda: len(harness.requests) == 1)
        assert not any(
            event.event_type == AlgorithmEvent.EVENT_GOAL_REACHED
            for event in harness.events
        )

        harness.fill_pub.publish(_fill(harness.requests[0].timestamp))
        assert _wait_for(
            lambda: harness.supervisor.machine.state == State.ESCAPE_REPULSE
        )
        harness.publish_inputs(
            _pose(0.6),
            duration=0.35,
            raw_cost=-1.0,
        )
        assert _wait_for(
            lambda: harness.supervisor.machine.state == State.SEARCH
        )

        global_confirmation = _confirmed_convergence(3.0, 0.0)
        harness.publish_inputs(
            _pose(3.0),
            _convergence(3.0, 0.0),
            duration=0.20,
            score=0.1,
            raw_cost=-2.0,
            confirmation=global_confirmation,
        )
        assert _wait_for(
            lambda: harness.supervisor.machine.state == State.GOAL_HOLD
        )
        assert _wait_for(
            lambda: any(
                event.event_type == AlgorithmEvent.EVENT_GOAL_REACHED
                for event in harness.events
            )
        )

        goal = next(
            event
            for event in harness.events
            if event.event_type == AlgorithmEvent.EVENT_GOAL_REACHED
        )
        evidence = dict(zip(goal.value_names, goal.values))
        assert "strictly lower" in goal.detail
        assert evidence["candidate_raw_cost_estimate"] == pytest.approx(-2.0)
        assert evidence["candidate_ordinal"] == 2.0
        assert evidence["filled_candidate_count"] == 1.0
        assert evidence["known_source_count"] == 2.0
        assert len(harness.supervisor.active_fill_records) == 1
        assert len(harness.requests) == 1
    finally:
        harness.close()
        rclpy.shutdown()


def test_counted_candidate_pretrigger_history_uses_raw_and_resets_epoch():
    rclpy.init()
    node = SupervisorNode(
        parameter_overrides=[
            Parameter(
                "extremum_classification_mode",
                value="counted_candidates",
            ),
            Parameter("known_source_count", value=2),
            Parameter("max_fill_clusters", value=1),
            Parameter("candidate_cost_rotation_period_sec", value=1.0),
            Parameter("candidate_cost_required_rotations", value=3),
            Parameter("candidate_cost_pretrigger_rotations", value=6),
            Parameter("candidate_cost_mad_scale", value=3.0),
            Parameter("recenter_after_escape", value=False),
        ]
    )
    now = [0.0]
    node._now_sec = lambda: now[0]
    try:
        for stamp, raw_cost in enumerate(
            (-3.8, -3.8, -3.8, -0.03, -0.02, -0.01, -0.01),
        ):
            now[0] = float(stamp)
            source = _source(raw_cost=raw_cost)
            source.augmented_cost = [-100.0]
            source.augmented_cost_valid = True
            node.source_callback(source)

        assert tuple(
            node.candidate_cost_search_window.completed_minima
        ) == pytest.approx(
            (-3.8, -3.8, -3.8, -0.03, -0.02, -0.01),
        )

        node.machine.state = State.VERIFY_EXTREMUM
        node._handle_transition(
            Transition(
                State.SEARCH,
                State.VERIFY_EXTREMUM,
                "detector convergence confirmation received",
            ),
            now[0],
        )
        assert node.candidate_cost_pretrigger_minima == pytest.approx(
            (-3.8, -3.8, -3.8, -0.03, -0.02, -0.01),
        )

        for offset, raw_cost in enumerate(
            (-0.02, -0.01, -0.03, -0.02),
            start=1,
        ):
            now[0] = 6.0 + float(offset)
            source = _source(raw_cost=raw_cost)
            source.augmented_cost = [-100.0]
            source.augmented_cost_valid = True
            node.source_callback(source)

        summary = node.latest_candidate_cost_summary
        assert summary.estimate == pytest.approx(-3.8)
        assert summary.mad == pytest.approx(0.0)
        assert summary.rotation_count == 3
        assert summary.pretrigger_rotation_count == 6
        assert summary.verification_rotation_count == 3
        assert summary.available_rotation_count == 9

        names, values = node._candidate_evidence(summary)
        evidence = dict(zip(names, values))
        assert evidence["candidate_pretrigger_rotation_count"] == 6.0
        assert evidence["candidate_verification_rotation_count"] == 3.0
        assert evidence["candidate_available_rotation_count"] == 9.0

        node.machine.state = State.SEARCH
        node._handle_transition(
            Transition(
                State.VERIFY_EXTREMUM,
                State.SEARCH,
                "counted candidate not strictly stronger; resume search",
            ),
            now[0],
        )
        assert node.candidate_cost_pretrigger_minima == ()
        assert not node.candidate_cost_search_window.completed_minima
        assert node.candidate_cost_window.ready is False
        assert node.latest_candidate_cost_summary is None
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_candidate_pretrigger_history_is_default_off():
    rclpy.init()
    node = SupervisorNode()
    try:
        assert node.machine.config.candidate_cost_pretrigger_rotations == 0
        assert node.candidate_cost_search_window is None
        assert node.candidate_cost_pretrigger_minima == ()
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_candidate_informed_fill_request_carries_only_frozen_raw_evidence():
    rclpy.init()
    node = SupervisorNode(
        parameter_overrides=[
            Parameter(
                "extremum_classification_mode",
                value="counted_candidates",
            ),
            Parameter("known_source_count", value=2),
            Parameter("max_fill_clusters", value=1),
            Parameter("candidate_cost_required_rotations", value=3),
            Parameter("candidate_cost_pretrigger_rotations", value=6),
            Parameter("candidate_informed_fill_enabled", value=True),
            Parameter("recenter_after_escape", value=False),
        ]
    )
    requests = Recorder()
    node.fill_request_publisher = requests
    try:
        node.machine.state = State.DESIGN_OR_MERGE_FILL
        node.machine.pending_candidate_cost = CandidateCostSummary(
            estimate=-1.572582366887451,
            mad=0.2898819545479434,
            uncertainty=0.8696458636438302,
            rotation_count=3,
            pretrigger_rotation_count=6,
            verification_rotation_count=3,
            available_rotation_count=9,
        )
        node.latest_convergence = _convergence(0.9, 1.1)
        transition = Transition(
            State.VERIFY_EXTREMUM,
            State.DESIGN_OR_MERGE_FILL,
            "counted candidate requires local fill before terminal ranking",
        )
        node._handle_transition(transition, node.machine.last_now_sec)

        assert len(requests.messages) == 1
        request = requests.messages[0]
        assert request.header == CANDIDATE_INFORMED_FILL_HEADER
        assert len(request.data) == 13
        assert request.data[:8] == pytest.approx(
            node.latest_convergence.data
        )
        evidence = decode_candidate_informed_fill_payload(
            request.header,
            request.data,
        )
        assert evidence.estimate == pytest.approx(-1.572582366887451)
        assert evidence.lower == pytest.approx(-2.4422282305312812)
        assert evidence.rotation_count == 3
        assert node.machine.fill_request_timestamp == pytest.approx(
            node.latest_convergence.timestamp
        )
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_open_field_disables_bounds_without_weakening_explicit_stop():
    rclpy.init()
    node = SupervisorNode(
        parameter_overrides=[
            Parameter("operating_bounds_enabled", value=False),
            Parameter("recenter_after_escape", value=False),
        ]
    )
    try:
        node.latest_pose = Pose2D(
            node._now_sec(),
            100.0,
            -100.0,
            0.0,
        )
        node.latest_pose_valid = True

        assert node.operating_bounds_enabled is False
        assert node.bounded_mode is False
        assert node.bounds is None
        assert node._prepare_geometry(node._now_sec()) is None

        transition = node.machine.step(
            node._now_sec(),
            TransitionInputs(explicit_stop=True),
        )
        assert transition.current == State.FAILSAFE
        assert transition.reason == "explicit stop requested"
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_open_field_escape_assist_requires_bounds_disabled():
    rclpy.init()
    try:
        with pytest.raises(
            ValueError,
            match="open-field escape assist requires operating bounds",
        ):
            SupervisorNode(
                parameter_overrides=[
                    Parameter(
                        "open_field_escape_assist_enabled",
                        value=True,
                    ),
                    Parameter("recenter_after_escape", value=False),
                ]
            )
    finally:
        rclpy.shutdown()


def test_open_field_escape_assist_commands_radially_outward_and_zeros_on_exit():
    rclpy.init()
    node = SupervisorNode(
        parameter_overrides=[
            Parameter("operating_bounds_enabled", value=False),
            Parameter("recenter_after_escape", value=False),
            Parameter("open_field_escape_assist_enabled", value=True),
            Parameter("direction_lookahead_m", value=0.50),
            Parameter("fill_avoidance_margin_m", value=0.10),
            Parameter("recenter_tolerance_m", value=0.25),
            Parameter("recenter_max_linear_velocity_mps", value=0.10),
            Parameter("supervisor_command_stale_sec", value=0.50),
        ]
    )
    node.command_publisher = Recorder()
    try:
        node.machine.state = State.ESCAPE_ASSIST
        node.machine.escape_started_sec = node.machine.last_now_sec
        node.machine.active_escape_fill_id = 1
        node.latest_pose = Pose2D(0.0, 0.25, 0.0, 0.0)
        node.latest_pose_valid = True
        node.latest_pose_sequence = 1
        node.active_fill_records = {
            1: {
                "fill_id": 1,
                "revision": 1,
                "center": [0.0, 0.0],
                "support_radius": 0.50,
                "exit_radius": 1.25,
            }
        }
        node.escape_tracker = EscapeProgressTracker(
            EscapeGeometry(
                initial_fill_id=1,
                center_x=0.0,
                center_y=0.0,
                exit_radius=1.25,
                started_sec=0.0,
                approach_x=1.0,
                approach_y=0.0,
            ),
            node.escape_progress_config,
        )
        node.escape_tracker.update(node.latest_pose)

        assert node._prepare_geometry(0.0) is None
        assert node.safe_direction.direction == pytest.approx([1.0, 0.0])
        assert node.current_supervisor_command.linear.x > 0.0
        assert node.current_supervisor_command.angular.z == pytest.approx(0.0)
        assert node.machine.weights == (0.0, 1.0, 0.0)

        node._publish_state_and_command(0.0)
        assert node.command_publisher.messages[-1].linear.x > 0.0

        transition_time = node.machine.last_now_sec + 0.1
        transition = node.machine.step(
            transition_time,
            TransitionInputs(stable_exit=True),
        )
        assert transition.current == State.SEARCH
        node._handle_transition(transition, transition_time)
        node._publish_state_and_command(transition_time)
        assert node.current_supervisor_command.linear.x == 0.0
        assert node.command_publisher.messages[-1].linear.x == 0.0
        assert node.escape_tracker is None
    finally:
        node.destroy_node()
        rclpy.shutdown()


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


def _m4_4_adaptive_recenter_node(**overrides):
    values = {
        'recoverable_navigation_enabled': True,
        'recovery_retry_limit': 3,
        'adaptive_recenter_lookahead_enabled': True,
        'room_bounds_x_min_m': -0.25,
        'room_bounds_x_max_m': 3.75,
        'room_bounds_y_min_m': -0.25,
        'room_bounds_y_max_m': 3.75,
        'room_center_x_m': 1.75,
        'room_center_y_m': 1.75,
        'wall_margin_m': 0.20,
        'direction_lookahead_m': 0.50,
        'fill_avoidance_margin_m': 0.10,
        'recenter_max_sec': 1.0,
        'recenter_max_linear_velocity_mps': 0.10,
        'supervisor_command_stale_sec': 0.50,
    }
    values.update(overrides)
    return SupervisorNode(
        parameter_overrides=[
            Parameter(name, value=value)
            for name, value in values.items()
        ]
    )


def _activate_m4_4_corner_recenter(node):
    node.machine.state = State.RECENTER
    node.machine.state_entered_sec = node.machine.last_now_sec
    node.latest_pose = Pose2D(253.116, 0.3963, 0.2401, 0.1619)
    node.latest_pose_valid = True
    node.recenter_target = node.bounds.center.copy()
    node.recenter_started_distance = float(
        math.dist(node.latest_pose.position, node.recenter_target)
    )
    node.recenter_best_distance = node.recenter_started_distance
    node.active_fill_records = {
        1: {
            'fill_id': 1,
            'revision': 1,
            'center': [0.5447780037, 0.8569669278],
            'support_radius': 0.5086747487,
            'exit_radius': 0.4238956239,
        }
    }


def test_m4_4_adaptive_recenter_resolves_retained_corner_geometry():
    rclpy.init()
    node = _m4_4_adaptive_recenter_node()
    try:
        _activate_m4_4_corner_recenter(node)

        assert node._update_recenter(253.116) is None
        assert node.machine.state == State.RECENTER
        assert node.safe_direction is not None
        assert node.recenter_route_planner.selected_lookahead_m == (
            pytest.approx(0.25)
        )
        assert node.recenter_recovery_allowed is True
        assert node.recenter_route_unavailable_reported is False
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_4_empty_adaptive_route_holds_then_exhausts_bounded_recovery(
    monkeypatch,
):
    rclpy.init()
    node = _m4_4_adaptive_recenter_node()
    events = Recorder()
    node.event_publisher = events
    try:
        _activate_m4_4_corner_recenter(node)
        monkeypatch.setattr(
            node.recenter_route_planner,
            'select',
            lambda *args, **kwargs: None,
        )

        assert node._update_recenter(0.1) is None
        assert node._update_recenter(0.2) is None
        assert node.machine.state == State.RECENTER
        assert node.current_supervisor_command.linear.x == 0.0
        assert node.recenter_recovery_allowed is True
        assert sum(
            'recenter route temporarily unavailable; bounded '
            'recovery continues' in event.detail
            for event in events.messages
        ) == 1

        for unused_attempt in range(3):
            transition = node.machine.step(
                node.machine.state_entered_sec + 1.0,
                TransitionInputs(recenter_recovery_allowed=True),
            )
            assert transition.current == State.RECENTER
        exhausted = node.machine.step(
            node.machine.state_entered_sec + 1.0,
            TransitionInputs(recenter_recovery_allowed=True),
        )
        assert exhausted.current == State.FAILSAFE
        assert exhausted.reason == 'recenter timeout'
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_4_adaptive_recenter_does_not_relax_physical_room_boundary():
    rclpy.init()
    node = _m4_4_adaptive_recenter_node()
    try:
        _activate_m4_4_corner_recenter(node)
        node.latest_pose = Pose2D(253.2, -0.251, 0.24, 0.0)

        assert node._prepare_geometry(253.2) == (
            'pose outside physical room bounds'
        )
        assert node.recenter_route_unavailable_reported is False
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_4_controls_require_recoverable_progress_owners():
    rclpy.init()
    try:
        with pytest.raises(
            ValueError,
            match='adaptive recenter look-ahead requires recoverable',
        ):
            SupervisorNode(
                parameter_overrides=[
                    Parameter(
                        'adaptive_recenter_lookahead_enabled',
                        value=True,
                    ),
                ]
            )
        with pytest.raises(
            ValueError,
            match='source-led handoff requires post-recovery progress',
        ):
            SupervisorNode(
                parameter_overrides=[
                    Parameter(
                        'recoverable_navigation_enabled',
                        value=True,
                    ),
                    Parameter('recovery_retry_limit', value=3),
                    Parameter(
                        'post_recovery_source_led_handoff_enabled',
                        value=True,
                    ),
                ]
            )
    finally:
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


def _activate_m4_2_guidance(
    node,
    pose_value=None,
    source_led_handoff=False,
):
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
    assert node._start_post_recovery_epoch(
        node._now_sec(),
        source_led_handoff=source_led_handoff,
    ) is None


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


def test_m4_4_source_led_window_has_no_affine_direction_or_supervisor_motion():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_liveness_window_sec=12.0,
        post_recovery_source_led_handoff_enabled=True,
    )
    states = Recorder()
    commands = Recorder()
    events = Recorder()
    node.state_publisher = states
    node.command_publisher = commands
    node.event_publisher = events
    try:
        _activate_m4_2_guidance(node, source_led_handoff=True)
        anchor = node.latest_pose.position.copy()

        assert node.post_recovery_source_led_active is True
        assert node.safe_direction is None
        node._publish_state_and_command(node._now_sec())
        assert states.messages[-1].sensor_weight == 1.0
        assert states.messages[-1].gaussian_weight == 1.0
        assert states.messages[-1].affine_weight == 0.0
        assert states.messages[-1].safe_direction_valid is False
        assert commands.messages[-1].linear.x == 0.0
        assert commands.messages[-1].angular.z == 0.0

        node.latest_pose = Pose2D(21.999, *(anchor + [0.19, 0.0]), 0.0)
        node.latest_pose_sequence += 1
        assert node._update_post_recovery_guidance(21.999) is None
        node._publish_state_and_command(21.999)

        assert node.post_recovery_source_led_active is True
        assert node.machine.post_recovery_guidance_active is True
        assert node.safe_direction is None
        assert states.messages[-1].affine_weight == 0.0
        assert commands.messages[-1].linear.x == 0.0
        assert sum(
            event.detail == 'post-recovery source-led handoff started'
            for event in events.messages
        ) == 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_4_recenter_search_boundary_starts_source_led_handoff():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_liveness_window_sec=12.0,
        post_recovery_source_led_handoff_enabled=True,
    )
    events = Recorder()
    node.event_publisher = events
    try:
        node.latest_pose = Pose2D(10.0, 1.75, 1.75, 0.0)
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
        node.machine.state = State.RECENTER
        node.machine.state_entered_sec = node.machine.last_now_sec
        node.machine.active_fill_count = 1
        node.machine.post_recovery_fill_id = 4
        node.machine.active_escape_fill_id = 4
        node.recenter_target = node.bounds.center.copy()
        node.recenter_distance = 0.0

        now_sec = node.machine.last_now_sec + 0.1
        transition = node.machine.step(
            now_sec,
            TransitionInputs(recenter_complete=True),
        )
        assert transition.previous == State.RECENTER
        assert transition.current == State.SEARCH
        node._handle_transition(transition, now_sec)

        assert node.post_recovery_source_led_active is True
        assert node.machine.post_recovery_guidance_active is True
        assert node.safe_direction is None
        assert node.current_supervisor_command.linear.x == 0.0
        assert sum(
            event.detail == 'post-recovery source-led handoff started'
            for event in events.messages
        ) == 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_4_source_led_handoff_does_not_restart_after_fallback_recenter():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_liveness_window_sec=12.0,
        post_recovery_source_led_handoff_enabled=True,
    )
    try:
        _activate_m4_2_guidance(node)
        node.post_recovery_recenter_attempted = True

        assert node._start_post_recovery_epoch(
            node._now_sec(),
            source_led_handoff=True,
        ) is None

        assert node.post_recovery_source_led_active is False
        assert node.safe_direction is not None
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_4_source_led_translation_releases_to_ordinary_search():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_liveness_window_sec=12.0,
        post_recovery_source_led_handoff_enabled=True,
    )
    states = Recorder()
    events = Recorder()
    node.state_publisher = states
    node.event_publisher = events
    try:
        _activate_m4_2_guidance(node, source_led_handoff=True)
        anchor = node.latest_pose.position.copy()
        node.latest_pose = Pose2D(22.0, *(anchor + [0.21, 0.0]), 0.0)
        node.latest_pose_sequence += 1

        assert node._update_post_recovery_guidance(22.0) is None
        node._publish_state_and_command(22.0)

        assert node.post_recovery_source_led_active is False
        assert node.machine.post_recovery_guidance_active is False
        assert node.machine.state == State.SEARCH
        assert node.safe_direction is None
        assert node.current_supervisor_command.linear.x == 0.0
        assert states.messages[-1].sensor_weight == 1.0
        assert states.messages[-1].gaussian_weight == 1.0
        assert states.messages[-1].affine_weight == 0.0
        assert sum(
            event.detail == 'post-recovery source-led handoff completed'
            for event in events.messages
        ) == 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_4_source_led_threshold_arms_exactly_one_existing_fallback():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_liveness_window_sec=12.0,
        post_recovery_source_led_handoff_enabled=True,
    )
    states = Recorder()
    events = Recorder()
    node.state_publisher = states
    node.event_publisher = events
    try:
        _activate_m4_2_guidance(node, source_led_handoff=True)
        anchor = node.latest_pose.position.copy()
        node.latest_pose = Pose2D(22.0, *(anchor + [0.20, 0.0]), 0.0)
        node.latest_pose_sequence += 1

        assert node._update_post_recovery_guidance(22.0) is None
        node._publish_state_and_command(22.0)

        assert node.post_recovery_source_led_active is False
        assert node.machine.post_recovery_guidance_active is True
        assert node.safe_direction is not None
        assert node.post_recovery_source_bypass_active is False
        assert node.post_recovery_progress_tracker.latest.window_valid is False
        assert states.messages[-1].affine_weight == pytest.approx(0.50)
        detail = (
            'post-recovery source-led handoff stalled; '
            'fallback guidance armed'
        )
        assert sum(
            event.detail == detail for event in events.messages
        ) == 1

        assert node._update_post_recovery_guidance(22.1) is None
        assert sum(
            event.detail == detail for event in events.messages
        ) == 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


def _activate_m4_5_retained_radius_two(node):
    anchor = np.array([1.2320122160, 1.4710422281])
    current = np.array([1.3775, 1.5451])
    fill_center = np.array([1.8278297781, 1.7700514862])
    node.latest_pose = Pose2D(0.0, *anchor, 0.0)
    node.latest_pose_valid = True
    node.latest_pose_sequence += 1
    node.active_fill_records = {
        1: {
            'fill_id': 4,
            'revision': 1,
            'center': fill_center,
            'support_radius': 0.5086747487,
            'exit_radius': 0.4238956239,
        }
    }
    node.machine.state = State.SEARCH
    node.machine.active_fill_count = 1
    node.machine.post_recovery_fill_id = 4
    node.machine.active_escape_fill_id = 4
    node.machine.post_recovery_guidance_active = True
    node.machine.post_recovery_guidance_started_sec = 0.0
    assert node._start_post_recovery_epoch(
        0.0,
        source_led_handoff=True,
    ) is None
    return anchor, current, fill_center


def _feed_m4_5_retained_source_window(node, anchor, current):
    samples = (
        (3.0, anchor + [0.20, 0.0]),
        (6.0, anchor + [0.20, 0.20]),
        (9.0, anchor + [0.0, 0.20]),
        (12.0, current),
    )
    for stamp, position in samples:
        node.latest_pose = Pose2D(stamp, *position, 0.0)
        node.latest_pose_sequence += 1
        assert node._update_post_recovery_guidance(stamp) is None


def test_m4_6_exact_failed_geometry_uses_only_calibrated_threshold():
    anchor = np.array([1.1809160175, 1.5969815630])
    current = np.array([1.3563818523, 1.5646136279])
    fill_center = np.array([1.8117325336, 1.7511796132])

    assert source_continuity_evidence(
        anchor,
        current,
        fill_center,
        0.05,
        -0.90,
    ) is None
    evidence = source_continuity_evidence(
        anchor,
        current,
        fill_center,
        0.05,
        -0.80,
    )

    assert evidence is not None
    assert evidence.displacement_m == pytest.approx(0.1784262940)
    assert evidence.radial_alignment == pytest.approx(-0.8412123478)
    assert evidence.direction == pytest.approx(
        [0.9834079430, -0.1814078764]
    )

    avoidance_radius = 0.6086747487
    selected = select_safe_direction(
        current,
        evidence.direction,
        [
            FillAvoidance(
                4,
                1,
                fill_center[0],
                fill_center[1],
                avoidance_radius,
            )
        ],
        DirectionConfig(
            lookahead_m=0.50,
            candidate_step_rad=0.7853981633974483,
        ),
        OperatingBounds(
            x_min=-0.25,
            x_max=3.75,
            y_min=-0.25,
            y_max=3.75,
            center_x=1.75,
            center_y=1.75,
            wall_margin=0.20,
        ),
    )

    assert selected is not None
    assert selected.direction == pytest.approx(
        [-0.1814078760, -0.9834079431]
    )
    assert np.dot(
        selected.direction,
        evidence.direction,
    ) == pytest.approx(0.0, abs=1e-12)
    radial_outward = (
        (current - fill_center)
        / np.linalg.norm(current - fill_center)
    )
    assert np.dot(
        selected.direction,
        radial_outward,
    ) == pytest.approx(0.5407048973)
    endpoint = current + 0.50 * selected.direction
    assert np.linalg.norm(
        endpoint - fill_center
    ) == pytest.approx(0.8707616100)
    assert (
        np.linalg.norm(endpoint - fill_center)
        > avoidance_radius + 0.10
    )


@pytest.mark.parametrize(
    ('case_id', 'radial_alignment', 'should_trigger'),
    [
        ('m4_4_visible_central', -0.336356, False),
        ('m4_4_radius_1p0', 0.885685, False),
        ('m4_4_radius_1p5_a45', 0.201668, False),
        ('m4_4_radius_1p5_a67p5', 0.787593, False),
        ('m4_4_radius_2p0', -0.9999689709, True),
        ('m4_4_repeat_18410', 0.413417, False),
        ('m4_4_repeat_18411', 0.953112, False),
        ('m4_4_repeat_18412', -0.192921, False),
        ('m4_5_radius_2p0', -0.8412123478, True),
    ],
)
def test_m4_6_calibration_replays_retained_alignment_table(
    case_id,
    radial_alignment,
    should_trigger,
):
    direction = np.array([1.0, 0.0])
    current = np.array([1.0, 1.0])
    anchor = current - 0.20 * direction
    radial_outward = np.array([
        radial_alignment,
        math.sqrt(max(0.0, 1.0 - radial_alignment ** 2)),
    ])
    fill_center = current - radial_outward

    evidence = source_continuity_evidence(
        anchor,
        current,
        fill_center,
        0.05,
        -0.80,
    )

    assert (evidence is not None) is should_trigger, case_id
    if evidence is not None:
        assert evidence.radial_alignment == pytest.approx(
            radial_alignment
        )


def test_m4_5_retained_radius_two_arms_nonreversing_safe_bypass():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_liveness_window_sec=12.0,
        post_recovery_source_led_handoff_enabled=True,
        post_recovery_source_continuity_enabled=True,
    )
    events = Recorder()
    states = Recorder()
    node.event_publisher = events
    node.state_publisher = states
    try:
        anchor, current, unused_fill = (
            _activate_m4_5_retained_radius_two(node)
        )
        _feed_m4_5_retained_source_window(node, anchor, current)
        node._publish_state_and_command(12.0)

        assert node.post_recovery_source_led_active is False
        assert node.post_recovery_source_bypass_active is True
        assert node.post_recovery_source_continuity is not None
        assert node.safe_direction is not None
        assert (
            np.dot(
                node.safe_direction.direction,
                node.post_recovery_source_continuity.direction,
            )
            >= -1e-12
        )
        assert node.safe_direction.direction == pytest.approx(
            [-0.4536405406, 0.8911847507]
        )
        assert states.messages[-1].affine_weight == pytest.approx(0.50)
        assert sum(
            event.detail
            == 'post-recovery source-continuity bypass armed'
            for event in events.messages
        ) == 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_5_source_bypass_releases_at_exact_clearance_boundary():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_liveness_window_sec=12.0,
        post_recovery_source_led_handoff_enabled=True,
        post_recovery_source_continuity_enabled=True,
    )
    events = Recorder()
    node.event_publisher = events
    try:
        anchor, current, fill_center = (
            _activate_m4_5_retained_radius_two(node)
        )
        _feed_m4_5_retained_source_window(node, anchor, current)
        target = node._source_bypass_clearance_target()
        assert target == pytest.approx(0.7086747487)
        radial = (current - fill_center) / np.linalg.norm(
            current - fill_center
        )

        node.latest_pose = Pose2D(
            12.1,
            *(fill_center + (target - 1e-6) * radial),
            0.0,
        )
        node.latest_pose_sequence += 1
        assert node._update_post_recovery_guidance(12.1) is None
        assert node.post_recovery_source_bypass_active is True

        node.latest_pose = Pose2D(
            12.2,
            *(fill_center + target * radial),
            0.0,
        )
        node.latest_pose_sequence += 1
        assert node._update_post_recovery_guidance(12.2) is None

        assert node.machine.post_recovery_guidance_active is False
        assert node.post_recovery_source_bypass_active is False
        assert node.post_recovery_source_continuity is None
        assert node.safe_direction is None
        assert sum(
            event.detail
            == 'post-recovery source-continuity bypass completed'
            for event in events.messages
        ) == 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_7_clearance_transitions_to_resume_without_releasing_guidance():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_liveness_window_sec=12.0,
        post_recovery_source_led_handoff_enabled=True,
        post_recovery_source_continuity_enabled=True,
        post_recovery_source_resume_enabled=True,
        post_recovery_source_resume_min_progress_m=0.20,
    )
    events = Recorder()
    states = Recorder()
    node.event_publisher = events
    node.state_publisher = states
    try:
        anchor, current, fill_center = (
            _activate_m4_5_retained_radius_two(node)
        )
        _feed_m4_5_retained_source_window(node, anchor, current)
        target = node._source_bypass_clearance_target()
        radial = (current - fill_center) / np.linalg.norm(
            current - fill_center
        )
        clearance_pose = fill_center + target * radial

        node.latest_pose = Pose2D(12.2, *clearance_pose, 0.0)
        node.latest_pose_sequence += 1
        assert node._update_post_recovery_guidance(12.2) is None
        node._publish_state_and_command(12.2)

        assert node.machine.post_recovery_guidance_active is True
        assert node.post_recovery_source_bypass_active is False
        assert node.post_recovery_source_resume_active is True
        assert node.post_recovery_source_resume_anchor == pytest.approx(
            clearance_pose
        )
        assert node.post_recovery_source_continuity is not None
        assert node.safe_direction is not None
        assert states.messages[-1].affine_weight == pytest.approx(0.50)
        assert sum(
            event.detail
            == 'post-recovery source-bypass clearance acquired'
            for event in events.messages
        ) == 1
        assert sum(
            event.detail == 'post-recovery source-resume corridor armed'
            for event in events.messages
        ) == 1
        assert all(
            event.detail
            != 'post-recovery source-continuity bypass completed'
            for event in events.messages
        )
    finally:
        node.destroy_node()
        rclpy.shutdown()


def _activate_m4_7_resume_corridor(node):
    _activate_m4_2_guidance(
        node,
        pose_value=Pose2D(0.0, 0.50, 0.0, 0.0),
    )
    node.active_fill_records[1]['center'] = [0.0, 0.0]
    node.post_recovery_progress_tracker = (
        supervisor_node_script.PostRecoveryProgressTracker(
            node.latest_pose,
            [0.0, 0.0],
            node.post_recovery_progress_config,
        )
    )
    node.post_recovery_pose_sequence = node.latest_pose_sequence
    node.post_recovery_source_continuity = SourceContinuityEvidence(
        direction_x=1.0,
        direction_y=0.0,
        displacement_m=0.10,
        radial_alignment=-1.0,
    )
    node.post_recovery_source_bypass_active = False
    node.post_recovery_source_resume_active = True
    node.post_recovery_source_resume_anchor = np.array([0.50, 0.0])
    node.post_recovery_source_progress_acquired = False
    node.safe_direction = None
    assert node._ensure_post_recovery_direction() is None


def test_m4_7_source_progress_and_existing_taper_both_gate_release():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_source_led_handoff_enabled=True,
        post_recovery_source_continuity_enabled=True,
        post_recovery_source_resume_enabled=True,
        post_recovery_source_resume_min_progress_m=0.20,
    )
    events = Recorder()
    states = Recorder()
    commands = Recorder()
    node.event_publisher = events
    node.state_publisher = states
    node.command_publisher = commands
    try:
        _activate_m4_7_resume_corridor(node)

        def update(stamp, x):
            node.latest_pose = Pose2D(stamp, x, 0.0, 0.0)
            node.latest_pose_sequence += 1
            assert node._update_post_recovery_guidance(stamp) is None
            node._publish_state_and_command(stamp)

        update(1.0, 0.50 + 0.20 - 1e-6)
        assert node.post_recovery_source_progress_acquired is False
        assert node.machine.post_recovery_guidance_active is True
        assert states.messages[-1].affine_weight == pytest.approx(0.50)
        assert commands.messages[-1].linear.x > 0.0

        update(2.0, 0.70)
        assert node.post_recovery_source_progress_acquired is True
        assert node.machine.post_recovery_guidance_active is True
        assert states.messages[-1].affine_weight == pytest.approx(0.50)

        update(3.0, 1.10)
        assert node.machine.post_recovery_guidance_active is True
        assert states.messages[-1].affine_weight == pytest.approx(0.50)
        assert commands.messages[-1].linear.x == 0.0

        update(4.0, 1.35)
        assert node.machine.post_recovery_guidance_active is True
        assert states.messages[-1].affine_weight == pytest.approx(0.25)

        update(5.0, 1.60)
        assert node.machine.post_recovery_guidance_active is False
        assert node.post_recovery_source_continuity is None
        assert node.post_recovery_source_resume_active is False
        assert node.safe_direction is None
        assert sum(
            event.detail == 'post-recovery source progress acquired'
            for event in events.messages
        ) == 1
        assert sum(
            event.detail
            == 'post-recovery source-resume corridor completed'
            for event in events.messages
        ) == 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_7_resume_recomputation_uses_source_not_radial_preference():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_source_led_handoff_enabled=True,
        post_recovery_source_continuity_enabled=True,
        post_recovery_source_resume_enabled=True,
        post_recovery_source_resume_min_progress_m=0.20,
    )
    try:
        _activate_m4_7_resume_corridor(node)
        node.latest_pose = Pose2D(0.0, 1.0, 1.0, 0.0)
        node.latest_pose_sequence += 1
        node.active_fill_records[1]['center'] = [1.0, 0.0]
        node.post_recovery_progress_tracker = (
            supervisor_node_script.PostRecoveryProgressTracker(
                node.latest_pose,
                [1.0, 0.0],
                node.post_recovery_progress_config,
            )
        )
        node.post_recovery_source_continuity = SourceContinuityEvidence(
            direction_x=1.0,
            direction_y=0.0,
            displacement_m=0.10,
            radial_alignment=0.0,
        )
        node.post_recovery_source_bypass_active = False
        node.post_recovery_source_resume_active = True
        node.post_recovery_source_resume_anchor = np.array([1.0, 1.0])
        node.safe_direction = None

        assert node._ensure_post_recovery_direction() is None
        assert node.safe_direction.direction == pytest.approx([1.0, 0.0])
        assert float(
            np.dot(
                node.safe_direction.direction,
                node.post_recovery_source_continuity.direction,
            )
        ) == pytest.approx(1.0)
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_7_dynamic_upgrade_does_not_consume_liveness_refresh():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_source_led_handoff_enabled=True,
        post_recovery_source_continuity_enabled=True,
        post_recovery_source_resume_enabled=True,
        post_recovery_source_resume_min_progress_m=0.20,
    )
    events = Recorder()
    node.event_publisher = events
    try:
        source = np.array([0.9909899820, 0.1339360130])
        source /= np.linalg.norm(source)
        anchor = np.array([1.2274432561, 1.4964333762])
        arm = anchor + 0.1147496923 * source
        fill_center = np.array([1.8189935808, 1.7649913445])
        tangent = np.array([source[1], -source[0]])
        node.latest_pose = Pose2D(0.0, *arm, 0.0)
        node.latest_pose_valid = True
        node.latest_pose_sequence += 1
        node.active_fill_records = {
            1: {
                'fill_id': 4,
                'revision': 1,
                'center': fill_center,
                'support_radius': 0.5086747487,
                'exit_radius': 0.4238956239,
            }
        }
        node.machine.state = State.SEARCH
        node.machine.active_fill_count = 1
        node.machine.post_recovery_fill_id = 4
        node.machine.active_escape_fill_id = 4
        node.machine.post_recovery_guidance_active = True
        node.machine.post_recovery_guidance_started_sec = 0.0
        node.post_recovery_source_continuity = SourceContinuityEvidence(
            direction_x=source[0],
            direction_y=source[1],
            displacement_m=0.1147496923,
            radial_alignment=-0.9383691118,
        )
        node.post_recovery_source_bypass_active = True
        node.post_recovery_progress_tracker = (
            supervisor_node_script.PostRecoveryProgressTracker(
                node.latest_pose,
                fill_center,
                node.post_recovery_progress_config,
            )
        )
        node.post_recovery_pose_sequence = node.latest_pose_sequence

        assert node._ensure_post_recovery_direction() is None
        assert math.degrees(
            node.safe_direction.rotation_rad
        ) == pytest.approx(-90.0)
        initial_revision = node.safe_direction_revision

        node.latest_pose = Pose2D(0.1, *(arm + 0.20 * tangent), 0.0)
        node.latest_pose_sequence += 1
        assert node._update_post_recovery_guidance(0.1) is None

        assert math.degrees(
            node.safe_direction.rotation_rad
        ) == pytest.approx(-45.0)
        assert node.safe_direction_revision == initial_revision + 1
        assert node.post_recovery_direction_refresh_count == 0
        assert sum(
            event.detail
            == 'post-recovery source-continuity direction changed'
            for event in events.messages
        ) == 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_7_recenter_resets_resume_anchor_and_excludes_its_motion():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_source_led_handoff_enabled=True,
        post_recovery_source_continuity_enabled=True,
        post_recovery_source_resume_enabled=True,
        post_recovery_source_resume_min_progress_m=0.20,
    )
    try:
        _activate_m4_7_resume_corridor(node)
        node.post_recovery_recenter_attempted = True
        node.latest_pose = Pose2D(10.0, 1.50, 0.0, 0.0)
        node.latest_pose_sequence += 1

        assert node._start_post_recovery_epoch(
            10.0,
            source_led_handoff=True,
        ) is None

        assert node.post_recovery_source_resume_active is True
        assert node.post_recovery_source_resume_anchor == pytest.approx(
            [1.50, 0.0]
        )
        assert node._source_resume_progress() == pytest.approx(0.0)
        assert node.post_recovery_source_progress_acquired is False
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_7_post_recenter_liveness_keeps_corridor_nonterminal():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_source_led_handoff_enabled=True,
        post_recovery_source_continuity_enabled=True,
        post_recovery_source_resume_enabled=True,
        post_recovery_source_resume_min_progress_m=0.20,
    )
    events = Recorder()
    node.event_publisher = events
    try:
        _activate_m4_7_resume_corridor(node)
        node.post_recovery_recenter_attempted = True
        node.post_recovery_direction_refresh_count = (
            node.post_recovery_direction_refresh_limit
        )
        for stamp, offset in (
            (1.0, (0.0, 0.20)),
            (2.0, (-0.20, 0.20)),
            (3.0, (-0.20, 0.0)),
            (4.0, (0.0, 0.0)),
        ):
            node.latest_pose = Pose2D(
                stamp,
                0.50 + offset[0],
                offset[1],
                0.0,
            )
            node.latest_pose_sequence += 1
            assert node._update_post_recovery_guidance(stamp) is None

        assert node.machine.post_recovery_guidance_active is True
        assert node.machine.state == State.SEARCH
        assert node.machine.state != State.FAILSAFE
        assert node.post_recovery_source_resume_active is True
        assert node.recenter_recovery_requested is False
        assert any(
            event.detail
            == 'post-recovery source-resume liveness persists after recenter'
            for event in events.messages
        )
        assert (
            node.post_recovery_progress_tracker.latest.window_valid
            is False
        )
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_7_corridor_duration_exhaustion_releases_nonterminal():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_source_led_handoff_enabled=True,
        post_recovery_source_continuity_enabled=True,
        post_recovery_source_resume_enabled=True,
        post_recovery_source_resume_min_progress_m=0.20,
    )
    events = Recorder()
    node.event_publisher = events
    try:
        _activate_m4_7_resume_corridor(node)
        started = node.machine.post_recovery_guidance_started_sec

        assert node._update_post_recovery_guidance(started + 90.0) is None

        assert node.machine.post_recovery_guidance_active is False
        assert node.machine.active_escape_fill_id is None
        assert node.machine.state == State.SEARCH
        assert node.machine.state != State.FAILSAFE
        assert node.post_recovery_source_continuity is None
        assert node.post_recovery_source_resume_active is False
        report = next(
            event
            for event in events.messages
            if event.detail
            == 'post-recovery source-resume corridor exhausted'
        )
        assert all(math.isfinite(value) for value in report.values)
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_7_no_safe_corridor_candidate_requests_bounded_recenter(
    monkeypatch,
):
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_source_led_handoff_enabled=True,
        post_recovery_source_continuity_enabled=True,
        post_recovery_source_resume_enabled=True,
        post_recovery_source_resume_min_progress_m=0.20,
    )
    events = Recorder()
    node.event_publisher = events
    try:
        _activate_m4_7_resume_corridor(node)
        monkeypatch.setattr(
            supervisor_node_script,
            'select_source_continuity_direction',
            lambda *args, **kwargs: None,
        )
        node.safe_direction = None
        node.latest_pose_sequence += 1

        assert node._update_post_recovery_guidance(1.0) is None

        assert node.machine.post_recovery_guidance_active is True
        assert node.machine.state == State.SEARCH
        assert node.machine.state != State.FAILSAFE
        assert node.recenter_recovery_requested is True
        assert node.post_recovery_recenter_attempted is True
        assert any(
            event.detail
            == 'post-recovery direction unavailable; recover by recenter'
            for event in events.messages
        )
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_5_source_constraint_survives_one_recoverable_recenter():
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_liveness_window_sec=12.0,
        post_recovery_source_led_handoff_enabled=True,
        post_recovery_source_continuity_enabled=True,
    )
    events = Recorder()
    node.event_publisher = events
    try:
        anchor, current, unused_fill = (
            _activate_m4_5_retained_radius_two(node)
        )
        _feed_m4_5_retained_source_window(node, anchor, current)
        retained_direction = (
            node.post_recovery_source_continuity.direction.copy()
        )
        node.post_recovery_recenter_attempted = True

        node.machine.state = State.RECENTER
        node._handle_transition(
            Transition(
                State.SEARCH,
                State.RECENTER,
                'post-recovery liveness recovery requested',
            ),
            12.1,
        )
        assert node.post_recovery_source_bypass_active is True
        assert node.post_recovery_source_continuity.direction == (
            pytest.approx(retained_direction)
        )

        node.recenter_distance = 0.0
        node.machine.state = State.SEARCH
        node._handle_transition(
            Transition(
                State.RECENTER,
                State.SEARCH,
                'recenter tolerance dwell satisfied',
            ),
            12.2,
        )

        assert node.post_recovery_source_led_active is False
        assert node.post_recovery_source_bypass_active is True
        assert node.safe_direction is not None
        assert np.dot(
            node.safe_direction.direction,
            retained_direction,
        ) >= -1e-12
    finally:
        node.destroy_node()
        rclpy.shutdown()


def test_m4_5_no_forward_safe_candidate_requests_bounded_recenter(
    monkeypatch,
):
    rclpy.init()
    node = _m4_2_progress_node(
        post_recovery_liveness_window_sec=12.0,
        post_recovery_source_led_handoff_enabled=True,
        post_recovery_source_continuity_enabled=True,
    )
    events = Recorder()
    node.event_publisher = events
    try:
        anchor, current, unused_fill = (
            _activate_m4_5_retained_radius_two(node)
        )
        monkeypatch.setattr(
            supervisor_node_script,
            'select_safe_direction',
            lambda *args, **kwargs: None,
        )
        _feed_m4_5_retained_source_window(node, anchor, current)

        assert node.post_recovery_source_bypass_active is True
        assert node.safe_direction is None
        assert node.recenter_recovery_requested is True
        assert node.post_recovery_recenter_attempted is True
        assert node.machine.post_recovery_guidance_active is True
        assert any(
            event.detail
            == 'post-recovery direction unavailable; recover by recenter'
            for event in events.messages
        )
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
