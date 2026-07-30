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
    command_sweep_is_safe,
    DirectionConfig,
    DirectionSelection,
    EscapeGeometry,
    EscapeProgressConfig,
    EscapeProgressTracker,
    evaluate_direction,
    evaluate_direction_safety,
    FillAvoidance,
    OperatingBounds,
    Pose2D,
    PostRecoveryProgressConfig,
    PostRecoveryProgressTracker,
    preferred_escape_direction,
    recent_approach,
    recenter_command,
    RecenterControlConfig,
    RecenterHoldTracker,
    RecenterRoutePlanner,
    select_post_recovery_direction,
    select_recenter_direction,
    select_safe_direction,
    select_safe_recenter_target,
    source_continuity_evidence,
)
from ros_esc.supervisor_node.state_machine import (
    ROBUST_PROFILE,
    RotationScoreWindow,
    State,
    StateMachineConfig,
    SupervisorStateMachine,
    TransitionInputs,
)


ROBUST_FILL_CREATE = "ROBUST_FILL_CREATE"
ROBUST_FILL_REDESIGN_PREFIX = "ROBUST_FILL_REDESIGN:"
CONFIRMED_CONVERGENCE_VALUE_NAMES = (
    "metric",
    "r_mean_m2",
    "decay",
    "fill_center_x_m",
    "fill_center_y_m",
    "mean_old_x_m",
    "mean_old_y_m",
    "count_remaining",
)


