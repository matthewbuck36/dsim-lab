#!/usr/bin/env python3

"""ROS adapter for the robust GESC/Gaussian supervisor state machine."""

from collections import deque
import math
import uuid

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import numpy as np
import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from ros_esc_interfaces.msg import (
    AlgorithmEvent,
    AlgorithmState,
    CostBreakdown,
    GaussianFill,
    StampedFloat64MultiArray,
)
from std_msgs.msg import Bool

from ros_esc.deferred_signal_shutdown import DeferredSignalShutdown
from ros_esc.supervisor_node.escape_recenter import (
    DirectionConfig,
    DirectionSelection,
    EscapeGeometry,
    EscapeProgressConfig,
    EscapeProgressTracker,
    FillAvoidance,
    OperatingBounds,
    Pose2D,
    RecenterControlConfig,
    RecenterHoldTracker,
    evaluate_direction,
    preferred_escape_direction,
    recent_approach,
    recenter_command,
    select_safe_direction,
)
from ros_esc.supervisor_node.state_machine import (
    ROBUST_PROFILE,
    State,
    StateMachineConfig,
    SupervisorStateMachine,
    TransitionInputs,
)


ROBUST_FILL_CREATE = "ROBUST_FILL_CREATE"
ROBUST_FILL_REDESIGN_PREFIX = "ROBUST_FILL_REDESIGN:"