def convergence_snapshot_from_confirmation(event, fallback=None):
    """Build the canonical eight-value fill snapshot from a confirmed event."""

    if (
        event.event_type != AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED
        or not event.source_timestamp_valid
        or not math.isfinite(float(event.source_timestamp))
    ):
        return None

    values = {
        str(name): float(value)
        for name, value in zip(event.value_names, event.values)
        if math.isfinite(float(value))
    }
    if all(name in values for name in CONFIRMED_CONVERGENCE_VALUE_NAMES):
        data = [values[name] for name in CONFIRMED_CONVERGENCE_VALUE_NAMES]
    elif (
        fallback is not None
        and len(fallback.data) == 8
        and all(math.isfinite(float(value)) for value in fallback.data)
        and math.isclose(
            float(fallback.timestamp),
            float(event.source_timestamp),
            rel_tol=0.0,
            abs_tol=1e-9,
        )
    ):
        data = [float(value) for value in fallback.data]
        if "count_remaining" in values:
            data[7] = values["count_remaining"]
    else:
        return None

    snapshot = StampedFloat64MultiArray()
    snapshot.header = "CONVERGED_FILL_READY"
    snapshot.timestamp = float(event.source_timestamp)
    snapshot.data = data
    return snapshot


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
                max_fill_clusters=self._nonnegative_int(
                    "max_fill_clusters"
                ),
                post_recovery_guidance_enabled=bool(
                    self.get_parameter(
                        "post_recovery_guidance_enabled"
                    ).value
                ),
                post_recovery_guidance_max_sec=self._float(
                    "post_recovery_guidance_max_sec"
                ),
                post_recovery_retry_limit=self._nonnegative_int(
                    "post_recovery_retry_limit"
                ),
                recoverable_navigation_enabled=bool(
                    self.get_parameter(
                        'recoverable_navigation_enabled'
                    ).value
                ),
                recovery_retry_limit=self._nonnegative_int(
                    'recovery_retry_limit'
                ),
            ),
        )
        self.recoverable_navigation_enabled = (
            self.machine.config.recoverable_navigation_enabled
        )
        self.adaptive_recenter_lookahead_enabled = bool(
            self.get_parameter(
                'adaptive_recenter_lookahead_enabled'
            ).value
        )
        self.post_recovery_source_led_handoff_enabled = bool(
            self.get_parameter(
                'post_recovery_source_led_handoff_enabled'
            ).value
        )
        self.post_recovery_source_continuity_enabled = bool(
            self.get_parameter(
                'post_recovery_source_continuity_enabled'
            ).value
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
        self.goal_score_window = RotationScoreWindow(
            self._positive_float("goal_score_rotation_period_sec"),
            self._positive_int("goal_score_required_rotations"),
        )
        self.goal_score_verification_margin_sec = (
            self.machine.config.verification_max_sec
            - self.goal_score_window.evidence_duration_sec
            - max(
                self.machine.config.goal_hold_sec,
                self.machine.config.undesired_score_hold_sec,
            )
        )
        self.goal_score_verification_timing_sufficient = (
            self.goal_score_verification_margin_sec > 0.0
        )
        if not self.goal_score_verification_timing_sufficient:
            self.get_logger().warning(
                'verification_max_sec leaves no scheduling margin after '
                'complete rotation evidence and score dwell; use only for an '
                'intentional safe-timeout scenario'
            )
        self.fill_avoidance_margin_m = self._nonnegative_float(
            'fill_avoidance_margin_m'
        )
        self.supervisor_command_stale_sec = self._nonnegative_float(
            'supervisor_command_stale_sec'
        )
        self.adaptive_recenter_minimum_lookahead_m = (
            self.recenter_config.max_linear_velocity_mps
            * self.supervisor_command_stale_sec
        )
        if self.adaptive_recenter_lookahead_enabled:
            if not self.recoverable_navigation_enabled:
                raise ValueError(
                    'adaptive recenter look-ahead requires recoverable '
                    'navigation'
                )
            if not self.bounded_mode:
                raise ValueError(
                    'adaptive recenter look-ahead requires bounded recenter'
                )
            if (
                self.adaptive_recenter_minimum_lookahead_m <= 0.0
                or self.adaptive_recenter_minimum_lookahead_m
                > self.direction_config.lookahead_m
            ):
                raise ValueError(
                    'adaptive recenter persistence distance must be positive '
                    'and no greater than direction look-ahead'
                )
        self.boundary_recovery_trigger_clearance_m = self._nonnegative_float(
            'boundary_recovery_trigger_clearance_m'
        )
        self.boundary_recovery_release_clearance_m = self._nonnegative_float(
            'boundary_recovery_release_clearance_m'
        )
        if (
            self.boundary_recovery_release_clearance_m
            <= self.boundary_recovery_trigger_clearance_m
        ):
            raise ValueError(
                'boundary recovery release clearance must exceed its trigger'
            )
        self.recenter_target_fill_clearance_m = self._nonnegative_float(
            'recenter_target_fill_clearance_m'
        )
        self.post_recovery_affine_weight = self._nonnegative_float(
            'post_recovery_affine_weight'
        )
        if self.post_recovery_affine_weight > 1.0:
            raise ValueError('post-recovery affine weight must be at most one')
        self.post_recovery_affine_taper_distance_m = self._positive_float(
            'post_recovery_affine_taper_distance_m'
        )
        self.post_recovery_progress_enabled = bool(
            self.get_parameter('post_recovery_progress_enabled').value
        )
        self.post_recovery_guidance_min_progress_m = self._positive_float(
            'post_recovery_guidance_min_progress_m'
        )
        self.post_recovery_progress_config = PostRecoveryProgressConfig(
            window_sec=self._positive_float(
                'post_recovery_liveness_window_sec'
            ),
            minimum_path_length_m=self._positive_float(
                'post_recovery_liveness_min_path_length_m'
            ),
            maximum_displacement_m=self._nonnegative_float(
                'post_recovery_liveness_max_displacement_m'
            ),
        )
        self.post_recovery_direction_refresh_limit = self._nonnegative_int(
            'post_recovery_direction_refresh_limit'
        )
        self.post_recovery_source_continuity_min_displacement_m = (
            self._positive_float(
                'post_recovery_source_continuity_min_displacement_m'
            )
        )
        self.post_recovery_source_reversal_dot_threshold = self._float(
            'post_recovery_source_reversal_dot_threshold'
        )
        if (
            not math.isfinite(
                self.post_recovery_source_reversal_dot_threshold
            )
            or self.post_recovery_source_reversal_dot_threshold < -1.0
            or self.post_recovery_source_reversal_dot_threshold >= 0.0
        ):
            raise ValueError(
                'post-recovery source reversal dot threshold must be in '
                '[-1, 0)'
            )
        self.post_recovery_source_bypass_clearance_m = (
            self._nonnegative_float(
                'post_recovery_source_bypass_clearance_m'
            )
        )
        if self.post_recovery_progress_enabled:
            if not self.machine.config.post_recovery_guidance_enabled:
                raise ValueError(
                    'post-recovery progress requires post-recovery guidance'
                )
            if not self.recoverable_navigation_enabled:
                raise ValueError(
                    'post-recovery progress requires recoverable navigation'
                )
            if self.post_recovery_direction_refresh_limit <= 0:
                raise ValueError(
                    'post-recovery progress requires a positive direction '
                    'refresh limit'
                )
        if self.post_recovery_source_led_handoff_enabled:
            if not self.recoverable_navigation_enabled:
                raise ValueError(
                    'post-recovery source-led handoff requires recoverable '
                    'navigation'
                )
            if not self.post_recovery_progress_enabled:
                raise ValueError(
                    'post-recovery source-led handoff requires post-recovery '
                    'progress'
                )
        if self.post_recovery_source_continuity_enabled:
            if not self.post_recovery_source_led_handoff_enabled:
                raise ValueError(
                    'post-recovery source continuity requires source-led '
                    'handoff'
                )
            if self.post_recovery_source_bypass_clearance_m <= 0.0:
                raise ValueError(
                    'post-recovery source bypass clearance must be positive'
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
        self.pending_convergence_confirmation_receipt_sec = None
        self.pending_fill_result = None
        self.active_fill_records = {}
        self.escape_tracker = None
        self.escape_pose_sequence = 0
        self.safe_direction = None
        self.safe_direction_revision = 0
        self.recenter_hold_tracker = None
        self.recenter_route_planner = RecenterRoutePlanner()
        self.recenter_target = None
        self.recenter_distance = float("nan")
        self.recenter_complete = False
        self.recenter_started_distance = float('nan')
        self.recenter_best_distance = float('nan')
        self.recenter_recovery_allowed = False
        self.recenter_recovery_requested = False
        self.boundary_recovery_active = False
        self.post_recovery_direction_recovery_attempted = False
        self.post_recovery_progress_tracker = None
        self.post_recovery_pose_sequence = 0
        self.post_recovery_direction_refresh_count = 0
        self.post_recovery_recenter_attempted = False
        self.post_recovery_guidance_release_reported = False
        self.post_recovery_source_led_active = False
        self.post_recovery_source_continuity = None
        self.post_recovery_source_bypass_active = False
        self.recenter_route_unavailable_reported = False
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
            'supervisor_command_stale_sec': 0.50,
            "startup_timeout_sec": 5.0,
            "convergence_hold_sec": 2.0,
            "goal_score_threshold": 0.95,
            "goal_score_rotation_period_sec": 3.0,
            "goal_score_required_rotations": 2,
            "goal_hold_sec": 3.0,
            "undesired_score_hold_sec": 3.0,
            "verification_max_sec": 12.0,
            "fill_design_timeout_sec": 5.0,
            "escape_max_sec": 20.0,
            "escape_exit_hold_sec": 1.0,
            "stall_window_sec": 3.0,
            "minimum_radial_progress_m": 0.05,
            "approach_history_window_sec": 3.0,
            "recenter_after_escape": True,
            "recenter_max_sec": 30.0,
            "max_fill_clusters": 0,
            "post_recovery_guidance_enabled": False,
            "post_recovery_guidance_max_sec": 0.0,
            "post_recovery_retry_limit": 0,
            'recoverable_navigation_enabled': False,
            'recovery_retry_limit': 0,
            'boundary_recovery_trigger_clearance_m': 0.025,
            'boundary_recovery_release_clearance_m': 0.10,
            'recenter_target_fill_clearance_m': 0.05,
            'post_recovery_affine_weight': 1.0,
            'post_recovery_affine_taper_distance_m': 0.50,
            'post_recovery_progress_enabled': False,
            'post_recovery_guidance_min_progress_m': 0.60,
            'post_recovery_liveness_window_sec': 12.0,
            'post_recovery_liveness_min_path_length_m': 0.60,
            'post_recovery_liveness_max_displacement_m': 0.20,
            'post_recovery_direction_refresh_limit': 0,
            'adaptive_recenter_lookahead_enabled': False,
            'post_recovery_source_led_handoff_enabled': False,
            'post_recovery_source_continuity_enabled': False,
            'post_recovery_source_continuity_min_displacement_m': 0.05,
            'post_recovery_source_reversal_dot_threshold': -0.90,
            'post_recovery_source_bypass_clearance_m': 0.10,
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

    def _positive_int(self, name):
        value = int(self.get_parameter(name).value)
        if value <= 0:
            raise ValueError(f"{name} must be positive")
        return value

    def _nonnegative_int(self, name):
        value = int(self.get_parameter(name).value)
        if value < 0:
            raise ValueError(f"{name} must be nonnegative")
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
        receipt_sec = self._now_sec()
        if (
            self.machine.state == State.VERIFY_EXTREMUM
            and self.latest_source_score_valid
        ):
            self.goal_score_window.update(receipt_sec, float(np.max(scores)))
        else:
            self.goal_score_window.reset()
        self.latest_source_score = self.goal_score_window.score
        self.latest_source_timestamp = (
            float(msg.source_timestamp)
            if msg.source_timestamp_valid and math.isfinite(msg.source_timestamp)
            else None
        )
        self.latest_source_receipt_sec = receipt_sec

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
        if msg.event_type == AlgorithmEvent.EVENT_CONVERGENCE_CONFIRMED:
            snapshot = convergence_snapshot_from_confirmation(
                msg, fallback=self.latest_convergence
            )
            if snapshot is not None:
                receipt_sec = self._now_sec()
                self.latest_convergence = snapshot
                self.latest_convergence_receipt_sec = receipt_sec
                self.pending_convergence_confirmation_receipt_sec = receipt_sec
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
                (
                    'retryable_rejected'
                    if (
                        self.recoverable_navigation_enabled
                        and msg.event_type
                        == AlgorithmEvent.EVENT_FILL_REJECTED
                        and int(msg.reason_code) == 30
                    )
                    else 'rejected'
                ),
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
                    inputs = self._transition_inputs(now_sec)
                    transition = self.machine.step(now_sec, inputs)
                    if inputs.convergence_confirmed:
                        self.pending_convergence_confirmation_receipt_sec = None
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
        self.recenter_recovery_requested = False
        if (
            self.bounds is not None
            and self.latest_pose_valid
            and self.latest_pose is not None
        ):
            position = self.latest_pose.position
            if self.recoverable_navigation_enabled:
                if not self.bounds.contains_physical(position):
                    return 'pose outside physical room bounds'
                inset_clearance = self.bounds.clearance(position)
                if self.machine.state != State.RECENTER:
                    if self.boundary_recovery_active:
                        self.boundary_recovery_active = bool(
                            inset_clearance
                            < self.boundary_recovery_release_clearance_m
                        )
                    elif (
                        inset_clearance
                        <= self.boundary_recovery_trigger_clearance_m
                    ):
                        self.boundary_recovery_active = True
                    if self.boundary_recovery_active:
                        self.recenter_recovery_requested = True
            elif not self.bounds.contains(position):
                return 'pose outside wall-margin-inset operating bounds'

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
        if (
            self.machine.state == State.SEARCH
            and self.machine.post_recovery_guidance_active
        ):
            if self.post_recovery_progress_enabled:
                return self._update_post_recovery_guidance(now_sec)
            failure = self._ensure_post_recovery_direction()
            if failure is None:
                return None
            if not self.recoverable_navigation_enabled:
                return failure
            if not self.post_recovery_direction_recovery_attempted:
                self.post_recovery_direction_recovery_attempted = True
                self.recenter_recovery_requested = True
                return None
            self.machine.deactivate_post_recovery_guidance()
            self.safe_direction = None
            return None
        if self.post_recovery_progress_tracker is not None:
            self._clear_post_recovery_epoch()
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
        convergence_confirmed = self._fresh(
            self.pending_convergence_confirmation_receipt_sec,
            self._float("stale_sensor_sec"),
            now_sec,
        )
        fill_result = self.pending_fill_result or (None, None, None, None)
        progress = (
            self.escape_tracker.latest
            if self.escape_tracker is not None
            else None
        )
        return TransitionInputs(
            convergence=False,
            convergence_confirmed=convergence_confirmed,
            source_score=self.latest_source_score,
            source_score_observed=self.latest_source_receipt_sec is not None,
            source_score_valid=self.latest_source_score_valid,
            source_score_ready=self.goal_score_window.ready,
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
            recenter_recovery_requested=bool(
                self.recoverable_navigation_enabled
                and self.recenter_recovery_requested
            ),
            recenter_recovery_allowed=bool(
                self.recoverable_navigation_enabled
                and self.recenter_recovery_allowed
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
        if transition.current == State.VERIFY_EXTREMUM:
            self.goal_score_window.reset()
            self.latest_source_score = None
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
        if (
            transition.current == State.RECENTER
            and transition.previous != State.RECENTER
        ):
            self.current_supervisor_command = Twist()
            self._clear_post_recovery_epoch(
                preserve_source_continuity=(
                    self.post_recovery_source_bypass_active
                ),
            )
            self.safe_direction = None
            self.recenter_route_unavailable_reported = False
            self.recenter_route_planner.reset()
            fills = self._active_fill_avoidances()
            if self.recoverable_navigation_enabled:
                self.recenter_target = select_safe_recenter_target(
                    self.latest_pose.position,
                    self.bounds.center,
                    fills,
                    self.bounds,
                    self.recenter_target_fill_clearance_m,
                )
            else:
                self.recenter_target = np.array(
                    self.bounds.center, dtype=np.float64, copy=True
                )
            if self.recenter_target is None:
                self._force_failsafe(
                    now_sec, 'no finite safe recenter target'
                )
                return
            self.recenter_hold_tracker = RecenterHoldTracker(
                self.recenter_config
            )
            self.recenter_distance = float(
                np.linalg.norm(
                    self.recenter_target - self.latest_pose.position
                )
            )
            self.recenter_started_distance = self.recenter_distance
            self.recenter_best_distance = self.recenter_distance
            self.recenter_recovery_allowed = False
            self.recenter_complete = False
            self._publish_event(
                AlgorithmEvent.EVENT_RECENTER_STARTED,
                now_sec,
                'bounded center-return controller started',
                [
                    'target_x_m',
                    'target_y_m',
                    'active_fill_count',
                    'safe_proxy_target',
                ],
                [
                    float(self.recenter_target[0]),
                    float(self.recenter_target[1]),
                    float(len(self.active_fill_records)),
                    (
                        1.0
                        if not np.allclose(
                            self.recenter_target,
                            self.bounds.center,
                            rtol=0.0,
                            atol=1e-12,
                        )
                        else 0.0
                    ),
                ],
            )
        if transition.previous == State.RECENTER and transition.current == State.SEARCH:
            self._publish_event(
                AlgorithmEvent.EVENT_RECENTER_COMPLETE,
                now_sec,
                "recenter tolerance dwell satisfied",
                ["target_x_m", "target_y_m", "recenter_distance_m"],
                [
                    float(self.recenter_target[0]),
                    float(self.recenter_target[1]),
                    self.recenter_distance,
                ],
            )
            self.boundary_recovery_active = False
        if "timeout" in transition.reason:
            self._publish_event(
                AlgorithmEvent.EVENT_TIMEOUT, now_sec, transition.reason
            )
        if transition.current == State.FAILSAFE:
            self.current_supervisor_command = Twist()
            self._publish_failsafe_event(now_sec, transition.reason)
            self._reset_escape_attempt()
        if transition.current == State.SEARCH:
            previous_revision = self.safe_direction_revision
            self._reset_escape_attempt(
                preserve_post_recovery_recovery=(
                    transition.previous == State.RECENTER
                )
            )
            if self.machine.post_recovery_guidance_active:
                self.safe_direction_revision = previous_revision
                if self.post_recovery_progress_enabled:
                    failure = self._start_post_recovery_epoch(
                        now_sec,
                        source_led_handoff=(
                            transition.previous == State.RECENTER
                        ),
                    )
                    if failure is not None:
                        self._recover_post_recovery_direction_failure(
                            now_sec, failure
                        )
                elif not self.recoverable_navigation_enabled:
                    failure = self._ensure_post_recovery_direction()
                    if failure is not None:
                        self._force_failsafe(now_sec, failure)
                        return

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
        self._clear_post_recovery_epoch(preserve_recenter_attempt=False)
        self.post_recovery_direction_recovery_attempted = False
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
            target = (
                self.recenter_target
                if self.recenter_target is not None
                else self.bounds.center
            )
            preferred = target - position
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
        if recenter:
            if self.recoverable_navigation_enabled:
                selected = self.recenter_route_planner.select(
                    position,
                    target,
                    fills,
                    self.direction_config,
                    self.bounds,
                    minimum_lookahead_m=(
                        self.adaptive_recenter_minimum_lookahead_m
                        if self.adaptive_recenter_lookahead_enabled
                        else None
                    ),
                )
            else:
                selected = select_recenter_direction(
                    position,
                    target,
                    fills,
                    self.direction_config,
                    self.bounds,
                )
            if selected is None:
                return 'no safe recenter direction candidate'
            self.safe_direction = selected
            self.safe_direction_revision += 1
            self.recenter_route_unavailable_reported = False
            return None

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

    def _ensure_post_recovery_direction(self):
        if self.latest_pose is None or not self.latest_pose_valid:
            return "post-recovery guidance requires a valid pose"
        record = self._record_for_fill(self.machine.active_escape_fill_id)
        if record is None:
            return "post-recovery guidance fill has no active finite geometry"
        position = self.latest_pose.position
        preferred = position - np.asarray(record["center"], dtype=np.float64)
        if self.post_recovery_source_bypass_active:
            if self.post_recovery_source_continuity is None:
                return (
                    'post-recovery source-continuity bypass has no '
                    'measured direction'
                )
            preferred = self.post_recovery_source_continuity.direction
        if float(np.linalg.norm(preferred)) <= 1e-12:
            return "post-recovery guidance direction is undefined at fill center"
        fills = self._active_fill_avoidances()
        if self.safe_direction is not None:
            if self.recoverable_navigation_enabled:
                safe, clearance = evaluate_direction_safety(
                    position,
                    self.safe_direction.direction,
                    fills,
                    self.direction_config,
                    self.bounds,
                )
            else:
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
        if self.post_recovery_source_bypass_active:
            selected = select_safe_direction(
                position,
                preferred,
                fills,
                self.direction_config,
                self.bounds,
            )
        elif self.recoverable_navigation_enabled:
            selected = select_post_recovery_direction(
                position,
                preferred,
                fills,
                self.direction_config,
                self.bounds,
            )
        else:
            selected = select_safe_direction(
                position,
                preferred,
                fills,
                self.direction_config,
                self.bounds,
            )
        if selected is None:
            return 'no safe post-recovery direction candidate'
        self.safe_direction = selected
        self.safe_direction_revision += 1
        return None

    def _start_post_recovery_epoch(
        self,
        now_sec,
        source_led_handoff=False,
    ):
        """Anchor progress and recompute direction at a guided SEARCH boundary."""
        if self.latest_pose is None or not self.latest_pose_valid:
            return 'post-recovery epoch requires a valid pose'
        record = self._record_for_fill(self.machine.active_escape_fill_id)
        if record is None:
            return 'post-recovery epoch fill has no active finite geometry'
        self.post_recovery_progress_tracker = PostRecoveryProgressTracker(
            self.latest_pose,
            record['center'],
            self.post_recovery_progress_config,
        )
        self.post_recovery_pose_sequence = self.latest_pose_sequence
        self.post_recovery_direction_refresh_count = 0
        self.post_recovery_guidance_release_reported = False
        self.safe_direction = None
        self.post_recovery_source_led_active = bool(
            source_led_handoff
            and self.post_recovery_source_led_handoff_enabled
            and not self.post_recovery_recenter_attempted
        )
        if self.post_recovery_source_led_active:
            self.current_supervisor_command = Twist()
            self.post_recovery_source_continuity = None
            self.post_recovery_source_bypass_active = False
        if not self.post_recovery_source_led_active:
            failure = self._ensure_post_recovery_direction()
            if failure is not None:
                return failure
        progress = self.post_recovery_progress_tracker.latest
        self._publish_event(
            AlgorithmEvent.EVENT_CONFIGURATION,
            now_sec,
            (
                'post-recovery source-led handoff started'
                if self.post_recovery_source_led_active
                else 'post-recovery guidance epoch started'
            ),
            [
                'anchor_x_m',
                'anchor_y_m',
                'fill_center_x_m',
                'fill_center_y_m',
                'anchor_fill_distance_m',
                'guidance_min_progress_m',
                'affine_taper_progress_m',
                'direction_revision',
                'recenter_attempted',
            ],
            [
                self.latest_pose.x,
                self.latest_pose.y,
                float(record['center'][0]),
                float(record['center'][1]),
                progress.fill_distance_m,
                self.post_recovery_guidance_min_progress_m,
                self.post_recovery_affine_taper_distance_m,
                float(self.safe_direction_revision),
                1.0 if self.post_recovery_recenter_attempted else 0.0,
            ],
        )
        return None

    def _update_post_recovery_guidance(self, now_sec):
        """Update measured progress, recover loops, and publish a safe command."""
        guidance_started_sec = (
            self.machine.post_recovery_guidance_started_sec
        )
        if (
            guidance_started_sec is not None
            and now_sec - guidance_started_sec
            >= self.machine.config.post_recovery_guidance_max_sec
        ):
            self._release_post_recovery_guidance(
                now_sec,
                'post-recovery guidance maximum duration elapsed',
            )
            return None
        if self.post_recovery_progress_tracker is None:
            failure = self._start_post_recovery_epoch(now_sec)
            if failure is not None:
                return self._recover_post_recovery_direction_failure(
                    now_sec, failure
                )
        if (
            self.latest_pose is not None
            and self.latest_pose_valid
            and self.latest_pose_sequence
            != self.post_recovery_pose_sequence
        ):
            self.post_recovery_progress_tracker.update(self.latest_pose)
            self.post_recovery_pose_sequence = self.latest_pose_sequence

        progress = self.post_recovery_progress_tracker.latest
        release_progress = (
            self.post_recovery_guidance_min_progress_m
            + self.post_recovery_affine_taper_distance_m
        )
        if self.post_recovery_source_led_active:
            self.current_supervisor_command = Twist()
            self.safe_direction = None
            if progress.outward_progress_m >= release_progress:
                self._release_post_recovery_guidance(
                    now_sec,
                    'post-recovery source-led handoff completed',
                )
                return None
            if not progress.window_valid:
                return None
            if (
                progress.net_displacement_m
                > self.post_recovery_progress_config.maximum_displacement_m
            ):
                self._release_post_recovery_guidance(
                    now_sec,
                    'post-recovery source-led handoff completed',
                )
                return None
            self.post_recovery_source_led_active = False
            self._arm_source_continuity_bypass(now_sec)
            self._publish_post_recovery_liveness_event(
                now_sec,
                'post-recovery source-led handoff stalled; '
                'fallback guidance armed',
                progress,
            )
            self.post_recovery_progress_tracker.reset_liveness_window()
            progress = self.post_recovery_progress_tracker.latest

        if self.post_recovery_source_bypass_active:
            clearance_target = self._source_bypass_clearance_target()
            if clearance_target is None:
                return self._recover_post_recovery_direction_failure(
                    now_sec,
                    'post-recovery source-continuity bypass has no active '
                    'fill clearance',
                )
            if progress.fill_distance_m >= clearance_target:
                self._release_post_recovery_guidance(
                    now_sec,
                    'post-recovery source-continuity bypass completed',
                )
                return None

        if progress.outward_progress_m >= release_progress:
            self._release_post_recovery_guidance(
                now_sec, 'post-recovery outward progress completed'
            )
            return None

        if progress.stalled:
            if self.post_recovery_recenter_attempted:
                self._publish_post_recovery_liveness_event(
                    now_sec,
                    'post-recovery liveness released guidance to ordinary search',
                    progress,
                )
                self._release_post_recovery_guidance(
                    now_sec,
                    'post-recovery liveness recovery exhausted; '
                    'continue ordinary search',
                    publish_event=False,
                )
                return None
            if (
                self.post_recovery_direction_refresh_count
                < self.post_recovery_direction_refresh_limit
            ):
                self.post_recovery_direction_refresh_count += 1
                self.safe_direction = None
                failure = self._ensure_post_recovery_direction()
                if failure is not None:
                    return self._recover_post_recovery_direction_failure(
                        now_sec, failure
                    )
                self._publish_post_recovery_liveness_event(
                    now_sec,
                    'post-recovery liveness direction refreshed',
                    progress,
                )
                self.post_recovery_progress_tracker.reset_liveness_window()
                progress = self.post_recovery_progress_tracker.latest
            elif not self.post_recovery_recenter_attempted:
                self.post_recovery_recenter_attempted = True
                self.recenter_recovery_requested = True
                self._publish_post_recovery_liveness_event(
                    now_sec,
                    'post-recovery liveness requested recoverable recenter',
                    progress,
                )
                self.post_recovery_progress_tracker.reset_liveness_window()
                return None

        failure = self._ensure_post_recovery_direction()
        if failure is not None:
            return self._recover_post_recovery_direction_failure(
                now_sec, failure
            )
        if (
            progress.outward_progress_m
            >= self.post_recovery_guidance_min_progress_m
        ):
            self.current_supervisor_command = Twist()
            return None

        remaining = max(
            0.0,
            self.post_recovery_guidance_min_progress_m
            - progress.outward_progress_m,
        )
        linear, angular = recenter_command(
            self.safe_direction.direction,
            self.latest_pose.yaw,
            remaining + self.recenter_config.tolerance_m,
            self.recenter_config,
        )
        if not command_sweep_is_safe(
            self.latest_pose.position,
            self.latest_pose.yaw,
            linear,
            self.supervisor_command_stale_sec,
            self._active_fill_avoidances(),
            self.bounds,
            allow_inward_from_margin=True,
            boundary_trigger_clearance_m=(
                self.boundary_recovery_trigger_clearance_m
            ),
        ):
            linear = 0.0
        command = Twist()
        command.linear.x = linear
        command.angular.z = angular
        self.current_supervisor_command = command
        return None

    def _arm_source_continuity_bypass(self, now_sec):
        """Retain source motion only when radial fallback would reverse it."""
        if (
            not self.post_recovery_source_continuity_enabled
            or self.post_recovery_progress_tracker is None
            or self.latest_pose is None
            or not self.latest_pose_valid
        ):
            return
        tracker = self.post_recovery_progress_tracker
        try:
            evidence = source_continuity_evidence(
                tracker.anchor_pose.position,
                self.latest_pose.position,
                tracker.fill_center,
                self.post_recovery_source_continuity_min_displacement_m,
                self.post_recovery_source_reversal_dot_threshold,
            )
        except ValueError:
            return
        if evidence is None:
            return
        clearance_target = self._source_bypass_clearance_target()
        if clearance_target is None:
            return
        self.post_recovery_source_continuity = evidence
        self.post_recovery_source_bypass_active = True
        self._publish_event(
            AlgorithmEvent.EVENT_CONFIGURATION,
            now_sec,
            'post-recovery source-continuity bypass armed',
            [
                'source_direction_x',
                'source_direction_y',
                'source_displacement_m',
                'source_radial_alignment',
                'reversal_dot_threshold',
                'bypass_fill_clearance_target_m',
            ],
            [
                evidence.direction_x,
                evidence.direction_y,
                evidence.displacement_m,
                evidence.radial_alignment,
                self.post_recovery_source_reversal_dot_threshold,
                float(clearance_target),
            ],
        )

    def _source_bypass_clearance_target(self):
        """Return the active avoidance radius plus the fixed bypass margin."""
        record = self._record_for_fill(self.machine.active_escape_fill_id)
        if record is None:
            return None
        support_radius = float(record['support_radius'])
        if not math.isfinite(support_radius) or support_radius <= 0.0:
            return None
        return (
            support_radius
            + self.fill_avoidance_margin_m
            + self.post_recovery_source_bypass_clearance_m
        )

    def _recover_post_recovery_direction_failure(self, now_sec, failure):
        if (
            not self.post_recovery_direction_recovery_attempted
            and not self.post_recovery_recenter_attempted
        ):
            self.post_recovery_direction_recovery_attempted = True
            self.post_recovery_recenter_attempted = True
            self.recenter_recovery_requested = True
            self._publish_event(
                AlgorithmEvent.EVENT_CONFIGURATION,
                now_sec,
                'post-recovery direction unavailable; recover by recenter',
                ['direction_revision'],
                [float(self.safe_direction_revision)],
            )
            return None
        self._release_post_recovery_guidance(
            now_sec,
            f'{failure}; continue ordinary search',
        )
        return None

    def _publish_post_recovery_liveness_event(
        self, now_sec, detail, progress
    ):
        names, values = self._post_recovery_report(progress)
        self._publish_event(
            AlgorithmEvent.EVENT_CONFIGURATION,
            now_sec,
            detail,
            names,
            values,
        )

    def _post_recovery_report(self, progress):
        window_valid = bool(progress.window_valid)
        return (
            [
                'path_length_m',
                'net_displacement_m',
                'outward_progress_m',
                'window_path_length_m',
                'window_displacement_m',
                'window_valid',
                'window_sec',
                'minimum_window_path_m',
                'maximum_window_displacement_m',
                'direction_revision',
                'direction_refresh_count',
                'recenter_attempted',
                'post_recovery_retry_count',
                'recovery_retry_count',
            ],
            [
                progress.path_length_m,
                progress.net_displacement_m,
                progress.outward_progress_m,
                (
                    progress.window_path_length_m
                    if window_valid
                    else 0.0
                ),
                (
                    progress.window_displacement_m
                    if window_valid
                    else 0.0
                ),
                1.0 if window_valid else 0.0,
                self.post_recovery_progress_config.window_sec,
                self.post_recovery_progress_config.minimum_path_length_m,
                self.post_recovery_progress_config.maximum_displacement_m,
                float(self.safe_direction_revision),
                float(self.post_recovery_direction_refresh_count),
                1.0 if self.post_recovery_recenter_attempted else 0.0,
                float(self.machine.post_recovery_retry_count),
                float(self.machine.recovery_retry_count),
            ],
        )

    def _release_post_recovery_guidance(
        self, now_sec, detail, publish_event=True
    ):
        tracker = self.post_recovery_progress_tracker
        if (
            publish_event
            and not self.post_recovery_guidance_release_reported
            and tracker is not None
        ):
            self.post_recovery_guidance_release_reported = True
            progress = tracker.latest
            names, values = self._post_recovery_report(progress)
            self._publish_event(
                AlgorithmEvent.EVENT_CONFIGURATION,
                now_sec,
                detail,
                names,
                values,
            )
        self.machine.deactivate_post_recovery_guidance()
        self.current_supervisor_command = Twist()
        self.safe_direction = None
        self._clear_post_recovery_epoch(
            preserve_source_continuity=False,
        )

    def _clear_post_recovery_epoch(
        self,
        preserve_recenter_attempt=True,
        preserve_source_continuity=False,
    ):
        self.post_recovery_progress_tracker = None
        self.post_recovery_pose_sequence = 0
        self.post_recovery_direction_refresh_count = 0
        self.post_recovery_guidance_release_reported = False
        self.post_recovery_source_led_active = False
        if not preserve_source_continuity:
            self.post_recovery_source_continuity = None
            self.post_recovery_source_bypass_active = False
        if not preserve_recenter_attempt:
            self.post_recovery_recenter_attempted = False

    def _update_recenter(self, now_sec):
        if self.bounds is None:
            return "RECENTER requires configured bounded indoor mode"
        if self.latest_pose is None or not self.latest_pose_valid:
            return "recenter requires a valid pose"
        target = (
            self.recenter_target
            if self.recenter_target is not None
            else self.bounds.center
        )
        self.recenter_distance = float(
            np.linalg.norm(target - self.latest_pose.position)
        )
        if not math.isfinite(self.recenter_best_distance):
            self.recenter_best_distance = self.recenter_distance
        else:
            self.recenter_best_distance = min(
                self.recenter_best_distance, self.recenter_distance
            )
        self.recenter_recovery_allowed = bool(
            self.bounds.contains_physical(self.latest_pose.position)
            and self.recenter_target is not None
            and np.all(np.isfinite(self.recenter_target))
            and math.isfinite(self.recenter_distance)
            and math.isfinite(self.recenter_started_distance)
            and math.isfinite(self.recenter_best_distance)
        )
        if self.recenter_hold_tracker is None:
            self.recenter_hold_tracker = RecenterHoldTracker(
                self.recenter_config
            )
        fills = self._active_fill_avoidances()
        outside_fills = all(
            float(
                np.linalg.norm(
                    self.latest_pose.position - fill.center
                )
            )
            > fill.radius
            for fill in fills
        )
        completion_distance = (
            self.recenter_distance
            if outside_fills
            else self.recenter_config.tolerance_m + 1.0
        )
        self.recenter_complete = self.recenter_hold_tracker.update(
            now_sec, completion_distance
        )
        if (
            outside_fills
            and self.recenter_distance <= self.recenter_config.tolerance_m
        ):
            self.current_supervisor_command = Twist()
            self.safe_direction = None
            return None
        failure = self._ensure_safe_direction(recenter=True)
        if failure is not None:
            if (
                self.adaptive_recenter_lookahead_enabled
                and self.recenter_recovery_allowed
                and failure == 'no safe recenter direction candidate'
            ):
                preferred = target - self.latest_pose.position
                _, angular = recenter_command(
                    preferred,
                    self.latest_pose.yaw,
                    completion_distance,
                    self.recenter_config,
                )
                self.safe_direction = None
                command = Twist()
                command.angular.z = angular
                self.current_supervisor_command = command
                if not self.recenter_route_unavailable_reported:
                    self.recenter_route_unavailable_reported = True
                    self._publish_event(
                        AlgorithmEvent.EVENT_CONFIGURATION,
                        now_sec,
                        'measured escape: recenter route temporarily '
                        'unavailable; bounded recovery continues',
                        [
                            'pose_x_m',
                            'pose_y_m',
                            'target_x_m',
                            'target_y_m',
                            'configured_lookahead_m',
                            'minimum_lookahead_m',
                            'recovery_retry_count',
                        ],
                        [
                            self.latest_pose.x,
                            self.latest_pose.y,
                            float(target[0]),
                            float(target[1]),
                            self.direction_config.lookahead_m,
                            self.adaptive_recenter_minimum_lookahead_m,
                            float(self.machine.recovery_retry_count),
                        ],
                    )
                return None
            return failure
        linear, angular = recenter_command(
            self.safe_direction.direction,
            self.latest_pose.yaw,
            completion_distance,
            self.recenter_config,
        )
        if not command_sweep_is_safe(
            self.latest_pose.position,
            self.latest_pose.yaw,
            linear,
            self.supervisor_command_stale_sec,
            fills,
            self.bounds,
            allow_inward_from_margin=self.recoverable_navigation_enabled,
            boundary_trigger_clearance_m=(
                self.boundary_recovery_trigger_clearance_m
                if self.recoverable_navigation_enabled
                else None
            ),
        ):
            linear = 0.0
        command = Twist()
        command.linear.x = linear
        command.angular.z = angular
        self.current_supervisor_command = command
        return None

    def _reset_escape_attempt(self, preserve_post_recovery_recovery=False):
        self.escape_tracker = None
        self.escape_pose_sequence = 0
        self.safe_direction = None
        self.safe_direction_revision = 0
        self.recenter_hold_tracker = None
        self.recenter_route_planner.reset()
        self.recenter_target = None
        self.recenter_distance = float("nan")
        self.recenter_complete = False
        self.recenter_started_distance = float('nan')
        self.recenter_best_distance = float('nan')
        self.recenter_recovery_allowed = False
        self.recenter_recovery_requested = False
        self.recenter_route_unavailable_reported = False
        if not preserve_post_recovery_recovery:
            self.post_recovery_direction_recovery_attempted = False
        self._clear_post_recovery_epoch(
            preserve_recenter_attempt=preserve_post_recovery_recovery,
            preserve_source_continuity=preserve_post_recovery_recovery,
        )
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
            "goal_score_rotation_period_sec",
            "goal_score_required_rotations",
            'goal_score_evidence_duration_sec',
            'goal_score_verification_margin_sec',
            'goal_score_verification_timing_sufficient',
            "escape_exit_hold_sec",
            "stall_window_sec",
            "minimum_radial_progress_m",
            "approach_history_window_sec",
            "direction_lookahead_m",
            'adaptive_recenter_lookahead_enabled',
            'adaptive_recenter_minimum_lookahead_m',
            "direction_candidate_step_rad",
            "fill_avoidance_margin_m",
            "recenter_tolerance_m",
            "recenter_hold_sec",
            "recenter_linear_gain",
            "recenter_angular_gain",
            "recenter_max_linear_velocity_mps",
            "recenter_max_angular_velocity_rps",
            "recenter_rotate_in_place_angle_rad",
            'supervisor_command_stale_sec',
            "max_fill_clusters",
            "post_recovery_guidance_enabled",
            "post_recovery_guidance_max_sec",
            "post_recovery_retry_limit",
            'recoverable_navigation_enabled',
            'recovery_retry_limit',
            'boundary_recovery_trigger_clearance_m',
            'boundary_recovery_release_clearance_m',
            'recenter_target_fill_clearance_m',
            'post_recovery_affine_weight',
            'post_recovery_affine_taper_distance_m',
            'post_recovery_progress_enabled',
            'post_recovery_guidance_min_progress_m',
            'post_recovery_liveness_window_sec',
            'post_recovery_liveness_min_path_length_m',
            'post_recovery_liveness_max_displacement_m',
            'post_recovery_direction_refresh_limit',
            'post_recovery_source_led_handoff_enabled',
            'post_recovery_source_continuity_enabled',
            'post_recovery_source_continuity_min_displacement_m',
            'post_recovery_source_reversal_dot_threshold',
            'post_recovery_source_bypass_clearance_m',
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
            self.goal_score_window.rotation_period_sec,
            float(self.goal_score_window.required_rotations),
            self.goal_score_window.evidence_duration_sec,
            self.goal_score_verification_margin_sec,
            (
                1.0
                if self.goal_score_verification_timing_sufficient
                else 0.0
            ),
            self.escape_progress_config.escape_exit_hold_sec,
            self.escape_progress_config.stall_window_sec,
            self.escape_progress_config.minimum_radial_progress_m,
            self.approach_history_window_sec,
            self.direction_config.lookahead_m,
            (
                1.0
                if self.adaptive_recenter_lookahead_enabled
                else 0.0
            ),
            self.adaptive_recenter_minimum_lookahead_m,
            self.direction_config.candidate_step_rad,
            self.fill_avoidance_margin_m,
            self.recenter_config.tolerance_m,
            self.recenter_config.hold_sec,
            self.recenter_config.linear_gain,
            self.recenter_config.angular_gain,
            self.recenter_config.max_linear_velocity_mps,
            self.recenter_config.max_angular_velocity_rps,
            self.recenter_config.rotate_in_place_angle_rad,
            self.supervisor_command_stale_sec,
            float(self.machine.config.max_fill_clusters),
            (
                1.0
                if self.machine.config.post_recovery_guidance_enabled
                else 0.0
            ),
            self.machine.config.post_recovery_guidance_max_sec,
            float(self.machine.config.post_recovery_retry_limit),
            1.0 if self.recoverable_navigation_enabled else 0.0,
            float(self.machine.config.recovery_retry_limit),
            self.boundary_recovery_trigger_clearance_m,
            self.boundary_recovery_release_clearance_m,
            self.recenter_target_fill_clearance_m,
            self.post_recovery_affine_weight,
            self.post_recovery_affine_taper_distance_m,
            1.0 if self.post_recovery_progress_enabled else 0.0,
            self.post_recovery_guidance_min_progress_m,
            self.post_recovery_progress_config.window_sec,
            self.post_recovery_progress_config.minimum_path_length_m,
            self.post_recovery_progress_config.maximum_displacement_m,
            float(self.post_recovery_direction_refresh_limit),
            (
                1.0
                if self.post_recovery_source_led_handoff_enabled
                else 0.0
            ),
            (
                1.0
                if self.post_recovery_source_continuity_enabled
                else 0.0
            ),
            self.post_recovery_source_continuity_min_displacement_m,
            self.post_recovery_source_reversal_dot_threshold,
            self.post_recovery_source_bypass_clearance_m,
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
            and (
                self.machine.state in (State.ESCAPE_ASSIST, State.RECENTER)
                or (
                    self.machine.state == State.SEARCH
                    and self.machine.post_recovery_guidance_active
                )
            )
        ):
            state.safe_direction_x = self.safe_direction.x
            state.safe_direction_y = self.safe_direction.y
            state.safe_direction_clearance_m = self.safe_direction.clearance_m
            state.safe_direction_valid = True
            state.safe_direction_revision = self.safe_direction_revision
            state.safe_direction_revision_valid = self.safe_direction_revision > 0
        if self.machine.state == State.RECENTER and self.bounds is not None:
            target = (
                self.recenter_target
                if self.recenter_target is not None
                else self.bounds.center
            )
            state.recenter_target_x = float(target[0])
            state.recenter_target_y = float(target[1])
            state.recenter_target_valid = True
            state.recenter_distance = self.recenter_distance
            state.recenter_distance_valid = math.isfinite(self.recenter_distance)
        weights = list(self.machine.weights)
        if (
            self.machine.state == State.SEARCH
            and self.machine.post_recovery_guidance_active
            and self.post_recovery_source_led_active
        ):
            weights[2] = 0.0
        if (
            self.recoverable_navigation_enabled
            and self.machine.state == State.SEARCH
            and self.machine.post_recovery_guidance_active
            and not self.post_recovery_source_led_active
        ):
            taper = self._post_recovery_affine_taper()
            weights[2] = self.post_recovery_affine_weight * taper
        state.sensor_weight = weights[0]
        state.gaussian_weight = weights[1]
        state.affine_weight = weights[2]
        state.weights_valid = True
        state.failsafe = self.machine.state == State.FAILSAFE
        state.failsafe_valid = True
        self.state_publisher.publish(state)
        command = (
            self.current_supervisor_command
            if (
                self.machine.state == State.RECENTER
                or (
                    self.post_recovery_progress_enabled
                    and self.machine.state == State.SEARCH
                    and self.machine.post_recovery_guidance_active
                )
            )
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

    def _post_recovery_affine_taper(self):
        """Return the bounded spatial affine scale for post-recovery SEARCH."""
        if self.post_recovery_source_led_active:
            return 0.0
        if (
            self.post_recovery_progress_enabled
            and self.post_recovery_progress_tracker is not None
        ):
            outward = (
                self.post_recovery_progress_tracker.latest.outward_progress_m
            )
            excess = max(
                0.0,
                outward - self.post_recovery_guidance_min_progress_m,
            )
            return float(
                np.clip(
                    1.0
                    - excess
                    / self.post_recovery_affine_taper_distance_m,
                    0.0,
                    1.0,
                )
            )
        if self.latest_pose is None or not self.latest_pose_valid:
            return 0.0
        record = self._record_for_fill(self.machine.active_escape_fill_id)
        if record is None:
            return 0.0
        distance = float(
            np.linalg.norm(
                self.latest_pose.position
                - np.asarray(record['center'], dtype=np.float64)
            )
        )
        excess = max(0.0, distance - float(record['support_radius']))
        return float(
            np.clip(
                1.0
                - excess / self.post_recovery_affine_taper_distance_m,
                0.0,
                1.0,
            )
        )

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