class SupervisorNode(Node):
    """Own robust state, escape geometry, fill requests, and recenter commands."""

    def __init__(self, parameter_overrides=None):
        super().__init__(
            "gesc_gaussian_supervisor",
            parameter_overrides=parameter_overrides,
        )
        self._declare_parameters()
        profile = str(self.get_parameter("algorithm_profile").value).strip()
        if profile != ROBUST_PROFILE:
            raise ValueError(
                "supervisor_node is only valid for algorithm_profile="
                f"{ROBUST_PROFILE}"
            )
        self.algorithm_profile = profile

        now_sec = self._now_sec()
        self.started_sec = now_sec
        self.machine = SupervisorStateMachine(
            now_sec=now_sec,
            config=StateMachineConfig(
                convergence_hold_sec=self._float("convergence_hold_sec"),
                goal_score_threshold=self._float("goal_score_threshold"),
                goal_hold_sec=self._float("goal_hold_sec"),
                undesired_score_hold_sec=self._float("undesired_score_hold_sec"),
                verification_max_sec=self._float("verification_max_sec"),
                fill_design_timeout_sec=self._float("fill_design_timeout_sec"),
                escape_max_sec=self._float("escape_max_sec"),
                recenter_after_escape=bool(
                    self.get_parameter("recenter_after_escape").value
                ),
                recenter_max_sec=self._float("recenter_max_sec"),
            ),
        )
        self.bounded_mode = bool(
            self.get_parameter("recenter_after_escape").value
        )
        self.bounds = None
        if self.bounded_mode:
            self.bounds = OperatingBounds(
                x_min=self._float("room_bounds_x_min_m"),
                x_max=self._float("room_bounds_x_max_m"),
                y_min=self._float("room_bounds_y_min_m"),
                y_max=self._float("room_bounds_y_max_m"),
                center_x=self._float("room_center_x_m"),
                center_y=self._float("room_center_y_m"),
                wall_margin=self._float("wall_margin_m"),
            )
        self.escape_progress_config = EscapeProgressConfig(
            stall_window_sec=self._float("stall_window_sec"),
            minimum_radial_progress_m=self._float(
                "minimum_radial_progress_m"
            ),
            escape_exit_hold_sec=self._float("escape_exit_hold_sec"),
        )
        self.direction_config = DirectionConfig(
            lookahead_m=self._float("direction_lookahead_m"),
            candidate_step_rad=self._float("direction_candidate_step_rad"),
        )
        self.recenter_config = RecenterControlConfig(
            tolerance_m=self._float("recenter_tolerance_m"),
            hold_sec=self._float("recenter_hold_sec"),
            linear_gain=self._float("recenter_linear_gain"),
            angular_gain=self._float("recenter_angular_gain"),
            max_linear_velocity_mps=self._float(
                "recenter_max_linear_velocity_mps"
            ),
            max_angular_velocity_rps=self._float(
                "recenter_max_angular_velocity_rps"
            ),
            rotate_in_place_angle_rad=self._float(
                "recenter_rotate_in_place_angle_rad"
            ),
        )
        self.approach_history_window_sec = self._positive_float(
            "approach_history_window_sec"
        )
        self.fill_avoidance_margin_m = self._nonnegative_float(
            "fill_avoidance_margin_m"
        )
        self.run_id = uuid.uuid4().hex
        self.latest_pose_receipt_sec = None
        self.latest_pose_valid = False
        self.latest_pose = None
        self.latest_pose_sequence = 0
        self.pose_history = deque(maxlen=20000)
        self.latest_source_receipt_sec = None
        self.latest_source_valid = False
        self.latest_source_score = None
        self.latest_source_score_valid = False
        self.latest_source_timestamp = None
        self.latest_convergence = None
        self.latest_convergence_receipt_sec = None
        self.pending_fill_result = None
        self.active_fill_records = {}
        self.escape_tracker = None
        self.escape_pose_sequence = 0
        self.safe_direction = None
        self.safe_direction_revision = 0
        self.recenter_hold_tracker = None
        self.recenter_distance = float("nan")
        self.recenter_complete = False
        self.current_supervisor_command = Twist()
        self.configuration_published = False
        self.stall_event_published = False
        self.stop_requested = False
        self.controller_fault = False
        self.graph_fault = self._graph_fault()

        self.state_publisher = self.create_publisher(
            AlgorithmState, self._string("algorithm_state_topic"), 10
        )
        self.event_publisher = self.create_publisher(
            AlgorithmEvent, self._string("algorithm_event_topic"), 10
        )
        self.fill_request_publisher = self.create_publisher(
            StampedFloat64MultiArray, self._string("fill_request_topic"), 10
        )
        self.command_publisher = self.create_publisher(
            Twist, self._string("supervisor_command_topic"), 10
        )

        self.pose_subscriber = self.create_subscription(
            Odometry, self._string("pose_topic"), self.pose_callback, 10
        )
        self.source_subscriber = self.create_subscription(
            CostBreakdown,
            self._string("source_cost_topic"),
            self.source_callback,
            10,
        )
        self.convergence_subscriber = self.create_subscription(
            StampedFloat64MultiArray,
            self._string("convergence_status_topic"),
            self.convergence_callback,
            10,
        )
        self.fill_subscriber = self.create_subscription(
            GaussianFill,
            self._string("gaussian_fill_diagnostics_topic"),
            self.fill_callback,
            10,
        )
        self.stop_subscriber = self.create_subscription(
            Bool, self._string("supervisor_stop_topic"), self.stop_callback, 10
        )
        self.event_subscriber = self.create_subscription(
            AlgorithmEvent,
            self._string("algorithm_event_topic"),
            self.event_callback,
            10,
        )

        publish_rate = max(1e-6, self._float("supervisor_publish_rate_hz"))
        self.timer = self.create_timer(1.0 / publish_rate, self.timer_callback)
        self._publish_state_and_command(now_sec)

    def _declare_parameters(self):
        defaults = {
            "algorithm_profile": ROBUST_PROFILE,
            "supervisor_publish_rate_hz": 20.0,
            "startup_timeout_sec": 5.0,
            "convergence_hold_sec": 2.0,
            "goal_score_threshold": 0.95,
            "goal_hold_sec": 3.0,
            "undesired_score_hold_sec": 3.0,
            "verification_max_sec": 10.0,
            "fill_design_timeout_sec": 5.0,
            "escape_max_sec": 20.0,
            "escape_exit_hold_sec": 1.0,
            "stall_window_sec": 3.0,
            "minimum_radial_progress_m": 0.05,
            "approach_history_window_sec": 3.0,
            "recenter_after_escape": True,
            "recenter_max_sec": 30.0,
            "room_bounds_x_min_m": -2.0,
            "room_bounds_x_max_m": 2.0,
            "room_bounds_y_min_m": -2.0,
            "room_bounds_y_max_m": 2.0,
            "room_center_x_m": 0.0,
            "room_center_y_m": 0.0,
            "wall_margin_m": 0.35,
            "direction_lookahead_m": 0.50,
            "direction_candidate_step_rad": math.pi / 4.0,
            "fill_avoidance_margin_m": 0.10,
            "recenter_tolerance_m": 0.25,
            "recenter_hold_sec": 1.0,
            "recenter_linear_gain": 0.50,
            "recenter_angular_gain": 1.50,
            "recenter_max_linear_velocity_mps": 0.10,
            "recenter_max_angular_velocity_rps": 0.40,
            "recenter_rotate_in_place_angle_rad": math.pi / 3.0,
            "stale_pose_sec": 0.5,
            "stale_sensor_sec": 0.5,
            "pose_topic": "/odom",
            "source_cost_topic": "/gesc_gaussian/source_cost",
            "convergence_status_topic": "/gesc_gaussian/convergence_status",
            "fill_request_topic": "/gesc_gaussian/fill_requests",
            "supervisor_command_topic": "/gesc_gaussian/supervisor_command",
            "supervisor_stop_topic": "/gesc_gaussian/stop_requested",
            "algorithm_state_topic": "/gesc_gaussian/algorithm_state",
            "algorithm_event_topic": "/gesc_gaussian/algorithm_events",
            "gaussian_fill_diagnostics_topic": "/gesc_gaussian/gaussian_fills",
            "pde_extensions_enabled": True,
            "directional_controller_selected": True,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

    def _float(self, name):
        return float(self.get_parameter(name).value)

    def _positive_float(self, name):
        value = self._float(name)
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be finite and positive")
        return value

    def _nonnegative_float(self, name):
        value = self._float(name)
        if not math.isfinite(value) or value < 0.0:
            raise ValueError(f"{name} must be finite and nonnegative")
        return value

    def _string(self, name):
        return str(self.get_parameter(name).value)

    def _now_sec(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def _graph_fault(self):
        if not bool(self.get_parameter("pde_extensions_enabled").value):
            return "robust profile requires PDE/Gaussian extensions"
        if not bool(self.get_parameter("directional_controller_selected").value):
            return "robust profile requires Directional_Controller"
        return None

    def pose_callback(self, msg):
        values = np.array(
            [
                msg.pose.pose.position.x,
                msg.pose.pose.position.y,
                msg.pose.pose.position.z,
                msg.pose.pose.orientation.x,
                msg.pose.pose.orientation.y,
                msg.pose.pose.orientation.z,
                msg.pose.pose.orientation.w,
            ],
            dtype=np.float64,
        )
        quat_norm = float(np.linalg.norm(values[3:]))
        self.latest_pose_valid = bool(
            np.all(np.isfinite(values)) and quat_norm > 1e-9
        )
        receipt_sec = self._now_sec()
        self.latest_pose_receipt_sec = receipt_sec
        self.latest_pose_sequence += 1
        if self.latest_pose_valid:
            quaternion = values[3:] / quat_norm
            x_value, y_value, z_value, w_value = quaternion
            yaw = math.atan2(
                2.0 * (w_value * z_value + x_value * y_value),
                1.0 - 2.0 * (y_value ** 2 + z_value ** 2),
            )
            self.latest_pose = Pose2D(
                receipt_sec,
                float(values[0]),
                float(values[1]),
                yaw,
            )
            if not self.pose_history or receipt_sec > self.pose_history[-1].stamp_sec:
                self.pose_history.append(self.latest_pose)
            elif receipt_sec == self.pose_history[-1].stamp_sec:
                self.pose_history[-1] = self.latest_pose

    def source_callback(self, msg):
        raw = np.asarray(msg.raw_cost, dtype=np.float64)
        count_valid = int(msg.channel_count) == raw.size and raw.size > 0
        self.latest_source_valid = bool(
            msg.source_timestamp_valid
            and math.isfinite(msg.source_timestamp)
            and msg.raw_cost_valid
            and count_valid
            and np.all(np.isfinite(raw))
        )
        scores = np.asarray(msg.source_score, dtype=np.float64)
        self.latest_source_score_valid = bool(
            msg.source_score_valid
            and scores.size == raw.size
            and scores.size > 0
            and np.all(np.isfinite(scores))
        )
        self.latest_source_score = (
            float(np.max(scores)) if self.latest_source_score_valid else None
        )
        self.latest_source_timestamp = (
            float(msg.source_timestamp)
            if msg.source_timestamp_valid and math.isfinite(msg.source_timestamp)
            else None
        )
        self.latest_source_receipt_sec = self._now_sec()

    def convergence_callback(self, msg):
        data = np.asarray(msg.data, dtype=np.float64)
        if data.size != 8 or not np.all(np.isfinite(data)):
            self.latest_convergence = None
            self.latest_convergence_receipt_sec = self._now_sec()
            return
        copied = StampedFloat64MultiArray()
        copied.header = msg.header
        copied.timestamp = float(msg.timestamp)
        copied.data = [float(value) for value in data]
        self.latest_convergence = copied
        self.latest_convergence_receipt_sec = self._now_sec()

    def fill_callback(self, msg):
        if not msg.source_timestamp_valid:
            return
        cluster_id = int(msg.cluster_id)
        fill_id = int(msg.fill_id)
        revision = int(msg.revision)
        if cluster_id <= 0 or fill_id <= 0 or revision <= 0:
            return
        current = self.active_fill_records.get(cluster_id)
        if msg.superseded or not msg.active:
            if (
                current is not None
                and current["revision"] == revision
                and current["fill_id"] == fill_id
            ):
                del self.active_fill_records[cluster_id]
            return
        if current is not None:
            if revision < current["revision"]:
                return
            if revision == current["revision"]:
                return
        required = np.array(
            [
                msg.center_x,
                msg.center_y,
                msg.amplitude,
                msg.sigma_major,
                msg.sigma_minor,
                msg.support_radius,
                msg.exit_radius,
            ],
            dtype=np.float64,
        )
        valid = bool(
            msg.frame_id == "odom"
            and msg.covariance_valid
            and msg.principal_widths_valid
            and msg.support_radius_valid
            and msg.exit_radius_valid
            and np.all(np.isfinite(required))
            and msg.amplitude >= 0.0
            and msg.sigma_major > 0.0
            and msg.sigma_minor > 0.0
            and msg.support_radius > 0.0
            and msg.exit_radius > 0.0
        )
        if valid:
            self.active_fill_records[cluster_id] = {
                "revision": revision,
                "fill_id": fill_id,
                "center": np.array(
                    [msg.center_x, msg.center_y], dtype=np.float64
                ),
                "support_radius": float(msg.support_radius),
                "exit_radius": float(msg.exit_radius),
            }
        self.pending_fill_result = (
            "success" if valid else "rejected",
            float(msg.source_timestamp),
            fill_id,
            len(self.active_fill_records),
        )

    def stop_callback(self, msg):
        if bool(msg.data):
            self.stop_requested = True

    def event_callback(self, msg):
        if (
            msg.event_type == AlgorithmEvent.EVENT_FAILSAFE
            and msg.detail.startswith("controller watchdog:")
        ):
            self.controller_fault = True
        if (
            msg.event_type
            in (
                AlgorithmEvent.EVENT_FILL_REJECTED,
                AlgorithmEvent.EVENT_FILL_DESIGN_FAILED,
            )
            and msg.source_timestamp_valid
        ):
            self.pending_fill_result = (
                "rejected",
                float(msg.source_timestamp),
                None,
                len(self.active_fill_records),
            )

    def timer_callback(self):
        now_sec = self._now_sec()
        self.current_supervisor_command = Twist()
        try:
            if (
                not self.configuration_published
                and self.latest_pose_receipt_sec is not None
                and self.latest_source_receipt_sec is not None
            ):
                self._publish_configuration_event(now_sec)
                self.configuration_published = True
            if self.graph_fault is not None:
                transition = self.machine.force_failsafe(now_sec, self.graph_fault)
                if transition is not None:
                    self._handle_transition(transition, now_sec)
                self.graph_fault = None
            if self.machine.state != State.FAILSAFE:
                geometry_fault = self._prepare_geometry(now_sec)
                if geometry_fault is not None:
                    self._force_failsafe(now_sec, geometry_fault)
                else:
                    transition = self.machine.step(
                        now_sec, self._transition_inputs(now_sec)
                    )
                    self.pending_fill_result = None
                    if transition is not None:
                        self._handle_transition(transition, now_sec)
        except Exception as exc:  # safety boundary at the ROS adapter
            self.current_supervisor_command = Twist()
            self._force_failsafe(
                now_sec,
                f"supervisor exception: {type(exc).__name__}: {exc}",
            )
        self._publish_state_and_command(now_sec)

    def _prepare_geometry(self, now_sec):
        if (
            self.bounds is not None
            and self.latest_pose_valid
            and self.latest_pose is not None
            and not self.bounds.contains(self.latest_pose.position)
        ):
            return "pose outside wall-margin-inset operating bounds"

        if (
            self.escape_tracker is not None
            and self.latest_pose_valid
            and self.latest_pose is not None
            and self.latest_pose_sequence != self.escape_pose_sequence
            and self.machine.state
            in (
                State.ESCAPE_REPULSE,
                State.DESIGN_OR_MERGE_FILL,
                State.ESCAPE_ASSIST,
            )
        ):
            self.escape_tracker.update(self.latest_pose)
            self.escape_pose_sequence = self.latest_pose_sequence

        if self.machine.state == State.ESCAPE_ASSIST:
            return self._ensure_safe_direction(recenter=False)
        if self.machine.state == State.RECENTER:
            return self._update_recenter(now_sec)
        return None

    def _transition_inputs(self, now_sec):
        startup_grace = now_sec - self.started_sec < self._float("startup_timeout_sec")
        pose_valid = startup_grace or self._fresh(
            self.latest_pose_receipt_sec, self._float("stale_pose_sec"), now_sec
        ) and self.latest_pose_valid
        sensor_valid = startup_grace or self._fresh(
            self.latest_source_receipt_sec,
            self._float("stale_sensor_sec"),
            now_sec,
        ) and self.latest_source_valid
        convergence_fresh = self._fresh(
            self.latest_convergence_receipt_sec,
            self._float("stale_sensor_sec"),
            now_sec,
        )
        convergence = bool(
            convergence_fresh
            and self.latest_convergence is not None
            and float(self.latest_convergence.data[0]) <= 0.0
        )
        fill_result = self.pending_fill_result or (None, None, None, None)
        progress = (
            self.escape_tracker.latest
            if self.escape_tracker is not None
            else None
        )
        return TransitionInputs(
            convergence=convergence,
            source_score=self.latest_source_score,
            source_score_valid=self.latest_source_score_valid,
            pose_valid=pose_valid,
            sensor_valid=sensor_valid,
            explicit_stop=self.stop_requested,
            controller_fault=self.controller_fault,
            fill_result=fill_result[0],
            fill_source_timestamp=fill_result[1],
            fill_id=fill_result[2],
            active_fill_count=fill_result[3],
            stable_exit=bool(
                progress is not None
                and self.machine.state
                in (State.ESCAPE_REPULSE, State.ESCAPE_ASSIST)
                and progress.stable_exit
            ),
            stalled=bool(
                progress is not None
                and self.machine.state == State.ESCAPE_REPULSE
                and progress.stalled_valid
                and progress.stalled
            ),
            recenter_complete=bool(
                self.machine.state == State.RECENTER
                and self.recenter_complete
            ),
        )

    @staticmethod
    def _fresh(receipt_sec, limit_sec, now_sec):
        return bool(
            receipt_sec is not None
            and now_sec >= receipt_sec
            and now_sec - receipt_sec <= limit_sec
        )

    def _handle_transition(self, transition, now_sec):
        if "escape stalled" in transition.reason:
            self._publish_stall_event(now_sec, transition.previous)
        self._publish_transition(transition, now_sec)
        if transition.current == State.DESIGN_OR_MERGE_FILL:
            if self.latest_convergence is None:
                self._force_failsafe(
                    now_sec, "fill request has no convergence snapshot"
                )
                return
            request = StampedFloat64MultiArray()
            request.timestamp = float(self.latest_convergence.timestamp)
            request.data = [float(value) for value in self.latest_convergence.data]
            if self.machine.design_returns_to_assist:
                if self.machine.active_escape_fill_id is None:
                    self._force_failsafe(
                        now_sec, "stall redesign has no active escape fill"
                    )
                    return
                request.header = (
                    ROBUST_FILL_REDESIGN_PREFIX
                    + str(self.machine.active_escape_fill_id)
                )
            else:
                request.header = ROBUST_FILL_CREATE
            self.machine.register_fill_request(request.timestamp)
            self.fill_request_publisher.publish(request)
        if transition.current == State.GOAL_HOLD:
            self.current_supervisor_command = Twist()
            self._publish_event(
                AlgorithmEvent.EVENT_GOAL_REACHED,
                now_sec,
                "goal source-score dwell satisfied",
            )
            self._reset_escape_attempt()
        if transition.current == State.ESCAPE_REPULSE:
            failure = self._begin_escape(now_sec)
            if failure is not None:
                self._force_failsafe(now_sec, failure)
                return
            geometry = self.escape_tracker.geometry
            self._publish_event(
                AlgorithmEvent.EVENT_ESCAPE_STARTED,
                now_sec,
                "Gaussian repulsion escape started",
                [
                    "initial_fill_id",
                    "escape_center_x_m",
                    "escape_center_y_m",
                    "escape_exit_radius_m",
                    "approach_x_m",
                    "approach_y_m",
                ],
                [
                    float(geometry.initial_fill_id),
                    geometry.center_x,
                    geometry.center_y,
                    geometry.exit_radius,
                    geometry.approach_x,
                    geometry.approach_y,
                ],
            )
        if transition.current == State.ESCAPE_ASSIST:
            failure = self._ensure_safe_direction(recenter=False)
            if failure is not None:
                self._force_failsafe(now_sec, failure)
                return
        if transition.current == State.RECENTER:
            self.current_supervisor_command = Twist()
            self.safe_direction = None
            self.recenter_hold_tracker = RecenterHoldTracker(
                self.recenter_config
            )
            self.recenter_distance = float("nan")
            self.recenter_complete = False
            self._publish_event(
                AlgorithmEvent.EVENT_RECENTER_STARTED,
                now_sec,
                "bounded center-return controller started",
                ["target_x_m", "target_y_m", "active_fill_count"],
                [
                    self.bounds.center_x,
                    self.bounds.center_y,
                    float(len(self.active_fill_records)),
                ],
            )
        if transition.previous == State.RECENTER and transition.current == State.SEARCH:
            self._publish_event(
                AlgorithmEvent.EVENT_RECENTER_COMPLETE,
                now_sec,
                "recenter tolerance dwell satisfied",
                ["target_x_m", "target_y_m", "recenter_distance_m"],
                [
                    self.bounds.center_x,
                    self.bounds.center_y,
                    self.recenter_distance,
                ],
            )
        if "timeout" in transition.reason:
            self._publish_event(
                AlgorithmEvent.EVENT_TIMEOUT, now_sec, transition.reason
            )
        if transition.current == State.FAILSAFE:
            self.current_supervisor_command = Twist()
            self._publish_failsafe_event(now_sec, transition.reason)
            self._reset_escape_attempt()
        if transition.current == State.SEARCH:
            self._reset_escape_attempt()

    def _force_failsafe(self, now_sec, reason):
        self.current_supervisor_command = Twist()
        transition = self.machine.force_failsafe(now_sec, reason)
        if transition is not None:
            self._publish_transition(transition, now_sec)
            if "timeout" in transition.reason:
                self._publish_event(
                    AlgorithmEvent.EVENT_TIMEOUT, now_sec, transition.reason
                )
            self._publish_failsafe_event(now_sec, transition.reason)
            self._reset_escape_attempt()

    def _begin_escape(self, now_sec):
        if self.latest_pose is None or not self.latest_pose_valid:
            return "escape start requires a valid pose"
        record = self._record_for_fill(self.machine.active_escape_fill_id)
        if record is None:
            return "escape start fill has no active finite geometry"
        approach = recent_approach(
            tuple(self.pose_history), self.approach_history_window_sec
        )
        geometry = EscapeGeometry(
            initial_fill_id=int(record["fill_id"]),
            center_x=float(record["center"][0]),
            center_y=float(record["center"][1]),
            exit_radius=float(record["exit_radius"]),
            started_sec=float(self.machine.escape_started_sec or now_sec),
            approach_x=float(approach[0]),
            approach_y=float(approach[1]),
        )
        self.escape_tracker = EscapeProgressTracker(
            geometry, self.escape_progress_config
        )
        self.escape_tracker.update(self.latest_pose)
        self.escape_pose_sequence = self.latest_pose_sequence
        self.safe_direction = None
        self.safe_direction_revision = 0
        self.stall_event_published = False
        return None

    def _record_for_fill(self, fill_id):
        if fill_id is None:
            return None
        for record in self.active_fill_records.values():
            if record["fill_id"] == int(fill_id):
                return record
        return None

    def _active_fill_avoidances(self):
        avoidances = []
        for cluster_id, record in self.active_fill_records.items():
            avoidances.append(
                FillAvoidance(
                    fill_id=record["fill_id"],
                    cluster_id=cluster_id,
                    center_x=float(record["center"][0]),
                    center_y=float(record["center"][1]),
                    radius=(
                        record["support_radius"]
                        + self.fill_avoidance_margin_m
                    ),
                )
            )
        return tuple(avoidances)

    def _ensure_safe_direction(self, recenter):
        if self.latest_pose is None or not self.latest_pose_valid:
            return "safe-direction selection requires a valid pose"
        position = self.latest_pose.position
        if recenter:
            preferred = self.bounds.center - position
            if float(np.linalg.norm(preferred)) <= 1e-12:
                return None
        else:
            if self.escape_tracker is None:
                return "assisted escape has no frozen geometry"
            preferred = preferred_escape_direction(
                position,
                self.escape_tracker.geometry,
                self.bounds,
            )
        fills = self._active_fill_avoidances()
        if self.safe_direction is not None:
            safe, clearance = evaluate_direction(
                position,
                self.safe_direction.direction,
                preferred,
                fills,
                self.direction_config,
                self.bounds,
            )
            if safe:
                self.safe_direction = DirectionSelection(
                    self.safe_direction.x,
                    self.safe_direction.y,
                    clearance,
                    self.safe_direction.rotation_rad,
                    self.safe_direction.candidate_index,
                )
                return None
        selected = select_safe_direction(
            position,
            preferred,
            fills,
            self.direction_config,
            self.bounds,
        )
        if selected is None:
            return "no safe assisted/recenter direction candidate"
        self.safe_direction = selected
        self.safe_direction_revision += 1
        return None

    def _update_recenter(self, now_sec):
        if self.bounds is None:
            return "RECENTER requires configured bounded indoor mode"
        if self.latest_pose is None or not self.latest_pose_valid:
            return "recenter requires a valid pose"
        self.recenter_distance = float(
            np.linalg.norm(self.bounds.center - self.latest_pose.position)
        )
        if self.recenter_hold_tracker is None:
            self.recenter_hold_tracker = RecenterHoldTracker(
                self.recenter_config
            )
        self.recenter_complete = self.recenter_hold_tracker.update(
            now_sec, self.recenter_distance
        )
        if self.recenter_distance <= self.recenter_config.tolerance_m:
            self.current_supervisor_command = Twist()
            self.safe_direction = None
            return None
        failure = self._ensure_safe_direction(recenter=True)
        if failure is not None:
            return failure
        linear, angular = recenter_command(
            self.safe_direction.direction,
            self.latest_pose.yaw,
            self.recenter_distance,
            self.recenter_config,
        )
        command = Twist()
        command.linear.x = linear
        command.angular.z = angular
        self.current_supervisor_command = command
        return None

    def _reset_escape_attempt(self):
        self.escape_tracker = None
        self.escape_pose_sequence = 0
        self.safe_direction = None
        self.safe_direction_revision = 0
        self.recenter_hold_tracker = None
        self.recenter_distance = float("nan")
        self.recenter_complete = False
        self.stall_event_published = False
        self.current_supervisor_command = Twist()

    def _publish_stall_event(self, now_sec, event_state):
        if self.stall_event_published or self.escape_tracker is None:
            return
        progress = self.escape_tracker.latest
        geometry = self.escape_tracker.geometry
        if progress is None:
            return
        self.stall_event_published = True
        self._publish_event(
            AlgorithmEvent.EVENT_ESCAPE_STALLED,
            now_sec,
            "radial progress below threshold; requesting one targeted redesign",
            [
                "escape_center_x_m",
                "escape_center_y_m",
                "escape_exit_radius_m",
                "radial_distance_m",
                "radial_progress_m",
                "stall_window_sec",
                "minimum_radial_progress_m",
            ],
            [
                geometry.center_x,
                geometry.center_y,
                geometry.exit_radius,
                progress.radial_distance,
                progress.radial_progress,
                self.escape_progress_config.stall_window_sec,
                self.escape_progress_config.minimum_radial_progress_m,
            ],
            state_override=event_state,
        )

    def _publish_transition(self, transition, now_sec):
        self._publish_event(
            AlgorithmEvent.EVENT_STATE_TRANSITION,
            now_sec,
            f"{transition.previous.name}->{transition.current.name}: {transition.reason}",
        )

    def _publish_failsafe_event(self, now_sec, reason):
        self._publish_event(AlgorithmEvent.EVENT_FAILSAFE, now_sec, reason)

    def _publish_event(
        self,
        event_type,
        source_timestamp,
        detail,
        value_names=None,
        values=None,
        state_override=None,
    ):
        del source_timestamp
        event = AlgorithmEvent()
        event.stamp = self.get_clock().now().to_msg()
        event.source_timestamp = float(self.latest_source_timestamp or 0.0)
        event.source_timestamp_valid = self.latest_source_timestamp is not None
        event.event_type = event_type
        event_state = self.machine.state if state_override is None else state_override
        event.state = int(event_state)
        event.state_name = event_state.name
        event.state_valid = True
        event.fill_id = int(self.machine.active_escape_fill_id or 0)
        event.fill_id_valid = self.machine.active_escape_fill_id is not None
        event.reason_code = 0
        event.detail = detail
        event.value_names = list(value_names or [])
        event.values = [float(value) for value in (values or [])]
        self.event_publisher.publish(event)

    def _publish_configuration_event(self, now_sec):
        names = [
            "bounded_mode",
            "room_bounds_x_min_m",
            "room_bounds_x_max_m",
            "room_bounds_y_min_m",
            "room_bounds_y_max_m",
            "room_center_x_m",
            "room_center_y_m",
            "wall_margin_m",
            "escape_exit_hold_sec",
            "stall_window_sec",
            "minimum_radial_progress_m",
            "approach_history_window_sec",
            "direction_lookahead_m",
            "direction_candidate_step_rad",
            "fill_avoidance_margin_m",
            "recenter_tolerance_m",
            "recenter_hold_sec",
            "recenter_linear_gain",
            "recenter_angular_gain",
            "recenter_max_linear_velocity_mps",
            "recenter_max_angular_velocity_rps",
            "recenter_rotate_in_place_angle_rad",
        ]
        values = [
            1.0 if self.bounded_mode else 0.0,
            self._float("room_bounds_x_min_m"),
            self._float("room_bounds_x_max_m"),
            self._float("room_bounds_y_min_m"),
            self._float("room_bounds_y_max_m"),
            self._float("room_center_x_m"),
            self._float("room_center_y_m"),
            self._float("wall_margin_m"),
            self.escape_progress_config.escape_exit_hold_sec,
            self.escape_progress_config.stall_window_sec,
            self.escape_progress_config.minimum_radial_progress_m,
            self.approach_history_window_sec,
            self.direction_config.lookahead_m,
            self.direction_config.candidate_step_rad,
            self.fill_avoidance_margin_m,
            self.recenter_config.tolerance_m,
            self.recenter_config.hold_sec,
            self.recenter_config.linear_gain,
            self.recenter_config.angular_gain,
            self.recenter_config.max_linear_velocity_mps,
            self.recenter_config.max_angular_velocity_rps,
            self.recenter_config.rotate_in_place_angle_rad,
        ]
        self._publish_event(
            AlgorithmEvent.EVENT_CONFIGURATION,
            now_sec,
            "measured escape, safe-direction, and recenter configuration",
            names,
            values,
        )

    def _publish_state_and_command(self, now_sec):
        state = AlgorithmState()
        state.stamp = self.get_clock().now().to_msg()
        state.source_timestamp = float(self.latest_source_timestamp or 0.0)
        state.source_timestamp_valid = self.latest_source_timestamp is not None
        state.run_id = self.run_id
        state.run_id_valid = True
        state.algorithm_profile = self.algorithm_profile
        state.state = int(self.machine.state)
        state.state_name = self.machine.state.name
        state.state_valid = True
        state.previous_state = int(self.machine.previous_state or 0)
        state.previous_state_name = (
            self.machine.previous_state.name
            if self.machine.previous_state is not None
            else "UNAVAILABLE"
        )
        state.previous_state_valid = self.machine.previous_state is not None
        state.transition_reason = self.machine.transition_reason
        state.transition_reason_valid = True
        state.state_elapsed_sec = self.machine.elapsed(now_sec)
        state.state_elapsed_valid = True
        state.active_fill_count = self.machine.active_fill_count
        state.active_fill_count_valid = True
        state.active_escape_fill_id = int(self.machine.active_escape_fill_id or 0)
        state.active_escape_fill_id_valid = self.machine.active_escape_fill_id is not None
        state.escape_center_x = float("nan")
        state.escape_center_y = float("nan")
        state.escape_exit_radius = float("nan")
        state.escape_geometry_valid = False
        state.radial_distance = float("nan")
        state.radial_distance_valid = False
        state.radial_progress = float("nan")
        state.radial_progress_valid = False
        state.escape_exit_hold_elapsed_sec = float("nan")
        state.escape_exit_hold_elapsed_valid = False
        state.escape_stalled = False
        state.escape_stalled_valid = False
        state.safe_direction_x = float("nan")
        state.safe_direction_y = float("nan")
        state.safe_direction_clearance_m = float("nan")
        state.safe_direction_valid = False
        state.safe_direction_revision = 0
        state.safe_direction_revision_valid = False
        state.recenter_target_x = float("nan")
        state.recenter_target_y = float("nan")
        state.recenter_target_valid = False
        state.recenter_distance = float("nan")
        state.recenter_distance_valid = False
        if self.escape_tracker is not None:
            geometry = self.escape_tracker.geometry
            state.escape_center_x = geometry.center_x
            state.escape_center_y = geometry.center_y
            state.escape_exit_radius = geometry.exit_radius
            state.escape_geometry_valid = True
            progress = self.escape_tracker.latest
            if progress is not None:
                state.radial_distance = progress.radial_distance
                state.radial_distance_valid = True
                state.radial_progress = progress.radial_progress
                state.radial_progress_valid = progress.radial_progress_valid
                state.escape_exit_hold_elapsed_sec = progress.exit_hold_elapsed_sec
                state.escape_exit_hold_elapsed_valid = (
                    progress.exit_hold_elapsed_valid
                )
                state.escape_stalled = progress.stalled
                state.escape_stalled_valid = progress.stalled_valid
        if (
            self.safe_direction is not None
            and self.machine.state in (State.ESCAPE_ASSIST, State.RECENTER)
        ):
            state.safe_direction_x = self.safe_direction.x
            state.safe_direction_y = self.safe_direction.y
            state.safe_direction_clearance_m = self.safe_direction.clearance_m
            state.safe_direction_valid = True
            state.safe_direction_revision = self.safe_direction_revision
            state.safe_direction_revision_valid = self.safe_direction_revision > 0
        if self.machine.state == State.RECENTER and self.bounds is not None:
            state.recenter_target_x = self.bounds.center_x
            state.recenter_target_y = self.bounds.center_y
            state.recenter_target_valid = True
            state.recenter_distance = self.recenter_distance
            state.recenter_distance_valid = math.isfinite(self.recenter_distance)
        weights = self.machine.weights
        state.sensor_weight = weights[0]
        state.gaussian_weight = weights[1]
        state.affine_weight = weights[2]
        state.weights_valid = True
        state.failsafe = self.machine.state == State.FAILSAFE
        state.failsafe_valid = True
        self.state_publisher.publish(state)
        command = (
            self.current_supervisor_command
            if self.machine.state == State.RECENTER
            else Twist()
        )
        values = np.array(
            [
                command.linear.x,
                command.linear.y,
                command.linear.z,
                command.angular.x,
                command.angular.y,
                command.angular.z,
            ],
            dtype=np.float64,
        )
        self.command_publisher.publish(command if np.all(np.isfinite(values)) else Twist())

    def destroy_node(self):
        self.command_publisher.publish(Twist())
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = SupervisorNode()
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


if __name__ == "__main__":
    main()
